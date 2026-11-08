// 파트장 2 승인 대기(가이드 30쪽): 요약 셋 → 확정된 보고서 → (호출 없이 조치함 · 약속 v9) → 오늘 기록(감사 기록 최근 5줄) · 처리할 호출.
// 값은 지금 API 그대로(/api/lead/overview · /api/lead/audit · /api/lead/calls, 부록 4 — 새 API 0). 보고서 검토는 Review.tsx.

import { hhmm, shortCause, type Schemas } from "@c1a15/ui";
import { Bar, headDate, LBtn } from "./Frame";

type Overview = Schemas["LeadOverview"];
type Audit = Schemas["LeadAudit"];
type Calls = Schemas["LeadCalls"];

export const KIND_LABEL: Record<string, string> = { approval: "파트장 호출", handover: "숙련자 인계" };
export const appLabel = (app: string) => (app === "system" ? "시스템" : `${app} 앱`);

export function ApprovalList({
  data,
  audit,
  calls,
  onOpen,
  onCall,
  onAudit,
  onCalls,
}: {
  data: Overview;
  audit: Audit | null;
  calls: Calls | null;
  onOpen: (reportId: number) => void;
  onCall: (callId: number) => void;
  onAudit: () => void;
  onCalls: () => void;
}) {
  const t = data.tiles;
  const logs = (audit?.rows ?? []).slice(0, 5);
  const open = calls?.rows ?? [];
  const acted = data.acted ?? [];
  return (
    <>
      <Bar title="승인 대기" date={headDate(data.now)} />
      <div className="ltiles">
        <div>
          <b className="acc">{t.awaiting}</b>
          <span>승인 대기</span>
        </div>
        <div>
          <b>{t.calls_open}</b>
          <span>처리할 호출</span>
        </div>
        <div>
          <b>{t.violations}</b>
          <span>권한 위반</span>
        </div>
      </div>
      <div className="lsect">
        <div className="lsect-h">
          확정된 보고서<span className="c">{data.rows.length}건</span>
        </div>
        <table className="lt">
          <tbody>
            <tr>
              <th>설비 · 알람</th>
              <th>확정 원인</th>
              <th>작성</th>
              <th className="n">확정</th>
              <th className="n">근거 기록</th>
              <th>권한</th>
              <th />
            </tr>
            {data.rows.map((r) => (
              <tr key={r.report_id} className="pick" data-report={r.report_id} onClick={() => onOpen(r.report_id)}>
                <td>
                  <b>{r.equipment_id}</b>
                  <div className="m">{r.group_name}</div>
                </td>
                {/* D-642 R2: 한 줄 = 서버 줄 값(예외면 '예외상황 · 점검 → 조치', 아니면 원인 이름) · 칸 안 한 줄(긴 글은 「검토」) */}
                <td className="cause">{r.line || shortCause(r.cause, 40)}</td>
                <td>{r.author_name}</td>
                <td className="n">{r.confirmed_at ? hhmm(r.confirmed_at) : ""}</td>
                <td className="n">
                  {r.evidence_count}건{r.low_evidence ? <span className="tx warn"> 근거 적음</span> : null}
                </td>
                <td>
                  <span className={`tx ${r.violations ? "bad" : "ok"}`}>위반 {r.violations}</span>
                </td>
                <td className="r">
                  <LBtn cls="g" label="검토" onClick={() => onOpen(r.report_id)} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {data.rows.length === 0 ? <div className="lempty">승인 대기 보고서가 없습니다</div> : null}
      </div>
      {acted.length ? ( // 약속 v9 lead_notice acted_without_call: 정비자가 [예외] 바로 조치를 고른 세션 — 있을 때만
        <div className="lsect" data-part="acted">
          <div className="lsect-h">
            호출 없이 조치함<span className="c">{acted.length}건</span>
          </div>
          <table className="lt">
            <tbody>
              <tr>
                <th>설비 · 알람</th>
                <th>정비자</th>
                <th className="n">조치 시작</th>
                <th />
              </tr>
              {acted.map((r) => (
                <tr key={r.session_id} data-acted={r.session_id}>
                  <td>
                    <b>{r.equipment_id}</b>
                    <div className="m">{r.group_name}</div>
                  </td>
                  <td>{r.tech_name ?? ""}</td>
                  <td className="n">{hhmm(r.at)}</td>
                  <td className="r">
                    <span className="tx warn">호출 없이 조치함</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : null}
      <div className="lgrid32">
        <div className="lsect" data-part="today">
          <div className="lsect-h">
            오늘 기록<span className="c">{audit ? audit.rows.length : 0}건</span>
          </div>
          <table className="lt">
            <tbody>
              <tr>
                <th className="n">시각</th>
                <th>앱</th>
                <th>사용자</th>
                <th>행동</th>
                <th>대상</th>
              </tr>
              {logs.length ? (
                logs.map((x) => (
                  <tr key={x.audit_id} className="lsm">
                    <td className="n">{hhmm(x.at)}</td>
                    <td>{appLabel(x.app)}</td>
                    <td>{x.user_name}</td>
                    <td className="w">{x.action /* D-642 R2: 긴 행동 글은 칸 안에서 줄바꿈 */}</td>
                    <td>
                      {x.report_id ? (
                        <button type="button" className="ltx" onClick={() => onOpen(x.report_id as number)}>
                          보고서 보기
                        </button>
                      ) : (
                        (x.equipment_id ?? x.target)
                      )}
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={5} className="lnone">
                    기록이 없습니다
                  </td>
                </tr>
              )}
            </tbody>
          </table>
          <div className="lmore">
            <button type="button" className="ltx" onClick={onAudit}>
              감사 기록 전체 보기
            </button>
          </div>
        </div>
        <div className="lsect" data-part="calls">
          <div className="lsect-h">
            처리할 호출<span className="c">{open.length}건</span>
          </div>
          <table className="lt">
            <tbody>
              <tr>
                <th className="n">시각</th>
                <th>설비 · 알람</th>
                <th>유형</th>
              </tr>
              {open.length ? (
                open.map((c) => (
                  <tr key={c.call_id} className="pick lsm" data-call={c.call_id} onClick={() => onCall(c.call_id)}>
                    <td className="n">{c.sent_at ? hhmm(c.sent_at) : ""}</td>
                    <td>
                      <b>{c.equipment_id}</b>
                    </td>
                    <td>{KIND_LABEL[c.kind]}</td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={3} className="lnone">
                    처리할 호출이 없습니다
                  </td>
                </tr>
              )}
            </tbody>
          </table>
          <div className="lmore">
            <button type="button" className="ltx" onClick={onCalls}>
              호출 전체 보기
            </button>
          </div>
        </div>
      </div>
    </>
  );
}
