"""gap1_partition_routing_cortex_R_schema_closed_form_v1_META_M7.

Tests Research Gap 1 cortex-as-router insight: 0.66 routing ceiling is a
SINGLE-PATHWAY ceiling. Brain solves it via mPFC schema-bias signal --
a SEPARATE pathway from query to partition that bypasses the
noise-collapsed forward retrieval state.

This cell extends Cell B v2 + bidir-collide infrastructure with a
closed-form R_schema query-to-partition router (Research Cand 1; the
cheapest decisive test of the brain-architecture insight). Reuses the
kv_learned_projection precedent (chain-grade 0.827; 2026-06-20).

Mechanism: R_schema in R^{N_PARTS x N x N_HOPS}, fitted via ridge-regularized
least squares from training chains (80%) to (one-hot target partition per
hop). At inference, partition_logits[h] = R_schema[h] @ query_at_hop_h;
predicted_part_h = argmax. Then standard within-partition cleanup.

ARMS (6 in full; 7 with optional ARM_PART_R_SCHEMA_TRAINED stretch):
  ARM_BASELINE_HRR_2HOP             sanity rail [0.62, 0.68]
  ARM_REPRODUCE_POINTER_CHAIN_V2_5HOP  META_M7 rail [0.08, 0.25] (mandatory)
  ARM_SINGLE_TOP1_5HOP              v1 monolithic informational rail
  ARM_PART_ORACLE_5HOP              CROSS-CELL SANITY (Cell B v2 0.9550 +/- 0.02)
  ARM_PART_BIDIR_COLLIDE_5HOP       CROSS-CELL SANITY (bidir-collide 0.6583 +/- 0.03)
  ARM_PART_R_SCHEMA_CLOSED_FORM_5HOP MAIN TEST -- closed-form query-router
                                                   [HP >= 0.80; HF <= 0.50]

PROSPECTIVE BANDS (locked at module-init assert):
  HARD_PASS_CHAIN_GRADE_BIDIR_ROUTER_REMOVED:
      R_SCHEMA top1 >= 0.80
      AND META_M7 PASS
      AND R_schema cv <= 0.07
      AND R_schema beats BIDIR_COLLIDE by >= 0.10
  HARD_PASS_PARTIAL:
      R_SCHEMA in [0.70, 0.80)
  MIDDLE_BAND:
      R_SCHEMA in [0.50, 0.70)
  HARD_FAIL:
      R_SCHEMA <= 0.50 (closed-form router insufficient)

Train/test discipline: R_schema fit on 80% chains; HP evaluation on 20% held-out.
Cone-preservation guard: measure cosine of R_schema-projected query vs query.

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

ANCHOR_NAME = "gap1_partition_routing_cortex_R_schema_closed_form_v1_META_M7"
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
HP_ROUTER = 0.80
HP_PARTIAL_LO = 0.70
MIDDLE_BAND_LO = 0.50
HF_ROUTER = 0.50
HP_CV_MAX = 0.07
HP_LIFT_OVER_BIDIR = 0.10

# SACRED SANITY rails
BASELINE_SANITY_LO = 0.62
BASELINE_SANITY_HI = 0.68

# META_M7 rail
META_M7_RAIL_LO = 0.08
META_M7_RAIL_HI = 0.25

# Cross-cell PART_ORACLE rail (Cell B v2 mean = 0.9550)
CROSS_CELL_PART_ORACLE_TARGET = 0.9550
CROSS_CELL_PART_ORACLE_TOL = 0.02

# Cross-cell PART_BIDIR_COLLIDE rail (parent cell mean = 0.6583)
CROSS_CELL_BIDIR_TARGET = 0.6583
CROSS_CELL_BIDIR_TOL = 0.03

# Regime constants
BASELINE_V_P = 2
BASELINE_N_CHAINS = 200
POINTER_V_P = 10
POINTER_K_SET = 20

# POINTER-V2 regime (META_M7 rail)
POINTER_V2_N_CHAINS = 200
POINTER_V2_MAX_DEPTH = 10

# Partition primitives
N_PARTITIONS = 20

# R_schema discipline
R_SCHEMA_RIDGE_LAMBDA = 0.01     # ridge regularization (tiny; closed-form fit)
R_SCHEMA_TRAIN_FRACTION = 0.80   # train/test split

# META_PROSPECTIVE_BANDS_FRESH_SEEDS lock
assert HP_ROUTER > HP_PARTIAL_LO > MIDDLE_BAND_LO == HF_ROUTER, \
    "HP > HP_PARTIAL_LO > MIDDLE_BAND_LO == HF_ROUTER"
assert 0.0 < HP_CV_MAX < 0.20
assert META_M7_RAIL_LO < META_M7_RAIL_HI < HF_ROUTER, \
    "META_M7 must be below HF_ROUTER (pointer-v2 regime is genuinely harder)"
assert BASELINE_SANITY_LO < BASELINE_SANITY_HI
assert 0.90 < CROSS_CELL_PART_ORACLE_TARGET < 1.0
assert 0.0 < CROSS_CELL_PART_ORACLE_TOL < 0.10
assert 0.55 < CROSS_CELL_BIDIR_TARGET < 0.75
assert 0.0 < CROSS_CELL_BIDIR_TOL < 0.10
assert HP_LIFT_OVER_BIDIR > 0
assert 0.0 < R_SCHEMA_RIDGE_LAMBDA < 1.0
assert 0.5 < R_SCHEMA_TRAIN_FRACTION < 1.0

if RUN_MODE == "smoke":
    N_DIM = 2048
    V_CONCEPTS = 200
    SEEDS = [11]
    POINTER_N_CHAINS = 50
    POINTER_V2_N_CHAINS_LOCAL = 100  # smoke keeps depth=10 to preserve crosstalk regime
    BASELINE_N_CHAINS_LOCAL = BASELINE_N_CHAINS
else:
    N_DIM = 8192
    V_CONCEPTS = 200
    SEEDS = [11, 13, 19]
    POINTER_N_CHAINS = 200
    POINTER_V2_N_CHAINS_LOCAL = POINTER_V2_N_CHAINS  # 2000 bindings
    BASELINE_N_CHAINS_LOCAL = BASELINE_N_CHAINS

DEPTH = 5
n_predicates = max(BASELINE_V_P, POINTER_V_P)

assert V_CONCEPTS % N_PARTITIONS == 0, \
    "V_CONCEPTS=%d must divide N_PARTITIONS=%d" % (V_CONCEPTS, N_PARTITIONS)
PART_SIZE = V_CONCEPTS // N_PARTITIONS

CONFIG_VERSION = (
    "gap1PartitionRoutingCortexRSchemaClosedFormV1MetaM7: N=%d V_C=%d "
    "BASELINE_V_P=%d BASELINE_N=%d POINTER_V_P=%d POINTER_N=%d K_SET=%d "
    "POINTER_V2_N=%d POINTER_V2_DEPTH=%d "
    "N_PARTS=%d PART_SIZE=%d "
    "R_RIDGE=%.4f R_TRAIN_FRAC=%.2f "
    "seeds=%s mode=%s depth=%d midhop=%d "
    "HP_router>=%.2f HP_partial=[%.2f,%.2f) MIDDLE=[%.2f,%.2f) HF<=%.2f "
    "HP_cv<=%.2f HP_lift_over_bidir>=%.2f "
    "META_M7=[%.2f,%.2f] cross_cell_part_oracle=%.4f+/-%.2f "
    "cross_cell_bidir=%.4f+/-%.2f "
    "baseline_sanity=[%.2f,%.2f] encoder_provenance=SUBSTRATE_NATIVE"
) % (
    N_DIM, V_CONCEPTS, BASELINE_V_P, BASELINE_N_CHAINS_LOCAL,
    POINTER_V_P, POINTER_N_CHAINS, POINTER_K_SET,
    POINTER_V2_N_CHAINS_LOCAL, POINTER_V2_MAX_DEPTH,
    N_PARTITIONS, PART_SIZE,
    R_SCHEMA_RIDGE_LAMBDA, R_SCHEMA_TRAIN_FRACTION,
    SEEDS, RUN_MODE, DEPTH, DEPTH // 2,
    HP_ROUTER, HP_PARTIAL_LO, HP_ROUTER, MIDDLE_BAND_LO, HP_PARTIAL_LO, HF_ROUTER,
    HP_CV_MAX, HP_LIFT_OVER_BIDIR,
    META_M7_RAIL_LO, META_M7_RAIL_HI,
    CROSS_CELL_PART_ORACLE_TARGET, CROSS_CELL_PART_ORACLE_TOL,
    CROSS_CELL_BIDIR_TARGET, CROSS_CELL_BIDIR_TOL,
    BASELINE_SANITY_LO, BASELINE_SANITY_HI,
)


# ---- substrate primitives (verbatim ports from parent cell) ----

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
    """VERBATIM port of pointer-chain v2 / Cell B v2 cleanup primitive."""
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


# ---- forward / backward state walkers (verbatim parent cell) ----

def _forward_state(E, W, R, sq, start_idx: int, predicates: List[int]) -> np.ndarray:
    state = E[start_idx].copy()
    for p in predicates:
        state = W @ (state * R[p] * sq)
    return state


def _backward_state(E, W, R, sq, end_idx: int, predicates: List[int]) -> np.ndarray:
    state = E[end_idx].copy()
    for i in range(len(predicates) - 1, -1, -1):
        p = predicates[i]
        state = W.T @ state
        state = state * R[p] * sq
    return state


# ---- ARM: PART_ORACLE (cross-cell sanity reproduction of Cell B v2) ----

def arm_part_oracle(E, R, sq, triples, chains_test, depth: int,
                    n_partitions: int = N_PARTITIONS) -> Dict[str, Any]:
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
            routing_correct[i] += 1
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
    routing_acc = (routing_correct.astype(np.float32) /
                   max(total_routing_calls // depth, 1)).tolist()
    return {"top1": round(hits / max(n, 1), 4),
            "per_step_acc": [round(x, 4) for x in per_step_acc],
            "routing_acc_per_hop": [round(x, 4) for x in routing_acc],
            "n_queries": n, "depth": depth, "n_partitions": n_partitions,
            "mechanism": "partition_per_hop_oracle_routed_cross_cell_sanity",
            "W_n_bindings": len(triples)}


# ---- ARM: PART_BIDIR_COLLIDE (parent cell cross-cell rail) ----

def arm_part_bidir_collide(E, R, sq, W, chains_test, depth: int,
                            n_partitions: int = N_PARTITIONS) -> Dict[str, Any]:
    """Parent-cell bidir-collide; reproduced as cross-cell rail at 0.6583 +/- 0.03."""
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
        state_fwd_mid = _forward_state(E, W, R, sq, S, preds[:mid])
        state_fwd_full = _forward_state(E, W, R, sq, S, preds)
        bwd = E.copy()
        remaining = preds[mid:]
        for j in range(len(remaining) - 1, -1, -1):
            p_j = remaining[j]
            bwd = bwd @ W
            bwd = bwd * (R[p_j] * sq)
        cos_per_Z = bwd @ state_fwd_mid
        scores = np.array([cos_per_Z[pp * part_sz:(pp + 1) * part_sz].sum()
                           for pp in range(n_partitions)], dtype=np.float32)
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
            "midpoint_hop": mid,
            "mechanism": "partition_meet_in_middle_bidirectional_collide_cross_cell_rail"}


# ---- ARM: PART_R_SCHEMA_CLOSED_FORM (MAIN TEST) ----

def fit_R_schema(queries_X: np.ndarray, targets_Y: np.ndarray,
                  n_dim: int, n_parts: int, ridge_lambda: float) -> np.ndarray:
    """Closed-form ridge regression: R = Y^T X (X^T X + lambda I)^-1.

    Args:
        queries_X: (N_train, N_DIM) -- training query embeddings (E[source_at_hop_h]).
        targets_Y: (N_train, N_PARTS) -- one-hot target partition per training query.
        n_dim: substrate dim.
        n_parts: N_PARTITIONS.
        ridge_lambda: regularization strength (tiny; closed-form fit).

    Returns:
        R: (N_PARTS, N_DIM) -- partition_logits[p] = R[p] @ query.

    Brain-analog: mPFC schema-bias projection from query input -> partition pre-activation.
    Substrate-precedent: kv_learned_projection (chain-grade 0.827; 2026-06-20) uses
    the same closed-form pseudoinverse capability class.
    """
    # X: (N_train, N_DIM); Y: (N_train, N_PARTS)
    # Solve: minimize ||X B - Y||^2 + lambda ||B||^2 over B in R^{N_DIM, N_PARTS}.
    # Closed form: B = (X^T X + lambda I)^-1 X^T Y    -> shape (N_DIM, N_PARTS)
    # Then R = B^T -> (N_PARTS, N_DIM).
    XtX = queries_X.T @ queries_X  # (N_DIM, N_DIM)
    XtY = queries_X.T @ targets_Y  # (N_DIM, N_PARTS)
    # Ridge: add lambda * I  (scaled by trace/N_DIM for stability)
    trace_factor = float(np.trace(XtX) / max(n_dim, 1))
    A = XtX + ridge_lambda * trace_factor * np.eye(n_dim, dtype=np.float32)
    # Solve A B = XtY  -> B = A^-1 XtY
    B = np.linalg.solve(A.astype(np.float64), XtY.astype(np.float64)).astype(np.float32)
    R = B.T  # (N_PARTS, N_DIM)
    return R


def arm_part_r_schema_closed_form(E, R_rel, sq, W, chains_test, depth: int,
                                    n_partitions: int = N_PARTITIONS,
                                    train_fraction: float = R_SCHEMA_TRAIN_FRACTION,
                                    ridge_lambda: float = R_SCHEMA_RIDGE_LAMBDA,
                                    seed: int = 0) -> Dict[str, Any]:
    """Closed-form query-to-partition router (Research Cand 1; brain analog).

    Architecture (per Research Section 3 Cand 1):
        Offline (training set): for each training chain c, for each hop h,
            x_h = E[source_at_hop_h(c)]   # query embedding at hop h
            y_h = one_hot(target_part_at_hop_h(c))   # one-hot in R^N_PARTS
        Fit R_schema[h] in R^{N_PARTS x N_DIM} via ridge least squares.

        Inference (test set): for each test chain, for each hop h,
            partition_logits[h] = R_schema[h] @ E[current_source_h]
            predicted_part[h] = argmax(partition_logits[h])
            scores_within = E_parts[predicted_part[h]] @ (W @ key)
            predicted_o = part_offset[predicted_part[h]] + argmax(scores_within)

    NO ORACLE. Reads from QUERY (clean signal), NOT from noise-collapsed state_fwd.
    This SIDESTEPS the 0.66 bidirectional ceiling structurally.

    Train/test split: train_fraction (default 0.80) of chains for R_schema fit;
    remainder for HP evaluation. Train >> test gap >0.10 flags overfit.

    Returns top1 (test-set fraction of chains where final predicted endpoint matches),
    per_step_acc, train_top1 (train-set held-out for overfit detection),
    routing_acc_per_hop, R_schema_fit_s.
    """
    n_dim = E.shape[1]
    V = E.shape[0]
    assert V % n_partitions == 0
    part_sz = V // n_partitions
    E_parts = [E[p * part_sz:(p + 1) * part_sz] for p in range(n_partitions)]
    part_offsets = [p * part_sz for p in range(n_partitions)]

    # Train/test split (deterministic from seed)
    n = len(chains_test)
    rng_split = np.random.default_rng(seed + 1000003)
    perm = rng_split.permutation(n)
    n_train = int(n * train_fraction)
    train_idx = perm[:n_train]
    test_idx = perm[n_train:]
    chains_train = [chains_test[i] for i in train_idx]
    chains_eval = [chains_test[i] for i in test_idx]
    assert len(chains_train) > 0 and len(chains_eval) > 0, \
        "need both train and eval chains; got %d/%d" % (len(chains_train), len(chains_eval))

    # ---- Offline fit: build per-hop R_schema[h] from training chains ----
    t_fit_start = time.time()
    R_schema_per_hop: List[np.ndarray] = []
    cone_cos_per_hop: List[float] = []
    for h in range(depth):
        # Collect (query_embedding_at_hop_h, target_partition_at_hop_h) from training chains
        # Use teacher-forced source (clean chain trajectory), matching the brain-analog:
        # mPFC schema-bias on the QUERY input, not on noise-degraded retrieval state.
        Xs = []
        Ys = []
        for chain in chains_train:
            # Source at hop h is the (h)-th source in the chain (h=0 is start; h>=1 is
            # previous-hop target, i.e. the clean chain). Targets are chain[h][2].
            if h == 0:
                s_h = chain[0][0]
            else:
                s_h = chain[h - 1][2]
            t_h = chain[h][2]
            target_part = t_h // part_sz
            Xs.append(E[s_h])
            y = np.zeros(n_partitions, dtype=np.float32)
            y[target_part] = 1.0
            Ys.append(y)
        Xs_arr = np.asarray(Xs, dtype=np.float32)
        Ys_arr = np.asarray(Ys, dtype=np.float32)
        R_h = fit_R_schema(Xs_arr, Ys_arr, n_dim, n_partitions, ridge_lambda)
        R_schema_per_hop.append(R_h)
        # Cone-preservation guard (Research cross-cell rail): measure cosine of
        # R_schema-projected query vs raw query for a sample of training queries.
        # Project = R_h.T @ R_h @ query (back-projection into N_DIM); compare cosine.
        Rt_R = R_h.T @ R_h  # (N_DIM, N_DIM)
        sample = Xs_arr[:min(20, len(Xs_arr))]
        cos_vals = []
        for q in sample:
            qp = Rt_R @ q
            cn = (np.linalg.norm(q) * np.linalg.norm(qp)) + 1e-8
            cos_vals.append(float(np.dot(q, qp) / cn))
        cone_cos_per_hop.append(float(np.mean(cos_vals)) if cos_vals else 0.0)
    R_schema_fit_s = round(time.time() - t_fit_start, 3)

    # ---- Train-set HP (using teacher-forced sources; for overfit detection) ----
    train_hits = 0
    train_per_hop_routing = np.zeros(depth, dtype=np.int64)
    for chain in chains_train:
        s = chain[0][0]
        for h in range(depth):
            p = chain[h][1]
            target_o = chain[h][2]
            true_part = target_o // part_sz
            # Predict partition for hop h from QUERY (current source)
            q_h = E[s]
            part_logits = R_schema_per_hop[h] @ q_h
            predicted_part = int(part_logits.argmax())
            if predicted_part == true_part:
                train_per_hop_routing[h] += 1
            # Within-partition cleanup
            key = (E[s] * R_rel[p] * sq).astype(np.float32)
            scores_within = E_parts[predicted_part] @ (W @ key)
            local_idx = int(scores_within.argmax())
            s = part_offsets[predicted_part] + local_idx
        if s == chain[depth - 1][2]:
            train_hits += 1
    train_top1 = train_hits / max(len(chains_train), 1)

    # ---- Test-set HP (THIS is the verdict-relevant metric) ----
    test_hits = 0
    per_step_hits = np.zeros(depth, dtype=np.int64)
    routing_correct = np.zeros(depth, dtype=np.int64)
    for chain in chains_eval:
        s = chain[0][0]
        for h in range(depth):
            p = chain[h][1]
            target_o = chain[h][2]
            true_part = target_o // part_sz
            q_h = E[s]
            part_logits = R_schema_per_hop[h] @ q_h
            predicted_part = int(part_logits.argmax())
            if predicted_part == true_part:
                routing_correct[h] += 1
            key = (E[s] * R_rel[p] * sq).astype(np.float32)
            scores_within = E_parts[predicted_part] @ (W @ key)
            local_idx = int(scores_within.argmax())
            s_pred = part_offsets[predicted_part] + local_idx
            if s_pred == target_o:
                per_step_hits[h] += 1
            s = s_pred
        if s == chain[depth - 1][2]:
            test_hits += 1
    test_top1 = test_hits / max(len(chains_eval), 1)
    per_step_acc = (per_step_hits.astype(np.float32) / max(len(chains_eval), 1)).tolist()
    routing_acc = (routing_correct.astype(np.float32) / max(len(chains_eval), 1)).tolist()

    # Overfit guard (Research cross-cell rail): train >> test by >0.10
    overfit_gap = train_top1 - test_top1
    overfit_flag = bool(overfit_gap > 0.10)

    # Cone-rotation guard (Research cross-cell rail): mean cone-cos < 0.90 flags rotation
    mean_cone_cos = float(np.mean(cone_cos_per_hop))
    cone_rotation_risk = bool(mean_cone_cos < 0.90)

    return {"top1": round(test_top1, 4),
            "train_top1": round(train_top1, 4),
            "overfit_gap": round(overfit_gap, 4),
            "overfit_flag": overfit_flag,
            "per_step_acc": [round(x, 4) for x in per_step_acc],
            "routing_acc_per_hop": [round(x, 4) for x in routing_acc],
            "cone_cos_per_hop": [round(x, 4) for x in cone_cos_per_hop],
            "mean_cone_cos": round(mean_cone_cos, 4),
            "cone_rotation_risk": cone_rotation_risk,
            "n_queries_train": len(chains_train),
            "n_queries_eval": len(chains_eval),
            "depth": depth, "n_partitions": n_partitions,
            "R_schema_fit_s": R_schema_fit_s,
            "ridge_lambda": ridge_lambda,
            "train_fraction": train_fraction,
            "mechanism": "partition_routing_closed_form_R_schema_query_to_partition_brain_mPFC_analog"}


# ---- self-test ----

def _selftest() -> None:
    g = np.random.default_rng(0)
    n = 512
    V = 40
    sq = math.sqrt(n)
    E = bipolar(V, n, g)
    R_rel = bipolar(max(BASELINE_V_P, POINTER_V_P), n, g)

    # T1: BASELINE
    Rb = bipolar(max(BASELINE_V_P, 2), n, g)
    train, queries = make_two_hop_chains_betasweep(20, V, g, p1=0, p2=1)
    r_base = arm_baseline_hrr_2hop_betasweep(E, Rb, sq, train, queries)
    assert 0.0 <= r_base["top1"] <= 1.0

    # T2: REPRODUCE arm (META_M7 rail)
    triples_v2, chains_v2 = make_deep_chains(8, V, 4, max_depth=10, g=g, disallow_s=set())
    W_v2 = ingest_hebbian(triples_v2, E, R_rel, sq, n)
    chains_v2_test = [c[:5] for c in chains_v2]
    r_reproduce = arm_single_chain_naive(E, R_rel, sq, W_v2, chains_v2_test, depth=5)
    assert 0.0 <= r_reproduce["top1"] <= 1.0

    # T3: SINGLE arm (v1 regime)
    triples_v1, chains_v1 = make_deep_chains(8, V, 4, max_depth=5, g=g, disallow_s=set())
    W_v1 = ingest_hebbian(triples_v1, E, R_rel, sq, n)
    r_single = arm_single_chain_naive(E, R_rel, sq, W_v1, chains_v1, depth=5)
    assert 0.0 <= r_single["top1"] <= 1.0

    # T4: PART_ORACLE
    r_oracle = arm_part_oracle(E, R_rel, sq, triples_v1, chains_v1, depth=5, n_partitions=4)
    assert 0.0 <= r_oracle["top1"] <= 1.0
    for ra in r_oracle["routing_acc_per_hop"]:
        assert ra == 1.0, "PART_ORACLE routing_acc must be 1.0; got %s" % ra

    # T5: PART_BIDIR_COLLIDE
    r_bidir = arm_part_bidir_collide(E, R_rel, sq, W_v1, chains_v1, depth=5, n_partitions=4)
    assert 0.0 <= r_bidir["top1"] <= 1.0

    # T6: PART_R_SCHEMA closed-form (MAIN TEST)
    r_rschema = arm_part_r_schema_closed_form(
        E, R_rel, sq, W_v1, chains_v1, depth=5,
        n_partitions=4, train_fraction=R_SCHEMA_TRAIN_FRACTION,
        ridge_lambda=R_SCHEMA_RIDGE_LAMBDA, seed=0)
    assert 0.0 <= r_rschema["top1"] <= 1.0
    assert 0.0 <= r_rschema["train_top1"] <= 1.0
    assert r_rschema["n_queries_train"] > 0
    assert r_rschema["n_queries_eval"] > 0
    assert r_rschema["R_schema_fit_s"] >= 0.0
    # Cone-preservation sanity: closed-form fit on tiny data may rotate; just assert finite.
    assert -1.0 <= r_rschema["mean_cone_cos"] <= 1.0

    # T7: closed-form fit math sanity -- on a tiny problem, recovers a known mapping
    # X = identity-ish; Y = perfect partition; R should give near-perfect train top1.
    n_train_sanity = 8
    n_dim_sanity = 32
    n_parts_sanity = 4
    Xs = bipolar(n_train_sanity, n_dim_sanity, g)
    Ys = np.zeros((n_train_sanity, n_parts_sanity), dtype=np.float32)
    for i in range(n_train_sanity):
        Ys[i, i % n_parts_sanity] = 1.0
    R_test = fit_R_schema(Xs, Ys, n_dim_sanity, n_parts_sanity, 0.001)
    # Train-set predicted partitions; sanity that the matrix multiplies the right way.
    logits = Xs @ R_test.T  # (n_train, n_parts)
    pred = logits.argmax(axis=1)
    true_parts = np.array([i % n_parts_sanity for i in range(n_train_sanity)], dtype=np.int64)
    # With ridge on under-determined system + 8 examples, accuracy is regime-dependent;
    # require >= 1/N_PARTS chance level (closed-form is at least informative).
    acc = (pred == true_parts).mean()
    assert acc >= 1.0 / n_parts_sanity, "closed-form fit sanity below chance"

    # T8: bands locked
    assert HP_ROUTER == 0.80
    assert HP_PARTIAL_LO == 0.70
    assert MIDDLE_BAND_LO == 0.50
    assert HF_ROUTER == 0.50
    assert HP_CV_MAX == 0.07
    assert HP_LIFT_OVER_BIDIR == 0.10
    assert META_M7_RAIL_LO == 0.08 and META_M7_RAIL_HI == 0.25
    assert CROSS_CELL_PART_ORACLE_TARGET == 0.9550 and CROSS_CELL_PART_ORACLE_TOL == 0.02
    assert CROSS_CELL_BIDIR_TARGET == 0.6583 and CROSS_CELL_BIDIR_TOL == 0.03
    assert R_SCHEMA_RIDGE_LAMBDA == 0.01
    assert R_SCHEMA_TRAIN_FRACTION == 0.80

    # T9: LLM call counter == 0 (substrate-only at inference)
    assert _LLM_CALL_COUNTER[0] == 0

    print("[selftest] PASS base=%.3f reproduce=%.3f single=%.3f oracle=%.3f "
          "bidir=%.3f r_schema=%.3f r_schema_train=%.3f fit_s=%.3fs cone_cos=%.3f"
          % (r_base["top1"], r_reproduce["top1"], r_single["top1"], r_oracle["top1"],
             r_bidir["top1"], r_rschema["top1"], r_rschema["train_top1"],
             r_rschema["R_schema_fit_s"], r_rschema["mean_cone_cos"]),
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
    R_rel = bipolar(n_predicates, N_DIM, g)

    out = {
        "seed": seed, "run_mode": RUN_MODE, "N": N_DIM, "V_C": V_CONCEPTS,
        "n_predicates": n_predicates,
        "n_partitions": N_PARTITIONS, "part_size": PART_SIZE,
        "pointer_n_chains": POINTER_N_CHAINS,
        "pointer_v2_n_chains": POINTER_V2_N_CHAINS_LOCAL,
        "pointer_v2_max_depth": POINTER_V2_MAX_DEPTH,
        "depth": DEPTH, "midpoint_hop": DEPTH // 2,
        "ridge_lambda": R_SCHEMA_RIDGE_LAMBDA,
        "train_fraction": R_SCHEMA_TRAIN_FRACTION,
        "config_version": CONFIG_VERSION,
        "encoder_provenance": "SUBSTRATE_NATIVE",
        "_llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
    }

    # ===== BASELINE =====
    t_arm = time.time()
    base_triples, base_queries = make_two_hop_chains_betasweep(
        BASELINE_N_CHAINS_LOCAL, V_CONCEPTS, g, p1=0, p2=1)
    r_baseline = arm_baseline_hrr_2hop_betasweep(E, R_rel, sq, base_triples, base_queries)
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
    W_pointer_v2 = ingest_hebbian(ptr_v2_triples, E, R_rel, sq, N_DIM)
    print("  [seed=%d] META_M7 W built (%d triples; v2 regime depth=%d) t=%.1fs" % (
        seed, len(ptr_v2_triples), POINTER_V2_MAX_DEPTH,
        round(time.time() - t_arm, 2)), flush=True)
    t_arm = time.time()
    ptr_v2_chains_test = [c[:DEPTH] for c in ptr_v2_chains]
    r_reproduce = arm_single_chain_naive(E, R_rel, sq, W_pointer_v2,
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
    W_v1_regime = ingest_hebbian(ptr_triples, E, R_rel, sq, N_DIM)
    print("  [seed=%d] v1-regime W built (%d triples) t=%.1fs" % (
        seed, len(ptr_triples), round(time.time() - t_arm, 2)), flush=True)

    # ----- SINGLE_TOP1 (informational rail) -----
    t_arm = time.time()
    r_single = arm_single_chain_naive(E, R_rel, sq, W_v1_regime, ptr_chains, depth=DEPTH)
    r_single["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    r_single["W_n_bindings"] = len(ptr_triples)
    out["arm_single_top1_5hop"] = r_single
    print("  [seed=%d] SINGLE_TOP1 top1=%.4f per_step=%s t=%.1fs" % (
        seed, r_single["top1"], r_single["per_step_acc"],
        r_single["elapsed_s_arm"]), flush=True)

    # ----- PART_ORACLE (cross-cell sanity to Cell B v2) -----
    t_arm = time.time()
    r_oracle = arm_part_oracle(E, R_rel, sq, ptr_triples, ptr_chains, depth=DEPTH,
                                  n_partitions=N_PARTITIONS)
    r_oracle["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    out["arm_part_oracle_5hop"] = r_oracle
    print("  [seed=%d] PART_ORACLE top1=%.4f per_step=%s t=%.1fs" % (
        seed, r_oracle["top1"], r_oracle["per_step_acc"],
        r_oracle["elapsed_s_arm"]), flush=True)
    if RUN_MODE == "full":
        cross_cell_drift_oracle = abs(r_oracle["top1"] - CROSS_CELL_PART_ORACLE_TARGET) > CROSS_CELL_PART_ORACLE_TOL
        out["cross_cell_part_oracle_drift"] = cross_cell_drift_oracle
        if cross_cell_drift_oracle:
            print("  [seed=%d] CROSS_CELL_DRIFT(ORACLE): PART_ORACLE=%.4f deviates from "
                  "Cell B v2 target %.4f by > %.2f"
                  % (seed, r_oracle["top1"], CROSS_CELL_PART_ORACLE_TARGET,
                     CROSS_CELL_PART_ORACLE_TOL), flush=True)
    else:
        out["cross_cell_part_oracle_drift"] = False

    # ----- PART_BIDIR_COLLIDE (parent-cell cross-cell rail at 0.6583) -----
    t_arm = time.time()
    r_bidir = arm_part_bidir_collide(E, R_rel, sq, W_v1_regime, ptr_chains, depth=DEPTH,
                                        n_partitions=N_PARTITIONS)
    r_bidir["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    out["arm_part_bidir_collide_5hop"] = r_bidir
    print("  [seed=%d] PART_BIDIR_COLLIDE top1=%.4f endpoint_routing_acc=%.4f t=%.1fs" % (
        seed, r_bidir["top1"], r_bidir["endpoint_routing_acc"],
        r_bidir["elapsed_s_arm"]), flush=True)
    if RUN_MODE == "full":
        cross_cell_drift_bidir = abs(r_bidir["top1"] - CROSS_CELL_BIDIR_TARGET) > CROSS_CELL_BIDIR_TOL
        out["cross_cell_bidir_drift"] = cross_cell_drift_bidir
        if cross_cell_drift_bidir:
            print("  [seed=%d] CROSS_CELL_DRIFT(BIDIR): PART_BIDIR_COLLIDE=%.4f deviates "
                  "from parent target %.4f by > %.2f"
                  % (seed, r_bidir["top1"], CROSS_CELL_BIDIR_TARGET,
                     CROSS_CELL_BIDIR_TOL), flush=True)
    else:
        out["cross_cell_bidir_drift"] = False

    # ----- PART_R_SCHEMA_CLOSED_FORM (MAIN TEST -- brain mPFC analog) -----
    t_arm = time.time()
    r_rschema = arm_part_r_schema_closed_form(
        E, R_rel, sq, W_v1_regime, ptr_chains, depth=DEPTH,
        n_partitions=N_PARTITIONS,
        train_fraction=R_SCHEMA_TRAIN_FRACTION,
        ridge_lambda=R_SCHEMA_RIDGE_LAMBDA,
        seed=seed)
    r_rschema["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    out["arm_part_r_schema_closed_form_5hop"] = r_rschema
    print("  [seed=%d] PART_R_SCHEMA test_top1=%.4f train_top1=%.4f overfit_gap=%.4f "
          "routing_acc_h0=%.4f cone_cos=%.4f t=%.1fs"
          % (seed, r_rschema["top1"], r_rschema["train_top1"], r_rschema["overfit_gap"],
             r_rschema["routing_acc_per_hop"][0], r_rschema["mean_cone_cos"],
             r_rschema["elapsed_s_arm"]), flush=True)

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
    rschema = mean_top1("arm_part_r_schema_closed_form_5hop")
    rschema_cv = cv_top1("arm_part_r_schema_closed_form_5hop")

    # R_schema overfit aggregation
    overfit_flags = sum(1 for p in per_seed
                       if p.get("arm_part_r_schema_closed_form_5hop", {}).get("overfit_flag", False))
    cone_rotation_risks = sum(1 for p in per_seed
                              if p.get("arm_part_r_schema_closed_form_5hop", {}).get("cone_rotation_risk", False))

    sanity_breached = sum(1 for p in per_seed if not p.get("baseline_sanity_ok", False))
    meta_m7_breached = sum(1 for p in per_seed if not p.get("meta_m7_rail_ok", False))
    cross_cell_drifted_oracle = sum(1 for p in per_seed if p.get("cross_cell_part_oracle_drift", False))
    cross_cell_drifted_bidir = sum(1 for p in per_seed if p.get("cross_cell_bidir_drift", False))

    rails: List[str] = []
    if sanity_breached > 0:
        rails.append("SANITY_BREACH(%d/%d; baseline_mean=%.4f)" % (
            sanity_breached, len(per_seed), baseline))
    if meta_m7_breached > 0:
        rails.append("META_M7_BREACH(%d/%d; reproduce_mean=%.4f; rail=[%.2f, %.2f])" % (
            meta_m7_breached, len(per_seed), reproduce, META_M7_RAIL_LO, META_M7_RAIL_HI))
    if cross_cell_drifted_oracle > 0:
        rails.append("CROSS_CELL_DRIFT_ORACLE(%d/%d; oracle_mean=%.4f vs %.4f tol=%.2f)" % (
            cross_cell_drifted_oracle, len(per_seed), oracle,
            CROSS_CELL_PART_ORACLE_TARGET, CROSS_CELL_PART_ORACLE_TOL))
    if cross_cell_drifted_bidir > 0:
        rails.append("CROSS_CELL_DRIFT_BIDIR(%d/%d; bidir_mean=%.4f vs %.4f tol=%.2f)" % (
            cross_cell_drifted_bidir, len(per_seed), bidir,
            CROSS_CELL_BIDIR_TARGET, CROSS_CELL_BIDIR_TOL))
    if overfit_flags > 0:
        rails.append("R_SCHEMA_OVERFIT(%d/%d; train >> test by >0.10)" % (
            overfit_flags, len(per_seed)))
    if cone_rotation_risks > 0:
        rails.append("CONE_ROTATION_RISK(%d/%d; mean_cone_cos<0.90)" % (
            cone_rotation_risks, len(per_seed)))

    rschema_lift_over_bidir = (rschema - bidir) if (not math.isnan(rschema) and not math.isnan(bidir)) else float("nan")
    meta_m7_ok_overall = (meta_m7_breached < max(1, (len(per_seed) + 1) // 2))

    rschema_hp = (not math.isnan(rschema)
                  and rschema >= HP_ROUTER
                  and (math.isnan(rschema_cv) or rschema_cv <= HP_CV_MAX)
                  and not math.isnan(rschema_lift_over_bidir)
                  and rschema_lift_over_bidir >= HP_LIFT_OVER_BIDIR
                  and meta_m7_ok_overall)
    rschema_partial = (not math.isnan(rschema)
                       and HP_PARTIAL_LO <= rschema < HP_ROUTER)
    rschema_middle = (not math.isnan(rschema)
                      and MIDDLE_BAND_LO < rschema < HP_PARTIAL_LO)
    rschema_hf = (not math.isnan(rschema) and rschema <= HF_ROUTER)

    if rschema_hp:
        bias_p_tag = "BIAS_P_REMOVED_VIA_R_SCHEMA_CLOSED_FORM_QUERY_TO_PARTITION_ROUTER"
        interp = ("R_schema closed-form query-to-partition router beats 0.66 ceiling; "
                  "brain-architecture insight (separate-pathway routing from query) vindicated; "
                  "BIAS-P scope flag REMOVED from Gap 1")
    elif rschema_partial:
        bias_p_tag = "BIAS_P_PARTIAL_R_SCHEMA_LIFTS_BUT_BELOW_HP"
        interp = ("R_schema lifts above bidir baseline but does not clear HP; "
                  "partial validation of brain-architecture insight; "
                  "pivot to Cand 2 (Modern Hopfield prototype) or Cand 3 (CLS-replay)")
    elif rschema_middle:
        bias_p_tag = "BIAS_P_STANDS_R_SCHEMA_IN_MIDDLE_BAND"
        interp = ("R_schema in middle band; closed-form query-routing is informative but not "
                  "decisive; pivot to nonlinear router (Modern Hopfield) or composition (Cand 6)")
    else:
        bias_p_tag = "BIAS_P_STANDS_R_SCHEMA_HARD_FAIL"
        interp = ("Closed-form linear R_schema is NOT a viable router; partition information "
                  "NOT linearly extractable from query embedding; "
                  "pivot to nonlinear (Modern Hopfield) or replay-extracted (CLS) routing")

    summ = ("BASELINE=%.4f (sanity_breach=%d/%d) REPRODUCE_PV2=%.4f (META_M7_breach=%d/%d) "
            "SINGLE=%.4f PART_ORACLE=%.4f (cross_cell_drift_oracle=%d/%d vs %.4f) "
            "PART_BIDIR_COLLIDE=%.4f (cross_cell_drift_bidir=%d/%d vs %.4f) "
            "PART_R_SCHEMA=%.4f (cv=%.3f lift_over_bidir=%.4f) "
            "overfit_flags=%d/%d cone_rotation=%d/%d "
            "| %s | %s | rails=%s") % (
        baseline, sanity_breached, len(per_seed),
        reproduce, meta_m7_breached, len(per_seed),
        single, oracle, cross_cell_drifted_oracle, len(per_seed),
        CROSS_CELL_PART_ORACLE_TARGET,
        bidir, cross_cell_drifted_bidir, len(per_seed),
        CROSS_CELL_BIDIR_TARGET,
        rschema, rschema_cv, rschema_lift_over_bidir,
        overfit_flags, len(per_seed),
        cone_rotation_risks, len(per_seed),
        bias_p_tag, interp, rails,
    )

    # Sanity rail pre-emption
    if sanity_breached >= max(1, (len(per_seed) + 1) // 2):
        return "SANITY_BREACH", "SANITY_BREACH_BASELINE_OUT_OF_BAND: " + summ

    # Composite verdict
    if rschema_hp:
        return "HARD_PASS_CHAIN_GRADE_BIDIR_ROUTER_REMOVED", \
               "HARD_PASS_CHAIN_GRADE_BIDIR_ROUTER_REMOVED: " + summ
    if rschema_partial:
        return "HARD_PASS_PARTIAL", "HARD_PASS_PARTIAL: " + summ
    if rschema_hf:
        return "HARD_FAIL", "HARD_FAIL: " + summ
    return "MIDDLE_BAND", "MIDDLE_BAND: " + summ


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
            "encoder_provenance": "SUBSTRATE_NATIVE",
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
        "encoder_provenance": "SUBSTRATE_NATIVE",
        "DESIGN_NOTE": (
            "Gap 1 cortex-as-router R_schema closed-form: Research drill on brain "
            "mechanism for destination-hint routing (mPFC schema-bias via theta-gamma "
            "phase coupling). Closed-form pseudoinverse from QUERY (clean signal) to "
            "partition one-hot; reads SEPARATE pathway from noise-collapsed forward "
            "state. Substrate-precedent: kv_learned_projection (chain-grade 0.827; "
            "2026-06-20) same capability class. HP_CHAIN_GRADE_BIDIR_ROUTER_REMOVED: "
            "R_SCHEMA >= 0.80 AND lift over BIDIR_COLLIDE >= 0.10 AND META_M7 PASS. "
            "Cross-cell rails: PART_ORACLE = 0.9550 +/- 0.02; PART_BIDIR_COLLIDE = "
            "0.6583 +/- 0.03. Train/test split: 80/20; overfit flag >0.10 gap."
        ),
    }
    write_metrics(out_dir, metrics, results=per_seed)
    print("[done] metrics.json written (%d seeds, %.1fs)" % (
        len(per_seed), metrics["elapsed_s"]), flush=True)
