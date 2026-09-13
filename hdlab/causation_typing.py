"""Force-dynamic CAUSE/ENABLE/PREVENT typing of within-clause causatives, for the live reader.

Promoted 2026-08-31 for the causation-dimension live-reader landing. This is a FAITHFUL port of the
validated typed-causation logic from experiments/exp_wire_causation_typer_live_reader_v1.py (the
module-level helpers + the WiredCausationReader within-clause typing path) plus the GRADED foreground
event-hood gate from experiments/_foreground_eventhood.py. No logic/thresholds changed.

BRAIN MECHANISM (PINNED unless noted):
  TYPING     -- Talmy 1988 / Wolff 2007 (force theory of causation) / Wolff & Song 2003: CAUSE / ENABLE
                / PREVENT fall out of a small discrete truth-table over (patient-tendency, affector/
                patient concordance, endstate-reached). The verb's force class (FrameNet Causation
                family) supplies the first two in compressed form; the narrative outcome supplies the
                endstate bit; a patient-tendency estimator resolves tendency-ambiguous verbs.
  DETECT     -- verb-/construction-triggered causative detection (Goldberg construction grammar + the
                FrameNet force lexicon).
  BIND ROLES -- actor-first thematic assignment (eADM; Bornkessel-Schlesewsky & Schlesewsky 2006):
                affector = nsubj Actor, patient = dobj/nsubjpass Undergoer.
  READ END-  -- telicity/culmination + prevention-as-negation (Pinango 1999; Kaup 2007; Wolff & Barbey
    STATE      2015): force dynamics natively represents a never-realised endstate (the PREVENT case).
  FOREGROUND -- (graded gate) causal encoding is a by-product of event-model construction; only a
                FOREGROUNDED EVENT is a causal-arc candidate (Zwaan & Radvansky 1998 event-indexing;
                Hopper & Thompson 1980 transitivity-gradient -> foregrounding; Zacks 2007). OUR-INVENTION:
                the exact feature legs, weights, and engage threshold theta (swept).

DEFAULT-OFF in the reader: SituationReader gains a `causation_typed` flag delegating here. Plain
`import hdlab.causation_typing` is cheap -- the parse is the IN-SUBSTRATE frontend (pos_tagger +
arc_parser + arc_labeler; ZERO spaCy, owner 2026-09-08), and the literalness/WSD gate is LAZILY imported from
experiments/ (its own separate queued promotion; NOT promoted here). NO external LLM/tool at inference
(in-substrate parse + NLTK FrameNet/WordNet only). ASCII only. Deterministic.
"""
from __future__ import annotations
from hdlab import morphology as _gbm   # glass-box morphy (byte-identical; no nltk on the lemma path)

__bf_status__ = 'BF_SPIRIT'   # BF | BF_SPIRIT | NOT_BF | BF_UNPINNED | BF_UNVERIFIED ; mirrors notes/bf_status_registry.jsonl
__bf_verified__ = '2026-09-09 BF-certification pass (operation/math read of the pinned computation + key ops; strategy first-hand)'
__bf_note__ = 'Wolff/Talmy force-dynamic CAUSE/ENABLE/PREVENT typing of within-clause causatives + graded foreground event-hood gate; pinned force-dynamics op; DORMANT (causation_typed=False)'
__bf_corrections__ = []


import os

from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence

from hdlab.force_dynamics_lexicon import (
    build_force_lexicon, force_dynamic_type, detect_endstate_reached)
from hdlab.patient_tendency import (
    type_with_full_tendency, AMBIGUOUS_VERBS, lemmatize_verb)

TYPES = ("CAUSE", "ENABLE", "PREVENT")

# ===========================================================================
# TypedCausalLink -- the causation-dimension extension to hdlab's CausalLink (ctype + endstate_reached).
# ===========================================================================
@dataclass
class TypedCausalLink:
    sent_idx: int
    affector: str
    verb: str
    patient: str
    ctype: str                 # CAUSE | ENABLE | PREVENT | NO_CAUSATION | SEQUENTIAL | ABSTAIN
    endstate_reached: bool
    engage_label: str          # literalness-gate label (ENGAGE_PHYSICAL / FORCE_NONPHYSICAL / ABSTAIN)
    source: str = "within_clause"


# a PREVENT-construction path marker ("keep/save/stop/prevent X FROM Ving"): the prevention SUCCEEDS by
# default (endstate NOT reached) unless the prevention itself is negated ("could not keep X from ...").
_FROM_PREP = {"from"}
# directional PATH/goal prepositions that make a clause a CAUSED-MOTION construction (Talmy path satellite).
_PATH_PREPS = {"into", "onto", "off", "out", "down", "up", "across", "through", "to", "toward",
               "towards", "over", "away", "back", "in", "on", "against", "upon"}
# periphrastic CAUSE verbs (Goldberg caused-change; make/have/get carry the causation, the real predicate
# is the complement). Treated as CAUSE-class for the construction even if the FrameNet lexicon lacks them.
_PERIPHRASTIC_CAUSE = {"make", "have", "get", "cause", "force", "render", "drive", "set"}
# reliable NON-physical-force verb-sense frames (the WSD organ commits to these reliably): a force-lexicon
# verb committed to one of these in context is NOT in its force-dynamic sense -> the sense gate abstains.
_NONFORCE_FRAMES = {"perception", "cognition", "communication", "possession", "stative", "social", "emotion"}

# ---------------------------------------------------------------------------
# FORCE-EVENT DISCRIMINATION -- the brain-foundational fix (deep drill 2026-08-30). NOT verb-sense
# classification (measured net-harmful): read THREE force-relevant constraints off the ARGUMENTS and let
# them VOTE (graded). PINNED: constraint satisfaction over verb+args (McRae/Spivey-Knowlton/Tanenhaus 1998;
# Elman 2009), affectedness (Dowty 1991; Beavers 2011), affector force-fit (Wolff 2007; Paczynski &
# Kuperberg 2012 animacy), eventivity (Gennari & Poeppel 2003), light-verb-from-qualia (Pustejovsky 1995).
# OUR-INVENTION: the WordNet buckets / stative + force lexicons / weights / threshold.
# ---------------------------------------------------------------------------
# Leg C: STATIVE verb senses (Vendler states) -- a state that holds, not a dynamic caused change. Coarse
# closed-class cue (a vote, not a veto -- a stative verb with an affected patient + a from-construction can
# still engage). Deliberately EXCLUDES polysemous force verbs whose force sense is common (hold/keep are in
# the force lexicon; here they contribute a stativity VOTE only).
_STATIVE_VERBS = {"have", "own", "possess", "know", "believe", "contain", "see", "hear", "inherit",
                  "belong", "cost", "weigh", "consist", "comprise", "lack", "resemble", "seem", "appear",
                  "exist", "remain", "sit", "stand", "lie", "occupy", "hold", "keep", "want", "need"}
