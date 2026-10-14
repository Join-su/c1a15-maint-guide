# Engineering Discovery v1

Run `2026-10-11-c1a15-product-r2` · PBC-1 · 2026-10-12. 입력은 PBC-0에서 잠근 두 묶음뿐이다: Use Case Bundle v6(`manifests/use_case_bundle-v6.json`)과 Prototype Bundle v16(`manifests/prototype_bundle-v16.json`), 주소록 `approved-inputs/approved-artifact-manifest.json`. Evidence Pack · G2A · G2B는 읽지 않았다. 이 문서는 구현 방법을 고르기 위한 사실과 후보만 적는다. 사용자 흐름 · AC · 권한 · 데이터 의미 · 화면 구조는 바꾸지 않는다.

## Repository and environment facts

기준선: `discovery/planning-baseline.json` v2(v1은 `discovery/history/planning-baseline-v1.json`, Playbook 보충판이 v3가 되어 다시 기록).

| 사실 | 관찰 값 | 계획에 주는 영향 |
| --- | --- | --- |
| 저장소 | `/Users/insujo/Documents/repo/c1a15-maint-guide`, branch main, HEAD `f73c240`. 추적 안 된 것은 `.vibe-factory/runs/`와 새 Playbook v2 · v3 파일뿐 | 제품 코드가 아직 없다(greenfield). 첫 slice가 저장소 골격을 만든다 |
| 추적 파일 | `data/`(alarm_rules.json · manifest.json · manuals/MG-MM.md · manuals/manual_sections.json · history/maintenance_history.jsonl), `scripts/build_data.py` · `scripts/manual_spec.py`, `eval/cards/*` · `eval/validate_cards.py`, `generation/cause_ratio_table.json`, `docs/spec` · `docs/architecture`, `.gitignore`(`.env` · `.venv/` · `node_modules/` 제외) | 적재기(FLOW-11)의 입력은 `data/`에 이미 있다. 평가 카드 · 원인 비율표는 진단 처리 · 색인이 읽지 않는다(AC-15) |
| 데이터 | `data/manifest.json`: AI4I 2020(CC BY 4.0, 라벨 6열 삭제), seed 10, 이력 300건(CL 158 · PW 65 · LD 47 · TW 30), 결과 원인 확정 253 · 이상 없음 · 감시 36 · 원인 미상 · 인계 11 | 이력 색인 · 검색 fixture의 고정 입력이 된다 |
| 의존성 | `package.json` · `pyproject.toml` · lockfile 없음 → `dependency_revision` unavailable | 첫 slice에서 lockfile(npm `package-lock.json`, uv `uv.lock` — EP-C1-WS-001 · EP-C1-PY-001)을 만든다 |
| 실행 환경 | darwin arm64, Python 3.14.2(pip 25.3), uv 있음, Node v26.9.0, Docker 29.1.3. 로컬 image: nginx:latest · node:18 · pgvector/pgvector:0.8.6-pg16-bookworm · postgres:15/latest(다른 프로젝트 것). Playwright 브라우저 캐시 있음, Playwright 패키지 · node_modules 없음 | 설치 · image pull · 컨테이너 실행은 사용자 승인 뒤. 팀원 Windows 환경(EP-C1-RUN-001 한계)도 대상 |
| Prototype 사실 | `prototype/v16/index.html` 한 문서에 승인 화면 69 + 파생 7, Region 252. 화면 값은 `wireframes/v4/samples/review-sample.json`과 `data/`에서 옮긴 fixture, 서버 · DB · LLM 없음 | 구현 화면의 판정 기준(EP-FE-001). 구조 계약은 `prototype/v16/prototype-coverage.json`의 `compiled_structure_contract`만 쓴다 |
| UI surface | `tech` 1080 × 740(태블릿 · 터치), `lead` 1280 × 620(PC · 마우스) | 앱마다 빌드 · E2E를 따로(EP-C1-SURFACE-001) |
| 논리 흐름 | FLOW-01~14(applicability required). 외부 의존은 live 모드 OpenAI(문장 · 임베딩)뿐, 모든 흐름 durable | 첫 end-to-end slice와 L3 증거는 PBC-2 · 3에서 이 흐름으로 정한다 |

## Requirement signals and cheapest verifiers

