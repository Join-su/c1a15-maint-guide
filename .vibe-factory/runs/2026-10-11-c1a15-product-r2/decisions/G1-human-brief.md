# Gate Brief: G1 / use_case v2

## 쉬운 설명

정비 길잡이가 해야 할 일을 사용자 행동 단위로 정리했다.

- **정비자 앱(태블릿):** 경보 받기 → 진단 보기 → 잠금 → 지시된 점검 하나씩 결과 입력 → 원인 확정·조치·재가동 → 보고서 확정. 혼자 하면 안 되는 작업이 나오면 파트장을 부르고, 원인이 안 나오면 숙련자에게 넘긴다.
- **파트장 앱(PC):** 보고서 승인 · 고쳐서 승인 · 반려, 호출에 답하기, 등급 설정, 감사 기록 보기.

두 앱은 서로 직접 연결되지 않고, 가운데 "진단 처리"를 거쳐서만 정보를 주고받는다.

규모:
- scenario 35개(정비자 21, 파트장 10, 화면 없는 처리 4)
- 수용 기준 36개
- 논리 흐름 12개

Critic 이력:
- 1회차 `revise`: 2건 지적
- 고친 v2를 확인 검토 → `pass`

## 이번에 결정할 것

| Decision | Proposed value or options | Why it matters | Evidence / artifact link |
| --- | --- | --- | --- |
| Use Case v2 승인 | 승인 / 수정 요청 / 반려 | 승인해야 G2A(화면 구조)로 간다 | `use-case/v2/use-case-packet.md` |
| 만료(timeout) 유형 | 해당 없음. 근거 자료에 시간 제한·만료 규칙이 없다 | 새 만료 규칙을 만들면 근거 없는 요구가 된다 | `scenario-coverage.json` coverage.timeout_expiry |
| 시연 알람 발생 방식 | "명령(또는 시연용 버튼)"으로 둔다. 버튼을 둘지, 둔다면 어느 화면에 둘지는 G2A에서 정한다 | 가이드에 없는 화면이 생길 수 있다 | SC-50, FLOW-01, CO-09 |
| 수용 기준 AC-19~AC-36 | 명세 AC-01~18에 더해, Evidence Pack의 시나리오 약속을 관찰 조건으로 옮겼다 | 이후 구현 검증의 기준이 된다 | `acceptance-criteria.json` |

## 전체 흐름 그림

- Use Case 그림: `use-case/v2/use-case-map.svg`
- 논리 시스템 개요: `use-case/v2/logical-system-overview.svg`
- 대표 흐름(M-07 정상 + 호출 + 승인 → 이력): `use-case/v2/logical-scenario-flow.svg`

## 상태·규칙·위험 그림

- **1회차 지적과 수정:**
  - ISS-001: 제가 버튼 화면을 빼기로 정한 것은 근거 밖이었다 → 근거 표현으로 되돌림
  - ISS-002: "지시된 점검 건너뛰기 금지"가 빠져 있었다 → 권한 경계와 AC-35에 넣음
- **확인 검토의 비차단 의견 3개:** `run-state.json` carryover_notes에 기록함
  - CO-09(G2A): 버튼을 두기로 하면 맞출 곳 3군데
  - CO-10(PBC): AC-14 "활성 세션은 한 번에 하나", AC-18 "비교 설정" 관찰 조건
  - CO-11(PBC): 실패 시 기본 처리 2개의 출처 표시
- validator(v0.8.21): G1 상태 통과. v1 → v2 이력이 보존되어 있다.

## 하지 않는 것

- 화면 설계: G2A·G2B에서 한다
- 기술 구조 선택: PBC에서 한다
- 코드 작성
- push
- OpenAI 호출

## Human decision

Approve / revise / reject와 reviewer note를 Gate Decision JSON(`decisions/G1-use-case.json`)에 기록한다.
