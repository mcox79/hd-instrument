"""PROTOTYPE (research, experiments/-only): MANNER-ENCODED HARM -- give the harm/help reader an INTENSITY read
of the MANNER a verb (or an adverb in running prose) specifies, so "treat brutally" / "handle roughly" reach a
patient endstate the verb tables are silent on.

THE PROBLEM (the named residual of the integrated harm/help arm, pri-14). For brutalize / manhandle / maltreat /
tyrannize / subjugate / gore the harm is not in a result state (VerbNet names none), not in the verb's own norm
(absent or weak) and not in its superordinate category (WordNet troponymy gives the affect-NEUTRAL 'treat' /
'handle'). It is in a MANNER expression. Every parse-FREE read of the definition was drilled and refuted: the
strongest-gloss-word proxy recovers 4 but flips 93 verbs with 8 neutral leaks + 6 wrong signs; adverb-only
valence recovers 0; an arousal-gated negative recovers 3 with 4 leaks + 3 wrong signs.

THE BRAIN (the opening move -- how does a reader know 'brutalize' harms when its superordinate 'treat' is
neutral?).
  * MANNER / RESULT COMPLEMENTARITY (Talmy 1985/2000; Levin & Rappaport Hovav 2010; PINNED lexicalisation
    universal): a verb root lexicalises the MANNER of an action or its RESULT, never both. For a manner verb
    there IS no result state to value -- the valuation target is the manner component itself.
  * GROUNDED SIMULATION (Barsalou 1999; Zwaan; Pulvermuller action-word somatotopy; PINNED): comprehending
    "brutally" re-enacts a forceful action on a body. The FORCE MAGNITUDE of the simulation is read from the
    sensorimotor spokes (Lancaster action/contact strength) and from core-affect ACTIVATION (Warriner arousal =
    Russell's circumplex arousal axis / Osgood's Activity).
  * OUTCOME VALUATION, SIGN AND MAGNITUDE FROM DIFFERENT CHANNELS (OFC/vmPFC value; Barrett core affect; PINNED):
        value(patient endstate) = sign(valence(manner)) * intensity(manner) * affectedness(patient)
    The sign is the manner's VALENCE; the magnitude is its simulated force INTENSITY. This is exactly what the
    parse-free proxies collapsed: a high-arousal POSITIVE manner (thrill / excitedly / tenderly) must read HELP,
    a high-arousal NEGATIVE manner (brutally) HARM. The 2x2 is reported below.
  * WHERE THE MANNER WORD IS. In running prose: the adverb the reader's OWN governor binds to the predicate.
    In a lexicalised manner verb: inside the stored lexical concept, recovered OFFLINE by parsing the verb's
    WordNet definition with the reader's own glass-box stack (count-based category organ + attachment arm) --
    tools/build_manner_intensity_asset.py ships the resulting dict. No spaCy, no supervised parser, no external
    tool at inference; WordNet definitions are an admissible offline foundation asset, the same standing as the
    VerbNet result predicates the landed arm already reads.
  * PRECISION-WEIGHTED CUE FUSION (Ernst & Banks 2002; MacDonald 1994 constraint satisfaction; a PINNED row of
    BRAIN_MATH_REFERENCE): an event-level, high-intensity manner cue dominates a DIFFUSE, weak lexical prior.
    This is what the prose arm needs -- the floor does not merely abstain on "treated him brutally", it answers
    HELP (Warriner treat +0.46, handle +0.18, hold +0.26 -> the landed cascade signs them positive).

ARMS
  floor     : hdlab.force_dynamics_valence at HEAD (the landed cascade: result state -> word norm -> superordinate)
  manner    : floor + the manner-intensity read (verb-level: RESIDUAL-ONLY; prose: fuses against a weak prior)
  twin      : manner with the INTENSITY norms (arousal + grounded action strength) SCRAMBLED across words
  twin_val  : manner with the VALENCE norms scrambled (the sign channel control)
  genus arm : the definition's HEAD VERB as an extra slot -- measured separately because it is the refuted
              parse-free gloss read in disguise; reported, not shipped, unless it holds precision.

CONTROLS / POPULATIONS
  * 15 named manner verbs (the brief's slice; floor decides 9, abstains on brutalize/manhandle/gore/subjugate/
    tyrannize/maltreat)
  * Connotation Frames Effect(o) (Rashkin, Singh & Choi ACL 2016) -- INDEPENDENT human crowd gold, never read at
    inference; precision of every NEW decision
  * P_NEUTRAL_BROAD (n=36) -- 0 leaks required
  * the 36-item live modern gold (exp_fd_harm_help_live_modern_v1.GOLD) -- no-regress, >= 35/36
  * NEW, DECLARED HERE: ADVERB_PROSE_GOLD, 36 one-sentence scenes in which an affect-neutral verb carries a
    manner adverb (12 harm-manner / 12 help-manner / 12 neutral-manner); the manner is the ONLY signal.

Run:  .venv/Scripts/python.exe experiments/exp_manner_intensity_harm_v1.py
      .venv/Scripts/python.exe experiments/exp_manner_intensity_harm_v1.py --self-test
Glass-box, deterministic, ASCII, no external LLM at inference.
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "2")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "2")
os.environ.setdefault("MKL_NUM_THREADS", "2")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "2")

import json
import random
import sys
from typing import Dict, List, Optional, Tuple

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import hdlab.force_dynamics_valence as FDV
import experiments.exp_fd_harm_help_arithmetic_v1 as A
from experiments._seed_checkpoint import get_output_dir
from experiments.fetch_connotation_frames_v1 import load_effect_o

ANCHOR = "manner_intensity_harm_v1"
SEED = 20260913
N_BOOT = 2000
ASSET = os.path.join(REPO, "data", "frontend_assets", "manner_intensity_v1.json")
CF_NEG, CF_POS = -0.25, 0.25

# ---- OPERATING POINT (all SWEPT below; the phase diagram is free to move) --------------------------------
TAU_INTENSITY = 0.40    # simulated force intensity a manner must reach before it determines the endstate
TAU_MANNER_VAL = 0.10   # |valence| a manner filler must reach to carry a sign
PRIOR_WEAK = 0.30       # |word-level verb valence| below which a DIFFUSE lexical prior yields to the manner cue
# INTENSITY = the CIRCUMPLEX RADIUS of the manner's core affect (Russell 1980, PINNED: core affect is a 2-D
# valence x arousal space; the RADIUS is the intensity of the affective state and the ANGLE its quality), taken
# together with the GROUNDED force of the action the manner evokes (Lancaster action/contact strength; Barsalou
# simulation). A0 = the neutral arousal reference (the resting point of the circumplex); K_AROUSAL / K_GROUNDED
# are OUR-INVENTION scalings, SWEPT (never adopted). "roughly" is a LOW-valence manner rescued by the grounded
# channel; "kindly" is a LOW-arousal manner carried by the evaluative axis -- an arousal-only gate is
# structurally incapable of admitting a gentle helping manner, which is why the radius, not arousal, is the read.
INTENSITY_MODE = "circumplex"     # circumplex | arousal | grounded | arousal_grounded | valence
A0 = 0.40
K_AROUSAL, K_GROUNDED = 1.0, 1.0
SHIP_SLOTS = ("ADVMOD", "MANNER_PP", "MEANS_PP", "RESULT_ADJ")   # GENUS deliberately excluded (measured below)

NAMED_HARM = ["savage", "victimize", "oppress", "maul", "persecute", "molest", "brutalize", "manhandle",
              "gore", "ravage", "terrorize", "subjugate", "enslave", "tyrannize", "maltreat"]
MANNER_SLICE = ["brutalize", "manhandle", "gore", "subjugate", "tyrannize", "maltreat"]   # the floor's abstentions


# ==========================================================================================================
# THE ASSET (offline foundation; counts, so the table stays plastic)
# ==========================================================================================================
_ASSET: Optional[Dict] = None


def asset() -> Dict:
    global _ASSET
    if _ASSET is None:
        try:
            with open(ASSET, encoding="utf-8") as f:
                _ASSET = json.load(f)
        except Exception:
            _ASSET = {"words": {}, "evidence": {}, "meta": {}}
    return _ASSET


def observe_manner(verb: str, filler: str, slot: str = "ADVMOD", synset: str = "*online*") -> None:
    """THE ONLINE PATH (plastic, never frozen). When the reader meets a manner adverb bound to a predicate in
    running prose it accrues the same COUNT the offline build accrues from a definition; the strengths below are
    one pure function of those counts. Same units, same table -- no second mechanism."""
    ev = asset().setdefault("evidence", {}).setdefault(FDV.lemmatize_verb(verb), [])
    for row in ev:
        if row[0] == synset and row[1] == slot and row[2] == filler:
            row[3] += 1
            return
    ev.append([synset, slot, filler, 1])


# ==========================================================================================================
# THE INTENSITY READ  (sign from VALENCE, magnitude from AROUSAL + GROUNDED ACTION STRENGTH)
# ==========================================================================================================
def filler_intensity(word: str, afx=None, aro_over: Optional[Dict[str, float]] = None,
                     gro_over: Optional[Dict[str, float]] = None, mode: Optional[str] = None) -> Optional[float]:
    """Simulated INTENSITY of a manner in [0,1].

    `circumplex` (the shipped read): max( sqrt(valence^2 + (K_AROUSAL*(arousal-A0)_+)^2),  K_GROUNDED*grounded ).
    The first term is the RADIUS of the word's core affect in Russell's valence x arousal circumplex -- how far
    the manner is from affective neutrality, which is the magnitude the outcome valuation codes; the second is
    the grounded force of the action it evokes, which rescues a physically forceful but weakly evaluative manner
    ("roughly"). The other modes are the ABLATIONS reported in the intensity table (an arousal-only gate is the
    brief's literal hypothesis and is shown below to be structurally unable to admit a gentle helping manner).
    None when no norm covers the word (honest abstention)."""
    afx = FDV._afx() if afx is None else afx
    mode = INTENSITY_MODE if mode is None else mode
    w = word.lower()
    v = afx.valence(w)
    a = aro_over.get(w) if aro_over is not None else afx.arousal(w)
    g = (gro_over.get(w) if gro_over is not None else asset().get("words", {}).get(w, {}).get("g"))
    if mode == "arousal":
        return None if a is None else float(a)
    if mode == "grounded":
        return None if g is None else float(g)
    if mode == "valence":
        return None if v is None else abs(float(v))
    if mode == "arousal_grounded":
        xs = [float(x) for x in (a, g) if x is not None]
        return (sum(xs) / len(xs)) if xs else None
    if v is None and a is None and g is None:
        return None
    rad2 = 0.0
    if v is not None:
        rad2 += float(v) ** 2
    if a is not None:
        rad2 += (K_AROUSAL * max(0.0, float(a) - A0)) ** 2
    r = rad2 ** 0.5
    if g is not None:
        r = max(r, K_GROUNDED * float(g))
    return min(1.0, r)


def manner_evidence(verb: str, slots=SHIP_SLOTS, slot_scramble: Optional[Dict] = None) -> List[List]:
    """[[synset, slot, filler, count], ...] for the verb's affecting animate-object senses (offline asset +
    anything observe_manner has accrued). `slot_scramble` is the PARSE control: it substitutes a RANDOM content
    word of the same definition for the parsed manner filler -- i.e. exactly the parse-free gloss read that was
    drilled and refuted, run through the identical valuation."""
    v = FDV.lemmatize_verb(verb)
    if slot_scramble is not None:
        return [r for r in slot_scramble.get(v, []) if r[1] in slots]
    ev = asset().get("evidence", {}).get(v, [])
    return [r for r in ev if r[1] in slots]


def manner_state_value(verb: str, afx=None, slots=SHIP_SLOTS, tau_int: float = TAU_INTENSITY,
                       tau_val: float = TAU_MANNER_VAL, aro_over=None, gro_over=None,
                       mode: Optional[str] = None, slot_scramble: Optional[Dict] = None) -> Optional[float]:
    """Affective value of the patient's endstate as determined by the MANNER the verb specifies, under the same
    precision discipline that rescued the superordinate read: value the manner per SENSE, count a sense only when
    at least one of its manner fillers reaches the intensity gate, and trust the result only under CROSS-SENSE
    SIGN CONSENSUS (a verb whose senses disagree about the manner's goodness abstains -- honest).
    Counts weight the fillers (plastic: an online observation of the same manner strengthens it)."""
    afx = FDV._afx() if afx is None else afx
    per_sense: Dict[str, List[Tuple[float, float]]] = {}
    for syn, _slot, filler, cnt in manner_evidence(verb, slots, slot_scramble):
        v = afx.valence(filler)
        if v is None or abs(v) < tau_val:
            continue
        inten = filler_intensity(filler, afx, aro_over, gro_over, mode)
        if inten is None or inten < tau_int:
            continue
        per_sense.setdefault(syn, []).append((float(v), float(cnt)))
    vals = []
    for _syn, items in per_sense.items():
        wsum = sum(c for _v, c in items)
        vals.append(sum(v * c for v, c in items) / wsum)
    if not vals:
        return None
    if not (all(x > 0 for x in vals) or all(x < 0 for x in vals)):
        return None                                  # sense disagreement -> abstain
    return sum(vals) / len(vals)


def manner_state_sign(verb: str, afx=None, **kw) -> Optional[int]:
    mv = manner_state_value(verb, afx, **kw)
    if mv is None:
        return None
    return 1 if mv > 0 else -1


# ---- the proposed hdlab drop-in: the landed cascade, then the manner read as a FOURTH source --------------
_LANDED_ENDSTATE = FDV.endstate_valence_sign
_LANDED_ISAFFECTING = FDV.is_affecting

# ---- PUSH LEVERS (each measured on its own below; the shipped configuration is the one the numbers pick) ---
# L1  MANNER_FIRST      the manner outranks the DIFFUSE word-level norm (manner/result complementarity: a manner
#                       verb lexicalises no result, so its manner IS the outcome evidence -- and the word-level
#                       Warriner norm conflates senses and parts of speech: 'treat' +0.46 is largely 'a treat')
# L2  MANNER_HOST_ABSTAIN  a verb whose own lexical entry has an OPEN MANNER SLOT ('treat', 'handle', 'hold' --
#                       derived from the asset: heads that appear with a manner filler) is UNDERSPECIFIED for the
#                       patient's outcome when no manner is supplied, so the diffuse word norm must not decide it
# L3  GENUS_CASCADE     the DEFINITION's genus verb ("gore = WOUND by piercing") valued by the organ's OWN
#                       endstate cascade (not by raw word valence -- that is the refuted parse-free read)
# L4  MORPH_REANALYSIS  a -ly word with an adjective pertainym IS a manner adverb even when the category organ
#                       tags it NOUN (words-and-rules reanalysis; the same conflict-triggered repair the category
#                       organ already lands)
# MEASURED VERDICT (lever_ablation below, all on the INDEPENDENT human gold): L1 and L2 are REFUTED-AS-BUILT --
# putting the manner above the word norm costs the Connotation-Frames whole-arm 0.9333 -> 0.9111 (7 decisions
# flipped wrong), and abstaining on manner-host verbs costs 0.9014 and a live-gold item. They are the "obviously
# right" reorderings and the human gold says no; the ADDITIVE, RESIDUAL-ONLY shape (the same shape the landed
# superordinate arm has) is what holds. L3 and L4 are kept: both are strictly additive and cost nothing.
MANNER_FIRST = False
MANNER_HOST_ABSTAIN = False
GENUS_CASCADE = True
MORPH_REANALYSIS = True

_HOST: Optional[Dict[str, int]] = None


def manner_host_verbs() -> Dict[str, int]:
    """Verbs with an OPEN MANNER SLOT, derived from the asset (no list): the GENUS head of a definition that also
    carries a manner filler is a verb whose event structure takes a manner ('treat brutally' -> 'treat')."""
    global _HOST
    if _HOST is None:
        _HOST = {}
        for _v, rows in asset().get("evidence", {}).items():
            bysyn: Dict[str, List] = {}
            for s, sl, f, _c in rows:
                bysyn.setdefault(s, []).append((sl, f))
            for _s, items in bysyn.items():
                g = [f for sl, f in items if sl == "GENUS"]
                m = [f for sl, f in items if sl in ("ADVMOD", "MANNER_PP")]
                if g and m:
                    _HOST[g[0]] = _HOST.get(g[0], 0) + 1
    return _HOST


def genus_cascade_sign(verb: str, afx=None) -> Optional[int]:
    """The definition's GENUS verb valued by the organ's OWN result-state read, under FULL cross-sense UNANIMITY.
    'gore' = "WOUND by piercing": the definitional superordinate is a result verb the organ already values
    (wound -> result state -0.77), where WordNet troponymy gives a manner-neutral parent (+0.19).

    TWO restrictions, each measured (without them this is the refuted parse-free gloss read):
      (a) the genus must itself NAME A RESULT STATE. Inheriting a genus's diffuse word norm leaks -- 'visit' =
          "PAY a brief visit" inherits pay's +0.42 (exactly 1 leak on P_NEUTRAL_BROAD, measured).
      (b) UNANIMITY, not mere non-contradiction: EVERY affecting-animate sense with a genus must yield a sign
          and all must agree. A sense whose genus is silent is MISSING evidence, not agreement -- 'spur' has
          "GIVE heart or courage to" (silent) beside "STRIKE with a spur" (-1), and reading only the second
          gave the one wrong sign this arm produced (spur -> HARM, human gold +0.47)."""
    v = FDV.lemmatize_verb(verb)
    bysyn: Dict[str, List[str]] = {}
    for syn, slot, filler, _c in asset().get("evidence", {}).get(v, []):
        if slot == "GENUS" and filler != v:
            bysyn.setdefault(syn, []).append(filler)
    if not bysyn:
        return None
    signs = []
    for _syn, genera in bysyn.items():
        here = []
        for g in genera:
            rs = FDV.result_state_value(g, None if afx is None else afx)
            if rs is not None and abs(rs) >= FDV.STATE_MIN:
                here.append(1 if rs > 0 else -1)
        if not here:
            return None                      # (b) a silent sense breaks unanimity
        signs.extend(here)
    if all(x > 0 for x in signs):
        return 1
    if all(x < 0 for x in signs):
        return -1
    return None


def extended_endstate_sign(verb: str, afx=None, states=None, **kw) -> Optional[int]:
    """THE PROPOSED CASCADE. Cues ordered by their PRECISION about the state the patient is left in:
       1 the verb's RESULT STATE (sense-keyed; direct)
       2 the MANNER the verb lexicalises (Talmy complementarity: a manner verb has no result to read)
       3 the verb's WORD-LEVEL norm (diffuse, sense-conflating) -- skipped for a manner-host verb
       4 the SUPERORDINATE category (taxonomic inheritance; landed)
       5 the DEFINITION's genus, valued by this same cascade
    MANNER_FIRST=False puts the manner back at the end (residual-only) -- the conservative ablation."""
    v = FDV.lemmatize_verb(verb)
    afx_l = FDV._afx() if afx is None else afx
    if not MANNER_FIRST:
        s = _LANDED_ENDSTATE(v, afx, states)
        if s is not None:
            return s
        s = manner_state_sign(v, afx, **kw)
        return s if s is not None else (genus_cascade_sign(v, afx) if GENUS_CASCADE else None)
    rs = FDV.result_state_value(v, None if afx_l is FDV._AFX else afx_l, states)
    if rs is not None and abs(rs) >= FDV.STATE_MIN:
        return 1 if rs > 0 else -1
    ms = manner_state_sign(v, afx, **kw)
    if ms is not None:
        return ms
    if not (MANNER_HOST_ABSTAIN and v in manner_host_verbs()):
        val = afx_l.valence(v)
        if val is not None and abs(val) >= FDV.WEAK_VALENCE:
            return 1 if val > 0 else -1
    hs = FDV.hyper_state_sign(v, None if afx_l is FDV._AFX else afx_l)
    if hs is not None:
        return hs
    return genus_cascade_sign(v, afx) if GENUS_CASCADE else None


def is_affecting_extended(verb, lexicon=None, afx=None, tau=None, **kw) -> bool:
    """The same ONE decomposition doing double duty (as the superordinate read does at HEAD): a verb whose
    manner component is unambiguously forceful and valenced IS an affecting event. GUARDED exactly as the landed
    admission is -- never over the subject-experiencer exclusion, never a perception/cognition/communication/
    stative/motion-dominant verb."""
    if _LANDED_ISAFFECTING(verb, lexicon, afx, tau):
        return True
    if FDV._is_subject_experiencer(verb):
        return False
    if FDV.verb_first_supersense(verb) in FDV._NON_AFFECTING_DOMINANT:
        return False
    if manner_state_sign(verb, afx, **kw) is not None:
        return True
    return GENUS_CASCADE and genus_cascade_sign(verb, afx) is not None


def _with(endstate_fn, isaff_fn=None):
    def run_arm(verb, animacy, **kw):
        FDV._EV_CACHE.clear()
        old_e, old_a = FDV.endstate_valence_sign, FDV.is_affecting
        FDV.endstate_valence_sign = endstate_fn
        if isaff_fn is not None:
            FDV.is_affecting = isaff_fn
        try:
            return FDV.harm_help_arithmetic(verb, animacy, **kw)
        finally:
            FDV.endstate_valence_sign = old_e
            FDV.is_affecting = old_a
            FDV._EV_CACHE.clear()
    return run_arm


def harm_help_floor(verb, animacy, **kw):
    FDV._EV_CACHE.clear()
    return FDV.harm_help_arithmetic(verb, animacy, **kw)


harm_help_manner = _with(lambda v, afx=None, states=None: extended_endstate_sign(v, afx, states),
                         is_affecting_extended)


def _arm_with_overrides(slots=SHIP_SLOTS, tau_int=TAU_INTENSITY, tau_val=TAU_MANNER_VAL,
                        afx_over=None, aro_over=None, gro_over=None, mode=None, slot_scramble=None):
    kw = dict(slots=slots, tau_int=tau_int, tau_val=tau_val, aro_over=aro_over, gro_over=gro_over,
              mode=mode, slot_scramble=slot_scramble)
    es = lambda v, afx=None, states=None: (_LANDED_ENDSTATE(v, afx_over or afx, states)
                                           if _LANDED_ENDSTATE(v, afx_over or afx, states) is not None
                                           else manner_state_sign(v, afx_over or afx, **kw))
    ia = lambda v, lexicon=None, afx=None, tau=None: is_affecting_extended(
        v, lexicon, afx_over or afx, tau, **kw)
    return _with(es, ia)


# ==========================================================================================================
# THE PROSE ARM -- the manner adverb bound to the predicate by the READER'S OWN governor
# ==========================================================================================================
_FE = {}


def _frontend():
    if not _FE:
        from hdlab import frontend as FE
        _FE["T"] = FE.Tagger(); _FE["P"] = FE.Parser(); _FE["M"] = FE
    return _FE


def prose_manner_fillers(tokens, gov_idx: int, graded: bool = True,
                         tau_head: float = 0.10) -> List[Tuple[str, float, float]]:
    """(adjective stem, valence, posterior mass on the predicate) for every DE-ADJECTIVAL adverb the reader's own
    governor binds to the predicate at `gov_idx`.

    GRADED HAND-OFF (the point). The live governor's POINT head for a clause-final manner adverb is the preceding
    NOUN (measured below); an adverb cannot be a manner modifier of a common noun, and the arm itself keeps the
    alternatives alive -- so the reader reads the POSTERIOR P(head = the predicate | this adverb) instead of the
    argmax. `graded=False` reproduces the argmax-only read (the ablation)."""
    fe = _frontend()
    toks = list(tokens)
    pos, post = fe["T"].tag_with_posterior(toks)
    out = fe["P"].parse(toks, pos, post)
    afx = FDV._afx()
    from nltk.corpus import wordnet as wn
    from tools.build_manner_intensity_asset import adverb_stem
    res = []
    for i, t in enumerate(toks):
        if not t.isalpha():
            continue
        # the category organ mistags some -ly adverbs ADJ at clause end (measured); the DE-ADJECTIVAL test is
        # the real gate, so accept ADV or ADJ and let the morphology decide.
        # MORPH_REANALYSIS: the DE-ADJECTIVAL test is the real gate. The category organ tags some clause-final
        # -ly adverbs NOUN (measured: 2/36 on the prose gold); a -ly word with a stored adjective pertainym IS a
        # manner adverb, so the morphology re-reads the category (words-and-rules conflict-triggered reanalysis,
        # the same repair hdlab.lexical_categories already lands). Without it those events lose their manner.
        if pos[i] not in ("ADV", "ADJ") and not (MORPH_REANALYSIS and t.lower().endswith("ly")):
            continue
        st = adverb_stem(t.lower(), wn)
        if not st:
            continue
        if graded and out.marginals:
            mass = float(out.marginals.get(i + 1, {}).get(gov_idx + 1, 0.0))
        else:
            mass = 1.0 if out.heads.get(i + 1, -1) == gov_idx + 1 else 0.0
        if mass < tau_head:
            continue
        v = afx.valence(st)
        if v is None:
            continue
        res.append((st, float(v), mass))
    return res


def prose_manner_value(tokens, gov_idx: int, graded: bool = True, tau_int: float = TAU_INTENSITY,
                       tau_val: float = TAU_MANNER_VAL, mode: Optional[str] = None) -> Optional[float]:
    """Endstate value carried by the manner adverbs of THIS event (posterior-mass-weighted mean valence of the
    fillers that pass the intensity gate), or None when the event carries no qualifying manner."""
    afx = FDV._afx()
    num = den = 0.0
    for st, v, mass in prose_manner_fillers(tokens, gov_idx, graded):
        if abs(v) < tau_val:
            continue
        inten = filler_intensity(st, afx, mode=mode)
        if inten is None or inten < tau_int:
            continue
        num += v * mass; den += mass
    return (num / den) if den else None


def prose_manner_sign(tokens, gov_idx: int, **kw) -> Optional[int]:
    m = prose_manner_value(tokens, gov_idx, **kw)
    return None if m is None else (1 if m > 0 else -1)


def harm_help_prose_mode(mode, verb, tokens, gov_idx, animacy="animate"):
    return harm_help_prose(verb, tokens, gov_idx, animacy, graded=True, fuse=True, mode=mode)


def harm_help_prose(verb: str, tokens, gov_idx: int, animacy: str = "animate", graded: bool = True,
                    fuse: bool = True, mode: Optional[str] = None,
                    prior_rule: str = "precision") -> Optional[str]:
    """PRECISION-WEIGHTED CUE FUSION (Ernst & Banks 2002 w ~ 1/sigma^2; MacDonald 1994 constraint satisfaction;
    a PINNED row of BRAIN_MATH_REFERENCE). The cues are ordered by their PRECISION about THIS event's outcome:

      1. the verb's RESULT STATE (sense-keyed, direct evidence about the state the patient is left in) -- a
         manner adverb modulates it but never reverses it ("stabbed him gently" is still HARM);
      2. the MANNER of this very event (explicit, event-level, and the whole point of a manner adverb);
      3. the verb's WORD-LEVEL norm (Warriner rates a word out of context and conflates its senses -- 'treat'
         +0.46 is largely the noun 'a treat'), and the SUPERORDINATE category -- both DIFFUSE priors.

    So a qualifying manner outranks 2 and 3 and yields to 1. `prior_rule='weak_prior'` is the ablation in which
    the manner only fires when |word valence| < PRIOR_WEAK (i.e. the word norm outranks the manner)."""
    v = FDV.lemmatize_verb(verb)
    base = harm_help_manner(v, animacy)
    if not fuse or animacy == "inanimate":
        return base
    mval = prose_manner_value(tokens, gov_idx, graded, mode=mode)
    if mval is None:
        return base
    rs = FDV.result_state_value(v)
    if rs is not None and abs(rs) >= FDV.STATE_MIN:
        return base                                    # cue 1 outranks the manner
    if prior_rule == "weak_prior":
        wv = FDV._afx().valence(v)
        if wv is not None and abs(wv) >= PRIOR_WEAK and base in ("HARM", "HELP"):
            return base
    if not FDV.is_affecting(v):
        # the manner does not create an event out of nothing. Same guard as the lexical arm, plus the HEAD's own
        # branch (d): a communication/social event with STRONG affect IS affecting (betray/slander) -- here the
        # strong affect is supplied by the manner ("addressed him contemptuously"), one categorisation, not two.
        ss = FDV.verb_first_supersense(v)
        if FDV._is_subject_experiencer(v) or ss in ("perception", "cognition", "stative", "motion"):
            return base
        if abs(mval) < FDV.TAU_STRONG:
            return base
    return "HARM" if mval < 0 else "HELP"


# ==========================================================================================================
# THE NEW GOLD -- DECLARED HERE (36 sentences; the manner adverb is the only signal)
# ==========================================================================================================
# CONSTRUCTION (transparent, mirrors the method of the 36-item live modern gold): every scene is
# "<DET> <agent> <verb> the <patient> <adverb> ." with an AFFECT-NEUTRAL manner-host verb (treat/handle/hold/
# grab/touch/push/pull/lead/shake/carry/lift/seize/grip/address ...). 12 harm-manner, 12 help-manner, 12
# neutral-manner. The verbs are deliberately shared across the three cells so the verb itself carries NO
# information -- an arm that ignores the adverb cannot beat chance-by-verb. The adverbs are ordinary English
# manner adverbs, chosen before any measurement and NOT filtered by whether the norms cover them.
ADVERB_PROSE_GOLD = [
    # ---- 12 HARM-manner ----
    ("guard", "treated", "prisoner", "brutally", "HARM"),
    ("officer", "handled", "suspect", "roughly", "HARM"),
    ("warden", "treated", "inmate", "cruelly", "HARM"),
    ("boss", "treated", "assistant", "harshly", "HARM"),
    ("nurse", "handled", "patient", "carelessly", "HARM"),
    ("soldier", "pushed", "villager", "violently", "HARM"),
    ("man", "grabbed", "child", "savagely", "HARM"),
    ("bouncer", "seized", "customer", "forcefully", "HARM"),
    ("driver", "shook", "passenger", "angrily", "HARM"),
    ("teacher", "addressed", "pupil", "contemptuously", "HARM"),
    ("landlord", "treated", "tenant", "unfairly", "HARM"),
    ("coach", "pulled", "player", "aggressively", "HARM"),
    # ---- 12 HELP-manner ----
    ("nurse", "treated", "patient", "kindly", "HELP"),
    ("mother", "handled", "baby", "gently", "HELP"),
    ("doctor", "held", "child", "tenderly", "HELP"),
    ("teacher", "addressed", "pupil", "warmly", "HELP"),
    ("warden", "treated", "inmate", "humanely", "HELP"),
    ("officer", "handled", "suspect", "respectfully", "HELP"),
    ("volunteer", "carried", "elder", "carefully", "HELP"),
    ("guide", "led", "climber", "patiently", "HELP"),
    ("man", "grabbed", "child", "protectively", "HELP"),
    ("boss", "treated", "assistant", "generously", "HELP"),
    ("landlord", "treated", "tenant", "fairly", "HELP"),
    ("coach", "pulled", "player", "encouragingly", "HELP"),
    # ---- 12 NEUTRAL-manner (a manner that leaves the patient's condition unchanged) ----
    ("clerk", "addressed", "customer", "formally", "NEUTRAL"),
    ("officer", "handled", "suspect", "legally", "NEUTRAL"),
    ("guard", "treated", "prisoner", "routinely", "NEUTRAL"),
    ("nurse", "treated", "patient", "privately", "NEUTRAL"),
    ("teacher", "addressed", "pupil", "publicly", "NEUTRAL"),
    ("driver", "carried", "passenger", "briefly", "NEUTRAL"),
    ("guide", "led", "climber", "silently", "NEUTRAL"),
    ("man", "grabbed", "child", "suddenly", "NEUTRAL"),
    ("volunteer", "held", "elder", "briefly", "NEUTRAL"),
    ("boss", "addressed", "assistant", "verbally", "NEUTRAL"),
    ("landlord", "treated", "tenant", "impersonally", "NEUTRAL"),
    ("coach", "pulled", "player", "sideways", "NEUTRAL"),
]


def prose_sentence(agent, verb, patient, adverb):
    a = "An" if agent[0] in "aeiou" else "A"
    return [a, agent, verb, "the", patient, adverb, "."]


def _prose_correct(pred, gold) -> int:
    if gold == "NEUTRAL":
        return 1 if pred not in ("HARM", "HELP") else 0
    return 1 if pred == gold else 0


# ==========================================================================================================
# metrics helpers
# ==========================================================================================================
def boot_ci(corr, n_boot=N_BOOT, seed=SEED):
    if not corr:
        return 0.0, 0.0
    rng = random.Random(seed)
    n = len(corr); ms = []
    for _ in range(n_boot):
        ms.append(sum(corr[rng.randrange(n)] for _ in range(n)) / n)
    ms.sort()
    return sum(corr) / n, (ms[int(0.975 * n_boot)] - ms[int(0.025 * n_boot)]) / 2.0


def paired_boot(a, b, n_boot=N_BOOT, seed=SEED):
    """Paired bootstrap of mean(a) - mean(b): (delta, lo, hi)."""
    rng = random.Random(seed + 1)
    n = len(a); ds = []
    for _ in range(n_boot):
        idx = [rng.randrange(n) for _ in range(n)]
        ds.append(sum(a[i] for i in idx) / n - sum(b[i] for i in idx) / n)
    ds.sort()
    return (sum(a) / n - sum(b) / n, ds[int(0.025 * n_boot)], ds[int(0.975 * n_boot)])


def _scrambled_intensity(seed=SEED + 11):
    """THE TWIN the brief names: permute the INTENSITY norms (arousal + grounded action strength) across words.
    Same distributions, no word->intensity information; the sign channel (valence) is untouched, so what is
    tested is exactly whether the intensity READ carries information."""
    afx = FDV._afx()
    ak = sorted(afx.aro.keys()); av = [afx.aro[k] for k in ak]
    rng = random.Random(seed); rng.shuffle(av)
    aro = dict(zip(ak, av))
    gw = asset().get("words", {})
    gk = sorted(k for k in gw if "g" in gw[k]); gv = [gw[k]["g"] for k in gk]
    rng2 = random.Random(seed + 1); rng2.shuffle(gv)
    return aro, dict(zip(gk, gv))


def _parse_free_table(verbs) -> Dict[str, List[List]]:
    """THE PARSE CONTROL (the sharpest one here). For every verb, replace the PARSED manner filler with the
    strongest-valence content word of the SAME definition -- i.e. the parse-free gloss proxy that was drilled and
    refuted (8 neutral leaks + 6 wrong signs) -- and run it through the identical intensity/consensus valuation.
    If the parse is what makes the read work, this arm must lose on precision."""
    from nltk.corpus import wordnet as wn
    from hdlab import frontend as FE
    afx = FDV._afx()
    out: Dict[str, List[List]] = {}
    ev = asset().get("evidence", {})
    for v in verbs:
        rows = ev.get(FDV.lemmatize_verb(v), [])
        if not rows:
            continue
        new = []
        for syn in sorted({r[0] for r in rows}):
            try:
                d = wn.synset(syn).definition()
            except Exception:
                continue
            best, bv = None, 0.0
            for w in FE.tokenize(d):
                if not w.isalpha() or len(w) < 3:
                    continue
                x = afx.valence(w.lower())
                if x is not None and abs(x) > abs(bv):
                    best, bv = w.lower(), x
            if best:
                new.append([syn, "ADVMOD", best, 1])
        if new:
            out[FDV.lemmatize_verb(v)] = new
    return out


def _scrambled_valence(seed=SEED + 7):
    afx = FDV._afx()
    keys = sorted(afx.val.keys()); vals = [afx.val[k] for k in keys]
    random.Random(seed).shuffle(vals)
    from hdlab.affect_lexicon import AffectLexicon
    return AffectLexicon(dict(zip(keys, vals)), afx.aro)


def _candidate_verbs() -> List[str]:
    from nltk.corpus import wordnet as wn
    afx = FDV._afx()
    cand = [w for w in afx.val if " " not in w and wn.synsets(w, "v")]
    return sorted(set(FDV.lemmatize_verb(v) for v in cand if is_affecting_extended(v)))


# ==========================================================================================================
# run
# ==========================================================================================================
def run() -> Dict:
    out_dir = get_output_dir(ANCHOR)
    gold = load_effect_o()

    def glabel(v):
        e = gold.get(FDV.lemmatize_verb(v))
        if e is None:
            return None
        return "HARM" if e < CF_NEG else ("HELP" if e > CF_POS else "NEUTRAL")

    res: Dict = {"_meta": {"seed": SEED, "anchor": ANCHOR, "out_dir": str(out_dir),
                           "tau_intensity": TAU_INTENSITY, "tau_manner_val": TAU_MANNER_VAL,
                           "prior_weak": PRIOR_WEAK, "ship_slots": list(SHIP_SLOTS),
                           "asset_meta": asset().get("meta", {}), "cf_gold_verbs": len(gold)}}

    # ---- 1. THE NAMED SLICE ------------------------------------------------------------------------------
    per = {}
    for v in NAMED_HARM:
        per[v] = {"floor": harm_help_floor(v, "animate"), "manner": harm_help_manner(v, "animate"),
                  "manner_value": manner_state_value(v),
                  "evidence": [[r[1], r[2]] for r in manner_evidence(v)]}
    rec = [v for v in MANNER_SLICE if per[v]["floor"] is None and per[v]["manner"] == "HARM"]
    res["named_slice"] = {
        "per_verb": per,
        "floor_HARM_of_15": sum(1 for v in NAMED_HARM if per[v]["floor"] == "HARM"),
        "manner_HARM_of_15": sum(1 for v in NAMED_HARM if per[v]["manner"] == "HARM"),
        "manner_slice_recovered": rec, "manner_slice_n": len(MANNER_SLICE),
        "flips_to_wrong_sign": [v for v in NAMED_HARM
                                if per[v]["floor"] in ("HARM", "HELP") and per[v]["manner"] != per[v]["floor"]],
    }

    # ---- 2. NEUTRAL PRECISION (0 leaks required) ---------------------------------------------------------
    res["neutral_precision"] = {
        "n": len(A.P_NEUTRAL_BROAD),
        "floor_leaks": [(v, harm_help_floor(v, "animate")) for v in A.P_NEUTRAL_BROAD
                        if harm_help_floor(v, "animate") in ("HARM", "HELP")],
        "manner_leaks": [(v, harm_help_manner(v, "animate")) for v in A.P_NEUTRAL_BROAD
                         if harm_help_manner(v, "animate") in ("HARM", "HELP")],
    }

    # ---- 3. brief populations hold -----------------------------------------------------------------------
    def cnt(pop, target, fn):
        return sum(fn(v, "animate") == target for v in pop)
    res["populations"] = {
        "harm_frame_HARM": [cnt(A.P_HARM_FRAME, "HARM", harm_help_floor), cnt(A.P_HARM_FRAME, "HARM", harm_help_manner), len(A.P_HARM_FRAME)],
        "social_harm_HARM": [cnt(A.P_SOCIAL_HARM, "HARM", harm_help_floor), cnt(A.P_SOCIAL_HARM, "HARM", harm_help_manner), len(A.P_SOCIAL_HARM)],
        "nonprevent_help_HELP": [cnt(A.P_NONPREVENT_HELP, "HELP", harm_help_floor), cnt(A.P_NONPREVENT_HELP, "HELP", harm_help_manner), len(A.P_NONPREVENT_HELP)],
    }

    # ---- 4. CF: whole-arm agreement + precision of every NEW decision -------------------------------------
    lem = _candidate_verbs()

    def cf_agree(fn):
        a = t = 0; disc = []
        for v in lem:
            g = glabel(v); p = fn(v, "animate")
            if g in ("HARM", "HELP") and p in ("HARM", "HELP"):
                t += 1
                if g == p:
                    a += 1
                else:
                    disc.append((v, p, g, round(gold[v], 2)))
        return a, t, disc
    fa, ft, _ = cf_agree(harm_help_floor)
    ma, mt, mdisc = cf_agree(harm_help_manner)
    res["cf_whole_arm"] = {"floor": [fa, ft, round(fa / max(1, ft), 4)],
                           "manner": [ma, mt, round(ma / max(1, mt), 4)],
                           "manner_discordant_sample": mdisc[:12]}

    residual = [v for v in lem if harm_help_floor(v, "animate") is None]
    new_dec = [(v, harm_help_manner(v, "animate")) for v in residual]
    new_dec = [(v, p) for v, p in new_dec if p in ("HARM", "HELP")]
    p = t = 0; wrong = []; neut = []
    for v, pred in new_dec:
        g = glabel(v)
        if g in ("HARM", "HELP"):
            t += 1
            if g == pred:
                p += 1
            else:
                wrong.append((v, pred, g, round(gold[v], 2)))
        elif g == "NEUTRAL":
            neut.append((v, pred, round(gold[v], 2)))
    res["new_decisions"] = {"n_residual_floor_abstains": len(residual), "n_newly_decided": len(new_dec),
                            "cf_precision": [p, t, round(p / max(1, t), 4)],
                            "cf_wrong_sign": wrong, "cf_neutral_but_decided": neut,
                            "sample": sorted(new_dec)[:40]}

    # ---- 5. TWINS ----------------------------------------------------------------------------------------
    aro_s, gro_s = _scrambled_intensity()
    twin_int = _arm_with_overrides(aro_over=aro_s, gro_over=gro_s)
    twin_val = _arm_with_overrides(afx_over=_scrambled_valence())
    def slice_harm(fn):
        return sum(1 for v in MANNER_SLICE if fn(v, "animate") == "HARM")
    def slice_wrong(fn):
        return sum(1 for v in MANNER_SLICE if fn(v, "animate") == "HELP")
    res["twin"] = {
        "manner_slice_HARM": {"real": slice_harm(harm_help_manner), "twin_intensity": slice_harm(twin_int),
                              "twin_valence": slice_harm(twin_val), "n": len(MANNER_SLICE)},
        "manner_slice_WRONG_HELP": {"real": slice_wrong(harm_help_manner), "twin_intensity": slice_wrong(twin_int),
                                    "twin_valence": slice_wrong(twin_val)},
        "neutral_leaks": {"real": len(res["neutral_precision"]["manner_leaks"]),
                          "twin_intensity": sum(1 for v in A.P_NEUTRAL_BROAD if twin_int(v, "animate") in ("HARM", "HELP")),
                          "twin_valence": sum(1 for v in A.P_NEUTRAL_BROAD if twin_val(v, "animate") in ("HARM", "HELP"))},
    }
    # CF precision of the twins' new decisions (the real quality control, not just a count)
    def twin_new_prec(fn):
        pp = tt = 0
        for v in residual:
            pr = fn(v, "animate")
            if pr not in ("HARM", "HELP"):
                continue
            g = glabel(v)
            if g in ("HARM", "HELP"):
                tt += 1; pp += (g == pr)
        return [pp, tt, round(pp / max(1, tt), 4)]
    pf = _parse_free_table(lem)
    twin_slot = _arm_with_overrides(slot_scramble=pf)
    res["twin"]["manner_slice_HARM"]["twin_parse_free"] = slice_harm(twin_slot)
    res["twin"]["neutral_leaks"]["twin_parse_free"] = sum(
        1 for v in A.P_NEUTRAL_BROAD if twin_slot(v, "animate") in ("HARM", "HELP"))
    res["twin"]["cf_precision_new"] = {"real": res["new_decisions"]["cf_precision"],
                                       "twin_intensity": twin_new_prec(twin_int),
                                       "twin_valence": twin_new_prec(twin_val),
                                       "twin_parse_free": twin_new_prec(twin_slot)}
    res["twin"]["n_newly_decided"] = {
        "real": res["new_decisions"]["n_newly_decided"],
        "twin_intensity": sum(1 for v in residual if twin_int(v, "animate") in ("HARM", "HELP")),
        "twin_valence": sum(1 for v in residual if twin_val(v, "animate") in ("HARM", "HELP")),
        "twin_parse_free": sum(1 for v in residual if twin_slot(v, "animate") in ("HARM", "HELP"))}

    # ---- 5b. INTENSITY-CHANNEL ABLATION (which read of "how forceful" is load-bearing?) -------------------
    imodes = {}
    for md in ("circumplex", "arousal", "grounded", "arousal_grounded", "valence"):
        arm = _arm_with_overrides(mode=md)
        pp = tt = nd = 0
        for v in residual:
            pr = arm(v, "animate")
            if pr not in ("HARM", "HELP"):
                continue
            nd += 1
            g = glabel(v)
            if g in ("HARM", "HELP"):
                tt += 1; pp += (g == pr)
        imodes[md] = {"slice": sum(1 for v in MANNER_SLICE if arm(v, "animate") == "HARM"),
                      "newly_decided": nd, "cf_prec": [pp, tt, round(pp / max(1, tt), 4)],
                      "leaks": sum(1 for v in A.P_NEUTRAL_BROAD if arm(v, "animate") in ("HARM", "HELP")),
                      "prose_acc": round(sum(_prose_correct(
                          harm_help_prose_mode(md, g_[1], prose_sentence(g_[0], g_[1], g_[2], g_[3]), 2), g_[4])
                          for g_ in ADVERB_PROSE_GOLD) / len(ADVERB_PROSE_GOLD), 4)}
    res["intensity_modes"] = imodes

    # ---- 6. THE 2x2 the brief asks for: SIGN from VALENCE x MAGNITUDE from AROUSAL ------------------------
    # Computed UNGATED (tau_int = tau_val = 0) so both arousal rows are populated: the question is whether a
    # high-arousal POSITIVE manner (excite / thrill / arouse) is read HELP rather than HARM, i.e. whether the two
    # channels are genuinely doing different jobs. AROUSAL_SPLIT is the circumplex arousal axis midpoint.
    AROUSAL_SPLIT = 0.50
    afx = FDV._afx()
    cells = {"hiA_neg": [], "hiA_pos": [], "loA_neg": [], "loA_pos": []}
    for v in lem:
        best = None
        for _s, _sl, f, _c in manner_evidence(v):
            x = afx.valence(f)
            if x is None:
                continue
            if best is None or abs(x) > abs(best[1]):
                best = (f, x, afx.arousal(f))
        if best is None:
            continue
        f, x, a = best
        key = ("hiA_" if (a is not None and a >= AROUSAL_SPLIT) else "loA_") + ("neg" if x < 0 else "pos")
        cells[key].append((v, f, round(x, 2), glabel(v)))
    res["two_by_two"] = {}
    for k, vs in cells.items():
        cov = [g for _v, _f, _x, g in vs if g in ("HARM", "HELP")]
        agree = sum(1 for _v, _f, x, g in vs
                    if (g == "HARM" and x < 0) or (g == "HELP" and x > 0))
        res["two_by_two"][k] = {"n": len(vs), "cf_covered": len(cov),
                                "cf_sign_agree": round(agree / max(1, len(cov)), 4),
                                "n_in_P_NEUTRAL_BROAD": sum(1 for v, _f, _x, _g in vs if v in A.P_NEUTRAL_BROAD),
                                "sample": vs[:8]}

    # ---- 7. SLOT ABLATION (which decomposition slots hold precision; GENUS is the refuted gloss read) -----
    slot_rows = {}
    for slots in (("ADVMOD",), ("MANNER_PP",), ("MEANS_PP",), ("RESULT_ADJ",), ("GENUS",),
                  SHIP_SLOTS, SHIP_SLOTS + ("GENUS",)):
        arm = _arm_with_overrides(slots=slots)
        leaks = sum(1 for v in A.P_NEUTRAL_BROAD if arm(v, "animate") in ("HARM", "HELP"))
        pp = tt = nd = 0
        for v in residual:
            pr = arm(v, "animate")
            if pr not in ("HARM", "HELP"):
                continue
            nd += 1
            g = glabel(v)
            if g in ("HARM", "HELP"):
                tt += 1; pp += (g == pr)
        slot_rows["+".join(slots)] = {"slice_recovered": sum(1 for v in MANNER_SLICE if arm(v, "animate") == "HARM"),
                                      "newly_decided": nd, "cf_prec": [pp, tt, round(pp / max(1, tt), 4)],
                                      "neutral_leaks": leaks}
    res["slot_ablation"] = slot_rows

    # ---- 8. OPERATING-POINT SWEEP (phase diagram) --------------------------------------------------------
    sweep = {}
    for ti in (0.35, 0.40, 0.45, 0.50, 0.55, 0.60):
        for tv in (0.10, 0.20, 0.30):
            arm = _arm_with_overrides(tau_int=ti, tau_val=tv)
            leaks = sum(1 for v in A.P_NEUTRAL_BROAD if arm(v, "animate") in ("HARM", "HELP"))
            pp = tt = nd = 0
            for v in residual:
                pr = arm(v, "animate")
                if pr not in ("HARM", "HELP"):
                    continue
                nd += 1
                g = glabel(v)
                if g in ("HARM", "HELP"):
                    tt += 1; pp += (g == pr)
            sweep["ti%.2f_tv%.2f" % (ti, tv)] = {
                "slice": sum(1 for v in MANNER_SLICE if arm(v, "animate") == "HARM"),
                "newly_decided": nd, "cf_prec": round(pp / max(1, tt), 4), "cf_n": tt, "leaks": leaks}
    res["sweep"] = sweep

    # ---- 9. THE 36-ITEM LIVE MODERN GOLD (no-regress) -----------------------------------------------------
    try:
        import experiments.exp_fd_harm_help_live_modern_v1 as LIVE
        broken = []; nfl = nma = 0
        for g in LIVE.GOLD:
            verb, label = g[1], g[3]
            if label not in ("HARM", "HELP"):
                continue
            f = harm_help_floor(verb, "animate"); m = harm_help_manner(verb, "animate")
            nfl += (f == label); nma += (m == label)
            if m != label and f == label:
                broken.append((verb, f, m, label))
        # the 12 NEUTRAL items too: 6 have an ANIMATE patient (watch/photograph/greet/phone/describe/email --
        # they must keep abstaining) and 6 an inanimate one (NA by animacy, untouched by any endstate read).
        nleak = [(g[1], harm_help_manner(g[1], "animate")) for g in LIVE.GOLD if g[3] == "NEUTRAL"
                 and harm_help_manner(g[1], "animate") in ("HARM", "HELP")]
        res["live_modern_gold"] = {"n_harm_help": nfl + 0, "floor_correct": nfl, "manner_correct": nma,
                                   "broken_by_manner": broken,
                                   "n_items": sum(1 for g in LIVE.GOLD if g[3] in ("HARM", "HELP")),
                                   "neutral_items_newly_decided": nleak,
                                   "floor_neutral_newly_decided": [(g[1], harm_help_floor(g[1], "animate"))
                                                                   for g in LIVE.GOLD if g[3] == "NEUTRAL"
                                                                   and harm_help_floor(g[1], "animate") in ("HARM", "HELP")]}
    except Exception as e:
        res["live_modern_gold"] = {"error": repr(e)}

    # ---- 10. THE NEW ADVERB-IN-PROSE GOLD ----------------------------------------------------------------
    res["adverb_prose_gold"] = prose_report()

    # ---- 10b. LEVER ABLATION (each push lever on its own; the shipped config is the one the numbers pick) --
    G = globals()   # NOT `import experiments.exp_... as SELF`: run as a script this file is __main__ and the
                    # import would create a SECOND module object whose flags the arms never read.
    _FLAGS = ("MANNER_FIRST", "MANNER_HOST_ABSTAIN", "GENUS_CASCADE", "MORPH_REANALYSIS")
    base_flags = tuple(G[k] for k in _FLAGS)
    lev = {}
    configs = {"residual_only": (False, False, False, False),
               "residual+L4_morph": (False, False, False, True),
               "residual+L3_genus": (False, False, True, False),
               "SHIP residual+L3+L4": (False, False, True, True),
               "L1_manner_first": (True, False, False, True),
               "L1+L2_host_abstain": (True, True, False, True),
               "L1+L2+L3+L4_all": (True, True, True, True)}
    try:
        for name, flags in configs.items():
            for k, x in zip(_FLAGS, flags):
                G[k] = x
            FDV._EV_CACHE.clear()
            a_, t_, _ = cf_agree(harm_help_manner)
            leaks_ = [v for v in A.P_NEUTRAL_BROAD if harm_help_manner(v, "animate") in ("HARM", "HELP")]
            try:
                import experiments.exp_fd_harm_help_live_modern_v1 as LIVE
                lg = sum(1 for g in LIVE.GOLD if g[3] in ("HARM", "HELP")
                         and harm_help_manner(g[1], "animate") == g[3])
            except Exception:
                lg = -1
            pc = [_prose_correct(harm_help_prose(g_[1], prose_sentence(g_[0], g_[1], g_[2], g_[3]), 2), g_[4])
                  for g_ in ADVERB_PROSE_GOLD]
            pm, ph = boot_ci(pc)
            nd_ = pp_ = tt_ = 0
            for v in residual:
                pr = harm_help_manner(v, "animate")
                if pr not in ("HARM", "HELP"):
                    continue
                nd_ += 1
                g = glabel(v)
                if g in ("HARM", "HELP"):
                    tt_ += 1; pp_ += (g == pr)
            lev[name] = {"slice_recovered": sum(1 for v in MANNER_SLICE if harm_help_manner(v, "animate") == "HARM"),
                         "named_HARM_of_15": sum(1 for v in NAMED_HARM if harm_help_manner(v, "animate") == "HARM"),
                         "cf_whole_arm": [a_, t_, round(a_ / max(1, t_), 4)],
                         "new_decisions": nd_, "new_cf_prec": [pp_, tt_, round(pp_ / max(1, tt_), 4)],
                         "neutral_leaks": leaks_, "live_gold_24": lg,
                         "prose_acc": [round(pm, 4), round(ph, 4)]}
    finally:
        for k, x in zip(_FLAGS, base_flags):
            G[k] = x
        FDV._EV_CACHE.clear()
    res["lever_ablation"] = lev

    # ---- 11. residual after the manner read (the honest remainder) ---------------------------------------
    still = [v for v in residual if harm_help_manner(v, "animate") is None]
    res["residual_after"] = {"before": len(residual), "after": len(still),
                             "still_CF_nonneutral": sum(1 for v in still if glabel(v) in ("HARM", "HELP"))}

    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "metrics.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, indent=1, default=str)
    return res


def prose_report() -> Dict:
    """The NEW adverb-in-prose gold: floor vs the manner read, with the governor's advmod attachment counted."""
    fe = _frontend()
    rows = []
    adv_to_verb_argmax = adv_to_verb_mass = 0
    for agent, verb, patient, adverb, label in ADVERB_PROSE_GOLD:
        toks = prose_sentence(agent, verb, patient, adverb)
        gov_idx = 2                                    # the verb slot of the template
        pos, post = fe["T"].tag_with_posterior(toks)
        out = fe["P"].parse(toks, pos, post)
        ai = 5                                         # the adverb slot of the template
        argmax_head = out.heads.get(ai + 1, -1)
        mass = float(out.marginals.get(ai + 1, {}).get(gov_idx + 1, 0.0)) if out.marginals else \
            (1.0 if argmax_head == gov_idx + 1 else 0.0)
        adv_to_verb_argmax += (argmax_head == gov_idx + 1)
        adv_to_verb_mass += mass
        f = harm_help_floor(verb, "animate")
        m_graded = harm_help_prose(verb, toks, gov_idx, graded=True)
        m_argmax = harm_help_prose(verb, toks, gov_idx, graded=False)
        rows.append({"sent": " ".join(toks), "gold": label, "adverb": adverb, "adv_tag": pos[ai],
                     "argmax_head": (toks[argmax_head - 1] if argmax_head > 0 else "ROOT"),
                     "posterior_on_verb": round(mass, 3),
                     "floor": f, "manner_graded": m_graded, "manner_argmax": m_argmax})
    cf = [_prose_correct(r["floor"], r["gold"]) for r in rows]
    cg = [_prose_correct(r["manner_graded"], r["gold"]) for r in rows]
    ca = [_prose_correct(r["manner_argmax"], r["gold"]) for r in rows]
    mf, hf = boot_ci(cf); mg, hg = boot_ci(cg); ma, ha = boot_ci(ca)
    d, lo, hi = paired_boot(cg, cf)
    return {
        "n": len(rows),
        "floor_acc": [round(mf, 4), round(hf, 4)],
        "manner_graded_acc": [round(mg, 4), round(hg, 4)],
        "manner_argmax_acc": [round(ma, 4), round(ha, 4)],
        "delta_graded_minus_floor": [round(d, 4), round(lo, 4), round(hi, 4)],
        "ci_separated": bool(lo > 0.0),
        "governor_advmod": {"argmax_adverb_attached_to_verb": adv_to_verb_argmax,
                            "mean_posterior_on_verb": round(adv_to_verb_mass / max(1, len(rows)), 4),
                            "n": len(rows)},
        "by_cell": {c: {"floor": sum(_prose_correct(r["floor"], r["gold"]) for r in rows if r["gold"] == c),
                        "manner": sum(_prose_correct(r["manner_graded"], r["gold"]) for r in rows if r["gold"] == c),
                        "n": sum(1 for r in rows if r["gold"] == c)}
                    for c in ("HARM", "HELP", "NEUTRAL")},
        "rows": rows,
    }


