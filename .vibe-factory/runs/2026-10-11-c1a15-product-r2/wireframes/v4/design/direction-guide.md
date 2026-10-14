# G2B Design Direction direction-guide: 사용 가이드 시각 언어 (v4)

## G2A structural baseline

- Selected structure version: wireframe_structure v4 (G2A 승인 `decisions/G2A-wireframe-structure.json`)
- Selected structure-render baseline path / SHA-256: wireframes/v4/structure/selected-visual-baseline.json / 3be81abf77220c9a1f18566d6877d712f76e15b6708565cfdcd49270d985a3f0
- Structure preserved from this baseline: 모든 Region(v4 구조 계약 252개), 정보 단위, 탐색, 작업 순서, 필수 정보, 상태 의미, 조작 위치
- Non-binding G2A visual treatment replaced here: v3 규칙(승인) 그대로 + v4(010 · 011): 상단 '홈' 버튼, 진행 표시의 보는 단계, 지난 화면 띠, 보기 상태의 보낸 결과 · 메모, 정정 창(원래 값 · 필수 사유 · 입력칸 토큰), 정정 표시(연필 + 정정 n회), '정정으로 무효', 보낸 뒤 정비자 정정 상자, Craft Review 보정 1회(`wireframes/v4/design/direction-guide.css`)

## Design hypothesis and Playbook inputs

- Visual hypothesis: 승인된 사용 가이드 시각 언어를 그대로 쓰되, '지금'(현재 단계 · 파랑)과 '지난 기록을 보는 중'(보는 단계 · 진한 잉크 링 · 지난 화면 띠), 보낸 값(읽기 전용 패널 · '보냄')과 고칠 수 있는 입력(흰 입력칸), 정정의 흔적(연필 · 정정 n회 · 정정으로 무효)을 모양으로 구분하면 정비자가 지난 기록을 지금 입력으로 착각하지 않고, 파트장은 덧붙은 정정을 경고와 구분해 읽는다
- Design Playbook version: references/07-design-playbook.md (Curated 2026-10-01)
- Applied Playbook principle IDs: FL-01, FL-02, CA-02, AT-01, PO-01
- Intended work experience: 정비자는 점검 중에도 '홈'으로 나갔다 돌아오고, 지난 화면에서 보낸 값을 확인해 사유와 함께 정정하며, 파트장은 호출 · 감사 기록에서 정정을 한눈에 본다
- Contrast from the other directions: 다른 방향 없음(D17) — 가이드 시각 언어 v4가 유일한 방향이다

## Visual distinction

- Distinct visual axes (at least 3; comma-separated: typography_density, color_state, surface_hierarchy, item_control_form, emphasis_reading_order): typography_density, color_state, surface_hierarchy, item_control_form, emphasis_reading_order

## Representative screens: before and after

| Page ID / State | Why this screen represents a distinct task or risk | G2A baseline path | This direction's after path |
| --- | --- | --- | --- |
| T15 / correct | 새 상태: 지난 화면 띠 · 보는 단계 위의 정정 창(원래 값 · 정정 값 · 필수 사유 · 잠긴 저장), 상단 '홈' | wireframes/v4/structure/selected/T15--correct.html | wireframes/v4/design/direction-guide/T15.html |
| T08 / corrected_path | 새 상태: 다시 판정 뒤 점검 경로의 정정 표시와 '정정으로 무효' | wireframes/v4/structure/selected/T08--corrected_path.html | wireframes/v4/design/direction-guide/T08.html |
| L04 / call_corrected | 새 상태(파트장 PC): 보낸 호출에 덧붙은 정비자 정정(경고와 다른 의미) | wireframes/v4/structure/selected/L04--call_corrected.html | wireframes/v4/design/direction-guide/L04.html |

## Refinement impact

