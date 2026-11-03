// D-538 예외 상황 기록을 사람 손 순서로: 정비자 보고서 화면 '예외 상황 기록'(선택) 두 글 → 「보고서 확정」 → 확인 창 「취소」(글 그대로)
// → 다시 확정 → 확정 뒤 칸은 읽기만 → 파트장 최종본 '6. 예외 상황 기록'(두 글 + 자동 정보 · 보기만) → 승인
// → 정비 이력 원본 층(record.exception_record)에 같이 저장.
// 0.4초 막기는 켠 채(누름 사이 0.8초). SHOT_DIR이면 화면마다 PNG(1280 × 800).

import { mkdirSync, writeFileSync } from "node:fs";
import path from "node:path";
import { expect, test, type Page, type TestInfo } from "@playwright/test";
import { guard, LEAD_PW, LEAD_URL, login, psql, resetOps, restartWithin, result, shot, toFirstCheck } from "./helpers";

test.beforeEach(() => resetOps());

const SIT = "바닥에 절삭유가 고여 있었고 필터 덮개 고정 나사 하나가 빠져 있었음";
const ACT = "나사를 새로 끼우고 필터를 교체한 뒤 바닥을 닦음";

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
  // 보고서 화면: 확정 전 확인 위 '예외 상황 기록' 칸(선택 · 두 글 · 설명 문장 0)
  const sit = page.locator('textarea[aria-label="어떤 상황이었나"]');
  const act = page.locator('textarea[aria-label="무엇을 했나"]');
  await expect(sit).toBeVisible();
  await expect(page.locator(".kh .cd-h b")).toHaveText("예외 상황 기록");
  await pause(page);
  await sit.click();
  await sit.fill(SIT);
  await pause(page);
  await act.click();
  await act.fill(ACT);
  await snap(page, info, "X1-report-exception");
  await pause(page);
  await page.locator(".cta2 .btn", { hasText: "보고서 확정" }).click();
  const dlg = page.locator('.modal[aria-label="보고서 확정"]');
  await pause(page);
  await dlg.locator(".btn", { hasText: "취소" }).click(); // 같은 화면에서 취소 → 다시(D-503 1)
  await expect(sit).toHaveValue(SIT); // 취소해도 글 그대로
  await expect(act).toHaveValue(ACT);
  await pause(page);
  await page.locator(".cta2 .btn", { hasText: "보고서 확정" }).click();
  await pause(page);
  await dlg.locator(".btn").filter({ hasText: /^확정$/ }).click();
  await expect(page.locator(".banner.ok b")).toHaveText(/^보고서를 확정했습니다/);
  await expect(sit).toHaveCount(0);
  await expect(page.locator(".kh .khv")).toHaveText([SIT, ACT]); // 확정 뒤엔 읽기만
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
  await expect(lead.locator(".fd-ex td").nth(0)).toHaveText(SIT);
  await expect(lead.locator(".fd-ex td").nth(1)).toHaveText(ACT);
  await expect(lead.locator(".fd-ex td").nth(5)).toHaveText("4.3 흡기 필터 육안 점검"); // 자동: AI 첫 안내
  await expect(lead.locator(".fd-ex td").nth(6)).toHaveText("냉각 필터 막힘"); // 자동: 확정 원인
  await lead.locator(".fd-ex").scrollIntoViewIfNeeded();
  await snap(lead, info, "X3-lead-final-exception");
  await pause(lead);
  await lead.locator(".lbar button.lbtn", { hasText: "승인" }).click();
  await pause(lead);
  await lead.locator(".lmdl button.lbtn", { hasText: "승인" }).click();
  await expect(lead.locator(".lempty")).toHaveText("승인 대기 보고서가 없습니다");
  // 승인 = 정비 이력 원본 층에 같이(record.exception_record)
  expect(psql("select record->'exception_record'->>'situation' from knowledge.history_records where source = 'approved_report'")).toBe(SIT);
  expect(psql("select record->'exception_record'->'context'->>'equipment_id' from knowledge.history_records where source = 'approved_report'")).toBe("M-01");
  if (process.env.SHOT_DIR) {
    // D-503 2: 이력 원본 층에 실제로 저장된 꼴 한 건
    const real = psql("select record->'exception_record' from knowledge.history_records where source = 'approved_report'");
    writeFileSync(path.join(process.env.SHOT_DIR, "real-exception-record.json"), JSON.stringify(JSON.parse(real), null, 1));
  }
  g.check(info);
  lg.check(info);
});
