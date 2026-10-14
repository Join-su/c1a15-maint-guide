"""dev 스택(8081)에서 S-03 상태별 실제 API 응답을 받아 component 시험 fixture로 저장한다."""
import json, os, subprocess, sys, urllib.request, urllib.error, http.cookiejar
OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
B = "http://127.0.0.1:8081"; ROOT = "/Users/insujo/Documents/repo/c1a15-maint-guide"
cj = http.cookiejar.CookieJar(); op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
def call(method, path, body=None, ok=True):
    req = urllib.request.Request(B + path, method=method, data=json.dumps(body).encode() if body is not None else None, headers={"Content-Type": "application/json"})
    try:
        with op.open(req) as r: return json.loads(r.read())
    except urllib.error.HTTPError as e:
        if ok: raise RuntimeError(f"{method} {path} {body} -> {e.code} {e.read()[:300]}")
        return {"_status": e.code, **json.loads(e.read())}
def save(name, obj): json.dump(obj, open(f"{OUT}/{name}.json", "w"), ensure_ascii=False, indent=1)
def dc(*a, inp=None): return subprocess.run(["docker", "compose", *a], cwd=ROOT, check=True, capture_output=True, text=True, input=inp).stdout
def psql(sql): dc("exec", "-T", "db", "psql", "-U", "c1a15", "-d", "c1a15", "-c", sql)
def alarm(sid): return int(dc("exec", "-T", "api", "python", "-m", "c1a15.alarms", sid).split()[2])
def answer(sid, a): dc("exec", "-T", "api", "python", "-", str(sid), a, inp=open(f"{ROOT}/e2e/sim_lead_answer.py").read())
def ev(s, **body): return call("POST", f"/api/tech/sessions/{s['session_id']}/events", {"seq": s["last_seq"] + 1, **body})
def get(s): return call("GET", f"/api/tech/sessions/{s['session_id']}")
GR = "update ops.grade_table g set grade = s.initial_grade from knowledge.manual_sections s where s.section_id = g.section_id"
psql("delete from ops.audit_log; delete from ops.calls; delete from ops.reports; delete from ops.session_events; delete from ops.diag_sessions; delete from ops.alarms; " + GR)
call("POST", "/api/login", {"user_id": "tech.kim", "password": os.environ["C1A15_TECH_PASSWORD"]})
def start(demo):
    s = call("POST", f"/api/tech/alarms/{alarm(demo)}/session")
    s = ev(s, type="lock"); return ev(s, type="precheck_done")
def run(s, stop, choose):
    for _ in range(12):
        if s["step"]["kind"] in stop: return s
        sec = s["instruction"]["section"]; s = ev(s, type="result", section=sec, value=choose(sec))
    raise RuntimeError(s["step"])
# 1. A 조치 → 재가동 → 값 → 보고서 → 실패 → 확정
s = start("DEMO-01"); assert s["instruction"]["section"] == "4.3", s["step"]
s = ev(s, type="result", section="4.3", value="이상", memo="기름때가 필터 표면 절반 넘게 덮음"); save("s03-action-a", s)
s = ev(s, type="action_done", section=s["action"]["section"]); save("s03-restart-check", s)
s = ev(s, type="restart", checked=s["restart"]["checklist"]); save("s03-restart-value", s)
s = ev(s, type="restart_result", outcome="within"); save("s03-report-draft", s)
act = next(f for f in s["report"]["fields"] if f["key"] == "action")["text"]
s = ev(s, type="report_edit", field="action", text=act + " · 교체 후 온도 차 9.4 K로 회복"); save("s03-report-failed", s)
s = ev(s, type="report_edit", field="action", text=act)
s = ev(s, type="report_confirm"); save("s03-report-confirmed", s)
save("home-done", call("GET", "/api/tech/home"))
# 2. B 조치(4.5.2 B): 4.3 정상 → 4.6 정상? 순서대로 진행하다 4.5 이상
psql("update ops.grade_table set grade = 'B' where section_id = '4.3.2'")
s = start("DEMO-02"); s = ev(s, type="result", section="4.3", value="이상", memo="기름때"); save("s03-action-b", s)
psql(GR)
# 3. 호출: 모두 정상 → 호출 요약 → 대기 → 보냄 → 승인
s = start("DEMO-03"); s = run(s, {"call"}, lambda sec: "정상"); save("s03-call-summary", s)
s = ev(s, type="call_wait"); save("s03-call-waiting", s)
s = ev(s, type="call_send"); save("s03-call-sent", s)
answer(s["session_id"], "approved"); save("s03-ans-approved", get(s))
save("notifications-answered", call("GET", "/api/tech/notifications"))
s = start("DEMO-04"); s = run(s, {"call"}, lambda sec: "정상"); s = ev(s, type="call_send")
answer(s["session_id"], "daytime"); s = get(s); save("s03-ans-daytime", s); save("s03-report-daytime", s)
s = start("DEMO-05"); s = run(s, {"call"}, lambda sec: "정상"); s = ev(s, type="call_send")
answer(s["session_id"], "direct"); save("s03-ans-direct", get(s))
# 4. 인계: 확인 불가 반복(4.4 = A), 맞지 않는 소견, 재가동 뒤 밖
psql("update ops.grade_table set grade = 'A' where section_id = '4.4'")
s = start("DEMO-01"); s = run(s, {"handover"}, lambda sec: "확인 불가" if sec in {"4.3", "4.4"} else "정상"); save("s03-handover-unable", s)
# 5. 감시 마감(4.4 = A, 모두 정상)
s = start("DEMO-02"); s = run(s, {"restart_check"}, lambda sec: "정상"); save("s03-restart-monitor", s)
s = ev(s, type="restart", checked=s["restart"]["checklist"]); s = ev(s, type="restart_result", outcome="within"); save("s03-monitor-close", s)
s = ev(s, type="monitor_close"); save("s03-monitor-report", s)
psql(GR)
s = start("DEMO-03"); s = ev(s, type="result", section=s["instruction"]["section"], value="정상", memo="바닥에서 타는 냄새")
s = ev(s, type="out_of_scope_choice", choice="handover"); save("s03-handover-oos", s)
s = ev(s, type="call_send"); save("s03-report-unknown", s)
s = start("DEMO-04"); s = ev(s, type="result", section="4.3", value="이상", memo="기름때")
s = ev(s, type="action_done", section=s["action"]["section"]); s = ev(s, type="restart", checked=s["restart"]["checklist"])
s = ev(s, type="restart_result", outcome="outside"); save("s03-handover-restart", s)
# 6. 근거 적음 보고서: 그 세션의 상위 기록 score를 낮춰 시뮬레이션(score ≥ 0.5가 3건 미만, S-02 T04 / low_evidence와 같은 방식)
s = start("DEMO-05"); s = ev(s, type="result", section="4.3", value="이상", memo="기름때")
s = ev(s, type="action_done", section=s["action"]["section"]); s = ev(s, type="restart", checked=s["restart"]["checklist"])
s = ev(s, type="restart_result", outcome="within")
psql(f"""update ops.diag_sessions set "similar" = (select jsonb_agg(jsonb_set(e, '{{score}}', to_jsonb(case when i <= 2 then 0.9 else 0.3 end))) from jsonb_array_elements("similar") with ordinality as t(e, i)) where session_id = {s['session_id']}""")
save("s03-report-low-evidence", get(s))
print("saved", sorted(x for x in os.listdir(OUT) if x.startswith(("s03", "home-done", "notifications-answered"))))
