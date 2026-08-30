"""Glass-box PATIENT-TENDENCY estimator for the Wolff force-dynamic CAUSE/ENABLE/PREVENT typer.

PROBLEM: `causation_typing_needs_a_patient_tendency_estimator`. The landed Wolff typer
(`hdlab/force_dynamics_typer.py`) reads CAUSE/ENABLE/PREVENT from the VERB's force class. For
TENDENCY-AMBIGUOUS verbs (open/move/turn/roll/...) the class is NOT in the verb: "the key opened the
gate" (patient tended -> ENABLE) vs "the wind opened the gate" (patient resisted, overcome -> CAUSE),
same verb, opposite type. Wolff's truth-table needs a third input the verb cannot carry: does the
PATIENT tend toward the outcome on its own?

BRAIN MECHANISM (PINNED -- Wolff 2007 "force theory of causation"; Wolff & Song 2003 Cog.Psych.
47:276-332; Talmy 1988). Causal type is read off FORCE VECTORS. The patient has an intrinsic tendency
force toward-or-away-from the endstate; the affector supplies a force; the type follows from
(patient-tendency sign, affector-patient concordance, endstate-reached). The patient-tendency vector's
inputs come from "perception/knowledge" (Wolff & Song), and the CAUSE-vs-ENABLE distinction is partly
LINGUISTICALLY CONSTRUCTED (Kuhnmuench & Beller 2005). We recover the SIGN of the patient's tendency
force from three sources, combined as a signed FORCE SUM (Wolff's forces add as vectors):

  (1) AFFECTOR MAGNITUDE  [PROVEN first term -- exp_causal_tendency_recovery_v1]. Given the endstate is
      reached: a WEAK affector (a nudge/breeze) that still succeeds => the patient's own force made up
      the difference => patient TENDED => +1. A STRONG affector (a winch/heave) => it OVERCAME the
      patient => patient RESISTED => -1. An ABDUCTIVE term, valid only when the endstate is reached.
  (2) PATIENT AFFORDANCE  [built here]. The patient's intrinsic physical disposition toward the outcome
      motion: round/wheeled things afford rolling, buoyant things afford rising, hinged things afford
      swinging (+1); heavy/anchored/structural things resist (-1). Read from a glass-box CORE-PHYSICS
      property lexicon (Spelke/Baillargeon core physical knowledge; Gibson affordances are
      action-specific). NOT reliably in WordNet's taxonomy (category != disposition -- measured), so
      this is a principled property lexicon, broader than any test item and validated on HELD-OUT
      patients, NOT a gold lookup.
  (3) DIRECTIONAL / GRAVITY / ASPECTUAL cues  [built here]. Environmental forces are Wolff force
      vectors too: "down the slope / downstream / with the current" aligns gravity/flow with the
      outcome (+1); "up the slope / against the current" opposes it (-1). Aspectual self-motion ("on
      its own", "kept rolling") = the patient tending (+1); "would not / jammed / stuck" = resisting
      (-1). Purely linguistic -- no KB.

COMBINATION: T = w_m*m + w_a*a + w_d*d ; sign(T) > 0 => patient TENDS => ENABLE ; < 0 => RESISTS =>
CAUSE ; == 0 => fall back to the verb lexicon (force_dynamic_type). The weights are OUR-INVENTION and
SWEPT (never adopted); the result is reported robust to them. NO external LLM at inference.

ASCII-only. Deterministic.
"""
from __future__ import annotations

import json
import sys
import os
from typing import Dict, List, Optional, Set, Tuple

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments._force_dynamics_lexicon import force_dynamic_type  # noqa: E402


def lemmatize_verb(verb: str) -> str:
    """Verb -> base form so the estimator fires on INFLECTED real text (moved->move, rolled->roll,
    turned->turn, opened->open, raised->raise). The constructed pairs use lemmas already (a no-op there),
    but real narrative is inflected -- WITHOUT this the estimator abstains on 100% of real sentences
    (measured on the McGuffey serve). Uses WordNet morphy (handles irregulars), with a suffix-strip
    fallback. This is the `lookup_does_not_lemmatise` fix, applied at the estimator entry."""
    v = (verb or "").lower().strip()
    if not v:
        return v
    try:
        from nltk.corpus import wordnet as wn
        lem = wn.morphy(v, wn.VERB)
        if lem:
            return lem
    except Exception:
        pass
    for suf in ("ing", "ed", "es", "s"):
        if v.endswith(suf) and len(v) - len(suf) >= 3:
            base = v[:-len(suf)]
            if suf == "ing" and len(base) >= 2 and base[-1] == base[-2]:  # running -> run
                base = base[:-1]
            return base
    return v

