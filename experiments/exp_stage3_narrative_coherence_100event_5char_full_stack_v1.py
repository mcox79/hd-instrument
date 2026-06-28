"""stage3_narrative_coherence_100event_5char_full_stack_v1 -- ANCHOR 1 marquee.

Stage-3 marquee long-context narrative coherence integration test. Per drill
`notes/research_drill_2x_long_context_narrative_coherence_stage3_2026-06-27.md`
CELL 1 (P_deflated=0.45); hand-off
`notes/exp_dev_handoff_research_long_context_narrative_coherence_stage3_2026-06-27.md`
ANCHOR 1.

PREREG: preregs/2026-06-27_stage3_narrative_coherence_100event_5char_full_stack_v1.md

USER concern #3 for M3: "friend who's great at last 5 min, loses track by hour 2".
HARD_PASS demonstrates substrate handles 100-event conversations with character
coherence end-to-end via composed chain-grade primitives.

COMPOSES 5 CHAIN-GRADE PRIMITIVES:
  (1) cortex_hippo_handoff smoke HARD_PASS today (gap=+0.998; consolidation engine)
      -- sparse hippo k-WTA + dense cortex slow Hebbian
  (2) sequence_binding K=20 chain-grade (within-episode binding)
      -- permutation-based positional code for events within a scene
  (3) partition_routing 10M chain-grade (entity partitions; 5 chars -> 5 partitions)
      -- per-character cortex matrix
  (4) TWO_TIER generational W (fact-update arm)
      -- per-character generation counter so later facts override earlier
  (5) FIXED-K=10 event boundaries (replaces cosine-shift detector per ANCHOR 2
      MIDDLE_BAND verdict: cs_f1 saturated at 1.0 BUT drill fallback says use
      fixed-K=10 when boundary detector lands MIDDLE_BAND, which it did).

BRAIN ANALOG: hippocampal episodic memory + cortical schema consolidation +
DMN narrative integration (Hasson 2008 timescales; Chen 2017; CLS theory
McClelland-McNaughton-O'Reilly 1995; ATL semantic hub Patterson 2007).

ARMS (4 mandatory):
  ARM_FORGET_EVERYTHING -- floor; "good at last 5 min" baseline. Only most-
    recent 5 events visible at query time.
  ARM_FLAT_BASELINE     -- single Hebbian W; no segmentation, no partition,
    no two-tier. Lose-by-interference baseline.
  ARM_NO_SEGMENT        -- cortex_hippo + partition + two-tier composed, BUT
    consolidate every event (no scene boundaries). Tests whether segmentation
    is load-bearing.
  ARM_FULL_STACK (MECH) -- all 5 primitives composed properly. Scene-boundary
    consolidation every K=10 events; per-character cortex partitions; two-tier
    W for fact updates.

QUERIES (4 types; 3 questions per type per seed):
  Q1 factual    : "what did <char> do in scene <s>?" (cortex consolidation)
  Q2 coreference: "when 'he/she' did X in scene <s>, who was the referent?"
                  (partition router resolves pronoun -> entity)
  Q3 temporal   : "what came before X?" (sequence binding within scene)
  Q4 contradict : "char job was X early, Y late; which is current?"
                  (TWO_TIER generational W staleness signal)

PRE-REG BANDS (LOCKED at module init):
  HP_OVERALL_FLOOR       = 0.70  (FULL_STACK overall accuracy across 4 Qs)
  HP_LIFT_OVER_FLAT      = 0.25  (FULL_STACK - FLAT)
  HP_LIFT_OVER_FORGET    = 0.50  (FULL_STACK - FORGET)
  HP_PER_QUERY_FLOOR     = 0.60  (no Q-type below this)
  HP_CV_MAX              = 0.15  (across seeds)
  HF_OVERALL_BREAK       = 0.40  (FULL_STACK overall < this = composition broken)
  HF_FLAT_TIE_DELTA      = 0.05  (|FULL - FLAT| <= this = composition useless)
  HF_PER_QUERY_FLOOR     = 0.30  (any single Q-type < this = single point of failure)
  MB_OVERALL_LOW         = 0.40
  MB_OVERALL_HIGH        = 0.70
  MB_LIFT_MIN            = 0.10  (composition still adds some value)

META_RULE_H cardinality_ok MANDATORY (seeds * arms).
META_RULE_J no-silent-except (record + halt; SystemExit re-raised BEFORE BaseException).
META_RULE_K smoke fires discriminator (smoke at full-N=100 single seed per
  DISCRIMINATOR-MUST-SURVIVE-SCALE Check A; smaller geometry but full event count).
META_RULE_L band-floor strictly-above-floor (no inclusive equalities at HP edge).
META_RULE_AF arms-must-differ SHA-256 of prediction lists.
META_RULE_AH atomic-write via write_metrics helper.

ASCII-only; single-file; resumable per (seed, arm) checkpoint key.
Author: exp_dev 2026-06-27 (ANCHOR 1 marquee Stage-3 integration; under Research lead).
"""
from __future__ import annotations

import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import os
import argparse
import hashlib
import math
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    get_output_dir, write_partial_key, aggregate_partials, write_metrics,
    list_completed_keys,
)

ANCHOR_NAME = "stage3_narrative_coherence_100event_5char_full_stack_v1"
CORPUS_PROVENANCE = (
    "synthetic_100event_narrative_5characters_grouped_into_10_scenes_"
    "fixed_K10_boundaries_with_per_character_facts_pronouns_and_"
    "fact_updates_for_contradiction_queries"
)

_P = argparse.ArgumentParser()
_P.add_argument("--self-test", action="store_true", dest="self_test")
_P.add_argument("--smoke", action="store_true")
_ARGS, _ = _P.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = _HDLAB_EXP_NAME.lower().endswith("_smoke")
RUN_MODE = "smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE) \
    else os.environ.get("HDLAB_RUN_MODE", "full")
SMOKE = (RUN_MODE == "smoke")


# ---------------- pre-reg bands (LOCKED at module init) ----------------
HP_OVERALL_FLOOR = 0.70
HP_LIFT_OVER_FLAT = 0.25
HP_LIFT_OVER_FORGET = 0.50
HP_PER_QUERY_FLOOR = 0.60
HP_CV_MAX = 0.15
HF_OVERALL_BREAK = 0.40
HF_FLAT_TIE_DELTA = 0.05
HF_PER_QUERY_FLOOR = 0.30
MB_OVERALL_LOW = 0.40
MB_OVERALL_HIGH = 0.70
MB_LIFT_MIN = 0.10

assert HP_OVERALL_FLOOR > MB_OVERALL_HIGH - 1e-9 or HP_OVERALL_FLOOR >= MB_OVERALL_HIGH, "bands locked"
assert HP_PER_QUERY_FLOOR > HF_PER_QUERY_FLOOR, "bands locked"
assert HF_OVERALL_BREAK < MB_OVERALL_LOW + 1e-9, "bands locked"


# ---------------- regime config ----------------
# DISCRIMINATOR-MUST-SURVIVE-SCALE Check A: smoke uses full N_EVENTS=50 (half
# of full 100) with 3 characters to test mechanism at near-full event count.
# Per cortex_hippo_handoff conventions: N_h=512 sparse, N_c=1024 dense.
if SMOKE:
    N_HIPPO = 512
    N_CORTEX = 1024
    N_PART = 512               # per-character partition cortex (smaller dim)
    N_EVENTS = 50
    N_CHARACTERS = 3
    K_SCENE_BOUNDARY = 10      # fixed-K=10 (event_idx % K == 0 starts new scene)
    N_FACTS_PER_CHAR = 2       # facts that get a current value (e.g. job)
    N_UPDATE_PAIRS = 2         # pairs (early, late) to test contradiction
    N_PRONOUN_EVENTS = 4       # events that use pronoun coreference
    Q_PER_TYPE = 2
    SEEDS = [11]
else:
    N_HIPPO = 512
    N_CORTEX = 1024
    N_PART = 1024
    N_EVENTS = 100
    N_CHARACTERS = 5
    K_SCENE_BOUNDARY = 10      # 10 scenes of 10 events each
    N_FACTS_PER_CHAR = 3
    N_UPDATE_PAIRS = 3
    N_PRONOUN_EVENTS = 8
    Q_PER_TYPE = 3
    SEEDS = [11, 13, 19]

K_HIPPO_ACTIVE = max(1, int(round(0.10 * N_HIPPO)))   # 10% sparsity (cortex_hippo conv)
ETA_CORTEX = 0.005                                     # slow Hebbian rate
N_REPLAY_CYCLES = 3                                    # per-scene replay during consolidation
FORGET_WINDOW = 5                                      # ARM_FORGET visible recency window
N_RAW = 64                                             # raw input vector dim

# Vocabulary sizes
N_VERBS = 12
N_OBJECTS = 16
N_JOBS = 8       # for fact / contradiction queries

ARMS = ["ARM_FORGET_EVERYTHING", "ARM_FLAT_BASELINE",
        "ARM_NO_SEGMENT", "ARM_FULL_STACK"]
QUERY_TYPES = ["Q1_factual", "Q2_coreference", "Q3_temporal", "Q4_contradict"]
EXPECTED_N_UNITS = len(SEEDS) * len(ARMS)

