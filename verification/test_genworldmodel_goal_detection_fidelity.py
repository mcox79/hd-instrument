"""Witness -- deepening-cron cycle 4: FIDELITY-AUDIT of the upstream goal-DETECTION component the rollout depends
on (goal_register / Levin desiderative-intention-try classes), flagged Tier-6 "brain-fidelity unestablished".
Findings: (1) it is LOAD-BEARING (info-free shuffled-label twin LOSES CI-sep, ~chance); (2) it is brain-faithful
and high-fidelity (balanced-acc ~0.95, near-perfect non-goal rejection); (3) it is NOT the underperformance cause
-- it TIES a naive lexical floor on this gold (goal-causes are lexically obvious), so goal-detection is CLEARED
as the upstream fidelity gap. The remaining upstream suspect is coref/participant-binding quality (the confirmed
lever). This closes the checklist-#5 gap for goal_register.

problem: build_the_generative_result_state_world_model
Run: .venv/Scripts/python.exe verification/test_genworldmodel_goal_detection_fidelity.py
"""
from __future__ import annotations
import os, sys
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
from experiments import exp_genworldmodel_goal_detection_fidelity_v1 as G


def check(name, cond, detail=""):
    print("[%s] %s: %s" % ("PASS" if cond else "FAIL", name, detail))
    return bool(cond)


def main():
    o = G.run(n=1500)
    oks = []
    oks.append(check(
        "W1 goal-detection is LOAD-BEARING: the info-free shuffled-label twin LOSES CI-separated (drops to ~chance)",
        o["twin_loses"] and o["twin_balanced_acc"] < 0.6,
        "Levin ba %.3f vs twin ba %.3f (Levin-twin %+.4f CI%s)" % (
            o["levin"]["balanced_acc"], o["twin_balanced_acc"], o["levin_vs_twin"]["delta"], o["levin_vs_twin"]["ci"])))
    oks.append(check(
        "W2 goal-detection is HIGH-FIDELITY (Levin desiderative/intention/try classes): balanced-acc >= 0.9 with near-perfect non-goal rejection",
        o["levin"]["balanced_acc"] >= 0.9 and o["levin"]["reject_other"] >= 0.95,
        "balanced-acc %.3f recall %.3f reject-other %.3f" % (
            o["levin"]["balanced_acc"], o["levin"]["recall_goal"], o["levin"]["reject_other"])))
    oks.append(check(
        "W3 goal-detection is CLEARED as the upstream fidelity gap: it TIES a naive lexical floor on this gold (detection is easy here; the bottleneck is downstream coref/participant-binding, not detection)",
        not o["levin_beats_naive"],
        "Levin %.3f vs naive %.3f (Levin-naive %+.4f CI%s, beats=%s)" % (
            o["levin"]["balanced_acc"], o["naive"]["balanced_acc"], o["levin_vs_naive"]["delta"],
            o["levin_vs_naive"]["ci"], o["levin_beats_naive"])))
    n = sum(oks)
    print("=" * 92)
    print("%s (%d/%d)  verdict=%s" % ("ALL CHECKS PASS" if n == len(oks) else "SOME CHECKS FAILED",
                                      n, len(oks), o["verdict"]))
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
