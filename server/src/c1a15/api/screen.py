"""정비자 화면 값(P-19, B-04): 화면이 보이는 값을 서버가 만든다(앱은 받은 값만 그린다).

값 정의는 사용자 결정 014(평소 범위 · 최대 m · 근거 기록 · 교대)와 데이터에 이미 있는 값(설비 종류 · 계통 · 승인자 ·
유사 % = R3 score × 100 · 잠금 절차 = R1 1.2절 · 원인 이름 = 매뉴얼 원인 표)만 쓴다.
"""

import re
from datetime import datetime, timedelta, timezone

from sqlalchemy import Connection, select

from c1a15.api import deps
from c1a15.db import models as m
from c1a15.engine import rules
from c1a15.engine.alarm_rules import SNAPSHOT_KEY
from c1a15.engine.knowledge import ManualKnowledge
from c1a15.llm import adapter_for_mode, grounding
from c1a15.llm.base import Facts

KST = timezone(timedelta(hours=9))
NIGHT_START, NIGHT_END = 22, 6  # 결정 014 ④: 야간 22:00 ~ 06:00 고정
LOCK_SECTION = "1.2"  # R1: 세션의 첫 단계는 1.2절 잠금 확인

# 센서 표(T03 / R-ALARM): 알람 센서 먼저, 이어서 이 순서에서 나머지를 채워 5행(Prototype T03 '알람 센서 + 4개')
SENSORS = {
    "power_w": ("기계 출력", "W"),
    "rotational_speed_rpm": ("회전 속도", "rpm"),
    "torque_nm": ("회전력", "Nm"),
    "tool_wear_min": ("공구 마모", "분"),
    "air_temperature_k": ("공기 온도", "K"),
    "temp_diff_k": ("온도 차", "K"),
}
TABLE_ORDER = ["rotational_speed_rpm", "torque_nm", "tool_wear_min", "air_temperature_k", "temp_diff_k"]
TABLE_ROWS = 5

OUTCOME_LABEL = {
    "이상 없음·감시": ("이상 없음 · 감시", "감시 마감"),
    "원인 미상·숙련자 인계": ("원인 미상", "숙련자 인계"),
}


def hhmm_kst(at: datetime) -> str:
    return at.astimezone(KST).strftime("%H:%M")


def fmt(key: str, v: float) -> str:
    if key in {"power_w", "rotational_speed_rpm"}:
        return f"{v:,.0f}"
    if key == "tool_wear_min":
        return f"{v:.0f}"
    return f"{v:.1f}"


# ---------------------------------------------------------------- 알람 블록(T03)


def _rule_for(table: dict, group: str) -> dict:
    return next(r for r in table["rules"] if r["group"] == group)


def _status(key: str, value: float, table: dict) -> str:
    """상태 = 알람 경계 기준(data/alarm_rules.json). 경계가 없는 센서는 '정상'."""
    for r in table["rules"]:
        if SNAPSHOT_KEY[r["key"]] != key:
            continue
        b = r["boundaries"]
        if "low" in b and value < b["low"]:
            return "경계 아래"
        if "high" in b and value > b["high"]:
            return "경계 위"
    return "정상"


def sensor_rows(alarm: dict, group: str, snapshot: dict, table: dict) -> list[dict]:
    alarm_key = SNAPSHOT_KEY[_rule_for(table, group)["key"]]
    keys = [alarm_key] + [k for k in TABLE_ORDER if k != alarm_key]
    ranges = table["normal_ranges"]
    rows = []
    for key in keys[:TABLE_ROWS]:
        name, unit = SENSORS[key]
        v = snapshot[key]
        if key == alarm_key:  # 알람 센서는 경계 쪽 한쪽 범위(결정 014 ①)
            side = "이상" if alarm["direction"] == "경계 아래" else "이하"
            range_text = f"{fmt(key, alarm['boundary'])} {unit} {side}"
        else:
            range_text = f"{fmt(key, ranges[key]['low'])} ~ {fmt(key, ranges[key]['high'])}"
        status = _status(key, v, table)
        rows.append(
            {
                "key": key,
                "name": name,
                "value": v,
                "unit": unit,
                "value_text": f"{fmt(key, v)} {unit}",
                "range_text": range_text,
                "status": status,
                "is_alarm_sensor": key == alarm_key,
                "out_of_range": status != "정상",
            }
        )
    return rows


