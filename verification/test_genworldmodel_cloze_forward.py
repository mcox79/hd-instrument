"""Witness -- the REAL LEVER on its NATIVE task (owner: go after the real lever, make it happen). The online-
learned GENERATIVE forward world-model (MINERVA-2 echo over structured events; transitions learned UNSUPERVISED
from roc_stories narrative order) evaluated on the Story Cloze Test (pick the coherent ending; the world-model's
native forward-prediction task, chance 0.5, n=1871). DECISIVE LOCATED NEGATIVE:
  (W1) AT CHANCE -- the generative forward model does NOT predict real endings above chance (acc CI includes 0.5).
  (W2) the LEARNED TRANSITIONS are NOT load-bearing -- ties the SHUFFLE-TRANSITION twin (permuted effect traces).
  (W3) verdict FWD_MODEL_AT_CHANCE.
=> the ARCHITECTURE is brain-foundational (structured binding + episodic echo + predictive coding) but its
KNOWLEDGE SUBSTRATE is not: text-statistical event co-occurrence over UNGROUNDED symbol fillers does not carry the
grounded causal structure the brain's forward model uses. The mechanism is starved of GROUNDING, not of a gold.

problem: build_the_generative_result_state_world_model
Run: .venv/Scripts/python.exe verification/test_genworldmodel_cloze_forward.py
"""
from __future__ import annotations
import os, sys
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
from experiments import exp_genworldmodel_cloze_forward_v1 as C


def check(name, cond, detail=""):
    print("[%s] %s: %s" % ("PASS" if cond else "FAIL", name, detail))
    return bool(cond)


def main():
    o = C.run(cap=3000)
    oks = []
    oks.append(check(
        "W1 the generative forward model is AT CHANCE on its native forward-prediction task (Story Cloze) -- the "
        "learned text-statistical transitions do not predict real endings above chance",
        not o["beats_chance"],
        "acc %.4f CI%s (chance 0.5); %d traces / %d roc stories" % (
            o["acc"], o["acc_ci"], o["n_traces"], o["n_trace_stories"])))
    oks.append(check(
        "W2 the LEARNED TRANSITIONS are NOT load-bearing -- the forward model ties its SHUFFLE-TRANSITION twin "
        "(permuted effect traces): text co-occurrence of surface events carries no grounded causal structure",
        not o["transition_load_bearing"],
        "vs trans-shuffle %+.4f CI%s" % (o["vs_transshuf_twin"]["delta"], o["vs_transshuf_twin"]["ci"])))
    oks.append(check(
        "W3 verdict = at chance / transitions not load-bearing (the architecture is brain-foundational; the "
        "ungrounded text-statistical KNOWLEDGE substrate is the gap)",
        o["verdict"] in ("FWD_MODEL_AT_CHANCE", "FWD_MODEL_BEATS_CHANCE_NOT_LOAD_BEARING"), o["verdict"]))
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