# ---------------------------------------------------------------------------
# TERM 1 -- affector magnitude (REUSE the proven first term; do NOT re-derive).
# WEAK/STRONG manner+instrument lexicon of general physical-force vocabulary (broader than any test
# item). Weak affector + endstate reached => patient tended (+1); strong => overcame patient (-1).
# ---------------------------------------------------------------------------
WEAK_FORCE: Set[str] = {
    "nudge", "tap", "touch", "breeze", "gust", "current", "tide", "updraft", "ripple", "whisper",
    "brush", "draft", "waft", "puff", "trickle", "drift", "ease", "coax", "prod", "flick", "nod",
    "eddy", "swell", "lap", "breath", "wind",
}
STRONG_FORCE: Set[str] = {
    "shove", "heave", "wrench", "winch", "crash", "crane", "jack", "piston", "ram", "bulldozer",
    "sledgehammer", "hurl", "blast", "smash", "wrestle", "haul", "yank", "thrust", "slam", "batter",
    "crank", "lever", "hydraulic", "engine", "torrent", "avalanche", "boulder",
}
# TENDENCY-AMBIGUOUS verbs: the CAUSE/ENABLE split needs the tendency cue (not the verb). Rather than a
# hand-list, DERIVE the gate from the linguistic SIGNATURE of patient-tendency -- the CAUSATIVE-INCHOATIVE
# ALTERNATION (Levin 1993): a verb is tendency-ambiguous iff the patient can undergo the change ITSELF (an
# intransitive inchoative form exists: "the gate opened", "the water drained", "the leaf drifted"). We take
# VerbNet's alternating physical MANNER-OF-MOTION class roll-51.3.1 (external, PINNED -- the patient moves
# on its own) PLUS a small core-physics GRAVITY/FLOW set (liquids flow, unsupported objects fall/sink under
# gravity -- the patient tends). We deliberately EXCLUDE break-45.1 (shatter/smash: prototypical CAUSE, the
# patient does NOT tend) and the 382-verb abstract other_cos class -- the alternation is NECESSARY but not
# SUFFICIENT for force-dynamic tendency-ambiguity. Cached to data/; falls back to the hand-seed if VerbNet
# is absent. Class assignment predates any test gold (the parent's escape-the-construction-proof discipline).
_AMBIGUOUS_SEED: Set[str] = {"move", "turn", "roll", "slide", "raise", "lift", "drive", "push", "rock",
                             "open", "spread", "swing", "pull", "draw", "drop"}
# core-physics gravity/flow motions (patient = liquid or unsupported object -> tends under gravity).
_FLOW_GRAVITY_VERBS: Set[str] = {"drain", "pour", "flow", "spill", "leak", "seep", "trickle", "gush",
                                 "sink", "fall", "rise", "slip", "tumble", "topple", "cascade", "stream"}
_AMBIGUOUS_CACHE = os.path.join(_REPO, "data", "patient_tendency_v1", "ambiguous_verbs.json")


def derive_ambiguous_verbs(use_cache: bool = True) -> Set[str]:
    """Derive the tendency-ambiguous verb gate from the causative-inchoative alternation (VerbNet
    roll-51.3.1 manner-of-motion) + a core-physics gravity/flow set, unioned with the hand-seed floor."""
    if use_cache and os.path.exists(_AMBIGUOUS_CACHE):
        try:
            with open(_AMBIGUOUS_CACHE, "r", encoding="utf-8") as f:
                return set(json.load(f)["verbs"])
        except Exception:
            pass
    verbs = set(_AMBIGUOUS_SEED) | set(_FLOW_GRAVITY_VERBS)
    try:
        from nltk.corpus import verbnet as vn
        vc = vn.vnclass("roll-51.3.1")
        for lu in vn.lemmas(vc):
            lem = lu.split("-")[0].split("_")[0].lower()
            if lem.isalpha():
                verbs.add(lem)
    except Exception:
        pass  # VerbNet absent -> seed + flow set only
    try:
        os.makedirs(os.path.dirname(_AMBIGUOUS_CACHE), exist_ok=True)
        with open(_AMBIGUOUS_CACHE, "w", encoding="utf-8") as f:
            json.dump({"verbs": sorted(verbs),
                       "source": "seed + VerbNet roll-51.3.1 (causative-inchoative manner-motion) + flow/gravity"},
                      f, indent=1)
    except Exception:
        pass
    return verbs


