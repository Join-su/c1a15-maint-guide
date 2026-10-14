# S-02 2차 cycle 별도 승인 (2026-10-13)

| 대상 | 사용자 답 | 범위(질문에 함께 보인 문장) |
| --- | --- | --- |
| npm 패키지 설치 | "네 묶음 모두 허용 (권장)" | ① openapi-fetch 0.17.0(앱 API 클라이언트, 실행 의존) ② openapi-typescript 7.13.0 + typescript 5.x(OpenAPI → 타입 생성, 별도 도구 workspace tools/api-types에만 — 저장소 TS 7과 충돌을 피함) ③ @playwright/test 1.63.0(E2E, 로컬 chromium 1243 사용 · 브라우저 내려받기 없음) ④ vitest 5.0.4 · @testing-library/react 16.3.3 · @testing-library/dom 10.x · @testing-library/user-event 14.6.7 · jsdom 30.1.2(화면 component 시험). 모두 저장소 안 npm workspaces에만 설치하고 package-lock.json에 고정. 시험 컨테이너 실행은 S-01 승인 범위 그대로 |
| 시험 컨테이너 · uv | S-01 승인 범위 그대로 | execution/S-01/separate-approvals.md |
