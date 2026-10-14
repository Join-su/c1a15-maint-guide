# Coding Plan {{version}} — Director Review

## 한눈에 보기

## 사용자 기대와 계획의 대응

| 사용자가 이 단계에서 기대한 것 | 계획 artifact / ID | 확인 방법 |
| --- | --- | --- |

## What remains fixed

## What this plan will and will not do

## Implementation design

Explain component responsibilities, interface/state-data/external-action boundaries, logical-flow mapping, dependencies, slice order, and delivery/recovery. When a logical system contract is applicable, show the first end-to-end flow, runtime mode, state/readback expectation, and fixture/live limitation. Embed the implementation-design and runtime-sequence diagrams when the plan has multiple boundaries.

When the Use Case declares multiple product UI surfaces, show each surface's critical scenario, entry and result/readback boundaries, integrated slice, and verifier. The architecture diagram must show the UI branches converging on shared components where applicable; do not present the surfaces as implementation alternatives.

## Why this engineering approach

Explain selected and rejected approaches in plain language. Link each claim to plan item IDs.

## Engineering, skills, and model roles

Summarize the Selection Register. Show selected and excluded categories, current environment-verified skills, product-model roles, development-model roles, and the requirement signal behind each choice.

## Traceability map

Embed/render the `traceability` diagram using `artifact-dependency-tree`. Its nodes show only role/reference/output; every content edge has the exact plan, AC, verifier, or evidence artifact name. Show critic, Human Gate, manifest, and lineage as distinct control/lineage edges. Explain the legend and the reuse audit.

## Delivery roadmap

Embed/render the `roadmap` diagram and explain its legend.

## Conditional structure, state, and risk diagrams

Add only when the plan actually has those elements.

Use `artifact-dependency-tree` for any additional SVG whose purpose is artifact dependency, approval, or verification explanation. Do not force it onto component topology, product state, or time-only roadmap diagrams.

## Risks, authority boundaries, and stop conditions

State the approved execution mode, batch item IDs, automatic quality gates, critic escalation triggers, and stop conditions. Ordinary slices create no separate human report; the final batch review summarizes their ledger evidence.

## 승인자에게 요청할 결정

## Approval effect

State the plan version and exactly which implementation actions become authorized. List actions requiring a separate approval.
