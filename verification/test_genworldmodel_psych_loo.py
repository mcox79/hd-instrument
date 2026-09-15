"""Witness -- the CONTEXT-CONDITIONED LOO over the PSYCHOLOGICAL (goal) ontology (research Design 1b:
goal-resolution counterfactual necessity; Trabasso/van den Broek/Suh 1989 applied the SAME LOO test to
motivational causation). Reuses the LANDED goal machinery (goal_register.extract_goals/bind_agents/
track_status_thwart -- excluding a candidate's events IS the fold). MEASURES the signal-loss funnel and files a
located negative: goals ARE extracted (GLUCOSE ~0.64 / TellMeWhy ~0.78) but only ~0.16 get RESOLVED
(satisfied/failed) and only ~0.02 are LOO-necessary -> the loss is at goal-RESOLUTION (track_status_thwart needs
a later event whose predicate LEXICALLY matches the goal head; goals are satisfied SEMANTICALLY, not lexically).
No CI-sep integrator lift on either corpus. The wall is goal-outcome SATISFACTION detection = the meaning
foundation (semantic goal<->outcome relation), the same Q111 dependency, now on the psychological ontology.

problem: build_the_generative_result_state_world_model
Run: .venv/Scripts/python.exe verification/test_genworldmodel_psych_loo.py
"""
from __future__ import annotations
import os, sys
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
from experiments import exp_genworldmodel_psych_loo_v1 as P


def check(name, cond, detail=""):
    print("[%s] %s: %s" % ("PASS" if cond else "FAIL", name, detail))
    return bool(cond)


def main():
    o = P.run(n_glu=3000, n_tmw=1500)
    gd = o["goal_diagnostic"]; g = gd["GLUCOSE"]; t = gd["TellMeWhy_GOAL"]; oks = []

    oks.append(check(
        "W1 the psychological goal machinery RUNS and goals ARE extracted on most items (has_goal > 0.5 both) "
        "-- extraction is NOT the bottleneck",
        g["has_goal"] > 0.5 and t["has_goal"] > 0.5,
        "GLUCOSE has_goal %.3f | TellMeWhy has_goal %.3f" % (g["has_goal"], t["has_goal"])))

    oks.append(check(
        "W2 the signal is LOST at goal-RESOLUTION: only a small fraction of extracted goals RESOLVE "
        "(has_resolved_goal << has_goal), and LOO-necessity fires on ~2%",
        g["has_resolved_goal"] < 0.3 and g["has_resolved_goal"] < g["has_goal"] - 0.2
        and t["has_resolved_goal"] < 0.3 and o["max_fires"] < 0.1,
        "GLUCOSE goal %.3f -> resolved %.3f -> fires %.3f | TMW goal %.3f -> resolved %.3f -> fires %.3f" % (
            g["has_goal"], g["has_resolved_goal"], g["loo_fires"], t["has_goal"], t["has_resolved_goal"], t["loo_fires"])))

    oks.append(check(
        "W3 HARD-FAIL: no CI-separated integrator lift on either corpus (the ~2% firing slice cannot lift)",
        not o["integrator_lift_ci_sep"],
        "GLUCOSE best +int %s | TMW best +int %s" % (
            max(o["GLUCOSE"]["arms"].values(), key=lambda a: a["fires"])["vs_base"],
            max(o["TellMeWhy_GOAL"]["arms"].values(), key=lambda a: a["fires"])["vs_base"])))

    oks.append(check(
        "W4 verdict = psych-LOO HARD-FAIL, loss localized to goal-resolution (semantic goal<->outcome, Q111)",
        o["verdict"] == "PSYCH_LOO_HARD_FAIL", o["verdict"]))

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
