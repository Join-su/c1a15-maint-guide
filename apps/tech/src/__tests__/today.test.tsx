// D-528 정비자 앱(가이드 정비자 2 · 부록 2): 왼쪽 「오늘 밤 알람」 칸 · 내 알람 카드 상태값 한 줄 · 홈 안내 문장 뺌.
// home-d528.json = 시험 DB 실제 응답 한 건(server/tests/test_tech_home_d528.py HOME_FIXTURE_OUT, D-503 2).

import { cleanup, fireEvent, render } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import type { Home } from "@c1a15/ui";
import { HomeScreen, val } from "../screens/Home";
import { TodayPanel } from "../screens/Today";

const fx = import.meta.glob("./fixtures/*.json", { eager: true, import: "default" }) as Record<string, unknown>;
const load = <T,>(name: string) => structuredClone(fx[`./fixtures/${name}.json`]) as T;
const texts = (root: ParentNode, sel: string) => [...root.querySelectorAll(sel)].map((e) => e.textContent?.trim() ?? "");

afterEach(cleanup);

describe("왼쪽 「오늘 밤 알람」 칸", () => {
  it("진행 탭: 새 · 진행 중 알람만 · 계통 · 시각 · 설비 · 알람 · 값 · 경계 · 단계, 누르면 그 알람(점검 시작과 같은 길)", () => {
    const h = load<Home>("home-d528");
    const onOpen = vi.fn();
    const { container } = render(<TodayPanel home={h} current={null} onOpen={onOpen} />);
    const live = h.alarms.filter((a) => a.status !== "done");
    expect(container.querySelector(".n-lh b")?.textContent).toBe("오늘 밤 알람");
    expect(container.querySelector(".n-cnt")?.textContent).toBe(String(live.length));
    expect(texts(container, ".tabs button")).toEqual(["진행", "완료"]);
    const rows = container.querySelectorAll("button.n-li");
    expect(rows.length).toBe(live.length);
    const a = live[0];
    expect(rows[0].querySelector(".n-k")?.textContent).toBe("냉각 계통");
    expect(rows[0].querySelector("b")?.textContent).toBe(`${a.equipment_id} · ${a.group_name}`);
    expect(texts(rows[0], ".n-lv span")).toEqual([`${a.alarm.sensor} ${val(a.alarm.value, a.alarm.unit)}`, `경계 ${val(a.alarm.boundary, a.alarm.unit)}`]);
    expect(rows[0].querySelector(".n-ls")?.textContent).toBe("🚨새 알람");
    fireEvent.click(rows[0]);
    expect(onOpen).toHaveBeenCalledWith(a);
  });

  it("완료 탭: 최근 내 보고서(계통 · 설비 · 원인 · 승인 상태) · 같은 탭 한 번 더 눌러도 그대로 · 진행으로 돌아옴", () => {
    const h = load<Home>("home-d528");
    const { container } = render(<TodayPanel home={h} current={null} onOpen={() => {}} />);
    const done = () => container.querySelectorAll(".n-li.ro");
    fireEvent.click(container.querySelectorAll(".tabs button")[1]);
    fireEvent.click(container.querySelectorAll(".tabs button")[1]);
    expect(done().length).toBe(h.recent_reports.length);
    const r = h.recent_reports[0];
    expect(done()[0].querySelector("b")?.textContent).toBe(`${r.equipment_id} · ${r.cause}`);
    expect(done()[0].querySelector(".n-k")?.textContent).toBe("냉각 계통");
    expect(done()[0].querySelector(".ch")?.textContent).toBe("승인 대기");
    fireEvent.click(container.querySelectorAll(".tabs button")[0]);
    expect(container.querySelectorAll("button.n-li").length).toBe(1);
  });

  it("빈 상태: 진행 중인 알람 없음(개수 칸 없음)", () => {
    const h = { ...load<Home>("home-d528"), alarms: [] };
    const { container } = render(<TodayPanel home={h} current={null} onOpen={() => {}} />);
    expect(container.querySelector(".n-le")?.textContent).toBe("진행 중인 알람 없음");
    expect(container.querySelector(".n-cnt")).toBeNull();
  });
});

describe("홈 내 알람 · 안내 문장", () => {
  it("내 알람 카드 한 줄: 계통 · 값 · 경계 · 방향(완료 행은 없음) · 안전 수칙은 제목만", () => {
    const h = load<Home>("home-d528");
    const { container } = render(<HomeScreen home={h} onOpen={() => {}} />);
    const a = h.alarms.find((x) => x.status === "new")!;
    const row = container.querySelector(`[data-alarm="${a.alarm_id}"]`)!;
    expect(texts(row, ".n-vals > *")).toEqual(["냉각 계통", val(a.alarm.value, a.alarm.unit), val(a.alarm.boundary, a.alarm.unit), "경계 아래"]);
    const done = h.alarms.find((x) => x.status === "done")!;
    expect(container.querySelector(`[data-alarm="${done.alarm_id}"] .n-vals`)).toBeNull();
    expect(container.querySelector(".safe")?.textContent).toBe("잠금을 먼저 확인합니다");
  });

  it("반려 칸: 사유 · 파트장 · 시각 · 「이어서 하기」, 설명 문장 없음", () => {
    const h = load<Home>("home-rejected");
    const r = h.recent_reports.find((x) => x.status === "rejected")!;
    const { container } = render(<HomeScreen home={h} onOpen={() => {}} />);
    expect(container.querySelector(".banner.bad div")?.textContent).toMatch(new RegExp(`^반려 사유 · ${r.rejected_by_name} \\d\\d:\\d\\d${r.reject_reason}$`));
    expect(container.textContent).not.toContain("이어서 하기\"로");
    expect(texts(container, ".btn.full")).toEqual(["이어서 하기"]);
  });
});
