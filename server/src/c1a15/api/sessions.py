"""진단 세션 서비스: append-only 업무 기록(정본) → LangGraph 재개(다음 단계) · engine.session 접기(화면 상태).

화면 값은 서버 판정만(Authority boundary).
"""

import json
from datetime import UTC, datetime

from fastapi import HTTPException
from langgraph.types import Command
from sqlalchemy import Connection, func, select, text

from c1a15.api import deps, flow, screen
from c1a15.db import models as m
from c1a15.deploy import runs
from c1a15.engine import checkpoint, graph, rules, session
from c1a15.llm import adapter_for_mode, grounding
from c1a15.llm.base import AdapterError, Facts
from c1a15.retrieval import search

SERVER_FIELDS = {
    "seq",
    "type",
    "signal",
    "llm_fallback",
    "at",
    "void",
    "_at",
    "_client",
    "_client_type",
}  # 서버만 쓰는 event 필드(재전송 비교에서 뺌)
CLIENT_TYPES = {
    "lock",
    "equipment_change",
    "precheck_done",
    "b_checklist_done",
    "result",
    "confirm_answer",
    "out_of_scope_choice",
} | flow.CLIENT_TYPES
INPUT_TYPES = (
    CLIENT_TYPES - flow.CLIENT_TYPES
    | {  # 판정 엔진이 접는 업무 기록(S-03 · 파트장 답 포함)
        "lock",
        "equipment_change",
        "precheck_done",
        "approval",
        "correction",  # S-05(P-14): 조치 뒤 정정 → 정정 호출(AC-47-C1)
    }
    | flow.ENGINE_TYPES
)
GROUP_NAME = {"TW": "공구 마모 경고", "PW": "출력 이탈", "CL": "온도 차 저하", "LD": "토크 과부하"}


def audit(c: Connection, actor: str, action: str, target: str, detail: dict, equipment_id: str | None = None) -> None:
    c.execute(
        m.AuditEntry.__table__.insert().values(
            actor=actor, action=action, target=target, detail=detail, equipment_id=equipment_id
        )
    )


def audit_rejection(actor: str, action: str, target: str, detail: dict, equipment_id: str | None = None) -> None:
    """거부 감사는 요청 트랜잭션과 따로 커밋한다 — 거부 응답(HTTPException)으로 요청이 rollback돼도 남는다(S02-G6-1)."""
    with deps.engine().begin() as c2:
        audit(c2, actor, action, target, detail, equipment_id)


def raw_events_of(c: Connection, sid: int) -> list[dict]:
    """append-only 업무 기록 그대로(정정 · 메모 덧붙임도 각자 한 행)."""
    rows = c.execute(
        select(m.SessionEvent.seq, m.SessionEvent.type, m.SessionEvent.payload, m.SessionEvent.created_at)
        .where(m.SessionEvent.session_id == sid)
        .order_by(m.SessionEvent.seq)
    ).all()
    return [{"seq": r.seq, "type": r.type, **r.payload, "_at": r.created_at.isoformat()} for r in rows]


NO_REJUDGE = {"call_with_correction", "attach_to_call", "attach_answered"}  # 다시 판정하지 않는 정정(AC-47 · 019 ② ③)


def logical(raw: list[dict]) -> list[dict]:
    """정정 · 메모 덧붙임을 적용한 업무 기록(S-05 P-14, FLOW-14 '다시 읽기').

    - correction: 대상 기록 값을 최신 값으로 바꾸고 corrections(시각 · 전 · 후 · 사유)와
      corrected_from(처음 값 · 마지막 시각 · 횟수)을 남긴다. 원래 값은 업무 기록 행과 감사에 그대로 있다.
      mode rejudge면 대상 뒤 · 정정 앞의 기록을 '정정으로 무효'(void)로 둔다.
    - note_append: 대상 기록에 notes(시각 · 메모)를 붙인다(판정 · 보고서 값은 그대로 — 결정 019 ⑥).
    판정 엔진 · 화면 · 보고서 · 감사 · 이력 변환은 모두 이 결과를 읽는다.
    """
    out = [dict(e) for e in raw]
    by_seq = {e["seq"]: e for e in out}
    for e in out:
        target = by_seq.get(e.get("target_seq"))
        if target is None:
            continue
        if e["type"] == "correction":
            history = target.setdefault("corrections", [])
            history.append(
                {
                    "seq": e["seq"],
                    "at": e["_at"],
                    "by": e.get("by"),
                    "reason": e.get("reason"),
                    "before": e.get("before"),
                    "after": e.get("after"),
                    "mode": e.get("mode"),
                }
            )
            target.update(e.get("after") or {})
            target.pop("signal", None)  # 정정한 결과는 R7 확인 질문을 다시 띄우지 않는다
            first = history[0]["before"] or {}
            target["corrected_from"] = {**first, "at": e["_at"], "count": len(history)}
            if (
                target["type"] == "result" and e.get("mode") in NO_REJUDGE
            ):  # AC-47: 화면 · 보고서는 최신 값, 판정은 그대로
                target.setdefault("judged_value", (e.get("before") or {}).get("value"))
            if e.get("mode") == "rejudge":
                target.pop("judged_value", None)
                for later in out:
                    if e["target_seq"] < later["seq"] < e["seq"] and not later.get("void"):
                        later["void"], later["voided_by"] = True, e["seq"]
        elif e["type"] == "note_append":
            target.setdefault("notes", []).append({"seq": e["seq"], "at": e["_at"], "memo": e.get("memo")})
    return out


