"""Organ-landing witness for chain_belief_and_goal_into_theory_of_mind_inference_intention_and_false_belief
(Q111, landed 2026-09-06): the glass-box FORWARD mentalizing chain (believes(A,F,t) x wants(A) -> action,
reading the action off the BELIEVED state) promoted into hdlab.theory_of_mind and wired as a read()-time query
callable on the SituationReader (sm.predict_action / sm.will_act_on / sm.attribute_belief, default-on
track_tom_action). Reuses the LIVE organs hdlab.belief_timeline (rTPJ belief) + hdlab.goal_register (dmPFC
desire) -- rebuilds neither.

  W1 LIVE READER acts off the BELIEVED state on a FALSE-belief item. Through SituationReader.read() on a
     Sally-Anne conll (Anna does not see the letter moved drawer->shelf), the reader's OWN extraction gives
     sm.believes='drawer' (a stale FALSE belief, sm.knows='stale') while reality='shelf'. sm.predict_action
     acts off the BELIEVED value (PROCEED when believed==desired) where a reality-only baseline DIVERGES
     (FETCH) -- so the chain reads believes, not reality. The default-off reader exposes no such callable.
  W2 BigToM NUMBERS reproduced THROUGH THE LANDED ORGAN. The composition rule + present-tense percept gate +
     COS cues used by the BigToM measurement are asserted to BE hdlab.theory_of_mind (identity check), and the
     arm accuracies recompute to the validated headline: belief CHAIN 0.849 (FB 0.871) vs reality floor 0.500
     (FB 0.000, provably), CHAIN_NOFIX ~chance, ORACLE_BELIEF 1.000, both info-free twins LOSE on FB; action
     CHAIN 0.655 (FB 0.669).
  W3 ADDITIVE SAFETY: track_tom_action is a PURE ADD. Off-vs-on on a real LitBank doc, every existing dimension
     is BYTE-IDENTICAL (events, entities, coref, and -- load-bearing -- sm.believes and sm.wants outputs); the
     off reader leaves sm.predict_action/will_act_on/attribute_belief = None, the on reader exposes them.

Glass-box, NO external LLM, deterministic, ASCII, CPU-only.
Reverify: .venv/Scripts/python.exe verification/test_tom_chain_landing.py

NOTE: readers are built with track_bridges=False to ISOLATE this witness from the CONCURRENT meaning-channel
(bridging) integration landing into the same file; it is orthogonal to the ToM action dimension under test.
"""
from __future__ import annotations

import os
import re
import sys
import glob
import tempfile

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

FAILS = []


def check(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + ("  -- " + detail if detail else ""))
    if not cond:
        FAILS.append(name)


def _reader(**kw):
    from hdlab.situation_reader import SituationReader
    from experiments.exp_name_entity_clustering_v1 import load_given_gazetteer
    # track_bridges=False: isolate from the concurrent meaning-channel integration (orthogonal to ToM).
    kw.setdefault("track_bridges", False)
    return SituationReader(gaz=load_given_gazetteer(), **kw)


def _tok(s):
    return re.findall(r"[A-Za-z']+|[0-9]+|[.,;:!?]", s)


def _sents(p):
    return [x.strip() for x in re.split(r"(?<=[.!?])\s+", p.strip()) if x.strip()]


def _write_conll(text, alias_set, pid, outdir):
    """LitBank-style CoNLL with one protagonist coref cluster (0) on the agent name + 3p pronouns."""
    path = os.path.join(outdir, pid + ".conll")
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write("#begin document (%s); part 0\n" % pid)
        for s in _sents(text):
            for i, tk in enumerate(_tok(s)):
                bare = tk.lower().strip(".,;:!?\"'()")
                coref = "(0)" if bare in alias_set else "_"
                f.write("\t".join([pid, "0", str(i), tk] + ["_"] * 8 + [coref]) + "\n")
            f.write("\n")
    return path


