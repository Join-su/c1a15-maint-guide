// EV-009 사람 판단(D-444 #18): ML 길에서 알람 없이 남은 후보(확신 낮음 · RNF · 예측 실패) 목록 — 호출 목록과 같은 표.
// [알람으로 올림]: 경계를 넘은 줄은 바로, 아니면 그 줄 아래에 증상군 고르기(ML 1위 제안 미리 고름) → [올림 저장].
// [문제없음]: 닫음. 판단이 끝난 줄은 서버가 409(두 번 누름도 한 번).

import { useRef, useState } from "react";
import { errorDetail, hhmm, Icon, type Api, type Schemas } from "@c1a15/ui";
import { Btn, Options } from "./Frame";

type Data = Schemas["LeadCandidates"];
type Row = Data["rows"][number];

const REASON: Record<string, { label: string; chip: string }> = {
  low_confidence: { label: "확신 낮음", chip: "amber" },
  rnf: { label: "RNF", chip: "gray" },
  model_failure: { label: "모델 실패", chip: "red" },
};

function ml(r: Row): string {
  const risk = r.risk == null ? "" : `위험도 ${Math.round(r.risk * 100)}%`;
  const top = r.top ? `${r.top.type} ${Math.round(r.top.probability * 100)}%` : "";
  return [risk, top].filter(Boolean).join(" · ") || "—";
}

export function JudgeList({ api, data, onChanged }: { api: Api; data: Data; onChanged: () => void }) {
  const [open, setOpen] = useState<number | null>(null);
  const [group, setGroup] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const saving = useRef(false); // 같은 순간 두 번 누름도 한 번만 보냄(EV-007과 같은 꼴)

  const decide = async (r: Row, decision: "promote" | "dismiss", g?: string | null) => {
    if (saving.current) return;
    saving.current = true;
    setBusy(true);
    setError(null);
    const { data: res, error: err } = await api
      .POST("/api/lead/candidates/{candidate_id}/decision", {
        params: { path: { candidate_id: r.candidate_id } },
        body: { decision, ...(g ? { group: g as "TW" | "PW" | "CL" | "LD" } : {}) },
      })
      .finally(() => {
        saving.current = false;
      });
    setBusy(false);
    if (res) {
      setOpen(null);
      onChanged();
    } else setError(errorDetail(err) ?? "save_failed");
  };
  const promote = (r: Row) => {
    if (r.group_fixed) return void decide(r, "promote");
    setOpen(r.candidate_id);
    setGroup(r.group_suggestion ?? null);
  };

  return (
    <div className="cd">
      <table className="wt">
        <tbody>
          <tr>
            <th>이유</th>
            <th>설비 · 시각</th>
            <th>센서 값</th>
            <th>ML</th>
            <th />
          </tr>
          {data.rows.map((r) => (
            <JudgeRow
              key={r.candidate_id}
              r={r}
              busy={busy}
              open={open === r.candidate_id}
              group={group}
              groups={data.groups}
              onGroup={setGroup}
              onPromote={() => promote(r)}
              onSave={() => void decide(r, "promote", group)}
              onDismiss={() => void decide(r, "dismiss")}
            />
          ))}
        </tbody>
      </table>
      {error ? (
        <div className="banner bad" role="alert">
          <Icon name="circle-alert" />
          <div>
            <b>저장하지 못했습니다</b>
            {error}
          </div>
        </div>
      ) : null}
      {data.rows.length === 0 ? (
        <div className="empty">
          <Icon name="circle-help" />
          사람 판단이 필요한 기록이 없습니다
        </div>
      ) : null}
    </div>
  );
}

function JudgeRow(p: {
  r: Row;
  busy: boolean;
  open: boolean;
  group: string | null;
  groups: Data["groups"];
  onGroup: (g: string) => void;
  onPromote: () => void;
  onSave: () => void;
  onDismiss: () => void;
}) {
  const { r } = p;
  const reason = REASON[r.reason] ?? { label: r.reason, chip: "gray" };
  return (
    <>
      <tr data-candidate={r.candidate_id}>
        <td>
          <span className={`ch ${reason.chip}`}>{reason.label}</span>
        </td>
        <td>
          <b>{r.equipment_id}</b>
          <span>{hhmm(r.created_at)}</span>
        </td>
        <td>{r.sensors_text}</td>
        <td>{ml(r)}</td>
        <td>
          <Btn cls="sm2" label="알람으로 올림" off={p.busy} onClick={p.onPromote} />
          <Btn cls="sm2" label="문제없음" off={p.busy} onClick={p.onDismiss} />
        </td>
      </tr>
      {p.open ? (
        <tr className="pick" data-pick={r.candidate_id}>
          <td colSpan={5}>
            <Options
              options={p.groups.map((g) => ({ value: g.value, label: g.label, hint: g.value }))}
              value={p.group}
              onChange={p.onGroup}
            />
            <Btn cls="sm2" label="올림 저장" off={p.busy || !p.group} onClick={p.onSave} />
          </td>
        </tr>
      ) : null}
    </>
  );
}
