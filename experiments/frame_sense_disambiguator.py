"""frame_sense_disambiguator -- a glass-box verb-sense / event-FRAME disambiguator over the dependency parse.

BRAIN MECHANISM (PINNED -- copy the computation; see BRAIN_MECHANISM_SPEC.md):
Verb-sense selection = reordered lexical access (a frequency PRIOR; Duffy/Morris/Rayner 1988) + the realized
argument-structure CONSTRUCTION (a near-CATEGORICAL constraint; Goldberg construction grammar, Levin 1993
diathesis) + graded THEMATIC FIT of the argument's semantic type (McRae/Ferretti; Bicknell 2010), COMBINED as a
graded cue competition whose additive-activation->softmax IS the FLMP/Bayesian posterior (McClelland 2013;
MacDonald/Pearlmutter/Seidenberg 1994). When the frame cue is diagnostic it overrides the prior; when the frame
is neutral the reader STAYS at the prior = most-frequent-sense = UNDERSPECIFICATION (Frazier & Rayner 1990).

We COPY that operation and SWEEP the feature/weight/granularity. We do NOT use a fixed verb->sense lookup or a
manner-verb whitelist (the ToM solver proved the whitelist is the implementation trap). No LLM at inference.

The disambiguating signal is IN the realized syntax + the argument's semantic TYPE, read off the dependency
parse -- NOT the verb string. Two dominant confusions (brief bar): motion-vs-transitive-deposit and
perception-vs-speech; the mechanism is GENERAL (construction/selectional rules applied to any verb), scored over
the verb's candidate coarse frames (its distinct WordNet verb lexnames).

Currency: hdlab.graded_competition (net_activation -> softmax; entropy = the gold-free underspecification gate).
Noun typing reuses experiments.location_register.is_place_ground (WordNet, witnessed) to avoid drift. spaCy
en_core_web_sm parse; NLTK WordNet for sense inventory + frequency prior + per-sense noun typing.

BRAIN-FOUNDATIONAL REFINEMENTS from the 2026-08-28 research drill
(research_brain_foundational_verb_sense_2026-08-28.md), with honest PINNED/INVENTED labels:
  * JOINT verb-sense x argument-noun-sense scoring (INVENTED-UNDER-TEST, lit-consistent P~0.45): the argument
    noun's sense is co-selected with the verb frame at the governor-dependent edge, NOT typed first (Altmann &
    Kamide 1999; McRae/Ferretti/Amyote 1997; Trueswell/Tanenhaus/Garnsey 1994 -- constraint is local+immediate).
    We take max over the dobj's noun senses inside the construction cue (bounded cross-product; ablated below).
  * HOMONYMY vs POLYSEMY gate (PINNED grain): polysemy clusters stay underspecified at MFS until a cue
    discriminates (Pickering & Frisson 2001; Klepousniotou 2002/2012 -- shared cluster, priming); homonym splits
    get fast obligatory commitment (same papers, opposite finding). Gated by the verb's own WordNet sense
    connectivity, computed once per lemma.
  * The additive-cues -> softmax combination is STRUCTURALLY ISOMORPHIC to, but NOT proven equal to, a Bayesian
    posterior (McClelland 2013 requires calibrated log-likelihood weights + conditional independence; our
    construction and thematic-fit cues are NOT independent -- both derive from the event schema). We therefore use
    TWO genuine cues (frequency prior + a single construction/thematic-fit cue) and do not claim a proven posterior.

ASCII only. No hdlab writes.
"""
from __future__ import annotations

import os
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import numpy as np
from hdlab.graded_competition import net_activation, graded_pick
from experiments.location_register import is_place_ground  # WordNet place typing (witnessed, reused)

# Optional brain-foundational assets (composed if present; the disambiguator works without them):
#  * idiom_gate    -- the STORED-UNIT lexicon: non-compositional MWEs are retrieved holistically (Jackendoff's
#                     construction lexicon; Cutting & Bock 1997 direct access) BEFORE literal composition.
#  * sense_selprefs-- a SENSE-keyed selectional-preference table -> a thematic-fit cue INDEPENDENT of the
#                     construction cue (so the additive->softmax combination approaches a true Bayesian posterior).
try:
    from experiments import idiom_gate as _IDIOM
except Exception:
    _IDIOM = None
try:
    from experiments import sense_selprefs as _SELPREF
except Exception:
    _SELPREF = None
try:
    from experiments import context_prior as _CTXPRIOR   # reliability-gated CONTEXT cue (reordered access)
except Exception:
    _CTXPRIOR = None

# ---------------------------------------------------------------------------
# Coarse event-FRAME inventory = the WordNet verb lexnames (Ciaramita & Altun supersenses), the coarse partition
# the brain represents and downstream consumes. The two dominant confusions live inside it:
#   motion  vs  possession   ("left the room" vs "left a note")
#   perception vs communication ("observed the swap" vs "observed that ...")
# ---------------------------------------------------------------------------
COARSE_FRAMES = ["motion", "possession", "communication", "perception", "cognition",
                 "change", "contact", "stative", "creation", "body", "emotion",
                 "consumption", "social", "competition", "weather"]

