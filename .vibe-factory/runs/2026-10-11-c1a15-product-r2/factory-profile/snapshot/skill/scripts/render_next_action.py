#!/usr/bin/env python3
"""Render only the human or agent action implied by a run-state."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ACTIONS = {
    "compile_context_packet": "G0: Compile the Context Packet and draft the Evidence Pack.",
    "run_g0_critic": "G0: Request the independent critic verdict.",
    "await_g1_approval": "Human Gate G1: Approve, reject, or request revision of the Use Case.",
    "await_g2a_structure_approval": "Human Gate G2A: Select, combine, reject, or request a new Wireframe structure.",
    "await_g2b_design_approval": "Human Gate G2B: Approve, reject, or request revision of the final visual design direction.",
    "await_g3_approval": "Human Gate G3: Approve, reject, or request revision of the Prototype Slice.",
    "prepare_prebuild_contract": "PBC-0: Lock approved G0-G3 artifacts before preparing the Pre-build Contract.",
    "lock_approved_inputs": "PBC-0: Lock the approved G0-G3 input versions, hashes, and planning baseline.",
    "run_engineering_discovery": "PBC-1: Select implementation methods from repository facts and engineering evidence; do not change product scope.",
    "prepare_coding_plan": "PBC-2: Create the machine plan and reserve the director-review and diagram paths for post-critic rendering.",
    "prepare_verification_plan": "PBC-3: Map every Acceptance Criterion to a slice, verifier, and evidence.",
    "await_pbc4_approval": "Human Gate PBC-4: Approve, reject, hold, or request revision of the implementation plan and its authorization scope.",
    "prepare_implementation_contract": "G4: Revalidate the planning baseline, compile the closed slice execution packet, and prepare the compact authorized execution card.",
    "implement_authorized_slice": "G5: Implement only the G4-authorized plan items and record the execution ledger.",
    "verify_authorized_slice": "G6: Execute the verification matrix and record evidence; request independent review only when the plan requires it, then run it once at batch completion.",
    "decide_cycle_outcome": "G7: Decide next slice, complete, repair, amendment, or blocked from recorded evidence.",
}


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: render_next_action.py <run-state.json>")
        return 2
    state = json.loads(Path(sys.argv[1]).read_text())
    action = state.get("next_action", "")
    print(ACTIONS.get(action, action or "No next action recorded."))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
