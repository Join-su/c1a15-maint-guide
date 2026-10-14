"""dev 스택(정비자 8081 · 파트장 8082)에서 S-04 상태별 실제 API 응답을 받아 component 시험 fixture로 저장한다.
파트장 답 · 반려는 실제 파트장 API로 만든다(S-03의 시험 DB 시뮬레이션을 쓰지 않음)."""
import json, os, subprocess, sys, urllib.request, urllib.error, http.cookiejar
OUT_T, OUT_L = sys.argv[1], sys.argv[2]
for d in (OUT_T, OUT_L): os.makedirs(d, exist_ok=True)
ROOT = "/Users/insujo/Documents/repo/c1a15-maint-guide"
def client(base):
    cj = http.cookiejar.CookieJar(); op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    def call(method, path, body=None, ok=True, query=None):
        url = base + path + ("?" + "&".join(f"{k}={v}" for k, v in query.items()) if query else "")
        req = urllib.request.Request(url, method=method, data=json.dumps(body).encode() if body is not None else None, headers={"Content-Type": "application/json"})
        try:
            with op.open(req) as r: return json.loads(r.read())
        except urllib.error.HTTPError as e:
            if ok: raise RuntimeError(f"{method} {path} {body} -> {e.code} {e.read()[:300]}")
            return {"_status": e.code, **json.loads(e.read())}
    return call
T, L = client("http://127.0.0.1:8081"), client("http://127.0.0.1:8082")
def save(d, name, obj): json.dump(obj, open(f"{d}/{name}.json", "w"), ensure_ascii=False, indent=1)
def dc(*a): return subprocess.run(["docker", "compose", *a], cwd=ROOT, check=True, capture_output=True, text=True).stdout
def psql(sql): dc("exec", "-T", "db", "psql", "-U", "c1a15", "-d", "c1a15", "-c", sql)
def alarm(sid): return int(dc("exec", "-T", "api", "python", "-m", "c1a15.alarms", sid).split()[2])
def ev(s, **body): return T("POST", f"/api/tech/sessions/{s['session_id']}/events", {"seq": s["last_seq"] + 1, **body})
def get(s): return T("GET", f"/api/tech/sessions/{s['session_id']}")
GR = "update ops.grade_table g set grade = s.initial_grade from knowledge.manual_sections s where s.section_id = g.section_id"
psql("delete from ops.audit_log; delete from ops.calls; delete from ops.reports; delete from ops.grade_changes; delete from ops.session_events; delete from ops.diag_sessions; delete from ops.alarms; delete from knowledge.history_embeddings where record_id like 'R-%'; delete from knowledge.history_records where record_id like 'R-%'; " + GR)
T("POST", "/api/login", {"user_id": "tech.kim", "password": os.environ["C1A15_TECH_PASSWORD"]})
L("POST", "/api/login", {"user_id": "lead.park", "password": os.environ["C1A15_LEAD_PASSWORD"]})
save(OUT_L, "overview-empty", L("GET", "/api/lead/overview")); save(OUT_L, "calls-empty", L("GET", "/api/lead/calls"))
def start(demo):
    s = T("POST", f"/api/tech/alarms/{alarm(demo)}/session"); s = ev(s, type="lock"); return ev(s, type="precheck_done")
def run(s, stop, choose):
    for _ in range(12):
        if s["step"]["kind"] in stop: return s
        sec = s["instruction"]["section"]; s = ev(s, type="result", section=sec, value=choose(sec))
    raise RuntimeError(s["step"])
def confirm(demo, memo="기름때가 필터 표면 절반 넘게 덮음"):
    s = start(demo); s = ev(s, type="result", section="4.3", value="이상", memo=memo)
    s = ev(s, type="action_done", section=s["action"]["section"]); s = ev(s, type="restart", checked=s["restart"]["checklist"])
    s = ev(s, type="restart_result", outcome="within"); return ev(s, type="report_confirm")
