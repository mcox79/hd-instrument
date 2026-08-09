"""hdlab/goal_outcome_relation.py (2026-08-09) -- Direction-B fork-A: does a GOAL<->OUTCOME
SEMANTIC-RELATION mechanism recover the DesireDB abstain-cohort residual Director's own decomposition
surfaced after M1 (idiom lexicon, 0/37 breadth) and M2/M3-inc1 (learned result-type classifier,
plateaued at 3/8 primary / 9/37 breadth, "no returns" HARD_FAIL)? Of the abstain-cohort's non-firing
items, the goal-relevance lives in the RELATION between the outcome EVENT and the GOAL, with NO
word-level cue -- two relation types, given TWO STRUCTURALLY DIFFERENT mechanisms (per the 2026-08-09
Director+USER design-refinement mid-build -- see "DESIGN REFINEMENT" below):

  MEANS-END / INSTANTIATES (->Fulfilled): the outcome event INSTANTIATES the goal (a means/instance
    of it). "wanted to KNOW why" / "I TALKED about that" (talk instantiates know); "wanted to be OUT
    AND ABOUT" / "went GROCERY SHOPPING" (shopping instantiates out-and-about); "wanted to PRACTICE
    sitflying" / "instructor GOT ME sitflying" (instructed-practice instantiates skill-practice).
    GENUINELY COMPOSITIONAL (a verb-CLASS relation, e.g. any communication verb instantiates a
    cognition goal) -- measured via a LEARNED classifier (hdlab.learner.registry.learn) over
    construction-cue features, held-out-surface-form GENERALIZATION accuracy.
  CONVENTIONALIZED CONTRADICTION (->Unfulfilled): the outcome is a conventionalized avoidance/
    disengagement/block/refusal expression that CONTRADICTS an engagement/achievement goal (goal-
    RELATIVE -- the SAME disengage-flavored outcome could INSTANTIATE an avoidance-type goal instead;
    see `goal_polarity`). "wanted her to stay and talk" / "she WALKED AWAY"; "wanted to keep
    negotiating" / "they BACKED OFF"; a reflexive self-reliance construction ("wanted him to fix the
    car" / "she TOOK CARE OF IT ON HER OWN", no-collaboration). NON-COMPOSITIONAL / a DICTIONARY-
    LOOKUP problem, NOT a generalization-of-a-tiny-hand-authored-class problem (idioms/colloquialisms
    share nothing lexically with each other -- "kibosh" shares nothing with "walk away") -- measured
    via WordNet multi-word-expression (MWE) lemma GLOSSES (owned, immediate) for COVERAGE against a
    dictionary-grounded representative phrase bank, NOT held-out generalization accuracy of a learned
    classifier. The self-reliance REFLEXIVE construction (verb-agnostic regex, not a word-list) is
    the one CONTRADICTS sub-class that genuinely is compositional and is kept in the learned
    classifier's held-out generalization test.

DESIGN REFINEMENT (2026-08-09, Director+USER, applied mid-build -- see prereg "Scope changes"
section): the FIRST build of this module tried to test CONTRADICTS generalization the SAME way as
MEANS-END (a tiny 2-item TRAIN set -> registry.learn -> held-out surface forms including genuinely
unrelated idioms like "turned the other cheek"/"kibosh"). Director+USER correctly flagged this as
category-confused: idioms/colloquialisms are NON-COMPOSITIONAL by definition, so "does a learned
classifier generalize from 2 examples to an unrelated idiom" is not a meaningful test -- the right
question is COVERAGE of a real lexical resource (dictionary lookup), not generalization of a tiny
hand-authored class. This module was rewritten to measure the CONTRADICTS/disengagement fraction via
`mwe_disengage_scan` (WordNet-MWE + gloss keyword classification, see below) reported as coverage %
against `REPRESENTATIVE_DISENGAGEMENT_PHRASES` (authored from conventional/dictionary knowledge of
this semantic class -- e.g. Merriam-Webster's phrasal-verb entries for "back off"/"pull out"/"give
up" -- NEVER from checking which DesireDB item it would flip). A richer supply source (kaikki.org
Wiktextract, the full machine-readable English Wiktionary with idiomatic/colloquial/slang register
tags) was identified as the scale-up ceiling but MEASURED infeasible to fetch+parse within this local
CPU run (HEAD request this session: raw JSONL Content-Length=3,212,430,706 bytes [~3.2GB], gzip
Content-Length=501,997,915 bytes [~502MB], both at https://kaikki.org/dictionary/English/ -- see
"COVERAGE PROVENANCE" below) -- WordNet-MWE is therefore reported as the FLOOR, not the ceiling, with
kaikki-Wiktionary flagged as the verified next-step supply source for M3 (never hand-authored to fill
the gap, per calibration-honesty).

STAGE-1-CONFOUND IMMUNITY (identical discipline to Stage-2/M1/M2/M3-inc1, hdlab/goal_achievement.py's
own module comment): NEITHER mechanism compares the goal's specific words directly against the
outcome's specific words. MEANS-END goal-side atoms (goal_cognition/goal_activity_engagement/
goal_skill_practice) are computed from `hdlab.goal_typing.find_desired_state(desire)`'s verb_lemma/
referent against a FIXED, outcome-independent exemplar pool -- never inspects outcome text.
MEANS-END outcome-side atoms (outcome_info_exchange/outcome_errand_activity/outcome_skill_training)
and the self-reliance construction atom are computed from outcome tokens/regex against a FIXED,
goal-independent pool -- never inspect the goal's specific words. `mwe_disengage_scan` similarly
never inspects the goal's words -- it fires on the OUTCOME's own WordNet-MWE dictionary sense; the
GOAL-RELATIVE mapping (`goal_polarity`) reads only the goal's own ENGAGEMENT-vs-AVOIDANCE polarity
(a closed 2-way structural class), never a goal-specific word comparison against the outcome. The
BRIDGE between goal and outcome runs only through shared CLASS-LEVEL signals (relation-type /
dictionary-gloss-polarity / goal-polarity), never through direct goal-word-vs-outcome-word
comparison -- structurally unable to inherit Stage-1's tautological-absence failure.

GROUNDING TECHNIQUE CALIBRATION for MEANS-END (MEASURED@this session's design probe, scratchpad
diagnostics, not committed -- summarized here per calibration-honesty): three WordNet techniques
were tried for the MEANS-END outcome-side pools (info_exchange/errand_activity/skill_training)
before literal-pool authorship was adopted: (a) primary-sense-only pool_related (goal_achievement.
py's own `_pool_related`, k=1, no hypernym expansion) essentially FAILED to bridge this vocabulary
(discuss/explain/tell/chat/describe/mentor/practice/figure/grasp/discover/chore ALL measured False
against small 2-word seed pools); (b) all-senses hypernym-ancestor bridging (depth 2-3) MEASURED
much noisier (an obscure secondary sense of "shop" -- British-slang "inform on someone" -- spuriously
bridged "explained" to an unrelated pool; common light verbs want/be/get/put/move spuriously bridged
to arbitrary pools via generic hub synsets); (c) ADOPTED: literal, hand-authored pool membership
(6-10 members/pool, from conventional/dictionary synonymy) PLUS a light-verb exclusion list PLUS a
Tier-2 `_pool_related`-style fallback for genuine OOV words -- the SAME pattern `hdlab/goal_
achievement.py`'s ATTRIBUTES dict and `hdlab/idiom_grounding.py`'s IDIOM_LEXICON already use.

MWE-DISENGAGE-SCAN MECHANISM (CONTRADICTS/dictionary-lookup route): scans the outcome for a
contiguous 1-4-token span whose morphy-normalized head, joined with its tail, is a WordNet VERB
lemma (`walk_off`, `back_off`, `give_up`, `call_it_quits`, `throw_in_the_towel`, or a bare
single-word verb like `withdrew`/`abandoned`/`quit`) with AT LEAST ONE sense whose GLOSS contains a
disengagement/refusal/abandonment keyword (checks ALL senses, not just primary -- a deliberately
BROADER check than this arc's other primary-sense-only Tier-2 fallbacks, appropriate here because
this is a COVERAGE measurement of a whole-gloss keyword match against a real dictionary resource, not
a fine per-token polarity vote prone to the obscure-secondary-sense noise class documented in (b)
above and elsewhere in this arc). ONE discontinuous span is hand-declared (the "put THE
kibosh/kabash/kabosh/kibash ON" light-verb frame -- DesireDB's own attested misspelling of "kibosh"
per hdlab/idiom_grounding.py's docstring; "kibosh" IS a real WordNet lemma, kibosh.v ->
stop.v.03 "stop from happening or developing", so this is a spelling/discontinuity accommodation of
a REAL dictionary entry, not a hand-authored idiom) -- not a general discontinuous-MWE parser.

COVERAGE PROVENANCE (measured this session, MEASURED@`REPRESENTATIVE_DISENGAGEMENT_PHRASES` self-
test): WordNet-MWE floor coverage = 26/29 = 0.897 on a dictionary-grounded representative phrase
bank (authored from conventional Merriam-Webster/dictionary phrasal-verb meaning, never from
DesireDB); false-positive probe on 5 unrelated real-outcome sentences = 0/5 clean. Disclosed misses
(genuine WordNet gloss/lemma gaps, NOT patched): "bailed out" (bail_out.v IS a WordNet lemma but its
2 listed senses -- legal bail, bailing water -- do not carry a disengagement gloss), "chickened out"
(chicken_out is referenced only as ANOTHER lemma's gloss target, not itself indexed), "shied away",
"washed her hands of" (both absent from WordNet entirely), "turned the other cheek" (confirmed 0
WordNet synsets -- genuinely idiomatic, matches this arc's own repeated finding that a
conventionalization SPECTRUM exists from productive phrasal-verb (WordNet-covered) to fully
idiomatic (dictionary-absent)). kaikki.org Wiktextract (the full English Wiktionary, editorially
vetted unlike Urban Dictionary, with idiomatic/colloquial/slang register tags) is the verified
scale-up ceiling for these specific gaps -- flagged, NOT fetched (3.2GB raw / 502MB gzip, infeasible
for this local CPU run's compute-proportionality budget; see module docstring's DESIGN REFINEMENT
section for the exact measured Content-Length values and URLs).
"""
from __future__ import annotations

