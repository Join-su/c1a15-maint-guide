// L04 처리할 호출: 목록(유형 · 설비 · 시각 · 필요한 작업 · 보낸 사람 · 답하기) · 상세(정비자 요약 · 답 선택지 · 처리 메모 · 답 저장).
// 선택지는 서버가 준다(D등급 호출에는 '승인 후 진행'이 없음 — AC-23-C3). 보낸 뒤 정비자 정정 상자(L04 / call_corrected, S-05 P-15).

import { useState } from "react";
import { errorDetail, hhmm, Icon, type Api, type Schemas } from "@c1a15/ui";
import { Btn, Options } from "./Frame";

type Calls = Schemas["LeadCalls"];
type Call = Schemas["LeadCall"];

/** 정정 전 → 후: 결과가 바뀌면 결과, 아니면 메모 · 측정값. */
function change(before: Record<string, unknown> | null | undefined, after: Record<string, unknown> | null | undefined): string {
  const b = before ?? {};
  const a = { ...b, ...(after ?? {}) };
  if ("values" in b) return `${String(b.values ?? "")} → ${String(a.values ?? "")}`;
  if (b.value !== a.value) return `${String(b.value)} → ${String(a.value)}`;
  return `메모 '${String(b.memo ?? "")}' → '${String(a.memo ?? "")}'`;
}

const KIND: Record<string, { label: string; chip: string }> = {
  approval: { label: "파트장 호출", chip: "amber" },
  handover: { label: "숙련자 인계", chip: "red" },
};

export function CallList({ data, onOpen }: { data: Calls; onOpen: (callId: number) => void }) {
  return (
    <div className="cd">
      <table className="wt">
        <tbody>
          <tr>
            <th>유형</th>
            <th>설비 · 알람</th>
            <th>시각</th>
            <th>필요한 작업</th>
            <th>보낸 사람</th>
            <th />
          </tr>
          {data.rows.map((r) => (
            <tr key={r.call_id} className="" data-call={r.call_id}>
              <td>
                <span className={`ch ${KIND[r.kind].chip}`}>{KIND[r.kind].label}</span>
              </td>
              <td>
                <b>
                  {r.equipment_id} · {r.group_name}
                </b>
              </td>
              <td>{r.sent_at ? hhmm(r.sent_at) : ""}</td>
              <td>{r.need}</td>
              <td>{r.sender_name}</td>
              <td>
                <Btn cls="sm2" label="답하기" onClick={() => onOpen(r.call_id)} />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      {data.rows.length === 0 ? (
        <div className="empty">
          <Icon name="phone-call" />
          처리할 호출이 없습니다
        </div>
      ) : null}
    </div>
  );
}

export function CallDetail({ api, call, onDone }: { api: Api; call: Call; onDone: () => void }) {
  const [answer, setAnswer] = useState<string | null>(call.options[0]?.value ?? null);
  const [note, setNote] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const save = async () => {
    if (!answer) return;
    setBusy(true);
    const { data, error: err } = await api.POST("/api/lead/calls/{call_id}/answer", {
      params: { path: { call_id: call.call_id } },
      body: { answer: answer as "approved" | "daytime" | "direct" | "assign", note: note.trim() || null },
    });
    setBusy(false);
    if (data) onDone();
    else setError(errorDetail(err) ?? "save_failed");
  };

  return (
    <div className="wg">
      <div className="cd">
        <div className="cd-h">
          <Icon name="phone-call" />
          <b>
            {call.equipment_id} · {KIND[call.kind].label} · {call.sent_at ? hhmm(call.sent_at) : ""}
          </b>
        </div>
        <div className="pv">
          <span className="sm">정비자가 보낸 요약</span>
          <p>{call.summary}</p>
        </div>
        {(call.corrections ?? []).map((x, i) => (
          // L04 / call_corrected: 보낸 뒤 정비자 정정(AC-47-C2 · 결정 019 ② ③) — 새 호출 없이 이 호출에 붙는다
          <div className="corr-box" key={i}>
            <Icon name="pencil" />
            <b>보낸 뒤 정비자 정정 · {x.at ? hhmm(x.at) : ""}</b>
            <div>
              {x.section} {x.title} · {change(x.before, x.after)}
            </div>
            <span className="sm">사유 · {x.reason}. 이 호출을 보낸 뒤라 다시 판정하지 않았습니다.</span>
          </div>
        ))}
      </div>
      <div className="cd">
        <div className="cd-h">
          <Icon name="file-check-2" />
          <b>답하기</b>
        </div>
        <Options options={call.options} value={answer} onChange={setAnswer} />
        <textarea className="memo sm3" aria-label="처리 메모" placeholder="처리 메모" value={note} onChange={(e) => setNote(e.target.value)} />
        {call.kind === "approval" ? <span className="note">D등급 작업 호출에는 "승인 후 진행"이 없습니다.</span> : null}
        {error ? (
          <div className="banner bad" role="alert">
            <Icon name="circle-alert" />
            <div>
              <b>저장하지 못했습니다</b>
              {error}
            </div>
          </div>
        ) : null}
        <Btn label="답 저장" off={busy || !answer || call.answered} onClick={() => void save()} />
      </div>
    </div>
  );
}
