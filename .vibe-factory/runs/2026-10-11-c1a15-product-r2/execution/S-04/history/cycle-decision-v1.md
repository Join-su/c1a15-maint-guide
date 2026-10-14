# Cycle Decision S-04

## Verified result

S-04(packet v3, plan v10: P-11 · P-12 · P-13)의 결과는 다음과 같다.
- **자동 gate:** 12개 가운데 P-11 · P-12는 모두 pass, P-13은 ac_verifier만 fail이다(verifier ② — UF-S04-01). 적용 범위는 `evidence/gate-applicability.md` 그대로다.
- **item verifier:** P-11 · P-12 pass, P-13 fail(verifier ②만, ① · ③ · ④ · AC-37은 pass).
- **검사 결과:**
  - `scripts/check-fast`: unit 71 · component 정비자 50 · 파트장 15 · OpenAPI 재생성 diff 0
  - `scripts/verify-db`: 통합 56
  - `scripts/verify-e2e`: 권한 경계 · 알람 발생기 · checkpoint 재개 · Playwright 21(교차 6) · smoke
- **구조 대조:** packet 부록 v2 기준 영역 68 — 일치 37 · 분류된 차이 28 · slice 밖 3(T12 / empty) · 기준 전용 4, 미분류 0.
- **비밀값:** 증거 폴더 비밀값 검사 0건, 결함 주입은 검출.

AC 결과:
- pass 13: AC-06 · 08 · 10 · 11 · 12 · 23 · 24 · 25 · 26 · 27 · 29 · 37 · 42
- fail 1: AC-09 — C1 L3 화면 문구 미충족, C2는 pass
- deferred 1: AC-17(완료 P-17)

G6 독립 검토 이력:
- 1차 `critics/G6-S04-review.json` revise — B1 AC-09-C1 L1 분류, B2 AC-29 · AC-25-C4 L3 근거, B3 결정 018 ③ ④ 화면 구조 대조 누락, 비차단 3
- 2차 `critics/G6-S04-2-review.json` pass — 비차단 3(사용자 결정으로 G7 전 반영)
- 3차 `critics/G6-S04-3-review.json` pass — 비차단 3(아래 '이어받을 일')

사용자 결정 기록:
- `g6-revise-decision.md`(history v2와 그 뒤 G7 범위 추가)
- G4 결정 `sources/intent/017.md` · `018.md`(① ~ ⑤, G5 중 ⑥, 수리 중 7 정정)
- run-state 이탈 기록 DEV-24 · 25 · 26

## Decision

`amendment`

UF-S04-01(L1)은 AC-09-C1 '승인 뒤 같은 증상군 알람의 검색 후보에 그 보고서가 포함된다'에 관한 것이다.
- 승인 보고서는 다음 같은 증상군 알람의 R3 검색 대상(BM25 · 의미 색인)에 들어 순위가 매겨진다(승인 전 없음 → 승인 뒤 BM25 3위 · 합친 20위).
- 그러나 진단 화면의 과거 기록 후보(상위 10건)에는 들지 않는다.
- 그래서 Matrix AC-09 L3 '진단 과거 기록 후보에 다시 읽힘'과 P-12 · P-13 verifier 문장은 화면으로 충족되지 않는다.

사용자 결정('검증 문구만 고침', `g6-revise-decision.md` G6 2차 뒤 결정)에 따라 L1 수정 A-07(plan v11)을 만든다.
- A-07은 Matrix AC-09 L2 · L3와 P-11 · P-12 · P-13 verifier 문장을 사용자 결정 018 ⑥('검색 대상에 들어 순위가 매겨지고 R-번호 기록이 열림, 상위 10건 포함은 보장 안 함')으로 맞춘다.
- 이전 승인에서 '다음 plan 판에서'로 미룬 정리도 함께 넣는다(사용자 'A-07에 함께 정리').
- 제품 동작은 바꾸지 않는다.
- 처리 순서: PBC-4 독립 검토 한 번 → 사람 승인.
- 승인 뒤 S-04 cycle decision을 next_slice로 다시 쓰고 S-04를 닫는다.

## Evidence and remaining plan items

- **기록:** packet `slice-execution-packet.json`(v3), 실행 카드 `implementation-contract.md`(v2), ledger `execution-ledger.json`(v3), 보고서 `verification-report.json`(v3), 증거 `evidence/`, history 사본 `history/`.
- **남은 plan item:** S-05(P-14 · P-15), S-06(P-16 · P-17). 둘 다 PBC-4 v11 authorization 안에 있다.

## Mismatch classification

`L1`

- 승인된 AC 원문 · 관찰 조건 · 흐름 · 권한 · 데이터 의미는 그대로다.
- AC-09-C1의 '검색 후보'를 무엇으로 확인하는지(Matrix L2 · L3 기대 증거와 item verifier 문장)만 바뀐다.

## Unexpected-fact impact check

| ID | 영향 | 처리 |
| --- | --- | --- |
| UF-S04-01 | L1 | 이 결정(amendment A-07) |
| UF-S04-07 | none | T12 / empty는 S-02에서 확인, 전 화면 대조는 P-17 |
| UF-S04-02 · 03 · 04 · 05 · 06 · 08 · 09 · 10 · 11 | L0 | 같은 slice에서 고치고 다시 검증(pass), 또는 사용자 결정 017 · 018 · G6 revise 결정 |

## Carried tasks

다음 slice와 plan 판으로 넘기는 일이다.

- **ledger scope_notes에서:**
  - S-05: 정정 입력 · 기록(P-14), T10 / summary_corrected, 정정 호출 승인 이어 가기(A-06), 반려 뒤 추가 점검 경로, L06 / correction
  - S-06: 평가 실행 경로의 alarms.eval_mode(P-16)
  - P-17: 전 화면 대조
  - live 전 실패 셈 정의
- **AC-23-C2 문장:** '파트장 확인 중' 상태가 결정 018 ③으로 없어졌다(UF-S04-08). AC 원문은 승인 제품 산출물이라 A-07에서 바꾸지 않는다. packet 실행 해석(결정 018 ③)으로 둔다.
- **G6 3차 비차단 의견 셋(기록 · 주석, 다음 slice G4 때 정리):**
  - AC-09 순위 출력의 실행 명령 · DB 기록과 pgvector 순위 한계를 report에도 적기
  - cross.spec.ts 시험 제목 · 옛 주석과 structure-dom-capture 주석
  - 부록 extracted_at 재기록(hash는 그대로)과 packet v3 version_note

## Required next action

1. **A-07 plan v11:**
   - Matrix AC-09 L2 · L3 기대 증거와 P-11 · P-12 · P-13 verifier를 결정 018 ⑥ 문장으로 맞춘다.
   - execution_status 구조 필드를 S-01 ~ S-03 완료 · S-04 진행으로 고친다.
   - note의 A-05 · A-06 근거를 history 사본 경로로 바꾼다.
   - P-19 번호 순서는 확인만 한다(이미 순서대로).
   - LR-06 판 범위 정정 줄은 LR-07에 둔다.
2. 계약 v12 → PBC-4 독립 검토 한 번(PBC4-A12) → 사람 승인(그때 묻는다).
3. 승인 뒤 S-04 cycle decision을 next_slice로 다시 쓰고, slice 산출물을 slice_history로 옮긴다. S-05 G4는 지시 때 한다.
4. commit · push는 사용자 지시 때만 한다.

## Final Integration Critic Review

해당 없음 — complete 결정이 아니다(S-06 끝 batch 통합 검토).

## Batch Evidence Index

해당 없음 — complete 결정이 아니다.
