#!/usr/bin/env python3
"""Witness for the grounded SIGN fix (Q2) + the corpus-SCALING analysis (Q3), 2026-09-09.

GROUNDED SIGN FIX (exp_causal_sign_grounded_ddyn_v1) -- the brain's mechanism the research named (sign of corr(dX,dY)
from grounded INTERVENTIONAL experience) recovers the coupling sign that co-occurrence (text-analog) cannot:
  G1  grounded interventional Delta-Delta recovers the coupling sign near-perfectly.
  G2  grounded beats the observational/co-occurrence (text-analog) sign CI-separated.
  G3  grounded beats the info-free random-sign twin CI-separated.

CORPUS SCALING (exp_causal_corpus_scaling_v1):
  S1  more corpus RAISES gold-link coverage (coverage@100% >> coverage@5%).
  S2  more corpus does NOT raise DIRECTION accuracy (it is intrinsically capped, not scale-limited).
  S3  the missing links are MOSTLY link-sparsity (Gricean everyday gap) -> add commonsense/procedural corpus.

Standalone. Run: .venv/Scripts/python.exe verification/test_causal_grounded_sign_and_scaling.py  (exit 0 = all PASS).
"""
from __future__ import annotations

import os
import sys

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments.exp_causal_sign_grounded_ddyn_v1 import run as run_grounded
from experiments.exp_causal_corpus_scaling_v1 import run as run_scaling


def _check(cond, msg):
    print(("PASS  " if cond else "FAIL  ") + msg)
    return 0 if cond else 1


def main() -> int:
    n_fail = 0
    g = run_grounded(smoke=True)
    c = g["coupling_sign_recovery"]
    n_fail += _check(c["grounded_ddyn"]["acc"] > 0.90,
                     "G1 grounded interventional Delta-Delta recovers the coupling sign (acc=%.3f > 0.90)"
                     % c["grounded_ddyn"]["acc"])
    n_fail += _check(c["paired_grounded_minus_observational"]["ci"][0] > 0.0,
                     "G2 grounded beats observational/co-occurrence CI-sep (paired %+.3f CI%s; grounded %.3f vs obs %.3f)"
                     % (c["paired_grounded_minus_observational"]["delta"], c["paired_grounded_minus_observational"]["ci"],
                        c["grounded_ddyn"]["acc"], c["observational_textanalog"]["acc"]))
    n_fail += _check(c["paired_grounded_minus_twin"]["ci"][0] > 0.0,
                     "G3 grounded beats the info-free random-sign twin CI-sep (paired %+.3f CI%s)"
                     % (c["paired_grounded_minus_twin"]["delta"], c["paired_grounded_minus_twin"]["ci"]))

    s = run_scaling(smoke=True)
    cur = s["scaling_curve"]
    cov_lo, cov_hi = cur[0]["coverage"], cur[-1]["coverage"]
    acc_lo, acc_hi = cur[0]["direction_acc_covered"], cur[-1]["direction_acc_covered"]
    n_fail += _check(cov_hi > cov_lo + 0.1,
                     "S1 more corpus RAISES coverage (%.3f@5%% -> %.3f@100%%)" % (cov_lo, cov_hi))
    n_fail += _check(acc_hi <= acc_lo + 0.03,
                     "S2 more corpus does NOT raise direction accuracy (%.3f@5%% -> %.3f@100%%; intrinsic cap, not scale)"
                     % (acc_lo, acc_hi))
    n_fail += _check(s["ideal_to_add"]["link_sparsity_gricean_frac"] > 0.5,
                     "S3 missing links MOSTLY link-sparsity/Gricean (%.0f%%) -> add commonsense/procedural corpus"
                     % (100 * s["ideal_to_add"]["link_sparsity_gricean_frac"]))

    print("RESULT  %s" % ("all PASS" if n_fail == 0 else "%d FAIL" % n_fail))
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
