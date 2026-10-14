# ruff: noqa: F811, E501 — test_api의 fixture(api · db · night)를 이름으로 가져와 쓴다, 시험 설명 문장은 길이 제한 밖
"""P-11 파트장 API 통합 시험(시험 DB): 승인 대기 · 검토 결정 · 이력 변환(R12) · 호출 답 · 권한 등급(R13) · 감사 조회.

값 정의는 사용자 결정 018(권한 위반 · 등급 표 범위 · 직접 확인 · 숙련자 인계 답 · 이력 변환).
"""

from datetime import datetime, timedelta

import pytest
from sqlalchemy import text

from test_api import (  # noqa: F401 — fixture(api · db · night)는 이름으로 쓴다
    LEAD_PW,
    api,
    db,
    ev,
    login,
    night,
    ok,
    register,
    reset_ops,
    run_until,
    start,
    to_instruct,
)

pytestmark = pytest.mark.db


def lead(api):
    c, r = login(api, "lead", "lead.park", LEAD_PW)
    assert r.status_code == 200
    return c


def confirmed_report(api, db, equipment="M-01", memo="기름때가 필터 표면 절반 넘게 덮음"):
    """정비자: 4.3 이상 → 조치 → 재가동 → 경계 이내 → 보고서 확정(승인 대기)."""
    tech, s = start(api, db, equipment=equipment)
    s = to_instruct(tech, s)
    s = ok(tech, s, type="result", section="4.3", value="이상", memo=memo)
    s = ok(tech, s, type="action_done", section="4.3.2")
    s = ok(tech, s, type="restart", checked=s["restart"]["checklist"])
    s = ok(tech, s, type="restart_result", outcome="within")
    s = ok(tech, s, type="report_confirm")
    with db.connect() as c:
        rid = c.execute(
            text("select report_id from ops.reports where session_id = :s"), {"s": s["session_id"]}
        ).scalar()
    return tech, s, rid


def test_lead_role_boundary_and_empty_overview(api, db):
    """AC-12(파트장 API 부분) · AC-27-C3: 파트장 역할만, 비면 타일 0 · 빈 행."""
    reset_ops(db)
    tech, _ = login(api, "tech", "tech.kim", __import__("test_api").TECH_PW)
    assert tech.get("/api/lead/overview").status_code in {401, 403}
    lc = lead(api)
    o = lc.get("/api/lead/overview").json()
    assert o["tiles"] == {"awaiting": 0, "calls_open": 0, "violations": 0} and o["rows"] == []
    assert lc.get("/api/tech/home").status_code in {401, 403}


def r3_positions(db, hid):
    """다음 온도 차 저하(CL) 알람 질의에서 그 기록의 (BM25 순위, pgvector 순위, RRF 합친 순위) — 없으면 None."""
    from c1a15.api import deps
    from c1a15.loader.embedding import fake_embedding
    from c1a15.retrieval import db as rdb
    from c1a15.retrieval import search

    idx = deps.index()
    ids = sorted(dc.record_id for dc in idx.docs if dc.symptom_group == "CL")
    q = search.query_text("온도 차 저하", "경계 아래", [])
    bm = idx.bm25.rank(q, ids)
    with db.connect() as c:
        vec = rdb.vector_ranks(c, {"symptom_group": "CL"}, fake_embedding(q))
    fused = search.rrf([bm, [x for x in vec if x in set(ids)]])
    order = sorted(fused, key=lambda x: (-fused[x], x))
    pos = lambda xs: xs.index(hid) + 1 if hid in xs else None  # noqa: E731
    return pos(bm), pos(vec), pos(order)


