# Engineering Playbook — C1-a15 정비 길잡이 보충 v4

> PBC에서 C1-a15 구현 방법을 고를 때 쓰는 판단 규칙이다. 제품 동작·AC·권한·데이터 의미·화면 약속을 바꾸는 근거가 될 수 없다.
> 일반 규칙은 아래 두 문서를 그대로 쓰고, 이 문서는 두 문서에 없는 C1-a15 규칙만 더한다. Selection Register는 세 문서의 규칙 ID를 함께 인용할 수 있다.
> - **v1**: `/Users/insujo/Documents/repo/llmops-lite-v2/.vibe-factory/playbooks/engineering-playbook-v1.md` (SHA-256 `018da82df11eff7921fabd771d0bc8641ad2887f3ce59c90df8a365b829e3d73`)
> - **pack-supplement-v1**: `/Users/insujo/Documents/repo/task10-pack/.vibe-factory/playbooks/engineering-playbook-pack-supplement-v1.md` (SHA-256 `48fa80df00d339823caea75c451ec552047c770b81e801ee101a9d57757add1d`) — 이 문서의 EP-PACK-DATA-001/002/003, EP-PACK-RET-001/002, EP-PACK-EVAL-001만 C1-a15에 적용한다(Pack IR·Pack 그래프·task10-pack 실행 환경 규칙은 적용하지 않음).
>
> v4(2026-10-12): 규칙 내용은 v3와 같다. Selection Register가 이 문서 하나를 Playbook으로 고정하고 기본 v1 · pack-supplement-v1의 규칙 ID도 인용하므로, 인용할 수 있는 두 문서의 규칙 ID · 이름을 아래 '함께 쓰는 규칙 ID 목록'에 그대로 옮겼다(규칙 본문은 각 원본이 정본). v3: `engineering-playbook-c1a15-supplement-v3.md`(SHA-256 `f68cb6ca18ddb99802037fc82bcd6d06039b9856801635b13b264a4e3f36b0a4`).
>
> v3(2026-10-12): PBC-1 조사 중 나온 아홉 번째 빈 규칙(Python 환경 · 의존성 고정)을 사용자 결정으로 채웠다(EP-C1-PY-001). v2: `engineering-playbook-c1a15-supplement-v2.md`(SHA-256 `8de3736a176b87f5e47e35b52f96ea02d2e8a3c5ebcdd36f545802c4ace4d7c6`).
>
> v2(2026-10-12): v1의 Currency review가 남긴 'Wiki 근거 없는 선택 8개'를 사용자 결정으로 채웠다(아래 EP-C1-WS-001 ~ EP-C1-E2E-002, 근거 = 사용자 결정, Wiki 근거 없음). v1 규칙 10개는 문장 그대로 두고 한계 문장에 v2 규칙을 가리키는 말만 더했다. v1: `engineering-playbook-c1a15-supplement-v1.md`(SHA-256 `27eff759a7910bdc42af6db675da63d699b55e312f0a1f501d550691020ad506`).
>
> 위치: 템플릿은 Wiki 안 장기 문서로 정의하지만, Wiki는 사용자 요청 전까지 읽기만 하는 약속(2026-10-09) 때문에 프로젝트 `.vibe-factory/playbooks/`에 둔다. Wiki로 옮길지는 사용자가 정한다.

## Metadata

- Version: `c1a15-supplement-v4`
- Reviewed at: `2026-10-12T00:00:00+09:00`
- Review owner: `사용자(프로젝트 소유자) — 작성: Claude Code. 2026-10-12 사용자가 이 판과 함께 쓰는 v1 · pack-supplement-v1을 '내용 그대로 사용 승인'(규칙별 검토는 하지 않음, VCF run 2026-10-11-c1a15-product-r2 discovery/pbc1-user-decisions.md). 다른 저장소의 두 Playbook 파일은 고치지 않고 이 승인을 여기에만 적는다`
- Scope: implementation method selection only; it cannot change product behavior, AC, authority, data meaning, or UI promises.
- Wiki root: `/Users/insujo/Documents/repo/ob-rep-sv1` (HEAD `43af7ac`)
- 제품 기준: `docs/spec/C1-a15-구현-명세.md` v1.0 (결정 D1~D19). 이 Playbook은 그 결정을 바꾸지 않는다.

## Source documents

