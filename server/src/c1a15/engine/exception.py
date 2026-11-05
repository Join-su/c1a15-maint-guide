"""예외 안내 갈래(D-545 · 약속 v8) — 순수 함수(그래프 파일 · 망 · DB 0). Pack custom/judge.py가 쓰고, 앱 engine/exception.py는 이 파일의 사본(import 줄만 바뀜).
꼴 정본 = handoff/d545/graph-shape.md 3 · 4절: exception_relations 줄 {id, step, mode, grade, when{group, sensors[[칸, 연산, 값]], equipment_id?}, cause, records, n}
· sections 예외 줄 {no = app_no = EX-<이력 번호>, kind 예외, grade, name, guide, steps, criteria, group, minutes, records}.
흐름(약속 v10 · D-566 덧 1): 잠금 · 사전 확인 뒤 첫 점검 차례에 예외 절 먼저 → 등급 C면 파트장 승인 **예외 전체에 한 번** →
**걸음마다** 점검 c1 → c2 … → 조치 a1 → a2 …(적은 순서 · 결과로 건너뛰지 않음 · 사건 step 칸) → 재가동 → 재가동 값 →
정상(안)이면 보고서(반려 뒤 다시 보고서) · 아니면(밖) **원래 점검 순서(4.3 …)**(D-566 덧 2 · 그 재가동 둘은 원래 순서 판정에서 뺌).
점검 · 조치 목록이 없는 옛 예외 절(check · action 칸 0)은 옛 길: 예외 절 점검 하나 → 결과 정상이면 원래 순서 · 이상이면 조치 → 재가동 → 보고서."""
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


def lists(sec):
    """예외 절의 (점검 목록, 조치 목록) — v10 checks · actions · 옛 하나 꼴(check · action)은 목록 하나로 · 없으면 빈 목록."""
    checks = list(sec.get("checks") or ([sec["check"]] if sec.get("check") else []))
    actions = list(sec.get("actions") or ([sec["action"]] if sec.get("action") else []))
    return checks, actions


def walk(sec):
    """걸음 차례 [(step, 'check' | 'action', 칸)] — 점검 c1 · c2 … 다음 조치 a1 · a2 …(적은 순서)."""
    checks, actions = lists(sec)
    return [(f"c{i}", "check", c) for i, c in enumerate(checks, 1)] + [(f"a{i}", "action", a) for i, a in enumerate(actions, 1)]


def guide(ex, grades, minutes, next_section):
    """start 결과 exception_guide 칸(약속 v8) — next_section = 예외 절이 없었을 때의 다음 점검(정상이면 갈 곳) · minutes = 요청 분 표 → 없으면 그래프 줄.
    D-554 · v10(D-566): 예외 절 줄의 주제 · 점검 목록 · 조치 목록 · 덧붙임(topic · checks · actions · note)은 있을 때만 그대로 싣음."""
    x, sec = ex
    out = {"section": sec["no"], "relation_id": x["id"], "grade": grades.get(sec["no"]) or sec.get("grade") or "C", "title": sec.get("name"),
           "text": sec.get("guide"), "steps": list(sec.get("steps") or []), "criteria": sec.get("criteria") or None, "basis": list(x.get("records") or sec.get("records") or []),
           "minutes": minutes.get(sec["no"]) or sec.get("minutes"), "next_section": next_section}
    checks, actions = lists(sec)
    return {**out, **({"checks": checks} if checks else {}), **({"actions": actions} if actions else {}), **{k: sec[k] for k in ("topic", "note") if sec.get(k)}}


def phase_restart(events, ex):
    """걸음 길에서 마지막 걸음이 끝난 뒤 첫 재가동 · 그 뒤 첫 재가동 값의 차례 번호(없으면 None) — 예외 몫 재가동(D-566 덧 2)."""
    sec = ex[1]
    steps = {name for name, _, _ in walk(sec)}
    if not (lists(sec)[0] and lists(sec)[1]):
        return None, None
    done, end = set(), None
    for i, e in enumerate(events):
        if e.get("void") or e.get("section") != sec["no"]:
            continue
        if (e["type"] == "result" and str(e.get("step", "")).startswith("c")) or (e["type"] == "action_done" and str(e.get("step", "")).startswith("a")):
            done.add(e.get("step"))
            if steps <= done and end is None:
                end = i
    if end is None:
        return None, None
    r = next((i for i in range(end + 1, len(events)) if events[i]["type"] == "restart" and not events[i].get("void")), None)
    v = next((i for i in range(r + 1, len(events)) if events[i]["type"] == "restart_result" and not events[i].get("void")), None) if r is not None else None
    return r, v


def base_events(events, ex):
    """원래 순서 판정(사본 session)에 넘길 사건 — 예외 절 사건과 예외 몫 재가동 둘을 뺌."""
    r, v = phase_restart(events, ex)
    return without([e for i, e in enumerate(events) if i not in (r, v)])


def without(events):
    """사본 session에 넘길 사건 — 예외 절 사건은 뺌(사본은 예외 절을 모름)."""
    return [e for e in events if not str(e.get("section") or "").startswith(PREFIX)]