def test_lead_overview_rows_and_approve_adds_history(api, db):
    """AC-27-C1 · C2 · AC-29-C3 · AC-09-C1 · R12(결정 018 ⑤): 승인 대기 행 → 그대로 승인 → R-번호 이력 · 색인 → 다음 진단 후보."""
    from c1a15.api import deps

    reset_ops(db)
    tech, s, rid = confirmed_report(api, db)
    lc = lead(api)
    o = lc.get("/api/lead/overview").json()
    row = o["rows"][0]
    assert o["tiles"]["awaiting"] == 1 and o["tiles"]["violations"] == 0
    assert (row["equipment_id"], row["group_name"], row["cause"]) == ("M-01", "온도 차 저하", "냉각 필터 막힘")
    assert row["author_name"] and row["confirmed_at"] and row["evidence_count"] == 3 and row["violations"] == 0
    d = lc.get(f"/api/lead/reports/{rid}").json()
    assert [f["label"] for f in d["fields"]] == ["확정 원인", "점검 경로", "조치", "근거 사례", "미확인"]
    before = r3_positions(db, f"R-{rid:04d}")
    r = lc.post(f"/api/lead/reports/{rid}/decision", json={"decision": "approve"})
    assert r.status_code == 200 and r.json()["history_record_id"] == f"R-{rid:04d}"
    hid = r.json()["history_record_id"]
    with db.connect() as c:
        h = c.execute(
            text("select source, symptom_group, record from knowledge.history_records where record_id = :i"), {"i": hid}
        ).one()
        emb = c.execute(
            text("select count(*) from knowledge.history_embeddings where record_id = :i"), {"i": hid}
        ).scalar()
        st = c.execute(text("select status, approval from ops.reports where report_id = :r"), {"r": rid}).one()
    assert h.source == "approved_report" and h.symptom_group == "CL" and emb == 1
    rec = h.record
    assert (
        rec["source"] == {"report_id": rid}
        and rec["outcome"]["cause_code"] == "CL-1"
        and rec["approval"]["status"] == "승인"
    )
    assert [x["kind"] for x in rec["steps"]][:2] == ["lock", "check"] and rec["narrative"].endswith("분.")
    assert st.status == "approved" and st.approval["mode"] == "approve"
    assert any(dc.record_id == hid for dc in deps.index().docs)  # BM25 · 문서 목록에 추가
    home = tech.get("/api/tech/home").json()
    assert home["recent_reports"][0]["status"] == "approved"
    # 결정 018 ⑥(AC-09-C1): 다음 같은 증상군 알람의 R3 검색 대상(BM25 · pgvector 의미 색인)에 들어 순위가 매겨진다.
    # 서버 경로 그대로(BM25 메모리 색인 + DB vector_ranks → RRF). 승인 전에는 어느 순위에도 없었다.
    after = r3_positions(db, hid)
    print(f"AC-09 R3 순위(BM25, pgvector, RRF 합친 순위): 승인 전 {before} · 승인 뒤 {after}")
    assert before == (None, None, None) and after[0] <= 5 and after[1] is not None and after[2] is not None
    rec_view = tech.get(f"/api/records/{hid}").json()  # 기록 창에서 R-번호로 열림
    assert rec_view["source"] == "approved_report" and rec_view["outcome"]["cause_name"] == "냉각 필터 막힘"
    assert (
        lc.post(f"/api/lead/reports/{rid}/decision", json={"decision": "approve"}).status_code == 409
    )  # 두 번 승인 없음


def test_lead_violation_tile_counts_reports(api, db):
    """AC-27-C1 · 결정 018 ①: 지시로 열리지 않은 절의 결과가 든 보고서는 행 위반 수 · 타일(위반 1건 이상 보고서 수)에 셈."""
    reset_ops(db)
    _, s, rid = confirmed_report(api, db)
    _, s2, rid2 = confirmed_report(api, db, equipment="M-03")
    with db.begin() as c:  # 시험 DB: 결과 하나의 절을 지시받지 않은 절로 바꿔 위반 기록을 만든다
        c.execute(
            text(
                "update ops.session_events set payload = jsonb_set(payload, '{section}', '\"4.5\"') "
                "where session_id = :s and type = 'result'"
            ),
            {"s": s["session_id"]},
        )
    o = lead(api).get("/api/lead/overview").json()
    rows = {r["report_id"]: r["violations"] for r in o["rows"]}
    assert o["tiles"]["violations"] == 1 and rows[rid] >= 1 and rows[rid2] == 0


def test_approve_index_only_after_commit(api, db, monkeypatch):
    """R12 · G6-S04-2 비차단 ③: 승인 요청이 commit 전에 실패하면 이력 행도 메모리 색인도 남지 않고, commit 뒤 할 일은 성공 때만 돈다."""
    from c1a15.api import deps
    from c1a15.api import lead as lead_api

    called: list[str] = []
    g = deps.conn()
    next(g).info["after_commit"].append(lambda: called.append("x"))
    with pytest.raises(RuntimeError):
        g.throw(RuntimeError("요청 실패"))
    g = deps.conn()
    next(g).info["after_commit"].append(lambda: called.append("ok"))
    with pytest.raises(StopIteration):
        next(g)
    assert called == ["ok"]
    reset_ops(db)
    _, s, rid = confirmed_report(api, db)
    hid = f"R-{rid:04d}"
    real = lead_api.sessions.audit

    def boom(c, user_id, action, *a, **k):
        if action == "report_approve":
            raise RuntimeError("승인 감사 실패")
        return real(c, user_id, action, *a, **k)

    monkeypatch.setattr(lead_api.sessions, "audit", boom)
    with pytest.raises(RuntimeError):
        lead(api).post(f"/api/lead/reports/{rid}/decision", json={"decision": "approve"})
    assert not any(dc.record_id == hid for dc in deps.index().docs)
    with db.connect() as c:
        assert not c.execute(
            text("select count(*) from knowledge.history_records where record_id = :i"), {"i": hid}
        ).scalar()
        assert (
            c.execute(text("select status from ops.reports where report_id = :r"), {"r": rid}).scalar()
            == "awaiting_approval"
        )


