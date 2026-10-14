---
name: vibe-coding-factory
description: Wiki 근거를 승인 가능한 개발 artifact로 컴파일한다.
---

# Vibe Coding Factory

Skill version: `0.8.20`

Wiki와 작업 요청을 Context Packet, Evidence Pack, Use Case, Wireframe, Prototype, Pre-build Contract로 순차 컴파일한다. 이 Skill은 전체 workflow와 run-state를 관리한다. 현재 gate의 reference와 template만 읽고, 사람 승인 없이 코드·외부 시스템을 변경하지 않는다.

## When to Use

- 새 사용자 흐름, 다중 파일 변경, UI·workflow·Agent 기능을 시작할 때
- 의도·제약·결과물 형태가 prose만으로 고정되지 않은 작업
- Wiki 근거를 사용해 구현 전 승인 artifact를 만들 때

## Do Not Use

- 한 파일의 명확한 저위험 수정(일반 개발 workflow 또는 Goal을 사용)
- 즉시 복구가 필요한 장애 대응
- 이미 승인된 Contract 범위 안의 사소한 구현·테스트 수정

## Inputs

- 작업 요청과 프로젝트 root
- 사용할 Wiki source 후보
- 기존 run의 `run-state.json` (있을 때만)

## Run location

모든 run artifact는 `<project-root>/.vibe-factory/runs/<run-id>/`에 둔다. 다른 run의 state나 승인 기록을 복사하지 않는다. 새 run은 `scripts/init_run.py`로 만든다. v0.8.10+ run에서 생성되는 `factory-profile/`은 이번 run이 사용할 Skill·template·validator·Critic protocol의 hash 고정 snapshot이다. 재개 시 이 snapshot의 Skill·Critic protocol을 읽고, 검증은 반드시 `factory-profile/snapshot/skill/scripts/validate_artifacts.py <run-dir>`로 실행한다. 전역 또는 프로젝트의 최신 복사본 validator는 해당 run을 검증할 수 없다. Profile, 산출물 유형, legacy 규칙은 `references/08-runtime-profile.md`를 읽는다.

모든 Critic 호출 전에는 현재 Gate의 공식 subject와 허용된 comparison source를 `critic-input-bundle.json`으로 고정한다. Critic은 bundle 밖의 파일을 읽지 않으며, validator는 bundle subject가 현재 run-state artifact인지 확인한다.

## Evidence insufficiency boundary

근거가 부족할 때에는 현재 단계가 허용한 비교 기준 밖으로 자동 확장하지 않는다. 먼저 허용된 source·artifact 안에서 직접 근거를 다시 찾는다. 설계 파생이 허용된 G2A/G3만 가장 가까운 원리를 차용하거나 승인 Contract에서 설계한 부분을 명시적으로 기록할 수 있다. 새 공개 source, 사용자 제공 자료, 권한이 필요하면 그 확장을 요청한다. Use Case·AC·authority·data meaning 자체가 부족하거나 바뀌어야 하면 어떤 단계에서도 추정하지 않고 멈춘다. G0/G1/PBC/G4~G7은 이 원리 차용 권한이 없다.

## Working-context compression policy

이 규칙은 run artifact를 새로 만들거나 내용을 요약하는 규칙이 아니라, Agent의 **누적 작업 context**를 줄이는 규칙이다. 다음 Gate가 새 direct input을 읽기 직전, 이전 Gate의 raw source·대화 이력·중간 탐색 결과가 더 이상 direct input이 아니면 context를 compact하거나 새 worker/session으로 전환한다. 이때 in-memory checkpoint에는 `run_id`, 현재 승인 Gate/version, 다음 Gate의 direct input artifact 이름·path·hash, 유지할 approval/authorization, unresolved·blocked 항목, next action만 남긴다. 제품 요구·AC·화면·권한·data meaning의 요약은 checkpoint로 넘기지 않는다. 다음 worker는 checkpoint를 받은 뒤 반드시 선언된 direct input artifact를 disk에서 새로 읽는다.

이 전환은 이전 Gate가 승인되고 필요한 artifact path/hash가 고정된 뒤에만 수행한다. 같은 direct input을 계속 사용해 artifact를 작성·수정·검토하는 중에는 compact하지 않는다. 새 run artifact, 별도 보고서, critic, Human Gate를 추가하지 않으며 checkpoint는 canonical source도 검증 입력도 아니다. runtime이 context compaction을 지원하지 않으면 같은 원칙으로 새 agent context를 시작한다.

## Human-facing explanatory SVGs

사용자·승인자에게 workflow, 산출물 재사용, 승인, 검증 결과를 설명하는 SVG를 전달할 때는 `artifact-dependency-tree` Skill을 사용한다. 먼저 해당 그림 범위의 producer·consumer·정확한 artifact 이름을 inventory로 잠그고, node에는 `역할 / 참조 / 산출물`만 표시한다. 실제 content reference는 정확한 artifact 이름의 실선으로, critic·Human Gate·manifest·hash lock은 control 점선으로, 과거 version은 lineage 점선으로 구분한다.

이 규칙은 artifact 관계를 설명하는 `traceability`, PBC Director Review의 dependency 그림, Gate Brief·plan amendment·final summary의 설명용 SVG에 적용한다. Use Case scenario map, G2 wireframe·design, Prototype, 제품 UI·상태·interaction 그림은 제품 경험 자체를 설명하므로 이 트리로 대체하지 않는다. 하나의 artifact만 설명하고 재사용·관계가 없는 경우에는 설명용 트리를 만들지 않는다.

## Routing

1. 새 기능이면 `ui_workflow_slice` 또는 `high_risk`로 분류한다. 이 Skill에는 `simple` 경로를 두지 않는다.
2. 기존 승인·구현 기능의 변경 요청은 이 Skill의 범위 밖이다. 별도 변경 workflow를 정하기 전에는 분석·구현·전달 artifact를 만들지 않고 멈춘다.
3. `ui_workflow_slice`는 G0~G3, PBC-0~PBC-4, 승인된 범위의 G4~G7 slice cycle을 수행한다.
4. `high_risk`는 권한·외부 영향·rollback을 명시하고 각 Human Gate를 필수로 둔다.
5. v0.8.10+ 기존 run은 `next_action`에 따라 해당 run의 Factory Profile snapshot으로 재개한다. v0.8.9 이하 run은 `legacy`로 표시하고 현재 Skill 규칙을 부분 적용하지 않는다. 진행 중 run의 Profile migration은 지원하지 않으며, 새 규칙이 필요하면 새 run을 만든다.

## Pre-build Procedure

### G0 — Context Packet and Evidence Pack

