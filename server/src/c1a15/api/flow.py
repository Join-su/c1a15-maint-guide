"""S-03(P-09, B-04): 조치 · 재가동 · 재가동 후 값 · 감시 마감 · 호출 · 숙련자 인계 · 보고서.

판정(다음 단계)은 engine.session.decide, 문장은 llm adapter(fixture 기본) + R8 근거 검사, 저장은 append-only 업무 기록 +
목록용 투영(ops.calls · ops.reports) + 감사. 화면은 여기서 만든 값만 보인다.
보고서 8항목 = 명세 R10, 계산 세부 = 사용자 결정 015(sources/intent/015.md).
"""

import hashlib
import json
import re
from datetime import UTC, datetime

from fastapi import HTTPException
from sqlalchemy import Connection, select

from c1a15.api import deps, screen
from c1a15.db import models as m
from c1a15.deploy import runs
from c1a15.deploy.client import PackUnavailable
from c1a15.engine import rules, session
from c1a15.engine.knowledge import ManualKnowledge
from c1a15.llm import adapter_for_mode, grounding
from c1a15.llm.base import AdapterError, Draft, Facts

# 정비자 앱이 보내는 S-03 입력(클라이언트 type) → 업무 기록 type
CLIENT_TYPES = {
    "action_done",
    "restart",
    "restart_result",
    "monitor_close",
    "call_send",
    "call_wait",
    "report_edit",
    "report_confirm",
    "handover_request",
}
# 판정 엔진이 접는 S-03 업무 기록(파트장 답 call_answer는 S-04 P-11이 쓴다)
ENGINE_TYPES = {
    "action_done",
    "restart",
    "restart_result",
    "monitor_close",
    "call_wait",
    "call_sent",
    "call_answer",
    "report_confirm",
    "handover_request",
    "report_rejected",
}

MEMO_SUMMARY_CHARS = 30  # 결정 015 ②
REPORT_FIELDS = [  # 명세 R10: (키, 항목, 출처 표시)
    ("equipment_alarm", "설비 · 알람", "자동"),
    ("sensor_evidence", "센서 근거", "센서"),
    ("check_path", "점검 경로", "입력"),
    ("cause", "확정 원인", "입력"),
    ("evidence_records", "근거 사례", "기록"),
    ("action", "조치", "매뉴얼"),
    ("downtime", "정지 시간", "자동"),
    ("unresolved", "미확인 · 요청", "입력"),
]
FIELD_KEYS = {k for k, _, _ in REPORT_FIELDS}
OUTCOME_CAUSE = {"monitor": "이상 없음 · 감시", "unknown": "원인 미상", "daytime": "원인 미상", "direct": "원인 미상"}
ANSWER_LABEL = {  # 파트장 답(1.4 · 결정 018): 파트장 호출 3종, 숙련자 인계 2종
    "approved": "승인 후 진행",
    "daytime": "주간 처리 요청",
    "direct": "파트장 직접 확인",
    "assign": "주간 숙련자 배정",
}


def _parse(at: str | None) -> datetime | None:
    return datetime.fromisoformat(at) if at else None


def memo_summary(memo: str | None) -> str:
    memo = (memo or "").strip()
    return memo if len(memo) <= MEMO_SUMMARY_CHARS else memo[:MEMO_SUMMARY_CHARS] + "…"


def checklist_of(k: ManualKnowledge, c: Connection, section: str) -> list[str]:
    """그 절의 시작 전 체크리스트(조치 절은 상위 절 안의 그 조치 블록), 없으면 공통 시작 전 확인(AC-43-C2 · C4)."""
    block, _ = screen._block(k, section)
    match = re.search(r"\*\*시작 전 체크리스트\*\*\s*\n((?:\s*- \[ \] .+\n?)+)", block)
    own = [line.split("] ", 1)[1].strip() for line in match.group(1).splitlines() if "] " in line] if match else []
    return own or [i for (i,) in c.execute(select(m.CommonPrecheckItem.text).order_by(m.CommonPrecheckItem.seq)).all()]


# ---------------------------------------------------------------- 재가동 후 값(R11)


def restart_value(alarm: m.Alarm, table: dict, scenarios: dict, after_fix: bool) -> float:
    """R11: 각본 값, 없으면 경계 안쪽 값(경계 + 여유 10%)."""
    sc = scenarios.get(alarm.scenario_id or "", {})
    v = sc.get("restart_value_after_fix" if after_fix else "restart_value_if_none")
    if v is not None:
        return v
    b, low = alarm.alarm["boundary"], alarm.alarm["direction"] == "경계 아래"
    return round(b * 1.1, 1) if low else round(b * 0.9, 1)


def restart_block(alarm: m.Alarm, after_fix: bool) -> dict:
    al = alarm.alarm
    key = screen.SNAPSHOT_KEY[screen._rule_for(deps.alarm_table(), alarm.symptom_group)["key"]]
    v = restart_value(alarm, deps.alarm_table(), deps.scenarios(), after_fix)
    unit = al["unit"]
    side = "이상" if al["direction"] == "경계 아래" else "이하"
    return {
        "sensor": al["sensor"],
        "value": v,
        "value_text": f"{screen.fmt(key, v)} {unit}",
        "boundary_text": f"{screen.fmt(key, al['boundary'])} {unit}",
        "rule_text": f"경계 {screen.fmt(key, al['boundary'])} {unit} {side}이면 경계 이내",
        "basis": "무부하 3분 운전 뒤",
    }


# ---------------------------------------------------------------- 점검 경로(R-PATH)


