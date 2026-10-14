# Slice Execution Card S-06

| Field | Record |
| --- | --- |
| Slice execution packet path / SHA-256 | `execution/S-06/slice-execution-packet.json` / `e5123c13da5e8caf5af79d10572708f2c612cd214047682697783250c8ba59ae` (packet v2 — G5 중 결정 020 ⑩ ~ ⑰ · v1 `6319f3c9…`는 history) |
| Plan version / authorized item IDs / batch | plan v11 / P-16 · P-17(PBC-4 v12 authorization P-08 ~ P-19) / per_slice_gated, 마지막 slice |
| Baseline revalidation result | pass — HEAD · Playbook은 기준선 v3와 같고, lockfile · data · OpenAPI hash는 S-05 예상 변경 표 값과 같음, 평가 카드 · 시연 각본은 commit 판 그대로(`execution/S-06/baseline-revalidation.json`) |
| G4 전 대조 | 점검표 C1 ~ C12 모두 pass(packet precheck), 정의 없던 것은 사용자 결정 020(① ~ ⑨). G5 중 ⑩ ~ ⑰(지표 정의 보완 · 사용자 위임 권장안 · 앞 slice 결함 수리)을 C6대로 packet v2에 실음 |
| AC and expected slice outcome | 연결 AC 5개(AC-02, AC-15, AC-16, AC-17, AC-18). 결과: 평가 실행기(평가 모드 · 카드 30건 · 지표 6 + 목표 · 등급 위반 0 · 분리), 깨끗한 환경 시연 10건이 보고서 확정(감시 · 인계 마감 포함)까지 · 외부 호출 0 · 재시작 재개, 두 앱 전 화면 252영역 대조(결정 020 ①), 감사 중복 행 수리(020 ④) |
| Allowed changes / prohibited actions | 허용: scripts(평가 실행기 CLI · 실행 wrapper · 검사 보강) · server/src/c1a15/alarms(표준 입력 · 평가 모드) · server/src/c1a15/api/{schemas,main}.py(내부 등록 eval_mode) · server/src/c1a15/api/sessions.py(결정 020 ④) · 앞 slice 결함 수리(packet front_slice_repairs — 결정 020 ⑬ api/{deps,lead,main}.py, ⑯ api/flow.py, ⑮ ⑰ apps/tech/src/screens/Session.tsx) · server/openapi.json · packages/ui/src/api/schema.d.ts(생성물) · server/tests · e2e · scripts/verify-e2e. 금지: authorization prohibited_actions 전부 · 제품 코드(server · apps · 적재기 · 색인)가 eval/ · generation/ 읽기 · live OpenAI · live 평가 · 앱이 화면 값을 직접 만들기 · Prototype 원본 읽기(부록만) · commit · push |
| Commands and AC verifier | `scripts/check-fast` · `scripts/verify-db` · `scripts/verify-e2e`(시연 10건 · 재시작 재개 포함) · 평가 실행(격리 시험 스택, fixture) · 전 화면 구조 대조(부록 기준, 상태별 수) · 증거 폴더 비밀값 검사. 증거 순서(점검표 C9): E2E 보고서 복사 → 이미지 본문을 screens 경로로 → `--list`, dev 스택 내린 뒤 verify-e2e, 증거를 고치면 비밀값 검사를 다시 마지막에 |
| Required automatic quality gates | 12개 전부 |
| Review requirement and rationale | `automatic`(plan P-16 · P-17) — G7 complete 전에 마지막 batch 통합 검토(독립 reviewer)와 Batch Evidence Index |
| Loop cap / stop or escalation condition | 같은 verifier 3회. 중단 5종 + 누수 검사 실패 · 시연 하나라도 실패하면 멈춤, 입력표 밖 단계 · 계산 정의 없음이면 멈추고 묻기, G5 결정은 G6 전에 packet 판 올림 |
| Rollback or recovery | 새 파일 삭제, 수정 파일은 ledger에 적어 되돌림(commit 전), 평가 · 시연 스택은 down -v |
