"""hdlab/force_dynamics_valence.py -- harm/help patient-valence from FORCE DYNAMICS x grounded outcome valence.

Since 2026-09-12 (owner-DONE pri-7) the decision is the force-dynamic ARITHMETIC (see the block below): force STRUCTURE
(Talmy 1988; Wolff 2007: CAUSE / ENABLE / PREVENT from hdlab.force_dynamics_lexicon) x the patient's ENDSTATE VALENCE
(Warriner norms via hdlab.affect_lexicon) x a graded AFFECTEDNESS gate (Beavers 2011; McRae-Tanenhaus thematic fit);
inanimate patient = NA; non-affecting event = abstain. The earlier verb-LIST membership test (FrameNet harm frames
enumerated on the read path + a hand backoff) is GONE -- a list is not a mechanism and FrameNet-at-inference was an
external tool on the read path. The structural gate (`force_dynamics_event_type`) is unchanged except that it now
prefers the READER'S bound predicate (item["gov_idx"], STEP 3d) over the positional nearest-verb search.
Since 2026-09-12 (strategy, pri-14) the endstate valence is read FIRST from the RESULT STATE the patient is left in
(VerbNet class semantics keyed by WordNet sense, an offline foundation asset; the brain values the simulated outcome
state, not the verb's lexical pleasantness) and only then from the verb's word-level norm.
Glass-box; no external LLM at inference. SELF-CONTAINED: hdlab-only imports.
"""
from __future__ import annotations

__bf_status__ = "BF_SPIRIT"   # BF | BF_SPIRIT | NOT_BF | BF_UNPINNED | BF_UNVERIFIED ; mirrors data/bf_status_registry.jsonl
__bf_verified__ = "2026-09-12 pri-7 landing (strategy; reverified 9/9+6/6): force-dynamic arithmetic = Wolff force structure x Warriner endstate valence x graded Beavers affectedness gate; computational-level composite (RESEARCH_harm_help_and_selectional_math_2026-09-12)"
__bf_note__ = "harm/help = force STRUCTURE (Wolff CAUSE/ENABLE/PREVENT) x patient endstate VALENCE (Warriner, OFC/amygdala valuation) x graded AFFECTEDNESS gate (Beavers/Dowty proto-patient; McRae-Tanenhaus thematic fit); subject-experiencer psych verbs excluded; NO verb list, NO read-path FrameNet parse; labelled BF_SPIRIT (composite of supported parts, not one pinned equation)"
__bf_corrections__ = ["2026-09-12 harm/help decision: verb-LIST membership + read-path FrameNet enumeration (NOT_BF) -> force-dynamic arithmetic with grounded valence + graded affectedness (BF_SPIRIT)", "2026-09-12 endstate valence: word-level Warriner sign (sense-conflating; batter/throttle/bludgeon abstained or mis-signed) -> RESULT-STATE read first (VerbNet sense-keyed state predicates valued by the affect lexicon + the innate nociceptive sign), word-level norm second (strategy, pri-14 research)"]

import os
import sys
from typing import Dict, Optional, Set

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from hdlab.force_dynamics_lexicon import build_force_lexicon      # CAUSE/PREVENT/ENABLE force classes
from hdlab.patient_tendency import lemmatize_verb                 # inflected surface -> verb lemma
from hdlab.thematic_role_labeler import lemma_verb                # governing-verb lemma (== bridge1.lemma_verb)
from hdlab.affect_lexicon import AffectLexicon                    # grounded endstate valence (Warriner norms)
import hdlab.psych_verb_frames as _PVF                            # subject- vs object-experiencer psych verbs (VerbNet)


_LEX: Optional[Dict[str, str]] = None
_AFX: Optional[AffectLexicon] = None


# --- structural gate: copied VERBATIM from the validated bridge1/v2 cells (no behaviour change) -------
# nearest_verb_idx: experiments/exp_bridge1_governor_grounding_v1.py; valid_direct_object:
# experiments/exp_bridge1_twostage_event_situation_v2.py. Inlined so this organ has ZERO experiments/
# import (hdlab self-containment / clean-checkout reproducibility).
def _nearest_verb_idx(tokens, pos, target_idx):
    for i in range(target_idx - 1, -1, -1):
        if pos[i] == "VERB":
            return i
    return -1


def _valid_direct_object(pos, gi: int, target_idx: int) -> bool:
    """True iff a governing verb exists (gi>=0) and no ADP token sits between it and the target -- i.e.
    the target is the verb's direct object, not inside/after a PP (DET/PRON in between are fine)."""
    if gi < 0 or target_idx <= gi:
        return False
    for i in range(gi + 1, target_idx):
        if i < len(pos) and pos[i] == "ADP":
            return False
    return True


def _lex() -> Dict[str, str]:
    global _LEX
    if _LEX is None:
        _LEX = build_force_lexicon()
    return _LEX


