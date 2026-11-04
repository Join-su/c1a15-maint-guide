# ruff: noqa: F811, E501 — test_api · test_deploy_path의 fixture(api · db · deploy)를 이름으로 가져와 쓴다, 시험 설명 문장은 길이 제한 밖
"""D-538 · D-556 1단계 예외 상황 기록: 정비자가 예외라고 판단할 때만 적는 글 하나 → 「AI 나눔」(배포 Run 임시 kind
exception_split — 점검 1 + 조치 1 × n · 줄마다 KG 비슷한 것) → 줄마다 같음(놓침) / 아님(새 예외) → 보고서 확정 기록
(+ 서버가 붙이는 상황 · 결과 · 자동 정보 여덟) → 파트장 승인 때 정비 이력 원본 층(record.exception_record) → 승인된 기록 목록.

표 · 열 더함 0. 글이 비면 기록 없음. 자동 정보에 데이터가 없는 칸은 null(지어내기 0). 칸 이름은 앱 임시(Pack 약속 v9 전).
가짜 배포 서버 AI 나눔 = fake_deploy.split_answer(글 줄 '점검 …' · '조치 …' 짝 · '나사'가 든 줄만 KG 비슷한 것 EX-R-0001).
"""

import json
import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from test_api import api, db, ok, reset_ops, start, to_instruct  # noqa: F401
from test_deploy_path import deploy  # noqa: F401
from test_lead import lead

pytestmark = pytest.mark.db

TEXT = "점검 필터 덮개 고정 나사를 손으로 확인. 조치 나사를 새로 끼움. 점검 흡기 덕트 이음매. 조치 밴드를 다시 조임"
SIM = {"relation_id": "EX-R-0001", "section": "EX-R-0001", "title": "필터 덮개 고정 나사 확인"}
NOTE_TEXT = (
    "점검 필터 덮개 고정 나사를 손으로 확인 · 조치 나사를 새로 끼움. 점검 흡기 덕트 이음매 · 조치 밴드를 다시 조임"
)
H = {"X-Internal-Token": "test-internal-token"}


def _to_report(api, db, equipment="M-01"):
    tech, s = start(api, db, equipment=equipment)
    s = to_instruct(tech, s)
    s = ok(tech, s, type="result", section="4.3", value="이상", memo="기름때가 필터 표면 절반 넘게 덮음")
    s = ok(tech, s, type="action_done", section="4.3.2")
    s = ok(tech, s, type="restart", checked=s["restart"]["checklist"])
    s = ok(tech, s, type="restart_result", outcome="within")
    return tech, s


def _split(tech, s, txt=TEXT):
    return ok(tech, s, type="exception_split", exception_text=txt)


def _confirm(tech, s, txt=TEXT, choices=({"same": "EX-R-0001"}, {"same": None})):
    return ok(tech, s, type="report_confirm", exception_record={"text": txt, "choices": list(choices)})


def _mine(api, rid):
    """승인된 예외 기록 목록 중 이 보고서 것만(앞 시험이 남긴 승인 이력 — 지식 schema — 은 뺌)."""
    items = TestClient(api).get("/api/internal/exception-records", headers=H).json()["items"]
    return [x for x in items if x["report_id"] == rid]


def _set(ex: dict) -> dict:
    return {k: v for k, v in ex.items() if v is not None}


def _rid(db, sid):
    with db.connect() as c:
        return c.execute(text("select report_id from ops.reports where session_id = :s"), {"s": sid}).scalar()


def _post(tech, s, **body):
    return tech.post(f"/api/tech/sessions/{s['session_id']}/events", json={"seq": s["last_seq"] + 1, **body})


