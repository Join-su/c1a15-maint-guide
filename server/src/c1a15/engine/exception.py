"""예외 안내 갈래(D-545 · 약속 v8) — 순수 함수(그래프 파일 · 망 · DB 0). Pack custom/judge.py가 쓰고, 앱 engine/exception.py는 이 파일의 사본(import 줄만 바뀜).
꼴 정본 = handoff/d545/graph-shape.md 3 · 4절: exception_relations 줄 {id, step, mode, grade, when{group, sensors[[칸, 연산, 값]], equipment_id?}, cause, records, n}
· sections 예외 줄 {no = app_no = EX-<이력 번호>, kind 예외, grade, name, guide, steps, criteria, group, minutes, records}.
흐름: 잠금 · 사전 확인 뒤 첫 점검 차례에 예외 절 먼저(등급 C → 파트장 승인 → 지시) → 결과 정상이면 원래 순서 다음 · 이상이면 조치 → 재가동 → 재가동 값 → 보고서."""
from c1a15.engine import rules, session

FIELDS = ("air_temperature_k", "process_temperature_k", "rotational_speed_rpm", "torque_nm", "tool_wear_min", "temp_diff_k", "power_w")
OPS = {">=": lambda a, b: a >= b, "<=": lambda a, b: a <= b, ">": lambda a, b: a > b, "<": lambda a, b: a < b, "=": lambda a, b: a == b}
PREFIX = "EX-"
BEFORE = {"instruct", "instruct_after_checklist", "call"}   # 첫 점검 차례(잠금 · 사전 확인 · 확인 질문 · 범위 밖 · 보고서 단계는 그대로)


class RuleError(ValueError):
    pass


def check(x, sec, names):
    """예외 관계 줄 꼴 검사 — 어기면 RuleError(그 그래프는 쓰지 않음)."""
    w = x.get("when") or {}
    if x.get("step") not in sec or w.get("group") not in names:
        raise RuleError(f"{x.get('id')}: 예외 관계가 가리키는 절 · 증상군이 그래프에 없음")
    for c in w.get("sensors") or []:
        if len(c) != 3 or c[0] not in FIELDS or c[1] not in OPS or isinstance(c[2], bool) or not isinstance(c[2], (int, float)):
            raise RuleError(f"{x.get('id')}: 예외 조건 칸이 허용 목록 밖")


def _parts(graph):
    sec = {s["no"]: s for s in graph["sections"] if s["kind"] == "예외"}
    return sec, {g["name"] for g in graph["groups"]}


def find(graph, rel_id):
    """관계 id → (관계 줄, 예외 절 줄) 또는 None(그래프 버전이 바뀌어 없어짐 → 예외 안내 없이 원래 판정)."""
    sec, names = _parts(graph)
    for x in graph.get("exception_relations") or []:
        if x.get("id") == rel_id and x.get("mode") == "안내":
            check(x, sec, names)
            return x, sec[x["step"]]
    return None


def match(graph, group, sensors, equipment_id=None):
    """알람 → 맞는 안내 관계 하나(증상군 · 센서 구간 · 같은 설비 모두 맞을 때). mode 참고는 판단에 안 씀.
    여럿 맞으면 좁은 것 먼저(D-546 덧 15): ① 설비 조건 있는 줄 → ② 센서 조건 줄 수 많은 줄 → ③ 근거 수 n 큰 줄 → ④ id 큰 줄(나중 관계 · D-546 덧 36)."""
    sec, names = _parts(graph)
    name = next(g["name"] for g in graph["groups"] if g["code"] == group)
    hits = []
    for x in graph.get("exception_relations") or []:
        if x.get("mode") != "안내":
            continue
        check(x, sec, names)
        w = x["when"]
        if w["group"] != name or (w.get("equipment_id") and w["equipment_id"] != equipment_id):
            continue
        if all(OPS[op](sensors[f], v) for f, op, v in w.get("sensors") or []):
            hits.append(x)
    if not hits:
        return None
    x = min(sorted(hits, key=lambda x: x["id"], reverse=True), key=lambda x: (not x["when"].get("equipment_id"), -len(x["when"].get("sensors") or []), -(x.get("n") or 0)))
    return x, sec[x["step"]]


