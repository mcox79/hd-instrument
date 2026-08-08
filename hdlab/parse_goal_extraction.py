"""hdlab/parse_goal_extraction.py -- parse-structure GOAL-referent extraction organ (promotion,
2026-08-08, wire-don't-island).

PROMOTION: lifts (verbatim structural logic, cleaned to a production wire-point) the parse-structure
goal extractor validated this session in a scratchpad build-1 script ("BUILD 1 -- phrasing-gap fix
for hdlab.goal_typing.find_desired_state, test-first, REUSE owned organs"). That script HARD-PASSED
component 1 + component 3 of its own pre-registered gate (component 2, STRICT-ADD sanity, PARTIAL at
3/6 -- diagnosed as EXACTLY the missing SUBJECT_IS_REFERENT_CLASSES fix this module applies; see
below): parse-extraction recall = 17/18 = 0.944 on a fresh 18-item bank of nominal/categorical-request,
ditransitive, passive, coordination, relative-clause, and PP-distractor request phrasings, vs
hdlab.goal_typing.find_desired_state recall = 0/18 on the SAME bank (find_desired_state's coverage is
purpose-infinitival "X V-goal to VP" + dialogue-goal constructions; it has no NOMINAL-request-
complement pass at all -- "asked for a window seat" / "booked her an aisle seat" / "was requested for
Maria" are a genuine phrasing gap, not a construction find_desired_state was ever meant to cover, so
this module is a STRICT ADD, not a replacement). The MDL-induced nominal_request construction
(hdlab.learner ruleind plugin, single-feature rule on 'nominal_np_complement') is non-episodic,
compression_ratio=5.628 (null_bits=8.920, description_bits=1.585), and held out 9/9 on FIT
verbs={ask,request} / TEST verbs={book,reserve,order,require} (disjoint) -- the FIT/TEST split
confirms the pattern generalizes across the REQUEST_VERB_SEEDS class, not just the two FIT verbs;
that induction step itself is NOT wired here (validation evidence only -- the detector this module
exposes, parse_extract_goal, already IS the practical recognizer: non-None is the "fires" signal).

MECHANISM (glass-box, deterministic, no RNG): given a sentence, run the persisted UPOS-tagger + arc-
parser front end (hdlab.candidate_generator.CandidateGenerator, loaded from
data/frontend_assets/pos_tagger_ud_ewt_upos.json / arc_parser_hashed_ud_ewt.npz -- REUSED BY IMPORT,
never retrained here) to get a (verb_idx, nominal-argument_idx) candidate-pair set
(hdlab.candidate_generator.candidates_from_parse), then:
  PASS A -- NOMINAL-REQUEST: a REQUEST_VERB_SEEDS governing verb's own NOMINAL argument (NP-
    complement: "asked for [a window seat]", "booked her [an aisle seat]", passive "was requested
    [for Maria]" -> the promoted subject; relative-clause gap: "the seat that Maria requested").
    REQUEST_VERB_SEEDS is a small hand-authored closed SUPPLY set of governing-verb surface forms
    (same convention as hdlab.goal_typing.DESIDERATIVE_PASS -- membership only; every argument
    EXTRACTION is structural via the parse, not a positional cue-phrase pattern). Precision guards:
    control-site exclusion (_is_control_site, "ordered the WORKERS to leave" -> the ECM subject is
    not this construction's NP-complement), a coordination-direction + explicit-coordinator gate on
    candidate_generator's 'conj_obj' rule (_valid_conj_obj, blocks "window seat" noun-compound over-
    generation), voice-appropriate positional filtering (pre-verbal promoted-subject for PASSIVE,
    post-verbal object/oblique for ACTIVE -- a pre-verbal candidate in ACTIVE voice is the REQUESTER,
    never the goal-standard, and is excluded outright), and a relative-clause-gap fallback
    (governing verb itself is an acl:relcl dependent of a nominal antecedent).
  PASS B -- PURPOSE-INFINITIVAL: verb-lemma-independent "to VERB (NP)" (POS-structural, mirrors
    hdlab.goal_typing.action_frame_feats' verb-lemma-independent detection philosophy), covering the
    EXISTING desiderative-goal styles find_desired_state already handles ("wanted to fix the FENCE").
    SUBJECT_IS_REFERENT FIX (critical, see below): for an embedded verb in the ARRIVE_SUCCEED /
    FAIL_LOSE classes (win/lose/reach/escape/arrive/succeed/miss/fail), the referent is the SUBJECT
    of the governing clause, not the embedded verb's object.

SUBJECT_IS_REFERENT_CLASSES FIX (the load-bearing precision repair this module adds over a naive
lift): hdlab.goal_typing.find_desired_state's CONTROL branch (goal_typing.py
SUBJECT_IS_REFERENT_CLASSES / OBJECT_IS_REFERENT_CLASSES, ~line 714) distinguishes achievement verbs
(win/reach/... -- the SUBJECT changes state, "X longed to WIN the prize" means X becomes the winner,
not that the prize changes) from change-of-state transitives (mend/save/open/fill/... -- the OBJECT
changes state). A naive PASS-B lift that always takes the embedded verb's object regresses this: on
the scratchpad script's own STRICT-ADD sanity bank, "Beth hoped to win a place at the summer fair."
find_desired_state correctly returns "beth" (subject) while the naive object-only PASS B returned
"place" (object) -- a DISAGREE. This module closes that gap: _SUBJECT_REFERENT_LEMMAS is the lemma
UNION of goal_typing.CLASS_REGISTRY[c] for c in goal_typing.SUBJECT_IS_REFERENT_CLASSES, imported
directly (not hand-copied) so it can never drift out of sync with the production organ's own class
membership; when the PASS-B embedded verb lemmas into that set, parse_extract_goal reports the
governing clause's SUBJECT (via _find_subject_referent: primary = the arc-parser's own nsubj-style
dependent of the governing verb, i.e. the NOMINAL token whose parsed head IS the governing verb and
which precedes it; fallback = nearest preceding NOMINAL-POS token, for parser-noise robustness) —
tagged construction="PURPOSE_INF_SUBJECT" so the fix's firing is visible in the glass-box output.

STRICT-ADD COMPOSITION: find_desired_state_v2(sentence) = hdlab.goal_typing.find_desired_state(
sentence) or parse_extract_goal(sentence) -- byte-identical to find_desired_state whenever the
baseline fires (the parse-structure path is consulted ONLY when the baseline returns None), so every
existing coverage/recall/precision number hdlab.goal_typing.py reproduces is untouched.
hdlab/goal_typing.py itself is NOT edited by this promotion (not even a comment) -- this module is a
pure downstream ADD.

SCOPE (do not overclaim): validated on the 18-item hand-authored fresh bank above (families:
request_basic, ditransitive, passive, coordination, relative_clause, pp_distractor) plus a 2-item
bonus set (chained relative-clause, precision-control) and a 6-item desiderative STRICT-ADD sanity
bank -- not validated on open-domain text beyond those banks. Known residual: PASS A's relative-
clause-gap fallback mis-attaches on a chained relative clause ("The clerk canceled the seat that
Maria had requested." -> None; "The seat that Maria requested was near the window." -> "window" not
"seat") -- both are relative-clause parse-attachment residuals, consistent with the arc-parser's own
disk-verified UAS ~0.80 (relative clauses are exactly its weaker construction class), not a bug
specific to this extractor. REQUEST_VERB_SEEDS membership is a hand SUPPLY set (verb_lexical_
similarity's "outcome"/"goal" domains do not lexicalize the booking/ordering/reserving verb class --
all probed OOV/abstain), not an open-vocabulary classifier; extending it is a future TIER-2 follow-up,
same pattern hdlab.goal_typing already applies to other closed classes.

Cites: hdlab.candidate_generator (CandidateGenerator, candidates_from_parse, NOMINAL -- REUSED
UNMODIFIED); hdlab.pos_tagger.PosTagger / hdlab.arc_parser.ArcParser (persisted checkpoints, loaded
not retrained); hdlab.thematic_role_labeler.lemma_verb; hdlab.goal_typing (find_desired_state,
CLASS_REGISTRY, SUBJECT_IS_REFERENT_CLASSES -- consumed by IMPORT, never edited).
"""
from __future__ import annotations