def test_split_choose_confirm_context_reject_reconfirm_approve_history_and_list(api, db, deploy):
    reset_ops(db)
    tech, s = _to_report(api, db)
    assert s["report"]["exception_record"] is None and s["report"]["exception_split"] is None
    auto = s["report"]["exception_auto"]  # 확정 전 칸에 보일 자동 두 칸(입력 0)
    assert auto["situation"].startswith("M-01 · 온도 차 저하 · ") and auto["result"] == "재가동 정상(경계 이내)"
    runs_before = len(deploy.posts())
    step = s["step"]
    s = _split(tech, s, f" {TEXT} ")
    sp = s["report"]["exception_split"]
    assert sp["text"] == TEXT and sp["error"] is None and len(sp["items"]) == 2  # 점검 1 + 조치 1 × 2
    assert sp["items"][0]["check"]["what"] == "필터 덮개 고정 나사를 손으로 확인"
    assert sp["items"][0]["action"] == {"what": "나사를 새로 끼움", "parts": [], "minutes": None}
    assert [it["similar"] for it in sp["items"]] == [[SIM], []]  # KG 비슷한 것(나사 줄만)
    posts = deploy.posts()[runs_before:]
    assert [p["body"]["kind"] for p in posts] == ["exception_split"]  # 판정 Run 다시 0 · 나눔 Run 하나
    assert posts[0]["body"]["text"] == TEXT and posts[0]["body"]["equipment_id"] == "M-01"
    assert s["step"] == step  # 단계 그대로
    s = _split(tech, s)  # 같은 화면 한 번 더 = 새 Run(seq가 다름) · 같은 결과
    assert len(deploy.posts()) == runs_before + 2 and s["report"]["exception_split"]["items"] == sp["items"]
    # 확정: 줄마다 같음 / 아님 — 고르지 않음 · 남의 관계 · 글이 바뀜(다시 나눠야 함)은 409
    for bad, reason in (
        ({"text": TEXT, "choices": [{"same": None}]}, "exception_choice_needed"),
        ({"text": TEXT, "choices": [{"same": "EX-R-9999"}, {"same": None}]}, "exception_choice_invalid"),
        ({"text": TEXT + " 더", "choices": [{"same": None}, {"same": None}]}, "exception_split_needed"),
        ({"text": TEXT, "choices": [{"same": None}, {"same": "EX-R-0001"}]}, "exception_choice_invalid"),
    ):
        r = _post(tech, s, type="report_confirm", exception_record=bad)
        assert (r.status_code, r.json()["detail"]["reason"]) == (409, reason)
    assert _rid(db, s["session_id"]) is None  # 확정되지 않음
    s = _confirm(tech, s)
    ex = s["report"]["exception_record"]
    rid = _rid(db, s["session_id"])
    assert ex["text"] == TEXT and [(it["same"], it["kind"]) for it in ex["items"]] == [
        ("EX-R-0001", "miss"),  # 같음 = 놓침(KG에 있음)
        (None, "new"),  # 아님 = 새 예외(관문)
    ]
    fields = {f["key"]: f["text"] for f in s["report"]["fields"]}
    assert ex["situation"] == f"{fields['equipment_alarm']} · {fields['sensor_evidence']}"  # 확정 때 값
    assert ex["result"] == "재가동 정상(경계 이내)" and "action" not in ex
    assert s["report"]["exception_split"] is None  # 확정 뒤 나눔 결과는 기록 안으로
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
    final = lc.get(f"/api/lead/reports/{rid}/final").json()["exception_record"]
    assert _set(final) == ex  # 최종 보기 · 내부 목록은 빈 칸도 None으로 보임(action 등)
    assert _mine(api, rid) == []  # 승인 전엔 목록 0
    # 반려 → 다시 나눔 · 다시 확정: 새 확정의 기록이 이김
    assert (
        lc.post(f"/api/lead/reports/{rid}/decision", json={"decision": "reject", "memo": "조치 글 다시"}).status_code
        == 200
    )
    s = tech.get(f"/api/tech/sessions/{s['session_id']}").json()
    assert s["report"]["exception_record"]["text"] == TEXT  # 다시 열린 보고서 칸에 앞 기록
    one = "점검 흡기 덕트 이음매. 조치 밴드를 다시 조임"
    r = _post(tech, s, type="report_confirm", exception_record={"text": one, "choices": [{"same": None}]})
    assert r.json()["detail"]["reason"] == "exception_split_needed"  # 반려 전 나눔은 쓰지 않음
    s = _split(tech, s, one)
    s = _confirm(tech, s, one, [{"same": None}])
    r = lc.post(f"/api/lead/reports/{rid}/decision", json={"decision": "approve"})
    assert r.status_code == 200
    hid = r.json()["history_record_id"]
    with db.connect() as c:
        rec = c.execute(text("select record from knowledge.history_records where record_id = :i"), {"i": hid}).scalar()
    assert rec["exception_record"]["text"] == one and [it["kind"] for it in rec["exception_record"]["items"]] == ["new"]
    assert rec["exception_record"]["context"]["report_id"] == rid
    items = _mine(api, rid)
    assert [(x["record_id"], x["report_id"]) for x in items] == [(hid, rid)]
    assert items[0]["approved_at"] and _set(items[0]["exception_record"]) == rec["exception_record"]
    if os.environ.get("EXCEPTION_LIST_OUT"):  # D-545: 내부 목록 응답 한 건 그대로(가상 기록 · 토큰 · 접속 정보 0)
        with open(os.environ["EXCEPTION_LIST_OUT"], "w", encoding="utf-8") as fp:
            json.dump(items[0], fp, ensure_ascii=False, indent=1)
    if os.environ.get("KG_RECORD_OUT"):  # D-543 받은 편지함 꼴 초안의 예시 한 건(시험 DB 값 그대로 · 실제 꼴)
        with open(os.environ["KG_RECORD_OUT"], "w", encoding="utf-8") as fp:
            json.dump({"approved_at": items[0]["approved_at"], "record": rec}, fp, ensure_ascii=False, indent=1)


