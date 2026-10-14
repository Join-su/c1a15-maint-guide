# Plan Learning Record LR-01

## Original plan item and assumption

P-03(판정 엔진). PBC-2는 'R1 ~ R13 계열 순수 함수, 규칙 값은 설정 · 기본값은 명세'로 썼다. 같은 규칙을 쓰는 P-04 · P-05 · P-06 · P-07 · P-09 · P-11 · P-14 · P-16도 같은 가정이었다. 가정은 "AC 원문과 규칙 이름 · 값이 있으면 구현할 수 있다"였다.

## Observed result and evidence

S-02 G4에서 규칙 본문이 없어 packet을 완성할 수 없었다(`execution/S-02/g4-stop.md`).

## What was missed, and what was unknowable

PBC는 Use Case · Prototype 두 bundle만 입력으로 받는데, Use Case Bundle이 핵심 계산 규칙을 이름(D4 · D5)으로만 가리켰다. PBC-2 · PBC-4 독립 검토도 AC → item 연결과 컴파일 손실을 봤지만, '이름으로만 가리킨 결정의 본문'이 빠진 것은 잡지 못했다. 알 수 있었던 일이다.

## Causal category

discovery(입력 경계 안의 참조 결정 본문 누락) · verifier(PBC consistency check에 '참조 결정 본문 존재' 검사 없음)

## Amendment and product-contract impact

L1 amendment A-01(plan v4). 제품 계약 변화 없음.

## Recurrence and severity

같은 구조의 run에서 다시 일어날 수 있다(Use Case가 '지킬 결정'을 이름으로만 가리키는 경우). 이번에는 구현 전에 G4에서 잡았기 때문에 코드 손실은 없다.

## Prevention proposal and validation

G1 또는 PBC-2에서 'Known decisions to preserve'가 가리키는 결정의 본문이 bundle 또는 plan에 있는지 확인한다.

## Skill Improvement Proposal decision

`candidate` — 자동 적용하지 않는다. 사용자에게 보고한다.