1. `references/01-wiki-context-contract.md`와 `templates/context-packet.md`를 읽는다.
2. Wiki index와 source를 넓게 탐색해 Intent Context 후보를 찾는다. 기본으로 현재 프로젝트의 목적·계획·결정과 사용자의 장기 목표·진로·캡스톤 전략을 검토한다.
3. 선택한 Intent Context 문서는 발췌하지 말고 전문을 Context Packet에 보존한다. 제외한 후보와 제외 이유도 기록한다.
4. 현재 slice의 Task Evidence를 별도 층으로 추가하고, `fact`, `decision`, `proposal`, `constraint`, `assumption`, `open_question`을 분리한다. 특정 단계·MVP·실험에만 유효한 결정은 제품 전체 요구로 확대하지 않고 적용 범위를 기록한다.
5. `templates/evidence-pack.md`로 Evidence Pack 초안을 만든다. `Data and system context`에는 구현 방식을 결정하지 않는 사실만 구조화한다: entry surface, interaction-surface mode(`single`/`multiple`/`non_ui`)와 multiple일 때의 actor·device·독립 작업, 처리 책임의 존재, durable state/readback 기대, 외부·비동기 의존성, 실패·취소·재시도·restart 기대, 아직 모르는 제품 사실. 정적 화면·로컬 단일 process처럼 해당하지 않는 값은 근거와 함께 `not_applicable`로 기록한다. product UI surface는 구조 후보나 reference 조사 surface가 아니라 실제 출시해야 하는 사용자용 UI다.
6. source manifest와 artifact version을 기록한다. 각 Intent source의 전문 snapshot과 SHA-256을 run 안에 보존하고, Context Packet에 같은 전문을 포함한다. Context Packet manifest에는 `content_mode: full_document`을 사용한다.
7. Profile에 고정된 Critic protocol로 독립 critic 검토를 요청한다. 호출 전 `templates/critic-input-bundle.json`으로 현재 Evidence Pack subject와 허용된 비교 source의 path/version/hash만 담은 input bundle을 만들고, Critic 결과에는 그 bundle path/hash와 같은 source 목록을 기록한다.
8. `risk_level: high`이거나 Core premises·Direction constraints가 현재 구조를 크게 제한하면, `gate-brief.md`로 G0 Human Brief를 제시하고 필요한 범위만 확인받는다.

### G0 Critic response

- `pass`: G1로 진행한다.
- `revise`: source가 있는 내용만 재작성하고 critic을 다시 호출한다. G0 critic은 최대 3회이며, 어느 회차든 `pass`면 즉시 G1로 진행한다.
- `ask-user`: 구현 범위·흐름·권한·데이터·완료 판정을 바꾸는 질문만 최대 3개 묶어 사람에게 제시하고 멈춘다.
- `insufficient-evidence`: source 재확인 후에도 핵심 근거가 없으면 사람에게 escalation하고 멈춘다.

세 번째 G0 critic에도 `revise`가 남으면 네 번째 생성으로 넘어가지 않는다. 남은 핵심 문제·확인한 source·사용자 판단이 필요한 질문을 기록하고 멈춘다.

### G1 — Use Case and Human Gate

1. 확정된 Evidence Pack만 근거로 `templates/use-case-packet.md`를 작성한다. Evidence ledger의 stable Evidence ID를 scenario마다 `evidence_refs`로 연결한다.
2. Actor, trigger, precondition, main flow, alternate/failure/cancel flow, postcondition, acceptance criteria, non-goals를 포함한다. Evidence Pack의 interaction-surface mode가 `multiple`이면 `scenario-coverage.json`에 출시 UI surface의 ID·사용자·기기/맥락·독립 작업·필수 scenario를 기록하고, 각 user-facing scenario를 정확히 하나의 `ui_surface_id`에 연결한다. background/non-UI scenario에는 surface를 억지로 붙이지 않는다.
3. 먼저 전문 용어 없이 문제·사용자 행동·성공 결과를 쉬운 말로 설명하고, 이어서 정확한 명세를 제시한다.
4. 글의 시나리오와 일치하는 `use-case-map.svg` 그림을 만들고, 각 scenario가 어느 그림 노드·화살표에 대응하는지 기록한다.
5. `templates/scenario-coverage.json`으로 기능별 happy path, alternate, failure, cancel, empty/no-result, permission/authority, external dependency failure, timeout/expiry를 빠짐없이 판정한다. 적용하지 않는 항목은 이유를 기록하고, `run-state.json`의 `use_case` artifact에 packet·diagram·coverage 경로를 기록한다.
6. Acceptance Criterion마다 scenario와 관찰 가능한 판정 조건을 `acceptance-criteria.json`에 기록한다. Use Case Packet은 구현에 영향을 주는 problem/success outcome, non-goal, authority boundary, data meaning·sensitivity, external-action boundary, failure cost, known decision을 명시적으로 포함한다. 이 정보가 source에 없으면 추측하지 않고 G1에서 멈춘다.
7. `logical-system-contract.json`을 Use Case Bundle 안의 canonical product connection record로 만든다. 처리·저장·외부 또는 비동기 경계가 있으면, 각 관련 scenario의 entry surface, 논리 책임, state ownership/durability/readback, 외부 의존성, success/failure/cancel-or-retry outcome, AC를 연결한다. 실제 framework·DB·protocol은 쓰지 않는다. 그런 경계가 전혀 없으면 `not_applicable`과 이유를 기록한다. multiple product UI surface이면 logical system overview와 scenario flow에서 각 UI 진입과 공유 처리 경계를 이름으로 보인다. 경로와 hash는 `run-state.json`의 `use_case.logical_system_contract`와 Use Case Bundle manifest의 `logical_system_contract` role에 함께 잠근다. contract가 applicable이면 이 JSON에서 만든 `logical-system-overview.svg`와 `logical-scenario-flow.svg`를 G1 Human Gate에 함께 보여 준다. 새 Gate나 critic은 만들지 않는다.
8. `scenario-coverage.json`의 `handoff_readiness.blocking_product_unknowns`는 G1 승인 전에 비어 있어야 한다. scenario·AC·권한·data meaning·외부 행동·실패 결과를 바꿀 미결 사항은 다음 Gate로 넘기지 않고 G1에서 해결 또는 escalation한다.
9. `risk_level: high`이면 `risk-controls.json`에 failure cost→mitigation→Acceptance Criterion과 개발·검증 중 Agent 권한을 기록한다.
10. 독립 critic 검토 후 `gate-brief.md`로 Human Gate G1에 제시한다. critic은 Evidence Pack을 비교 기준으로 Use Case와 logical system contract가 scenario·AC·authority/data·failure promise를 누락·왜곡하지 않았는지만 본다. multiple product UI surface이면 source가 말한 사용자·기기·독립 작업과 scenario/authority의 surface 배정이 누락·혼동되지 않았는지도 확인한다. critic이 `revise`이면 source 기반 재작성 뒤 확인 전용 critic을 한 번 더 호출한다. 확인 전용 critic이 `pass`할 때만 G1 Human Gate에 간다. 확인 critic도 `revise`이면 Human Gate에 가지 않는다. 새 artifact version으로 새 검토 cycle을 시작하며, 같은 blocking category가 새 cycle에서도 반복되거나 해결에 제품·권한 선택이 필요할 때만 사람에게 escalation한다.
11. Gate Decision이 승인될 때까지 G2A로 진행하지 않는다.

### G2A — Wireframe structure and Human Gate