| Source path | Section / anchor | Why it is authoritative | Checked at |
| --- | --- | --- | --- |
| `wiki/concepts/current-implementation-planning-engineering-reference.md` | `## 3. Agent·Workflow·Graph Engineering`, `## 4. Architecture·상태·통합 계약`, `## 5. Frontend·Accessibility·Test Strategy`, `## 6. Performance·Resilience·Operations` | 공식 current source(LangGraph, OpenAPI, RFC 9110, Playwright, OpenAI eval, SRE 등)를 우선해 정리한 구현 계획 정본 | 2026-10-11 |
| `wiki/capstone/claude-code-program-delivery-playbooks.md` | `## 1. Greenfield web / mobile MVP`, `## 3. API / data / FastAPI backend`, `## 4. AI Agent / RAG / MCP product`, `## 4층 완료 정의` | 프로그램 유형별 입력·순서·evidence | 2026-10-11 |
| `wiki/academy/2026-09-18-agent-workflow-lab-live-rag-update.md` | `### 2. live RAG가 실제 adapter로 분리됨`, `## 해석·학습 의미` | fixture 기본·live 분리, OpenAI+pgvector adapter, 503 오류 구분, fixture 성공을 live 증거로 승격 금지 | 2026-10-11 |
| `wiki/academy/levelled-rag-multi-agent-practice-curriculum.md` | `## 로컬 live 환경`, `## 2026-09-18 구현 상태 갱신` | Docker Compose pgvector → extension → 임베딩 seed → 검색 → LangGraph → FastAPI 순서 | 2026-10-11 |
| `wiki/academy/2026-09-21-post-basic-rag-curriculum-gap-analysis.md` | `## 1. Advanced RAG — 가장 큰 공백`, `## 3. Multi-Agent·LangGraph·HITL` | Hybrid(BM25 + dense) + rank fusion, interrupt·checkpointer·thread ID·resume가 필요한 기능으로 정리됨(구현 예는 없음) | 2026-10-11 |
| `wiki/capstone/enterprise-retrieval-strategy-conflicting-claims-experiment.md` | `## 확인된 사실`, `## 참가자 주장 또는 결정` | 작은 corpus에서 lexical(BM25)·retrieval-first 판단 근거 | 2026-10-11 |
| `wiki/queries/2026-10-03-agent-pack-spec-v0-2-followup-review.md` | `## 반영 확인` | 사람 검토 = checkpoint/pause/resume, append-only review event, 수정 뒤 재검증 | 2026-10-11 |
| 사용자 결정(Wiki 아님): VCF run `2026-10-11-c1a15-product-r2` `discovery/pbc1-user-decisions.md` | 질문 9개와 답 | Wiki에 근거가 없는 선택을 프로젝트 소유자가 정함. 근거의 성격은 '결정'이지 검증된 지식이 아니므로 각 규칙의 검증 · 재검토 조건으로 확인한다 | 2026-10-12 |

## 함께 쓰는 규칙 ID 목록

규칙 본문은 원본 문서가 정본이다(경로 · SHA-256은 머리말). 이 목록은 Selection Register가 인용할 수 있는 ID를 이 문서 안에서 찾게 하려는 색인이며 규칙을 바꾸지 않는다.

| 원본 | 규칙 ID | 이름(원본 제목 그대로) |
| --- | --- | --- |
| v1 | `EP-GEN-001` | 선택의 공통 순서 |
| v1 | `EP-GEN-002` | vertical slice 순서와 4층 완료 |
| v1 | `EP-HARNESS-001` | repo harness (guide + sensor) |
| v1 | `EP-HARNESS-002` | 실행 전 capability preflight |
| v1 | `EP-LOOP-001` | act → verify → repair loop |
| v1 | `EP-WORKFLOW-001` | workflow / single agent / multi-agent 선택 |
| v1 | `EP-GRAPH-001` | state machine과 execution graph 계약 |
| v1 | `EP-GRAPH-002` | 병렬 fan-out / 동시 실행 |
| v1 | `EP-GRAPH-003` | side effect, idempotency, HITL |
| v1 | `EP-SUBAGENT-001` | subagent 사용 |
| v1 | `EP-HOOK-001` | hook 사용 |
| v1 | `EP-MCP-001` | MCP 사용 |
| v1 | `EP-WORKTREE-001` | worktree / 병렬 write |
| v1 | `EP-STATE-001` | 상태·데이터 계약 |
| v1 | `EP-INTEG-001` | 외부 integration·provider 경계 |
| v1 | `EP-TEST-001` | test 전략 선택 |
| v1 | `EP-TEST-002` | AI 출력 평가 |
| v1 | `EP-TEST-003` | negative·adversarial verifier와 judge 검증 |
| v1 | `EP-FE-001` | frontend 구현·검증 |
| v1 | `EP-OPS-001` | timeout·retry·취소 |
| v1 | `EP-OPS-002` | 관측·로그 |
| v1 | `EP-OPS-003` | release·rollback·provenance 적용 범위 |
| v1 | `EP-SKILL-001` | Skill·extension 선택 |
| v1 | `EP-MODEL-001` | 제품 안의 model 역할 |
| v1 | `EP-MODEL-002` | 개발용 model 역할 (구현·검토 Agent) |
| pack-supplement-v1 | `EP-PACK-DATA-001` | 원본 파생과 split manifest |
| pack-supplement-v1 | `EP-PACK-DATA-002` | 정답 누수 방지 검사 |
| pack-supplement-v1 | `EP-PACK-DATA-003` | 가상(synthetic) corpus 생성 |
| pack-supplement-v1 | `EP-PACK-RET-001` | 수치 사례 검색(정규화 거리) |
| pack-supplement-v1 | `EP-PACK-RET-002` | 문서 검색(벡터 색인) |
| pack-supplement-v1 | `EP-PACK-EVAL-001` | 평가셋과 node별 정답지 |

## Decision rules

### EP-C1-SURFACE-001 — 출시 UI surface 2개와 공통 패키지

