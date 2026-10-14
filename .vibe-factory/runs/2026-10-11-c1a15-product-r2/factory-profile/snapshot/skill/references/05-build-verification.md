# Build and verification

## G4→G7 cycle

```text
PBC-4 approved plan
  → G4 baseline revalidation + implementation contract
  → G5 one authorized vertical slice
  → G6 verifier evidence + independent review
  → G7 next slice | complete | repair | amendment | blocked
```

The cycle does not create new product behavior. Every code/test action references an authorized plan item. A failed or missing verifier is evidence, never a pass. An unexpected fact is also not a local note: record its affected plan items, assumptions, and controls in the execution ledger before selecting repair, amendment, or the next slice.

## Continuous batch execution

Use `continuous_batch` only when PBC-4 authorizes the batch item IDs, automatic quality gates, and stop conditions together. A normal slice records one compact execution card plus one execution-ledger row; it does not wait for a human or critic when its required automatic gates and AC evidence pass.

Automatic gates must include the plan-item/AC scope check and its planned AC verifier, plus the applicable static, format, type, contract, or performance budget checks selected in the Coding Plan. A passing build alone is not a passing slice.

Escalate to `independent_critic` before continuing when a slice touches external actions, authority, sensitive data, irreversible effects, public interfaces or migrations, a performance budget, or an unexpected failure. UI/AI is an escalation trigger only when an important changed AC cannot be judged by deterministic assertion, fixed-condition visual/interaction evidence, or an explicit pass/fail observation defined in the Verification Matrix. A UI/AI slice satisfying those checks and no other trigger remains `automatic`. Before `complete`, create one `batch-evidence-index.json` that lists every completed slice's packet, ledger, and verification report with hashes. Run one final integration critic over that index and its accumulated evidence. That review confirms only evidence completeness and cross-slice contract alignment; it is not a second implementation or product-quality review. This is one machine index per batch, not a new report per slice.

## Closed slice execution packet

G4 compiles one `slice-execution-packet.json` per slice. G5~G7 read only that packet, the current code, and the current slice's generated ledger/report. The packet is not a prose summary: it copies selected Coding Plan items (including compiled behavior, UI/state/interaction, authority/data, and applicable logical-flow behavior), linked ACs with all observable conditions from the Verification Matrix, matching verification entries, and only the safe adversarial cases whose `completion_plan_item_id` belongs to the slice. It also copies implementation authorization and planning-baseline result as structured source-of-truth data.

This packet exists because G5, G6, and G7 reuse the same slice contract. Before opening a new slice packet, compact only the prior slice's no-longer-needed raw working context; then load the new packet and current code directly. Do not create a compact artifact for this: the in-memory checkpoint is not a source of truth. If the packet is incomplete, stop for the declared amendment or decision path rather than reloading PBC or pre-PBC sources.

G4~G7 never directly read or inject a Use Case Bundle, Prototype Bundle, Evidence Pack, or G2 artifact. Those are PBC input lineage, not execution input. If the PBC contract lacks information needed to implement or verify, stop for an L1 plan amendment, a blocked out-of-scope contract change, or human judgment; do not reopen pre-PBC artifacts to fill the gap.

## Authority

PBC-4 `implementation_authorization` permits only its plan version and allowed item IDs. Deployment, external transmission, real-provider calls, sensitive data access, and irreversible effects remain blocked unless separately approved. A repository/dependency/environment change since the planning baseline requires revalidation before G5.

## Repair and change

Use a bounded repair loop only when a deterministic verifier can say pass/fail. Record its cap and outcome in the execution ledger. L0 implementation details remain in the ledger, but a newly observed fact still requires an impact check against the current plan; `none` and `L0` require a passing recheck, otherwise the fact is L1 or out of scope. L1 changes require an approved Amendment before implementation continues. A product-contract change is outside this Skill and stops the run.
