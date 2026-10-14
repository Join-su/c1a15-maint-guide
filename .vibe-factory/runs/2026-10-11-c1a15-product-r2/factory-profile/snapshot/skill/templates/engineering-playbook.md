# Engineering Playbook {{version}}

> 이 문서는 Wiki의 기술 지식을 PBC에서 재사용할 수 있는 판단 규칙으로 정리한, Wiki 안의 장기 유지 문서다. 프로젝트 run artifact가 아니며 매 run에 복제하지 않는다.

## Metadata

- Version: `{{version}}`
- Reviewed at: `{{ISO-8601}}`
- Review owner: `{{owner}}`
- Scope: implementation method selection only; it cannot change product behavior, AC, authority, data meaning, or UI promises.

## Source documents

| Source path | Section / anchor | Why it is authoritative | Checked at |
| --- | --- | --- | --- |
| `{{wiki path}}` | `{{heading}}` | `{{reason}}` | `{{ISO-8601}}` |

## Decision rules

Each rule has a stable ID. A Selection Register must cite the exact ID it used, not this document only by name.

### EP-{{CATEGORY}}-001 — {{short decision name}}

- Situation / requirement signals: `{{observable condition that makes this relevant}}`
- Recommended approach: `{{skill, model role, loop, harness, graph, or other method}}`
- Do not use when: `{{non-trigger or cheaper sufficient approach}}`
- Preconditions and authority boundary: `{{what must already be true; what it may not do}}`
- Verification and stop condition: `{{how to prove it and when to stop/escalate}}`
- Revalidate when: `{{environment, dependency, model, risk, or requirement signal changes}}`
- Wiki basis: `{{source path + heading from Source documents}}`

## Currency review

List rules whose tooling/model facts require periodic review. If a PBC needs a missing or stale rule, update and version this Playbook before beginning PBC-1; do not invent the rule inside a Selection Register.
