"""Scaffold-free witness for the per-agent BELIEF TIMELINE (ToM x TIME composition).

Runs with tracing off, no pytest scaffold. Covers: the core sample-and-hold mechanism (past-T,
re-observe, testimony/deception, hindsight-decoupling), the substrate read-out, the info-free twin
losing, and the three landed aggregates (construction CI-sep proof, register-composition on
flashback prose, real-prose incidence).

    .venv/Scripts/python.exe verification/test_belief_timeline.py
"""
from __future__ import annotations

import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

N = 0


def check(cond, msg):
    global N
    assert cond, "FAIL: " + msg
    N += 1
    print(f"  ok  {msg}")


def test_core_mechanism():
    from experiments.belief_timeline import (
        WorldEvent, timeline_belief, current_belief_floor, reality_at, initial_value,
        hindsight_invariant, narration_timeline_belief,
    )
    print("[core sample-and-hold]")
    # multi-change: past-T recovers the earlier belief a current-belief tracker overwrites
    ev = [WorldEvent("m", "basket", 0, 0, "initial"),
          WorldEvent("m", "box", 1, 1), WorldEvent("m", "drawer", 2, 2)]
    obs = {("A", 0): True, ("A", 1): True, ("A", 2): True}
    check(timeline_belief(ev, obs, "A", "m", 0.5) == "basket", "belief at past-T = earlier value")
    check(timeline_belief(ev, obs, "A", "m", 2.5) == "drawer", "belief at final-T = latest value")
    check(current_belief_floor(ev, obs, "A", "m", 0.5) == "drawer",
          "current-belief floor reports final value at every T (wrong at past-T)")

    print("[re-observe stale-then-corrected]")
    ev2 = [WorldEvent("m", "basket", 0, 0, "initial"),
           WorldEvent("m", "box", 1, 1), WorldEvent("m", "box", 2, 2)]
    obs2 = {("A", 0): True, ("A", 1): False, ("A", 2): True}
    check(timeline_belief(ev2, obs2, "A", "m", 1.5) == "basket", "stale (false) belief between move and re-see")
    check(timeline_belief(ev2, obs2, "A", "m", 2.5) == "box", "corrected after re-observation")
    check(current_belief_floor(ev2, obs2, "A", "m", 1.5) == "box", "floor overwrites the stale belief")

    print("[reality + memory intact]")
    check(reality_at(ev2, "m", 1.5) == "box", "reality tracks the true world state")
    check(initial_value(ev2, "m") == "basket", "memory = initial placement")

    print("[testimony / deception -- belief updates by communication]")
    dec = [WorldEvent("m", "shelf", 0, 0, "initial", True),
           WorldEvent("m", "chest", 1, 1, "testimony", False)]  # a LIE; object never moved
    dobs = {("A", 0): True, ("A", 1): True}
    check(timeline_belief(dec, dobs, "A", "m", 1.5) == "chest", "A believes the false testimony")
    check(reality_at(dec, "m", 1.5) == "shelf", "the lie does NOT move the world")
    check(timeline_belief(dec, dobs, "A", "m", 0.5) == "shelf", "before the lie, belief = truth")

    print("[hindsight decoupling -- later unobserved change cannot corrupt a past belief]")
    ev3 = [WorldEvent("m", "basket", 0, 0, "initial"), WorldEvent("m", "box", 1, 1)]
    obs3 = {("A", 0): True, ("A", 1): False}
    check(hindsight_invariant(ev3, obs3, "A", "m", 0.5) is True,
          "past belief invariant to a later unobserved world change (beats curse-of-knowledge)")

    print("[narration-order ablation loses on a flashback]")
    fb = [WorldEvent("m", "drawer", chrono=0, narr=1, kind="initial"),  # chrono-first, narrated-2nd
          WorldEvent("m", "box", chrono=1, narr=0)]                     # chrono-2nd, narrated-1st
    fobs = {("A", 0): True, ("A", 1): True}
    check(timeline_belief(fb, fobs, "A", "m", 0.5) == "drawer", "register-order belief correct on flashback")
    check(narration_timeline_belief(fb, fobs, "A", "m", 0.5) != "drawer",
          "narration-order belief wrong on flashback (mis-sequences)")


def test_substrate_readout():
    from experiments.belief_timeline import SubstrateReadout
    print("[substrate read-out round-trips on the belief_partition organs]")
    ro = SubstrateReadout(d=1024)
    vocab = ["basket", "box", "drawer", "shelf"]
    for v in vocab:
        check(ro.readout("m", v, vocab) == v, f"FHRR read-out recovers '{v}'")


