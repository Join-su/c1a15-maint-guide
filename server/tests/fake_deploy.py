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
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

# ML 길 alarm 출력 = c1a15-pack이 뜬 실제 Pack 출력(D-304 (3) · 보고 012-11, 사용자 모델)
# — 시험 기대값도 여기서 셈(EV-001 CH-28)
ML_ALARM_DATA = Path(__file__).parent / "fixtures" / "ml_alarm_outputs.jsonl"
# start = 사람이 승인한 40행(D-314)의 Pack v4 출력(EV-001 CH-35) — 첫 판정은 아래 앱 engine 계산(받은 similar로)
# — 값 = 장면 ③ 후보 pool20-hybrid-s0.5 40행(D-418, 실제 이력 벡터 DB ir-history-16d297d8 · rerank.pool 20)
START_V4_DATA = Path(__file__).parent / "fixtures" / "start_v4_outputs.jsonl"
# 대역(40행 밖 시험 알람) = 옛 시험값 40행(ES-15 · D-363 ir-history-412ea43e)
# — 다른 시험의 기대(첫 지시 등)가 이 값으로 짜여 있음(D-396 시험 1에서 찾음)
STANDIN_DATA = Path(__file__).parent / "fixtures" / "start_standin_outputs.jsonl"
STAND_INS: list[str] = []  # 대역을 쓴 start 요청의 session_id(시험 기록 — CH-35 'stand_in: true'를 시험에만)

REQUIRED = {
    "alarm": {"event_card"},
    "start": {"session_id", "event_id", "group", "query", "events", "grades", "minutes"},
    "judge": {"session_id", "group", "similar", "events", "grades", "minutes"},
    "report": {"session_id", "group", "similar", "report_draft", "allowed_sections"},  # 약속 v3(EV-001 ES-10)
}
FORBIDDEN = {
    "alarm": {"session_id", "group", "similar", "events", "grades", "minutes", "query"},
    "start": {"event_card", "settings"},
    "judge": {"event_card", "settings", "event_id", "query"},
    "report": {"event_card", "settings", "event_id", "query", "events", "grades", "minutes"},
}


