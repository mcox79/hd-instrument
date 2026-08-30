"""state_register EXTRACTION ADAPTER (spaCy). The tracking + semantic-matching CORE was PROMOTED
2026-08-30 to hdlab/state_register.py (sibling of hdlab/location_register.py, which is also core-only).
This file keeps the parser-dependent extraction (OUR-INVENTION front-end) experiment-side and
re-exports the promoted core so the 61/61 witness + the exp_state_register_* cells import the SAME core.
"""
from __future__ import annotations

from dataclasses import dataclass, field  # noqa: F401
from typing import Dict, List, Optional, Sequence, Set, Tuple  # noqa: F401

from hdlab.state_register import *          # noqa: F401,F403
from hdlab import state_register as _sr
import sys as _sys

_self = _sys.modules[__name__]
for _n in dir(_sr):
    if not _n.startswith("__") and not hasattr(_self, _n):
        setattr(_self, _n, getattr(_sr, _n))


def has_privative_modifier(pred_tok) -> bool:
    """True if a predicate head is modified by a privative/non-subsective adjective ('a fake soldier',
    'a former captain') -> the state must NOT be asserted (Kamp & Partee 1995; research guard #1)."""
    for c in pred_tok.children:
        if c.dep_ in ("amod", "compound", "nmod", "advmod") and c.text.lower().strip("-") in _PRIVATIVE:
            return True
    return False

# ===========================================================================
# EXTRACTION ADAPTER (OUR-INVENTION-UNDER-TEST): prose -> abstract state events, via a spaCy dependency
# parse (perception-of-syntax). Lazy spaCy import so the tracking core stays parser-free. This is the
# analog of experiments/location_register.py's motion reader -- it emits (entity_span, value, aspect,
# polarity, kind) events the core folds. On raw 19c prose it is coverage-bounded (measured, not assumed).
# ===========================================================================

# Telic change-of-state verb -> resultant target-state value (the value a competent reader binds after the
# event; Parsons occurrence-fact + closable target-state). Curated glass-box lexicon (SWEEP, not adopt).
COS_VERB_RESULT: Dict[str, str] = {
    "open": "open", "shut": "shut", "close": "closed", "unlock": "unlocked", "lock": "locked",
    "break": "broken", "shatter": "shattered", "smash": "broken", "crack": "cracked", "mend": "mended",
    "repair": "repaired", "fix": "repaired", "wake": "awake", "waken": "awake", "awaken": "awake",
    "rouse": "awake", "light": "lit", "kindle": "lit", "extinguish": "unlit", "quench": "unlit",
    "empty": "empty", "fill": "full", "hide": "hidden", "conceal": "hidden", "reveal": "visible",
    "die": "dead", "kill": "dead", "perish": "dead", "freeze": "frozen", "melt": "melted",
    "lose": "lost", "find": "found", "free": "free", "release": "free", "imprison": "captive",
    "capture": "captive", "marry": "married", "widow": "widowed", "ruin": "ruined", "spoil": "spoiled",
}
# archaic BE-perfect participles (was become / was grown / was come / was gone / was fallen): the be-verb
# is the perfect auxiliary (19c), so these are PERFECT-aspect prior/resultant states, not passives.
_BE_PERFECT_PARTICIPLES = {"become", "grown", "come", "gone", "fallen", "risen", "arrived", "returned",
                           "changed", "turned", "married", "seated", "gathered", "assembled"}
# habitual / generic / modal guards -- constructions that are NOT a first-order state assertion.
_HABITUAL_CUES = {"habit", "wont", "custom", "use", "used", "accustomed", "apt", "liable", "wont"}
_BE_LEMMAS = {"be"}
_PERFECT_AUX = {"had", "has", "have", "'d", "'ve"}


def _neg_scope(v) -> bool:
    """True if the predication is negated (a `neg` child, or a 'no longer'/'never'/'not' modifier)."""
    for c in v.children:
        if c.dep_ == "neg":
            return True
        if c.text.lower() in ("never", "no") and c.dep_ in ("advmod", "neg", "det"):
            return True
    # 'no longer X'
    for c in v.subtree:
        if c.text.lower() == "longer":
            return True
    return False


