"""Scaffold-free witness: the two deepening drills (third-reasoner extraction lever + nominal-residual localization).

D1 THIRD-REASONER: the joint front-end recovers the OUTCOME event on EVERY OCC appraisal item (dense+sparse) where the
   incumbent's tense-gate drops some -- the brain-foundational extraction lever for the appraisal reasoner (the brain
   represents the outcome event, then appraises it). The residual is the appraisal SOLVED's semantic-matching wall.
D2 NOMINAL residual is SEMANTIC, not syntactic: Grimshaw's argument-structure gate raises precision but CRUSHES
   NOUN-event recall (news event-nominals appear bare), confirming the precision residual belongs to the WSD/context
   channel -- a drilled, evidence-backed located negative.

Re-derives live from experiments.exp_joint_third_reasoner_and_nominal_wsd_v1.run().
Run: .venv/Scripts/python.exe verification/test_joint_third_reasoner_and_nominal_wsd.py
"""
import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
import experiments._hashseed_guard  # noqa: E402,F401

from experiments.exp_joint_third_reasoner_and_nominal_wsd_v1 import run

PASS = FAIL = 0


def chk(name, cond, detail=""):
    global PASS, FAIL
    ok = bool(cond)
    print(("  PASS " if ok else "  FAIL ") + name + ("" if not detail else "  [%s]" % detail), flush=True)
    PASS += int(ok); FAIL += int(not ok)
    return ok


def main():
    r = run()
    ap = r["appraisal"]
    dense = ap.get("occ_appraisal_gold_v1.jsonl")
    sparse = ap.get("occ_appraisal_gold_sparse_v1.jsonl")
    chk("D1 joint recovers outcome events on ALL appraisal items where incumbent drops some (3rd-reasoner lever)",
        dense and sparse and dense["joint_has_outcome_event"] == dense["n"]
        and sparse["joint_has_outcome_event"] == sparse["n"]
        and dense["incumbent_has_outcome_event"] < dense["n"] and sparse["incumbent_has_outcome_event"] < sparse["n"],
        "dense inc %d/%d->joint %d/%d | sparse inc %d/%d->joint %d/%d" % (
            dense["incumbent_has_outcome_event"], dense["n"], dense["joint_has_outcome_event"], dense["n"],
            sparse["incumbent_has_outcome_event"], sparse["n"], sparse["joint_has_outcome_event"], sparse["n"]))
    nd = r["nominal_wsd"]
    chk("D2 nominal residual is SEMANTIC: Grimshaw gate raises precision but crushes NOUN-event recall (>0.4 drop)",
        nd["nom_wordnet_grimshaw"]["precision"] > nd["nom_wordnet"]["precision"]
        and nd["nom_wordnet"]["noun_event_recall"] - nd["nom_wordnet_grimshaw"]["noun_event_recall"] > 0.4,
        "NOUN-event recall %.3f -> %.3f  precision %.3f -> %.3f" % (
            nd["nom_wordnet"]["noun_event_recall"], nd["nom_wordnet_grimshaw"]["noun_event_recall"],
            nd["nom_wordnet"]["precision"], nd["nom_wordnet_grimshaw"]["precision"]))
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
