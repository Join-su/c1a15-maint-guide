# ruff: noqa: F811, E501 — test_api · test_deploy_path의 fixture(api · db · deploy)를 이름으로 가져와 쓴다, 시험 설명 문장은 길이 제한 밖
"""D-566 약속 v10 5절 다음 같은 조건 알람의 예외 안내 — 걸음마다(Pack 3502e29 engine/exception 사본):
C 승인 예외 전체에 한 번 → 점검 c1 → c2 → 조치 a1 → a2(적은 순서 · 결과로 건너뛰지 않음 · 사건 step 칸) → 재가동 → 재가동 값
→ 안(정상)이면 보고서 · 밖이면 원래 점검 순서(D-566 덧 2). 정답지 26쪽 '안내 차례 · 적은 순서 그대로'."""

import json
import os

import pytest

from test_api import api, db, ok, reset_ops, start, to_instruct  # noqa: F401
from test_deploy_path import deploy  # noqa: F401
from test_exception_guide import _approve_call, _approved_exception, _bodies, _guide

pytestmark = pytest.mark.db

CHECKS = [
    {"what": "필터 덮개 고정 나사 확인", "how": "손으로 돌려 봄", "criteria": "모두 체결 = 정상", "minutes": 5},
    {"what": "흡기 덕트 이음매", "how": "", "criteria": "", "minutes": None},
]
ACTIONS = [
    {"what": "나사를 새로 끼움", "parts": ["M6 나사"], "minutes": 5},
    {"what": "밴드를 다시 조임", "parts": [], "minutes": None},
]


def _walk(s):
    return [(w["step"], w["what"], w["done"], w["now"]) for w in s["exception_walk"]]


def _to_walk(api, db, deploy):
    reset_ops(db)
    hid = _approved_exception(api, db)
    eg = {
        **_guide(hid),
        "minutes": 15,
        "next_section": "4.3",
        "topic": "필터 덮개 나사",
        "checks": CHECKS,
        "actions": ACTIONS,
    }
    deploy.default = pack_answer_of(eg)
    tech, s = start(api, db, equipment="M-01")
    s = to_instruct(tech, s)
    return tech, s, eg


def pack_answer_of(eg):
    from fake_deploy import pack_answer

    return pack_answer(exception_guide=eg)


def test_walk_call_once_then_each_step_in_order_restart_within_report(api, db, deploy):
    tech, s, eg = _to_walk(api, db, deploy)
    sec = eg["section"]
    # 승인 전 호출(예외 전체에 한 번): 제목 = 첫 걸음 무엇 · 안내 차례 넷 · 지금 = c1(정답지 26쪽)
    assert (s["step"]["kind"], s["step"]["section"]) == ("call", sec) and "step" not in s["step"]
    assert s["call"]["title"] == CHECKS[0]["what"]
    g = s["call"]["exception_guide"]
    assert (g["checks"], g["actions"], g["topic"]) == (CHECKS, ACTIONS, "필터 덮개 나사")
    assert g["next"] is None  # 걸음 길 = '원래 순서 다음' 줄 0(정답지 26쪽)
    assert _walk(s) == [
        ("c1", CHECKS[0]["what"], False, True),
        ("c2", CHECKS[1]["what"], False, False),
        ("a1", ACTIONS[0]["what"], False, False),
        ("a2", ACTIONS[1]["what"], False, False),
    ]
    s = ok(tech, s, type="call_send")
    _approve_call(api, eg)
    s = tech.get(f"/api/tech/sessions/{s['session_id']}").json()
    # c1: 점검 칸 그대로(무엇 = 제목 · 방법 = 절차 · 기준 · 분)
    assert (s["step"]["kind"], s["step"]["step"], s["step"]["step_index"], s["step"]["steps_total"]) == (
        "instruct",
        "c1",
        1,
        4,
    )
    ins = s["instruction"]
    assert (ins["title"], ins["steps"], ins["criterion"], ins["minutes"]) == (
        CHECKS[0]["what"],
        ["손으로 돌려 봄"],
        "모두 체결 = 정상",
        5,
    )
    n_judge = len(_bodies(deploy, "judge"))
    s = ok(tech, s, type="result", section=sec, value="정상")  # 정상이어도 다음 걸음(건너뛰지 않음)
    ev = [e for e in _bodies(deploy, "judge")[n_judge]["events"] if e.get("section") == sec and e["type"] == "result"]
    assert ev[-1]["step"] == "c1"  # 사건 step 칸(약속 v10 5절)
    assert (s["step"]["kind"], s["step"]["step"]) == ("instruct", "c2")
    assert (s["instruction"]["title"], s["instruction"]["steps"], s["instruction"]["criterion"]) == (
        CHECKS[1]["what"],
        [],
        None,
    )
    assert [w[2:] for w in _walk(s)] == [(True, False), (False, True), (False, False), (False, False)]
    s = ok(tech, s, type="result", section=sec, value="이상", memo="이음매 벌어짐")
    assert (s["step"]["kind"], s["step"]["step"]) == ("action", "a1")
    act = s["action"]
    assert (act["title"], act["steps"], act["minutes"], act["done_at"]) == (
        ACTIONS[0]["what"],
        ["부품 M6 나사"],
        5,
        None,
    )
    assert act["cause_name"] == "예외상황-필터 덮개 나사"
    s = ok(tech, s, type="action_done", section=sec)
    assert (s["step"]["kind"], s["step"]["step"]) == ("action", "a2") and s["action"]["title"] == ACTIONS[1]["what"]
    r = tech.post(
        f"/api/tech/sessions/{s['session_id']}/events",
        json={"seq": s["last_seq"] + 1, "type": "action_done", "section": "4.3.2"},
    )
    assert r.status_code == 409  # 다른 절 조치는 받지 않음
    s = ok(tech, s, type="action_done", section=sec)
    if os.environ.get("WALK_JUDGE_OUT"):  # D-503 2: 걸음 사건이 실린 judge 요청 실제 한 건(Pack v10 schema 대조용)
        with open(os.environ["WALK_JUDGE_OUT"], "w", encoding="utf-8") as fp:
            json.dump(_bodies(deploy, "judge")[-1], fp, ensure_ascii=False, indent=1)
    ad = [e for e in _bodies(deploy, "judge")[-1]["events"] if e["type"] == "action_done"]
    assert [e.get("step") for e in ad] == ["a1", "a2"]
    assert (
        s["step"]["kind"] == "restart_check" and s["action"]["title"] == ACTIONS[1]["what"] and s["action"]["done_at"]
    )
    assert all(w[2] for w in _walk(s)) and not any(w[3] for w in _walk(s))
    titles = [p["title"] for p in s["path"]]
    assert [t for t in titles if t in {x["what"] for x in CHECKS + ACTIONS}] == [
        x["what"] for x in CHECKS + ACTIONS
    ]  # 경로 = 걸음마다
    s = ok(tech, s, type="restart", checked=s["restart"]["checklist"])
    s = ok(tech, s, type="restart_result", outcome="within")
    assert s["step"]["kind"] == "report"  # 안(정상) → 보고서
    f = {x["key"]: x["text"] for x in s["report"]["fields"]}  # 보고서 = 걸음마다 그 점검 · 조치 무엇
    assert f"{CHECKS[0]['what']}({sec}, 정상) → {CHECKS[1]['what']}({sec}, 이상: 이음매 벌어짐)" in f["check_path"]
    assert f["action"].startswith(f"{ACTIONS[0]['what']}({sec}, C) · {ACTIONS[1]['what']}({sec}, C) · 재가동")
    s2 = tech.get(f"/api/tech/sessions/{s['session_id']}").json()
    assert s2["step"] == s["step"]  # 같은 화면 다시 열어도 그대로