def path(events: list[dict], k: ManualKnowledge, step: dict, alarm: m.Alarm) -> list[dict]:
    """시각 · 점 색(ok · bad · void · now) · 단계 이름 · 결과. 정정으로 무효인 기록은 지우지 않고 void로 보인다."""
    out = []
    unable: dict[str, int] = {}
    for e in events:
        at, void = e.get("_at"), bool(e.get("void"))
        t = e["type"]
        if t == "lock":
            out.append(
                {"at": e.get("at") or at, "title": k.sections["1.2"]["title"], "detail": "1.2절", "status": "ok"}
            )
        elif t == "precheck_done":
            sec = next(
                (
                    x["decision"]["section"]
                    for x in events
                    if x["type"] == "step_opened" and x["decision"].get("kind") == "precheck"
                ),
                None,
            )
            if sec:
                out.append({"at": at, "title": k.sections[sec]["title"], "detail": f"{sec}절", "status": "ok"})
        elif t == "result" and e.get("value"):
            sec, val = e["section"], e["value"]
            detail = val
            if val == "확인 불가":
                unable[sec] = unable.get(sec, 0) + 1
                if unable[sec] >= 2:
                    detail = "확인 불가 2회 · 제외"
            cf = e.get("corrected_from")
            if cf:
                when = screen.hhmm_kst(datetime.fromisoformat(cf["at"])) if cf.get("at") else ""
                detail += f" · 정정 {cf.get('count', 1)}회({when}, {cf.get('value')} → {val})"
            elif e.get("memo") and unable.get(sec, 0) < 2:
                detail += f" · {memo_summary(e['memo'])}"
            status = "void" if void else ("ok" if val == "정상" else "bad")
            out.append({"at": at, "title": k.sections[sec]["title"], "detail": detail, "status": status})
        elif t == "action_done":
            out.append(
                {
                    "at": at,
                    "title": k.sections[e["section"]]["title"],
                    "detail": f"{e['section']}절",
                    "status": "void" if void else "ok",
                }
            )
        elif t == "restart":
            out.append(
                {
                    "at": at,
                    "title": k.sections[session.RESTART_SECTION]["title"],
                    "detail": "6.1절 · 체크리스트 확인",
                    "status": "ok",
                }
            )
        elif t == "restart_result":
            rv = restart_block(alarm, True)
            label = "경계 이내" if e["outcome"] == "within" else "여전히 밖"
            out.append(
                {
                    "at": at,
                    "title": "재가동 후 값 확인",
                    "detail": f"{rv['value_text']} · {label}",
                    "status": "ok" if e["outcome"] == "within" else "bad",
                }
            )
        elif t == "monitor_close":
            out.append(
                {"at": at, "title": k.sections[session.MONITOR_SECTION]["title"], "detail": "6.2절", "status": "ok"}
            )
    now = _now_entry(step, k)
    if now:
        out.append(now)
    return out


def _now_entry(step: dict, k: ManualKnowledge) -> dict | None:
    kind = step.get("kind")
    if kind in {"action", "action_after_checklist"}:
        return {
            "at": None,
            "title": k.sections[step["section"]]["title"],
            "detail": f"{step['section']}절",
            "status": "now",
        }
    if kind == "restart_check":
        return {
            "at": None,
            "title": k.sections[session.RESTART_SECTION]["title"],
            "detail": "체크리스트 확인 중",
            "status": "now",
        }
    if kind == "restart_value":
        return {"at": None, "title": "재가동 후 값 확인", "detail": "", "status": "now"}
    return None


# ---------------------------------------------------------------- 호출 · 인계 요약(R-CALL · R-STOP, 1.4)


def checks_done(events: list[dict], k: ManualKnowledge) -> list[dict]:
    """지금까지 점검(결과가 있는 점검 · 정정으로 무효 제외).

    점검마다 한 줄 = 마지막 결과, 확인 불가 반복은 '확인 불가 n회'.
    """
    last: dict[str, str] = {}
    notes: dict[str, str | None] = {}
    unable: dict[str, int] = {}
    for e in events:
        if e["type"] == "result" and e.get("value") and not e.get("void"):
            last[e["section"]] = e["value"]
            cf = e.get("corrected_from") or {}
            changed = cf and cf.get("value") != e["value"]
            notes[e["section"]] = f"정정 {cf.get('count', 1)}회, 원래 {cf.get('value')}" if changed else None
            if e["value"] == "확인 불가":
                unable[e["section"]] = unable.get(e["section"], 0) + 1
    return [
        {
            "section": sec,
            "title": k.sections[sec]["title"],
            "value": f"확인 불가 {unable[sec]}회" if v == "확인 불가" and unable.get(sec, 0) >= 2 else v,
            "note": notes.get(sec),
        }
        for sec, v in last.items()
    ]


def _done_text(done: list[dict]) -> str:
    """'흡기 필터 육안 점검 · 냉각 팬 분해 점검 확인 불가 2회, 냉각 설정값 확인 정상'(같은 결과끼리 묶음)."""
    groups: dict[str, list[str]] = {}
    for d in done:
        groups.setdefault(d["value"], []).append(d["title"])
    return ", ".join(f"{' · '.join(titles)} {value}" for value, titles in groups.items())


def _candidates(state: session.SessionState, k: ManualKnowledge) -> list[dict]:
    probs = session.probabilities(state)
    names = screen.cause_names(k, state.group)
    return [{"code": c, "name": names.get(c, c), "pct": p} for c, p in sorted(probs.items(), key=lambda x: -x[1])]


def _write(facts: Facts, g: grounding.Grounding, template: str) -> grounding.Checked:
    return grounding.checked(lambda: adapter_for_mode().write(facts), g, template)