# Leg B: natural-force / energy affectors (physical entities already fit via WordNet physical_entity).
_FORCE_NOUNS = {"storm", "wind", "gust", "gale", "fire", "flame", "water", "wave", "flood", "current",
                "tide", "quake", "earthquake", "blast", "explosion", "avalanche", "gravity", "pressure",
                "heat", "cold", "frost", "sun", "rain", "lightning", "thunder", "hurricane", "tornado"}
_ABSTRACT_EVENTIVE_ROOTS = {"abstraction.n.06", "act.n.02", "event.n.01", "communication.n.02",
                            "cognition.n.01", "state.n.02", "psychological_feature.n.01",
                            "attribute.n.02", "measure.n.02", "relation.n.01", "group.n.01"}
_PHYSICAL_ROOT = "physical_entity.n.01"
# WordNet SUPERSENSE (lexname) buckets -- the clean event-nominal vs physical-patient discriminator
# (Pustejovsky event nominals: "make an APPLICATION/PRETENCE/JUDGMENT" -> the event is in the object's
# qualia, no affected patient). Physical -> affectable; abstract/eventive -> light-verb/creation.
_PHYSICAL_LEX = {"noun.artifact", "noun.substance", "noun.body", "noun.animal", "noun.plant",
                 "noun.food", "noun.object", "noun.person", "noun.location", "noun.shape"}
_ABSTRACT_LEX = {"noun.act", "noun.cognition", "noun.communication", "noun.attribute", "noun.feeling",
                 "noun.state", "noun.event", "noun.motive", "noun.relation"}


def _wn_lexname(noun):
    try:
        from nltk.corpus import wordnet as wn
    except Exception:
        return None
    n = (noun or "").strip().lower()
    syn = wn.synsets(n, pos=wn.NOUN)
    if not syn:
        lem = _gbm.morphy(n, "n")
        if lem:
            syn = wn.synsets(lem, pos=wn.NOUN)
    return syn[0].lexname() if syn else None
_ANIMATE_ROOTS = ("person.n.01", "animal.n.01", "causal_agent.n.01")
_PERSON_PRON = {"he", "she", "they", "i", "we", "you", "him", "her", "them", "me", "us"}
# referentially-OPEN pronouns (it/this/that): could denote a concrete entity -> NEUTRAL (the brain resolves
# them via coref; coupling causation to the reader's coref is the named follow-on). Only the genuinely
# NON-referential quantifiers (nothing/none) denote no affectable patient.
_OPEN_PRON = {"it", "this", "that", "which", "who", "what", "one", "these", "those"}
_NULL_PRON = {"nothing", "none", "anything", "everything", "something", "all"}


def _wn_noun_roots(noun):
    try:
        from nltk.corpus import wordnet as wn
    except Exception:
        return set()
    roots = set()
    n = (noun or "").strip().lower()
    syn = wn.synsets(n, pos=wn.NOUN)
    if not syn:
        lem = _gbm.morphy(n, "n")
        if lem:
            syn = wn.synsets(lem, pos=wn.NOUN)
    for s in syn[:4]:
        for path in s.hypernym_paths():
            roots |= {h.name() for h in path}
    return roots


def _leg_patient_affectedness(patient) -> int:
    """+1 a pre-existing CONCRETE entity that can undergo change; -2 an EVENTIVE/ABSTRACT object (light-verb
    /creation -- no pre-existing patient to type; the WIDEST + strongest cue per the drill, so it cannot be
    out-voted by an animate agent -- "the prisoner MAKES an application"); 0 unknown."""
    if not patient:
        return 0
    p = patient.strip().lower()
    if p in _NULL_PRON:
        return -2                       # nothing/none: no affectable patient denoted
    if p in _OPEN_PRON:
        return 0                        # it/that: referentially open -> neutral (needs coref)
    if p in _PERSON_PRON:
        return 1                        # a person can be affected
    # WordNet IS-A roots (broad, forgiving -- measured better than the first-synset lexname, which cost
    # curated recall on group/phenomenon patients). physical_entity -> affectable; abstract/eventive ->
    # light-verb/creation. (The lexname supersense is a cleaner cut in ISOLATION but the reader's real
    # extracted patients need the broad root test.)
    roots = _wn_noun_roots(p)
    if not roots:
        return 0
    phys = _PHYSICAL_ROOT in roots
    absev = bool(roots & _ABSTRACT_EVENTIVE_ROOTS)
    if phys and not absev:
        return 1
    if absev and not phys:
        return -2                       # eventive/abstract object -> light-verb/creation (strong veto)
    return 0


def _leg_affector_forcefit(affector) -> int:
    """+1 a plausible FORCE source (animate agent / natural force / physical instrument); -1 an
    abstract/institutional holder; 0 none/unknown (no subject -> neutral, e.g. imperative/passive)."""
    if not affector:
        return 0
    a = affector.strip().lower()
    if a in _PERSON_PRON:
        return 1
    if a in _OPEN_PRON:
        return 0
    if a in _FORCE_NOUNS:
        return 1
    roots = _wn_noun_roots(a)
    if not roots:
        return 0
    if any(r in roots for r in _ANIMATE_ROOTS):
        return 1
    phys = _PHYSICAL_ROOT in roots
    absev = bool(roots & _ABSTRACT_EVENTIVE_ROOTS)
    if phys and not absev:
        return 1                        # a physical thing can exert force (instrument)
    if absev and not phys:
        return -1                       # abstract/institutional holder (court/favour/...)
    return 0


def _leg_eventivity(vlem) -> int:
    """+1 dynamic (a happening/change); -1 STATIVE (a state that holds)."""
    return -1 if vlem in _STATIVE_VERBS else 1


def force_engagement_score(affector, vlem, patient) -> int:
    """The graded force-engagement VOTE (deep drill): sum of the three argument-read constraints. Higher =
    more force-event-like. Engage force typing iff score >= theta (swept)."""
    return (_leg_patient_affectedness(patient) + _leg_affector_forcefit(affector) + _leg_eventivity(vlem))