# 승인 대기 3건(하나는 근거 적음) + 호출 2건(파트장 호출 · 숙련자 인계)
r1 = confirm("DEMO-01"); r2 = confirm("DEMO-02")
s3 = start("DEMO-03"); s3 = ev(s3, type="result", section="4.3", value="이상", memo="기름때"); s3 = ev(s3, type="action_done", section=s3["action"]["section"])
s3 = ev(s3, type="restart", checked=s3["restart"]["checklist"]); s3 = ev(s3, type="restart_result", outcome="within")
psql(f"""update ops.diag_sessions set "similar" = (select jsonb_agg(jsonb_set(e, '{{score}}', to_jsonb(case when i <= 2 then 0.9 else 0.3 end))) from jsonb_array_elements("similar") with ordinality as t(e, i)) where session_id = {s3['session_id']}""")
s3 = ev(get(s3), type="report_confirm")
c1 = start("DEMO-04"); c1 = run(c1, {"call"}, lambda sec: "정상"); c1 = ev(c1, type="call_send")
psql("update ops.grade_table set grade = 'A' where section_id = '4.4'")
h1 = start("DEMO-05"); h1 = run(h1, {"handover"}, lambda sec: "확인 불가" if sec in {"4.3", "4.4"} else "정상"); h1 = ev(h1, type="call_send")
psql(GR)
save(OUT_T, "s04-handover-sent", get(h1))
ov = L("GET", "/api/lead/overview"); save(OUT_L, "overview-list", ov)
rid = next(r["report_id"] for r in ov["rows"] if r["session_id"] == r1["session_id"])
save(OUT_L, "report-review", L("GET", f"/api/lead/reports/{rid}"))
f = {x["key"]: x["text"] for x in L("GET", f"/api/lead/reports/{rid}")["fields"]}
save(OUT_L, "check-failed", L("POST", f"/api/lead/reports/{rid}/check", {"edits": {"unresolved": f["unresolved"] + " · 팬 회전수 1,850 rpm으로 정상 확인"}}))
save(OUT_L, "check-ok", L("POST", f"/api/lead/reports/{rid}/check", {"edits": {"unresolved": "냉각 팬 상태(4.4, C) · 주간 조 확인 배정"}}))
cl = L("GET", "/api/lead/calls"); save(OUT_L, "calls-list", cl)
cid = next(x["call_id"] for x in cl["rows"] if x["kind"] == "approval"); hid = next(x["call_id"] for x in cl["rows"] if x["kind"] == "handover")
save(OUT_L, "call-detail", L("GET", f"/api/lead/calls/{cid}")); save(OUT_L, "handover-detail", L("GET", f"/api/lead/calls/{hid}"))
save(OUT_L, "grades-default", L("GET", "/api/lead/grades"))
save(OUT_L, "warning-raise", L("GET", "/api/lead/grades/4.3/warning", query={"grade": "C"}))
save(OUT_L, "warning-lower", L("GET", "/api/lead/grades/4.4/warning", query={"grade": "B"}))
# 답 · 결정
L("POST", f"/api/lead/calls/{cid}/answer", {"answer": "direct", "note": "팬 베어링 소음 확인, 주간 교체 예정"})
save(OUT_T, "s04-ans-direct", get(c1))
L("POST", f"/api/lead/calls/{hid}/answer", {"answer": "assign", "note": "주간 조 숙련자 배정"})
save(OUT_T, "s04-handover-answered", get(h1))
L("POST", f"/api/lead/reports/{rid}/decision", {"decision": "reject", "memo": "필터 표면 상태를 메모로 다시 적어 주세요"})
rid2 = next(r["report_id"] for r in ov["rows"] if r["session_id"] == r2["session_id"])
L("POST", f"/api/lead/reports/{rid2}/decision", {"decision": "approve"})
save(OUT_T, "home-rejected", T("GET", "/api/tech/home")); save(OUT_T, "notifications-rejected", T("GET", "/api/tech/notifications"))
save(OUT_T, "s04-report-reopened", get(r1))
L("POST", "/api/lead/grades/4.3", {"grade": "C", "confirmed": True}); L("POST", "/api/lead/grades/4.3", {"grade": "A", "confirmed": True})
save(OUT_L, "grades-changed", L("GET", "/api/lead/grades"))
save(OUT_L, "audit-default", L("GET", "/api/lead/audit"))
save(OUT_L, "audit-filtered", L("GET", "/api/lead/audit", query={"equipment": "M-01", "user_id": "tech.kim"}))
# D 등급 호출 상세(파생 L04 / call_detail_d)
psql("update ops.grade_table set grade = 'D' where section_id = '4.4'")
d1 = start("DEMO-01"); d1 = run(d1, {"call"}, lambda sec: "정상"); d1 = ev(d1, type="call_send")
did = next(x["call_id"] for x in L("GET", "/api/lead/calls")["rows"] if x["kind"] == "approval")
save(OUT_L, "call-detail-d", L("GET", f"/api/lead/calls/{did}"))
psql(GR)
print("saved", sorted(os.listdir(OUT_L)), sorted(x for x in os.listdir(OUT_T) if x.startswith(("s04", "home-rej", "notifications-rej"))))