def call_summary(
    alarm: m.Alarm, state: session.SessionState, k: ManualKnowledge, step: dict, events: list[dict]
) -> dict:
    """1.4 호출 요약: 알람 · 지금까지 한 점검과 결과 · 남은 원인 후보 · 필요한 작업 · 설비 상태.

    자동 작성 · 고칠 수 있음(정비자가 고친 문장은 보낼 때 그대로 저장).
    """
    group = deps.group_names()[alarm.symptom_group]
    done = checks_done(events, k)
    cands = _candidates(state, k)
    head = f"{alarm.equipment_id} {group}({screen.hhmm_kst(alarm.occurred_at)})."
    if step.get("corrected"):  # T10 / summary_corrected: 조치 뒤 정정 → 다시 판정 대신 확인 요청(AC-47-C1)
        cor = correction_of(events, step) or {}
        acts = actions_of(events, k)
        act_text = " · ".join(f"{a['title']}({a['section']}) 완료 {screen.hhmm_kst(_parse(a['at']))}" for a in acts)
        when = screen.hhmm_kst(_parse(cor.get("at"))) if cor.get("at") else ""
        body = (
            f"{act_text}. {when} 정비자가 {cor.get('section')} {cor.get('title')} 결과를 {cor.get('before')} → "
            f"{cor.get('after')}으로 정정(사유: {cor.get('reason')}). "
            "조치 뒤 설비 상태가 바뀌어 다시 판정하지 않고 확인을 요청합니다."
        )
        template = f"{head} {body}"
        facts_vals = {"kind": "correction_call", "head": head, "body": body}
        sections = {cor.get("section")} | {a["section"] for a in acts} | {d["section"] for d in done}
        sections.discard(None)
    elif step["kind"] == "handover":
        reason = step.get("reason")
        path_text = _done_text(done) or "점검 전"
        if reason == "out_of_scope_finding":
            quote = next((r.get("memo") for r in reversed(state.results) if r.get("memo")), "")
            body = f"{path_text}. 소견: {memo_summary(quote)}. 매뉴얼 후보 원인과 맞지 않음."
        elif reason == "restart_outside":
            body = f"{path_text}. 재가동 뒤에도 값이 경계 밖."
        elif reason == "llm_failure":
            body = f"{path_text}. 안내 문장 생성 3회 연속 실패, 매뉴얼 원문으로만 진행 가능."
        else:
            body = f"{path_text}. 할 수 있는 A · B 점검 없음."
        template = f"{head} {body} 설비 정지 대기."
        facts_vals = {"kind": "handover", "head": head, "body": body}
        sections = {d["section"] for d in done}
    else:
        sec = step["section"]
        title = k.sections[sec]["title"]
        top = cands[0] if cands else None
        done_text = (
            (" · ".join(d["title"] for d in done) + " 점검 " + "/".join(sorted({d["value"] for d in done})))
            if done
            else "점검 전"
        )
        need = f"확인에 {title}({sec}절, {step.get('grade')}등급) 필요"
        cand_text = f"1순위 후보 {top['name']}({top['pct']}%), " if top else ""
        template = f"{head} {done_text}. {cand_text}{need}. 설비는 정지 상태로 대기 중."
        facts_vals = {"kind": "call", "head": head, "done": done_text, "candidate": cand_text, "need": need}
        sections = {sec} | {d["section"] for d in done}
    g = grounding.Grounding(
        allowed_sections=frozenset(
            sections | {n for n in grounding.numbers_in(template) if grounding.is_section_like(n)}
        ),
        source_numbers=grounding.numbers_in(template),
        top_record_ids=frozenset(),
    )
    r = _write(Facts("call_summary", step.get("section") or "", {**facts_vals, "template": template}), g, template)
    return {"text": r.text, "fallback": r.fallback, "label": r.label, "checks_done": done, "candidates": cands}


def correction_of(events: list[dict], step: dict) -> dict | None:
    """정정 호출(T10 / summary_corrected)을 연 정정: 절 · 점검 이름 · 전 → 후 · 사유 · 시각."""
    e = next(
        (e for e in reversed(events) if e["type"] == "correction" and e.get("mode") == "call_with_correction"), None
    )
    if e is None:
        return None
    k = deps.manual()
    sec = e.get("section")
    return {
        "seq": e["seq"],
        "section": sec,
        "title": k.sections[sec]["title"] if sec in k.sections else None,
        "before": (e.get("before") or {}).get("value"),
        "after": (e.get("after") or {}).get("value"),
        "reason": e.get("reason"),
        "at": e.get("_at"),
    }


def actions_of(events: list[dict], k: ManualKnowledge) -> list[dict]:
    """마친 조치(정정으로 무효 제외): 절 · 이름 · 완료 시각."""
    return [
        {"section": e["section"], "title": k.sections[e["section"]]["title"], "at": e.get("_at")}
        for e in events
        if e["type"] == "action_done" and not e.get("void")
    ]


def handover_head(step: dict, state: session.SessionState, k: ManualKnowledge) -> str:
    reason = step.get("reason")
    if reason == "out_of_scope_finding":
        return "후보 원인과 맞지 않는 소견"
    if reason == "restart_outside":
        return "재가동 뒤에도 값이 경계 밖"
    if reason == "llm_failure":
        return "안내 문장 생성이 반복해서 실패함"
    twice = [s for s, n in state.unable.items() if n >= 2]
    if twice:
        return f"{k.sections[twice[0]]['title']} · 확인 불가 2회, 남은 대안 없음"
    return "할 수 있는 점검을 모두 했으나 원인이 나오지 않음"


# ---------------------------------------------------------------- 보고서(R10 · R8)


def _restart_events(events: list[dict]) -> tuple[dict | None, dict | None]:
    restart = next((e for e in events if e["type"] == "restart" and not e.get("void")), None)
    result = next((e for e in events if e["type"] == "restart_result" and not e.get("void")), None)
    return restart, result


def downtime_minutes(alarm: m.Alarm, events: list[dict], confirmed_at: datetime | None) -> int:
    """결정 015 ③: 알람 시각 ~ 재가동 확인 시각.

    주간 처리(감시 운전)로 끝나면 ~ 그 답 시각, 둘 다 없으면 ~ 보고서 확정 시각.
    """
    _, result = _restart_events(events)
    daytime = next((e for e in events if e["type"] == "call_answer" and e.get("answer") == "daytime"), None)
    end = (
        _parse((result or {}).get("_at"))
        or _parse((daytime or {}).get("at") or (daytime or {}).get("_at"))
        or confirmed_at
        or datetime.now(UTC)
    )
    return max(0, round((end - alarm.occurred_at).total_seconds() / 60))


