// T15 지난 화면(S-05 P-15, AC-41 · 45 · 46 · 48): 진행 표시의 지나온 단계를 누르면 그 단계의 원래 화면을 그때 값으로 보기 상태로 보인다.
// 띠(R-PASTBAR) = '지난 화면 · 단계' · 제출 시각 · 보내지 않은 입력 '그대로' 칩 · 이전 · 다음(n / m) · 현재 단계로.
// 정비자가 입력한 결과 · 메모 · 사전 확인 측정값에만 '이 기록 정정', 그 밖의 기록은 '메모 덧붙이기'만(가능 여부는 서버 값).
// 다시 판정으로 열린 지시가 바뀌면 서버가 확인을 요구하고(confirm_required), 확인 창에서 보내지 않은 입력이 지워진다고 알린다.
// 값은 모두 API(/history) 값이고, 앱은 판정 · 정정 반영 방식을 정하지 않는다.

import { useState } from "react";
import { errorDetail, GradeBadge, hhmm, Icon, type Api, type Schemas, type SessionView } from "@c1a15/ui";
import { AlarmScreen } from "./Alarm";
import { DiagnosisScreen } from "./Diagnosis";
import { LockOk, Proc } from "./Lock";

export type PastData = Schemas["SessionPast"];
type Rec = Schemas["PastRecord"];
type Value = "정상" | "이상" | "확인 불가";
const VALUES: Value[] = ["정상", "이상", "확인 불가"];
const VICON: Record<Value, string> = { 정상: "circle-check", 이상: "circle-alert", "확인 불가": "circle-help" };

function Btn({ label, cls, off, onClick }: { label: string; cls: string; off?: boolean; onClick?: () => void }) {
  return (
    <span className={`btn${cls ? ` ${cls}` : ""}${off ? " dis" : ""}`} role="button" tabIndex={0} aria-disabled={off} onClick={() => !off && onClick?.()}>
      {label}
    </span>
  );
}

function IconBtn({ label, icon, cls, onClick }: { label: string; icon: string; cls: string; onClick: () => void }) {
  // template: <span class="btn lg full ghost"><I:pencil/>이 기록 정정</span> — 아이콘이 앞
  return (
    <span className={`btn ${cls}`} role="button" tabIndex={0} onClick={onClick}>
      <Icon name={icon} />
      {label}
    </span>
  );
}

function fmtBefore(v: Record<string, unknown> | null | undefined): string {
  if (!v) return "";
  if ("values" in v) return String(v.values ?? "");
  return `${v.value ?? ""}${v.memo ? ` · '${v.memo}'` : ""}`;
}

/** 보낸 결과 카드(T06 오른쪽, 조작 잠김) + 정정 n회 · 이전 값 · 정정 버튼 또는 확정 안내. */
function ResultCard({ r, closedNote, onCorrect }: { r: Rec; closedNote: string | null; onCorrect: () => void }) {
  const n = r.corrections.length;
  return (
    <div className="cd">
      <div className="res">
        <div className="corr-h">
          <b className="rt">보낸 결과</b>
          {n ? <span className="ch amber">정정 {n}회</span> : null}
          {r.void ? <span className="ch gray">정정으로 무효</span> : null}
        </div>
        <div className="rbtns">
          {VALUES.map((v) => (
            <span key={v} className={`rbtn${r.value === v ? ` sel ${v === "정상" ? "ok" : v === "이상" ? "bad" : "na"}` : ""} dis`}>
              <Icon name={VICON[v]} />
              {v}
            </span>
          ))}
        </div>
        <span className="sm">메모</span>
        <div className="memo">{r.memo ?? ""}</div>
        {n ? (
          <div className="corr-list">
            {r.corrections.map((c, i) => (
              <div key={i}>
                <span className="tt">{c.at ? hhmm(c.at) : ""}</span> <s>{fmtBefore(c.before)}</s> → <b>{fmtBefore({ ...c.before, ...c.after })}</b>
                <span className="sm">사유 · {c.reason}</span>
              </div>
            ))}
          </div>
        ) : null}
        {r.correctable ? (
          <>
            <IconBtn cls="lg full ghost" icon="pencil" label="이 기록 정정" onClick={onCorrect} />
            <span className="note">정비자가 입력한 결과 · 메모만 정정합니다. 사유를 적어야 저장되고 원래 값은 감사 기록에 남습니다.</span>
          </>
        ) : closedNote ? (
          <div className="hint">
            <Icon name="lock" />
            {closedNote}
          </div>
        ) : null}
      </div>
    </div>
  );
}

