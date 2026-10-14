"""P-19 화면 값 unit 시험(표 기반, DB 없음): 교대 · 점검 n / 최대 m · 근거 기록 · 원인 이름 · 센서 표 · 절차."""

import json
from datetime import datetime

import pytest

from c1a15.api import screen
from c1a15.engine import alarm_rules, knowledge
from c1a15.llm.base import Draft
from c1a15.loader import core

KST = screen.KST


@pytest.fixture(scope="module")
def k(data_dir_module):
    return knowledge.from_sections(core.read_manual(data_dir_module))


@pytest.fixture(scope="module")
def grades(data_dir_module):
    rows = core.grade_rows(core.read_manual(data_dir_module))
    return {r["section_id"]: r["grade"] for r in rows}, {r["section_id"]: r["minutes"] for r in rows}


@pytest.fixture(scope="module")
def table(data_dir_module):
    return alarm_rules.load(data_dir_module / "alarm_rules.json")


@pytest.mark.parametrize(
    ("now", "start"),
    [
        ("2026-10-13T23:30", "2026-10-13T22:00"),  # 야간 앞부분
        ("2026-10-14T03:00", "2026-10-13T22:00"),  # 자정 넘어
        ("2026-10-14T05:59", "2026-10-13T22:00"),
        ("2026-10-14T06:00", "2026-10-13T22:00"),  # 주간 시작 = 방금 끝난 야간이 가장 가까움
        ("2026-10-14T13:59", "2026-10-13T22:00"),
        ("2026-10-14T14:00", "2026-10-13T22:00"),  # 같은 거리(8시간)면 지난 야간
        ("2026-10-14T14:01", "2026-10-14T22:00"),  # 다가올 야간이 더 가까움
        ("2026-10-14T22:00", "2026-10-14T22:00"),
    ],
)
def test_shift_window_is_fixed_night_or_nearest(now, start):
    """결정 014 ④: 야간 22:00 ~ 06:00 고정, 주간이면 가장 가까운 야간 교대."""
    s, e = screen.shift_window(datetime.fromisoformat(now).replace(tzinfo=KST))
    assert s == datetime.fromisoformat(start).replace(tzinfo=KST) and (e - s).total_seconds() == 8 * 3600


def test_shift_summary_counts_before_s03():
    out = screen.shift_summary(2, datetime(2026, 10, 14, 1, 0, tzinfo=KST))
    assert out["label"] == "야간" and (out["start_text"], out["end_text"]) == ("22:00", "06:00")
    assert (out["done"], out["in_progress"], out["calls"]) == (0, 2, 0)  # 보고서 · 호출은 S-03부터


def opened(section, kind="instruct"):
    return {"type": "step_opened", "decision": {"kind": kind, "section": section}}


def test_check_progress_definition(k, grades):
    """결정 014 ②: n = 지시된 점검 순번, m = 지금 지시할 수 있는 점검(A · B 또는 승인된 C) ∪ 이미 지시된 점검."""
    g = dict(grades[0])
    assert (g["4.3"], g["4.4"], g["4.5"], g["4.6"]) == ("A", "C", "A", "A")
    base = [opened("1.2", "lock"), opened("4.2", "precheck")]
    assert screen.check_progress(base, k, "CL", g, set()) == {"check_no": 0, "check_max": 3}
    ev = base + [opened("4.3"), opened("4.3"), opened("4.5")]  # 같은 점검이 다시 열려도 한 번
    assert screen.check_progress(ev, k, "CL", g, set()) == {"check_no": 2, "check_max": 3}
    assert screen.check_progress(ev, k, "CL", g, {"4.4"}) == {"check_no": 2, "check_max": 4}  # 승인된 C
    g2 = {**g, "4.5": "C"}  # 지시 뒤 C가 된 점검도 '한 점검'으로 남는다
    assert screen.check_progress(ev, k, "CL", g2, set()) == {"check_no": 2, "check_max": 3}
    g3 = {**g, "4.4": "B"}
    assert screen.check_progress(base, k, "CL", g3, set())["check_max"] == 4
    assert screen.check_progress(base + [opened("4.4", "call")], k, "CL", g, set())["check_no"] == 0  # 호출은 지시 아님


def test_evidence_records_are_top_confirmed_of_that_cause(k):
    """결정 014 ③: 상위 10건 중 그 점검의 연결 원인으로 확정된 기록, 유사도 순 최대 2건(없으면 빈 목록)."""
    sim = [
        {"record_id": "H-0001", "cause": "CL-2", "score": 0.95},
        {"record_id": "H-0002", "cause": "CL-1", "score": 0.80},
        {"record_id": "H-0003", "cause": "CL-1", "score": 0.91},
        {"record_id": "H-0004", "cause": None, "score": 0.99},
        {"record_id": "H-0005", "cause": "CL-1", "score": 0.70},
    ]
    assert screen.evidence_record_ids(k, "4.3", sim) == ["H-0003", "H-0002"]  # 4.3 → CL-1
    assert screen.evidence_record_ids(k, "4.4", sim) == ["H-0001"]
    assert screen.evidence_record_ids(k, "4.5", sim) == []
    assert screen.evidence_record_ids(k, "4.2", sim) == []  # 사전 확인은 원인을 가르지 않음


