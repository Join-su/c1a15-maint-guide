# G2A Reference-backed Candidate {{id}}: {{title}}

## Target actor and task

## Reference patterns

| Reference ID | Product and specific screen/pattern | URL | Observed at | Task fit | Borrowed structural principle | Explicitly not borrowed |
| --- | --- | --- | --- | --- | --- | --- |
| RP-01 | | | | | | |

## Reference surface and discovery route

- Page group / Page IDs:
- Classification (`game_ui | marketing_site | interactive_site | workflow_product | general_utility`):
- Workflow signals observed:
- Why this route fits this candidate's work model:
- Discovery source or open-search rationale:

## Candidate work model

사용자가 이 후보에서 어떤 순서로 판단·선택·완료하는지 쓴다. G1에 없는 기능·권한·data meaning을 추가하지 않는다.

| Structural axis | This candidate's explicit choice | Why it fits the target task |
| --- | --- | --- |
| First view | | |
| Navigation | | |
| Layout topology | | |
| Primary information unit | | |
| Primary action surface | | |
| Interaction mode | | |
| Information exposure | | |
| State and feedback placement | | |

다른 후보와 `Layout topology`·`Primary information unit`·`Interaction mode` 중 하나 이상, 그리고 총 세 축 이상이 달라야 한다. 색·여백·카드 스타일의 차이는 이 표의 차이가 아니다.

## Candidate viability

후보 차이를 세기 전에 모든 대응 scenario에서 이 후보가 실제로 쓸 만한지 확인한다. 더 적은 클릭 수만을 목표로 하지 않는다. 위험 작업의 확인 단계, 필요한 정보의 가시성, 실패 비용도 함께 판단한다. 계약을 훼손하거나 편익 없는 이동·재입력·맥락 전환을 만드는 후보는 제외한다.

| Scenario refs | Critical path and required information | Additional cost | Compensating benefit | Result |
| --- | --- | --- | --- | --- |
| S-01 | | none, or describe | | supports |

## Product-specific adaptations

| Adaptation ID | Reference principle | Preserved | Changed for this product | Newly designed domain behavior | Use Case / AC boundary |
| --- | --- | --- | --- | --- | --- |
| AD-01 | RP-01 | | | | |

참조 화면에 직접 존재하지 않는 제품 고유 기능도 여기서 명시한다. 참조 화면의 작업 원리는 활용하되, 해당 기능의 상태·조작·표현은 현재 Use Case에 맞게 설계한다. 외부 제품의 기능·권한·data meaning을 가져오지 않는다.

서로 다른 성격의 예시는 다음과 같다.

- 그래프·실행 흐름 기능: workflow의 진행·실패 판단 원리는 참고하되, 연결 관계·실행 상태·재시도 조작은 제품 요구에 맞게 설계한다.
- 여러 대상의 비교·선택 기능: list-detail의 탐색 원리는 참고하되, 비교 기준·선택 결과·일괄 작업은 제품의 data meaning과 권한 경계에 맞게 설계한다.
- 검토·승인 기능: review queue의 우선순위 표현은 참고하되, 승인 조건·이력·되돌리기 가능 범위는 현재 authority와 failure cost에 맞게 설계한다.

## Decision screens

기본 decision view에서 큰 화면으로 비교할 1~3개 screen을 적는다. 각 screen은 다른 후보와 같은 `Page ID / State`여야 한다.

| Page ID / State | Candidate screen path | Scenario refs | What a user does here | Observable difference from the other candidates |
| --- | --- | --- | --- | --- |
| P01 / default | wireframes/structure/{{id}}/P01--default.html | | | |

## Candidate page evidence

후보의 모든 Page ID를 한 행씩 기록한다. `match_type`은 `direct | principle | contract_designed`만 사용한다. `direct`는 보이는 구조·상태만 screenshot 근거로 주장할 수 있다. `principle`에는 차용 원리와 Adaptation ID를, `contract_designed`에는 직접 차용이 부적절한 이유와 승인 Use Case·AC 근거를 적는다.

| Page ID | States | Actor / object / primary action | Completion judgment / required information | Match type | Reference IDs / borrowed principle | Adaptation IDs | Scenario / AC refs |
| --- | --- | --- | --- | --- | --- | --- |
| P01 | default | | | principle | RP-01 / | AD-01 | S-01 / AC-01 |

## Observable differences from other candidates

색·여백·카드 모양이 아니라, 여덟 구조 축 중 무엇이 달라져 정보 구조·작업 순서·판단 지점·control surface가 어떻게 달라지는지 명시한다. 각 차이는 Candidate viability에서 확인한 편익 또는 trade-off와 연결한다.

## Strengths

## Trade-offs and likely failure points

## Page inventory coverage

| Page ID | State | Exact renderable path | Scenario covered |
| --- | --- | --- | --- |
| P01 | default | wireframes/structure/{{id}}/P01--default.html | |

모든 `page-inventory.json` 페이지·비교 상태를 한 행씩 기록한다. 이 문서는 화면을 생성하는 청사진이 아니다.

## Evidence and Use Case links

## Human Gate G2A decision