import os
from typing import Dict, List, Optional, Sequence, Set, Tuple

from hdlab.candidate_generator import CandidateGenerator, NOMINAL
from hdlab.thematic_role_labeler import lemma_verb
from hdlab.goal_typing import (
    find_desired_state as _baseline_find_desired_state,
    CLASS_REGISTRY as _GOAL_CLASS_REGISTRY,
    SUBJECT_IS_REFERENT_CLASSES as _SUBJECT_IS_REFERENT_CLASSES,
)

# ============================================================================ persisted front end
_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
POS_CKPT = os.path.join(_REPO, "data", "frontend_assets", "pos_tagger_ud_ewt_upos.json")
ARC_CKPT = os.path.join(_REPO, "data", "frontend_assets", "arc_parser_hashed_ud_ewt.npz")

_GEN_CACHE: Optional[CandidateGenerator] = None


def _default_generator() -> CandidateGenerator:
    """Lazily load + cache the persisted UPOS-tagger/arc-parser CandidateGenerator (module-level
    singleton -- checkpoint load is the slow part of this organ; every call site shares one)."""
    global _GEN_CACHE
    if _GEN_CACHE is None:
        _GEN_CACHE = CandidateGenerator.load(POS_CKPT, ARC_CKPT)
    return _GEN_CACHE


