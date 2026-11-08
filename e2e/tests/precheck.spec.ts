// D-619 사전 점검 후보를 사람 손 순서로 — D-650 덧1 A안: 시연 첫 상태 예시 줄 = 패턴 B만(A · C 줄 0).
// 담당 홈 B 카드 1장(첫 상태부터) → tech.kim M-01 예외 → 파트장 승인 → 새 배포 뒤에도 A 0(덮개 이어짐 1건 < 3) · B 그대로
// → 근거 보기 → [이번엔 제외] 이유 → 같은 화면 다시 열기.
// 0.4초 막기는 켠 채(누름 사이 0.8초). SHOT_DIR이면 화면마다 PNG(1280 × 800).

import { mkdirSync } from "node:fs";
import path from "node:path";
import { expect, test, type Page, type TestInfo } from "@playwright/test";
import {
  confirmReportModal,
  demoHistory,
  demoHistoryInput,
  guard,
  login,
  loginLead,
  psql,
  resetOps,
  restartWithin,
  shot,
  toFirstCheck,
} from "./helpers";

const DEPLOY = process.env.C1A15_DEPLOY_URL ?? "http://127.0.0.1:18796";
const TEXT = "점검 필터 덮개 고정 나사를 손으로 확인. 조치 나사를 새로 끼움";
const pause = (p: Page) => p.waitForTimeout(800);

async function snap(page: Page, info: TestInfo, name: string) {
  await shot(page, info, name);
  const dir = process.env.SHOT_DIR;
  if (dir) {
    mkdirSync(dir, { recursive: true });
    await page.screenshot({ path: path.join(dir, `${name}.png`) });
  }
}

async function revision(value: string) {
  const r = await fetch(`${DEPLOY}/_revision`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ revision: value }),
  });
  expect(r.status).toBe(200);
}

const NAMES: Record<string, string> = { "4.3.2": "흡기 필터 교체", "2.4.2": "공구 교체", "3.4.2": "엔코더 커넥터 재체결" };

function line(id: string, eq: string, daysAgo: number, group: string, did: string[], bad: string[], text?: string) {
  const at = new Date(Date.now() - daysAgo * 86400000);
  at.setMilliseconds(0);
  return {
    record_id: id,
    equipment_id: eq,
    occurred_at: at.toISOString(),
    symptom_group: { code: group, name: group },
    sensor_snapshot: {},
    steps: [
      ...bad.map((s) => ({ kind: "check", section: s, result: "이상" })),
      ...did.map((s) => ({ kind: "action", section: s, name: NAMES[s] })),
    ],
    outcome: { type: "원인 미상·숙련자 인계" },
    narrative: `${eq} 정비`,
    ...(text ? { exception_record: { text } } : {}),
  };
}

const LINES = [ // D-650 덧1 A안: 패턴 B(공구 교체 2.4.2 → 14일 안 교체 기록 대조 2.3 이상)만 — 번호는 예시 대본과 같음
  line("H-P008", "M-09", 60, "TW", ["2.4.2"], []),
  line("H-P009", "M-09", 48, "TW", [], ["2.3"]),
  line("H-P010", "M-10", 53, "TW", ["2.4.2"], []),
  line("H-P011", "M-10", 41, "TW", [], ["2.3"]),
  line("H-P012", "M-11", 46, "TW", ["2.4.2"], []),
  line("H-P013", "M-11", 34, "TW", [], ["2.3"]),
  line("H-P014", "M-12", 40, "TW", ["2.4.2"], []),
  line("H-P015", "M-14", 33, "TW", ["2.4.2"], []),
  line("H-P016", "M-04", 4, "TW", ["2.4.2"], []),
];

test.beforeEach(async () => {
  resetOps();
  await revision("sha256:e2e-first");
  demoHistory("precheck-remove");
  demoHistory("add");
  demoHistoryInput(LINES.map((l) => JSON.stringify(l)).join("\n"), "precheck-add");
});

test.afterEach(() => {
  demoHistory("precheck-remove");
  demoHistory("remove");
});