# ---------------------------------------------------------------------------
# FOREGROUNDED-EVENT gate (deep drill #4: the DECISION TO ENCODE). Causal encoding is a by-product of
# event-model construction -- only a FOREGROUNDED EVENT is a causal-arc candidate; a backgrounded clause
# (participial adjunct / relative / appositive) or a NAMING frame never becomes a main event. The scanner
# over-generates by deciding at VERB-LEXICON grain instead of EVENT-NODE grain (a category error). This is
# a PRECISION FILTER ON EVENT-HOOD, not a suppressor on causation (the brain is causal-by-default; Sanders).
# PINNED: event-indexing (Zwaan & Radvansky 1998), aspect grounding (Hopper 1979), event segmentation
# (Zacks). OUR-INVENTION: the dependency->foreground mapping, the naming-frame test.
# ---------------------------------------------------------------------------
_BACKGROUND_DEPS = {"acl", "relcl", "appos"}      # noun-modifying clauses = background, not main-line events


def is_foregrounded_event(vtok) -> bool:
    """B3 foreground grounding: the verb must head a MAIN-LINE clause, not a noun-modifying or participial
    adjunct ("smoke ... MAKING a drizzle", "the court WHICH HAS its houses" are background)."""
    if vtok.dep_ in _BACKGROUND_DEPS:
        return False
    if vtok.dep_ == "advcl" and vtok.tag_ in ("VBG", "VBN") and not any(
            c.dep_ in ("aux", "auxpass", "nsubj", "nsubjpass", "mark") for c in vtok.children):
        return False                              # bare participial adverbial = background
    return True


def is_naming_frame(vtok) -> bool:
    """B2 naming/dubbing frame ("CALL a native a pig", "NAME the child Sam"): verb + direct object + an
    object-complement NOMINAL -- an equative/labelling relation, not a caused physical change."""
    has_obj = any(c.dep_ in ("dobj", "obj") for c in vtok.children)
    has_nom_complement = any(c.dep_ in ("oprd", "attr") and c.pos_ in ("NOUN", "PROPN")
                             for c in vtok.children)
    return has_obj and has_nom_complement


# ===========================================================================
# GRADED foreground / event-hood gate (ported from experiments/_foreground_eventhood.py; the p3
# improvement over the boolean is_foregrounded_event). Hopper & Thompson (1980) transitivity is a GRADIENT
# (a cluster of co-varying parameters) that PREDICTS foregrounding; a graded event-hood SCORE over that
# cluster passes a HIGH-transitivity causative in a subordinate clause (recall held) while vetoing a LOW-
# transitivity stative/generic/backgrounded clause (precision raised). PINNED: causal encoding over
# foregrounded EVENT nodes; transitivity-gradient -> foregrounding; aspect as an online foreground signal.
# OUR-INVENTION (built + swept in the source cell): the exact feature legs, weights, and threshold theta.
# ===========================================================================
# LEG 1 -- DYNAMICITY / KINESIS (Hopper&Thompson param A; Vendler states; Levin stative classes). A state
# that HOLDS is not a foreground event. Superset of _STATIVE_VERBS (which was tuned for the SENSE leg).
_STATIVE_RELATIONAL = {
    "be", "have", "own", "possess", "contain", "hold", "comprise", "consist", "belong", "constitute",
    "represent", "include", "involve", "lack", "concern", "regard", "resemble", "remain", "exist",
    "stay", "seem", "appear", "look", "sound", "equal", "measure", "weigh", "cost", "matter", "count",
    "depend", "range", "extend", "stand", "sit", "lie", "occupy", "surround", "face", "border",
    # perception / cognition (stative senses -- LitBank tags these O)
    "know", "believe", "think", "understand", "realize", "realise", "suppose", "imagine", "doubt",
    "mean", "see", "hear", "feel", "notice", "perceive", "recognize", "recognise", "wonder", "expect",
    "want", "wish", "need", "prefer", "love", "hate", "like", "dislike", "fear", "hope", "mind",
    "deserve", "owe", "require",
}
# LEG 4 -- REALIS / affirmation & mode (Hopper&Thompson params I mode, J affirmation). A negated or
# hypothetical clause is not an asserted foreground event (LitBank annotates REALIS events only).
_IRREALIS_MODALS = {"would", "could", "might", "should", "may", "must", "shall", "can", "ca"}
# LEG 2 -- GROUNDING (Hopper 1979 foreground/background via the parse). GRADED, not a hard kill.
_BG_NOUN_MOD = {"acl", "relcl", "appos"}          # noun-modifying clauses = background
_MAINLINE = {"ROOT", "conj", "parataxis"}


def _leg_dynamicity(vlem: str) -> int:
    return -2 if vlem in _STATIVE_RELATIONAL else 1


def _leg_grounding(vtok) -> int:
    dep = vtok.dep_
    if dep in _MAINLINE:
        return 1
    if dep in _BG_NOUN_MOD:
        return -2
    if dep == "advcl":
        # bare participial free adjunct (VBG/VBN, no subject/aux/mark) = background; finite advcl = neutral
        finite = any(c.dep_ in ("aux", "auxpass", "nsubj", "nsubjpass", "mark") for c in vtok.children)
        if vtok.tag_ in ("VBG", "VBN") and not finite:
            return -2
        return 0
    if dep in ("ccomp", "xcomp", "pcomp"):
        return 0                                    # complement clause -- neutral (can be an event)
    return 0                                         # conj-less / other -- neutral


def _leg_aspect(vtok) -> int:
    """Hopper: perfective/bounded = foreground; imperfective/progressive/gnomic-present = background.
    Read off the tense/aspect morphology + aux children."""
    tag = vtok.tag_
    auxlemmas = {c.lemma_.lower() for c in vtok.children if c.dep_ in ("aux", "auxpass")}
    if tag == "VBG":
        # progressive (be + VBG) = imperfective/backgroundable; bare VBG handled by grounding
        return -1 if ("be" in auxlemmas) else 0
    if tag == "VBN":
        return 1 if ("have" in auxlemmas) else 0    # perfect = bounded/foreground; bare passive = neutral
    if tag == "VBD":
        return 1                                     # simple past = the canonical foreground tense
    if tag in ("VBZ", "VBP"):
        return -1                                    # gnomic/habitual present = description (downweight)
    return 0                                          # VB base / infinitive


