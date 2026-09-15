"""Witness -- APPLYING commonsense causal knowledge DISCRIMINATIVELY IN-CONTEXT (weighted ATOMIC edges, scored
relative to THIS story's candidates) STILL does not recover the zero-overlap residual, and the specific
commonsense CONFIDENCES are NOT load-bearing (a weight-shuffle twin matches/beats it). No integrator lift; the
zero-overlap gold slice stays below the base integrator. => a static commonsense KB is CONTEXT-FREE at any
application (naive OR weighted-discriminative); RETRIEVAL is the wrong shape. The residual needs
SITUATION-SPECIFIC GENERATIVE SIMULATION (the brain simulates THIS scenario forward, not retrieves general
'study->pass') -- the 'generate don't retrieve' thesis, now proven from the commonsense-KB side too.

problem: build_the_generative_result_state_world_model
Run: .venv/Scripts/python.exe verification/test_genworldmodel_applied_commonsense.py
"""
from __future__ import annotations
import os, sys
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
from experiments import exp_genworldmodel_applied_commonsense_v1 as A


def check(name, cond, detail=""):
    print("[%s] %s: %s" % ("PASS" if cond else "FAIL", name, detail))
    return bool(cond)


def main():
    o = A.run(cap=6000)
    oks = []

    oks.append(check(
        "W1 weighted, discriminative, in-context applied commonsense gives NO CI-separated integrator lift",
        not o["applied_vs_base"]["ci_sep"],
        "base %.3f +applied %.3f (%+.4f CI%s) solo %.3f fires %.3f" % (
            o["acc_base"], o["acc_with_applied"], o["applied_vs_base"]["delta"], o["applied_vs_base"]["ci"],
            o["applied_solo"], o["applied_fires"])))

    oks.append(check(
        "W2 the specific commonsense CONFIDENCES are NOT load-bearing: a weight-shuffle twin (same graph, "
        "permuted weights) matches or beats it -- only raw graph density carries, not the knowledge",
        not o["applied_vs_weighttwin"]["ci_sep"],
        "vs weight-shuffle twin %.3f (%+.4f CI%s)" % (
            o["acc_weight_twin"], o["applied_vs_weighttwin"]["delta"], o["applied_vs_weighttwin"]["ci"])))

    oks.append(check(
        "W3 it does NOT recover the ZERO-OVERLAP residual (applied-picks-gold stays low, below the base "
        "integrator's ~0.54 on that slice)",
        o["zov_applied_hit"] < 0.5,
        "zero-overlap gold n=%d: applied-picks-gold %.3f" % (o["n_zero_overlap_gold"], o["zov_applied_hit"])))

    oks.append(check(
        "W4 verdict = a static commonsense KB is context-free at any application -> retrieval is the wrong "
        "shape; the residual needs situation-specific generative simulation",
        o["verdict"] == "APPLIED_COMMONSENSE_NO_LIFT_CONTEXT_FREE", o["verdict"]))

    n = sum(oks)
    print("=" * 92)
    print("%s (%d/%d)" % ("ALL CHECKS PASS" if n == len(oks) else "SOME CHECKS FAILED", n, len(oks)))
    print("=" * 92)
    return 0 if n == len(oks) else 1


if __name__ == "__main__":
    sys.exit(main())


# --- pytest-collectable wrapper (pri 128, mechanical; see notes/problems/447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest/PROBLEM.md) ---
import pytest as _pri128_pytest
from verification._witness_wrap import _run_main_as_test as _pri128_run


@_pri128_pytest.mark.fast
def test_witness():
    _code, _out = _pri128_run(main)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
