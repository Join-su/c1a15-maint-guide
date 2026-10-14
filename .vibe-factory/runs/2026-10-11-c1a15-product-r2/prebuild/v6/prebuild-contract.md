# Pre-build Contract: v6

> This contract compiles approved product artifacts into an implementation plan. It cannot add or reinterpret product behavior.

Run `2026-10-11-c1a15-product-r2` · PBC-4 · approval attempt `PBC4-A6`(L1 plan amendment A-02의 사람 요청 수정판, 부모 `PBC4-A5` revise — `critics/PBC4-5-review.json` · 사용자 결정 `coding-plan/v5/decisions/pbc4-a5-user-decisions.md`, 승인된 마지막 attempt는 `PBC4-A4`) · 2026-10-13. 승인된 v4와 달라진 점은 `coding-plan/amendments/A-02/plan-amendment-v6.md`(Prototype Bundle v17의 T04 / first_call을 P-08에, 새 P-18 진단 미리보기 보강, P-09 · P-10에 첫 판정 호출의 호출 요약 '점검 전', S-02 2차 cycle(P-08 · P-18), OOS-01 해결, 이전 결정의 정리 항목). 바뀐 범위는 `approved-inputs/changed-scope-v2.md`. 그 밖의 계약 내용은 v4와 같다.

## Feature identity

- Feature ID: `c1a15-maintenance-guide`(정비 길잡이 — 정비자 앱 `tech` · 파트장 앱 `lead`, multiple product UI surface)
- Plan mode: `standard`(일반 UI/workflow + 여러 subsystem. run risk_level standard. 권한 · 감사 · 외부 provider 경계는 item별 `independent_critic`으로 다룬다)

## Approved product input lock

`approved-inputs/approved-artifact-manifest.json`(v2, product_lock true — v1은 approved-inputs/history/, 바뀐 것은 Prototype Bundle v16 → v17뿐).

| Bundle | Version | Manifest | Manifest SHA-256 | Gate Decision |
| --- | --- | --- | --- | --- |
| use_case_bundle | v6 | `manifests/use_case_bundle-v6.json` | `492a33836fbaec95d09fba52b7d8d6bbacbcba0617df6083d0fdef7a2b197a94` | `decisions/G1-use-case.json` |
| prototype_bundle | v17 | `manifests/prototype_bundle-v17.json` | `ba27e0b2209963f40e4f6d725c7100f41733afd7f8a1ff1a383e3e056000569b` | `decisions/G3-prototype.json` |

Use Case manifest는 use_case_packet · use_case_map · scenario_coverage · acceptance_criteria · logical_system_contract를, Prototype manifest는 prototype_slice · prototype_renderable · prototype_coverage · variation_evidence · execution_evidence를 path · hash로 잠근다. 지킬 약속(manifest preservation_promises 원문):

- PBC와 G4~G7은 Use Case Bundle v6과 Prototype Bundle v17만 제품 입력으로 쓴다(Evidence Pack · G2A · G2B는 직접 읽지 않는다)
- AC 48개 · Scenario · 권한(정비자 · 파트장) · 데이터 의미 · 승인 화면 69개와 파생 상태 8개의 구조 · Region 252개 · G2B 시각 규칙을 바꾸지 않는다. 바뀌어야 하면 범위 밖 계약 변경으로 멈춘다
- T04 / first_call의 규칙 예외(R-NEXT에 C 배지 · 절 · 점검 이름 · 소요 분, '점검 시작'에 호출 경고 토큰)는 그 상태에서만 쓴다(G3 v17 승인, CO-42)
- G3 excluded_scope(미룬 AC 23개 조건 단위 · 화면 판정 AC 안의 서버 부분 AC-45-C3 · AC-48-C1 · AC-48-C2)는 PBC에서 서버 · 단위 · 통합 시험으로 모두 연결한다
- agent와 검색 index는 eval/cards와 generation/cause_ratio_table.json을 읽지 않는다
- credential · key는 저장소에 두지 않고, 설치 · Docker pull · 실제 OpenAI 호출은 사용자 승인 뒤에만

