// 정비자 앱 T15 · T08 / corrected_path · T10 / summary_corrected · 파생 T09 / draft_corrected · T10 / corrected_ans_* 와
// 파트장 앱 L04 / call_corrected · 파생 L04 / handover_corrected · correction_call_detail · L06 / correction 을 S-05 상태마다 움직여 DOM을 저장한다(구조 대조 입력).
// CO-38: T15 / check_b 실제 화면 높이 측정, CO-39: 지난 화면 칩(.ch.amber)과 G2B '수정 가능' 흰 칩 토큰(.hist-row.unsent .ch.amber)을 나란히 캡처.
import { chromium } from "/Users/insujo/Documents/repo/c1a15-maint-guide/node_modules/playwright/index.mjs";
import { execFileSync } from "node:child_process";
import { writeFileSync } from "node:fs";
const OUT = process.argv[2]; const SHOTS = process.argv[3]; const ROOT = "/Users/insujo/Documents/repo/c1a15-maint-guide";
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
const st = (name) => save(t, name, ".ap"); const sl = (name) => save(l, name, ".wb");
const login = async (p, base, u, pw) => { await p.goto(base + "/"); await p.getByLabel("ID").fill(u); await p.getByLabel("비밀번호").fill(pw); await p.getByText("로그인", { exact: true }).click(); };
const step = (n) => t.locator(".ap-step .sp").nth(n - 1);
const pb = (label) => t.locator(".pastbar .btn", { hasText: label });
const toCheck = async (demo) => {
  await t.locator(".tb-home").click(); alarm(demo);
  await t.locator(".al .btn", { hasText: "점검 시작" }).first().click({ timeout: 8000 }); await t.waitForURL(/\/session\/\d+/);
  await t.getByText("진단 보기").click(); await t.locator(".nx .btn").click();
  await t.getByText("잠금 완료", { exact: true }).click(); await t.getByLabel("기록할 값").fill("하우징 표면 52 °C · 공기 302.7 K · 공정 310.5 K");
  await t.getByText("사전 확인 완료").click(); await t.waitForSelector(".rbtns");
  return Number(/\/session\/(\d+)/.exec(t.url())[1]);
};
const result = async (value, memo) => {
  await t.locator(".rbtn", { hasText: value }).click(); if (memo) await t.getByLabel("메모").fill(memo);
  const sent = t.waitForResponse((r) => r.url().endsWith("/events") && r.request().method() === "POST");
  await t.getByText("결과 보내기").click(); await sent; await t.waitForTimeout(200);
};
const toPast = async (n, idxFromEnd = 0) => { await step(n).click(); await t.waitForSelector(".pastbar"); for (let i = 0; i < idxFromEnd; i++) await pb("이전").click(); };
const metrics = {};
await login(l, LEAD, "lead.park", process.env.C1A15_LEAD_PASSWORD); await l.waitForSelector(".wb-side");
await login(t, TECH, "tech.kim", process.env.C1A15_TECH_PASSWORD); await t.waitForSelector(".g2");
// A. DEMO-01: 4.3 정상 → 지금 지시 + 보내지 않은 입력 → 지난 화면 알람 · 진단 · 잠금 · 사전 확인 · check_current · correct · correct_value · confirm · note
const sidA = await toCheck("DEMO-01");
await result("정상", "필터 깨끗함");
await t.locator(".rbtn", { hasText: "정상" }).click(); await t.getByLabel("메모").fill("수위 MAX 선 가까이");
await toPast(1); await st("T15--alarm");
await toPast(2); await st("T15--diagnosis");
await toPast(3); await st("T15--check_current");
writeFileSync(`${SHOTS}/T15-check_current.png`, await t.locator(".ap").screenshot());
// CO-39: 같은 화면에 G2B '수정 가능' 흰 칩 토큰을 나란히 붙여 캡처(승인 CSS의 .hist-row.unsent .ch.amber)
await t.evaluate(() => {
  const bar = document.querySelector(".pastbar"); const box = document.createElement("div"); box.id = "co39";
  box.style.cssText = "display:flex;gap:24px;align-items:center;margin:8px 22px;padding:10px 14px;background:#fff;border:1px dashed #94a3b8;border-radius:10px";
  box.innerHTML = '<span style="font-size:13px;color:#475569">앱(Prototype) 지난 화면 칩</span>' + bar.querySelector(".ch.amber").outerHTML
    + '<span style="font-size:13px;color:#475569">G2B \'수정 가능\' 흰 칩 토큰</span><div class="hist-row unsent" style="display:inline-flex;grid-template-columns:none;padding:4px 8px;margin:0"><span class="ch amber">수정 가능</span></div>';
  bar.after(box);
});
writeFileSync(`${SHOTS}/CO-39-chips.png`, await t.locator("#co39").screenshot());
await t.evaluate(() => document.getElementById("co39")?.remove());
await pb("이전").click(); await st("T15--precheck");
await pb("이전").click(); await st("T15--lock");
await t.locator(".btn", { hasText: "메모 덧붙이기" }).click(); await t.getByLabel("덧붙일 메모").fill("잠금 표지 2번 패널에 추가로 걺"); await st("T15--note");
await t.locator(".modal .btn", { hasText: "취소" }).click();
await pb("다음").click(); await t.locator(".btn", { hasText: "이 기록 정정" }).click();
await t.getByLabel("정정할 값").fill("하우징 표면 52 °C · 공기 302.7 K · 공정 310.5 K"); await st("T15--correct_value");
await t.locator(".modal .btn", { hasText: "취소" }).click();
await pb("다음").click(); await t.locator(".btn", { hasText: "이 기록 정정" }).click();
await t.locator(".modal .rbtn", { hasText: "이상" }).click(); await t.getByLabel("정정할 메모").fill("필터 뒷면에 기름때가 절반 넘게 덮음"); await st("T15--correct");
await t.getByLabel("정정 사유").fill("필터 뒷면 기름때를 못 보고 정상으로 눌렀음"); await t.locator(".modal .btn", { hasText: "정정 저장" }).click();
await t.waitForSelector('.modal[aria-label="이 정정으로 다음 지시가 바뀝니다"]'); await st("T15--correct_confirm");
await t.locator(".modal .btn.warnb", { hasText: "정정 저장" }).click(); await t.waitForSelector(".corr-list");
await pb("현재 단계로").click(); await t.waitForSelector(".done-h"); await st("T08--corrected_path");
await toPast(3); await st("T15--corrected");
await pb("현재 단계로").click();
// 조치 → 재가동 → 보고서(정정 표기, 파생 T09 / draft_corrected) → T15 / action · check(지금 보고서 단계에서 점검 기록) → 확정 → closed
await t.getByText("교체 완료").click(); await t.waitForSelector(".act .ck"); const it = t.locator(".act .ck"); for (let i = 0; i < (await it.count()); i++) await it.nth(i).click();
await t.locator(".btn", { hasText: /^재가동$/ }).click(); await t.waitForSelector(".rv-big");
await t.locator(".choice2 .btn", { hasText: "경계 이내" }).click(); await t.waitForSelector(".rf"); await st("T09--draft_corrected");
await toPast(4); await st("T15--action");
await toPast(3); await st("T15--check");
await pb("현재 단계로").click(); await t.locator(".cta2 .btn").click(); await t.waitForSelector(".banner.ok");
await toPast(3); await st("T15--closed");
// B. DEMO-02(4.3 = B): B 점검 기록 지난 화면 + CO-38 높이
psql("update ops.grade_table set grade = 'B' where section_id = '4.3'");
await toCheck("DEMO-02");
await t.waitForSelector(".act.pre .ck"); const cks = t.locator(".act.pre .ck"); for (let i = 0; i < (await cks.count()); i++) await cks.nth(i).click();
await t.waitForSelector(".rbtn:not(.dis)"); await result("이상", "기름때가 필터 표면 절반 넘게 덮음"); await t.waitForSelector(".done-h"); psql(GR);
await toPast(3); await t.waitForSelector(".ap-body.past .act.pre"); await st("T15--check_b");
metrics.check_b = await t.evaluate(() => {
  const body = document.querySelector(".ap-body.past"); const ck = document.querySelector(".act.pre .ck"); const li = document.querySelector(".proc li");
  const fs = (e) => (e ? getComputedStyle(e).fontSize : null);
  return { frame: [document.querySelector(".ap").clientWidth, document.querySelector(".ap").clientHeight], body_height: body.clientHeight, body_scroll_height: body.scrollHeight,
    overflows: body.scrollHeight > body.clientHeight + 1, ck_row_px: ck ? Math.round(ck.getBoundingClientRect().height) : null, ck_font: fs(ck), proc_font: fs(li), proc_line_height: li ? getComputedStyle(li).lineHeight : null };
});
writeFileSync(`${SHOTS}/T15-check_b.png`, await t.locator(".ap").screenshot());
// C. DEMO-03: 보낸 호출 뒤 정정 → T15 / call · L04 / call_corrected · L06 / correction
const sidC = await toCheck("DEMO-03");
for (let i = 0; i < 4 && (await t.locator(".rbtns").count()); i++) await result("정상");
await t.getByText("파트장 호출").click(); await t.waitForSelector(".banner.info");
const hc = await t.request.get(`${TECH}/api/tech/sessions/${sidC}/history`).then((r) => r.json());
const rc = hc.steps[2].records; const i43 = rc.findIndex((r) => r.kind === "check" && r.section === "4.3");
await toPast(3, rc.length - 1 - i43); await t.locator(".btn", { hasText: "이 기록 정정" }).click();
await t.locator(".modal .rbtn", { hasText: "이상" }).click(); await t.getByLabel("정정 사유").fill("필터 뒷면 기름때를 못 보고 정상으로 눌렀음"); await t.locator(".modal .btn", { hasText: "정정 저장" }).click();
await t.waitForSelector(".corr-list"); for (let i = i43; i < rc.length - 1; i++) await pb("다음").click(); await t.waitForSelector(".corr-box"); await st("T15--call");
await l.goto(LEAD + "/calls"); await l.locator("tr[data-call] .btn", { hasText: "답하기" }).first().click(); await l.waitForSelector(".corr-box"); await sl("L04--call_corrected");
await l.goto(LEAD + "/audit"); await l.waitForSelector(".wt td"); await l.locator(".flt > .sel2").nth(0).click(); await l.locator(".dd div", { hasText: "M-04" }).click(); await l.waitForTimeout(800); await sl("L06--correction");
// D. DEMO-05: 숙련자 인계 답 대기 중 정정(결정 019 ②) → 파생 L04 / handover_corrected
psql("update ops.grade_table set grade = 'A' where section_id = '4.4'");
const sidD = await toCheck("DEMO-05");
for (let i = 0; i < 10 && (await t.locator(".rbtns").count()); i++) { const x = await t.locator(".ins-h h3").textContent(); await result(x === "흡기 필터 육안 점검" || x === "냉각 팬 분해 점검" ? "확인 불가" : "정상"); }
await t.locator(".btn.warnb", { hasText: "숙련자 인계" }).click(); await t.waitForSelector(".banner.info"); psql(GR);
const hd = await t.request.get(`${TECH}/api/tech/sessions/${sidD}/history`).then((r) => r.json());
const t46 = hd.steps[2].records.find((r) => r.kind === "check" && r.section === "4.6");
await t.request.post(`${TECH}/api/tech/sessions/${sidD}/corrections`, { data: { target_seq: t46.seq, value: "이상", reason: "설정값을 다시 읽음" } });
await l.goto(LEAD + "/calls"); await l.locator("tr[data-call]", { hasText: "숙련자 인계" }).locator(".btn").click(); await l.waitForSelector(".corr-box"); await sl("L04--handover_corrected");
// E. 조치 뒤 정정 → T10 / summary_corrected → 파생 L04 / correction_call_detail → 답 → 파생 T10 / corrected_ans_daytime · direct
for (const [demo, answer] of [["DEMO-04", "주간 처리"], ["DEMO-06", "직접 확인"]]) {
  await toCheck(demo); await result("이상", "기름때");
  await t.locator(".act .btn").first().click(); await t.waitForTimeout(400);
  await toPast(3); await t.locator(".btn", { hasText: "이 기록 정정" }).click();
  await t.locator(".modal .rbtn", { hasText: "정상" }).click(); await t.getByLabel("정정 사유").fill("다시 보니 깨끗함"); await t.locator(".modal .btn", { hasText: "정정 저장" }).click();
  await t.waitForSelector(".corr-list"); await pb("현재 단계로").click(); await t.waitForSelector(".warn-h");
  if (answer === "주간 처리") await st("T10--summary_corrected");
  await t.getByText("파트장 호출").click(); await t.waitForSelector(".banner.info");
  await l.goto(LEAD + "/calls"); await l.locator("tr[data-call]", { hasText: "정정 확인" }).locator(".btn").click(); await l.waitForSelector(".dopt");
  if (answer === "주간 처리") await sl("L04--correction_call_detail");
  await l.locator(".dopt", { hasText: answer }).click(); if (answer === "직접 확인") await l.getByLabel("처리 메모").fill("직접 확인, 필터 표면 양호");
  await l.locator(".btn", { hasText: "답 저장" }).click(); await l.waitForSelector("tr[data-call], .empty");
  await t.reload(); await t.waitForSelector(".banner"); await st(answer === "주간 처리" ? "T10--corrected_ans_daytime" : "T10--corrected_ans_direct");
}
writeFileSync(`${OUT}/../co38-metrics.json`, JSON.stringify(metrics, null, 1));
await b.close(); console.log("saved", JSON.stringify(metrics));