side effect: 그 AC가 만드는 저장 · 외부 효과. 실패 신호: 깨지면 보이는 것. 가장 싼 결정적 verifier: 먼저 쓸 검사(E2E는 surface별 핵심 journey에만, EP-TEST-001).

| AC | Flow | side effect | 품질 · 실패 신호 | 가장 싼 결정적 verifier |
| --- | --- | --- | --- | --- |
| AC-01 잠금 전 지시 없음 | FLOW-03 | 세션 잠금 시각 기록 | 잠금 전 응답에 절차 · 판정 기준이 있음 | 판정 함수 unit + API 음성 시험(잠금 전 요청 → 지시 내용 없음, 설비 변경 → 잠금 전) |
| AC-02 C · D는 호출 | FLOW-04 · 05 · 08 | 호출 요약 생성 | C · D 지시가 나감, 평가 30건 등급 위반 > 0 | 등급 판정 표 기반 unit + API 음성 시험 + 평가 실행기 집계(C3) |
| AC-03 R5 계산 예시 | FLOW-03 | 없음(계산) | 50 · 28 · 11 · 11, 첫 지시 4.3, 정상 뒤 57 · 22 · 21 + 호출이 아님 | 고정 입력 unit(EP-C1-RULE-001) |
| AC-04 재계산 · 합 100 | FLOW-03 | 세션 단계 기록 | 결과별 규칙 위반, 합 ≠ 100 | 표 기반 unit + property(합 100, 재정규화) |
| AC-05 확인 질문 '아니요' | FLOW-03 | 확인 질문 답 기록 | '아니요' 뒤 순위 변화 | unit(순위 불변) |
| AC-06 근거 검사 실패 → 원문 대체 | FLOW-03 · 06 | 대체 표시 기록 | 근거 없는 문장이 화면 · 보고서에 남음 | 근거 검사 unit(fixture 문장) + 보고서 생성 음성 시험 |
| AC-07 확정 전 확인 3항목 | FLOW-06 | 보고서 상태 | 실패 항목에도 확정됨 | API 상태 전이 시험 + component(버튼 잠김) |
| AC-08 승인 후 진행 뒤에만 C | FLOW-05 · 08 | 호출 답 · 승인자 · 시각 | 답 전 C 지시 노출 | API 음성 시험 + 두 앱 E2E(호출 → 답 → 지시 열림) |
| AC-09 승인 보고서가 다음 검색 후보 | FLOW-07 | 이력 · 두 색인 추가 | 승인 뒤 후보에 없음, 평가 모드 보고서가 이력에 들어감 | 통합 시험(실제 PostgreSQL + 가짜 임베딩) |
| AC-10 수정 후 승인 감사 | FLOW-07 · 10 | 감사 기록 | 항목 · 전후 값 · 메모 · 파트장 · 시각 빠짐 | API 시험(감사 행 필드) |
| AC-11 반려 뒤 다시 확정 | FLOW-06 · 07 | 보고서 버전 · 상태 | 반려 보고서를 고칠 수 없음 | API 상태 전이 시험 |
| AC-12 앱별 역할 로그인 | FLOW-02 · 07 | 세션(로그인) | 다른 역할 로그인 성공 | API 음성 시험(앱 × 역할 4조합) |
| AC-13 새 알람 5초 안 | FLOW-01 · 02 | 알람 · 배정 | 5초 넘게 안 보임 | E2E(주기 조회 5초, EP-C1-SYNC-001) |
| AC-14 이어서 하기 | FLOW-02 | 세션 단계(durable) | 다시 연 뒤 단계 · 잠금 시각 · 입력이 다름 | 통합 시험(API 재시작 뒤 재개) + E2E |
| AC-15 평가 데이터 분리 | FLOW-11 · 12 | 이력 색인 | 교집합 > 0, 처리 코드가 평가 폴더를 읽음, 원인 필터 있음 | 정적 검사 + 분리 검사 스크립트 + 누수 음성 시험(EP-PACK-DATA-002) |
| AC-16 키 없이 시연 10건 | FLOW-11 · 06 | 보고서 10건 | 외부 호출 > 0, 각본 중단 | fixture 모드 각본 실행 + 외부 호출 0 검사(네트워크 차단) |
| AC-17 화면 대조 | 모든 UI flow | 없음 | Region · 버튼 · 순서 불일치, 값이 가이드 예시 | Prototype `compiled_structure_contract` 대조 체크리스트 + surface별 E2E 스냅숏 |
| AC-18 평가 지표 | FLOW-12 | 평가 결과 | 지표 · 목표 누락 | 평가 실행기 출력 schema 시험(값 미달도 보고) |
| AC-19 확인 불가 반복 | FLOW-03 | 세션 단계 | 순위 변화, 2회 뒤 재지시, 대안 없을 때 인계 없음 | 표 기반 unit |
| AC-20 맞지 않는 소견 | FLOW-03 | 해석 기록 | 순위 변화, 고르기 전 인계 | unit + component |
| AC-21 재가동 체크리스트 · 여전히 밖 | FLOW-04 | 재가동 · 확인 기록 | 미확인에도 재가동, '여전히 밖'인데 인계 없음 | API 상태 전이 시험 + component |
| AC-22 후보 소진 + 경계 이내 | FLOW-04 | 감시 마감 | 원인이 '이상 없음 · 감시'가 아님 | unit + API 시험 |
| AC-23 호출 답 반영 | FLOW-05 · 08 | 답 · 처리 메모 · 보고서 | 답이 정비자 앱 · 보고서에 없음, D에 '승인 후 진행' | API 시험 + 두 앱 E2E 1개 |
| AC-24 반려 사유 필수 | FLOW-07 | 결정 저장 | 사유 없이 저장 | API 음성 시험 |
| AC-25 등급 변경 | FLOW-09 | 등급표 · 변경 기록 | 경고 없이 저장, 열린 화면이 바뀜, 다음 판정에 미적용 | API 시험 + component(경고) + 통합(진행 중 세션) |
| AC-26 감사 기록 필터 | FLOW-10 | 없음(조회) | 종류 누락, 필터 불일치 | API 시험(고정 fixture) |
| AC-27 승인 대기 목록 | FLOW-07 | 없음(조회) | 타일 숫자 ≠ 건수, 행 항목 누락 | API 시험 + component(빈 목록) |
| AC-28 배정 규칙 | FLOW-01 | 배정 | 규칙 밖 배정 | 표 기반 unit |
| AC-29 근거 적음 | FLOW-03 · 06 · 07 | 표시 플래그 | 세 화면 중 누락, 지시 중단 | unit(기준 3건) + API 시험 |
| AC-30 호출하지 않고 대기 | FLOW-05 | 세션 대기 | 호출이 보내짐 | API 시험 |
| AC-31 LLM · 검색 실패 | FLOW-03 | 대체 표시 · 실패 수 | 진행 막힘, 3회 뒤 권함 없음 | 가짜 provider 실패 주입 unit(EP-INTEG-001) |
| AC-32 조치 등급 | FLOW-04 | 조치 완료 시각 | B 조치가 체크 없이 진행 | API 시험 + component |
| AC-33 확정 뒤 수정 불가 | FLOW-06 | 없음(거부) | 확정 보고서 수정 성공 | API 음성 시험 |
| AC-34 시연 알람 등록 | FLOW-01 | 알람 | 시각 · 센서 값 불일치, 각본 행이 이력 · 카드와 겹침 | CLI 시험 + 분리 검사 |
| AC-35 건너뛰기 불가 | FLOW-03 | 없음(거부) | 지시 밖 결과 접수 | API 음성 시험 |
| AC-36 비밀 원문 없음 | FLOW-11 | 계정 기록 | 저장소 · 적재 기록에 원문 | 비밀값 스캔 + 적재 뒤 DB 검사(가짜 secret 주입, EP-TEST-003) |
| AC-37 종 목록 | FLOW-13 | 없음(조회) | 종류 누락, 이동 오류, 빈 목록 안내 없음 | API 시험 + E2E |
| AC-38 과거 기록 전체 | FLOW-03 | 없음(조회) | 기록 항목 불일치, 닫은 뒤 단계 바뀜 | API 시험 + component |
| AC-39 매뉴얼 원문 | FLOW-03 | 없음(조회) | 절 불일치 | API 시험 |
| AC-40 근거 n 기준 | FLOW-03 | 없음(표시) | 기준 문구 없음 | component |
| AC-41 지난 화면 보기 | FLOW-14 | 없음(조회), 보내지 않은 입력은 기기에만 | 그때 값과 다름, 현재 단계 바뀜, 보기로 건너뛰기 | 세션 단계 조회 API 시험 + component + tech E2E |
| AC-42 승인 C 점검 결과 뒤 | FLOW-03 · 05 | 세션 단계 | 규칙 밖 다음 단계 | 표 기반 unit |
| AC-43 B 시작 전 체크리스트 | FLOW-03 · 04 | B 체크 기록 | 미확인에도 결과 입력 · 진행 | API 음성 시험 + component |
| AC-44 상단 홈 | FLOW-02 | 없음(보내지 않은 입력은 기기) | 버튼 없음, 돌아왔을 때 입력 사라짐 | component + tech E2E |
| AC-45 정정 · 감사 | FLOW-14 · 10 | 정정 덧붙임 기록 · 감사(G3 서버 부분 AC-45-C3) | 원래 값 사라짐, 사유 없이 저장, 감사 항목 누락 | API 시험(덧붙임 · 감사 5항목) + 통합(파트장 감사 조회) |
| AC-46 정정 뒤 다시 판정 | FLOW-14 | 뒤 기록 무효 표시 | 다시 판정 결과 ≠ R4 · R5 재적용, 뒤 기록 삭제 | 표 기반 unit(정정 지점 재판정) + API 시험 |
| AC-47 조치 · 보낸 호출 뒤 정정 | FLOW-14 · 08 | 호출 요약 / 호출에 정정 첨부 | 다시 판정함, 새 호출 생성 | API 시험 + 두 앱 E2E 1개 |
| AC-48 정정 불가 기록 · 확정 세션 | FLOW-14 | 없음(거부, G3 서버 부분 C1 · C2) | 서버가 정정 요청 접수 | API 음성 시험(기록 종류 7 × 세션 상태) |