## Planning baseline and revalidation

`discovery/planning-baseline.json` v3: 저장소 HEAD `f73c240`, 의존성 revision `package-lock.json sha256 16ab13dd3ae21554c227877797d25b4bb0cf3a8ced7293bb05499ecfcc609cf5 · server/uv.lock sha256 a5d3473321ed79b62b4e18dae7e13c67667acd7ab13593c5600e636d43587997 (S-01 · S-02 승인 산출물, commit 전)`, 기록 2026-10-13T12:44:42+09:00. 사실:

- git branch main, HEAD f73c240 TW-4를 공구 편마모로 바꾸고 데이터·평가 카드를 맞춘다 — S-01 · S-02 구현은 사용자 지시대로 commit 전(작업 트리 변경 24건: .gitignore 수정 1, 추적 안 된 경로 23개 — apps/ · packages/ · server/ · infra/ · scripts/ · data/demo/ · docker-compose.yml · package.json · package-lock.json · CLAUDE.md · .env.example · .vibe-factory/)
- 도구: uv 0.12.17, Python 3.12.14(uv 고정 · server/.python-version), Node v26.9.0, Docker 29.1.3, Chrome headless(G3 시험), Playwright 브라우저 캐시 chromium 1243(@playwright/test 1.63.0 — PBC-2 FP-02)
- 제품 데이터: data/manifest.json sha256 7b36f4234634bee098f63ea099ea73c0f3d35de1bba7494b497ed8f2a1cdc10d, data/alarm_rules.json sha256 ef84d5b0317ed9de839c8b7b150bf5f58ce72764192fd9dfd54049dbf3865042, data/demo/scenarios.json sha256 f374d051ea2e040870e06f9fd2c2f7b65cb722bcd178aaa927079b7d2ca1c45c(S-02 P-07, 재생성 diff 없음)
- OpenAPI 정본 server/openapi.json sha256 15b6b5dd257ee6371fb41be89f632b733a749fc5465ff82c62f1e7ee1743ceea(S-02 P-06)
- Engineering Playbook: .vibe-factory/playbooks/engineering-playbook-c1a15-supplement-v4.md sha256 5420be68c37528bd80323188e3ebd84296a99a7f03c45314a0329b940b8460a7(v2 기준과 같음)
- 평가 자료 eval/cards · generation/cause_ratio_table.json은 저장소에 있으나 제품 코드 접근 금지(scripts/forbidden_paths_check.py), scripts/만 card_udi_map UDI 읽기(사용자 결정)
- 검증 명령: scripts/check-fast · verify-db · verify-e2e가 S-02 끝(2026-10-13)에 모두 pass(execution/S-02/evidence-v2/)
- 로컬 Docker image pgvector/pgvector:0.8.6-pg16-bookworm · nginx:latest · python:3.12-slim(S-01 승인 pull), OpenAI 키는 저장소 밖

재검토 조건: repository revision or dependency revision changes · selected model, framework, or external contract changes · data/manifest.json · alarm_rules.json · scenarios.json · Engineering Playbook hash가 바뀔 때 · approved inputs(Use Case Bundle · Prototype Bundle) version이 바뀔 때. 각 slice 시작(G4) 때 이 기준선과 현재 저장소 · 의존성 · 환경을 비교하고, 계획을 무효로 만드는 변화는 PBC-1 이상 재검토 또는 L1 amendment로 보낸다. Engineering discovery: `discovery/engineering-discovery.md` v2, Engineering Playbook `c1a15-supplement-v4`(Selection Register에 path · SHA-256 · 검토일 고정).

## Scope

### In scope

