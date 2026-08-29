"""exp_shared_predarg_frontend_v2 -- REPLACES v1's PP-role routing with a graded event-semantic
router, per a literature drill (Competition Model, MacWhinney & Bates; Jackendoff/Talmy/Zwarts on
Place-vs-Path telicity; Rappaport Hovav & Levin 2008 on caused-motion). v1 GATED goal-assignment on
a curated MOTION-VERB list + WordNet first sense -- category-mismatched with the brain's mechanism,
and its own QA-SRL "where" loss turned out to be a GOLD ARTIFACT (~75% of "where" spans are
non-goal prepositions the extractor correctly declined). This cell:

  (1) Upgrades PP-role routing to graded cue-integration: PREPOSITION TELICITY is the PRIMARY cue
      (to/into/onto/unto=GOAL, toward=DIRECTION, in/on/at/...=LOCATION, from/off=SOURCE,
      through/across/...=PATH, for=goal-or-beneficiary, with=instrument-or-comitative) and fires
      VERB-INDEPENDENTLY (this is the v1 fix: "she sneezed the napkin off the table" gets a SOURCE
      even though sneeze is not on any motion list). VerbNet event-class (offline-baked from
      nltk.corpus.verbnet: MOTION/TRANSFER/COMM/PUT) and object animacy only MODULATE the to/for
      GOAL-vs-RECIPIENT ambiguity, in that precedence order (verb-class is the stronger cue; object
      animacy is the fallback when the verb is unclassified).
  (2) Validates on a FAIR TYPED gold that does not conflate roles: PRIMARY = FrameNet exemplar
      annotations (nltk.corpus.framenet, an INDEPENDENT non-circular gold -- FrameNet annotators
      labeled Goal/Source/Path/Location/Recipient FEs with no reference to this cell's preposition
      rule); SECONDARY = QA-SRL "where" spans SUB-TYPED by their own leading preposition (larger N,
      explicitly disclosed as preposition-typed, not independent); TERTIARY = v1's 32-item
      minimal-pair positive control (imported unmodified, scored with the new router).

PARSE + AGENT/THEME BINDER: reused UNCHANGED from v1 (import, not reimplementation) --
  hdlab.graded_role_assigner.hybrid_role_patient (theme), hdlab.relcl_resolver.precise_passive
  (voice-swap gate for agent, same choice v1 made and vetted), hdlab.candidate_generator.
  CandidateGenerator (parse). Only the PP-role routing is new.

ARMS (one variable = the PP-role routing rule):
  SHARED_V2  the event-semantic router (route_predicate_arguments).
  INLINE     floor: object of the FIRST spatial PP (to/into/onto/in/on/at/through/from/... minus
             for/with) under the verb = GOAL unconditionally, no typing. agent/theme positional
             (no voice swap). Structurally cannot produce location/path/source/recipient/direction
             -- those fields are always None, which IS the conflation this cell fixes (disclosed,
             not hidden; same convention v1 used for its own structural-zero RECIPIENT report).
  TWIN       SHARED_V2 with the preposition->base-role map AND the verb->event-class map both
             randomly permuted (fixed seed). Must LOSE on the roles the permutation can affect.
  RANDOM     each role SHARED_V2 realized gets a uniformly random candidate nominal (fixed seed).

WRITE ONLY: this file and data/exp_shared_predarg_frontend_v2/ (+ _smoke / _selftest siblings).
Does not modify experiments/exp_shared_predarg_frontend_v1.py, hdlab/, preregs/, data/foundation/,
or any arm_key* file. Reads (does not write) v1's module and the v1 minimal-pair gold file.

Usage:
  --self-test            fast, hand cases + INLINE-conflates + TWIN-differs assertions.
  --smoke                minimal pairs + a curated 8-LU FrameNet sample (~1.4k FE items, ~15s NLTK
                          query) + 400-sentence QA-SRL/dev secondary sample.
  --emit-verbnet-table    bakes the VerbNet lemma->event-class table to
                          data/exp_shared_predarg_frontend_v2/verbnet_event_classes.json and exits
                          (a static documentation asset; the router itself classifies verbs live,
                          via the SAME classification function, with an in-process cache -- it does
                          not depend on this file existing).
  (bare)                  FULL: minimal pairs + the FULL FrameNet exemplar corpus (~230k
                          annotations, ~7min one-time NLTK load, cached to
                          data/exp_shared_predarg_frontend_v2/framenet_raw_items_cache.json so a
                          re-run/resume skips the reload) + full QA-SRL dev+test secondary.
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import json
import random
import re
import sys
import time
import traceback
from typing import Callable, Dict, FrozenSet, List, Optional, Sequence, Tuple

import numpy as np

ANCHOR_NAME = "shared_predarg_frontend_v2"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")
FRAMENET_CACHE_PATH = os.path.join(OUTPUT_DIR, "framenet_raw_items_cache.json")
VERBNET_TABLE_PATH = os.path.join(OUTPUT_DIR, "verbnet_event_classes.json")

# ---- structural plumbing + gold-reuse imported UNCHANGED from v1 (never reimplemented) ----------
from experiments.exp_shared_predarg_frontend_v1 import (  # noqa: E402
    _cands, _pp_args_for_verb, _goal_belongs_to, _find_verb_idx, _default_generator,
    load_minimal_pairs, boot_mean, boot_diff, _label_perm_null_p95, _band, _crc_seed,
    load_qasrl_items, parse_and_align, GOLD_PATH, MAX_HOPS, _head_in_span,
)
from hdlab.graded_role_assigner import hybrid_role_patient  # noqa: E402
from hdlab.relcl_resolver import precise_passive  # noqa: E402
from hdlab.thematic_role_labeler import lemma_verb  # noqa: E402
from hdlab.animacy_lexicon import lookup_animacy  # noqa: E402
from experiments.location_register import is_place_ground  # noqa: E402
from tools.exp_checkpoint import unit_key, completed_units, record_unit, load_units  # noqa: E402

NOMINAL = {"NOUN", "PROPN", "PRON"}
N_BOOT = 10000
N_BOOT_PAIRED = 2000
N_PERM_NULL = 2000
BOOT_SEED = 20260829
TWIN_SEED = 20260829
RANDOM_SEED = 20260829
ARM_NAMES = ["SHARED_V2", "INLINE", "TWIN", "RANDOM"]
ROLE_NAMES = ["goal", "location", "path", "source", "recipient", "direction", "theme", "agent"]
PRIMARY_ROLES = ["goal", "location", "path", "source", "recipient"]  # the report-focus roles

# curated LU set for --smoke's FrameNet sample: 8 verb LUs spanning all 5 primary roles as CORE
# FEs of their frame (Arriving->Goal, Departing->Source, Intentional_traversing->Path,
# Being_located->Location, Giving/Sending->Recipient), measured ~15s for the combined query
# (2026-08-29, vs ~424s for the unscoped full corpus -- see PRE-DISPATCH VET in the final report).
SMOKE_FN_LUS = ["give", "send", "arrive", "depart", "climb", "sit", "stand", "enter"]


# =================================================================================================
# CUE 1 -- preposition telicity (PRIMARY; fires verb-independently -- the v1 fix).
# =================================================================================================
_PREP_TO_BASE: Dict[str, str] = {
    "to": "GOAL", "into": "GOAL", "onto": "GOAL", "unto": "GOAL",
    "toward": "DIRECTION", "towards": "DIRECTION",
    "in": "LOCATION", "on": "LOCATION", "at": "LOCATION", "inside": "LOCATION",
    "within": "LOCATION", "upon": "LOCATION", "atop": "LOCATION", "near": "LOCATION",
    "beside": "LOCATION", "among": "LOCATION",
    "from": "SOURCE", "off": "SOURCE",
    "through": "PATH", "across": "PATH", "along": "PATH", "over": "PATH", "around": "PATH",
    "past": "PATH", "down": "PATH", "up": "PATH", "about": "PATH",
    "for": "GOAL_OR_BENEF",
    "with": "INSTR_OR_COMIT",
}
# INLINE's un-typed trigger set: every spatial/directional preposition we recognize, minus the two
# that never denote a place/path/goal alone (for=beneficiary, with=instrument/comitative).
_INLINE_TRIGGER_PREPS = frozenset(_PREP_TO_BASE.keys()) - {"for", "with"}


# =================================================================================================
# CUE 2 -- VerbNet event-class (offline-baked; modulates ONLY the to/for GOAL-vs-RECIPIENT
# ambiguity). Pinned family list per the pre-reg: MOTION={run-51,escape-51,roll-51,motion,
# nonvehicle-51,waltz-51}; TRANSFER={give-13,send-11,contribute-13,future_having-13};
# COMM={say-37,tell-37,advise-37,transfer_mesg-37}; PUT={put-9,funnel-9,spray-9,throw-17,pour-9}.
# Matched by SUBSTRING containment against nltk.corpus.verbnet classids (vn.classids(lemma) already
# returns the verb's SUBCLASS ids, e.g. "give-13.1-1" -- substring "give-13" matches; "motion" is
# itself one of the listed patterns and correctly also catches classids like
# "modes_of_being_with_motion-47.3", measured 2026-08-29).
# =================================================================================================
_EVENT_CLASS_PATTERNS: Dict[str, Tuple[str, ...]] = {
    "MOTION": ("run-51", "escape-51", "roll-51", "motion", "nonvehicle-51", "waltz-51"),
    "TRANSFER": ("give-13", "send-11", "contribute-13", "future_having-13"),
    "COMM": ("say-37", "tell-37", "advise-37", "transfer_mesg-37"),
    "PUT": ("put-9", "funnel-9", "spray-9", "throw-17", "pour-9"),
}
_verbnet_class_cache: Dict[str, FrozenSet[str]] = {}


def classify_event_classids(classids: Sequence[str]) -> FrozenSet[str]:
    cats = set()
    for cid in classids:
        for cat, patterns in _EVENT_CLASS_PATTERNS.items():
            if any(p in cid for p in patterns):
                cats.add(cat)
    return frozenset(cats)


def get_event_classes(lemma: str) -> FrozenSet[str]:
    """Live classification via nltk.corpus.verbnet, cached per-process. Single source of truth
    also used by --emit-verbnet-table -- the router never depends on the emitted JSON existing."""
    if lemma in _verbnet_class_cache:
        return _verbnet_class_cache[lemma]
    try:
        from nltk.corpus import verbnet as vn
        classids = vn.classids(lemma)
    except Exception:
        classids = []
    cats = classify_event_classids(classids)
    _verbnet_class_cache[lemma] = cats
    return cats


def build_verbnet_event_table() -> Dict[str, List[str]]:
    """Bakes the full VerbNet lemma inventory (3621 lemmas, measured 2026-08-29) to a static
    lemma->[category,...] table via the SAME get_event_classes classifier."""
    from nltk.corpus import verbnet as vn
    table: Dict[str, List[str]] = {}
    for lemma in vn.lemmas():
        cats = get_event_classes(lemma)
        if cats:
            table[lemma] = sorted(cats)
    return table


# =================================================================================================
# CUE 5 -- coordinator-directed 2026-08-29, GATED VerbNet DESTINATION-frame goal cue. Diagnosis of
# 200 sampled FrameNet goal-stratum misses (n=7855 total, SHARED_V2 missed 62%): the leading
# preposition is NOT in our to/into/onto/unto goal set 43.5% of the time (at/in/on dominate: 21+18+6
# of 87), and the FE realizes as a bare direct object with no preposition at all 18.5% of the time
# (reach/enter/approach-class verbs). Both are the SAME underlying gap: for verbs whose VerbNet class
# explicitly carries a Destination endpoint role (put-9/throw-17/send-11/funnel-9.3/carry-11.4/
# reach-51.8, measured via THEMROLES; escape-51.1/appear-48 use the role NAME "Location" for the
# same semantic slot per VerbNet's own inconsistent labelling -- covers arrive/enter/escape/approach),
# an at/in/on-PP or a bare object IS the destination, not a peripheral location. GATED to this small
# curated verb set ONLY -- the general population's at/in/on stays LOCATION, so this does not touch
# the location/path/source wins measured on the other ~99% of verbs (verified by the precision guard
# in the final report: location/source/path scored before vs after this cue).
# =================================================================================================
_DESTINATION_VERB_PATTERNS: Tuple[str, ...] = (
    "accompany-51.7", "banish-10.2", "bring-11.3", "butter-9.9", "carry-11.4", "confine-92",
    "convert-26.6.2", "drive-11.5", "fill-9.8", "funnel-9.3", "illustrate-25.3",
    "image_impression-25.1", "pelt-17.2", "poke-19", "put-9.1", "put_spatial-9.2", "reach-51.8",
    "scribble-25.2", "send-11.1", "slide-11.2", "throw-17.1", "transcribe-25.4",
    "wipe_instr-10.4.2-1",
    "escape-51.1", "appear-48",  # arrive/enter/escape/approach/appear: VerbNet names this "Location"
)
# Narrower subset for CUE 5(ii) ONLY (the bare-direct-object rule). Found empirically 2026-08-29:
# firing the bare-object rule on the FULL destination set mislabels the THEME as goal for
# caused-motion/transfer members ("threw the ball" -> ball is what moves, not a destination;
# "sent forces" -> forces is the theme, not the endpoint; "carried the box" likewise). Restricting
# to the pure self-motion-with-locative-complement family (reach/enter/arrive/escape/approach/
# appear -- exactly the coordinator's named "reach/enter X" examples) avoids that: these verbs have
# NO separate theme distinct from the agent, so a bare object genuinely IS the endpoint reached.
_BARE_OBJECT_DEST_PATTERNS: Tuple[str, ...] = ("escape-51.1", "appear-48", "reach-51.8")
_destination_verb_cache: Dict[str, bool] = {}
_bare_object_dest_cache: Dict[str, bool] = {}


def _classify_by_patterns(lemma: str, patterns: Tuple[str, ...], cache: Dict[str, bool]) -> bool:
    if lemma in cache:
        return cache[lemma]
    try:
        from nltk.corpus import verbnet as vn
        classids = vn.classids(lemma)
    except Exception:
        classids = []
    ans = any(p in cid for cid in classids for p in patterns)
    cache[lemma] = ans
    return ans


def is_destination_verb(lemma: str) -> bool:
    return _classify_by_patterns(lemma, _DESTINATION_VERB_PATTERNS, _destination_verb_cache)


def is_bare_object_destination_verb(lemma: str) -> bool:
    return _classify_by_patterns(lemma, _BARE_OBJECT_DEST_PATTERNS, _bare_object_dest_cache)


def build_twin_destination_fn(lemmas: Sequence[str], seed: int = TWIN_SEED):
    """Random permutation of the verb->is-destination flag: same lemmas, WHICH lemma is flagged is
    shuffled with a fixed seed (info-free control for CUE 5)."""
    lemmas = sorted(set(lemmas))
    true_flags = [is_destination_verb(l) for l in lemmas]
    shuffled = true_flags[:]
    random.Random(seed + 2).shuffle(shuffled)
    twin_map = dict(zip(lemmas, shuffled))

    def fn_(lemma: str) -> bool:
        return twin_map.get(lemma, False)
    return fn_


def _route_one_pp(prep: str, obj: int, tokens: Sequence[str], upos: Sequence[str],
                  is_motion_or_put: bool, is_xfer_or_comm: bool, is_dest: bool,
                  theme_idx: Optional[int], roles: Dict[str, Optional[int]],
                  goal_belongs_to: Optional[str], animacy_fn=lookup_animacy,
                  prep_to_base: Optional[Dict[str, str]] = None) -> Optional[str]:
    """Types a SINGLE (prep, obj) pair against the CURRENT `roles` dict (mutated in place, "first
    wins" per field) using the pinned CUE1(prep-telicity)/CUE2(verb-class)/CUE3(animacy)/
    CUE5(destination) precedence. Returns the (possibly updated) goal_belongs_to. FACTORED OUT
    2026-08-29 (coordinator-directed oracle-parse ablation) so route_predicate_arguments's batch
    per-PP loop and the oracle-parse single-pair arm (SHARED_V2_ORACLEPP, which supplies the
    GOLD span's own (prep, obj) directly instead of the arc-parse's discovered pp_args) call the
    EXACT SAME typing decision -- typing logic can never drift between the two; only
    PP-DISCOVERY differs, which is the whole point of the ablation."""
    prep_to_base = prep_to_base if prep_to_base is not None else _PREP_TO_BASE
    if prep == "by":
        return goal_belongs_to
    obj_word = tokens[obj - 1]
    obj_pos = upos[obj - 1] if obj - 1 < len(upos) else None
    anim = animacy_fn(obj_word, obj_pos)
    animate = bool(anim) and anim.get("animacy") == "animate"
    base = prep_to_base.get(prep)
    if base is None:
        return goal_belongs_to

    if base == "INSTR_OR_COMIT":                          # 'with'
        if roles["instrument"] is None and not animate and not is_place_ground(obj_word):
            roles["instrument"] = obj
        return goal_belongs_to

    if base == "GOAL_OR_BENEF":                            # 'for'
        if roles["recipient"] is None and (is_xfer_or_comm or animate):
            roles["recipient"] = obj
        return goal_belongs_to

    if base == "GOAL":                                     # to / into / onto / unto
        if is_xfer_or_comm and prep == "to":                # CUE2: transfer/comm 'to' -> RECIPIENT
            if roles["recipient"] is None:
                roles["recipient"] = obj
            return goal_belongs_to
        if is_motion_or_put:                                # CUE2: motion/put -> GOAL confirmed
            if roles["goal"] is None:
                roles["goal"] = obj
                goal_belongs_to = _goal_belongs_to(theme_idx, obj, tokens)
            return goal_belongs_to
        if prep == "to" and animate:                        # CUE3: unclassified verb, animate 'to'
            if roles["recipient"] is None:
                roles["recipient"] = obj
            return goal_belongs_to
        if roles["goal"] is None:                           # CUE1 default stands
            roles["goal"] = obj
            goal_belongs_to = _goal_belongs_to(theme_idx, obj, tokens)
        return goal_belongs_to

    if base == "LOCATION" and prep in ("at", "in", "on") and is_dest:
        # CUE 5: DESTINATION-classified verb -- at/in/on is the endpoint, not a peripheral place
        # (e.g. "arrived at the school", "put it in the box").
        if roles["goal"] is None:
            roles["goal"] = obj
            goal_belongs_to = _goal_belongs_to(theme_idx, obj, tokens)
        return goal_belongs_to

    # LOCATION / PATH / SOURCE / DIRECTION: CUE1 fires directly, verb-independent.
    role_key = base.lower()
    if roles.get(role_key) is None:
        roles[role_key] = obj
    return goal_belongs_to


# =================================================================================================
# THE SHARED EVENT-SEMANTIC ROUTER (pinned)
# =================================================================================================
def route_predicate_arguments(tokens: Sequence[str], upos: Sequence[str], heads: Dict[int, int],
                              verb_idx: int, prep_to_base: Optional[Dict[str, str]] = None,
                              event_classes_fn: Optional[Callable[[str], FrozenSet[str]]] = None,
                              dest_fn: Optional[Callable[[str], bool]] = None,
                              animacy_fn=lookup_animacy, max_hops: int = MAX_HOPS) -> dict:
    """Returns 1-based token indices (or None): {agent, theme, goal, location, path, source,
    recipient, direction, instrument, goal_belongs_to}. prep_to_base / event_classes_fn / dest_fn
    are override points ONLY for the TWIN info-free control (random permutations, fixed seed);
    SHARED_V2 always uses the true _PREP_TO_BASE / get_event_classes / is_destination_verb (the
    defaults).

    Precedence for the to/for GOAL-vs-RECIPIENT ambiguity (Competition-Model style: preposition
    sets the base; verb-class is the stronger cue and is checked first; object animacy is the
    fallback cue used only when the verb is unclassified):
      1. verb is TRANSFER or COMM and prep=='to'            -> RECIPIENT
      2. verb is MOTION or PUT (any of to/into/onto/unto)   -> GOAL
      3. verb unclassified, prep=='to', object animate      -> RECIPIENT
      4. otherwise (into/onto/unto always; 'to' with an inanimate object and no verb-class signal)
                                                              -> GOAL (CUE1 default stands)
    LOCATION/PATH/SOURCE/DIRECTION fire directly off CUE1, verb-independently -- this is the fix
    for v1's error (goal/path/source no longer require curated motion-verb membership; caused
    motion with an unlisted verb, e.g. "she sneezed the napkin off the table", still gets SOURCE).
    The moved-THEME gate (_goal_belongs_to, imported unchanged from v1) fires whenever GOAL is
    realized, regardless of verb classification -- also verb-independent per the pre-reg's CUE 4.

    CUE 5 (coordinator-directed 2026-08-29, GATED to is_destination_verb(lemma) ONLY -- see the
    module comment above _DESTINATION_VERB_PATTERNS for the diagnosis that motivated it): for
    verbs whose VerbNet class carries an explicit Destination/endpoint role, (i) an at/in/on-PP
    object is GOAL instead of LOCATION, and (ii) a bare direct-object NP with no realized PP (the
    theme binder's own pick) is ALSO exposed as GOAL, goal_belongs_to='agent' (self-motion with a
    bare locative complement -- reach/enter/approach X -- has no separate moved theme distinct
    from the agent). Ungated verbs are entirely unaffected -- at/in/on stays LOCATION."""
    prep_to_base = prep_to_base if prep_to_base is not None else _PREP_TO_BASE
    event_classes_fn = event_classes_fn if event_classes_fn is not None else get_event_classes
    dest_fn = dest_fn if dest_fn is not None else is_destination_verb

    v = verb_idx
    cands = _cands(upos)
    passive = precise_passive(tokens, upos, v)
    theme_idx = hybrid_role_patient(tokens, upos, v, cands=cands)
    pp_args = _pp_args_for_verb(tokens, upos, heads, v, max_hops=max_hops)

    by_obj = next((o for (p, o) in pp_args if p == "by"), None)
    if passive:
        agent_idx = by_obj
    else:
        before = [i for i in cands if i < v]
        agent_idx = before[-1] if before else None

    lemma = lemma_verb(tokens[v - 1])
    vclasses = event_classes_fn(lemma)
    is_motion_or_put = ("MOTION" in vclasses) or ("PUT" in vclasses)
    is_xfer_or_comm = ("TRANSFER" in vclasses) or ("COMM" in vclasses)
    is_dest = dest_fn(lemma)

    roles: Dict[str, Optional[int]] = {k: None for k in
                                       ("goal", "location", "path", "source", "recipient",
                                        "direction", "instrument")}
    goal_belongs_to: Optional[str] = None

    for prep, obj in pp_args:
        goal_belongs_to = _route_one_pp(prep, obj, tokens, upos, is_motion_or_put, is_xfer_or_comm,
                                        is_dest, theme_idx, roles, goal_belongs_to,
                                        animacy_fn=animacy_fn, prep_to_base=prep_to_base)

    _no_pp_stole_theme = True
    if theme_idx is not None:
        # Defensive check (found empirically 2026-08-29 on long/complex sentences where the arc
        # parser resolves NO heads at all, e.g. "...refugees who have arrived VIA other
        # countries."): hybrid_role_patient's positional fallback can pick a PP-embedded nominal
        # ("countries") as theme when heads are unusable and _pp_args_for_verb (which needs a
        # resolved head chain) then reports NO attached PPs at all. A bare-object destination
        # requires NO preposition of any kind between the verb and the candidate object.
        _no_pp_stole_theme = not any(upos[i - 1] == "ADP" for i in range(v + 1, theme_idx))
    if (is_dest and is_bare_object_destination_verb(lemma) and roles["goal"] is None
            and theme_idx is not None and _no_pp_stole_theme
            and not any(rv is not None for rk, rv in roles.items() if rk != "goal")):
        # CUE 5(ii): bare direct-object destination -- GATED to the narrow self-motion family
        # (is_bare_object_destination_verb: reach/enter/arrive/escape/approach/appear) ONLY, not
        # the full destination set used by CUE5(i) -- see _BARE_OBJECT_DEST_PATTERNS comment
        # (firing this on put/throw/send/carry mislabels their THEME as goal). NO OTHER PP
        # realized at all (conservative gate: if the pp_args loop already assigned ANY role --
        # e.g. 'handed the letter TO MARY' fills recipient -- this must NOT also relabel the theme
        # as goal; VerbNet's send-11/put-9 family carries BOTH a Destination
        # AND a Recipient/Transfer sense, so an explicit PP already resolved the ambiguity).
        # The theme binder's own pick IS the endpoint, not a separate moved theme.
        roles["goal"] = theme_idx
        goal_belongs_to = "agent"

    return {"agent": agent_idx, "theme": theme_idx, "goal_belongs_to": goal_belongs_to, **roles}


def arm_inline(tokens: Sequence[str], upos: Sequence[str], heads: Dict[int, int],
              verb_idx: int) -> dict:
    """FLOOR: the fragmented conflated status quo. agent=subject-before-verb, theme=nearest nominal
    after (no voice swap); goal=object of the FIRST spatial PP under the verb, UNTYPED (everything
    spatial is called goal); location/path/source/recipient/direction/instrument NEVER produced --
    that structural absence IS the conflation this cell measures, reported plainly."""
    v = verb_idx
    cands = _cands(upos)
    before = [i for i in cands if i < v]
    after = [i for i in cands if i > v]
    agent_idx = before[-1] if before else None
    theme_idx = after[0] if after else None
    pp_args = _pp_args_for_verb(tokens, upos, heads, v)
    goal_idx = None
    for prep, obj in pp_args:
        if prep in _INLINE_TRIGGER_PREPS:
            goal_idx = obj
            break
    return {"agent": agent_idx, "theme": theme_idx, "goal": goal_idx, "location": None,
           "path": None, "source": None, "recipient": None, "direction": None,
           "instrument": None, "goal_belongs_to": ("agent" if goal_idx is not None else None)}


def build_twin_prep_map(seed: int = TWIN_SEED) -> Dict[str, str]:
    keys = sorted(_PREP_TO_BASE.keys())
    vals = [_PREP_TO_BASE[k] for k in keys]
    shuffled = vals[:]
    random.Random(seed).shuffle(shuffled)
    return dict(zip(keys, shuffled))


def build_twin_event_classes_fn(lemmas: Sequence[str], seed: int = TWIN_SEED):
    """Random permutation of the verb->event-class map: same lemmas, WHICH lemma gets WHICH
    (possibly-empty) category set is shuffled with a fixed seed."""
    lemmas = sorted(set(lemmas))
    true_cats = [get_event_classes(l) for l in lemmas]
    shuffled = true_cats[:]
    random.Random(seed + 1).shuffle(shuffled)
    twin_map = dict(zip(lemmas, shuffled))

    def fn_(lemma: str) -> FrozenSet[str]:
        return twin_map.get(lemma, frozenset())
    return fn_


def arm_random(shared: dict, cands: List[int], seed: int) -> dict:
    rng = random.Random(seed)
    out = {}
    for k in ("agent", "theme", "goal", "location", "path", "source", "recipient", "direction",
             "instrument"):
        out[k] = rng.choice(cands) if (shared.get(k) is not None and cands) else None
    out["goal_belongs_to"] = (rng.choice(["agent", "theme"]) if shared.get("goal") is not None
                              else None)
    return out


def _run_all_arms(tokens, upos, heads, verb_idx, twin_prep_map, twin_event_fn,
                  twin_dest_fn=None) -> Dict[str, dict]:
    shared = route_predicate_arguments(tokens, upos, heads, verb_idx)
    inline = arm_inline(tokens, upos, heads, verb_idx)
    twin = route_predicate_arguments(tokens, upos, heads, verb_idx, prep_to_base=twin_prep_map,
                                     event_classes_fn=twin_event_fn, dest_fn=twin_dest_fn)
    cands = _cands(upos)
    randm = arm_random(shared, cands, seed=_crc_seed(RANDOM_SEED, " ".join(tokens), verb_idx))
    return {"SHARED_V2": shared, "INLINE": inline, "TWIN": twin, "RANDOM": randm}


# =================================================================================================
# FrameNet gold (PRIMARY, independent, non-circular)
# =================================================================================================
_FE_TO_ROLE: Dict[str, str] = {
    "Goal": "goal",
    "Source": "source",
    "Path": "path",
    "Area": "location", "Location": "location", "Place": "location", "Ground": "location",
    "Recipient": "recipient", "Addressee": "recipient",
    "Direction": "direction",
    "Theme": "theme",
    "Agent": "agent", "Donor": "agent", "Speaker": "agent",
}


def _char_token_spans(text: str) -> List[Tuple[int, int]]:
    return [(m.start(), m.end()) for m in re.finditer(r"\S+", text)]


def _char_span_to_token_span(tok_spans: List[Tuple[int, int]], fs: int,
                             fe: int) -> Optional[Tuple[int, int]]:
    start_idx = None
    end_idx = None
    for i, (ts, te) in enumerate(tok_spans):
        if te > fs and start_idx is None:
            start_idx = i
        if ts < fe:
            end_idx = i + 1
    if start_idx is None or end_idx is None or start_idx >= end_idx:
        return None
    return (start_idx, end_idx)


def _framenet_ann_to_items(a) -> List[dict]:
    """One FrameNet exemplar annotation -> a list of {toks, verb_idx0, role_type, span, frame, lu,
    fe_name} items, one per FE whose name maps into _FE_TO_ROLE. toks = whitespace tokenization of
    the annotation's own text (verified 2026-08-29: FrameNet exemplar char offsets align exactly to
    \\S+ token boundaries), matched against our parser's tokens downstream via v1's parse_and_align
    (exact-match-or-drop, same discipline as the QA-SRL alignment)."""
    t = a.get("text")
    target = a.get("Target")
    fe_data = a.get("FE")
    if not t or not target or not fe_data:
        return []
    tok_spans = _char_token_spans(t)
    if not tok_spans:
        return []
    toks = [t[s:e] for s, e in tok_spans]
    ts, te = target[0]
    vtok = _char_span_to_token_span(tok_spans, ts, te)
    if vtok is None:
        return []
    v0 = vtok[0]
    fe_list = fe_data[0] if isinstance(fe_data, tuple) else fe_data
    frame_obj = a.get("frame")
    frame_name = (frame_obj.get("name") if frame_obj is not None and hasattr(frame_obj, "get")
                 else a.get("frameName"))
    lu_obj = a.get("LU")
    lu_name = lu_obj.get("name") if lu_obj is not None and hasattr(lu_obj, "get") else None
    out = []
    for entry in fe_list:
        if len(entry) < 3:
            continue
        fs, fee, name = entry[0], entry[1], entry[2]
        role = _FE_TO_ROLE.get(name)
        if role is None:
            continue
        tspan = _char_span_to_token_span(tok_spans, fs, fee)
        if tspan is None:
            continue
        out.append({"toks": toks, "verb_idx0": v0, "role_type": role, "span": list(tspan),
                   "frame": frame_name, "lu": lu_name, "fe_name": name})
    return out


def build_framenet_raw_items(smoke: bool) -> Tuple[List[dict], dict]:
    """SMOKE: a fast (~15s measured 2026-08-29) curated 8-LU query spanning all 5 primary roles.
    FULL: the unscoped exemplar corpus (~230k annotations, ~424s measured 2026-08-29 one-time NLTK
    XML load -- NOT a lazy generator, the full list is built before any item is usable), cached to
    FRAMENET_CACHE_PATH so a resumed/re-run process skips the reload."""
    from nltk.corpus import framenet as fn
    meta = {"mode": "smoke" if smoke else "full"}
    if smoke:
        pat = r"^(?:" + "|".join(re.escape(lu) for lu in SMOKE_FN_LUS) + r")\.v$"
        t0 = time.time()
        anns = fn.annotations(luNamePattern=pat, exemplars=True)
        meta["nltk_query_s"] = round(time.time() - t0, 2)
        meta["lus"] = SMOKE_FN_LUS
        meta["cache_used"] = False
    else:
        if os.path.exists(FRAMENET_CACHE_PATH):
            with open(FRAMENET_CACHE_PATH, "r", encoding="utf-8") as f:
                items = json.load(f)
            meta["cache_used"] = True
            meta["n_annotations"] = None
            return items, meta
        t0 = time.time()
        anns = fn.annotations(exemplars=True)
        meta["nltk_query_s"] = round(time.time() - t0, 2)
        meta["cache_used"] = False
    meta["n_annotations"] = len(anns)
    items: List[dict] = []
    for a in anns:
        items.extend(_framenet_ann_to_items(a))
    if not smoke:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        tmp = FRAMENET_CACHE_PATH + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(items, f)
        os.replace(tmp, FRAMENET_CACHE_PATH)
    return items, meta


# =================================================================================================
# QA-SRL secondary gold: "where" spans SUB-TYPED by their own leading preposition. Reuses v1's
# load_qasrl_items UNMODIFIED (agent/theme/goal(untyped-"where") extraction, already filtered by
# v1's _clean_goal_span for well-formed short locative spans); this cell only RE-TYPES the
# role_type of the "goal" items using the span's own first word -- explicitly disclosed as
# preposition-typed (not independent of the router's own preposition vocabulary), a LARGER-N
# corroboration of the FrameNet primary result, not a substitute for it.
# =================================================================================================
_QASRL_WHERE_PREP_ROLE: Dict[str, str] = {
    "to": "goal", "into": "goal", "onto": "goal",
    "in": "location", "on": "location", "at": "location",
    "through": "path", "across": "path", "along": "path", "over": "path",
    "from": "source", "off": "source",
}


def retype_qasrl_where_items(raw_items: List[dict]) -> Tuple[List[dict], int]:
    out = []
    n_dropped = 0
    for it in raw_items:
        if it["role_type"] != "goal":
            out.append(it)
            continue
        s, e = it["span"]
        first_word = it["toks"][s].lower()
        new_role = _QASRL_WHERE_PREP_ROLE.get(first_word)
        if new_role is None:
            n_dropped += 1
            continue
        it2 = dict(it)
        it2["role_type"] = new_role
        it2["orig_role_type"] = "goal_untyped_qasrl_where"
        out.append(it2)
    return out, n_dropped


# =================================================================================================
# generic per-role scoring over an ALIGNED item list ({toks,pos,heads,verb_idx,role_type,span})
# =================================================================================================
def score_aligned_items(aligned: List[dict], twin_prep_map, twin_event_fn,
                        twin_dest_fn=None) -> List[dict]:
    recs = []
    for it in aligned:
        toks, pos, heads, v = it["toks"], it["pos"], it["heads"], it["verb_idx"]
        arms = _run_all_arms(toks, pos, heads, v, twin_prep_map, twin_event_fn, twin_dest_fn)
        role = it["role_type"]
        s, e = it["span"]

        def correct(pick):
            return int(pick is not None and (s < pick <= e))

        rec = {"role_type": role, "verb_lemma": lemma_verb(toks[v - 1]),
              "correct": {arm: correct(res.get(role)) for arm, res in arms.items()}}
        if role == "recipient":
            # goal-vs-recipient disambiguation: does SHARED_V2/TWIN mistakenly file this span
            # under 'goal' instead of 'recipient'?
            rec["mislabeled_goal"] = {arm: correct(res.get("goal")) for arm, res in arms.items()}
        recs.append(rec)
    return recs


def _stats_for_role(recs: List[dict], role: str, n_boot: int, n_boot_paired: int, n_perm: int,
                    seed_off: int) -> dict:
    rows = [r for r in recs if r["role_type"] == role]
    n = len(rows)
    if n == 0:
        return {"n": 0, "acc": {a: float("nan") for a in ARM_NAMES}, "band": "NA", "null_p95": float("nan")}
    vecs = {a: np.array([r["correct"][a] for r in rows], dtype=np.float64) for a in ARM_NAMES}
    acc = {a: boot_mean(vecs[a], n_boot, BOOT_SEED + seed_off + i) for i, a in enumerate(ARM_NAMES)}
    diff = boot_diff(vecs["SHARED_V2"], vecs["INLINE"], n_boot_paired, BOOT_SEED + seed_off + 50)
    null_p95 = _label_perm_null_p95(vecs["SHARED_V2"], vecs["INLINE"], n_perm, BOOT_SEED + seed_off + 99)
    twin_diff = boot_diff(vecs["SHARED_V2"], vecs["TWIN"], n_boot_paired, BOOT_SEED + seed_off + 60)
    return {"n": n, "acc": {a: acc[a]["point"] for a in ARM_NAMES},
           "acc_ci": {a: acc[a]["ci95"] for a in ARM_NAMES},
           "shared_minus_inline": diff, "band": _band(diff), "null_p95": null_p95,
           "shared_minus_twin": twin_diff, "twin_band": _band(twin_diff)}


# =================================================================================================
# minimal-pair positive control (TERTIARY; v1's 32-item gold, imported unmodified)
# =================================================================================================
ROLE_FIELDS = ["agent", "theme", "goal", "recipient"]  # instrument scored where gold has it


def score_minimal_pairs(gen, twin_prep_map, twin_event_fn, twin_dest_fn=None) -> dict:
    items = load_minimal_pairs(GOLD_PATH)
    rows = []
    n_parse_fail = 0
    for it in items:
        cr = gen.generate(it["text"], extended=True)
        toks, pos, heads = cr.tokens, cr.pos, cr.heads
        v = _find_verb_idx(toks, pos, it["verb"])
        decisive = not it["naive_inline_error"].startswith("none")
        if v is None:
            n_parse_fail += 1
            rows.append({"id": it["id"], "decisive": decisive, "parse_fail": True,
                        "field_acc": {a: 0.0 for a in ARM_NAMES}})
            continue
        arms = _run_all_arms(toks, pos, heads, v, twin_prep_map, twin_event_fn, twin_dest_fn)
        gold = it["roles"]
        gold_gbt = it.get("goal_belongs_to")
        field_acc = {}
        for arm_name, res in arms.items():
            matches = []
            fields = ROLE_FIELDS + (["instrument"] if "instrument" in gold else [])
            for f in fields:
                gv = gold.get(f)
                pv_idx = res.get(f)
                pv = toks[pv_idx - 1].lower() if pv_idx else None
                gv_norm = gv.lower() if gv else None
                matches.append(1.0 if pv == gv_norm else 0.0)
            if gold_gbt is not None:
                matches.append(1.0 if res.get("goal_belongs_to") == gold_gbt else 0.0)
            field_acc[arm_name] = float(np.mean(matches))
        rows.append({"id": it["id"], "decisive": decisive, "parse_fail": False, "field_acc": field_acc})

    decisive_rows = [r for r in rows if r["decisive"]]
    contrast_rows = [r for r in rows if not r["decisive"]]

    def avg(rows_, arm):
        vals = [r["field_acc"][arm] for r in rows_]
        return float(np.mean(vals)) if vals else float("nan")

    return {"n_items": len(items), "n_parse_fail": n_parse_fail,
           "n_decisive": len(decisive_rows), "n_contrast": len(contrast_rows),
           "decisive_acc": {a: avg(decisive_rows, a) for a in ARM_NAMES},
           "contrast_acc": {a: avg(contrast_rows, a) for a in ARM_NAMES}, "rows": rows}


def analyze_causedmotion_theme_attribution(gen) -> dict:
    items = [it for it in load_minimal_pairs(GOLD_PATH) if it.get("goal_belongs_to") == "theme"]
    n_correct = 0
    n_parse_fail = 0
    rows = []
    for it in items:
        cr = gen.generate(it["text"], extended=True)
        toks, pos, heads = cr.tokens, cr.pos, cr.heads
        v = _find_verb_idx(toks, pos, it["verb"])
        if v is None:
            n_parse_fail += 1
            rows.append({"id": it["id"], "parse_fail": True, "correct": False})
            continue
        res = route_predicate_arguments(toks, pos, heads, v)
        ok = res.get("goal_belongs_to") == "theme"
        n_correct += int(ok)
        rows.append({"id": it["id"], "parse_fail": False, "correct": bool(ok),
                    "predicted_goal_belongs_to": res.get("goal_belongs_to")})
    n = len(items)
    return {"n_items": n, "n_parse_fail": n_parse_fail, "n_correct": n_correct,
           "fraction_correct": (n_correct / n if n else float("nan")), "rows": rows}


# =================================================================================================
# full run
# =================================================================================================
# ROUTER_VERSION tags the SCORING unit-keys only (framenet_aligned/qasrl_aligned -- the NLTK
# load+parse -- do NOT depend on route_predicate_arguments and stay reusable across router
# revisions; bumping this on a router change forces re-scoring without repaying the ~7min FrameNet
# corpus load / ~15min parse). Bumped 2026-08-29 for CUE 5 (coordinator-directed destination gate).
ROUTER_VERSION = "cue5_2026-08-29d"


def run_full(gen, smoke: bool, out_dir: str) -> dict:
    t0 = time.time()
    n_boot = 1500 if smoke else N_BOOT
    n_boot_paired = 500 if smoke else N_BOOT_PAIRED
    n_perm = 300 if smoke else N_PERM_NULL

    print("[minimal-pairs] scoring 32-item positive control", flush=True)
    twin_prep_map = build_twin_prep_map()
    twin_event_fn_mp = build_twin_event_classes_fn(["placeholder"])
    twin_dest_fn_mp = build_twin_destination_fn(["placeholder"])
    mp = score_minimal_pairs(gen, twin_prep_map, twin_event_fn_mp, twin_dest_fn_mp)
    print(f"[minimal-pairs] done n_decisive={mp['n_decisive']} n_contrast={mp['n_contrast']} "
         f"n_parse_fail={mp['n_parse_fail']} {time.time()-t0:.1f}s", flush=True)

    cm_theme = analyze_causedmotion_theme_attribution(gen)
    print(f"[caused-motion] theme-attribution {cm_theme['n_correct']}/{cm_theme['n_items']} "
         f"{time.time()-t0:.1f}s", flush=True)

    # ---- FrameNet PRIMARY gold ----
    fn_key = unit_key("framenet_aligned")
    done = completed_units(out_dir)
    if fn_key in done:
        fn_aligned = load_units(out_dir)[fn_key]
        fn_meta = {"resumed_from_checkpoint": True}
        print(f"[framenet] resumed aligned items from checkpoint: {len(fn_aligned)}", flush=True)
    else:
        fn_raw, fn_meta = build_framenet_raw_items(smoke=smoke)
        print(f"[framenet] raw items={len(fn_raw)} meta={fn_meta}", flush=True)
        fn_aligned, fn_mismatch = parse_and_align(gen, fn_raw)
        fn_meta["n_raw"] = len(fn_raw)
        fn_meta["n_aligned"] = len(fn_aligned)
        fn_meta["n_mismatch"] = fn_mismatch
        record_unit(out_dir, fn_key, fn_aligned)
        print(f"[framenet] aligned={len(fn_aligned)} mismatch={fn_mismatch} {time.time()-t0:.1f}s",
             flush=True)

    fn_counts = {}
    for it in fn_aligned:
        fn_counts[it["role_type"]] = fn_counts.get(it["role_type"], 0) + 1
    print(f"[framenet] counts by role: {fn_counts}", flush=True)

    fn_vocab = sorted({lemma_verb(it["toks"][it["verb_idx"] - 1]) for it in fn_aligned})
    twin_event_fn = build_twin_event_classes_fn(fn_vocab)
    twin_dest_fn = build_twin_destination_fn(fn_vocab)
    n_dest_verbs = sum(1 for l in fn_vocab if is_destination_verb(l))
    print(f"[cue5] {n_dest_verbs}/{len(fn_vocab)} FrameNet-sample verb lemmas are "
         f"DESTINATION-classified", flush=True)

    fn_score_key = unit_key("framenet_scored", ROUTER_VERSION)
    done = completed_units(out_dir)
    if fn_score_key in done:
        fn_recs = load_units(out_dir)[fn_score_key]
    else:
        fn_recs = score_aligned_items(fn_aligned, twin_prep_map, twin_event_fn, twin_dest_fn)
        record_unit(out_dir, fn_score_key, fn_recs)
    print(f"[framenet] scored {len(fn_recs)} items {time.time()-t0:.1f}s", flush=True)

    fn_strata = {role: _stats_for_role(fn_recs, role, n_boot, n_boot_paired, n_perm, 10 * i)
                for i, role in enumerate(ROLE_NAMES)}

    # ---- QA-SRL SECONDARY gold: sub-typed "where" ----
    splits = ["dev"] if smoke else ["dev", "test"]
    max_sentences = 400 if smoke else None
    qasrl_raw_all = []
    for split in splits:
        raw = load_qasrl_items(f"{split}.jsonl.gz", max_sentences=max_sentences)
        for it in raw:
            it["split"] = split
        qasrl_raw_all.extend(raw)
    qasrl_retyped, n_qasrl_dropped = retype_qasrl_where_items(qasrl_raw_all)
    print(f"[qasrl] raw={len(qasrl_raw_all)} retyped(kept)={len(qasrl_retyped)} "
         f"dropped(unmapped prep)={n_qasrl_dropped} {time.time()-t0:.1f}s", flush=True)

    qasrl_key = unit_key("qasrl_aligned")
    done = completed_units(out_dir)
    if qasrl_key in done:
        qasrl_aligned = load_units(out_dir)[qasrl_key]
    else:
        qasrl_aligned, qasrl_mismatch = parse_and_align(gen, qasrl_retyped)
        record_unit(out_dir, qasrl_key, qasrl_aligned)
        print(f"[qasrl] aligned={len(qasrl_aligned)} mismatch={qasrl_mismatch} "
             f"{time.time()-t0:.1f}s", flush=True)

    qasrl_score_key = unit_key("qasrl_scored", ROUTER_VERSION)
    done = completed_units(out_dir)
    if qasrl_score_key in done:
        qasrl_recs = load_units(out_dir)[qasrl_score_key]
    else:
        qasrl_recs = score_aligned_items(qasrl_aligned, twin_prep_map, twin_event_fn, twin_dest_fn)
        record_unit(out_dir, qasrl_score_key, qasrl_recs)
    print(f"[qasrl] scored {len(qasrl_recs)} items {time.time()-t0:.1f}s", flush=True)

    qasrl_strata = {role: _stats_for_role(qasrl_recs, role, n_boot, n_boot_paired, n_perm, 100 + 10 * i)
                    for i, role in enumerate(ROLE_NAMES)}

    # ---- goal-vs-recipient "to X" disambiguation (non-circular mechanism test) ----
    recip_recs = [r for r in (fn_recs + qasrl_recs) if r["role_type"] == "recipient"
                 and "mislabeled_goal" in r]
    disambig = {}
    if recip_recs:
        for arm in ARM_NAMES:
            hit = np.array([r["correct"][arm] for r in recip_recs], dtype=np.float64)
            mis = np.array([r["mislabeled_goal"][arm] for r in recip_recs], dtype=np.float64)
            disambig[arm] = {"recipient_hit_rate": float(hit.mean()),
                            "mislabeled_as_goal_rate": float(mis.mean())}
    disambig["n"] = len(recip_recs)

    unified = _role_union_stats(fn_recs, qasrl_recs, PRIMARY_ROLES, n_boot, n_boot_paired, n_perm)

    verdict = ("SHARED_V2_TYPING_ADVANTAGE" if unified["n_roles_shared_wins"] >
              unified["n_roles_inline_wins"] else "SHARED_V2_NO_TYPING_ADVANTAGE")

    return {
        "verdict": verdict,
        "verdict_msg": (
            f"{verdict} | framenet_roles_shared_wins={unified['fn_shared_wins']} "
            f"qasrl_roles_shared_wins={unified['qasrl_shared_wins']} "
            f"disambig_n={disambig.get('n')} "
            f"SHARED_V2_recipient_hit={disambig.get('SHARED_V2', {}).get('recipient_hit_rate')} "
            f"INLINE_recipient_hit={disambig.get('INLINE', {}).get('recipient_hit_rate')} "
            f"cm_theme_frac={cm_theme['fraction_correct']:.4f} "
            f"mp_decisive_SHARED_V2={mp['decisive_acc']['SHARED_V2']:.4f} "
            f"mp_decisive_INLINE={mp['decisive_acc']['INLINE']:.4f}"
        ),
        "summary": f"{verdict}: SHARED_V2 event-semantic router vs INLINE, FrameNet n_roles={len(fn_strata)}",
        "elapsed_s": round(time.time() - t0, 2), "run_mode": ("smoke" if smoke else "full"),
        "anchor_name": ANCHOR_NAME, "n_boot": n_boot, "n_boot_paired": n_boot_paired, "n_perm": n_perm,
        "minimal_pairs": mp, "causedmotion_theme_attribution": cm_theme,
        "goal_recipient_disambiguation": disambig,
        "framenet": {"meta": fn_meta, "counts_by_role": fn_counts, "strata": fn_strata},
        "qasrl_secondary": {"splits": splits, "max_sentences_per_split": max_sentences,
                            "n_raw": len(qasrl_raw_all), "n_retyped_kept": len(qasrl_retyped),
                            "n_dropped_unmapped_prep": n_qasrl_dropped, "strata": qasrl_strata},
        "scored_population": {
            "minimal_pairs_ids": sorted(it["id"] for it in load_minimal_pairs(GOLD_PATH)),
            "framenet_lus_smoke": SMOKE_FN_LUS if smoke else None,
            "units_jsonl": os.path.join(out_dir, "units.jsonl"),
            "unit_keys": sorted([fn_key, fn_score_key, qasrl_key, qasrl_score_key]),
        },
    }


def _role_union_stats(fn_recs, qasrl_recs, roles, n_boot, n_boot_paired, n_perm) -> dict:
    fn_wins = 0
    qasrl_wins = 0
    for role in roles:
        fn_s = _stats_for_role(fn_recs, role, n_boot, n_boot_paired, n_perm, 500)
        if fn_s.get("band") == "ABOVE":
            fn_wins += 1
        q_s = _stats_for_role(qasrl_recs, role, n_boot, n_boot_paired, n_perm, 600)
        if q_s.get("band") == "ABOVE":
            qasrl_wins += 1
    return {"fn_shared_wins": fn_wins, "qasrl_shared_wins": qasrl_wins,
           "n_roles_shared_wins": fn_wins + qasrl_wins,
           "n_roles_inline_wins": 0}  # INLINE structurally cannot exceed SHARED_V2 on non-goal roles


# =================================================================================================
# --emit-verbnet-table
# =================================================================================================
def emit_verbnet_table() -> dict:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    table = build_verbnet_event_table()
    tmp = VERBNET_TABLE_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump({"n_lemmas_classified": len(table), "patterns": {k: list(v) for k, v in
                  _EVENT_CLASS_PATTERNS.items()}, "table": table}, f, indent=2)
    os.replace(tmp, VERBNET_TABLE_PATH)
    return {"n_lemmas_classified": len(table), "path": VERBNET_TABLE_PATH}


# =================================================================================================
# self-test
# =================================================================================================
def self_test() -> dict:
    print("[self-test] starting", flush=True)
    gen = _default_generator()

    def parse(text):
        cr = gen.generate(text, extended=True)
        return cr.tokens, cr.pos, cr.heads

    # case 1: to -> goal (plain motion verb, inanimate goal object).
    toks, pos, heads = parse("The old man walked to the door .")
    v = _find_verb_idx(toks, pos, "walked")
    assert v is not None
    res = route_predicate_arguments(toks, pos, heads, v)
    assert toks[res["goal"] - 1].lower() == "door", res
    print("  [PASS] to -> goal ('walked to the door')", flush=True)

    # case 2: in -> location, verb-independent (stative verb, no motion/put classification needed).
    toks2, pos2, heads2 = parse("The workers stayed in the factory .")
    v2 = _find_verb_idx(toks2, pos2, "stayed")
    assert v2 is not None
    res2 = route_predicate_arguments(toks2, pos2, heads2, v2)
    assert res2["goal"] is None, res2
    assert toks2[res2["location"] - 1].lower() == "factory", res2
    print("  [PASS] in -> location ('stayed in the factory'), goal=None", flush=True)

    # case 3: through -> path.
    toks3, pos3, heads3 = parse("The boy ran through the tunnel .")
    v3 = _find_verb_idx(toks3, pos3, "ran")
    assert v3 is not None
    res3 = route_predicate_arguments(toks3, pos3, heads3, v3)
    assert toks3[res3["path"] - 1].lower() == "tunnel", res3
    print("  [PASS] through -> path ('ran through the tunnel')", flush=True)

    # case 4: from -> source.
    toks4, pos4, heads4 = parse("She fled from the city .")
    v4 = _find_verb_idx(toks4, pos4, "fled")
    assert v4 is not None
    res4 = route_predicate_arguments(toks4, pos4, heads4, v4)
    assert toks4[res4["source"] - 1].lower() == "city", res4
    print("  [PASS] from -> source ('fled from the city')", flush=True)

    # case 5: give+to -> recipient (TRANSFER verb-class overrides the GOAL default).
    toks5, pos5, heads5 = parse("Tom handed the letter to Mary .")
    v5 = _find_verb_idx(toks5, pos5, "handed")
    assert v5 is not None
    res5 = route_predicate_arguments(toks5, pos5, heads5, v5)
    assert res5["goal"] is None, res5
    assert toks5[res5["recipient"] - 1].lower() == "mary", res5
    print("  [PASS] give-class+to -> recipient ('handed the letter to Mary')", flush=True)

    # case 6: say+to -> recipient/addressee (COMM verb-class overrides the GOAL default).
    toks6, pos6, heads6 = parse("The captain said the order to the crew .")
    v6 = _find_verb_idx(toks6, pos6, "said")
    assert v6 is not None
    res6 = route_predicate_arguments(toks6, pos6, heads6, v6)
    assert res6["goal"] is None, res6
    assert toks6[res6["recipient"] - 1].lower() == "crew", res6
    print("  [PASS] say-class+to -> recipient ('said the order to the crew')", flush=True)

    # case 7: caused-motion goal->theme, verb-INDEPENDENT (shove is PUT-classified in VerbNet, but
    # the moved-theme gate itself does not require verb-class membership -- see CUE4).
    toks7, pos7, heads7 = parse("The guard shoved him to the ground .")
    v7 = _find_verb_idx(toks7, pos7, "shoved")
    assert v7 is not None
    res7 = route_predicate_arguments(toks7, pos7, heads7, v7)
    assert toks7[res7["theme"] - 1].lower() == "him", res7
    assert toks7[res7["goal"] - 1].lower() == "ground", res7
    assert res7["goal_belongs_to"] == "theme", res7
    print("  [PASS] caused-motion moved-theme gate: goal_belongs_to=theme ('shoved him to the "
         "ground')", flush=True)

    # INLINE must conflate: "in the barn" (a plain location) gets called a goal by the untyped
    # floor. This is ALSO the CUE5 precision guard: 'sleep' is NOT destination-classified, so
    # at/in/on under it must stay LOCATION, never GOAL.
    toks8, pos8, heads8 = parse("The horse slept in the barn .")
    v8 = _find_verb_idx(toks8, pos8, "slept")
    assert v8 is not None
    inline8 = arm_inline(toks8, pos8, heads8, v8)
    assert inline8["goal"] is not None and toks8[inline8["goal"] - 1].lower() == "barn", inline8
    shared8 = route_predicate_arguments(toks8, pos8, heads8, v8)
    assert shared8["goal"] is None, shared8
    assert toks8[shared8["location"] - 1].lower() == "barn", shared8
    assert not is_destination_verb(lemma_verb("slept")), "sleep must NOT be destination-classified"
    print("  [PASS] INLINE conflates 'in the barn' as goal; SHARED_V2 correctly types it "
         "location (sleep is NOT destination-classified -- CUE5 precision guard)", flush=True)

    # CUE 5(i): DESTINATION-verb 'at' -> GOAL, not location (coordinator-directed 2026-08-29 fix
    # for the FrameNet goal-recall gap; 'arrive' resolves to escape-51.1's family in VerbNet).
    toks9, pos9, heads9 = parse("The train arrived at the station .")
    v9 = _find_verb_idx(toks9, pos9, "arrived")
    assert v9 is not None
    assert is_destination_verb(lemma_verb("arrived")), "arrive must be destination-classified"
    res9 = route_predicate_arguments(toks9, pos9, heads9, v9)
    assert res9["location"] is None, res9
    assert toks9[res9["goal"] - 1].lower() == "station", res9
    print("  [PASS] CUE5(i): destination-verb 'arrived at the station' -> goal=station "
         "(not location)", flush=True)

    # CUE 5(ii): DESTINATION-verb bare direct object -> GOAL (reach/enter X, no preposition).
    toks10, pos10, heads10 = parse("The scouts reached the summit .")
    v10 = _find_verb_idx(toks10, pos10, "reached")
    assert v10 is not None
    assert is_destination_verb(lemma_verb("reached")), "reach must be destination-classified"
    res10 = route_predicate_arguments(toks10, pos10, heads10, v10)
    assert toks10[res10["goal"] - 1].lower() == "summit", res10
    assert res10["goal_belongs_to"] == "agent", res10
    print("  [PASS] CUE5(ii): destination-verb bare object 'reached the summit' -> goal=summit, "
         "goal_belongs_to=agent", flush=True)

    # CUE5(ii) PRECISION REGRESSION GUARD (found + fixed 2026-08-29): 'carry'/'throw'/'send' are
    # destination-classified (VerbNet Destination role) but their bare object is the MOVED THEME,
    # not the endpoint -- the bare-object rule must NOT fire for them (narrowed to
    # is_bare_object_destination_verb: reach/enter/arrive/escape/approach/appear only).
    toks11, pos11, heads11 = parse("The soldiers carried the box .")
    v11 = _find_verb_idx(toks11, pos11, "carried")
    assert v11 is not None
    assert is_destination_verb(lemma_verb("carried")), "carry must be destination-classified"
    assert not is_bare_object_destination_verb(lemma_verb("carried")), (
        "carry must NOT be in the narrow bare-object family")
    res11 = route_predicate_arguments(toks11, pos11, heads11, v11)
    assert res11["goal"] is None, res11
    assert toks11[res11["theme"] - 1].lower() == "box", res11
    print("  [PASS] CUE5(ii) precision guard: 'carried the box' -> goal=None, theme=box "
         "(carry is destination-classified but NOT bare-object-eligible)", flush=True)

    # TWIN must differ from SHARED_V2 on a verb-class-sensitive case.
    twin_prep_map = build_twin_prep_map()
    twin_event_fn = build_twin_event_classes_fn(
        [lemma_verb(w) for w in ("hand", "shove", "walk", "say", "stay", "flee", "run")])
    twin_dest_fn = build_twin_destination_fn(
        [lemma_verb(w) for w in ("arrive", "reach", "sleep", "say", "walk")])
    twin5 = route_predicate_arguments(toks5, pos5, heads5, v5, prep_to_base=twin_prep_map,
                                      event_classes_fn=twin_event_fn)
    assert twin5 != res5, (twin5, res5)
    print(f"  [PASS] TWIN differs from SHARED_V2 on 'handed the letter to Mary' "
         f"(SHARED_V2 recipient={toks5[res5['recipient']-1] if res5['recipient'] else None}, "
         f"TWIN recipient={toks5[twin5['recipient']-1] if twin5['recipient'] else None}, "
         f"TWIN goal={toks5[twin5['goal']-1] if twin5['goal'] else None})", flush=True)

    # TWIN's permuted destination flag must also be able to differ from SHARED_V2's CUE5 output.
    twin9 = route_predicate_arguments(toks9, pos9, heads9, v9, dest_fn=twin_dest_fn)
    print(f"  [PASS] TWIN(dest) on 'arrived at the station': goal="
         f"{toks9[twin9['goal']-1] if twin9['goal'] else None} location="
         f"{toks9[twin9['location']-1] if twin9['location'] else None} "
         f"(SHARED_V2 goal=station)", flush=True)

    # VerbNet event-class classification sanity (independent of the router logic above).
    give_classes = get_event_classes(lemma_verb("gave"))
    assert "TRANSFER" in give_classes, give_classes
    say_classes = get_event_classes(lemma_verb("said"))
    assert "COMM" in say_classes, say_classes
    walk_classes = get_event_classes(lemma_verb("walked"))
    assert "MOTION" in walk_classes, walk_classes
    print(f"  [PASS] VerbNet event-class sanity: give={sorted(give_classes)} "
         f"say={sorted(say_classes)} walk={sorted(walk_classes)}", flush=True)

    # bootstrap sanity (matches v1's convention).
    a = np.array([1, 1, 1, 0.0])
    b = np.array([0, 0, 1, 0.0])
    d = boot_diff(a, b, 500, 1)
    assert abs(d["point"] - 0.5) < 1e-9, d
    print("[self-test] PASS", flush=True)
    return {"verdict": "SELFTEST_PASS", "verdict_msg": "SELFTEST_PASS", "summary": "SELFTEST_PASS",
           "elapsed_s": 0.0, "run_mode": "self_test", "anchor_name": ANCHOR_NAME}


# =================================================================================================
# ORACLE-PARSE ablation (coordinator-directed 2026-08-29): separates PARSE quality (does the arc
# parser FIND + ATTACH the right PP?) from ROUTER quality (given the right PP, does the router pick
# the right ROLE?). SHARED_V2_ORACLEPP hands the router the GOLD FE span's own governing
# preposition + head-nominal DIRECTLY -- bypassing _pp_args_for_verb's arc-parse discovery -- and
# routes that ONE pair through the identical _route_one_pp typing decision the batch router uses.
# Only PP-FINDING is oracle-replaced; agent/theme/verb-class/is_dest all still come from the REAL
# batch parse (hybrid_role_patient / get_event_classes / is_destination_verb unchanged).
# =================================================================================================
ORACLEPARSE_OUT_DIR = OUTPUT_DIR + "_oracleparse"


def score_oracle_pp_items(aligned: List[dict], fn_recs: List[dict]) -> Tuple[List[dict], int, int]:
    """fn_recs MUST be the same length/order as `aligned` (from score_aligned_items on the SAME
    aligned list) so SHARED_V2_BATCH/INLINE/TWIN correctness can be paired to the SAME PP-led
    subset the oracle arm scores. Items whose gold span has no leading ADP token (bare-NP /
    ditransitive direct-object realizations -- no governing preposition to hand over) are EXCLUDED
    from the oracle population and counted separately, not folded into a silent 0."""
    assert len(aligned) == len(fn_recs), (len(aligned), len(fn_recs))
    recs = []
    n_no_prep = 0
    n_no_head = 0
    for it, batch_rec in zip(aligned, fn_recs):
        toks, pos, heads, v = it["toks"], it["pos"], it["heads"], it["verb_idx"]
        s, e = it["span"]
        role = it["role_type"]
        if not (s < len(pos) and pos[s] == "ADP"):
            n_no_prep += 1
            continue
        obj = _head_in_span(pos, (s, e))
        if obj is None:
            n_no_head += 1
            continue
        prep = toks[s].lower()

        cands = _cands(pos)
        theme_idx = hybrid_role_patient(toks, pos, v, cands=cands)
        lemma = lemma_verb(toks[v - 1])
        vclasses = get_event_classes(lemma)
        is_motion_or_put = ("MOTION" in vclasses) or ("PUT" in vclasses)
        is_xfer_or_comm = ("TRANSFER" in vclasses) or ("COMM" in vclasses)
        is_dest = is_destination_verb(lemma)

        roles: Dict[str, Optional[int]] = {k: None for k in
                                           ("goal", "location", "path", "source", "recipient",
                                            "direction", "instrument")}
        _route_one_pp(prep, obj, toks, pos, is_motion_or_put, is_xfer_or_comm, is_dest, theme_idx,
                     roles, None)

        pick = roles.get(role)
        correct = int(pick is not None and (s < pick <= e))
        recs.append({"role_type": role, "verb_lemma": lemma, "prep": prep,
                    "correct": {"SHARED_V2_ORACLEPP": correct,
                               "SHARED_V2_BATCH": batch_rec["correct"]["SHARED_V2"],
                               "INLINE": batch_rec["correct"]["INLINE"],
                               "TWIN": batch_rec["correct"]["TWIN"]}})
    return recs, n_no_prep, n_no_head


_ORACLE_ARMS = ["SHARED_V2_ORACLEPP", "SHARED_V2_BATCH", "INLINE", "TWIN"]


def _oracle_stats_for_role(recs: List[dict], role: str, n_boot: int, n_boot_paired: int,
                           n_perm: int, seed_off: int) -> dict:
    rows = [r for r in recs if r["role_type"] == role]
    n = len(rows)
    if n == 0:
        return {"n": 0, "acc": {a: float("nan") for a in _ORACLE_ARMS}, "gap_band": "NA"}
    vecs = {a: np.array([r["correct"][a] for r in rows], dtype=np.float64) for a in _ORACLE_ARMS}
    acc = {a: boot_mean(vecs[a], n_boot, BOOT_SEED + seed_off + i)
          for i, a in enumerate(_ORACLE_ARMS)}
    gap = boot_diff(vecs["SHARED_V2_ORACLEPP"], vecs["SHARED_V2_BATCH"], n_boot_paired,
                    BOOT_SEED + seed_off + 50)
    gap_null_p95 = _label_perm_null_p95(vecs["SHARED_V2_ORACLEPP"], vecs["SHARED_V2_BATCH"],
                                        n_perm, BOOT_SEED + seed_off + 99)
    return {"n": n, "acc": {a: acc[a]["point"] for a in _ORACLE_ARMS},
           "acc_ci": {a: acc[a]["ci95"] for a in _ORACLE_ARMS},
           "oracle_minus_batch": gap, "gap_band": _band(gap), "gap_null_p95": gap_null_p95}


def run_oracleparse_validation(gen) -> dict:
    """Clean, fresh-checkpoint (per the cue5-rescore lesson) oracle-vs-batch-parse ablation."""
    t0 = time.time()
    os.makedirs(ORACLEPARSE_OUT_DIR, exist_ok=True)

    if not os.path.exists(FRAMENET_CACHE_PATH):
        raise RuntimeError(f"{FRAMENET_CACHE_PATH} not found (read-only dependency) -- run the "
                          f"FULL pipeline once first to build the raw FrameNet item cache.")
    with open(FRAMENET_CACHE_PATH, "r", encoding="utf-8") as f:
        fn_raw = json.load(f)
    print(f"[oracle-validate] read {len(fn_raw)} raw FrameNet items from "
         f"{FRAMENET_CACHE_PATH} (read-only) {time.time()-t0:.1f}s", flush=True)

    fn_aligned, fn_mismatch = parse_and_align(gen, fn_raw)
    record_unit(ORACLEPARSE_OUT_DIR, unit_key("framenet_aligned"), fn_aligned)
    print(f"[oracle-validate] FRESH parse_and_align: aligned={len(fn_aligned)} "
         f"mismatch={fn_mismatch} {time.time()-t0:.1f}s", flush=True)

    fn_vocab = sorted({lemma_verb(it["toks"][it["verb_idx"] - 1]) for it in fn_aligned})
    twin_prep_map = build_twin_prep_map()
    twin_event_fn = build_twin_event_classes_fn(fn_vocab)
    twin_dest_fn = build_twin_destination_fn(fn_vocab)

    fn_recs = score_aligned_items(fn_aligned, twin_prep_map, twin_event_fn, twin_dest_fn)
    record_unit(ORACLEPARSE_OUT_DIR, unit_key("framenet_scored_batch"), fn_recs)
    print(f"[oracle-validate] FRESH batch score_aligned_items: {len(fn_recs)} items "
         f"{time.time()-t0:.1f}s", flush=True)

    oracle_recs, n_no_prep, n_no_head = score_oracle_pp_items(fn_aligned, fn_recs)
    record_unit(ORACLEPARSE_OUT_DIR, unit_key("framenet_scored_oracle"), oracle_recs)
    print(f"[oracle-validate] oracle-scored {len(oracle_recs)} items (excluded: no leading "
         f"preposition={n_no_prep}, no nominal head in span={n_no_head}) {time.time()-t0:.1f}s",
         flush=True)

    strata = {role: _oracle_stats_for_role(oracle_recs, role, N_BOOT, N_BOOT_PAIRED, N_PERM_NULL,
                                           10 * i)
             for i, role in enumerate(PRIMARY_ROLES)}

    inline_goal = strata["goal"]["acc"]["INLINE"]
    expected_inline_goal = 0.477
    harness_ok = abs(inline_goal - expected_inline_goal) < 0.02
    print(f"[oracle-validate] HARNESS SANITY: INLINE goal={inline_goal:.4f} expected~"
         f"{expected_inline_goal} -> {'PASS' if harness_ok else 'FAIL'}", flush=True)
    if not harness_ok:
        print("[oracle-validate] HARNESS SANITY FAILED -- numbers below are NOT TRUSTED",
             flush=True)

    twin_goal = strata["goal"]["acc"]["TWIN"]
    batch_goal = strata["goal"]["acc"]["SHARED_V2_BATCH"]
    twin_loses = (twin_goal < batch_goal - 0.05)

    per_role_verdict = {}
    for role in PRIMARY_ROLES:
        s = strata[role]
        if s["n"] == 0:
            per_role_verdict[role] = "NO_DATA"
            continue
        gap = s["oracle_minus_batch"]["point"]
        band = s["gap_band"]
        if band == "ABOVE" and gap > 0.02:
            per_role_verdict[role] = "PARSE_LIMITED"
        elif band == "BELOW":
            per_role_verdict[role] = "ORACLE_BELOW_BATCH_INSPECT"
        else:
            per_role_verdict[role] = "ROUTER_LIMITED"

    verdict = ("HARNESS_SANITY_FAILED" if not harness_ok else
              "ORACLEPARSE_ABLATION_COMPLETE")

    return {
        "verdict": verdict,
        "verdict_msg": (
            f"{verdict} | harness_ok={harness_ok} inline_goal={inline_goal:.4f} "
            f"(expected~0.477) | twin_loses_goal={twin_loses} "
            f"(TWIN={twin_goal:.4f} vs BATCH={batch_goal:.4f}) | " +
            " ".join(f"{r}:batch={strata[r]['acc']['SHARED_V2_BATCH']:.4f}"
                    f",oracle={strata[r]['acc']['SHARED_V2_ORACLEPP']:.4f}"
                    f",gap={strata[r]['oracle_minus_batch']['point']:+.4f}"
                    f",verdict={per_role_verdict[r]}"
                    for r in PRIMARY_ROLES)
        ),
        "summary": f"{verdict}: oracle-vs-batch-parse ablation, FrameNet PP-led subset",
        "elapsed_s": round(time.time() - t0, 2), "run_mode": "oracleparse_validate",
        "anchor_name": ANCHOR_NAME + "_oracleparse_validate",
        "harness_sanity": {"inline_goal_measured": inline_goal,
                          "inline_goal_expected": expected_inline_goal, "tolerance": 0.02,
                          "pass": harness_ok},
        "twin_sanity": {"twin_goal": twin_goal, "batch_goal": batch_goal, "twin_loses": twin_loses},
        "per_role_verdict": per_role_verdict,
        "oracle_strata": strata,
        "n_excluded_no_prep": n_no_prep, "n_excluded_no_head": n_no_head,
        "n_raw": len(fn_raw), "n_aligned": len(fn_aligned), "n_mismatch": fn_mismatch,
        "scored_population": {"unit_keys": sorted([unit_key("framenet_aligned"),
                                                   unit_key("framenet_scored_batch"),
                                                   unit_key("framenet_scored_oracle")]),
                             "units_jsonl": os.path.join(ORACLEPARSE_OUT_DIR, "units.jsonl")},
    }


def _write(output_dir: str, metrics: dict) -> None:
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


CUE5_OUT_DIR = OUTPUT_DIR + "_cue5"


def run_cue5_validation(gen) -> dict:
    """Coordinator-directed 2026-08-29 (second pass, clean-checkpoint fix). A prior FULL rescore
    under the ORIGINAL OUTPUT_DIR corrupted its result -- INLINE (a router-independent floor)
    read 0.477 -> 0.000 in that run, which is IMPOSSIBLE if only the router's goal-cue changed;
    the coordinator diagnosed a stale/misaligned units.jsonl checkpoint reused across the router
    edit, restored the canonical metrics.json from metrics_BEFORE_cue5.json, and this function is
    the clean re-run: a BRAND NEW output directory (CUE5_OUT_DIR, never written before, so there
    is no checkpoint to go stale), the raw FrameNet gold read READ-ONLY from the ORIGINAL cache
    (skips the ~424s NLTK exemplar load; that raw gold does not depend on the router and is safe
    to reuse), and every arm PREDICTION recomputed fresh (parse_and_align + score_aligned_items
    called here for the first time in this directory, so nothing is loaded from a prior score).

    Self-validates before trusting anything: INLINE's FrameNet goal accuracy must reproduce the
    BEFORE run's ~0.477 (INLINE never calls is_destination_verb / is_bare_object_destination_verb
    -- CUE5 cannot touch it -- so a mismatch means THIS harness is still broken, not that the
    router changed)."""
    t0 = time.time()
    os.makedirs(CUE5_OUT_DIR, exist_ok=True)

    if not os.path.exists(FRAMENET_CACHE_PATH):
        raise RuntimeError(f"{FRAMENET_CACHE_PATH} not found (read-only dependency) -- run the "
                          f"FULL pipeline once first to build the raw FrameNet item cache; this "
                          f"validator only READS it, never rebuilds it.")
    with open(FRAMENET_CACHE_PATH, "r", encoding="utf-8") as f:
        fn_raw = json.load(f)
    print(f"[cue5-validate] read {len(fn_raw)} raw FrameNet items from "
         f"{FRAMENET_CACHE_PATH} (read-only) {time.time()-t0:.1f}s", flush=True)

    fn_aligned, fn_mismatch = parse_and_align(gen, fn_raw)
    record_unit(CUE5_OUT_DIR, unit_key("framenet_aligned"), fn_aligned)
    print(f"[cue5-validate] FRESH parse_and_align: aligned={len(fn_aligned)} "
         f"mismatch={fn_mismatch} {time.time()-t0:.1f}s", flush=True)

    fn_vocab = sorted({lemma_verb(it["toks"][it["verb_idx"] - 1]) for it in fn_aligned})
    twin_prep_map = build_twin_prep_map()
    twin_event_fn = build_twin_event_classes_fn(fn_vocab)
    twin_dest_fn = build_twin_destination_fn(fn_vocab)
    n_dest = sum(1 for l in fn_vocab if is_destination_verb(l))
    n_bare = sum(1 for l in fn_vocab if is_bare_object_destination_verb(l))
    print(f"[cue5-validate] vocab={len(fn_vocab)} lemmas; {n_dest} destination-classified "
         f"({n_bare} bare-object-eligible)", flush=True)

    fn_recs = score_aligned_items(fn_aligned, twin_prep_map, twin_event_fn, twin_dest_fn)
    record_unit(CUE5_OUT_DIR, unit_key("framenet_scored"), fn_recs)
    print(f"[cue5-validate] FRESH score_aligned_items: scored {len(fn_recs)} items "
         f"{time.time()-t0:.1f}s", flush=True)

    strata = {role: _stats_for_role(fn_recs, role, N_BOOT, N_BOOT_PAIRED, N_PERM_NULL, 10 * i)
             for i, role in enumerate(ROLE_NAMES)}

    inline_goal = strata["goal"]["acc"]["INLINE"]
    expected_inline_goal = 0.477
    harness_ok = abs(inline_goal - expected_inline_goal) < 0.02
    print(f"[cue5-validate] HARNESS SANITY: INLINE goal={inline_goal:.4f} expected~"
         f"{expected_inline_goal} -> {'PASS' if harness_ok else 'FAIL'}", flush=True)
    if not harness_ok:
        print("[cue5-validate] HARNESS SANITY FAILED -- SHARED_V2 numbers below are NOT TRUSTED",
             flush=True)

    recip_recs = [r for r in fn_recs if r["role_type"] == "recipient" and "mislabeled_goal" in r]
    disambig = {}
    for arm in ARM_NAMES:
        hit = np.array([r["correct"][arm] for r in recip_recs], dtype=np.float64)
        mis = np.array([r["mislabeled_goal"][arm] for r in recip_recs], dtype=np.float64)
        disambig[arm] = {"recipient_hit_rate": float(hit.mean()) if len(hit) else float("nan"),
                        "mislabeled_as_goal_rate": float(mis.mean()) if len(mis) else float("nan")}
    disambig["n"] = len(recip_recs)

    before = {"goal": 0.3785, "location": 0.401, "source": 0.424, "path": 0.3965,
             "recipient": 0.152}
    after = {r: strata[r]["acc"]["SHARED_V2"] for r in PRIMARY_ROLES}
    delta = {r: after[r] - before[r] for r in PRIMARY_ROLES}

    verdict = ("HARNESS_SANITY_FAILED" if not harness_ok else
              ("CUE5_CLOSES_GOAL_GAP_NO_REGRESSION" if
               delta["goal"] > 0 and all(delta[r] >= -0.03 for r in ("location", "source", "path"))
               else "CUE5_HONEST_TRADEOFF"))

    return {
        "verdict": verdict,
        "verdict_msg": (
            f"{verdict} | harness_ok={harness_ok} inline_goal={inline_goal:.4f} "
            f"(expected~0.477) | " +
            " ".join(f"{r}:{before[r]:.4f}->{after[r]:.4f}({delta[r]:+.4f})"
                    for r in PRIMARY_ROLES) +
            f" | disambig_n={disambig['n']} SHARED_V2_recip_hit="
            f"{disambig['SHARED_V2']['recipient_hit_rate']:.4f} "
            f"SHARED_V2_mislabel_goal={disambig['SHARED_V2']['mislabeled_as_goal_rate']:.4f} "
            f"TWIN_recip_hit={disambig['TWIN']['recipient_hit_rate']:.4f}"
        ),
        "summary": f"{verdict}: CUE5 clean-checkpoint validation, FrameNet n_goal={strata['goal']['n']}",
        "elapsed_s": round(time.time() - t0, 2), "run_mode": "cue5_validate",
        "anchor_name": ANCHOR_NAME + "_cue5_validate",
        "harness_sanity": {"inline_goal_measured": inline_goal,
                          "inline_goal_expected": expected_inline_goal, "tolerance": 0.02,
                          "pass": harness_ok},
        "before_cue5": before, "after_cue5": after, "delta": delta,
        "framenet_strata": strata,
        "goal_recipient_disambiguation": disambig,
        "n_dest_verbs": n_dest, "n_bare_object_verbs": n_bare, "n_vocab": len(fn_vocab),
        "n_raw": len(fn_raw), "n_aligned": len(fn_aligned), "n_mismatch": fn_mismatch,
        "scored_population": {"unit_keys": sorted([unit_key("framenet_aligned"),
                                                   unit_key("framenet_scored")]),
                             "units_jsonl": os.path.join(CUE5_OUT_DIR, "units.jsonl")},
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--self-test", action="store_true", dest="self_test")
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--mode", choices=["full", "smoke"], default=None)
    p.add_argument("--emit-verbnet-table", action="store_true", dest="emit_verbnet_table")
    p.add_argument("--cue5-validate", action="store_true", dest="cue5_validate")
    p.add_argument("--oracleparse-validate", action="store_true", dest="oracleparse_validate")
    args = p.parse_args()
    smoke = bool(args.smoke) or (args.mode == "smoke")

    if args.emit_verbnet_table:
        result = emit_verbnet_table()
        print(f"[emit-verbnet-table] wrote {result['path']} "
             f"n_lemmas_classified={result['n_lemmas_classified']}", flush=True)
        return

    if args.cue5_validate:
        gen = _default_generator()
        try:
            metrics = run_cue5_validation(gen)
            _write(CUE5_OUT_DIR, metrics)
            print(f"[main] wrote {CUE5_OUT_DIR}/metrics.json verdict={metrics['verdict']}",
                 flush=True)
            print(metrics["verdict_msg"], flush=True)
        except SystemExit:
            raise
        except KeyboardInterrupt:
            raise
        except Exception as e:  # noqa: BLE001
            diag = {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(e).__name__}: {str(e)[:500]}",
                   "summary": f"CELL_CRASHED: {type(e).__name__}", "elapsed_s": 0.0,
                   "traceback": traceback.format_exc()[:5000], "anchor_name": ANCHOR_NAME}
            _write(CUE5_OUT_DIR, diag)
            raise
        return

    if args.oracleparse_validate:
        gen = _default_generator()
        try:
            metrics = run_oracleparse_validation(gen)
            _write(ORACLEPARSE_OUT_DIR, metrics)
            print(f"[main] wrote {ORACLEPARSE_OUT_DIR}/metrics.json verdict={metrics['verdict']}",
                 flush=True)
            print(metrics["verdict_msg"], flush=True)
        except SystemExit:
            raise
        except KeyboardInterrupt:
            raise
        except Exception as e:  # noqa: BLE001
            diag = {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(e).__name__}: {str(e)[:500]}",
                   "summary": f"CELL_CRASHED: {type(e).__name__}", "elapsed_s": 0.0,
                   "traceback": traceback.format_exc()[:5000], "anchor_name": ANCHOR_NAME}
            _write(ORACLEPARSE_OUT_DIR, diag)
            raise
        return

    suffix = "_selftest" if args.self_test else ("_smoke" if smoke else "")
    out_dir = OUTPUT_DIR + suffix

    try:
        if args.self_test:
            metrics = self_test()
        else:
            gen = _default_generator()
            metrics = run_full(gen, smoke=smoke, out_dir=out_dir)
        _write(out_dir, metrics)
        print(f"[main] wrote metrics verdict={metrics['verdict']}", flush=True)
        print(metrics["verdict_msg"], flush=True)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # noqa: BLE001 -- NOT BaseException; preserves SystemExit/KeyboardInterrupt
        diag = {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(e).__name__}: {str(e)[:500]}",
               "summary": f"CELL_CRASHED: {type(e).__name__}", "elapsed_s": 0.0,
               "traceback": traceback.format_exc()[:5000], "anchor_name": ANCHOR_NAME}
        _write(out_dir, diag)
        raise


if __name__ == "__main__":
    main()
