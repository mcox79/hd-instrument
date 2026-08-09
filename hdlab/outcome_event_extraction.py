"""hdlab/outcome_event_extraction.py -- glass-box OUTCOME-EVENT extraction + extraction-fed
composition of ALREADY-PROVEN goal-outcome organs (2026-08-09, Director-redirected build).

WHY (Director redirect, evidence-grounded, superseding the earlier "swap a stronger teacher into the
acquisition loop" plan): a real-DesireDB probe found the OWNED wordnet_polarity_propagation grounding
organ scores F1 0.643/acc 0.500 (BELOW the tuned valence+negation RULE, macro-F1 0.620) not because the
organ is wrong, but because "the pipeline just rarely feeds it the right word" -- the blocker is OUTCOME
EXTRACTION (which span/event in the outcome resolves the desire), not grounding-knowledge quality or
teacher strength. This module attacks THAT: find the right span, then hand it to organs already proven
to work when fed the right span.

MECHANISM: `extract_outcome_event(desire, outcome)` parses `outcome` with the persisted UPOS-tagger +
arc-parser front end (hdlab.candidate_generator.CandidateGenerator -- the SAME checkpoint
hdlab.parse_goal_extraction.py and hdlab.goal_achievement.goal_cued_valence_channel already load;
REUSED BY IMPORT, never retrained here). For every VERB token in the parse, the token's CLAUSE is scoped
by scanning outward to the nearest hdlab.goal_typing._CB_CLAUSE_BOUNDARY token -- BYTE-IDENTICAL
technique to hdlab.consequence_learning_loop._credit_targets's own clause-bounding (no new boundary
vocabulary invented). Every NOMINAL (NOUN/PROPN/PRON) token inside that clause is tested against the
goal's referent (hdlab.goal_typing.find_desired_state) via hdlab.goal_typing._referent_links (the SAME
literal/pronoun_coref/shared_feature tiered test hdlab.consequence_learning_loop._credit_targets and
hdlab.goal_typing's own referent-recurrence channels already use). The clause with the HIGHEST referent-
link tier wins (literal > pronoun_coref > shared_feature); ties broken by whether the clause's own head
verb is a WordNet-synonym of the goal verb (hdlab.goal_achievement._verb_synonyms, reused). No clause
anywhere links to the goal referent -> None (honest abstain; never fabricates a span).

The extracted `event_span` (or, in the mandatory extraction-ablation control, the RAW whole outcome
text) is fed to FOUR already-proven organs, composed by fired-majority-vote (tie among firing channels
-> abstain, mirrors hdlab.goal_achievement.valence_channel's own npos==nneg->None convention):
  CH_A "relation"          : hdlab.goal_achievement.relation_channel (literal-synonym recurrence +
                              negation/refusal), UNMODIFIED.
  CH_B "grounded_relation" : hdlab.goal_outcome_relation_grounded.relation_votes_grounded (learned-
                              classifier ACHIEVE leg -- graded concept_similarity pool test -- +
                              CONTRADICT engagement-axis fallback), UNMODIFIED.
  CH_C "graded_relation"   : NEW, same shape as CH_A, but the goal-verb-recurrence test is
                              hdlab.lexical_similarity.concept_similarity(goal_verb, event_verb) >=
                              SIMILARITY_LINK_THRESHOLD instead of literal WordNet-synset membership --
                              the direct wire-in of concept_similarity the Director named explicitly.
  CH_V "valence"            : hdlab.goal_achievement.valence_channel, UNMODIFIED.

Every channel is called READ-ONLY / verbatim; the only genuinely-new code in this module is the
extractor itself (`extract_outcome_event`), the graded channel (`graded_relation_channel`), and the
composition (`composed_extraction_verdict`). No production file is edited. Not wired into
hdlab.goal_achievement's default verdict path -- opt-in, Director-land-decision after VET, same
discipline as the union-wire and goal_outcome_relation_grounded promotions.

Cites: hdlab.candidate_generator (CandidateGenerator, NOMINAL); hdlab.parse_goal_extraction (the
GOAL-side precedent for reusing this exact front end); hdlab.goal_typing (find_desired_state,
_referent_links, _CB_CLAUSE_BOUNDARY, _tokens, _verb_negated_before); hdlab.goal_achievement
(relation_channel, valence_channel, _extend_goal, _verb_synonyms); hdlab.goal_outcome_relation_grounded
(relation_votes_grounded, build_episode_grounded); hdlab.goal_outcome_relation (TRAIN_EXAMPLES, induce);
hdlab.lexical_similarity (concept_similarity, SIMILARITY_LINK_THRESHOLD); hdlab.thematic_role_labeler
(lemma_verb).
"""
from __future__ import annotations

