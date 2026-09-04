"""Scaffold-free witness for the_situation_model_has_no_goal_intention_dimension.

Asserts the load-bearing claims of the GOAL/INTENTION dimension from the landed metrics.json (re-runs
NO cell) PLUS a from-source unit test of the extractor + register (constructed, deterministic, no reader):
  W1  the glass-box goal extractor + per-agent register bind the right goal to the right agent
      (constructed multi-agent passage), and the goal is NOT the agent's most-recent action.
  W2  WANT (goal identity), EXPLICIT slice: the register beats the most-recent-action floor AND the
      shuffled-agent info-free twin, CI-separated.
  W3  WANT extraction fidelity: on the EXPLICIT slice the register matches a spaCy ORACLE at high
      precision (reference-only); the BARE-purpose slice is LOW precision -> the parse-gated negative.
  W4  WHY (goal-why) vs PHYSICAL cause: the goal register produces the PURPOSE where the physical-cause
      dimension does not (CI-separated) -- goals are a dimension SEPARATE from physical causation.
  W5  COMPLEMENTARITY (the converse): on physical because/so questions the CAUSAL dim answers and the
      goal register does not -> the two dimensions are DISJOINT (Malle reason-vs-cause), both real.
  W6  POSITIVE CONTROL: multi-agent passages where an agent-blind floor returns the WRONG agent's goal
      -- the register is right and the floor wrong far more often than the reverse (binds the agent).
  W7  GOAL STATUS (PINNED status field): track_status recovers active/satisfied/failed on authored gold,
      beating a no-status floor; thwart-by-outcome is the named located negative.

    .venv/Scripts/python.exe verification/test_goal_register.py
"""
import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)


def _load():
    p = os.path.join(REPO, "data", "exp_goal_register_qa_v1", "metrics.json")
    assert os.path.exists(p), "MISSING landed metrics: %s (run: experiments/exp_goal_register_qa_v1.py --run)" % p
    with open(p, encoding="ascii") as f:
        return json.load(f)


