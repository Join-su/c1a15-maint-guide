// T02 홈 · T12 알람 · 할 일(종 목록). 값은 /api/tech/home · /api/tech/notifications 응답 그대로(P-19 ① · ②, S-03 P-09).

import { Fragment } from "react";
import { dateTime, hhmm, Icon, type Home as HomeData, type Notifications } from "@c1a15/ui";

type Row = HomeData["alarms"][number];

const REPORT: Record<string, { label: string; chip: string }> = {
  awaiting_approval: { label: "승인 대기", chip: "amber" },
  approved: { label: "승인 완료", chip: "green" },
  rejected: { label: "반려", chip: "red" },
};

function rowState(a: Row): { dot: string; text: string; button: string; ghost: boolean } {
  if (a.status === "new") return { dot: "red", text: `${hhmm(a.occurred_at)} · 새 알람`, button: "점검 시작", ghost: false };
  if (a.status === "done") {
    const label = REPORT[a.report_status ?? ""]?.label ?? "";
    return { dot: "green", text: `${hhmm(a.occurred_at)} · 보고서 확정 · ${label}`, button: "보기", ghost: true };
  }
  const p = a.progress;
  const n = p && p.check_no > 0 ? `점검 ${p.check_no} / 최대 ${p.check_max} 진행 중` : "진행 중";
  return { dot: "amber", text: `${hhmm(a.occurred_at)} · ${n}`, button: "이어서 하기", ghost: true };
}

/** 새 알람(빨강) → 진행 중 → 완료(이 교대에 확정한 보고서) 순, 같은 상태 안에서는 서버 순서(최근 먼저). */
export function sortedAlarms(h: HomeData): Row[] {
  const rank = (a: Row) => (a.status === "new" ? 0 : a.status === "done" ? 2 : 1);
  return [...h.alarms].sort((a, b) => rank(a) - rank(b));
}

export function HomeScreen({
  home,
  onOpen,
  onResume,
}: {
  home: HomeData;
  onOpen: (a: Row) => void;
  onResume?: (sessionId: number) => void;
}) {
  const rows = sortedAlarms(home);
  const rejected = home.recent_reports.find((r) => r.status === "rejected");
  const s = home.shift;
  return (
    <div className="ap-body nostep">
      <div className="g2">
        <div>
          <div className="cd ">
            <div className="cd-h">
              <Icon name="bell" />
              <b>내 알람</b>
              {rows.length ? <span className="cnt">{rows.length}</span> : null}
            </div>
            {rows.length === 0 ? (
              <div className="empty">
                <Icon name="bell" />
                배정된 알람이 없습니다
              </div>
            ) : (
              rows.map((a) => {
                const st = rowState(a);
                return (
                  <div className="al" key={a.alarm_id} data-alarm={a.alarm_id}>
                    <span className={`dot ${st.dot}`} />
                    <div className="al-m">
                      <b>
                        {a.equipment_id} · {a.group_name}
                      </b>
                      <span>{st.text}</span>
                    </div>
                    <span className={`btn ${st.ghost ? "ghost" : ""}`} role="button" tabIndex={0} onClick={() => onOpen(a)}>
                      {st.button}
                    </span>
                  </div>
                );
              })
            )}
          </div>
        </div>
        <div>
          <div className="cd ">
            <div className="cd-h">
              <Icon name="clock" />
              <b>
                오늘 교대 · {s.start_text} ~ {s.end_text}
              </b>
            </div>
            <div className="kts">
              <div className="kt">
                <b>{s.done}</b>
                <span>처리 완료</span>
              </div>
              <div className="kt">
                <b>{s.in_progress}</b>
                <span>진행 중</span>
              </div>
              <div className="kt">
                <b>{s.calls}</b>
                <span>파트장 호출</span>
              </div>
            </div>
          </div>
          <div className="cd mt">
            <div className="cd-h">
              <Icon name="shield" />
              <b>안전 수칙</b>
            </div>
            <div className="safe">
              <Icon name="lock" />
              <div>
                <b>잠금을 먼저 확인합니다</b>
                <span>잠금(1.2절)을 확인하기 전에는 어떤 점검 지시도 표시되지 않습니다.</span>
              </div>
            </div>
          </div>
          <div className="cd mt">
            <div className="cd-h">
              <Icon name="file-text" />
              <b>최근 내 보고서</b>
            </div>
            {home.recent_reports.length === 0 ? (
              <div className="empty">
                <Icon name="file-text" />
                최근 보고서가 없습니다
              </div>
            ) : (
              home.recent_reports.map((r) => (
                <div className="rl" key={r.report_id}>
                  <span>
                    {r.equipment_id} · {r.cause} · {r.confirmed_at ? dayTime(r.confirmed_at) : ""}
                  </span>
                  <span className={`ch ${REPORT[r.status]?.chip ?? "gray"}`}>{REPORT[r.status]?.label ?? r.status}</span>
                </div>
              ))
            )}
            {rejected ? ( // T02 / rejected(결정 017 ①, AC-11-C1): 반려 사유 · 파트장 · 시각 + 이어서 하기
              <>
                <div className="banner bad">
                  <Icon name="rotate-ccw" />
                  <div>
                    <b>
                      반려 사유 · {rejected.rejected_by_name} {rejected.rejected_at ? hhmm(rejected.rejected_at) : ""}
                    </b>
                    {rejected.reject_reason} "이어서 하기"로 추가 점검하거나 보고서 항목을 고친 뒤 다시 확정합니다.
                  </div>
                </div>
                <span className="btn ghost full" role="button" tabIndex={0} onClick={() => onResume?.(rejected.session_id)}>
                  이어서 하기
                </span>
              </>
            ) : null}
          </div>
        </div>
      </div>
    </div>
  );
}

