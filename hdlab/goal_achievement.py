"""hdlab/goal_achievement.py -- glass-box narrative goal/desire-FULFILLMENT verdict (2026-08-08).

Three independent, inspectable channels, composed by an explicit precedence policy. On real DesireDB
(Rahimtoroghi, Wu, Wang, Anand & Walker, SIGDIAL 2017; n=80 balanced seed 20260808) this edges above
the tuned valence+negation RULE: macro-F1 0.686 vs 0.620 (suggestive, ~1.3 SE / net +3 at n=80).

  Channel R (goal-relative action-relation, the differentiated signal): did the WANTED action recur in
    the outcome (met up / did just that / took what was offered = MET) or get negated/refused/blocked
    (couldn't / would not give = UNMET). Reuses goal_typing.find_desired_state + WordNet verb-synonyms
    + a pro-form completion cue + goal_typing._verb_negated_before / refusal cues.
  Channel V (outcome valence, the coverage bulk): opinion_lexicon (Hu & Liu) + the owned
    wordnet_polarity_propagation.dictionary_lookup for verbs, negation-flipped, voted. Degrades to
    no-decision if nltk opinion_lexicon is unavailable (never raises).
  Channel C (contrast/concession discourse override, PDTB/SDRT defeasible): a closed-class contrast
    connective ('but/yet/however/instead/only to/...') DEFEATS a Fulfilled default (denial-of-
    expectation). Validated by DesireDB's own ablation (a single But-Present feature ~ their LSTM).

PRECEDENCE: R (when it fires) -> V (when it fires) -> corpus majority (Fulfilled); then Channel C
one-directional override (a Fulfilled base + a contrast connective -> Unfulfilled). This crude broad
composition is the OPERATING POINT: on messy real prose, coarse high-coverage rules beat principled-
narrow ones (synonym-tightening, referent-gating, and denial-scoping all measured NET-WORSE this arc).

Returns a glass-box trace (which channel decided + why). NO LLM at inference; every organ is owned or a
vetted external lexicon (WordNet / opinion_lexicon). Extensible: add a channel (e.g. AVOID-goal +
Talmy force-dynamics) as another function without changing the others.
"""
from __future__ import annotations

import os
import re
from typing import Optional, Tuple

from hdlab import goal_typing as _gt
from hdlab import wordnet_polarity_propagation as _wpp
from nltk.corpus import wordnet as _wn

MAJORITY_CLASS = "Fulfilled"

# closed-class contrast/concession/substitution connectives + strong blocks (Channel C).
_CONNECTIVES = ("but ", "yet ", "however", "instead", "nevertheless", "nonetheless", "although",
                "though ", "only to ", "unfortunately", "sadly", "despite", "no more",
                "would not", "could not", "couldn't", "wouldn't", "never got", "never have")
_REFUSAL = ("could not", "couldn't", "would not", "wouldn't", "did not", "didn't", "never",
            "unable", "failed to", "but no", "no one would", "wouldnt", "couldnt")
_AUX_STOP = frozenset({"be", "is", "are", "was", "were", "been", "being", "am", "have", "has", "had",
                       "do", "does", "did", "will", "would", "shall", "should", "can", "could", "may",
                       "might", "must", "let", "not", "the", "a", "an", "of", "to", "and", "i", "he",
                       "she", "it", "we", "they", "you", "my", "his", "her"})
_PROFORMS = ("did just that", "did that", "did it", "did so", "did the same", "just that", "sure enough")

_opinion_cache = None


def _opinion() -> Tuple[frozenset, frozenset]:
    """(positive_set, negative_set) from nltk opinion_lexicon; empty (graceful) if unavailable."""
    global _opinion_cache
    if _opinion_cache is None:
        try:
            from nltk.corpus import opinion_lexicon
            _opinion_cache = (frozenset(opinion_lexicon.positive()), frozenset(opinion_lexicon.negative()))
        except Exception:
            _opinion_cache = (frozenset(), frozenset())
    return _opinion_cache


def _extend_goal(desire: str) -> str:
    """Light goal-recognition coverage: rewrite unrecognized governing verbs to 'wanted to'."""
    d = desire
    for pat in ("ached to", "ache to", "aching to", "longed to", "long to"):
        d = d.replace(pat, "wanted to")
    return d.replace("asked for", "wanted to get").replace("ask for", "wanted to get")


