"""hdlab/animacy_lexicon.py (2026-08-02)

GLASS-BOX SYMBOLIC LEXICON: word/lemma -> {animacy, category, agent_capable}.

Source: WordNet (nltk.corpus.wordnet), via first-sense noun hypernym-closure classification.
This is a LOOKUP, not a learned encoder and not a borrowed embedding (no vectors returned; every
entry is a small readable dict). Supplying this table is supplying KNOWLEDGE/DATA (same status as
CSKG/ConceptNet already used elsewhere in this project), not a bolt-on reading mechanism -- the
extraction/role-assignment code that CONSUMES this table is unchanged glass-box logic (a linear
softmax + hand-written construction gates); this module only supplies the vocabulary a reader is
entitled to already know (MEANING=ASSIGNMENT: a dictionary is a lookup).

TWO KNOWN WORDNET FAILURE MODES this module guards against (found by direct probe on the McGuffey
corpus before writing this file -- see exp_extraction_commit_then_revise_v4_animacy.py docstring):

1. PRONOUN / SHORT-WORD COLLISION: WordNet has noun senses for single/two-letter ABBREVIATIONS that
   collide with common pronouns -- "I" matches the iodine symbol (chemistry noun sense), "He" matches
   the helium symbol. Looking these up as common nouns would mislabel "I"/"he"/"she" as inanimate.
   FIX: an explicit closed PRONOUN_TABLE is checked FIRST (before any WordNet call) for any token
   POS-tagged PRON; falls back to WordNet only for tokens NOT in the table.
2. PROPER-NOUN / COMMON-NOUN HOMOGRAPH COLLISION: a proper name that happens to share a surface form
   with an unrelated common noun gets the WRONG WordNet sense -- "Dash" (a dog's name in the McGuffey
   corpus) matches the common noun "dash" (a punctuation mark / abstract dash-mark sense); "Patty"
   matches "patty" (a small flat cake); "Read" (a person's surname, "Thomas Read") matches the verb-
   turned-noun "read". FIX: tokens POS-tagged PROPN are NEVER looked up in WordNet as common nouns --
   for a proper noun this module returns UNKNOWN (None) unless the surface form is in PRONOUN_TABLE
   (it never is, by construction) or a curated PROPER_NOUN_OVERRIDES table (empty by default; left as
   an extension point, not populated here since guessing person-vs-place from a bare capitalized token
   without additional NER signal would silently reintroduce the same collision risk it is meant to
   avoid). This is an HONEST coverage gap: proper nouns get NO lexicon signal in this version.

Public API:
    lookup_animacy(word, pos_tag=None) -> dict | None
        dict keys: "animacy" ("animate"|"inanimate"), "category" ("person"|"animal"|"object"|
        "abstract"), "agent_capable" (bool). Returns None if the word is not covered (proper noun
        with no override, unknown common noun, or WordNet has no noun sense).
    coverage_report(words, pos_tags=None) -> dict
        words: iterable of surface tokens (optionally parallel pos_tags iterable, "PROPN"/"PRON"/
        "NOUN"/other). Returns {"n_total", "n_covered", "coverage_frac", "by_category": Counter}.
    scrambled_lookup_factory(words, seed) -> callable
        builds a SCRAMBLED version of this lexicon for the can-fail negative control: same covered
        vocabulary, but animacy/category/agent_capable values are PERMUTED across words (a word that
        would look up as animate may now report inanimate, and vice versa) with a fixed seed. Used to
        confirm a lift is driven by CORRECT knowledge, not just by having ANY extra numeric feature.
"""
from __future__ import annotations

import random
from collections import Counter
from typing import Iterable, Optional

from nltk.corpus import wordnet as wn

# ---------------------------------------------------------------------------
# 1) PRONOUN TABLE (checked first; guards the I->iodine / He->helium WordNet collision).
#    "it"/"this"/"that"/"these"/"those" are deliberately UNKNOWN (None) -- genuinely ambiguous
#    (can corefer to a person, animal, or object; guessing either way risks a wrong prior).
# ---------------------------------------------------------------------------
PRONOUN_TABLE = {
    "i": "person", "me": "person", "you": "person", "he": "person", "him": "person",
    "she": "person", "her": "person", "we": "person", "us": "person", "they": "person",
    "them": "person", "myself": "person", "himself": "person", "herself": "person",
    "themselves": "person", "yourself": "person", "ourselves": "person",
    "it": None, "its": None, "itself": None,
    "this": None, "that": None, "these": None, "those": None,
}

# Extension point for curated proper-noun overrides (deliberately empty; see module docstring).
PROPER_NOUN_OVERRIDES: dict = {}

_PERSON_SYNSETS = {"person.n.01"}
_ANIMAL_SYNSETS = {"animal.n.01", "organism.n.01"}
_ARTIFACT_SYNSETS = {"artifact.n.01", "physical_entity.n.01"}
_ABSTRACT_SYNSETS = {"abstraction.n.06"}

