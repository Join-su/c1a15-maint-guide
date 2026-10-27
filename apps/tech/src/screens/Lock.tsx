// T05 잠금(R1): 잠금 전에는 1.2절 절차만 보이고 지시 내용은 내려받지 않는다(가린 자리는 빈 자리 표시).
// 잠금 뒤에는 사전 확인 절(점수 없이 항상 먼저).

import { GradeBadge, hhmm, Icon, type SessionWithPreview } from "@c1a15/ui";

export function Proc({ steps }: { steps: string[] }) {
  return (
    <ol className="proc">
      {steps.map((t, i) => (
        <li key={i}>
          <span>{i + 1}</span>
          {t}
        </li>
      ))}
    </ol>
  );
}

export function LockOk({ at }: { at: string | null | undefined }) {
  return (
    <div className="lockok">
      <Icon name="lock" />
      <b>잠금 확인 완료</b>
      <span>1.2절 · {at ? hhmm(at) : ""}</span>
      <Icon name="check" className="ok" />
    </div>
  );
}

// 가린 자리: 지시 내용을 내려받지 않으므로 내용 없는 줄만 흐리게 보인다.
const MASK = ["", "", ""];

export function LockScreen({ s, busy, onLock }: { s: SessionWithPreview; busy: boolean; onLock: () => void }) {
  const li = s.lock_instruction;
  return (
    <div className="ap-body">
      <div className="g64">
        <div className="cd">
          <div className="lockbox">
            <Icon name="lock" />
            <h3>잠금 확인이 필요합니다</h3>
            <span>
              매뉴얼 {li?.section ?? "1.2"}절 · {li?.title}
            </span>
          </div>
          <Proc steps={li?.steps ?? []} />
          <span className={`btn lg full${busy ? " dis" : ""}`} role="button" tabIndex={0} onClick={onLock}>
            잠금 완료
          </span>
          <span className="note">누른 시각이 기록되고 보고서에 자동으로 들어갑니다.</span>
        </div>
        <div className="cd">
          <div className="masked" aria-hidden="true">
            <ol className="proc">
              {MASK.map((_, i) => (
                <li key={i}>
                  <span>{i + 1}</span>
                  {" ".repeat(24)}
                </li>
              ))}
            </ol>
          </div>
          <div className="hint">
            <Icon name="info" />
            잠금 확인 전에는 지시 내용이 가려져 있습니다. 다른 설비로 옮기면 그 설비에서 다시 잠금을 확인합니다.
          </div>
        </div>
      </div>
    </div>
  );
}

/** 사전 확인 뒤 다음 안내 = 진단 미리보기(서버, P-06 · P-18). */
export function nextNote(s: SessionWithPreview): string {
  const p = s.preview;
  if (p.kind === "call") return `다음: 파트장 호출 요약(${p.section}절 ${p.title ?? ""}, ${p.grade}등급)`;
  if (p.kind === "instruct" || p.kind === "instruct_after_checklist") return `다음: 지시된 점검 1개(${p.section}절 ${p.title ?? ""})`;
  return "";
}

export function PrecheckScreen({
  s,
  busy,
  values,
  onValues,
  onDone,
}: {
  s: SessionWithPreview;
  busy: boolean;
  values: string;
  onValues: (v: string) => void;
  onDone: () => void;
}) {
  const ins = s.instruction;
  if (!ins) return null;
  return (
    <div className="ap-body">
      <div className="g64">
        <div className="cd">
          <LockOk at={s.lock_at} />
          <div className="ins-h">
            <span className="sm">사전 확인 · 점수 없이 항상 먼저</span>
            <h3>{ins.title}</h3>
            <div className="tags">
              <GradeBadge grade={ins.grade} />
              <span className="ch blue">매뉴얼 {ins.section}절</span>
              {ins.minutes != null ? <span className="ch gray">약 {ins.minutes}분</span> : null}
            </div>
          </div>
          {ins.fallback ? <div className="orig">{ins.original}</div> : <Proc steps={ins.steps} />}
        </div>
        <div className="cd">
          <div className="res">
            <b className="rt">사전 확인</b>
            <span className="sm">기록할 값</span>
            <textarea className="memo" aria-label="기록할 값" value={values} onChange={(e) => onValues(e.target.value)} />
            <span
              className={`btn lg full${busy || !values.trim() ? " dis" : ""}`}
              role="button"
              tabIndex={0}
              onClick={busy || !values.trim() ? undefined : onDone} // D-422: 값 없이 다음으로 가지 않음(서버도 거절)
            >
              사전 확인 완료 <Icon name="check" />
            </span>
            <span className="note">{nextNote(s)}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
