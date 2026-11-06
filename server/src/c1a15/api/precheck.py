"""D-619 사전 점검 후보(고장 판단 아님 · 자동 조치 없음): 정비자 홈을 열 때 앱 서버가 이력 표에서 셈.

- 셈 범위 = 예시 줄(record.demo D-619) + 패턴 표에 적은 시연 줄 · 나머지 이력은 안 셈(D-620 · 화면에 표시 안 함).
- 한 건 = 앞 조치 하나: 이어짐(같은 설비 · 며칠 안 뒤 이상) · 이상 없음(며칠 지남) ·
  진행 중(며칠 안 지남 · 분모 밖 · 후보 자리).
- 승인 예외는 승인 때 배포 revision과 지금이 달라진 뒤에만 이어짐(KG 반영 뒤).
- 표시 = 이어짐 3건 이상 · 분모의 절반 이상.
- 후보 = 그 설비 담당자의 진행 중 건 · 앞 조치 뒤 알람이 있던 설비 · 열린 알람 설비 뺌.
- [살펴봄] · [이번엔 제외]는 누가 · 언제 · 이유만 audit_log에 남김(건수 안 바뀜)."""

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from fastapi import HTTPException
from sqlalchemy import Connection, text

from c1a15.api import sessions
from c1a15.deploy import runs

MARK = "D-619"
MIN_HITS = 3
ACTIONS = {"look": "precheck_look", "skip": "precheck_skip"}


@dataclass(frozen=True)
class Pattern:
    id: str
    group: str
    section: str
    days: int
    follow: str
    look_at: str
    follow_check: str | None = None  # 뒤 사건 = 이 점검 절 '이상'(예시 줄은 원인 칸이 비어 있음 · 관문 확률 영향 0)
    follow_word: str | None = None
    extra: tuple[str, ...] = ()


PATTERNS = (
    Pattern("A", "CL", "4.3.2", 7, "필터 덮개 고정 문제", "필터 덮개 고정", follow_word="덮개", extra=("H-0301",)),
    Pattern("B", "TW", "2.4.2", 14, "마모 카운터 미초기화", "마모 카운터 · 교체 기록", follow_check="2.3"),
    Pattern("C", "PW", "3.4.2", 7, "회전 조건 설정 오류", "회전 조건 설정", follow_check="3.3"),
)


def shows(hits: int, clean: int) -> bool:
    return hits >= MIN_HITS and hits * 2 >= hits + clean


def _did(rec: dict) -> list[str]:
    return [s.get("section") for s in rec.get("steps") or [] if s.get("kind") == "action"]


def _exception_words(rec: dict) -> str:
    ex = rec.get("exception_record") or {}
    return f"{(ex.get('exception') or {}).get('topic') or ''} {ex.get('text') or ''}"


def _is_follow(p: Pattern, row: dict, reflected: frozenset | set) -> bool:
    rec = row["record"]
    if row["source"] == "approved_report":
        return bool(p.follow_word) and row["record_id"] in reflected and p.follow_word in _exception_words(rec)
    if rec.get("demo") != MARK:
        return False
    if p.follow_check:
        return any(
            s.get("kind") == "check" and s.get("section") == p.follow_check and s.get("result") == "이상"
            for s in rec.get("steps") or []
        )
    return p.follow_word in _exception_words(rec)


def classify(p: Pattern, rows: list[dict], now: datetime, reflected: frozenset | set = frozenset()) -> dict:
    """패턴 하나의 앞 조치 건을 이어짐 · 이상 없음 · 진행 중으로 나눔(시각 앞선 줄만)."""
    seen = [r for r in rows if r["occurred_at"] < now]
    out: dict = {"hits": [], "clean": [], "open": []}
    for b in sorted(seen, key=lambda r: r["occurred_at"]):
        rec = b["record"]
        marked = rec.get("demo") == MARK or b["record_id"] in p.extra
        if not (marked and b["symptom_group"] == p.group and p.section in _did(rec)):
            continue
        end = b["occurred_at"] + timedelta(days=p.days)
        after = [
            r
            for r in seen
            if r["equipment_id"] == b["equipment_id"]
            and b["occurred_at"] < r["occurred_at"] <= end
            and _is_follow(p, r, reflected)
        ]
        case = {"record_id": b["record_id"], "equipment_id": b["equipment_id"], "at": b["occurred_at"]}
        if after:
            f = min(after, key=lambda r: r["occurred_at"])
            days = (f["occurred_at"] - b["occurred_at"]).days
            out["hits"].append({**case, "follow_id": f["record_id"], "follow_days": days})
        elif end <= now:
            out["clean"].append({**case, "follow_id": None, "follow_days": None})
        else:
            out["open"].append({**case, "row": b})
    return out


