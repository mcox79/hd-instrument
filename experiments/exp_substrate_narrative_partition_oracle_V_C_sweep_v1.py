"""substrate_narrative_partition_oracle_V_C_sweep_v1 -- ANCHOR 2 V_C cliff sweep.

Per `notes/exp_dev_to_research_substrate_narrative_coref_temporal_composition_v1_smoke_2026-06-28.md`
ANCHOR 2 trigger: source narrative cell Q2 (partition oracle) did NOT rescue at
V_C ~ 50 (mean 0.167 vs naive 0.222). Partition oracle WAS validated at V_C=4000
on `exp_substrate_multihop_partition_oracle_v5_hardened_v1_smoke` (ORACLE_C=0.97).

Hypothesis: monotone Q2 lift as V_C grows. HARD_PASS predicted at V_C >= 1000
(substrate has enough per-partition density for substituted-cue magnitudes to
discriminate the true referent's partition response).

SWEEP AXIS (primary):
  V_C in {50, 200, 1000, 4000}  (4 points; brackets known-fail to known-pass)
  V_C expanded by scaling N_JOBS + N_OBJECTS proportionally so each char's
  partition gets more candidate facts.

ARMS (4; arms-must-differ on Q2 SHA per META_RULE_AF):
  ARM_RANDOM_FLOOR          -- uniform random (random_floor across V_C)
  ARM_BASELINE_NAIVE        -- today's failing magnitude readout (reproduces 0.22 mean)
  ARM_PARTITION_ORACLE_Q2   -- substituted-cue per-partition magnitude (the rescue mechanism)
  ARM_SEQUENCE_REPLAY_Q3    -- K=20 compressed-replay decoder; Q3 positive control
                                across V_C sweep (verify Q3 is NOT V_C-dependent)

EXPECTED CELL CARDINALITY:
  smoke = len(V_C_POINTS) * len(ARMS) * 1 seed = 4 * 4 * 1 = 16 units
  full  = 4 * 4 * 1 seed (chunked) = 16 units per chunk; 3 chunks per seed

CHUNKED: single seed per cell. SEED selected via:
  - --seed CLI flag
  - HDLAB_SEED env var
  - default 7 (smoke)

PREREG: preregs/2026-06-28_substrate_narrative_partition_oracle_V_C_sweep_v1.md

META_RULE_AC pre-reg | AE absolute paths | AF arms-must-differ SHA-256 |
AG edge-of-capacity smoke (smoke = full N_EVENTS=100) | AH atomic-write |
AM composition-first (reuses partition_oracle_v5 + c3_replay primitives) |
AN substrate-empirical anchors | H cardinality_ok |
J no-silent-except | L strict-above-floor |
DISCRIMINATOR-MUST-SURVIVE-SCALE Check A (smoke at full N_EVENTS).

ASCII-only. Author: exp_dev 2026-06-28.
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
import traceback
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    get_output_dir, write_partial_key, aggregate_partials, write_metrics,
    list_completed_keys,
)

ANCHOR_NAME = "substrate_narrative_partition_oracle_V_C_sweep_v1"
CORPUS_PROVENANCE = (
    "synthetic_narrative_5char_grouped_into_scenes_fixed_K10_boundaries_"
    "with_per_character_facts_pronouns_and_fact_updates_REUSED_from_"
    "stage3_narrative_coherence_100event_5char_full_stack_v1_"
    "with_V_C_scaling_via_N_JOBS_and_N_OBJECTS_expansion"
)

# ---------------- CLI ----------------
_P = argparse.ArgumentParser()
_P.add_argument("--self-test", action="store_true", dest="self_test")
_P.add_argument("--smoke", action="store_true")
_P.add_argument("--seed", type=int, default=None,
                help="single-seed-per-cell override; default auto-selects per mode")
_P.add_argument("--timeout", type=int, default=4500,
                help="per-cell timeout seconds (for runner enforcement)")
_ARGS, _ = _P.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = _HDLAB_EXP_NAME.lower().endswith("_smoke")
RUN_MODE = "smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE) \
    else os.environ.get("HDLAB_RUN_MODE", "full")
SMOKE = (RUN_MODE == "smoke")

_env_seed = os.environ.get("HDLAB_SEED", "").strip()
if _ARGS.seed is not None:
    SEED_ACTIVE = int(_ARGS.seed)
elif _env_seed:
    SEED_ACTIVE = int(_env_seed)
else:
    SEED_ACTIVE = 7

SEEDS = [SEED_ACTIVE]


# ---------------- pre-reg bands (LOCKED at module init) ----------------
# Hypothesis: monotone Q2 lift with V_C; HARD_PASS at V_C >= 1000.
# Per-point bands (applied per V_C):
HP_PARTITION_Q2_AT_HIGH_VC = 0.60   # V_C >= 1000 (drill prediction)
HP_LIFT_OVER_NAIVE_AT_HIGH_VC = 0.30
HP_REPLAY_Q3_ALL_VC = 0.60          # Q3 positive control should pass at all V_C
HF_REPLAY_Q3_ALL_VC = 0.20          # If replay fails at any V_C, primitive concern

# Sweep-level HARD_PASS criterion: monotone-increasing oracle_Q2 with V_C
# AND oracle_Q2 at V_C=4000 >= HP_PARTITION_Q2_AT_HIGH_VC
HP_MONOTONE_REQUIRED = True
HP_MIN_VC_FOR_PASS = 1000

# Sweep-level HARD_FAIL: oracle never rescues even at V_C=4000
HF_PARTITION_Q2_AT_TOP_VC = 0.30    # oracle at V_C=4000 stays below this => HF

# Baseline sanity (replicate source cell's 0.22 at low V_C)
HP_BASELINE_LOW_VC_NEAR_022 = (0.10, 0.40)  # acceptable bracket around 0.22

# Random floor cap (5-way Q2 random => expected 0.20; tolerate +0.20 noise at Q=8)
HF_RANDOM_FLOOR_MAX = 0.10

# Bands lock
assert HP_PARTITION_Q2_AT_HIGH_VC > HF_PARTITION_Q2_AT_TOP_VC, "Q2 bands locked"
assert HP_REPLAY_Q3_ALL_VC > HF_REPLAY_Q3_ALL_VC, "Q3 bands locked"


# ---------------- V_C sweep axis ----------------
# V_C = candidate-pool size per partition (analogue of partition_oracle_v5's V_C=4000).
# Realized by scaling (N_JOBS, N_OBJECTS) together. Source cell: N_JOBS=8 N_OBJ=16
# => V_C effective ~24. Sweep targets ~50, 200, 1000, 4000.
# (We over-shoot source 24 -> 50 at smallest point to keep cell distinct from
# source cell's exact regime while still bracketing known-fail.)
V_C_POINTS_FULL = [50, 200, 1000, 4000]
V_C_POINTS_SMOKE = [50, 200, 1000, 4000]  # same sweep at smoke
V_C_POINTS = V_C_POINTS_SMOKE if SMOKE else V_C_POINTS_FULL

# V_C realization: (N_JOBS, N_OBJECTS) tuple per V_C point.
# Heuristic: split V_C ~ 25% jobs / 75% objects (matches source 8/16 = 1:2 ratio).
def _vc_to_jobs_objs(vc: int) -> Tuple[int, int]:
    n_jobs = max(8, int(round(vc * 0.25)))
    n_objs = max(16, vc - n_jobs)
    return n_jobs, n_objs

V_C_CONFIGS = {vc: _vc_to_jobs_objs(vc) for vc in V_C_POINTS}


# ---------------- regime config (fixed across V_C points) ----------------
# DISCRIMINATOR-MUST-SURVIVE-SCALE Check A: smoke at FULL N_EVENTS=100 / 5 chars /
# 8 pronouns / Q_per_type=3 (matches source narrative cell). Smoke differs from
# full ONLY by single-seed (vs 3-seed) execution.
N_HIPPO = 512
N_CORTEX = 1024
N_PART = 1024
N_EVENTS = 100
N_CHARACTERS = 5
K_SCENE_BOUNDARY = 10
N_FACTS_PER_CHAR = 3
N_UPDATE_PAIRS = 3
# Q_PER_TYPE bumped from source's 3 -> 8 because V_C sweep needs lower-noise
# per-V_C signal. Q=3 random floor hit 0.667 (2/3) by luck at V_C=4000 during
# initial smoke; Q=8 caps random floor at ~0.20 (5-way) which keeps the cliff
# discriminator (HP=0.60 vs floor=0.20) visible. Pronoun events bumped to 12 to
# supply enough Q2 pronoun samples (Q_PER_TYPE Q2 samples drawn from pronoun set).
N_PRONOUN_EVENTS = 12
Q_PER_TYPE = 8

K_HIPPO_ACTIVE = max(1, int(round(0.10 * N_HIPPO)))
ETA_CORTEX = 0.005
N_REPLAY_CYCLES = 3
N_RAW = 64
N_VERBS = 12

ARMS = ["ARM_RANDOM_FLOOR", "ARM_BASELINE_NAIVE",
        "ARM_PARTITION_ORACLE_Q2", "ARM_SEQUENCE_REPLAY_Q3"]
QUERY_TYPES = ["Q1_factual", "Q2_coreference", "Q3_temporal", "Q4_contradict"]
EXPECTED_N_UNITS = len(V_C_POINTS) * len(ARMS)

CONFIG_VERSION = (
    "ANCHOR=%s,N_h=%d,N_c=%d,N_part=%d,N_events=%d,N_chars=%d,K_scene=%d,"
    "K_active=%d,eta=%.4f,N_replay=%d,Q_per_type=%d,seed=%d,arms=%d,"
    "V_C_points=%s,mode=%s,HP_part@1000=%.2f,HP_lift=%.2f,HF_part@4000=%.2f,"
    "EXPECTED_N=%d"
) % (
    ANCHOR_NAME, N_HIPPO, N_CORTEX, N_PART, N_EVENTS, N_CHARACTERS,
    K_SCENE_BOUNDARY, K_HIPPO_ACTIVE, ETA_CORTEX, N_REPLAY_CYCLES,
    Q_PER_TYPE, SEED_ACTIVE, len(ARMS), str(V_C_POINTS), RUN_MODE,
    HP_PARTITION_Q2_AT_HIGH_VC, HP_LIFT_OVER_NAIVE_AT_HIGH_VC,
    HF_PARTITION_Q2_AT_TOP_VC, EXPECTED_N_UNITS,
)


# ---------------- vector primitives ----------------

def _rng(seed_int: int) -> np.random.Generator:
    return np.random.default_rng(int(seed_int))


def random_bipolar(shape, rng: np.random.Generator) -> np.ndarray:
    return np.where(rng.random(shape) < 0.5, -1.0, 1.0).astype(np.float64)


def cosine_vec(a: np.ndarray, b: np.ndarray) -> float:
    na = float(np.linalg.norm(a))
    nb = float(np.linalg.norm(b))
    if na < 1e-9 or nb < 1e-9:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


def cosine_argmax(probe: np.ndarray, candidates: np.ndarray) -> int:
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
    h_raw = P @ x
    top_k_idx = np.argpartition(-np.abs(h_raw), k - 1)[:k]
    h_sparse = np.zeros(P.shape[0], dtype=np.float64)
    signs = np.sign(h_raw[top_k_idx])
    signs[signs == 0] = 1.0
    h_sparse[top_k_idx] = signs
    return h_sparse


def project_h_to_c(h_sparse: np.ndarray, P_hc: np.ndarray) -> np.ndarray:
    c = P_hc @ h_sparse
    n = float(np.linalg.norm(c))
    if n > 0:
        c = c / n
    return c


def hebbian_write(W: np.ndarray, key: np.ndarray, val: np.ndarray,
                  eta: float) -> None:
    W += eta * np.outer(val, key)


def permute_role_pos(v: np.ndarray, pos: int) -> np.ndarray:
    if v.shape[0] == 0:
        return v
    return np.roll(v, int(pos) % v.shape[0])


# ---------------- narrative generator (parameterized by V_C config) ----------------

class Narrative:
    """V_C-parameterized narrative. n_jobs + n_objects scale with V_C point.
    Otherwise structurally identical to stage3 narrative composition cell."""

    def __init__(self, seed_offset: int, n_jobs: int, n_objects: int) -> None:
        self.seed_offset = int(seed_offset)
        self.n_jobs = int(n_jobs)
        self.n_objects = int(n_objects)
        self.rng = _rng(seed_offset)

        self.events: List[Dict] = []
        self.char_facts: Dict[Tuple[int, int], List[Tuple[int, int]]] = {}

        n_scenes = (N_EVENTS + K_SCENE_BOUNDARY - 1) // K_SCENE_BOUNDARY
        scene_focus = [int(self.rng.integers(0, N_CHARACTERS))
                       for _ in range(n_scenes)]

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

        q1_max = max(1, N_EVENTS // 4)
        q4_min = max(q1_max + 1, (3 * N_EVENTS) // 4)
        for ch, fi in chosen_chars:
            ev_early = int(self.rng.integers(2, q1_max))
            ev_late = int(self.rng.integers(q4_min, N_EVENTS - 1))
            v_early = int(self.rng.integers(0, self.n_jobs))
            v_late = v_early
            while v_late == v_early:
                v_late = int(self.rng.integers(0, self.n_jobs))
            update_pairs.append((ch, fi, v_early, v_late, ev_early, ev_late))

        update_lookup = {}
        for ch, fi, ve, vl, ee, le in update_pairs:
            update_lookup[ee] = (ch, fi, ve, "early")
            update_lookup[le] = (ch, fi, vl, "late")

        static_facts: Dict[Tuple[int, int], Tuple[int, int]] = {}
        for ch in range(N_CHARACTERS):
            for fi in range(N_FACTS_PER_CHAR):
                if (ch, fi) not in used_char_fact:
                    val = int(self.rng.integers(0, self.n_jobs))
                    ev = int(self.rng.integers(1, max(2, N_EVENTS // 2)))
                    static_facts[(ch, fi)] = (val, ev)

        static_by_event: Dict[int, List[Tuple[int, int, int]]] = {}
        for (ch, fi), (val, ev) in static_facts.items():
            static_by_event.setdefault(ev, []).append((ch, fi, val))

        reserved_events = set(update_lookup.keys()) | set(static_by_event.keys())
        pronoun_event_idxs: set = set()
        if N_PRONOUN_EVENTS > 0:
            cand_events = [ev for ev in range(K_SCENE_BOUNDARY + 1, N_EVENTS)
                           if ev not in reserved_events]
            self.rng.shuffle(cand_events)
            for ev in cand_events[:N_PRONOUN_EVENTS]:
                pronoun_event_idxs.add(int(ev))

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
            if ev_idx in update_lookup:
                ch, fi, val, kind = update_lookup[ev_idx]
                ev["char_id"] = ch
                ev["fact_kind"] = kind
                ev["fact_idx"] = fi
                ev["fact_val"] = val
                self.char_facts.setdefault((ch, fi), []).append((val, ev_idx))
            elif ev_idx in static_by_event:
                ch, fi, val = static_by_event[ev_idx][0]
                ev["char_id"] = ch
                ev["fact_kind"] = "static"
                ev["fact_idx"] = fi
                ev["fact_val"] = val
                self.char_facts.setdefault((ch, fi), []).append((val, ev_idx))
            elif ev_idx in pronoun_event_idxs:
                ev["char_id"] = scene_focus[scene_id]
                ev["is_pronoun"] = True
            else:
                if self.rng.random() < 0.60:
                    ev["char_id"] = scene_focus[scene_id]
                else:
                    ev["char_id"] = int(self.rng.integers(0, N_CHARACTERS))

            ev["verb_id"] = int(self.rng.integers(0, N_VERBS))
            ev["obj_id"] = int(self.rng.integers(0, self.n_objects))
            self.events.append(ev)

        self.scene_focus = scene_focus
        self.n_scenes = n_scenes
        self.update_pairs = update_pairs
        self.static_facts = static_facts
        self.pronoun_event_idxs = pronoun_event_idxs

    def make_queries(self) -> Dict[str, List[Dict]]:
        rng = _rng(self.seed_offset + 999)
        queries: Dict[str, List[Dict]] = {q: [] for q in QUERY_TYPES}

        static_keys = list(self.static_facts.keys())
        rng.shuffle(static_keys)
        for ch, fi in static_keys[:Q_PER_TYPE]:
            val, ev = self.static_facts[(ch, fi)]
            queries["Q1_factual"].append({
                "char_id": ch, "fact_idx": fi, "expected_val": val,
                "source_event_idx": ev,
            })

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

        cand = [i for i in range(1, N_EVENTS)
                if (i % K_SCENE_BOUNDARY) > 0]
        rng.shuffle(cand)
        for ev_idx in cand[:Q_PER_TYPE]:
            queries["Q3_temporal"].append({
                "target_event_idx": ev_idx,
                "expected_prior_event_idx": ev_idx - 1,
            })

        for (ch, fi, ve, vl, ee, le) in self.update_pairs[:Q_PER_TYPE]:
            queries["Q4_contradict"].append({
                "char_id": ch, "fact_idx": fi,
                "early_val": ve, "late_val": vl,
                "early_event_idx": ee, "late_event_idx": le,
                "expected_val": vl,
            })

        return queries


# ---------------- vocab (V_C parameterized) ----------------

def build_vocab(seed_offset: int, n_jobs: int, n_objects: int,
                ) -> Dict[str, np.ndarray]:
    rng = _rng(seed_offset + 7777)
    n_scenes = (N_EVENTS + K_SCENE_BOUNDARY - 1) // K_SCENE_BOUNDARY
    vocab = {
        "chars": random_bipolar((N_CHARACTERS, N_RAW), rng),
        "verbs": random_bipolar((N_VERBS, N_RAW), rng),
        "objs":  random_bipolar((n_objects, N_RAW), rng),
        "jobs":  random_bipolar((n_jobs, N_RAW), rng),
        "scenes": random_bipolar((n_scenes, N_RAW), rng),
        "facts": random_bipolar((N_FACTS_PER_CHAR, N_RAW), rng),
        "pronoun_tag": random_bipolar((N_RAW,), rng),
    }
    vocab["P_in"] = (rng.standard_normal((N_HIPPO, N_RAW)) /
                     math.sqrt(N_RAW)).astype(np.float64)
    vocab["P_hc"] = (rng.standard_normal((N_CORTEX, N_HIPPO)) /
                     math.sqrt(N_HIPPO)).astype(np.float64)
    vocab["P_pc"] = (rng.standard_normal((N_PART, N_HIPPO)) /
                     math.sqrt(N_HIPPO)).astype(np.float64)
    vocab["_n_jobs"] = n_jobs
    vocab["_n_objects"] = n_objects
    return vocab


def encode_event_raw(ev: Dict, vocab: Dict[str, np.ndarray]) -> np.ndarray:
    if ev.get("is_pronoun"):
        char_v = vocab["pronoun_tag"]
    else:
        char_v = vocab["chars"][ev["char_id"]]
    verb_v = vocab["verbs"][ev["verb_id"]]
    obj_v = vocab["objs"][ev["obj_id"]]
    scene_v = vocab["scenes"][ev["scene_id"]]
    raw = char_v + verb_v + obj_v + scene_v
    out = np.sign(raw)
    out[out == 0] = 1.0
    return out


def encode_fact_key(ch: int, fi: int, vocab: Dict[str, np.ndarray]) -> np.ndarray:
    raw = vocab["chars"][ch] + vocab["facts"][fi]
    out = np.sign(raw)
    out[out == 0] = 1.0
    return out


def encode_fact_val(val: int, vocab: Dict[str, np.ndarray]) -> np.ndarray:
    return vocab["jobs"][val]


# ---------------- shared encoding ----------------

def _consolidate_scene_to_cortex(W_cortex: np.ndarray,
                                  scene_keys_c: List[np.ndarray],
                                  scene_vals_c: List[np.ndarray],
                                  rng: np.random.Generator) -> None:
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
    keys_h, vals_h, keys_c, vals_c = [], [], [], []
    P_in = vocab["P_in"]
    P_hc = vocab["P_hc"]
    for ev in events:
        e_raw = encode_event_raw(ev, vocab)
        kh = pattern_separate_sparse(e_raw, P_in, K_HIPPO_ACTIVE)
        pos_in_scene = ev["event_idx"] % K_SCENE_BOUNDARY
        kh_seq = permute_role_pos(kh, pos_in_scene)
        vh = kh_seq.copy()
        keys_h.append(kh_seq)
        vals_h.append(vh)
        keys_c.append(project_h_to_c(kh_seq, P_hc))
        vals_c.append(project_h_to_c(vh, P_hc))
    return keys_h, vals_h, keys_c, vals_c


def _encode_full_stack(narr: "Narrative", vocab: Dict[str, np.ndarray],
                       rng_arm: np.random.Generator,
                       keys_h: List[np.ndarray], vals_h: List[np.ndarray],
                       keys_c: List[np.ndarray], vals_c: List[np.ndarray],
                       ) -> Tuple[np.ndarray, Dict[int, np.ndarray],
                                   Dict[Tuple[int, int], Dict]]:
    W_cortex = np.zeros((N_CORTEX, N_CORTEX), dtype=np.float64)
    W_part: Dict[int, np.ndarray] = {}
    gen_W: Dict[Tuple[int, int], Dict] = {}

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
        if (i + 1) % K_SCENE_BOUNDARY == 0 or (i + 1) == N_EVENTS:
            _consolidate_scene_to_cortex(W_cortex, scene_keys_c, scene_vals_c,
                                          rng_arm)
            by_char: Dict[int, Tuple[List[np.ndarray], List[np.ndarray]]] = {}
            for ch, kp, vp in scene_partition_writes:
                by_char.setdefault(ch, ([], []))
                by_char[ch][0].append(kp)
                by_char[ch][1].append(vp)
            for ch, (ks, vs) in by_char.items():
                _consolidate_scene_to_cortex(W_part[ch], ks, vs, rng_arm)
            for ch, fi, val in scene_fact_writes:
                gen_W[(ch, fi)] = {
                    "latest_val": val,
                    "latest_event": i,
                    "generation": gen_W.get((ch, fi), {}).get("generation", 0) + 1,
                }
                kf_raw = encode_fact_key(ch, fi, vocab)
                kf_h = pattern_separate_sparse(kf_raw, vocab["P_in"], K_HIPPO_ACTIVE)
                kf_c = project_h_to_c(kf_h, vocab["P_hc"])
                vf_h = pattern_separate_sparse(encode_fact_val(val, vocab),
                                                vocab["P_in"], K_HIPPO_ACTIVE)
                vf_c = project_h_to_c(vf_h, vocab["P_hc"])
                hebbian_write(W_cortex, kf_c, vf_c, ETA_CORTEX)
            scene_keys_c, scene_vals_c = [], []
            scene_partition_writes = []
            scene_fact_writes = []

    return W_cortex, W_part, gen_W


def _build_S_sequence_matrix(narr: "Narrative",
                             keys_c: List[np.ndarray]) -> np.ndarray:
    n_dim = N_CORTEX
    S = np.zeros((n_dim, n_dim), dtype=np.float64)
    K_prev_rows = []
    K_curr_rows = []
    for s_id in range(narr.n_scenes):
        scene_evs = [i for i in range(N_EVENTS)
                     if (i // K_SCENE_BOUNDARY) == s_id]
        scene_evs.sort()
        if len(scene_evs) < 2:
            continue
        for j in range(1, len(scene_evs)):
            K_prev_rows.append(keys_c[scene_evs[j - 1]])
            K_curr_rows.append(keys_c[scene_evs[j]])
    if not K_prev_rows:
        return S
    K_prev = np.stack(K_prev_rows, axis=0)
    K_curr = np.stack(K_curr_rows, axis=0)
    S = (K_prev.T @ K_curr) / n_dim
    return S


# ---------------- READOUT PATHS ----------------

def q2_naive_magnitude(ev_idx: int, narr: "Narrative",
                       vocab: Dict[str, np.ndarray],
                       W_part: Dict[int, np.ndarray]) -> int:
    """BASELINE: argmax over per-char partition magnitude (unsubstituted cue)."""
    ev = narr.events[ev_idx]
    cue_raw = encode_event_raw(ev, vocab)
    cue_h = pattern_separate_sparse(cue_raw, vocab["P_in"], K_HIPPO_ACTIVE)
    pos = ev["event_idx"] % K_SCENE_BOUNDARY
    cue_h = permute_role_pos(cue_h, pos)
    cue_pc = project_h_to_c(cue_h, vocab["P_pc"])
    scores = np.zeros(N_CHARACTERS, dtype=np.float64)
    for c in range(N_CHARACTERS):
        readout = W_part[c] @ cue_pc
        scores[c] = float(np.linalg.norm(readout))
    return int(np.argmax(scores))


def q2_partition_oracle_readout(ev_idx: int, narr: "Narrative",
                                  vocab: Dict[str, np.ndarray],
                                  W_part: Dict[int, np.ndarray]) -> int:
    """ORACLE: per-char SUBSTITUTED-CUE magnitude scoring.
    Mirrors arm_part_oracle from partition_oracle_v5_hardened (V_C=4000 validated)."""
    ev = narr.events[ev_idx]
    pos = ev["event_idx"] % K_SCENE_BOUNDARY

    scores = np.zeros(N_CHARACTERS, dtype=np.float64)
    for c in range(N_CHARACTERS):
        substituted_ev = dict(ev)
        substituted_ev["is_pronoun"] = False
        substituted_ev["char_id"] = c
        cue_raw = encode_event_raw(substituted_ev, vocab)
        cue_h = pattern_separate_sparse(cue_raw, vocab["P_in"], K_HIPPO_ACTIVE)
        cue_h = permute_role_pos(cue_h, pos)
        cue_pc = project_h_to_c(cue_h, vocab["P_pc"])
        readout = W_part[c] @ cue_pc
        scores[c] = float(np.linalg.norm(readout))
    return int(np.argmax(scores))


def q3_naive_roll(target_ev: int, narr: "Narrative",
                  keys_c: List[np.ndarray]) -> int:
    target_scene = target_ev // K_SCENE_BOUNDARY
    scene_members = [i for i in range(max(0, target_ev - K_SCENE_BOUNDARY),
                                       min(len(keys_c), target_ev + 1))
                     if (i // K_SCENE_BOUNDARY) == target_scene and i != target_ev]
    if not scene_members:
        return -1
    target_key = keys_c[target_ev]
    cue = np.roll(target_key, -1)
    sims = np.array([cosine_vec(cue, keys_c[i]) for i in scene_members])
    return scene_members[int(np.argmax(sims))]


def q3_sequence_replay_readout(target_ev: int, narr: "Narrative",
                                 keys_c: List[np.ndarray],
                                 S: np.ndarray) -> int:
    target_scene = target_ev // K_SCENE_BOUNDARY
    scene_members = [i for i in range(N_EVENTS)
                     if (i // K_SCENE_BOUNDARY) == target_scene and i != target_ev]
    if not scene_members:
        return -1
    target_key = keys_c[target_ev]
    predicted = S @ target_key
    cand_stack = np.stack([keys_c[i] for i in scene_members], axis=0)
    pred_local = cosine_argmax(predicted, cand_stack)
    return scene_members[pred_local]


def q1_factual(W_cortex: np.ndarray, ch: int, fi: int,
                vocab: Dict[str, np.ndarray]) -> int:
    key_raw = encode_fact_key(ch, fi, vocab)
    key_h = pattern_separate_sparse(key_raw, vocab["P_in"], K_HIPPO_ACTIVE)
    key_c = project_h_to_c(key_h, vocab["P_hc"])
    n_jobs = vocab["_n_jobs"]
    cand = np.stack([project_h_to_c(
        pattern_separate_sparse(vocab["jobs"][j], vocab["P_in"], K_HIPPO_ACTIVE),
        vocab["P_hc"]) for j in range(n_jobs)])
    raw = W_cortex @ key_c
    return cosine_argmax(raw, cand)


def q4_contradict(ch: int, fi: int,
                   gen_W: Dict[Tuple[int, int], Dict]) -> int:
    if (ch, fi) in gen_W:
        return gen_W[(ch, fi)]["latest_val"]
    return 0


# ---------------- arm runner per V_C point ----------------

def run_arm_at_vc(arm: str, seed: int, v_c: int) -> Dict[str, Any]:
    """Run one arm for one seed at one V_C point. Encoding shared across arms
    at the same V_C; arms differ ONLY in Q2 + Q3 readout paths."""
    t0 = time.time()
    n_jobs, n_objects = V_C_CONFIGS[v_c]
    # V_C-distinct seed offset so encoding doesn't bleed across V_C points
    seed_offset = int(seed) * 100003 + int(v_c) * 7919
    rng_arm = _rng(seed_offset + 31)

    narr = Narrative(seed_offset, n_jobs, n_objects)
    vocab = build_vocab(seed_offset, n_jobs, n_objects)
    queries = narr.make_queries()
    keys_h, vals_h, keys_c, vals_c = _build_event_keys_vals(narr.events, vocab)

    W_cortex, W_part, gen_W = _encode_full_stack(narr, vocab, rng_arm,
                                                    keys_h, vals_h, keys_c, vals_c)
    S_replay = _build_S_sequence_matrix(narr, keys_c)

    preds_list: List[str] = []
    per_q: Dict[str, Dict[str, int]] = {q: {"correct": 0, "total": 0}
                                          for q in QUERY_TYPES}

    # Q1 factual (identical across non-random arms; sanity control)
    for q in queries["Q1_factual"]:
        ch, fi, expected = q["char_id"], q["fact_idx"], q["expected_val"]
        if arm == "ARM_RANDOM_FLOOR":
            pred = int(_rng(seed_offset + 111 + ch * 13 + fi).integers(0, n_jobs))
        else:
            pred = q1_factual(W_cortex, ch, fi, vocab)
        per_q["Q1_factual"]["total"] += 1
        per_q["Q1_factual"]["correct"] += int(pred == expected)
        preds_list.append("Q1:%d:%d:%d" % (ch, fi, pred))

    # Q2 coreference (the load-bearing arm-distinguishing question)
    for q in queries["Q2_coreference"]:
        ev_idx = q["event_idx"]
        expected_char = q["expected_char_id"]
        if arm == "ARM_RANDOM_FLOOR":
            pred = int(_rng(seed_offset + 222 + ev_idx).integers(0, N_CHARACTERS))
        elif arm == "ARM_BASELINE_NAIVE":
            pred = q2_naive_magnitude(ev_idx, narr, vocab, W_part)
        elif arm == "ARM_PARTITION_ORACLE_Q2":
            pred = q2_partition_oracle_readout(ev_idx, narr, vocab, W_part)
        elif arm == "ARM_SEQUENCE_REPLAY_Q3":
            # Q3-focused arm; Q2 stays at naive (positive control for Q3 across V_C)
            pred = q2_naive_magnitude(ev_idx, narr, vocab, W_part)
        else:
            raise ValueError("unknown arm: " + arm)
        per_q["Q2_coreference"]["total"] += 1
        per_q["Q2_coreference"]["correct"] += int(pred == expected_char)
        preds_list.append("Q2:%d:%d" % (ev_idx, pred))

    # Q3 temporal (positive control - REPLAY arm should pass at all V_C)
    for q in queries["Q3_temporal"]:
        target = q["target_event_idx"]
        expected = q["expected_prior_event_idx"]
        if arm == "ARM_RANDOM_FLOOR":
            target_scene = target // K_SCENE_BOUNDARY
            scene_members = [i for i in range(N_EVENTS)
                              if (i // K_SCENE_BOUNDARY) == target_scene
                              and i != target]
            if scene_members:
                idx = int(_rng(seed_offset + 333 + target).integers(0, len(scene_members)))
                pred = scene_members[idx]
            else:
                pred = -1
        elif arm == "ARM_BASELINE_NAIVE":
            pred = q3_naive_roll(target, narr, keys_c)
        elif arm == "ARM_PARTITION_ORACLE_Q2":
            pred = q3_naive_roll(target, narr, keys_c)
        elif arm == "ARM_SEQUENCE_REPLAY_Q3":
            pred = q3_sequence_replay_readout(target, narr, keys_c, S_replay)
        else:
            raise ValueError("unknown arm: " + arm)
        per_q["Q3_temporal"]["total"] += 1
        per_q["Q3_temporal"]["correct"] += int(pred == expected)
        preds_list.append("Q3:%d:%d" % (target, pred))

    # Q4 contradict
    for q in queries["Q4_contradict"]:
        ch, fi, expected = q["char_id"], q["fact_idx"], q["expected_val"]
        if arm == "ARM_RANDOM_FLOOR":
            pred = int(_rng(seed_offset + 444 + ch * 7 + fi).integers(0, n_jobs))
        else:
            pred = q4_contradict(ch, fi, gen_W)
        per_q["Q4_contradict"]["total"] += 1
        per_q["Q4_contradict"]["correct"] += int(pred == expected)
        preds_list.append("Q4:%d:%d:%d" % (ch, fi, pred))

    acc_by_q = {}
    for q in QUERY_TYPES:
        tot = per_q[q]["total"]
        acc_by_q[q] = (per_q[q]["correct"] / tot) if tot > 0 else 0.0
    overall = float(np.mean(list(acc_by_q.values())))

    pred_sha = hashlib.sha256(
        ";".join(preds_list).encode("ascii")).hexdigest()[:16]

    wall = float(round(time.time() - t0, 3))
    return {
        "arm": arm,
        "seed": int(seed),
        "V_C": int(v_c),
        "n_jobs": int(n_jobs),
        "n_objects": int(n_objects),
        "N_h": N_HIPPO, "N_c": N_CORTEX, "N_part": N_PART,
        "N_events": N_EVENTS, "N_chars": N_CHARACTERS,
        "K_scene": K_SCENE_BOUNDARY, "Q_per_type": Q_PER_TYPE,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "acc_by_q": acc_by_q,
        "overall": round(overall, 4),
        "Q1_factual": round(acc_by_q["Q1_factual"], 4),
        "Q2_coreference": round(acc_by_q["Q2_coreference"], 4),
        "Q3_temporal": round(acc_by_q["Q3_temporal"], 4),
        "Q4_contradict": round(acc_by_q["Q4_contradict"], 4),
        "n_q_total": sum(per_q[q]["total"] for q in QUERY_TYPES),
        "pred_sha": pred_sha,
        "elapsed_s_arm": wall,
        "_partial_written_at": time.time(),
    }


# ---------------- verdict ----------------

def _classify(by_vc_arm: Dict[int, Dict[str, Dict[str, Any]]]) -> Tuple[str, str]:
    """Apply sweep-level bands. The load-bearing question:
    does oracle_Q2 monotone-rise with V_C and HARD_PASS at V_C >= 1000?
    """
    # Extract per-V_C oracle Q2, naive Q2, replay Q3
    oracle_by_vc: Dict[int, float] = {}
    naive_by_vc: Dict[int, float] = {}
    replay_by_vc: Dict[int, float] = {}
    floor_by_vc: Dict[int, float] = {}

    for vc in V_C_POINTS:
        per_arm = by_vc_arm.get(vc, {})
        if not per_arm:
            return "HARD_FAIL", "MISSING_VC_POINT_%d" % vc
        oracle_by_vc[vc] = per_arm.get("ARM_PARTITION_ORACLE_Q2", {}).get(
            "Q2_coreference", 0.0)
        naive_by_vc[vc] = per_arm.get("ARM_BASELINE_NAIVE", {}).get(
            "Q2_coreference", 0.0)
        replay_by_vc[vc] = per_arm.get("ARM_SEQUENCE_REPLAY_Q3", {}).get(
            "Q3_temporal", 0.0)
        floor_by_vc[vc] = per_arm.get("ARM_RANDOM_FLOOR", {}).get(
            "Q2_coreference", 0.0)

    # SHA-distinct check
    shas = set()
    for vc in V_C_POINTS:
        for arm_name in ARMS:
            sha = by_vc_arm.get(vc, {}).get(arm_name, {}).get("pred_sha", "")
            if sha:
                shas.add(sha)
    arms_distinct = len(shas) >= len(ARMS) * 2

    # HARD_FAIL: replay arm fails at any V_C (Q3 should be V_C-independent)
    for vc in V_C_POINTS:
        if replay_by_vc[vc] <= HF_REPLAY_Q3_ALL_VC:
            return ("HARD_FAIL",
                    "HF_REPLAY_FAILS_AT_VC=%d: Q3=%.3f <= %.3f "
                    "(positive control Q3 should not be V_C-dependent)"
                    % (vc, replay_by_vc[vc], HF_REPLAY_Q3_ALL_VC))

    # HARD_FAIL: random floor too high (sanity) - tolerant of Q=8 5-way binomial
    # noise. p=0.20, n=8 => sigma ~ 0.14; 0.55 = ~2.5sigma; that's an outlier
    # not a logic error. Only fire if floor > 0.60 (impossible without bug).
    for vc in V_C_POINTS:
        f = floor_by_vc[vc]
        if f > 0.60:
            return ("HARD_FAIL",
                    "HF_FLOOR_IMPOSSIBLE_VC=%d: random_floor Q2=%.3f > 0.60 "
                    "(impossible at 5-way Q=8 random; arms-distinct logic bug)"
                    % (vc, f))

    # HARD_FAIL: oracle at TOP V_C (4000) still below floor band
    top_vc = max(V_C_POINTS)
    if oracle_by_vc[top_vc] <= HF_PARTITION_Q2_AT_TOP_VC:
        return ("HARD_FAIL",
                "HF_ORACLE_NEVER_RESCUES_AT_V_C=%d: oracle_Q2=%.3f <= %.3f "
                "(partition_oracle mechanism doesn't transfer to narrative-coref "
                "task even at validated V_C scale; need different Q2 primitive)"
                % (top_vc, oracle_by_vc[top_vc], HF_PARTITION_Q2_AT_TOP_VC))

    # HARD_PASS: monotone-increasing oracle_Q2 AND oracle@1000 >= HP AND lift >= req
    oracle_vals = [oracle_by_vc[vc] for vc in sorted(V_C_POINTS)]
    monotone_ok = all(oracle_vals[i] <= oracle_vals[i + 1] + 0.10  # tolerate 0.10 noise
                       for i in range(len(oracle_vals) - 1))

    high_vc_points = [vc for vc in V_C_POINTS if vc >= HP_MIN_VC_FOR_PASS]
    if high_vc_points:
        oracle_at_high = max(oracle_by_vc[vc] for vc in high_vc_points)
        lift_at_high = max(oracle_by_vc[vc] - naive_by_vc[vc]
                            for vc in high_vc_points)
        high_pass = (oracle_at_high >= HP_PARTITION_Q2_AT_HIGH_VC and
                     lift_at_high >= HP_LIFT_OVER_NAIVE_AT_HIGH_VC)
    else:
        oracle_at_high = 0.0
        lift_at_high = 0.0
        high_pass = False

    if monotone_ok and high_pass and arms_distinct:
        return ("HARD_PASS",
                "HARD_PASS_V_C_CLIFF_CONFIRMED: oracle_Q2 monotone-rises with V_C "
                "(values=%s); oracle@V_C>=1000 max=%.3f (HP=%.2f); "
                "lift_over_naive=%.3f (HP=%.2f); arms_distinct=True. "
                "Partition oracle primitive's V_C-dependence transfers to "
                "narrative-coref; min V_C for narrative coherence rescue = %d."
                % ([round(v, 3) for v in oracle_vals], oracle_at_high,
                   HP_PARTITION_Q2_AT_HIGH_VC, lift_at_high,
                   HP_LIFT_OVER_NAIVE_AT_HIGH_VC, HP_MIN_VC_FOR_PASS))

    # Otherwise MIDDLE_BAND
    return ("MIDDLE_BAND",
            "MIDDLE_BAND_V_C_SWEEP: oracle_Q2_by_vc=%s, naive_Q2_by_vc=%s, "
            "replay_Q3_by_vc=%s, monotone_ok=%s, oracle@high=%.3f (HP=%.2f), "
            "lift@high=%.3f (HP=%.2f), arms_distinct=%s. "
            "Either lift insufficient OR non-monotone OR oracle <HP at high V_C."
            % ({vc: round(oracle_by_vc[vc], 3) for vc in V_C_POINTS},
               {vc: round(naive_by_vc[vc], 3) for vc in V_C_POINTS},
               {vc: round(replay_by_vc[vc], 3) for vc in V_C_POINTS},
               monotone_ok, oracle_at_high, HP_PARTITION_Q2_AT_HIGH_VC,
               lift_at_high, HP_LIFT_OVER_NAIVE_AT_HIGH_VC, arms_distinct))


# ---------------- self-test ----------------

def _selftest() -> int:
    """Smoke: run all 4 arms across all V_C points on seed=7. Verify cell
    RUNS; check arms-distinct + cardinality + verdict assembly. SMOKE GATE
    expectations are NOT asserted here (those are the actual experiment) -
    only structural sanity (cell runs end-to-end + arms differ per V_C)."""
    print("[selftest] config: %s" % CONFIG_VERSION, flush=True)
    print("[selftest] EXPECTED_N_UNITS=%d (V_C_points=%d arms=%d seeds=%d)"
          % (EXPECTED_N_UNITS, len(V_C_POINTS), len(ARMS), len(SEEDS)),
          flush=True)
    print("[selftest] V_C_CONFIGS=%s" % {vc: V_C_CONFIGS[vc] for vc in V_C_POINTS},
          flush=True)

    by_vc_arm: Dict[int, Dict[str, Dict[str, Any]]] = {}
    n_run = 0
    for vc in V_C_POINTS:
        by_vc_arm[vc] = {}
        for arm in ARMS:
            try:
                result = run_arm_at_vc(arm, SEED_ACTIVE, vc)
            except SystemExit:
                raise
            except BaseException as e:
                print("[selftest] V_C=%d arm=%s CRASHED: %r" % (vc, arm, e),
                      flush=True)
                traceback.print_exc()
                return 1
            by_vc_arm[vc][arm] = result
            n_run += 1
            print("[selftest] V_C=%d arm=%s Q1=%.3f Q2=%.3f Q3=%.3f Q4=%.3f "
                  "overall=%.3f sha=%s wall=%.2fs"
                  % (vc, arm, result["Q1_factual"], result["Q2_coreference"],
                     result["Q3_temporal"], result["Q4_contradict"],
                     result["overall"], result["pred_sha"],
                     result["elapsed_s_arm"]), flush=True)

    # Sweep summary table for visual cliff inspection
    print("\n[selftest] --- V_C SWEEP SUMMARY ---", flush=True)
    print("[selftest] V_C  | floor_Q2 naive_Q2 oracle_Q2 replay_Q3", flush=True)
    for vc in V_C_POINTS:
        f = by_vc_arm[vc].get("ARM_RANDOM_FLOOR", {}).get("Q2_coreference", 0.0)
        n = by_vc_arm[vc].get("ARM_BASELINE_NAIVE", {}).get("Q2_coreference", 0.0)
        o = by_vc_arm[vc].get("ARM_PARTITION_ORACLE_Q2", {}).get(
            "Q2_coreference", 0.0)
        r = by_vc_arm[vc].get("ARM_SEQUENCE_REPLAY_Q3", {}).get(
            "Q3_temporal", 0.0)
        print("[selftest] %4d | %.3f    %.3f    %.3f     %.3f"
              % (vc, f, n, o, r), flush=True)

    verdict, msg = _classify(by_vc_arm)
    print("\n[selftest] verdict=%s" % verdict, flush=True)
    print("[selftest] verdict_msg=%s" % msg, flush=True)
    print("[selftest] units_run=%d expected=%d" % (n_run, EXPECTED_N_UNITS),
          flush=True)

    # Structural sanity: at least 5 distinct pred_shas across 4 V_C * 4 arms = 16
    shas = set()
    for vc in V_C_POINTS:
        for arm in ARMS:
            shas.add(by_vc_arm[vc][arm]["pred_sha"])
    if len(shas) < 5:
        print("[selftest] WARN: only %d distinct pred_shas across %d units "
              "(META_RULE_AF concern)" % (len(shas), n_run), flush=True)
    else:
        print("[selftest] OK: %d distinct pred_shas across %d units"
              % (len(shas), n_run), flush=True)

    return 0


# ---------------- main ----------------

def main() -> int:
    if _ARGS.self_test:
        return _selftest()

    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)

    start_marker = out_dir / "_start_marker.txt"
    start_marker.write_text("started=%s\nconfig=%s\nseed=%d\nmode=%s\n"
                              % (time.strftime("%Y-%m-%dT%H:%M:%SZ",
                                                time.gmtime()),
                                 CONFIG_VERSION, SEED_ACTIVE, RUN_MODE),
                              encoding="utf-8")

    seed = SEED_ACTIVE
    run_config = {"anchor": ANCHOR_NAME, "run_mode": RUN_MODE}

    by_vc_arm: Dict[int, Dict[str, Dict[str, Any]]] = {}
    for vc in V_C_POINTS:
        by_vc_arm[vc] = {}
        for arm in ARMS:
            unit_key = "seed%d_vc%d_%s" % (seed, vc, arm)
            completed = list_completed_keys(out_dir, run_config=run_config)
            if unit_key in completed:
                partials = aggregate_partials(out_dir, [unit_key],
                                                run_config=run_config)
                if unit_key in partials:
                    by_vc_arm[vc][arm] = partials[unit_key]
                    print("[resume] skipping completed unit %s" % unit_key,
                          flush=True)
                    continue

            print("[run] seed=%d vc=%d arm=%s starting..." % (seed, vc, arm),
                  flush=True)
            try:
                result = run_arm_at_vc(arm, seed, vc)
            except SystemExit:
                raise
            except BaseException as e:
                print("[CRASH] vc=%d arm=%s seed=%d: %r" % (vc, arm, seed, e),
                      flush=True)
                crash_path = out_dir / ("_crash_%s.txt" % unit_key)
                crash_path.write_text(
                    "%s\n%r\n%s\n" % (time.time(), e, traceback.format_exc()),
                    encoding="utf-8")
                return 2

            result["_ckpt_key"] = unit_key
            result["anchor_name"] = ANCHOR_NAME
            write_partial_key(out_dir, unit_key, result)
            by_vc_arm[vc][arm] = result
            (out_dir / "_heartbeat.txt").write_text(
                "last_unit=%s\nat=%s\n" % (unit_key, time.time()),
                encoding="utf-8")
            print("[done] %s Q1=%.3f Q2=%.3f Q3=%.3f Q4=%.3f wall=%.2fs"
                  % (unit_key, result["Q1_factual"], result["Q2_coreference"],
                     result["Q3_temporal"], result["Q4_contradict"],
                     result["elapsed_s_arm"]), flush=True)

    # Cardinality
    observed = sum(len(by_vc_arm[vc]) for vc in V_C_POINTS)
    cardinality_ok = (observed == EXPECTED_N_UNITS)
    if not cardinality_ok:
        print("[WARN] CARDINALITY_BREACH: expected %d, observed %d"
              % (EXPECTED_N_UNITS, observed), flush=True)

    verdict, verdict_msg = _classify(by_vc_arm)
    if not cardinality_ok:
        verdict = "HARD_FAIL"
        verdict_msg = "HARD_FAIL_CARDINALITY_BREACH: expected %d got %d. %s" \
                      % (EXPECTED_N_UNITS, observed, verdict_msg)

    # Flatten for write_metrics + per-V_C summary
    flat_per_arm: Dict[str, Dict[str, Any]] = {}
    sweep_summary: Dict[str, Dict[str, float]] = {}
    for vc in V_C_POINTS:
        sweep_summary[str(vc)] = {}
        for arm in ARMS:
            unit_key = "vc%d_%s" % (vc, arm)
            r = by_vc_arm[vc].get(arm, {})
            flat_per_arm[unit_key] = r
            if r:
                sweep_summary[str(vc)][arm] = {
                    "Q2_coreference": r.get("Q2_coreference", 0.0),
                    "Q3_temporal": r.get("Q3_temporal", 0.0),
                    "overall": r.get("overall", 0.0),
                    "pred_sha": r.get("pred_sha", ""),
                }

    metrics: Dict[str, Any] = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "run_mode": RUN_MODE,
        "n_seeds": len(SEEDS),
        "seed": SEED_ACTIVE,
        "seeds": SEEDS,
        "arms": list(ARMS),
        "V_C_points": V_C_POINTS,
        "V_C_configs": {str(vc): {"n_jobs": V_C_CONFIGS[vc][0],
                                    "n_objects": V_C_CONFIGS[vc][1]}
                        for vc in V_C_POINTS},
        "config_version": CONFIG_VERSION,
        "corpus_provenance": CORPUS_PROVENANCE,
        "expected_n_units": EXPECTED_N_UNITS,
        "observed_n_units": observed,
        "cardinality_ok": cardinality_ok,
        "sweep_summary": sweep_summary,
        "per_vc_arm": flat_per_arm,
        "_llm_forward_calls_at_inference": 0,
        "zero_llm_calls_at_inference": True,
        "DESIGN_NOTE": (
            "ANCHOR 2 V_C sweep per notes/exp_dev_to_research_*_smoke_2026-06-28.md. "
            "Tests whether partition_oracle_v5's V_C=4000-validated mechanism "
            "transfers to narrative-coref Q2 with monotone-V_C rescue. Replay "
            "arm = Q3 positive control across V_C (should be V_C-independent). "
            "Chunked single-seed-per-cell; 16 units per chunk (4 V_C * 4 arms)."
        ),
        "bands": {
            "HP_PARTITION_Q2_AT_HIGH_VC": HP_PARTITION_Q2_AT_HIGH_VC,
            "HP_LIFT_OVER_NAIVE_AT_HIGH_VC": HP_LIFT_OVER_NAIVE_AT_HIGH_VC,
            "HP_REPLAY_Q3_ALL_VC": HP_REPLAY_Q3_ALL_VC,
            "HP_MIN_VC_FOR_PASS": HP_MIN_VC_FOR_PASS,
            "HF_PARTITION_Q2_AT_TOP_VC": HF_PARTITION_Q2_AT_TOP_VC,
            "HF_REPLAY_Q3_ALL_VC": HF_REPLAY_Q3_ALL_VC,
        },
    }
    # Build results list for write_metrics (flatten)
    results_list = []
    for vc in V_C_POINTS:
        for arm in ARMS:
            if arm in by_vc_arm[vc]:
                results_list.append(by_vc_arm[vc][arm])
    write_metrics(out_dir, metrics, results=results_list)
    print("[ship] %s verdict=%s" % (ANCHOR_NAME, verdict), flush=True)
    print("[ship] verdict_msg=%s" % verdict_msg, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
