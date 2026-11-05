# ruff: noqa: F811, E501 — test_api · test_deploy_path의 fixture(api · db · deploy)를 이름으로 가져와 쓴다, 시험 설명 문장은 길이 제한 밖
"""D-570(recent-condition.md · 줄인 꼴): 예외 기록 자동 정보 = 같은 설비 최근 N일 정비 이력 전부(이력 번호 · 시각 · 며칠 전 ·
한 조치 절 did · 한 점검 절 checked · 결과) · 시연 이력 줄 명령(넣기 · 보기 · 빼기 — 시연 줄만)."""

import json
import os
from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import text

from test_api import api, db, ok, reset_ops  # noqa: F401
from test_deploy_path import deploy  # noqa: F401
from test_exception_record import NOT, TEXT, _split, _to_report

pytestmark = pytest.mark.db

FAR = datetime(2027, 6, 1, 10, 0, tzinfo=UTC)  # 이력 자료(2026년) 뒤 — 창 안엔 넣은 줄만


def _add(*args):
    from c1a15 import demo_history

    return demo_history.main(["add", *args])


def _drop(*records):
    from c1a15 import demo_history

    for r in records:
        demo_history.main(["remove", "--record", r])


def test_recent_window_equipment_order_and_fields(api, db, capsys):
    from c1a15.api import flow
    from c1a15.db import models as m

    at = FAR.isoformat()
    try:
        _add(
            "--record",
            "H-9001",
            "--equipment",
            "M-01",
            "--days-ago",
            "3",
            "--action",
            "4.3.2",
            "--check",
            "4.3",
            "--at",
            at,
        )
        _add("--record", "H-9002", "--equipment", "M-01", "--days-ago", "1", "--action", "4.5.2", "--at", at)
        _add("--record", "H-9003", "--equipment", "M-01", "--days-ago", "8", "--action", "4.3.2", "--at", at)  # 7일 밖
        _add(
            "--record", "H-9004", "--equipment", "M-02", "--days-ago", "2", "--action", "4.3.2", "--at", at
        )  # 다른 설비
        _add(
            "--record", "H-9005", "--equipment", "M-01", "--days-ago", "-1", "--action", "4.3.2", "--at", at
        )  # 알람 뒤
        line = json.loads(
            capsys.readouterr().out.strip().splitlines()[0]
        )  # add = 이력 원본 꼴 한 줄(배포단 적재기 입력)
        assert line["record_id"] == "H-9001" and line["demo"] == "D-570" and line["equipment_id"] == "M-01"
        assert [(s["kind"], s["section"]) for s in line["steps"]] == [("check", "4.3"), ("action", "4.3.2")]
        assert line["outcome"]["cause_name"]  # 그 조치 절 원인 이름(매뉴얼 표)
        alarm = m.Alarm(equipment_id="M-01", occurred_at=FAR, symptom_group="CL")
        with db.connect() as c:
            got = flow.recent_maintenance(c, alarm)
            assert [r["record_id"] for r in got] == ["H-9002", "H-9001"]  # 최근 것 먼저 · 7일 안 · 같은 설비 · 알람 앞
            h1 = got[1]
            assert (h1["days_before"], h1["did"], h1["checked"]) == (3, ["4.3.2"], ["4.3"])
            assert h1["occurred_at"] == (FAR - timedelta(days=3)).isoformat() and h1["outcome"]
            assert [r["record_id"] for r in flow.recent_maintenance(c, alarm, days=30)] == [
                "H-9002",
                "H-9001",
                "H-9003",
            ]
    finally:
        _drop("H-9001", "H-9002", "H-9003", "H-9004", "H-9005")
    with db.connect() as c:
        left = c.execute(text("select count(*) from knowledge.history_records where record_id like 'H-900%'")).scalar()
    assert left == 0


def test_demo_command_only_touches_demo_rows(api, db):
    from c1a15 import demo_history

    with db.connect() as c:
        real = c.execute(
            text(
                "select record_id from knowledge.history_records where source = 'generated' and record->>'demo' is null limit 1"
            )
        ).scalar()
    with pytest.raises(ValueError):  # 시연 줄 아닌 이력과 번호가 겹치면 거절
        _add("--record", real, "--equipment", "M-01", "--days-ago", "3", "--action", "4.3.2")
    demo_history.main(["remove", "--record", real])  # 시연 표시 없는 이력은 빼지 않음
    with db.connect() as c:
        assert (
            c.execute(text("select count(*) from knowledge.history_records where record_id = :r"), {"r": real}).scalar()
            == 1
        )
    with pytest.raises(ValueError):  # 매뉴얼에 없는 절
        _add("--record", "H-9010", "--equipment", "M-01", "--days-ago", "3", "--action", "9.9.9")


def test_exception_record_context_carries_recent_list(api, db, deploy):
    """예외 기록 확정 → 자동 정보 recent_maintenance에 3일 전 시연 줄(승인 기록 파일 칸 그대로)."""
    reset_ops(db)
    tech, s = _to_report(api, db)
    with db.connect() as c:
        at = c.execute(text("select occurred_at from ops.alarms where alarm_id = :a"), {"a": s["alarm_id"]}).scalar()
    try:
        _add(
            "--record", "H-9011", "--equipment", "M-01", "--days-ago", "3", "--action", "4.3.2", "--at", at.isoformat()
        )
        s = _split(tech, s)
        s = ok(tech, s, type="report_confirm", exception_record={"text": TEXT}, exception_review=NOT)
        ctx = s["report"]["exception_record"]["context"]
        demo = [r for r in ctx["recent_maintenance"] if r["record_id"] == "H-9011"]
        assert len(demo) == 1 and (demo[0]["days_before"], demo[0]["did"]) == (3, ["4.3.2"])
        assert all(0 <= r["days_before"] <= 7 for r in ctx["recent_maintenance"])  # 7일 창
        assert ctx["previous_maintenance"]  # 옛 칸 그대로(파트장 '직전 정비' 줄)
        if os.environ.get("RECENT_OUT"):  # D-503 2: 승인 기록 파일 context 실제 한 건(시험 DB 값)
            with open(os.environ["RECENT_OUT"], "w", encoding="utf-8") as fp:
                json.dump(ctx, fp, ensure_ascii=False, indent=1)
    finally:
        _drop("H-9011")
