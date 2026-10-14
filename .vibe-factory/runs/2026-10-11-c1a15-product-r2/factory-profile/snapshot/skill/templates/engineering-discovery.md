# Engineering Discovery {{version}}

## Repository and environment facts

Only observed facts. Link the planning baseline and relevant code/configuration evidence.

## Requirement signals and cheapest verifiers

For each relevant AC, identify side effect, quality/failure signal, and the cheapest deterministic verifier.

## Candidate methods and evidence

Read the fixed Engineering Playbook version and list only the decision-rule IDs relevant to this run, plus repository/environment facts that affect their applicability. List selected and rejected skill/model-role/workflow/loop/harness/graph candidates. This is not a product design change. Do not copy or snapshot Wiki originals here.

## Spike decision

Default: no spike. If a disposable spike is proposed, record the separate approval, isolated workspace, no-production/no-live boundary, and disposal evidence. Otherwise state which first approved implementation slice will resolve the uncertainty.

## Coupled-control feasibility

State `not_required` only as `single_control`, or as `existing_observed_evidence` with a current Planning Baseline or Selection Register pointer. When two or more isolation, harness, or process controls must work together for a verifier or authority boundary, run only an internal compatibility probe before PBC approval: no product/dependency source change, external connection, live service, secret, sensitive data, or deployment. Record control set, temporary isolation, command, expected and observed result, evidence, and cleanup in `feasibility-probe.json`; Coding Plan's `feasibility_preflight` locks its path/hash. A failed or inconclusive probe blocks that plan; a probe requiring product behavior or external actions follows the disposable-spike policy instead.

## Revalidation triggers
