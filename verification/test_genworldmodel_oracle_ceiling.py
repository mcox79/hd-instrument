"""Witness -- the ORACLE-CEILING decomposition: KNOW EXACTLY what the brain-faithful component is looking for and
whether PATH A (the online per-story world-model) can supply it (owner: is there a way to know exactly what it's
looking for and if the prototype will solve? brain-faithful, right not easy). Self-supervised next-event surprisal
on naturalistic narrative (roc_stories) -- NO crowd gold, glass-box parse (NO spaCy), NO LLM. Decomposes the
predictability of the actual outcome into information tiers (T0 generic -> T1 story-context [=PATH A] -> T3
in-sample-experience oracle). Powered findings (n=8000):
  (W1) the STORY'S OWN CONTEXT carries REAL story-specific signal -- the best-link context predictor beats its
       STORY-SHUFFLE twin CI-sep (real story beats a random story's context). PATH A has something to grab.
  (W2) PATH A is PARTIAL -- story context closes ~1/3 of the total gap to the in-sample-experience oracle; the
       remaining ~2/3 needs having EXPERIENCED the specific scenario (the lifetime-grounded-knowledge frontier
       story-context alone cannot supply).
=> the brain-faithful target = surprisal-reducing story-specific structure; path A (online per-story world-model)
supplies a real but partial share; the residual is the lifetime learner / grounded-experience program.

problem: build_the_generative_result_state_world_model
Run: .venv/Scripts/python.exe verification/test_genworldmodel_oracle_ceiling.py
"""
from __future__ import annotations
import os, sys
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
from experiments import exp_genworldmodel_oracle_ceiling_v1 as O


def check(name, cond, detail=""):
    print("[%s] %s: %s" % ("PASS" if cond else "FAIL", name, detail))
    return bool(cond)


def main():
    o = O.run(cap=8000)
    sb = o["surprisal_bits"]
    oks = []
    oks.append(check(
        "W1 the story's OWN context carries real story-specific signal -- best-link context predictor beats its "
        "STORY-SHUFFLE twin CI-sep (path A has genuine story-specificity to exploit)",
        o["story_context_load_bearing"],
        "T1best %.3f vs shuffle twin (delta %+.4f CI%s)" % (
            sb["T1best_story_context"], o["T1best_vs_shuffle_twin"]["delta"], o["T1best_vs_shuffle_twin"]["ci"])))
    oks.append(check(
        "W2 PATH A is PARTIAL -- story context closes a real but minority share (0.15-0.55) of the T0->T3 gap; the "
        "residual needs lifetime EXPERIENCE (in-sample oracle) story-context alone cannot supply",
        0.15 <= o["fraction_of_gap_closed_by_story_context"] <= 0.55
        and o["surprisal_bits"]["T1best_story_context"] < o["surprisal_bits"]["T0_generic"],
        "T0 %.3f -> T1best %.3f -> T3 %.3f | closes %.0f%% | residual %.3f bits" % (
            sb["T0_generic"], sb["T1best_story_context"], sb["T3_insample_oracle"],
            o["fraction_of_gap_closed_by_story_context"] * 100, o["residual_T1best_T3"])))
    oks.append(check(
        "W3 verdict names path A partial + the residual as the experience/lifetime-learner frontier",
        o["verdict"] in ("PATH_A_PARTIAL_STORY_CONTEXT_CLOSES_SOME_RESIDUAL_IS_EXPERIENCE",
                         "PATH_A_SOLVES_STORY_CONTEXT_CLOSES_MAJORITY"),
        o["verdict"]))
    n = sum(oks)
    print("=" * 100)
    print("%s (%d/%d)" % ("ALL CHECKS PASS" if n == len(oks) else "SOME CHECKS FAILED", n, len(oks)))
    print("=" * 100)
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