def _verb_synonyms(lemma: str) -> frozenset:
    syn = {lemma}
    for s in _wn.synsets(lemma, pos=_wn.VERB):
        for l in s.lemmas():
            syn.add(l.name().replace("_", " ").lower())
    return frozenset(syn)


def relation_channel(desire: str, outcome: str) -> Tuple[Optional[str], str]:
    """Goal-relative action-recurrence/negation. Returns (Fulfilled|Unfulfilled|None, reason)."""
    g = _gt.find_desired_state(_extend_goal(desire))
    if g is None or not g.get("verb_lemma"):
        return None, "no_goal"
    gl = g["verb_lemma"]
    syn = _verb_synonyms(gl)
    toks = _gt._tokens(outcome)
    olc = outcome.lower()
    recur_idx = None
    for i, tok in enumerate(toks):
        lem = _gt.lemma_verb(tok.lower())
        if lem == gl or lem in syn or tok.lower() in syn:
            recur_idx = i
            break
    proform = any(p in olc for p in _PROFORMS)
    recur = recur_idx is not None or proform
    neg = recur_idx is not None and _gt._verb_negated_before(toks, recur_idx)
    refusal = any(cue in olc for cue in _REFUSAL)
    if recur and not neg and not refusal:
        return "Fulfilled", "recur" + ("_proform" if (proform and recur_idx is None) else "")
    if recur and (neg or refusal):
        return "Unfulfilled", "recur_negated"
    if refusal:
        return "Unfulfilled", "refusal_no_recur"
    return None, "abstain"


def valence_channel(outcome: str) -> Optional[str]:
    """Outcome valence vote (opinion_lexicon + owned verb-polarity organ, negation-flipped)."""
    pos, neg = _opinion()
    toks = _gt._tokens(outcome)
    npos = nneg = 0
    for idx, tok in enumerate(toks):
        w = tok.lower()
        if not w.isalpha() or len(w) < 2 or w in _AUX_STOP:
            continue
        lem = _gt.lemma_verb(w)
        val = "POS" if (w in pos or lem in pos) else ("NEG" if (w in neg or lem in neg) else None)
        if val is None:
            val = _wpp.dictionary_lookup(lem).polarity
        if val and _gt._verb_negated_before(toks, idx):
            val = "NEG" if val == "POS" else "POS"
        if val == "POS":
            npos += 1
        elif val == "NEG":
            nneg += 1
    if npos == nneg:
        return None
    return "Fulfilled" if npos > nneg else "Unfulfilled"