def test_lead_eval_mode_report_not_indexed(api, db):
    """AC-09-C2(결정 017 ②: 평가 모드 표시는 시험 DB로): 평가 모드 알람의 보고서는 승인해도 이력에 들어가지 않는다."""
    reset_ops(db)
    _, s, rid = confirmed_report(api, db)
    with db.begin() as c:
        c.execute(text("update ops.alarms set eval_mode = true where alarm_id = :a"), {"a": s["alarm_id"]})
    lc = lead(api)
    r = lc.post(f"/api/lead/reports/{rid}/decision", json={"decision": "approve"})
    assert r.status_code == 200 and r.json().get("history_record_id") is None
    with db.connect() as c:
        n = c.execute(
            text("select count(*) from knowledge.history_records where record_id = :i"), {"i": f"R-{rid:04d}"}
        ).scalar()
    assert n == 0


def test_lead_edit_approve_r8_and_audit(api, db):
    """AC-06(P-11) · AC-10 · L03 / edit · edit_failed: 근거 없는 수치는 승인 안 됨, 고친 항목 전 → 후 · 메모가 감사에."""
    reset_ops(db)
    _, s, rid = confirmed_report(api, db)
    lc = lead(api)
    bad = {"unresolved": "냉각 팬 상태(4.4, C) · 팬 회전수 1,850 rpm으로 정상 확인"}
    chk = lc.post(f"/api/lead/reports/{rid}/check", json={"edits": bad}).json()
    assert (
        not chk["ok"]
        and chk["fields"][0]["unsupported_numbers"]
        and "세션 입력·매뉴얼 원문에 없습니다" in chk["messages"][0]
    )
    r = lc.post(f"/api/lead/reports/{rid}/decision", json={"decision": "edit", "edits": bad, "memo": "팬 상태 확인됨"})
    assert r.status_code == 409 and r.json()["detail"]["reason"] == "edit_ungrounded"
    good = {"unresolved": "냉각 팬 상태(4.4, C) · 주간 조 확인 배정"}
    assert lc.post(f"/api/lead/reports/{rid}/check", json={"edits": good}).json()["ok"]
    r = lc.post(
        f"/api/lead/reports/{rid}/decision", json={"decision": "edit", "edits": good, "memo": "주간 확인 담당을 지정함"}
    )
    assert r.status_code == 200
    with db.connect() as c:
        ap = c.execute(text("select approval, fields from ops.reports where report_id = :r"), {"r": rid}).one()
        au = c.execute(text("select detail from ops.audit_log where action = 'report_edit_approve'")).scalar()
        rej = [d for (d,) in c.execute(text("select detail from ops.audit_log where action = 'reject'"))]
    e = ap.approval["edits"][0]
    assert (
        ap.approval["mode"] == "edit"
        and e["field"] == "unresolved"
        and e["after"] == good["unresolved"]
        and e["before"]
    )
    assert au["edits"][0]["after"] == good["unresolved"] and au["memo"] == "주간 확인 담당을 지정함"  # AC-10-C1
    assert {f["key"]: f["text"] for f in ap.fields}["unresolved"] == good["unresolved"]
    assert any(d.get("reason") == "edit_ungrounded" for d in rej)


def test_lead_reject_requires_reason_and_reaches_tech(api, db, night):
    """AC-24 · AC-11-C1(API) · AC-37(반려 항목): 사유 없으면 거부(감사), 사유 있으면 정비자 최근 보고서 · 종 목록 · 세션 재개."""
    reset_ops(db)
    tech, s, rid = confirmed_report(api, db)
    lc = lead(api)
    r = lc.post(f"/api/lead/reports/{rid}/decision", json={"decision": "reject", "memo": "  "})
    assert r.status_code == 409 and r.json()["detail"] == "reason_required"
    with db.connect() as c:
        assert (
            c.execute(text("select status from ops.reports where report_id = :r"), {"r": rid}).scalar()
            == "awaiting_approval"
        )
        assert (
            c.execute(
                text(
                    "select count(*) from ops.audit_log where action = 'reject' and detail->>'reason' = 'reason_required'"
                )
            ).scalar()
            == 1
        )
    reason = "필터 표면 상태를 메모로 다시 적어 주세요"
    assert lc.post(f"/api/lead/reports/{rid}/decision", json={"decision": "reject", "memo": reason}).status_code == 200
    rr = tech.get("/api/tech/home").json()["recent_reports"][0]
    assert rr["status"] == "rejected" and rr["reject_reason"] == reason and rr["rejected_by_name"]
    items = tech.get("/api/tech/notifications").json()["items"]
    assert any(i["kind"] == "rejected_report" and i["reject_reason"] == reason for i in items)
    s = tech.get(f"/api/tech/sessions/{s['session_id']}").json()
    assert (
        s["status"] == "in_progress" and s["step"]["kind"] == "report" and s["report"]["rejection"]["reason"] == reason
    )
    s = ok(tech, s, type="report_confirm")  # AC-11-C2: 다시 확정 → 승인 대기
    assert lc.get("/api/lead/overview").json()["rows"][0]["report_id"] == rid


