// EV-007(D-422 · D-423): 사용자 리허설에서 찾은 결함 — '점검 시작'을 빠르게 여러 번 누르면 알람 · 잠금 · 사전 확인을 지나감.
// 이 시험만 새 화면 직후 0.4초 누름 무시를 켠 채로(login guardOff=false) 사람처럼 같은 자리를 빠르게 누른다.

import { expect, test, type Page } from "@playwright/test";
import { alarm, login, psql, resetOps, TECH_PW } from "./helpers";

test.beforeEach(() => resetOps());

/** 같은 자리를 사람 손 빠르기(약 0.1초 간격)로 n번 누른다. */
async function rapid(page: Page, sel: string, n = 3) {
  const box = await page.locator(sel).first().boundingBox();
  if (!box) throw new Error(`버튼 없음: ${sel}`);
  for (let i = 0; i < n; i++) {
    await page.mouse.click(box.x + box.width / 2, box.y + box.height / 2);
    await page.waitForTimeout(100);
  }
}

test("빠른 세 번 누름: 홈 '점검 시작' → 알람 화면에 머묾 · 알람 '진단 보기' → 진단 화면에 머묾 · 사전 확인은 값 없이 안 넘어감", async ({ page }) => {
  await login(page, "tech.kim", TECH_PW, false);
  const id = alarm("DEMO-01");
  await expect(page.locator(`[data-alarm="${id}"] .btn`)).toBeVisible({ timeout: 15_000 });

  await rapid(page, `[data-alarm="${id}"] .btn`);
  await page.waitForURL(/\/session\/\d+/);
  await page.waitForTimeout(1500); // 늦게 온 응답 · 다음 화면까지 기다려 봄
  await expect(page.locator(".cta .btn", { hasText: "진단 보기" })).toBeVisible(); // 알람 화면(센서 · 경계)을 지나치지 않음
  await expect(page.getByText("잠금 완료", { exact: true })).toHaveCount(0);
  expect(psql(`select count(*) from ops.diag_sessions where alarm_id = ${id}`)).toBe("1");

  await rapid(page, ".cta .btn");
  await page.waitForTimeout(1500);
  await expect(page.locator(".nx .btn", { hasText: "점검 시작" })).toBeVisible(); // 진단 화면에서 멈춤
  await expect(page.getByText("잠금 완료", { exact: true })).toHaveCount(0);
  const sid = Number(/\/session\/(\d+)/.exec(page.url())![1]);
  expect(psql(`select count(*) from ops.session_events where session_id = ${sid} and type = 'alarm_ack'`)).toBe("1");

  await page.waitForTimeout(500);
  await page.locator(".nx .btn").click();
  await page.waitForTimeout(500);
  await page.getByText("잠금 완료", { exact: true }).click();
  const done = page.locator(".btn", { hasText: "사전 확인 완료" });
  await expect(done).toHaveClass(/dis/); // 값 없으면 잠김
  await page.waitForTimeout(500);
  await rapid(page, ".btn:has-text('사전 확인 완료')");
  await page.waitForTimeout(1000);
  await expect(done).toBeVisible(); // 그대로 사전 확인 화면
  expect(psql(`select count(*) from ops.session_events where session_id = ${sid} and type = 'precheck_done'`)).toBe("0");
});
