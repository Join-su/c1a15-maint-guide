# ruff: noqa: F811, E501 — test_api의 fixture(api · db)를 이름으로 가져와 쓴다, 시험 설명 문장은 길이 제한 밖
"""EV-001 ES-03(시험 DB): 적재기가 만든 첫 판 · 검색이 release를 읽음 · R12 새 판 · 판 실패 뒤 다음 시도 · 세션당 검색 1회.

VC-10(AC-09) · VC-11(DB 값으로) · VC-12 · VC-25.
"""

import json
from pathlib import Path

import pytest
from sqlalchemy import text

from test_api import api, db, reset_ops, start  # noqa: F401
from test_lead import confirmed_report, lead

pytestmark = pytest.mark.db
DATA = Path(__file__).resolve().parents[2] / "data"


def _active(db):
    with db.connect() as c:
        rid = c.execute(text("select release_id from knowledge.active_releases where kind = 'history'")).scalar_one()
        n = c.execute(
            text("select count(*) from knowledge.release_chunks where release_id = :r"), {"r": rid}
        ).scalar_one()
        parent = c.execute(
            text("select parent_release_id from knowledge.data_releases where release_id = :r"), {"r": rid}
        ).scalar_one()
        ids = {
            r
            for (r,) in c.execute(
                text("select metadata->>'record_id' from knowledge.release_chunks where release_id = :r"), {"r": rid}
            )
        }
    return rid, n, parent, ids


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


def test_vc11_db_release_docs_equal_legacy_docs(db):
    """DB 값으로: 활성 이력 release 조각(load_release_docs) ↔ 지금 표(history_records + history_embeddings, load_docs) — 시연 10건 상위 10 같음."""
    from c1a15.api import deps
    from c1a15.engine import alarm_rules
    from c1a15.ingest import store
    from c1a15.loader.embedding import fake_embedding
    from c1a15.retrieval import db as rdb
    from c1a15.retrieval import search

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


def test_vc10_r12_approval_makes_new_release(api, db):
    """AC-09 · CH-08: 승인 → 그 보고서 조각을 더한 새 이력 판(앞 판 = 지금 판, 조각 +1) → 검색 색인이 새 판을 읽음."""
    from c1a15.api import deps

    reset_ops(db)
    _, _, rid = confirmed_report(api, db)
    before, n0, _, ids0 = _active(db)
    r = lead(api).post(f"/api/lead/reports/{rid}/decision", json={"decision": "approve"})
    hid = r.json()["history_record_id"]
    after, n1, parent, ids1 = _active(db)
    assert r.status_code == 200 and after != before and parent == before and n1 == n0 + 1 and ids1 - ids0 == {hid}
    assert deps.index().release_id == after and any(d.record_id == hid for d in deps.index().docs)
    with db.connect() as c:  # 앞 판은 그대로(판 불변)
        assert (
            c.execute(
                text("select count(*) from knowledge.release_chunks where release_id = :r"), {"r": before}
            ).scalar_one()
            == n0
        )


def test_vc25_release_failure_keeps_approval_and_next_try_catches_up(api, db, monkeypatch):
    """판 만들기 실패 주입 → 승인은 저장 · 감사 'history_release_failed' · 가리킴 그대로 → 다음 승인 때 밀린 기록까지 새 판."""
    from c1a15.api import deps
    from c1a15.ingest import store

    reset_ops(db)
    _, _, rid1 = confirmed_report(api, db)
    _, _, rid2 = confirmed_report(api, db, equipment="M-03")
    before, n0, _, _ = _active(db)
    real = store.sync_history

    def boom(c):
        raise RuntimeError("판 만들기 실패(주입)")

    monkeypatch.setattr(store, "sync_history", boom)
    r1 = lead(api).post(f"/api/lead/reports/{rid1}/decision", json={"decision": "approve"})
    h1 = r1.json()["history_record_id"]
    with db.connect() as c:
        status = c.execute(text("select status from ops.reports where report_id = :r"), {"r": rid1}).scalar_one()
        failed = c.execute(
            text("select count(*) from ops.audit_log where action = 'history_release_failed'")
        ).scalar_one()
        stored = c.execute(
            text("select count(*) from knowledge.history_records where record_id = :i"), {"i": h1}
        ).scalar_one()
    assert r1.status_code == 200 and status == "approved" and stored == 1 and failed == 1
    assert _active(db)[0] == before and not any(d.record_id == h1 for d in deps.index().docs)
    monkeypatch.setattr(store, "sync_history", real)
    r2 = lead(api).post(f"/api/lead/reports/{rid2}/decision", json={"decision": "approve"})
    h2 = r2.json()["history_record_id"]
    after, n1, parent, ids1 = _active(db)
    assert after != before and parent == before and n1 == n0 + 2 and {h1, h2} <= ids1  # 다음 시도가 밀린 기록까지
    assert {h1, h2} <= {d.record_id for d in deps.index().docs}


def test_vc12_one_search_per_session(api, db, monkeypatch):
    """검색은 세션 시작 때 한 번(D-237 (2)) — 결과 입력 · 정정 등에서 다시 검색하지 않음."""
    from c1a15.retrieval import search

    calls = []
    real = search.similar_records
    monkeypatch.setattr(search, "similar_records", lambda *a, **k: calls.append(1) or real(*a, **k))
    reset_ops(db)
    tech, s = start(api, db)
    sid = s["session_id"]
    for etype in ("lock", "precheck_done"):
        s = tech.post(f"/api/tech/sessions/{sid}/events", json={"seq": s["last_seq"] + 1, "type": etype}).json()
    sec = s["instruction"]["section"]
    tech.post(
        f"/api/tech/sessions/{sid}/events",
        json={"seq": s["last_seq"] + 1, "type": "result", "section": sec, "value": "정상", "memo": "이상 없음"},
    )
    tech.get(f"/api/tech/sessions/{sid}")
    assert len(calls) == 1
