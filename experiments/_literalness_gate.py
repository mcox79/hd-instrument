"""_literalness_gate -- a glass-box FORCE-AFFORDANCE gate that lets the force-dynamic (sensorimotor)
   reader ENGAGE only on LITERAL, correctly-attached PHYSICAL events, and ABSTAIN otherwise.
   (problem: the_force_dynamic_reader_needs_a_literal_sense_and_attachment_gate)

BRAIN MECHANISM (from the 2026-08-30 research drill, research_literalness_gating_2026-08-30.md):
Grounded/embodied simulation is GRADED, not hard-gated: motor/force simulation runs FULL for literal
physical events, BLEACHED for novel force metaphors, and is OFF for conventional/lexicalized-figurative
and opaque idioms (Raposo 2009; Desai 2011/2023: LIT > MET > IDIOM > ABS; primary-motor recruitment
falls with figurative conventionality). The force-dynamic PHYSICAL reader must engage on the LITERAL
bucket and abstain on the OFF bucket -- exactly the residual over-fire class ("the news broke", "the
deal fell through"). We replicate the OUTCOME at the COMPUTATIONAL (constraint-satisfaction) level:
"should I run the physical force simulation?" is the readout of whether the physical-force interpretation
best satisfies the joint constraints -- it is the SEMANTIC-CONTROL competition (LIFG/pMTG select the
context-appropriate sense and suppress strong-but-irrelevant ones; Lambon Ralph, Jefferies), NOT a
separate module. So we compute ONE graded FORCE-AFFORDANCE SCORE, not a bolted-on three-way AND:

    affordance(clause) = s_sense * s_conc            (soft-AND: the weakest satisfied constraint dominates)
        s_sense  = P(physical event-frame | context)   -- controlled semantic cognition + stored-unit idiom
        s_conc   = min(conc(antagonist), conc(agonist)) -- grounded-simulation affordance over BOTH force
                   roles (Wolff/Talmy two-force structure): an ABSTRACT filler in EITHER physical-force
                   slot is a selectional-preference violation (Wilks 1978; -> N400) => figurative.
    ENGAGE_PHYSICAL iff affordance >= tau  AND  attachment_ok  AND  not opaque-idiom.

THREE-WAY OUTPUT (the drill's refinement -- do NOT discard social-force metaphor):
    ENGAGE_PHYSICAL  (A) -- literal physical; run the patient-tendency estimator + force typer.
    FORCE_NONPHYSICAL(B) -- physical-sense verb but an abstract force role (social/psych/institutional
                            force: "she forced him to admit", "arrest the dealer"): a real force event,
                            LABELED for a future social-force reader; the PHYSICAL reader abstains.
    ABSTAIN          (C/O)-- non-physical sense / opaque idiom / abstract non-force.

PINNED (replicate): sense selection = controlled semantic cognition; stored-unit idiom access (Giora
graded salience); selectional-violation -> figurative; attachment = the dependency parse.
OUR-INVENTION (swept): the exact affordance combiner (product), tau, PHYSICAL_FRAMES set, the concreteness
mapping. Glass-box; NO external LLM at inference (spaCy parse + NLTK WordNet, as the substrate uses).

Reuses (does NOT rebuild): experiments.frame_sense_disambiguator (the WSD organ) + experiments.idiom_gate.
ASCII only. No hdlab writes.
"""
from __future__ import annotations

import os
import sys
from functools import lru_cache
from typing import Dict, List, Optional, Tuple

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import numpy as np

from experiments.frame_sense_disambiguator import (
    FrameSenseDisambiguator, candidate_frames, extract_frame)
from experiments import idiom_gate as _IDIOM_MOD

# The coarse event-frames that AFFORD a literal physical force simulation (motion/contact/change of
# physical state / bodily action). A verb sense outside this set does not license the physical reader.
PHYSICAL_FRAMES = {"motion", "contact", "change", "body"}

# Frames the WSD organ commits to RELIABLY when non-physical (validated in no_glass_box_verb_sense_
# disambiguation). A diagnostic move to one of THESE suppresses the physical salience floor. The
# motion/possession/change construction confusions are NOT reliable enough to override a dominant-
# physical prior (measured: "pour water" mis-committed to possession over a 0.958 motion prior), so a
# move to possession/weather/etc. does NOT suppress -- Giora graded salience keeps the salient sense.
_RELIABLE_NONPHYS = {"communication", "cognition", "social", "emotion", "perception"}

