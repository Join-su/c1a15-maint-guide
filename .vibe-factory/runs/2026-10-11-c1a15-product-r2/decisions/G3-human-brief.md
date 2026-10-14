# Gate Brief: G3 / prototype v9

## 쉬운 설명

승인된 화면 51개와 파생 상태 4개를 한 문서(`prototype/v9/index.html`)에 담았다. 두 앱을 나란히 놓고 실제로 눌러 볼 수 있다.
- v5 검토에서 찾아 주신 동작하지 않는 요소 7건을 고쳤다: 홈 '보기' · 과거 기록 기준 문구와 기록 열기 · 결과 버튼 선택 표시 · 체크 칸 · '홈으로' · 종 아이콘 목록 · 등급 변경.
- 새 화면 3개를 연결했다: 종 아이콘 '알람 · 할 일' 패널(T12), 과거 기록 전체 창(T13), 매뉴얼 원문 창(T14).
- 샘플이 없는 흐름(M-03 밖의 설비 · 보고서, 승인 후 진행 뒤 4.4 이후 등)은 'prototype은 M-03 한 건만 제공' 안내만 띄운다.
- 값은 data/ 에서 계산한 sample이다. 서버 · DB · LLM은 없다.

수용 기준 40개는 다음과 같이 판정했다.

| 구분 | 수 | 판정 방법 |
| --- | --- | --- |
| 화면에서 판정 | 17개 | 클릭으로 도는 자동 자체 시험으로 판정했다(새 AC-37 · 38 · 39 · 40 포함) |
| 서버 · 계산 · 데이터 동작 | 23개 | 구현 단계로 미룬다. 이 중 화면에서 판정할 수 있는 조건 12개는 시제품에서 따로 확인했다 |

## 이번에 결정할 것

| Decision | Proposed value or options | Why it matters | Evidence / artifact link |
| --- | --- | --- | --- |
| Prototype v9 승인 | 승인 / 수정 요청 | 승인한 Prototype Bundle과 Use Case Bundle만 PBC 입력이 된다 | `prototype/v9/index.html`, `prototype/v9/prototype-slice.md` |
| 미룬 AC · 조건 | AC-01: AC-01-C1, AC-01-C2, AC-01-C3; AC-02: AC-02-C3, AC-02-C1; AC-03: AC-03-C1, AC-03-C2, AC-03-C3; AC-04: AC-04-C1, AC-04-C2; AC-05: AC-05-C1, AC-05-C2; AC-06: AC-06-C1, AC-06-C2; AC-09: AC-09-C1, AC-09-C2; AC-10: AC-10-C1; AC-13: AC-13-C1; AC-14: AC-14-C1; AC-15: AC-15-C1, AC-15-C2, AC-15-C3; AC-16: AC-16-C1, AC-16-C2; AC-17: AC-17-C1, AC-17-C2; AC-18: AC-18-C1, AC-18-C2; AC-19: AC-19-C2, AC-19-C1; AC-20: AC-20-C1; AC-23: AC-23-C4, AC-23-C2, AC-23-C1; AC-25: AC-25-C1, AC-25-C2; AC-26: AC-26-C1, AC-26-C2; AC-28: AC-28-C1, AC-28-C2, AC-28-C3; AC-34: AC-34-C1, AC-34-C2, AC-34-C3; AC-35: AC-35-C1; AC-36: AC-36-C1, AC-36-C2 | 승인하면 G3 excluded_scope로 넘어가 PBC에서 서버 · 단위 · 통합 시험으로 연결한다 | `prototype/v9/prototype-coverage.json` |
| 파생 상태 4개 | T09 / low_evidence, T09 / monitor_report, T06 / second_check, L04 / call_detail_d | 승인 화면 구조를 지킨 채 상태 표현만 더했다 | `prototype/v9/prototype-slice.md` |
| Critic 비차단 의견 | 기록 정리 3건(CO-22) | 승인하면 PBC 이월 메모로 남는다 | `critics/G3-9-review.json` |

## 전체 흐름 그림

