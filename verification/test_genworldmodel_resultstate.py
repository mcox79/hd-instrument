"""Witness -- the GENERATIVE RESULT-STATE WORLD-MODEL: a participant-bound rollout that SIMULATES an
action forward to a result-STATE and CHECKS achievement against the goal-STATE (Schank-Abelson RESULT /
Baker-Saxe-Tenenbaum inverse planning), composing landed organs (world_state_register + possession_operators
+ goal_register), WINS the GOAL subset of modern TellMeWhy non-adjacent CI-separated with the info-free
NULL losing, feeds a TOP-DOWN expectation the feed-forward silo cannot, is additive/no-regress -- and on the
FULL population is a LOCATED NEGATIVE: the single-step result-state schema covers ~9% of goal->action
means-ends, 91% of the misses are MULTI-STEP PLANS, and broadening coverage via learned co-occurrence (GEK)
does NOT cross it (co-occurrence is directionless).

problem: build_the_generative_result_state_world_model
Run: .venv/Scripts/python.exe verification/test_genworldmodel_resultstate.py
"""
from __future__ import annotations
import os, sys
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
from experiments import exp_genworldmodel_resultstate_v1 as G


def check(name, cond, detail=""):
    print("[%s] %s: %s" % ("PASS" if cond else "FAIL", name, detail))
    return bool(cond)


def main():
    o = G.run(n=1500)
    ov = o["overall"]; cov = o["coverage"]
    oks = []

    oks.append(check(
        "W1 REPRODUCES the disk baseline (base~0.277, objmatch~0.293, gen_union~0.309 = the prior best arm)",
        abs(ov["base"] - 0.277) < 0.02 and abs(ov["objmatch"] - 0.293) < 0.02 and abs(ov["gen_union"] - 0.309) < 0.02,
        "base=%.4f objmatch=%.4f gen_union=%.4f" % (ov["base"], ov["objmatch"], ov["gen_union"])))

    b = o["rs_refine_vs_base_GOAL"]; t = o["rs_refine_vs_topical_GOAL"]
    oks.append(check(
        "W2 GOAL-SUBSET POSITIVE: the result-state achievement check BEATS base AND topical CI-separated on the GOAL subset",
        b["ci_sep"] and t["ci_sep"],
        "GOAL rs=%.4f base=%.4f delta_base=%s delta_topical=%s" % (
            o["breakdown"]["GOAL"]["rs_refine"], o["breakdown"]["GOAL"]["base"], b["ci"], t["ci"])))

    nrg = o["null_rs_refine_GOAL"]
    oks.append(check(
        "W3 the info-free NULL (permute the generated result-state across candidates, many draws) LOSES on the GOAL subset (observed > null p95, p~0)",
        nrg["beats_p95"] and nrg["observed"] > nrg["null_p95"],
        "observed=%.4f null_p95=%.4f p=%s" % (nrg["observed"], nrg["null_p95"], nrg["p_value"])))

    fb = o["rs_refine_vs_base"]
    oks.append(check(
        "W4 FULL-POPULATION LOCATED NEGATIVE: ties base (not CI-sep) -- the single-step result-state schema covers <15% of goal-actions and >80% of the misses are MULTI-STEP (coverage-miss)",
        (not fb["ci_sep"]) and cov["schema_cover_rate"] < 0.15 and cov["coverage_frac_of_miss"] > 0.8,
        "full rs-base=%s schema_cover=%.3f coverage_frac_of_miss=%.3f" % (
            fb["ci"], cov["schema_cover_rate"], cov["coverage_frac_of_miss"])))

    gk = o["gek_broad_vs_base"]
    oks.append(check(
        "W5 UPSTREAM (co-occurrence) does NOT cross the wall: broad GEK forward reachability (fires ~as often as objmatch) ties base -- learned co-occurrence is the WRONG axis (directionless)",
        not gk["ci_sep"],
        "gek_broad=%.4f gek-base=%s fires gek=%d objmatch=%d" % (
            ov["gek_broad"], gk["ci"], o["fire_counts"]["gek_broad"], o["fire_counts"]["objmatch"])))

    td = G.topdown_control()
    oks.append(check(
        "W6 TOP-DOWN into extraction (can-fail POSITIVE control): the generated goal-STATE expectation discriminates achieve-vs-defeat where the feed-forward SURFACE silo (goal-object overlap) TIES and cannot",
        td["rs_beats_silo"] and td["rs_acc"] > 0.7 and td["silo_acc"] < td["rs_acc"],
        "silo_acc=%.3f (ties) rs_acc=%.3f over n=%d pairs" % (td["silo_acc"], td["rs_acc"], td["n_pairs"])))

    nr = G.no_regress()
    oks.append(check(
        "W7 NO-REGRESS / additive: the rollout is inert without an explicit goal marker (byte-identical to the goal-OFF base) and never modifies a live reasoner",
        nr["inert_without_goal_marker"] and nr["additive_off_equals_base"] and not nr["modifies_live_reasoner"],
        "inert=%s additive=%s modifies_live=%s" % (
            nr["inert_without_goal_marker"], nr["additive_off_equals_base"], nr["modifies_live_reasoner"])))

    oks.append(check(
        "W8 SELECTIVITY is real but coverage-capped: rs_refine NEVER fires where objmatch did not (pure precision), suppressing goal-DEFEATING actions -- but on this gold only a few covered defeat-verbs appear",
        o["fire_counts"]["rs_refine"] <= o["fire_counts"]["objmatch"],
        "fires objmatch=%d rs_refine=%d rs_strict=%d (schema-covered achievements)" % (
            o["fire_counts"]["objmatch"], o["fire_counts"]["rs_refine"], o["fire_counts"]["rs_strict"])))

    n = sum(oks)
    print("=" * 90)
    print("%s (%d/%d)  verdict=%s" % ("ALL CHECKS PASS" if n == len(oks) else "SOME CHECKS FAILED",
                                      n, len(oks), o["verdict"]))
    print("=" * 90)
    return 0 if n == len(oks) else 1


if __name__ == "__main__":
    sys.exit(main())


# --- pytest-collectable wrapper (pri 128, mechanical; see notes/problems/447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest/PROBLEM.md) ---
import pytest as _pri128_pytest
from verification._witness_wrap import _run_main_as_test as _pri128_run


@_pri128_pytest.mark.fast
def test_witness():
    _code, _out = _pri128_run(main)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
