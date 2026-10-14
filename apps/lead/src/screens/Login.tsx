// L01 파트장 로그인(AC-12): 파트장 계정만. 역할이 다르면 서버가 403 role_mismatch.

import { useState } from "react";
import { errorDetail, Icon, type Api } from "@c1a15/ui";
import type { Me } from "../device";

export function Login({ api, onDone }: { api: Api; onDone: (me: Me) => void }) {
  const [userId, setUserId] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<"role" | "bad" | null>(null);
  const [busy, setBusy] = useState(false);
  const ready = !busy && !!userId && !!password;

  const submit = async () => {
    if (!ready) return;
    setBusy(true);
    const { data, error: err, response } = await api.POST("/api/login", { body: { user_id: userId, password } });
    setBusy(false);
    if (data) {
      const d = data as { user_id: string; display_name: string };
      onDone({ user_id: d.user_id, display_name: d.display_name });
      return;
    }
    setError(response.status === 403 && errorDetail(err) === "role_mismatch" ? "role" : "bad");
  };

  return (
    <div className="wb" style={{ justifyContent: "center", alignItems: "center" }}>
      <div className="lg-card">
        <div className="brand">
          <Icon name="map" className="logo2" />
          정비 길잡이 · 파트장
        </div>
        <h3>파트장 로그인</h3>
        {error ? (
          <div className="banner bad" role="alert">
            <Icon name="circle-alert" />
            <div>
              {error === "role" ? (
                <>
                  <b>파트장 계정만 로그인할 수 있습니다</b>정비자 계정은 정비자 앱(태블릿)에서 로그인하십시오.
                </>
              ) : (
                <>
                  <b>ID 또는 비밀번호가 맞지 않습니다</b>사전 등록된 파트장 계정으로 다시 로그인하십시오.
                </>
              )}
            </div>
          </div>
        ) : null}
        <div className="fld">
          ID
          <input
            aria-label="ID"
            className={`inp${error === "role" ? " err" : ""}`}
            autoComplete="username"
            value={userId}
            onChange={(e) => setUserId(e.target.value)}
          />
        </div>
        <div className="fld">
          비밀번호
          <input
            aria-label="비밀번호"
            className="inp"
            type="password"
            autoComplete="current-password"
            value={password}
            onKeyDown={(e) => e.key === "Enter" && void submit()}
            onChange={(e) => setPassword(e.target.value)}
          />
        </div>
        <span className={`btn lg full${ready ? "" : " dis"}`} role="button" tabIndex={0} onClick={() => void submit()}>
          로그인
        </span>
        <span className="note">사전 등록된 파트장 계정으로만 로그인합니다.</span>
      </div>
    </div>
  );
}
