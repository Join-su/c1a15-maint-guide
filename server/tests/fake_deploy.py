"""시험용 가짜 배포 서버(EV-001 TB-12): 127.0.0.1 임시 포트, 배포 서버 API 계약 v0.9의 키 저장 규칙을 그대로 따른다.

- 같은 키 + 같은 본문 + 끝남 = 저장한 응답 그대로 + `Idempotent-Replayed: true`(성공 · 실행 뒤 실패 모두)
- 같은 키 + 같은 본문 + 실행 중 = 409 idempotency_in_progress(run_id 담김)
- 같은 키 + 다른 본문 = 422 idempotency_key_reused
- 실행 전 거부(422 invalid_input · 400)는 키를 쓰지 않는다
- 새 실행마다 시험이 넣은 동작(`plan`)을 하나씩 꺼내 쓴다: 성공 출력 · 오류(상태 · code · node retryable) · 지연(초)
- 받은 요청(방법 · 경로 · 머리글 · 본문)을 모두 `requests`에 남긴다
kind별 필수 · 금지 칸만 본다 — 정본 v2 전체 schema 검사는 받은 본문 증거를 c1a15-pack .venv로(VC-35).
"""

import hashlib
import json
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

REQUIRED = {
    "alarm": {"event_card"},
    "start": {"session_id", "event_id", "group", "query", "events", "grades", "minutes"},
    "judge": {"session_id", "group", "similar", "events", "grades", "minutes"},
}
FORBIDDEN = {
    "alarm": {"session_id", "group", "similar", "events", "grades", "minutes", "query"},
    "start": {"event_card", "settings"},
    "judge": {"event_card", "settings", "event_id", "query"},
}