- Situation / requirement signals: 서로 다른 사용자·기기의 UI 제품이 둘 이상(정비자 태블릿 앱, 파트장 PC 앱)이고 같은 API·데이터를 쓴다(명세 D3).
- Recommended approach: 앱마다 독립 빌드 단위(별도 entry·route·build output)를 두고, 상단 바·등급 배지·기록 카드·API 클라이언트만 공통 패키지로 묶는다. 앱끼리 서로의 화면 코드를 import하지 않는다. 화면 판정 기준은 사용 가이드 HTML(v1 EP-FE-001: 기존 mockup이 진실의 기준). 앱별로 normal/narrow 화면과 핵심 journey를 따로 검증한다.
- Do not use when: 한 사용자·한 기기 UI뿐일 때(공통 패키지 없이 앱 하나).
- Preconditions and authority boundary: 공통 패키지에 한 앱 전용 업무 로직을 넣지 않는다. 앱 이름·역할·로그인 범위는 명세 D3·D9를 따른다.
- Verification and stop condition: 두 앱 각각 빌드·타입 검사·E2E(EP-C1-E2E-001) 통과, 한 앱 변경이 다른 앱 빌드를 깨지 않음, 공통 패키지 변경 시 두 앱 모두 재검증.
- Revalidate when: UI surface가 늘거나 합쳐질 때, 프론트엔드 도구 버전이 바뀔 때.
- Wiki basis: `current-implementation-planning-engineering-reference.md` `## 5.`(server data/local UI state, 원격 state AC); `claude-code-program-delivery-playbooks.md` `## 1. Greenfield web / mobile MVP`; v1 EP-FE-001. **한계:** React·TypeScript·Vite·workspace 구성 자체에 대한 Wiki 근거는 없다 — workspace 방식은 v2 EP-C1-WS-001(사용자 결정).

### EP-C1-API-001 — OpenAPI 계약이 정본, 앱 타입은 계약에서 생성

- Situation / requirement signals: 백엔드 하나를 프론트엔드 둘이 부르고, 보고서 8항목·세션 상태 같은 구조 데이터가 오간다.
- Recommended approach: FastAPI의 Pydantic 모델에서 나온 OpenAPI 문서를 버전 관리되는 계약으로 두고, 공통 패키지의 API 클라이언트 타입은 그 계약에서 생성한다. 계약에 인증·오류 형식·재시도 가능 여부를 포함한다. 생성물은 손으로 고치지 않는다.
- Do not use when: 앱과 서버가 같은 언어 단일 프로세스여서 계약 경계가 없을 때.
- Preconditions and authority boundary: 엔드포인트·필드 의미는 명세 6장·10장의 결정을 따르고, 계약 생성 도구가 의미를 바꾸지 않는다.
- Verification and stop condition: 계약 파일 diff가 서버 코드와 일치(생성 후 변경 없음 검사), 계약 기반 contract test 통과, 타입 생성 후 두 앱 타입 검사 통과. 계약이 깨지면 다음 slice 시작 금지.
- Revalidate when: 엔드포인트·스키마가 바뀔 때.
- Wiki basis: `current-implementation-planning-engineering-reference.md` `## 4.`(version-controlled OpenAPI contract를 source of truth로, auth·error·retry/idempotency 포함). **한계:** 타입 생성 도구 선택 근거는 Wiki에 없다 — v2 EP-C1-APITYPE-001(사용자 결정).

### EP-C1-RULE-001 — 판정 규칙은 결정적 함수 + 표 기반 테스트

- Situation / requirement signals: 원인 순위, 다음 점검 선택, 호출 조건, 권한 판정, 잠금 선행, 근거 검사처럼 명세가 "코드가 판정"으로 정한 규칙(명세 4장 R1~R13).
- Recommended approach: 규칙을 LLM·DB·네트워크에 의존하지 않는 순수 함수로 두고, LangGraph node는 이 함수를 호출만 한다. 명세의 계산 예시(R5)를 그대로 고정 입력 테스트로 만들고, 입력 공간이 넓은 규칙(확률 합 100, 후보 제거 후 재정규화)은 property-based 테스트를 더한다. LLM은 후보·문장만 제안한다.
- Do not use when: 해당 없음(C1-a15 판정 규칙 전부에 적용).
- Preconditions and authority boundary: 규칙 값(α, 호출 기준 50%, 근거 적음 기준)은 설정 값으로 두되 기본값은 명세를 따른다. 구현에서 공식을 바꾸지 않는다(바꾸려면 명세 변경).
- Verification and stop condition: R5 계산 예시 테스트 통과(첫 지시 4.3, 4.3 정상 뒤 호출), 확률 합 100 property 통과, 잠금 전 지시·C·D 지시가 나가는 음성 테스트가 실패해야 함(v1 EP-TEST-003).
- Revalidate when: 명세 규칙·기본값이 바뀔 때.
- Wiki basis: `current-implementation-planning-engineering-reference.md` `## 3.`(고위험 전이는 deterministic guard, LLM은 후보 제안), `## 5.`(property-based는 입력 공간이 넓고 invariant가 명확한 규칙); v1 EP-TEST-001·EP-TEST-003.

### EP-C1-HITL-001 — 점검 세션의 중단·재개(checkpoint)와 업무 기록

