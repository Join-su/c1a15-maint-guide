# Gate Brief: PBC-4 / pre-build contract v5

## 쉬운 설명

Prototype이 v17로 바뀌었습니다(첫 판정이 바로 호출인 진단 화면 T04 / first_call). 그래서 구현 계획을 v5로 다시 맞췄습니다. 바뀐 범위(`approved-inputs/changed-scope-v2.md`)만 고쳤습니다.

- **P-08**(정비자 앱 화면): T04 / first_call 화면을 더합니다. 규칙 예외는 그 상태에서만 씁니다. E2E 경로도 더합니다.
- **새 P-18**(진단 미리보기 API 보강): 첫 판정이 호출일 때도 서버가 확인 점검 이름, 소요 분, 근거 검사를 거친 이유를 줍니다. 화면은 API 값만 보이기 때문입니다.
- **S-02 2차 cycle:** S-02는 1차 cycle(P-03~P-07)만 끝났습니다. 첫 end-to-end(화면까지)는 2차 cycle에서 판정합니다(P-08 · P-18).
- **OOS-01:** 해결됐습니다(결정 013).
- **함께 정리한 것:** R11 원문, 규칙 우선순위 한 줄, R3 해석, 이월 메모 CO-40~42, S-02 G6 의견 5묶음.

남은 단계: S-02 2차 cycle → S-03(조치 · 보고서) → S-04(파트장 앱) → S-05(정정) → S-06(평가 · 시연). 단계마다 사람 결정 뒤 다음으로 갑니다.

## 이번에 결정할 것

| Decision | Proposed value or options | Why it matters | Evidence / artifact link |
| --- | --- | --- | --- |
| L1 amendment A-02 · 구현 승인(P-08 ~ P-18) | 승인 / 수정 요청 / 보류 / 제품 변경 요청 | 남은 item 전부의 구현 승인. P-01 ~ P-07은 완료(계약 그대로) | `prebuild/v5/prebuild-contract.md` 'Implementation authorization proposal' |
| 새 item P-18 | 진단 미리보기 응답에 호출 판정 때의 이름 · 소요 분 · 이유(R8 검사)를 더함(공개 API 변경 → 독립 검토) | 완료된 P-06 계약을 바꾸지 않고 새 item으로 | `coding-plan/amendments/A-02/plan-amendment.md` |
| S-02 2차 cycle | 첫 end-to-end slice는 S-02 그대로, P-08 · P-18을 2차 cycle로 실행 | 첫 관통(화면 → 서버 → 다시 읽기)이 아직 판정되지 않았다 | `coding-plan/v5/coding-plan.json` execution_status |
| 실행 방식 · 별도 승인 | per_slice_gated 그대로. openapi-typescript 설치 · 시험 컨테이너 · commit · push · live OpenAI는 실행 직전에 따로 묻는다 | 구현 승인만으로 허용되지 않는다 | contract 'Authority, risk, and external-action boundary' |
| Critic 결과 | PBC4-A5 검토(뒤에 채움) | 변경 설명 A-02 | `critics/PBC4-5-review.json` |

## Human decision

Approve / revise / hold / product-change와 reviewer note, 실제 `implementation_authorization`(authorized · approved_by · approved_at, proposal과 같은 값)을 `decisions/PBC-4-prebuild-contract.json`에 기록한다(v4 결정은 history로).
