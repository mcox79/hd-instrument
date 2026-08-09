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


# ============================================================================ UTILITY-SATISFACTION
# CHANNEL (2026-08-09). Per notes/research_glassbox_utility_inverse_planning_leg_2026-08-09.md
# (Naive Utility Calculus / Baker-Saxe-Tenenbaum U=R-C reframed as a stated-goal SATISFACTION check,
# not behavior-inference -- see that drill's Section 3 "the reframe"). Represents the stated goal as
# a small WEIGHTED BUNDLE of grounded ATTRIBUTE-PREDICATES (`bundle_i(w_i * bind(ATTR_ROLE_i,
# FILLER[state_i]))`, hdlab.binding.bind/hdlab.bundling.bundle, unmodified) and scores the outcome
# against each ACTIVE attribute independently, then reads the composite verdict back out via an
# unbind + argmax-with-margin cleanup (the hdlab.glass_box_loop.cleanup_with_margin DISCIPLINE --
# argmax + top1-top2 margin as the audit "why-signal" -- reimplemented here for FHRR complex64
# vectors specifically, since glass_box_loop's own cleanup_with_margin is written for the numpy
# bipolar-BSC convention; hdlab/binding.py dispatches FHRR for complex64, so this stays torch/complex64
# per CLAUDE.md's dtype convention rather than mixing BSC numpy in).
#
# CRITICAL LESSON FROM STAGE-1 (goal_cued_valence_channel, HARD_FAIL commit 215ae7a38): that
# channel's goal-cue anchor was `_verb_synonyms(goal_verb)` searched for LITERALLY IN THE OUTCOME
# TEXT -- on the cohort defined by relation_channel finding NO such recurrence, the anchor was
# therefore tautologically absent, so the channel degenerated to uniform weighting (delta=0.0
# structurally). This channel avoids that confound BY CONSTRUCTION: activation compares the GOAL's
# verb/referent only against a FIXED, goal-independent attribute-exemplar vocabulary (never touches
# the outcome text), and evidence-scoring compares OUTCOME tokens only against a FIXED,
# goal-independent attribute cue vocabulary (never touches the goal's specific words). The bridge
# between goal and outcome runs ONLY through the shared attribute-category label, never through
# direct goal-word-vs-outcome-word comparison, so it is structurally unable to inherit Stage-1's
# tautological-absence failure -- it can fire freely on the relation_channel-abstain population.
#
# GROUNDING (per the CRITICAL LESSON's mandate: grounded-semantic relevance, NOT lexical
# recurrence): PRIMARY-SENSE (k=1, WordNet's own frequency-ordered synset[0]) WordNet synonym-set
# overlap, POS-aware (VERB/ADJ/NOUN). Calibration probe (this session, scratchpad, not committed):
# raw path/wup taxonomic similarity with best-of-all-synset-pairs was measured UNRELIABLE for this
# task -- e.g. ("know","meaning") vs the ACQUIRE_POSSESS pool scored 0.94 wup-similarity via an
# obscure secondary sense of "get" ("get.v", "move into a desired direction of discourse"), a clear
# false positive; restricting to primary-sense-only synonym-SET overlap (no hypernym/hyponym
# expansion) eliminated that class of false positive in a 15-pair spot-check while still correctly
# linking ("purchase","get"), ("reach","arrive"), ("meet","see"), ("happy","glad") etc. -- precision-
# favoring by design (a channel that rarely-but-correctly fires is safer against the full-bench
# no-regression gate than a noisy high-recall one).
from functools import lru_cache

import torch

from hdlab.binding import bind, unbind
from hdlab.bundling import bundle

