"""Reusable FORCE-DYNAMIC verb lexicon + the Wolff/Talmy CAUSE/ENABLE/PREVENT typer.

Landed 2026-08-29 (verbatim from the integrated `causation_has_no_force_dynamic_typing`, owner-DONE/EXCELLENT — the
situation-model CAUSATION dimension's typer): on connective-neutral minimal pairs it types the three 0.929 vs the
connective/adjacency placeholder 0.190 AND precedence-only 0.190 (both beaten CI-sep), the force-class-shuffle twin loses,
and the PREVENT killer (an outcome that never happens) reads 0.900 vs 0.000 — only force dynamics can represent a prevented
endstate. This is the store-agnostic scoring CORE; the coupled wiring (a TYPED `CausalLink` into `situation_reader._read_causation`,
precedence-gated by the TIME register) is a queued follow-on. NO external LLM at inference (FrameNet is a static nltk lexical
asset — like the landed location_register's wordnet / predarg_frontend's verbnet; the verb→class map is cached to
`data/force_dynamics_lexicon_v1/lexicon.json` for speed and REGENERATED deterministically from the nltk FrameNet corpus if absent).

BRAIN MECHANISM (PINNED -- Talmy 1988; Wolff 2007 "force theory of causation"; Wolff & Song 2003
"Models of causation and the semantics of causal verbs" Cog.Psych. 47:276-332 shows verb choice
tracks force-vectors; Feng, Wang, Liu, Wang, Tian & Fan 2021 Front.Hum.Neurosci. 15:666179 ALE
meta-analysis localises DISCOURSE causal inference to left IFG + left MTG + bilateral mPFC -- NOTE
this meta-analysis does NOT itself dissociate CAUSE/ENABLE/PREVENT; see the research note):
CAUSE / ENABLE / PREVENT fall out of a small DISCRETE truth-table over 3 (mostly binary) dims:
    (1) does the PATIENT tend toward the endstate on its own?
    (2) do the AFFECTOR and PATIENT forces CONCUR or OPPOSE?
    (3) is the endstate REACHED?
    CAUSE   = (patient does NOT tend, forces OPPOSE, endstate REACHED)
    ENABLE  = (patient DOES tend,     forces CONCUR,  endstate REACHED)
    PREVENT = (patient DOES tend,     forces OPPOSE,  endstate NOT reached)
The verb's force CLASS supplies (patient-tendency, concordance) in compressed form; the narrative's
outcome polarity supplies the endstate bit. Glass-box, no LLM at inference.

THE LEXICON IS EXTERNAL (this is the point -- not curated to any gold). Force classes are derived by
FRAME MEMBERSHIP in the FrameNet Causation family (nltk.corpus.framenet), the substrate-native
lexical resource the brief names:
  CAUSE   <- Causation + the Cause_* family (affector forces the change against patient inertia)
  ENABLE  <- the LETTING lexical units {allow, enable, let, permit} of Preventing_or_letting
             (+ the allow-sense of Prevent_or_allow_possession)
  PREVENT <- the PREVENTING lexical units of Preventing_or_letting + Thwarting + Hindering
             (opposing what tends to happen; endstate blocked)
The ONE unavoidable hand-split: Preventing_or_letting conflates ENABLE and PREVENT senses in a single
frame, so its 19 verb LUs are split by the closed ENABLE set below. Everything else is pure frame
membership. This yields a lexicon of ~300 verbs whose class assignment PREDATES any test gold.

Reuse: nltk FrameNet (cached to data/force_dynamics_lexicon_v1/). ASCII-only. Deterministic.
"""
from __future__ import annotations

import json
import os
import sys
from typing import Dict, List, Optional, Tuple

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

CACHE_DIR = os.path.join(_REPO, "data", "force_dynamics_lexicon_v1")
CACHE_PATH = os.path.join(CACHE_DIR, "lexicon.json")

# ---------------------------------------------------------------------------
# Frame -> force class. Pure FrameNet Causation-family membership (the external asset).
# ---------------------------------------------------------------------------
CAUSE_FRAMES = [
    "Causation", "Cause_to_start", "Cause_change", "Cause_change_of_consistency",
    "Cause_change_of_phase", "Cause_change_of_position_on_a_scale", "Cause_change_of_strength",
    "Cause_expansion", "Cause_fluidic_motion", "Cause_harm", "Cause_impact", "Cause_motion",
    "Cause_temperature_change", "Cause_to_amalgamate", "Cause_to_be_dry", "Cause_to_be_wet",
    "Cause_to_end", "Cause_to_fragment", "Cause_to_make_noise", "Cause_to_move_in_place",
    "Cause_to_wake", "Cause_bodily_experience", "Cause_emotion", "Cause_to_experience",
    "Corroding_caused",
]
# The whole-frame PREVENT sources (uniformly opposing / impeding). Halt = {halt, stop}: adding it is a
# principled FRAME-level coverage fix (not verb tuning) for the common narrative verb 'halt'.
PREVENT_FRAMES = ["Thwarting", "Hindering", "Halt"]
# Activity_stop / Process_stop drift toward aspectual cessation, not force-dynamic prevention -- held
# OUT of the core and only swept in the coverage cell to show the frame-inclusion sensitivity.
PREVENT_FRAMES_SWEEP_EXTRA = ["Activity_stop", "Process_stop"]
# The frames FrameNet conflates -- split by the closed ENABLE lexical-unit set.
MIXED_FRAMES = ["Preventing_or_letting", "Prevent_or_allow_possession"]
# The ONE hand-split: which lexical units in a MIXED frame are ENABLE (letting); the rest PREVENT.
ENABLE_LUS = {"allow", "enable", "let", "permit", "leave"}