def test_lead_call_answers(api, db):
    """AC-08 · AC-23-C1 · C3 · AC-42(API) · L04: 호출 목록 · 상세 선택지, D는 승인 없음(서버 거부), 승인 → 그 C 지시."""
    reset_ops(db)
    tech, s = start(api, db)
    s = to_instruct(tech, s)
    s = run_until(tech, s, {"call"}, lambda sec: "정상")
    sec = s["call"]["section"]
    s = ok(tech, s, type="call_send")
    lc = lead(api)
    rows = lc.get("/api/lead/calls").json()["rows"]
    assert (
        rows[0]["kind"] == "approval" and rows[0]["need"] == f"냉각 팬 분해 점검({sec}, C)" and rows[0]["sender_name"]
    )
    cid = rows[0]["call_id"]
    d = lc.get(f"/api/lead/calls/{cid}").json()
    assert [o["value"] for o in d["options"]] == ["approved", "daytime", "direct"] and d["summary"]
    assert lc.get("/api/lead/overview").json()["tiles"]["calls_open"] == 1
    r = lc.post(f"/api/lead/calls/{cid}/answer", json={"answer": "assign"})
    assert r.status_code == 409  # 파트장 호출에 인계 답 없음
    assert (
        lc.post(f"/api/lead/calls/{cid}/answer", json={"answer": "approved", "note": "팬 점검 승인"}).status_code == 200
    )
    assert lc.post(f"/api/lead/calls/{cid}/answer", json={"answer": "daytime"}).status_code == 409  # 한 번만
    s = tech.get(f"/api/tech/sessions/{s['session_id']}").json()
    assert s["step"]["kind"] == "instruct" and s["instruction"]["section"] == sec  # AC-08-C2
    assert s["call"]["answer"]["by"] == "lead.park" and s["call"]["answer"]["at"]
    s = ok(tech, s, type="result", section=sec, value="이상", memo="팬 축 유격 큼")  # AC-42-C1: 확정형 C '이상'
    assert s["step"]["kind"] in {"call", "action", "action_after_checklist"} and s["action"]["cause_code"] == "CL-2"
    assert (
        lc.get("/api/lead/calls").json()["rows"][0]["call_id"] != cid
        if lc.get("/api/lead/calls").json()["rows"]
        else True
    )
    # D 등급 호출(초기화하면 로그인도 지워지므로 다시 로그인)
    reset_ops(db)
    with db.begin() as c:
        c.execute(text(f"update ops.grade_table set grade = 'D' where section_id = '{sec}'"))
    tech, s = start(api, db)
    s = to_instruct(tech, s)
    s = run_until(tech, s, {"call"}, lambda x: "정상")
    s = ok(tech, s, type="call_send")
    lc = lead(api)
    cid = lc.get("/api/lead/calls").json()["rows"][0]["call_id"]
    assert [o["value"] for o in lc.get(f"/api/lead/calls/{cid}").json()["options"]] == ["daytime", "direct"]  # AC-23-C3
    r = lc.post(f"/api/lead/calls/{cid}/answer", json={"answer": "approved"})
    assert r.status_code == 409 and r.json()["detail"] == "answer_not_allowed"
    assert (
        lc.post(f"/api/lead/calls/{cid}/answer", json={"answer": "daytime", "note": "주간 정비 배정"}).status_code
        == 200
    )
    s = tech.get(f"/api/tech/sessions/{s['session_id']}").json()
    f = {x["key"]: x["text"] for x in s["report"]["fields"]}
    assert s["step"]["outcome"] == "daytime" and "주간 처리 요청 · 주간 정비 배정" in f["unresolved"]  # AC-23-C1


