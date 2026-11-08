// T04 진단: 원인 후보 순위(이름 = cause_names, A-04) · 비슷한 과거 기록 3건(P-19 ④) · 다음 점검(미리보기, P-06 · P-18).
// 첫 판정이 호출이면 같은 구조에서 강조 카드 값만 바뀐다(T04 / first_call, 예외는 이 상태에서만 — CO-42).
// D-528(가이드 정비자 4): 순위 아래 「근거 n = …」 설명 · 과거 기록 아래 안내 문장 뺌.
// D-637(리허설 F1 · F8 · F2 · 표시 · 글만, 셈 손 0): 확률(판정 출력 probabilities = 이 설비의 지난 같은 알람 기록 원인 비율)과
// 오른쪽 수(evidence = 비슷한 기록 상위 10건 중 그 원인)는 출처가 달라 '근거 n' → '비슷한 기록 n건' · 순위 아래 출처 한 줄 ·
// 100%면 까닭 한 줄 · 지시 카드 이유 아래 고르는 셈 한 줄(rules.best_pick: A · B 점검 중 원인 확률 ÷ 분이 가장 큰 것).
// 리허설 F11: 다음 점검 카드에 예외가 맞은 까닭 · 안 맞은 까닭 한 줄(서버 글 그대로).

import { useState } from "react";
import {
  GradeBadge,
  Icon,
  RecordCard,
  type SessionWithPreview,
} from "@c1a15/ui";
import { SwitchRows } from "./Instruction";
import { SecChip } from "./Lock";

type Diag = Pick<
  SessionWithPreview,
  | "probabilities"
  | "evidence"
  | "cause_names"
  | "similar_cards"
  | "low_evidence"
  | "preview"
  | "exception_topic"
  | "exception_why"
  | "exception_miss"
>;

export function rankRows(
  s: Diag,
): { code: string; name: string; pct: number; n: number }[] {
  return Object.entries(s.probabilities)
    .map(([code, pct]) => ({
      code,
      name: s.cause_names[code] ?? code,
      pct,
      n: s.evidence[code] ?? 0,
    }))
    .sort((a, b) => b.pct - a.pct);
}

const RANK_SOURCE = "확률: 이 설비의 지난 같은 알람 기록에서 원인별 비율 · 비슷한 기록: 비슷한 과거 기록 상위 10건 중 그 원인 수";

// 지시 카드(A · B)만 — 호출 · 고른 점검 · 원인 모름이면 null. 분을 모르면 숫자 부분만 뺌.
export function pickRule(s: Diag): string | null {
  const p = s.preview;
  if (p.picked || !p.cause || !p.title || (p.kind !== "instruct" && p.kind !== "instruct_after_checklist")) return null;
  const name = s.cause_names[p.cause] ?? p.cause;
  const pct = s.probabilities[p.cause];
  const nums = pct != null && p.minutes != null ? ` — ${name} ${pct}% ÷ 약 ${p.minutes}분` : "";
  const sec = p.section ? `(매뉴얼 ${p.section}절)` : "";
  return `고르는 셈: A · B 등급 점검 중 '원인 확률 ÷ 걸리는 분'이 가장 큰 것${nums}. ${p.title} = ${name} 확인 점검${sec}`;
}