# ======================================================================================================
# THE FORCE-DYNAMIC HARM/HELP ARITHMETIC (landed 2026-09-12 from owner-DONE pri-7
# `harm_help_valence_is_a_fitted_verb_list_not_the_substrates_force_dynamic_arithmetic`; reverified 9/9 + 6/6;
# owner Q131: confirm mathematically BF, land top-down -- notes/SIGNAL_FLOW_MAP.md s3 and
# notes/RESEARCH_harm_help_and_selectional_math_2026-09-12.md). REPLACES the verb-LIST membership test (FrameNet harm
# frames enumerated on the read path + a hand backoff list) with the brain's computation, decomposed into TWO
# independently grounded bits plus a gate:
#   force STRUCTURE  -- Wolff's vector model (Wolff 2007; Wolff & Song 2003; Talmy 1988): the affector's force vs the
#                       patient's tendency -> CAUSE / ENABLE / PREVENT (hdlab.force_dynamics_lexicon). COMPUTATIONAL-
#                       LEVEL: behaviourally pinned for verb choice, not shown as a neural force vector while reading.
#   endstate VALENCE -- the affective value of the outcome FOR THE PATIENT (Warriner 2013 norms = the OFC/amygdala
#                       outcome-valuation machinery; PINNED for experienced outcomes, an extension to narrated outcomes).
#   AFFECTEDNESS gate -- graded E[proto-patient degree | verb sense] (Beavers 2011 hierarchy; Dowty 1991 proto-patient;
#                       McRae-Tanenhaus graded thematic fit); the ordinal ORDER is pinned, the degrees are OUR-INVENTION
#                       swept; sense posterior = WordNet SemCor counts; subject-experiencer psych verbs excluded (VerbNet).
#   decision          -- inanimate -> NA; not affecting -> abstain; PREVENT: blocking a bad endstate = HELP, a good one =
#                       HARM; CAUSE/ENABLE/affecting: the sign of the patient's endstate valence.
# Overall label: BF_SPIRIT -- a computational-level composite of well-supported parts (none pinned as ONE equation).
# MEASURED (solver; reverified first-hand): live 36-item modern gold 0.778 -> 0.944 (+0.167 CI[+0.056,+0.278], 6 gains
# / 0 losses); 32 social/emotional verbs the frame list missed 0.000 -> 0.875; info-free twin (scrambled valence +
# lexicon) loses; a valence-only control destroys neutral precision (gate AND structure are both necessary).
# DURABLE BOUNDARIES: communication-supersense harm verbs (betray/slander) need the strong-valence branch; near-zero-
# valence mild harm (scratch) abstains (valence coverage); the 36-item gold is directional; the board arm scores it.
# ======================================================================================================
TAU_STRONG = 0.45   # |valence| above which a state-changing SENSE + strong affect => affected (betray/slander)
TAU_AFFECT = 0.40   # engage threshold on the graded affectedness (SWEPT by the solver; plateau 0.38-0.45)
# HYPERNYM-CONSENSUS RESULT STATE (owner-DONE 2026-09-13, pri-14 remaining scope: the_harm_help_read_needs_the_affective_value_of_the_
# resulting_state...): when a verb's result state is not lexicalised, the brain values the outcome of the SUPERORDINATE action
# (anterior-temporal taxonomic hub: 'to savage' IS a kind of assault) -- WordNet troponymy over the verb's AFFECTING ANIMATE-OBJECT
# senses, trusted only under cross-sense SIGN CONSENSUS and strength >= TAU_HYPER (swept 0.30-0.50: CF-gold precision 1.00, 0
# neutral leaks, 0 wrong-sign at every point; 0.35 = the knee). Recovers savage/victimize/oppress/maul; 65 residual verbs newly
# decided at Connotation-Frames precision 1.00; whole-arm agreement with the human gold 0.9323 (landed 0.9276).
TAU_HYPER = 0.35
# a verb whose DOMINANT (most frequent) sense is one of these is NOT admitted by the superordinate extension (the object is a
# stimulus/topic, not an undergoer: recognize/notice); the subject-experiencer exclusion (admire/envy) is never overridden either.
_NON_AFFECTING_DOMINANT = {"perception", "cognition", "communication", "stative", "motion"}
# UPSTREAM JOINS landed with the same solution (all reuse existing BF organs; switchable for attribution):
UPSTREAM_JOINS = os.environ.get("HDLAB_FDV_UPSTREAM_JOINS", "1") == "1"   # event realization (polarity_operator) + prevented complement
SENSE_CONTEXT = os.environ.get("HDLAB_FDV_SENSE_CONTEXT", "1") == "1"     # sense-in-context (grounded_semantic_graph.select_sense)
# MEASURED 2026-09-13 11:40 on the 36-item live modern gold: letting a NON-affecting context-selected sense ABSTAIN cost 6 verdicts
# ("punched the student", "beat the prisoner", "bullied the intern" -> neutral; "fired the clerk" -> HELP): on short sentences the
# spreading activation settles on a wrong sense. So the context read only chooses AMONG affecting senses (the sign); a non-affecting
# selection defers to the verb-level cascade unless HDLAB_FDV_SENSE_ABSTAIN=1 (kept selectable for the measurement).
SENSE_ABSTAIN = os.environ.get("HDLAB_FDV_SENSE_ABSTAIN", "0") == "1"
AFFECTING_SUPERSENSES = {"contact", "body", "change", "emotion", "possession", "consumption",
                         "competition", "creation", "social"}
# Beavers (2011) affectedness hierarchy -> proto-patient degree per WordNet verb supersense. ORDER pinned
# (quantized change > non-quantized/consumption > surface-contact/possession > motion > communication/perception/
# cognition); the numeric degrees are OUR-INVENTION, swept.
_AFFECTEDNESS_BY_SUPERSENSE = {
    "change": 1.0, "body": 1.0, "consumption": 0.9, "emotion": 0.85, "contact": 0.7, "possession": 0.7,
    "competition": 0.7, "creation": 0.5, "social": 0.45, "motion": 0.3, "communication": 0.1,
    "perception": 0.0, "cognition": 0.0, "stative": 0.1, "weather": 0.0,
}
_SS_CACHE: Dict[str, Optional[str]] = {}
_ALLSS_CACHE: Dict[str, set] = {}
_AFFECT_CACHE: Dict[str, float] = {}


def _afx() -> AffectLexicon:
    global _AFX
    if _AFX is None:
        _AFX = AffectLexicon.load()
    return _AFX


def verb_first_supersense(verb: str) -> Optional[str]:
    """The verb's DOMINANT (first) WordNet sense supersense (mental-lexicon category knowledge; foundation asset)."""
    v = lemmatize_verb(verb)
    if v in _SS_CACHE:
        return _SS_CACHE[v]
    ss = None
    try:
        from nltk.corpus import wordnet as wn
        syn = wn.synsets(v, pos=wn.VERB)
        if syn:
            ss = syn[0].lexname().split(".")[1]
    except Exception:
        ss = None
    _SS_CACHE[v] = ss
    return ss


def _verb_all_supersenses(verb: str) -> set:
    v = lemmatize_verb(verb)
    if v in _ALLSS_CACHE:
        return _ALLSS_CACHE[v]
    out: set = set()
    try:
        from nltk.corpus import wordnet as wn
        out = {s.lexname().split(".")[1] for s in wn.synsets(v, pos=wn.VERB)}
    except Exception:
        out = set()
    _ALLSS_CACHE[v] = out
    return out


def affectedness_score(verb: str) -> float:
    """E[proto-patient affectedness | sense], sense posterior = WordNet SemCor tagged counts (+1 smoothing).
    Graded and continuous: high for change/contact/emotion verbs, ~0 for perception/communication."""
    v = lemmatize_verb(verb)
    if v in _AFFECT_CACHE:
        return _AFFECT_CACHE[v]
    num = den = 0.0
    try:
        from nltk.corpus import wordnet as wn
        for s in wn.synsets(v, pos=wn.VERB):
            ss = s.lexname().split(".")[1]
            cnt = 1.0
            for lm in s.lemmas():
                if lm.name().lower() == v:
                    cnt += lm.count()
            num += cnt * _AFFECTEDNESS_BY_SUPERSENSE.get(ss, 0.3)
            den += cnt
    except Exception:
        den = 0.0
    val = (num / den) if den else 0.0
    _AFFECT_CACHE[v] = val
    return val


def _is_subject_experiencer(verb: str) -> bool:
    """admire/envy/fear/love: the OBJECT is the stimulus, the SUBJECT feels (VerbNet admire-31.2) -> not affecting."""
    v = lemmatize_verb(verb)
    return v in _PVF.SUBJ_EXP_VERBS and v not in _PVF.OBJ_EXP_VERBS