def test_lead_handover_answer(api, db):
    """AC-23-C4 · 결정 018 ④: 숙련자 인계 → 답 대기 → 주간 숙련자 배정 + 처리 메모 → 보고서에 기록."""
    reset_ops(db)
    with db.begin() as c:
        c.execute(text("update ops.grade_table set grade = 'A' where section_id = '4.4'"))
    tech, s = start(api, db)
    s = to_instruct(tech, s)
    s = run_until(tech, s, {"handover"}, lambda sec: "확인 불가" if sec in {"4.3", "4.4"} else "정상")
    s = ok(tech, s, type="call_send")
    lc = lead(api)
    row = lc.get("/api/lead/calls").json()["rows"][0]
    assert row["kind"] == "handover" and row["need"] == "점검 소진 · 원인 미상"
    d = lc.get(f"/api/lead/calls/{row['call_id']}").json()
    assert [o["label"] for o in d["options"]] == ["주간 숙련자 배정", "직접 확인"]
    assert lc.post(f"/api/lead/calls/{row['call_id']}/answer", json={"answer": "approved"}).status_code == 409
    assert (
        lc.post(
            f"/api/lead/calls/{row['call_id']}/answer", json={"answer": "assign", "note": "주간 조 숙련자"}
        ).status_code
        == 200
    )
    s = tech.get(f"/api/tech/sessions/{s['session_id']}").json()
    f = {x["key"]: x["text"] for x in s["report"]["fields"]}
    assert (
        s["step"]["kind"] == "report"
        and f["cause"] == "원인 미상"
        and "주간 숙련자 배정 · 주간 조 숙련자" in f["unresolved"]
    )


def test_lead_handover_direct_answer(api, db):
    """AC-23-C4 · 결정 018 ③ ④: 숙련자 인계 → 파트장 '직접 확인' + 처리 메모 → 보고서에 처리 결과."""
    reset_ops(db)
    with db.begin() as c:
        c.execute(text("update ops.grade_table set grade = 'A' where section_id = '4.4'"))
    tech, s = start(api, db)
    s = to_instruct(tech, s)
    s = run_until(tech, s, {"handover"}, lambda sec: "확인 불가" if sec in {"4.3", "4.4"} else "정상")
    s = ok(tech, s, type="call_send")
    assert (s["step"]["kind"], s["step"]["call_status"]) == ("handover", "sent")  # 답 대기
    lc = lead(api)
    cid = lc.get("/api/lead/calls").json()["rows"][0]["call_id"]
    note = "팬 축 직접 확인, 베어링 교체 필요"
    assert lc.post(f"/api/lead/calls/{cid}/answer", json={"answer": "direct", "note": note}).status_code == 200
    s = tech.get(f"/api/tech/sessions/{s['session_id']}").json()
    f = {x["key"]: x["text"] for x in s["report"]["fields"]}
    assert (
        s["step"]["kind"] == "report" and f["cause"] == "원인 미상" and f"파트장 직접 확인 · {note}" in f["unresolved"]
    )


def test_lead_grade_change(api, db):
    """AC-25 · R13 · 결정 018 ②: 등급표 전부 · 경고 확인해야 저장 · 기록 · 다음 판정부터 · 열린 지시는 그대로."""
    reset_ops(db)
    lc = lead(api)
    g = lc.get("/api/lead/grades").json()
    with db.connect() as c:
        n = c.execute(text("select count(*) from ops.grade_table")).scalar()
    assert g["total"] == n == len(g["rows"]) and g["changes"] == []
    secs = [r["section"] for r in g["rows"]]
    assert secs == sorted(secs, key=lambda s: [int(x) for x in s.split(".")])
    tech, s = start(api, db)
    s = to_instruct(tech, s)
    assert s["instruction"]["section"] == "4.3"
    w = lc.get("/api/lead/grades/4.3/warning", params={"grade": "C"}).json()
    assert w["direction"] == "raise" and w["head"] == "등급을 올리려 합니다 · 4.3 흡기 필터 육안 점검 A → C"
    assert lc.get("/api/lead/grades/4.6/warning", params={"grade": "A"}).status_code == 422  # 같은 등급
    r = lc.post("/api/lead/grades/4.3", json={"grade": "C"})
    assert r.status_code == 409 and r.json()["detail"] == "warning_not_confirmed"  # AC-25-C3
    assert lc.post("/api/lead/grades/4.3", json={"grade": "C", "confirmed": True}).status_code == 200
    assert lc.post("/api/lead/grades/4.6", json={"grade": "C", "confirmed": True}).status_code == 200
    ch = lc.get("/api/lead/grades").json()["changes"]
    assert {(x["section"], x["before"], x["after"]) for x in ch} == {("4.3", "A", "C"), ("4.6", "A", "C")} and ch[0][
        "by_name"
    ]
    s = tech.get(f"/api/tech/sessions/{s['session_id']}").json()
    assert s["step"]["kind"] == "instruct" and s["instruction"]["section"] == "4.3"  # AC-25-C4: 열린 지시 그대로
    s = ok(tech, s, type="result", section="4.3", value="정상")
    assert s["step"].get("section") != "4.6" and (s.get("instruction") or {}).get("section") != "4.6"  # AC-25-C1
    w = lc.get("/api/lead/grades/4.3/warning", params={"grade": "A"}).json()
    assert w["direction"] == "lower" and "C → A" in w["head"]
    w = lc.get("/api/lead/grades/4.6/warning", params={"grade": "D"}).json()  # AC-25-C3: D도 경고 · 확인
    assert w["direction"] == "raise" and "C → D" in w["head"] and w["body"]
    assert lc.post("/api/lead/grades/4.6", json={"grade": "D"}).status_code == 409
    assert lc.post("/api/lead/grades/4.6", json={"grade": "D", "confirmed": True}).status_code == 200


