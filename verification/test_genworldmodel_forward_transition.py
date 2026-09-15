"""Witness -- the OTHER component: an UNTRAINED ALGEBRAIC forward-TRANSITION operator over bound events, done
RIGHT (generative VSA: GENERATE C's predicted bound next-event -- participants preserved, predicate transitioned
to the ATOMIC-consequence distribution -- and CHECK vs the effect; NOT a retrieval lookup). Two decisive,
powered findings on pooled TellMeWhy-GOAL:
  (+) ROLE-BINDING STRUCTURE IS LOAD-BEARING: the forward-transition score CI-beats its BIND-SHUFFLE twin (roles
      permuted) -- the STRUCTURED bound representation carries real signal (the brain-foundational representational
      fix, confirmed; unlike the mean-pool where binding-shuffle matched).
  (-) the ATOMIC transition KNOWLEDGE is NOT load-bearing: it ties/loses to its ATOM-SHUFFLE twin (cause->effect
      map permuted) -- context-free transition knowledge does not carry even generatively; the score reduces to
      structured PARTICIPANT matching. Does NOT recover the zero-overlap residual.
=> the forward-transition MECHANISM + STRUCTURED representation are right and load-bearing, but its KNOWLEDGE
input cannot be supplied CONTEXT-FREELY (ATOMIC not load-bearing) nor TRAINED (SR-TD falsified) -- a working
transition needs SITUATION-SPECIFIC (context-conditioned) knowledge = the meaning-foundation-wired-live world
model (Q111). Structure: solved/load-bearing. Transition-knowledge: the wall.

problem: build_the_generative_result_state_world_model
Run: .venv/Scripts/python.exe verification/test_genworldmodel_forward_transition.py
"""
from __future__ import annotations
import os, sys
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
from experiments import exp_genworldmodel_forward_transition_v1 as F


def check(name, cond, detail=""):
    print("[%s] %s: %s" % ("PASS" if cond else "FAIL", name, detail))
    return bool(cond)


def main():
    o = F.run(cap=3000)
    oks = []

    oks.append(check(
        "W1 ROLE-BINDING STRUCTURE is LOAD-BEARING: the forward-transition CI-beats its BIND-SHUFFLE twin (roles "
        "permuted) -- the structured bound representation carries real signal (brain-foundational fix confirmed)",
        o["fwd_vs_bindshuf_twin"]["ci_sep"],
        "solo fwd %.3f vs bind-shuffle twin %.3f (%+.4f CI%s)" % (
            o["solo_fwd"], o["solo_bindshuf"], o["fwd_vs_bindshuf_twin"]["delta"], o["fwd_vs_bindshuf_twin"]["ci"])))

    oks.append(check(
        "W2 the ATOMIC transition KNOWLEDGE is NOT load-bearing: forward-transition ties/loses to its ATOM-SHUFFLE "
        "twin (cause->effect map permuted) -- context-free transition knowledge does not carry even generatively",
        not o["fwd_vs_atomshuf_twin"]["ci_sep"],
        "solo fwd %.3f vs atom-shuffle twin %.3f (%+.4f CI%s)" % (
            o["solo_fwd"], o["solo_atomshuf"], o["fwd_vs_atomshuf_twin"]["delta"], o["fwd_vs_atomshuf_twin"]["ci"])))

    oks.append(check(
        "W3 it does NOT recover the zero-overlap residual (participant matching alone cannot bridge studied->passed "
        "without a working, situation-specific predicate transition)",
        o["zov_fwd_hit"] <= o["zov_base_hit"] + 0.02,
        "zero-overlap gold n=%d: fwd %.3f vs base %.3f" % (o["n_zero_overlap_gold"], o["zov_fwd_hit"], o["zov_base_hit"])))

    oks.append(check(
        "W4 verdict = the transition-knowledge input is the wall (context-free ATOMIC not load-bearing; trained "
        "SR-TD falsified) -> needs situation-specific context-conditioned knowledge (Q111)",
        o["verdict"] in ("FWD_TRANSITION_NO_LIFT", "FWD_TRANSITION_LIFTS_NOT_LOAD_BEARING")
        and not o["transition_knowledge_load_bearing"], o["verdict"]))

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
