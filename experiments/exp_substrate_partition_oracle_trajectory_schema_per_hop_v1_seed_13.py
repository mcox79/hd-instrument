"""substrate_partition_oracle_trajectory_schema_per_hop_v1 (seed=13).

DRILL B — per-hop schema-Bayes redesign via sequence-binding trajectory map.
Replaces Drill A's hop-0-locked cluster_to_target_part[k] map with a per-
(cluster, hop_idx) -> partition trajectory store built via the substrate's
chain-grade sequence-binding S matrix in its native shape.

PURPOSE (2x-discipline gateway per
feedback_2x_drill_negatives_before_capability_closure_USER_2026-06-28):

  Drill A (pfc_wm_state_tracker_v1) HARD_FAILed all 3 adapters (MEASURED@
  2026-06-28). Root cause CONFIRMED: cluster_to_target_part[k] is built from
  chains_train[ci][0][2] // PART_SIZE -- hop-0 only. Every cluster maps to a
  hop-0 partition; per-hop discrimination capped at chance (1/N_PARTS=0.20).

  Drill B replaces the primitive output map. For each (cluster_k, hop_i) the
  S matrix stores the target partition vector for hop i. At inference per
  hop: schema-Bayes picks cluster k_pred, key = cluster_codes[k_pred] *
  hop_codes[i], partition = argmax over 5-way partition codebook of S @ key.

  If Drill B HARD_FAILs -> capability box CLOSES on brain-faithful 4-
  primitive multi-hop chain composition (2 structurally-different mechanism
  classes both null = 2x discipline satisfied).

ARMS (6):
    A BASELINE                  per-hop cleanup over full V_C; no hint
    B PATH2_PERCHAIN            3-primitive; schema fires once per chain
    C PATH3_4PRIM_HOP0_LOCKED   Drill A's SUB_A (positive control discriminator)
    D PATH4_TRAJECTORY_SCHEMA   THE NEW MECHANISM (sequence-binding S matrix)
    E ORACLE_PER_HOP            ground-truth partition per hop (upper bound)
    F RANDOM                    random partition (floor)

PRE-REG BANDS (LOCKED at module init; META_RULE_AL):
    HARD_PASS:
        arm_d top1 in [0.50, 0.95]
        AND arm_d - arm_c >= 0.30  (lift over hop-0-locked)
        AND arm_d - arm_a >= 0.20  (lift over baseline)
        AND arm_d per-hop part-acc at hops 5,10,15 > 0.50
        AND arm_e > arm_d  (oracle upper bound)
        AND arm_f < 0.05   (random floor)
        AND arms_distinct
        AND cardinality_ok
    HARD_FAIL (CAPABILITY CLOSURE TRIGGER per 2x-drill discipline):
        arm_d <= 0.30
        OR arm_d - arm_c < 0.10
        OR arm_d < arm_a
        OR per-hop part-acc at hop 10 <= 0.25
        OR arms_distinct = False
        OR arm_c > 0.30  (Gate D regime-match failure)
    MIDDLE_BAND:
        arm_d in [0.30, 0.50] AND (arm_d - arm_c) >= 0.10

GATE D (positive control reproduce AT TEST REGIME):
    arm_c (PATH3_4PRIM_HOP0_LOCKED) must reproduce Drill A SUB_A at SAME
    regime (N=8192 V_C=4000 d=15 psz=800 K=200). Expected <= 0.20; tolerance
    [0.00, 0.30]. If > 0.30: invocation/regime mismatch -> HARD_FAIL.

NUMBER TAGGING (META_RULE_AC):
    HYPOTHESIZED@HARD_PASS_BAND_D: [0.50, 0.95]
    MEASURED@DRILL_A_SUB_A_TOP1: 0.00
        d:/AI/hd-instrument/data/exp_substrate_partition_oracle_pfc_wm_state_tracker_v1_seed_13_smoke/metrics.json
    MEASURED@DRILL_A_PATH2_TOP1: 0.01 (same file)
    MEASURED@DRILL_A_ORACLE_TOP1: 0.84 (same file)
    MEASURED@DRILL_A_BASELINE_TOP1: 0.40 (same file)
    THEORETICAL@CAPACITY_K_300_N_8192: ratio 0.037 << capacity cliff 0.50
    THEORETICAL@SUPERPOSITION_REDUNDANCY: 300/5=60 repeats per partition
    THEORETICAL@DEPTH_SCALE_BASELINE: 0.948^15 = 0.449
    CITED@FRADY_SOMMER_2020 / PLATE_2003 / HERSCHE_2023

DISCIPLINE TAGS:
    META_RULE_AC AE AF AG AH AL AN AP H BIAS-N BIAS-Q BIAS-S
    DISCRIMINATOR-MUST-SURVIVE-SCALE PROT-018 PROT-021 Fix-28 NO-LOCAL
    CHUNKED single-seed-per-cell sibling (seed=13; siblings seed=7,13,19)

SOURCE CITATIONS (ABSOLUTE PATHS; META_RULE_AE):
    - Drill A template (cell):
      d:/AI/hd-instrument/experiments/exp_substrate_partition_oracle_pfc_wm_state_tracker_v1_seed_13.py
    - Drill A smoke metrics (HARD_FAIL):
      d:/AI/hd-instrument/data/exp_substrate_partition_oracle_pfc_wm_state_tracker_v1_seed_13_smoke/metrics.json
    - Drill note:
      d:/AI/hd-instrument/notes/research_drill_per_hop_schema_bayes_redesign_drill_B_2026-06-28.md
    - Pre-reg:
      d:/AI/hd-instrument/preregs/2026-06-28_substrate_partition_oracle_trajectory_schema_per_hop_v1.md

Author: exp_dev 2026-06-28 (Drill B; chunked single-seed sibling seed=13).
ASCII-only; __main__ guard; SystemExit re-raised before BaseException.
"""
from __future__ import annotations

import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import argparse
import atexit
import hashlib
import math
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    get_output_dir, resumable_seeds, write_partial_key, aggregate_partials,
    write_metrics,
)

ANCHOR_NAME = "substrate_partition_oracle_trajectory_schema_per_hop_v1_seed_13"
_LLM_CALL_COUNTER = [0]

# ----------------------------------------------------------------------------
# arg parsing
# ----------------------------------------------------------------------------
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true", dest="self_test")
_ARGS, _ = _ap.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = ("smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE)
            else os.environ.get("HDLAB_RUN_MODE", "full").lower())

# ----------------------------------------------------------------------------
# PRE-REG BANDS (LOCKED at module init; META_RULE_AL)
# ----------------------------------------------------------------------------
N_DIM = 8192
V_CONCEPTS = 4000
V_PRED = 10
DEPTH = 15
MAX_DEPTH = 15

N_PARTS = 5
assert V_CONCEPTS % N_PARTS == 0
PART_SIZE = V_CONCEPTS // N_PARTS  # 800

N_SCHEMAS = 20
WM_BANK_K = 200  # retained for arm_c reproduction of Drill A mechanism

def _cone_collapse_crosstalk(v_c_per_hop: int, n: int) -> float:
    return float(math.sqrt(max(v_c_per_hop - 1, 1) / max(n, 1)))

CROSSTALK_PART = _cone_collapse_crosstalk(PART_SIZE, N_DIM)        # 0.3123
CROSSTALK_BASELINE = _cone_collapse_crosstalk(V_CONCEPTS, N_DIM)   # 0.6987

# BASELINE rail
BASELINE_RAIL_LO = 0.05
BASELINE_RAIL_HI = 0.95
BASELINE_RAIL_TARGET = 0.449

# HARD_PASS bands for arm D (the mechanism)
HP_D_LO = 0.50
HP_D_HI = 0.95
HP_LIFT_OVER_C = 0.30          # arm_d - arm_c (PATH3) >= 0.30
HP_LIFT_OVER_A = 0.20          # arm_d - arm_a (BASELINE) >= 0.20
HP_PER_HOP_PARTACC = 0.50      # arm_d per-hop part-acc at hops 5/10/15 > 0.50
HP_RANDOM_CEIL = 0.05          # arm_f < 0.05
HP_CV_MAX = 0.15
HP_SATURATION_CEIL = 0.95

# HARD_FAIL gates
HF_D_ABS = 0.30
HF_LIFT_OVER_C = 0.10
HF_PER_HOP_AT_HOP10 = 0.25
MM_LIFT_MIN = 0.10

# Gate D positive control: arm_c expected band (regime match to Drill A)
GATED_C_EXPECTED_LO = 0.00
GATED_C_EXPECTED_HI = 0.30

# Chain configuration
N_CHAINS_TRAIN = 200
SEEDS = [13]  # CHUNKED single-seed cell; siblings seed_13, seed_19
if RUN_MODE == "smoke":
    N_CHAINS_TEST = 100
