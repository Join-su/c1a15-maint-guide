# Gate Brief: PBC-4 / pre-build contract v7

## 쉬운 설명

S-02 2차 cycle에서 정비자 앱 화면(P-08)을 만들기 전에 화면 template을 API 응답과 하나씩 대조했습니다. 화면에 보여야 하는데 API가 주지 않는 값이 있었습니다(`execution/S-02/cycle-2/g5-stop.md`). 화면은 API 값만 보일 수 있으므로, 결정하신 대로 L1 수정 A-03으로 새 item P-19를 더했습니다.

- **새 P-19**(정비자 화면 값 API 보강): 홈 교대 현황 · 알람 행 진행(점검 n / 최대 m), 알람 화면의 설비 종류 · 계통 · 센서 표(평소 범위 · 상태) · AI 해석(근거 검사 R8) · 찾은 기록 수, 과거 기록 카드 값, 잠금 전 1.2절 절차, 지시의 점검 n / 최대 m · 근거 기록, 과거 기록 승인자. 새 엔드포인트는 없고, 기존 응답에 값을 더합니다.
- **값 정의(결정 014):** 평소 범위 = 1~9월 2.5~97.5 백분위, 최대 m = 지금 혼자 할 수 있는 점검 + 이미 한 점검, 근거 기록 = 그 점검 원인으로 확정된 상위 기록 2건, 오늘 교대 = 야간 22:00~06:00 · 내 기록.
- **P-08:** 선행 조건에 P-19만 더했습니다. 화면과 시험은 v6와 같습니다.
- **그대로인 것:** P-18 코드, 설치한 패키지, AC, 경계, 기술 선택, 금지 · 별도 승인 행동.

남은 단계: S-02 2차 cycle(P-08 · P-18 · P-19) → S-03 → S-04 → S-05 → S-06. 단계마다 사람 결정을 받은 뒤 다음으로 갑니다.

## 이번에 결정할 것

| Decision | Proposed value or options | Why it matters | Evidence / artifact link |
| --- | --- | --- | --- |
| L1 amendment A-03 · 구현 승인(P-08 ~ P-19) | 승인 / 수정 요청 / 보류 / 제품 변경 요청 | 남은 item 전부의 구현 승인. P-01 ~ P-07은 완료, P-18은 구현됨(계약 그대로) | `prebuild/v7/prebuild-contract.md` 'Implementation authorization proposal' |
| 새 item P-19 | 기존 응답에 화면 값을 더함(공개 API 변경 → 독립 검토), data/alarm_rules.json에 normal_ranges | 화면이 API 값만 보이기 때문 | `coding-plan/amendments/A-03/plan-amendment.md` |
| 화면 값 정의 | 결정 014 네 가지 그대로(이탈 DEV-20) | 승인 묶음 · 명세에 정의가 없던 값 | `sources/intent/014.md` |
| 실행 방식 · 별도 승인 | per_slice_gated 그대로. 시험 컨테이너 · commit · push · live OpenAI는 실행 직전에 따로 묻는다 | 구현 승인만으로 허용되지 않는다 | contract 'Authority, risk, and external-action boundary' |
| Critic 결과 | PBC4-A7 pass(차단 0 · 비차단 3건 → 실행 해석 ① PW 센서 표 5행 구성 · 화면 밖 값 기록, ② data · OpenAPI hash를 '예상 변경'으로 기록, ③ S-03 홈 값 채우기 확인을 S-03 packet에 — `coding-plan/v7/director-review.md`) | 변경 설명 `coding-plan/amendments/A-03/plan-amendment.md` | `critics/PBC4-7-review.json` |

## Human decision

Approve / revise / hold / product-change와 reviewer note, 실제 `implementation_authorization`(authorized · approved_by · approved_at, proposal과 같은 값)을 `decisions/PBC-4-prebuild-contract.json`에 기록한다(v6 결정은 history로).