# ============================================================================ SUPPLY sets
# Request/booking governing-verb SURFACE forms -- hand-authored closed SUPPLY set, same convention as
# hdlab.goal_typing.DESIDERATIVE_PASS (a supply set of surface forms, not an induced cue-phrase
# pattern; every argument EXTRACTION below is structural via the parse, only verb MEMBERSHIP is
# supplied). hdlab.verb_lexical_similarity's ("outcome","goal") domains do not lexicalize this
# booking/ordering/reserving verb class (all probed words OOV/abstain), so there is no open-vocab
# fallback for this set yet -- see module docstring SCOPE.
REQUEST_VERB_SEEDS = {
    "ask", "asks", "asked", "asking",
    "request", "requests", "requested", "requesting",
    "order", "orders", "ordered", "ordering",
    "book", "books", "booked", "booking",
    "reserve", "reserves", "reserved", "reserving",
    "require", "requires", "required", "requiring",
    "demand", "demands", "demanded", "demanding",
}

_BE_FORMS = {"is", "are", "was", "were", "been", "being", "am", "be"}
_COORD_WORDS = {"and", "or"}
_RULE_PRIORITY = {"core_dep": 0, "relcl_gap": 1, "conj_obj": 3}  # 'coord' deliberately excluded, see below

# SUBJECT_IS_REFERENT fix: the SAME lemma set hdlab.goal_typing.find_desired_state's CONTROL branch
# gates on (ARRIVE_SUCCEED | FAIL_LOSE), reused BY IMPORT from CLASS_REGISTRY / SUBJECT_IS_REFERENT_
# CLASSES so this can never silently drift out of sync with the production organ's own class
# membership (a hand-copied win/lose list would).
_SUBJECT_REFERENT_LEMMAS = frozenset().union(
    *(_GOAL_CLASS_REGISTRY[c] for c in _SUBJECT_IS_REFERENT_CLASSES)
)


# ============================================================================ precision guards
def _is_passive_voice(v: int, lower: List[str], heads: Dict[int, int], pos: List[str]) -> bool:
    """True iff the token immediately preceding governing verb v (1-based) is a BE-form attached to v
    as its auxiliary (heads[p] == v) -- promotes v's PATIENT to the pre-verbal subject position."""
    p = v - 1
    if p < 1:
        return False
    return lower[p - 1] in _BE_FORMS and heads.get(p) == v


def _is_control_site(a: int, lower: List[str], pos: List[str], n: int) -> bool:
    """True iff the NOMINAL candidate at 1-based index a is immediately followed by 'to VERB' -- an
    ECM/object-control complement site ('ordered the WORKERS to leave'), not this construction's own
    NP-complement. a's own token is 1-based a; the following two tokens are 1-based a+1 ('to') and
    a+2 (the embedded verb), i.e. 0-based indices a and a+1."""
    i_to = a
    i_v = a + 1
    return i_to < n and lower[i_to] == "to" and i_v < n and pos[i_v] == "VERB"