1. `references/04-wireframe-review-bundle.md`와 `templates/wireframe-candidate.md`를 읽는다.
2. 승인된 G1 scenario에서 `wireframes/page-inventory.json`을 만든다. 각 페이지에는 ID, 대응 scenario, 비교할 상태를 기록하고, 모든 승인 scenario를 `page_state` 또는 `non_ui`로 정확히 한 번 분류한다. `non_ui`에는 화면으로 표현하지 않는 이유를 기록한다. multiple product UI surface이면 모든 Page ID에 해당 `ui_surface_ids`를 붙이고, 페이지가 공유될 때만 여러 surface를 기록한다. 그 page의 scenario surface와 정확히 일치해야 한다. 이 UI들은 후보 A/B가 아니라 모두 출시 범위다. 보드와 Gate Brief는 surface별로 페이지를 그룹화하고, decision view에는 surface마다 적어도 하나의 핵심 화면을 포함한다. G1 logical system contract가 applicable이면 각 page/state와 scenario handoff에 해당 logical flow를 연결해, 사용자에게 보이는 상태가 어느 처리 결과인지 보존한다. G2A는 그 flow의 기술 구조를 설계하거나 화면에 없는 backend를 표현하지 않는다.
3. `reference_strategy`에 page inventory의 모든 Page ID를 `game_ui`, `marketing_site`, `interactive_site`, `workflow_product`, `general_utility` 중 하나로 분류하고 근거를 기록한다. 이 record의 `research_scope`에는 이번 run에서 허용된 공개 웹 조사, user-provided source, 열린 조사 대상, route 밖 조사·로그인/유료/비공개 자료의 요청 정책을 먼저 기록한다. 공개 웹 조사 권한이 명시되지 않았고 user-provided source만으로 충분하지 않으면 탐색 전에 한 번만 사용자에게 묻는다. SaaS 여부·결제 방식·배포 형태는 판단 기준이 아니다. `general_utility`는 workflow_product의 업무 흐름 신호가 두 개 미만일 때만 선택하며, 이 경우 고정 사이트 없이 실제 출시된 유사 제품을 열린 검색으로 조사한다.
4. 조사 전에 가능한 작업 모델을 만든다. 후보 모델은 `첫 화면`, `탐색`, `화면 토폴로지`, `핵심 정보 단위`, `주요 조작 위치`, `상호작용 방식`, `정보 노출`, `상태·피드백 위치`를 기록한다. 최종 후보 쌍은 `화면 토폴로지`·`핵심 정보 단위`·`상호작용 방식` 중 하나 이상과 총 세 축 이상에서 달라야 한다. 이는 색·서체·그림자·브랜드 톤을 바꾸는 규칙이 아니라 사용자가 정보를 보고 조작하는 구조적 선택지를 만드는 규칙이다.
5. G1의 기능·scenario·AC를 바꾸지 않는 범위에서, reference_strategy의 각 분류와 작업 모델에 맞는 **실제 출시 제품의 화면·패턴**을 조사한다. 지정된 source route가 있으면 먼저 사용하되, 검색 순위나 같은 화면의 변주로 후보를 정하지 않는다. 직접 대응 화면이 없다는 사실만으로 멈추지 않는다. route 안의 가장 가까운 작업 원리를 차용하고 제품 고유 부분은 승인 Use Case·AC로 설계한다. route 안에 적합한 원리도 없으면, `general_utility`의 허용된 열린 조사 외에는 route 밖 조사를 자동으로 시작하지 않고 사용자에게 요청한다. 실제 화면을 전혀 확인할 수 없거나 Use Case·AC도 설계 기준을 주지 않으면 멈춘다. 와이어프레임 도구, 일반 템플릿, 장식용 영감 이미지는 구조 근거로 쓰지 않는다. `reference-board.html`과 reference record에는 제품·화면·URL·확인 시각·적합한 작업·가져올 패턴·가져오지 않을 제품 결정을 명시한다.
6. reference pattern을 출발점으로, 위 작업 모델을 구현한 후보마다 먼저 `candidate_viability`를 검사한다. 모든 대응 scenario의 핵심 경로·필수 정보 가시성·추가 비용·그 비용을 정당화하는 편익을 기록하고, 승인 Use Case·AC·권한·data meaning을 훼손하거나 불필요한 이동·재입력·맥락 전환을 만드는 후보는 제외한다. 위험 작업에서는 빠름을 이유로 필요한 확인을 제거하지 않는다. 이 검사를 통과한 renderable HTML/CSS 후보를 기본으로 최대 **3개** 만든다. 통과 후보가 2개 또는 1개뿐이면 비효율적인 후보를 억지로 만들지 않고, 제외한 구조와 사유를 `candidate_count_exception_reason` 및 G2A Gate Brief에 기록한다. 후보는 실제 제품 화면처럼 정보 위계·밀도·상태·조작을 판단할 수 있어야 하며, 외부 화면을 복제하지 않고 현재 제품의 fixture·용어·제약으로 재구성한다. 참조 화면에 직접 존재하지 않는 제품 고유 기능은 승인 Use Case에 맞는 전용 영역·상태·조작으로 설계하고, 어떤 참조 원리를 어떻게 바꾸었는지 남긴다. 색상·카드 모양·장식만 다른 안은 후보가 아니다.
7. 후보마다 어느 reference pattern을 사용했는지, 여덟 구조 축 값, 적합성 판단, 현재 기능에 맞게 무엇을 보존·변경·새로 설계했는지, 다른 후보와 비교해 사용자가 무엇을 다르게 하고 무엇을 얻거나 잃는지 `structure/<candidate>.md`에 기록한다. `candidate_page_evidence`에는 **후보 × Page ID**마다 page task, 상태, `direct | principle | contract_designed`, reference·차용 원리·adaptation·scenario link를 기록한다. 화면을 먼저 만들며, 이 문서는 화면의 렌더링 명령서가 아니다. **모든 후보는 page inventory의 모든 페이지·상태에 대해 정확한 renderable path를 제공한다.**
8. `wireframes/structure-review.html`은 두 보기를 제공한다. 기본 `decision view`는 후보 차이가 가장 크게 드러나는 1~3개 핵심 화면을 큰 크기로, 같은 `Page ID / State`의 모든 후보와 명시적 차이 설명을 나란히 보여 준다. 각 후보에는 핵심 scenario의 추가 비용과 그 비용을 보상하는 편익도 짧게 보인다. `coverage view`는 inventory 전체를 감사용으로 제공한다. 각 후보 화면은 hover와 keyboard focus에서 원본 경로의 확대 미리보기를 제공하고, layout을 밀지 않는다. 사용자는 각 `Page ID / State`에서 후보를 클릭해 선택할 수 있으며, 보드는 그 결과를 `g2a-page-state-selection.json`으로 복사·다운로드할 수 있어야 한다. 이 파일은 다음 Human Gate의 입력 기록일 뿐 승인 자체는 아니다. 각 후보×페이지×상태 cell은 실제 렌더 경로를 포함한 `data-cell="candidate_id:page_id:state|image_path"` marker를 남긴다. 후보별 화면·brief·sample data를 만든다.
9. `gate-brief.md`로 Human Gate G2A에서 구조를 선택·결합·재정의한다. 클릭 선택이 있으면 `templates/g2a-page-state-selection.json` 형식으로 저장하고 Gate Decision에 그 path를 기록한다. 선택 또는 결합 결과의 화면을 `wireframes/structure/selected/`에 먼저 렌더하고, 그 **선택된 실제 화면에서** `selected.md` 승인 구조 청사진을 추출한다. 이어 `selected-structure-contract.json`에 모든 핵심 `Page / State / Region / structure / content / interaction`을 구조화해 잠근다. 장식 요소는 넣지 않는다. 청사진은 구조·내용·행동의 guardrail이며 화면 생성 원본이 아니다. 기존 파일명 `selected-visual-baseline.json`에는 모든 선택 화면의 path·hash를 잠그되 `baseline_role: structure_workflow_only`, `semantic_alias: selected_structure_render_baseline`을 기록한다. 이 alias는 G2B/G3가 이 artifact를 디자인 기준이 아닌 구조 render 기준으로 읽게 한다. 승인 결정은 `decisions/G2A-wireframe-structure.json`에 기록한다.

### G2B — Visual design and Human Gate

