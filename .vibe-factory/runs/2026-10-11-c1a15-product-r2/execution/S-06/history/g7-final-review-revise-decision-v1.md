# S-06 마지막 batch 통합 검토 1차 revise — 사용자 위임 권장안 (2026-10-14)

- 검토 기록: critics/G6-FINAL-review.json. 판정 revise, 차단 2 · 비차단 3.
- 처리 근거: 사용자 지시(2026-10-14) "보안 문제가 있는 중요한 사항이 아니라면 모두 권장 방향으로 진행". 차단 · 비차단 모두 보안 문제가 아니라 기록 · 시험 보강이라, 멈추지 않고 권장안으로 처리한다.
- 구현자 확인: 두 주장 모두 사실이다.
  - B1: S-01 · S-02 현재 판은 execution-ledger-v2.json · verification-report-v2.json이다(run-state slice_history).
  - B2: CO-31 ① · OOS-01 뒷부분 · CO-40 결과는 S-02 2차 cycle 기록 어디에도 없다.

| 항목 | 권장안 | 할 일 |
| --- | --- | --- |
| B1 색인이 v1 기록을 가리킴 | 고쳐 다시 대조 | batch-evidence-index v2: earlier_slices · acceptance_coverage가 S-01 · S-02 v2 기록과 S-02 2차 cycle 현재 기록을 가리키게 하고 결과를 다시 대조한다 |
| B2 수동 검토 3건 기록 없음 | 지금 확인하고 기록 | ① CO-31 ①: 마지막 빌드 T06 / b_precheck(4.3 B, 절차 4단계)를 1080 × 740 틀에서 열어 행 높이 · 간격 · 넘침을 잰다. ② OOS-01: T04 / first_call 앱 화면을 packet 부록 template(같은 앱 CSS)과 나란히 캡처해 사용자에게 보고한다. PBC 이전 v17 캡처는 다시 읽지 않는다. ③ CO-40: 실제 값(결함 복사본 10개 · Z-1 ~ Z-5)을 수동 검토 대조표에 적는다. 수동 검토 7건 전부를 evidence/manual-reviews.md 한 표로 모은다 |
| 비차단 ① AC-41 · AC-44 수리 note | 적음 | index acceptance_coverage에 S-06 수리 증거 note |
| 비차단 ② 작은 기록 불일치 | 고침 · 기록 | DEMO-03 E2E에 '주간 처리' 미확인 행 단언을 더한다. packet v2 slice_scope_note '1건'(실제 5건)은 cycle decision에 정정으로 적는다(hash 묶인 packet은 판을 올리지 않음). S-06 cycle-decision.md는 G7에서 만든다 |
| 비차단 ③ 실패 카드 단축률 | 고침 | 실패 카드는 Agent 분 = 기준 분(단축 0)으로 센다. 단위 시험을 더하고, G6-S05-2 비차단 ② ③은 최종 보고로 옮긴다 |

다음: 위 처리 → 증거 다시 받기(C9) → ledger · report v2 · index v2 → 통합 검토 2차.