# The two dominant confusions the brief names (+ their event-neighbours). The construction cue is VERB-SENSITIVE
# (research 2026-08-28): it fires ONLY for the alternation a verb actually participates in -- a physobj object is
# a 'deposit' signal for a motion/possession verb but a plain transitive object for a perception verb; a
# that-clause is diagnostic for a perception/speech verb but not for a change/social verb. Applying the cue to
# every verb is the indiscriminate signal that HURTS broad WSD (measured on SemCor: -0.03).
PROPOSITIONAL = {"communication", "cognition"}          # a that-clause / reply / idea complement
DEPOSIT_FRAMES = {"possession", "contact", "change", "creation"}
NONPROP = {"motion", "perception", "possession", "contact", "change", "social", "competition", "stative"}


def verb_confusions(cands: Sequence[str]) -> set:
    """Which targeted confusion FAMILY(ies) this verb participates in, from its candidate coarse frames:
      'prop'  -- a propositional/non-propositional alternation (observe: perception<->communication; return:
                 motion<->communication; see: perception<->cognition). Cue: a clausal/propositional complement.
      'md'    -- a motion/deposit alternation (leave: motion<->possession). Cue: object type + caused-motion."""
    cs = set(cands)
    out = set()
    if (cs & PROPOSITIONAL) and (cs & NONPROP):
        out.add("prop")
    if "motion" in cs and (cs & DEPOSIT_FRAMES):
        out.add("md")
    return out


def lexname_to_frame(lexname: Optional[str]) -> Optional[str]:
    """WordNet verb lexname ('verb.motion') -> coarse frame ('motion'). None if not a verb lexname."""
    if not lexname or not lexname.startswith("verb."):
        return None
    return lexname.split(".", 1)[1]


# ---------------------------------------------------------------------------
# Noun semantic typing (glass-box WordNet). Types the brain's ATL hub supplies for selectional/thematic fit.
# ---------------------------------------------------------------------------
_TIME_NOUNS = {"time", "hour", "minute", "moment", "day", "year", "week", "month", "night", "morning",
               "evening", "afternoon", "instant", "while", "second", "decade", "century", "season",
               "spring", "summer", "autumn", "winter", "period", "age"}
# WordNet noun lexname -> coarse selectional type. The brain's ATL hub supplies the argument's semantic type;
# we read it from the noun's senses and, faithful to reordered access, FREQUENCY-WEIGHT them (the dominant sense
# drives thematic fit) rather than unioning every minor sense (which pollutes typing).
_LEX2TYPE = {
    "noun.location": "place",
    "noun.artifact": "physobj", "noun.object": "physobj", "noun.food": "physobj",
    "noun.substance": "physobj", "noun.body": "physobj", "noun.plant": "physobj",
    # split the abstract objects by their OWN semantic field: a message/reply is COMMUNICATED, an idea/point/
    # reason is COGNIZED -- this is what distinguishes 'return a reply' (communication) from 'see the point'
    # (cognition), a distinction the brain reads off the object and a coarse 'proposition' type erases.
    "noun.communication": "comm_obj", "noun.cognition": "cog_obj",
    "noun.state": "proposition", "noun.attribute": "proposition",
    "noun.event": "perceivable", "noun.act": "perceivable",
    "noun.phenomenon": "perceivable", "noun.process": "perceivable",
    "noun.time": "time",
    "noun.person": "animate", "noun.animal": "animate", "noun.group": "animate",
}
_NTYPE_CACHE: Dict[str, Dict[str, float]] = {}
_PLACE_HYPERNYMS = {"location", "region", "tract", "geographical_area", "structure", "way", "room",
                    "building", "land", "body_of_water"}


def _sense_noun_type(syn) -> Optional[str]:
    """Coarse type for ONE noun synset: a sense is a PLACE iff its own hypernyms are locations (this decides
    room=place vs key=object PER SENSE, resolving the argument-noun polysemy that a flat lemma tag cannot)."""
    names = set()
    for path in syn.hypernym_paths():
        for h in path:
            names.add(h.name().split(".")[0])
    if names & _PLACE_HYPERNYMS:
        return "place"
    return _LEX2TYPE.get(syn.lexname())


def noun_frame_types(word: Optional[str]) -> Dict[str, float]:
    """Frequency-WEIGHTED coarse selectional tags for a noun head:
    {place, physobj, proposition, animate, time, perceivable} -> weight in [0,1] (dominant-sense-driven).
    Typed PER SENSE (hypernym-location check) so a noun's minor senses do not pollute its dominant type."""
    if not word:
        return {}
    w = word.lower()
    if w in _NTYPE_CACHE:
        return _NTYPE_CACHE[w]
    weights: Dict[str, float] = defaultdict(float)
    try:
        from nltk.corpus import wordnet as wn
        syns = wn.synsets(w, pos="n")[:6]
    except Exception:
        syns = []
    freqs = []
    for rank, s in enumerate(syns):
        c = sum(lm.count() for lm in s.lemmas() if lm.name().lower() == w)
        freqs.append(c + 1.0 / (rank + 1.0))          # rank-decayed floor (WordNet order = frequency proxy)
    tot = sum(freqs) if freqs else 0.0
    for s, f in zip(syns, freqs):
        t = _sense_noun_type(s)
        if t is not None and tot > 0:
            weights[t] += f / tot
    if w in _TIME_NOUNS:
        weights["time"] = max(weights.get("time", 0.0), 0.7)
    out = dict(weights)
    _NTYPE_CACHE[w] = out
    return out


