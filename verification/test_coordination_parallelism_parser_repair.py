"""Scaffold-free witness: the FIXED PARSER prototype (brain-foundational, all-the-way-upstream).

The parse-aware scope resolver's residual is PARSER ATTACHMENT error, dominated by POS mistags. This witnesses
the brain-foundational post-parse repair (WordNet lexical-category + Frazier coordination parallelism +
do-support predicate expectation) and its HONEST outcome:

  R1 the repair FIRES: it makes many POS/attachment corrections over the reader's own front-end parse.
  R2 it RECOVERS negation RECALL to the surface-heuristic level (the structural resolver crosses the wall the
     parse errors created) with clean-affirmative over-negation still 0.
  R3 the HONEST tradeoff, closed the brain's way (NO training): the residual precision cost on
     complement/reduced-relative distractors is resolved by STORED LEXICAL KNOWLEDGE -- verb argument structure
     (subcategorization: a coordinated verb inside a matrix 'to-VP' complement is governed by the matrix's
     implicative meaning, not its negation) -- retrieved not learned (constraint-based parsing). The residual is
     MORE lexical knowledge to encode (foundation-buildable), never training. (A rigorous located result.)

Requires the front-end assets + EWT gold on disk.
Run: .venv/Scripts/python.exe verification/test_coordination_parallelism_parser_repair.py
"""
import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments.exp_coordination_parallelism_parser_repair_v1 import run, LAB_PATH, GOLD_PATH

PASS = FAIL = 0


def chk(name, cond, detail=""):
    global PASS, FAIL
    ok = bool(cond)
    print(("  PASS " if ok else "  FAIL ") + name + ("" if not detail else "  [%s]" % detail), flush=True)
    PASS += int(ok); FAIL += int(not ok)
    return ok


def main():
    if not (os.path.exists(LAB_PATH) and os.path.exists(GOLD_PATH)):
        print("  SKIP: front-end assets or EWT gold missing", flush=True)
        return 0
    out = run()
    chk("R1 brain-foundational repair FIRES (POS/attachment corrections over the front-end parse)",
        out["total_pos_attachment_repairs"] >= 10 and out["docs_repaired"] >= 8,
        "%d repairs over %d docs" % (out["total_pos_attachment_repairs"], out["docs_repaired"]))
    chk("R2 recovers negation RECALL to the surface level (structural resolver crosses the parse-error wall)",
        out["negated_recall"]["parsed_repaired"] >= out["negated_recall"]["surface"] - 1e-9
        and out["negated_recall"]["parsed_repaired"] > out["negated_recall"]["parsed_orig"]
        and out["over_negation_clean"]["parsed_repaired"] <= 0.02,
        "neg-recall orig %.4f -> repaired %.4f (surface %.4f); clean over-neg %.4f" % (
            out["negated_recall"]["parsed_orig"], out["negated_recall"]["parsed_repaired"],
            out["negated_recall"]["surface"], out["over_negation_clean"]["parsed_repaired"]))
    chk("R3 CLEAN WIN via STORED lexical knowledge (subcat + shared-subject), NOT training: parsed == surface",
        out["net_accuracy"]["parsed_repaired"] >= out["net_accuracy"]["surface"] - 1e-9
        and out["over_negation_distractor"]["parsed_repaired"] <= out["over_negation_distractor"]["surface"] + 1e-9
        and out["over_negation_clean"]["parsed_repaired"] <= 0.02,
        "parsed-repaired net %.4f == surface %.4f; distractor over-neg surface %.4f == repaired %.4f (verdict %s)" % (
            out["net_accuracy"]["parsed_repaired"], out["net_accuracy"]["surface"],
            out["over_negation_distractor"]["surface"], out["over_negation_distractor"]["parsed_repaired"],
            out["verdict"]))
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
