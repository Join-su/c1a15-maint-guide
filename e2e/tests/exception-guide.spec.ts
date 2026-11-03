// D-543 구현 2 예외 안내(파트장 승인 전)를 사람 손 순서로 · 약속 v8(D-545 덧 2): 세션 시작(start 결과 exception_guide)
// → 잠금 · 사전 확인 뒤 예외 절 먼저(가짜 배포 서버가 Pack 흉내) → 호출 화면 '예외 기록에서 온 점검' · 노하우 글 + 출처(앱 원본)
// → 「노하우 등록」 → 「취소」 → 다시 「노하우 등록」(D-503 1) → 두 칸 → 「등록」 → 다시 열면 서버 초안으로 채워짐
// → 「파트장 호출」(호출과 따로) → 보냄 배너 뒤에도 카드 그대로. 승인 뒤 예외 절 지시 · 결과는 engine 사본 갱신 뒤.
// SHOT_DIR이면 화면마다 PNG(1280 × 800).

import { mkdirSync } from "node:fs";
import path from "node:path";
import { expect, test, type Page, type TestInfo } from "@playwright/test";
import { alarm, guard, login, psql, resetOps, shot } from "./helpers";

const DEPLOY = process.env.C1A15_DEPLOY_URL ?? "http://127.0.0.1:18796";
const SIT = "바닥에 절삭유가 고여 있었고 덮개 고정 나사 하나가 빠져 있었음";
const TEXT = "흡기 필터를 교체한 뒤 사흘 안에 같은 알람이 다시 울리면, 덮개 고정 나사 네 개가 다 있는지 먼저 본다.";
const pause = (p: Page) => p.waitForTimeout(800);

async function answer(opts: Record<string, unknown>) {
  const r = await fetch(`${DEPLOY}/_answer`, { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(opts) });
  expect(r.status).toBe(200);
}

async function snap(page: Page, info: TestInfo, name: string) {
  await shot(page, info, name);
  const dir = process.env.SHOT_DIR;
  if (dir) {
    mkdirSync(dir, { recursive: true });
    await page.screenshot({ path: path.join(dir, `${name}.png`) });
  }
}

let rid = "";
test.beforeEach(async () => {
  resetOps();
  // 출처 = 앱 원본의 예외 기록 한 건(같은 설비 · 같은 증상군 생성 이력 하나에 예외 기록 칸을 잠시 붙임 — 끝나면 뺌)
  rid = psql(
    "select record_id from knowledge.history_records where equipment_id = 'M-01' and symptom_group = 'CL' " +
      "order by occurred_at desc, record_id desc limit 1",
  );
  psql(
    `update knowledge.history_records set record = record || jsonb_build_object('exception_record', ` +
      `jsonb_build_object('situation', '${SIT}', 'action', '나사를 새로 끼움')) where record_id = '${rid}'`,
  );
  await answer({
    exception_guide: {
      section: `EX-${rid}`,
      relation_id: `EX-${rid}`,
      grade: "C",
      title: "필터 덮개 고정 나사 확인",
      text: TEXT,
      steps: ["덮개 나사 확인", "빠졌으면 새로 끼움"],
      criteria: "나사 네 개 모두 체결 = 정상",
      basis: [rid],
    },
  });
});
test.afterEach(async () => {
  psql(`update knowledge.history_records set record = record - 'exception_record' where record_id = '${rid}'`);
  await answer({}); // 다른 시험은 기본 답
});

