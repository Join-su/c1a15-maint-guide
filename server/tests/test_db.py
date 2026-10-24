"""실제 PostgreSQL 통합 시험(marker db, DATABASE_URL 필요). 시험 DB 컨테이너는 매번 새로 만든다."""

import os
import subprocess
from pathlib import Path

import pytest
from sqlalchemy import create_engine, text

from c1a15.checks.passwords import is_argon2id_hash_of

pytestmark = pytest.mark.db
SERVER = Path(__file__).resolve().parents[1]
URL = os.environ.get("DATABASE_URL", "")


def alembic(*args):
    subprocess.run(["alembic", *args], cwd=SERVER, check=True)


@pytest.fixture(scope="module")
def db():
    if not URL:
        pytest.skip("DATABASE_URL 없음")
    return create_engine(URL)


def test_migration_round_trip_and_no_model_drift(db):
    alembic("upgrade", "head")
    alembic("downgrade", "base")
    with db.connect() as c:
        assert c.execute(text("select count(*) from pg_namespace where nspname in ('ops','knowledge')")).scalar() == 0
    alembic("upgrade", "head")
    alembic("check")  # 모델과 DB 사이 차이 없음


def test_loader_counts_and_storage(db):
    env = {**os.environ, "DATA_DIR": str(SERVER.parent / "data"), "PYTHONPATH": str(SERVER / "src")}
    subprocess.run(["python", "-m", "c1a15.loader"], cwd=SERVER, env=env, check=True)
    with db.connect() as c:
        q = lambda sql: c.execute(text(sql)).scalar()  # noqa: E731
        assert q("select count(*) from knowledge.manual_sections") == 43
        assert q("select count(*) from knowledge.history_records") == 300
        assert q("select count(*) from ops.grade_table") == 36
        assert q("select count(*) from ops.common_precheck_items") == 3
        assert q("select count(*) from ops.equipment_assignments") == 20
        assert q("select extversion from pg_extension where extname = 'vector'")
        rows = c.execute(text("select role, password_hash from ops.accounts")).all()
    assert len(rows) == 5
    plain = {"tech": os.environ["C1A15_TECH_PASSWORD"], "lead": os.environ["C1A15_LEAD_PASSWORD"]}
    assert all(is_argon2id_hash_of(h, plain[role]) for role, h in rows)
    assert all(plain[role] not in h for role, h in rows)


FOUR = tuple(f"knowledge.{t}" for t in ("active_releases", "release_chunks", "data_releases", "history_embeddings"))


def test_vc56_0009_drops_four_tables_and_downgrade_recreates_empty(db):
    """VC-56(EV-001 CH-34): 0009 = 앱 리트리버 · release 표 넷 지움 · downgrade = 빈 표로 다시 · 다시 upgrade.

    downgrade는 자료를 되살리지 않음(S3-Q5).

    남길 표(history_records · manual_sections)와 적재 자료는 그대로.
    """
    env = {**os.environ, "DATA_DIR": str(SERVER.parent / "data"), "PYTHONPATH": str(SERVER / "src")}
    alembic("upgrade", "head")
    subprocess.run(["python", "-m", "c1a15.loader"], cwd=SERVER, env=env, check=True)
    reg = lambda c, t: c.execute(text("select to_regclass(:t)"), {"t": t}).scalar()  # noqa: E731
    with db.connect() as c:
        assert [reg(c, t) for t in FOUR] == [None] * 4
        assert c.execute(text("select count(*) from knowledge.history_records")).scalar() == 300
    alembic("downgrade", "0008")
    with db.connect() as c:
        assert all(reg(c, t) for t in FOUR)
        assert [c.execute(text(f"select count(*) from {t}")).scalar() for t in FOUR] == [0] * 4
        assert c.execute(text("select count(*) from knowledge.history_records")).scalar() == 300
    alembic("upgrade", "head")
    with db.connect() as c:
        assert [reg(c, t) for t in FOUR] == [None] * 4
        assert c.execute(text("select version_num from alembic_version")).scalar() == "0009"


