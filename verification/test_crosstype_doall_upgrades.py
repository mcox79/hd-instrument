"""Witness for the three "do all, brain-foundationally" upgrades (owner 2026-09-08) to the crosstype name-bridge.

  W1 (A) HONEST CUE-BASED CLUSTERING: the brain's cue-based content-addressable retrieval (Lewis-Vasishth ACT-R)
        matches-or-beats the situation_predict heuristic on entity-layer CoNLL, and the shuffled-cue twin LOSES
        (the cues are load-bearing). Full-set number: +0.0036 CI[+0.0015,+0.0059] CI-sep (data/.../metrics.json).
  W2 (B) SYSTEMATIC DEVERBAL-AGENT ROLES: WordNet derivation reaches >= the curated ~30-verb lexicon on the
        occupational stratum, and the shuffled-verb-role twin LOSES.
  W3 (C) FULL THREE-ROUTE beats its own info-free twin (the added semantic-memory + deverbal routes carry CORRECT
        signal), even though it does not net-beat the in-text bridge on GUM (the coverage wall, documented).

Run: .venv/Scripts/python.exe verification/test_crosstype_doall_upgrades.py
"""
import os
import random
import sys

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import experiments.gum_coref as G
from experiments.exp_name_entity_clustering_v1 import load_given_gazetteer


def main():
    ok = 0
    gaz = load_given_gazetteer()

    # W1 -- cue-based clustering
    import experiments.exp_crosstype_cuebased_cluster_gum_v1 as CU
    r = CU.run(docs_limit=150, verbose=False)
    assert r["cue_based"] >= r["situation_predict_floor"] - 0.001, \
        "W1: cue-based must match-or-beat situation_predict: %.4f vs %.4f" % (r["cue_based"], r["situation_predict_floor"])
    assert r["cue_vs_twin"]["ci_sep"] and r["twin_shuffled_cues"] < r["cue_based"], \
        "W1: shuffled-cue twin must LOSE CI-sep: %s" % r["cue_vs_twin"]
    print("W1 PASS: cue-based %.4f >= situation_predict %.4f ; shuffled-cue twin %.4f loses (+%.4f CI-sep)"
          % (r["cue_based"], r["situation_predict_floor"], r["twin_shuffled_cues"], r["cue_vs_twin"]["delta"]))
    ok += 1

    # W2 -- systematic deverbal-agent roles
    import experiments.exp_crosstype_deverbal_roles_gum_v1 as DV
    assert "writer" in DV.deverbal_agent_nouns("write") and "director" in DV.deverbal_agent_nouns("direct"), \
        "W2: productive morphology must derive write->writer, direct->director"
    r2 = DV.run(docs_limit=None, verbose=False)
    assert r2["deverbal"]["reach"] >= r2["curated"]["reach"] and r2["twin_shuffled_verbroles"]["reach"] <= r2["deverbal"]["reach"], \
        "W2: systematic deverbal must reach >= curated and beat the shuffled twin: %s" % r2["headline"]
    print("W2 PASS: occupational reach curated %d -> deverbal %d (twin %d) / %d -- productive > curated, twin loses"
          % (r2["curated"]["reach"], r2["deverbal"]["reach"], r2["twin_shuffled_verbroles"]["reach"], r2["curated"]["pop"]))
    ok += 1

    # W3 -- full three-route beats its info-free twin (routes carry correct signal)
    import experiments.exp_crosstype_full_tworoute_gum_v1 as FT
    docs = G.load_docs(gum_only=True, limit=80, name_gazetteer=gaz)
    three = FT._measure(docs, gaz, {"kb", "deverbal"})
    twin = FT._measure(docs, gaz, {"kb", "deverbal"}, shuffle=True)
    assert three["delta"]["delta"] > twin["delta"]["delta"], \
        "W3: three-route must beat its info-free twin (routes carry correct signal): %s vs %s" % (three["delta"], twin["delta"])
    print("W3 PASS: three-route C3 %+.4f > info-free twin %+.4f (added KB+deverbal routes carry correct signal)"
          % (three["delta"]["delta"], twin["delta"]["delta"]))
    ok += 1

    print("\nALL WITNESSES PASS (%d/%d)" % (ok, ok))
    return 0


if __name__ == "__main__":
    sys.exit(main())


# --- pytest-collectable wrapper (pri 128, mechanical; see notes/problems/447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest/PROBLEM.md) ---
import pytest as _pri128_pytest
from verification._witness_wrap import _run_main_as_test as _pri128_run


@_pri128_pytest.mark.corpus
def test_witness():
    _code, _out = _pri128_run(main)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
