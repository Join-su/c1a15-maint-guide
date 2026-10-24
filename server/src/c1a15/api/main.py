"""API 서버(P-06, B-04): 인증 · 알람 등록 · 배정 · 진단 · 잠금 · 지시 · 결과 · 종 목록 · 과거 기록 · 매뉴얼 원문.

화면은 서버가 준 값만 보인다. 판정은 engine, 문장은 llm(fixture 기본), 저장은 append-only 업무 기록 + 감사.
"""

from datetime import UTC, datetime

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerifyMismatchError
from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from sqlalchemy import Connection, select

from c1a15 import config
from c1a15.alarms import ml
from c1a15.api import deps, history, lead, responses, screen, sessions
from c1a15.api.deps import User, conn, current_user, internal_token, tech_user
from c1a15.api.schemas import AlarmBody, CorrectionBody, EventBody, LoginBody, NoteBody
from c1a15.db import models as m
from c1a15.deploy import runs
from c1a15.deploy.client import PackUnavailable
from c1a15.engine import alarm_rules, rules

PACK = config.pack_settings()  # Pack을 부르는 길 · 배포 서버 주소 — 어긋나면 서버 시작 거절(EV-001 CH-15)
config.r12_inbox()  # R12 받은 편지 폴더 — 절대 경로가 아니면 시작 거절(EV-001 CH-23)
app = FastAPI(title="정비 길잡이 API", version="0.2.0")
app.include_router(lead.router)  # 파트장 API(P-11)


@app.exception_handler(PackUnavailable)
def pack_unavailable(request: Request, exc: PackUnavailable) -> JSONResponse:
    """배포 서버에서 판정을 받지 못함(EV-001 CH-15): 요청 transaction은 되돌려지고(업무 기록 0),
    감사 pack_call_failed는 클라이언트가 따로 남겼다. 화면은 같은 seq로 다시 보낸다(503 = 앱 쪽 코드, D-265)."""
    return JSONResponse(status_code=503, content={"detail": "pack_unavailable", "code": exc.code})


_hasher = PasswordHasher()


@app.get("/api/health")
def health(request: Request) -> dict[str, str | None]:
    # nginx가 앱별 server 블록에서 덮어쓰는 앱 표시를 그대로 돌려준다(EP-C1-WEB-001, 권한 판정 아님).
    return {"status": "ok", "app": request.headers.get("x-app")}


@app.post("/api/login")
def login(
    body: LoginBody, request: Request, response: Response, c: Connection = Depends(conn, scope="function")
) -> dict:
    """사전 등록 계정 · 앱별 역할(R9 · AC-12): 정비자 앱은 정비자만, 파트장 앱은 파트장만."""
    app_id = deps.request_app(request)
    acct = c.execute(select(m.Account.__table__).where(m.Account.user_id == body.user_id)).first()
    ok = False
    if acct:
        try:
            ok = _hasher.verify(acct.password_hash, body.password)
        except (VerifyMismatchError, InvalidHashError):
            ok = False
    if not ok:
        raise HTTPException(status_code=401, detail="bad_credentials")
    if acct.role != app_id:
        sessions.audit_rejection(acct.user_id, "login_rejected", f"app:{app_id}", {"reason": "role_mismatch"})
        raise HTTPException(status_code=403, detail="role_mismatch")
    token = deps.new_session(c, acct.user_id, app_id)
    response.set_cookie(
        deps.COOKIE[app_id], token, httponly=True, samesite="strict", max_age=deps.SESSION_HOURS * 3600, path="/"
    )
    if app_id == "tech":  # R9: 미배정 알람은 다음 로그인 정비자에게
        for (alarm_id,) in c.execute(
            select(m.Alarm.alarm_id).where(m.Alarm.assigned_to.is_(None), m.Alarm.status == "new")
        ).all():
            c.execute(
                m.Alarm.__table__.update()
                .where(m.Alarm.alarm_id == alarm_id)
                .values(assigned_to=acct.user_id, change_seq=deps.next_change_seq(c))
            )
            sessions.audit(
                c, "system", "assign", f"alarm:{alarm_id}", {"to": acct.user_id, "rule": "R9 미배정 → 다음 로그인"}
            )
    sessions.audit(c, acct.user_id, "login", f"app:{app_id}", {})
    return {"user_id": acct.user_id, "display_name": acct.display_name, "role": acct.role}


