# Pre-build Contract planning

## Boundary

PBC의 직접 product truth는 승인된 Use Case Bundle과 Prototype Bundle뿐이다. Use Case는 intent·authority/data·scenario·AC와 필요 시 기술 없는 `logical_system_contract`를, Prototype은 구조·디자인·page/state·interaction·AC evidence를 완결적으로 보존해야 한다. Use Case Bundle manifest는 `use_case_packet`, `use_case_map`, `scenario_coverage`, `acceptance_criteria`, `logical_system_contract`를, Prototype Bundle manifest는 `prototype_slice`, `prototype_renderable`, `prototype_coverage`, `variation_evidence`, `execution_evidence`를 각각 path와 hash로 잠근다. Evidence Pack·G2A·G2B는 이 두 bundle을 만든 상위 artifact이며 PBC가 직접 읽지 않는다. PBC를 시작하기 전에는 앞 단계의 raw 작업 context만 compact하고, 이 두 bundle은 새 context에서 직접 읽는다. 그 뒤 PBC는 이 정보를 Coding Plan의 compiled product contract와 Verification Matrix의 완전한 AC/observable-condition record로 옮긴다. 이후 G4~G7은 이 PBC 산출물만 직접 읽고 pre-PBC artifact를 읽지 않는다. Wiki와 repository discovery는 implementation method를 고르는 근거이며, 새로운 user flow, AC, role, authority, data meaning, 화면 구조를 만들 근거가 아니다. 충돌이나 필요한 제품 변화는 PBC가 해결하지 않고 범위 밖 계약 변경으로 기록한 뒤 멈춘다.

## Implementation design before technical selection

Coding Plan은 skill·model·engineering 목록이 아니라 전체 구현 설계다. 먼저 component/책임 경계, interface·state/data·external-action 경계, boundary dependency, slice sequence, delivery/recovery를 `implementation_design`으로 결정한다. logical system contract가 applicable이면 boundary·plan item이 해당 flow를 명시하고, 하나의 승인 핵심 scenario를 entry→processing→필요한 persistence/external adapter→result→readback으로 완주하는 첫 end-to-end slice와 필요한 L3 evidence를 정한다. 이 규칙은 관계없는 subsystem을 첫 slice에 억지로 포함시키지 않는다. 그 다음 Selection Register가 이 설계를 실현하는 skill·model·harness·loop·graph 등의 선택·제외를 기록한다. 각 plan item은 하나 이상의 design boundary와 slice, selected Selection Register record, 그리고 Prototype Bundle 안에 컴파일된 하나 이상의 `Page / State / Region`에 연결돼야 한다. 모든 Prototype 핵심 Region은 적어도 하나의 plan item으로 이어진다. PBC는 G2A를 다시 읽지 않고 Prototype이 보존한 이 구조 계약만 사용한다.

Engineering Wiki는 product truth가 아니라 기술 선택 근거다. Wiki 원문은 PBC run마다 복제하지 않는다. 대신 Wiki에서 미리 정리·검토한 versioned **Engineering Playbook**을 PBC-1의 유일한 기술 지식 입력으로 사용한다. Playbook은 원 Wiki 문서·section, 검토일, version을 밝히고, 각 decision rule에 ID·적용 신호·권장/비권장 방법·verifier/stop·재검토 조건을 둔다. Selection Register는 Playbook path·version·SHA-256·검토일을 고정하고, 모든 record가 하나 이상의 decision-rule ID를 참조한다. 누락되거나 낡은 rule은 PBC 중 즉석 보완하지 않고 별도 knowledge-curation 작업에서 Playbook을 갱신·versioning한 뒤 다시 PBC-1부터 사용한다. Wiki와 Playbook 모두 사용자 흐름·AC·권한·data meaning·UI 구조를 바꾸는 근거로 사용할 수 없다.

## Mode selection