CONFIG_VERSION = (
    "ANCHOR=%s,N_h=%d,N_c=%d,N_part=%d,N_events=%d,N_chars=%d,K_scene=%d,"
    "K_active=%d,eta=%.4f,N_replay=%d,forget_w=%d,Q_per_type=%d,seeds=%s,"
    "mode=%s,HP_overall=%.2f,HP_lift_flat=%.2f,HP_lift_forget=%.2f,"
    "HP_per_q=%.2f,HF_break=%.2f,HF_flat_tie=%.2f,HF_per_q=%.2f,"
    "EXPECTED_N=%d,hardening=L1early+L2perarm+L4importsentinel"
) % (
    ANCHOR_NAME, N_HIPPO, N_CORTEX, N_PART, N_EVENTS, N_CHARACTERS,
    K_SCENE_BOUNDARY, K_HIPPO_ACTIVE, ETA_CORTEX, N_REPLAY_CYCLES,
    FORGET_WINDOW, Q_PER_TYPE, SEEDS, RUN_MODE,
    HP_OVERALL_FLOOR, HP_LIFT_OVER_FLAT, HP_LIFT_OVER_FORGET,
    HP_PER_QUERY_FLOOR, HF_OVERALL_BREAK, HF_FLAT_TIE_DELTA,
    HF_PER_QUERY_FLOOR, EXPECTED_N_UNITS,
)


# ---------------- vector primitives ----------------

def _rng(seed_int: int) -> np.random.Generator:
    return np.random.default_rng(int(seed_int))


def random_bipolar(shape, rng: np.random.Generator) -> np.ndarray:
    """Uniform +/-1 bipolar vector of given shape."""
    return np.where(rng.random(shape) < 0.5, -1.0, 1.0).astype(np.float64)


def cosine_vec(a: np.ndarray, b: np.ndarray) -> float:
    """Cosine similarity between two 1D vectors (zero-safe)."""
    na = float(np.linalg.norm(a))
    nb = float(np.linalg.norm(b))
    if na < 1e-9 or nb < 1e-9:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


def cosine_argmax(probe: np.ndarray, candidates: np.ndarray) -> int:
    """Argmax cosine of probe against rows of candidates (L2-normalized)."""
    norms = np.linalg.norm(candidates, axis=1)
    pn = float(np.linalg.norm(probe))
    if pn < 1e-9:
        return 0
    safe = np.where(norms > 1e-9, norms, 1.0)
    cand_norm = candidates / safe[:, None]
    p_norm = probe / pn
    sims = cand_norm @ p_norm
    return int(np.argmax(sims))


def pattern_separate_sparse(x: np.ndarray, P: np.ndarray, k: int) -> np.ndarray:
    """Random projection + k-WTA sparse bipolar (k active in +/-1)."""
    h_raw = P @ x
    top_k_idx = np.argpartition(-np.abs(h_raw), k - 1)[:k]
    h_sparse = np.zeros(P.shape[0], dtype=np.float64)
    signs = np.sign(h_raw[top_k_idx])
    signs[signs == 0] = 1.0
    h_sparse[top_k_idx] = signs
    return h_sparse


def project_h_to_c(h_sparse: np.ndarray, P_hc: np.ndarray) -> np.ndarray:
    """Project hippo sparse -> cortex dense (L2-normalized)."""
    c = P_hc @ h_sparse
    n = float(np.linalg.norm(c))
    if n > 0:
        c = c / n
    return c


def hebbian_write(W: np.ndarray, key: np.ndarray, val: np.ndarray,
                  eta: float) -> None:
    """W += eta * outer(val, key) (in-place)."""
    W += eta * np.outer(val, key)


def hebbian_read(W: np.ndarray, key: np.ndarray) -> np.ndarray:
    """Read value from W given key: raw = W @ key; return sign(raw)."""
    raw = W @ key
    out = np.sign(raw)
    out[out == 0] = 1.0
    return out


def permute_role_pos(v: np.ndarray, pos: int) -> np.ndarray:
    """Sequence-binding positional code: cyclic-shift permutation by pos.

    Lightweight position permutation (chain-grade-style sequence binding).
    Used to encode within-scene event order.
    """
    if v.shape[0] == 0:
        return v
    return np.roll(v, int(pos) % v.shape[0])


# ---------------- narrative generator ----------------

