"""Witness -- OPTIMIZATION #2 built brain-foundationally: DEEPEN the result-state rollout (multi-step plan/script
chaining; Schank-Abelson / Mattar-Daw; reusing the LANDED directed BFS `_reach` + `multistep_fire` machinery,
generalized past its K=2 cap). On TellMeWhy non-adjacent GOAL: deeper K MONOTONICALLY adds reach (coverage
~12%->38%) and lifts accuracy (deepK1 0.326 -> deepK3 0.380), catching up to the hand-composed single-step
result-state and beating base CI-sep -- BUT it is COVERAGE-BOUND: even at K=4 only ~38% of GOAL items get any
multi-step bridge on the sparse CSKG store, so it does not EXCEED the single-step result-state. The completing
lever is STORE DENSITY (the curated plan/meaning foundation, Q111), not the rollout mechanism (which is built).

problem: build_the_generative_result_state_world_model
Run: .venv/Scripts/python.exe verification/test_genworldmodel_deep_rollout.py
"""
from __future__ import annotations
import os, sys
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
from experiments import exp_genworldmodel_deep_rollout_v1 as D


def check(name, cond, detail=""):
    print("[%s] %s: %s" % ("PASS" if cond else "FAIL", name, detail))
    return bool(cond)


def main():
    o = D.run(n=1500)
    g = o["GOAL"]; gv = g["overall"]; cov = g["coverage"]
    oks = []

    oks.append(check(
        "W1 depth is a MONOTONE lever: deeper K adds reach (coverage grows K1->K4) and does not lower accuracy "
        "(best deep rollout >= single-hop deepK1)",
        cov["deepK4"] > cov["deepK1"] and gv[g["best_deep"]] >= gv["deepK1"] - 1e-9,
        "coverage K1 %.3f -> K4 %.3f | deepK1 %.3f best_deep(%s) %.3f" % (
            cov["deepK1"], cov["deepK4"], gv["deepK1"], g["best_deep"], gv[g["best_deep"]])))

    oks.append(check(
        "W2 the multi-step rollout is a REAL signal: the best deep arm CI-beats base",
        g["bestdeep_vs_base"]["ci_sep"] and gv[g["best_deep"]] > gv["base"],
        "best_deep %.3f vs base %.3f (%+.4f CI%s)" % (
            gv[g["best_deep"]], gv["base"], g["bestdeep_vs_base"]["delta"], g["bestdeep_vs_base"]["ci"])))

    oks.append(check(
        "W3 COVERAGE-BOUND: even at K=4 the majority of GOAL items get NO multi-step bridge (coverage < 0.5), and "
        "depth does not EXCEED the single-step result-state -> the ceiling is store density (Q111), not the rollout",
        cov["deepK4"] < 0.5 and gv[g["best_deep"]] <= gv["rs_refine"] + 0.02,
        "coverage@K4 %.3f | best_deep %.3f vs rs_refine %.3f" % (
            cov["deepK4"], gv[g["best_deep"]], gv["rs_refine"])))

    oks.append(check(
        "W4 verdict = DEPTH_COVERAGE_BOUND_ON_EXISTING_STORE",
        o["verdict"] == "DEPTH_COVERAGE_BOUND_ON_EXISTING_STORE", o["verdict"]))

    n = sum(oks)
    print("=" * 92)
    print("%s (%d/%d)  GOAL n=%d" % ("ALL CHECKS PASS" if n == len(oks) else "SOME CHECKS FAILED", n, len(oks), g["n"]))
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
