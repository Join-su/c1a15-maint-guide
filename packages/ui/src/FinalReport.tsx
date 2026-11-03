// 보고서 최종본(D-528 · 가이드 정비자 14 · 파트장 2 · 부록 5): 문서 한 장 — 머리 · 진행 넷 · 구역 1 ~ 5 · 꼬리.
// 두 앱이 같은 화면을 부른다(정비자: 확정 뒤 · 홈 최근 보고서, 파트장: 보고서 검토 본문). 값은 서버 최종본 읽기 그대로, 없는 값은 넣지 않는다.
// 스타일은 styles/final-report.css(앱 main.tsx에서 불러옴).

import type { Schemas } from "./api";
import { hhmm } from "./format";

type Final = Schemas["FinalReport"];

const STATUS: Record<string, { label: string; cls: string }> = {
  awaiting_approval: { label: "승인 대기", cls: "wait" },
  approved: { label: "승인 완료", cls: "ok" },
  rejected: { label: "반려", cls: "bad" },
};

const t = (iso: string | null | undefined) => (iso ? hhmm(iso) : "");

export function FinalReport({ data }: { data: Final }) {
  const approved = data.status === "approved";
  const rejected = data.status === "rejected";
  const cb = data.cause_basis; // 답장 001-zzx-2(가이드 20쪽): 확정 근거 = 확정 원인을 정한 점검 결과 · 메모
  const steps: [string, boolean][] = [
    ["초안 자동 작성", true],
    [`정비자 ${data.rejected_before ? "다시 " : ""}확정${!rejected && data.confirmed_at ? ` ${t(data.confirmed_at)}` : ""}`, !rejected && !!data.confirmed_at],
    [`파트장 승인${approved && data.decision ? ` ${t(data.decision.at)}` : ""}`, approved],
    ["이력 추가", approved],
  ];
  const now = steps.findIndex(([, done]) => !done);
  const st = STATUS[data.status] ?? { label: data.status, cls: "" };
  const lead = data.decision
    ? `${data.decision.by_name} · ${data.decision.kind === "approved" ? "승인" : "반려"} ${t(data.decision.at)}`
    : "승인 대기";
  const g = data.grade_use;
  return (
    <article className="fdoc" data-report={data.report_id}>
      <header className="fd-h">
        <div>
          <h1>정비 보고서 {data.equipment_id}</h1>
          <p>
            {data.equipment_type} · 알람 {t(data.occurred_at)}
            {data.confirmed_at ? ` · 보고서 확정 ${t(data.confirmed_at)}` : ""} · 작성 {data.author_name}({data.author_role})
          </p>
        </div>
        <div className="fd-st">
          {data.lock_at ? <span>잠금 확인 {t(data.lock_at)}</span> : null}
          <span className={st.cls}>{st.label}</span>
        </div>
      </header>
      <ol className="fd-steps">
        {steps.map(([label, done], i) => (
          <li key={i} className={done ? "done" : i === now ? "now" : ""}>
            <b>{i + 1}</b>
            {label}
          </li>
        ))}
      </ol>
      <div className="fd-2">
        <section>
          <h2>1. 이상 내용 · 센서 근거</h2>
          <table>
            <tbody>
              <tr>
                <th>센서</th>
                <th className="n">현재</th>
                <th>평소 범위</th>
                <th>상태</th>
              </tr>
              {data.sensors.map((s) => (
                <tr key={s.name} className={s.out_of_range ? "hot" : ""}>
                  <td>{s.name}</td>
                  <td className="n">
                    <b>{s.value_text}</b>
                  </td>
                  <td>{s.range_text}</td>
                  <td>{s.status}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {data.sensor_evidence ? <p className="fd-note">{data.sensor_evidence}</p> : null}
        </section>
        <section>
          <h2>2. 원인 분석</h2>
          <table>
            <tbody>
              <tr>
                <th>원인 후보</th>
                <th className="n">진단 때</th>
                <th className="n">근거</th>
                <th>결과</th>
              </tr>
              {data.causes.map((c) => (
                <tr key={c.name} className={c.confirmed ? "hot" : ""}>
                  <td>{c.name}</td>
                  <td className="n">{c.probability}%</td>
                  <td className="n">{c.evidence}건</td>
                  <td>{c.result}</td>
                </tr>
              ))}
            </tbody>
          </table>
          <p className="fd-note">
            <b>확정 원인</b> {data.cause}
            {cb ? (
              <>
                {" · "}
                <b>확정 근거</b> {cb.title}({cb.section}) 결과 {cb.value}
                {cb.memo ? ` · 메모 "${cb.memo}"` : ""}
              </>
            ) : null}
            <br />
            <b>근거 사례</b> {data.evidence_records}
          </p>
        </section>
      </div>
      <section>
        <h2>3. 조치 경과</h2>
        <table>
          <tbody>
            <tr>
              <th className="n" style={{ width: 60 }}>
                시각
              </th>
              <th style={{ width: 80 }}>누가</th>
              <th>내용</th>
              <th style={{ width: 70 }}>매뉴얼</th>
              <th style={{ width: 48 }}>등급</th>
            </tr>
            {data.timeline.map((x, i) => (
              <tr key={i}>
                <td className="n">{t(x.at)}</td>
                <td>{x.who}</td>
                <td>{x.text}</td>
                <td>{x.section ? `${x.section}절` : "—"}</td>
                <td>{x.grade ? <span className="fd-g">{x.grade}</span> : "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
      <div className="fd-2">
        <section>
          <h2>4. 조치 결과</h2>
          <table className="fd-kv">
            <tbody>
              <tr>
                <th>조치</th>
                <td>{data.action}</td>
              </tr>
              {data.restart ? (
                <tr>
                  <th>재가동 뒤</th>
                  <td>{data.restart}</td>
                </tr>
              ) : null}
              <tr>
                <th>정지 시간</th>
                <td>{data.downtime}</td>
              </tr>
              <tr>
                <th>권한 사용</th>
                <td>
                  A {g.A ?? 0} · B {g.B ?? 0} · C {g.C ?? 0}
                </td>
              </tr>
            </tbody>
          </table>
        </section>
        <section>
          <h2>5. 미확인 · 주간 요청</h2>
          <div className="fd-open">{data.unresolved}</div>
        </section>
      </div>
      <footer className="fd-f">
        <div>
          <span>작성(정비자)</span>
          <b>
            {data.author_name}
            {data.confirmed_at ? ` · ${t(data.confirmed_at)} 확정` : ""}
          </b>
        </div>
        <div>
          <span>승인(파트장)</span>
          <b>{lead}</b>
        </div>
      </footer>
    </article>
  );
}
