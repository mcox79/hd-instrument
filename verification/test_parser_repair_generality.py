"""Scaffold-free witness: the HONEST generality check on the parse repair -- a negative that PREVENTS a mistake.

The parse repair matches the surface operator ON THE NEGATION GOLD (which is enriched for coordination-negation
constructions), but measured against GOLD UPOS on general modern UD-EWT it is NET-NEGATIVE: the WordNet-verb-sense
retag over-fires (most nouns/adjectives have a verb sense), breaking far more correct tags than it fixes.

  G1 on general UD-EWT gold, the repair LOWERS POS accuracy (net negative) and its retag PRECISION is very low
     (breaks >> fixes) -- so it must NOT be deployed as a default parser pass.
  G2 => the SURFACE operator (which never touches the parse) is the correct GENERAL primary; the parse-aware +
     repair path is a research demonstration that the wall is crossable IN PRINCIPLE. The genuine general parser
     fix needs a PRECISE lexical resource (VerbNet subcategorization frames + frequency priors), a FOUNDATION
     build -- NOT a permissive WordNet-verb-sense heuristic, and NOT training.

Requires UD-EWT test on disk. Re-derives live from experiments.exp_parser_repair_pos_recovery_v1.
Run: .venv/Scripts/python.exe verification/test_parser_repair_generality.py
"""
import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments.exp_parser_repair_pos_recovery_v1 import run, UD_TEST

PASS = FAIL = 0


def chk(name, cond, detail=""):
    global PASS, FAIL
    ok = bool(cond)
    print(("  PASS " if ok else "  FAIL ") + name + ("" if not detail else "  [%s]" % detail), flush=True)
    PASS += int(ok); FAIL += int(not ok)
    return ok


def main():
    if not os.path.exists(UD_TEST):
        print("  SKIP: UD-EWT test not on disk", flush=True)
        return 0
    out = run(2000)
    chk("G1 repair is NET-NEGATIVE on general UD-EWT gold POS (low retag precision, breaks >> fixes)",
        out["net_pos_correct_delta"] < 0 and out["repair_broke"] > out["repair_fixed"]
        and out["repair_precision_fixed"] < 0.25,
        "POS acc base %.4f -> repaired %.4f; retags fixed %d broke %d (precision %.3f)" % (
            out["pos_accuracy"]["base"], out["pos_accuracy"]["repaired"], out["repair_fixed"],
            out["repair_broke"], out["repair_precision_fixed"]))
    chk("G2 verdict = NOT general -> do NOT default the repair; surface operator is the general primary",
        out["verdict"] == "REPAIR_NOT_GENERAL", "verdict=%s" % out["verdict"])
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
