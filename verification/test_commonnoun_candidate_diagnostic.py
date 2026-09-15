"""Witness -- the common-noun coref candidate/ranking DIAGNOSTIC reproduces the board defect EXACTLY and localizes it.
problem: improve_the_common_noun_coref_candidate_quality_the_resolver_trails_string_identity
Run: .venv/Scripts/python.exe verification/test_commonnoun_candidate_diagnostic.py
"""
from __future__ import annotations
import os, sys
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
from experiments import exp_commonnoun_candidate_diagnostic_gum_v1 as D


def check(name, cond, detail=""):
    print("[%s] %s: %s" % ("PASS" if cond else "FAIL", name, detail))
    return bool(cond)


def main():
    o = D.run(n_docs=None)
    a = o["arm_accs_common"]
    oks = []
    oks.append(check("W1 reproduces the board defect: URG unified 0.4879 CI-below string-identity 0.5412 (n=2855)",
                     abs(a["unified"]["acc"] - 0.4879) < 0.01 and abs(a["string_identity"]["acc"] - 0.5412) < 0.01
                     and a["unified_minus_string_identity"]["CIsep_below"] and a["unified"]["n"] == 2855,
                     "unified=%.4f string_id=%.4f delta=%s" % (a["unified"]["acc"], a["string_identity"]["acc"],
                                                               a["unified_minus_string_identity"]["ci"])))
    r = o["reachability"]
    oks.append(check("W2 reachability: ~66% same-head, ~34% different-head only, ~0% unreachable",
                     r["A_reachable_by_head"]["frac"] > 0.6 and r["B_reachable_diff_head"]["frac"] > 0.3
                     and r["C_unreachable"]["n"] == 0,
                     "A=%.3f B=%.3f C=%d" % (r["A_reachable_by_head"]["frac"], r["B_reachable_diff_head"]["frac"],
                                             r["C_unreachable"]["n"])))
    sA = o["slice_A_reachable_by_head"]
    oks.append(check("W3 on same-head slice, string-identity (0.817) BEATS the incumbent (0.736) -> incumbent is self-inflicted, not candidate-starved",
                     sA["string_identity_acc_on_A"] > sA["unified_acc_on_A"],
                     "string_id_on_A=%.4f unified_on_A=%.4f self_inflicted=%d" % (
                         sA["string_identity_acc_on_A"], sA["unified_acc_on_A"],
                         o["head_to_head"]["string_identity_wins_unified_loses"])))
    sB = o["slice_B_reachable_diff_head"]
    oks.append(check("W4 different-head slice: BOTH string-identity and the incumbent score 0 (head-gated) -> bridging is the only route there",
                     sB["string_identity_correct"] == 0 and sB["unified_correct"] == 0 and sB["n"] > 500,
                     "sliceB n=%d string_id=%d unified=%d" % (sB["n"], sB["string_identity_correct"], sB["unified_correct"])))
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
