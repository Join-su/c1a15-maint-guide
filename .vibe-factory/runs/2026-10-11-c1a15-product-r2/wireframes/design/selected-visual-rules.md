# Selected Global Visual Rules: direction-guide

## Source direction

- Selected direction ID: direction-guide
- Source direction brief: wireframes/design/direction-guide.md
- Design Playbook version: references/07-design-playbook.md (Curated 2026-10-01)
- Applied Playbook principle IDs: FL-01, FL-02, CA-02, AT-01, PO-01

시각 구현 원본: `wireframes/structure/_assets/guide-a.css`(가이드 토큰) + `wireframes/design/direction-guide.css`(Craft Review 보정). G3는 이 두 파일과 아래 규칙을 모든 47개 화면에 적용한다.

## Global visual rules

| Visual axis | Global rule | Preserve from G2A |
| --- | --- | --- |
| Typography and density | Noto Sans KR · 화면 제목 26px 900 · 카드 제목 17px 800 · 본문 15px, 태블릿은 큰 터치 버튼과 넉넉한 행 간격, PC는 표 15px 중간 밀도 | Required information and task order |
| Color and state language | 연회색 바탕 + 흰 카드, 파랑 주 행동, 등급 A 초록 · B 파랑 · C 주황 · D 빨강 배지(글자 + 색 + 테두리), 상태는 칩 · 배너 · 아이콘 함께 | Status meaning and visible state |
| Surface and hierarchy | 1px 회색 테두리 흰 카드(그림자 거의 없음), 강조 카드만 2px 파랑 테두리, 카드 안 패널은 테두리 없는 색 바탕, 입력칸은 흰 바탕 + 1.5px 테두리 | Region containment and role |
| Item silhouette and control form | 모서리 14~16px 카드 · 10px 패널 · 옵션, 꽉 찬 큰 주 버튼 하나 + 흰 보조 버튼, 호출 · 경고 주 버튼은 진한 주황 변형 | Item meaning, metadata, and affordance |
| Emphasis and reading order | 상단 알람 표시줄 → 진행 단계 → 왼쪽 판단 정보 → 오른쪽 지금 할 행동(주 버튼) / PC는 왼쪽 메뉴 → 제목 → 내용 → 오른쪽 결정 | Navigation and user task order |

## Component foundation

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

## Structure protection

These rules do not change information units, layout regions, navigation, task order, functionality, authority, or Acceptance Criteria. A needed change returns to G2A.
