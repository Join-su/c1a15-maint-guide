# Plan Learning Record LR-04

## Original plan item and assumption

A-03(plan v7)의 P-19. G5 첫 중단 표가 T04에서 기록 카드(R-RECORDS)만 빠진 값으로 적었고, 순위(R-RANK)는 P-06 응답으로 충분하다고 보았다.

## Observed result and evidence

P-19 구현 전 재대조에서 R-RANK의 원인 이름이 응답에 없음을 찾았다(`execution/S-02/cycle-2/g5-stop-2.md`).

## What was missed, and what was unknowable

알 수 있던 일이다. 대조를 영역 단위로 하지 않고 '눈에 띄는 값' 단위로 했다.

## Causal category

planning(화면 값 → API 필드 대조를 영역 전수로 하지 않음)

## Amendment and product-contract impact

L1 amendment A-04(plan v8): P-19에 R-RANK. 제품 계약 변화 없음.

## Recurrence and severity

같은 대조 방식이면 다시 생긴다. 이번에는 코드 전에 잡았다.

## Prevention proposal and validation

화면 item의 prototype_refs 영역마다 '보이는 값 → 응답 필드(item)' 표를 만들고, 빈 칸이 0인지 확인한 뒤 API item 계약을 닫는다(LR-03 제안을 영역 전수로 강화).