@app.post("/api/logout")
def logout(
    request: Request,
    response: Response,
    user: User = Depends(current_user),
    c: Connection = Depends(conn, scope="function"),
) -> dict:
    token = request.cookies.get(deps.COOKIE[user.app])
    c.execute(
        m.LoginSession.__table__.update()
        .where(m.LoginSession.token_hash == deps.token_hash(token))
        .values(revoked_at=datetime.now(UTC))
    )
    response.delete_cookie(deps.COOKIE[user.app], path="/")
    return {"ok": True}


@app.post("/api/internal/alarms", dependencies=[Depends(internal_token)])
def register_alarm(body: AlarmBody, c: Connection = Depends(conn, scope="function")) -> dict:
    """시연 알람 발생기(FLOW-01)만 부른다. 경계 판정 · 증상군 = 서버, 시각 = 지금(AC-34-C1), 배정 = R9."""
    assignments = dict(c.execute(select(m.EquipmentAssignment.equipment_id, m.EquipmentAssignment.user_id)).all())
    if body.equipment_id not in assignments:
        raise HTTPException(status_code=422, detail="unknown_equipment")
    pack_cols = {}
    if runs.deploy_on():  # 알람을 켤지 · 증상군 = Pack alarm Run(EV-001 ES-08, D-259 (2))
        hit, snapshot, pack_cols = _alarm_via_pack(c, body)
        if hit is None:
            return pack_cols  # 알람 없이 '사람 판단 필요' 후보로 기록함
    else:
        try:
            hit = alarm_rules.detect(body.sensor_snapshot, deps.alarm_table())
        except KeyError as e:
            raise HTTPException(status_code=422, detail="bad_sensor_snapshot") from e
        if hit is None:
            raise HTTPException(status_code=422, detail="no_boundary_crossed")
        snapshot = body.sensor_snapshot
    to = rules.assign(body.equipment_id, assignments, sessions.open_alarm_counts(c))
    now = datetime.now(UTC)
    alarm_id = c.execute(
        m.Alarm.__table__.insert()
        .values(
            equipment_id=body.equipment_id,
            symptom_group=hit["group"],
            alarm=hit["alarm"],
            sensor_snapshot=snapshot,
            **pack_cols,
            trend=[p.model_dump() for p in body.trend],
            scenario_id=body.scenario_id,
            eval_mode=body.eval_mode,
            occurred_at=now,
            assigned_to=to,
            change_seq=deps.next_change_seq(c),
        )
        .returning(m.Alarm.alarm_id)
    ).scalar_one()
    sessions.audit(
        c,
        "system",
        "alarm",
        f"alarm:{alarm_id}",
        {"assigned_to": to, "scenario_id": body.scenario_id, **({"eval_mode": True} if body.eval_mode else {})},
        body.equipment_id,
    )
    return {"alarm_id": alarm_id, "assigned_to": to, "occurred_at": now.isoformat(), "symptom_group": hit["group"]}


