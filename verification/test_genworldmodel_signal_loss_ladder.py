"""Witness -- the BRAIN-FOUNDATIONAL FIDELITY SCAN / signal-loss ladder: an oracle ladder that grants each
stage its perfect version localizes WHERE the generative-result-state chain loses signal on modern TellMeWhy
non-adjacent. Extraction is NOT the bottleneck (0.98 recall on this clean gold); the dominant loss is the
FORWARD MODEL depth -- a perfect GOAL simulator (that bridges the MULTI-STEP plans the single-step rollout
cannot) would add ~+0.15, ~10x what our current surface means-end recovers; a second loss is
SELECTION/competition (a correct boost is overridden by base plausibility ~25% of the time).

problem: build_the_generative_result_state_world_model
Run: .venv/Scripts/python.exe verification/test_genworldmodel_signal_loss_ladder.py
"""
from __future__ import annotations
import os, sys
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
from experiments import exp_genworldmodel_signal_loss_ladder_v1 as L


def check(name, cond, detail=""):
    print("[%s] %s: %s" % ("PASS" if cond else "FAIL", name, detail))
    return bool(cond)


def main():
    o = L.run(n=1500)
    lad = o["overall_ladder"]; gap = o["stage_gaps"]; rec = o["stage_recall"]
    oks = []

    oks.append(check(
        "W1 the LADDER is monotone and the dominant recoverable gap is the FORWARD-MODEL depth: a perfect GOAL simulator adds far more than our surface means-end",
        lad["base"] <= lad["surface"] <= lad["oracle_goal"] <= lad["oracle_all"] <= lad["gold"]
        and gap["R2-R1_multistep_and_coverage_LOST"] > 3 * max(gap["R1-R0_surface_recovers"], 0.001),
        "base %.3f -> surface %.3f -> oracle_goal %.3f -> oracle_all %.3f -> gold %.3f | surface +%.3f vs forward-model +%.3f" % (
            lad["base"], lad["surface"], lad["oracle_goal"], lad["oracle_all"], lad["gold"],
            gap["R1-R0_surface_recovers"], gap["R2-R1_multistep_and_coverage_LOST"])))

    oks.append(check(
        "W2 the GOAL means-end is DOMINATED by MULTI-STEP plans (the single-step rollout structurally cannot generate them)",
        rec["meansend_tier_MULTI_STEP"] > 0.5,
        "tiers DIRECT %.2f / SINGLE-STEP %.2f / MULTI-STEP %.2f" % (
            rec["meansend_tier_DIRECT"], rec["meansend_tier_SINGLE_STEP"], rec["meansend_tier_MULTI_STEP"])))

    oks.append(check(
        "W3 EXTRACTION is NOT the bottleneck for this task (high event recall) -- the loss is DOWNSTREAM (forward model + selection), not the upstream parse",
        rec["extraction_q_event_recall"] > 0.9 and rec["extraction_gold_event_recall"] > 0.9,
        "extraction recall q-event %.2f gold-event %.2f | goal-detect %.2f" % (
            rec["extraction_q_event_recall"], rec["extraction_gold_event_recall"], rec["goal_detection_recall_on_gold"])))

    oks.append(check(
        "W4 SELECTION/competition is a real secondary loss: even a CORRECT means-end boost is overridden by base plausibility on the GOAL subset (< 1.0)",
        rec["selection_oracle_goal_acc_on_GOAL"] < 0.9,
        "oracle_goal accuracy on GOAL = %.2f (%.0f%% of correct boosts survive base competition)" % (
            rec["selection_oracle_goal_acc_on_GOAL"], 100 * rec["selection_oracle_goal_acc_on_GOAL"])))

    n = sum(oks)
    print("=" * 90)
    print("%s (%d/%d)" % ("ALL CHECKS PASS" if n == len(oks) else "SOME CHECKS FAILED", n, len(oks)))
    print("=" * 90)
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
