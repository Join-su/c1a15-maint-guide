# G2B Design Direction direction-guide: 사용 가이드 시각 언어 (v3)

## G2A structural baseline

- Selected structure version: wireframe_structure v3 (G2A 승인 `decisions/G2A-wireframe-structure.json`)
- Selected structure-render baseline path / SHA-256: wireframes/v3/structure/selected-visual-baseline.json / 7d5f21c40c9b12e07162e90d79b1eabd81bb2e69101d67b85bb91cf0f0d95b39
- Structure preserved from this baseline: 모든 Region(v3 구조 계약 199개), 정보 단위, 탐색, 작업 순서, 필수 정보, 상태 의미, 조작 위치
- Non-binding G2A visual treatment replaced here: v2 규칙(자동 검사 상태 아이콘 등) 그대로 + v3(007 · 008): 진행 표시 완료 단계의 누르기 단서, 지난 단계 창의 제출됨 / 수정 가능 칩, B 점검 시작 전 체크리스트 패널 · 잠긴 결과 버튼, 등급 경고 낮춤 / 올림 구분, Craft Review 보정 1회(`wireframes/v3/design/direction-guide.css`)

## Design hypothesis and Playbook inputs

- Visual hypothesis: 승인된 사용 가이드 시각 언어를 그대로 쓰되, 누를 수 있는 것(완료 단계 · 수정 가능 입력)과 고칠 수 없는 것(제출됨 · 잠긴 결과 입력), 위험이 커지는 변경(낮춤)과 작업을 막는 변경(올림)을 모양으로 구분하면 정비자 · 파트장이 헷갈리지 않는다
- Design Playbook version: references/07-design-playbook.md (Curated 2026-10-01)
- Applied Playbook principle IDs: FL-01, FL-02, CA-02, AT-01, PO-01
- Intended work experience: 정비자는 지금 할 행동 하나와 지난 기록 · 잠긴 입력을 바로 구분하고, 파트장은 등급을 바꿀 때 그 영향을 경고 색과 아이콘으로 먼저 본다
- Contrast from the other directions: 다른 방향 없음(D17) — 가이드 시각 언어 v3가 유일한 방향이다

## Visual distinction

- Distinct visual axes (at least 3; comma-separated: typography_density, color_state, surface_hierarchy, item_control_form, emphasis_reading_order): typography_density, color_state, surface_hierarchy, item_control_form, emphasis_reading_order

## Representative screens: before and after

| Page ID / State | Why this screen represents a distinct task or risk | G2A baseline path | This direction's after path |
| --- | --- | --- | --- |
| T15 / check_current | 새 화면: 지난 기록(제출됨)과 이 기기에만 있는 입력(수정 가능)의 구분, 완료 단계 누르기 단서 | wireframes/v3/structure/selected/T15--check_current.html | wireframes/v3/design/direction-guide/T15.html |
| T06 / b_precheck | 새 상태: B 점검 시작 전 체크리스트와 잠긴 결과 입력 | wireframes/v3/structure/selected/T06--b_precheck.html | wireframes/v3/design/direction-guide/T06.html |
| L05 / raise_warning | 새 상태: 등급 올림 경고(낮춤 경고와 다른 의미) | wireframes/v3/structure/selected/L05--raise_warning.html | wireframes/v3/design/direction-guide/L05.html |

## Refinement impact