1. `references/04-wireframe-review-bundle.md`, `references/07-design-playbook.md`, `templates/design-direction.md`를 읽는다. Playbook은 여러 공개 design system에서 미리 정제한 짧은 시각 설계 기준이다. 매 run마다 원문 사이트를 다시 읽지 않으며, product contract를 추가하거나 바꾸지 않는다. 원문 재조사는 Playbook에 없는 시각 문제를 풀어야 할 때만 사용자 권한을 받아 수행한다. G2A의 `selected_structure_render_baseline`은 **구조·작업 흐름 기준선**이며, G2A의 서체·팔레트·표면·모서리·item silhouette은 G2B에서 보존할 의무가 없는 잠정 표현이다. `wireframes/design/`에 page inventory 중 대표 화면 3개(페이지가 3개 미만이면 모든 페이지)를 고르고, 각 화면의 `Page ID / State`와 서로 다른 핵심 작업 또는 위험을 보이는 선택 이유를 기록한다. multiple product UI surface이면 surface마다 하나 이상의 대표 화면을 반드시 포함하며, UI surface 수가 3보다 많을 때만 대표 화면 수를 그 수만큼 늘린다.
2. 구조를 다시 설계하는 대신, 공통 구조·fixture·상태를 재사용한 4~6개의 **design refinement**를 제안한다. 방향 수가 1~3개이면 다른 진정한 시각 가설이 승인 계약 안에서 성립하지 않는 이유를 `direction_count_exception_reason`과 G2B Gate Brief에 남긴다. 후보 하나를 매번 새 페이지로 재구현하지 말고, 공통 renderable 화면 위에 visual layer를 적용해 시간을 제한한다. 각 방향은 Playbook principle ID와 다섯 시각 축의 실제 선택값을 `visual_signature`로 기록한다. 모든 후보 쌍은 `서체·밀도 / 색·상태 언어 / 표면·위계 / item silhouette·control form / 강조·읽기 순서` 중 적어도 세 값이 달라야 한다. 단, item silhouette은 항목의 의미·필수 metadata·상태 신호·조작 affordance·연결점과 상호작용 방식을 보존하는 범위에서만 바꾼다. 방향별로 실제 렌더 가능한 before/after 화면과 `유지한 구조 / 바꾼 시각 표현 / 기대 편익 / trade-off`를 보여 준다. `design-direction.md`의 **Component foundation**에는 이 대표 화면에 실제로 반복되는 요소만 적어, tab·button·panel·입력·status 등 각 요소의 형태·상태·token/규칙·의도적 예외를 고정한다. multiple product UI surface이면 하나의 방향 안에서 공통 규칙과 surface별 적용 규칙(밀도·조작 크기·정보 위계)을 함께 기록한다. 이는 surface별 별도 디자인 방향이나 제품 정체성을 만드는 일이 아니다. 카드/표의 정보 단위와 영역 배치, 탐색, 사용자의 작업 순서, 기능·권한·AC는 G2A의 결정이므로 바꾸지 않는다.
3. Human Gate 전에 모든 방향의 실제 렌더 화면을 한 번에 보는 **별도 Visual Craft Review pass**를 수행한다. 이 pass는 `design-direction.md`의 Component foundation과 실제 render path만 비교해 alignment, 반복 요소의 일관성, surface/border, typography/density, state clarity만 점검한다. G1/G2A 계약·구조·기능·권한·정보 단위·작업 순서를 비판하거나 바꾸지 않으며, G3/PBC/G6 critic이 아니다. 실제 screen을 검토할 수 있는 독자적인 외부 디자인 skill 또는 UI guideline이 있으면 이 제한된 pass에 사용할 수 있다. 없으면 candidate authoring과 분리된 visual review pass가 실제 렌더를 검토한다. review 결과는 방향별 문서의 짧은 표에만 기록한다.
4. Craft Review가 찾은 문제는 방향별 공통 visual layer/token/component rule에서 **한 번만** 보정하고 대표 화면을 다시 렌더한다. 화면별 반복 수정이나 두 번째 Craft Review는 하지 않는다. 한 번의 보정 뒤에도 조립 품질이 부족한 방향은 board에서 제외한다. 후보가 1~3개로 줄면 기존 `direction_count_exception_reason`을 사용한다. Craft Review를 마친 `ready` 방향만 `design-review.html`에 표시하고, board에는 각 방향의 Craft Review 결과가 보이도록 한다.
5. `gate-brief.md`로 Human Gate G2B에서 최종 디자인 방향을 승인한다. 승인 후 선택한 direction을 `templates/selected-visual-rules.md`로 한 번 컴파일한다. 이 문서는 대표 화면 밖의 페이지·상태에도 적용할 전역 type·density·color/state·surface·item/control·emphasis 규칙과 선택된 **Component foundation**을 담으며, G3가 G2B 문서를 다시 해석하지 않도록 하는 유일한 최종 시각 기준이다. 구조·흐름 변경이 필요하면 G2A로 돌아간다. 승인 결정에는 `selected_direction_id`와 `selected_visual_rules_path`를 기록한다.

### G3 — Prototype slice and Human Gate

1. G2A의 **승인 structure render baseline과 selected structure contract**는 구조·작업 흐름·핵심 상호작용의 1차 기준이고, 사람이 읽는 청사진은 보조 guardrail이며, G2B의 `selected-visual-rules.md`와 그 안의 **Component foundation**은 모든 페이지·상태의 최종 시각 표현의 1차 기준이다. 이 기준을 적용해 핵심 흐름·현실적인 fixture·최소 1개 empty/error/permission 상태를 포함한 Prototype Slice를 만든다. G1 Use Case·AC가 요구하지만 승인 화면에 없는 상태는, 원본 Page/State의 구조·탐색·작업 순서·핵심 Region을 유지할 때만 `derived_states`로 추가하고 근거를 기록한다. 새 영역·탐색·작업 순서·제어 방식이 필요하면 G3에서 추정하지 않고 G2A로 돌아간다. 청사진으로 화면을 다시 생성하거나 HTML/CSS보다 우선해 구조를 추정하지 않는다.
2. `prototype-coverage.json`에 G1의 모든 Acceptance Criterion을 `covered` 또는 `deferred`로 연결한다. covered criterion에는 관찰 조건별 test/assertion과 run 내부의 실행 증거를, deferred criterion에는 이유를 기록한다. 같은 파일에는 G2A `selected-structure-contract.json`을 내용 그대로 `compiled_structure_contract`로 복사하고, 모든 핵심 `Page / State / Region`을 `structure_coverage`의 prototype 위치·assertion·evidence에 정확히 한 번 연결한다. multiple product UI surface이면 각 surface의 핵심 scenario·Page/State·AC를 `ui_surface_coverage`에 한 번씩 연결해 두 UI 모두의 성공·권한 또는 오류 상태가 증명되게 한다.
3. 선택 가능한 Project·item·case·node·tab 같은 상호작용 축이 있으면, 축별 서로 다른 값을 선택했을 때 표시 결과가 달라지는 variation check를 남긴다.
4. 독립 critic이 승인 Use Case Bundle·G2A structure render baseline·G2A 승인 페이지 청사진·G2A selected structure contract·G2B selected visual rules를 비교 기준으로, Prototype이 AC→관찰 조건→test/assertion→evidence와 G2A의 구조·작업 흐름·핵심 상호작용, G2B의 최종 시각 표현을 정확히 반영하는지 검토한다. `derived_states`가 있으면 해당 Use Case·AC 근거, 원본 Page/State, 구조 보존, 추가 상태 표현과 증거만 비교해 확인한다. 이 검토는 승인된 화면이나 구조 자체를 비판하지 않고, Prototype이 두 기준에서 멋대로 달라지거나 핵심 구조 contract의 Region·구조 방식·내용 구성·행동을 빠뜨리거나 바꾸지 않았는지만 확인한다. screenshot 또는 흐름 완주만으로 기능 통과를 추론하지 않는다. Critic JSON에는 실제 비교 기준의 path/version/hash를 남긴다. G3는 초안당 critic 1회로 시작하며, `revise`이면 source 기반 수정본에 확인 critic을 **한 번만** 호출한다. 확인 critic도 `revise`이면 세 번째 자동 critic을 만들지 않고, 남은 blocking issue와 가능한 선택지를 기록해 사람 판단으로 멈춘다.
5. Prototype Bundle에는 승인된 `selected-structure-contract`의 핵심 구조표와 selected visual rules의 전역 규칙표·**Component foundation**을 **내용 그대로** 포함하고, blueprint·structure contract·structure render baseline·selected visual rules의 source path·hash를 lineage로 기록한다. 페이지·상태, interaction/variation, fixture 경계, G1 AC별 coverage·assertion·evidence, deferred scope도 보존한다. logical system contract가 applicable이면 prototype의 사용자-visible success/failure/loading/retry 상태가 연결한 logical flow의 결과와 모순되지 않는지 확인한다. 실제 API·DB·runtime을 G3에서 구현하거나 추정하지 않는다. Prototype은 G2A/G2B의 경로나 요약만 가리켜서는 안 되며, 구현자가 필요한 UI 정보를 bundle 안에서 확인할 수 있어야 한다.
6. `gate-brief.md`로 Human Gate G3에서 멈춘다. 승인 결정은 `decisions/G3-prototype.json`에 기록한다. deferred criterion은 이 decision의 `excluded_scope`에도 명시한다.
7. 승인된 Use Case Bundle과 Prototype Bundle만 사용해 PBC-0으로 진행한다. G3 승인만으로 코드·외부 행동 권한이 생기지 않는다.