export function NextCard({
  s,
  onStart,
  past,
  onSwitch,
}: {
  s: Diag;
  onStart: () => void;
  past?: boolean;
  onSwitch?: (section: string) => void; // D-585 진단에서 고름 — 잠금 · 사전 확인 뒤 그 점검
}) {
  const p = s.preview;
  const pick = p.picked;
  const call = !pick && p.kind === "call";
  const [switching, setSwitching] = useState(false);
  const rule = pickRule(s);
  // F11: 예외 후보가 왜 맞았나(배운 기기 · 근거 기록 · 이 기기 같은 정비 · 며칠 전) · 같은 증상인데 왜 안 맞았나(최근 같은 정비 없음)
  const exLine = s.exception_why ? (
    <span className="xwhy" data-part="ex-why">
      예외 후보 · {s.exception_why}
    </span>
  ) : s.exception_miss ? (
    <span className="xwhy" data-part="ex-miss">
      {s.exception_miss}
    </span>
  ) : null;
  return (
    <div className="cd hl">
      <div className="nx">
        <span className="sm">다음 점검</span>
        <h3>{pick ? pick.title : call ? "파트장 호출 필요" : p.title}</h3>
        <div className="tags">
          <GradeBadge grade={pick ? pick.grade : p.grade} />
          {(pick ?? p).section ? (
            <SecChip
              section={(pick ?? p).section ?? ""}
              topic={s.exception_topic}
            />
          ) : null}
          {!pick && p.minutes != null ? (
            <span className="ch gray">
              {call ? `${p.title} · 약 ${p.minutes}분` : `약 ${p.minutes}분`}
            </span>
          ) : null}
          {!pick && p.reason_fallback ? (
            <span className="ch fb">{p.reason_label}</span>
          ) : null}
        </div>
        {p.reason && !pick ? (
          <div className="why">
            <b>{call ? "호출이 필요한 이유" : "이 점검을 고른 이유"}</b>
            <span>{p.reason}</span>
            {rule ? (
              <span className="rs" data-part="pick-rule">
                {rule}
              </span>
            ) : null}
            {exLine}
          </div>
        ) : (
          exLine
        )}
        {!past && onSwitch && p.candidates?.length ? (
          <div className="refs">
            <span
              className="lk sw"
              role="button"
              tabIndex={0}
              onClick={() => setSwitching(true)}
            >
              <Icon name="arrow-left-right" />
              점검 바꾸기
            </span>
          </div>
        ) : null}
        {s.low_evidence ? (
          <div className="banner warn">
            <Icon name="triangle-alert" />
            <div>
              <b>근거 적음</b>비슷한 과거 기록이 3건 미만입니다. 지시는 그대로
              따르되, 결과 메모를 더 자세히 적으십시오.
            </div>
          </div>
        ) : null}
        <span
          className={
            past
              ? `btn lg dis full${call ? " warnb" : ""}`
              : `btn lg full${call ? " warnb" : ""}`
          }
          role="button"
          tabIndex={0}
          onClick={past ? undefined : onStart}
        >
          점검 시작 <Icon name="arrow-right" />
        </span>
      </div>
      {switching && onSwitch ? (
        <>
          <div className="dim" />
          <div className="modal swm" role="dialog" aria-label="점검 바꾸기">
            <div className="mh">
              <Icon name="arrow-left-right" />
              <b>점검 바꾸기</b>
            </div>
            <div className="swl">
              <SwitchRows
                cands={(p.candidates ?? []).filter(
                  (c) => c.section !== pick?.section,
                )}
                busy={false}
                topic={s.exception_topic}
                onPick={(section) => {
                  setSwitching(false);
                  onSwitch(section);
                }}
              />
            </div>
            <div className="mb">
              <span
                className="btn ghost"
                role="button"
                tabIndex={0}
                onClick={() => setSwitching(false)}
              >
                취소
              </span>
            </div>
          </div>
        </>
      ) : null}
    </div>
  );
}

export function DiagnosisScreen({
  s,
  onRecord,
  onStart,
  past,
  onSwitch,
}: {
  s: Diag;
  onRecord: (id: string) => void;
  onStart: () => void;
  past?: boolean; // T15 / diagnosis: 그때의 원인 순위 · 첫 지시, 조작은 잠김
  onSwitch?: (section: string) => void;
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
              {s.low_evidence ? (
                <span className="ch amber">근거 적음</span>
              ) : null}
            </div>
            {rows.map((r, i) => (
              <div className={`rk ${i === 0 ? "on" : ""}`} key={r.code} style={{ gridTemplateColumns: "28px 150px 1fr 48px 104px" }}>
                <span className="rn">{i + 1}</span>
                <b>{r.name}</b>
                <span className="rb">
                  <i style={{ width: `${r.pct}%` }} />
                </span>
                <span className="rv">{r.pct}%</span>
                <span className="rs">비슷한 기록 {r.n}건</span>
              </div>
            ))}
            {rows.length ? (
              <div className="rs" data-part="rank-source" style={{ marginTop: 10, lineHeight: 1.6 }}>
                {RANK_SOURCE}
              </div>
            ) : null}
            {rows[0]?.pct === 100 ? (
              <div className="rs" data-part="rank-full" style={{ marginTop: 4, lineHeight: 1.6 }}>
                100%인 까닭: 이 설비의 지난 같은 알람 기록이 모두 이 원인({rows[0].name})이었습니다.
              </div>
            ) : null}
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
          </div>
        </div>
        <NextCard s={s} onStart={onStart} past={past} onSwitch={onSwitch} />
      </div>
    </div>
  );
}
