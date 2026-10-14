# G2B Design Direction direction-guide: 사용 가이드 시각 언어

## G2A structural baseline

- Selected structure version: wireframe_structure v1 (G2A 승인 `decisions/G2A-wireframe-structure.json`)
- Selected structure-render baseline path / SHA-256: wireframes/structure/selected-visual-baseline.json / d216b925696377259cd9a838f1f7bc34cc7f38ddd3bf41cb27473b08110e8333
- Structure preserved from this baseline: 모든 Region(R-TOP · R-STEP · R-RANK · R-RECORDS · R-NEXT · R-CALLHEAD · R-CALLACT · R-NAV · R-REPORTVIEW · R-DECISION), 정보 단위, 탐색, 작업 순서, 필수 정보, 상태 의미, 조작 위치
- Non-binding G2A visual treatment replaced here: 없음 — G2A 렌더가 이미 가이드 시각 언어이며, Craft Review 보정 1회(direction-guide.css)만 얹었다

## Design hypothesis and Playbook inputs

- Visual hypothesis: 승인된 사용 가이드의 시각 언어를 그대로 쓰면, 야간 정비자와 파트장이 가이드로 배운 화면을 실제 앱에서 그대로 알아보고 지금 할 행동 하나에 집중한다
- Design Playbook version: references/07-design-playbook.md (Curated 2026-10-01)
- Applied Playbook principle IDs: FL-01, FL-02, CA-02, AT-01, PO-01
- Intended work experience: 태블릿에서는 오른쪽 큰 주 버튼 하나가 지금 할 일을, 왼쪽이 판단 근거를 보인다. PC에서는 목록 → 검토 → 결정이 같은 틀에서 반복된다
- Contrast from the other directions: 다른 방향 없음(D17) — 가이드 시각 언어 자체가 유일한 방향이다

## Visual distinction

- Distinct visual axes (at least 3; comma-separated: typography_density, color_state, surface_hierarchy, item_control_form, emphasis_reading_order): typography_density, color_state, surface_hierarchy, item_control_form, emphasis_reading_order

방향이 하나라 다른 방향과 비교할 축 차이는 없다. 위 다섯 축의 실제 값은 run-state `visual_signatures`에 있다.

## Representative screens: before and after

| Page ID / State | Why this screen represents a distinct task or risk | G2A baseline path | This direction's after path |
| --- | --- | --- | --- |
| T04 / default | 정비자의 핵심 판단(순위 · 근거 · 다음 점검 하나) | wireframes/structure/selected/T04--default.html | wireframes/design/direction-guide/T04.html |
| T10 / summary | 권한 경계 위험(C등급을 지시하지 않고 호출) | wireframes/structure/selected/T10--summary.html | wireframes/design/direction-guide/T10.html |
| L03 / review | 파트장 승인 결정(이력 품질을 정하는 일) | wireframes/structure/selected/L03--review.html | wireframes/design/direction-guide/L03.html |

## Refinement impact

| Maintained structure | Changed visual expression | Observable benefit | Trade-off |
| --- | --- | --- | --- |
| 2열 배치 · 카드 구성 · 순서 | 왼쪽 열 마지막 카드를 오른쪽 아래 선까지 늘림 | 두 열 아래 선이 맞아 화면이 정돈돼 보임 | 기록 카드 아래 빈 공간 |
| 기록 카드 내용 | 유사 % 줄바꿈 금지 · 줄 단위 내림 | '유사/92%'처럼 갈라지지 않음 | 머리 줄이 두 줄이 될 수 있음 |
| 등급 배지 의미 | 모든 배지에 테두리, 경고 패널 위 C 배지는 흰 바탕 | 주황 패널 위에서도 'C 승인 필요'가 배지로 읽힘 | 배지가 조금 더 무거워 보임 |
| 호출 행동 | 호출 · 경고 주 버튼을 진한 주황으로 | 흰 글자 대비 향상, 파랑 주 버튼과 구분 | 주 버튼 색이 두 가지 |
| 요약 수정 가능 | 정비자 요약 칸을 입력칸 모양 + 연필 | 고칠 수 있다는 것이 보임 | 읽기 패널과 모양이 달라짐 |
| 파트장 메뉴 | 현재 메뉴에 강조 막대 · 굵기 · 대비 | 현재 위치를 색 없이도 구분 | 없음 |

