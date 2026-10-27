// L02 승인 대기(요약 타일 3개 · 표 · 빈 목록) · L03 보고서 검토(그대로 승인 · 수정 후 승인 · 반려).
// 값은 /api/lead/overview · /api/lead/reports/{id}(P-11). 수정 문장 근거 검사(R8)는 서버가 한다(/check).

import { useEffect, useRef, useState } from "react";
import { errorDetail, hhmm, Icon, type Api, type Schemas } from "@c1a15/ui";
import { Btn, Options } from "./Frame";

type Overview = Schemas["LeadOverview"];
type Report = Schemas["LeadReport"];
type Check = Schemas["EditCheck"];
type Decision = "approve" | "edit" | "reject";

const DECISIONS: { value: Decision; label: string; hint: string }[] = [
  { value: "approve", label: "그대로 승인", hint: "이력에 추가되고 다음 진단의 근거로 쓰입니다" },
  { value: "edit", label: "수정 후 승인", hint: "왼쪽 항목을 직접 고치고 이유를 적으면 반영 후 승인됩니다" },
  { value: "reject", label: "반려", hint: "사유와 함께 작성자에게 돌아갑니다" },
];

export function ApprovalList({ data, onOpen }: { data: Overview; onOpen: (reportId: number) => void }) {
  const t = data.tiles;
  return (
    <>
      <div className="kts w">
        <div className="kt">
          <b>{t.awaiting}</b>
          <span>승인 대기</span>
        </div>
        <div className="kt">
          <b>{t.calls_open}</b>
          <span>처리할 호출</span>
        </div>
        <div className="kt">
          <b>{t.violations}</b>
          <span>권한 위반</span>
        </div>
      </div>
      <div className="cd">
        <table className="wt">
          <tbody>
            <tr>
              <th>설비 · 알람</th>
              <th>확정 원인</th>
              <th>작성</th>
              <th>확정 시각</th>
              <th>근거 기록</th>
              <th>권한</th>
              <th />
            </tr>
            {data.rows.map((r, i) => (
              <tr key={r.report_id} className={r.low_evidence ? "low" : i === 0 ? "on" : ""} data-report={r.report_id}>
                <td>
                  <b>{r.equipment_id}</b>
                  <span>{r.group_name}</span>
                </td>
                <td>{r.cause}</td>
                <td>{r.author_name}</td>
                <td>{r.confirmed_at ? hhmm(r.confirmed_at) : ""}</td>
                <td>
                  {r.evidence_count}건{r.low_evidence ? <span className="ch amber">근거 적음</span> : null}
                </td>
                <td>
                  <span className={`ch ${r.violations ? "red" : "green"}`}>위반 {r.violations}</span>
                </td>
                <td>
                  <Btn cls="sm2" label="검토" onClick={() => onOpen(r.report_id)} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {data.rows.length === 0 ? (
          <div className="empty">
            <Icon name="file-check-2" />
            승인 대기 보고서가 없습니다
          </div>
        ) : null}
      </div>
    </>
  );
}

export function Review({ api, report, onDone }: { api: Api; report: Report; onDone: () => void }) {
  const [decision, setDecision] = useState<Decision>("approve");
  const [memo, setMemo] = useState("");
  const [edits, setEdits] = useState<Record<string, string>>({});
  const [check, setCheck] = useState<Check | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const changed = Object.fromEntries(
    Object.entries(edits).filter(([k, v]) => v !== report.fields.find((f) => f.key === k)?.text),
  );
  const changedKey = JSON.stringify(changed);
  useEffect(() => {
    if (decision !== "edit" || !Object.keys(changed).length) {
      setCheck(null);
      return;
    }
    const id = setTimeout(async () => {
      const { data } = await api.POST("/api/lead/reports/{report_id}/check", {
        params: { path: { report_id: report.report_id } },
        body: { edits: changed },
      });
      if (data) setCheck(data);
    }, 300);
    return () => clearTimeout(id);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [changedKey, decision]);

  const failing = new Set((check?.fields ?? []).filter((f) => !f.ok).map((f) => f.key));
  const needReason = decision === "reject" && !memo.trim();
  const blocked =
    busy ||
    needReason ||
    (decision === "edit" && (!Object.keys(changed).length || !check || !check.ok));

  const saving = useRef(false); // EV-007: 같은 순간 두 번 누름도 한 번만 보냄
  const save = async () => {
    if (saving.current) return;
    saving.current = true;
    setBusy(true);
    setError(null);
    const { data, error: err } = await api.POST("/api/lead/reports/{report_id}/decision", {
      params: { path: { report_id: report.report_id } },
      body: { decision, edits: decision === "edit" ? changed : {}, memo: memo.trim() || null },
    });
    setBusy(false);
    saving.current = false;
    if (data) onDone();
    else setError(errorDetail(err) ?? "save_failed");
  };

  return (
    <div className="wg">
      <div className="cd">
        <div className="cd-h">
          <Icon name="file-text" />
          <b>
            {report.equipment_id} · {report.group_name} · {report.occurred_at ? hhmm(report.occurred_at) : ""}
          </b>
          <span className="ch gray">{report.author_name} 작성</span>
        </div>
        {report.fields.map((f) => {
          const editing = decision === "edit" && f.key in edits;
          return (
            <div className={`rf${failing.has(f.key) ? " fail" : ""}`} key={f.key} data-field={f.key}>
              <span className="rk2">{f.label}</span>
              {editing ? (
                <textarea
                  className="rv2 edit-in"
                  aria-label={`${f.label} 고치기`}
                  value={edits[f.key]}
                  autoFocus
                  onChange={(e) => setEdits({ ...edits, [f.key]: e.target.value })}
                />
              ) : (
                <span
                  className="rv2"
                  role={decision === "edit" ? "button" : undefined}
                  tabIndex={decision === "edit" ? 0 : undefined}
                  onClick={() => decision === "edit" && setEdits({ ...edits, [f.key]: f.text })}
                >
                  {f.text}
                </span>
              )}
            </div>
          );
        })}
      </div>
      <div className="cd">
        <div className="cd-h">
          <Icon name="file-check-2" />
          <b>검토 결정</b>
        </div>
        <Options options={DECISIONS} value={decision} onChange={(d) => setDecision(d)} />
        <textarea
          className="memo sm3"
          aria-label="메모"
          placeholder={decision === "reject" ? "반려 사유" : decision === "edit" ? "고친 이유" : "메모 (선택)"}
          style={needReason ? { borderColor: "var(--bad)" } : undefined}
          value={memo}
          onChange={(e) => setMemo(e.target.value)}
        />
        {needReason ? <div className="req">반려 사유를 입력해야 저장됩니다</div> : null}
        {decision === "edit" && check && !check.ok ? (
          <div className="banner bad">
            <Icon name="circle-alert" />
            <div>
              <b>근거 검사 실패</b>
              {check.messages.join(" ")}
            </div>
          </div>
        ) : null}
        {error ? (
          <div className="banner bad" role="alert">
            <Icon name="circle-alert" />
            <div>
              <b>저장하지 못했습니다</b>
              {error}
            </div>
          </div>
        ) : null}
        <Btn label="결정 저장" off={blocked} onClick={() => void save()} />
      </div>
    </div>
  );
}
