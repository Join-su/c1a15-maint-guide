# Slice Execution Card S-02 (2차 cycle)

| Field | Record |
| --- | --- |
| Slice execution packet path / SHA-256 | `execution/S-02/cycle-2/slice-execution-packet.json` / `d8aa752ddc2766013e2cd90e6deb7ea198f62e159c1e17bee6efaf426e337a41` |
| Plan version / authorized item IDs / batch | plan v6 / P-08 · P-18(PBC-4 v6 authorization P-08 ~ P-18) / per_slice_gated — S-02 2차 cycle(1차 P-03 ~ P-07 완료) |
| Baseline revalidation result | pass — HEAD · lockfile · data · OpenAPI · Playbook hash가 기준선 v3와 같음(`execution/S-02/cycle-2/baseline-revalidation.json`) |
| AC and expected slice outcome | 연결 AC 22개(AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-12, AC-13, AC-14, AC-17, AC-19, AC-20, AC-29, AC-31, AC-35, AC-37, AC-38, AC-39, AC-40, AC-42, AC-43, AC-44). 완료 판정(matrix completion item = P-08 · P-18): AC-01 · AC-04 · AC-05 · AC-13 · AC-14 · AC-31 · AC-35 · AC-37 · AC-38 · AC-39 · AC-40. 그 밖 11개는 부분 증거 후 deferred(AC-02→P-16, AC-03→P-10, AC-06→P-11, AC-12→P-12, AC-17→P-17, AC-19→P-10, AC-20→P-10, AC-29→P-12, AC-42→P-13, AC-43→P-10, AC-44→P-15). 결과: 정비자 앱 로그인 → 홈 · 종 → 알람 → 진단(첫 판정 호출이면 T04 / first_call) → 잠금 → 점검 지시 · 결과 입력 · 확인 질문 · 과거 기록 · 매뉴얼 원문, 첫 end-to-end L3(4.3 확인 불가 → 4.5 지시, 새로고침 · API 재시작 뒤 같은 단계), 진단 미리보기 호출 값(P-18) |
| Allowed changes / prohibited actions | 허용: apps/tech · packages/ui · e2e/(Playwright) · server/src/c1a15/api(미리보기 · 결과 입력 검증 — 실행 해석 ②) · server/tests · server/openapi.json · scripts/(검사 보강 S02-G6-2) · package.json · package-lock.json(승인 패키지). 금지: authorization prohibited_actions 전부 · S-03 이후 item(T08 ~ T11 화면 · 조치 · 보고서 · 호출 요약 API) · commit · push |
| Commands and AC verifier | `scripts/check-fast`(typecheck · component · unit) · `scripts/verify-db`(API 통합) · `scripts/verify-e2e`(compose + Playwright tech journey) · OpenAPI 재생성 diff 0 · Prototype 구조 대조 체크리스트 |
| Required automatic quality gates | 12개 전부(e2e_surface_journey · prototype_structure_checklist가 이 cycle에서 처음 실제 대상을 가짐) |
| Review requirement and rationale | `independent_critic` — P-18이 공개 API 계약(public_contract) |
| Loop cap / stop or escalation condition | 같은 verifier 3회. 중단 5종 + Prototype 구조와 다르면 out-of-scope로 멈춤, T04 / first_call 예외가 다른 상태로 번지면 멈춤. 별도 승인(npm 패키지 · 시험 컨테이너는 S-01 범위) 전 설치 안 함 |
| Rollback or recovery | 새 파일은 삭제, 수정한 기존 파일(apps/tech/src/main.tsx · packages/ui/src/index.ts · api/sessions.py · api/schemas.py · openapi.json · package*.json · scripts/*)은 ledger에 수정 내용을 적어 되돌림(commit 전이라 git 복원 불가), npm 패키지는 npm uninstall |
