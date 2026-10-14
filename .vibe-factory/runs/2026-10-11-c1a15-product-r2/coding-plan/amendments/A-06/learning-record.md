# Plan Learning Record LR-06

## Original plan item and assumption

Coding Plan v6 ~ v9의 P-09(조치 · 재가동 · 호출 · 보고서 API, S-03). 생성자 해석 ②(사용자 결정 012로 승인) — "조치 뒤 정정 호출의 '승인 후 진행'은 새 작업을 열지 않고 정비자가 정정 때 하던 단계로 '이어서 하기'" — 를 P-09가 서버 상태 전이로 구현한다고 두었다. 가정은 'P-09가 호출 · 답 상태 전이를 만들 때 정정 호출의 답 처리도 함께 만들 수 있다'였다.

## Observed result and evidence

S-03 G5 · G6에서 확인한 결과(`execution/S-03/history/execution-ledger-v3.json` UF-S03-03 · UF-S03-10, `critics/G6-S03-review.json` B2 (b), `execution/S-03/history/g6-revise-decision-v2.md`):
- 이 전이는 '조치 뒤 정정'이 업무 기록에 어떻게 남는지(정정 덧붙임 형식)에 기대는데, 정정 입력 · 기록은 P-14(S-05)가 만든다.
- 그래서 S-03에서는 정정 호출 요약 화면(T10 / summary_corrected)도 만들 수 없었다(사용자 결정 016 ③).

## What was missed, and what was unknowable

알 수 있던 일이다. 생성자 해석을 item에 나눌 때 그 전이가 기대는 기록(정정 덧붙임)을 처음 만드는 item의 slice를 보지 않았다. LR-05(AC 완료 slice)와 같은 종류의 대조 누락이 계약 문장 단위에서 다시 생겼다.

## Causal category

planning(계약 문장을 맡는 item을 상태 전이 계층만 보고 정함, 기대는 기록의 생성 item을 보지 않음)

## Amendment and product-contract impact

L1 amendment A-06(plan v10): 생성자 해석 ②의 서버 상태 전이와 T10 / summary_corrected 화면 · 요약 값을 P-14(S-05)로 옮긴다. 승인된 제품 약속(결정 012 ②)은 그대로이고, 맡는 item과 slice만 바뀐다.

## Recurrence and severity

정정 · 되돌리기 · 재개처럼 '다른 item이 만드는 기록에 반응하는 전이'에서 다시 생길 수 있다. 이번에는 G6에서 잡았고 사용자에게 보이는 동작 손실은 없다(정정 입력 자체가 아직 없음).

## Prevention proposal and validation

PBC-2 · PBC-4 consistency check에서 compiled_product_contract의 각 상태 전이 문장마다 '그 전이를 일으키는 입력 · 기록을 만드는 item'을 적게 하고, 그 item의 slice가 전이를 맡는 item의 slice보다 늦으면 경고한다. LR-05의 AC 단위 대조와 같은 표에서 함께 본다.
