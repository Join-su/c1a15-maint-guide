# Gate Brief: G1 / use_case v3

## 쉬운 설명

G3에서 정하신 결정을 Use Case에 넣었다.
- 정비자 앱 종 아이콘을 누르면 알람 · 할 일 목록이 뜬다(SC-22, 비었을 때 SC-25).
- 진단의 과거 기록 카드를 누르면 그 기록 전체를 본다(SC-23).
- '매뉴얼 원문 보기'를 누르면 그 절의 원문을 본다(SC-24).
- 순위의 '근거 n'(상위 10건 기준)과 화면의 과거 기록 3건의 차이를 화면 안내로 밝힌다(SC-02, AC-40).

v2의 승인 내용은 그대로이고, 추가만 했다. 규모는 scenario 39개, 수용 기준 40개, 논리 흐름 13개다. Critic은 1회에 pass를 냈다.

## 이번에 결정할 것

| Decision | Proposed value or options | Why it matters | Evidence / artifact link |
| --- | --- | --- | --- |
| Use Case v3 승인 | 승인 / 수정 | 승인해야 G2A v2(새 화면)로 간다 | `use-case/v3/use-case-packet.md` |
| 종 목록 항목을 누르면 가는 곳(생성자 파생, 근거에 직접 없음) | 새 알람 → 알람 화면 / 진행 중 점검 → 이어서 하기 / 호출 답 → 호출 답 화면 / 반려 보고서 → 반려 보고서 | Critic 비차단 의견. 기존 화면에 잇는 파생이라 확인을 받는다 | SC-22, AC-37 |
| 종 아이콘을 누를 수 있는 곳 | 정비자 앱 모든 화면(상단 바에 항상 있음) | 같은 이유 | SC-22 |
| 과거 기록 전체에 보일 항목 | 설비 · 발생 시각 · 증상 · 센서 값 · 점검 경로 · 확정 원인 · 조치 · 정지 시간 · 서술(명세 S2 · 이력 데이터 필드) | 같은 이유 | SC-23, AC-38 |

## 전체 흐름 그림

- Use Case 그림: `use-case/v3/use-case-map.svg`
- 논리 시스템 개요: `use-case/v3/logical-system-overview.svg`
- 대표 흐름: `use-case/v3/logical-scenario-flow.svg`

## 상태·규칙·위험 그림

- 새 논리 흐름 FLOW-13: 정비자 앱이 알람 · 세션 · 호출 · 보고서 상태를 다시 읽어 목록을 만든다.
- 과거 기록 · 매뉴얼 원문은 FLOW-03에서 지식 저장소를 읽는다.
- Critic 비차단 의견 3건은 G2A · PBC로 넘긴다(CO-19).

## 하지 않는 것

- 화면 설계(G2A)
- 시각(G2B)
- 코드
- push
- OpenAI 호출

## Human decision

Approve / revise / reject와 reviewer note를 `decisions/G1-use-case.json`에 기록한다(이전 v2 결정은 `decisions/history/G1-use-case-v2.json`).