## Design choices and trade-offs

| Axis | Choice | What it improves | What it sacrifices |
| --- | --- | --- | --- |
| Typography and density | Noto Sans KR · 화면 제목 26px 900 · 카드 제목 17px 800 · 본문 15px, 태블릿은 큰 터치 버튼과 넉넉한 행 간격, PC는 표 15px 중간 밀도 | 장갑 낀 손 · 야간 조명에서도 읽기 쉬움 | 태블릿 한 화면 정보량 |
| Color and state language | 연회색 바탕 + 흰 카드, 파랑 주 행동, 등급 A 초록 · B 파랑 · C 주황 · D 빨강 배지(글자 + 색 + 테두리), 상태는 칩 · 배너 · 아이콘 함께 | 등급 · 상태를 색 없이도 구분 | 색 수가 많음 |
| Surface and hierarchy | 1px 회색 테두리 흰 카드(그림자 거의 없음), 강조 카드만 2px 파랑 테두리, 카드 안 패널은 테두리 없는 색 바탕, 입력칸은 흰 바탕 + 1.5px 테두리 | 강조 카드 하나에 시선이 감 | 평평해 보일 수 있음 |
| Item silhouette and control form | 모서리 14~16px 카드 · 10px 패널 · 옵션, 꽉 찬 큰 주 버튼 하나 + 흰 보조 버튼, 호출 · 경고 주 버튼은 진한 주황 변형 | 주 행동 하나가 분명 | 보조 행동이 덜 보임 |
| Tone and reading order | 상단 알람 표시줄 → 진행 단계 → 왼쪽 판단 정보 → 오른쪽 지금 할 행동(주 버튼) / PC는 왼쪽 메뉴 → 제목 → 내용 → 오른쪽 결정 | 판단 → 행동 순서가 화면 배치와 같음 | 없음 |

## Component foundation

대표 화면에 실제로 반복되는 요소만 기록한다.

| Element | States and form | Token or rule | Intentional exception |
| --- | --- | --- | --- |
| 카드(.cd) | 기본 · 강조(.hl) | 흰 바탕, 1px --ln 테두리, 모서리 16px, 안쪽 여백 18 × 20px / 강조는 2px --pri 테두리 | 강조는 화면당 하나(다음 점검) |
| 카드 머리(.cd-h) | 아이콘 + 굵은 제목 + 오른쪽 칩 | 17px 800, 아이콘 --sub, 아래 14px | None |
| 주 버튼(.btn.lg.full) | 기본 · 잠김(.dis) · 호출/경고(.warnb) | 꽉 찬 폭, 높이 약 52px, --pri 바탕 흰 글자 / 잠김은 연회색 / 경고는 --btn-primary-warn #b45309 | 경고 변형은 C · D 호출 행동에만 |
| 보조 버튼(.btn.ghost) | 기본 | 흰 바탕 1px 테두리, 주 버튼과 같은 모서리 | None |
| 등급 배지(.gb) | A · B · C · D | 글자 사각형 + 이름, 바탕 틴트 + 1px 테두리(A 초록 · B 파랑 · C 주황 · D 빨강), 경고 패널 위는 흰 바탕 | None |
| 정보 칩(.ch) | blue · gray · amber · green · red · src | 999px 모서리, 13px 700, 칩 간격 8px | None |
| 순위 행(.rk) | 1순위 강조 · 나머지 | 순번 사각형 · 이름 · 막대 · % · 근거 n, 행 사이 1px 선 | None |
| 기록 카드(.hc) | 기본 | 1px 테두리, 모서리 12px, 번호 mono · 유사 % 오른쪽 · 줄바꿈 금지 | None |
| 정보 패널(.why · .pv) | 읽기 전용 · 고칠 수 있음 | 읽기: 테두리 없는 연회색 바탕 10px / 고칠 수 있음(정비자 앱): 흰 바탕 1.5px --input-border + 연필 | 파트장 앱의 정비자 요약은 읽기 전용 |
| 결정 옵션(.dopt) | 선택 · 미선택 | 1.5px 테두리 12px, 선택은 --pri 테두리 · 틴트 바탕 · 채운 라디오 | 하나만 선택 |
| 보고서 행(.rf) | 기본 | 이름 120px · 값, 첫 줄 정렬(align-items: start), 행 사이 1px 선 | None |
| 왼쪽 메뉴(.wn) | 현재 · 나머지 | 남색 바탕, 나머지 흐린 글자 500 / 현재 흰 글자 800 + 왼쪽 3px --accent 막대 + 밝은 바탕 | None |
| 진행 단계(.sp) | 완료 · 현재 · 남음 | 완료 초록 체크, 현재 파랑 번호 + 링, 남음 회색 번호 | None |

