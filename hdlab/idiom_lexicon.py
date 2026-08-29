"""idiom_lexicon -- a glass-box, spaCy-FREE stored-unit idiom / multiword-expression (MWE) FOUNDATION.

Landed 2026-08-28 from the integrated `no_glass_box_verb_sense_disambiguation` (SOLVED/EXCELLENT, owner-DONE): the
solver flagged the idiom stored-unit lexicon as "the highest-value brain-foundational lever" and "the spaCy-free
FOUNDATION that can land first". This is a SHARED asset -- any front-end (the verb-sense disambiguator, the ToM ledger's
motion signal, an event miner) can flag a non-compositional MWE and retrieve its holistic coarse frame BEFORE literal
composition, suppressing the false literal reading ("pass away" != a motion; "make sense" != a creation; "take place"
!= a possession).

BRAIN RATIONALE (PINNED): the mental lexicon stores non-compositional MWEs as UNITS and retrieves them HOLISTICALLY
before literal composition (Jackendoff's construction lexicon; Cutting & Bock 1997 -- idioms are accessed as stored
wholes, faster than their literal parse). This module is that holistic retrieval: a dict lookup over a committed,
offline-built asset (`data/idiom_foundation_v1/idioms.json`, 1813 phrasal + 414 verb+object entries mined glass-box
from WordNet's multiword verb inventory + a PMI corpus pass + a hand-vetted institutional/light-verb table).

RUNTIME (inference) is a pure DICT LOOKUP -- NO spaCy, NO WordNet, NO LLM, no network (the invariant). The caller
supplies the already-lemmatized (verb, particle, object-head) triple from whatever parse it has; this returns the
stored coarse frame or None. The OFFLINE BUILD (WordNet/PMI mining) stays in `experiments/idiom_gate.py` -- a static
offline-built asset is an admissible FOUNDATION (owner 2026-08-16). Missing/corrupt asset -> empty maps -> always None
(graceful: the caller degrades to pure composition).
"""
from __future__ import annotations

import json
import os
from typing import Dict, Optional

# Coarse event-FRAME inventory (WordNet verb lexnames / Ciaramita-Altun supersenses) -- the value space of a lookup.
COARSE_FRAMES = ["motion", "possession", "communication", "perception", "cognition",
                 "change", "contact", "stative", "creation", "body", "emotion",
                 "consumption", "social", "competition", "weather"]
_FRAMESET = set(COARSE_FRAMES)

# Standard phrasal-verb particles (adverbial/prepositional): a helper for callers deciding whether a two-token verb
# lemma's tail is a particle (-> phrasal-verb lookup) rather than an object.
PARTICLES = {"away", "off", "out", "up", "down", "in", "on", "over", "back", "across", "around",
             "about", "along", "apart", "aside", "forth", "forward", "through", "together", "under",
             "by", "upon", "ahead", "round", "past"}

_ASSET_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "data", "idiom_foundation_v1", "idioms.json")
_CACHE: Optional[Dict[str, Dict[str, str]]] = None


def lexname_to_frame(lexname: Optional[str]) -> Optional[str]:
    """WordNet verb lexname ('verb.motion') -> coarse frame ('motion'). None if not a verb lexname."""
    if not lexname or not lexname.startswith("verb."):
        return None
    return lexname.split(".", 1)[1]


def _load() -> Dict[str, Dict[str, str]]:
    """Load the committed asset once (cached). Missing/corrupt -> empty maps (idiom_sense then always returns None)."""
    global _CACHE
    if _CACHE is not None:
        return _CACHE
    try:
        with open(_ASSET_PATH, "r", encoding="ascii") as f:
            obj = json.load(f)
        _CACHE = {"phrasal": dict(obj.get("phrasal", {})), "vobj": dict(obj.get("vobj", {}))}
    except Exception:
        _CACHE = {"phrasal": {}, "vobj": {}}
    return _CACHE


def idiom_sense(verb_lemma: str, particle: Optional[str] = None,
                dobj_head: Optional[str] = None) -> Optional[str]:
    """Stored-unit lookup: return the coarse frame (in COARSE_FRAMES) if (verb [+particle] [+object head]) is a stored
    non-compositional MWE, else None. Holistic MWE retrieval (Jackendoff; Cutting & Bock).

    Order: the phrasal (verb+particle) unit is the stronger stored cue and is checked first; the verb+object unit
    second. LITERAL cases ('leave'+'room', 'leave'+'key') are simply absent -> None (the caller composes literally).
    spaCy-FREE: the caller supplies the lemmatized triple; this is a dict get."""
    if not verb_lemma:
        return None
    data = _load()
    v = verb_lemma.strip().lower()
    if particle:
        fr = data["phrasal"].get(v + "|" + particle.strip().lower())
        if fr is not None:
            return fr
    if dobj_head:
        fr = data["vobj"].get(v + "|" + dobj_head.strip().lower())
        if fr is not None:
            return fr
    return None


def is_idiom(verb_lemma: str, particle: Optional[str] = None, dobj_head: Optional[str] = None) -> bool:
    """True iff (verb [+particle] [+object head]) is a stored non-compositional MWE (idiom_sense is not None)."""
    return idiom_sense(verb_lemma, particle, dobj_head) is not None
