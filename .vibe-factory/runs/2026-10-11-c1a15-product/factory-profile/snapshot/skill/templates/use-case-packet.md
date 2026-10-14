# Use Case Packet: {{version}}

## Feature identity

- Feature ID: `{{stable-kebab-case-feature-id}}`
- Parent run, if any:

## 한눈에 보기

### 쉬운 설명

## 사용자 이야기

{{actor}}가 {{trigger}}가 되었을 때 {{goal}}을 하며, 잘되면 {{success outcome}}이 된다.

## Use Case 그림

- 그림 파일: `use-case-map.svg`
- Scenario와 그림 대응: `scenario-coverage.json`의 `diagram_ref`

## Name and goal

## Actor

## Trigger

## Preconditions

## Main flow

1.

## Alternate flows

## Failure and cancel flows

## Postconditions

## Acceptance criteria

- [ ]

`acceptance-criteria.json`에 각 AC의 scenario와 관찰 가능한 판정 조건을 기록한다.

## Non-goals

## Product constraints

구현에 영향을 주는 아래 항목을 source 기반으로 모두 명시한다. source에 없는 값은 빈칸으로 두지 말고 `Not known — see UA-…`로 쓰고, 해당 `UA-…`를 `unresolved assumptions`에 남긴다.

- Problem / success outcome:
- Known decisions to preserve:
- Authority boundary (who may do what):
- Data meaning and sensitivity:
- External-action boundary:
- Failure cost and required safe outcome:

## Unresolved assumptions

Product assumptions or open questions that would change a scenario, AC, authority, data meaning, external-action boundary, or failure outcome must be resolved before G1 approval. Record `none` when no such blocking unknown remains; non-product process notes do not belong here.

- Blocking product unknowns: none

## Source links

## Scenario coverage

`scenario-coverage.json`을 참조한다. 모든 기능은 inventory에 한 번 이상 나타나며, 각 coverage category는 `covered` 또는 근거 있는 `not_applicable`이어야 한다.

## Product UI surfaces

`interaction_surface_mode`가 `multiple`일 때만 `scenario-coverage.json`의 `ui_surfaces`를 표로 풀어 쓴다. 각 surface의 사용자·기기 또는 이용 맥락·독립 작업·Scenario ID를 보여 준다. 이것은 G2A의 후보나 reference 조사 surface가 아니라, 모두 출시해야 하는 제품 UI다.

## Logical system connections

- Canonical contract: `logical-system-contract.json`
- Applicability and reason:
- Human diagrams, when applicable: `logical-system-overview.svg`, `logical-scenario-flow.svg`
- This is a product-level processing/state/outcome contract. It does not choose frameworks, databases, protocols, or deployment topology.

## Critic verdict
