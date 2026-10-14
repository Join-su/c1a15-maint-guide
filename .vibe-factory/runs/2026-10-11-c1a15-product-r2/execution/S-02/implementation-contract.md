# Slice Execution Card S-02

| Field | Record |
| --- | --- |
| Slice execution packet path / SHA-256 | `execution/S-02/slice-execution-packet.json` / `cecf0134c8ea94807c2037d430b835810e5acb6508c2f0c47247acd38ceb02d3` |
| Plan version / authorized item IDs / batch | plan v4 / P-03 · P-04 · P-05 · P-06 · P-07(PBC-4 v4 authorization) / per_slice_gated — slice S-02의 P-08은 승인 밖(OOS-01 화면 결정 → 새 판) |
| Baseline revalidation result | pass — HEAD · 데이터 · Playbook · 도구 같음. lockfile 2개는 S-01 승인 산출물(`execution/S-02/baseline-revalidation.json`) |
| AC and expected slice outcome | 완료 판정: AC-28 · AC-34(완료 P-07). 그 밖 28개 AC는 부분 증거 후 deferred(완료 item P-08 · P-10 · P-11 · P-12 · P-13 · P-15 · P-16 · P-17). 결과: 명세 R1 ~ R13 판정 함수(R5 계산 예시 통과) · 세션 state machine · 검색 · LLM Adapter(fixture) · API 핵심 · 알람 발생기 CLI, P-03 직후 OOS-01 질문 |
| Allowed changes / prohibited actions | 허용: server/src/c1a15/(engine · retrieval · llm · api · alarms) · server/tests · server/migrations(0002 이후) · scripts/(검사 보강) · data/demo/(각본, 사용자 결정 뒤). 금지: authorization prohibited_actions 전부 · P-08 화면 · commit · push |
| Commands and AC verifier | `scripts/check-fast`(unit · property · 정적 검사) · `scripts/verify-db`(API · 통합 · 실제 PostgreSQL) · `scripts/verify-e2e`(compose smoke) · ADV-04 ~ 07 |
| Required automatic quality gates | 12개 전부. 대상이 아직 없는 gate(e2e_surface_journey · prototype_structure_checklist)는 확인 범위를 evidence에 밝힌다 |
| Review requirement and rationale | `independent_critic` — P-03 · P-05 · P-06이 권한 판정 · 외부 provider 경계 · 공개 API |
| Loop cap / stop or escalation condition | 같은 verifier 3회. 중단 5종 + OOS-01(P-03 완료 즉시 질문) · 실행 해석 ③(Prototype 변경 시작 시 멈춤). 별도 승인(새 패키지 · 시험 컨테이너는 S-01 승인 범위) 전 실행 안 함 |
| Rollback or recovery | 새 파일 · 새 migration만(0001 · 적재기 · S-01 파일은 필요한 경우만 수정하고 ledger에 기록). 되돌림: 생성 파일 삭제 · Alembic downgrade 0001 · compose down -v |