## Pre-build Contract Procedure

PBC는 승인된 **Use Case Bundle과 Prototype Bundle**을 완결된 구현 계약으로 컴파일한다. `logical-system-contract.json`은 Use Case Bundle 내부 구성물이므로 세 번째 제품 입력이 아니다. Evidence Pack·G2A·G2B는 두 bundle을 만든 상위 artifact이며 PBC의 직접 제품 입력이 아니다. G4~G7은 PBC 산출물만 실행하며 어떤 pre-PBC 제품 artifact도 직접 읽지 않는다. Wiki는 구현 방식의 근거로만 사용하며, Use Case·AC·화면·권한·데이터 의미를 재해석하거나 추가하지 않는다. `references/06-prebuild-contract-planning.md`와 해당 template을 읽는다.

### PBC-0 — Approved input lock

1. 승인된 Use Case Bundle(`use-case-packet.md`, `use-case-map.svg`, `scenario-coverage.json`, `acceptance-criteria.json`, `logical-system-contract.json`, 필요 시 `risk-controls.json`, G1 Gate Decision)과 Prototype Bundle(`prototype-slice.md`, renderable prototype, `prototype-coverage.json`, execution/variation evidence, G3 Gate Decision)의 version·hash·경로·Feature/Scenario/AC ID를 `approved-inputs/approved-artifact-manifest.json`에 고정한다. 이 manifest는 두 bundle의 허용 version을 잠그는 주소록이지 내용을 대신 주입하지 않는다.
2. 현재 repository revision·dependency/environment 사실을 `discovery/planning-baseline.json`에 기록한다. 구현 시작 직전에 이 기준선이 달라지면 PBC-1 이상을 재검토한다.
3. 승인되지 않았거나 서로 맞지 않는 입력은 추측으로 고치지 않고 blocker로 기록한다.

### PBC-1 — Engineering discovery

1. 승인된 Use Case Bundle의 AC·authority/data/external-action/failure 및 applicable logical flow 정보와 Prototype Bundle의 UI/state/fixture/coverage 정보를 실제로 읽고, 현재 repository 사실을 조사한다.
2. Wiki 원문을 이 run에 복제하지 않는다. PBC 시작 전 Wiki 지식으로 유지·검토한 버전 고정 `Engineering Playbook`을 읽고, path·version·SHA-256·검토일을 기록한다. Playbook은 `templates/engineering-playbook.md`의 형식대로 상황별 skill·model·harness·loop·graph 등의 선택 규칙, 비적용 조건, verifier/stop 조건, 원 Wiki 문서·section 근거를 포함해야 한다. 필요한 규칙이 없거나 Playbook이 낡았으면 PBC를 진행하며 즉석에서 추측하지 말고, 별도 knowledge-curation 작업으로 Playbook을 갱신·versioning한 뒤 그 버전부터 다시 시작한다. 이 지식은 **구현 방법의 선택 근거**일 뿐, 사용자 흐름·AC·권한·data meaning·화면 구조를 새로 만들거나 바꾸는 근거가 될 수 없다.
3. 가장 싼 결정론적 verifier와 단순한 single workflow/service를 먼저 검토한다. 관찰된 필요가 없으면 agentic 구조를 추가하지 않는다.
4. **기본적으로 PBC 중 code spike, production code 변경, 외부 호출은 금지한다.** 다만 둘 이상의 실행 격리·harness·process 제어가 함께 권한 경계 또는 verifier의 성립을 좌우할 때는, 제품 source·의존성·제품 동작을 **변경하거나 실행하지 않고** 임시 workspace 안에서 그 조합의 호환성만 확인하는 `internal compatibility probe`를 PBC-1에서 수행할 수 있다. 이 probe는 외부 연결·실서비스·secret·배포·의존성/제품 source 변경을 하지 않고, 명령·격리·예상/관찰 결과·폐기 증거를 조건부 `feasibility-probe.json`에 남긴다. Coding Plan의 `feasibility_preflight`은 그 artifact의 path/hash를 잠그며 PBC critic input bundle에 같은 artifact를 포함한다. 단일 제어장치면 `single_control`, 기존 PBC 관찰 근거가 충분하면 그 artifact pointer를 `not_required` basis로 기록한다. 그 범위를 넘거나 실제 제품 동작을 시험해야 하면 별도 명시 승인, 격리 workspace, production 미반영, 실서비스·민감정보 미사용, 폐기 방법을 갖춘 disposable spike만 허용한다. 그렇지 않으면 spike는 승인 뒤 첫 implementation slice로 계획한다.

### PBC-2 — Coding Plan and director review bundle