def is_affecting(verb: str, lexicon: Optional[Dict[str, str]] = None, afx: Optional[AffectLexicon] = None,
                 tau: Optional[float] = None) -> bool:
    """Does the verb transmit a force/consequence that changes the patient's state? (a) exclude subject-experiencer
    psych verbs; (b) marked PREVENT/ENABLE force senses -> affected; (c) graded affectedness >= tau -> affected;
    (d) strongly-valenced verbal/social harm whose dominant sense is communication (betray/slander) -> affected."""
    lexicon = _lex() if lexicon is None else lexicon
    afx = _afx() if afx is None else afx
    tau = TAU_AFFECT if tau is None else tau
    v = lemmatize_verb(verb)
    if _is_subject_experiencer(v):
        return False
    if lexicon.get(v) in ("PREVENT", "ENABLE"):
        return True
    if affectedness_score(v) >= tau:
        return True
    val = afx.valence(v)
    if verb_first_supersense(v) == "communication" and val is not None and abs(val) >= 0.5 \
            and (_verb_all_supersenses(v) & {"emotion", "social", "body", "change"}):
        return True
    # (e) UPSTREAM FIX (2026-09-13): the SemCor-frequency average above discards a MARKED-but-infrequent affecting sense ('savage':
    # the attack sense diluted by the criticize sense). A verb whose affecting-animate SUPERORDINATE is unambiguously affect-laden
    # IS an affecting event -- the same categorisation that signs it admits it. GUARDED: never a subject-experiencer verb, never a
    # verb whose dominant sense is perception/cognition/communication/stative/motion (un-guarded this leaked 6 neutral verbs; guarded 0).
    if verb_first_supersense(v) in _NON_AFFECTING_DOMINANT:
        return False
    if hyper_state_sign(v, afx) is not None:
        return True
    # (f) the SAME manner/genus decomposition doing double duty (2026-09-13): a verb whose lexicalised manner
    # is unambiguously forceful and valenced IS an affecting event -- one categorisation admits it and signs it.
    return MANNER_READ and (manner_state_sign(v, afx) is not None or genus_state_sign(v, afx) is not None)


WEAK_VALENCE = 0.10   # |word-level valence| below this is treated as UNINFORMATIVE for the patient's outcome (swept)
_EV_CACHE: Dict[str, Optional[int]] = {}

# ---- RESULT-STATE ARM (strategy 2026-09-12, pri-14) -------------------------------------------------------------
# The brain values the STATE the patient ends up in (OFC/vmPFC outcome valuation over a simulated event; Barsalou /
# Zwaan situation simulation), not the verb's lexical pleasantness. Causative verbs lexicalise a RESULT STATE (Levin /
# Rappaport Hovav). Source = VerbNet class semantics over the Patient at result(E)/end(E), keyed by WORDNET SENSE KEY
# (offline foundation asset; tools/build_verbnet_result_state_asset.py), read only for the verb's AFFECTING senses
# that take an ANIMATE object (WordNet frames 9/10/17/18 "----s somebody"). The state is VALUED by the affect lexicon
# (harmed / suffocate / degradation / not-alive) or by the innate nociceptive sign (forceful contact on the body).
# No verb list; a verb is read through its senses' classes. Measured (research note 2026-09-12): agreement with the
# word-level sign 0.87 where both exist (n=79); the 10 disagreements are weapon/assault senses read correctly for a
# person (club, brain, birch, throttle); 31 formerly-abstaining verbs decided (batter, pound, slash, crush ...).
RESULT_STATE_READ = True
RESULT_STATE_ASSET = os.path.join(_REPO, "data", "frontend_assets", "verbnet_result_state_v1.json")
ANIMATE_OBJECT_FRAMES = {9, 10, 17, 18}
STATE_MIN = 0.5                      # |mean state value| below this abstains (values are near +-1; swept: insensitive)
_RS_TABLE: Optional[Dict[str, list]] = None
_RS_CACHE: Dict[str, Optional[float]] = {}


def result_state_table() -> Dict[str, list]:
    """sense key -> [[verbnet class, member, [state ...]], ...] (offline asset; {} when absent -> arm abstains)."""
    global _RS_TABLE
    if _RS_TABLE is None:
        try:
            import json
            with open(RESULT_STATE_ASSET, "r", encoding="utf-8") as f:
                _RS_TABLE = dict(json.load(f).get("states", {}))
        except Exception:
            _RS_TABLE = {}
    return _RS_TABLE


def state_value(state: str, afx: Optional[AffectLexicon] = None) -> Optional[float]:
    """Affective value of a result-state predicate for the patient: the affect lexicon's valence of the state word
    (negation flips); forceful contact on the body = the innate nociceptive sign (-1, PINNED: pain is not learned)."""
    if state == "forceful_contact_end":
        return -1.0
    afx = _afx() if afx is None else afx
    neg = state.startswith("!")
    word = state.lstrip("!").split("_")[0]
    val = afx.valence(word)
    if val is None:
        return None
    return -val if neg else val


def result_state_evidence(verb: str, states: Optional[Dict[str, list]] = None) -> list:
    """[(synset, lemma, verbnet class, state), ...] over the verb's affecting animate-object senses."""
    table = result_state_table() if states is None else states
    v = lemmatize_verb(verb)
    out = []
    if not table:
        return out
    try:
        from nltk.corpus import wordnet as wn
        for ss in wn.synsets(v, pos=wn.VERB):
            if ss.lexname().split(".")[1] not in AFFECTING_SUPERSENSES:
                continue
            if not (set(ss.frame_ids()) & ANIMATE_OBJECT_FRAMES):
                continue
            for lm in ss.lemmas():
                key = lm.key().split("::")[0]
                for cid, member, sts in table.get(key, ()):
                    for st in sts:
                        out.append((ss.name(), lm.name(), cid, st))
    except Exception:
        return []
    return out


def result_state_value(verb: str, afx: Optional[AffectLexicon] = None,
                       states: Optional[Dict[str, list]] = None) -> Optional[float]:
    """Mean affective value of the result states the verb's affecting animate-object senses leave the patient in;
    None when the foundation names no result state (honest abstention -> the word-level norm is consulted)."""
    default = afx is None and states is None
    v = lemmatize_verb(verb)
    if default and v in _RS_CACHE:
        return _RS_CACHE[v]
    vals = [sv for *_, st in result_state_evidence(v, states) for sv in [state_value(st, afx)] if sv is not None]
    out = (sum(vals) / len(vals)) if vals else None
    if default:
        _RS_CACHE[v] = out
    return out


