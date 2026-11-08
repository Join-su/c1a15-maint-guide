// 리허설 2 R3 · R6(A 진단 숫자 · 앱 몫, 표시 · 글만): 순위 줄 = 확률 셈에 쓴 '이 설비 기록 n건 중 k건'(Pack 판정 출력 그대로) ·
// 비슷한 과거 기록은 순위 줄에서 빼고 그 칸 이름에 '참고(다른 설비 포함) · 순위 계산에 안 씀' · 출처 줄은 새 셈(원인마다 기본 1건)을 말함.
// n · k = Pack 판정 출력 record_counts(앱 서버가 equipment_counts · total · count_scope · count_prior로 실음) · 칸이 없으면(옛 Pack · 옛 세션) 숫자 자리를 숨김 — 지어낸 숫자 0.

import { cleanup, render } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import type { SessionWithPreview } from "@c1a15/ui";
import { DiagnosisScreen } from "../screens/Diagnosis";

const fx = import.meta.glob("./fixtures/*.json", { eager: true, import: "default" }) as Record<string, unknown>;
const load = (name: string) => structuredClone(fx[`./fixtures/${name}.json`]) as SessionWithPreview;
const texts = (root: ParentNode, sel: string) => [...root.querySelectorAll(sel)].map((e) => e.textContent?.trim() ?? "");

// M-02 = Pack pack/d642 c36ec02 실제 출력(저장소 그래프 · count_equipment): 이 설비 기록 6건 4/1/1/0 · prior 1 → 50/20/20/10 · 비슷한 기록 상위 10건은 4/0/6/0
function m02(): SessionWithPreview {
  const s = load("session-before-lock");
  s.probabilities = { "CL-1": 50, "CL-2": 20, "CL-3": 20, "CL-4": 10 };
  s.evidence = { "CL-1": 4, "CL-2": 0, "CL-3": 6, "CL-4": 0 };
  Object.assign(s, { equipment_counts: { "CL-1": 4, "CL-2": 1, "CL-3": 1, "CL-4": 0 }, equipment_total: 6, count_scope: "equipment", count_prior: 1 });
  return s;
}

afterEach(cleanup);