def events_of(c: Connection, sid: int) -> list[dict]:
    return logical(raw_events_of(c, sid))


def similar_of(row: m.DiagSession) -> list[rules.Similar]:
    return [rules.Similar(s["record_id"], s["cause"], s["score"]) for s in row.similar]


def _store(c: Connection, sid: int, seq: int, etype: str, payload: dict, actor: str) -> None:
    c.execute(
        m.SessionEvent.__table__.insert().values(
            session_id=sid, seq=seq, type=etype, payload=payload, actor=actor, change_seq=deps.next_change_seq(c)
        )
    )


def _graph_decision(c: Connection, row: m.DiagSession, inputs: list[dict]) -> tuple[dict, str]:
    """다음 단계 = LangGraph graph(thread = 세션)를 마지막 입력으로 재개해 받는다(EP-C1-HITL-001).

    graph node는 session.decide를 부르고, 등급은 판정 시점의 등급표를 읽는다(R13).
    checkpoint가 업무 기록과 어긋나면(새 세션 · checkpoint만 앞섬 · 없음) 업무 기록으로 thread를 다시 세운다.
    """
    k = deps.manual()
    # key에 정정 횟수 · 무효 여부를 넣는다 — 정정으로 값 · 무효가 바뀐 기록이 있으면
    # checkpoint와 어긋나 업무 기록으로 다시 세운다
    keyed = [
        {**e, "key": f"{row.session_id}:{e['seq']}:{len(e.get('corrections', []))}:{int(bool(e.get('void')))}"}
        for e in inputs
    ]
    with checkpoint.saver() as saver:
        app = graph.build(k, lambda: deps.grades(c)[0], lambda: deps.grades(c)[1], checkpointer=saver)
        cfg = checkpoint.thread(row.session_id)
        snap = app.get_state(cfg)
        have = [e.get("key") for e in snap.values.get("events", [])] if snap.values else None
        if keyed and snap.next == ("wait",) and have == [e["key"] for e in keyed[:-1]]:
            out, via = app.invoke(Command(resume=keyed[-1]), cfg), "resume"
        else:
            seed = {"group": row.symptom_group, "similar": row.similar, "events": keyed}
            out, via = app.invoke(seed, cfg), "rebuild"
    return out["__interrupt__"][0].value["decision"], via


def _deploy_decision(c: Connection, row: m.DiagSession, inputs: list[dict]) -> tuple[dict, dict]:
    """다음 단계 = 배포 서버 judge Run(EV-001 ES-07, C1A15_JUDGE=deploy). 판정 하나 = Run 하나 — checkpoint 안 씀."""
    g, minutes = deps.grades(c)
    res = runs.judge(row.alarm_id, row.symptom_group, row.similar, inputs, g, minutes)
    return res.output["decision"], {"via": "deploy", "run_id": res.run_id, "deployment_id": res.deployment_id}


def _open_step(
    c: Connection, sid: int, row: m.DiagSession, events: list[dict], actor: str, decided: tuple | None = None
) -> dict:
    """다음 단계를 지금 등급표로 판정해 step_opened로 남긴다(R13: 열린 단계는 이후 등급 변경에도 그대로).

    판정 길: 기본 inproc = LangGraph 재개, deploy = 배포 서버 judge Run. decided = 세션 시작 start Run이 낸 첫 단계.
    """
    inputs = [e for e in events if e["type"] in INPUT_TYPES]
    if decided is not None:
        decision, ref = decided
    elif runs.deploy_on():
        decision, ref = _deploy_decision(c, row, inputs)
    else:
        decision, via = _graph_decision(c, row, inputs)
        ref = {"via": via}
    seq = (events[-1]["seq"] if events else 0) + 1
    _store(c, sid, seq, "step_opened", {"decision": decision, **ref}, actor)
    if decision["kind"] in {
        "precheck",
        "instruct",
        "instruct_after_checklist",
        "call",
        "action",
        "action_after_checklist",
    } and not decision.get(
        "call_status"
    ):  # 결정 020 ④: 보냄 · 대기 뒤 다시 열린 같은 호출 단계는 '호출 필요'를 다시 남기지 않음
        audit(
            c,
            actor,
            "instruct" if decision["kind"].startswith(("instruct", "action", "precheck")) else "call_required",
            f"session:{sid}",
            {"section": decision.get("section"), "grade": decision.get("grade"), "kind": decision["kind"]},
        )
    if (
        decision["kind"] in INSTRUCTION_KINDS
    ):  # R8 '지시문': 열 때 한 번 쓰고 근거 검사 결과를 남긴다(주기 조회마다 다시 쓰지 않음)
        guide = screen.instruction_guide(deps.manual(), decision["section"], row.similar)
        payload = {k2: guide[k2] for k2 in ("section", "steps", "label", "original")} | {
            "llm_fallback": guide["fallback"]
        }
        _store(c, sid, seq + 1, "instruction_shown", payload, actor)
    return decision


