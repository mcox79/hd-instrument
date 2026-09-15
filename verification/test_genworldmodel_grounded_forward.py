"""Witness -- R2 of the grounding synthesis: does PERCEPTUAL GROUNDING (Lancaster sensorimotor SimHash fillers)
supply what amodal random fillers cannot, in the online generative forward model on Story Cloze? LOCATED NEGATIVE:
  (W1) grounding does NOT beat amodal (it ties/slightly-hurts) -- perceptual SIMILARITY fillers do not add
       forward-prediction signal.
  (W2) grounding is NOT load-bearing (ties its grounded-SHUFFLE twin) -- the specific perceptual structure carries
       nothing here.
  (W3) verdict GROUNDING_NO_EFFECT / not-load-bearing.
=> grounded similarity encodes "alike" (perception/interaction), NOT "leads-to" (directed causal dynamics); it
cannot supply the affordance/causal structure the forward model needs. Combined with R1 (contingency, inert on the
anti-correlated gold) this triangulates the wall: DIRECTED CAUSAL DYNAMICS are absent from every representation and
not text-recoverable -- a grounded-experiential foundation, not a representation swap.

problem: build_the_generative_result_state_world_model
Run: .venv/Scripts/python.exe verification/test_genworldmodel_grounded_forward.py
"""
from __future__ import annotations
import os, sys
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
from experiments import exp_genworldmodel_grounded_forward_v1 as G


def check(name, cond, detail=""):
    print("[%s] %s: %s" % ("PASS" if cond else "FAIL", name, detail))
    return bool(cond)


def main():
    o = G.run(cap=3000)
    oks = []
    oks.append(check(
        "W1 GROUNDING does not beat amodal fillers -- perceptual-similarity fillers add no forward-prediction "
        "signal on the native task",
        not o["grounding_beats_amodal"],
        "amodal %.4f | grounded %.4f | grounded vs amodal %+.4f CI%s" % (
            o["acc_amodal"], o["acc_grounded"], o["grounded_vs_amodal"]["delta"], o["grounded_vs_amodal"]["ci"])))
    oks.append(check(
        "W2 GROUNDING is NOT load-bearing (ties its grounded-shuffle twin) -- the specific perceptual structure "
        "carries nothing (grounding = similarity, not causal dynamics)",
        not o["grounding_load_bearing"],
        "grounded %.4f vs shuffle %.4f (%+.4f CI%s); %d covered words" % (
            o["acc_grounded"], o["acc_grounded_shuffle"], o["grounded_vs_shuffle_twin"]["delta"],
            o["grounded_vs_shuffle_twin"]["ci"], o["n_covered_words"])))
    oks.append(check(
        "W3 verdict = grounding-as-similarity supplies no causal-dynamics signal (directed causal structure is a "
        "grounded-experiential foundation, not a representation swap)",
        o["verdict"] in ("GROUNDING_NO_EFFECT", "GROUNDING_LOAD_BEARING_NO_LIFT_OVER_AMODAL"), o["verdict"]))
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