## Candidate methods and evidence

Playbook(PBC-1의 유일한 기술 지식 입력, Wiki 원문은 복제하지 않음):

| Playbook | Path | Version | SHA-256 | 검토일 |
| --- | --- | --- | --- | --- |
| C1-a15 보충 | `/Users/insujo/Documents/repo/c1a15-maint-guide/.vibe-factory/playbooks/engineering-playbook-c1a15-supplement-v3.md` | c1a15-supplement-v3 | `f68cb6ca18ddb99802037fc82bcd6d06039b9856801635b13b264a4e3f36b0a4` | 2026-10-12(사용자 결정 9개 반영, '내용 그대로 사용 승인') |
| 기본 | `/Users/insujo/Documents/repo/llmops-lite-v2/.vibe-factory/playbooks/engineering-playbook-v1.md` | v1 | `018da82df11eff7921fabd771d0bc8641ad2887f3ce59c90df8a365b829e3d73` | 작성 2026-10-01, 사용 승인 2026-10-12 |
| pack 보충 | `/Users/insujo/Documents/repo/task10-pack/.vibe-factory/playbooks/engineering-playbook-pack-supplement-v1.md` | pack-supplement-v1 | `48fa80df00d339823caea75c451ec552047c770b81e801ee101a9d57757add1d` | 작성 2026-10-05, 사용 승인 2026-10-12(DATA-001~003 · RET-001~002 · EVAL-001만) |

