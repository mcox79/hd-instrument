"""Scaffold-free witness: the UPSTREAM deepening for the coref pick -- where the residual wall is, which
upstream is brain-foundational and fixable, and which is a located negative.

  U1  ENTITY UNIFICATION is the next brain-foundational lever: unifying an entity's surface variants into
      ONE representation (oracle gold-cluster grouping) lifts the graded pick CI-separated, named no-regress.
  U2  GENDER PROPAGATION with a hard agreement filter is a LOCATED NEGATIVE on the live FRAGMENTED overlay:
      it scores BELOW the graded pick and ~= the random-gender twin (error propagation, not signal) -> do
      NOT wire it standalone; it is COUPLED to unification + a recall-safe (soft) agreement constraint.
  A1  the residual above the pick is the DOCUMENTED individuation wall, not pool coverage: with oracle
      gender the structurally-dominated errors dominate and gold-not-in-pool is tiny.
  G1  the gender ladder confirms naive name-gender filtering HURTS (over-narrows) and incremental gender
      establishment recovers it -- but only meaningfully on a clean/unified pool.

Reads the three deepening metrics files.
Run: .venv/Scripts/python.exe verification/test_coref_graded_deepening.py
"""
import json
import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LT = os.path.join(_REPO, "data", "exp_coref_graded_live_transfer_v1", "metrics_full.json")
AN = os.path.join(_REPO, "data", "exp_coref_graded_residual_anatomy_v1", "metrics_full.json")
GP = os.path.join(_REPO, "data", "exp_coref_incremental_gender_prototype_v1", "metrics_full.json")
DR = os.path.join(_REPO, "data", "exp_coref_graded_upstream_drill_v1", "metrics_full.json")
PASS = FAIL = 0


def chk(name, cond, detail=""):
    global PASS, FAIL
    ok = bool(cond)
    print(("  PASS " if ok else "  FAIL ") + name + ("" if not detail else "  [%s]" % detail), flush=True)
    PASS += int(ok); FAIL += int(not ok)
    return ok


def main():
    lt = json.load(open(LT))["result"]; arms = lt["arms"]; dv = lt["deltas_vs_floor"]
    g = arms["GRADED"]["acc"]; u = arms["GRADED+unify(oracle)"]["acc"]
    chk("U1 entity unification lifts the graded pick CI-sep (oracle ceiling) with named no-regress",
        u > g and dv["GRADED+unify(oracle)"]["ci_sep_above"]
        and arms["GRADED+unify(oracle)"]["named_acc"] >= arms["GRADED"]["named_acc"] - 0.005,
        "graded %.4f -> unify %.4f (+%.4f); named %.4f -> %.4f" % (
            g, u, u - g, arms["GRADED"]["named_acc"], arms["GRADED+unify(oracle)"]["named_acc"]))
    gp_live = arms["GRADED+genderprop"]["acc"]; gtw = arms["GRADED+genderTWIN"]["acc"]
    chk("U2 hard-filter gender propagation is a LOCATED NEGATIVE on the live overlay (below the pick, ~= random twin)",
        gp_live < g - 0.01 and abs(gp_live - gtw) < 0.03,
        "graded %.4f -> genderprop %.4f (random-gender twin %.4f)" % (g, gp_live, gtw))
    an = json.load(open(AN))["result"]
    chk("A1 the HARD agreement filter OVER-NARROWS (gold-filtered-OUT is the dominant error on a clean pool)",
        an["of_errors"]["gold_not_in_pool"] > 0.4,
        "of errors: not-in-pool %.1f%% (over-narrow) vs dominated %.1f%% -- but opening it up (recall-safe) REGRESSES the FRAGMENTED live pool; the fix is UNIFICATION first" % (
            100 * an["of_errors"]["gold_not_in_pool"], 100 * an["of_errors"]["structurally_dominated"]))
    chk("G1 naive name-gender filtering HURTS (over-narrows); incremental gender recovers it",
        an["acc"]["name_only"] < an["acc"]["no_filter"] and an["acc"]["name+prior_pron"] > an["acc"]["name_only"] + 0.05,
        "no_filter %.4f > name_only %.4f ; name+prior_pron %.4f" % (
            an["acc"]["no_filter"], an["acc"]["name_only"], an["acc"]["name+prior_pron"]))
    gpm = json.load(open(GP))["result"]
    dr = json.load(open(DR))["result"]
    chk("G2 the gender/recall-safe fixes are CACHE-OPTIMISTIC: they help the idealized unified cache but REGRESS live",
        gpm["incrementalRS_minus_liveemul"]["CIsep"] and dr["recallsafe_minus_graded"]["delta"] < 0
        and dr["full_stack_minus_graded"]["delta"] < 0,
        "cache +RS %+.4f (helps) BUT live +recallsafe %+.4f, full-stack(unify+RS+gender) %+.4f (both REGRESS the pick)" % (
            gpm["incrementalRS_minus_liveemul"]["delta"], dr["recallsafe_minus_graded"]["delta"],
            dr["full_stack_minus_graded"]["delta"]))
    ec = dr["EC_drill"]
    chk("EC1 turning event-centrality OFF is JUSTIFIED (not convenient): it hurts the graded pick UNIFORMLY (near AND far)",
        ec["GRADED+EC_near"] < ec["GRADED_near"] and ec["GRADED+EC_far"] < ec["GRADED_far"],
        "near %.4f->%.4f | far %.4f->%.4f (overall %.4f->%.4f)" % (
            ec["GRADED_near"], ec["GRADED+EC_near"], ec["GRADED_far"], ec["GRADED+EC_far"], dr["GRADED"], dr["GRADED+EC"]))
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
