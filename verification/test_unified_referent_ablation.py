"""Scaffold-free witness: WHICH cue carries the unified-referent lift, and that the UPSTREAM parser must be
brain-foundational too.

  A1  PRONOUN pick: GENDER agreement is load-bearing (leave-one-out gain CI-sep) -- the unified referent
      completes gender across mention types; the aliaser is register-NEUTRAL on modern text (~0, not CI-sep),
      corroborating why names do not lift on GUM.
  A2  ENTITY-KB HARD-LINK: ACT-R grammatical-PROMINENCE salience is load-bearing (leave-one-out gain CI-sep)
      -- prominence routes the pronoun to the salient NAMED protagonist so the fact files under the name.
  A3  UPSTREAM FIDELITY: replacing gold grammatical roles with POSITIONAL roles (the live reader's
      _assign_roles) drops the entity-KB hard-link CI-sep -> the downstream benefit REQUIRES a brain-foundational
      upstream role assigner (the filed Competition-Model problem).

Reads data/exp_unified_referent_ablation_gum_v1/metrics_full.json.
Run: .venv/Scripts/python.exe verification/test_unified_referent_ablation.py
"""
import json
import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
M = os.path.join(_REPO, "data", "exp_unified_referent_ablation_gum_v1", "metrics_full.json")
PASS = FAIL = 0


def chk(name, cond, detail=""):
    global PASS, FAIL
    ok = bool(cond)
    print(("  PASS " if ok else "  FAIL ") + name + ("" if not detail else "  [%s]" % detail), flush=True)
    PASS += int(ok); FAIL += int(not ok)
    return ok


def main():
    A = json.load(open(M))["result"]["arms"]
    p = A["pronoun"]; k = A["kb_hardlink"]
    pg = p["leave_one_out"]["U_minus_gender"]; pa = p["leave_one_out"]["U_minus_aliaser"]
    ka = k["leave_one_out"]["U_minus_actr"]; kr = k["leave_one_out"]["U_positional_roles"]
    chk("A1 PRONOUN: gender agreement is load-bearing (LOO CI-sep); aliaser is register-neutral on modern text",
        pg["CIsep"] and (not pa["CIsep"]),
        "-gender %+.4f ci%s (CIsep=%s) | -aliaser %+.4f (CIsep=%s)" % (
            pg["loo_gain"], pg["ci"], pg["CIsep"], pa["loo_gain"], pa["CIsep"]))
    chk("A2 KB-HARDLINK: ACT-R grammatical-prominence salience is load-bearing (LOO CI-sep)",
        ka["CIsep"] and ka["loo_gain"] > 0.05,
        "-ACTR(pure recency) %+.4f ci%s CIsep=%s" % (ka["loo_gain"], ka["ci"], ka["CIsep"]))
    chk("A3 UPSTREAM: positional roles (live _assign_roles) drop the KB hard-link CI-sep vs gold grammatical roles",
        kr["CIsep"] and kr["loo_gain"] > 0.03,
        "gold_roles - positional = %+.4f ci%s CIsep=%s" % (kr["loo_gain"], kr["ci"], kr["CIsep"]))
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
