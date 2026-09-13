"""hdlab/lexical_utils.py -- the BF lexical foundation split out of hdlab.commonnoun_binder (2026-09-11,
consolidate_the_six_coreference_organs_into_one_cue_based_entity_resolver, Q111 landing).

WHY THIS EXISTS: commonnoun_binder's `situation_predict` clustering is NOT_BF and empirically DEAD on the live
path (shadowed by online_entity_cluster) -- it retires from the default reader. But its LEXICAL HELPERS
(head_lemma / concept_lemma / coarse_class / is_name / modifiers / definiteness / person_synset / _num_of and the
WordNet lazy loader) are a BF_SPIRIT static offline foundation that FOUR live organs depend on
(online_entity_cluster, crosstype_bridge, goal_register, situation_reader, and the new entity_resolver). So the
helpers SPLIT here (canonical home) and commonnoun_binder re-imports them for backward compatibility -- deleting
the organ would have broken the live consumers (the audit's INVERSE-split shape, cf. thematic_role_labeler
Cluster-4). Bodies are VERBATIM from commonnoun_binder (byte-identical behavior; shared module-level caches).

Static offline lexical foundation (nltk WordNet morphy/supersense), NO inference-time LLM. Glass-box, ASCII.
"""
from __future__ import annotations

__bf_status__ = 'BF_SPIRIT'   # BF | BF_SPIRIT | NOT_BF | BF_UNPINNED | BF_UNVERIFIED ; mirrors notes/bf_status_registry.jsonl
__bf_verified__ = '2026-09-11 consolidation landing (strategy first-hand; verbatim split of the BF lexical helpers from commonnoun_binder)'
__bf_note__ = 'WordNet morphy/supersense lexical-concept helpers (head_lemma/concept_lemma/coarse_class/person_synset/is_name/modifiers/definiteness/_num_of); static offline lexical foundation (admissible supply), NO inference LLM'
__bf_corrections__ = []

import re
from typing import Dict

from hdlab.coref import name_content_tokens
from hdlab import morphology as _gbm   # glass-box morphy (byte-identical; no nltk on the lemma path)


# =========================== ported lexical helpers (VERBATIM from DIAG) ==============================
DEF_DET = {"the", "this", "that", "these", "those", "his", "her", "my", "your", "our", "their", "its"}
INDEF_DET = {"a", "an", "some", "any", "another", "no", "each", "every", "one"}
_IRREG = {"men": "man", "women": "woman", "children": "child", "people": "person", "gentlemen": "gentleman",
          "gentlewomen": "gentlewoman", "wives": "wife", "ladies": "lady", "brothers": "brother",
          "sisters": "sister", "feet": "foot", "teeth": "tooth", "geese": "goose", "mice": "mouse"}


def head_lemma(head: str) -> str:
    """Light noun lemma: irregular map, then regular plural strip (ies->y, ses/xes/ches->s.., s)."""
    h = re.sub(r"[^a-z]+", "", str(head).lower())
    if not h:
        return ""
    if h in _IRREG:
        return _IRREG[h]
    if len(h) > 4 and h.endswith("ies"):
        return h[:-3] + "y"
    if len(h) > 4 and h.endswith(("ses", "xes", "zes", "ches", "shes")):
        return h[:-2]
    if len(h) > 3 and h.endswith("s") and not h.endswith("ss"):
        return h[:-1]
    return h


_MORPHY = {}


def concept_lemma(surf: str) -> str:
    """Brain-foundational lexical-CONCEPT lemma (owner-DONE the_common_noun_binder_is_string_identity...): WordNet
    morphy NOUN lemma of the head surface -- the substrate's standing wordform->lemma-concept map (the same morphy
    convention used by causation_typing/event_type/generalized_event_knowledge/goal_achievement). This is the BF
    replacement for `head_lemma` on the RESOLUTION path: non-alpha heads (redaction "____", digits) are KEPT as
    their lowered surface -- NEVER collapsed to "" (head_lemma's false-merge bug) -- and there is no -us/-es
    over-strip ("corpus" stays "corpus", not "corpu"). Static offline lexical foundation (nltk-WordNet), no
    inference-time LLM. Memoized. Leaves `head_lemma` UNCHANGED so the clustering consumer stays byte-identical."""
    v = _MORPHY.get(surf)
    if v is not None:
        return v
    base = "".join(c for c in surf.lower() if c.isalpha())
    if not base:
        v = surf.lower()          # keep "____"/"_____"/"9" DISTINCT -- do not merge redactions (the crude-regex bug)
    else:
        wn = _wn()
        v = _gbm.morphy(base, "n") or _gbm.morphy(base) or base
    _MORPHY[surf] = v
    return v