def unresolved(
    state: session.SessionState, k: ManualKnowledge, events: list[dict], grades: dict, notes: bool = True
) -> str:
    """결정 015 ④: 후보로 남은 원인(확정 원인 제외)의 C · D 점검 가운데 하지 못한 것.

    여기에 주간 처리 요청 + 호출 처리 결과를 더한다. notes = False면 파트장 답 메모를 뺀다(Pack 본문 — D-294).
    """
    items = []
    for cause in state.candidates:
        if cause == state.confirmed:
            continue
        for chk in k.checks.get(state.group, []):
            if chk.cause == cause and chk.section_id not in state.done and grades.get(chk.section_id) in {"C", "D"}:
                items.append(f"{chk.title}({chk.section_id}, {grades[chk.section_id]}등급) · 주간 확인 요청")
    for e in events:
        if e["type"] == "call_answer" and not e.get("void") and e.get("corrected"):  # 결정 019 ①: 정정 내용 · 답 · 메모
            cor = correction_of([x for x in events if x["seq"] < e["seq"]], {}) or {}
            note = f" · {e['note']}" if e.get("note") and notes else ""
            items.append(
                f"정정 확인 · {cor.get('section')} {cor.get('title')}({cor.get('before')} → {cor.get('after')}) · "
                f"{ANSWER_LABEL.get(e['answer'], e['answer'])}{note}"
            )
            continue
        if e["type"] == "call_answer" and not e.get("void"):  # 호출 처리 결과(결정 015 ④ · 018 ③ ④)
            sec = e.get("section")
            what = f"{k.sections[sec]['title']}({sec}) " if sec in k.sections else "숙련자 인계 답 · "
            note = f" · {e['note']}" if e.get("note") and notes else ""
            items.append(f"{what}{ANSWER_LABEL.get(e['answer'], e['answer'])}{note}")
        if e["type"] == "call_sent" and e.get("kind") == "handover" and not e.get("void"):
            items.append("숙련자 인계")
    return " / ".join(dict.fromkeys(items)) or "없음"


def report_draft(
    c: Connection,
    row: m.DiagSession,
    alarm: m.Alarm,
    state: session.SessionState,
    step: dict,
    events: list[dict],
    confirmed_at: datetime | None,
    grades: dict | None = None,
    for_pack: bool = False,
) -> dict[str, str]:
    """R10 8항목 초안(코드 사실). 원인 · 조치는 문장 생성 전 원문(실패면 이 글로 대체).

    grades = {}면 등급 글 없이(초안 열쇠용). for_pack = Pack report 본문용 — 미확인 칸에서 파트장 답 메모를 뺀다(D-294).
    """
    k = deps.manual()
    g = deps.grades(c)[0] if grades is None else grades
    group = deps.group_names()[alarm.symptom_group]
    system = deps.group_systems()[alarm.symptom_group]
    end = confirmed_at or datetime.now(UTC)
    al = alarm.alarm
    table = deps.alarm_table()
    rows = screen.sensor_rows(al, alarm.symptom_group, alarm.sensor_snapshot, table)
    first = rows[0]
    others = [r for r in rows[1:] if r["out_of_range"]] or rows[1:2]  # 결정 015 ①
    side = "아래" if al["direction"] == "경계 아래" else "위"
    key = first["key"]
    sensor = f"{first['name']} {first['value_text']} (경계 {screen.fmt(key, al['boundary'])} {al['unit']} {side})"
    sensor += "".join(f" · {r['value_text']}" for r in others[:1]) + f" → {system} 쪽"
    parts = ["잠금 확인(1.2)"]
    for p in path(events, k, {}, alarm):
        if p["title"] in {
            k.sections["1.2"]["title"],
            "재가동 후 값 확인",
            k.sections[session.RESTART_SECTION]["title"],
        }:
            continue
        if p["status"] == "void":  # 결정 019 ⑤: 정정으로 무효가 된 점검도 경로에 남긴다
            vsec = next((s for s in k.sections if k.sections[s]["title"] == p["title"]), "")
            if k.sections.get(vsec, {}).get("kind") != "action":
                parts.append(f"{p['title']}({vsec}, 정정으로 무효)")
            continue
        if p["title"] == k.sections[session.MONITOR_SECTION]["title"]:
            parts.append(f"{p['title']}(6.2)")
            continue
        sec = next((s for s in k.sections if k.sections[s]["title"] == p["title"]), "")
        if k.sections.get(sec, {}).get("kind") == "action":
            continue
        detail = p["detail"].replace(f"{sec}절", "").strip(" ·")
        parts.append(f"{p['title']}({sec}{', ' + detail.replace(' · ', ': ', 1) if detail else ''})")
    outcome = step.get("outcome") or ("confirmed" if state.confirmed else "unknown")
    cause = (
        k.cause(state.confirmed).name
        if state.confirmed and outcome == "confirmed"
        else OUTCOME_CAUSE.get(outcome, "원인 미상")
    )
    restart, result = _restart_events(events)
    rv = restart_block(alarm, bool(state.confirmed))
    restart_text = ""
    if restart and result:
        label = "경계 이내" if result["outcome"] == "within" else "경계 밖"
        restart_text = f"재가동(6.1, {g.get('6.1')}, 확인 완료) 후 {al['sensor']} {rv['value_text']} {label}"
    if state.confirmed and outcome == "confirmed":
        ac = k.cause(state.confirmed).action_section
        action = f"{k.sections[ac]['title']}({ac}, {g.get(ac)})" + (f" · {restart_text}" if restart_text else "")
    elif outcome == "monitor":
        action = "조치 없음" + (f" · {restart_text}" if restart_text else "") + " · 감시 대상 등록(6.2)"
    elif actions_of(events, k):  # 결정 019 ①: 정정 호출에 주간 처리 · 직접 확인 — 이미 한 조치는 그대로
        action = " · ".join(f"{a['title']}({a['section']}, {g.get(a['section'])})" for a in actions_of(events, k))
        action += f" · {restart_text}" if restart_text else ""
    else:
        action = "조치 없음" + (f" · {restart_text}" if restart_text else "")
    facts = {
        "equipment_alarm": (
            f"{alarm.equipment_id} · {group} · {screen.hhmm_kst(alarm.occurred_at)} ~ {screen.hhmm_kst(end)}"
        ),
        "sensor_evidence": sensor,
        "check_path": " → ".join(parts),
        "cause": cause,
        "evidence_records": " · ".join(s["record_id"] for s in row.similar[:3]),  # R3 상위 최대 3개
        "action": action,
        "downtime": f"{downtime_minutes(alarm, events, confirmed_at)}분",
        "unresolved": unresolved(state, k, events, g, notes=not for_pack),
    }
    return facts