INSTRUCTION_KINDS = {"precheck", "instruct", "instruct_after_checklist", "action", "action_after_checklist"}


def instructed_sections(events: list[dict]) -> set[str]:
    """이 세션에서 지시로 열린 절(지금 · 이전). 호출(C · D) 단계의 절은 들지 않는다."""
    return {
        e["decision"]["section"]
        for e in events
        if e["type"] == "step_opened" and e["decision"].get("kind") in INSTRUCTION_KINDS
    }


def current_step(events: list[dict]) -> dict | None:
    opened = [e for e in events if e["type"] == "step_opened"]
    return opened[-1]["decision"] if opened else None


def create(c: Connection, alarm: m.Alarm, user_id: str) -> int:
    # 같은 알람의 동시 시작은 알람 줄 잠금으로 줄 세움 — 뒤 요청은 앞 요청 commit 뒤 기존 세션을 받음(GAP-18)
    c.execute(select(m.Alarm.alarm_id).where(m.Alarm.alarm_id == alarm.alarm_id).with_for_update())
    existing = c.execute(select(m.DiagSession.session_id).where(m.DiagSession.alarm_id == alarm.alarm_id)).scalar()
    if existing:
        return existing
    idx = deps.fresh_index(c)
    pool = [d for d in idx.docs if d.symptom_group == alarm.symptom_group]
    qtext = search.query_text(GROUP_NAME.get(alarm.symptom_group, ""), alarm.alarm.get("direction", ""), [])
    if qtext in idx.queries:  # 이력 release에 미리 계산한 질의 벡터(EV-001 Q-2)
        qv = [float(x) for x in idx.queries[qtext].strip("[]").split(",")]
    else:
        from c1a15.loader.embedding import fake_embedding  # fixture 모드 질의 임베딩(live 임베딩은 승인 뒤 LLM Adapter)

        qv = fake_embedding(qtext)
    vector = search.cosine_rank(qv, pool)
    top = search.similar_records(
        {"symptom_group": alarm.symptom_group},
        qtext,
        alarm.sensor_snapshot,
        idx.docs,
        idx.bm25,
        vector,
        deps.stats(),
        idx.cfg,
    )
    similar = [{"record_id": s.record_id, "cause": s.cause, "score": s.score} for s in top]
    deploy_cols, decided = {}, None
    if (
        runs.deploy_on()
    ):  # 첫 Run = start(P1 다리: 앱 임시 리트리버 상위 10건을 담음, D-259 (3)) — 실패면 세션을 만들지 않음
        g, minutes = deps.grades(c)
        res = runs.start(alarm, similar, g, minutes)
        similar = res.output["similar"]
        retrieval = {**res.output["retrieval"], "app_release_id": idx.release_id}
        deploy_cols = {"retrieval": retrieval, "start_run_id": res.run_id, "deployment_id": res.deployment_id}
        decided = (res.output["decision"], {"via": "deploy", "run_id": res.run_id, "deployment_id": res.deployment_id})
    sid = c.execute(
        m.DiagSession.__table__.insert()
        .values(
            alarm_id=alarm.alarm_id, user_id=user_id, symptom_group=alarm.symptom_group, similar=similar, **deploy_cols
        )
        .returning(m.DiagSession.session_id)
    ).scalar_one()
    c.execute(
        m.Alarm.__table__.update()
        .where(m.Alarm.alarm_id == alarm.alarm_id)
        .values(status="in_progress", change_seq=deps.next_change_seq(c))
    )
    row = _row(c, sid)
    _open_step(c, sid, row, [], user_id, decided)
    pv = preview(row, c)  # 처음 보이는 진단 미리보기 문장의 대체 여부를 세션 실패 수에 남긴다(S02-G6-4)
    state = session.fold(deps.manual(), row.symptom_group, similar_of(row), [])
    snap = {  # T15 / diagnosis '그때의 원인 순위 · 첫 지시'(S-05 P-14)
        "kind": pv["kind"],
        "preview": pv,
        "probabilities": session.probabilities(state),
        "evidence": rules.evidence_counts(state.candidates, state.similar),
    }
    if "reason_fallback" in pv:
        snap["llm_fallback"] = pv["reason_fallback"]
    _store(c, sid, events_of(c, sid)[-1]["seq"] + 1, "preview_shown", snap, user_id)
    audit(c, user_id, "session_start", f"session:{sid}", {"alarm_id": alarm.alarm_id}, alarm.equipment_id)
    return sid