def _sha(body: dict) -> str:
    return hashlib.sha256(
        json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


class FakeDeploy:
    def __init__(self, deployment_id: str = "c1a15@v1-local", port: int = 0):
        self.deployment_id = deployment_id
        # 새 실행마다 앞에서 하나씩: {"output": {...}} | {"status": 500, "code": ..., "retryable": bool} + 선택 "delay"
        self.plan: list[dict] = []
        self.default: dict | None = None  # plan이 비었을 때(함수면 본문으로 계산)
        self.keys: dict[str, dict] = {}
        self.runs: dict[str, dict] = {}
        self.requests: list[dict] = []
        self.executions = 0
        self.lock = threading.Lock()
        self.done = threading.Event()  # 실행 하나가 끝나 키에 저장될 때마다 set
        fake = self

        class H(BaseHTTPRequestHandler):
            def log_message(self, *a):
                pass

            def _send(self, status, payload, replayed=False):
                data = json.dumps(payload, ensure_ascii=False).encode()
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                if replayed:
                    self.send_header("Idempotent-Replayed", "true")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                try:
                    self.wfile.write(data)
                except (BrokenPipeError, ConnectionResetError):  # 클라이언트가 시간 초과로 끊음 — 실행은 끝까지 저장됨
                    pass

            def do_GET(self):
                if self.path == "/_keys":  # 단독 실행 때 시험 스크립트가 받은 키 순서를 증거로 떠 감(VC-42)
                    seen = [
                        {
                            "kind": r["body"].get("kind"),
                            "key": r["headers"].get("Idempotency-Key"),
                            "status": (fake.keys.get(r["headers"].get("Idempotency-Key")) or {}).get("status"),
                        }
                        for r in fake.posts()
                    ]
                    return self._send(200, seen)
                fake.requests.append({"method": "GET", "path": self.path, "headers": dict(self.headers), "body": None})
                rid = self.path.rsplit("/", 1)[-1]
                run = fake.runs.get(rid)
                if run is None:
                    return self._send(404, {"error": {"code": "run_not_found", "run_id": None}})
                self._send(200, run)

            def do_POST(self):
                raw = self.rfile.read(int(self.headers.get("Content-Length") or 0))
                key = self.headers.get("Idempotency-Key")
                try:
                    body = json.loads(raw)
                except ValueError:
                    return self._send(400, {"error": {"code": "invalid_json", "run_id": None}})
                if self.path == "/_plan":  # 단독 실행 때 시험 스크립트가 다음 실행 동작을 넣음(화면 한 바퀴 VC-42)
                    fake.plan = list(body)
                    return self._send(200, {"plan": len(fake.plan)})
                fake.requests.append({"method": "POST", "path": self.path, "headers": dict(self.headers), "body": body})
                if not key:
                    return self._send(400, {"error": {"code": "idempotency_key_missing", "run_id": None}})
                kind = body.get("kind")
                if kind not in REQUIRED or REQUIRED[kind] - body.keys() or FORBIDDEN[kind] & body.keys():
                    return self._send(422, {"error": {"code": "invalid_input", "where": "$", "run_id": None}})
                with fake.lock:
                    rec = fake.keys.get(key)
                    if rec is not None:
                        if rec["sha"] != _sha(body):
                            return self._send(422, {"error": {"code": "idempotency_key_reused", "run_id": None}})
                        if rec["status"] is None:
                            return self._send(
                                409,
                                {
                                    "error": {
                                        "code": "idempotency_in_progress",
                                        "retryable": True,
                                        "run_id": rec["run_id"],
                                    }
                                },
                            )
                        return self._send(rec["status"], rec["payload"], replayed=True)
                    fake.executions += 1
                    rid = f"run_{fake.executions:04d}"
                    fake.keys[key] = rec = {"sha": _sha(body), "status": None, "payload": None, "run_id": rid}
                    fake.runs[rid] = {"run_id": rid, "status": "running", "result": None, "error": None}
                    step = (
                        fake.plan.pop(0)
                        if fake.plan
                        else (fake.default(body) if callable(fake.default) else fake.default)
                    )
                if step and step.get("use_default"):  # 지연만 주고 출력은 기본 계산으로
                    step = {**(fake.default(body) if callable(fake.default) else fake.default or {}), **step}
                step = step or {"output": {}}
                if step.get("delay"):
                    time.sleep(step["delay"])
                if "output" in step:
                    summary = {"run_id": rid, "status": "succeeded", "deployment_id": fake.deployment_id}
                    status, payload = 201, {**summary, "result": {"output": step["output"], "grounding": {}}}
                    fake.runs[rid] = {**payload}
                else:
                    node = step.get("node_retryable", step.get("retryable", False))
                    err = {
                        "code": step["code"],
                        "run_id": rid,
                        "retryable": step.get("retryable", False),
                        "where": step.get("where", "$"),
                        "details": {"node_error": {"retryable": node, "code": step.get("node_code")}},
                    }
                    status, payload = step.get("status", 500), {"error": err}
                    fake.runs[rid] = {"run_id": rid, "status": "failed", "result": None, "error": err}
                rec["status"], rec["payload"] = status, payload
                fake.done.set()
                self._send(status, payload)

        self.server = ThreadingHTTPServer(("127.0.0.1", port), H)
        self.url = f"http://127.0.0.1:{self.server.server_address[1]}"
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)

    def __enter__(self):
        self.thread.start()
        return self

    def __exit__(self, *exc):
        self.server.shutdown()
        self.server.server_close()

    def start_running(self, key: str, body: dict, run_id: str | None = "run_held") -> str | None:
        """다른 요청이 이 키로 실행 중인 모양(409 시험용). run_id=None이면 409에 run_id가 없는 모양."""
        self.keys[key] = {"sha": _sha(body), "status": None, "payload": None, "run_id": run_id}
        if run_id:
            self.runs[run_id] = {"run_id": run_id, "status": "running", "result": None, "error": None}
        return run_id

    def finish(self, key: str, *, output: dict | None = None, error: dict | None = None) -> None:
        """start_running으로 잡은 실행을 끝냄 — 키에 응답 저장 · GET /runs/{id}도 끝난 모양."""
        rec = self.keys[key]
        rid = rec["run_id"]
        if error is None:
            payload = {
                "run_id": rid,
                "status": "succeeded",
                "deployment_id": self.deployment_id,
                "result": {"output": output or {}, "grounding": {}},
            }
            rec["status"], rec["payload"] = 201, payload
            if rid:
                self.runs[rid] = payload
        else:
            err = {"run_id": rid, **error}
            rec["status"], rec["payload"] = 500, {"error": err}
            if rid:
                self.runs[rid] = {"run_id": rid, "status": "failed", "result": None, "error": err}

    def gets(self) -> list[dict]:
        return [r for r in self.requests if r["method"] == "GET"]

    def posts(self) -> list[dict]:
        return [r for r in self.requests if r["method"] == "POST"]


def engine_answer(body: dict) -> dict:
    """가짜가 판정을 계산하는 법: 앱 engine(fold → decide) 그대로.

    두 길 대조(VC-34)는 '본문이 충분하고 저장이 맞다'를 본다.

    실제 Pack과 같은 결과는 ES-09(1건) · VC-43(미리보기 = Pack) · 3단계 대조 몫.
    """
    from c1a15.api import deps
    from c1a15.engine import rules, session

    k = deps.manual()
    similar = [rules.Similar(s["record_id"], s.get("cause"), s["score"]) for s in body.get("similar", [])]
    state = session.fold(k, body["group"], similar, body["events"])
    out = {"decision": session.decide(state, k, body["grades"], body["minutes"])}
    if body["kind"] == "start":
        out["similar"] = body.get("similar", [])
        out["retrieval"] = {"source": "request", "vector_db_version": None, "query_from": None, "top_k": 10}
    return {"output": out}


# 단독 실행: python fake_deploy.py <port> — 기본 = engine_answer(DATABASE_URL 필요), /_plan으로 동작 넣기
if __name__ == "__main__":
    import sys

    fake = FakeDeploy(port=int(sys.argv[1]))
    fake.default = engine_answer
    print(f"fake deploy {fake.url}", flush=True)
    fake.server.serve_forever()