후보(채택 · 제외). PBC-2 Selection Register가 이 표를 기록 단위로 옮긴다.

| 범주 | 채택 후보 | 근거 rule ID | 제외 후보 · 이유 |
| --- | --- | --- | --- |
| 구조 | modular monolith: API 서버 1개(FastAPI) + agent 패키지, 두 앱 별도 빌드 | EP-WORKFLOW-001, EP-C1-SURFACE-001, EP-C1-RUN-001 | 서비스 분리 — 독립 scale · 배포 · 보안 경계가 관찰되지 않음 |
| 흐름 제어 | 판정은 결정적 순수 함수(R1~R13 계열), 세션 흐름은 state machine + guard. LangGraph는 명세(사용자 결정)대로 interrupt · checkpoint 껍데기로만, 업무 사실은 append-only 업무 기록 | EP-C1-RULE-001, EP-GRAPH-001, EP-GRAPH-003, EP-C1-HITL-001 | single agent · multi-agent — 경로 · 순서가 정해져 있고 LLM은 문장만 씀(EP-WORKFLOW-001). checkpoint를 감사 정본으로 쓰기 — EP-C1-HITL-001이 금지 |
| 데이터 | PostgreSQL 1개 · `ops` / `knowledge` schema · pgvector, SQLAlchemy + Alembic, 적재기 | EP-C1-DB-001, EP-C1-MIG-001, EP-STATE-001, EP-PACK-DATA-001, EP-PACK-DATA-003 | 번호 SQL 파일 — 사용자 결정으로 제외 |
| 검색 | 같은 증상군 필터 → BM25(글자 2-gram, 메모리 색인) + pgvector → RRF k=60 → 정규화 센서 거리 재정렬 | EP-C1-RET-001, EP-C1-FUSE-001, EP-PACK-RET-001, EP-PACK-RET-002 | 형태소 분석 — 평가 결과가 나쁠 때만 재검토 |
| LLM | LLM Adapter, `APP_MODE=fixture` 기본, live는 승인 뒤, 구조화 출력 + 근거 검사, 모델 ID는 설정 | EP-C1-LLM-001, EP-INTEG-001, EP-MODEL-001, EP-OPS-001 | 판정에 LLM 사용 — Authority boundary가 금지 |
| API 계약 | OpenAPI 정본 → openapi-typescript 타입 + openapi-fetch | EP-C1-API-001, EP-C1-APITYPE-001 | orval — 사용자 결정으로 제외 |
| 프론트 | React + TypeScript + Vite(명세), npm workspaces(apps/tech · apps/lead · packages/ui), Prototype 화면 · 토큰이 판정 기준 | EP-C1-SURFACE-001, EP-C1-WS-001, EP-FE-001, EP-STATE-001 | pnpm — 사용자 결정으로 제외 |
| 인증 | argon2id + 서버 세션 쿠키(앱별 이름, 12시간), 서버가 앱 · 역할 검사 | EP-C1-AUTH-001, EP-C1-AUTH-002 | bcrypt + JWT · OIDC — 사용자 결정 · 범위 밖 |
| 갱신 | 주기 조회 5 · 3 · 10초 + 변경 순번 | EP-C1-SYNC-001 | SSE · WebSocket — 측정된 필요 없음 |
| 웹 · 실행 | nginx 1개 · 8081/8082 server 블록 · 각자 `/api` 중계, Docker Compose db → init → api → web | EP-C1-WEB-001, EP-C1-RUN-001, EP-OPS-003 | 한 포트 경로 분리 — 사용자 결정으로 제외. canary · SBOM — 배포 없는 local 시연(EP-OPS-003) |
| 시험 | unit · 표 기반 · property(규칙), API · 통합(실제 PostgreSQL 컨테이너), contract(OpenAPI diff), Playwright TypeScript E2E(surface별 journey + 두 앱 호출 1개), 음성 · 누수 · 비밀값 시험, 평가 실행기 | EP-TEST-001, EP-TEST-002, EP-TEST-003, EP-C1-E2E-001, EP-C1-E2E-002, EP-PACK-EVAL-001, EP-PACK-DATA-002 | 모든 규칙을 E2E로 — EP-TEST-001이 금지. Playwright Python — 사용자 결정으로 제외 |
| 관측 | request-id 기반 안전 로그, 비밀값 없음 | EP-OPS-002 | 별도 trace 시스템 — 운영 배포 없음 |
| 개발 harness | 짧은 repo `CLAUDE.md` + `scripts/check-fast` · `scripts/verify-e2e`, 실행 전 capability preflight, act → verify → repair loop(반복 상한) | EP-HARNESS-001, EP-HARNESS-002, EP-LOOP-001, EP-GEN-002 | hook · MCP · worktree 병렬 write — 관찰된 필요 없음, 같은 파일 · DB 포트 공유(EP-HOOK-001, EP-MCP-001, EP-WORKTREE-001) |
| Python 환경 | uv 프로젝트(`pyproject.toml` + `uv.lock`), Python 3.12 고정, Docker image도 같은 lock | EP-C1-PY-001, EP-OPS-003 | venv + pip · Python 3.14 — 사용자 결정으로 제외 |
| 개발 model · Skill | 현재 환경 model 그대로, 품질은 verifier + 독립 critic. Skill은 설치된 것만(구체 목록은 PBC-2에서 현재 environment 확인) | EP-MODEL-002, EP-SKILL-001, EP-SUBAGENT-001 | 새 Skill · plugin 제작 — 근거 없음 |