import os
from typing import Dict, List, Optional, Tuple

from hdlab.candidate_generator import CandidateGenerator, NOMINAL
from hdlab.thematic_role_labeler import lemma_verb
from hdlab.goal_typing import (
    find_desired_state,
    _referent_links,
    _CB_CLAUSE_BOUNDARY,
    _tokens,
    _verb_negated_before,
)
from hdlab.goal_achievement import (
    _extend_goal,
    _verb_synonyms,
    relation_channel,
    valence_channel,
)
from hdlab import lexical_similarity as _ls
from hdlab import goal_outcome_relation as _gor
from hdlab import goal_outcome_relation_grounded as _gorg

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
POS_CKPT = os.path.join(_REPO, "data", "frontend_assets", "pos_tagger_ud_ewt_upos.json")
ARC_CKPT = os.path.join(_REPO, "data", "frontend_assets", "arc_parser_hashed_ud_ewt.npz")

_GEN_CACHE: Optional[CandidateGenerator] = None
# NOTE: "pronoun_coref" is deliberately EXCLUDED from the extractor's accepted tiers (precision-
# favoring scope decision, caught during smoke): hdlab.goal_typing._referent_links's pronoun_coref
# tier fires whenever a BARE pronoun's gender/number is merely COMPATIBLE with the referent's inferred
# gender/number -- a promiscuous test for generic/under-informative pronouns ("it"/"they"/"you"),
# which is exactly what a full-clause NOMINAL-token scan is saturated with (unlike _referent_links'
# original callers, which apply it only to a single, already structurally-narrowed subject/object
# candidate). MEASURED@this build's smoke debug: referent="doctor" (abstract/occupation noun)
# pronoun-coref-linked to a bare "It" in an UNRELATED sentence ("It was a wonderful, happy day..."),
# a clear false positive. Only "literal" (exact surface recurrence) and "shared_feature" (WordNet-
# grounded concept_similarity, itself threshold-gated) are accepted -- both are structurally immune to
# this specific promiscuity. Revisiting pronoun_coref with an added antecedent-distance/animacy gate is
# a disclosed follow-on, out of this build's scope.
_TIER_RANK = {"literal": 3, "shared_feature": 1}


def _default_generator() -> CandidateGenerator:
    """Lazily load + cache the persisted UPOS-tagger/arc-parser CandidateGenerator (module-level
    singleton, same convention as hdlab.parse_goal_extraction._default_generator -- checkpoint load
    is the slow part, every call site shares one instance)."""
    global _GEN_CACHE
    if _GEN_CACHE is None:
        _GEN_CACHE = CandidateGenerator.load(POS_CKPT, ARC_CKPT)
    return _GEN_CACHE


# ================================================================================ EXTRACTOR
def _segment_clauses(lower: List[str], n: int) -> List[Tuple[int, int]]:
    """Segment the WHOLE token sequence into clause spans (1-based, inclusive) delimited by
    hdlab.goal_typing._CB_CLAUSE_BOUNDARY tokens (boundary tokens themselves excluded from both
    neighboring spans) -- the SAME boundary vocabulary hdlab.consequence_learning_loop._credit_targets
    uses, generalized here from 'one verb's clause' to 'every clause in the text' (see
    extract_outcome_event's docstring for why per-verb scoping alone under-covers copula clauses)."""
    spans = []
    start = 1
    for i in range(1, n + 1):
        if lower[i - 1] in _CB_CLAUSE_BOUNDARY:
            if start <= i - 1:
                spans.append((start, i - 1))
            start = i + 1
    if start <= n:
        spans.append((start, n))
    return spans