_CATEGORY_TO_ANIMACY = {"person": "animate", "animal": "animate", "object": "inanimate", "abstract": "inanimate"}
_CATEGORY_TO_AGENT_CAPABLE = {"person": True, "animal": True, "object": False, "abstract": False}


def _wordnet_category(word: str) -> Optional[str]:
    """First-noun-sense hypernym-closure classification. None if WordNet has no noun sense."""
    syns = wn.synsets(word, pos=wn.NOUN)
    if not syns:
        return None
    names = set()
    for path in syns[0].hypernym_paths():
        for s in path:
            names.add(s.name())
    if names & _PERSON_SYNSETS:
        return "person"
    if names & _ANIMAL_SYNSETS:
        return "animal"
    if names & _ARTIFACT_SYNSETS:
        return "object"
    if names & _ABSTRACT_SYNSETS:
        return "abstract"
    return None


def lookup_animacy(word: str, pos_tag: Optional[str] = None) -> Optional[dict]:
    """word/lemma -> {"animacy", "category", "agent_capable"} or None if uncovered.

    pos_tag (universal-POS style: "PROPN"/"PRON"/"NOUN"/other) determines the lookup PATH:
      - PRON (or bare lowercase form present in PRONOUN_TABLE regardless of tag): PRONOUN_TABLE only.
      - PROPN: PROPER_NOUN_OVERRIDES only (empty by default) -- NEVER WordNet-common-noun lookup
        (guards the Dash/Patty/Read homograph collision).
      - anything else (typically NOUN): PRONOUN_TABLE first (harmless if absent), then WordNet.
    """
    w = word.lower().strip(".,\"'();:")
    if not w:
        return None
    if pos_tag == "PRON" or w in PRONOUN_TABLE:
        cat = PRONOUN_TABLE.get(w)
    elif pos_tag == "PROPN":
        cat = PROPER_NOUN_OVERRIDES.get(w)
    else:
        if len(w) <= 2:
            return None  # guards short-word WordNet symbol collisions even off the PRON path
        cat = _wordnet_category(w)
    if cat is None:
        return None
    return {"animacy": _CATEGORY_TO_ANIMACY[cat], "category": cat,
            "agent_capable": _CATEGORY_TO_AGENT_CAPABLE[cat]}


def coverage_report(words: Iterable[str], pos_tags: Optional[Iterable[Optional[str]]] = None) -> dict:
    words = list(words)
    tags = list(pos_tags) if pos_tags is not None else [None] * len(words)
    assert len(tags) == len(words)
    n_total = len(words)
    n_covered = 0
    by_cat = Counter()
    for w, t in zip(words, tags):
        r = lookup_animacy(w, t)
        if r is not None:
            n_covered += 1
            by_cat[r["category"]] += 1
    return {
        "n_total": n_total, "n_covered": n_covered,
        "coverage_frac": (n_covered / n_total) if n_total else None,
        "by_category": dict(by_cat),
    }


def scrambled_lookup_factory(words: Iterable[str], pos_tags: Optional[Iterable[Optional[str]]] = None,
                              seed: int = 20260802):
    """Builds a SCRAMBLED lexicon (can-fail negative control per director contract): looks up each
    word's REAL animacy dict, then randomly PERMUTES the dict-to-word assignment across the covered
    vocabulary (same covered set, same distribution of category values, but a word's assigned dict is
    someone else's, or its own by chance -- a true permutation, not resampling). A DETERMINISTIC
    sorted-then-shuffled word list is used so the permutation is reproducible across runs at a fixed
    seed (per project convention: sorted(set()) not list(set()) for split/permutation determinism).
    Returns a callable scrambled_lookup(word, pos_tag=None) -> dict|None with the SAME signature as
    lookup_animacy, backed by a frozen word->dict map built once at construction time.
    """
    words = list(words)
    tags = list(pos_tags) if pos_tags is not None else [None] * len(words)
    assert len(tags) == len(words)
    real = {}
    for w, t in zip(words, tags):
        key = (w.lower().strip(".,\"'();:"), t)
        if key in real:
            continue
        r = lookup_animacy(w, t)
        if r is not None:
            real[key] = r
    keys_sorted = sorted(real.keys())
    values_sorted = [real[k] for k in keys_sorted]
    rng = random.Random(seed)
    permuted_values = values_sorted[:]
    rng.shuffle(permuted_values)
    scrambled_map = dict(zip(keys_sorted, permuted_values))

    def scrambled_lookup(word: str, pos_tag: Optional[str] = None) -> Optional[dict]:
        key = (word.lower().strip(".,\"'();:"), pos_tag)
        return scrambled_map.get(key)

    return scrambled_lookup