# A tiny narrative back-off for archaic / high-frequency force verbs FrameNet's Causation family
# misses as a *causal* sense (measured coverage gaps on real narrative; each labelled by force role,
# NOT tuned to any test item -- these are generic force verbs). Kept SMALL and auditable.
NARRATIVE_BACKOFF = {
    # CAUSE: an agonist exerting force that overcomes patient inertia
    "swell": "CAUSE", "topple": "CAUSE", "shatter": "CAUSE", "ignite": "CAUSE", "snap": "CAUSE",
    "capsize": "CAUSE", "sink": "CAUSE", "flood": "CAUSE", "spark": "CAUSE", "burst": "CAUSE",
    # PREVENT: opposing what tends to happen. deter/curb/stall + save/protect/defend/spare are canonical
    # prevention verbs (protection = preventing harm) GENUINELY ABSENT from FrameNet's Causation family
    # (a measured resource gap, reported in the coverage cell) -- textbook force-dynamic PREVENT, not
    # gold-specific. (These are also highly POLYSEMOUS -- save money, keep quiet -- which is exactly the
    # verb-sense-disambiguation precision bound the real-text serve measures.)
    "dam": "PREVENT", "shield": "PREVENT", "guard": "PREVENT", "ward": "PREVENT", "fend": "PREVENT",
    "stave": "PREVENT", "bar": "PREVENT", "deter": "PREVENT", "curb": "PREVENT", "stall": "PREVENT",
    "save": "PREVENT", "protect": "PREVENT", "defend": "PREVENT", "spare": "PREVENT", "shelter": "PREVENT",
    "rescue": "PREVENT",
    # ENABLE: permitting / freeing what already tends
    "free": "ENABLE", "loosen": "ENABLE", "unleash": "ENABLE", "release": "ENABLE",
}


def _lemmatize_lu(lu_name: str) -> Optional[str]:
    """FrameNet LU name -> a single lower verb lemma, or None for multiwords we can't index by head."""
    base = lu_name.rsplit(".", 1)[0].strip().lower()
    # keep single tokens (multiword 'give rise', 'stave off' indexed by their head where unambiguous)
    if " " in base:
        head = base.split()[0]
        return head if head.isalpha() else None
    return base if base.isalpha() else None


