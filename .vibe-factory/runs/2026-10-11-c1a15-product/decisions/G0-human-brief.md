# Gate Brief: G0 / evidence_pack v2

## 쉬운 설명

정비 길잡이를 만들기 전에, 무엇을 근거로 만들지를 한 묶음으로 정리했다. 의도 문서는 아이디어, 구현 명세, 과제 원문 세 개다. 사용자 지시에 따라 Wiki 대신 구현 명세를 썼다. 사용 가이드·데이터·평가 카드 설명·아키텍처 그림은 사실 확인용으로만 썼다. 독립 Critic은 1회차에 수정 2건을 요구했고, 고친 뒤 2회차에 통과했다.

화면은 가이드를 따르고 앱 2개는 따로 만든다. 기술 구조도 이미 정해져 있다. 이 전제들이 이후 설계 폭을 크게 좁히므로 Skill 규칙(G0 8번)에 따라 사람 확인을 받는다.

## 이번에 결정할 것

| Decision | Proposed value or options | Why it matters | Evidence / artifact link |
| --- | --- | --- | --- |
| 핵심 전제 확인 | 화면·흐름은 가이드 그대로이고 값은 실제 데이터(D1). 앱 2개는 별도 제품(D3). G2A·G2B는 가이드를 유일한 안으로(D17). 기술 구조 고정(D2·D15, PBC에서 적용) | 이후 Gate에서 다른 구조 후보를 만들지 않는다 | `evidence-pack.md` EV-010~012, EV-032 |
| 평가 카드 작성자 상충(Q-04) | 지금 있는 AI 작성 카드 30건을 그대로 쓰고 발표 때 한계를 밝힘 / 팀원(사람)이 다시 씀 | 평가 결과를 어떻게 해석할지 정한다. 제품 구현 범위는 바뀌지 않는다 | EV-037, Open questions Q-04 |
| fixture 임베딩(EV-048) | PBC에서 결정: 승인을 받아 live 1회로 녹화 / 키 없이 만드는 대체 방식 | AC-16(키 없이 시연)을 어떻게 충족할지 정한다 | EV-048 |
| validator 결함(RT-01) | 아래 "상태·규칙·위험" 참고 | 이대로는 G1로 넘어갈 때 validator가 반드시 실패한다 | `run-state.json` known_runtime_issues |

## 전체 흐름 그림

이번 Gate에서는 설명용 의존 관계 그림을 만들지 않는다. 산출물 관계가 단순하다: 의도 3개 + 사실 확인 자료 6개 → Context Packet v1 → Evidence Pack v1(Critic revise) → v2(Critic pass).

## 상태·규칙·위험 그림

- Critic 이력:
  - 1회차 `revise`
    - ISS-001: 평가 카드 작성자가 문서마다 다름(팀원 vs 격리 AI)
    - ISS-002: 비밀 원문 제약이 빠짐
  - 2회차 `pass` — 비차단 의견 3개는 `run-state.json` carryover_notes에 남김
- **RT-01 validator 결함**
  - G0 규칙은 Critic을 최대 3회(revise → 수정 → 재검토)까지 허용한다.
  - 그런데 pinned validator는 G1 이상에서 기록된 모든 G0 review가 **현재** Evidence Pack을 대상으로 했는지 검사한다.
  - 따라서 1회차 review는 v1 기준이라 반드시 실패한다.
  - 복제 run에서 시험한 결과: `FAIL: G0 critic input subject hash does not match`.
  - VCF 원본 validator도 같은 파일(sha256 f0562e7a…)이다.
  - Profile 고정 run이므로 snapshot을 고치면 Profile hash가 깨진다.

## 하지 않는 것

- Wiki 읽기·쓰기
- 원인 비율표·평가 카드 정답 열람
- 코드·데이터 변경
- push
- OpenAI 호출

## Human decision

Approve / revise / reject와 reviewer note를 Gate Decision JSON에 기록한다.
