"""Witness -- the UPSTREAM broadening (full-stack-upstream directive): swapping the possession-only
result-state schema for VerbNet's DIRECTED semantic-predicate result-states (a curated glass-box offline
asset) raises coverage but STILL does not cross the full-population wall, because ~95% of the GOAL-subset
misses are genuine MULTI-STEP PLANS ("wanted milk" -> "went to the store") that carry no single-step
result-state achieving the goal. The residual is rollout DEPTH (plan/script chaining), not verb->result-state
COVERAGE -- the precise, deeper located negative.

problem: build_the_generative_result_state_world_model
Run: .venv/Scripts/python.exe verification/test_genworldmodel_upstream_verbnet.py
"""
from __future__ import annotations
import os, sys
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
from experiments import exp_genworldmodel_upstream_verbnet_v1 as U


def check(name, cond, detail=""):
    print("[%s] %s: %s" % ("PASS" if cond else "FAIL", name, detail))
    return bool(cond)


def main():
    oks = []
    # VerbNet directed result-state predicate extraction (the brain-foundational curated asset)
    oks.append(check(
        "W1 VerbNet gives DIRECTED result-states: buy->has_possession, build->exist, and go carries NO possession (a plan verb, not a possession-achiever)",
        "has_possession" in U.vn_result_preds("buy")
        and ("exist" in U.vn_result_preds("build") or "made_of" in U.vn_result_preds("build"))
        and "has_possession" not in U.vn_result_preds("go"),
        "buy=%s build=%s go=%s" % (U.vn_result_preds("buy"), U.vn_result_preds("build"), U.vn_result_preds("go"))))

    o = U.run(n=1500)
    ov = o["overall"]; cov = o["coverage"]
    vb = o["rs_vn_vs_base"]

    oks.append(check(
        "W2 broadening does NOT cross the full-population wall: the VerbNet directed result-state arm ties base",
        not vb["ci_sep"],
        "rs_verbnet=%.4f base=%.4f delta=%s fires objmatch=%d rs_verbnet=%d" % (
            ov["rs_verbnet"], ov["base"], vb["ci"], o["fire_counts"]["objmatch"], o["fire_counts"]["rs_verbnet"])))

    oks.append(check(
        "W3 the RESIDUAL is MULTI-STEP PLANS, not coverage: >80% of the GOAL-subset misses have NO single-step goal-type result-state (the deeper wall = plan/script chaining)",
        cov["multistep_frac_of_miss"] > 0.8,
        "multistep_frac_of_miss=%.3f (single-step VerbNet-coverable=%.3f); type-matched coverage: possession %.3f -> VerbNet %.3f" % (
            cov["multistep_frac_of_miss"], 1 - cov["multistep_frac_of_miss"],
            cov.get("poss_cover_rate", float("nan")), cov.get("vn_cover_rate", float("nan")))))

    n = sum(oks)
    print("=" * 90)
    print("%s (%d/%d)" % ("ALL CHECKS PASS" if n == len(oks) else "SOME CHECKS FAILED", n, len(oks)))
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
