"""Scaffold-free witness for the brain-fidelity DELTA prototypes (exp_coref_faithful_integrator_deltas_v1).

Asserts the load-bearing, can-fail claims of the "how does our ideal differ from the brain, and can we close the
deltas" analysis:
  W1  self-test (the conditional-logit reranker learns a discriminative feature) passes.
  W2  DELTA 1 -- SELF-SUPERVISED (label-free, cue-agreement pseudo-labels) recovers essentially the SAME
      point-estimate gain as GOLD-supervised (|self_sup - gold| < 0.02, both > 0.03) -> the organ is learnable
      WITHOUT gold antecedents (the brain-faithful requirement; the North Star's core).
  W3  DELTA 2 -- DEFER: the learned posterior's entropy predicts its own errors (AUC > 0.70) and deferring the
      ambiguous 34% raises kept accuracy well above a random-defer twin (>+0.05) -> the brain's Nref/defer is
      realizable (unlike the graded pick's 99.5%-confident wrong picks).
  W4  DELTA 3 + DELTA 4/7 -- HONEST NEGATIVES: the recurrent (integrator-in-the-loop) feedback does NOT beat the
      static one-shot (band != ABOVE), and the multiplicative+interference features do NOT beat the plain gold
      integrator -- both are brain-real but not realizable-useful at the coarse representation / current coref
      quality (gated behind p1 + better coref = the North Star).

Deterministic; reads the who-did-what cache; ~60-90s. ASCII only.
"""
import os
import sys

os.environ.setdefault("PYTHONIOENCODING", "utf-8")
_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import experiments.exp_coref_faithful_integrator_deltas_v1 as F


def main():
    checks = []
    try:
        F.self_test()
        checks.append(("W1 self-test (conditional-logit reranker learns a discriminative feature)", True, "pass"))
    except Exception as e:  # noqa
        checks.append(("W1 self-test", False, "raised %r" % e))
        return _report(checks)

    out = F.cell(docs=None)
    gold = out["DELTA1_gold_supervised"]
    ss = out["DELTA1_self_supervised_label_free"]
    df = out["DELTA2_defer"]
    ru, rg = out["DELTA3_recurrent_ungated"], out["DELTA3_recurrent_conf_gated"]
    it = out["DELTA4_7_multiplicative_plus_interference"]

    w2 = gold["delta"] > 0.03 and ss["delta"] > 0.03 and abs(ss["delta"] - gold["delta"]) < 0.02
    checks.append(("W2 DELTA1 self-supervised (label-free) ~= gold-supervised (learnable WITHOUT gold)", bool(w2),
                   "gold +%.4f %s | self-sup +%.4f %s (n_pseudo=%d)"
                   % (gold["delta"], gold["band"], ss["delta"], ss["band"], ss["n_pseudo"])))

    w3 = (df["entropy_auc"] or 0) > 0.70 and (df["kept_acc_defer_34pct"] - df["kept_acc_random_defer_34pct"]) > 0.05
    checks.append(("W3 DELTA2 defer realizable: calibrated posterior (AUC>0.70), deferral >> random-defer", bool(w3),
                   "AUC=%.3f kept-defer=%.4f random-defer=%.4f full=%.4f"
                   % (df["entropy_auc"], df["kept_acc_defer_34pct"], df["kept_acc_random_defer_34pct"], df["full_acc"])))

    w4 = (ru["band"] != "ABOVE") and (rg["band"] != "ABOVE") and (it["delta"] <= gold["delta"] + 0.005)
    checks.append(("W4 DELTA3 recurrent + DELTA4/7 multiplicative/interference are HONEST NEGATIVES at our representation", bool(w4),
                   "recur ungated +%.4f %s / gated +%.4f %s | +interference +%.4f (gold +%.4f)"
                   % (ru["delta"], ru["band"], rg["delta"], rg["band"], it["delta"], gold["delta"])))

    return _report(checks)


def _report(checks):
    npass = sum(1 for _, ok, _ in checks if ok)
    print("\n==== WITNESS: %d/%d ====" % (npass, len(checks)))
    for name, ok, detail in checks:
        print("  [%s] %s -- %s" % ("PASS" if ok else "FAIL", name, detail))
    return 0 if npass == len(checks) else 1


if __name__ == "__main__":
    sys.exit(main())


# --- pytest-collectable wrapper (pri 128, mechanical; see notes/problems/447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest/PROBLEM.md) ---
import pytest as _pri128_pytest
from verification._witness_wrap import _run_main_as_test as _pri128_run


@_pri128_pytest.mark.fast
def test_witness():
    _code, _out = _pri128_run(main)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
