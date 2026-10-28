// EV-009(D-444 #18 · D-446 ⑤): 파트장 '사람 판단' — ML 길 후보(시험 DB에 넣음) → 알람으로 올림 → 정비자 홈 · 알람 화면 / 문제없음 → 목록에서 빠짐.
// 후보는 ML 길(C1A15_ALARM=ml)에서만 생겨 시험 스택(경계 길)에는 없음 — 서버 시험(test_human_judge)이 만드는 꼴 그대로 넣는다.

import { mkdirSync } from "node:fs";
import path from "node:path";
import { expect, test, type Browser, type Page, type TestInfo } from "@playwright/test";
import { login, loginLead, psql, resetOps, shot } from "./helpers";

const NORMAL = { air_temperature_k: 300.0, process_temperature_k: 310.0, rotational_speed_rpm: 1500.0, torque_nm: 40.0, tool_wear_min: 100.0 };
const DERIVED = { power_w: 6283, temp_diff_k: 10.0 }; // Pack 계산 칸(가짜 Pack과 같은 식)

function candidate(reason: string, topK: unknown[]): number {
  const event = JSON.stringify({ event_id: `evt-e2e-${reason}`, sensor_snapshot: NORMAL, sensor_derived: DERIVED });
  const out = psql(
    "insert into ops.alarm_candidates (equipment_id, reason, risk, top_k, boundary_crossed, model_release, sensor_snapshot, event, event_id) " +
      `values ('M-01', '${reason}', 0.62, '${JSON.stringify(topK)}'::jsonb, false, 'c1a15-ml@e2e', '${JSON.stringify(NORMAL)}'::jsonb, '${event}'::jsonb, 'evt-e2e-${reason}') returning candidate_id`,
  );
  return Number(out.split("\n")[0]);
}

async function snap(page: Page, info: TestInfo, name: string) {
  await shot(page, info, name);
  const dir = process.env.SHOT_DIR;
  if (dir) {
    mkdirSync(dir, { recursive: true });
    await page.screenshot({ path: path.join(dir, `${name}.png`) });
  }
}

async function leadPage(browser: Browser): Promise<Page> {
  const ctx = await browser.newContext({ viewport: { width: 1280, height: 620 } });
  const page = await ctx.newPage();
  await loginLead(page);
  await expect(page.locator(".wb-side")).toBeVisible();
  return page;
}

test.beforeEach(() => {
  resetOps();
  psql("delete from ops.alarm_candidates");
});

test("사람 판단: 목록 → 확신 낮음 올림(ML 제안 증상군) → 정비자 홈 · 알람 화면 '경계 안 · 파트장이 올림' · RNF 문제없음 → 빈 목록", async ({ page, browser }, info) => {
  await login(page);
  const low = candidate("low_confidence", [{ type: "HDF", probability: 0.41, group_suggestion: "CL" }]);
  const rnf = candidate("rnf", [{ type: "RNF", probability: 0.55, group_suggestion: null }]);
  const lead = await leadPage(browser);
  await lead.locator(".wn", { hasText: "사람 판단" }).click();
  await expect(lead.locator("tr[data-candidate]")).toHaveCount(2);
  await expect(lead.locator(`tr[data-candidate="${low}"] .ch`)).toHaveText("확신 낮음");
  await expect(lead.locator(`tr[data-candidate="${rnf}"] .ch`)).toHaveText("RNF");
  await snap(lead, info, "L-judge-list");

  await lead.locator(`tr[data-candidate="${low}"] .btn`, { hasText: "알람으로 올림" }).click();
  await expect(lead.locator(".pick .dopt.sel b")).toHaveText("온도 차 저하"); // ML 1위 HDF → CL 미리 고름
  await snap(lead, info, "L-judge-pick");
  await lead.locator(".pick .btn", { hasText: "올림 저장" }).click();
  await expect(lead.locator(`tr[data-candidate="${low}"]`)).toHaveCount(0);
  expect(psql(`select status from ops.alarm_candidates where candidate_id = ${low}`)).toBe("promoted");

  await page.goto("/");
  const card = page.locator("[data-alarm] .btn").first();
  await expect(card).toBeVisible({ timeout: 15_000 });
  await card.click();
  await page.waitForURL(/\/session\/\d+/);
  await expect(page.locator(".ai")).toContainText("경계 안 · 파트장이 올림");
  await snap(page, info, "T03-lead-promoted");

  await lead.locator(`tr[data-candidate="${rnf}"] .btn`, { hasText: "문제없음" }).click();
  await expect(lead.locator(".empty")).toHaveText("사람 판단이 필요한 기록이 없습니다");
  expect(psql(`select status from ops.alarm_candidates where candidate_id = ${rnf}`)).toBe("dismissed");
  await snap(lead, info, "L-judge-empty");
});
