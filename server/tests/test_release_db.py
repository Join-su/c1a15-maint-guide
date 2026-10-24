# ruff: noqa: F811, E501 — test_api의 fixture(api · db)를 이름으로 가져와 쓴다, 시험 설명 문장은 길이 제한 밖
"""EV-001 ES-03(시험 DB): 적재기가 만든 첫 판 · 검색이 release를 읽음(파일 전체는 ES-18에서 지움).

VC-11(DB 값으로). VC-10 · VC-25는 ES-17, VC-12는 ES-16에서 지움.
"""

import json
from pathlib import Path

import pytest
from sqlalchemy import text

from test_api import api, db, reset_ops, start  # noqa: F401

pytestmark = pytest.mark.db
DATA = Path(__file__).resolve().parents[2] / "data"


def test_loader_makes_first_releases(db):
    with db.connect() as c:
        rows = {k: r for k, r in c.execute(text("select kind, release_id from knowledge.active_releases"))}
        assert set(rows) == {"history", "manual"}
        q = c.execute(
            text("select queries from knowledge.data_releases where release_id = :r"), {"r": rows["history"]}
        ).scalar_one()
        man = c.execute(
            text("select count(*) from knowledge.release_chunks where release_id = :r"), {"r": rows["manual"]}
        ).scalar_one()
        gen = c.execute(text("select count(*) from knowledge.history_records where source = 'generated'")).scalar_one()
        hist_gen = c.execute(
            text(
                "select count(*) from knowledge.release_chunks c join knowledge.history_records r on r.record_id = c.metadata->>'record_id' "
                "where c.release_id = :r and r.source = 'generated'"
            ),
            {"r": rows["history"]},
        ).scalar_one()
    assert len(q) == 8 and man > 0 and hist_gen == gen == 300  # 질의 = 증상군 4 × 방향 2 · 이력 조각 = 생성 이력 300


def test_vc11_db_release_docs_equal_legacy_docs(db, monkeypatch):
    """DB 값으로: 활성 이력 release 조각(load_release_docs) ↔ 지금 표(history_records + history_embeddings, load_docs) — 시연 10건 상위 10 같음."""
    from c1a15.api import deps
    from c1a15.engine import alarm_rules
    from c1a15.ingest import store
    from c1a15.loader.embedding import fake_embedding
    from c1a15.retrieval import db as rdb
    from c1a15.retrieval import search

    monkeypatch.setenv("DATA_DIR", str(DATA))  # deps.retriever() — 앞 시험의 캐시에 기대지 않음
    with db.connect() as c:
        cur = store.active(c, "history")
        legacy, released = rdb.load_docs(c), rdb.load_release_docs(c, cur["release_id"])
    assert {d.record_id for d in legacy} == {d.record_id for d in released}
    a, b = search.Index(legacy), search.Index(released, deps.retriever(), cur["release_id"], cur["queries"])
    stats = search.sensor_stats(legacy)
    table = alarm_rules.load(DATA / "alarm_rules.json")
    for s in json.loads((DATA / "demo" / "scenarios.json").read_text(encoding="utf-8"))["scenarios"]:
        hit = alarm_rules.detect(s["sensor_snapshot"], table)
        g = hit["group"]
        from c1a15.api.sessions import GROUP_NAME

        q = search.query_text(GROUP_NAME[g], hit["alarm"]["direction"], [])
        pa = [d for d in a.docs if d.symptom_group == g]
        pb = [d for d in b.docs if d.symptom_group == g]
        ta = search.similar_records(
            {"symptom_group": g},
            q,
            s["sensor_snapshot"],
            a.docs,
            a.bm25,
            search.cosine_rank(fake_embedding(q), pa),
            stats,
        )
        qv = [float(x) for x in b.queries[q].strip("[]").split(",")]
        tb = search.similar_records(
            {"symptom_group": g}, q, s["sensor_snapshot"], b.docs, b.bm25, search.cosine_rank(qv, pb), stats, b.cfg
        )
        assert [(t.record_id, t.score) for t in ta] == [(t.record_id, t.score) for t in tb], s["scenario_id"]


# VC-10 · VC-25(승인 → 앱 새 이력 release · 판 실패 뒤 다음 시도)는 EV-001 ES-17(CH-32)에서 지움 — R12는 배포 서버 몫(PR-25 · deploy KS-5).


def test_alarm_candidates_reason_check(db):
    """EV-001 ES-04(가): '사람 판단 필요' 기록 표 — 사유는 low_confidence · rnf · model_failure만, 경계 길 알람의 ml 칸은 null."""
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
