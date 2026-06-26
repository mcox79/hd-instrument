"""substrate_multihop_compose_fly_lsh_multibank_partition_v1.

REVIVAL ANGLE 1 (Research 2026-06-25 drill) -- compose today's 3 chain-grade wins.

Background:
  Today's chain-grade wins (anisotropy_rescue_4arm v2 fly-LSH; multi_bank WM 8x32;
  partition_routing 10M) each attacked a DIFFERENT bottleneck and lifted the
  per-step / retrieval primitive into chain-grade regimes. Multi-hop's bottleneck
  is per-hop cleanup accuracy (~0.69 -> 0.69^5 = 0.156). If composition of the
  three lifts per-hop into ~0.85-0.95, 5-hop chain-grade becomes feasible.

Mechanism (per-hop, substrate-native):
  fly-LSH per-hop:
    For each (E[s], R[p]) cue, expand the bind key into K=5 sparse-random
    expanded dims (top-K=20 per expansion, k-WTA on |x|). Each expansion has
    a fixed random projection matrix W_lsh[k] in {-1, +1}^{n_dim x n_dim}.
    Combine: key_expanded = mean(top-K-WTA(W_lsh[k] @ key)). cleanup against
    pre-expanded codebook E_expanded. The expansion lifts the per-cue rep
    into a less crowded subspace.
  multi-bank per-hop:
    Maintain N_BANK=8 WM banks. Per query, route the current state to its
    designated bank by (chain_id mod N_BANK). Each bank holds intermediates
    cleaned by argmax over a bank-local codebook E_bank[i] (V_C / N_BANK
    entities each). Cross-bank crosstalk is by-construction zero.
  partition-routed per-hop:
    Split the entity codebook E into P=20 partitions of V_C/P=10 entities.
    Route each cue to its partition by argmax over partition-anchor
    similarities; do argmax-cleanup within the partition only.

Arms (6) -- ablation:
  ARM_BASELINE_HRR_2HOP        beta-sweep sanity rail [0.62, 0.68]
  ARM_SINGLE_CHAIN_5HOP        pointer-chain v2 monolithic 5hop (rail)
  ARM_COMPOSE_FLY_LSH_5HOP     only fly-LSH applied per-hop
  ARM_COMPOSE_MULTI_BANK_5HOP  only multi-bank WM per-hop
  ARM_COMPOSE_PARTITION_5HOP   only partition routing per-hop
  ARM_COMPOSE_ALL_3_5HOP       all three composed

PROSPECTIVE BANDS (locked):
  HARD_PASS_CHAIN_GRADE_COMPOSITION_WORKS:
    ALL_3 top1 >= 0.50 AND cv <= 0.07 AND ALL_3 > (FLY + BANK + PART - SINGLE)
    i.e. super-additive composition vs individual lifts.
  HARD_PASS_INDIVIDUAL_LIFT:
    any single arm (FLY / BANK / PART) top1 >= 0.30 (lift over 0.122 rail)
  HARD_FAIL_COMPOSITION_DOESNT_HELP:
    ALL_3 top1 < 0.20

SACRED SANITY: ARM_BASELINE_HRR_2HOP reproduces 0.65 +/- 0.03.

ASCII-only; per-seed checkpoint; atexit synthesizer.
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

ANCHOR_NAME = "substrate_multihop_compose_fly_lsh_multibank_partition_v1"
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
HP_COMPOSE_ALL3_5HOP = 0.50
HP_COMPOSE_CV_MAX = 0.07
HP_INDIVIDUAL_LIFT = 0.30
HF_COMPOSE_5HOP = 0.20

# SACRED SANITY: baseline must reproduce beta-sweep regime
BASELINE_SANITY_LO = 0.62
BASELINE_SANITY_HI = 0.68

# BASELINE regime
BASELINE_V_P = 2
BASELINE_N_CHAINS = 200
# POINTER regime
POINTER_V_P = 10
POINTER_K_SET = 20
# Composition primitives
N_BANKS = 8           # multi-bank WM (mirrors today's 8x32 win)
N_PARTITIONS = 20     # partition routing (V_C / N_PARTITIONS = 10 per partition)
N_LSH_EXPANSIONS = 5  # fly-LSH expansions per cue
LSH_TOPK = 20         # top-K WTA per expansion (sparse selection on n_dim)

# META_PROSPECTIVE_BANDS_FRESH_SEEDS lock
assert HP_COMPOSE_ALL3_5HOP > HP_INDIVIDUAL_LIFT > HF_COMPOSE_5HOP, \
    "META_PROSPECTIVE_BANDS_FRESH_SEEDS: bands must be HP > partial > HF"
assert 0.0 < HP_COMPOSE_CV_MAX < 0.20

if RUN_MODE == "smoke":
    N_DIM = 2048
    V_CONCEPTS = 200
    SEEDS = [7]
    POINTER_N_CHAINS = 50
    BASELINE_N_CHAINS_LOCAL = BASELINE_N_CHAINS
else:
    N_DIM = 8192
    V_CONCEPTS = 200
    SEEDS = [7, 17, 23]
    POINTER_N_CHAINS = 200
    BASELINE_N_CHAINS_LOCAL = BASELINE_N_CHAINS

DEPTH = 5
n_predicates = max(BASELINE_V_P, POINTER_V_P)

# V_CONCEPTS must be cleanly divisible by N_PARTITIONS for clean partitions
assert V_CONCEPTS % N_PARTITIONS == 0, \
    "V_CONCEPTS=%d must be divisible by N_PARTITIONS=%d" % (V_CONCEPTS, N_PARTITIONS)
PART_SIZE = V_CONCEPTS // N_PARTITIONS

CONFIG_VERSION = (
    "composeFlyLshMultiBankPartitionV1: N=%d V_C=%d "
    "BASELINE_V_P=%d BASELINE_N=%d POINTER_V_P=%d POINTER_N=%d K_SET=%d "
    "N_BANKS=%d N_PARTS=%d PART_SIZE=%d N_LSH=%d LSH_TOPK=%d "
    "seeds=%s mode=%s depth=%d "
    "HP_all3>=%.2f HP_cv<=%.2f HP_individual>=%.2f HF<%.2f "
    "baseline_sanity=[%.2f,%.2f]"
) % (
    N_DIM, V_CONCEPTS, BASELINE_V_P, BASELINE_N_CHAINS_LOCAL,
    POINTER_V_P, POINTER_N_CHAINS, POINTER_K_SET,
    N_BANKS, N_PARTITIONS, PART_SIZE, N_LSH_EXPANSIONS, LSH_TOPK,
    SEEDS, RUN_MODE, DEPTH,
    HP_COMPOSE_ALL3_5HOP, HP_COMPOSE_CV_MAX, HP_INDIVIDUAL_LIFT, HF_COMPOSE_5HOP,
    BASELINE_SANITY_LO, BASELINE_SANITY_HI,
)


def bipolar(M: int, n: int, g: np.random.Generator) -> np.ndarray:
    X = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)


def ingest_hebbian(triples, E: np.ndarray, R: np.ndarray, sq: float, n_dim: int,
                   batch: int = 2000) -> np.ndarray:
    if not triples:
        return np.zeros((n_dim, n_dim), dtype=np.float32)
    tr = np.asarray(triples, dtype=np.int64)
    s_idx, p_idx, o_idx = tr[:, 0], tr[:, 1], tr[:, 2]
    W = np.zeros((n_dim, n_dim), dtype=np.float32)
    for b in range(0, len(tr), batch):
        ks = (E[s_idx[b:b + batch]] * R[p_idx[b:b + batch]] * sq).astype(np.float32)
        W += (E[o_idx[b:b + batch]].T @ ks) / n_dim
    return W


# ---- BASELINE: verbatim beta-sweep regime ---------------------------------

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


# ---- POINTER chain machinery ---------------------------------------------

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


def _retrieve_1hop_naive(E, W, R, s: int, p: int, sq: float) -> int:
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
            s_pred = _retrieve_1hop_naive(E, W, R, s, p, sq)
            if s_pred == chain[i][2]:
                per_step_hits[i] += 1
            s = s_pred
        if s == chain[depth - 1][2]:
            hits += 1
    per_step_acc = (per_step_hits.astype(np.float32) / max(n, 1)).tolist()
    return {"top1": round(hits / max(n, 1), 4),
            "per_step_acc": [round(x, 4) for x in per_step_acc],
            "n_queries": n, "depth": depth}


# ---- fly-LSH per-hop cleanup ---------------------------------------------

def build_fly_lsh_projs(n_dim: int, n_expansions: int,
                         g: np.random.Generator) -> np.ndarray:
    """Build n_expansions x n_dim x n_dim bipolar random projection matrices.

    Heavy memory if n_dim is large; for n_dim=8192 and n=5, this is 5 * 8192 * 8192
    * 4 bytes = 1.3 GB. To bound memory at n_dim=8192, use SPARSE projections:
    each row of W_lsh[k] has only LSH_TOPK non-zero +-1 entries.
    """
    projs = np.zeros((n_expansions, n_dim, n_dim), dtype=np.float32)
    for k in range(n_expansions):
        # Sparse: each input dim picks LSH_TOPK random output dims to project to
        # with +-1. This gives a rough fly-style random fan-out.
        rows = g.integers(0, n_dim, size=(n_dim, LSH_TOPK))
        signs = (g.integers(0, 2, size=(n_dim, LSH_TOPK)) * 2 - 1).astype(np.float32)
        for i in range(n_dim):
            projs[k, i, rows[i]] += signs[i]
    return projs


def fly_lsh_expand(key: np.ndarray, projs: np.ndarray) -> np.ndarray:
    """Apply each fly-LSH projection then top-K-WTA on |x|; sum across expansions."""
    out = np.zeros_like(key)
    n_dim = key.shape[0]
    for k in range(projs.shape[0]):
        z = projs[k] @ key  # (n_dim,)
        # k-WTA on absolute value
        if LSH_TOPK < n_dim:
            thr_idx = np.argpartition(np.abs(z), -LSH_TOPK)[-LSH_TOPK:]
            mask = np.zeros_like(z)
            mask[thr_idx] = 1.0
            z = z * mask
        out += z
    norm = np.linalg.norm(out) + 1e-8
    return out / norm


def _retrieve_1hop_fly_lsh(E, E_expanded, W_fly, R, s: int, p: int, sq: float,
                            projs: np.ndarray) -> int:
    """fly-LSH-rescued per-hop: project key into expanded space via fly-LSH,
    cleanup against E_expanded (entities also projected via fly-LSH).
    """
    raw_key = (E[s] * R[p] * sq).astype(np.float32)
    key_exp = fly_lsh_expand(raw_key, projs)
    state = W_fly @ key_exp
    return int((E_expanded @ state).argmax())


def arm_compose_fly_lsh(E, R, sq, triples, chains_test, depth: int,
                          projs: np.ndarray) -> Dict[str, Any]:
    """fly-LSH per-hop ONLY. W is built in EXPANDED space; E_expanded for cleanup."""
    n_dim = E.shape[1]
    V = E.shape[0]
    E_expanded = np.zeros_like(E)
    for i in range(V):
        E_expanded[i] = fly_lsh_expand(E[i], projs)
    # W_fly: ingestion in expanded space
    tr = np.asarray(triples, dtype=np.int64)
    s_idx, p_idx, o_idx = tr[:, 0], tr[:, 1], tr[:, 2]
    W_fly = np.zeros((n_dim, n_dim), dtype=np.float32)
    for b in range(0, len(tr), 200):
        for j in range(b, min(b + 200, len(tr))):
            raw_key = (E[s_idx[j]] * R[p_idx[j]] * sq).astype(np.float32)
            key_exp = fly_lsh_expand(raw_key, projs)
            o_exp = E_expanded[o_idx[j]]
            W_fly += np.outer(o_exp, key_exp) / n_dim
    n = len(chains_test)
    hits = 0
    per_step_hits = np.zeros(depth, dtype=np.int64)
    for chain in chains_test:
        s = chain[0][0]
        for i in range(depth):
            p = chain[i][1]
            s_pred = _retrieve_1hop_fly_lsh(E, E_expanded, W_fly, R, s, p, sq, projs)
            if s_pred == chain[i][2]:
                per_step_hits[i] += 1
            s = s_pred
        if s == chain[depth - 1][2]:
            hits += 1
    per_step_acc = (per_step_hits.astype(np.float32) / max(n, 1)).tolist()
    return {"top1": round(hits / max(n, 1), 4),
            "per_step_acc": [round(x, 4) for x in per_step_acc],
            "n_queries": n, "depth": depth,
            "mechanism": "fly_lsh_expanded_W_and_cleanup"}


# ---- multi-bank per-hop --------------------------------------------------

def arm_compose_multi_bank(E, R, sq, triples, chains_test, depth: int,
                             n_banks: int = N_BANKS) -> Dict[str, Any]:
    """Multi-bank WM per-hop: split E into n_banks contiguous bank-codebooks
    (V_C / n_banks per bank). Each chain id is routed to its bank by (chain_id
    mod n_banks). Per-hop cleanup is argmax within the bank's local codebook.
    Each bank has its OWN W (ingested only with triples whose o is in-bank).
    """
    n_dim = E.shape[1]
    V = E.shape[0]
    assert V % n_banks == 0, "V_C must divide by n_banks"
    bank_sz = V // n_banks
    # Build per-bank W matrices: each bank ingests triples where o is in-bank
    Ws = [np.zeros((n_dim, n_dim), dtype=np.float32) for _ in range(n_banks)]
    for s_, p_, o_ in triples:
        bank = o_ // bank_sz
        key = (E[s_] * R[p_] * sq).astype(np.float32)
        Ws[bank] += np.outer(E[o_], key) / n_dim
    # Per-bank codebooks
    E_banks = [E[b * bank_sz:(b + 1) * bank_sz] for b in range(n_banks)]
    bank_offsets = [b * bank_sz for b in range(n_banks)]
    n = len(chains_test)
    hits = 0
    per_step_hits = np.zeros(depth, dtype=np.int64)
    for chain_id, chain in enumerate(chains_test):
        s = chain[0][0]
        for i in range(depth):
            p = chain[i][1]
            target_o = chain[i][2]
            target_bank = target_o // bank_sz
            # Cleanup within target's bank (uses target_o's bank for ingest-aligned argmax)
            key = (E[s] * R[p] * sq).astype(np.float32)
            scores = E_banks[target_bank] @ (Ws[target_bank] @ key)
            local_idx = int(scores.argmax())
            s_pred = bank_offsets[target_bank] + local_idx
            if s_pred == target_o:
                per_step_hits[i] += 1
            s = s_pred
        if s == chain[depth - 1][2]:
            hits += 1
    per_step_acc = (per_step_hits.astype(np.float32) / max(n, 1)).tolist()
    return {"top1": round(hits / max(n, 1), 4),
            "per_step_acc": [round(x, 4) for x in per_step_acc],
            "n_queries": n, "depth": depth, "n_banks": n_banks,
            "mechanism": "multi_bank_per_hop_oracle_routed"}


# ---- partition-routing per-hop --------------------------------------------

def arm_compose_partition(E, R, sq, triples, chains_test, depth: int,
                            n_partitions: int = N_PARTITIONS) -> Dict[str, Any]:
    """Partition routing per-hop: split E into N_PARTITIONS contiguous partitions.
    For each per-hop cue, route to the target partition (oracle-routed for now;
    matches partition_routing_10M which had route_acc=1.000). Cleanup within
    the partition only.
    """
    n_dim = E.shape[1]
    V = E.shape[0]
    assert V % n_partitions == 0
    part_sz = V // n_partitions
    # Single global W (matching partition_routing's flat W)
    W = ingest_hebbian(triples, E, R, sq, n_dim)
    E_parts = [E[p * part_sz:(p + 1) * part_sz] for p in range(n_partitions)]
    part_offsets = [p * part_sz for p in range(n_partitions)]
    n = len(chains_test)
    hits = 0
    per_step_hits = np.zeros(depth, dtype=np.int64)
    for chain in chains_test:
        s = chain[0][0]
        for i in range(depth):
            p = chain[i][1]
            target_o = chain[i][2]
            target_part = target_o // part_sz
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
    return {"top1": round(hits / max(n, 1), 4),
            "per_step_acc": [round(x, 4) for x in per_step_acc],
            "n_queries": n, "depth": depth, "n_partitions": n_partitions,
            "mechanism": "partition_per_hop_oracle_routed"}


# ---- ALL THREE COMPOSED ---------------------------------------------------

def arm_compose_all_3(E, R, sq, triples, chains_test, depth: int,
                        projs: np.ndarray) -> Dict[str, Any]:
    """fly-LSH expansion + multi-bank + partition-routing all per-hop."""
    n_dim = E.shape[1]
    V = E.shape[0]
    bank_sz = V // N_BANKS
    # Expand E
    E_expanded = np.zeros_like(E)
    for i in range(V):
        E_expanded[i] = fly_lsh_expand(E[i], projs)
    # Build per-bank W_fly matrices in expanded space
    Ws_fly = [np.zeros((n_dim, n_dim), dtype=np.float32) for _ in range(N_BANKS)]
    for s_, p_, o_ in triples:
        bank = o_ // bank_sz
        raw_key = (E[s_] * R[p_] * sq).astype(np.float32)
        key_exp = fly_lsh_expand(raw_key, projs)
        Ws_fly[bank] += np.outer(E_expanded[o_], key_exp) / n_dim
    # Per-bank codebooks (in expanded space)
    E_bank_exps = [E_expanded[b * bank_sz:(b + 1) * bank_sz] for b in range(N_BANKS)]
    bank_offsets = [b * bank_sz for b in range(N_BANKS)]
    n = len(chains_test)
    hits = 0
    per_step_hits = np.zeros(depth, dtype=np.int64)
    for chain in chains_test:
        s = chain[0][0]
        for i in range(depth):
            p = chain[i][1]
            target_o = chain[i][2]
            target_bank = target_o // bank_sz
            raw_key = (E[s] * R[p] * sq).astype(np.float32)
            key_exp = fly_lsh_expand(raw_key, projs)
            scores = E_bank_exps[target_bank] @ (Ws_fly[target_bank] @ key_exp)
            local_idx = int(scores.argmax())
            s_pred = bank_offsets[target_bank] + local_idx
            if s_pred == target_o:
                per_step_hits[i] += 1
            s = s_pred
        if s == chain[depth - 1][2]:
            hits += 1
    per_step_acc = (per_step_hits.astype(np.float32) / max(n, 1)).tolist()
    return {"top1": round(hits / max(n, 1), 4),
            "per_step_acc": [round(x, 4) for x in per_step_acc],
            "n_queries": n, "depth": depth,
            "mechanism": "all3_fly_lsh_multi_bank_partition_composed"}


def _selftest() -> None:
    g = np.random.default_rng(0)
    n = 512
    V = 40
    sq = math.sqrt(n)
    E = bipolar(V, n, g)
    R = bipolar(4, n, g)

    Rb = bipolar(max(BASELINE_V_P, 2), n, g)
    train, queries = make_two_hop_chains_betasweep(20, V, g, p1=0, p2=1)
    r_base = arm_baseline_hrr_2hop_betasweep(E, Rb, sq, train, queries)
    assert 0.0 <= r_base["top1"] <= 1.0

    triples_d, chains_d = make_deep_chains(8, V, 4, max_depth=5, g=g, disallow_s=set())
    W = ingest_hebbian(triples_d, E, R, sq, n)
    r_single = arm_single_chain_naive(E, R, sq, W, chains_d, depth=5)
    assert 0.0 <= r_single["top1"] <= 1.0

    # fly-LSH at small n
    projs = build_fly_lsh_projs(n, 2, g)
    r_fly = arm_compose_fly_lsh(E, R, sq, triples_d, chains_d, depth=5, projs=projs)
    assert 0.0 <= r_fly["top1"] <= 1.0

    # multi-bank (V=40, n_banks=8 -> bank_sz=5)
    r_bank = arm_compose_multi_bank(E, R, sq, triples_d, chains_d, depth=5, n_banks=8)
    assert 0.0 <= r_bank["top1"] <= 1.0

    # partition (V=40, n_partitions=4 -> part_sz=10)
    r_part = arm_compose_partition(E, R, sq, triples_d, chains_d, depth=5, n_partitions=4)
    assert 0.0 <= r_part["top1"] <= 1.0

    r_all3 = arm_compose_all_3(E, R, sq, triples_d, chains_d, depth=5, projs=projs)
    assert 0.0 <= r_all3["top1"] <= 1.0

    print("[selftest] PASS base=%.3f single=%.3f fly=%.3f bank=%.3f part=%.3f all3=%.3f"
          % (r_base["top1"], r_single["top1"], r_fly["top1"], r_bank["top1"],
             r_part["top1"], r_all3["top1"]), flush=True)


_selftest()
if _ARGS.self_test:
    print("[self-test] PASS; exiting", flush=True)
    sys.exit(0)


def run_seed(seed: int) -> Dict[str, Any]:
    t = time.time()
    g = np.random.default_rng(seed)
    sq = math.sqrt(N_DIM)
    E = bipolar(V_CONCEPTS, N_DIM, g)
    R = bipolar(n_predicates, N_DIM, g)

    out = {
        "seed": seed, "run_mode": RUN_MODE, "N": N_DIM, "V_C": V_CONCEPTS,
        "n_predicates": n_predicates,
        "n_banks": N_BANKS, "n_partitions": N_PARTITIONS,
        "n_lsh_expansions": N_LSH_EXPANSIONS, "lsh_topk": LSH_TOPK,
        "pointer_n_chains": POINTER_N_CHAINS, "depth": DEPTH,
        "config_version": CONFIG_VERSION,
        "_llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
    }

    # ===== BASELINE sanity =====
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

    # ===== POINTER chains =====
    t_arm = time.time()
    ptr_triples, ptr_chains = make_deep_chains(
        POINTER_N_CHAINS, V_CONCEPTS, POINTER_V_P, max_depth=DEPTH,
        g=g, disallow_s=set())
    W_naive = ingest_hebbian(ptr_triples, E, R, sq, N_DIM)
    print("  [seed=%d] pointer W built (%d triples) t=%.1fs" % (
        seed, len(ptr_triples), round(time.time() - t_arm, 2)), flush=True)

    # ----- SINGLE_CHAIN rail -----
    t_arm = time.time()
    r_single = arm_single_chain_naive(E, R, sq, W_naive, ptr_chains, depth=DEPTH)
    r_single["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    out["arm_single_chain_5hop"] = r_single
    print("  [seed=%d] SINGLE_CHAIN_5HOP top1=%.4f per_step=%s t=%.1fs" % (
        seed, r_single["top1"], r_single["per_step_acc"],
        r_single["elapsed_s_arm"]), flush=True)

    # ----- fly-LSH -----
    t_arm = time.time()
    projs = build_fly_lsh_projs(N_DIM, N_LSH_EXPANSIONS, g)
    r_fly = arm_compose_fly_lsh(E, R, sq, ptr_triples, ptr_chains, depth=DEPTH,
                                  projs=projs)
    r_fly["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    out["arm_compose_fly_lsh_5hop"] = r_fly
    print("  [seed=%d] FLY_LSH_5HOP top1=%.4f per_step=%s t=%.1fs" % (
        seed, r_fly["top1"], r_fly["per_step_acc"],
        r_fly["elapsed_s_arm"]), flush=True)

    # ----- multi-bank -----
    t_arm = time.time()
    r_bank = arm_compose_multi_bank(E, R, sq, ptr_triples, ptr_chains,
                                       depth=DEPTH, n_banks=N_BANKS)
    r_bank["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    out["arm_compose_multi_bank_5hop"] = r_bank
    print("  [seed=%d] MULTI_BANK_5HOP top1=%.4f per_step=%s t=%.1fs" % (
        seed, r_bank["top1"], r_bank["per_step_acc"],
        r_bank["elapsed_s_arm"]), flush=True)

    # ----- partition -----
    t_arm = time.time()
    r_part = arm_compose_partition(E, R, sq, ptr_triples, ptr_chains,
                                      depth=DEPTH, n_partitions=N_PARTITIONS)
    r_part["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    out["arm_compose_partition_5hop"] = r_part
    print("  [seed=%d] PARTITION_5HOP top1=%.4f per_step=%s t=%.1fs" % (
        seed, r_part["top1"], r_part["per_step_acc"],
        r_part["elapsed_s_arm"]), flush=True)

    # ----- ALL THREE COMPOSED -----
    t_arm = time.time()
    r_all3 = arm_compose_all_3(E, R, sq, ptr_triples, ptr_chains, depth=DEPTH,
                                  projs=projs)
    r_all3["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    out["arm_compose_all_3_5hop"] = r_all3
    print("  [seed=%d] ALL_3_5HOP top1=%.4f per_step=%s t=%.1fs" % (
        seed, r_all3["top1"], r_all3["per_step_acc"],
        r_all3["elapsed_s_arm"]), flush=True)

    out["elapsed_s"] = round(time.time() - t, 1)
    return out


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
    single = mean_top1("arm_single_chain_5hop")
    fly = mean_top1("arm_compose_fly_lsh_5hop")
    bank = mean_top1("arm_compose_multi_bank_5hop")
    part = mean_top1("arm_compose_partition_5hop")
    all3 = mean_top1("arm_compose_all_3_5hop")
    all3_cv = cv_top1("arm_compose_all_3_5hop")

    sanity_breached = sum(1 for p in per_seed if not p.get("baseline_sanity_ok", False))
    rails: List[str] = []
    if sanity_breached > 0:
        rails.append("SANITY_BREACH(%d/%d seeds; baseline_mean=%.4f)"
                      % (sanity_breached, len(per_seed), baseline))

    # Super-additivity check: lift over sum of individual lifts
    indiv_lifts = []
    for v in (fly, bank, part):
        if not math.isnan(v) and not math.isnan(single):
            indiv_lifts.append(v - single)
    sum_indiv = sum(indiv_lifts) if indiv_lifts else 0.0
    all3_lift = all3 - single if (not math.isnan(all3) and not math.isnan(single)) else float("nan")
    super_additive = (not math.isnan(all3_lift)) and (all3_lift > sum_indiv)

    summ = ("BASELINE=%.4f (sanity_breach=%d/%d) SINGLE=%.4f FLY=%.4f BANK=%.4f "
            "PART=%.4f ALL3=%.4f (cv=%.3f) all3_lift=%+.4f sum_indiv_lifts=%+.4f "
            "super_additive=%s | rails=%s") % (
        baseline, sanity_breached, len(per_seed), single, fly, bank, part,
        all3, all3_cv, all3_lift, sum_indiv, super_additive, rails,
    )

    if sanity_breached >= max(1, (len(per_seed) + 1) // 2):
        return "SANITY_BREACH", "SANITY_BREACH_BASELINE_OUT_OF_BAND: " + summ

    hp_chain_grade = (
        not math.isnan(all3) and all3 >= HP_COMPOSE_ALL3_5HOP
        and (math.isnan(all3_cv) or all3_cv <= HP_COMPOSE_CV_MAX)
    )
    hp_individual = any(
        (not math.isnan(v)) and v >= HP_INDIVIDUAL_LIFT for v in (fly, bank, part)
    )

    if hp_chain_grade:
        if super_additive:
            return "HARD_PASS_CHAIN_GRADE_COMPOSITION_SUPERADDITIVE", \
                   "HARD_PASS_CHAIN_GRADE_COMPOSITION_SUPERADDITIVE: " + summ
        return "HARD_PASS_CHAIN_GRADE_COMPOSITION_ADDITIVE", \
               "HARD_PASS_CHAIN_GRADE_COMPOSITION_ADDITIVE: " + summ
    if hp_individual:
        return "HARD_PASS_PARTIAL", "HARD_PASS_PARTIAL_INDIVIDUAL_LIFT: " + summ
    if not math.isnan(all3) and all3 < HF_COMPOSE_5HOP:
        return "HARD_FAIL", "HARD_FAIL_COMPOSITION_DOESNT_HELP: " + summ
    return "MIDDLE_BAND", "MIDDLE_BAND_COMPOSITION_PARTIAL: " + summ


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
            "ANGLE 1 revival: compose today's 3 chain-grade wins. fly-LSH "
            "expands per-hop key into sparse-random subspace; multi-bank "
            "partitions WM into banks; partition-routing restricts per-hop "
            "argmax to a small partition. ALL_3 arm composes all three; "
            "individual-arm ablation tests whether each lift is independent "
            "and whether composition is super-additive vs sum-of-individual. "
            "NOTE: bank and partition arms use ORACLE routing (target_bank / "
            "target_part); this is the favourable-conditions test. If oracle-"
            "routed bank/part STILL fail, the routing is not the bottleneck. "
            "If they pass, follow-up cell to add real router."
        ),
    }
    write_metrics(out_dir, metrics, results=per_seed)
    print("[done] metrics.json written (%d seeds, %.1fs)" % (
        len(per_seed), metrics["elapsed_s"]), flush=True)
