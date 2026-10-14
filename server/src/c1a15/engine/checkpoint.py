"""LangGraph checkpoint 저장소(EP-C1-HITL-001): PostgreSQL, 진단 세션마다 thread 하나.

checkpoint는 재개 장치이고 감사 정본이 아니다. 정본은 API가 append-only로 저장하는 업무 기록(ops.session_events).
표 만들기(setup)는 init 단계에서 한 번: python -m c1a15.engine.checkpoint
"""

import sys
from collections.abc import Iterator
from contextlib import contextmanager

from langgraph.checkpoint.postgres import PostgresSaver

from c1a15.config import database_url


def conn_string() -> str:
    return database_url().replace("postgresql+psycopg://", "postgresql://")


@contextmanager
def saver() -> Iterator[PostgresSaver]:
    with PostgresSaver.from_conn_string(conn_string()) as s:
        yield s


def thread(session_id: int) -> dict:
    return {"configurable": {"thread_id": f"session-{session_id}"}}


def main() -> int:
    with saver() as s:
        s.setup()
    print("checkpoint: setup done")
    return 0


if __name__ == "__main__":
    sys.exit(main())