# ============================================================================ GOAL-CUED VALENCE
# CHANNEL (top-down / biased-competition reframe, 2026-08-09). Per notes/research_brain_fidelity_
# goal_outcome_architecture_2026-08-09.md: valence_channel above is goal-BLIND (uniform bag-of-words
# vote over the whole outcome, independent of what the goal was) -- a bottom-up "extract
# independently, then compare" pattern the RPE / PFC guided-activation+biased-competition+predictive-
# coding / situation-model literature converges on as a fidelity divergence for the sub-population
# where affect words ARE present but not bound to what the goal-owner cares about. This channel makes
# the active GOAL bias which valence-bearing outcome tokens get weighted toward the vote -- the direct
# glass-box analog of a top-down template pre-activating/weighting matching candidates BEFORE the
# competition resolves (Desimone & Duncan 1995), rather than a uniform post-hoc scan.
#
# MECHANISM (glass-box, deterministic, no LLM, no new external dependency): (1) GOAL CUE = the goal
# verb's lemma + WordNet-neighbor synonyms (_verb_synonyms, the SAME organ relation_channel already
# uses) UNION the goal's referent content word (hdlab.goal_typing.find_desired_state's own "referent"
# field). (2) crude sentence-split the outcome ('.', '!', '?' -- no new parser); parse EACH clause via
# the persisted UD front-end (hdlab.candidate_generator.CandidateGenerator: UPOS tagger + hashed arc
# parser, UAS ~0.79 -- already-owned, already-persisted, reused unmodified; heuristic/over-generating
# per that module's own docstring, fine for a relevance PROXY, not required to be precise). (3) for
# each candidate valence-bearing token (same opinion_lexicon/wordnet_polarity_propagation detection
# valence_channel already uses), weight it by RELEVANCE to the goal cue:
#   - a goal-cue-lemma token is present in the SAME clause -> weight = 1/(1+dependency-tree-distance
#     to the NEAREST such anchor token in that clause) (closer syntactic attachment = higher weight,
#     matching the biased-competition/predictive-coding "closer to the template = more activated");
#   - the goal cue is mentioned only in a DIFFERENT clause of the outcome -> a fixed, lower
#     cross-clause weight (_FAR_CLAUSE_WEIGHT);
#   - the goal cue is not found ANYWHERE in the outcome -> weight = 1.0 (uniform fallback; this is
#     the principled null case -- with no textual anchor to bias toward, every candidate competes
#     equally, which is exactly today's valence_channel behavior; the mechanism degrades gracefully
#     rather than fabricating bias where the text gives none).
# (4) weighted-vote (not count-vote) the polarity signals; negation-flip via the same
# _verb_negated_before scan valence_channel already uses. ONE formula, stated once here, not tuned
# or swept per-item (per the pre-reg's own mandate) -- see preregs/2026-08-09_goal_cued_valence_
# channel_v1.md for the falsifiable HARD-PASS/HARD-FAIL/INVALID bands this channel is evaluated
# against (exp_goal_cued_valence_channel_v1.py), including the MANDATORY scrambled-goal-cue control
# (goal_cue_desire drawn from a different item) that falsifies whether goal-RELEVANCE specifically,
# not just any reweighting, is the active ingredient.
#
# Lazy-imports hdlab.candidate_generator (UPOS tagger + hashed arc parser, a heavier dependency than
# anything else in this module) INSIDE _cued_generator() so every existing lightweight consumer of
# this module (valence_channel / relation_channel / goal_achievement_verdict) is completely
# unaffected -- this function is a pure ADD, not wired into goal_achievement_verdict's precedence.
_CLAUSE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")
_FAR_CLAUSE_WEIGHT = 0.25

_cued_gen_cache = None


def _cued_generator():
    """Lazy-load + cache the persisted UD front-end (POS tagger + hashed arc parser)."""
    global _cued_gen_cache
    if _cued_gen_cache is None:
        from hdlab.candidate_generator import CandidateGenerator
        repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        pos_path = os.path.join(repo, "data", "frontend_assets", "pos_tagger_ud_ewt_upos.json")
        arc_path = os.path.join(repo, "data", "frontend_assets", "arc_parser_hashed_ud_ewt.npz")
        _cued_gen_cache = CandidateGenerator.load(pos_path, arc_path)
    return _cued_gen_cache


def _goal_cue_words(goal_cue_desire: str) -> frozenset:
    """Goal cue = verb lemma + WordNet synonyms UNION the referent content word. Empty frozenset if
    no goal is recognized (caller falls back to uniform weighting -- never crashes)."""
    g = _gt.find_desired_state(_extend_goal(goal_cue_desire))
    if g is None:
        return frozenset()
    words = set()
    vl = g.get("verb_lemma")
    if vl:
        words |= _verb_synonyms(vl)
    ref = g.get("referent")
    if ref:
        for w in _gt._tokens(str(ref)):
            if w not in _AUX_STOP and len(w) > 2:
                words.add(w)
    return frozenset(words)


def _split_clauses(outcome: str):
    parts = [p.strip() for p in _CLAUSE_SPLIT_RE.split(outcome.strip()) if p.strip()]
    return parts if parts else ([outcome] if outcome.strip() else [])


def _ancestors(heads, idx):
    chain = [idx]
    cur, seen = idx, {idx}
    while True:
        h = heads.get(cur)
        if h is None or h == 0 or h in seen:
            break
        chain.append(h)
        seen.add(h)
        cur = h
    return chain


def _tree_distance(heads, i, j) -> int:
    """Dependency-tree edge distance between two 1-based token indices in the same parse."""
    if i == j:
        return 0
    anc_i, anc_j = _ancestors(heads, i), _ancestors(heads, j)
    pos_j = {a: k for k, a in enumerate(anc_j)}
    for k, a in enumerate(anc_i):
        if a in pos_j:
            return k + pos_j[a]
    return len(anc_i) + len(anc_j)  # disconnected fallback (defensive; should not occur in a tree)


