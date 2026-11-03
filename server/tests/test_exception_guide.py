# ruff: noqa: F811, E501 — test_api · test_deploy_path의 fixture(api · db · deploy)를 이름으로 가져와 쓴다
"""D-543 구현 2 예외 안내(승인 전 화면): Pack이 예외 기록에서 온 매뉴얼 밖 새 점검(C)을 호출 단계로 내면
호출 화면 칸 call.exception = 노하우 글 · 출처(앱 원본의 승인 예외 기록) · 원래 순서 다음.

Pack 응답 칸 이름은 v7과 함께 c1a15-pack이 정함(답장 001-zzz9 나) — 그 전엔 가짜 배포 서버 + 앱 임시 칸 이름.
승인 뒤 새 점검 수행 · 판정은 Pack 몫(질문 001-zzz15) — 여기선 호출 · 대기 · 「노하우 등록」까지.
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

GUIDE = "흡기 필터를 교체한 뒤 사흘 안에 같은 알람이 다시 울리면, 덮개 고정 나사 네 개가 다 있는지 먼저 본다."


def _approved_exception(api, db):
    tech, s = _to_report(api, db)
    s = ok(tech, s, type="report_confirm", exception_record={"situation": SIT, "action": ACT})
    rid = _rid(db, s["session_id"])
    return lead(api).post(f"/api/lead/reports/{rid}/decision", json={"decision": "approve"}).json()["history_record_id"]


def test_exception_guide_call_block_source_next_and_send(api, db, deploy):
    reset_ops(db)
    hid = _approved_exception(api, db)
    deploy.default = pack_answer(
        exception={
            "section": "X-0012",
            "title": "필터 덮개 고정 나사 확인",
            "record_id": hid,
            "guide_text": GUIDE,
            "next_section": "4.5",
        }
    )
    tech, s = start(api, db, equipment="M-01")
    s = to_instruct(tech, s)
    s = ok(tech, s, type="result", section=s["instruction"]["section"], value="정상")
    assert s["step"]["kind"] == "call" and s["step"]["section"] == "X-0012"
    call = s["call"]
    assert (call["section"], call["title"], call["grade"], call["minutes"]) == (
        "X-0012",
        "필터 덮개 고정 나사 확인",
        "C",
        None,
    )  # 매뉴얼 밖 절 — 이름은 Pack 답에서
    ex = call["exception"]
    assert ex["record_id"] == hid and ex["guide_text"] == GUIDE
    assert ex["next"] == {"section": "4.5", "title": "냉각수 수위 확인"}
    with db.connect() as c:
        at = c.execute(
            text("select occurred_at from knowledge.history_records where record_id = :i"), {"i": hid}
        ).scalar()
    assert ex["source"] == {"record_id": hid, "equipment_id": "M-01", "occurred_at": at.isoformat(), "situation": SIT}
    assert "예외 기록" in call["summary"]["text"] and "필터 덮개 고정 나사 확인" in call["summary"]["text"]
    if os.environ.get("EXCEPTION_GUIDE_OUT"):  # D-503 2: 바뀐 응답 꼴 실제 한 건(시험 DB 값 그대로)
        with open(os.environ["EXCEPTION_GUIDE_OUT"], "w", encoding="utf-8") as fp:
            json.dump(call, fp, ensure_ascii=False, indent=1)
    # 「노하우 등록」은 호출과 따로 — 단계 · 호출 상태 그대로, 판정 Run을 다시 부르지 않음(판정 입력 아님)
    runs_before = len(deploy.posts())
    s = ok(tech, s, type="exception_draft", exception_record={"situation": "덕트 이음매 빠짐", "action": "다시 끼움"})
    assert s["exception_draft"]["situation"] == "덕트 이음매 빠짐" and s["call"]["status"] == "none"
    assert len(deploy.posts()) == runs_before
    s = ok(tech, s, type="call_wait")
    assert s["call"]["status"] == "waiting" and s["call"]["exception"]["record_id"] == hid
    s = ok(tech, s, type="call_send")
    assert s["call"]["status"] == "sent" and s["call"]["exception"]["guide_text"] == GUIDE


def test_ordinary_call_has_no_exception(api, db, deploy):
    reset_ops(db)
    tech, s = start(api, db, equipment="M-01")
    s = to_instruct(tech, s)
    for _ in range(8):
        if s["step"]["kind"] == "call":
            break
        s = ok(tech, s, type="result", section=s["instruction"]["section"], value="정상")
    assert s["step"]["kind"] == "call" and s["call"]["exception"] is None


def test_exception_guide_unknown_record_has_no_source(api, db, deploy):
    reset_ops(db)
    deploy.default = pack_answer(
        exception={
            "section": "X-0099",
            "title": "새 점검",
            "record_id": "R-9999",
            "guide_text": GUIDE,
            "next_section": None,
        }
    )
    tech, s = start(api, db, equipment="M-01")
    s = to_instruct(tech, s)
    s = ok(tech, s, type="result", section=s["instruction"]["section"], value="정상")
    ex = s["call"]["exception"]
    assert ex["source"] is None and ex["next"] is None  # 앱 원본에 없는 기록 · 다음 없음 — 지어내기 0
