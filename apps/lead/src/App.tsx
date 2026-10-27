// 파트장 앱(P-12): 로그인 → 승인 대기(L02 · L03) · 처리할 호출(L04) · 권한 등급(L05) · 감사 기록(L06). 10초 주기 조회.
// 화면은 API 값만 보인다(P-11). 주소(/review/{id} · /calls/{id} 등)를 기억해 새로고침에도 같은 자리.

import { useCallback, useMemo, useState } from "react";
import { createApi, useFreshScreenGuard, type Schemas } from "@c1a15/ui";
import { device, type Me } from "./device";
import { usePoll } from "./hooks";
import { ApprovalList, Review } from "./screens/Approvals";
import { AuditScreen, type AuditFilter } from "./screens/Audit";
import { CallDetail, CallList } from "./screens/Calls";
import { Frame, type Menu } from "./screens/Frame";
import { GradesScreen } from "./screens/Grades";
import { Login } from "./screens/Login";

type View =
  | { name: "approvals" }
  | { name: "review"; id: number }
  | { name: "calls" }
  | { name: "call"; id: number }
  | { name: "grades" }
  | { name: "audit" };

const TITLE: Record<Menu, string> = { approvals: "승인 대기", calls: "처리할 호출", grades: "권한 등급", audit: "감사 기록" };

function viewFromPath(): View {
  const p = window.location.pathname;
  let m = /^\/review\/(\d+)/.exec(p);
  if (m) return { name: "review", id: Number(m[1]) };
  m = /^\/calls\/(\d+)/.exec(p);
  if (m) return { name: "call", id: Number(m[1]) };
  if (p.startsWith("/calls")) return { name: "calls" };
  if (p.startsWith("/grades")) return { name: "grades" };
  if (p.startsWith("/audit")) return { name: "audit" };
  return { name: "approvals" };
}

function pathOf(v: View): string {
  return v.name === "review" ? `/review/${v.id}` : v.name === "call" ? `/calls/${v.id}` : v.name === "approvals" ? "/" : `/${v.name}`;
}

function menuOf(v: View): Menu {
  return v.name === "review" ? "approvals" : v.name === "call" ? "calls" : v.name;
}

export function App() {
  const api = useMemo(() => createApi(), []);
  const [me, setMeState] = useState<Me | null>(() => device.me());
  const [view, setView] = useState<View>(viewFromPath);
  useFreshScreenGuard(JSON.stringify(view)); // EV-007: 목록 → 검토 · 답하기 화면이 바뀐 직후 누름 무시
  const [overview, setOverview] = useState<Schemas["LeadOverview"] | null>(null);
  const [report, setReport] = useState<Schemas["LeadReport"] | null>(null);
  const [calls, setCalls] = useState<Schemas["LeadCalls"] | null>(null);
  const [call, setCall] = useState<Schemas["LeadCall"] | null>(null);
  const [grades, setGrades] = useState<Schemas["LeadGrades"] | null>(null);
  const [audit, setAudit] = useState<Schemas["LeadAudit"] | null>(null);
  const [filter, setFilter] = useState<AuditFilter>({ equipment: null, user_id: null, date: null });

  const setMe = (m: Me | null) => {
    setMeState(m);
    device.setMe(m);
  };
  const expired = useCallback(() => setMe(null), []);
  const go = (v: View) => {
    setView(v);
    if (window.location.pathname !== pathOf(v)) window.history.pushState(null, "", pathOf(v));
  };

  const load = async () => {
    if (!me) return;
    const check = (status: number) => status === 401 && expired();
    if (view.name === "approvals") {
      const r = await api.GET("/api/lead/overview");
      check(r.response.status);
      if (r.data) setOverview(r.data);
    } else if (view.name === "review") {
      const r = await api.GET("/api/lead/reports/{report_id}", { params: { path: { report_id: view.id } } });
      check(r.response.status);
      if (r.data) setReport((prev) => (prev?.report_id === r.data.report_id ? prev : r.data));
    } else if (view.name === "calls") {
      const r = await api.GET("/api/lead/calls");
      check(r.response.status);
      if (r.data) setCalls(r.data);
    } else if (view.name === "call") {
      const r = await api.GET("/api/lead/calls/{call_id}", { params: { path: { call_id: view.id } } });
      check(r.response.status);
      if (r.data) setCall((prev) => (prev?.call_id === r.data.call_id ? prev : r.data));
    } else if (view.name === "grades") {
      const r = await api.GET("/api/lead/grades");
      check(r.response.status);
      if (r.data) setGrades(r.data);
    } else {
      const query = Object.fromEntries(Object.entries(filter).filter(([, v]) => v)) as Record<string, string>;
      const r = await api.GET("/api/lead/audit", { params: { query } });
      check(r.response.status);
      if (r.data) setAudit(r.data);
    }
  };
  // 검토 · 답하기 화면은 입력 중이라 처음 한 번만 읽고(같은 대상이면 덮어쓰지 않음), 목록 화면은 10초마다
  usePoll(load, 10_000, [me?.user_id, view.name, (view as { id?: number }).id, JSON.stringify(filter)]);

  if (!me) return <Login api={api} onDone={(m) => { setMe(m); go({ name: "approvals" }); }} />;

  const menu = menuOf(view);
  const now =
    (view.name === "approvals" && overview?.now) ||
    ((view.name === "calls" || view.name === "call") && calls?.now) ||
    (view.name === "grades" && grades?.now) ||
    (view.name === "audit" && audit?.now) ||
    new Date().toISOString();
  let body = null;
  if (view.name === "approvals" && overview) body = <ApprovalList data={overview} onOpen={(id) => go({ name: "review", id })} />;
  else if (view.name === "review" && report?.report_id === view.id)
    body = <Review key={report.report_id} api={api} report={report} onDone={() => go({ name: "approvals" })} />;
  else if (view.name === "calls" && calls) body = <CallList data={calls} onOpen={(id) => go({ name: "call", id })} />;
  else if (view.name === "call" && call?.call_id === view.id)
    body = <CallDetail key={call.call_id} api={api} call={call} onDone={() => go({ name: "calls" })} />;
  else if (view.name === "grades" && grades) body = <GradesScreen api={api} data={grades} onChanged={() => void load()} />;
  else if (view.name === "audit" && audit) body = <AuditScreen data={audit} onFilter={setFilter} />;
  return (
    <Frame menu={menu} me={me} title={TITLE[menu]} now={now} onMenu={(mm) => go({ name: mm })}>
      {body}
    </Frame>
  );
}
