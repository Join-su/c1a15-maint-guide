# Gate Brief: PBC-4 / pre-build contract v9

## 쉬운 설명

P-19(정비자 화면 값 API)를 구현하기 전에 화면 template 24개를 다시 대조했습니다. 진단 화면(T04)의 원인 후보 순위에 원인 이름이 보여야 하는데 API가 원인 코드만 주고 있었습니다(`execution/S-02/cycle-2/g5-stop-2.md`). 결정하신 대로 L1 수정 A-04로 P-19에 그 영역을 더했습니다.

- **P-19:** 세션 응답에 cause_names(원인 코드 → 매뉴얼 원인 표의 이름)를 더합니다. 이미 있는 % · 근거 n 값은 그대로입니다.
- **그대로인 것:** 다른 item 18개, AC, 경계, slice, 기술 선택, 결정 014, 금지 · 별도 승인 행동.

## 이번에 결정할 것

| Decision | Proposed value or options | Why it matters | Evidence / artifact link |
| --- | --- | --- | --- |
| L1 amendment A-04 · 구현 승인(P-08 ~ P-19, plan v8) | 승인 / 수정 요청 / 보류 / 제품 변경 요청 | 공개 API 응답에 필드 하나를 더함 | `prebuild/v9/prebuild-contract.md` 'Implementation authorization proposal' |
| 실행 해석 | v8 승인의 실행 해석(PW 센서 표 5행 · hash 예상 변경 기록 · S-03 홈 값 확인)을 그대로 이어 감 | 같은 slice | `decisions/history/PBC-4-prebuild-contract-v8.json` |
| Critic 결과 | PBC4-A9 pass(차단 0 · 비차단 3건 → 실행 해석 3가지 — `coding-plan/v8/director-review.md`) | 변경 설명 `coding-plan/amendments/A-04/plan-amendment.md` | `critics/PBC4-9-review.json` |

## Human decision

Approve / revise / hold / product-change와 reviewer note, 실제 `implementation_authorization`(authorized · approved_by · approved_at, proposal과 같은 값)을 `decisions/PBC-4-prebuild-contract.json`에 기록한다(v8 결정은 history로).