def _alarm_via_pack(c: Connection, body: AlarmBody) -> tuple[dict | None, dict, dict]:
    """Pack alarm Run(정본 = c1a15-pack 약속 v2): 알람이면 (경계 판정 모양 hit, 센서 7칸, 저장 칸),
    후보(낮은 확신 · RNF · 예측 실패 D-275)면 alarm_candidates에 기록하고 (None, {}, 응답)을 돌려준다."""
    sc = deps.scenarios().get(body.scenario_id or "", {})
    lineage = body.data_lineage
    if lineage is None and sc.get("udi"):
        lineage = {"source_release": runs.source_release(), "row_id": int(sc["udi"]), "split": "demo"}
    if lineage is None:
        raise HTTPException(status_code=422, detail="missing_lineage")
    mode = "ml_predicted" if runs.settings()["alarm"] == "ml" else "sensor_boundary"
    ptype = body.product_type or sc.get("product_type")
    if mode == "ml_predicted" and not ptype:
        raise HTTPException(status_code=422, detail="missing_product_type")
    try:
        req = runs.alarm_body(
            runs.new_event_id(),
            body.equipment_id,
            body.sensor_snapshot,
            mode,
            lineage,
            ptype,
            ml.threshold() if mode == "ml_predicted" else None,
        )
    except KeyError as e:
        raise HTTPException(status_code=422, detail="bad_sensor_snapshot") from e
    event_id = req["event_card"]["event_id"]
    try:
        res = runs.alarm(event_id, req)
    except PackUnavailable as e:
        if (
            e.code == "run_failed" and e.where == "run.predict_failure"
        ):  # D-275: 예측 실패 = Run 실패 → 후보 model_failure
            cand = {"reason": "model_failure", "risk": None, "top_k": [], "model_release": None, "run_id": e.run_id}
            return None, {}, _store_candidate(c, body, req, cand)
        raise
    out = res.output["alarm"]
    refs = {"event_id": event_id, "run_id": res.run_id, "deployment_id": res.deployment_id}
    if out.get("candidate"):
        return None, {}, _store_candidate(c, body, req, {**out["candidate"], "run_id": res.run_id})
    if not out["alarm"]:
        raise HTTPException(status_code=422, detail="no_boundary_crossed")  # 지금 기본 길과 같은 응답 · 저장 0
    if out["alarm_block"] is None:  # ML 유형으로 정한 알람(경계 표시 없음) — 화면 · 세션이 알람 행의 경계 표시를 씀
        sessions.audit_rejection(  # 화면 판(정할 것)까지 알람으로 등록하지 않음 — 감사는 따로 남김
            "system",
            "alarm_rejected",
            f"event:{event_id}",
            {"reason": "ml_type_alarm_unsupported", **refs},
            body.equipment_id,
        )
        raise HTTPException(status_code=422, detail="ml_type_alarm_unsupported")
    snapshot = {**req["event_card"]["sensor_snapshot"], **out["sensor_derived"]}  # 화면 · 리트리버 센서 7칸
    if out.get("ml") is not None:  # 없으면 칸을 빼 SQL NULL(JSON null로 저장하지 않음)
        refs["ml"] = out["ml"]
    return {"group": out["group"], "alarm": out["alarm_block"]}, snapshot, refs


def _store_candidate(c: Connection, body: AlarmBody, req: dict, cand: dict) -> dict:
    """알람을 만들지 않은 '사람 판단 필요' 기록(ES-04 표) — 화면 0."""
    card = req["event_card"]
    try:
        crossed = alarm_rules.detect(body.sensor_snapshot, deps.alarm_table()) is not None  # 기록용(판정 아님)
    except KeyError:
        crossed = False
    cid = c.execute(
        m.AlarmCandidate.__table__.insert()
        .values(
            equipment_id=body.equipment_id,
            reason=cand["reason"],
            risk=cand.get("risk"),
            top_k=cand.get("top_k") or [],
            boundary_crossed=bool(cand.get("boundary_crossed", crossed)),
            model_release=cand.get("model_release"),
            sensor_snapshot=card["sensor_snapshot"],
            event=card,
            eval_mode=body.eval_mode,
            event_id=card["event_id"],
            run_id=cand.get("run_id"),
        )
        .returning(m.AlarmCandidate.candidate_id)
    ).scalar_one()
    sessions.audit(
        c,
        "system",
        "alarm_candidate",
        f"candidate:{cid}",
        {"reason": cand["reason"], "event_id": card["event_id"]},
        body.equipment_id,
    )
    return {"alarm_id": None, "candidate_id": cid, "reason": cand["reason"]}


def _alarm_view(a) -> dict:
    return {
        "alarm_id": a.alarm_id,
        "equipment_id": a.equipment_id,
        "symptom_group": a.symptom_group,
        "group_name": deps.group_names()[a.symptom_group],  # P-19: 알람 행 증상 이름
        "alarm": a.alarm,
        "sensor_snapshot": a.sensor_snapshot,
        "trend": a.trend,
        "occurred_at": a.occurred_at.isoformat(),
        "status": a.status,
        "change_seq": a.change_seq,
    }


