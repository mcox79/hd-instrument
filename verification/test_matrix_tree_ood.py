"""Witness -- the marginal's reliability GENERALIZES out-of-distribution (QA-SRL), attenuated but CI-separated.

problem: replace_the_greedy_arc_eager_with_a_globally_normalized_graded_parser_with_marginals (OOD generalization).

Run: .venv/Scripts/python.exe verification/test_matrix_tree_ood.py
"""
from __future__ import annotations
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments import exp_matrix_tree_ood_v1 as O


def check(name, cond, detail=""):
    print("[%s] %s: %s" % ("PASS" if cond else "FAIL", name, detail))
    return bool(cond)


def main():
    oks = []
    o = O.run(smoke=True)
    sm = o["selective@50_marginal"]; tw = o["selective@50_twin"]

    oks.append(check("W1 OOD (QA-SRL): the marginal carries right-vs-wrong signal above chance (twin at chance)",
                     o["marginal_auc_right_vs_wrong"] > 0.52 and abs(o["twin_auc"] - 0.5) < 0.03,
                     "marginal AUC %.4f vs twin %.4f (blanket %.4f, n=%d)" % (o["marginal_auc_right_vs_wrong"], o["twin_auc"], o["blanket_patient_acc"], o["n"])))
    oks.append(check("W2 OOD: deferring on the marginal lifts selective patient accuracy CI-separated (generalizes)",
                     sm["ci_separated"],
                     "selective %.4f->%.4f (delta %s CI %s)" % (o["blanket_patient_acc"], sm["sel"], sm["delta"], sm["ci"])))
    oks.append(check("W3 OOD: the shuffled-marginal info-free twin is FLAT (the OOD lift is the marginal, not abstain-helps)",
                     tw["ci"][0] <= 0,
                     "twin delta %s CI %s" % (tw["delta"], tw["ci"])))

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
