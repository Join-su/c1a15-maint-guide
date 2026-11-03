# ruff: noqa: F811, E501 — test_api의 fixture(api · db)를 이름으로 가져와 쓴다, 시험 설명 문장은 길이 제한 밖
"""D-538 예외 상황 기록: 정비자가 예외라고 판단할 때만 적는 두 글(상황 · 조치) + 서버가 붙이는 자동 정보 여덟
→ 보고서 확정 기록 → 파트장 승인 때 정비 이력 원본 층(record.exception_record) → 승인된 기록 목록(내부 API).

표 · 열 더함 0. 두 글이 모두 비면 기록 없음. 자동 정보에 데이터가 없는 칸은 null(지어내기 0).
"""

import json
import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from test_api import api, db, ok, reset_ops, start, to_instruct  # noqa: F401
from test_lead import lead

pytestmark = pytest.mark.db

SIT = "바닥에 절삭유가 고여 있었고 필터 덮개 고정 나사 하나가 빠져 있었음"
ACT = "나사를 새로 끼우고 필터를 교체한 뒤 바닥을 닦음"
H = {"X-Internal-Token": "test-internal-token"}


def _to_report(api, db, equipment="M-01"):
    tech, s = start(api, db, equipment=equipment)
    s = to_instruct(tech, s)
    s = ok(tech, s, type="result", section="4.3", value="이상", memo="기름때가 필터 표면 절반 넘게 덮음")
    s = ok(tech, s, type="action_done", section="4.3.2")
    s = ok(tech, s, type="restart", checked=s["restart"]["checklist"])
    s = ok(tech, s, type="restart_result", outcome="within")
    return tech, s


def _mine(api, rid):
    """승인된 예외 기록 목록 중 이 보고서 것만(앞 시험이 남긴 승인 이력 — 지식 schema — 은 뺌)."""
    items = TestClient(api).get("/api/internal/exception-records", headers=H).json()["items"]
    return [x for x in items if x["report_id"] == rid]


def _rid(db, sid):
    with db.connect() as c:
        return c.execute(text("select report_id from ops.reports where session_id = :s"), {"s": sid}).scalar()


def test_exception_record_confirm_context_reject_reconfirm_approve_history_and_list(api, db):
    reset_ops(db)
    tech, s = _to_report(api, db)
    assert s["report"]["exception_record"] is None  # 확정 전엔 없음 · 앱이 묻거나 띄우는 조건 0
    s = ok(tech, s, type="report_confirm", exception_record={"situation": f" {SIT} ", "action": ACT})
    ex = s["report"]["exception_record"]
    rid = _rid(db, s["session_id"])
    assert (ex["situation"], ex["action"]) == (SIT, ACT)  # 앞뒤 빈칸 뺌
    ctx = ex["context"]  # 자동 정보 여덟(정비자 입력 0)
    assert ctx["equipment_id"] == "M-01" and ctx["symptom_group"] == {"code": "CL", "name": "온도 차 저하"}
    assert (
        ctx["occurred_at"] and ctx["sensor_values"]["alarm"]["sensor"] == "온도 차" and ctx["sensor_values"]["snapshot"]
    )
    assert ctx["ai_first_check"] == {"section": "4.3", "title": "흡기 필터 육안 점검"}  # 세션 시작 때 첫 안내
    assert ctx["confirmed_cause"] == "냉각 필터 막힘" and ctx["report_id"] == rid
    prev = ctx["previous_maintenance"]  # 같은 설비 정비 이력 중 이 알람 앞 마지막 한 건
    with db.connect() as c:
        want = c.execute(
            text(
                "select record_id from knowledge.history_records where equipment_id = 'M-01' and occurred_at < :at "
                "order by occurred_at desc, record_id desc limit 1"
            ),
            {"at": ctx["occurred_at"]},
        ).scalar()
    assert prev["record_id"] == want and prev["occurred_at"] and prev["outcome"]
    lc = lead(api)
    assert lc.get(f"/api/lead/reports/{rid}/final").json()["exception_record"] == ex
    assert _mine(api, rid) == []  # 승인 전엔 목록 0
    # 반려 → 다시 확정: 새 확정의 기록이 이김
    assert (
        lc.post(f"/api/lead/reports/{rid}/decision", json={"decision": "reject", "memo": "조치 글 다시"}).status_code
        == 200
    )
    s = tech.get(f"/api/tech/sessions/{s['session_id']}").json()
    assert s["report"]["exception_record"]["situation"] == SIT  # 다시 열린 보고서 칸에 앞 기록
    s = ok(tech, s, type="report_confirm", exception_record={"situation": SIT, "action": ACT + " · 사진 남김"})
    r = lc.post(f"/api/lead/reports/{rid}/decision", json={"decision": "approve"})
    assert r.status_code == 200
    hid = r.json()["history_record_id"]
    with db.connect() as c:
        rec = c.execute(text("select record from knowledge.history_records where record_id = :i"), {"i": hid}).scalar()
    assert (
        rec["exception_record"]["action"] == ACT + " · 사진 남김"
        and rec["exception_record"]["context"]["report_id"] == rid
    )
    items = _mine(api, rid)
    assert [(x["record_id"], x["report_id"]) for x in items] == [(hid, rid)]
    assert items[0]["approved_at"] and items[0]["exception_record"] == rec["exception_record"]
    if os.environ.get("KG_RECORD_OUT"):  # D-543 받은 편지함 꼴 초안의 예시 한 건(시험 DB 값 그대로 · 실제 꼴)
        with open(os.environ["KG_RECORD_OUT"], "w", encoding="utf-8") as fp:
            json.dump({"approved_at": items[0]["approved_at"], "record": rec}, fp, ensure_ascii=False, indent=1)


def test_exception_record_empty_is_none_and_list_needs_internal_token(api, db):
    reset_ops(db)
    tech, s = _to_report(api, db)
    s = ok(tech, s, type="report_confirm", exception_record={"situation": "  ", "action": ""})
    assert s["report"]["exception_record"] is None
    rid = _rid(db, s["session_id"])
    lc = lead(api)
    hid = lc.post(f"/api/lead/reports/{rid}/decision", json={"decision": "approve"}).json()["history_record_id"]
    with db.connect() as c:
        rec = c.execute(text("select record from knowledge.history_records where record_id = :i"), {"i": hid}).scalar()
    assert "exception_record" not in rec  # 빈 기록은 이력에 칸을 만들지 않음
    items = TestClient(api).get("/api/internal/exception-records", headers=H).json()["items"]
    assert [x for x in items if x["report_id"] == rid] == []  # 이 보고서는 목록에 없음(앞 시험이 남긴 승인 이력은 뺌)
    assert TestClient(api).get("/api/internal/exception-records").status_code in {401, 403}  # 내부 토큰 없으면 거부
    assert lc.get("/api/internal/exception-records").status_code in {401, 403}  # 파트장 로그인으로도 못 읽음


def test_exception_record_too_long_is_rejected(api, db):
    reset_ops(db)
    tech, s = _to_report(api, db)
    body = {
        "seq": s["last_seq"] + 1,
        "type": "report_confirm",
        "exception_record": {"situation": "가" * 1001, "action": "나"},
    }
    assert tech.post(f"/api/tech/sessions/{s['session_id']}/events", json=body).status_code == 422  # 1000자까지
    assert _rid(db, s["session_id"]) is None  # 확정되지 않음