# ---------------------------------------------------------------------------
# W1 -- the LIVE reader acts off the BELIEVED state on a false-belief item.
# ---------------------------------------------------------------------------
def test_w1_live_reader_acts_off_believed_state():
    from hdlab.scene_segment import parse_conll_sentences
    from hdlab.belief_timeline import reality_at
    from hdlab.perceptual_access_ledger import PerceptualAccessLedger
    from hdlab.theory_of_mind import compose_action
    import experiments._belief_reader as BR

    outdir = tempfile.mkdtemp()
    text = ("Anna put the letter in the drawer. Anna went outside to play. While Anna was away, "
            "Ben moved the letter from the drawer to the shelf. Anna did not see Ben move the letter.")
    alset = {"anna", "she", "her", "hers"}
    aliases = ["Anna", "she", "her"]
    fact = {"fact_type": "location", "fact_aliases": ["letter", "it"], "value_vocab": ["drawer", "shelf"]}
    conll = _write_conll(text, alset, "tom_fb_sallyanne", outdir)

    off = _reader(track_tom_action=False).read(conll)
    on = _reader(track_tom_action=True).read(conll)
    check("W1a default-off exposes NO ToM callables; default-on exposes predict_action/will_act_on/attribute_belief",
          off.predict_action is None and off.will_act_on is None and off.attribute_belief is None
          and callable(on.predict_action) and callable(on.will_act_on) and callable(on.attribute_belief))

    sents = parse_conll_sentences(conll)
    T = float(len(sents)) + 1.0
    believed = on.believes(aliases, fact, T)
    knows = on.knows(aliases, fact, T)
    # reality-only baseline: what the reader's OWN extraction says F actually is (the beliefless floor)
    led = PerceptualAccessLedger()
    ev, ob, ag, _r, _b, _s = BR.drive(sents, {i: [] for i in range(len(sents))}, fact, aliases, led)
    reality = reality_at(ev, fact["fact_aliases"][0].lower(), T)
    check("W1b the reader's OWN extraction yields a FALSE belief (believes != reality, knows='stale')",
          believed is not None and reality is not None and believed != reality and knows == "stale",
          "believes=%r knows=%r reality=%r" % (believed, knows, reality))

    # the agent WANTS the letter where she believes she left it (desired == the believed/stale value)
    desired = believed
    act = on.predict_action(aliases, fact, T, desired=desired)
    act_alias = on.will_act_on(aliases, fact, T, desired=desired)
    floor = compose_action(reality, desired)   # the reality-only reader acts on the TRUE state
    check("W1c sm.predict_action acts OFF THE BELIEVED STATE (PROCEED) where the reality-only baseline DIVERGES "
          "(FETCH) -- the chain reads believes, not reality (the false-belief action)",
          act == "PROCEED" and floor == "FETCH" and act != floor and act_alias == act,
          "predict_action(off believes)=%r  reality-only=%r  (desired=%r)" % (act, floor, desired))

    # INVERSE: the SAME engine attributes the belief the observed action implies (Baker 2017 intentional stance)
    b_from_proceed = on.attribute_belief(aliases, fact, "PROCEED", desired=desired)
    b_from_fetch = on.attribute_belief(aliases, fact, "FETCH", desired=desired)
    check("W1d sm.attribute_belief runs the SAME engine INVERSE: PROCEED -> believed==desired ('drawer'); "
          "FETCH -> the OTHER candidate ('shelf')",
          b_from_proceed == desired and b_from_fetch == "shelf",
          "PROCEED->%r  FETCH->%r" % (b_from_proceed, b_from_fetch))


# ---------------------------------------------------------------------------
# W2 -- the BigToM numbers reproduce THROUGH THE LANDED ORGAN.
# ---------------------------------------------------------------------------
def test_w2_bigtom_numbers_through_landed_organ():
    import numpy as np
    import hdlab.theory_of_mind as TOM
    import experiments.exp_tom_chain_belief_goal_action_v1 as E
    from experiments._tom_bigtom import load_bigtom

    # ROUTING PROOF: the composition rule + present-tense gate + COS cues the measurement uses ARE the landed
    # organ (not a private copy) -- so the numbers below are produced THROUGH hdlab.theory_of_mind.
    routed = (E.C.forward_action is TOM.forward_action
              and E.C.perceives_change is TOM.perceives_change
              and E.C.attribute_belief_from_action is TOM.attribute_belief_from_action
              and E.C._COS_CUES is TOM._COS_CUES)
    check("W2a the BigToM measurement routes THROUGH the landed organ (forward_action / perceives_change / "
          "attribute_belief_from_action / _COS_CUES are hdlab.theory_of_mind, identity-checked)", routed)

    items = load_bigtom(tasks=("action",))
    rows = E._predict_all(items)                 # runs C.* (=> hdlab.theory_of_mind) for every arm
    n = len(rows)
    # info-free twins: reproduce the cell's seeded permutation EXACTLY (RandomState(20260906), perms first)
    rng = np.random.RandomState(20260906)
    perm_obs = rng.permutation(n)
    perm_bel = rng.permutation(n)
    for i, r in enumerate(rows):
        obs_sh = rows[perm_obs[i]]["obs"]
        bel_sh = rows[perm_bel[i]]["bel_fix"]
        r["_arms"] = E._correct_arms(r, observed_shuffle=(bool(obs_sh) if obs_sh is not None else False),
                                     belief_shuffle=bel_sh)

    def acc(arm, ti, subset=None):
        return E._acc(rows, arm, ti, subset)

    # BELIEF task (ti=0): the pure, floor-0.000 discriminator
    bC, bCfb = acc("CHAIN", 0), acc("CHAIN", 0, "FB")
    bF, bFfb = acc("REALITY_FLOOR", 0), acc("REALITY_FLOOR", 0, "FB")
    bN = acc("CHAIN_NOFIX", 0)
    bO = acc("ORACLE_BELIEF", 0)
    twP, twB = acc("TWIN_PERCEPT", 0, "FB"), acc("TWIN_BELIEF", 0, "FB")
    check("W2b BELIEF CHAIN 0.849 (FB 0.871) vs reality floor 0.500 (FB 0.000, provably) -- through the organ",
          abs(bC - 0.849) < 0.01 and abs(bCfb - 0.871) < 0.01 and abs(bF - 0.500) < 0.01 and bFfb == 0.0,
          "CHAIN %.3f (FB %.3f) | floor %.3f (FB %.3f)" % (bC, bCfb, bF, bFfb))
    check("W2c the UPSTREAM FIX is load-bearing (CHAIN_NOFIX ~chance %.3f) and the composition is EXACT with "
          "oracle belief (%.3f) -> the gap is EXTRACTION" % (bN, bO),
          bN < 0.52 and bO >= 0.999)
    check("W2d both info-free twins LOSE on the FALSE-belief subset (percept-shuffle %.3f, belief-shuffle %.3f "
          "both << CHAIN FB %.3f)" % (twP, twB, bCfb),
          twP < bCfb - 0.2 and twB < bCfb - 0.2)

    # ACTION task (ti=1): the belief x desire composition
    aC, aCfb = acc("CHAIN", 1), acc("CHAIN", 1, "FB")
    aFfb = acc("REALITY_FLOOR", 1, "FB")
    check("W2e ACTION CHAIN 0.655 (FB 0.669) beats the reality floor on FB (%.3f) -- the belief x desire "
          "composition through the organ" % aFfb,
          abs(aC - 0.655) < 0.01 and abs(aCfb - 0.669) < 0.01 and aCfb > aFfb + 0.3,
          "CHAIN %.3f (FB %.3f) | floor FB %.3f" % (aC, aCfb, aFfb))