def test_construction_proof():
    from experiments.exp_belief_timeline_query_v1 import run
    print("[landed: construction CI-sep proof]")
    m = run(mode="full", d=1024, twin_seeds=100)
    h = m["headline"]
    check(h["timeline"] == 1.0, "timeline belief-acc == 1.000")
    check(h["ci_separated"], "timeline CI-separated over the current-belief floor")
    check(h["beats_twin"], "timeline beats the info-free twin p95")
    check(m["arms"]["current_belief"]["belief_acc"] < 0.6, "current-belief floor is a real floor (<0.6)")
    check(m["controls_reality_memory"]["acc"] == 1.0, "reality+memory controls intact 1.000")
    pc = m["positive_control_floor_cannot_get"]
    check(pc["timeline"]["acc"] == 1.0 and pc["current_belief"]["acc"] == 0.0,
          "positive control: timeline 1.0 vs floor 0.0 on the floor-cannot-get subset")
    check(m["hindsight_decoupling"]["invariant_fraction"] == 1.0, "hindsight-decoupling invariant 1.0")
    # rep B honest characterization: exact at wide gaps, degrades as the gap shrinks
    st = m["repB_timescale_stress"]
    check(st["1.0"]["repB"] == 1.0, "graded rep-B exact at wide inter-event gap")
    check(st["0.1"]["repB"] < st["0.1"]["repA"], "graded rep-B degrades near boundaries; discrete rep-A does not")


def test_register_composition():
    from experiments.exp_belief_timeline_flashback_register_v1 import run
    print("[landed: composition with the REAL temporal-order register on flashback prose]")
    m = run()
    check(m["extraction_coverage"] >= 0.8, "register extraction coverage >= 0.80 on the authored prose")
    check(m["flashback"]["register"] == 1.0, "register-ordered belief 1.0 on flashback")
    check(m["flashback"]["narration"] == 0.0, "narration-ordered belief 0.0 on flashback")
    check(m["verdict"]["register_beats_narration_on_flashback"], "register beats narration on flashback")
    check(m["verdict"]["no_over_reorder_on_linear"], "no over-reorder on the linear controls")


def test_knowledge_gap():
    from experiments.exp_belief_timeline_gap_v1 import run
    print("[landed: knowledge-gap over time -- dramatic irony / deception]")
    m = run(n=80, twin_seeds=120)
    check(m["timeline"]["acc"] == 1.0, "belief-timeline gap-acc == 1.000")
    check(m["verdict"]["ci_separated"], "gap CI-separated over the current-belief floor")
    check(m["verdict"]["beats_twin"], "gap beats the info-free order-shuffle twin p95")
    check(m["divergence_window_t1.5"]["timeline"] == 1.0 and m["divergence_window_t1.5"]["floor"] == 0.0,
          "divergence window: timeline 1.0 vs floor 0.0 (floor misses the past divergence)")


def test_precision_unification():
    from experiments.exp_belief_timeline_precision_v1 import run
    print("[landed: recency -> precision unification -- stale belief flattens; confidence = entropy]")
    m = run(n_inst=120, twin_seeds=120)
    check(m["verdict"]["entropy_rises_with_staleness"],
          "posterior entropy rises with staleness (a stale belief flattens) above the twin")
    check(m["verdict"]["fixed_precision_floor_is_flat"],
          "the fixed-precision floor CANNOT produce the staleness->uncertainty signature (flat)")
    check(m["verdict"]["confidence_unified_with_recency"],
          "confidence(=1-entropy) unified with the recency signal (Spearman > 0.9) -- one quantity")


def test_graded_posterior():
    from experiments.exp_belief_timeline_posterior_v1 import run
    print("[landed: GRADED posterior belief -- per-element weights, Bayesian ToM]")
    m = run(n=80, twin_seeds=80)
    a = m["arms"]
    check(a["graded"]["below_map_pairs"] > 0.85, "graded posterior ranks below-MAP pairs well (>0.85)")
    check(a["equal_set"]["below_map_pairs"] < 0.6 and a["value_conf"]["below_map_pairs"] < 0.6,
          "both floors are at chance below the MAP (structurally cannot rank non-top candidates)")
    check(m["verdict"]["graded_beats_equalset_below_map"] and m["verdict"]["graded_beats_valueconf_below_map"],
          "graded beats the equal-set AND value+confidence floors on the hard below-MAP pairs")
    check(m["verdict"]["graded_beats_twin"], "graded posterior beats the info-free weight-shuffle twin")


def test_uncertain_belief():
    from experiments.exp_belief_timeline_uncertain_v1 import run
    print("[landed: distributional / partial belief -- belief as a SET narrowing over time]")
    m = run(n=80, twin_seeds=80)
    check(m["distributional_f1"] >= 0.99, "distributional belief F1 ~1.000 (superposition + cleanup_set)")
    check(m["verdict"]["beats_crisp"] and m["verdict"]["beats_omniscient"] and m["verdict"]["beats_twin"],
          "distributional beats crisp-argmax, omniscient, and the info-free twin")
    check(m["uncertain_setsize_recall"]["distributional"] == 1.0
          and m["uncertain_setsize_recall"]["crisp"] == 0.0,
          "crisp point-belief STRUCTURALLY cannot represent uncertainty (set-size recall 1.0 vs 0.0)")