def out_of_range_count(snapshot: dict, table: dict) -> int:
    """이탈 센서 수 = 알람 경계를 넘은 센서 수(표에 없는 센서 포함)."""
    keys = {SNAPSHOT_KEY[r["key"]] for r in table["rules"]}
    return sum(1 for key in keys if _status(key, snapshot[key], table) != "정상")


LEAD_PROMOTED = "경계 안 · 파트장이 올림"  # EV-009 이름표(설명 문장 0)


def ai_reading(alarm: dict, key: str, group_name: str, system: str) -> dict:
    """T03 'AI 해석': 코드 사실(알람 센서 · 값 · 경계 · 방향 · 계통)로 한두 문장.

    판정이 아니고 R8 근거 검사를 거친다(실패 → 코드 템플릿 + '원문으로 대체됨').
    """
    value_text = f"{fmt(key, alarm['value'])} {alarm['unit']}"
    if alarm.get("origin") == "lead":  # EV-009: 경계를 넘지 않은 후보를 파트장이 올림 — 경계 문장을 짓지 않고 이름표만
        return {"text": f"{alarm['sensor']} {value_text} · {LEAD_PROMOTED}", "fallback": False, "label": None}
    boundary_text = f"{fmt(key, alarm['boundary'])} {alarm['unit']}"
    facts = Facts(
        "ai_reading",
        "",
        {
            "group_name": group_name,
            "sensor": alarm["sensor"],
            "value_text": value_text,
            "boundary_text": boundary_text,
            "direction": alarm["direction"],
            "system": system,
        },
    )
    nums = grounding.numbers_in(value_text, boundary_text)
    g = grounding.Grounding(
        # 소수 한 자리 센서 값(7.8 K · 8.3 K)은 R8 검사의 절 번호 꼴과 같다. 그 값만 허용하고 다른 절 번호는 막는다.
        allowed_sections=frozenset(n for n in nums if grounding.is_section_like(n)),
        source_numbers=nums,
        top_record_ids=frozenset(),
    )
    template = f"{alarm['sensor']} {value_text} · 경계 {boundary_text} {alarm['direction']} · {system}"
    r = grounding.checked(lambda: adapter_for_mode().write(facts), g, template)
    return {"text": r.text, "fallback": r.fallback, "label": r.label}


def alarm_block(a: m.Alarm, similar_count: int) -> dict:
    table = deps.alarm_table()
    group_name = deps.group_names()[a.symptom_group]
    system = deps.group_systems()[a.symptom_group]
    al = a.alarm
    boundary_side = "하위 경계" if al["direction"] == "경계 아래" else "상위 경계"
    rule_key = SNAPSHOT_KEY[_rule_for(table, a.symptom_group)["key"]]
    return {
        "alarm_id": a.alarm_id,
        "equipment_id": a.equipment_id,
        "equipment_type": deps.equipment_types().get(a.equipment_id, deps.default_equipment_type()),
        "occurred_at": a.occurred_at.isoformat(),
        "symptom_group": a.symptom_group,
        "group_name": group_name,
        "system": system,
        "alarm": al,
        "boundary_text": f"{boundary_side} {fmt(rule_key, al['boundary'])} {al['unit']}",
        "out_of_range_count": out_of_range_count(a.sensor_snapshot, table),
        "trend": a.trend,
        "trend_title": al.get("trend_title"),
        "sensors": sensor_rows(al, a.symptom_group, a.sensor_snapshot, table),
        "ai_reading": ai_reading(al, rule_key, group_name, system),
        "similar_count": similar_count,
    }


# ---------------------------------------------------------------- 진단(T04)


def cause_names(k: ManualKnowledge, group: str) -> dict[str, str]:
    """순위 원인 이름 = 매뉴얼 원인 표(x.1 개요 '원인 후보') 이름 그대로(A-04)."""
    return {c.code: c.name for c in k.causes.get(group, [])}


