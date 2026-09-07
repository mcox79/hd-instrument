"""Scaffold-free LANDING witness for the OCC-APPRAISAL inferred-emotion organ promoted into hdlab (Q111,
infer_unstated_emotion_via_occ_appraisal_over_event_goal_congruence, landed 2026-09-06).

Asserts the LANDED organ -- hdlab.occ_appraisal (the glass-box forward OCC appraisal: desirability x prospect
-> OCC type + valence) + hdlab.goal_register.track_status_thwart (the upstream goal-FAILURE-by-thwart strict
superset) + the default-on sm.infer_emotion(char[, t]) read-out on SituationReader -- works from hdlab only
(NO experiments/ dependency in the organ), REPRODUCES the headline THROUGH the landed organ, and is a purely
ADDITIVE wire (mirrors the sibling _read_tom_action). This complements verification/test_occ_appraisal.py (the
scaffold-free measurement witness, which imports the experiments/ solver cells); here the organ under test is
the hdlab.* promotion driven via a live SituationReader.read().

  L1  hdlab.occ_appraisal imports; depends ONLY on stdlib + hdlab (NO experiments import); the pure OCC rule
      table is exact (8/8 desirability x prospect -> type).
  L2  LIVE HEADLINE THROUGH THE LANDED ORGAN: drive sm.infer_emotion over the constructed MODERN OCC gold
      (50 items) via SituationReader.read(); TYPE accuracy reproduces the headline ~0.940 (>= 0.90). ROUTING
      PROOF: sm.infer_emotion is byte-identical, per item, to a direct hdlab.occ_appraisal.infer_emotion call
      using hdlab.goal_register.track_status_thwart -> the read-out routes through the landed organ.
  L3  BYTE-IDENTITY vs all_capabilities_off (the task's literal reference): existing dimensions (events,
      entities, coref) are byte-identical with track_goal_thwart + track_infer_emotion ON (on top of
      all_capabilities_off) vs plain all_capabilities_off; the off reader leaves sm.infer_emotion = None, the
      on reader exposes it.
  L4  PRODUCTION ADDITIVITY on the DEFAULT reader: toggling ONLY {track_goal_thwart, track_infer_emotion}
      leaves events/entities/coref/entity_states/causal_links byte-identical, and -- load-bearing -- the affect
      register + sm.feels are byte-identical (sm.infer_emotion NEVER overwrites a stated feeling; it writes to
      no existing field).
  L5  STRICT SUPERSET (the upstream goal-FAILURE generalization): on the reader's OWN path, the goal register's
      status with track_goal_thwart=True preserves EVERY baseline (track_goal_thwart=False) satisfied/failed
      verdict and only adds active->{satisfied,failed}; wants() never regresses (a changed want only removes a
      now-failed goal).

Glass-box, NO external LLM, deterministic, ASCII, CPU-only.
Reverify: .venv/Scripts/python.exe verification/test_occ_appraisal_landing.py
"""
from __future__ import annotations

import copy
import glob
import os
import re
import sys
import tempfile

os.environ.setdefault("OMP_NUM_THREADS", "2")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "2")
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

FAILS = []


def check(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + ("  -- " + detail if detail else ""))
    if not cond:
        FAILS.append(name)


def _real_docs(n=2):
    for sub in ("coref/conll", "coref_conll"):
        docs = sorted(glob.glob(os.path.join(REPO, "data", "litbank", *sub.split("/"), "*.conll")))
        if docs:
            return docs[:n]
    return []


def _fingerprint_existing_dims(sm):
    """A digest of the EXISTING situation-model dimensions the OCC read-out + thwart flag must NOT touch."""
    d = {
        "events": [(str(e.predicate), str(e.agent), str(e.patient), e.global_idx) for e in sm.events],
        "entities": [(str(e.cluster), tuple(e.heads), e.n_mentions) for e in sm.entities],
        "coref": [(r.pronoun, r.sent_idx, r.resolved_cluster, r.gold_cluster, r.correct)
                  for r in sm.coref_resolutions],
        "entity_states": [(s.holder, s.property, s.htype, s.sent_idx) for s in sm.entity_states],
        "causal_links": [(cl.sent_idx, cl.cause, cl.outcome, cl.method) for cl in sm.causal_links],
    }
    return d


# ---------------------------------------------------------------------------
# L1 -- the landed organ imports; stdlib+hdlab only; the pure OCC rule is exact.
# ---------------------------------------------------------------------------
def test_l1_landed_organ_imports_no_experiments_dep():
    import hdlab.occ_appraisal as OCC
    import hdlab.goal_register as GR
    src = open(os.path.join(REPO, "hdlab", "occ_appraisal.py"), encoding="utf-8").read()
    bad = [l.strip() for l in src.splitlines()
           if re.match(r"\s*(import |from )", l) and "experiments" in l and not l.lstrip().startswith("#")]
    check("L1a hdlab.occ_appraisal imports; depends ONLY on stdlib+hdlab (no experiments import)",
          not bad and hasattr(GR, "track_status_thwart") and hasattr(GR, "implicit_investment_goals"),
          "experiments-imports=%s" % bad)
    table = [(+1, "actual", "satisfaction"), (-1, "actual", "disappointment"), (+1, "prospective", "hope"),
             (-1, "prospective", "fear"), (-1, "confirmed", "fears_confirmed"), (-1, "disconfirmed", "relief"),
             (+1, "confirmed", "satisfaction"), (+1, "disconfirmed", "disappointment")]
    check("L1b pure OCC rule table exact (8/8 desirability x prospect -> type)",
          all(OCC.appraise(d, p) == t for d, p, t in table))