test("예외 안내: 노하우 글 + 출처 · 「노하우 등록」(취소 · 다시 · 등록 · 다시 열면 채워짐) · 「파트장 호출」 따로(사람 손 순서)", async ({ page }, info) => {
  const g = guard(page);
  await login(page);
  alarm("DEMO-01");
  await page.locator(".al .btn", { hasText: "점검 시작" }).click();
  await page.waitForURL(/\/session\/\d+/);
  await page.getByText("진단 보기").click();
  await page.locator(".nx .btn").click();
  await page.getByText("잠금 완료", { exact: true }).click();
  await page.getByLabel("기록할 값").fill("하우징 표면 52 °C");
  await pause(page);
  await page.getByText("사전 확인 완료").click();
  const left = page.locator(".g64 > .cd").first();
  await expect(left.locator(".warn-h .sm")).toHaveText("예외 기록에서 온 점검"); // 잠금 · 사전 확인 뒤 예외 절 먼저
  await expect(left.locator(".warn-h h3")).toHaveText("필터 덮개 고정 나사 확인");
  await expect(left.locator(".warn-h .tags > *")).toHaveText(["C승인 필요", `예외 기록 ${rid}`]);
  await expect(left.locator(".xkh p")).toHaveText(TEXT);
  await expect(left.locator(".xkh .xsrc")).toHaveText(new RegExp(`^출처 · 예외 기록 ${rid} · M-01 · \\d\\d-\\d\\d — 상황 '${SIT}'$`));
  await expect(left.locator(".sub")).toHaveText(["노하우", "지금까지 점검"]); // 원래 순서 다음 = v8에 칸 없음(질문 001-zzz17)
  await snap(page, info, "G1-exception-guide");
  await pause(page);
  await left.locator(".xkr .btn", { hasText: "노하우 등록" }).click();
  await expect(left.locator(".xkf")).toBeVisible();
  await expect(left.locator(".sub")).toHaveText(["노하우"]);
  await pause(page);
  await left.locator(".xkf .btn", { hasText: "취소" }).click(); // 같은 화면에서 취소 → 다시
  await expect(left.locator(".xkf")).toHaveCount(0);
  await expect(left.locator(".sub")).toHaveText(["노하우", "지금까지 점검"]);
  await pause(page);
  await left.locator(".xkr .btn", { hasText: "노하우 등록" }).click();
  const sit = left.getByLabel("어떤 상황이었나");
  const act = left.getByLabel("무엇을 했나");
  await sit.click();
  await sit.fill("덮개 고정 나사는 다 있었고, 필터 뒤 흡기 덕트 이음매가 빠져 바람이 새고 있었음");
  await pause(page);
  await act.click();
  await act.fill("덕트 이음매를 다시 끼우고 밴드를 조임");
  await snap(page, info, "G2-knowhow-form");
  await pause(page);
  const sent = page.waitForResponse((r) => r.url().endsWith("/events") && r.request().method() === "POST");
  await left.locator(".xkf .btn").filter({ hasText: /^등록$/ }).click();
  expect((await sent).status()).toBe(200);
  await expect(left.locator(".xkf")).toHaveCount(0);
  await page.reload(); // 서버에 남은 초안으로 다시 열림
  await expect(left.locator(".warn-h .sm")).toHaveText("예외 기록에서 온 점검");
  await pause(page);
  await left.locator(".xkr .btn", { hasText: "노하우 등록" }).click();
  await expect(left.getByLabel("어떤 상황이었나")).toHaveValue("덮개 고정 나사는 다 있었고, 필터 뒤 흡기 덕트 이음매가 빠져 바람이 새고 있었음");
  await expect(left.getByLabel("무엇을 했나")).toHaveValue("덕트 이음매를 다시 끼우고 밴드를 조임");
  await pause(page);
  await left.locator(".xkf .btn", { hasText: "취소" }).click();
  await pause(page);
  await page.locator(".g64 > .cd").nth(1).locator(".btn", { hasText: "파트장 호출" }).click();
  await expect(page.locator(".banner.info b")).toHaveText(/^파트장 호출을 보냈습니다 · \d\d:\d\d$/);
  await expect(left.locator(".xkh p")).toHaveText(TEXT); // 보낸 뒤에도 카드 그대로
  await snap(page, info, "G3-call-sent");
  const ev = psql("select string_agg(type, ',' order by seq) from ops.session_events where type in ('exception_draft', 'call_sent')");
  expect(ev).toBe("exception_draft,call_sent");
  g.check(info);
});
