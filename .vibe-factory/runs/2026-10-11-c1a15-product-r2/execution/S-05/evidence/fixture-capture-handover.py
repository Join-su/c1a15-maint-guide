"""capture.py의 앞부분(초기화 · 로그인 · 도우미)을 그대로 두고 숙련자 인계 답 대기 중 정정 세션의 지난 화면만 받는다(G6-S05 비차단 ③)."""
import json, os, subprocess, sys, urllib.request, urllib.error, http.cookiejar
OUT_T, OUT_L = sys.argv[1], sys.argv[2]
for d in (OUT_T, OUT_L): os.makedirs(d, exist_ok=True)
ROOT = "/Users/insujo/Documents/repo/c1a15-maint-guide"
def client(base):
    cj = http.cookiejar.CookieJar(); op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    def call(method, path, body=None, ok=True):
        req = urllib.request.Request(base + path, method=method, data=json.dumps(body).encode() if body is not None else None, headers={"Content-Type": "application/json"})
        try:
            with op.open(req) as r: return json.loads(r.read())
        except urllib.error.HTTPError as e:
            if ok: raise RuntimeError(f"{method} {path} -> {e.code}")
            return {"_status": e.code, **json.loads(e.read())}
    return call
T, L = client("http://127.0.0.1:8081"), client("http://127.0.0.1:8082")
def save(d, name, obj): json.dump(obj, open(f"{d}/{name}.json", "w"), ensure_ascii=False, indent=1)
def dc(*a): return subprocess.run(["docker", "compose", *a], cwd=ROOT, check=True, capture_output=True, text=True).stdout
def psql(sql): dc("exec", "-T", "db", "psql", "-U", "c1a15", "-d", "c1a15", "-c", sql)
def alarm(sid): return int(dc("exec", "-T", "api", "python", "-m", "c1a15.alarms", sid).split()[2])
def ev(s, **body): return T("POST", f"/api/tech/sessions/{s['session_id']}/events", {"seq": s["last_seq"] + 1, **body})
def get(s): return T("GET", f"/api/tech/sessions/{s['session_id']}")
def hist(s): return T("GET", f"/api/tech/sessions/{s['session_id']}/history")
def fix(s, ok=True, **body): return T("POST", f"/api/tech/sessions/{s['session_id']}/corrections", body, ok=ok)
def note(s, **body): return T("POST", f"/api/tech/sessions/{s['session_id']}/notes", body)
def seq(s, section):
    return next(r["seq"] for r in reversed(get(s)["results"]) if r["section"] == section)
def rec_seq(s, kind):
    return next(r["seq"] for st in hist(s)["steps"] for r in st["records"] if r["kind"] == kind)
GR = "update ops.grade_table g set grade = s.initial_grade from knowledge.manual_sections s where s.section_id = g.section_id"
psql("delete from ops.audit_log; delete from ops.calls; delete from ops.reports; delete from ops.grade_changes; delete from ops.session_events; delete from ops.diag_sessions; delete from ops.alarms; delete from knowledge.history_embeddings where record_id like 'R-%'; delete from knowledge.history_records where record_id like 'R-%'; " + GR)
T("POST", "/api/login", {"user_id": "tech.kim", "password": os.environ["C1A15_TECH_PASSWORD"]})
L("POST", "/api/login", {"user_id": "lead.park", "password": os.environ["C1A15_LEAD_PASSWORD"]})
def start(demo, values="하우징 표면 52 °C · 공기 302.7 K · 공정 310.5 K"):
    s = T("POST", f"/api/tech/alarms/{alarm(demo)}/session"); s = ev(s, type="lock"); return ev(s, type="precheck_done", values=values)
psql("update ops.grade_table set grade = 'A' where section_id = '4.4'")
s4 = start("DEMO-05")
for _ in range(10):
    if s4["step"]["kind"] == "handover": break
    sec = s4["instruction"]["section"]; s4 = ev(s4, type="result", section=sec, value="확인 불가" if sec in {"4.3", "4.4"} else "정상")
s4 = ev(s4, type="call_send"); psql(GR)
s4 = fix(s4, target_seq=seq(s4, "4.6"), value="이상", reason="설정값을 다시 읽음")
save(OUT_T, "s05-history-handover", hist(s4))
print("saved s05-history-handover")