_NSENSE_CACHE: Dict[str, List[Tuple[str, float]]] = {}


def noun_sense_list(word: Optional[str]) -> List[Tuple[str, float]]:
    """The noun's senses as (coarse_type, normalized_prior) pairs -- for JOINT (verb,noun)-sense scoring, where
    the verb frame co-selects the fitting noun sense (max over these) instead of consuming a pre-typed scalar."""
    if not word:
        return []
    w = word.lower()
    if w in _NSENSE_CACHE:
        return _NSENSE_CACHE[w]
    try:
        from nltk.corpus import wordnet as wn
        syns = wn.synsets(w, pos="n")[:6]
    except Exception:
        syns = []
    rows = []
    freqs = []
    for rank, s in enumerate(syns):
        t = _sense_noun_type(s)
        c = sum(lm.count() for lm in s.lemmas() if lm.name().lower() == w)
        freqs.append(c + 1.0 / (rank + 1.0))
        rows.append([t, 0.0])
    tot = sum(freqs) if freqs else 0.0
    out = []
    for (t, _), f in zip(rows, freqs):
        if t is not None and tot > 0:
            out.append((t, f / tot))
    if w in _TIME_NOUNS:
        out.append(("time", 0.7))
    _NSENSE_CACHE[w] = out
    return out


# ---------------------------------------------------------------------------
# The realized argument FRAME, read off a spaCy-parsed sentence around the target verb token.
# ---------------------------------------------------------------------------
_PARTICLE_AWAY = {"away"}
_MOTION_PARTICLES = {"out", "off", "back", "up", "down", "in", "over", "along", "across", "forward"}
_GOAL_SOURCE_PREPS = {"to", "into", "onto", "toward", "towards", "from", "for", "at", "in", "on", "through",
                      "across", "past", "up", "down", "out", "off", "along", "over", "under", "behind"}


_DEVERBAL_CACHE: Dict[str, bool] = {}


def _is_deverbal(noun: str) -> bool:
    """True if the noun has a corresponding VERB form (a deverbal/event noun): walk, laugh, glance, look, ...
    Used only for the light-verb construction (take/give/have/make + deverbal -> defer to the noun's event)."""
    if not noun:
        return False
    w = noun.lower()
    if w in _DEVERBAL_CACHE:
        return _DEVERBAL_CACHE[w]
    try:
        from nltk.corpus import wordnet as wn
        # a deverbal noun: the same string is also a common verb AND its dominant noun sense is an act/event
        has_verb = len(wn.synsets(w, pos="v")) > 0
        nsyns = wn.synsets(w, pos="n")[:2]
        event_noun = any(s.lexname() in ("noun.act", "noun.event", "noun.process") for s in nsyns)
        ans = bool(has_verb and event_noun)
    except Exception:
        ans = False
    _DEVERBAL_CACHE[w] = ans
    return ans


_HOMONYM_CACHE: Dict[str, bool] = {}


def is_homonym_split(lemma: str) -> bool:
    """PINNED grain gate (Pickering & Frisson 2001; Klepousniotou 2002): does the verb's WordNet sense-set split
    into UNRELATED meaning clusters (homonymy -> fast obligatory commitment) vs a related polysemy cluster
    (-> underspecified, stays at MFS until a cue discriminates)? Approximated by coarse-frame spread + absence of
    a shared dominant supersense. Computed ONCE per lemma (needs no sentence context)."""
    if lemma in _HOMONYM_CACHE:
        return _HOMONYM_CACHE[lemma]
    try:
        from nltk.corpus import wordnet as wn
        syns = wn.synsets(lemma, pos="v")
    except Exception:
        syns = []
    frames = defaultdict(float)
    for rank, s in enumerate(syns):
        fr = lexname_to_frame(s.lexname())
        if fr is None:
            continue
        c = sum(lm.count() for lm in s.lemmas() if lm.name().lower() == lemma.lower())
        frames[fr] += c + 1.0 / (rank + 1.0)
    if len(frames) < 2:
        ans = False
    else:
        tot = sum(frames.values())
        shares = sorted((v / tot for v in frames.values()), reverse=True)
        # homonym signature: >=2 coarse frames each carrying substantial mass (no single shared dominant cluster)
        ans = bool(shares[0] < 0.75 and shares[1] >= 0.20 and len(frames) >= 2)
    _HOMONYM_CACHE[lemma] = ans
    return ans


# Per-noun-SENSE-type -> coarse-frame support (the thematic-fit / selectional table). Enables JOINT scoring:
# the verb frame co-selects the argument noun sense whose type best fits it (max over the dobj's senses).
_TYPE_FRAME_SUPPORT = {
    "place": {"motion": 1.0, "possession": -0.6, "communication": -0.6},
    "physobj": {"possession": 0.9, "contact": 0.4, "creation": 0.2, "motion": -0.7, "communication": -0.5},
    "comm_obj": {"communication": 0.9, "cognition": 0.3, "motion": -0.7},    # reply/message/word -> speech
    "cog_obj": {"cognition": 0.9, "communication": 0.3, "motion": -0.7},     # point/idea/reason -> cognition
    "proposition": {"communication": 0.6, "cognition": 0.6, "motion": -0.7},  # generic state/attribute
    "perceivable": {"perception": 0.7, "communication": -0.3},
    "animate": {"social": 0.4, "contact": 0.2},
    "time": {},
}
_PROP_TYPES = ("comm_obj", "cog_obj", "proposition")