def endstate_valence_sign(verb: str, afx: Optional[AffectLexicon] = None,
                          states: Optional[Dict[str, list]] = None, posterior=None) -> Optional[int]:
    """The affective value of the patient's ENDSTATE, read at the SENSE level (strategy 2026-09-12, the landing's
    downstream check): Warriner's word-level valence conflates a verb's senses -- 'throttle' is rated mildly POSITIVE
    (the engine sense) though its affecting sense is 'strangle'; 'batter' is near-neutral (the food sense); 'bludgeon'
    has no norm at all. The brain reads meaning at the sense level (the settled-vector principle; Rodd), so when the
    word-level norm is absent or weak (|v| < WEAK_VALENCE) the outcome valence is the mean Warriner valence of the
    LEMMAS of the verb's AFFECTING senses (body/contact/change/emotion/... supersenses), SemCor-weighted -- i.e. the
    affective value of the state the patient is put in, estimated from the synonyms that name it. Still None when no
    affecting-sense lemma carries a norm (honest abstention)."""
    default_afx = (afx is None or afx is _AFX) and states is None
    afx = _afx() if afx is None else afx
    v = lemmatize_verb(verb)
    if default_afx and posterior is None and v in _EV_CACHE:   # cache ONLY for the live lexicon, context-free reads only
        return _EV_CACHE[v]
    sign: Optional[int] = None
    if RESULT_STATE_READ:                       # 1. the RESULT STATE the patient is left in (the brain's valuation target)
        sv = result_state_value(v, None if afx is _AFX else afx, states)
        if sv is not None and abs(sv) >= STATE_MIN:
            sign = 1 if sv > 0 else -1
    if sign is None:                            # 2. the SENSE-KEYED value (pri 100): the word-form norm weighted by rho, fused with
        from hdlab.affect_lexicon import sense_endstate_sign   #    the expectation over the sense posterior (see SENSE_POSTERIOR)
        sgn, verdict = sense_endstate_sign(v, posterior) if afx is _AFX else (None, "na")
        if verdict == "sign":
            sign = sgn
        elif verdict == "neutral":              # a DECIDED neutral: the active meaning leaves the patient unchanged -> 0, stop
            if default_afx and posterior is None:
                _EV_CACHE[v] = 0
            return 0
        elif verdict == "na":                   # not in the sense asset -> the word-level norm, unchanged
            val = afx.valence(v)
            if val is not None and abs(val) >= WEAK_VALENCE:
                sign = 1 if val > 0 else -1
    if sign is None:                            # 3. the outcome of the SUPERORDINATE action (taxonomic inheritance; 2026-09-13)
        sign = hyper_state_sign(v, None if afx is _AFX else afx)
    if sign is None and MANNER_READ:            # 4. the MANNER the verb lexicalises (Talmy manner/result complementarity)
        sign = manner_state_sign(v, None if afx is _AFX else afx)
    if sign is None and MANNER_READ:            # 5. the DEFINITION's genus, valued by this organ's result-state read
        sign = genus_state_sign(v, None if afx is _AFX else afx)
    # else: ABSTAIN. TRIED 2026-09-12 and WITHDRAWN the same night: backing off to the mean Warriner valence of the
    # affecting-sense SYNONYM lemmas (throttle -> strangle ...) turned batter/throttle/bludgeon into HELP -- the synonym
    # lemmas carry the same word-level sense conflation one step removed (bound/limit/buffet rate positive). A wrong
    # HARM/HELP is worse than an honest abstention. The brain-faithful fix is the affective value of the RESULTING
    # STATE the patient is put in (a resulting-state read / verb-sense-in-context), the solver's filed deepest step;
    # 2026-09-12 (pri-14 research): that read now EXISTS as the result-state arm above (VerbNet sense-keyed states);
    # verbs whose senses name no result state in the foundation AND whose norm is weak (wrench, maul) still ABSTAIN.
    if default_afx and posterior is None:
        _EV_CACHE[v] = sign
    return sign


def hyper_state_value(verb: str, afx: Optional[AffectLexicon] = None) -> Optional[float]:
    """Mean affective value of the SUPERORDINATE action(s) of the verb's AFFECTING ANIMATE-OBJECT senses, trusted only under
    cross-sense SIGN CONSENSUS. None when no affecting-animate sense has an affect-valued hypernym, or when the per-sense signs
    disagree (the manner-encoded / polysemous cases -> honest abstain). Value = Warriner valence of the hypernym synsets' lemma
    heads, averaged per sense, then across senses. (Solver prototype experiments/exp_fd_result_state_hypernym_v1.py, verbatim.)"""
    afx = _afx() if afx is None else afx
    v = lemmatize_verb(verb)
    try:
        from nltk.corpus import wordnet as wn
    except Exception:
        return None
    per_sense = []
    for ss in wn.synsets(v, pos=wn.VERB):
        if ss.lexname().split(".")[1] not in AFFECTING_SUPERSENSES:
            continue
        if not (set(ss.frame_ids()) & ANIMATE_OBJECT_FRAMES):
            continue
        hv = []
        for h in ss.hypernyms():
            for lm in h.lemmas():
                x = afx.valence(lm.name().replace("_", " ").split()[0])
                if x is not None:
                    hv.append(x)
        if hv:
            per_sense.append(sum(hv) / len(hv))
    if not per_sense:
        return None
    if all(x > 0 for x in per_sense) or all(x < 0 for x in per_sense):
        return sum(per_sense) / len(per_sense)
    return None                                   # sign disagreement across senses -> abstain (honest)


def hyper_state_sign(verb: str, afx: Optional[AffectLexicon] = None, tau: float = TAU_HYPER) -> Optional[int]:
    hv = hyper_state_value(verb, afx)
    if hv is not None and abs(hv) >= tau:
        return 1 if hv > 0 else -1
    return None


