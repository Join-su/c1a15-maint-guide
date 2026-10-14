// S-06 수동 검토(Matrix manual_reviews, 최종 통합 검토 B2): dev 스택 마지막 빌드에서
// ① CO-31 ①: T06 / b_precheck(4.3 B, 절차 4단계) 1080 × 740 틀 — 절차 행 높이 · 간격 · 체크 행 · 본문 넘침을 잰다.
// ② OOS-01: T04 / first_call 앱 화면과 packet 부록 template(같은 앱 CSS)을 같은 크기로 나란히 캡처한다(PBC 이전 v17 캡처는 읽지 않음).
// 비밀번호는 환경 변수, 저장하는 것은 측정값 · 화면 캡처뿐.
import { chromium } from "/Users/insujo/Documents/repo/c1a15-maint-guide/node_modules/playwright/index.mjs";
import { execFileSync } from "node:child_process";
import { writeFileSync, readFileSync, readdirSync } from "node:fs";
const [, , OUT, APPX] = process.argv;
const ROOT = "/Users/insujo/Documents/repo/c1a15-maint-guide";
const dc = (a) => execFileSync("docker", ["compose", ...a], { cwd: ROOT, encoding: "utf-8" });
const psql = (q) => dc(["exec", "-T", "db", "psql", "-U", "c1a15", "-d", "c1a15", "-tAc", q]).trim();
const GR = "update ops.grade_table g set grade = s.initial_grade from knowledge.manual_sections s where s.section_id = g.section_id";
const reset = () => psql(`delete from ops.audit_log; delete from ops.calls; delete from ops.reports; delete from ops.grade_changes; delete from ops.session_events; delete from ops.diag_sessions; delete from ops.alarms; delete from ops.login_sessions; ${GR}; truncate checkpoints, checkpoint_blobs, checkpoint_writes`);
const alarm = (s) => dc(["exec", "-T", "api", "python", "-m", "c1a15.alarms", s]);
const b = await chromium.launch();
const ctx = await b.newContext({ viewport: { width: 1080, height: 740 } });
const page = await ctx.newPage();
const login = async () => {
  await page.goto("http://127.0.0.1:8081/");
  await page.getByLabel("ID").fill("tech.kim");
  await page.getByLabel("비밀번호").fill(process.env.C1A15_TECH_PASSWORD);
  await page.getByText("로그인", { exact: true }).click();
  await page.waitForSelector(".g2");
};
const result = {};
// ① CO-31 ①
reset();
psql("update ops.grade_table set grade = 'B' where section_id = '4.3'");
await login();
alarm("DEMO-01");
await page.locator(".al .btn", { hasText: "점검 시작" }).click();
await page.getByText("진단 보기").click();
await page.locator(".nx .btn").click();
await page.getByText("잠금 완료", { exact: true }).click();
await page.getByLabel("기록할 값").fill("하우징 표면 52 °C");
await page.getByText("사전 확인 완료").click();
await page.waitForSelector(".act.pre");
await page.waitForTimeout(500);
result.co31_b_precheck = await page.evaluate(() => {
  const r = (e) => e.getBoundingClientRect();
  const body = document.querySelector(".ap-body");
  const li = [...document.querySelectorAll(".proc li")];
  const ck = [...document.querySelectorAll(".act.pre .ck")];
  const gaps = li.slice(1).map((e, i) => Math.round(r(e).top - r(li[i]).bottom));
  return {
    frame: [window.innerWidth, window.innerHeight],
    proc_steps: li.length,
    proc_row_px: li.map((e) => Math.round(r(e).height)),
    proc_gap_px: gaps,
    proc_font: li[0] ? getComputedStyle(li[0]).fontSize : null,
    ck_rows: ck.length,
    ck_row_px: ck.map((e) => Math.round(r(e).height)),
    body_client_height: body.clientHeight,
    body_scroll_height: body.scrollHeight,
    overflows: body.scrollHeight > body.clientHeight + 1,
    page_overflows: document.documentElement.scrollHeight > window.innerHeight + 1,
  };
});
writeFileSync(`${OUT}/CO-31-T06-b_precheck.png`, await page.locator(".ap").screenshot());
// ② OOS-01: T04 / first_call — 앱 · 부록 template 나란히
reset();
psql("update ops.grade_table set grade = 'C' where section_id in ('4.3', '4.5', '4.6')");
await login(); // 초기화가 로그인 세션도 지움
alarm("DEMO-03");
await page.waitForSelector(".al .btn");
await page.locator(".al .btn", { hasText: "점검 시작" }).first().click();
await page.getByText("진단 보기").click();
await page.waitForSelector(".nx");
await page.waitForTimeout(500);
const appShot = await page.locator(".ap").screenshot();
writeFileSync(`${OUT}/OOS-01-T04-first_call-app.png`, appShot);
const css = readdirSync(`${ROOT}/apps/tech/dist/assets`).filter((f) => f.endsWith(".css")).map((f) => readFileSync(`${ROOT}/apps/tech/dist/assets/${f}`, "utf-8")).join("\n");
const tpl = readFileSync(`${APPX}/templates/T04--first_call.html`, "utf-8");
const p2 = await ctx.newPage();
await p2.setContent(`<!doctype html><html><head><meta charset="utf-8"><style>${css}</style></head><body>${tpl}</body></html>`);
await p2.waitForTimeout(300);
writeFileSync(`${OUT}/OOS-01-T04-first_call-template.png`, await p2.locator(".ap").screenshot());
const a64 = appShot.toString("base64"), t64 = readFileSync(`${OUT}/OOS-01-T04-first_call-template.png`).toString("base64");
const p3 = await b.newPage({ viewport: { width: 2200, height: 820 } });
await p3.setContent(`<!doctype html><html><body style="margin:0;font:14px sans-serif;display:flex;gap:16px;padding:12px;background:#fff">
<figure style="margin:0"><figcaption>앱(마지막 빌드) T04 / first_call</figcaption><img src="data:image/png;base64,${a64}" width="1080"></figure>
<figure style="margin:0"><figcaption>packet 부록 template(같은 앱 CSS)</figcaption><img src="data:image/png;base64,${t64}" width="1080"></figure></body></html>`);
writeFileSync(`${OUT}/OOS-01-T04-first_call-side-by-side.png`, await p3.screenshot({ fullPage: true }));
result.oos01 = await page.evaluate(() => ({
  next_card_head: document.querySelector(".nx .sm")?.textContent ?? null,
  next_title: document.querySelector(".nx h3")?.textContent ?? null,
  start_button_class: document.querySelector(".nx .btn")?.className ?? null,
}));
reset();
writeFileSync(`${OUT}/manual-review-metrics.json`, JSON.stringify(result, null, 1));
console.log(JSON.stringify(result));
await b.close();
