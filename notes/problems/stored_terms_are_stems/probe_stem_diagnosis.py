#!/usr/bin/env python3
"""Diagnosis probe for the stored_terms_are_stems problem.

Two jobs:
  (1) RUNTIME EVIDENCE: run HEAD's lemma_word / lemma_verb on the known-damaged
      words and on inflections that SHOULD normalize. Does the current code still
      emit `analysi`, `cigarett`, ...?
  (2) REPRODUCE: measure the true-stem rate on the v2_qualityfix store's subjects,
      per source/relation, with the ROUND-TRIP detector re-implemented here (NOT a
      "not in WordNet" check -- that was the strategy session's retracted 24%).

Round-trip detector (per PROBLEM.md sec 3): a token counts as stemmer output iff
  (a) it is NOT a word, AND
  (b) appending a plausible suffix makes one (analysi+s, acquaintanc+e).
This cannot share a blind spot with the damage because it makes no assumption about
what damage looks like -- it just asks "is a suffix missing".
"""
import json
import sys

sys.path.insert(0, r"D:/AI/hd-instrument")

from nltk.corpus import wordnet as wn  # noqa: E402
_WORDSET = set()
try:
    from nltk.corpus import words as nltk_words
    _WORDSET |= set(w.lower() for w in nltk_words.words())
except Exception:
    pass
# Function words (and, with, for, these, ...) are real words WordNet + the words-corpus omit;
# without them the round-trip detector FALSE-POSITIVES every stopword (and+es->andes). nltk's
# stopwords data is not downloaded here, so the closed-class list is HARDCODED (deterministic,
# no data dependency). This is the detector's own negative control -- see validate_detector().
_FUNCTION_WORDS = set("""
a an the and but or nor for yet so if because as until while of at by with about against between
into through during before after above below to from up down in out on off over under again
further then once here there when where why how all any both each few more most other some such no
not only own same than too very can will just should now i me my myself we our ours ourselves you
your yours yourself yourselves he him his himself she her hers herself it its itself they them their
theirs themselves what which who whom this that these those am is are was were be been being have has
had having do does did doing would could may might must shall this these those also into upon
""".split())
_WORDSET |= _FUNCTION_WORDS
try:
    from nltk.corpus import stopwords as _sw
    _WORDSET |= set(w.lower() for w in _sw.words("english"))
except Exception:
    pass

from hdlab.thematic_role_labeler import lemma_word, lemma_verb  # noqa: E402

STORE = r"D:/AI/hd-instrument/data/foundation/reading_grounding_v2_qualityfix/store/store_facts.json"

# suffixes that the Porter/Snowball signature strips (terminal -s, -e; plus common inflections)
SUFFIXES = ["s", "e", "es", "y", "ed", "ing", "ies", "d"]


def is_word(t: str) -> bool:
    """A token is a word if WordNet knows it OR a large English word list has it.
    The word-list arm exists precisely for the real words WordNet lacks (archaea,
    adipocytes) that inflated the crude detector."""
    tl = t.lower()
    if wn.morphy(tl) is not None:
        return True
    return tl in _WORDSET


def stem_suffix(t: str):
    """If t is a stemmer artifact, return the suffix that recovers a word; else None."""
    if len(t) < 3:
        return None
    if is_word(t):
        return None
    for suf in SUFFIXES:
        if is_word(t + suf):
            return suf
    return None


def validate_detector():
    """The detector must catch real chops (POSITIVE control) and flag NONE of a set of real words
    including FUNCTION WORDS (NEGATIVE control). A detector that fails either cannot be trusted."""
    positives = ["analysi", "cigarett", "apoptosi", "arteri", "statu", "acquaintanc", "heterozygou"]
    negatives = ["analysis", "cigarette", "dog", "running", "archaea", "adipocytes",
                 "and", "for", "her", "his", "with", "these", "than", "them", "she", "how"]
    miss_pos = [t for t in positives if stem_suffix(t) is None]
    false_pos = [(t, stem_suffix(t)) for t in negatives if stem_suffix(t) is not None]
    ok = not miss_pos and not false_pos
    print(f"=== DETECTOR CONTROLS: {'PASS' if ok else 'FAIL'} ===")
    if miss_pos:
        print(f"  POSITIVE control MISSED (real chops not flagged): {miss_pos}")
    if false_pos:
        print(f"  NEGATIVE control FALSE-POSITIVES (real words flagged): {false_pos}")
    if ok:
        print("  all 7 known chops flagged; all 16 real words (incl. function words) left alone")
    return ok


def runtime_evidence():
    damaged = ["analysis", "hypothesis", "cigarette", "heterozygous", "status",
               "apoptosis", "acquaintance", "elongate", "encode", "define",
               "duplicate", "luteinize", "arteries"]
    print("=== (1) HEAD lemma_word / lemma_verb on KNOWN-DAMAGED words ===")
    print("    (a chop = output is a truncation of the input; want output == a real word)")
    any_chop = False
    for w in damaged:
        lw, lv = lemma_word(w), lemma_verb(w)
        chop = (lw != w and w.startswith(lw) and not is_word(lw)) or \
               (lv != w and w.startswith(lv) and not is_word(lv))
        if chop:
            any_chop = True
        flag = "  <-- CHOP" if chop else ""
        print(f"  {w:16s} lemma_word={lw:16s} lemma_verb={lv:16s}{flag}")
    print(f"  ==> HEAD still chops at least one: {any_chop}")

    print("\n=== inflection sanity (these SHOULD reduce; proves we did not disable normalization) ===")
    infl = ["dogs", "running", "studies", "arteries", "leaves", "attaches",
            "encoded", "cats", "houses", "carries", "walked", "bigger"]
    for w in infl:
        print(f"  {w:12s} lemma_word={lemma_word(w):12s} lemma_verb={lemma_verb(w)}")


def reproduce_store():
    facts = json.load(open(STORE, encoding="utf-8"))
    print(f"\n=== (2) v2_qualityfix store: {len(facts)} facts ===")
    # distinct subjects, partitioned by (source, relation)
    from collections import defaultdict
    subs_by_group = defaultdict(set)
    all_subs = set()
    for f in facts:
        s = f.get("subject", "")
        if not isinstance(s, str) or not s:
            continue
        grp = (f.get("source", "?"), f.get("relation", "?"))
        subs_by_group[grp].add(s)
        all_subs.add(s)

    def rate(subs):
        stems = [(t, stem_suffix(t)) for t in subs]
        stems = [(t, suf) for t, suf in stems if suf]
        return len(stems), len(subs), stems

    n_stem, n_tot, examples = rate(all_subs)
    print(f"  ALL distinct subjects: {n_stem}/{n_tot} = {100*n_stem/max(1,n_tot):.2f}% true stems")
    print("  per (source, relation) group:")
    for grp in sorted(subs_by_group, key=lambda g: -len(subs_by_group[g])):
        ns, nt, ex = rate(subs_by_group[grp])
        if nt >= 20:
            print(f"    {str(grp):70s} {ns:4d}/{nt:4d} = {100*ns/nt:5.2f}%")
    print("\n  first 40 stem examples (token +suffix -> recovered word):")
    for t, suf in sorted(examples)[:40]:
        print(f"    {t:22s} +{suf} -> {t+suf}")


if __name__ == "__main__":
    runtime_evidence()
    reproduce_store()