@app.get("/api/tech/home", response_model=responses.Home)
def tech_home(since: int = 0, user: User = Depends(tech_user), c: Connection = Depends(conn, scope="function")) -> dict:
    """주기 조회(EP-C1-SYNC-001): 내 알람과 진행 중 세션, 변경 순번."""
    start, end = screen.shift_window()
    reports = c.execute(  # 내 확정 보고서(S-03): 최근 · 이 교대 완료 수 · 완료 알람 행
        select(m.Report.__table__, m.DiagSession.alarm_id, m.Alarm.equipment_id)
        .join(m.DiagSession, m.DiagSession.session_id == m.Report.session_id)
        .join(m.Alarm, m.Alarm.alarm_id == m.DiagSession.alarm_id)
        .where(m.Report.author == user.user_id)
        .order_by(m.Report.confirmed_at.desc())
    ).all()
    names = dict(c.execute(select(m.Account.user_id, m.Account.display_name)).all())
    in_shift = [  # 처리 완료 = 이 교대에 확정해 반려되지 않은 내 보고서
        r for r in reports if r.status != "rejected" and r.confirmed_at and start <= r.confirmed_at < end
    ]
    done_alarm_ids = [r.alarm_id for r in in_shift]
    rows = c.execute(
        select(m.Alarm.__table__)
        .where(
            m.Alarm.assigned_to == user.user_id,
            m.Alarm.status.in_(["new", "in_progress"]) | m.Alarm.alarm_id.in_(done_alarm_ids or [-1]),
        )
        .order_by(m.Alarm.occurred_at.desc())
    ).all()
    alarms = [_alarm_view(a) for a in rows]
    report_of = {r.alarm_id: r for r in reports}
    for a in alarms:  # 완료 알람 행(T02 초록 점): 보고서 상태 · 세션
        r = report_of.get(a["alarm_id"])
        a["report_status"] = r.status if r else None
        a["report_session_id"] = r.session_id if r else None
    calls = c.execute(
        select(m.Call.call_id).where(m.Call.sent_by == user.user_id, m.Call.sent_at >= start, m.Call.sent_at < end)
    ).all()
    in_progress = []
    mine = select(m.DiagSession.__table__).where(
        m.DiagSession.user_id == user.user_id, m.DiagSession.status == "in_progress"
    )
    for s in c.execute(mine).all():
        prog = sessions.progress(c, m.DiagSession(**s._mapping))
        in_progress.append({"session_id": s.session_id, "alarm_id": s.alarm_id, "progress": prog})
    by_alarm = {s["alarm_id"]: s for s in in_progress}
    for a in alarms:  # P-19 ①: 진행 중 알람 행의 '점검 n / 최대 m'
        a["session_id"] = by_alarm[a["alarm_id"]]["session_id"] if a["alarm_id"] in by_alarm else None
        a["progress"] = by_alarm[a["alarm_id"]]["progress"] if a["alarm_id"] in by_alarm else None
    latest = max([a["change_seq"] for a in alarms] + [since])
    return {
        "alarms": alarms,
        "new_since": [a for a in alarms if a["change_seq"] > since],
        "in_progress": in_progress,
        "change_seq": latest,
        "shift": screen.shift_summary(len(in_progress), done=len(in_shift), calls=len(calls)),  # 결정 014 ④
        "recent_reports": [  # 최근 내 보고서(상태 칩), 최근 3건
            {
                "report_id": r.report_id,
                "session_id": r.session_id,
                "equipment_id": r.equipment_id,
                "cause": next((f["text"] for f in r.fields if f["key"] == "cause"), ""),
                "confirmed_at": r.confirmed_at.isoformat() if r.confirmed_at else None,
                "status": r.status,
                # AC-11-C1: 반려 · 사유(반려 기록은 S-04 P-11이 쓴다)
                **(
                    {
                        "reject_reason": r.rejection.get("reason"),
                        "rejected_by_name": names.get(r.rejection.get("by")),
                        "rejected_at": r.rejection.get("at"),
                    }
                    if r.status == "rejected" and r.rejection
                    else {}
                ),
            }
            for r in reports[:3]
        ],
    }


