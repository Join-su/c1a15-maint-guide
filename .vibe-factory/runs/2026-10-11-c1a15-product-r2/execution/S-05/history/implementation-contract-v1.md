# Slice Execution Card S-05

| Field | Record |
| --- | --- |
| Slice execution packet path / SHA-256 | `execution/S-05/slice-execution-packet.json` / `5bd8ba5f5f21ea8461b514fd6236092f225c48da480f83453214334b64166367` |
| Plan version / authorized item IDs / batch | plan v11 / P-14 · P-15(PBC-4 v12 authorization P-08 ~ P-19) / per_slice_gated |
| Baseline revalidation result | pass — HEAD · Playbook은 기준선 v3와 같고, lockfile · data · OpenAPI hash는 S-04 예상 변경 표 값과 같음(`execution/S-05/baseline-revalidation.json`) |
| G4 전 대조 | 점검표 C1 ~ C10 모두 pass(packet precheck), 정의 없던 8가지는 사용자 결정 019 |
| AC and expected slice outcome | 연결 AC 7개(AC-17, AC-41, AC-44, AC-45, AC-46, AC-47, AC-48). 결과: 지나온 단계 지난 화면(그때 값 · 이전 · 다음 · 현재 단계로 · 보내지 않은 입력 그대로), 정정(사유 필수 · 덧붙임 · 감사 · 정정 n회 · 이전 값), 결과 정정 뒤 다시 판정 · 뒤 기록 무효 · 확인 창, 조치 뒤 정정 호출 · 보낸 호출에 정정 상자, 정정하지 않는 기록 · 확정 세션 거부 · 메모 덧붙이기, 보고서 · 감사 · 이력 반영(결정 019), 홈 버튼 · 이어서 하기(AC-44) |
| Allowed changes / prohibited actions | 허용: server/src/c1a15/{api, engine, db} · server/migrations · server/tests · server/openapi.json · packages/ui · apps/tech · apps/lead(L04 정정 상자 · L06 정정 행만) · e2e · scripts(검사 보강). 금지: authorization prohibited_actions 전부 · 평가 실행기(P-16) · 시연 완주(P-17) · 앱이 화면 값을 직접 만들기 · Prototype 원본 읽기(부록만) · commit · push |
| Commands and AC verifier | `scripts/check-fast` · `scripts/verify-db` · `scripts/verify-e2e`(tech E2E 정정 · 지난 화면, 교차 E2E 보낸 호출 뒤 정정 → L04 · L06) · OpenAPI 재생성 diff 0 · 구조 대조(부록 기준) · 증거 폴더 비밀값 검사. 증거 순서(점검표 C9): E2E 보고서 복사 → 이미지 본문을 screens 경로로 → `--list`, dev 스택 내린 뒤 verify-e2e, 비밀값 검사 마지막 |
| Required automatic quality gates | 12개 전부 |
| Review requirement and rationale | `independent_critic` — P-14가 권한(정정 대상 · 확정 세션 거부) · 감사 · 공개 API · 판정 재적용 · 이력 변환을 다룬다 |
| Loop cap / stop or escalation condition | 같은 verifier 3회. 중단 5종 + 원래 값 손실 · 거부 실패 시 멈춤, 화면 값이 API에 없거나 계산 정의가 없으면 멈추고 묻기, G5 결정은 G6 전에 packet 판 올림 |
| Rollback or recovery | 새 파일 삭제, 수정 파일은 ledger에 적어 되돌림(commit 전), migration은 downgrade 왕복 시험 |
