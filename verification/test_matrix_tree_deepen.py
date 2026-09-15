"""Witness -- the deepening drills: (A) the absolute-recovery wall is genuine two-valid ambiguity (not the parser),
and (B) the Matrix-Tree marginal EXCELS on the obl/spatial attachment reader (beats the landed obl calibrator).

problem: replace_the_greedy_arc_eager_with_a_globally_normalized_graded_parser_with_marginals (deepening).

Run: .venv/Scripts/python.exe verification/test_matrix_tree_deepen.py
"""
from __future__ import annotations
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments import exp_matrix_tree_deepen_v1 as D


def check(name, cond, detail=""):
    print("[%s] %s: %s" % ("PASS" if cond else "FAIL", name, detail))
    return bool(cond)


def main():
    oks = []
    o = D.run(smoke=True)
    a = o["A_wrong_pick_decomposition"]; b = o["B_obl_attachment_reader"]
    cl = a["classes"]; tot = max(sum(cl.values()), 1)

    oks.append(check("W1 (A) the ABSOLUTE-recovery wall is DOMINATED by genuine two-valid ambiguity (not a parser fix)",
                     cl["TWO_VALID_ambiguous"] > cl["BURIED_scorer"] and cl["TWO_VALID_ambiguous"] / tot > 0.4,
                     "TWO_VALID=%d (%.0f%%) vs BURIED=%d, RANKABLE=%d of %d wrong picks"
                     % (cl["TWO_VALID_ambiguous"], 100 * cl["TWO_VALID_ambiguous"] / tot, cl["BURIED_scorer"], cl["RANKABLE_2ndbest"], a["n_wrong"])))
    oks.append(check("W2 (B) the RAW Matrix-Tree marginal BEATS the landed obl-calibrated logistic on right-vs-wrong AUC",
                     b["auc"]["matrix_tree_marginal"] > b["auc"]["landed_obl_calibrated"]
                     and b["auc"]["matrix_tree_marginal"] > b["auc"]["raw_a2_margin"],
                     "marginal %.4f vs obl-calibrated %.4f vs raw-a2 %.4f" % (b["auc"]["matrix_tree_marginal"], b["auc"]["landed_obl_calibrated"], b["auc"]["raw_a2_margin"])))
    oks.append(check("W3 (B) deferring the live obl attachment on the marginal lifts selective accuracy CI-sep, twin flat",
                     b["selective@50_marginal"]["ci_separated"] and b["selective@50_twin"]["ci"][0] <= 0,
                     "selective %s->%s (delta %s CI %s); twin delta %s"
                     % (b["blanket_attach_acc"], b["selective@50_marginal"]["sel"], b["selective@50_marginal"]["delta"],
                        b["selective@50_marginal"]["ci"], b["selective@50_twin"]["delta"])))
    oks.append(check("W4 (B) adding the marginal to the obl calibrator RAISES its sensitivity (a genuine upgrade)",
                     b["calibrator_aug"]["gain"] > 0,
                     "obl calibrator %.4f -> +marginal %.4f (gain %+.4f)"
                     % (b["calibrator_aug"]["base_refit_auc"], b["calibrator_aug"]["augmented_auc"], b["calibrator_aug"]["gain"])))

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