REPORT_SENTENCES = ("cause", "action")  # R8 대상: 보고서 원인 · 조치 문장(약속 v3 report 출력 칸)
REPORT_RUN_WHERE = {"run.write_report", "run.rewrite_report"}  # D-288: Pack 문장 node 실패 = provider_failure


def draft_key(row: m.DiagSession, events: list[dict], draft: dict[str, str]) -> str:
    """초안 열쇠(CH-20): 원인 · 조치 원문 · 근거 절 — 바뀌면 새로 한 번 쓴다(반려 뒤 추가 점검 · 확정 전 정정).

    draft는 등급 글 없는 초안(report_draft grades={}) — 파트장 등급표 변경은 _open_step을 거치지 않으므로
    열쇠에 넣지 않는다
    (R13: 열린 단계는 이후 등급 변경에도 그대로 — 쓴 문장도 그때 등급 그대로).
    """
    sections = sorted(_report_grounding(row, events, draft).allowed_sections)
    raw = json.dumps([draft["cause"], draft["action"], sections], ensure_ascii=False)
    return "sha256:" + hashlib.sha256(raw.encode()).hexdigest()


def report_sentences(
    row: m.DiagSession, events: list[dict], draft: dict[str, str], key: str
) -> tuple[dict[str, dict], int]:
    """화면 · 확정이 읽는 원인 · 조치 문장과 그 기록 seq — 화면 조회는 쓰지 않는다(쓰기는 _open_step 한 곳)."""
    written = [e for e in events if e["type"] == "report_written"]
    if not written:  # Q-18: 이 판 전에 보고서 단계를 연 세션은 지금 동작(그릴 때 씀)
        gr = _report_grounding(row, events, draft)
        return {k: _sentence(k, draft, gr) for k in REPORT_SENTENCES}, 0
    hit = next((e for e in reversed(written) if e.get("draft_key") == key), None)
    if hit is not None:
        return hit["fields"], hit["seq"]
    fields = {
        k: {"text": draft[k], "fallback": True, "attempts": None, "reason": "draft_changed"} for k in REPORT_SENTENCES
    }
    return fields, written[-1]["seq"]


def report_written_payload(
    c: Connection, row: m.DiagSession, state: session.SessionState, step: dict, events: list[dict], seq: int
) -> dict | None:
    """보고서 단계를 열 때(CH-20): 초안 열쇠가 마지막 report_written과 같으면 None, 아니면 새로 쓴 문장."""
    alarm = sessions_alarm(c, row)
    draft = report_draft(c, row, alarm, state, step, events, None)
    key = draft_key(row, events, report_draft(c, row, alarm, state, step, events, None, grades={}))
    last = next((e for e in reversed(events) if e["type"] == "report_written"), None)
    if last is not None and last.get("draft_key") == key:
        return None
    gr = _report_grounding(row, events, draft)
    if not runs.deploy_on():
        return {"draft_key": key, "fields": {k: _sentence(k, draft, gr) for k in REPORT_SENTENCES}, "via": "inproc"}
    body = report_draft(c, row, alarm, state, step, events, None, for_pack=True)  # PR-16: 파트장 답 메모 0(D-294)
    sections = sorted(_report_grounding(row, events, body).allowed_sections)
    try:  # CH-19: Pack report Run(약속 v3)
        res = runs.report(alarm.alarm_id, row.symptom_group, row.similar, body, sections, seq)
    except PackUnavailable as e:  # CH-22: 재시도 뒤 끝내 실패 — 503 대신 두 칸 원문(확정 가능 · 다시 부르지 않음)
        reason = "provider_failure" if e.code == "run_failed" and e.where in REPORT_RUN_WHERE else "pack_unavailable"
        fields = {k: {"text": draft[k], "fallback": True, "attempts": None, "reason": reason} for k in REPORT_SENTENCES}
        return {"draft_key": key, "fields": fields, "via": "deploy", "run_id": e.run_id}
    try:
        out = res.output["report"]
        fields = {k: {x: out[k][x] for x in ("text", "fallback", "attempts", "reason")} for k in REPORT_SENTENCES}
    except (KeyError, TypeError):  # 201인데 report 모양이 아님 — CH-22 '표 밖'과 같이 원문(세션이 막히지 않게)
        fields = {
            k: {"text": draft[k], "fallback": True, "attempts": None, "reason": "pack_unavailable"}
            for k in REPORT_SENTENCES
        }
    return {
        "draft_key": key,
        "fields": fields,
        "via": "deploy",
        "run_id": res.run_id,
        "deployment_id": res.deployment_id,
    }


def _sentence(fkey: str, draft: dict[str, str], gr: grounding.Grounding) -> dict:
    """앱 adapter(기본 길): 생성 → R8 → 1회 다시 → 원문. reason은 앱이 아는 만큼(preview v12 H)."""
    failed = []

    def generate() -> Draft:
        try:
            return adapter_for_mode().write(Facts("report_sentence", "", {"field": fkey, "template": draft[fkey]}))
        except AdapterError:
            failed.append(True)
            raise

    r = grounding.checked(generate, gr, draft[fkey])
    reason = None if not r.fallback else "provider_failure" if failed else "ungrounded"
    return {"text": r.text, "fallback": r.fallback, "attempts": r.attempts, "reason": reason}


def _report_grounding(row: m.DiagSession, events: list[dict], facts: dict[str, str]) -> grounding.Grounding:
    """R8 원천: 절 번호 = 이번 세션 기록, 수치 = 세션 입력 · 센서 값 · 초안 사실, 근거 사례 = R3 상위 10건."""
    nums = grounding.numbers_in(*facts.values())
    secs = {s for s in nums if grounding.is_section_like(s)} | {e.get("section") for e in events if e.get("section")}
    secs |= {e["decision"]["section"] for e in events if e["type"] == "step_opened" and e["decision"].get("section")}
    return grounding.Grounding(
        allowed_sections=frozenset(x for x in secs if x),
        source_numbers=nums,
        top_record_ids=frozenset(s["record_id"] for s in row.similar),
    )


