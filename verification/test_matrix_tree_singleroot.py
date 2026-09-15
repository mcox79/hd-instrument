"""Witness -- the grammar-faithful SINGLE-ROOT Matrix-Tree marginals (Koo 2007): exact vs brute force, and at
parity-or-better than multi-root on the live reliability signal.

problem: replace_the_greedy_arc_eager_with_a_globally_normalized_graded_parser_with_marginals (fidelity upgrade).

Run: .venv/Scripts/python.exe verification/test_matrix_tree_singleroot.py
"""
from __future__ import annotations
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments import exp_matrix_tree_singleroot_v1 as SR


def check(name, cond, detail=""):
    print("[%s] %s: %s" % ("PASS" if cond else "FAIL", name, detail))
    return bool(cond)


def main():
    oks = []
    try:
        SR.self_test()
        oks.append(check("W0 EXACTNESS: single-root Matrix-Tree marginals == brute-force SINGLE-ROOT enumeration (n<=4, 3 temps)", True))
    except AssertionError as e:
        oks.append(check("W0 EXACTNESS (single-root brute force)", False, str(e)))

    o = SR.run(smoke=True)
    p = o["patient"]; b = o["obl"]
    oks.append(check("W1 single-root (grammar-faithful) reliability is at PARITY-OR-BETTER than multi-root on patient arcs",
                     p["singleroot_auc"] >= p["multiroot_auc"] - 0.005,
                     "patient single-root AUC %.4f vs multi-root %.4f (n=%d)" % (p["singleroot_auc"], p["multiroot_auc"], p["n"])))
    oks.append(check("W2 single-root reliability is at PARITY-OR-BETTER than multi-root on obl attachment arcs",
                     b["singleroot_auc"] >= b["multiroot_auc"] - 0.005,
                     "obl single-root AUC %.4f vs multi-root %.4f (n=%d)" % (b["singleroot_auc"], b["multiroot_auc"], b["n"])))

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