# 6 domain-generic attribute-predicates (hand-specified, tier-2 bootstrap per the research drill's
# Section 2 finding that a small hand-specified candidate set is literature-standard practice, not a
# shortcut). Each: goal_verbs/goal_nouns = GOAL-side exemplars (activation, never touches outcome);
# satisfied_cues/violated_cues = OUTCOME-side exemplars (evidence, never touches the goal's words).
#
# VOCABULARY-BREADTH ITERATION (2026-08-09, ONE pass, pre-full-dispatch): the initial cue lists
# above (kept minimal deliberately) MEASURED verdict_fires_rate=0.0 in --smoke (n=80; 3/16 cohort
# items activated an attribute, but 0/3 outcome texts contained an in-vocabulary evidence token --
# real DesireDB "Evidence" text for this residual cohort is frequently very short/garbled scraped
# prose, e.g. "Uh. No. Uh. No.", "none -hypothetical"). Per the prereg's MIDDLE_BAND remedy
# ("iterate attribute vocab/weights"), this is a single GENERIC broadening pass -- common
# near-synonyms any English outcome description would plausibly use for each attribute category,
# chosen BEFORE re-inspecting any additional specific DesireDB items (not fit to particular cohort
# outcomes) -- not a change to the mechanism (activation tiers, evidence tiers, FHRR layer, scoring
# formula all unchanged).
ATTRIBUTES: dict = {
    "ACQUIRE_POSSESS": {
        "goal_verbs": ["get", "obtain", "acquire", "receive", "gain", "earn", "win", "buy", "find",
                       "collect", "keep"],
        "goal_nouns": ["money", "prize", "gift", "reward"],
        "satisfied_cues": ["get", "receive", "obtain", "gain", "win", "earn", "acquire", "find",
                            "collect", "keep", "afford", "buy", "purchase", "land", "secure",
                            "score", "grab", "snag", "claim", "capture"],
        "violated_cues": ["lose", "miss", "lack", "spend", "waste", "deny", "refuse", "withhold"],
    },
    "LOCATION_REACHED": {
        "goal_verbs": ["go", "arrive", "reach", "return", "travel", "visit", "come", "escape"],
        "goal_nouns": ["home", "school", "town", "place"],
        "satisfied_cues": ["arrive", "reach", "return", "come", "escape", "land", "enter",
                            "approach", "show"],
        "violated_cues": ["stranded", "stuck", "trapped", "wander", "lost", "miss", "delay"],
    },
    "SOCIAL_CONNECTION": {
        "goal_verbs": ["meet", "see", "visit", "join", "help", "reunite", "befriend", "marry"],
        "goal_nouns": ["friend", "family", "mother", "father"],
        "satisfied_cues": ["meet", "greet", "welcome", "join", "help", "reunite", "hug", "embrace",
                            "thank", "invite", "accept", "call", "visit", "talk", "chat", "kiss"],
        "violated_cues": ["reject", "abandon", "betray", "leave", "refuse", "ignore", "scold",
                           "punish", "avoid", "snub", "fight", "argue"],
    },
    "AVOID_HARM_SAFETY": {
        "goal_verbs": ["save", "rescue", "protect", "survive", "escape", "heal", "recover", "avoid"],
        "goal_nouns": ["danger", "safety", "harm", "illness"],
        "satisfied_cues": ["save", "rescue", "protect", "survive", "heal", "recover", "shelter",
                            "cure", "dodge"],
        "violated_cues": ["die", "hurt", "injure", "wound", "perish", "drown", "sink", "crash",
                           "starve", "suffer", "kill", "attack", "threaten", "harm"],
    },
    "ACTIVITY_COMPLETION": {
        "goal_verbs": ["finish", "complete", "accomplish", "achieve", "succeed", "win", "build",
                       "fix", "repair", "make"],
        "goal_nouns": [],
        "satisfied_cues": ["finish", "complete", "accomplish", "achieve", "succeed", "win", "build",
                            "fix", "repair", "manage", "solve", "resolve", "handle"],
        "violated_cues": ["fail", "quit", "abandon", "lose", "stop", "struggle", "botch"],
    },
    "EMOTIONAL_STATE_ACHIEVED": {
        "goal_verbs": ["feel", "enjoy", "relax", "celebrate", "rest", "sleep"],
        "goal_nouns": ["happiness", "joy", "peace", "fun"],
        "satisfied_cues": ["enjoy", "smile", "laugh", "celebrate", "happy", "glad", "joyful",
                            "pleased", "delighted", "love", "thrilled", "excite", "content",
                            "relieve", "comfortable"],
        "violated_cues": ["cry", "sad", "miserable", "upset", "disappointed", "angry", "frustrated",
                           "worry", "hate", "depressed", "anxious", "stressed", "lonely",
                           "devastated", "heartbroken"],
    },
}

_WN_POS = (None,)  # set below once _wn is confirmed imported (module already imports _wn at top)
try:
    _WN_POS = (_wn.VERB, _wn.ADJ, _wn.NOUN)
except Exception:
    _WN_POS = ()


@lru_cache(maxsize=None)
def _primary_synonyms(word: str, pos) -> frozenset:
    """Primary-sense (k=1, WordNet's own frequency-ordered synsets()[0]) synonym set for `word` at
    a given POS, plus `word` itself. Deliberately NOT hypernym/hyponym-expanded and NOT all-senses
    (see module-comment calibration note: both were measured noisier -- pull in unrelated senses of
    common polysemous words like 'get'/'fix'/'meet')."""
    syn = {word}
    syns = _wn.synsets(word, pos=pos)
    if syns:
        for l in syns[0].lemmas():
            syn.add(l.name().replace("_", " ").lower())
    return frozenset(syn)


def _related_any_pos(word: str, cand: str) -> bool:
    """True iff `word` and `cand` are identical, or share a primary-sense synonym in ANY of
    VERB/ADJ/NOUN (cue lists mix verbs like 'enjoy' with adjectives like 'happy', so the POS of a
    cue word is not assumed in advance)."""
    if word == cand:
        return True
    for pos in _WN_POS:
        if _primary_synonyms(word, pos) & _primary_synonyms(cand, pos):
            return True
    return False


def _pool_related(word: str, pool) -> bool:
    return any(_related_any_pos(word, cand) for cand in pool)


def activate_attributes(desire: str) -> dict:
    """Which attributes does THIS goal invoke? GOAL-side only (find_desired_state's verb_lemma /
    referent vs each attribute's FIXED goal_verbs/goal_nouns exemplar pool) -- never inspects the
    outcome text, so this cannot inherit Stage-1's tautological-absence confound. Returns
    {attribute: weight}, weight=1.0 for a literal exact-lemma hit (Tier-1), 0.7 for a WordNet
    primary-sense-synonym-only hit (Tier-2, grounded but indirect). Empty dict if no goal recognized
    or no attribute clears either tier."""
    g = _gt.find_desired_state(_extend_goal(desire))
    if g is None:
        return {}
    verb = g.get("verb_lemma")
    referent = g.get("referent")
    active = {}
    for attr, spec in ATTRIBUTES.items():
        w = 0.0
        if verb:
            if verb in spec["goal_verbs"]:
                w = max(w, 1.0)
            elif _pool_related(verb, spec["goal_verbs"]):
                w = max(w, 0.7)
        if referent and spec["goal_nouns"]:
            if referent in spec["goal_nouns"]:
                w = max(w, 1.0)
            elif _pool_related(referent, spec["goal_nouns"]):
                w = max(w, 0.7)
        if w > 0:
            active[attr] = w
    return active


