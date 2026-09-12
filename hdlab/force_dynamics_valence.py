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
    return False


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
                          states: Optional[Dict[str, list]] = None) -> Optional[int]:
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
    if default_afx and v in _EV_CACHE:          # cache ONLY for the live lexicon (a scrambled twin must not read it)
        return _EV_CACHE[v]
    sign: Optional[int] = None
    if RESULT_STATE_READ:                       # 1. the RESULT STATE the patient is left in (the brain's valuation target)
        sv = result_state_value(v, None if afx is _AFX else afx, states)
        if sv is not None and abs(sv) >= STATE_MIN:
            sign = 1 if sv > 0 else -1
    if sign is None:                            # 2. the verb's word-level norm (a cue to that state; sense-conflating)
        val = afx.valence(v)
        if val is not None and abs(val) >= WEAK_VALENCE:
            sign = 1 if val > 0 else -1
    # else: ABSTAIN. TRIED 2026-09-12 and WITHDRAWN the same night: backing off to the mean Warriner valence of the
    # affecting-sense SYNONYM lemmas (throttle -> strangle ...) turned batter/throttle/bludgeon into HELP -- the synonym
    # lemmas carry the same word-level sense conflation one step removed (bound/limit/buffet rate positive). A wrong
    # HARM/HELP is worse than an honest abstention. The brain-faithful fix is the affective value of the RESULTING
    # STATE the patient is put in (a resulting-state read / verb-sense-in-context), the solver's filed deepest step;
    # 2026-09-12 (pri-14 research): that read now EXISTS as the result-state arm above (VerbNet sense-keyed states);
    # verbs whose senses name no result state in the foundation AND whose norm is weak (wrench, maul) still ABSTAIN.
    if default_afx:
        _EV_CACHE[v] = sign
    return sign


def harm_help_arithmetic(verb: str, animacy: str, *, endstate_reached: Optional[bool] = None,
                         embedded_endstate_valence: Optional[int] = None,
                         lexicon: Optional[Dict[str, str]] = None,
                         afx: Optional[AffectLexicon] = None,
                         states: Optional[Dict[str, list]] = None) -> Optional[str]:
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
    vval = endstate_valence_sign(v, afx, states=states)       # result-state first, word-level norm second (see above)
    if cls == "PREVENT":
        ev = embedded_endstate_valence
        if ev is None:
            ev = (-vval if vval else -1)                      # default: prevents a NEGATIVE endstate
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
    hh = harm_help(gov_word, a["animacy"])
    mapped = {"NA": "NEUTRAL", "HARM": "BLOCK_HIGH", "HELP": "RECIPROCITY"}.get(hh)
    return (mapped, a["category"], gov_word) if mapped else (None, a["category"], gov_word)