# ---------------------------------------------------------------------------
# W3 -- additive safety: track_tom_action is a PURE ADD (existing dimensions byte-identical off vs on).
# ---------------------------------------------------------------------------
def test_w3_additive_safety_byte_identical():
    from hdlab.scene_segment import parse_conll_sentences
    doc = sorted(glob.glob(os.path.join(REPO, "data/litbank/coref/conll", "*.conll")))[0]
    off = _reader(track_tom_action=False).read(doc)
    on = _reader(track_tom_action=True).read(doc)

    check("W3a off reader leaves sm.predict_action/will_act_on/attribute_belief = None; on reader exposes them",
          off.predict_action is None and off.will_act_on is None and off.attribute_belief is None
          and callable(on.predict_action) and callable(on.will_act_on) and callable(on.attribute_belief))

    ev_off = [(e.global_idx, e.predicate, e.agent, e.patient) for e in off.events]
    ev_on = [(e.global_idx, e.predicate, e.agent, e.patient) for e in on.events]
    ent_off = [(e.cluster, tuple(e.heads), e.n_mentions) for e in off.entities]
    ent_on = [(e.cluster, tuple(e.heads), e.n_mentions) for e in on.entities]
    cor_off = [(r.correct, r.sent_dist) for r in off.coref_resolutions]
    cor_on = [(r.correct, r.sent_dist) for r in on.coref_resolutions]
    check("W3b existing dimensions BYTE-IDENTICAL off vs on (events, entities, coref)",
          ev_off == ev_on and ent_off == ent_on and cor_off == cor_on,
          "events %d==%d entities %d==%d coref %d==%d" % (len(ev_off), len(ev_on), len(ent_off), len(ent_on),
                                                          len(cor_off), len(cor_on)))

    # load-bearing: the ToM query must NOT perturb the belief/goal EXTRACTION it consumes
    sents = parse_conll_sentences(doc)
    fact = {"fact_type": "location", "fact_aliases": ["letter", "it"], "value_vocab": ["drawer", "shelf", "box", "table"]}
    ag = ["he", "him", "his"]
    bel_ident = all(off.believes(ag, fact, t) == on.believes(ag, fact, t) for t in (1.0, 3.0, 5.0))
    know_ident = all(off.knows(ag, fact, t) == on.knows(ag, fact, t) for t in (1.0, 3.0, 5.0))
    agents = list({(g.agent_canonical or g.agent or "?") for g in on.goal_register.goals}) if on.goal_register else []
    def _w(sm, a):
        g = sm.wants(a)
        return None if g is None else (g.goal_head, g.goal_text, g.status, g.negated)
    want_ident = (off.goal_register is not None and on.goal_register is not None
                  and all(_w(off, a) == _w(on, a) for a in agents))
    check("W3c the belief + goal EXTRACTION sm.believes/knows/wants consume is BYTE-IDENTICAL off vs on "
          "(the ToM chain is a read-only query; it changes no extraction)",
          bel_ident and know_ident and want_ident,
          "believes-identical=%s knows-identical=%s wants-identical=%s (n_agents=%d)"
          % (bel_ident, know_ident, want_ident, len(agents)))


if __name__ == "__main__":
    test_w1_live_reader_acts_off_believed_state()
    test_w2_bigtom_numbers_through_landed_organ()
    test_w3_additive_safety_byte_identical()
    print()
    if FAILS:
        print("WITNESS FAILED: " + ", ".join(FAILS))
        sys.exit(1)
    print("ALL LANDING WITNESS CHECKS PASSED")