def test_inferred_edge():
    from experiments.exp_belief_timeline_inference_v1 import run
    print("[landed: evidence-gated INFERRED belief edge -- Sodian & Wimmer dissociation]")
    m = run(n=60, twin_seeds=100)
    check(m["arms"]["timeline"]["acc"] == 1.0, "gated inference 1.000 on both halves")
    check(m["verdict"]["beats_never_infer"], "beats the never-infer floor (which under-attributes)")
    check(m["verdict"]["beats_omniscient"], "beats the omniscient floor (which over-attributes)")
    # the dissociation: each floor fails a DIFFERENT half
    b = m["breakdown"]
    check(b["never_infer"]["all_premises"][0] == 0.0 and b["never_infer"]["partial_premise"][0] == 1.0,
          "never-infer floor: 0.0 all-premises, 1.0 partial (under-attributes only)")
    check(b["omniscient"]["all_premises"][0] == 1.0 and b["omniscient"]["partial_premise"][0] == 0.0,
          "omniscient floor: 1.0 all-premises, 0.0 partial (over-attributes only)")
    check(m["inference_deception"]["false_belief_by_inference"] == 1.0,
          "inference-based deception representable (false belief by inference from misleading evidence)")


def test_decaying_confidence():
    from experiments.exp_belief_timeline_confidence_v1 import run
    print("[landed: decaying confidence -- access decays, value persists]")
    m = run(n_inst=120, twin_seeds=120)
    check(m["verdict"]["fresh_is_confident"], "confidence is 1.0 fresh and near-0 when very stale")
    check(m["verdict"]["monotone"], "confidence monotone-decreasing in staleness")
    check(m["spearman_true"] > 0.5 and m["spearman_true"] > m["twin_abs_rho_p95"],
          "confidence predicts staleness (Spearman) far above the shuffled twin p95")
    check(m["conflict_resolution"]["recent_more_confident"],
          "a recent source is held more confidently than a stale one (conflict adjudication)")


def test_authored_second_gold():
    from experiments.exp_belief_timeline_authored_v1 import run
    print("[landed: hand-authored second gold -- external validity]")
    m = run(twin_seeds=100)
    check(m["timeline"]["acc"] == 1.0, "timeline 1.000 on hand-authored real-English passages")
    check(m["verdict"]["ci_separated"], "CI-separated over the current-belief floor on the second gold")
    check(m["verdict"]["mechanism_matches_handgold"],
          "0 mechanism-vs-hand-gold mismatches (reproduces human judgement independently)")


def test_live_end_to_end():
    from experiments.exp_belief_timeline_live_e2e_v1 import run
    print("[landed: END-TO-END LIVE serve -- belief timeline + LIVE observation-cue extractor]")
    m = run()
    check(m["oracle_upper_bound"]["acc"] == 1.0, "oracle (gold obs) 1.000 -- the mechanism is correct")
    check(m["verdict"]["live_beats_floor"],
          "LIVE end-to-end beats the timeline-agnostic floor CI-separated (imperfect extraction in the loop)")
    check(m["observation_cue_extraction_acc"] > 0.85,
          "the LIVE observation-cue extractor is real and works on the prose (>0.85)")
    check(m["live_end_to_end"]["acc"] > m["timeline_agnostic_floor"]["acc"] + 0.3,
          "large live lift over the floor (>0.3) with the real extractor in the loop")


def test_live_flashback_e2e():
    from experiments.exp_belief_timeline_live_flashback_e2e_v1 import run
    print("[landed: COMBINED live serve -- LIVE order + LIVE observation jointly on flashback prose]")
    m = run()
    check(m["arms"]["live"]["acc"] >= 0.9, "combined live stack >= 0.90 on flashback prose")
    check(m["verdict"]["live_beats_narration"] and m["arms"]["narration"]["acc"] == 0.0,
          "LIVE beats narration-order (0.0) -- the live temporal-order register is load-bearing")
    check(m["verdict"]["live_beats_obs_blind"] and m["arms"]["obs_blind"]["acc"] == 0.0,
          "LIVE beats observation-blind (0.0) -- the live observation cue is load-bearing")
    check(m["arms"]["floor"]["acc"] == 0.0, "the timeline-agnostic floor fails entirely (0.0)")


def test_real_prose_incidence():
    from experiments.exp_belief_timeline_real_prose_v1 import run
    print("[landed: real-prose incidence bound]")
    m = run()
    check(m["corpus"]["n_observation_events"] > 900, "corpus incidence measured on >900 events")
    check(0.0 < m["corpus"]["staleness_fraction"] < 1.0, "staleness fraction is a real proportion")
    check(m["authored_tom_gold"]["over_time_multievent"] == 0,
          "authored ToM gold is single-change (over-time structure needed construction gold)")


if __name__ == "__main__":
    print("=" * 70)
    print("WITNESS: per-agent BELIEF TIMELINE (what an agent knew when)")
    print("=" * 70)
    test_core_mechanism()
    test_substrate_readout()
    test_construction_proof()
    test_register_composition()
    test_knowledge_gap()
    test_precision_unification()
    test_graded_posterior()
    test_uncertain_belief()
    test_inferred_edge()
    test_decaying_confidence()
    test_authored_second_gold()
    test_live_end_to_end()
    test_live_flashback_e2e()
    test_real_prose_incidence()
    print("=" * 70)
    print(f"ALL {N} CHECKS PASS")
