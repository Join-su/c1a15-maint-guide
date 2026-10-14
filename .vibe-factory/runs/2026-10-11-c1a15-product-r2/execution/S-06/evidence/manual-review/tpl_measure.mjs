// 부록 template T06--b_precheck를 앱 CSS로 1080 × 740에 그려 같은 값을 잰다(CO-31 비교 — 기준은 packet 부록).
import { chromium } from "/Users/insujo/Documents/repo/c1a15-maint-guide/node_modules/playwright/index.mjs";
import { readFileSync, readdirSync, writeFileSync } from "node:fs";
const [, , APPX, OUT] = process.argv; const ROOT = "/Users/insujo/Documents/repo/c1a15-maint-guide";
const css = readdirSync(`${ROOT}/apps/tech/dist/assets`).filter((f) => f.endsWith(".css")).map((f) => readFileSync(`${ROOT}/apps/tech/dist/assets/${f}`, "utf-8")).join("\n");
const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1080, height: 740 } });
await p.setContent(`<!doctype html><html><head><meta charset="utf-8"><style>${css}</style></head><body>${readFileSync(`${APPX}/templates/T06--b_precheck.html`, "utf-8")}</body></html>`);
await p.waitForTimeout(300);
const m = await p.evaluate(() => { const r = (e) => e.getBoundingClientRect(); const body = document.querySelector(".ap-body"); const li = [...document.querySelectorAll(".proc li")]; const ck = [...document.querySelectorAll(".act.pre .ck")];
  return { proc_steps: li.length, proc_row_px: li.map((e) => Math.round(r(e).height)), proc_gap_px: li.slice(1).map((e, i) => Math.round(r(e).top - r(li[i]).bottom)), proc_font: li[0] ? getComputedStyle(li[0]).fontSize : null, ck_row_px: ck.map((e) => Math.round(r(e).height)), body_client_height: body.clientHeight, body_scroll_height: body.scrollHeight, overflows: body.scrollHeight > body.clientHeight + 1 }; });
writeFileSync(`${OUT}/CO-31-T06-b_precheck-template.png`, await p.locator(".ap").screenshot());
console.log(JSON.stringify(m)); await b.close();