def _row(c: Connection, sid: int) -> m.DiagSession:
    r = c.execute(select(m.DiagSession.__table__).where(m.DiagSession.session_id == sid)).first()
    if r is None:
        raise HTTPException(status_code=404, detail="no_session")
    return m.DiagSession(**r._mapping)


def checklist_for(c: Connection, section: str) -> list[str]:
    """B 시작 전 체크리스트: 그 절의 목록, 절에 없으면 공통 시작 전 확인 목록(AC-43-C2)."""
    k = deps.manual()
    own = []
    for cs in k.checks.values():
        for chk in cs:
            if chk.section_id == section:
                own = list(chk.checklist)
    return own or [i for (i,) in c.execute(select(m.CommonPrecheckItem.text).order_by(m.CommonPrecheckItem.seq)).all()]


def checklist_is_common(section: str) -> bool:
    """그 절에 시작 전 체크리스트가 없어 공통 시작 전 확인을 쓰는가(T06 / b_precheck '공통 시작 전 확인' 칩)."""
    return not any(chk.checklist for cs in deps.manual().checks.values() for chk in cs if chk.section_id == section)


def session_for(c: Connection, sid: int, user_id: str) -> m.DiagSession:
    row = _row(c, sid)
    if row.user_id != user_id:
        raise HTTPException(status_code=403, detail="not_your_session")
    return row


def preview(row: m.DiagSession, c: Connection) -> dict:
    """진단 화면(T04)의 '다음 점검' 미리보기: 잠금 · 사전 확인을 했다고 놓고 판정한 다음 단계.

    절차 · 판정 기준은 넣지 않는다(R1).
    """
    k = deps.manual()
    g, minutes = deps.grades(c)
    state = session.fold(k, row.symptom_group, similar_of(row), [{"type": "lock"}, {"type": "precheck_done"}])
    d = session.decide(state, k, g, minutes)
    out = {"kind": d["kind"], "section": d.get("section"), "grade": d.get("grade"), "cause": d.get("cause")}
    if d["kind"] in {"instruct", "instruct_after_checklist"}:
        sec = k.sections[d["section"]]
        facts = Facts(
            "reason",
            d["section"],
            {
                "cause_name": k.cause(d["cause"]).name,
                "probability": d["reason_facts"]["probability"],
                "minutes": d["reason_facts"]["minutes"],
                "grade": d["grade"],
                "alternatives": d["reason_facts"]["alternatives"],
            },
        )
        out.update(title=sec["title"], minutes=minutes[d["section"]], **_checked_reason(row, d, facts))
    elif d["kind"] == "call":  # P-18: 첫 판정이 호출(T04 / first_call)이어도 카드 값은 서버가 낸다
        sec = k.sections[d["section"]]
        p = d["probabilities"].get(d["cause"], 0)
        facts = Facts(
            "call_reason",
            d["section"],
            {
                "cause_name": k.cause(d["cause"]).name,
                "probability": p,
                "check_title": sec["title"],
                "grade": d["grade"],
                "reason": d["reason"],
            },
        )
        g = grounding.Grounding(
            allowed_sections=frozenset([d["section"]]),
            source_numbers=frozenset([str(p), "1"]),  # '1순위'의 1은 순위 사실
            top_record_ids=frozenset(s["record_id"] for s in row.similar),
        )
        template = (
            f"{k.cause(d['cause']).name} {p}% · {d['section']}절 {sec['title']} · {d['grade']}등급 · 파트장 호출 필요"
        )
        r = grounding.checked(lambda: adapter_for_mode().write(facts), g, template)
        out.update(
            title=sec["title"],
            minutes=minutes[d["section"]],
            call_reason=d["reason"],
            reason=r.text,
            reason_fallback=r.fallback,
            reason_label=r.label,
        )
    return out


def _checked_reason(row: m.DiagSession, d: dict, facts: Facts) -> dict:
    """R5-6 '고른 이유'는 R8 근거 검사를 거친다.

    실패 · provider 오류 → 코드 템플릿 + '원문으로 대체됨'(AC-06 · AC-31-C1).
    """
    v = facts.values
    alts = v["alternatives"]
    g = grounding.Grounding(
        allowed_sections=frozenset([d["section"], *(a["section"] for a in alts)]),
        source_numbers=frozenset(str(x) for x in (v["probability"], v["minutes"])),
        top_record_ids=frozenset(s["record_id"] for s in row.similar),
    )
    template = f"{v['cause_name']} {v['probability']}% · {d['section']}절 · 약 {v['minutes']}분 · {v['grade']}등급"
    r = grounding.checked(lambda: adapter_for_mode().write(facts), g, template)
    return {"reason": r.text, "reason_fallback": r.fallback, "reason_label": r.label}