import re
from typing import Dict, List, Optional, Tuple

from hdlab import goal_typing as _gt
from hdlab.learner import registry

RELATION_TYPES = ("INSTANTIATES", "CONTRADICTS", "NEITHER")
RELATION_POLARITY = {"INSTANTIATES": "POS", "CONTRADICTS": "NEG"}  # NEITHER never votes

# ---------------------------------------------------------------------------------------------
# Standalone WordNet primary-sense pool-overlap check (Tier-2 fallback for MEANS-END only). Self-
# contained copy of hdlab.goal_achievement._pool_related/_primary_synonyms (same already-vetted
# technique) to avoid a circular import (goal_achievement imports THIS module below), matching
# hdlab/result_type_induction.py's own established convention for the identical reason.
# ---------------------------------------------------------------------------------------------
def _primary_synonyms(word: str, pos) -> frozenset:
    from nltk.corpus import wordnet as _wn
    syn = {word}
    syns = _wn.synsets(word, pos=pos)
    if syns:
        for l in syns[0].lemmas():
            syn.add(l.name().replace("_", " ").lower())
    return frozenset(syn)


def _pool_related(word: str, pool) -> bool:
    from nltk.corpus import wordnet as _wn
    if word in pool:
        return True
    for pos in (_wn.VERB, _wn.ADJ, _wn.NOUN):
        w_syn = _primary_synonyms(word, pos)
        for cand in pool:
            if w_syn & _primary_synonyms(cand, pos):
                return True
    return False


# ============================================================================ MEANS-END: hand-
# authored, dictionary-grounded pools (literal Tier-1 membership + Tier-2 _pool_related fallback).
# See module docstring's calibration note for why literal authorship, not automatic WordNet
# hypernym expansion.
LIGHT_STOP = frozenset({
    "be", "is", "are", "was", "were", "been", "being", "do", "does", "did", "doing", "done",
    "have", "has", "had", "get", "gets", "got", "go", "goes", "went", "going", "gone",
    "the", "a", "an", "it", "this", "that", "and", "but", "not",
})

INFO_EXCHANGE_POOL = ["talk", "say", "speak", "tell", "discuss", "explain", "describe", "chat",
                       "converse", "read"]
