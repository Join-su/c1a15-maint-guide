# ruff: noqa: F811, E501 — test_api · test_deploy_path의 fixture(api · db · deploy)를 이름으로 가져와 쓴다
"""약속 v9 [점검 바꾸기] · [예외](c1a15-pack d94f18e · contract-v9.md 1 · 2 · 3절): 점검 안내 중 지금 추천 후보 하나를 고르면
judge 사건 switch_check{section, from_section, choice: candidate} → Pack이 그 점검을 엶(등급 그대로 · switched{from, to}) ·
[예외] = exception_start{mode} → 절 EX-NEW(C): call_first = 호출 → 승인 → 조치 · act_now = 바로 조치(lead_notice
acted_without_call → 파트장 '호출 없이 조치함') → 조치 완료 → 재가동 → 보고서(원인 미상). 후보 밖 · 점검 안내 밖은 409.
기록 줄(3절) = 내부 목록 check-records: 헛걸음 wasted_step · 놓침 missed · 새 예외 new_exception + human_check.
가짜 배포 서버 judge = 앱 engine 사본 + engine/switch.py(Pack custom/switch.py 사본) — Pack judge.py 차례 그대로."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from test_api import ok, reset_ops, start, to_instruct  # noqa: F401
from test_deploy_path import api, db, deploy  # noqa: F401
from test_lead import lead

pytestmark = pytest.mark.db
H = {"X-Internal-Token": "test-internal-token"}


def _post(tech, s, **body):
    return tech.post(f"/api/tech/sessions/{s['session_id']}/events", json={"seq": s["last_seq"] + 1, **body})


def _events(db, sid, etype):
    with db.connect() as c:
        return [
            r.payload
            for r in c.execute(
                text("select payload from ops.session_events where session_id = :s and type = :t order by seq"),
                {"s": sid, "t": etype},
            )
        ]


def _seq(db, sid, etype):
    with db.connect() as c:
        return c.execute(
            text("select seq from ops.session_events where session_id = :s and type = :t"), {"s": sid, "t": etype}
        ).scalar_one()


def _records(api, sid):
    items = TestClient(api).get("/api/internal/check-records", headers=H).json()["items"]
    return [x for x in items if x["session_id"] == sid]


def test_switch_to_candidate_is_a_judge_event_pack_opens_it_then_continues(api, db, deploy):
    reset_ops(db)
    tech, s = start(api, db)
    assert s.get("switch_candidates", []) == []  # 잠금 전 0
    s = to_instruct(tech, s)
    assert (s["step"]["kind"], s["step"]["section"]) == ("instruct", "4.3")
    cands = s["switch_candidates"]
    assert cands and all(set(x) == {"section", "title", "grade"} for x in cands)
    assert "4.3" not in {x["section"] for x in cands}  # 지금 점검은 후보 밖
    ab = next(x for x in cands if x["grade"] in {"A", "B"})
    runs_before = len(deploy.posts())
    assert (_post(tech, s, type="switch_check", section="4.3").status_code) == 409  # 지금 점검 = 후보 아님
    assert _post(tech, s, type="switch_check", section="9.9").status_code == 409
    assert _post(tech, s, type="switch_check").status_code == 422  # 절 칸 없으면 422
    assert _post(tech, s, type="check_switch", section=ab["section"]).status_code == 422  # 1단계 임시 이름은 없음
    s = ok(tech, s, type="switch_check", section=ab["section"])
    posts = deploy.posts()[runs_before:]
    assert [p["body"]["kind"] for p in posts] == ["judge"]  # Pack이 판정(앱이 열지 않음)
    want = {"section": ab["section"], "from_section": "4.3", "choice": "candidate"}
    assert {k: posts[0]["body"]["events"][-1].get(k) for k in ("type", *want)} == {"type": "switch_check", **want}
    assert s["step"]["section"] == ab["section"]
    assert s["step"]["kind"] == ("instruct" if ab["grade"] == "A" else "instruct_after_checklist")
    assert s["instruction"]["section"] == ab["section"] and s["instruction"]["title"] == ab["title"]
    assert _events(db, s["session_id"], "switch_check") == [want]
    opened = _events(db, s["session_id"], "step_opened")[-1]["decision"]
    assert opened["switched"] == {"from": "4.3", "to": ab["section"]}  # Pack 결정 칸
    s = tech.get(f"/api/tech/sessions/{s['session_id']}").json()  # 같은 화면 다시 읽어도 고른 점검 그대로
    assert s["step"]["section"] == ab["section"]
    if s["step"]["kind"] == "instruct_after_checklist":
        s = ok(tech, s, type="b_checklist_done", section=ab["section"], checked=s["instruction"]["checklist"])
    s = ok(tech, s, type="result", section=ab["section"], value="정상")  # 고른 점검 결과 → 이어 감
    assert s["step"]["section"] != ab["section"]
    assert _records(api, s["session_id"]) == [
        {
            "kind": "wasted_step",
            "session_id": s["session_id"],
            "human_check": {"section": ab["section"], "from_section": "4.3"},
            "relation_id": None,
            "at_seq": _seq(db, s["session_id"], "switch_check"),
        }
    ]


def test_switch_only_while_instructing_and_c_grade_becomes_call(api, db, deploy):
    reset_ops(db)
    tech, s = start(api, db)
    s = ok(tech, s, type="alarm_ack")
    s = ok(tech, s, type="lock")
    assert s["step"]["kind"] == "precheck" and s["switch_candidates"] == []  # 사전 확인 중엔 후보 0
    for body in ({"type": "switch_check", "section": "4.4"}, {"type": "exception_start", "mode": "act_now"}):
        r = _post(tech, s, **body)
        assert (r.status_code, r.json()["detail"]) == (409, "not_switchable")  # 안전 단계 먼저
    s = ok(tech, s, type="precheck_done", values="하우징 52 °C")
    cd = [x for x in s["switch_candidates"] if x["grade"] in {"C", "D"}]
    if not cd:
        pytest.skip("이 각본 후보에 C · D 점검 없음")
    s = ok(tech, s, type="switch_check", section=cd[0]["section"])
    assert (s["step"]["kind"], s["step"]["section"], s["step"]["reason"]) == (
        "call",
        cd[0]["section"],
        "switched_check",
    )
    assert s["switch_candidates"] == []  # 호출 단계에선 후보 0


def test_exception_call_first_call_approve_action_restart_report_unknown(api, db, deploy):
    reset_ops(db)
    lc = lead(api)
    tech, s = start(api, db)
    s = to_instruct(tech, s)
    assert _post(tech, s, type="exception_start").status_code == 422  # mode 없으면 422
    assert _post(tech, s, type="exception_start", mode="later").status_code == 422
    s = ok(tech, s, type="exception_start", mode="call_first")
    assert _events(db, s["session_id"], "exception_start") == [{"mode": "call_first"}]
    step = s["step"]
    assert (step["kind"], step["section"], step["grade"], step["reason"]) == (
        "call",
        "EX-NEW",
        "C",
        "exception_progress",
    )
    assert (s["call"]["section"], s["call"]["title"], s["call"]["grade"]) == ("EX-NEW", "예외 조치", "C")
    assert s["call"]["status"] == "sent" and s["step"]["call_status"] == "sent"  # 정답지 16쪽: 호출은 자동으로 나감
    assert s["call"]["summary"]["text"].endswith(" 매뉴얼 후보 밖 — 예외 조치(C등급) 승인 요청. 설비는 정지 상태로 대기 중.")
    assert [e["section"] for e in _events(db, s["session_id"], "call_sent")] == ["EX-NEW"]
    assert "action" not in s  # 승인 전 조치 지시 0
    r = _post(tech, s, type="exception_start", mode="act_now")
    assert (r.status_code, r.json()["detail"]) == (409, "not_switchable")  # 한 번만
    cid = lc.get("/api/lead/calls").json()["rows"][0]["call_id"]
    assert lc.post(f"/api/lead/calls/{cid}/answer", json={"answer": "approved"}).status_code == 200
    s = tech.get(f"/api/tech/sessions/{s['session_id']}").json()
    assert (s["step"]["kind"], s["step"]["section"]) == ("action", "EX-NEW")
    act = s["action"]
    assert (act["section"], act["title"], act["cause_name"], act["grade"], act["steps"]) == (
        "EX-NEW",
        "예외 조치",
        "예외",
        "C",
        [],
    )
    opened = _events(db, s["session_id"], "step_opened")[-1]["decision"]
    assert opened["stage"] == "exception_progress" and "lead_notice" not in opened  # 승인 뒤 = 호출한 조치
    s = ok(tech, s, type="action_done", section="EX-NEW")
    assert s["step"]["kind"] == "restart_check" and s["action"]["done_at"]
    s = ok(tech, s, type="restart", checked=s["restart"]["checklist"])
    s = ok(tech, s, type="restart_result", outcome="within")
    assert (s["step"]["kind"], s["step"]["outcome"]) == ("report", "unknown")
    fields = {f["key"]: f["text"] for f in s["report"]["fields"]}
    assert fields["cause"] == "원인 미상"
    assert all(r["session_id"] != s["session_id"] for r in lc.get("/api/lead/overview").json()["acted"])
    assert _records(api, s["session_id"]) == []  # 확정 전 · 바꾼 점검 0 = 기록 줄 0


def test_exception_act_now_notices_lead_and_records_human_check(api, db, deploy):
    reset_ops(db)
    lc = lead(api)
    tech, s = start(api, db)
    s = to_instruct(tech, s)
    s = ok(tech, s, type="exception_start", mode="act_now")
    assert (s["step"]["kind"], s["step"]["section"]) == ("action", "EX-NEW")  # 호출 없이 바로 조치
    assert _events(db, s["session_id"], "call_sent") == []
    assert (s["path"][-1]["title"], s["path"][-1]["detail"], s["path"][-1]["status"]) == ("예외 조치", "예외", "now")
    opened = _events(db, s["session_id"], "step_opened")[-1]["decision"]
    assert opened["lead_notice"] == "acted_without_call" and opened["exception_progress"] == {"mode": "act_now"}
    acted = [r for r in lc.get("/api/lead/overview").json()["acted"] if r["session_id"] == s["session_id"]]
    assert len(acted) == 1 and acted[0]["equipment_id"] == "M-01" and acted[0]["tech_name"] and acted[0]["at"]
    assert acted[0]["group_name"] == "온도 차 저하"
    s = ok(tech, s, type="action_done", section="EX-NEW")
    s = ok(tech, s, type="restart", checked=s["restart"]["checklist"])
    s = ok(tech, s, type="restart_result", outcome="within")
    assert s["step"]["kind"] == "report"
    txt = "점검 필터 덮개 고정 나사를 손으로 확인. 조치 나사를 새로 끼움"
    s = ok(tech, s, type="exception_split", exception_text=txt)
    m0 = s["report"]["exception_split"]["items"][0]["matches"][0]
    review = [{"item": 0, "decision": "same", "match": {"kind": m0["kind"], "no": m0["no"]}}]
    s = ok(tech, s, type="report_confirm", exception_record={"text": txt}, exception_review=review)
    (rec,) = _records(api, s["session_id"])
    assert rec["kind"] == "missed" and rec["relation_id"] == m0["no"]
    assert rec["human_check"] == {"section": "EX-NEW", "from_section": "4.3"}  # 예외 진행 = EX-NEW · 그때 점검
    assert TestClient(api).get("/api/internal/check-records").status_code in {401, 403}  # 내부 토큰 없으면 거부


def test_check_records_order_and_names():
    """기록 줄 셈(순수 함수): 바꾼 점검마다 헛걸음 · 마지막 확정 예외 칸 item마다 놓침 / 새 예외 · 무효 사건은 뺌."""
    from c1a15.api.sessions import check_records

    events = [
        {"seq": 5, "type": "step_opened", "decision": {"kind": "instruct", "section": "4.3"}},
        {"seq": 6, "type": "switch_check", "section": "4.5", "from_section": "4.3", "choice": "candidate"},
        {
            "seq": 7,
            "type": "switch_check",
            "section": "4.6",
            "from_section": "4.5",
            "choice": "candidate",
            "void": True,
        },
        {"seq": 8, "type": "step_opened", "decision": {"kind": "instruct", "section": "4.5"}},
        {
            "seq": 9,
            "type": "report_confirm",
            "exception_record": {
                "items": [
                    {"kind": "missed", "match": {"kind": "매뉴얼", "no": "4.5.2"}},
                    {"kind": "new_exception", "match": None},
                ]
            },
        },
    ]
    hc = {"section": "4.5", "from_section": "4.3"}
    assert check_records(3, events) == [
        {"kind": "wasted_step", "session_id": 3, "human_check": hc, "at_seq": 6},
        {"kind": "missed", "session_id": 3, "human_check": hc, "relation_id": "4.5.2", "at_seq": 9},
        {"kind": "new_exception", "session_id": 3, "human_check": hc, "relation_id": None, "at_seq": 9},
    ]
    assert check_records(3, [*events[:1], {"seq": 6, "type": "exception_start", "mode": "act_now"}]) == []