async function approveException(page: Page, lead: Page) {
  await toFirstCheck(page, "DEMO-01");
  await pause(page);
  await page.locator(".refs .lk", { hasText: "점검 바꾸기" }).click();
  const sw = page.locator('.modal[aria-label="점검 바꾸기"]');
  await pause(page);
  await sw.locator(".swc.swx").click();
  await pause(page);
  await sw.locator(".swc", { hasText: "바로 조치" }).click();
  await pause(page);
  await page.locator(".act .btn", { hasText: "조치 완료" }).click();
  await restartWithin(page);
  await pause(page);
  await page.locator(".choice2 .btn", { hasText: "경계 이내" }).click();
  const dlg = page.locator('.modal[aria-label="예외 상황 기록"]');
  const ta = dlg.getByLabel("예외 글", { exact: true });
  await ta.click();
  await ta.fill(TEXT);
  await pause(page);
  await dlg.locator(".exa .btn", { hasText: "AI 나눔" }).click();
  const rows = dlg.locator('[data-part="ex-items"] .exi');
  await expect(rows).toHaveCount(1);
  await pause(page);
  await rows.locator(".exb .btn", { hasText: "아님" }).click();
  await pause(page);
  await dlg.locator(".mb .btn", { hasText: "보고서에 적용" }).click();
  await expect(dlg).toHaveCount(0);
  await pause(page);
  await confirmReportModal(page);
  await loginLead(lead);
  await lead.locator("tr[data-report] button.lbtn", { hasText: "검토" }).click();
  await pause(lead);
  await lead.locator(".lbar button.lbtn", { hasText: "승인" }).click();
  await pause(lead);
  await lead.locator(".lmdl button.lbtn", { hasText: "승인" }).click();
  await expect(lead.locator(".lempty").first()).toBeVisible();
}

test("사전 점검 후보(A안): B 한 장 첫 상태부터 → 승인 → 새 배포 뒤에도 A 0 · B 그대로 → 근거 보기 → 이번엔 제외 → 다시 열기(사람 손 순서)", async ({ page, browser }, info) => {
  test.setTimeout(180000);
  const g = guard(page);
  const jung = await (await browser.newContext({ viewport: { width: 1280, height: 800 } })).newPage();
  const lead = await (await browser.newContext({ viewport: { width: 1280, height: 800 } })).newPage();
  await login(jung, "tech.jung"); // 시험 자료의 M-04 담당(시연 첫 상태는 김 정비 · 데이터만 다름)
  const cards = jung.locator(".pck");
  await expect(cards).toHaveCount(1);
  const b = jung.locator('.pck[data-precheck="B"]');
  await expect(b.locator(".pck-d")).toHaveText("M-04 · 4일 전 공구 교체(2.4.2)");
  await expect(b.locator(".pck-n")).toHaveText(
    "같은 조건 사례 5건 중 3건이 14일 안에 마모 카운터 미초기화로 이어졌고, 2건은 이상 없었습니다",
  );
  await snap(jung, info, "P1-home-before");

  await login(page);
  await expect(page.locator(".pck")).toHaveCount(0); // 내 설비 후보가 아님
  await approveException(page, lead);
  await jung.reload();
  await expect(cards).toHaveCount(1);

  await revision("sha256:e2e-next");
  await jung.waitForTimeout(12000); // 홈 다시 읽기 두 주기(5초)를 넘겨 기다림 — 그래도 A는 뜨지 않음
  await expect(jung.locator('.pck[data-precheck="A"]')).toHaveCount(0); // 덮개 이어짐 = M-01 한 건뿐(< 3)
  await expect(cards).toHaveCount(1);
  await expect(b.locator(".pck-n")).toContainText("5건 중 3건");
  await snap(jung, info, "P2-home-after");

  await pause(jung);
  await b.locator(".lk", { hasText: "근거 보기" }).click();
  const dlg = jung.locator('.modal[aria-label="과거에 같은 순서로 이어진 사례"]');
  await expect(dlg.locator(".pcs")).toHaveText("살펴볼 곳 · 마모 카운터 · 교체 기록");
  await expect(dlg.locator(".pcb")).toHaveCount(5);
  await snap(jung, info, "P3-basis");
  await pause(jung);
  await dlg.locator(".btn", { hasText: "닫기" }).click();

  await pause(jung);
  await b.locator(".pck-b .btn", { hasText: "이번엔 제외" }).click();
  const skip = jung.locator('.modal[aria-label="이번엔 제외"]');
  await expect(skip.locator(".btn", { hasText: "저장" })).toHaveClass(/dis/);
  await skip.getByLabel("이유").fill("이번 주 교체 예정");
  await pause(jung);
  await skip.locator(".btn", { hasText: "저장" }).click();
  await expect(b.locator(".pck-m")).toHaveText(/^이번엔 제외 · \d\d:\d\d · 이번 주 교체 예정$/);
  await jung.reload(); // 같은 화면 다시 열기: 기록 · 건수 그대로
  await expect(b.locator(".pck-m")).toHaveText(/^이번엔 제외 · /);
  await expect(b.locator(".pck-n")).toContainText("5건 중 3건");
  await snap(jung, info, "P4-marked");
  expect(psql("select string_agg(actor || ' ' || action || ' ' || target, ',' order by audit_id) from ops.audit_log where action in ('precheck_look', 'precheck_skip')")).toBe(
    "tech.jung precheck_skip precheck:B:H-P016",
  );
  g.check(info);
});