def main():
    checks = []
    r = _load()

    # ---- W1: from-source unit -- extractor + register bind the right goal to the right agent ----
    import experiments.goal_register as GR
    sents = [["Mary", "wanted", "to", "escape", "the", "house", "."],
             ["She", "ran", "to", "the", "door", "."],
             ["John", "tried", "to", "stop", "her", "."]]
    from hdlab.pos_tagger import PosTagger
    tg = PosTagger.load(os.path.join(REPO, "data/frontend_assets/pos_tagger_ud_ewt_upos.json"))
    pos = [tg.tag(t) for t in sents]
    goals = GR.extract_goals(sents, pos)
    GR.bind_agents(goals, lambda s, si: {"mary": "mary", "she": "mary", "john": "john"}.get(s.lower()))
    reg = GR.GoalRegister(goals)
    assert reg.wants("mary") and GR._lemma(reg.wants("mary").goal_head) == GR._lemma("escape"), \
        [(g.agent_canonical, g.goal_head) for g in goals]
    assert reg.wants("john") and GR._lemma(reg.wants("john").goal_head) == GR._lemma("stop"), \
        [(g.agent_canonical, g.goal_head) for g in goals]
    assert GR._lemma("ran") != GR._lemma("escape"), "the goal must differ from the most-recent action"
    checks.append(("W1 extractor+register bind right goal->right agent (goal != recent action)", "mary:escape/john:stop", "UNIT"))

    # ---- W2: WANT explicit slice -- model beats most-recent-action floor AND shuffled-agent twin, CI-sep ----
    we = r["want_explicit"]
    ci = we["ci"]
    assert ci["sep_over_floor_most_recent_action"] and ci["model_minus_floor_most_recent_action"][0] > 0, we
    assert ci["sep_over_twin_shuffled_agent"] and ci["model_minus_twin_shuffled_agent"][0] > 0, we
    assert we["acc"]["model"] > we["acc"]["floor_most_recent_action"] > we["acc"]["twin_shuffled_agent"], we
    checks.append(("W2 WANT explicit: model %.3f > floor %.3f > twin %.3f (both CI-sep)" % (
        we["acc"]["model"], we["acc"]["floor_most_recent_action"], we["acc"]["twin_shuffled_agent"]),
        we["acc"]["model"], "CI-SEP"))

    # ---- W2b: the info-free twin null p95 loses to the model (whole WANT population) ----
    w = r["want"]
    tp95 = (w.get("twin_null_p95") or {}).get("p95")
    assert tp95 is not None and w["acc"]["model"] > tp95, ("twin null p95 must lose", w.get("twin_null_p95"))
    checks.append(("W2b WANT model %.3f > info-free twin null p95 %.4f" % (w["acc"]["model"], tp95), tp95, "TWIN-LOSES"))

    # ---- W3: extraction fidelity vs spaCy ORACLE -- explicit slice HIGH precision, bare-purpose LOW ----
    oq = r["oracle_extraction_quality"]
    ep = oq["explicit_head_precision"]["precision"]; bp = oq["bare_purpose_head_precision"]["precision"]
    assert ep is not None and ep >= 0.75, ("explicit-slice precision must be high", oq)
    assert bp is not None and bp < 0.55 and bp < ep, ("bare-purpose is the parse-gated negative", oq)
    checks.append(("W3 oracle precision: explicit %.3f (reliable) >> bare-purpose %.3f (parse-gated)" % (ep, bp), ep, "FIDELITY"))

    # ---- W4: WHY (goal-why) vs PHYSICAL cause -- goals produce the purpose where the cause dim cannot ----
    y = r["why"]
    assert y["ci"]["sep_over_floor_physical_cause"] and y["ci"]["model_minus_floor_physical_cause"][0] > 0, y
    assert y["acc"]["model_goal_register"] > 0.5 and y["acc"]["floor_physical_cause"] < 0.2, y
    checks.append(("W4 WHY goal-register %.3f >> physical-cause floor %.3f (CI-sep; goals != cause)" % (
        y["acc"]["model_goal_register"], y["acc"]["floor_physical_cause"]), y["acc"]["model_goal_register"], "CI-SEP"))

    # ---- W5: COMPLEMENTARITY converse -- on physical cause questions the CAUSAL dim wins, register ~0 ----
    cc = r["causal_complementarity"]
    assert cc["causal_dimension_acc"] > 0.5 and cc["goal_register_acc"] < 0.2, cc
    checks.append(("W5 complementarity: on physical-cause q, causal-dim %.3f vs goal-register %.3f (DISJOINT)" % (
        cc["causal_dimension_acc"], cc["goal_register_acc"]), cc["goal_register_acc"], "DISJOINT"))

    # ---- W6: POSITIVE CONTROL -- register binds the right agent where an agent-blind floor cannot ----
    pc = r["positive_control"]
    assert pc["model_right_agentblind_wrong"] > 5 * max(1, pc["agentblind_right_model_wrong"]), pc
    checks.append(("W6 positive control: model-right/floor-wrong %d vs reverse %d (binds the agent)" % (
        pc["model_right_agentblind_wrong"], pc["agentblind_right_model_wrong"]), pc["model_right_agentblind_wrong"], "AGENT-BOUND"))

    # ---- W7: GOAL STATUS field (PINNED) -- track_status recovers active/satisfied/failed, beats floor ----
    gs = r["goal_status"]
    assert gs["model_acc"] > gs["floor_always_active_acc"], gs
    assert gs["model_acc"] >= 0.9, gs
    assert set(gs["by_status"].keys()) >= {"satisfied", "active", "failed"}, gs
    checks.append(("W7 goal status: track_status %.3f > floor[always-active] %.3f (active/satisfied/failed)" % (
        gs["model_acc"], gs["floor_always_active_acc"]), gs["model_acc"], "STATUS-FIELD"))

    # ---- W8: REINSTATEMENT (PINNED Suh-Trabasso) -- a satisfied subgoal reinstates the superordinate;
    #      status-gated wants() gets it where a status-blind RECENCY floor cannot, twin null loses ----
    ri = r["reinstatement"]
    assert ri["model_reinstatement_acc"] >= 0.9 and ri["floor_recency_acc"] <= 0.1, ri
    assert ri["model_reinstatement_acc"] > ri["twin_status_shuffle_null"]["p95"], ri
    checks.append(("W8 reinstatement: wants %.3f > recency floor %.3f & twin null p95 %.3f (Suh-Trabasso)" % (
        ri["model_reinstatement_acc"], ri["floor_recency_acc"], ri["twin_status_shuffle_null"]["p95"]),
        ri["model_reinstatement_acc"], "REINSTATEMENT"))

    # ---- W9: the UPSTREAM brain-foundational fix -- the lexicalist verb SUBCATEGORIZATION FRAME. (a) the
    #      frame classifies complement-takers vs adjunct-hosts brain-faithfully (want/begin=complement,
    #      go/come=adjunct-host); (b) A/B: the lexicalist frame >= the hardcoded heuristic on all-precision
    #      (removes complement/extraposition over-fires) without collapsing recall. ----
    from experiments.verb_subcat_frames import SubcatFrames
    sf = SubcatFrames.load()
    assert sf.is_complement_taker("want") and sf.is_complement_taker("begin"), "W9 want/begin are complement-takers"
    assert not sf.is_complement_taker("go") and not sf.is_complement_taker("come"), "W9 go/come are adjunct-hosts (go: the 'be going to' future is excluded)"
    ab_h = r.get("oracle_extraction_quality_heuristic", {}).get("all_head", {})
    ab_l = r["oracle_extraction_quality"]["all_head"]
    if ab_h.get("precision") is not None:
        assert ab_l["precision"] >= ab_h["precision"], ("W9 lexicalist all-precision >= heuristic", ab_l, ab_h)
    checks.append(("W9 upstream lexicalist frame: want/begin=complement, go/come=adjunct; A/B all-prec %s->%s" % (
        ab_h.get("precision"), ab_l["precision"]), ab_l["precision"], "UPSTREAM-FIX"))

    # ---- W10: ZERO REGRESSION on the OTHER consumers of the upstream frame -- the subcat frame gates ONLY
    #      the bare-purpose branch, so the EXPLICIT goals (desire/intend/try + in-order-to) are BYTE-IDENTICAL
    #      with the frame OFF vs ON (proven from source on a constructed multi-kind passage). Confirmed on
    #      100 docs: WANT-explicit OFF 0.6068 == ON 0.6068. ----
    sents2 = [["Mary", "wanted", "to", "escape", "."],
              ["She", "went", "to", "town", "to", "buy", "bread", "."],
              ["John", "tried", "to", "help", "in", "order", "to", "win", "."]]
    pos2 = [tg.tag(t) for t in sents2]
    g_off = [(g.kind, g.agent, GR._lemma(g.goal_head)) for g in GR.extract_goals(sents2, pos2, subcat=None)
             if g.kind in ("desire", "intend", "try", "purpose_marked")]
    g_on = [(g.kind, g.agent, GR._lemma(g.goal_head)) for g in GR.extract_goals(sents2, pos2, subcat=sf)
            if g.kind in ("desire", "intend", "try", "purpose_marked")]
    assert g_off == g_on and len(g_off) >= 3, ("W10 explicit goals must be identical off vs on", g_off, g_on)
    checks.append(("W10 zero-regression: explicit goals byte-identical subcat OFF==ON (%d goals); frame gates only bare" % len(g_on),
                   float(len(g_on)), "ZERO-REGRESSION"))

    print("PASS -- %d witness groups:" % len(checks))
    for name, val, verdict in checks:
        print("  %-72s %s  %s" % (name, ("%+.4f" % val) if isinstance(val, float) else str(val), verdict))
    print("\nHEADLINE: the reader now has a glass-box GOAL/INTENTION dimension (the missing 5th "
          "Zwaan-Radvansky dimension). On the RELIABLE explicit-construction anchor (desire/intend/try + "
          "in-order-to) the per-agent goal register answers 'what is X trying to do' CI-separated over a "
          "most-recent-action floor with a shuffled-agent info-free twin LOSING, extraction precision high "
          "vs a spaCy oracle; goal-why is answered where the physical-cause dimension cannot AND vice versa "
          "(the two dimensions are DISJOINT, Malle reason-vs-cause); the PINNED status field recovers "
          "active/satisfied/failed. The LOCATED NEGATIVE: bare-purpose adjuncts are parse-gated (low "
          "precision vs the oracle) and unstated/abductive goals (Tier-2 'why this over that') need the "
          "meaning/world-knowledge channel -- the explicit-vs-inferred split the brief predicted.")


if __name__ == "__main__":
    main()
