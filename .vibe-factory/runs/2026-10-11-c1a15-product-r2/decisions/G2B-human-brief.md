# Gate Brief: G2B / visual_design v1

## 쉬운 설명

G2A에서 승인한 화면 구조 위에 최종 시각 표현을 정한다. D17에 따라 사용 가이드의 시각 언어 하나를 방향으로 썼다.
- 대표 화면: 진단(T04) · 파트장 호출(T10) · 보고서 검토(L03). 두 앱이 모두 들어가도록 골랐다.
- 검토: 화면을 만들지 않은 검토자가 실제 렌더만 보고 완성도를 점검했다.
- 보정: 공통 시각 규칙에서 한 번 고쳤다.
  - 두 열 아래 선 맞춤
  - 기록 카드 줄바꿈
  - C등급 배지 테두리
  - 호출 버튼 대비
  - 고칠 수 있는 요약 칸 표시
  - 파트장 현재 메뉴 표시

## 이번에 결정할 것

| Decision | Proposed value or options | Why it matters | Evidence / artifact link |
| --- | --- | --- | --- |
| 시각 방향 승인 | direction-guide 승인 / 수정 요청 | 승인하면 모든 47개 화면에 적용할 전역 시각 규칙(selected-visual-rules.md)으로 굳힌다 | `wireframes/design/design-review.html` |
| 호출 · 경고 주 버튼 색 | 진한 주황(#b45309)을 C · D 호출 행동에만 쓴다 | 가이드의 밝은 주황보다 대비가 높다(Craft Review 보정) | `wireframes/design/direction-guide.md` |

방향 수 예외 사유(direction_count_exception_reason): 시각 방향은 direction-guide 하나다. 사용자가 G0에서 'G2A·G2B는 사용 가이드 화면을 유일한 안으로 한다'(D17)를 승인했고, G2A에서 가이드 화면 그대로를 승인했다. 다른 서체·색·표면·조작 모양의 방향 4~6개를 만들면 승인된 가이드의 시각 언어(등급 배지 색, 큰 주 버튼, 카드 구성)를 다시 고르게 하므로 승인 결정을 뒤집는다. 그래서 G2B는 가이드 시각 언어를 그대로 쓰고, 분리된 Craft Review에서 찾은 완성도 문제만 공통 시각 규칙에서 한 번 보정했다.

## 전체 흐름 그림

- 디자인 검토 보드: `wireframes/design/design-review.html` (대표 화면 3개의 before · after)

## 상태·규칙·위험 그림

- Component foundation 13개 요소와 두 앱의 적용 차이를 방향 문서에 고정했다.
- G2A 구조(영역 · 탐색 · 순서 · 기능 · 권한)는 바꾸지 않았다.

## 하지 않는 것

- 구조 변경
- 새 기능
- 코드 작성
- push
- OpenAI 호출

## Human decision

Approve / revise / reject와 reviewer note를 Gate Decision JSON(`decisions/G2B-visual-design.json`)에 기록한다.