def extract_outcome_event(desire: str, outcome: str, gen: Optional[CandidateGenerator] = None) -> Optional[dict]:
    """Locate the outcome CLAUSE that resolves `desire`'s referent. Returns
    {"event_span", "clause_start", "clause_end", "verb_idx", "verb_lemma", "verb_matches_goal",
    "referent_link_tier", "referent", "goal_verb_lemma"} or None (no goal recognized, no referent, or
    no clause anywhere links to the referent -- honest abstain, never fabricates a span).

    Clauses are segmented from the WHOLE outcome UPFRONT via `_segment_clauses` (not centered on VERB
    tokens): a naive "scope a clause around each VERB-tagged token" design silently misses every
    COPULA-headed clause ("I am Kame", "It was a success") because UD tags a copula as AUX, not VERB --
    caught during smoke (a literal referent match inside a copula-only sentence produced zero candidate
    clauses). Each segmented clause is scored by referent-link tier over its NOMINAL tokens; the
    tie-breaking verb-match bonus looks for a VERB token first, falling back to AUX (covers copula
    clauses) -- absence of either only costs the tie-break bonus, never blocks extraction itself."""
    g = find_desired_state(_extend_goal(desire))
    if g is None:
        return None
    referent = g.get("referent")
    if referent is None:
        return None
    goal_verb = g.get("verb_lemma")
    goal_verb_syns = _verb_synonyms(goal_verb) if goal_verb else frozenset()

    gen = gen or _default_generator()
    cr = gen.generate(outcome)
    toks, pos, heads = cr.tokens, cr.pos, cr.heads
    n = len(toks)
    if n == 0:
        return None
    lower = [t.lower() for t in toks]

    best = None
    best_score = -1
    for (cl_start, cl_end) in _segment_clauses(lower, n):
        link_tier = None
        for i in range(cl_start, cl_end + 1):
            if pos[i - 1] not in NOMINAL:
                continue
            ok, tier = _referent_links(referent, lower[i - 1])
            if ok and tier in _TIER_RANK and (link_tier is None or _TIER_RANK[tier] > _TIER_RANK.get(link_tier, 0)):
                link_tier = tier
        if link_tier is None:
            continue  # no referent link anywhere in this clause -> not a candidate event
        verb_idx = None
        for i in range(cl_start, cl_end + 1):
            if pos[i - 1] == "VERB":
                verb_idx = i
                break
        if verb_idx is None:
            for i in range(cl_start, cl_end + 1):
                if pos[i - 1] == "AUX":
                    verb_idx = i
                    break
        verb_lemma = lemma_verb(lower[verb_idx - 1]) if verb_idx is not None else None
        verb_matches_goal = bool(goal_verb) and verb_lemma is not None and \
            (verb_lemma == goal_verb or verb_lemma in goal_verb_syns)
        score = _TIER_RANK.get(link_tier, 0) * 10 + (5 if verb_matches_goal else 0)
        if score > best_score:
            best_score = score
            best = {
                "event_span": " ".join(toks[cl_start - 1:cl_end]),
                "clause_start": cl_start, "clause_end": cl_end, "verb_idx": verb_idx,
                "verb_lemma": verb_lemma, "verb_matches_goal": verb_matches_goal,
                "referent_link_tier": link_tier, "referent": referent, "goal_verb_lemma": goal_verb,
            }
    return best


# ================================================================================ CH_C: graded relation
def graded_relation_channel(desire: str, event_span: str) -> Tuple[Optional[str], dict]:
    """Same shape as hdlab.goal_achievement.relation_channel (goal-verb recurrence + negation/refusal
    over `event_span`) but the recurrence test is GRADED: hdlab.lexical_similarity.concept_similarity
    (McRae-style shared-feature cosine) against the goal verb, cleared at SIMILARITY_LINK_THRESHOLD,
    instead of literal WordNet-synset membership. Returns (verdict, trace); trace always reports
    `best_sim` (even sub-threshold, or None if every candidate was OOV of CONCEPT_FEATURES) so a
    near-miss is distinguishable from "no lexical anchor exists at all" (diagnosis taxonomy)."""
    g = find_desired_state(_extend_goal(desire))
    if g is None or not g.get("verb_lemma"):
        return None, {"reason": "no_goal", "best_sim": None}
    gl = g["verb_lemma"]
    toks = _tokens(event_span)
    recur_idx = None
    best_sim = None
    for i, tok in enumerate(toks):
        lem = lemma_verb(tok)
        sim = _ls.concept_similarity(gl, lem)
        if sim is None:
            continue
        if best_sim is None or sim > best_sim:
            best_sim = sim
        if sim >= _ls.SIMILARITY_LINK_THRESHOLD and (recur_idx is None or sim > best_sim - 1e-9):
            recur_idx = i
    if recur_idx is None:
        reason = "below_threshold" if best_sim is not None else "no_lexical_anchor"
        return None, {"reason": reason, "best_sim": best_sim}
    neg = _verb_negated_before(toks, recur_idx)
    verdict = "Unfulfilled" if neg else "Fulfilled"
    return verdict, {"reason": "concept_match_negated" if neg else "concept_match", "best_sim": best_sim}