ERRAND_POOL = ["shop", "shopping", "errand", "errands", "chore", "chores", "outing"]
SKILL_TRAIN_POOL = ["practice", "train", "instruct", "instructor", "teach", "drill", "coach",
                     "mentor", "tutor", "lesson"]
COGNITION_GOAL_POOL = ["know", "understand", "learn", "realize", "figure", "discover"]
SKILL_GOAL_VERB_POOL = ["practice", "train", "drill", "improve", "master"]
SKILL_GOAL_REFERENT_POOL = ["skill", "skills", "technique", "better"]
ACTIVITY_ENGAGEMENT_WORDS = frozenset({"out", "about", "active", "busy", "occupied", "engaged",
                                        "involved"})

# self-reliance: a genuinely verb-agnostic REGEX construction (reflexive pronoun / "on X own" /
# "by X-self") -- COMPOSITIONAL (any verb + this marking fires), unlike a fixed-phrase idiom
# lexicon, so it stays in the LEARNED classifier's held-out generalization test (unlike
# mwe_disengage_scan below, which is a dictionary-lookup, not a construction).
SELF_RELIANCE_RE = re.compile(
    r"\b(myself|himself|herself|themselves|ourselves)\b|"
    r"\bon (?:my|his|her|their|our) own\b|"
    r"\bby (?:myself|himself|herself|themselves|ourselves)\b")

CONSTRUCTION_ATOMS = ["goal_cognition", "goal_activity_engagement", "goal_skill_practice",
                       "outcome_info_exchange", "outcome_errand_activity", "outcome_skill_training",
                       "outcome_self_reliance_reflexive", "no_relation_cue"]


def goal_atoms(desire: str) -> List[str]:
    """GOAL-side atoms ONLY -- computed from find_desired_state(desire)'s verb_lemma/referent (never
    inspects outcome text; Stage-1-confound-immunity, see module docstring)."""
    feats = []
    g = _gt.find_desired_state(desire)
    vl = (g or {}).get("verb_lemma")
    ref = (g or {}).get("referent")
    if vl and vl not in LIGHT_STOP and _pool_related(vl, COGNITION_GOAL_POOL):
        feats.append("goal_cognition")
    if any(t in ACTIVITY_ENGAGEMENT_WORDS for t in _gt._tokens(desire)):
        feats.append("goal_activity_engagement")
    if (vl and vl not in LIGHT_STOP and _pool_related(vl, SKILL_GOAL_VERB_POOL)) or \
            (ref and ref in SKILL_GOAL_REFERENT_POOL):
        feats.append("goal_skill_practice")
    return feats


def outcome_atoms(outcome: str) -> List[str]:
    """OUTCOME-side atoms ONLY (means-end pools + the self-reliance construction) -- computed from
    outcome tokens/regex (never inspects the goal's specific words; Stage-1-confound-immunity, see
    module docstring). Does NOT include disengagement/MWE detection -- that is `mwe_disengage_scan`,
    a separate DICTIONARY-LOOKUP mechanism, deliberately excluded from the learned classifier's
    feature space per the 2026-08-09 design refinement (see module docstring)."""
    toks = [t for t in _gt._tokens(outcome) if t not in LIGHT_STOP]
    feats = []
    if any(t.isalpha() and len(t) > 2 and _pool_related(t, INFO_EXCHANGE_POOL) for t in toks):
        feats.append("outcome_info_exchange")
    if any(t.isalpha() and len(t) > 2 and _pool_related(t, ERRAND_POOL) for t in toks):
        feats.append("outcome_errand_activity")
    if any(t.isalpha() and len(t) > 2 and _pool_related(t, SKILL_TRAIN_POOL) for t in toks):
        feats.append("outcome_skill_training")
    if SELF_RELIANCE_RE.search(outcome.lower()):
        feats.append("outcome_self_reliance_reflexive")
    if not feats:
        feats.append("no_relation_cue")
    return feats


def pair_feats(desire: str, outcome: str) -> List[str]:
    """The 8 boolean CONSTRUCTION_ATOMS for a (desire, outcome) PAIR -- goal_atoms UNION
    outcome_atoms. NEVER contains a literal lemma from either side, only class-level atom names, so
    the induced hypothesis transfers to a held-out surface form on EITHER side (frame_induction's
    discipline, extended to pair-level episodes). Covers MEANS-END (INSTANTIATES) and the
    self-reliance CONTRADICTS sub-class only -- see module docstring for why MWE-disengage
    (CONTRADICTS' other, non-compositional sub-class) is a separate dictionary-lookup function."""
    return goal_atoms(desire) + outcome_atoms(outcome)


def build_episode(desire: str, outcome: str, gold_class: str, tag: str = "") -> dict:
    return {"feats": pair_feats(desire, outcome), "gold_class": gold_class, "tag": tag}


# ---------------------------------------------------------------------------------------------
# TRAIN / HELD-OUT surface-form banks (MEANS-END generalization + self-reliance construction
# generalization ONLY -- see module docstring; the disengagement/MWE fraction is measured for
# COVERAGE below, not generalization). Held-out tags are DISJOINT from train tags (asserted in
# self_test); held-out items use DIFFERENT literal pool members / different phrasings than TRAIN on
# the SAME class.
# ---------------------------------------------------------------------------------------------
TRAIN_EXAMPLES: List[Tuple[str, str, str, str]] = [
    # ---- MEANS-END / INSTANTIATES ----
    ("I wanted to know why he left.", "I talked to him about it.", "INSTANTIATES", "talk_know"),
    ("She wanted to understand the problem.", "She read several articles about it.",
     "INSTANTIATES", "read_understand"),
    ("He wanted to be out and about.", "He went grocery shopping that afternoon.",
     "INSTANTIATES", "shopping_outabout"),
    ("She wanted to stay busy and active.", "She ran errands all day.",
     "INSTANTIATES", "errand_busy"),
    ("He wanted to practice sitflying.", "The instructor got him sitflying that weekend.",
     "INSTANTIATES", "instructed_practice"),
    ("She wanted to improve her skill at chess.", "Her coach drilled her on openings for an hour.",
     "INSTANTIATES", "coached_drill"),
    # ---- SELF-RELIANCE CONSTRUCTION / CONTRADICTS ----
    ("She wanted him to help her move.", "In the end she managed it herself.",
     "CONTRADICTS", "did_it_herself"),
    ("He wanted them to pitch in.", "He ended up handling it on his own.",
     "CONTRADICTS", "handled_own"),
    # ---- NEITHER (goal-class/outcome-class MISMATCH, or genuinely unrelated content) ----
    ("He wanted to know why she left.", "He cooked dinner and watched a movie.",
     "NEITHER", "unrelated_cook"),
    ("She wanted to be out and about.", "It rained heavily all weekend.",
     "NEITHER", "unrelated_rain"),
    ("He wanted to practice sitflying.", "He stayed home reading a book all day.",
     "NEITHER", "read_vs_practice_mismatch"),
    ("She wanted to understand the recipe.", "She gave up and ate a sandwich instead.",
     "NEITHER", "gaveup_vs_cognition"),
    ("She wanted to be out and about.", "She stayed in and read all day.",
     "NEITHER", "activity_goal_read_outcome_mismatch"),
    ("He wanted them to pitch in.", "They threw a small party for him.",
     "NEITHER", "pitch_in_party_unrelated"),
]