@dataclass
class RealizedFrame:
    lemma: str
    has_dobj: bool = False
    dobj_head: Optional[str] = None
    dobj_types: dict = field(default_factory=dict)
    has_ccomp: bool = False           # FINITE that-clause complement (epistemic proposition)
    has_percept_smallclause: bool = False  # naked-infinitive / participial small clause ('saw him LEAVE') = direct perception
    has_quote: bool = False
    has_xcomp_vb: bool = False        # 'started to run' -- infinitival
    particle: Optional[str] = None    # phrasal-verb prt
    prep: Optional[str] = None        # first PP preposition under the verb
    pobj_head: Optional[str] = None
    pobj_types: dict = field(default_factory=dict)
    is_intransitive: bool = False
    subj_types: dict = field(default_factory=dict)
    has_iobj: bool = False            # dative recipient
    recipient_animate: bool = False
    has_result_adj: bool = False      # resultative secondary predicate ('painted the fence RED')
    dobj_deverbal: Optional[str] = None   # light-verb complement lemma ('took a WALK')


def extract_frame(sent, verb_tok) -> RealizedFrame:
    """Glass-box frame extraction from a spaCy sentence + its target verb Token."""
    rf = RealizedFrame(lemma=verb_tok.lemma_.lower())
    for ch in verb_tok.children:
        d = ch.dep_
        if d in ("dobj", "obj"):
            rf.has_dobj = True
            rf.dobj_head = ch.lemma_.lower()
            # a PRONOUN / anaphoric object's semantic type depends on its REFERENT -- unknown without coreference
            # (the research coref seam). Do NOT type it: leave dobj_types empty so the cue defers to MFS rather
            # than guessing 'physobj' from 'it/him/them' (a measured error source on real prose).
            rf.dobj_types = {} if ch.pos_ == "PRON" else noun_frame_types(ch.lemma_)
            if _is_deverbal(ch.lemma_):
                rf.dobj_deverbal = ch.lemma_.lower()
            # resultative secondary predicate on the object: 'painted the fence RED', 'wiped it CLEAN'
            for gc in ch.children:
                if gc.pos_ == "ADJ" and gc.dep_ in ("oprd", "acomp") and gc.i > ch.i:
                    rf.has_result_adj = True
        elif ch.pos_ == "ADJ" and d in ("oprd", "advcl", "acomp") and ch.i > verb_tok.i:
            rf.has_result_adj = True     # verb-level secondary-predicate ADJ ('wiped it CLEAN', 'hammered flat')
        elif d in ("ccomp",):
            # FINITE that-clause (epistemic) is marked by 'that/whether/if' or a quote -> has_ccomp. A bare
            # complement VERB with its OWN subject and NO complementizer is a naked-infinitive/participial SMALL
            # CLAUSE ('saw him LEAVE', 'saw him LEAVING') = DIRECT PERCEPTION (Barwise & Perry 1983) -> percept.
            has_that = any(gc.dep_ == "mark" and gc.lemma_.lower() in ("that", "whether", "if") for gc in ch.children)
            has_q = any(gc.text in ('"', "``", "''", "'") for gc in ch.subtree)
            has_subj = any(gc.dep_ in ("nsubj", "nsubjpass") for gc in ch.children)
            if has_that or has_q:
                rf.has_ccomp = True
            elif ch.pos_ in ("VERB", "AUX") and has_subj:
                rf.has_percept_smallclause = True
        elif d in ("acomp",):
            pass
        elif d in ("xcomp",):
            if ch.pos_ in ("VERB", "AUX"):
                rf.has_xcomp_vb = True
        elif d in ("prt",):
            rf.particle = ch.lemma_.lower()
        elif d in ("dative", "iobj"):
            rf.has_iobj = True
            if noun_frame_types(ch.lemma_).get("animate", 0.0) > 0.3:
                rf.recipient_animate = True
        elif d in ("prep",):
            if rf.prep is None:
                rf.prep = ch.lemma_.lower()
                for gc in ch.children:
                    if gc.dep_ in ("pobj", "pcomp"):
                        rf.pobj_head = gc.lemma_.lower()
                        rf.pobj_types = noun_frame_types(gc.lemma_)
                        if gc.dep_ == "pobj" and (noun_frame_types(gc.lemma_).get("animate", 0.0) > 0.3):
                            rf.recipient_animate = True
        elif d in ("nsubj", "nsubjpass"):
            rf.subj_types = noun_frame_types(ch.lemma_)
    # a direct quotation immediately governed by the verb is a speech complement
    if not rf.has_ccomp:
        for ch in verb_tok.children:
            if ch.dep_ in ("ccomp", "parataxis") and any(gc.text in ('"', "``", "''") for gc in ch.subtree):
                rf.has_quote = True
    rf.is_intransitive = (not rf.has_dobj) and (not rf.has_ccomp) and (not rf.has_percept_smallclause)
    return rf


