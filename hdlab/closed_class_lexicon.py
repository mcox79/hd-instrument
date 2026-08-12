"""hdlab/closed_class_lexicon.py -- CLOSED-CLASS (function-word) lexicon for grounding eligibility.

WHY THIS EXISTS: a content word's MEANING cannot be a function/discourse word. The reading
grounding loop picks a grounded word's "meaning" by cosine-nearest neighbour over a
bag-of-content-words concept space; that procedure gravitates to high-frequency grammatical words
for ANY target with a thin or noisy context, independent of what the target actually means. The
2026-08-12 foundation audit (notes/foundation_grounding_sample_2026-08-12.md) measured the most
frequent grounded objects in the landed store as `also`(31), `say`(15), `people`(10), `like`(5),
`more`(5), `most`(5) -- i.e. the single most common "meaning" assigned to any word was a discourse
marker. This module supplies the principled exclusion.

CRITERION (deliberately NOT a blacklist of the words the audit happened to surface -- a list tuned
to that sample would be overfitting to the audit). A lemma is CLOSED-CLASS iff EITHER:

  (i) UD FUNCTIONAL CLASS. Its MAJORITY UPOS tag in the Universal Dependencies English EWT
      treebank (data/corpora/ud_english_ewt/en_ewt-ud-train.conllu, already in-repo) is one of
      UD's own FUNCTIONAL (closed) part-of-speech classes:
          ADP, AUX, CCONJ, DET, NUM, PART, PRON, SCONJ, PUNCT, SYM, X
      UD's open-vs-closed class split is a published, language-general standard
      (CITED@universaldependencies.org/u/pos/ -- open: ADJ ADV INTJ NOUN PROPN VERB;
      closed: ADP AUX CCONJ DET NUM PART PRON SCONJ; other: PUNCT SYM X). This is EMPIRICAL and
      corpus-derived, not hand-listed: the tag counts come from the treebank's own annotations.
      It is what catches e.g. `like` (majority tag ADP, MEASURED 161 ADP vs 138 VERB vs 83 SCONJ).

  (ii) CURATED FUNCTION/DISCOURSE-WORD LIST. It appears in spaCy's English default stop-word list
      (CITED@spacy.lang.en.stop_words.STOP_WORDS, 326 entries). UD's tag inventory classes
      DISCOURSE ADVERBS (`also`, `most`) as ADV, which UD counts as OPEN class, so criterion (i)
      alone cannot exclude them; a curated function-word list can. spaCy's list is preferred over
      sklearn's ENGLISH_STOP_WORDS on DOCUMENTED grounds rather than outcome grounds: sklearn's own
      documentation flags that list as having known issues and not being a good general-purpose
      stop list, and it additionally excludes plainly lexical items (`thin`, `describe`, `system`)
      that a semantic foundation has every reason to keep as candidate meanings.

Membership is tested against BOTH the surface form AND its hdlab.thematic_role_labeler.lemma_verb
normalization, because the grounding loop stores suffix-stripped lemmas (`says` -> `say`).

DISCLOSED LIMITATION (stated in the pre-reg BEFORE measuring, not discovered afterwards): this
criterion does NOT exclude `people` (UD majority tag NOUN; in no stop list). `people` is a genuine
open-class noun. Hand-adding it because it appeared in the audit's top-10 is precisely the
overfitting this module refuses to do, so it stays eligible and the limitation is disclosed.

DETERMINISM: the built set is cached to data/closed_class_lexicon_v1.json as a SORTED list, so
every consumer in every process sees a byte-identical lexicon. Rebuild is deterministic (a
majority-count over a fixed corpus file plus a frozen library constant); ties in the UPOS majority
are broken by sorted tag name, never by dict order. ASCII-only. PROT-023/F.5 compliant.
"""
from __future__ import annotations

import json
import os
from functools import lru_cache
from typing import Dict, FrozenSet, List, Optional, Set