- Situation / requirement signals: 정비자 입력·파트장 답을 기다리며 세션이 멈췄다가 이어져야 하고, 앱을 닫아도 같은 단계에서 계속돼야 한다(명세 S1·S5, AC-14).
- Recommended approach: LangGraph의 interrupt·checkpoint를 PostgreSQL에 저장하고 세션마다 thread ID를 둔다. checkpoint 재개 시 node가 다시 실행될 수 있으므로, 화면에 보이는 업무 사실(잠금·점검 결과·호출·보고서 확정)은 checkpoint와 별도로 append-only 업무 기록(`session_steps`·`calls`·`audit_log`)에 남기고, 쓰기에는 업무 idempotency key(세션 ID + 단계 순번)를 붙인다. 파트장 수정은 수정 뒤 근거 재검사를 거친다(명세 D18).
- Do not use when: 한 요청 안에서 끝나는 처리(중단 없음).
- Preconditions and authority boundary: checkpoint는 재개 장치일 뿐 감사 정본이 아니다. 감사·보고서는 업무 기록에서 만든다. framework API(체크포인터 클래스·설정)는 구현 시점 공식 문서로 다시 확인한다.
- Verification and stop condition: 중간 단계에서 프로세스를 재시작해도 같은 단계·같은 순위로 재개(L3), 같은 입력을 두 번 보내도 업무 기록이 한 번만 남음, 재개 뒤 잠금 상태가 유지됨.
- Revalidate when: LangGraph 버전·체크포인터 저장소가 바뀔 때.
- Wiki basis: `current-implementation-planning-engineering-reference.md` `## 3.`(checkpoint/resume 뒤 재실행 가능 → business idempotency key와 execution ledger, HITL 위치·approval payload); `2026-09-21-post-basic-rag-curriculum-gap-analysis.md` `## 3.`(interrupt·checkpointer·thread ID·resume); `2026-10-03-agent-pack-spec-v0-2-followup-review.md` `## 반영 확인`(append-only review event, edit 후 revalidation).

### EP-C1-DB-001 — PostgreSQL 1개, schema 2개, pgvector

- Situation / requirement signals: 운영 데이터(세션·보고서·감사·등급표)와 지식 데이터(매뉴얼 절·이력 + 임베딩)를 용도별로 나누되 한 인스턴스에 둔다(명세 D2).
- Recommended approach: PostgreSQL 하나에 `ops`·`knowledge` schema, `knowledge`에만 pgvector extension 사용. 접근은 agent 패키지의 DB 접근 계층 한 곳에서만. 스키마 변경은 버전 관리되는 migration으로 하고, 적재 스크립트가 seed(매뉴얼·이력·임베딩·초기 등급표·계정·설비 담당표)를 넣는다. Docker Compose의 DB는 healthcheck 뒤 적재.
- Do not use when: 저장소가 하나의 용도뿐일 때.
- Preconditions and authority boundary: 앱(브라우저)은 DB에 직접 붙지 않는다. 적재·migration은 운영 외 작업(점선)으로 실행한다.
- Verification and stop condition: migration 적용·되돌리기 명령이 깨끗한 DB에서 통과, 적재 후 건수(매뉴얼 절·이력 300건) 일치, pgvector extension 존재 확인, 테스트는 실제 PostgreSQL(컨테이너)로.
- Revalidate when: schema·임베딩 차원·PostgreSQL/pgvector 버전이 바뀔 때.
- Wiki basis: `levelled-rag-multi-agent-practice-curriculum.md` `## 로컬 live 환경`(Compose pgvector → extension → seed); `current-implementation-planning-engineering-reference.md` `## 4.`(data를 소유하는 경계, modular monolith 기본); `claude-code-program-delivery-playbooks.md` `## 3. API / data / FastAPI backend`(seed/migration/rollback evidence). **한계:** schema 분리·migration 도구 선택에 대한 Wiki 근거는 없다 — migration 도구는 v2 EP-C1-MIG-001(사용자 결정).

### EP-C1-RET-001 — 비슷한 기록 검색: BM25 + pgvector 융합 후 센서 거리 재정렬

- Situation / requirement signals: 과거 정비 기록이 서술(교대 일지체)과 수치(센서 값)를 함께 가진다. 명세 R3.
- Recommended approach: 같은 증상군으로 먼저 거르고, 서술에 대한 키워드(BM25, agent 패키지 메모리 색인)와 의미(pgvector) 결과를 순위 융합해 상위 10건을 만든 뒤 pack-supplement EP-PACK-RET-001의 정규화 거리로 다시 정렬한다. 승인 보고서가 추가되면 두 색인을 함께 갱신(평가 모드 제외). 테스트는 가짜 임베딩(결정적)으로.
- Do not use when: 서술이 없거나 수치만 있는 기록(EP-PACK-RET-001 단독).
- Preconditions and authority boundary: 원인 필드를 검색 필터로 쓰지 않는다(정답 누수, EP-PACK-DATA-002). 실제 임베딩 호출은 live 모드 승인 뒤.
- Verification and stop condition: 고정 이력·고정 질의로 상위 10건과 순서 고정 테스트, 같은 원인 필터를 넣으면 누수 검사가 실패하는 음성 테스트, 승인 후 재검색에 새 기록이 나타남(AC-09), 평가 모드에서는 나타나지 않음.
- Revalidate when: 이력 구성·토큰 규칙·융합 가중치·임베딩 모델이 바뀔 때.
- Wiki basis: `2026-09-21-post-basic-rag-curriculum-gap-analysis.md` `## 1.`(BM25/lexical + dense Hybrid와 rank fusion); `enterprise-retrieval-strategy-conflicting-claims-experiment.md` `## 확인된 사실`(작은 corpus에서 lexical 우위); pack-supplement EP-PACK-RET-001. **한계:** RRF 식·k 값, 한국어 토큰화(형태소 / n-gram) 선택에 대한 Wiki 근거는 없다 — v2 EP-C1-FUSE-001(사용자 결정)을 쓰고 평가로 확인한다.