# ======================================================================================================
# MANNER-INTENSITY ARM (solver 2026-09-13, pri-98 `manner_encoded_harm_needs_an_intensity_read...`).
# THE GAP IT CLOSES: for brutalize / manhandle / maltreat / tyrannize / subjugate / gore the harm is in a
# MANNER word. VerbNet names no result state, the Warriner norm is absent or weak, and WordNet troponymy gives
# the affect-NEUTRAL superordinate ('treat', 'handle') -- so the cascade above abstains (measured at HEAD:
# 6 of the 15 named manner verbs abstain; 9 decide).
# THE BRAIN: MANNER/RESULT COMPLEMENTARITY (Talmy 1985/2000; Levin & Rappaport Hovav 2010, PINNED lexicalisation
# universal) -- a verb root lexicalises the MANNER of an action or its RESULT, never both, so for a manner verb
# the valuation target IS the manner. Comprehension SIMULATES it (Barsalou 1999; Zwaan; Pulvermuller action-word
# somatotopy) and the OFC/vmPFC values the simulated outcome:
#     value(patient endstate) = sign(valence(manner)) , gated by intensity(manner)
# SIGN from the evaluative axis, MAGNITUDE from the CIRCUMPLEX RADIUS of the manner's core affect (Russell 1980,
# PINNED: core affect is a 2-D valence x arousal space whose radius is intensity and whose angle is quality) or
# from the GROUNDED action/contact strength of the simulation (Lancaster sensorimotor norms), whichever is
# larger. MEASURED (experiments/exp_manner_intensity_harm_v1.py, independent Connotation-Frames human gold):
# with a HIGH-arousal manner the valence sign agrees with the human gold 0.864 (negative) / 0.769 (positive);
# with a LOW-arousal manner 0.643 / 0.633 -- the intensity gate is what makes the sign trustworthy, and a
# high-arousal POSITIVE manner (excite/arouse/animate) reads HELP, not HARM: the two channels do different jobs.
# WHERE THE MANNER WORD COMES FROM: the verb's WordNet definition, decomposed OFFLINE into manner / means /
# result / genus slots by the READER'S OWN glass-box stack (count-based category organ + attachment arm) --
# tools/build_manner_intensity_asset.py; a dict is shipped, nothing external runs at inference. The entries are
# COUNTS, so `observe_manner()` accrues the same units from running prose (plastic, never frozen).
# SHAPE: strictly ADDITIVE and RESIDUAL-ONLY, like the superordinate arm. REFUTED-AS-BUILT and NOT shipped
# (measured against the human gold): putting the manner ABOVE the diffuse word-level norm costs the whole-arm
# Connotation-Frames agreement 0.9333 -> 0.9111, and abstaining on manner-host verbs ('treat'/'handle', whose
# outcome really is underspecified without a manner) costs 0.9014 and a live-gold item.
# MEASURED at the shipped operating point: 6/6 of the manner slice recovered, 15/15 of the named manner verbs
# HARM (HEAD 9/15), 46 residual verbs newly decided at Connotation-Frames precision 1.00 with 0 wrong signs,
# 0 leaks on P_NEUTRAL_BROAD, whole-arm CF agreement 0.9333 >= HEAD 0.9320, live 36-item gold 24/24 unchanged;
# scrambled-intensity twin 4/6 and 0.875, scrambled-valence twin 2/6 with 3 wrong HELP, parse-free twin 0/6.
# ======================================================================================================
MANNER_READ = os.environ.get("HDLAB_FDV_MANNER_READ", "1") == "1"
MANNER_ASSET = os.path.join(_REPO, "data", "frontend_assets", "manner_intensity_v1.json")
TAU_INTENSITY = 0.40    # SWEPT 0.35-0.60 x TAU_MANNER_VAL 0.10-0.30: CF precision on new decisions 1.00 and 0
TAU_MANNER_VAL = 0.10   # neutral leaks at EVERY point; 0.40/0.10 is the knee (46 decided vs 15 at 0.60/0.30)
A0 = 0.40               # the circumplex resting point (neutral arousal reference); OUR-INVENTION, swept
K_AROUSAL = 1.0
K_GROUNDED = 1.0
MANNER_SLOTS = ("ADVMOD", "MANNER_PP", "MEANS_PP", "RESULT_ADJ")   # the GENUS slot is read separately, below
_MANNER: Optional[Dict] = None


def manner_table() -> Dict:
    """The offline manner asset ({} when absent -> the arm abstains and nothing else changes)."""
    global _MANNER
    if _MANNER is None:
        try:
            import json
            with open(MANNER_ASSET, "r", encoding="utf-8") as f:
                _MANNER = dict(json.load(f))
        except Exception:
            _MANNER = {"words": {}, "evidence": {}}
    return _MANNER


def observe_manner(verb: str, filler: str, slot: str = "ADVMOD", synset: str = "*online*") -> None:
    """THE ONLINE PATH (plastic, never frozen). A manner adverb bound to a predicate in running prose accrues
    the SAME count the offline definition parse accrues; the strengths are one pure function of these counts."""
    ev = manner_table().setdefault("evidence", {}).setdefault(lemmatize_verb(verb), [])
    for row in ev:
        if row[0] == synset and row[1] == slot and row[2] == filler:
            row[3] += 1
            return
    ev.append([synset, slot, filler, 1])


def manner_intensity(word: str, afx: Optional[AffectLexicon] = None) -> Optional[float]:
    """Simulated intensity of a manner in [0,1]: max(circumplex radius of its core affect, grounded action
    strength). None when no norm covers the word."""
    afx = _afx() if afx is None else afx
    w = word.lower()
    v = afx.valence(w)
    a = afx.arousal(w)
    g = manner_table().get("words", {}).get(w, {}).get("g")
    if v is None and a is None and g is None:
        return None
    r2 = (float(v) ** 2 if v is not None else 0.0)
    if a is not None:
        r2 += (K_AROUSAL * max(0.0, float(a) - A0)) ** 2
    r = r2 ** 0.5
    if g is not None:
        r = max(r, K_GROUNDED * float(g))
    return min(1.0, r)


def manner_state_value(verb: str, afx: Optional[AffectLexicon] = None) -> Optional[float]:
    """Affective value of the patient's endstate as determined by the MANNER the verb lexicalises, under the
    same precision discipline that rescued the superordinate read: value per SENSE, and trust the result only
    under CROSS-SENSE SIGN CONSENSUS (senses that disagree about the manner's goodness -> honest abstain)."""
    afx = _afx() if afx is None else afx
    v = lemmatize_verb(verb)
    per_sense: Dict[str, list] = {}
    for syn, slot, filler, cnt in manner_table().get("evidence", {}).get(v, ()):
        if slot not in MANNER_SLOTS:
            continue
        x = afx.valence(filler)
        if x is None or abs(x) < TAU_MANNER_VAL:
            continue
        inten = manner_intensity(filler, afx)
        if inten is None or inten < TAU_INTENSITY:
            continue
        per_sense.setdefault(syn, []).append((float(x), float(cnt)))
    vals = []
    for items in per_sense.values():
        wsum = sum(c for _x, c in items)
        vals.append(sum(x * c for x, c in items) / wsum)
    if not vals:
        return None
    if all(x > 0 for x in vals) or all(x < 0 for x in vals):
        return sum(vals) / len(vals)
    return None


def manner_state_sign(verb: str, afx: Optional[AffectLexicon] = None) -> Optional[int]:
    mv = manner_state_value(verb, afx)
    return None if mv is None else (1 if mv > 0 else -1)


def genus_state_sign(verb: str, afx: Optional[AffectLexicon] = None) -> Optional[int]:
    """The DEFINITION's genus verb valued by THIS organ's result-state read, under full cross-sense UNANIMITY.
    'gore' = "wound by piercing": the definitional superordinate is a result verb the organ already values
    (wound -> -0.77) where WordNet troponymy gives a manner-neutral parent (+0.19). TWO restrictions, each
    measured, without which this degenerates into the refuted parse-free gloss read: (a) the genus must itself
    NAME A RESULT STATE (inheriting a genus's diffuse word norm leaks -- 'visit' = "pay a brief visit" inherits
    pay's +0.42: exactly 1 leak on P_NEUTRAL_BROAD); (b) UNANIMITY rather than non-contradiction -- EVERY
    affecting-animate sense with a genus must yield a sign ('spur' = "give heart or courage to" beside "strike
    with a spur"; reading only the second produced this arm's one wrong sign against the human gold)."""
    v = lemmatize_verb(verb)
    bysyn: Dict[str, list] = {}
    for syn, slot, filler, _c in manner_table().get("evidence", {}).get(v, ()):
        if slot == "GENUS" and filler != v:
            bysyn.setdefault(syn, []).append(filler)
    if not bysyn:
        return None
    signs = []
    for genera in bysyn.values():
        here = []
        for g in genera:
            rs = result_state_value(g, afx)
            if rs is not None and abs(rs) >= STATE_MIN:
                here.append(1 if rs > 0 else -1)
        if not here:
            return None
        signs.extend(here)
    if all(x > 0 for x in signs):
        return 1
    if all(x < 0 for x in signs):
        return -1
    return None


