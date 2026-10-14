"""dev 스택(정비자 8081 · 파트장 8082)에서 S-05 상태별 실제 API 응답을 받아 component 시험 fixture로 저장한다.
정정 · 메모 덧붙이기 · 파트장 답은 실제 API로 만든다(시험 DB 시뮬레이션 없음)."""
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
# 1 열린 지시 · 지난 화면(알람 · 진단 · 잠금 · 사전 확인 · 점검) → 확인 필요 → 다시 판정
s1 = start("DEMO-01")
s1 = ev(s1, type="result", section="4.3", value="정상", memo="필터 깨끗함")
save(OUT_T, "s05-session-open", get(s1)); save(OUT_T, "s05-history-open", hist(s1))
save(OUT_T, "s05-confirm-required", fix(s1, ok=False, target_seq=seq(s1, "4.3"), value="이상", memo="필터 뒷면에 기름때가 절반 넘게 덮음", reason="필터 뒷면 기름때를 못 보고 정상으로 눌렀음"))
s1 = fix(s1, target_seq=seq(s1, "4.3"), value="이상", memo="필터 뒷면에 기름때가 절반 넘게 덮음", reason="필터 뒷면 기름때를 못 보고 정상으로 눌렀음", confirmed=True)
s1 = note(s1, target_seq=rec_seq(s1, "lock"), memo="잠금 표지 2번 패널에 추가로 걺")
save(OUT_T, "s05-session-rejudged", get(s1)); save(OUT_T, "s05-history-corrected", hist(s1))
# 조치 · 재가동 · 확정 세션
s1 = ev(s1, type="action_done", section="4.3.2"); s1 = ev(s1, type="restart", checked=s1["restart"]["checklist"]); s1 = ev(s1, type="restart_result", outcome="within")
save(OUT_T, "s05-history-action", hist(s1))
s1 = ev(s1, type="report_confirm"); save(OUT_T, "s05-history-closed", hist(s1))
# 2 B 점검 기록(T15 / check_b)
psql("update ops.grade_table set grade = 'B' where section_id = '4.3'")
s2 = start("DEMO-02")
ins = s2["instruction"]; s2 = ev(s2, type="b_checklist_done", section="4.3", checked=ins["checklist"])
s2 = ev(s2, type="result", section="4.3", value="이상", memo="기름때가 필터 표면 절반 넘게 덮음")
psql(GR); save(OUT_T, "s05-history-b", hist(s2))
# 3 보낸 호출 뒤 정정 → 정정 상자(L04 / call_corrected), 지난 화면 호출 기록(T15 / call)
s3 = start("DEMO-03")
for _ in range(6):
    if s3["step"]["kind"] == "call": break
    s3 = ev(s3, type="result", section=s3["instruction"]["section"], value="정상")
s3 = ev(s3, type="call_send")
s3 = fix(s3, target_seq=seq(s3, "4.3"), value="이상", reason="필터 뒷면 기름때를 못 보고 정상으로 눌렀음")
save(OUT_T, "s05-history-call", hist(s3))
cid = next(x["call_id"] for x in L("GET", "/api/lead/calls")["rows"])
save(OUT_L, "call-corrected", L("GET", f"/api/lead/calls/{cid}"))
# 4 숙련자 인계 답 대기 중 정정(결정 019 ②)
psql("update ops.grade_table set grade = 'A' where section_id = '4.4'")
s4 = start("DEMO-05")
for _ in range(10):
    if s4["step"]["kind"] == "handover": break
    sec = s4["instruction"]["section"]; s4 = ev(s4, type="result", section=sec, value="확인 불가" if sec in {"4.3", "4.4"} else "정상")
s4 = ev(s4, type="call_send"); psql(GR)
s4 = fix(s4, target_seq=seq(s4, "4.6"), value="이상", reason="설정값을 다시 읽음")
hid = next(x["call_id"] for x in L("GET", "/api/lead/calls")["rows"] if x["kind"] == "handover")
save(OUT_L, "handover-corrected", L("GET", f"/api/lead/calls/{hid}"))
# 5 조치 뒤 정정 → 정정 호출(T10 / summary_corrected) → 답(주간 처리 · 직접 확인)
for demo, answer, name in (("DEMO-04", "daytime", "daytime"), ("DEMO-06", "direct", "direct")):
    s5 = start(demo)
    s5 = ev(s5, type="result", section=s5["instruction"]["section"], value="이상", memo="기름때")
    if s5["step"]["kind"] not in {"action", "action_after_checklist"}:
        raise SystemExit(f"{demo}: 첫 점검 이상 뒤 조치가 아님 {s5['step']}")
    sec_first = next(r["section"] for r in get(s5)["results"])
    s5 = ev(s5, type="action_done", section=s5["action"]["section"])
    s5 = fix(s5, target_seq=seq(s5, sec_first), value="정상", reason="다시 보니 깨끗함")
    if name == "daytime":
        save(OUT_T, "s05-session-correction-call", get(s5))
    s5 = ev(s5, type="call_send")
    cc = next(x["call_id"] for x in L("GET", "/api/lead/calls")["rows"] if x["need"].startswith("정정 확인"))
    if name == "daytime":
        save(OUT_L, "correction-call-detail", L("GET", f"/api/lead/calls/{cc}"))
    L("POST", f"/api/lead/calls/{cc}/answer", {"answer": answer, "note": "필터 재확인 · 주간 교체" if answer == "daytime" else "직접 확인, 필터 표면 양호"})
    save(OUT_T, f"s05-session-correction-ans-{name}", get(s5))
save(OUT_L, "audit-correction", L("GET", "/api/lead/audit"))
print("saved", sorted(x for x in os.listdir(OUT_T) if x.startswith("s05")), sorted(x for x in os.listdir(OUT_L) if "correct" in x))