@app.get("/api/tech/notifications", response_model=responses.Notifications, response_model_exclude_unset=True)
def tech_notifications(user: User = Depends(tech_user), c: Connection = Depends(conn, scope="function")) -> dict:
    """종 목록(FLOW-13, AC-37): 배정된 새 알람 · 진행 중 점검 · 답이 온 호출 · 반려된 보고서.

    뒤 두 종류는 S-03 · S-04에서 채운다.
    """
    home = tech_home(0, user, c)
    alarms = {a["alarm_id"]: a for a in home["alarms"]}

    def row(a: dict) -> dict:  # P-19 ②: 항목 행 = 설비 · 증상 · 시각
        return {"equipment_id": a["equipment_id"], "group_name": a["group_name"], "occurred_at": a["occurred_at"]}

    items = [{"kind": "new_alarm", "alarm_id": a["alarm_id"], **row(a)} for a in home["alarms"] if a["status"] == "new"]
    items += [
        {"kind": "in_progress", "session_id": s["session_id"], "alarm_id": s["alarm_id"], "progress": s["progress"]}
        | (row(alarms[s["alarm_id"]]) if s["alarm_id"] in alarms else {})
        for s in home["in_progress"]
    ]
    k = deps.manual()
    answered = c.execute(  # 파트장 답이 온 호출(AC-37, 답은 S-04 P-11이 쓴다)
        select(m.Call.__table__, m.DiagSession.alarm_id)
        .join(m.DiagSession, m.DiagSession.session_id == m.Call.session_id)
        .where(m.DiagSession.user_id == user.user_id, m.DiagSession.status == "in_progress", m.Call.answer.is_not(None))
        .order_by(m.Call.answered_at.desc())
    ).all()
    names = dict(c.execute(select(m.Account.user_id, m.Account.display_name)).all())
    answered_sessions = {cl.session_id for cl in answered}
    for it in items:  # T12: 진행 중 항목 '· 파트장 답 도착'
        if it["kind"] == "in_progress" and it["session_id"] in answered_sessions:
            it["answer"] = next(cl.answer.get("answer") for cl in answered if cl.session_id == it["session_id"])
    for cl in answered:
        a = alarms.get(cl.alarm_id)
        items.append(
            {
                "kind": "answered_call",
                "alarm_id": cl.alarm_id,
                "session_id": cl.session_id,
                "call_section": cl.section,
                "call_title": k.sections[cl.section]["title"] if cl.section in k.sections else None,
                "call_grade": cl.grade,
                "answer": cl.answer.get("answer"),
                "answered_by": cl.answer.get("by"),
                "answered_by_name": names.get(cl.answer.get("by")),
                "answered_at": cl.answered_at.isoformat() if cl.answered_at else None,
            }
            | (
                {"equipment_id": a["equipment_id"], "group_name": a["group_name"], "occurred_at": a["occurred_at"]}
                if a
                else {}
            )
        )
    rejected = c.execute(  # 반려된 보고서(AC-37 · AC-11, 반려는 S-04 P-11이 쓴다)
        select(m.Report.__table__, m.DiagSession.alarm_id)
        .join(m.DiagSession, m.DiagSession.session_id == m.Report.session_id)
        .where(m.Report.author == user.user_id, m.Report.status == "rejected")
        .order_by(m.Report.updated_at.desc())
    ).all()
    for r in rejected:
        a = alarms.get(r.alarm_id)
        rj = r.rejection or {}
        items.append(
            {
                "kind": "rejected_report",
                "alarm_id": r.alarm_id,
                "session_id": r.session_id,
                "report_cause": next((f["text"] for f in r.fields if f["key"] == "cause"), None),
                "reject_reason": rj.get("reason"),
                "rejected_by_name": names.get(rj.get("by")),
                "rejected_at": rj.get("at"),
            }
            | (row(a) if a else {})
        )
    return {"items": items, "empty": not items}


@app.post(
    "/api/tech/alarms/{alarm_id}/session",
    response_model=responses.SessionWithPreview,
    response_model_exclude_unset=True,
)
def start_session(
    alarm_id: int, user: User = Depends(tech_user), c: Connection = Depends(conn, scope="function")
) -> dict:
    row = c.execute(select(m.Alarm.__table__).where(m.Alarm.alarm_id == alarm_id)).first()
    if row is None:
        raise HTTPException(status_code=404, detail="no_alarm")
    if row.assigned_to != user.user_id:
        raise HTTPException(status_code=403, detail="not_assigned")
    sid = sessions.create(c, m.Alarm(**row._mapping), user.user_id)
    s = sessions.session_for(c, sid, user.user_id)
    return {**sessions.view(c, s), "preview": sessions.preview(s, c)}


@app.get("/api/tech/sessions/{sid}", response_model=responses.SessionWithPreview, response_model_exclude_unset=True)
def get_session(sid: int, user: User = Depends(tech_user), c: Connection = Depends(conn, scope="function")) -> dict:
    s = sessions.session_for(c, sid, user.user_id)
    return {**sessions.view(c, s), "preview": sessions.preview(s, c)}


