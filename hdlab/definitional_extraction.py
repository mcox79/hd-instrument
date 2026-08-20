"""hdlab/definitional_extraction.py -- glass-box DEFINITIONAL-SENTENCE extractor.

WHAT THIS IS
------------
A symbolic (no learning, no LLM, fully inspectable) detector + extractor for the surface
constructions by which running text EXPLICITLY states what a word means:

  COPULA         "a nephron is the functional unit of the kidney"
  APPOSITIVE     "the nephron, the functional unit of the kidney, filters blood"
  GLOSSARY_COLON "renal artery: the artery that delivers blood to the kidney"
  CALLED         "this structure is called the nephron" / "known as the nephron"
  REFERS_TO      "nephron refers to the filtering unit" / "is defined as"

For each match it returns a `Definition(definiendum_span, definiens_span, pattern, ...)` and, from
the definiens, the HEAD noun (the genus term) -- i.e. the answer to "X is a kind of ___".

WHY IT EXISTS (2026-08-12)
--------------------------
The reading-grounding loop's only grounding signal is `canonicalize()`: bundle a word's
bag-of-content-words context over all its exposures, take the cosine-nearest anchor already in
ConceptSpace. That signal is DISTRIBUTIONAL CO-OCCURRENCE and is structurally unable to separate
"X means Y" from "X occurs near Y" (measured: see notes/definitional_grounding_v3_2026-08-12.md).
This module supplies the ORTHOGONAL signal -- meaning read off EXPLICIT DEFINITIONAL STRUCTURE --
so the two can be compared on the same audit rubric rather than one replacing the other.

BRAIN NOTE (per the for-every-mechanism-ask rule): explicit definitional learning ("a nephron is
the functional unit of the kidney") is fast, single-exposure, declarative encoding of a
relational proposition -- hippocampal/relational, not slow neocortical distributional statistics.
The two signals here are the CLS pair, not competitors: the distributional path is the slow
cortical accumulator, the definitional path is the one-shot relational bind. That is why this
module ADDS a signal instead of replacing the existing one.

REUSE (what this module does NOT reimplement)
---------------------------------------------
  hdlab.thematic_role_labeler.lemma_word   -- canonical never-emit-a-non-word normalizer
                                             (NOT lemma_verb, which returns stems like `arteri`)
  hdlab.closed_class_lexicon.is_closed_class / is_eligible_meaning -- function-word gate
  WordNet (already vendored, already used by hdlab.animacy_lexicon) -- nominal test for the
                                             definiendum; nothing new is downloaded or trained
Nothing here re-derives lemmatization, stop-lists, or a parser. The head-of-NP pick is a
right-most-noun-before-a-clause-boundary heuristic over the definiens span, deliberately shallow
and deliberately visible, NOT a new parser (hdlab already owns parse organs; none of them expose
a bare NP-head API, so the ~20-line local heuristic is the honest minimum).

ASCII-only. No unicode.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

from hdlab.closed_class_lexicon import is_closed_class
from hdlab.thematic_role_labeler import lemma_word as lemma_verb  # canonical never-non-word normalizer

# -------------------------------------------------------------------------------------------
# Surface inventory. Every item is a literal surface cue; nothing is learned or tuned.
# -------------------------------------------------------------------------------------------

_DET = r"(?:a|an|the|any|each|every|one)"
_BE = r"(?:is|are|was|were)"

# Determiners / degree words that can never be a genus head.
# 2026-08-12 (v4 F5 fix): the WEAK-TAXONOMY NOUNS (kind/type/form/part/number/group/set/series/
# process) were REMOVED from this set. Excluding them from the candidate list is what let the
# ADJECTIVE `medical` win in "a medical process of removing wastes" (-> `dialysis -> medical`).
# Weak nouns are now legal heads, ranked below a more specific noun, and the partitive rule
# below handles the cases where the content really does sit in the of-complement.
_NON_HEAD = {
    "a", "an", "the", "this", "that", "these", "those", "its", "their", "his", "her",
    "one",
}
_WEAK_HEAD = {"kind", "type", "sort", "form", "way", "part", "piece", "number", "group",
              "set", "lot", "bit", "series", "process", "unit", "thing"}

# MEASURE / PARTITIVE heads: "a pair of bean-shaped structures" asserts that the definiendum is
# a STRUCTURE, not a PAIR. The content sits in the of-complement -- but ONLY when that complement
# is indefinite/bare. "the functional unit of THE kidney" is a RELATIONAL noun, not a partitive:
# a nephron is a unit, it is not a kidney. That determiner test is the whole rule.
_MEASURE_HEAD = {"pair", "group", "number", "set", "collection", "variety", "bunch", "couple",
                 "series", "amount", "lot", "class", "kind", "type", "sort", "form", "piece",
                 "range", "array", "majority", "portion", "handful", "sequence",
                 # ADDED 2026-08-20, MEASURED not guessed. Sampling every definition extracted
                 # from 40,000 sentences of simplewiki + textbook_biology_2e: 7 of 47 heads
                 # (14.9%) are semantically EMPTY -- a definition whose head is one of these
                 # asserts nothing. `means` is the single commonest (2 of 47) and that is not
                 # chance: it is the TRIGGER WORD, so it appears in the definiens far more often
                 # than an ordinary noun would.
                 #   `Firing squad -> means`   from "the lawful means of execution in Finland"
                 #   `fruits -> means`         from "a means of dispersal"
                 # The partitive machinery below ALREADY handles this shape correctly for the
                 # entries above -- "a type of physical science" -> `science`, "a kind of bird"
                 # -> `bird`. These three were simply missing from a curated list, so this is a
                 # gap-fill in an existing tested mechanism, NOT new behaviour.
                 "means", "way", "part"}
_DEFINITE = {"the", "this", "that", "these", "those", "its", "their", "his", "her", "our"}

PATTERNS = ("COPULA", "APPOSITIVE", "GLOSSARY_COLON", "CALLED", "REFERS_TO")


@dataclass
class Definition:
    """One extracted definitional statement."""
    definiendum: str                 # surface string being defined
    definiens: str                   # surface string doing the defining
    pattern: str                     # one of PATTERNS
    head: Optional[str] = None       # lemma of the genus head noun of the definiens
    definiendum_lemma: Optional[str] = None
    definiens_lemmas: List[str] = field(default_factory=list)
    sentence: str = ""
    # v4 (2026-08-12). `definiendum_lemma` is the HEAD lemma and is what v3 stored as the
    # subject; storing it alone asserts about the general word something that was said about a
    # compound ("transcription bubble" -> `bubble`). `term` is the full definiendum and is the
    # v4 subject key; `term_type` is COMMON or PROPER, and PROPER keys keep their case so a
    # surname can never fold onto a common noun (`Shanhui Fan` vs `fan`).
    term: Optional[str] = None
    term_type: str = "COMMON"

    def to_dict(self) -> dict:
        return {
            "definiendum": self.definiendum,
            "definiens": self.definiens,
            "pattern": self.pattern,
            "head": self.head,
            "definiendum_lemma": self.definiendum_lemma,
            "definiens_lemmas": list(self.definiens_lemmas),
            "sentence": self.sentence,
            "term": self.term,
            "term_type": self.term_type,
        }


# -------------------------------------------------------------------------------------------
# Tokenization / lemma helpers (thin wrappers over the OWNED normalizer)
# -------------------------------------------------------------------------------------------

_TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z'-]*")


def _tokens(text: str) -> List[str]:
    return _TOKEN_RE.findall(text)


def _lemmas(text: str) -> List[str]:
    return [lemma_verb(t) for t in _tokens(text)]


# Tokens that END the leading NP of a definiens: relativizers, prepositions, and the
# post-nominal modifier cues (participles / predicative adjectives) that in English can only
# follow the head noun ("a physical structure PRESENT in an organism" -> head is `structure`).
_NP_BOUNDARY = {
    # relativizers / complementizers
    "that", "which", "who", "whom", "whose", "where", "when", "while", "because",
    # prepositions
    "of", "in", "on", "for", "to", "with", "by", "from", "into", "onto", "at", "as",
    "between", "among", "through", "during", "within", "across", "over", "under",
    # post-nominal participles / predicative adjectives
    "used", "found", "made", "having", "responsible", "containing", "consisting",
    "present", "called", "known", "located", "produced", "involved", "capable", "based",
    "formed", "composed", "derived", "attached", "surrounded", "carrying", "able",
    "such", "including", "known", "given", "taken", "seen", "shown",
    # coordination ends the NP too (a LIST is not a definiens)
    "and", "or", "but",
    # 2026-08-12 (v4 F4 fix) NEGATION / EXCLUSION cues. Their absence is why
    # "These unused structures WITHOUT function are called vestigial structures" yielded
    # `structure -> function`: the head walk crossed the negation and took the word whose
    # ABSENCE the sentence asserts. A genus head can never sit inside the scope of a negator.
    "without", "lacking", "lack", "lacks", "no", "not", "non", "never", "absent",
    "absence", "except", "excluding", "unlike", "rather", "instead", "minus", "sans",
}


def is_nominal_lemma(lemma: str) -> bool:
    """True iff `lemma` can be a NOUN: it has a WordNet noun sense, or WordNet does not know it
    at all (technical terms / proper nouns must pass). A lemma WordNet knows ONLY as an adjective
    or verb (`medical`, `moist`, `indicate`) returns False -- that test is what the old head
    picker lacked."""
    if not lemma:
        return False
    try:
        from nltk.corpus import wordnet as wn
    except Exception:                        # noqa: BLE001 - degraded mode, do not block
        return True
    if wn.synsets(lemma, pos="n"):
        return True
    if wn.synsets(lemma):
        return False
    return True


def _lead_np(tokens: List[str]) -> List[str]:
    lead: List[str] = []
    for t in tokens:
        if t.lower() in _NP_BOUNDARY:
            break
        lead.append(t)
    return lead


def definiens_head(definiens: str, _depth: int = 0) -> Optional[str]:
    """Genus head of a definiens NP: the LAST NOUN of the leading NP (English NPs are
    head-final), never a word from its post-modifier, never a word inside a negation, never an
    adjective. If that head is a MEASURE/partitive noun with an INDEFINITE of-complement, the
    real genus is the complement's head, so recurse into it.

    v4 (2026-08-12) fixes, each with a named regression test in _self_test:
      `dialysis -> medical`   an adjective won because `process` was excluded from the candidates
      `kidney -> pair`        partitive head kept instead of its of-complement
      `structure -> function` head taken from inside "without function"
    Deliberately shallow + fully visible (see module docstring)."""
    toks = _tokens(definiens)
    if not toks:
        return None
    lead = _lead_np(toks)
    span = lead if lead else toks
    cands = [t for t in span
             if t.lower() not in _NON_HEAD and not is_closed_class(lemma_verb(t))]
    nouns = [t for t in cands if is_nominal_lemma(lemma_verb(t))]
    if not nouns:
        # nothing nominal in the leading NP: try the whole span once, then REFUSE. Emitting an
        # adjective ("a moist, permeable skin" -> `moist`) is worse than emitting nothing.
        if lead:
            allc = [t for t in toks
                    if t.lower() not in _NON_HEAD and not is_closed_class(lemma_verb(t))]
            nouns = [t for t in allc if is_nominal_lemma(lemma_verb(t))]
        if not nouns:
            return None
    head = lemma_verb(nouns[-1])
    # ---- partitive / measure expansion -------------------------------------------------------
    if _depth < 2 and head in _MEASURE_HEAD:
        m = re.search(r"\b" + re.escape(nouns[-1]) + r"\s+of\s+(?P<comp>.+)$", definiens,
                      re.IGNORECASE)
        if m:
            comp = m.group("comp")
            first = (_tokens(comp) or [""])[0].lower()
            if first not in _DEFINITE:          # indefinite/bare complement => true partitive
                sub = definiens_head(comp, _depth + 1)
                if sub:
                    return sub
    return head


# -------------------------------------------------------------------------------------------
# The five extractors. Each returns 0..n Definitions from ONE sentence.
# -------------------------------------------------------------------------------------------

# "renal artery: the artery that delivers blood to the kidney"
# TIGHTENED 2026-08-12: the definiendum must be a SHORT sentence-initial term (<=4 words, no
# finite verb) or the pattern fires on any sentence that happens to contain a colon
# ("Prokaryotic DNA is found in the central part of the cell: a darkened region ..." was yielding
# cell -> nucleoid, a false definition). Measured before/after in
# data/analysis_definitional_harvest_v{1,2}/metrics.json.
_RE_COLON = re.compile(
    r"^\s*(?P<dfd>[A-Za-z][A-Za-z'\-]*(?:\s+[A-Za-z][A-Za-z'\-]*){0,3})\s*:\s*"
    r"(?P<dfs>" + _DET + r"\s+.+)$",
    re.IGNORECASE)
# A colon-definiendum containing a finite verb is a clause, not a term.
_FINITE_VERB = {"is", "are", "was", "were", "has", "have", "had", "do", "does", "did",
                "can", "will", "would", "found", "said", "says", "means", "include"}

# "a nephron is the functional unit of the kidney"
_RE_COPULA = re.compile(
    r"(?:^|[,;]\s*|\.\s+)(?:" + _DET + r"\s+)?(?P<dfd>[A-Za-z][A-Za-z '\-]{0,60}?)\s+"
    r"(?P<be>" + _BE + r")\s+(?P<dfs>" + _DET + r"\s+[A-Za-z].{2,120}?)(?=[,.;]|$)",
    re.IGNORECASE)

# "the nephron, the functional unit of the kidney, filters blood"
# TIGHTENED 2026-08-12: bare `X, a Y,` also matches (i) COORDINATE LISTS -- "the thigh, the leg,
# and the foot" gave thigh -> leg -- and (ii) FRONTED PPs -- "In addition, the wide range of
# topics," gave addition -> range. Both are guarded below in _appos_ok(), not by regex, so the
# rejection reason stays inspectable.
_RE_APPOS = re.compile(
    r"(?:^|\s)(?:" + _DET + r"\s+)?(?P<dfd>[A-Za-z][A-Za-z'\-]{1,30})\s*,\s*"
    r"(?P<dfs>" + _DET + r"\s+[A-Za-z].{2,120}?)\s*,",
    re.IGNORECASE)

_FRONTING_PREP = {"in", "at", "on", "for", "by", "with", "from", "during", "after", "before",
                  "under", "over", "within", "through", "among", "between", "besides",
                  "unlike", "like", "despite", "according",
                  # sentence-initial SUBORDINATORS open a clause whose comma is not an appositive
                  "while", "although", "though", "because", "since", "if", "when", "whereas",
                  "unless", "as"}


def _is_nominal_or_unknown(lemma: str) -> bool:
    """True if `lemma` can head a noun phrase, or is not in WordNet at all (technical terms and
    proper nouns must pass -- they are precisely the words a reader needs defined)."""
    try:
        from nltk.corpus import wordnet as wn
    except Exception:                       # noqa: BLE001 - degraded mode, do not block
        return True
    if wn.synsets(lemma, pos="n"):
        return True
    if wn.synsets(lemma):                   # known to WordNet but NOT as a noun -> reject
        return False
    return True                             # out-of-WordNet -> allow


# v4 F2: verbs that introduce an ENUMERATION OF PARTS. "the urinary system, which is comprised
# of the paired kidneys, the ureter, urinary bladder and urethra" is a LIST; its commas are
# item separators, not appositive brackets.
_ENUM_TRIGGER = re.compile(
    r"\b(?:consists?\s+of|consisted\s+of|comprised\s+of|comprises|composed\s+of|"
    r"made\s+up\s+of|made\s+of|divided\s+into|consisting\s+of|including|includes?|"
    r"such\s+as|contains?|containing)\b", re.IGNORECASE)

_CLAUSE_SUBJ_PRONOUN = {"it", "they", "he", "she", "we", "this", "that", "there", "these"}
_FINITE_VERB_TAIL = {"is", "are", "was", "were", "has", "have", "had", "does", "do", "did",
                     "can", "will", "would", "means", "becomes", "become"}


def _tail_is_further_list_items(sentence: str, end_idx: int) -> bool:
    """After the appositive's closing comma: do MORE bare NPs follow, joined by and/or?
    "..., the ureter, urinary bladder and urethra" -> yes (LIST).
    "..., taking oxygenated blood to the organs and muscles" -> no (participial adjunct).
    "..., and Indonesia is the biggest exporter" -> no (coordinated CLAUSE)."""
    low = [t.lower() for t in _tokens(sentence[end_idx:])]
    if "and" not in low and "or" not in low:
        return False
    cut = min([low.index(c) for c in ("and", "or") if c in low])
    pre, post = low[:cut], low[cut + 1: cut + 6]
    if cut > 4:
        return False
    if any(t in _FINITE_VERB_TAIL or t.endswith("ing") or t == "to" for t in pre):
        return False
    if any(t in _FINITE_VERB_TAIL for t in post) or (post and post[0] in _CLAUSE_SUBJ_PRONOUN):
        return False
    return True


def _appos_ok(sentence: str, m: "re.Match") -> bool:
    """Guards for the appositive pattern. Returns False (with the reason implicit in which test
    fires) for coordinate lists and fronted prepositional phrases."""
    # (1) COORDINATE LIST: the appositive's closing comma is followed by `and`/`or`.
    tail = sentence[m.end():].lstrip()
    if re.match(r"(?:and|or)\b", tail, re.IGNORECASE):
        return False
    # (2) COORDINATE LIST, item N: the definiendum is itself preceded by `, <det> `.
    head_ctx = sentence[max(0, m.start() - 30):m.start("dfd")]
    if re.search(r",\s*(?:a|an|the)\s+[A-Za-z'\-]*\s*$", head_ctx, re.IGNORECASE):
        return False
    # (3) FRONTED PP: the sentence opens with a preposition and the appositive comma is that
    #     PP's closing comma ("In addition, the wide range ...").
    lead = _tokens(sentence[:m.start("dfd")])
    if lead and lead[0].lower() in _FRONTING_PREP and len(lead) <= 4:
        return False
    # (4) v4 F2a: an ENUMERATION VERB before the definiendum + a BARE-NP "definiens" is a list
    #     item, not a definition ("comprised of the paired kidneys, the ureter, urinary bladder
    #     and urethra" gave `kidney -> ureter`). Both conditions are required: a descriptive
    #     definiens after an enumeration verb ("consists of the aorta, the major artery of the
    #     body, which ...") is still a real appositive.
    dfs_content = [t for t in _tokens(m.group("dfs")) if not is_closed_class(lemma_verb(t))]
    if len(dfs_content) <= 2 and _ENUM_TRIGGER.search(sentence[:m.start("dfd")]):
        return False
    # (5) v4 F2b: more bare NPs follow the closing comma, joined by and/or
    if len(dfs_content) <= 3 and _tail_is_further_list_items(sentence, m.end()):
        return False
    return True


# "... is called the nephron" / "known as the nephron" / "referred to as X"
# TIGHTENED 2026-08-12: the trailing term is an NP, not one token -- "is called oxidative
# phosphorylation" was yielding definiendum `oxidative` (the modifier) instead of
# `phosphorylation` (the head). English NPs are head-final, so capture the span and take its
# last open-class token.
_RE_CALLED = re.compile(
    r"(?P<dfs>[A-Za-z][A-Za-z '\-]{2,120}?)\s+(?:" + _BE + r"\s+)?"
    r"(?:called|known\s+as|termed|named|referred\s+to\s+as)\s+"
    r"(?:" + _DET + r"\s+)?(?P<dfd>[A-Za-z][A-Za-z'\- ]{1,45}?)(?=[,.;]|\s+(?:that|which|and|or|in|of|to|for|by|with)\b|$)",
    re.IGNORECASE)

# "X refers to Y" / "X is defined as Y" / "X means Y"
_RE_REFERS = re.compile(
    r"(?:^|[,;]\s*)(?:" + _DET + r"\s+)?(?P<dfd>[A-Za-z][A-Za-z'\-]{1,30})\s+"
    r"(?:refers\s+to|" + _BE + r"\s+defined\s+as|means)\s+(?P<dfs>.{2,120}?)(?=[,.;]|$)",
    re.IGNORECASE)


# v4 F3/F1 -------------------------------------------------------------------------------------
# A definiendum is a TERM. v3 stored only its head lemma, so "transcription bubble is called..."
# banked `bubble -> region`, which asserts about the general word something that was said about a
# compound; and a COPULA whose subject span ran on ("...and are surrounded by new nuclear
# envelopes Cancer") banked a subject that is not a term at all.
_TERM_STOP = set(_NP_BOUNDARY) | {"is", "are", "was", "were", "has", "have", "had", "does",
                                  "do", "did", "can", "will", "would", "until", "unless"}
_MAX_TERM_CONTENT_TOKENS = 4


def _sentence_token_spans(sentence: str):
    """(token, start_offset, end_offset) for every word token. The END offset is what makes the
    v5 gap test possible; v4 kept only the start and so could not see that two tokens it was
    about to merge had a comma between them."""
    return [(m.group(0), m.start(), m.end()) for m in _TOKEN_RE.finditer(sentence)]


# v5 F7 (2026-08-12). A TERM IS A CONTIGUOUS SURFACE SPAN. Anything other than spaces between
# two tokens -- a comma, a period, a quote, a bracket -- is a boundary that no single term can
# cross. v4's proper-name expansion walked leftwards over the TOKEN list, which drops punctuation
# entirely, so "Like DNA, RNA is a polymer" merged into the term `DNA RNA`, and
# "at Wembley Stadium, Bowie was one of the best performers" into `Wembley Stadium Bowie`.
# MEASURED@notes/definitional_term_boundary_v5_2026-08-12.md: 22 such merged terms in the 1956
# v4 facts.
def _gap_is_clean(sentence: str, a_end: int, b_start: int) -> bool:
    return sentence[a_end:b_start].strip(" ") == ""


def _expand_proper_name(dfd: str, sentence: str) -> Tuple[str, bool]:
    """If the definiendum is a NAME, grow it leftwards over contiguous capitalised tokens and
    report proper-ness. "said Shanhui Fan, an expert..." -> ("Shanhui Fan", True);
    "Currie Technologies, the number one seller" -> ("Currie Technologies", True).
    Capitalisation at position 0 of the sentence is NOT evidence of a name.
    v5: expansion NEVER crosses punctuation (see _gap_is_clean)."""
    toks = _tokens(dfd)
    if not toks or not toks[0][:1].isupper():
        return dfd, False
    spans = _sentence_token_spans(sentence)
    for i, (t, _pos, _end) in enumerate(spans):
        if t != toks[0]:
            continue
        if i == 0 and len(toks) == 1:
            return dfd, False              # sentence-initial capital only -> ordinary word
        j = i
        while (j > 0 and spans[j - 1][0][:1].isupper()
               and spans[j - 1][0].lower() not in _NP_BOUNDARY
               and not is_closed_class(lemma_verb(spans[j - 1][0]))
               and j - 1 > 0                # never absorb the sentence-initial token
               and _gap_is_clean(sentence, spans[j - 1][2], spans[j][1])):   # v5 F7
            j -= 1
        head_tok = toks[-1]
        end = None
        for k in range(i, len(spans)):
            if spans[k][0] == head_tok:
                end = k
                break
        if end is None:
            end = i
        for k in range(i, end):            # v5 F7: forward extent is contiguous too
            if not _gap_is_clean(sentence, spans[k][2], spans[k + 1][1]):
                end = k
                break
        name = " ".join(s[0] for s in spans[j:end + 1])
        proper = (i > 0) or (j < i)
        return name, proper
    return dfd, False


# v6.1 F-D1 (2026-08-13) -- ONE TERM-BOUNDARY ROUTINE FOR EVERY PATTERN.
# The v5 fix (F7/F8 above) and this one are the SAME defect class: a term whose surface span was
# cut in the wrong place. v5 fixed it inside `build_term`/`_expand_proper_name`/
# `split_glossary_entries`; the v6 predicate block reached the same code through `build_term`,
# and still banked `form`, `process`, `second-degree`, `termination` (twice, colliding). The
# response is NOT a second per-pattern fix: `build_term` is now a thin wrapper over ONE routine,
# `build_term_explain`, whose behaviour is selected by an explicit TermPolicy. Every pattern --
# the five shipped ISA ones and every predicate one -- boundaries its term here and nowhere else.
# LEGACY is byte-identical to the pre-v6.1 code (proved by the per-pattern ISA digests in
# experiments/exp_definitional_predicate_v61.py); STRICT adds the three v6.1 rules.
_CATEGORY_NOUN = {
    # bare container nouns that carry no identity of their own. As a WHOLE term they name
    # nothing ("The process begins when ..." -> `process`); as a MODIFIED term they are fine
    # ("age structure", "cell cycle"), so the rule only fires on a single-content-token term.
    "form", "process", "type", "kind", "way", "stage", "sort", "part", "piece", "example",
    "case", "thing", "aspect", "version", "variety", "step", "phase", "class", "category",
    "group", "set", "series", "number", "unit",
}


# ---- V62_TERM_SANITY_BLOCK_START (2026-08-13) --------------------------------------------------
# v6.2 D-B. The v5/v6.1 boundary work fixed UNDER-taking and overshot into OVER-taking: the term
# now swallows material that is not part of the concept's name. Three surfaces, hand-named off the
# v6.1 blind sample, all fixed HERE in the one centralized routine (a per-pattern patch is what
# made the boundary bug recur once already):
#   [20] `pathway's`                             a bare possessive fragment is not a term
#   [27] `interesting example of ecosystem dynamics`   a DISCOURSE FRAME, not a concept
#   [46] `tragic irish potato famine`            an evaluative adjective is not part of the name
# All three are POLICY-GATED and OFF under TERM_POLICY_LEGACY, so the five shipped ISA patterns
# (which reach this routine through `build_term`, i.e. LEGACY) cannot move.
_EVALUATIVE_LEAD_ADJ = {
    # The director's list, verbatim. Each is a WRITER'S APPRAISAL of the referent, never part of
    # the term itself: a reader looking the concept up would not find it under this word.
    "tragic", "interesting", "important", "remarkable", "classic", "famous",
}
_DISCOURSE_FRAME_HEAD = {
    # "an interesting EXAMPLE OF ecosystem dynamics occurred when ..." -- the head noun frames the
    # DISCOURSE ("here comes an illustration"), it does not name a concept. Refuse; do not guess a
    # trim to the of-complement, which is a different (and unasserted) claim.
    "example", "case", "instance", "illustration",
}
# ---- V62_TERM_SANITY_BLOCK_END -----------------------------------------------------------------


@dataclass(frozen=True)
class TermPolicy:
    """Which term-boundary rules apply. LEGACY = the shipped behaviour, bit for bit."""
    name: str = "LEGACY"
    reject_bare_category_head: bool = False        # v6.1 D1a
    restart_at_shared_head_coordination: bool = False   # v6.1 D1b
    extend_over_of_complement: bool = False        # v6.1 D1c
    # ---- V62_TERM_SANITY_BLOCK_START (fields) --------------------------------------------------
    reject_possessive_term: bool = False           # v6.2 D-Ba
    reject_discourse_frame_head: bool = False      # v6.2 D-Bb
    strip_evaluative_lead_adjective: bool = False  # v6.2 D-Bc
    # ---- V62_TERM_SANITY_BLOCK_END -------------------------------------------------------------


TERM_POLICY_LEGACY = TermPolicy()
TERM_POLICY_STRICT = TermPolicy("STRICT_V61", True, True, True)
# ---- V62_TERM_SANITY_BLOCK_START (policy) ------------------------------------------------------
TERM_POLICY_STRICT_V62 = TermPolicy("STRICT_V62", True, True, True, True, True, True)
# ---- V62_TERM_SANITY_BLOCK_END -----------------------------------------------------------------


def _term_cut(toks: List[str], proper: bool) -> Tuple[List[str], Optional[int]]:
    """(span kept, index of the STOP token that ended it or None). The stop index is what the
    v6.1 rules need: which boundary word cut the term tells you whether the rest of the span is
    a shared-head coordination (`or`) or a postmodifier (`of`)."""
    cut: List[str] = []
    for i, t in enumerate(toks):
        if t.lower() in _TERM_STOP and not proper:
            return cut, i
        cut.append(t)
    return cut, None


def _term_content(span: List[str]) -> List[str]:
    return [t for t in span if t.lower() not in _NON_HEAD and not is_closed_class(lemma_verb(t))]


def _is_shared_head_modifier(tok: str) -> bool:
    """True if `tok` cannot itself head an NP, so a coordination it sits in must be sharing the
    head that follows ("a SECOND-DEGREE or incomplete BLOCK"). Hyphenated compounds and
    WordNet-adjective-only tokens qualify; a token WordNet knows as a noun does not."""
    if "-" in tok:
        return True
    lem = lemma_verb(tok)
    try:
        from nltk.corpus import wordnet as wn
    except Exception:                        # noqa: BLE001 - degraded mode, do not block
        return False
    if wn.synsets(lem, pos="n"):
        return False
    return bool(wn.synsets(lem, pos="a") or wn.synsets(lem, pos="s"))


def _coord_last_conjunct(toks: List[str], cut: List[str], stop_idx: Optional[int]
                         ) -> Tuple[List[str], Optional[int], bool]:
    """"A second-degree or incomplete block" -- the term was cut at `or` and banked
    `second-degree`, which is not a term. When the LEFT conjunct cannot head an NP the two
    conjuncts SHARE the head to their right, and the recoverable term is the RIGHT conjunct."""
    if stop_idx is None or toks[stop_idx].lower() not in ("and", "or"):
        return cut, stop_idx, False
    right, right_stop = _term_cut(toks[stop_idx + 1:], False)
    if not right:
        return cut, stop_idx, False
    left_content = _term_content(cut)
    if left_content and not _is_shared_head_modifier(left_content[-1]):
        return cut, stop_idx, False          # both conjuncts are real terms: keep the first
    right_content = _term_content(right)
    if not right_content or not is_nominal_lemma(lemma_verb(right_content[-1])):
        return cut, stop_idx, False
    new_stop = None if right_stop is None else stop_idx + 1 + right_stop
    return right, new_stop, True


def _of_complement_content(toks: List[str], stop_idx: int, n_left: int) -> List[str]:
    """Content tokens of the `of`-postmodifier, or [] if it cannot be carried into the term.
    "Termination of translation" and "Termination of the signal" are DIFFERENT terms; cutting
    both to `termination` collides them into one indistinguishable subject."""
    span, _ = _term_cut(toks[stop_idx + 1:], False)
    content = _term_content(span)
    if not content or len(content) + n_left > _MAX_TERM_CONTENT_TOKENS:
        return []
    if not is_nominal_lemma(lemma_verb(content[-1])):
        return []
    return content


def build_term_explain(dfd: str, sentence: str, policy: TermPolicy = TERM_POLICY_LEGACY
                       ) -> Tuple[Optional[Tuple[str, str]], str]:
    """((term, term_type) or None, REASON). THE single term-boundary routine (v6.1 D1)."""
    name, proper = _expand_proper_name(dfd, sentence)
    toks = _tokens(name)
    if not toks:
        return None, "NO_TOKENS"
    cut, stop_idx = _term_cut(toks, proper)
    note = ""
    if policy.restart_at_shared_head_coordination and not proper:
        cut, stop_idx, restarted = _coord_last_conjunct(toks, cut, stop_idx)
        if restarted:
            note = "|COORD_RESTART"
    if not cut:
        return None, "EMPTY_CUT"
    content = _term_content(cut)
    if not content:
        return None, "NO_CONTENT"
    # ---- V62_TERM_SANITY_BLOCK_START (checks) --------------------------------------------------
    if policy.strip_evaluative_lead_adjective:
        while len(content) > 1 and content[0].lower() in _EVALUATIVE_LEAD_ADJ:
            content = content[1:]
            note += "|EVAL_ADJ_STRIPPED"
        if content[0].lower() in _EVALUATIVE_LEAD_ADJ:
            return None, "EVALUATIVE_ONLY_TERM"     # nothing left that names anything
    if policy.reject_possessive_term and any(t.lower().endswith("'s") for t in content):
        return None, "POSSESSIVE_FRAGMENT"
    if (policy.reject_discourse_frame_head
            and lemma_verb(content[-1]).lower() in _DISCOURSE_FRAME_HEAD):
        return None, "DISCOURSE_FRAME_TERM"
    # ---- V62_TERM_SANITY_BLOCK_END -------------------------------------------------------------
    if len(content) > _MAX_TERM_CONTENT_TOKENS:
        return None, "TOO_LONG"             # run-on span, not a term (F3b)
    if any(t.lower() in _TERM_STOP for t in content):
        return None, "STOP_IN_CONTENT"
    if proper:
        return (" ".join(content), "PROPER"), "OK" + note
    if (policy.reject_bare_category_head and len(content) == 1
            and lemma_verb(content[0]).lower() in _CATEGORY_NOUN):
        return None, "BARE_CATEGORY_HEAD"
    tail: List[str] = []
    if (policy.extend_over_of_complement and stop_idx is not None
            and toks[stop_idx].lower() == "of"):
        tail = _of_complement_content(toks, stop_idx, len(content))
    body = [t.lower() for t in content[:-1]]
    if tail:
        term = " ".join(body + [content[-1].lower(), "of"]
                        + [t.lower() for t in tail[:-1]] + [lemma_verb(tail[-1])])
        return (term, "COMMON"), "OK" + note + "|OF_EXTENDED"
    return (" ".join(body + [lemma_verb(content[-1])]), "COMMON"), "OK" + note


def build_term_policy(dfd: str, sentence: str, policy: TermPolicy = TERM_POLICY_LEGACY
                      ) -> Optional[Tuple[str, str]]:
    return build_term_explain(dfd, sentence, policy)[0]


def build_term(dfd: str, sentence: str) -> Optional[Tuple[str, str]]:
    """(term, term_type) for a definiendum span, or None if it is not a term at all.
    COMMON terms are lowercased with the HEAD token lemmatised ("Age structure" ->
    "age structure"); PROPER terms keep their surface case so they can never collide with a
    common noun ("Shanhui Fan" stays distinct from `fan`).

    v6.1: this is `build_term_explain` under TERM_POLICY_LEGACY -- unchanged behaviour, one
    implementation. Every pattern in this module boundaries its term through that routine."""
    return build_term_policy(dfd, sentence, TERM_POLICY_LEGACY)


def _mk(dfd: str, dfs: str, pattern: str, sentence: str,
        head_span: Optional[str] = None) -> Optional[Definition]:
    # v7 (2026-08-13): `head_span` lets a CALLER name a DIFFERENT sub-span of the definiens as
    # the span the genus head is read from, without changing what is RECORDED as the definiens.
    # Default None == read the head from `dfs`, i.e. byte-identical to the pre-v7 behaviour for
    # every existing caller. Only the CALLED branch passes it.
    dfd = dfd.strip().strip(",;:'\" ")
    dfs = dfs.strip().strip(",;:'\" ")
    if not dfd or not dfs:
        return None
    dfd_toks = _tokens(dfd)
    if not dfd_toks:
        return None
    # definiendum head = last token of the definiendum phrase (English NPs are head-final)
    dfd_lemma = lemma_verb(dfd_toks[-1])
    if is_closed_class(dfd_lemma):
        return None
    # A DEFINIENDUM IS A NOMINAL. Adverbs and pure verbs cannot be defined by "X is a Y" in the
    # taxonomic sense this module extracts -- "Additionally, the gradual melting ..." was yielding
    # `additionally -> melting`, and "although they were disappointing, the prequels ..." was
    # yielding `disappoint -> prequels`. Out-of-WordNet tokens (technical coinages, proper nouns:
    # `rubisco`, `arthropoda`) are ALLOWED through, since those are exactly the terms a reader
    # most needs defined and WordNet cannot adjudicate them.
    if not _is_nominal_or_unknown(dfd_lemma):
        return None
    head = definiens_head(head_span if head_span is not None else dfs)
    if head is None or head == dfd_lemma:
        return None
    built = build_term(dfd, sentence)
    if built is None:
        return None                          # F3b: run-on / non-term definiendum
    term, term_type = built
    if term.lower() == head:                 # tautology at TERM level too
        return None
    dfs_lemmas = [l for l in _lemmas(dfs) if not is_closed_class(l)]
    return Definition(definiendum=dfd, definiens=dfs, pattern=pattern, head=head,
                      definiendum_lemma=dfd_lemma, definiens_lemmas=dfs_lemmas,
                      sentence=sentence, term=term, term_type=term_type)


# v4 F6: OpenStax glossary blocks arrive as ONE "sentence" holding many `term: definition`
# entries with no sentence boundary, so a definiens runs into the NEXT entry
# ("bottleneck effect: the magnification of genetic drift ... catastrophes FOUNDER EFFECT: a
# magnification ..."). Split on entry starts before extracting.
#
# v5 F8 (2026-08-12) -- THE SPLIT POINT IS MINIMAL, NOT MAXIMAL. v4's `{0,3}` let the entry term
# start up to THREE WORDS to the LEFT of where it really starts, and regex alternation picks the
# LEFTMOST viable start, so the term absorbed the TAIL OF THE PREVIOUS ENTRY'S DEFINIENS:
#   "... with their abiotic environment equilibrium: the steady state ..."
#        -> term `abiotic environment equilibrium`   (true term: `equilibrium`)
#   "... from the producers to the apex consumers biome: a large-scale community ..."
#        -> term `apex consumers biome`              (true term: `biome`)
# MEASURED@notes/definitional_term_boundary_v5_2026-08-12.md: 292 of 363 glossary facts (80.4%)
# carried a term that is NOT a real glossary key of the source textbook.
#
# Inside a RUN-ON block the true left edge of the term is UNRECOVERABLE -- the preceding words
# are ordinary running text and no surface cue separates them. What IS certain is that the token
# immediately left of the colon is the term's HEAD (English terms are head-final). So the split
# point is that token: the resulting term is UNDER-SPECIFIC (`web` for `detrital food web`) but
# it is NEVER A DIFFERENT CONCEPT. Under-specific beats corrupt.
#
# The multiword term is recovered instead by NOT DESTROYING THE LINE STRUCTURE upstream: in a
# line-aware corpus each glossary entry is its own sentence, `split_glossary_entries` finds a
# single marker and returns the text unchanged, and `_RE_COLON` (anchored at ^) reads the full
# correct term. See `load_biology_sentences_lineaware` in experiments/exp_definitional_grounding_v5.py.
_GLOSSARY_ENTRY = re.compile(
    r"(?:(?<=^)|(?<=\s))(?P<term>[A-Za-z][A-Za-z0-9'\-]*)\s*:\s")


def split_glossary_entries(text: str) -> List[str]:
    """Split a run-on glossary block into one string per `term: definition` entry. Returns
    [text] unchanged unless at least TWO entry markers are present (a single mid-sentence colon
    is not a glossary). The boundary is placed at the LAST token before the colon (v5 F8)."""
    starts = [m.start("term") for m in _GLOSSARY_ENTRY.finditer(text)]
    if len(starts) < 2:
        return [text]
    starts = [s for s in starts if s > 0] if starts[0] != 0 else starts
    bounds = sorted(set([0] + starts + [len(text)]))
    segs = [text[a:b].strip() for a, b in zip(bounds, bounds[1:])]
    return [s for s in segs if len(s) >= 6]


_LEADING_COORD = {"and", "or", "then", "but", "also"}


def _strip_leading_coordinator(sentence: str, dfs: str, dfs_start: int) -> Optional[str]:
    """A CALLED definiens that starts with a coordinator is one of two things:
      (a) the LAST ITEM of a comma list -- "for gas exchange, nutrient circulation, AND
          locomotion called the water vascular system" -> `system -> locomotion`, a FAULT; or
      (b) a clause continuation whose leading conjunction is just noise -- "diverge into minor
          arteries, AND THEN smaller vessels called arterioles" -> `arteriole -> vessel`, a GOOD
          fact that must NOT be dropped.
    Distinguish by what precedes: two or more comma-separated segments ending in a BARE NP is a
    list (return None = refuse); otherwise strip the conjunction and keep the definiens."""
    toks = _tokens(dfs)
    if not toks or toks[0].lower() not in _LEADING_COORD:
        return dfs
    segs = [s.strip() for s in sentence[:dfs_start].split(",")]
    segs = [s for s in segs if s]
    if len(segs) >= 2:
        last = segs[-1]
        last_toks = [t.lower() for t in _tokens(last)]
        if last_toks and len(last_toks) <= 5 and not any(
                t in _FINITE_VERB_TAIL or t.endswith("ing") for t in last_toks):
            return None                      # list item, not a definiens
    kept = list(toks)
    while kept and kept[0].lower() in _LEADING_COORD:
        kept.pop(0)
    if not kept:
        return None
    idx = dfs.lower().find(kept[0].lower())
    return dfs[idx:] if idx >= 0 else " ".join(kept)


def extract_definitions(sentence: str) -> List[Definition]:
    """All definitional statements in ONE sentence. Order: GLOSSARY_COLON, APPOSITIVE, COPULA,
    CALLED, REFERS_TO. Duplicates on (definiendum_lemma, head) are collapsed, first-pattern-wins."""
    if not sentence or len(sentence) < 6:
        return []
    segs = split_glossary_entries(sentence)
    if len(segs) > 1:
        out_all: List[Definition] = []
        seen_g = set()
        for seg in segs:
            for d in _extract_one(seg):
                key = (d.definiendum_lemma, d.head)
                if key in seen_g:
                    continue
                seen_g.add(key)
                d.sentence = sentence          # provenance stays the ORIGINAL block
                out_all.append(d)
        return out_all
    return _extract_one(sentence)


def _extract_one(sentence: str) -> List[Definition]:
    out: List[Definition] = []
    for rx, pat in ((_RE_COLON, "GLOSSARY_COLON"),
                    (_RE_APPOS, "APPOSITIVE"),
                    (_RE_COPULA, "COPULA"),
                    (_RE_CALLED, "CALLED"),
                    (_RE_REFERS, "REFERS_TO")):
        for m in rx.finditer(sentence):
            if pat == "GLOSSARY_COLON":
                # a colon-definiendum containing a finite verb is a clause, not a term
                if any(t.lower() in _FINITE_VERB for t in _tokens(m.group("dfd"))):
                    continue
            if pat == "APPOSITIVE" and not _appos_ok(sentence, m):
                continue
            dfs_text = m.group("dfs")
            head_span = None
            if pat == "CALLED":
                dfs_text = _strip_leading_coordinator(sentence, dfs_text, m.start("dfs"))
                if dfs_text is None:
                    continue
                # v7 (2026-08-13): CONSTITUENT-BOUNDED antecedent. See `called_antecedent`.
                # Returns None to REFUSE -- a dropped fact beats `fermentation ISA nadh`.
                ant = called_antecedent(sentence, m, dfs_text)
                if ant is None:
                    continue
                dfs_text, head_span = ant.definiens, ant.head_span
            d = _mk(m.group("dfd"), dfs_text, pat, sentence, head_span=head_span)
            if d is not None:
                out.append(d)
    seen = set()
    uniq: List[Definition] = []
    for d in out:
        key = (d.definiendum_lemma, d.head)
        if key in seen:
            continue
        seen.add(key)
        uniq.append(d)
    return uniq


def sentence_has_definitional_pattern(sentence: str) -> bool:
    """Weak test: does the sentence contain ANY definitional construction (regardless of which
    words it links)? Used for base-rate measurement, NOT for grounding."""
    return bool(extract_definitions(sentence))


def links(sentence: str, subject_lemma: str, object_lemma: str) -> Optional[str]:
    """Does a definitional construction in `sentence` link `subject_lemma` (as definiendum) to
    `object_lemma` (as the definiens HEAD, or anywhere in the definiens)? Returns the pattern
    name at the strongest match level, else None. Levels: '<PATTERN>:HEAD' (object IS the genus
    head -- the strong claim) or '<PATTERN>:SPAN' (object merely occurs inside the definiens)."""
    for d in extract_definitions(sentence):
        if d.definiendum_lemma != subject_lemma:
            continue
        if d.head == object_lemma:
            return d.pattern + ":HEAD"
    for d in extract_definitions(sentence):
        if d.definiendum_lemma != subject_lemma:
            continue
        if object_lemma in d.definiens_lemmas:
            return d.pattern + ":SPAN"
    return None


def extract_from_sentences(sentences: Sequence[str]) -> Dict[str, List[Definition]]:
    """definiendum_lemma -> [Definition, ...] over a corpus slice."""
    out: Dict[str, List[Definition]] = {}
    for s in sentences:
        for d in extract_definitions(s):
            out.setdefault(d.definiendum_lemma, []).append(d)
    return out


# ===========================================================================================
# VP-PREDICATE EXTRACTION (2026-08-13). STRICTLY ADDITIVE.
#
# MEASURED@notes/verb_definition_gap_2026-08-13.md: 0 of 2092 banked facts define a VERB, but
# 119 already have a PROCESS-flavoured genus head. The predicate is not missing from the text --
# it is THROWN AWAY. `definiens_head()` returns the leading-NP head and `_NP_BOUNDARY` cuts at
# `of / by / which / when`, i.e. exactly where the verbal content of a process definition starts.
# We bank `photosynthesis ISA process` and discard "by which light energy is converted ...".
#
# THIS BLOCK ADDS A SECOND, SEPARATE READ-OUT. It does NOT touch `extract_definitions`,
# `_mk`, `definiens_head`, `build_term`, or any regex above this line, so the ISA fact set is
# byte-identical before and after (asserted off-corpus in
# experiments/exp_definitional_predicate_v6.py).
#
# SCHEMA: the store persists 3-tuples and drops edge metadata on flush, so a predicate is
# emitted as ADDITIONAL 3-tuples with distinct relation types, never as an enriched record:
#   PROCESS_ACTION            subject=TERM, object=verb lemma            (VP1, VP2)
#   PROCESS_PATIENT           subject=TERM, object=head noun of the verb's complement (VP1, VP2)
#   ENABLING_CONDITION        subject=TERM, object=verb lemma of the when-clause      (VP4)
#   ENABLING_CONDITION_AGENT  subject=TERM, object=head noun of the when-clause subject (VP4)
# VP4 is deliberately NOT an ISA/genus relation: "X occurs when C" states a triggering
# condition, not a kind. Forcing it into the genus slot would be a false taxonomic claim.
#
# NO PARSER. The clause main-verb walk below is a stack of NAMED SURFACE RULES over WordNet
# morphology, in the same deliberately-shallow, deliberately-visible style as `definiens_head`.
# hdlab.pos_tagger (the owned UPOS perceptron, data/frontend_assets/pos_tagger_ud_ewt_upos.json)
# WAS evaluated for this job on 2026-08-13 and REJECTED: on OpenStax prose it tags `occurs`,
# `prevents`, `break`, `form` and `fail` as NOUN (UD-EWT web-text training, domain shift), which
# is precisely the decision this walk has to make. It is not reused because it is wrong here,
# not because it was overlooked.
# ===========================================================================================

PREDICATE_PATTERNS = ("VP1_PROCESS_OF", "VP2_BY_WHICH", "VP4_OCCURS_WHEN")
PREDICATE_RELATIONS = ("PROCESS_ACTION", "PROCESS_PATIENT",
                       "ENABLING_CONDITION", "ENABLING_CONDITION_AGENT")

# Container nouns that name a PROCESS rather than a kind. Union of the containers proposed in
# notes/verb_definition_gap_2026-08-13.md s.4 and the process-flavoured genus heads it measured
# in the banked v5 facts (process 52, mechanism 10, reaction 9, method 9, event 7, change 7,
# response 6, movement 6, technique 5, pathway 2, cycle 2, action 2, act 1, activity 1).
_PROCESS_CONTAINER = {
    "process", "act", "action", "activity", "mechanism", "method", "technique", "procedure",
    "reaction", "response", "movement", "series", "phenomenon", "event", "change", "pathway",
    "cycle",
}
_CONT_ALT = "(?:" + "|".join(sorted(_PROCESS_CONTAINER)) + ")"

# "Magnification is the process of enlarging an object in appearance"
_RE_VP1 = re.compile(
    r"(?:^|[,;]\s*|\.\s+)(?:" + _DET + r"\s+)?(?P<dfd>[A-Za-z][A-Za-z '\-]{0,60}?)\s+"
    r"(?:" + _BE + r")\s+" + _DET + r"\s+(?:[A-Za-z'\-]+\s+){0,2}?"
    r"(?P<cont>" + _CONT_ALT + r")\s+of\s+(?P<rest>[A-Za-z][^.;]{2,200})",
    re.IGNORECASE)

# "Differentiation is the process by which unspecialized cells become specialized ..."
_RE_VP2 = re.compile(
    r"(?:^|[,;]\s*|\.\s+)(?:" + _DET + r"\s+)?(?P<dfd>[A-Za-z][A-Za-z '\-]{0,60}?)\s+"
    r"(?:" + _BE + r")\s+" + _DET + r"\s+(?:[A-Za-z'\-]+\s+){0,2}?"
    r"(?P<cont>" + _CONT_ALT + r")\s+"
    r"(?:(?:by|in|through|from|with|via)\s+which|whereby)\s+(?P<clause>[A-Za-z][^.;]{2,220})",
    re.IGNORECASE)

# "Dissociation occurs when atoms or groups of atoms break off from molecules"
# WHEN only (not AS / IF): the director's approved scope, and the conservative choice --
# "occurs BECAUSE of the cold temperatures" is an adjunct, not a definition.
_RE_VP4 = re.compile(
    r"(?:^|[,;]\s*|\.\s+)(?:" + _DET + r"\s+)?(?P<dfd>[A-Za-z][A-Za-z '\-]{0,60}?)\s+"
    r"(?:occurs?|occurred|begins?|began|happens?|happened|takes\s+place|took\s+place)\s+"
    r"(?:when|whenever)\s+(?P<clause>[A-Za-z][^.;]{2,220})",
    re.IGNORECASE)

# Demonstrative / pronominal subjects are the dominant VP4 false positive ("This occurs when ...").
_ANAPHORIC_SUBJ = {"this", "that", "these", "those", "it", "they", "there", "he", "she", "we",
                   "which", "what", "such", "one", "some", "both", "each", "all", "another"}

_BE_FORMS = {"is", "are", "was", "were", "be", "been", "being", "am"}
_MODAL_FORMS = {"can", "could", "will", "would", "may", "might", "must", "shall", "should"}
_AUX_HEAD = _BE_FORMS | _MODAL_FORMS | {"have", "has", "had", "do", "does", "did"}
_AUX_SKIP = _AUX_HEAD | {"not", "also", "then", "already", "often", "usually",
                         "therefore", "thus", "subsequently"}
# THE VERB SLOT DOES NOT USE `is_closed_class`. That gate is the FUNCTION-WORD gate, calibrated
# for the genus/meaning slot, and it classes the high-frequency LIGHT VERBS as closed-class:
# is_closed_class('take') == is_closed_class('become') == is_closed_class('move') == True.
# In the genus slot that is right (`X ISA take` is contentless); in the PREDICATE slot those
# verbs ARE the content -- "unspecialized cells BECOME specialized", "a bone MOVES away from
# the midline", "the process of TAKING in food". Applying the meaning-gate here would delete
# the finding this block exists to recover. The verb slot therefore refuses only the genuinely
# contentless auxiliaries below; `is_closed_class` still guards the PATIENT / AGENT noun slots
# (via `definiens_head`), where it is correctly calibrated.
_CONTENTLESS_VERB = _BE_FORMS | _MODAL_FORMS | {"have", "has", "had", "do", "does", "did"}
# Raising / control verbs: "chromatids FAIL TO SEPARATE" -- the content predicate is the infinitive.
_CONTROL_VERB = {"fail", "begin", "start", "continue", "tend", "help", "seem", "appear", "cease",
                 "try", "attempt", "manage", "come", "go"}
# A token in this set to the LEFT of an -ed form makes that form PRENOMINAL ("an INFECTED mammal").
_PRENOMINAL_LEFT = {"a", "an", "the", "this", "that", "these", "those", "its", "their", "his",
                    "her", "our", "any", "each", "every", "one", "some", "many", "most", "all",
                    "both", "several", "other", "such", "no"}
# Particles and prepositions that sit between a verb and its complement head.
_PARTICLE_OR_PREP = {"in", "out", "up", "down", "off", "on", "over", "away", "apart", "together",
                     "back", "into", "onto", "through", "to", "for", "from", "with", "at", "by",
                     "across", "along", "around", "against", "upon", "of", "about", "between",
                     "among", "within", "toward", "towards"}


@dataclass
class PredicateFact:
    """ONE 3-tuple (term, relation, object) read off the predicate of a process definition."""
    term: str
    term_type: str
    relation: str                    # one of PREDICATE_RELATIONS
    object: str                      # verb lemma or complement head lemma
    pattern: str                     # one of PREDICATE_PATTERNS
    definiendum: str = ""
    predicate_span: str = ""         # the clause / of-complement the object was read from
    sentence: str = ""

    def to_dict(self) -> dict:
        return {"term": self.term, "term_type": self.term_type, "relation": self.relation,
                "object": self.object, "pattern": self.pattern,
                "definiendum": self.definiendum, "predicate_span": self.predicate_span,
                "sentence": self.sentence}


def _wn():
    try:
        from nltk.corpus import wordnet as wn
    except Exception:                            # noqa: BLE001 - degraded mode, do not block
        return None
    return wn


def verb_lemma_of(token: str) -> Optional[str]:
    """VERB-sense lemma of a surface token, or None. `lemma_word` cannot be used here: it is the
    NOUN-safe normalizer and leaves `copying`/`breaking`/`taking` unchanged because those are
    themselves WordNet nouns. WordNet's own verb morphy is the right organ and is already
    vendored; when it refuses we fall back to `lemma_word` rather than inventing a stem (the
    module's never-emit-a-non-word rule)."""
    wn = _wn()
    if wn is None:
        return lemma_verb(token)
    got = wn.morphy(token.lower(), "v")
    return got if got else lemma_verb(token)


def is_verbal_lemma(lemma: str) -> bool:
    """True iff WordNet has a VERB sense for `lemma`. Unknown-to-WordNet tokens return False
    here (the opposite of the definiendum gate): asserting an unverifiable predicate is worse
    than refusing one."""
    if not lemma:
        return False
    wn = _wn()
    if wn is None:
        return False
    try:
        return bool(wn.synsets(lemma, pos="v"))
    except Exception:                            # noqa: BLE001
        return False


def _has_noun_sense(lemma: str) -> bool:
    wn = _wn()
    if wn is None:
        return True
    try:
        return bool(wn.synsets(lemma, pos="n"))
    except Exception:                            # noqa: BLE001
        return True


def _looks_plural_noun(token: str) -> bool:
    """Surface plural test. Used ONLY to license a BARE verb form ("cells PRODUCE"), which is
    otherwise indistinguishable from a noun."""
    t = token.lower()
    if len(t) < 4 or not t.endswith("s") or t.endswith("ss") or t.endswith("us"):
        return False
    wn = _wn()
    if wn is None:
        return True
    base = wn.morphy(t, "n")
    if base and base != t:
        return True
    try:                                          # technical plural WordNet has never seen
        return not wn.synsets(t)
    except Exception:                             # noqa: BLE001
        return False


def clause_main_verb(tokens: List[str]) -> Optional[Tuple[int, str]]:
    """(index, verb lemma) of the FINITE main verb of a subordinate clause, or None.

    Six named rules, each of which exists because a real corpus sentence needs it:
      R0 the clause-initial slot is the subject, never the verb   ("WIND moves pieces ...")
      R1 an auxiliary is not the content predicate; skip to what it governs
                                                    ("light energy IS CONVERTED to ...")
      R2 a bare -ing form is non-finite; it is a reduced relative, not the main verb
                                                    ("plant cells CONTAINING chlorophyll produce")
      R3 an -ed form after a determiner is prenominal ("saliva from an INFECTED mammal enters")
      R4 a bare form is only a verb if a plural subject licensed it
                                                    ("chromosome SEGMENT dissociates" is a noun)
      R5 an -s form whose lemma is also a noun needs a nominal immediately to its left
                                                    ("atoms or GROUPS of atoms" is a noun)
      R6 a control verb hands the content over to its infinitive ("FAIL TO SEPARATE" -> separate)
    REFUSING is a legal outcome and is preferred to guessing."""
    n = len(tokens)
    if n < 2:
        return None
    plural_before = [False] * n
    seen = False
    for i in range(n):
        plural_before[i] = seen
        if _looks_plural_noun(tokens[i]):
            seen = True
    i = 1                                          # R0
    while i < n:
        low = tokens[i].lower()
        if low in _AUX_HEAD:
            j = i + 1                              # R1
            while j < n and tokens[j].lower() in _AUX_SKIP:
                j += 1
            if j < n:
                lem = verb_lemma_of(tokens[j])
                if lem and is_verbal_lemma(lem) and lem not in _CONTENTLESS_VERB:
                    return j, lem
            i += 1
            continue
        lem = verb_lemma_of(tokens[i])
        if not lem or not is_verbal_lemma(lem) or lem in _CONTENTLESS_VERB:
            i += 1
            continue
        if low.endswith("ing"):                    # R2
            i += 1
            continue
        prev = tokens[i - 1].lower()
        if low.endswith("ed") and prev in _PRENOMINAL_LEFT:      # R3
            i += 1
            continue
        if low == lem.lower():                     # R4: bare form
            if not plural_before[i]:
                i += 1
                continue
        elif low.endswith("s") and _has_noun_sense(lem):          # R5
            prev_lem = lemma_verb(tokens[i - 1])
            if (prev in _PRENOMINAL_LEFT or is_closed_class(prev_lem)
                    or not is_nominal_lemma(prev_lem)):
                i += 1
                continue
        if lem in _CONTROL_VERB and i + 2 < n and tokens[i + 1].lower() == "to":   # R6
            lem2 = verb_lemma_of(tokens[i + 2])
            if lem2 and is_verbal_lemma(lem2) and lem2 not in _CONTENTLESS_VERB:
                return i + 2, lem2
        return i, lem
    return None


def _complement_head(span: str) -> Optional[str]:
    """Head noun of the NP a verb takes as its complement. Leading particles/prepositions are
    stripped first, because `definiens_head` breaks its leading-NP walk on exactly those tokens
    and would otherwise fall back to the LAST noun of the whole span
    ("taking IN food through the MOUTH" -> `mouth` instead of `food`)."""
    spans = [(m.group(0), m.start()) for m in _TOKEN_RE.finditer(span)]
    k = 0
    while k < len(spans) and spans[k][0].lower() in _PARTICLE_OR_PREP:
        k += 1
    if k >= len(spans):
        return None
    return definiens_head(span[spans[k][1]:])


def _vp1_verbs(rest: str) -> List[Tuple[str, int]]:
    """(verb lemma, char offset just past the verb) for the V-ing head of an of-complement, plus
    any V-ing COORDINATED with it ("the act of SEARCHING for and EXPLOITING food resources" is
    two predicates and must not be silently truncated to the first).
    `of` + a plain noun ("the process of chemiosmosis") has no predicate and REFUSES."""
    spans = [(m.group(0), m.start(), m.end()) for m in _TOKEN_RE.finditer(rest)]
    if not spans or not spans[0][0].lower().endswith("ing"):
        return []
    out: List[Tuple[str, int]] = []
    lem = verb_lemma_of(spans[0][0])
    if not lem or not is_verbal_lemma(lem) or lem in _CONTENTLESS_VERB:
        return []
    out.append((lem, spans[0][2]))
    for k in range(1, min(len(spans), 9) - 1):
        if spans[k][0].lower() not in ("and", "or"):
            continue
        nxt = spans[k + 1][0]
        if not nxt.lower().endswith("ing"):
            continue
        lem2 = verb_lemma_of(nxt)
        if lem2 and is_verbal_lemma(lem2) and lem2 not in _CONTENTLESS_VERB and lem2 != lem:
            out.append((lem2, spans[k + 1][2]))
    return out


def _predicate_term(dfd: str, sentence: str, anaphoric_gate: bool) -> Optional[Tuple[str, str]]:
    """(term, term_type) for a predicate-pattern definiendum, reusing the SAME vetted gates the
    ISA path uses (`_is_nominal_or_unknown`, `build_term`). Nothing new is invented here."""
    toks = _tokens(dfd)
    if not toks:
        return None
    if anaphoric_gate and any(t.lower() in _ANAPHORIC_SUBJ for t in toks):
        return None
    dfd_lemma = lemma_verb(toks[-1])
    if is_closed_class(dfd_lemma) or not _is_nominal_or_unknown(dfd_lemma):
        return None
    return build_term(dfd, sentence)


def extract_predicates(sentence: str) -> List[PredicateFact]:
    """All PREDICATE facts in ONE sentence. Independent of `extract_definitions`: it neither
    calls it nor is called by it, so the ISA fact set is unaffected."""
    if not sentence or len(sentence) < 12:
        return []
    out: List[PredicateFact] = []

    for m in _RE_VP1.finditer(sentence):
        built = _predicate_term(m.group("dfd"), sentence, anaphoric_gate=False)
        if built is None:
            continue
        term, ttype = built
        rest = m.group("rest")
        for lem, off in _vp1_verbs(rest):
            if lem == term.lower():
                continue
            out.append(PredicateFact(term, ttype, "PROCESS_ACTION", lem, "VP1_PROCESS_OF",
                                     m.group("dfd").strip(), rest, sentence))
            pat = _complement_head(rest[off:])
            if pat and pat != lem and pat != term.lower():
                out.append(PredicateFact(term, ttype, "PROCESS_PATIENT", pat, "VP1_PROCESS_OF",
                                         m.group("dfd").strip(), rest, sentence))

    for m in _RE_VP2.finditer(sentence):
        built = _predicate_term(m.group("dfd"), sentence, anaphoric_gate=False)
        if built is None:
            continue
        term, ttype = built
        clause = m.group("clause")
        ctoks = [(t.group(0), t.start(), t.end()) for t in _TOKEN_RE.finditer(clause)]
        hit = clause_main_verb([t[0] for t in ctoks])
        if hit is None:
            continue
        idx, lem = hit
        if lem == term.lower():
            continue
        out.append(PredicateFact(term, ttype, "PROCESS_ACTION", lem, "VP2_BY_WHICH",
                                 m.group("dfd").strip(), clause, sentence))
        pat = _complement_head(clause[ctoks[idx][2]:])
        if pat and pat != lem and pat != term.lower():
            out.append(PredicateFact(term, ttype, "PROCESS_PATIENT", pat, "VP2_BY_WHICH",
                                     m.group("dfd").strip(), clause, sentence))

    for m in _RE_VP4.finditer(sentence):
        built = _predicate_term(m.group("dfd"), sentence, anaphoric_gate=True)
        if built is None:
            continue
        term, ttype = built
        clause = m.group("clause")
        ctoks = [(t.group(0), t.start(), t.end()) for t in _TOKEN_RE.finditer(clause)]
        hit = clause_main_verb([t[0] for t in ctoks])
        if hit is None:
            continue
        idx, lem = hit
        if lem == term.lower():
            continue
        out.append(PredicateFact(term, ttype, "ENABLING_CONDITION", lem, "VP4_OCCURS_WHEN",
                                 m.group("dfd").strip(), clause, sentence))
        agent = definiens_head(clause[:ctoks[idx][1]]) if idx > 0 else None
        if agent and agent != lem and agent != term.lower():
            out.append(PredicateFact(term, ttype, "ENABLING_CONDITION_AGENT", agent,
                                     "VP4_OCCURS_WHEN", m.group("dfd").strip(), clause, sentence))

    seen = set()
    uniq: List[PredicateFact] = []
    for p in out:
        key = (p.term, p.relation, p.object)
        if key in seen:
            continue
        seen.add(key)
        uniq.append(p)
    return uniq


def predicate_candidate_pattern(sentence: str) -> List[str]:
    """Which VP pattern REGEXES fire on this sentence, regardless of whether a fact survives.
    Used to measure per-pattern YIELD RATE (converted / candidates), not for extraction."""
    hits = []
    if _RE_VP1.search(sentence):
        hits.append("VP1_PROCESS_OF")
    if _RE_VP2.search(sentence):
        hits.append("VP2_BY_WHICH")
    if _RE_VP4.search(sentence):
        hits.append("VP4_OCCURS_WHEN")
    return hits


# -------------------------------------------------------------------------------------------
# Self-test (run: python -m hdlab.definitional_extraction)
# -------------------------------------------------------------------------------------------

def _heads_for(sentence: str, definiendum_lemma: str) -> set:
    """Set of genus heads this sentence banks for `definiendum_lemma`. The FACT SET uses the
    HEAD, so regressions must be asserted on the head -- links(...) also matches at SPAN level
    (any word inside the definiens) and would mask a head fix."""
    return {d.head for d in extract_definitions(sentence)
            if d.definiendum_lemma == definiendum_lemma}


def _self_test() -> None:
    pos: List[Tuple[str, str, str]] = [
        ("Renal artery: the artery that delivers blood to the kidney",
         "arteri", "arteri"),   # head==definiendum -> collapses; checked separately below
    ]
    del pos

    # GLOSSARY_COLON
    ds = extract_definitions("nephron: the functional unit of the kidney")
    assert any(d.pattern == "GLOSSARY_COLON" and d.definiendum_lemma == "nephron"
               and d.head == "unit" for d in ds), ds

    # COPULA
    ds = extract_definitions("A nephron is the functional unit of the kidney.")
    assert any(d.definiendum_lemma == "nephron" and d.head == "unit" for d in ds), ds

    # APPOSITIVE
    ds = extract_definitions("The mitochondrion, an organelle of the cell, makes energy.")
    assert any(d.definiendum_lemma == "mitochondrion" and d.head == "organelle"
               for d in ds), ds

    # CALLED
    ds = extract_definitions("This tiny filtering structure is called the nephron.")
    assert any(d.definiendum_lemma == "nephron" for d in ds), ds

    # REFERS_TO
    ds = extract_definitions("Photosynthesis refers to the capture of light energy by plants")
    assert any(d.definiendum_lemma == "photosynthesis" for d in ds), ds

    # NEGATIVE: pure co-occurrence prose must NOT yield a definition linking the pair
    neg = ("The key moment for Northumberland came in 2013 when the entire national park got "
           "Dark Sky Park status")
    assert links(neg, "sky", "statu") is None, extract_definitions(neg)
    neg2 = "The increase will put more pressure on agricultural land, water, forests and nutrients"
    assert links(neg2, "nutrient", "pressure") is None, extract_definitions(neg2)

    # links() positive
    s = "A nephron is the functional unit of the kidney"
    assert links(s, "nephron", "unit") == "COPULA:HEAD", links(s, "nephron", "unit")
    assert links(s, "nephron", "kidney") == "COPULA:SPAN", links(s, "nephron", "kidney")

    # head must never be a closed-class word
    for s in ("A widget is the thing that we use",
              "A quark is a kind of particle"):
        for d in extract_definitions(s):
            assert not is_closed_class(d.head or "x"), (s, d)

    # --- REGRESSION: the three false-positive classes measured on the real corpus 2026-08-12 ---
    # (a) COORDINATE LIST must not read as an appositive definition
    s = "The lower limb consists of the thigh, the leg, and the foot"
    assert links(s, "thigh", "leg") is None, extract_definitions(s)
    # (b) FRONTED PP must not read as an appositive definition
    s = ("In addition, the wide range of topics, data, and legal circumstances in sociology "
         "change frequently")
    assert links(s, "addition", "range") is None, extract_definitions(s)
    # (c) a mid-sentence colon after a full clause is not a glossary line
    s = ("Prokaryotic DNA is found in the central part of the cell: a darkened region called "
         "the nucleoid")
    assert links(s, "cell", "nucleoid") is None, extract_definitions(s)
    # (d) CALLED must take the NP HEAD, not the leading modifier
    s = "The entirety of this process is called oxidative phosphorylation"
    heads = {d.definiendum_lemma for d in extract_definitions(s)}
    assert "phosphorylation" in heads, heads
    assert "oxidative" not in heads, heads
    # (e) post-nominal modifier must not be taken as the genus head ("present" is not the genus)
    s = "vestigial structure: a physical feature present in an organism but with no function"
    ds = [d for d in extract_definitions(s) if d.pattern == "GLOSSARY_COLON"]
    assert ds and ds[0].head == "feature", ds
    # (e2) head == definiendum collapses to a tautology and MUST be refused, not banked
    s2 = "vestigial structure: a physical structure present in an organism"
    assert all(d.head != d.definiendum_lemma for d in extract_definitions(s2))
    # (g) a definiendum must be NOMINAL: adverbs and pure verbs are not definable this way
    s = ("Additionally, the gradual melting and refreezing of the poles, glaciers and ice "
         "sheets, occurred")
    assert links(s, "additionally", "melting") is None, extract_definitions(s)
    s = "While this might sound like an exaggeration, the threat was actually severe"
    assert all(d.definiendum_lemma != "exaggeration" for d in extract_definitions(s)),         extract_definitions(s)
    # ...but out-of-WordNet technical terms and proper nouns MUST still pass
    s = "Arthropoda is the largest phylum in the animal world"
    assert links(s, "arthropoda", "phylum") == "COPULA:HEAD", extract_definitions(s)

    # (f) real bio definitions still survive all the guards
    for s, subj, obj in (
            ("Cholesterol is a lipid that contributes to cell membrane flexibility",
             "cholesterol", "lipid"),
            ("The aorta is the major artery of the body, taking oxygenated blood to the organs",
             "aorta", "artery"),
            ("Arthropoda is the largest phylum in the animal world", "arthropoda", "phylum"),
            ("Gene therapy is a genetic engineering technique that may cure diseases",
             "therapy", "technique")):
        assert links(s, subj, obj) == "COPULA:HEAD", (s, extract_definitions(s))

    # === v4 PARSE-FAULT REGRESSIONS (2026-08-12) ==============================================
    # Each case below is a REAL ROW from data/foundation/reading_grounding_v3_definitional/
    # definitional_facts.jsonl that the director hand-scored NOISE or RELATED. The assertion is
    # the fixed behaviour; the comment records the v3 output being corrected.

    # F5a: adjective head. v3 gave `dialysis -> medical` because `process` was excluded from the
    # candidate list, leaving the adjective as the last "strong" token.
    s = ("Dialysis is a medical process of removing wastes and excess water from the blood by "
         "diffusion and ultrafiltration")
    assert _heads_for(s, "dialysis") == {"process"}, extract_definitions(s)

    # F5a: adjective-only heads are refused outright rather than emitted.
    assert definiens_head("a moist") is None
    assert definiens_head("a harder") is None
    assert definiens_head("a moist, permeable skin") == "skin"

    # F5b: partitive head. v3 gave `kidney -> pair`.
    s = ("The kidneys are a pair of bean-shaped structures that are located just below the liver "
         "in the body cavity")
    assert _heads_for(s, "kidney") == {"structure"}, extract_definitions(s)
    assert definiens_head("a group of multicellular Eukarya") == "eukarya"
    assert definiens_head("a class of drugs that modulate neurotransmitters") == "drug"
    # ...but a RELATIONAL noun with a DEFINITE of-complement is NOT a partitive: a nephron is a
    # unit, it is not a kidney. This determiner test is the whole rule and must not regress.
    assert definiens_head("the functional unit of the kidney") == "unit"

    # F4: polarity inversion. v3 gave `structure -> function` from a sentence asserting the
    # ABSENCE of function; with `without` as an NP boundary the head becomes `structure`, which
    # equals the definiendum and is refused as a tautology.
    s = "These unused structures without function are called vestigial structures"
    assert _heads_for(s, "structure") == set(), extract_definitions(s)
    assert definiens_head("These unused structures without function") == "structure"

    # F2a: enumeration verb + bare-NP "definiens" = list item. v3 gave `kidney -> ureter`.
    s = ("Here we focus on the urinary system, which is comprised of the paired kidneys, the "
         "ureter, urinary bladder and urethra")
    assert _heads_for(s, "kidney") == set(), extract_definitions(s)
    # ...and the guard must not cost the known-good rows: this is the REAL corpus sentence
    # behind `aorta -> artery`, which the loose F2 detector wrongly suspected.
    s = ("The aorta is the major artery of the body, taking oxygenated blood to the organs and "
         "muscles of the body")
    assert "artery" in _heads_for(s, "aorta"), extract_definitions(s)

    # F2c: CALLED definiens that is the last item of a comma list. v3 gave `system -> locomotion`.
    s = ("Echinoderms have a unique system for gas exchange, nutrient circulation, and "
         "locomotion called the water vascular system")
    assert _heads_for(s, "system") == set(), extract_definitions(s)
    # ...but a leading conjunction that is mere noise must be STRIPPED, not used to drop a good
    # fact: v3's `arteriole -> vessel` is correct and must survive.
    s = ("The major arteries diverge into minor arteries, and then smaller vessels called "
         "arterioles, to reach more deeply into the muscles")
    assert _heads_for(s, "arteriole") == {"vessel"}, extract_definitions(s)

    # F6: glossary run-on -- one "sentence" holding many `term: definition` entries. v3 let a
    # definiens run into the NEXT entry (`effect -> magnification` from bottleneck+founder).
    block = ("bottleneck effect: the magnification of genetic drift as a result of natural "
             "events or catastrophes founder effect: a magnification of genetic drift in a "
             "small population")
    assert len(split_glossary_entries(block)) >= 2, split_glossary_entries(block)
    assert split_glossary_entries("A nephron is the functional unit of the kidney") == [
        "A nephron is the functional unit of the kidney"]

    # F3: subject truncation. v3 stored only the head lemma of a multiword term.
    def _terms(sentence):
        return {(d.term, d.term_type, d.head) for d in extract_definitions(sentence)}
    assert ("transcription bubble", "COMMON", "region") in _terms(
        "The region of unwinding is called a transcription bubble"), _terms(
        "The region of unwinding is called a transcription bubble")
    assert ("age structure", "COMMON", "proportion") in _terms(
        "Age structure is the proportion of a population in different age classes")
    # F3b: a run-on COPULA subject is not a term at all. v3 banked `cancer -> collective` from
    # a definiendum span reading "and are surrounded by new nuclear envelopes Cancer".
    assert build_term("and are surrounded by new nuclear envelopes Cancer", "x") is None
    assert build_term("An important characteristic of extant amphibians", "x") == (
        "important characteristic", "COMMON")

    # F1: proper-noun / common-noun collision. v3 banked `fan -> expert` (a SURNAME) and
    # `technology -> seller` (the head token of an ORG name) onto the common nouns.
    s = ("You can offset the electricity used for air conditioning, said Shanhui Fan, an expert "
         "in the study of light at Stanford University, who led the development of the mirror")
    got = _terms(s)
    assert ("Shanhui Fan", "PROPER", "expert") in got, got
    assert not any(t == "fan" for t, _ty, _h in got), got
    s = ("Pizzi, who is now CEO of Currie Technologies, the number one seller of e-bikes in the "
         "US, believes thats about to change")
    got = _terms(s)
    assert ("Currie Technologies", "PROPER", "seller") in got, got
    assert not any(t == "technology" for t, _ty, _h in got), got
    # ...and proper nouns are NOT dropped: a real proper-noun definition survives, typed PROPER
    s = "I would dock in Piraeus, the port in Athens, take my pay, then get the first boat over"
    assert ("Piraeus", "PROPER", "port") in _terms(s), _terms(s)
    s = "Eye color in Drosophila, the common fruit fly, was the first X-linked trait identified"
    assert ("Drosophila", "PROPER", "fly") in _terms(s), _terms(s)
    # a sentence-INITIAL capital is not evidence of a name
    assert build_term("Dialysis", "Dialysis is a medical process of removing wastes") == (
        "dialysis", "COMMON")

    # === v5 TERM-BOUNDARY REGRESSIONS (2026-08-12) ============================================
    # Every case below is a REAL v4 row from
    # data/foundation/reading_grounding_v4_parsefix/definitional_facts_v4.jsonl.

    # --- F7: a term may not cross PUNCTUATION -------------------------------------------------
    # v4 merged across a comma because the proper-name walk ran over the TOKEN list.
    s = "Like DNA, RNA is a polymer of nucleotides"
    assert not any(t == "DNA RNA" for t, _ty, _h in _terms(s)), _terms(s)
    s = ("At the 1985 Live Aid famine relief concert at Wembley Stadium, Bowie was one of the "
         "best performers")
    assert not any(t.startswith("Wembley") for t, _ty, _h in _terms(s)), _terms(s)
    s = ("The money made broadcasting the London Olympics was almost enough to pay for a mission "
         "to Mars, Bas Lansdorp, the company's founder, said")
    assert not any(t.startswith("Mars") for t, _ty, _h in _terms(s)), _terms(s)
    assert _gap_is_clean("Ban Ki-moon said", 0, 0) is True
    assert _expand_proper_name("RNA", "Like DNA, RNA is a polymer")[0] == "RNA"

    # --- F8: a term may not cross a GLOSSARY ENTRY BOUNDARY -----------------------------------
    # v4 absorbed up to three words of the PREVIOUS entry's definiens into the next term.
    blk = ("ecosystem: a community of living organisms and their interactions with their abiotic "
           "environment equilibrium: the steady state of a system in which the relationships "
           "between elements of the system do not change")
    got = set()
    for seg in split_glossary_entries(blk):
        got |= {d.term for d in _extract_one(seg)}
    assert not any(t and "abiotic" in t and "equilibrium" in t for t in got), got
    blk2 = ("autotroph: an organism capable of synthesizing its own food molecules from smaller "
            "inorganic molecules apex consumer: an organism at the top of the food chain "
            "biomagnification: an increasing concentration of persistent toxic substances")
    got = set()
    for seg in split_glossary_entries(blk2):
        got |= {d.term for d in _extract_one(seg)}
    assert not any(t and t.startswith("apex consumers") for t in got), got
    # ...and a LINE-AWARE (one entry per sentence) glossary entry keeps its FULL multiword term,
    # which is the whole reason the run-on split is allowed to be under-specific.
    assert ("absorption spectrum", "COMMON", "pattern") in _terms(
        "absorption spectrum: the specific pattern of absorption for a substance"), _terms(
        "absorption spectrum: the specific pattern of absorption for a substance")
    assert ("bottleneck effect", "COMMON", "magnification") in _terms(
        "bottleneck effect: the magnification of genetic drift as a result of natural events")

    # --- F1 GAINS MUST NOT REGRESS ------------------------------------------------------------
    # The v4 proper-noun fix is the one thing the director confirmed WORKED. Each row below is a
    # v4 fact the director hand-scored correct; the v5 boundary fix must leave all of them intact.
    F1_GAINS = [
        ("Pate K Chon, a counsellor who works with HIV sufferers in Liberia, provided a "
         "surprising solution", "Chon", "counsellor"),
        ("Furqan Naeem, a campaigner from Manchester, said: I recently visited the United States",
         "Naeem", "campaigner"),
        ("Cathy Olkin, a mission scientist, said: Charon just blew our socks off",
         "Olkin", "scientist"),
        ("Hariharan Rajagopalan, 18, Boston, Massachusetts Rajagopalan, a student at Boston "
         "College, doesnt see any problem with not using social media", "Rajagopalan", "student"),
        ("You can offset the electricity used for air conditioning, said Shanhui Fan, an expert "
         "in the study of light at Stanford University, who led the development of the mirror",
         "Shanhui Fan", "expert"),
        ("Pizzi, who is now CEO of Currie Technologies, the number one seller of e-bikes in the "
         "US, believes thats about to change", "Currie Technologies", "seller"),
        ("I would dock in Piraeus, the port in Athens, take my pay, then get the first boat over",
         "Piraeus", "port"),
        ("Eye color in Drosophila, the common fruit fly, was the first X-linked trait identified",
         "Drosophila", "fly"),
    ]
    for s, term, head in F1_GAINS:
        assert (term, "PROPER", head) in _terms(s), (term, head, _terms(s))
    # ...and the v3 common-noun COLLISIONS the F1 fix removed must stay removed.
    s = ("You can offset the electricity used for air conditioning, said Shanhui Fan, an expert "
         "in the study of light at Stanford University, who led the development of the mirror")
    assert not any(t == "fan" for t, _ty, _h in _terms(s)), _terms(s)
    s = ("Pizzi, who is now CEO of Currie Technologies, the number one seller of e-bikes in the "
         "US, believes thats about to change")
    assert not any(t == "technology" for t, _ty, _h in _terms(s)), _terms(s)

    # === 2026-08-13 VP-PREDICATE (ADDITIVE) ===================================================
    # Every sentence below is a REAL corpus sentence quoted with provenance in
    # notes/verb_definition_gap_2026-08-13.md. The ISA assertions above are UNCHANGED; these
    # only assert the NEW read-out and that it did not disturb the old one.
    def _pf(sentence):
        return {(p.relation, p.object) for p in extract_predicates(sentence)}

    def _terms_pf(sentence):
        return {p.term for p in extract_predicates(sentence)}

    # --- ADDITIVITY: the ISA fact must still be there when a predicate is also emitted --------
    s = "Hydrolysis is the process of breaking complex macromolecules apart"
    assert _heads_for(s, "hydrolysis") == {"process"}, extract_definitions(s)
    assert ("PROCESS_ACTION", "break") in _pf(s), _pf(s)
    assert "hydrolysis" in _terms_pf(s), _terms_pf(s)

    # --- VP1 PROCESS_OF -----------------------------------------------------------------------
    s = "Transcription is the process of copying the information in a cell's DNA into mRNA"
    assert ("PROCESS_ACTION", "copy") in _pf(s), _pf(s)
    assert ("PROCESS_PATIENT", "information") in _pf(s), _pf(s)
    s = "Ingestion is the process of taking in food through the mouth"
    # the leading particle must be stripped, else the complement head is `mouth`
    assert ("PROCESS_PATIENT", "food") in _pf(s), _pf(s)
    s = "Foraging is the act of searching for and exploiting food resources"
    got = {o for r, o in _pf(s) if r == "PROCESS_ACTION"}
    assert got == {"search", "exploit"}, got        # coordination is not truncated to the first
    # `of` + a plain NOUN has no predicate and must REFUSE rather than take the noun
    s = "The production of ATP is the process of chemiosmosis"
    assert not any(r == "PROCESS_ACTION" for r, _o in _pf(s)), _pf(s)

    # --- VP2 BY_WHICH -------------------------------------------------------------------------
    s = ("Differentiation is the process by which unspecialized cells become specialized to "
         "carry out distinct functions")
    assert ("PROCESS_ACTION", "become") in _pf(s), _pf(s)
    s = ("Ammonification is the process by which ammonium ion is released from decomposing "
         "organic compounds")
    assert ("PROCESS_ACTION", "release") in _pf(s), _pf(s)   # R1: skip the passive auxiliary
    s = ("Photosynthesis is the process by which plant cells containing chlorophyll produce "
         "food substances from carbon dioxide and water")
    assert ("PROCESS_ACTION", "produce") in _pf(s), _pf(s)   # R2: skip the reduced relative
    s = "Hemostasis is the physiological process by which bleeding ceases"
    assert ("PROCESS_ACTION", "cease") in _pf(s), _pf(s)     # one intervening modifier

    # --- VP4 OCCURS_WHEN: an ENABLING_CONDITION, never an ISA ---------------------------------
    s = "Dissociation occurs when atoms or groups of atoms break off from molecules and form ions"
    got = _pf(s)
    assert ("ENABLING_CONDITION", "break") in got, got       # R5: `groups` is a noun, not the verb
    assert ("ENABLING_CONDITION_AGENT", "atom") in got, got
    assert not any(r in ("PROCESS_ACTION", "PROCESS_PATIENT") for r, _o in got), got
    s = "Abduction occurs when a bone moves away from the midline of the body"
    assert ("ENABLING_CONDITION", "move") in _pf(s), _pf(s)
    s = ("Nondisjunction occurs when homologous chromosomes or sister chromatids fail to "
         "separate during meiosis")
    assert ("ENABLING_CONDITION", "separate") in _pf(s), _pf(s)   # R6: control verb
    s = "Behavioral isolation occurs when the presence or absence of a specific behavior prevents reproduction"
    assert ("ENABLING_CONDITION", "prevent") in _pf(s), _pf(s)
    # R3 (`infected` is a prenominal participle, not the main verb) asserted at the walk, because
    # the sentence-level definiendum of the real corpus row [BIO:8622] "Rabies transmission
    # occurs when saliva from an infected mammal enters a wound" is refused UPSTREAM by the
    # SHIPPED gate -- is_closed_class('transmission') is True, so the ISA path refuses it too.
    assert clause_main_verb(
        _tokens("saliva from an infected mammal enters a wound")) == (5, "enter"), (
        clause_main_verb(_tokens("saliva from an infected mammal enters a wound")))
    assert extract_predicates(
        "Rabies transmission occurs when saliva from an infected mammal enters a wound") == []
    # ANAPHORIC subject must be refused -- it names no term
    for s in ("This occurs when the temperature drops",
              "It occurs when the membrane depolarizes",
              "That happens when the cells divide"):
        assert extract_predicates(s) == [], extract_predicates(s)
    # a non-`when` adjunct is not a definition and must not match
    s = "Little evaporation occurs because of the cold temperatures"
    assert extract_predicates(s) == [], extract_predicates(s)

    # --- the clause walk REFUSES rather than guessing ------------------------------------------
    assert clause_main_verb(["the", "cold", "dark", "winter", "sky"]) is None
    assert clause_main_verb(["light"]) is None
    # R0: the clause-initial token is the subject even when it has a verb sense
    assert clause_main_verb(["wind", "moves", "pieces", "of", "earth"]) == (1, "move")
    # R4: a bare form with no plural subject is a noun
    assert clause_main_verb(["one", "chromosome", "segment", "dissociates"]) == (3, "dissociate")

    # --- the ISA path is byte-untouched: a definition with NO predicate reads exactly as before
    s = "A nephron is the functional unit of the kidney"
    assert links(s, "nephron", "unit") == "COPULA:HEAD", extract_definitions(s)
    assert extract_predicates(s) == [], extract_predicates(s)

    print("[definitional_extraction] self-test PASS")
    _called_boundary_self_test()


# ===========================================================================================
# CALLED ANTECEDENT BOUNDARY (v7, 2026-08-13). Scope: the CALLED pattern ONLY.
#
# MEASURED@data/exp_definitional_predicate_v6/metrics.json (`called_left_boundary_diagnostic`),
# over 1,622 banked CALLED facts on biology_2e + anatomy_physiology_2e + psychology_2e:
#   L1 antecedent opens with a function word          182
#   L2 antecedent swallows a finite verb              534
#   L3 antecedent truncated mid-phrase                 36
#   -> 668 (41.2%) wrong LEFT BOUNDARY
#   L4 head is not the constituent adjacent to trigger 851 (52.5%), measured separately
#
# WHY. `_RE_CALLED`'s antecedent group is `[A-Za-z][A-Za-z '\-]{2,120}?` -- a character class
# that stops only at punctuation/digits, with a 120-char cap. `finditer` takes the LEFTMOST
# viable start, so the "antecedent" is everything from the last comma/paren/digit (or 120 chars
# back, mid-word) up to the naming verb. That is not a constituent; it is a window. Real
# failures it produced: `fermentation ISA nadh`, `impurity ISA mold`.
#
# THE FIX IS NOT A WIDER REGEX. The antecedent is located by walking LEFT from the naming
# trigger over the sentence's own token spans to a real constituent boundary. Two INDEPENDENT
# changes, switchable so each can be measured alone (experiments/exp_called_boundary_v7.py):
#
#   A = CALLED_FIX_LEFT   WHICH SPAN is the antecedent.
#       Walk left from the trigger; stop BEFORE a finite verb, a clause coordinator, any
#       punctuation gap, or the sentence start; then iteratively drop leading tokens that
#       cannot START an English NP (prepositions, relativizers, subordinators, coordinators,
#       non-nominal -ly adverbs). Head rule unchanged: `definiens_head` over that span.
#
#   B = CALLED_FIX_HEAD   WHICH SUB-CONSTITUENT the head is read from.
#       `definiens_head` returns the head of the LEADING NP. That is right when the antecedent
#       is linked to the name by a COPULA ("the liquid-filled space surrounding the granum IS
#       called stroma" -> `space`, not `granum`), because the copula makes the whole subject NP
#       the antecedent. It is wrong for a REDUCED RELATIVE ("a passage through a specialized
#       protein channel called the ATP synthase" -> the naming attaches LOW, to `channel`, not
#       to `passage`). So: low attachment ONLY when there is no copula link AND the intervening
#       post-modifier is NOT an of-complement. The `of` carve-out is deliberate and
#       conservative -- it is what keeps "a region OF THE CELL called the nucleoid" reading
#       `region` (low attachment there would resurrect the `cell -> nucleoid` regression that
#       `_RE_COLON` was tightened to kill) and "a branch OF BIOLOGY called virology" reading
#       `branch`. When in doubt B does nothing.
#
# REFUSAL IS A FIRST-CLASS OUTCOME. If the walk cannot reach nominal material -- "...NAD+ from
# NADH are collectively referred to as fermentation", where everything left of the trigger is
# an adverb and then a finite verb -- this returns None and NO fact is emitted. A dropped fact
# beats `fermentation ISA nadh`.
#
# NO PARSER, same reason as the VP block above: hdlab.pos_tagger mis-tags OpenStax prose. This
# is a stack of named surface rules over token spans, in the style of `definiens_head`.
# ===========================================================================================

# Experiment ablation switches. BOTH DEFAULT ON = shipped behaviour. They exist so A and B can
# be attributed separately; nothing in hdlab/ reads them except this block.
CALLED_FIX_LEFT = True
CALLED_FIX_HEAD = True

# Finite verbs the antecedent walk must never cross. SUPERSET of the L2 detector's set in
# experiments/exp_definitional_predicate_v6.py (so L2 goes to zero BY CONSTRUCTION -- stated
# plainly rather than presented as an independent confirmation), plus the remaining auxiliaries
# and copula forms. Ambiguous noun/verb forms (`use`, `cause`, `form`, `produce`) are
# DELIBERATELY ABSENT: stopping on them would cut real NPs ("the use of oxygen").
_CB_FINITE_VERB = {
    "is", "are", "was", "were", "has", "have", "had", "does", "do", "did",
    "can", "will", "would", "means", "becomes", "become", "includes", "include",
    "consists", "consist", "occurs", "occur",
    "be", "been", "being", "may", "might", "could", "should", "must", "shall",
    "said", "says", "cannot",
}

# Clause-level coordinators. `_NP_BOUNDARY` already treats these as NP-enders; the walk stops
# before them so an antecedent can never span two coordinated clauses.
_CB_COORD = {"and", "or", "but", "nor"}

# Tokens that cannot be the FIRST token of an English NP. SUPERSET of the L1 detector's set
# (again: L1 goes to zero by construction).
_CB_CANNOT_START_NP = {
    "of", "in", "on", "for", "to", "with", "from", "into", "onto", "at", "as", "by", "between",
    "among", "through", "during", "within", "across", "over", "under", "and", "or", "but",
    "that", "which", "who", "whom", "whose", "where", "when", "while", "because", "if", "than",
    "such", "then", "also", "however", "therefore", "thus", "so",
    "nor", "although", "though", "since", "unless", "whereas", "about", "against", "around",
    "before", "after", "toward", "towards", "upon", "via", "per", "until",
}

# Negation / exclusion cues. If the span's left edge lands ON one of these, the head sits inside
# the negator's scope and the real head was cut off by the hard boundary -> REFUSE. (Trimming
# instead would resurrect the v4 F4 fault: "structures WITHOUT function" -> `... ISA function`.)
_CB_NEG_EDGE = {"without", "lacking", "lack", "lacks", "no", "not", "non", "never", "absent",
                "absence", "except", "excluding", "unlike", "rather", "instead", "minus",
                "sans", "neither"}

# Determiners / possessives: an NP's LEFT EDGE. The minimal-NP walk (B) stops INCLUSIVELY here.
_CB_DETERMINER = {"a", "an", "the", "this", "that", "these", "those", "its", "their", "his",
                  "her", "our", "your", "my", "any", "each", "every", "one", "some", "all",
                  "both", "several", "many", "few", "other", "another"}

# Post-modifier OPENERS: walking left, these mean the material to their right is a modifier and
# the head lies further left. Used by the minimal-NP walk (B) as an exclusive stop. The
# closed set is the module's OWN `_NP_BOUNDARY` plus the remaining prepositions; participles are
# recognised MORPHOLOGICALLY (`_cb_is_postmod_opener`) rather than by an example-fitted list.
_CB_POSTMOD_CLOSED = (set(_NP_BOUNDARY) | _CB_NEG_EDGE
                      | {"around", "against", "about", "toward", "towards", "upon", "via",
                         "than", "before", "after", "until", "per"})

_CB_NAMING = re.compile(r"(?:called|known\s+as|termed|named|referred\s+to\s+as)", re.IGNORECASE)
_CB_BE = {"is", "are", "was", "were"}
_CB_MAX_WALK = 25
_CB_MAX_NP = 8


@dataclass
class CalledAntecedent:
    """The constituent-bounded antecedent of one CALLED match."""
    definiens: str              # what is RECORDED as the definiens span
    head_span: Optional[str]    # sub-span the genus head is read from (None = read from definiens)
    start: int                  # char offset of `definiens` in the sentence
    end: int
    be_linked: bool             # True = "<NP> is/are/was/were called X" (copula link)
    mode: str                   # BE_LINKED | REDUCED_RELATIVE
    reason: str                 # OK, or the named refusal


def _cb_is_adverbial(tok: str) -> bool:
    """A leading -ly token that WordNet does not know as a noun is an adverb, not the NP head.
    `collectively`/`simply` are trimmed; `family`/`assembly`/`supply` are not."""
    low = tok.lower()
    if low in ("also", "often", "sometimes", "generally", "usually", "commonly", "now", "then"):
        return True
    return low.endswith("ly") and not is_nominal_lemma(lemma_verb(tok))


def _cb_is_finite_verb(tok: str) -> bool:
    """Finite verb the antecedent walk must not cross. The closed list covers the auxiliaries
    and copulas; 3sg present forms are caught MORPHOLOGICALLY so the list does not have to be
    grown one textbook sentence at a time. `contains` is a verb (`contain` has no noun sense);
    `amounts`, `processes`, `cells` are plural NOUNS and must NOT stop the walk -- that is what
    `_looks_plural_noun`, already owned by this module, decides."""
    low = tok.lower()
    if low in _CB_FINITE_VERB:
        return True
    if not low.endswith("s"):
        return False
    lem = verb_lemma_of(tok)
    return lem is not None and lem != low and not _looks_plural_noun(tok)


def _cb_is_postmod_opener(tok: str) -> bool:
    """Walking LEFT, does this token open a POST-modifier (so the head lies further left)?
    Closed set = the module's own `_NP_BOUNDARY` + the remaining prepositions. Participles are
    recognised morphologically -- an -ing/-ed form with a verb sense and no noun sense -- rather
    than by a list fitted to the examples this fix was written against."""
    low = tok.lower()
    if low in _CB_POSTMOD_CLOSED:
        return True
    if low.endswith("ing") or low.endswith("ed"):
        lem = verb_lemma_of(tok)
        # `lem != low` is load-bearing: `verb_lemma_of` echoes back tokens WordNet does not
        # know, so without it `liquid-filled` and `unused` read as participles.
        return lem is not None and lem != low and is_verbal_lemma(lem)
    return False


def _cb_peelable_postmod(spans, i: int, upto: int) -> bool:
    """Is the opener at `spans[i]` a POST-nominal modifier (head lies further left) rather than
    a PRE-nominal one? Prepositions and relativizers always are. A participle is post-nominal
    only when it takes its own NP object -- "surrounding THE granum" does, "filtering structure"
    and "specialized protein channel" do not, and peeling those would eat the head."""
    low = spans[i][0].lower()
    if low in _CB_POSTMOD_CLOSED:
        return True
    if not _cb_is_postmod_opener(spans[i][0]):
        return False
    return any(spans[j][0].lower() in _CB_DETERMINER for j in range(i + 1, upto + 1))


def _cb_minimal_np_left(sentence: str, spans, left: int, right_i: int) -> int:
    """Index of the left edge of the NP whose head is `spans[right_i]`: walk left through
    NP-internal material, stop INCLUSIVELY at a determiner, EXCLUSIVELY at a modifier opener,
    a finite verb, a coordinator or a punctuation gap."""
    np_left = right_i
    steps = 0
    while np_left - 1 >= left and steps < _CB_MAX_NP:
        steps += 1
        if spans[np_left][0].lower() in _CB_DETERMINER:
            break                                   # determiner = NP left edge, inclusive
        prev = spans[np_left - 1]
        if not _gap_is_clean(sentence, prev[2], spans[np_left][1]):
            break
        if (_cb_is_postmod_opener(prev[0]) or _cb_is_finite_verb(prev[0])
                or prev[0].lower() in _CB_COORD):
            break
        np_left -= 1
    return np_left


def _cb_is_infinitival_to(spans, i: int) -> bool:
    """`to` + a BARE verb form = an infinitival clause boundary ("to form structures"), as
    opposed to the preposition `to` ("attached to the membrane")."""
    if spans[i][0].lower() != "to" or i + 1 >= len(spans):
        return False
    nxt = spans[i + 1][0]
    lem = verb_lemma_of(nxt)
    return lem is not None and lem == nxt.lower()


def _cb_called_antecedent_core(sentence: str, m: "re.Match", dfs_text: str):
    """(CalledAntecedent | None, reason). Split out so the refusal reason is countable."""
    spans = _sentence_token_spans(sentence)
    if not spans:
        return None, "NO_TOKENS"
    mm = _CB_NAMING.search(sentence, m.end("dfs"), m.start("dfd"))
    trigger_at = mm.start() if mm else m.end("dfs")

    # right edge of the antecedent: skip back over the trigger's own adverbs and its copula
    right = -1
    for i, (_t, _s, e) in enumerate(spans):
        if e <= trigger_at:
            right = i
        else:
            break
    if right < 0:
        return None, "NO_TOKEN_LEFT_OF_TRIGGER"
    be_linked = False
    guard = 0
    while right >= 0 and guard < 4:
        guard += 1
        tok = spans[right][0]
        if _cb_is_adverbial(tok):
            right -= 1
            continue
        if tok.lower() in _CB_BE:
            be_linked = True
            right -= 1
            continue
        break
    if right < 0:
        return None, "ONLY_TRIGGER_MATERIAL_LEFT_OF_TRIGGER"

    # ---- A: left edge --------------------------------------------------------------------
    if CALLED_FIX_LEFT:
        left = right
        steps = 0
        while left - 1 >= 0 and steps < _CB_MAX_WALK:
            steps += 1
            prev = spans[left - 1]
            if not _gap_is_clean(sentence, prev[2], spans[left][1]):
                break                                   # punctuation is a hard boundary
            low = prev[0].lower()
            if _cb_is_finite_verb(prev[0]) or low in _CB_COORD:
                break
            # An infinitival clause boundary is a hard stop for a REDUCED RELATIVE (the
            # antecedent is the adjacent NP, and `to form ...` is outside it). Under a COPULA
            # link the antecedent is the whole subject NP, which may legitimately contain an
            # infinitival complement ("the ability TO MOVE is called motility"), so it is not.
            if not be_linked and _cb_is_infinitival_to(spans, left - 1):
                break
            left -= 1
        # A token that cannot START an English NP is not the left edge -- it is material the
        # walk stopped inside. A NEGATOR at the edge is different: the head it modifies is on
        # the far side of the hard boundary, so trimming would bank a word whose ABSENCE the
        # sentence asserts (the v4 F4 fault). That case REFUSES.
        while left <= right:
            tok = spans[left][0]
            if tok.lower() in _CB_NEG_EDGE:
                return None, "REFUSE_LEFT_EDGE_IN_NEGATION_SCOPE"
            if (tok.lower() in _CB_CANNOT_START_NP or _cb_is_adverbial(tok)
                    or _cb_peelable_postmod(spans, left, right)):
                if be_linked:
                    # A COPULA antecedent is a CLAUSE SUBJECT. If the walk stopped inside a PP
                    # or a reduced relative, the subject is unreachable and there is nothing
                    # honest to emit: "...NAD+ from NADH are collectively referred to as
                    # fermentation" would otherwise trim `from` and bank `fermentation ISA nadh`.
                    return None, "REFUSE_COPULA_SUBJECT_UNREACHABLE"
                left += 1
                continue
            break
        if left > right:
            return None, "REFUSE_NO_NP_MATERIAL"
        start, end = spans[left][1], spans[right][2]
        span_text = sentence[start:end]
    else:
        idx = sentence.find(dfs_text, m.start("dfs"))
        start = idx if idx >= 0 else m.start("dfs")
        end = start + len(dfs_text)
        span_text = dfs_text
        left = 0
        for i, (_t, s_, _e) in enumerate(spans):
            if s_ >= start:
                left = i
                break

    # ---- B: which sub-constituent supplies the head ---------------------------------------
    head_span = None
    if CALLED_FIX_HEAD and be_linked:
        # COPULA LINK: the antecedent is the whole subject NP, so the head is that NP's head --
        # `stroma`'s antecedent is "the liquid-filled space surrounding the granum" and its head
        # is `space`, NOT the trigger-adjacent `granum`. `definiens_head` alone gets this wrong
        # whenever the post-modifier's opener is missing from `_NP_BOUNDARY` (`surrounding` is),
        # so peel trailing POST-modifiers off explicitly instead of relying on that list.
        r = right
        np_left = right
        for _ in range(4):
            np_left = _cb_minimal_np_left(sentence, spans, left, r)
            g = np_left - 1
            if g > left and _cb_peelable_postmod(spans, g, r):
                r = g - 1
                continue
            break
        if np_left > left or r < right:
            head_span = sentence[spans[np_left][1]:spans[r][2]]
    elif CALLED_FIX_HEAD:
        np_left = _cb_minimal_np_left(sentence, spans, left, right)
        gov_i = np_left - 1
        gov = spans[gov_i][0].lower() if gov_i >= left else None
        # gov is the token GOVERNING the trigger-adjacent NP.
        #   gov == "of"  => the NP is an OF-COMPLEMENT. Whether the genus is the of-complement
        #                   or the noun that takes it is decided by THAT NOUN, using the
        #                   module's own _MEASURE_HEAD / _WEAK_HEAD sets: "small amounts OF
        #                   other elements" and "a type OF white blood cell" put the content in
        #                   the complement; "a region OF the cell" and "a branch OF biology" do
        #                   not (low attachment there would give `nucleoid ISA cell`).
        #   gov anything else (a non-of preposition, a participle, a relativizer)
        #                => the naming attaches LOW, to the adjacent NP.
        take_low = gov is not None and np_left > left
        if take_low and gov == "of":
            take_low = False
            if gov_i - 1 >= left and _gap_is_clean(sentence, spans[gov_i - 1][2],
                                                   spans[gov_i][1]):
                gov_noun = lemma_verb(spans[gov_i - 1][0])
                take_low = (gov_noun in _MEASURE_HEAD or gov_noun in _WEAK_HEAD
                            or is_closed_class(gov_noun))
        if take_low:
            head_span = sentence[spans[np_left][1]:spans[right][2]]

    return CalledAntecedent(definiens=span_text, head_span=head_span, start=start, end=end,
                            be_linked=be_linked,
                            mode="BE_LINKED" if be_linked else "REDUCED_RELATIVE",
                            reason="OK"), "OK"


def called_antecedent(sentence: str, m: "re.Match", dfs_text: str) -> Optional[CalledAntecedent]:
    """Constituent-bounded antecedent for one `_RE_CALLED` match, or None to REFUSE."""
    obj, _reason = _cb_called_antecedent_core(sentence, m, dfs_text)
    return obj


def called_antecedent_reason(sentence: str, m: "re.Match", dfs_text: str) -> str:
    return _cb_called_antecedent_core(sentence, m, dfs_text)[1]


def _called_boundary_self_test() -> None:
    """Every case below is a REAL sentence from the v6 diagnostic's example dump, with the
    fault class it was flagged under. `None` in the expectation column = the extractor must
    emit NOTHING for that definiendum."""
    def head_of(sent, dfd_lemma):
        hs = {d.head for d in extract_definitions(sent)
              if d.definiendum_lemma == dfd_lemma and d.pattern == "CALLED"}
        return sorted(hs)

    # L1: antecedent opened with a preposition -> `in a gel-like substance`
    s = ("The nucleus stores chromatin (DNA plus proteins) in a gel-like substance called "
         "the nucleoplasm")
    assert head_of(s, "nucleoplasm") == ["substance"], head_of(s, "nucleoplasm")

    # L1 + L2: everything left of the trigger is an adverb then a finite verb -> REFUSE.
    # Shipped code banked `fermentation ISA nadh` here.
    s = ("Processes that use an organic molecule to regenerate NAD+ from NADH are collectively "
         "referred to as fermentation")
    assert head_of(s, "fermentation") == [], head_of(s, "fermentation")

    # L2: the antecedent swallowed a whole preceding clause -> `impurity ISA mold`
    s = ("A gold coin is simply a very large number of gold atoms molded into the shape of a "
         "coin and contains small amounts of other elements known as impurities")
    # (`elements` not `element`: the OWNED lemmatizer `lemma_word` leaves this plural alone.
    #  That is pre-existing and out of scope here -- the CONSTITUENT is what this fix owns.)
    assert head_of(s, "impurity") == ["elements"], head_of(s, "impurity")

    # L2: `monomer ISA molecule` came from "a polymer is a large molecule that is made by"
    s = ("Many molecules that are biologically important are macromolecules, large molecules "
         "that are typically formed by polymerization (a polymer is a large molecule that is "
         "made by combining smaller units called monomers, which are simpler than "
         "macromolecules)")
    assert head_of(s, "monomer") == ["unit"], head_of(s, "monomer")

    # B, low attachment across a NON-of post-modifier: the name attaches to `channel`,
    # not to the leading NP head `passage`.
    s = ("In the thylakoid, that opening is a passage through a specialized protein channel "
         "called the ATP synthase")
    assert head_of(s, "synthase") == ["channel"], head_of(s, "synthase")

    # B MUST NOT fire across a COPULA link: the antecedent is the whole subject NP, so the
    # head is `space`, NOT the trigger-adjacent `granum`.
    s = ("As shown in, a stack of thylakoids is called a granum, and the liquid-filled space "
         "surrounding the granum is called stroma")
    assert head_of(s, "stroma") == ["space"], head_of(s, "stroma")

    # B's `of` carve-out: low attachment here would give `nucleoid ISA cell`, the exact
    # regression _RE_COLON was tightened to kill.
    s = "Prokaryotic DNA is found in a darkened region of the cell called the nucleoid"
    assert head_of(s, "nucleoid") == ["region"], head_of(s, "nucleoid")

    # v4 F4 polarity fix must SURVIVE: the head is `structure`, never `function`.
    s = "These unused structures without function are called vestigial structures"
    assert "function" not in head_of(s, "structure"), head_of(s, "structure")

    # v4 F2c list guard must SURVIVE: a comma-list's last item is not a definiens.
    s = ("The tube feet are used for gas exchange, nutrient circulation, and locomotion called "
         "the water vascular system")
    assert head_of(s, "system") == [], head_of(s, "system")
    # ... while the coordinated-clause continuation must still yield its fact.
    s = ("The major arteries diverge into minor arteries, and then smaller vessels called "
         "arterioles")
    assert head_of(s, "arteriole") == ["vessel"], head_of(s, "arteriole")

    # the module's own shipped CALLED cases still read as before
    s = "This tiny filtering structure is called the nephron"
    assert head_of(s, "nephron") == ["structure"], head_of(s, "nephron")
    s = "The entirety of this process is called oxidative phosphorylation"
    assert head_of(s, "phosphorylation") == ["entirety"], head_of(s, "phosphorylation")
    s = "The region of unwinding is called a transcription bubble"
    assert any(d.term == "transcription bubble" for d in extract_definitions(s)), \
        extract_definitions(s)

    print("[definitional_extraction] CALLED-boundary v7 self-test PASS")


if __name__ == "__main__":
    _self_test()