def test_lead_grade_change_keeps_open_call(api, db):
    """AC-25-C4: 이미 열린 호출 화면(C 점검 호출 요약)은 그 절 등급을 낮춰도 바뀌지 않는다."""
    reset_ops(db)
    tech, s = start(api, db)
    s = run_until(tech, to_instruct(tech, s), {"call"}, lambda sec: "정상")
    before = (s["step"], s["call"])
    lc = lead(api)
    sec = s["call"]["section"]
    assert lc.post(f"/api/lead/grades/{sec}", json={"grade": "A", "confirmed": True}).status_code == 200
    s = tech.get(f"/api/tech/sessions/{s['session_id']}").json()
    assert (s["step"], s["call"]) == before


def test_lead_audit_and_filters(api, db):
    """AC-26-C1 · C2 · L06: 시간 역순 · 행동 문구 · 시스템 지시 행 · 설비 · 사용자 · 기간 필터."""
    reset_ops(db)
    tech, s, rid = confirmed_report(api, db)
    tech2, s2 = start(api, db, equipment="M-03")
    lc = lead(api)
    assert lc.post(f"/api/lead/reports/{rid}/decision", json={"decision": "approve"}).status_code == 200
    a = lc.get("/api/lead/audit").json()
    acts = [r["action"] for r in a["rows"]]
    assert acts[0] == "보고서 승인" and "보고서 확정" in acts and "조치 완료 · 4.3.2" in acts
    assert "재가동 확인 · 경계 이내" in acts and "결과 입력 · 4.3 이상" in acts and "잠금 완료 · 1.2" in acts
    sysrow = next(r for r in a["rows"] if r["action"].startswith("지시 · 4.3"))
    assert sysrow["user_name"] == "시스템" and sysrow["app"] == "system" and sysrow["target"] == "M-01 세션"
    assert [r["at"] for r in a["rows"]] == sorted((r["at"] for r in a["rows"]), reverse=True)
    f = lc.get("/api/lead/audit", params={"equipment": "M-03"}).json()["rows"]
    assert f and all(r["equipment_id"] == "M-03" for r in f)
    u = lc.get("/api/lead/audit", params={"user_id": "lead.park"}).json()["rows"]
    assert u and all(r["user_id"] == "lead.park" and r["app"] == "파트장" for r in u)
    assert lc.get("/api/lead/audit", params={"date": "2020-01-01"}).json()["rows"] == []
    assert "M-01" in a["options"]["equipment"] and any(x["user_id"] == "tech.kim" for x in a["options"]["users"])
    reg = next(r for r in a["rows"] if r["action"].startswith("알람 등록"))  # 시스템 행: 알람 등록 · 배정
    assert (
        reg["user_name"] == "시스템"
        and reg["app"] == "system"
        and reg["target"].endswith(" 알람")
        and "배정 " in reg["action"]
    )
    assert all(r["target"].startswith(f"{r['equipment_id']} ") for r in f)


def test_call_required_audit_once_per_call_step(api, db):
    """결정 020 ④(앞 slice 결함 수리): '호출 필요' 감사 행은 호출 단계를 처음 열 때만 — 보냄 · 대기 뒤 다시 열린 단계는 새 행이 아님.

    틀리면 실패: 호출을 보낸 뒤 '호출 필요'가 한 번 더 남거나(S-03 · S-04 동작), 두 번째 호출(다른 절)의 행이 빠지면."""
    reset_ops(db)
    lc = lead(api)
    tech, s = start(api, db)
    s = run_until(tech, to_instruct(tech, s), {"call"}, lambda sec: "정상")
    first = s["step"]["section"]

    def call_rows():
        with db.connect() as c:
            return [
                d["section"]
                for (d,) in c.execute(
                    text(
                        "select detail from ops.audit_log where action = 'call_required' and target = :t order by audit_id"
                    ),
                    {"t": f"session:{s['session_id']}"},
                )
            ]

    assert call_rows() == [first]
    s = ok(tech, s, type="call_send")
    assert s["step"]["call_status"] == "sent" and call_rows() == [first]  # 보낸 뒤 다시 열린 호출 단계는 새 행 아님
    cid = lc.get("/api/lead/calls").json()["rows"][0]["call_id"]
    assert lc.post(f"/api/lead/calls/{cid}/answer", json={"answer": "approved"}).status_code == 200
    s = tech.get(f"/api/tech/sessions/{s['session_id']}").json()
    s = ok(tech, s, type="result", section=first, value="이상")  # 승인된 C 점검 이상 → 조치도 C면 두 번째 호출
    assert s["step"]["kind"] == "call" and s["step"]["section"] != first
    second = s["step"]["section"]
    assert call_rows() == [first, second]
    s = ok(tech, s, type="call_wait")  # 호출하지 않고 대기도 새 행 아님
    assert call_rows() == [first, second]
    acts = [r["action"] for r in lc.get("/api/lead/audit").json()["rows"] if r["action"].startswith("호출 필요")]
    assert len(acts) == 2  # L06 화면 행도 같음