def guide(ex, grades, minutes, next_section):
    """start 결과 exception_guide 칸(약속 v8) — next_section = 예외 절이 없었을 때의 다음 점검(정상이면 갈 곳) · minutes = 요청 분 표 → 없으면 그래프 줄."""
    x, sec = ex
    return {"section": sec["no"], "relation_id": x["id"], "grade": grades.get(sec["no"]) or sec.get("grade") or "C", "title": sec.get("name"),
            "text": sec.get("guide"), "steps": list(sec.get("steps") or []), "criteria": sec.get("criteria"), "basis": list(x.get("records") or sec.get("records") or []),
            "minutes": minutes.get(sec["no"]) or sec.get("minutes"), "next_section": next_section}


def without(events):
    """사본 session에 넘길 사건 — 예외 절 사건은 뺌(사본은 예외 절을 모름)."""
    return [e for e in events if not str(e.get("section") or "").startswith(PREFIX)]


def step(d, ex, events, grades, layer=None):
    """d = 예외 절 사건을 뺀 사본 판정(원래 순서) · events = 모든 사건 → 다음 단계 하나. 결과 정상이면 d 그대로.
    예외 갈래 결정에는 relation(관계 id)과 graph{used = 관계 id, layer = 그때 그래프 layer}를 붙임(실행 기록 · LLMOps ① · deploy K6가 읽음)."""
    out = _step(d, ex, events, grades)
    return out if out is d else {**out, "graph": {"used": ex[0]["id"], "layer": layer}}


def _step(d, ex, events, grades):
    x, sec = ex
    sid, cause = sec["no"], x.get("cause")
    base = {key: d[key] for key in ("probabilities", "evidence", "low_evidence") if key in d}
    mine = [e for e in events if e.get("section") == sid and not e.get("void")]
    results = [e.get("judged_value", e.get("value")) for e in mine if e["type"] == "result"]
    grade = grades.get(sid) or sec.get("grade") or "C"
    head = {"section": sid, "grade": grade, "cause": cause, "reason": "exception_guide", "relation": x["id"]}
    if not results:
        if d["kind"] not in BEFORE or d.get("corrected"):
            return d
        approved = any(e["type"] == "approval" or (e["type"] == "call_answer" and e.get("answer") == "approved") for e in mine)
        decision = rules.grade_decision("A" if approved else grade)
        if decision == "call":
            calls = [e for e in mine if e["type"] in ("call_sent", "call_wait")]
            out = {**base, "kind": "call", **head}
            return {**out, "call_status": "sent" if calls[-1]["type"] == "call_sent" else "waiting"} if calls else out
        return {**base, "kind": decision, **head}
    if results[-1] != "이상":
        return d   # 정상 · 확인 불가 → 원래 순서 다음 점검
    if not any(e["type"] == "action_done" for e in mine):
        return {**base, "kind": "action", **head, "stage": "action"}
    outcome = "confirmed" if cause else "unknown"
    seen = {e["type"]: e for e in events if not e.get("void")}
    if "report_confirm" in seen:
        return {**base, "kind": "closed"}
    if "restart" not in seen:
        return {**base, "kind": "restart_check", "section": session.RESTART_SECTION, "grade": grades.get(session.RESTART_SECTION),
                "cause": cause, "outcome": outcome, "relation": x["id"]}
    if "restart_result" not in seen:
        return {**base, "kind": "restart_value", "section": session.RESTART_SECTION, "cause": cause, "outcome": outcome, "relation": x["id"]}
    if seen["restart_result"].get("outcome") == "outside":
        return {**base, "kind": "handover", "reason": "restart_outside", "relation": x["id"]}
    return {**base, "kind": "report", "outcome": outcome, "cause": cause, "relation": x["id"]}
