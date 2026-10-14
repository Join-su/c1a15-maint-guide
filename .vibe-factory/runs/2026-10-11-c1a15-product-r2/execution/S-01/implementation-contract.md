# Slice Execution Card S-01

| Field | Record |
| --- | --- |
| Slice execution packet path / SHA-256 | `execution/S-01/slice-execution-packet.json` / `f01eb9f3d327ac3425bdbd2c241213b6e279d9039ae96a547c0a021919afecb8` |
| Plan version / authorized item IDs / batch | plan v3 / P-01 · P-02(PBC-4 authorization P-01 ~ P-07 안) / per_slice_gated — S-01 끝나면 사람 결정 |
| Baseline revalidation result | pass — HEAD f73c240 · 작업 트리 · 도구 버전 · 데이터 · Playbook hash가 planning baseline v2와 같음(`execution/S-01/baseline-revalidation.json`) |
| AC and expected slice outcome | 완료 판정: AC-36(완료 P-02). 부분 증거 후 deferred: AC-09(완료 P-13) · AC-15(P-16) · AC-16(P-17) · AC-34(P-07). 결과: 저장소 골격 · 실행 구성 · DB schema · 적재 완료, check-fast 통과, migration 왕복, 적재 건수 · 분리 검사 통과 |
| Allowed changes / prohibited actions | 허용: 저장소 `/Users/insujo/Documents/repo/c1a15-maint-guide` 안 P-01 · P-02 파일(apps/ · packages/ · e2e/ 골격, server/ uv 프로젝트, migrations, 적재기, compose · nginx 설정, scripts/, CLAUDE.md, .env.example). 금지: authorization prohibited_actions 전부(eval/cards · generation/ 읽기, 비밀 원문, 외부 호출, 다른 저장소 · Wiki, 배포) · commit · push |
| Commands and AC verifier | `npm ci` · `uv sync --frozen` · `scripts/check-fast`(format · lint · typecheck · unit · 비밀값 스캔 · eval 접근 정적 검사) · `docker compose config` · 8081/8082 smoke · Alembic upgrade → downgrade → upgrade · 적재 건수 · 분리 검사 · argon2id 저장값 검사 · ADV-01 · 02 · 03 |
| Required automatic quality gates | scope_traceability · ac_verifier · static_check · typecheck · unit_and_property · api_negative_authority(S-01 해당 없음 → 근거 기록) · integration_real_postgres · e2e_surface_journey(S-01 해당 없음) · prototype_structure_checklist(S-01 해당 없음) · secret_scan · external_call_zero_in_fixture · leakage_check |
| Review requirement and rationale | `independent_critic` — P-02가 data migration · 저장 데이터 경계(SEL-SUBAGENT read-only reviewer) |
| Loop cap / stop or escalation condition | act → verify → repair 같은 verifier 3회. 중단: failed_or_missing_automatic_gate · L1_or_out_of_scope_contract_change · new_external_or_separate_approval_action · baseline_drift · repair_cap_exceeded. 별도 승인(설치 · Python 3.12 · image pull · 시험 컨테이너) 전에는 해당 명령 실행 안 함 |
| Rollback or recovery | 새 파일만 만든다(기존 data/ · scripts/ · eval/ · docs/ 수정 없음). 되돌림: 생성 파일 삭제 · `docker compose down -v` · Alembic downgrade base |
