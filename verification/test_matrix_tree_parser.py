"""Witness -- the globally-normalized graded parser: exactness (brute-force self-test) + attachment + marginal.

problem: replace_the_greedy_arc_eager_with_a_globally_normalized_graded_parser_with_marginals (core).

Run: .venv/Scripts/python.exe verification/test_matrix_tree_parser.py
"""
from __future__ import annotations
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments import exp_matrix_tree_parser_v1 as MT


def check(name, cond, detail=""):
    print("[%s] %s: %s" % ("PASS" if cond else "FAIL", name, detail))
    return bool(cond)


def main():
    oks = []
    try:
        MT.self_test()
        oks.append(check("W0 EXACTNESS: Matrix-Tree marginals + Z + CLE MAP + 2nd-best == brute-force enumeration (n<=4, 200 trials, 3 temps)", True))
    except AssertionError as e:
        oks.append(check("W0 EXACTNESS (brute-force self-test)", False, str(e)))

    o = MT.run(smoke=True)
    at = o["attachment"]; mc = o["marginal_confidence"]

    oks.append(check("W1 the EXACT MST decode beats the greedy heuristic decode over the SAME arc-factored scores (bar 2a)",
                     at["mst_decode_uas"] >= at["greedy_decode_uas"] and at["mst_minus_greedy"] > 0,
                     "greedy %.4f -> MST %.4f (delta %+.4f CI %s)" % (at["greedy_decode_uas"], at["mst_decode_uas"], at["mst_minus_greedy"], at["ci"])))
    oks.append(check("W2 the greedy decode leaves INVALID (non-tree) parses the exact decode never does",
                     at["greedy_decode_left_invalid_tree_sents"] > 0 and at["mst_fixes_greedy_error"] > 0,
                     "greedy invalid-tree sents=%d; MST fixes %d greedy errors (breaks %d)"
                     % (at["greedy_decode_left_invalid_tree_sents"], at["mst_fixes_greedy_error"], at["mst_breaks_greedy_correct"])))
    oks.append(check("W3 the exact marginal is a STRONG graded confidence (right-vs-wrong AUC >> the arc-eager raw conf 0.50-0.62)",
                     mc["marginal_auc_on_greedy_pick"] > 0.75,
                     "marginal AUC %.4f (greedy margin %.4f); best_temp=%s" % (mc["marginal_auc_on_greedy_pick"], mc["greedy_margin_auc_on_greedy_pick"], mc["best_temp"])))
    oks.append(check("W4 the search-failure is STRUCTURALLY eliminated: gold ALWAYS in the marginal support (vs arc-eager beam 0.492)",
                     mc["gold_in_marginal_support_frac"] > 0.999,
                     "gold_in_support=%.4f" % mc["gold_in_marginal_support_frac"]))

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