AMBIGUOUS_VERBS: Set[str] = derive_ambiguous_verbs()


def affector_magnitude_sign(affector: str, weak: Set[str] = None, strong: Set[str] = None) -> int:
    """+1 (weak affector -> patient tended), -1 (strong -> overcame), 0 (unknown magnitude).
    Abductive: only meaningful when the endstate is reached (caller guarantees)."""
    weak = WEAK_FORCE if weak is None else weak
    strong = STRONG_FORCE if strong is None else strong
    if affector in weak:
        return +1
    if affector in strong:
        return -1
    return 0


# ---------------------------------------------------------------------------
# TERM 2 -- patient affordance (physical disposition), a glass-box CORE-PHYSICS property lexicon.
# Two maps: patient-noun -> physical properties, and property -> which outcome-motions it AFFORDS or
# RESISTS. Affordance is ACTION-SPECIFIC (Gibson): a hinged door affords swinging, not rolling.
# The property->motion PRINCIPLE is physics, not gold; the noun->property table is broader than any
# test set and is validated on held-out patients.
# ---------------------------------------------------------------------------
# properties that CONFER a tendency, with the motions each affords spontaneously under a small force.
AFFORDS: Dict[str, Set[str]] = {
    "rollable":  {"roll", "move", "drive", "spread"},          # round / cylindrical / spherical
    "wheeled":   {"roll", "move", "drive", "pull", "draw"},    # on wheels
    "buoyant":   {"lift", "raise", "rise", "drift", "move", "float"},  # floats in fluid
    "aerial":    {"move", "lift", "raise", "swing", "turn", "drift", "spread", "blow", "rock", "drop"},  # light / catches air
    # REST-STATE HONESTY (Talmy/Wolff): a hinged joint affords bidirectional OSCILLATION (swing/turn/
    # rock) freely, but a directional STATE-CHANGE from a stable rest (open a closed gate) needs an
    # impulse -- it is NOT spontaneously afforded, so "open" is deliberately EXCLUDED. This is why
    # "the wind opened the gate" is not settled by affordance alone (the gate does not tend to open at
    # rest) -- see the key-vs-wind wall note.
    "hinged":    {"swing", "turn", "rock"},                    # pivots on an axis (free oscillation)
    "sliding":   {"slide", "draw", "pull", "move"},            # runs in a groove/track (low friction)
}
# properties that RESIST spontaneous motion (heavy / fixed / structural) -> patient does NOT tend.
RESIST_PROPS: Set[str] = {"heavy", "anchored", "structural", "rigid"}