def report_view(
    c: Connection, row: m.DiagSession, alarm: m.Alarm, state: session.SessionState, step: dict, events: list[dict]
) -> dict:
    stored = c.execute(select(m.Report.__table__).where(m.Report.session_id == row.session_id)).first()
    k = deps.manual()
    reopened = stored is not None and stored.status == "rejected" and not state.report_confirmed
    if stored and not reopened:
        fields = stored.fields
        status, confirmed_at = stored.status, stored.confirmed_at
    else:
        facts = report_draft(c, row, alarm, state, step, events, None)
        key = draft_key(row, events, report_draft(c, row, alarm, state, step, events, None, grades={}))
        sent, sent_seq = report_sentences(row, events, facts, key)
        facts |= {k: sent[k]["text"] for k in REPORT_SENTENCES}
        fallback = {k: bool(sent[k]["fallback"]) for k in REPORT_SENTENCES}
        gr = _report_grounding(row, events, facts)
        edits = {}
        rejected_seq = (state.report_rejected_seq or 0) if reopened else 0
        before = next(  # 반려 전 마지막 문장 기록 — 없으면(이 판 전 세션) FLOW-06 그대로
            (e for e in reversed(events) if e["type"] == "report_written" and e["seq"] < rejected_seq), None
        )
        # CH-20: 반려 뒤 추가 점검 · 정정으로 초안 열쇠가 반려 전과 달라졌으면 새 초안 · 새 문장(A7 · A13)
        redrafted = reopened and before is not None and before.get("draft_key") != key
        since = max(rejected_seq, sent_seq)  # 정비자 수정은 그 문장 기록(또는 반려) 뒤 것만
        if reopened and not redrafted:  # FLOW-06: 반려된 보고서는 확정했던 문장에서 다시 고친다(그 뒤 수정만 새로 검사)
            base = {f["key"]: f["text"] for f in stored.fields}
            facts = {key: base.get(key, facts[key]) for key in facts}
            fallback = {f["key"]: bool(f.get("fallback")) for f in stored.fields if f["key"] in REPORT_SENTENCES}
            gr = _report_grounding(row, events, {**facts, **base})
        for e in events:
            if e["type"] == "report_edit" and not e.get("void") and e["seq"] > since:
                edits[e["field"]] = e["text"]
        fields = []
        for key, label, source in REPORT_FIELDS:
            text = edits.get(key, facts[key])
            ok = key not in edits or grounding.is_grounded(Draft(text), gr)
            missing = sorted(grounding.numbers_in(text) - gr.source_numbers) if key in edits else []
            fields.append(
                {
                    "key": key,
                    "label": label,
                    "source": source,
                    "text": text,
                    "edited": key in edits,
                    "ok": ok,
                    "unsupported_numbers": missing,
                }
                | ({"fallback": fallback.get(key, False) and key not in edits} if key in REPORT_SENTENCES else {})
            )
        status, confirmed_at = "draft", None
    failures = [f for f in fields if not f["ok"]]
    authority_ok = _authority_ok(events, k)
    required_ok = all(f["text"].strip() for f in fields)
    checks = [
        {
            "key": "grounded",
            "label": "근거 없는 문장 없음" if not failures else f"근거 없는 문장 {len(failures)}건",
            "ok": not failures,
        },
        {
            "key": "authority",
            "label": "권한 등급 위반 없음" if authority_ok else "권한 등급 위반 있음",
            "ok": authority_ok,
        },
        {
            "key": "required",
            "label": "필수 8항목 모두 채워짐" if required_ok else "필수 항목이 비어 있음",
            "ok": required_ok,
        },
    ]
    fix = "문장을 고치거나 지우십시오."

    def quote(f: dict) -> str:  # T09 / check_failed: 근거 없는 수치가 든 문장 조각을 인용
        parts = [p for p in f["text"].split(" · ") if any(n in p for n in f["unsupported_numbers"])]
        return (parts[0] if parts else f["text"])[:60]

    messages = [
        f'"{quote(f)}"의 수치 {", ".join(f["unsupported_numbers"])}가 이번 세션 기록에 없습니다. {fix}'
        if f["unsupported_numbers"]
        else f'"{quote(f)}"의 절 번호 · 근거 기록이 이번 세션 기록에 없습니다. {fix}'
        for f in failures
    ]
    rejection = stored.rejection if stored is not None and stored.rejection else None
    return {
        "status": status,
        "rejection": (
            {
                **{k2: rejection.get(k2) for k2 in ("reason", "by", "at")},
                "by_name": c.execute(
                    select(m.Account.display_name).where(m.Account.user_id == rejection.get("by"))
                ).scalar(),
            }
            if rejection
            else None
        ),
        "fields": fields,
        "checks": checks,
        "messages": messages,
        "can_confirm": status == "draft" and all(x["ok"] for x in checks),
        "confirmed_at": confirmed_at.isoformat() if confirmed_at else None,
        "low_evidence": rules.low_evidence(
            session.fold(k, row.symptom_group, [rules.Similar(**s) for s in row.similar], []).similar
        ),
    }


def _authority_ok(events: list[dict], k: ManualKnowledge) -> bool:
    """확정 전 확인 ②: 결과 · 조치는 그때 지시로 열린 절에만(R2). 서버가 이미 거부하므로 기록 대조."""
    opened = set()
    for e in events:
        if e["type"] == "step_opened" and e["decision"].get("kind") in {
            "instruct",
            "instruct_after_checklist",
            "action",
            "action_after_checklist",
        }:
            opened.add(e["decision"]["section"])
        if e["type"] in {"result", "action_done"} and not e.get("void") and e.get("section") not in opened:
            return False
    return True


# ---------------------------------------------------------------- 입력 검증 · 부수 효과