| Mode | Use when | Minimum review bundle |
|---|---|---|
| `compact` | 작은 저위험 다중 파일 기능, 외부·민감·비가역 영향 없음 | input lock, concise plan, traceability/roadmap, AC verification matrix, approval |
| `standard` | 일반 UI/workflow 또는 여러 subsystem 변경 | full PBC-0~PBC-4 bundle |
| `high_risk` | sensitive data, authority, money, external execution, irreversible effect, high failure cost | standard plus authority, failure/recovery, explicit external-action approval |

Mode는 문서 양이 아니라 risk와 검증 필요에 따라 선택한다. compact도 scope lock과 Human Gate는 생략하지 않는다. 다만 compact Selection Register는 실제로 선택했거나 현실적인 대안이었던 범주만 상세 record로 남기고, 나머지 범주는 `not_applicable_categories` 한 목록으로 선언한다. standard와 high_risk는 모든 범주를 selected 또는 excluded로 검토한다.

## Execution compression policy

PBC-2 must select an execution mode. `continuous_batch` is appropriate only for a pre-authorized set of low-risk plan items with explicit automatic quality gates, critic escalation triggers, and stop conditions. `per_slice_gated` remains appropriate when each slice needs a decision before the next one.

Every plan item declares `automatic` or `independent_critic` review. Use independent critic for external or authority changes, sensitive/irreversible effects, public interfaces or migrations, performance-budget impact, and unexpected failures. UI/AI is an independent-review reason only when an important changed AC cannot be judged by deterministic assertion, fixed-condition visual/interaction evidence, or an explicit pass/fail observation defined in the Verification Matrix. An automatic slice still requires its AC verifier and every planned automatic quality gate to pass; build success alone is insufficient. A final integration critic reviews the accumulated batch evidence before completion, limited to evidence completeness and cross-slice contract alignment.

The compact per-slice artifact is a one-table execution card plus a row in the execution ledger. The PBC critic compares PBC machine artifacts with the approved Use Case and Prototype bundles; it does not re-evaluate those bundles. Only a passing critic result triggers one director review bundle for the same plan version. The final human-facing summary remains the other normal human document.

## Director review bundle

사람용 문서는 critic pass 뒤 machine plan과 같은 version/hash를 사용해 한 번 렌더한다. `director_review`와 diagram path는 critic 전 Coding Plan에 예약만 하고, pass 뒤 그 예약 경로에 파일을 생성한다. 이때 Coding Plan 자체를 수정하지 않는다. `implementation_authorization_proposal`은 critic 전에 고정하고, 실제 승인자·시각을 포함한 authorization은 Human Gate Decision에만 기록한다. 최소 두 그림은 필수다. artifact reference·승인·검증 관계를 설명하는 SVG는 `artifact-dependency-tree`를 사용해 정확한 producer→consumer content edge와 control/lineage edge를 구분한다. critic 수정 왕복 중에는 사람용 문서를 만들거나 다시 만들지 않는다.

1. traceability: Scenario → AC → plan item/slice → verifier → evidence
2. roadmap: slice 순서, dependency, gate, stop/escalation

구조·state·risk 그림은 해당 요소가 있을 때만 renderable SVG/PNG/HTML로 추가한다. 각 그림은 쉬운 설명과 ID legend를 가져야 한다.

## Pre-critic consistency check

PBC-4 critic 직전에 `pbc-consistency-check.json`을 만든다. 이는 별도 critic·승인 문서가 아니라 현재 machine artifact의 짧은 self-check다. 다음 세 검사를 모두 `pass`로 기록한다.

1. `selected_vs_rejected`: 각 plan item의 채택 방식·제외 방식과 Selection Register의 selected/excluded 결정이 서로 같은 방식을 채택·제외하지 않는지 확인한다.
2. `plan_vs_verification`: Coding Plan의 verifier·권한/중단 경계가 Verification Matrix의 방법·예상 증거·fixture/live 경계와 충돌하지 않는지 확인한다.
3. `logical_flow_compilation`: applicable logical flow가 Use Case Bundle에서 plan item·implementation boundary·첫 end-to-end slice·필요한 L3 evidence까지 빠짐없이 이어지는지 확인한다.
4. `change_representation`: 이번 approval attempt에서 설명하는 변경이 plan·contract·delta/그림 등 명시된 변경 설명 artifact에 같은 의미로 반영됐는지 확인한다. 변경 설명 artifact가 없으면 빈 목록으로 명시한다.
5. `feasibility_preflight`: Coding Plan의 `not_required` 이유 또는 각 coupled-control probe의 plan item·제어장치·격리·증거가 현재 plan·verification·authority boundary와 충돌하지 않는지 확인한다.