def _leg_individuation(ptok, patient: str) -> int:
    """Hopper&Thompson param individuation of O: a SPECIFIC referential patient is transitive/foreground;
    a GENERIC / bare-plural / kind-referring object is a description. Read off the object token's
    determiner + POS."""
    if ptok is None:
        return 0                                      # no object (intransitive) -- neutral, not penalized
    if ptok.pos_ == "PROPN":
        return 1
    if ptok.pos_ == "PRON":
        # a wh-/relative/indefinite/expletive pro-form (do WHAT, make WHO) is NON-referential = a
        # light/pro-verb frame, not an affected individuated patient (-1); a referentially-OPEN pronoun
        # (it/that/this) needs coref -> NEUTRAL (0, as the p2 gate found); a bound personal pronoun
        # (him/her/them...) is individuated (+1). Hopper&Thompson individuation of O.
        pl = ptok.lemma_.lower()
        if pl in ("what", "who", "whom", "whose", "which", "there", "something", "anything", "nothing"):
            return -1
        if pl in ("it", "that", "this", "these", "those"):
            return 0
        return 1                                      # he/she/they/him/her/us/me... referential
    dets = {c.lemma_.lower() for c in ptok.children if c.dep_ in ("det", "poss")}
    if dets & {"the", "this", "that", "these", "those", "my", "his", "her", "its", "their", "our", "your"}:
        return 1                                      # definite / demonstrative / possessive = specific
    if ptok.tag_ == "NNS" and not dets:
        return -1                                     # bare plural = kind/generic reference
    if ptok.tag_ == "NN" and not dets:
        return -1                                     # bare mass/generic
    return 0


def eventhood_legs(vtok, affector: str, patient: str, ptok, vlem: str) -> Dict[str, int]:
    """Every leg, transparently, for auditing/ablation."""
    neg = any(c.dep_ == "neg" or c.lemma_.lower() in ("not", "never", "no") for c in vtok.children)
    auxlemmas = {c.lemma_.lower() for c in vtok.children if c.dep_ in ("aux", "auxpass")}
    marks = {c.lemma_.lower() for c in vtok.children if c.dep_ == "mark"}
    irrealis = bool(auxlemmas & _IRREALIS_MODALS) or ("if" in marks)
    realis = -2 if neg else (-1 if irrealis else 0)
    return {
        "dyn": _leg_dynamicity(vlem),                                  # kinesis (B1)
        "ground": _leg_grounding(vtok),                               # foreground grounding (B3, graded)
        "aspect": _leg_aspect(vtok),                                  # boundedness (B4/Hopper)
        "indiv": _leg_individuation(ptok, patient),                   # individuation of O (B4)
        "affect": _leg_patient_affectedness(patient),                # affectedness of O (Dowty; shared leg)
        "realis": realis,                                            # affirmation/mode (Hopper)
    }


# the discourse legs that are NEW relative to the p2 argument SENSE gate (dynamicity/affectedness already
# read there). Used for the ablation that isolates the foreground gate's marginal lift.
_DISCOURSE_LEGS = ("ground", "aspect", "indiv", "realis")
# THE DEFAULT GATE (chosen by the INDEPENDENT leg-alignment measurement + held-out validation): the three
# cleanest Hopper transitivity parameters -- ASPECT (dominant online foreground signal), INDIVIDUATION of
# O, REALIS/affirmation. GROUNDING (dep-attachment) is dropped (weakest separator + net-harmful even as a
# categorical veto); DYNAMICITY + AFFECTEDNESS are dropped from the SCORE (they duplicate the upstream
# force-SENSE gate; kinesis survives as the categorical STATIVE veto).
DEFAULT_LEGS = ("aspect", "indiv", "realis")
# Engage threshold for the graded gate on DEFAULT_LEGS. OUR-INVENTION (swept in the source experiment); the
# graded gate is DEFAULT-OFF in the reader, so this constant only takes effect when a caller passes
# graded_foreground=True without an explicit theta. Placeholder default; the strategy session sets the
# operating theta from the sweep when/if the graded gate is turned on.
THETA_DEFAULT = 1


def eventhood_score(vtok, affector: str, patient: str, ptok, vlem: str,
                    legs: Optional[List[str]] = None) -> int:
    d = eventhood_legs(vtok, affector, patient, ptok, vlem)
    keys = legs if legs is not None else list(d.keys())
    return sum(d[k] for k in keys)


# ===========================================================================
# DETECT + BIND ROLES + CONSTRUCTION + ENDSTATE + TYPE -- ported verbatim from
# WiredCausationReader's methods (self._lex -> lex, self.use_constructions -> use_constructions,
# self.tendency -> tendency).
# ===========================================================================
def _from_complement(vtok) -> Optional[str]:
    """The 'FROM Ving/N' complement of a prevention verb (keep/save/stop/prevent X FROM Y). The 'from'
    can attach to the verb OR to the dobj ('saved the driver FROM injury'); scan both + the subtree."""
    heads = [vtok] + [c for c in vtok.children if c.dep_ in ("dobj", "obj", "advcl", "xcomp")]
    for h in heads:
        for c in h.children:
            if c.dep_ in ("prep", "obl", "advcl", "prt") and c.text.lower() in _FROM_PREP:
                head = next((g.lemma_.lower() for g in c.children
                             if g.dep_ in ("pobj", "obj", "pcomp")), None)
                return head or "from"
            if c.dep_ in ("advcl", "xcomp") and any(g.text.lower() == "from" for g in c.children):
                return c.lemma_.lower()
    return None


