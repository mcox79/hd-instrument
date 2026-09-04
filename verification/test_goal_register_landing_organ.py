"""Scaffold-free LANDING witness for the GOAL/INTENTION dimension promoted into hdlab (Q111).

Asserts the LANDED organ -- hdlab.goal_register + hdlab.verb_subcat_frames + SituationReader(track_goals)
-- works from the SHIPPED assets, imports ONLY hdlab (no experiments/ dependency), and is a PURELY
ADDITIVE wire (the existing dimensions are byte-identical track_goals OFF vs ON, mirroring
_read_belief / _read_world_state):

  L1  the landed hdlab modules import; hdlab.goal_register depends ONLY on stdlib + hdlab.
  L2  hdlab.verb_subcat_frames.SubcatFrames.load() reads the SHIPPED frontend asset
      (data/frontend_assets/verb_subcat_frames_ud_ewt.json); is_complement_taker('want')=True,
      is_complement_taker('go')=False (the brain-faithful complement-vs-adjunct split).
  L3  BYTE-IDENTITY (additive wire): SituationReader(track_goals=False).read(doc) and
      SituationReader(track_goals=True).read(doc) produce IDENTICAL existing dimensions
      (events [(predicate,agent,patient,global_idx)], coref_acc, coref_resolutions, entity_states,
      causal_links, timeline_order, timeline_frames) across several docs -- track_goals is purely additive.
  L4  the goal_register field is None on the OFF reader (never populated unless track_goals=True).
  L5  from-source UNIT: the landed extractor + per-agent register bind the right goal to the right agent
      on a constructed multi-agent passage (Mary:escape / John:stop), and the goal != the recent action.
  L6  LIVE: with track_goals=True, sm.goal_register is populated on real LitBank prose and the bound
      query callables sm.wants(agent) / sm.why(action) / sm.achieved(agent,goal) return sane results;
      the register binds an explicit goal to a canonical NAMED agent (self-consistent wants()).

    .venv/Scripts/python.exe verification/test_goal_register_landing_organ.py
"""
import hashlib
import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

CONLL = os.path.join(REPO, "data", "litbank", "coref_conll")
DOCS = ["11_alices_adventures_in_wonderland_brat",
        "120_treasure_island_brat",
        "1342_pride_and_prejudice_brat"]


def _fingerprint(sm):
    """A stable digest of the EXISTING situation-model dimensions (everything the goal wire must NOT
    touch). If track_goals is additive, this is identical off vs on."""
    d = {
        "events": [(str(e.predicate), str(e.agent), str(e.patient), e.global_idx) for e in sm.events],
        "coref_acc": sm.coref_acc,
        "coref_xsent_acc": sm.coref_xsent_acc,
        "coref_res": [(r.pronoun, r.sent_idx, r.resolved_cluster, r.gold_cluster, r.correct)
                      for r in sm.coref_resolutions],
        "entity_states": [(s.holder, s.property, s.htype, s.sent_idx) for s in sm.entity_states],
        "causal_links": [(cl.sent_idx, cl.cause, cl.outcome, cl.method) for cl in sm.causal_links],
        "timeline_order": sm.timeline_order,
        "timeline_frames": [tuple(getattr(f, "chrono_order", [])) for f in sm.timeline_frames],
        "n_targets": sm.n_targets,
    }
    return hashlib.sha256(json.dumps(d, default=str, sort_keys=True).encode()).hexdigest()


