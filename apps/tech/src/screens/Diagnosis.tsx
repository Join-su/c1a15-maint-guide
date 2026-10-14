// T04 진단: 원인 후보 순위(이름 = cause_names, A-04) · 비슷한 과거 기록 3건(P-19 ④) · 다음 점검(미리보기, P-06 · P-18).
// 첫 판정이 호출이면 같은 구조에서 강조 카드 값만 바뀐다(T04 / first_call, 예외는 이 상태에서만 — CO-42).

import { GradeBadge, Icon, RecordCard, type SessionWithPreview } from "@c1a15/ui";

type Diag = Pick<SessionWithPreview, "probabilities" | "evidence" | "cause_names" | "similar_cards" | "low_evidence" | "preview">;

export function rankRows(s: Diag): { code: string; name: string; pct: number; n: number }[] {
  return Object.entries(s.probabilities)
    .map(([code, pct]) => ({ code, name: s.cause_names[code] ?? code, pct, n: s.evidence[code] ?? 0 }))
    .sort((a, b) => b.pct - a.pct);
}

export function NextCard({ s, onStart, past }: { s: Diag; onStart: () => void; past?: boolean }) {
  const p = s.preview;
  const call = p.kind === "call";
  return (
    <div className="cd hl">
      <div className="nx">
        <span className="sm">다음 점검</span>
        <h3>{call ? "파트장 호출 필요" : p.title}</h3>
        <div className="tags">
          <GradeBadge grade={p.grade} />
          {p.section ? <span className="ch blue">매뉴얼 {p.section}절</span> : null}
          {p.minutes != null ? (
            <span className="ch gray">{call ? `${p.title} · 약 ${p.minutes}분` : `약 ${p.minutes}분`}</span>
          ) : null}
          {p.reason_fallback ? <span className="ch fb">{p.reason_label}</span> : null}
        </div>
        {p.reason ? (
          <div className="why">
            <b>{call ? "호출이 필요한 이유" : "이 점검을 고른 이유"}</b>
            <span>{p.reason}</span>
          </div>
        ) : null}
        {s.low_evidence ? (
          <div className="banner warn">
            <Icon name="triangle-alert" />
            <div>
              <b>근거 적음</b>비슷한 과거 기록이 3건 미만입니다. 지시는 그대로 따르되, 결과 메모를 더 자세히 적으십시오.
            </div>
          </div>
        ) : null}
        <span
          className={past ? `btn lg dis full${call ? " warnb" : ""}` : `btn lg full${call ? " warnb" : ""}`}
          role="button"
          tabIndex={0}
          onClick={past ? undefined : onStart}
        >
          점검 시작 <Icon name="arrow-right" />
        </span>
      </div>
    </div>
  );
}

export function DiagnosisScreen({
  s,
  onRecord,
  onStart,
  past,
}: {
  s: Diag;
  onRecord: (id: string) => void;
  onStart: () => void;
  past?: boolean; // T15 / diagnosis: 그때의 원인 순위 · 첫 지시, 조작은 잠김
}) {
  const rows = rankRows(s);
  return (
    <div className={past ? "ap-body past" : "ap-body"}>
      <div className="g64">
        <div>
          <div className="cd ">
            <div className="cd-h">
              <Icon name="list-checks" />
              <b>원인 후보 순위</b>
              {s.low_evidence ? <span className="ch amber">근거 적음</span> : null}
            </div>
            {rows.map((r, i) => (
              <div className={`rk ${i === 0 ? "on" : ""}`} key={r.code}>
                <span className="rn">{i + 1}</span>
                <b>{r.name}</b>
                <span className="rb">
                  <i style={{ width: `${r.pct}%` }} />
                </span>
                <span className="rv">{r.pct}%</span>
                <span className="rs">근거 {r.n}</span>
              </div>
            ))}
            <div className="hint">
              <Icon name="info" />
              근거 n = 비슷한 과거 기록 상위 10건 중 그 원인으로 확정된 기록 수. 이 빈도로 시작해, 점검 결과를 입력할 때마다 다시
              계산됩니다.
            </div>
          </div>
          <div className="cd mt">
            <div className="cd-h">
              <Icon name="history" />
              <b>비슷한 과거 기록 {s.similar_cards.length}건 · 상위 10건 중</b>
            </div>
            <div className="hcs">
              {s.similar_cards.map((c) => (
                <RecordCard key={c.record_id} card={c} onOpen={onRecord} />
              ))}
            </div>
            <div className="hint">
              <Icon name="info" />
              카드를 누르면 그 기록 전체를 봅니다.
            </div>
          </div>
        </div>
        <NextCard s={s} onStart={onStart} past={past} />
      </div>
    </div>
  );
}
