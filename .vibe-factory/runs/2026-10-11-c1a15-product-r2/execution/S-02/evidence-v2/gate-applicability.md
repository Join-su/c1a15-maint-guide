# S-02 자동 gate 적용 범위 (v2 — G6-S02 지적 반영)

plan의 자동 gate 12개를 모든 slice에 같은 이름으로 기록한다. S-02(P-03 ~ P-07)에는 화면이 없다(실행 해석 ①: 화면 gate · 첫 end-to-end L3 journey는 새 판). 아래 표는 각 gate가 이 slice에서 실제로 확인한 범위다. 결과 'pass'는 이 범위에 대한 판정이며 부풀리지 않는다.

| Gate | S-02에서 실제로 확인한 것 | 증거 | 본래 대상이 생기는 곳 |
| --- | --- | --- | --- |
| scope_traceability | 바뀐 파일 전부가 P-03 ~ P-07 중 하나에 묶임(ledger changed_files). 실행 카드 허용 목록 밖 파일(docker-compose.yml · .env.example · server/openapi.json · pyproject · uv.lock)은 ledger scope_notes에 이유와 함께 적음. 별도 승인 2건 · 사용자 결정 2건(OOS-01 · LangGraph) 기록 | implementation-contract.md · separate-approvals.md · oos01-decision.md · langgraph-decision.md | — |
| ac_verifier | item verifier 문장을 하나씩 시험으로 대응(P-03 R5 예시 · property · 등급 표 · 음성 · OOS-01 계산표, P-04 고정 질의 · 누수 음성 · 승인 뒤 메모리 색인 재검색 후보 포함 · 평가 모드 제외 — 승인 보고서 DB 저장 · 색인 갱신 통합 경로는 P-13, P-05 API 미리보기 근거 검사 · 원문 대체 · 메모 해석 오류 계속 · 3회 인계 권함 · fixture 전체 외부 호출 0, P-06 API 음성(ADV-07 도우미의 정상 통과 · 결함 실패) · 중복 1건 · 재시작 재개 · OpenAPI diff, P-07 CLI 시각 · 센서 값 · 배정 · 미배정 → 다음 로그인 · 각본 재생성 diff 없음) | check-fast.txt · verify-db.txt · verify-e2e.txt · unit/db-test-list.txt | — |
| static_check | ruff format · lint, OpenAPI 재생성 diff(결함 주입 시 exit 1) | check-fast.txt · openapi-negative.txt | — |
| typecheck | 두 앱 · packages/ui tsc(S-02는 앱 코드를 바꾸지 않음). Python은 타입 검사기를 쓰지 않는다(plan 선택에 없음) | check-fast.txt | P-08 |
| unit_and_property | 판정 규칙 · 검색 · LLM Adapter · 발생기 단위 시험, hypothesis property 2개(합 100 · 재정규화) | check-fast.txt · unit-test-list.txt | — |
| api_negative_authority | TestClient(verify-db): 앱 × 역할 · 위조 X-App · 다른 앱 쿠키 · 쿠키 없음 · 만료 · 로그아웃 · 잠금 전 · 지시 밖 · B 체크 전 · 승인 없는 C 호출 단계 · 지시되지 않은 절 원문 · 서버 전용 필드 · 필수 필드 없음 · 내부 토큰 없음 · X-App 붙은 내부 등록. 실제 nginx(verify-e2e): 위조 X-App 덮어쓰기 · 파트장 세션의 정비자 쿠키 · 다른 앱 쿠키 · 쿠키 없음 · 위조 세션 쓰기 · 로그아웃 뒤 · 토큰 붙인 내부 등록(8081 · 8082) 거부. 만료 세션은 TestClient로만 | verify-db.txt · verify-e2e.txt | 파트장 API는 P-12 · P-13 |
| integration_real_postgres | 시험 DB(pgvector)에서 migration 왕복 · alembic drift 0 · 적재 · pgvector 순위 = 메모리 순위 · PostgresSaver 재개 · API 통합 · 발생기 → DB | verify-db.txt · db-test-list.txt | — |
| e2e_surface_journey | 화면 journey가 없다. compose 실행 구성만 확인: 발생기(api 컨테이너 안) → 8081 정비자 홈 API 5초, api 컨테이너 재시작 뒤 같은 단계 재개(L3 일부), 두 앱 첫 문서 · 깊은 경로 | verify-e2e.txt | P-08 이후 Playwright |
| prototype_structure_checklist | 그리는 Region이 없다. P-07 prototype_refs(T02 R-ALARMS · R-TOP)에 공급하는 값만 확인: 홈 API의 새 알람 행(설비 · 증상 · 시각 · 상태 new) · 변경 순번 · 추이 제목 | verify-db.txt(test_alarm_generator_cli_registers_scenarios) | P-08 |
| secret_scan | 저장소 비밀값 0건. 시험 비밀값은 실행마다 무작위 · 환경 변수, 증거 파일에 비밀번호 · 토큰 문자열 없음 | check-fast.txt | — |
| external_call_zero_in_fixture | ① 정적: 제품 코드 외부 HTTP 클라이언트 · 외부 주소 0, 예외는 live.py의 openai(호출 안 함) · alarms/__main__.py의 로컬 urllib(주소 제한 시험, 모듈 이름 정확 비교), 허용 밖 파일에 넣거나 허용 파일에 urllib3를 넣으면 exit 1 ② 실행: fixture API 전체 흐름에서 Python 소켓 연결 0(DB libpq 연결은 셈 밖, UF-13), 컨테이너 외부 키 없음 · APP_MODE=fixture, 발생기가 외부 주소를 거부. 범위 밖: image build의 uv sync(승인된 설치) | check-fast.txt · external-call-check-negative.txt · verify-db.txt · verify-e2e.txt | P-17 시연 E2E |
| leakage_check | 제품 코드의 eval · generation 참조 0, 각본 ∩ 이력 · 평가 카드 = 0(scripts만 행 번호 읽기, 사용자 결정), 검색 원인 필터 음성(ADV-04), 각본 재생성 diff 없음 | check-fast.txt · demo-separation.txt · scenario-regenerate.txt | P-16 평가 실행 |
