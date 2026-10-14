// 파트장 앱(L01 ~ L06) · 정비자 앱(T02 / rejected · T12 / list · T10)을 S-04 Prototype 상태마다 움직여 DOM을 저장한다(구조 대조 입력).
import { chromium } from "/Users/insujo/Documents/repo/c1a15-maint-guide/node_modules/playwright/index.mjs";
import { execFileSync } from "node:child_process";
import { writeFileSync } from "node:fs";
const OUT = process.argv[2]; const ROOT = "/Users/insujo/Documents/repo/c1a15-maint-guide";
const TECH = "http://127.0.0.1:8081", LEAD = "http://127.0.0.1:8082";
const dc = (args) => execFileSync("docker", ["compose", ...args], { cwd: ROOT, encoding: "utf-8" });
const psql = (q) => dc(["exec", "-T", "db", "psql", "-U", "c1a15", "-d", "c1a15", "-tAc", q]).trim();
const alarm = (s) => Number(/알람 (\d+) 등록/.exec(dc(["exec", "-T", "api", "python", "-m", "c1a15.alarms", s]))[1]);
const GR = "update ops.grade_table g set grade = s.initial_grade from knowledge.manual_sections s where s.section_id = g.section_id";
psql(`delete from ops.audit_log; delete from ops.calls; delete from ops.reports; delete from ops.grade_changes; delete from ops.session_events; delete from ops.diag_sessions; delete from ops.alarms; delete from ops.login_sessions; delete from knowledge.history_embeddings where record_id like 'R-%'; delete from knowledge.history_records where record_id like 'R-%'; ${GR}; truncate checkpoints, checkpoint_blobs, checkpoint_writes`);
const b = await chromium.launch();
const tctx = await b.newContext({ viewport: { width: 1100, height: 760 } }); const t = await tctx.newPage();
const lctx = await b.newContext({ viewport: { width: 1280, height: 620 } }); const l = await lctx.newPage();
const save = async (p, name, root) => { await p.waitForTimeout(500); writeFileSync(`${OUT}/${name}.html`, await p.locator(root).first().evaluate((e) => {
  const c = e.cloneNode(true);
  c.querySelectorAll("input").forEach((i) => { if (i.type === "password") { i.setAttribute("value", ""); i.value = ""; } });
  return c.outerHTML;
})); };
const sl = (name) => save(l, name, ".wb"); const st = (name) => save(t, name, ".ap");
const login = async (p, base, u, pw) => { await p.goto(base + "/"); await p.getByLabel("ID").fill(u); await p.getByLabel("비밀번호").fill(pw); await p.getByText("로그인", { exact: true }).click(); };
const first = async (demo) => {
  await t.locator(".tb-home").click(); alarm(demo);
  await t.locator(".al .btn", { hasText: "점검 시작" }).first().click({ timeout: 8000 }); await t.waitForURL(/\/session\/\d+/);
  await t.getByText("진단 보기").click(); await t.locator(".nx .btn").click();
  await t.getByText("잠금 완료", { exact: true }).click(); await t.getByText("사전 확인 완료").click(); await t.waitForSelector(".rbtns");
  return Number(/\/session\/(\d+)/.exec(t.url())[1]);
};
const result = async (value, memo) => {
  await t.locator(".rbtn", { hasText: value }).click(); if (memo) await t.getByLabel("메모").fill(memo);
  const sent = t.waitForResponse((r) => r.url().endsWith("/events") && r.request().method() === "POST");
  await t.getByText("결과 보내기").click(); await sent; await t.waitForTimeout(200);
};
const confirm = async (demo, low = false) => {
  const sid = await first(demo);
  if (low) { psql(`update ops.diag_sessions set "similar" = (select jsonb_agg(jsonb_set(e, '{score}', to_jsonb(case when i <= 2 then 0.9 else 0.3 end))) from jsonb_array_elements("similar") with ordinality as t(e, i)) where session_id = ${sid}`); await t.reload(); await t.waitForSelector(".rbtns"); }
  await result("이상", "기름때가 필터 표면 절반 넘게 덮음"); await t.getByText("교체 완료").click(); await t.waitForSelector(".act .ck");
  const it = t.locator(".act .ck"); for (let i = 0; i < (await it.count()); i++) await it.nth(i).click();
  await t.locator(".btn", { hasText: /^재가동$/ }).click(); await t.waitForSelector(".rv-big");
  await t.locator(".choice2 .btn", { hasText: "경계 이내" }).click(); await t.waitForSelector(".rf"); await t.locator(".cta2 .btn").click(); await t.waitForSelector(".banner.ok");
  return sid;
};
// L01
await l.goto(LEAD + "/"); await sl("L01--default");
await login(l, LEAD, "tech.kim", process.env.C1A15_TECH_PASSWORD); await l.waitForSelector(".banner.bad"); await sl("L01--role_error");
await login(l, LEAD, "lead.park", process.env.C1A15_LEAD_PASSWORD); await l.waitForSelector(".wb-side"); await l.waitForSelector(".empty"); await sl("L02--empty");
await login(t, TECH, "tech.kim", process.env.C1A15_TECH_PASSWORD); await t.waitForSelector(".g2");
// 승인 대기 3건(근거 적음 1) + 호출 2건
const r1 = await confirm("DEMO-01"); await confirm("DEMO-02"); await confirm("DEMO-03", true);
await first("DEMO-04"); for (let i = 0; i < 4 && (await t.locator(".rbtns").count()); i++) await result("정상"); await t.getByText("파트장 호출").click(); await t.waitForSelector(".banner.info");
await st("T10--sent");
psql("update ops.grade_table set grade = 'A' where section_id = '4.4'");
await first("DEMO-05");
for (let i = 0; i < 8 && (await t.locator(".rbtns").count()); i++) { const x = await t.locator(".ins-h h3").textContent(); await result(x === "흡기 필터 육안 점검" || x === "냉각 팬 분해 점검" ? "확인 불가" : "정상"); }
await t.locator(".btn.warnb", { hasText: "숙련자 인계" }).click(); await t.waitForSelector(".banner.info");
await st("T11--handover_sent"); // 결정 018 ④ 보냄 · 답 대기(파생: T10 / sent 구조)
psql(GR);
await l.goto(LEAD + "/"); await l.waitForSelector("tr[data-report]"); await sl("L02--list");
await l.locator("tr[data-report] .btn").last().click(); await l.waitForSelector(".rk2"); await sl("L03--review");
await l.locator(".dopt", { hasText: "수정 후 승인" }).click(); await l.locator('[data-field="unresolved"] .rv2').click();
await l.locator('[data-field="unresolved"] textarea').fill("냉각 팬 상태(4.4, C) · 주간 조 확인 배정"); await l.getByLabel("메모").fill("고친 이유: 주간 확인 담당을 지정함"); await l.waitForTimeout(900); await sl("L03--edit");
await l.locator('[data-field="unresolved"] textarea').fill("냉각 팬 상태(4.4, C) · 팬 회전수 1,850 rpm으로 정상 확인"); await l.waitForSelector(".rf.fail"); await sl("L03--edit_failed");
await l.locator(".dopt", { hasText: "반려" }).click(); await l.getByLabel("메모").fill(""); await l.waitForSelector(".req"); await sl("L03--reject");
await l.goto(LEAD + "/calls"); await l.waitForSelector("tr[data-call]"); await sl("L04--list");
await l.locator("tr[data-call]", { hasText: "파트장 호출" }).locator(".btn").click(); await l.waitForSelector(".dopt"); await sl("L04--call_detail");
await l.goto(LEAD + "/calls"); await l.locator("tr[data-call]", { hasText: "숙련자 인계" }).locator(".btn").click(); await l.waitForSelector(".dopt"); await sl("L04--handover_detail");
await l.goto(LEAD + "/grades"); await l.waitForSelector("tr[data-section]"); await sl("L05--default");
await l.locator('tr[data-section="4.3"] .sel2').click(); await l.locator(".dd div", { hasText: "C 승인 필요" }).click(); await l.waitForSelector(".banner.info"); await sl("L05--raise_warning");
await l.locator(".choice2 .btn", { hasText: "취소" }).click();
await l.locator('tr[data-section="4.4"] .sel2').click(); await l.locator(".dd div", { hasText: "B 확인 후" }).click(); await l.waitForSelector(".banner.warn"); await sl("L05--lower_warning");
await l.locator(".choice2 .btn", { hasText: "취소" }).click();
// 승인 후 진행 → T10 / ans_approved, 반려 → T02 / rejected, T12 / list(4종류)
await l.goto(LEAD + "/calls"); await l.locator("tr[data-call]", { hasText: "파트장 호출" }).locator(".btn").click(); await l.locator(".btn", { hasText: "답 저장" }).click(); await l.waitForSelector("tr[data-call], .empty");
await l.goto(LEAD + "/"); await l.waitForSelector("tr[data-report]");
const rid = psql(`select report_id from ops.reports where session_id = ${r1}`);
await l.goto(LEAD + `/review/${rid}`); await l.waitForSelector(".rk2"); await l.locator(".dopt", { hasText: "반려" }).click(); await l.getByLabel("메모").fill("필터 표면 상태를 메모로 다시 적어 주세요"); await l.locator(".btn", { hasText: "결정 저장" }).click(); await l.waitForSelector("tr[data-report]");
alarm("DEMO-01");
await t.locator(".tb-home").click(); await t.waitForTimeout(5600); await t.waitForSelector(".banner.bad"); await st("T02--rejected");
await t.locator(".tb-bell").click(); await t.waitForSelector(".panel .grp"); await st("T12--list");
await t.locator(".nt-item .btn", { hasText: "답 보기" }).click(); await t.waitForSelector(".banner.ok"); await st("T10--ans_approved");
await l.goto(LEAD + "/audit"); await l.waitForSelector(".wt td"); await sl("L06--default");
await l.locator(".flt > .sel2").nth(0).click(); await l.locator(".dd div").nth(1).click(); await l.waitForTimeout(800);
await l.locator(".flt > .sel2").nth(1).click(); await l.locator(".dd div", { hasText: "김 정비" }).click(); await l.waitForTimeout(800); await sl("L06--filtered");
// T10 / ans_direct(결정 018 ③: 직접 확인 답 + 처리 메모 → 처리 결과 배너 · 보고서 작성)
await t.locator(".tb-home").click(); await first("DEMO-03"); for (let i = 0; i < 4 && (await t.locator(".rbtns").count()); i++) await result("정상"); await t.getByText("파트장 호출").click(); await t.waitForSelector(".banner.info");
await l.goto(LEAD + "/calls"); await l.locator("tr[data-call]", { hasText: "파트장 호출" }).locator(".btn").click(); await l.waitForSelector(".dopt"); await l.locator(".dopt", { hasText: "직접 확인" }).click(); await l.getByLabel("처리 메모").fill("팬 베어링 소음 확인, 주간 교체 예정"); await l.locator(".btn", { hasText: "답 저장" }).click(); await l.waitForSelector("tr[data-call], .empty");
await t.reload(); await t.waitForSelector(".btn:has-text('보고서 작성')"); await st("T10--ans_direct");
// 파생 L04 / call_detail_d
psql("update ops.grade_table set grade = 'D' where section_id = '4.4'");
await first("DEMO-02"); for (let i = 0; i < 4 && (await t.locator(".rbtns").count()); i++) await result("정상"); await t.getByText("파트장 호출").click(); await t.waitForSelector(".banner.info");
await l.goto(LEAD + "/calls"); await l.locator("tr[data-call]", { hasText: "파트장 호출" }).locator(".btn").click(); await l.waitForSelector(".dopt"); await sl("L04--call_detail_d");
psql(GR);
await b.close(); console.log("saved");