# ---------------------------------------------------------------------------
# The CONSTRUCTION cue: near-categorical support per coarse frame from the realized frame. GENERAL rules
# (apply to any verb) -- constructions carry event semantics (Goldberg). Positive = licenses; negative = blocks.
# ---------------------------------------------------------------------------
def frame_support(rf: RealizedFrame, confusions: Optional[set] = None) -> Dict[str, float]:
    """FRAME-LEVEL construction support (coarse-frame -> score), independent of the dobj noun SENSE (that is
    co-selected in the joint scorer via _TYPE_FRAME_SUPPORT). VERB-SENSITIVE: rules fire only for the confusion
    the verb participates in (`confusions`, from verb_confusions(cands)); None = fire all (legacy/self-test)."""
    C = confusions if confusions is not None else {"md", "prop"}
    sup: Dict[str, float] = defaultdict(float)
    # (a) clausal-complement / quote -> a PROPOSITION is said or thought. It licenses communication AND cognition
    # EQUALLY (a that-clause does not say WHICH); the PRIOR breaks that tie. It rules OUT motion/perception/deposit.
    if (rf.has_ccomp or rf.has_quote) and "prop" in C:
        sup["communication"] += 0.9
        sup["cognition"] += 0.9
        sup["perception"] -= 0.7
        sup["motion"] -= 1.0
        sup["possession"] -= 0.6
    # (a2) naked-infinitive / participial SMALL CLAUSE ('saw him leave') = DIRECT PERCEPTION (Barwise & Perry) --
    # the discriminator that separates see-PERCEIVE from see-COGNIZE ('see that S'). Perception, not proposition.
    if rf.has_percept_smallclause and "prop" in C:
        sup["perception"] += 1.0
        sup["cognition"] -= 0.6
        sup["communication"] -= 0.6
    md = "md" in C
    # (c) phrasal particle
    if md and rf.particle in _PARTICLE_AWAY:               # 'passed away' -> die (change of state)
        sup["change"] += 0.9
        sup["stative"] -= 0.3
    elif md and rf.particle in _MOTION_PARTICLES:          # 'went out', 'came back' -> motion
        sup["motion"] += 0.8
    # (d) intransitive + subject type. A TIME subject -> elapse. A BARE intransitive with no other cue is
    # genuinely ambiguous ('leave'=depart|remain, 'go'=travel|become) -> the reader STAYS at the prior/MFS
    # (Frazier & Rayner underspecification); do NOT default it to motion (measured: that OUR-INVENTION flipped
    # MFS-correct stative/social/change intransitives to motion and was the dominant break vs MFS).
    if md and rf.is_intransitive and rf.subj_types.get("time", 0.0) > 0.3:
        sup["change"] += 0.7
        sup["stative"] += 0.5
        sup["motion"] -= 0.8
    # (e) Goal/Source/Path PP with NO direct object -> self-motion (unless a recipient of transfer/speech)
    if md and rf.prep in _GOAL_SOURCE_PREPS and not rf.has_dobj and not rf.has_ccomp:
        if rf.prep in ("to", "toward", "towards") and rf.recipient_animate:
            sup["communication"] += 0.4
            sup["possession"] += 0.3
        else:
            sup["motion"] += 0.7
    # (f) DOUBLE-OBJECT dative -> caused-POSSESSION (Rappaport Hovav & Levin 2008; Pinker 1989).
    if md and rf.has_iobj and rf.has_dobj:
        sup["possession"] += 0.8
        if rf.recipient_animate:
            sup["communication"] += 0.2
    elif md and rf.has_iobj:
        sup["possession"] += 0.4
    # (g) CAUSED-MOTION construction (Goldberg): dobj + a resultative LOCATIVE PP -> the OBJECT is placed at a
    # location => deposit/transfer, NOT the agent moving. 'left the keys ON THE TABLE', 'put it IN the box'.
    if md and rf.has_dobj and rf.prep in ("on", "in", "into", "onto", "at", "under", "over", "beside", "near"):
        if rf.pobj_types.get("place", 0.0) > 0 or rf.pobj_types.get("physobj", 0.0) > 0:
            sup["possession"] += 0.8
            sup["motion"] -= 0.6
    # (h) RESULTATIVE construction (Goldberg & Jackendoff 2004): dobj + secondary-predicate ADJECTIVE ->
    # caused-CHANGE-OF-STATE ('painted the fence red', 'wiped it clean'). Distinct from caused-motion (PP).
    if md and rf.has_dobj and rf.has_result_adj:
        sup["change"] += 0.8
        sup["motion"] -= 0.4
        sup["possession"] -= 0.2
    return dict(sup)