def _causative_candidate(sent, vtok, lex, use_constructions):
    """DETECT + BIND ROLES + CONSTRUCTION: a within-clause causative candidate. Construction grammar
    (Goldberg 1995): the same force triple is recoverable across lexical, periphrastic, resultative,
    caused-motion and inchoative constructions. Returns a dict (or None)."""
    vlem = vtok.lemma_.lower()
    cls = lex.get(vlem)
    is_ambig = vlem in AMBIGUOUS_VERBS
    is_periph = vlem in _PERIPHRASTIC_CAUSE
    subj = next((c for c in vtok.children if c.dep_ in ("nsubj", "nsubjpass")), None)
    obj = next((c for c in vtok.children if c.dep_ in ("dobj", "obj")), None)
    passive = any(c.dep_ == "nsubjpass" for c in vtok.children) or \
        any(c.dep_ == "auxpass" for c in vtok.children)
    from_comp = _from_complement(vtok)
    # PERIPHRASTIC/LETTING (let/allow/make/have/get X [to] V): causee (patient) = complement subject.
    comp = next((c for c in vtok.children if c.dep_ in ("ccomp", "xcomp", "advcl")), None)
    comp_causee = None
    if comp is not None:
        # causee = the complement's subject; fall back to its object/compound when spaCy mis-parses the
        # bare-infinitive causee ("made the baby cry" -> spaCy reads "baby" as compound of "cry").
        for dep in ("nsubj", "nsubjpass", "dobj", "obj", "attr", "compound"):
            comp_causee = next((g for g in comp.children if g.dep_ == dep), None)
            if comp_causee is not None:
                break
    # RESULTATIVE: a result secondary predicate -- an ADJ predicated of the object (oprd/acomp), or an
    # ADJ complement ("hammered it FLAT", "wiped it CLEAN"). The endstate is the adjective (RH&L).
    result_xp = next((c for c in vtok.children if c.dep_ in ("oprd", "acomp", "advcl", "xcomp")
                      and c.pos_ == "ADJ"), None)
    # CAUSED-MOTION: a directional PATH goal WITH A GROUND ("pushed the cart INTO the BARN"); Talmy's
    # caused-motion needs a path landmark. A BARE PARTICLE ("held OUT his hat", "reached UP") is a
    # phrasal-verb/aspect marker, NOT a caused-motion path -- require a real prep + pobj ground (this
    # halves the open-text over-fire).
    path_pp = next((c for c in vtok.children if c.dep_ in ("prep", "obl")
                    and c.text.lower() in _PATH_PREPS
                    and any(g.dep_ in ("pobj", "obj") for g in c.children)), None)
    # A PERIPHRASTIC causative REQUIRES the caused-event COMPLEMENT ("made her LAUGH", "had them
    # REWRITE"); a bare "have X" / "get X" is POSSESSION/acquisition, NOT causation -- requiring the
    # complement kills the dominant open-text false-positive class (has houses / has knowledge).
    is_periph_cxn = (comp is not None) and (is_periph or comp_causee is not None)
    # DETECT: force-lexicon verb, OR tendency-ambiguous+object, OR a construction (resultative /
    # caused-motion / periphrastic-cause). Else not a within-clause causative.
    fire = (cls is not None) or (is_ambig and obj is not None)
    if use_constructions:
        fire = fire or (result_xp is not None) or (path_pp is not None and obj is not None) \
            or is_periph_cxn
    if not fire:
        return None
    # role binding (actor-first; passive; periphrastic causee; from-event; inchoative subject)
    if passive and subj is not None:
        patient = subj.text.lower()
        affector = next((g.lemma_.lower() for c in vtok.children if c.dep_ in ("agent", "obl", "prep")
                         for g in c.children if g.dep_ in ("pobj", "obj")), "")
        ptok = subj
    else:
        affector = subj.text.lower() if subj is not None else ""
        if obj is not None:
            patient, ptok = obj.text.lower(), obj
        elif comp_causee is not None:
            patient, ptok = comp_causee.text.lower(), comp_causee
        elif from_comp is not None:
            patient, ptok = from_comp, None
        elif is_ambig and subj is not None:
            patient, ptok, affector = subj.text.lower(), subj, ""   # inchoative: subject = patient
        else:
            return None
    # construction label (priority: resultative > periphrastic > caused-motion > inchoative > lexical)
    if result_xp is not None:
        construction = "resultative"
    elif is_periph_cxn:
        construction = "periphrastic"           # make/have/get/let/allow X [to] V (complement required)
    elif path_pp is not None and obj is not None:
        construction = "caused_motion"
    elif obj is None and affector == "" and is_ambig:
        construction = "inchoative"
    else:
        construction = "lexical"
    if not use_constructions:
        construction = "lexical"                # ablation: no construction-route typing
        result_xp = None
    return {"affector": affector, "patient": patient, "ptok": ptok, "from_comp": from_comp,
            "construction": construction, "result_xp": result_xp}


def _clause_context(vtok, ptok) -> List[str]:
    """AUTO version of the hand-extracted patient-mods: CONTENT cues only (patient ADJ modifiers + verb
    directional/aspectual particles + directional prep GROUND nouns + negation). Deliberately EXCLUDES
    determiners/case/punctuation -- those pollute the gate's attachment check and are not force-dynamic
    cues (a det failing attachment_ok wrongly ABSTAINed literal physical clauses)."""
    ctx: List[str] = []
    if ptok is not None:
        for c in ptok.children:
            if c.dep_ == "amod" and c.pos_ == "ADJ":
                ctx.append(c.text.lower())
            if c.dep_ == "neg" or c.lemma_.lower() in ("not", "never"):
                ctx.append(c.text.lower())
    for c in vtok.children:
        if c.dep_ in ("advmod", "prt", "neg") and c.pos_ in ("ADV", "ADP", "PART"):
            ctx.append(c.text.lower())
        if c.dep_ in ("prep", "obl", "npadvmod"):
            # directional particle words (down/up) count; also add the GROUND noun (down the SLOPE)
            if c.text.lower() in ("down", "up", "downhill", "uphill", "downstream", "upstream",
                                  "downward", "upward", "with", "against"):
                ctx.append(c.text.lower())
            for g in c.children:
                if g.dep_ in ("pobj", "obj"):
                    ctx.append(g.lemma_.lower())
    return ctx


def _read_endstate(sent, vtok, ptok, from_comp, lex, construction="lexical", result_xp=None) -> bool:
    """READ ENDSTATE per construction (Rappaport Hovav & Levin event structure): PREVENT-from succeeds
    (not reached); RESULTATIVE endstate = the RESULT adjective (reached unless negated); CAUSED-MOTION
    endstate = path reached (unless negated); else the glass-box negation detector on the OUTCOME
    (excluding the patient's own modifier span)."""
    vlem = vtok.lemma_.lower()
    cls = lex.get(vlem)
    neg_on_verb = any(c.dep_ == "neg" or c.lemma_.lower() in ("not", "never", "n't")
                      for c in vtok.children)
    if cls == "PREVENT" and from_comp is not None:
        return neg_on_verb          # succeeded prevention -> endstate not reached (False) unless negated
    if construction == "resultative" and result_xp is not None:
        # the RESULT XP is the endstate: reached unless negated (on the result phrase or the verb)
        neg_res = any(c.dep_ == "neg" or c.lemma_.lower() in ("not", "never", "n't")
                      for c in result_xp.children)
        return not (neg_res or neg_on_verb)
    if construction in ("caused_motion", "periphrastic"):
        return not neg_on_verb      # implicative / bounded-path: reached unless negated
    # Endstate polarity from the OUTCOME, EXCLUDING the PATIENT's own modifier span: a patient-size
    # negation ("the table was not very heavy") is a disposition cue, NOT an endstate negation --
    # scoping it to the endstate wrongly reads not-reached (a real negation-scope bug the given path
    # shares). Verb-attached negation/failure ("never came", "did not ignite") is kept.
    patient_span = set()
    if ptok is not None:
        try:
            patient_span = {t.i for t in ptok.subtree}
        except Exception:
            patient_span = set()
    outcome_toks = [t.text for t in sent if t.i not in patient_span]
    return detect_endstate_reached(outcome_toks)