# patient-noun -> physical properties. Core-physics dispositions; deliberately broad (many nouns never
# used in the test pairs) so held-out patients are classified by the SAME principle, not fitted.
PATIENT_PROPS: Dict[str, Set[str]] = {
    # rollable / round
    "ball": {"rollable"}, "wheel": {"rollable", "wheeled", "hinged"}, "barrel": {"rollable"},
    "drum": {"rollable"}, "hoop": {"rollable"}, "marble": {"rollable"}, "coin": {"rollable"},
    "cylinder": {"rollable"}, "tire": {"rollable", "wheeled"}, "log": {"rollable"}, "pebble": {"rollable"},
    "orb": {"rollable"}, "globe": {"rollable"}, "wagon": {"wheeled"}, "cart": {"wheeled"},
    "carriage": {"wheeled"}, "trolley": {"wheeled"}, "pram": {"wheeled"}, "bicycle": {"wheeled"},
    # buoyant / floats
    "boat": {"buoyant"}, "raft": {"buoyant"}, "canoe": {"buoyant"}, "ship": {"buoyant"},
    "buoy": {"buoyant"}, "cork": {"buoyant", "aerial"}, "float": {"buoyant"}, "barge": {"buoyant"},
    "balloon": {"buoyant", "aerial"}, "dinghy": {"buoyant"}, "vessel": {"buoyant"},
    # aerial / light
    "leaf": {"aerial"}, "kite": {"aerial"}, "feather": {"aerial"}, "paper": {"aerial"},
    "sail": {"aerial"}, "banner": {"aerial"}, "flag": {"aerial"}, "dust": {"aerial"},
    "petal": {"aerial"}, "curtain": {"aerial"}, "veil": {"aerial"}, "ash": {"aerial"},
    # hinged / pivoted
    "door": {"hinged"}, "gate": {"hinged"}, "vane": {"hinged"}, "lever": {"hinged"},
    "flap": {"hinged"}, "shutter": {"hinged"}, "hatch": {"hinged"}, "lid": {"hinged"},
    "valve": {"hinged"}, "arm": {"hinged"}, "hinge": {"hinged"}, "trapdoor": {"hinged"},
    # sliding (in a track)
    "drawer": {"sliding"}, "sash": {"sliding", "structural"}, "bolt": {"sliding"}, "panel": {"sliding"},
    "slide": {"sliding"}, "sled": {"sliding"},
    # heavy / inert
    "crate": {"heavy"}, "boulder": {"rollable", "heavy"}, "rock": {"heavy"}, "safe": {"heavy"},
    "chest": {"heavy"}, "block": {"heavy"}, "anvil": {"heavy"}, "cabinet": {"heavy"},
    "piano": {"heavy"}, "stone": {"heavy"}, "vault": {"heavy"}, "boiler": {"heavy"},
    "load": {"heavy"}, "cargo": {"heavy"}, "slab": {"heavy"}, "trunk": {"heavy"},
    # anchored / structural
    "pillar": {"structural", "anchored"}, "wall": {"structural", "anchored"}, "post": {"anchored"},
    "column": {"structural", "anchored"}, "beam": {"structural"}, "mast": {"anchored"},
    "hull": {"structural", "heavy"}, "axle": {"structural", "anchored"}, "shaft": {"structural"},
    "foundation": {"structural", "anchored"}, "girder": {"structural"}, "pole": {"anchored"},
    "stake": {"anchored"}, "root": {"anchored"}, "frame": {"structural"}, "gatepost": {"anchored"},
}


# In-sentence property ADJECTIVES (read the disposition off the modifier, not only the noun -- the brain
# reads "the HEAVY lid" directly). Core-physics: mass/size -> resist; lightness/roundness/looseness -> afford.
# genuine MASS/SIZE adjectives only (motion-state cues like jammed/stuck belong to the directional term).
PROPERTY_ADJ_RESIST: Set[str] = {
    "heavy", "massive", "huge", "enormous", "giant", "big", "large", "dense", "solid", "thick", "sturdy",
    "bulky", "weighty", "leaden", "ponderous", "hefty",
}
# unambiguous LIGHTNESS/BUOYANCY adjectives only. EXCLUDES round/smooth/loose/slippery -- ambiguous with
# manner particles ("twisted round", "come loose") -- a measured over-fire source; disambiguating them is
# the word-sense (WSD) problem the brain solves in context, not a lexical list.
PROPERTY_ADJ_AFFORD: Set[str] = {
    "light", "lightweight", "tiny", "small", "thin", "buoyant", "floating", "flimsy", "delicate",
    "airy", "feathery",
}


_ADJ_NEG_CUES: Set[str] = {"not", "n't", "no", "never", "hardly", "barely"}


def _adjective_sign(context) -> int:
    """+1/-1/0 from in-sentence property adjectives (read the patient's disposition off its modifier).
    NEGATION-as-simulation (Kaup et al.): a negation cue in the modifier phrase FLIPS the property sign
    ('not very heavy' -> not-resist -> afford)."""
    if not context:
        return 0
    toks = {t.lower().strip(".,;:!?\"'") for t in context}
    s = 0
    if toks & PROPERTY_ADJ_AFFORD:
        s += 1
    if toks & PROPERTY_ADJ_RESIST:
        s -= 1
    if toks & _ADJ_NEG_CUES:      # negated property: flip (not heavy -> affords; not light -> resists)
        s = -s
    return 1 if s > 0 else (-1 if s < 0 else 0)