_INVERSION_LEADS = {"had", "were", "should", "have", "has", "was", "hadst", "wert",
                    "couldst", "shouldst", "wouldst", "could", "would", "did"}


def _is_conditional_inversion(sent) -> bool:
    """Subject-aux INVERSION => conditional/counterfactual, NOT a state assertion ('Had he been a soldier,
    ...', 'Were she ill, ...'). Detect a clause-initial aux/finite-verb whose clause SUBJECT follows it."""
    toks = [t for t in sent if not t.is_space and t.text.strip()]
    if not toks:
        return False
    lead = toks[0]
    if lead.text.lower() not in _INVERSION_LEADS or lead.pos_ not in ("AUX", "VERB"):
        return False
    # the first subject of the sentence appears AFTER the leading aux => inversion (no subject precedes it)
    subj = next((t2 for t2 in sent if t2.dep_ in ("nsubj", "nsubjpass")), None)
    return subj is not None and subj.i > lead.i


# Non-entity SUBJECTS (relative/interrogative/demonstrative pronouns): a state predicated of these is not
# a trackable entity's state (the brain binds a state to a referential entity, not to a relativizer).
_SUBJ_BLOCK = {"which", "that", "what", "whatever", "who", "whom", "whose", "whoever", "whichever",
               "whatsoever", "there", "here", "this", "these", "those", "one", "none", "all", "some",
               "any", "each", "either", "neither", "both", "such"}
# Non-state PREDICATE nominals (interrogative / quantifier / light nouns): not a contentful state VALUE.
_PRED_BLOCK = {"what", "whatever", "one", "all", "who", "which", "that", "nothing", "something", "anything",
               "everything", "such", "none", "this", "it", "kind", "sort", "matter", "thing", "way",
               "number", "part", "deal", "lot", "sort", "manner", "any", "some", "who", "none", "here",
               "there", "no", "more", "less", "much", "many", "most", "enough", "case", "point"}


def _bad_subject(tok) -> bool:
    """A subject that is NOT a trackable entity (relativizer / interrogative / bare quantifier)."""
    if tok.tag_ in ("WDT", "WP", "WP$", "WRB"):
        return True
    if tok.text.lower() in _SUBJ_BLOCK:
        return True
    return False


def _pred_value(tok) -> Optional[str]:
    """The state VALUE from a predicate token, with a content gate. Adjective -> lemma; noun -> lemma;
    predicative past-participle -> its surface form ('known', 'broken', 'kept'); rejects interrogative /
    quantifier / light nouns and any VERB-tagged non-participle (a parse artifact, not a state)."""
    lem = tok.lemma_.lower()
    txt = tok.text.lower().strip(".,;:'\"!?")
    if tok.pos_ == "ADJ" or tok.tag_ in ("JJ", "JJR", "JJS"):
        return lem if lem not in _PRED_BLOCK else None
    if tok.tag_ == "VBN":                       # predicative participle: 'was tired/broken/known/kept'
        return txt if txt not in _PRED_BLOCK else None
    if tok.pos_ in ("NOUN", "PROPN") or tok.tag_ in ("NN", "NNS", "NNP", "NNPS"):
        return lem if lem not in _PRED_BLOCK else None
    return None                                  # VERB / DET / PRON predicate = parse artifact, not a state


