// L06 감사 기록: 필터 3개(설비 · 사용자 · 기간 — 바꾸면 즉시 걸러짐, AC-26-C2) · 표(시각 · 사용자 · 앱 · 행동 · 대상, 시간 역순).
// 행동 문구 · 대상 · 사용자 이름은 서버가 준다. 정비자 정정 행(L06 / correction)은 S-05(P-15).

import { useState } from "react";
import { dateTime, hhmm, type Schemas } from "@c1a15/ui";

type Audit = Schemas["LeadAudit"];
export type AuditFilter = { equipment: string | null; user_id: string | null; date: string | null };

function Select({
  label,
  value,
  options,
  onPick,
}: {
  label: string;
  value: string;
  options: { value: string | null; label: string }[];
  onPick: (v: string | null) => void;
}) {
  const [open, setOpen] = useState(false);
  return (
    <span className="sel2" style={{ position: "relative" }} role="button" tabIndex={0} aria-label={`${label} 고르기`} onClick={() => setOpen(!open)}>
      {label} · {value}
      {open ? (
        <div className="dd" style={{ left: 0, top: 34 }}>
          {options.map((o) => (
            <div
              key={o.label}
              role="option"
              aria-selected={o.label === value}
              className={o.label === value ? "on" : ""}
              onClick={(e) => {
                e.stopPropagation();
                setOpen(false);
                onPick(o.value);
              }}
            >
              {o.label}
            </div>
          ))}
        </div>
      ) : null}
    </span>
  );
}

function days(today: string): string[] {
  const d = new Date(`${today}T12:00:00+09:00`);
  return Array.from({ length: 7 }, (_, i) => new Date(d.getTime() - i * 86400000).toISOString().slice(0, 10));
}

export function AuditScreen({ data, onFilter }: { data: Audit; onFilter: (f: AuditFilter) => void }) {
  const f: AuditFilter = { equipment: data.filters.equipment ?? null, user_id: data.filters.user_id ?? null, date: data.date };
  const userName = data.options.users.find((u) => u.user_id === f.user_id)?.name ?? "전체";
  return (
    <>
      <div className="flt">
        <Select
          label="설비"
          value={f.equipment ?? "전체"}
          options={[{ value: null, label: "전체" }, ...data.options.equipment.map((e) => ({ value: e, label: e }))]}
          onPick={(v) => onFilter({ ...f, equipment: v })}
        />
        <Select
          label="사용자"
          value={userName}
          options={[{ value: null, label: "전체" }, ...data.options.users.map((u) => ({ value: u.user_id, label: u.name }))]}
          onPick={(v) => onFilter({ ...f, user_id: v })}
        />
        <Select
          label="기간"
          value={data.date}
          options={days(dateTime(data.now).slice(0, 10)).map((d) => ({ value: d, label: d }))}
          onPick={(v) => onFilter({ ...f, date: v })}
        />
      </div>
      <div className="cd">
        <table className="wt">
          <tbody>
            <tr>
              <th>시각</th>
              <th>사용자</th>
              <th>앱</th>
              <th>행동</th>
              <th>대상</th>
            </tr>
            {data.rows.map((r) => (
              <tr key={r.audit_id}>
                <td>{hhmm(r.at)}</td>
                <td>{r.user_name}</td>
                <td>{r.app}</td>
                <td>{r.action}</td>
                <td>{r.target}</td>
              </tr>
            ))}
          </tbody>
        </table>
        {data.rows.length === 0 ? <div className="empty">조건에 맞는 기록이 없습니다</div> : null}
      </div>
    </>
  );
}
