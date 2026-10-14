"""P-07 시연 알람 발생기 시험.

각본 = R11(10건 · 증상군 배분 · 숨은 원인 없음) · 센서 값 그대로(AC-34-C2) · 주소 제한 · 실패 시 오류.
"""

import json
import urllib.error
from pathlib import Path

import pytest

from c1a15.alarms import __main__ as cli
from c1a15.engine import alarm_rules

REPO = Path(__file__).resolve().parents[2]
SCENARIOS = REPO / "data" / "demo" / "scenarios.json"
TABLE = alarm_rules.load(REPO / "data" / "alarm_rules.json")


@pytest.fixture
def items():
    return cli.load_scenarios(SCENARIOS)


def test_scenarios_follow_r11(items):
    groups = [alarm_rules.detect(s["sensor_snapshot"], TABLE)["group"] for s in items]
    assert {g: groups.count(g) for g in set(groups)} == {"CL": 5, "PW": 2, "TW": 2, "LD": 1}
    assert len({s["udi"] for s in items}) == 10
    assert all(len(s["trend"]) == alarm_rules.TREND_N for s in items)
    assert all([p["at"] for p in s["trend"]] == sorted(p["at"] for p in s["trend"]) for s in items)
    text = json.dumps(items, ensure_ascii=False)
    assert all(w not in text for w in ("cause", "원인", "CL-", "PW-", "TW-", "LD-"))  # 각본 행에 숨은 원인 없음


def test_detect_boundaries_and_priority():
    base = {"power_w": 6000, "temp_diff_k": 9.0, "torque_nm": 40.0, "tool_wear_min": 100}
    assert alarm_rules.detect(base, TABLE) is None
    cl = alarm_rules.detect({**base, "temp_diff_k": 8.2}, TABLE)
    assert cl["group"] == "CL" and cl["alarm"]["direction"] == "경계 아래" and cl["alarm"]["boundary"] == 8.3
    assert alarm_rules.detect({**base, "temp_diff_k": 8.3}, TABLE) is None  # 경계 값은 넘지 않음
    both = alarm_rules.detect({**base, "temp_diff_k": 8.0, "power_w": 9000}, TABLE)
    assert both["group"] == "PW"  # priority PW → CL → LD → TW
    assert both["alarm"]["trend_title"] == "기계 출력 추이 · 최근 12회 측정"


def test_payload_is_scenario_row(items):
    s = items[0]
    p = cli.payload(s)
    assert p["sensor_snapshot"] == s["sensor_snapshot"] and p["trend"] == s["trend"]  # AC-34-C2
    assert set(p) == {"scenario_id", "equipment_id", "sensor_snapshot", "trend"}  # 시각 · 증상군은 서버가 정함


@pytest.mark.parametrize("url", ["https://127.0.0.1:8000", "http://example.com", "http://10.0.0.5:8000", "ftp://api"])
def test_url_must_be_local(url):
    with pytest.raises(SystemExit):
        cli.check_url(url)


@pytest.mark.parametrize("url", ["http://127.0.0.1:8000", "http://localhost:8000/", "http://api:8000"])
def test_local_urls_allowed(url):
    assert cli.check_url(url) == url.rstrip("/")


def test_cli_reports_failure_and_exit_code(monkeypatch, capsys):
    monkeypatch.setenv("C1A15_SCENARIOS", str(SCENARIOS))
    monkeypatch.setenv("C1A15_INTERNAL_TOKEN", "t")

    def down(*_):
        raise urllib.error.URLError("connection refused")

    monkeypatch.setattr(cli, "send", down)
    assert cli.main(["DEMO-01"]) == 1
    assert "등록 실패" in capsys.readouterr().err  # FLOW-01: 오류를 보이고 다시 실행
    assert cli.main(["DEMO-99"]) == 2
    monkeypatch.delenv("C1A15_INTERNAL_TOKEN")
    assert cli.main(["DEMO-01"]) == 2


def test_cli_list(monkeypatch, capsys):
    monkeypatch.setenv("C1A15_SCENARIOS", str(SCENARIOS))
    assert cli.main(["--list"]) == 0
    assert capsys.readouterr().out.splitlines()[0].startswith("DEMO-01 ")
    assert json.loads(SCENARIOS.read_text())["scenarios"][0]["scenario_id"] == "DEMO-01"


def test_cli_stdin_eval_mode(monkeypatch, capsys):
    """P-16: --stdin [--eval] — 줄마다 알람 하나를 내부 등록 API로, 평가 모드 표시는 --eval일 때만, 응답은 줄마다 JSON.

    틀리면 실패: eval_mode가 --eval 없이 참이 되거나, 입력에 없는 키(ref)가 등록 본문에 실리거나,
    실패가 줄로 남지 않으면."""
    import io

    monkeypatch.setenv("C1A15_INTERNAL_TOKEN", "t")
    sent = []

    def fake(base, token, body):
        sent.append(body)
        if body["equipment_id"] == "M-99":
            raise urllib.error.HTTPError(base, 422, "x", {}, io.BytesIO(b'{"detail": "unknown_equipment"}'))
        return {"alarm_id": len(sent), "assigned_to": "tech.kim", "occurred_at": "t", "symptom_group": "CL"}

    monkeypatch.setattr(cli, "send", fake)
    lines = [
        {"ref": "A", "equipment_id": "M-01", "sensor_snapshot": {"temp_diff_k": 8.0}, "trend": []},
        {"ref": "B", "equipment_id": "M-99", "sensor_snapshot": {"temp_diff_k": 8.0}},
    ]
    monkeypatch.setattr("sys.stdin", io.StringIO("\n".join(json.dumps(x) for x in lines) + "\n"))
    assert cli.main(["--stdin", "--eval"]) == 0
    out = [json.loads(x) for x in capsys.readouterr().out.splitlines()]
    assert (
        [o["ref"] for o in out] == ["A", "B"] and out[0]["alarm_id"] == 1 and out[1]["error"] == "422 unknown_equipment"
    )
    assert all(b["eval_mode"] is True and "ref" not in b for b in sent)
    sent.clear()
    monkeypatch.setattr("sys.stdin", io.StringIO(json.dumps(lines[0]) + "\n"))
    assert cli.main(["--stdin"]) == 0 and sent[0]["eval_mode"] is False
