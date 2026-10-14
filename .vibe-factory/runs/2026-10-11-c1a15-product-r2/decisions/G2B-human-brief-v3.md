# Gate Brief: G2B / visual_design v3

## 쉬운 설명

v2 시각 방향(가이드 시각 언어)을 그대로 쓰고, 007 · 008로 생긴 화면 · 상태의 시각 규칙을 더했다.
1. 진행 표시: 완료 단계는 흰 알약 · 초록 테두리 · ›로 눌러 볼 수 있게 보인다. 현재 단계는 글자가 가장 굵은 파랑이다.
2. 지난 단계 보기 창: '제출됨'은 회색 칩 + 자물쇠(고칠 수 없음), '수정 가능'은 흰 칩 · 주황 테두리 + 연필(이 기기에만 있는 입력). 창 뒤 화면은 더 어둡게 가린다.
3. B 점검 시작 전 확인: 체크리스트는 테두리 없는 파랑 틴트 패널, 오른쪽 위에 '확인 1 / 3'. 확인 전에는 결과 버튼도 '결과 보내기'처럼 흐린 바탕 + 자물쇠로 잠긴다.
4. 등급 변경 경고: 낮춤은 주황 ⚠ + 진한 주황 저장 버튼, 올림은 파랑 ⓘ + 일반 저장 버튼.
5. 독립 Craft Review가 찾은 11건을 공통 시각 규칙에서 한 번 보정했다. 보정 뒤 T06이 화면 아래로 넘쳐 같은 보정 안에서 맞췄다(넘침 0).

## 이번에 결정할 것

| Decision | Proposed value or options | Why it matters | Evidence / artifact link |
| --- | --- | --- | --- |
| 시각 방향 v3 승인 | 승인 / 수정 | 승인하면 58개 화면 전체에 적용할 전역 시각 규칙 v3가 된다 | `wireframes/v3/design/design-review.html` |
| 체크 행 높이 | 32px(태블릿 큰 터치 규칙보다 작음) | 검토자는 44px를 권했지만 B 점검 지시가 한 화면에 들어가도록 32px로 맞췄다 | `wireframes/v3/design/direction-guide/T06.html` |

방향 수 예외 사유(direction_count_exception_reason): 시각 방향은 direction-guide 하나다(D17). v3는 v2(승인) 방향을 그대로 쓰고 G3 Human Gate(v9 승인 뒤) 사용자 결정(007 · 008)에 따른 새 화면 · 상태(T15 지난 단계 보기, T06 B 점검 시작 전 확인, L05 올림 경고)와 진행 표시 완료 단계의 누르기 단서에 쓰는 규칙을 더했다. 다른 시각 방향 4~6개를 만들면 승인된 가이드 시각 언어를 다시 고르게 하므로 승인 결정을 뒤집는다. 분리된 Craft Review에서 찾은 완성도 문제는 공통 시각 규칙에서 한 번 보정했다.

## 전체 흐름 그림

- 디자인 검토 보드: `wireframes/v3/design/design-review.html`(대표 화면 3개 before · after)
- 방향 문서: `wireframes/v3/design/direction-guide.md` · 시각 규칙 파일: `wireframes/v3/design/direction-guide.css`

## 상태·규칙·위험 그림

- 구조 · 영역 · 순서 · 기능 · 권한은 G2A v3 승인 그대로다. 바뀐 것은 시각 규칙 파일뿐이다.
- 창 뒤 막을 짙게 한 것은 공통 창 토큰이라 T07 · T13 · T14에도 같이 적용된다.
- 이미 승인된 v2 화면의 등급 배지 글자(A)가 아래로 조금 처져 보이는 점은 v2에도 있던 것으로, 이번 범위에서 바꾸지 않았다.

## 하지 않는 것

- 구조 변경(G2A)
- 승인 뒤 4.4 이후 · 등급 반영 prototype(G3)
- 코드
- push

## Human decision

Approve / revise와 reviewer note를 `decisions/G2B-visual-design.json`에 기록한다(v2 결정은 `decisions/history/`로 옮긴다).
