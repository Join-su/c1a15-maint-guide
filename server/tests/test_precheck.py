"""D-619 사전 점검 후보 셈(순수 함수 · 약속 handoff/d619/precheck-contract.md 3절 · 세는 곳 = 앱 서버).
예시 줄(표시 D-619)과 표에 적은 시연 줄만 셈 · 진행 중은 분모 밖 · 승인 예외는 배포가 바뀐 뒤에만 이어짐."""

from datetime import UTC, datetime, timedelta

import pytest

NOW = datetime(2026, 11, 7, 10, 0, tzinfo=UTC)


def line(
    rid, eq, days_ago, *, did=(), bad=(), good=(), group="CL", topic=None, demo="D-619", source="generated", ex=None
):
    rec = {
        "steps": [
            *({"kind": "check", "section": s, "result": "이상"} for s in bad),
            *({"kind": "check", "section": s, "result": "정상"} for s in good),
            *({"kind": "action", "section": s, "name": f"이름 {s}"} for s in did),
        ],
        "outcome": {"type": "원인 미상·숙련자 인계"},  # 예시 줄 원인 칸 비움(관문 확률 영향 0 · graph-values 01:13)
        "demo": demo,
    }
    if topic:
        rec["exception_record"] = {"text": topic}
    if ex:
        rec["exception_record"] = ex
    return {
        "record_id": rid,
        "equipment_id": eq,
        "symptom_group": group,
        "occurred_at": NOW - timedelta(days=days_ago),
        "source": source,
        "record": rec,
    }


def pattern(pid):
    from c1a15.api import precheck

    return next(p for p in precheck.PATTERNS if p.id == pid)


def count(pid, rows, reflected=frozenset()):
    from c1a15.api import precheck

    return precheck.classify(pattern(pid), rows, NOW, reflected)


def a_rows():
    """A: 이어짐 둘 · 이상 없음 둘 · 시연 H-0301(3일 전) · 지금 설비 하나."""
    return [
        line("H-P001", "M-04", 90, did=["4.3.2"]),
        line("H-P002", "M-04", 85, topic="필터 덮개 고정"),
        line("H-P003", "M-05", 80, did=["4.3.2"]),
        line("H-P004", "M-05", 75, topic="필터 덮개 고정"),
        line("H-P005", "M-06", 50, did=["4.3.2"]),
        line("H-P006", "M-08", 40, did=["4.3.2"]),
        line("H-P007", "M-07", 2, did=["4.3.2"]),
        line("H-0301", "M-01", 3, did=["4.3.2"], demo="D-570"),
    ]


APPROVED = line(
    "R-8001",
    "M-01",
    1,
    demo=None,
    source="approved_report",
    ex={"text": "흡기 필터 덮개 볼트가 덜 조여져 있었음", "exception": {"topic": "흡기 필터 덮개 볼트"}},
)


def test_a_before_approval_two_of_four_and_open_rows_stay_out_of_total():
    got = count("A", a_rows())
    assert (len(got["hits"]), len(got["clean"])) == (2, 2)
    assert sorted(r["record_id"] for r in got["open"]) == ["H-0301", "H-P007"]


def test_approved_exception_counts_only_after_the_deployed_graph_changed():
    assert len(count("A", [*a_rows(), APPROVED])["hits"]) == 2
    got = count("A", [*a_rows(), APPROVED], frozenset({"R-8001"}))
    assert (len(got["hits"]), len(got["clean"])) == (3, 2)
    hit = next(r for r in got["hits"] if r["record_id"] == "H-0301")
    assert (hit["follow_id"], hit["follow_days"]) == ("R-8001", 2)
    assert [r["record_id"] for r in got["open"]] == ["H-P007"]


def test_only_marked_lines_count_real_history_is_not_the_total():
    real = line("H-0100", "M-09", 120, did=["4.3.2"], demo=None)
    got = count("A", [*a_rows(), real])
    assert "H-0100" not in {r["record_id"] for k in ("hits", "clean", "open") for r in got[k]}


def test_follow_must_be_on_the_same_equipment_and_inside_the_window():
    rows = [
        line("H-P101", "M-09", 90, did=["2.4.2"], good=["2.3"], group="TW"),
        line("H-P102", "M-10", 88, bad=["2.3"], group="TW"),  # 다른 설비
        line("H-P103", "M-09", 70, bad=["2.3"], group="TW"),  # 14일 밖
        line("H-P104", "M-09", 85, good=["2.3"], group="TW"),  # 그 절 정상은 뒤 사건 아님
    ]
    got = count("B", rows)
    assert (len(got["hits"]), [r["record_id"] for r in got["clean"]]) == (0, ["H-P101"])


def test_follow_is_the_check_section_found_abnormal():
    rows = [
        line("H-P101", "M-09", 90, did=["2.4.2"], good=["2.3"], group="TW"),
        line("H-P102", "M-09", 80, bad=["2.3"], group="TW"),
    ]
    got = count("B", rows)
    assert [(r["record_id"], r["follow_id"], r["follow_days"]) for r in got["hits"]] == [("H-P101", "H-P102", 10)]


def test_exception_without_the_pattern_word_is_not_a_follow():
    other = {
        **APPROVED,
        "record": {**APPROVED["record"], "exception_record": {"text": "팬 소리", "exception": {"topic": "팬"}}},
    }
    assert len(count("A", [*a_rows(), other], frozenset({"R-8001"}))["hits"]) == 2


@pytest.mark.parametrize(
    ("hits", "clean", "show"), [(2, 2, False), (3, 2, True), (3, 4, False), (3, 3, True), (0, 0, False)]
)
def test_show_needs_three_hits_and_at_least_half(hits, clean, show):
    from c1a15.api import precheck

    assert precheck.shows(hits, clean) is show


def test_words_stay_off_the_banned_list():
    from c1a15.api import precheck

    assert not [p for p in precheck.PATTERNS if "연쇄" in p.follow + p.look_at]
