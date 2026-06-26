"""gap1_partition_routing_bidirectional_collide_and_fly_lsh_v1_META_M7.

Tests USER's steelman: can substrate ROUTE to correct partition WITHOUT oracle?

Cell B v2 PART_ORACLE_5HOP=0.9550 cleared chain-grade BUT used
    target_part = target_o // part_sz    # ORACLE
This carries BIAS-P scope flag. USER asked: "why can't we use bidirectional to
tell us where it is for the 1st method?" Research drilled 5 mechanism classes
across info theory, hippocampal CA3, pulvinar, mushroom body, learned routers.
USER's steelman ranked #1; fly-LSH ranked #2.

This cell BUNDLES anchors 1+2 (sharing _forward_state / _backward_state /
fly_lsh_expand infrastructure from Cell B v2 + Cell C v2).

Anchor 1 (USER steelman) = ARM_PART_BIDIR_COLLIDE_5HOP:
    For each partition p:
        score_p = sum_{Z in part_p} state_fwd . _backward_state(E[Z], preds[mid:])
    predicted_part = argmax_p score_p
    Then argmax within winning partition.

Anchor 2 (cheap-decisive) = ARM_PART_FLY_LSH_5HOP:
    E_lsh[i] = fly_lsh_expand(E[i]); c_lsh_p = mean(E_lsh[i] : i in part_p)
    state_fwd_lsh = fly_lsh_expand(state_fwd)
    predicted_part = argmax_p (state_fwd_lsh . c_lsh_p)
    Then argmax within winning partition (E_lsh @ W_v1_regime cleanup).

Falsification anchor (Research recommended) = ARM_PART_NAIVE_CENTROID_5HOP:
    centroid_p = mean(E[i] : i in part_p)
    predicted_part = argmax_p (state_fwd . centroid_p)
    Cell C v2 measured mean_midpoint_cosine=0.0000 -> this arm should FAIL.

ARMS (7):
  ARM_BASELINE_HRR_2HOP             beta-sweep sanity rail [0.62, 0.68]
  ARM_REPRODUCE_POINTER_CHAIN_V2_5HOP  pointer-v2 regime W; verbatim [0.08, 0.25]
  ARM_SINGLE_TOP1_5HOP              v1 1000-binding-W monolithic 5hop (info rail)
  ARM_PART_ORACLE_5HOP              CROSS-CELL SANITY: Cell B v2 PART=0.9550 +/- 0.02
  ARM_PART_BIDIR_COLLIDE_5HOP       USER steelman; ORACLE-FREE; [0.80, 1.00] HARD_PASS
  ARM_PART_FLY_LSH_5HOP             Anchor 2; ORACLE-FREE; [0.80, 1.00] HARD_PASS
  ARM_PART_NAIVE_CENTROID_5HOP      Falsification: expected <= 0.40

SACRED SANITY rails:
  RAIL_BASELINE: BASELINE NOT in [0.62, 0.68] -> SANITY_BREACH
  RAIL_META_M7: REPRODUCE NOT in [0.08, 0.25] -> META_M7_RAIL_VIOLATION
  RAIL_CROSS_CELL_PART_ORACLE: PART_ORACLE drifts > 0.02 from 0.9550 -> CROSS_CELL_DRIFT flag

PROSPECTIVE BANDS (locked at module-init assert):
  HP_ROUTER >= 0.80
  HF_ROUTER <= 0.50
  HP_CV_MAX <= 0.07

ASCII-only; per-seed checkpoint; atexit synthesizer; zero LLM forward calls.
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
    write_metrics
)

ANCHOR_NAME = "gap1_partition_routing_bidirectional_collide_and_fly_lsh_v1_META_M7"
_LLM_CALL_COUNTER = [0]

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true", dest="self_test")
_ARGS, _ = _ap.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = ("smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE)
            else os.environ.get("HDLAB_RUN_MODE", "full").lower())

# HARD bands (LOCKED prospectively)
HP_ROUTER = 0.80          # bidir-collide AND fly-LSH each must clear this
HP_CV_MAX = 0.07
HF_ROUTER = 0.50          # both routers below this -> Gap 1 BIAS-P stands

# SACRED SANITY rails
BASELINE_SANITY_LO = 0.62
BASELINE_SANITY_HI = 0.68

# META_M7 rail
META_M7_RAIL_LO = 0.08
META_M7_RAIL_HI = 0.25

# Cross-cell PART_ORACLE rail (Cell B v2 mean = 0.9550)
CROSS_CELL_PART_ORACLE_TARGET = 0.9550
CROSS_CELL_PART_ORACLE_TOL = 0.02

# Regime constants
BASELINE_V_P = 2
BASELINE_N_CHAINS = 200
POINTER_V_P = 10
POINTER_K_SET = 20

# POINTER-V2 regime (META_M7 rail)
POINTER_V2_N_CHAINS = 200
POINTER_V2_MAX_DEPTH = 10

# Partition / fly-LSH primitives (mirror Cell B v2)
N_PARTITIONS = 20
N_LSH_EXPANSIONS = 5
LSH_TOPK = 20

# META_PROSPECTIVE_BANDS_FRESH_SEEDS lock
assert HP_ROUTER > HF_ROUTER, "HP > HF"
assert 0.0 < HP_CV_MAX < 0.20
assert META_M7_RAIL_LO < META_M7_RAIL_HI < HF_ROUTER, \
    "META_M7 must be below HF_ROUTER (pointer-v2 regime is genuinely harder)"
assert BASELINE_SANITY_LO < BASELINE_SANITY_HI
assert 0.90 < CROSS_CELL_PART_ORACLE_TARGET < 1.0
assert 0.0 < CROSS_CELL_PART_ORACLE_TOL < 0.10

if RUN_MODE == "smoke":
    N_DIM = 2048
    V_CONCEPTS = 200
    SEEDS = [7]
    POINTER_N_CHAINS = 50
    POINTER_V2_N_CHAINS_LOCAL = 100  # smoke keeps depth=10 to preserve crosstalk regime
    BASELINE_N_CHAINS_LOCAL = BASELINE_N_CHAINS
else:
    N_DIM = 8192
    V_CONCEPTS = 200
    SEEDS = [7, 17, 23]
    POINTER_N_CHAINS = 200
    POINTER_V2_N_CHAINS_LOCAL = POINTER_V2_N_CHAINS  # 2000 bindings
    BASELINE_N_CHAINS_LOCAL = BASELINE_N_CHAINS

DEPTH = 5
n_predicates = max(BASELINE_V_P, POINTER_V_P)

assert V_CONCEPTS % N_PARTITIONS == 0, \
    "V_CONCEPTS=%d must divide N_PARTITIONS=%d" % (V_CONCEPTS, N_PARTITIONS)
PART_SIZE = V_CONCEPTS // N_PARTITIONS

CONFIG_VERSION = (
    "gap1PartitionRoutingBidirCollideFlyLshV1MetaM7: N=%d V_C=%d "
    "BASELINE_V_P=%d BASELINE_N=%d POINTER_V_P=%d POINTER_N=%d K_SET=%d "
    "POINTER_V2_N=%d POINTER_V2_DEPTH=%d "
    "N_PARTS=%d PART_SIZE=%d N_LSH=%d LSH_TOPK=%d "
    "seeds=%s mode=%s depth=%d midhop=%d "
    "HP_router>=%.2f HP_cv<=%.2f HF<%.2f "
    "META_M7=[%.2f,%.2f] cross_cell_part_oracle=%.4f+/-%.2f "
    "baseline_sanity=[%.2f,%.2f]"
) % (
    N_DIM, V_CONCEPTS, BASELINE_V_P, BASELINE_N_CHAINS_LOCAL,
    POINTER_V_P, POINTER_N_CHAINS, POINTER_K_SET,
    POINTER_V2_N_CHAINS_LOCAL, POINTER_V2_MAX_DEPTH,
    N_PARTITIONS, PART_SIZE, N_LSH_EXPANSIONS, LSH_TOPK,
    SEEDS, RUN_MODE, DEPTH, DEPTH // 2,
    HP_ROUTER, HP_CV_MAX, HF_ROUTER,
    META_M7_RAIL_LO, META_M7_RAIL_HI,
    CROSS_CELL_PART_ORACLE_TARGET, CROSS_CELL_PART_ORACLE_TOL,
    BASELINE_SANITY_LO, BASELINE_SANITY_HI,
)


# ---- substrate primitives (verbatim ports from Cell B v2 + Cell C v2) ----

def bipolar(M: int, n: int, g) -> np.ndarray:
    X = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)


def ingest_hebbian(triples, E, R, sq, n_dim, batch=2000) -> np.ndarray:
    if not triples:
        return np.zeros((n_dim, n_dim), dtype=np.float32)
    tr = np.asarray(triples, dtype=np.int64)
    s_idx, p_idx, o_idx = tr[:, 0], tr[:, 1], tr[:, 2]
    W = np.zeros((n_dim, n_dim), dtype=np.float32)
    for b in range(0, len(tr), batch):
        ks = (E[s_idx[b:b + batch]] * R[p_idx[b:b + batch]] * sq).astype(np.float32)
        W += (E[o_idx[b:b + batch]].T @ ks) / n_dim
    return W


def make_two_hop_chains_betasweep(n_chains: int, V: int, g, p1: int = 0, p2: int = 1):
    train: List[Tuple[int, int, int]] = []
    queries: List[Tuple[int, int, int, int, int]] = []
    used_s: set = set()
    tries = 0
    while len(queries) < n_chains and tries < n_chains * 100:
        tries += 1
        s = int(g.integers(0, V))
        if s in used_s:
            continue
        x = int(g.integers(0, V))
        while x == s:
            x = int(g.integers(0, V))
        o = int(g.integers(0, V))
        while o == s or o == x:
            o = int(g.integers(0, V))
        train.append((s, p1, x))
        train.append((x, p2, o))
        queries.append((s, p1, p2, o, x))
        used_s.add(s)
    return train, queries


def chain_naive_hard(W, E, R, sq, start: int, relations: List[int]) -> int:
    state = E[start].copy()
    last = start
    for p in relations:
        state = W @ (state * R[p] * sq)
        last = int((E @ state).argmax())
    return last


def arm_baseline_hrr_2hop_betasweep(E, R, sq, train_triples, queries):
    n_dim = E.shape[1]
    W = ingest_hebbian(train_triples, E, R, sq, n_dim)
    hits = 0
    for q in queries:
        s, p1, p2, o_true, _x = q
        pred = chain_naive_hard(W, E, R, sq, s, [p1, p2])
        if pred == o_true:
            hits += 1
    return {"top1": round(hits / max(len(queries), 1), 4),
            "n_queries": len(queries), "mechanism": "beta_sweep_naive_hard"}


def make_deep_chains(n_chains: int, V: int, P: int, max_depth: int,
                      g, disallow_s: set):
    all_triples = []
    chain_queries = []
    used_s = set(disallow_s)
    tries = 0
    while len(chain_queries) < n_chains and tries < n_chains * 200:
        tries += 1
        nodes = []
        s = int(g.integers(0, V))
        if s in used_s:
            continue
        nodes.append(s)
        for _ in range(max_depth):
            cand = int(g.integers(0, V))
            while cand in nodes:
                cand = int(g.integers(0, V))
            nodes.append(cand)
        chain = []
        for i in range(max_depth):
            p = int(g.integers(0, P))
            chain.append((nodes[i], p, nodes[i + 1]))
        all_triples.extend(chain)
        chain_queries.append(chain)
        used_s.add(s)
    if len(chain_queries) < n_chains:
        raise RuntimeError("BLOCKING make_deep_chains: only %d/%d" % (len(chain_queries), n_chains))
    return all_triples, chain_queries


def _retrieve_1hop(E, W, R, s: int, p: int, sq: float) -> int:
    """VERBATIM port of pointer-chain v2 / Cell B v2 / Cell C v2 cleanup primitive."""
    key = (E[s] * R[p] * sq).astype(np.float32)
    return int((E @ (W @ key)).argmax())


def arm_single_chain_naive(E, R, sq, W, chains_test, depth: int) -> Dict[str, Any]:
    n = len(chains_test)
    hits = 0
    per_step_hits = np.zeros(depth, dtype=np.int64)
    for chain in chains_test:
        s = chain[0][0]
        for i in range(depth):
            p = chain[i][1]
            s_pred = _retrieve_1hop(E, W, R, s, p, sq)
            if s_pred == chain[i][2]:
                per_step_hits[i] += 1
            s = s_pred
        if s == chain[depth - 1][2]:
            hits += 1
    per_step_acc = (per_step_hits.astype(np.float32) / max(n, 1)).tolist()
    return {"top1": round(hits / max(n, 1), 4),
            "per_step_acc": [round(x, 4) for x in per_step_acc],
            "n_queries": n, "depth": depth}


# ---- forward / backward state walkers (verbatim Cell C v2) ----

def _forward_state(E, W, R, sq, start_idx: int, predicates: List[int]) -> np.ndarray:
    state = E[start_idx].copy()
    for p in predicates:
        state = W @ (state * R[p] * sq)
    return state


def _backward_state(E, W, R, sq, end_idx: int, predicates: List[int]) -> np.ndarray:
    """Walk backward from E[end_idx] through predicates in REVERSE order."""
    state = E[end_idx].copy()
    for i in range(len(predicates) - 1, -1, -1):
        p = predicates[i]
        state = W.T @ state
        state = state * R[p] * sq
    return state


# ---- fly-LSH (verbatim Cell B v2) ----

def build_fly_lsh_projs(n_dim: int, n_expansions: int, g) -> np.ndarray:
    projs = np.zeros((n_expansions, n_dim, n_dim), dtype=np.float32)
    for k in range(n_expansions):
        rows = g.integers(0, n_dim, size=(n_dim, LSH_TOPK))
        signs = (g.integers(0, 2, size=(n_dim, LSH_TOPK)) * 2 - 1).astype(np.float32)
        for i in range(n_dim):
            projs[k, i, rows[i]] += signs[i]
    return projs


def fly_lsh_expand(key: np.ndarray, projs: np.ndarray) -> np.ndarray:
    out = np.zeros_like(key)
    n_dim = key.shape[0]
    for k in range(projs.shape[0]):
        z = projs[k] @ key
        if LSH_TOPK < n_dim:
            thr_idx = np.argpartition(np.abs(z), -LSH_TOPK)[-LSH_TOPK:]
            mask = np.zeros_like(z)
            mask[thr_idx] = 1.0
            z = z * mask
        out += z
    norm = np.linalg.norm(out) + 1e-8
    return out / norm


# ---- ARM: PART_ORACLE (cross-cell sanity reproduction of Cell B v2) ----

def arm_part_oracle(E, R, sq, triples, chains_test, depth: int,
                    n_partitions: int = N_PARTITIONS) -> Dict[str, Any]:
    """Cell B v2 PART_ORACLE_5HOP verbatim: target_part = target_o // part_sz.

    This is the CROSS-CELL SANITY RAIL. Must reproduce Cell B v2 0.9550 +/- 0.02.
    """
    n_dim = E.shape[1]
    V = E.shape[0]
    assert V % n_partitions == 0
    part_sz = V // n_partitions
    W = ingest_hebbian(triples, E, R, sq, n_dim)
    E_parts = [E[p * part_sz:(p + 1) * part_sz] for p in range(n_partitions)]
    part_offsets = [p * part_sz for p in range(n_partitions)]
    n = len(chains_test)
    hits = 0
    per_step_hits = np.zeros(depth, dtype=np.int64)
    routing_correct = np.zeros(depth, dtype=np.int64)
    total_routing_calls = 0
    for chain in chains_test:
        s = chain[0][0]
        for i in range(depth):
            p = chain[i][1]
            target_o = chain[i][2]
            target_part = target_o // part_sz  # ORACLE
            routing_correct[i] += 1  # by construction
            total_routing_calls += 1
            key = (E[s] * R[p] * sq).astype(np.float32)
            scores = E_parts[target_part] @ (W @ key)
            local_idx = int(scores.argmax())
            s_pred = part_offsets[target_part] + local_idx
            if s_pred == target_o:
                per_step_hits[i] += 1
            s = s_pred
        if s == chain[depth - 1][2]:
            hits += 1
    per_step_acc = (per_step_hits.astype(np.float32) / max(n, 1)).tolist()
    routing_acc = (routing_correct.astype(np.float32) / max(total_routing_calls // depth, 1)).tolist()
    return {"top1": round(hits / max(n, 1), 4),
            "per_step_acc": [round(x, 4) for x in per_step_acc],
            "routing_acc_per_hop": [round(x, 4) for x in routing_acc],
            "n_queries": n, "depth": depth, "n_partitions": n_partitions,
            "mechanism": "partition_per_hop_oracle_routed_cross_cell_sanity",
            "W_n_bindings": len(triples)}


# ---- ARM: PART_BIDIR_COLLIDE (USER's steelman; Anchor 1) ----

def arm_part_bidir_collide(E, R, sq, W, chains_test, depth: int,
                            n_partitions: int = N_PARTITIONS) -> Dict[str, Any]:
    """USER STEELMAN: MEET-IN-MIDDLE bidirectional partition routing.

    Architecture (chain-monolithic, matches USER's literal intuition + Research formula):
        S = chain[0][0]; preds = [chain[i][1] for i in range(depth)]
        mid = depth // 2
        state_fwd_mid = _forward_state(S, preds[:mid])   # forward through mid hops
        For each candidate chain-endpoint Z in V_C:
            state_bwd_Z = _backward_state(E[Z], preds[mid:])  # backward (depth-mid) hops
            cos_Z = state_fwd_mid . state_bwd_Z
        For each partition p:
            score_p = sum_{Z in p} cos_Z
        predicted_endpoint_part = argmax_p score_p
        # Then standard cleanup within winning partition for the chain endpoint:
        scores_within = E_parts[predicted_endpoint_part] @ state_fwd_full
        local_idx = argmax(scores_within)
        predicted_Z = part_offset[predicted_endpoint_part] + local_idx

    Interpretation: substrate has NO ORACLE. It picks the chain endpoint partition by
    bidirectional collision at the midpoint -- forward walk through first mid hops meets
    backward-walks-from-each-candidate-endpoint through last (depth-mid) hops. The
    nonlinear backward-walk through MULTIPLE predicates gives this signal genuine
    discriminative power vs forward-only (Cell C v2 measured 0.62 lift on this signal).

    top1 = fraction of chains where predicted endpoint == chain[depth-1][2].
    routing_acc = fraction of chains where predicted_endpoint_part == true_endpoint_part.
    This is COMPARABLE to Cell C v2 BIDIR_MEET_MID (which scored full-V_C) but with
    partition-routed cleanup at the end.

    BIAS-P removal: chain endpoint Z is predicted WITHOUT using chain[depth-1][2] as
    input; routing is bidirectional-collide; cleanup is within-partition argmax.

    NO ORACLE. Uses _forward_state + _backward_state from Cell C v2.
    """
    n_dim = E.shape[1]
    V = E.shape[0]
    assert V % n_partitions == 0
    part_sz = V // n_partitions
    E_parts = [E[p * part_sz:(p + 1) * part_sz] for p in range(n_partitions)]
    part_offsets = [p * part_sz for p in range(n_partitions)]

    n = len(chains_test)
    hits = 0
    routing_correct_count = 0

    mid = depth // 2

    for chain in chains_test:
        S = chain[0][0]
        preds = [chain[i][1] for i in range(depth)]
        true_endpoint = chain[depth - 1][2]
        true_endpoint_part = true_endpoint // part_sz

        # Forward walk through first mid hops
        state_fwd_mid = _forward_state(E, W, R, sq, S, preds[:mid])
        # Forward walk through ALL hops (used for within-partition cleanup at end)
        state_fwd_full = _forward_state(E, W, R, sq, S, preds)

        # Backward-walk ALL candidate endpoints Z through last (depth-mid) preds.
        # Batched: for each Z in 0..V-1, compute _backward_state(Z, preds[mid:]).
        # We do this manually with batched numpy.
        # Start: state[Z] = E[Z]   shape (V, n_dim)
        bwd = E.copy()  # (V, n_dim)
        # For each remaining pred in REVERSE order:
        remaining = preds[mid:]
        for j in range(len(remaining) - 1, -1, -1):
            p_j = remaining[j]
            # bwd_new[Z] = W.T @ bwd[Z]    -> batched: bwd @ W
            bwd = bwd @ W
            # bwd_new[Z] = bwd_new[Z] * R[p_j] * sq
            bwd = bwd * (R[p_j] * sq)

        # Collide forward midpoint with each candidate backward state
        cos_per_Z = bwd @ state_fwd_mid  # (V,)

        # Partition score = sum over Z in partition
        scores = np.array([cos_per_Z[pp * part_sz:(pp + 1) * part_sz].sum()
                           for pp in range(n_partitions)], dtype=np.float32)
        predicted_endpoint_part = int(scores.argmax())
        if predicted_endpoint_part == true_endpoint_part:
            routing_correct_count += 1

        # Within winning partition: argmax cleanup against state_fwd_full
        scores_within = E_parts[predicted_endpoint_part] @ state_fwd_full
        local_idx = int(scores_within.argmax())
        predicted_endpoint = part_offsets[predicted_endpoint_part] + local_idx
        if predicted_endpoint == true_endpoint:
            hits += 1

    routing_acc = routing_correct_count / max(n, 1)
    return {"top1": round(hits / max(n, 1), 4),
            "endpoint_routing_acc": round(routing_acc, 4),
            "n_queries": n, "depth": depth, "n_partitions": n_partitions,
            "midpoint_hop": mid,
            "mechanism": "partition_meet_in_middle_bidirectional_collide_chain_endpoint_router_oracle_free"}


# ---- ARM: PART_FLY_LSH (Anchor 2) ----

def arm_part_fly_lsh(E, R, sq, W, chains_test, depth: int, projs: np.ndarray,
                       n_partitions: int = N_PARTITIONS) -> Dict[str, Any]:
    """fly-LSH chain-endpoint router (apples-to-apples vs bidir-collide).

    Architecture:
        state_fwd_full = _forward_state(S, all preds)
        state_lsh = fly_lsh_expand(state_fwd_full, projs)
        c_lsh_p = sum_{Z in p} fly_lsh_expand(E[Z]) (normalized)
        predicted_endpoint_part = argmax_p (state_lsh . c_lsh_p)
        scores_within = E_parts[predicted_endpoint_part] @ state_fwd_full
        predicted_endpoint = part_offsets[predicted_endpoint_part] + argmax(scores_within)

    Substrate-native sparse-projection router. NO ORACLE. Uses fly_lsh_expand from Cell B v2.
    """
    n_dim = E.shape[1]
    V = E.shape[0]
    assert V % n_partitions == 0
    part_sz = V // n_partitions

    # Build E_lsh and lsh centroids per partition (one-time per seed)
    E_lsh = np.zeros_like(E)
    for i in range(V):
        E_lsh[i] = fly_lsh_expand(E[i], projs)
    c_lsh_parts = np.zeros((n_partitions, n_dim), dtype=np.float32)
    for pp in range(n_partitions):
        seg = E_lsh[pp * part_sz:(pp + 1) * part_sz].sum(axis=0)
        cn = np.linalg.norm(seg) + 1e-8
        c_lsh_parts[pp] = seg / cn

    E_parts = [E[p * part_sz:(p + 1) * part_sz] for p in range(n_partitions)]
    part_offsets = [p * part_sz for p in range(n_partitions)]

    n = len(chains_test)
    hits = 0
    routing_correct_count = 0

    for chain in chains_test:
        S = chain[0][0]
        preds = [chain[i][1] for i in range(depth)]
        true_endpoint = chain[depth - 1][2]
        true_endpoint_part = true_endpoint // part_sz

        state_fwd_full = _forward_state(E, W, R, sq, S, preds)
        state_lsh = fly_lsh_expand(state_fwd_full, projs)
        scores = c_lsh_parts @ state_lsh
        predicted_endpoint_part = int(scores.argmax())
        if predicted_endpoint_part == true_endpoint_part:
            routing_correct_count += 1

        scores_within = E_parts[predicted_endpoint_part] @ state_fwd_full
        local_idx = int(scores_within.argmax())
        predicted_endpoint = part_offsets[predicted_endpoint_part] + local_idx
        if predicted_endpoint == true_endpoint:
            hits += 1

    routing_acc = routing_correct_count / max(n, 1)
    return {"top1": round(hits / max(n, 1), 4),
            "endpoint_routing_acc": round(routing_acc, 4),
            "n_queries": n, "depth": depth, "n_partitions": n_partitions,
            "mechanism": "partition_chain_endpoint_fly_lsh_router_oracle_free"}


# ---- ARM: PART_NAIVE_CENTROID (falsification) ----

def arm_part_naive_centroid(E, R, sq, W, chains_test, depth: int,
                              n_partitions: int = N_PARTITIONS) -> Dict[str, Any]:
    """Naive centroid chain-endpoint router (FALSIFICATION ANCHOR).

    Architecture (apples-to-apples vs bidir-collide + fly-LSH):
        state_fwd_full = _forward_state(S, all preds)
        centroid_p = mean(E[Z] : Z in part_p), normalized
        predicted_endpoint_part = argmax_p (state_fwd_full . centroid_p)
        within-partition argmax cleanup gives predicted endpoint

    Cell C v2 PROBE measured mean_midpoint_cosine=0.0000 -> this arm expected FAIL.
    If instead this arm PASSES, Cell C v2 probe was misleading and the whole
    bidir-collide premise needs re-examination.
    """
    n_dim = E.shape[1]
    V = E.shape[0]
    assert V % n_partitions == 0
    part_sz = V // n_partitions
    E_parts = [E[p * part_sz:(p + 1) * part_sz] for p in range(n_partitions)]
    part_offsets = [p * part_sz for p in range(n_partitions)]

    # Centroids: mean of E within partition; normalized
    centroids = np.zeros((n_partitions, n_dim), dtype=np.float32)
    for pp in range(n_partitions):
        seg = E_parts[pp].sum(axis=0)
        cn = np.linalg.norm(seg) + 1e-8
        centroids[pp] = seg / cn

    n = len(chains_test)
    hits = 0
    routing_correct_count = 0

    for chain in chains_test:
        S = chain[0][0]
        preds = [chain[i][1] for i in range(depth)]
        true_endpoint = chain[depth - 1][2]
        true_endpoint_part = true_endpoint // part_sz

        state_fwd_full = _forward_state(E, W, R, sq, S, preds)
        scores = centroids @ state_fwd_full
        predicted_endpoint_part = int(scores.argmax())
        if predicted_endpoint_part == true_endpoint_part:
            routing_correct_count += 1

        scores_within = E_parts[predicted_endpoint_part] @ state_fwd_full
        local_idx = int(scores_within.argmax())
        predicted_endpoint = part_offsets[predicted_endpoint_part] + local_idx
        if predicted_endpoint == true_endpoint:
            hits += 1

    routing_acc = routing_correct_count / max(n, 1)
    return {"top1": round(hits / max(n, 1), 4),
            "endpoint_routing_acc": round(routing_acc, 4),
            "n_queries": n, "depth": depth, "n_partitions": n_partitions,
            "mechanism": "partition_chain_endpoint_naive_centroid_falsification_anchor"}


# ---- self-test ----

def _selftest() -> None:
    g = np.random.default_rng(0)
    n = 512
    V = 40
    sq = math.sqrt(n)
    E = bipolar(V, n, g)
    R = bipolar(max(BASELINE_V_P, POINTER_V_P), n, g)

    # T1: BASELINE arm
    Rb = bipolar(max(BASELINE_V_P, 2), n, g)
    train, queries = make_two_hop_chains_betasweep(20, V, g, p1=0, p2=1)
    r_base = arm_baseline_hrr_2hop_betasweep(E, Rb, sq, train, queries)
    assert 0.0 <= r_base["top1"] <= 1.0

    # T2: REPRODUCE arm
    triples_v2, chains_v2 = make_deep_chains(8, V, 4, max_depth=10, g=g, disallow_s=set())
    W_v2 = ingest_hebbian(triples_v2, E, R, sq, n)
    chains_v2_test = [c[:5] for c in chains_v2]
    r_reproduce = arm_single_chain_naive(E, R, sq, W_v2, chains_v2_test, depth=5)
    assert 0.0 <= r_reproduce["top1"] <= 1.0

    # T3: SINGLE arm (v1 regime)
    triples_v1, chains_v1 = make_deep_chains(8, V, 4, max_depth=5, g=g, disallow_s=set())
    W_v1 = ingest_hebbian(triples_v1, E, R, sq, n)
    r_single = arm_single_chain_naive(E, R, sq, W_v1, chains_v1, depth=5)
    assert 0.0 <= r_single["top1"] <= 1.0

    # T4: PART_ORACLE -- byte-equivalent per-hop math to Cell B v2 (one query check)
    r_oracle = arm_part_oracle(E, R, sq, triples_v1, chains_v1, depth=5, n_partitions=4)
    assert 0.0 <= r_oracle["top1"] <= 1.0
    # Routing acc must be 1.0 per hop (oracle by construction)
    for ra in r_oracle["routing_acc_per_hop"]:
        assert ra == 1.0, "PART_ORACLE routing_acc must be 1.0 by construction; got %s" % ra

    # T5: PART_BIDIR_COLLIDE
    r_bidir = arm_part_bidir_collide(E, R, sq, W_v1, chains_v1, depth=5, n_partitions=4)
    assert 0.0 <= r_bidir["top1"] <= 1.0

    # T6: PART_FLY_LSH
    projs = build_fly_lsh_projs(n, 2, g)
    r_lsh = arm_part_fly_lsh(E, R, sq, W_v1, chains_v1, depth=5, projs=projs, n_partitions=4)
    assert 0.0 <= r_lsh["top1"] <= 1.0

    # T7: PART_NAIVE_CENTROID
    r_naive = arm_part_naive_centroid(E, R, sq, W_v1, chains_v1, depth=5, n_partitions=4)
    assert 0.0 <= r_naive["top1"] <= 1.0

    # T8: bands locked
    assert HP_ROUTER == 0.80 and HF_ROUTER == 0.50 and HP_CV_MAX == 0.07
    assert META_M7_RAIL_LO == 0.08 and META_M7_RAIL_HI == 0.25
    assert CROSS_CELL_PART_ORACLE_TARGET == 0.9550 and CROSS_CELL_PART_ORACLE_TOL == 0.02

    # T9: LLM call counter == 0 (substrate-only)
    assert _LLM_CALL_COUNTER[0] == 0

    # Backward walk math sanity (from Cell C v2)
    g2 = np.random.default_rng(1)
    E1 = bipolar(V, n, g2)
    R1 = bipolar(4, n, g2)
    triple_1hop = [(0, 0, 1)]
    W1 = ingest_hebbian(triple_1hop, E1, R1, sq, n)
    fwd_state = W1 @ (E1[0] * R1[0] * sq)
    fwd_cos = float(np.dot(fwd_state, E1[1]) /
                    (np.linalg.norm(fwd_state) * np.linalg.norm(E1[1]) + 1e-8))
    bwd_state = (W1.T @ E1[1]) * R1[0] * sq
    bwd_cos = float(np.dot(bwd_state, E1[0]) /
                    (np.linalg.norm(bwd_state) * np.linalg.norm(E1[0]) + 1e-8))
    assert fwd_cos > 0.2, "selftest forward-cos=%.3f too low" % fwd_cos
    assert bwd_cos > 0.2, "selftest backward-cos=%.3f too low" % bwd_cos

    print("[selftest] PASS base=%.3f reproduce=%.3f single=%.3f oracle=%.3f "
          "bidir=%.3f lsh=%.3f naive=%.3f fwd_cos=%.3f bwd_cos=%.3f"
          % (r_base["top1"], r_reproduce["top1"], r_single["top1"], r_oracle["top1"],
             r_bidir["top1"], r_lsh["top1"], r_naive["top1"], fwd_cos, bwd_cos),
          flush=True)


_selftest()
if _ARGS.self_test:
    print("[self-test] PASS; exiting", flush=True)
    sys.exit(0)


# ---- run_seed ----

def run_seed(seed: int) -> Dict[str, Any]:
    t = time.time()
    g = np.random.default_rng(seed)
    sq = math.sqrt(N_DIM)
    E = bipolar(V_CONCEPTS, N_DIM, g)
    R = bipolar(n_predicates, N_DIM, g)

    out = {
        "seed": seed, "run_mode": RUN_MODE, "N": N_DIM, "V_C": V_CONCEPTS,
        "n_predicates": n_predicates,
        "n_partitions": N_PARTITIONS, "part_size": PART_SIZE,
        "n_lsh_expansions": N_LSH_EXPANSIONS, "lsh_topk": LSH_TOPK,
        "pointer_n_chains": POINTER_N_CHAINS,
        "pointer_v2_n_chains": POINTER_V2_N_CHAINS_LOCAL,
        "pointer_v2_max_depth": POINTER_V2_MAX_DEPTH,
        "depth": DEPTH, "midpoint_hop": DEPTH // 2,
        "config_version": CONFIG_VERSION,
        "_llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
    }

    # ===== BASELINE =====
    t_arm = time.time()
    base_triples, base_queries = make_two_hop_chains_betasweep(
        BASELINE_N_CHAINS_LOCAL, V_CONCEPTS, g, p1=0, p2=1)
    r_baseline = arm_baseline_hrr_2hop_betasweep(E, R, sq, base_triples, base_queries)
    r_baseline["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    out["arm_baseline_hrr_2hop"] = r_baseline
    print("  [seed=%d] BASELINE top1=%.4f t=%.1fs" % (
        seed, r_baseline["top1"], r_baseline["elapsed_s_arm"]), flush=True)
    baseline_ok = (BASELINE_SANITY_LO <= r_baseline["top1"] <= BASELINE_SANITY_HI)
    out["baseline_sanity_ok"] = baseline_ok

    # ===== META_M7 ARM: REPRODUCE POINTER-CHAIN-V2 =====
    t_arm = time.time()
    ptr_v2_triples, ptr_v2_chains = make_deep_chains(
        POINTER_V2_N_CHAINS_LOCAL, V_CONCEPTS, POINTER_V_P,
        max_depth=POINTER_V2_MAX_DEPTH, g=g, disallow_s=set())
    W_pointer_v2 = ingest_hebbian(ptr_v2_triples, E, R, sq, N_DIM)
    print("  [seed=%d] META_M7 W built (%d triples; v2 regime depth=%d) t=%.1fs" % (
        seed, len(ptr_v2_triples), POINTER_V2_MAX_DEPTH,
        round(time.time() - t_arm, 2)), flush=True)
    t_arm = time.time()
    ptr_v2_chains_test = [c[:DEPTH] for c in ptr_v2_chains]
    r_reproduce = arm_single_chain_naive(E, R, sq, W_pointer_v2,
                                            ptr_v2_chains_test, depth=DEPTH)
    r_reproduce["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    r_reproduce["mechanism"] = "verbatim_pointer_chain_v2_at_2000_bindings"
    r_reproduce["W_n_bindings"] = len(ptr_v2_triples)
    out["arm_reproduce_pointer_chain_v2_5hop"] = r_reproduce
    print("  [seed=%d] REPRODUCE_POINTER_CHAIN_V2 top1=%.4f per_step=%s t=%.1fs" % (
        seed, r_reproduce["top1"], r_reproduce["per_step_acc"],
        r_reproduce["elapsed_s_arm"]), flush=True)
    meta_m7_ok = (META_M7_RAIL_LO <= r_reproduce["top1"] <= META_M7_RAIL_HI)
    out["meta_m7_rail_ok"] = meta_m7_ok

    # ===== CELL B V1 REGIME (1000 bindings) =====
    t_arm = time.time()
    ptr_triples, ptr_chains = make_deep_chains(
        POINTER_N_CHAINS, V_CONCEPTS, POINTER_V_P, max_depth=DEPTH,
        g=g, disallow_s=set())
    W_v1_regime = ingest_hebbian(ptr_triples, E, R, sq, N_DIM)
    print("  [seed=%d] v1-regime W built (%d triples) t=%.1fs" % (
        seed, len(ptr_triples), round(time.time() - t_arm, 2)), flush=True)

    # ----- SINGLE_TOP1 (informational rail) -----
    t_arm = time.time()
    r_single = arm_single_chain_naive(E, R, sq, W_v1_regime, ptr_chains, depth=DEPTH)
    r_single["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    r_single["W_n_bindings"] = len(ptr_triples)
    out["arm_single_top1_5hop"] = r_single
    print("  [seed=%d] SINGLE_TOP1 top1=%.4f per_step=%s t=%.1fs" % (
        seed, r_single["top1"], r_single["per_step_acc"],
        r_single["elapsed_s_arm"]), flush=True)

    # ----- PART_ORACLE (cross-cell sanity to Cell B v2) -----
    t_arm = time.time()
    r_oracle = arm_part_oracle(E, R, sq, ptr_triples, ptr_chains, depth=DEPTH,
                                  n_partitions=N_PARTITIONS)
    r_oracle["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    out["arm_part_oracle_5hop"] = r_oracle
    print("  [seed=%d] PART_ORACLE top1=%.4f per_step=%s t=%.1fs" % (
        seed, r_oracle["top1"], r_oracle["per_step_acc"],
        r_oracle["elapsed_s_arm"]), flush=True)
    # Cross-cell drift check only applies in FULL regime (Cell B v2 was 1000 bindings @ N=8192).
    # Smoke uses 250 bindings @ N=2048 -- a different regime, so PART_ORACLE will naturally drift.
    if RUN_MODE == "full":
        cross_cell_drift = abs(r_oracle["top1"] - CROSS_CELL_PART_ORACLE_TARGET) > CROSS_CELL_PART_ORACLE_TOL
        out["cross_cell_part_oracle_drift"] = cross_cell_drift
        if cross_cell_drift:
            print("  [seed=%d] CROSS_CELL_DRIFT: PART_ORACLE=%.4f deviates from "
                  "Cell B v2 target %.4f by > %.2f"
                  % (seed, r_oracle["top1"], CROSS_CELL_PART_ORACLE_TARGET,
                     CROSS_CELL_PART_ORACLE_TOL), flush=True)
    else:
        out["cross_cell_part_oracle_drift"] = False  # smoke regime; not measured against full target

    # ----- PART_BIDIR_COLLIDE (USER's steelman; Anchor 1) -----
    t_arm = time.time()
    r_bidir = arm_part_bidir_collide(E, R, sq, W_v1_regime, ptr_chains, depth=DEPTH,
                                        n_partitions=N_PARTITIONS)
    r_bidir["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    out["arm_part_bidir_collide_5hop"] = r_bidir
    print("  [seed=%d] PART_BIDIR_COLLIDE top1=%.4f endpoint_routing_acc=%.4f t=%.1fs" % (
        seed, r_bidir["top1"], r_bidir["endpoint_routing_acc"],
        r_bidir["elapsed_s_arm"]), flush=True)

    # ----- PART_FLY_LSH (Anchor 2) -----
    t_arm = time.time()
    projs = build_fly_lsh_projs(N_DIM, N_LSH_EXPANSIONS, g)
    r_lsh = arm_part_fly_lsh(E, R, sq, W_v1_regime, ptr_chains, depth=DEPTH,
                                projs=projs, n_partitions=N_PARTITIONS)
    r_lsh["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    out["arm_part_fly_lsh_5hop"] = r_lsh
    print("  [seed=%d] PART_FLY_LSH top1=%.4f endpoint_routing_acc=%.4f t=%.1fs" % (
        seed, r_lsh["top1"], r_lsh["endpoint_routing_acc"],
        r_lsh["elapsed_s_arm"]), flush=True)

    # ----- PART_NAIVE_CENTROID (falsification anchor) -----
    t_arm = time.time()
    r_naive = arm_part_naive_centroid(E, R, sq, W_v1_regime, ptr_chains, depth=DEPTH,
                                         n_partitions=N_PARTITIONS)
    r_naive["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    out["arm_part_naive_centroid_5hop"] = r_naive
    print("  [seed=%d] PART_NAIVE_CENTROID top1=%.4f endpoint_routing_acc=%.4f t=%.1fs" % (
        seed, r_naive["top1"], r_naive["endpoint_routing_acc"],
        r_naive["elapsed_s_arm"]), flush=True)

    out["elapsed_s"] = round(time.time() - t, 1)
    return out


# ---- verdict ----

def verdict_from(per_seed: List[Dict[str, Any]]) -> Tuple[str, str]:
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

    baseline = mean_top1("arm_baseline_hrr_2hop")
    reproduce = mean_top1("arm_reproduce_pointer_chain_v2_5hop")
    single = mean_top1("arm_single_top1_5hop")
    oracle = mean_top1("arm_part_oracle_5hop")
    bidir = mean_top1("arm_part_bidir_collide_5hop")
    bidir_cv = cv_top1("arm_part_bidir_collide_5hop")
    lsh = mean_top1("arm_part_fly_lsh_5hop")
    lsh_cv = cv_top1("arm_part_fly_lsh_5hop")
    naive = mean_top1("arm_part_naive_centroid_5hop")

    sanity_breached = sum(1 for p in per_seed if not p.get("baseline_sanity_ok", False))
    meta_m7_breached = sum(1 for p in per_seed if not p.get("meta_m7_rail_ok", False))
    cross_cell_drifted = sum(1 for p in per_seed if p.get("cross_cell_part_oracle_drift", False))

    rails: List[str] = []
    if sanity_breached > 0:
        rails.append("SANITY_BREACH(%d/%d; baseline_mean=%.4f)" % (
            sanity_breached, len(per_seed), baseline))
    if meta_m7_breached > 0:
        rails.append("META_M7_BREACH(%d/%d; reproduce_mean=%.4f; rail=[%.2f, %.2f])" % (
            meta_m7_breached, len(per_seed), reproduce, META_M7_RAIL_LO, META_M7_RAIL_HI))
    if cross_cell_drifted > 0:
        rails.append("CROSS_CELL_DRIFT(%d/%d; PART_ORACLE_mean=%.4f vs Cell_B_v2=%.4f tol=%.2f)" % (
            cross_cell_drifted, len(per_seed), oracle,
            CROSS_CELL_PART_ORACLE_TARGET, CROSS_CELL_PART_ORACLE_TOL))

    bidir_passes = (not math.isnan(bidir) and bidir >= HP_ROUTER
                    and (math.isnan(bidir_cv) or bidir_cv <= HP_CV_MAX))
    lsh_passes = (not math.isnan(lsh) and lsh >= HP_ROUTER
                  and (math.isnan(lsh_cv) or lsh_cv <= HP_CV_MAX))
    both_fail_hf = (not math.isnan(bidir) and bidir <= HF_ROUTER
                    and not math.isnan(lsh) and lsh <= HF_ROUTER)

    meta_m7_ok_overall = (meta_m7_breached < max(1, (len(per_seed) + 1) // 2))

    # Discriminator tag for BIAS-P scope flag
    if bidir_passes and lsh_passes:
        bias_p_tag = "BIAS_P_REMOVED_VIA_BOTH_INDEPENDENT_PATHS"
    elif bidir_passes and not lsh_passes:
        bias_p_tag = "BIAS_P_REMOVED_VIA_BIDIR_COLLIDE"
    elif lsh_passes and not bidir_passes:
        bias_p_tag = "BIAS_P_REMOVED_VIA_FLY_LSH"
    else:
        bias_p_tag = "BIAS_P_STANDS_NEITHER_ROUTER_VIABLE"

    interp = ("Bidirectional state IS a substrate-native routing signal"
              if bidir_passes else
              "Bidirectional state IS NOT a substrate-native routing signal at HP threshold")

    summ = ("BASELINE=%.4f (sanity_breach=%d/%d) REPRODUCE_PV2=%.4f (META_M7_breach=%d/%d) "
            "SINGLE=%.4f PART_ORACLE=%.4f (cross_cell_drift=%d/%d vs %.4f) "
            "PART_BIDIR_COLLIDE=%.4f (cv=%.3f) PART_FLY_LSH=%.4f (cv=%.3f) "
            "PART_NAIVE_CENTROID=%.4f | %s | %s | rails=%s") % (
        baseline, sanity_breached, len(per_seed),
        reproduce, meta_m7_breached, len(per_seed),
        single, oracle, cross_cell_drifted, len(per_seed),
        CROSS_CELL_PART_ORACLE_TARGET,
        bidir, bidir_cv, lsh, lsh_cv, naive, bias_p_tag, interp, rails,
    )

    # Sanity rail pre-emption
    if sanity_breached >= max(1, (len(per_seed) + 1) // 2):
        return "SANITY_BREACH", "SANITY_BREACH_BASELINE_OUT_OF_BAND: " + summ

    # Composite verdict
    if bidir_passes and lsh_passes and meta_m7_ok_overall:
        return "HARD_PASS_CHAIN_GRADE_BOTH_ROUTERS", \
               "HARD_PASS_CHAIN_GRADE_BOTH_ROUTERS: " + summ
    if bidir_passes and not lsh_passes and meta_m7_ok_overall:
        return "HARD_PASS_CHAIN_GRADE_BIDIR_ROUTER", \
               "HARD_PASS_CHAIN_GRADE_BIDIR_ROUTER: " + summ
    if lsh_passes and not bidir_passes and meta_m7_ok_overall:
        return "HARD_PASS_CHAIN_GRADE_LSH_ROUTER", \
               "HARD_PASS_CHAIN_GRADE_LSH_ROUTER: " + summ
    if (bidir_passes or lsh_passes) and not meta_m7_ok_overall:
        return "HARD_PASS_WITH_META_M7_NOTE", \
               "HARD_PASS_WITH_META_M7_NOTE_REGIME_DIFF: " + summ
    if both_fail_hf:
        return "HARD_FAIL_ROUTING_NOT_VIABLE", \
               "HARD_FAIL_ROUTING_NOT_VIABLE: " + summ
    return "MIDDLE_BAND_ROUTING_PARTIAL", "MIDDLE_BAND_ROUTING_PARTIAL: " + summ


_RESULTS_HOLDER: Dict[str, Any] = {"out_dir": None, "started_at": time.time()}


def _atexit_synth() -> None:
    od = _RESULTS_HOLDER["out_dir"]
    if od is None:
        return
    try:
        agg = aggregate_partials(od, seeds=[str(s) for s in SEEDS],
                                  run_config={"N": N_DIM, "run_mode": RUN_MODE})
        if not agg:
            return
        per_seed = [agg[k] for k in sorted(agg.keys())]
        if not per_seed:
            return
        if (od / "metrics.json").exists():
            return
        v, vmsg = verdict_from(per_seed)
        metrics = {
            "anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg,
            "run_mode": RUN_MODE, "n_seeds": len(per_seed),
            "config_version": CONFIG_VERSION, "per_seed": per_seed,
            "elapsed_s": round(time.time() - _RESULTS_HOLDER["started_at"], 1),
            "summary": vmsg, "_atexit_synth": True,
            "_llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
        }
        write_metrics(od, metrics, results=per_seed)
        print("[atexit] wrote synth metrics.json (%d seeds)" % len(per_seed), flush=True)
    except Exception as e:
        print("[atexit] FAIL: %s" % e, flush=True)


atexit.register(_atexit_synth)


if __name__ == "__main__":
    print("[config] anchor=%s mode=%s seeds=%s N=%d | %s" % (
        ANCHOR_NAME, RUN_MODE, SEEDS, N_DIM, CONFIG_VERSION), flush=True)
    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)
    _RESULTS_HOLDER["out_dir"] = out_dir

    run_config = {"N": N_DIM, "run_mode": RUN_MODE}
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print("[ckpt] done=%s remaining=%s" % (done, remaining), flush=True)

    for s in remaining:
        rec = run_seed(s)
        write_partial_key(out_dir, s, rec)

    agg = aggregate_partials(out_dir, seeds=[str(s) for s in SEEDS], run_config=run_config)
    per_seed = [agg[str(s)] for s in SEEDS if str(s) in agg]
    if not per_seed:
        print("[FATAL] no partials available", flush=True)
        sys.exit(1)

    assert _LLM_CALL_COUNTER[0] == 0

    v, vmsg = verdict_from(per_seed)
    print("\n[VERDICT] " + vmsg, flush=True)
    metrics = {
        "anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg,
        "run_mode": RUN_MODE, "n_seeds": len(per_seed),
        "config_version": CONFIG_VERSION, "per_seed": per_seed,
        "elapsed_s": round(time.time() - _RESULTS_HOLDER["started_at"], 1),
        "summary": vmsg,
        "_llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
        "DESIGN_NOTE": (
            "Gap 1 partition-routing BIAS-P removal: tests USER steelman "
            "(bidirectional-collide) + Research-ranked Anchor 2 (fly-LSH). "
            "Cell B v2 PART_ORACLE=0.9550 used oracle target_part = target_o // part_sz. "
            "This cell replaces oracle with substrate-native routers; verdict_msg "
            "explicitly states which router (if any) removes BIAS-P. Cross-cell "
            "sanity rail: ARM_PART_ORACLE must reproduce Cell B v2 0.9550 +/- 0.02."
        ),
    }
    write_metrics(out_dir, metrics, results=per_seed)
    print("[done] metrics.json written (%d seeds, %.1fs)" % (
        len(per_seed), metrics["elapsed_s"]), flush=True)
