// T03 알람 화면: 증상 · 계통 · 이탈 수 · 추이 · 센서 표 · AI 해석(R8) · 찾은 기록 수(P-19 ③). '진단 보기'가 유일한 다음 행동.

import { hhmm, Icon, type SessionView } from "@c1a15/ui";

type Block = SessionView["alarm"];

const GROUP_ICON: Record<string, string> = { CL: "thermometer" };

/** 같은 설비 직전 12회 추이(R11)와 경계 점선. 위치 계산은 그리기만 한다(값은 서버). */
export function Trend({ a }: { a: Block }) {
  const vals = a.trend.map((p) => p.value);
  const b = a.alarm.boundary;
  const lo = Math.min(b, ...vals);
  const hi = Math.max(b, ...vals);
  const span = hi - lo || 1;
  const y = (v: number) => 72 - ((v - lo) / span) * 50;
  const x = (i: number) => (vals.length > 1 ? 10 + (300 * i) / (vals.length - 1) : 310);
  const d = vals.map((v, i) => `${i ? "L" : "M"}${Math.round(x(i))},${Math.round(y(v))}`).join(" ");
  const by = Math.round(y(b));
  return (
    <svg viewBox="0 0 330 90" className="spk" role="img" aria-label={a.trend_title ?? "추이"}>
      <line x1="0" y1={by} x2="330" y2={by} className="thr" />
      <text x="4" y={by - 4} className="tl">
        {a.boundary_text}
      </text>
      {vals.length ? <path d={d} className="ln" /> : null}
      {vals.length ? <circle cx={Math.round(x(vals.length - 1))} cy={Math.round(y(vals[vals.length - 1]))} r="5" className="pt" /> : null}
    </svg>
  );
}

/** past = T15 / alarm(지난 화면): 같은 화면, 조작은 잠김. */
export function AlarmScreen({ s, onNext, past }: { s: Pick<SessionView, "alarm">; onNext: () => void; past?: boolean }) {
  const a = s.alarm;
  return (
    <div className={past ? "ap-body past" : "ap-body"}>
      <div className="g73">
        <div className="cd">
          <div className="alh">
            <span className="ali">
              <Icon name={GROUP_ICON[a.symptom_group] ?? "triangle-alert"} />
            </span>
            <div>
              <span className="sm">
                설비 {a.equipment_id} · {a.equipment_type} · {hhmm(a.occurred_at)} 발생
              </span>
              <h3>{a.group_name}</h3>
              <div className="tags">
                <span className="ch blue">증상군 · {a.system}</span>
                {a.out_of_range_count > 0 ? <span className="ch red">센서 {a.out_of_range_count}개 이탈</span> : null}
              </div>
            </div>
          </div>
          <div className="sub">{a.trend_title}</div>
          <Trend a={a} />
          <table className="tbl">
            <tbody>
              <tr>
                <th>센서</th>
                <th>현재</th>
                <th>평소 범위</th>
                <th>상태</th>
              </tr>
              {a.sensors.map((r) => (
                <tr key={r.key} className={r.out_of_range ? "down" : ""}>
                  <td>{r.name}</td>
                  <td>
                    <b>{r.value_text}</b>
                  </td>
                  <td>{r.range_text}</td>
                  <td>
                    <span className={`ch ${r.out_of_range ? "red" : "gray"}`}>{r.status}</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div>
          <div className="cd ai-c">
            <div className="cd-h">
              <Icon name="sparkles" />
              <b>AI 해석</b>
              {a.ai_reading.fallback ? <span className="ch fb">{a.ai_reading.label}</span> : null}
            </div>
            <p className="ai">{a.ai_reading.text}</p>
            <div className="ev">
              <Icon name="search" />
              <span>
                비슷한 과거 기록 <b>{a.similar_count}건</b>을 찾았습니다
              </span>
            </div>
          </div>
          <div className="cta">
            <span className={past ? "btn lg dis" : "btn lg"} role="button" tabIndex={0} onClick={past ? undefined : onNext}>
              진단 보기 <Icon name="arrow-right" />
            </span>
            <span className="note">알람 확인 시각이 기록됩니다</span>
          </div>
        </div>
      </div>
    </div>
  );
}