def strong_construction(rf: RealizedFrame, confusions: set) -> bool:
    """Is a STRONG, near-categorical construction present -- FOR A CONFUSION THIS VERB HAS -- that licenses a
    commitment OFF the frequency prior? Brain-faithful: commitment is TRIGGERED by structural bias, not the
    default (Fishbein & Harris 2014); else the reader stays underspecified at MFS (Frazier & Rayner 1990)."""
    if not confusions:
        return False
    ps = "prop" in confusions
    md = "md" in confusions
    if ps and (rf.has_ccomp or rf.has_quote or rf.has_percept_smallclause):   # propositional / perceptual complement
        return True
    if md and rf.has_result_adj:
        return True
    if md and rf.has_iobj and rf.has_dobj:                           # double-object dative
        return True
    if md and (rf.particle in _PARTICLE_AWAY or rf.particle in _MOTION_PARTICLES):
        return True
    if md and rf.is_intransitive and rf.subj_types.get("time", 0.0) > 0.3:   # elapse
        return True
    if md and rf.prep in _GOAL_SOURCE_PREPS and not rf.has_dobj and not rf.has_ccomp:   # Goal/Path PP, no object
        return True
    if md and rf.has_dobj and rf.prep in ("on", "in", "into", "onto", "at", "under", "over", "beside", "near") \
            and (rf.pobj_types.get("place", 0.0) > 0 or rf.pobj_types.get("physobj", 0.0) > 0):
        return True                                                  # caused-motion PP
    if rf.has_dobj:
        dt = rf.dobj_types                                           # the motion/deposit or perception pivot
        if md and (dt.get("place", 0.0) >= 0.5 or dt.get("physobj", 0.0) >= 0.6):
            return True
        if ps and (dt.get("comm_obj", 0.0) + dt.get("cog_obj", 0.0) + dt.get("proposition", 0.0) >= 0.5
                   or dt.get("perceivable", 0.0) >= 0.5):
            return True
    return False


# ---------------------------------------------------------------------------
# Frequency PRIOR over coarse frames for a verb lemma, from WordNet SemCor sense counts (reordered access).
# ---------------------------------------------------------------------------
_PRIOR_CACHE: Dict[str, Dict[str, float]] = {}


def frame_prior(lemma: str) -> Dict[str, float]:
    """coarse-frame -> prior weight (normalized SemCor sense frequency aggregated by lexname)."""
    if lemma in _PRIOR_CACHE:
        return _PRIOR_CACHE[lemma]
    try:
        from nltk.corpus import wordnet as wn
        syns = wn.synsets(lemma, pos="v")
    except Exception:
        syns = []
    counts: Dict[str, float] = defaultdict(float)
    for rank, s in enumerate(syns):
        fr = lexname_to_frame(s.lexname())
        if fr is None:
            continue
        c = 0
        for lm in s.lemmas():
            if lm.name().lower() == lemma.lower():
                c += lm.count()
        # WordNet order is a frequency proxy; add a small rank-decayed floor so unattested senses still exist
        counts[fr] += c + 1.0 / (rank + 1.0)
    tot = sum(counts.values())
    out = {fr: (v / tot if tot else 0.0) for fr, v in counts.items()}
    _PRIOR_CACHE[lemma] = out
    return out


def candidate_frames(lemma: str) -> List[str]:
    """The verb's distinct coarse frames (its WordNet verb lexnames). Ordered by prior desc (MFS first)."""
    pr = frame_prior(lemma)
    return sorted(pr.keys(), key=lambda f: -pr[f])


# ---------------------------------------------------------------------------
# The disambiguator: combine prior + frame construction cue + thematic fit via graded_competition.
# ---------------------------------------------------------------------------
# TWO genuine cues (frequency prior + construction/thematic-fit); no redundant third cue (honesty: the fit
# signal is NOT independent of the construction cue). W_NPRIOR = relative weight of the co-selected noun-sense
# prior inside the joint construction cue (nudges sense selection; type-fit dominates).
DEFAULT_WEIGHTS = {"prior": 1.0, "construction": 1.6}
W_NPRIOR = 0.5
_LIGHT_VERBS = {"take", "give", "have", "make", "do"}


@dataclass
class SenseVerdict:
    frame: Optional[str]                 # predicted coarse frame
    mfs: Optional[str]                   # most-frequent-sense (prior argmax)
    entropy: float                       # underspecification (1 = fully ambiguous)
    diagnostic: bool                     # frame cue moved the answer off MFS OR sharpened a near-tie
    homonym: bool = False                # verb is a homonym split (fast commitment) vs polysemy cluster
    route: str = "joint"                 # 'joint' | 'light_verb' | 'no_cands'
    p: Dict[str, float] = field(default_factory=dict)
    activations: Dict = field(default_factory=dict)   # per-cue support arrays + cands (for weight calibration)