else:
    N_CHAINS_TEST = 200

# Cardinality (META_RULE_H): 6 arms x 1 seed
N_ARMS = 6
EXPECTED_N_UNITS = N_ARMS * len(SEEDS)

ENCODER_PROVENANCE = "SUBSTRATE_NATIVE_BIPOLAR"

CONFIG_VERSION = (
    "ANCHOR=%s,trajectorySchemaPerHopV1Seed13: N=%d V_C=%d V_P=%d depth=%d "
    "n_parts=%d psz=%d xtalk_part=%.4f xtalk_baseline=%.4f n_schemas=%d "
    "wm_bank_K=%d n_chains_train=%d n_chains_test=%d seeds=%s mode=%s "
    "encoder=%s "
    "RAIL=[%.3f,%.3f] target=%.3f HP_D_band=[%.2f,%.2f] "
    "HP_lift_C=%.2f HP_lift_A=%.2f HP_per_hop_partacc=%.2f "
    "HP_random_ceil=%.2f HP_cv_max=%.2f HP_sat_ceil=%.2f "
    "HF_D_abs=%.2f HF_lift_C=%.2f HF_per_hop_h10=%.2f MM_lift_min=%.2f "
    "gateD_C_expected=[%.2f,%.2f] "
    "expected_units=%d arms=%d"
) % (
    ANCHOR_NAME, N_DIM, V_CONCEPTS, V_PRED, DEPTH,
    N_PARTS, PART_SIZE, CROSSTALK_PART, CROSSTALK_BASELINE, N_SCHEMAS,
    WM_BANK_K, N_CHAINS_TRAIN, N_CHAINS_TEST, SEEDS, RUN_MODE,
    ENCODER_PROVENANCE,
    BASELINE_RAIL_LO, BASELINE_RAIL_HI, BASELINE_RAIL_TARGET,
    HP_D_LO, HP_D_HI, HP_LIFT_OVER_C, HP_LIFT_OVER_A,
    HP_PER_HOP_PARTACC, HP_RANDOM_CEIL, HP_CV_MAX, HP_SATURATION_CEIL,
    HF_D_ABS, HF_LIFT_OVER_C, HF_PER_HOP_AT_HOP10, MM_LIFT_MIN,
    GATED_C_EXPECTED_LO, GATED_C_EXPECTED_HI,
    EXPECTED_N_UNITS, N_ARMS,
)

# Locked invariants (META_RULE_AL)
assert BASELINE_RAIL_LO < BASELINE_RAIL_HI
assert HP_D_LO > HF_D_ABS
assert HP_D_LO < HP_D_HI <= HP_SATURATION_CEIL
assert HP_LIFT_OVER_C > HF_LIFT_OVER_C
assert 0.0 < HP_CV_MAX < 0.5
assert CROSSTALK_PART < CROSSTALK_BASELINE
assert DEPTH == 15
assert WM_BANK_K >= N_CHAINS_TEST  # one slot per test chain (for arm_c)


# ----------------------------------------------------------------------------
# Primitives (verbatim from Drill A template; chain-grade)
# ----------------------------------------------------------------------------

def bipolar(M: int, n: int, g: np.random.Generator) -> np.ndarray:
    X = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)


def ingest_hebbian(triples, E: np.ndarray, R: np.ndarray, sq: float,
                   n_dim: int, batch: int = 2000) -> np.ndarray:
    if not triples:
        return np.zeros((n_dim, n_dim), dtype=np.float32)
    tr = np.asarray(triples, dtype=np.int64)
    s_idx, p_idx, o_idx = tr[:, 0], tr[:, 1], tr[:, 2]
    W = np.zeros((n_dim, n_dim), dtype=np.float32)
    for b in range(0, len(tr), batch):
        ks = (E[s_idx[b:b + batch]] * R[p_idx[b:b + batch]] * sq).astype(np.float32)
        W += (E[o_idx[b:b + batch]].T @ ks) / n_dim
    return W


def make_deep_chains(n_chains: int, V: int, P: int, max_depth: int,
                     g: np.random.Generator,
                     disallow_s: set
                     ) -> Tuple[List[Tuple[int, int, int]],
                                List[List[Tuple[int, int, int]]]]:
    all_triples: List[Tuple[int, int, int]] = []
    chain_queries: List[List[Tuple[int, int, int]]] = []
    used_s = set(disallow_s)
    tries = 0
    while len(chain_queries) < n_chains and tries < n_chains * 200:
        tries += 1
        nodes: List[int] = []
        s = int(g.integers(0, V))
        if s in used_s:
            continue
        nodes.append(s)
        for _ in range(max_depth):
            cand = int(g.integers(0, V))
            while cand in nodes:
                cand = int(g.integers(0, V))
            nodes.append(cand)
        chain: List[Tuple[int, int, int]] = []
        for i in range(max_depth):
            p = int(g.integers(0, P))
            chain.append((nodes[i], p, nodes[i + 1]))
        all_triples.extend(chain)
        chain_queries.append(chain)
        used_s.add(s)
    if len(chain_queries) < n_chains:
        raise RuntimeError(
            "BLOCKING make_deep_chains: only %d/%d at max_depth=%d"
            % (len(chain_queries), n_chains, max_depth)
        )
    return all_triples, chain_queries


# ----------------------------------------------------------------------------
# Schema-Bayes primitive (vmPFC analog; from PATH 2)
# ----------------------------------------------------------------------------

def chain_schema_vector(chain: List[Tuple[int, int, int]],
                        R: np.ndarray) -> np.ndarray:
    """FR1: encode a chain's predicate sequence as a schema vector."""
    s = np.zeros(R.shape[1], dtype=np.float32)
    for (_, p, _) in chain:
        s += R[p]
    return s / (np.linalg.norm(s) + 1e-8)


def build_schema_prototypes(chains_train: List[List[Tuple[int, int, int]]],
                            R: np.ndarray,
                            n_schemas: int,
                            g: np.random.Generator) -> Tuple[np.ndarray,
                                                              List[int],
                                                              np.ndarray]:
    """vmPFC schema-Bayes prototypes; cluster_to_target_part is hop-0-locked
    (preserved for arm_c reproduction of Drill A's failed mechanism)."""
    n = len(chains_train)
    N = R.shape[1]

    def chain_hash(chain):
        return hash(tuple(p for (_, p, _) in chain))

    chain_to_schema = [(chain_hash(c) & 0x7fffffff) % n_schemas
                       for c in chains_train]

    prototypes = np.zeros((n_schemas, N), dtype=np.float32)
    counts = np.zeros(n_schemas, dtype=np.int64)
    for ci, c in enumerate(chains_train):
        s = chain_schema_vector(c, R)
        k = chain_to_schema[ci]
        prototypes[k] += s
        counts[k] += 1
    for k in range(n_schemas):
        if counts[k] > 0:
            prototypes[k] /= counts[k]
            nrm = float(np.linalg.norm(prototypes[k]))
            if nrm > 1e-8:
                prototypes[k] /= nrm
        else:
            v = g.standard_normal(N).astype(np.float32)
            prototypes[k] = v / (np.linalg.norm(v) + 1e-8)

    # Hop-0-locked map (Drill A's bug; preserved for arm_c reproduction)
    cluster_to_target_part = np.zeros(n_schemas, dtype=np.int64)
    for k in range(n_schemas):
        member_parts = [chains_train[ci][0][2] // PART_SIZE
                        for ci in range(n) if chain_to_schema[ci] == k]
        if member_parts:
            counts_per_part = np.bincount(member_parts, minlength=N_PARTS)
            cluster_to_target_part[k] = int(counts_per_part.argmax())
        else:
            cluster_to_target_part[k] = int(g.integers(0, N_PARTS))

    return prototypes, chain_to_schema, cluster_to_target_part


def build_schema_to_partition_W(prototypes: np.ndarray,
                                cluster_to_target_part: np.ndarray,
                                n_dim: int) -> np.ndarray:
    """Cortex partition activation matrix (Drill A's PATH2 readout)."""
    n_schemas, N = prototypes.shape
    W = np.zeros((N_PARTS, N), dtype=np.float32)
    for k in range(n_schemas):
        part = int(cluster_to_target_part[k])
        W[part] += prototypes[k]
    for p in range(N_PARTS):
        nrm = float(np.linalg.norm(W[p]))
        if nrm > 1e-8:
            W[p] /= nrm
    return W


# ----------------------------------------------------------------------------
# DRILL B NEW: trajectory S matrix (chain-grade sequence-binding readout)
# ----------------------------------------------------------------------------

