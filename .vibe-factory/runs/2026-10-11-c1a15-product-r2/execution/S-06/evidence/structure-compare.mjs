// Prototype 전 화면 구조 대조(S-06 P-17 · AC-17): 기준 = packet 부록(execution/S-06/prototype-appendix) appendix.json · templates · regions.json만
// (결정 017 ③ · 020 ①). 부록 compare_rule대로 영역 상태(자기 template · 자기 selector) · Prototype 파생(자기 template · 기준 상태 selector)
// · 결정 파생(기준 template · 기준 selector, region_base)을 앱 DOM과 태그 · class 구조로 비교하고, 상태마다 대조 영역 수를 센다(점검표 C12).
import { JSDOM } from "/Users/insujo/Documents/repo/c1a15-maint-guide/node_modules/jsdom/lib/api.js";
import { readFileSync, writeFileSync, existsSync } from "node:fs";
const [, , APPX, DOM, OUT] = process.argv; // APPX = 부록 폴더
const ax = JSON.parse(readFileSync(`${APPX}/appendix.json`, "utf-8"));
const base = JSON.parse(readFileSync(`${APPX}/regions.json`, "utf-8"));
const TPL = `${APPX}/templates`;
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
function diff(a, b) {
  const n = a.length, m = b.length, dp = Array.from({ length: n + 1 }, () => new Array(m + 1).fill(0));
  for (let i = n - 1; i >= 0; i--) for (let j = m - 1; j >= 0; j--) dp[i][j] = a[i] === b[j] ? dp[i + 1][j + 1] + 1 : Math.max(dp[i + 1][j], dp[i][j + 1]);
  const out = []; let i = 0, j = 0;
  while (i < n && j < m) { if (a[i] === b[j]) { i++; j++; } else if (dp[i + 1][j] >= dp[i][j + 1]) out.push("- " + a[i++]); else out.push("+ " + b[j++]); }
  while (i < n) out.push("- " + a[i++]); while (j < m) out.push("+ " + b[j++]);
  return out;
}
const key = (r) => `${r.page_id}--${r.state}`;
const jobs = base.map((r) => ({ ...r, template: key(r) }));
for (const [st, src] of Object.entries(ax.prototype_derived_selector_base)) // Prototype 파생: 자기 template, 기준 상태 selector
  for (const r of base.filter((x) => key(x) === src)) jobs.push({ ...r, page_id: st.split("--")[0], state: st.split("--")[1], template: st, selector_from: src });
for (const d of ax.decision_derived_states) // 결정 파생: 기준 template · selector(region_base가 있으면 그 영역만 다른 기준)
  for (const r of base.filter((x) => key(x) === d.base)) jobs.push({ ...r, page_id: d.state.split("--")[0], state: d.state.split("--")[1], template: d.region_base?.[r.region_id] ?? d.base, derived_from: d.base });
const ALT_BASE = { "T15--correct_value": { "R-PASTVIEW": "T15--precheck" } }; // 분류 근거용(S-05 X-4)
const res = [];
for (const r of jobs) {
  const k = key(r), tp = `${TPL}/${r.template}.html`, ap = `${DOM}/${k}.html`;
  if (!existsSync(tp)) { res.push({ ...r, status: "template_missing" }); continue; }
  if (!existsSync(ap)) { res.push({ ...r, status: "missing_in_app_dom" }); continue; }
  const t = doc(tp).querySelector(r.selector), a = doc(ap).querySelector(r.selector);
  if (!t) { res.push({ ...r, status: "template_missing_selector" }); continue; }
  if (!a) { res.push({ ...r, status: "missing_in_app" }); continue; }
  const d = diff(skel(t), skel(a));
  const alt = ALT_BASE[k]?.[r.region_id];
  const altDiff = alt ? diff(skel(doc(`${TPL}/${alt}.html`).querySelector(r.selector)), skel(a)) : undefined;
  res.push({ ...r, status: d.length ? "diff" : "match", diff: d, ...(alt ? { alt_compare: { template: alt, diff: altDiff } } : {}) });
}
const states = [...new Set([...ax.states.map((s) => s.state), ...ax.decision_derived_states.map((d) => d.state)])];
const perState = Object.fromEntries(states.map((s) => [s, res.filter((x) => key(x) === s).length]));
const zero = Object.entries(perState).filter(([, n]) => n === 0).map(([s]) => s); // C12
writeFileSync(OUT, JSON.stringify({ per_state_region_count: perState, zero_states: zero, rows: res }, null, 1));
const count = {}; for (const x of res) count[x.status] = (count[x.status] ?? 0) + 1;
console.log(JSON.stringify({ states: states.length, compared: res.length, base_regions: base.length, zero_states: zero, ...count }));
if (zero.length || res.some((x) => !["diff", "match"].includes(x.status))) process.exit(1);
