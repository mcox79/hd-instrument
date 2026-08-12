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
                 "range", "array", "majority", "portion", "handful", "sequence"}
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

    def to_dict(self) -> dict:
        return {
            "definiendum": self.definiendum,
            "definiens": self.definiens,
            "pattern": self.pattern,
            "head": self.head,
            "definiendum_lemma": self.definiendum_lemma,
            "definiens_lemmas": list(self.definiens_lemmas),
            "sentence": self.sentence,
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


def _mk(dfd: str, dfs: str, pattern: str, sentence: str) -> Optional[Definition]:
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
    head = definiens_head(dfs)
    if head is None or head == dfd_lemma:
        return None
    dfs_lemmas = [l for l in _lemmas(dfs) if not is_closed_class(l)]
    return Definition(definiendum=dfd, definiens=dfs, pattern=pattern, head=head,
                      definiendum_lemma=dfd_lemma, definiens_lemmas=dfs_lemmas,
                      sentence=sentence)


def extract_definitions(sentence: str) -> List[Definition]:
    """All definitional statements in ONE sentence. Order: GLOSSARY_COLON, APPOSITIVE, COPULA,
    CALLED, REFERS_TO. Duplicates on (definiendum_lemma, head) are collapsed, first-pattern-wins."""
    if not sentence or len(sentence) < 6:
        return []
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
            d = _mk(m.group("dfd"), m.group("dfs"), pat, sentence)
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

    print("[definitional_extraction] self-test PASS")


if __name__ == "__main__":
    _self_test()