def build_trajectory_S(
    chains_train: List[List[Tuple[int, int, int]]],
    chain_to_schema: List[int],
    cluster_codes: np.ndarray,
    hop_codes: np.ndarray,
    partition_codes: np.ndarray,
    n_dim: int,
) -> np.ndarray:
    """Build the per-(cluster, hop) -> partition trajectory matrix S.

    For each training chain c and each hop i:
        traj_key = cluster_codes[chain_to_schema[c]] * hop_codes[i]
        target_part = chains_train[c][i][2] // PART_SIZE
        S += outer(partition_codes[target_part], traj_key) / N

    K_seq superposition density = n_chains_train * DEPTH / n_schemas-equivalent
    For our config: 200 chains x 15 hops = 3000 individual writes, but they
    superpose onto N_SCHEMAS * DEPTH = 300 distinct key buckets.

    Returns S shape (N, N).
    """
    N = n_dim
    S = np.zeros((N, N), dtype=np.float32)
    for c_idx, chain in enumerate(chains_train):
        k = chain_to_schema[c_idx]
        cvec = cluster_codes[k]
        for i in range(len(chain)):
            target_part = chain[i][2] // PART_SIZE
            traj_key = (cvec * hop_codes[i]).astype(np.float32)
            S += np.outer(partition_codes[target_part], traj_key) / N
    return S


def read_trajectory_S(
    S: np.ndarray,
    k_pred: int,
    hop_i: int,
    cluster_codes: np.ndarray,
    hop_codes: np.ndarray,
    partition_codes: np.ndarray,
) -> Tuple[int, float]:
    """Readout: argmax over partition codebook of (S @ traj_key).

    Returns (target_part_idx, max_cosine).
    """
    traj_key = (cluster_codes[k_pred] * hop_codes[hop_i]).astype(np.float32)
    pvec = S @ traj_key
    # Cosine to each partition code
    scores = partition_codes @ pvec
    # Normalize for cosine reporting (only on the max)
    p_argmax = int(scores.argmax())
    pvec_nrm = float(np.linalg.norm(pvec))
    cos = float(scores[p_argmax]) / max(pvec_nrm, 1e-8)
    return p_argmax, cos


# ----------------------------------------------------------------------------
# dlPFC WM bank (Frady-Sommer 2020; kept for arm_c reproduction of Drill A)
# ----------------------------------------------------------------------------

def build_wm_bank_keys(K: int, n: int, g: np.random.Generator) -> np.ndarray:
    return bipolar(K, n, g)


def wm_write_slot(bank: np.ndarray, slot_idx: int,
                  slot_key: np.ndarray, state: np.ndarray,
                  n_dim: int) -> None:
    bound = (slot_key * state).astype(np.float32)
    nrm = float(np.linalg.norm(bound))
    if nrm > 1e-8:
        bound = bound / nrm
    bank[slot_idx] = bank[slot_idx] + bound


def wm_read_slot(bank: np.ndarray, slot_idx: int,
                 slot_key: np.ndarray) -> np.ndarray:
    raw = (bank[slot_idx] * slot_key).astype(np.float32)
    nrm = float(np.linalg.norm(raw))
    if nrm > 1e-8:
        return raw / nrm
    return raw


def hop_state_vector(s_idx: int, p_idx: int, hop_idx: int,
                     E: np.ndarray, R: np.ndarray,
                     hop_codes_wm: np.ndarray) -> np.ndarray:
    v = (E[s_idx] * R[p_idx] * hop_codes_wm[hop_idx]).astype(np.float32)
    nrm = float(np.linalg.norm(v))
    if nrm > 1e-8:
        v = v / nrm
    return v


# ----------------------------------------------------------------------------
# Arm C helper: Drill-A SUB_A prior-modulation pick (hop-0-locked)
# ----------------------------------------------------------------------------

def pick_sub_a_prior_modulation(per_hop_schema_q: np.ndarray,
                                wm_state_prev: np.ndarray,
                                prototypes: np.ndarray,
                                cluster_to_target_part: np.ndarray) -> int:
    """Drill A SUB_A: WM state biases schema posterior, then hop-0-locked map."""
    raw_post = prototypes @ per_hop_schema_q
    state_bias = prototypes @ wm_state_prev
    biased = raw_post * (1.0 + state_bias)
    part_scores = np.zeros(N_PARTS, dtype=np.float32)
    for k in range(prototypes.shape[0]):
        part_scores[int(cluster_to_target_part[k])] += float(biased[k])
    return int(part_scores.argmax())


# ----------------------------------------------------------------------------
# Arms (generic partition-restricted cleanup with pluggable partition picker)
# ----------------------------------------------------------------------------

def arm_baseline(E: np.ndarray, R: np.ndarray, sq: float,
                 W: np.ndarray, chains_test: List[List[Tuple[int, int, int]]],
                 depth: int) -> Dict[str, Any]:
    """ARM A: full-V_C cleanup (no partition restriction)."""
    n = len(chains_test)
    hits = 0
    per_step_hits = np.zeros(depth, dtype=np.int64)
    for chain in chains_test:
        s = chain[0][0]
        for i in range(depth):
            p = chain[i][1]
            key = (E[s] * R[p] * sq).astype(np.float32)
            scores = E @ (W @ key)
            s_pred = int(scores.argmax())
            if s_pred == chain[i][2]:
                per_step_hits[i] += 1
            s = s_pred
        if s == chain[depth - 1][2]:
            hits += 1
    return {
        "top1": round(hits / max(n, 1), 4),
        "per_step_acc": [round(float(x) / max(n, 1), 4)
                         for x in per_step_hits],
        "n_queries": n, "depth": depth,
        "mechanism": "baseline_per_hop_cleanup_full_V_C",
    }


def arm_part_restricted(E: np.ndarray, R: np.ndarray, sq: float,
                        W: np.ndarray,
                        chains_test: List[List[Tuple[int, int, int]]],
                        depth: int,
                        partition_picker,
                        mechanism_tag: str) -> Dict[str, Any]:
    """Generic partition-restricted cleanup arm (pluggable picker)."""
    n = len(chains_test)
    hits = 0
    per_step_hits = np.zeros(depth, dtype=np.int64)
    E_parts = [E[p * PART_SIZE:(p + 1) * PART_SIZE]
               for p in range(N_PARTS)]
    correct_part_hits = np.zeros(depth, dtype=np.int64)
    for chain_idx, chain in enumerate(chains_test):
        s = chain[0][0]
        for i in range(depth):
            p = chain[i][1]
            target_o = chain[i][2]
            target_part = target_o // PART_SIZE
            chosen_part = partition_picker(chain, chain_idx, i, s)
            if chosen_part == target_part:
                correct_part_hits[i] += 1
            key = (E[s] * R[p] * sq).astype(np.float32)
            state = W @ key
            scores = E_parts[chosen_part] @ state
            local_idx = int(scores.argmax())
            s_pred = chosen_part * PART_SIZE + local_idx
            if s_pred == target_o:
                per_step_hits[i] += 1
            s = s_pred
        if s == chain[depth - 1][2]:
            hits += 1
    return {
        "top1": round(hits / max(n, 1), 4),
        "per_step_acc": [round(float(x) / max(n, 1), 4)
                         for x in per_step_hits],
        "partition_correct_per_step": [round(float(x) / max(n, 1), 4)
                                       for x in correct_part_hits],
        "n_queries": n, "depth": depth,
        "n_partitions": N_PARTS, "part_size": PART_SIZE,
        "mechanism": mechanism_tag,
    }


