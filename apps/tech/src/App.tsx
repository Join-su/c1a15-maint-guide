// 정비자 앱(P-08): 로그인 → 홈(5초 주기 조회) · 종 목록 → 진단 세션(3초). 상단 '홈'은 확인 없이 홈으로(세션 · 입력은 그대로).
// D-528: 모든 화면 왼쪽에 「오늘 밤 알람」 칸(264px), 본문은 그 오른쪽(1280 − 264px).
// 화면은 API 값만 보인다. 주소(/session/{id})를 기억해 새로고침 · 다시 열기에도 같은 자리로 온다.

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import {
  createApi,
  hhmm,
  RecordModal,
  TopBar,
  useFreshScreenGuard,
  type HistoryRecord,
  type Home as HomeData,
  type Notifications,
  type SessionWithPreview,
} from "@c1a15/ui";
import { device, type Me } from "./device";
import { PackNotice, trackPack, type PackState } from "./PackNotice";
import { chime, unlockSound, useClock, usePoll } from "./hooks";
import { HomeScreen, NotifyPanel } from "./screens/Home";
import { ManualModal, type ManualView } from "./screens/Instruction";
import { Login } from "./screens/Login";
import { FinalScreen } from "./screens/Final";
import { Session } from "./screens/Session";
import { TodayPanel } from "./screens/Today";

type View = { name: "home" } | { name: "session"; sid: number } | { name: "final"; rid: number };

function viewFromPath(): View {
  const m = /^\/session\/(\d+)/.exec(window.location.pathname);
  if (m) return { name: "session", sid: Number(m[1]) };
  const f = /^\/report\/(\d+)/.exec(window.location.pathname); // D-528 보고서 최종본
  return f ? { name: "final", rid: Number(f[1]) } : { name: "home" };
}

