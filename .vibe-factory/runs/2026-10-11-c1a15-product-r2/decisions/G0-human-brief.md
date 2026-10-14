# Gate Brief: G0 / evidence_pack v1

## 쉬운 설명

정비 길잡이를 만들기 전에, 무엇을 근거로 만들지를 한 묶음으로 정리했다.
- **의도 문서(3개):** 아이디어, 구현 명세, 과제 원문. 사용자 지시에 따라 Wiki 대신 구현 명세를 썼다.
- **사실 확인용 자료:** 사용 가이드, 데이터, 평가 카드 설명, 아키텍처 그림.
- **Critic 결과:** 독립 Critic이 1회에 통과(`pass`)시켰다.

화면은 가이드를 따르고 앱 2개는 따로 만들며 기술 구조도 이미 정해져 있다. 이 전제들이 이후 설계 폭을 크게 좁히므로 Skill 규칙(G0 8번)에 따라 사람 확인을 받는다.

이 run은 VCF v0.8.21로 새로 만들었다. 이전 run(`2026-10-11-c1a15-product`, v0.8.20)은 validator의 critic 이력 결함 때문에 G0에서 멈췄다. 그 run의 기록은 이 run의 근거로 쓰지 않는다.

## 이번에 결정할 것

| Decision | Proposed value or options | Why it matters | Evidence / artifact link |
| --- | --- | --- | --- |
| 핵심 전제 확인 | 화면·흐름은 가이드 그대로이고 값은 실제 데이터다(D1). 앱 2개는 별도 제품이다(D3). G2A·G2B는 가이드 화면을 유일한 안으로 한다(D17). 기술 구조는 고정이다(D2·D15, PBC에서 적용) | 이후 Gate에서 다른 구조 후보를 만들지 않는다 | `evidence-pack-v1.md` EV-010~012, EV-032 |
| 평가 카드 작성자 상충(Q-04) | 지금 있는 AI 작성 카드 30건을 그대로 쓰고 발표 때 한계를 밝힌다 / 팀원(사람)이 다시 쓴다 | 평가 결과를 어떻게 해석할지가 정해진다. 제품 구현 범위는 바뀌지 않는다 | EV-037, Q-04 |
| fixture 임베딩(EV-048) | PBC에서 정한다. 선택지: 승인을 받아 live 1회로 녹화 / 키 없이 만드는 대체 방식 | AC-16(키 없이 시연)을 어떻게 충족할지가 정해진다 | EV-048 |

## 전체 흐름 그림

이번 Gate의 산출물 관계는 단순해서 설명용 그림을 만들지 않는다.

의도 문서 3개 + 사실 확인 자료 6개 → Context Packet v1 → Evidence Pack v1 → Critic `pass`

## 상태·규칙·위험 그림

- **Critic 1회차:** `pass`. 비차단 의견 3개는 `run-state.json`의 carryover_notes(CO-06~08)에 남겼다.
  - D16의 "v0.8.20"은 이 run에서 v0.8.21로 대체됨
  - 맞지 않는 소견의 옛 흐름을 아이디어 문서 대체 목록에 추가
  - OpenAI 키를 받는 시점은 PBC에서 정함
- **validator(v0.8.21):** G0 현재 상태 PASS. 복사본에서 G1 진입 조건도 PASS.

## 하지 않는 것

- Wiki 읽기·쓰기
- 원인 비율표·평가 카드 정답 열람
- 코드·데이터 변경
- push
- OpenAI 호출

## Human decision

Approve / revise / reject와 reviewer note를 Gate Decision JSON에 기록한다.
