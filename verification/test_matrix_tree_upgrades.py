"""Witness -- the brain-foundational upgrades the globally-normalized parser unlocks:
(C) Hale (2001) parse entropy as a graded difficulty signal (greedy 1-best has entropy 0 -> cannot give it);
(D) the marginal as a UNIVERSAL attachment-reliability signal across every head-driven label.

problem: replace_the_greedy_arc_eager_with_a_globally_normalized_graded_parser_with_marginals (upgrades).

Run: .venv/Scripts/python.exe verification/test_matrix_tree_upgrades.py
"""
from __future__ import annotations
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments import exp_matrix_tree_upgrades_v1 as U


def check(name, cond, detail=""):
    print("[%s] %s: %s" % ("PASS" if cond else "FAIL", name, detail))
    return bool(cond)


def main():
    oks = []
    o = U.run(smoke=True)
    c = o["C_hale_parse_entropy"]; d = o["D_universal_attachment_reliability"]["per_label_marginal_auc"]
    dfr = c["sentence_defer_drop_hardest_quartile"]
    buckets = c["difficulty_buckets"]
    errs = [b["arc_error_rate"] for b in buckets]

    oks.append(check("W1 (C) parse ENTROPY predicts sentence difficulty (Spearman entropy-vs-error > 0.4; greedy 1-best has entropy 0)",
                     c["spearman_sentence_entropy_vs_error"] > 0.4 and c["greedy_per_token_entropy"] == 0.0,
                     "spearman=%.4f; entropy-quartile error rates=%s" % (c["spearman_sentence_entropy_vs_error"], errs)))
    oks.append(check("W2 (C) error rate rises MONOTONICALLY across entropy quartiles (a genuine difficulty curve)",
                     all(errs[i] <= errs[i + 1] + 1e-9 for i in range(len(errs) - 1)),
                     "%s" % errs))
    oks.append(check("W3 (C) deferring on the hardest-entropy sentences lifts accuracy on the rest; random-entropy twin flat",
                     dfr["delta"] > 0.01 and dfr["twin_delta"] < dfr["delta"] / 2.0,
                     "blanket %.4f -> kept75 %.4f (delta %+.4f); twin delta %+.4f" % (dfr["blanket_arc_acc"], dfr["kept75_acc"], dfr["delta"], dfr["twin_delta"])))
    med = sorted(v["marginal_auc"] for v in d.values())[len(d) // 2]
    strong = sum(1 for v in d.values() if v["marginal_auc"] > 0.7)
    oks.append(check("W4 (D) the marginal is a UNIVERSAL attachment-reliability signal (median per-label AUC > 0.7, strong on the core labels)",
                     med > 0.7 and d.get("nsubj", {}).get("marginal_auc", 0) > 0.7 and d.get("obj", {}).get("marginal_auc", 0) > 0.7,
                     "median AUC %.3f over %d labels (%d with AUC>0.7); nsubj %.3f obj %.3f obl %.3f"
                     % (med, len(d), strong, d.get("nsubj", {}).get("marginal_auc", 0), d.get("obj", {}).get("marginal_auc", 0), d.get("obl", {}).get("marginal_auc", 0))))

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
