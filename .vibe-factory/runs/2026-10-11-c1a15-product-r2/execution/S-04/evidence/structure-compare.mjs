// Prototype 구조 대조(S-04: 기준 = packet 부록 templates · regions, 결정 017 ③): regions.json의 상태 · 영역 selector마다 template과 앱 DOM의 구조(태그 · class 순서)를 비교한다.
import { JSDOM } from "/Users/insujo/Documents/repo/c1a15-maint-guide/node_modules/jsdom/lib/api.js";
import { readFileSync, writeFileSync, existsSync } from "node:fs";
const [, , TPL, DOM, REGIONS, OUT] = process.argv;
const regions = JSON.parse(readFileSync(REGIONS, "utf-8"));
const doc = (p) => new JSDOM(readFileSync(p, "utf-8")).window.document;
function skel(el, depth = 0, out = []) {
  for (const c of el.children) {
    const tag = c.tagName.toLowerCase();
    const cls = [...c.classList].filter((x) => x).sort().join(".");
    out.push(`${depth}:${tag}${cls ? "." + cls : ""}`);
    if (tag !== "svg") skel(c, depth + 1, out);
  }
  return out;
}
function diff(a, b) { // LCS 기반 차이(template a → 앱 b)
  const n = a.length, m = b.length, dp = Array.from({ length: n + 1 }, () => new Array(m + 1).fill(0));
  for (let i = n - 1; i >= 0; i--) for (let j = m - 1; j >= 0; j--) dp[i][j] = a[i] === b[j] ? dp[i + 1][j + 1] + 1 : Math.max(dp[i + 1][j], dp[i][j + 1]);
  const out = []; let i = 0, j = 0;
  while (i < n && j < m) { if (a[i] === b[j]) { i++; j++; } else if (dp[i + 1][j] >= dp[i][j + 1]) out.push("- " + a[i++]); else out.push("+ " + b[j++]); }
  while (i < n) out.push("- " + a[i++]); while (j < m) out.push("+ " + b[j++]);
  return out;
}
// 파생 상태(regions.json에 없음): 원본 상태의 영역 selector로 대조(Prototype v17 derived_states — 구조 보존)
const DERIVED = { "L04--call_detail_d": "L04--call_detail", "T11--handover_sent": "T11--unable_repeat" }; // S-04: D등급 호출 답하기 · 결정 018 ④ 인계 보냄(부록 v2 derived_states)
for (const [derived, base] of Object.entries(DERIVED)) {
  const [bp, bs] = base.split("--");
  for (const r of regions.filter((x) => x.page_id === bp && x.state === bs)) regions.push({ ...r, page_id: derived.split("--")[0], state: derived.split("--")[1], derived_from: base });
}
const BASE_ONLY = new Set(["T11--unable_repeat"]); // 부록 v2: 인계 보낸 화면(T11 / handover_sent)의 기준
const res = [];
for (const r of regions) {
  const key = `${r.page_id}--${r.state}`;
  const tp = `${TPL}/${r.derived_from ?? key}.html`, ap = `${DOM}/${key}.html`; // 파생 상태는 원본 template
  if (!existsSync(tp)) continue; // 파트장 앱 · 범위 밖 상태
  if (BASE_ONLY.has(key)) { res.push({ ...r, status: "base_only" }); continue; } // 파생 대조의 기준으로만 실은 상태(그 화면 자체는 S-03에서 대조)
  if (!existsSync(ap)) { res.push({ ...r, status: "not_in_slice" }); continue; }
  const t = doc(tp).querySelector(r.selector), a = doc(ap).querySelector(r.selector);
  if (!t) { res.push({ ...r, status: "template_missing_selector" }); continue; }
  if (!a) { res.push({ ...r, status: "missing_in_app" }); continue; }
  const d = diff(skel(t), skel(a));
  res.push({ ...r, status: d.length ? "diff" : "match", diff: d });
}
writeFileSync(OUT, JSON.stringify(res, null, 1));
const count = {}; for (const x of res) count[x.status] = (count[x.status] ?? 0) + 1;
console.log(JSON.stringify(count));
for (const x of res.filter((x) => x.status !== "match")) console.log(x.page_id, x.state, x.region_id, x.status, (x.diff ?? []).slice(0, 8).join(" | "));