def _sha(body: dict) -> str:
    return hashlib.sha256(
        json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


class FakeDeploy:
    def __init__(self, deployment_id: str = "c1a15@v1-local", port: int = 0, host: str = "127.0.0.1"):
        self.deployment_id = deployment_id
        # 새 실행마다 앞에서 하나씩: {"output": {...}} | {"status": 500, "code": ..., "retryable": bool} + 선택 "delay"
        self.plan: list[dict] = []
        self.default: dict | None = None  # plan이 비었을 때(함수면 본문으로 계산)
        self.keys: dict[str, dict] = {}
        self.runs: dict[str, dict] = {}
        self.requests: list[dict] = []
        self.executions = 0
        self.lock = threading.Lock()
        self.feedback: list[dict] = []  # 받은 사람 체크 기록(EV-006)
        self.feedback_keys: dict[str, dict] = {}
        self.feedback_fail: int | None = None
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
                if self.path.endswith("/feedback"):  # 사람 체크 기록 한 장(EV-006 · deploy 202 꼴)
                    return self._send(*fake.take_feedback(self.path.split("/")[2], key, body))
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

        self.server = ThreadingHTTPServer((host, port), H)  # host = 0.0.0.0은 compose 시험 서비스만(EV-001 CH-42)
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

    def take_feedback(self, run_id: str, key: str, body: dict) -> tuple[int, dict]:
        """`POST /runs/{run_id}/feedback` — kind check_record만 · 같은 키 같은 본문 = 같은 응답 · 다른 본문 = 422.

        시험이 `feedback_fail`(상태 코드)를 넣으면 그 응답을 돌려줌(보내기 실패해도 승인 그대로 시험).
        """
        if self.feedback_fail:
            return self.feedback_fail, {"error": {"code": "internal_error", "run_id": run_id}}
        if body.get("kind") != "check_record" or not isinstance(body.get("record"), dict):
            return 422, {"error": {"code": "invalid_input", "where": "$.kind", "run_id": run_id}}
        if self.runs.get(run_id, {}).get("status") != "succeeded":
            return 404, {"error": {"code": "run_not_found", "run_id": run_id}}
        with self.lock:
            old = self.feedback_keys.get(key)
            if old is not None:
                if old["sha"] != _sha(body):
                    return 422, {"error": {"code": "idempotency_key_reused", "run_id": run_id}}
                return 201, old["reply"]
            reply = {"feedback_id": f"fb_{len(self.feedback) + 1:04d}", "run_id": run_id, "at": "2026-10-27T00:00:00Z"}
            self.feedback.append({"run_id": run_id, "key": key, "body": body})
            self.feedback_keys[key] = {"sha": _sha(body), "reply": reply}
            return 201, reply

    def gets(self) -> list[dict]:
        return [r for r in self.requests if r["method"] == "GET"]

    def posts(self) -> list[dict]:
        return [r for r in self.requests if r["method"] == "POST"]


def start_v4_rows(path: Path | None = None) -> list[dict]:
    """승인 40행(D-314 — 시연 10 + 카드 val 30, Pack v4 start 출력) + 입력 칸.

    만든 도구 = 기록 폴더 ES-15 make_start_fixture.py.
    """
    lines = (path or START_V4_DATA).read_text(encoding="utf-8").splitlines()
    return [json.loads(x) for x in lines if x.strip()]


def start_v4_row(body: dict) -> dict:
    """요청 (group · direction · 센서 5칸)과 같은 행.

    없으면 대역 자료(STANDIN_DATA)에서 같은 group · direction의 첫 행(대역, 40행 밖 시험 알람만 — CH-35).
    """
    q = body["query"]
    rows = [r for r in start_v4_rows() if (r["group"], r["direction"]) == (body["group"], q["direction"])]
    if not rows:
        raise KeyError(f"start 자료에 {body['group']} · {q['direction']} 행이 없음")
    same = [r for r in rows if r["sensor5"] == q["sensor_snapshot"]]
    if same:
        return same[0]
    STAND_INS.append(body.get("session_id"))
    print(f"start stand_in session={body.get('session_id')}", file=sys.stderr, flush=True)  # 단독 실행 기록(fake.log)
    stand = [r for r in start_v4_rows(STANDIN_DATA) if (r["group"], r["direction"]) == (body["group"], q["direction"])]
    return {**stand[0], "stand_in": True}


def ml_alarm_outputs(path: Path | None = None) -> dict[str, dict]:
    """시험 자료 읽기 한 곳(Q-22): jsonl 한 줄 = 한 행, 열쇠 row_id(= 각본 udi) → output.alarm(약속 v3 alarm 객체)."""
    lines = (path or ML_ALARM_DATA).read_text(encoding="utf-8").splitlines()
    return {str(r["row_id"]): r["output"]["alarm"] for r in (json.loads(x) for x in lines if x.strip())}


def engine_answer(body: dict) -> dict:
    """가짜가 판정을 계산하는 법: 앱 engine(fold → decide) 그대로.

    두 길 대조(VC-34)는 '본문이 충분하고 저장이 맞다'를 본다.

    실제 Pack과 같은 결과는 ES-09(1건) · VC-43(미리보기 = Pack) · 3단계 대조 몫.
    """
    from c1a15.api import deps
    from c1a15.engine import alarm_rules, rules, session

    if body["kind"] == "alarm" and body["event_card"]["source_mode"] == "ml_predicted":
        card = body["event_card"]
        out = ml_alarm_outputs()[str(card["data_lineage"]["row_id"])]  # 앱은 row_id를 int로 보냄 — 형 맞춤
        return {"output": {"alarm": {**out, "event_id": card["event_id"]}}}
    if body["kind"] == "alarm":  # 경계 길: 앱 경계 규칙 그대로(계산 칸은 Pack과 같은 식)
        import math

        card = body["event_card"]
        s5 = card["sensor_snapshot"]
        derived = {
            "power_w": round(s5["torque_nm"] * s5["rotational_speed_rpm"] * 2 * math.pi / 60),
            "temp_diff_k": round(s5["process_temperature_k"] - s5["air_temperature_k"], 1),
        }
        hit = alarm_rules.detect({**s5, **derived}, deps.alarm_table())
        return {
            "output": {
                "alarm": {
                    "event_id": card["event_id"],
                    "alarm": hit is not None,
                    "group": hit["group"] if hit else None,
                    "group_source": "sensor_boundary" if hit else None,
                    "alarm_block": hit["alarm"] if hit else None,
                    "sensor_derived": derived,
                    "ml": None,
                    "candidate": None,
                }
            }
        }
    if body["kind"] == "report":  # Pack 가짜 provider(tools/fake/rule.py)와 같은 뜻: 초안 그대로 · 근거 검사 통과
        draft = body["report_draft"]
        return {
            "output": {
                "report": {
                    f: {"text": draft[f], "fallback": False, "attempts": 1, "reason": None} for f in ("cause", "action")
                }
            }
        }
    k = deps.manual()
    row = start_v4_row(body) if body["kind"] == "start" else None  # start = Pack 리트리버 자리(약속 v4) — 승인 자료에서
    given = row["similar"] if row else body.get("similar", [])
    similar = [rules.Similar(s["record_id"], s.get("cause"), s["score"]) for s in given]
    state = session.fold(k, body["group"], similar, body["events"])
    out = {"decision": session.decide(state, k, body["grades"], body["minutes"])}
    if row:
        out["similar"], out["retrieval"] = row["similar"], row["retrieval"]
    return {"output": out}


# 단독 실행: python fake_deploy.py <port> [bind] — 기본 = engine_answer(DATABASE_URL 필요), /_plan으로 동작 넣기
# bind 기본 127.0.0.1(host 시험). compose 시험 서비스(docker-compose.e2e.yml)만 0.0.0.0 — 같은 compose 망 안에서만 열림
if __name__ == "__main__":
    fake = FakeDeploy(port=int(sys.argv[1]), host=sys.argv[2] if len(sys.argv) > 2 else "127.0.0.1")
    fake.default = engine_answer
    print(f"fake deploy {fake.url}", flush=True)
    fake.server.serve_forever()
