"""Scaffold-free witness: the CONTEXTUAL goal-attachment mechanism WINS where the context-free means-end
bridge could not. The brain attaches a marker-less action to the goal it serves from the SITUATION, not a
verb->goal lookup; conditioning on the situation makes the info-free twin LOSE CI-separated.

  W1  the CONTEXTUAL mechanism BEATS the info-free shuffled-situation twin CI-separated on real narrative
      (ALL real extractions, both K1 and K3)
  W2  the context-free ATOMIC means-end bridge (the brief's mechanism) does NOT (~ twin) on the same items
      -> the win comes from the situation, not the means-end table
  W3  from-source unit (spaCy-free): a danger/escape SITUATION relates more to 'escape' than to 'cook'

Reads data/exp_contextual_goal_attachment_v1/metrics_full.json + a from-source unit.
Run: .venv/Scripts/python.exe verification/test_contextual_goal_attachment.py
"""
import json
import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

METRICS = os.path.join(_REPO, "data", "exp_contextual_goal_attachment_v1", "metrics_full.json")
PASS = FAIL = 0


def chk(name, cond, detail=""):
    global PASS, FAIL
    ok = bool(cond)
    print(("  PASS " if ok else "  FAIL ") + name + ("" if not detail else "  [%s]" % detail), flush=True)
    PASS += int(ok); FAIL += int(not ok)
    return ok


def main():
    r = json.load(open(METRICS))["result"]
    allp = r["ALL_extractions"]
    for K in ("K1", "K3"):
        x = allp[K]; c = x["CONTEXTUAL"]
        chk("W1 CONTEXTUAL beats the info-free twin CI-separated on real narrative (%s)" % K,
            x["beats_twin_ci_sep"] and c["ci"][0] > x["twin_null"]["p95"],
            "ctx %.3f ci_lo %.3f vs twin p95 %.3f" % (c["acc"], c["ci"][0], x["twin_null"]["p95"]))
        chk("W2 context-free ATOMIC bridge does NOT clearly beat the twin (%s) -> the win is the situation" % K,
            x["atomic_bridge_baseline"] <= x["twin_null"]["p95"] + 0.03,
            "atomic %.3f vs twin p95 %.3f" % (x["atomic_bridge_baseline"], x["twin_null"]["p95"]))

    import experiments.exp_contextual_goal_attachment_v1 as T
    assoc = T.Assoc()
    it = {"situation": ["trap", "door", "lock", "fear", "dark", "run", "knife"]}
    s_esc = T.contextual_score(assoc, it, "escape")
    s_cook = T.contextual_score(assoc, it, "cook")
    chk("W3 a danger/escape SITUATION relates more to 'escape' than to 'cook' (contextual sanity)",
        s_esc is not None and s_cook is not None and s_esc > s_cook,
        "escape %.3f > cook %.3f" % (s_esc or -9, s_cook or -9))

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
