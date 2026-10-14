// Prototype 구조 대조(S-05: 기준 = packet 부록 templates · regions, 결정 017 ③ · 점검표 C4): regions.json의 상태 · 영역 selector마다 template과 앱 DOM의 구조(태그 · class 순서)를 비교한다.
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
const DERIVED = { "L04--handover_corrected": "L04--call_corrected", "L04--correction_call_detail": "L04--call_detail", "T09--draft_corrected": "T09--draft", "T10--corrected_ans_daytime": "T10--ans_daytime", "T10--corrected_ans_direct": "T10--ans_direct" }; // 부록 decision_derived_states(결정 019 ② ⑤ ① ⑧)
for (const [derived, base] of Object.entries(DERIVED)) {
  const [bp, bs] = base.split("--");
  for (const r of regions.filter((x) => x.page_id === bp && x.state === bs)) regions.push({ ...r, page_id: derived.split("--")[0], state: derived.split("--")[1], derived_from: base });
}
// Prototype 파생 상태(부록 prototype_derived_states): 자기 template이 있고 regions.json에는 영역이 없다 — 기준 상태의 영역 selector를
// 빌려 자기 template과 대조한다(점검표 C4, G5 다시 검토 때 빠진 것을 찾아 더함)
const PROTO_DERIVED = { "T15--check_b": "T15--check", "T15--call": "T15--lock", "T15--correct_value": "T15--correct" };
for (const [derived, base] of Object.entries(PROTO_DERIVED)) {
  const [bp, bs] = base.split("--");
  for (const r of regions.filter((x) => x.page_id === bp && x.state === bs && !x.derived_from)) regions.push({ ...r, page_id: derived.split("--")[0], state: derived.split("--")[1], selector_from: base });
}
const BASE_ONLY = new Set(["L04--call_detail", "T09--draft", "T10--ans_daytime", "T10--ans_direct"]); // 파생 대조의 기준으로만 실은 상태
// 결정 파생 상태의 영역별 기준(부록 v2 decision_derived_states): 정정 호출 답 화면의 왼쪽 머리는 T10 / summary_corrected
const REGION_BASE = {
  "T10--corrected_ans_daytime": { "R-CALLHEAD": "T10--summary_corrected" },
  "T10--corrected_ans_direct": { "R-CALLHEAD": "T10--summary_corrected" },
};
// 분류 근거용 대조(기준은 그대로 자기 template): 측정값 정정 창(T15 / correct_value)의 뒤 화면은 정정하는 그 기록 — 사전 확인 지난 화면(T15 / precheck)과도 대조해 적는다
const ALT_BASE = { "T15--correct_value": { "R-PASTVIEW": "T15--precheck" } };
const res = [];
for (const r of regions) {
  const key = `${r.page_id}--${r.state}`;
  const tp = `${TPL}/${REGION_BASE[key]?.[r.region_id] ?? r.derived_from ?? key}.html`, ap = `${DOM}/${key}.html`; // 파생 상태는 원본 template
  if (!existsSync(tp)) continue; // 파트장 앱 · 범위 밖 상태
  if (BASE_ONLY.has(key)) { res.push({ ...r, status: "base_only" }); continue; } // 파생 대조의 기준으로만 실은 상태(그 화면 자체는 S-03에서 대조)
  if (!existsSync(ap)) { res.push({ ...r, status: "not_in_slice" }); continue; }
  const t = doc(tp).querySelector(r.selector), a = doc(ap).querySelector(r.selector);
  if (!t) { res.push({ ...r, status: "template_missing_selector" }); continue; }
  if (!a) { res.push({ ...r, status: "missing_in_app" }); continue; }
  const d = diff(skel(t), skel(a));
  const alt = ALT_BASE[key]?.[r.region_id];
  const altDiff = alt ? diff(skel(doc(`${TPL}/${alt}.html`).querySelector(r.selector)), skel(a)) : undefined;
  res.push({ ...r, status: d.length ? "diff" : "match", diff: d, ...(alt ? { alt_compare: { template: alt, diff: altDiff } } : {}) });
}
writeFileSync(OUT, JSON.stringify(res, null, 1));
const count = {}; for (const x of res) count[x.status] = (count[x.status] ?? 0) + 1;
console.log(JSON.stringify(count));
for (const x of res.filter((x) => x.status !== "match")) console.log(x.page_id, x.state, x.region_id, x.status, (x.diff ?? []).slice(0, 8).join(" | "));
