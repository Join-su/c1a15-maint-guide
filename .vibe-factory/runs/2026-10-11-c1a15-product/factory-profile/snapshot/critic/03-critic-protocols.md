# Critic Protocols

## Input and alignment rule

Critic은 현재 draft/result와 gate별 선언된 비교 기준만 받는다. 호출 전 Generator가 만든 `critic-input-bundle.json`의 subject·comparison source만 읽고, bundle 밖의 source는 추가하지 않는다. subject는 `G0=evidence_pack`, `G1=use_case`, `G3=prototype`, `PBC-4=prebuild_contract`, `G6=verification_report`의 현재 run-state artifact여야 한다. 비교 기준에 비추어 결과물이 누락·왜곡·범위 확대 없이 만들어졌는지를 판정한다. 승인된 비교 기준의 제품 품질·의도·결정을 다시 비판하거나 수정하지 않는다. 모든 critic JSON에는 input bundle path/hash와 실제로 읽은 기준의 artifact/path/version/hash를 `reference_artifacts`로 남긴다. Generator의 채팅 이력·숨은 추론·선택되지 않은 Vault 전체는 받지 않는다.

| Gate | 비교 기준 | 검토 대상 |
| --- | --- | --- |
| G0 | Context Packet 전문 Intent Context, source manifest | Evidence Pack |
| G1 | Evidence Pack | Use Case Bundle |
| G3 | 승인 Use Case Bundle, G2A structure render baseline, G2A 승인 페이지 청사진, G2A selected structure contract, G2B selected visual rules | Prototype Bundle |
| PBC-4 | 승인 Use Case Bundle, 승인 Prototype Bundle | Coding Plan, Verification Matrix, Selection Register, implementation authorization proposal |
| G6/final | 승인 PBC 구현 계약 | ledger, verification report, batch evidence |

## Economy and completeness rule

Critic은 의미 정합성의 독립 점검자이며 schema·필수 field·path·hash·중복·형식처럼 validator 또는 gate consistency check가 판정할 수 있는 문제의 대체자가 아니다. 호출 전 Generator는 해당 Gate에서 가능한 기계 검증을 먼저 통과시킨다. Critic은 그러한 기계적 결함만을 blocking issue로 내지 않는다. 기계적 결함 때문에 비교 자체가 불가능하면 `unverifiable-plan` 또는 해당 Gate의 `insufficient-evidence` 하나로 멈추며, 세부 형식 오류 목록을 새 critic 작업으로 만들지 않는다.

한 critic은 선언된 input bundle에서 발견한 모든 blocking issue를 한 번에 제시한다. 각 issue는 비교한 subject·reference와, 왜 자동 검증만으로 해결할 수 없는 의미 문제인지, 요구하는 최소 수정 또는 사람 판단을 밝혀야 한다. 같은 input bundle을 다시 열어 뒤늦은 issue를 추가하지 않는다. 비차단 의견은 최대 세 개이며, 범위 밖 개선·취향·코드 스타일은 기록하지 않는다.

## Verdict

- `pass`: blocking issue 없음
- `revise`: source로 해소 가능한 blocking issue 있음
- `ask-user`: 사람 답에 따라 scope, authority, flow, data, acceptance가 달라짐
- `insufficient-evidence`: source 재확인 후에도 핵심 근거 없음

## Limits