### EP-C1-LLM-001 — fixture 기본, live는 승인 뒤, LLM은 문장만

- Situation / requirement signals: 지시문·고른 이유·메모 해석·보고서 문장·호출 요약에 LLM을 쓰고, 키 없이도 시연·평가가 돌아야 한다(명세 D10, AC-16).
- Recommended approach: LLM Adapter 뒤에 OpenAI(대화·임베딩)를 두고 `APP_MODE=fixture`(기본: 템플릿 문장·단어 규칙·녹화 임베딩) / `live`를 나눈다. 모든 LLM 출력은 구조화 출력 + 근거 검사(명세 R8)를 거친다. 설정·provider 오류는 사용자에게 구분된 오류(원문 대체 표시)로 보이고 판정 규칙은 계속 동작한다.
- Do not use when: 해당 없음.
- Preconditions and authority boundary: live 호출·키 사용은 사용자 승인 뒤(키는 필요할 때 사용자에게 요청). fixture 성공을 live 동작의 증거로 승격하지 않는다. 모델 ID는 설정으로(v1 EP-MODEL-001).
- Verification and stop condition: fixture 모드 전체 E2E 통과, 근거 없는 문장이 화면에 나가지 않는 음성 테스트, live는 소수의 격리된 smoke만(승인 뒤).
- Revalidate when: provider·모델·임베딩 차원이 바뀔 때.
- Wiki basis: `2026-09-18-agent-workflow-lab-live-rag-update.md` `### 2.`(fixture 기본, live에서만 OpenAI+pgvector, 오류 구분), `## 해석·학습 의미`(fixture 성공을 live 증거로 승격 금지); v1 EP-INTEG-001·EP-MODEL-001·EP-TEST-002.

### EP-C1-AUTH-001 — 사전 등록 계정과 앱별 역할

- Situation / requirement signals: 계정은 미리 등록, ID·비밀번호 로그인, 정비자 앱은 정비자만·파트장 앱은 파트장만(명세 D9).
- Recommended approach: 비밀번호는 느린 해시(salt 포함)로만 저장하고, 로그인 시 서버가 짧은 수명의 토큰을 발급해 모든 API에서 역할을 검사한다(앱 이름과 역할이 다르면 거부). 감사 기록의 행위자는 토큰의 사용자로만 정한다.
- Do not use when: 외부 사내 SSO를 써야 하는 경우(그때는 OIDC — 현재 범위 밖).
- Preconditions and authority boundary: 토큰·비밀번호를 URL·로그·화면에 남기지 않는다. 시연 계정 비밀번호는 저장소에 평문으로 두지 않는다(적재 시 환경 변수).
- Verification and stop condition: 잘못된 역할 로그인 거부(AC-12), 토큰 없는 API 거부, 다른 사용자의 세션 접근 거부 음성 테스트, 로그에 비밀값 없음 검사.
- Revalidate when: 인증 방식·역할이 바뀔 때.
- Wiki basis: `current-implementation-planning-engineering-reference.md` `## 4.`(auth를 API 계약에 포함, OIDC는 authentication 기본 검토 — 본 제품은 사용자 결정 D9로 로컬 계정 선택). **한계:** 비밀번호 해시·토큰 수명·세션 방식에 대한 Wiki 근거는 없다 — v2 EP-C1-AUTH-002(사용자 결정)가 정한다.

### EP-C1-SYNC-001 — 주기 조회로 새 알람·호출 반영

- Situation / requirement signals: 새 알람·파트장 답·호출을 몇 초 안에 다른 앱에 보여야 한다(명세 S1·S5, AC-13). 사용자 규모가 작다(정비자 수 명, 파트장 1명).
- Recommended approach: 앱이 짧은 주기로 조회(정비자 홈 5초, 세션 3초, 파트장 10초)하고, 서버 응답에 변경 순번을 넣어 바뀐 것만 다시 그린다. 서버 push(SSE·WebSocket)는 조회 부하·지연이 실제 문제로 측정될 때만 검토한다.
- Do not use when: 지연 허용이 1초 미만이거나 사용자 수가 커서 조회 부하가 문제일 때.
- Preconditions and authority boundary: 조회 API는 읽기 전용, 상태 변경은 별도 쓰기 API로만.
- Verification and stop condition: 알람 발생 후 5초 안 표시 E2E(AC-13), 파트장 답 후 정비자 화면 반영 E2E.
- Revalidate when: 사용자 수·지연 요구가 바뀔 때.
- Wiki basis: `current-implementation-planning-engineering-reference.md` `## 4.`(sync는 즉시 결과가 필요한 곳, event는 독립 consumer·비동기가 실제로 필요할 때). **한계:** 조회 주기·SSE/WebSocket 선택 기준에 대한 Wiki 근거는 없다 — 2026-10-12 사용자가 이 규칙의 주기 · 전환 기준을 그대로 쓰기로 결정(근거 = 사용자 결정).

