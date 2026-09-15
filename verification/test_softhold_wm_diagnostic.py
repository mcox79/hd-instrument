"""Scaffold-free witness: WHY the last two optimizations behaved as they did (understood to mechanism).

  D1  SOFT-HOLD (confidence-gated / graded Nref writeback) is net-negative because low-margin ("ambiguous") pronoun
      picks STILL carry real signal (accuracy well above multi-way chance) -> gating/holding them discards good
      salience; HARD COMMIT wins (Garrod & Sanford bonding; "attractors settle" -- confirms the prior LitBank finding
      on modern GUM). Not a fidelity gap: soft-hold is the wrong mechanism for running-discourse reference.
  D2  the WORKING-MEMORY bound k=4 is marginal because the ACT-R base-level activation IS the (graded) working-memory
      limit (Lewis & Vasishth 2005 cue-based retrieval = ACT-R): the correct antecedent is within the 4 most-recent
      referents ~92% of the time and the ACT-R pick already lies in the recency-top-4 ~99.9% -> a hard discrete-slot
      bound is REDUNDANT with the activation decay.

Reads data/exp_softhold_wm_diagnostic_gum_v1/metrics_full.json.
Run: .venv/Scripts/python.exe verification/test_softhold_wm_diagnostic.py
"""
import json
import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
M = os.path.join(_REPO, "data", "exp_softhold_wm_diagnostic_gum_v1", "metrics_full.json")
PASS = FAIL = 0


def chk(name, cond, detail=""):
    global PASS, FAIL
    ok = bool(cond)
    print(("  PASS " if ok else "  FAIL ") + name + ("" if not detail else "  [%s]" % detail), flush=True)
    PASS += int(ok); FAIL += int(not ok)
    return ok


def main():
    r = json.load(open(M))["result"]
    sh, wm = r["softhold"], r["wm"]
    chk("D1 low-margin (would-be-gated) picks carry real signal (well above multi-way chance) -> soft-hold discards it",
        sh["low_margin_acc"] > 0.25 and sh["low_margin_n"] > 200,
        "low-margin acc %.3f (n=%d) vs high-margin %.3f (n=%d)" % (
            sh["low_margin_acc"], sh["low_margin_n"], sh["high_margin_acc"], sh["high_margin_n"]))
    chk("D2 ACT-R activation IS the working-memory limit -> a hard k=4 bound is redundant with the decay",
        wm["correct_antecedent_within_recency_top4"] > 0.85 and wm["actr_pick_within_recency_top4"] > 0.98,
        "correct antecedent within recency-top-4 %.3f | ACT-R pick within recency-top-4 %.3f" % (
            wm["correct_antecedent_within_recency_top4"], wm["actr_pick_within_recency_top4"]))
    print("\n%d/%d checks passed" % (PASS, PASS + FAIL), flush=True)
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(main())


# --- pytest-collectable wrapper (pri 128, mechanical; see notes/problems/447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest/PROBLEM.md) ---
import pytest as _pri128_pytest
from verification._witness_wrap import _run_main_as_test as _pri128_run


@_pri128_pytest.mark.corpus
def test_witness():
    _code, _out = _pri128_run(main)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