def test_cause_names_are_manual_cause_table(k, data_dir_module):
    """A-04: 순위 원인 이름 = 매뉴얼 원인 표 이름. 이력 기록의 원인 이름과도 같다(PBC4-A9 실행 해석 ②)."""
    sections = {s["id"]: s for s in core.read_manual(data_dir_module)}
    for group in ("TW", "PW", "CL", "LD"):
        names = screen.cause_names(k, group)
        overview = next(s for s in sections.values() if s.get("group") == group and s["id"].endswith(".1"))
        for code, name in names.items():
            assert f"| {code} | {name} |" in overview["text"]
        assert len(names) >= 3
    hist = [
        json.loads(line) for line in (data_dir_module / "history/maintenance_history.jsonl").read_text().splitlines()
    ]
    allnames = {c: n for g in ("TW", "PW", "CL", "LD") for c, n in screen.cause_names(k, g).items()}
    confirmed = [r["outcome"] for r in hist if r["outcome"].get("cause_code")]
    assert confirmed and all(allnames[o["cause_code"]] == o["cause_name"] for o in confirmed)


SNAP = {
    "air_temperature_k": 302.7,
    "process_temperature_k": 310.5,
    "rotational_speed_rpm": 1511,
    "torque_nm": 37.7,
    "tool_wear_min": 60,
    "temp_diff_k": 7.8,
    "power_w": 5965,
}


def test_sensor_table_cl_matches_prototype_t03(table):
    """T03 / default: 알람 센서 + 4개, 평소 범위 = 1~9월 2.5 ~ 97.5 백분위, 알람 센서는 경계 쪽 한쪽 범위."""
    alarm = alarm_rules.detect(SNAP, table)
    assert alarm["group"] == "CL"
    rows = screen.sensor_rows(alarm["alarm"], "CL", SNAP, table)
    got = [(r["name"], r["value_text"], r["range_text"], r["status"]) for r in rows]
    assert got == [
        ("온도 차", "7.8 K", "8.3 K 이상", "경계 아래"),
        ("회전 속도", "1,511 rpm", "1,305 ~ 1,979", "정상"),
        ("회전력", "37.7 Nm", "20.5 ~ 59.7", "정상"),
        ("공구 마모", "60 분", "4 ~ 214", "정상"),
        ("공기 온도", "302.7 K", "296.4 ~ 302.4", "정상"),  # 경계 없는 센서는 평소 범위 밖이어도 '정상'
    ]
    assert screen.out_of_range_count(SNAP, table) == 1


def test_sensor_table_pw_alarm_sensor_plus_four(table):
    """PBC4-A8 실행 해석 ①: PW 알람 = 기계 출력 · 회전 속도 · 회전력 · 공구 마모 · 공기 온도(온도 차 빠짐), 5행."""
    snap = {**SNAP, "temp_diff_k": 9.5, "power_w": 9000}
    alarm = alarm_rules.detect(snap, table)
    assert alarm["group"] == "PW"
    rows = screen.sensor_rows(alarm["alarm"], "PW", snap, table)
    assert [r["name"] for r in rows] == ["기계 출력", "회전 속도", "회전력", "공구 마모", "공기 온도"]
    assert rows[0]["range_text"] == "8,366 W 이하" and rows[0]["status"] == "경계 위" and rows[0]["is_alarm_sensor"]


def test_sensor_table_counts_other_boundaries(table):
    snap = {**SNAP, "torque_nm": 61.0}  # 온도 차(알람) + 회전력 경계 위
    alarm = alarm_rules.detect(snap, table)
    rows = {r["name"]: r for r in screen.sensor_rows(alarm["alarm"], alarm["group"], snap, table)}
    assert rows["회전력"]["status"] == "경계 위" and rows["회전력"]["out_of_range"]
    assert screen.out_of_range_count(snap, table) == 2


def test_procedure_steps_and_criterion(k):
    assert screen.procedure_steps(k, "1.2")[0] == "운전자에게 정지를 알리고 가공 중인 프로그램을 끝낸다."
    assert len(screen.procedure_steps(k, "1.2")) == 4
    check = screen.procedure_steps(k, "4.3")  # 점검 방법만(조치 4.3.2 단계는 넣지 않음)
    assert len(check) == 4 and check[-1] == "커버를 닫고 나사를 조인다."
    assert len(screen.procedure_steps(k, "4.2")) == 2
    assert screen.procedure_steps(k, "4.3.2")[0] == "흡기구 덮개를 열고 필터를 빼낸다."
    assert screen.criterion(k, "4.3") == '기름때·먼지가 필터 표면의 절반 이상을 덮으면 "이상"이다.'
    assert screen.criterion(k, "1.2") is None


def test_lock_instruction_is_only_section_1_2(k, grades):
    out = screen.lock_instruction(k, *grades)
    assert set(out) == {"section", "title", "grade", "minutes", "steps"}
    assert out["section"] == "1.2" and out["title"] == "잠금 확인" and len(out["steps"]) == 4


def test_ai_reading_is_grounded_or_falls_back(table, monkeypatch):
    """T03 AI 해석: fixture 문장은 R8 통과(수치 = 값 · 경계), 근거 없는 문장은 코드 템플릿 + '원문으로 대체됨'."""
    alarm = alarm_rules.detect(SNAP, table)["alarm"]
    r = screen.ai_reading(alarm, "temp_diff_k", "온도 차 저하", "냉각 계통")
    assert not r["fallback"] and r["label"] is None and "7.8 K" in r["text"] and "냉각 계통" in r["text"]

    class Ungrounded:
        mode = "x"

        def write(self, facts):
            return Draft("온도 차가 4.4절 기준으로 12% 낮습니다.")

    monkeypatch.setattr(screen, "adapter_for_mode", lambda: Ungrounded())
    r = screen.ai_reading(alarm, "temp_diff_k", "온도 차 저하", "냉각 계통")
    assert r["fallback"] and r["label"] == "원문으로 대체됨" and "4.4" not in r["text"] and "12" not in r["text"]