def test_second_call_view_is_not_previous_answer(api, db):
    """앞 slice 결함 수리(S-06 G5 시연 E2E에서 발견): 승인 답 뒤 같은 세션에 새 호출 단계(다른 절)가 열리면
    호출 화면 값은 그 새 호출 — 보냄 전(status none · 답 없음 · 새 요약), 보낸 뒤 답도 그 호출 것만.

    틀리면 실패: 새 호출 단계에 앞 호출의 '승인 후 진행' 답 · 보냄 상태가 붙어 정비자 화면에 '파트장 호출' 버튼이 없음."""
    reset_ops(db)
    lc = lead(api)
    tech, s = start(api, db)
    s = run_until(tech, to_instruct(tech, s), {"call"}, lambda sec: "정상")
    first = s["step"]["section"]
    s = ok(tech, s, type="call_send")
    cid = lc.get("/api/lead/calls").json()["rows"][0]["call_id"]
    assert lc.post(f"/api/lead/calls/{cid}/answer", json={"answer": "approved"}).status_code == 200
    s = tech.get(f"/api/tech/sessions/{s['session_id']}").json()
    s = ok(tech, s, type="result", section=first, value="이상")
    second = s["step"]["section"]
    assert s["step"]["kind"] == "call" and second != first
    c = s["call"]
    assert (c["section"], c["status"], c["answer"]) == (second, "none", None)  # 새 호출 — 앞 답 아님
    assert second in c["summary"]["text"]  # 요약도 새 호출(그 절) 것
    s = ok(tech, s, type="call_send")
    assert (s["call"]["section"], s["call"]["status"], s["call"]["answer"]) == (second, "sent", None)
    cid2 = next(x["call_id"] for x in lc.get("/api/lead/calls").json()["rows"])
    assert cid2 != cid and lc.post(f"/api/lead/calls/{cid2}/answer", json={"answer": "approved"}).status_code == 200
    s = tech.get(f"/api/tech/sessions/{s['session_id']}").json()
    assert s["step"]["kind"] in {"action", "action_after_checklist"} and s["call"]["answer"]["answer"] == "approved"


def test_lead_audit_records_review_call_and_grade(api, db):
    """AC-26-C1: 반려 · 호출 · 호출 답 · 등급 변경도 감사 행으로 남고 L06 문구로 읽힌다."""
    reset_ops(db)
    _, s, rid = confirmed_report(api, db)
    lc = lead(api)
    assert (
        lc.post(f"/api/lead/reports/{rid}/decision", json={"decision": "reject", "memo": "다시 확인"}).status_code
        == 200
    )
    tech2, s2 = start(api, db, equipment="M-03")
    s2 = run_until(tech2, to_instruct(tech2, s2), {"call"}, lambda sec: "정상")
    s2 = ok(tech2, s2, type="call_send")
    cid = lc.get("/api/lead/calls").json()["rows"][0]["call_id"]
    assert lc.post(f"/api/lead/calls/{cid}/answer", json={"answer": "daytime"}).status_code == 200
    assert lc.post("/api/lead/grades/4.6", json={"grade": "C", "confirmed": True}).status_code == 200
    rows = lc.get("/api/lead/audit").json()["rows"]
    acts = [r["action"] for r in rows]
    assert "보고서 반려" in acts and "호출 답 · 주간 처리" in acts
    assert any(x.startswith("파트장 호출 · ") for x in acts) and any(x.startswith("지시 · ") for x in acts)
    g = next(r for r in rows if r["action"].startswith("등급 변경 · 4.6"))
    assert g["action"].endswith("A → C") and g["user_id"] == "lead.park" and g["target"] == "권한 등급"
    # 확인 질문 답(AC-05): '정상' 버튼 + 이상 뜻 메모 → 확인 질문 → '아니요'
    tech3, s3 = start(api, db, equipment="M-02")
    s3 = to_instruct(tech3, s3)
    sec = s3["instruction"]["section"]
    s3 = ok(tech3, s3, type="result", section=sec, value="정상", memo="기름때가 표면 절반 넘게 덮음")
    assert s3["step"]["kind"] == "confirm_question"
    ok(tech3, s3, type="confirm_answer", yes=False)
    acts = [r["action"] for r in lc.get("/api/lead/audit").json()["rows"]]
    assert "확인 질문 답 · 아니요" in acts
    # 기간 필터: 고른 날짜(KST)의 행만, 기본값은 오늘
    from c1a15.api import screen

    today = datetime.now(screen.KST).date()
    d = lc.get("/api/lead/audit", params={"date": today.isoformat()}).json()
    assert d["date"] == today.isoformat() and [r["audit_id"] for r in d["rows"]] == [
        r["audit_id"] for r in lc.get("/api/lead/audit").json()["rows"]
    ]
    assert d["rows"] and all(datetime.fromisoformat(r["at"]).astimezone(screen.KST).date() == today for r in d["rows"])
    prev = (today - timedelta(days=1)).isoformat()
    assert all(
        datetime.fromisoformat(r["at"]).astimezone(screen.KST).date().isoformat() == prev
        for r in lc.get("/api/lead/audit", params={"date": prev}).json()["rows"]
    )