class FrameSenseDisambiguator:
    def __init__(self, nlp=None, weights: Optional[Dict[str, float]] = None, gain: float = 2.0,
                 use_idioms: bool = True, use_indep_fit: bool = True, context_weight: float = 3.0):
        self._nlp = nlp
        self.weights = dict(weights or DEFAULT_WEIGHTS)
        self.gain = gain
        self.use_idioms = use_idioms and _IDIOM is not None
        self.use_indep_fit = use_indep_fit and _SELPREF is not None
        self.context_weight = context_weight   # reordered-access context cue weight (swept ~3; caller supplies scores)

    def _nlp_or_load(self):
        if self._nlp is None:
            import spacy
            self._nlp = spacy.load("en_core_web_sm")
        return self._nlp

    def disambiguate_token(self, sent, verb_tok, cand: Optional[List[str]] = None,
                           frame_feats: Optional[RealizedFrame] = None,
                           shuffle_frame: Optional[np.ndarray] = None,
                           joint: bool = True,
                           prior: Optional[Dict[str, float]] = None,
                           conservative: bool = True,
                           context_scores: Optional[Dict[str, float]] = None,
                           context_words: Optional[Sequence[str]] = None) -> SenseVerdict:
        """Disambiguate one verb token. `cand` overrides the candidate frame list (e.g. the gold's cand pool).
        `shuffle_frame` (a permutation of candidate indices) is the info-free construction twin.
        `joint`=True co-selects the dobj noun sense with the verb frame (research #1); False = the ablation that
        types the noun first (frequency-weighted union) then scores the verb.
        `prior` overrides the frequency-prior cue (e.g. a train-split MFS prior, so the MFS floor and this arm
        share the IDENTICAL prior and the construction cue is the only variable)."""
        lemma = verb_tok.lemma_.lower()
        rf = frame_feats if frame_feats is not None else extract_frame(sent, verb_tok)
        homo = is_homonym_split(lemma)
        # CONTEXT cue (reordered access): if raw context words are supplied, derive the RELIABILITY-GATED context
        # scores from the context_prior asset (zero for context-unreliable verbs -> safe on the broad population).
        if context_scores is None and context_words is not None and _CTXPRIOR is not None and cand is None:
            context_scores = _CTXPRIOR.gated_context_scores(lemma, candidate_frames(lemma), context_words)
        # STORED-UNIT (idiom) route -- holistic retrieval precedes literal composition (Cutting & Bock 1997;
        # Jackendoff's construction lexicon). A non-compositional MWE ('pass away', 'pass a law', 'make sense',
        # 'go off') is retrieved as a UNIT and its stored frame overrides the compositional construction reading.
        if self.use_idioms and shuffle_frame is None:
            fr = _IDIOM.idiom_sense(lemma, rf.particle, rf.dobj_head)
            if fr is not None and (cand is None or fr in cand):
                return SenseVerdict(frame=fr, mfs=(candidate_frames(lemma)[:1] or [None])[0],
                                    entropy=0.15, diagnostic=True, homonym=homo, route="idiom")
        # LIGHT-VERB construction: take/give/have/make/do + a deverbal event-noun -> the event reading is the
        # NOUN's (research rule 1). 'took a walk' -> walk's frame (motion); do not score the light verb's sense.
        if joint and lemma in _LIGHT_VERBS and rf.dobj_deverbal and cand is None:
            nf = candidate_frames(rf.dobj_deverbal)
            if nf:
                return SenseVerdict(frame=nf[0], mfs=(candidate_frames(lemma)[:1] or [None])[0],
                                    entropy=0.3, diagnostic=True, homonym=homo, route="light_verb")
        cands = cand if cand is not None else candidate_frames(lemma)
        if not cands:
            return SenseVerdict(frame=None, mfs=None, entropy=1.0, diagnostic=False,
                                homonym=homo, route="no_cands")
        pri = prior if prior is not None else frame_prior(lemma)
        prior_arr = np.array([pri.get(c, 0.0) for c in cands], dtype=float)
        confusions = verb_confusions(cands)                       # VERB-SENSITIVE: fire only the verb's alternation
        fsup = frame_support(rf, confusions)                      # frame-level (non-dobj-sense) construction
        constr_arr = np.array([fsup.get(c, 0.0) for c in cands], dtype=float)
        # dobj noun-SENSE selectional contribution -- only for the types relevant to the verb's confusion.
        relevant = set()
        if "md" in confusions:
            relevant |= {"place", "physobj"}
        if "prop" in confusions:
            relevant |= {"comm_obj", "cog_obj", "proposition", "perceivable"}
        if rf.has_dobj and relevant:
            if joint:
                # JOINT: for each verb frame, co-select the dobj noun sense that best fits it (max over senses).
                nsenses = [(t, pn) for (t, pn) in noun_sense_list(rf.dobj_head) if t in relevant]
                if nsenses:
                    for i, c in enumerate(cands):
                        constr_arr[i] += max(_TYPE_FRAME_SUPPORT.get(t, {}).get(c, 0.0) + W_NPRIOR * pn
                                             for (t, pn) in nsenses)
            else:
                # ABLATION: type the noun ONCE (frequency-weighted union), then score the verb.
                dt = {t: w for t, w in noun_frame_types(rf.dobj_head).items() if t in relevant}
                for i, c in enumerate(cands):
                    constr_arr[i] += sum(w * _TYPE_FRAME_SUPPORT.get(t, {}).get(c, 0.0) for t, w in dt.items())
        if shuffle_frame is not None:
            constr_arr = constr_arr[shuffle_frame]
        supports = {"prior": prior_arr, "construction": constr_arr}
        weights = dict(self.weights)
        # CONTEXT cue -- reordered access: the prior discourse primes the sense (Duffy/Morris/Rayner). A learned
        # P(frame | context) supplied by the caller (leakage-controlled), z-scored across candidates. This is the
        # brain's dominant disambiguation lever; measured to beat MFS on the motion confusion where the local
        # construction cue could not. First-class cue at the ACTIVATION level (not softmax-of-softmax).
        if context_scores is not None:
            ctx_arr = np.array([context_scores.get(c, 0.0) for c in cands], dtype=float)
            if np.abs(ctx_arr).sum() > 1e-9 and shuffle_frame is None:
                supports["context"] = ctx_arr
                weights.setdefault("context", self.context_weight)
        # INDEPENDENT thematic-fit cue (sense-keyed selectional preference: how typical is this object for each
        # candidate frame). Data-driven, NOT derived from the construction rules -> a genuinely separate cue.
        if self.use_indep_fit and rf.has_dobj and rf.dobj_head and shuffle_frame is None:
            fit_arr = np.array([_SELPREF.fit(lemma, c, rf.dobj_head) for c in cands], dtype=float)
            if np.abs(fit_arr).sum() > 1e-9:
                supports["fit"] = fit_arr
                # SECONDARY tie-breaker weight: the construction is the PINNED categorical cue (weight 1.6); the
                # data-driven fit is a graded second opinion that must not OVERRIDE a clean construction read.
                weights.setdefault("fit", 0.4)
        gp = graded_pick(supports, weights, gain=self.gain)
        win = gp["win"]
        pred = cands[win]
        mfs_idx = int(np.argmax(prior_arr)) if prior_arr.any() else 0
        mfs = cands[mfs_idx]
        p = {c: float(gp["p"][i]) for i, c in enumerate(cands)}
        moved = (win != mfs_idx)
        # CONSERVATIVE / underspecification default: only ACCEPT a move OFF the MFS prior when a STRONG targeted
        # construction is present (commitment is triggered by structural bias; else stay at MFS). This is the
        # brain-faithful gate that prevents a weak, indiscriminate LOCAL cue from hurting the broad population.
        # BUT the CONTEXT cue (reordered access) is a legitimate mover -- a strong discourse vote for the winning
        # frame justifies the commitment even without a local construction (measured: reverting context moves was
        # suppressing real wins). So the gate yields to either a strong construction OR a decisive context vote.
        strong = strong_construction(rf, confusions)   # same gate for real + twin (twin only shuffles the map)
        ctx_moves = bool("context" in supports and int(np.argmax(np.asarray(supports["context"]))) == win
                         and np.max(np.asarray(supports["context"])) > 0)
        if conservative and moved and not strong and not ctx_moves:
            pred, win, moved = mfs, mfs_idx, False
        diagnostic = bool(moved and strong)
        acts = {"cands": list(cands)}
        for cue in ("prior", "construction", "fit", "context"):
            if cue in supports:
                acts[cue] = [float(x) for x in np.asarray(supports[cue])]
        return SenseVerdict(frame=pred, mfs=mfs, entropy=float(gp["entropy"]),
                            diagnostic=diagnostic, homonym=homo, route="joint", p=p, activations=acts)

    def disambiguate(self, text: str, target_lemma: Optional[str] = None,
                     joint: bool = True) -> List[Tuple[str, SenseVerdict]]:
        """Parse `text`, disambiguate every (or the target) verb ROOT-ish token. Returns [(surface, verdict)]."""
        nlp = self._nlp_or_load()
        out = []
        doc = nlp(text)
        for sent in doc.sents:
            for tok in sent:
                if tok.pos_ != "VERB":
                    continue
                if target_lemma and tok.lemma_.lower() != target_lemma.lower():
                    continue
                ctx = [t.lemma_.lower() for t in sent
                       if t.pos_ in ("NOUN", "PROPN", "ADJ", "ADV", "VERB") and t.i != tok.i
                       and not t.is_stop and t.is_alpha]
                out.append((tok.text, self.disambiguate_token(sent, tok, joint=joint, context_words=ctx)))
        return out