/** 정정하지 않는 기록(잠금 · 조치 · 재가동 · 호출)의 '기록' 카드: 기록 줄 · 덧붙인 메모 · 메모 덧붙이기. */
function RecordCard({ r, closedNote, onNote }: { r: Rec; closedNote: string | null; onNote: () => void }) {
  return (
    <div className="cd">
      <div className="res">
        <b className="rt">기록</b>
        <span className="sm">{r.record}</span>
        {r.notes.length ? (
          <div className="corr-list">
            {r.notes.map((x, i) => (
              <div key={i}>
                <span className="tt">{x.at ? hhmm(x.at) : ""}</span> 덧붙인 메모 · <b>{x.memo}</b>
              </div>
            ))}
          </div>
        ) : null}
        {r.notable ? (
          <>
            <IconBtn cls="lg full ghost" icon="message-square-plus" label="메모 덧붙이기" onClick={onNote} />
            <span className="note">실제로 한 일이나 이미 보낸 기록은 정정하지 않습니다. 메모를 덧붙일 수 있습니다.</span>
          </>
        ) : closedNote ? (
          <div className="hint">
            <Icon name="lock" />
            {closedNote}
          </div>
        ) : null}
      </div>
    </div>
  );
}

function Tags({ r }: { r: Rec }) {
  return (
    <div className="tags">
      <GradeBadge grade={r.grade} />
      {r.section ? <span className="ch blue">매뉴얼 {r.section}절</span> : null}
      {r.minutes != null ? <span className="ch gray">약 {r.minutes}분</span> : null}
    </div>
  );
}

function CheckLeft({ r, onManual, onRecord }: { r: Rec; onManual: () => void; onRecord: (id: string) => void }) {
  const ids = r.evidence_record_ids ?? [];
  return (
    <div className="cd">
      <LockOk at={r.lock_at} />
      <div className="ins-h">
        <span className="sm">
          점검 {r.check_no} / 최대 {r.check_max}
        </span>
        <h3>{r.title}</h3>
        <Tags r={r} />
      </div>
      {r.b_checklist ? (
        <div className="act pre">
          <div className="act-h">
            <b>시작 전 체크리스트</b>
            {r.b_checklist_common ? <span className="ch gray">공통 시작 전 확인</span> : null}
          </div>
          <span className="sm">그때 모두 확인한 뒤 결과를 보냈습니다</span>
          {r.b_checklist.map((x) => (
            <div className="ck on" key={x}>
              <span className="cb">
                <Icon name="check" />
              </span>
              {x}
            </div>
          ))}
        </div>
      ) : null}
      <Proc steps={r.steps ?? []} />
      {r.criterion ? (
        <div className="hint">
          <Icon name="info" />
          판정 기준 · {r.criterion}
        </div>
      ) : null}
      <div className="refs">
        <span className="lk" role="button" tabIndex={0} onClick={onManual}>
          <Icon name="book-open" />
          매뉴얼 원문 보기
        </span>
        {ids.length ? (
          <span className="lk">
            <Icon name="history" />
            근거{" "}
            {ids.map((id, i) => (
              <span key={id} role="button" tabIndex={0} onClick={() => onRecord(id)}>
                {i ? " · " : ""}
                {id}
              </span>
            ))}
          </span>
        ) : null}
      </div>
    </div>
  );
}

export interface PastProps {
  api: Api;
  sid: number;
  s: SessionView;
  data: PastData;
  no: number; // 보는 단계(1 ~ 5)
  idx: number;
  onIdx: (i: number) => void;
  onCurrent: () => void;
  unsent: { section: string; title: string; desc: string } | null; // 지금 지시의 보내지 않은 입력(기기)
  onSaved: (v: SessionView, clearedDraft: boolean) => void;
  onRecord: (id: string) => void;
  onManual: (section: string) => void;
}

type Modal =
  | { kind: "correct"; r: Rec; value: Value | null; memo: string; values: string; reason: string }
  | { kind: "confirm"; r: Rec; body: Record<string, unknown>; detail: Record<string, unknown> }
  | { kind: "note"; r: Rec; memo: string };

