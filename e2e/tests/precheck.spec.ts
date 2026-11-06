// D-619 사전 점검 후보를 사람 손 순서로: 예시 줄 · 시연 줄 → tech.jung 홈 B · C 카드(A 없음) → tech.kim M-01 예외 → 파트장 승인
// → 승인만으로는 A 없음 → 배포 revision이 바뀐 뒤 다음 주기에 A 5건 중 3건 → 근거 보기 → [살펴봄] → 같은 화면 다시 열기 → [이번엔 제외] 이유.
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

const LINES = [
  line("H-P001", "M-05", 60, "CL", ["4.3.2"], []),
  line("H-P002", "M-05", 55, "CL", [], [], "필터 덮개 고정 볼트가 풀려 있었음"),
  line("H-P003", "M-06", 50, "CL", ["4.3.2"], []),
  line("H-P004", "M-06", 45, "CL", [], [], "필터 덮개 고정 볼트가 풀려 있었음"),
  line("H-P005", "M-07", 40, "CL", ["4.3.2"], []),
  line("H-P006", "M-08", 33, "CL", ["4.3.2"], []),
  line("H-P007", "M-04", 2, "CL", ["4.3.2"], []),
  line("H-P008", "M-09", 60, "TW", ["2.4.2"], []),
  line("H-P009", "M-09", 48, "TW", [], ["2.3"]),
  line("H-P010", "M-10", 53, "TW", ["2.4.2"], []),
  line("H-P011", "M-10", 41, "TW", [], ["2.3"]),
  line("H-P012", "M-11", 46, "TW", ["2.4.2"], []),
  line("H-P013", "M-11", 34, "TW", [], ["2.3"]),
  line("H-P014", "M-12", 40, "TW", ["2.4.2"], []),
  line("H-P015", "M-14", 33, "TW", ["2.4.2"], []),
  line("H-P016", "M-04", 4, "TW", ["2.4.2"], []),
  line("H-P017", "M-15", 60, "PW", ["3.4.2"], []),
  line("H-P018", "M-15", 55, "PW", [], ["3.3"]),
  line("H-P019", "M-16", 53, "PW", ["3.4.2"], []),
  line("H-P020", "M-16", 48, "PW", [], ["3.3"]),
  line("H-P021", "M-17", 46, "PW", ["3.4.2"], []),
  line("H-P022", "M-17", 41, "PW", [], ["3.3"]),
  line("H-P023", "M-18", 40, "PW", ["3.4.2"], []),
  line("H-P024", "M-19", 33, "PW", ["3.4.2"], []),
  line("H-P025", "M-04", 3, "PW", ["3.4.2"], []),
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

test("사전 점검 후보: B만 → 승인 → 새 배포 뒤 A 5건 중 3건 → 근거 보기 → 살펴봄 → 다시 열기 → 이번엔 제외(사람 손 순서)", async ({ page, browser }, info) => {
  test.setTimeout(180000);
  const g = guard(page);
  const jung = await (await browser.newContext({ viewport: { width: 1280, height: 800 } })).newPage();
  const lead = await (await browser.newContext({ viewport: { width: 1280, height: 800 } })).newPage();
  await login(jung, "tech.jung");
  const cards = jung.locator(".pck");
  await expect(cards).toHaveCount(2);
  await expect(cards.first()).toHaveAttribute("data-precheck", "B");
  await expect(cards.first().locator(".pck-d")).toHaveText("M-04 · 4일 전 공구 교체(2.4.2)");
  await expect(cards.first().locator(".pck-n")).toHaveText(
    "같은 조건 사례 5건 중 3건이 14일 안에 마모 카운터 미초기화로 이어졌고, 2건은 이상 없었습니다",
  );
  await snap(jung, info, "P1-home-before");

  await login(page);
  await expect(page.locator(".pck")).toHaveCount(0); // 내 설비 후보가 아님
  await approveException(page, lead);
  await jung.reload();
  await expect(cards).toHaveCount(2); // 승인만으로는 A 없음(KG 반영 전)

  await revision("sha256:e2e-next");
  const a = jung.locator('.pck[data-precheck="A"]');
  await expect(a).toHaveCount(1, { timeout: 15000 }); // 화면 다시 열기 없이 다음 주기
  await expect(a.locator(".pck-d")).toHaveText("M-04 · 2일 전 흡기 필터 교체(4.3.2)");
  await expect(a.locator(".pck-n")).toHaveText(
    "같은 조건 사례 5건 중 3건이 7일 안에 필터 덮개 고정 문제로 이어졌고, 2건은 이상 없었습니다",
  );
  await expect(cards).toHaveCount(3);
  await expect(cards.first()).toHaveAttribute("data-precheck", "A"); // 새로 뜬 A가 맨 위
  for (let i = 0; i < 3; i++) await expect(cards.nth(i)).toBeInViewport({ ratio: 1 }); // 카드 셋이 한 화면에(1280 × 800)
  await snap(jung, info, "P2-home-after");

  await pause(jung);
  await a.locator(".lk", { hasText: "근거 보기" }).click();
  const dlg = jung.locator('.modal[aria-label="과거에 같은 순서로 이어진 사례"]');
  await expect(dlg.locator(".pcs")).toHaveText("살펴볼 곳 · 필터 덮개 고정");
  await expect(dlg.locator(".pcb")).toHaveCount(5);
  await expect(dlg.locator(".pcb", { hasText: "M-01" })).toHaveText(/M-01 · .+ · \d일 뒤 이어짐/);
  await snap(jung, info, "P3-basis");
  await pause(jung);
  await dlg.locator(".btn", { hasText: "닫기" }).click();

  await pause(jung);
  await a.locator(".pck-b .btn", { hasText: "살펴봄" }).click();
  await expect(a.locator(".pck-m")).toHaveText(/^살펴봄 · \d\d:\d\d$/);
  await jung.reload(); // 같은 화면 다시 열기: 기록 · 건수 그대로
  await expect(a.locator(".pck-m")).toHaveText(/^살펴봄 · /);
  await expect(a.locator(".pck-n")).toContainText("5건 중 3건");

  const b = jung.locator('.pck[data-precheck="B"]');
  await pause(jung);
  await b.locator(".pck-b .btn", { hasText: "이번엔 제외" }).click();
  const skip = jung.locator('.modal[aria-label="이번엔 제외"]');
  await expect(skip.locator(".btn", { hasText: "저장" })).toHaveClass(/dis/);
  await skip.getByLabel("이유").fill("이번 주 교체 예정");
  await pause(jung);
  await skip.locator(".btn", { hasText: "저장" }).click();
  await expect(b.locator(".pck-m")).toHaveText(/^이번엔 제외 · \d\d:\d\d · 이번 주 교체 예정$/);
  await snap(jung, info, "P4-marked");
  expect(psql("select string_agg(actor || ' ' || action || ' ' || target, ',' order by audit_id) from ops.audit_log where action in ('precheck_look', 'precheck_skip')")).toBe(
    "tech.jung precheck_look precheck:A:H-P007,tech.jung precheck_skip precheck:B:H-P016",
  );
  g.check(info);
});
