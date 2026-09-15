#!/usr/bin/env python3
"""Witness for the SIGN located-negative (2026-09-09): the brain's force-dynamic relation-type mechanism, faithfully
built (research-directed) and tested with the proper SCRAMBLED-LEXICON falsifier, does NOT carry the WIQA more/less
sign. This is the 6th sign source to fail; per the research gate + the owner protocol (a rigorous negative on the
brain's ACTUAL mechanism is a full pass), it means the sign requires grounded interventional Delta-Delta experience.

Asserts the smoke-stable located-negative facts (fixed seeds):
  SIGN-1  the force-dynamic coupling does NOT beat its scrambled-lexicon twin CI-separated (falsifier: no CI-sep win).
  SIGN-2  the coupling adds no CI-sep marginal over the embedded-polarity baseline (arm - phrase, no CI-sep win).
  SIGN-3  the instrument is alive: the setup produced effect items + a non-trivial covered subset (the test CAN run).

Standalone. Run: .venv/Scripts/python.exe verification/test_causal_sign_forcedynamic.py  (exit 0 = located-negative confirmed).
"""
from __future__ import annotations

import os
import sys

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments.exp_causal_sign_forcedynamic_v1 import run as run_sign


def _check(cond, msg):
    print(("PASS  " if cond else "FAIL  ") + msg)
    return 0 if cond else 1


def main() -> int:
    n_fail = 0
    s = run_sign(smoke=True)
    f = s["more_vs_less_FULL"]
    n_fail += _check(f["paired_arm_minus_scrambled"]["ci"][0] <= 0.0,
                     "SIGN-1 FALSIFIER: force-dynamic coupling does NOT beat scrambled-lexicon twin CI-sep "
                     "(arm-scrambled %+.4f CI%s) -> relation-type force dynamics does NOT carry the sign"
                     % (f["paired_arm_minus_scrambled"]["delta"], f["paired_arm_minus_scrambled"]["ci"]))
    n_fail += _check(f["paired_arm_minus_phrase"]["ci"][0] <= 0.0,
                     "SIGN-2 coupling adds no CI-sep marginal over embedded-polarity baseline "
                     "(arm-phrase %+.4f CI%s)" % (f["paired_arm_minus_phrase"]["delta"], f["paired_arm_minus_phrase"]["ci"]))
    n_fail += _check(s["n_effect_items"] > 50 and s["n_effect_covered"] > 5,
                     "SIGN-3 instrument alive: %d effect items, %d covered (test CAN run; the negative is real, not empty)"
                     % (s["n_effect_items"], s["n_effect_covered"]))
    print("RESULT  %s (located-negative confirmed)" % ("all PASS" if n_fail == 0 else "%d FAIL" % n_fail))
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
