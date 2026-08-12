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
  hdlab.thematic_role_labeler.lemma_verb   -- surface->lemma normalizer (POS-generic despite name)
  hdlab.closed_class_lexicon.is_closed_class / is_eligible_meaning -- function-word gate
  hdlab.animacy_lexicon                    -- WordNet-sourced category lexicon (head-noun sanity)
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
from hdlab.thematic_role_labeler import lemma_verb

# -------------------------------------------------------------------------------------------
# Surface inventory. Every item is a literal surface cue; nothing is learned or tuned.
# -------------------------------------------------------------------------------------------

_DET = r"(?:a|an|the|any|each|every|one)"
_BE = r"(?:is|are|was|were)"

# Determiners / degree words that can never be a genus head.
_NON_HEAD = {
    "a", "an", "the", "this", "that", "these", "those", "its", "their", "his", "her",
    "one", "kind", "type", "sort", "form", "way", "part", "piece", "number", "group",
    "set", "lot", "bit", "series", "process",  # weak taxonomy nouns: kept but down-ranked
}
# The weak-taxonomy nouns above are legal heads only when nothing better exists in the span.
_WEAK_HEAD = {"kind", "type", "sort", "form", "way", "part", "piece", "number", "group",
              "set", "lot", "bit", "series", "process", "unit", "thing"}

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


def definiens_head(definiens: str) -> Optional[str]:
    """Genus head of a definiens NP: the LAST open-class token before the first clause boundary
    ('that', 'which', 'who', 'where', 'when', 'used', 'in', 'of', 'for', 'to' ... ) -- i.e. the
    head of the leading NP, not a word from its post-modifier. Falls back to the last open-class
    token in the whole span. Deliberately shallow + fully visible (see module docstring)."""
    toks = _tokens(definiens)
    if not toks:
        return None
    boundary = {"that", "which", "who", "whom", "whose", "where", "when", "used", "found",
                "of", "in", "on", "for", "to", "with", "by", "from", "made", "having",
                "responsible", "containing", "consisting"}
    lead: List[str] = []
    for t in toks:
        if t.lower() in boundary:
            break
        lead.append(t)
    span = lead if lead else toks
    strong = [t for t in span
              if t.lower() not in _NON_HEAD and not is_closed_class(lemma_verb(t))]
    if not strong:
        # allow weak-taxonomy heads only when nothing stronger exists
        weak = [t for t in span if lemma_verb(t) in _WEAK_HEAD]
        if weak:
            return lemma_verb(weak[-1])
        # try the full span before giving up
        strong = [t for t in toks
                  if t.lower() not in _NON_HEAD and not is_closed_class(lemma_verb(t))]
        if not strong:
            return None
    return lemma_verb(strong[-1])


# -------------------------------------------------------------------------------------------
# The five extractors. Each returns 0..n Definitions from ONE sentence.
# -------------------------------------------------------------------------------------------

# "renal artery: the artery that delivers blood to the kidney"
_RE_COLON = re.compile(
    r"^\s*(?P<dfd>[A-Za-z][A-Za-z '\-]{0,60}?)\s*:\s*(?P<dfs>" + _DET + r"\s+.+)$",
    re.IGNORECASE)

# "a nephron is the functional unit of the kidney"
_RE_COPULA = re.compile(
    r"(?:^|[,;]\s*|\.\s+)(?:" + _DET + r"\s+)?(?P<dfd>[A-Za-z][A-Za-z '\-]{0,60}?)\s+"
    r"(?P<be>" + _BE + r")\s+(?P<dfs>" + _DET + r"\s+[A-Za-z].{2,120}?)(?=[,.;]|$)",
    re.IGNORECASE)

# "the nephron, the functional unit of the kidney, filters blood"
_RE_APPOS = re.compile(
    r"(?:^|\s)(?:" + _DET + r"\s+)?(?P<dfd>[A-Za-z][A-Za-z'\-]{1,30})\s*,\s*"
    r"(?P<dfs>" + _DET + r"\s+[A-Za-z].{2,120}?)\s*,",
    re.IGNORECASE)

# "... is called the nephron" / "known as the nephron" / "referred to as X"
_RE_CALLED = re.compile(
    r"(?P<dfs>[A-Za-z][A-Za-z '\-]{2,120}?)\s+(?:" + _BE + r"\s+)?"
    r"(?:called|known\s+as|termed|named|referred\s+to\s+as)\s+"
    r"(?:" + _DET + r"\s+)?(?P<dfd>[A-Za-z][A-Za-z'\-]{1,30})",
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
    assert any(d.definiendum_lemma == "photosynthesi" for d in ds), ds

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

    print("[definitional_extraction] self-test PASS")


if __name__ == "__main__":
    _self_test()
