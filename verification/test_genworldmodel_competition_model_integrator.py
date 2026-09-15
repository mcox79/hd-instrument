"""Witness -- OPTIMIZATION #1 built brain-foundationally: a COMPETITION-MODEL cue-validity integrator
(Bates-MacWhinney; additive activation via the LANDED hdlab.graded_competition organ; cue weights learned by an
error-driven delta rule, no leak) resolves the cycle-9 dataset-dependence. ONE integrator, learning cue
validities per corpus, is ROBUST: on position-dominant GLUCOSE it MATCHES the position floor (no dilution), and
on position-useless TellMeWhy it CI-BEATS the best single cue (synergy). The learned weights ADAPT -- position
dominant on GLUCOSE, result-state dominant on TellMeWhy.

problem: build_the_generative_result_state_world_model
Run: .venv/Scripts/python.exe verification/test_genworldmodel_competition_model_integrator.py
"""
from __future__ import annotations
import os, sys
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
from experiments import exp_genworldmodel_competition_model_integrator_v1 as C


def check(name, cond, detail=""):
    print("[%s] %s: %s" % ("PASS" if cond else "FAIL", name, detail))
    return bool(cond)


def main():
    o = C.run(n_glu=3000, n_tmw=1500)
    glu = o["GLUCOSE"]; tmw = o["TellMeWhy"]
    oks = []

    oks.append(check(
        "W1 ROBUST on position-dominant GLUCOSE: the integrator MATCHES the best single cue (does NOT dilute the "
        "dominant position cue -- the cycle-9 blend-hurts failure is gone)",
        glu["integrator_test_acc"] >= glu["test_cue_acc"][glu["best_single_cue"]] - 0.02,
        "integrator %.3f vs best_cue(%s) %.3f (%+.4f CI%s)" % (
            glu["integrator_test_acc"], glu["best_single_cue"], glu["test_cue_acc"][glu["best_single_cue"]],
            glu["integrator_vs_best_cue"]["delta"], glu["integrator_vs_best_cue"]["ci"])))

    oks.append(check(
        "W2 SYNERGY on position-useless TellMeWhy: the integrator CI-BEATS the best single cue",
        tmw["integrator_vs_best_cue"]["ci_sep"] and tmw["integrator_test_acc"] > tmw["test_cue_acc"][tmw["best_single_cue"]],
        "integrator %.3f vs best_cue(%s) %.3f (%+.4f CI%s)" % (
            tmw["integrator_test_acc"], tmw["best_single_cue"], tmw["test_cue_acc"][tmw["best_single_cue"]],
            tmw["integrator_vs_best_cue"]["delta"], tmw["integrator_vs_best_cue"]["ci"])))

    oks.append(check(
        "W3 the learned cue validities ADAPT to the environment (Competition Model): position is the top positive "
        "weight on GLUCOSE, the result-state means_end is the top positive weight on TellMeWhy",
        max(glu["learned_weights"], key=lambda c: glu["learned_weights"][c]) == "position"
        and max(tmw["learned_weights"], key=lambda c: tmw["learned_weights"][c]) == "means_end",
        "GLUCOSE weights %s | TellMeWhy weights %s" % (glu["learned_weights"], tmw["learned_weights"])))

    oks.append(check(
        "W4 verdict = robust best-of-both", o["robust_best_of_both"] and "ROBUST" in o["verdict"], o["verdict"]))

    n = sum(oks)
    print("=" * 92)
    print("%s (%d/%d)  verdict=%s" % ("ALL CHECKS PASS" if n == len(oks) else "SOME CHECKS FAILED", n, len(oks), o["verdict"]))
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
