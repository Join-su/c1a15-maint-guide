# Plan Learning Record LR-05

## Original plan item and assumption

Verification Matrix(v3 ~ v8)의 AC-37(정비자 앱 종 목록 4종류 · 항목 이동 · 빈 목록). 완료 item을 P-08(S-02)로 두었다. plan_item_ids도 S-02 item(P-06 · P-08 · P-19)뿐이었다. 가정은 '종 목록 화면을 만드는 slice에서 네 종류를 모두 판정할 수 있다'였다.

## Observed result and evidence

S-02 2차 cycle G5 · G6에서 확인한 결과는 다음과 같다(`execution/S-02/cycle-2/verification-report.json` AC-37 blocked, ledger UF-C2-03).
- 배정된 새 알람 · 진행 중인 점검 · 빈 목록 안내는 통과했다.
- 파트장 답이 온 호출 · 반려된 보고서는 기록이 S-03(호출, P-09 · P-10) · S-04(파트장 답 · 반려, P-11 · P-12) 전에는 생기지 않아 판정할 수 없었다.

## What was missed, and what was unknowable

알 수 있던 일이다. PBC-3에서 AC별 완료 item을 정할 때 '관찰 조건이 기대하는 기록이 언제 처음 생기는가'를 보지 않고, 화면 영역을 그리는 item만 보았다.

## Causal category

planning(AC 완료 slice를 화면 item 기준으로만 잡음)

## Amendment and product-contract impact

L1 amendment A-05(plan v9):
- AC-37 완료를 S-04 P-13(두 앱 교차 E2E)으로 옮긴다.
- P-09 · P-10 · P-11 · P-12를 연결한다.

제품 계약 변화는 없다.

## Recurrence and severity

여러 앱 · 여러 역할의 기록을 한 화면에 모으는 AC(종 목록 · 대시보드)에서 다시 생길 수 있다. 이번에는 해당 종류를 판정하기 전에 잡았다.

## Prevention proposal and validation

PBC-3 consistency check에 '완료 item의 slice ≥ 관찰 조건이 기대하는 기록을 처음 만드는 item의 slice' 대조를 넣는다. 각 관찰 조건마다 그 기록을 만드는 item을 적게 한다.