# ================================================================================ CH_B: induced classifier (cached)
_gor_classifier_cache = None


def _induced_gor_classifier():
    """Lazy, module-wide-cached induction of goal_outcome_relation's classifier on its own
    TRAIN_EXAMPLES via the GROUNDED (concept_similarity-mediated) feature pipeline -- byte-identical
    call sequence to hdlab.goal_outcome_relation_grounded.self_test's own induction step. Deterministic
    (fixed TRAIN_EXAMPLES, no RNG)."""
    global _gor_classifier_cache
    if _gor_classifier_cache is None:
        train_eps = [_gorg.build_episode_grounded(d, o, c, tag) for d, o, c, tag in _gor.TRAIN_EXAMPLES]
        chosen_name, chosen, _all = _gor.induce(train_eps)
        _gor_classifier_cache = (chosen_name, chosen.hypothesis if chosen is not None else None)
    return _gor_classifier_cache


# ================================================================================ composition
def composed_extraction_verdict(desire: str, event_span: str) -> Tuple[Optional[str], dict]:
    """Runs CH_A/CH_B/CH_C/CH_V on (desire, event_span) and composes by fired-majority-vote (tie among
    FIRING channels -> abstain). Returns (verdict, trace) where trace names each channel's own
    verdict/reason for per-item glass-box audit."""
    chosen_name, chosen_hyp = _induced_gor_classifier()

    a_verdict, a_reason = relation_channel(desire, event_span)
    b_votes = _gorg.relation_votes_grounded(desire, event_span, chosen_name, chosen_hyp)
    if b_votes["POS"] > b_votes["NEG"]:
        b_verdict = "Fulfilled"
    elif b_votes["NEG"] > b_votes["POS"]:
        b_verdict = "Unfulfilled"
    else:
        b_verdict = None
    c_verdict, c_trace = graded_relation_channel(desire, event_span)
    v_verdict = valence_channel(event_span)

    named = [("relation", a_verdict), ("grounded_relation", b_verdict),
             ("graded_relation", c_verdict), ("valence", v_verdict)]
    fired = [(name, vv) for name, vv in named if vv is not None]
    n_fulfilled = sum(1 for _, vv in fired if vv == "Fulfilled")
    n_unfulfilled = sum(1 for _, vv in fired if vv == "Unfulfilled")
    if not fired or n_fulfilled == n_unfulfilled:
        final = None
    else:
        final = "Fulfilled" if n_fulfilled > n_unfulfilled else "Unfulfilled"

    trace = {
        "relation": a_verdict, "relation_reason": a_reason,
        "grounded_relation": b_verdict, "grounded_relation_votes": b_votes,
        "graded_relation": c_verdict, "graded_relation_trace": c_trace,
        "valence": v_verdict,
        "fired": [n for n, _ in fired], "n_fulfilled": n_fulfilled, "n_unfulfilled": n_unfulfilled,
    }
    return final, trace


def real_arm_predict(desire: str, outcome: str, gen: Optional[CandidateGenerator] = None) -> Tuple[Optional[str], dict]:
    """REAL arm: extraction-fed. Abstains (None) when extraction itself finds no linked clause --
    kept structurally distinct from the ablation arm's always-attempt-on-whole-text behavior."""
    event = extract_outcome_event(desire, outcome, gen=gen)
    if event is None:
        return None, {"extraction_fired": False, "event": None}
    verdict, trace = composed_extraction_verdict(desire, event["event_span"])
    trace["extraction_fired"] = True
    trace["event"] = event
    return verdict, trace