def _record_card(rec: dict, score: float) -> dict:
    outcome = rec["outcome"]
    if outcome["type"] == "원인 확정":
        label = outcome["cause_name"]
        action = next((s["name"] for s in reversed(rec["steps"]) if s["kind"] == "action"), "")
    else:
        label, action = OUTCOME_LABEL.get(outcome["type"], (outcome["type"], ""))
    return {
        "record_id": rec["record_id"],
        "equipment_id": rec["equipment_id"],
        "month": int(rec["occurred_at"][5:7]),
        "similarity_pct": round(score * 100),  # R3: 유사도 % = score × 100(반올림)
        "outcome_type": outcome["type"],
        "cause_code": outcome.get("cause_code"),
        "outcome_label": label,
        "action_name": action,
        "downtime_min": rec["downtime_min"],
    }


def in_order(values: dict, order: list[str]) -> dict:
    """원인 칸을 매뉴얼 개요 순으로(저장 JSONB의 키 순서와 무관 — 같은 % 정렬 · 응답 바이트가 앱 셈과 같게)."""
    return {c: values[c] for c in sorted(values, key=lambda c: order.index(c) if c in order else len(order))}


def decided_numbers(step: dict | None, order: list[str]) -> tuple[dict, dict] | None:
    """화면 원인 % · 근거 n = Pack 판정 출력(EV-011 CH-02 · 05). 두 칸이 없으면 None(옛 Pack · 옛 세션 → 앱 셈)."""
    if not step or not isinstance(step.get("probabilities"), dict) or not isinstance(step.get("evidence"), dict):
        return None
    return in_order(step["probabilities"], order), in_order(step["evidence"], order)


def similar_cards(c: Connection, similar: list[dict]) -> list[dict]:
    """T04 기록 카드 = R3 상위 3건 가운데 근거가 되는 기록(R6 score ≥ 0.5).

    근거 적음이면 3건 미만(T04 / low_evidence).
    """
    top = [s for s in similar if s["score"] >= rules.LOW_EVIDENCE_SCORE][:3]
    ids = [s["record_id"] for s in top]
    recs = {
        r.record_id: r.record
        for r in c.execute(
            select(m.HistoryRecord.record_id, m.HistoryRecord.record).where(m.HistoryRecord.record_id.in_(ids))
        ).all()
    }
    return [_record_card(recs[s["record_id"]], s["score"]) for s in top if s["record_id"] in recs]


# ---------------------------------------------------------------- 잠금 · 지시(T05 · T06)

_STEP = re.compile(r"^\d+\. (.+)$", re.M)


def _block(k: ManualKnowledge, section: str) -> tuple[str, str]:
    """(지시 블록, 그 절의 원문 전체). 점검 절은 'x.y.1 점검 방법' 블록, 조치 절은 상위 절 안의 그 조치 블록."""
    sec = k.sections[section]
    if sec["kind"] == "action":
        text = k.sections[sec["parent"]]["text"]
        block = text[text.index(f"#### {section} ") :]
    else:
        text = sec["text"]
        heads = [mm.start() for mm in re.finditer(r"^#### ", text, re.M)]
        block = text[heads[0] :] if heads else text
    nxt = block.find("\n#### ", 1)
    return (block if nxt < 0 else block[:nxt]), text


def procedure_steps(k: ManualKnowledge, section: str) -> list[str]:
    """절의 절차 단계(번호 목록). 점검 절은 'x.y.1 점검 방법' 아래만, 조치 절은 상위 절 안의 그 조치 블록만."""
    return _STEP.findall(_block(k, section)[0])


def _plain(md: str) -> str:
    lines = [re.sub(r"^#{1,6}\s+|^>\s?", "", line).replace("**", "") for line in md.strip().splitlines()]
    return "\n".join(lines).strip()


def instruction_guide(k: ManualKnowledge, section: str, similar: list[dict]) -> dict:
    """R8 대상 '점검 · 조치 지시문': 절차를 문장 생성기가 쓰고(fixture = 절 원문 절차) 근거 검사를 거친다.

    실패 → 1회 다시 작성 → 또 실패면 절 원문 블록 + '원문으로 대체됨'(T06 / fallback).
    """
    block, text = _block(k, section)
    steps = procedure_steps(k, section)
    facts = Facts("instruction", section, {"procedure": "\n".join(steps)})
    nums = grounding.numbers_in(text)
    g = grounding.Grounding(
        allowed_sections=frozenset({section} | {n for n in nums if grounding.is_section_like(n)}),
        source_numbers=nums,
        top_record_ids=frozenset(s["record_id"] for s in similar),
    )
    original = _plain(block)
    r = grounding.checked(lambda: adapter_for_mode().write(facts), g, original)
    if r.fallback:
        return {"section": section, "steps": [], "fallback": True, "label": r.label, "original": original}
    lines = [re.sub(r"^\d+\.\s*", "", x).strip() for x in r.text.splitlines() if x.strip()]
    return {"section": section, "steps": lines, "fallback": False, "label": None, "original": None}