def arm_c_path3_4prim(E: np.ndarray, R: np.ndarray, sq: float,
                       W: np.ndarray,
                       chains_test: List[List[Tuple[int, int, int]]],
                       depth: int,
                       prototypes: np.ndarray,
                       cluster_to_target_part: np.ndarray,
                       g_arm: np.random.Generator,
                       mechanism_tag: str) -> Dict[str, Any]:
    """ARM C: Drill A's PATH3 4-primitive with hop-0-locked map (SUB_A variant).

    Positive control discriminator. Reproduces Drill-A SUB_A at SAME regime.
    Expected top1 <= 0.20 (Gate D regime match).
    """
    n = len(chains_test)
    n_dim = E.shape[1]
    E_parts = [E[p * PART_SIZE:(p + 1) * PART_SIZE]
               for p in range(N_PARTS)]
    bank = np.zeros((WM_BANK_K, n_dim), dtype=np.float32)
    slot_keys = build_wm_bank_keys(WM_BANK_K, n_dim, g_arm)
    hop_codes_wm = bipolar(depth, n_dim, g_arm)

    hits = 0
    per_step_hits = np.zeros(depth, dtype=np.int64)
    correct_part_hits = np.zeros(depth, dtype=np.int64)

    for chain_idx, chain in enumerate(chains_test):
        c_slot = chain_idx % WM_BANK_K
        bank[c_slot] = 0.0
        s = chain[0][0]
        for i in range(depth):
            p = chain[i][1]
            target_o = chain[i][2]
            target_part = target_o // PART_SIZE

            if i == 0:
                wm_state_prev = np.zeros(n_dim, dtype=np.float32)
            else:
                wm_state_prev = wm_read_slot(bank, c_slot, slot_keys[c_slot])

            q_hop = np.zeros(n_dim, dtype=np.float32)
            for j in range(i + 1):
                q_hop = q_hop + R[chain[j][1]]
            nrm = float(np.linalg.norm(q_hop))
            if nrm > 1e-8:
                q_hop = q_hop / nrm

            chosen_part = pick_sub_a_prior_modulation(
                q_hop, wm_state_prev, prototypes, cluster_to_target_part)

            if chosen_part == target_part:
                correct_part_hits[i] += 1

            key = (E[s] * R[p] * sq).astype(np.float32)
            state = W @ key
            scores = E_parts[chosen_part] @ state
            local_idx = int(scores.argmax())
            s_pred = chosen_part * PART_SIZE + local_idx
            if s_pred == target_o:
                per_step_hits[i] += 1

            state_now = hop_state_vector(s_pred, p, i, E, R, hop_codes_wm)
            wm_write_slot(bank, c_slot, slot_keys[c_slot], state_now, n_dim)

            s = s_pred
        if s == chain[depth - 1][2]:
            hits += 1

    return {
        "top1": round(hits / max(n, 1), 4),
        "per_step_acc": [round(float(x) / max(n, 1), 4)
                         for x in per_step_hits],
        "partition_correct_per_step": [round(float(x) / max(n, 1), 4)
                                       for x in correct_part_hits],
        "n_queries": n, "depth": depth,
        "n_partitions": N_PARTS, "part_size": PART_SIZE,
        "wm_bank_K": WM_BANK_K,
        "mechanism": mechanism_tag,
    }


def arm_d_trajectory_schema(E: np.ndarray, R: np.ndarray, sq: float,
                            W: np.ndarray,
                            chains_test: List[List[Tuple[int, int, int]]],
                            depth: int,
                            prototypes: np.ndarray,
                            chain_to_schema_train: List[int],
                            S_traj: np.ndarray,
                            cluster_codes: np.ndarray,
                            hop_codes: np.ndarray,
                            partition_codes: np.ndarray,
                            mechanism_tag: str) -> Dict[str, Any]:
    """ARM D: trajectory-schema readout via sequence-binding S matrix.

    Per test chain q, per hop i:
        q_schema_per_hop = chain_schema_vector(q[0..i], R)
        k_pred  = argmax(prototypes @ q_schema_per_hop)
        traj_key = cluster_codes[k_pred] * hop_codes[i]
        partition_vec = S @ traj_key
        target_part = argmax(partition_codes @ partition_vec)
        cleanup within target_part partition

    Critical diagnostics recorded for HARD_FAIL analysis:
      - k_pred vs k_train mismatch rate (per chain, per hop)
      - trajectory_readout_cosine (per hop average across chains)
    """
    n = len(chains_test)
    n_dim = E.shape[1]
    E_parts = [E[p * PART_SIZE:(p + 1) * PART_SIZE]
               for p in range(N_PARTS)]

    hits = 0
    per_step_hits = np.zeros(depth, dtype=np.int64)
    correct_part_hits = np.zeros(depth, dtype=np.int64)
    # Diagnostics
    traj_cos_sum = np.zeros(depth, dtype=np.float64)
    traj_cos_count = np.zeros(depth, dtype=np.int64)
    # For test chains we don't know "true k" since they weren't in training,
    # but we can compute the schema-Bayes choice on the FULL-chain schema as
    # the "intended" cluster proxy (per-chain schema; what Drill A's PATH2
    # would have used). Mismatch = (k_pred_per_hop) != (k_train_proxy).
    mismatch_sum = np.zeros(depth, dtype=np.int64)
    mismatch_count = np.zeros(depth, dtype=np.int64)

    for chain_idx, chain in enumerate(chains_test):
        # Train-time proxy: schema-Bayes on full chain
        s_full = chain_schema_vector(chain, R)
        k_train_proxy = int((prototypes @ s_full).argmax())

        s = chain[0][0]
        for i in range(depth):
            p = chain[i][1]
            target_o = chain[i][2]
            target_part = target_o // PART_SIZE

            # Per-hop schema query (past hops only)
            q_hop = np.zeros(n_dim, dtype=np.float32)
            for j in range(i + 1):
                q_hop = q_hop + R[chain[j][1]]
            nrm = float(np.linalg.norm(q_hop))
            if nrm > 1e-8:
                q_hop = q_hop / nrm

            scores_k = prototypes @ q_hop
            k_pred = int(scores_k.argmax())

            # Trajectory readout
            chosen_part, traj_cos = read_trajectory_S(
                S_traj, k_pred, i, cluster_codes, hop_codes, partition_codes)

            # Diagnostics
            traj_cos_sum[i] += traj_cos
            traj_cos_count[i] += 1
            if k_pred != k_train_proxy:
                mismatch_sum[i] += 1
            mismatch_count[i] += 1

            if chosen_part == target_part:
                correct_part_hits[i] += 1

            # Cleanup within chosen partition
            key = (E[s] * R[p] * sq).astype(np.float32)
            state = W @ key
            scores = E_parts[chosen_part] @ state
            local_idx = int(scores.argmax())
            s_pred = chosen_part * PART_SIZE + local_idx
            if s_pred == target_o:
                per_step_hits[i] += 1
            s = s_pred
        if s == chain[depth - 1][2]:
            hits += 1

    return {
        "top1": round(hits / max(n, 1), 4),
        "per_step_acc": [round(float(x) / max(n, 1), 4)
                         for x in per_step_hits],
        "partition_correct_per_step": [round(float(x) / max(n, 1), 4)
                                       for x in correct_part_hits],
        "trajectory_readout_cosine_per_hop": [
            round(float(traj_cos_sum[i] / max(traj_cos_count[i], 1)), 4)
            for i in range(depth)
        ],
        "k_pred_per_hop_vs_k_train_mismatch_rate": [
            round(float(mismatch_sum[i] / max(mismatch_count[i], 1)), 4)
            for i in range(depth)
        ],
        "n_queries": n, "depth": depth,
        "n_partitions": N_PARTS, "part_size": PART_SIZE,
        "n_schemas": N_SCHEMAS,
        "K_seq_effective": N_SCHEMAS * depth,
        "mechanism": mechanism_tag,
    }


# ----------------------------------------------------------------------------
# Arms-must-differ SHA-256 (META_RULE_AF)
# ----------------------------------------------------------------------------

ARM_KEYS = [
    "arm_a_baseline",
    "arm_b_path2_perchain",
    "arm_c_path3_4prim_hop0_locked",
    "arm_d_path4_trajectory_schema",
    "arm_e_oracle_per_hop",
    "arm_f_random",
]


def _arms_must_differ_sha256(per_seed: List[Dict[str, Any]]) -> Dict[str, str]:
    hashes: Dict[str, str] = {}
    for k in ARM_KEYS:
        h = hashlib.sha256()
        for p in per_seed:
            if k in p and isinstance(p[k].get("per_step_acc"), list):
                h.update(repr(p[k]["per_step_acc"]).encode("utf-8"))
                h.update(b"|")
                h.update(repr(p[k].get("top1", "")).encode("utf-8"))
                h.update(b"||")
        hashes[k] = h.hexdigest()[:16]
    return hashes


# ----------------------------------------------------------------------------
# Self-test (formula + mechanism sanity)
# ----------------------------------------------------------------------------