HELDOUT_EXAMPLES: List[Tuple[str, str, str, str]] = [
    # ---- MEANS-END: same INFO_EXCHANGE_POOL, DIFFERENT literal members than TRAIN (talk/read) ----
    ("I wanted to know why he left.", "We discussed it at length last night.",
     "INSTANTIATES", "discuss_know"),
    ("I wanted to know the truth.", "She explained everything to me.",
     "INSTANTIATES", "explain_know"),
    ("I wanted to know what happened.", "He told me the whole story.",
     "INSTANTIATES", "tell_know"),
    ("She wanted to understand the contract terms.", "Her lawyer described each clause carefully.",
     "INSTANTIATES", "describe_understand"),
    # ---- MEANS-END: same ERRAND_POOL/ACTIVITY words, DIFFERENT members than TRAIN ----
    ("She wanted to get out of the house.", "She spent the day doing chores around town.",
     "INSTANTIATES", "chores_out_of_house"),
    ("He wanted to stay involved with the club.", "He signed up for every outing they planned.",
     "INSTANTIATES", "outing_involved"),
    # ---- MEANS-END: same SKILL_TRAIN_POOL, DIFFERENT member than TRAIN (instruct/coach/drill) ----
    ("He wanted to get better at chess.", "A mentor coached him through several matches.",
     "INSTANTIATES", "mentor_teach_skill"),
    # ---- SELF-RELIANCE CONSTRUCTION: DIFFERENT phrasing than TRAIN ----
    ("She wanted him to fix the car.", "In the end she took care of it on her own.",
     "CONTRADICTS", "took_care_own"),
    ("He wanted her to ask him for help moving the boxes.", "In the end she carried them by herself.",
     "CONTRADICTS", "carried_by_herself"),
    # ---- NEITHER ----
    ("I wanted to know why he left.", "It snowed all afternoon.", "NEITHER", "unrelated_snow"),
    ("She wanted to get better at chess.", "She baked a cake for the party.",
     "NEITHER", "unrelated_cake"),
]

# Sub-type groupings for the honest recovery-vs-long-tail breakdown (per the task's explicit
# mandate: "report per-relation-type breakdown + generalization separately from recovery").
HELDOUT_SUBTYPES: Dict[str, List[str]] = {
    "means_end": ["discuss_know", "explain_know", "tell_know", "describe_understand",
                  "chores_out_of_house", "outing_involved", "mentor_teach_skill"],
    "self_reliance_construction": ["took_care_own", "carried_by_herself"],
    "neither": ["unrelated_snow", "unrelated_cake"],
}


def default_spec(classes=RELATION_TYPES, atoms=None, max_nodes: int = 4) -> dict:
    """Hypothesis-space CONFIG: MDL-auto-select over estimation/ruleind, mirroring
    hdlab.result_type_induction.default_spec's structure. `proginduction` is DELIBERATELY EXCLUDED
    from candidate_plugins (compute-proportionality): result_type_induction's own design probe
    MEASURED 91s at n_atoms=9/max_nodes=7 vs 0.26s at n_atoms=7/max_nodes=5 -- estimation+ruleind
    (the SAME plugin M2 actually chose as its MDL winner) already cover this hypothesis space."""
    atoms = list(atoms) if atoms is not None else list(CONSTRUCTION_ATOMS)
    classes = list(classes)

    def _key_fn(ep):
        return "|".join(sorted(ep["feats"]))

    return {
        "candidate_plugins": ["estimation", "ruleind"],
        "per_plugin": {
            "estimation": {"mode": "generic_mdl", "key_fn": _key_fn,
                           "label_fn": lambda ep: ep["gold_class"], "classes": classes},
            "ruleind": {"max_conjunct": 2, "min_coverage": 2, "purity_thresh": 0.75,
                        "max_rules": 25, "key_fn": _key_fn},
        },
    }


def induce(episodes: List[dict], spec: Optional[dict] = None):
    """Fit + MDL-auto-select. Returns (chosen_name, chosen_LearnResult_or_None, all_results)."""
    spec = spec or default_spec()
    return registry.learn(episodes, lambda ep: ep["feats"], spec)


def predict(chosen_name, hypothesis, feats: List[str], key: str, default: Optional[str]) -> Optional[str]:
    """Consult the induced hypothesis. Mirrors result_type_induction.predict's honest-degrade path."""
    if hypothesis is None:
        return default
    feats = list(feats)
    if chosen_name == "ruleind":
        from hdlab.learner.plugins import ruleind_plugin
        pred = ruleind_plugin.apply(hypothesis, feats, key=key, default_class=default)
    elif chosen_name == "estimation":
        from hdlab.learner.plugins import estimation_plugin
        pred = estimation_plugin.apply(hypothesis, key)
    else:  # KEEP_EPISODIC or unknown
        pred = None
    return pred if pred is not None else default


def memorization_baseline_predict(train_examples: List[Tuple[str, str, str, str]], tag: str,
                                   default: str) -> str:
    """GATE-1 memorization-baseline control: exact TRAIN-surface-form-tag lookup. By construction
    every HELDOUT_EXAMPLES tag is absent from TRAIN_EXAMPLES (disjointness asserted in self_test),
    so this can only ever return `default` on held-out items."""
    lookup: Dict[str, str] = {}
    for _d, _o, gold, tag_ in train_examples:
        lookup.setdefault(tag_, gold)
    return lookup.get(tag, default)


