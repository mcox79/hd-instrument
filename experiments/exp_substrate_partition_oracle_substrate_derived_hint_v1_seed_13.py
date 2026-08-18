"""substrate_partition_oracle_substrate_derived_hint_v1_seed_13.

PURPOSE (M3-USABLE Barrier 1 break via primitive composition):
    The `_hardened_v1` cell SMOKE_HARD_PASS used ORACLE_B with GROUND-TRUTH
    partition assignment (target_part = target_o // part_size; gen-time peek).
    That's an upper-bound test, not M3-usable.

    This cell composes the chain-grade partition-routing primitive
    (exp_substrate_partition_routing_10M_full_v2 MEASURED@M=1M routed=0.95
    route_acc=1.0) into the multihop oracle cell to DERIVE the partition hint
    from substrate state alone.

    Composition mechanism (substrate-native; no gen-time peek):
      ingest:  C[p] = normalize(mean(E_part[p] @ W) over partition rows)
               per-partition centroid in W-output space (substrate-learned)
      query:   key   = E[s] * R[p] * sq
               state = W @ key
               pred_part = argmax(C @ state)      # SUBSTRATE-DERIVED hint
               scores = E_part[pred_part] @ state
               s_pred = pred_part * psz + argmax(scores)

    No ground-truth at query time. M3-usable.

ARMS (5; all psz=800 / 5 partitions for clean derived-vs-oracle gap test):
    A: BASELINE          argmax over V_C=4000 (no hint; rail)
    B: SUBSTRATE_DERIVED substrate-centroid routing (M3-usable mechanism)
    C: ORACLE            ground-truth partition (upper bound)
    D: NOISY_HINT        random-permuted partition labels (negative control)
    E: RANDOM            random partition pick per hop (floor)

PRE-REG BANDS (META_RULE_AL; LOCKED at module init):
    BASELINE rail (BIAS-S):
        ARM_A.top1@d15 in [0.30, 0.70]
    HARD_PASS (cell-grade; M3-usable mechanism real):
        ARM_B.top1@d15 in [0.50, 0.95]
        AND ARM_B - ARM_A >= 0.30  (real signal vs baseline)
        AND ARM_B - ARM_E >= 0.30  (vs random floor)
        AND ARM_C - ARM_B <= 0.30  (substrate retains most of oracle's lift)
        AND |ARM_D - ARM_A| <= 0.10 (noisy-hint sanity)
        AND saturation == False (ARM_B < 0.95)
        AND arms_distinct == True
    HARD_FAIL:
        ARM_B.top1@d15 <= 0.30
        OR (ARM_B - ARM_A) < 0.10
        OR (saturation AND lift_b_a < 0.20)
    MIDDLE_BAND:
        ARM_B in [0.30, 0.50) with lift_b_a >= 0.15
        OR HP-band hit BUT lift_b_a in [0.15, 0.30)
        OR ARM_D sanity violated (|D - A| > 0.10)

DISCIPLINE TAGS:
    META_RULE_AC: number tagging MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@
    META_RULE_AE: absolute metrics.json paths in DESIGN_NOTE
    META_RULE_AF: arms-must-differ SHA-256 hash check post-run
    META_RULE_AG: discriminator at edge-of-capacity (B un-saturated; A in rail)
    META_RULE_AH: atomic metrics.json write (via _seed_checkpoint)
    META_RULE_AL: HP + HF bands LOCKED at module init
    META_RULE_AN: substrate-empirical anchor (per_step=0.948)
    META_RULE_H : CARDINALITY_OK; expected_n_units = 5 (1 seed x 5 arms)
    BIAS-Q     : saturation guard at 0.95
    BIAS-N     : per-arm metrics in summary (NOT verdict_msg only)
    BIAS-S     : baseline rail [0.30, 0.70]
    DISCRIMINATOR-MUST-SURVIVE-SCALE: smoke at FULL-N + FULL-depth
    PROT-018: regime params bind to ANCHOR_NAME in CONFIG_VERSION
    Fix #28: per-arm reads from metrics.json
    CHUNKED: single seed per cell; sibling cells for seeds 13 and 19
    functional_requirement_first: primitive mapped (routing + cleanup) BEFORE
        cell design; composition documented in DESIGN_NOTE

SOURCE CITATIONS (ABSOLUTE PATHS; META_RULE_AE):
    - Source oracle cell (ground-truth; upper-bound test):
      d:/AI/hd-instrument/experiments/exp_substrate_multihop_partition_oracle_v5_hardened_FULL_seed_11_v1.py
    - Source smoke metrics (SMOKE_HARD_PASS w/ ORACLE_B=0.90):
      d:/AI/hd-instrument/data/exp_substrate_multihop_partition_oracle_v5_hardened_v1_smoke/metrics.json
    - Partition routing primitive (chain-grade M=1M; mechanism being composed):
      d:/AI/hd-instrument/experiments/exp_substrate_partition_routing_10M_full_v2.py
    - Partition routing metrics (routed=0.95 route_acc=1.0 @ M=1M):
      d:/AI/hd-instrument/data/exp_substrate_partition_routing_10M_full_v2/metrics.json
    - Prereg:
      d:/AI/hd-instrument/preregs/2026-06-28_substrate_partition_oracle_substrate_derived_hint_v1.md
    - Parent prereg (hardened oracle ground-truth):
      d:/AI/hd-instrument/preregs/2026-06-28_substrate_multihop_partition_oracle_v5_hardened_v1.md

NUMBER TAGGING (META_RULE_AC):
    MEASURED@SOURCE_ORACLE_B_SMOKE: 0.90 (source smoke ARM_B w/ ground-truth)
    MEASURED@SOURCE_BASELINE_SMOKE: 0.39 (source smoke ARM_A)
    MEASURED@PARTITION_ROUTING_M1M: routed=0.95 route_acc=1.0
    HYPOTHESIZED@HP_BAND_DERIVED_B: in [0.50, 0.95]
    HYPOTHESIZED@HP_LIFT_DERIVED_VS_BASELINE: >= 0.30
    HYPOTHESIZED@HP_GAP_ORACLE_VS_DERIVED: <= 0.30
    HYPOTHESIZED@NOISY_D_SANITY: |D - A| <= 0.10
    THEORETICAL@RANDOM_E_FLOOR: 0.20^15 ~ 3e-11

Author: exp_dev 2026-06-28 (functional-requirement-first per USER directive).
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

ANCHOR_NAME = "substrate_partition_oracle_substrate_derived_hint_v1_seed_13"
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

# BASELINE rail @d=15 -- discriminating mid-band (matches `_hardened_v1` source)
BASELINE_RAIL_TARGET = 0.449     # THEORETICAL@DEPTH_SCALE_BASELINE
BASELINE_RAIL_LO = 0.30
BASELINE_RAIL_HI = 0.70

# ARM_B substrate-derived bands @d=15 -- un-saturated discriminating
HP_ARM_B_LO = 0.50               # HYPOTHESIZED@HP_BAND_DERIVED_B floor
HP_ARM_B_HI = 0.95               # ceiling (sat-aware)
HP_LIFT_OVER_BASELINE = 0.30     # HARDER than oracle's 0.20: real M3-usable signal
HP_LIFT_OVER_RANDOM = 0.30       # ARM_B - ARM_E >= 0.30 (RANDOM proj ~0)
HP_GAP_ORACLE_OVER_DERIVED = 0.30  # ARM_C - ARM_B <= 0.30 (substrate retains lift)
HP_NOISY_SANITY_BAND = 0.10      # |D - A| <= 0.10 (noisy-hint matches baseline)
HP_CV_MAX = 0.15                 # cv across seeds (post-hoc cross-cell)
HP_SATURATION_CEIL = 0.95        # BIAS-Q

HF_ARM_B_ABS = 0.30              # mechanism dies
HF_LIFT_MIN_FOR_SIGNAL = 0.10    # HARD_FAIL if lift < 0.10 (no signal at all)
HF_LIFT_MIN_IF_SATURATED = 0.20
MM_LIFT_MIN = 0.15

# Partitioning: ALL 4 partition-arms use IDENTICAL psz=800 / 5 parts.
# Only the partition-prediction MECHANISM differs (derived / oracle / noisy / random).
# Clean derived-vs-oracle gap test (controls partition geometry).
def _cone_collapse_crosstalk(v_c_per_hop: int, n: int) -> float:
    return float(math.sqrt(max(v_c_per_hop - 1, 1) / max(n, 1)))

N_PART = 5                         # 5 partitions for all 4 partition arms
PART_SIZE = V_CONCEPTS // N_PART   # 800
assert V_CONCEPTS % N_PART == 0

CROSSTALK_PART = _cone_collapse_crosstalk(PART_SIZE, N_DIM)
CROSSTALK_BASELINE = _cone_collapse_crosstalk(V_CONCEPTS, N_DIM)

# Locked invariants (META_RULE_AL)
assert BASELINE_RAIL_LO < BASELINE_RAIL_TARGET < BASELINE_RAIL_HI
assert HP_ARM_B_LO > HF_ARM_B_ABS, "HP floor must exceed HF ceiling"
assert HP_ARM_B_LO < HP_ARM_B_HI <= HP_SATURATION_CEIL
assert HP_LIFT_OVER_BASELINE > MM_LIFT_MIN
assert HP_LIFT_OVER_BASELINE > HF_LIFT_MIN_FOR_SIGNAL
assert 0.0 < HP_NOISY_SANITY_BAND < 0.2
assert 0.0 < HP_GAP_ORACLE_OVER_DERIVED < 1.0
assert CROSSTALK_PART < CROSSTALK_BASELINE
assert abs(CROSSTALK_PART - math.sqrt(799 / 8192)) < 1e-6
assert DEPTH == 15

# Chain configuration -- single seed per cell (CHUNKED architecture)
N_CHAINS_TRAIN = 200
if RUN_MODE == "smoke":
    SEEDS = [13]
    N_CHAINS_TEST = 100
else:
    SEEDS = [13]
    N_CHAINS_TEST = 200

# Cardinality (META_RULE_H)
N_ARMS = 5
EXPECTED_N_UNITS = N_ARMS * len(SEEDS)

ENCODER_PROVENANCE = "SUBSTRATE_NATIVE_BIPOLAR"

CONFIG_VERSION = (
    "ANCHOR=%s,substrateDerivedHintV1: N=%d V_C=%d V_P=%d depth=%d "
    "n_chains_train=%d n_chains_test=%d seeds=%s mode=%s encoder=%s "
    "n_parts=%d psz=%d xtalk=%.4f baseline_xtalk=%.4f "
    "RAIL=[%.3f,%.3f] target=%.3f HP_B_band=[%.2f,%.2f] HP_lift_base=%.2f "
    "HP_lift_rand=%.2f HP_gap_oracle=%.2f HP_noisy_band=%.2f HP_cv_max=%.2f "
    "HP_sat_ceil=%.2f HF_B_abs=%.2f HF_lift_min_signal=%.2f "
    "HF_lift_min_if_sat=%.2f MM_lift_min=%.2f expected_units=%d arms=%d"
) % (
    ANCHOR_NAME,
    N_DIM, V_CONCEPTS, V_PRED, DEPTH,
    N_CHAINS_TRAIN, N_CHAINS_TEST, SEEDS, RUN_MODE, ENCODER_PROVENANCE,
    N_PART, PART_SIZE, CROSSTALK_PART, CROSSTALK_BASELINE,
    BASELINE_RAIL_LO, BASELINE_RAIL_HI, BASELINE_RAIL_TARGET,
    HP_ARM_B_LO, HP_ARM_B_HI, HP_LIFT_OVER_BASELINE, HP_LIFT_OVER_RANDOM,
    HP_GAP_ORACLE_OVER_DERIVED, HP_NOISY_SANITY_BAND, HP_CV_MAX,
    HP_SATURATION_CEIL, HF_ARM_B_ABS, HF_LIFT_MIN_FOR_SIGNAL,
    HF_LIFT_MIN_IF_SATURATED, MM_LIFT_MIN, EXPECTED_N_UNITS, N_ARMS,
)


# ----------------------------------------------------------------------------
# Primitives (verbatim numpy port from parent hardened cell)
# ----------------------------------------------------------------------------

def bipolar(M: int, n: int, g: np.random.Generator) -> np.ndarray:
    """Bipolar bit vectors; row-normalized."""
    X = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)


def ingest_hebbian(triples, E: np.ndarray, R: np.ndarray, sq: float,
                   n_dim: int, batch: int = 2000) -> np.ndarray:
    """Hebbian outer-product ingest."""
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
# Substrate-derived partition centroids (the M3-usable composition)
# ----------------------------------------------------------------------------

def build_partition_centroids(E: np.ndarray, W: np.ndarray,
                              part_size: int, n_partitions: int) -> np.ndarray:
    """SUBSTRATE-DERIVED partition signatures.

    For each partition p, compute the mean of (E_part[p] @ W) -- the typical
    OUTPUT state when atoms in partition p are addressed. At query time, the
    state W @ key is matched against these centroids via argmax to predict
    which partition the target lies in. This is the substrate-native
    composition of the chain-grade partition-routing primitive (centroid-
    routing in W-output space) into the multihop oracle cell.

    No gen-time peek: centroids are built purely from substrate state
    (E and W) which any agent inspecting the substrate could compute.

    Returns: (n_partitions, n_dim) array; rows are unit-normalized centroids.
    """
    n_dim = E.shape[1]
    C = np.zeros((n_partitions, n_dim), dtype=np.float32)
    for p in range(n_partitions):
        E_part = E[p * part_size:(p + 1) * part_size]  # (psz, n_dim)
        # Each atom's OUTPUT state when it is addressed:
        #   state_atom = W @ atom_key, but atom_key is the binding (E[s] * R[p_rel] * sq);
        # We want a partition-level signature in OUTPUT-state space, so use
        # E_part @ W which is the typical W-row mass projected onto partition rows.
        # Mean reduction across the partition's atoms gives the centroid.
        proj = E_part @ W  # (psz, n_dim)
        c = proj.mean(axis=0)
        nrm = float(np.linalg.norm(c)) + 1e-8
        C[p] = c / nrm
    return C


# ----------------------------------------------------------------------------
# Arms
# ----------------------------------------------------------------------------

def arm_baseline(E: np.ndarray, R: np.ndarray, sq: float,
                 W: np.ndarray, chains_test: List[List[Tuple[int, int, int]]],
                 depth: int) -> Dict[str, Any]:
    """Baseline: argmax over full V_C cleanup at each hop (no hint)."""
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


def arm_substrate_derived(E: np.ndarray, R: np.ndarray, sq: float,
                          W: np.ndarray,
                          chains_test: List[List[Tuple[int, int, int]]],
                          depth: int, part_size: int,
                          C: np.ndarray) -> Dict[str, Any]:
    """SUBSTRATE-DERIVED partition routing (M3-usable mechanism).

    At each hop: state = W @ key; pred_part = argmax(C @ state); cleanup
    over E_part[pred_part]. No ground-truth used. Records routing accuracy
    (pred_part == true_part) as a diagnostic.
    """
    n = len(chains_test)
    hits = 0
    per_step_hits = np.zeros(depth, dtype=np.int64)
    route_hits = 0
    route_total = 0
    n_partitions = E.shape[0] // part_size
    E_parts = [E[p * part_size:(p + 1) * part_size]
               for p in range(n_partitions)]
    for chain in chains_test:
        s = chain[0][0]
        for i in range(depth):
            p = chain[i][1]
            target_o = chain[i][2]
            true_part = target_o // part_size
            key = (E[s] * R[p] * sq).astype(np.float32)
            state = W @ key
            # SUBSTRATE-DERIVED HINT (no gen-time peek):
            pred_part = int((C @ state).argmax())
            route_total += 1
            if pred_part == true_part:
                route_hits += 1
            scores = E_parts[pred_part] @ state
            local_idx = int(scores.argmax())
            s_pred = pred_part * part_size + local_idx
            if s_pred == target_o:
                per_step_hits[i] += 1
            s = s_pred
        if s == chain[depth - 1][2]:
            hits += 1
    return {
        "top1": round(hits / max(n, 1), 4),
        "per_step_acc": [round(float(x) / max(n, 1), 4)
                         for x in per_step_hits],
        "n_queries": n, "depth": depth,
        "n_partitions": n_partitions, "part_size": part_size,
        "route_acc": round(route_hits / max(route_total, 1), 4),
        "route_hits": int(route_hits), "route_total": int(route_total),
        "mechanism": "substrate_derived_centroid_routing_M3_usable",
    }


def arm_oracle_ground_truth(E: np.ndarray, R: np.ndarray, sq: float,
                            W: np.ndarray,
                            chains_test: List[List[Tuple[int, int, int]]],
                            depth: int, part_size: int) -> Dict[str, Any]:
    """ORACLE upper bound: ground-truth partition (gen-time peek)."""
    n = len(chains_test)
    hits = 0
    per_step_hits = np.zeros(depth, dtype=np.int64)
    n_partitions = E.shape[0] // part_size
    E_parts = [E[p * part_size:(p + 1) * part_size]
               for p in range(n_partitions)]
    for chain in chains_test:
        s = chain[0][0]
        for i in range(depth):
            p = chain[i][1]
            target_o = chain[i][2]
            target_part = target_o // part_size  # ORACLE
            key = (E[s] * R[p] * sq).astype(np.float32)
            state = W @ key
            scores = E_parts[target_part] @ state
            local_idx = int(scores.argmax())
            s_pred = target_part * part_size + local_idx
            if s_pred == target_o:
                per_step_hits[i] += 1
            s = s_pred
        if s == chain[depth - 1][2]:
            hits += 1
    return {
        "top1": round(hits / max(n, 1), 4),
        "per_step_acc": [round(float(x) / max(n, 1), 4)
                         for x in per_step_hits],
        "n_queries": n, "depth": depth,
        "n_partitions": n_partitions, "part_size": part_size,
        "mechanism": "oracle_ground_truth_partition_upper_bound",
    }


def arm_noisy_hint(E: np.ndarray, R: np.ndarray, sq: float,
                   W: np.ndarray,
                   chains_test: List[List[Tuple[int, int, int]]],
                   depth: int, part_size: int,
                   g: np.random.Generator) -> Dict[str, Any]:
    """NOISY hint: random-permuted partition labels (negative control).

    A fixed permutation is sampled per chain; hint_p = perm[true_p]. So the
    hint is consistent within a chain (not pure random per hop), but the
    mapping carries zero information about the actual target. Sanity check:
    should match BASELINE (no info means no lift over baseline + can hurt
    via wrong-partition cleanup-narrowing).
    """
    n = len(chains_test)
    hits = 0
    per_step_hits = np.zeros(depth, dtype=np.int64)
    n_partitions = E.shape[0] // part_size
    E_parts = [E[p * part_size:(p + 1) * part_size]
               for p in range(n_partitions)]
    for chain in chains_test:
        # Permutation per chain (deterministic given g)
        perm = g.permutation(n_partitions)
        s = chain[0][0]
        for i in range(depth):
            p = chain[i][1]
            target_o = chain[i][2]
            true_part = target_o // part_size
            noisy_part = int(perm[true_part])  # permuted label; no info
            key = (E[s] * R[p] * sq).astype(np.float32)
            state = W @ key
            scores = E_parts[noisy_part] @ state
            local_idx = int(scores.argmax())
            s_pred = noisy_part * part_size + local_idx
            if s_pred == target_o:
                per_step_hits[i] += 1
            s = s_pred
        if s == chain[depth - 1][2]:
            hits += 1
    return {
        "top1": round(hits / max(n, 1), 4),
        "per_step_acc": [round(float(x) / max(n, 1), 4)
                         for x in per_step_hits],
        "n_queries": n, "depth": depth,
        "n_partitions": n_partitions, "part_size": part_size,
        "mechanism": "noisy_permuted_partition_label_negative_control",
    }


def arm_random_partition(E: np.ndarray, R: np.ndarray, sq: float,
                         W: np.ndarray,
                         chains_test: List[List[Tuple[int, int, int]]],
                         depth: int, part_size: int,
                         g: np.random.Generator) -> Dict[str, Any]:
    """RANDOM: random partition per hop (floor)."""
    n = len(chains_test)
    hits = 0
    per_step_hits = np.zeros(depth, dtype=np.int64)
    n_partitions = E.shape[0] // part_size
    E_parts = [E[p * part_size:(p + 1) * part_size]
               for p in range(n_partitions)]
    for chain in chains_test:
        s = chain[0][0]
        for i in range(depth):
            p = chain[i][1]
            target_o = chain[i][2]
            chosen_part = int(g.integers(0, n_partitions))
            key = (E[s] * R[p] * sq).astype(np.float32)
            state = W @ key
            scores = E_parts[chosen_part] @ state
            local_idx = int(scores.argmax())
            s_pred = chosen_part * part_size + local_idx
            if s_pred == target_o:
                per_step_hits[i] += 1
            s = s_pred
        if s == chain[depth - 1][2]:
            hits += 1
    return {
        "top1": round(hits / max(n, 1), 4),
        "per_step_acc": [round(float(x) / max(n, 1), 4)
                         for x in per_step_hits],
        "n_queries": n, "depth": depth,
        "n_partitions": n_partitions, "part_size": part_size,
        "mechanism": "random_partition_per_hop_floor",
    }


# ----------------------------------------------------------------------------
# Arms-must-differ SHA-256 (META_RULE_AF)
# ----------------------------------------------------------------------------

def _arms_must_differ_sha256(per_seed: List[Dict[str, Any]]) -> Dict[str, str]:
    hashes: Dict[str, str] = {}
    arm_keys = [
        "arm_a_baseline",
        "arm_b_substrate_derived",
        "arm_c_oracle",
        "arm_d_noisy_hint",
        "arm_e_random",
    ]
    for k in arm_keys:
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
# Self-test
# ----------------------------------------------------------------------------

def _selftest() -> None:
    g = np.random.default_rng(0)
    n_tiny = 256
    V_tiny = 40
    P_tiny = 4
    sq = math.sqrt(n_tiny)
    E = bipolar(V_tiny, n_tiny, g)
    R = bipolar(P_tiny, n_tiny, g)

    # T1: bipolar shapes + norm
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

    # T4: centroid construction (8 partitions of 5 atoms each for V_tiny=40)
    part_sz_tiny = V_tiny // 8
    assert V_tiny % 8 == 0
    C = build_partition_centroids(E, W, part_sz_tiny, n_partitions=8)
    assert C.shape == (8, n_tiny)
    # Centroids should be unit-norm
    nrms = np.linalg.norm(C, axis=1)
    assert np.all(np.abs(nrms - 1.0) < 1e-3), \
        "centroid norms not unit: %s" % nrms

    # T5: all 5 arms produce valid output at tiny config
    r_a = arm_baseline(E, R, sq, W, chains, depth=DEPTH)
    r_b = arm_substrate_derived(E, R, sq, W, chains, depth=DEPTH,
                                part_size=part_sz_tiny, C=C)
    r_c = arm_oracle_ground_truth(E, R, sq, W, chains, depth=DEPTH,
                                  part_size=part_sz_tiny)
    r_d = arm_noisy_hint(E, R, sq, W, chains, depth=DEPTH,
                         part_size=part_sz_tiny, g=g)
    r_e = arm_random_partition(E, R, sq, W, chains, depth=DEPTH,
                               part_size=part_sz_tiny, g=g)
    for r in (r_a, r_b, r_c, r_d, r_e):
        assert 0.0 <= r["top1"] <= 1.0
        assert len(r["per_step_acc"]) == DEPTH

    # T6: substrate-derived arm tracks route_acc
    assert "route_acc" in r_b
    assert 0.0 <= r_b["route_acc"] <= 1.0
    assert r_b["route_total"] == 8 * DEPTH

    # T7: ORACLE >= SUBSTRATE_DERIVED at the floor (oracle is upper bound)
    # NOT a strict invariant at tiny config (random fluctuation) -- just
    # verify the relationship is in the right direction at expectation:
    # we'd expect oracle to have route_acc=1.0 by construction; substrate-
    # derived has route_acc in [0, 1]. Substrate top1 <= oracle top1
    # at expectation but not strictly enforced at tiny n.

    # T8: cone-collapse formula sanity
    assert abs(CROSSTALK_PART - 0.3123) < 0.001, \
        "psz=800/N=8192 xtalk drift: %.4f" % CROSSTALK_PART
    assert CROSSTALK_BASELINE > 0.6

    # T9: bands LOCKED (regression on band drift)
    assert N_DIM == 8192
    assert V_CONCEPTS == 4000
    assert DEPTH == 15
    assert PART_SIZE == 800
    assert N_PART == 5
    assert HP_ARM_B_LO == 0.50
    assert HP_ARM_B_HI == 0.95
    assert HF_ARM_B_ABS == 0.30
    assert BASELINE_RAIL_LO == 0.30
    assert BASELINE_RAIL_HI == 0.70
    assert HP_LIFT_OVER_BASELINE == 0.30  # HARDER than oracle's 0.20
    assert HP_LIFT_OVER_RANDOM == 0.30
    assert HP_GAP_ORACLE_OVER_DERIVED == 0.30
    assert HP_NOISY_SANITY_BAND == 0.10
    assert HP_CV_MAX == 0.15
    assert HP_SATURATION_CEIL == 0.95

    # T10: zero LLM calls (substrate-only)
    assert _LLM_CALL_COUNTER[0] == 0

    # T11: cardinality declared
    assert EXPECTED_N_UNITS == 5 * len(SEEDS)

    # T12: anchor binding (single-seed cell)
    assert "substrate_derived_hint" in ANCHOR_NAME and ANCHOR_NAME.endswith("_seed_13")

    # T13: arms-must-differ SHA-256 on tiny per_seed result
    tiny_per_seed = [{
        "arm_a_baseline": r_a,
        "arm_b_substrate_derived": r_b,
        "arm_c_oracle": r_c,
        "arm_d_noisy_hint": r_d,
        "arm_e_random": r_e,
    }]
    hashes_tiny = _arms_must_differ_sha256(tiny_per_seed)
    assert hashes_tiny["arm_a_baseline"] != hashes_tiny["arm_b_substrate_derived"], \
        "META_RULE_AF: A vs B SHA collision in selftest"
    assert hashes_tiny["arm_b_substrate_derived"] != hashes_tiny["arm_e_random"], \
        "META_RULE_AF: B vs E SHA collision in selftest"
    assert hashes_tiny["arm_c_oracle"] != hashes_tiny["arm_e_random"], \
        "META_RULE_AF: C vs E SHA collision in selftest"

    # T14: per-step bounded (monotone-ish; max at or near start)
    psa = r_a["per_step_acc"]
    assert max(psa) >= psa[-1] - 0.5, \
        "per_step should not radically increase: %s" % psa

    print("[selftest] PASS N=%d V_C=%d depth=%d psz=%d arms: a=%.3f b=%.3f "
          "c=%.3f d=%.3f e=%.3f route_acc_b=%.3f xtalk=%.4f HP_band=[%.2f,%.2f] "
          "HP_lift=%.2f HP_gap=%.2f" % (
              N_DIM, V_CONCEPTS, DEPTH, PART_SIZE,
              r_a["top1"], r_b["top1"], r_c["top1"], r_d["top1"], r_e["top1"],
              r_b["route_acc"],
              CROSSTALK_PART, HP_ARM_B_LO, HP_ARM_B_HI,
              HP_LIFT_OVER_BASELINE, HP_GAP_ORACLE_OVER_DERIVED),
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

    # SUBSTRATE-DERIVED partition centroids (the M3-usable composition)
    print("  [seed=%d] building substrate-derived partition centroids "
          "(n_partitions=%d, psz=%d)" % (seed, N_PART, PART_SIZE), flush=True)
    t_cent = time.time()
    C = build_partition_centroids(E, W, PART_SIZE, N_PART)
    print("  [seed=%d] centroids built t=%.1fs shape=%s" % (
        seed, time.time() - t_cent, C.shape), flush=True)

    out: Dict[str, Any] = {
        "seed": seed, "run_mode": RUN_MODE, "N": N_DIM, "V_C": V_CONCEPTS,
        "V_P": V_PRED, "depth": DEPTH,
        "n_chains_train": N_CHAINS_TRAIN, "n_chains_test": N_CHAINS_TEST,
        "n_partitions": N_PART, "part_size": PART_SIZE,
        "crosstalk_baseline": CROSSTALK_BASELINE,
        "crosstalk_part": CROSSTALK_PART,
        "encoder_provenance": ENCODER_PROVENANCE,
        "config_version": CONFIG_VERSION,
        "anchor_name": ANCHOR_NAME,
        "_llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
    }

    # ===== ARM_A: BASELINE =====
    t_arm = time.time()
    r_a = arm_baseline(E, R, sq, W, chains_test, depth=DEPTH)
    r_a["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    out["arm_a_baseline"] = r_a
    rail_ok = (BASELINE_RAIL_LO <= r_a["top1"] <= BASELINE_RAIL_HI)
    out["baseline_rail_ok"] = rail_ok
    print("  [seed=%d] ARM_A BASELINE top1=%.4f rail_ok=%s "
          "(target=%.3f band=[%.3f,%.3f]) per_step=%s t=%.1fs" % (
              seed, r_a["top1"], rail_ok,
              BASELINE_RAIL_TARGET, BASELINE_RAIL_LO, BASELINE_RAIL_HI,
              r_a["per_step_acc"], r_a["elapsed_s_arm"]), flush=True)

    # ===== ARM_B: SUBSTRATE_DERIVED (THE M3-USABLE MECHANISM) =====
    t_arm = time.time()
    r_b = arm_substrate_derived(E, R, sq, W, chains_test, depth=DEPTH,
                                part_size=PART_SIZE, C=C)
    r_b["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    out["arm_b_substrate_derived"] = r_b
    print("  [seed=%d] ARM_B SUBSTRATE_DERIVED top1=%.4f route_acc=%.4f "
          "(HP_band=[%.2f,%.2f] lift_vs_A>=%.2f) per_step=%s t=%.1fs" % (
              seed, r_b["top1"], r_b["route_acc"],
              HP_ARM_B_LO, HP_ARM_B_HI, HP_LIFT_OVER_BASELINE,
              r_b["per_step_acc"], r_b["elapsed_s_arm"]), flush=True)

    # ===== ARM_C: ORACLE (ground-truth; upper bound) =====
    t_arm = time.time()
    r_c = arm_oracle_ground_truth(E, R, sq, W, chains_test, depth=DEPTH,
                                  part_size=PART_SIZE)
    r_c["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    out["arm_c_oracle"] = r_c
    print("  [seed=%d] ARM_C ORACLE top1=%.4f (upper bound; gap_C_B<=%.2f) "
          "per_step=%s t=%.1fs" % (
              seed, r_c["top1"], HP_GAP_ORACLE_OVER_DERIVED,
              r_c["per_step_acc"], r_c["elapsed_s_arm"]), flush=True)

    # ===== ARM_D: NOISY_HINT (negative control) =====
    t_arm = time.time()
    g_d = np.random.default_rng(seed * 7919 + 2)
    r_d = arm_noisy_hint(E, R, sq, W, chains_test, depth=DEPTH,
                         part_size=PART_SIZE, g=g_d)
    r_d["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    out["arm_d_noisy_hint"] = r_d
    print("  [seed=%d] ARM_D NOISY_HINT top1=%.4f (sanity: |D-A|<=%.2f) "
          "per_step=%s t=%.1fs" % (
              seed, r_d["top1"], HP_NOISY_SANITY_BAND,
              r_d["per_step_acc"], r_d["elapsed_s_arm"]), flush=True)

    # ===== ARM_E: RANDOM (floor) =====
    t_arm = time.time()
    g_e = np.random.default_rng(seed * 7919 + 1)
    r_e = arm_random_partition(E, R, sq, W, chains_test, depth=DEPTH,
                               part_size=PART_SIZE, g=g_e)
    r_e["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    out["arm_e_random"] = r_e
    print("  [seed=%d] ARM_E RANDOM top1=%.4f (floor; lift_B_E>=%.2f) "
          "per_step=%s t=%.1fs" % (
              seed, r_e["top1"], HP_LIFT_OVER_RANDOM,
              r_e["per_step_acc"], r_e["elapsed_s_arm"]), flush=True)

    # Lifts + gaps (per-seed)
    out["lift_b_over_a"] = round(r_b["top1"] - r_a["top1"], 4)
    out["lift_b_over_e"] = round(r_b["top1"] - r_e["top1"], 4)
    out["gap_c_over_b"] = round(r_c["top1"] - r_b["top1"], 4)
    out["noisy_sanity_abs"] = round(abs(r_d["top1"] - r_a["top1"]), 4)

    out["elapsed_s"] = round(time.time() - t, 1)
    return out


# ----------------------------------------------------------------------------
# Verdict
# ----------------------------------------------------------------------------

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

    arm_a = mean_top1("arm_a_baseline")
    arm_b = mean_top1("arm_b_substrate_derived")
    arm_c = mean_top1("arm_c_oracle")
    arm_d = mean_top1("arm_d_noisy_hint")
    arm_e = mean_top1("arm_e_random")

    cv_b = cv_top1("arm_b_substrate_derived")

    lift_b_a = arm_b - arm_a if not (math.isnan(arm_b) or math.isnan(arm_a)) \
        else float("nan")
    lift_b_e = arm_b - arm_e if not (math.isnan(arm_b) or math.isnan(arm_e)) \
        else float("nan")
    gap_c_b = arm_c - arm_b if not (math.isnan(arm_c) or math.isnan(arm_b)) \
        else float("nan")
    noisy_sanity = abs(arm_d - arm_a) if not (math.isnan(arm_d) or math.isnan(arm_a)) \
        else float("nan")

    # route_acc for B (diagnostic; not a HP gate but reported)
    route_accs = [p["arm_b_substrate_derived"]["route_acc"]
                  for p in per_seed
                  if "arm_b_substrate_derived" in p
                  and "route_acc" in p["arm_b_substrate_derived"]]
    mean_route_acc = float(np.mean(route_accs)) if route_accs else float("nan")

    # Cardinality (META_RULE_H)
    observed_units = sum(
        1 for p in per_seed for arm_key in (
            "arm_a_baseline", "arm_b_substrate_derived",
            "arm_c_oracle", "arm_d_noisy_hint",
            "arm_e_random")
        if arm_key in p
    )
    cardinality_ok = (observed_units == EXPECTED_N_UNITS)

    # Arms-must-differ SHA-256 (META_RULE_AF)
    arms_hashes = _arms_must_differ_sha256(per_seed)
    # All 5 arms must produce distinct hashes
    unique_hashes = len(set(arms_hashes.values()))
    arms_distinct = (unique_hashes == 5)

    # BIAS-Q saturation check
    saturation_flag = (not math.isnan(arm_b)) and arm_b >= HP_SATURATION_CEIL

    # Baseline rail check (BIAS-S)
    rail_breach = sum(1 for p in per_seed
                      if not p.get("baseline_rail_ok", False))

    # HP-band check
    arm_b_in_band = ((not math.isnan(arm_b))
                     and HP_ARM_B_LO <= arm_b <= HP_ARM_B_HI)
    noisy_sanity_ok = ((not math.isnan(noisy_sanity))
                       and noisy_sanity <= HP_NOISY_SANITY_BAND)
    gap_ok = ((not math.isnan(gap_c_b))
              and gap_c_b <= HP_GAP_ORACLE_OVER_DERIVED)

    summ = (
        "BASELINE_A=%.4f (rail_breach=%d/%d; target=%.3f band=[%.2f,%.2f]) "
        "SUBSTRATE_DERIVED_B=%.4f (cv=%.3f route_acc=%.4f in_band=%s) "
        "ORACLE_C=%.4f NOISY_D=%.4f RANDOM_E=%.4f "
        "lift_B_A=%.4f lift_B_E=%.4f gap_C_B=%.4f (ok=%s) "
        "noisy_sanity=%.4f (ok=%s) cardinality_ok=%s expected_units=%d "
        "observed_units=%d arms_distinct=%s saturation=%s HP_band=[%.2f,%.2f] "
        "HP_lift_base=%.2f depth=%d xtalk=%.4f"
    ) % (
        arm_a, rail_breach, len(per_seed), BASELINE_RAIL_TARGET,
        BASELINE_RAIL_LO, BASELINE_RAIL_HI,
        arm_b, cv_b, mean_route_acc, arm_b_in_band,
        arm_c, arm_d, arm_e,
        lift_b_a, lift_b_e, gap_c_b, gap_ok,
        noisy_sanity, noisy_sanity_ok,
        cardinality_ok, EXPECTED_N_UNITS, observed_units,
        arms_distinct, saturation_flag,
        HP_ARM_B_LO, HP_ARM_B_HI, HP_LIFT_OVER_BASELINE, DEPTH,
        CROSSTALK_PART,
    )

    # Cardinality gate FIRST (META_RULE_H)
    if not cardinality_ok:
        return ("HARD_FAIL_CARDINALITY_BREACH",
                "HARD_FAIL_CARDINALITY_BREACH: " + summ, arms_hashes)

    # Arms-distinct gate (META_RULE_AF)
    if not arms_distinct:
        return ("HARD_FAIL_ARMS_TIED",
                "HARD_FAIL_ARMS_TIED_NO_DISCRIMINATION: " + summ, arms_hashes)

    # HARD_FAIL: mechanism dies
    if (not math.isnan(arm_b)) and arm_b <= HF_ARM_B_ABS:
        return ("HARD_FAIL_NO_SIGNAL_AT_DERIVED",
                "HARD_FAIL_SUBSTRATE_DERIVED_DEAD: " + summ, arms_hashes)

    # HARD_FAIL: lift_b_a below signal floor
    if (not math.isnan(lift_b_a)) and lift_b_a < HF_LIFT_MIN_FOR_SIGNAL:
        return ("HARD_FAIL_NO_SIGNAL_LIFT",
                "HARD_FAIL_NO_REAL_SIGNAL_LIFT_BELOW_FLOOR: " + summ,
                arms_hashes)

    # HARD_FAIL: saturated AND insufficient lift
    if saturation_flag and (not math.isnan(lift_b_a)) \
            and lift_b_a < HF_LIFT_MIN_IF_SATURATED:
        return ("HARD_FAIL_SATURATION_WITHOUT_LIFT",
                "HARD_FAIL_SATURATION_WITH_LIFT_BELOW_THRESHOLD: " + summ,
                arms_hashes)

    # Smoke verdict
    if RUN_MODE == "smoke":
        if arm_b_in_band \
                and (not math.isnan(lift_b_a)) and lift_b_a >= HP_LIFT_OVER_BASELINE \
                and (not math.isnan(lift_b_e)) and lift_b_e >= HP_LIFT_OVER_RANDOM \
                and gap_ok and noisy_sanity_ok and not saturation_flag:
            return ("SMOKE_HARD_PASS",
                    "SMOKE_HARD_PASS_M3_USABLE_SUBSTRATE_DERIVED_MECHANISM: "
                    + summ, arms_hashes)
        # MIDDLE: B in band but missing some gate (lift / gap / noisy)
        if arm_b_in_band and (not math.isnan(lift_b_a)) \
                and lift_b_a >= MM_LIFT_MIN:
            return ("MIDDLE_BAND",
                    "MIDDLE_BAND_PARTIAL_M3_USABLE_MECHANISM: " + summ,
                    arms_hashes)
        return ("HARD_FAIL_LIFT_BELOW_THRESHOLD",
                "HARD_FAIL_LIFT_BELOW_THRESHOLD_AT_DEPTH15: " + summ,
                arms_hashes)

    # Full verdict (per-cell single-seed; cv enforced post-hoc cross-cell)
    if arm_b_in_band \
            and (not math.isnan(lift_b_a)) and lift_b_a >= HP_LIFT_OVER_BASELINE \
            and (not math.isnan(lift_b_e)) and lift_b_e >= HP_LIFT_OVER_RANDOM \
            and gap_ok and noisy_sanity_ok and not saturation_flag:
        return ("HARD_PASS_CELL_GRADE_M3_USABLE_DERIVED_HINT",
                "HARD_PASS_CELL_GRADE_M3_USABLE_SUBSTRATE_DERIVED_BARRIER_1_BREAK_CANDIDATE: "
                + summ, arms_hashes)

    if saturation_flag and (not math.isnan(lift_b_a)) \
            and lift_b_a >= HF_LIFT_MIN_IF_SATURATED:
        return ("MIDDLE_BAND_SATURATED_AUTO_DEMOTE",
                "MIDDLE_BAND_SATURATED_AUTO_DEMOTE_BIAS_Q: " + summ, arms_hashes)

    if (not math.isnan(lift_b_a)) and lift_b_a >= MM_LIFT_MIN:
        return ("MIDDLE_BAND",
                "MIDDLE_BAND_PARTIAL_M3_USABLE_MECHANISM: " + summ, arms_hashes)

    return ("HARD_FAIL_LIFT_BELOW_THRESHOLD",
            "HARD_FAIL_LIFT_BELOW_THRESHOLD_NO_MECHANISM: " + summ, arms_hashes)


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
                                 run_config={"N": N_DIM,
                                             "run_mode": RUN_MODE,
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
            "expected_arms": [
                "baseline_full_V_C", "substrate_derived_centroid",
                "oracle_ground_truth", "noisy_permuted_hint",
                "random_partition_floor"],
            "arms_must_differ_sha256": ahashes,
        }
        write_metrics(od, metrics, results=per_seed)
        print("[atexit] wrote synth metrics.json (%d seeds)" % len(per_seed),
              flush=True)
    except SystemExit:
        raise
    except BaseException as e:  # noqa: BLE001
        print("[atexit] FAIL: %s" % e, flush=True)


atexit.register(_atexit_synth)


if __name__ == "__main__":
    print("[config] anchor=%s mode=%s seeds=%s | %s" % (
        ANCHOR_NAME, RUN_MODE, SEEDS, CONFIG_VERSION), flush=True)
    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)
    _RESULTS_HOLDER["out_dir"] = out_dir

    run_config = {"N": N_DIM, "run_mode": RUN_MODE, "anchor": ANCHOR_NAME}
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print("[ckpt] done=%s remaining=%s" % (done, remaining), flush=True)

    for s in remaining:
        rec = run_seed(s)
        write_partial_key(out_dir, s, rec)

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
        "expected_arms": [
            "baseline_full_V_C", "substrate_derived_centroid",
            "oracle_ground_truth", "noisy_permuted_hint",
            "random_partition_floor"],
        "arms_must_differ_sha256": ahashes,
        "DESIGN_NOTE": (
            "M3-USABLE Barrier 1 break test: replaces ground-truth ORACLE_B "
            "(parent _hardened_v1 cell; gen-time peek) with SUBSTRATE_DERIVED "
            "hint via composition of chain-grade partition-routing primitive "
            "(MEASURED@d:/AI/hd-instrument/data/exp_substrate_partition_routing_10M_full_v2/metrics.json "
            "routed=0.95 route_acc=1.0 @M=1M). Composition: ingest -> "
            "C[p]=normalize(mean(E_part[p] @ W)) [substrate-learned per-partition "
            "centroid in W-output space; no gen-time peek]; query -> "
            "state=W@key; pred_part=argmax(C @ state); cleanup over "
            "E_part[pred_part]. ARMS (5; all psz=800/5 partitions): A=BASELINE "
            "(no hint), B=SUBSTRATE_DERIVED (M3-usable), C=ORACLE (ground-truth "
            "upper bound), D=NOISY_HINT (random-permuted labels; negative "
            "control), E=RANDOM (floor). HP requires B in [0.50, 0.95] AND "
            "lift_B_A >= 0.30 (HARDER than parent's 0.20 to gate REAL "
            "substrate signal) AND lift_B_E >= 0.30 AND gap_C_B <= 0.30 "
            "(substrate retains most of oracle's lift) AND |D-A| <= 0.10 "
            "(noisy sanity) AND saturation == False AND arms_distinct. "
            "META_RULE_AC/AE/AF/AG/AH/AL/AN/H all enforced; BIAS-Q/N/S; "
            "functional_requirement_first per USER 2026-06-28; DISCRIMINATOR-"
            "MUST-SURVIVE-SCALE (smoke at FULL N + FULL depth). Source: "
            "d:/AI/hd-instrument/data/exp_substrate_multihop_partition_oracle_v5_hardened_v1_smoke/metrics.json "
            "(BASELINE=0.39 ORACLE_B=0.90 lift=0.51 unsat). CHUNKED single-"
            "seed (seed_13); siblings: seed_7 + seed_19. cv enforced post-hoc "
            "cross-cell at chain-grade VET tier."
        ),
    }
    write_metrics(out_dir, metrics, results=per_seed)
    print("[done] metrics.json written (%d seeds, %.1fs)" % (
        len(per_seed), metrics["elapsed_s"]), flush=True)
