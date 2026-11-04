// T08 조치 · 재가동 · 재가동 후 값, T10 파트장 호출(요약 · 대기 · 보냄 · 답 3종), T11 숙련자 인계 · 감시 마감, T09 보고서.
// 값은 세션 응답의 path · action · restart · monitor · call · report(P-09). 화면 문구 외의 값은 만들지 않는다.

import { useState } from "react";
import { dateTime, GradeBadge, hhmm, Icon, type Instruction, type Schemas, type SessionView } from "@c1a15/ui";
import { Proc } from "./Lock";

type Call = Schemas["CallBlock"];
type Report = Schemas["ReportBlock"];

export function PathCard({ path }: { path: SessionView["path"] }) {
  return (
    <div className="cd ">
      <div className="cd-h">
        <Icon name="history" />
        <b>지금까지 점검 · 조치</b>
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

// 답장 001-zzx 가(가이드 14쪽): '원인 확정' 카드 — 머리 오른쪽 원인 칩 · '근거 사례' 한 줄.
function CauseCard({ a }: { a: NonNullable<SessionView["action"]> }) {
  return (
    <div className="cd">
      <div className="cd-h">
        <Icon name="circle-alert" />
        <b>원인 확정</b>
        <span className="ch red">{a.cause_name}</span>
      </div>
      {a.evidence_record_ids.length ? (
        <div className="kvr">
          <span>근거 사례</span>
          <b>{a.evidence_record_ids.join(" · ")}</b>
        </div>
      ) : null}
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

function Btn({
  label,
  icon,
  lead,
  cls = "lg full",
  off,
  onClick,
}: {
  label: string;
  icon?: string;
  lead?: string; // 이름 앞 아이콘(가이드 24 · 25 · 28쪽 호출 · 인계)
  cls?: string;
  off?: boolean;
  onClick: () => void;
}) {
  return (
    <span className={`btn ${cls}${off ? " dis" : ""}`} role="button" tabIndex={0} aria-disabled={off} onClick={() => !off && onClick()}>
      {lead ? (
        <>
          <Icon name={lead} />{" "}
        </>
      ) : null}
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

/** T08: 원인 확정 · 조치(A 바로 · B 체크리스트 뒤) · 재가동(체크리스트 → 재가동 뒤 값 · 경계 이내 · 여전히 밖) — 한 화면 카드 셋. */
// 답장 001-zzx 가(가이드 14 ~ 16 · 27쪽): 재가동 뒤 값과 두 버튼은 따로 화면이 아니라 재가동 카드 안 · 버튼 이름은 잠긴 동안도 그대로.
export function ActionScreen({ s, busy, checked, onCheck, send }: ActionProps) {
  const [askOutside, setAskOutside] = useState(false); // D-530 답장 001-zzt 6(가이드 27쪽): 「여전히 밖」 → 숙련자 인계 확인 창
  const a = s.action;
  const r = s.restart;
  const kind = s.step.kind;
  const toggle = (x: string) => onCheck(checked.includes(x) ? checked.filter((y) => y !== x) : [...checked, x]);
  const actionOpen = a && !a.done_at && (kind === "action" || kind === "action_after_checklist");
  const needs = !!a && a.checklist.length > 0 && !a.checklist_done;
  const actionChecks = needs ? a!.checklist : [];
  const restartReady = r && r.checklist.every((x) => checked.includes(x));
  const v = kind === "restart_value" ? r?.value : null;
  return (
    <div className="ap-body">
      <div className="g64">
        <div className="stk">
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
          {a ? <CauseCard a={a} /> : null}
          {a ? (
            <div className="cd act">
              <div className="act-h">
                <b>
                  조치 · {a.section} {a.title}
                </b>
                <GradeBadge grade={a.grade} />
                {a.done_at ? <span className="ch green">완료</span> : null}
              </div>
              {a.steps.length ? <Proc steps={a.steps} /> : null}
              {actionOpen && needs ? <Checks items={actionChecks} on={(x) => checked.includes(x)} onToggle={toggle} /> : null}
              {actionOpen ? (
                needs ? (
                  <Btn
                    label="조치 진행"
                    off={busy || !actionChecks.every((x) => checked.includes(x))}
                    onClick={() => send({ type: "b_checklist_done", section: a.section, checked: a.checklist })}
                  />
                ) : (
                  <Btn label="조치 완료" off={busy} onClick={() => send({ type: "action_done", section: a.section })} />
                )
              ) : null}
            </div>
          ) : null}
          {r && (kind === "restart_check" || v) ? (
            <div className="cd act">
              <div className="act-h">
                <b>
                  {r.title} · {r.section}절
                </b>
                <GradeBadge grade={r.grade} />
                {r.restarted_at ? <span className="ch green">재가동 {hhmm(r.restarted_at)}</span> : null}
              </div>
              {v ? (
                <>
                  <div className="rvrow">
                    <span>{v.sensor}</span>
                    <b className="rv-big">{v.value_text}</b>
                    <span>경계 {v.boundary_text}</span>
                  </div>
                  <div className="choice2">
                    <Btn cls="ghost" label="여전히 밖" off={busy} onClick={() => setAskOutside(true)} />
                    <Btn cls="" label="경계 이내" off={busy} onClick={() => send({ type: "restart_result", outcome: "within" })} />
                  </div>
                </>
              ) : (
                <>
                  <Checks items={r.checklist} on={(x) => checked.includes(x)} onToggle={toggle} />
                  <Btn label="재가동" off={busy || !restartReady} onClick={() => send({ type: "restart", checked: r.checklist })} />
                </>
              )}
            </div>
          ) : null}
        </div>
        <PathCard path={s.path} />
      </div>
      {askOutside ? (
        <>
          <div className="dim" />
          <div className="modal" role="dialog" aria-label="숙련자 인계 확인">
            <div className="mh">
              <Icon name="triangle-alert" />
              <b>재가동 뒤에도 경계 밖입니다. 숙련자에게 인계합니까?</b>
            </div>
            <div className="mb">
              <span className="btn ghost" role="button" tabIndex={0} onClick={() => setAskOutside(false)}>
                취소
              </span>
              <span
                className={`btn warnb${busy ? " dis" : ""}`}
                role="button"
                tabIndex={0}
                onClick={() => {
                  if (busy) return;
                  setAskOutside(false);
                  send({ type: "restart_result", outcome: "outside" });
                }}
              >
                숙련자 인계
              </span>
            </div>
          </div>
        </>
      ) : null}
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
  ro,
}: {
  call: Call;
  label: string;
  editable: boolean;
  text: string | null;
  onText: (t: string | null) => void;
  ro?: boolean; // 보낸 뒤 '보낸 요약'(읽기만 · 연필 표시 뺌)
}) {
  if (ro)
    // G3 대조(덧 4 T10b): 이름표는 칸 밖 위 · 글은 테두리 없는 회색 칸(읽기만)
    return (
      <>
        <span className="sml">{label}</span>
        <div className="pv ro">
          <p>{call.summary.text}</p>
        </div>
      </>
    );
  return (
    <div className={ro ? "pv ro" : "pv"}>
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
  const ex = cor ? null : call.exception_guide; // D-543 예외 안내(약속 v8 · 예외 기록에서 온 매뉴얼 밖 점검)
  const exRec = ex ? (ex.source?.record_id ?? ex.basis[0] ?? "") : ""; // 근거 예외 기록 번호
  const [kf, setKf] = useState<{ situation: string; action: string } | null>(null); // 「노하우 등록」 두 칸(열림)
  const ans = call.answer;
  const ins: Instruction | null | undefined = s.instruction;
  const editable = call.status === "none" || call.status === "waiting";
  const by = ans ? `${ans.by_name ?? ans.by ?? ""} ${ans.at ? hhmm(ans.at) : ""}`.trim() : "";
  const sendCall = () => {
    const body: Record<string, unknown> = { type: "call_send" };
    if (text !== null && text.trim() && text.trim() !== call.summary.text) body.summary = text.trim();
    void send(body);
  };
  const callBtn = <Btn cls="lg full warnb" label="파트장 호출" lead="phone-call" off={busy} onClick={sendCall} />;
  const summary = (
    <Summary call={call} label="파트장에게 보낼 요약" editable={editable} text={text} onText={setText} />
  );
  let right;
  if (ans?.answer === "approved" && ins && !approvedSeen) {
    right = (
      <div className="cd">
        <div className="banner ok">
          <Icon name="circle-check" />
          <div>
            <b>파트장 답 · 승인 후 진행 · {by}</b>
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
    // D-546 U4 대조(답장 u4-audit-fix): '보낸 요약'(읽기만) 아래 '파트장 호출 보냄 · 시각 / 답 기다림' 한 줄 · 설명 문장 0
    right = (
      <div className="cd">
        <Summary call={call} label="보낸 요약" editable={false} text={null} onText={() => {}} ro />
        <div className="wait">
          <b>파트장 호출 보냄 · {call.sent_at ? hhmm(call.sent_at) : ""}</b>
          <span>답 기다림</span>
        </div>
      </div>
    );
  } else if (call.status === "waiting") {
    right = (
      <div className="cd">
        <div className="banner warn">
          <Icon name="clock" />
          <div>
            <b>호출하지 않고 대기 중 · {call.waiting_at ? hhmm(call.waiting_at) : ""}</b>
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
            // 답장 001-zzx 사(가이드 24쪽): 작은 줄 · 제목 '정정 확인 · 절 이름' · 칩 '이상 → 정상'
            <div className="warn-h">
              <Icon name="hand" />
              <div>
                <span className="sm">파트장 확인이 필요합니다</span>
                <h3>
                  정정 확인 · {cor.section} {cor.title}
                </h3>
                <div className="tags">
                  <span className="ch gray">
                    {cor.before} → {cor.after}
                  </span>
                </div>
              </div>
            </div>
          ) : (
            <div className="warn-h">
              <Icon name="hand" />
              <div>
                <span className="sm">{ex ? "예외 기록에서 온 점검" : "다음 점검은 혼자 진행할 수 없습니다"}</span>
                <h3>{call.title}</h3>
                <div className="tags">
                  <GradeBadge grade={call.grade} />
                  <span className="ch blue">{ex ? `예외 기록 ${exRec}` : `매뉴얼 ${call.section}절`}</span>
                  {call.minutes != null ? <span className="ch gray">약 {call.minutes}분</span> : null}
                </div>
              </div>
            </div>
          )}
          {ex ? (
            // 답장 001-zzz10(사용자): 노하우 글 = 안내 글 + 출처 한 줄(앱 원본의 승인 예외 기록)
            <>
              <div className="sub">노하우</div>
              <div className="pv xkh">
                <p>{ex.text}</p>
                <span className="xsrc">
                  출처 · 예외 기록 {exRec}
                  {ex.source
                    ? ` · ${ex.source.equipment_id} · ${dateTime(ex.source.occurred_at).slice(5, 10)} — 상황 '${ex.source.situation}'`
                    : ""}
                </span>
              </div>
            </>
          ) : null}
          {kf ? (
            // 「노하우 등록」: 같은 카드 자리에 예외 상황 기록 두 칸(보고서 칸과 같은 꼴) · 열린 동안 목록 둘은 접음
            <div className="xkf">
              <div className="cd-h">
                <b>노하우 등록</b>
                <span className="ch gray">보고서와 함께 승인</span>
              </div>
              <span className="sm">어떤 상황이었나</span>
              <textarea
                className="memo"
                aria-label="어떤 상황이었나"
                maxLength={1000}
                value={kf.situation}
                onChange={(e) => setKf({ ...kf, situation: e.target.value })}
              />
              <span className="sm">무엇을 했나</span>
              <textarea
                className="memo"
                aria-label="무엇을 했나"
                maxLength={1000}
                value={kf.action}
                onChange={(e) => setKf({ ...kf, action: e.target.value })}
              />
              <div className="mb">
                <Btn cls="ghost" label="취소" onClick={() => setKf(null)} />
                <Btn
                  cls=""
                  label="등록"
                  off={busy}
                  onClick={() => {
                    void send({
                      type: "exception_draft",
                      exception_record: { situation: kf.situation.trim(), action: kf.action.trim() },
                    });
                    setKf(null);
                  }}
                />
              </div>
            </div>
          ) : (
            <>
            <div className="sub">지금까지 점검</div>
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
            </div>
            {ex ? (
              ex.next ? (
                <>
                  <div className="sub">원래 순서 다음</div>
                  <div className="tags xnext">
                    <span className="ch gray">
                      {ex.next.section} {ex.next.title}
                    </span>
                  </div>
                </>
              ) : null
            ) : cor ? null : ( // 정정 확인은 조치 뒤라 남은 후보 칸 없음(가이드 24쪽)
              <>
                <div className="sub">남은 후보</div>
                <div className="tags">
                  {call.candidates.map((c) => (
                    <span className="ch gray" key={c.code}>
                      {c.name} {c.pct}%
                    </span>
                  ))}
                </div>
              </>
            )}
            </>
          )}
          {ex && !kf ? ( // 답장 001-zzz10(사용자): 왼쪽 카드 오른쪽 아래 — 호출과 따로
            <div className="xkr">
              <Btn
                cls="ghost"
                label="노하우 등록"
                onClick={() => setKf({ situation: s.exception_draft?.situation ?? "", action: s.exception_draft?.action ?? "" })}
              />
            </div>
          ) : null}
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
  const label = "숙련자 인계 요약"; // D-530 답장 001-zzt 7: 괄호 이름표 뺌(가이드 28쪽)
  const rv = s.restart?.outcome === "outside" ? s.restart.value : null;
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
    // 결정 018 ④: 보낸 뒤 답 대기 — 파트장 호출과 같은 꼴(답장 u4-audit-fix: '보낸 요약' 아래 '보냄 · 시각 / 답 기다림')
    action = (
      <>
        <Summary call={call} label="보낸 요약" editable={false} text={null} onText={() => {}} ro />
        <div className="wait">
          <b>숙련자 인계 보냄 · {call.sent_at ? hhmm(call.sent_at) : ""}</b>
          <span>답 기다림</span>
        </div>
      </>
    );
  } else {
    action = (
      <>
        <Summary call={call} label={label} editable text={text} onText={setText} />
        <Btn cls="lg full warnb" label="숙련자 인계 보내기" lead="user" off={busy} onClick={sendIt} />
      </>
    );
  }
  return (
    <div className="ap-body">
      <div className="g64">
        {/* 답장 001-zzx 바(가이드 28쪽): 왼쪽 = 한 카드(빨강 머리 · 재가동 뒤 값 줄 + '지금까지 점검 · 조치' 체크 목록), 오른쪽 = 인계 요약 + 보내기 */}
        <div className="cd">
          <div className="warn-h bad">
            <Icon name="user" />
            <div>
              <span className="sm">{head}</span>
              <h3>{call.head}</h3>
              {rv ? (
                <span className="vline">
                  {rv.sensor} {rv.value_text} · 경계 {rv.boundary_text}
                </span>
              ) : null}
            </div>
          </div>
          <div className="sub">지금까지 점검 · 조치</div>
          <div className="cklist">
            {(s.path ?? []).map((p, i) => (
              <div className={`cki ${p.status}`} key={i}>
                <span className="cb">{p.status === "bad" ? "!" : <Icon name="check" />}</span>
                <span className="t">{p.detail ? `${p.title} · ${p.detail}` : p.title}</span>
              </div>
            ))}
          </div>
        </div>
        <div className="cd">{action}</div>
      </div>
    </div>
  );
}

export interface ReportProps {
  report: Report;
  busy: boolean;
  send: (body: Record<string, unknown>) => Promise<boolean> | void;
  onHome: () => void;
  onFinal?: (reportId: number) => void;
}

/** T09: 보고서 8항목(출처 · 고치기), 확정 전 확인 3항목, 확정 → 승인 대기(확정 뒤 수정 없음 — AC-33).
 *  D-528(가이드 정비자 12 · 13 · 반려 34쪽): 반려면 오른쪽 위에 반려 사유 · 「보고서 확정」은 확인 창(확정 · 취소) · 안내 문장 뺌. */
export function ReportScreen({ report, busy, send, onHome, onFinal }: ReportProps) {
  const [edit, setEdit] = useState<{ key: string; text: string } | null>(null);
  const [asking, setAsking] = useState(false);
  // D-538 예외 상황 기록(선택): 정비자가 예외라고 판단할 때만 적는 두 글 — 자동 정보는 서버가 확정 때 붙임
  const pre = report.exception_record ?? report.exception_draft; // D-543: 「노하우 등록」 초안이 있으면 칸에 미리 채움
  const [ex, setEx] = useState({ situation: pre?.situation ?? "", action: pre?.action ?? "" });
  const rej = report.rejection;
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
            {draft ? (
              <span className={`ch ${rej ? "red" : "amber"}`}>{rej ? "반려 · 고치는 중" : "초안"}</span>
            ) : (
              <span className="ch green">확정 · 승인 대기</span>
            )}
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
                  {f.fallback ? (
                    <>
                      <span className="ch fb">원문으로 대체됨</span>{" "}
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
          {draft && rej ? (
            <div className="banner bad rej" data-part="rejection">
              <Icon name="rotate-ccw" />
              <div>
                <b>
                  반려 사유 · {rej.by_name ?? ""} {rej.at ? hhmm(rej.at) : ""}
                </b>
                {rej.reason}
              </div>
            </div>
          ) : null}
          {draft || report.exception_record ? ( // D-538: 예외 상황 기록(선택) — 확정 전엔 적고, 뒤엔 읽기만
            <div className="cd kh">
              <div className="cd-h">
                <Icon name="message-square-plus" />
                <b>예외 상황 기록</b>
                <span className="ch gray">선택</span>
              </div>
              {(
                [
                  ["situation", "어떤 상황이었나"],
                  ["action", "무엇을 했나"],
                ] as const
              ).map(([k2, label]) => (
                <div className="khf" key={k2}>
                  <span className="sm">{label}</span>
                  {draft ? (
                    <textarea
                      className="memo"
                      aria-label={label}
                      maxLength={1000}
                      value={ex[k2]}
                      onChange={(e) => setEx({ ...ex, [k2]: e.target.value })}
                    />
                  ) : (
                    <div className="khv">{report.exception_record?.[k2]}</div>
                  )}
                </div>
              ))}
            </div>
          ) : null}
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
            {/* 답장 001-zzx 다(가이드 17 · 19쪽): 「보고서 확정」 · 확정 띠 · 「최종본 보기」「홈으로」는 확정 전 확인 카드 안 */}
            {draft ? (
              <div className="cta2">
                <Btn
                  label="보고서 확정"
                  icon="file-check-2"
                  off={busy || !report.can_confirm || edit !== null}
                  onClick={() => setAsking(true)}
                />
              </div>
            ) : (
              <>
                <div className="banner ok">
                  <Icon name="circle-check" />
                  <div>
                    <b>보고서를 확정했습니다 · {report.confirmed_at ? hhmm(report.confirmed_at) : ""}</b>
                  </div>
                </div>
                {report.report_id != null && onFinal ? ( // D-528 가이드 정비자 13: 확정 뒤 「최종본 보기」(새 화면)
                  <Btn cls="lg full" label="최종본 보기" onClick={() => onFinal(report.report_id as number)} />
                ) : null}
                <Btn cls="lg full ghost" label="홈으로" onClick={onHome} />
              </>
            )}
          </div>
        </div>
      </div>
      {asking && draft ? (
        <>
          <div className="dim" />
          <div className="modal" role="dialog" aria-label="보고서 확정">
            <div className="mh">
              <Icon name="file-check-2" />
              <b>보고서를 확정합니까?</b>
            </div>
            <div className="bub ai">
              <div>확정하면 파트장 승인 대기로 넘어갑니다.</div>
            </div>
            <div className="mb">
              <span className="btn ghost" role="button" tabIndex={0} onClick={() => setAsking(false)}>
                취소
              </span>
              <span
                className={`btn${busy || !report.can_confirm ? " dis" : ""}`}
                role="button"
                tabIndex={0}
                onClick={() => {
                  if (busy || !report.can_confirm) return;
                  setAsking(false);
                  const situation = ex.situation.trim();
                  const action = ex.action.trim();
                  void send({ type: "report_confirm", ...(situation || action ? { exception_record: { situation, action } } : {}) });
                }}
              >
                확정
              </span>
            </div>
          </div>
        </>
      ) : null}
    </div>
  );
}
