# Plan Learning Record LR-07

## Original plan item and assumption

Coding Plan · Verification Matrix v1 ~ v10의 AC-09 L3와 P-12 verifier(v1부터) · P-13 verifier(S-04)는 AC-09-C1('승인 뒤 같은 증상군 알람의 검색 후보에 그 보고서가 포함된다')을 '다음 같은 증상군 알람의 정비자 진단 과거 기록 후보에 다시 읽힘'으로 확인하게 두었다. 가정은 '승인 보고서는 다음 같은 증상군 알람의 진단 상위 10건에 들어간다'였다.

## Observed result and evidence

S-04 G5 · G6에서 확인한 결과다(`execution/S-04/history/execution-ledger-v3.json` UF-S04-01, `critics/G6-S04-review.json` B1, `execution/S-04/evidence/ac09-r3-positions.txt`).
- 승인 보고서는 R3 검색 대상에 들어 순위가 매겨진다(승인 전 없음 → 승인 뒤 BM25 3위 · pgvector 82위 · 합친 20위).
- 그러나 진단 화면 상위 10건에는 들지 않는다. 순위는 질의 · 이력 300건 · 임베딩(fixture 가짜 임베딩)에 달려 있다.
- 정비자 기록 창은 진단 카드 · 지시 근거 번호로만 열린다.

## What was missed, and what was unknowable

계획 때 알 수 있던 일이다. 이력 300건 가운데 같은 증상군 기록이 수십 건이고 상위 10건만 진단에 보인다는 것은 R3 정의와 데이터에서 계획 때 알 수 있었다. 그런데 AC 문장의 '검색 후보'를 화면 상위 10건으로 좁혀 읽고, 순위가 데이터에 달린 결과를 확인 문장으로 삼았다. G5에서 사용자 결정(018 ⑥)을 받았지만 packet에 싣지 않아 G6에서 L1로 다시 잡혔다.

## Causal category

planning(데이터 · 순위에 달린 결과를 결정적 확인 문장으로 둠) + execution recording(G5 중 사용자 결정을 packet 실행 해석으로 싣지 않음)

## Amendment and product-contract impact

L1 amendment A-07(plan v11): Matrix AC-09 L2 · L3와 P-11 · P-12 · P-13 verifier를 '검색 대상에 들어 순위가 매겨지고 R-번호 기록이 열림(상위 10건은 보장 안 함)'으로 맞춘다. AC 원문 · 제품 동작은 그대로다.

## Recurrence and severity

검색 · 순위 · 추천처럼 데이터에 달린 결과를 화면 위치로 확인하는 AC에서 다시 생길 수 있다. 이번에는 G6에서 잡았다. 사용자에게 보이는 동작 손실은 없다(승인 보고서는 검색 대상에 들어감).

## Prevention proposal and validation

- PBC-3 Verification Matrix를 만들 때, 기대 증거가 순위 · 상위 n건 · 유사도 같은 데이터 의존 결과이면 '결정적으로 보장되는가'를 적게 한다. 보장되지 않으면 포함 여부가 아니라 대상 포함 · 순위 매김 · 전후 대조로 확인 문장을 쓴다.
- G5 중 사용자 결정이 AC 판정 방식을 정하면 그 자리에서 packet 실행 해석으로 싣는다(G6 전에).

## 정정 — LR-06 판 범위(PBC4-A11 실행 해석 ②)

LR-06(`coding-plan/amendments/A-06/learning-record.md`)의 'Coding Plan v6 ~ v9의 P-09'는 'Coding Plan v1 ~ v9의 P-09'로 읽는다. 생성자 해석 ②를 P-09에 둔 것은 plan v1부터다. LR-06 파일은 PBC-4 v11 consistency check hash로 잠겨 있어 고치지 않고, 이 절로 정정한다.
