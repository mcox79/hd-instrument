"""Scaffold-free witness: the gender bootstrapping wall is FIXED brain-foundationally -- but the prize was
smaller than the ceiling suggested (an honest located result).

  S1  the brain-faithful fix (gender as a VIOLABLE graded cue, Carminati + confidence-gated propagation)
      REMOVES the hard-filter regression: HARD gender = -0.125; soft gender is NON-negative, and the
      random-gender-propagation TWIN does not help (control).
  S2  HONEST: the soft-gender benefit is MARGINAL and NOT CI-separated (~+0.008) -- the +0.28 "ceiling"
      (anatomy) was headroom over a WEAK over-narrowing baseline, not signal the strong recency-dominated
      pick was missing. Gender is now a faithful, non-regressing, marginal component; the deployable lever
      stays PICK (+0.133) + UNIFICATION (+0.020).

Reads data/exp_coref_graded_soft_gender_v1/metrics_full.json.
Run: .venv/Scripts/python.exe verification/test_coref_graded_soft_gender.py
"""
import json
import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SG = os.path.join(_REPO, "data", "exp_coref_graded_soft_gender_v1", "metrics_full.json")
PASS = FAIL = 0


def chk(name, cond, detail=""):
    global PASS, FAIL
    ok = bool(cond)
    print(("  PASS " if ok else "  FAIL ") + name + ("" if not detail else "  [%s]" % detail), flush=True)
    PASS += int(ok); FAIL += int(not ok)
    return ok


def main():
    r = json.load(open(SG))["result"]
    A = r["arms"]; D = r["deltas"]
    best = r["best_soft_arm"]
    hard_d = D["+HARD gender (regression)"]["delta"]
    best_d = D[best]["delta"]
    twin_d = D["+soft_gender TWIN (random gender)"]["delta"]
    chk("S1 soft violable gender cue REMOVES the hard-filter regression; random-gender twin does not help",
        hard_d < -0.05 and best_d >= -0.001 and twin_d <= best_d,
        "HARD %+.4f -> best soft %s %+.4f | random-gender twin %+.4f" % (hard_d, best, best_d, twin_d))
    chk("S2 HONEST: the gender benefit is MARGINAL, not CI-separated (the +0.28 ceiling was over a weak baseline)",
        (not D[best]["CIsep"]) and best_d < 0.03,
        "baseline %.4f -> best soft %.4f (%+.4f, ci %s)" % (r["baseline_glassbox"], A[best]["acc"], best_d, D[best]["ci"]))
    print("\n%d/%d checks passed" % (PASS, PASS + FAIL), flush=True)
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(main())


# --- pytest-collectable wrapper (pri 128, mechanical; see notes/problems/447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest/PROBLEM.md) ---
import pytest as _pri128_pytest
from verification._witness_wrap import _run_main_as_test as _pri128_run


@_pri128_pytest.mark.fast
def test_witness():
    _code, _out = _pri128_run(main)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