@app.post("/api/tech/sessions/{sid}/events", response_model=responses.SessionView, response_model_exclude_unset=True)
def post_event(
    sid: int, body: EventBody, user: User = Depends(tech_user), c: Connection = Depends(conn, scope="function")
) -> dict:
    s = sessions.session_for(c, sid, user.user_id)
    return sessions.post_event(c, s, user.user_id, body.model_dump(exclude_none=True))


@app.get("/api/tech/sessions/{sid}/history", response_model=responses.SessionPast, response_model_exclude_unset=True)
def get_history(sid: int, user: User = Depends(tech_user), c: Connection = Depends(conn, scope="function")) -> dict:
    """T15 지난 화면(S-05 P-14): 진행 표시 5단계의 제출 기록 · 그때 값 · 정정 · 덧붙인 메모."""
    s = sessions.session_for(c, sid, user.user_id)
    return history.history(c, s)


@app.post(
    "/api/tech/sessions/{sid}/corrections", response_model=responses.SessionView, response_model_exclude_unset=True
)
def post_correction(
    sid: int, body: CorrectionBody, user: User = Depends(tech_user), c: Connection = Depends(conn, scope="function")
) -> dict:
    """T15 정정(S-05 P-14): 덧붙임 기록 · 감사 · 다시 판정 또는 정정 호출 · 보낸 호출에 붙임."""
    s = sessions.session_for(c, sid, user.user_id)
    return sessions.post_correction(c, s, user.user_id, body.model_dump(exclude_unset=True))


@app.post("/api/tech/sessions/{sid}/notes", response_model=responses.SessionView, response_model_exclude_unset=True)
def post_note(
    sid: int, body: NoteBody, user: User = Depends(tech_user), c: Connection = Depends(conn, scope="function")
) -> dict:
    """T15 메모 덧붙이기(S-05 P-14)."""
    s = sessions.session_for(c, sid, user.user_id)
    return sessions.post_note(c, s, user.user_id, body.model_dump())


@app.get("/api/tech/sessions/{sid}/manual/{section}")
def manual_section(
    sid: int, section: str, user: User = Depends(tech_user), c: Connection = Depends(conn, scope="function")
) -> dict:
    """매뉴얼 원문(AC-39): 잠금 뒤, 이 세션에서 지시된 절만(R1 · R2). 절차 · 판정 기준 · 현재 등급 · 소요 분."""
    s = sessions.session_for(c, sid, user.user_id)
    if not sessions.view(c, s)["locked"]:
        raise HTTPException(status_code=409, detail="not_locked")
    k = deps.manual()
    if section not in k.sections:
        raise HTTPException(status_code=404, detail="no_section")
    if section not in sessions.instructed_sections(sessions.events_of(c, sid)):  # R2: 지시되지 않은 C · D 절 원문 금지
        raise HTTPException(status_code=409, detail="not_instructed")
    g, minutes = deps.grades(c)
    sec = k.sections[section]
    return {
        "section": section,
        "title": sec["title"],
        "text": sec["text"],
        "grade": g.get(section),
        "minutes": minutes.get(section),
    }


@app.get("/api/records/{record_id}", response_model=responses.Record)
def record(record_id: str, user: User = Depends(current_user), c: Connection = Depends(conn, scope="function")) -> dict:
    """과거 기록 전체(AC-38): 설비 · 발생 시각 · 증상 · 센서 값 · 점검 경로 · 확정 원인 · 조치 · 정지 시간 · 서술."""
    row = c.execute(
        select(m.HistoryRecord.record, m.HistoryRecord.source, m.HistoryRecord.provenance).where(
            m.HistoryRecord.record_id == record_id
        )
    ).first()
    if row is None:
        raise HTTPException(status_code=404, detail="no_record")
    r = row.record
    return {
        "record_id": record_id,
        "equipment_id": r["equipment_id"],
        "equipment_type": r.get("equipment_type"),  # P-19 ⑦: 설비 종류 · 승인 · 출처
        "approval": r.get("approval"),
        "source": row.source,
        "provenance": row.provenance,
        "occurred_at": r["occurred_at"],
        "symptom": r["symptom_group"],
        "alarm": r["alarm"],
        "sensor_snapshot": r["sensor_snapshot"],
        "steps": r["steps"],
        "outcome": r["outcome"],
        "downtime_min": r["downtime_min"],
        "narrative": r["narrative"],
    }