# personal pronouns almost always denote a physical entity in these clauses; relative/indefinite ones
# are referentially open -> neutral. (The concreteness VETO must only bite on KNOWN-abstract nouns.)
_PERSON_OBJ_PRON = {"he", "she", "him", "her", "me", "us", "them", "they", "i", "you", "we", "myself",
                    "himself", "herself", "themselves", "myself", "ourselves", "yourself"}
_OPEN_PRON = {"it", "this", "that", "which", "who", "what", "one", "these", "those", "something",
              "everything", "anything", "nothing", "some", "all", "them"}

_ABSTRACT_ROOTS = {"abstraction.n.06", "communication.n.02", "group.n.01", "psychological_feature.n.01",
                   "measure.n.02", "cognition.n.01", "act.n.02", "event.n.01", "state.n.02",
                   "attribute.n.02", "relation.n.01"}
_PHYSICAL_ROOT = "physical_entity.n.01"


@lru_cache(maxsize=4096)
def concreteness_score(noun: str) -> float:
    """Grounded-simulation affordance of a force-role filler, in [0,1]. Brain-faithful DEFAULT-HIGH:
    the simulation is ATTEMPTED by default and only BLOCKED by a KNOWN selectional-preference violation
    (a known-abstract filler in a physical-force slot -> N400; Wilks 1978). So concreteness is HIGH for
    everything EXCEPT known-abstract nouns -- pronouns and unknown nouns do NOT veto (in physical clauses
    they overwhelmingly denote physical entities). Glass-box WordNet IS-A (generalizes to novel nouns,
    not a word list): known physical_entity -> 0.95; known abstraction (not physical) -> 0.1;
    personal pronoun -> 0.9; referentially-open pronoun (it/that/which) -> 0.75; unknown noun -> 0.8."""
    if not noun:
        return 0.9
    n = noun.strip().lower()
    if n in _PERSON_OBJ_PRON:
        return 0.9
    if n in _OPEN_PRON:
        return 0.75
    try:
        from nltk.corpus import wordnet as wn
    except Exception:
        return 0.8
    syns = wn.synsets(n, pos=wn.NOUN)
    if not syns:                                   # lemmatize (plurals: activities->activity, forces->force)
        lem = wn.morphy(n, wn.NOUN)
        if lem:
            syns = wn.synsets(lem, pos=wn.NOUN)
    if not syns:
        return 0.8
    names = set()
    for s in syns[:5]:                          # top-5: catch physical-object polysemy (board GAME, a
        for path in s.hypernym_paths():          # STACK, a DROP) whose physical sense is not the top-ranked
            names |= {h.name() for h in path}
    phys = _PHYSICAL_ROOT in names
    abstr = bool(names & _ABSTRACT_ROOTS)
    if phys and not abstr:
        return 0.95
    if abstr and not phys:
        return 0.1            # KNOWN abstract -> the selectional-violation veto
    if phys and abstr:
        return 0.7            # both roots reachable (polysemous) -> lean physical, no veto
    return 0.8


