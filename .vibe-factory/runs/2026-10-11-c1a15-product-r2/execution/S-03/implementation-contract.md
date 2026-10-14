# Slice Execution Card S-03

| Field | Record |
| --- | --- |
| Slice execution packet path / SHA-256 | `execution/S-03/slice-execution-packet.json` / `a8f1658bc7173a114283202a44682a30e77aa68596148e561da8a80474714b37` |
| Plan version / authorized item IDs / batch | plan v9 / P-09 · P-10(PBC-4 v10 authorization P-08 ~ P-19) / per_slice_gated |
| Baseline revalidation result | pass — HEAD · uv.lock · 각본 · Playbook은 기준선 v3와 같고, package-lock · data · OpenAPI hash는 S-02 예상 변경 표와 같음(`execution/S-03/baseline-revalidation.json`) |
| AC and expected slice outcome | 연결 AC 20개(AC-02, AC-03, AC-06, AC-07, AC-08, AC-11, AC-17, AC-19, AC-20, AC-21, AC-22, AC-23, AC-26, AC-29, AC-30, AC-32, AC-33, AC-37, AC-42, AC-43). 결과: 정비자 조치(A · B 체크리스트) · 재가동(체크리스트) · 재가동 후 값 확인(경계 이내 · 여전히 밖) · 호출 요약(수정 · 보내기 · 대기) · 답 반영(시험 답 기록) · 숙련자 인계 · 이상 없음 · 감시 마감 · 보고서 8항목 초안 · 수정(R8) · 확정 전 확인 · 확정(승인 대기) |
| Allowed changes / prohibited actions | 허용: server/src/c1a15/{api, engine, llm, db} · server/migrations(새 표가 필요하면) · server/tests · server/openapi.json · packages/ui · apps/tech · e2e · scripts(검사 보강). 금지: authorization prohibited_actions 전부 · 파트장 앱 · 파트장 답 API(P-11 · P-12, S-04) · 정정 API(P-14, S-05) · 앱이 화면 값을 직접 만들기 · commit · push |
| Commands and AC verifier | `scripts/check-fast` · `scripts/verify-db` · `scripts/verify-e2e`(Playwright tech journey 확장) · OpenAPI 재생성 diff 0 · Prototype 구조 대조(T08 ~ T11 · 파생 T09 상태) · 증거 폴더 비밀값 검사 |
| Required automatic quality gates | 12개 전부 |
| Review requirement and rationale | `independent_critic` — P-09가 권한(C · D 호출, 확정 뒤 수정 금지) · 감사 · 공개 API를 다룬다 |
| Loop cap / stop or escalation condition | 같은 verifier 3회. 중단 5종 + 권한 음성 시험 실패 시 멈춤, 화면 값이 API에 없으면 멈춤, 계산 정의가 없는 값은 멈추고 묻기(결정 015처럼) |
| Rollback or recovery | 새 파일 삭제, 수정 파일은 ledger에 적어 되돌림(commit 전), migration은 downgrade 왕복 시험 |
