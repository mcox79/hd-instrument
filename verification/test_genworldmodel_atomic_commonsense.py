"""Witness -- INGESTING a commonsense causal KB (ATOMIC, Sap et al. 2019) the NAIVE way does NOT recover the
zero-overlap residual: as an event->effect reachability signal it FLOODS (K=2 fires 97%) or stays context-free
(K=1 fires 72%), gives NO integrator lift over the surface signal set, and is WORSE than base on the zero-overlap
gold slice (~0.20 vs ~0.54). Reason: a generic KB knows what-causes-what IN GENERAL ('study'->'pass') but not
WHICH candidate caused it in THIS story -- context-free, the same wall as the cycle-11 directed causal-KB. =>
the fix is NOT a bigger/raw KB dump; it is the brain-faithful CAREFUL INGEST (hdlab.consolidation_gate -- whose
own result is 'reading-derived growth does not beat the curated glass-box') + the CURATED meaning_foundation
(LATENT) applied IN-CONTEXT (bridging/forward-simulation), not context-free reachability.

problem: build_the_generative_result_state_world_model
Run: .venv/Scripts/python.exe verification/test_genworldmodel_atomic_commonsense.py
"""
from __future__ import annotations
import os, sys
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
from experiments import exp_genworldmodel_atomic_commonsense_v1 as A


def check(name, cond, detail=""):
    print("[%s] %s: %s" % ("PASS" if cond else "FAIL", name, detail))
    return bool(cond)


def main():
    o = A.run(cap=6000)
    oks = []

    oks.append(check(
        "W1 the commonsense causal KB INGESTS (ATOMIC: many verbs + edges) and FIRES (it is present, not absent)",
        o["atomic_verbs"] > 500 and o["atomic_fires_frac_K1"] > 0.2,
        "ATOMIC %d verbs %d edges | fires K1 %.3f K2 %.3f" % (
            o["atomic_verbs"], o["atomic_pairs"], o["atomic_fires_frac_K1"], o["atomic_fires_frac_K2"])))

    oks.append(check(
        "W2 but naive ingest gives NO CI-separated integrator lift at either operating point (K=1 precise or "
        "K=2 flood)",
        not o["atomicK1_vs_base"]["ci_sep"] and not o["atomicK2_vs_base"]["ci_sep"],
        "base %.3f | +atomicK1 %.3f (%+.4f%s) | +atomicK2 %.3f (%+.4f%s)" % (
            o["acc_base"], o["acc_with_atomic_K1"], o["atomicK1_vs_base"]["delta"], o["atomicK1_vs_base"]["ci"],
            o["acc_with_atomic_K2"], o["atomicK2_vs_base"]["delta"], o["atomicK2_vs_base"]["ci"])))

    oks.append(check(
        "W3 it does NOT recover the ZERO-OVERLAP residual -- on the zero-overlap gold slice the ATOMIC pick is "
        "no better (and typically worse) than the base integrator (context-free: knows general causation, not "
        "which candidate here)",
        o["zov_atomicK1_hit"] <= o["zov_base_hit"] + 0.02,
        "zero-overlap gold n=%d: atomicK1-picks-gold %.3f vs base %.3f" % (
            o["n_zero_overlap_gold"], o["zov_atomicK1_hit"], o["zov_base_hit"])))

    oks.append(check(
        "W4 verdict = ATOMIC floods / no lift / context-free -> the lever is CAREFUL brain-faithful ingest + "
        "in-context application, not a raw KB dump",
        o["verdict"] == "ATOMIC_FLOODS_NO_LIFT_CONTEXT_FREE", o["verdict"]))

    n = sum(oks)
    print("=" * 92)
    print("%s (%d/%d)" % ("ALL CHECKS PASS" if n == len(oks) else "SOME CHECKS FAILED", n, len(oks)))
    print("=" * 92)
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
