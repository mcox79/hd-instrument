"""Scaffold-free witness: ONE unified discourse referent lifts >= 2 downstream consumers on MODERN gold (GUM).

  U1  PRONOUN PICK lifts CI-separated over the STRONGEST floor actually run, and the info-free twin
      (shuffled identity evidence) LOSES.
  U2  ENTITY-KB HARD-LINK (a named entity's pronoun resolves to the referent CARRYING the name) lifts
      CI-separated over the separate-tracking reader, twin LOSES. -> the bar's 2nd consumer.
  U3  NAME resolution NO-REGRESS vs the separate-tracking reader.
  U4  HONEST located negative: COMMON-noun resolution does NOT beat blind head-identity (Ariel accessibility:
      definite NPs resolve by head/recency, not the salience/gender unification completes).
  U5  headroom: the ORACLE-unified (gold clusters) ceiling is above the unified arm (clustering error remains).

Reads data/exp_unified_referent_gum_v1/metrics_full.json (regenerate: experiments/exp_unified_referent_gum_v1.py --run).
Run: .venv/Scripts/python.exe verification/test_unified_referent_gum.py
"""
import json
import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
M = os.path.join(_REPO, "data", "exp_unified_referent_gum_v1", "metrics_full.json")
PASS = FAIL = 0


def chk(name, cond, detail=""):
    global PASS, FAIL
    ok = bool(cond)
    print(("  PASS " if ok else "  FAIL ") + name + ("" if not detail else "  [%s]" % detail), flush=True)
    PASS += int(ok); FAIL += int(not ok)
    return ok


def main():
    T = json.load(open(M))["result"]["TEST"]
    pr, kb, cm, nm = T["pronoun"], T["kb_hardlink"], T["common"], T["name"]
    prf = pr["unified_minus_STRONGEST_FLOOR"]
    chk("U1 PRONOUN PICK lifts CI-sep over strongest floor AND twin loses",
        prf["CIsep"] and pr["unified_minus_twin"]["twin_loses"],
        "unified %.4f vs FLOOR[%s] %.4f: %+.4f ci%s | twin %.4f (uni-twin %+.4f)" % (
            pr["unified"]["acc"], prf["floor"], prf["floor_acc"], prf["delta"], prf["ci"],
            pr["twin"]["acc"], pr["unified_minus_twin"]["delta"]))
    chk("U2 ENTITY-KB HARD-LINK lifts CI-sep over the separate reader AND twin loses",
        kb["unified_minus_separate"]["CIsep"] and kb["unified_minus_twin"]["twin_loses"],
        "unified %.4f vs sep %.4f: %+.4f ci%s | twin %.4f" % (
            kb["unified"]["acc"], kb["separate"]["acc"], kb["unified_minus_separate"]["delta"],
            kb["unified_minus_separate"]["ci"], kb["twin"]["acc"]))
    chk("U3 NAME resolution NO-REGRESS vs the separate-tracking reader",
        nm["unified_minus_separate"]["ci"][0] > -0.02,
        "unified %.4f vs sep %.4f (%+.4f ci%s)" % (
            nm["unified"]["acc"], nm["separate"]["acc"], nm["unified_minus_separate"]["delta"],
            nm["unified_minus_separate"]["ci"]))
    chk("U4 HONEST: COMMON-noun does NOT beat blind head-identity (Ariel: definite NP = recency/identity, not salience)",
        cm["unified"]["acc"] <= cm["string_identity"]["acc"] + 0.005,
        "unified %.4f vs string-identity floor %.4f (%+.4f)" % (
            cm["unified"]["acc"], cm["string_identity"]["acc"], cm["unified"]["acc"] - cm["string_identity"]["acc"]))
    chk("U5 headroom: oracle-unified ceiling above the unified arm (residual clustering error)",
        pr["oracle"]["acc"] > pr["unified"]["acc"],
        "pronoun oracle %.4f > unified %.4f" % (pr["oracle"]["acc"], pr["unified"]["acc"]))
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
