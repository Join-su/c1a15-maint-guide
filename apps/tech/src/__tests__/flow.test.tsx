// P-10 component 시험: S-03 실제 API 응답(fixtures/s03-*)으로 T08 · T09 · T10 · T11 · 홈 완료 행 · 종 '답이 온 호출'을 그려
// Prototype v17 구조(영역 · 버튼 · 순서 · 토큰)와 보내는 입력을 대조한다.

import { act, cleanup, fireEvent, render, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import type { Api, Home, Notifications, SessionView } from "@c1a15/ui";
import { ActionScreen, CallScreen, HandoverScreen, MonitorScreen, PathCard, ReportScreen } from "../screens/Flow";
import { dayTime, HomeScreen, NotifyPanel } from "../screens/Home";
import { Session, stepNumber } from "../screens/Session";

const fx = import.meta.glob("./fixtures/*.json", { eager: true, import: "default" }) as Record<string, unknown>;
function load<T = SessionView>(name: string): T {
  return structuredClone(fx[`./fixtures/${name}.json`]) as T;
}
const texts = (root: ParentNode, sel: string) => [...root.querySelectorAll(sel)].map((e) => e.textContent?.trim() ?? "");
const btn = (root: ParentNode, label: string) =>
  [...root.querySelectorAll(".btn")].find((b) => b.textContent?.trim() === label) as HTMLElement;

afterEach(() => {
  cleanup();
  localStorage.clear();
});

describe("T08 조치 · 재가동", () => {
  it("action_a: 원인 확정 머리 · 조치(A, 절, 분) · '교체 완료' → action_done, 점검 경로 끝은 '지금'", () => {
    const s = load("s03-action-a");
    const send = vi.fn();
    const { container } = render(<ActionScreen s={s} busy={false} checked={[]} onCheck={() => {}} send={send} />);
    expect(container.querySelector(".done-h .sm")?.textContent).toBe("원인 확정");
    expect(container.querySelector(".done-h h3")?.textContent).toBe(s.action!.cause_name);
    expect(container.querySelector(".done-h span:last-child")?.textContent).toBe(
      `근거: 점검 결과(이상) · 과거 기록 ${s.action!.evidence_record_ids.join(" · ")}`,
    );
    expect(texts(container, ".act-h > *")).toEqual(["흡기 필터 교체", "A단독 가능", "4.3.2절", `약 ${s.action!.minutes}분`]);
    fireEvent.click(btn(container, "교체 완료"));
    expect(send).toHaveBeenCalledWith({ type: "action_done", section: "4.3.2" });
    const tl = [...container.querySelectorAll(".tli")];
    expect(tl.map((t) => t.className)).toEqual(["tli ok", "tli ok", "tli bad", "tli now"]);
    expect(tl.at(-1)!.querySelector(".tt")?.textContent).toBe("지금");
  });

  it("checklist_b: B 조치는 체크리스트를 모두 확인해야 진행 버튼이 열린다(AC-32-C2 · AC-43-C4)", () => {
    const s = load("s03-action-b");
    const a = s.action!;
    const send = vi.fn();
    const onCheck = vi.fn();
    const r = render(<ActionScreen s={s} busy={false} checked={[]} onCheck={onCheck} send={send} />);
    expect(r.container.querySelector(".act .sm")?.textContent).toBe("아래 항목을 모두 확인해야 진행 버튼이 열립니다");
    expect(texts(r.container, ".act .ck")).toEqual(a.checklist);
    const locked = btn(r.container, "체크리스트 확인 후 교체 진행");
    expect(locked.className).toContain("dis");
    fireEvent.click(locked);
    expect(send).not.toHaveBeenCalled();
    fireEvent.click(r.container.querySelectorAll(".act .ck")[0]);
    expect(onCheck).toHaveBeenCalledWith([a.checklist[0]]);
    r.rerender(<ActionScreen s={s} busy={false} checked={a.checklist} onCheck={onCheck} send={send} />);
    fireEvent.click(btn(r.container, "교체 진행"));
    expect(send).toHaveBeenCalledWith({ type: "b_checklist_done", section: "4.3.2", checked: a.checklist });
  });

  it("restart_check: 조치 완료 칩 · 재가동(B, 6.1) 체크리스트, 다 확인해야 재가동(AC-21-C1)", () => {
    const s = load("s03-restart-check");
    const items = s.restart!.checklist;
    const send = vi.fn();
    const r = render(<ActionScreen s={s} busy={false} checked={items.slice(0, 2)} onCheck={() => {}} send={send} />);
    const acts = r.container.querySelectorAll(".act");
    expect(acts[0].querySelector(".ch.green")?.textContent).toMatch(/^완료 \d\d:\d\d$/);
    expect(texts(acts[1], ".act-h > *")).toEqual(["재가동", "B확인 후", "6.1절"]);
    expect(texts(acts[1], ".ck.on")).toEqual(items.slice(0, 2));
    const locked = btn(r.container, "체크리스트 확인 후 재가동");
    expect(locked.className).toContain("dis");
    r.rerender(<ActionScreen s={s} busy={false} checked={items} onCheck={() => {}} send={send} />);
    fireEvent.click(btn(r.container, "재가동"));
    expect(send).toHaveBeenCalledWith({ type: "restart", checked: items });
  });

  it("restart_value: 재가동 시각 · 센서 · 큰 값 · 경계 규칙, '경계 이내' · '여전히 밖'(AC-21-C2)", () => {
    const s = load("s03-restart-value");
    const send = vi.fn();
    const { container } = render(<ActionScreen s={s} busy={false} checked={[]} onCheck={() => {}} send={send} />);
    expect(container.querySelector(".act-h b")?.textContent).toBe("재가동 후 값 확인");
    expect(container.querySelector(".act-h .ch.green")?.textContent).toMatch(/^재가동 \d\d:\d\d$/);
    expect(container.querySelector(".sub")?.textContent).toBe("온도 차 · 무부하 3분 운전 뒤");
    expect(container.querySelector(".rv-big")?.textContent).toBe(s.restart!.value!.value_text);
    expect(container.querySelector(".rv-sub")?.textContent).toBe("경계 8.3 K 이상이면 경계 이내");
    expect(texts(container, ".choice2 .btn")).toEqual(["경계 이내", "여전히 밖"]);
    fireEvent.click(btn(container, "여전히 밖"));
    expect(send).toHaveBeenCalledWith({ type: "restart_result", outcome: "outside" });
  });
});

describe("T10 파트장 호출", () => {
  it("summary: 혼자 진행 불가 머리 · 지금까지 점검 · 남은 후보, 요약을 고쳐 보낸다(1.4 · AC-30)", () => {
    const s = load("s03-call-summary");
    const c = s.call!;
    const send = vi.fn();
    const { container } = render(
      <CallScreen s={s} busy={false} approvedSeen={false} onApprovedSeen={() => {}} onReport={() => {}} send={send} />,
    );
    expect(container.querySelector(".warn-h .sm")?.textContent).toBe("다음 점검은 혼자 진행할 수 없습니다");
    expect(container.querySelector(".warn-h h3")?.textContent).toBe(c.title);
    expect(texts(container, ".warn-h .tags > *")).toEqual(["C승인 필요", "매뉴얼 4.4절", `약 ${c.minutes}분`]);
    expect(texts(container, ".sub")).toEqual(["지금까지 점검", "남은 후보"]);
    expect(texts(container, ".dn2 span")).toEqual(c.checks_done.map((d) => `${d.title} · ${d.value}`));
    expect(texts(container, ".tags .ch.gray").slice(1)).toEqual(c.candidates.map((x) => `${x.name} ${x.pct}%`));
    expect(texts(container, ".cd:nth-child(2) > .btn")).toEqual(["파트장 호출", "호출하지 않고 대기"]);
    fireEvent.click(container.querySelector(".pv p")!);
    const ta = container.querySelector(".pv textarea") as HTMLTextAreaElement;
    expect(ta.value).toBe(c.summary.text);
    fireEvent.change(ta, { target: { value: `${c.summary.text} 팬 소음 있음.` } });
    fireEvent.click(btn(container, "파트장 호출"));
    expect(send).toHaveBeenCalledWith({ type: "call_send", summary: `${c.summary.text} 팬 소음 있음.` });
    fireEvent.click(btn(container, "호출하지 않고 대기"));
    expect(send).toHaveBeenCalledWith({ type: "call_wait" });
  });

  it("첫 판정 호출처럼 한 점검이 없으면 '점검 전'", () => {
    const s = load("s03-call-summary");
    s.call!.checks_done = [];
    const { container } = render(
      <CallScreen s={s} busy={false} approvedSeen={false} onApprovedSeen={() => {}} onReport={() => {}} send={() => {}} />,
    );
    expect(texts(container, ".dn2 span")).toEqual(["점검 전"]);
  });

  it("waiting · sent · 답 3종 배너와 다음 행동(AC-30-C2 · AC-23 · AC-08-C2)", () => {
    const view = (name: string, approvedSeen = false) => {
      cleanup();
      const onReport = vi.fn();
      const onSeen = vi.fn();
      const r = render(
        <CallScreen s={load(name)} busy={false} approvedSeen={approvedSeen} onApprovedSeen={onSeen} onReport={onReport} send={() => {}} />,
      );
      return { c: r.container, onReport, onSeen };
    };
    let v = view("s03-call-waiting");
    expect(v.c.querySelector(".banner.warn b")?.textContent).toMatch(/^호출하지 않고 대기 중 · \d\d:\d\d$/);
    expect(texts(v.c, ".cd:nth-child(2) > .btn")).toEqual(["파트장 호출"]);
    v = view("s03-call-sent");
    expect(v.c.querySelector(".banner.info b")?.textContent).toMatch(/^파트장 호출을 보냈습니다 · \d\d:\d\d$/);
    expect(v.c.querySelector(".pv p")?.getAttribute("role")).toBeNull(); // 보낸 뒤에는 고치지 않는다
    expect(v.c.querySelectorAll(".cd:nth-child(2) > .btn").length).toBe(0);
    v = view("s03-ans-approved");
    const s = load("s03-ans-approved");
    expect(v.c.querySelector(".banner.ok b")?.textContent).toMatch(/^승인 후 진행 · 박 파트장 \d\d:\d\d$/);
    expect(v.c.querySelector(".ins-h .sm")?.textContent).toBe(`점검 ${s.instruction!.check_no} · 파트장 승인`);
    expect(texts(v.c, ".ins-h .tags > *")).toEqual(["C승인 필요", "승인됨", "매뉴얼 4.4절"]);
    expect(texts(v.c, ".proc li").length).toBe(s.instruction!.steps.length);
    fireEvent.click(btn(v.c, "점검 시작"));
    expect(v.onSeen).toHaveBeenCalled();
    v = view("s03-ans-daytime");
    expect(v.c.querySelector(".banner.warn b")?.textContent).toBe("주간 처리로 결정 · 저부하 감시 운전");
    expect(v.c.querySelector(".banner.warn div")?.textContent).toContain('"냉각 팬 분해 점검(4.4, C)"이 보고서 "미확인 · 요청"에 기록됩니다.');
    fireEvent.click(btn(v.c, "보고서 작성"));
    expect(v.onReport).toHaveBeenCalled();
    v = view("s03-ans-direct");
    expect(v.c.querySelector(".banner.info b")?.textContent).toBe("파트장 직접 확인 · 처리 결과"); // 결정 018 ③
    fireEvent.click(btn(v.c, "보고서 작성"));
    expect(v.onReport).toHaveBeenCalled();
  });
});

describe("T11 숙련자 인계 · 감시 마감", () => {
  it("unable_repeat: '확인 불가가 반복됨' · 머리 · 인계 요약 · 숙련자 인계 → call_send, 점검 경로(AC-19-C3)", () => {
    const s = load("s03-handover-unable");
    const send = vi.fn();
    const { container } = render(<HandoverScreen s={s} busy={false} send={send} />);
    expect(container.querySelector(".warn-h .sm")?.textContent).toBe("확인 불가가 반복됨");
    expect(container.querySelector(".warn-h h3")?.textContent).toBe(s.call!.head);
    expect(container.querySelector(".pv .sm")?.textContent).toBe("숙련자 인계 요약 (자동 작성 · 고칠 수 있음)");
    expect(container.querySelector(".pv p")?.textContent).toContain("확인 불가 2회");
    fireEvent.click(btn(container, "숙련자 인계"));
    expect(send).toHaveBeenCalledWith({ type: "call_send" });
    expect(texts(container, ".tli .ch.vd")).toEqual([]);
    expect(texts(container, ".tli span:not(.tt):not(.td)")).toContain("확인 불가 2회 · 제외");
  });

  it("expert_handover(맞지 않는 소견) · 재가동 뒤 밖: '숙련자 인계' 머리(AC-20 · AC-21-C3)", () => {
    for (const [name, head] of [
      ["s03-handover-oos", "후보 원인과 맞지 않는 소견"],
      ["s03-handover-restart", "재가동 뒤에도 값이 경계 밖"],
    ]) {
      cleanup();
      const { container } = render(<HandoverScreen s={load(name)} busy={false} send={() => {}} />);
      expect(container.querySelector(".warn-h .sm")?.textContent).toBe("숙련자 인계");
      expect(container.querySelector(".warn-h h3")?.textContent).toBe(head);
    }
  });

  it("monitor_close: 이상 없음 · 감시 머리 · 6.2절 · '보고서 작성' → monitor_close(AC-22)", () => {
    const s = load("s03-monitor-close");
    const send = vi.fn();
    const { container } = render(<MonitorScreen s={s} busy={false} send={send} />);
    expect(container.querySelector(".done-h .sm")?.textContent).toBe("이상 없음 · 감시");
    expect(texts(container, ".act-h > *")).toEqual(["이상 없음 · 감시 마감", "A단독 가능", "6.2절"]);
    fireEvent.click(btn(container, "보고서 작성"));
    expect(send).toHaveBeenCalledWith({ type: "monitor_close" });
    expect(container.querySelectorAll(".tli.now").length).toBe(0);
  });
});

describe("T09 보고서", () => {
  const LABELS = ["설비 · 알람", "센서 근거", "점검 경로", "확정 원인", "근거 사례", "조치", "정지 시간", "미확인 · 요청"];

  it("draft: 8항목(출처 칩 · 고치기), 확정 전 확인 3항목 통과, 확정 버튼이 열린다(R10 · AC-07-C2)", () => {
    const s = load("s03-report-draft");
    const send = vi.fn();
    const { container } = render(<ReportScreen report={s.report!} busy={false} send={send} onHome={() => {}} />);
    expect(texts(container, ".cd-h b, .cd-h .ch")).toEqual(["정비 보고서 초안", "초안", "확정 전 확인"]);
    expect(texts(container, ".rk2")).toEqual(LABELS);
    expect(texts(container, ".rf .ch.src")).toEqual(["자동", "센서", "입력", "입력", "기록", "매뉴얼", "자동", "입력"]);
    expect(container.querySelectorAll(".rf .ed svg").length).toBe(8);
    expect(texts(container, ".ckl .ck.on")).toEqual(["근거 없는 문장 없음", "권한 등급 위반 없음", "필수 8항목 모두 채워짐"]);
    fireEvent.click(btn(container, "보고서 확정"));
    expect(send).toHaveBeenCalledWith({ type: "report_confirm" });
  });

  it("고치기: 연필 → 글 상자 → 벗어나면 report_edit(바뀐 경우만)", () => {
    const s = load("s03-report-draft");
    const send = vi.fn();
    const { container } = render(<ReportScreen report={s.report!} busy={false} send={send} onHome={() => {}} />);
    fireEvent.click(container.querySelector('[data-field="unresolved"] .ed')!);
    const ta = container.querySelector('[data-field="unresolved"] textarea') as HTMLTextAreaElement;
    fireEvent.change(ta, { target: { value: "냉각 팬 소음 · 주간 확인 요청" } });
    expect(btn(container, "보고서 확정").className).toContain("dis"); // 고치는 중에는 확정하지 않는다
    fireEvent.blur(ta);
    expect(send).toHaveBeenCalledWith({ type: "report_edit", field: "unresolved", text: "냉각 팬 소음 · 주간 확인 요청" });
  });

  it("check_failed: 실패 항목 줄 · ✕ 확인 · 실패 배너 · 확정 잠김(AC-07-C1)", () => {
    const s = load("s03-report-failed");
    const send = vi.fn();
    const { container } = render(<ReportScreen report={s.report!} busy={false} send={send} onHome={() => {}} />);
    expect(container.querySelector(".rf.fail .rk2")?.textContent).toBe("조치");
    expect(texts(container, ".ckl .ck.no")).toEqual(["근거 없는 문장 1건"]);
    expect(container.querySelector(".banner.bad b")?.textContent).toBe("근거 없는 문장 1건");
    expect(container.querySelector(".banner.bad div")?.textContent).toContain('"교체 후 온도 차 9.4 K로 회복"');
    const confirm = btn(container, "보고서 확정");
    expect(confirm.className).toContain("dis");
    fireEvent.click(confirm);
    expect(send).not.toHaveBeenCalled();
    expect(container.querySelector(".cta2 .note")?.textContent).toBe("확정 전 확인을 모두 통과해야 확정할 수 있습니다.");
  });

  it("confirmed: 확정 · 승인 대기 칩, 고치기 없음, 확정 배너 · 홈으로(AC-33)", () => {
    const s = load("s03-report-confirmed");
    const onHome = vi.fn();
    const { container } = render(<ReportScreen report={s.report!} busy={false} send={() => {}} onHome={onHome} />);
    expect(container.querySelector(".cd-h .ch.green")?.textContent).toBe("확정 · 승인 대기");
    expect(container.querySelectorAll(".rf .ed svg").length).toBe(0);
    fireEvent.click(container.querySelector(".rf .ed")!);
    expect(container.querySelector(".rf textarea")).toBeNull();
    expect(container.querySelector(".banner.ok b")?.textContent).toMatch(/^보고서를 확정했습니다 · \d\d:\d\d$/);
    fireEvent.click(btn(container, "홈으로"));
    expect(onHome).toHaveBeenCalled();
  });

  it("low_evidence · monitor_report · 원인 미상: 근거 적음 칩 · 확정 원인 값(AC-29-C2 · AC-22 · AC-21-C3)", () => {
    let r = render(<ReportScreen report={load("s03-report-low-evidence").report!} busy={false} send={() => {}} onHome={() => {}} />);
    expect(r.container.querySelector('[data-field="evidence_records"] .rv2 .ch.amber')?.textContent).toBe("근거 적음");
    cleanup();
    r = render(<ReportScreen report={load("s03-monitor-report").report!} busy={false} send={() => {}} onHome={() => {}} />);
    expect(r.container.querySelector('[data-field="cause"] .rv2')?.textContent).toBe("이상 없음 · 감시");
    cleanup();
    r = render(<ReportScreen report={load("s03-report-unknown").report!} busy={false} send={() => {}} onHome={() => {}} />);
    expect(r.container.querySelector('[data-field="cause"] .rv2')?.textContent).toBe("원인 미상");
  });

  it("원문 대체된 원인 · 조치 칸에만 '원문으로 대체됨' 표지(EV-001 CH-21 · VC-46)", () => {
    const base = load("s03-report-draft").report!;
    const report = { ...base, fields: base.fields.map((f) => (f.key === "cause" ? { ...f, fallback: true } : f.key === "action" ? { ...f, fallback: false } : f)) };
    const { container } = render(<ReportScreen report={report} busy={false} send={() => {}} onHome={() => {}} />);
    expect(texts(container, '[data-field="cause"] .ch.fb')).toEqual(["원문으로 대체됨"]);
    expect(container.querySelectorAll(".ch.fb")).toHaveLength(1); // 조치(false) · 나머지 6칸(칸 없음)은 표지 없음
    expect(container.querySelector('[data-field="cause"] .rv2')?.textContent).toBe(`원문으로 대체됨 ${base.fields.find((f) => f.key === "cause")!.text}`);
  });
});

describe("진행 표시 · 점검 경로", () => {
  it("조치 · 재가동 · 감시 마감 = 4, 보고서 = 5, 호출 · 인계 = 3", () => {
    expect(stepNumber(load("s03-action-a"), "lock")).toBe(4);
    expect(stepNumber(load("s03-restart-value"), "lock")).toBe(4);
    expect(stepNumber(load("s03-monitor-close"), "lock")).toBe(4);
    expect(stepNumber(load("s03-report-draft"), "lock")).toBe(5);
    expect(stepNumber(load("s03-report-confirmed"), "lock")).toBe(5);
    expect(stepNumber(load("s03-call-summary"), "lock")).toBe(3);
    expect(stepNumber(load("s03-handover-unable"), "lock")).toBe(3);
    expect(stepNumber(load("s03-ans-daytime"), "lock", false)).toBe(3); // 답 화면에서 '보고서 작성' 전
  });

  it("정정으로 무효인 기록은 지우지 않고 회색 점 · '정정으로 무효'", () => {
    const path = [
      { at: "2026-10-13T17:20:00+00:00", title: "냉각수 수위 확인", detail: "정상", status: "void" },
      { at: null, title: "흡기 필터 교체", detail: "4.3.2절", status: "now" },
    ];
    const { container } = render(<PathCard path={path} />);
    expect(container.querySelector(".tli.void .ch.gray.vd")?.textContent).toBe("정정으로 무효");
  });
});

describe("T02 홈 완료 행 · 최근 보고서 · T12 답이 온 호출", () => {
  it("이 교대 확정 보고서: 초록 점 '보고서 확정 · 승인 대기' · 보기, 처리 완료 · 호출 수, 최근 보고서 칩(PBC-4 v8 해석 ③)", () => {
    const home = load<Home>("home-done");
    const onOpen = vi.fn();
    const { container } = render(<HomeScreen home={home} onOpen={onOpen} />);
    const rows = [...container.querySelectorAll(".al")];
    expect(rows.map((r) => r.querySelector(".dot")?.className)).toEqual(["dot red", "dot amber", "dot green"]);
    expect(rows[2].querySelector(".al-m span")?.textContent).toMatch(/^\d\d:\d\d · 보고서 확정 · 승인 대기$/);
    fireEvent.click(rows[2].querySelector(".btn")!);
    expect(onOpen).toHaveBeenCalledWith(expect.objectContaining({ status: "done", report_session_id: home.recent_reports[0].session_id }));
    expect(texts(container, ".kt b")).toEqual(["1", "1", "1"]);
    expect(texts(container, ".rl span:first-child")[0]).toMatch(/^M-01 · 냉각 필터 막힘 · /);
    expect(texts(container, ".rl .ch")).toEqual(["승인 대기"]);
    expect(container.querySelector(".rl .ch")?.className).toBe("ch amber");
  });

  it("최근 보고서 시각: 오늘은 시:분, 어제는 '어제 시:분'", () => {
    const now = new Date("2026-10-13T18:00:00+09:00");
    expect(dayTime("2026-10-13T00:29:00+09:00", now)).toBe("00:29");
    expect(dayTime("2026-10-12T22:44:00+09:00", now)).toBe("어제 22:44");
  });

  it("종 목록: 진행 중 '· 파트장 답 도착', '파트장 답이 온 호출' 묶음 · 답 보기(AC-37-C1 · C2)", () => {
    const data = load<Notifications>("notifications-answered");
    const onItem = vi.fn();
    const { container } = render(<NotifyPanel data={data} onItem={onItem} />);
    expect(texts(container, ".grp")).toEqual(["진행 중인 점검", "파트장 답이 온 호출"]);
    expect(texts(container, ".nt-item .al-m span").filter((t) => / · 파트장 답 도착$/.test(t)).length).toBe(
      data.items.filter((i) => i.kind === "in_progress" && i.answer).length,
    );
    const last = [...container.querySelectorAll(".nt-item")].at(-1)!;
    expect(last.querySelector(".dot")?.className).toBe("dot green");
    expect(last.querySelector("b")?.textContent).toBe("M-04 · 냉각 팬 분해 점검(4.4, C)");
    expect(last.querySelector(".al-m span")?.textContent).toMatch(/^박 파트장 \d\d:\d\d · 승인 후 진행$/);
    fireEvent.click(last.querySelector(".btn")!);
    expect(onItem).toHaveBeenCalledWith(expect.objectContaining({ kind: "answered_call", session_id: data.items.at(-1)!.session_id }));
  });
});

describe("세션 화면 넘김(기기 표시)", () => {
  const mount = (view: SessionView) => {
    const ok = (data: unknown) => Promise.resolve({ data, error: undefined, response: { status: 200 } });
    const api = { GET: vi.fn(() => ok(view)), POST: vi.fn(() => ok(view)) } as unknown as Api;
    return render(
      <Session
        api={api}
        sid={view.session_id}
        initial={null}
        onSession={() => {}}
        onExpired={() => {}}
        onRecord={() => {}}
        onManual={() => {}}
        onHome={() => {}}
      />,
    );
  };

  it("승인 답: 승인 화면 → '점검 시작' → 그 C 점검 지시 · 결과 입력(T10 / ans_approved → T06)", async () => {
    const { container } = mount(load("s03-ans-approved"));
    await waitFor(() => expect(container.querySelector(".banner.ok")).not.toBeNull());
    await act(async () => fireEvent.click(btn(container, "점검 시작")));
    expect(container.querySelector(".rbtns")).not.toBeNull();
    expect(container.querySelector(".ins-h h3")?.textContent).toBe("냉각 팬 분해 점검");
  });

  it("주간 처리 답: 답 화면 → '보고서 작성' → 보고서(T10 / ans_daytime → T09)", async () => {
    const { container } = mount(load("s03-ans-daytime"));
    await waitFor(() => expect(container.querySelector(".banner.warn")).not.toBeNull());
    expect(container.querySelector(".sp.on")?.textContent).toBe("3점검");
    await act(async () => fireEvent.click(btn(container, "보고서 작성")));
    expect(container.querySelector(".rf")).not.toBeNull();
    expect(container.querySelector(".sp.on")?.textContent).toBe("5보고서");
    expect(container.querySelector('[data-field="unresolved"] .rv2')?.textContent).toContain("주간 처리 요청");
  });
});

describe("S-04 정비자 쪽: 반려 · 숙련자 인계 답 · 직접 확인(결정 017 ① · 018 ③ ④)", () => {
  it("T02 / rejected: 최근 보고서 반려 칩 · 반려 사유 배너(파트장 · 시각) · '이어서 하기'(AC-11-C1)", () => {
    const home = load<Home>("home-rejected");
    const onResume = vi.fn();
    const { container } = render(<HomeScreen home={home} onOpen={() => {}} onResume={onResume} />);
    const rej = home.recent_reports.find((r) => r.status === "rejected")!;
    expect(container.querySelector(".rl .ch.red")?.textContent).toBe("반려");
    expect(container.querySelector(".banner.bad b")?.textContent).toMatch(new RegExp(`^반려 사유 · ${rej.rejected_by_name} \\d\\d:\\d\\d$`));
    expect(container.querySelector(".banner.bad div")?.textContent).toContain(rej.reject_reason!);
    fireEvent.click(container.querySelector(".banner.bad + .btn.ghost.full")!); // 알람 행의 '이어서 하기'와 다른 버튼
    expect(onResume).toHaveBeenCalledWith(rej.session_id);
  });

  it("T12: '반려된 보고서' 묶음 · '보고서 보기' → 그 세션(AC-37-C1 · C2)", () => {
    const data = load<Notifications>("notifications-rejected");
    const onItem = vi.fn();
    const { container } = render(<NotifyPanel data={data} onItem={onItem} />);
    expect(texts(container, ".grp")).toEqual(["진행 중인 점검", "파트장 답이 온 호출", "반려된 보고서"]);
    const last = [...container.querySelectorAll(".nt-item")].at(-1)!;
    expect(last.querySelector(".dot")?.className).toBe("dot red");
    expect(last.querySelector(".al-m span")?.textContent).toMatch(/· 필터 표면 상태를 메모로 다시 적어 주세요$/);
    fireEvent.click(last.querySelector(".btn")!);
    expect(onItem).toHaveBeenCalledWith(expect.objectContaining({ kind: "rejected_report" }));
  });

  it("숙련자 인계 보낸 뒤 · 답 온 뒤(결정 018 ④): 보냄 배너 · 답 대기 → 답 배너 · '보고서 작성'", () => {
    const sent = load("s04-handover-sent");
    let r = render(<HandoverScreen s={sent} busy={false} send={() => {}} />);
    expect(r.container.querySelector(".banner.info b")?.textContent).toMatch(/^숙련자 인계를 보냈습니다 · \d\d:\d\d$/);
    expect([...r.container.querySelectorAll(".btn")].length).toBe(0);
    cleanup();
    const onReport = vi.fn();
    r = render(<HandoverScreen s={load("s04-handover-answered")} busy={false} send={() => {}} onReport={onReport} />);
    expect(r.container.querySelector(".banner.ok b")?.textContent).toMatch(/^주간 숙련자 배정 · 박 파트장 \d\d:\d\d$/);
    fireEvent.click(btn(r.container, "보고서 작성"));
    expect(onReport).toHaveBeenCalled();
  });

  it("반려 뒤 다시 열린 보고서는 초안(고칠 수 있음) · 확정 가능(AC-11-C2)", () => {
    const s = load("s04-report-reopened");
    const { container } = render(<ReportScreen report={s.report!} busy={false} send={() => {}} onHome={() => {}} />);
    expect(container.querySelector(".cd-h .ch.amber")?.textContent).toBe("초안");
    expect(container.querySelectorAll(".rf .ed svg").length).toBe(8);
    expect(btn(container, "보고서 확정").className).not.toContain("dis");
  });
});