def _token_cue_polarity(token_form: str, attr: str) -> Optional[str]:
    """POS/NEG/None for one outcome token-form against attribute `attr`'s FIXED satisfied_cues/
    violated_cues pools -- never inspects the goal's words. Tier-1 exact membership; Tier-2 WordNet
    primary-sense-synonym overlap (same _pool_related organ activate_attributes uses). None if OOV
    of both pools, or (rare) an ambiguous hit on both -- abstain, never guess."""
    spec = ATTRIBUTES[attr]
    if token_form in spec["satisfied_cues"]:
        return "POS"
    if token_form in spec["violated_cues"]:
        return "NEG"
    pos_hit = _pool_related(token_form, spec["satisfied_cues"])
    neg_hit = _pool_related(token_form, spec["violated_cues"])
    if pos_hit and not neg_hit:
        return "POS"
    if neg_hit and not pos_hit:
        return "NEG"
    return None


def _outcome_token_forms(tok: str) -> list:
    """Candidate lemma forms for one outcome token, tried in order until one hits a cue pool:
    surface form, hdlab.thematic_role_labeler.lemma_verb (suffix-stripping heuristic, matches the
    rest of this module's convention), and WordNet's own morphy analyzer (catches cases lemma_verb's
    heuristic mangles into a non-word, e.g. "purchased" -> "purchas" via naive -ed stripping, where
    morphy correctly recovers "purchase"). Deduplicated, order-preserving."""
    forms = [tok]
    lem = _gt.lemma_verb(tok)
    if lem not in forms:
        forms.append(lem)
    for pos in (_wn.VERB, _wn.ADJ, None):
        m = _wn.morphy(tok, pos) if pos else _wn.morphy(tok)
        if m and m not in forms:
            forms.append(m)
    return forms


def _token_vote(attr: str, outcome: str, extra_lookup=None) -> Tuple[int, int]:
    """(npos, nneg) per-outcome-token grounded polarity vote against `attr`'s FIXED cue pools
    (negation-aware via the same _verb_negated_before scan valence_channel/relation_channel use).
    `extra_lookup(form, attr) -> POS|NEG|None`, if given, is tried ONLY when the WordNet-grounded
    `_token_cue_polarity` returns None (a SUPPLEMENTARY lookup, e.g. Direction-B M1's ConceptNet-
    antonym bridge -- kept as a parameter so this module carries no hard import of
    hdlab.idiom_grounding when unused). Factored out of `_attribute_outcome_state` so the M1
    idiom-grounded variant below can reuse the identical token-vote loop; behavior of
    `_attribute_outcome_state` is UNCHANGED by this factor (extra_lookup=None reproduces it
    exactly)."""
    toks = _gt._tokens(outcome)
    npos = nneg = 0
    for idx, tok in enumerate(toks):
        if not tok.isalpha() or len(tok) < 2 or tok in _AUX_STOP:
            continue
        val = None
        for form in _outcome_token_forms(tok):
            val = _token_cue_polarity(form, attr)
            if val is None and extra_lookup is not None:
                val = extra_lookup(form, attr)
            if val is not None:
                break
        if val is None:
            continue
        if _gt._verb_negated_before(toks, idx):
            val = "NEG" if val == "POS" else "POS"
        if val == "POS":
            npos += 1
        else:
            nneg += 1
    return npos, nneg


def _attribute_outcome_state(attr: str, outcome: str) -> str:
    """SATISFIED / VIOLATED / ABSENT for `attr` against `outcome`: per-token grounded polarity vote
    (negation-aware via the same _verb_negated_before scan valence_channel/relation_channel use),
    count-voted like valence_channel (not weighted) for the same tie->ABSENT convention."""
    npos, nneg = _token_vote(attr, outcome)
    if npos == nneg:
        return "ABSENT"
    return "SATISFIED" if npos > nneg else "VIOLATED"


# ============================================================================ DIRECTION-B M1:
# IDIOM/COLLOQUIALISM-GROUNDED evidence-scoring (2026-08-09). Per notes/direction_b_grounded_
# knowledge_build_plan_2026-08-09.md milestone M1: Stage-2's utility_channel ARCHITECTURE is
# validated (activation fires, pairscramble collapses, no regression) but its per-token WordNet
# evidence-scoring cannot READ short/idiomatic/colloquial real DesireDB outcome text ("put the
# kabash on that idea", "she told her no", "Uh. No."). This SUPPLEMENTS (never replaces) the same
# per-token WordNet vote with (a) hdlab.idiom_grounding.IDIOM_LEXICON phrase votes and (b) a
# ConceptNet-Antonym-bridge per-token fallback (see hdlab/idiom_grounding.py module comment for
# full source documentation + calibration-honesty note). SAME activation (`activate_attributes`,
# goal-side only, never touches outcome text) -- confound-immunity argument identical to Stage-2's.
_IDIOM_VOTE_WEIGHT = 2  # a multi-word idiom-phrase match is a more decisive/less-ambiguous signal
                        # than one single ambiguous token (e.g. 'call' phone-call vs 'call' pay-a-
                        # visit) -- a FIXED design choice declared before any scoring/eval run, not
                        # tuned per item.


