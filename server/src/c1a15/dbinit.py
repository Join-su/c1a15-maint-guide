"""DB 준비(compose `init`, EV-001 CH-39): python -m c1a15.dbinit

- 빈 DB(alembic_version 표가 없거나 행이 없음) = 첫 설치 → migration head + 적재기 + LangGraph checkpoint 표.
- 이미 설치된 DB = migration · 적재 0. DB 판이 이 이미지의 head와 같으면 그대로 끝(0),
  다르면 '사람 migration 필요' 메시지로 끝(1) — compose `api`는 init이 성공해야 뜨므로 앱이 서지 않는다.
- 사람 migration = 일회용 `migrate` 서비스(compose profile `migrate`). 운영 자료(승인 이력 · 등급 · 계정 · 운영 기록)는
  띄울 때마다 다시 넣지 않는다(PR-35).
"""

import sys
from pathlib import Path

from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import text

from c1a15.db.session import engine

ALEMBIC_INI = Path(__file__).resolve().parents[2] / "alembic.ini"
MIGRATE_HINT = "docker compose --profile migrate run --rm migrate"


def alembic_config() -> Config:
    cfg = Config(str(ALEMBIC_INI))
    cfg.set_main_option("script_location", str(ALEMBIC_INI.parent / "migrations"))
    return cfg


def current_revision() -> str | None:
    """설치된 판 — 표가 없거나 행이 없으면 None(빈 DB)."""
    with engine().connect() as c:
        if c.execute(text("select to_regclass('public.alembic_version')")).scalar() is None:
            return None
        return c.execute(text("select version_num from alembic_version")).scalar()


def main() -> int:
    cfg = alembic_config()
    head = ScriptDirectory.from_config(cfg).get_current_head()
    now = current_revision()
    if now is None:
        command.upgrade(cfg, "head")
        from c1a15.engine import checkpoint
        from c1a15.loader.__main__ import main as load

        print(f"dbinit: 빈 DB — migration head({head})", flush=True)
        load()
        checkpoint.main()
        return 0
    if now == head:
        print(f"dbinit: 이미 설치됨({now}) — migration · 적재 0", flush=True)
        return 0
    print(f"dbinit: DB 판 {now} ≠ 이미지 {head} — 사람 migration 필요: {MIGRATE_HINT}", flush=True)
    return 1


if __name__ == "__main__":
    sys.exit(main())
