// 리허설 2 R3 · R6(A 진단 숫자 · 앱 몫, 표시 · 글만): 순위 줄 = 확률 셈에 쓴 '이 설비 기록 n건 중 k건'(Pack 판정 출력 그대로) ·
// 비슷한 과거 기록은 순위 줄에서 빼고 그 칸 이름에 '참고(다른 설비 포함) · 순위 계산에 안 씀' · 출처 줄은 새 셈(원인마다 기본 1건)을 말함.
// n · k 칸이 없으면(옛 Pack · 옛 세션) 숫자 자리를 숨김 — 지어낸 숫자 0.

import { cleanup, render } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import type { SessionWithPreview } from "@c1a15/ui";
import { DiagnosisScreen } from "../screens/Diagnosis";

const fx = import.meta.glob("./fixtures/*.json", { eager: true, import: "default" }) as Record<string, unknown>;
const load = (name: string) => structuredClone(fx[`./fixtures/${name}.json`]) as SessionWithPreview;
const texts = (root: ParentNode, sel: string) => [...root.querySelectorAll(sel)].map((e) => e.textContent?.trim() ?? "");

// M-02 꼴: 이 설비 기록 6건(냉각 필터 막힘 4 · 냉각 팬 열화 1 · 냉각수 부족 1 · 냉각 설정 오류 0) · 비슷한 기록 상위 10건은 4/0/6/0
function m02(): SessionWithPreview {
  const s = load("session-before-lock");
  s.probabilities = { "CL-1": 50, "CL-2": 20, "CL-3": 20, "CL-4": 10 };
  s.evidence = { "CL-1": 4, "CL-2": 0, "CL-3": 6, "CL-4": 0 };
  Object.assign(s, { equipment_counts: { "CL-1": 4, "CL-2": 1, "CL-3": 1, "CL-4": 0 }, equipment_total: 6 });
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
      "확률: 이 설비의 지난 같은 알람 기록 6건에서 원인별 건수 비율 · 원인마다 기본 1건을 더해 셈(기록이 적어도 한 원인이 100%가 되지 않게)",
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

  it("그룹으로 넓혀 센 셈(count_scope group): '같은 그룹 기록 n건 중 k건' · 출처 줄이 까닭(이 설비 기록 3건 미만)을 말함", () => {
    const s = Object.assign(m02(), { count_scope: "group", equipment_counts: { "CL-1": 9, "CL-2": 3, "CL-3": 2, "CL-4": 1 }, equipment_total: 15 });
    const { container } = render(<DiagnosisScreen s={s} onRecord={() => {}} onStart={() => {}} />);
    expect(texts(container, ".rk .rs")).toEqual([
      "같은 그룹 기록 15건 중 9건",
      "같은 그룹 기록 15건 중 3건",
      "같은 그룹 기록 15건 중 2건",
      "같은 그룹 기록 15건 중 1건",
    ]);
    expect(container.querySelector('[data-part="rank-source"]')?.textContent).toBe(
      "확률: 이 설비 기록이 3건 미만이라 같은 그룹의 지난 같은 알람 기록 15건에서 원인별 건수 비율 · 원인마다 기본 1건을 더해 셈(기록이 적어도 한 원인이 100%가 되지 않게)",
    );
    expect(container.querySelector(".cd")!.textContent ?? "").not.toMatch(/이 설비 기록 15건/);
  });

  it("지난 화면도 같은 글 · 화면 글에 내부 번호 0", () => {
    const { container } = render(<DiagnosisScreen s={m02()} onRecord={() => {}} onStart={() => {}} past />);
    expect(texts(container, ".rk .rs")[0]).toBe("이 설비 기록 6건 중 4건");
    expect(container.textContent ?? "").not.toMatch(/D-\d|R\d\b|F\d\b/);
  });
});
