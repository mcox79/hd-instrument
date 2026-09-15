"""Scaffold-free witness: the OPEN-ENDED scene-inference tail is a RIGOROUS LOCATED NEGATIVE (properly controlled).

SC1 the ConceptNet script/causal bridge is NON-DISCRIMINATIVE: it connects a scene to a MISMATCHED (shuffled) goal
    almost as often as to the correct goal (matched - shuffled is small) -- so a 'connection' is promiscuous graph
    reachability, NOT scene inference.
SC2 the distributional hub fuzzy bridge is near-zero -- it cannot connect these open-ended scenes to their goals either.
    => the open-ended scene tail needs a SIMULATION / episodic faculty (Barsalou), NOT a static causal KB and NOT the
    hub -- a distinct organ. A rigorous located negative is a full pass.

Re-derives live from experiments.exp_scene_inference_conceptnet_v1.run(). Requires ConceptNet subset + the OCC sparse gold.
Run: .venv/Scripts/python.exe verification/test_scene_inference_located_negative.py
"""
import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
import experiments._hashseed_guard  # noqa: E402,F401

from experiments.exp_scene_inference_conceptnet_v1 import run

PASS = FAIL = 0


def chk(name, cond, detail=""):
    global PASS, FAIL
    ok = bool(cond)
    print(("  PASS " if ok else "  FAIL ") + name + ("" if not detail else "  [%s]" % detail), flush=True)
    PASS += int(ok); FAIL += int(not ok)
    return ok


def main():
    r = run()
    n = r["n"]
    matched = r["conceptnet_script_connected"]
    shuffled = r["conceptnet_SHUFFLED_goal"]
    disc = (matched - shuffled) / n
    chk("SC1 ConceptNet script bridge is NON-discriminative (matched ~= shuffled; signal < 0.20)",
        disc < 0.20,
        "matched %d/%d vs shuffled %d/%d -> discriminative %.2f" % (matched, n, shuffled, n, disc))
    chk("SC2 hub fuzzy bridge near-zero on the open-ended scene tail",
        r["hub_fuzzy_connected"] / n <= 0.10,
        "hub %d/%d" % (r["hub_fuzzy_connected"], n))
    print("\n%d/%d checks passed" % (PASS, PASS + FAIL), flush=True)
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(main())


# --- pytest-collectable wrapper (pri 128, mechanical; see notes/problems/447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest/PROBLEM.md) ---
import pytest as _pri128_pytest
from verification._witness_wrap import _run_main_as_test as _pri128_run


@_pri128_pytest.mark.fast
def test_witness():
    _code, _out = _pri128_run(main)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
