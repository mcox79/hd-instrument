"""Scaffold-free witness: the bidirectional DOWNSTREAM payoff of the stronger pronoun pick, and the
premise-correcting located negative on the brief's NAMED downstream.

  D1  WHO-HAS-WHAT (the pronoun-BOUND dimension) RISES CI-separated when the deployed rolemass pick is
      swapped for the landed graded ACT-R pick (paired per-target bootstrap), and the info-free twin LOSES.
      NOTE: this cell uses the TRUE pronoun sentence index -> cross-checks the primary cell's p_sent proxy.
  D2  AFFECT experiencer (a brief-NAMED downstream) does NOT move CI-separated -- a rigorous located
      negative: affect is COMMON-NOUN-experiencer bound (83.5%% of experiencers are common nouns), not
      pronoun bound, so the pronoun-pick gain correctly does not propagate there.

Reads data/exp_coref_graded_downstream_whohaswhat_v1/metrics_full.json + .../downstream_affect_v1/metrics_full.json
Run: .venv/Scripts/python.exe verification/test_coref_graded_downstream.py
"""
import json
import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
WHW = os.path.join(_REPO, "data", "exp_coref_graded_downstream_whohaswhat_v1", "metrics_full.json")
AFF = os.path.join(_REPO, "data", "exp_coref_graded_downstream_affect_v1", "metrics_full.json")
PASS = FAIL = 0


def chk(name, cond, detail=""):
    global PASS, FAIL
    ok = bool(cond)
    print(("  PASS " if ok else "  FAIL ") + name + ("" if not detail else "  [%s]" % detail), flush=True)
    PASS += int(ok); FAIL += int(not ok)
    return ok


def main():
    w = json.load(open(WHW))["result"]
    pg = w["graded_minus_rolemass"]; pt = w["twin_minus_rolemass"]
    chk("D1 who-has-what RISES CI-separated (graded > deployed rolemass, paired) AND the twin LOSES",
        pg["CIsep"] and pg["ci"][0] > 0 and w["arms"]["twin"]["acc"] < w["arms"]["rolemass"]["acc"] - 0.10,
        "rolemass %.4f -> graded %.4f delta %+.4f ci[%.4f,%.4f] | twin %.4f" % (
            w["arms"]["rolemass"]["acc"], w["arms"]["graded"]["acc"], pg["delta"], pg["ci"][0], pg["ci"][1],
            w["arms"]["twin"]["acc"]))
    a = json.load(open(AFF))["result"]
    ag = a["graded_minus_deployed"]
    chk("D2 affect experiencer (brief-named) is a LOCATED NEGATIVE (not CI-separated) -- common-noun bound",
        not ag["ci_sep_above"],
        "feel_reliable dep %.4f -> grad %.4f delta %+.4f ci[%.4f,%.4f]" % (
            a["arms"]["deployed"]["feel_reliable"], a["arms"]["graded"]["feel_reliable"],
            ag["delta"], ag["lo"], ag["hi"]))
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