export function App() {
  const api = useMemo(() => createApi(), []);
  const clock = useClock();
  const [me, setMeState] = useState<Me | null>(() => device.me());
  const [view, setView] = useState<View>(viewFromPath);
  useFreshScreenGuard(view.name === "home" ? "home" : view.name === "final" ? `final:${view.rid}` : `session:${view.sid}`); // EV-007: 홈 → 세션 바뀐 직후 누름 무시
  const [home, setHome] = useState<HomeData | null>(null);
  const [notes, setNotes] = useState<Notifications | null>(null);
  const [panel, setPanel] = useState(false);
  const [record, setRecord] = useState<HistoryRecord | null>(null);
  const [manual, setManual] = useState<ManualView | null>(null);
  const [session, setSession] = useState<SessionWithPreview | null>(null);
  const [opened, setOpened] = useState<SessionWithPreview | null>(null);
  const lastNew = useRef<number | null>(null);

  const setMe = (m: Me | null) => {
    setMeState(m);
    device.setMe(m);
  };
  const expired = useCallback(() => setMe(null), []);

  const go = (v: View) => {
    setView(v);
    setPanel(false);
    const path = v.name === "session" ? `/session/${v.sid}` : v.name === "final" ? `/report/${v.rid}` : "/";
    if (window.location.pathname !== path) window.history.pushState(null, "", path);
  };
  useEffect(() => {
    const onPop = () => setView(viewFromPath());
    window.addEventListener("popstate", onPop);
    return () => window.removeEventListener("popstate", onPop);
  }, []);

  const refresh = async () => {
    if (!me) return;
    const [h, n] = await Promise.all([api.GET("/api/tech/home"), api.GET("/api/tech/notifications")]);
    if (h.response.status === 401 || n.response.status === 401) return expired();
    if (h.data) setHome(h.data);
    if (n.data) {
      setNotes(n.data);
      const count = n.data.items.filter((i) => i.kind === "new_alarm").length;
      if (lastNew.current !== null && count > lastNew.current) chime();
      lastNew.current = count;
    }
  };
  usePoll(refresh, 5000, [me?.user_id]);
  // D-528: 왼쪽 「오늘 밤 알람」 · 위 띠가 세션 단계와 어긋나지 않게 — 잠금 · 단계 · 보고서 상태가 바뀌면 홈을 바로 다시 읽는다(5초 주기를 기다리지 않음)
  useEffect(() => {
    if (session) void refresh();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [session?.session_id, session?.locked, session?.step?.kind, session?.instruction?.check_no, session?.report?.status]); // 점검 번호(답장 001-zzt 3)

  const [pack, setPack] = useState<PackState>(null); // CH-17: 점검 시작(첫 Run)이 늦거나 실패할 때
  const [packAlarm, setPackAlarm] = useState<number | null>(null);
  const starting = useRef(false); // EV-007: '점검 시작'을 여러 번 눌러도 세션 시작 요청은 한 번(응답 뒤 풀림)
  const startAlarm = async (alarmId: number) => {
    if (starting.current) return;
    starting.current = true;
    const { data, response } = await trackPack(
      () => api.POST("/api/tech/alarms/{alarm_id}/session", { params: { path: { alarm_id: alarmId } } }),
      setPack,
    ).finally(() => {
      starting.current = false;
    });
    setPackAlarm(response.status === 503 ? alarmId : null);
    if (response.status === 401) return expired();
    if (data) {
      setOpened(data);
      go({ name: "session", sid: data.session_id });
      void refresh(); // 새 알람 → 진행 중: 종 숫자 · 홈 행을 바로 다시 읽는다
    }
  };
  const openRecord = async (id: string) => {
    const { data } = await api.GET("/api/records/{record_id}", { params: { path: { record_id: id } } });
    if (data) setRecord(data);
  };
  const openManual = async (sid: number, section: string) => {
    const { data } = await api.GET("/api/tech/sessions/{sid}/manual/{section}", {
      params: { path: { sid, section } },
    });
    if (data) setManual(data as unknown as ManualView); // 매뉴얼 원문 응답(P-06)은 OpenAPI에서 객체로만 선언됨
  };

  if (!me) {
    return (
      <div className="ap">
        <Login
          api={api}
          onDone={(m) => {
            setMe(m);
            go({ name: "home" });
          }}
        />
      </div>
    );
  }

  const bell = notes ? notes.items.filter((i) => i.kind === "new_alarm").length : 0;
  const inProgress = home?.alarms.find((a) => a.status === "in_progress");
  const ctxAlarm =
    view.name === "session" && session?.session_id === view.sid
      ? session.alarm
      : inProgress
        ? { equipment_id: inProgress.equipment_id, group_name: inProgress.group_name, occurred_at: inProgress.occurred_at }
        : null;
  const context = ctxAlarm ? `${ctxAlarm.equipment_id} · ${ctxAlarm.group_name} · ${hhmm(ctxAlarm.occurred_at)}` : null;

  return (
    <div className="ap" onPointerDown={unlockSound}>
      <TopBar
        context={context}
        clock={clock}
        homeOn={view.name === "home"}
        bell={bell}
        user={{ name: me.display_name, role: `${home?.shift.label ?? ""} 정비`.trim() }}
        onHome={() => go({ name: "home" })}
        onBell={() => {
          if (view.name !== "home") go({ name: "home" });
          setPanel((x) => !x);
        }}
      />
      <TodayPanel
        home={home}
        current={view.name === "session" ? view.sid : null}
        onOpen={(a) =>
          a.status === "new" ? void startAlarm(a.alarm_id) : a.session_id ? go({ name: "session", sid: a.session_id }) : undefined
        }
      />
      <div className="ap-main">
        {view.name === "home" ? <PackNotice state={pack} onRetry={() => packAlarm !== null && void startAlarm(packAlarm)} /> : null}
        {view.name === "home" ? (
          home ? (
            <HomeScreen
              home={home}
              onResume={(sid) => go({ name: "session", sid })}
              onFinal={(rid) => go({ name: "final", rid })}
              onOpen={(a) => {
                const sid = a.session_id ?? a.report_session_id; // 완료 행 '보기' = 확정한 보고서
                if (a.status === "new") void startAlarm(a.alarm_id);
                else if (sid) go({ name: "session", sid });
              }}
            />
          ) : null
        ) : view.name === "final" ? (
          <FinalScreen api={api} rid={view.rid} onReport={(sid) => go({ name: "session", sid })} />
        ) : (
          <Session
            key={view.sid}
            api={api}
            sid={view.sid}
            initial={opened?.session_id === view.sid ? opened : null}
            onSession={setSession}
            onExpired={expired}
            onRecord={(id) => void openRecord(id)}
            onManual={(section) => void openManual(view.sid, section)}
            onHome={() => go({ name: "home" })}
            onFinal={(rid) => go({ name: "final", rid })}
          />
        )}
      </div>
      {panel && notes ? (
        <>
          <div className="catch" onClick={() => setPanel(false)} />
          <NotifyPanel
            data={notes}
            onItem={(i) =>
              i.kind === "new_alarm" ? void startAlarm(i.alarm_id) : i.session_id ? go({ name: "session", sid: i.session_id }) : undefined
            }
          />
        </>
      ) : null}
      {record ? <RecordModal record={record} onClose={() => setRecord(null)} /> : null}
      {manual ? <ManualModal m={manual} onClose={() => setManual(null)} /> : null}
    </div>
  );
}
