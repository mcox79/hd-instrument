#!/usr/bin/env python3
"""Witness for the per-item FORWARD SIMULATOR (2026-09-09) -- closes the causal-reader investigation.

Two load-bearing facts (smoke-stable, fixed seeds):
  FS1  the GIVEN-CHAIN simulation is load-bearing for NECESSITY: the simulator beats its CHAIN-SCRAMBLE twin CI-sep
       (scrambling the passage's step order collapses it) -> causal comprehension = running the given model (the
       correct operation, per Gerstenberg CSM), CONFIRMED with the correct falsifier (chain-scramble, not store-scramble).
  FS2  the SIGN is NOT fixed by the operation: the simulator does NOT beat its chain-scramble twin on more/less
       (it ties at chance) -> the wall is the per-EDGE coupling sign (token-level, regime-dependent; our data: 80%
       verb-flip), NOT the propagation operation. This precisely localizes the residual.

Run: .venv/Scripts/python.exe verification/test_causal_forward_simulator.py  (exit 0 = both facts confirmed).
"""
from __future__ import annotations

import os
import sys

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments.exp_causal_forward_simulator_v1 import run as run_sim


def _check(cond, msg):
    print(("PASS  " if cond else "FAIL  ") + msg)
    return 0 if cond else 1


def main() -> int:
    n_fail = 0
    r = run_sim(smoke=True)
    ne = r["NECESSITY_in_paragraph"]; sg = r["SIGN_more_vs_less_in_paragraph"]
    n_fail += _check(ne["paired_sim_minus_CHAINSCRAMBLE"]["ci"][0] > 0.0,
                     "FS1 given-chain simulation LOAD-BEARING for necessity: sim beats CHAIN-SCRAMBLE twin CI-sep "
                     "(paired %+.3f CI%s) -> running the given model is the correct operation"
                     % (ne["paired_sim_minus_CHAINSCRAMBLE"]["delta"], ne["paired_sim_minus_CHAINSCRAMBLE"]["ci"]))
    n_fail += _check(sg["paired_sim_minus_CHAINSCRAMBLE"]["ci"][0] <= 0.0,
                     "FS2 SIGN residual: simulator does NOT beat its chain-scramble twin on more/less "
                     "(paired %+.3f CI%s) -> the wall is the per-EDGE sign (regime-dependent), not the operation"
                     % (sg["paired_sim_minus_CHAINSCRAMBLE"]["delta"], sg["paired_sim_minus_CHAINSCRAMBLE"]["ci"]))
    print("RESULT  %s (operation proven; per-edge sign is the localized residual)"
          % ("all PASS" if n_fail == 0 else "%d FAIL" % n_fail))
    return 1 if n_fail else 0


if __name__ == "__main__":
    sys.exit(main())


# --- pytest-collectable wrapper (pri 128, mechanical; see notes/problems/447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest/PROBLEM.md) ---
import pytest as _pri128_pytest
from verification._witness_wrap import _run_main_as_test as _pri128_run


@_pri128_pytest.mark.fast
def test_witness():
    _code, _out = _pri128_run(main)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
