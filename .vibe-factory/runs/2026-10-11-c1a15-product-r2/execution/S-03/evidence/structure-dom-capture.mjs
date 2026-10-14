// 정비자 앱을 S-03 Prototype template 상태마다 움직여 .ap DOM을 저장한다(구조 대조 체크리스트 입력).
import { chromium } from "/Users/insujo/Documents/repo/c1a15-maint-guide/node_modules/playwright/index.mjs";
import { execFileSync } from "node:child_process";
import { writeFileSync, readFileSync } from "node:fs";
const OUT = process.argv[2]; const ROOT = "/Users/insujo/Documents/repo/c1a15-maint-guide";
const dc = (args, input) => execFileSync("docker", ["compose", ...args], { cwd: ROOT, encoding: "utf-8", input });
const psql = (q) => dc(["exec", "-T", "db", "psql", "-U", "c1a15", "-d", "c1a15", "-tAc", q]).trim();
const alarm = (s) => Number(/알람 (\d+) 등록/.exec(dc(["exec", "-T", "api", "python", "-m", "c1a15.alarms", s]))[1]);
const sim = (file, ...a) => dc(["exec", "-T", "api", "python", "-", ...a.map(String)], readFileSync(`${ROOT}/e2e/${file}`));
const GR = "update ops.grade_table g set grade = s.initial_grade from knowledge.manual_sections s where s.section_id = g.section_id";
const reset = () => psql(`delete from ops.audit_log; delete from ops.calls; delete from ops.reports; delete from ops.session_events; delete from ops.diag_sessions; delete from ops.alarms; delete from ops.login_sessions; ${GR}; truncate checkpoints, checkpoint_blobs, checkpoint_writes`);
const b = await chromium.launch();
const ctx = await b.newContext({ viewport: { width: 1100, height: 760 } }); const page = await ctx.newPage();
const save = async (name) => { await page.waitForTimeout(400); writeFileSync(`${OUT}/${name}.html`, await page.locator(".ap").evaluate((e) => {
  const c = e.cloneNode(true);
  c.querySelectorAll("input").forEach((i) => { if (i.type === "password") { i.setAttribute("value", ""); i.value = ""; } });
  return c.outerHTML;
})); };
const sidOf = () => Number(/\/session\/(\d+)/.exec(page.url())[1]);
const first = async (demo) => {
  await page.locator(".tb-home").click(); alarm(demo);
  await page.locator(".al .btn", { hasText: "점검 시작" }).first().click({ timeout: 8000 }); await page.waitForURL(/\/session\/\d+/);
  await page.getByText("진단 보기").click(); await page.locator(".nx .btn").click();
  await page.getByText("잠금 완료", { exact: true }).click(); await page.getByText("사전 확인 완료").click(); await page.waitForSelector(".rbtns");
  return sidOf();
};
const result = async (value, memo) => {
  await page.locator(".rbtn", { hasText: value }).click(); if (memo) await page.getByLabel("메모").fill(memo);
  const sent = page.waitForResponse((r) => r.url().endsWith("/events") && r.request().method() === "POST");
  await page.getByText("결과 보내기").click(); await sent; await page.waitForTimeout(200);
};
const checkN = async (n) => { const it = page.locator(".act .ck"); for (let i = 0; i < n; i++) await it.nth(i).click(); };
const allNormal = async () => { for (let i = 0; i < 6 && (await page.locator(".rbtns").count()); i++) await result("정상"); };

