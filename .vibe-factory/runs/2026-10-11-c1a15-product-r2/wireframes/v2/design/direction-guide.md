# G2B Design Direction direction-guide: 사용 가이드 시각 언어 (v2)

## G2A structural baseline

- Selected structure version: wireframe_structure v2 (G2A 승인 `decisions/G2A-wireframe-structure.json`)
- Selected structure-render baseline path / SHA-256: wireframes/v2/structure/selected-visual-baseline.json / 9e53627e1facfec03017b1a696f9c5f67b23379e40023bc0c203c0ce614477ad
- Structure preserved from this baseline: 모든 Region(v2 구조 계약 172개), 정보 단위, 탐색, 작업 순서, 필수 정보, 상태 의미, 조작 위치
- Non-binding G2A visual treatment replaced here: 확정 전 확인의 체크박스 모양 → 자동 검사 상태 아이콘(004 · EV-058), Craft Review 보정 1회(`wireframes/v2/design/direction-guide.css`)

## Design hypothesis and Playbook inputs

- Visual hypothesis: 승인된 사용 가이드 시각 언어를 그대로 쓰되, 자동 검사 결과를 사람이 누르는 체크와 다른 모양으로 보이면 확정 전 판단이 헷갈리지 않는다
- Design Playbook version: references/07-design-playbook.md (Curated 2026-10-01)
- Applied Playbook principle IDs: FL-01, FL-02, CA-02, AT-01, PO-01
- Intended work experience: 정비자는 지금 할 행동 하나와 자동 검사 결과를 바로 구분하고, 파트장은 목록 → 검토 → 결정을 같은 틀에서 반복한다
- Contrast from the other directions: 다른 방향 없음(D17) — 가이드 시각 언어 v2가 유일한 방향이다

## Visual distinction

- Distinct visual axes (at least 3; comma-separated: typography_density, color_state, surface_hierarchy, item_control_form, emphasis_reading_order): typography_density, color_state, surface_hierarchy, item_control_form, emphasis_reading_order

## Representative screens: before and after

| Page ID / State | Why this screen represents a distinct task or risk | G2A baseline path | This direction's after path |
| --- | --- | --- | --- |
| T04 / default | 정비자의 핵심 판단(순위 · 근거 안내 · 다음 점검 하나) | wireframes/v2/structure/selected/T04--default.html | wireframes/v2/design/direction-guide/T04.html |
| T09 / draft | 확정 전 자동 검사(v2에서 바뀐 규칙)와 보고서 행 | wireframes/v2/structure/selected/T09--draft.html | wireframes/v2/design/direction-guide/T09.html |
| L03 / review | 파트장 승인 결정 | wireframes/v2/structure/selected/L03--review.html | wireframes/v2/design/direction-guide/L03.html |

## Refinement impact

| Maintained structure | Changed visual expression | Observable benefit | Trade-off |
| --- | --- | --- | --- |
| 확정 전 확인 3항목 · 순서 | 체크박스 → ✓ / ✕ 상태 아이콘 + '자동 검사' 보조 문구 | 누를 수 있는 체크와 구분(사용자 피드백 해소) | 체크리스트(T08)와 모양이 달라짐 |
| 보고서 행 · 실패 상태 | 실패 행에 왼쪽 띠 + ✕, 행 안쪽 여백 | 흑백에서도 실패 행이 보임 | 행이 조금 넓어 보임 |
| 잠긴 주 버튼 | 흐린 바탕 · 흐린 글자 · 🔒 | 잠김이 모양으로 보임 | 없음 |
| 기록 카드 머리 | 한 줄 · 유사 % 중립 잉크 | 머리 줄 끊김 해소, 초록 의미 충돌 해소 | 설비 · 월이 길면 줄임표 |
| 안내 줄 · 메뉴 · 입력칸 | 내어쓰기 정렬, 독립 띠, 입력칸 표면 구분 | 정렬 · 상태 · 조작 종류 구분 | 없음 |

## Design choices and trade-offs