export function PastScreen(p: PastProps) {
  const step = p.data.steps[p.no - 1];
  const recs = step?.records ?? [];
  const r = recs[Math.min(p.idx, recs.length - 1)];
  const [modal, setModal] = useState<Modal | null>(null);
  const [busy, setBusy] = useState(false);
  const closedNote = p.data.closed ? (p.data.closed_note ?? null) : null;
  if (!r) return null;

  const save = async (body: Record<string, unknown>, rr: Rec) => {
    setBusy(true);
    const { data, error, response } = await p.api.POST("/api/tech/sessions/{sid}/corrections", {
      params: { path: { sid: p.sid } },
      body: body as never,
    });
    setBusy(false);
    if (data) {
      setModal(null);
      p.onSaved(data, !!body.confirmed);
      return;
    }
    const detail = (error as { detail?: unknown } | undefined)?.detail;
    if (response.status === 409 && detail && typeof detail === "object" && (detail as { reason?: string }).reason === "confirm_required")
      setModal({ kind: "confirm", r: rr, body, detail: detail as Record<string, unknown> }); // AC-46-C3
    else if (errorDetail(error)) setModal(null);
  };
  const saveNote = async (rr: Rec, memo: string) => {
    setBusy(true);
    const { data } = await p.api.POST("/api/tech/sessions/{sid}/notes", {
      params: { path: { sid: p.sid } },
      body: { target_seq: rr.seq, memo },
    });
    setBusy(false);
    if (data) {
      setModal(null);
      p.onSaved(data, false);
    }
  };

  const openCorrect = (rr: Rec) =>
    setModal({ kind: "correct", r: rr, value: (rr.value as Value) ?? null, memo: rr.memo ?? "", values: rr.values ?? "", reason: "" });

  let body;
  if (r.kind === "alarm" && r.alarm) {
    body = <AlarmScreen s={{ alarm: r.alarm }} onNext={() => undefined} past />;
  } else if (r.kind === "diagnosis" && r.next) {
    body = (
      <DiagnosisScreen
        s={{
          probabilities: r.probabilities ?? {},
          evidence: r.evidence ?? {},
          cause_names: r.cause_names ?? {},
          similar_cards: r.similar_cards ?? [],
          low_evidence: !!r.low_evidence,
          preview: r.next,
        }}
        onRecord={p.onRecord}
        onStart={() => undefined}
        past
      />
    );
  } else {
    let left;
    let right;
    if (r.kind === "check") {
      left = <CheckLeft r={r} onManual={() => r.section && p.onManual(r.section)} onRecord={p.onRecord} />;
      right = <ResultCard r={r} closedNote={closedNote} onCorrect={() => openCorrect(r)} />;
    } else if (r.kind === "precheck") {
      left = (
        <div className="cd">
          <LockOk at={r.lock_at} />
          <div className="ins-h">
            <span className="sm">사전 확인 · 점수 없이 항상 먼저</span>
            <h3>{r.title}</h3>
            <Tags r={r} />
          </div>
          <Proc steps={r.steps ?? []} />
        </div>
      );
      right = (
        <div className="cd">
          <div className="res">
            <b className="rt">기록한 값</b>
            <div className="memo">{r.values ?? ""}</div>
            {r.corrections.length ? (
              <div className="corr-list">
                {r.corrections.map((c, i) => (
                  <div key={i}>
                    <span className="tt">{c.at ? hhmm(c.at) : ""}</span> <s>{fmtBefore(c.before)}</s> → <b>{fmtBefore(c.after)}</b>
                    <span className="sm">사유 · {c.reason}</span>
                  </div>
                ))}
              </div>
            ) : null}
            {r.correctable ? (
              <>
                <IconBtn cls="lg full ghost" icon="pencil" label="이 기록 정정" onClick={() => openCorrect(r)} />
                <span className="note">측정값은 정정할 수 있습니다. 사전 확인 완료 자체는 정정하지 않습니다.</span>
              </>
            ) : closedNote ? (
              <div className="hint">
                <Icon name="lock" />
                {closedNote}
              </div>
            ) : null}
          </div>
        </div>
      );
    } else if (r.kind === "lock") {
      left = (
        <div className="cd">
          <div className="lockbox">
            <Icon name="lock" />
            <h3>잠금 완료 · {r.at ? hhmm(r.at) : ""}</h3>
            <span>매뉴얼 1.2절 · 설비 전원을 잠그고 표지를 겁니다</span>
          </div>
          <Proc steps={r.steps ?? []} />
        </div>
      );
      right = <RecordCard r={r} closedNote={closedNote} onNote={() => setModal({ kind: "note", r, memo: "" })} />;
    } else if (r.kind === "call") {
      left = (
        <div className="cd">
          <div className="lockbox">
            <Icon name={r.call_kind === "handover" ? "hand" : "phone-call"} />
            <h3>
              {r.call_kind === "handover" ? "숙련자 인계" : "파트장 호출"} · {r.at ? hhmm(r.at) : ""}
            </h3>
            <span>{r.section ? `${r.title}(${r.section}${r.grade ? `, ${r.grade}` : ""})` : "숙련자 확인 필요"}</span>
          </div>
          <div className="pv">
            <span className="sm">보낸 요약</span>
            <p>{r.summary}</p>
          </div>
          {r.box?.map((b, i) => (
            <div className="corr-box" key={i}>
              <Icon name="pencil" />
              <b>보낸 뒤 정비자 정정 · {b.at ? hhmm(b.at) : ""}</b>
              <div>
                {b.section} {b.title} · {fmtBefore(b.before)} → {fmtBefore({ ...b.before, ...b.after })}
              </div>
              <span className="sm">사유 · {b.reason}</span>
            </div>
          ))}
        </div>
      );
      right = <RecordCard r={r} closedNote={closedNote} onNote={() => setModal({ kind: "note", r, memo: "" })} />;
    } else {
      // 조치 · 재가동 · 감시 마감(T15 / action)
      left = (
        <div className="cd">
          {r.cause_name ? (
            <div className="done-h">
              <Icon name="circle-check" />
              <div>
                <span className="sm">원인 확정</span>
                <h3>{r.cause_name}</h3>
                <span>근거: 점검 결과(이상){r.evidence_record_ids?.length ? ` · 과거 기록 ${r.evidence_record_ids.join(" · ")}` : ""}</span>
              </div>
            </div>
          ) : null}
          <div className="act">
            <div className="act-h">
              <b>{r.title}</b>
              <GradeBadge grade={r.grade} />
              <span className="ch blue">{r.section}절</span>
              <span className="ch green">완료 {r.at ? hhmm(r.at) : ""}</span>
            </div>
          </div>
          {r.restart ? (
            <div className="act">
              <div className="act-h">
                <b>재가동</b>
                <GradeBadge grade={r.restart.grade} />
                <span className="ch blue">{r.restart.section}절</span>
                <span className="ch green">재가동 {r.restart.at ? hhmm(r.restart.at) : ""}</span>
              </div>
              {r.restart.checklist.map((x) => (
                <div className="ck on" key={x}>
                  <span className="cb">
                    <Icon name="check" />
                  </span>
                  {x}
                </div>
              ))}
            </div>
          ) : null}
        </div>
      );
      right = <RecordCard r={r} closedNote={closedNote} onNote={() => setModal({ kind: "note", r, memo: "" })} />;
    }
    body = (
      <div className="ap-body past">
        <div className="g64">
          {left}
          {right}
        </div>
      </div>
    );
  }

  const many = p.no >= 3; // 알람 · 진단은 기록 하나(띠에 이전 · 다음 없음)
  const m = modal;
  return (
    <>
      <div className="pastbar">
        <Icon name="history" />
        <b>지난 화면 · {step.name}</b>
        <span className="tt">{r.band}</span>
        {p.unsent ? <span className="ch amber">지금 {p.unsent.section} 입력(보내지 않음)은 그대로</span> : null}
        <span className="pn">
          {many ? (
            <>
              <span className={`btn ghost sm2${p.idx <= 0 ? " dis" : ""}`} role="button" tabIndex={0} onClick={() => p.idx > 0 && p.onIdx(p.idx - 1)}>
                <Icon name="chevron-left" />
                이전
              </span>
              <b>{r.position}</b>
              <span
                className={`btn ghost sm2${p.idx >= recs.length - 1 ? " dis" : ""}`}
                role="button"
                tabIndex={0}
                onClick={() => p.idx < recs.length - 1 && p.onIdx(p.idx + 1)}
              >
                다음
                <Icon name="chevron-right" />
              </span>
            </>
          ) : null}
          <span className="btn sm2" role="button" tabIndex={0} onClick={p.onCurrent}>
            현재 단계로 <Icon name="arrow-right" />
          </span>
        </span>
      </div>
      {body}
      {m ? <div className="dim" onClick={() => !busy && setModal(null)} /> : null}
      {m?.kind === "correct" ? (
        <div className="modal wide" role="dialog" aria-label="이 기록 정정">
          <div className="mh">
            <Icon name="pencil" />
            <b>
              이 기록 정정 · {m.r.section} {m.r.kind === "precheck" ? "사전 확인 측정값" : m.r.title}
            </b>
            <span className="ch gray">{m.r.at ? hhmm(m.r.at) : ""} 보냄</span>
          </div>
          <div className="fld2">
            <span className="sm">원래 값</span>
            <b>{m.r.kind === "precheck" ? m.r.values : `${m.r.value}${m.r.memo ? ` · 메모 '${m.r.memo}'` : ""}`}</b>
          </div>
          {m.r.kind === "precheck" ? (
            <div className="fld2">
              <span className="sm">정정할 값</span>
              <textarea className="memo" aria-label="정정할 값" value={m.values} onChange={(e) => setModal({ ...m, values: e.target.value })} />
            </div>
          ) : (
            <>
              <div className="fld2">
                <span className="sm">정정할 결과</span>
                <div className="rbtns">
                  {VALUES.map((v) => (
                    <span
                      key={v}
                      className={`rbtn${m.value === v ? ` sel ${v === "정상" ? "ok" : v === "이상" ? "bad" : "na"}` : ""}`}
                      role="button"
                      tabIndex={0}
                      onClick={() => setModal({ ...m, value: v })}
                    >
                      <Icon name={VICON[v]} />
                      {v}
                    </span>
                  ))}
                </div>
              </div>
              <div className="fld2">
                <span className="sm">정정할 메모</span>
                <textarea className="memo" aria-label="정정할 메모" value={m.memo} onChange={(e) => setModal({ ...m, memo: e.target.value })} />
              </div>
            </>
          )}
          <div className="fld2">
            <span className="sm">정정 사유 (꼭 적습니다)</span>
            <textarea className="memo req" aria-label="정정 사유" value={m.reason} onChange={(e) => setModal({ ...m, reason: e.target.value })} />
          </div>
          <div className="mb">
            <Btn cls="ghost" label="취소" onClick={() => setModal(null)} />
            <Btn
              cls=""
              label="정정 저장"
              off={busy || !m.reason.trim()}
              onClick={() => {
                const b: Record<string, unknown> = { target_seq: m.r.seq, reason: m.reason.trim() };
                if (m.r.kind === "precheck") b.values = m.values.trim();
                else {
                  if (m.value && m.value !== m.r.value) b.value = m.value;
                  if (m.memo.trim() !== (m.r.memo ?? "")) b.memo = m.memo.trim();
                }
                void save(b, m.r);
              }}
            />
          </div>
          <span className="note">사유를 적어야 저장됩니다. 원래 값은 지워지지 않고 감사 기록에 남습니다.</span>
        </div>
      ) : null}
      {m?.kind === "confirm" ? (
        <div className="modal" role="dialog" aria-label="이 정정으로 다음 지시가 바뀝니다">
          <div className="mh">
            <Icon name="triangle-alert" />
            <b>이 정정으로 다음 지시가 바뀝니다</b>
          </div>
          <div className="banner warn">
            <Icon name="triangle-alert" />
            <div>
              <b>
                {m.r.section} {m.r.title} · {m.r.value} → {String((m.body.value as string | undefined) ?? m.r.value)}
              </b>
              그 점검부터 다시 판정합니다. 지금 지시 {String((m.detail.current as { section?: string })?.section ?? "")}{" "}
              {String((m.detail.current as { title?: string })?.title ?? "")}
              {p.unsent ? `의 보내지 않은 입력(${p.unsent.desc})은 지워지고` : "은(는) 닫히고"} 새 지시가 나옵니다.
            </div>
          </div>
          <span className="sm">사유 · {String(m.body.reason)}</span>
          <div className="mb">
            <Btn cls="ghost" label="취소" onClick={() => setModal(null)} />
            <Btn cls="warnb" label="정정 저장" off={busy} onClick={() => void save({ ...m.body, confirmed: true }, m.r)} />
          </div>
        </div>
      ) : null}
      {m?.kind === "note" ? (
        <div className="modal" role="dialog" aria-label="메모 덧붙이기">
          <div className="mh">
            <Icon name="message-square-plus" />
            <b>메모 덧붙이기 · {(m.r.record ?? "").split(" · ")[0]}</b>
          </div>
          <span className="sm">원래 기록은 그대로이고, 메모가 시각과 함께 덧붙습니다.</span>
          <textarea className="memo sm3" aria-label="덧붙일 메모" value={m.memo} onChange={(e) => setModal({ ...m, memo: e.target.value })} />
          <div className="mb">
            <Btn cls="ghost" label="취소" onClick={() => setModal(null)} />
            <Btn cls="" label="메모 저장" off={busy || !m.memo.trim()} onClick={() => void saveNote(m.r, m.memo.trim())} />
          </div>
        </div>
      ) : null}
    </>
  );
}