def _valid_conj_obj(a: int, m: int, lower: List[str]) -> bool:
    """Precision guard for candidate_generator's 'conj_obj' (conjoined-object grandchild) rule, which
    over-generates on a plain NOUN-NOUN compound ('window seat': heads[window]=seat, heads[seat]=verb
    -> (verb,window) fires conj_obj even though 'window' is just seat's own compound modifier, not a
    coordinate object). A conj_obj candidate is only accepted when (a) it POSITIONALLY FOLLOWS its
    nominal parent m (true coordination lists the 2nd conjunct after the 1st: 'time AND budget'; a
    compound modifier PRECEDES its head: 'window SEAT') AND (b) an explicit coordinator token ('and'/
    'or') actually occurs between them (rules out a merely-intervening PP: 'discount ON the item')."""
    if a <= m:
        return False
    lo, hi = m, a - 1  # 1-based span (m, a) exclusive of both ends -> 0-based range(m, a-1)
    return any(lower[k] in _COORD_WORDS for k in range(lo, hi))


def _select_np_arg(v: int, lower: List[str], pos: List[str], heads: Dict[int, int],
                    pairs: Set[Tuple[int, int]], rules: Dict[Tuple[int, int], str], n: int,
                    passive: bool) -> Tuple[Optional[int], Optional[str]]:
    """Given a governing token v (1-based) and the candidate_generator pair/rule set, pick the single
    best NOMINAL argument: (1) filter to valid, non-control-site candidates; (2) restrict to the
    voice-appropriate side (post-verbal object/oblique for ACTIVE; pre-verbal promoted-subject for
    PASSIVE -- a pre-verbal candidate in ACTIVE voice is the REQUESTER, never the goal-standard, and is
    excluded outright, not merely deprioritized); (3) prefer core_dep > relcl_gap > conj_obj, then
    prefer a NOUN/PROPN over a bare PRON; (4) if nothing survives, fall back to the relative-clause
    GAP case (v itself is an acl:relcl dependent of a nominal antecedent: heads[v] == antecedent).
    Returns (idx, rule_tag) or (None, None)."""
    filtered = []
    for (vv, a) in pairs:
        if vv != v:
            continue
        rtag = rules.get((v, a))
        if rtag == "coord":
            continue  # verb-sharing 'coord' over-generates on ECM/object-control; excluded
        if not (1 <= a <= n and pos[a - 1] in NOMINAL):
            continue
        if rtag == "conj_obj":
            m = heads.get(a)
            if m is None or not _valid_conj_obj(a, m, lower):
                continue
        if _is_control_site(a, lower, pos, n):
            continue
        filtered.append((a, rtag))

    positional = [(a, r) for (a, r) in filtered if (a < v if passive else a > v)]
    if not positional:
        antecedent = heads.get(v)
        if antecedent and 1 <= antecedent <= n and pos[antecedent - 1] in NOMINAL:
            return antecedent, "relcl_gap_antecedent"
        return None, None

    positional.sort(key=lambda x: (_RULE_PRIORITY.get(x[1], 9), x[0]))
    non_pron = [(a, r) for (a, r) in positional if pos[a - 1] != "PRON"]
    return (non_pron[0] if non_pron else positional[0])


def _find_subject_referent(gov0: int, lower: List[str], pos: List[str], heads: Dict[int, int],
                            n: int) -> Tuple[Optional[int], Optional[str]]:
    """Structural SUBJECT of the governing token at 0-based index gov0 (the token immediately before
    the purpose-infinitival 'to' -- the SUBJECT_IS_REFERENT_CLASSES branch's target). Primary: the
    NOMINAL dependent whose arc-parser head IS the governing verb (nsubj-style), positionally closest
    among those preceding it -- mirrors the arc-parser's own structure rather than a positional
    heuristic. Fallback: nearest preceding NOMINAL-POS token (parser-noise robustness, same spirit as
    hdlab.goal_typing.find_desired_state's positional _np_last_content(toks[:dv_idx]), but POS-
    informed so it cannot grab a determiner). Returns (idx_1based, tag) or (None, None)."""
    if gov0 < 0:
        return None, None
    gov1 = gov0 + 1
    deps = [a for a in range(1, gov1) if heads.get(a) == gov1 and pos[a - 1] in NOMINAL]
    if deps:
        return deps[-1], "subject_nsubj"
    for a in range(gov1 - 1, 0, -1):
        if pos[a - 1] in NOMINAL:
            return a, "subject_nearest_nominal"
    return None, None


