# Gate Brief: PBC-4 / pre-build contract v3

## 쉬운 설명

승인한 Use Case(v6)와 Prototype(v16)을 구현 계획으로 옮겼다. 계획은 6단계(slice)로 나뉜다.

1. 저장소 · DB · 적재
2. 정비자 앱 진단 첫 관통
3. 조치 · 보고서
4. 파트장 앱 · 두 앱 교차
5. 정정
6. 평가 · 시연

단계마다 사람 결정 뒤 다음 단계로 간다. 이 판이 독립 검토를 통과하면 사람용 검토 자료(`coding-plan/v3/director-review.md`)와 그림 4장을 한 번 만들어 구현 승인을 묻는다.

## 이번에 결정할 것

| Decision | Proposed value or options | Why it matters | Evidence / artifact link |
| --- | --- | --- | --- |
| 구현 승인(P-01 ~ P-07) | 승인 / 수정 요청 / 보류 / 제품 변경 요청 | 이번 승인 요청은 S-01 전체와 S-02의 화면 없는 item뿐. P-08 이후는 OOS-01 화면 결정 뒤 새 판에서 | `prebuild/v3/prebuild-contract.md` 'Implementation authorization proposal' |
| 실행 방식 | `per_slice_gated`(slice마다 사람 결정) | 권한 · 감사 경계가 있는 item이 많다 | `coding-plan/v3/coding-plan.json` execution_policy |
| 별도 승인 행동 | 설치 · image pull · 시험 컨테이너 실행 · live OpenAI · commit · push는 실행 직전에 따로 묻는다 | 구현 승인만으로 허용되지 않는다 | contract 'Authority, risk, and external-action boundary' |
| 범위 밖 OOS-01 | 첫 판정이 바로 호출인 진단 화면은 이 plan으로 만들지 않는다. S-02에서 T04 구현 전에 반드시 멈추고 화면을 정한다(2026-10-12 결정) | 승인 화면에 없는 상태, 등급 변경으로도 생김 | `coding-plan/v2/decisions/pbc4-a2-user-decisions.md` |
| Critic 결과 | PBC4-A1 revise(4건) → PBC4-A2 revise(1건) → PBC4-A3 **pass**(비차단 3건 — 실행 해석으로 승인 때 정함) | 사람용 검토 자료 `coding-plan/v3/director-review.md` · 그림 4장 `coding-plan/v3/diagrams/` | `critics/PBC4-3-review.json` |

## Human decision

Approve / revise / hold / product-change와 reviewer note, 실제 `implementation_authorization`(authorized · approved_by · approved_at, proposal과 같은 값)을 `decisions/PBC-4-prebuild-contract.json`에 기록한다.
