# ruff: noqa: F811, E501 — test_api의 fixture(api · db)를 이름으로 가져와 쓴다, 시험 설명 문장은 길이 제한 밖
"""EV-001 ES-07(시험 DB): 판정 길 deploy — start · judge Run 본문 · 저장 · 실패 되돌림 · 같은 seq 다시 · 세션 시작 실패.

VC-35(본문 칸 · session_id S-A<alarm_id> · 되돌림 뒤 같은 기본 키 · 알람 하나 = 세션 하나) · VC-36(이어) · PR-10(start Run 세션당 1회).
가짜 배포 서버가 받은 본문 · 돌려준 응답은 증거 파일로 남겨 c1a15-pack .venv로 정본 v2 schema 검사(VC-35 도구).
"""

import json
import os
from pathlib import Path

import pytest
from sqlalchemy import text

from fake_deploy import FakeDeploy, engine_answer
from test_api import TECH_PW, api, db, login, ok, register, reset_ops  # noqa: F401

pytestmark = pytest.mark.db
BANNED = {
    "user_id",
    "actor",
    "by",
    "display_name",
    "memo",
    "notes",
    "corrections",
    "corrected_from",
    "before",
    "after",
    "_at",
    "reason_text",
}
EVIDENCE = os.environ.get("C1A15_DEPLOY_EVIDENCE")  # 있으면 받은 본문 · 응답을 여기에 jsonl로


@pytest.fixture
def deploy(api, monkeypatch):
    from c1a15.deploy import runs

    with FakeDeploy() as fake:
        fake.default = engine_answer
        monkeypatch.setenv("C1A15_JUDGE", "deploy")
        monkeypatch.setenv("C1A15_DEPLOY_URL", fake.url)
        runs.settings.cache_clear()
        runs.client.cache_clear()
        yield fake
        if EVIDENCE:
            with Path(EVIDENCE).open("a", encoding="utf-8") as f:
                for r in fake.posts():
                    f.write(json.dumps({"request": r["body"]}, ensure_ascii=False) + "\n")
                for rec in fake.keys.values():
                    if rec["status"] in (200, 201):
                        f.write(json.dumps({"response": rec["payload"]["result"]["output"]}, ensure_ascii=False) + "\n")
    runs.settings.cache_clear()
    runs.client.cache_clear()


