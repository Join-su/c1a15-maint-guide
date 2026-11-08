// 사람 리허설 피드백(11-08) F1 · F8 · F2 — 진단 화면 숫자의 출처와 첫 점검을 고른 셈을 글로 보인다. 셈 손 0(표시 · 글만).
// 확률 = Pack 판정 출력 probabilities(원인 확률 셈: 이 설비의 지난 같은 알람 기록에서 원인별 비율) · 오른쪽 수 = evidence(비슷한 기록 상위 10건 중 그 원인).
// 첫 점검 = A · B 등급 점검 중 '원인 확률 ÷ 걸리는 분'이 가장 큰 것(rules.best_pick).

import { cleanup, render } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import type { SessionWithPreview } from "@c1a15/ui";
import { DiagnosisScreen } from "../screens/Diagnosis";

const fx = import.meta.glob("./fixtures/*.json", { eager: true, import: "default" }) as Record<string, unknown>;
const load = (name: string) => structuredClone(fx[`./fixtures/${name}.json`]) as SessionWithPreview;
const texts = (root: ParentNode, sel: string) => [...root.querySelectorAll(sel)].map((e) => e.textContent?.trim() ?? "");

// 리허설 화면 그대로의 숫자(img-01 M-01 · img-09 M-03)
function shot(probabilities: Record<string, number>): SessionWithPreview {
  const s = load("session-before-lock");
  s.probabilities = probabilities;
  s.evidence = { "CL-1": 4, "CL-2": 0, "CL-3": 6, "CL-4": 0 };
  s.preview = { ...s.preview, reason: `냉각 필터 막힘 가능성이 ${probabilities["CL-1"]}%로 가장 높고, 4.3절 점검은 약 3분 · A등급입니다.` };
  return s;
}
const M01 = { "CL-1": 40, "CL-2": 20, "CL-3": 20, "CL-4": 20 };
const M03 = { "CL-1": 100, "CL-2": 0, "CL-3": 0, "CL-4": 0 };

afterEach(cleanup);

describe("F1 · F8 원인 후보 순위: 확률과 오른쪽 수의 출처가 다름을 글로", () => {
  it("오른쪽 수 = '비슷한 기록 n건' · 순위 아래 한 줄이 두 숫자의 출처를 말함 · '근거 n' 글자 0", () => {
    const { container } = render(<DiagnosisScreen s={shot(M01)} onRecord={() => {}} onStart={() => {}} />);
    expect(texts(container, ".rk .rs")).toEqual(["비슷한 기록 4건", "비슷한 기록 0건", "비슷한 기록 6건", "비슷한 기록 0건"]);
    expect(texts(container, ".rk .rv")).toEqual(["40%", "20%", "20%", "20%"]);
    const note = container.querySelector('[data-part="rank-source"]')?.textContent ?? "";
    expect(note).toBe("확률: 이 설비의 지난 같은 알람 기록에서 원인별 비율 · 비슷한 기록: 비슷한 과거 기록 상위 10건 중 그 원인 수");
    const rank = container.querySelector(".cd")!.textContent ?? "";
    expect(rank).not.toMatch(/근거 \d/);
    expect(container.querySelector('[data-part="rank-full"]')).toBeNull(); // 100%가 없으면 까닭 줄 0
  });

  it("100%가 되면 까닭 한 줄: 이 설비의 지난 같은 알람 기록이 모두 그 원인", () => {
    const { container } = render(<DiagnosisScreen s={shot(M03)} onRecord={() => {}} onStart={() => {}} />);
    expect(texts(container, ".rk .rv")).toEqual(["100%", "0%", "0%", "0%"]);
    expect(container.querySelector('[data-part="rank-full"]')?.textContent).toBe(
      "100%인 까닭: 이 설비의 지난 같은 알람 기록이 모두 이 원인(냉각 필터 막힘)이었습니다.",
    );
  });

  it("지난 화면(T15)도 같은 글 · 화면 글에 내부 번호 0", () => {
    const { container } = render(<DiagnosisScreen s={shot(M03)} onRecord={() => {}} onStart={() => {}} past />);
    expect(container.querySelector('[data-part="rank-source"]')).not.toBeNull();
    expect(container.querySelector('[data-part="rank-full"]')).not.toBeNull();
    expect(container.textContent ?? "").not.toMatch(/D-\d|F\d\b/);
  });
});

describe("F2 이 점검을 고른 이유: 고르는 셈을 한 줄로", () => {
  it("지시 카드: 셈(원인 확률 ÷ 걸리는 분)과 이 점검이 1순위 원인을 보는 점검임을 보임 · 이유 글은 그대로 첫 줄", () => {
    const s = shot(M01);
    const { container } = render(<DiagnosisScreen s={s} onRecord={() => {}} onStart={() => {}} />);
    expect(container.querySelector(".why span")?.textContent).toBe(s.preview.reason);
    expect(container.querySelector('[data-part="pick-rule"]')?.textContent).toBe(
      "고르는 셈: A · B 등급 점검 중 '원인 확률 ÷ 걸리는 분'이 가장 큰 것 — 냉각 필터 막힘 40% ÷ 약 3분. " +
        "흡기 필터 육안 점검 = 냉각 필터 막힘 확인 점검(매뉴얼 4.3절)",
    );
  });

  it("B 등급(체크리스트 뒤 지시)도 같은 줄 · 분을 모르면 숫자 부분만 뺌", () => {
    const s = shot(M01);
    s.preview = { ...s.preview, kind: "instruct_after_checklist", grade: "B", minutes: null };
    const { container } = render(<DiagnosisScreen s={s} onRecord={() => {}} onStart={() => {}} />);
    expect(container.querySelector('[data-part="pick-rule"]')?.textContent).toBe(
      "고르는 셈: A · B 등급 점검 중 '원인 확률 ÷ 걸리는 분'이 가장 큰 것. 흡기 필터 육안 점검 = 냉각 필터 막힘 확인 점검(매뉴얼 4.3절)",
    );
  });

  it("호출 카드 · 진단에서 고른 점검 · 원인을 모르는 카드에는 셈 줄 0", () => {
    const fc = load("session-first-call");
    const a = render(<DiagnosisScreen s={fc} onRecord={() => {}} onStart={() => {}} />);
    expect(a.container.querySelector(".why b")?.textContent).toBe("호출이 필요한 이유");
    expect(a.container.querySelector('[data-part="pick-rule"]')).toBeNull();
    cleanup();
    const s = shot(M01);
    const picked = { ...s, preview: { ...s.preview, picked: { section: "4.4", title: "냉각 팬 분해 점검", grade: "C" } } };
    const b = render(<DiagnosisScreen s={picked} onRecord={() => {}} onStart={() => {}} />);
    expect(b.container.querySelector('[data-part="pick-rule"]')).toBeNull();
    cleanup();
    const nocause = { ...s, preview: { ...s.preview, cause: null } };
    const c = render(<DiagnosisScreen s={nocause} onRecord={() => {}} onStart={() => {}} />);
    expect(c.container.querySelector(".why span")?.textContent).toBe(s.preview.reason);
    expect(c.container.querySelector('[data-part="pick-rule"]')).toBeNull();
  });
});