- Coding Plan v6 `coding-plan/v6/coding-plan.json`의 plan item P-01 ~ P-18(slice S-01 ~ S-06; S-01 = P-01 · P-02와 S-02 1차 cycle = P-03 ~ P-07은 구현 · 검증 완료, commit 전, S-02 2차 cycle = P-08 · P-18): 두 앱 · 공통 UI 패키지 · FastAPI API 서버 · 결정적 판정 엔진 · 검색 · LLM Adapter(fixture 기본) · PostgreSQL(ops · knowledge + pgvector) · 적재기 · 알람 발생기 · 평가 실행기 · Compose/nginx 실행 구성 · harness.
- 승인 AC 48개 전부와 Prototype 구조 계약 252 Region, 논리 흐름 FLOW-01 ~ FLOW-14.
- G3 excluded_scope로 넘어온 서버 부분(AC-45-C3 · AC-48-C1 · AC-48-C2, AC-41-C2 · AC-33-C1 · AC-12 서버 거부)과 미룬 AC 23개의 서버 · 계산 · 데이터 조건.
- G3 승인 판단 · 생성자 해석 · T04 / first_call 규칙 예외(v17)와 이월 메모 CO-22 · 31 · 32 · 36 · 37 · 38 · 39 · 40 · 41 · 42, S-02 G6 이월 의견 S02-G6-1 ~ 5(Coding Plan `approved_gate_interpretations` · `carryover_resolution`).

### Out of scope

- 배포 · 외부 메신저 · 실제 설비 연동 · Use Case Non-goals 전부.
- 없음(OOS-01은 해결 — OOS-01 해결(사용자 결정 013, sources/intent/013.md · G3 v17 승인 decisions/G3-prototype.json): 첫 판정이 바로 파트장 호출인 진단 화면은 파생 상태 T04 / first_call — 진단 화면 구조 그대로 '다음 점검' 카드에 '파트장 호출 필요'와 이유, 주 버튼 '점검 시작'(호출 경고 토큰) → 잠금 → 호출 요약(T10). S-02 계산(execution/S-02/oos01-first-judgment.md): 초기 등급표에서 시연 각본 10건은 모두 첫 판정이 점검 지시, 이 화면은 등급 변경 뒤나 CL-2 50% 이상일 때. 서버 호출 판정 함수는 S-02에서 이미 구현됐다(top_cause_cd_only · no_ab_left).).
- live OpenAI 호출 · live 평가(별도 승인 전).

### Product changes that this Contract must not make

AC · 사용자 흐름 · 권한 의미(정비자 / 파트장 역할, 등급 A · B · C · D, 잠금 선행, 정정 범위) · 데이터 의미(평가 카드 · 원인 비율표 분리, 정정은 덧붙임) · Prototype 화면 구조 · Component foundation · 표시 조정. 필요하면 범위 밖 계약 변경으로 기록하고 멈춘다.

## Approved flow and Acceptance Criteria

Use Case Bundle v6 · Prototype Bundle v17만 제품 입력이다. AC → plan item → verifier 연결은 Coding Plan items[].acceptance_ids와 Verification Matrix `coding-plan/v6/verification-matrix.json`(AC 48개 원문 · 관찰 조건 복사, plan_item_ids · completion_plan_item_id · L1 ~ L4)에 있다. Evidence Pack · G2A · G2B는 PBC 입력으로 다시 열지 않았다.

## Engineering selection summary

Coding Plan `coding-plan/v6/coding-plan.json`, Selection Register `coding-plan/v6/selection-register.json`(standard: 범주 15개 모두 검토, record 27건 — 채택 21 · 제외 6). 채택: modular monolith + deterministic workflow, 순수 함수 판정 + state machine + LangGraph interrupt · checkpoint 껍데기, PostgreSQL 1개 + Alembic, BM25 글자 2-gram + pgvector + RRF k=60 + 센서 거리, LLM Adapter fixture 기본, OpenAPI + openapi-typescript, React + Vite + npm workspaces, argon2id + 서버 세션 쿠키(앱별 이름) + nginx 앱 표시 header 대조, 주기 조회, Compose + nginx 8081/8082, uv + Python 3.12, Playwright TypeScript 1.63.0, act → verify → repair(상한 3회), read-only reviewer subagent, 현재 개발 model. 제외: single · multi-agent, hook, MCP, worktree 병렬, 추가 Skill, SSE · WebSocket. provisional 결정 없음(모든 item decided).