| Axis | Choice | What it improves | What it sacrifices |
| --- | --- | --- | --- |
| Typography and density | Noto Sans KR · 화면 제목 26px 900 · 카드 제목 17px 800 · 본문 15px, 태블릿은 큰 터치 버튼과 넉넉한 행 간격, PC는 표 15px 중간 밀도 | 야간 · 장갑 조건 가독성 | 태블릿 한 화면 정보량 |
| Color and state language | 연회색 바탕 + 흰 카드, 파랑 주 행동, 등급 A 초록 · B 파랑 · C 주황 · D 빨강 배지(글자 + 색 + 테두리), 상태는 칩 · 배너 · 아이콘 함께 · 자동 검사 통과 ✓(초록) / 실패 ✕(빨강, 굵게), 유사 %는 중립 잉크(초록은 완료 · 통과에만) | 상태를 색 없이도 구분 | 색 수가 많음 |
| Surface and hierarchy | 1px 회색 테두리 흰 카드(그림자 거의 없음), 강조 카드만 2px 파랑 테두리, 카드 안 패널은 테두리 없는 색 바탕, 입력칸은 흰 바탕 + 1.5px 테두리 | 강조 카드 하나에 시선 | 평평해 보일 수 있음 |
| Item silhouette and control form | 모서리 14~16px 카드 · 10px 패널 · 옵션, 꽉 찬 큰 주 버튼 하나 + 흰 보조 버튼, 호출 · 경고 주 버튼은 진한 주황 변형 | 주 행동 하나가 분명 | 보조 행동이 덜 보임 |
| Tone and reading order | 상단 알람 표시줄 → 진행 단계 → 왼쪽 판단 정보 → 오른쪽 지금 할 행동(주 버튼) / PC는 왼쪽 메뉴 → 제목 → 내용 → 오른쪽 결정 | 판단 → 행동 순서가 배치와 같음 | 없음 |

## Component foundation

대표 화면과 새 화면에 실제로 반복되는 요소만 기록한다.

| Element | States and form | Token or rule | Intentional exception |
| --- | --- | --- | --- |
| 카드(.cd) | 기본 · 강조(.hl) | 흰 바탕, 1px --ln 테두리, 모서리 16px, 안쪽 여백 18 × 20px / 강조는 2px --pri 테두리 | 강조는 화면당 하나(다음 점검) |
| 카드 머리(.cd-h) | 아이콘 + 굵은 제목 + 오른쪽 칩 | 17px 800, 아이콘 --sub, 아래 14px | None |
| 보조 버튼(.btn.ghost) | 기본 | 흰 바탕 1px 테두리, 주 버튼과 같은 모서리 | None |
| 등급 배지(.gb) | A · B · C · D | 글자 사각형 + 이름, 바탕 틴트 + 1px 테두리(A 초록 · B 파랑 · C 주황 · D 빨강), 경고 패널 위는 흰 바탕 | None |
| 정보 칩(.ch) | blue · gray · amber · green · red · src | 999px 모서리, 13px 700, 칩 간격 8px | None |
| 순위 행(.rk) | 1순위 강조 · 나머지 | 순번 사각형 · 이름 · 막대 · % · 근거 n, 행 사이 1px 선 | None |
| 정보 패널(.why · .pv) | 읽기 전용 · 고칠 수 있음 | 읽기: 테두리 없는 연회색 바탕 10px / 고칠 수 있음(정비자 앱): 흰 바탕 1.5px --input-border + 연필 | 파트장 앱의 정비자 요약은 읽기 전용 |
| 결정 옵션(.dopt) | 선택 · 미선택 | 1.5px 테두리 12px, 선택은 --pri 테두리 · 틴트 바탕 · 채운 라디오 | 하나만 선택 |
| 진행 단계(.sp) | 완료 · 현재 · 남음 | 완료 초록 체크, 현재 파랑 번호 + 링, 남음 회색 번호 | None |
| 주 버튼(.btn.lg.full) | 기본 · 잠김(.dis) · 호출/경고(.warnb) | 꽉 찬 폭, 높이 약 52px, --pri 바탕 흰 글자 / 잠김은 #eef0f3 바탕 · 흐린 글자 · 1px 테두리 · 아이콘 대신 🔒 / 경고는 --btn-primary-warn #b45309 | 경고 변형은 C · D 호출 행동에만 |
| 기록 카드(.hc) | 기본 | 1px 테두리, 모서리 12px, 머리 한 줄(번호 mono · 설비 · 월 줄임 · 유사 % 오른쪽 중립 잉크), 초록은 쓰지 않음 | None |
| 보고서 행(.rf) | 기본 · 실패(.fail) | 이름 120px · 값, 첫 줄 정렬, 행 안쪽 여백 12px, 실패는 왼쪽 3px 빨강 띠 + 이름 앞 ✕ + 옅은 빨강 바탕 | None |
| 자동 검사 행(.ckl .ck) | 통과(.on) · 실패(.no) | 상자 없음, 통과 ✓ 초록 · 실패 ✕ 빨강(실패 문구 굵게), 목록 위 보조 문구 '자동 검사 · 모두 통과해야 확정할 수 있습니다', 누를 수 없음 | 사람이 누르는 체크리스트(T08 .act .ck)는 기존 상자 모양 유지 |
| 왼쪽 메뉴(.wn) | 현재 · 나머지 | 남색 바탕, 나머지 흐린 글자 500 / 현재 흰 글자 800 + 밝은 바탕 + 왼쪽 3px 독립 띠(모서리와 분리) | None |
| 안내 줄(.hint) | 기본 | 아이콘 16px 칸 + 문장 칸(줄이 바뀌어도 문장 시작점 정렬) | None |
| 입력칸(.memo.sm3) | 기본 | #f6f8fb 바탕 · #c9d0db 테두리 · 모서리 8px(선택 옵션 카드와 구분) | None |
| 목록 패널(.panel) | 열림 | 종 아이콘 아래 흰 패널, 1px 테두리 · 모서리 16px · 그림자, 묶음 머리 13px 굵게, 항목 행 = 상태 점 · 2줄 요약 · 이동 버튼 | 새 화면 T12 |
| 창(.modal.wide) | 열림 | 뒤 화면 흐림, 흰 창 720px · 모서리 18px, 머리 오른쪽 '닫기' 보조 버튼, 내용이 길면 창 안 스크롤 | 새 화면 T13 · T14 |