/** 최근 보고서 시각: 오늘이면 "00:29", 다른 날이면 "어제 22:44" · "10-11 22:44"(현장 시각). */
export function dayTime(iso: string, now: Date = new Date()): string {
  const d = dateTime(iso).slice(0, 10);
  const today = dateTime(now.toISOString()).slice(0, 10);
  const yesterday = dateTime(new Date(now.getTime() - 86400000).toISOString()).slice(0, 10);
  if (d === today) return hhmm(iso);
  return `${d === yesterday ? "어제" : d.slice(5)} ${hhmm(iso)}`;
}

const ANSWER: Record<string, string> = {
  approved: "승인 후 진행",
  daytime: "주간 처리",
  direct: "직접 확인",
  assign: "주간 숙련자 배정",
};

const GROUPS: { kind: string; label: string; button: string; dot: string }[] = [
  { kind: "new_alarm", label: "배정된 새 알람", button: "알람 보기", dot: "red" },
  { kind: "in_progress", label: "진행 중인 점검", button: "이어서 하기", dot: "amber" },
  { kind: "answered_call", label: "파트장 답이 온 호출", button: "답 보기", dot: "green" },
  { kind: "rejected_report", label: "반려된 보고서", button: "보고서 보기", dot: "red" },
];

type Item = Notifications["items"][number];

function itemText(i: Item): { title: string; sub: string } {
  const when = i.occurred_at ? hhmm(i.occurred_at) : "";
  if (i.kind === "rejected_report") {
    // T12 / list '반려된 보고서'(결정 017 ①): 설비 · 원인 · 시각 / 파트장 · 시각 · 사유
    return {
      title: `${i.equipment_id} · ${i.report_cause} · ${when}`,
      sub: `${i.rejected_by_name ?? ""} ${i.rejected_at ? hhmm(i.rejected_at) : ""} · ${i.reject_reason ?? ""}`.trim(),
    };
  }
  if (i.kind === "answered_call") {
    const by = `${i.answered_by_name ?? i.answered_by ?? ""} ${i.answered_at ? hhmm(i.answered_at) : ""}`.trim();
    return {
      title: `${i.equipment_id} · ${i.call_title}(${i.call_section}, ${i.call_grade})`,
      sub: `${by} · ${ANSWER[i.answer ?? ""] ?? i.answer ?? ""}`,
    };
  }
  const p = i.progress;
  const sub =
    i.kind === "new_alarm"
      ? `${when} · 새 알람`
      : `${when} · ${p && p.check_no > 0 ? `점검 ${p.check_no} / 최대 ${p.check_max}` : "진행 중"}${i.answer ? " · 파트장 답 도착" : ""}`;
  return { title: `${i.equipment_id} · ${i.group_name}`, sub };
}

/** T12 종 목록 패널: 배정된 새 알람 · 진행 중인 점검 · 파트장 답이 온 호출 · 반려된 보고서(AC-37). */
export function NotifyPanel({
  data,
  onItem,
}: {
  data: Notifications;
  onItem: (item: Notifications["items"][number]) => void;
}) {
  return (
    <div className="panel" role="dialog" aria-label="알람 · 할 일">
      <div className="cd-h">
        <Icon name="bell" />
        <b>알람 · 할 일</b>
      </div>
      {data.empty ? (
        <div className="empty">
          <Icon name="bell" />
          알람 · 할 일이 없습니다
        </div>
      ) : (
        GROUPS.map((g) => {
          const items = data.items.filter((i) => i.kind === g.kind);
          if (!items.length) return null;
          return (
            <Fragment key={g.kind}>
              <div className="grp">{g.label}</div>
              {items.map((i) => {
                const t = itemText(i);
                return (
                  <div className="nt-item" key={`${i.kind}-${i.alarm_id}-${i.call_section ?? ""}`}>
                    <span className={`dot ${g.dot}`} />
                    <div className="al-m">
                      <b>{t.title}</b>
                      <span>{t.sub}</span>
                    </div>
                    <span className="btn ghost sm2" role="button" tabIndex={0} onClick={() => onItem(i)}>
                      {g.button}
                    </span>
                  </div>
                );
              })}
            </Fragment>
          );
        })
      )}
    </div>
  );
}
