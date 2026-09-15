"""Scaffold-free witness: the EPISODIC-SIMULATION organ shows the FIRST discriminative signal on the open-ended scene
tail -- confirming Barsalou experiential simulation is the faithful mechanism (where the KB + pairwise hub failed).

SIM1 EPISODIC (ROCStories NB log-odds) DISCRIMINATES matched vs shuffled-episode by a clear margin (pairwise >= 0.60
     and >= shuffled + 0.15) -- the scene->goal link IS recoverable from accumulated narrative experience.
SIM2 EPISODIC top-1 is well above chance (>= 2x) -- and above the hub-aggregate's compositional-simulation-lite.

Honest scope: n is small (hand-constructed OCC sparse gold, only the cleanly-parseable items) and absolute accuracy is
LOW -- this is a working prototype of the missing faculty + a correct DIRECTION, underpowered by the small gold +
ROCStories vocabulary coverage; a production organ needs a larger episodic corpus + a powered natural-narrative gold.

Re-derives live from experiments.exp_scene_simulation_episodic_v1.run(). Requires data/corpora/roc_stories + OCC sparse gold + hub.
Run: .venv/Scripts/python.exe verification/test_scene_simulation_episodic.py
"""
import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
import experiments._hashseed_guard  # noqa: E402,F401

from experiments.exp_scene_simulation_episodic_v1 import run

PASS = FAIL = 0


def chk(name, cond, detail=""):
    global PASS, FAIL
    ok = bool(cond)
    print(("  PASS " if ok else "  FAIL ") + name + ("" if not detail else "  [%s]" % detail), flush=True)
    PASS += int(ok); FAIL += int(not ok)
    return ok


def main():
    r = run()
    ep, sh, hb = r["episodic_mean"], r["episodic_shuffled_max"], r["hub_agg"]
    chk("SIM1 episodic DISCRIMINATES matched vs shuffled-episode (pairwise>=0.60 and >= shuffled+0.15)",
        ep["pairwise"] >= 0.60 and ep["pairwise"] >= sh["pairwise"] + 0.15,
        "episodic pairwise %.3f vs shuffled %.3f" % (ep["pairwise"], sh["pairwise"]))
    chk("SIM2 episodic top-1 >= 2x chance and >= hub-aggregate",
        ep["top1"] >= 2 * r["chance_top1"] and ep["top1"] >= hb["top1"] - 1e-9,
        "episodic top-1 %.3f (chance %.3f, hub %.3f)" % (ep["top1"], r["chance_top1"], hb["top1"]))
    print("\n%d/%d checks passed" % (PASS, PASS + FAIL), flush=True)
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(main())


# --- pytest-collectable wrapper (pri 128, mechanical; see notes/problems/447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest/PROBLEM.md) ---
import pytest as _pri128_pytest
from verification._witness_wrap import _run_main_as_test as _pri128_run


@_pri128_pytest.mark.corpus
def test_witness():
    _code, _out = _pri128_run(main)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
