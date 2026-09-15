"""Witness -- AUDIT THE RULER: string-identity's strength is NOT a metric artifact. It beats every glass-box splitter
on BOTH the board's dominant-eid metric AND the field-standard CoNLL (MUC/B3/CEAFe), which DOES penalize over-merge.
problem: improve_the_common_noun_coref_candidate_quality_the_resolver_trails_string_identity
Run: .venv/Scripts/python.exe verification/test_commonnoun_metric_audit.py
"""
from __future__ import annotations
import os, sys
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
from experiments import exp_commonnoun_metric_audit_gum_v1 as M
from experiments.exp_commonnoun_clustering_probe_gum_v1 import (
    a_string_identity, make_recency_gap, a_modifier_split, make_combo)


def check(name, cond, detail=""):
    print("[%s] %s: %s" % ("PASS" if cond else "FAIL", name, detail))
    return bool(cond)


def main():
    dev, test = M._load(None)
    rules = {"string_identity": a_string_identity, "recency_gap_W40": make_recency_gap(40),
             "modifier_split": a_modifier_split, "combo_W40": make_combo(40, 1.0)}
    sc = {k: M.eval_all(test, fn)[0] for k, fn in rules.items()}
    si = sc["string_identity"]
    oks = []
    oks.append(check("W1 string-identity is strong on the field-standard CoNLL metric (not just the board's dominant-eid)",
                     si["conll_avg"] > 0.70,
                     "string_id CoNLL=%.4f (MUC=%.4f B3=%.4f CEAFe=%.4f)" % (
                         si["conll_avg"], si["muc_f1"], si["b3_f1"], si["ceafe_f1"])))
    oks.append(check("W2 NO splitter beats string-identity on CoNLL -> the over-merge string-identity commits is small on modern GUM; splitting is not a metric artifact",
                     all(sc[k]["conll_avg"] <= si["conll_avg"] for k in ("recency_gap_W40", "modifier_split", "combo_W40")),
                     "CoNLL: recency=%.4f modifier=%.4f combo=%.4f vs string_id=%.4f" % (
                         sc["recency_gap_W40"]["conll_avg"], sc["modifier_split"]["conll_avg"],
                         sc["combo_W40"]["conll_avg"], si["conll_avg"])))
    oks.append(check("W3 NO splitter beats string-identity on the board's dominant-eid metric either",
                     all(sc[k]["dominant_eid_acc"] <= si["dominant_eid_acc"] for k in
                         ("recency_gap_W40", "modifier_split", "combo_W40")),
                     "dominant-eid: recency=%.4f modifier=%.4f combo=%.4f vs string_id=%.4f" % (
                         sc["recency_gap_W40"]["dominant_eid_acc"], sc["modifier_split"]["dominant_eid_acc"],
                         sc["combo_W40"]["dominant_eid_acc"], si["dominant_eid_acc"])))
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


@_pri128_pytest.mark.corpus
def test_witness():
    _code, _out = _pri128_run(main)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
