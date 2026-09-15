"""Witness -- the goal-RESOLUTION wall closed with LANDED knowledge (owner: "we have knowledge/foundation work;
look at what we've done"). The substrate's glass-box semantic desire-FULFILLMENT detector
(hdlab.goal_achievement.relation_channel; WordNet verb-synonyms + goal_typing; DesireDB-validated) -- when fed
the goal SENTENCE as the desire (my earlier bug fed the bare goal span -> 0 fire) -- RECOVERS the goal-resolution
funnel over track_status_thwart's STRICT-lexical check: TellMeWhy-GOAL resolved 0.163 -> 0.304 (+0.141), GLUCOSE
+0.027; fires ~16-25%. So the knowledge IS on disk. BUT recovering resolution does NOT lift cause-selection
accuracy (sem_resolve/sem_loo do not CI-beat base as integrator cues) -- because the golds reward
best-EXPLANATION/relevance, not goal-resolution-necessity (cycle-17 reframe). Two separate facts: we HAVE the
semantic knowledge (yes); it does not move THIS metric (no -- the metric measures a different construct).

problem: build_the_generative_result_state_world_model
Run: .venv/Scripts/python.exe verification/test_genworldmodel_semantic_goal_resolution.py
"""
from __future__ import annotations
import os, sys
import numpy as np
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
from experiments import exp_genworldmodel_semantic_goal_resolution_v1 as R


def check(name, cond, detail=""):
    print("[%s] %s: %s" % ("PASS" if cond else "FAIL", name, detail))
    return bool(cond)


def main():
    o = R.run(n_glu=3000, n_tmw=1500)
    g = o["GLUCOSE"]; t = o["TellMeWhy_GOAL"]; oks = []

    oks.append(check(
        "W1 the LANDED semantic resolver (goal_achievement.relation_channel) FIRES substantially when fed the "
        "goal sentence (>0.1 on both) -- the knowledge is on disk, was under-used",
        g["diag"]["sem_fires"] > 0.1 and t["diag"]["sem_fires"] > 0.1,
        "GLUCOSE sem_fires %.3f | TellMeWhy sem_fires %.3f" % (g["diag"]["sem_fires"], t["diag"]["sem_fires"])))

    oks.append(check(
        "W2 it RECOVERS the goal-resolution funnel over the strict-lexical check (resolved_semantic >= "
        "resolved_strict on both; substantial on TellMeWhy-GOAL)",
        t["diag"]["resolved_semantic"] > t["diag"]["resolved_strict"] + 0.05
        and g["diag"]["resolved_semantic"] >= g["diag"]["resolved_strict"],
        "GLUCOSE strict %.3f -> sem %.3f | TellMeWhy strict %.3f -> sem %.3f (recovery %+.3f)" % (
            g["diag"]["resolved_strict"], g["diag"]["resolved_semantic"],
            t["diag"]["resolved_strict"], t["diag"]["resolved_semantic"], o["resolution_recovery_tmw"])))

    oks.append(check(
        "W3 BUT recovering resolution does NOT give a CI-separated cause-selection lift (the semantic cues do not "
        "CI-beat base) -- the golds reward best-explanation/relevance, not goal-resolution-necessity",
        not any(a["vs_base"]["ci_sep"] for a in g["arms"].values())
        and not any(a["vs_base"]["ci_sep"] for a in t["arms"].values()),
        "GLUCOSE sem_resolve +int %s sem_loo +int %s | TMW sem_resolve +int %s sem_loo +int %s" % (
            g["arms"]["sem_resolve"]["vs_base"]["ci"], g["arms"]["sem_loo"]["vs_base"]["ci"],
            t["arms"]["sem_resolve"]["vs_base"]["ci"], t["arms"]["sem_loo"]["vs_base"]["ci"])))

    oks.append(check(
        "W4 verdict = semantic resolution RECOVERS coverage but does not lift (knowledge present; metric measures "
        "a different construct)",
        o["verdict"] == "SEMANTIC_RESOLUTION_RECOVERS_COVERAGE_NO_LIFT", o["verdict"]))

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
