"""Scaffold-free witness: END-TO-END through the ACTUAL solved reasoner (connective+tense), not the iconicity proxy.

R1 the joint front-end (tense-agnostic + copular) beats the incumbent through the REAL reasoner, CI-separated.
R2 the WordNet-NOMINAL front-end reaches near the gold-event CEILING end-to-end (answered-correct >= 0.85 x ceiling),
   and its conditional accuracy does NOT drop vs joint_cop (the nominal over-extraction does not degrade the reasoner).
R3 the info-free TWIN loses CI-separated.

Re-derives live from experiments.exp_joint_temporal_realreasoner_v1.run(). Requires data/corpora/tb_dense.
Run: .venv/Scripts/python.exe verification/test_joint_temporal_realreasoner.py
"""
import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
import experiments._hashseed_guard  # noqa: E402,F401

from experiments.exp_joint_temporal_realreasoner_v1 import run

PASS = FAIL = 0


def chk(name, cond, detail=""):
    global PASS, FAIL
    ok = bool(cond)
    print(("  PASS " if ok else "  FAIL ") + name + ("" if not detail else "  [%s]" % detail), flush=True)
    PASS += int(ok); FAIL += int(not ok)
    return ok


def main():
    r = run()
    chk("R1 joint_cop beats incumbent through the REAL reasoner CI-separated",
        r["margins"]["joint_cop_vs_incumbent"]["ci_sep"],
        "%.4f->%.4f +%.4f CI%s" % (r["incumbent"]["answered_correct"], r["joint_cop"]["answered_correct"],
                                   r["margins"]["joint_cop_vs_incumbent"]["delta"], r["margins"]["joint_cop_vs_incumbent"]["ci"]))
    ceil = r["gold_ceiling"]["answered_correct"]
    chk("R2 WordNet-NOMINAL reaches >=0.85x the gold ceiling end-to-end; cond-acc not degraded",
        r["joint_nom"]["answered_correct"] >= 0.85 * ceil and r["joint_nom"]["conditional_acc"] >= r["joint_cop"]["conditional_acc"] - 0.03,
        "joint_nom %.4f (ceiling %.4f) cond-acc nom %.4f vs cop %.4f" % (
            r["joint_nom"]["answered_correct"], ceil, r["joint_nom"]["conditional_acc"], r["joint_cop"]["conditional_acc"]))
    chk("R3 info-free TWIN loses CI-separated",
        r["margins"]["joint_cop_vs_twin"]["ci_sep"],
        "+%.4f CI%s" % (r["margins"]["joint_cop_vs_twin"]["delta"], r["margins"]["joint_cop_vs_twin"]["ci"]))
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
