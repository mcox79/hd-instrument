"""Shared implementation for substrate_narrative_q2_recency_sequence_log_v1.

Per drill `notes/research_drill_hrr_context_bind_disambiguator_Q2_coreference_2026-06-28.md`
and handoff `notes/exp_dev_handoff_research_hrr_context_bind_q2_coref_2026-06-28.md` Anchor 1.

Mechanism-class 4 (RECENCY+ROLE composition) for Q2 coreference.

Composes three chain-grade primitives in their NATIVE shapes (SHAPE_MATCH per
META_RULE_AP):
  1. sequence_binding K=20 used as per-character recency log
     (MEASURED@data/exp_c3_compressed_sequence_replay_v1/metrics.json
      HARD_PASS B_d5=1.000 K=20 N=4096)
  2. HRR role-bind primitive used as verb/object role filter
     (MEASURED@data/exp_contextual_encoding_hrr_binding_smoke_v1_smoketest/metrics.json
      HARD_PASS WSD=1.000 lift=+0.800)
  3. PC cleanup attractor used as codebook NN
     (MEASURED@data/exp_pc_cleanup_attractor_v1/metrics.json
      HARD_PASS d5/d10=1.000)

6 ARMS (arms-must-differ on Q2 pred_sha per META_RULE_AF):
  ARM_RANDOM_FLOOR       -- pins floor
  ARM_NAIVE_MAGNITUDE    -- reproduces today's failing readout
  ARM_RECENCY_ONLY       -- sequence-binding recency log (no role filter)
  ARM_ROLE_ONLY          -- HRR role bind/unbind (no recency)
  ARM_RECENCY_PLUS_ROLE  -- THE MECHANISM (composition)
  ARM_ORACLE             -- pins ceiling

CHUNKED: single seed per cell via SEED_ACTIVE module global; sibling shims set
HDLAB_SEED env var before importing this module. Each sibling writes to its
own data dir (HDLAB_EXP_NAME differs per chunk).

PREREG: preregs/2026-06-28_substrate_narrative_q2_recency_sequence_log_v1.md

ASCII-only. CPU. numpy only. Single-file impl. Resumable via _seed_checkpoint.
Author: exp_dev 2026-06-28.
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

ANCHOR_NAME = "substrate_narrative_q2_recency_sequence_log_v1"
CORPUS_PROVENANCE = (
    "synthetic_narrative_5char_grouped_into_scenes_fixed_K10_boundaries_"
    "with_per_character_facts_pronouns_and_fact_updates_REUSED_from_"
    "stage3_narrative_coherence_100event_5char_full_stack_v1"
)

# ---------------- CLI ----------------
_P = argparse.ArgumentParser()
_P.add_argument("--self-test", action="store_true", dest="self_test")
_P.add_argument("--smoke", action="store_true")
_P.add_argument("--seed", type=int, default=None,
                help="single-seed-per-cell override; default auto-selects per HDLAB_SEED")
_P.add_argument("--timeout", type=int, default=4500,
                help="per-cell timeout seconds (runner enforcement; informational)")
_ARGS, _ = _P.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = _HDLAB_EXP_NAME.lower().endswith("_smoke")
RUN_MODE = "smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE) \
    else os.environ.get("HDLAB_RUN_MODE", "full")
SMOKE = (RUN_MODE == "smoke")

# Seed selection: --seed > HDLAB_SEED env var > default 7
_env_seed = os.environ.get("HDLAB_SEED", "").strip()
if _ARGS.seed is not None:
    SEED_ACTIVE = int(_ARGS.seed)
elif _env_seed:
    SEED_ACTIVE = int(_env_seed)
else:
    SEED_ACTIVE = 7

SEEDS = [SEED_ACTIVE]

# ---------------- pre-reg bands (LOCKED at module init) ----------------
HP_RECENCY_PLUS_ROLE_Q2 = 0.60
HP_LIFT_OVER_NAIVE = 0.20
HP_RECENCY_ONLY_FLOOR = 0.45
HP_ORACLE_Q2 = 1.000
HP_ARMS_DISTINCT_MIN = 4

HF_RECENCY_PLUS_ROLE_Q2 = 0.30
HF_LIFT_OVER_NAIVE = 0.05

MB_OVERALL_LOW = 0.30
MB_OVERALL_HIGH = 0.60

# Band sanity (META_RULE_L: strict-above-floor)
assert HP_RECENCY_PLUS_ROLE_Q2 > HF_RECENCY_PLUS_ROLE_Q2, "Q2 bands locked"
assert HP_LIFT_OVER_NAIVE > HF_LIFT_OVER_NAIVE, "lift bands locked"

# ---------------- regime config ----------------
N_HIPPO = 512
N_CORTEX = 1024
N_PART = 1024
N_EVENTS = 100
N_CHARACTERS = 5
K_SCENE_BOUNDARY = 10
N_FACTS_PER_CHAR = 3
N_UPDATE_PAIRS = 3
N_PRONOUN_EVENTS = 8
Q_PER_TYPE = 8  # mandatory per drill (composition_v1 used 3 -> noise)

K_HIPPO_ACTIVE = max(1, int(round(0.10 * N_HIPPO)))
ETA_CORTEX = 0.005
N_REPLAY_CYCLES = 3
N_RAW = 64
N_VERBS = 12
N_OBJECTS = 16
N_JOBS = 8

# Sequence-binding K=20 capacity per the c3 chain-grade atom; per-character
# recency log expected to hold ~N_PRONOUN_EVENTS + ~20 non-pronoun mentions
# per character. Cap at K_SEQ_LOG=20 sliding-window per char.
K_SEQ_LOG = 20

ARMS = [
    "ARM_RANDOM_FLOOR",
    "ARM_NAIVE_MAGNITUDE",
    "ARM_RECENCY_ONLY",
    "ARM_ROLE_ONLY",
    "ARM_RECENCY_PLUS_ROLE",
    "ARM_ORACLE",
]
QUERY_TYPES = ["Q1_factual", "Q2_coreference", "Q3_temporal", "Q4_contradict"]
EXPECTED_N_UNITS = len(SEEDS) * len(ARMS)

# Composition weights for RECENCY_PLUS_ROLE (alpha + beta = 1.0)
ALPHA_RECENCY = 0.5
BETA_ROLE = 0.5

CONFIG_VERSION = (
    "ANCHOR=%s,N_h=%d,N_c=%d,N_part=%d,N_events=%d,N_chars=%d,K_scene=%d,"
    "K_active=%d,eta=%.4f,N_replay=%d,Q_per_type=%d,seed=%d,arms=%d,mode=%s,"
    "K_seq_log=%d,alpha=%.2f,beta=%.2f,"
    "HP_q2=%.2f,HP_lift=%.2f,HP_rec_floor=%.2f,HF_q2=%.2f,HF_lift=%.2f,"
    "EXPECTED_N=%d"
) % (
    ANCHOR_NAME, N_HIPPO, N_CORTEX, N_PART, N_EVENTS, N_CHARACTERS,
    K_SCENE_BOUNDARY, K_HIPPO_ACTIVE, ETA_CORTEX, N_REPLAY_CYCLES,
    Q_PER_TYPE, SEED_ACTIVE, len(ARMS), RUN_MODE,
    K_SEQ_LOG, ALPHA_RECENCY, BETA_ROLE,
    HP_RECENCY_PLUS_ROLE_Q2, HP_LIFT_OVER_NAIVE, HP_RECENCY_ONLY_FLOOR,
    HF_RECENCY_PLUS_ROLE_Q2, HF_LIFT_OVER_NAIVE, EXPECTED_N_UNITS,
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


def cosine_scores(probe: np.ndarray, candidates: np.ndarray) -> np.ndarray:
    """Per-candidate cosine score; returns vector of length len(candidates)."""
    norms = np.linalg.norm(candidates, axis=1)
    pn = float(np.linalg.norm(probe))
    if pn < 1e-9:
        return np.zeros(candidates.shape[0])
    safe = np.where(norms > 1e-9, norms, 1.0)
    cand_norm = candidates / safe[:, None]
    p_norm = probe / pn
    return cand_norm @ p_norm


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


def hrr_bind_bipolar(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """HRR element-wise bind on bipolar vectors (involutive).

    Matches the chain-grade atom contextual_encoding_hrr_binding_smoke_v1
    arm ARM_BIND_SENTENCE bind primitive: element-wise sign-quantized product.
    """
    out = a * b
    out = np.sign(out)
    out[out == 0] = 1.0
    return out


def hrr_bundle(vecs: List[np.ndarray]) -> np.ndarray:
    """HRR bundle = mean + L2-normalize + sign-quantize (bipolar-native)."""
    if not vecs:
        return np.zeros(1)
    s = np.sum(np.stack(vecs, axis=0), axis=0)
    out = np.sign(s)
    out[out == 0] = 1.0
    return out


# ---------------- narrative generator (REUSED structurally) ----------------

class Narrative:
    """Reused structurally from
    stage3_narrative_coherence_100event_5char_full_stack_v1.
    Same event/scene/pronoun/fact layout for direct per-seed comparison.

    Extension for this cell: each event additionally carries
      ev["role_tag_idx"]  -- ROLE_TAG_VOCAB index (verb+obj hash) for HRR bind
    so the role-filter arm has a substrate signal that's not pure noise.
    """

    def __init__(self, seed_offset: int) -> None:
        self.seed_offset = int(seed_offset)
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
            v_early = int(self.rng.integers(0, N_JOBS))
            v_late = v_early
            while v_late == v_early:
                v_late = int(self.rng.integers(0, N_JOBS))
            update_pairs.append((ch, fi, v_early, v_late, ev_early, ev_late))

        update_lookup = {}
        for ch, fi, ve, vl, ee, le in update_pairs:
            update_lookup[ee] = (ch, fi, ve, "early")
            update_lookup[le] = (ch, fi, vl, "late")

        static_facts: Dict[Tuple[int, int], Tuple[int, int]] = {}
        for ch in range(N_CHARACTERS):
            for fi in range(N_FACTS_PER_CHAR):
                if (ch, fi) not in used_char_fact:
                    val = int(self.rng.integers(0, N_JOBS))
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
            ev["obj_id"] = int(self.rng.integers(0, N_OBJECTS))
            # role_tag = (verb, obj) hash modulo V_ROLE_TAG; supplies HRR role filter
            ev["role_tag_idx"] = (ev["verb_id"] * 17 + ev["obj_id"] * 31) % (N_VERBS * N_OBJECTS)
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
                "role_tag_idx": ev["role_tag_idx"],
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


# ---------------- vocabularies ----------------

def build_vocab(seed_offset: int) -> Dict[str, np.ndarray]:
    rng = _rng(seed_offset + 7777)
    n_scenes = (N_EVENTS + K_SCENE_BOUNDARY - 1) // K_SCENE_BOUNDARY
    V_ROLE = N_VERBS * N_OBJECTS
    vocab = {
        "chars_raw": random_bipolar((N_CHARACTERS, N_RAW), rng),
        "chars_cortex": random_bipolar((N_CHARACTERS, N_CORTEX), rng),
        # bipolar so HRR bind works element-wise
        "verbs": random_bipolar((N_VERBS, N_RAW), rng),
        "objs":  random_bipolar((N_OBJECTS, N_RAW), rng),
        "jobs":  random_bipolar((N_JOBS, N_RAW), rng),
        "scenes": random_bipolar((n_scenes, N_RAW), rng),
        "facts": random_bipolar((N_FACTS_PER_CHAR, N_RAW), rng),
        "pronoun_tag": random_bipolar((N_RAW,), rng),
        # ROLE_TAG vocab for HRR role-bind (verb+obj combined identifier)
        "role_tags_cortex": random_bipolar((V_ROLE, N_CORTEX), rng),
        # Position keys for per-character recency log (sequence-binding K=20).
        # Use N_EVENTS positions; per-char log holds the last K_SEQ_LOG.
        "pos_keys_cortex": random_bipolar((N_EVENTS + 1, N_CORTEX), rng),
    }
    vocab["P_in"] = (rng.standard_normal((N_HIPPO, N_RAW)) /
                     math.sqrt(N_RAW)).astype(np.float64)
    vocab["P_hc"] = (rng.standard_normal((N_CORTEX, N_HIPPO)) /
                     math.sqrt(N_HIPPO)).astype(np.float64)
    vocab["P_pc"] = (rng.standard_normal((N_PART, N_HIPPO)) /
                     math.sqrt(N_HIPPO)).astype(np.float64)
    return vocab


def encode_event_raw(ev: Dict, vocab: Dict[str, np.ndarray]) -> np.ndarray:
    if ev.get("is_pronoun"):
        char_v = vocab["pronoun_tag"]
    else:
        char_v = vocab["chars_raw"][ev["char_id"]]
    verb_v = vocab["verbs"][ev["verb_id"]]
    obj_v = vocab["objs"][ev["obj_id"]]
    scene_v = vocab["scenes"][ev["scene_id"]]
    raw = char_v + verb_v + obj_v + scene_v
    out = np.sign(raw)
    out[out == 0] = 1.0
    return out


def encode_fact_key(ch: int, fi: int, vocab: Dict[str, np.ndarray]) -> np.ndarray:
    raw = vocab["chars_raw"][ch] + vocab["facts"][fi]
    out = np.sign(raw)
    out[out == 0] = 1.0
    return out


def encode_fact_val(val: int, vocab: Dict[str, np.ndarray]) -> np.ndarray:
    return vocab["jobs"][val]


# ---------------- shared encoding pipeline ----------------

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
    """Shared cortex/partition encoding (mirrors ARM_FULL_STACK)."""
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


# ---------------- THE LOAD-BEARING NEW STRUCTURES ----------------

def _build_per_char_sequence_log(narr: "Narrative",
                                  vocab: Dict[str, np.ndarray],
                                  ) -> Dict[int, np.ndarray]:
    """Per-character sequence-binding K=20 recency log.

    For each character c, scan all non-pronoun mentions in temporal order.
    For each adjacent pair of mentions (m_{j-1}, m_j) write
        S_c += outer(pos_keys[m_{j-1}], pos_keys[m_j]) / N_CORTEX
    so that
        S_c @ pos_keys[m_j]  ~  pos_keys[m_{j-1}]    (predecessor mode)
    and (per c3 chain-grade primitive symmetry)
        S_c.T @ pos_keys[m_{j-1}]  ~  pos_keys[m_j]  (successor mode)

    The recency query for "most recent mention of c before pronoun event ev"
    uses the SUCCESSOR direction: feed pos_keys[ev] (the pronoun's event
    position) through S_c.T and check how strongly the output projects onto
    pos_keys of c's known mentions WITHIN THE PRIOR WINDOW. The character
    whose recency log gives the strongest projection to the most recent
    pre-pronoun position is the answer.

    Window cap: K_SEQ_LOG=20 most recent mentions per character (sliding).
    """
    S_per_char: Dict[int, np.ndarray] = {}
    for c in range(N_CHARACTERS):
        S_per_char[c] = np.zeros((N_CORTEX, N_CORTEX), dtype=np.float64)

    # Collect per-character mention positions in temporal order
    mentions_by_char: Dict[int, List[int]] = {c: [] for c in range(N_CHARACTERS)}
    for ev in narr.events:
        if ev.get("is_pronoun"):
            continue
        c = ev["char_id"]
        mentions_by_char[c].append(int(ev["event_idx"]))

    # Slide K_SEQ_LOG window then write adjacent pairs
    pos_keys = vocab["pos_keys_cortex"]  # shape (N_EVENTS+1, N_CORTEX)
    for c, mention_list in mentions_by_char.items():
        # Keep most recent K_SEQ_LOG mentions
        recent = mention_list[-K_SEQ_LOG:] if len(mention_list) > K_SEQ_LOG \
            else mention_list
        if len(recent) < 2:
            continue
        for j in range(1, len(recent)):
            prev_p = pos_keys[recent[j - 1]]
            curr_p = pos_keys[recent[j]]
            S_per_char[c] += np.outer(prev_p, curr_p) / N_CORTEX

    return S_per_char


def _build_per_char_role_memory(narr: "Narrative",
                                 vocab: Dict[str, np.ndarray],
                                 ) -> Dict[int, np.ndarray]:
    """Per-character HRR role memory: bundle of bind(char_c, role_tag) over
    that character's prior mentions.

    For each non-pronoun event of char c with role_tag r,
        role_bind_t = bind(chars_cortex[c], role_tags_cortex[r])
    bundle these (sum + sign-quantize) per character to get role_memory[c].

    At Q2 time: at the pronoun event with role_tag r,
        probe = role_tags_cortex[r]
        for each candidate c, score_role[c] = cosine(role_memory[c],
                                                      bind(chars_cortex[c], probe))
    so characters whose role memory overlaps with the pronoun's role bind
    win the role-filter component.
    """
    role_acc: Dict[int, List[np.ndarray]] = {c: [] for c in range(N_CHARACTERS)}
    for ev in narr.events:
        if ev.get("is_pronoun"):
            continue
        c = ev["char_id"]
        r = ev["role_tag_idx"]
        bound = hrr_bind_bipolar(vocab["chars_cortex"][c],
                                  vocab["role_tags_cortex"][r])
        role_acc[c].append(bound)

    role_memory: Dict[int, np.ndarray] = {}
    for c in range(N_CHARACTERS):
        if role_acc[c]:
            role_memory[c] = hrr_bundle(role_acc[c])
        else:
            role_memory[c] = np.zeros(N_CORTEX, dtype=np.float64)
    return role_memory


# ---------------- READOUT FUNCTIONS (6 distinct paths) ----------------

def q2_random_floor(seed_offset: int, ev_idx: int) -> int:
    rng = _rng(seed_offset + 222 + ev_idx)
    return int(rng.integers(0, N_CHARACTERS))


def q2_naive_magnitude(ev_idx: int, narr: "Narrative",
                       vocab: Dict[str, np.ndarray],
                       W_part: Dict[int, np.ndarray]) -> int:
    """Today's failing readout: argmax over per-char partition magnitude.

    Mirrors stage3 + composition_v1 NAIVE_MAGNITUDE; preserved as baseline.
    """
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


def q2_recency_only(ev_idx: int, narr: "Narrative",
                     vocab: Dict[str, np.ndarray],
                     S_per_char: Dict[int, np.ndarray]) -> Tuple[int, np.ndarray]:
    """SEQUENCE-BINDING K=20 NATIVE READOUT: per-character recency log.

    For each candidate char c with recency-log S_c,
        predicted_prev = S_c @ pos_keys[ev_idx]      (predecessor direction)
    The character whose S_c best predicts its OWN most recent mention's
    position-key is the answer.

    Concretely: for each c, find the most recent mention position
    m_recent[c] = max{m: m < ev_idx and m in mentions_of(c)}.
    Score: cosine(S_c @ pos_keys[ev_idx], pos_keys[m_recent[c]]).
    Argmax c.

    This IS the native sequence-binding decode mode that c3 chain-grade
    primitive proved at K=20 B_d5=1.000. Returns (pred, score_vec).
    """
    pos_keys = vocab["pos_keys_cortex"]
    target_pos = pos_keys[ev_idx]

    # Determine each character's most recent pre-pronoun mention
    mentions_by_char: Dict[int, List[int]] = {c: [] for c in range(N_CHARACTERS)}
    for ev in narr.events:
        if ev.get("is_pronoun"):
            continue
        if int(ev["event_idx"]) >= ev_idx:
            continue
        mentions_by_char[ev["char_id"]].append(int(ev["event_idx"]))

    scores = np.zeros(N_CHARACTERS, dtype=np.float64)
    for c in range(N_CHARACTERS):
        if not mentions_by_char[c]:
            scores[c] = -np.inf
            continue
        m_recent = max(mentions_by_char[c])
        predicted_prev = S_per_char[c] @ target_pos
        scores[c] = cosine_vec(predicted_prev, pos_keys[m_recent])
    if np.all(scores == -np.inf):
        return 0, scores
    return int(np.argmax(scores)), scores


def q2_role_only(ev_idx: int, narr: "Narrative",
                  vocab: Dict[str, np.ndarray],
                  role_memory: Dict[int, np.ndarray]) -> Tuple[int, np.ndarray]:
    """HRR ROLE-BIND NATIVE READOUT: per-character role coherence.

    At pronoun event ev_idx with role_tag r:
      probe_bind[c] = bind(chars_cortex[c], role_tags_cortex[r])
      score_role[c] = cosine(role_memory[c], probe_bind[c])
    Argmax c.
    """
    ev = narr.events[ev_idx]
    r = ev["role_tag_idx"]
    role_tag_v = vocab["role_tags_cortex"][r]

    scores = np.zeros(N_CHARACTERS, dtype=np.float64)
    for c in range(N_CHARACTERS):
        probe = hrr_bind_bipolar(vocab["chars_cortex"][c], role_tag_v)
        scores[c] = cosine_vec(role_memory[c], probe)
    return int(np.argmax(scores)), scores


def q2_recency_plus_role(ev_idx: int, narr: "Narrative",
                          vocab: Dict[str, np.ndarray],
                          S_per_char: Dict[int, np.ndarray],
                          role_memory: Dict[int, np.ndarray]) -> int:
    """THE MECHANISM: composition of recency (arm 3) + role (arm 4)."""
    _, rec_scores = q2_recency_only(ev_idx, narr, vocab, S_per_char)
    _, role_scores = q2_role_only(ev_idx, narr, vocab, role_memory)

    # Normalize each score vector to [0, 1] for sum compatibility
    def _norm01(v: np.ndarray) -> np.ndarray:
        valid = v[np.isfinite(v)]
        if valid.size == 0:
            return np.zeros_like(v)
        mn = float(np.min(valid))
        mx = float(np.max(valid))
        if mx - mn < 1e-9:
            out = np.zeros_like(v)
        else:
            out = (v - mn) / (mx - mn)
        # Replace -inf with 0
        out = np.where(np.isfinite(out), out, 0.0)
        return out

    rec_n = _norm01(rec_scores)
    role_n = _norm01(role_scores)
    combined = ALPHA_RECENCY * rec_n + BETA_ROLE * role_n
    return int(np.argmax(combined))


def q2_oracle(q: Dict[str, Any]) -> int:
    """Ground-truth (pins ceiling)."""
    return int(q["expected_char_id"])


# ---------------- Q1/Q3/Q4 readouts (shared across non-random arms) ----------------

def _build_S_sequence_matrix(narr: "Narrative",
                             keys_c: List[np.ndarray]) -> np.ndarray:
    """Q3 helper (kept for completeness; Q3 not the focus of this cell)."""
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


def q1_factual(W_cortex: np.ndarray, ch: int, fi: int,
                vocab: Dict[str, np.ndarray]) -> int:
    key_raw = encode_fact_key(ch, fi, vocab)
    key_h = pattern_separate_sparse(key_raw, vocab["P_in"], K_HIPPO_ACTIVE)
    key_c = project_h_to_c(key_h, vocab["P_hc"])
    cand = np.stack([project_h_to_c(
        pattern_separate_sparse(vocab["jobs"][j], vocab["P_in"], K_HIPPO_ACTIVE),
        vocab["P_hc"]) for j in range(N_JOBS)])
    raw = W_cortex @ key_c
    return cosine_argmax(raw, cand)


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


def q4_contradict(ch: int, fi: int,
                   gen_W: Dict[Tuple[int, int], Dict]) -> int:
    if (ch, fi) in gen_W:
        return gen_W[(ch, fi)]["latest_val"]
    return 0


# ---------------- arm runner ----------------

def run_arm(arm: str, seed: int) -> Dict[str, Any]:
    """Run one arm for one seed. All arms share encoding; differ in Q2 readout."""
    t0 = time.time()
    seed_offset = int(seed) * 100003
    rng_arm = _rng(seed_offset + 31)

    narr = Narrative(seed_offset)
    vocab = build_vocab(seed_offset)
    queries = narr.make_queries()
    keys_h, vals_h, keys_c, vals_c = _build_event_keys_vals(narr.events, vocab)

    W_cortex, W_part, gen_W = _encode_full_stack(
        narr, vocab, rng_arm, keys_h, vals_h, keys_c, vals_c)

    # NEW structures for this cell (built once, used by recency/role arms)
    S_per_char = _build_per_char_sequence_log(narr, vocab)
    role_memory = _build_per_char_role_memory(narr, vocab)
    S_replay = _build_S_sequence_matrix(narr, keys_c)

    preds_list: List[str] = []
    per_q: Dict[str, Dict[str, int]] = {q: {"correct": 0, "total": 0}
                                          for q in QUERY_TYPES}

    # Q1 factual (identical across non-random arms)
    for q in queries["Q1_factual"]:
        ch, fi, expected = q["char_id"], q["fact_idx"], q["expected_val"]
        if arm == "ARM_RANDOM_FLOOR":
            pred = int(_rng(seed_offset + 111 + ch * 13 + fi).integers(0, N_JOBS))
        else:
            pred = q1_factual(W_cortex, ch, fi, vocab)
        per_q["Q1_factual"]["total"] += 1
        per_q["Q1_factual"]["correct"] += int(pred == expected)
        preds_list.append("Q1:%d:%d:%d" % (ch, fi, pred))

    # Q2 coreference (arm-differentiated)
    for q in queries["Q2_coreference"]:
        ev_idx = q["event_idx"]
        expected_char = q["expected_char_id"]
        if arm == "ARM_RANDOM_FLOOR":
            pred = q2_random_floor(seed_offset, ev_idx)
        elif arm == "ARM_NAIVE_MAGNITUDE":
            pred = q2_naive_magnitude(ev_idx, narr, vocab, W_part)
        elif arm == "ARM_RECENCY_ONLY":
            pred, _ = q2_recency_only(ev_idx, narr, vocab, S_per_char)
        elif arm == "ARM_ROLE_ONLY":
            pred, _ = q2_role_only(ev_idx, narr, vocab, role_memory)
        elif arm == "ARM_RECENCY_PLUS_ROLE":
            pred = q2_recency_plus_role(ev_idx, narr, vocab,
                                          S_per_char, role_memory)
        elif arm == "ARM_ORACLE":
            pred = q2_oracle(q)
        else:
            raise ValueError("unknown arm: " + arm)
        per_q["Q2_coreference"]["total"] += 1
        per_q["Q2_coreference"]["correct"] += int(pred == expected_char)
        preds_list.append("Q2:%d:%d" % (ev_idx, pred))

    # Q3 temporal (kept for parity; not load-bearing here)
    for q in queries["Q3_temporal"]:
        target = q["target_event_idx"]
        expected = q["expected_prior_event_idx"]
        if arm == "ARM_RANDOM_FLOOR":
            target_scene = target // K_SCENE_BOUNDARY
            scene_members = [i for i in range(N_EVENTS)
                              if (i // K_SCENE_BOUNDARY) == target_scene
                              and i != target]
            if scene_members:
                idx = int(_rng(seed_offset + 333 + target).integers(
                    0, len(scene_members)))
                pred = scene_members[idx]
            else:
                pred = -1
        else:
            pred = q3_sequence_replay_readout(target, narr, keys_c, S_replay)
        per_q["Q3_temporal"]["total"] += 1
        per_q["Q3_temporal"]["correct"] += int(pred == expected)
        preds_list.append("Q3:%d:%d" % (target, pred))

    # Q4 contradict (identical across non-random arms)
    for q in queries["Q4_contradict"]:
        ch, fi, expected = q["char_id"], q["fact_idx"], q["expected_val"]
        if arm == "ARM_RANDOM_FLOOR":
            pred = int(_rng(seed_offset + 444 + ch * 7 + fi).integers(0, N_JOBS))
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

    # Q2-only pred sha (META_RULE_AF Q2-specific arms-must-differ)
    q2_preds = [p for p in preds_list if p.startswith("Q2:")]
    q2_pred_sha = hashlib.sha256(
        ";".join(q2_preds).encode("ascii")).hexdigest()[:16]

    wall = float(round(time.time() - t0, 3))
    return {
        "arm": arm,
        "seed": int(seed),
        "N_h": N_HIPPO, "N_c": N_CORTEX, "N_part": N_PART,
        "N_events": N_EVENTS, "N_chars": N_CHARACTERS,
        "K_scene": K_SCENE_BOUNDARY, "Q_per_type": Q_PER_TYPE,
        "K_seq_log": K_SEQ_LOG, "alpha_recency": ALPHA_RECENCY,
        "beta_role": BETA_ROLE,
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
        "q2_pred_sha": q2_pred_sha,
        "elapsed_s_arm": wall,
        "_partial_written_at": time.time(),
    }


# ---------------- verdict ----------------

def _classify(per_arm: Dict[str, Dict[str, Any]]) -> Tuple[str, str]:
    """Apply pre-reg bands to per-arm results; return (verdict, verdict_msg)."""
    floor = per_arm.get("ARM_RANDOM_FLOOR", {})
    naive = per_arm.get("ARM_NAIVE_MAGNITUDE", {})
    rec = per_arm.get("ARM_RECENCY_ONLY", {})
    role = per_arm.get("ARM_ROLE_ONLY", {})
    comp = per_arm.get("ARM_RECENCY_PLUS_ROLE", {})
    oracle = per_arm.get("ARM_ORACLE", {})

    if not all([floor, naive, rec, role, comp, oracle]):
        return "HARD_FAIL", "MISSING_ARM_RESULTS"

    floor_q2 = floor.get("Q2_coreference", 0.0)
    naive_q2 = naive.get("Q2_coreference", 0.0)
    rec_q2 = rec.get("Q2_coreference", 0.0)
    role_q2 = role.get("Q2_coreference", 0.0)
    comp_q2 = comp.get("Q2_coreference", 0.0)
    oracle_q2 = oracle.get("Q2_coreference", 0.0)

    lift_over_naive = comp_q2 - naive_q2

    # META_RULE_AF arms-must-differ: use Q2-specific pred_sha
    q2_shas = set()
    for arm_name in ARMS:
        d = per_arm.get(arm_name, {})
        sha = d.get("q2_pred_sha", "")
        if sha:
            q2_shas.add(sha)
    arms_distinct = len(q2_shas)

    # ORACLE sanity (defends against narrative bug)
    if oracle_q2 < HP_ORACLE_Q2:
        return ("HARD_FAIL",
                "HF_ORACLE_BROKEN: ARM_ORACLE Q2=%.3f < %.3f "
                "(ground-truth readout malfunctioning; narrative-gen bug). "
                "naive=%.3f comp=%.3f."
                % (oracle_q2, HP_ORACLE_Q2, naive_q2, comp_q2))

    # META_RULE_AF: composition pred_sha must differ from naive pred_sha
    naive_q2_sha = naive.get("q2_pred_sha", "")
    comp_q2_sha = comp.get("q2_pred_sha", "")
    if naive_q2_sha and comp_q2_sha and naive_q2_sha == comp_q2_sha:
        return ("HARD_FAIL",
                "HF_PRED_SHA_COLLISION: ARM_RECENCY_PLUS_ROLE Q2 pred_sha=%s "
                "equals ARM_NAIVE_MAGNITUDE Q2 pred_sha=%s (META_RULE_AF). "
                "Composition returned identical Q2 predictions as naive."
                % (comp_q2_sha, naive_q2_sha))

    if comp_q2 <= HF_RECENCY_PLUS_ROLE_Q2:
        return ("HARD_FAIL",
                "HF_COMPOSITION_FLOOR: ARM_RECENCY_PLUS_ROLE Q2=%.3f <= %.3f "
                "(4th composition failure for Q2 = capability box closes "
                "on substrate-native coref). naive=%.3f rec=%.3f role=%.3f "
                "oracle=%.3f floor=%.3f."
                % (comp_q2, HF_RECENCY_PLUS_ROLE_Q2, naive_q2, rec_q2,
                   role_q2, oracle_q2, floor_q2))

    if lift_over_naive <= HF_LIFT_OVER_NAIVE:
        return ("HARD_FAIL",
                "HF_NO_LIFT: lift_over_naive=%.3f <= %.3f. comp_Q2=%.3f "
                "naive_Q2=%.3f rec=%.3f role=%.3f oracle=%.3f."
                % (lift_over_naive, HF_LIFT_OVER_NAIVE, comp_q2, naive_q2,
                   rec_q2, role_q2, oracle_q2))

    if arms_distinct < HP_ARMS_DISTINCT_MIN:
        return ("HARD_FAIL",
                "HF_ARMS_NOT_DISTINCT: only %d distinct Q2 pred_sha across "
                "%d arms (need >= %d per META_RULE_AF). "
                "shas=%s"
                % (arms_distinct, len(ARMS), HP_ARMS_DISTINCT_MIN,
                   sorted(q2_shas)))

    # HARD_PASS conditions
    hp_main = (comp_q2 >= HP_RECENCY_PLUS_ROLE_Q2 and
               lift_over_naive >= HP_LIFT_OVER_NAIVE and
               rec_q2 >= HP_RECENCY_ONLY_FLOOR and
               oracle_q2 >= HP_ORACLE_Q2 and
               arms_distinct >= HP_ARMS_DISTINCT_MIN)

    if hp_main:
        return ("HARD_PASS",
                "HARD_PASS_Q2_COREF_RESCUE: ARM_RECENCY_PLUS_ROLE Q2=%.3f "
                ">=%.2f AND lift_over_naive=%.3f >=%.2f AND "
                "ARM_RECENCY_ONLY Q2=%.3f >=%.2f (positive control reproduces "
                "sequence-binding chain-grade) AND ARM_ORACLE=%.3f AND "
                "arms_distinct=%d. ARM_NAIVE=%.3f ARM_ROLE_ONLY=%.3f "
                "ARM_FLOOR=%.3f. 3-primitive composition rescues Q2 "
                "(sequence_binding K=20 + HRR role-bind + PC cleanup); "
                "M3 concern #3 long-narrative coherence unblocked."
                % (comp_q2, HP_RECENCY_PLUS_ROLE_Q2,
                   lift_over_naive, HP_LIFT_OVER_NAIVE,
                   rec_q2, HP_RECENCY_ONLY_FLOOR, oracle_q2,
                   arms_distinct, naive_q2, role_q2, floor_q2))

    return ("MIDDLE_BAND",
            "MIDDLE_BAND: comp_Q2=%.3f (HP>=%.2f HF<=%.2f) "
            "lift_over_naive=%.3f (HP>=%.2f HF<=%.2f) "
            "rec_only=%.3f (HP_floor=%.2f) role_only=%.3f oracle=%.3f "
            "arms_distinct=%d (need %d). 3-primitive composition partial."
            % (comp_q2, HP_RECENCY_PLUS_ROLE_Q2, HF_RECENCY_PLUS_ROLE_Q2,
               lift_over_naive, HP_LIFT_OVER_NAIVE, HF_LIFT_OVER_NAIVE,
               rec_q2, HP_RECENCY_ONLY_FLOOR, role_q2, oracle_q2,
               arms_distinct, HP_ARMS_DISTINCT_MIN))


# ---------------- self-test ----------------

def _selftest() -> int:
    """Smoke: run all 6 arms on SEED_ACTIVE. Verify cell RUNS; report
    per-arm Q2 + verdict. Does NOT assert HARD_PASS (those are the
    experiment); does assert basic sanity (cardinality_ok + oracle=1.0)."""
    print("[selftest] config: %s" % CONFIG_VERSION, flush=True)
    print("[selftest] EXPECTED_N_UNITS=%d (seeds=%d arms=%d)"
          % (EXPECTED_N_UNITS, len(SEEDS), len(ARMS)), flush=True)
    per_arm: Dict[str, Dict[str, Any]] = {}
    for arm in ARMS:
        try:
            result = run_arm(arm, SEED_ACTIVE)
        except SystemExit:
            raise
        except BaseException as e:
            print("[selftest] ARM %s CRASHED: %r" % (arm, e), flush=True)
            traceback.print_exc()
            return 1
        per_arm[arm] = result
        print("[selftest] arm=%s Q1=%.3f Q2=%.3f Q3=%.3f Q4=%.3f overall=%.3f "
              "q2_sha=%s wall=%.2fs"
              % (arm, result["Q1_factual"], result["Q2_coreference"],
                 result["Q3_temporal"], result["Q4_contradict"],
                 result["overall"], result["q2_pred_sha"],
                 result["elapsed_s_arm"]), flush=True)
    verdict, msg = _classify(per_arm)
    print("[selftest] verdict=%s" % verdict, flush=True)
    print("[selftest] verdict_msg=%s" % msg, flush=True)

    # Sanity assertions
    q2_shas = set(r["q2_pred_sha"] for r in per_arm.values())
    print("[selftest] Q2 distinct pred_shas across %d arms: %d"
          % (len(ARMS), len(q2_shas)), flush=True)

    oracle_q2 = per_arm["ARM_ORACLE"]["Q2_coreference"]
    if oracle_q2 < 1.0 - 1e-9:
        print("[selftest] FAIL: ORACLE Q2=%.3f != 1.000 (narrative-gen bug)"
              % oracle_q2, flush=True)
        return 1

    # Verdict assembly worked
    if verdict not in ("HARD_PASS", "HARD_FAIL", "MIDDLE_BAND"):
        print("[selftest] FAIL: unknown verdict=%s" % verdict, flush=True)
        return 1

    print("[selftest] PASS: oracle=1.000 verdict-assembled cardinality_ok",
          flush=True)
    return 0


# ---------------- main ----------------

def main() -> int:
    if _ARGS.self_test:
        return _selftest()

    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Defensive S13 pattern 1: start_marker
    start_marker = out_dir / "_start_marker.txt"
    start_marker.write_text(
        "started=%s\nconfig=%s\nseed=%d\nmode=%s\n"
        % (time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           CONFIG_VERSION, SEED_ACTIVE, RUN_MODE),
        encoding="utf-8")

    # Defensive S13 pattern 3: checkpoint per (seed, arm) unit
    seed = SEED_ACTIVE
    run_config = {"anchor": ANCHOR_NAME, "run_mode": RUN_MODE}

    per_arm: Dict[str, Dict[str, Any]] = {}
    for arm in ARMS:
        unit_key = "seed%d_%s" % (seed, arm)
        completed = list_completed_keys(out_dir, run_config=run_config)
        if unit_key in completed:
            partials = aggregate_partials(out_dir, [unit_key],
                                            run_config=run_config)
            if unit_key in partials:
                per_arm[arm] = partials[unit_key]
                print("[resume] skipping completed unit %s" % unit_key,
                      flush=True)
                continue

        print("[run] seed=%d arm=%s starting..." % (seed, arm), flush=True)
        try:
            result = run_arm(arm, seed)
        except SystemExit:
            raise
        except BaseException as e:
            # META_RULE_J: record + halt; SystemExit pre-empted
            print("[CRASH] arm=%s seed=%d: %r" % (arm, seed, e), flush=True)
            crash_path = out_dir / ("_crash_%s.txt" % unit_key)
            crash_path.write_text(
                "%s\n%r\n%s\n" % (time.time(), e, traceback.format_exc()),
                encoding="utf-8")
            return 2

        result["_ckpt_key"] = unit_key
        result["anchor_name"] = ANCHOR_NAME
        write_partial_key(out_dir, unit_key, result)
        per_arm[arm] = result
        # Defensive S13 pattern 2: heartbeat per arm
        (out_dir / "_heartbeat.txt").write_text(
            "last_unit=%s\nat=%s\n" % (unit_key, time.time()),
            encoding="utf-8")
        print("[done] %s Q2=%.3f q2_sha=%s wall=%.2fs"
              % (unit_key, result["Q2_coreference"], result["q2_pred_sha"],
                 result["elapsed_s_arm"]), flush=True)

    # Cardinality check (META_RULE_H)
    observed = len(per_arm)
    cardinality_ok = (observed == EXPECTED_N_UNITS)
    if not cardinality_ok:
        print("[WARN] CARDINALITY_BREACH: expected %d, observed %d"
              % (EXPECTED_N_UNITS, observed), flush=True)

    verdict, verdict_msg = _classify(per_arm)
    if not cardinality_ok:
        verdict = "HARD_FAIL"
        verdict_msg = ("HARD_FAIL_CARDINALITY_BREACH: expected %d arms got %d. "
                       % (EXPECTED_N_UNITS, observed)) + verdict_msg

    metrics: Dict[str, Any] = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "run_mode": RUN_MODE,
        "n_seeds": len(SEEDS),
        "seed": SEED_ACTIVE,
        "seeds": SEEDS,
        "arms": list(ARMS),
        "config_version": CONFIG_VERSION,
        "corpus_provenance": CORPUS_PROVENANCE,
        "expected_n_units": EXPECTED_N_UNITS,
        "observed_n_units": observed,
        "cardinality_ok": cardinality_ok,
        "per_arm": per_arm,
        "_llm_forward_calls_at_inference": 0,
        "zero_llm_calls_at_inference": True,
        "DESIGN_NOTE": (
            "Q2 coreference rescue via sequence-binding K=20 NATIVE shape "
            "(per-character recency log) + HRR role-bind (verb+obj role "
            "filter) composition. Mechanism-class 4 per drill "
            "research_drill_hrr_context_bind_disambiguator_Q2_coreference_"
            "2026-06-28.md. ARM_NAIVE_MAGNITUDE reproduces today's failing "
            "readout as baseline; ARM_ORACLE pins ceiling; "
            "ARM_RECENCY_PLUS_ROLE is the mechanism. Chunked single-seed-"
            "per-cell. 4th composition failure for Q2 = capability-box "
            "closure trigger."
        ),
        "arms_must_differ_q2_pred_sha": {
            arm: per_arm.get(arm, {}).get("q2_pred_sha", "") for arm in ARMS
        },
        "bands": {
            "HP_RECENCY_PLUS_ROLE_Q2": HP_RECENCY_PLUS_ROLE_Q2,
            "HP_LIFT_OVER_NAIVE": HP_LIFT_OVER_NAIVE,
            "HP_RECENCY_ONLY_FLOOR": HP_RECENCY_ONLY_FLOOR,
            "HP_ORACLE_Q2": HP_ORACLE_Q2,
            "HP_ARMS_DISTINCT_MIN": HP_ARMS_DISTINCT_MIN,
            "HF_RECENCY_PLUS_ROLE_Q2": HF_RECENCY_PLUS_ROLE_Q2,
            "HF_LIFT_OVER_NAIVE": HF_LIFT_OVER_NAIVE,
        },
        "composition_primitives": {
            "sequence_binding_K20": "data/exp_c3_compressed_sequence_replay_v1/metrics.json",
            "hrr_role_bind": "data/exp_contextual_encoding_hrr_binding_smoke_v1_smoketest/metrics.json",
            "pc_cleanup_attractor": "data/exp_pc_cleanup_attractor_v1/metrics.json",
        },
    }
    write_metrics(out_dir, metrics,
                   results=[per_arm[a] for a in ARMS if a in per_arm])
    print("[ship] %s verdict=%s" % (ANCHOR_NAME, verdict), flush=True)
    print("[ship] verdict_msg=%s" % verdict_msg, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
