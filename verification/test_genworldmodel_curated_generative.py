"""Witness -- feeding the RICHER CURATED meaning_foundation (200-d, WSD-selected sense signatures, done RIGHT via
diagnostic_context_wsd -- not a cheap all-sense average) into the generative predictive-coding loop. HONEST
result: it does NOT recover the residual and gives NO integrator lift, and DECISIVELY the curated KNOWLEDGE is
NOT load-bearing -- a shuffled-knowledge twin (meaning_foundation signatures permuted across synsets) MATCHES it,
and the richer 200-d curated representation ties the coarse 12-d grounded one. => the cycle-21 hypothesis
(representation RESOLUTION is the gap) is REFUTED: the generative surprisal-reduction over a sentence-MEAN content
gist is a coarse topical signal invariant to the specific meaning content. The real gap is STRUCTURED event
simulation over RESOLVED participants (the original result-state world-model), not content representation -- every
bag/gist/edge approach (retrieval OR generative-content) hits the same wall.

problem: build_the_generative_result_state_world_model
Run: .venv/Scripts/python.exe verification/test_genworldmodel_curated_generative.py
"""
from __future__ import annotations
import os, sys
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
from experiments import exp_genworldmodel_curated_generative_v1 as C


def check(name, cond, detail=""):
    print("[%s] %s: %s" % ("PASS" if cond else "FAIL", name, detail))
    return bool(cond)


def main():
    o = C.run(cap=3000)
    oks = []

    oks.append(check(
        "W1 the curated 200-d WSD-selected generative loop gives NO CI-separated integrator lift and does NOT "
        "recover the zero-overlap residual (stays below the base integrator's ~0.54)",
        not o["gencur_vs_base"]["ci_sep"] and o["zov_gencur_hit"] < 0.45,
        "base %.3f +gencur %.3f (%+.4f CI%s) | zero-overlap gold n=%d: gencur-picks-gold %.3f" % (
            o["acc_base"], o["acc_with_gencur"], o["gencur_vs_base"]["delta"], o["gencur_vs_base"]["ci"],
            o["n_zero_overlap_gold"], o["zov_gencur_hit"])))

    oks.append(check(
        "W2 DECISIVE: the curated KNOWLEDGE is NOT load-bearing -- a shuffled-knowledge twin (signatures permuted "
        "across synsets) matches it (not CI-beaten) -> the mean-gist generative signal is invariant to the "
        "specific meaning content",
        not o["gencur_vs_shuffled_knowledge_twin"]["ci_sep"],
        "gen_cur solo %.3f vs shuffled-knowledge twin %.3f (%+.4f CI%s)" % (
            o["solo_gen_cur"], o["solo_gen_cur_twin"], o["gencur_vs_shuffled_knowledge_twin"]["delta"],
            o["gencur_vs_shuffled_knowledge_twin"]["ci"])))

    oks.append(check(
        "W3 representation RESOLUTION was NOT the gap (cycle-21 hypothesis refuted): the richer 200-d curated "
        "representation does NOT CI-beat the coarse 12-d grounded one",
        not o["gencur_vs_grounded12"]["ci_sep"],
        "gen_cur(200d) %.3f vs grounded12 %.3f (%+.4f CI%s)" % (
            o["solo_gen_cur"], o["solo_gen_g12"], o["gencur_vs_grounded12"]["delta"], o["gencur_vs_grounded12"]["ci"])))

    oks.append(check(
        "W4 verdict = curated generative no gain -> the gap is STRUCTURED event simulation over resolved "
        "participants, not content representation",
        o["verdict"] in ("CURATED_GENERATIVE_NO_GAIN", "CURATED_RICHER_THAN_GROUNDED_NOT_LOAD_BEARING"),
        o["verdict"]))

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
