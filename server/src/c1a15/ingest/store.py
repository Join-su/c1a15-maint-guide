"""data release DB 쓰기 · 읽기(knowledge.data_releases · release_chunks · active_releases). 판은 고치지 않는다
— 새 판을 더하고 가리킴만 옮긴다.
"""

import json

from sqlalchemy import Connection, text

from c1a15 import ingest


def write(c: Connection, rel: dict) -> bool:
    """판을 넣는다. 같은 판(release_id)이 이미 있으면 그대로 둔다(같은 입력 = 같은 판)."""
    if c.execute(text("select 1 from knowledge.data_releases where release_id = :r"), {"r": rel["release_id"]}).first():
        return False
    c.execute(  # 같은 판을 동시에 넣으면 앞 것이 이김(판 내용은 hash로 같음)
        text(
            "insert into knowledge.data_releases (release_id, kind, recipe, recipe_sha256, "
            "embedding_model, embedding_dim, source, "
            "parent_release_id, release_sha256, queries) values (:id, :k, cast(:rc as jsonb), :rs, :m, :d, "
            "cast(:s as jsonb), :p, :h, cast(:q as jsonb)) on conflict (release_id) do nothing"
        ),
        {
            "id": rel["release_id"],
            "k": rel["kind"],
            "rc": json.dumps(rel["recipe"]),
            "rs": rel["recipe_sha256"],
            "m": rel["embedding_model"],
            "d": rel["embedding_dim"],
            "s": json.dumps(rel["source"], ensure_ascii=False),
            "p": rel["parent_release_id"],
            "h": rel["release_sha256"],
            "q": json.dumps(rel["queries"], ensure_ascii=False),
        },
    )
    c.execute(
        text(
            "insert into knowledge.release_chunks (release_id, chunk_id, doc, locator, text, metadata, embedding) "
            "values (:r, :c, :d, cast(:l as jsonb), :t, cast(:md as jsonb), cast(:e as vector))"
        ),
        [
            {
                "r": rel["release_id"],
                "c": ch["chunk_id"],
                "d": ch["doc"],
                "l": json.dumps(ch["locator"], ensure_ascii=False),
                "t": ch["text"],
                "md": json.dumps(ch["metadata"], ensure_ascii=False),
                "e": ingest.vec_text(ch["embedding"]),
            }
            for ch in rel["chunks"]
        ],
    )
    return True


def activate(c: Connection, kind: str, release_id: str) -> None:
    c.execute(
        text(
            "insert into knowledge.active_releases (kind, release_id) values (:k, :r) on conflict (kind) "
            "do update set release_id = excluded.release_id"
        ),
        {"k": kind, "r": release_id},
    )


def active(c: Connection, kind: str) -> dict | None:
    row = c.execute(
        text(
            "select d.release_id, d.queries from knowledge.active_releases a join knowledge.data_releases "
            "d using (release_id) where a.kind = :k"
        ),
        {"k": kind},
    ).first()
    return {"release_id": row[0], "queries": row[1]} if row else None


def chunks(c: Connection, release_id: str) -> list[dict]:
    rows = c.execute(
        text(
            "select chunk_id, doc, locator, text, metadata, embedding::text from knowledge.release_chunks "
            "where release_id = :r order by chunk_id"
        ),
        {"r": release_id},
    ).all()
    return [
        {
            "chunk_id": cid,
            "doc": doc,
            "locator": loc,
            "text": t,
            "metadata": md,
            "embedding": [float(x) for x in emb.strip("[]").split(",")],
        }
        for cid, doc, loc, t, md, emb in rows
    ]


def sync_history(c: Connection) -> str | None:
    """R12(CH-08): 활성 이력 판에 없는 이력 기록
    (승인 보고서)이 있으면 그것을 더한 새 판을 만들고 가리킴을 옮긴다. 새 판 ID 또는 None.
    """
    c.execute(
        text("select pg_advisory_xact_lock(hashtext('c1a15.history_release'))")
    )  # 승인 둘이 겹쳐도 판은 차례로(transaction 끝에 풀림)
    cur = active(c, "history")
    if cur is None:
        raise RuntimeError("활성 이력 release가 없음 — 적재기(python -m c1a15.loader)를 먼저 돌려야 함")
    have = chunks(c, cur["release_id"])
    in_release = {ch["metadata"]["record_id"] for ch in have}
    rows = c.execute(
        text("select record_id, symptom_group, narrative from knowledge.history_records order by record_id")
    ).all()
    missing = [{"record_id": r, "symptom_group": g, "narrative": n} for r, g, n in rows if r not in in_release]
    if not missing:
        return None
    parent = c.execute(
        text("select source from knowledge.data_releases where release_id = :r"), {"r": cur["release_id"]}
    ).scalar_one()
    rel = ingest.release(
        "history",
        ingest.HISTORY_RECIPE,
        have + ingest.history_chunks(missing),
        {**parent, "added": sorted(m["record_id"] for m in missing)},
        parent=cur["release_id"],
        qs=cur["queries"],
    )
    write(c, rel)
    activate(c, "history", rel["release_id"])
    return rel["release_id"]
