"""앱 → Pack Run 입력 만들기(EV-001 ES-07 · 08 · 10): 정본 = c1a15-pack 약속 v2(+ README 읽는 법) · v3(kind report).

- session_id = `S-A<alarm_id>`(알람 하나 = 세션 하나 — 실패로 되돌린 뒤 다시 보내도 같은 값, R6-1)
- start.event_id = 세션을 연 알람의 event_id, 기본 길로 등록돼 없으면 `C1A-A<alarm_id>`(R6-2)
- 업무 기록은 판정이 쓰는 칸만(사용자 ID · 표시 이름 · 메모 원문 · 정정 사유 0, VC-35)
부르기는 deploy.client 한 곳(키 · 재시도 · 감사).
"""

import secrets
from functools import lru_cache

from c1a15 import config
from c1a15.deploy.client import Client, RunResult
from c1a15.deploy.ledger import DbLedger

SENSORS5 = ("air_temperature_k", "process_temperature_k", "rotational_speed_rpm", "torque_nm", "tool_wear_min")
EVENT_KEYS = ("seq", "type", "void", "section", "value", "judged_value", "yes", "outcome", "corrected")
EVENT_KEYS += ("kind", "answer", "mode", "choice")
SIGNAL_KEYS = ("out_of_scope_finding", "conflicts_with_button", "interpretation", "quote")
HANDOVER_REASONS = {"llm_failure", "out_of_scope_finding"}  # 정본 event.reason enum — 자유 문장 사유는 넣지 않음


@lru_cache
def settings() -> dict:
    return config.pack_settings()


@lru_cache
def client() -> Client:
    return Client(settings()["deploy_url"], DbLedger(), host_name=settings()["deploy_host"])


def session_ident(alarm_id: int) -> str:
    return f"S-A{alarm_id}"


def start_event_id(alarm) -> str:
    return alarm.event_id or f"C1A-A{alarm.alarm_id}"


def sensors5(snapshot: dict) -> dict:
    return {k: snapshot[k] for k in SENSORS5}


def similar_body(similar: list[dict]) -> list[dict]:
    return [{"record_id": s["record_id"], "cause": s.get("cause"), "score": s["score"]} for s in similar]


def judge_events(inputs: list[dict]) -> list[dict]:
    """정정 · 무효가 반영된 논리 기록(INPUT_TYPES만)에서 판정이 쓰는 칸만."""
    out = []
    for e in inputs:
        ev = {k: e[k] for k in EVENT_KEYS if k in e}
        if isinstance(e.get("signal"), dict):
            ev["signal"] = {k: e["signal"][k] for k in SIGNAL_KEYS if k in e["signal"]}
        if e["type"] == "handover_request" and e.get("reason") in HANDOVER_REASONS:
            ev["reason"] = e["reason"]
        out.append(ev)
    return out


@lru_cache
def source_release() -> str:
    """시연 · 평가 행의 출처 = AI4I 원본 sha256(data/manifest.json)."""
    import json
    import os
    from pathlib import Path

    manifest = json.loads((Path(os.environ["DATA_DIR"]) / "manifest.json").read_text(encoding="utf-8"))
    return f"ai4i-2020@sha256:{manifest['source']['sha256']}"


def new_event_id() -> str:
    """알람 Run의 사건 id — 알람 행이 생기기 전에 만든다(ML 길은 Run 결과를 보고 알람을 만들므로)."""
    return "C1A-E" + secrets.token_hex(6)


def alarm_body(
    event_id: str,
    equipment_id: str,
    snapshot: dict,
    source_mode: str,
    lineage: dict,
    product_type: str | None,
    threshold: float | None,
) -> dict:
    card = {
        "event_id": event_id,
        "source_mode": source_mode,
        "equipment_id": equipment_id,
        "sensor_snapshot": sensors5(snapshot),  # 계산 칸(출력 · 온도 차)은 Pack 한 곳에서 — 7칸이 와도 5칸만
        "alarm": {"source": "none"},
        "data_lineage": lineage,
    }
    if product_type:
        card["product_type"] = product_type
    body = {"kind": "alarm", "event_card": card}
    if source_mode == "ml_predicted":
        body["settings"] = {"ml_alarm_threshold": threshold}
    return body


def alarm(event_id: str, body: dict) -> RunResult:
    return client().run("alarm", event_id, 0, body)


def start_body(alarm, grades: dict, minutes: dict) -> dict:
    """약속 v4: 상위 10건은 Pack 리트리버(retrieve_history)가 고름 — similar 칸은 보내지 않음(EV-001 CH-29)."""
    return {
        "kind": "start",
        "session_id": session_ident(alarm.alarm_id),
        "event_id": start_event_id(alarm),
        "group": alarm.symptom_group,
        "query": {
            "direction": None
            if alarm.alarm.get("origin") == "lead"
            else alarm.alarm.get("direction"),  # EV-009: 넘지 않은 경계
            "sensor_snapshot": sensors5(alarm.sensor_snapshot),
        },  # 없으면 null(정본 enum)
        "events": [],
        "grades": grades,
        "minutes": minutes,
    }


def judge_body(alarm_id: int, group: str, similar: list[dict], inputs: list[dict], grades: dict, minutes: dict) -> dict:
    return {
        "kind": "judge",
        "session_id": session_ident(alarm_id),
        "group": group,
        "similar": similar_body(similar),
        "events": judge_events(inputs),
        "grades": grades,
        "minutes": minutes,
    }


def start(alarm, grades: dict, minutes: dict) -> RunResult:
    return client().run("start", session_ident(alarm.alarm_id), 0, start_body(alarm, grades, minutes))


def judge(alarm_id: int, group: str, similar: list[dict], inputs: list[dict], grades: dict, minutes: dict) -> RunResult:
    body = judge_body(alarm_id, group, similar, inputs, grades, minutes)
    seq = inputs[-1]["seq"] if inputs else 0  # 그 판정을 부른 마지막 입력 기록
    return client().run("judge", session_ident(alarm_id), seq, body)


def report_body(alarm_id: int, group: str, similar: list[dict], draft: dict, sections: list[str]) -> dict:
    """약속 v3 kind report: 앱 코드 초안 8항목(원인 · 조치 = 원문 대체 글) · 세션에서 열린 · 기록된 절."""
    return {
        "kind": "report",
        "session_id": session_ident(alarm_id),
        "group": group,
        "similar": similar_body(similar),
        "report_draft": dict(draft),
        "allowed_sections": sorted(sections),
    }


def report(alarm_id: int, group: str, similar: list[dict], draft: dict, sections: list[str], seq: int) -> RunResult:
    """seq = 보고서 단계를 연 기록 — 초안이 바뀌면 본문 hash가 달라 기본 키도 달라짐(CH-20 초안 열쇠)."""
    return client().run("report", session_ident(alarm_id), seq, report_body(alarm_id, group, similar, draft, sections))