## PBC critic record

PBC-4 uses exactly one independent critic invocation for this approval attempt.

- Approval attempt ID: `PBC4-A6`
- Parent approval attempt ID, if this is a human-requested revision: `PBC4-A5`(critic revise `critics/PBC4-5-review.json` — ISS-001 P-08 L3가 S-03 범위에 기댐 · ISS-002 첫 판정 호출의 호출 요약 누락, 사용자 결정 'plan v6로 고침'). 그 위의 승인 attempt는 `PBC4-A4`(pass, `decisions/PBC-4-prebuild-contract.json`)
- Critic comparison references (artifact / path / version / hash): critic input bundle `critics/PBC4-6-input.json`의 comparison_sources — use_case_bundle `manifests/use_case_bundle-v6.json` v6, prototype_bundle `manifests/prototype_bundle-v17.json` v17, coding_plan `coding-plan/v6/coding-plan.json` v6, verification_plan `coding-plan/v6/verification-matrix.json` v6, selection_register `coding-plan/v6/selection-register.json` v6, feasibility_probe `coding-plan/v1/feasibility-probe.json` v1(불변), pbc_consistency_check `prebuild/v6/pbc-consistency-check.json` v6, prebuild_contract(이 문서) v6. hash는 input bundle에 고정한다.

If it returns `revise` or `ask-user`, record the issues and stop for a human decision; do not silently revise and request another PBC critic. A human-requested plan revision creates a new plan version and approval attempt, which may receive one new critic invocation.

## Authority, risk, and external-action boundary

- 이번 구현 승인 요청 범위는 plan v6의 P-08 ~ P-18(S-02 2차 cycle과 S-03 ~ S-06의 남은 item 전부)이다. P-01 ~ P-07은 plan v3 · v4 승인으로 S-01 · S-02 1차 cycle에서 완료됐다(`execution/S-01/` · `execution/S-02/`, 이번 수정이 계약을 바꾸지 않음). slice(와 S-02 2차 cycle)마다 사람 결정 뒤 다음으로 간다.
- 구현은 승인된 plan item 범위의 파일만 만든다(저장소 `/Users/insujo/Documents/repo/c1a15-maint-guide`). slice마다 사람 결정 뒤 다음 slice(`per_slice_gated`).
- 절대 하지 않는 것: 승인 Use Case Bundle v6 · Prototype Bundle v17의 AC · 사용자 흐름 · 권한 의미 · 데이터 의미 · 화면 구조 · 시각 규칙 변경; T04 / first_call의 규칙 예외(R-NEXT의 C · D 점검 정보 · '점검 시작'의 호출 경고 토큰)를 그 상태 밖 화면 · 상태에 쓰기; 완료된 P-01 ~ P-07의 계약 바꾸기(바꿀 일이 생기면 L1 amendment); eval/cards · generation/cause_ratio_table.json을 진단 처리 · 색인 · 적재기에서 읽기; 비밀번호 · API 키 원문을 저장소 · 로그 · DB에 쓰기; fixture 시험 · 시연에서 외부 네트워크 호출; plan item 밖 파일 · 다른 저장소 수정, Wiki 쓰기; 배포 · 외부 메시지 전송.
- 별도 승인이 필요한 것(실행 직전): live OpenAI 문장 · 임베딩 smoke(소수 · 격리, 키는 사용자 제공); live 모드 평가 실행; npm · uv 패키지 설치, Python 3.12 내려받기; Docker image pull(python · node 빌드 image 등 로컬에 없는 것); Playwright 브라우저 내려받기(1.63.0 밖의 판을 쓸 때); git commit · push; Docker 컨테이너로 시험 DB · 시험 스택 실행(첫 실행 전 한 번).
- 권한 경계의 정본은 서버(B-04 · B-05). 화면은 서버가 허용한 수단만 보인다. 권한 · 감사 · 외부 provider · migration · 공개 API를 다루는 P-02 · P-03 · P-05 · P-06 · P-09 · P-11 · P-14 · P-18은 완료 때 read-only 독립 reviewer 검토.

