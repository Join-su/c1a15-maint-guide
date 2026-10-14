# Plan Learning Record LR-03

## Original plan item and assumption

P-06(API 핵심, S-02 1차 cycle)과 P-18(진단 미리보기 보강). plan v3 ~ v6는 이 둘이 정비자 화면(P-08)에 필요한 값을 낸다고 보았고, 화면 값을 하나씩 대조하는 일을 P-08 구현 때로 미뤘다.

## Observed result and evidence

S-02 2차 cycle G5에서 P-08을 시작하기 전에 template 24개를 API 응답과 대조했다. 교대 현황 · 평소 범위 · AI 해석 · 기록 카드 요약 · 잠금 절차 · 점검 n / m · 근거 기록 · 승인자가 빠져 있었다(`execution/S-02/cycle-2/g5-stop.md`).

## What was missed, and what was unknowable

화면 template은 G3 v16 · v17에서 이미 정해져 있었으므로 미리 알 수 있었다. P-06을 화면 없이 만들면서 '화면 영역마다 응답 필드를 적은 대조표'를 PBC-1(plan)에 두지 않은 것이 원인이다. 평소 범위 · 최대 m · 근거 기록 · 교대의 정의가 승인 묶음에 없었던 것은 discovery 단계에서 놓친 부분이다.

## Causal category

planning(화면 값 → API 필드 대조 없이 API item을 먼저 구현)

## Amendment and product-contract impact

L1 amendment A-03(plan v7): 새 P-19, P-08 선행 조건. 승인된 제품 계약 변화는 없다. 정의가 없던 값 네 가지는 결정 014로 정했다(DEV-20).

## Recurrence and severity

API를 화면보다 먼저 구현하는 run에서 다시 생길 수 있다. 이번에는 화면 코드를 쓰기 전에 잡았고, P-18 코드는 그대로 쓴다.

## Prevention proposal and validation

API item의 verifier에 '그 API를 쓰는 화면 영역의 값 목록 → 응답 필드' 대조표를 넣고, 화면 item 전에 그 대조표가 비어 있지 않은지 PBC-3 consistency check에서 확인한다.