def _wordnet_props(patient: str) -> Set[str]:
    """Coverage EXTENDER: physical properties from WordNet glosses/hypernyms for patients absent from
    the core lexicon. Measured weak (category != disposition) -- used only as a backstop, and the cell
    reports the WordNet-only score to show a lexical resource alone cannot supply this term."""
    try:
        from nltk.corpus import wordnet as wn
    except Exception:
        return set()
    LAB = {"round": "rollable", "circular": "rollable", "spherical": "rollable", "cylindrical": "rollable",
           "wheel": "wheeled", "float": "buoyant", "buoyant": "buoyant", "raft": "buoyant",
           "boat": "buoyant", "vessel": "buoyant", "light": "aerial", "thin": "aerial", "flat": "aerial",
           "paper": "aerial", "hinge": "hinged", "hinged": "hinged", "pivot": "hinged", "door": "hinged"}
    INE = {"heavy", "massive", "solid", "stone", "concrete", "fixed", "anchored", "support",
           "structural", "structure", "column", "pillar", "wall", "beam", "rigid", "foundation"}
    props: Set[str] = set()
    for s in wn.synsets(patient, pos=wn.NOUN)[:3]:
        toks = set(s.definition().lower().replace(",", "").replace(".", "").split())
        for h in s.hypernyms():
            toks |= set(h.name().split(".")[0].split("_"))
        for t in toks:
            if t in LAB:
                props.add(LAB[t])
        if toks & INE:
            props.add("heavy")
    return props


def patient_affordance_sign(patient: str, verb: str, context=None, use_wordnet: bool = False,
                            props_map: Dict[str, Set[str]] = None) -> int:
    """+1 (patient physically affords this outcome motion -> tends), -1 (resists), 0 (unknown/neutral).
    Action-specific: a property contributes +1 only if the outcome verb is in what it affords. ALSO reads
    in-sentence property ADJECTIVES from `context` ("the HEAVY lid" -> resists) -- the disposition off the
    modifier, not only the noun."""
    props_map = PATIENT_PROPS if props_map is None else props_map
    verb = lemmatize_verb(verb)            # fire on inflected real text (turned->turn)
    props = set(props_map.get(patient, set()))
    if not props and use_wordnet:
        props = _wordnet_props(patient)
    noun_sign = 0
    if props:
        tends = any(verb in AFFORDS.get(p, set()) for p in props)
        resists = bool(props & RESIST_PROPS)
        noun_sign = (1 if tends else 0) - (1 if resists else 0)
    adj_sign = _adjective_sign(context)
    total = noun_sign + adj_sign
    return 1 if total > 0 else (-1 if total < 0 else 0)


# ---------------------------------------------------------------------------
# TERM 3 -- directional / gravity / aspectual cues (purely linguistic; Wolff environmental forces).
# ---------------------------------------------------------------------------
# SELF-CONTAINED directions (unambiguous gravity path -- fire on their own).
DOWN_CUES: Set[str] = {"downhill", "downward", "downwards", "downstream", "downslope", "downgrade"}
UP_CUES: Set[str] = {"uphill", "upward", "upwards", "upstream", "upslope"}
# BARE particles (down/up/below/above): ambiguous with PHRASAL VERBS ("turn UP the sound", "pull it UP").
# They count as a gravity PATH only with a real SPATIAL GROUND nearby ("down the HILL") -- the
# particle-vs-path distinction (UD compound:prt vs a spatial obl). Prevents over-firing on phrasal verbs.
BARE_DOWN: Set[str] = {"down", "below"}
BARE_UP: Set[str] = {"up", "above"}
# a small hand FAST-PATH of spatial grounds; the GENERAL check grounds the word in the INCLINED-SURFACE /
# PATH image schema via WordNet IS-A (below) so it GENERALIZES to novel grounds (knoll/gully/ravine/...).
SPATIAL_GROUNDS: Set[str] = {"hill", "slope", "incline", "grade", "stairs", "staircase", "ramp", "chute",
                             "street", "road", "path", "ground", "floor", "valley", "bank", "riverbank",
                             "mountain", "ladder", "roof", "hillside", "slide", "drain", "gutter", "shaft"}