def extract_state_events(nlp, text: str):
    """Parse `text` and return a list of raw state events, each a dict:
       {kind: 'state'|'event', subj_span:(a,b), subj_head:str, value:str, aspect:str, polarity:int,
        verb:str|None, t:int, source:str}
    subj_span is a character span into `text` (for gold-coref binding). t = sentence index. Glass-box.

    STATE: copular/perfect predication (X is/was/had been ADJ/NP; archaic X was become/grown Y).
    EVENT: telic change-of-state verb (the door opened -> door is-open) with its patient.
    Wall-guarded: skips conditional subject-aux inversions and habitual 'in the habit of' constructions."""
    doc = nlp(text)
    events = []
    for si, sent in enumerate(sent_list(doc)):
        if _is_conditional_inversion(sent):
            continue
        # -- copular / perfect predication (INCLUDING 'be + participle' as a STATE, not an event) --------
        for tok in sent:
            head = tok
            # (A) a be-verb head with an acomp/attr/oprd predicate ('was ill', 'had been a soldier').
            is_be = tok.lemma_.lower() in _BE_LEMMAS and tok.pos_ in ("AUX", "VERB")
            # (B) a participle head with a be-aux ('was locked', 'was become a woman', 'had been broken') --
            #     a copular/passive STATE, NOT a fresh telic event (the entity IS in the resultant state).
            has_be_aux = any(c.lemma_.lower() in _BE_LEMMAS and c.dep_ in ("aux", "auxpass")
                             for c in tok.children)
            is_participle_state = (tok.tag_ == "VBN" and tok.lemma_.lower() not in _BE_LEMMAS and has_be_aux)
            if not (is_be or is_participle_state):
                continue
            # existential 'there is/was/has been X' has an expletive subject, no entity -> skip
            if any(c.dep_ == "expl" for c in head.children):
                continue
            subj = next((c for c in head.children if c.dep_ in ("nsubj", "nsubjpass")), None)
            if subj is None:
                # only a DIRECTLY-attached subject (avoid grabbing a matrix subject across a clause, e.g.
                # 'We know there has been a presentation' -> do NOT bind 'we' to the embedded predicate)
                subj = next((c for c in head.head.children if c.dep_ in ("nsubj", "nsubjpass")), None) \
                    if head.dep_ in ("acomp", "attr", "oprd", "xcomp") else None
            if subj is None or _bad_subject(subj):
                continue
            # irrealis guard: a copular state inside an 'if/unless/whether/though' clause is NOT asserted
            # ('if he had been clean', 'if knighthood were hereditary'); distinct from the inversion guard.
            _cond = {"if", "unless", "whether", "lest", "though", "although"}
            if any(c.dep_ == "mark" and c.text.lower() in _cond
                   for anc in ([head] + list(head.ancestors)) for c in anc.children):
                continue
            # modal-perfect irrealis ('he would/could/might/should have been a soldier') -> counterfactual,
            # not asserted into the real timeline (Iatridou 2000; research drill wall-check item #5).
            if any(c.tag_ == "MD" for c in head.children if c.dep_ in ("aux", "auxpass")) or \
               any(t.tag_ == "MD" and t.head.i in (head.i, head.head.i) and t.dep_ in ("aux", "auxpass")
                   for t in sent):
                continue
            # habitual guard: skip only when the habit cue IS the predicate ('was in the habit of', 'was wont')
            if any(c.dep_ in ("acomp", "attr", "prep") and any(g.text.lower() in _HABITUAL_CUES
                    for g in c.subtree) for c in head.children):
                continue
            # perfect aspect if a perfect aux is present on the be chain (had/has been ...), OR the head is
            # an archaic BE-perfect participle ('was become/grown/come/gone' -- 19c perfect, wall-check #9).
            aspect = CURRENT
            if any((c.lemma_.lower() in _PERFECT_AUX or c.text.lower() in _PERFECT_AUX)
                   for c in head.children if c.dep_ in ("aux", "auxpass")):
                aspect = PRIOR
            elif is_participle_state and head.lemma_.lower() in _BE_PERFECT_PARTICIPLES:
                aspect = PRIOR
            polarity = -1 if _neg_scope(head) else 1
            if is_participle_state:
                lem = head.lemma_.lower()
                pred = next((c for c in head.children if c.dep_ in ("attr", "acomp", "oprd", "dobj")), None)
                if lem in COS_VERB_RESULT and pred is None:
                    value = COS_VERB_RESULT[lem]          # 'was locked' -> locked ; 'was broken' -> broken
                elif pred is not None:
                    value = _pred_value(pred)             # 'was become a woman' -> woman ; 'was grown old' -> old
                else:
                    value = head.text.lower().strip(".,;:'\"!?")   # 'was gone'->gone; 'been born'->born; 'known'
            else:
                pred = next((c for c in head.children if c.dep_ in ("acomp", "attr", "oprd")), None)
                if pred is None:
                    continue
                value = _pred_value(pred)
            # privative guard: 'a fake soldier' / 'a former captain' -> the property is cancelled/suspended,
            # do NOT assert it (Kamp & Partee 1995; research guard #1).
            if pred is not None and has_privative_modifier(pred):
                continue
            if not value:
                continue
            events.append(dict(kind="state", subj_span=(subj.idx, subj.idx + len(subj.text)),
                               subj_head=subj.text.lower(), value=value, aspect=aspect,
                               polarity=polarity, verb=None, t=si,
                               source=sent.text.strip()[:120]))
        # -- resultant state of an ACTIVE telic change-of-state verb (NOT a 'be + participle' copular) -----
        for tok in sent:
            if tok.pos_ != "VERB":
                continue
            lem = tok.lemma_.lower()
            if lem not in COS_VERB_RESULT:
                continue
            # must be a FINITE active verb (an asserted event), not a participial modifier ('dying people',
            # 'the opened door') or gerund -- those are not first-order telic assertions of a state change.
            if tok.tag_ not in ("VBD", "VBZ", "VBP") or tok.dep_ in ("amod", "acl"):
                continue
            # a 'be + participle' reading was already captured as a STATE above -> skip here (no double-count)
            if any(c.lemma_.lower() in _BE_LEMMAS and c.dep_ in ("aux", "auxpass") for c in tok.children):
                continue
            # skip irrealis (modal / conditional / negated) -> the resultant state is not asserted
            if any(c.dep_ == "aux" and c.tag_ == "MD" for c in tok.children):
                continue
            if _neg_scope(tok):
                continue
            # patient: a direct object (transitive 'she opened the door') else the subject (unaccusative
            # 'the door opened'). The patient is the entity whose state changes.
            dobj = next((c for c in tok.children if c.dep_ in ("dobj", "obj")), None)
            patient = dobj if dobj is not None else next(
                (c for c in tok.children if c.dep_ in ("nsubj", "nsubjpass")), None)
            if patient is None or _bad_subject(patient):
                continue
            events.append(dict(kind="event", subj_span=(patient.idx, patient.idx + len(patient.text)),
                               subj_head=patient.text.lower(), value=COS_VERB_RESULT[lem], aspect=RESULT,
                               polarity=1, verb=lem, t=si, source=sent.text.strip()[:120]))
    return events