def test_split_failure_does_not_block_report(api, db, deploy):
    """배포 서버가 끝내 실패하면 나눔 결과 error · 줄 0 — 그 글로는 확정 0, 글을 지우면 보고서는 그대로 확정."""
    reset_ops(db)
    tech, s = _to_report(api, db)
    deploy.plan.extend([{"status": 500, "code": "internal", "retryable": False}] * 3)
    s = _split(tech, s)
    assert s["report"]["exception_split"] == {"text": TEXT, "items": [], "error": "pack_unavailable"}
    r = _post(tech, s, type="report_confirm", exception_record={"text": TEXT, "choices": []})
    assert r.json()["detail"]["reason"] == "exception_split_needed"
    deploy.plan.clear()
    s = ok(tech, s, type="report_confirm")
    assert s["report"]["status"] == "awaiting_approval" and s["report"]["exception_record"] is None


def test_exception_record_empty_is_none_and_list_needs_internal_token(api, db):
    reset_ops(db)
    tech, s = _to_report(api, db)
    s = ok(tech, s, type="report_confirm", exception_record={"text": "  ", "choices": []})
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


def test_exception_text_too_long_and_split_only_on_report_step(api, db):
    reset_ops(db)
    tech, s = start(api, db)
    s = to_instruct(tech, s)
    r = _post(tech, s, type="exception_split", exception_text=TEXT)
    assert (r.status_code, r.json()["detail"]) == (409, "no_report_step")  # 보고서 단계에서만
    tech, s = _to_report(api, db)
    assert _post(tech, s, type="exception_split", exception_text="가" * 2001).status_code == 422  # 2000자까지
    assert _post(tech, s, type="exception_split").status_code == 422  # 글 칸 없으면 422
    assert _post(tech, s, type="exception_split", exception_text="  ").json()["detail"] == "exception_text_required"
    for bad in ({"text": "가" * 2001}, {"situation": "가"}, {"check": {"what": "가"}}):  # 옛 꼴 두 글 · 칸 0
        assert _post(tech, s, type="report_confirm", exception_record=bad).status_code == 422
    assert _rid(db, s["session_id"]) is None  # 확정되지 않음


