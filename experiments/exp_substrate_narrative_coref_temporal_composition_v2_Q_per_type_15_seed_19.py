"""substrate_narrative_coref_temporal_composition_v2_Q_per_type_15 sibling seed=19.

2x-drill from v1 which BLOCKED at full-N preview because Q_PER_TYPE=3 produced
bit-identical predictions across ARM_PARTITION_ORACLE and ARM_NAIVE
(discriminator-must-survive-scale failure). Audit aa4be7382 hypothesis: Q-set
too sparse to separate readout paths; 5x widen Q_per_type to discriminate.

SINGLE-AXIS LEVER CHANGE FROM v1: Q_PER_TYPE 3 -> 15 + N_PRONOUN_EVENTS 8 -> 15.
All other axes IDENTICAL to v1 (encoding stack + 5 arms + readouts unchanged).

ARMS (5; arms-must-differ on Q2 + Q3 per META_RULE_AF):
  ARM_RANDOM_FLOOR        -- uniform random over candidates
  ARM_NAIVE_MAGNITUDE     -- v1 failing readout (Q2=norm-per-char; Q3=cosine(roll(-1)))
  ARM_PARTITION_ORACLE_ONLY -- Q2 fixed; Q3 unchanged
  ARM_SEQUENCE_REPLAY_ONLY  -- Q3 fixed; Q2 unchanged
  ARM_COMPOSITION         -- both fixes wired

CHUNKED: single seed per cell. SEED=7 pinned for this sibling.

PREREG: preregs/2026-06-30_substrate_narrative_coref_temporal_composition_v2_Q_per_type_15.md

CARDINALITY_OK: per-seed sibling produces 5 arms * 4 Q-types * 15 queries = 300 records.
EXPECTED_N_UNITS at arm-level = 5 (one per arm).

META_RULE_AC pre-reg | AE absolute paths | AF arms-must-differ SHA-256 |
AG edge-of-capacity smoke | AH atomic-write | AM composition-first |
AN substrate-empirical anchors | H cardinality_ok | J no-silent-except |
L strict-above-floor | DISCRIMINATOR-MUST-SURVIVE-SCALE preview via ARM_NAIVE.

ASCII-only. Author: exp_dev 2026-06-30 (Opus 4.7 1M, agent-spawn).
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

# Pinned seed for this sibling
SEED_PINNED = 19

ANCHOR_NAME = "substrate_narrative_coref_temporal_composition_v2_Q_per_type_15_seed_%d" % SEED_PINNED
CORPUS_PROVENANCE = (
    "synthetic_narrative_5char_grouped_into_scenes_fixed_K10_boundaries_"
    "with_per_character_facts_pronouns_and_fact_updates_v2_Q15_widened_"
    "REUSED_from_v1_with_Q_PER_TYPE_3_to_15_and_N_PRONOUN_EVENTS_8_to_15"
)

# ---------------- CLI ----------------
_P = argparse.ArgumentParser()
_P.add_argument("--self-test", action="store_true", dest="self_test")
_P.add_argument("--smoke", action="store_true")
_P.add_argument("--seed", type=int, default=None,
                help="override pinned seed (smoke/dev use only)")
_P.add_argument("--timeout", type=int, default=5400,
                help="per-cell timeout seconds (for runner enforcement)")
_ARGS, _ = _P.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = _HDLAB_EXP_NAME.lower().endswith("_smoke")
RUN_MODE = "smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE) \
    else os.environ.get("HDLAB_RUN_MODE", "full")
SMOKE = (RUN_MODE == "smoke")

# Seed selection: --seed override > HDLAB_SEED env > pinned default.
# Pinned seed is normally authoritative; override only used in dev/debug.
_env_seed = os.environ.get("HDLAB_SEED", "").strip()
if _ARGS.seed is not None:
    SEED_ACTIVE = int(_ARGS.seed)
elif _env_seed:
    SEED_ACTIVE = int(_env_seed)
else:
    SEED_ACTIVE = SEED_PINNED

SEEDS = [SEED_ACTIVE]

# ---------------- pre-reg bands (LOCKED at module init) ----------------
# v2 retains v1 bands; the only change is Q_PER_TYPE.
HP_PARTITION_Q2 = 0.60
HP_REPLAY_Q3 = 0.60
HP_COMPOSITION_MIN_PER_Q = 0.50
HP_LIFT_PARTITION_OVER_NAIVE = 0.30
HP_LIFT_REPLAY_OVER_NAIVE = 0.30

HF_PARTITION_Q2 = 0.30
HF_REPLAY_Q3 = 0.20
HF_COMPOSITION_ANY_Q = 0.30

MB_OVERALL_LOW = 0.30
MB_OVERALL_HIGH = 0.60

assert HP_PARTITION_Q2 > HF_PARTITION_Q2, "Q2 bands locked"
assert HP_REPLAY_Q3 > HF_REPLAY_Q3, "Q3 bands locked"
assert HP_COMPOSITION_MIN_PER_Q > HF_COMPOSITION_ANY_Q, "comp bands locked"

# ---------------- regime config ----------------
# DISCRIMINATOR-MUST-SURVIVE-SCALE Check A: smoke runs at FULL Q_PER_TYPE=15 +
# FULL N_HIPPO/N_CORTEX/N_EVENTS so the smoke directly tests whether the
# chain-grade readout discriminates at the widened-Q regime where v1 collapsed.
# Smoke differs from full ONLY by being single-seed; this IS the discriminator
# preview at full-scale the drill demanded.
N_HIPPO = 512
N_CORTEX = 1024
N_PART = 1024
N_EVENTS = 100
N_CHARACTERS = 5
K_SCENE_BOUNDARY = 10
N_FACTS_PER_CHAR = 3
N_UPDATE_PAIRS = 3
# v2 widens these two axes from v1 (v1: N_PRONOUN_EVENTS=8 Q_PER_TYPE=3)
N_PRONOUN_EVENTS = 15
Q_PER_TYPE = 15

K_HIPPO_ACTIVE = max(1, int(round(0.10 * N_HIPPO)))
ETA_CORTEX = 0.005
N_REPLAY_CYCLES = 3
N_RAW = 64
N_VERBS = 12
N_OBJECTS = 16
N_JOBS = 8

ARMS = ["ARM_RANDOM_FLOOR", "ARM_NAIVE_MAGNITUDE",
        "ARM_PARTITION_ORACLE_ONLY", "ARM_SEQUENCE_REPLAY_ONLY",
        "ARM_COMPOSITION"]
QUERY_TYPES = ["Q1_factual", "Q2_coreference", "Q3_temporal", "Q4_contradict"]
EXPECTED_N_UNITS = len(SEEDS) * len(ARMS)
# Per pre-reg CARDINALITY_OK at record level
EXPECTED_N_RECORDS = len(SEEDS) * len(ARMS) * len(QUERY_TYPES) * Q_PER_TYPE  # 300

CONFIG_VERSION = (
    "ANCHOR=%s,N_h=%d,N_c=%d,N_part=%d,N_events=%d,N_chars=%d,K_scene=%d,"
    "K_active=%d,eta=%.4f,N_replay=%d,Q_per_type=%d,N_pronoun=%d,seed=%d,"
    "arms=%d,mode=%s,HP_part=%.2f,HP_replay=%.2f,HP_comp_min=%.2f,"
    "HF_part=%.2f,HF_replay=%.2f,HF_comp=%.2f,EXPECTED_N=%d,EXPECTED_RECORDS=%d"
) % (
    ANCHOR_NAME, N_HIPPO, N_CORTEX, N_PART, N_EVENTS, N_CHARACTERS,
    K_SCENE_BOUNDARY, K_HIPPO_ACTIVE, ETA_CORTEX, N_REPLAY_CYCLES,
    Q_PER_TYPE, N_PRONOUN_EVENTS, SEED_ACTIVE, len(ARMS), RUN_MODE,
    HP_PARTITION_Q2, HP_REPLAY_Q3, HP_COMPOSITION_MIN_PER_Q,
    HF_PARTITION_Q2, HF_REPLAY_Q3, HF_COMPOSITION_ANY_Q,
    EXPECTED_N_UNITS, EXPECTED_N_RECORDS,
)

# ---------------- vector primitives (reused; identical to v1) ----------------

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


# ---------------- narrative generator (REUSED; identical to v1 except Q15) ----

class Narrative:
    """Reused from v1; Q_PER_TYPE=15 + N_PRONOUN_EVENTS=15 widen the query set."""

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
            # v2: take up to N_PRONOUN_EVENTS=15 candidates; if fewer available,
            # warn but proceed (Q_PER_TYPE will saturate at the floor).
            if len(cand_events) < N_PRONOUN_EVENTS:
                print("[narrative] WARN: only %d pronoun-candidate events "
                      "available; needed %d. Q2 will be capped at len(cand)."
                      % (len(cand_events), N_PRONOUN_EVENTS), flush=True)
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
            self.events.append(ev)

        self.scene_focus = scene_focus
        self.n_scenes = n_scenes
        self.update_pairs = update_pairs
        self.static_facts = static_facts
        self.pronoun_event_idxs = pronoun_event_idxs

    def make_queries(self) -> Dict[str, List[Dict]]:
        rng = _rng(self.seed_offset + 999)
        queries: Dict[str, List[Dict]] = {q: [] for q in QUERY_TYPES}

        # Q1 factual: up to Q_PER_TYPE static facts; cycle if shorter
        static_keys = list(self.static_facts.keys())
        rng.shuffle(static_keys)
        chosen_q1 = static_keys[:Q_PER_TYPE]
        # If fewer static facts exist than Q_PER_TYPE, cycle through them
        if len(chosen_q1) < Q_PER_TYPE and len(static_keys) > 0:
            while len(chosen_q1) < Q_PER_TYPE:
                chosen_q1.append(static_keys[len(chosen_q1) % len(static_keys)])
        for ch, fi in chosen_q1:
            val, ev = self.static_facts[(ch, fi)]
            queries["Q1_factual"].append({
                "char_id": ch, "fact_idx": fi, "expected_val": val,
                "source_event_idx": ev,
            })

        # Q2 coreference: pronoun events; up to Q_PER_TYPE
        pronoun_list = sorted(self.pronoun_event_idxs)
        rng.shuffle(pronoun_list)
        chosen_q2 = pronoun_list[:Q_PER_TYPE]
        if len(chosen_q2) < Q_PER_TYPE and len(pronoun_list) > 0:
            while len(chosen_q2) < Q_PER_TYPE:
                chosen_q2.append(pronoun_list[len(chosen_q2) % len(pronoun_list)])
        for ev_idx in chosen_q2:
            ev = self.events[ev_idx]
            queries["Q2_coreference"].append({
                "event_idx": ev_idx,
                "verb_id": ev["verb_id"],
                "obj_id": ev["obj_id"],
                "scene_id": ev["scene_id"],
                "expected_char_id": ev["char_id"],
            })

        # Q3 temporal: take up to Q_PER_TYPE non-scene-start events
        cand = [i for i in range(1, N_EVENTS)
                if (i % K_SCENE_BOUNDARY) > 0]
        rng.shuffle(cand)
        chosen_q3 = cand[:Q_PER_TYPE]
        for ev_idx in chosen_q3:
            queries["Q3_temporal"].append({
                "target_event_idx": ev_idx,
                "expected_prior_event_idx": ev_idx - 1,
            })

        # Q4 contradict: update_pairs; cycle if fewer than Q_PER_TYPE
        if len(self.update_pairs) > 0:
            chosen_q4 = list(self.update_pairs[:Q_PER_TYPE])
            while len(chosen_q4) < Q_PER_TYPE:
                chosen_q4.append(self.update_pairs[len(chosen_q4)
                                                   % len(self.update_pairs)])
            for (ch, fi, ve, vl, ee, le) in chosen_q4:
                queries["Q4_contradict"].append({
                    "char_id": ch, "fact_idx": fi,
                    "early_val": ve, "late_val": vl,
                    "early_event_idx": ee, "late_event_idx": le,
                    "expected_val": vl,
                })

        return queries


# ---------------- vocabularies (identical to v1) ----------------

def build_vocab(seed_offset: int) -> Dict[str, np.ndarray]:
    rng = _rng(seed_offset + 7777)
    n_scenes = (N_EVENTS + K_SCENE_BOUNDARY - 1) // K_SCENE_BOUNDARY
    vocab = {
        "chars": random_bipolar((N_CHARACTERS, N_RAW), rng),
        "verbs": random_bipolar((N_VERBS, N_RAW), rng),
        "objs":  random_bipolar((N_OBJECTS, N_RAW), rng),
        "jobs":  random_bipolar((N_JOBS, N_RAW), rng),
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


# ---------------- shared encoding pipeline (identical to v1) ----------------

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


# ---------------- READOUT PATHS (identical to v1) ----------------

def q2_naive_magnitude(ev_idx: int, narr: "Narrative",
                       vocab: Dict[str, np.ndarray],
                       W_cortex: np.ndarray,
                       W_part: Dict[int, np.ndarray]) -> int:
    ev = narr.events[ev_idx]
    cue_raw = encode_event_raw(ev, vocab)
    cue_h = pattern_separate_sparse(cue_raw, vocab["P_in"], K_HIPPO_ACTIVE)
    pos = ev["event_idx"] % K_SCENE_BOUNDARY
    cue_h = permute_role_pos(cue_h, pos)
    cue_pc = project_h_to_c(cue_h, vocab["P_pc"])
    scores = np.zeros(N_CHARACTERS, dtype=np.float64)
    for c in range(N_CHARACTERS):
        Wp = W_part[c]
        readout = Wp @ cue_pc
        scores[c] = float(np.linalg.norm(readout))
    return int(np.argmax(scores))


def q2_partition_oracle_readout(ev_idx: int, narr: "Narrative",
                                  vocab: Dict[str, np.ndarray],
                                  W_cortex: np.ndarray,
                                  W_part: Dict[int, np.ndarray]) -> int:
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
                  keys_c: List[np.ndarray],
                  S_unused: Optional[np.ndarray] = None) -> int:
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
    cand = np.stack([project_h_to_c(
        pattern_separate_sparse(vocab["jobs"][j], vocab["P_in"], K_HIPPO_ACTIVE),
        vocab["P_hc"]) for j in range(N_JOBS)])
    raw = W_cortex @ key_c
    return cosine_argmax(raw, cand)


def q4_contradict(ch: int, fi: int,
                   gen_W: Dict[Tuple[int, int], Dict]) -> int:
    if (ch, fi) in gen_W:
        return gen_W[(ch, fi)]["latest_val"]
    return 0


# ---------------- arm runner (identical structure to v1) ----------------

def run_arm(arm: str, seed: int) -> Dict[str, Any]:
    t0 = time.time()
    seed_offset = int(seed) * 100003
    rng_arm = _rng(seed_offset + 31)

    narr = Narrative(seed_offset)
    vocab = build_vocab(seed_offset)
    queries = narr.make_queries()
    keys_h, vals_h, keys_c, vals_c = _build_event_keys_vals(narr.events, vocab)

    W_cortex, W_part, gen_W = _encode_full_stack(narr, vocab, rng_arm,
                                                    keys_h, vals_h, keys_c, vals_c)
    S_replay = _build_S_sequence_matrix(narr, keys_c)

    preds_list: List[str] = []
    per_q: Dict[str, Dict[str, int]] = {q: {"correct": 0, "total": 0}
                                          for q in QUERY_TYPES}
    # Per-query records for cardinality (META_RULE_H at record-level)
    n_records = 0

    for q in queries["Q1_factual"]:
        ch, fi, expected = q["char_id"], q["fact_idx"], q["expected_val"]
        if arm == "ARM_RANDOM_FLOOR":
            pred = int(_rng(seed_offset + 111 + ch * 13 + fi).integers(0, N_JOBS))
        else:
            pred = q1_factual(W_cortex, ch, fi, vocab)
        per_q["Q1_factual"]["total"] += 1
        per_q["Q1_factual"]["correct"] += int(pred == expected)
        preds_list.append("Q1:%d:%d:%d" % (ch, fi, pred))
        n_records += 1

    for q in queries["Q2_coreference"]:
        ev_idx = q["event_idx"]
        expected_char = q["expected_char_id"]
        if arm == "ARM_RANDOM_FLOOR":
            pred = int(_rng(seed_offset + 222 + ev_idx).integers(0, N_CHARACTERS))
        elif arm == "ARM_NAIVE_MAGNITUDE":
            pred = q2_naive_magnitude(ev_idx, narr, vocab, W_cortex, W_part)
        elif arm == "ARM_PARTITION_ORACLE_ONLY":
            pred = q2_partition_oracle_readout(ev_idx, narr, vocab,
                                                  W_cortex, W_part)
        elif arm == "ARM_SEQUENCE_REPLAY_ONLY":
            pred = q2_naive_magnitude(ev_idx, narr, vocab, W_cortex, W_part)
        elif arm == "ARM_COMPOSITION":
            pred = q2_partition_oracle_readout(ev_idx, narr, vocab,
                                                  W_cortex, W_part)
        else:
            raise ValueError("unknown arm: " + arm)
        per_q["Q2_coreference"]["total"] += 1
        per_q["Q2_coreference"]["correct"] += int(pred == expected_char)
        preds_list.append("Q2:%d:%d" % (ev_idx, pred))
        n_records += 1

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
        elif arm == "ARM_NAIVE_MAGNITUDE":
            pred = q3_naive_roll(target, narr, keys_c)
        elif arm == "ARM_PARTITION_ORACLE_ONLY":
            pred = q3_naive_roll(target, narr, keys_c)
        elif arm == "ARM_SEQUENCE_REPLAY_ONLY":
            pred = q3_sequence_replay_readout(target, narr, keys_c, S_replay)
        elif arm == "ARM_COMPOSITION":
            pred = q3_sequence_replay_readout(target, narr, keys_c, S_replay)
        else:
            raise ValueError("unknown arm: " + arm)
        per_q["Q3_temporal"]["total"] += 1
        per_q["Q3_temporal"]["correct"] += int(pred == expected)
        preds_list.append("Q3:%d:%d" % (target, pred))
        n_records += 1

    for q in queries["Q4_contradict"]:
        ch, fi, expected = q["char_id"], q["fact_idx"], q["expected_val"]
        if arm == "ARM_RANDOM_FLOOR":
            pred = int(_rng(seed_offset + 444 + ch * 7 + fi).integers(0, N_JOBS))
        else:
            pred = q4_contradict(ch, fi, gen_W)
        per_q["Q4_contradict"]["total"] += 1
        per_q["Q4_contradict"]["correct"] += int(pred == expected)
        preds_list.append("Q4:%d:%d:%d" % (ch, fi, pred))
        n_records += 1

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
        "N_h": N_HIPPO, "N_c": N_CORTEX, "N_part": N_PART,
        "N_events": N_EVENTS, "N_chars": N_CHARACTERS,
        "K_scene": K_SCENE_BOUNDARY, "Q_per_type": Q_PER_TYPE,
        "N_pronoun_events": N_PRONOUN_EVENTS,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "acc_by_q": acc_by_q,
        "overall": round(overall, 4),
        "Q1_factual": round(acc_by_q["Q1_factual"], 4),
        "Q2_coreference": round(acc_by_q["Q2_coreference"], 4),
        "Q3_temporal": round(acc_by_q["Q3_temporal"], 4),
        "Q4_contradict": round(acc_by_q["Q4_contradict"], 4),
        "n_q_total": sum(per_q[q]["total"] for q in QUERY_TYPES),
        "n_records": n_records,
        "pred_sha": pred_sha,
        "elapsed_s_arm": wall,
        "_partial_written_at": time.time(),
    }


# ---------------- verdict (identical bands to v1) ----------------

def _classify(per_arm: Dict[str, Dict[str, Any]]) -> Tuple[str, str]:
    naive = per_arm.get("ARM_NAIVE_MAGNITUDE", {})
    floor = per_arm.get("ARM_RANDOM_FLOOR", {})
    part = per_arm.get("ARM_PARTITION_ORACLE_ONLY", {})
    rep = per_arm.get("ARM_SEQUENCE_REPLAY_ONLY", {})
    comp = per_arm.get("ARM_COMPOSITION", {})

    if not all([naive, floor, part, rep, comp]):
        return "HARD_FAIL", "MISSING_ARM_RESULTS"

    naive_q2 = naive.get("Q2_coreference", 0.0)
    naive_q3 = naive.get("Q3_temporal", 0.0)
    part_q2 = part.get("Q2_coreference", 0.0)
    rep_q3 = rep.get("Q3_temporal", 0.0)
    floor_q2 = floor.get("Q2_coreference", 0.0)
    floor_q3 = floor.get("Q3_temporal", 0.0)

    comp_per_q = [comp.get(q, 0.0) for q in QUERY_TYPES]
    comp_min = min(comp_per_q)

    lift_part = part_q2 - naive_q2
    lift_rep = rep_q3 - naive_q3

    # META_RULE_AF arms-must-differ check
    shas = set()
    for arm_name in ARMS:
        d = per_arm.get(arm_name, {})
        sha = d.get("pred_sha", "")
        if sha:
            shas.add(sha)
    arms_distinct = len(shas) >= 3

    # META_RULE_AY: HARD_FAIL on self-reported non-distinctness
    if not arms_distinct:
        return ("HARD_FAIL",
                "HF_ARMS_NOT_DISTINCT: only %d distinct pred_sha across %d arms "
                "(META_RULE_AF+AY tripped; arms collapsed at Q_PER_TYPE=15)."
                % (len(shas), len(ARMS)))

    if part_q2 <= HF_PARTITION_Q2:
        return ("HARD_FAIL",
                "HF_PARTITION_BROKEN: ARM_PARTITION_ORACLE_ONLY Q2=%.3f <= %.3f "
                "naive_Q2=%.3f floor_Q2=%.3f."
                % (part_q2, HF_PARTITION_Q2, naive_q2, floor_q2))
    if rep_q3 <= HF_REPLAY_Q3:
        return ("HARD_FAIL",
                "HF_REPLAY_BROKEN: ARM_SEQUENCE_REPLAY_ONLY Q3=%.3f <= %.3f "
                "naive_Q3=%.3f floor_Q3=%.3f."
                % (rep_q3, HF_REPLAY_Q3, naive_q3, floor_q3))
    if comp_min < HF_COMPOSITION_ANY_Q:
        return ("HARD_FAIL",
                "HF_COMPOSITION_SPOF: min_per_q=%.3f < %.3f."
                % (comp_min, HF_COMPOSITION_ANY_Q))

    hp_part = (part_q2 >= HP_PARTITION_Q2 and
               lift_part >= HP_LIFT_PARTITION_OVER_NAIVE)
    hp_rep = (rep_q3 >= HP_REPLAY_Q3 and
              lift_rep >= HP_LIFT_REPLAY_OVER_NAIVE)
    hp_comp = (comp_min >= HP_COMPOSITION_MIN_PER_Q)

    if hp_part and hp_rep and hp_comp:
        return ("HARD_PASS",
                "HARD_PASS_COMPOSITION_RESCUE_Q15: part_Q2=%.3f rep_Q3=%.3f "
                "comp_min=%.3f naive_Q2=%.3f naive_Q3=%.3f "
                "lift_part=%.3f lift_rep=%.3f arms_distinct=True n_shas=%d. "
                "Q-widening to 15 separates readout paths."
                % (part_q2, rep_q3, comp_min, naive_q2, naive_q3,
                   lift_part, lift_rep, len(shas)))

    return ("MIDDLE_BAND",
            "MIDDLE_BAND_Q15: part_Q2=%.3f (HP=%.2f HF=%.2f) rep_Q3=%.3f "
            "(HP=%.2f HF=%.2f) comp_min=%.3f (HP=%.2f) lift_part=%.3f "
            "(req %.2f) lift_rep=%.3f (req %.2f) arms_distinct=True n_shas=%d"
            % (part_q2, HP_PARTITION_Q2, HF_PARTITION_Q2,
               rep_q3, HP_REPLAY_Q3, HF_REPLAY_Q3,
               comp_min, HP_COMPOSITION_MIN_PER_Q,
               lift_part, HP_LIFT_PARTITION_OVER_NAIVE,
               lift_rep, HP_LIFT_REPLAY_OVER_NAIVE, len(shas)))


# ---------------- self-test ----------------

def _selftest() -> int:
    """Smoke at FULL Q_PER_TYPE=15 + FULL N regime (discriminator-survives-scale
    Check A). Run all 5 arms on the pinned seed; verify cell RUNS + arms-distinct
    + cardinality + verdict assembly. No band assertions on accuracies."""
    print("[selftest] config: %s" % CONFIG_VERSION, flush=True)
    print("[selftest] EXPECTED_N_UNITS=%d EXPECTED_N_RECORDS=%d (seeds=%d arms=%d Q=%d)"
          % (EXPECTED_N_UNITS, EXPECTED_N_RECORDS, len(SEEDS), len(ARMS),
             Q_PER_TYPE), flush=True)
    per_arm: Dict[str, Dict[str, Any]] = {}
    for arm in ARMS:
        try:
            result = run_arm(arm, SEED_ACTIVE)
        except SystemExit:
            raise
        except Exception as e:
            print("[selftest] ARM %s CRASHED: %r" % (arm, e), flush=True)
            traceback.print_exc()
            return 1
        per_arm[arm] = result
        print("[selftest] arm=%s Q1=%.3f Q2=%.3f Q3=%.3f Q4=%.3f overall=%.3f "
              "sha=%s n_rec=%d wall=%.2fs"
              % (arm, result["Q1_factual"], result["Q2_coreference"],
                 result["Q3_temporal"], result["Q4_contradict"],
                 result["overall"], result["pred_sha"], result["n_records"],
                 result["elapsed_s_arm"]), flush=True)
    verdict, msg = _classify(per_arm)
    print("[selftest] verdict=%s" % verdict, flush=True)
    print("[selftest] verdict_msg=%s" % msg, flush=True)

    shas = set(r["pred_sha"] for r in per_arm.values())
    print("[selftest] distinct pred_shas across %d arms: %d"
          % (len(ARMS), len(shas)), flush=True)
    if len(shas) < 4:
        print("[selftest] WARN: only %d distinct pred_shas (META_RULE_AF concern)"
              % len(shas), flush=True)

    # Q2 + Q3 per-arm value separation diagnostic (not a gate)
    q2_vals = sorted(set(round(r["Q2_coreference"], 3) for r in per_arm.values()))
    q3_vals = sorted(set(round(r["Q3_temporal"], 3) for r in per_arm.values()))
    print("[selftest] distinct Q2 values: %s" % q2_vals, flush=True)
    print("[selftest] distinct Q3 values: %s" % q3_vals, flush=True)

    # Cardinality check at record-level
    total_records = sum(r["n_records"] for r in per_arm.values())
    print("[selftest] total_records=%d expected=%d cardinality_ok=%s"
          % (total_records, EXPECTED_N_RECORDS,
             total_records == EXPECTED_N_RECORDS), flush=True)
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
        except Exception as e:
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
        (out_dir / "_heartbeat.txt").write_text(
            "last_unit=%s\nat=%s\n" % (unit_key, time.time()),
            encoding="utf-8")
        print("[done] %s Q1=%.3f Q2=%.3f Q3=%.3f Q4=%.3f wall=%.2fs"
              % (unit_key, result["Q1_factual"], result["Q2_coreference"],
                 result["Q3_temporal"], result["Q4_contradict"],
                 result["elapsed_s_arm"]), flush=True)

    observed = len(per_arm)
    cardinality_ok = (observed == EXPECTED_N_UNITS)
    # Record-level cardinality check
    total_records = sum(r.get("n_records", 0) for r in per_arm.values())
    records_ok = (total_records == EXPECTED_N_RECORDS)

    if not cardinality_ok:
        print("[WARN] CARDINALITY_BREACH_ARMS: expected %d, observed %d"
              % (EXPECTED_N_UNITS, observed), flush=True)
    if not records_ok:
        print("[WARN] CARDINALITY_BREACH_RECORDS: expected %d, observed %d"
              % (EXPECTED_N_RECORDS, total_records), flush=True)

    verdict, verdict_msg = _classify(per_arm)
    if not cardinality_ok or not records_ok:
        verdict = "HARD_FAIL"
        verdict_msg = ("HARD_FAIL_CARDINALITY_BREACH: arms expected=%d got=%d "
                       "records expected=%d got=%d. %s"
                       % (EXPECTED_N_UNITS, observed,
                          EXPECTED_N_RECORDS, total_records, verdict_msg))

    metrics: Dict[str, Any] = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict_msg,
        "run_mode": RUN_MODE,
        "n_seeds": len(SEEDS),
        "seed": SEED_ACTIVE,
        "seeds": SEEDS,
        "arms": list(ARMS),
        "config_version": CONFIG_VERSION,
        "corpus_provenance": CORPUS_PROVENANCE,
        "expected_n_units": EXPECTED_N_UNITS,
        "observed_n_units": observed,
        "expected_n_records": EXPECTED_N_RECORDS,
        "observed_n_records": total_records,
        "cardinality_ok": cardinality_ok and records_ok,
        "per_arm": per_arm,
        "_llm_forward_calls_at_inference": 0,
        "zero_llm_calls_at_inference": True,
        "DESIGN_NOTE": (
            "COMPOSITION test v2: widens Q_PER_TYPE from 3 to 15 + "
            "N_PRONOUN_EVENTS from 8 to 15 to expose readout-path separation "
            "that was masked at Q=3 in v1. Wires partition_oracle_v5 anchor-"
            "projection readout for Q2 + c3_compressed_sequence_replay K=20 "
            "decoder for Q3. ARM_NAIVE_MAGNITUDE reproduces v1 failing readout."
        ),
        "arms_must_differ_pred_sha": {
            arm: per_arm.get(arm, {}).get("pred_sha", "") for arm in ARMS
        },
        "bands": {
            "HP_PARTITION_Q2": HP_PARTITION_Q2,
            "HP_REPLAY_Q3": HP_REPLAY_Q3,
            "HP_COMPOSITION_MIN_PER_Q": HP_COMPOSITION_MIN_PER_Q,
            "HP_LIFT_PARTITION_OVER_NAIVE": HP_LIFT_PARTITION_OVER_NAIVE,
            "HP_LIFT_REPLAY_OVER_NAIVE": HP_LIFT_REPLAY_OVER_NAIVE,
            "HF_PARTITION_Q2": HF_PARTITION_Q2,
            "HF_REPLAY_Q3": HF_REPLAY_Q3,
            "HF_COMPOSITION_ANY_Q": HF_COMPOSITION_ANY_Q,
        },
    }
    write_metrics(out_dir, metrics,
                   results=[per_arm[a] for a in ARMS if a in per_arm])
    print("[ship] %s verdict=%s" % (ANCHOR_NAME, verdict), flush=True)
    print("[ship] verdict_msg=%s" % verdict_msg, flush=True)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception as e:
        traceback.print_exc()
        sys.exit(1)