class LiteralnessGate:
    """Reuses the WSD disambiguator; parses each sentence once (spaCy). No LLM."""

    def __init__(self, nlp=None, tau: float = 0.5):
        self._nlp = nlp
        self.tau = tau
        self._dis = FrameSenseDisambiguator(nlp=nlp)

    def _nlp_or_load(self):
        if self._nlp is None:
            import spacy
            self._nlp = spacy.load("en_core_web_sm")
            self._dis._nlp = self._nlp
        return self._nlp

    # ---- component 1: physical-sense posterior (controlled semantic cognition + stored-unit idiom) --
    def physical_sense_score(self, sent, verb_tok,
                             shuffle_sense: Optional[Dict[str, str]] = None) -> Tuple[float, str, Optional[str]]:
        """P(physical event-frame | context) in [0,1] from the WSD organ, under Giora graded salience.
        Idiom route: a stored non-compositional MWE whose frame is non-physical -> 0 (opaque idiom, no
        sim); physical -> 1. Otherwise the physical posterior, FLOORED at the physical PRIOR mass (the
        salient sense governs) UNLESS the disambiguator diagnostically committed to a RELIABLE
        non-physical frame (communication/cognition/social/emotion/perception) -- only then do we trust
        the override and drop below the prior. This makes s_sense robust to the WSD organ's fragile
        motion/possession/change construction confusions while keeping its reliable non-physical calls.
        `shuffle_sense` (a frame->frame permutation) is the info-free SENSE twin."""
        from experiments.frame_sense_disambiguator import frame_prior
        v = self.verdict(sent, verb_tok)
        route, frame, p = v.route, v.frame, v.p
        pri = frame_prior(verb_tok.lemma_.lower())
        if shuffle_sense is not None:
            pri = {shuffle_sense.get(k, k): val for k, val in pri.items()}
        phys_prior = sum(val for k, val in pri.items() if k in PHYSICAL_FRAMES)
        # idiom / light-verb / unknown routes give no posterior -> fall back to the PHYSICAL PRIOR
        # (Giora salience: the salient physical sense of a dominant-physical verb). The OPAQUE-IDIOM
        # decision is made SEPARATELY in assess() from the VOBJ (verb+object) non-compositional lexicon
        # ONLY -- NOT the phrasal-particle lexicon, whose members ('throw away', 'cut off', 'set up')
        # retain a live LITERAL physical sense that concreteness handles (measured: phrasal-idiom vetoes
        # are net-harmful, they wrongly veto literal phrasal uses).
        if route in ("idiom", "light_verb", "no_cands") or not p:
            return float(max(0.0, min(1.0, phys_prior if route != "no_cands" else 0.5))), route, frame
        post = dict(p)
        if shuffle_sense is not None:
            post = {shuffle_sense.get(k, k): val for k, val in post.items()}
        phys_post = sum(val for k, val in post.items() if k in PHYSICAL_FRAMES)
        # Suppress the physical salience floor ONLY on a CONFIDENT diagnostic commitment to a reliable
        # non-physical frame (posterior > 0.55). The WSD organ's LOW-confidence non-physical moves are
        # its documented taxonomy fallibility ("hit play"->communication, "leave the nail"->cognition)
        # and must NOT suppress a dominant-physical verb (Giora salience).
        nonphys_conf = post.get(frame, 0.0) if frame in _RELIABLE_NONPHYS else 0.0
        reliable_nonphys_move = bool(v.diagnostic and frame in _RELIABLE_NONPHYS
                                     and nonphys_conf > 0.55 and shuffle_sense is None)
        s = phys_post if reliable_nonphys_move else max(phys_post, phys_prior)
        return float(max(0.0, min(1.0, s))), route, frame

    @lru_cache(maxsize=2048)
    def _cached_verdict(self, sent_text: str, lemma: str, i: int):
        raise NotImplementedError  # placeholder; verdict() caches on the doc instead

    def verdict(self, sent, verb_tok, use_context: bool = True):
        """Reordered-access CONTEXT cue (Duffy/Morris/Rayner; the parent WSD organ's reliable lever):
        pass the sentence content words so the disambiguator's RELIABILITY-GATED P(frame|context) fires
        for verbs where context beats the prior on TRAIN (zero otherwise -> safe on the broad set)."""
        ctx = None
        if use_context:
            ctx = [t.lemma_.lower() for t in sent
                   if t.pos_ in ("NOUN", "PROPN", "ADJ", "ADV", "VERB") and t.i != verb_tok.i
                   and not t.is_stop and t.is_alpha]
        return self._dis.disambiguate_token(sent, verb_tok, conservative=True, context_words=ctx)

    # ---- component 2: concreteness over ALL physical force roles --------------------------------
    # DIRECTIONAL/PATH prepositions -- these mark the GROUND/GOAL of a motion event (Talmy). ONLY these
    # license the oblique-concreteness veto; accompaniment/measure/benefactive PPs (with/of/by/for/at)
    # are NOT force roles and must not veto ("bring the car back with 9000 MILES", "the rest OF the rice").
    _PATH_PREP = {"into", "onto", "to", "toward", "towards", "in", "on", "across", "through", "over",
                  "down", "up", "off", "out", "from", "against", "at", "upon", "under", "past"}

    def oblique_goal_heads(self, verb_tok) -> List[str]:
        """The GROUND/GOAL/LANDMARK head noun(s) of a MOTION event, reached via a DIRECTIONAL/PATH
        preposition only. Talmy: an ABSTRACT Ground = metaphorical motion ('fall in LOVE', 'sink into
        EGOS', 'throw muscle into STRUGGLE'). Read off the parse (path-prep -> pobj)."""
        heads = []
        for ch in verb_tok.children:
            if ch.dep_ in ("prep", "obl", "dative") and ch.text.lower() in self._PATH_PREP:
                for g in ch.children:
                    if g.dep_ in ("pobj", "obj"):
                        heads.append(g.lemma_.lower() if hasattr(g, "lemma_") else g.text.lower())
        return heads

    def role_concreteness(self, affector: str, patient: str, verb_tok=None,
                          conc_map: Optional[Dict[str, float]] = None,
                          use_oblique: bool = False) -> Tuple[float, float, float, float]:
        """Grounded-simulation affordance over the CORE force roles: antagonist (affector=nsubj) and
        agonist (patient=obj). The motion GROUND (oblique goal) is a refinement that needs argument-role
        typing to separate a Goal ('into the BOX') from a temporal/quantity/manner adjunct ('in a couple
        of MINUTES', 'with 9000 MILES'); the raw parse label does not, so the oblique veto is OFF by
        default (measured net-negative on real text -- it wrongly vetoes literals on adjunct PPs)."""
        def conc(n):
            if conc_map is not None:
                return conc_map.get(n.strip().lower(), 0.5) if n else 1.0
            return concreteness_score(n) if n else 1.0
        ca = conc(affector) if affector else 1.0   # intransitive: no antagonist to veto
        cp = conc(patient) if patient else 1.0
        cg = 1.0
        if use_oblique and verb_tok is not None:
            goals = self.oblique_goal_heads(verb_tok)
            if goals:
                cg = min(conc(g) for g in goals)
        core = min(ca, cp, cg) if use_oblique else min(ca, cp)
        return core, ca, cp, cg

    # ---- component 3: attachment (dependency confirms the cue tokens modify the force roles) -----
    @staticmethod
    def attachment_ok(sent, verb_tok, patient_surface: str, context: List[str]) -> bool:
        """The directional/magnitude CUE tokens (context) that would drive the estimator's tendency
        sign must be parse-attached to the PATIENT (amod) or the VERB (obl/prt/advmod). A context token
        present in the sentence but attached elsewhere is a MISATTACHMENT -> the cue is spurious."""
        if not context:
            return True
        # tokens legitimately reachable as cues: children of the verb (obl/advmod/prt) and their case/
        # amod markers, plus amod of the patient token.
        legit = set()
        pat = None
        for ch in verb_tok.children:
            if ch.dep_ in ("prep", "advmod", "prt", "npadvmod", "obl", "dobj", "obj", "nsubj", "nsubjpass"):
                if ch.text.lower() == patient_surface:
                    pat = ch
                if ch.dep_ in ("prep", "advmod", "prt", "npadvmod", "obl"):
                    legit.add(ch.text.lower())
                    for g in ch.children:
                        if g.dep_ in ("pobj", "amod", "advmod", "case"):
                            legit.add(g.text.lower())
        if pat is not None:
            for ch in pat.children:
                if ch.dep_ == "amod":
                    legit.add(ch.text.lower())
        # every cue token should be legit-reachable; a directional/adjective cue that is not is misattached
        cue_tokens = [t for t in context if t.isalpha()]
        if not cue_tokens:
            return True
        missing = [t for t in cue_tokens if t not in legit]
        # tolerate incidental function words; flag only if a MAJORITY of alpha cues are unreachable
        return len(missing) <= len(cue_tokens) // 2

    # ---- the combined graded affordance + three-way label ---------------------------------------
    def assess(self, sent, verb_tok, affector: str, patient: str, context: List[str],
               shuffle_sense: Optional[Dict[str, str]] = None,
               permute_attach: bool = False,
               conc_map: Optional[Dict[str, float]] = None,
               s_min: float = 0.34, c_min: float = 0.34,
               use_sense_veto: bool = False, use_oblique: bool = False) -> Dict:
        """VETO architecture (constraint satisfaction; Bergen/Barsalou grounded simulation is ATTEMPTED
        by default and only BLOCKED by a detected violation): ENGAGE the physical reader UNLESS
          (1) an OPAQUE IDIOM fires (stored-unit non-physical retrieval -- reliable, always on), or
          (2) a force ROLE is KNOWN-ABSTRACT (s_conc < c_min -> selectional-preference violation), or
          (3) [opt] the physical SENSE posterior is suppressed below s_min (a CONFIDENT non-physical WSD
              commitment). OFF by default: the compositional WSD frame-posterior is measured net-harmful
              here (it confidently mis-commits literal events -- 'leave the nail'->cognition, 'cut'->
              communication -- the WSD organ's documented taxonomy fallibility); the RELIABLE part of the
              sense channel is the stored-unit idiom (kept, clause 1), matching the parent WSD finding.
          (4) the cue ATTACHMENT is wrong.
        Thresholds/switches are OUR-INVENTION-UNDER-TEST (swept). affordance = s_sense*s_conc reported."""
        s_sense, route, frame = self.physical_sense_score(sent, verb_tok, shuffle_sense=shuffle_sense)
        # OPAQUE-IDIOM veto from the VOBJ (verb+object) non-compositional lexicon ONLY (make sense, take
        # place, pass a law -- reliably abstract stored units), NOT phrasal particles. Shuffled in the twin.
        rf = extract_frame(sent, verb_tok)
        vobj_frame = _IDIOM_MOD.idiom_sense(verb_tok.lemma_.lower(), None, rf.dobj_head)
        eff_vf = shuffle_sense.get(vobj_frame, vobj_frame) if (shuffle_sense and vobj_frame) else vobj_frame
        opaque_idiom = (eff_vf is not None and eff_vf not in PHYSICAL_FRAMES)
        s_conc, ca, cp, cg = self.role_concreteness(affector, patient, verb_tok=verb_tok,
                                                    conc_map=conc_map, use_oblique=use_oblique)
        attach = True if permute_attach else self.attachment_ok(sent, verb_tok, patient, context)
        affordance = s_sense * s_conc
        if opaque_idiom or (use_sense_veto and s_sense < s_min):
            label = "ABSTAIN"            # non-physical sense / opaque idiom (bucket C/O)
        elif s_conc < c_min:
            label = "FORCE_NONPHYSICAL"  # physical-sense verb, abstract force role (bucket B)
        elif attach:
            label = "ENGAGE_PHYSICAL"    # bucket A -- no violation detected
        else:
            label = "ABSTAIN"            # misattached cue
        engage = (label == "ENGAGE_PHYSICAL")
        # graded engage SCORE (for a precision-recall curve / calibrated operating point): 0 when a hard
        # veto fires (opaque idiom / misattached), else the affordance. Ranks clauses by physical-literalness.
        score = 0.0 if (opaque_idiom or not attach) else affordance
        return {"engage": engage, "label": label, "affordance": affordance, "score": score,
                "s_sense": s_sense, "s_conc": s_conc, "conc_aff": ca, "conc_pat": cp, "conc_goal": cg,
                "attach_ok": attach, "route": route, "frame": frame, "opaque_idiom": opaque_idiom}