def step(d, ex, events, grades, layer=None):
    """d = 예외 절 사건을 뺀 사본 판정(원래 순서) · events = 모든 사건 → 다음 단계 하나. 결과 정상이면 d 그대로.
    예외 갈래 결정에는 relation(관계 id)과 graph{used = 관계 id, layer = 그때 그래프 layer}를 붙임(실행 기록 · LLMOps ① · deploy K6가 읽음)."""
    out = _step(d, ex, events, grades)
    return out if out is d else {**out, "graph": {"used": ex[0]["id"], "layer": layer}}


def _confirmed(events):
    """보통 세션과 같게 차례대로 — 확정 → 닫힘 · 파트장 반려(report_rejected) → 보고서 다시 열림(D-560 · 반려 뒤 결함 고침)."""
    out = False
    for e in events:
        if e["type"] in ("report_confirm", "report_rejected") and not e.get("void"):
            out = e["type"] == "report_confirm"
    return out


def _after(base, events, grades, cause, x):
    """모든 걸음 · 조치가 끝난 뒤 — 재가동 → 재가동 값 → 보고서(원인 있으면 confirmed · 없으면 unknown) · 재가동 밖이면 인계."""
    outcome = "confirmed" if cause else "unknown"
    seen = {e["type"]: e for e in events if not e.get("void")}
    if _confirmed(events):
        return {**base, "kind": "closed"}
    if "restart" not in seen:
        return {**base, "kind": "restart_check", "section": session.RESTART_SECTION, "grade": grades.get(session.RESTART_SECTION),
                "cause": cause, "outcome": outcome, "relation": x["id"]}
    if "restart_result" not in seen:
        return {**base, "kind": "restart_value", "section": session.RESTART_SECTION, "cause": cause, "outcome": outcome, "relation": x["id"]}
    if seen["restart_result"].get("outcome") == "outside":
        return {**base, "kind": "handover", "reason": "restart_outside", "relation": x["id"]}
    return {**base, "kind": "report", "outcome": outcome, "cause": cause, "relation": x["id"]}


def _approval(mine, grade, base, head):
    """등급 C · D 예외 절 — 파트장 승인 예외 전체에 한 번(D-566 덧 1 Q2) · 승인 전이면 call(보냄 · 기다림) · 승인 뒤 None."""
    approved = any(e["type"] == "approval" or (e["type"] == "call_answer" and e.get("answer") == "approved") for e in mine)
    if rules.grade_decision("A" if approved else grade) != "call":
        return None
    calls = [e for e in mine if e["type"] in ("call_sent", "call_wait")]
    out = {**base, "kind": "call", **head}
    return {**out, "call_status": "sent" if calls[-1]["type"] == "call_sent" else "waiting"} if calls else out


def _walk_step(d, ex, events, grades, steps):
    """v10 걸음 길: 승인 한 번 → c1 … → a1 … 모두(결과로 건너뛰지 않음) → 재가동 → 보고서."""
    x, sec = ex
    sid, cause = sec["no"], x.get("cause")
    base = {key: d[key] for key in ("probabilities", "evidence", "low_evidence") if key in d}
    mine = [e for e in events if e.get("section") == sid and not e.get("void")]
    done = {e.get("step") for e in mine if (e["type"] == "result" and str(e.get("step", "")).startswith("c")) or (e["type"] == "action_done" and str(e.get("step", "")).startswith("a"))}
    started = bool(done) or any(e["type"] in ("approval", "call_answer", "call_sent", "call_wait") for e in mine)
    if not started and (d["kind"] not in BEFORE or d.get("corrected")):
        return d
    grade = grades.get(sid) or sec.get("grade") or "C"
    head = {"section": sid, "grade": grade, "cause": cause, "reason": "exception_guide", "relation": x["id"], "steps_total": len(steps)}
    wait = _approval(mine, grade, base, head)
    if wait:
        return wait
    for i, (name, side, item) in enumerate(steps, 1):
        if name in done:
            continue
        at = {**head, "step": name, "step_index": i, side: item}
        if side == "check":
            return {**base, "kind": "instruct", **at}
        return {**base, "kind": "action", **at, "stage": "action"}
    r, v = phase_restart(events, ex)   # D-566 덧 2: 예외 안내 뒤 재가동 확인
    outcome = "confirmed" if cause else "unknown"
    if r is None:
        return {**base, "kind": "restart_check", "section": session.RESTART_SECTION, "grade": grades.get(session.RESTART_SECTION), "cause": cause, "outcome": outcome, "relation": x["id"]}
    if v is None:
        return {**base, "kind": "restart_value", "section": session.RESTART_SECTION, "cause": cause, "outcome": outcome, "relation": x["id"]}
    if events[v].get("outcome") == "outside":
        return d   # 정상 아님 → 원래 점검 순서(그 재가동 둘을 뺀 사본 판정 · 그 뒤는 보통 세션)
    if _confirmed(events):
        return {**base, "kind": "closed"}
    return {**base, "kind": "report", "outcome": outcome, "cause": cause, "relation": x["id"]}


def _step(d, ex, events, grades):
    x, sec = ex
    steps = walk(sec)
    if steps and lists(sec)[0] and lists(sec)[1]:
        return _walk_step(d, ex, events, grades, steps)
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
    return _after(base, events, grades, cause, x)   # 옛 길도 반려 뒤 다시 보고서(D-560 결함 고침)