describe("순위 줄 = 이 설비 기록 n건 중 k건 · 비슷한 기록은 순위 밖", () => {
  it("오른쪽 수 = '이 설비 기록 6건 중 k건' · '비슷한 기록' · '근거' 글자는 순위 칸에 0", () => {
    const { container } = render(<DiagnosisScreen s={m02()} onRecord={() => {}} onStart={() => {}} />);
    expect(texts(container, ".rk .rv")).toEqual(["50%", "20%", "20%", "10%"]);
    expect(texts(container, ".rk .rs")).toEqual([
      "이 설비 기록 6건 중 4건",
      "이 설비 기록 6건 중 1건",
      "이 설비 기록 6건 중 1건",
      "이 설비 기록 6건 중 0건",
    ]);
    const rank = container.querySelector(".cd")!.textContent ?? "";
    expect(rank).not.toMatch(/비슷한|근거 \d/);
  });

  it("출처 줄은 새 셈을 말함(이 설비의 지난 같은 알람 기록 · 원인마다 기본 1건) · 100% 까닭 줄 0", () => {
    const { container } = render(<DiagnosisScreen s={m02()} onRecord={() => {}} onStart={() => {}} />);
    expect(container.querySelector('[data-part="rank-source"]')?.textContent).toBe(
      "확률 = (그 원인 건수 + 1) ÷ (6 + 원인 4개) — 이 설비의 지난 같은 알람 기록 6건 기준 · 원인마다 기본 1건을 더해 기록이 적어도 100%가 되지 않음",
    );
    expect(container.querySelector('[data-part="rank-full"]')).toBeNull();
  });

  it("비슷한 과거 기록 칸 이름 = '참고(다른 설비 포함) · 순위 계산에 안 씀' · 카드는 그대로", () => {
    const s = m02();
    const { container } = render(<DiagnosisScreen s={s} onRecord={() => {}} onStart={() => {}} />);
    const head = [...container.querySelectorAll(".cd-h b")].map((b) => b.textContent);
    expect(head).toContain(`비슷한 과거 기록 ${s.similar_cards.length}건 · 참고(다른 설비 포함) · 순위 계산에 안 씀`);
    expect(container.querySelectorAll(".hcs > *").length).toBe(s.similar_cards.length);
  });

  it("n · k 칸이 없으면(옛 세션) 숫자 자리 숨김 · 출처 줄은 비율만 · 비슷한 기록 글자 0", () => {
    const s = m02();
    const old = { ...s, equipment_counts: undefined, equipment_total: undefined } as SessionWithPreview;
    const { container } = render(<DiagnosisScreen s={old} onRecord={() => {}} onStart={() => {}} />);
    expect(texts(container, ".rk .rs")).toEqual([]);
    expect(container.querySelector('[data-part="rank-source"]')?.textContent).toBe(
      "확률: 이 설비의 지난 같은 알람 기록에서 원인별 비율",
    );
    expect(container.querySelector(".cd")!.textContent ?? "").not.toMatch(/비슷한/);
  });

  it("넓혀 센 셈(scope group · Pack 실제 출력 M-ZZ): '같은 증상 전체 기록 n건 중 k건' · 출처 줄이 까닭(이 설비 기록 3건 미만)을 말함", () => {
    const s = Object.assign(m02(), { count_scope: "group", count_prior: 1, equipment_counts: { "CL-1": 57, "CL-2": 25, "CL-3": 10, "CL-4": 16 }, equipment_total: 108 });
    s.probabilities = { "CL-1": 52, "CL-2": 23, "CL-3": 10, "CL-4": 15 };
    const { container } = render(<DiagnosisScreen s={s} onRecord={() => {}} onStart={() => {}} />);
    expect(texts(container, ".rk .rs")).toEqual([
      "같은 증상 전체 기록 108건 중 57건",
      "같은 증상 전체 기록 108건 중 25건",
      "같은 증상 전체 기록 108건 중 16건",
      "같은 증상 전체 기록 108건 중 10건",
    ]);
    expect(container.querySelector('[data-part="rank-source"]')?.textContent).toBe(
      "확률 = (그 원인 건수 + 1) ÷ (108 + 원인 4개) — 이 설비 기록이 3건 미만이라 같은 증상 전체 기록 108건 기준 · 원인마다 기본 1건을 더해 기록이 적어도 100%가 되지 않음",
    );
    expect(container.querySelector(".cd")!.textContent ?? "").not.toMatch(/이 설비 기록 108건/);
  });

  it("기본 건수 0(같은 증상 전체 셈 옵션): 식에 +1 없음 · 기본 1건 글 0", () => {
    const s = Object.assign(m02(), { count_scope: "group", count_prior: 0, equipment_counts: { "CL-1": 57, "CL-2": 25, "CL-3": 10, "CL-4": 16 }, equipment_total: 108 });
    const { container } = render(<DiagnosisScreen s={s} onRecord={() => {}} onStart={() => {}} />);
    expect(container.querySelector('[data-part="rank-source"]')?.textContent).toBe(
      "확률 = 그 원인 건수 ÷ 108 — 같은 증상 전체 기록 108건 기준",
    );
  });

  it("지난 화면도 같은 글 · 화면 글에 내부 번호 0", () => {
    const { container } = render(<DiagnosisScreen s={m02()} onRecord={() => {}} onStart={() => {}} past />);
    expect(texts(container, ".rk .rs")[0]).toBe("이 설비 기록 6건 중 4건");
    expect(container.textContent ?? "").not.toMatch(/D-\d|R\d\b|F\d\b/);
  });
});