def _memo_signal(k, section: str, memo: str, value: str | None) -> tuple[dict | None, bool]:
    """R7 메모 해석. provider 오류는 신호 없음으로 진행을 막지 않고 실패로 센다(AC-31-C1 · C2)."""
    try:
        sig = adapter_for_mode().memo_signal(section, k.sections[section].get("text", ""), memo, value)
    except AdapterError:
        return None, True
    return (sig.as_event_signal() if sig else None), False


def llm_failures(events: list[dict]) -> list[bool]:
    """같은 세션의 문장 생성 · 메모 해석 실패 순서(AC-31-C2).

    대상: 진단 미리보기 문장(처음 보인 때) · 지시문(열 때) · 메모가 있는 결과.
    """
    return [
        bool(e.get("llm_fallback"))
        for e in events
        if e["type"] in {"result", "preview_shown", "instruction_shown"} and "llm_fallback" in e and not e.get("void")
    ]


def alarm_of(c: Connection, alarm_id: int) -> m.Alarm:
    return m.Alarm(**c.execute(select(m.Alarm.__table__).where(m.Alarm.alarm_id == alarm_id)).first()._mapping)


def _guide_of(events: list[dict], k, section: str) -> dict:
    """지금 열린 지시의 지시문(instruction_shown). 기록이 없으면(이전 세션) 절 원문 절차."""
    last_open = max((e["seq"] for e in events if e["type"] == "step_opened"), default=0)
    shown = next(
        (
            e
            for e in reversed(events)
            if e["type"] == "instruction_shown" and e["seq"] > last_open and e["section"] == section
        ),
        None,
    )
    if shown is None:
        return {
            "steps": screen.procedure_steps(k, section),
            "fallback": False,
            "fallback_label": None,
            "original": None,
        }
    return {
        "steps": shown["steps"],
        "fallback": shown["llm_fallback"],
        "fallback_label": shown.get("label"),
        "original": shown.get("original"),
    }


def view(c: Connection, row: m.DiagSession) -> dict:
    events = events_of(c, row.session_id)
    k = deps.manual()
    g, minutes = deps.grades(c)
    state = session.fold(k, row.symptom_group, similar_of(row), [e for e in events if e["type"] in INPUT_TYPES])
    step = current_step(events) or {}
    probs = session.probabilities(state)
    out = {
        "session_id": row.session_id,
        "alarm_id": row.alarm_id,
        "status": row.status,
        "locked": state.locked,
        "lock_at": next((e["at"] for e in reversed(events) if e["type"] == "lock"), None) if state.locked else None,
        "probabilities": probs,
        "evidence": rules.evidence_counts(state.candidates, state.similar),
        "low_evidence": rules.low_evidence(state.similar),
        "top_records": [s["record_id"] for s in row.similar[:3]],
        "similar_basis": "상위 10건",
        "cause_names": screen.cause_names(k, row.symptom_group),  # P-19 ⑨(A-04): T04 순위 원인 이름
        "similar_cards": screen.similar_cards(c, row.similar),  # P-19 ④: T04 기록 카드
        "alarm": screen.alarm_block(alarm_of(c, row.alarm_id), len(row.similar)),  # P-19 ③: T03
        "results": [
            {k2: e.get(k2) for k2 in ("seq", "section", "value", "memo")} for e in events if e["type"] == "result"
        ],
        "step": {
            key: step.get(key)
            for key in (
                "kind",
                "section",
                "grade",
                "cause",
                "reason",
                "unable_before",
                "interpretation",
                "quote",
                "outcome",
                "call_status",
                "corrected",
            )
            if key != "corrected" or step.get("corrected")
        },
        "last_seq": events[-1]["seq"] if events else 0,
        "recommend_handover": grounding.should_recommend_handover(
            llm_failures(events)
        ),  # AC-31-C2(미리보기 문장 · 지시문 · 메모 해석 실패)
    }
    if not state.locked:  # P-19 ⑤: 잠금 전에는 1.2절 절차만(R1)
        out["lock_instruction"] = screen.lock_instruction(k, g, minutes)
    if (
        state.locked
        and step.get("section")
        and step.get("kind") in {"instruct", "instruct_after_checklist", "precheck", "action", "action_after_checklist"}
    ):
        sec = k.sections[step["section"]]
        needs = step["kind"] in {"instruct_after_checklist", "action_after_checklist"}
        out["instruction"] = {  # 지시 내용은 잠금 뒤에만(R1)
            "section": step["section"],
            "title": sec["title"],
            "text": sec["text"],
            "checklist": (
                flow.checklist_of(k, c, step["section"])
                if k.sections[step["section"]]["kind"] == "action"
                else checklist_for(c, step["section"])
            )
            if needs
            else [],
            "checklist_done": step["section"] in state.b_checklist_done,
            "checklist_common": needs and checklist_is_common(step["section"]),
            # P-19 ⑥ · T06 R-INSTR: 등급 · 분 · 절차 단계 · 판정 기준 · 점검 n / 최대 m · 근거 기록 · 확인 불가 점검
            "grade": step.get("grade") or g.get(step["section"]),  # 사전 확인처럼 판정 값에 등급이 없으면 현재 등급표
            "minutes": minutes.get(step["section"]),
            **_guide_of(events, k, step["section"]),
            "criterion": screen.criterion(k, step["section"]),
            **screen.check_progress(events, k, row.symptom_group, g, state.approvals),
            "evidence_record_ids": screen.evidence_record_ids(k, step["section"], row.similar),
            "unable": [
                {"section": s, "title": k.sections[s]["title"], "count": n} for s, n in sorted(state.unable.items())
            ],
        }
    out.update(flow.flow_view(c, row, state, step, events))  # S-03(P-09): 경로 · 조치 · 재가동 · 호출 · 보고서
    return out


