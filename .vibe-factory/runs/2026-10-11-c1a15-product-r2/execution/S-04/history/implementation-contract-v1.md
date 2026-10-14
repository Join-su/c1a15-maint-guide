# Slice Execution Card S-04

| Field | Record |
| --- | --- |
| Slice execution packet path / SHA-256 | `execution/S-04/slice-execution-packet.json` / `98def5865bf715001639649bcfe7c9cc2413201208679e3782964d62a771d846` |
| Plan version / authorized item IDs / batch | plan v10 / P-11 · P-12 · P-13(PBC-4 v11 authorization P-08 ~ P-19) / per_slice_gated |
| Baseline revalidation result | pass — HEAD · Playbook은 기준선 v3와 같고, lockfile · data · OpenAPI hash는 S-03 예상 변경 표 값과 같음(`execution/S-04/baseline-revalidation.json`) |
| AC and expected slice outcome | 연결 AC 15개(AC-06, AC-08, AC-09, AC-10, AC-11, AC-12, AC-17, AC-23, AC-24, AC-25, AC-26, AC-27, AC-29, AC-37, AC-42). 결과: 파트장 로그인 · 승인 대기 목록(요약 타일 · 행 · 빈 목록) · 검토(그대로 승인 · 수정 후 승인 R8 · 반려 사유 필수) · 승인 시 이력 변환 · 두 색인 갱신(평가 모드 제외) · 호출 답(파트장 호출 3종 · D는 승인 없음 · 숙련자 인계 2종 · 처리 메모) · 등급 변경(모든 변경 경고 · 다음 판정부터 · 열린 화면 그대로 · 기록) · 감사 조회 · 필터, 두 앱 교차 E2E 4개 + 종 목록 4종류, 정비자 반려 화면(결정 017 ①) |
| Allowed changes / prohibited actions | 허용: server/src/c1a15/{api, engine, retrieval, llm, db, loader} · server/migrations · server/tests · server/openapi.json · packages/ui · apps/lead · apps/tech(반려 화면 · 종 반려 묶음만, 결정 017 ①) · e2e · scripts(검사 보강). 금지: authorization prohibited_actions 전부 · 정정 API · 지난 화면(P-14 · P-15, S-05) · 평가 실행기(P-16) · 앱이 화면 값을 직접 만들기 · Prototype 원본 읽기(부록만) · commit · push |
| Commands and AC verifier | `scripts/check-fast` · `scripts/verify-db` · `scripts/verify-e2e`(Playwright lead journey · 두 browser context 교차 E2E) · OpenAPI 재생성 diff 0 · 구조 대조(부록 기준, L01 ~ L06 · T02 / rejected · T12) · 증거 폴더 비밀값 검사 |
| Required automatic quality gates | 12개 전부 |
| Review requirement and rationale | `independent_critic` — P-11이 권한(파트장 역할 · 승인 · 반려 · 등급 변경) · 감사 · 공개 API · 색인(지식 schema 쓰기)을 다룬다 |
| Loop cap / stop or escalation condition | 같은 verifier 3회. 중단 5종 + 권한 · 누수 음성 시험 실패 시 멈춤, 화면 값이 API에 없거나 계산 정의가 없으면 멈추고 묻기, 계약 문장이 뒤 slice 기록에 기대면 구현 전에 묻기 |
| Rollback or recovery | 새 파일 삭제, 수정 파일은 ledger에 적어 되돌림(commit 전), migration은 downgrade 왕복 시험, 색인 추가는 시험 DB에서만 |
