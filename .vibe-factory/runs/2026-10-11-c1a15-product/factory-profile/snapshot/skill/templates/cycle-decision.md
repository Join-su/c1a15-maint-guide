# Cycle Decision {{slice_id}}

## Verified result

## Decision

`next_slice | complete | repair | amendment | blocked`

## Evidence and remaining plan items

## Mismatch classification

State `none`, `L0`, `L1`, or `out_of_scope_contract_change` and why.

## Unexpected-fact impact check

Link each new observation in the execution ledger and state its affected plan items, assumptions, controls, recheck result, and whether it requires `L1` or `out_of_scope_contract_change`.

## Required next action

## Final Integration Critic Review

Required only for `complete`. Link the G6-format critic review that assessed the accumulated batch ledgers and verification reports.

## Batch Evidence Index

Required only for `complete`. Link one `batch-evidence-index.json` containing the packet, ledger, and verification-report paths plus hashes for every slice included in the completed batch.

## Learning Record

Required for unexpected results that create an L1 change.

## Out-of-scope contract-change record

Required only when this cycle is `blocked` because the approved product contract must change. Link `out-of-scope-contract-change.md`. It records the later decision required; it does not revise or replace an approved artifact.
