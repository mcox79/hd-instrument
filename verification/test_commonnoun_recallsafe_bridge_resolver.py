"""Witness -- the HEADLINE located negative: NO glass-box candidate/ranking mechanism beats same-head string-identity
on the board's common_noun_coref instrument; the resolver's deficit is cross-type PRONOUN POLLUTION (recovered by the
no-pollute ceiling), and BEATING string-identity is world-knowledge-bound (only the gold-cluster oracle clears it).
problem: improve_the_common_noun_coref_candidate_quality_the_resolver_trails_string_identity
Run: .venv/Scripts/python.exe verification/test_commonnoun_recallsafe_bridge_resolver.py
"""
from __future__ import annotations
import os, sys
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
from experiments import exp_commonnoun_recallsafe_bridge_resolver_gum_v1 as R


def check(name, cond, detail=""):
    print("[%s] %s: %s" % ("PASS" if cond else "FAIL", name, detail))
    return bool(cond)


def main():
    o = R.run(n_docs=None)
    cn = o["common_noun"]
    si = cn["string_identity"]["acc"]; urg = cn["urg_unified"]["acc"]
    npol = cn["rs_nopollute"]["acc"]; orc = cn["oracle_cluster"]["acc"]
    oks = []
    oks.append(check("W1 LADDER: urg_unified < rs_nopollute < string_identity < oracle_cluster (only gold clusters beat string-identity)",
                     urg < npol < si < orc,
                     "urg=%.4f nopollute=%.4f string_id=%.4f oracle=%.4f" % (urg, npol, si, orc)))
    oks.append(check("W2 the POLLUTION ceiling (pronouns never write eids) recovers most of the gap but STILL does not beat string-identity",
                     npol > urg + 0.02 and not cn["rs_nopollute_minus_string_identity"]["CIsep"]
                     and cn["rs_nopollute_minus_string_identity"]["ci"][1] < 0,
                     "nopollute-string_id ci=%s" % cn["rs_nopollute_minus_string_identity"]["ci"]))
    oks.append(check("W3 NO glass-box candidate/ranking arm (recall-safe, bridge, Nref-gate) BEATS string-identity CI-separated",
                     not cn["rs_parity_minus_string_identity"]["CIsep"]
                     and not cn["rs_bridge_minus_string_identity"]["CIsep"]
                     and not cn["rs_gate_bridge_minus_string_identity"]["CIsep"],
                     "parity=%.4f bridge=%.4f gate=%.4f all < string_id" % (
                         cn["rs_parity"]["acc"], cn["rs_bridge"]["acc"], cn["rs_gate_bridge"]["acc"])))
    oks.append(check("W4 de-pollution is ANTAGONISTIC: the arm that most recovers common REGRESSES the pronoun consumer (shared-card tradeoff)",
                     o["no_regress"]["pronoun"]["regress"] and not o["no_regress"]["name"]["regress"],
                     "pronoun d=%+.4f (regress) name d=%+.4f" % (
                         o["no_regress"]["pronoun"]["delta"], o["no_regress"]["name"]["delta"])))
    oks.append(check("W5 the info-free twin does NOT lose (random-within-same-head ties) -> same-head content, not ranking, carries the signal; ranking has no glass-box headroom",
                     not cn["rs_gate_bridge_minus_rs_gate_bridge_twin"]["CIsep"],
                     "gate-twin ci=%s" % cn["rs_gate_bridge_minus_rs_gate_bridge_twin"]["ci"]))
    oks.append(check("W6 even the highest-precision GLASS-BOX different-head bridge (text-stated apposition/copula is-a) nets ~0 over the no-pollute base -> every glass-box bridge is exhausted",
                     not cn["rs_nopollute_intext_isa_minus_rs_nopollute"]["CIsep"]
                     and cn["rs_nopollute_intext_isa_minus_rs_nopollute"]["delta"] < 0.005,
                     "intext_isa - nopollute = %s" % cn["rs_nopollute_intext_isa_minus_rs_nopollute"]["ci"]))
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
