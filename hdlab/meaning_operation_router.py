"""Meaning operation router -- dispatch the meaning read-out by word class (semantic control).

Landed 2026-08-28 (landing-step 3 of the integrated `build_the_composed_scalar_magnitude_meaning_channel`,
SOLVED/EXCELLENT, owner-DONE). The reader's meaning read-out is OPERATION-SPECIFIC: a GRADABLE/evaluative adjective wants
the scalar-magnitude "ruler" (`hdlab.scalar_adjective_operation`); a noun / verb / CLASSIFICATORY adjective wants the
definitional gloss (`hdlab.conceptual_meaning`). This organ is the GATE + dispatch decision, NOT the computation.

WHAT IS PINNED (copy the operation): semantic control (LIFG / pMTG) selects the operation/representation appropriate to
the word (Controlled Semantic Cognition). ROUTING, not replacement, is the fidelity lever -- the magnitude op is a
"how much" op, not a "similar to what" op, so using it on nouns DESTROYS their similarity (validated: magnitude-only on
nouns 0.066 vs gloss 0.599). The routed reader beats BOTH a gloss-only reader (0.616 vs 0.424, misses gradable-adj
magnitude) AND a magnitude-only reader (0.339), with N/V read-outs IDENTICAL under routing (exact no-regression).

THE GRADABILITY GATE (the sharper one built + validated in the p1 work): a word is a gradable adjective IFF it
(has a WordNet ANTONYM OR is a SATELLITE scalar adjective) AND is NOT PERTAINYM-relational. WordNet PERTAINYM flags
classificatory/denominal adjectives (medical, financial, presidential) that the coarse `has_antonym` gate would misroute
(it catches 303 such misroutes); those stay TAXONOMIC on the gloss op. OUR-INVENTION-UNDER-TEST: the gate itself (a coarse
lexical trigger; corpus comparative-form / "very"-modifiability would sharpen it further).

DEFAULT-SAFE island: new module; wiring it into the LIVE meaning dispatch (so the reader actually routes) is the
composition step. `route()` returns a STRING label -- the caller holds the channels and calls the chosen one. Depends only
on nltk WordNet.
"""
from __future__ import annotations

from typing import Optional

from nltk.corpus import wordnet as wn

_ADJ_POS = ("a", "s")                # WordNet adjective (a) + satellite adjective (s)
_ADJ_TAGS = {"ADJ", "JJ", "JJR", "JJS", "a", "s", "adj"}


def _adj_lemmas(word: str):
    for pos in _ADJ_POS:
        for syn in wn.synsets(word, pos=pos):
            for lem in syn.lemmas():
                if lem.name().replace("_", " ").lower() == word.lower():
                    yield lem


def has_antonym(word: str) -> bool:
    """Any adjective lemma of `word` carries a WordNet antonym (the bipolar/gradable signature)."""
    return any(lem.antonyms() for lem in _adj_lemmas(word))


def has_satellite_scalar(word: str) -> bool:
    """`word` has a SATELLITE adjective synset (pos 's') -- a scalar sense clustered around a head adjective."""
    return len(wn.synsets(word, pos="s")) > 0


def is_pertainym_relational(word: str) -> bool:
    """Any adjective lemma of `word` is a PERTAINYM (relational/denominal: medical, financial) -> classificatory,
    NOT gradable -> keep it on the gloss op."""
    return any(lem.pertainyms() for lem in _adj_lemmas(word))


def is_gradable_adjective(word: str) -> bool:
    """The sharper gradability gate: (has_antonym OR satellite scalar) AND NOT pertainym-relational."""
    return (has_antonym(word) or has_satellite_scalar(word)) and not is_pertainym_relational(word)


def route(word: str, pos: Optional[str]) -> str:
    """Return the meaning OPERATION for (word, pos): 'magnitude' for a gradable/evaluative adjective (-> the scalar
    ruler), else 'conceptual' (-> the definitional gloss). The caller holds the channels and invokes the chosen one."""
    if pos is not None and str(pos) in _ADJ_TAGS and is_gradable_adjective(word):
        return "magnitude"
    return "conceptual"