# --- the manner adverb in RUNNING PROSE, read from the reader's own GRADED governor -------------------------
# THE UPSTREAM LOSS, COUNTED (36-sentence adverb-in-prose gold): the live governor's POINT head for a clause-
# final manner adverb is the preceding NOUN in 33/36 sentences (argmax adverb->verb 3/36; mean posterior mass on
# the verb 0.215). An adverb is not a manner modifier of a common noun, and the attachment arm KEEPS THE
# ALTERNATIVES ALIVE (MacDonald 1994) -- so this consumer reads the POSTERIOR P(head = the predicate | adverb)
# instead of the argmax. Measured: graded read 0.639 vs argmax read 0.472 vs the floor 0.444 (+0.194,
# CI [+0.083, +0.306], CI-separated). The argmax read buys almost nothing; the graded hand-off is the mechanism.
# The right permanent fix is upstream (an ADV's governor is a predicate -- a category-conditioned arc constraint
# in hdlab/attachment_arm.py); filed as a board item, not done here.
MANNER_PROSE = os.environ.get("HDLAB_FDV_MANNER_PROSE", "1") == "1"
# SENSE-KEYED AFFECT (pri 100, landed 2026-09-13 20:50): the verb's affect value is read at the SENSE level -- value(verb | context)
# = sum_s P(s | context) v(s), fused with the word-form norm weighted by the word's own sense-unambiguity rho (the precision term
# pri 98 named as the one rung it could not crack). P(s | context) is the semantic graph's own log-linear blend of the resting level
# with the settled spreading activation, read as a DISTRIBUTION instead of an argmax (hdlab.affect_lexicon.sense_endstate_sign).
# Measured (solver cell, reverified 19:12): neutral-cell prose errors 8 -> 3, prose gold 0.444 -> 0.667 CI-sep over the floor, CF
# whole-arm 0.932 -> 0.949, SemCor sense agreement 0.975 vs the word norm 0.815; 0 leaks, live gold 24/24. HDLAB_FDV_SENSE_POSTERIOR=0
# = resting-level expectation only (no context).
SENSE_POSTERIOR = os.environ.get("HDLAB_FDV_SENSE_POSTERIOR", "1") == "1"
TAU_HEAD_MASS = 0.10    # posterior mass on the predicate below which the adverb is not this event's manner


def _adverb_stem(word: str) -> Optional[str]:
    """The ADJECTIVE a manner adverb is derived from ('brutally'->'brutal'), else None. Route 1 = the stored
    derivational link (WordNet pertainym); route 2 = -ly stripping with a lexical check (Taft 1979 affix strip +
    lexical check; Pinker-Ullman dual route). Verb particles ('put down', 'take off') fail both routes."""
    w = word.lower()
    try:
        from nltk.corpus import wordnet as wn
        for s in wn.synsets(w, "r"):
            for lm in s.lemmas():
                if lm.name().lower() == w:
                    for p in lm.pertainyms():
                        return p.name().lower()
        if w.endswith("ly") and len(w) > 4:
            for cand in (w[:-2], w[:-1] + "e", (w[:-3] + "y") if w.endswith("ily") else None):
                if cand and wn.synsets(cand, "a"):
                    return cand
    except Exception:
        return None
    return None


def prose_manner_value(tokens, pos, gov_idx: int, parse=None,
                       afx: Optional[AffectLexicon] = None) -> Optional[float]:
    """Endstate value carried by the manner adverbs the reader binds to THIS event, or None. MORPHOLOGICAL
    REANALYSIS: the de-adjectival test is the real gate, so a -ly word the category organ tagged NOUN is still
    read as a manner adverb (words-and-rules conflict-triggered reanalysis; measured worth 1 item in 36)."""
    afx = _afx() if afx is None else afx
    if parse is None:
        parse = _parse_out(tokens, pos)
    if parse is None:
        return None
    marg = getattr(parse, "marginals", None)
    heads = dict(getattr(parse, "heads", {}) or {})
    num = den = 0.0
    for i, t in enumerate(tokens):
        if not str(t).isalpha():
            continue
        if pos[i] not in ("ADV", "ADJ") and not str(t).lower().endswith("ly"):
            continue
        st = _adverb_stem(str(t))
        if st is None:
            continue
        x = afx.valence(st)
        if x is None or abs(x) < TAU_MANNER_VAL:
            continue
        inten = manner_intensity(st, afx)
        if inten is None or inten < TAU_INTENSITY:
            continue
        if marg:
            mass = float(marg.get(i + 1, {}).get(gov_idx + 1, 0.0))
        else:
            mass = 1.0 if heads.get(i + 1, -1) == gov_idx + 1 else 0.0
        if mass < TAU_HEAD_MASS:
            continue
        num += float(x) * mass
        den += mass
    return (num / den) if den else None


# --- RUNG 3: SENSE-IN-CONTEXT (reuses the PPR spreading-activation WSD of hdlab.grounded_semantic_graph; BF) -----------------
_GSG = None


def _gsg():
    """The grounded semantic graph, built once per process (static foundation; ~80 s cold)."""
    global _GSG
    if _GSG is None:
        from hdlab.grounded_semantic_graph import GroundedSemanticGraph
        _GSG = GroundedSemanticGraph().build()
    return _GSG


def synset_endstate_sign(synset_name: Optional[str], afx: Optional[AffectLexicon] = None):
    """Value ONE context-selected synset's endstate for an animate patient. Returns (sign, affecting): affecting=False means the
    selected sense is not an affecting-animate event (the engine/food sense) -> the decision ABSTAINS; sign None with
    affecting=True means the sense is affecting but unvalued -> fall back to the verb-level cascade."""
    if synset_name is None:
        return None, None
    afx = _afx() if afx is None else afx
    from nltk.corpus import wordnet as wn
    ss = wn.synset(synset_name)
    if ss.lexname().split(".")[1] not in AFFECTING_SUPERSENSES or not (set(ss.frame_ids()) & ANIMATE_OBJECT_FRAMES):
        return None, False
    table = result_state_table(); vals = []
    for lm in ss.lemmas():
        key = lm.key().split("::")[0]
        for _cid, _member, sts in table.get(key, ()):
            for st in sts:
                sv = state_value(st, afx)
                if sv is not None:
                    vals.append(sv)
    if vals:
        m = sum(vals) / len(vals)
        if abs(m) >= STATE_MIN:
            return (1 if m > 0 else -1), True
    hv = [afx.valence(l.name().replace("_", " ").split()[0]) for h in ss.hypernyms() for l in h.lemmas()]
    hv = [x for x in hv if x is not None]
    if hv and abs(sum(hv) / len(hv)) >= TAU_HYPER:
        return (1 if sum(hv) / len(hv) > 0 else -1), True
    lv = [afx.valence(l.name().replace("_", " ").split()[0]) for l in ss.lemmas()]
    lv = [x for x in lv if x is not None]
    if lv and abs(sum(lv) / len(lv)) >= WEAK_VALENCE:
        return (1 if sum(lv) / len(lv) > 0 else -1), True
    return None, True


