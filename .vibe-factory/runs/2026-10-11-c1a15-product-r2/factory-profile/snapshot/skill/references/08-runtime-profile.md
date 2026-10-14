# Runtime Profile and Artifact Governance

## Purpose

Factory Profile은 한 run이 실제로 따른 Skill, template, validator, Critic protocol을 고정한다. 제품 요구·G0~G7 순서·critic 횟수·Human Gate를 바꾸는 산출물이 아니다.

v0.8.10+ 새 run은 시작 시 `factory-profile/profile.json`과 그 snapshot 파일을 만든다. 재개 시 snapshot의 `skill/SKILL.md`와 Critic protocol을 읽고, 검증은 snapshot의 `skill/scripts/validate_artifacts.py`만 실행한다. `critic/vibe-factory-critic.md` adapter가 함께 snapshot되었으면 실행 adapter로 사용할 수 있지만, 검토 범위의 규칙 권위는 항상 Critic protocol이다. 전역·프로젝트 복사본 validator는 profile validator와 hash·경로가 일치하지 않으면 실패한다.

v0.8.9 이하 run은 Profile을 실행 기준으로 삼지 않는 `legacy` run이다. 현재 Skill 규칙을 일부만 덧씌우거나 자동 migration하지 않는다. 기존 runtime이 보존되어 있으면 그 runtime으로만 재개하고, 새 runtime 규칙이 필요하면 새 run을 시작한다.

## Artifact classes

| Class | Examples | Write rule |
| --- | --- | --- |
| `immutable_contract` | Evidence Pack, Use Case, selected structure/design, Prototype, Coding Plan, Verification Matrix | critic이 읽은 version은 수정하지 않는다. 의미 변경은 새 version과 필요한 critic/Human Gate를 만든다. |
| `derived_materialization` | Director Review, explanatory SVG, Gate Brief | immutable contract의 예약된 경로에 생성할 수 있다. contract를 수정하거나 새 제품·구현 결정을 추가하지 않는다. |
| `decision_lifecycle` | Gate Decision, actual authorization, run-state, critic output | 승인·상태·시간을 기록한다. immutable contract의 hash 범위에 넣지 않는다. |

`implementation_authorization_proposal`은 immutable contract의 일부이고, 실제 `implementation_authorization`은 PBC-4 Gate Decision만의 decision_lifecycle record다. 다른 Gate Decision에는 authorization을 기록하지 않는다.

## Critic input bundle

critic을 호출하기 전에 Generator는 `critics/<gate>-<attempt>-input.json`을 만든다. 이 파일은 subject와 비교 source의 `artifact/path/version/sha256`만 담는다. subject는 **그 호출 시점**의 `G0=evidence_pack`, `G1=use_case`, `G3=prototype`, `PBC-4=prebuild_contract`, `G6=verification_report` run-state artifact여야 한다. Critic은 이 bundle과 그 안의 파일만 읽는다. Critic output은 input bundle의 path/hash와 같은 source 목록을 그대로 기록한다. 재검토 history가 있는 G0·G1·G3는 각 review가 당시 subject의 file/hash를 보존하고, 마지막 pass만 현재 artifact와 일치해야 한다.

PBC-4는 approved input lock 및 현재 machine artifact의 실제 path만 source로 쓸 수 있다. `verified` feasibility preflight의 `feasibility_probe`, 또는 `existing_observed_evidence`가 가리키는 current Planning Baseline도 조건부 PBC machine source다. 다른 gate도 선언된 bundle 밖의 source를 추가하지 않는다.

## Upgrade boundary

- 새 Factory 버전은 새 run의 기본 Profile일 뿐, 진행 중 run에 자동 적용되지 않는다.
- v0.8.10+ run은 해당 run의 Profile snapshot으로만 재개한다.
- 진행 중 run의 Profile migration은 지원하지 않는다. contract·검증 의미를 바꿔야 하면 새 run을 시작한다. 이 규칙은 반쯤 이관된 run과 critic hash 충돌을 방지한다.