def _type_with_construction(affector, vlem, patient, ctx, endstate, construction, lex, tendency=True) -> str:
    """Construction-aware force typing (Goldberg): the construction supplies CAUSE for a manner verb
    (resultative/caused-motion) or a periphrastic causer (make/have/get); else defer to verb/tendency."""
    if construction == "periphrastic" and vlem in _PERIPHRASTIC_CAUSE:
        return "CAUSE" if endstate else "NO_CAUSATION"
    base = (type_with_full_tendency(affector, vlem, patient, ctx, endstate, lex) if tendency
            else force_dynamic_type(lemmatize_verb(vlem), endstate, lex))
    # RESULTATIVE / CAUSED-MOTION: the construction supplies CAUSE when the (manner/agentive) verb does NOT
    # determine a force type -- but keep an informative ENABLE/PREVENT if the verb/tendency yields one
    # (e.g. gravity-aligned caused motion -> ENABLE). Goldberg: the construction carries the causal relation.
    if construction in ("resultative", "caused_motion") and base in ("SEQUENTIAL", "NO_CAUSATION") and endstate:
        return "CAUSE"
    return base


def _type_clause(affector, vlem, patient, ctx, endstate, lex, construction="lexical",
                 result_xp=None, tendency=True) -> str:
    """Type the clause. The CONSTRUCTION supplies CAUSE when the verb is a MANNER (non-force) verb
    (resultative/caused-motion) or a periphrastic causer (make/have/get) -- Goldberg: the construction
    carries the causal relation independent of the verb. Otherwise defer to the verb/tendency typer."""
    return _type_with_construction(affector, vlem, patient, ctx, endstate, construction, lex,
                                   tendency=tendency)


# ===========================================================================
# Lazy loaders (spaCy + the experiments literalness/WSD gate). Kept lazy so plain
# `import hdlab.causation_typing` never pulls spaCy or the experiment WSD chain.
# ===========================================================================
# In-substrate parse frontend (the SAME assets the reader already loads for the copular/state path).
# ---------------------------------------------------------------------------
_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
_POS_ASSET = os.path.join(_REPO, "data", "frontend_assets", "pos_tagger_ud_ewt_upos.json")
_ARC_ASSET = os.path.join(_REPO, "data", "frontend_assets", "arc_parser_hashed_ud_ewt.npz")
_LAB_ASSET = os.path.join(_REPO, "data", "frontend_assets", "arc_labeler_hashed_ud_ewt.json")
_FRONTEND: Dict[str, object] = {}


def _frontend():
    if "t" not in _FRONTEND:
        from hdlab.pos_tagger import PosTagger
        from hdlab.arc_parser import ArcParser
        from hdlab.arc_labeler import ArcLabeler
        from hdlab import frontend as _FE   # ONE shared frontend (2026-09-12): HDLAB_TAG_SOURCE / HDLAB_HEADS_SOURCE reach here
        _FRONTEND["t"] = _FE.tagger()
        _FRONTEND["p"] = _FE.parser()
        _FRONTEND["l"] = ArcLabeler.load(_LAB_ASSET)
    return _FRONTEND["t"], _FRONTEND["p"], _FRONTEND["l"]


# ---------------------------------------------------------------------------
# Lemmatization (spaCy .lemma_ replacement). Verbs via the substrate's lemma_verb; nouns via WordNet
# morphy (already a dependency of causation_typing); function words -> lowered surface.
# ---------------------------------------------------------------------------
def _lemma(word: str, upos: str) -> str:
    w = (word or "").lower()
    if upos in ("VERB", "AUX"):
        try:
            from hdlab.thematic_role_labeler import lemma_verb
            return lemma_verb(w).lower()
        except Exception:
            return w
    if upos in ("NOUN", "PROPN"):
        try:
            from nltk.corpus import wordnet as wn
            m = _gbm.morphy(w, "n")
            return m if m else w
        except Exception:
            return w
    return w


_IRREG_VBN = frozenset({
    "done", "gone", "seen", "taken", "given", "known", "shown", "broken", "chosen", "driven", "eaten",
    "written", "spoken", "stolen", "frozen", "hidden", "bitten", "beaten", "worn", "torn", "sworn",
    "drawn", "thrown", "grown", "blown", "flown", "held", "built", "sent", "spent", "lost", "found",
    "caught", "taught", "bought", "brought", "fought", "sought", "thought", "kept", "left", "felt",
    "meant", "dealt", "made", "said", "paid", "laid", "led", "put", "set", "cost", "hurt", "shut",
    "made", "become", "begun", "come", "run",
})


def _penn(word: str, upos: str) -> str:
    """Reconstruct the Penn fine tag the causation legs read off .tag_ (VBG/VBN/VBD/VBZ/VBP/VB, NNS/NN,
    JJ/RB/...). Morphological guess -- UPOS carries no fine tense/number, exactly the PAL .tag_ gap."""
    w = (word or "").lower()
    if upos in ("VERB", "AUX"):
        if w.endswith("ing"):
            return "VBG"
        if w in _IRREG_VBN or w.endswith("en"):
            return "VBN"
        if w.endswith("ed"):
            return "VBD"                       # simple past (canonical foreground tense) -- see _leg_aspect
        if w.endswith("s") and not w.endswith("ss"):
            return "VBZ"
        if upos == "AUX" and w in ("am", "is", "are", "was", "were", "be", "been", "being",
                                   "have", "has", "had", "do", "does", "did", "will", "would",
                                   "can", "could", "may", "might", "must", "shall", "should"):
            return "MD" if w in ("will", "would", "can", "could", "may", "might", "must",
                                 "shall", "should") else "VBP"
        return "VBP" if w not in ("be",) else "VB"
    if upos == "PROPN":
        return "NNP"
    if upos == "NOUN":
        return "NNS" if (w.endswith("s") and not w.endswith("ss") and len(w) > 3) else "NN"
    if upos == "ADJ":
        return "JJ"
    if upos == "ADV":
        return "RB"
    if upos == "PRON":
        return "PRP"
    if upos == "ADP":
        return "IN"
    if upos == "PART":
        return "RP"
    if upos == "DET":
        return "DT"
    return upos


# ---------------------------------------------------------------------------
# spaCy-token-compatible ADAPTER over the in-substrate UD parse.
# ---------------------------------------------------------------------------
try:
    from nltk.corpus import stopwords as _nltk_sw
    _STOP = set(_nltk_sw.words("english"))