def _attribute_outcome_state_idiom_grounded(attr: str, outcome: str,
                                             use_conceptnet_bridge: bool = True) -> Tuple[str, dict]:
    """Direction-B M1 variant of `_attribute_outcome_state`: same WordNet per-token vote PLUS
    idiom-phrase + (optionally) ConceptNet-antonym-bridge supplementary votes. Returns (state,
    trace) where trace separates the WordNet-only sub-total from the idiom/ConceptNet contribution
    (auditability -- the product differentiator per the arc's own repeated finding).
    `use_conceptnet_bridge=False` isolates the hand-authored-idiom-lexicon-only contribution for
    the M1 cell's ablation arm (a spot-check surfaced that the bridge's "tell"/ConceptNet-Antonym-
    of-"show" hit on a flagship case is a word-sense collision -- 'show' meaning show-up/arrive in
    LOCATION_REACHED's cue pool vs ConceptNet's communication-mode "show, don't tell" sense -- the
    ablation lets the cell report whether ConceptNet materially changes any verdict beyond what the
    hand-vetted idiom lexicon alone achieves, same discipline as the WordNet-oversense-expansion
    risk this module's own calibration note already flags). Also applies `hdlab.idiom_grounding.
    dedupe_repeated_sentences` before the per-token vote (general data-hygiene fix for DesireDB's
    own verbatim-repeated-sentence scraping artifact -- see that function's docstring; Stage-2's
    original `_attribute_outcome_state` / arm ii is UNTOUCHED by this)."""
    from hdlab import idiom_grounding as _ig
    outcome_dedup = _ig.dedupe_repeated_sentences(outcome)
    extra = (lambda f, a: _ig.conceptnet_bridge_vote(f, a, ATTRIBUTES[a])) if use_conceptnet_bridge else None
    npos, nneg = _token_vote(attr, outcome_dedup, extra_lookup=extra)
    idiom = _ig.idiom_votes(outcome_dedup)
    idiom_pos_w = _IDIOM_VOTE_WEIGHT * idiom["POS"]
    idiom_neg_w = _IDIOM_VOTE_WEIGHT * idiom["NEG"]
    trace = {"token_npos": npos, "token_nneg": nneg,
              "idiom_pos_votes": idiom["POS"], "idiom_neg_votes": idiom["NEG"],
              "idiom_pos_weighted": idiom_pos_w, "idiom_neg_weighted": idiom_neg_w,
              "idiom_matches": idiom["matched"]}
    npos += idiom_pos_w
    nneg += idiom_neg_w
    if npos == nneg:
        return "ABSENT", trace
    return ("SATISFIED" if npos > nneg else "VIOLATED"), trace


# ---- FHRR weighted-bundle-of-role-bound-attribute-predicates representation ------------------
_UTIL_N_DIM = 2048
_UTIL_SEED = 20260809
_UTIL_STATES = ("SATISFIED", "VIOLATED", "ABSENT")
_UTIL_SIGN = {"SATISFIED": 1.0, "VIOLATED": -1.0, "ABSENT": 0.0}
_util_vecs_cache = None


def _unit_phase(gen: torch.Generator) -> torch.Tensor:
    theta = torch.rand(_UTIL_N_DIM, generator=gen) * (2.0 * 3.14159265358979)
    return torch.polar(torch.ones(_UTIL_N_DIM), theta).to(torch.complex64)


def _utility_vecs():
    """Deterministic (fixed-seed) FHRR role atoms (one per attribute) + filler atoms (SATISFIED/
    VIOLATED/ABSENT), cached module-wide. Same random-unit-phase-vector convention as
    hdlab.situation_model_accumulate.unit_phase_vec."""
    global _util_vecs_cache
    if _util_vecs_cache is None:
        gen = torch.Generator().manual_seed(_UTIL_SEED)
        roles = {a: _unit_phase(gen) for a in ATTRIBUTES}
        fillers = {s: _unit_phase(gen) for s in _UTIL_STATES}
        _util_vecs_cache = (roles, fillers)
    return _util_vecs_cache


def _fhrr_cos(a: torch.Tensor, b: torch.Tensor) -> float:
    """FHRR cosine, same convention as hdlab.lexical_similarity._cos_complex."""
    return float(torch.real(torch.sum(torch.conj(a) * b))) / a.shape[0]


def _cleanup_margin_fhrr(probe: torch.Tensor, codebook: dict) -> Tuple[str, float]:
    """FHRR analog of hdlab.glass_box_loop.cleanup_with_margin (argmax + top1-top2 margin
    "why-signal"), for complex64 vectors -- glass_box_loop's own implementation is numpy
    bipolar-BSC-specific (a different substrate flavor), so this is a minimal same-discipline
    reimplementation, not a call-through."""
    scores = {name: _fhrr_cos(probe, vec) for name, vec in codebook.items()}
    ranked = sorted(scores.items(), key=lambda kv: -kv[1])
    top_name, top_score = ranked[0]
    _, second_score = ranked[1]
    return top_name, top_score - second_score