# COARSE ONTOLOGICAL CLASS (Rosch basic-level; owner-DONE the_common_noun_binder_is_string_identity...): the MFS
# WordNet lexname (supersense) grouped into ABSTRACT/OBJECT/PERSON/GROUP/LOCATION/TIME/QUANTITY -- the situation-model
# FOCUS bridge's compatibility class. Static offline lexical foundation (nltk-WordNet), no inference-time LLM.
_LEXGROUP = {}
for _g, _lns in {
    "ABSTRACT": ("noun.act", "noun.cognition", "noun.state", "noun.attribute", "noun.feeling", "noun.phenomenon",
                 "noun.relation", "noun.communication", "noun.motive", "noun.process", "noun.event"),
    "OBJECT": ("noun.artifact", "noun.object", "noun.substance", "noun.food", "noun.plant", "noun.body", "noun.animal"),
    "PERSON": ("noun.person",), "GROUP": ("noun.group",), "LOCATION": ("noun.location",),
    "TIME": ("noun.time",), "QUANTITY": ("noun.quantity",),
}.items():
    for _ln in _lns:
        _LEXGROUP[_ln] = _g
_CLASS_CACHE = {}


def coarse_class(lemma):
    """Broad ontological class of a noun lemma via its most-frequent-sense WordNet lexname (supersense). None if OOV."""
    if lemma in _CLASS_CACHE:
        return _CLASS_CACHE[lemma]
    ss = _wn().synsets(lemma, pos="n")                  # freq-ordered -> [0] is the MFS
    c = _LEXGROUP.get(ss[0].lexname()) if ss else None
    _CLASS_CACHE[lemma] = c
    return c


def is_name(m, gaz) -> bool:
    """A clean proper name (aliasable) -- reuse the coref organ's own name test on the raw span."""
    return bool(name_content_tokens(m.get("span_toks", [m["head"]])))


def modifiers(m) -> set:
    """Non-determiner, non-head alphabetic modifier tokens of the span (lowercased)."""
    span = [w.lower() for w in m.get("span_toks", [m["head"]])]
    hl = head_lemma(m["head"])
    return {w for w in span[:-1] if w.isalpha() and w not in DEF_DET and w not in INDEF_DET
            and head_lemma(w) != hl}


def definiteness(m) -> str:
    span = [w.lower() for w in m.get("span_toks", [m["head"]])]
    if not span:
        return "bare"
    d = span[0]
    if d in INDEF_DET:
        return "indef"
    if d in DEF_DET:
        return "def"
    return "bare"


# =========================== WordNet person-typing (VERBATIM from LK) =================================
_WN = None
_PERSON_SYN = None
_person_cache: Dict[str, object] = {}


def _wn():
    global _WN, _PERSON_SYN
    if _WN is None:
        from nltk.corpus import wordnet as wn
        _WN = wn
        _PERSON_SYN = wn.synset("person.n.01")
    return _WN


def person_synset(lemma):
    """The most-common PERSON-denoting noun synset of `lemma` (person.n.01 in its hypernym paths), or None."""
    if lemma in _person_cache:
        return _person_cache[lemma]
    wn = _wn()
    best = None
    for s in wn.synsets(lemma, "n"):
        paths = s.hypernym_paths()
        if any(_PERSON_SYN in p for p in paths):
            best = s
            break
    _person_cache[lemma] = best
    return best


def _num_of(m):
    n = m.get("number")
    if n in ("singular", "sing"):
        return "sing"
    if n in ("plural", "plur"):
        return "plur"
    h = head_lemma(m["head"])
    raw = m["head"].lower()
    if raw != h and raw.endswith("s"):
        return "plur"
    return "sing"