reset();
await page.goto("http://127.0.0.1:8081/"); await page.getByLabel("ID").fill("tech.kim"); await page.getByLabel("비밀번호").fill(process.env.C1A15_TECH_PASSWORD);
await page.getByText("로그인", { exact: true }).click(); await page.waitForSelector(".g2");
// T08 · T09 주 흐름
let sid = await first("DEMO-01"); await result("이상", "기름때가 필터 표면 절반 이상");
await page.getByText("교체 완료").click(); await page.waitForSelector(".act .ck"); await checkN(2); await save("T08--action_a");
await checkN(0); const it = page.locator(".act .ck"); await it.nth(2).click();
await page.locator(".btn", { hasText: /^재가동$/ }).click(); await page.waitForSelector(".rv-big"); await save("T08--restart_check");
await page.locator(".choice2 .btn", { hasText: "경계 이내" }).click(); await page.waitForSelector(".rf"); await save("T09--draft");
const act = await page.locator('[data-field="action"] .rv2').textContent();
await page.locator('[data-field="action"] .ed').click(); await page.locator('[data-field="action"] textarea').fill(`${act} · 교체 후 온도 차 9.4 K로 회복`);
await page.locator(".cd-h b", { hasText: "정비 보고서 초안" }).click(); await page.waitForSelector(".rf.fail"); await save("T09--check_failed");
await page.locator('[data-field="action"] .ed').click(); await page.locator('[data-field="action"] textarea').fill(act);
await page.locator(".cd-h b", { hasText: "정비 보고서 초안" }).click(); await page.waitForTimeout(500);
await page.locator(".cta2 .btn").click(); await page.waitForSelector(".banner.ok"); await save("T09--confirmed");
// 근거 적음 보고서(score 시뮬레이션)
sid = await first("DEMO-02"); await result("이상", "기름때"); await page.getByText("교체 완료").click(); await page.waitForSelector(".act .ck"); await checkN(3);
await page.locator(".btn", { hasText: /^재가동$/ }).click(); await page.waitForSelector(".rv-big"); await page.locator(".choice2 .btn", { hasText: "경계 이내" }).click(); await page.waitForSelector(".rf");
psql(`update ops.diag_sessions set "similar" = (select jsonb_agg(jsonb_set(e, '{score}', to_jsonb(case when i <= 2 then 0.9 else 0.3 end))) from jsonb_array_elements("similar") with ordinality as t(e, i)) where session_id = ${sid}`);
await page.reload(); await page.waitForSelector('[data-field="evidence_records"] .ch.amber'); await save("T09--low_evidence");
// T10 호출
sid = await first("DEMO-03"); await allNormal(); await page.waitForSelector(".warn-h"); await save("T10--summary");
await page.getByText("호출하지 않고 대기").click(); await page.waitForSelector(".banner.warn"); await save("T10--waiting");
await page.getByText("파트장 호출").click(); await page.waitForSelector(".banner.info"); await save("T10--sent");
sim("sim_lead_answer.py", sid, "approved"); await page.reload(); await page.waitForSelector(".banner.ok"); await save("T10--ans_approved");
sid = await first("DEMO-04"); await allNormal(); await page.getByText("파트장 호출").click(); await page.waitForSelector(".banner.info");
sim("sim_lead_answer.py", sid, "daytime"); await page.reload(); await page.waitForSelector(".banner.warn"); await save("T10--ans_daytime");
sid = await first("DEMO-05"); await allNormal(); await page.getByText("파트장 호출").click(); await page.waitForSelector(".banner.info");
sim("sim_lead_answer.py", sid, "direct"); await page.reload(); await page.waitForSelector(".banner.info"); await save("T10--ans_direct");
// T11 · 감시 · B · 정정
psql("update ops.grade_table set grade = 'A' where section_id = '4.4'");
sid = await first("DEMO-01");
for (let i = 0; i < 8 && (await page.locator(".rbtns").count()); i++) { const t = await page.locator(".ins-h h3").textContent(); await result(t === "흡기 필터 육안 점검" || t === "냉각 팬 분해 점검" ? "확인 불가" : "정상"); }
await page.waitForSelector(".warn-h"); await save("T11--unable_repeat");
sid = await first("DEMO-02"); await allNormal(); await page.waitForSelector(".act .ck"); await checkN(3);
await page.locator(".btn", { hasText: /^재가동$/ }).click(); await page.waitForSelector(".rv-big"); await page.locator(".choice2 .btn", { hasText: "경계 이내" }).click();
await page.waitForSelector(".done-h"); await save("T11--monitor_close");
await page.getByText("보고서 작성").click(); await page.waitForSelector(".rf"); await save("T09--monitor_report");
psql(GR);
sid = await first("DEMO-03"); await result("정상", "바닥에서 타는 냄새"); await page.locator(".modal .btn", { hasText: "숙련자 인계" }).click(); await page.waitForSelector(".warn-h"); await save("T11--expert_handover");
psql("update ops.grade_table set grade = 'B' where section_id = '4.3.2'");
sid = await first("DEMO-04"); await result("이상", "기름때"); await page.waitForSelector(".act .ck"); await checkN(2); await save("T08--checklist_b");
psql(GR);
sid = await first("DEMO-05"); await result("정상"); await result("정상"); sim("sim_correction.py", sid, "4.3", "이상");
await page.reload(); await page.waitForSelector(".banner.info"); await save("T08--corrected_path");
await b.close(); console.log("saved");