def test_walk_restart_outside_goes_back_to_original_order(api, db, deploy):
    """D-566 덧 2: 안내를 마친 뒤 재가동 값이 밖이면 원래 점검 순서(4.3 …) — 그 재가동 둘은 원래 순서 접기에서 뺌."""
    tech, s, eg = _to_walk(api, db, deploy)
    sec = eg["section"]
    s = ok(tech, s, type="call_send")
    _approve_call(api, eg)
    s = tech.get(f"/api/tech/sessions/{s['session_id']}").json()
    for _ in range(2):
        s = ok(tech, s, type="result", section=sec, value="정상")
    for _ in range(2):
        s = ok(tech, s, type="action_done", section=sec)
    s = ok(tech, s, type="restart", checked=s["restart"]["checklist"])
    s = ok(tech, s, type="restart_result", outcome="outside")
    assert s["step"]["section"] == "4.3" and s["step"]["kind"] in ("instruct", "instruct_after_checklist")
    assert "step" not in s["step"] and s["instruction"]["title"] == "흡기 필터 육안 점검"  # 보통 지시(걸음 칸 0)
    s = ok(tech, s, type="result", section="4.3", value="이상", memo="기름때")
    s = ok(tech, s, type="action_done", section="4.3.2")
    assert s["step"]["kind"] == "restart_check"  # 원래 순서의 재가동은 처음부터(예외 몫 재가동은 뺌)
    s = ok(tech, s, type="restart", checked=s["restart"]["checklist"])
    s = ok(tech, s, type="restart_result", outcome="within")
    assert s["step"]["kind"] == "report"


def test_old_guide_without_lists_keeps_old_path(api, db, deploy):
    """목록 없는 옛 예외 절(v8 · v9 꼴)은 옛 길: 점검 하나 → 정상이면 원래 순서 · 안내 차례 없음."""
    reset_ops(db)
    eg = {**_guide(_approved_exception(api, db)), "next_section": "4.3"}
    deploy.default = pack_answer_of(eg)
    tech, s = start(api, db, equipment="M-01")
    s = to_instruct(tech, s)
    assert s["exception_walk"] is None and s["call"]["title"] == eg["title"]
    s = ok(tech, s, type="call_send")
    _approve_call(api, eg)
    s = tech.get(f"/api/tech/sessions/{s['session_id']}").json()
    assert "step" not in s["step"] and s["instruction"]["steps"] == eg["steps"]
    s = ok(tech, s, type="result", section=eg["section"], value="정상")
    assert s["step"]["section"] == "4.3"