def test_exception_draft_prefills_report_and_reference_notes(api, db):
    """D-543 「노하우 등록」: 잠금 뒤 글 초안 → 보고서 칸에 채워짐 → 나눔 · 보고서와 함께 확정 · 승인 →
    같은 설비 · 같은 증상군의 다음 세션에 참고 알림(앱 원본 조회 — 답장 001-zzz9 다 = A)."""
    reset_ops(db)
    tech, s = start(api, db)
    body = {"seq": s["last_seq"] + 1, "type": "exception_draft", "exception_record": {"text": TEXT}}
    assert tech.post(f"/api/tech/sessions/{s['session_id']}/events", json=body).status_code == 409  # 잠금 전 0
    s = to_instruct(tech, s)
    assert s["exception_draft"] is None  # 아직 초안 없음(앞 시험이 남긴 승인 이력이 있으면 참고 알림은 있을 수 있음)
    s = ok(tech, s, type="exception_draft", exception_record={"text": f" {TEXT} "})
    assert s["exception_draft"] == {"text": TEXT}
    assert s["step"]["kind"] == "instruct" and s["instruction"]["section"] == "4.3"  # 판정 · 단계 그대로
    s = ok(tech, s, type="result", section="4.3", value="이상", memo="기름때가 필터 표면 절반 넘게 덮음")
    s = ok(tech, s, type="action_done", section="4.3.2")
    s = ok(tech, s, type="restart", checked=s["restart"]["checklist"])
    s = ok(tech, s, type="restart_result", outcome="within")
    assert s["report"]["exception_draft"] == {"text": TEXT}  # 보고서 칸에 채울 값
    s = _split(tech, s)
    s = _confirm(tech, s)
    assert s["report"]["exception_draft"] is None and s["report"]["exception_record"]["text"] == TEXT
    rid = _rid(db, s["session_id"])
    hid = lead(api).post(f"/api/lead/reports/{rid}/decision", json={"decision": "approve"}).json()["history_record_id"]
    tech2, s2 = start(api, db, equipment="M-01")
    s2 = to_instruct(tech2, s2)
    note = next(n for n in s2["exception_notes"] if n["record_id"] == hid)
    assert note["situation"].startswith("M-01 · ") and note["action"] == NOTE_TEXT and note["occurred_at"]
    assert note["text"] == NOTE_TEXT  # 알림 한 줄 = 나눈 줄을 이은 글(상황은 자동이라 머리와 겹침)
    tech3, s3 = start(api, db, equipment="M-03")  # 다른 설비는 이 기록을 보지 않음
    s3 = to_instruct(tech3, s3)
    assert all(n["record_id"] != hid for n in s3["exception_notes"])


def test_exception_draft_empty_clears(api, db):
    reset_ops(db)
    tech, s = start(api, db)
    s = to_instruct(tech, s)
    s = ok(tech, s, type="exception_draft", exception_record={"text": TEXT})
    assert s["exception_draft"] == {"text": TEXT}
    s = ok(tech, s, type="exception_draft", exception_record={"text": " "})
    assert s["exception_draft"] is None  # 비우면 초안 없음


def test_old_drafts_read_as_one_text():
    """D-556 전 업무 기록 초안(두 글 situation · action)은 글 하나로 읽음(읽기만)."""
    from c1a15.api import flow

    events = [{"seq": 1, "type": "exception_draft", "exception_record": {"situation": "가 ", "action": "나"}}]
    assert flow.exception_draft_of(events) == {"text": "가\n나"}
    assert flow.exception_draft_of([{**events[0], "exception_record": {"situation": " ", "action": ""}}]) is None
    old = {"situation": "상황 글", "action": "조치 글", "context": {}}
    assert flow.exception_text(old) == "조치 글"  # 전 기록 알림 = 조치 글 그대로


def test_split_items_drop_malformed_lines():
    """배포 출력 줄 꼴이 어긋나면 그 줄만 뺌(지어내기 0)."""
    from c1a15.api import flow

    good = {
        "check": {"what": "가", "how": "나", "criteria": "다", "minutes": 3},
        "action": {"what": "라"},
        "similar": [],
    }
    out = flow.split_items({"exception_split": {"items": [good, {"check": "글"}, {"action": {}}]}})
    assert out == [
        {
            "check": {"what": "가", "how": "나", "criteria": "다", "minutes": 3},
            "action": {"what": "라", "parts": [], "minutes": None},
            "similar": [],
        }
    ]
    assert flow.split_items({}) == []
