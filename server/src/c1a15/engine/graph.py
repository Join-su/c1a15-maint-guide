"""LangGraph 껍데기(EP-C1-HITL-001): 판정은 session.decide가 하고, graph는 사람 입력을 기다렸다 이어 갈 뿐이다.

checkpoint는 재개 장치이고 감사 정본이 아니다. 업무 사실(event)은 API가 append-only로 따로 저장한다.
node는 재개 때 다시 실행될 수 있으므로 event는 업무 key(세션 ID + 순번)로 한 번만 반영한다.
"""

from collections.abc import Callable, Mapping
from typing import TypedDict

from langgraph.graph import END, START, StateGraph
from langgraph.types import interrupt

from c1a15.engine import rules, session
from c1a15.engine.knowledge import ManualKnowledge


class GraphState(TypedDict, total=False):
    group: str
    similar: list[dict]
    events: list[dict]
    decision: dict
    closed: bool


def build(
    k: ManualKnowledge,
    grades: Callable[[], Mapping[str, str]],
    minutes: Callable[[], Mapping[str, int]],
    checkpointer=None,
):
    def _similar(state: GraphState) -> list[rules.Similar]:
        return [rules.Similar(**s) for s in state.get("similar", [])]

    def decide(state: GraphState) -> GraphState:
        s = session.fold(k, state["group"], _similar(state), state.get("events", []))
        return {"decision": session.decide(s, k, grades(), minutes())}

    def wait(state: GraphState) -> GraphState:
        event = interrupt({"decision": state["decision"]})
        if event.get("type") == "close":
            return {"closed": True}
        events = list(state.get("events", []))
        if any(e.get("key") == event.get("key") for e in events):  # 같은 업무 key는 한 번만
            return {"events": events}
        if event.get("type") == "result":
            s = session.fold(k, state["group"], _similar(state), events)
            session.validate_result(s, state["decision"], event)
        return {"events": events + [event]}

    g = StateGraph(GraphState)
    g.add_node("decide", decide)
    g.add_node("wait", wait)
    g.add_edge(START, "decide")
    g.add_edge("decide", "wait")
    g.add_conditional_edges("wait", lambda s: END if s.get("closed") else "decide")
    return g.compile(checkpointer=checkpointer)
