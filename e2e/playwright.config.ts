import { defineConfig } from "@playwright/test";

// 정비자 앱 E2E(P-08 L3): compose 스택(nginx 8081)에 붙는다. scripts/verify-e2e가 스택을 띄우고 값(env)을 넘긴다.
// 브라우저는 로컬 캐시 chromium(Playwright 1.63.0 = chromium 1243)만 쓰고 내려받지 않는다. 외부 요청은 시험마다 막고 센다.
export default defineConfig({
  testDir: "tests",
  workers: 1,
  fullyParallel: false,
  timeout: 90_000,
  expect: { timeout: 8_000 },
  reporter: [["list"], ["json", { outputFile: process.env.E2E_REPORT ?? "test-results/report.json" }]],
  use: {
    baseURL: process.env.BASE_URL ?? "http://127.0.0.1:8081",
    viewport: { width: 1100, height: 760 },
    trace: "off",
    screenshot: "only-on-failure",
  },
});