except Exception:
    _STOP = {"the", "a", "an", "of", "to", "in", "on", "at", "for", "with", "by", "and", "or", "but",
             "is", "are", "was", "were", "be", "been", "being", "it", "this", "that", "he", "she",
             "they", "i", "we", "you", "him", "her", "them", "his", "its", "their", "as", "so", "not",
             "no", "do", "did", "does", "have", "has", "had", "will", "would", "can", "could"}


class _AdaptTok:
    __slots__ = ("i", "text", "lemma_", "pos_", "tag_", "dep_", "_children", "head")

    def __init__(self, i, text, lemma, pos, tag, dep):
        self.i = i
        self.text = text
        self.lemma_ = lemma
        self.pos_ = pos
        self.tag_ = tag
        self.dep_ = dep
        self._children: List["_AdaptTok"] = []
        self.head: Optional["_AdaptTok"] = None

    @property
    def children(self):
        return self._children

    @property
    def is_alpha(self):
        return self.text.isalpha()

    @property
    def is_stop(self):
        return self.text.lower() in _STOP

    @property
    def subtree(self):
        seen = {}
        stack = [self]
        while stack:
            x = stack.pop()
            if id(x) in seen:
                continue
            seen[id(x)] = x
            stack.extend(x._children)
        return sorted(seen.values(), key=lambda t: t.i)


class _AdaptSent(list):
    """A sentence = an ordered list of _AdaptTok (iterating it yields the tokens, like a spaCy Span)."""
    pass


# UD deprel (subtype-collapsed by arc_labeler.norm_label) -> the ClearNLP label the cue functions read.
_UD2DEP = {
    "root": "ROOT", "nsubj": "nsubj", "nsubj:pass": "nsubjpass", "csubj": "csubj",
    "obj": "dobj", "iobj": "dative", "obl": "obl", "obl:agent": "agent", "nmod": "nmod",
    "advcl": "advcl", "acl": "relcl", "appos": "appos", "ccomp": "ccomp", "xcomp": "xcomp",
    "amod": "amod", "advmod": "advmod", "det": "det", "mark": "mark", "aux": "aux", "cop": "cop",
    "cc": "cc", "conj": "conj", "nummod": "nummod", "punct": "punct", "expl": "expl",
    "compound": "compound", "case": "case", "vocative": "vocative", "discourse": "advmod",
    "parataxis": "parataxis", "fixed": "fixed", "flat": "flat", "dep": "dep",
}


def _build_adapt_sent(toks: Sequence[str], t, p, l) -> _AdaptSent:
    """Parse one already-tokenized sentence with the in-substrate frontend and present a spaCy-style Span.

    Topology translations:
      * UD `case` preposition (child of its nominal) -> re-parented to a spaCy prep->pobj chain under the
        nominal's head (verb/noun). This is the one structural inversion spaCy vs UD.
      * `acl` covers relative clauses (UD collapses acl:relcl -> acl); mapped to `relcl` (both are the
        causation module's _BACKGROUND_DEPS anyway).
      * an object-predicate NOMINAL (UD xcomp with NOUN/PROPN UPOS, "call X a pig") -> `attr` so the
        naming-frame veto can see it; an object-predicate ADJ stays reachable via xcomp.
    """
    toks = list(toks)
    upos = list(t.tag(toks))
    heads = dict(p.parse(toks, upos).heads)          # 1-based dep -> head (0 = ROOT)
    deprels = dict(l.label(toks, upos, heads))       # 1-based dep -> UD deprel
    n = len(toks)
    atoks = []
    for k in range(1, n + 1):
        w = toks[k - 1]
        up = upos[k - 1]
        dep = _UD2DEP.get(deprels.get(k, "dep"), "dep")
        # object-predicate nominal -> naming-frame-visible attr
        if deprels.get(k) == "xcomp" and up in ("NOUN", "PROPN"):
            dep = "attr"
        atoks.append(_AdaptTok(k - 1, w, _lemma(w, up), up, _penn(w, up), dep))
    # wire heads (spaCy head links), skipping the prepositions we will re-parent below
    ud_head = {k: heads.get(k, 0) for k in range(1, n + 1)}
    is_case = {k for k in range(1, n + 1) if deprels.get(k) == "case"}
    for k in range(1, n + 1):
        if k in is_case:
            continue
        h = ud_head[k]
        if h != 0:
            atoks[k - 1].head = atoks[h - 1]
            atoks[h - 1]._children.append(atoks[k - 1])
    # re-parent each UD `case` preposition into a spaCy prep -> pobj chain:
    #   verb/noun G  ->  prep(into)  ->  pobj(river)
    for c in sorted(is_case):
        noun = ud_head[c]                             # the nominal the preposition marks
        if not (1 <= noun <= n):
            continue
        g = ud_head[noun]                             # the nominal's head (verb / noun)
        prep_tok = atoks[c - 1]
        noun_tok = atoks[noun - 1]
        prep_tok.dep_ = "prep"
        # detach the nominal from its UD head; attach it under the preposition as pobj
        if noun_tok.head is not None and noun_tok in noun_tok.head._children:
            noun_tok.head._children.remove(noun_tok)
        noun_tok.dep_ = "pobj"
        noun_tok.head = prep_tok
        prep_tok._children.append(noun_tok)
        # attach the preposition under the nominal's head (or ROOT)
        if 1 <= g <= n:
            prep_tok.head = atoks[g - 1]
            atoks[g - 1]._children.append(prep_tok)
        else:
            prep_tok.head = None
    return _AdaptSent(atoks)


class _AdaptFrontend:
    """Non-None sentinel handed to LiteralnessGate as `nlp` so it does not self-load spaCy (assess() reads
    the passed adapter tokens, never this object)."""
    pass


def _gate_or_load(nlp, use_gate):
    if not use_gate:
        return None
    from experiments._literalness_gate import LiteralnessGate   # lazily imported; NOT promoted here
    return LiteralnessGate(nlp=nlp)