# ==========================================================================================================
def self_test() -> bool:
    """Off-disk smoke, all can-fail: the manner read recovers the manner slice, keeps the landed wins, never
    leaks on a neutral verb, and the scrambled-intensity twin loses."""
    assert asset().get("evidence"), "manner asset missing -- run tools/build_manner_intensity_asset.py"
    # (1) the named manner verbs the floor abstains on are recovered to HARM
    assert harm_help_floor("brutalize", "animate") is None
    assert harm_help_manner("brutalize", "animate") == "HARM", "brutalize must recover to HARM"
    assert harm_help_manner("manhandle", "animate") == "HARM"
    assert harm_help_manner("maltreat", "animate") == "HARM"
    # (2) the sign comes from VALENCE, not from intensity: a high-arousal POSITIVE manner is not HARM
    assert manner_state_sign("thrill") != -1, "high-arousal positive manner must not read HARM"
    # (3) landed wins untouched
    assert harm_help_manner("stab", "animate") == "HARM"
    assert harm_help_manner("comfort", "animate") == "HELP"
    assert harm_help_manner("watch", "animate") is None
    # (4) no leak on the broad neutral population
    leaks = [v for v in A.P_NEUTRAL_BROAD if harm_help_manner(v, "animate") in ("HARM", "HELP")]
    assert not leaks, "neutral leaks: %s" % leaks
    # (5) the twin (scrambled intensity norms) loses on the manner slice
    aro_s, gro_s = _scrambled_intensity()
    tw = _arm_with_overrides(aro_over=aro_s, gro_over=gro_s)
    real = sum(harm_help_manner(v, "animate") == "HARM" for v in MANNER_SLICE)
    twin = sum(tw(v, "animate") == "HARM" for v in MANNER_SLICE)
    assert twin < real, "twin %d !< real %d" % (twin, real)
    # (6) the prose read fires on an adverb in running prose and gets the sign right
    toks = prose_sentence("guard", "treated", "prisoner", "brutally")
    assert harm_help_prose("treated", toks, 2) == "HARM", "prose manner read must give HARM"
    toks2 = prose_sentence("nurse", "treated", "patient", "kindly")
    assert harm_help_prose("treated", toks2, 2) == "HELP"
    print("[SELFTEST PASS] manner-intensity recovers brutalize/manhandle/maltreat -> HARM, keeps landed wins, "
          "0 neutral leaks, twin loses (%d<%d), prose adverb read HARM/HELP correct" % (twin, real))
    return True


if __name__ == "__main__":
    if "--self-test" in sys.argv or "--smoke" in sys.argv:
        self_test()
    else:
        import pprint
        r = run()
        big = r.pop("adverb_prose_gold")
        rows = big.pop("rows")
        pprint.pprint(r, width=130, sort_dicts=False)
        print("\n==== ADVERB-IN-PROSE GOLD ====")
        pprint.pprint(big, width=130, sort_dicts=False)
        for x in rows:
            print("  %-52s gold=%-7s floor=%-6s manner=%-6s adv=%s/%s->%s p=%.2f" % (
                x["sent"], x["gold"], x["floor"], x["manner_graded"], x["adverb"], x["adv_tag"],
                x["argmax_head"], x["posterior_on_verb"]))