def progress(c: Connection, row: m.DiagSession) -> dict:
    """홈 · 종 목록의 '점검 n / 최대 m'(P-19 ① · ②, 결정 014 ②)."""
    k = deps.manual()
    events = events_of(c, row.session_id)
    state = session.fold(k, row.symptom_group, similar_of(row), [e for e in events if e["type"] in INPUT_TYPES])
    return screen.check_progress(events, k, row.symptom_group, deps.grades(c)[0], state.approvals)


def post_event(c: Connection, row: m.DiagSession, actor: str, body: dict) -> dict:
    """입력 하나를 업무 기록에 덧붙인다. seq = 클라이언트가 본 마지막 seq + 1(같은 seq · 같은 내용 재전송은 한 번만)."""
    etype = body.get("type")
    if etype not in CLIENT_TYPES:
        raise HTTPException(status_code=422, detail="unknown_event")

    def deny(reason: str, **detail):  # 업무 규칙 거부는 감사 행을 남긴다(S02-G6-1, G6-S03 비차단 의견)
        audit_rejection(actor, "reject", f"session:{row.session_id}", {"reason": reason, "type": etype, **detail})
        raise HTTPException(status_code=409, detail=reason)

    if row.status == "reported":  # AC-33: 확정한 보고서 · 세션은 정비자가 고칠 수 없다
        deny("session_closed")
    events = events_of(c, row.session_id)
    last = events[-1]["seq"] if events else 0
    payload = {k2: v for k2, v in body.items() if k2 not in {"type", "seq"}}
    seq = body.get("seq")
    if isinstance(seq, int) and seq <= last:
        stored = next((e for e in events if e["seq"] == seq), None)
        client_stored = {k2: v for k2, v in stored.items() if k2 not in SERVER_FIELDS} if stored else None
        same_flow = stored and stored.get("_client_type") == etype and stored.get("_client") == payload
        if same_flow or (
            stored and stored["type"] == etype and client_stored == payload
        ):  # 저장된 클라이언트 필드 전체가 같을 때만(S02-G6-3)
            return view(c, row)  # 같은 업무 key 재전송
        raise HTTPException(status_code=409, detail="stale_seq")
    if seq is not None and seq != last + 1:
        raise HTTPException(status_code=409, detail="stale_seq")
    k = deps.manual()
    state = session.fold(k, row.symptom_group, similar_of(row), [e for e in events if e["type"] in INPUT_TYPES])
    step = current_step(events) or {}
    if etype == "result":
        if payload.get("memo") and step.get("section"):
            sig, failed = _memo_signal(k, step["section"], payload["memo"], payload.get("value"))
            payload["llm_fallback"] = failed  # 서버만 쓰는 필드(요청 스키마는 받지 않음)
            if sig:
                payload["signal"] = sig
        try:
            session.validate_result(state, step, {"type": "result", **payload})
        except session.EventRejected as exc:
            audit_rejection(
                actor, "reject", f"session:{row.session_id}", {"reason": str(exc), "section": payload.get("section")}
            )
            raise HTTPException(status_code=409, detail=str(exc)) from exc
    elif etype == "b_checklist_done":
        if step.get("kind") not in {"instruct_after_checklist", "action_after_checklist"} or payload.get(
            "section"
        ) != step.get("section"):
            deny("no_b_checklist_step")
        expected = (
            flow.checklist_of(k, c, step["section"])
            if k.sections[step["section"]]["kind"] == "action"
            else checklist_for(c, step["section"])
        )
        if sorted(payload.get("checked", [])) != sorted(expected):
            deny("checklist_incomplete")
    elif etype in {"precheck_done"} and not state.locked:
        deny("not_locked")
    elif etype in {"confirm_answer", "out_of_scope_choice"} and not state.pending:
        deny("nothing_pending")
    elif etype in flow.CLIENT_TYPES:  # S-03: 조치 · 재가동 · 마감 · 호출 · 보고서(P-09)
        try:
            stype, spayload = flow.accept(c, row, actor, step, state, events, etype, payload)
        except HTTPException as exc:
            audit_rejection(actor, "reject", f"session:{row.session_id}", {"reason": str(exc.detail), "type": etype})
            raise
        _store(c, row.session_id, last + 1, stype, {**spayload, "_client_type": etype, "_client": payload}, actor)
        audit(c, actor, etype, f"session:{row.session_id}", {"seq": last + 1, **spayload})
        _open_step(c, row.session_id, row, events_of(c, row.session_id), actor)
        return view(c, _row(c, row.session_id))
    if etype == "lock":
        from datetime import UTC, datetime

        payload["at"] = datetime.now(UTC).isoformat()
    _store(c, row.session_id, last + 1, etype, payload, actor)
    audit(
        c,
        actor,
        {"result": "input", "confirm_answer": "confirm_answer"}.get(etype, etype),
        f"session:{row.session_id}",
        {"seq": last + 1, **payload},
    )
    _open_step(c, row.session_id, row, events_of(c, row.session_id), actor)
    return view(c, row)


