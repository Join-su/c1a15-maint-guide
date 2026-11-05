// D-538 · D-556 예외 상황 기록을 사람 손 순서로: 정비자 보고서 화면 '예외 상황 기록'(선택) 글 하나(자리글 = 안내 문구)
// → 「AI 나눔」(가짜 배포 서버 — 점검 1 + 조치 1 × 2 · 약속 v9 exception_similar 비슷한 것 상위 3) → 「AI 나눔」 한 번 더
// (같은 화면 · D-503 1) → item마다 비슷한 것 하나 「같음」(놓침 missed) / 「아님」(새 예외 new_exception)
// → 「보고서 확정」 → 확인 창 「취소」(글 · 고름 그대로) → 다시 확정 → 확정 뒤 칸은 읽기만
// → 파트장 최종본 '6. 예외 상황 기록'(글 · 나눔 줄 + 자동 정보 · 보기만) → 승인
// → 정비 이력 원본 층(record.exception_record)에 같이 저장.
// 0.4초 막기는 켠 채(누름 사이 0.8초). SHOT_DIR이면 화면마다 PNG(1280 × 800).

import { mkdirSync, writeFileSync } from "node:fs";
import path from "node:path";
import { expect, test, type Page, type TestInfo } from "@playwright/test";
import { guard, LEAD_PW, LEAD_URL, login, psql, resetOps, restartWithin, result, shot, toFirstCheck } from "./helpers";

test.beforeEach(() => resetOps());

const TEXT = "점검 필터 덮개 고정 나사를 손으로 확인. 조치 나사를 새로 끼움. 점검 흡기 덕트 이음매. 조치 밴드를 다시 조임";
const RESULT = "재가동 정상(경계 이내)";

async function snap(page: Page, info: TestInfo, name: string) {
  await shot(page, info, name);
  const dir = process.env.SHOT_DIR;
  if (dir) {
    mkdirSync(dir, { recursive: true });
    await page.screenshot({ path: path.join(dir, `${name}.png`) });
  }
}

const pause = (p: Page) => p.waitForTimeout(800);

