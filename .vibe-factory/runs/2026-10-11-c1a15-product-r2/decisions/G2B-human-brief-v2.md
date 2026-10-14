# Gate Brief: G2B / visual_design v2

## 쉬운 설명

v1 시각 방향(가이드 시각 언어)을 그대로 쓰고 세 가지를 더했다.
1. 보고서 '확정 전 확인'을 체크박스 대신 자동 검사 상태 아이콘으로 바꿨다(사용자 결정).
   - 통과는 ✓ 초록, 실패는 ✕ 빨강이다.
   - 목록 위에 "자동 검사 · 모두 통과해야 확정할 수 있습니다"를 표시했다.
2. 새 화면(알람 · 할 일 패널, 과거 기록 · 매뉴얼 원문 창)의 시각 규칙을 정했다.
3. 독립 Craft Review가 찾은 완성도 문제를 한 번 보정했다.
   - 실패 행: 왼쪽 띠와 ✕로 표시
   - 잠긴 버튼: 🔒 표시
   - 기록 카드: 머리 한 줄로 정리
   - 안내 줄: 둘째 줄 시작점 정렬
   - 메뉴 현재 표시: 독립 띠로 분리
   - 입력칸: 선택 옵션과 다른 모양

## 이번에 결정할 것

| Decision | Proposed value or options | Why it matters | Evidence / artifact link |
| --- | --- | --- | --- |
| 시각 방향 v2 승인 | 승인 / 수정 | 승인하면 51개 화면 전체에 적용할 전역 시각 규칙 v2가 된다 | `wireframes/v2/design/design-review.html` |
| 실패 행 문구 | G3에서 '근거 없는 문장 없음 ✕'를 결과 문장('근거 없는 문장 1건')으로 바꾼다 | Craft Review가 이중 부정으로 읽힌다고 지적했다. 내용 변경이라 G3에서 처리한다 | CO-20 |

방향 수 예외 사유(direction_count_exception_reason): 시각 방향은 direction-guide 하나다(D17). v2는 v1(승인) 방향을 그대로 쓰고 G3 Human Gate 사용자 결정(004 · EV-058)의 '확정 전 확인 = 자동 검사 상태 아이콘' 규칙과 새 화면(T12 · T13 · T14)에 쓰인 패널 · 창 규칙을 더했다. 다른 시각 방향 4~6개를 만들면 승인된 가이드 시각 언어를 다시 고르게 하므로 승인 결정을 뒤집는다. 분리된 Craft Review에서 찾은 완성도 문제는 공통 시각 규칙에서 한 번 보정했다.

## 전체 흐름 그림

- 디자인 검토 보드: `wireframes/v2/design/design-review.html`(대표 화면 3개 before · after)

## 상태·규칙·위험 그림

- 구조(영역 · 탐색 · 순서 · 기능 · 권한)는 바꾸지 않았다.

## 하지 않는 것

- 구조 변경
- 새 기능
- 코드
- push

## Human decision

`decisions/G2B-visual-design.json`에 기록한다.