def utility_channel_trace(desire: str, outcome: str) -> dict:
    """Full glass-box trace of the utility-satisfaction channel. `verdict` is Fulfilled/Unfulfilled/
    None (abstain: no attribute activated, or the weighted sum of recovered per-attribute states is
    exactly zero -- mixed/no evidence, same tie->abstain convention as valence_channel)."""
    active = activate_attributes(desire)
    if not active:
        return {"verdict": None, "reason": "no_attribute_activated", "active": {}}
    roles, fillers = _utility_vecs()
    per_attr = {}
    weighted_terms = []
    for attr, w in active.items():
        state = _attribute_outcome_state(attr, outcome)
        weighted_terms.append(w * bind(roles[attr], fillers[state]))
        per_attr[attr] = {"activation_weight": round(w, 2), "outcome_state": state}
    U = bundle(torch.stack(weighted_terms))
    score = 0.0
    for attr, w in active.items():
        probe = unbind(U, roles[attr])
        recovered_name, margin = _cleanup_margin_fhrr(probe, fillers)
        per_attr[attr]["recovered_state"] = recovered_name
        per_attr[attr]["recovered_margin"] = round(margin, 4)
        per_attr[attr]["roundtrip_ok"] = (recovered_name == per_attr[attr]["outcome_state"])
        score += w * _UTIL_SIGN[recovered_name]
    if score == 0.0:
        return {"verdict": None, "reason": "margin_refuse_zero_sum", "score": 0.0, "active": per_attr}
    verdict = "Fulfilled" if score > 0.0 else "Unfulfilled"
    return {"verdict": verdict, "reason": "weighted_bundle", "score": round(score, 4), "active": per_attr}


def utility_channel(desire: str, outcome: str) -> Optional[str]:
    """Fulfilled/Unfulfilled/None -- the utility-satisfaction 4th channel (see module comment above
    for the full mechanism + the Stage-1 confound this is built to avoid). NOT wired into
    goal_achievement_verdict's precedence -- pure ADD, evaluated standalone by
    experiments/exp_utility_satisfaction_channel_v1.py."""
    return utility_channel_trace(desire, outcome)["verdict"]


def utility_channel_trace_idiom_grounded(desire: str, outcome: str,
                                          use_conceptnet_bridge: bool = True) -> dict:
    """Direction-B M1 (2026-08-09) idiom/colloquialism-grounded variant of `utility_channel_trace`.
    SAME activation (`activate_attributes`, unchanged) and SAME FHRR bind/bundle/unbind scoring
    layer as the Stage-2 channel; only the per-attribute outcome-evidence function differs
    (`_attribute_outcome_state_idiom_grounded` instead of `_attribute_outcome_state`).
    `use_conceptnet_bridge=False` = idiom-lexicon-only ablation arm (see that function's docstring).
    NOT wired into goal_achievement_verdict's precedence -- pure ADD, evaluated standalone by
    experiments/exp_direction_b_M1_idiom_grounding_recovery_v1.py."""
    active = activate_attributes(desire)
    if not active:
        return {"verdict": None, "reason": "no_attribute_activated", "active": {}}
    roles, fillers = _utility_vecs()
    per_attr = {}
    weighted_terms = []
    for attr, w in active.items():
        state, trace = _attribute_outcome_state_idiom_grounded(attr, outcome, use_conceptnet_bridge)
        weighted_terms.append(w * bind(roles[attr], fillers[state]))
        per_attr[attr] = {"activation_weight": round(w, 2), "outcome_state": state,
                           "grounding_trace": trace}
    U = bundle(torch.stack(weighted_terms))
    score = 0.0
    for attr, w in active.items():
        probe = unbind(U, roles[attr])
        recovered_name, margin = _cleanup_margin_fhrr(probe, fillers)
        per_attr[attr]["recovered_state"] = recovered_name
        per_attr[attr]["recovered_margin"] = round(margin, 4)
        per_attr[attr]["roundtrip_ok"] = (recovered_name == per_attr[attr]["outcome_state"])
        score += w * _UTIL_SIGN[recovered_name]
    if score == 0.0:
        return {"verdict": None, "reason": "margin_refuse_zero_sum", "score": 0.0, "active": per_attr}
    verdict = "Fulfilled" if score > 0.0 else "Unfulfilled"
    return {"verdict": verdict, "reason": "weighted_bundle", "score": round(score, 4), "active": per_attr}


def utility_channel_idiom_grounded(desire: str, outcome: str,
                                    use_conceptnet_bridge: bool = True) -> Optional[str]:
    """Fulfilled/Unfulfilled/None -- Direction-B M1's idiom-grounded 4th-channel variant. See
    `utility_channel_trace_idiom_grounded` for the mechanism."""
    return utility_channel_trace_idiom_grounded(desire, outcome, use_conceptnet_bridge)["verdict"]


