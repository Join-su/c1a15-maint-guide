# Gate Brief: PBC-4 / pre-build contract v12

## 쉬운 설명

S-04 G6 검토에서 AC-09-C1('승인 뒤 같은 증상군 알람의 검색 후보에 그 보고서가 포함')의 확인 문장이 문제로 드러났습니다.
- 계획은 이를 '다음 알람 진단 화면 상위 10건에 다시 읽힘'으로 확인하게 적었습니다.
- 실제로는 승인 보고서가 검색 대상에 들어 순위가 매겨지지만, 상위 10건 밖(합친 20위)입니다.

결정하신 대로 L1 수정 A-07에서 확인 문장만 결정 018 ⑥('검색 대상에 들어 순위가 매겨지고 R-번호 기록이 열림, 상위 10건은 보장 안 함')으로 맞췄습니다. 대상은 Matrix AC-09 L2 · L3와 P-11 · P-12 · P-13 verifier입니다. 이전 승인에서 '다음 판에서'로 미룬 실행 상태 정리도 함께 했습니다.

- **그대로인 것:** AC 원문 · 관찰 조건, item 계약, 경계, slice, 기술 선택, 금지 · 별도 승인 행동, 구현한 item의 동작(S-04에서 만든 P-11 · P-12 · P-13 그대로).

## 이번에 결정할 것

| Decision | Proposed value or options | Why it matters | Evidence / artifact link |
| --- | --- | --- | --- |
| L1 amendment A-07 · 구현 승인(P-08 ~ P-19, plan v11) | 승인 / 수정 요청 / 보류 / 제품 변경 요청 | AC-09-C1 확인 문장 정리 | `prebuild/v12/prebuild-contract.md` |
| 승인 뒤 | S-04 cycle decision을 next_slice로 다시 쓰고 S-04를 닫음 → S-05 | 다음 slice | `execution/S-04/cycle-decision.md` |
| Critic 결과 | PBC4-A12 pass(차단 0 · 비차단 3건 → 실행 해석 3가지: ① 승인 기록에 'AC-09-C1은 진단 상위 10건 · 카드 포함을 약속하지 않음' 확정 ② S-04 닫을 때 report AC-09에 순위 출처 · 한계 ③ LR-07 정밀도는 다음 학습 기록 정정 절, `coding-plan/v11/director-review.md`) | | `critics/PBC4-12-review.json` |

## Human decision

Approve / revise / hold / product-change와 reviewer note, 실제 `implementation_authorization`을 `decisions/PBC-4-prebuild-contract.json`에 기록한다(v11 결정은 history로).