## UI surface adaptation

| UI surface ID | Preserved global rule | Surface-specific application | Reason from actor/device/task |
| --- | --- | --- | --- |
| tech | 카드 · 배지 · 칩 · 버튼 토큰, 상태 색 의미 | 1080 × 740 기준, 상단 알람 표시줄 + 진행 단계, 큰 주 버튼(높이 52px · 꽉 찬 폭), 결과 버튼 3개 큰 터치 영역 | 설비 앞 태블릿 · 터치 · 야간 단독 작업 |
| lead | 카드 · 배지 · 칩 · 버튼 토큰, 상태 색 의미 | 1280 × 620 기준, 왼쪽 남색 메뉴 230px, 표 15px · 행 간격 중간, 목록 → 검토 2열 | 사무실 PC · 마우스 · 키보드 · 여러 건 검토 |

## Visual Craft Review

- Review mode: `independent_visual_pass`
- Reviewed render paths: `wireframes/design/direction-guide/T04.html, wireframes/design/direction-guide/T10.html, wireframes/design/direction-guide/L03.html`
- Direction-level repair count (0 or 1): 1
- Outcome: `ready`
- G2A structure changed: `no`

화면을 만든 쪽과 분리된 검토자가 실제 렌더 PNG(before)만 보고 다섯 항목을 점검했다. 찾은 문제는 `wireframes/design/direction-guide.css` 한 곳에서 한 번 보정했다(after). 두 번째 Craft Review는 하지 않았다.

| Check | Result (pass or repaired) | Observed issue / direction-level repair |
| --- | --- | --- |
| Alignment | repaired | T04 두 열 아래 선 32px 어긋남, 보고서 행 이름 칸 세로 가운데 → 왼쪽 열 마지막 카드 flex:1, 행 align-items:start |
| Repeated components | repaired | 경고 패널 위 C 배지 테두리 사라짐, 주황 주 버튼 대비 약함 → 모든 배지 1px 테두리 · 경고 패널 위 흰 바탕, 호출 주 버튼 #b45309 |
| Surface and edges | pass | 카드 1px 테두리 · 모서리 14~16px · 강조 2px 규칙 일관 |
| Typography and density | repaired | '유사/92%' 줄 갈라짐, 안내 · 경로 값 이른 줄바꿈 → 유사 % nowrap, text-wrap: pretty, 값 칸 max-width 해제 |
| State clarity | repaired | 파트장 현재 메뉴가 바탕 하나로만 구분, 고칠 수 있는 요약이 읽기 패널과 같음 → 메뉴 강조 막대 · 굵기, 요약 칸 입력칸 모양 + 연필 |

## Structure preservation check

영역 배치, 탐색, 작업 순서, 기능, 권한, Acceptance Criteria는 G2A · G1 승인 그대로다. 바꾼 것은 `direction-guide.css`의 시각 규칙뿐이며 HTML 구조는 선택 화면과 같다.

## Human Gate G2B decision

`decisions/G2B-visual-design.json`에 기록한다.