## Required implementation and verification evidence

Verification Matrix `coding-plan/v6/verification-matrix.json`: AC 48개 × L1(규칙) · L2(API · 실제 PostgreSQL 통합) · L3(E2E · visual) · L4(증거 연결), 경계는 모두 fixture(APP_MODE=fixture, 외부 호출 0) + 시험 DB 컨테이너 + Playwright 외부 요청 차단. 수동 검토 7건. 별도 승인이 필요한 행동 7건(Matrix live_actions_requiring_separate_approval = 아래 proposal separate_approval_required_for, 같은 목록).

첫 end-to-end: FLOW-03 · SC-04 · slice S-02, 경계 B-01 → B-03 → B-04 → B-05 → B-06 → B-07 → B-08. 결과: 정비자가 정비자 앱에서 알람의 진단을 열고 잠금을 확인한 뒤 지시된 점검 결과를 넣으면, 서버가 결과를 세션 단계 기록에 저장하고 순위를 다시 계산해 다음 점검 지시를 낸다(fixture 문장). S-02 L3(2차 cycle, 완료 P-08)는 다음 단계가 점검 지시인 경로(예: 4.3 '확인 불가' → 순위 그대로 · 4.5 지시, T06 / unable_next)로 판정한다. 다음 단계가 호출 요약인 경로(4.3 정상 → 호출)는 호출 요약 화면이 있는 S-03(P-10)에서 L3로 판정한다. 다시 읽기: 새로고침 · 앱 재시작 · API 재시작 뒤 같은 세션의 같은 단계 · 잠금 시각 · 입력 결과 · 재계산 순위가 서버 기록에서 다시 읽힌다(AC-14). L3: AC-04 L3 e2e — 첫 end-to-end(FLOW-03 · SC-04 · S-02 2차 cycle, 완료 P-08): 로그인 → 알람 → 진단 → 잠금 → 4.3 '확인 불가' → 순위 그대로(합 100) · 4.5 지시(T06 / unable_next)가 서버 기록에 저장되고 새로고침 · API 재시작 뒤 같은 순위 · 단계로 다시 읽힘 (완료 item P-08). 다음 단계가 호출 요약인 경로의 L3: AC-03 L3 e2e — S-03(완료 P-10): 정비자 앱에서 같은 입력의 진단 50 · 28 · 11 · 11 · 첫 지시 4.3 → 정상 입력 → 순위 57 · 22 · 21 → 파트장 호출 요약 화면(T10 / summary) (완료 item P-10). 제외한 live 행동: live OpenAI · 임베딩.

UI surface 통합: tech — SC-06 · slice S-03 · 진입 B-01 → 다시 읽기 B-04 · AC-07 L3 e2e — tech 핵심 Scenario SC-06(S-03, 완료 P-10): 보고서 화면(T09 / check_failed) 실패 항목 표시 · 확정 버튼 잠김 → 고친 뒤 확정 → 승인 대기가 서버에서 다시 읽힘 (완료 item P-10) + AC-33 L3 e2e — tech 핵심 Scenario SC-06(S-03, 완료 P-10): 보고서 확정 → T09 / confirmed에 연필 없음 · 다시 열어도 수정 수단 없음, 승인 대기 상태가 서버에서 다시 읽힘 (완료 item P-10) / lead — SC-35 · slice S-04 · 진입 B-02 → 다시 읽기 B-01 · AC-11 L3 e2e — lead 핵심 Scenario SC-35(S-04, 완료 P-13): 파트장 앱 L03 / reject에서 사유 입력 · 반려 → 정비자 앱 홈(T02 / rejected) · 최근 보고서에 반려 · 사유가 다시 읽힘 → 고쳐 다시 확정 → 파트장 승인 대기 목록에 다시 나타남 (완료 item P-13) + AC-24 L3 e2e — lead 핵심 Scenario SC-35(S-04, 완료 P-13): 파트장 앱 L03 / reject에서 사유를 비우고 저장 → 저장 안 됨 · 보고서 상태 그대로(정비자 앱 홈에 반려 없음) (완료 item P-13).

