"""Witness -- the PROPER brain-foundational GENERATIVE solution (predictive coding, not retrieval): the cause is
the candidate whose removal most RAISES the effect's prediction error against the running situation-model gist
(N400 surprisal-reduction; reusing hdlab.n400_coherence_monitor's content prediction-error over
hdlab.grounded_similarity grounded vectors; Rao-Ballard/Friston; Rabovsky 2018; Reynolds-Zacks-Braver EST). NO
training. RESULT: the generative signal BEATS the cheap raw-overlap cue CI-separated (generate > retrieve, even
for content) -- but at the available 12-d GROUNDED content resolution it is too COARSE to lift the integrator or
recover the zero-overlap residual (implicit causal links). So the generative MECHANISM is correct; the remaining
gap is content-REPRESENTATION resolution -> run the SAME generative loop over the richer CURATED meaning
foundation (200-d sense-signatures), the concrete final wire (Q111).

problem: build_the_generative_result_state_world_model
Run: .venv/Scripts/python.exe verification/test_genworldmodel_generative_simulation.py
"""
from __future__ import annotations
import os, sys
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
from experiments import exp_genworldmodel_generative_simulation_v1 as G


def check(name, cond, detail=""):
    print("[%s] %s: %s" % ("PASS" if cond else "FAIL", name, detail))
    return bool(cond)


def main():
    o = G.run(cap=6000)
    oks = []

    oks.append(check(
        "W1 the GENERATIVE simulation signal (N400 surprisal-reduction over the running gist) BEATS the cheap "
        "raw-overlap cue CI-separated -- generate > retrieve, and it is NOT relabeled overlap",
        o["gensim_vs_overlap"]["ci_sep"] and o["gen_sim_solo"] > o["overlap_solo"],
        "gen_sim solo %.3f vs overlap solo %.3f (%+.4f CI%s)" % (
            o["gen_sim_solo"], o["overlap_solo"], o["gensim_vs_overlap"]["delta"], o["gensim_vs_overlap"]["ci"])))

    oks.append(check(
        "W2 the generative mechanism RUNS everywhere (fires ~1.0, no coverage wall -- unlike retrieval) and "
        "reuses landed brain-foundational organs (N400 error + grounded vectors), no training",
        o["gen_sim_fires"] > 0.9,
        "gen_sim fires %.3f | weight %.3f" % (o["gen_sim_fires"], o["gensim_weight"])))

    oks.append(check(
        "W3 but at 12-d GROUNDED content resolution it is too COARSE: no CI-separated integrator lift AND it does "
        "not recover the zero-overlap residual (stays below the base integrator's ~0.54 there) -> the gap is "
        "content-representation resolution, not the mechanism",
        not o["gensim_vs_base"]["ci_sep"] and o["zov_gensim_hit"] < 0.45,
        "+gensim over base %+.4f CI%s | zero-overlap gold n=%d: gensim-picks-gold %.3f" % (
            o["gensim_vs_base"]["delta"], o["gensim_vs_base"]["ci"], o["n_zero_overlap_gold"], o["zov_gensim_hit"])))

    n = sum(oks)
    print("=" * 92)
    print("%s (%d/%d)  verdict=%s" % ("ALL CHECKS PASS" if n == len(oks) else "SOME CHECKS FAILED", n, len(oks), o["verdict"]))
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