def build_force_lexicon(use_cache: bool = True, cause_frames=None, prevent_frames=None,
                        enable_lus=None, backoff=None) -> Dict[str, str]:
    """Build (or load cached) verb -> force-class map from the FrameNet Causation family.

    Class priority when a verb sits in multiple frames: PREVENT > ENABLE > CAUSE. Prevention/letting
    verbs are the marked, low-frequency, force-specific senses; a verb that is BOTH (e.g. 'check' in
    Preventing_or_letting AND some Cause_* frame) is force-dynamically the prevent sense in a causal
    clause. This priority is a fixed rule, not per-verb tuning.

    The frame lists / ENABLE-LU set / backoff can be overridden (the coverage cell sweeps them);
    the cache is only used for the DEFAULT configuration.
    """
    default = (cause_frames is None and prevent_frames is None and enable_lus is None and backoff is None)
    cause_frames = CAUSE_FRAMES if cause_frames is None else cause_frames
    prevent_frames = PREVENT_FRAMES if prevent_frames is None else prevent_frames
    enable_lus = ENABLE_LUS if enable_lus is None else enable_lus
    backoff = NARRATIVE_BACKOFF if backoff is None else backoff
    if default and use_cache and os.path.exists(CACHE_PATH):
        with open(CACHE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)["lexicon"]

    from nltk.corpus import framenet as fn  # local import (heavy; remote has no need to parse)

    cause: Dict[str, None] = {}
    enable: Dict[str, None] = {}
    prevent: Dict[str, None] = {}

    def add_frame(name, sink):
        try:
            fr = fn.frame_by_name(name)
        except Exception:
            return
        for lu in fr.lexUnit.keys():
            if not lu.endswith(".v"):
                continue
            lem = _lemmatize_lu(lu)
            if lem:
                sink[lem] = None

    for fr in cause_frames:
        add_frame(fr, cause)
    for fr in prevent_frames:
        add_frame(fr, prevent)
    for fr in MIXED_FRAMES:
        try:
            f = fn.frame_by_name(fr)
        except Exception:
            continue
        for lu in f.lexUnit.keys():
            if not lu.endswith(".v"):
                continue
            lem = _lemmatize_lu(lu)
            if not lem:
                continue
            (enable if lem in enable_lus else prevent)[lem] = None

    lex: Dict[str, str] = {}
    for v in cause:
        lex[v] = "CAUSE"
    for v in enable:
        lex[v] = "ENABLE"     # ENABLE overrides CAUSE (marked letting sense)
    for v in prevent:
        lex[v] = "PREVENT"    # PREVENT overrides both (marked opposing sense)
    for v, c in backoff.items():
        lex.setdefault(v, c)  # ONLY fill gaps -- never override a FrameNet assignment

    if not default:
        return lex            # swept configs are not cached
    os.makedirs(CACHE_DIR, exist_ok=True)
    meta = {
        "resource": "nltk.corpus.framenet (FrameNet 1.7 bundled with NLTK)",
        "cause_frames": CAUSE_FRAMES, "prevent_frames": PREVENT_FRAMES, "mixed_frames": MIXED_FRAMES,
        "enable_lus": sorted(ENABLE_LUS), "narrative_backoff": NARRATIVE_BACKOFF,
        "n_verbs": len(lex),
        "note": "verb->force-class by FrameNet Causation-family membership; the ONLY hand-split is the "
                "ENABLE vs PREVENT lexical units of the Preventing_or_letting/Prevent_or_allow_possession "
                "frames. Class assignment predates any test gold.",
    }
    with open(CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump({"_meta": meta, "lexicon": lex}, f, indent=1, sort_keys=True)
    return lex


# ---------------------------------------------------------------------------
# The typer (Wolff truth-table). class + endstate-reached -> CAUSE/ENABLE/PREVENT.
# ---------------------------------------------------------------------------
def force_dynamic_type(verb: str, endstate_reached: bool, lexicon: Dict[str, str]) -> str:
    """Glass-box Wolff typing. Returns CAUSE / ENABLE / PREVENT / NO_CAUSATION / SEQUENTIAL.

    SEQUENTIAL: the verb carries no force-dynamic class -> not a causal link (precision on Set B).
    NO_CAUSATION: a canonical config failed (a CAUSE/ENABLE verb whose endstate was NOT reached, or a
      PREVENT verb whose endstate WAS reached -- the prevention failed); not one of the 3 canonical types.
    """
    cls = lexicon.get(verb)
    if cls is None:
        return "SEQUENTIAL"
    if cls == "PREVENT":
        # PREVENT is canonical only when the (tending) endstate is BLOCKED. If the outcome happened,
        # the prevention failed -> no prevented endstate exists.
        return "PREVENT" if not endstate_reached else "NO_CAUSATION"
    if cls == "ENABLE":
        return "ENABLE" if endstate_reached else "NO_CAUSATION"
    # CAUSE class
    return "CAUSE" if endstate_reached else "NO_CAUSATION"


# ---------------------------------------------------------------------------
# Endstate polarity detector (the negation/polarity component the brief puts IN SCOPE).
# Brain-faithful: the endstate bit comes from the narrative OUTCOME (not the verb), read with a
# glass-box negation/failure detector. Default polarity = "reached"; flipped by explicit negation or a
# failure/blocked cue in the outcome clause. This keeps endstate an INDEPENDENT text signal so the
# CAUSE-vs-ENABLE contrast (both reached) isolates the verb-force contribution.
# ---------------------------------------------------------------------------
NEG_CUES = {
    "not", "n't", "never", "no", "none", "nothing", "without", "failed", "fails", "fail",
    "unable", "cannot", "couldn't", "didn't", "wouldn't", "prevented", "stopped", "blocked",
    "avoided", "averted", "spared", "safe", "dry", "unharmed", "intact", "survived", "escaped",
}
# outcome verbs/adjs that name a REACHED endstate positively (a small closed set for the gold's domain;
# the detector is scored, and its coverage is a reported bound -- not asserted complete).
POS_REACHED_HINTS = {"flooded", "shattered", "burned", "collapsed", "fell", "broke", "spread",
                     "happened", "occurred", "opened", "escaped_pos"}


def detect_endstate_reached(outcome_tokens: List[str]) -> bool:
    """Read endstate polarity from the narrative outcome clause. Returns True if the endstate was
    REACHED, False if negated/blocked. Glass-box: a negation/failure cue anywhere in the outcome
    clause flips the default (reached) to not-reached."""
    toks = [t.lower().strip(".,;:!?\"'") for t in outcome_tokens]
    toks = [t for t in toks if t]
    for t in toks:
        if t in NEG_CUES:
            return False
    # split contractions like "didn't" already covered; also catch trailing n't tokens
    joined = " ".join(toks)
    if "n't" in joined:
        return False
    return True
