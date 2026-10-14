"""DB 쪽 검색 입력: 이력 문서 읽기 · pgvector 의미 검색 순위(같은 증상군 필터만)."""

from sqlalchemy import Connection, text

from c1a15.retrieval.search import HistoryDoc, check_filters


def load_docs(conn: Connection) -> list[HistoryDoc]:
    rows = conn.execute(
        text(
            "select r.record_id, r.symptom_group, r.narrative, r.sensor_snapshot, "
            "r.record -> 'outcome' ->> 'cause_code', e.embedding::text, r.source "
            "from knowledge.history_records r join knowledge.history_embeddings e using (record_id)"
        )
    ).all()
    return [
        HistoryDoc(rid, grp, narr, sensor, cause, tuple(float(x) for x in emb.strip("[]").split(",")), source)
        for rid, grp, narr, sensor, cause, emb, source in rows
    ]


def vector_ranks(conn: Connection, filters: dict, query_vec: list[float], limit: int = 300) -> list[str]:
    check_filters(filters)
    rows = conn.execute(
        text(
            "select r.record_id from knowledge.history_embeddings e join knowledge.history_records r using (record_id) "
            "where r.symptom_group = :g order by e.embedding <=> cast(:q as vector), r.record_id limit :n"
        ),
        {"g": filters["symptom_group"], "q": "[" + ",".join(f"{v:.8f}" for v in query_vec) + "]", "n": limit},
    ).all()
    return [r[0] for r in rows]