# ===========================================================================
# THE PUBLIC ENTRY POINT -- reproduces WiredCausationReader._read_causation_typed EXACTLY on the same
# input (default args), plus an optional graded-foreground veto (default-off).
# ===========================================================================
def read_typed_causation(reader, conll_path, sm, *, gate_mode="force", use_gate=True,
                         role_source="parse", tendency=True, use_constructions=True,
                         sense_gate=True, sense_tau=1.0, foreground_gate=False,
                         graded_foreground=False, theta=None, nlp=None,
                         lexicon=None) -> List[TypedCausalLink]:
    """Type every within-clause causative in the document at `conll_path` and return the TypedCausalLinks.

    Faithful port of WiredCausationReader._read_causation_typed: with default args (foreground_gate=False,
    graded_foreground=False) it returns byte-identical links to the experiment reader on the same input.

    Args:
      reader  -- an already-built SituationReader (used only to reuse an nlp handle if `nlp` is None, and
                 to receive the per-clause `typed_debug` trace).
      conll_path -- the doc; parsed via hdlab.scene_segment.parse_conll_sentences (same as the reader).
      sm      -- the built SituationModel (role_source="reader" indexes sm.events for role fillers).
      gate_mode ("force"|"physical_only"), use_gate, role_source ("parse"|"reader"), tendency,
      use_constructions, sense_gate, sense_tau, foreground_gate -- as on WiredCausationReader.
      graded_foreground/theta -- optional graded event-hood veto (ported from _foreground_eventhood.py;
                 DEFAULT-OFF, so it never perturbs the faithful default path). theta defaults to
                 THETA_DEFAULT (a placeholder; set from the sweep when the graded gate is enabled).
      nlp, lexicon -- optional pre-built spaCy pipeline / force lexicon (loaded lazily if None).
    """
    from hdlab.scene_segment import parse_conll_sentences
    sents = parse_conll_sentences(conll_path)
    t, p, l = _frontend()
    gate = _gate_or_load(_AdaptFrontend(), use_gate)   # non-None -> gate never self-loads spaCy
    lex = lexicon if lexicon is not None else build_force_lexicon()
    links: List[TypedCausalLink] = []
    typed_debug: List[dict] = []
    # reader-native roles (ablation): index stock EventRecords by (sent_idx, predicate lemma)
    reader_roles = {}
    if sm is not None and role_source == "reader":
        for ev in sm.events:
            reader_roles.setdefault((ev.sent_idx, ev.predicate), (ev.agent, ev.patient))
    for si, toks in enumerate(sents):
        for sent in (_build_adapt_sent(toks, t, p, l),):
            for vtok in sent:
                # DETECT: verb tokens, OR a force-lexicon lemma the parser GARDEN-PATHED into a NOUN
                # that still heads a direct object ("A firewall blocks hackers ..." -> blocks tagged NOUN).
                is_verb = vtok.pos_ == "VERB"
                misparsed_verb = (vtok.pos_ in ("NOUN", "PROPN")
                                  and lex.get(vtok.lemma_.lower()) is not None
                                  and any(c.dep_ in ("dobj", "obj") for c in vtok.children))
                if not (is_verb or misparsed_verb):
                    continue
                cand = _causative_candidate(sent, vtok, lex, use_constructions)
                if cand is None:
                    continue
                affector, patient, ptok = cand["affector"], cand["patient"], cand["ptok"]
                from_comp, construction, result_xp = cand["from_comp"], cand["construction"], cand["result_xp"]
                vlem = vtok.lemma_.lower()
                # reader-native role override (ablation)
                if role_source == "reader":
                    ra = reader_roles.get((si, vlem))
                    if ra is not None:
                        affector = ra[0] if ra[0] not in (None, "?", "") else affector
                        patient = ra[1] if ra[1] not in (None, "?", "") else patient
                ctx = _clause_context(vtok, ptok)
                endstate = _read_endstate(sent, vtok, ptok, from_comp, lex, construction, result_xp)
                label = "ENGAGE_PHYSICAL"
                if use_gate:
                    r = gate.assess(sent, vtok, affector, patient, ctx)
                    label = r["label"]
                    allowed = ("ENGAGE_PHYSICAL", "FORCE_NONPHYSICAL") if gate_mode == "force" \
                        else ("ENGAGE_PHYSICAL",)
                    # FORCE-EVENT DISCRIMINATION: engage force typing only if the 3-leg argument VOTE clears
                    # theta. Only the FROM-construction and the PERIPHRASTIC complement are syntactically
                    # disambiguated -> they bypass; everything else still needs the argument VOTE.
                    gate_applies = (sense_gate and from_comp is None
                                    and construction != "periphrastic")
                    force_veto = (gate_applies
                                  and force_engagement_score(affector, vlem, patient) < sense_tau)
                    # FOREGROUNDED-EVENT gate (boolean p2): a backgrounded (participial/relative/appositive)
                    # clause or a naming frame is not a main causal event -> encode NO link.
                    bg_veto = foreground_gate and (not is_foregrounded_event(vtok)
                                                   or is_naming_frame(vtok))
                    # GRADED foreground gate (p3, ported): veto when the graded event-hood score on the
                    # clean DEFAULT_LEGS is below theta, or a naming frame, or a categorical stative head
                    # (bypassed by periphrastic / from-construction, as the sense gate is). DEFAULT-OFF.
                    graded_veto = False
                    if graded_foreground:
                        th = THETA_DEFAULT if theta is None else theta
                        graded_veto = (
                            eventhood_score(vtok, affector, patient, ptok, vlem, DEFAULT_LEGS) < th
                            or is_naming_frame(vtok)
                            or (vlem in _STATIVE_RELATIONAL and construction != "periphrastic"
                                and from_comp is None))
                    if label not in allowed or force_veto or bg_veto or graded_veto:
                        why = ("BACKGROUND" if bg_veto and label in allowed
                               else "BACKGROUND_GRADED" if (graded_veto and label in allowed
                                                            and not force_veto)
                               else "FORCE_EVENT" if (force_veto and label in allowed) else label)
                        links.append(TypedCausalLink(si, affector, vlem, patient, "ABSTAIN",
                                                     endstate, why, source=construction))
                        typed_debug.append({"sent_idx": si, "verb": vlem, "aff": affector,
                                            "pat": patient, "ctype": "ABSTAIN", "label": why,
                                            "endstate": endstate, "ctx": ctx, "cons": construction})
                        continue
                ctype = _type_clause(affector, vlem, patient, ctx, endstate, lex, construction,
                                     result_xp, tendency)
                links.append(TypedCausalLink(si, affector, vlem, patient, ctype, endstate, label,
                                             source=construction))
                typed_debug.append({"sent_idx": si, "verb": vlem, "aff": affector, "pat": patient,
                                    "ctype": ctype, "label": label, "endstate": endstate,
                                    "ctx": ctx, "from": from_comp, "cons": construction})
    if reader is not None:
        reader.typed_debug = typed_debug     # mirror WiredCausationReader.typed_debug for auditing
    return links


__all__ = [
    "TypedCausalLink", "read_typed_causation", "TYPES",
    "force_engagement_score", "is_foregrounded_event", "is_naming_frame",
    "eventhood_legs", "eventhood_score", "DEFAULT_LEGS", "THETA_DEFAULT",
]
