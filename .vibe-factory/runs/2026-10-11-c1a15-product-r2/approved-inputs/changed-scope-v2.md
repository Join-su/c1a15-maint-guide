# PBC-0 재잠금 v2 — 바뀐 범위 (2026-10-13)

`approved-inputs/approved-artifact-manifest.json` v2는 Prototype Bundle을 v16에서 v17로 바꿨다(`manifests/prototype_bundle-v17.json`). Use Case Bundle v6은 hash가 같다. PBC-1 ~ 4는 아래 범위만 다시 본다. 승인된 결정 · 선택(plan v4 · Selection Register · Playbook v4)은 바뀐 범위와 닿는 곳만 고친다.

## 승인 입력에서 바뀐 것 (Prototype Bundle v16 → v17)

| 항목 | v16 | v17 | 근거 |
| --- | --- | --- | --- |
| 파생 상태 | 7개 | 8개: **T04 / first_call** 추가 — 첫 판정이 바로 파트장 호출이면 진단 화면 구조 그대로 '다음 점검' 카드에 '파트장 호출 필요' · C 배지 · 매뉴얼 절 · 확인 점검 · 소요 분 · 이유, 주 버튼 '점검 시작'(호출 경고 토큰) → 잠금(T05) → 사전 확인 → 호출 요약(T10 / summary) | 결정 013(`sources/intent/013.md`), `decisions/G3-prototype.json` |
| 규칙 예외 | — | T04 / first_call에서만: R-NEXT에 C · D 점검 정보, '점검 시작'에 warnb(사용자 확정) | G3 v17 승인, CO-42 |
| AC 화면 조건 | AC-02 C1 · C2 = C등급 4.4가 지시로 안 나옴 · 호출 요약 | 같은 조건에 첫 판정 호출 두 경로(검색 결과 CL-2 61% · 등급 변경으로 A · B 없음)를 더함 | `prototype/v17/prototype-coverage.json` |
| 시험 장치 | 시험 막대 4개 | '첫 판정 호출 세션' 더함(fixture, 제품 UI 아님) | G3 excluded_scope |
| 이월 메모 | CO-22 · 31 · 32 · 36 · 37 · 38 | + CO-40(slice 문구) · CO-41(fixture 기록 카드 값) · CO-42(예외는 그 상태만) | run-state carryover |

AC 48개 · Scenario · 권한 · 데이터 의미 · 승인 화면 69개 · Region 252개 · G2B 시각 규칙은 바뀌지 않았다. covered 25 · deferred 23도 같다.

## PBC에서 다시 볼 곳 (plan v4 기준)

| plan item | 상태 | 바뀐 범위와의 관계 |
| --- | --- | --- |
| P-08 (S-02, 정비자 앱 화면) | 미구현 · 승인 밖 | T04 / first_call 화면을 더해야 한다. prototype_refs · 완료 AC(AC-02 화면 조건) · E2E fixture에 첫 판정 호출 경로를 더한다. OOS-01 제외 문구는 해결된 결정으로 바꾼다 |
| P-03 (S-02 완료) | 구현 · 검증 끝 | 판정 함수는 이미 첫 판정 호출을 낸다(`decide` call · top_cause_cd_only / no_ab_left). 바뀌는 것은 없음 — plan v5에서 OOS-01 문구만 정리 |
| P-06 (S-02 완료) | 구현 · 검증 끝 | 진단 미리보기 API는 이미 kind call · 절 · 등급 · 원인을 내준다. first_call 카드에 필요한 '이유' 문장 · 소요 분이 응답에 있는지 P-08 계약에서 확인한다(지금은 instruct 계열에만 reason · minutes) |
| P-09 · P-10 (S-03) | 미구현 | 호출 요약(T10)은 같은 화면. 첫 판정 호출이면 '지금까지 점검'이 '점검 전'인 경우를 더한다 |
| P-16 (S-06) | 미구현 | 변화 없음(등급 위반 0 지표 그대로) |
| Verification Matrix | v4 | AC-02 화면 조건 · P-08 E2E에 T04 / first_call 경로, CO-41(fixture 기록 카드 값)을 E2E fixture에서 맞춤 |

## plan v5에 함께 넣기로 한 것 (이전 결정)

- R11 재가동 표시 값 · 추이 그래프 줄을 P-09 등에 원문 그대로(PBC4-A4 비차단)
- OOS-01 문장의 'P-01 ~ P-07' v3 문구 정리, 규칙 우선순위 한 줄, P-04 안의 R3 해석
- S-02 G6 이월 의견 11건(`execution/S-02/cycle-decision.md` Required next action)
- P-08 ~ P-17 새 implementation authorization
