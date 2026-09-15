"""Witness -- the REAL LEVER on TellMeWhy-GOAL (owner: go after the real lever, brain-foundationally). The
online-learned directed GENERATIVE forward world-model (MINERVA-2 echo over structured bound events; transitions
learned UNSUPERVISED from narrative order; scored by forward-prediction + context-conditioned surprise-reduction).
LOCATED NEGATIVE, powered on pooled TellMeWhy-GOAL (n=935, robust across 12k and 40k traces -- more data did NOT
help, ruling out a data-limit):
  (W1) NO CI-sep integrator lift over the strong base (neither the forward-prediction nor the context-conditioned
       surprise-reduction arm beats the base).
  (W2) the LEARNED TRANSITIONS are not CI-sep load-bearing (both arms tie/only-borderline over the SHUFFLE-
       TRANSITION twin) -- text-statistical transitions carry no more than a shuffle.
=> completes the knowledge sweep: static-associative (cycle-26) + static-directed (cycle-24) + online-learned-
generative (this) ALL fail. The mechanism/architecture is brain-foundational; the KNOWLEDGE substrate (ungrounded
text co-occurrence) and the explanation-gold are the non-brain-foundational parts.

problem: build_the_generative_result_state_world_model
Run: .venv/Scripts/python.exe verification/test_genworldmodel_online_forward_model.py
"""
from __future__ import annotations
import os, sys
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
from experiments import exp_genworldmodel_online_forward_model_v1 as F


def check(name, cond, detail=""):
    print("[%s] %s: %s" % ("PASS" if cond else "FAIL", name, detail))
    return bool(cond)


def main():
    o = F.run(cap=3000)
    F_, C_ = o["FWD"], o["CTX"]
    oks = []
    oks.append(check(
        "W1 NO CI-sep integrator lift over the strong base (neither the forward-prediction nor the "
        "context-conditioned surprise-reduction arm beats it)",
        not o["lifts"],
        "base %.3f | FWD acc %.3f (%+.4f CI%s) | CTX acc %.3f (%+.4f CI%s)" % (
            o["acc_base"], F_["acc"], F_["vs_base"]["delta"], F_["vs_base"]["ci"],
            C_["acc"], C_["vs_base"]["delta"], C_["vs_base"]["ci"])))
    oks.append(check(
        "W2 the LEARNED TRANSITIONS are not CI-sep load-bearing (tie/borderline over the shuffle-transition twin) "
        "-- text-statistical transitions carry no more than a shuffle",
        not o["transition_load_bearing"],
        "FWD vs trans-shuf %+.4f CI%s | CTX vs trans-shuf %+.4f CI%s | traces %d/%d stories" % (
            F_["vs_transhuf_twin"]["delta"], F_["vs_transhuf_twin"]["ci"],
            C_["vs_transhuf_twin"]["delta"], C_["vs_transhuf_twin"]["ci"], o["n_traces"], o["n_trace_stories"])))
    oks.append(check(
        "W3 verdict = no lift / transitions not load-bearing (architecture brain-foundational; ungrounded "
        "text-statistical knowledge is the gap)",
        o["verdict"] in ("FWD_MODEL_NO_LIFT_TRANSITION_NOT_LOAD_BEARING", "FWD_MODEL_LIFTS_NOT_LOAD_BEARING"),
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