1. `plan_mode`를 `compact`, `standard`, `high_risk` 중 하나로 고른다. 고위험 run은 반드시 `high_risk`다. compact는 작은 저위험 다중 파일 기능에만 사용하며 PBC-0, AC→slice→verifier 연결, 사람 승인을 생략할 수 없다.
2. 먼저 Coding Plan의 `implementation_design` 초안을 만든다. 이 설계는 component/책임 경계, interface·state/data·external-action 경계, boundary dependency, slice 순서·dependency·기대 결과, delivery/recovery를 기록한다. logical system contract가 applicable이면 각 구현 경계가 어떤 logical flow를 실현하는지, runtime mode, state ownership, failure/recovery, 필요한 operational readiness를 명시하고, 최소 하나의 승인 핵심 scenario를 entry→processing→required persistence/external adapter→result→readback까지 관통하는 첫 end-to-end slice로 지정한다. 관련 경계가 없으면 이 slice를 `not_applicable`과 이유로 닫는다. multiple product UI surface이면 `ui_surface_delivery`에 각 surface의 핵심 scenario, entry/result-readback boundary, 처음 통합되는 slice, AC verifier를 기록한다. 전역 첫 end-to-end slice는 하나로 유지하되, 다른 UI surface를 계획 밖으로 미루지 않는다. 여러 boundary가 있으면 실제 구현 architecture와 runtime sequence 그림을 만든다.
3. 이 구현 설계를 실현하는 데 필요한 skill·model·harness·loop·graph 등을 `selection-register.json`에 selected/excluded로 기록한다. 모든 record는 version/hash가 고정된 Engineering Playbook의 구체적인 decision-rule ID를 하나 이상 참조한다. **selected** 항목에는 선택 근거, trigger/non-trigger, precondition, side-effect boundary, verifier, stop/escalation, currentness를 기록한다. **excluded** 항목에는 제외 근거, 비적용 조건, 재검토 조건만 짧게 기록한다. `compact`에서는 실제 선택했거나 현실적인 대안이었던 범주만 record로 만들고, 나머지는 `not_applicable_categories`로 한 번에 선언한다. `standard`·`high_risk`에서는 모든 범주를 selected 또는 excluded로 검토한다. 선택 Skill은 현재 environment inventory에서 확인한 이름만 쓴다.
4. 그 선택을 Coding Plan의 각 plan item에 연결한다. 모든 AC는 하나 이상의 plan item과 verifier에 연결하고, 각 plan item은 `implementation_design`의 boundary와 slice, Selection Register ref, AC refs, 결정 상태(`decided`/`provisional`), verifier, 권한 경계, 변경 수준 정책을 기록한다. 둘 이상의 제어장치를 함께 써야 verifier·권한 경계가 성립하는 경우에는 `feasibility_preflight`가 가리키는 안전한 `feasibility-probe.json`에 그 가정·제어장치·증거를 기록하고, `pass` 전에는 해당 계획을 승인하지 않는다. 단일 장치면 `single_control`, 이미 관찰된 환경 사실이면 현재 Planning Baseline 또는 Selection Register pointer를 가진 `existing_observed_evidence`만 `not_required`로 기록할 수 있다.
5. 각 plan item은 Use Case와 Prototype에서 컴파일한 `behavior`, `ui_state_interaction`, `authority_data`를 원문 의미가 바뀌지 않게 보존하고, 하나 이상의 Prototype `Page / State / Region`을 `prototype_refs`로 연결한다. 반복 UI 요소를 렌더·수정하는 item의 `ui_state_interaction`에는 해당 Prototype Component foundation의 상태·형태·token/규칙을 원문 의미가 바뀌지 않게 포함한다. 모든 Prototype 핵심 Region은 하나 이상의 plan item에 연결한다. 이 값들은 빈 요약이나 원본 경로가 아니며 G4 구현자가 plan만 읽고 구현 범위를 판단할 수 있는 계약이다.
6. `execution_policy`에서 `continuous_batch` 또는 `per_slice_gated`를 고른다. continuous batch는 필수 자동 품질 게이트, critic 승격 조건, 중단 조건을 명시한 승인된 plan item 묶음에만 쓴다. 위험·외부 연결·권한·민감 data·비가역 효과·공개 interface/data migration·성능 예산 영향은 `independent_critic` review requirement로 표시한다. UI/AI slice는 변경한 AC를 deterministic assertion, 고정 조건의 visual/interaction evidence, 또는 Verification Matrix에 정의한 명확한 pass/fail 관찰로 충분히 판정할 수 있고 다른 승격 조건이 없으면 `automatic`이다. 승인된 AC의 중요한 결과를 이 방법들로 판정할 수 없는 UI/AI 판단만 `independent_critic`으로 승격한다.
7. PBC critic 전에는 machine artifact(`coding-plan.json`, Selection Register, verification matrix, draft contract)만 만든다. 이어 `templates/pbc-consistency-check.json`으로 선택/제외, plan/verification, 이번 approval attempt의 변경 설명, 조건부 feasibility preflight가 서로 충돌하거나 이전 문구·그림을 재사용하지 않는지 검사한다. 이 check는 현재 artifact path/hash와 검사 결과를 기록하며, `pass`가 아니면 critic을 호출하지 않는다. `coding-plan.json`에는 critic 전부터 `director_review`와 diagram의 **예정 경로만** 선언하고, 그 파일은 아직 만들지 않는다. critic pass 뒤에만 고정된 plan을 수정하지 않고 그 예정 경로에 `director-review.md`와 그림을 한 번 렌더한다. critic 수정 왕복에서 사람용 문서·그림을 재생성하지 않는다.
8. 모든 plan에는 실제 내용에 대응하는 renderable `traceability` 그림과 `roadmap` 그림을 제공한다. `traceability`와 artifact reference·승인·검증 관계를 설명하는 SVG는 `artifact-dependency-tree` 방식으로 만든다. 구조·상태·위험·순수 시간 roadmap 그림은 해당 요소가 실제로 있을 때만 적합한 표현으로 추가한다. 그림은 장식이 아니라 계획을 설명해야 한다.

### PBC-3 — Verification plan

1. AC→implementation slice→test/eval→execution evidence의 verification matrix를 만든다. 각 entry에는 승인된 AC와 모든 observable condition을 그대로 복사한다. fixture/live 경계와 필요한 manual review를 기록한다. `L4`는 모든 AC의 최종 evidence 연결이며 새 테스트를 뜻하지 않는다. `L1`(핵심 규칙), `L2`(API·storage·adapter contract/integration), `L3`(entry→result→readback)은 관련 경계가 있을 때만 선정한다. applicable logical flow의 첫 end-to-end slice에는 필요한 L3 증거가 있어야 한다. multiple product UI surface의 각 `ui_surface_delivery`도 지정된 통합 slice에서 해당 surface의 핵심 scenario를 entry→result→readback으로 확인하는 L3 evidence를 가져야 한다. high risk에서는 정상 흐름의 무사고 확인만으로 통과시키지 말고, secret·권한·저장 데이터 같은 위험을 의도적으로 주입해 경계 밖에 남지 않음을 보이는 adversarial verifier를 포함한다. 각 결함 주입은 연결된 plan item과 **완료 plan item**을 함께 지정한다. 완료 item의 slice는 나머지 연결 item의 같은 slice 또는 의존 후속 slice여야 하며, 시험은 그 완료 slice에서 한 번만 실행한다. 또한 위험, **명시적인 안전 대상**(in-memory fixture·임시 로컬 파일·격리 process·loopback/local test listener 중 하나), containment, 금지된 실제 행동, fail-closed assertion, cleanup을 구조화해 기록한다. 실제 외부 주소·실서비스·secret·민감 data를 결함 주입 대상으로 쓰지 않는다. 안전한 대상과 fail-closed 증명을 정할 수 없으면 주입하지 말고 별도 승인 또는 stop/escalation으로 처리한다.

### PBC-4 — Critic and implementation authorization gate

