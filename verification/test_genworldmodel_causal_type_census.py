"""Witness -- WHY the LOO physical-world-state mechanism reaches only ~5%: a causal-type census of the gold
cause->effect pairs shows real-narrative causation is DOMINANTLY PSYCHOLOGICAL/GOAL, not physical. GLUCOSE:
GOAL ~41%, OTHER ~36%, MENTAL+AFFECTIVE ~11%, PHYSICAL only ~12%; TellMeWhy: GOAL ~37%, OTHER ~40%, PHYSICAL
~9%. The STRIPS world-state (`hdlab.world_state_register`) models only PHYSICAL possession/toggle preconditions,
so it can represent only ~5% (GLUCOSE) / ~3% (TellMeWhy) of gold pairs BY CONSTRUCTION -- exactly the LOO
coverage ceiling. The blocker is the world-state ONTOLOGY (too physical), not coref: the right substrate for the
dominant GOAL/mental causation is a psychological state (inverse planning + ToM), not physical possession.

problem: build_the_generative_result_state_world_model
Run: .venv/Scripts/python.exe verification/test_genworldmodel_causal_type_census.py
"""
from __future__ import annotations
import os, sys
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
from experiments import exp_genworldmodel_causal_type_census_v1 as C


def check(name, cond, detail=""):
    print("[%s] %s: %s" % ("PASS" if cond else "FAIL", name, detail))
    return bool(cond)


def main():
    o = C.run(n_glu=3000, n_tmw=1500)
    g = o["GLUCOSE"]; t = o["TellMeWhy"]; oks = []

    oks.append(check(
        "W1 causation is DOMINANTLY psychological/goal on both corpora: GOAL is the largest single causal type "
        "and PHYSICAL is a small minority (<0.2)",
        g["type_dist"]["GOAL"] > g["type_dist"]["PHYSICAL"] and g["type_dist"]["PHYSICAL"] < 0.2
        and t["type_dist"]["GOAL"] > t["type_dist"]["PHYSICAL"] and t["type_dist"]["PHYSICAL"] < 0.2,
        "GLUCOSE types %s | TellMeWhy types %s" % (g["type_dist"], t["type_dist"])))

    oks.append(check(
        "W2 the STRIPS physical world-state can REPRESENT only a tiny fraction of gold cause->effect pairs "
        "(<0.15) -- exactly the LOO coverage ceiling, explaining the ~5% fire rate",
        g["representable_frac"] < 0.15 and t["representable_frac"] < 0.15,
        "GLUCOSE representable %.3f | TellMeWhy representable %.3f" % (g["representable_frac"], t["representable_frac"])))

    oks.append(check(
        "W3 psychological (GOAL+MENTAL+AFFECTIVE) causation dominates the physical share on both corpora "
        "-> the right substrate is a goal/mental state, not physical possession",
        (g["type_dist"]["GOAL"] + g["type_dist"]["MENTAL"] + g["type_dist"]["AFFECTIVE"]) > 2 * g["type_dist"]["PHYSICAL"]
        and (t["type_dist"]["GOAL"] + t["type_dist"]["MENTAL"] + t["type_dist"]["AFFECTIVE"]) > 2 * t["type_dist"]["PHYSICAL"],
        "GLUCOSE psych %.3f vs phys %.3f | TellMeWhy psych %.3f vs phys %.3f" % (
            g["type_dist"]["GOAL"] + g["type_dist"]["MENTAL"] + g["type_dist"]["AFFECTIVE"], g["type_dist"]["PHYSICAL"],
            t["type_dist"]["GOAL"] + t["type_dist"]["MENTAL"] + t["type_dist"]["AFFECTIVE"], t["type_dist"]["PHYSICAL"])))

    oks.append(check(
        "W4 verdict = causation dominantly psychological, world-state too physical",
        o["verdict"] == "CAUSATION_DOMINANTLY_PSYCHOLOGICAL_WORLD_STATE_TOO_PHYSICAL", o["verdict"]))

    n = sum(oks)
    print("=" * 92)
    print("%s (%d/%d)" % ("ALL CHECKS PASS" if n == len(oks) else "SOME CHECKS FAILED", n, len(oks)))
    print("=" * 92)
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
