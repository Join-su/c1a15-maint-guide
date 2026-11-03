// D-528 정비자 앱 최종안(가이드 정비자 1 ~ 13 · 반려 33 · 34쪽)을 사람 손 순서로(태블릿 1280 × 800 · 0.4초 막기 켬 · 누름 사이 0.8초):
// 홈(왼쪽 「오늘 밤 알람」 · 내 알람 한 줄) → 알람(추이 그래프 없음) → 진단 → 잠금 큰 창(단계 띠 「진단 ›」으로 갔다 돌아옴) → 사전 확인
// → 점검 → 조치 · 재가동 → 보고서 「보고서 확정」 확인 창(취소 → 다시 → 확정) → 왼쪽 완료 탭 → 파트장 반려 → 홈 반려 칸 → 「이어서 하기」
// → 보고서 오른쪽 위 반려 사유 → 고쳐 다시 확정 → 홈 최근 보고서 「최종본 보기」(정비자 14). SHOT_DIR이면 화면마다 PNG.

import { mkdirSync } from "node:fs";
import path from "node:path";
import { expect, test, type Page, type TestInfo } from "@playwright/test";
import { alarm, confirmReportModal, guard, LEAD_PW, LEAD_URL, login, resetOps, result, shot } from "./helpers";

test.beforeEach(() => resetOps());

async function snap(page: Page, info: TestInfo, name: string) {
  await shot(page, info, name);
  const dir = process.env.SHOT_DIR;
  if (dir) {
    mkdirSync(dir, { recursive: true });
    await page.screenshot({ path: path.join(dir, `${name}.png`) });
  }
}

const pause = (p: Page) => p.waitForTimeout(800);

