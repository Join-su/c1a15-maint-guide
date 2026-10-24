"""적재기 CLI(FLOW-11): python -m c1a15.loader. 한 번 실행하며 실패하면 트랜잭션 전체를 되돌린다."""

import os
import sys
from pathlib import Path

from sqlalchemy import delete, insert

from c1a15.config import require_env
from c1a15.db import models as m
from c1a15.db.session import engine
from c1a15.loader import core


def main() -> int:
    data_dir = Path(os.environ.get("DATA_DIR", "/data"))
    sections = core.read_manual(data_dir)
    history = core.read_history(data_dir)
    seeds = core.account_seeds(require_env("C1A15_TECH_PASSWORD"), require_env("C1A15_LEAD_PASSWORD"))
    with engine().begin() as conn:
        # EV-001 ES-18(CH-33): release · 벡터는 쓰지 않음. 옛 행이 남은 DB에서 이력 지우기가 외래 키로 막히지 않게
        # 네 표(active · chunk · release · embedding)는 비우기만 — 표 자체는 migration 0009(ES-19)에서 지움.
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
        conn.execute(insert(m.Account), [s.__dict__ for s in seeds])
        conn.execute(insert(m.GradeEntry), [{**g, "updated_by": "loader"} for g in core.grade_rows(sections)])
        conn.execute(insert(m.EquipmentAssignment), core.equipment_assignments(history))
        conn.execute(insert(m.CommonPrecheckItem), core.common_precheck_items(sections))
    print(f"loaded sections={len(sections)} history={len(history)} accounts={len(seeds)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