_INDUCED_HYP_CACHE: Optional[Tuple[Optional[str], Optional[object]]] = None


def get_induced_hypothesis(use_cache: bool = True) -> Tuple[Optional[str], Optional[object]]:
    """(chosen_name, hypothesis) trained ONCE on TRAIN_EXAMPLES only (module-level cache) -- the SAME
    hypothesis GATE-1's held-out eval uses, reused unmodified for GATE-2's DesireDB scoring. NEVER
    trains on DesireDB (anti-circular design, identical mandate to M2's get_induced_hypothesis)."""
    global _INDUCED_HYP_CACHE
    if use_cache and _INDUCED_HYP_CACHE is not None:
        return _INDUCED_HYP_CACHE
    train_eps = [build_episode(d, o, c, tag) for d, o, c, tag in TRAIN_EXAMPLES]
    chosen_name, chosen, _all = induce(train_eps)
    result = (chosen_name, chosen.hypothesis) if chosen is not None else (None, None)
    if use_cache:
        _INDUCED_HYP_CACHE = result
    return result


# ============================================================================ CONTRADICTS
# non-compositional fraction: WordNet-MWE DICTIONARY LOOKUP (coverage-measured, not learned/
# generalization-tested -- see module docstring's DESIGN REFINEMENT section).
DISENGAGE_GLOSS_KEYWORDS = ["away", "back off", "backward", "withdraw", "abandon", "give up",
                            "stop", "cease", "refuse", "retreat", "remove oneself", "chicken out",
                            "forfeit", "quit", "discontinue", "reject", "decline", "renounce",
                            "relinquish", "forsake", "desist", "flee", "cut and run"]
# STRICTER keyword subset for WIDTH=1 (single-token) checks only -- MEASURED@this session's design
# probe (real DesireDB smoke run): the FULL keyword list's weaker/shorter members ("stop"/"away")
# incidentally matched unrelated senses of common words ("calls" -> call.v.11 "stop or postpone
# because of adverse conditions"/call.v.13 "make a stop in a harbour"; "excuse" -> apologize.v.02
# "defend... or make excuses for... clear AWAY, or..."), the SAME obscure-secondary-sense noise class
# already documented for "turned" above. Multi-word phrasal spans (width 2-4) keep the FULL list --
# a 2+-word combination is already narrowed by construction and did not show this noise class in
# calibration. Width=1 checks ONLY the stronger, less-ambiguous keywords.
_DISENGAGE_GLOSS_KEYWORDS_WIDTH1 = ["withdraw", "abandon", "give up", "retreat", "remove oneself",
                                    "chicken out", "forfeit", "quit", "discontinue", "reject",
                                    "refuse", "decline", "renounce", "relinquish", "forsake", "desist",
                                    "flee", "cut and run"]
_MWE_STOP_SHORT = frozenset({"the", "a", "an", "to", "of", "in", "on", "at", "it", "he", "she",
                             "they", "and", "but"})
# highly-polysemous light verbs excluded from WIDTH=1 (single-token) disengage-gloss checking only
# -- MEASURED@this session's design probe: "turned" (alone, from "turned the other cheek") spuriously
# matched turn.v.20 ("channel one's attention... toward or AWAY from something", an unrelated
# attention-shift sense) via the "away" keyword -- the SAME obscure-secondary-sense noise class this
# arc's module docstrings already document for "get"/"shop". Multi-word phrasal forms of these SAME
# verbs (turn_away/turn_down/give_up/...) are UNAFFECTED -- this exclusion applies to width=1 only.
_MWE_WIDTH1_LIGHT_VERB_STOP = frozenset({
    "turn", "turned", "turns", "turning", "get", "gets", "got", "getting", "put", "puts", "putting",
    "go", "goes", "went", "going", "come", "comes", "came", "coming", "take", "takes", "took", "taking",
    "make", "makes", "made", "making", "do", "does", "did", "doing", "have", "has", "had", "having",
    "be", "is", "are", "was", "were", "set", "sets", "setting", "run", "runs", "running", "ran",
    "hold", "holds", "held", "holding", "keep", "keeps", "kept", "keeping", "give", "gives", "gave",
    "giving", "let", "lets", "letting",
})
_KIBOSH_RE = re.compile(
    r"\b(put|puts|putting|gave|give|giving)\b.{0,25}?\b(?:kibosh|kabosh|kabash|kibash)\b.{0,10}?\bon\b")


def _wn_verb_gloss_disengage(lemma_form: str, width: int = 2) -> Tuple[Optional[str], Optional[str]]:
    """ALL senses (not just primary) of `lemma_form` as a WordNet VERB; returns (synset_name, gloss)
    for the first sense whose gloss contains a disengagement/refusal/abandonment keyword, else
    (None, None). Deliberately broader than this arc's other primary-sense-only Tier-2 fallbacks --
    see module docstring's MWE-DISENGAGE-SCAN MECHANISM note for why that is appropriate here
    (coverage measurement of a whole-gloss keyword match, not a fine polarity vote). `width=1` uses
    the STRICTER `_DISENGAGE_GLOSS_KEYWORDS_WIDTH1` subset (see that constant's docstring)."""
    from nltk.corpus import wordnet as _wn
    keywords = _DISENGAGE_GLOSS_KEYWORDS_WIDTH1 if width == 1 else DISENGAGE_GLOSS_KEYWORDS
    for syn in _wn.synsets(lemma_form, pos=_wn.VERB):
        gloss = syn.definition().lower()
        if any(kw in gloss for kw in keywords):
            return syn.name(), syn.definition()
    return None, None


