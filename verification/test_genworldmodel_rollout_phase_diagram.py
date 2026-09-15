"""Witness -- PHASE-DIAGRAM move on the deep rollout (owner: "remember the phase diagram"). The Prototype-B
"coverage-bound ceiling" was a MOVABLE operating point: sliding the store-density knob (augment the causal graph
with associative edges, swept rho) lifts the goal-gated multi-step rollout over base AND topical CI-separated on
TellMeWhy GOAL (op-point selected on train, scored on a disjoint test split -> no leak, no selection bias). BUT
the lift is RAW-DENSITY, not edge-structure: an info-free same-density RANDOM-edge twin matches it. So density is
a free knob worth ~+0.17, but a STRUCTURE-dependent (load-bearing) lift needs a denser CORRECT store -- the
edge-correctness frontier (meaning/plan foundation, Q111), consistent with the solution's meta-conclusion.

problem: build_the_generative_result_state_world_model
Run: .venv/Scripts/python.exe verification/test_genworldmodel_rollout_phase_diagram.py
"""
from __future__ import annotations
import os, sys
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
from experiments import exp_genworldmodel_rollout_phase_diagram_v1 as P


def check(name, cond, detail=""):
    print("[%s] %s: %s" % ("PASS" if cond else "FAIL", name, detail))
    return bool(cond)


def main():
    o = P.run(n=1500)
    oks = []

    oks.append(check(
        "W1 DENSITY IS MOVABLE, not a ceiling: the selected dense op-point beats the SPARSE-store (rho=0) rollout "
        "on the test split (Prototype-B 'coverage-bound' wall was a movable operating point)",
        o["best_acc_test"] > o["sparse_best_acc_test"],
        "selected %s test acc %.3f vs sparse-best %.3f (base %.3f)" % (
            o["selected_operating_point"], o["best_acc_test"], o["sparse_best_acc_test"], o["base_acc_test"])))

    oks.append(check(
        "W2 the density move beats topical CI-separated (real reach value over the pairwise cue)",
        o["best_vs_topical_test"]["ci_sep"],
        "vs topical %.3f (%+.4f CI%s)" % (
            o["topical_acc_test"], o["best_vs_topical_test"]["delta"], o["best_vs_topical_test"]["ci"])))

    oks.append(check(
        "W3 the lift is RAW-DENSITY, not edge-STRUCTURE: an info-free same-density RANDOM-edge twin MATCHES the "
        "relatedness-augmented graph (not CI-beaten) -> a load-bearing lift needs a denser CORRECT store (Q111)",
        not o["best_vs_infofree_twin_test"]["ci_sep"],
        "best %.3f vs info-free density twin %.3f (%+.4f CI%s); load_bearing=%s" % (
            o["best_acc_test"], o["infofree_density_twin_acc_test"], o["best_vs_infofree_twin_test"]["delta"],
            o["best_vs_infofree_twin_test"]["ci"], o["density_lift_load_bearing"])))

    oks.append(check(
        "W4 verdict = density move lifts but is associative-density (not structure) bound",
        o["verdict"] == "DENSITY_MOVE_LIFTS_BUT_JUST_ASSOCIATIVE_DENSITY", o["verdict"]))

    n = sum(oks)
    print("=" * 92)
    print("%s (%d/%d)  GOAL n=%d test n=%d" % (
        "ALL CHECKS PASS" if n == len(oks) else "SOME CHECKS FAILED", n, len(oks), o["n_goal"], o["n_test"]))
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