_CTX_STOP = {"the", "and", "but", "she", "him", "her", "his", "they", "them", "that", "this", "with", "from", "into", "was", "were",
             "had", "has", "have", "did", "not", "then", "when", "who", "which", "their", "our", "you", "your", "for", "are"}


def sense_posterior_in_context(verb: str, tokens, gov_idx: int, lam: Optional[float] = None):
    """P(s | context) over ALL of the verb's senses (pri 100): the semantic graph's own log-linear blend of the resting level with
    the settled spreading activation over the sentence's content words, read as a DISTRIBUTION (not an argmax). None when the
    verb has < 2 senses in the asset, the context is thin (< 2 content words), or the graph has no seed -- the resting level stands."""
    try:
        from hdlab.affect_lexicon import sense_rows, resting_level, SENSE_LAM
        import numpy as np
        from nltk.corpus import wordnet as wn
        from hdlab.grounded_semantic_graph import _sense_ppr
        lam = SENSE_LAM if lam is None else lam
        lem = lemmatize_verb(verb)
        rows = sense_rows(lem)
        if not rows or len(rows) < 2:
            return None
        ctx = [str(t).lower() for i, t in enumerate(tokens) if i != gov_idx and str(t).isalpha()]
        if sum(1 for w in ctx if len(w) > 2 and w not in _CTX_STOP) < 2:
            return None
        g = _gsg()
        tgt = [wn.synset(r[0]) for r in rows]; tn = [r[0] for r in rows]
        ppr = _sense_ppr(wn, lem, "V", ctx, g.syn2idx, g.T, len(g.syn2idx), tgt, tn)
        if ppr is None:
            return None
        pp = np.asarray(ppr, float) + 1e-6; pp = pp / pp.sum()
        lg = np.log(np.asarray(resting_level(rows), float)) + lam * np.log(pp)
        lg = lg - lg.max(); q = np.exp(lg)
        return list(q / q.sum())
    except Exception:
        return None


def context_sense_sign(verb: str, tokens, gov_idx: int):
    """(sign, affecting) of the CONTEXT-ACTIVE sense of the verb, or (None, None) when the graph selects no sense."""
    ctx = [t.lower() for i, t in enumerate(tokens) if i != gov_idx and t.isalpha()]
    # the read needs CONTEXT: with fewer than two content words the PPR cannot settle and select_sense falls back to the
    # FIRST (most frequent) sense, which abstained on "She beat the man" (smoke) -- thin context -> defer to the verb-level cascade
    if sum(1 for w in ctx if len(w) > 2 and w not in _CTX_STOP) < 2:
        return None, None
    try:
        g = _gsg()
        # the frequency RESTING LEVEL blended with the settled activation (the brain's base-rate prior; robust to thin context)
        syn = g.select_sense_blended(lemmatize_verb(verb), "V", ctx) if hasattr(g, "select_sense_blended") else g.select_sense(lemmatize_verb(verb), "V", ctx)
    except Exception:
        return None, None
    return synset_endstate_sign(syn)


# --- RUNG 2: the PREVENTED complement, read from the reader's OWN parse (BF finder; the surface scan is NOT shipped) ----------
def find_blocked_verb_parsed(tokens, pos, heads: Dict[int, int], prevent_idx0: int) -> Optional[int]:
    """The blocked event = the VERB whose dependency head-path reaches the PREVENT verb within 3 hops. 0-based; heads 1-based."""
    n = len(tokens); pv1 = prevent_idx0 + 1; best = None; best_hops = 99
    for i1 in range(1, n + 1):
        if i1 == pv1 or pos[i1 - 1] != "VERB":
            continue
        h = heads.get(i1); hops = 1; seen = set()
        while h and h != 0 and h not in seen and hops <= 3:
            if h == pv1:
                if hops < best_hops:
                    best, best_hops = i1 - 1, hops
                break
            seen.add(h); h = heads.get(h); hops += 1
    return best


def _parse_out(tokens, pos):
    """The reader's shared governor with its GRADED posterior kept (the manner read needs the alternatives)."""
    try:
        from hdlab.frontend import parser as _fe_parser
        return _fe_parser().parse(list(tokens), list(pos))
    except Exception:
        return None


def _parse_heads(tokens, pos) -> Optional[Dict[int, int]]:
    """The reader's shared governor (hdlab.frontend; default = the attachment arm) on an already-tagged sentence."""
    try:
        from hdlab.frontend import parser as _fe_parser
        return dict(_fe_parser().parse(list(tokens), list(pos)).heads)
    except Exception:
        return None


def harm_help_arithmetic(verb: str, animacy: str, *, endstate_reached: Optional[bool] = None,
                         embedded_endstate_valence: Optional[int] = None,
                         lexicon: Optional[Dict[str, str]] = None,
                         afx: Optional[AffectLexicon] = None,
                         states: Optional[Dict[str, list]] = None,
                         endstate_sign_override: Optional[int] = None, posterior=None) -> Optional[str]:
    """Force STRUCTURE x endstate VALENCE-for-patient -> HARM / HELP / NA / None(abstain).
    `endstate_reached` is None when unknown (the live bare-SVO path): for CAUSE/ENABLE unknown => the caused endstate
    happened; for PREVENT unknown => the prevention succeeded. The live path therefore reduces to:
      inanimate -> NA ; not-affecting -> abstain ; PREVENT/ENABLE -> HELP ; else sign(verb valence)."""
    lexicon = _lex() if lexicon is None else lexicon
    afx = _afx() if afx is None else afx
    if animacy == "inanimate":
        return "NA"
    v = lemmatize_verb(verb)
    cls = lexicon.get(v)
    if not is_affecting(v, lexicon, afx):
        return None
    vval = (endstate_sign_override if endstate_sign_override is not None
            else endstate_valence_sign(v, afx, states=states, posterior=posterior))   # result state, sense-keyed value, superordinate, manner, genus
    if cls == "PREVENT":
        ev = embedded_endstate_valence
        if ev is None:
            # pri 100 (18a): a DECIDED neutral (0) is not missing data -- only None takes the default path
            ev = -1 if vval is None else (0 if vval == 0 else -vval)   # default: prevents a NEGATIVE endstate
        prevention_succeeded = (endstate_reached is not True)
        outcome = (-ev) if prevention_succeeded else ev
        return "HELP" if outcome > 0 else ("HARM" if outcome < 0 else None)
    reached = True if endstate_reached is None else endstate_reached
    if not reached:
        return None
    ev = embedded_endstate_valence
    if ev is None:
        ev = vval
    if ev is None or ev == 0:
        return None
    return "HELP" if ev > 0 else "HARM"


