#!/usr/bin/env python3
"""Witness for the STOICHIOMETRY sign lever (2026-09-09) -- the FIRST sign source to beat the falsifier.

On WIQA's chemistry-tractable slice, the coupling sign computed from GROUND-TRUTH reaction stoichiometry (reactant -,
product +) BEATS the scrambled-role falsifier CI-separated -- the exact control that all 7 prose sign sources TIED.
This proves the sign is carried by the reaction STRUCTURE (formal-model route), not by co-occurrence. Domain-limited
(~10% WIQA coverage, the science slice); the everyday/biological tail still needs the grounded-experience program.

Cell is tagger-free (fast), so the witness runs the FULL population.
  ST1  arm beats the SCRAMBLED-ROLE falsifier CI-separated on the covered slice (the discriminator prose failed).
  ST2  the scrambled-role twin is at/below chance (scrambling roles destroys/inverts the sign) -- confirms the sign
       lives in the stoichiometric structure.
  ST3  coverage is the honest domain-limited science slice (a precision lever, not a universal fix).

Run: .venv/Scripts/python.exe verification/test_causal_sign_stoichiometry.py  (exit 0 = falsifier beaten).
"""
from __future__ import annotations

import os
import sys

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments.exp_causal_sign_stoichiometry_wiqa_v1 import run as run_stoich


def _check(cond, msg):
    print(("PASS  " if cond else "FAIL  ") + msg)
    return 0 if cond else 1


def main() -> int:
    n_fail = 0
    r = run_stoich(smoke=False)          # tagger-free -> full run is fast
    c = r["COVERED_subset"]
    n_fail += _check(c["paired_arm_minus_SCRAMBLED"]["ci"][0] > 0.0,
                     "ST1 stoichiometry sign BEATS the scrambled-role falsifier CI-sep (arm %.3f vs scrambled %.3f, "
                     "paired %+.3f CI%s) -- the control all 7 prose sources tied"
                     % (c["arm"]["acc"], c["scrambled_role_twin"]["acc"], c["paired_arm_minus_SCRAMBLED"]["delta"],
                        c["paired_arm_minus_SCRAMBLED"]["ci"]))
    n_fail += _check(c["scrambled_role_twin"]["acc"] <= 0.52,
                     "ST2 scrambled-role twin at/below chance (%.3f) -- scrambling roles destroys the sign => the sign "
                     "lives in the reaction STRUCTURE" % c["scrambled_role_twin"]["acc"])
    n_fail += _check(0.03 < r["coverage"] < 0.35,
                     "ST3 honest domain-limited coverage (%.1f%% of effect items = the science slice; precision lever, "
                     "not a universal fix)" % (100 * r["coverage"]))
    print("RESULT  %s (stoichiometry = the first sign source to beat the falsifier, on its domain slice)"
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