| Maintained structure | Changed visual expression | Observable benefit | Trade-off |
| --- | --- | --- | --- |
| 진행 표시 5단계 · 순서 | 완료 단계 = 흰 알약 · 1px 초록 테두리 · ›, 현재 단계 글자 800 · 파랑 | 터치 기기에서도 완료 단계를 누를 수 있어 보이고, 현재 단계가 가장 무겁다 | 진행 표시가 조금 넓어짐 |
| 지난 단계 창 기록 행 · 순서 | 제출됨 = 회색 칩 + 단색 자물쇠, 수정 가능 = 흰 칩 · 주황 테두리 + 연필, 옅은 주황 행 · 열 맞춤, 뒤 막 짙게 | 고칠 수 없는 것 / 고칠 수 있는 것이 색 없이도 구분 | 창 뒤 화면이 더 어두움 |
| B 점검 지시 · 결과 입력 | 시작 전 체크리스트 = 테두리 없는 파랑 틴트 패널 · 터치 행 32px · '확인 n / m' 칩, 결과 버튼 = 잠김 토큰(흐린 바탕 · 자물쇠) | 잠긴 이유와 여는 조건이 한눈에 | 지시 카드가 꽉 참(절차 행 여백을 줄임) |
| 등급 변경 경고 자리 | 낮춤 = 주황 ⚠ + 진한 주황 저장, 올림 = 파랑 ⓘ + 일반 주 버튼, 등급 선택 상자 폭 고정 | 두 경고가 다른 의미로 읽히고 표 오른쪽 끝이 맞음 | 경고 종류가 둘이 됨 |

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
| 진행 단계(.sp) | 완료(누를 수 있음) · 현재 · 남음 | 완료 초록 체크 + 흰 알약 · 1px 초록 테두리 · ›(누르면 지난 단계 보기), 현재 파랑 번호 + 링 · 글자 800 파랑, 남음 회색 번호 | None |
| 주 버튼(.btn.lg.full) | 기본 · 잠김(.dis) · 호출/경고(.warnb) | 꽉 찬 폭, 높이 약 52px, --pri 바탕 흰 글자 / 잠김은 #eef0f3 바탕 · 흐린 글자 · 1px 테두리 · 아이콘 대신 🔒 / 경고는 --btn-primary-warn #b45309 | 경고 변형은 C · D 호출 행동에만 |
| 기록 카드(.hc) | 기본 | 1px 테두리, 모서리 12px, 머리 한 줄(번호 mono · 설비 · 월 줄임 · 유사 % 오른쪽 중립 잉크), 초록은 쓰지 않음 | None |
| 보고서 행(.rf) | 기본 · 실패(.fail) | 이름 120px · 값, 첫 줄 정렬, 행 안쪽 여백 12px, 실패는 왼쪽 3px 빨강 띠 + 이름 앞 ✕ + 옅은 빨강 바탕 | None |
| 자동 검사 행(.ckl .ck) | 통과(.on) · 실패(.no) | 상자 없음, 통과 ✓ 초록 · 실패 ✕ 빨강(실패 문구 굵게), 목록 위 보조 문구 '자동 검사 · 모두 통과해야 확정할 수 있습니다', 누를 수 없음 | 사람이 누르는 체크리스트(T08 .act .ck)는 기존 상자 모양 유지 |
| 왼쪽 메뉴(.wn) | 현재 · 나머지 | 남색 바탕, 나머지 흐린 글자 500 / 현재 흰 글자 800 + 밝은 바탕 + 왼쪽 3px 독립 띠(모서리와 분리) | None |
| 안내 줄(.hint) | 기본 | 아이콘 16px 칸 + 문장 칸(줄이 바뀌어도 문장 시작점 정렬) | None |
| 입력칸(.memo.sm3) | 기본 | #f6f8fb 바탕 · #c9d0db 테두리 · 모서리 8px(선택 옵션 카드와 구분) | None |
| 목록 패널(.panel) | 열림 | 종 아이콘 아래 흰 패널, 1px 테두리 · 모서리 16px · 그림자, 묶음 머리 13px 굵게, 항목 행 = 상태 점 · 2줄 요약 · 이동 버튼 | 새 화면 T12 |
| 창(.modal.wide) | 열림 | 뒤 화면 흐림(짙은 막 45% + 2px 흐림), 흰 창 720px · 모서리 18px, 머리 오른쪽 '닫기' 보조 버튼, 창 안 칩도 999px 알약, 내용이 길면 창 안 스크롤 | 새 화면 T13 · T14 · T15 |
| 지난 단계 기록 행(.hist-row) | 제출됨 · 수정 가능(.unsent) | 시각 · 내용 · 오른쪽 칩, 제출됨은 회색 칩 + 단색 자물쇠, 수정 가능은 옅은 주황 행 + 흰 칩 · 주황 테두리 · 연필 + '이 화면에서 고치기', 왼쪽 단계 목록 현재 항목은 독립 3px 파랑 띠 | 새 화면 T15 |
| 시작 전 체크리스트(.act.pre) | 확인 중 · 모두 확인 | 테두리 없는 파랑 틴트 패널 10px, 사람이 누르는 체크 행 32px 이상 · 상자 24px, 오른쪽 위 '확인 n / m' 칩 | B 점검 지시(T06 / b_precheck)에만 |
| 잠긴 결과 버튼(.rbtn.dis) | 잠김 | 잠김 토큰과 같은 모양(#eef0f3 바탕 · 테두리 · 흐린 글자 · 오른쪽 위 단색 자물쇠), 누를 수 없음 | B 점검 확인 전에만 |
| 등급 변경 경고 배너(L05) | 낮춤 · 올림 | 낮춤 = 주황 경고 배너 ⚠ + 진한 주황 '…로 변경 저장', 올림 = 파랑 안내 배너 ⓘ + 일반 주 버튼, 제목 줄 균형 | 모든 등급 변경에 경고(EV-062) |

## UI surface adaptation

| UI surface ID | Preserved global rule | Surface-specific application | Reason from actor/device/task |
| --- | --- | --- | --- |
| tech | 카드 · 배지 · 칩 · 버튼 토큰, 상태 색 의미 | 1080 × 740 기준, 상단 알람 표시줄 + 진행 단계, 큰 주 버튼(높이 52px · 꽉 찬 폭), 결과 버튼 3개 큰 터치 영역 | 설비 앞 태블릿 · 터치 · 야간 단독 작업 |
| lead | 카드 · 배지 · 칩 · 버튼 토큰, 상태 색 의미 | 1280 × 620 기준, 왼쪽 남색 메뉴 230px, 표 15px · 행 간격 중간, 목록 → 검토 2열 | 사무실 PC · 마우스 · 키보드 · 여러 건 검토 |

## Visual Craft Review

- Review mode: `independent_visual_pass`
- Reviewed render paths: `wireframes/v3/design/direction-guide/T15.html, wireframes/v3/design/direction-guide/T06.html, wireframes/v3/design/direction-guide/L05.html`
- Direction-level repair count (0 or 1): 1
- Outcome: `ready`
- G2A structure changed: `no`

화면을 만든 쪽과 분리된 검토자가 실제 렌더(v3 초안 PNG, 비교용 낮춤 경고 포함)만 보고 다섯 항목을 점검했다. 찾은 문제 11건은 모두 시각 층으로 고칠 수 있다는 판단이었고, `wireframes/v3/design/direction-guide.css` 한 곳에서 한 번 보정했다(after). 보정 중 T06이 화면 아래로 넘쳐 같은 보정 안에서 체크 행 · 절차 행 여백을 맞췄다(넘침 0px 확인).

| Check | Result (pass or repaired) | Observed issue / direction-level repair |
| --- | --- | --- |
| Alignment | repaired | T15 '지금' 행이 위 행보다 4px 밀림, L05 등급 선택 상자 폭이 행마다 다름 → 강조 행 바탕을 바깥으로 늘려 열 맞춤, 선택 상자 폭 고정 |
| Repeated components | repaired | 창 안 칩이 사각형 · 컬러 이모지, '수정 가능' 칩이 행 바탕에 묻힘, 단계 목록 띠가 모서리를 따라 휨, 잠긴 결과 버튼과 잠긴 주 버튼 모양이 다름, 체크리스트 패널이 강조 테두리, 올림 · 낮춤 같은 ⚠ → 999px 칩 · 단색 아이콘, 흰 칩 + 주황 테두리 + 연필, 독립 띠, 잠김 토큰 통일, 테두리 없는 색 패널, 올림은 ⓘ |
| Surface and edges | repaired | 창 뒤 막이 옅어 뒤 화면 주 버튼이 시선을 다툼 → 막 45% + 2px 흐림(공통 창 토큰) |
| Typography and density | repaired | '지금' 행 제목 2줄 · 보조 문구 3줄, 체크 행 30px로 좁음, 올림 배너 제목 마지막 글자 줄바꿈 → 칩 · 버튼 세로 쌓기, 체크 행 32px · 상자 24px(한 화면에 들도록 절차 행 여백 축소), 제목 줄 균형 |
| State clarity | repaired | 완료 단계 누르기 단서 없음, 잠긴 결과 버튼이 '아직 안 고름'과 헷갈림, 체크 진행 수 없음, 올림 · 낮춤이 색 없이는 같은 경고 → 흰 알약 · 초록 테두리 · ›, 잠김 토큰 · 자물쇠, '확인 n / m' 칩(CSS가 체크 수를 셈), ⓘ / ⚠ 구분 |

## Structure preservation check

영역 배치, 탐색, 작업 순서, 기능, 권한, AC는 G2A v3 · G1 v5 승인 그대로다. 바꾼 것은 `wireframes/v3/design/direction-guide.css`의 시각 규칙뿐이다.

## Human Gate G2B decision

`decisions/G2B-visual-design.json`에 기록한다(v2 결정은 `decisions/history/G2B-visual-design-v2.json`).