def test_tech_cannot_send_lead_records_and_rejections_audited(api, db):
    """S-03 G6 2차 의견: 정비자가 call_answer · report_rejected를 보내면 422, 확정 뒤 입력 · 체크리스트 부족 거부도 감사."""
    reset_ops(db)
    tech, s, rid = confirmed_report(api, db)
    assert ev(tech, s, type="call_answer").status_code == 422
    assert ev(tech, s, type="report_rejected").status_code == 422
    assert ev(tech, s, type="report_edit", field="cause", text="x").status_code == 409  # session_closed
    tech2, s2 = start(api, db, equipment="M-03")
    with db.begin() as c:
        c.execute(text("update ops.grade_table set grade = 'B' where section_id = '4.3'"))
    s2 = ok(tech2, s2, type="lock")
    s2 = ok(tech2, s2, type="precheck_done")
    assert s2["step"]["kind"] == "instruct_after_checklist"
    assert ev(tech2, s2, type="b_checklist_done", section="4.3", checked=["x"]).status_code == 409
    with db.connect() as c:
        reasons = {r for (r,) in c.execute(text("select detail->>'reason' from ops.audit_log where action = 'reject'"))}
    assert {"session_closed", "checklist_incomplete"} <= reasons
    with db.begin() as c:
        c.execute(
            text(
                "update ops.grade_table g set grade = s.initial_grade from knowledge.manual_sections s where s.section_id = g.section_id"
            )
        )
    _ = register


def test_ac06_report_sentences_never_ungrounded(api, db, monkeypatch):
    """AC-06 L2(P-11 완료): 가짜 provider가 근거 없는 보고서 문장을 내도 초안 · 확정 · 승인 보고서에 남지 않는다(템플릿 대체),
    파트장 수정 문장도 다시 검사해 근거 없으면 승인되지 않는다."""
    from c1a15.api import flow
    from c1a15.llm.base import Draft

    class Ungrounded:
        mode = "x"

        def write(self, facts):
            if facts.kind == "report_sentence":
                return Draft("교체 후 온도 차 12.3 K로 회복, 5.9절 기준 통과")
            return Draft(facts.values.get("template", ""))

    reset_ops(db)
    monkeypatch.setattr(flow, "adapter_for_mode", lambda: Ungrounded())
    _, s, rid = confirmed_report(api, db)
    f = {x["key"]: x["text"] for x in s["report"]["fields"]}
    assert "12.3" not in f["action"] + f["cause"] and "5.9" not in f["action"]  # AC-06-C2: 템플릿 문장으로 대체
    assert f["cause"] == "냉각 필터 막힘" and f["action"].startswith("흡기 필터 교체(4.3.2, A)")
    lc = lead(api)
    bad = {"action": f["action"] + " · 교체 후 온도 차 12.3 K로 회복"}
    assert not lc.post(f"/api/lead/reports/{rid}/check", json={"edits": bad}).json()["ok"]
    assert lc.post(f"/api/lead/reports/{rid}/decision", json={"decision": "edit", "edits": bad}).status_code == 409
    assert lc.post(f"/api/lead/reports/{rid}/decision", json={"decision": "approve"}).status_code == 200
    with db.connect() as c:
        rec = c.execute(
            text("select record from knowledge.history_records where record_id = :i"), {"i": f"R-{rid:04d}"}
        ).scalar()
    assert "12.3" not in rec["narrative"] and "12.3" not in rec["action"]