def _rows(c: Connection) -> list[dict]:
    extra = sorted({r for p in PATTERNS for r in p.extra})
    found = c.execute(
        text(
            "select record_id, equipment_id, symptom_group, occurred_at, source, record from knowledge.history_records "
            "where record->>'demo' = :mark or record_id = any(:extra) "
            "or (source = 'approved_report' and record->'exception_record' is not null)"
        ),
        {"mark": MARK, "extra": extra},
    ).all()
    return [dict(r._mapping) for r in found]


def _reflected(c: Connection, rows: list[dict]) -> set[str]:
    """승인 예외 중 지금 배포 revision이 승인 때와 다른 것(둘 중 하나라도 모르면 안 셈)."""
    ids = [r["record_id"] for r in rows if r["source"] == "approved_report"]
    if not ids:
        return set()
    found = c.execute(
        text(
            "select detail->>'history_record_id' as rid, detail->>'deploy_revision' as rev from ops.audit_log "
            "where action in ('report_approve', 'report_edit_approve') and detail->>'history_record_id' = any(:ids)"
        ),
        {"ids": ids},
    ).all()
    now = runs.revision_now()
    return {r.rid for r in found if now and r.rev and r.rev != now}


def _marks(c: Connection) -> dict[str, dict]:
    found = c.execute(
        text(
            "select target, action, actor, at, detail from ops.audit_log "
            "where action in ('precheck_look', 'precheck_skip') order by audit_id"
        )
    ).all()
    choice = {v: k for k, v in ACTIONS.items()}
    return {
        r.target: {
            "choice": choice[r.action],
            "by": r.actor,
            "at": r.at.isoformat(),
            "reason": r.detail.get("reason"),
        }
        for r in found
    }


def _target(pattern: str, record_id: str) -> str:
    return f"precheck:{pattern}:{record_id}"


def _basis(case: dict, result: str) -> dict:
    return {
        "record_id": case["record_id"],
        "equipment_id": case["equipment_id"],
        "at": case["at"].isoformat(),
        "result": result,
        "follow_days": case["follow_days"],
    }


def cards(c: Connection, user_id: str, now: datetime | None = None) -> list[dict]:
    """그 정비자 담당 설비의 후보 카드 — 값은 모두 코드가 이력에서 셈."""
    now = now or datetime.now(UTC)
    rows = _rows(c)
    if not rows:
        return []
    reflected = _reflected(c, rows)
    mine = set(
        c.execute(
            text("select equipment_id from ops.equipment_assignments where user_id = :u"), {"u": user_id}
        ).scalars()
    )
    alarms = c.execute(text("select equipment_id, occurred_at, status from ops.alarms")).all()
    marks = _marks(c)
    out = []
    for p in PATTERNS:
        got = classify(p, rows, now, reflected)
        hits, clean = len(got["hits"]), len(got["clean"])
        if not shows(hits, clean):
            continue
        basis = [_basis(x, "이어짐") for x in got["hits"]] + [_basis(x, "이상 없음") for x in got["clean"]]
        for o in got["open"]:
            eq = o["equipment_id"]
            had_alarm = any(
                a.equipment_id == eq and (a.occurred_at >= o["at"] or a.status in ("new", "in_progress"))
                for a in alarms
            )
            if eq not in mine or had_alarm:
                continue
            step = next(s for s in o["row"]["record"]["steps"] if s.get("section") == p.section)
            out.append(
                {
                    "pattern": p.id,
                    "record_id": o["record_id"],
                    "equipment_id": eq,
                    "section": p.section,
                    "section_title": step.get("name") or p.section,
                    "days_ago": (now - o["at"]).days,
                    "within_days": p.days,
                    "follow": p.follow,
                    "look_at": p.look_at,
                    "total": hits + clean,
                    "hits": hits,
                    "clean": clean,
                    "basis": sorted(basis, key=lambda b: b["at"]),
                    "mark": marks.get(_target(p.id, o["record_id"])),
                }
            )
    return out


def mark(c: Connection, user_id: str, pattern: str, record_id: str, choice: str, reason: str | None) -> dict:
    """[살펴봄] · [이번엔 제외] 한 줄 — 지금 내 홈에 뜬 후보만 · 건수는 안 바뀜."""
    card = next((x for x in cards(c, user_id) if x["pattern"] == pattern and x["record_id"] == record_id), None)
    if card is None:
        raise HTTPException(status_code=404, detail="no_precheck")
    note = (reason or "").strip()
    if choice == "skip" and not note:
        raise HTTPException(status_code=422, detail="reason_required")
    if card["mark"] is None:
        sessions.audit(
            c,
            user_id,
            ACTIONS[choice],
            _target(pattern, record_id),
            {"pattern": pattern, "record_id": record_id, "reason": note or None},
            card["equipment_id"],
        )
    return {"pattern": pattern, "record_id": record_id}