## Feasibility preflight and safe adversarial verification

Coding Plan `feasibility_preflight`: status `verified`, basis `internal_compatibility_probe`, probe `coding-plan/v1/feasibility-probe.json`(v1 그대로 — v6의 plan item ID P-01 · P-06 · P-13이 v1과 같다, sha256 `117d4df0de124a8f4d46423cd9da177e76df7d4007ca24819a21b7f650f7efe9`) — FP-01(authority_boundary, item P-01, P-06): pass; FP-02(verifier, item P-01, P-13): pass. 사용자 승인 범위(로컬 image 컨테이너 · 임시 폴더 Playwright)로만 실행했고 정리 증거가 있다.

결함 주입(Verification Matrix adversarial_cases, run risk는 standard지만 권한 · 비밀 · 누수 경계 때문에 둔다):

| ID | 완료 item | 안전 대상 | fail-closed 판정 | 정리 |
| --- | --- | --- | --- | --- |
| ADV-01 | P-01 | temporary_local_file: pytest tmp_path 아래 가짜 저장소 사본 | 스캔이 종료 코드 1로 실패하고 파일 · 행을 보고해야 통과 | tmp_path 자동 삭제 |
| ADV-02 | P-02 | in_memory_fixture: 분리 검사 함수에 넘기는 메모리 목록(가짜 행) | 분리 검사가 교집합 1건을 보고하며 실패해야 통과 | 메모리 객체만 |
| ADV-03 | P-02 | isolated_process: 시험용 PostgreSQL 컨테이너(매 시험 초기화)의 ops.accounts | 결함 사본에서 '저장값이 argon2id 형식이 아님' 검사가 실패해야 통과 | 컨테이너 DB 초기화 |
| ADV-04 | P-04 | in_memory_fixture: 고정 이력 fixture + 가짜 임베딩 | 누수 검사가 원인 필드 사용을 찾아 실패해야 통과 | 메모리 객체만 |
| ADV-05 | P-05 | local_test_listener: 127.0.0.1 임시 포트의 시험 listener(외부 주소 대용) + 소켓 차단 | (a) 차단으로 호출이 실패 · 외부 호출 카운터 1이면 시험 실패 표시, (b) 화면 · 보고서 문장이 원문 대체로 바뀌어야 통과 | listener 종료 |
| ADV-06 | P-06 | loopback_listener: Compose 시험 스택의 nginx 127.0.0.1:8081/8082(API 포트 비공개) | 모든 위조 요청이 401/403이고 업무 기록이 바뀌지 않아야 통과 | compose down -v |
| ADV-07 | P-06 | isolated_process: 시험용 API 프로세스 + 시험 DB | API가 지시 내용 없이 거부 · 호출 요약으로 응답하고, 결함 사본에서는 음성 시험이 실패해야 통과 | 시험 DB 초기화 |
| ADV-08 | P-14 | isolated_process: 시험용 API 프로세스 + 시험 DB | 정정 불가 · 확정 세션 요청이 거부되고, 결함 사본에서는 '원래 값 남음' 검사가 실패해야 통과 | 시험 DB 초기화 |
| ADV-09 | P-16 | temporary_local_file: tmp_path의 가짜 eval/cards 사본(가짜 카드) | 파일 접근 감시가 진단 처리의 eval 경로 접근을 잡아 실패해야 통과 | tmp_path 삭제 |

금지된 실제 행동(모든 case): 외부 네트워크, 실서비스 · live OpenAI, 실제 secret · 민감 데이터, 평가 카드 원본을 진단 처리에 넣기. This Contract never authorizes an external or live action merely to inject a failure.

## Pre-critic consistency check

`prebuild/v6/pbc-consistency-check.json`: 현재 coding plan · selection register · verification matrix · 이 contract · feasibility probe hash와 selected_vs_rejected · plan_vs_verification · logical_flow_compilation · change_representation · feasibility_preflight 결과. It is a PBC machine-artifact check, not a product-contract review.