1. 독립 critic은 **승인된 Use Case Bundle과 Prototype Bundle을 완전하고 올바른 고정 비교 기준으로 취급한다.** Evidence Pack·Use Case·Wireframe·Prototype의 품질, 기능 누락, 제품 판단을 비판하거나 재검토하지 않는다. 두 기준과 PBC machine artifact를 함께 읽어 PBC 산출물이 두 고정 입력을 손실 없이 컴파일했는지, applicable logical flow가 implementation boundary·첫 end-to-end slice·필요한 L3 evidence로 끊기지 않았는지, plan이 범위를 넓히지 않았는지, AC→plan→verifier→evidence 연결에 누락이 없는지, Selection Register가 plan mode에 맞는 선택 범주·현재 environment Skill·제품/개발 model role을 빠뜨리지 않았는지, `pbc_consistency_check`가 선택/제외·검증·logical-flow compilation·변경 설명·조건부 feasibility preflight의 충돌을 정직하게 기록했는지, 근거 없는 복잡성·불명확한 stop 조건·권한 경계가 없는지만 검토한다. Critic JSON에는 실제 비교 기준의 path/version/hash를 남긴다. PBC-4에서는 `use_case_bundle`, `prototype_bundle`, `coding_plan`, `verification_plan`, `selection_register`, `pbc_consistency_check`, `prebuild_contract`가 각각 현재 승인 input lock 또는 현재 machine artifact의 실제 경로를 가리켜야 하며, 이름만 같은 다른 파일로 대체할 수 없다.
2. PBC critic은 approval attempt마다 정확히 한 번만 호출한다. `pass`면 사람용 review bundle을 렌더하고 Human Gate로 간다. `revise`/`ask-user`면 issues와 선택지를 기록해 사람 판단으로 멈춘다. 사람의 수정 요청으로 계획을 바꾸려면 새 plan version과 새 `approval_attempt_id`를 만들며, 그 새 attempt에서만 critic을 한 번 호출할 수 있다. 자동 재호출·확인 critic·조용한 수정 후 진행은 금지한다. PBC critic의 `revise`는 PBC-0~PBC-4 artifact만 고친다. PBC `ask-user`는 승인된 제품 계약을 바꾸지 않는 구현 권한 또는 L1 계획 판단만 묻는다. AC·사용자 흐름·권한 의미·data meaning 변경은 Factory 범위 밖 계약 변경으로 기록하고 멈춘다. 모든 PBC critic도 호출 전 input bundle을 만들고, 해당 bundle의 source만 읽는다.
3. critic 전 `prebuild-contract.md`와 artifact record에는 `implementation_authorization_proposal`만 기록한다. 이 proposal은 허용할 plan version·item·execution mode·stop condition·금지/별도 승인 행동을 고정하지만 아직 사람 승인이 아니다. Human Gate의 Gate Decision에만 실제 `implementation_authorization`과 approver·time을 기록한다. `authorized: true`인 Gate Decision이 proposal과 정확히 일치할 때만 승인된 plan version과 `allowed_plan_item_ids`의 G4 구현을 시작할 수 있다. continuous batch의 경우 이 목록은 한 번에 실행 가능한 batch이며, execution mode와 stop condition도 함께 승인한다.
4. 배포, 외부 전송, 실서비스 호출, 민감정보 접근, 비가역 변경은 plan 승인만으로 허용되지 않는다. `separate_approval_required_for`에 남기고 실행 직전에 별도 승인을 받는다.
5. 사람은 `templates/pbc-4-gate-decision.json`으로 승인, 수정 요청, 보류, 제품 변경 요청 중 하나를 결정한다. 승인 이후 계획을 바꾸려면 아래 Plan amendment policy를 따른다.

### Plan amendment policy

- L0 구현 세부(승인된 private 내부 작업의 이름·작은 정리)는 plan version을 바꾸지 않고 execution log에 남긴다. 공개 contract, data, dependency, test strategy, model role, loop/harness/graph 변화는 L0가 아니다. 예상 밖 사실이 발견되면 크기와 무관하게 execution ledger의 `unexpected_facts`에 관찰 증거와 영향받는 plan item/가정/제어장치, 재확인 결과를 먼저 기록한다. `none` 또는 `L0`는 재확인이 `pass`일 때만 허용한다. 그 외에는 L1 또는 범위 밖 영향으로 승격하며 다음 slice나 repair 전에 해당 경로로 간다.
- L1 기술 계획 변화는 `plan-amendment.md`, 이전/이후 비교 그림, 영향받는 AC·slice·test, critic pass, 사람 승인이 있는 새 plan version 없이는 실행하지 않는다.
- 제품 계약 변화(AC, user flow, authority, data meaning, G2A/G2B 약속)는 PBC에서 처리하지 않는다. Factory 범위 밖 계약 변경으로 기록하고 멈춘다.
- 기계 검증은 task·evidence의 plan item ID, 승인 version, AC traceability를 확인한다. 실제 코드 의미와 제품 범위 일치는 독립 critic 또는 사람 review가 확인한다.
- 예상 밖 결과가 L1 또는 범위 밖 계약 변경을 만들면 `plan-learning-record.md`를 작성한다. 반복되거나 고위험인 실패만 `skill-improvement-proposal.md`로 승격하며, 사람 승인 전에는 Factory 규칙을 자동 변경하지 않는다.

## Build and Verification Procedure

G4~G7은 PBC-4에서 `authorized: true`로 승인된 plan version과 plan item만 실행한다. 각 cycle은 작은 vertical slice 하나다. G4에서 `slice-execution-packet.json`을 먼저 컴파일하고, G5~G7은 이 packet·현재 코드·현재 slice의 ledger/report만 읽는다. `continuous_batch`에서는 slice별 Human Gate나 독립 critic을 기다리지 않고, 필수 자동 품질 게이트와 evidence가 모두 통과한 뒤 다음 승인 item으로 계속 진행한다. `per_slice_gated` 또는 critic 승격 slice는 기존처럼 검토를 마친다. `references/05-build-verification.md`와 해당 template을 읽는다.

### G4 — Implementation contract and baseline revalidation

1. planning baseline과 현재 repository/dependency/environment를 비교한다. plan을 무효화할 변화는 PBC-1~PBC-4 재검토 또는 Amendment로 보낸다.
2. `templates/slice-execution-packet.json`으로 닫힌 실행 packet을 만든다. packet은 선택한 plan item 전문(컴파일된 behavior/UI·state·interaction/authority·data/logical flow 포함), 연결된 AC 전문과 모든 관찰 조건, 해당 verification-matrix entry 전문과 적용되는 safe adversarial case, PBC-4 authorization 전문, **원문 Planning Baseline과 이번 재검증 결과·증거**, 자동 품질 게이트·review·stop condition을 구조 그대로 포함한다.
3. G4~G7은 Use Case·Prototype·Evidence Pack·G2 artifact를 직접 주입하거나 읽지 않는다. packet은 Coding Plan, Verification Matrix, implementation authorization, planning baseline에서만 컴파일한다.
4. packet의 `unresolved_questions` 또는 `missing_information`이 비어 있지 않으면 구현을 시작하지 않는다. PBC 산출물에 구현·검증 정보가 빠졌다면 G4에서 원본을 재탐색하지 않고 L1 plan amendment 또는 범위 밖 계약 변경으로 멈춘다.
5. `implementation-contract.md`의 한 장 실행 표에는 packet path/hash, 이번 slice의 authorized plan item, AC, 실행 명령, verifier, 자동 품질 게이트, review requirement, 권한·외부 행동 경계, rollback/recovery와 stop condition만 기록한다. 별도 slice 보고서는 만들지 않는다.
6. PBC-4 authorization 밖의 코드·외부 행동은 시작하지 않는다. 별도 승인이 필요한 행동은 실행 전에 멈춘다.