from hdlab.thematic_role_labeler import lemma_verb

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# UD's own FUNCTIONAL (closed) + "other" classes. CITED@universaldependencies.org/u/pos/
UD_CLOSED_UPOS: FrozenSet[str] = frozenset({
    "ADP", "AUX", "CCONJ", "DET", "NUM", "PART", "PRON", "SCONJ", "PUNCT", "SYM", "X",
})

UD_TRAIN_CONLLU = os.path.join(REPO_ROOT, "data", "corpora", "ud_english_ewt",
                               "en_ewt-ud-train.conllu")
CACHE_PATH = os.path.join(REPO_ROOT, "data", "closed_class_lexicon_v1.json")

_CACHED: Optional[FrozenSet[str]] = None


def _ud_majority_closed_forms(conllu_path: str) -> Set[str]:
    """Word forms whose MAJORITY UPOS in the treebank is a UD functional class.

    Ties are broken deterministically by sorted tag name (never by dict insertion order), so the
    result is byte-identical across processes and Python versions."""
    counts: Dict[str, Dict[str, int]] = {}
    with open(conllu_path, encoding="utf-8") as f:
        for line in f:
            if not line.strip() or line.startswith("#"):
                continue
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 5:
                continue
            tok_id, form, upos = parts[0], parts[1], parts[3]
            if "-" in tok_id or "." in tok_id:      # multiword-token range / empty node
                continue
            key = form.lower()
            counts.setdefault(key, {})
            counts[key][upos] = counts[key].get(upos, 0) + 1
    out: Set[str] = set()
    for form in sorted(counts):
        tags = counts[form]
        best = sorted(tags.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]
        if best in UD_CLOSED_UPOS:
            out.add(form)
    return out


def _spacy_stop_words() -> Set[str]:
    from spacy.lang.en.stop_words import STOP_WORDS  # frozen library constant, no model needed
    return {str(w).lower() for w in STOP_WORDS}


def build_closed_class_set(conllu_path: str = UD_TRAIN_CONLLU) -> FrozenSet[str]:
    """Build the lexicon from its two sources. Raises (never silently degrades) if a source is
    unavailable -- a silently-empty exclusion set would let the defect this module exists to fix
    reappear undetected."""
    if not os.path.isfile(conllu_path):
        raise FileNotFoundError(
            f"UD English EWT treebank not found at {conllu_path!r}; closed-class criterion (i) "
            f"cannot be built. Refusing to fall back to a partial lexicon.")
    forms = _ud_majority_closed_forms(conllu_path) | _spacy_stop_words()
    # Also admit the lemma_verb normalization of every entry, because the grounding loop stores
    # suffix-stripped lemmas (e.g. `says` -> `say`, `does` -> `do`).
    normalized = {lemma_verb(w) for w in forms}
    return frozenset(sorted(forms | normalized))


def closed_class_set(rebuild: bool = False) -> FrozenSet[str]:
    """The lexicon, cached in-process and on disk (data/closed_class_lexicon_v1.json)."""
    global _CACHED
    if _CACHED is not None and not rebuild:
        return _CACHED
    if os.path.isfile(CACHE_PATH) and not rebuild:
        with open(CACHE_PATH, encoding="utf-8") as f:
            payload = json.load(f)
        _CACHED = frozenset(payload["closed_class"])
        return _CACHED
    built = build_closed_class_set()
    payload = {
        "criterion": "UD-EWT majority-UPOS in UD functional classes UNION spaCy English "
                     "default stop words; both surface form and lemma_verb normalization",
        "ud_closed_upos": sorted(UD_CLOSED_UPOS),
        "ud_source": os.path.relpath(UD_TRAIN_CONLLU, REPO_ROOT).replace("\\", "/"),
        "spacy_list": "spacy.lang.en.stop_words.STOP_WORDS",
        "n_entries": len(built),
        "closed_class": sorted(built),
    }
    os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
    tmp = CACHE_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=1)
    os.replace(tmp, CACHE_PATH)
    _CACHED = built
    return _CACHED


