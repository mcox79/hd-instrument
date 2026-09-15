"""Witness -- the different-head slice (the ONLY headroom) is dominated by world-knowledge / abstract anaphora, NOT
glass-box in-text signal: 84% residual world-knowledge, ~16% glass-box-reachable (apposition/copula is-a + name +
WordNet). This is WHY candidate/ranking cannot beat string-identity: the beat requires the barred world knowledge.
problem: improve_the_common_noun_coref_candidate_quality_the_resolver_trails_string_identity
Run: .venv/Scripts/python.exe verification/test_commonnoun_diffhead_anatomy.py
"""
from __future__ import annotations
import os, sys
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
from experiments import exp_commonnoun_diffhead_anatomy_gum_v1 as A


def check(name, cond, detail=""):
    print("[%s] %s: %s" % ("PASS" if cond else "FAIL", name, detail))
    return bool(cond)


def main():
    o = A.run(n_docs=None, dump=0)
    c = o["categories"]
    oks = []
    oks.append(check("W1 the different-head slice is DOMINATED by residual world-knowledge / abstract anaphora (>70%)",
                     c["residual_world_knowledge"]["frac_of_diffhead"] > 0.7,
                     "residual=%.4f (n=%d of %d)" % (c["residual_world_knowledge"]["frac_of_diffhead"],
                                                     c["residual_world_knowledge"]["n"], o["n_different_head"])))
    oks.append(check("W2 glass-box in-text signal (appos/copula is-a + name-containment + WordNet) reaches only a small fraction",
                     o["glassbox_reachable_frac"] < 0.25,
                     "glassbox_reachable=%.4f" % o["glassbox_reachable_frac"]))
    oks.append(check("W3 text-stated is-a (apposition/copula) exists but is small -> a real brain-faithful cue, not a big lever",
                     0 < c["appos_copula_intext"]["n"] < c["residual_world_knowledge"]["n"],
                     "appos_copula n=%d" % c["appos_copula_intext"]["n"]))
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