# ---------------------------------------------------------------------------
# self-test: the two dominant confusions on context-flipped minimal pairs (the positive control shape).
# ---------------------------------------------------------------------------
def _self_test():
    import spacy
    nlp = spacy.load("en_core_web_sm")
    dis = FrameSenseDisambiguator(nlp)
    cases = [
        # the two dominant confusions (context-flipped minimal pairs = the positive control shape)
        ("She left the room quietly.", "leave", "motion"),
        ("She left the keys on the table.", "leave", "possession"),
        ("He observed the swap carefully.", "observe", "perception"),
        ("He observed that it was late.", "observe", "communication"),
        ("He returned home before dark.", "return", "motion"),
        ("He returned a sharp reply.", "return", "communication"),
        # the three research construction rules
        ("She took a long walk.", "take", "motion"),               # light-verb -> defer to 'walk'
        ("He gave Mary the book.", "give", "possession"),          # double-object dative -> caused-possession
        ("He wiped the table clean.", "wipe", "change"),           # resultative-AP -> change-of-state
    ]
    npass = 0
    for text, lemma, want in cases:
        res = dis.disambiguate(text, target_lemma=lemma)
        v = res[0][1] if res else None
        got = v.frame if v else None
        ok = (got == want)
        npass += int(ok)
        if v:
            print(f"  [{'PASS' if ok else 'FAIL'}] {text!r:36s} {lemma}: got={got} want={want} "
                  f"(H={v.entropy:.2f} diag={v.diagnostic} homo={v.homonym} route={v.route})")
        else:
            print(f"  [FAIL] {text!r} no verb")
    print(f"\nSELF-TEST frame_sense_disambiguator: {npass}/{len(cases)} cases correct")
    return npass >= len(cases) - 1


if __name__ == "__main__":
    _self_test()
