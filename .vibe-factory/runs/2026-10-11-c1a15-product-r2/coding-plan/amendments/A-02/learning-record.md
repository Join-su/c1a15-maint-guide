# Plan Learning Record LR-02

## Original plan item and assumption

P-06(API 핵심)의 진단 미리보기. plan v3 · v4는 OOS-01(첫 판정 호출 화면)을 제외하면서 '서버의 호출 판정 함수와 호출 요약 화면은 승인대로 만든다'고 썼고, 진단 미리보기 응답은 점검 지시 경로만 기준으로 설계됐다.

## Observed result and evidence

G3 v17에서 첫 판정 호출 화면(T04 / first_call)이 정해지자, 그 카드가 요구하는 확인 점검 이름 · 소요 분 · 이유를 미리보기 API가 내지 않는다는 것을 PBC-0 재잠금의 바뀐 범위 확인에서 찾았다(`approved-inputs/changed-scope-v2.md`).

## What was missed, and what was unknowable

화면이 정해지지 않은 상태라 필요한 응답 필드를 미리 알 수 없었다(알 수 없던 일). 다만 '제외한 화면이 정해지면 그 화면에 값을 내는 API item도 다시 본다'는 문장을 OOS-01 처리 규칙에 넣었으면 더 빨리 보였다.

## Causal category

discovery(제외 범위가 서버 계약에 미치는 영향)

## Amendment and product-contract impact

L1 amendment A-02(plan v5): 새 P-18. 제품 계약 변화 없음.

## Recurrence and severity

제외 범위(OOS)를 두고 앞 slice를 먼저 구현하는 run에서 다시 생길 수 있다. 이번에는 화면 구현 전에 잡았다.

## Prevention proposal and validation

OOS를 둘 때 그 화면에 값을 내는 API · 경계 item을 함께 적고, OOS 해결 때 그 item의 응답 필드를 대조한다.