test("예외 상황 기록: 보고서 확정과 함께 → 파트장 최종본 6번 구역 → 승인 → 이력 원본 층(사람 손 순서)", async ({ page, browser }, info) => {
  const g = guard(page);
  await login(page); // 진단 · 잠금까지는 도우미(다른 시험과 같음) — 이 시험의 사람 손 순서는 보고서 화면부터
  await toFirstCheck(page, "DEMO-01");
  await pause(page);
  await result(page, "이상", "기름때가 필터 표면 절반 넘게 덮음");
  await pause(page);
  await page.locator(".act .btn", { hasText: "조치 완료" }).click();
  await restartWithin(page);
  await pause(page);
  await page.locator(".choice2 .btn", { hasText: "경계 이내" }).click();
  // 보고서 화면: 확정 전 확인 위 '예외 상황 기록' 칸(선택 · 상황 · 결과 자동 · 설명 문장 0)
  const kh = page.locator(".kh");
  await expect(kh.locator(".cd-h b")).toHaveText("예외 상황 기록");
  await expect(kh.locator(".khf > .sm")).toHaveText(["상황 자동", "결과 자동"]);
  await expect(kh.locator('[data-part="ex-situation"]')).toHaveText(/^M-01 · 온도 차 저하 · .+ · 온도 차 /);
  await expect(kh.locator('[data-part="ex-result"]')).toHaveText(RESULT);
  const ta = kh.getByLabel("예외 글", { exact: true });
  await expect(ta).toHaveAttribute("placeholder", "점검한 것과 조치한 것을 모두 적어 주세요");
  await pause(page);
  await ta.click();
  await ta.fill(TEXT);
  await expect(page.locator(".cta2 .btn", { hasText: "보고서 확정" })).toHaveClass(/dis/); // 나눔 · 고름까지 잠금
  const rows = kh.locator('[data-part="ex-items"] .exi');
  for (let n = 0; n < 2; n++) {
    // 같은 화면에서 「AI 나눔」 두 번(D-503 1) — 같은 결과
    await pause(page);
    const sent = page.waitForResponse((r) => r.url().endsWith("/events") && r.request().method() === "POST");
    await kh.locator(".exa .btn", { hasText: "AI 나눔" }).click();
    expect((await sent).status()).toBe(200);
    await expect(rows).toHaveCount(2);
  }
  await expect(rows.nth(0).locator(".exl")).toHaveText(["점검필터 덮개 고정 나사를 손으로 확인 · 기준 정상 범위", "조치나사를 새로 끼움"]);
  const sim0 = rows.nth(0).locator(".exr");
  await expect(sim0.first()).toHaveText("예외EX-R-0001 필터 덮개 고정 나사 확인같음"); // 나사 item = 등록 예외가 맨 위
  expect(await sim0.count()).toBeLessThanOrEqual(3);
  await expect(rows.nth(1).locator(".exs .ch")).toHaveText("새 예외"); // 비슷한 것 0 → 같음 / 아님 없이(D-556 덧 5)
  await expect(rows.nth(1).locator(".exr, .btn")).toHaveCount(0);
  await pause(page);
  await rows.nth(0).locator(".exb .btn", { hasText: "아님" }).click();
  await pause(page);
  await sim0.first().locator(".btn", { hasText: "같음" }).click(); // 다시 고름 — 마지막이 이김
  await expect(page.locator(".cta2 .btn", { hasText: "보고서 확정" })).not.toHaveClass(/dis/); // 둘째 item은 고를 것 0
  await snap(page, info, "X1-report-exception");
  await pause(page);
  await page.locator(".cta2 .btn", { hasText: "보고서 확정" }).click();
  const dlg = page.locator('.modal[aria-label="보고서 확정"]');
  await pause(page);
  await dlg.locator(".btn", { hasText: "취소" }).click(); // 같은 화면에서 취소 → 다시(D-503 1)
  await expect(ta).toHaveValue(TEXT); // 취소해도 글 · 고름 그대로
  await expect(sim0.first().locator(".btn", { hasText: "같음" })).not.toHaveClass(/ghost/);
  await pause(page);
  await page.locator(".cta2 .btn", { hasText: "보고서 확정" }).click();
  await pause(page);
  await dlg.locator(".btn").filter({ hasText: /^확정$/ }).click();
  await expect(page.locator(".banner.ok b")).toHaveText(/^보고서를 확정했습니다/);
  await expect(kh.locator("textarea, .exb")).toHaveCount(0); // 확정 뒤엔 읽기만
  // 상황의 끝 시각 = 확정 시각(확정 전엔 지금 시각) — 확정 뒤 값으로 대조
  const situation = (await kh.locator('[data-part="ex-situation"]').textContent()) ?? "";
  expect(situation).toMatch(/^M-01 · 온도 차 저하 · .+ · 온도 차 /);
  await expect(kh.locator(".khf > .sm")).toHaveText(["상황", "적은 글", "결과"]);
  await expect(kh.locator(".exs .ch")).toHaveText(["같음 · 예외 EX-R-0001", "새 예외"]);
  await snap(page, info, "X2-confirmed");

  const lead = await (await browser.newContext({ viewport: { width: 1280, height: 800 } })).newPage();
  const lg = guard(lead);
  await lead.goto(LEAD_URL + "/");
  await lead.getByLabel("ID").fill("lead.park");
  await lead.getByLabel("비밀번호").fill(LEAD_PW);
  await pause(lead);
  await lead.locator(".lg-card button.lbtn").click();
  await expect(lead.locator("tr[data-report]")).toHaveCount(1);
  await pause(lead);
  await lead.locator("tr[data-report] button.lbtn", { hasText: "검토" }).click();
  await expect(lead.locator(".fdoc h2").last()).toHaveText("6. 예외 상황 기록");
  await expect(lead.locator(".fd-ex th")).toHaveText(["상황", "적은 글", "나눔 1", "나눔 2", "결과", "설비 · 증상", "센서값", "직전 정비", "AI 첫 안내", "확정 원인"]);
  await expect(lead.locator(".fd-ex td").nth(0)).toHaveText(situation);
  await expect(lead.locator(".fd-ex td").nth(1)).toHaveText(TEXT);
  await expect(lead.locator(".fd-ex td").nth(2)).toHaveText("점검 필터 덮개 고정 나사를 손으로 확인 · 조치 나사를 새로 끼움 같음 · 예외 EX-R-0001");
  await expect(lead.locator(".fd-ex td").nth(3)).toHaveText("점검 흡기 덕트 이음매 · 조치 밴드를 다시 조임 새 예외");
  await expect(lead.locator(".fd-ex td").nth(4)).toHaveText(RESULT);
  await expect(lead.locator(".fd-ex td").nth(8)).toHaveText("4.3 흡기 필터 육안 점검"); // 자동: AI 첫 안내
  await expect(lead.locator(".fd-ex td").nth(9)).toHaveText("냉각 필터 막힘"); // 자동: 확정 원인
  await lead.locator(".fd-ex").scrollIntoViewIfNeeded();
  await snap(lead, info, "X3-lead-final-exception");
  await pause(lead);
  await lead.locator(".lbar button.lbtn", { hasText: "승인" }).click();
  await pause(lead);
  await lead.locator(".lmdl button.lbtn", { hasText: "승인" }).click();
  await expect(lead.locator(".lempty")).toHaveText("승인 대기 보고서가 없습니다");
  // 승인 = 정비 이력 원본 층에 같이(record.exception_record)
  expect(psql("select record->'exception_record'->>'situation' from knowledge.history_records where source = 'approved_report'")).toBe(situation);
  expect(psql("select string_agg(i->>'kind', ',') from knowledge.history_records, jsonb_array_elements(record->'exception_record'->'items') i where source = 'approved_report'")).toBe("missed,new_exception"); // 약속 v9 3절 기록 이름
  expect(psql("select record->'exception_record'->'context'->>'equipment_id' from knowledge.history_records where source = 'approved_report'")).toBe("M-01");
  if (process.env.SHOT_DIR) {
    // D-503 2: 이력 원본 층에 실제로 저장된 꼴 한 건
    const real = psql("select record->'exception_record' from knowledge.history_records where source = 'approved_report'");
    writeFileSync(path.join(process.env.SHOT_DIR, "real-exception-record.json"), JSON.stringify(JSON.parse(real), null, 1));
  }
  g.check(info);
  lg.check(info);
});