### G5 — One vertical slice implementation

1. G4 Execution Card와 `slice-execution-packet.json`의 plan item만 구현한다. 요구사항·화면·권한·data meaning을 발명하거나 변경하지 않는다. packet 밖의 문서 재탐색은 G4 packet 보완 절차를 따른다.
2. 객관적 verifier가 있는 경우에만 `act → verify → targeted repair` loop를 사용한다. loop의 횟수·시간·비용 한도를 넘으면 멈추고 G7로 간다.
3. `execution-ledger.json` 한 행에 plan item, 변경 파일, 실행한 command, 자동 품질 게이트 결과, verifier 결과, evidence path, L0 세부 결정을 남긴다. ledger의 `unexpected_facts`에는 새 관찰 사실마다 영향받는 plan item·가정·제어장치와 재확인 결과를 남긴다. 자동 게이트는 최소한 plan 범위 추적과 연결된 AC verifier를 포함하고, plan에 정한 static/format/type check를 모두 통과해야 한다.
4. 동일한 사실(AC ID, plan item ID, command 결과, evidence path)은 execution ledger를 canonical source로 한 번만 기록한다. slice execution card·사람용 최종 문서는 이 원본을 참조하거나 생성해 중복 수기 전사를 하지 않는다.

### G6 — Verification and independent review

1. packet에 포함된 verification entry의 해당 AC를 unit/contract/integration/E2E/visual/manual 방식으로 실행한다. fixture와 live boundary를 지킨다. 여러 slice에 걸친 AC는 matrix의 `completion_plan_item_id`를 하나 지정한다. 완료 전 slice에서는 partial evidence와 함께 `deferred`로 기록하고, 지정 completion slice에서만 pass/fail/blocked를 최종 판정한다.
2. `verification-report.json`에 AC→plan item→실행 결과→evidence를 기록한다. test가 없거나 실패했는데 통과로 표현하지 않는다.
3. `review_requirement: independent_critic`인 slice만 독립 critic이 승인된 PBC 구현 계약과 Coding Plan에 비추어 실제 slice가 범위를 넘지 않았는지, 증거가 assertion을 뒷받침하는지 검토한다. UI/AI라는 이유만으로 critic을 요구하지 않으며, 검증할 수 없는 중요한 결과 판단일 때만 승격한다. `automatic` slice는 자동 게이트와 AC evidence가 모두 pass일 때만 계속한다. batch의 마지막에는 누적 실행 원장·검증 보고서를 입력으로 최종 통합 critic을 반드시 수행한다. 이 최종 review는 batch evidence의 완결성·cross-slice contract만 확인하며, 이미 통과한 개별 slice의 제품 판단이나 코드 스타일을 다시 심사하지 않는다.

### G7 — Cycle decision, mismatch, and learning

1. `cycle-decision.md`에서 `next_slice`, `complete`, `repair`, `amendment`, `blocked` 중 하나를 선택한다. continuous batch의 `next_slice`는 승인된 batch item과 자동 게이트가 남아 있을 때만 가능하다. `complete`에는 최종 통합 critic pass와 `batch-evidence-index.json`이 필요하다. 이 index는 batch의 packet·ledger·verification report 경로와 hash만 한 번 모으며, 추가 slice 보고서가 아니다.
2. L0는 ledger에 기록하고 repair 또는 next slice로 간다. L1은 Plan Amendment와 critic·사람 승인 전 다음 구현을 시작하지 않는다. 승인 제품 계약을 바꿔야 하는 사실은 `blocked`와 `out_of_scope_contract_change`로 기록하고 멈춘다.
3. 예상 밖 결과가 plan 변경을 만들면 Learning Record를 남긴다. `unexpected_facts`의 영향 판정이 L1 또는 범위 밖이면 Cycle Decision의 분류와 일치해야 한다. Skill 개선은 자동 적용하지 않는다.

## Safety Rules

- Vault 전체를 기계적으로 주입하지 않는다. 대신 이번 작업의 의도·목적·장기 방향을 설명하는 문서를 넓게 찾고, 선택된 Intent Context 문서는 전문으로 보존한다.
- 미확인 정보를 확정 사실로 표현하지 않는다.
- Human Gate 승인은 해당 artifact version·slice·scope에만 적용한다.
- 코드 변경은 PBC-4에서 명시 승인된 plan version·item 안에서만 허용한다. 외부 호출, 배포, 메시지 전송, 실서비스·민감정보 접근, 비가역 행동은 별도 명시 승인 전 금지한다.
- critic은 Generator의 대화 이력을 보지 않으며, write·edit·bash·network 권한이 없다.

## Verification

1. v0.8.10+ run은 `factory-profile/snapshot/skill/scripts/validate_artifacts.py <run-dir>`를 실행한다. legacy run은 현재 validator로 판정하지 않고, 해당 run의 기존 runtime으로만 확인한다.
2. run-state의 gate와 next_action이 일치하는지 확인한다.
3. artifact마다 manifest, version, status, source link가 있는지 확인한다. Use Case에는 쉬운 설명, 대응 그림, scenario coverage record가 있는지 확인한다.
4. 다음 gate로 진행하기 전에 이전 Gate Decision의 승인 여부, artifact version, scope, reviewer note를 확인한다. G3 전에는 G2A 구조 승인과 G2B 디자인 승인을 모두 확인한다.
5. PBC-4 전에는 승인 입력 lock, Coding Plan, verification matrix, critic pass, implementation authorization을 확인한다.
6. G3 승인 전과 PBC-4 승인 전에는 production code 변경이 없었는지 `git diff`로 확인한다. 승인된 disposable spike가 있었다면 격리·폐기·미반영 증거를 확인한다.
7. G4~G7에서는 implementation contract의 allowed plan item, execution ledger, verification report, independent review, cycle decision이 서로 같은 plan version과 AC를 가리키는지 확인한다.

`git` 저장소가 아닌 프로젝트에서는 코드 변경 부재를 자동으로 증명할 수 없다. 이 경우 repository snapshot에 그 한계를 기록하고, G3 승인에서 사람이 해당 경계를 확인한다.

## v0.8.20 Boundary

v0.8.20은 기존 G0~G7의 제품·구현 결과 기준을 바꾸지 않는다. `multiple` product UI surface일 때만 G0의 제품 사실, G1 Scenario, G2A Page/State, G2B의 하나의 디자인 방향 안의 surface별 적용 규칙, G3 Prototype coverage, PBC의 `ui_surface_delivery`를 연결한다. 이 surface는 후보·reference 조사 단위·별도 디자인 시스템이 아니라 모두 출시해야 하는 사용자용 UI다. 단일·non-UI 제품은 해당 record를 비워 둔다. 전역 첫 end-to-end slice는 하나로 유지하지만, PBC는 다른 UI surface의 핵심 scenario·boundary·통합 slice·L3 evidence도 승인 전에 연결한다. 새 Gate·critic·별도 풀스택 계획 문서는 만들지 않으며, PBC와 G4~G7의 direct-input 경계도 그대로 유지한다.

## Optional Factory Calibration

Factory 자체가 병목이 되는지 확인해야 할 때만, 여러 run을 묶어 준비 시간, critic 호출 수, Human Gate 번복 수, PBC 이후 L1 또는 범위 밖 계약 변경 수를 비교한다. 이는 run별 필수 artifact나 Gate가 아니며, 측정 근거 없이 절차를 늘리거나 줄이지 않기 위한 주기적 운영 점검이다.
