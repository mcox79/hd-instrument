"""Scaffold-free witness: JOINT extraction lifts END-TO-END temporal reasoning over the front-end's OWN extraction.

E1 the joint front-end lets the fixed reasoner ANSWER-CORRECTLY far more gold before/after pairs than the incumbent,
   CI-separated (the win is coverage: the reasoner can only answer pairs whose events were extracted).
E2 the reasoner-level info-free TWIN (shuffle the extracted event->text-position map) LOSES CI-separated -- the
   extracted ORDER structure is load-bearing, not a coverage artifact.
E3 the gold-event CEILING bounds the reasoner (the reasoner is fixed; extraction is the only variable).

Re-derives live from experiments.exp_joint_temporal_endtoend_v1.run(). Requires data/corpora/tb_dense.
Run: .venv/Scripts/python.exe verification/test_joint_temporal_endtoend.py
"""
import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
import experiments._hashseed_guard  # noqa: E402,F401  (pins PYTHONHASHSEED=0 -> reproducible parse)

from experiments.exp_joint_temporal_endtoend_v1 import run

PASS = FAIL = 0


def chk(name, cond, detail=""):
    global PASS, FAIL
    ok = bool(cond)
    print(("  PASS " if ok else "  FAIL ") + name + ("" if not detail else "  [%s]" % detail), flush=True)
    PASS += int(ok); FAIL += int(not ok)
    return ok


def main():
    r = run()
    chk("E1 joint beats incumbent end-to-end (answered-correct) CI-separated",
        r["margins"]["joint_vs_incumbent"]["ci_sep"] and r["margins"]["joint_vs_incumbent"]["delta"] > 0.10,
        "%.4f->%.4f +%.4f CI%s" % (r["incumbent"]["answered_correct"], r["joint_cop"]["answered_correct"],
                                   r["margins"]["joint_vs_incumbent"]["delta"], r["margins"]["joint_vs_incumbent"]["ci"]))
    chk("E2 reasoner-level TWIN (shuffled positions) loses CI-separated",
        r["margins"]["joint_vs_twin"]["ci_sep"],
        "twin %.4f vs joint %.4f (+%.4f CI%s)" % (r["twin"]["answered_correct"], r["joint_cop"]["answered_correct"],
                                                  r["margins"]["joint_vs_twin"]["delta"], r["margins"]["joint_vs_twin"]["ci"]))
    chk("E3 gold-event CEILING >= joint (extraction is the only variable; reasoner fixed)",
        r["gold_ceiling"]["answered_correct"] >= r["joint_cop"]["answered_correct"],
        "ceiling %.4f  joint %.4f  coverage %.3f->%.3f" % (
            r["gold_ceiling"]["answered_correct"], r["joint_cop"]["answered_correct"],
            r["incumbent"]["coverage"], r["joint_cop"]["coverage"]))
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