**열린 항목:** 없음. 조사 중 나온 아홉 번째 빈 규칙(Python 환경)은 사용자 결정으로 Playbook 보충판 v3(EP-C1-PY-001)에 넣었고, 이 문서는 v3 기준이다(`discovery/pbc1-user-decisions.md`).

## Spike decision

spike 없음. 불확실한 것은 승인 뒤 첫 구현 slice가 확인한다.

- LangGraph PostgreSQL checkpointer의 현재 API · Python 3.12 호환, pgvector 임베딩 차원(256), OpenAI 모델 이름: 첫 slice의 capability preflight(EP-HARNESS-002)와 공식 문서 재확인(Playbook Currency review).
- 글자 2-gram + RRF 품질: 평가 실행기 slice(FLOW-12)가 측정한다.
- live OpenAI smoke: 사용자 승인 뒤 격리된 소수 호출만(EP-C1-LLM-001). PBC 중에는 하지 않는다.

## Coupled-control feasibility

둘 이상의 제어장치가 함께 성립해야 하는 곳이 두 군데 있어 `not_required`로 둘 수 없다. PBC-2에서 plan item이 정해진 뒤 internal compatibility probe로 확인하고, `feasibility-probe.json`과 Coding Plan `feasibility_preflight`(status verified)에 잠근다.