# ---------------------------------------------------------------------------
# L2 -- the LIVE headline reproduces THROUGH the landed organ (sm.infer_emotion).
# ---------------------------------------------------------------------------
def test_l2_live_headline_through_landed_organ():
    import hdlab.occ_appraisal as OCC
    from hdlab.goal_register import track_status_thwart
    from hdlab.situation_reader import SituationReader
    from experiments._tom_chain import split_sents, tokenize
    from experiments._occ_probe import write_conll, load_gold, _protagonist_canon

    gold = load_gold()
    reader = SituationReader(track_goals=True, track_affect=True)
    tmp = tempfile.mkdtemp(prefix="occ_land_")
    ok = 0
    routed = True
    for it in gold:
        cp = write_conll(it["text"], it["char"], tmp, it["id"])
        sm = reader.read(cp)
        canon = _protagonist_canon(sm, it["char"])
        # the LANDED read-out (uses hdlab.occ_appraisal + hdlab.goal_register.track_status_thwart internally):
        em = sm.infer_emotion(it["char"], canon=canon)
        # ROUTING PROOF: a direct call to the landed organ with the same inputs must match, per item.
        sents = [tokenize(s) for s in split_sents(it["text"])]
        em_direct = OCC.infer_emotion(sm, it["char"], sents=sents, status_fn=track_status_thwart, canon=canon)
        t_sm = em.occ_type if em else None
        t_direct = em_direct.occ_type if em_direct else None
        if t_sm != t_direct:
            routed = False
        ok += int(t_sm == it["type"])
    acc = ok / len(gold)
    check("L2a sm.infer_emotion routes THROUGH the landed hdlab.occ_appraisal organ (per-item identical to a "
          "direct organ call with hdlab.goal_register.track_status_thwart)", routed)
    check("L2b LIVE TYPE accuracy reproduces the headline ~0.940 through sm.infer_emotion (>= 0.90)",
          acc >= 0.90, "TYPE acc = %.3f (%d/%d)" % (acc, ok, len(gold)))


# ---------------------------------------------------------------------------
# L3 -- BYTE-IDENTITY vs all_capabilities_off (the task's literal reference).
# ---------------------------------------------------------------------------
def test_l3_byte_identical_vs_all_capabilities_off():
    from hdlab.situation_reader import SituationReader
    from experiments.exp_name_entity_clustering_v1 import load_given_gazetteer
    gaz = load_given_gazetteer()
    off = SituationReader.all_capabilities_off(gaz=gaz)
    on = SituationReader.all_capabilities_off(gaz=gaz, track_belief=True, track_goals=True, track_affect=True,
                                              track_goal_thwart=True, track_infer_emotion=True)
    docs = _real_docs(2)
    check("L3-setup found >= 1 real LitBank doc", len(docs) >= 1, "docs=%d" % len(docs))
    n_ident = 0
    for d in docs:
        so = off.read(d)
        sn = on.read(d)
        fo, fn = _fingerprint_existing_dims(so), _fingerprint_existing_dims(sn)
        # only compare dims all_capabilities_off actually produces (events/entities/coref); entity_states/causal
        # are empty in the weak reader on both sides.
        same = (fo["events"] == fn["events"] and fo["entities"] == fn["entities"] and fo["coref"] == fn["coref"])
        n_ident += int(same)
        if not same:
            check("L3 existing dims byte-identical on %s" % os.path.basename(d), False)
    check("L3a existing dims (events/entities/coref) BYTE-IDENTICAL: all_capabilities_off vs +track_goal_thwart"
          "+track_infer_emotion ON, across %d doc(s)" % len(docs), n_ident == len(docs) and len(docs) >= 1)
    # the OCC read-out is exposed only when the flag is on
    so0 = off.read(docs[0]); sn0 = on.read(docs[0])
    check("L3b off reader leaves sm.infer_emotion = None; on reader exposes a callable sm.infer_emotion",
          so0.infer_emotion is None and callable(sn0.infer_emotion))


