"""Witness -- the PRECISE, orthogonal signal-loss trace + two component-fidelity audits the cumulative ladder
hid. EXACTLY where we lose signal on modern TellMeWhy non-adjacent:
 * TOPICAL CONTENT is LOAD-BEARING, not a removable confound (removing it CRASHES accuracy to ~0.10) -- but it
   is ALSO the dominant ERROR source (>80% of the base's wrong picks are the max-topical NON-cause): the
   generative means-end must OVERRIDE topical, and fails to exactly where it is absent.
 * EXTRACTION is NOT the loss point (main-verb recall ~0.98, goal-marker ~0.89) -- the "goal object not in q"
   is the multi-step phenomenon, not a parse failure.
 * The GOAL means-end generation coverage, EXACT by hop-distance: DIRECT + SINGLE_STEP + TWO_HOP reach ~46%;
   the largest single tier is DEEP_MULTISTEP (~51%) -- goal->action plans beyond a 2-hop reach, the exact
   knowledge-depth residual.

problem: build_the_generative_result_state_world_model
Run: .venv/Scripts/python.exe verification/test_genworldmodel_signal_loss_precise.py
"""
from __future__ import annotations
import os, sys
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
from experiments import exp_genworldmodel_signal_loss_precise_v1 as P


def check(name, cond, detail=""):
    print("[%s] %s: %s" % ("PASS" if cond else "FAIL", name, detail))
    return bool(cond)


def main():
    o = P.run(n=1500)
    tc = o["topical_confound"]; ef = o["extraction_fidelity"]; tf = o["reachability_tiers"]
    oks = []

    oks.append(check(
        "W1 TOPICAL content is LOAD-BEARING (removing it crashes accuracy far below base) -- NOT a removable confound (a corrected hypothesis)",
        tc["no_topical_vs_base"]["delta"] < -0.05 and o["overall"]["no_topical"] < o["overall"]["base"] - 0.05,
        "base %.3f vs no_topical %.3f (%+.4f CI%s)" % (
            o["overall"]["base"], o["overall"]["no_topical"], tc["no_topical_vs_base"]["delta"],
            tc["no_topical_vs_base"]["ci"])))

    oks.append(check(
        "W2 BUT topical is the dominant ERROR source: >80% of the base's wrong picks are the max-topical NON-cause -> the generative means-end must OVERRIDE it and fails where absent",
        tc["frac_of_base_errors_from_topical"] > 0.8,
        "%.0f%% of base errors pick the max-topical non-cause (n_wrong=%d)" % (
            100 * tc["frac_of_base_errors_from_topical"], tc["base_wrong"])))

    oks.append(check(
        "W3 EXTRACTION is NOT the loss point: main-verb recall > 0.9 and goal-marker recall > 0.85 (the parse delivers what the check needs)",
        ef["q_verb_recall"] > 0.9 and ef["goal_marker_on_gold_recall"] > 0.85,
        "q-verb %.2f / goal-marker %.2f / goal-object-bound-in-q %.2f (the 'object not in q' is the multi-step phenomenon)" % (
            ef["q_verb_recall"], ef["goal_marker_on_gold_recall"], ef["goal_object_bound_in_q_recall"])))

    reached = tf.get("DIRECT", 0) + tf.get("SINGLE_STEP", 0) + tf.get("TWO_HOP", 0)
    oks.append(check(
        "W4 the EXACT generation residual: DEEP_MULTISTEP (goal->action plans beyond 2 hops) is the LARGEST single tier and our mechanisms reach < 55% of goal means-ends",
        tf.get("DEEP_MULTISTEP", 0) > 0.4 and reached < 0.55
        and tf.get("DEEP_MULTISTEP", 0) >= max(tf.get("DIRECT", 0), tf.get("TWO_HOP", 0)),
        "DIRECT %.2f + SINGLE_STEP %.2f + TWO_HOP %.2f = %.2f reached; DEEP_MULTISTEP %.2f (the residual)" % (
            tf.get("DIRECT", 0), tf.get("SINGLE_STEP", 0), tf.get("TWO_HOP", 0), reached, tf.get("DEEP_MULTISTEP", 0))))

    oks.append(check(
        "W5 the tiers PARTITION the GOAL subset (a complete, orthogonal decomposition of the means-end coverage)",
        abs(sum(tf.values()) - 1.0) < 0.02,
        "sum of tier fractions = %.3f" % sum(tf.values())))

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