- G0 Evidence Pack: draft 1회 + critic 최대 3회. 각 회차의 `revise`는 source로 해소 가능한 문제만 재작성한다. 어느 회차의 `pass`도 즉시 확정이며, 3회 뒤 남은 blocking issue는 사용자 질문 또는 insufficient-evidence로 멈춘다.
- G1 Use Case: 기본 draft 1회 + critic 1회 + source 기반 재작성 최대 1회.
- G3 Prototype: 초안 critic 1회 + `revise`일 때 source 기반 수정본의 확인 critic 최대 1회. 확인 critic도 `revise`이면 세 번째 자동 critic을 호출하지 않고, 남은 issue와 선택지를 사람에게 제시한다.
- 질문: gate당 최대 3개
- 새 요구사항, UI, 기술 구조를 발명하지 않음
- 문서 길이 자체를 품질로 간주하지 않음
- Intent Context가 task detail만 담고 사용자 목표·현재 우선순위·기존 결정·장기 방향을 빠뜨렸는지 검사한다.
- Use Case critic은 글·그림의 형식 일치보다 먼저 각 scenario가 Evidence Pack의 problem, Actor, success outcome, constraint, authority boundary, failure cost, known decision과 맞는지 검사한다. logical system contract가 applicable이면 scenario·AC마다 entry, 처리 책임, state/readback, 외부 의존, success/failure/cancel outcome이 Evidence Pack과 Use Case promise에서 누락·왜곡되지 않았는지만 검사한다. 기술 구조·framework·DB 선택은 G1 critic 범위가 아니다.
- Evidence Pack이 `multiple` product UI surface를 말하면, Use Case critic은 각 surface의 actor·device/context·독립 작업과 Scenario·권한 배정이 source와 맞는지만 확인한다. surface를 G2A 후보나 reference 조사 단위로 취급하거나 별도 제품 요구를 만들지 않는다.
- G0 critic은 특정 MVP·실험·단계의 결정을 제품 전체 요구로 확대하지 않았는지, Core premises와 Direction constraints가 현재 구조에 반영됐는지 검사한다.
- Evidence Pack에 근거 없는 scenario, Evidence Pack의 핵심 목표를 빠뜨린 scenario, 기존 결정을 뒤집는 scenario, 성공 기준을 관찰할 수 없게 만드는 scenario는 blocking issue다. 그림·coverage 검사는 이 의미적 정합성 검사 뒤의 보조 검사다.
- G3 verification critic은 AC의 관찰 조건이 실제 assertion·실행 증거에 모두 연결됐는지, 선택 축별 variation check가 있는지, G2A `selected-visual-baseline.json`의 구조·작업 흐름·핵심 상호작용과 G2B의 최종 시각 표현·승인된 Component foundation이 Prototype에 각각 보존됐는지, G2A `selected-structure-contract.json`의 모든 핵심 `Page / State / Region`이 Prototype의 `compiled_structure_contract`에 원문 그대로 복사되고 `structure_coverage`·prototype evidence에 정확히 한 번 연결됐는지를 검사한다. `derived_states`가 있으면 각 상태가 G1 scenario·AC에 근거하고 같은 승인 Page/State의 구조·탐색·작업 순서·핵심 Region을 보존하는지만 검사한다. 새 영역·탐색·작업 순서·제어 방식이면 G3에서 허용되지 않는다. `selected-visual-baseline.json`은 구조 기준선이고 `selected.md`는 사람이 읽는 guardrail이며, `selected-structure-contract.json`은 machine-readable 핵심 구조 기준이고, G2B 승인 디자인과 Component foundation이 최종 시각 표현 기준이다. critic JSON은 `wireframe_structure` reference로 세 파일의 실제 path·hash를 기록한다. 승인 화면·청사진·디자인의 품질이나 구조 선택 자체는 비판하지 않는다. 화면 전환이나 screenshot만으로 기능 통과를 주장하면 `revise`다.
- PBC-4 critic은 locked Use Case Bundle과 Prototype Bundle의 품질·누락·제품 결정을 심사하지 않는다. 두 bundle은 이미 승인된 immutable **비교 기준**이다. PBC critic은 두 기준과 PBC **machine artifact**를 함께 받아 Coding Plan이 behavior·UI/state/interaction·authority/data와 applicable logical flow를 손실 없이 컴파일했는지, 반복 UI 요소를 렌더·수정하는 plan item이 Prototype의 승인된 Component foundation을 `ui_state_interaction`에 보존하는지, `implementation_design`이 component/책임·interface·state/data·external-action 경계·dependency·slice sequence·delivery/recovery와 첫 end-to-end path를 먼저 정하고 모든 plan item을 그 설계에 연결하는지, Verification Matrix가 모든 AC·관찰 조건과 필요한 L3 evidence를 보존했는지, 모든 AC가 plan item·verifier·evidence에 연결됐는지, Selection Register가 plan mode에 맞는 범주·현재 Skill inventory·모델 역할을 빠뜨리지 않았는지 검사한다. `pbc_consistency_check`는 selected/excluded·plan/verifier·logical flow compilation·이번 변경 설명 artifact 사이의 충돌 여부와 현재 hash를 기록하는 보조 machine artifact다. Critic은 이를 신뢰 선언으로 받아들이지 않고, 기록된 path/hash와 판정 근거가 현재 PBC artifact와 맞는지 확인한다. `implementation_authorization_proposal`은 허용 범위·실행 mode·중단 조건·금지/별도 승인 행동을 고정하는 critic input이지만 사람 승인은 아니다. compact에서는 실제 선택·현실적 대안만 record가 되고 나머지는 `not_applicable_categories`로 한 번에 선언될 수 있다. 모든 Selection Register record는 hash 고정 Engineering Playbook의 구체적인 decision-rule ID를 참조해야 하며, Playbook이 제품 계약을 바꾸는 근거로 쓰이면 안 된다. 선택한 engineering 방식의 trigger/non-trigger와 stop 조건도 확인한다. 사람용 계획서·그림은 critic `pass` 뒤 같은 machine plan version에서 한 번만 렌더하며 critic input이 아니다. 실제 `implementation_authorization`과 approver/time은 이후 Human Gate Decision에만 기록한다. 계획의 문서 길이나 기술 화려함은 통과 근거가 아니다.
- multiple product UI surface일 때 PBC-4 critic은 각 `ui_surface_delivery`가 해당 surface의 핵심 Scenario, entry/result-readback boundary, 통합 slice, L3 evidence로 이어지는지 확인한다. 전역 첫 end-to-end slice를 여러 UI로 억지로 확장하거나, 한 surface의 제품 계약을 다른 surface에 재적용해서는 안 된다.
- PBC-4 critic은 둘 이상의 실행 제어장치가 verifier 또는 authority boundary의 성립에 필요한 경우 Coding Plan의 feasibility preflight가 실제 조합·격리·관찰 증거를 갖고 `pass`했는지 확인한다. `verified` preflight의 `feasibility_probe` 또는 `existing_observed_evidence` basis는 input bundle에 명시 source로 포함되어야 하며, critic은 그 source 밖 증거를 읽지 않는다. high-risk adversarial verifier는 안전 대상·containment·금지된 실제 행동·fail-closed assertion·cleanup과 completion plan item을 가져야 하며, 실제 외부 행동을 요구하면 `unsafe-authorization`이다.
- PBC-4 critic은 approval attempt마다 정확히 한 번만 호출한다. `revise` 또는 `ask-user`이면 자동 재호출·확인 critic·조용한 수정 후 진행 없이 사람 판단으로 멈춘다. 사람이 PBC 수정 요청을 결정하면 새 plan version과 새 approval attempt를 만들고, 그 attempt에서 한 번만 검토한다.
- PBC-4의 `ask-user`는 implementation authorization 또는 L1 계획 판단만 대상으로 한다. 승인된 AC·사용자 흐름·권한 의미·data meaning에 관한 질문은 내지 않고 범위 밖 계약 변경으로 기록한 뒤 멈춘다.
- PBC-4 critic은 `missing-traceability`, `plan-contract-mismatch`, `scope-creep`, `unjustified-complexity`, `unverifiable-plan`, `unsafe-authorization`, `baseline-drift`만 blocking issue로 사용할 수 있다. verdict는 PBC artifact의 수정만 요구하며 G0~G3 재작업을 요구하지 않는다.
- PBC-4 critic은 plan amendment 권한을 주지 않는다. implementation authorization의 allowed plan items, prohibited actions, separate approvals가 명확하지 않으면 `revise`다.
- G6 critic은 `independent_critic` slice 또는 final integration에서만 호출한다. slice execution packet, implementation contract, execution ledger, verification report를 비교한다. UI/AI slice가 deterministic assertion, 고정 조건 visual/interaction evidence, 또는 Matrix의 명확한 pass/fail 관찰로 모든 변경 AC를 판정하고 다른 위험 trigger가 없으면 `automatic`이며 G6 critic을 호출하지 않는다. blocking은 `scope-creep`, `unsafe-authorization`, `unverifiable-plan`으로 한정하고, non-blocking note는 최대 3개다. final integration은 batch evidence의 완결성과 cross-slice contract만 읽으며, 통과한 개별 slice의 제품 판단·코드 스타일·추가 개선을 재심사하지 않는다. 예시·fixture 세부, 문구 선호, 요청되지 않은 개선은 review 범위 밖이다.
- high-risk slice의 adversarial case가 있으면 G6 critic은 packet의 안전 계약과 결과의 fail-closed assertion·evidence가 대응하는지도 확인한다.

## Recording

- Critic 통과 artifact는 `status: critic_passed`와 artifact manifest를 기록한다.
- G0 Evidence Pack은 `critic_reviews`에 1~3개의 review path와 `critic_attempts`를 기록한다. 마지막 review만 `pass`일 수 있으며, pass 뒤에는 추가 review를 만들지 않는다.
- Human Gate 승인 뒤에는 artifact를 `status: approved`로 올리고, 같은 version을 가리키는 Gate Decision을 `decisions/`에 기록한다. PBC-4의 실제 authorization만 PBC-4 Gate Decision에 기록한다.
- 거절·수정은 새 artifact version으로 기록한다. 이미 승인된 version을 덮어쓰지 않는다.
- G1은 첫 critic이 `revise`이면 source 기반 재작성 뒤 확인 전용 critic을 한 번 더 호출한다. 이 확인 pass가 없으면 Human Gate에 가지 않는다.