def _selftest() -> None:
    g = np.random.default_rng(0)
    n_tiny = 256
    V_tiny = 40
    P_tiny = 4
    n_parts_tiny = 4
    psz_tiny = V_tiny // n_parts_tiny  # 10
    n_schemas_tiny = 4
    wm_K_tiny = 8
    sq = math.sqrt(n_tiny)
    E = bipolar(V_tiny, n_tiny, g)
    R = bipolar(P_tiny, n_tiny, g)

    # T1: bipolar shapes
    assert E.shape == (V_tiny, n_tiny) and R.shape == (P_tiny, n_tiny)
    assert abs(float(np.linalg.norm(E[0])) - 1.0) < 1e-4

    # T2: chain construction at DEPTH=15
    triples, chains = make_deep_chains(8, V_tiny, P_tiny,
                                       max_depth=DEPTH, g=g,
                                       disallow_s=set())
    assert len(chains) == 8 and len(triples) == 8 * DEPTH

    # T3: ingest
    W = ingest_hebbian(triples, E, R, sq, n_tiny)
    assert W.shape == (n_tiny, n_tiny)
    assert np.isfinite(W).all()

    # T4: schema vector + prototypes (tiny config)
    sv = chain_schema_vector(chains[0], R)
    assert sv.shape == (n_tiny,)
    assert abs(float(np.linalg.norm(sv)) - 1.0) < 1e-4

    # Patch module-level PART_SIZE / N_PARTS / WM_BANK_K for tiny run
    global PART_SIZE, N_PARTS, WM_BANK_K
    _saved_psz = PART_SIZE
    _saved_np = N_PARTS
    _saved_K = WM_BANK_K
    try:
        PART_SIZE = psz_tiny
        N_PARTS = n_parts_tiny
        WM_BANK_K = wm_K_tiny

        protos, chain2sch, cl2part = build_schema_prototypes(
            chains, R, n_schemas_tiny, g)
        assert protos.shape == (n_schemas_tiny, n_tiny)
        assert cl2part.shape == (n_schemas_tiny,)
        assert all(0 <= pp < n_parts_tiny for pp in cl2part)

        # T5: trajectory S matrix construction
        cluster_codes = bipolar(n_schemas_tiny, n_tiny, g)
        hop_codes = bipolar(DEPTH, n_tiny, g)
        partition_codes = bipolar(n_parts_tiny, n_tiny, g)
        S = build_trajectory_S(chains, chain2sch, cluster_codes, hop_codes,
                               partition_codes, n_tiny)
        assert S.shape == (n_tiny, n_tiny)
        assert np.isfinite(S).all()

        # T6: trajectory readout returns valid partition
        for hop_i in [0, 5, 10, 14]:
            p_arg, cos = read_trajectory_S(S, 0, hop_i, cluster_codes,
                                            hop_codes, partition_codes)
            assert 0 <= p_arg < n_parts_tiny
            assert -1.0 < cos < 1.5  # cosine-like score; can exceed 1 for unnormalized S @ key

        # T7: arm_d_trajectory_schema produces valid output at tiny config
        W_arm = ingest_hebbian([t for c in chains for t in c], E, R, sq, n_tiny)
        r_d = arm_d_trajectory_schema(E, R, sq, W_arm, chains, DEPTH,
                                       protos, chain2sch, S,
                                       cluster_codes, hop_codes, partition_codes,
                                       "trajectory_schema_test")
        assert 0.0 <= r_d["top1"] <= 1.0
        assert len(r_d["per_step_acc"]) == DEPTH
        assert len(r_d["partition_correct_per_step"]) == DEPTH
        assert len(r_d["trajectory_readout_cosine_per_hop"]) == DEPTH
        assert len(r_d["k_pred_per_hop_vs_k_train_mismatch_rate"]) == DEPTH

        # T8: arm_baseline
        r_a = arm_baseline(E, R, sq, W_arm, chains, depth=DEPTH)
        assert 0.0 <= r_a["top1"] <= 1.0

        # T9: arm_c_path3_4prim returns valid output
        g_c = np.random.default_rng(101)
        r_c = arm_c_path3_4prim(E, R, sq, W_arm, chains, DEPTH, protos, cl2part,
                                 g_c, "arm_c_test")
        assert 0.0 <= r_c["top1"] <= 1.0
        assert len(r_c["per_step_acc"]) == DEPTH

        # T10: arm_part_restricted with pickers (oracle / random / path2)
        def pick_oracle(chain, chain_idx, i, s_now):
            return chain[i][2] // PART_SIZE

        g_rand = np.random.default_rng(0)

        def pick_random(chain, chain_idx, i, s_now):
            return int(g_rand.integers(0, n_parts_tiny))

        W_s2p = build_schema_to_partition_W(protos, cl2part, n_tiny)
        _schema_cache: Dict[int, np.ndarray] = {}

        def pick_path2(chain, chain_idx, i, s_now):
            cid = id(chain)
            if cid not in _schema_cache:
                _schema_cache[cid] = chain_schema_vector(chain, R)
            qs = _schema_cache[cid]
            scores = W_s2p @ qs
            return int(scores.argmax())

        r_b = arm_part_restricted(E, R, sq, W_arm, chains, DEPTH, pick_path2,
                                  "path2_test")
        r_e_arm = arm_part_restricted(E, R, sq, W_arm, chains, DEPTH, pick_oracle,
                                       "oracle_test")
        r_f = arm_part_restricted(E, R, sq, W_arm, chains, DEPTH, pick_random,
                                  "random_test")
        for r in (r_b, r_e_arm, r_f):
            assert 0.0 <= r["top1"] <= 1.0

        # T11: oracle >= random at tiny (sanity; weak)
        assert r_e_arm["top1"] >= r_f["top1"] - 0.20

        # T12: arms must differ -- per_step_acc patterns distinct across arms
        # (at least D vs A and D vs B)
        assert r_d["per_step_acc"] != r_a["per_step_acc"]
        assert r_d["per_step_acc"] != r_b["per_step_acc"]

        # T13: trajectory readout in capacity regime (300/8192=0.037 at full)
        # at tiny, ratio is n_schemas_tiny * DEPTH / n_tiny = 4*15/256 = 0.23
        # Still below cliff but tighter; expect noisy readout (just check ran).
        assert r_d["top1"] >= 0.0  # already asserted above; explicit re-check

    finally:
        PART_SIZE = _saved_psz
        N_PARTS = _saved_np
        WM_BANK_K = _saved_K

    # T14: cone-collapse formula sanity
    assert abs(CROSSTALK_PART - 0.3123) < 0.001, \
        "psz=800/N=8192 xtalk drift: %.4f" % CROSSTALK_PART
    assert CROSSTALK_BASELINE > 0.6

    # T15: bands LOCKED
    assert N_DIM == 8192
    assert V_CONCEPTS == 4000
    assert DEPTH == 15
    assert PART_SIZE == 800
    assert N_PARTS == 5
    assert N_SCHEMAS == 20
    assert WM_BANK_K == 200
    assert HP_D_LO == 0.50
    assert HP_D_HI == 0.95
    assert HF_D_ABS == 0.30
    assert HP_LIFT_OVER_C == 0.30
    assert HP_LIFT_OVER_A == 0.20
    assert HP_PER_HOP_PARTACC == 0.50
    assert HP_RANDOM_CEIL == 0.05

    # T16: zero LLM calls
    assert _LLM_CALL_COUNTER[0] == 0

    # T17: cardinality declared
    assert EXPECTED_N_UNITS == N_ARMS * len(SEEDS) == 6

    # T18: anchor binding (seed=7 sibling)
    assert "_seed_13" in ANCHOR_NAME
    assert ANCHOR_NAME.endswith("_seed_13")
    assert "trajectory_schema_per_hop" in ANCHOR_NAME

    # T19: capacity feasibility (THEORETICAL@)
    capacity_ratio = (N_SCHEMAS * DEPTH) / float(N_DIM)
    assert capacity_ratio < 0.10, \
        "capacity ratio drift: %.4f >= 0.10" % capacity_ratio

    print(("[selftest] PASS N=%d V_C=%d depth=%d n_parts=%d psz=%d n_schemas=%d "
           "K_seq=%d capacity_ratio=%.4f tiny_arms: a=%.3f b=%.3f c=%.3f "
           "d=%.3f e=%.3f f=%.3f xtalk_part=%.4f xtalk_baseline=%.4f "
           "HP_D=[%.2f,%.2f] expected_proj_baseline=%.3f") % (
              N_DIM, V_CONCEPTS, DEPTH, N_PARTS, PART_SIZE, N_SCHEMAS,
              N_SCHEMAS * DEPTH, capacity_ratio,
              r_a["top1"], r_b["top1"], r_c["top1"],
              r_d["top1"], r_e_arm["top1"], r_f["top1"],
              CROSSTALK_PART, CROSSTALK_BASELINE, HP_D_LO, HP_D_HI,
              0.948 ** DEPTH),
          flush=True)


_selftest()
if _ARGS.self_test:
    print("[self-test] PASS; exiting", flush=True)
    sys.exit(0)


# ----------------------------------------------------------------------------
# run_seed
# ----------------------------------------------------------------------------