@lru_cache(maxsize=None)
def _is_closed_class_cached(word: str) -> bool:
    s = closed_class_set()
    w = word.lower().strip()
    return w in s or lemma_verb(w) in s


def is_closed_class(word: str) -> bool:
    """True iff `word` (or its lemma_verb normalization) is closed-class under the criterion.

    Memoized: the grounding loop calls this once per ANCHOR per canonicalize scan (tens of
    millions of calls over a full corpus run), and the answer is a pure function of the word."""
    return _is_closed_class_cached(str(word))


def is_eligible_meaning(word: str) -> bool:
    """True iff `word` may serve as the OBJECT of a GROUNDED_MEANING fact (i.e. may be what some
    other word MEANS). The exact complement of is_closed_class; named separately so call sites read
    as the semantic claim they are making, not as a stopword test."""
    return not is_closed_class(word)


# ===================== formula self-tests ==========================================

def _selftest_catches_the_audited_filler_classes() -> None:
    """The AUDITED failure classes are excluded -- but each for a CRITERION reason, verified
    against the criterion that catches it, not because it was hand-listed."""
    ud_only = _ud_majority_closed_forms(UD_TRAIN_CONLLU)
    spacy_only = _spacy_stop_words()
    # (i) UD functional-majority catches prepositional/complementizer `like`
    assert "like" in ud_only, "UD majority-UPOS criterion must catch 'like' (majority tag ADP)"
    # (ii) curated function/discourse list catches discourse adverbs + reporting verb
    for w in ("also", "more", "most", "say"):
        assert w in spacy_only, f"curated function-word criterion must catch {w!r}"
    for w in ("also", "more", "most", "say", "like", "the", "of", "which", "would", "one"):
        assert is_closed_class(w), f"{w!r} must be closed-class"


def _selftest_does_not_eat_content_words() -> None:
    """Genuine content words -- including every MEANINGFUL object the prior audit found -- remain
    eligible. A criterion that quietly excluded them would 'pass' the filler band by destroying
    the signal."""
    for w in ("deductive", "decay", "phylogenetic", "cytoplasm", "invaginat", "polymerase",
              "haploid", "gene", "meaning", "nest", "soot", "alliance", "engine", "harbor",
              "boat", "storm", "electron", "mitochondria"):
        assert is_eligible_meaning(w), f"content word {w!r} must stay eligible as a meaning"


def _selftest_disclosed_limitation_is_real() -> None:
    """The disclosed limitation is asserted as a TEST so it cannot silently drift into a hidden
    hand-patch later: `people` is open-class under the stated criterion and IS still eligible."""
    assert is_eligible_meaning("people"), (
        "'people' must remain eligible -- excluding it would mean the lexicon had been hand-tuned "
        "to the audit sample, which the criterion explicitly refuses")


def _selftest_lemma_normalization_covered() -> None:
    """Suffix-stripped forms the loop actually stores are caught too."""
    assert is_closed_class("says"), "'says' normalizes to 'say'"
    assert is_closed_class("SAY"), "case-insensitive"


def _selftest_deterministic_rebuild() -> None:
    a = build_closed_class_set()
    b = build_closed_class_set()
    assert a == b and sorted(a) == sorted(b), "lexicon build is not deterministic"


def _run_all_selftests() -> dict:
    _selftest_catches_the_audited_filler_classes()
    _selftest_does_not_eat_content_words()
    _selftest_disclosed_limitation_is_real()
    _selftest_lemma_normalization_covered()
    _selftest_deterministic_rebuild()
    return {"n_entries": len(closed_class_set()),
            "criterion": "UD-EWT majority-UPOS functional UNION spaCy English stop words",
            "catches_audited_filler_ok": True, "keeps_content_words_ok": True,
            "disclosed_limitation_people_still_eligible": True}


if __name__ == "__main__":
    print(json.dumps(_run_all_selftests(), indent=2))
    print("ALL SELF-TESTS PASSED")
