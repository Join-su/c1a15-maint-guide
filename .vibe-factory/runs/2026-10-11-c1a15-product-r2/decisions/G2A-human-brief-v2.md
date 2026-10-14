# Gate Brief: G2A / wireframe_structure v2

## 쉬운 설명

v1(승인) 화면 47개에 새 화면 3개를 더했고, 진단 화면 안내 문구를 고쳤다. 전체 51개 상태다.
- **T12 알람 · 할 일 목록**(목록 · 빈 목록): 종 아이콘을 누르면 현재 화면 위에 패널이 뜬다.
  - 배정된 새 알람, 진행 중인 점검, 파트장 답이 온 호출, 반려된 보고서를 묶음으로 보이고, 항목마다 이동 버튼이 있다.
- **T13 과거 기록 전체:** 진단의 기록 카드를 누르면 창이 뜬다.
  - 설비 · 발생 시각 · 증상 · 센서 값 · 점검 경로 · 확정 원인 · 조치 · 정지 시간 · 서술을 보이고, 머리에 '닫기'가 있다.
- **T14 매뉴얼 원문:** 지시의 '매뉴얼 원문 보기'를 누르면 그 절 원문이 창으로 뜬다.
- **T04 진단 안내 문구:** 근거 n은 상위 10건 기준이고, 화면 기록은 그중 3건이라는 것을 밝힌다.

새 화면 참고 자료로 RP-09(Attio 활동 패널)와 RP-10(Productboard 받은편지함 항목 행)을 추가했다. 둘 다 허락된 경로(saasui.design)에서 확인한 것이다.

## 이번에 결정할 것

| Decision | Proposed value or options | Why it matters | Evidence / artifact link |
| --- | --- | --- | --- |
| 구조 v2 승인 | 51개 화면 전체 승인 / 수정 요청 | 승인한 화면이 G2B v2 · G3 v6의 구조 기준선이 된다 | `wireframes/v2/structure-review.html` |
| 새 화면 3개의 배치 | T12는 종 아래 패널, T13 · T14는 화면 위 창(머리에 닫기) | 가이드에 없는 화면이다(D17 예외) | `wireframes/v2/structure/guide-a/T12--list.html` 등 |

후보 수 예외 사유(candidate_count_exception_reason): wireframe_structure v2: v1(승인)에 G3 Human Gate 사용자 결정(004)에 따른 새 화면 T12 알람 · 할 일 목록(새 기능) · T13 과거 기록 전체(명세 S2) · T14 매뉴얼 원문(명세 S3)과 T04 근거 안내 문구(EV-060)를 더했다. 세 화면은 가이드에 없어 같은 시각 언어로 만들었다(D17 예외). 후보는 guide-a 하나다. 사용자가 G0에서 'G2A·G2B는 사용 가이드 화면을 유일한 안으로 한다'(D17)를 승인했다. 그래서 다른 화면 토폴로지·정보 단위·상호작용 방식의 후보를 만들면 승인 결정을 뒤집게 된다. 제외한 구조는 세 가지다. (1) 목록-상세 분할 화면 하나에서 순위와 점검을 함께 처리하는 안: 태블릿 한 화면에 점검 하나만 보이게 한 가이드 원칙과 맞지 않는다. (2) 보드형 점검 대기열 안: 지시된 점검 하나를 따르는 흐름(AC-35)을 깨고 건너뛰기를 유도한다. (3) 파트장 앱을 받은편지함형 한 목록으로 합치는 안: 가이드 15~17쪽의 메뉴 4개 구조를 바꾼다.

## 전체 흐름 그림

- 구조 검토 보드: `wireframes/v2/structure-review.html`
  - decision view: T04 · T12 · L03
  - coverage view: 51개 전체
- 참고 자료 보드: `wireframes/v2/reference-board.html`(RP-01~RP-10)

## 상태·규칙·위험 그림

- G1 v3 scenario 39개를 모두 화면 상태(35개) 또는 비UI(4개)로 연결했다.
- T12는 FLOW-13에, T13 · T14는 FLOW-03에 연결했다.

## 하지 않는 것

- 시각 규칙 변경(G2B v2에서: 자동 검사 상태 아이콘)
- 기능 · 권한 변경
- 코드
- push

## Human decision

Approve / revise / reject와 reviewer note를 `decisions/G2A-wireframe-structure.json`에 기록한다(v1 결정은 `decisions/history/G2A-wireframe-structure-v1.json`).