def test_adv03_plaintext_store_is_caught(db):
    """ADV-03: 저장 계층을 원문 저장으로 바꾼 결함을 시험 DB에 흉내 내면 저장값 검사가 실패를 잡아야 한다."""
    with db.begin() as c:
        c.execute(
            text(
                "insert into ops.accounts(user_id, display_name, role, password_hash) "
                "values ('adv.plain', 'x', 'tech', 'plain-pass')"
            )
        )
        stored = c.execute(text("select password_hash from ops.accounts where user_id='adv.plain'")).scalar()
        c.execute(text("delete from ops.accounts where user_id='adv.plain'"))
    assert not is_argon2id_hash_of(stored, "plain-pass")


def test_langgraph_postgres_checkpoint_resume(db):
    """P-03 · EP-C1-HITL-001: LangGraph checkpoint를 PostgreSQL에 저장한다.

    새 graph(재시작)가 같은 thread에서 같은 단계로 재개한다."""
    from langgraph.checkpoint.postgres import PostgresSaver
    from langgraph.types import Command

    from c1a15.engine import graph, knowledge
    from c1a15.loader import core

    sections = core.read_manual(SERVER.parent / "data")
    rows = core.grade_rows(sections)
    k = knowledge.from_sections(sections)
    g, m = {r["section_id"]: r["grade"] for r in rows}, {r["section_id"]: r["minutes"] for r in rows}
    similar = [
        {"record_id": "H-a", "cause": "CL-1", "score": 0.96},
        {"record_id": "H-b", "cause": "CL-1", "score": 0.91},
        {"record_id": "H-c", "cause": "CL-2", "score": 0.84},
    ]
    conn_str = URL.replace("postgresql+psycopg://", "postgresql://")
    cfg = {"configurable": {"thread_id": "db-session-1"}}
    with PostgresSaver.from_conn_string(conn_str) as saver:
        saver.setup()
        app = graph.build(k, lambda: g, lambda: m, checkpointer=saver)
        app.invoke({"group": "CL", "similar": similar, "events": []}, cfg)
        app.invoke(Command(resume={"type": "lock", "key": "1"}), cfg)
        app.invoke(Command(resume={"type": "precheck_done", "key": "2"}), cfg)
    with PostgresSaver.from_conn_string(conn_str) as saver2:  # 새 연결 · 새 graph = 프로세스 재시작
        restarted = graph.build(k, lambda: g, lambda: m, checkpointer=saver2)
        assert restarted.get_state(cfg).values["decision"]["section"] == "4.3"
        out = restarted.invoke(Command(resume={"type": "result", "section": "4.3", "value": "정상", "key": "3"}), cfg)
        assert out["__interrupt__"][0].value["decision"]["kind"] == "call"


# EV-001 ES-18: test_release_db.py를 지우며 옮겨 옴 — 릴리스와 무관한 ES-04 시험
def test_alarm_candidates_reason_check(db):
    """EV-001 ES-04(가): '사람 판단 필요' 기록 표 — 사유는 low_confidence · rnf · model_failure만.

    경계 길 알람의 ml 칸은 null.
    """
    import sqlalchemy

    ins = text(
        "insert into ops.alarm_candidates (equipment_id, reason, boundary_crossed, sensor_snapshot, event) "
        "values ('M-01', :r, false, '{}'::jsonb, '{}'::jsonb)"
    )
    with db.begin() as c:
        for r in ("low_confidence", "rnf", "model_failure"):
            c.execute(ins, {"r": r})
        assert (
            c.execute(text("select count(*) from ops.alarm_candidates where status = 'needs_human'")).scalar_one() >= 3
        )
    with pytest.raises(sqlalchemy.exc.IntegrityError), db.begin() as c:
        c.execute(ins, {"r": "boundary"})
    with db.begin() as c:
        c.execute(text("delete from ops.alarm_candidates"))
        assert c.execute(text("select count(*) from ops.alarms where ml is not null")).scalar_one() == 0