def open_alarm_counts(c: Connection) -> dict[str, int]:
    """R9 입력: 로그인한 정비자(유효 세션)별 처리 중 알람 수."""
    from datetime import UTC, datetime

    users = [
        u
        for (u,) in c.execute(
            select(m.LoginSession.user_id)
            .join(m.Account, m.Account.user_id == m.LoginSession.user_id)
            .where(
                m.LoginSession.app == "tech",
                m.Account.role == "tech",
                m.LoginSession.revoked_at.is_(None),
                m.LoginSession.expires_at > datetime.now(UTC),
            )
            .distinct()
        ).all()
    ]
    counts = dict(
        c.execute(
            select(m.Alarm.assigned_to, func.count())
            .where(m.Alarm.status.in_(["new", "in_progress"]), m.Alarm.assigned_to.is_not(None))
            .group_by(m.Alarm.assigned_to)
        ).all()
    )
    return {u: counts.get(u, 0) for u in users}


# ---------------------------------------------------------------- S-05(P-14): 정정 · 메모 덧붙이기(FLOW-14)


def _closed_deny(row: m.DiagSession, actor: str, etype: str) -> None:
    """확정한 세션(승인 대기 · 승인)은 정정 · 메모 덧붙이기 모두 거부(AC-48-C2 · 생성자 해석 ③).

    반려로 다시 열리면 다시 된다(AC-48-C3).
    """
    if row.status == "reported":
        audit_rejection(actor, "reject", f"session:{row.session_id}", {"reason": "session_closed", "type": etype})
        raise HTTPException(status_code=409, detail="session_closed")


def _step_label(k, d: dict) -> dict:
    sec = d.get("section")
    return {"kind": d.get("kind"), "section": sec, "title": k.sections[sec]["title"] if sec in k.sections else None}


