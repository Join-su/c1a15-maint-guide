"""P-03 LangGraph 껍데기: 사람 입력 대기 → 재개, 다시 만든 graph(재시작)에서도 같은 단계, 같은 업무 key는 한 번만."""

import pytest
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

from c1a15.engine import graph, knowledge
from c1a15.engine.session import EventRejected
from c1a15.loader import core

SIMILAR = [
    {"record_id": "H-a", "cause": "CL-1", "score": 0.96},
    {"record_id": "H-b", "cause": "CL-1", "score": 0.91},
    {"record_id": "H-c", "cause": "CL-2", "score": 0.84},
]


@pytest.fixture(scope="module")
def setup(data_dir_module):
    sections = core.read_manual(data_dir_module)
    rows = core.grade_rows(sections)
    return (
        knowledge.from_sections(sections),
        {r["section_id"]: r["grade"] for r in rows},
        {r["section_id"]: r["minutes"] for r in rows},
    )


def decision_of(result):
    return result["__interrupt__"][0].value["decision"]


def test_pause_resume_restart_and_idempotency(setup):
    k, g, m = setup
    saver = InMemorySaver()
    cfg = {"configurable": {"thread_id": "session-1"}}
    app = graph.build(k, lambda: g, lambda: m, checkpointer=saver)
    assert decision_of(app.invoke({"group": "CL", "similar": SIMILAR, "events": []}, cfg))["kind"] == "lock"
    assert decision_of(app.invoke(Command(resume={"type": "lock", "key": "s1:1"}), cfg))["kind"] == "precheck"
    d = decision_of(app.invoke(Command(resume={"type": "precheck_done", "key": "s1:2"}), cfg))
    assert d["kind"] == "instruct" and d["section"] == "4.3"
    restarted = graph.build(k, lambda: g, lambda: m, checkpointer=saver)  # 프로세스 재시작 흉내
    assert restarted.get_state(cfg).values["decision"]["section"] == "4.3"  # 같은 단계로 재개(AC-14 판정 부분)
    d = decision_of(
        restarted.invoke(Command(resume={"type": "result", "section": "4.3", "value": "정상", "key": "s1:3"}), cfg)
    )
    assert d["kind"] == "call" and d["section"] == "4.4"
    d = decision_of(
        restarted.invoke(Command(resume={"type": "result", "section": "4.3", "value": "정상", "key": "s1:3"}), cfg)
    )
    assert len(restarted.get_state(cfg).values["events"]) == 3 and d["section"] == "4.4"  # 같은 key는 한 번만


def test_graph_rejects_result_before_lock(setup):
    k, g, m = setup
    app = graph.build(k, lambda: g, lambda: m, checkpointer=InMemorySaver())
    cfg = {"configurable": {"thread_id": "session-2"}}
    app.invoke({"group": "CL", "similar": SIMILAR, "events": []}, cfg)
    with pytest.raises(EventRejected, match="not_locked"):
        app.invoke(Command(resume={"type": "result", "section": "4.3", "value": "정상", "key": "s2:1"}), cfg)
