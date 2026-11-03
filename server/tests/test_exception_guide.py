# ruff: noqa: F811, E501 — test_api · test_deploy_path의 fixture(api · db · deploy)를 이름으로 가져와 쓴다
"""D-543 구현 2 예외 안내(승인 전 화면) · 약속 v8(D-545 덧 2): start 결과 exception_guide를 세션에 저장 →
judge 요청마다 exception_relation(relation_id)을 다시 담고 등급표에 EX 줄(처음 값 = 안내 등급) →
Pack이 잠금 · 사전 확인 뒤 예외 절(C)을 호출 단계로 내면 호출 화면 칸 call.exception_guide
= 안내 글 · 절차 · 판정 기준 · 근거 이력 · 출처(앱 원본의 승인 예외 기록).

승인 뒤 예외 절 지시 · 결과 · 조치는 engine 사본 갱신(c1a15-pack handoff) 뒤 — 여기선 호출 · 대기 · 「노하우 등록」까지.
"""

import json
import os

import pytest
from sqlalchemy import text

from fake_deploy import pack_answer
from test_api import ok, reset_ops, start, to_instruct  # noqa: F401
from test_deploy_path import api, db, deploy  # noqa: F401
from test_exception_record import ACT, SIT, _rid, _to_report
from test_lead import lead

pytestmark = pytest.mark.db

TEXT = "흡기 필터를 교체한 뒤 사흘 안에 같은 알람이 다시 울리면, 덮개 고정 나사 네 개가 다 있는지 먼저 본다."


def _approved_exception(api, db):
    tech, s = _to_report(api, db)
    s = ok(tech, s, type="report_confirm", exception_record={"situation": SIT, "action": ACT})
    rid = _rid(db, s["session_id"])
    return lead(api).post(f"/api/lead/reports/{rid}/decision", json={"decision": "approve"}).json()["history_record_id"]


def _guide(hid: str) -> dict:
    """약속 v8 결과 exception_guide(그래프 꼴 정본 4절 · c1a15-pack 주인)."""
    return {
        "section": f"EX-{hid}",
        "relation_id": f"EX-{hid}",
        "grade": "C",
        "title": "필터 덮개 고정 나사 확인",
        "text": TEXT,
        "steps": ["덮개 나사 확인", "빠졌으면 새로 끼움"],
        "criteria": "나사 네 개 모두 체결 = 정상",
        "basis": [hid],
    }


def _bodies(deploy, kind):
    return [r["body"] for r in deploy.posts() if r["body"].get("kind") == kind]


def test_exception_guide_v8_start_relation_call_block_and_send(api, db, deploy):
    reset_ops(db)
    hid = _approved_exception(api, db)
    eg = _guide(hid)
    deploy.default = pack_answer(exception_guide=eg)
    n_judge = len(_bodies(deploy, "judge"))
    tech, s = start(api, db, equipment="M-01")
    s = to_instruct(tech, s)  # 잠금 · 사전 확인 뒤 예외 절 먼저(그래프 꼴 4절 2)
    assert s["step"]["kind"] == "call" and s["step"]["section"] == eg["section"]
    judges = _bodies(deploy, "judge")[n_judge:]
    assert judges and all(b["exception_relation"] == eg["relation_id"] for b in judges)  # judge마다 다시 담음
    assert all(b["grades"][eg["section"]] == "C" for b in judges)  # 등급표 EX 줄(처음 값 = 안내 등급)
    assert "exception_relation" not in _bodies(deploy, "start")[-1]  # start엔 없음(결과로 받음)
    call = s["call"]
    assert (call["section"], call["title"], call["grade"], call["minutes"]) == (
        eg["section"],
        "필터 덮개 고정 나사 확인",
        "C",
        None,
    )  # 매뉴얼 밖 절 — 이름은 Pack 답에서
    g = call["exception_guide"]
    assert {k: g[k] for k in eg} == eg  # v8 칸 그대로
    with db.connect() as c:
        at = c.execute(
            text("select occurred_at from knowledge.history_records where record_id = :i"), {"i": hid}
        ).scalar()
    assert g["source"] == {"record_id": hid, "equipment_id": "M-01", "occurred_at": at.isoformat(), "situation": SIT}
    assert g["next"] is None  # 원래 순서 다음 = v8에 칸 없음(질문 001-zzz17)
    assert f"예외 기록 {hid}" in call["summary"]["text"] and "필터 덮개 고정 나사 확인" in call["summary"]["text"]
    if os.environ.get("EXCEPTION_GUIDE_OUT"):  # D-503 2: 바뀐 응답 꼴 실제 한 건(시험 DB 값 그대로)
        with open(os.environ["EXCEPTION_GUIDE_OUT"], "w", encoding="utf-8") as fp:
            json.dump(call, fp, ensure_ascii=False, indent=1)
    # 「노하우 등록」은 호출과 따로 — 단계 · 호출 상태 그대로, 판정 Run을 다시 부르지 않음(판정 입력 아님)
    runs_before = len(deploy.posts())
    s = ok(tech, s, type="exception_draft", exception_record={"situation": "덕트 이음매 빠짐", "action": "다시 끼움"})
    assert s["exception_draft"]["situation"] == "덕트 이음매 빠짐" and s["call"]["status"] == "none"
    assert len(deploy.posts()) == runs_before
    s = ok(tech, s, type="call_wait")
    assert s["call"]["status"] == "waiting" and s["call"]["exception_guide"]["relation_id"] == eg["relation_id"]
    s = ok(tech, s, type="call_send")
    assert s["call"]["status"] == "sent" and s["call"]["exception_guide"]["text"] == TEXT
    assert _bodies(deploy, "judge")[-1]["exception_relation"] == eg["relation_id"]


def test_ordinary_call_has_no_exception_guide(api, db, deploy):
    reset_ops(db)
    tech, s = start(api, db, equipment="M-01")
    s = to_instruct(tech, s)
    for _ in range(8):
        if s["step"]["kind"] == "call":
            break
        s = ok(tech, s, type="result", section=s["instruction"]["section"], value="정상")
    assert s["step"]["kind"] == "call" and s["call"]["exception_guide"] is None
    assert all("exception_relation" not in b for b in _bodies(deploy, "judge"))  # 안내가 없으면 지금 바이트


def test_exception_guide_unknown_record_has_no_source(api, db, deploy):
    reset_ops(db)
    deploy.default = pack_answer(exception_guide={**_guide("R-9999"), "steps": [], "criteria": None})
    tech, s = start(api, db, equipment="M-01")
    s = to_instruct(tech, s)
    g = s["call"]["exception_guide"]
    assert g["source"] is None and g["steps"] == [] and g["criteria"] is None  # 원본에 없는 기록 — 지어내기 0
