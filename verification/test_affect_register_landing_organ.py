"""Scaffold-free LANDING witness for the AFFECT/EMOTION dimension promoted into hdlab (Q111).

Asserts the LANDED organ -- hdlab.affect_register + hdlab.affect_lexicon + hdlab.psych_verb_frames +
SituationReader(track_affect) -- works from the SHIPPED assets, imports ONLY hdlab (no experiments/
dependency), and is a PURELY ADDITIVE wire (the existing dimensions are byte-identical track_affect OFF
vs ON, mirroring _read_goals / _read_belief / _read_world_state):

  L1  the landed hdlab modules import; hdlab.affect_register / affect_lexicon / psych_verb_frames depend
      ONLY on stdlib + hdlab (grep confirms NO experiments/ import in any of the three).
  L2  hdlab.affect_lexicon.AffectLexicon.load() reads the SHIPPED frontend asset
      (data/frontend_assets/Ratings_Warriner_et_al.csv) and hdlab.psych_verb_frames.PsychVerbFrames.load()
      reads the SHIPPED frontend asset (data/frontend_assets/psych_verb_transitivity_ud_ewt.json); the
      brain-faithful gate ('afraid' -> fear/-1) + experiencer split (fear=subject, frighten=object) hold.
  L3  BYTE-IDENTITY (additive wire): SituationReader(track_affect=False).read(doc) and
      SituationReader(track_affect=True).read(doc) produce IDENTICAL existing dimensions
      (events [(predicate,agent,patient,global_idx)], coref_acc, coref_resolutions, entity_states,
      causal_links, timeline_order, timeline_frames, GOAL_REGISTER) across several docs -- track_affect
      is purely additive.
  L4  the affect_register field is None on the OFF reader (never populated unless track_affect=True).
  L5  from-source UNIT: the landed extractor + per-character register bind the right emotion to the right
      experiencer on a constructed passage (Mary:afraid / the dog frightened John -> John is the experiencer).
  L6  LIVE: with track_affect=True, sm.affect_register is populated on real LitBank prose and the bound
      query callables sm.feels(char) / sm.valence_of(char) return a sane emotion (valence sign in {-1,0,1},
      a curated category) for a canonical NAMED experiencer.

    .venv/Scripts/python.exe verification/test_affect_register_landing_organ.py
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
    """A stable digest of the EXISTING situation-model dimensions (everything the affect wire must NOT
    touch, INCLUDING the goal register -- track_goals is default-on so it must be identical off vs on).
    If track_affect is additive, this is identical off vs on."""
    goals = []
    if getattr(sm, "goal_register", None) is not None:
        goals = [(str(g.agent_canonical), str(g.goal_head), str(g.goal_text), g.kind, g.status,
                  g.sent_idx, g.negated) for g in sm.goal_register.goals]
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
        "goal_register": goals,
        "n_targets": sm.n_targets,
    }
    return hashlib.sha256(json.dumps(d, default=str, sort_keys=True).encode()).hexdigest()


def main():
    checks = []

    # ---- L1: the landed hdlab modules import; all three are stdlib+hdlab only (no experiments) ----
    import hdlab.affect_register as AR
    import hdlab.affect_lexicon as AL
    import hdlab.psych_verb_frames as PVF
    import re as _re
    for mod in ("affect_register", "affect_lexicon", "psych_verb_frames"):
        src = open(os.path.join(REPO, "hdlab", mod + ".py"), encoding="utf-8").read()
        bad = [l.strip() for l in src.splitlines()
               if _re.match(r"\s*(import |from )", l) and "experiments" in l and not l.lstrip().startswith("#")]
        assert not bad, ("hdlab/%s.py must not import experiments/" % mod, bad)
    checks.append(("L1 hdlab.affect_register + affect_lexicon + psych_verb_frames import; NO experiments dep", "OK"))

    # ---- L2: the lexicon + frame load from the SHIPPED frontend assets; brain-faithful gate + split ----
    warr = os.path.join(REPO, "data", "frontend_assets", "Ratings_Warriner_et_al.csv")
    pvf_asset = os.path.join(REPO, "data", "frontend_assets", "psych_verb_transitivity_ud_ewt.json")
    assert os.path.exists(warr), ("shipped Warriner frontend asset missing", warr)
    assert os.path.exists(pvf_asset), ("shipped psych-verb frontend asset missing", pvf_asset)
    assert os.path.normcase(os.path.normpath(AL.WARRINER)) == os.path.normcase(os.path.normpath(warr)), \
        ("hdlab.affect_lexicon.WARRINER must point at the shipped frontend asset", AL.WARRINER)
    assert os.path.normcase(os.path.normpath(PVF.ASSET)) == os.path.normcase(os.path.normpath(pvf_asset)), \
        ("hdlab.psych_verb_frames.ASSET must point at the shipped frontend asset", PVF.ASSET)
    lex = AL.AffectLexicon.load()
    assert lex.is_emotion_word("afraid") and lex.category("afraid") == "fear" and lex.valence_sign("afraid") == -1
    assert lex.is_emotion_word("happy") and lex.valence_sign("happy") == 1
    assert not lex.is_emotion_word("war") and not lex.is_emotion_word("frightening")   # laden/causative EXCLUDED
    pvf = PVF.PsychVerbFrames.load()
    assert pvf.experiencer_position("fear") == "subject" and pvf.experiencer_position("frighten") == "object"
    checks.append(("L2 AffectLexicon + PsychVerbFrames load from shipped assets; afraid=fear/-1, frighten=object", "OK"))

    from hdlab.situation_reader import SituationReader

    # ---- L3 + L4: BYTE-IDENTITY of the existing dimensions (additive wire) + OFF register is None ----
    r_off = SituationReader(track_affect=False)
    r_on = SituationReader(track_affect=True)
    n_docs = 0
    for name in DOCS:
        path = os.path.join(CONLL, name + ".conll")
        if not os.path.exists(path):
            continue
        n_docs += 1
        sm_off = r_off.read(path)
        sm_on = r_on.read(path)
        fp_off, fp_on = _fingerprint(sm_off), _fingerprint(sm_on)
        assert fp_off == fp_on, ("L3 track_affect must be additive (existing dims identical)", name, fp_off, fp_on)
        assert sm_off.affect_register is None, ("L4 OFF reader must not populate affect_register", name)
        assert sm_on.affect_register is not None, ("L6 ON reader must populate affect_register", name)
    assert n_docs >= 2, ("need >= 2 real docs", n_docs)
    checks.append(("L3 byte-identity: existing dims IDENTICAL track_affect off==on across %d docs" % n_docs, "ADDITIVE"))
    checks.append(("L4 affect_register is None on the OFF reader (never populated unless track_affect)", "OK"))

    # ---- L5: from-source UNIT -- landed extractor + register bind the right emotion to the right experiencer ----
    sents = [["Mary", "was", "afraid", "."],
             ["The", "dog", "frightened", "John", "."]]
    from hdlab.pos_tagger import PosTagger
    tg = PosTagger.load(os.path.join(REPO, "data/frontend_assets/pos_tagger_ud_ewt_upos.json"))
    pos = [tg.tag(t) for t in sents]
    affects = AR.extract_affect(sents, pos, lex, pvf=pvf)
    # Mary (copular subject) is afraid; John (OBJECT of frighten) is the experiencer, not the dog (stimulus)
    assert any(a.experiencer == "mary" and a.emotion_cat == "fear" and a.valence_sign == -1
               for a in affects), [(a.experiencer, a.emotion_word, a.emotion_cat) for a in affects]
    j = [a for a in affects if a.kind == "psych_verb"]
    assert j and j[0].experiencer == "john" and j[0].stimulus == "dog", \
        [(a.experiencer, a.stimulus) for a in j]
    reg = AR.AffectRegister(affects)
    for a in affects:
        a.experiencer_canonical = a.experiencer
    reg = AR.AffectRegister(affects)
    assert reg.feels("john") is not None and reg.feels("john").emotion_cat == "fear"
    checks.append(("L5 landed extractor+register bind right emotion->right experiencer (mary:afraid / frighten->john)", "UNIT"))

    # ---- L6: LIVE on real prose -- populated register + sane query callables + a NAMED experiencer ----
    _PRON = {"he", "him", "his", "she", "her", "hers", "they", "them", "their", "it", "its",
             "himself", "herself", "themselves", "itself"}
    live = None
    total_affects = 0
    for name in DOCS:
        path = os.path.join(CONLL, name + ".conll")
        if not os.path.exists(path):
            continue
        sm = r_on.read(path)
        assert sm.affect_register is not None, ("live register must exist", name)
        assert callable(sm.feels) and callable(sm.valence_of) and callable(sm.feels_about), "callables bound"
        total_affects += len(sm.affect_register.affects)
        named = [a for a in sm.affect_register.affects
                 if a.experiencer_canonical and a.experiencer_canonical != "?"
                 and AR._norm(a.experiencer_canonical) not in _PRON and a.valence_sign is not None]
        if named and live is None:
            a0 = named[0]
            f = sm.feels(a0.experiencer_canonical)
            assert f is not None, ("feels() must return an emotion for a feeling named char", a0.experiencer_canonical)
            assert f.valence_sign in (-1, 0, 1), ("valence sign must be sane", f.valence_sign)
            vs = sm.valence_of(a0.experiencer_canonical)
            assert vs in (-1, 0, 1, None), ("valence_of must be sane", vs)
            # self-consistency: the returned current emotion is one of that char's registered affects
            char_words = {x.emotion_word for x in sm.affect_register.affects
                          if (x.experiencer_canonical or "").lower() == (a0.experiencer_canonical or "").lower()}
            assert f.emotion_word in char_words, ("feels() must be a registered affect of the char", f.emotion_word)
            live = (name, a0.experiencer_canonical, f.emotion_word, f.emotion_cat, f.valence_sign, vs,
                    len(sm.affect_register.affects))
    assert live is not None, ("at least one canonical NAMED experiencer with a valid emotion across the docs",
                              total_affects)
    checks.append(("L6 LIVE: feels(%r)->%s/%s val=%s (%d affects in %s)" % (
        live[1], live[2], live[3], live[4], live[6], live[0]), "LIVE"))

    print("PASS -- %d/%d landing checks:" % (len(checks), len(checks)))
    for name, verdict in checks:
        print("  %-92s %s" % (name, verdict))
    print("\nHEADLINE: the AFFECT/EMOTION dimension is LANDED in hdlab -- hdlab.affect_register (stdlib+hdlab "
          "only) + hdlab.affect_lexicon + hdlab.psych_verb_frames (shipped frontend assets) + "
          "SituationReader(track_affect=True), wired exactly like _read_goals. The wire is PURELY ADDITIVE: the "
          "existing situation-model dimensions (incl. the goal register) are byte-identical track_affect off vs "
          "on; the register is populated + the sm.feels/valence_of/feels_about query callables answer on real "
          "prose only when the flag is on.")


if __name__ == "__main__":
    main()