def self_test_utility_channel() -> dict:
    """MECHANISM-FIRES + FHRR-round-trip-fidelity + STAGE-1-CONFOUND-IMMUNITY checks."""
    # (1) clear Fulfilled case, single attribute.
    r1 = utility_channel_trace("I wanted to buy a new bike.", "She purchased the bicycle yesterday.")
    assert r1["verdict"] == "Fulfilled", f"case1 verdict={r1['verdict']!r} (expected Fulfilled): {r1}"

    # (2) clear Unfulfilled case.
    r2 = utility_channel_trace("I wanted to save the puppy.", "The puppy drowned before help arrived.")
    assert r2["verdict"] == "Unfulfilled", f"case2 verdict={r2['verdict']!r} (expected Unfulfilled): {r2}"

    # (3) FHRR round-trip fidelity: every active attribute's recovered_state must match what was
    # bound in (bundle capacity check at up to 6 items, N_DIM=2048 -- should hold with large margin).
    for r in (r1, r2):
        for attr, info in r["active"].items():
            assert info["roundtrip_ok"], f"FHRR ROUND-TRIP FAILURE on {attr!r}: {info}"
            assert info["recovered_margin"] > 0.05, f"low-margin roundtrip on {attr!r}: {info}"

    # (4) STAGE-1-CONFOUND-IMMUNITY: fire correctly on a case where the goal's verb/synonyms are
    # ABSENT from the outcome text (relation_channel abstains) AND valence_channel also abstains
    # (no net opinion_lexicon/wpp polarity) -- exactly the abstain-to-majority cohort definition.
    # If this channel inherited Stage-1's confound it would be UNABLE to fire here by construction.
    desire3 = "I wanted to reach the summit."
    outcome3 = "She arrived at the top of the mountain by dawn."  # no literal 'reach'/'summit'
                                                                   # recurrence; 'arrived' is a FIXED
                                                                   # LOCATION_REACHED cue, reached via
                                                                   # the attribute bridge, not via
                                                                   # goal-word recurrence in the outcome
    rel3, _ = relation_channel(desire3, outcome3)
    val3 = valence_channel(outcome3)
    assert rel3 is None, f"fixture assumption broken: relation_channel fired ({rel3!r}) on case3"
    r3 = utility_channel_trace(desire3, outcome3)
    assert r3["verdict"] is not None, (
        f"STAGE-1-CONFOUND-IMMUNITY FAILURE: utility_channel abstained on a relation_channel-abstain "
        f"case exactly like Stage-1's structurally-tautological-absence failure mode: {r3}")

    # (5) no-goal-recognized -> abstain gracefully (never crashes).
    r5 = utility_channel_trace("The weather was nice.", "It rained all day.")
    assert r5["verdict"] is None and r5["reason"] == "no_attribute_activated", r5

    # (6) determinism.
    assert utility_channel_trace("I wanted to buy a new bike.",
                                  "She purchased the bicycle yesterday.")["score"] == r1["score"]

    return {"case1": r1, "case2": r2, "case3_stage1_immunity": r3,
            "relation_channel_abstained_case3": rel3 is None, "valence_channel_case3": val3,
            "case5_no_goal": r5}


def self_test_idiom_grounded_channel() -> dict:
    """MECHANISM-FIRES check for Direction-B M1: on the two flagship real-DesireDB cohort cases
    the plain WordNet-only `utility_channel` ABSTAINS or MIS-fires on (verified below), the
    idiom-grounded variant must reach the semantically-correct verdict. Also verifies the
    pairscramble control (a scrambled goal cue must not reproduce the correct idiom-grounded pick
    through genuine goal-conditioning) and FHRR round-trip fidelity, mirroring self_test_utility_
    channel's own discipline."""
    from hdlab import idiom_grounding as _ig  # noqa: F401 (import-path smoke; real object exercised below)

    # (1) "Uh. No." case (real DesireDB cohort item): plain WordNet-only channel ABSTAINS
    # (margin_refuse_zero_sum, no outcome-side cue token); idiom-grounded must reach Unfulfilled.
    desire1 = "My girl [wanted to] act it out in real life, even wanting to move to England! Uh. No."
    outcome1 = "Uh. No. Uh. No."
    plain1 = utility_channel_trace(desire1, outcome1)
    grounded1 = utility_channel_trace_idiom_grounded(desire1, outcome1)
    assert plain1["verdict"] is None, f"fixture assumption broken: plain channel did not abstain: {plain1}"
    assert grounded1["verdict"] == "Unfulfilled", (
        f"MECHANISM-FIRES FAILURE: idiom-grounded channel did not recover 'Uh. No.' case: {grounded1}")

    # (2) "she told her no" case (real DesireDB cohort item): plain WordNet-only channel MIS-fires
    # Fulfilled (a spurious literal-token hit: 'calls' matches SOCIAL_CONNECTION's satisfied_cues
    # phone-call/pay-a-visit sense); idiom-grounded must flip to the semantically-correct Unfulfilled
    # once the decisive 'told her no' idiom outweighs the single ambiguous token.
    desire2 = "She [wanted to] see us."
    # verbatim as it appears in real DesireDB (3x-repeated scraping artifact -- this exact
    # duplication is what motivated `hdlab.idiom_grounding.dedupe_repeated_sentences`: without it
    # the per-token 'calls' hit (a SOCIAL_CONNECTION satisfied_cue, phone-call sense) is counted
    # 3x by the raw WordNet token vote and outvotes the (correctly deduplicated) idiom hit).
    outcome2 = ("So Jarrad calls and bec tells him she asked Robyn and she told her no. "
                "So Jarrad calls and bec tells him she asked Robyn and she told her no "
                "So Jarrad calls and bec tells him she asked Robyn and she told her no ")
    plain2 = utility_channel_trace(desire2, outcome2)
    grounded2 = utility_channel_trace_idiom_grounded(desire2, outcome2)
    assert plain2["verdict"] == "Fulfilled", f"fixture assumption broken: plain channel = {plain2}"
    assert grounded2["verdict"] == "Unfulfilled", (
        f"MECHANISM-FIRES FAILURE: idiom-grounded channel did not flip 'told her no' case: {grounded2}")

    # (3) FHRR round-trip fidelity on both grounded cases.
    for r in (grounded1, grounded2):
        for attr, info in r["active"].items():
            assert info["roundtrip_ok"], f"FHRR ROUND-TRIP FAILURE on {attr!r}: {info}"

    # (4) pairscramble control: a WRONG goal cue (unrelated desire) on outcome2 must not reproduce
    # the correct Unfulfilled pick via genuine goal-conditioning (activation itself changes with a
    # scrambled desire, so this checks the mechanism is not just reading outcome-idiom polarity
    # blind to the goal -- mirrors self_test_goal_cued's own scramble-control discipline).
    scramble_desire = "I wanted to buy a new bike."
    scrambled = utility_channel_idiom_grounded(scramble_desire, outcome2)
    assert scrambled != "Unfulfilled" or activate_attributes(scramble_desire) != activate_attributes(desire2), (
        f"SCRAMBLE-CONTROL AMBIGUOUS: scrambled-cue verdict={scrambled!r} reproduced the grounded "
        f"pick with an IDENTICAL activation set to the real goal -- would indicate the mechanism "
        f"ignores the goal cue entirely")

    # (5) determinism.
    assert utility_channel_trace_idiom_grounded(desire2, outcome2)["score"] == grounded2["score"]

    return {"case1_uh_no": grounded1, "case2_told_her_no": grounded2,
            "plain_channel_case1_abstained": plain1["verdict"] is None,
            "plain_channel_case2_misfired_fulfilled": plain2["verdict"] == "Fulfilled",
            "scrambled_case2": scrambled}