def goal_cued_valence_channel(desire: str, outcome: str,
                               goal_cue_desire: Optional[str] = None) -> Optional[str]:
    """Goal-CUED relevance-weighted valence vote (top-down/biased-competition reframe of
    valence_channel; see module-level comment above for the full mechanism). `goal_cue_desire`
    defaults to `desire` (the mechanism arm); the pre-registered SCRAMBLED-cue control passes a
    DIFFERENT item's desire text to isolate whether goal-RELEVANCE specifically, not just any
    reweighting, is the active ingredient. Never raises (mirrors valence_channel's graceful-degrade
    contract): an unrecognized goal cue or an anchor-free outcome falls back to uniform weighting."""
    cue_words = _goal_cue_words(goal_cue_desire if goal_cue_desire is not None else desire)
    pos, neg = _opinion()
    gen = _cued_generator()
    clauses = _split_clauses(outcome)
    parsed = []
    any_anchor_anywhere = False
    for c in clauses:
        r = gen.generate(c)
        toks = r.tokens
        anchors = [i for i, t in enumerate(toks, start=1)
                   if t.lower() in cue_words or _gt.lemma_verb(t.lower()) in cue_words]
        if anchors:
            any_anchor_anywhere = True
        parsed.append((toks, r.heads, anchors))
    wpos = wneg = 0.0
    for toks, heads, anchors in parsed:
        for idx0, tok in enumerate(toks):
            w = tok.lower()
            if not w.isalpha() or len(w) < 2 or w in _AUX_STOP:
                continue
            lem = _gt.lemma_verb(w)
            val = "POS" if (w in pos or lem in pos) else ("NEG" if (w in neg or lem in neg) else None)
            if val is None:
                val = _wpp.dictionary_lookup(lem).polarity
            if val is None:
                continue
            if _gt._verb_negated_before(toks, idx0):
                val = "NEG" if val == "POS" else "POS"
            idx1 = idx0 + 1
            if anchors:
                dist = min(_tree_distance(heads, idx1, a) for a in anchors)
                weight = 1.0 / (1.0 + dist)
            elif any_anchor_anywhere:
                weight = _FAR_CLAUSE_WEIGHT
            else:
                weight = 1.0
            if val == "POS":
                wpos += weight
            else:
                wneg += weight
    if wpos == wneg:
        return None
    return "Fulfilled" if wpos > wneg else "Unfulfilled"


def contrast_present(outcome: str) -> bool:
    """Channel C: a closed-class contrast/concession connective is present (denial-of-expectation)."""
    o = " " + outcome.lower() + " "
    return any(c in o for c in _CONNECTIVES)


def goal_achievement_verdict(desire: str, outcome: str) -> dict:
    """3-channel verdict. Returns {verdict, channel, reason, trace}. Glass-box, deterministic."""
    rel, reason = relation_channel(desire, outcome)
    val = valence_channel(outcome)
    if rel is not None:
        base, channel = rel, "relation:" + reason
    elif val is not None:
        base, channel = val, "valence"
    else:
        base, channel = MAJORITY_CLASS, "majority"
    verdict = base
    override = False
    if base == "Fulfilled" and contrast_present(outcome):
        verdict, override = "Unfulfilled", True
    return {"verdict": verdict, "channel": ("contrast_override" if override else channel),
            "reason": reason, "trace": {"relation": rel, "relation_reason": reason,
                                        "valence": val, "contrast": contrast_present(outcome),
                                        "base": base, "override": override}}


def self_test() -> dict:
    """Mechanism-fires check: each channel decides correctly on a clear representative case."""
    cases = [
        # irregular past 'met' is NOT lemmatized to 'meet' (known lemmatizer gap) -> relation abstains
        # -> majority; verdict still correct. Documents the gap honestly rather than asserting a fire.
        ("I wanted to meet my friend.", "I met up with my friend.", "Fulfilled", "majority"),
        ("I wanted to save him.", "But I couldn't.", "Unfulfilled", None),
        ("I wanted a good day.", "It was wonderful and I felt so happy.", "Fulfilled", "valence"),
        ("I wanted a good day.", "It was a terrible, miserable disaster.", "Unfulfilled", "valence"),
        ("I wanted to relax at home.", "But people showed up and started drinking.", "Unfulfilled", "contrast_override"),
        ("I wanted to get the kids to the museum.", "On Tuesday we did just that.", "Fulfilled", "relation"),
    ]
    out = []
    for desire, outcome, exp, chan in cases:
        r = goal_achievement_verdict(desire, outcome)
        assert r["verdict"] == exp, f"verdict {r['verdict']!r} != {exp!r} for {outcome!r} ({r})"
        if chan is not None:
            assert r["channel"].startswith(chan) or r["channel"] == chan, \
                f"channel {r['channel']!r} != {chan!r} for {outcome!r}"
        # determinism
        assert goal_achievement_verdict(desire, outcome) == r, f"non-deterministic on {outcome!r}"
        out.append((outcome, r["verdict"], r["channel"]))
    return {"cases": out, "n": len(cases)}


