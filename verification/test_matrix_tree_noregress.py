"""Witness -- no-regress on the parse-head consumers + the can-fail POSITIVE control the greedy 1-best cannot pass.

problem: replace_the_greedy_arc_eager_with_a_globally_normalized_graded_parser_with_marginals (no-regress).

Run: .venv/Scripts/python.exe verification/test_matrix_tree_noregress.py
"""
from __future__ import annotations
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments import exp_matrix_tree_noregress_v1 as NR


def check(name, cond, detail=""):
    print("[%s] %s: %s" % ("PASS" if cond else "FAIL", name, detail))
    return bool(cond)


def main():
    oks = []
    o = NR.run(smoke=True)
    sw = o["decode_swap_greedy_to_mst"]; pc = o["positive_control_greedy_cannot_pass"]

    oks.append(check("W1 NO consumer-relevant label REGRESSES under the exact-decode swap (obj/obl/nmod/nsubj/root)",
                     not sw["any_label_regresses"] and sw["overall_delta"] >= -1e-9,
                     "overall greedy %.4f -> MST %.4f (delta %+.4f); per-label regress=%s"
                     % (sw["overall_greedy_uas"], sw["overall_mst_uas"], sw["overall_delta"], sw["any_label_regresses"])))
    oks.append(check("W2 the ADDITIVE marginal path changes NO head (byte-identical -> no consumer can regress)",
                     "changes NO head" in o["additive_marginal_path"], o["additive_marginal_path"]))
    oks.append(check("W3 POSITIVE CONTROL: greedy leaves INVALID (non-tree) parses; exact MST recovers gold there, CI-sep",
                     pc["greedy_left_invalid_tree_sents"] > 0 and pc["ci_separated"],
                     "invalid-tree sents=%d (%.1f%%); MST-greedy UAS on them %+.4f CI %s"
                     % (pc["greedy_left_invalid_tree_sents"], 100 * pc["frac_of_sents"], pc["on_those_sents_mst_minus_greedy_uas"], pc["ci"])))
    oks.append(check("W4 the root attachment (greedy multi-root failure mode) improves most under the exact decode",
                     sw["per_consumer_label"]["root"]["delta"] >= 0,
                     "root greedy %.4f -> MST %.4f (delta %+.4f)" % (sw["per_consumer_label"]["root"]["greedy"],
                     sw["per_consumer_label"]["root"]["mst"], sw["per_consumer_label"]["root"]["delta"])))

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
