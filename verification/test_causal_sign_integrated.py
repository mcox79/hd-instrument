#!/usr/bin/env python3
"""Witness for the INTEGRATED sign reader (2026-09-09): forward-simulator necessity + PASSAGE-CONTEXT-GATED formal-model
edge signs. The instantiation fix (passage selects which formal model fires) grows coverage AND keeps precision.

Cell is tagger-free (fast) -> witness runs the FULL population.
  IG1  SIGN: context-gated formal sign BEATS the scrambled-sign falsifier CI-sep on the gated subset (the control all
       prose sources tied; loose grounding also tied at 26% -- context-gating restores the win).
  IG2  3-WAY (necessity+sign) beats the scrambled twin AND majority CI-sep on the gated subset.
  IG3  the instantiation fix grew coverage past the naive chemistry-only ~9% while staying honestly domain-limited.

Run: .venv/Scripts/python.exe verification/test_causal_sign_integrated.py  (exit 0 = integration confirmed).
"""
from __future__ import annotations

import os
import sys

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments.exp_causal_sign_integrated_v1 import run as run_int


def _check(cond, msg):
    print(("PASS  " if cond else "FAIL  ") + msg)
    return 0 if cond else 1


def main() -> int:
    n_fail = 0
    r = run_int(smoke=False)
    s = r["SIGN_more_vs_less_on_gated_subset"]; t3 = r["THREE_WAY_on_gated_subset"]
    n_fail += _check(s["paired_arm_minus_SCRAMBLED"]["ci"][0] > 0.0,
                     "IG1 context-gated SIGN beats the scrambled-sign falsifier CI-sep (arm %.3f vs scrambled %.3f, "
                     "paired %+.3f CI%s)" % (s["arm"]["acc"], s["scrambled_sign_twin"]["acc"],
                     s["paired_arm_minus_SCRAMBLED"]["delta"], s["paired_arm_minus_SCRAMBLED"]["ci"]))
    n_fail += _check(t3["paired_arm_minus_scrambled"]["ci"][0] > 0.0 and t3["arm"]["acc"] > t3["majority"]["acc"],
                     "IG2 3-WAY beats scrambled + majority CI-sep (arm %.3f vs scrambled %.3f vs majority %.3f, paired "
                     "%+.3f CI%s)" % (t3["arm"]["acc"], t3["scrambled_sign"]["acc"], t3["majority"]["acc"],
                     t3["paired_arm_minus_scrambled"]["delta"], t3["paired_arm_minus_scrambled"]["ci"]))
    n_fail += _check(0.10 < r["coverage"] < 0.35,
                     "IG3 instantiation fix grew coverage past naive ~9%% to %.1f%% (still honestly domain-limited = "
                     "the science slice)" % (100 * r["coverage"]))
    print("RESULT  %s (integration: passage-context gating grows coverage AND keeps the falsifier-beating sign)"
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
