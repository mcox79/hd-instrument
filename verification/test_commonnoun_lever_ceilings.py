"""Witness -- the two candidate/ranking levers are glass-box-capped: (2) same-head splitting is net-negative on the
board metric; (3) different-head bridging is low-yield (~15% of slice B) and low-precision (~52%), so it pollutes.
The residual routes to the world-knowledge / entity-type-KB (sibling brief), not to salience ranking.
problem: improve_the_common_noun_coref_candidate_quality_the_resolver_trails_string_identity
Run: .venv/Scripts/python.exe verification/test_commonnoun_lever_ceilings.py
"""
from __future__ import annotations
import os, sys
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
from experiments import exp_commonnoun_clustering_probe_gum_v1 as C
from experiments import exp_commonnoun_bridge_probe_gum_v1 as B


def check(name, cond, detail=""):
    print("[%s] %s: %s" % ("PASS" if cond else "FAIL", name, detail))
    return bool(cond)


def main():
    oks = []
    _dev, test = C._load(None)
    si = C.eval_rule(test, lambda: C.a_string_identity)[2]
    rg = C.eval_rule(test, lambda: C.make_recency_gap(80))[2]
    md = C.eval_rule(test, lambda: C.a_modifier_split)[2]
    oks.append(check("W1 same-head SPLITTING is net-negative on the board metric (breaks more correct merges than it fixes over-merge)",
                     rg < si and md < si,
                     "string_id=%.4f recency_gap=%.4f modifier=%.4f" % (si, rg, md)))

    bo = B.run(n_docs=None)
    wn = bo["bridges"]["wordnet_syn"]; comb = bo["bridges"]["combined"]
    oks.append(check("W2 different-head slice B is a large share of items but glass-box bridging reaches only a small fraction",
                     bo["sliceB_frac"] > 0.2 and wn["yield_frac_of_sliceB"] < 0.35,
                     "sliceB_frac=%.3f wordnet_yield=%.3f" % (bo["sliceB_frac"], wn["yield_frac_of_sliceB"])))
    oks.append(check("W3 the bridge is LOW-PRECISION (~half wrong) -> it pollutes the referent cards; net gain is marginal",
                     comb["precision"] < 0.65 and comb["net_gain_over_string_identity"] < 0.05,
                     "combined precision=%.4f net_gain=%.4f" % (comb["precision"], comb["net_gain_over_string_identity"])))
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