각 검사는 실제로 읽은 artifact path와 SHA-256, 검토한 plan item 또는 AC ID, 간단한 판정 근거를 남긴다. hash가 현재 artifact와 다르거나 `pass`가 아니면 critic을 호출하지 않는다. 이 check는 승인된 제품 계약을 다시 평가하거나 새 요구를 만들지 않는다.

## Technical decision record

선택된 engineering item은 requirement signal, options, selected/rejected reason, trigger/non-trigger, precondition, side effect/authority, verifier, stop/escalation, currentness/revalidation trigger를 가진다. 제외된 item은 제외 이유, 비적용 조건, 재검토 trigger만 간결하게 남긴다. plan item은 selected item만 참조한다. `provisional` item은 확정에 필요한 관찰·verifier·decision owner를 추가한다.

## Feasibility preflight and spike policy

PBC는 production implementation phase가 아니다. 기본은 code spike 금지다. 다만 둘 이상의 실행 격리·harness·process 제어가 함께 authority boundary 또는 verifier의 성립을 좌우할 때는, `feasibility_preflight`로 조합 호환성을 먼저 확인한다. 이는 제품 동작이나 source를 시험하는 spike가 아니라, 임시 workspace에서 해당 제어장치가 함께 적용되는지만 보는 internal compatibility probe다.

이 probe는 product/dependency source 변경, 외부 연결, 실서비스·secret·민감 data·배포를 하지 않고 command, control set, isolation, expected/observed result, evidence, cleanup을 조건부 `feasibility-probe.json`에 남긴다. Coding Plan은 이 artifact의 path/hash를 잠그고 PBC critic input bundle은 같은 artifact를 명시 source로 받는다. `pass`하지 못하면 해당 plan item을 승인하지 않는다. 단일 제어장치라면 `single_control`, 이미 관찰된 환경 사실이면 현재 Planning Baseline 또는 Selection Register의 path/hash pointer가 있는 `existing_observed_evidence`만 `not_required`로 쓸 수 있다. 실제 제품 동작, 외부 환경, credential이 필요하면 별도 허가된 disposable spike만 격리 workspace, 명시 scope, no production merge, no real secret/live call, disposal evidence를 사용한다. 그 외의 spike는 승인 후 첫 slice에 둔다.

## Plan changes and learning

L1 Amendment는 새 전체 plan version과 다음을 제공한다: one-page delta, before/after diagram, observed evidence, alternatives, AC/slice/test impact, preservation statement, critic verdict, human decision. 제품 계약 변화는 PBC 밖의 범위이며 run을 멈춘다.

Execution ledger의 unexpected fact는 먼저 영향을 받는 plan item·가정·제어장치와 재확인 결과를 기록한다. 영향이 L1 또는 제품 계약 범위 밖이면 Learning record는 가정과 실제 증거, 놓친/알 수 없던 신호, causal category, recurrence/severity, prevention proposal, validation method를 기록한다. 고위험 실패는 한 번이라도 improvement proposal 후보가 될 수 있다. 그 외에는 반복 또는 다른 run에 일반화되는 근거가 있어야 한다.

## Evidence and session handoff

Execution ledger는 실제 command 결과, evidence path, AC/plan-item ID의 canonical record다. 실행 카드와 최종 요약은 이 기록을 참조·생성하며 같은 사실을 별도로 수기 전사하지 않는다. Agent 또는 세션이 바뀌는 경우에만 `execution-handoff.md`에 현재 packet path/hash, 승인 plan version·item, 완료/미완료 verifier, blocker와 다음 안전한 action을 남긴다. 이는 slice마다 추가하는 보고서가 아니며, 새 담당자는 이를 hash 검증한 뒤 재개한다.
