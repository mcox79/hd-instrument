"""Scaffold-free witness: the CONTEXTUAL goal-attachment mechanism generalizes to MODERN GENERAL TEXT,
closing the 19c-LitBank validation's two gaps (power + the corpus-age confound). UD-EWT is modern +
gold-parsed, so the genuine-purpose set is the GOLD advcl label (no parser/spaCy noise), and there are
~800 items (vs 80 in LitBank).

  W1  hundreds of modern gold-advcl purpose items (powered, vs 80 in 19c LitBank)
  W2  the CONTEXTUAL mechanism (simple situation-relatedness, v1) BEATS the info-free shuffled-situation
      twin CI-separated on modern general text -- BOTH K1 and K3 -- on GOLD-clean genuine purposes
  W3  honest located negative: the IDF+attention "optimization" does NOT improve over the simple v1
      mechanism (the simple situation-relatedness is already near-optimal)

Reads data/exp_contextual_goal_attachment_modern_v1/metrics_full.json.
Run: .venv/Scripts/python.exe verification/test_contextual_goal_attachment_modern.py
"""
import json
import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
METRICS = os.path.join(_REPO, "data", "exp_contextual_goal_attachment_modern_v1", "metrics_full.json")
PASS = FAIL = 0


def chk(name, cond, detail=""):
    global PASS, FAIL
    ok = bool(cond)
    print(("  PASS " if ok else "  FAIL ") + name + ("" if not detail else "  [%s]" % detail), flush=True)
    PASS += int(ok); FAIL += int(not ok)
    return ok


def main():
    r = json.load(open(METRICS))["result"]
    chk("W1 powered: hundreds of modern GOLD-advcl purpose items (vs 80 in 19c LitBank)",
        r["n_items"] >= 300, "n_items=%d, distinct purposes=%d" % (r["n_items"], r["n_distinct_purposes"]))
    for K in ("K1", "K3"):
        x = r[K]; b = x["BASELINE_v1"]
        chk("W2 CONTEXTUAL (v1 situation-relatedness) beats the info-free twin CI-separated on modern text (%s)" % K,
            x["base_beats_twin_ci"] and b["ci"][0] > x["twin_null"]["p95"],
            "mech %.3f ci_lo %.3f vs twin p95 %.3f (chance %.2f)" % (b["acc"], b["ci"][0], x["twin_null"]["p95"], x["chance"]))
    k3 = r["K3"]
    chk("W3 located negative: IDF+attention does NOT beat the simple v1 mechanism (simple is near-optimal)",
        k3["OPTIMIZED"]["acc"] <= k3["BASELINE_v1"]["acc"] + 0.01,
        "opt %.3f vs simple %.3f (%+.3f)" % (k3["OPTIMIZED"]["acc"], k3["BASELINE_v1"]["acc"], k3["opt_over_baseline"]))
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