test("정비자 최종안: 왼쪽 칸 · 한 줄 · 잠금 큰 창 · 확정 확인 창 · 반려 → 다시 확정(사람 손 순서)", async ({ page, browser }, info) => {
  const g = guard(page);
  await login(page, undefined, undefined, false); // 막기 켬
  alarm("DEMO-01");
  // 정비자 2 홈: 왼쪽 칸 · 내 알람 한 줄
  const left = page.locator('aside.n-lp[aria-label="오늘 밤 알람"]');
  await expect(left.locator("button.n-li")).toHaveCount(1);
  await expect(left.locator(".n-k")).toHaveText("냉각 계통");
  await expect(left.locator(".n-ls")).toHaveText("🚨새 알람");
  await expect(page.locator(".al .n-vals > *")).toHaveText(["냉각 계통", /^\d+\.\d K$/, "8.2 K", "경계 아래"]);
  await expect(page.locator(".safe")).toHaveText("잠금을 먼저 확인합니다");
  await snap(page, info, "T2-home");
  await pause(page);
  await page.locator(".al .btn", { hasText: "점검 시작" }).click();
  // 정비자 3 알람: 추이 그래프 · 안내 문장 없음
  await page.waitForURL(/\/session\/\d+/);
  await expect(page.locator(".tbl tr")).toHaveCount(6);
  await expect(page.locator("svg.spk")).toHaveCount(0);
  await expect(left.locator("button.n-li.on")).toHaveCount(1);
  await snap(page, info, "T3-alarm");
  await pause(page);
  await page.getByText("진단 보기").click();
  // 정비자 4 진단
  await expect(page.locator(".rk").first()).toHaveClass(/on/);
  await expect(page.locator(".hint")).toHaveCount(0);
  await snap(page, info, "T4-diagnosis");
  await pause(page);
  await page.locator(".nx .btn").click();
  // 정비자 5 잠금 큰 창 · 단계 띠 「진단 ›」만으로 돌아감
  const lock = page.locator('.lockm[role="dialog"]');
  await expect(lock.locator(".proc li")).toHaveCount(4);
  await expect(page.locator(".lockdim")).toBeVisible();
  await snap(page, info, "T5-lock");
  await pause(page);
  await page.locator('.ap-step [aria-label="진단 지난 화면"]').click();
  await expect(lock).toHaveCount(0);
  await expect(page.locator(".rk").first()).toBeVisible();
  await pause(page);
  await page.getByText("현재 단계로").click();
  await expect(lock).toBeVisible();
  await pause(page);
  await lock.getByText("잠금 완료", { exact: true }).click();
  await expect(page.locator(".lockok b")).toHaveText("잠금 확인 완료");
  await expect(page.locator(".ins-h .sm")).toHaveText("사전 확인");
  await expect(page.locator(".res .note")).toHaveCount(0);
  await expect(page.locator(".res .btn")).toHaveClass(/dis/);
  await snap(page, info, "T5-precheck");
  await page.getByLabel("기록할 값").fill("하우징 표면 52 °C");
  await pause(page);
  await page.getByText("사전 확인 완료").click();
  // 정비자 6 점검 → 9 조치 · 재가동
  await expect(page.locator(".rbtns")).toBeVisible();
  await expect(page.locator(".res .note")).toHaveCount(0);
  await snap(page, info, "T6-check");
  await pause(page); // 새 화면 직후 0.4초 누름 무시(EV-007) — 사람처럼 잠깐 뒤
  await result(page, "이상", "기름때가 필터 표면 절반 넘게 덮음");
  await pause(page);
  await page.getByText("교체 완료").click();
  // 재가동 체크리스트 셋(다 고르기 전 잠김) — 공용 restartWithin은 막기를 끈 시험용이라 여기서는 사람처럼 하나씩
  await expect(page.getByText("체크리스트 확인 후 재가동")).toHaveClass(/dis/);
  const items = page.locator(".act .ck");
  for (let i = 0; i < (await items.count()); i++) {
    await pause(page);
    await items.nth(i).click();
  }
  await pause(page);
  await page.locator(".btn", { hasText: /^재가동$/ }).click();
  await expect(page.locator(".rv-big")).toBeVisible();
  await pause(page);
  await page.locator(".choice2 .btn", { hasText: "경계 이내" }).click();
  // 정비자 12 · 13 보고서 확정 확인 창
  await expect(page.locator(".cta2 .note")).toHaveCount(0);
  await snap(page, info, "T12-report");
  await pause(page);
  await page.locator(".cta2 .btn", { hasText: "보고서 확정" }).click();
  const dlg = page.locator('.modal[aria-label="보고서 확정"]');
  await expect(dlg.locator(".mh b")).toHaveText("보고서를 확정합니까?");
  await snap(page, info, "T12-confirm-modal");
  await pause(page);
  await dlg.locator(".btn", { hasText: "취소" }).click(); // 취소는 창만 닫음
  await expect(dlg).toHaveCount(0);
  await expect(page.locator(".cd-h .ch.amber")).toHaveText("초안");
  await pause(page);
  await confirmReportModal(page);
  await expect(page.locator(".banner.ok b")).toHaveText(/^보고서를 확정했습니다 · \d\d:\d\d$/);
  await expect(page.locator(".banner.ok div")).toHaveText(/^보고서를 확정했습니다 · \d\d:\d\d$/); // 안내 문장 두 줄 뺌
  // 확정하면 왼쪽 칸도 바로 '진행 중인 알람 없음'(가이드 19쪽 — 홈 5초 주기를 기다리지 않음).
  // 위 띠는 지금 앱 그대로(세션 화면은 그 세션 알람 — 조각 2 남은 차이 1, 답장 001-zzr 받음)
  await expect(left.locator(".n-le")).toHaveText("진행 중인 알람 없음", { timeout: 2000 });
  await snap(page, info, "T13-confirmed");
  // 정비자 14 최종본: 「최종본 보기」 → 문서 · 「출력」(동작 0) 두 번 · 「보고서로」
  await pause(page);
  await page.locator(".btn", { hasText: "최종본 보기" }).click();
  await expect(page).toHaveURL(/\/report\/\d+$/);
  await expect(page.locator(".fd-h h1")).toHaveText("정비 보고서 M-01");
  await expect(page.locator(".fd-st span").last()).toHaveText("승인 대기");
  await expect(page.locator(".fdoc h2")).toHaveCount(5);
  await snap(page, info, "T14-final");
  // 결함(답장 001-zzv-1): 4번 구역 값 칸이 공용 .kv(grid)에 눌려 한 글자 폭 — 값 칸 폭 ≥ 구역 폭의 절반 · 아래까지 내린 그림
  {
    const sec4 = page.locator(".fdoc section", { hasText: "4. 조치 결과" });
    const secW = (await sec4.boundingBox())!.width;
    const tdW = (await sec4.locator("table td").first().boundingBox())!.width;
    expect(tdW).toBeGreaterThanOrEqual(secW / 2);
    await page.locator(".fd-f").scrollIntoViewIfNeeded();
    await snap(page, info, "T14-final-bottom");
  }
  await pause(page);
  await page.locator(".fbar .btn", { hasText: "출력" }).click();
  await pause(page);
  await page.locator(".fbar .btn", { hasText: "출력" }).click();
  await expect(page.locator(".fd-h h1")).toHaveText("정비 보고서 M-01");
  await pause(page);
  await page.locator(".fbar .btn", { hasText: "보고서로" }).click();
  await expect(page.locator(".cd-h .ch.green")).toHaveText("확정 · 승인 대기");
  await pause(page);
  await left.locator(".tabs button", { hasText: "완료" }).click();
  await expect(left.locator(".n-li.ro").first()).toContainText("냉각 필터 막힘");
  await expect(left.locator(".n-li.ro .ch").first()).toHaveText("승인 대기");
  await snap(page, info, "T-left-done");

  // 파트장 반려
  const lead = await (await browser.newContext({ viewport: { width: 1280, height: 800 } })).newPage();
  const lg = guard(lead);
  await lead.goto(LEAD_URL + "/");
  await lead.getByLabel("ID").fill("lead.park");
  await lead.getByLabel("비밀번호").fill(LEAD_PW);
  await pause(lead);
  await lead.locator(".lg-card button.lbtn").click();
  await pause(lead);
  await lead.locator("tr[data-report] button.lbtn", { hasText: "검토" }).click();
  await pause(lead);
  await lead.locator(".lbar button.lbtn", { hasText: "반려" }).click();
  await lead.getByLabel("반려 사유").fill("4.3 메모를 더 자세히 적어 다시 확정");
  await pause(lead);
  await lead.locator(".lmdl button.lbtn", { hasText: "반려" }).click();
  await expect(lead.locator(".lempty")).toHaveText("승인 대기 보고서가 없습니다");

  // 정비자 2(반려 33쪽) · 12(34쪽): 홈 반려 칸 → 이어서 하기 → 반려 사유 오른쪽 위 → 고쳐 다시 확정
  await pause(page);
  await page.locator(".tb-home").click();
  await expect(page.locator(".banner.bad div")).toContainText("4.3 메모를 더 자세히 적어 다시 확정");
  await expect(page.locator(".banner.bad div")).not.toContainText("이어서 하기");
  await snap(page, info, "T33-home-rejected");
  await pause(page);
  await page.locator(".btn.full", { hasText: "이어서 하기" }).click();
  await expect(page.locator(".cd-h .ch.red")).toHaveText("반려 · 고치는 중");
  await expect(page.locator('[data-part="rejection"]')).toContainText("4.3 메모를 더 자세히 적어 다시 확정");
  await snap(page, info, "T34-report-rejected");
  await pause(page);
  await page.locator('[data-field="check_path"] .ed').click();
  const ta = page.locator('[data-field="check_path"] textarea');
  await ta.fill((await ta.inputValue()).replace("이상: 기름때", "이상: 기름때가 필터 표면 절반 넘게 덮음, 뒷면도 확인"));
  await page.locator(".cd-h b", { hasText: "정비 보고서 초안" }).click();
  await pause(page);
  await confirmReportModal(page);
  await expect(page.locator(".cd-h .ch.green")).toHaveText("확정 · 승인 대기");
  await expect(page.locator('[data-part="rejection"]')).toHaveCount(0);
  await lead.reload();
  await expect(lead.locator("tr[data-report]")).toHaveCount(1);
  // 홈 「최근 내 보고서」 줄에서도 최종본 — 다시 확정 표시
  await pause(page);
  await page.locator(".tb-home").click();
  await pause(page);
  await page.locator(".rl .lk2", { hasText: "최종본 보기" }).first().click();
  await expect(page.locator(".fd-steps li").nth(1)).toContainText("정비자 다시 확정");
  await snap(page, info, "T14-final-reconfirmed");
  g.check(info);
  lg.check(info);
});

