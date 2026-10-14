# Pre-build Contract: {{version}}

> This contract compiles approved product artifacts into an implementation plan. It cannot add or reinterpret product behavior.

## Feature identity

- Feature ID:
- Plan mode: `compact | standard | high_risk`

## Approved product input lock

Link `approved-inputs/approved-artifact-manifest.json`. List only the approved Use Case Bundle and Prototype Bundle versions, hashes, paths, and Gate Decisions. The Use Case manifest enumerates `use_case_packet`, `use_case_map`, `scenario_coverage`, `acceptance_criteria`, `logical_system_contract`; the Prototype manifest enumerates `prototype_slice`, `prototype_renderable`, `prototype_coverage`, `variation_evidence`, `execution_evidence`. State product promises that this plan must preserve.

## Planning baseline and revalidation

Link `discovery/planning-baseline.json`. Record repository/environment facts, dependency revision, currentness check dates, and when PBC must be re-reviewed before implementation.

## Scope

### In scope

### Out of scope

### Product changes that this Contract must not make

## Approved flow and Acceptance Criteria

Link the approved Use Case Bundle, Prototype Bundle, and the AC→plan item→verifier traceability matrix. Do not reopen Evidence Pack, G2A, or G2B as PBC product inputs.

## Engineering selection summary

Link the Coding Plan and Selection Register. Explain selected and rejected approaches, including any provisional decision and its resolution condition.

## PBC critic record

PBC-4 uses exactly one independent critic invocation for this approval attempt.

- Approval attempt ID:
- Parent approval attempt ID, if this is a human-requested revision:
- Critic comparison references (artifact / path / version / hash):

If it returns `revise` or `ask-user`, record the issues and stop for a human decision; do not silently revise and request another PBC critic. A human-requested plan revision creates a new plan version and approval attempt, which may receive one new critic invocation.

## Authority, risk, and external-action boundary

State what the implementation may do, what it must never do, and which actions require separate approval.

## Required implementation and verification evidence

Link `verification/verification-matrix.json`, fixture/live boundary, and manual review requirements.

When the logical system contract is applicable, identify the first end-to-end flow and its entry, boundary path, result, readback expectation, L3 evidence, and any explicitly excluded live action. L4 remains the AC-to-evidence trace, not an extra test requirement.

## Feasibility preflight and safe adversarial verification

Link the Coding Plan's `feasibility_preflight`. It is `not_required` only as `single_control` or with a current observed-evidence pointer; otherwise it locks a passing `feasibility-probe.json` included in the PBC critic input bundle. For high-risk verification, list each safe fault-injection target, containment, prohibited real action, fail-closed assertion, cleanup, and completion plan item. This Contract never authorizes an external or live action merely to inject a failure.

## Pre-critic consistency check

Link `prebuild/.../pbc-consistency-check.json`. It records current artifact hashes and the results for selected/excluded, plan/verification, change-representation, and feasibility-preflight consistency. It is a PBC machine-artifact check, not a product-contract review.

## Plan amendment and learning policy

L0/L1/out-of-scope-contract-change classification, approved amendment location, and Learning Record policy.

## Implementation authorization proposal

```json
{
  "allowed_plan_version": "v1",
  "allowed_plan_item_ids": [],
  "execution_mode": "continuous_batch | per_slice_gated",
  "stop_conditions": [],
  "prohibited_actions": [],
  "separate_approval_required_for": [],
  "approver_role": ""
}
```

This is a critic-reviewed proposal, not an authorization. The Human Gate Decision records the actual `implementation_authorization`, including `authorized`, `approved_by`, and `approved_at`. An actual authorization may authorize only the listed plan items and never an action listed in `separate_approval_required_for`.
