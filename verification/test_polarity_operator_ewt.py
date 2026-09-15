"""Scaffold-free witness: the NEGATION operator READER-NATIVE on modern UD-EWT gold (the HEADLINE).

  E1 net factuality accuracy beats the POLARITY-BLIND floor CI-separated (doc-level bootstrap) -- reader-native
     over the live SituationReader's sm.events (align_fail small).
  E2 the operator RECOVERS negations the blind floor gets ZERO of (negated-recall >> 0), AND affirmative
     regression (over-negation) is <= 0.02 on CLEAN affirmatives -- BEATING the prior negation_factuality_gate
     which stalled at MIDDLE_BAND (regression 0.0303) on this same gold. The clause-bounded / implicative-gated
     scope is what removes the over-propagation.
  E3 the info-free shuffled-cue TWIN loses (beats null p95).

Requires data/gold_negation_factuality_ewt_v1 (on disk).
Re-derives live from experiments.exp_polarity_operator_ewt_v1 (runs the SituationReader).
Run: .venv/Scripts/python.exe verification/test_polarity_operator_ewt.py
"""
import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments.exp_polarity_operator_ewt_v1 import run, GOLD_PATH

PASS = FAIL = 0


def chk(name, cond, detail=""):
    global PASS, FAIL
    ok = bool(cond)
    print(("  PASS " if ok else "  FAIL ") + name + ("" if not detail else "  [%s]" % detail), flush=True)
    PASS += int(ok); FAIL += int(not ok)
    return ok


def main():
    if not os.path.exists(GOLD_PATH):
        print("  SKIP: EWT negation gold not on disk", flush=True)
        return 0
    out = run()
    chk("E1 net accuracy beats the polarity-blind floor CI-sep (reader-native sm.events)",
        out["operator_minus_blind"]["ci_sep"] and out["net_accuracy"]["operator_full"] > 0.85,
        "net op %.4f vs blind %.4f (+%.4f CI%s) align_fail=%d" % (
            out["net_accuracy"]["operator_full"], out["net_accuracy"]["blind_floor"],
            out["operator_minus_blind"]["delta"], out["operator_minus_blind"]["ci"], out["align_fail"]))
    chk("E2 recovers negations (recall>0.80) with CLEAN over-negation <= 0.02 (beats prior MIDDLE_BAND 0.0303)",
        out["negated_recall"]["operator_full"] > 0.80 and out["negated_recall"]["blind_floor"] == 0.0
        and out["affirmative_regression"]["operator_full_clean"] <= 0.02,
        "neg-recall %.4f vs blind %.4f | regression clean %.4f all %.4f" % (
            out["negated_recall"]["operator_full"], out["negated_recall"]["blind_floor"],
            out["affirmative_regression"]["operator_full_clean"], out["affirmative_regression"]["operator_full_all"]))
    chk("E3 info-free shuffled-cue twin loses (beats null p95)",
        out["operator_minus_twin"]["beats_twin"],
        "op-twin +%.4f > null_p95 %.4f" % (out["operator_minus_twin"]["delta"], out["operator_minus_twin"]["null_p95"]))
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