def post_correction(c: Connection, row: m.DiagSession, actor: str, body: dict) -> dict:
    """'이 기록 정정'(AC-45 ~ AC-48): 정비자가 입력해 제출한 결과 · 메모 · 사전 확인 측정값만, 사유 필수, 덧붙임 기록.

    결과를 바꾸면 반영 방식(session.correction_mode)에 따라 다시 판정 · 정정 호출 · 보낸 호출에 붙임.
    다시 판정으로 지금 열린 지시가 바뀌면 confirmed 없이 409 confirm_required
    (AC-46-C3 · C4: 취소하면 아무것도 바뀌지 않음).
    """
    etype = "correction"

    def deny(reason: str, **detail):
        audit_rejection(actor, "reject", f"session:{row.session_id}", {"reason": reason, "type": etype, **detail})
        raise HTTPException(status_code=409, detail=reason)

    _closed_deny(row, actor, etype)
    reason = (body.get("reason") or "").strip()
    if not reason:
        deny("reason_required")  # AC-45-C2
    events = events_of(c, row.session_id)
    idx = next((i for i, e in enumerate(events) if e["seq"] == body.get("target_seq")), None)
    if idx is None:
        deny("no_record")
    target = events[idx]
    if target["type"] == "result":
        before = {"value": target.get("value"), "memo": target.get("memo")}
        after = {"value": body.get("value", before["value"]), "memo": body.get("memo", before["memo"])}
        if after["value"] not in session.RESULT_VALUES:
            deny("invalid_value")
    elif target["type"] == "precheck_done":
        before = {"values": target.get("values")}
        after = {"values": body.get("values", before["values"])}
    else:
        deny("not_correctable", target_type=target["type"])  # AC-48-C1
    after = {k2: (v.strip() if isinstance(v, str) else v) for k2, v in after.items()}
    if after == before:
        deny("no_change")
    changed = target["type"] == "result" and after["value"] != before["value"]
    try:
        plan = session.correction_mode(events, idx, value_changed=changed)
    except session.EventRejected as exc:
        deny(str(exc))
    k = deps.manual()
    seq = events[-1]["seq"] + 1
    at = datetime.now(UTC).isoformat()
    payload = {
        "target_seq": target["seq"],
        "target_type": target["type"],
        "section": target.get("section"),
        "before": before,
        "after": after,
        "reason": reason,
        "by": actor,
        "mode": plan["mode"],
    }
    if plan.get("call_id"):
        payload["call_id"] = plan["call_id"]
    if plan["mode"] == "rejudge":
        cur = current_step(events) or {}
        trial = logical([*raw_events_of(c, row.session_id), {"seq": seq, "type": etype, "_at": at, **payload}])
        g, minutes = deps.grades(c)
        state = session.fold(k, row.symptom_group, similar_of(row), [e for e in trial if e["type"] in INPUT_TYPES])
        nxt = session.decide(state, k, g, minutes)
        changes_open = cur.get("kind") in INSTRUCTION_KINDS and (nxt.get("kind"), nxt.get("section")) != (
            cur.get("kind"),
            cur.get("section"),
        )
        if changes_open and not body.get(
            "confirmed"
        ):  # AC-46-C3: 확인해야 저장(거부가 아니라 확인 요청 — 감사하지 않음)
            raise HTTPException(
                status_code=409,
                detail={
                    "reason": "confirm_required",
                    "current": _step_label(k, cur),
                    "next": _step_label(k, nxt),
                    "target": {"section": target.get("section"), "before": before, "after": after},
                },
            )
    _store(c, row.session_id, seq, etype, payload, actor)
    audit(c, actor, "correction", f"session:{row.session_id}", {"seq": seq, **payload})
    if plan["mode"] in {"attach_to_call", "attach_answered"} and plan.get("call_id"):  # AC-47-C2 · 019 ② ③
        sec = target.get("section") or next(
            (
                x["decision"]["section"]
                for x in events
                if x["type"] == "step_opened" and x["decision"].get("kind") == "precheck"
            ),
            None,
        )
        item = {
            "at": at,
            "section": sec,
            "title": k.sections[sec]["title"] if sec in k.sections else None,
            "target_type": target["type"],
            "before": before,
            "after": after,
            "reason": reason,
            "answered": plan["mode"] == "attach_answered",
        }
        c.execute(
            text(
                "update ops.calls set corrections = corrections || cast(:item as jsonb), change_seq = :q "
                "where call_id = :c"
            ),
            {"item": json.dumps([item], ensure_ascii=False), "q": deps.next_change_seq(c), "c": plan["call_id"]},
        )
    if plan["mode"] in {
        "rejudge",
        "call_with_correction",
    }:  # 메모만 · 보낸 호출에 붙임은 다음 단계 그대로(R13 — 다시 열지 않음)
        _open_step(c, row.session_id, row, events_of(c, row.session_id), actor)
    return view(c, _row(c, row.session_id))


def post_note(c: Connection, row: m.DiagSession, actor: str, body: dict) -> dict:
    """'메모 덧붙이기'(AC-48-C1): 정정하지 않는 기록에 시각과 함께 메모를 덧붙인다.

    원래 기록 · 판정 · 보고서는 그대로(019 ⑥).
    """
    etype = "note_append"

    def deny(reason: str, **detail):
        audit_rejection(actor, "reject", f"session:{row.session_id}", {"reason": reason, "type": etype, **detail})
        raise HTTPException(status_code=409, detail=reason)

    _closed_deny(row, actor, etype)
    memo = (body.get("memo") or "").strip()
    if not memo:
        deny("memo_required")
    events = events_of(c, row.session_id)
    target = next((e for e in events if e["seq"] == body.get("target_seq")), None)
    if target is None:
        deny("no_record")
    if target["type"] not in session.NOTE_TYPES or target.get("void"):
        deny("not_note_target", target_type=target["type"])
    seq = events[-1]["seq"] + 1
    sec = target.get("section") or {
        "lock": "1.2",
        "restart": "6.1",
        "restart_result": "6.1",
        "monitor_close": "6.2",
    }.get(target["type"])
    payload = {"target_seq": target["seq"], "target_type": target["type"], "section": sec, "memo": memo}
    _store(c, row.session_id, seq, etype, payload, actor)
    audit(c, actor, "note_append", f"session:{row.session_id}", {"seq": seq, **payload})
    return view(c, _row(c, row.session_id))
