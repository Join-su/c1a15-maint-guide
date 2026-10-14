# S-01 자동 gate 적용 범위

plan의 자동 gate 12개는 모든 slice에 같은 이름으로 기록한다. S-01(P-01 · P-02)에 업무 화면 · 업무 API가 아직 없으므로 아래 세 gate는 "이 slice에 있는 대상"만 확인했고, 그 범위를 여기 밝힌다(통과로 부풀리지 않음).

| Gate | S-01에서 실제로 확인한 것 | 증거 | 본래 대상이 생기는 곳 |
| --- | --- | --- | --- |
| api_negative_authority | 업무 API가 없다. 대신 권한 경계의 전제 두 가지를 음성으로 확인: 클라이언트가 위조한 X-App이 nginx에서 앱별 값으로 덮어써짐(8081 → tech, 8082 → lead), API 포트(8000)가 밖에서 접속되지 않음 | verify-e2e.txt | P-06(S-02): 앱 × 역할 · 다른 앱 쿠키 · 토큰 없음 · 잠금 전 · 지시 밖 거부 |
| e2e_surface_journey | 화면 journey가 없다. 두 앱 첫 문서 · 깊은 경로 새로고침이 각 앱 문서로 돌아오는 것만 확인(실행 구성) | verify-e2e.txt | P-08 이후(Playwright, 새 판 승인 뒤) |
| prototype_structure_checklist | 그리는 Region이 없다(P-01 · P-02의 prototype_refs는 값을 공급하는 영역). 적재 값이 그 영역의 원천인지(매뉴얼 43절 · 이력 300건 · 등급표 36행)만 확인 | verify-db.txt | P-08 · P-10 · P-12 · P-15 · P-17 |