def harm_help(verb: str, animacy: str) -> Optional[str]:
    """HARM / HELP / NA / None(abstain) -- the live bare-SVO decision = the force-dynamic arithmetic with the
    endstate unknown (signature unchanged for every consumer; see SIGNAL_FLOW_MAP s3)."""
    return harm_help_arithmetic(verb, animacy)

def force_dynamics_event_type(item, animacy_map, gov_class_dict):
    """Stage-2 drop-in for the affect/valence organ (replaces event_type_for_item_real's closed-list
    branch). SAME structural gate (nearest governing verb + valid direct object + WordNet animacy).
    Returns (BLOCK_HIGH|RECIPROCITY|NEUTRAL|None, category, gov_word) -> HARM|HELP|NA|abstain.
    `gov_class_dict` is accepted for signature parity with the retired call and is unused (the governor
    perceptron is retired from this decision)."""
    # STEP 3d (2026-09-12, pri-7 landing; SIGNAL_FLOW_MAP s3): when the READER hands over the predicate it already
    # bound this patient to (item["gov_idx"] = the event's verb index), use THAT -- one structure, one binding -- instead
    # of re-deriving the governor positionally (nearest preceding VERB with no ADP between; OUR-INVENTION gate that
    # made the decision depend on tokenization/tagging: 84/591 divergences on 19c text). The positional gate remains
    # the fallback for callers without a parse-bound predicate.
    gi = item.get("gov_idx")
    if gi is not None and 0 <= gi < len(item["pos"]) and item["pos"][gi] in ("VERB", "AUX"):
        pass
    else:
        gi = _nearest_verb_idx(item["tokens"], item["pos"], item["target_idx"])
        if not _valid_direct_object(item["pos"], gi, item["target_idx"]):
            return None, None, None
    gov_word = lemma_verb(item["tokens"][gi])
    a = animacy_map.get(item["target_word"].lower())
    if a is None:
        return None, None, gov_word
    # UPSTREAM JOINS (owner-DONE 2026-09-13; the solution's Rungs 1-3; each reuses an existing BF organ, none adds an asset):
    #  Rung 1 EVENT REALIZATION: hdlab.polarity_operator.event_polarity (Kaup-Zwaan negation toggle + Karttunen/de Marneffe
    #         veridicality) -> endstate_reached for non-PREVENT verbs ("did not hurt her" -> not reached -> neutral); PREVENT verbs
    #         abstain from this map (the verb's polarity is not the prevented endstate's realization). Measured 0.375 -> 0.95 (n=80).
    #  Rung 2 PREVENTED COMPLEMENT: for a PREVENT governor, the blocked event is read from the READER'S OWN parse (the verb whose
    #         head-path reaches the prevent verb) and valued by the same endstate cascade -> embedded_endstate_valence ("prevented
    #         the doctor from curing the patient" -> HARM). Measured 0.50 -> 0.90 (n=10); extraction is parser-gated (7/10).
    #  Rung 3 SENSE-IN-CONTEXT: the context-active sense (PPR spreading activation over WordNet++) is valued as ONE synset; a
    #         non-affecting active sense ("beat the eggs", "throttle the engine") ABSTAINS instead of the word-level HARM.
    toks, pos = item["tokens"], item["pos"]
    er = None; ev = None; override = None
    cls = _lex().get(gov_word)
    if UPSTREAM_JOINS:
        try:
            from hdlab.polarity_operator import event_polarity
            if cls != "PREVENT":
                pol = event_polarity(toks, gi, gov_word, pos=pos).polarity
                er = True if pol == 1 else (False if pol == -1 else None)
            else:
                heads = item.get("heads") or _parse_heads(toks, pos)
                if heads:
                    bi = find_blocked_verb_parsed(toks, pos, heads, gi)
                    if bi is not None:
                        ev = endstate_valence_sign(lemma_verb(toks[bi]))
        except Exception:
            er = None; ev = None
    if SENSE_CONTEXT and cls != "PREVENT":
        sgn, affecting = context_sense_sign(gov_word, toks, gi)
        if affecting is False and SENSE_ABSTAIN:
            return None, a["category"], gov_word                 # the active sense does not affect a patient -> abstain
        # the context read ADDS a sign where the verb-level cascade abstains; it never overrides a cascade decision (measured 11:42:
        # as an override it turned "fired the clerk" into HELP -- the selection among affecting senses is not yet reliable enough)
        override = sgn if (affecting and endstate_valence_sign(gov_word) is None) else None
    post = sense_posterior_in_context(gov_word, toks, gi) if SENSE_POSTERIOR else None     # pri 100: P(sense | this sentence)
    hh = harm_help_arithmetic(gov_word, a["animacy"], endstate_reached=er, embedded_endstate_valence=ev,
                              endstate_sign_override=override, posterior=post)
    # RUNG 5 MANNER-IN-PROSE (2026-09-13): PRECISION-WEIGHTED CUE FUSION (Ernst & Banks 2002 w ~ 1/sigma^2;
    # MacDonald 1994). The cues are ordered by their precision about THIS event's outcome: the verb's RESULT
    # STATE (direct, sense-keyed) > the MANNER of this very event (explicit, event-level) > the verb's WORD-LEVEL
    # norm (Warriner rates a word out of context: 'treat' +0.46 is largely the noun 'a treat', so the floor
    # answers HELP on "treated the prisoner brutally"). A manner therefore outranks the word norm and yields to
    # a result state -- "stabbed him gently" stays HARM. Measured on a 36-sentence adverb-in-prose gold:
    # 0.444 -> 0.639, +0.194 CI [+0.083, +0.306] CI-separated; the 36-item live modern gold is unchanged
    # (it contains no manner adverbs, so the read is identity there).
    if MANNER_PROSE and a["animacy"] != "inanimate" and cls != "PREVENT":
        try:
            mv = prose_manner_value(toks, pos, gi)
        except Exception:
            mv = None
        if mv is not None:
            rs = result_state_value(gov_word)
            if rs is None or abs(rs) < STATE_MIN:
                ss = verb_first_supersense(gov_word)
                admissible = is_affecting(gov_word) or (
                    not _is_subject_experiencer(gov_word)
                    and ss not in ("perception", "cognition", "stative", "motion")
                    and abs(mv) >= TAU_STRONG)
                if admissible:
                    hh = "HARM" if mv < 0 else "HELP"
    mapped = {"NA": "NEUTRAL", "HARM": "BLOCK_HIGH", "HELP": "RECIPROCITY"}.get(hh)
    return (mapped, a["category"], gov_word) if mapped else (None, a["category"], gov_word)