def criterion(k: ManualKnowledge, section: str) -> str | None:
    mm = re.search(r"\*\*판정 기준\*\* (.+)", k.sections[section].get("text") or "")
    return mm.group(1).strip() if mm else None


def lock_instruction(k: ManualKnowledge, grades: dict, minutes: dict) -> dict:
    """T05 잠금 전: 1.2절 제목 · 절차만(R1). 다른 절 원문은 잠금 전 계속 거부한다."""
    sec = k.sections[LOCK_SECTION]
    return {
        "section": LOCK_SECTION,
        "title": sec["title"],
        "grade": grades.get(LOCK_SECTION),
        "minutes": minutes.get(LOCK_SECTION),
        "steps": procedure_steps(k, LOCK_SECTION),
    }


def instructed_checks(events: list[dict], k: ManualKnowledge, group: str) -> list[str]:
    """이 세션에서 지시로 열린 점검 절(처음 열린 순서)."""
    checks = {c.section_id for c in k.checks.get(group, [])}
    seen: list[str] = []
    for e in events:
        if e["type"] != "step_opened" or e.get("void"):  # 정정으로 무효가 된 지시는 세지 않음(S-05)
            continue
        d = e["decision"]
        opened = d.get("kind") in {"instruct", "instruct_after_checklist"} and d["section"] in checks
        if opened and d["section"] not in seen:
            seen.append(d["section"])
    return seen


def check_progress(events: list[dict], k: ManualKnowledge, group: str, grades: dict, approvals) -> dict:
    """'점검 n / 최대 m'. n = 이 세션에서 지시된 점검 순번, m = 지금 등급으로 지시할 수 있는 점검(A · B 또는 승인된 C)
    과 이미 지시된 점검을 합한 수(결정 014 ②)."""
    seen = instructed_checks(events, k, group)
    now = {
        c.section_id
        for c in k.checks.get(group, [])
        if rules.effective_grade(c.section_id, grades, approvals) in rules.INSTRUCTABLE
    }
    return {"check_no": len(seen), "check_max": len(now | set(seen))}


def evidence_record_ids(k: ManualKnowledge, section: str, similar: list[dict]) -> list[str]:
    """점검 근거 = 상위 10건 중 그 점검의 연결 원인으로 확정된 기록, 유사도 순 최대 2건(결정 014 ③)."""
    if section not in {c.section_id for cs in k.checks.values() for c in cs}:
        return []
    cause = k.check(section).cause
    ranked = sorted((s for s in similar if s["cause"] == cause), key=lambda s: -s["score"])
    return [s["record_id"] for s in ranked[:2]]


# ---------------------------------------------------------------- 홈(T02)


def shift_window(now: datetime | None = None) -> tuple[datetime, datetime]:
    """지금 시각이 속한 야간 교대, 주간이면 가장 가까운 야간 교대(결정 014 ④)."""
    now = (now or datetime.now(KST)).astimezone(KST)
    day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    if now.hour >= NIGHT_START:
        start = day.replace(hour=NIGHT_START)
    elif now.hour < NIGHT_END:
        start = day.replace(hour=NIGHT_START) - timedelta(days=1)
    else:
        prev_end, next_start = day.replace(hour=NIGHT_END), day.replace(hour=NIGHT_START)
        start = next_start if (next_start - now) < (now - prev_end) else prev_end - timedelta(hours=8)
    return start, start + timedelta(hours=8)


def shift_summary(in_progress: int, now: datetime | None = None, done: int = 0, calls: int = 0) -> dict:
    start, end = shift_window(now)
    return {
        "label": "야간",
        "start": start.isoformat(),
        "end": end.isoformat(),
        "start_text": f"{NIGHT_START:02d}:00",
        "end_text": f"{NIGHT_END:02d}:00",
        "done": done,  # 이 교대에 확정한 내 보고서 수(S-03 P-09)
        "in_progress": in_progress,
        "calls": calls,  # 이 교대에 보낸 내 파트장 호출 수(S-03 P-09)
    }