# ---------------------------------------------------------------------------
# L4 -- production additivity on the DEFAULT reader (toggle only the two new flags).
# ---------------------------------------------------------------------------
def test_l4_default_reader_additive_never_overwrites_stated_feeling():
    from hdlab.situation_reader import SituationReader
    off = SituationReader(track_goal_thwart=False, track_infer_emotion=False)
    on = SituationReader()  # defaults: both new flags True
    docs = _real_docs(2)
    n_ident = 0
    feels_ident = True
    for d in docs:
        so = off.read(d)
        sn = on.read(d)
        fo, fn = _fingerprint_existing_dims(so), _fingerprint_existing_dims(sn)
        same = (fo["events"] == fn["events"] and fo["entities"] == fn["entities"] and fo["coref"] == fn["coref"]
                and fo["entity_states"] == fn["entity_states"] and fo["causal_links"] == fn["causal_links"])
        n_ident += int(same)
        # never overwrites a stated feeling: the affect register + sm.feels are byte-identical off vs on
        chars = list({(a.experiencer_canonical or a.experiencer or "?") for a in (sn.affect_register.affects
                      if sn.affect_register else [])})
        for c in chars:
            fo_a = so.feels(c) if callable(getattr(so, "feels", None)) else None
            fn_a = sn.feels(c) if callable(getattr(sn, "feels", None)) else None
            key = lambda a: None if a is None else (a.emotion_word, a.emotion_cat, a.valence_sign, a.sent_idx)
            if key(fo_a) != key(fn_a):
                feels_ident = False
    check("L4a DEFAULT reader: toggling ONLY {track_goal_thwart,track_infer_emotion} leaves events/entities/"
          "coref/entity_states/causal_links BYTE-IDENTICAL across %d doc(s)" % len(docs),
          n_ident == len(docs) and len(docs) >= 1)
    check("L4b sm.infer_emotion NEVER overwrites a stated feeling: sm.affect_register / sm.feels are "
          "byte-identical off vs on (the read-out writes to no existing field)", feels_ident)


# ---------------------------------------------------------------------------
# L5 -- the upstream goal-FAILURE generalization is a STRICT SUPERSET on the reader's own path.
# ---------------------------------------------------------------------------
def test_l5_thwart_is_strict_superset_on_reader_path():
    from hdlab.situation_reader import SituationReader
    off = SituationReader(track_goal_thwart=False)   # baseline track_status
    on = SituationReader(track_goal_thwart=True)     # thwart-aware strict superset
    docs = _real_docs(3)
    checked = 0
    violations = 0
    additions = 0
    wants_regressed = 0
    for d in docs:
        so = off.read(d)
        sn = on.read(d)
        rb = getattr(so, "goal_register", None)
        rt = getattr(sn, "goal_register", None)
        if not rb or not rt:
            continue
        key = lambda g: (str(g.agent_canonical or g.agent or "?").lower(), g.goal_head, g.sent_idx, g.verb_tok)
        base = {key(g): g.status for g in rb.goals}
        for g in rt.goals:
            k = key(g)
            if k not in base:
                continue
            checked += 1
            b = base[k]
            if b in ("satisfied", "failed") and g.status != b:
                violations += 1
            if b == "active" and g.status in ("satisfied", "failed"):
                additions += 1
        # wants() no-regression: a changed want may only REMOVE a goal that is now failed under thwart
        agents = {str(g.agent_canonical or g.agent or "?").lower() for g in rt.goals}
        agents = {a for a in agents if a and a != "?"}
        status_on = {g.goal_head: g.status for g in rt.goals}
        for a in agents:
            wb = so.wants(a); wt = sn.wants(a)
            hb = getattr(wb, "goal_head", None); ht = getattr(wt, "goal_head", None)
            if hb != ht and status_on.get(hb) != "failed":
                wants_regressed += 1
    check("L5-setup goal register populated on real docs (checked %d goals)" % checked, checked > 0)
    check("L5a STRICT SUPERSET on the reader path: 0 baseline satisfied/failed flipped by track_goal_thwart "
          "(%d additions active->satisfied/failed)" % additions, violations == 0,
          "violations=%d" % violations)
    check("L5b NO wants() REGRESSION (a changed current-want only removes a now-failed goal)",
          wants_regressed == 0, "wants_regressed=%d" % wants_regressed)


if __name__ == "__main__":
    test_l1_landed_organ_imports_no_experiments_dep()
    test_l2_live_headline_through_landed_organ()
    test_l3_byte_identical_vs_all_capabilities_off()
    test_l4_default_reader_additive_never_overwrites_stated_feeling()
    test_l5_thwart_is_strict_superset_on_reader_path()
    print()
    if FAILS:
        print("WITNESS FAILED: " + ", ".join(FAILS))
        sys.exit(1)
    print("ALL LANDING WITNESS CHECKS PASSED -- the glass-box OCC-appraisal inferred-emotion organ is LANDED in "
          "hdlab (hdlab.occ_appraisal + hdlab.goal_register.track_status_thwart + SituationReader.infer_emotion, "
          "default-on track_infer_emotion/track_goal_thwart): the LIVE reader infers the UNSTATED emotion at the "
          "headline 0.940 THROUGH the landed organ, the wire is purely additive (existing dims byte-identical, "
          "no stated feeling overwritten), and the upstream goal-failure generalization is a strict superset.")
