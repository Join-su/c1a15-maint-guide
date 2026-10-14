// T08 조치 · 재가동 · 재가동 후 값, T10 파트장 호출(요약 · 대기 · 보냄 · 답 3종), T11 숙련자 인계 · 감시 마감, T09 보고서.
// 값은 세션 응답의 path · action · restart · monitor · call · report(P-09). 화면 문구 외의 값은 만들지 않는다.

import { useState } from "react";
import { GradeBadge, hhmm, Icon, type Instruction, type Schemas, type SessionView } from "@c1a15/ui";
import { Proc } from "./Lock";

type Call = Schemas["CallBlock"];
type Report = Schemas["ReportBlock"];

export function PathCard({ path }: { path: SessionView["path"] }) {
  return (
    <div className="cd ">
      <div className="cd-h">
        <Icon name="history" />
        <b>점검 경로</b>
      </div>
      <div className="tlw">
        {(path ?? []).map((p, i) => (
          <div className={`tli ${p.status}`} key={i}>
            <span className="tt">{p.status === "now" ? "지금" : p.at ? hhmm(p.at) : ""}</span>
            <span className="td" />
            <div>
              <b>{p.title}</b>
              <span>{p.detail}</span>
              {p.status === "void" ? <span className="ch gray vd">정정으로 무효</span> : null}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function CauseHead({ a }: { a: NonNullable<SessionView["action"]> }) {
  const ev = a.evidence_record_ids.length ? ` · 과거 기록 ${a.evidence_record_ids.join(" · ")}` : "";
  return (
    <div className="done-h">
      <Icon name="circle-check" />
      <div>
        <span className="sm">원인 확정</span>
        <h3>{a.cause_name}</h3>
        <span>근거: 점검 결과(이상){ev}</span>
      </div>
    </div>
  );
}

function Checks({ items, on, onToggle }: { items: string[]; on: (x: string) => boolean; onToggle: (x: string) => void }) {
  return (
    <>
      {items.map((item) => (
        <div
          className={`ck ${on(item) ? "on" : ""}`}
          key={item}
          role="checkbox"
          aria-checked={on(item)}
          tabIndex={0}
          onClick={() => onToggle(item)}
        >
          <span className="cb">{on(item) ? <Icon name="check" /> : null}</span>
          {item}
        </div>
      ))}
    </>
  );
}

function Btn({ label, icon, cls = "lg full", off, onClick }: { label: string; icon?: string; cls?: string; off?: boolean; onClick: () => void }) {
  return (
    <span className={`btn ${cls}${off ? " dis" : ""}`} role="button" tabIndex={0} aria-disabled={off} onClick={() => !off && onClick()}>
      {label}
      {icon ? (
        <>
          {" "}
          <Icon name={icon} />
        </>
      ) : null}
    </span>
  );
}

export interface ActionProps {
  s: SessionView;
  busy: boolean;
  checked: string[];
  onCheck: (items: string[]) => void;
  send: (body: Record<string, unknown>) => void;
}

/** T08: 원인 확정 → 조치(A 바로 · B 체크리스트 뒤) → 재가동 체크리스트, 재가동 뒤 값 확인(경계 이내 · 여전히 밖). */
export function ActionScreen({ s, busy, checked, onCheck, send }: ActionProps) {
  const a = s.action;
  const r = s.restart;
  const kind = s.step.kind;
  const toggle = (x: string) => onCheck(checked.includes(x) ? checked.filter((y) => y !== x) : [...checked, x]);
  if (kind === "restart_value" && r?.value) {
    const v = r.value;
    return (
      <div className="ap-body">
        <div className="g64">
          <div className="cd">
            <div className="act-h">
              <b>재가동 후 값 확인</b>
              <GradeBadge grade={r.grade} />
              <span className="ch blue">{r.section}절</span>
              {r.restarted_at ? <span className="ch green">재가동 {hhmm(r.restarted_at)}</span> : null}
            </div>
            <div className="sub">
              {v.sensor} · {v.basis}
            </div>
            <div className="rv-big">{v.value_text}</div>
            <span className="rv-sub">{v.rule_text}</span>
            <div className="choice2">
              <Btn cls="" label="경계 이내" off={busy} onClick={() => send({ type: "restart_result", outcome: "within" })} />
              <Btn cls="ghost" label="여전히 밖" off={busy} onClick={() => send({ type: "restart_result", outcome: "outside" })} />
            </div>
            <span className="note">
              {a
                ? '값을 보고 정비자가 고릅니다. "여전히 밖"이면 원인 확정 후에도 회복되지 않은 것으로 보고 숙련자 인계로 넘어갑니다.'
                : '값을 보고 정비자가 고릅니다. "경계 이내"면 이상 없음 · 감시로 마감하고, "여전히 밖"이면 숙련자 인계로 넘어갑니다.'}
            </span>
          </div>
          <PathCard path={s.path} />
        </div>
      </div>
    );
  }
  const actionOpen = a && !a.done_at && (kind === "action" || kind === "action_after_checklist");
  const needs = !!a && a.checklist.length > 0 && !a.checklist_done;
  const actionChecks = needs ? a!.checklist : [];
  const restartReady = r && r.checklist.every((x) => checked.includes(x));
  return (
    <div className="ap-body">
      <div className="g64">
        <div className="cd">
          {a ? <CauseHead a={a} /> : null}
          {s.correction ? (
            <div className="banner info">
              <Icon name="pencil" />
              <div>
                <b>
                  {s.correction.section} 정정으로 다시 판정했습니다 · {s.correction.at ? hhmm(s.correction.at) : ""}
                </b>
                뒤의 기록은 지우지 않고 '정정으로 무효'로 남겼습니다.
              </div>
            </div>
          ) : null}
          {a ? (
            <div className="act">
              <div className="act-h">
                <b>{a.title}</b>
                <GradeBadge grade={a.grade} />
                <span className="ch blue">{a.section}절</span>
                {a.done_at ? (
                  <span className="ch green">완료 {hhmm(a.done_at)}</span>
                ) : a.minutes != null ? (
                  <span className="ch gray">약 {a.minutes}분</span>
                ) : null}
              </div>
              {actionOpen && a.checklist.length > 0 && !a.checklist_done ? (
                <>
                  <span className="sm">아래 항목을 모두 확인해야 진행 버튼이 열립니다</span>
                  <Checks items={actionChecks} on={(x) => checked.includes(x)} onToggle={toggle} />
                </>
              ) : null}
              {actionOpen ? (
                needs ? (
                  <Btn
                    label={actionChecks.every((x) => checked.includes(x)) ? `${a.verb} 진행` : `체크리스트 확인 후 ${a.verb} 진행`}
                    off={busy || !actionChecks.every((x) => checked.includes(x))}
                    onClick={() => send({ type: "b_checklist_done", section: a.section, checked: a.checklist })}
                  />
                ) : (
                  <Btn label={`${a.verb} 완료`} off={busy} onClick={() => send({ type: "action_done", section: a.section })} />
                )
              ) : null}
            </div>
          ) : null}
          {kind === "restart_check" && r ? (
            <div className="act">
              <div className="act-h">
                <b>{r.title}</b>
                <GradeBadge grade={r.grade} />
                <span className="ch blue">{r.section}절</span>
              </div>
              <span className="sm">아래 항목을 모두 확인해야 재가동 버튼이 열립니다</span>
              <Checks items={r.checklist} on={(x) => checked.includes(x)} onToggle={toggle} />
              <Btn
                label={restartReady ? "재가동" : "체크리스트 확인 후 재가동"}
                off={busy || !restartReady}
                onClick={() => send({ type: "restart", checked: r.checklist })}
              />
            </div>
          ) : null}
        </div>
        <PathCard path={s.path} />
      </div>
    </div>
  );
}

/** T11 / monitor_close: 후보가 모두 빠지고 재가동 뒤 경계 이내 → 6.2절 감시 마감 후 보고서. */
export function MonitorScreen({ s, busy, send }: { s: SessionView; busy: boolean; send: ActionProps["send"] }) {
  const mo = s.monitor!;
  return (
    <div className="ap-body">
      <div className="g64">
        <div className="cd">
          <div className="done-h">
            <Icon name="circle-check" />
            <div>
              <span className="sm">이상 없음 · 감시</span>
              <h3>A · B 점검 모두 정상 · 재가동 후 경계 이내</h3>
              <span>{mo.section}절 · 설비를 감시 대상으로 등록하고 다음 교대 시작 때 같은 값을 다시 확인합니다.</span>
            </div>
          </div>
          <div className="act">
            <div className="act-h">
              <b>{mo.title.replace("·", " · ")}</b>
              <GradeBadge grade={mo.grade} />
              <span className="ch blue">{mo.section}절</span>
            </div>
          </div>
          <Btn label="보고서 작성" icon="file-text" off={busy} onClick={() => send({ type: "monitor_close" })} />
          <span className="note">보고서 확정 원인은 "이상 없음 · 감시"입니다. 같은 알람이 다시 오면 이 보고서가 근거로 표시됩니다.</span>
        </div>
        <PathCard path={s.path} />
      </div>
    </div>
  );
}

const ANSWER_LABEL: Record<string, string> = { approved: "승인 후 진행", daytime: "주간 처리", direct: "직접 확인" };
export { ANSWER_LABEL };

function Summary({
  call,
  label,
  editable,
  text,
  onText,
}: {
  call: Call;
  label: string;
  editable: boolean;
  text: string | null;
  onText: (t: string | null) => void;
}) {
  return (
    <div className="pv">
      <span className="sm">{label}</span>
      {editable && text !== null ? (
        <textarea className="memo" aria-label="요약 고치기" value={text} autoFocus onChange={(e) => onText(e.target.value)} />
      ) : (
        <p
          role={editable ? "button" : undefined}
          tabIndex={editable ? 0 : undefined}
          title={editable ? "눌러서 고치기" : undefined}
          onClick={() => editable && onText(call.summary.text)}
        >
          {text ?? call.summary.text}
        </p>
      )}
    </div>
  );
}

export interface CallProps {
  s: SessionView;
  busy: boolean;
  approvedSeen: boolean;
  onApprovedSeen: () => void;
  onReport: () => void;
  send: (body: Record<string, unknown>) => Promise<boolean> | void;
}

/** T10: 다음 점검은 혼자 진행할 수 없음 → 요약(고칠 수 있음) · 파트장 호출 · 호출하지 않고 대기 → 보냄 → 답 3종. */
export function CallScreen({ s, busy, approvedSeen, onApprovedSeen, onReport, send }: CallProps) {
  const call = s.call!;
  const cor = call.correction; // T10 / summary_corrected: 조치 뒤 정정 → 다시 판정 대신 확인 요청(AC-47-C1)
  const [text, setText] = useState<string | null>(null);
  const ans = call.answer;
  const ins: Instruction | null | undefined = s.instruction;
  const editable = call.status === "none" || call.status === "waiting";
  const by = ans ? `${ans.by_name ?? ans.by ?? ""} ${ans.at ? hhmm(ans.at) : ""}`.trim() : "";
  const sendCall = () => {
    const body: Record<string, unknown> = { type: "call_send" };
    if (text !== null && text.trim() && text.trim() !== call.summary.text) body.summary = text.trim();
    void send(body);
  };
  const callBtn = <Btn cls="lg full warnb" label="파트장 호출" icon="phone-call" off={busy} onClick={sendCall} />;
  const summary = (
    <Summary call={call} label="파트장에게 보낼 요약 (자동 작성 · 고칠 수 있음)" editable={editable} text={text} onText={setText} />
  );
  let right;
  if (ans?.answer === "approved" && ins && !approvedSeen) {
    right = (
      <div className="cd">
        <div className="banner ok">
          <Icon name="circle-check" />
          <div>
            <b>승인 후 진행 · {by}</b>
            {call.title}({call.section}절) 지시가 열렸습니다. 호출 기록에 승인자와 시각이 남습니다.
          </div>
        </div>
        <div className="ins-h">
          <span className="sm">점검 {ins.check_no} · 파트장 승인</span>
          <h3>{ins.title}</h3>
          <div className="tags">
            <GradeBadge grade={ins.grade} />
            <span className="ch green">승인됨</span>
            <span className="ch blue">매뉴얼 {ins.section}절</span>
          </div>
        </div>
        <Proc steps={ins.steps} />
        <Btn label="점검 시작" icon="arrow-right" onClick={onApprovedSeen} />
      </div>
    );
  } else if (ans?.answer === "daytime") {
    right = (
      <div className="cd">
        <div className="banner warn">
          <Icon name="clock" />
          <div>
            <b>주간 처리로 결정 · 저부하 감시 운전</b>
            {by} · "{cor ? `정정 확인 · ${cor.section} ${cor.title}(${cor.before} → ${cor.after})` : `${call.title}(${call.section}, ${call.grade})`}"이 보고서 "미확인 · 요청"에 기록됩니다.
          </div>
        </div>
        {summary}
        <Btn label="보고서 작성" icon="file-text" onClick={onReport} />
      </div>
    );
  } else if (ans?.answer === "direct") {
    right = (
      <div className="cd">
        <div className="banner info">
          <Icon name="eye" />
          <div>
            <b>파트장 직접 확인 · 처리 결과</b>
            {by} · {ans.note ?? "처리 메모 없음"} — 보고서 "미확인 · 요청"에 기록됩니다.
          </div>
        </div>
        {summary}
        {/* 결정 018 ③: 처리 결과와 함께 답이 오므로 보고서로 간다 */}
        <Btn label="보고서 작성" icon="file-text" onClick={onReport} />
      </div>
    );
  } else if (call.status === "sent") {
    right = (
      <div className="cd">
        <div className="banner info">
          <Icon name="send" />
          <div>
            <b>파트장 호출을 보냈습니다 · {call.sent_at ? hhmm(call.sent_at) : ""}</b>파트장 앱 "처리할 호출"에 올라갔습니다. 답을 기다리는 중입니다.
          </div>
        </div>
        {summary}
        <span className="note">화면에 지시되지 않은 C · D등급 작업을 혼자 진행하지 마십시오.</span>
      </div>
    );
  } else if (call.status === "waiting") {
    right = (
      <div className="cd">
        <div className="banner warn">
          <Icon name="clock" />
          <div>
            <b>호출하지 않고 대기 중 · {call.waiting_at ? hhmm(call.waiting_at) : ""}</b>호출은 보내지 않았습니다. 설비는 정지 상태로 둡니다.
          </div>
        </div>
        {summary}
        {callBtn}
      </div>
    );
  } else {
    right = (
      <div className="cd">
        {summary}
        {callBtn}
        <Btn cls="ghost full" label="호출하지 않고 대기" off={busy} onClick={() => void send({ type: "call_wait" })} />
      </div>
    );
  }
  const icon = (v: string) => (v.startsWith("정상") ? "circle-check" : v.startsWith("이상") ? "circle-alert" : "circle-help");
  const tone = (v: string) => (v.startsWith("정상") ? "ok" : v.startsWith("이상") ? "bad" : "na");
  return (
    <div className="ap-body">
      <div className="g64">
        <div className="cd">
          {cor ? (
            <div className="warn-h">
              <Icon name="pencil" />
              <div>
                <span className="sm">정정한 점검 뒤에 조치를 이미 마쳐 다시 판정하지 않습니다</span>
                <h3>파트장 확인이 필요합니다</h3>
                <div className="tags">
                  <span className="ch amber">
                    정정 · {cor.section} {cor.before} → {cor.after}
                    {cor.at ? ` · ${hhmm(cor.at)}` : ""}
                  </span>
                  {call.actions_done?.map((a) => (
                    <span className="ch green" key={a.section}>
                      조치 완료 {a.section}
                      {a.at ? ` · ${hhmm(a.at)}` : ""}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <div className="warn-h">
              <Icon name="hand" />
              <div>
                <span className="sm">다음 점검은 혼자 진행할 수 없습니다</span>
                <h3>{call.title}</h3>
                <div className="tags">
                  <GradeBadge grade={call.grade} />
                  <span className="ch blue">매뉴얼 {call.section}절</span>
                  {call.minutes != null ? <span className="ch gray">약 {call.minutes}분</span> : null}
                </div>
              </div>
            </div>
          )}
          <div className="sub">{cor ? "지금까지 점검 · 조치" : "지금까지 점검"}</div>
          <div className="dn2">
            {call.checks_done.length ? (
              call.checks_done.map((d) => (
                <span key={d.section}>
                  <Icon name={icon(d.value)} className={tone(d.value)} />
                  {d.title} · {d.value}
                  {d.note ? `(${d.note})` : ""}
                </span>
              ))
            ) : (
              <span>점검 전</span>
            )}
            {cor
              ? call.actions_done?.map((a) => (
                  <span key={`a${a.section}`}>
                    <Icon name="circle-check" className="ok" />
                    {a.title}({a.section}) · 완료{a.at ? ` ${hhmm(a.at)}` : ""}
                  </span>
                ))
              : null}
          </div>
          <div className="sub">남은 후보</div>
          {cor ? (
            <div className="hint">
              <Icon name="info" />
              조치 뒤라 순위를 다시 계산하지 않았습니다. 파트장이 확인합니다.
            </div>
          ) : (
            <div className="tags">
              {call.candidates.map((c) => (
                <span className="ch gray" key={c.code}>
                  {c.name} {c.pct}%
                </span>
              ))}
            </div>
          )}
        </div>
        {right}
      </div>
    </div>
  );
}

/** T11: 숙련자 인계(맞지 않는 소견 · 확인 불가 반복 · 재가동 뒤 밖). 보내면 보고서(확정 원인 '원인 미상'). */
export function HandoverScreen({
  s,
  busy,
  send,
  onReport,
}: {
  s: SessionView;
  busy: boolean;
  send: CallProps["send"];
  onReport?: () => void;
}) {
  const call = s.call!;
  const [text, setText] = useState<string | null>(null);
  const head = s.step.reason === "no_alternative" ? "확인 불가가 반복됨" : "숙련자 인계";
  const ans = call.answer;
  const by = ans ? `${ans.by_name ?? ans.by ?? ""} ${ans.at ? hhmm(ans.at) : ""}`.trim() : "";
  const sendIt = () => {
    const body: Record<string, unknown> = { type: "call_send" };
    if (text !== null && text.trim() && text.trim() !== call.summary.text) body.summary = text.trim();
    void send(body);
  };
  const label = "숙련자 인계 요약 (자동 작성 · 고칠 수 있음)";
  let action;
  if (ans) {
    // 결정 018 ④: 파트장 답(주간 숙련자 배정 · 직접 확인)과 처리 메모 → 보고서
    action = (
      <>
        <div className="banner ok">
          <Icon name="circle-check" />
          <div>
            <b>
              {ans.answer === "assign" ? "주간 숙련자 배정" : "파트장 직접 확인"} · {by}
            </b>
            {ans.note ?? "처리 메모 없음"} — 보고서 "미확인 · 요청"에 기록됩니다.
          </div>
        </div>
        <Summary call={call} label={label} editable={false} text={null} onText={() => {}} />
        <Btn label="보고서 작성" icon="file-text" onClick={() => onReport?.()} />
      </>
    );
  } else if (call.status === "sent") {
    // 결정 018 ④: 보낸 뒤 답 대기(T10 / sent 구조)
    action = (
      <>
        <div className="banner info">
          <Icon name="send" />
          <div>
            <b>숙련자 인계를 보냈습니다 · {call.sent_at ? hhmm(call.sent_at) : ""}</b>파트장 앱 "처리할 호출"에 유형 "숙련자 인계"로
            올라갔습니다. 답을 기다리는 중입니다.
          </div>
        </div>
        <Summary call={call} label={label} editable={false} text={null} onText={() => {}} />
        <span className="note">답이 오면 보고서를 작성합니다. 보고서 확정 원인은 "원인 미상"입니다.</span>
      </>
    );
  } else {
    action = (
      <>
        <Summary call={call} label={label} editable text={text} onText={setText} />
        <Btn cls="lg full warnb" label="숙련자 인계" icon="phone-call" off={busy} onClick={sendIt} />
        <span className="note">파트장 앱 "처리할 호출"에 유형 "숙련자 인계"로 올라갑니다. 보고서 확정 원인은 "원인 미상"입니다.</span>
      </>
    );
  }
  return (
    <div className="ap-body">
      <div className="g64">
        <div className="cd">
          <div className="warn-h">
            <Icon name="triangle-alert" />
            <div>
              <span className="sm">{head}</span>
              <h3>{call.head}</h3>
            </div>
          </div>
          {action}
        </div>
        <PathCard path={s.path} />
      </div>
    </div>
  );
}

export interface ReportProps {
  report: Report;
  busy: boolean;
  send: (body: Record<string, unknown>) => Promise<boolean> | void;
  onHome: () => void;
}

/** T09: 보고서 8항목(출처 · 고치기), 확정 전 확인 3항목, 확정 → 승인 대기(확정 뒤 수정 없음 — AC-33). */
export function ReportScreen({ report, busy, send, onHome }: ReportProps) {
  const [edit, setEdit] = useState<{ key: string; text: string } | null>(null);
  const draft = report.status === "draft";
  const save = () => {
    if (!edit) return;
    const f = report.fields.find((x) => x.key === edit.key);
    setEdit(null);
    if (f && edit.text !== f.text) void send({ type: "report_edit", field: edit.key, text: edit.text });
  };
  const failed = report.checks.filter((c) => !c.ok);
  return (
    <div className="ap-body">
      <div className="g73">
        <div className="cd">
          <div className="cd-h">
            <Icon name="file-text" />
            <b>정비 보고서 초안</b>
            {draft ? <span className="ch amber">초안</span> : <span className="ch green">확정 · 승인 대기</span>}
          </div>
          {report.fields.map((f) => (
            <div className={`rf${f.ok ? "" : " fail"}`} key={f.key} data-field={f.key}>
              <span className="rk2">{f.label}</span>
              {edit?.key === f.key ? (
                <textarea
                  className="rv2 memo"
                  aria-label={`${f.label} 고치기`}
                  value={edit.text}
                  autoFocus
                  onChange={(e) => setEdit({ key: f.key, text: e.target.value })}
                  onBlur={save}
                />
              ) : (
                <span className="rv2">
                  {f.key === "evidence_records" && report.low_evidence ? (
                    <>
                      <span className="ch amber">근거 적음</span>{" "}
                    </>
                  ) : null}
                  {f.text}
                </span>
              )}
              <span className="ch src">{f.source}</span>
              <span
                className="ed"
                role={draft ? "button" : undefined}
                tabIndex={draft ? 0 : undefined}
                aria-label={draft ? `${f.label} 고치기` : undefined}
                onClick={() => draft && !busy && setEdit({ key: f.key, text: f.text })}
              >
                {draft ? <Icon name="pencil" /> : null}
              </span>
            </div>
          ))}
        </div>
        <div>
          <div className="cd ">
            <div className="cd-h">
              <Icon name="shield-check" />
              <b>확정 전 확인</b>
            </div>
            <div className="ckl">
              {report.checks.map((c) => (
                <div className={`ck ${c.ok ? "on" : "no"}`} key={c.key}>
                  <span className="cb">
                    <Icon name={c.ok ? "check" : "x"} />
                  </span>
                  {c.label}
                </div>
              ))}
            </div>
            {draft && failed.length ? (
              <div className="banner bad">
                <Icon name="circle-alert" />
                <div>
                  <b>{failed[0].label}</b>
                  {report.messages.join(" ")}
                </div>
              </div>
            ) : null}
          </div>
          {draft ? (
            <div className="cta2">
              <Btn
                label="보고서 확정"
                icon="file-check-2"
                off={busy || !report.can_confirm || edit !== null}
                onClick={() => void send({ type: "report_confirm" })}
              />
              <span className="note">
                {report.can_confirm
                  ? "확정하면 파트장 승인 대기로 넘어갑니다. 확정 뒤에는 정비자가 고칠 수 없습니다."
                  : "확정 전 확인을 모두 통과해야 확정할 수 있습니다."}
              </span>
            </div>
          ) : (
            <>
              <div className="banner ok">
                <Icon name="circle-check" />
                <div>
                  <b>보고서를 확정했습니다 · {report.confirmed_at ? hhmm(report.confirmed_at) : ""}</b>파트장 승인 대기로 넘어갔습니다. 고칠 내용이 있으면 파트장에게 수정 요청 메모를 남기십시오.
                </div>
              </div>
              <Btn cls="lg full ghost" label="홈으로" onClick={onHome} />
            </>
          )}
        </div>
      </div>
    </div>
  );
}
