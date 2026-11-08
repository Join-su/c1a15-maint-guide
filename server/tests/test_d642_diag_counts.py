# ruff: noqa: E501 — 시험 설명 문장은 길이 제한 밖
"""리허설 2 R3 · R6(A 진단 숫자 · 앱 몫, 표시만 · 셈 손 0): 순위 줄은 확률 셈에 쓴 이 설비 기록 n건 중 k건을 보인다.

n · k는 Pack 판정 출력이 준 그대로(앱이 다시 세지 않음) · 칸이 없거나 꼴이 다르면 None(옛 Pack · 옛 세션 → 화면은 숫자 자리를 숨김).
'이 점검을 고른 이유'의 다른 점검 목록은 확률 순위가 아닌 매뉴얼 점검 목록이라 '매뉴얼의 다른 점검'으로 부른다. DB 없음.
"""

from c1a15.api import screen
from c1a15.llm.base import Facts
from c1a15.llm.fixture import FixtureAdapter

ORDER = ["CL-1", "CL-2", "CL-3", "CL-4"]
KC, KT = screen.PACK_COUNT_KEYS


def test_counts_come_from_the_pack_output_in_manual_order():
    step = {"probabilities": {"CL-1": 50}, "evidence": {}, KC: {"CL-3": 1, "CL-1": 4, "CL-4": 0, "CL-2": 1}, KT: 6}
    got = screen.decided_counts(step, ORDER)
    assert got == {"equipment_counts": {"CL-1": 4, "CL-2": 1, "CL-3": 1, "CL-4": 0}, "equipment_total": 6}
    assert list(got["equipment_counts"]) == ORDER


def test_no_counts_or_odd_shape_gives_none():
    assert screen.decided_counts(None, ORDER) is None
    assert screen.decided_counts({"probabilities": {}, "evidence": {}}, ORDER) is None  # 옛 Pack · 옛 세션
    assert screen.decided_counts({KC: {"CL-1": 4}, KT: "6"}, ORDER) is None
    assert screen.decided_counts({KC: [4, 1], KT: 6}, ORDER) is None
    assert screen.decided_counts({KC: {"CL-1": "4"}, KT: 6}, ORDER) is None
    assert screen.decided_counts({KC: {"CL-1": True}, KT: 6}, ORDER) is None
    assert screen.decided_counts({KC: {"CL-1": 4}, KT: True}, ORDER) is None


def test_reason_calls_the_alternatives_the_manuals_other_checks():
    facts = {
        "cause_name": "냉각 필터 막힘",
        "probability": 50,
        "minutes": 3,
        "grade": "A",
        "alternatives": [{"section": "4.4", "grade": "C"}, {"section": "4.5", "grade": "A"}],
    }
    for rank in (1, 2):
        text = FixtureAdapter().write(Facts("reason", "4.3", {**facts, "rank": rank})).text
        assert text.endswith("매뉴얼의 다른 점검: 4.4(C), 4.5(A).")
        assert text.count("다른 점검") == 1