### EP-C1-E2E-001 — UI surface별 끝까지 관통 테스트

- Situation / requirement signals: VCF PBC-3이 첫 end-to-end slice와 surface별 L3(entry → result → readback) 증거를 요구한다.
- Recommended approach: 브라우저 E2E로 정비자 journey(로그인 → 알람 → 진단 → 잠금 → 점검 → 조치 → 재가동 확인 → 보고서 확정)와 파트장 journey(로그인 → 승인 대기 → 검토·승인 → 승인 기록이 다음 알람의 과거 기록으로 다시 읽힘)를 fixture 모드로 돌린다. 네트워크는 통제하고, 데이터는 테스트마다 초기화한다. 파트장 호출은 두 앱을 잇는 하나의 테스트로 검증한다.
- Do not use when: 규칙 하나·컴포넌트 하나 검증(unit·component로 충분, v1 EP-TEST-001).
- Preconditions and authority boundary: 브라우저 테스트 도구 설치는 승인 뒤. live provider는 E2E에서 쓰지 않는다.
- Verification and stop condition: 두 journey 통과 + 콘솔 오류 없음 + 화면 상태 목록(명세 7장) 대조 체크리스트(AC-17). 실패하면 다음 slice 시작 금지.
- Revalidate when: 화면 흐름·API 계약이 바뀔 때.
- Wiki basis: `current-implementation-planning-engineering-reference.md` `## 5.`(E2E는 적은 핵심 journey, test isolation과 controlled network mock); `claude-code-program-delivery-playbooks.md` `## 1. Greenfield web / mobile MVP`(실제 browser flow로 판정), `## 4층 완료 정의`.

### EP-C1-RUN-001 — Docker Compose 실행 구성

- Situation / requirement signals: 웹 서버·API 서버·DB·알람 발생기·적재를 한 번에 띄워 시연·평가한다.
- Recommended approach: Compose에 `db`(pgvector 포함 PostgreSQL, healthcheck) → `init`(migration·적재, 한 번 실행) → `api`(FastAPI) → `web`(nginx: 두 앱 빌드 파일 + `/api` 중계) 순서와 의존성을 두고, 알람 발생기는 명령으로 실행한다. 환경 값(모드·키·계정 비밀번호)은 `.env`(Git 제외).
- Do not use when: 개발 중 빠른 반복(앱은 개발 서버, API·DB만 컨테이너로 충분).
- Preconditions and authority boundary: 이미지 받기·빌드는 승인 뒤. 팀원 환경(Windows 포함)에서 실행 확인이 필요하다.
- Verification and stop condition: 깨끗한 환경에서 `compose up` 한 번으로 시연 10건이 보고서까지(AC-16), 컨테이너 재시작 후 세션 재개(AC-14).
- Revalidate when: 서비스 구성·OS 환경이 바뀔 때.
- Wiki basis: `levelled-rag-multi-agent-practice-curriculum.md` `## 로컬 live 환경`; `claude-code-program-delivery-playbooks.md` `## 9. Deployment / ops change`; v1 EP-OPS-003. **한계:** nginx 설정·reverse proxy에 대한 Wiki 근거는 없다 — v2 EP-C1-WEB-001(사용자 결정). 팀원 Windows 환경 주의 사항(예: 비동기 DB 드라이버와 이벤트 루프)은 Wiki가 아니라 agent-10 저장소 경험에서만 확인됐다.

### EP-C1-WS-001 — npm workspaces로 두 앱 + 공통 패키지 (v2, 사용자 결정)

- Situation / requirement signals: EP-C1-SURFACE-001의 두 앱 · 공통 패키지를 한 저장소에서 빌드한다. 팀원 환경에 Windows가 있다.
- Recommended approach: Node에 들어 있는 npm의 workspaces로 `apps/tech`(정비자) · `apps/lead`(파트장) · `packages/ui`(공통)를 둔다. lockfile은 루트 `package-lock.json` 하나. 앱 빌드는 각 workspace의 Vite 명령으로 따로 한다.
- Do not use when: 앱이 하나로 줄 때(workspace 없이 단일 패키지).
- Preconditions and authority boundary: 패키지 설치는 사용자 승인 뒤. 앱끼리 서로를 의존성으로 두지 않는다(EP-C1-SURFACE-001).
- Verification and stop condition: 깨끗한 checkout에서 `npm ci` 뒤 두 앱 각각 build · typecheck 통과, `apps/tech` → `apps/lead`(또는 반대) import가 있으면 실패하는 검사.
- Revalidate when: Node 주 버전 · 패키지 관리자 · 앱 수가 바뀔 때.
- Wiki basis: 없음 — 사용자 결정(2026-10-12, Source documents 마지막 행).

