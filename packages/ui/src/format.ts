// 표시 형식만(값은 서버). 기기 시간대와 상관없이 현장 시각(KST)으로 보인다.

const TZ = "Asia/Seoul";

function parts(iso: string | Date) {
  const d = typeof iso === "string" ? new Date(iso) : iso;
  const f = new Intl.DateTimeFormat("en-CA", {
    timeZone: TZ,
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    hourCycle: "h23",
  });
  const p = Object.fromEntries(f.formatToParts(d).map((x) => [x.type, x.value]));
  return p as Record<"year" | "month" | "day" | "hour" | "minute", string>;
}

/** "02:14" */
export function hhmm(iso: string | Date): string {
  const p = parts(iso);
  return `${p.hour}:${p.minute}`;
}

/** "2026-09-30 22:05" */
export function dateTime(iso: string): string {
  const p = parts(iso);
  return `${p.year}-${p.month}-${p.day} ${p.hour}:${p.minute}`;
}

/** 숫자 천 단위 쉼표(서버가 준 값의 표시만). */
export function num(v: number, digits = 0): string {
  return v.toLocaleString("en-US", { minimumFractionDigits: digits, maximumFractionDigits: digits });
}

const WEEKDAY = ["일", "월", "화", "수", "목", "금", "토"];

/** "2026-10-01 (목) 08:12"(파트장 앱 머리 시각) */
export function dateDay(iso: string): string {
  const p = parts(iso);
  const wd = new Date(`${p.year}-${p.month}-${p.day}T12:00:00+09:00`).getUTCDay(); // 현장 날짜의 정오
  return `${p.year}-${p.month}-${p.day} (${WEEKDAY[wd]}) ${p.hour}:${p.minute}`;
}
