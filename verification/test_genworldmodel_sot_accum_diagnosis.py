"""Witness -- HONEST diagnosis of the sot_accum win. The order-SHUFFLE twin's 0.758 (in the SOT witness) was a
SINGLE-SEED artifact: averaged over 40 random orders the shuffle marginal (0.593) does NOT exceed real-order
sot_accum (0.610), so narrative order is NOT the lever and NOT suboptimal. The win is ~80% ORDER-INDEPENDENT
CUE-DISTINCTIVENESS: `distinct` (each shared effect-stem weighted 1/k_s = given-new / cue-diagnosticity;
Haviland-Clark 1974; McClelland-Rumelhart cue validity) beats topical +0.129 CI-sep (of the +0.159 total) and is
load-bearing. Real-order accumulation adds only a small, NON-CI-separated increment on top.

problem: build_the_generative_result_state_world_model
Run: .venv/Scripts/python.exe verification/test_genworldmodel_sot_accum_diagnosis.py
"""
from __future__ import annotations
import os, sys
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
from experiments import exp_genworldmodel_sot_accum_diagnosis_v1 as D


def check(name, cond, detail=""):
    print("[%s] %s: %s" % ("PASS" if cond else "FAIL", name, detail))
    return bool(cond)


def main():
    o = D.run(n=3000)
    cs = o["coalition_subset"]; ov = cs["overall"]
    oks = []

    oks.append(check(
        "W1 the win is largely ORDER-FREE: `distinct` (cue-distinctiveness, sum_s 1/k_s) beats topical CI-separated",
        cs["distinct_vs_topical"]["ci_sep"] and ov["distinct"] > ov["topical"],
        "distinct %.3f vs topical %.3f (%+.4f CI%s)" % (
            ov["distinct"], ov["topical"], cs["distinct_vs_topical"]["delta"], cs["distinct_vs_topical"]["ci"])))

    oks.append(check(
        "W2 distinct is LOAD-BEARING: beats its value-permutation info-free twin CI-separated",
        cs["distinct_vs_infofree_twin"]["ci_sep"] and ov["distinct"] > ov["distinct_infofree_twin"],
        "distinct %.3f vs info-free twin %.3f (%+.4f CI%s)" % (
            ov["distinct"], ov["distinct_infofree_twin"], cs["distinct_vs_infofree_twin"]["delta"],
            cs["distinct_vs_infofree_twin"]["ci"])))

    oks.append(check(
        "W3 the 0.758 order-shuffle figure was a SINGLE-SEED artifact: averaged over 40 orders the shuffle "
        "marginal does NOT exceed real-order sot_accum (order is not suboptimal / not the lever)",
        ov["accum_shuffle_avg"] <= ov["sot_accum"] + 0.005,
        "accum_shuffle_avg %.3f <= sot_accum %.3f" % (ov["accum_shuffle_avg"], ov["sot_accum"])))

    oks.append(check(
        "W4 narrative ORDER adds only a small, NON-CI-separated increment over the order-free distinct arm "
        "(so the honest mechanism is cue-distinctiveness, not narrative-order accumulation)",
        not cs["distinct_vs_sot_accum"]["ci_sep"] and cs["distinct_vs_sot_accum"]["ci"][1] >= -0.001,
        "distinct-sot_accum %+.4f CI%s (CI includes 0 -> order not separable)" % (
            cs["distinct_vs_sot_accum"]["delta"], cs["distinct_vs_sot_accum"]["ci"])))

    n = sum(oks)
    print("=" * 92)
    print("%s (%d/%d)  verdict=%s  n_coalition_subset=%d" % (
        "ALL CHECKS PASS" if n == len(oks) else "SOME CHECKS FAILED", n, len(oks), o["verdict"], cs["n"]))
    print("=" * 92)
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