## Plan amendment and learning policy

- L0: 승인된 private 내부 작업의 이름 · 작은 정리만. execution ledger에 남기고 plan version을 바꾸지 않는다. 예상 밖 사실은 크기와 무관하게 unexpected_facts에 먼저 기록하고 재확인 pass일 때만 L0.
- L1: 공개 API 계약 · 데이터 · 의존성 · 시험 전략 · model role · loop/harness/graph 변화는 plan-amendment.md · 전후 그림 · 영향 AC · slice · test · critic pass · 사용자 승인이 있는 새 plan version 없이는 실행하지 않는다.
- 범위 밖: AC · 사용자 흐름 · 권한 의미 · 데이터 의미 · G2A/G2B 약속(Prototype 구조 · 시각 규칙) 변화는 PBC에서 처리하지 않고 Factory 범위 밖 계약 변경으로 기록한 뒤 멈춘다. OOS-01은 결정 013으로 해결됐다(G3 v17 · PBC-0 재잠금 v2).
- Learning Record: 예상 밖 사실 · 반복 실패 · Playbook 공백은 execution ledger `unexpected_facts`에 남기고, Playbook 갱신은 별도 knowledge-curation 작업(사용자 승인)으로만 한다. 검증 스크립트 결함(DEV-17)은 Skill 개선 제안으로 사용자에게 보고했다. 계약 본문은 생성 뒤 미렌더 변수가 없는지 기계 검사한다(PBC4-A1 ISS-001 재발 방지).

## Implementation authorization proposal

```json
{
  "allowed_plan_version": "v6",
  "allowed_plan_item_ids": [
    "P-08",
    "P-09",
    "P-10",
    "P-11",
    "P-12",
    "P-13",
    "P-14",
    "P-15",
    "P-16",
    "P-17",
    "P-18"
  ],
  "execution_mode": "per_slice_gated",
  "stop_conditions": [
    "failed_or_missing_automatic_gate",
    "L1_or_out_of_scope_contract_change",
    "new_external_or_separate_approval_action",
    "baseline_drift",
    "repair_cap_exceeded"
  ],
  "prohibited_actions": [
    "승인 Use Case Bundle v6 · Prototype Bundle v17의 AC · 사용자 흐름 · 권한 의미 · 데이터 의미 · 화면 구조 · 시각 규칙 변경",
    "T04 / first_call의 규칙 예외(R-NEXT의 C · D 점검 정보 · '점검 시작'의 호출 경고 토큰)를 그 상태 밖 화면 · 상태에 쓰기",
    "완료된 P-01 ~ P-07의 계약 바꾸기(바꿀 일이 생기면 L1 amendment)",
    "eval/cards · generation/cause_ratio_table.json을 진단 처리 · 색인 · 적재기에서 읽기",
    "비밀번호 · API 키 원문을 저장소 · 로그 · DB에 쓰기",
    "fixture 시험 · 시연에서 외부 네트워크 호출",
    "plan item 밖 파일 · 다른 저장소 수정, Wiki 쓰기",
    "배포 · 외부 메시지 전송"
  ],
  "separate_approval_required_for": [
    "live OpenAI 문장 · 임베딩 smoke(소수 · 격리, 키는 사용자 제공)",
    "live 모드 평가 실행",
    "npm · uv 패키지 설치, Python 3.12 내려받기",
    "Docker image pull(python · node 빌드 image 등 로컬에 없는 것)",
    "Playwright 브라우저 내려받기(1.63.0 밖의 판을 쓸 때)",
    "git commit · push",
    "Docker 컨테이너로 시험 DB · 시험 스택 실행(첫 실행 전 한 번)"
  ],
  "approver_role": "사용자(프로젝트 소유자)"
}
```

This is a critic-reviewed proposal, not an authorization. The Human Gate Decision records the actual `implementation_authorization`, including `authorized`, `approved_by`, and `approved_at`. An actual authorization may authorize only the listed plan items and never an action listed in `separate_approval_required_for`.