def run_seed(seed: int) -> Dict[str, Any]:
    t = time.time()
    print("[start_marker] seed=%d anchor=%s mode=%s" % (
        seed, ANCHOR_NAME, RUN_MODE), flush=True)
    g = np.random.default_rng(seed)
    sq = math.sqrt(N_DIM)

    print("  [seed=%d] building E (V_C=%d, N=%d) + R" % (
        seed, V_CONCEPTS, N_DIM), flush=True)
    E = bipolar(V_CONCEPTS, N_DIM, g)
    R = bipolar(V_PRED, N_DIM, g)

    print("  [seed=%d] generating train chains (n=%d, max_depth=%d)" % (
        seed, N_CHAINS_TRAIN, MAX_DEPTH), flush=True)
    triples_train, chains_train = make_deep_chains(
        N_CHAINS_TRAIN, V_CONCEPTS, V_PRED, max_depth=MAX_DEPTH,
        g=g, disallow_s=set())
    used_s = set(c[0][0] for c in chains_train)

    print("  [seed=%d] generating test chains (n=%d, max_depth=%d)" % (
        seed, N_CHAINS_TEST, MAX_DEPTH), flush=True)
    triples_test, chains_test = make_deep_chains(
        N_CHAINS_TEST, V_CONCEPTS, V_PRED, max_depth=MAX_DEPTH,
        g=g, disallow_s=used_s)

    all_triples = triples_train + triples_test
    print("  [seed=%d] ingesting W (%d bindings, N=%d -> %.1f MB)" % (
        seed, len(all_triples), N_DIM, (N_DIM * N_DIM * 4) / 1e6), flush=True)
    t_ingest = time.time()
    W = ingest_hebbian(all_triples, E, R, sq, N_DIM)
    print("  [seed=%d] W ingested t=%.1fs shape=%s" % (
        seed, time.time() - t_ingest, W.shape), flush=True)

    print("  [seed=%d] building schema prototypes (n_schemas=%d)" % (
        seed, N_SCHEMAS), flush=True)
    prototypes, chain_to_schema, cluster_to_target_part = build_schema_prototypes(
        chains_train, R, N_SCHEMAS, g)
    W_schema_to_part = build_schema_to_partition_W(
        prototypes, cluster_to_target_part, N_DIM)

    print("  [seed=%d] building trajectory codebooks (cluster/hop/partition)" % seed,
          flush=True)
    g_codes = np.random.default_rng(seed * 7919 + 31)
    cluster_codes = bipolar(N_SCHEMAS, N_DIM, g_codes)
    hop_codes = bipolar(DEPTH, N_DIM, g_codes)
    partition_codes = bipolar(N_PARTS, N_DIM, g_codes)

    print("  [seed=%d] building trajectory S matrix (K_seq=%d at N=%d)" % (
        seed, N_SCHEMAS * DEPTH, N_DIM), flush=True)
    t_S = time.time()
    S_traj = build_trajectory_S(
        chains_train, chain_to_schema, cluster_codes, hop_codes,
        partition_codes, N_DIM)
    print("  [seed=%d] S built t=%.1fs shape=%s capacity_ratio=%.4f" % (
        seed, time.time() - t_S, S_traj.shape,
        (N_SCHEMAS * DEPTH) / float(N_DIM)), flush=True)

    out: Dict[str, Any] = {
        "seed": seed, "run_mode": RUN_MODE, "N": N_DIM, "V_C": V_CONCEPTS,
        "V_P": V_PRED, "depth": DEPTH,
        "n_chains_train": N_CHAINS_TRAIN, "n_chains_test": N_CHAINS_TEST,
        "n_partitions": N_PARTS, "part_size": PART_SIZE,
        "n_schemas": N_SCHEMAS, "wm_bank_K": WM_BANK_K,
        "K_seq_effective": N_SCHEMAS * DEPTH,
        "capacity_ratio": round((N_SCHEMAS * DEPTH) / float(N_DIM), 4),
        "crosstalk_baseline": CROSSTALK_BASELINE,
        "crosstalk_part": CROSSTALK_PART,
        "encoder_provenance": ENCODER_PROVENANCE,
        "config_version": CONFIG_VERSION,
        "anchor_name": ANCHOR_NAME,
        "_llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
    }

    # Periodic heartbeat (defensive pattern per exp_dev.md)
    def _hb():
        try:
            hb = REPO / "data" / "heartbeats" / "exp_dev.timestamp"
            hb.write_text(time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                          encoding="utf-8")
        except Exception:
            pass

    # ===== ARM A: BASELINE =====
    t_arm = time.time()
    r_a = arm_baseline(E, R, sq, W, chains_test, depth=DEPTH)
    r_a["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    out["arm_a_baseline"] = r_a
    rail_ok = (BASELINE_RAIL_LO <= r_a["top1"] <= BASELINE_RAIL_HI)
    out["baseline_rail_ok"] = rail_ok
    print("  [seed=%d] ARM_A BASELINE top1=%.4f rail_ok=%s t=%.1fs" % (
        seed, r_a["top1"], rail_ok, r_a["elapsed_s_arm"]), flush=True)
    _hb()

    # ===== ARM B: PATH2_PERCHAIN (3-primitive; schema fires once per chain) =====
    _schema_cache_b: Dict[int, np.ndarray] = {}

    def pick_path2(chain, chain_idx, i, s_now):
        cid = id(chain)
        if cid not in _schema_cache_b:
            _schema_cache_b[cid] = chain_schema_vector(chain, R)
        qs = _schema_cache_b[cid]
        scores = W_schema_to_part @ qs
        return int(scores.argmax())

    t_arm = time.time()
    r_b = arm_part_restricted(
        E, R, sq, W, chains_test, DEPTH, pick_path2,
        "path2_per_chain_schema_fires_once_no_wm")
    r_b["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    out["arm_b_path2_perchain"] = r_b
    print("  [seed=%d] ARM_B PATH2_PERCHAIN top1=%.4f t=%.1fs" % (
        seed, r_b["top1"], r_b["elapsed_s_arm"]), flush=True)
    _hb()

    # ===== ARM C: PATH3 4-PRIMITIVE HOP-0-LOCKED (Drill A positive control) =====
    g_c = np.random.default_rng(seed * 7919 + 1)
    t_arm = time.time()
    r_c = arm_c_path3_4prim(
        E, R, sq, W, chains_test, DEPTH, prototypes, cluster_to_target_part,
        g_c,
        "path3_4primitive_hop0_locked_drill_a_positive_control")
    r_c["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    out["arm_c_path3_4prim_hop0_locked"] = r_c
    print(("  [seed=%d] ARM_C PATH3_4PRIM_HOP0_LOCKED top1=%.4f "
           "(Gate_D_expected=[%.2f,%.2f]) t=%.1fs") % (
        seed, r_c["top1"], GATED_C_EXPECTED_LO, GATED_C_EXPECTED_HI,
        r_c["elapsed_s_arm"]), flush=True)
    _hb()

    # ===== ARM D: PATH4 TRAJECTORY-SCHEMA (THE NEW MECHANISM) =====
    t_arm = time.time()
    r_d = arm_d_trajectory_schema(
        E, R, sq, W, chains_test, DEPTH,
        prototypes, chain_to_schema, S_traj,
        cluster_codes, hop_codes, partition_codes,
        "path4_trajectory_schema_per_hop_via_sequence_binding_S_matrix")
    r_d["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    out["arm_d_path4_trajectory_schema"] = r_d
    print(("  [seed=%d] ARM_D PATH4_TRAJECTORY_SCHEMA top1=%.4f "
           "(HP_D=[%.2f,%.2f] lift_C>=%.2f lift_A>=%.2f) "
           "k_pred_mismatch_h10=%.3f traj_cos_h10=%.3f t=%.1fs") % (
        seed, r_d["top1"], HP_D_LO, HP_D_HI,
        HP_LIFT_OVER_C, HP_LIFT_OVER_A,
        r_d["k_pred_per_hop_vs_k_train_mismatch_rate"][9],
        r_d["trajectory_readout_cosine_per_hop"][9],
        r_d["elapsed_s_arm"]), flush=True)
    _hb()

    # ===== ARM E: ORACLE_PER_HOP =====
    def pick_oracle(chain, chain_idx, i, s_now):
        return chain[i][2] // PART_SIZE

    t_arm = time.time()
    r_e = arm_part_restricted(
        E, R, sq, W, chains_test, DEPTH, pick_oracle,
        "oracle_ground_truth_partition_per_hop_upper_bound")
    r_e["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    out["arm_e_oracle_per_hop"] = r_e
    print("  [seed=%d] ARM_E ORACLE_PER_HOP top1=%.4f t=%.1fs" % (
        seed, r_e["top1"], r_e["elapsed_s_arm"]), flush=True)
    _hb()

    # ===== ARM F: RANDOM (floor) =====
    g_arm_f = np.random.default_rng(seed * 7919 + 9)

    def pick_random(chain, chain_idx, i, s_now):
        return int(g_arm_f.integers(0, N_PARTS))

    t_arm = time.time()
    r_f = arm_part_restricted(
        E, R, sq, W, chains_test, DEPTH, pick_random,
        "random_partition_per_hop_floor")
    r_f["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    out["arm_f_random"] = r_f
    print("  [seed=%d] ARM_F RANDOM top1=%.4f t=%.1fs" % (
        seed, r_f["top1"], r_f["elapsed_s_arm"]), flush=True)
    _hb()

    # Lifts
    out["lift_d_over_a"] = round(r_d["top1"] - r_a["top1"], 4)
    out["lift_d_over_b"] = round(r_d["top1"] - r_b["top1"], 4)
    out["lift_d_over_c"] = round(r_d["top1"] - r_c["top1"], 4)
    out["gap_e_minus_d"] = round(r_e["top1"] - r_d["top1"], 4)

    # Gate D positive control verdict
    gate_d_pass = GATED_C_EXPECTED_LO <= r_c["top1"] <= GATED_C_EXPECTED_HI
    out["gate_d_positive_control_pass"] = gate_d_pass
    out["gate_d_arm_c_top1"] = r_c["top1"]

    out["elapsed_s"] = round(time.time() - t, 1)
    return out


# ----------------------------------------------------------------------------
# Verdict
# ----------------------------------------------------------------------------

def _per_hop_partacc_pass(arm_payload: Dict[str, Any]) -> bool:
    pcs = arm_payload.get("partition_correct_per_step")
    if not isinstance(pcs, list) or len(pcs) < 15:
        return False
    return (pcs[4] > HP_PER_HOP_PARTACC
            and pcs[9] > HP_PER_HOP_PARTACC
            and pcs[14] > HP_PER_HOP_PARTACC)


def verdict_from(per_seed: List[Dict[str, Any]]) -> Tuple[str, str, Dict[str, str]]:
    def mean_top1(key: str) -> float:
        vals = [p[key]["top1"] for p in per_seed if key in p
                and isinstance(p[key].get("top1"), (int, float))
                and not math.isnan(p[key]["top1"])]
        return float(np.mean(vals)) if vals else float("nan")

    def cv_top1(key: str) -> float:
        vals = [p[key]["top1"] for p in per_seed if key in p
                and isinstance(p[key].get("top1"), (int, float))
                and not math.isnan(p[key]["top1"])]
        if len(vals) < 2:
            return float("nan")
        m = float(np.mean(vals))
        return float(np.std(vals) / max(m, 1e-9))

    a = mean_top1("arm_a_baseline")
    b = mean_top1("arm_b_path2_perchain")
    c = mean_top1("arm_c_path3_4prim_hop0_locked")
    d = mean_top1("arm_d_path4_trajectory_schema")
    e = mean_top1("arm_e_oracle_per_hop")
    f = mean_top1("arm_f_random")

    # Cardinality (META_RULE_H)
    observed_units = sum(1 for p in per_seed for ak in ARM_KEYS if ak in p)
    cardinality_ok = (observed_units == EXPECTED_N_UNITS)

    # Arms-must-differ (META_RULE_AF)
    arms_hashes = _arms_must_differ_sha256(per_seed)
    unique_hashes = set(arms_hashes.values())
    arms_distinct = (len(unique_hashes) == len(ARM_KEYS))

    saturated_any = (not math.isnan(d)) and d >= HP_SATURATION_CEIL

    cv_d = cv_top1("arm_d_path4_trajectory_schema")

    # Per-hop part-acc for arm D
    pcs_d = (per_seed[0].get("arm_d_path4_trajectory_schema", {})
             .get("partition_correct_per_step", []) if per_seed else [])
    per_hop_d_ok = _per_hop_partacc_pass(
        per_seed[0].get("arm_d_path4_trajectory_schema", {})) if per_seed else False

    def _hop_str(pcs: List[float]) -> str:
        if not pcs or len(pcs) < 15:
            return "n/a"
        return "h5=%.3f h10=%.3f h15=%.3f" % (pcs[4], pcs[9], pcs[14])

    rail_breach = sum(1 for p in per_seed
                      if not p.get("baseline_rail_ok", False))

    # Gate D positive control
    gate_d_pass = (per_seed[0].get("gate_d_positive_control_pass", False)
                   if per_seed else False)
    gate_d_c_val = (per_seed[0].get("gate_d_arm_c_top1", float("nan"))
                    if per_seed else float("nan"))

    # k_pred mismatch + traj cosine at hop 10
    kpm = (per_seed[0].get("arm_d_path4_trajectory_schema", {})
           .get("k_pred_per_hop_vs_k_train_mismatch_rate", []) if per_seed else [])
    trc = (per_seed[0].get("arm_d_path4_trajectory_schema", {})
           .get("trajectory_readout_cosine_per_hop", []) if per_seed else [])
    kpm_h10 = kpm[9] if len(kpm) > 9 else float("nan")
    trc_h10 = trc[9] if len(trc) > 9 else float("nan")

    summ = (
        "BASELINE_A=%.4f (rail_breach=%d/%d) PATH2_B=%.4f "
        "PATH3_C=%.4f (Gate_D_pass=%s expected=[%.2f,%.2f]) "
        "PATH4_D=%.4f (lift_C=%.4f lift_A=%.4f part %s cv=%.3f "
        "k_pred_mismatch_h10=%.3f traj_cos_h10=%.3f) "
        "ORACLE_E=%.4f RANDOM_F=%.4f cardinality_ok=%s expected_units=%d "
        "observed_units=%d arms_distinct=%s saturated_any=%s depth=%d "
        "HP_D=[%.2f,%.2f] HF_D_abs=%.2f HF_lift_C=%.2f"
    ) % (
        a, rail_breach, len(per_seed), b,
        c, gate_d_pass, GATED_C_EXPECTED_LO, GATED_C_EXPECTED_HI,
        d, (d - c if not math.isnan(d) else float("nan")),
        (d - a if not math.isnan(d) else float("nan")),
        _hop_str(pcs_d), cv_d, kpm_h10, trc_h10,
        e, f, cardinality_ok, EXPECTED_N_UNITS, observed_units,
        arms_distinct, saturated_any, DEPTH,
        HP_D_LO, HP_D_HI, HF_D_ABS, HF_LIFT_OVER_C,
    )

    # Cardinality FIRST (META_RULE_H)
    if not cardinality_ok:
        return ("HARD_FAIL_CARDINALITY_BREACH",
                "HARD_FAIL_CARDINALITY_BREACH: " + summ, arms_hashes)

    if not arms_distinct:
        return ("HARD_FAIL_ARMS_TIED",
                "HARD_FAIL_ARMS_TIED_NO_DISCRIMINATION: " + summ, arms_hashes)

    # Gate D positive control: arm_c must reproduce Drill A regime (<= 0.30)
    if not gate_d_pass:
        return ("HARD_FAIL_GATE_D_REGIME_MISMATCH",
                ("HARD_FAIL_GATE_D_POSITIVE_CONTROL_FAILED_ARM_C=%.4f_"
                 "OUTSIDE_[%.2f,%.2f]_INVESTIGATE_REGIME_INVOCATION: ") % (
                    gate_d_c_val, GATED_C_EXPECTED_LO, GATED_C_EXPECTED_HI
                ) + summ, arms_hashes)

    # ORACLE sanity (E must beat D unless D close to ceiling)
    if (not math.isnan(e)) and (not math.isnan(d)) \
            and e <= d - 0.001 and d < 0.99:
        return ("HARD_FAIL_ORACLE_BELOW_MECHANISM",
                "HARD_FAIL_ORACLE_NOT_UPPER_BOUND: " + summ, arms_hashes)

    # RANDOM floor breach
    if (not math.isnan(f)) and f >= HP_RANDOM_CEIL:
        return ("HARD_FAIL_RANDOM_FLOOR_BREACH",
                "HARD_FAIL_RANDOM_FLOOR_NOT_BELOW_CEIL: " + summ, arms_hashes)

    # HARD_FAIL gates per 2x-discipline (CAPABILITY CLOSURE TRIGGER)
    hf_reasons = []
    if (not math.isnan(d)) and d <= HF_D_ABS:
        hf_reasons.append("D_below_abs(%.4f<=%.2f)" % (d, HF_D_ABS))
    if (not math.isnan(d)) and (not math.isnan(c)) and (d - c) < HF_LIFT_OVER_C:
        hf_reasons.append("lift_C_below(%.4f<%.2f)" % (d - c, HF_LIFT_OVER_C))
    if (not math.isnan(d)) and (not math.isnan(a)) and d < a:
        hf_reasons.append("D_below_A(%.4f<%.4f)_cascade_collapse" % (d, a))
    if len(pcs_d) > 9 and pcs_d[9] <= HF_PER_HOP_AT_HOP10:
        hf_reasons.append("per_hop_h10_below(%.4f<=%.2f)" % (
            pcs_d[9], HF_PER_HOP_AT_HOP10))

    if hf_reasons:
        return ("HARD_FAIL_CAPABILITY_CLOSURE",
                ("HARD_FAIL_4_PRIMITIVE_BRAIN_FAITHFUL_COMPOSITION_CLOSES_"
                 "PER_2X_DRILL_DISCIPLINE_DRILL_A_AND_B_BOTH_NULL_M3_NEEDS_"
                 "EXTERNAL_CORTEX_LAYER_reasons=[%s]: ") % (",".join(hf_reasons))
                + summ, arms_hashes)

    # HARD_PASS check for arm D (the mechanism)
    hp_d_ok = (
        (not math.isnan(d))
        and HP_D_LO <= d <= HP_D_HI
        and (not math.isnan(c)) and (d - c) >= HP_LIFT_OVER_C
        and (not math.isnan(a)) and (d - a) >= HP_LIFT_OVER_A
        and per_hop_d_ok
        and (not math.isnan(e)) and e > d
        and (not math.isnan(f)) and f < HP_RANDOM_CEIL
        and not saturated_any
    )

    if RUN_MODE == "smoke":
        if hp_d_ok:
            return ("SMOKE_HARD_PASS",
                    ("SMOKE_HARD_PASS_PATH4_TRAJECTORY_SCHEMA_BRAIN_FAITHFUL_"
                     "4_PRIMITIVE_COMPOSITION_BREAKS_BARRIER_1_MULTI_HOP_AT_"
                     "DEPTH_15_VIA_SEQUENCE_BINDING_S_MATRIX: ") + summ, arms_hashes)

        # MIDDLE_BAND: D in [HF_D_ABS, HP_D_LO] AND (D - C) >= MM_LIFT_MIN
        if (not math.isnan(d)) and HF_D_ABS < d < HP_D_LO \
                and (not math.isnan(c)) and (d - c) >= MM_LIFT_MIN:
            return ("MIDDLE_BAND_PARTIAL_MECHANISM",
                    ("MIDDLE_BAND_PATH4_PARTIAL_LIFT_capability_box_open_for_v2_"
                     "modern_hopfield_or_resonator_cleaned_readout: ") + summ,
                    arms_hashes)
        return ("HARD_FAIL_NO_PASS",
                "HARD_FAIL_PATH4_DID_NOT_REACH_HP_OR_MM_BAND: " + summ,
                arms_hashes)

    # FULL verdict
    if hp_d_ok:
        return ("HARD_PASS_CHAIN_GRADE_4_PRIMITIVE_TRAJECTORY_SCHEMA",
                ("HARD_PASS_PATH4_TRAJECTORY_SCHEMA_BRAIN_FAITHFUL_4_PRIMITIVE_"
                 "DEPTH_15_BARRIER_1_BROKEN_VIA_SEQUENCE_BINDING_S_MATRIX: ")
                + summ, arms_hashes)

    if (not math.isnan(d)) and HF_D_ABS < d < HP_D_LO \
            and (not math.isnan(c)) and (d - c) >= MM_LIFT_MIN:
        return ("MIDDLE_BAND_PARTIAL_MECHANISM",
                "MIDDLE_BAND_PATH4_PARTIAL_LIFT: " + summ, arms_hashes)

    return ("HARD_FAIL_NO_PASS",
            "HARD_FAIL_PATH4_NO_PASS: " + summ, arms_hashes)


# ----------------------------------------------------------------------------
# atexit synthesizer + main
# ----------------------------------------------------------------------------

_RESULTS_HOLDER: Dict[str, Any] = {"out_dir": None, "started_at": time.time()}


def _atexit_synth() -> None:
    od = _RESULTS_HOLDER["out_dir"]
    if od is None:
        return
    try:
        agg = aggregate_partials(od, seeds=[str(s) for s in SEEDS],
                                 run_config={"N": N_DIM, "run_mode": RUN_MODE,
                                             "anchor": ANCHOR_NAME})
        if not agg:
            return
        per_seed = [agg[k] for k in sorted(agg.keys())]
        if not per_seed:
            return
        if (od / "metrics.json").exists():
            return
        v, vmsg, ahashes = verdict_from(per_seed)
        metrics = {
            "anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg,
            "run_mode": RUN_MODE, "n_seeds": len(per_seed),
            "config_version": CONFIG_VERSION, "per_seed": per_seed,
            "elapsed_s": round(time.time() - _RESULTS_HOLDER["started_at"], 1),
            "summary": vmsg, "_atexit_synth": True,
            "_llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
            "expected_n_units": EXPECTED_N_UNITS,
            "expected_arms": list(ARM_KEYS),
            "arms_must_differ_sha256": ahashes,
        }
        write_metrics(od, metrics, results=per_seed)
        print("[atexit] wrote synth metrics.json (%d seeds)" % len(per_seed),
              flush=True)
    except SystemExit:
        raise
    except BaseException as ex:  # noqa: BLE001
        print("[atexit] FAIL: %s" % ex, flush=True)


atexit.register(_atexit_synth)


if __name__ == "__main__":
    print("[config] anchor=%s mode=%s seeds=%s | %s" % (
        ANCHOR_NAME, RUN_MODE, SEEDS, CONFIG_VERSION), flush=True)
    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)
    _RESULTS_HOLDER["out_dir"] = out_dir

    hb_path = REPO / "data" / "heartbeats" / "exp_dev.timestamp"
    try:
        hb_path.write_text(time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                           encoding="utf-8")
    except Exception:
        pass

    run_config = {"N": N_DIM, "run_mode": RUN_MODE, "anchor": ANCHOR_NAME}
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print("[ckpt] done=%s remaining=%s" % (done, remaining), flush=True)

    for s in remaining:
        try:
            rec = run_seed(s)
            write_partial_key(out_dir, s, rec)
        except SystemExit:
            raise
        except BaseException as ex:  # noqa: BLE001
            print("[CRASH_DIAGNOSTIC] seed=%d anchor=%s exc=%r" % (
                s, ANCHOR_NAME, ex), flush=True)
            raise

    agg = aggregate_partials(out_dir, seeds=[str(s) for s in SEEDS],
                             run_config=run_config)
    per_seed = [agg[str(s)] for s in SEEDS if str(s) in agg]
    if not per_seed:
        print("[FATAL] no partials available", flush=True)
        sys.exit(1)

    assert _LLM_CALL_COUNTER[0] == 0

    v, vmsg, ahashes = verdict_from(per_seed)
    print("\n[VERDICT] " + vmsg, flush=True)
    print("[arms_must_differ_sha256] %s" % ahashes, flush=True)
    metrics = {
        "anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg,
        "run_mode": RUN_MODE, "n_seeds": len(per_seed),
        "config_version": CONFIG_VERSION, "per_seed": per_seed,
        "elapsed_s": round(time.time() - _RESULTS_HOLDER["started_at"], 1),
        "summary": vmsg,
        "_llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
        "expected_n_units": EXPECTED_N_UNITS,
        "expected_arms": list(ARM_KEYS),
        "arms_must_differ_sha256": ahashes,
        "DESIGN_NOTE": (
            "DRILL B: per-hop schema-Bayes redesign via sequence-binding "
            "trajectory map. Replaces Drill A's hop-0-locked "
            "cluster_to_target_part[k] map with per-(cluster_k, hop_idx) -> "
            "partition trajectory store via the substrate's chain-grade "
            "sequence-binding S matrix in native shape. Mechanism (arm D): at "
            "inference per hop i, schema-Bayes picks k_pred from past-hop "
            "predicates, then traj_key = cluster_codes[k_pred] * hop_codes[i], "
            "partition_vec = S @ traj_key, target_part = argmax(partition_codes "
            "@ partition_vec). Capacity ratio K_seq/N = 300/8192 = 0.037 << "
            "cliff 0.50 THEORETICAL@. Drill A SUB_A reproduced as arm C "
            "(positive control discriminator; Gate D expected <= 0.30). 6 arms "
            "x single seed (seed=7); siblings seed=13, seed=19. 2x-discipline "
            "gateway: HARD_PASS -> Barrier 1 multi-hop chain composition "
            "broken at depth 15; HARD_FAIL -> 4-primitive brain-faithful "
            "capability box CLOSES per 2x discipline (M3 needs external cortex "
            "layer). Regime matches Drill A: N=8192 V_C=4000 d=15 psz=800 "
            "K=200. META_RULE_AC/AE/AF/AG/AH/AL/AN/AP/H tagged. Sources: "
            "experiments/exp_substrate_partition_oracle_pfc_wm_state_tracker_"
            "v1_seed_13.py (template); pre-reg preregs/2026-06-28_substrate_"
            "partition_oracle_trajectory_schema_per_hop_v1.md; drill notes/"
            "research_drill_per_hop_schema_bayes_redesign_drill_B_2026-06-28.md."
        ),
    }
    write_metrics(out_dir, metrics, results=per_seed)
    print("[done] metrics.json written (%d seeds, %.1fs)" % (
        len(per_seed), metrics["elapsed_s"]), flush=True)