def sent_list(doc):
    try:
        return list(doc.sents)
    except Exception:
        return [doc[:]]


class StateReader:
    """Prose -> StateRegister adapter (the OUR-INVENTION front-end). read(text, entities) parses the text,
    extracts state events, binds each to an entity via its aliases, and folds them into a StateRegister.

    entities: {canonical_name: [aliases...]}. A raw subject head is bound to the entity whose alias set
    contains it (case-insensitive). Unbound state events are dropped (coverage-bounded, reported)."""

    def __init__(self, nlp=None):
        self._nlp = nlp

    def _nlp_or_load(self):
        if self._nlp is None:
            import spacy
            self._nlp = spacy.load("en_core_web_sm")
        return self._nlp

    def read(self, text: str, entities: Dict[str, Sequence[str]]) -> "StateRegister":
        nlp = self._nlp_or_load()
        alias_to_name = {}
        for name, al in entities.items():
            for a in list(al) + [name]:
                alias_to_name[a.lower()] = name
        raw = extract_state_events(nlp, text)
        reg = StateRegister().start(list(entities.keys()))
        for ev in raw:
            name = alias_to_name.get(ev["subj_head"])
            if name is None:
                continue
            if ev["kind"] == "state":
                reg.apply_state(name, ev["value"], aspect=ev["aspect"], polarity=ev["polarity"],
                                t=ev["t"], source=ev["source"])
            else:
                reg.apply_event(name, ev["verb"], ev["value"], t=ev["t"], source=ev["source"])
        return reg


# ---------------------------------------------------------------------------
# Self-test: the discriminating cases a STATELESS most-recent-adjective / entity-blind baseline gets WRONG,
# fed as abstract events (isolates the TRACKING mechanism from extraction).
# ---------------------------------------------------------------------------
