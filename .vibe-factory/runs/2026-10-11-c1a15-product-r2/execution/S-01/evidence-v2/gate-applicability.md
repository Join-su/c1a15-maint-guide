# S-01 자동 gate 적용 범위 (v2 — G6-S01 지적 반영)

plan의 자동 gate 12개는 모든 slice에 같은 이름으로 기록한다. S-01(P-01 · P-02)에는 업무 화면 · 업무 API · LLM 호출이 아직 없다. 그래서 아래 네 gate는 "이 slice에 있는 대상"만 확인했고, 그 범위를 여기 밝힌다(통과로 부풀리지 않음). 결과 'pass'는 이 표의 확인 범위에 대한 판정이다.

| Gate | S-01에서 실제로 확인한 것 | 증거 | 본래 대상이 생기는 곳 |
| --- | --- | --- | --- |
| api_negative_authority | 업무 API가 없다. 권한 경계의 전제 두 가지를 음성으로 확인: 클라이언트가 위조한 X-App이 nginx에서 앱별 값으로 덮어써짐(8081 → tech, 8082 → lead), API 포트(8000)가 밖에서 접속되지 않음 | evidence-v2/verify-e2e.txt | P-06(S-02): 앱 × 역할 · 다른 앱 쿠키 · 토큰 없음 · 잠금 전 · 지시 밖 거부 |
| e2e_surface_journey | 화면 journey가 없다. 두 앱 첫 문서 · 깊은 경로 새로고침이 각 앱 문서로 돌아오는 것만 확인(실행 구성) | evidence-v2/verify-e2e.txt | P-08 이후(Playwright, 새 판 승인 뒤) |
| prototype_structure_checklist | 그리는 Region이 없다(P-01 · P-02의 prototype_refs는 값을 공급하는 영역). 적재 값이 그 영역의 원천인지(매뉴얼 43절 · 이력 300건 · 등급표 36행)만 확인 | evidence-v2/verify-db.txt | P-08 · P-10 · P-12 · P-15 · P-17 |
| external_call_zero_in_fixture | LLM 호출 경로가 아직 없다. 실제로 확인한 것: ① 정적 — 제품 코드(server/src · apps · packages)에 외부 HTTP 클라이언트 · 외부 주소가 없고, Python 실행 의존성 · npm lock에 LLM SDK가 없음(scripts/external_call_check.py, 결함 주입 시 exit 1 확인) ② 실행 — fixture compose의 api 컨테이너에 외부 키 환경 변수가 없고 APP_MODE=fixture(verify-e2e). 범위 밖: image build의 `pip install uv` · `uv sync`는 제품 실행 중 호출이 아니라 사용자 승인을 받은 패키지 설치(execution/S-01/separate-approvals.md)이며, 이번 실행은 build 단계가 캐시를 썼다. 실행 중 외부 요청을 세는 관찰은 LLM Adapter(P-05)와 시연 E2E(P-17)에서 | evidence-v2/check-fast.txt · evidence-v2/external-call-check-negative.txt · evidence-v2/verify-e2e.txt | P-05(S-02) · P-17 |
