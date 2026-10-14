// L05 권한 등급: 절별 등급 표(결정 018 ② — 등급표 전부, 'n절 중 n절 표시') · 등급 고르기(A ~ D) · 낮춤 / 올림 경고(EV-062, 모든 변경)
// · 취소 / 변경 저장(경고를 확인해야 저장 — AC-25-C3) · 변경 기록(누가 · 언제 · 전 · 후 — AC-25-C2). 경고 문구는 서버가 준다.

import { useState } from "react";
import { dateTime, GradeBadge, GRADE_LABEL, Icon, type Api, type Schemas } from "@c1a15/ui";
import { Btn } from "./Frame";

type Grades = Schemas["LeadGrades"];
type Warning = Schemas["GradeWarning"];

export function GradesScreen({ api, data, onChanged }: { api: Api; data: Grades; onChanged: () => void }) {
  const [open, setOpen] = useState<string | null>(null);
  const [pending, setPending] = useState<{ section: string; grade: string; warning: Warning } | null>(null);
  const [busy, setBusy] = useState(false);

  const pick = async (section: string, grade: string, current: string) => {
    if (grade === current) {
      setOpen(null);
      setPending(null);
      return;
    }
    const { data: w } = await api.GET("/api/lead/grades/{section}/warning", {
      params: { path: { section }, query: { grade } },
    });
    if (w) setPending({ section, grade, warning: w });
  };
  const save = async () => {
    if (!pending) return;
    setBusy(true);
    const { data: r } = await api.POST("/api/lead/grades/{section}", {
      params: { path: { section: pending.section } },
      body: { grade: pending.grade as "A" | "B" | "C" | "D", confirmed: true },
    });
    setBusy(false);
    if (r) {
      setPending(null);
      setOpen(null);
      onChanged();
    }
  };

  return (
    <div className="wg">
      <div className="cd">
        <div className="cd-h">
          <Icon name="book-open" />
          <b>매뉴얼 절별 권한 등급</b>
          <span className="ch gray">
            {data.total}절 중 {data.rows.length}절 표시
          </span>
        </div>
        <table className="wt">
          <tbody>
            <tr>
              <th>절</th>
              <th>작업</th>
              <th>등급</th>
            </tr>
            {data.rows.map((r) => {
              const shown = pending?.section === r.section ? pending.grade : r.grade;
              return (
                <tr key={r.section} data-section={r.section}>
                  <td>
                    <b>{r.section}</b>
                  </td>
                  <td>{r.title}</td>
                  <td className="pos-r">
                    <span
                      className="sel2"
                      role="button"
                      tabIndex={0}
                      aria-label={`${r.section} 등급 고르기`}
                      onClick={() => setOpen(open === r.section ? null : r.section)}
                    >
                      <GradeBadge grade={shown} />
                      <Icon name="arrow-right" className="rot" />
                    </span>
                    {open === r.section ? (
                      <div className="dd" style={{ right: 0, top: 34 }}>
                        {["A", "B", "C", "D"].map((g) => (
                          <div key={g} className={g === shown ? "on" : ""} role="option" aria-selected={g === shown} onClick={() => void pick(r.section, g, r.grade)}>
                            {g} {GRADE_LABEL[g]}
                          </div>
                        ))}
                      </div>
                    ) : null}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
      {pending ? (
        <div className="cd">
          <div className={`banner ${pending.warning.direction === "raise" ? "info" : "warn"}`}>
            <Icon name="triangle-alert" />
            <div>
              <b>{pending.warning.head}</b>
              {pending.warning.body}
            </div>
          </div>
          <div className="choice2">
            <Btn
              cls="ghost"
              label="취소"
              onClick={() => {
                setPending(null);
                setOpen(null);
              }}
            />
            <Btn
              cls={pending.warning.direction === "raise" ? "" : "warnb"}
              label={`${pending.grade}로 변경 저장`}
              off={busy}
              onClick={() => void save()}
            />
          </div>
        </div>
      ) : (
        <div className="cd ">
          <div className="cd-h">
            <Icon name="history" />
            <b>변경 기록</b>
          </div>
          {data.changes.length === 0 ? (
            <div className="empty">
              <Icon name="history" />
              아직 변경 기록이 없습니다
            </div>
          ) : (
            <table className="wt">
              <tbody>
                <tr>
                  <th>시각</th>
                  <th>절</th>
                  <th>변경</th>
                  <th>사용자</th>
                </tr>
                {data.changes.map((ch, i) => (
                  <tr key={i}>
                    <td>{ch.at ? dateTime(ch.at) : ""}</td>
                    <td>
                      <b>{ch.section}</b> {ch.title}
                    </td>
                    <td>
                      {ch.before} → {ch.after}
                    </td>
                    <td>{ch.by_name}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
          <div className="hint">
            <Icon name="info" />
            등급은 이 화면에서만 바꿀 수 있고, 바꾼 내용은 모두 감사 기록에 남습니다.
          </div>
        </div>
      )}
    </div>
  );
}