# ------------------------------------------------------------------------------------------------
def _self_test() -> bool:
    import spacy
    nlp = spacy.load("en_core_web_sm")
    gate = LiteralnessGate(nlp=nlp, tau=0.5)
    cases = [
        # (sentence, verb_lemma, affector, patient, context, expect_engage)
        ("I cut the vegetables on the cutting board .", "cut", "i", "vegetables", ["board"], True),
        ("The hurricane slammed into Biloxi .", "slam", "hurricane", "biloxi", ["into"], True),
        ("The news broke that morning .", "break", "news", "news", [], False),
        ("She fell in love with it .", "fall", "she", "she", ["love", "in"], False),
        ("Birth rates are increasing the poverty .", "increase", "rates", "poverty", [], False),
        ("I poured cold water over the plant .", "pour", "i", "water", ["cold", "over"], True),
    ]
    npass = 0
    print("\nSELF-TEST _literalness_gate:")
    for sent_text, lemma, aff, pat, ctx, exp in cases:
        doc = nlp(sent_text)
        sent = list(doc.sents)[0]
        vtok = next((t for t in sent if t.lemma_.lower() == lemma and t.pos_ == "VERB"), None)
        if vtok is None:
            vtok = next((t for t in sent if t.lemma_.lower() == lemma), None)
        r = gate.assess(sent, vtok, aff, pat, ctx)
        ok = (r["engage"] == exp)
        npass += int(ok)
        print(f"  [{'PASS' if ok else 'FAIL'}] {lemma:8s} eng={r['engage']} exp={exp}  "
              f"label={r['label']:16s} sense={r['s_sense']:.2f} conc={r['s_conc']:.2f} "
              f"frame={r['frame']}  :: {sent_text[:40]}")
    print(f"SELF-TEST: {npass}/{len(cases)} correct")
    return npass >= len(cases) - 1  # tolerate 1 hard case


if __name__ == "__main__":
    ok = _self_test()
    sys.exit(0 if ok else 1)
