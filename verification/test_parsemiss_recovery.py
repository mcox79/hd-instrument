"""Witness -- parse-miss recovery: on the slice where the greedy parser NEVER attached the gold patient to the verb
(greedy floor 0 by definition), the exact edge MARGINAL exposes the gold as a top-2 head of the verb the large
majority of the time (twin losing) -> the graded parser structurally eliminates the search failure even on the
hardest slice. The exact 2nd-best TREE is a weak lever here (honest: the marginal, not the 2nd-best tree, is the
exposure mechanism); the remaining gap is SELECTION among exposed candidates.

problem: replace_the_greedy_arc_eager_with_a_globally_normalized_graded_parser_with_marginals (parse-miss recovery).
Run: .venv/Scripts/python.exe verification/test_parsemiss_recovery.py
"""
from __future__ import annotations
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
import sys
_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
from experiments import exp_parsemiss_recovery_v1 as PM


def check(name, cond, detail=""):
    print("[%s] %s: %s" % ("PASS" if cond else "FAIL", name, detail))
    return bool(cond)


def main():
    oks = []
    o = PM.run(smoke=True)
    r = o["recovery"]

    oks.append(check("W1 on the PARSE-MISS slice (greedy floor 0) the exact MARGINAL exposes gold as a top-2 head of v for the majority",
                     r["marginal_top2_head_is_v"]["frac"] > 0.5,
                     "marginal top2 exposure %.3f (top1 %.3f); greedy floor %s" % (r["marginal_top2_head_is_v"]["frac"], r["marginal_top1_head_is_v"]["frac"], o["greedy_floor_recovery"])))
    oks.append(check("W2 the SHUFFLED-marginal twin does NOT recover -> the exposure is the real posterior, not 'any alternative'",
                     r["twin_shuffled_marginal"]["frac"] < 0.15,
                     "twin recovery %.3f" % r["twin_shuffled_marginal"]["frac"]))
    oks.append(check("W3 ANY graded-parser mechanism recovers the gold on the majority of the parse-miss slice",
                     r["ANY_mechanism"]["frac"] > 0.5,
                     "ANY %.3f (2nd-best-tree %.3f, valency-sat %.3f)" % (r["ANY_mechanism"]["frac"], r["exact_2nd_best_tree_reanalysis"]["frac"], r["valency_saturation_fill"]["frac"])))
    oks.append(check("W4 HONEST: the exact 2nd-best TREE is a WEAK exposure lever here (the marginal is the mechanism, not the 2nd-best tree)",
                     r["exact_2nd_best_tree_reanalysis"]["frac"] < r["marginal_top2_head_is_v"]["frac"],
                     "2nd-best-tree %.3f << marginal-top2 %.3f" % (r["exact_2nd_best_tree_reanalysis"]["frac"], r["marginal_top2_head_is_v"]["frac"])))

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