test("두 번째 점검이 열리면 왼쪽 칸도 바로 '점검 2/3' · 매뉴얼 원문 창은 가운데 · 단계 띠 밝게(가이드 10 · 12쪽, D-530 답장 001-zzt 1 · 3)", async ({ page }, info) => {
  const g = guard(page);
  await login(page, undefined, undefined, false);
  alarm("DEMO-02");
  const left = page.locator('aside.n-lp[aria-label="오늘 밤 알람"]');
  await pause(page);
  await page.locator(".al .btn", { hasText: "점검 시작" }).click();
  await page.waitForURL(/\/session\/\d+/);
  await pause(page);
  await page.getByText("진단 보기").click();
  await pause(page);
  await page.locator(".nx .btn").click();
  await pause(page);
  await page.locator(".lockm").getByText("잠금 완료", { exact: true }).click();
  await page.getByLabel("기록할 값").fill("하우징 표면 52 °C");
  await pause(page);
  await page.getByText("사전 확인 완료").click();
  await expect(page.locator(".rbtns")).toBeVisible();
  // 매뉴얼 원문 창: 가운데 · 640px 안팎 · 단계 띠는 창 뒤 어둠 위(밝게)
  await pause(page);
  await page.locator(".refs .lk", { hasText: "매뉴얼 원문" }).click();
  const box = (await page.locator('.modal.wide[aria-label^="매뉴얼 원문"]').boundingBox())!;
  expect(box.width).toBeLessThanOrEqual(660);
  expect(Math.abs(box.x + box.width / 2 - 640)).toBeLessThanOrEqual(20);
  const step = (await page.locator(".ap-step").boundingBox())!;
  const top = await page.evaluate(([x, y]) => document.elementFromPoint(x, y)?.closest(".ap-step") !== null, [step.x + 40, step.y + step.height / 2]);
  expect(top).toBe(true);
  await snap(page, info, "T10-manual");
  await pause(page);
  await page.locator(".modal.wide .btn", { hasText: "닫기" }).click();
  // 첫 점검 정상 → 두 번째 점검: 왼쪽 칸 단계도 바로(홈 5초 주기를 기다리지 않음)
  await pause(page);
  await result(page, "정상");
  await expect(page.locator(".ins-h .sm")).toHaveText(/^점검 2 \/ 최대 \d$/);
  await expect(left.locator(".n-ls")).toHaveText(/진행 중 · 점검 2\/\d$/, { timeout: 2000 });
  await snap(page, info, "T12-second-check");
  g.check(info);
});
