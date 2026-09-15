"""Witness -- the downstream LIVE patient lift + twin + the located absolute-recovery negative + calibrator gain.

problem: replace_the_greedy_arc_eager_with_a_globally_normalized_graded_parser_with_marginals (downstream).

Run: .venv/Scripts/python.exe verification/test_matrix_tree_patient_lift.py
"""
from __future__ import annotations
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments import exp_matrix_tree_patient_lift_v1 as PL


def check(name, cond, detail=""):
    print("[%s] %s: %s" % ("PASS" if cond else "FAIL", name, detail))
    return bool(cond)


def main():
    oks = []
    o = PL.run(smoke=True)
    q1 = o["Q1_sensitivity_auc"]; q2 = o["Q2_reliability"]; q3 = o["Q3_absolute_recovery"]; q4 = o["Q4_calibrator_augmentation"]

    oks.append(check("W1 Q1 the RAW Matrix-Tree marginal is a stronger patient-arc reliability signal than the RAW arc-eager conf",
                     q1["matrix_tree_marginal_RAW"] > q1["arceager_arc_conf_RAW"],
                     "marginal RAW AUC %.4f vs arc-eager conf RAW %.4f (calibrated logistic %.4f; twin %.4f)"
                     % (q1["matrix_tree_marginal_RAW"], q1["arceager_arc_conf_RAW"], q1["landed_calibrated_logistic"], q1["shuffled_twin"])))
    oks.append(check("W2 Q2 DEFERRING the live patient read on the marginal lifts accuracy-on-answered, CI-separated (bar 3)",
                     q2["selective@50_marginal"]["ci_separated"] or q2["defer@tau_marginal"]["ci_separated"],
                     "selective@50 %s->%s (delta %s CI %s); defer@tau delta %s"
                     % (q2["blanket"], q2["selective@50_marginal"]["sel"], q2["selective@50_marginal"]["delta"],
                        q2["selective@50_marginal"]["ci"], q2["defer@tau_marginal"]["delta"])))
    oks.append(check("W3 Q2 the SHUFFLED-marginal info-free twin LOSES (flat) -- the marginal is load-bearing (bar 4)",
                     q2["selective@50_twin"]["ci"][0] <= 0 and q2["defer@tau_twin"]["delta"] <= 0.02,
                     "twin selective delta %s CI %s; twin defer delta %s"
                     % (q2["selective@50_twin"]["delta"], q2["selective@50_twin"]["ci"], q2["defer@tau_twin"]["delta"])))
    oks.append(check("W4 Q3 LOCATED NEGATIVE: absolute 2nd-best/MST fall-back does NOT beat blanket (the arc-factored SCORER under-separates, not the decode)",
                     not q3["recover_via_MST_patient"]["ci_separated"] and not q3["recover_via_2ndbest_patient"]["ci_separated"]
                     and q3["marginal_argmax_patient_solo"]["delta"] < 0,
                     "MST-recover delta %s; 2ndbest delta %s; margpick-solo %s (blanket %s); oracle headroom %s"
                     % (q3["recover_via_MST_patient"]["delta"], q3["recover_via_2ndbest_patient"]["delta"],
                        q3["marginal_argmax_patient_solo"]["delta"], q3["blanket"], q3["recover_oracle_bestof3"]["delta"])))
    oks.append(check("W5 Q4 adding the exact marginal to the calibrator does not REDUCE its sensitivity (augmentation >= base refit)",
                     q4["augmented_9feat_auc"] >= q4["base_8feat_refit_auc"] - 1e-9,
                     "base refit AUC %.4f -> +marginal %.4f (gain %+.4f)"
                     % (q4["base_8feat_refit_auc"], q4["augmented_9feat_auc"], q4["auc_gain_from_marginal"])))

    n = sum(oks)
    print("=" * 80)
    print("%s (%d/%d)" % ("ALL CHECKS PASS" if n == len(oks) else "SOME CHECKS FAILED", n, len(oks)))
    print("=" * 80)
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
