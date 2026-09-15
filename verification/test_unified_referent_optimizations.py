"""Scaffold-free witness: ALL brain-foundational optimizations tested; the dev-adopted set MAINTAINS the headline
(the base unified referent was already near the no-LLM frontier), and the rejected ones are honestly located.

  P1  the dev-adopted OPTIMIZED config still lifts BOTH consumers CI-separated over the separate-tracking reader,
      with the info-free twin LOSING and NO-regress on named coref (the optimizations do not break the result).
  P2  HONEST optimization ledger across the WHOLE within-component brain-foundational family (cue params + Nref
      writeback + working-memory bound): animacy redundant (0.0); GRADED Nref write net-NEGATIVE (the +0.027 LitBank
      who-did-what does not transfer); CONFIDENCE-GATED writeback net-NEGATIVE (abstaining loses correct low-confidence
      salience); a shallower ACT-R decay d=1.5 REGRESSES the pronoun pick (a kb trade). The component is saturated; the
      remaining headroom is UPSTREAM clustering (the P2 role assigner) + barred world knowledge, not more knobs here.

Reads data/exp_unified_referent_optimizations_gum_v1/metrics_full.json.
Run: .venv/Scripts/python.exe verification/test_unified_referent_optimizations.py
"""
import json
import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
M = os.path.join(_REPO, "data", "exp_unified_referent_optimizations_gum_v1", "metrics_full.json")
PASS = FAIL = 0


def chk(name, cond, detail=""):
    global PASS, FAIL
    ok = bool(cond)
    print(("  PASS " if ok else "  FAIL ") + name + ("" if not detail else "  [%s]" % detail), flush=True)
    PASS += int(ok); FAIL += int(not ok)
    return ok


def main():
    r = json.load(open(M))["result"]
    T = r["TEST"]; dev = r["dev_single_report"]
    pr, kb, nm = T["pronoun"], T["kb_hardlink"], T["name"]
    chk("P1 dev-adopted OPTIMIZED config still lifts pronoun+kb CI-sep vs separate, twin loses, name no-regress",
        pr["CIsep_vs_separate"] and kb["CIsep_vs_separate"] and pr["twin_loses"] and kb["twin_loses"]
        and nm["opt_minus_separate"] > -0.02,
        "adopted %s | PRON opt %.4f vs sep %+.4f | KB opt %.4f vs sep %+.4f | NAME %+.4f" % (
            r["adopted_config"], pr["OPTIMIZED"], pr["opt_minus_separate"], kb["OPTIMIZED"],
            kb["opt_minus_separate"], nm["opt_minus_separate"]))
    chk("P2 HONEST ledger (whole family): animacy redundant, graded+conf-gate net-negative, decay=1.5 regresses pronoun",
        abs(dev["+animacy"]["obj_gain"]) < 1e-6 and dev["+graded"]["obj_gain"] < 0
        and dev["+confgate0.5"]["obj_gain"] < 0 and dev["decay=1.5"]["pron_delta"] < -0.005,
        "animacy %+.4f | graded %+.4f | conf-gate %+.4f | decay=1.5 pron_delta %+.4f" % (
            dev["+animacy"]["obj_gain"], dev["+graded"]["obj_gain"], dev["+confgate0.5"]["obj_gain"],
            dev["decay=1.5"]["pron_delta"]))
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
