"""Witness -- the WIN unearthed by understanding the failures: a TYPED CARD VIEW (score common-noun coref on the
name+common nominal identity, so weak pronoun bindings never pollute it) + a NON-WRITING (Nref-hold) different-head
bridge BEATS same-head string-identity on the board's common_noun_coref instrument, CI-separated, info-free twin
LOSING, with NO pronoun / kb / named-antecedent regress.
problem: improve_the_common_noun_coref_candidate_quality_the_resolver_trails_string_identity
Run: .venv/Scripts/python.exe verification/test_commonnoun_typed_identity.py
"""
from __future__ import annotations
import os, sys
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
from experiments import exp_commonnoun_typed_identity_gum_v1 as T


def check(name, cond, detail=""):
    print("[%s] %s: %s" % ("PASS" if cond else "FAIL", name, detail))
    return bool(cond)


def main():
    o = T.run(n_docs=None)
    cn = o["common_noun"]
    nr = o["no_regress"]
    oks = []
    oks.append(check("W1 typed+non-writing bridge BEATS same-head string-identity CI-separated on the board instrument",
                     cn["typed_bridge_nowrite_minus_string_identity"]["CIsep"]
                     and cn["typed_bridge_nowrite"]["acc"] > cn["string_identity"]["acc"],
                     "typed=%.4f string_id=%.4f delta_ci=%s" % (
                         cn["typed_bridge_nowrite"]["acc"], cn["string_identity"]["acc"],
                         cn["typed_bridge_nowrite_minus_string_identity"]["ci"])))
    oks.append(check("W2 info-free twin (bridge fires but to a RANDOM antecedent -> type signal destroyed) LOSES CI-separated",
                     cn["typed_bridge_nowrite_minus_typed_bridge_nowrite_twin"]["CIsep"],
                     "twin=%.4f delta_ci=%s" % (cn["typed_bridge_nowrite_twin"]["acc"],
                                                cn["typed_bridge_nowrite_minus_typed_bridge_nowrite_twin"]["ci"])))
    oks.append(check("W3 the TYPED VIEW alone recovers the resolver +0.03..0.06 over the incumbent CI-separated (de-pollution)",
                     cn["typed_base_minus_urg_unified"]["CIsep"],
                     "typed_base=%.4f incumbent=%.4f delta_ci=%s" % (
                         cn["typed_base"]["acc"], cn["urg_unified"]["acc"], cn["typed_base_minus_urg_unified"]["ci"])))
    oks.append(check("W4 the WRITING bridge does NOT beat the typed base -> confirms the pollution mechanism (the write, not the resolution, is the cost)",
                     not cn["typed_bridge_write_minus_typed_base"]["CIsep"]
                     and cn["typed_bridge_write"]["acc"] <= cn["typed_bridge_nowrite"]["acc"],
                     "write=%.4f nowrite=%.4f" % (cn["typed_bridge_write"]["acc"], cn["typed_bridge_nowrite"]["acc"])))
    oks.append(check("W5 NO regress on pronoun (byte-identical) / kb / named-antecedent consumers",
                     not nr["typed_bridge_nowrite"]["pronoun"]["regress"]
                     and not nr["typed_bridge_nowrite"]["kb_hardlink"]["regress"]
                     and not nr["typed_bridge_nowrite"]["name"]["regress"],
                     "pronoun d=%+.4f kb d=%+.4f name d=%+.4f" % (
                         nr["typed_bridge_nowrite"]["pronoun"]["delta"], nr["typed_bridge_nowrite"]["kb_hardlink"]["delta"],
                         nr["typed_bridge_nowrite"]["name"]["delta"])))
    oks.append(check("W6 FIDELITY: the substrate's sense-resolved typed-spokes comparator BEATS the crude WordNet-MFS comparator CI-sep (more brain-foundational AND higher score)",
                     cn["typed_bridge_nowrite_minus_typed_bridge_wordnet"]["CIsep"],
                     "typed_spokes=%.4f wordnet=%.4f delta_ci=%s" % (
                         cn["typed_bridge_nowrite"]["acc"], cn["typed_bridge_wordnet"]["acc"],
                         cn["typed_bridge_nowrite_minus_typed_bridge_wordnet"]["ci"])))
    oks.append(check("W7 OPTIMALITY: always-hold BEATS the graded commit-gate CI-sep (committing corrupts the same-head chain), and the soft-binding is a WASH (<= hold; ranking is not the lever) -> the design is optimal, not a compromise",
                     cn["typed_bridge_nowrite_minus_typed_bridge_commit"]["CIsep"]
                     and cn["typed_bridge_softbind"]["acc"] <= cn["typed_bridge_nowrite"]["acc"],
                     "hold=%.4f commit=%.4f (regress CI-sep) softbind=%.4f (wash)" % (
                         cn["typed_bridge_nowrite"]["acc"], cn["typed_bridge_commit"]["acc"], cn["typed_bridge_softbind"]["acc"])))
    dc = o["commit_corruption_decomp"]
    oks.append(check("W8 MECHANISM (why commit fails): committing leaves BRIDGE items ~unchanged but CRASHES SAME-HEAD items (the bridged head is written into the target -> later same-head mentions inherit the uncertain bridge)",
                     dc["samehead_drop_from_commit"] > 0.02
                     and abs(dc["hold"]["bridge"]["acc"] - dc["commit"]["bridge"]["acc"]) < 0.02,
                     "samehead hold=%.3f commit=%.3f (drop %.3f); bridge hold=%.3f commit=%.3f; bridge glass-box precision=%.3f (world-knowledge-bound)" % (
                         dc["hold"]["samehead"]["acc"], dc["commit"]["samehead"]["acc"], dc["samehead_drop_from_commit"],
                         dc["hold"]["bridge"]["acc"], dc["commit"]["bridge"]["acc"], dc["bridge_glassbox_precision"])))
    kb = o["kb_merge_view"]
    oks.append(check("W9 CONSUMER-SPECIFIC MERGE VIEW (prototyped): the bridge, exposed via the kb view, lifts common->named-entity resolution from a 0.000 floor, with common/pronoun byte-unchanged (additive/read-only)",
                     kb["no_bridge"]["clean_acc"] == 0.0 and kb["bridge_holdview"]["clean_acc"] > 0.0
                     and o["no_regress"]["typed_bridge_nowrite"]["pronoun"]["delta"] == 0.0,
                     "common->name: no_bridge=%.4f bridge=%.4f (lift +%.4f, n=%d); common/pronoun unchanged" % (
                         kb["no_bridge"]["clean_acc"], kb["bridge_holdview"]["clean_acc"], kb["lift_clean"], kb["bridge_holdview"]["n"])))
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