# ============================================================================ public API
def parse_extract_goal(sentence: str, gen: Optional[CandidateGenerator] = None) -> Optional[dict]:
    """Locate the goal-standard / desired NP via PARSE STRUCTURE (arc_parser heads + candidate_
    generator's candidate pairs), not positional window-scanning.
    PASS A -- NOMINAL-REQUEST: a REQUEST_VERB_SEEDS governing verb's own NOMINAL argument (NP-
      complement: 'asked for [a window seat]', 'booked her [an aisle seat]', passive 'was requested
      [for Maria]' -> the promoted subject; relative-clause gap: 'the seat that Maria requested').
    PASS B -- PURPOSE-INFINITIVAL: verb-lemma-independent 'to VERB (NP)' (POS-structural), covering
      the existing desiderative-goal styles hdlab.goal_typing.find_desired_state already handles
      ('wanted to fix the FENCE' -> 'fence'). SUBJECT_IS_REFERENT FIX: when the embedded verb lemmas
      into _SUBJECT_REFERENT_LEMMAS (ARRIVE_SUCCEED | FAIL_LOSE -- win/lose/reach/escape/arrive/
      succeed/miss/fail), the referent is the governing clause's SUBJECT
      (construction='PURPOSE_INF_SUBJECT'), not the embedded verb's object.
    Returns {"referent": str, "idx": int, "verb_idx": int, "verb_lemma": str, "construction": str,
    "rule": str|None} or None."""
    gen = gen or _default_generator()
    cr = gen.generate(sentence)
    toks, pos, heads = cr.tokens, cr.pos, cr.heads
    n = len(toks)
    lower = [t.lower() for t in toks]
    pairs, rules = cr.candidates, cr.cand_rules  # already computed by gen.generate(extended=True)

    for v in range(1, n + 1):
        if pos[v - 1] != "VERB":
            continue
        if lower[v - 1] not in REQUEST_VERB_SEEDS:
            continue
        passive = _is_passive_voice(v, lower, heads, pos)
        chosen, rtag = _select_np_arg(v, lower, pos, heads, pairs, rules, n, passive)
        if chosen is None:
            continue
        return {"referent": lower[chosen - 1], "idx": chosen, "verb_idx": v,
                "verb_lemma": lemma_verb(lower[v - 1]),
                "construction": ("NOMINAL_REQUEST_PASSIVE" if passive else "NOMINAL_REQUEST"),
                "rule": rtag}

    for i in range(1, n):  # 0-based i: lower[i-1]=='to' (the infinitival marker), pos[i]=='VERB'
        if lower[i - 1] != "to" or pos[i] != "VERB":
            continue
        ev = i + 1  # 1-based index of the embedded verb
        embedded_lemma = lemma_verb(lower[ev - 1])

        if embedded_lemma in _SUBJECT_REFERENT_LEMMAS:
            gov0 = i - 2  # 0-based index of the token immediately preceding 'to'
            subj_idx, subj_tag = _find_subject_referent(gov0, lower, pos, heads, n)
            if subj_idx is not None:
                return {"referent": lower[subj_idx - 1], "idx": subj_idx, "verb_idx": ev,
                        "verb_lemma": embedded_lemma, "construction": "PURPOSE_INF_SUBJECT",
                        "rule": subj_tag}
            # no structural subject found (e.g. infinitival clause at sentence start) -- fall through
            # to the ordinary object-based extraction below as a safety net, does not suppress recall.

        chosen, rtag = _select_np_arg(ev, lower, pos, heads, pairs, rules, n, passive=False)
        if chosen is None:
            continue
        return {"referent": lower[chosen - 1], "idx": chosen, "verb_idx": ev,
                "verb_lemma": embedded_lemma, "construction": "PURPOSE_INF_OBJ", "rule": rtag}
    return None


def find_desired_state_v2(sentence: str, gen: Optional[CandidateGenerator] = None) -> Optional[dict]:
    """STRICT-ADD composition: hdlab.goal_typing.find_desired_state(sentence) if it fires (returned
    UNCHANGED, byte-identical passthrough -- find_desired_state itself is never edited or re-run
    differently), else parse_extract_goal(sentence) as a phrasing-gap fallback (only consulted when
    the baseline returns None). Every existing coverage/recall/precision number hdlab/goal_typing.py
    reproduces is therefore untouched by this module's existence."""
    baseline = _baseline_find_desired_state(sentence)
    if baseline is not None:
        return baseline
    return parse_extract_goal(sentence, gen=gen)
