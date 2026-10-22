"""적재기 CLI(FLOW-11): python -m c1a15.loader. 한 번 실행하며 실패하면 트랜잭션 전체를 되돌린다."""

import os
import sys
from pathlib import Path

from sqlalchemy import delete, insert

from c1a15 import ingest
from c1a15.config import require_env
from c1a15.db import models as m
from c1a15.db.session import engine
from c1a15.ingest import store as release_store
from c1a15.loader import core
from c1a15.loader.embedding import FAKE_MODEL, fake_embedding


def main() -> int:
    data_dir = Path(os.environ.get("DATA_DIR", "/data"))
    sections = core.read_manual(data_dir)
    history = core.read_history(data_dir)
    seeds = core.account_seeds(require_env("C1A15_TECH_PASSWORD"), require_env("C1A15_LEAD_PASSWORD"))
    with engine().begin() as conn:
        for table in (
            m.ActiveRelease,
            m.ReleaseChunk,
            m.DataRelease,
            m.HistoryEmbedding,
            m.CommonPrecheckItem,
            m.EquipmentAssignment,
            m.GradeEntry,
            m.Account,
            m.HistoryRecord,
            m.ManualSection,
        ):
            conn.execute(delete(table))
        conn.execute(
            insert(m.ManualSection),
            [
                {
                    "section_id": s["id"],
                    "title": s["title"],
                    "kind": s["kind"],
                    "chapter": s["chapter"],
                    "symptom_group": s.get("group"),
                    "initial_grade": s.get("grade"),
                    "minutes": s.get("minutes"),
                    "parent_section": s.get("parent"),
                    "text": s.get("text"),
                }
                for s in sections
            ],
        )
        conn.execute(insert(m.HistoryRecord), core.history_rows(history))
        conn.execute(
            insert(m.HistoryEmbedding),
            [
                {"record_id": h["record_id"], "embedding": fake_embedding(h["narrative"]), "model": FAKE_MODEL}
                for h in history
            ],
        )
        conn.execute(insert(m.Account), [s.__dict__ for s in seeds])
        conn.execute(insert(m.GradeEntry), [{**g, "updated_by": "loader"} for g in core.grade_rows(sections)])
        conn.execute(insert(m.EquipmentAssignment), core.equipment_assignments(history))
        conn.execute(insert(m.CommonPrecheckItem), core.common_precheck_items(sections))
        # EV-001 CH-05: 처음 data release 둘
        # — 이력(기본 recipe '1건 1조각', 질의 벡터 미리 계산) · 매뉴얼(절 단위, 검색 평가용)
        hist = ingest.release(
            "history",
            ingest.HISTORY_RECIPE,
            ingest.history_chunks(
                [
                    {
                        "record_id": h["record_id"],
                        "symptom_group": h["symptom_group"]["code"],
                        "narrative": h["narrative"],
                    }
                    for h in history
                ]
            ),
            {
                "rows": "분할 v2 train 행 생성 이력",
                "file": "history/maintenance_history.jsonl",
                "sha256": ingest.sha256((data_dir / "history" / "maintenance_history.jsonl").read_bytes()),
                "records": len(history),
            },
            qs=ingest.queries(ingest.GROUP_NAME),
        )
        manual_md = (data_dir / "manuals" / "MG-MM.md").read_text(encoding="utf-8")
        man = ingest.release(
            "manual",
            ingest.MANUAL_RECIPE,
            ingest.manual_chunks(manual_md, sections),
            {"doc": ingest.MANUAL_DOC, "file": "manuals/MG-MM.md", "sha256": ingest.sha256(manual_md.encode("utf-8"))},
        )
        for rel in (hist, man):
            release_store.write(conn, rel)
            release_store.activate(conn, rel["kind"], rel["release_id"])
    print(
        f"loaded sections={len(sections)} history={len(history)} accounts={len(seeds)} "
        f"releases={hist['release_id']},{man['release_id']}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
