# Wiki Context Contract

## Purpose

현재 작업의 세부 요구만이 아니라, 사용자가 왜 이 작업을 하며 무엇을 성공으로 보는지까지 재현 가능하게 Context Packet으로 컴파일한다. 기본 Intent Context는 현재 프로젝트의 목적·계획·결정과 사용자의 장기 목표·진로·캡스톤 전략이다.

## Rules

1. Wiki index·현재 프로젝트 문서·활성 계획·결정 기록을 먼저 탐색하고, 장기 의도를 설명하는 personal/capstone/strategy 문서도 후보로 찾는다.
2. Intent Context 후보는 다음 관점으로 선택한다: 프로젝트 목적, 사용자 성공 기준, 장기 목표, 현재 우선순위, 기존 결정·기각안, 관련 도메인 전략·제약.
3. 선택한 Intent Context 문서는 요약이나 일부 heading만 옮기지 않는다. 민감정보를 제외·redaction해야 하는 경우 외에는 전문을 `sources/intent/`의 run-local snapshot과 Context Packet의 `Full Intent Context`에 모두 넣고, source manifest에 `content_mode: full_document`, `snapshot_path`, `content_sha256`을 기록한다.
4. source마다 path, 사용 이유, revision/date, trust boundary, context role(`intent` 또는 `task_evidence`)을 기록한다.
5. raw는 원문 근거, Wiki는 합성·탐색 근거로 구분한다. Wiki 요약이 불명확하거나 충돌하면 raw 또는 지정 원문을 다시 확인한다.
6. `fact`, `decision`, `constraint`, `assumption`, `open_question`, `rejected_option`을 섞지 않는다. 오래되었거나 다른 프로젝트의 자료는 자동으로 현재 요구사항이 되지 않으며, 선택·제외 사유를 명시한다.
7. credential, PII, 불필요한 raw는 Context Packet에서 제외한다.
8. 핵심 의도 또는 성공 기준을 뒷받침할 문서가 부족하면 채워진 척 진행하지 않는다. source 재확인 또는 사람 질문으로 escalation한다.

## Completion

Context Packet에 scope, Intent Context selection rationale, 전문 Intent source, Task Evidence, source manifest, facts, decisions, constraints, assumptions, open questions, excluded sources가 존재한다. Intent source를 선택했는데 run-local snapshot·SHA-256·Packet 안의 같은 전문이 없거나 `content_mode`가 `full_document`가 아니면 G0는 완료되지 않는다.
