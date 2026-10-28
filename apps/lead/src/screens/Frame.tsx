// 파트장 앱 틀(R-NAV): 왼쪽 고정 메뉴 5개(사람 판단 — EV-009) + 아래 사용자, 본문 머리(제목 · 시각). 메뉴 이동은 본문만 바꾼다.

import type { ReactNode } from "react";
import { dateDay, Icon } from "@c1a15/ui";

export type Menu = "approvals" | "calls" | "judge" | "grades" | "audit";

const MENUS: { id: Menu; label: string; icon: string }[] = [
  { id: "approvals", label: "승인 대기", icon: "file-check-2" },
  { id: "calls", label: "호출", icon: "phone-call" },
  { id: "judge", label: "사람 판단", icon: "circle-help" }, // EV-009(D-444 #18)
  { id: "grades", label: "권한 등급", icon: "settings" },
  { id: "audit", label: "감사 기록", icon: "history" },
];

export function Frame({
  menu,
  me,
  title,
  now,
  onMenu,
  children,
}: {
  menu: Menu;
  me: { display_name: string };
  title: string;
  now: string | null;
  onMenu: (m: Menu) => void;
  children: ReactNode;
}) {
  return (
    <div className="wb">
      <div className="wb-side">
        <div className="brand">
          <Icon name="map" className="logo2" />
          정비 길잡이
        </div>
        {MENUS.map((m) => (
          <span key={m.id} className={`wn ${menu === m.id ? "on" : ""}`} role="button" tabIndex={0} onClick={() => onMenu(m.id)}>
            <Icon name={m.icon} />
            {m.label}
          </span>
        ))}
        <div className="wb-me">
          <span className="av">{me.display_name.slice(0, 1)}</span>
          {me.display_name} · 정비 파트장
        </div>
      </div>
      <div className="wb-main">
        <div className="wb-top">
          <h2>{title}</h2>
          <span className="sm">{now ? dateDay(now) : ""}</span>
        </div>
        {children}
      </div>
    </div>
  );
}

/** 하나만 고르는 결정 선택지(L03 · L04 .dopt). */
export function Options<T extends string>({
  options,
  value,
  onChange,
}: {
  options: { value: T; label: string; hint: string }[];
  value: T | null;
  onChange: (v: T) => void;
}) {
  return (
    <>
      {options.map((o) => (
        <div
          key={o.value}
          className={`dopt ${value === o.value ? "sel" : ""}`}
          role="radio"
          aria-checked={value === o.value}
          tabIndex={0}
          onClick={() => onChange(o.value)}
        >
          <span className="rd" />
          <div>
            <b>{o.label}</b>
            <span>{o.hint}</span>
          </div>
        </div>
      ))}
    </>
  );
}

export function Btn({ label, cls = "lg full", off, onClick }: { label: string; cls?: string; off?: boolean; onClick: () => void }) {
  return (
    <span className={`btn ${cls}${off ? " dis" : ""}`} role="button" tabIndex={0} aria-disabled={off} onClick={() => !off && onClick()}>
      {label}
    </span>
  );
}