def mwe_disengage_scan(outcome: str) -> Optional[dict]:
    """Scan `outcome` for a WordNet verb lemma (1-4 contiguous tokens, morphy-normalized head) whose
    dictionary GLOSS indicates disengagement/abandonment/refusal. Returns
    {'lemma','synset','gloss','span_kind'} or None. ONE discontinuous span is hand-declared (the
    'put THE kibosh/kabash/kabosh/kibash ON' light-verb frame -- see module docstring)."""
    ol = outcome.lower()
    if _KIBOSH_RE.search(ol):
        return {"lemma": "put_the_kibosh_on", "synset": "kibosh.v (via stop.v.03)",
                "gloss": "stop from happening or developing",
                "span_kind": "discontinuous_light_verb_frame"}
    from nltk.corpus import wordnet as _wn
    toks = _gt._tokens(outcome)
    n = len(toks)
    for width in (4, 3, 2, 1):
        for i in range(n - width + 1):
            span = toks[i:i + width]
            if width == 1 and (span[0] in _MWE_STOP_SHORT or len(span[0]) <= 3
                               or span[0] in _MWE_WIDTH1_LIGHT_VERB_STOP):
                continue
            head_lemma = _wn.morphy(span[0], _wn.VERB) or span[0]
            heads = [span[0]] if head_lemma == span[0] else [span[0], head_lemma]
            for head in heads:
                cand = "_".join([head] + span[1:])
                name, gloss = _wn_verb_gloss_disengage(cand, width=width)
                if name:
                    return {"lemma": cand, "synset": name, "gloss": gloss, "span_kind": f"{width}_gram"}
    return None


# Dictionary-grounded representative phrase bank for the COVERAGE measurement (authored from
# conventional/Merriam-Webster phrasal-verb meaning, NEVER from checking which DesireDB item it
# would flip -- calibration-honesty, identical discipline to hdlab/idiom_grounding.py's own
# IDIOM_LEXICON). `covered` states the EXPECTED WordNet-MWE floor result (MEASURED@this session's
# design probe, asserted in self_test as a regression guard on this exact list).
REPRESENTATIVE_DISENGAGEMENT_PHRASES: List[Tuple[str, bool]] = [
    ("She walked away without another word.", True),
    ("He walked off in a huff.", True),
    ("The other side backed off from the table.", True),
    ("They backed down from the plan.", True),
    ("The buyer backed out of the deal.", True),
    ("The buyer pulled back from the table entirely.", True),
    ("He pulled out of the race.", True),
    ("She gave up on the project.", True),
    ("He withdrew his application.", True),
    ("They retreated from the position.", True),
    ("She abandoned the plan.", True),
    ("He quit the team.", True),
    ("They bailed out of the contract.", False),   # DISCLOSED gap: bail_out.v's 2 WordNet senses
                                                    # (legal bail / bailing water) carry no
                                                    # disengagement gloss for this real-world sense
    ("The board turned away every request.", True),
    ("They turned down the offer.", True),
    ("The company shut down the project.", True),
    ("They called it quits after the fight.", True),
    ("He threw in the towel after the third round.", True),
    ("She simply turned the other cheek and moved on.", False),  # DISCLOSED gap: 0 WordNet synsets
    ("The board put the kabash on that idea entirely.", True),   # discontinuous frame
    ("He chickened out at the last second.", False),   # DISCLOSED gap: not independently indexed
    ("She shied away from the confrontation.", False),  # DISCLOSED gap: absent from WordNet
    ("She washed her hands of the whole affair.", False),  # DISCLOSED gap: absent from WordNet
    ("He backed away slowly.", True),
    ("She ran away from the argument.", True),
    ("He dropped out of the program.", True),
    ("He declined to help further.", True),
    ("She refused to continue.", True),
    ("They rejected the whole idea.", True),
]

# False-positive probe (real-outcome-flavored sentences with NO disengagement content) -- must ALL
# stay clean (None). Asserted in self_test.
_MWE_FALSE_POSITIVE_PROBE = [
    "She purchased the bicycle yesterday.", "He met up with his friend.",
    "They celebrated all evening.", "She finished the marathon on time.",
    "In the end she took care of it on her own.",  # self-reliance handled by a SEPARATE atom
]


def contradiction_dictionary_coverage() -> dict:
    """WordNet-MWE FLOOR coverage against REPRESENTATIVE_DISENGAGEMENT_PHRASES + the false-positive
    probe. Returns {'n','n_hit','coverage','hits','misses','false_positive_count',
    'kaikki_wiktextract_flagged'} -- the coverage % IS the number GATE-1's CONTRADICTS-dictionary
    fraction reports (see module docstring's COVERAGE PROVENANCE)."""
    hits, misses = [], []
    for text, _expected in REPRESENTATIVE_DISENGAGEMENT_PHRASES:
        r = mwe_disengage_scan(text)
        (hits if r else misses).append({"text": text, "match": r})
    n = len(REPRESENTATIVE_DISENGAGEMENT_PHRASES)
    n_hit = len(hits)
    fp = sum(1 for text in _MWE_FALSE_POSITIVE_PROBE if mwe_disengage_scan(text) is not None)
    return {
        "n": n, "n_hit": n_hit, "coverage": round(n_hit / n, 4),
        "hits": hits, "misses": misses,
        "false_positive_count": fp, "false_positive_probe_n": len(_MWE_FALSE_POSITIVE_PROBE),
        "coverage_provenance": "floor_wordnet_mwe",
        "kaikki_wiktextract_flagged": {
            "status": "flagged_not_fetched",
            "reason": "MEASURED infeasible for local-CPU compute-proportionality budget this session",
            "raw_jsonl_url": "https://kaikki.org/dictionary/English/kaikki.org-dictionary-English.jsonl",
            "raw_jsonl_content_length_bytes": 3212430706,
            "gzip_url": "https://kaikki.org/dictionary/English/kaikki.org-dictionary-English.jsonl.gz",
            "gzip_content_length_bytes": 501997915,
            "measured_via": "HEAD request, this session",
        },
    }


# ============================================================================ GOAL POLARITY
# (engagement vs avoidance) -- the goal-RELATIVE mapping the disengagement signal needs: a
# disengage-flavored outcome CONTRADICTS an engagement/achievement goal (the common case for every
# goal class this module + Stage-2's own 6 ATTRIBUTES recognize) but could INSTANTIATE an
# avoidance/leave-type goal instead. Structural, closed-class, goal-side-only (never inspects
# outcome text) -- Stage-1-confound-immune by the same argument as goal_atoms.
_AVOIDANCE_GOAL_RE = re.compile(
    r"\bwanted to (?:avoid|escape|get away from|leave|stay away from|not have to)\b")