def accept(
    c: Connection,
    row: m.DiagSession,
    actor: str,
    step: dict,
    state: session.SessionState,
    events: list[dict],
    etype: str,
    payload: dict,
) -> tuple[str, dict]:
    """S-03 입력을 검사하고 (저장할 업무 기록 type, payload)를 돌려준다. 거부는 409."""
    k = deps.manual()
    kind = step.get("kind")

    def reject(reason: str):
        raise HTTPException(status_code=409, detail=reason)

    if state.report_confirmed:
        reject("session_closed")
    if etype == "handover_request":  # AC-31-C2 · S6: 문장 생성 3회 연속 실패로 인계를 권할 때만 정비자가 고른다
        from c1a15.api import sessions as svc

        if not grounding.should_recommend_handover(svc.llm_failures(events)) or kind in {
            "handover",
            "report",
            "closed",
        }:
            reject("no_handover_recommendation")
        return "handover_request", {"reason": "llm_failure"}
    if etype == "action_done":
        if kind not in {"action", "action_after_checklist"} or payload.get("section") != step.get("section"):
            reject("no_action_step")
        if kind == "action_after_checklist" and step["section"] not in state.b_checklist_done:
            reject("b_checklist_required")  # AC-32-C2 · AC-43-C4
        if step["section"] in state.actions_done:
            reject("already_done")
        return "action_done", {"section": step["section"]}
    if etype == "restart":
        if kind != "restart_check":
            reject("no_restart_step")
        if sorted(payload.get("checked") or []) != sorted(checklist_of(k, c, session.RESTART_SECTION)):
            reject("checklist_incomplete")  # AC-21-C1
        return "restart", {"checked": payload["checked"]}
    if etype == "restart_result":
        if kind != "restart_value" or payload.get("outcome") not in {"within", "outside"}:
            reject("no_restart_value_step")
        return "restart_result", {"outcome": payload["outcome"]}
    if etype == "monitor_close":
        if kind != "monitor_close":
            reject("no_monitor_step")
        return "monitor_close", {}
    if etype in {"call_send", "call_wait"}:
        if kind not in {"call", "handover"} or step.get("call_status") == "sent":
            reject("no_call_step")
        corrected = {"corrected": True} if step.get("corrected") else {}  # T10 / summary_corrected(AC-47-C1)
        if etype == "call_wait":
            if kind != "call":
                reject("no_call_step")
            return "call_wait", {"section": step.get("section"), **corrected}
        alarm = sessions_alarm(c, row)
        text = (payload.get("summary") or "").strip() or call_summary(alarm, state, k, step, events)["text"]
        call_kind = "handover" if kind == "handover" else "approval"
        cor = correction_of(events, step) if corrected else None
        call_id = c.execute(
            m.Call.__table__.insert()
            .values(
                session_id=row.session_id,
                kind=call_kind,
                section=step.get("section"),
                grade=None if corrected else step.get("grade"),
                summary=text,
                sent_by=actor,
                correction=cor,
                change_seq=deps.next_change_seq(c),
            )
            .returning(m.Call.call_id)
        ).scalar_one()
        return "call_sent", {
            "kind": call_kind,
            "section": step.get("section"),
            "grade": None if corrected else step.get("grade"),
            "call_id": call_id,
            "summary": text,
            **corrected,
        }
    if etype == "report_edit":
        if kind != "report":
            reject("no_report_step")
        if payload.get("field") not in FIELD_KEYS or payload.get("text") is None:
            reject("invalid_report_field")
        return "report_edit", {"field": payload["field"], "text": payload["text"]}
    if etype == "report_confirm":
        if kind != "report":
            reject("no_report_step")
        alarm = sessions_alarm(c, row)
        view = report_view(c, row, alarm, state, step, events)
        if not view["can_confirm"]:  # AC-07-C1: 실패 항목이 있으면 확정 거부
            raise HTTPException(status_code=409, detail={"reason": "precheck_failed", "checks": view["checks"]})
        now = datetime.now(UTC)
        fields = view["fields"]
        for f in fields:  # 확정 때 정지 시간 · 시각을 확정 시각으로 고정
            if f["key"] in {"equipment_alarm", "downtime"} and not f["edited"]:
                f["text"] = report_draft(c, row, alarm, state, step, events, now)[f["key"]]
        values = {
            "author": actor,
            "status": "awaiting_approval",
            "fields": fields,
            "low_evidence": view["low_evidence"],
            "confirmed_at": now,
            "updated_at": now,
            "change_seq": deps.next_change_seq(c),
        }
        if c.execute(select(m.Report.report_id).where(m.Report.session_id == row.session_id)).first():
            c.execute(  # 반려 뒤 다시 확정(AC-11-C2): 같은 보고서 행을 승인 대기로(반려 기록은 남김)
                m.Report.__table__.update().where(m.Report.session_id == row.session_id).values(**values)
            )
        else:
            c.execute(m.Report.__table__.insert().values(session_id=row.session_id, **values))
        c.execute(
            m.DiagSession.__table__.update().where(m.DiagSession.session_id == row.session_id).values(status="reported")
        )
        c.execute(
            m.Alarm.__table__.update()
            .where(m.Alarm.alarm_id == row.alarm_id)
            .values(status="done", change_seq=deps.next_change_seq(c))
        )
        return "report_confirm", {"confirmed_at": now.isoformat()}
    reject("unknown_event")
    raise AssertionError


def sessions_alarm(c: Connection, row: m.DiagSession) -> m.Alarm:
    return m.Alarm(**c.execute(select(m.Alarm.__table__).where(m.Alarm.alarm_id == row.alarm_id)).first()._mapping)


# ---------------------------------------------------------------- 세션 응답의 S-03 블록


