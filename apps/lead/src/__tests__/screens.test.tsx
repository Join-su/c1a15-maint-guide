// P-12 component 시험: 실제 API 응답(fixtures, dev 스택 파트장 API)으로 L01 ~ L06을 그려 Prototype v17 구조(packet 부록)와
// 보내는 요청을 대조한다.

import { act, cleanup, fireEvent, render, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import type { Api, Schemas } from "@c1a15/ui";
import { ApprovalList, Review } from "../screens/Approvals";
import { AuditScreen } from "../screens/Audit";
import { CallDetail, CallList } from "../screens/Calls";
import { Frame } from "../screens/Frame";
import { GradesScreen } from "../screens/Grades";
import { JudgeList } from "../screens/Judge";
import { Login } from "../screens/Login";

const fx = import.meta.glob("./fixtures/*.json", { eager: true, import: "default" }) as Record<string, unknown>;
function load<T>(name: string): T {
  return structuredClone(fx[`./fixtures/${name}.json`]) as T;
}
const texts = (root: ParentNode, sel: string) => [...root.querySelectorAll(sel)].map((e) => e.textContent?.trim() ?? "");
const btn = (root: ParentNode, label: string) =>
  [...root.querySelectorAll(".btn")].find((b) => b.textContent?.trim() === label) as HTMLElement;
const ok = (data: unknown) => Promise.resolve({ data, error: undefined, response: { status: 200 } });
const fail = (status: number, detail: unknown) => Promise.resolve({ data: undefined, error: { detail }, response: { status } });

afterEach(cleanup);

describe("L01 로그인 · 틀", () => {
  it("파트장 계정만: 역할이 다르면 거부 배너 · ID 칸 오류 토큰(AC-12)", async () => {
    const api = { POST: vi.fn(() => fail(403, "role_mismatch")) } as unknown as Api;
    const { container } = render(<Login api={api} onDone={() => {}} />);
    expect(container.querySelector(".lg-card h3")?.textContent).toBe("파트장 로그인");
    expect(btn(container, "로그인").className).toContain("dis");
    fireEvent.change(container.querySelector('[aria-label="ID"]')!, { target: { value: "tech.kim" } });
    fireEvent.change(container.querySelector('[aria-label="비밀번호"]')!, { target: { value: "x" } });
    await act(async () => fireEvent.click(btn(container, "로그인")));
    expect(container.querySelector(".banner.bad b")?.textContent).toBe("파트장 계정만 로그인할 수 있습니다");
    expect(container.querySelector('[aria-label="ID"]')?.className).toBe("inp err");
  });

  it("왼쪽 메뉴 5개(EV-009 사람 판단) · 현재 메뉴 강조 · 메뉴 이동", () => {
    const onMenu = vi.fn();
    const { container } = render(
      <Frame menu="calls" me={{ display_name: "박 파트장" }} title="처리할 호출" now="2026-10-01T08:12:00+09:00" onMenu={onMenu}>
        <div />
      </Frame>,
    );
    expect(texts(container, ".wn")).toEqual(["승인 대기", "호출", "사람 판단", "권한 등급", "감사 기록"]);
    expect(container.querySelector(".wn.on")?.textContent).toBe("호출");
    expect(container.querySelector(".wb-top .sm")?.textContent).toBe("2026-10-01 (목) 08:12");
    fireEvent.click(container.querySelectorAll(".wn")[3]); // 권한 등급(사람 판단이 앞에 더해짐)
    expect(onMenu).toHaveBeenCalledWith("grades");
  });
});

describe("L02 승인 대기 · L03 검토", () => {
  it("요약 타일 3개 = 실제 건수 · 행 항목 · 근거 적음 칩 · 권한 위반(AC-27 · AC-29-C3)", () => {
    const o = load<Schemas["LeadOverview"]>("overview-list");
    const onOpen = vi.fn();
    const { container } = render(<ApprovalList data={o} onOpen={onOpen} />);
    expect(texts(container, ".kt b")).toEqual([String(o.tiles.awaiting), String(o.tiles.calls_open), String(o.tiles.violations)]);
    expect(texts(container, ".kt span")).toEqual(["승인 대기", "처리할 호출", "권한 위반"]);
    expect(texts(container, ".wt th")).toEqual(["설비 · 알람", "확정 원인", "작성", "확정 시각", "근거 기록", "권한", ""]);
    const rows = [...container.querySelectorAll("tr[data-report]")];
    expect(rows.length).toBe(o.rows.length);
    const low = rows.find((r) => r.className === "low")!;
    expect(low.querySelector(".ch.amber")?.textContent).toBe("근거 적음");
    expect(texts(container, ".ch.green")).toEqual(o.rows.map(() => "위반 0"));
    fireEvent.click(rows[0].querySelector(".btn")!);
    expect(onOpen).toHaveBeenCalledWith(o.rows[0].report_id);
  });

  it("빈 목록 안내(AC-27-C3)", () => {
    const { container } = render(<ApprovalList data={load("overview-empty")} onOpen={() => {}} />);
    expect(texts(container, ".kt b")).toEqual(["0", "0", "0"]);
    expect(container.querySelector(".empty")?.textContent).toBe("승인 대기 보고서가 없습니다");
  });

  it("EV-007: '결정 저장'을 빠르게 세 번 → 결정 요청 한 번(응답 전 두 번째 누름 무시)", async () => {
    const report = load<Schemas["LeadReport"]>("report-review");
    let release: () => void = () => {};
    const POST = vi.fn(
      () => new Promise((r) => (release = () => r({ data: { status: "approved", history_record_id: "R-0001" }, error: undefined, response: { status: 200 } }))),
    );
    const onDone = vi.fn();
    const { container } = render(<Review api={{ POST } as unknown as Api} report={report} onDone={onDone} />);
    fireEvent.click(btn(container, "결정 저장"));
    fireEvent.click(btn(container, "결정 저장"));
    fireEvent.click(btn(container, "결정 저장"));
    expect(POST).toHaveBeenCalledTimes(1);
    await act(async () => release());
    expect(onDone).toHaveBeenCalledTimes(1);
  });

  it("검토: 보고서 다섯 행 · 결정 3개(하나만) · 그대로 승인 저장", async () => {
    const report = load<Schemas["LeadReport"]>("report-review");
    const api = { POST: vi.fn(() => ok({ status: "approved", history_record_id: "R-0001" })) } as unknown as Api;
    const onDone = vi.fn();
    const { container } = render(<Review api={api} report={report} onDone={onDone} />);
    expect(texts(container, ".rk2")).toEqual(["확정 원인", "점검 경로", "조치", "근거 사례", "미확인"]);
    expect(container.querySelector(".cd-h .ch.gray")?.textContent).toBe(`${report.author_name} 작성`);
    expect(texts(container, ".dopt b")).toEqual(["그대로 승인", "수정 후 승인", "반려"]);
    expect(container.querySelectorAll(".dopt.sel").length).toBe(1);
    await act(async () => fireEvent.click(btn(container, "결정 저장")));
    expect(api.POST).toHaveBeenCalledWith("/api/lead/reports/{report_id}/decision", {
      params: { path: { report_id: report.report_id } },
      body: { decision: "approve", edits: {}, memo: null },
    });
    expect(onDone).toHaveBeenCalled();
  });

  it("반려: 사유가 비면 '반려 사유를 입력해야 저장됩니다' · 저장 잠김(AC-24-C1), 사유를 쓰면 저장", async () => {
    const report = load<Schemas["LeadReport"]>("report-review");
    const api = { POST: vi.fn(() => ok({ status: "rejected" })) } as unknown as Api;
    const { container } = render(<Review api={api} report={report} onDone={() => {}} />);
    fireEvent.click(container.querySelectorAll(".dopt")[2]);
    expect(container.querySelector(".req")?.textContent).toBe("반려 사유를 입력해야 저장됩니다");
    const save = btn(container, "결정 저장");
    expect(save.className).toContain("dis");
    fireEvent.click(save);
    expect(api.POST).not.toHaveBeenCalled();
    fireEvent.change(container.querySelector("textarea.memo")!, { target: { value: "필터 표면 상태를 다시 적어 주세요" } });
    await act(async () => fireEvent.click(btn(container, "결정 저장")));
    expect(api.POST).toHaveBeenCalledWith("/api/lead/reports/{report_id}/decision", expect.objectContaining({ body: expect.objectContaining({ decision: "reject", memo: "필터 표면 상태를 다시 적어 주세요" }) }));
  });

  it("수정 후 승인: 행을 직접 고침 → 서버 근거 검사 실패면 빨간 행 · 실패 배너 · 저장 잠김, 통과면 저장(L03 / edit · edit_failed)", async () => {
    const report = load<Schemas["LeadReport"]>("report-review");
    const failed = load("check-failed");
    const passed = load("check-ok");
    const post = vi.fn((path: string) => (path.endsWith("/check") ? ok(post.mock.calls.length < 2 ? failed : passed) : ok({ status: "approved" })));
    const api = { POST: post } as unknown as Api;
    const { container } = render(<Review api={api} report={report} onDone={() => {}} />);
    fireEvent.click(container.querySelectorAll(".dopt")[1]);
    fireEvent.click(container.querySelector('[data-field="unresolved"] .rv2')!);
    const ta = container.querySelector('[data-field="unresolved"] textarea.edit-in') as HTMLTextAreaElement;
    fireEvent.change(ta, { target: { value: `${ta.value} · 팬 회전수 1,850 rpm으로 정상 확인` } });
    await waitFor(() => expect(container.querySelector(".rf.fail")).not.toBeNull(), { timeout: 2000 });
    expect(container.querySelector(".banner.bad b")?.textContent).toBe("근거 검사 실패");
    expect(btn(container, "결정 저장").className).toContain("dis");
    fireEvent.change(ta, { target: { value: "냉각 팬 상태(4.4, C) · 주간 조 확인 배정" } });
    await waitFor(() => expect(container.querySelector(".rf.fail")).toBeNull(), { timeout: 2000 });
    fireEvent.change(container.querySelector("textarea.memo")!, { target: { value: "주간 확인 담당을 지정함" } });
    await act(async () => fireEvent.click(btn(container, "결정 저장")));
    expect(post).toHaveBeenLastCalledWith("/api/lead/reports/{report_id}/decision", {
      params: { path: { report_id: report.report_id } },
      body: { decision: "edit", edits: { unresolved: "냉각 팬 상태(4.4, C) · 주간 조 확인 배정" }, memo: "주간 확인 담당을 지정함" },
    });
  });
});

describe("L04 처리할 호출", () => {
  it("목록: 유형 칩 · 설비 · 시각 · 필요한 작업 · 보낸 사람 · 답하기", () => {
    const d = load<Schemas["LeadCalls"]>("calls-list");
    const onOpen = vi.fn();
    const { container } = render(<CallList data={d} onOpen={onOpen} />);
    expect(texts(container, ".wt th")).toEqual(["유형", "설비 · 알람", "시각", "필요한 작업", "보낸 사람", ""]);
    expect(texts(container, "td .ch")).toEqual(d.rows.map((r) => (r.kind === "approval" ? "파트장 호출" : "숙련자 인계")));
    expect(container.querySelector("td .ch.red")?.textContent).toBe("숙련자 인계");
    fireEvent.click(container.querySelector("tr[data-call] .btn")!);
    expect(onOpen).toHaveBeenCalledWith(d.rows[0].call_id);
  });

  it("파트장 호출 상세: 답 3개 · 처리 메모 · D 안내 · 답 저장(AC-23)", async () => {
    const call = load<Schemas["LeadCall"]>("call-detail");
    const api = { POST: vi.fn(() => ok({ status: "answered", answer: "daytime" })) } as unknown as Api;
    const { container } = render(<CallDetail api={api} call={call} onDone={() => {}} />);
    expect(container.querySelector(".pv .sm")?.textContent).toBe("정비자가 보낸 요약");
    expect(texts(container, ".dopt b")).toEqual(["승인 후 진행", "주간 처리", "직접 확인"]);
    expect(container.querySelector(".note")?.textContent).toBe('D등급 작업 호출에는 "승인 후 진행"이 없습니다.');
    fireEvent.click(container.querySelectorAll(".dopt")[1]);
    fireEvent.change(container.querySelector("textarea.memo")!, { target: { value: "주간 정비 배정" } });
    await act(async () => fireEvent.click(btn(container, "답 저장")));
    expect(api.POST).toHaveBeenCalledWith("/api/lead/calls/{call_id}/answer", {
      params: { path: { call_id: call.call_id } },
      body: { answer: "daytime", note: "주간 정비 배정" },
    });
  });

  it("D등급 호출(파생 L04 / call_detail_d)에는 '승인 후 진행'이 없다(AC-23-C3) · 숙련자 인계 상세는 2개", () => {
    let r = render(<CallDetail api={{} as Api} call={load("call-detail-d")} onDone={() => {}} />);
    expect(texts(r.container, ".dopt b")).toEqual(["주간 처리", "직접 확인"]);
    cleanup();
    r = render(<CallDetail api={{} as Api} call={load("handover-detail")} onDone={() => {}} />);
    expect(texts(r.container, ".dopt b")).toEqual(["주간 숙련자 배정", "직접 확인"]);
    expect(r.container.querySelector(".note")).toBeNull();
  });
});

describe("L05 권한 등급", () => {
  it("등급표 전부 · 'n절 중 n절 표시' · 변경 기록 없음 안내(결정 018 ②)", () => {
    const g = load<Schemas["LeadGrades"]>("grades-default");
    const { container } = render(<GradesScreen api={{} as Api} data={g} onChanged={() => {}} />);
    expect(container.querySelector(".cd-h .ch.gray")?.textContent).toBe(`${g.total}절 중 ${g.total}절 표시`);
    expect(container.querySelectorAll("tr[data-section]").length).toBe(g.total);
    expect(container.querySelector(".empty")?.textContent).toBe("아직 변경 기록이 없습니다");
  });

  it("고르기 → 올림 경고(서버 문구) · 취소 / 변경 저장(confirmed) · 낮춤은 warnb 버튼(AC-25-C3)", async () => {
    const g = load<Schemas["LeadGrades"]>("grades-default");
    const raise = load("warning-raise");
    const api = {
      GET: vi.fn(() => ok(raise)),
      POST: vi.fn(() => ok({ section: "4.3", before: "A", after: "C" })),
    } as unknown as Api;
    const onChanged = vi.fn();
    const { container } = render(<GradesScreen api={api} data={g} onChanged={onChanged} />);
    fireEvent.click(container.querySelector('tr[data-section="4.3"] .sel2')!);
    expect(texts(container, ".dd div")).toEqual(["A 단독 가능", "B 확인 후", "C 승인 필요", "D 범위 밖"]);
    await act(async () => fireEvent.click(container.querySelectorAll(".dd div")[2]));
    expect(container.querySelector(".banner.info b")?.textContent).toBe("등급을 올리려 합니다 · 4.3 흡기 필터 육안 점검 A → C");
    expect(container.querySelector(".dd .on")?.textContent).toBe("C 승인 필요");
    expect(texts(container, ".choice2 .btn")).toEqual(["취소", "C로 변경 저장"]);
    await act(async () => fireEvent.click(btn(container, "C로 변경 저장")));
    expect(api.POST).toHaveBeenCalledWith("/api/lead/grades/{section}", { params: { path: { section: "4.3" } }, body: { grade: "C", confirmed: true } });
    expect(onChanged).toHaveBeenCalled();
    cleanup();
    const api2 = { GET: vi.fn(() => ok(load("warning-lower"))), POST: vi.fn() } as unknown as Api;
    const r = render(<GradesScreen api={api2} data={g} onChanged={() => {}} />);
    fireEvent.click(r.container.querySelector('tr[data-section="4.4"] .sel2')!);
    await act(async () => fireEvent.click(r.container.querySelectorAll(".dd div")[1]));
    expect(r.container.querySelector(".banner.warn b")?.textContent).toBe("등급을 낮추려 합니다 · 4.4 냉각 팬 분해 점검 C → B");
    expect(btn(r.container, "B로 변경 저장").className).toContain("warnb");
    fireEvent.click(btn(r.container, "취소"));
    expect(r.container.querySelector(".banner")).toBeNull();
    expect(api2.POST).not.toHaveBeenCalled();
  });

  it("변경 기록: 누가 · 언제 · 전 → 후(AC-25-C2)", () => {
    const g = load<Schemas["LeadGrades"]>("grades-changed");
    const { container } = render(<GradesScreen api={{} as Api} data={g} onChanged={() => {}} />);
    expect(texts(container, ".cd:nth-child(2) td:nth-child(3)")).toEqual(["C → A", "A → C"]);
  });
});

describe("L04 정정(S-05 P-15)", () => {
  it("call_corrected: 보낸 파트장 호출에 '보낸 뒤 정비자 정정' 상자(시각 · 점검 · 전 → 후 · 사유, 새 호출 없음 — AC-47-C2)", () => {
    const call = load<Schemas["LeadCall"]>("call-corrected");
    const { container } = render(<CallDetail api={{} as Api} call={call} onDone={() => {}} />);
    const box = container.querySelector(".corr-box")!;
    expect(box.querySelector("b")?.textContent).toMatch(/^보낸 뒤 정비자 정정 · \d\d:\d\d$/);
    expect(box.querySelector("div")?.textContent).toBe("4.3 흡기 필터 육안 점검 · 정상 → 이상");
    expect(box.querySelector(".sm")?.textContent).toBe("사유 · 필터 뒷면 기름때를 못 보고 정상으로 눌렀음. 이 호출을 보낸 뒤라 다시 판정하지 않았습니다.");
    expect(container.querySelector(".pv")!.nextElementSibling).toBe(box); // 요약 아래
    expect(texts(container, ".dopt b")).toEqual(["승인 후 진행", "주간 처리", "직접 확인"]);
  });

  it("handover_corrected(결정 019 ②): 숙련자 인계에도 같은 상자, 선택지는 인계 2개", () => {
    const call = load<Schemas["LeadCall"]>("handover-corrected");
    const { container } = render(<CallDetail api={{} as Api} call={call} onDone={() => {}} />);
    expect(container.querySelector(".corr-box div")?.textContent).toBe("4.6 냉각 설정값 확인 · 정상 → 이상");
    expect(texts(container, ".dopt b")).toEqual(["주간 숙련자 배정", "직접 확인"]);
  });

  it("correction_call_detail(결정 019 ⑧): 조치 뒤 정정 호출 — '승인 후 진행' 설명은 '정비자가 정정 때 하던 단계로 이어서 합니다'", () => {
    const call = load<Schemas["LeadCall"]>("correction-call-detail");
    const { container } = render(<CallDetail api={{} as Api} call={call} onDone={() => {}} />);
    expect(call.need).toBe("정정 확인 · 4.3 흡기 필터 육안 점검(이상 → 정상)");
    expect(texts(container, ".dopt span:not(.rd)")[0]).toBe("정비자가 정정 때 하던 단계로 이어서 합니다");
    expect(container.querySelector(".pv p")?.textContent).toContain("정정");
    expect(container.querySelector(".corr-box")).toBeNull();
  });

  it("L06 / correction: 정정(전 → 후 · 사유) · 메모 덧붙이기 행은 서버 문구 그대로", () => {
    const a = load<Schemas["LeadAudit"]>("audit-correction");
    const { container } = render(<AuditScreen data={a} onFilter={() => {}} />);
    const acts = texts(container, ".wt td:nth-child(4)");
    expect(acts).toContain("정정 · 4.3 결과 정상 → 이상 · 사유 '필터 뒷면 기름때를 못 보고 정상으로 눌렀음'");
    expect(acts).toContain("메모 덧붙이기 · 잠금 완료 1.2");
  });
});

describe("L06 감사 기록", () => {
  it("필터 3개 · 표(시각 · 사용자 · 앱 · 행동 · 대상), 필터를 고르면 그 조건으로 다시 읽음(AC-26)", () => {
    const a = load<Schemas["LeadAudit"]>("audit-default");
    const onFilter = vi.fn();
    const { container } = render(<AuditScreen data={a} onFilter={onFilter} />);
    expect(texts(container, ".flt > .sel2").map((t) => t.split(" · ")[0])).toEqual(["설비", "사용자", "기간"]);
    expect(texts(container, ".wt th")).toEqual(["시각", "사용자", "앱", "행동", "대상"]);
    expect(container.querySelectorAll(".wt tr").length - 1).toBe(a.rows.length);
    expect(texts(container, ".wt td:nth-child(2)")).toContain("시스템");
    fireEvent.click(container.querySelectorAll(".flt > .sel2")[0]);
    fireEvent.click([...container.querySelectorAll(".dd div")].find((d) => d.textContent === "M-01")!);
    expect(onFilter).toHaveBeenCalledWith({ equipment: "M-01", user_id: null, date: a.date });
  });

  it("걸러진 기록(L06 / filtered)", () => {
    const a = load<Schemas["LeadAudit"]>("audit-filtered");
    const { container } = render(<AuditScreen data={a} onFilter={() => {}} />);
    expect(container.querySelectorAll(".flt > .sel2")[0].textContent).toMatch(/^설비 · M-01/);
    expect(container.querySelectorAll(".flt > .sel2")[1].textContent).toMatch(/^사용자 · /);
    expect(new Set(texts(container, ".wt td:nth-child(2)")).size).toBe(1);
  });
});

describe("EV-009 사람 판단(D-444 #18)", () => {
  type Data = Schemas["LeadCandidates"];
  const post = () => vi.fn(() => ok({ status: "promoted", alarm_id: 9 }));

  it("목록: 이유 칩 · 설비 · 센서 값 · ML · 버튼 둘, 빈 목록 안내", () => {
    const d = load<Data>("candidates");
    const { container } = render(<JudgeList api={{ POST: post() } as unknown as Api} data={d} onChanged={() => {}} />);
    expect(texts(container, ".wt th")).toEqual(["이유", "설비 · 시각", "센서 값", "ML", ""]);
    expect(texts(container, "tr[data-candidate] .ch")).toEqual(d.rows.map((r) => ({ low_confidence: "확신 낮음", rnf: "RNF", model_failure: "모델 실패" })[r.reason]));
    const low = container.querySelector(`tr[data-candidate="${d.rows.find((r) => r.reason === "low_confidence")!.candidate_id}"]`)!;
    expect(low.textContent).toContain("위험도 62% · HDF 41%");
    expect(texts(low, ".btn")).toEqual(["알람으로 올림", "문제없음"]);
    const empty = render(<JudgeList api={{} as Api} data={load<Data>("candidates-empty")} onChanged={() => {}} />);
    expect(empty.container.querySelector(".empty")?.textContent).toBe("사람 판단이 필요한 기록이 없습니다");
  });

  it("올림: 경계 넘은 줄은 바로 · 확신 낮음은 ML 제안 미리 고른 증상군 → 올림 저장 · RNF는 고르기 전 잠김", async () => {
    const d = load<Data>("candidates");
    const POST = post();
    const onChanged = vi.fn();
    const { container } = render(<JudgeList api={{ POST } as unknown as Api} data={d} onChanged={onChanged} />);
    const row = (reason: string) => container.querySelector(`tr[data-candidate="${d.rows.find((r) => r.reason === reason)!.candidate_id}"]`)!;
    const fixed = d.rows.find((r) => r.group_fixed)!;
    await act(async () => fireEvent.click(btn(row("model_failure"), "알람으로 올림")));
    expect(POST).toHaveBeenLastCalledWith("/api/lead/candidates/{candidate_id}/decision", {
      params: { path: { candidate_id: fixed.candidate_id } },
      body: { decision: "promote" },
    });
    expect(onChanged).toHaveBeenCalledTimes(1);
    const lowRow = d.rows.find((r) => r.reason === "low_confidence")!;
    fireEvent.click(btn(row("low_confidence"), "알람으로 올림"));
    expect(container.querySelector(".pick .dopt.sel b")?.textContent).toBe(d.groups.find((g) => g.value === lowRow.group_suggestion)!.label);
    await act(async () => fireEvent.click(btn(container.querySelector(".pick")!, "올림 저장")));
    expect(POST).toHaveBeenLastCalledWith("/api/lead/candidates/{candidate_id}/decision", {
      params: { path: { candidate_id: lowRow.candidate_id } },
      body: { decision: "promote", group: lowRow.group_suggestion },
    });
    fireEvent.click(btn(row("rnf"), "알람으로 올림"));
    expect(container.querySelector(".pick .dopt.sel")).toBeNull();
    expect(btn(container.querySelector(".pick")!, "올림 저장").className).toContain("dis");
  });

  it("문제없음 세 번 빠르게 → 요청 한 번", async () => {
    const d = load<Data>("candidates");
    let release: () => void = () => {};
    const POST = vi.fn(() => new Promise((r) => (release = () => r({ data: { status: "dismissed" }, error: undefined, response: { status: 200 } }))));
    const { container } = render(<JudgeList api={{ POST } as unknown as Api} data={d} onChanged={() => {}} />);
    const b = btn(container.querySelector("tr[data-candidate]")!, "문제없음");
    fireEvent.click(b);
    fireEvent.click(b);
    fireEvent.click(b);
    expect(POST).toHaveBeenCalledTimes(1);
    await act(async () => release());
  });
});