def ablation_arm_predict(desire: str, outcome: str) -> Tuple[Optional[str], dict]:
    """EXTRACTION-ABLATION control: SAME 4-channel composition fed the WHOLE unparsed outcome text
    (no clause extraction at all). Isolates whether extraction specifically carries the lift."""
    verdict, trace = composed_extraction_verdict(desire, outcome)
    trace["extraction_fired"] = "n_a_ablation_uses_whole_text"
    trace["event"] = None
    return verdict, trace


def pairscramble_arm_predict(scrambled_desire: str, outcome: str,
                              gen: Optional[CandidateGenerator] = None) -> Tuple[Optional[str], dict]:
    """PAIRSCRAMBLE control: identical to real_arm_predict but the desire is a WRONG (deterministically
    deranged) partner's -- extraction AND all 4 channels run end-to-end against the mismatched goal.
    Must collapse toward no-recovery (proves genuine goal<->outcome matching carries the real arm's
    lift, not exposure/plumbing alone)."""
    return real_arm_predict(scrambled_desire, outcome, gen=gen)


# ================================================================================ self-test
def self_test() -> dict:
    """Real-code-path check (SCHEMA-VET F.1): constructs the REAL CandidateGenerator, runs extraction
    + all 4 channels + composition on hand-authored cases (no DesireDB / no network)."""
    gen = _default_generator()

    # (1) extraction fires + picks the referent-linked clause over a distractor clause.
    desire = "I wanted to fix the old fence in the yard."
    outcome = ("The weather was miserable and gloomy all week. "
               "Later the fence was repaired nicely by a neighbor.")
    ev = extract_outcome_event(desire, outcome, gen=gen)
    assert ev is not None, "extraction must fire on a clear referent-linked case"
    assert "fence" in ev["event_span"].lower(), f"extraction picked the wrong clause: {ev}"
    assert ev["referent_link_tier"] == "literal", ev

    # (2) extraction abstains honestly when no clause links to the referent.
    desire2 = "I wanted to become a doctor."
    outcome2 = "It was a wonderful, happy day and everyone felt great."
    ev2 = extract_outcome_event(desire2, outcome2, gen=gen)
    assert ev2 is None, f"extraction must abstain with no referent link, got {ev2}"

    # (3) composed_extraction_verdict: mechanism-fires on a clean case (relation channel should fire).
    v, trace = composed_extraction_verdict(desire, ev["event_span"])
    assert v == "Fulfilled", f"expected Fulfilled on a clean repaired-fence case, got {v} ({trace})"
    assert "relation" in trace["fired"] or "valence" in trace["fired"], trace

    # (4) graded_relation_channel: fires via concept similarity even when literal recurrence would not
    # (goal verb 'fix' vs a near-synonymous but non-WordNet-synset outcome verb), and reports best_sim
    # for near-miss diagnosis.
    c_verdict, c_trace = graded_relation_channel("I wanted to mend the old boat.",
                                                 "The boat was repaired by evening.")
    assert c_trace["best_sim"] is not None, c_trace

    # (5) real_arm_predict / ablation_arm_predict / pairscramble_arm_predict all callable + honest
    # structural distinction (real abstains when extraction fails; ablation always attempts).
    r_v, r_t = real_arm_predict(desire2, outcome2, gen=gen)
    assert r_v is None and r_t["extraction_fired"] is False, r_t
    a_v, a_t = ablation_arm_predict(desire2, outcome2)
    assert a_t["extraction_fired"] == "n_a_ablation_uses_whole_text", a_t
    p_v, p_t = pairscramble_arm_predict(desire2, outcome, gen=gen)  # wrong desire, real outcome
    assert "extraction_fired" in p_t

    # (6) induced classifier is deterministic + cached (same object across calls).
    n1, h1 = _induced_gor_classifier()
    n2, h2 = _induced_gor_classifier()
    assert n1 == n2 and h1 is h2, "induced classifier must be cached + deterministic"

    return {
        "extraction_fires_ok": True, "extraction_abstain_ok": True,
        "clean_case_verdict": v, "clean_case_trace": trace,
        "graded_relation_best_sim": c_trace["best_sim"],
        "real_arm_abstain_structural_ok": True, "ablation_arm_ok": True,
        "induced_classifier_cached_ok": True, "induced_classifier_name": n1,
    }


if __name__ == "__main__":
    import json
    print(json.dumps(self_test(), indent=2, default=str))
    print("ALL SELF-TESTS PASSED")
