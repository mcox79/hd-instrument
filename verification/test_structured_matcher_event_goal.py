"""Scaffold-free witness: the structured SIGN matcher beats the polarity-blind hub + shuffled-KB twin on event<->goal.

EG1 STRUCTURED signed accuracy beats the DISTRIBUTIONAL-HUB baseline CI-separated on a relatedness-matched gold.
EG2 STRUCTURED beats the info-free SHUFFLED-KB twin CI-separated (the EDGES carry the sign, not just "having a KB").
EG3 POLARITY ISOLATION: on the antonym-thwart subset the hub is at/below chance while the structured matcher is high
    -- the sign comes from the edge, not the similarity (rel(win,lose) ~= rel(sell,buy), matched high relatedness).

Re-derives live from experiments.exp_structured_matcher_event_goal_v1.run(). Requires nltk WordNet+FrameNet + the hub.
Run: .venv/Scripts/python.exe verification/test_structured_matcher_event_goal.py
"""
import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
import experiments._hashseed_guard  # noqa: E402,F401  (pins PYTHONHASHSEED=0 -> reproducible WordNet/ConceptNet sampling)

from experiments.exp_structured_matcher_event_goal_v1 import run

PASS = FAIL = 0


def chk(name, cond, detail=""):
    global PASS, FAIL
    ok = bool(cond)
    print(("  PASS " if ok else "  FAIL ") + name + ("" if not detail else "  [%s]" % detail), flush=True)
    PASS += int(ok); FAIL += int(not ok)
    return ok


def main():
    r = run()
    chk("EG1 structured beats polarity-blind HUB baseline CI-separated",
        r["margins"]["vs_hub"]["ci_sep"] and r["margins"]["vs_hub"]["delta"] > 0.3,
        "structured %.4f vs hub %.4f  +%.4f CI%s" % (r["acc"]["structured"], r["acc"]["hub_baseline"],
                                                     r["margins"]["vs_hub"]["delta"], r["margins"]["vs_hub"]["ci"]))
    chk("EG2 structured beats info-free SHUFFLED-KB twin CI-separated",
        r["margins"]["vs_twin"]["ci_sep"] and r["margins"]["vs_twin"]["delta"] > 0.3,
        "twin %.4f  +%.4f CI%s" % (r["acc"]["twin"], r["margins"]["vs_twin"]["delta"], r["margins"]["vs_twin"]["ci"]))
    ant = r["by_slice"]["antonym_thwart"]
    chk("EG3 polarity isolation: hub at/below chance on antonym subset, structured high",
        ant["hub_baseline"] <= 0.10 and ant["structured"] >= 0.85,
        "antonym slice: hub %.4f vs structured %.4f (n=%d)" % (ant["hub_baseline"], ant["structured"], ant["n"]))
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