# BRAIN-FOUNDATIONAL GENERALIZATION (owner: "generalize the way the brain does"): the brain does not carry
# a WORD LIST -- it maps a word to its GROUNDED CONCEPTUAL FEATURE / image schema (Talmy 1988; Lakoff/
# Johnson image schemas; Barsalou grounded simulation) and runs the force-dynamic SIMULATION over that. So
# "is this an inclined-surface/path?" is decided by IS-A grounding (a hill/knoll/ravine IS-A geological_
# formation / incline / way), which GENERALIZES to novel words a list would miss. NOTE the earlier WordNet
# result is CONSISTENT, not contradictory: IS-A works for TAXONOMIC features (ground, physical-entity) and
# fails for DISPOSITION ("affords rolling" is not taxonomic) -- so affordance stays a core-physics property
# lexicon (itself a grounded feature), while ground/physicality are IS-A-grounded. The force-sum over these
# grounded features IS the simulation.
_GROUND_SCHEMA_ROOTS = ("geological_formation.n.01", "incline.n.01", "surface.n.01", "way.n.06",
                        "passage.n.03", "track.n.01", "road.n.01", "stairway.n.01", "channel.n.01",
                        "slope.n.01")


def _is_spatial_ground(noun: str) -> bool:
    """Does the noun evoke the INCLINED-SURFACE / PATH image schema? Hand fast-path, then WordNet IS-A
    grounding (generalizes to novel grounds). This is the brain's word->conceptual-feature route."""
    if noun in SPATIAL_GROUNDS:
        return True
    try:
        from nltk.corpus import wordnet as wn
    except Exception:
        return False
    roots = set()
    for s in wn.synsets(noun, pos=wn.NOUN)[:4]:
        for p in s.hypernym_paths():
            roots |= {h.name() for h in p}
    return any(r in roots for r in _GROUND_SCHEMA_ROOTS)
# "with the current/tide/wind/flow/stream/gravity" = aligned; "against ..." = opposed.
WITH_HEADS: Set[str] = {"current", "tide", "wind", "flow", "stream", "gravity", "slope", "grade"}
# aspectual self-motion (patient tending) vs blocked (patient INTRINSICALLY resisting -- genuine resistance
# words only; NOT "back/against/shut/locked" which are directions/particles, a measured over-fire source).
SELF_MOTION = [("on", "its", "own"), ("by", "itself"), ("of", "its", "own", "accord")]
SELF_WORDS: Set[str] = {"freely", "readily", "easily", "spontaneously", "itself", "alone"}
BLOCKED_WORDS: Set[str] = {"jammed", "stuck", "wedged", "refused", "resisted", "reluctant", "stubbornly"}


def directional_sign(context: List[str], verb: str = None) -> int:
    """+1 (gravity/flow/aspect aligns with the outcome -> patient tends), -1 (opposes), 0 (none)."""
    toks = [t.lower().strip(".,;:!?\"'") for t in context]
    toks = [t for t in toks if t]
    tset = set(toks)
    score = 0
    _dirwords = BARE_DOWN | BARE_UP | DOWN_CUES | UP_CUES   # a direction word cannot be its own ground
    has_ground = any(_is_spatial_ground(t) for t in toks if t not in _dirwords)  # IS-A grounded, generalizes
    # gravity/gradient direction: self-contained always; bare particles only with a spatial ground.
    if tset & DOWN_CUES or (has_ground and tset & BARE_DOWN):
        score += 1
    if tset & UP_CUES or (has_ground and tset & BARE_UP):
        score -= 1
    # "with X" / "against X" where X is a flow/gravity head
    for i, t in enumerate(toks):
        if t in ("with", "against") and i + 1 < len(toks):
            nxt = toks[i + 1]
            if nxt in ("the", "a") and i + 2 < len(toks):
                nxt = toks[i + 2]
            if nxt in WITH_HEADS:
                score += 1 if t == "with" else -1
    # aspectual self-motion vs blocked
    for pat in SELF_MOTION:
        if _contains_seq(toks, pat):
            score += 1
    if tset & SELF_WORDS:
        score += 1
    if tset & BLOCKED_WORDS:
        score -= 1
    return (1 if score > 0 else (-1 if score < 0 else 0))