| Maintained structure | Changed visual expression | Observable benefit | Trade-off |
| --- | --- | --- | --- |
| 진행 표시 5단계 · 순서 | 완료 단계 = 흰 알약 · 1px 초록 테두리 · ›, 현재 단계 글자 800 · 파랑 | 터치 기기에서도 완료 단계를 누를 수 있어 보이고, 현재 단계가 가장 무겁다 | 진행 표시가 조금 넓어짐 |
| 지난 단계 창 기록 행 · 순서 | 제출됨 = 회색 칩 + 단색 자물쇠, 수정 가능 = 흰 칩 · 주황 테두리 + 연필, 옅은 주황 행 · 열 맞춤, 뒤 막 짙게 | 고칠 수 없는 것 / 고칠 수 있는 것이 색 없이도 구분 | 창 뒤 화면이 더 어두움 |
| B 점검 지시 · 결과 입력 | 시작 전 체크리스트 = 테두리 없는 파랑 틴트 패널 · 터치 행 32px · '확인 n / m' 칩, 결과 버튼 = 잠김 토큰(흐린 바탕 · 자물쇠) | 잠긴 이유와 여는 조건이 한눈에 | 지시 카드가 꽉 참(절차 행 여백을 줄임) |
| 등급 변경 경고 자리 | 낮춤 = 주황 ⚠ + 진한 주황 저장, 올림 = 파랑 ⓘ + 일반 주 버튼, 등급 선택 상자 폭 고정 | 두 경고가 다른 의미로 읽히고 표 오른쪽 끝이 맞음 | 경고 종류가 둘이 됨 |
| 상단 바 · 진행 표시 | '홈' = 흰 알약 보조 버튼 44px(홈 화면에서는 파랑 틴트), 보는 단계 = 같은 크기 알약 + 진한 잉크 링 + 단색 눈(현재 단계 파랑과 다른 색) | 점검 중에도 홈이 바로 보이고, 지금 단계와 보는 단계가 헷갈리지 않음 | 상단 바 오른쪽이 조금 넓어짐 |
| 지난 화면 띠 · 보기 상태 | 띠 = 한 단계 진한 패널 + 왼쪽 3px 잉크 띠, 버튼 40px, 끝 기록의 이전 · 다음은 잠김 토큰 / 보낸 결과 = 1px 테두리 + '보냄' 알약, 보낸 메모 = 읽기 전용 패널, '지금 할 절차' 강조 끔 | 지금 입력이 아니라 지난 기록이라는 것이 모양으로 보임 | 화면 본문 높이가 띠만큼 줄어듦 |
| 정정 창 · 정정 표시 | 원래 값 = 읽기 전용 패널 + 자물쇠, 입력칸 하나(흰 바탕 · 1.5px · 8px), 필수는 이름표 뒤 빨강 '필수' 알약(빨강 테두리는 저장 시도 뒤 비었을 때만) · 포커스 2px 파랑 링, 정정 n회 = 연필 + 회색 알약, '정정으로 무효' = 취소선 + --sub 글자 + 속 빈 회색 점 | 고칠 칸과 고치지 않는 값이 구분되고, 처음부터 오류처럼 보이지 않음 | 창 안 요소가 하나 늘어남(원래 값 패널) |
| 보낸 뒤 정비자 정정 상자(L04) | 중립 연회색 패널 + 왼쪽 3px 주황 띠 + 연필, 본문 15px, 사유 --sub | 경고(주황 바탕)가 아니라 덧붙은 정보로 읽힘 | 주황은 띠에만 남음 |

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
| 상단 '홈'(.tb-home) | 기본 · 현재 위치(.on) | 흰 알약 보조 버튼, 1px --ln 테두리, 높이 44px 이상, 집 아이콘 + '홈' 15px 800 / 현재 위치는 --pri-s 바탕 · --pri 테두리 | 정비자 앱 모든 화면(010) |
| 보는 단계(.sp.done.pick.view) | 지난 화면을 여는 동안 | 완료 알약과 같은 크기, 1px 잉크 테두리 + 바깥 1px 잉크 링, 흰 바탕, 잉크 글자, › 대신 단색 눈 — 현재 단계(파랑)와 다른 색 | T15에만 |
| 지난 화면 띠(.pastbar) | 기본 | 테두리 없는 #e3e9f2 패널 10px + 왼쪽 3px 잉크 독립 띠, 시계 아이콘 · 굵은 '지난 화면 · 단계' · 보조 글자 시각, 오른쪽 이전 · 다음(보조 버튼 40px, 끝 기록은 잠김 토큰) · 위치 n / m · '현재 단계로'(작은 주 버튼) | T15에만 |
| 보기 상태(.ap-body.past) | 보낸 결과 · 보낸 메모 · 측정값 | 원래 화면 조작 잠김, 보낸 결과 버튼 = 1px 결과 색 테두리 · 틴트 + 오른쪽 위 '보냄' 회색 알약(자물쇠 없음), 고르지 않은 버튼 = 잠김 토큰, 메모 · 측정값 = 읽기 전용 패널(#f3f5f8 · 테두리 없음), 마지막 절차 행의 '지금 할 일' 주황 강조는 중립 | T15에만 |
| 정정 창 입력(.modal .fld2) | 원래 값 · 결과 · 메모 · 사유(필수) | 원래 값 = 읽기 전용 패널 + 단색 자물쇠, 입력칸 = 흰 바탕 · 1.5px --input-border · 8px, 이름표-칸 간격 6px, 필수 = 이름표 뒤 빨강 '필수' 알약, 포커스 2px --pri 링, 빨강 테두리(.err)는 저장 시도 뒤 비었을 때만, '정정 저장'은 사유 전 잠김 토큰 | T15 / correct · correct_confirm |
| 정정 표시(.corr-h .ch · .ch.corr · .corr-list) | 정정 n회 · 이전 값 | 연필 + 회색 알약 '정정 n회'(1px --ln), 이전 값 목록은 왼쪽 3px --ln 띠 · 전 값 취소선 --sub · 새 값 --bad 굵게 · 사유 줄 | 지난 화면 · 점검 경로 · 호출 상자 공통(경로 행 설명의 '정정 n회'도 이 칩으로 감쌈) |
| 정정으로 무효(.tli.void) | 무효 | 취소선 유지, 글자 --sub(대비 4.5:1 이상), 점은 속 빈 회색 링, 오른쪽 회색 '정정으로 무효' 칩 기준선 맞춤 | 점검 경로(T08 · T11)에서 지우지 않고 남김 |
| 보낸 뒤 정비자 정정 상자(.corr-box) | 기본 | 중립 #f3f5f8 패널 10px + 왼쪽 3px 주황 독립 띠, 머리 = 연필 16px + 8px 간격 + 13px --sub 이름표 · 시각, 본문 15px, 사유 14px --sub | 파트장 호출 상세(L04)에만, 경고 아이콘은 쓰지 않음 |

## UI surface adaptation

| UI surface ID | Preserved global rule | Surface-specific application | Reason from actor/device/task |
| --- | --- | --- | --- |
| tech | 카드 · 배지 · 칩 · 버튼 토큰, 상태 색 의미 | 1080 × 740 기준, 상단 알람 표시줄 + 진행 단계, 큰 주 버튼(높이 52px · 꽉 찬 폭), 결과 버튼 3개 큰 터치 영역 | 설비 앞 태블릿 · 터치 · 야간 단독 작업 |
| lead | 카드 · 배지 · 칩 · 버튼 토큰, 상태 색 의미 | 1280 × 620 기준, 왼쪽 남색 메뉴 230px, 표 15px · 행 간격 중간, 목록 → 검토 2열 | 사무실 PC · 마우스 · 키보드 · 여러 건 검토 |

## Visual Craft Review

- Review mode: `independent_visual_pass`
- Reviewed render paths: `wireframes/v4/design/direction-guide/T15.html, wireframes/v4/design/direction-guide/T08.html, wireframes/v4/design/direction-guide/L04.html`(+ 같은 규칙을 적용한 T15 / check 렌더)
- Direction-level repair count (0 or 1): 1
- Outcome: `ready`
- G2A structure changed: `no`

화면을 만든 쪽과 분리된 검토자가 실제 렌더(v4 초안 PNG 4장, 비교용 v3 승인 화면)만 보고 다섯 항목을 점검했다. 찾은 문제 15건은 모두 시각 층으로 고칠 수 있었고, `wireframes/v4/design/direction-guide.css` 한 곳에서 한 번 보정했다(after). 보정 안에서 원래 값 패널 선택자가 맞지 않은 것을 같은 보정으로 바로잡았다. 끝 기록의 '이전 · 다음' 잠김과 경로 행 '정정 n회' 칩은 규칙으로 정했고 G3가 위치 · 글자에 맞춰 붙인다(내용 · 구조 그대로).

| Check | Result (pass or repaired) | Observed issue / direction-level repair |
| --- | --- | --- |
| Alignment | repaired | 보는 단계 알약만 2px 커짐, 정정 창 이름표-칸 간격 불균일, 정정 상자 아이콘 붙음 · 시작점 어긋남, 카드 머리 A 배지 처짐 → 같은 크기 알약 + 바깥 링, 간격 6px 고정, 안내 줄 규칙 · 여백 통일, 배지 가운데 정렬 |
| Repeated components | repaired | 입력칸 모양이 화면마다 다름, 정정 표시가 화면마다 다름(연필 유무) · '정정 n회'가 칩이 아님 → 정비자 입력칸 토큰 하나, 정정 표시 하나(연필 + 회색 알약) |
| Surface and edges | repaired | 지난 화면 띠가 바탕과 비슷해 모드가 약함, 보낸 메모가 입력칸 표면, 원래 값에 표면 없음 → 진한 패널 + 왼쪽 잉크 띠, 보낸 값 · 원래 값은 읽기 전용 패널 |
| Typography and density | repaired | '홈' · 띠 버튼 32~36px로 낮음, 정정 상자 글자 작음 · 사유 대비 낮음, '정정으로 무효' 대비 낮음 → '홈' 44px · 띠 버튼 40px · 15px, 상자 본문 15px · 사유 --sub, 무효 글자 --sub · 속 빈 점 |
| State clarity | repaired | 보는 단계와 현재 단계가 같은 파랑, 필수 칸이 처음부터 빨강(오류처럼), 보낸 결과가 지금 고른 것처럼 보임, 끝 기록 '다음'이 활성처럼 보임, 정정된 행 구분 없음, 지난 화면에 '지금 할 절차' 강조 남음, 정정 상자 주황 바탕이 경고처럼 읽힘 → 잉크 링 + 눈, '필수' 알약 · 포커스 링 · 저장 시도 뒤 빨강, 1px + '보냄', 끝 기록 잠김 토큰, 정정 칩, 강조 중립, 중립 패널 + 주황 띠 |

## Structure preservation check

영역 배치, 탐색, 작업 순서, 기능, 권한, AC는 G2A v4 · G1 v6 승인 그대로다. 바꾼 것은 `wireframes/v4/design/direction-guide.css`의 시각 규칙뿐이다.

## Human Gate G2B decision

`decisions/G2B-visual-design.json`에 기록한다(v3 결정은 `decisions/history/G2B-visual-design-v3.json`).
