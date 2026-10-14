# Gate Brief: G2A / wireframe_structure v1

## 쉬운 설명

승인된 Use Case를 화면 47개로 옮겼다. 정비자 앱은 화면 11개·상태 32개, 파트장 앱은 화면 6개·상태 15개다.
- **구조:** 사용 가이드 4~17쪽 화면을 그대로 따랐다(D1, D17). 가이드의 마크업과 CSS를 그대로 썼다.
- **값:** 가이드 예시가 아니라 data/ 에서 계산한 값이다. 경보 UDI 4494 · M-03 · 온도 차 7.8 K를 썼고, 원인 순위는 명세 R4·R5 공식으로 계산했다.
- **가이드에 없는 상태:** 같은 시각 언어로 추가했다. 로그인, 반려, 호출 답 3종 등이다.
- **참고 자료:** 허락받은 경로(saasui.design) 안에서 실제 제품 화면 8개를 확인했다. 가이드 화면의 각 영역이 어떤 실제 제품 원리와 같은지만 기록했다.

## 이번에 결정할 것

| Decision | Proposed value or options | Why it matters | Evidence / artifact link |
| --- | --- | --- | --- |
| 구조 승인 | 후보 guide-a(가이드 그대로)의 47개 화면을 승인 / 일부 화면 수정 요청 | 승인한 화면이 G2B·G3의 구조 기준선이 된다 | `wireframes/structure-review.html` |
| 후보 수 예외 | 후보 1개 | D17을 지키기 위함 | 아래 사유 |
| 시연 알람 발생 방식 | 명령만 쓴다. 가이드에 없는 버튼 화면은 만들지 않는다(SC-50 non_ui) | G1에서 G2A로 넘긴 결정(CO-09)이다 | `page-inventory.json` scenario_handoffs SC-50 |
| 가이드와 다른 문구 | 추이 제목 "최근 12회 측정"(D12), 등급표 "32절 중 7절 표시"(실제 절 수), 확인 질문은 결과 버튼 없이 메모만 보낸 경우(D11) | 가이드 예시 문구를 결정에 맞게 바꿨다 | `wireframes/structure/guide-a.md` Observable differences |

후보 수 예외 사유(candidate_count_exception_reason): 후보는 guide-a 하나다. 사용자가 G0에서 'G2A·G2B는 사용 가이드 화면을 유일한 안으로 한다'(D17)를 승인했다. 그래서 다른 화면 토폴로지·정보 단위·상호작용 방식의 후보를 만들면 승인 결정을 뒤집게 된다. 제외한 구조는 세 가지다. (1) 목록-상세 분할 화면 하나에서 순위와 점검을 함께 처리하는 안: 태블릿 한 화면에 점검 하나만 보이게 한 가이드 원칙과 맞지 않는다. (2) 보드형 점검 대기열 안: 지시된 점검 하나를 따르는 흐름(AC-35)을 깨고 건너뛰기를 유도한다. (3) 파트장 앱을 받은편지함형 한 목록으로 합치는 안: 가이드 15~17쪽의 메뉴 4개 구조를 바꾼다.

## 전체 흐름 그림

- 구조 검토 보드: `wireframes/structure-review.html`
  - decision view: T04 진단 · T10 파트장 호출 · L03 보고서 검토
  - coverage view: 47개 전체
  - 화면을 누르면 선택되고, 선택 결과는 JSON으로 복사·다운로드할 수 있다.
- 참고 자료 보드: `wireframes/reference-board.html` (RP-01~RP-08)

## 상태·규칙·위험 그림

- 모든 G1 scenario 35개를 화면 상태 또는 비UI로 정확히 한 번씩 연결했다.
  - 화면 상태: 31개
  - 비UI: 4개(SC-50~53)
- 각 화면에는 논리 흐름(FLOW)을 연결했다.
- 화면의 sample 유사도는 구조 검토용 대용값(센서 거리)이다. 실제 제품은 R3로 계산한다.
- 근거 적음 상태는 표시를 확인하기 위한 예시다.

## 하지 않는 것

- 시각 디자인 결정(G2B)
- 기능·권한·AC 변경
- 코드 작성
- push
- OpenAI 호출
- 경로 밖 웹 조사

## Human decision

Approve / revise / reject와 reviewer note를 Gate Decision JSON(`decisions/G2A-wireframe-structure.json`)에 기록한다. 보드에서 받은 선택 JSON이 있으면 `wireframes/g2a-page-state-selection.json`으로 저장하고 그 경로를 함께 기록한다.