def _contains_seq(toks: List[str], seq: Tuple[str, ...]) -> bool:
    n = len(seq)
    return any(tuple(toks[i:i + n]) == seq for i in range(0, max(0, len(toks) - n + 1)))


# ---------------------------------------------------------------------------
# TERM 4 -- AFFECTOR ROLE: CAUSING vs LETTING (Talmy 1988 distinct force-dynamic pattern).
# The CAUSE/ENABLE split is carried by CONCORDANCE, not force magnitude (Wolff & Song 2003): an affector
# that REMOVES A RESTRAINT (a key unlocks; a valve/floodgate/cork releases) does NOT oppose the patient --
# it LETS the result happen -> ENABLE, independent of magnitude. This is why "the key opened the gate"
# (letting) vs "the wind opened the gate" (a force overcoming a shut gate = causing) split on the SAME verb.
# PINNED: Talmy (1988) "Force Dynamics in Language and Cognition" Cog.Sci. 12:49-100 (letting = the
# Antagonist ceases to impinge); Wolff & Song (2003) ENABLE/ALLOW verb class {enable, allow, permit, let,
# free, release}. Neural ENABLE-vs-CAUSE dissociation is a GAP (UNPINNED); developmental support: causative
# sub-types are acquired as separable classes (Nat.Hum.Behav. 2025; Bowerman). Alternative (non-force)
# account: Sloman, Barbey & Hotaling (2009) Cog.Sci. 33:21-50 (ENABLE = necessity + alternative cause).
# The lexicon is OUR-INVENTION (gated on the letting-shuffle twin + the onset-cause negative control).
#
# TWO-TIER (drill 2026-08-30, design-critical): clean restraint-removers fire ENABLE directly; ONSET-CAUSE
# instruments (switch/trigger/lever/button/press) APPLY AN IMPULSE TO INITIATE -> that is CAUSING, NOT
# letting, and must NEVER fire ENABLE (they return 0 here and fall to the tendency cues / verb lexicon).
# ---------------------------------------------------------------------------
RESTRAINT_REMOVER_INSTRUMENTS: Set[str] = {
    # instruments whose function is to hold-then-free. Deliberately EXCLUDES lexically ambiguous words:
    # "tap" (also = a light tap, a weak-force manner word), "hook"/"bolt" (also patients / can apply force).
    "key", "latch", "catch", "valve", "cork", "plug", "floodgate", "clasp", "buckle", "seal",
    "release", "brake", "clutch",
}
# clean restraint-removal ACTIONS in the surrounding context (the "un-" family + release verbs).
RELEASE_CONTEXT_CUES: Set[str] = {
    "unlocked", "unlock", "unbarred", "unbar", "unlatched", "unlatch", "unbolted", "unbolt",
    "unfastened", "unfasten", "unhooked", "unchained", "unclasped", "unbuckled", "uncorked",
    "unplugged", "unsealed", "unscrewed", "untied", "undone", "unblocked", "released", "release",
    "freed", "free", "loosened", "loosen", "slackened", "eased", "let", "permitted", "allowed", "unleashed",
}
# EXCLUDED onset-cause instruments (apply an impulse to START -> CAUSING, not letting). Never fire ENABLE.
ONSET_CAUSE_INSTRUMENTS: Set[str] = {"switch", "trigger", "lever", "button", "press", "crank", "pedal"}


def affector_letting_sign(affector: str, verb: str = None, context: List[str] = None) -> int:
    """+1 if the affector removes a restraint / lets the result happen (Talmy letting -> ENABLE), else 0.
    Onset-cause instruments (switch/trigger/lever) are explicitly NOT letting (return 0)."""
    if affector in ONSET_CAUSE_INSTRUMENTS:
        return 0
    if affector in RESTRAINT_REMOVER_INSTRUMENTS:
        return 1
    if context:
        toks = {t.lower().strip(".,;:!?\"'") for t in context}
        if toks & RELEASE_CONTEXT_CUES:
            return 1
    return 0


