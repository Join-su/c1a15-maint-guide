# Execution Handoff

> Create this only when the executing Agent or session changes. It is not a per-slice report.

## Authority and packet

| Field | Value |
|---|---|
| Approved plan version | |
| Authorized plan item(s) | |
| PBC-4 decision path / hash | |
| Current slice execution packet path / hash | |
| Current implementation contract path / hash | |

## Verified state

| Completed item / AC | Verifier and result | Evidence / ledger row |
|---|---|---|
| | | |

## Resume safely

| Next safe action | Unfinished verifier | Blocker or stop condition |
|---|---|---|
| | | |

The new executor verifies the listed hashes and authorization before resuming. If any value differs, return to G4 rather than continuing from this handoff.