def banned_keys(obj, path=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in BANNED:
                yield f"{path}.{k}"
            yield from banned_keys(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from banned_keys(v, f"{path}[{i}]")


def count(db, sql, **kw):
    with db.connect() as c:
        return c.execute(text(sql), kw).scalar_one()


def test_start_and_judge_runs_bodies_and_storage(api, db, deploy):
    reset_ops(db)
    tech, _ = login(api, "tech", "tech.kim", TECH_PW)
    alarm_id = register(api, "M-01").json()["alarm_id"]
    s = tech.post(f"/api/tech/alarms/{alarm_id}/session").json()
    sid = s["session_id"]
    start = deploy.posts()[0]["body"]
    assert (
        start["kind"] == "start" and start["session_id"] == f"S-A{alarm_id}" and start["event_id"] == f"C1A-A{alarm_id}"
    )
    assert set(start["query"]["sensor_snapshot"]) == {
        "air_temperature_k",
        "process_temperature_k",
        "rotational_speed_rpm",
        "torque_nm",
        "tool_wear_min",
    }
    assert start["events"] == [] and len(start["similar"]) == 10
    with db.connect() as c:
        row = c.execute(
            text(
                'select "similar", retrieval, start_run_id, deployment_id from ops.diag_sessions where session_id = :s'
            ),
            {"s": sid},
        ).one()
        first = c.execute(
            text("select payload from ops.session_events where session_id = :s and type = 'step_opened' order by seq"),
            {"s": sid},
        ).scalar()
    assert row.similar == start["similar"] and row.start_run_id == "run_0001" and row.deployment_id == "c1a15@v1-local"
    assert (
        row.retrieval["source"] == "request"
        and row.retrieval["vector_db_version"] is None
        and row.retrieval["app_release_id"]
    )
    assert (
        first["via"] == "deploy"
        and first["run_id"] == "run_0001"
        and first["decision"]["kind"] == s["step"]["kind"] == "lock"
    )
    s = ok(tech, s, type="lock")
    judge = deploy.posts()[-1]["body"]
    assert (
        judge["kind"] == "judge" and judge["session_id"] == f"S-A{alarm_id}" and judge["similar"] == row.similar
    )  # 저장 값 그대로
    assert [e["type"] for e in judge["events"]] == ["lock"] and "event_id" not in judge and "query" not in judge
    assert [b for p in deploy.posts() for b in banned_keys(p["body"])] == []
    with db.connect() as c:
        vias = [
            p["via"]
            for (p,) in c.execute(
                text("select payload from ops.session_events where session_id = :s and type = 'step_opened'"),
                {"s": sid},
            )
        ]
    assert (
        set(vias) == {"deploy"}
        and count(db, "select count(*) from ops.audit_log where action = 'pack_call_failed'") == 0
    )
    starts = [p for p in deploy.posts() if p["body"]["kind"] == "start"]
    tech.get(f"/api/tech/sessions/{sid}")
    assert tech.post(f"/api/tech/alarms/{alarm_id}/session").json()["session_id"] == sid  # 알람 하나 = 세션 하나(A9-N7)
    assert (
        len(starts) == len([p for p in deploy.posts() if p["body"]["kind"] == "start"]) == 1
    )  # PR-10: start Run 세션당 1회


def test_judge_failure_rolls_back_and_same_seq_resend_uses_attempt_key(api, db, deploy):
    """VC-36(이어): 저장된 retryable 실패 2번 → 503 pack_unavailable · 업무 기록 0 · 감사 2줄. 같은 seq 다시 → -r2 → 통과."""
    reset_ops(db)
    tech, _ = login(api, "tech", "tech.kim", TECH_PW)
    alarm_id = register(api, "M-01").json()["alarm_id"]
    s = tech.post(f"/api/tech/alarms/{alarm_id}/session").json()
    sid = s["session_id"]
    before = count(db, "select count(*) from ops.session_events where session_id = :s", s=sid)
    deploy.plan = [{"status": 503, "code": "trace_unavailable", "retryable": True}] * 2
    r = tech.post(f"/api/tech/sessions/{sid}/events", json={"seq": s["last_seq"] + 1, "type": "lock"})
    assert r.status_code == 503 and r.json() == {"detail": "pack_unavailable", "code": "trace_unavailable"}
    assert count(db, "select count(*) from ops.session_events where session_id = :s", s=sid) == before  # 되돌림
    assert count(db, "select count(*) from ops.audit_log where action = 'pack_call_failed'") == 2
    keys = [p["headers"]["Idempotency-Key"] for p in deploy.posts() if p["body"]["kind"] == "judge"]
    r = tech.post(f"/api/tech/sessions/{sid}/events", json={"seq": s["last_seq"] + 1, "type": "lock"})  # 같은 seq 다시
    assert r.status_code == 200 and r.json()["locked"]
    again = [p["headers"]["Idempotency-Key"] for p in deploy.posts() if p["body"]["kind"] == "judge"]
    assert again == keys + [keys[0] + "-r2"] and keys[1] == keys[0] + "-r1"  # 되돌린 뒤에도 같은 session_id · 기본 키


def test_start_failure_makes_no_session_and_alarm_stays_new(api, db, deploy):
    reset_ops(db)
    tech, _ = login(api, "tech", "tech.kim", TECH_PW)
    alarm_id = register(api, "M-01").json()["alarm_id"]
    deploy.plan = [{"status": 500, "code": "deployment_not_registered"}]
    r = tech.post(f"/api/tech/alarms/{alarm_id}/session")
    assert r.status_code == 503 and r.json()["code"] == "deployment_not_registered"
    assert count(db, "select count(*) from ops.diag_sessions where alarm_id = :a", a=alarm_id) == 0
    assert count(db, "select status from ops.alarms where alarm_id = :a", a=alarm_id) == "new"
    assert count(db, "select count(*) from ops.audit_log where action = 'session_start'") == 0
    assert count(db, "select count(*) from ops.audit_log where action = 'pack_call_failed'") == 1
    deploy.plan = [{"output": None}]  # 다음 실행은 engine 계산(default) — plan에서 빼고 다시
    deploy.plan.clear()
    r = tech.post(f"/api/tech/alarms/{alarm_id}/session")
    # 저장된 retryable 아닌 실패(deployment_not_registered)는 같은 키 replay — 운영 쪽 일(등록)이 풀려야 함
    assert r.status_code == 503 and deploy.executions == 1
    starts = {p["body"]["session_id"] for p in deploy.posts()}
    assert starts == {f"S-A{alarm_id}"}  # 세션 번호가 없어도 같은 session_id(되돌림 뒤에도)
