# Gate Brief: G3 / prototype v5

## 쉬운 설명

승인된 화면 47개와 파생 상태 4개를 한 문서(`prototype/v5/index.html`)에 담았다. 두 앱을 나란히 놓고 실제로 눌러 볼 수 있다.
- 정비자가 호출하면 파트장 목록에 올라가고, 파트장이 답하면 정비자 화면이 바뀐다.
- 파트장이 반려하면 정비자 홈에 사유가 보이고, 정비자가 보고서를 고쳐 다시 확정할 수 있다.
- 값은 data/ 에서 계산한 sample이다. 서버 · DB · LLM은 없다.

수용 기준 36개는 다음과 같이 판정했다.

| 구분 | 수 | 판정 방법 |
| --- | --- | --- |
| 화면에서 판정 | 13개 | 클릭으로 도는 자동 자체 시험으로 판정했다 |
| 서버 · 계산 · 데이터 동작 | 23개 | 구현 단계로 미룬다. 이 중 화면에서 판정할 수 있는 조건 11개는 시제품에서 따로 확인했다 |

## 이번에 결정할 것

| Decision | Proposed value or options | Why it matters | Evidence / artifact link |
| --- | --- | --- | --- |
| Prototype v5 승인 | 승인 / 수정 요청 | 승인한 Prototype Bundle과 Use Case Bundle만 PBC 입력이 된다 | `prototype/v5/index.html`, `prototype/v5/prototype-slice.md` |
| 미룬 AC · 조건 | AC-01: AC-01-C1, AC-01-C2, AC-01-C3; AC-02: AC-02-C3, AC-02-C1; AC-03: AC-03-C1, AC-03-C2, AC-03-C3; AC-04: AC-04-C1, AC-04-C2; AC-05: AC-05-C1, AC-05-C2; AC-06: AC-06-C1, AC-06-C2; AC-09: AC-09-C1, AC-09-C2; AC-10: AC-10-C1; AC-13: AC-13-C1; AC-14: AC-14-C1; AC-15: AC-15-C1, AC-15-C2, AC-15-C3; AC-16: AC-16-C1, AC-16-C2; AC-17: AC-17-C1, AC-17-C2; AC-18: AC-18-C1, AC-18-C2; AC-19: AC-19-C2, AC-19-C1; AC-20: AC-20-C1; AC-23: AC-23-C4, AC-23-C2, AC-23-C1; AC-25: AC-25-C1, AC-25-C2; AC-26: AC-26-C1, AC-26-C2; AC-28: AC-28-C1, AC-28-C2, AC-28-C3; AC-34: AC-34-C1, AC-34-C2, AC-34-C3; AC-35: AC-35-C1; AC-36: AC-36-C1, AC-36-C2 | G3 excluded_scope에 기록하고, PBC에서 서버 · 단위 · 통합 시험으로 연결해야 한다 | `prototype/v5/prototype-coverage.json` deferred_condition_ids · partial_conditions |
| 파생 상태 4개 | T09 / low_evidence, T09 / monitor_report, T06 / second_check, L04 / call_detail_d | 승인 화면 구조를 지킨 채 상태 표현만 더했다 | `prototype/v5/prototype-slice.md` |

## 전체 흐름 그림

- Prototype: `prototype/v5/index.html`
  - 위 막대의 버튼은 시험 장치이며 제품 UI가 아니다: 처음부터 · LLM 실패 시뮬레이션 · 근거 적음 세션 · D등급 호출 예시.
  - `?selftest=1`을 붙이면 자동 시험이 돈다.
- 시작 화면 캡처: `verification/g3-v5/prototype-start.png`

## 상태·규칙·위험 그림

- **자동 검증한 AC(13개):** AC-07, AC-08, AC-11, AC-12, AC-21, AC-22, AC-24, AC-27, AC-29, AC-30, AC-31, AC-32, AC-33. 결과는 `verification/g3-v5/selftest-result.json`
- **음성 시험(v5에서 다시 실행):**
  - MUT-1: 결함 4종 → AC-07 · 08 · 21 · 24 · 32 실패
  - MUT-2: 로그인이 비밀번호 칸을 읽는 결함 → AC-12 실패
- **구조 보존:** Region 158개가 모두 있다. 승인 화면과 마크업 hash를 비교하면 47개 중 43개가 같고, 로그인 4개는 입력칸만 다르다.
- **Critic 이력:**
  - 회차 1: v1 revise → v2 revise(확인). 규칙에 따라 멈췄다.
  - 회차 2(사용자 결정 DEV-01): v3 revise → v4 pass(확인).
  - 사용자 검토에서 로그인 불가 결함 발견(DEV-03).
  - 회차 3: v5 pass.
- **시연 계정:** 정비자 tech.kim · 파트장 lead.park. 비밀번호는 확인하지 않는다. 회원가입은 D9에 따라 없다.
- **prototype 한계:** 상태가 바뀌면 두 앱이 다시 그려진다. 그래서 다른 앱을 누르면 입력 중이던 ID 칸이 기본값으로 돌아간다.

## 하지 않는 것

- 실제 서버 · DB · LLM
- 순위 계산 로직 구현
- 코드 저장소 변경
- push
- OpenAI 호출

## Human decision

Approve / revise / reject와 reviewer note를 Gate Decision JSON(`decisions/G3-prototype.json`)에 기록한다. 미룬 AC는 excluded_scope에 모두 적는다.