def flow_view(c: Connection, row: m.DiagSession, state: session.SessionState, step: dict, events: list[dict]) -> dict:
    k = deps.manual()
    g, minutes = deps.grades(c)
    alarm = sessions_alarm(c, row)
    kind = step.get("kind")
    out: dict = {"path": path(events, k, step, alarm)}
    fixed = next(  # T08 / corrected_path: 정정으로 다시 판정한 점검(정정 기록은 P-14 · S-05가 만든다)
        (e for e in reversed(events) if e["type"] == "result" and e.get("corrected_from") and not e.get("void")), None
    )
    rejudged = fixed and (fixed.get("corrections") or [{}])[-1].get("mode", "rejudge") == "rejudge"
    if rejudged and fixed["corrected_from"].get("value") != fixed.get("value"):
        out["correction"] = {
            "section": fixed["section"],
            "title": k.sections[fixed["section"]]["title"],
            "at": fixed["corrected_from"].get("at"),
            "before": fixed["corrected_from"].get("value"),
            "after": fixed.get("value"),
        }
    if state.confirmed:
        cause = k.cause(state.confirmed)
        ac = cause.action_section
        done_e = next(
            (e for e in events if e["type"] == "action_done" and e.get("section") == ac and not e.get("void")), None
        )
        confirming = cause.confirm_check
        needs = g.get(ac) == "B"
        out["action"] = {
            "cause_code": cause.code,
            "cause_name": cause.name,
            "evidence_record_ids": screen.evidence_record_ids(k, confirming, row.similar),
            "section": ac,
            "title": k.sections[ac]["title"],
            "verb": k.sections[ac]["title"].split()[-1],  # 버튼 '{동사} 완료'(T08: 흡기 필터 교체 → 교체 완료)
            "grade": g.get(ac),
            "minutes": minutes.get(ac),
            "done_at": (done_e or {}).get("_at"),
            "checklist": checklist_of(k, c, ac) if needs else [],
            "checklist_done": ac in state.b_checklist_done,
        }
    if kind in {"restart_check", "restart_value", "monitor_close", "report"} or state.restarted:
        restart_e, result_e = _restart_events(events)
        out["restart"] = {
            "section": session.RESTART_SECTION,
            "title": k.sections[session.RESTART_SECTION]["title"],
            "grade": g.get(session.RESTART_SECTION),
            "checklist": checklist_of(k, c, session.RESTART_SECTION),
            "restarted_at": (restart_e or {}).get("_at"),
            "outcome": (result_e or {}).get("outcome"),
            **({"value": restart_block(alarm, bool(state.confirmed))} if restart_e else {}),
        }
    if kind == "monitor_close" or state.monitor_closed:
        out["monitor"] = {
            "section": session.MONITOR_SECTION,
            "title": k.sections[session.MONITOR_SECTION]["title"],
            "grade": g.get(session.MONITOR_SECTION),
            "closed": state.monitor_closed,
        }
    answer = state.call_answer or {}
    approved_open = answer.get("answer") == "approved" and step.get("section") == answer.get("section")
    # T10 ans_approved: 승인 배너와 그 C 점검 지시가 호출 카드에 함께 열린다
    if (
        kind in {"call", "handover", "call_direct"}
        or approved_open
        or (kind == "report" and (state.call_answer or state.handover_sent))
    ):
        last_call = next((e for e in reversed(events) if e["type"] == "call_sent" and not e.get("void")), None)
        # 정정 호출이면(지금 단계 또는 답이 온 뒤 보고서 단계) 정정 · 조치 값을 함께(T10 / summary_corrected · 019 ①)
        cor = correction_of(events, step) if step.get("corrected") or (last_call or {}).get("corrected") else None
        scope = [e for e in events if e["seq"] > cor["seq"]] if cor else events  # 정정 호출은 그 정정 뒤 기록만
        call_e = next((e for e in reversed(scope) if e["type"] == "call_sent" and not e.get("void")), None)
        wait_e = next((e for e in reversed(scope) if e["type"] == "call_wait" and not e.get("void")), None)
        ans_e = next((e for e in reversed(scope) if e["type"] == "call_answer" and not e.get("void")), None)
        if kind in {"call", "handover"} and not step.get("call_status"):
            # 아직 보내지도 기다리지도 않은 새 호출 단계 — 같은 세션 앞 호출의 보냄 · 대기 · 답을 붙이지 않음
            # (S-06 시연에서 발견: 승인 답 뒤 두 번째 호출)
            call_e = wait_e = ans_e = None
        elif call_e and ans_e and ans_e.get("call_id") != call_e.get("call_id"):
            ans_e = None  # 답은 그 호출 것만
        sec = step.get("section") or (call_e or {}).get("section")
        summary = {"text": call_e["summary"], "fallback": False, "label": None} if call_e else None
        if kind in {"call", "handover"} or summary is None:
            gen = call_summary(
                alarm,
                state,
                k,
                {
                    **step,
                    "kind": "handover" if (call_e or {}).get("kind") == "handover" or kind == "handover" else "call",
                    "section": sec,
                    "grade": step.get("grade") or (call_e or {}).get("grade"),
                },
                events,
            )
            summary = summary or {k2: gen[k2] for k2 in ("text", "fallback", "label")}
            checks, cands = gen["checks_done"], gen["candidates"]
        else:
            checks, cands = checks_done(events, k), _candidates(state, k)
        status = "answered" if ans_e else "sent" if call_e else "waiting" if wait_e else "none"
        out["call"] = {
            "kind": "handover" if kind == "handover" or (call_e or {}).get("kind") == "handover" else "approval",
            "reason": step.get("reason"),
            "head": handover_head(step, state, k) if kind == "handover" else None,
            "section": sec,
            "title": k.sections[sec]["title"] if sec in k.sections else None,
            "grade": (call_e or {}).get("grade")
            if approved_open
            else step.get("grade") or (call_e or {}).get("grade") or (g.get(sec) if sec else None),
            "minutes": minutes.get(sec) if sec else None,
            "checks_done": checks,
            "candidates": cands,
            "summary": summary,
            "status": status,
            "waiting_at": (wait_e or {}).get("_at"),
            "sent_at": (call_e or {}).get("_at"),
            "answer": (
                {k2: ans_e.get(k2) for k2 in ("answer", "by", "at", "note")}
                | {
                    "by_name": c.execute(
                        select(m.Account.display_name).where(m.Account.user_id == ans_e.get("by"))
                    ).scalar()
                }
                if ans_e
                else None
            ),
        }
        if cor:  # T10 / summary_corrected: 정정 · 조치 칩, 지금까지 점검 · 조치, 남은 후보는 다시 계산하지 않음
            out["call"].update(
                correction={k2: cor[k2] for k2 in ("section", "title", "before", "after", "reason", "at")},
                actions_done=actions_of(events, k),
                candidates=[],
                grade=None,
                minutes=None,
            )
    if kind in {"report", "closed"}:
        out["report"] = report_view(c, row, alarm, state, step, events)
    return out
