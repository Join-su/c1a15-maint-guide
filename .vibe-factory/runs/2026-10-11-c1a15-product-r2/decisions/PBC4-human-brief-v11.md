# Gate Brief: PBC-4 / pre-build contract v11

## 쉬운 설명

S-03 G6 검토에서, P-09 계약이 '조치 뒤 정정 호출에 승인 답이 오면 정정 때 하던 단계로 이어 가기'를 맡는다고 적혀 있었는데 이 전이는 정정 기록(S-05 P-14가 만듦)이 있어야 만들 수 있다는 점이 드러났습니다. P-14도 이미 같은 일을 맡고 있어 겹쳐 있었습니다. 결정하신 대로 L1 수정 A-06에서 이 일을 P-14로 정리하고, 정정 호출 요약 화면(T10 / summary_corrected) 영역도 P-09 · P-10에서 빼서 P-14 · P-15가 맡게 했습니다. 함께, 승인 답이 온 C 점검을 바로 지시하는 것(결정 016 ①)이 R5-3 점수 순서의 예외라는 점을 P-09 계약에 적었습니다.

- **그대로인 것:** AC 원문, Verification Matrix 내용, 경계, slice, 기술 선택, 금지 · 별도 승인 행동, 구현한 item의 동작(S-03에서 만든 P-09 · P-10 그대로).

## 이번에 결정할 것

| Decision | Proposed value or options | Why it matters | Evidence / artifact link |
| --- | --- | --- | --- |
| L1 amendment A-06 · 구현 승인(P-08 ~ P-19, plan v10) | 승인 / 수정 요청 / 보류 / 제품 변경 요청 | 계약 문장을 맡는 item 정리 | `prebuild/v11/prebuild-contract.md` |
| 승인 뒤 | S-03 cycle decision을 next_slice로 다시 쓰고 S-03을 닫음 → S-04 | 다음 slice | `execution/S-03/cycle-decision.md` |
| Critic 결과 | PBC4-A11 pass(차단 0 · 비차단 3건 → 실행 해석 3가지: ① P-03 계약은 바꾸지 않음 ② LR-06 판 범위 v1 ~ v9 ③ execution_status는 S-03 종료 기록 · 다음 판에서, `coding-plan/v10/director-review.md`) | | `critics/PBC4-11-review.json` |

## Human decision

Approve / revise / hold / product-change와 reviewer note, 실제 `implementation_authorization`을 `decisions/PBC-4-prebuild-contract.json`에 기록한다(v10 결정은 history로).
