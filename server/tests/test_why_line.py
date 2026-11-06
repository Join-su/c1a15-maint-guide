"""D-593(사용자): 예외 후보 글 — 규칙은 등록 기기에서, 최근 정비는 이 기기 것. 값은 Pack matched 그대로."""

import pytest

from c1a15.api import flow

BASE = {"group": "온도 차 저하", "sensors": [], "exception": "EX-R-5001", "records": ["R-5001"]}
RECENT = {"section": "4.3.2", "days": 6, "record_id": "H-0302", "at": "2026-11-04T04:01:32+00:00", "days_ago": 2.0}


@pytest.mark.parametrize(
    ("matched", "line"),
    [
        (
            {**BASE, "equipment_id": "M-03", "source_equipment": "M-01", "recent": RECENT},
            "M-01에서 배운 규칙 · 이 기기도 2일 전 같은 정비를 함",
        ),
        (
            {**BASE, "equipment_id": "M-01", "source_equipment": "M-01", "recent": {**RECENT, "days_ago": 3.3}},
            "이 기기에서 배운 규칙 · 3일 전 같은 정비를 함",
        ),
        (
            {**BASE, "equipment_id": "M-03", "source_equipment": "M-01", "recent": {**RECENT, "days_ago": 0.4}},
            "M-01에서 배운 규칙 · 이 기기도 오늘 같은 정비를 함",
        ),
        (
            {**BASE, "equipment_id": "M-03", "source_equipment": "M-01", "sensors": [["temp_diff_k", "<=", 7.8]]},
            "M-01에서 배운 규칙 · 온도 차 <= 7.8",
        ),
    ],
)
def test_why_line_says_rule_came_from_there_and_work_is_here(matched, line):
    assert flow.why_line({"matched": matched}) == line


def test_no_matched_no_line():
    assert flow.why_line({}) is None and flow.why_line(None) is None
