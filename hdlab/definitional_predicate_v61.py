"""v6.1 predicate layer -- the five defects the director hand-scored out of the v6 sample.

WHAT THIS IS. `hdlab/definitional_extraction.py` v6 recovered the PREDICATE of a process
definition (VP1 `X is the process of V-ing Y`, VP2 `X is the process by which CLAUSE`,
VP4 `X occurs when CLAUSE`). The director blind-scored 50 of its 250 facts 35 MEANINGFUL /
7 RELATED / 8 NOISE and named five defect classes. This module is the FIX LAYER: it reuses the
v6 regexes and the v6 clause walk unchanged, and changes only how the TERM is bounded, when a
match is REFUSED, and which ARGUMENT is taken.

  D1 TERM TRUNCATION  `form`, `process`, `second-degree`, `termination` (x2, colliding).
       Fixed in ONE place: `definitional_extraction.build_term_explain` under
       TERM_POLICY_STRICT. Not re-fixed per pattern -- that is what made this recur.
  D2 NEGATION DROPPED  "does NOT volunteer" banked as `volunteer`: the stored fact asserted the
       opposite of the source. Negation in scope over the recovered predicate -> REFUSE. No
       NEGATED_* relation is invented: nothing downstream consumes one, so it would be an island.
  D3 WRONG ARGUMENT  trailing adjuncts, obliques, parentheticals and purpose clauses were being
       read as the core argument (`lactation -> nipple`, `diffusion -> region`,
       `termination -> uag`, `differentiation -> function`).
  D4 FIRES ON NON-DEFINITIONS  the predicate search escaped the trigger's own clause (a
       coordinated main verb, a deeply embedded relative clause) and a data-description
       sentence was read as a definition.
  D5 PASSIVE SLOT  on "the development ... IS DISTURBED" the surface subject is the PATIENT.

v6.2 (2026-08-13) -- the director blind-scored v6.1 at 40 MEANINGFUL / 2 RELATED / 8 NOISE. All 13
v6 defect rows were fixed, but the NOISE FLOOR DID NOT MOVE (16% in both). Six of the eight
remaining noise rows fall to two narrow rules; four fixes are added, each behind its own flag, all
OFF under POLICY_V61 so v6.1 stays exactly reproducible:

  D-A SLOT TYPE      nothing checked that a slot's filler had the slot's part of speech.
       `cellular respiration --PROCESS_PATIENT--> convert` (a verb form in a noun slot),
       `photosynthesis --PROCESS_ACTION--> like` (a preposition in a verb slot). On a mismatch
       the slot is REFUSED under cause SLOT_TYPE_MISMATCH -- never coerced, never substituted.
  D-B TERM SANITY    the v5/v6.1 boundary work overshot into OVER-taking: `pathway's`,
       `interesting example of ecosystem dynamics`, `tragic irish potato famine`. Fixed in the ONE
       centralized routine `definitional_extraction.build_term_explain`, not per pattern.
  D-C MAIN VERB      the predicate must be the main verb of the trigger's OWN clause: not the head
       noun of the clause-initial subject NP (`the pathway's END product inhibits` -> `end`), and
       not a postnominal participle (`the variety GROWN in Ireland BECAME` -> `grow`).
  D-D MAIN CLAUSE    the argument comes from the main clause ("linking new information YOU ARE
       TRYING to learn" -> `try`).

REFUSAL IS A FIRST-CLASS OUTPUT. Every refusal is returned with its reason and its sentence; a
lower fact count is an accepted outcome. Nothing here writes to any foundation path.
ASCII-only.
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field, replace
from typing import Dict, List, Optional, Tuple

from hdlab.closed_class_lexicon import is_closed_class
from hdlab.definitional_extraction import (
    TERM_POLICY_LEGACY,
    TERM_POLICY_STRICT,
    TERM_POLICY_STRICT_V62,
    PredicateFact,
    _ANAPHORIC_SUBJ,
    _AUX_HEAD,
    _AUX_SKIP,
    _BE_FORMS,
    _CONTENTLESS_VERB,
    _PRENOMINAL_LEFT,
    _RE_VP1,
    _RE_VP2,
    _RE_VP4,
    _TOKEN_RE,
    _complement_head,
    _is_nominal_or_unknown,
    _tokens,
    _vp1_verbs,
    _wn,
    build_term_explain,
    clause_main_verb,
    definiens_head,
    is_nominal_lemma,
    is_verbal_lemma,
    verb_lemma_of,
)
from hdlab.thematic_role_labeler import lemma_word as lemma_verb

PATTERNS_V61 = ("VP1_PROCESS_OF", "VP2_BY_WHICH", "VP4_OCCURS_WHEN")
# ENABLING_CONDITION_PATIENT is the D5 correction, not a new capability: it is the same slot the
# v6 code already emitted, carrying the role the surface actually licenses. It replaces
# ENABLING_CONDITION_AGENT on passives; no NEGATED_* / MODAL_* type is introduced anywhere.
RELATIONS_V61 = ("PROCESS_ACTION", "PROCESS_PATIENT", "ENABLING_CONDITION",
                 "ENABLING_CONDITION_AGENT", "ENABLING_CONDITION_PATIENT")


@dataclass(frozen=True)
class PredicatePolicy:
    """One flag per DEFECT, so each fix can be ablated on its own (one variable per defect)."""
    name: str = "V61_ALL"
    strict_term: bool = True             # D1
    negation_refusal: bool = True        # D2
    argument_selection: bool = True      # D3
    clause_confinement: bool = True      # D4
    passive_patient: bool = True         # D5
    # ---- v6.2 (2026-08-13), all OFF under POLICY_V61 so v6.1 stays exactly reproducible --------
    slot_typing: bool = False            # D-A  a slot's filler must have the slot's part of speech
    term_sanity_v62: bool = False        # D-B  possessive / discourse-frame / evaluative terms
    subject_np_confinement: bool = False  # D-C  the clause-initial determiner NP is the SUBJECT
    reduced_relative_general: bool = False   # D-C  any postnominal participle, not a curated list
    main_clause_argument: bool = False   # D-D  the argument comes from the MAIN clause only


POLICY_V61 = PredicatePolicy()
POLICY_V6_EQUIV = PredicatePolicy("V6_EQUIVALENT", False, False, False, False, False)
POLICY_V62 = PredicatePolicy("V62_ALL", True, True, True, True, True,
                             True, True, True, True, True)


@dataclass
class Refusal:
    pattern: str
    reason: str
    detail: str
    definiendum: str
    sentence: str

    def to_dict(self) -> dict:
        return {"pattern": self.pattern, "reason": self.reason, "detail": self.detail,
                "definiendum": self.definiendum, "sentence": self.sentence}


@dataclass
class V61Out:
    facts: List[PredicateFact] = field(default_factory=list)
    refusals: List[Refusal] = field(default_factory=list)
    notes: Counter = field(default_factory=Counter)


# --------------------------------------------------------------------------------------- D3
# A parenthetical is an EXAMPLE, never the core argument: "a nonsense codon (UAA, UAG, or UGA)"
# gave `uag`. Strip before any argument is selected.
_PAREN_RE = re.compile(r"\([^()]*\)|\[[^\]]*\]")
# Particles belong to the verb and are stepped over; TRUE PREPOSITIONS open an oblique and the
# argument slot REFUSES rather than taking the oblique's object ("travels FROM regions" -> the
# core argument is the subject `material`, not `region`).
_V61_PARTICLE = {"in", "out", "up", "down", "off", "away", "apart", "together", "back", "on",
                 "over", "forward", "aside", "along", "around"}
_V61_OBLIQUE_PREP = {"from", "to", "with", "at", "by", "of", "about", "between", "among",
                     "within", "toward", "towards", "into", "onto", "through", "across",
                     "against", "upon", "for", "under", "during", "after", "before", "beyond",
                     "throughout", "per", "via"}

# --------------------------------------------------------------------------------------- D4
# The predicate lives in the TRIGGER'S OWN CLAUSE. A comma+coordinator opens a new main clause
# ("...old, AND THEN INCREASED even more" -- outside the when-clause), and a relativizer opens an
# embedded one ("the function of a gene THAT PRECEDES" -- two levels down).
_CLAUSE_BREAK_RE = re.compile(
    r",\s*(?:and|or|but|then|while|whereas|although|though|yet|so|since|because|however|"
    r"which|who)\b", re.IGNORECASE)
_EMBEDDED_CLAUSE_RE = re.compile(r"\s(?:that|which|who|whom|whose)\s", re.IGNORECASE)
_PURPOSE_MARK_RE = re.compile(r"\s(?:in\s+order\s+to|so\s+as\s+to|so\s+that)\s", re.IGNORECASE)
# A sentence that is DESCRIBING A FIGURE / TABLE / DATA COLUMN is reporting an observation, not
# defining a term ("As can be seen from the mortality rate data (column D), a high death rate
# occurred when ..."). Cheap, and only consulted on the text BEFORE the match.
_NONDEF_PHRASE = ("as can be seen", "as shown", "as seen", "as illustrated", "as depicted",
                  "as we can see", "note that", "notice that", "in this example",
                  "in the example above")
_NONDEF_WORD_RE = re.compile(r"\b(?:figure|table|column|graph|chart|axis|dataset)\b",
                             re.IGNORECASE)
# A REDUCED RELATIVE is a relative clause with its relativizer and copula elided: "an enzyme
# CALLED phosphodiesterase converts cAMP" -- `called` is a postnominal modifier, `converts` is
# the clause's verb. v6 banked `termination -> call`. The inventory is the participle members of
# the module's own `_NP_BOUNDARY` (already curated as "can only follow the head noun"), NOT a new
# guess, and the skip only takes effect if a LATER verb is actually found -- so a plain past-tense
# main verb ("when the sheep died") is left alone.
_REDUCED_REL_PARTICIPLE = {"called", "known", "termed", "named", "referred", "used", "found",
                           "made", "located", "produced", "involved", "formed", "composed",
                           "derived", "attached", "surrounded", "given", "taken", "seen",
                           "shown", "based", "related", "released", "carried", "labeled",
                           "labelled", "designated", "classified"}

# --------------------------------------------------------------------------------------- D2
_NEG_TOKEN = {"not", "never", "neither", "nor", "no", "none", "nothing", "cannot", "without",
              "rather", "instead", "unable", "lack", "lacks", "lacking", "absent", "absence",
              "fail", "fails", "failed", "failing", "seldom", "rarely", "hardly", "barely",
              "except", "unless", "non"}


# =============================================================================== v6.2 (D-A..D-D)
# THE TAGGER. There is exactly one part-of-speech oracle in this module family and v6.2 does not
# add a second: WordNet, reached through the functions this file already imports -- `verb_lemma_of`
# (wn.morphy(t,'v')), `is_verbal_lemma` (wn.synsets(l,'v')), `is_nominal_lemma`, and `_wn()` for
# the two SURFACE tests below. No nltk POS tagger, no hdlab.pos_tagger model, nothing trained.
#
# Why SURFACE and not LEMMA. The director's slot-type rule ("a verb slot needs a verb, a noun slot
# needs a noun") cannot be enforced on the LEMMA: `convert` and `salt` are both nouns AND verbs in
# WordNet, so a lemma-level test passes both defects it was written to catch. What separates them
# is the SURFACE FORM in context -- `converted` has no noun reading at all, `salts` has one. The
# two predicates below are therefore about the token as it stands in the sentence.
_SLOT_NOUN = ("PROCESS_PATIENT", "ENABLING_CONDITION_AGENT", "ENABLING_CONDITION_PATIENT")
_SLOT_VERB = ("PROCESS_ACTION", "ENABLING_CONDITION")

# A bare (uninflected) token from the module's OWN curated preposition/particle inventories is a
# PREPOSITION in the verb slot, not a predicate: "photosynthetic organisms LIKE plants harvest ..."
# banked `photosynthesis --PROCESS_ACTION--> like`. Inflected forms (`liked`, `likes`) are real
# verbs and are untouched.
_PREP_IN_VERB_SLOT = _V61_OBLIQUE_PREP | _V61_PARTICLE | {
    "like", "unlike", "near", "past", "despite", "versus", "plus", "minus", "as", "than",
    "while", "although", "because", "since", "if", "when", "whereas", "unless", "according",
    "such", "except", "including", "regarding", "concerning",
}
# D-D: a bare subject pronoun or a finite auxiliary opens a CLAUSE. Anything from there rightwards
# is a different clause's material and cannot be this predicate's argument ("linking new
# information YOU ARE TRYING to learn" banked `elaborative rehearsal -> try`).
_EMBEDDED_SUBJ = {"i", "you", "he", "she", "it", "we", "they", "who", "whom", "whose",
                  "that", "which"}


def surface_noun_reading(tok: str) -> bool:
    """True iff the SURFACE token has a noun reading (itself, or as an inflected noun form)."""
    wn = _wn()
    if wn is None:
        return True
    t = tok.lower()
    if t.endswith("'s"):
        return False                     # a possessive is a modifier, not a bare noun
    base = wn.morphy(t, "n")
    if base and wn.synsets(base, "n"):
        return True
    return bool(wn.synsets(t, "n"))


def surface_verb_reading(tok: str) -> bool:
    """True iff the SURFACE token has a verb reading (itself, or as an inflected verb form)."""
    wn = _wn()
    if wn is None:
        return False
    t = tok.lower()
    base = wn.morphy(t, "v")
    if base and wn.synsets(base, "v"):
        return True
    return bool(wn.synsets(t, "v"))


def surface_unknown(tok: str) -> bool:
    """True iff WordNet has never heard of this token in any part of speech. Technical terms
    (`ATP`, `phosphodiesterase`, `codon`) live here and must be allowed through the noun slot."""
    wn = _wn()
    if wn is None:
        return True
    t = tok.lower()
    if wn.synsets(t):
        return False
    return not any(wn.morphy(t, p) for p in ("n", "v", "a", "r"))


def surface_is_nominal(tok: str) -> bool:
    return surface_noun_reading(tok) or surface_unknown(tok)


def surface_is_verb_form_only(tok: str) -> bool:
    """`converted`, `stored`, `inhibits`, `grown`: a verb reading and NO noun reading at all."""
    return surface_verb_reading(tok) and not surface_noun_reading(tok) and not surface_unknown(tok)


def surface_is_modifier_only(tok: str) -> bool:
    """`photosynthetic`, `tragic`: WordNet knows it only as an adjective/adverb."""
    wn = _wn()
    if wn is None:
        return False
    t = tok.lower()
    if surface_noun_reading(tok) or surface_verb_reading(tok):
        return False
    return bool(wn.synsets(t, "a") or wn.synsets(t, "s") or wn.synsets(t, "r"))


def slot_type_violation(slot: str, surfaces: List[str], filler: str) -> Optional[str]:
    """The SLOT_TYPE_MISMATCH cause, or None. `surfaces` are every surface token in the span that
    could have produced `filler`; the slot is refused only if ALL of them violate the type, so an
    ambiguous back-mapping costs a refusal only when there is no legal reading at all."""
    if filler.lower().endswith("'s"):
        return "POSSESSIVE_FRAGMENT_IN_" + ("VERB" if slot in _SLOT_VERB else "NOUN") + "_SLOT"
    if slot in _SLOT_VERB:
        if not is_verbal_lemma(filler):
            return "NOT_A_VERB_LEMMA"
        if surfaces and all(s.lower() in _PREP_IN_VERB_SLOT and s.lower() == filler.lower()
                            for s in surfaces):
            return "PREPOSITION_IN_VERB_SLOT"
        if surfaces and all(surface_noun_reading(s) and not surface_verb_reading(s)
                            for s in surfaces):
            return "NOUN_SURFACE_IN_VERB_SLOT"
        return None
    if slot in _SLOT_NOUN:
        if surfaces and all(s.lower().endswith("'s") for s in surfaces):
            return "POSSESSIVE_SURFACE_IN_NOUN_SLOT"
        if surfaces and all(surface_is_verb_form_only(s) for s in surfaces):
            return "VERB_FORM_IN_NOUN_SLOT"
        if not is_nominal_lemma(filler):
            return "NOT_A_NOUN_LEMMA"
        return None
    return None


def surfaces_for(span: str, filler: str) -> List[str]:
    """Every surface token of `span` that lemmatizes to `filler` under either normalizer. This is
    the back-map from the emitted lemma to the words it could have come from."""
    want = filler.lower()
    out: List[str] = []
    for m in _TOKEN_RE.finditer(span):
        t = m.group(0)
        if (t.lower() == want or lemma_verb(t).lower() == want
                or (verb_lemma_of(t) or "").lower() == want):
            out.append(t)
    return out


def in_clause_initial_det_np(tokens: List[str], i: int) -> bool:
    """Is tokens[i] INSIDE the clause-initial DETERMINER-headed NP (i.e. the subject)?

    D-C. `clause_main_verb`'s R0 treats exactly ONE token as the subject, so on a longer subject
    NP the walk starts inside it and a noun-and-verb-ambiguous head is read as the predicate:
      "the process by which the mineral SALTS and water are kept in balance" -> `salt`
      "occurs when the pathway's END product inhibits an upstream"           -> `end`
    The scan walks LEFT over NP-internal material only (nouns, adjectives, possessives, and the
    coordinator of an NP-internal conjunction) and answers True only if it reaches a determiner
    AT INDEX 0. A determiner found further right belongs to some inner NP -- typically a PP's
    ("some impulses FROM THE SA NODE reach ...") -- and licenses nothing."""
    if i <= 0 or not surface_noun_reading(tokens[i]):
        return False
    j = i - 1
    while j >= 0:
        t = tokens[j].lower()
        if t.endswith("'s"):
            j -= 1
            continue
        if t in _PRENOMINAL_LEFT:
            return j == 0
        if t in ("and", "or"):
            j -= 1
            continue
        if surface_is_verb_form_only(tokens[j]):
            return False
        if surface_is_nominal(tokens[j]) or surface_is_modifier_only(tokens[j]):
            j -= 1
            continue
        return False
    return False


def is_postnominal_participle(tokens: List[str], i: int) -> bool:
    """A REDUCED RELATIVE's participle, generalized past v6.1's curated word list. "the single
    variety GROWN in Ireland BECAME susceptible" -- `grown` modifies `variety`, it is not the
    clause's verb. Requirements: an INFLECTED non-`-ing`, non-`-s` verb form, with no noun reading
    of its own, sitting immediately after a nominal. The caller additionally requires that a LATER
    verb actually exists, which is what keeps a plain past-tense main verb ("when the sheep DIED")
    from being skipped."""
    if i <= 0:
        return False
    t = tokens[i]
    tl = t.lower()
    if tl.endswith("ing") or tl.endswith("s"):
        return False
    lem = verb_lemma_of(tl)
    if not lem or lem.lower() == tl or not is_verbal_lemma(lem):
        return False
    if surface_noun_reading(t):
        return False
    return surface_is_nominal(tokens[i - 1])


def coordinator_opens_new_clause(tokens: List[str], a: int, b: int) -> bool:
    """Between two candidate verbs, does a coordinator introduce a NEW subject ("and THE debris
    is removed")? Then the later verb belongs to that clause and this predicate keeps its own."""
    for k in range(a + 1, min(b, len(tokens) - 1)):
        if tokens[k].lower() in ("and", "or", "but") and tokens[k + 1].lower() in _PRENOMINAL_LEFT:
            return True
    return False


def cut_at_embedded_clause(span: str) -> Tuple[str, bool]:
    """D-D. Truncate an ARGUMENT span at the first embedded-clause opener (a bare subject pronoun
    or a finite auxiliary). "new information YOU ARE trying to learn" -> "new information"."""
    toks = [(m.group(0), m.start()) for m in _TOKEN_RE.finditer(span)]
    for k, (t, pos) in enumerate(toks):
        if k == 0:
            continue
        tl = t.lower()
        if tl in _EMBEDDED_SUBJ or tl in _AUX_HEAD:
            return span[:pos].strip(" ,;"), True
    return span, False


def strip_parentheticals(span: str) -> Tuple[str, bool]:
    out = _PAREN_RE.sub(" ", span)
    out = re.sub(r"\s{2,}", " ", out).strip(" ,;")
    return out, out != span.strip(" ,;")


def confine_to_clause(span: str) -> Tuple[str, bool]:
    """Truncate `span` at the first boundary that leaves the trigger's own clause."""
    cuts = []
    m = _CLAUSE_BREAK_RE.search(span)
    if m:
        cuts.append(m.start())
    m = _EMBEDDED_CLAUSE_RE.search(span)
    if m:
        cuts.append(m.start())
    m = _PURPOSE_MARK_RE.search(span)
    if m:
        cuts.append(m.start())
    if not cuts:
        return span, False
    cut = min(cuts)
    return span[:cut].strip(" ,;"), True


def cut_at_purpose_infinitive(span: str) -> Tuple[str, bool]:
    """"specialized TO CARRY OUT distinct functions" -- the purpose clause is not the argument."""
    for m in re.finditer(r"\bto\s+([A-Za-z][A-Za-z'\-]*)", span):
        w = m.group(1)
        lem = verb_lemma_of(w)
        if lem and is_verbal_lemma(lem) and w.lower() == lem.lower():
            return span[:m.start()].strip(" ,;"), True
    return span, False


def nondefinitional_context(sentence: str, match_start: int) -> Optional[str]:
    pre = sentence[:match_start].lower()
    for p in _NONDEF_PHRASE:
        if p in pre:
            return p
    m = _NONDEF_WORD_RE.search(pre)
    return m.group(0).lower() if m else None


def negation_in_scope(tokens: List[str], verb_idx: int) -> Optional[str]:
    """The negator that has scope over the recovered predicate, or None. Scope = anything to the
    LEFT of the verb inside its own clause. A negator to the RIGHT belongs to a later constituent
    ("one member benefits WITHOUT affecting the other" negates `affect`, not `benefit`)."""
    for i in range(0, max(0, verb_idx)):
        t = tokens[i].lower()
        if t in _NEG_TOKEN or t.endswith("n't"):
            return tokens[i]
    return None


def passive_at(tokens: List[str], verb_idx: int) -> Tuple[bool, int]:
    """(is a BE-passive, index of the BE auxiliary). Progressive `-ing` is not a passive."""
    if verb_idx <= 0 or tokens[verb_idx].lower().endswith("ing"):
        return False, -1
    j = verb_idx - 1
    while j >= 0 and tokens[j].lower() in _AUX_SKIP:
        if tokens[j].lower() in _BE_FORMS:
            return True, j
        j -= 1
    return False, -1


def _skip_candidate(tokens: List[str], g: int, policy: PredicatePolicy) -> Optional[str]:
    """Why tokens[g] cannot be this clause's predicate, or None if it can be."""
    if passive_at(tokens, g)[0]:
        return None                         # a real BE-passive is the clause's own verb
    if tokens[g].lower() in _REDUCED_REL_PARTICIPLE:
        return "D4_REDUCED_RELATIVE"                                   # v6.1, curated list
    if policy.reduced_relative_general and is_postnominal_participle(tokens, g):
        return "DC_REDUCED_RELATIVE_GENERAL"                           # v6.2 D-C
    if policy.subject_np_confinement and in_clause_initial_det_np(tokens, g):
        return "DC_SUBJECT_NP_NOUN"                                    # v6.2 D-C
    return None


def clause_verb(tokens: List[str], policy: PredicatePolicy) -> Optional[Tuple[int, str]]:
    """The v6 clause walk, plus D4's reduced-relative skip and (v6.2) D-C. Refusing stays legal.

    Every skip is CONDITIONAL ON A LATER VERB EXISTING: if the walk finds nothing beyond the
    candidate, the candidate stands. That is what stops "when THESE CELLS PRODUCE ATP" (`produce`
    is the verb, nothing follows) from being confused with "when the mineral SALTS and water ARE
    KEPT in balance" (`salts` is the subject head, `kept` follows)."""
    hit = clause_main_verb(tokens)
    if hit is None or not policy.clause_confinement:
        return hit
    v62 = policy.reduced_relative_general or policy.subject_np_confinement
    first = hit                             # the v6.1 answer; every v6.2 skip must beat it
    base = 0
    used_v62 = False
    for _ in range(4 if v62 else 3):
        idx, lem = hit
        g = base + idx
        why = _skip_candidate(tokens, g, policy)
        if why is None:
            break
        nxt = clause_main_verb(tokens[g:])
        if nxt is None:
            break                           # no later verb: leave the original alone
        if why.startswith("DC_"):
            used_v62 = True
        base, hit = g, nxt
    g_final, lem_final = base + hit[0], hit[1]
    if not used_v62:
        return g_final, lem_final
    # A v6.2 skip must be PAID FOR: the verb it lands on has to be a token with NO noun reading
    # at all (`inhibits`, `kept`, `became`, `converted`). Without this test the walk trades a real
    # verb for a worse one -- measured on the v6.1 sample, `attaches` was replaced by `still`
    # ("are still bound") and `breaks` by the particle `down`. Failing the test is not an error:
    # the v6.1 candidate simply stands.
    g0 = first[0]
    if (not surface_is_verb_form_only(tokens[g_final])
            or coordinator_opens_new_clause(tokens, g0, g_final)):
        return first
    return g_final, lem_final


def core_argument(span: str, policy: PredicatePolicy) -> Tuple[Optional[str], str]:
    """Head of the CORE argument in `span` (the text right of the verb), or (None, reason)."""
    if not policy.argument_selection:
        return _complement_head(span), "OK_V6_PATH"
    span, cut = cut_at_purpose_infinitive(span)
    if not span:
        return None, "D3_PATIENT_PURPOSE_ONLY"
    if policy.main_clause_argument:
        span, emb = cut_at_embedded_clause(span)
        if not span:
            return None, "DD_ARGUMENT_EMBEDDED_ONLY"
        cut = cut or emb
    toks = [(m.group(0), m.start()) for m in _TOKEN_RE.finditer(span)]
    k = 0
    while k < len(toks) and toks[k][0].lower() in _V61_PARTICLE:
        k += 1
    if k >= len(toks):
        return None, "D3_PATIENT_EMPTY"
    if toks[k][0].lower() in _V61_OBLIQUE_PREP:
        return None, "D3_PATIENT_OBLIQUE"
    head = definiens_head(span[toks[k][1]:])
    if head is None:
        return None, "D3_PATIENT_NO_NOMINAL"
    return head, "OK_PURPOSE_CUT" if cut else "OK"


def _term(dfd: str, sentence: str, anaphoric_gate: bool, policy: PredicatePolicy
          ) -> Tuple[Optional[Tuple[str, str]], str]:
    toks = _tokens(dfd)
    if not toks:
        return None, "TERM_NO_TOKENS"
    if anaphoric_gate and any(t.lower() in _ANAPHORIC_SUBJ for t in toks):
        return None, "TERM_ANAPHORIC_SUBJECT"
    dfd_lemma = lemma_verb(toks[-1])
    if is_closed_class(dfd_lemma) or not _is_nominal_or_unknown(dfd_lemma):
        return None, "TERM_NOT_NOMINAL"
    if policy.strict_term:
        pol = TERM_POLICY_STRICT_V62 if policy.term_sanity_v62 else TERM_POLICY_STRICT
    else:
        pol = TERM_POLICY_LEGACY
    built, reason = build_term_explain(dfd, sentence, pol)
    if built is None:
        return None, "D1_" + reason if reason == "BARE_CATEGORY_HEAD" else "TERM_" + reason
    return built, reason


def _prep_span(span: str, policy: PredicatePolicy, notes: Counter) -> str:
    """Parenthetical strip (D3) + clause confinement (D4), each behind its own flag."""
    if policy.argument_selection:
        span, stripped = strip_parentheticals(span)
        if stripped:
            notes["D3_PARENTHETICAL_STRIPPED"] += 1
    if policy.clause_confinement:
        span, cut = confine_to_clause(span)
        if cut:
            notes["D4_CLAUSE_TRUNCATED"] += 1
    return span


def extract_predicates_v61(sentence: str, policy: PredicatePolicy = POLICY_V61) -> V61Out:
    """All v6.1 predicate facts in ONE sentence, plus every refusal and why."""
    out = V61Out()
    if not sentence or len(sentence) < 12:
        return out

    def _refuse(pattern: str, reason: str, detail: str, dfd: str) -> None:
        out.refusals.append(Refusal(pattern, reason, detail, dfd, sentence))
        out.notes[reason] += 1

    def _emit(term: str, ttype: str, relation: str, filler: str, pattern: str, dfd: str,
              span: str, surfaces: List[str]) -> bool:
        """D-A: a slot is filled only if its filler carries the slot's part of speech. On a
        mismatch the slot is REFUSED -- never coerced, never substituted."""
        if policy.slot_typing:
            why = slot_type_violation(relation, surfaces, filler)
            if why:
                _refuse(pattern, "SLOT_TYPE_MISMATCH",
                        "%s|%s|%s|%s" % (relation, filler, why, ",".join(surfaces[:3])), dfd)
                out.notes["DA_" + why] += 1
                return False
        out.facts.append(PredicateFact(term, ttype, relation, filler, pattern, dfd, span,
                                       sentence))
        return True

    # ---------------------------------------------------------------- VP1  "the process of V-ing"
    for m in _RE_VP1.finditer(sentence):
        dfd = m.group("dfd").strip()
        if policy.clause_confinement:
            cue = nondefinitional_context(sentence, m.start())
            if cue:
                _refuse("VP1_PROCESS_OF", "D4_NON_DEFINITIONAL_CONTEXT", cue, dfd)
                continue
        built, treason = _term(dfd, sentence, False, policy)
        if built is None:
            _refuse("VP1_PROCESS_OF", treason, "", dfd)
            continue
        term, ttype = built
        if "COORD_RESTART" in treason:
            out.notes["D1_COORD_RESTART"] += 1
        if "OF_EXTENDED" in treason:
            out.notes["D1_OF_EXTENDED"] += 1
        rest_raw = m.group("rest")
        rest = _prep_span(rest_raw, policy, out.notes)
        verbs = _vp1_verbs(rest)
        if not verbs:
            _refuse("VP1_PROCESS_OF", "NO_VERB_IN_OWN_CLAUSE", rest[:80], dfd)
            continue
        for lem, off in verbs:
            vtoks = [t.group(0) for t in _TOKEN_RE.finditer(rest[:off])]
            if policy.negation_refusal:
                neg = negation_in_scope(vtoks + [lem], len(vtoks))
                if neg:
                    _refuse("VP1_PROCESS_OF", "D2_NEGATION_IN_SCOPE", neg, dfd)
                    continue
            if lem == term.lower():
                continue
            if not _emit(term, ttype, "PROCESS_ACTION", lem, "VP1_PROCESS_OF", dfd, rest,
                         surfaces_for(rest[:off], lem)):
                continue                    # the predicate itself failed: its argument is moot
            arg_span = rest[off:]
            pat, why = core_argument(arg_span, policy)
            if pat is None:
                if why.startswith("D3") or why.startswith("DD"):
                    _refuse("VP1_PROCESS_OF", why, arg_span[:80], dfd)
                continue
            if pat != lem and pat != term.lower():
                _emit(term, ttype, "PROCESS_PATIENT", pat, "VP1_PROCESS_OF", dfd, rest,
                      surfaces_for(arg_span, pat))

    # ---------------------------------------------------------------- VP2  "the process by which"
    for m in _RE_VP2.finditer(sentence):
        dfd = m.group("dfd").strip()
        if policy.clause_confinement:
            cue = nondefinitional_context(sentence, m.start())
            if cue:
                _refuse("VP2_BY_WHICH", "D4_NON_DEFINITIONAL_CONTEXT", cue, dfd)
                continue
        built, treason = _term(dfd, sentence, False, policy)
        if built is None:
            _refuse("VP2_BY_WHICH", treason, "", dfd)
            continue
        term, ttype = built
        if "COORD_RESTART" in treason:
            out.notes["D1_COORD_RESTART"] += 1
        if "OF_EXTENDED" in treason:
            out.notes["D1_OF_EXTENDED"] += 1
        clause = _prep_span(m.group("clause"), policy, out.notes)
        ctoks = [(t.group(0), t.start(), t.end()) for t in _TOKEN_RE.finditer(clause)]
        hit = clause_verb([t[0] for t in ctoks], policy)
        if hit is None:
            _refuse("VP2_BY_WHICH", "NO_VERB_IN_OWN_CLAUSE", clause[:80], dfd)
            continue
        idx, lem = hit
        if policy.negation_refusal:
            neg = negation_in_scope([t[0] for t in ctoks], idx)
            if neg:
                _refuse("VP2_BY_WHICH", "D2_NEGATION_IN_SCOPE", neg, dfd)
                continue
        if lem == term.lower():
            continue
        if not _emit(term, ttype, "PROCESS_ACTION", lem, "VP2_BY_WHICH", dfd, clause,
                     [ctoks[idx][0]]):
            continue
        is_pass, aux_i = passive_at([t[0] for t in ctoks], idx)
        if policy.passive_patient and is_pass:
            subj_span = clause[:ctoks[aux_i][1]]
            subj = definiens_head(subj_span)
            out.notes["D5_PASSIVE_SUBJECT_IS_PATIENT"] += 1
            if subj and subj != lem and subj != term.lower():
                _emit(term, ttype, "PROCESS_PATIENT", subj, "VP2_BY_WHICH", dfd, clause,
                      surfaces_for(subj_span, subj))
            continue
        arg_span = clause[ctoks[idx][2]:]
        pat, why = core_argument(arg_span, policy)
        if pat is None:
            if why.startswith("D3") or why.startswith("DD"):
                _refuse("VP2_BY_WHICH", why, arg_span[:80], dfd)
            continue
        if pat != lem and pat != term.lower():
            _emit(term, ttype, "PROCESS_PATIENT", pat, "VP2_BY_WHICH", dfd, clause,
                  surfaces_for(arg_span, pat))

    # ---------------------------------------------------------------- VP4  "occurs when CLAUSE"
    for m in _RE_VP4.finditer(sentence):
        dfd = m.group("dfd").strip()
        if policy.clause_confinement:
            cue = nondefinitional_context(sentence, m.start())
            if cue:
                _refuse("VP4_OCCURS_WHEN", "D4_NON_DEFINITIONAL_CONTEXT", cue, dfd)
                continue
        built, treason = _term(dfd, sentence, True, policy)
        if built is None:
            _refuse("VP4_OCCURS_WHEN", treason, "", dfd)
            continue
        term, ttype = built
        if "COORD_RESTART" in treason:
            out.notes["D1_COORD_RESTART"] += 1
        if "OF_EXTENDED" in treason:
            out.notes["D1_OF_EXTENDED"] += 1
        clause = _prep_span(m.group("clause"), policy, out.notes)
        ctoks = [(t.group(0), t.start(), t.end()) for t in _TOKEN_RE.finditer(clause)]
        hit = clause_verb([t[0] for t in ctoks], policy)
        if hit is None:
            _refuse("VP4_OCCURS_WHEN", "NO_VERB_IN_OWN_CLAUSE", clause[:80], dfd)
            continue
        idx, lem = hit
        if policy.negation_refusal:
            neg = negation_in_scope([t[0] for t in ctoks], idx)
            if neg:
                _refuse("VP4_OCCURS_WHEN", "D2_NEGATION_IN_SCOPE", neg, dfd)
                continue
        if lem == term.lower():
            continue
        if not _emit(term, ttype, "ENABLING_CONDITION", lem, "VP4_OCCURS_WHEN", dfd, clause,
                     [ctoks[idx][0]]):
            continue
        is_pass, aux_i = passive_at([t[0] for t in ctoks], idx)
        subj_end = ctoks[aux_i][1] if (is_pass and policy.passive_patient) else (
            ctoks[idx][1] if idx > 0 else 0)
        role = ("ENABLING_CONDITION_PATIENT" if (is_pass and policy.passive_patient)
                else "ENABLING_CONDITION_AGENT")
        if is_pass and policy.passive_patient:
            out.notes["D5_PASSIVE_SUBJECT_IS_PATIENT"] += 1
        subj_span = clause[:subj_end] if subj_end > 0 else ""
        subj = definiens_head(subj_span) if subj_span else None
        if subj and subj != lem and subj != term.lower():
            _emit(term, ttype, role, subj, "VP4_OCCURS_WHEN", dfd, clause,
                  surfaces_for(subj_span, subj))

    seen = set()
    uniq: List[PredicateFact] = []
    for p in out.facts:
        key = (p.term, p.relation, p.object)
        if key in seen:
            continue
        seen.add(key)
        uniq.append(p)
    out.facts = uniq
    return out


def extract_predicates_v62(sentence: str, policy: PredicatePolicy = POLICY_V62) -> V61Out:
    """v6.2 = v6.1 + D-A slot typing + D-B term sanity + D-C main-verb-of-the-clause + D-D
    main-clause argument. Same function, different policy: v6.1 stays exactly reproducible."""
    return extract_predicates_v61(sentence, policy)


def ablations(base: PredicatePolicy = POLICY_V61) -> Dict[str, PredicatePolicy]:
    """LEAVE-ONE-OUT: one policy per defect with exactly that defect's fix turned OFF."""
    return {
        "D1_strict_term_OFF": replace(base, name="D1_OFF", strict_term=False),
        "D2_negation_OFF": replace(base, name="D2_OFF", negation_refusal=False),
        "D3_argument_OFF": replace(base, name="D3_OFF", argument_selection=False),
        "D4_clause_OFF": replace(base, name="D4_OFF", clause_confinement=False),
        "D5_passive_OFF": replace(base, name="D5_OFF", passive_patient=False),
    }


def ablations_v62(base: PredicatePolicy = POLICY_V62) -> Dict[str, PredicatePolicy]:
    """The five v6.1 leave-one-out arms plus one per v6.2 defect: still ONE VARIABLE PER ARM."""
    out = dict(ablations(base))
    out["DA_slot_typing_OFF"] = replace(base, name="DA_OFF", slot_typing=False)
    out["DB_term_sanity_OFF"] = replace(base, name="DB_OFF", term_sanity_v62=False)
    out["DC_subject_np_OFF"] = replace(base, name="DC_SUBJ_OFF", subject_np_confinement=False)
    out["DC_reduced_rel_general_OFF"] = replace(base, name="DC_RR_OFF",
                                                reduced_relative_general=False)
    out["DD_main_clause_arg_OFF"] = replace(base, name="DD_OFF", main_clause_argument=False)
    out["ALL_V62_OFF_v61_equivalent"] = POLICY_V61
    return out


# -------------------------------------------------------------------------------------------
# Self-test (run: python -m hdlab.definitional_predicate_v61). Every case is a REAL corpus
# sentence from the v6 blind sample the director hand-scored, named by its sample row.
# -------------------------------------------------------------------------------------------

S07 = ("The bystander effect is a phenomenon in which a witness or bystander does not volunteer "
       "to help a victim or person in distress")
S06 = ("Often the biochemical basis of epistasis is a gene pathway in which the expression of "
       "one gene is dependent on the function of a gene that precedes or follows in the pathway")
S13 = ("Differentiation is the process by which unspecialized cells become specialized to carry "
       "out distinct functions")
S16 = ("Diffusion is a process in which material travels from regions of high concentration to "
       "low concentration until equilibrium is reached")
S21 = ("The other form of polyploidy occurs when individuals of two different species reproduce "
       "to form a viable offspring that we call an allopolyploid")
S23 = ("As can be seen from the mortality rate data (column D), a high death rate occurred when "
       "the sheep were between 6 and 12 months old, and then increased even more rapidly")
S25 = ("Lactation is the process by which milk is synthesized and secreted from the mammary "
       "glands of the postpartum female breast in response to an infant sucking at the nipple")
S30 = "Neurodevelopmental disorders occur when the development of the nervous system is disturbed"
S36 = ("The process begins when mesenchymal cells in the embryonic skeleton gather together and "
       "begin to differentiate into specialized cells (a)")
S41 = ("A second-degree or incomplete block occurs when some impulses from the SA node reach the "
       "AV node and continue, while others do not")
S44 = ("Termination of the signal occurs when an enzyme called phosphodiesterase converts cAMP "
       "into AMP")
S45 = ("Termination of translation occurs when a nonsense codon (UAA, UAG, or UGA) is "
       "encountered")


# ---- v6.2. Every case is a REAL corpus sentence from the v6.1 blind sample, named by its row.
V08 = ("In contrast, cellular respiration is the process in which the chemical energy stored in "
       "sugars is converted into ATP, a source of chemical energy that can be used by the rest "
       "of the cell")
V16 = ("Alternatively, elaborative rehearsal is the act of linking new information you are "
       "trying to learn to existing information that you already know")
V19 = ("Feedback inhibition occurs when the pathway's end product (here isoleucine) inhibits an "
       "upstream")
V27 = ("In 1993, an interesting example of ecosystem dynamics occurred when a rare lung disease "
       "struck inhabitants of the southwestern United States")
V32 = ("The solutes in body fluids are mainly mineral salts and sugars, and osmotic regulation "
       "is the process by which the mineral salts and water are kept in balance")
V34 = ("Photosynthesis is the primary pathway in which photosynthetic organisms like plants "
       "(planktonic algae perform the majority of global photosynthesis) harvest the sun's "
       "energy and convert it into carbohydrates")
V46 = ("The tragic Irish potato famine occurred when the single variety grown in Ireland became "
       "susceptible to a potato blight, wiping out the entire crop")
# The two rows a first cut of D-C BROKE, kept as permanent regression cases.
V11 = ("Cross-bridge formation occurs when the myosin head attaches to the actin while adenosine "
       "diphosphate (ADP) and inorganic phosphate (Pi) are still bound to myosin")
V14 = ("Dysfunction occurs when an internal mechanism breaks down and can no longer perform its "
       "normal function")
V22 = ("Because erythrocytes do not contain mitochondria, glycolysis is the sole method by which "
       "these cells produce ATP")


def _trip(sentence: str) -> set:
    return {(f.term, f.relation, f.object) for f in extract_predicates_v61(sentence).facts}


def _trip62(sentence: str) -> set:
    return {(f.term, f.relation, f.object) for f in extract_predicates_v62(sentence).facts}


def _causes62(sentence: str) -> set:
    return {r.reason for r in extract_predicates_v62(sentence).refusals}


def _self_test() -> None:
    # ---- D2: THE PERMANENT REGRESSION. Sample row [07] must yield NO positive `volunteer` fact.
    got = _trip(S07)
    assert not any(o == "volunteer" for _s, _r, o in got), got
    assert not any(s == "bystander effect" for s, _r, _o in got), got
    res = extract_predicates_v61(S07)
    assert any(r.reason == "D2_NEGATION_IN_SCOPE" for r in res.refusals), res.refusals
    # negation to the RIGHT of the verb does not negate it -- this fact must SURVIVE
    keep = _trip("Commensalism occurs when one member benefits without affecting the other")
    assert ("commensalism", "ENABLING_CONDITION", "benefit") in keep, keep
    # "fails to" is negation, not a control verb
    assert _trip("Nondisjunction occurs when sister chromatids fail to separate") == set()

    # ---- D1: bare category nouns refuse; coordination and of-postmodifiers keep their identity
    assert _trip(S21) == set(), _trip(S21)
    assert _trip(S36) == set(), _trip(S36)
    r36 = extract_predicates_v61(S36)
    assert any(r.reason == "D1_BARE_CATEGORY_HEAD" for r in r36.refusals), r36.refusals
    assert {s for s, _r, _o in _trip(S41)} == {"incomplete block"}, _trip(S41)
    s44, s45 = {s for s, _r, _o in _trip(S44)}, {s for s, _r, _o in _trip(S45)}
    assert s44 == {"termination of signal"}, s44
    assert s45 == {"termination of translation"}, s45
    assert not (s44 & s45), (s44, s45)             # the v6 collision is gone
    # a MODIFIED container noun is still a term (PROPER here, so it keeps its surface case --
    # this is sample row [01], unchanged from v6)
    assert {s for s, _r, _o in _trip(
        "The VBNC state occurs when prokaryotes respond to environmental stressors")} == {
        "VBNC state"}
    assert {s for s, _r, _o in _trip(
        "A sensory activation occurs when a physical stimulus is processed by a receptor")} == {
        "sensory activation"}

    # ---- D3: core argument of the MAIN predicate, never an adjunct/oblique/parenthetical/purpose
    assert not any(o == "nipple" for _s, _r, o in _trip(S25)), _trip(S25)
    assert ("lactation", "PROCESS_PATIENT", "milk") in _trip(S25), _trip(S25)
    assert not any(o == "region" for _s, _r, o in _trip(S16)), _trip(S16)
    assert not any(o == "function" for _s, _r, o in _trip(S13)), _trip(S13)
    assert ("differentiation", "PROCESS_ACTION", "become") in _trip(S13), _trip(S13)
    assert not any(o == "uag" for _s, _r, o in _trip(S45)), _trip(S45)
    assert ("termination of translation", "ENABLING_CONDITION_PATIENT", "codon") in _trip(S45)

    # ---- D4: the predicate stays inside the trigger's own clause; data descriptions refuse
    assert _trip(S23) == set(), _trip(S23)
    r23 = extract_predicates_v61(S23)
    assert any(r.reason == "D4_NON_DEFINITIONAL_CONTEXT" for r in r23.refusals), r23.refusals
    assert not any(o == "precede" for _s, _r, o in _trip(S06)), _trip(S06)
    # the coordinated main verb OUTSIDE the when-clause is not the predicate, but the one INSIDE
    # it still is
    assert ("incomplete block", "ENABLING_CONDITION", "reach") in _trip(S41), _trip(S41)
    # a REDUCED RELATIVE ("an enzyme CALLED phosphodiesterase CONVERTS ...") is a relative clause:
    # its participle is not the predicate. v6 banked `termination -> call`.
    t44 = _trip(S44)
    assert not any(o == "call" for _s, _r, o in t44), t44
    assert ("termination of signal", "ENABLING_CONDITION", "convert") in t44, t44
    # ...but a plain past-tense main verb with no later verb is left alone
    assert ("dysfunction", "ENABLING_CONDITION", "die") in _trip(
        "Dysfunction occurs when the cells died"), _trip("Dysfunction occurs when the cells died")

    # ---- D5: on a passive the surface subject is the PATIENT
    assert ("neurodevelopmental disorder", "ENABLING_CONDITION_PATIENT", "development") \
        in _trip(S30), _trip(S30)
    assert not any(r == "ENABLING_CONDITION_AGENT" for _s, r, _o in _trip(S30)), _trip(S30)
    # ACTIVE clauses keep the AGENT role
    act = _trip("Vascular shock occurs when arterioles lose their normal muscular tone")
    assert ("vascular shock", "ENABLING_CONDITION_AGENT", "arteriole") in act, act

    # ---- schema
    for s in (S13, S16, S25, S30, S41, S44, S45):
        for f in extract_predicates_v61(s).facts:
            assert f.relation in RELATIONS_V61, f
            assert f.pattern in PATTERNS_V61, f
    print("[definitional_predicate_v61] self-test PASS")


def _self_test_v62() -> None:
    """v6.2. TWO obligations: the eight hand-named noise rows must not recur, AND every v6.1
    assertion above must still hold when the v6.2 policy is the one running."""
    # ---- D-A SLOT TYPE ----------------------------------------------------------------------
    # [34] a PREPOSITION in the verb slot ("organisms LIKE plants"): REFUSE the whole match.
    assert _trip62(V34) == set(), _trip62(V34)
    assert "SLOT_TYPE_MISMATCH" in _causes62(V34), extract_predicates_v62(V34).refusals
    # [08] a VERB FORM in the patient slot (`stored` -> `store`): REFUSE the slot, do not coerce.
    t08 = _trip62(V08)
    assert not any(r == "PROCESS_PATIENT" for _s, r, _o in t08), t08
    assert "SLOT_TYPE_MISMATCH" in _causes62(V08), extract_predicates_v62(V08).refusals
    # ...and the ACTION on that same sentence is the reduced relative's HOST verb, not `store`.
    assert ("cellular respiration", "PROCESS_ACTION", "convert") in t08, t08
    # the slot-type gate is a REFUSAL, never a substitution: nothing new appears
    assert len(t08) == 1, t08

    # ---- D-B TERM SANITY (in the ONE centralized routine) -------------------------------------
    assert _trip62(V27) == set(), _trip62(V27)                 # [27] discourse frame
    assert "TERM_DISCOURSE_FRAME_TERM" in _causes62(V27), _causes62(V27)
    assert {s for s, _r, _o in _trip62(V46)} == {"irish potato famine"}, _trip62(V46)   # [46]
    assert build_term_explain("the pathway's end", "x the pathway's end y",
                              TERM_POLICY_STRICT_V62)[0] is None                        # [20]
    assert build_term_explain("an interesting example", "an interesting example of x",
                              TERM_POLICY_STRICT_V62)[1] in ("DISCOURSE_FRAME_TERM",)
    # LEGACY is untouched by all three rules -- this is what keeps the ISA patterns byte-identical
    assert build_term_explain("tragic Irish potato famine",
                              "The tragic Irish potato famine occurred",
                              TERM_POLICY_LEGACY)[0][0] == "tragic irish potato famine"

    # ---- D-C THE MAIN VERB OF THE TRIGGER'S OWN CLAUSE ----------------------------------------
    assert ("feedback inhibition", "ENABLING_CONDITION", "inhibit") in _trip62(V19), _trip62(V19)
    assert not any(o == "end" for _s, _r, o in _trip62(V19)), _trip62(V19)              # [19]
    assert not any(o.endswith("'s") for _s, _r, o in _trip62(V19)), _trip62(V19)        # [20]
    assert ("osmotic regulation", "PROCESS_ACTION", "keep") in _trip62(V32), _trip62(V32)  # [32]
    assert ("irish potato famine", "ENABLING_CONDITION", "become") in _trip62(V46), _trip62(V46)
    # ...and the skip is PAID FOR: where the later verb is weaker, the v6.1 answer STANDS.
    assert ("cross-bridge formation", "ENABLING_CONDITION", "attach") in _trip62(V11), _trip62(V11)
    assert ("dysfunction", "ENABLING_CONDITION", "break") in _trip62(V14), _trip62(V14)
    assert ("glycolysis", "PROCESS_ACTION", "produce") in _trip62(V22), _trip62(V22)
    assert ("incomplete block", "ENABLING_CONDITION", "reach") in _trip62(S41), _trip62(S41)

    # ---- D-D THE ARGUMENT COMES FROM THE MAIN CLAUSE ------------------------------------------
    assert ("elaborative rehearsal", "PROCESS_PATIENT", "information") in _trip62(V16), _trip62(V16)
    assert not any(o == "try" for _s, _r, o in _trip62(V16)), _trip62(V16)              # [16]

    # ---- NO REGRESSION: every v6.1 assertion, re-run under the v6.2 policy --------------------
    for s in (S06, S07, S21, S23, S36):
        assert _trip62(s) == set(), (s[:40], _trip62(s))
    assert ("differentiation", "PROCESS_ACTION", "become") in _trip62(S13), _trip62(S13)
    assert ("diffusion", "PROCESS_ACTION", "travel") in _trip62(S16), _trip62(S16)
    assert ("lactation", "PROCESS_PATIENT", "milk") in _trip62(S25), _trip62(S25)
    assert ("neurodevelopmental disorder", "ENABLING_CONDITION_PATIENT", "development") \
        in _trip62(S30), _trip62(S30)
    assert ("termination of signal", "ENABLING_CONDITION", "convert") in _trip62(S44), _trip62(S44)
    assert ("termination of translation", "ENABLING_CONDITION_PATIENT", "codon") in _trip62(S45)
    assert ("commensalism", "ENABLING_CONDITION", "benefit") in _trip62(
        "Commensalism occurs when one member benefits without affecting the other")
    assert ("dysfunction", "ENABLING_CONDITION", "die") in _trip62(
        "Dysfunction occurs when the cells died")
    assert ("vascular shock", "ENABLING_CONDITION_AGENT", "arteriole") in _trip62(
        "Vascular shock occurs when arterioles lose their normal muscular tone and dilate")
    for s in (V08, V16, V19, V32, V46, S13, S25, S30, S41, S44, S45):
        for f in extract_predicates_v62(s).facts:
            assert f.relation in RELATIONS_V61, f
            assert f.pattern in PATTERNS_V61, f
    print("[definitional_predicate_v61] v6.2 self-test PASS")


if __name__ == "__main__":
    _self_test()
    _self_test_v62()
