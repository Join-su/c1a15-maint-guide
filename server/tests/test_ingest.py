# ruff: noqa: E501 — 시험 설명 문장은 길이 제한 밖
"""EV-001 ES-03: ingest · data release · 검색이 release를 읽음(DB 없이 — 적재 자료 data/로).

VC-08 같은 recipe → 같은 판 · VC-09 원문 위치로 조각 되찾기 · VC-11 release 검색 = 지금 검색(시연 10 · 카드 알람 전부) · VC-24 리트리버 설정 파일.
"""

import json
from pathlib import Path

import pytest

from c1a15 import ingest
from c1a15.api.sessions import GROUP_NAME
from c1a15.engine import alarm_rules
from c1a15.loader import core
from c1a15.loader.embedding import fake_embedding
from c1a15.retrieval import search, settings

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"


def _vec(text_vec: str) -> tuple[float, ...]:
    return tuple(float(x) for x in text_vec.strip("[]").split(","))


def _history():
    history = core.read_history(DATA)
    recs = [
        {"record_id": h["record_id"], "symptom_group": h["symptom_group"]["code"], "narrative": h["narrative"]}
        for h in history
    ]
    return recs, history


def test_vc08_same_recipe_same_release():
    recs, _ = _history()
    a = ingest.release(
        "history", ingest.HISTORY_RECIPE, ingest.history_chunks(recs), {"n": 1}, qs=ingest.queries(ingest.GROUP_NAME)
    )
    b = ingest.release(
        "history", ingest.HISTORY_RECIPE, ingest.history_chunks(recs), {"n": 2}, qs=ingest.queries(ingest.GROUP_NAME)
    )
    assert (a["release_id"], a["release_sha256"], a["recipe_sha256"]) == (
        b["release_id"],
        b["release_sha256"],
        b["recipe_sha256"],
    )
    other = ingest.release("history", {**ingest.HISTORY_RECIPE, "overlap": 1}, ingest.history_chunks(recs), {"n": 1})
    assert (
        other["release_id"] != a["release_id"] and other["recipe_sha256"] != a["recipe_sha256"]
    )  # recipe가 바뀌면 다른 판
    fewer = ingest.release("history", ingest.HISTORY_RECIPE, ingest.history_chunks(recs[:-1]), {"n": 1})
    assert fewer["release_id"] != a["release_id"]  # 조각이 바뀌면 다른 판
    assert len(a["chunks"]) == 300 and all(c["chunk_id"].endswith("#0") for c in a["chunks"])  # 기본 recipe '1건 1조각'


def test_vc09_locator_recovers_chunk():
    md = (DATA / "manuals" / "MG-MM.md").read_text(encoding="utf-8")
    sections = core.read_manual(DATA)
    chunks = ingest.manual_chunks(md, sections)
    assert len(chunks) == sum(1 for s in sections if s.get("text")) and chunks
    for c in chunks:
        assert (
            ingest.locate(c, md) == c["text"]
            and c["locator"]["doc"] == "MG-MM"
            and c["locator"]["section"] == c["metadata"]["section"]
        )
    recs, _ = _history()
    for c, r in zip(ingest.history_chunks(recs), recs, strict=True):
        assert ingest.locate(c, r["narrative"]) == r["narrative"] == c["text"]


def test_group_names_same_as_session_start():
    assert ingest.GROUP_NAME == GROUP_NAME  # 미리 계산한 질의 = 세션 시작 질의 글


def test_vc24_retriever_settings_file(tmp_path):
    cfg = settings.load(DATA / "retriever.json")
    assert cfg == search.DEFAULT and cfg.top_k == 10  # 파일 값 = 지금 검색 숫자, 상위 k 10 고정
    raw = (DATA / "retriever.json").read_text(encoding="utf-8")
    body = json.loads(raw)
    assert not settings.USER_SETTING_NAMES & set(body) and "about" in body
    for bad in ({"alpha": 0.5}, {"top_k": 12}, {"similarity_threshold": 0.3}, {"call_threshold": 50}):
        p = tmp_path / "r.json"
        p.write_text(json.dumps({**body, **bad}), encoding="utf-8")
        with pytest.raises(ValueError):
            settings.load(p)


def _alarms():
    table = alarm_rules.load(DATA / "alarm_rules.json")
    out = []
    for s in json.loads((DATA / "demo" / "scenarios.json").read_text(encoding="utf-8"))["scenarios"]:
        out.append((s["scenario_id"], s["sensor_snapshot"]))
    for p in sorted((ROOT / "eval" / "cards").glob("*/card_inputs.json")):  # 카드의 알람 입력만(정답 없음)
        out += [(c["card_id"], c["sensor_snapshot"]) for c in json.loads(p.read_text(encoding="utf-8"))]
    return [(name, snap, alarm_rules.detect(snap, table)) for name, snap in out]


def test_vc11_release_search_equals_current_search():
    """지금 길(이력 행 + 1건 1벡터, 질의 = 그때 가짜 임베딩) ↔ release 길(조각 · 조각 벡터, 질의 = release에 미리 계산한 벡터)."""
    recs, history = _history()
    rel = ingest.release(
        "history", ingest.HISTORY_RECIPE, ingest.history_chunks(recs), {}, qs=ingest.queries(ingest.GROUP_NAME)
    )
    by_id = {h["record_id"]: h for h in history}
    legacy = [
        search.HistoryDoc(
            h["record_id"],
            h["symptom_group"]["code"],
            h["narrative"],
            h["sensor_snapshot"],
            h["outcome"].get("cause_code"),
            _vec(ingest.vec_text(fake_embedding(h["narrative"]))),
        )
        for h in history
    ]
    released = [
        search.HistoryDoc(
            c["metadata"]["record_id"],
            c["metadata"]["symptom_group"],
            c["text"],
            by_id[c["metadata"]["record_id"]]["sensor_snapshot"],
            by_id[c["metadata"]["record_id"]]["outcome"].get("cause_code"),
            _vec(ingest.vec_text(c["embedding"])),
        )
        for c in rel["chunks"]
    ]
    a, b = (
        search.Index(legacy),
        search.Index(released, settings.load(DATA / "retriever.json"), rel["release_id"], rel["queries"]),
    )
    stats = search.sensor_stats(legacy)
    assert stats == search.sensor_stats(released)
    alarms = _alarms()
    assert len(alarms) == 70 and all(hit for _, _, hit in alarms)
    for name, snap, hit in alarms:
        g = hit["group"]
        q = search.query_text(GROUP_NAME[g], hit["alarm"]["direction"], [])
        top_a = search.similar_records(
            {"symptom_group": g},
            q,
            snap,
            a.docs,
            a.bm25,
            search.cosine_rank(fake_embedding(q), [d for d in a.docs if d.symptom_group == g]),
            stats,
        )
        top_b = search.similar_records(
            {"symptom_group": g},
            q,
            snap,
            b.docs,
            b.bm25,
            search.cosine_rank(list(_vec(b.queries[q])), [d for d in b.docs if d.symptom_group == g]),
            stats,
            b.cfg,
        )
        assert [(t.record_id, t.score) for t in top_a] == [(t.record_id, t.score) for t in top_b], name