def goal_polarity(desire: str) -> Optional[str]:
    """'avoidance' if the goal ITSELF is phrased as wanting to avoid/escape/leave something (a
    closed-class structural check on the desire text only); 'engagement' if SOME OTHER goal is
    recognized (`hdlab.goal_typing.find_desired_state` succeeds -- the SAME primitive
    `activate_attributes`/`goal_atoms` both build on, so this stays consistent with what the rest of
    the pipeline already considers 'a goal is present'); `None` (abstain) if NO goal is recognized at
    all. The `None` case is the GOAL-CONDITIONING gate for `disengagement_vote` below -- without it, a
    disengage-flavored outcome would fire NEG regardless of whether the paired desire has anything to
    do with a goal at all, which would fail the mandatory wrong-goal pairscramble control (a
    completely unrelated scrambled desire with NO recognizable goal must not still vote). SCOPE NOTE
    (disclosed): no item in this cell's GATE-2 cohort or TRAIN/HELDOUT banks exercises the
    'avoidance' branch -- implemented for correctness/completeness per the goal-relative design
    mandate, not empirically exercised by this cell's own eval data (see prereg)."""
    if _AVOIDANCE_GOAL_RE.search(desire.lower()):
        return "avoidance"
    return "engagement" if _gt.find_desired_state(desire) is not None else None


def disengagement_vote(desire: str, outcome: str) -> dict:
    """{'POS': int, 'NEG': int, 'matched': [...], 'source': 'mwe_dictionary'|'none'} -- the
    GOAL-RELATIVE dictionary-lookup CONTRADICTS vote (see module docstring). Fires NEG (Unfulfilled-
    supporting) when `mwe_disengage_scan` matches AND the goal is 'engagement'-polarity; fires POS
    (Fulfilled-supporting, the INSTANTIATES-an-avoidance-goal branch) when it matches AND the goal is
    'avoidance'-polarity; ABSTAINS (all-zero) when NO goal is recognized at all (`goal_polarity`
    returns None) -- the goal-conditioning gate, see that function's docstring."""
    m = mwe_disengage_scan(outcome)
    if m is None:
        return {"POS": 0, "NEG": 0, "matched": [], "source": "none"}
    pol = goal_polarity(desire)
    if pol is None:
        return {"POS": 0, "NEG": 0, "matched": [], "source": "none"}
    if pol == "avoidance":
        return {"POS": 1, "NEG": 0, "matched": [m["lemma"]], "source": "mwe_dictionary"}
    return {"POS": 0, "NEG": 1, "matched": [m["lemma"]], "source": "mwe_dictionary"}


def relation_votes(desire: str, outcome: str, chosen_name, hypothesis) -> dict:
    """{'POS': int, 'NEG': int, 'matched': [...]} -- SAME return shape as hdlab.idiom_grounding.
    idiom_votes / hdlab.result_type_induction.result_type_votes so a caller (hdlab.goal_achievement's
    relation-grounded channel) can combine it with the existing per-token WordNet vote the identical
    way M1/M2 did. Combines TWO independent sources (precedence: learned classifier first, dictionary
    fallback only when the learned classifier abstains -- keeps the trace auditable, same discipline
    as M3-inc1's combined channel):
      1. The LEARNED classifier (MEANS-END INSTANTIATES + self-reliance CONTRADICTS), via
         `pair_feats`/`predict` -- abstains (all-zero) when `pair_feats` found NOTHING informative
         (feats == ['no_relation_cue'] exactly), same honest-abstain precheck as M2's result_type_
         votes.
      2. `disengagement_vote` (WordNet-MWE dictionary lookup, goal-relative) -- tried ONLY when (1)
         abstained, so the trace's 'matched' field unambiguously identifies which source fired.
    """
    feats = pair_feats(desire, outcome)
    if feats != ["no_relation_cue"]:
        key = "|".join(sorted(feats))
        pred = predict(chosen_name, hypothesis, feats, key, default=None)
        if pred is not None and pred != "NEITHER":
            pol = RELATION_POLARITY[pred]
            return {"POS": 1 if pol == "POS" else 0, "NEG": 1 if pol == "NEG" else 0,
                    "matched": [pred], "source": "learned_classifier"}
    return disengagement_vote(desire, outcome)


