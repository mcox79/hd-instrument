"""Scaffold-free witness: the swept ACT-R decay is optimized with a proper DEV/TEST split.

  O1  the PINNED brain-foundational default d=2.0 is near-optimal for the PRONOUN pick: a DEV-tuned decay does
      NOT beat it on held-out TEST (no free headroom / no over-tuning on the primary consumer).
  O2  a DEV-validated shallower decay (d*=1.5) IMPROVES the ENTITY-KB hard-link on held-out TEST (a slower base-
      level decay keeps the frequently-mentioned named protagonist activated) -- a legitimate per-corpus refinement.

Reads data/exp_unified_referent_optimize_gum_v1/metrics_full.json.
Run: .venv/Scripts/python.exe verification/test_unified_referent_optimize.py
"""
import json
import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
M = os.path.join(_REPO, "data", "exp_unified_referent_optimize_gum_v1", "metrics_full.json")
PASS = FAIL = 0


def chk(name, cond, detail=""):
    global PASS, FAIL
    ok = bool(cond)
    print(("  PASS " if ok else "  FAIL ") + name + ("" if not detail else "  [%s]" % detail), flush=True)
    PASS += int(ok); FAIL += int(not ok)
    return ok


def main():
    r = json.load(open(M))["result"]
    pr, kb = r["pronoun"], r["kb_hardlink"]
    chk("O1 PINNED d=%.1f near-optimal for PRONOUN pick: dev-tuned does NOT beat it on TEST" % r["pinned_d"],
        not pr["tuning_helps_on_test"],
        "test pinned %.4f vs devtuned(d=%.1f) %.4f (%+.4f)" % (
            pr["test_pinned"], r["dev_best_d"], pr["test_devtuned"], pr["tuned_minus_pinned"]))
    chk("O2 DEV-validated d*=%.1f IMPROVES the ENTITY-KB hard-link on held-out TEST" % r["dev_best_d"],
        kb["tuning_helps_on_test"] and kb["tuned_minus_pinned"] > 0.0,
        "test pinned %.4f vs devtuned %.4f (%+.4f ci%s)" % (
            kb["test_pinned"], kb["test_devtuned"], kb["tuned_minus_pinned"], kb["ci"]))
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
