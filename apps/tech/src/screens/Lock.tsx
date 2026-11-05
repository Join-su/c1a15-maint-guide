// T05 잠금(R1): 잠금 전에는 1.2절 절차만 보이고 지시 내용은 내려받지 않는다(뒤 칸은 비어 있음).
// 잠금 뒤에는 사전 확인 절(점수 없이 항상 먼저 — 화면 문구는 D-528로 뺌).

import { GradeBadge, hhmm, Icon, type SessionWithPreview } from "@c1a15/ui";

/** 약속 v8 예외 절(EX-<이력 번호>) · v9 예외 진행 절(EX-NEW) — 매뉴얼 밖 절. */
export const isException = (section: string) => section.startsWith("EX-");
export const EX_NEW = "EX-NEW"; // 약속 v9 [예외] 진행 절(매뉴얼 · 기록 밖)

/** 절 이름: 매뉴얼 절 '4.3절' · 예외 절 번호 그대로 · 예외 진행 '예외'. */
export const secName = (section: string) => (section === EX_NEW ? "예외" : isException(section) ? section : `${section}절`);

/** 지시 머리 절 칩: 매뉴얼 절은 '매뉴얼 4.3절', 예외 절은 '예외상황-{주제}'(정답지 고침A · 주제 없으면 '예외 기록 H-0244'),
 *  예외 진행은 '예외'. */
export function SecChip({ section, topic }: { section: string; topic?: string | null }) {
  const ex = topic ? `예외상황-${topic}` : `예외 기록 ${section.slice(3)}`;
  const label = section === EX_NEW ? "예외" : isException(section) ? ex : `매뉴얼 ${section}절`;
  return <span className="ch blue">{label}</span>;
}

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

// D-528(가이드 정비자 5): 잠금 확인 = 가운데 큰 창(680px) · 뒤는 어둡게(지시 내용은 내려받지 않아 빈 칸만) · 단계 띠만 위에 남아
// 「진단 ›」으로 돌아감(창을 닫는 다른 길 없음). 「누른 시각이 기록되고 …」 · 가린 칸 안내 문장 뺌.
export function LockScreen({ s, busy, onLock }: { s: SessionWithPreview; busy: boolean; onLock: () => void }) {
  const li = s.lock_instruction;
  return (
    <>
      <div className="ap-body" aria-hidden="true">
        <div className="g64">
          <div className="cd" />
          <div className="cd" />
        </div>
      </div>
      <div className="lockdim" />
      <div className="lockm" role="dialog" aria-label="잠금 확인">
        <div className="n-lockbox">
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
      </div>
    </>
  );
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
            <span className="sm">사전 확인</span>
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
          </div>
        </div>
      </div>
    </div>
  );
}
