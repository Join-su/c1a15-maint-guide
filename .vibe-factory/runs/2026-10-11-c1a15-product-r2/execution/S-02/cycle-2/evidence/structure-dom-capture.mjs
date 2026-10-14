// 정비자 앱을 Prototype template 상태마다 움직여 .ap DOM을 저장한다(구조 대조 체크리스트 입력).
import { chromium } from "/Users/insujo/Documents/repo/c1a15-maint-guide/node_modules/playwright/index.mjs";
import { execFileSync } from "node:child_process";
import { writeFileSync, readFileSync } from "node:fs";
const OUT = process.argv[2]; const ROOT = "/Users/insujo/Documents/repo/c1a15-maint-guide";
const dc = (...a) => execFileSync("docker", ["compose", ...a], { cwd: ROOT, encoding: "utf-8" });
const psql = (q) => dc("exec", "-T", "db", "psql", "-U", "c1a15", "-d", "c1a15", "-tAc", q).trim();
const alarm = (s) => Number(/알람 (\d+) 등록/.exec(dc("exec", "-T", "api", "python", "-m", "c1a15.alarms", s))[1]);
const sim = (sid, mode) => execFileSync("docker", ["compose", "exec", "-T", "api", "python", "-", String(sid), mode], { cwd: ROOT, input: readFileSync(ROOT + "/e2e/sim_llm_failure.py") });
const reset = () => psql("delete from ops.audit_log; delete from ops.session_events; delete from ops.diag_sessions; delete from ops.alarms; delete from ops.login_sessions; update ops.grade_table g set grade = s.initial_grade from knowledge.manual_sections s where s.section_id = g.section_id; truncate checkpoints, checkpoint_blobs, checkpoint_writes");
const b = await chromium.launch();
let page;
const fresh = async () => { if (page) await page.context().close(); const ctx = await b.newContext({ viewport: { width: 1100, height: 760 } }); page = await ctx.newPage(); };
const save = async (name) => { await page.waitForTimeout(500); writeFileSync(`${OUT}/${name}.html`, await page.locator(".ap").evaluate((e) => {
  const c = e.cloneNode(true); // 비밀번호 칸 값은 저장하지 않는다(G6-S02C2-2 B2)
  c.querySelectorAll("input").forEach((i) => { if (i.type === "password") { i.setAttribute("value", ""); i.value = ""; } });
  return c.outerHTML;
})); };
const login = async (u = "tech.kim", pw = process.env.C1A15_TECH_PASSWORD) => { await page.goto("http://127.0.0.1:8081/"); await page.getByLabel("ID").fill(u); await page.getByLabel("비밀번호").fill(pw); await page.getByText("로그인", { exact: true }).click(); };
const sidOf = () => Number(/\/session\/(\d+)/.exec(page.url())[1]);
const toInstr = async () => { await page.getByText("진단 보기").click(); await page.locator(".nx .btn").click(); await page.getByText("잠금 완료", { exact: true }).click(); await page.waitForSelector(".lockok"); };

