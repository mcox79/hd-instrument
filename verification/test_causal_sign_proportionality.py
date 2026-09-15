#!/usr/bin/env python3
"""Witness for the SIGNED-PROPORTIONALITY grounding-bridge test (2026-09-09) -- the DEFINITIVE text-sign located negative.

The research-recommended route (mine EXPLICIT signed qualitative-proportionality edges from quantitative/procedural
text, compose via sign-propagation) was built (exp_causal_signed_proportionality_mine_v1 -> 440k signed edges, 53%
negative) and tested on WIQA more/less. FULL store gives 78% coverage yet the arm TIES the scrambled-store falsifier
and does NOT beat the co-occurrence baseline -> the text-stated SIGN content is not load-bearing for story-specific
more/less. 7th sign source to fail; text is exhausted for the sign (the numeric-covariation/interventional Delta-Delta
route is the only one left -- see exp_causal_sign_grounded_ddyn_v1, which PROVED that route works given grounded data).

Asserts the smoke-stable located-negative facts (fixed seeds); the full-store numbers (78% coverage, ties) are the
decisive evidence and are recorded in data/exp_causal_sign_proportionality_wiqa_v1/metrics.json + the docs.
  P1  arm does NOT beat the scrambled-store falsifier CI-sep (no CI-sep positive) -> sign content not load-bearing.
  P2  arm does NOT beat the co-occurrence baseline CI-sep.
  P3  the store HAS coverage (the negative is a content negative, not an empty test).

Run: .venv/Scripts/python.exe verification/test_causal_sign_proportionality.py  (exit 0 = located-negative confirmed).
"""
from __future__ import annotations

import json
import os
import sys

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments.exp_causal_sign_proportionality_wiqa_v1 import run as run_prop


def _check(cond, msg):
    print(("PASS  " if cond else "FAIL  ") + msg)
    return 0 if cond else 1


def main() -> int:
    n_fail = 0
    r = run_prop(smoke=True)
    f = r["more_vs_less_FULL"]
    n_fail += _check(f["paired_arm_minus_scrambled"]["ci"][0] <= 0.0,
                     "P1 FALSIFIER: mined signed-proportionality does NOT beat the scrambled-store twin CI-sep "
                     "(arm-scrambled %+.4f CI%s) -> the text-stated SIGN content is not load-bearing"
                     % (f["paired_arm_minus_scrambled"]["delta"], f["paired_arm_minus_scrambled"]["ci"]))
    n_fail += _check(f["paired_arm_minus_cooccur"]["ci"][0] <= 0.0,
                     "P2 arm does NOT beat the co-occurrence baseline CI-sep (arm-cooccur %+.4f CI%s)"
                     % (f["paired_arm_minus_cooccur"]["delta"], f["paired_arm_minus_cooccur"]["ci"]))
    n_fail += _check(r["n_effect_covered"] > 5,
                     "P3 store has coverage (%d effect items covered; the negative is a CONTENT negative, not empty)"
                     % r["n_effect_covered"])

    # if the full-store metrics exist, surface the decisive high-coverage numbers (not asserted -- reported)
    fp = os.path.join(_REPO, "data", "exp_causal_sign_proportionality_wiqa_v1", "metrics.json")
    if os.path.exists(fp):
        try:
            m = json.load(open(fp, encoding="utf-8"))
            if not m.get("smoke"):
                ff = m["more_vs_less_FULL"]
                print("INFO  full store (%s): coverage %.0f%% | arm %.3f vs scrambled %.3f (%+.4f) vs cooccur %.3f -- ties => definitive negative"
                      % (m["store"], 100 * m["coverage_on_effect"], ff["arm"]["acc"], ff["scrambled_store_twin"]["acc"],
                         ff["paired_arm_minus_scrambled"]["delta"], ff["cooccur_baseline"]["acc"]))
        except Exception:
            pass

    print("RESULT  %s (text-sign located-negative confirmed; numeric/interventional route is the only one left)"
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