- Prototype: `prototype/v9/index.html` (시연 계정 정비자 tech.kim · 파트장 lead.park, 비밀번호는 확인하지 않음, 회원가입은 D9에 따라 없음)
  - 위 막대의 버튼은 시험 장치이며 제품 UI가 아니다: 처음부터 · LLM 실패 시뮬레이션 · 근거 적음 세션 · D등급 호출 예시.
  - `?selftest=1`을 붙이면 자동 시험이 돈다.
- 화면 캡처: `verification/g3-v9/screens/`

## 상태·규칙·위험 그림

- **자동 자체 시험:** 수용 기준 17개 · 미룬 기준의 화면 조건 6개 AC · 조작 시험 CTL 14개, 모두 통과(`verification/g3-v9/selftest-result.json`).
- **조작 요소 전수 점검(넘기기 전 조건):** 99개 시나리오 × 2053개 요소를 하나씩 실제로 눌러 결과를 대조했다. 이름표와 다른 결과 0 · 다시 그린 뒤 보이는 상태와 내부 상태 불일치 0 · 연결 없음 0 · 오류 0. 샘플 없음 안내 116건은 따로 셌다. 결함 복사본 5개에서는 점검이 결함을 잡았다(`verification/g3-v9/control-audit.json`).
- **음성 시험:** 결함을 하나씩만 넣은 복사본 23개 모두에서 그 결함을 맡은 시험이 실패했다(`verification/g3-v9/mutation-check.json`).
- **구조 보존:** Region 172개가 모두 있다. 승인 화면과 마크업 hash가 51개 중 46개 같다. 다른 5개는 로그인 입력칸 4개와 T09 / check_failed 실패 문구(CO-20)다.
- **Critic 이력:**
  - 회차 1 · 2 · 3: v1~v5(G3-1~G3-5). v5 pass 뒤 사용자 검토에서 동작하지 않는 요소 발견 → 사용자 결정 004로 G0 v2부터 다시(DEV-04).
  - 회차 4: v6 revise → v7 revise(확인). 규칙에 따라 멈췄다.
  - 회차 5(사용자 결정 005, DEV-05): v8 pass(`critics/G3-8-review.json`). Human Gate에서 비차단 3건 수정 요청(006, DEV-06).
  - 회차 6: v9 pass(`critics/G3-9-review.json`).
- **v8에서 고친 것(사용자 결정 006):** 경로별 인계 화면의 '이상' · '확인 불가' 단계를 빨간 점으로, '4.3 확인 불가 → 4.5 이상 → 보충 → 여전히 밖' 경로의 인계 요약 · 점검 경로를 그 경로 값으로, slice 중복 문장 정리.
- **회차 6:** v9 pass(`critics/G3-9-review.json`). 남은 비차단 3건은 기록 정리 수준이다: CTL-15의 한 경로에서 파트장 행 제목을 모으기만 하고 확인하지 않음(같은 값이 다른 경로에서 확인됨), coverage의 상호작용 축 목록에 같은 항목 중복 1건, 증거 파일의 생성기 이름 표기. 승인하면 PBC 이월 메모(CO-22)로 남긴다.
- **prototype 한계:** 상태가 바뀌면 두 앱이 다시 그려진다. 같은 화면에서 넣은 결과 · 메모 · 체크 · 고친 글은 되살리지만, 다른 앱 쪽 입력 위치(커서)는 유지되지 않는다. 승인 대기 빈 목록은 M-01 · M-20을 클릭으로 처리할 수 없어 사용자 경로로는 보이지 않는다(자체 시험이 데이터 상태로 확인).

## 하지 않는 것

- 실제 서버 · DB · LLM
- 순위 계산 로직 구현
- 코드 저장소 변경(git 상태: 바뀐 것은 실행 기록 폴더 `.vibe-factory/runs/`뿐)
- push
- OpenAI 호출

## Human decision

Approve / revise / reject와 reviewer note를 Gate Decision JSON(`decisions/G3-prototype.json`)에 기록한다. 미룬 AC는 excluded_scope에 모두 적는다.