# ============================================================================ DIRECTION-B M2:
# LEARNED speech-act/RESULT-TYPE-grounded evidence-scoring (2026-08-09). Per notes/direction_b_
# grounded_knowledge_build_plan_2026-08-09.md milestone M2: M1's idiom lexicon supplements the
# WordNet token vote with a 29-entry HAND-AUTHORED phrase lexicon (recovery 0.25 primary-cohort,
# 0/37 enlarged-cohort breadth -- idioms are a non-compositional long-tail). M2 tests a DIFFERENT,
# complementary hypothesis: a LEARNED classifier (hdlab.result_type_induction, construction-cue
# features, hdlab.learner.registry.learn, held-out-surface-form generalization measured by
# experiments/exp_direction_b_M2_speechact_result_generalization_v1.py's GATE-1) over the COMMON
# COMPOSITIONAL CORE of refusal/grant/block/achieve/fail expressions. SAME activation
# (`activate_attributes`, goal-side only, never touches outcome text) -- confound-immunity argument
# identical to Stage-2/M1. `chosen_name`/`hypothesis` are the induced hypothesis from
# hdlab.result_type_induction.get_induced_hypothesis() (trained ONLY on TRAIN_EXAMPLES, never on
# DesireDB -- the caller passes it explicitly, rather than this module importing the getter itself,
# so it is visually obvious at every call site that DesireDB gold never touches the fit).
_RESULTTYPE_VOTE_WEIGHT = 2  # a whole-span result-type classification is a more decisive/less-
                             # ambiguous signal than one single ambiguous WordNet token vote --
                             # the SAME fixed, pre-declared design choice as M1's _IDIOM_VOTE_WEIGHT.


def _attribute_outcome_state_resulttype_grounded(attr: str, outcome: str, chosen_name, hypothesis
                                                   ) -> Tuple[str, dict]:
    """Direction-B M2 variant of `_attribute_outcome_state`: the same per-token WordNet vote PLUS a
    supplementary result-type vote from `hdlab.result_type_induction.result_type_votes` (weighted).
    Returns (state, trace) -- trace separates the WordNet-only sub-total from the result-type
    contribution (auditability, same discipline as M1's idiom-grounded trace). Applies
    `hdlab.idiom_grounding.dedupe_repeated_sentences` first (same general data-hygiene fix M1
    applied -- DesireDB's own verbatim-repeated-sentence scraping artifact otherwise inflates the
    per-token WordNet vote 2-3x; reused verbatim, not idiom-lexicon-specific per that function's own
    docstring)."""
    from hdlab import idiom_grounding as _ig
    from hdlab import result_type_induction as _rti
    outcome_dedup = _ig.dedupe_repeated_sentences(outcome)
    npos, nneg = _token_vote(attr, outcome_dedup)
    rt = _rti.result_type_votes(outcome_dedup, chosen_name, hypothesis)
    rt_pos_w = _RESULTTYPE_VOTE_WEIGHT * rt["POS"]
    rt_neg_w = _RESULTTYPE_VOTE_WEIGHT * rt["NEG"]
    trace = {"token_npos": npos, "token_nneg": nneg,
             "resulttype_pos_votes": rt["POS"], "resulttype_neg_votes": rt["NEG"],
             "resulttype_pos_weighted": rt_pos_w, "resulttype_neg_weighted": rt_neg_w,
             "resulttype_matched": rt["matched"]}
    npos += rt_pos_w
    nneg += rt_neg_w
    if npos == nneg:
        return "ABSENT", trace
    return ("SATISFIED" if npos > nneg else "VIOLATED"), trace


def utility_channel_trace_resulttype_grounded(desire: str, outcome: str, chosen_name, hypothesis
                                               ) -> dict:
    """Direction-B M2 (2026-08-09) result-type-grounded variant of `utility_channel_trace`. SAME
    activation and SAME FHRR bind/bundle/unbind scoring layer as Stage-2/M1; only the per-attribute
    outcome-evidence function differs (`_attribute_outcome_state_resulttype_grounded`). NOT wired
    into goal_achievement_verdict's precedence -- pure ADD, evaluated standalone by
    experiments/exp_direction_b_M2_speechact_result_generalization_v1.py."""
    active = activate_attributes(desire)
    if not active:
        return {"verdict": None, "reason": "no_attribute_activated", "active": {}}
    roles, fillers = _utility_vecs()
    per_attr = {}
    weighted_terms = []
    for attr, w in active.items():
        state, trace = _attribute_outcome_state_resulttype_grounded(attr, outcome, chosen_name, hypothesis)
        weighted_terms.append(w * bind(roles[attr], fillers[state]))
        per_attr[attr] = {"activation_weight": round(w, 2), "outcome_state": state,
                           "grounding_trace": trace}
    U = bundle(torch.stack(weighted_terms))
    score = 0.0
    for attr, w in active.items():
        probe = unbind(U, roles[attr])
        recovered_name, margin = _cleanup_margin_fhrr(probe, fillers)
        per_attr[attr]["recovered_state"] = recovered_name
        per_attr[attr]["recovered_margin"] = round(margin, 4)
        per_attr[attr]["roundtrip_ok"] = (recovered_name == per_attr[attr]["outcome_state"])
        score += w * _UTIL_SIGN[recovered_name]
    if score == 0.0:
        return {"verdict": None, "reason": "margin_refuse_zero_sum", "score": 0.0, "active": per_attr}
    verdict = "Fulfilled" if score > 0.0 else "Unfulfilled"
    return {"verdict": verdict, "reason": "weighted_bundle", "score": round(score, 4), "active": per_attr}