## UI surface adaptation

| UI surface ID | Preserved global rule | Surface-specific application | Reason from actor/device/task |
| --- | --- | --- | --- |
| tech | 카드 · 배지 · 칩 · 버튼 토큰, 상태 색 의미 | 1080 × 740 기준, 상단 알람 표시줄 + 진행 단계, 큰 주 버튼(높이 52px · 꽉 찬 폭), 결과 버튼 3개 큰 터치 영역 | 설비 앞 태블릿 · 터치 · 야간 단독 작업 |
| lead | 카드 · 배지 · 칩 · 버튼 토큰, 상태 색 의미 | 1280 × 620 기준, 왼쪽 남색 메뉴 230px, 표 15px · 행 간격 중간, 목록 → 검토 2열 | 사무실 PC · 마우스 · 키보드 · 여러 건 검토 |

## Visual Craft Review

- Review mode: `independent_visual_pass`
- Reviewed render paths: `wireframes/v2/design/direction-guide/T04.html, wireframes/v2/design/direction-guide/T09.html, wireframes/v2/design/direction-guide/L03.html`
- Direction-level repair count (0 or 1): 1
- Outcome: `ready`
- G2A structure changed: `no`

화면을 만든 쪽과 분리된 검토자가 실제 렌더(before PNG, T09 실패 상태 포함)만 보고 다섯 항목을 점검했다. 찾은 문제는 `wireframes/v2/design/direction-guide.css` 한 곳에서 한 번 보정했다(after).

| Check | Result (pass or repaired) | Observed issue / direction-level repair |
| --- | --- | --- |
| Alignment | repaired | T04 안내 둘째 줄이 아이콘 밑에서 시작, 실패 행 배경 여백 4px → 안내 줄 아이콘 · 문장 칸 분리, 보고서 행 안쪽 여백 12px |
| Repeated components | repaired | '자동 검사' 설명이 출처 칩 모양, 유사 % 초록이 통과 의미와 충돌 → 보조 문구 토큰, 유사 % 중립 잉크 |
| Surface and edges | repaired | 메뉴 현재 띠가 모서리 따라 휨, 메모 입력칸이 옵션 카드와 같은 모양 → 독립 띠, 입력칸 표면 · 모서리 구분 |
| Typography and density | repaired | 기록 카드 머리 줄 끊김, 실패 설명 상자가 확인 행에 3px로 붙음 → 머리 한 줄 · 줄임, 상자 위 12px |
| State clarity | repaired | 실패 행이 색으로만 표시, 잠긴 확정 버튼 대비 약 1.5:1 · 잠금 표시 없음 → 왼쪽 띠 + ✕, 잠김 버튼 흐린 바탕 · 🔒. 실패 행 문구('근거 없는 문장 없음' + ✕의 이중 부정)는 CSS로 고칠 수 없는 내용이라 G3에서 결과 문장으로 바꾸도록 넘긴다(CO-20) |

## Structure preservation check

영역 배치, 탐색, 작업 순서, 기능, 권한, AC는 G2A v2 · G1 v3 승인 그대로다. 바꾼 것은 `wireframes/v2/design/direction-guide.css`의 시각 규칙뿐이다.

## Human Gate G2B decision

`decisions/G2B-visual-design.json`에 기록한다(v1 결정은 `decisions/history/G2B-visual-design-v1.json`).
