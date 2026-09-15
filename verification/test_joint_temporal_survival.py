"""Scaffold-free witness: JOINT temporal extraction lifts WHOLE-SUBGRAPH SURVIVAL on TB-Dense (modern dense gold).

T1 the incumbent tense-gated extractor is the FLOOR and it is LOW: overall event recall ~0.32, whole-subgraph
   survival ~0.10 (the exponent wall).
T2 the joint (tense-agnostic + copular/stative) pass beats the incumbent CI-separated on whole-subgraph survival.
T3 the info-free TWIN (random same-size event recovery) LOSES CI-separated (recovered STRUCTURE is load-bearing).
T4 the tense-gate is the mechanism (same-tagger tense-agnostic control also clears it -> not a tagger artifact);
   the COPULAR channel specifically lifts stative-touching OVERLAP edges CI-separated (the named P2 lever).

Re-derives live from experiments.exp_joint_temporal_survival_v1.run(). Requires data/corpora/tb_dense.
Run: .venv/Scripts/python.exe verification/test_joint_temporal_survival.py
"""
import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
import experiments._hashseed_guard  # noqa: E402,F401  (pins PYTHONHASHSEED=0 -> reproducible parse)

from experiments.exp_joint_temporal_survival_v1 import run

PASS = FAIL = 0


def chk(name, cond, detail=""):
    global PASS, FAIL
    ok = bool(cond)
    print(("  PASS " if ok else "  FAIL ") + name + ("" if not detail else "  [%s]" % detail), flush=True)
    PASS += int(ok); FAIL += int(not ok)
    return ok


def main():
    r = run()
    sv = r["survival"]
    mg = r["margins"]
    ov = r["overlap_edges"]

    chk("T1 incumbent FLOOR is low (recall<0.40, survival<0.15)",
        r["recall"]["incumbent"] < 0.40 and sv["incumbent"]["rate"] < 0.15,
        "recall %.3f survival %.4f" % (r["recall"]["incumbent"], sv["incumbent"]["rate"]))
    chk("T2 joint beats incumbent CI-separated on whole-subgraph survival",
        mg["joint_cop_vs_incumbent"]["ci_sep"] and mg["joint_cop_vs_incumbent"]["delta"] > 0.15,
        "%.4f->%.4f  +%.4f CI%s" % (sv["incumbent"]["rate"], sv["joint_cop"]["rate"],
                                    mg["joint_cop_vs_incumbent"]["delta"], mg["joint_cop_vs_incumbent"]["ci"]))
    chk("T3 info-free TWIN loses CI-separated (structure load-bearing)",
        mg["joint_cop_vs_twin"]["ci_sep"] and sv["joint_twin"]["rate"] < sv["joint_cop"]["rate"],
        "twin %.4f vs joint %.4f  +%.4f CI%s" % (sv["joint_twin"]["rate"], sv["joint_cop"]["rate"],
                                                 mg["joint_cop_vs_twin"]["delta"], mg["joint_cop_vs_twin"]["ci"]))
    chk("T4a tense-gate is the mechanism (same-tagger tense-agnostic control also clears the floor)",
        sv["nltk_tenseagn"]["rate"] > sv["incumbent"]["rate"] + 0.15,
        "nltk_tenseagn %.4f vs incumbent %.4f" % (sv["nltk_tenseagn"]["rate"], sv["incumbent"]["rate"]))
    chk("T4b COPULAR channel lifts stative-touching OVERLAP edges CI-separated",
        ov["cop_channel_on_stative"]["ci_sep"] and ov["cop_channel_on_stative"]["delta"] > 0,
        "joint_verb %.4f -> joint_cop %.4f (+%.4f CI%s)" % (
            ov["joint_verb"]["stative_touch"], ov["joint_cop"]["stative_touch"],
            ov["cop_channel_on_stative"]["delta"], ov["cop_channel_on_stative"]["ci"]))
    chk("T5 WordNet NOMINAL channel lifts survival further, CI-separated over incumbent",
        mg["joint_nom_vs_incumbent"]["ci_sep"] and sv["joint_nom"]["rate"] > sv["joint_cop"]["rate"],
        "joint_nom %.4f (+%.4f CI%s over incumbent) vs joint_cop %.4f" % (
            sv["joint_nom"]["rate"], mg["joint_nom_vs_incumbent"]["delta"],
            mg["joint_nom_vs_incumbent"]["ci"], sv["joint_cop"]["rate"]))

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