# ---------------------------------------------------------------------------
# COMBINATION -- Wolff PATIENT-SIDE force sum, read out as concordance -> CAUSE / ENABLE.
#
# FIDELITY NOTE (drill 2026-08-29, Wolff 2007 JEP:General 136 / Wolff & Barbey 2015 Front.Hum.Neurosci.
# 9:1, PINNED): the vector-addition rule is faithful, but the causal TYPE is NOT read off the grand
# resultant R = A(ffector)+P(atient)+O(ther). CAUSE and ENABLE BOTH reach the endstate; the
# discriminator is the SIGN of the PATIENT tendency and its CONCORDANCE with the affector. So the sum
# below is PATIENT-SIDE ONLY -- {affordance (P internal + friction/momentum), directional/gravity (O)}
# plus the affector-magnitude term, which enters NOT as the affector's own force but as an ABDUCTIVE
# INFERENCE about the patient (weak affector + endstate reached => the patient supplied the rest =>
# positive patient tendency). The affector, being the agent of a REACHED endstate, points toward the
# endstate (+E); therefore CONCORDANCE = sign(patient-tendency): +1 tends -> concur -> ENABLE; -1
# resists -> oppose -> CAUSE. We never collapse the affector's magnitude into the tendency sign as a
# force -- that would destroy the CAUSE/ENABLE distinction (the drill's one flag).
#
# The property->lability map (TERM 2) is OUR-INVENTION-UNDER-TEST: Wolff PINS that the patient force may
# come from "mechanisms internal to the patient" and "resistance due to friction/momentum", but the
# specific round/buoyant/hinged=>tends, heavy/anchored=>resists lexicon is ours -- gated on a can-fail
# positive control + info-free twin, not face validity. Weights are OUR-INVENTION and SWEPT.
# ---------------------------------------------------------------------------
DEFAULT_WEIGHTS = {"m": 1.0, "a": 1.0, "d": 1.0, "e": 1.0}


def patient_tendency_signal(affector: str, verb: str, patient: str, context: List[str],
                            endstate_reached: bool, weights: Dict[str, float] = None,
                            use_wordnet: bool = False, weak: Set[str] = None, strong: Set[str] = None,
                            props_map: Dict[str, Set[str]] = None) -> Tuple[int, Dict[str, int]]:
    """Return (tendency_sign in {-1,0,+1}, per-term contributions).
    +1 => ENABLE (patient tends / concordant / affector lets); -1 => CAUSE (resists / discordant);
    0 => no evidence (caller falls back to the verb lexicon). Terms: m=affector-magnitude(abductive),
    a=patient-affordance, d=directional/gravity, e=affector-letting-role (Talmy causing-vs-letting)."""
    w = DEFAULT_WEIGHTS if weights is None else weights
    m = affector_magnitude_sign(affector, weak, strong) if endstate_reached else 0
    a = patient_affordance_sign(patient, verb, context=context, use_wordnet=use_wordnet, props_map=props_map)
    d = directional_sign(context, verb)
    e = affector_letting_sign(affector, verb, context)
    T = w["m"] * m + w["a"] * a + w["d"] * d + w.get("e", 1.0) * e
    sign = 1 if T > 1e-9 else (-1 if T < -1e-9 else 0)
    return sign, {"m": m, "a": a, "d": d, "e": e, "T": T}


def type_with_full_tendency(affector: str, verb: str, patient: str, context: List[str],
                            endstate_reached: bool, lexicon: Dict[str, str],
                            weights: Dict[str, float] = None, use_wordnet: bool = False,
                            weak: Set[str] = None, strong: Set[str] = None,
                            props_map: Dict[str, Set[str]] = None) -> str:
    """Full force-dynamic type. For tendency-ambiguous verbs with the endstate reached, use the
    patient-tendency force sum to set concordance (CAUSE vs ENABLE); otherwise defer to the verb
    lexicon (which is faithful where the verb fixes tendency: PREVENT verbs, prototypical CAUSE)."""
    vlem = lemmatize_verb(verb)            # fire on inflected real text (opened->open)
    if vlem in AMBIGUOUS_VERBS and endstate_reached:
        sign, _ = patient_tendency_signal(affector, vlem, patient, context, endstate_reached,
                                          weights=weights, use_wordnet=use_wordnet,
                                          weak=weak, strong=strong, props_map=props_map)
        if sign > 0:
            return "ENABLE"    # patient tended, forces concur
        if sign < 0:
            return "CAUSE"     # patient resisted, affector overcame -> forces oppose
        # sign == 0: no tendency evidence -> verb lexicon's fixed lean
    return force_dynamic_type(vlem, endstate_reached, lexicon)
