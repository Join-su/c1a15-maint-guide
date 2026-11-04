# ruff: noqa: F811, E501 — test_api · test_deploy_path의 fixture(api · db · deploy)를 이름으로 가져와 쓴다
"""D-556 1단계 [점검 바꾸기]: 점검 안내 중 지금 추천 후보(판정 reason_facts.alternatives) 하나를 고르면 그 점검으로 —
앱이 고른 점검을 엶(판정 Run 0 · Pack 약속 v9 전) · 등급 그대로(A 지시 · B 체크리스트 뒤 · C · D 호출) · 업무 기록
check_switch{from, to, kind: detour} = 헛걸음. 후보 밖 · 점검 안내 밖은 409. 고른 점검 결과부터는 다시 판정 Run."""

import pytest
from sqlalchemy import text

from test_api import ok, reset_ops, start, to_instruct  # noqa: F401
from test_deploy_path import api, db, deploy  # noqa: F401

pytestmark = pytest.mark.db


def _post(tech, s, **body):
    return tech.post(f"/api/tech/sessions/{s['session_id']}/events", json={"seq": s["last_seq"] + 1, **body})


def _switches(db, sid):
    with db.connect() as c:
        return [
            r.payload
            for r in c.execute(
                text(
                    "select payload from ops.session_events where session_id = :s and type = 'check_switch' order by seq"
                ),
                {"s": sid},
            )
        ]


def test_switch_to_candidate_opens_it_records_detour_then_judges_again(api, db, deploy):
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
    assert (_post(tech, s, type="check_switch", section="4.3").status_code) == 409  # 지금 점검 = 후보 아님
    assert _post(tech, s, type="check_switch", section="9.9").status_code == 409
    assert _post(tech, s, type="check_switch").status_code == 422  # 절 칸 없으면 422
    s = ok(tech, s, type="check_switch", section=ab["section"])
    assert len(deploy.posts()) == runs_before  # 판정 Run 0(앱이 엶)
    assert s["step"]["section"] == ab["section"]
    assert s["step"]["kind"] == ("instruct" if ab["grade"] == "A" else "instruct_after_checklist")
    assert s["instruction"]["section"] == ab["section"] and s["instruction"]["title"] == ab["title"]
    assert _switches(db, s["session_id"]) == [{"from": "4.3", "to": ab["section"], "kind": "detour"}]  # 헛걸음
    s = tech.get(f"/api/tech/sessions/{s['session_id']}").json()  # 같은 화면 다시 읽어도 고른 점검 그대로
    assert s["step"]["section"] == ab["section"]
    if s["step"]["kind"] == "instruct_after_checklist":
        s = ok(tech, s, type="b_checklist_done", section=ab["section"], checked=s["instruction"]["checklist"])
    s = ok(tech, s, type="result", section=ab["section"], value="정상")  # 고른 점검 결과 → 다시 판정 Run
    assert [p["body"]["kind"] for p in deploy.posts()[runs_before:]][-1] == "judge"
    assert s["step"]["section"] != ab["section"]


def test_switch_only_while_instructing_and_c_grade_becomes_call(api, db, deploy):
    reset_ops(db)
    tech, s = start(api, db)
    s = ok(tech, s, type="alarm_ack")
    s = ok(tech, s, type="lock")
    assert s["step"]["kind"] == "precheck" and s["switch_candidates"] == []  # 사전 확인 중엔 후보 0
    r = _post(tech, s, type="check_switch", section="4.4")
    assert (r.status_code, r.json()["detail"]) == (409, "not_switchable")
    s = ok(tech, s, type="precheck_done", values="하우징 52 °C")
    cd = [x for x in s["switch_candidates"] if x["grade"] in {"C", "D"}]
    if not cd:
        pytest.skip("이 각본 후보에 C · D 점검 없음")
    s = ok(tech, s, type="check_switch", section=cd[0]["section"])
    assert (s["step"]["kind"], s["step"]["section"], s["step"]["reason"]) == ("call", cd[0]["section"], "switched")
    assert s["switch_candidates"] == []  # 호출 단계에선 후보 0
