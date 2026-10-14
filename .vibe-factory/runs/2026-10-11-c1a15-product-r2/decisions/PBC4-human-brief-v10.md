# Gate Brief: PBC-4 / pre-build contract v10

## 쉬운 설명

S-02 2차 cycle에서 AC-37(정비자 앱 종 목록 4종류)을 끝까지 판정할 수 없었습니다. '파트장 답이 온 호출' · '반려된 보고서'는 S-03 · S-04에서야 생기기 때문입니다. 결정하신 대로 L1 수정 A-05에서 AC-37의 완료를 S-04 P-13(두 앱 교차 E2E)으로 옮기고, 호출 · 답 · 반려를 만드는 item(P-09 ~ P-12)을 연결했습니다. 이번 cycle에서 통과한 세 가지(새 알람 · 진행 중 점검 · 빈 목록)는 부분 증거로 남습니다.

- **그대로인 것:** AC 원문, 경계, slice, 기술 선택, 금지 · 별도 승인 행동, 구현한 item의 계약.

## 이번에 결정할 것

| Decision | Proposed value or options | Why it matters | Evidence / artifact link |
| --- | --- | --- | --- |
| L1 amendment A-05 · 구현 승인(P-08 ~ P-19, plan v9) | 승인 / 수정 요청 / 보류 / 제품 변경 요청 | AC-37 완료 slice 변경 | `prebuild/v10/prebuild-contract.md` |
| 승인 뒤 | S-02 2차 cycle의 AC-37을 deferred(완료 P-13)로 고치고 S-02를 닫음(next_slice) → S-03 | 다음 slice | `execution/S-02/cycle-2/cycle-decision.md` |
| Critic 결과 | PBC4-A10 pass(차단 0 · 비차단 3건 → 실행 해석 3가지, `coding-plan/v9/director-review.md`) | | `critics/PBC4-10-review.json` |

## Human decision

Approve / revise / hold / product-change와 reviewer note, 실제 `implementation_authorization`을 `decisions/PBC-4-prebuild-contract.json`에 기록한다(v9 결정은 history로).