### EP-C1-APITYPE-001 — openapi-typescript + openapi-fetch (v2, 사용자 결정)

- Situation / requirement signals: EP-C1-API-001의 OpenAPI 계약에서 앱용 타입을 만든다.
- Recommended approach: 서버가 내보낸 OpenAPI 파일(버전 관리)에서 `openapi-typescript`로 타입만 생성해 `packages/ui`(API 클라이언트)에 두고, 호출은 `openapi-fetch`로 한다. 생성물은 손으로 고치지 않는다.
- Do not use when: 계약 경계가 없을 때(EP-C1-API-001과 같음).
- Preconditions and authority boundary: 생성 도구는 타입만 만들고 엔드포인트 의미를 바꾸지 않는다. 설치는 승인 뒤.
- Verification and stop condition: '서버 → OpenAPI 파일 → 타입' 재생성 뒤 git diff 없음, 두 앱 typecheck 통과. diff가 있으면 다음 slice 금지.
- Revalidate when: OpenAPI 버전 · 생성 도구 주 버전이 바뀔 때.
- Wiki basis: 없음 — 사용자 결정(2026-10-12).

### EP-C1-WEB-001 — nginx 하나, 앱마다 포트, 각자 /api 중계 (v2, 사용자 결정)

- Situation / requirement signals: 두 앱은 완전히 별도 제품(명세 D3)이고 같은 API 서버를 쓴다(EP-C1-RUN-001의 `web`).
- Recommended approach: nginx 하나에 server 블록 2개 — 정비자 앱 8081, 파트장 앱 8082. 각 블록이 자기 빌드 파일(SPA fallback 포함)과 `/api/` → API 서버 중계를 가진다. 같은 host의 다른 포트는 쿠키를 나눠 갖지 않으므로(쿠키는 host 단위) 로그인 쿠키 이름을 앱마다 다르게 하고 서버가 쿠키 이름과 역할을 함께 검사한다(EP-C1-AUTH-002).
- Do not use when: 한 출처(origin)에 두 앱을 둬야 하는 배포 제약이 생길 때(그때는 경로 분리 재검토).
- Preconditions and authority boundary: nginx는 정적 파일과 중계만 한다(업무 판정 없음). 이미지 받기 · 빌드는 승인 뒤.
- Verification and stop condition: 8081 · 8082 각각 첫 화면 · 새로고침(깊은 경로) · `/api` 왕복 통과, 한 앱 쿠키로 다른 앱 API 역할 검사가 거부되는 음성 시험.
- Revalidate when: 배포 위치 · 도메인 · 포트 정책이 바뀔 때.
- Wiki basis: 없음 — 사용자 결정(2026-10-12).

### EP-C1-MIG-001 — Alembic migration (v2, 사용자 결정)

- Situation / requirement signals: EP-C1-DB-001의 `ops` · `knowledge` schema를 버전 관리한다.
- Recommended approach: SQLAlchemy 모델 + Alembic. 한 migration 줄기에서 두 schema와 `CREATE EXTENSION vector`를 관리하고, 모든 revision에 downgrade를 둔다. `init` 서비스가 `alembic upgrade head` 뒤 적재를 한다.
- Do not use when: DB가 없는 구성.
- Preconditions and authority boundary: migration은 운영 외 작업. 운영 DB에 자동 downgrade를 하지 않는다.
- Verification and stop condition: 깨끗한 PostgreSQL 컨테이너에서 upgrade head → downgrade base → upgrade head 통과, 모델과 DB 차이 자동 검사(autogenerate 결과 빈 diff).
- Revalidate when: SQLAlchemy · Alembic 주 버전, schema 구성이 바뀔 때.
- Wiki basis: 없음 — 사용자 결정(2026-10-12).

### EP-C1-AUTH-002 — argon2id + 서버 세션 쿠키 (v2, 사용자 결정)

- Situation / requirement signals: EP-C1-AUTH-001의 비밀번호 저장 · 로그인 유지 방식.
- Recommended approach: 비밀번호는 argon2id(salt 포함)로만 저장한다. 로그인 성공 시 서버가 임의 세션 ID를 만들어 `ops` schema에 (해시로) 저장하고, httpOnly · SameSite=Strict 쿠키로 준다. 유효 기간 12시간(야간 교대 한 번), 로그아웃하면 즉시 무효. 쿠키 이름은 앱마다 다르다(EP-C1-WEB-001). 상태를 바꾸는 요청은 쿠키 + 앱 역할 검사를 함께 한다.
- Do not use when: 외부 SSO가 필요할 때(EP-C1-AUTH-001과 같음).
- Preconditions and authority boundary: 세션 ID · 비밀번호를 URL · 로그 · 화면에 남기지 않는다. 시연 계정 비밀번호는 적재 시 환경 변수.
- Verification and stop condition: 잘못된 역할 · 만료 · 로그아웃 뒤 세션 거부 음성 시험, 저장값이 평문 · 원 세션 ID가 아님 검사, 로그 비밀값 검사.
- Revalidate when: 교대 시간 · 인증 요구가 바뀔 때.
- Wiki basis: 없음 — 사용자 결정(2026-10-12).