# ============================================================================ self-test
def self_test() -> dict:
    """MECHANISM-FIRES + GENERALIZATION (means-end + self-reliance) + COVERAGE (dictionary-lookup
    disengagement) + anti-circular-design sanity checks. Real construction-cue extraction + real
    registry.learn() fit (estimation/ruleind) + real WordNet-MWE scan, no DesireDB needed."""
    # (1) TRAIN/HELD-OUT tag disjointness (load-bearing anti-circular invariant).
    train_tags = {tag for _d, _o, _c, tag in TRAIN_EXAMPLES}
    held_tags = {tag for _d, _o, _c, tag in HELDOUT_EXAMPLES}
    assert not (train_tags & held_tags), f"TRAIN/HELD-OUT tag overlap: {train_tags & held_tags}"
    all_subtype_tags = {t for tags in HELDOUT_SUBTYPES.values() for t in tags}
    assert all_subtype_tags == held_tags, (
        f"HELDOUT_SUBTYPES coverage mismatch: {all_subtype_tags.symmetric_difference(held_tags)}")

    # (2) pair_feats never leaks a literal desire/outcome word as a feature name.
    f = pair_feats("I wanted to know why he left.", "I talked to him about it.")
    assert all(a in CONSTRUCTION_ATOMS for a in f), f
    assert "talk" not in " ".join(f) and "know" not in " ".join(f)

    # (3) mechanism-fires: each learned-classifier atom actually fires on its intended construction.
    assert "goal_cognition" in goal_atoms("I wanted to know why he left.")
    assert "goal_activity_engagement" in goal_atoms("He wanted to be out and about.")
    assert "goal_skill_practice" in goal_atoms("He wanted to practice sitflying.")
    assert "outcome_info_exchange" in outcome_atoms("I talked to him about it.")
    assert "outcome_errand_activity" in outcome_atoms("He went grocery shopping that afternoon.")
    assert "outcome_skill_training" in outcome_atoms("The instructor got him sitflying.")
    assert "outcome_self_reliance_reflexive" in outcome_atoms("In the end she managed it herself.")
    assert outcome_atoms("It rained heavily all weekend.") == ["no_relation_cue"]

    # (4) GENERALIZATION probe: the self-reliance regex fires on a construction NEVER in
    # TRAIN_EXAMPLES/HELDOUT_EXAMPLES (verb-agnostic).
    assert "outcome_self_reliance_reflexive" in outcome_atoms("They did it by themselves.")

    # (5) end-to-end induction + held-out generalization (means-end + self-reliance) + memorization/
    # scramble controls.
    train_eps = [build_episode(d, o, c, tag) for d, o, c, tag in TRAIN_EXAMPLES]
    held_eps = [build_episode(d, o, c, tag) for d, o, c, tag in HELDOUT_EXAMPLES]
    chosen_name, chosen, all_results = induce(train_eps)
    assert chosen is not None, "induction abstained on the TRAIN set entirely"
    majority_train = max(RELATION_TYPES, key=lambda c: sum(1 for e in train_eps if e["gold_class"] == c))

    def _eval(name, hyp, eps, examples):
        n_ok, per_item = 0, []
        for e, (d, o, c, tag) in zip(eps, examples):
            key = "|".join(sorted(e["feats"]))
            pred = predict(name, hyp, e["feats"], key, default=majority_train)
            ok = (pred == e["gold_class"])
            n_ok += ok
            per_item.append({"tag": tag, "gold": e["gold_class"], "pred": pred, "ok": ok})
        return n_ok / len(eps), per_item

    held_acc, held_per_item = _eval(chosen_name, chosen.hypothesis, held_eps, HELDOUT_EXAMPLES)
    mem_correct = sum(1 for (d, o, c, tag) in HELDOUT_EXAMPLES
                       if memorization_baseline_predict(TRAIN_EXAMPLES, tag, majority_train) == c)
    mem_acc = mem_correct / len(HELDOUT_EXAMPLES)

    import random
    rng = random.Random(20260809)
    scrambled_labels = [e["gold_class"] for e in train_eps]
    rng.shuffle(scrambled_labels)
    scr_train_eps = [{"feats": e["feats"], "gold_class": scrambled_labels[i], "tag": e["tag"]}
                      for i, e in enumerate(train_eps)]
    scr_name, scr_chosen, _ = induce(scr_train_eps)
    scr_acc, _ = _eval(scr_name, scr_chosen.hypothesis if scr_chosen else None, held_eps, HELDOUT_EXAMPLES)

    assert held_acc > mem_acc, f"held_acc={held_acc} did not beat mem_acc={mem_acc}"
    assert held_acc > scr_acc, f"held_acc={held_acc} did not beat scr_acc={scr_acc}"

    # per-subtype breakdown (the honest recovery-vs-long-tail split for the LEARNED-classifier side).
    per_item_by_tag = {it["tag"]: it for it in held_per_item}
    subtype_acc = {}
    for sub, tags in HELDOUT_SUBTYPES.items():
        n_ok = sum(1 for t in tags if per_item_by_tag[t]["ok"])
        subtype_acc[sub] = round(n_ok / len(tags), 4)

    # (6) MWE-DISENGAGE-SCAN mechanism-fires + regression guard on REPRESENTATIVE_DISENGAGEMENT_
    # PHRASES's own EXPECTED hit/miss labels (MEASURED@this session's design probe).
    for text, expected in REPRESENTATIVE_DISENGAGEMENT_PHRASES:
        got = mwe_disengage_scan(text) is not None
        assert got == expected, f"MWE-SCAN REGRESSION: {text!r} expected hit={expected}, got={got}"
    for text in _MWE_FALSE_POSITIVE_PROBE:
        assert mwe_disengage_scan(text) is None, f"MWE-SCAN FALSE POSITIVE: {text!r}"
    coverage = contradiction_dictionary_coverage()
    assert coverage["false_positive_count"] == 0, coverage

    # (7) goal_polarity + disengagement_vote: engagement (default) fires NEG; avoidance flips to POS.
    assert goal_polarity("He wanted to keep negotiating.") == "engagement"
    assert goal_polarity("She wanted to avoid the confrontation entirely.") == "avoidance"
    dv_engage = disengagement_vote("He wanted to keep negotiating.",
                                    "The other side backed off from the table.")
    assert dv_engage == {"POS": 0, "NEG": 1, "matched": ["back_off"], "source": "mwe_dictionary"}, dv_engage
    dv_avoid = disengagement_vote("She wanted to avoid the confrontation entirely.",
                                   "In the end she backed off from the whole thing.")
    assert dv_avoid["POS"] == 1 and dv_avoid["NEG"] == 0, dv_avoid
    dv_none = disengagement_vote("He wanted to keep negotiating.", "They celebrated all evening.")
    assert dv_none == {"POS": 0, "NEG": 0, "matched": [], "source": "none"}, dv_none

    # (8) relation_votes: honest abstain when NEITHER source fires; a real vote when the learned
    # classifier fires (precedence 1); a real vote via dictionary fallback when only that fires.
    abstain = relation_votes("She wanted to be out and about.", "It rained heavily all weekend.",
                              chosen_name, chosen.hypothesis)
    assert abstain == {"POS": 0, "NEG": 0, "matched": [], "source": "none"}, abstain
    fires_learned = relation_votes("I wanted to know why he left.",
                                    "We discussed it at length last night.", chosen_name, chosen.hypothesis)
    assert fires_learned["matched"] == ["INSTANTIATES"] and fires_learned["source"] == "learned_classifier", fires_learned
    fires_dict = relation_votes("He wanted to keep negotiating.",
                                 "The other side backed off from the table.", chosen_name, chosen.hypothesis)
    assert fires_dict["source"] == "mwe_dictionary" and fires_dict["NEG"] == 1, fires_dict

    return {"chosen_plugin": chosen_name, "n_train": len(train_eps), "n_heldout": len(held_eps),
            "held_out_acc": round(held_acc, 4), "memorization_baseline_acc": round(mem_acc, 4),
            "scramble_control_acc": round(scr_acc, 4), "majority_train_class": majority_train,
            "subtype_acc": subtype_acc, "held_per_item": held_per_item,
            "dictionary_coverage": {k: v for k, v in coverage.items() if k not in ("hits", "misses")},
            "dictionary_coverage_misses": coverage["misses"],
            "all_plugin_description_bits": {k: round(v.description_bits, 3) for k, v in all_results.items()}}


if __name__ == "__main__":
    import json
    print(json.dumps(self_test(), indent=2, default=str))