reset(); await fresh();
await page.goto("http://127.0.0.1:8081/"); await save("T01--default");
await login("lead.park", process.env.C1A15_LEAD_PASSWORD); await page.waitForSelector(".banner.bad"); await save("T01--role_error");
await login(); await page.waitForSelector(".g2"); await save("T02--empty");
await page.locator(".tb-bell").click(); await save("T12--empty"); await page.locator(".catch").click();
alarm("DEMO-01"); await page.waitForSelector(".al .dot.red", { timeout: 8000 }); await save("T02--new_alarm");
await page.locator(".al .btn").click(); await page.waitForSelector(".g73"); await save("T03--default");
await page.getByText("진단 보기").click(); await save("T04--default");
await page.locator(".hc").first().click(); await save("T13--default"); await page.locator(".mclose").click();
await page.locator(".nx .btn").click(); await save("T05--before_lock");
await page.getByText("잠금 완료", { exact: true }).click(); await page.waitForSelector(".lockok"); await save("T05--locked");
await page.getByText("사전 확인 완료").click(); await page.waitForSelector(".rbtns"); await save("T06--default");
await page.getByText("매뉴얼 원문 보기").click(); await save("T14--default"); await page.locator(".mclose").click();
alarm("DEMO-02"); await page.locator(".tb-home").click(); await page.waitForTimeout(5600); await save("T02--in_progress");
await page.locator(".tb-bell").click(); await save("T12--list"); await page.locator(".catch").click();
const sid1 = Number(psql("select max(session_id) from ops.diag_sessions"));
await page.goto(`http://127.0.0.1:8081/session/${sid1}`); await page.waitForSelector(".rbtns");
await page.locator(".rbtn", { hasText: "확인 불가" }).click(); await page.getByText("결과 보내기").click(); await page.waitForSelector(".banner.warn"); await save("T06--unable_next");
await page.getByLabel("메모").fill("기름때 보임"); await page.getByText("결과 보내기").click(); await page.waitForSelector(".modal"); await save("T07--confirm_question");
await page.getByText("아니요, 다시 입력").click(); await page.waitForSelector(".rbtns");
await page.locator(".rbtn", { hasText: "정상" }).click(); await page.getByLabel("메모").fill("바닥에서 타는 냄새"); await page.getByText("결과 보내기").click(); await page.waitForSelector(".modal"); await save("T07--out_of_scope");
await page.getByText("계속 진행").click(); await page.waitForTimeout(800); await save("T06--second_check");
// 첫 판정 호출
psql("update ops.grade_table set grade = 'C' where section_id in ('4.3', '4.5', '4.6')");
alarm("DEMO-03"); await page.locator(".tb-home").click(); await page.waitForTimeout(5600);
await page.locator(".al .btn", { hasText: "점검 시작" }).first().click(); await page.waitForSelector(".g73"); await page.getByText("진단 보기").click(); await save("T04--first_call");
psql("update ops.grade_table g set grade = s.initial_grade from knowledge.manual_sections s where s.section_id = g.section_id");
// 근거 적음: 그 세션의 상위 기록 score를 낮춰 시뮬레이션(score ≥ 0.5가 3건 미만)
const sid3 = sidOf(); psql(`update ops.diag_sessions set "similar" = (select jsonb_agg(jsonb_set(e, '{score}', to_jsonb(case when i <= 2 then 0.9 else 0.3 end))) from jsonb_array_elements("similar") with ordinality as t(e, i)) where session_id = ${sid3}`);
await page.reload(); await page.waitForSelector(".ch.amber"); await save("T04--low_evidence");
// B 점검
psql("update ops.grade_table set grade = 'B' where section_id = '4.3'");
alarm("DEMO-04"); await page.locator(".tb-home").click(); await page.waitForTimeout(5600);
await page.locator(".al .btn", { hasText: "점검 시작" }).first().click(); await page.waitForSelector(".g73"); await toInstr(); await page.getByText("사전 확인 완료").click(); await page.waitForSelector(".act.pre");
await page.locator(".ck").first().click(); await save("T06--b_precheck");
psql("update ops.grade_table g set grade = s.initial_grade from knowledge.manual_sections s where s.section_id = g.section_id");
// LLM 실패 시뮬레이션
alarm("DEMO-05"); await page.locator(".tb-home").click(); await page.waitForTimeout(5600);
await page.locator(".al .btn", { hasText: "점검 시작" }).first().click(); await page.waitForSelector(".g73"); await toInstr(); await page.getByText("사전 확인 완료").click(); await page.waitForSelector(".rbtns");
const sid5 = sidOf(); sim(sid5, "last"); await page.reload(); await page.waitForSelector(".orig"); await save("T06--fallback");
sim(sid5, "all"); await page.reload(); await page.waitForSelector(".banner.bad"); await save("T06--llm_repeat");
await b.close(); console.log("saved");