| 예정 ID | 함께 성립해야 하는 제어 | material_to | 임시 격리 · 명령 개요 | 실행 조건 |
| --- | --- | --- | --- | --- |
| FP-01 | nginx 앱별 server 블록이 붙이는 앱 표시 header(클라이언트가 보낸 값은 덮어씀) + Compose 내부망(API 포트를 밖에 열지 않음) + 서버의 앱 · 역할 검사 + 앱별 쿠키 이름. 쿠키는 host 단위라 8081 · 8082가 쿠키를 나눠 가지므로, 쿠키만으로는 앱을 가를 수 없음 | authority_boundary(AC-12 · 앱별 역할) | 임시 폴더에서 로컬 image nginx:latest + node:18(header를 되돌려 주는 stub 서버, 제품 코드 아님)로 두 포트를 띄우고, 위조 header · 다른 앱 쿠키 요청이 stub에 어떻게 닿는지 관찰한 뒤 컨테이너 · 폴더 삭제 | 사용자 승인(2026-10-12, 로컬 image로 실행). 외부 연결 · pull 없음 |
| FP-02 | Playwright 두 browser context(정비자 · 파트장) + Compose 테스트 DB 초기화 + fixture 모드 네트워크 차단(외부 호출 0) | verifier(AC-13 · 16 · 23 · 47 E2E, AC-16-C2) | 임시 workspace에 Playwright 패키지를 받아(캐시 브라우저 사용) 정적 stub 두 개와 차단 규칙으로 두 context · 외부 요청 차단 관찰 | 사용자 승인(2026-10-12, 저장소 밖 임시 폴더에만 @playwright/test 내려받기). 그 밖 외부 호출 없음 |

## Revalidation triggers

- `discovery/planning-baseline.json` v2의 저장소 HEAD · 의존성 revision이 바뀔 때(첫 slice가 lockfile을 만들면 PBC-4 승인 범위 안에서만)
- 세 Playbook 중 하나의 hash가 바뀔 때(그 판부터 PBC-1을 다시 기록)
- `data/manifest.json` · `data/alarm_rules.json` hash가 바뀔 때
- 선택한 framework(FastAPI · LangGraph · SQLAlchemy · Alembic · React · Vite · Playwright)의 주 버전이나 OpenAI 모델 · 임베딩 차원이 바뀔 때
- FP-01 · FP-02가 pass하지 못할 때(해당 plan item 승인 불가)
- 승인 입력(Use Case Bundle v6 · Prototype Bundle v16)이 바뀔 때 — 그때는 PBC-0부터 다시
