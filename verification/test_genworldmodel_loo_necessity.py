"""Witness -- the CONTEXT-CONDITIONED structure (research mechanism #1: LOO counterfactual world-state
necessity; Trabasso & van den Broek 1985 / Mackie INUS / Batusov-Soutchanski STRIPS actual-causality). BUILT
and brain-foundational (reuses hdlab.world_state_register fold + precondition state, folding the WHOLE story --
categorically different from pairwise rs_fire), but a rigorous LOCATED NEGATIVE on real narrative, with the exact
missing dependency QUANTIFIED: it HARD-FAILs (no CI-sep integrator lift on either corpus; on its ~4% firing
slice it does not beat its info-free twins), and the bottleneck is precisely NOT the mechanism and NOT the
operator lexicon (candidate_op_reach 0.585, E_has_goalobj 0.677) -- it is CROSS-SENTENCE OBJECT IDENTITY
(cross_sentence_obj_match only ~0.10): the object E needs is referred to by different surface forms/pronouns than
the candidate that establishes it, so the fold cannot connect them without RESOLVED DISCOURSE REFERENTS (coref /
meaning foundation, Q111). Mirrors cycle-3, where ORACLE binding made this mechanism class EXCEL (+0.035 CI-sep).
The bar's explicitly-blessed full pass: a located negative naming the exact missing knowledge.

problem: build_the_generative_result_state_world_model
Run: .venv/Scripts/python.exe verification/test_genworldmodel_loo_necessity.py
"""
from __future__ import annotations
import os, sys
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
from experiments import exp_genworldmodel_loo_necessity_v1 as L


def check(name, cond, detail=""):
    print("[%s] %s: %s" % ("PASS" if cond else "FAIL", name, detail))
    return bool(cond)


def main():
    o = L.run(n_glu=3000, n_tmw=1500)
    glu = o["GLUCOSE"]; tmw = o["TellMeWhy_GOAL"]; cd = o["coverage_diagnostic"]["GLUCOSE"]
    oks = []

    oks.append(check(
        "W1 the context-conditioned LOO mechanism is BUILT and RUNS (folds the story world-state, fires on some items)",
        glu["loo_fires_frac"] > 0.0,
        "GLUCOSE fires %.3f | TMW-GOAL fires %.3f | TMW-OTHER fires %.3f" % (
            glu["loo_fires_frac"], tmw["loo_fires_frac"], o["TellMeWhy_OTHER"]["loo_fires_frac"])))

    oks.append(check(
        "W2 HARD-FAIL on real narrative: no CI-separated integrator lift on either corpus (within noise)",
        not glu["loo_vs_base_integrator"]["ci_sep"] and not tmw["loo_vs_base_integrator"]["ci_sep"],
        "GLUCOSE +loo %+.4f CI%s | TMW-GOAL +loo %+.4f CI%s" % (
            glu["loo_vs_base_integrator"]["delta"], glu["loo_vs_base_integrator"]["ci"],
            tmw["loo_vs_base_integrator"]["delta"], tmw["loo_vs_base_integrator"]["ci"])))

    oks.append(check(
        "W3 where it fires it does NOT beat its info-free twins (necessity-permutation null + story-order shuffle) "
        "-> the firing slice is not carrying genuine necessity signal at surface-head binding",
        not glu["beats_null"] and not glu["beats_order_shuffle"],
        "GLUCOSE alone %.3f vs null p95 %.3f | order-shuffle %.3f" % (
            glu["loo_alone_acc_on_firing"], glu["null_p95"], glu["order_shuffle_alone_acc"])))

    oks.append(check(
        "W4 bottleneck LOCALIZED to cross-sentence OBJECT IDENTITY (the coref/meaning-foundation dependency, "
        "Q111), NOT the mechanism or the operator lexicon: object-match << op-reach and << E-has-goalobj",
        cd["cross_sentence_obj_match"] < 0.25 and cd["candidate_op_reach"] > 0.4 and cd["E_has_goalobj"] > 0.5,
        "E_has_goalobj %.3f | candidate_op_reach %.3f | cross_sentence_obj_match %.3f" % (
            cd["E_has_goalobj"], cd["candidate_op_reach"], cd["cross_sentence_obj_match"])))

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
