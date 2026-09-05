"""Event-TYPE representation: a verb's WordNet SUPERSENSE -> the folk-psychological ontology
{PHYSICAL, PERCEPTION, COGNITION, EMOTION, COMMUNICATION, BODY, SOCIAL, STATIVE, OTHER}.

Promoted VERBATIM (Q111) from experiments/exp_causal_unified_bridge_event_type_v1.py::event_type
(owner-DONE a_force_dynamic_meaning_hub_causal_scorer_retire_the_connective_scoping_workaround,
2026-09-05). This is the brain-foundational UPSTREAM that GENERALIZES the physical-only force
lexicon to the MENTAL majority of narrative causation (force dynamics covers ~3/16 real cause
verbs; 11/16 are perception/cognition/emotion/communication -- a DISTINCT brain system). It
consolidates the WordNet-supersense pattern the substrate already used ad hoc
(idiom_lexicon.lexname_to_frame; causation_typing._wn_lexname) into a first-class VERB event-type
organ.

Neural grounding is NETWORK-level only -- physical vs mental are anticorrelated systems (Jack et
al. 2013 opposing-domains; Fischer et al. 2016 intuitive-physics engine vs Saxe & Kanwisher 2003
rTPJ mentalizing; Campanella et al. 2022 triple dissociation). The class-level split is behavioral
(implicit causality: Ferstl et al. 2011; Hartshorne & Snedeker 2013). Do NOT claim VerbNet/
supersense CLASS-level neural grounding.

MFS (most-frequent-sense) is the ATL graded-semantic FREQUENCY DEFAULT (resting level). The
faithful accuracy upgrade is contextual WSD via the landed GroundedSemanticGraph organ (SemCor
resting-level + PPR spreading-activation) -- a named, filed further-upstream lever, NOT wired here
(it lifts type_ok 0.688->0.750 on hand-adjudicated gold; the cheap Lesk shortcut was tried and
REJECTED as a located negative). Documented MFS bound: it mis-types the homograph 'saw' (->contact)
and onomatopoeic sound verbs (tick/creak -> perception).

Glass-box, NO external LLM. Reuses WordNet (already in the substrate). Deterministic; ASCII.
"""
from __future__ import annotations

# WordNet verb supersense -> event type (the folk-psychological ontology).
_SUPERSENSE_TO_TYPE = {
    "verb.motion": "PHYSICAL", "verb.contact": "PHYSICAL", "verb.change": "PHYSICAL",
    "verb.creation": "PHYSICAL", "verb.consumption": "PHYSICAL", "verb.possession": "PHYSICAL",
    "verb.competition": "PHYSICAL", "verb.weather": "PHYSICAL",
    "verb.perception": "PERCEPTION", "verb.cognition": "COGNITION", "verb.emotion": "EMOTION",
    "verb.communication": "COMMUNICATION", "verb.body": "BODY", "verb.social": "SOCIAL",
    "verb.stative": "STATIVE",
}
MENTAL_TRIGGER = {"PERCEPTION", "COGNITION", "COMMUNICATION", "EMOTION"}   # can appraise -> cause a mental reaction
MENTAL_OUTCOME = {"EMOTION", "BODY", "COGNITION", "SOCIAL"}                # an experiential/expressive/intentional reaction

_WN = None
_LEXCACHE = {}


def _wn():
    global _WN
    if _WN is None:
        from nltk.corpus import wordnet as wn
        _WN = wn
    return _WN


def event_type(verb):
    """UPSTREAM event-type of a verb via its most-frequent-sense WordNet supersense. MFS is the frequency prior
    (the ATL graded-semantic default); full contextual WSD is the meaning-hub (a named further-upstream lever).
    Glass-box: lemmatize the surface via WordNet morphy (heard->hear, wept->weep) then take the first-synset
    supersense. Documented bound: MFS mis-types the homograph 'saw' (->contact) and onomatopoeic sound verbs
    (tick/creak -> perception); the constructed items avoid these, and the RC.GOLD coverage run reports the bound."""
    v = verb.lower()
    if v in _LEXCACHE:
        return _LEXCACHE[v]
    lem = _wn().morphy(v, "v") or v
    syns = _wn().synsets(lem, pos="v") or _wn().synsets(v, pos="v")
    t = _SUPERSENSE_TO_TYPE.get(syns[0].lexname(), "OTHER") if syns else "OTHER"
    _LEXCACHE[v] = t
    return t