def self_test_goal_cued() -> dict:
    """MECHANISM-FIRES check for goal_cued_valence_channel: (1) on a mixed-polarity outcome where
    one clause is goal-relevant and the other is a distractor, the goal-cued channel must pick the
    goal-relevant clause's polarity while the uniform valence_channel (no goal-bias) is dragged the
    other way by the distractor's larger token count. (2) a SCRAMBLED goal cue (wrong item's desire)
    on the SAME item must NOT reproduce the correct pick (falsifies "any reweighting helps" in
    isolation, mirroring the pre-registered scrambled-cue control). (3) no-anchor-in-outcome falls
    back to uniform-weighting parity with valence_channel (graceful degrade, not a crash)."""
    # (1) mixed-polarity, goal-relevant clause is SHORT (1 positive word), distractor clause is
    # LONG (3 negative words) -- uniform valence_channel must be dragged NEGATIVE by raw count;
    # goal-cued must follow the goal-relevant (positive) clause instead.
    desire = "I wanted to fix the old fence in the yard."
    outcome = ("The fence was repaired nicely. "
               "Meanwhile the weather was miserable, gloomy, and depressing all week.")
    uniform = valence_channel(outcome)
    cued = goal_cued_valence_channel(desire, outcome)
    assert uniform == "Unfulfilled", f"fixture assumption broken: uniform valence={uniform!r} (expected Unfulfilled, distractor-dragged)"
    assert cued == "Fulfilled", f"MECHANISM-FIRES FAILURE: goal_cued={cued!r} (expected Fulfilled, goal-relevant clause)"

    # (2) SCRAMBLED goal cue: reuse a wrong item's desire (unrelated to "fence") as the cue source
    # on the SAME (desire, outcome) pair. A goal cue built from "weather"/"miserable" content should
    # NOT anchor to the fence-repair clause, so the scrambled arm should NOT reproduce the correct
    # Fulfilled pick via genuine goal-relevance (it may coincidentally land elsewhere, but must not
    # be the SAME goal-directed selection mechanism firing correctly).
    scramble_desire = "I wanted the weather to be nice for the picnic."
    scrambled = goal_cued_valence_channel(desire, outcome, goal_cue_desire=scramble_desire)
    assert scrambled != "Fulfilled" or scrambled == uniform, (
        f"SCRAMBLE-CONTROL FAILURE: scrambled-cue verdict={scrambled!r} reproduced the correct "
        f"goal-relevant pick ({cued!r}) that only the TRUE cue should reach -- scrambled-cue control "
        f"must not silently pass through to the real goal's answer")

    # (3) no anchor anywhere in the outcome (goal referent/verb never recurs) -> graceful fallback to
    # uniform weighting, degenerating exactly to valence_channel's own verdict.
    desire2 = "I wanted to become a doctor."
    outcome2 = "It was a wonderful, happy day and everyone felt great."
    assert goal_cued_valence_channel(desire2, outcome2) == valence_channel(outcome2), (
        "GRACEFUL-DEGRADE FAILURE: no-anchor outcome must fall back to valence_channel's own verdict")

    # determinism
    assert goal_cued_valence_channel(desire, outcome) == cued, "non-deterministic goal_cued_valence_channel"

    return {"uniform_dragged": uniform, "cued_corrected": cued, "scrambled": scrambled,
            "fallback_matches_uniform": True}


if __name__ == "__main__":
    import json
    print(json.dumps({"self_test": self_test(), "self_test_goal_cued": self_test_goal_cued()},
                      indent=2, default=str))