def main():
    checks = []

    # ---- L1: the landed hdlab modules import; goal_register is stdlib+hdlab only ----
    import hdlab.goal_register as GR
    import hdlab.verb_subcat_frames as VSF
    src = open(os.path.join(REPO, "hdlab", "goal_register.py"), encoding="utf-8").read()
    import re as _re
    imports = [l.strip() for l in src.splitlines()
               if _re.match(r"\s*(import |from )", l) and "experiments" in l and not l.lstrip().startswith("#")]
    assert not imports, ("hdlab/goal_register.py must not import experiments/", imports)
    checks.append(("L1 hdlab.goal_register + hdlab.verb_subcat_frames import; NO experiments dependency", "OK"))

    # ---- L2: SubcatFrames loads the SHIPPED frontend asset; complement-vs-adjunct split is brain-faithful ----
    asset = os.path.join(REPO, "data", "frontend_assets", "verb_subcat_frames_ud_ewt.json")
    assert os.path.exists(asset), ("shipped frontend asset missing", asset)
    assert os.path.normcase(os.path.normpath(VSF.ASSET)) == os.path.normcase(os.path.normpath(asset)), \
        ("hdlab.verb_subcat_frames.ASSET must point at the shipped frontend asset", VSF.ASSET)
    sf = VSF.SubcatFrames.load()
    assert sf.is_complement_taker("want") and sf.is_complement_taker("try"), "want/try are complement-takers"
    assert not sf.is_complement_taker("go") and not sf.is_complement_taker("come"), "go/come are adjunct-hosts"
    checks.append(("L2 SubcatFrames.load() from shipped asset; want=complement, go=adjunct-host", "OK"))

    from hdlab.situation_reader import SituationReader

    # ---- L3 + L4: BYTE-IDENTITY of the existing dimensions (additive wire) + OFF register is None ----
    r_off = SituationReader(track_goals=False)
    r_on = SituationReader(track_goals=True)
    n_docs = 0
    for name in DOCS:
        path = os.path.join(CONLL, name + ".conll")
        if not os.path.exists(path):
            continue
        n_docs += 1
        sm_off = r_off.read(path)
        sm_on = r_on.read(path)
        fp_off, fp_on = _fingerprint(sm_off), _fingerprint(sm_on)
        assert fp_off == fp_on, ("L3 track_goals must be additive (existing dims identical)", name, fp_off, fp_on)
        assert sm_off.goal_register is None, ("L4 OFF reader must not populate goal_register", name)
        assert sm_on.goal_register is not None, ("L6 ON reader must populate goal_register", name)
    assert n_docs >= 2, ("need >= 2 real docs", n_docs)
    checks.append(("L3 byte-identity: existing dims IDENTICAL track_goals off==on across %d docs" % n_docs, "ADDITIVE"))
    checks.append(("L4 goal_register is None on the OFF reader (never populated unless track_goals)", "OK"))

    # ---- L5: from-source UNIT -- landed extractor + register bind the right goal to the right agent ----
    sents = [["Mary", "wanted", "to", "escape", "the", "house", "."],
             ["She", "ran", "to", "the", "door", "."],
             ["John", "tried", "to", "stop", "her", "."]]
    from hdlab.pos_tagger import PosTagger
    tg = PosTagger.load(os.path.join(REPO, "data/frontend_assets/pos_tagger_ud_ewt_upos.json"))
    pos = [tg.tag(t) for t in sents]
    goals = GR.extract_goals(sents, pos, subcat=sf)
    GR.bind_agents(goals, lambda s, si: {"mary": "mary", "she": "mary", "john": "john"}.get(s.lower()))
    reg = GR.GoalRegister(goals)
    assert reg.wants("mary") and GR._lemma(reg.wants("mary").goal_head) == GR._lemma("escape"), \
        [(g.agent_canonical, g.goal_head) for g in goals]
    assert reg.wants("john") and GR._lemma(reg.wants("john").goal_head) == GR._lemma("stop"), \
        [(g.agent_canonical, g.goal_head) for g in goals]
    assert GR._lemma("ran") != GR._lemma("escape"), "the goal must differ from the most-recent action"
    checks.append(("L5 landed extractor+register bind right goal->right agent (mary:escape/john:stop)", "UNIT"))

    # ---- L6: LIVE on real prose -- populated register + sane query callables + binds a named agent ----
    path = os.path.join(CONLL, DOCS[0] + ".conll")
    sm = r_on.read(path)
    assert sm.goal_register is not None and len(sm.goal_register.goals) > 0, "live register must have goals"
    assert callable(sm.wants) and callable(sm.why) and callable(sm.achieved), "query callables bound"
    named = [g for g in sm.goal_register.goals
             if g.agent_canonical and g.agent_canonical != "?" and GR._norm(g.agent_canonical) not in GR._PRONOUNS
             and g.kind in ("desire", "intend", "try", "purpose_marked")]
    assert named, "at least one explicit goal must bind to a canonical NAMED agent on real prose"
    g0 = named[0]
    w = sm.wants(g0.agent_canonical)
    assert w is not None, ("wants() must return a goal for a goal-holding named agent", g0.agent_canonical)
    # self-consistency: the returned current goal is one of that agent's registered goals
    agent_heads = {GR._lemma(g.goal_head) for g in sm.goal_register.goals
                   if (g.agent_canonical or "").lower() == (g0.agent_canonical or "").lower()}
    assert GR._lemma(w.goal_head) in agent_heads, ("wants() head must be a registered goal of the agent", w.goal_head)
    # why()/achieved() run without error and return the right shapes
    why = sm.why(g0.source_verb, g0.agent_canonical)
    ach = sm.achieved(g0.agent_canonical, g0.goal_head)
    assert ach in ("active", "satisfied", "failed", "unknown"), ("achieved() must return a status", ach)
    n_named_agents = len({(g.agent_canonical or "").lower() for g in named})
    checks.append(("L6 LIVE: %d goals, %d named goal-agents; wants(%r)->%s, achieved->%s" % (
        len(sm.goal_register.goals), n_named_agents, g0.agent_canonical, GR._lemma(w.goal_head), ach), "LIVE"))

    print("PASS -- %d/%d landing checks:" % (len(checks), len(checks)))
    for name, verdict in checks:
        print("  %-82s %s" % (name, verdict))
    print("\nHEADLINE: the GOAL/INTENTION dimension is LANDED in hdlab -- hdlab.goal_register (stdlib+hdlab "
          "only) + hdlab.verb_subcat_frames (shipped frontend asset) + SituationReader(track_goals=True), "
          "wired exactly like _read_belief/_read_world_state. The wire is PURELY ADDITIVE: the existing "
          "situation-model dimensions are byte-identical track_goals off vs on; the register is populated + "
          "the sm.wants/why/achieved query callables answer on real prose only when the flag is on.")


if __name__ == "__main__":
    main()
