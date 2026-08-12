"""One-shot: clear orphaned v3_chain_gen_fix running marker on remote_cpu_queue.

Orchestrator note (2026-06-27 ~19:10 PDT):
- Cell substrate_multihop_brain_pushback_composition_v3_chain_gen_fix marked running
  since 2026-06-27T13:21:41 by cpu_runner_0.
- Confirmed no live Python process for this script on remote (tasklist scan).
- v3_redispatch already completed at 15:54 PDT with RAIL_SANITY_BREACH verdict.
- No checkpoint dir for v3_chain_gen_fix (no salvageable work).
- Clearing to outcome=orphaned_timeout via force_status (not mark_outcome:
  mark_outcome requires current status=='running' which it has, but force_status
  is the broader-used orchestrator path).
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(r"C:\dev\hd-instrument")
sys.path.insert(0, str(REPO))

from tools.safe_queue import force_status

QUEUE = REPO / "data" / "remote_cpu_queue" / "queue.json"
NAME = "substrate_multihop_brain_pushback_composition_v3_chain_gen_fix"

ok = force_status(
    QUEUE,
    NAME,
    "orphaned_timeout",
    note=(
        "orchestrator(2026-06-27T19:10 PDT): cleared stale running marker. "
        "No Python PID alive for this script; v3_redispatch (same script) "
        "completed at 15:54 PDT with RAIL_SANITY_BREACH (baseline 0.5817 "
        "outside [0.10, 0.20] rail). No salvageable checkpoint."
    ),
)
print("FORCE_STATUS_OK" if ok else "FORCE_STATUS_FAIL")
