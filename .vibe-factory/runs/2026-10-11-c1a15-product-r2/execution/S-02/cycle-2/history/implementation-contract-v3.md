# Slice Execution Card S-02 (2차 cycle, v3)

| Field | Record |
| --- | --- |
| Slice execution packet path / SHA-256 | `execution/S-02/cycle-2/slice-execution-packet.json` / `4b9dc0ebedc5f03d7b9ee7fcbbee8c94c81cb59a9db70dff6145cc86fb9beeb8` |
| Plan version / authorized item IDs / batch | plan v7 / P-08 · P-18 · P-19(PBC-4 v8 authorization P-08 ~ P-19) / per_slice_gated — S-02 2차 cycle(1차 P-03 ~ P-07 완료, P-18 구현됨) |
| Baseline revalidation result | pass — HEAD · uv.lock · data · OpenAPI · Playbook hash가 기준선 v3와 같음, package-lock.json은 승인 설치로 바뀜(explained_differences, `execution/S-02/cycle-2/baseline-revalidation.json`) |
| AC and expected slice outcome | 연결 AC 22개(AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-12, AC-13, AC-14, AC-17, AC-19, AC-20, AC-29, AC-31, AC-35, AC-37, AC-38, AC-39, AC-40, AC-42, AC-43, AC-44). 결과: P-19 화면 값 API(홈 교대 · 진행 n / m · alarm 블록 · 기록 카드 · 잠금 절차 · 지시 n / m · 근거 · 승인자, data normal_ranges) → 정비자 앱 로그인 → 홈 · 종 → 알람 → 진단(첫 판정 호출이면 T04 / first_call) → 잠금 → 점검 지시 · 결과 입력 · 확인 질문 · 과거 기록 · 매뉴얼 원문, 첫 end-to-end L3(4.3 확인 불가 → 4.5 지시, 새로고침 · API 재시작 뒤 같은 단계) |
| Allowed changes / prohibited actions | 허용: apps/tech · packages/ui · e2e/(Playwright) · tools/api-types · server/src/c1a15/api · engine · llm(P-19 화면 값 · AI 해석, P-18 미리보기 · 결과 입력 검증) · server/tests · server/openapi.json · scripts/build_data.py → data/alarm_rules.json · data/manifest.json(normal_ranges만) · scripts/(검사 보강) · package.json · package-lock.json(승인 패키지). 금지: authorization prohibited_actions 전부 · S-03 이후 item(T08 ~ T11 화면 · 조치 · 보고서 · 호출 요약 API) · 앱이 화면 값을 직접 만들기 · commit · push |
| Commands and AC verifier | `scripts/check-fast`(typecheck · component · unit) · `scripts/verify-db`(API 통합, P-18 · P-19 L2) · `scripts/verify-e2e`(compose + Playwright tech journey) · data 재생성 diff(normal_ranges · manifest hash만) · OpenAPI 재생성 diff 0 · Prototype 구조 대조 체크리스트 |
| Required automatic quality gates | 12개 전부(e2e_surface_journey · prototype_structure_checklist가 이 cycle에서 처음 실제 대상을 가짐) |
| Review requirement and rationale | `independent_critic` — P-18 · P-19가 공개 API 계약(public_contract) |
| Loop cap / stop or escalation condition | 같은 verifier 3회. 중단 5종 + Prototype 구조와 다르면 out-of-scope로 멈춤, T04 / first_call 예외가 다른 상태로 번지면 멈춤, 화면 값이 API에 없으면 멈춤(이번 같은 L1). 새 패키지 설치 · 시험 컨테이너 범위 밖 실행 전 멈춤 |
| Rollback or recovery | 새 파일은 삭제, 수정한 기존 파일은 ledger에 수정 내용을 적어 되돌림(commit 전이라 git 복원 불가), data는 scripts/build_data.py를 normal_ranges 없이 다시 실행, npm 패키지는 npm uninstall |