def utility_channel_resulttype_grounded(desire: str, outcome: str, chosen_name, hypothesis
                                         ) -> Optional[str]:
    """Fulfilled/Unfulfilled/None -- Direction-B M2's result-type-grounded 4th-channel variant. See
    `utility_channel_trace_resulttype_grounded` for the mechanism."""
    return utility_channel_trace_resulttype_grounded(desire, outcome, chosen_name, hypothesis)["verdict"]


def self_test_resulttype_grounded_channel() -> dict:
    """MECHANISM-FIRES check for Direction-B M2, mirroring self_test_idiom_grounded_channel's
    discipline exactly (same two real-DesireDB-cohort flagship cases, same pairscramble control)."""
    from hdlab import result_type_induction as _rti
    chosen_name, hypothesis = _rti.get_induced_hypothesis()
    assert hypothesis is not None, "M2 induction abstained on its own TRAIN set -- cannot self-test"

    # (1) "Uh. No." case: plain WordNet-only channel ABSTAINS; result-type-grounded must recover
    # Unfulfilled via the bare-discourse-negation construction rule.
    desire1 = "My girl [wanted to] act it out in real life, even wanting to move to England! Uh. No."
    outcome1 = "Uh. No. Uh. No."
    plain1 = utility_channel_trace(desire1, outcome1)
    grounded1 = utility_channel_trace_resulttype_grounded(desire1, outcome1, chosen_name, hypothesis)
    assert plain1["verdict"] is None, f"fixture assumption broken: plain channel did not abstain: {plain1}"
    assert grounded1["verdict"] == "Unfulfilled", (
        f"MECHANISM-FIRES FAILURE: resulttype-grounded channel did not recover 'Uh. No.' case: {grounded1}")

    # (2) "she told her no" case: plain WordNet-only channel MIS-fires Fulfilled (spurious 'calls'
    # token hit); resulttype-grounded must flip to Unfulfilled via the comm_verb('told')+neg_present
    # REFUSAL rule (a HELD-OUT surface form -- 'told' is never in COMM_POOL/TRAIN_EXAMPLES).
    desire2 = "She [wanted to] see us."
    outcome2 = ("So Jarrad calls and bec tells him she asked Robyn and she told her no. "
                "So Jarrad calls and bec tells him she asked Robyn and she told her no "
                "So Jarrad calls and bec tells him she asked Robyn and she told her no ")
    plain2 = utility_channel_trace(desire2, outcome2)
    grounded2 = utility_channel_trace_resulttype_grounded(desire2, outcome2, chosen_name, hypothesis)
    assert plain2["verdict"] == "Fulfilled", f"fixture assumption broken: plain channel = {plain2}"
    assert grounded2["verdict"] == "Unfulfilled", (
        f"MECHANISM-FIRES FAILURE: resulttype-grounded channel did not flip 'told her no' case: {grounded2}")

    # (3) FHRR round-trip fidelity on both grounded cases.
    for r in (grounded1, grounded2):
        for attr, info in r["active"].items():
            assert info["roundtrip_ok"], f"FHRR ROUND-TRIP FAILURE on {attr!r}: {info}"

    # (4) pairscramble control: a WRONG goal cue must not reproduce the correct Unfulfilled pick.
    scramble_desire = "I wanted to buy a new bike."
    scrambled = utility_channel_resulttype_grounded(scramble_desire, outcome2, chosen_name, hypothesis)
    assert scrambled != "Unfulfilled" or activate_attributes(scramble_desire) != activate_attributes(desire2), (
        f"SCRAMBLE-CONTROL AMBIGUOUS: scrambled-cue verdict={scrambled!r} reproduced the grounded "
        f"pick with an IDENTICAL activation set to the real goal")

    # (5) determinism.
    assert utility_channel_trace_resulttype_grounded(
        desire2, outcome2, chosen_name, hypothesis)["score"] == grounded2["score"]

    return {"case1_uh_no": grounded1, "case2_told_her_no": grounded2,
            "plain_channel_case1_abstained": plain1["verdict"] is None,
            "plain_channel_case2_misfired_fulfilled": plain2["verdict"] == "Fulfilled",
            "scrambled_case2": scrambled, "chosen_plugin": chosen_name}


if __name__ == "__main__":
    import json
    print(json.dumps({"self_test": self_test(), "self_test_goal_cued": self_test_goal_cued(),
                       "self_test_utility_channel": self_test_utility_channel(),
                       "self_test_idiom_grounded_channel": self_test_idiom_grounded_channel()},
                      indent=2, default=str))