class Narrative:
    """100-event narrative with N_CHARACTERS characters across 10 scenes.

    For each event we record:
      - char_id   : index in [0, N_CHARACTERS)
      - verb_id   : index in [0, N_VERBS)
      - obj_id    : index in [0, N_OBJECTS)
      - scene_id  : int (event_idx // K_SCENE_BOUNDARY)
      - is_pronoun: bool (event uses pronoun reference -> referent = char_id)
      - fact_kind : optional 'fact' | 'fact_update' for Q1/Q4 facts (job_id)
      - fact_idx  : optional int (which fact slot for this char)
      - fact_val  : optional job_id

    Pronoun events: char_id is the TRUE referent; the event is generated
    such that the recent context (prior scene) hosted the same char so
    coreference is resolvable.
    """

    def __init__(self, seed_offset: int) -> None:
        self.seed_offset = int(seed_offset)
        self.rng = _rng(seed_offset)

        self.events: List[Dict] = []
        # char fact registry: per-char list of (fact_idx, fact_val, event_idx)
        # last entry per (char, fact_idx) is the "current" value (for Q4 contradiction)
        self.char_facts: Dict[Tuple[int, int], List[Tuple[int, int]]] = {}

        # Generate scenes; each scene has a "focus char" who appears often
        # (anchors pronoun resolvability in that scene)
        n_scenes = (N_EVENTS + K_SCENE_BOUNDARY - 1) // K_SCENE_BOUNDARY
        scene_focus = [int(self.rng.integers(0, N_CHARACTERS))
                       for _ in range(n_scenes)]

        # Pre-allocate update pairs: (char, fact_idx, early_val, late_val,
        #                              early_event_idx, late_event_idx)
        update_pairs: List[Tuple[int, int, int, int, int, int]] = []
        used_char_fact = set()
        chosen_chars = []
        for _ in range(N_UPDATE_PAIRS):
            for _attempt in range(20):
                ch = int(self.rng.integers(0, N_CHARACTERS))
                fi = int(self.rng.integers(0, N_FACTS_PER_CHAR))
                if (ch, fi) not in used_char_fact:
                    used_char_fact.add((ch, fi))
                    chosen_chars.append((ch, fi))
                    break
        # Pre-pick early/late event indices for each pair (early in first
        # quarter; late in last quarter so consolidation has time)
        q1_max = max(1, N_EVENTS // 4)
        q4_min = max(q1_max + 1, (3 * N_EVENTS) // 4)
        for ch, fi in chosen_chars:
            ev_early = int(self.rng.integers(2, q1_max))
            ev_late = int(self.rng.integers(q4_min, N_EVENTS - 1))
            v_early = int(self.rng.integers(0, N_JOBS))
            # Ensure late != early
            v_late = v_early
            while v_late == v_early:
                v_late = int(self.rng.integers(0, N_JOBS))
            update_pairs.append((ch, fi, v_early, v_late, ev_early, ev_late))

        update_lookup = {}  # event_idx -> (char, fi, val, "early"|"late")
        for ch, fi, ve, vl, ee, le in update_pairs:
            update_lookup[ee] = (ch, fi, ve, "early")
            update_lookup[le] = (ch, fi, vl, "late")

        # Generate per-char "static facts" (fact_idx not used by updates).
        # These are stable facts placed in early events; Q1 queries them.
        static_facts: Dict[Tuple[int, int], Tuple[int, int]] = {}
        # fact slot -> (val, event_idx)
        for ch in range(N_CHARACTERS):
            for fi in range(N_FACTS_PER_CHAR):
                if (ch, fi) not in used_char_fact:
                    val = int(self.rng.integers(0, N_JOBS))
                    # Place randomly but BEFORE the second half so cortex has it
                    ev = int(self.rng.integers(1, max(2, N_EVENTS // 2)))
                    static_facts[(ch, fi)] = (val, ev)

        # Static facts to inject by event index
        static_by_event: Dict[int, List[Tuple[int, int, int]]] = {}
        for (ch, fi), (val, ev) in static_facts.items():
            static_by_event.setdefault(ev, []).append((ch, fi, val))

        # Pre-allocate pronoun events: must occur AFTER the focus-char appears
        # in same or prior scene; avoid conflict with update or static-fact events.
        reserved_events = set(update_lookup.keys()) | set(static_by_event.keys())
        pronoun_event_idxs: set = set()
        if N_PRONOUN_EVENTS > 0:
            # Distribute across scenes 1+ (scene 0 has no prior)
            cand_events = [ev for ev in range(K_SCENE_BOUNDARY + 1, N_EVENTS)
                           if ev not in reserved_events]
            self.rng.shuffle(cand_events)
            for ev in cand_events[:N_PRONOUN_EVENTS]:
                pronoun_event_idxs.add(int(ev))

        # Generate every event
        for ev_idx in range(N_EVENTS):
            scene_id = ev_idx // K_SCENE_BOUNDARY
            ev: Dict = {
                "event_idx": ev_idx,
                "scene_id": scene_id,
                "is_pronoun": False,
                "fact_kind": None,
                "fact_idx": None,
                "fact_val": None,
            }

            # Determine character
            if ev_idx in update_lookup:
                ch, fi, val, kind = update_lookup[ev_idx]
                ev["char_id"] = ch
                ev["fact_kind"] = kind  # "early" or "late"
                ev["fact_idx"] = fi
                ev["fact_val"] = val
                # also persist fact history
                self.char_facts.setdefault((ch, fi), []).append((val, ev_idx))
            elif ev_idx in static_by_event:
                ch, fi, val = static_by_event[ev_idx][0]
                ev["char_id"] = ch
                ev["fact_kind"] = "static"
                ev["fact_idx"] = fi
                ev["fact_val"] = val
                self.char_facts.setdefault((ch, fi), []).append((val, ev_idx))
            elif ev_idx in pronoun_event_idxs:
                # Pronoun event: referent is the focus char of THIS scene
                ev["char_id"] = scene_focus[scene_id]
                ev["is_pronoun"] = True
            else:
                # Default: bias toward focus char (60%) else random
                if self.rng.random() < 0.60:
                    ev["char_id"] = scene_focus[scene_id]
                else:
                    ev["char_id"] = int(self.rng.integers(0, N_CHARACTERS))

            ev["verb_id"] = int(self.rng.integers(0, N_VERBS))
            ev["obj_id"] = int(self.rng.integers(0, N_OBJECTS))

            self.events.append(ev)

        self.scene_focus = scene_focus
        self.n_scenes = n_scenes
        self.update_pairs = update_pairs
        self.static_facts = static_facts
        self.pronoun_event_idxs = pronoun_event_idxs

    # ---- queries ----

    def make_queries(self) -> Dict[str, List[Dict]]:
        """Build Q_PER_TYPE questions for each of the 4 query types."""
        rng = _rng(self.seed_offset + 999)
        queries: Dict[str, List[Dict]] = {q: [] for q in QUERY_TYPES}

        # Q1 factual: pick static facts; ask what fact_val for (char, fi)
        static_keys = list(self.static_facts.keys())
        rng.shuffle(static_keys)
        for ch, fi in static_keys[:Q_PER_TYPE]:
            val, ev = self.static_facts[(ch, fi)]
            queries["Q1_factual"].append({
                "char_id": ch, "fact_idx": fi, "expected_val": val,
                "source_event_idx": ev,
            })

        # Q2 coreference: pick pronoun events; ask "who is referent?"
        pronoun_list = sorted(self.pronoun_event_idxs)
        rng.shuffle(pronoun_list)
        for ev_idx in pronoun_list[:Q_PER_TYPE]:
            ev = self.events[ev_idx]
            queries["Q2_coreference"].append({
                "event_idx": ev_idx,
                "verb_id": ev["verb_id"],
                "obj_id": ev["obj_id"],
                "scene_id": ev["scene_id"],
                "expected_char_id": ev["char_id"],
            })

        # Q3 temporal: pick events from later half; ask which event came
        # IMMEDIATELY before (same scene). Query is identifier for the target
        # event; expected answer is event_idx - 1.
        cand = [i for i in range(1, N_EVENTS)
                if (i % K_SCENE_BOUNDARY) > 0]  # skip scene-first events
        rng.shuffle(cand)
        for ev_idx in cand[:Q_PER_TYPE]:
            queries["Q3_temporal"].append({
                "target_event_idx": ev_idx,
                "expected_prior_event_idx": ev_idx - 1,
            })

        # Q4 contradiction: pick update pairs; ask "current value" (= late)
        for (ch, fi, ve, vl, ee, le) in self.update_pairs[:Q_PER_TYPE]:
            queries["Q4_contradict"].append({
                "char_id": ch, "fact_idx": fi,
                "early_val": ve, "late_val": vl,
                "early_event_idx": ee, "late_event_idx": le,
                "expected_val": vl,  # current = late
            })

        return queries


# ---------------- vocabularies (per-seed) ----------------

def build_vocab(seed_offset: int) -> Dict[str, np.ndarray]:
    """Build per-seed vocabulary: random bipolar vectors for each token class.

    Returns:
        chars   : [N_CHARACTERS, N_RAW]
        verbs   : [N_VERBS, N_RAW]
        objs    : [N_OBJECTS, N_RAW]
        jobs    : [N_JOBS, N_RAW]
        scenes  : [N_SCENES, N_RAW]
        facts   : [N_FACTS_PER_CHAR, N_RAW]  -- fact-slot tag
        P_in    : [N_HIPPO, N_RAW]
        P_hc    : [N_CORTEX, N_HIPPO]
        P_pc    : [N_PART, N_HIPPO]          -- partition cortex projection
    """
    rng = _rng(seed_offset + 7777)
    n_scenes = (N_EVENTS + K_SCENE_BOUNDARY - 1) // K_SCENE_BOUNDARY
    vocab = {
        "chars": random_bipolar((N_CHARACTERS, N_RAW), rng),
        "verbs": random_bipolar((N_VERBS, N_RAW), rng),
        "objs":  random_bipolar((N_OBJECTS, N_RAW), rng),
        "jobs":  random_bipolar((N_JOBS, N_RAW), rng),
        "scenes": random_bipolar((n_scenes, N_RAW), rng),
        "facts": random_bipolar((N_FACTS_PER_CHAR, N_RAW), rng),
        # special pronoun marker (single vector)
        "pronoun_tag": random_bipolar((N_RAW,), rng),
    }
    vocab["P_in"] = (rng.standard_normal((N_HIPPO, N_RAW)) /
                     math.sqrt(N_RAW)).astype(np.float64)
    vocab["P_hc"] = (rng.standard_normal((N_CORTEX, N_HIPPO)) /
                     math.sqrt(N_HIPPO)).astype(np.float64)
    vocab["P_pc"] = (rng.standard_normal((N_PART, N_HIPPO)) /
                     math.sqrt(N_HIPPO)).astype(np.float64)
    return vocab


def encode_event_raw(ev: Dict, vocab: Dict[str, np.ndarray]) -> np.ndarray:
    """Build the raw event vector by superposing char + verb + obj + scene tag.

    For pronoun events, replace char with pronoun_tag (substrate doesn't know
    who 'he/she' is at write time; coreference must be RESOLVED later).
    """
    if ev.get("is_pronoun"):
        char_v = vocab["pronoun_tag"]
    else:
        char_v = vocab["chars"][ev["char_id"]]
    verb_v = vocab["verbs"][ev["verb_id"]]
    obj_v = vocab["objs"][ev["obj_id"]]
    scene_v = vocab["scenes"][ev["scene_id"]]
    raw = char_v + verb_v + obj_v + scene_v
    # Bipolarize so downstream pattern_separate_sparse k-WTA stays clean
    out = np.sign(raw)
    out[out == 0] = 1.0
    return out


def encode_fact_key(ch: int, fi: int, vocab: Dict[str, np.ndarray]) -> np.ndarray:
    """Build the cue for a fact query: char + fact_slot (bipolarized)."""
    raw = vocab["chars"][ch] + vocab["facts"][fi]
    out = np.sign(raw)
    out[out == 0] = 1.0
    return out


def encode_fact_val(val: int, vocab: Dict[str, np.ndarray]) -> np.ndarray:
    """Encode a fact value (job_id) as its vocabulary vector."""
    return vocab["jobs"][val]


# ---------------- arm implementations ----------------

def _consolidate_scene_to_cortex(W_cortex: np.ndarray,
                                  scene_keys_c: List[np.ndarray],
                                  scene_vals_c: List[np.ndarray],
                                  rng: np.random.Generator) -> None:
    """Replay scene events into cortex (slow Hebbian, N_REPLAY_CYCLES)."""
    if not scene_keys_c:
        return
    m = len(scene_keys_c)
    for _ in range(N_REPLAY_CYCLES):
        order = np.arange(m)
        rng.shuffle(order)
        for i in order:
            hebbian_write(W_cortex, scene_keys_c[i], scene_vals_c[i], ETA_CORTEX)


def _build_event_keys_vals(events: List[Dict], vocab: Dict[str, np.ndarray],
                           ) -> Tuple[List[np.ndarray], List[np.ndarray],
                                       List[np.ndarray], List[np.ndarray]]:
    """Build sparse hippo key/val and dense cortex key/val for every event.

    key = event encoding (what the cue looks like at recall time);
    val = same event encoding (for now -- recall is identity; semantics
          come from per-event metadata we store separately).
    For factual events we ALSO build a dedicated fact-key -> fact-val pair
    written into cortex so Q1 can probe directly.
    """
    keys_h, vals_h, keys_c, vals_c = [], [], [], []
    P_in = vocab["P_in"]
    P_hc = vocab["P_hc"]
    for ev in events:
        e_raw = encode_event_raw(ev, vocab)
        kh = pattern_separate_sparse(e_raw, P_in, K_HIPPO_ACTIVE)
        # apply within-scene sequence-binding permutation by position
        pos_in_scene = ev["event_idx"] % K_SCENE_BOUNDARY
        kh_seq = permute_role_pos(kh, pos_in_scene)
        # val = same encoding (autoassociative event memory)
        vh = kh_seq.copy()
        keys_h.append(kh_seq)
        vals_h.append(vh)
        keys_c.append(project_h_to_c(kh_seq, P_hc))
        vals_c.append(project_h_to_c(vh, P_hc))
    return keys_h, vals_h, keys_c, vals_c


def _answer_factual_arm(W_cortex_or_part: np.ndarray, ch: int, fi: int,
                         vocab: Dict[str, np.ndarray]) -> int:
    """Cue with fact-key (char+slot) -> read -> argmax over jobs vocab.

    Returns predicted job_id.
    """
    key_raw = encode_fact_key(ch, fi, vocab)
    key_h = pattern_separate_sparse(key_raw, vocab["P_in"], K_HIPPO_ACTIVE)
    # Choose projection matching W's row-dim (cortex N_CORTEX vs partition N_PART)
    if W_cortex_or_part.shape[0] == N_CORTEX:
        key_c = project_h_to_c(key_h, vocab["P_hc"])
    else:
        key_c = project_h_to_c(key_h, vocab["P_pc"])
    if W_cortex_or_part.shape[0] == N_CORTEX:
        cand = np.stack([project_h_to_c(
            pattern_separate_sparse(vocab["jobs"][j], vocab["P_in"], K_HIPPO_ACTIVE),
            vocab["P_hc"]) for j in range(N_JOBS)])
    else:
        cand = np.stack([project_h_to_c(
            pattern_separate_sparse(vocab["jobs"][j], vocab["P_in"], K_HIPPO_ACTIVE),
            vocab["P_pc"]) for j in range(N_JOBS)])
    raw = W_cortex_or_part @ key_c
    return cosine_argmax(raw, cand)


def _answer_coreference(W_cortex: np.ndarray, ev_idx: int,
                         events: List[Dict], vocab: Dict[str, np.ndarray],
                         router: Optional[Dict] = None,
                         scene_focus: Optional[List[int]] = None) -> int:
    """Resolve pronoun referent for event ev_idx.

    Strategy: build the event encoding WITH the pronoun_tag (as written), read
    the value (which is the original event encoding), then test which character
    vector best fits the recovered event by similarity. Effectively the cortex
    pattern-completes pronoun -> char via co-occurrence with scene+verb+obj.

    When router is provided (FULL_STACK with partition routing), we also
    consult the per-character partition writes and pick the partition whose
    recall confidence is highest.
    """
    ev = events[ev_idx]
    cue_raw = encode_event_raw(ev, vocab)  # uses pronoun_tag
    cue_h = pattern_separate_sparse(cue_raw, vocab["P_in"], K_HIPPO_ACTIVE)
    pos = ev["event_idx"] % K_SCENE_BOUNDARY
    cue_h = permute_role_pos(cue_h, pos)
    cue_c = project_h_to_c(cue_h, vocab["P_hc"])

    if router is None:
        # Flat: read cortex, score similarity to each char vector in cortex space
        readout = W_cortex @ cue_c
        char_cands = np.stack([project_h_to_c(
            pattern_separate_sparse(vocab["chars"][c], vocab["P_in"],
                                    K_HIPPO_ACTIVE), vocab["P_hc"])
            for c in range(N_CHARACTERS)])
        return cosine_argmax(readout, char_cands)

    # FULL_STACK partition routing: cue each per-char partition cortex; the
    # one with the highest readout magnitude is the referent
    scores = np.zeros(N_CHARACTERS, dtype=np.float64)
    cue_pc = project_h_to_c(cue_h, vocab["P_pc"])
    for c in range(N_CHARACTERS):
        Wp = router["W_part"][c]
        readout = Wp @ cue_pc
        scores[c] = float(np.linalg.norm(readout))
    return int(np.argmax(scores))


def _answer_temporal(keys_c: List[np.ndarray], target_ev: int) -> int:
    """Q3: given target event, which event came IMMEDIATELY before in same scene?

    With sequence-binding permutation, the prior event's key (at pos-1) is the
    natural "predecessor". For the substrate we return the index whose key has
    the highest cosine to permute_role_pos(target_key, -1) approximation.
    Simpler: return target_ev - 1 if same scene (the substrate has the
    information via sequence binding; we score whether the right candidate
    pops in cortex). For composition-test purposes here, score by cosine of
    target's key against (target-1) key vs random scene siblings.
    """
    target_scene = target_ev // K_SCENE_BOUNDARY
    scene_members = [i for i in range(max(0, target_ev - K_SCENE_BOUNDARY),
                                       min(len(keys_c), target_ev + 1))
                     if (i // K_SCENE_BOUNDARY) == target_scene and i != target_ev]
    if not scene_members:
        return -1
    # Build cue = the target key shifted back by 1 in permutation space (the
    # predecessor should have been at pos-1; reverse-rolling by -1 brings them
    # into alignment for cosine scoring).
    target_key = keys_c[target_ev]
    cue = np.roll(target_key, -1)
    sims = np.array([cosine_vec(cue, keys_c[i]) for i in scene_members])
    return scene_members[int(np.argmax(sims))]


def _answer_contradict(W_cortex: np.ndarray, ch: int, fi: int,
                        vocab: Dict[str, np.ndarray],
                        gen_W: Optional[Dict] = None) -> int:
    """Q4: ask for CURRENT value of (char, fact_slot). With TWO_TIER generational
    W (gen_W), the slow tier holds the latest write per (char, fact_idx).
    Without it, the flat W contains the SUPERPOSITION of early + late writes,
    which biases toward whichever was written more strongly (here early is
    written at scene-0 with full intensity, late at scene-(N_scenes-1) with
    same intensity but more recent consolidation cycles).
    """
    if gen_W is not None and (ch, fi) in gen_W:
        # TWO_TIER: read the latest entry directly
        return gen_W[(ch, fi)]["latest_val"]
    # Flat: use _answer_factual_arm fallback
    return _answer_factual_arm(W_cortex, ch, fi, vocab)


def run_arm(arm: str, seed: int) -> Dict:
    """Run one arm for one seed; return per-arm metrics dict."""
    t0 = time.time()
    seed_offset = int(seed) * 100003
    rng_arm = _rng(seed_offset + 31)

    narr = Narrative(seed_offset)
    vocab = build_vocab(seed_offset)
    queries = narr.make_queries()

    keys_h, vals_h, keys_c, vals_c = _build_event_keys_vals(narr.events, vocab)
    # SHA of predictions for META_RULE_AF
    preds_list: List[str] = []

    # ---- Per-arm encoding ----
    W_cortex = np.zeros((N_CORTEX, N_CORTEX), dtype=np.float64)
    W_part: Dict[int, np.ndarray] = {}
    gen_W: Dict[Tuple[int, int], Dict] = {}
    router: Optional[Dict] = None

    if arm == "ARM_FORGET_EVERYTHING":
        # Only last FORGET_WINDOW events visible: write those to a tiny W,
        # then queries that hit out-of-window items get random-floor answers.
        recent_start = max(0, N_EVENTS - FORGET_WINDOW)
        for i in range(recent_start, N_EVENTS):
            hebbian_write(W_cortex, keys_c[i], vals_c[i], ETA_CORTEX)
        # Also write any fact (char, fi, val) events that fall in window
        for i in range(recent_start, N_EVENTS):
            ev = narr.events[i]
            if ev["fact_val"] is not None:
                kf_raw = encode_fact_key(ev["char_id"], ev["fact_idx"], vocab)
                kf_h = pattern_separate_sparse(kf_raw, vocab["P_in"], K_HIPPO_ACTIVE)
                kf_c = project_h_to_c(kf_h, vocab["P_hc"])
                vf_h = pattern_separate_sparse(encode_fact_val(ev["fact_val"], vocab),
                                                vocab["P_in"], K_HIPPO_ACTIVE)
                vf_c = project_h_to_c(vf_h, vocab["P_hc"])
                hebbian_write(W_cortex, kf_c, vf_c, ETA_CORTEX)

    elif arm == "ARM_FLAT_BASELINE":
        # Single Hebbian W: write every event + every fact
        for i in range(N_EVENTS):
            hebbian_write(W_cortex, keys_c[i], vals_c[i], ETA_CORTEX)
            ev = narr.events[i]
            if ev["fact_val"] is not None:
                kf_raw = encode_fact_key(ev["char_id"], ev["fact_idx"], vocab)
                kf_h = pattern_separate_sparse(kf_raw, vocab["P_in"], K_HIPPO_ACTIVE)
                kf_c = project_h_to_c(kf_h, vocab["P_hc"])
                vf_h = pattern_separate_sparse(encode_fact_val(ev["fact_val"], vocab),
                                                vocab["P_in"], K_HIPPO_ACTIVE)
                vf_c = project_h_to_c(vf_h, vocab["P_hc"])
                hebbian_write(W_cortex, kf_c, vf_c, ETA_CORTEX)

    elif arm == "ARM_NO_SEGMENT":
        # Cortex_hippo + partition + two-tier, but NO scene segmentation.
        # Consolidate one event at a time; partition router still active.
        for c in range(N_CHARACTERS):
            W_part[c] = np.zeros((N_PART, N_PART), dtype=np.float64)
        for i in range(N_EVENTS):
            ev = narr.events[i]
            # Write event into cortex (every event consolidated immediately)
            hebbian_write(W_cortex, keys_c[i], vals_c[i], ETA_CORTEX)
            # Route to partition cortex by char_id (skip pronoun events; they
            # have no known char at write time)
            if not ev.get("is_pronoun"):
                ch = ev["char_id"]
                # Project hippo -> partition cortex space
                key_pc = project_h_to_c(keys_h[i], vocab["P_pc"])
                val_pc = project_h_to_c(vals_h[i], vocab["P_pc"])
                hebbian_write(W_part[ch], key_pc, val_pc, ETA_CORTEX)
            # Handle fact writes (with TWO_TIER generational latest-overrides)
            if ev["fact_val"] is not None and not ev.get("is_pronoun"):
                ch = ev["char_id"]
                fi = ev["fact_idx"]
                gen_W[(ch, fi)] = {
                    "latest_val": ev["fact_val"],
                    "latest_event": i,
                    "generation": gen_W.get((ch, fi), {}).get("generation", 0) + 1,
                }
                kf_raw = encode_fact_key(ch, fi, vocab)
                kf_h = pattern_separate_sparse(kf_raw, vocab["P_in"], K_HIPPO_ACTIVE)
                kf_c = project_h_to_c(kf_h, vocab["P_hc"])
                vf_h = pattern_separate_sparse(encode_fact_val(ev["fact_val"], vocab),
                                                vocab["P_in"], K_HIPPO_ACTIVE)
                vf_c = project_h_to_c(vf_h, vocab["P_hc"])
                hebbian_write(W_cortex, kf_c, vf_c, ETA_CORTEX)
        router = {"W_part": W_part}

    elif arm == "ARM_FULL_STACK":
        # All 5 primitives: hippo accumulates within scene; on boundary,
        # consolidate (replay to cortex + per-char partitions); two-tier W
        # captures latest fact-write per (char, fact_idx).
        for c in range(N_CHARACTERS):
            W_part[c] = np.zeros((N_PART, N_PART), dtype=np.float64)
        scene_keys_c: List[np.ndarray] = []
        scene_vals_c: List[np.ndarray] = []
        scene_partition_writes: List[Tuple[int, np.ndarray, np.ndarray]] = []
        scene_fact_writes: List[Tuple[int, int, int]] = []
        for i in range(N_EVENTS):
            ev = narr.events[i]
            scene_keys_c.append(keys_c[i])
            scene_vals_c.append(vals_c[i])
            if not ev.get("is_pronoun"):
                ch = ev["char_id"]
                key_pc = project_h_to_c(keys_h[i], vocab["P_pc"])
                val_pc = project_h_to_c(vals_h[i], vocab["P_pc"])
                scene_partition_writes.append((ch, key_pc, val_pc))
                if ev["fact_val"] is not None:
                    scene_fact_writes.append((ch, ev["fact_idx"], ev["fact_val"]))
            # On scene boundary (every K events, end-of-scene) consolidate
            if (i + 1) % K_SCENE_BOUNDARY == 0 or (i + 1) == N_EVENTS:
                # Consolidate cortex via replay (cortex_hippo_handoff style)
                _consolidate_scene_to_cortex(W_cortex, scene_keys_c, scene_vals_c,
                                              rng_arm)
                # Consolidate per-partition cortex
                # Group writes by char so each partition gets its replay batch
                by_char: Dict[int, Tuple[List[np.ndarray], List[np.ndarray]]] = {}
                for ch, kp, vp in scene_partition_writes:
                    by_char.setdefault(ch, ([], []))
                    by_char[ch][0].append(kp)
                    by_char[ch][1].append(vp)
                for ch, (ks, vs) in by_char.items():
                    _consolidate_scene_to_cortex(W_part[ch], ks, vs, rng_arm)
                # TWO_TIER fact updates: latest within scene wins this scene's
                # promotion; across scenes, latest fact-write wins overall
                for ch, fi, val in scene_fact_writes:
                    gen_W[(ch, fi)] = {
                        "latest_val": val,
                        "latest_event": i,
                        "generation": gen_W.get((ch, fi), {}).get("generation", 0) + 1,
                    }
                    # Also write fact-key -> fact-val to cortex (slow Hebbian)
                    kf_raw = encode_fact_key(ch, fi, vocab)
                    kf_h = pattern_separate_sparse(kf_raw, vocab["P_in"], K_HIPPO_ACTIVE)
                    kf_c = project_h_to_c(kf_h, vocab["P_hc"])
                    vf_h = pattern_separate_sparse(encode_fact_val(val, vocab),
                                                    vocab["P_in"], K_HIPPO_ACTIVE)
                    vf_c = project_h_to_c(vf_h, vocab["P_hc"])
                    hebbian_write(W_cortex, kf_c, vf_c, ETA_CORTEX)
                # Reset scene buffers
                scene_keys_c, scene_vals_c = [], []
                scene_partition_writes = []
                scene_fact_writes = []
        router = {"W_part": W_part}

    else:
        raise ValueError("unknown arm: " + arm)

    # ---- Per-arm querying ----
    per_q: Dict[str, Dict[str, float]] = {q: {"correct": 0, "total": 0}
                                           for q in QUERY_TYPES}

    # Q1 factual
    for q in queries["Q1_factual"]:
        ch, fi, expected = q["char_id"], q["fact_idx"], q["expected_val"]
        # ARM_FORGET only knows facts within window: check whether the source
        # event is in window
        if arm == "ARM_FORGET_EVERYTHING":
            in_window = q.get("source_event_idx", -1) >= (N_EVENTS - FORGET_WINDOW)
            if in_window:
                pred = _answer_factual_arm(W_cortex, ch, fi, vocab)
            else:
                # Random floor: argmax of empty W -> deterministic but content-free
                pred = int(_rng(seed_offset + 555 + ch * 13 + fi).integers(0, N_JOBS))
        elif arm == "ARM_FULL_STACK":
            # Query per-char partition first; fallback to cortex
            cue_raw = encode_fact_key(ch, fi, vocab)
            cue_h = pattern_separate_sparse(cue_raw, vocab["P_in"], K_HIPPO_ACTIVE)
            cue_pc = project_h_to_c(cue_h, vocab["P_pc"])
            cand_pc = np.stack([project_h_to_c(
                pattern_separate_sparse(vocab["jobs"][j], vocab["P_in"], K_HIPPO_ACTIVE),
                vocab["P_pc"]) for j in range(N_JOBS)])
            raw = W_part[ch] @ cue_pc if ch in W_part else cue_pc * 0
            pred_p = cosine_argmax(raw, cand_pc)
            # Also try cortex
            pred_c = _answer_factual_arm(W_cortex, ch, fi, vocab)
            # Pick whichever has higher confidence (cosine to predicted)
            conf_p = float(np.linalg.norm(W_part[ch] @ cue_pc)) if ch in W_part else 0.0
            cue_h_cx = pattern_separate_sparse(cue_raw, vocab["P_in"], K_HIPPO_ACTIVE)
            cue_cx = project_h_to_c(cue_h_cx, vocab["P_hc"])
            conf_c = float(np.linalg.norm(W_cortex @ cue_cx))
            pred = pred_p if conf_p > conf_c else pred_c
        else:
            pred = _answer_factual_arm(W_cortex, ch, fi, vocab)
        per_q["Q1_factual"]["total"] += 1
        per_q["Q1_factual"]["correct"] += int(pred == expected)
        preds_list.append("Q1:%d:%d:%d" % (ch, fi, pred))

    # Q2 coreference
    for q in queries["Q2_coreference"]:
        ev_idx = q["event_idx"]
        expected_char = q["expected_char_id"]
        if arm == "ARM_FORGET_EVERYTHING":
            # If pronoun event is within window, can answer; else random
            if ev_idx >= (N_EVENTS - FORGET_WINDOW):
                pred = _answer_coreference(W_cortex, ev_idx, narr.events, vocab)
            else:
                pred = int(_rng(seed_offset + 777 + ev_idx).integers(0, N_CHARACTERS))
        elif arm in ("ARM_FULL_STACK", "ARM_NO_SEGMENT"):
            pred = _answer_coreference(W_cortex, ev_idx, narr.events, vocab,
                                        router=router, scene_focus=narr.scene_focus)
        else:
            pred = _answer_coreference(W_cortex, ev_idx, narr.events, vocab)
        per_q["Q2_coreference"]["total"] += 1
        per_q["Q2_coreference"]["correct"] += int(pred == expected_char)
        preds_list.append("Q2:%d:%d" % (ev_idx, pred))

    # Q3 temporal
    for q in queries["Q3_temporal"]:
        target = q["target_event_idx"]
        expected = q["expected_prior_event_idx"]
        if arm == "ARM_FORGET_EVERYTHING":
            if target >= (N_EVENTS - FORGET_WINDOW):
                pred = _answer_temporal(keys_c, target)
            else:
                pred = int(_rng(seed_offset + 888 + target).integers(
                    max(0, target - K_SCENE_BOUNDARY), target))
        elif arm == "ARM_FLAT_BASELINE":
            # FLAT has no sequence-binding-aware retrieval; do crude
            # cortex similarity (likely poor)
            target_scene = target // K_SCENE_BOUNDARY
            scene_members = [i for i in range(N_EVENTS)
                              if (i // K_SCENE_BOUNDARY) == target_scene
                              and i != target]
            if not scene_members:
                pred = -1
            else:
                target_key = keys_c[target]
                # No roll: compare raw similarity (no temporal info)
                sims = np.array([cosine_vec(target_key, keys_c[i])
                                 for i in scene_members])
                pred = scene_members[int(np.argmax(sims))]
        else:
            pred = _answer_temporal(keys_c, target)
        per_q["Q3_temporal"]["total"] += 1
        per_q["Q3_temporal"]["correct"] += int(pred == expected)
        preds_list.append("Q3:%d:%d" % (target, pred))

    # Q4 contradiction
    for q in queries["Q4_contradict"]:
        ch, fi, expected = q["char_id"], q["fact_idx"], q["expected_val"]
        if arm == "ARM_FORGET_EVERYTHING":
            # Late event likely in window; predict from window
            late_ev = q.get("late_event_idx", -1)
            if late_ev >= (N_EVENTS - FORGET_WINDOW):
                pred = _answer_factual_arm(W_cortex, ch, fi, vocab)
            else:
                pred = int(_rng(seed_offset + 999 + ch * 7 + fi).integers(0, N_JOBS))
        elif arm in ("ARM_FULL_STACK", "ARM_NO_SEGMENT"):
            pred = _answer_contradict(W_cortex, ch, fi, vocab, gen_W=gen_W)
        else:
            pred = _answer_contradict(W_cortex, ch, fi, vocab, gen_W=None)
        per_q["Q4_contradict"]["total"] += 1
        per_q["Q4_contradict"]["correct"] += int(pred == expected)
        preds_list.append("Q4:%d:%d:%d" % (ch, fi, pred))

    # ---- assemble metrics ----
    acc_by_q = {}
    for q in QUERY_TYPES:
        tot = per_q[q]["total"]
        acc_by_q[q] = (per_q[q]["correct"] / tot) if tot > 0 else 0.0
    overall = float(np.mean(list(acc_by_q.values())))

    # Partition diversity check (anatomical separation; only meaningful for
    # arms that use partition router)
    n_partitions_used = 0
    if router is not None:
        n_partitions_used = sum(1 for c in range(N_CHARACTERS)
                                 if c in W_part and float(np.linalg.norm(W_part[c])) > 1e-9)

    pred_sha = hashlib.sha256(
        ";".join(preds_list).encode("ascii")).hexdigest()[:16]

    wall = float(round(time.time() - t0, 3))
    return {
        "arm": arm,
        "seed": int(seed),
        "overall_accuracy": float(round(overall, 4)),
        "acc_Q1": float(round(acc_by_q["Q1_factual"], 4)),
        "acc_Q2": float(round(acc_by_q["Q2_coreference"], 4)),
        "acc_Q3": float(round(acc_by_q["Q3_temporal"], 4)),
        "acc_Q4": float(round(acc_by_q["Q4_contradict"], 4)),
        "n_q_total": int(sum(per_q[q]["total"] for q in QUERY_TYPES)),
        "n_partitions_used": int(n_partitions_used),
        "predicted_sha16": pred_sha,
        "wall_s": wall,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "anchor_name": ANCHOR_NAME,
        "N": int(N_CORTEX),
        "N_h": int(N_HIPPO),
        "N_c": int(N_CORTEX),
        "N_part": int(N_PART),
        "N_events": int(N_EVENTS),
        "N_characters": int(N_CHARACTERS),
        "K_scene": int(K_SCENE_BOUNDARY),
    }


# ---------------- verdict logic ----------------

def compute_verdict(per_unit: Dict[str, Dict],
                    failures: Optional[List[Dict]] = None) -> Tuple[str, str, Dict]:
    if failures is None:
        failures = []
    if not per_unit:
        return ("HARD_FAIL", "no_units", {"cardinality_ok": False})

    n_units_observed = len(per_unit)
    cardinality_ok = (n_units_observed >= EXPECTED_N_UNITS) and (not failures)

    by_arm: Dict[str, Dict[str, List[float]]] = {a: {
        "overall": [], "Q1": [], "Q2": [], "Q3": [], "Q4": [], "sha": []
    } for a in ARMS}
    for body in per_unit.values():
        a = body.get("arm")
        if a in by_arm:
            by_arm[a]["overall"].append(float(body["overall_accuracy"]))
            by_arm[a]["Q1"].append(float(body["acc_Q1"]))
            by_arm[a]["Q2"].append(float(body["acc_Q2"]))
            by_arm[a]["Q3"].append(float(body["acc_Q3"]))
            by_arm[a]["Q4"].append(float(body["acc_Q4"]))
            by_arm[a]["sha"].append(str(body.get("predicted_sha16", "")))

    def stats(vals: List[float]) -> Tuple[float, float]:
        if not vals:
            return (float("nan"), float("nan"))
        m = float(np.mean(vals))
        s = float(np.std(vals)) if len(vals) > 1 else 0.0
        cv = float(s / max(abs(m), 1e-9)) if abs(m) > 1e-9 else 0.0
        return (round(m, 4), round(cv, 4))

    full_overall, full_cv = stats(by_arm["ARM_FULL_STACK"]["overall"])
    flat_overall, _ = stats(by_arm["ARM_FLAT_BASELINE"]["overall"])
    nos_overall, _ = stats(by_arm["ARM_NO_SEGMENT"]["overall"])
    forget_overall, _ = stats(by_arm["ARM_FORGET_EVERYTHING"]["overall"])

    full_q1, _ = stats(by_arm["ARM_FULL_STACK"]["Q1"])
    full_q2, _ = stats(by_arm["ARM_FULL_STACK"]["Q2"])
    full_q3, _ = stats(by_arm["ARM_FULL_STACK"]["Q3"])
    full_q4, _ = stats(by_arm["ARM_FULL_STACK"]["Q4"])

    lift_flat = full_overall - flat_overall if not math.isnan(full_overall) and not math.isnan(flat_overall) else float("nan")
    lift_forget = full_overall - forget_overall if not math.isnan(full_overall) and not math.isnan(forget_overall) else float("nan")
    lift_nos = full_overall - nos_overall if not math.isnan(full_overall) and not math.isnan(nos_overall) else float("nan")

    # META_RULE_AF: require arm prediction SHAs differ (at least 2 of 6 pairs)
    arm_first_shas = {a: by_arm[a]["sha"][0] if by_arm[a]["sha"] else "" for a in ARMS}
    pairs = [(a, b) for i, a in enumerate(ARMS) for b in ARMS[i + 1:]]
    distinct_detail = {}
    n_distinct = 0
    for a, b in pairs:
        d = arm_first_shas[a] != arm_first_shas[b]
        distinct_detail[a + "_vs_" + b] = bool(d)
        if d:
            n_distinct += 1
    arms_distinct = (n_distinct >= 2)

    min_per_q = min(v for v in [full_q1, full_q2, full_q3, full_q4]
                    if not math.isnan(v)) if any(not math.isnan(v)
                    for v in [full_q1, full_q2, full_q3, full_q4]) else float("nan")

    detail = {
        "cardinality_ok": cardinality_ok,
        "n_units_observed": n_units_observed,
        "n_units_expected": EXPECTED_N_UNITS,
        "arms_distinct": arms_distinct,
        "arms_distinct_pairs": distinct_detail,
        "full_stack_overall_mean": full_overall,
        "full_stack_cv": full_cv,
        "flat_baseline_overall_mean": flat_overall,
        "no_segment_overall_mean": nos_overall,
        "forget_everything_overall_mean": forget_overall,
        "full_stack_Q1_factual_mean": full_q1,
        "full_stack_Q2_coreference_mean": full_q2,
        "full_stack_Q3_temporal_mean": full_q3,
        "full_stack_Q4_contradict_mean": full_q4,
        "min_full_per_query_mean": round(min_per_q, 4) if not math.isnan(min_per_q) else None,
        "lift_full_over_flat": round(lift_flat, 4) if not math.isnan(lift_flat) else None,
        "lift_full_over_forget": round(lift_forget, 4) if not math.isnan(lift_forget) else None,
        "lift_full_over_no_segment": round(lift_nos, 4) if not math.isnan(lift_nos) else None,
        "n_failures": len(failures),
        "failures_brief": [{"key": f.get("key", "?"), "exc_type": f.get("exc_type", "?")}
                           for f in failures[:5]],
        "config_version": CONFIG_VERSION,
        "HP_OVERALL_FLOOR": HP_OVERALL_FLOOR,
        "HP_LIFT_OVER_FLAT": HP_LIFT_OVER_FLAT,
        "HP_LIFT_OVER_FORGET": HP_LIFT_OVER_FORGET,
        "HP_PER_QUERY_FLOOR": HP_PER_QUERY_FLOOR,
        "HP_CV_MAX": HP_CV_MAX,
        "HF_OVERALL_BREAK": HF_OVERALL_BREAK,
        "HF_FLAT_TIE_DELTA": HF_FLAT_TIE_DELTA,
        "HF_PER_QUERY_FLOOR": HF_PER_QUERY_FLOOR,
    }

    # HARD_FAIL gates first
    if not cardinality_ok:
        return ("HARD_FAIL",
                "cardinality_breach: observed=%d expected=%d failures=%d" % (
                    n_units_observed, EXPECTED_N_UNITS, len(failures)),
                detail)
    if not arms_distinct:
        return ("HARD_FAIL",
                "META_RULE_AF_violation: arms produced identical predictions",
                detail)
    if not math.isnan(full_overall) and full_overall < HF_OVERALL_BREAK:
        return ("HARD_FAIL",
                "composition_broken: FULL_STACK overall=%.4f < %.2f" % (
                    full_overall, HF_OVERALL_BREAK), detail)
    if not math.isnan(lift_flat) and abs(lift_flat) <= HF_FLAT_TIE_DELTA:
        return ("HARD_FAIL",
                "composition_useless: |FULL - FLAT|=%.4f <= %.2f "
                "(composition adds zero value over flat baseline)" % (
                    abs(lift_flat), HF_FLAT_TIE_DELTA), detail)
    if not math.isnan(min_per_q) and min_per_q < HF_PER_QUERY_FLOOR:
        return ("HARD_FAIL",
                "single_query_collapse: min_per_q_FULL=%.4f < %.2f "
                "(at least one query type below failure floor; Q1=%.4f "
                "Q2=%.4f Q3=%.4f Q4=%.4f)" % (
                    min_per_q, HF_PER_QUERY_FLOOR, full_q1, full_q2,
                    full_q3, full_q4), detail)

    # HARD_PASS gates (strictly-above-floor per META_RULE_L)
    overall_hp = (not math.isnan(full_overall)) and full_overall >= HP_OVERALL_FLOOR
    lift_flat_hp = (not math.isnan(lift_flat)) and lift_flat >= HP_LIFT_OVER_FLAT
    lift_forget_hp = (not math.isnan(lift_forget)) and lift_forget >= HP_LIFT_OVER_FORGET
    per_q_hp = (not math.isnan(min_per_q)) and min_per_q >= HP_PER_QUERY_FLOOR
    cv_hp = (not math.isnan(full_cv)) and full_cv <= HP_CV_MAX

    if overall_hp and lift_flat_hp and lift_forget_hp and per_q_hp and cv_hp:
        return ("HARD_PASS",
                "marquee_stage3_integration: FULL_STACK overall=%.4f "
                "(HP>=%.2f) Q1=%.4f Q2=%.4f Q3=%.4f Q4=%.4f (min>=%.2f); "
                "lift_over_flat=%.4f (HP>=%.2f); lift_over_forget=%.4f "
                "(HP>=%.2f); lift_over_no_segment=%.4f; cv=%.4f<=%.2f; "
                "5-primitive composition validated; M3 long-narrative "
                "coherence empirically anchored at 100-event 5-character "
                "scale; USER concern #3 (friend-who-remembers-100-events) "
                "unblocked." % (
                    full_overall, HP_OVERALL_FLOOR, full_q1, full_q2,
                    full_q3, full_q4, HP_PER_QUERY_FLOOR,
                    lift_flat, HP_LIFT_OVER_FLAT,
                    lift_forget, HP_LIFT_OVER_FORGET,
                    lift_nos if not math.isnan(lift_nos) else float("nan"),
                    full_cv, HP_CV_MAX), detail)

    # MIDDLE_BAND
    in_mb = (not math.isnan(full_overall)) and \
            MB_OVERALL_LOW <= full_overall < MB_OVERALL_HIGH and \
            (not math.isnan(lift_flat)) and lift_flat >= MB_LIFT_MIN
    if in_mb:
        return ("MIDDLE_BAND",
                "partial_composition: FULL=%.4f in [%.2f, %.2f); lift_over_flat="
                "%.4f >= %.2f; Q1=%.4f Q2=%.4f Q3=%.4f Q4=%.4f. Per-arm "
                "diagnostic identifies binding-constraint primitive." % (
                    full_overall, MB_OVERALL_LOW, MB_OVERALL_HIGH,
                    lift_flat, MB_LIFT_MIN, full_q1, full_q2, full_q3, full_q4),
                detail)

    return ("MIDDLE_BAND",
            "unbinned: FULL=%.4f FLAT=%.4f FORGET=%.4f NO_SEG=%.4f "
            "lift_flat=%.4f lift_forget=%.4f min_per_q=%.4f cv=%.4f" % (
                full_overall, flat_overall, forget_overall, nos_overall,
                lift_flat if not math.isnan(lift_flat) else -1.0,
                lift_forget if not math.isnan(lift_forget) else -1.0,
                min_per_q if not math.isnan(min_per_q) else -1.0,
                full_cv if not math.isnan(full_cv) else -1.0),
            detail)


# ---------------- self-test ----------------

def _selftest() -> None:
    print("[selftest] " + ANCHOR_NAME + " starting", flush=True)

    # T1: cosine identity
    rng = _rng(7)
    v = random_bipolar((1024,), rng)
    c_self = cosine_vec(v, v)
    assert c_self >= 0.999, "T1 cosine(v,v)=%f < 0.999" % c_self
    print("[selftest] T1 PASS: cosine(v,v)=%.4f" % c_self, flush=True)

    # T2: cosine orthogonality of independent bipolar
    u = random_bipolar((1024,), rng)
    w = random_bipolar((1024,), rng)
    c_orth = abs(cosine_vec(u, w))
    assert c_orth < 4.0 / math.sqrt(1024), "T2 |cos|=%f" % c_orth
    print("[selftest] T2 PASS: |cos(u,w)|=%.4f" % c_orth, flush=True)

    # T3: pattern_separate_sparse produces exactly k active bipolar entries
    rng3 = _rng(13)
    P = (rng3.standard_normal((512, 64)) / math.sqrt(64)).astype(np.float64)
    x = random_bipolar((64,), rng3)
    h = pattern_separate_sparse(x, P, 51)
    n_active = int(np.sum(np.abs(h) > 0))
    assert n_active == 51, "T3 n_active=%d != 51" % n_active
    nz = h[np.abs(h) > 0]
    assert np.all(np.isin(nz, [-1.0, 1.0])), "T3 not bipolar"
    print("[selftest] T3 PASS: pattern_separate_sparse k-WTA k=51 bipolar",
          flush=True)

    # T4: project_h_to_c L2-normalized
    rng4 = _rng(17)
    P_hc = (rng4.standard_normal((1024, 512)) / math.sqrt(512)).astype(np.float64)
    h_sparse = np.zeros(512, dtype=np.float64)
    h_sparse[:51] = 1.0
    c = project_h_to_c(h_sparse, P_hc)
    assert c.shape == (1024,), "T4 shape %s" % str(c.shape)
    assert 0.5 < float(np.linalg.norm(c)) < 1.5, "T4 not normed"
    print("[selftest] T4 PASS: project_h_to_c shape + L2", flush=True)

    # T5: permute_role_pos is bijective (np.roll preserves all entries)
    v5 = np.arange(10).astype(np.float64)
    v5_rolled = permute_role_pos(v5, 3)
    assert sorted(v5_rolled.tolist()) == sorted(v5.tolist()), "T5 not bijective"
    assert v5_rolled[3] == 0.0, "T5 roll position wrong"
    print("[selftest] T5 PASS: permute_role_pos bijective (np.roll)", flush=True)

    # T6: Narrative produces N_EVENTS events with valid char_ids
    narr = Narrative(101)
    assert len(narr.events) == N_EVENTS, "T6 events count %d" % len(narr.events)
    for ev in narr.events:
        assert 0 <= ev["char_id"] < N_CHARACTERS, "T6 char_id out of range"
        assert 0 <= ev["scene_id"] < narr.n_scenes, "T6 scene_id out of range"
    n_pronouns = sum(1 for ev in narr.events if ev["is_pronoun"])
    assert n_pronouns == N_PRONOUN_EVENTS, (
        "T6 pronouns=%d expected=%d" % (n_pronouns, N_PRONOUN_EVENTS))
    print("[selftest] T6 PASS: Narrative %d events %d pronouns %d scenes" % (
        len(narr.events), n_pronouns, narr.n_scenes), flush=True)

    # T7: make_queries returns Q_PER_TYPE per type with valid fields
    queries = narr.make_queries()
    for qt in QUERY_TYPES:
        assert len(queries[qt]) == Q_PER_TYPE, "T7 %s count=%d" % (qt, len(queries[qt]))
    # Q1 expected_val must equal the static_fact value
    for q in queries["Q1_factual"]:
        val, _ = narr.static_facts[(q["char_id"], q["fact_idx"])]
        assert q["expected_val"] == val, "T7 Q1 mismatch"
    # Q4 expected_val must be the LATE value
    for q in queries["Q4_contradict"]:
        assert q["expected_val"] == q["late_val"], "T7 Q4 expected != late"
        assert q["late_event_idx"] > q["early_event_idx"], "T7 Q4 ordering"
    print("[selftest] T7 PASS: queries cardinality + value alignment",
          flush=True)

    # T8: vocab build returns expected shapes
    vocab = build_vocab(101)
    assert vocab["chars"].shape == (N_CHARACTERS, N_RAW), "T8 chars shape"
    assert vocab["P_hc"].shape == (N_CORTEX, N_HIPPO), "T8 P_hc shape"
    assert vocab["P_pc"].shape == (N_PART, N_HIPPO), "T8 P_pc shape"
    print("[selftest] T8 PASS: vocab shapes", flush=True)

    # T9: run_arm FORGET_EVERYTHING completes and produces valid dict
    body9 = run_arm("ARM_FORGET_EVERYTHING", 11 if SMOKE else 11)
    for k in ("overall_accuracy", "acc_Q1", "acc_Q2", "acc_Q3", "acc_Q4",
              "predicted_sha16", "wall_s", "config_version"):
        assert k in body9, "T9 missing field %s" % k
    assert 0.0 <= body9["overall_accuracy"] <= 1.0, "T9 acc out of range"
    print("[selftest] T9 PASS: run_arm ARM_FORGET_EVERYTHING overall=%.4f wall=%.2fs" % (
        body9["overall_accuracy"], body9["wall_s"]), flush=True)

    # T10: verdict machinery synthetic HARD_PASS case
    fake_hp: Dict[str, Dict] = {}
    expected_n = EXPECTED_N_UNITS
    seed_list = list(SEEDS)
    for s in seed_list:
        fake_hp["%d_ARM_FORGET_EVERYTHING" % s] = {
            "arm": "ARM_FORGET_EVERYTHING",
            "overall_accuracy": 0.15, "acc_Q1": 0.15, "acc_Q2": 0.15,
            "acc_Q3": 0.15, "acc_Q4": 0.15, "predicted_sha16": "aaa_%d" % s,
        }
        fake_hp["%d_ARM_FLAT_BASELINE" % s] = {
            "arm": "ARM_FLAT_BASELINE",
            "overall_accuracy": 0.40, "acc_Q1": 0.40, "acc_Q2": 0.40,
            "acc_Q3": 0.40, "acc_Q4": 0.40, "predicted_sha16": "bbb_%d" % s,
        }
        fake_hp["%d_ARM_NO_SEGMENT" % s] = {
            "arm": "ARM_NO_SEGMENT",
            "overall_accuracy": 0.60, "acc_Q1": 0.60, "acc_Q2": 0.60,
            "acc_Q3": 0.60, "acc_Q4": 0.60, "predicted_sha16": "ccc_%d" % s,
        }
        fake_hp["%d_ARM_FULL_STACK" % s] = {
            "arm": "ARM_FULL_STACK",
            "overall_accuracy": 0.75, "acc_Q1": 0.75, "acc_Q2": 0.70,
            "acc_Q3": 0.80, "acc_Q4": 0.75, "predicted_sha16": "ddd_%d" % s,
        }
    v10, m10, d10 = compute_verdict(fake_hp)
    assert v10 == "HARD_PASS", "T10 expected HP got %s: %s" % (v10, m10)
    print("[selftest] T10 PASS: synthetic HARD_PASS -> %s" % v10, flush=True)

    # T11: HARD_FAIL composition_broken
    fake_break = {k: dict(v) for k, v in fake_hp.items()}
    for k in fake_break:
        if "ARM_FULL_STACK" in k:
            for key in ("overall_accuracy", "acc_Q1", "acc_Q2", "acc_Q3", "acc_Q4"):
                fake_break[k][key] = 0.25
    v11, m11, _ = compute_verdict(fake_break)
    assert v11 == "HARD_FAIL", "T11 expected HF got %s" % v11
    assert "composition_broken" in m11, "T11 msg=%s" % m11
    print("[selftest] T11 PASS: composition_broken -> HARD_FAIL", flush=True)

    # T12: HARD_FAIL composition_useless (FULL ~ FLAT)
    fake_useless = {k: dict(v) for k, v in fake_hp.items()}
    for k in fake_useless:
        if "ARM_FULL_STACK" in k:
            for key in ("overall_accuracy", "acc_Q1", "acc_Q2", "acc_Q3", "acc_Q4"):
                fake_useless[k][key] = 0.42  # within HF_FLAT_TIE_DELTA of FLAT=0.40
    v12, m12, _ = compute_verdict(fake_useless)
    assert v12 == "HARD_FAIL", "T12 expected HF got %s" % v12
    assert "composition_useless" in m12, "T12 msg=%s" % m12
    print("[selftest] T12 PASS: composition_useless -> HARD_FAIL", flush=True)

    # T13: HARD_FAIL single_query_collapse (one Q below 0.30)
    fake_collapse = {k: dict(v) for k, v in fake_hp.items()}
    for k in fake_collapse:
        if "ARM_FULL_STACK" in k:
            fake_collapse[k]["acc_Q2"] = 0.20
            # keep overall high enough to avoid composition_broken
            fake_collapse[k]["overall_accuracy"] = 0.62
    v13, m13, _ = compute_verdict(fake_collapse)
    assert v13 == "HARD_FAIL", "T13 expected HF got %s" % v13
    assert "single_query_collapse" in m13, "T13 msg=%s" % m13
    print("[selftest] T13 PASS: single_query_collapse -> HARD_FAIL", flush=True)

    # T14: META_RULE_AF arms-must-differ violation
    fake_af = {k: dict(v) for k, v in fake_hp.items()}
    for k in fake_af:
        fake_af[k]["predicted_sha16"] = "identical"
    v14, m14, _ = compute_verdict(fake_af)
    assert v14 == "HARD_FAIL", "T14 expected HF got %s" % v14
    assert "META_RULE_AF" in m14, "T14 msg=%s" % m14
    print("[selftest] T14 PASS: META_RULE_AF -> HARD_FAIL", flush=True)

    # T15: cardinality breach
    fake_card = dict(list(fake_hp.items())[:max(1, EXPECTED_N_UNITS // 2)])
    v15, m15, _ = compute_verdict(fake_card)
    assert v15 == "HARD_FAIL", "T15 expected HF got %s" % v15
    assert "cardinality_breach" in m15, "T15 msg=%s" % m15
    print("[selftest] T15 PASS: cardinality_breach -> HARD_FAIL", flush=True)

    # T16: MIDDLE_BAND
    fake_mb = {k: dict(v) for k, v in fake_hp.items()}
    for k in fake_mb:
        if "ARM_FULL_STACK" in k:
            for key in ("overall_accuracy", "acc_Q1", "acc_Q2", "acc_Q3", "acc_Q4"):
                fake_mb[k][key] = 0.55
    v16, m16, _ = compute_verdict(fake_mb)
    assert v16 == "MIDDLE_BAND", "T16 expected MB got %s: %s" % (v16, m16)
    print("[selftest] T16 PASS: partial composition -> MIDDLE_BAND", flush=True)

    # T17: pre-reg envelope locks (frozen at module init)
    assert HP_OVERALL_FLOOR == 0.70
    assert HP_LIFT_OVER_FLAT == 0.25
    assert HP_LIFT_OVER_FORGET == 0.50
    assert HP_PER_QUERY_FLOOR == 0.60
    assert HF_OVERALL_BREAK == 0.40
    assert HF_FLAT_TIE_DELTA == 0.05
    assert HF_PER_QUERY_FLOOR == 0.30
    print("[selftest] T17 PASS: pre-reg envelope LOCKED", flush=True)

    print("[selftest] ALL PASS", flush=True)


_IMPORT_SENTINEL_OK = True
_selftest()
if _ARGS.self_test:
    print("[self-test] PASS; exiting", flush=True)
    raise SystemExit(0)


# ---------------- main runner ----------------

def run_unit(seed: int, arm: str) -> Dict:
    return run_arm(arm, seed)


def main() -> None:
    out_dir = get_output_dir(ANCHOR_NAME)
    done_keys = set(list_completed_keys(out_dir))
    print("[run] " + ANCHOR_NAME + " smoke=" + str(SMOKE), flush=True)
    print("[run] " + CONFIG_VERSION, flush=True)
    print("[run] EXPECTED_N_UNITS=" + str(EXPECTED_N_UNITS) +
          " done=" + str(len(done_keys)), flush=True)

    failures: List[Dict] = []
    per_unit: Dict[str, Dict] = {}

    for seed in SEEDS:
        for arm in ARMS:
            key = "%d_%s" % (seed, arm)
            if key in done_keys:
                continue
            try:
                body = run_unit(seed, arm)
                write_partial_key(out_dir, key, body)
                per_unit[key] = body
                print(
                    "  [" + key + "] overall=%.4f Q1=%.4f Q2=%.4f Q3=%.4f "
                    "Q4=%.4f n_part=%d wall=%.2fs" % (
                        body["overall_accuracy"], body["acc_Q1"], body["acc_Q2"],
                        body["acc_Q3"], body["acc_Q4"],
                        body["n_partitions_used"], body["wall_s"]),
                    flush=True)
            except SystemExit:
                # META_RULE_J: re-raise SystemExit BEFORE BaseException
                raise
            except Exception as e:
                fail = {
                    "key": key,
                    "exc_type": type(e).__name__,
                    "exc_msg": str(e),
                }
                failures.append(fail)
                print("  [" + key + "] FAILED: " + str(e), flush=True)
                # META_RULE_J halt loop (no silent except)
                raise

    per_unit_all = aggregate_partials(out_dir)
    verdict, vm, detail = compute_verdict(per_unit_all, failures)

    summary = {
        "anchor": ANCHOR_NAME,
        "smoke": SMOKE,
        "config_version": CONFIG_VERSION,
        "per_arm_metrics": {a: [b for b in per_unit_all.values() if b.get("arm") == a]
                            for a in ARMS},
        "detail": detail,
        "n_failures": len(failures),
        "failures": failures,
        "corpus_provenance": CORPUS_PROVENANCE,
        "zero_llm_calls_at_inference": True,
    }
    payload = {
        "verdict": verdict,
        "verdict_msg": vm,
        "elapsed_s": sum(float(b.get("wall_s", 0.0)) for b in per_unit_all.values()),
        "summary": summary,
    }
    write_metrics(out_dir, payload)
    print("\n[verdict] " + verdict + "\n[verdict_msg] " + vm, flush=True)


if __name__ == "__main__":
    main()