### EP-C1-FUSE-001 — RRF k=60 · 같은 비중 + 글자 2-gram (v2, 사용자 결정)

- Situation / requirement signals: EP-C1-RET-001의 순위 융합 식과 한국어 토큰화.
- Recommended approach: Reciprocal Rank Fusion, k=60, BM25 순위와 pgvector 순위를 같은 비중으로 합친다. BM25 토큰은 공백 · 기호로 나눈 뒤 글자 2-gram(설치 필요 없음).
- Do not use when: 평가 카드에서 상위 10건 품질이 기준에 못 미칠 때(그때 형태소 분석 · 가중치 재검토, 설치 승인 필요).
- Preconditions and authority boundary: 원인 필드를 토큰 · 필터에 쓰지 않는다(EP-PACK-DATA-002).
- Verification and stop condition: 고정 입력 상위 10건 · 순서 고정 시험, 평가 카드 결과 기록. 평가 카드는 agent · index가 읽지 않는다.
- Revalidate when: 이력 구성 · 평가 결과 · 임베딩 모델이 바뀔 때.
- Wiki basis: 없음(융합 자체는 EP-C1-RET-001의 Wiki 근거) — k · 비중 · 토큰화는 사용자 결정(2026-10-12).

### EP-C1-E2E-002 — Playwright TypeScript (v2, 사용자 결정)

- Situation / requirement signals: EP-C1-E2E-001의 브라우저 E2E 도구.
- Recommended approach: `@playwright/test`를 npm workspace(`e2e/`)에 두고, 정비자 · 파트장 두 browser context로 두 앱을 잇는 시험을 한 파일에서 돌린다. fixture 모드 · 테스트마다 DB 초기화.
- Do not use when: 규칙 · 컴포넌트 하나 검증(EP-C1-E2E-001과 같음).
- Preconditions and authority boundary: Playwright · 브라우저 내려받기는 사용자 승인 뒤. live provider를 쓰지 않는다.
- Verification and stop condition: EP-C1-E2E-001과 같음.
- Revalidate when: Playwright 주 버전 · 대상 브라우저가 바뀔 때.
- Wiki basis: Playwright best practices 출처 인용은 `current-implementation-planning-engineering-reference.md` `## 5.`, 도구 · 언어 선택은 사용자 결정(2026-10-12).

### EP-C1-PY-001 — uv 프로젝트 + Python 3.12 고정 (v3, 사용자 결정)

- Situation / requirement signals: 서버(FastAPI · agent 패키지 · 적재기 · 알람 발생기 · 평가 실행기)의 Python 환경과 의존성을 팀원 Mac · Windows와 Docker image에서 같게 맞춘다. 기본 v1 EP-OPS-003은 lockfile · clean build만 요구한다.
- Recommended approach: 저장소 루트(또는 서버 폴더)에 uv 프로젝트(`pyproject.toml` + `uv.lock`)를 두고 `requires-python`과 `.python-version`을 3.12로 고정한다. 실행 · 시험은 `uv run`, 설치는 `uv sync --frozen`. Docker image도 같은 lock으로 만든다(로컬 Python 3.14와 따로).
- Do not use when: Python 코드가 없는 구성.
- Preconditions and authority boundary: uv가 Python 3.12와 패키지를 내려받는 일은 사용자 승인 뒤. 비밀값을 `pyproject.toml` · lock에 두지 않는다.
- Verification and stop condition: 깨끗한 checkout에서 `uv sync --frozen` 뒤 `uv run` 시험 통과, lock과 `pyproject.toml` 불일치 시 실패(`uv lock --check`), 컨테이너 안 Python 버전 3.12 확인.
- Revalidate when: 주요 라이브러리(LangGraph · FastAPI · SQLAlchemy · psycopg)가 3.12 지원을 바꾸거나 더 높은 버전이 필요해질 때, 팀원 OS 환경이 바뀔 때.
- Wiki basis: 없음 — 사용자 결정(2026-10-12, Source documents 마지막 행).

## Currency review

- **v1이 남긴 Wiki 근거 없는 선택 8개는 v2에서, PBC-1에서 나온 1개(Python 환경)는 v3에서 사용자 결정으로 채웠다**(EP-C1-WS-001 · APITYPE-001 · WEB-001 · MIG-001 · AUTH-002 · FUSE-001 · E2E-002 · PY-001, 주기 조회는 EP-C1-SYNC-001 그대로). 이 규칙들의 근거는 검증된 지식이 아니라 결정이므로, 각 규칙의 검증 · 재검토 조건이 실제로 통과하는지로 확인한다. 실패하면 이 Playbook을 다시 올리고 그 판부터 PBC-1을 다시 시작한다.
- **framework API 재확인 필요:** LangGraph interrupt·checkpointer(PostgreSQL) API, pgvector·임베딩 차원(256), OpenAI 모델 이름, openapi-typescript · openapi-fetch · Alembic · argon2 · Playwright의 현재 주 버전 — 구현 시점 공식 문서로 다시 확인한다.
- Wiki의 Hybrid 검색·HITL 내용은 "필요하다"는 공백 분석이며 검증된 구현 예가 아니다. EP-C1-RET-001·EP-C1-HITL-001은 평가·E2E로 확인한 뒤 재검토한다.
