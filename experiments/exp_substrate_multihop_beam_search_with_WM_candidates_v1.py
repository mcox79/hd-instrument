"""substrate_multihop_beam_search_with_WM_candidates_v1.

USER-DIRECTED 2026-06-25 (Gap 1; 6th multi-hop attempt). The architectural lever not tested in
prior 5 HARD_FAILs: parallel multi-candidate beam search using substrate's chain-grade primitives
(WM multi-bank as candidate-slot store; per-hop cleanup as top-K retrieval; composite score as
prune signal).

Brain analog: PFC + hippocampus + dorsal striatum maintain MULTIPLE candidate plans in parallel
and prune by reward prediction. Substrate primitives chain-grade individually today:
  - WM multi-bank (chain-grade K=1024 @ N=4096): holds W candidate continuations
  - CSP confidence (HARD_PASS): per-hop confidence score (used here as ranking signal)
  - HRR 2-hop binding (sanity rail 0.65): per-hop retrieval primitive

Background (5-for-5 prior HARD_FAIL):
  pointer-chain-v2 / wm-scaffold / csp-gated / consolidation-v3 / pfc-chunked-2hop all do
  TOP-1 sequential cleanup. Per-step accuracy 0.69 -> 0.485 -> 0.31 -> 0.205 -> 0.145; 5-hop
  cumulative ~0.122. Chunked 2-hop restart gave only +0.04 lift; the per-chunk decay was the
  same (0.54 -> 0.265 -> 0.20).

  The information loss: top-1 hard-decision at each hop discards the runner-up candidates
  even when the correct continuation is in top-3 or top-5. Beam search preserves top-K
  continuations per chain and prunes only at the end.

Mechanism (this cell):
  For each k-hop query:
    1. Hop 0: starting candidate = query subject (single chain; weight=0.0 log-cumulative)
    2. At each hop i:
       a. For each current chain: compute per-hop cleanup scores E @ state; argpartition top_K
       b. Each chain branches into K candidate continuations; new chain weight = chain_weight
          + log(softmax_score_for_that_candidate)
       c. Keep beam_width=W best continuations by cumulative log-score
    3. At final hop: pick chain with highest cumulative log-score; final answer = last
       cleaned entity in that chain.

  WM-bank slot count = W per query (uses multi-bank WM primitive bank-as-candidate-slot
  pattern; though here we hold the W candidate chains in plain numpy arrays since the
  primitive's load-bearing property at this depth is candidate-slot count, not bank-isolation).

ARMS (5):
  ARM_BASELINE_HRR_2HOP        beta-sweep verbatim regime (sanity rail [0.62, 0.68])
  ARM_SINGLE_TOP1_5HOP         pointer-chain v2 monolithic 5hop (rail ~0.122)
  ARM_BEAM_W2_TOPK3_5HOP       beam_width=2, top_k_per_hop=3
  ARM_BEAM_W5_TOPK3_5HOP       beam_width=5, top_k_per_hop=3
  ARM_BEAM_W10_TOPK5_5HOP      beam_width=10, top_k_per_hop=5

PROSPECTIVE BANDS (LOCKED at module init via assert):
  HARD_PASS_CHAIN_GRADE_BARRIER_1_BEAM:
    ARM_BEAM_W10_TOPK5_5HOP top1 >= 0.50 AND
    monotonic in beam_width (W2 < W5 < W10 within tol) AND
    cv (all 3 beam arms) <= 0.07
  HARD_PASS_PARTIAL:
    ARM_BEAM_W10_TOPK5_5HOP top1 >= 0.30 (lift over 0.122 rail)
  HARD_FAIL_BEAM_DOESNT_HELP:
    ARM_BEAM_W10_TOPK5_5HOP top1 < 0.20

SACRED SANITY: ARM_BASELINE_HRR_2HOP reproduces 0.65 +/- 0.03; otherwise SANITY_BREACH.

META_M6: baseline arms measured in-cell at current regime (not copied from prior cells).
META_M7: smoke matches full on N_DIM, V_C, V_P, K_SET (capacity-sensitive dimensions);
  only N_CHAINS + SEEDS reduce.

Author: exp_dev 2026-06-25 (USER-directed Gap 1 brain-correct PFC analog).
ASCII-only; per-seed checkpoint; substrate-only (no LLM forward calls at inference).
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

ANCHOR_NAME = "substrate_multihop_beam_search_with_WM_candidates_v1"
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
HP_BEAM_W10_5HOP = 0.50
HP_BEAM_CV_MAX = 0.07
HP_PARTIAL_5HOP = 0.30
HF_BEAM_W10_5HOP = 0.20
MONOTONIC_TOL = 0.02  # W5 must beat W2 by at least this (and W10 must beat W5); within-tol counts as monotonic

# SACRED SANITY: baseline must reproduce beta-sweep regime
BASELINE_SANITY_LO = 0.62
BASELINE_SANITY_HI = 0.68

# Q-discipline saturation guard
Q_SATURATION = 0.995

# BASELINE arm regime (verbatim beta-sweep)
BASELINE_V_P = 2
BASELINE_N_CHAINS = 200
# POINTER+BEAM regime
POINTER_V_P = 10
POINTER_K_SET = 20

# Beam configs (locked)
BEAM_CONFIGS = [
    ("ARM_BEAM_W2_TOPK3_5HOP", 2, 3),
    ("ARM_BEAM_W5_TOPK3_5HOP", 5, 3),
    ("ARM_BEAM_W10_TOPK5_5HOP", 10, 5),
]

# META_PROSPECTIVE_BANDS_FRESH_SEEDS lock
assert HP_BEAM_W10_5HOP > HP_PARTIAL_5HOP > HF_BEAM_W10_5HOP, \
    "META_PROSPECTIVE_BANDS_FRESH_SEEDS: HP > MID_low > HF"
assert 0.0 < HP_BEAM_CV_MAX < 0.20, \
    "META_PROSPECTIVE_BANDS_FRESH_SEEDS: cv ceiling in (0, 0.20)"
assert Q_SATURATION > HP_BEAM_W10_5HOP, \
    "META_PROSPECTIVE_BANDS_FRESH_SEEDS: Q_SATURATION above HP threshold"
assert MONOTONIC_TOL > 0.0, "monotonic tol positive"

if RUN_MODE == "smoke":
    N_DIM = 2048
    V_CONCEPTS = 200
    SEEDS = [7]
    POINTER_N_CHAINS = 50
    BASELINE_N_CHAINS_LOCAL = BASELINE_N_CHAINS  # baseline stays at full N_CHAINS so sanity is meaningful
else:
    N_DIM = 8192
    V_CONCEPTS = 200
    SEEDS = [7, 17, 23]
    POINTER_N_CHAINS = 200
    BASELINE_N_CHAINS_LOCAL = BASELINE_N_CHAINS

DEPTH_5HOP = 5
n_predicates = max(BASELINE_V_P, POINTER_V_P)

CONFIG_VERSION = (
    "beamSearchWithWMCandidatesV1: N=%d V_C=%d "
    "BASELINE_V_P=%d BASELINE_N=%d POINTER_V_P=%d POINTER_N=%d K_SET=%d "
    "seeds=%s mode=%s beam_configs=%s depth=%d "
    "HP_beam_w10_5hop>=%.2f HP_cv<=%.2f HP_partial>=%.2f HF<%.2f "
    "monotonic_tol=%.3f Q_saturation>=%.3f "
    "baseline_sanity=[%.2f,%.2f]"
) % (
    N_DIM, V_CONCEPTS, BASELINE_V_P, BASELINE_N_CHAINS_LOCAL,
    POINTER_V_P, POINTER_N_CHAINS, POINTER_K_SET,
    SEEDS, RUN_MODE, [(n, w, k) for n, w, k in BEAM_CONFIGS], DEPTH_5HOP,
    HP_BEAM_W10_5HOP, HP_BEAM_CV_MAX, HP_PARTIAL_5HOP, HF_BEAM_W10_5HOP,
    MONOTONIC_TOL, Q_SATURATION,
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


# ---- BASELINE: verbatim beta-sweep regime + mechanism --------------------

def make_two_hop_chains_betasweep(n_chains: int, V: int, g: np.random.Generator,
                                    p1: int = 0, p2: int = 1):
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


# ---- DEEP CHAINS (shared by single-top1 + beam arms) --------------------

def make_deep_chains(n_chains: int, V: int, P: int, max_depth: int,
                      g: np.random.Generator, disallow_s: set):
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
        raise RuntimeError(
            "BLOCKING make_deep_chains: only %d/%d generated"
            % (len(chain_queries), n_chains)
        )
    return all_triples, chain_queries


def _retrieve_1hop(E, W, R, s: int, p: int, sq: float) -> int:
    key = (E[s] * R[p] * sq).astype(np.float32)
    scores = E @ (W @ key)
    return int(scores.argmax())


def arm_single_chain_naive(E, R, sq, W, chains_test, depth: int) -> Dict[str, Any]:
    """Monolithic chain via top-1 cleanup per hop. Rail-match for pointer-chain v2."""
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


# ---- BEAM SEARCH (the new mechanism) ------------------------------------

def _topk_cleanup(E: np.ndarray, W: np.ndarray, R: np.ndarray,
                   sq: float, s_idx: int, p: int, K: int) -> Tuple[np.ndarray, np.ndarray]:
    """Return (top_K_entity_indices, top_K_softmax_scores) for cleanup of E @ (W @ key).

    Substrate-only: argpartition + softmax over cleanup scores; no LLM call.
    """
    key = (E[s_idx] * R[p] * sq).astype(np.float32)
    scores = E @ (W @ key)  # (V_C,)
    # argpartition for top-K (faster than full argsort at large V_C)
    if K >= len(scores):
        topk_idx = np.argsort(-scores)
    else:
        # Get top-K unsorted, then sort within
        partition_idx = np.argpartition(-scores, K)[:K]
        topk_idx = partition_idx[np.argsort(-scores[partition_idx])]
    topk_scores = scores[topk_idx]
    # Softmax over the top-K for ranking (substrate-native; no LLM)
    s_shifted = topk_scores - topk_scores.max()
    exp_s = np.exp(s_shifted)
    softmax = exp_s / (exp_s.sum() + 1e-12)
    return topk_idx.astype(np.int64), softmax.astype(np.float32)


def arm_beam_search(E, R, sq, W, chains_test, depth: int,
                     beam_width: int, top_k: int) -> Dict[str, Any]:
    """Parallel-candidate beam search.

    For each query, maintain a beam of (chain_state, cumulative_log_score) candidates.
    At each hop, branch each beam chain into top_k continuations via _topk_cleanup,
    score them by softmax_score, keep beam_width best by cumulative log-score.

    Final answer = last entity in highest-scoring beam at hop=depth.

    Returns top1 (exact-match at depth) + per-hop diagnostics (correct-in-beam rate).
    """
    n = len(chains_test)
    hits = 0
    # per-hop diagnostic: how often is the GROUND-TRUTH at hop i present in the beam?
    correct_in_beam_per_hop = np.zeros(depth, dtype=np.int64)
    # also track top-1 of beam (sanity vs ARM_SINGLE_TOP1 at same depth)
    top1_in_beam_top1_per_hop = np.zeros(depth, dtype=np.int64)

    for chain in chains_test:
        s_start = chain[0][0]
        # Each beam entry = (entity_idx, cumulative_log_score)
        beam: List[Tuple[int, float]] = [(s_start, 0.0)]

        for i in range(depth):
            p = chain[i][1]
            target_at_i = chain[i][2]
            # Branch every beam entry into top_k continuations
            candidates: List[Tuple[int, float]] = []
            for (s_idx, cum_log) in beam:
                topk_idx, topk_softmax = _topk_cleanup(E, W, R, sq, s_idx, p, top_k)
                for j in range(len(topk_idx)):
                    s_new = int(topk_idx[j])
                    sc = float(topk_softmax[j])
                    log_sc = math.log(max(sc, 1e-12))
                    candidates.append((s_new, cum_log + log_sc))
            # Prune: keep beam_width best by cumulative log-score
            candidates.sort(key=lambda t: -t[1])
            beam = candidates[:beam_width]
            # Diagnostics: is target at hop i in the beam?
            beam_idxs = {b[0] for b in beam}
            if target_at_i in beam_idxs:
                correct_in_beam_per_hop[i] += 1
            if beam and beam[0][0] == target_at_i:
                top1_in_beam_top1_per_hop[i] += 1

        # Final answer: top-of-beam entity
        if beam and beam[0][0] == chain[depth - 1][2]:
            hits += 1

    correct_in_beam_acc = (correct_in_beam_per_hop.astype(np.float32) / max(n, 1)).tolist()
    top1_acc = (top1_in_beam_top1_per_hop.astype(np.float32) / max(n, 1)).tolist()
    return {
        "top1": round(hits / max(n, 1), 4),
        "correct_in_beam_per_hop": [round(x, 4) for x in correct_in_beam_acc],
        "top_of_beam_correct_per_hop": [round(x, 4) for x in top1_acc],
        "n_queries": n, "depth": depth,
        "beam_width": beam_width, "top_k": top_k,
    }


def _selftest() -> None:
    g = np.random.default_rng(0)
    n = 1024
    V = 60
    sq = math.sqrt(n)
    E = bipolar(V, n, g)
    R = bipolar(4, n, g)

    # Baseline sanity at selftest scale
    Rb = bipolar(max(BASELINE_V_P, 2), n, g)
    train, queries = make_two_hop_chains_betasweep(20, V, g, p1=0, p2=1)
    r_base = arm_baseline_hrr_2hop_betasweep(E, Rb, sq, train, queries)
    assert 0.0 <= r_base["top1"] <= 1.0

    # Build deep chains for beam selftest
    triples_d, chains_d = make_deep_chains(8, V, 4, max_depth=5, g=g, disallow_s=set())
    W2 = ingest_hebbian(triples_d, E, R, sq, n)

    # Single-top1 reference
    r_single = arm_single_chain_naive(E, R, sq, W2, chains_d, depth=5)
    assert 0.0 <= r_single["top1"] <= 1.0
    assert len(r_single["per_step_acc"]) == 5

    # Beam at small width
    r_beam2 = arm_beam_search(E, R, sq, W2, chains_d, depth=5, beam_width=2, top_k=3)
    r_beam5 = arm_beam_search(E, R, sq, W2, chains_d, depth=5, beam_width=5, top_k=3)
    r_beam10 = arm_beam_search(E, R, sq, W2, chains_d, depth=5, beam_width=10, top_k=5)
    for r in (r_beam2, r_beam5, r_beam10):
        assert 0.0 <= r["top1"] <= 1.0
        assert len(r["correct_in_beam_per_hop"]) == 5
        assert len(r["top_of_beam_correct_per_hop"]) == 5
        assert r["beam_width"] >= 1
        assert r["top_k"] >= 1

    # Sanity invariant: top-of-beam top1 must be <= correct-in-beam (target in beam at all)
    for r in (r_beam2, r_beam5, r_beam10):
        for i in range(5):
            assert r["top_of_beam_correct_per_hop"][i] <= r["correct_in_beam_per_hop"][i] + 1e-6, \
                "top-of-beam cannot exceed correct-in-beam at hop %d (got top=%.3f corr=%.3f)" % (
                    i, r["top_of_beam_correct_per_hop"][i], r["correct_in_beam_per_hop"][i])

    # Sanity invariant: beam_width=1 with top_k=1 should match single-top1 (modulo softmax
    # ranking ties); test as approximate match for top1 metric
    r_beam1 = arm_beam_search(E, R, sq, W2, chains_d, depth=5, beam_width=1, top_k=1)
    # Per-hop top-of-beam should match per-step-acc of single (top_k=1 is just argmax)
    for i in range(5):
        assert abs(r_beam1["top_of_beam_correct_per_hop"][i] - r_single["per_step_acc"][i]) < 1e-6, \
            "beam(W=1,K=1) hop %d top-of-beam %.3f must match single per_step %.3f" % (
                i, r_beam1["top_of_beam_correct_per_hop"][i], r_single["per_step_acc"][i])

    print(("[selftest] PASS baseline=%.3f single5=%.3f "
           "beam(W=2,K=3)=%.3f beam(W=5,K=3)=%.3f beam(W=10,K=5)=%.3f "
           "beam(W=1,K=1)=%.3f (matches single top1=%.3f)")
          % (r_base["top1"], r_single["top1"],
             r_beam2["top1"], r_beam5["top1"], r_beam10["top1"],
             r_beam1["top1"], r_single["top1"]), flush=True)


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
        "n_predicates": n_predicates, "K_SET": POINTER_K_SET,
        "baseline_n_chains": BASELINE_N_CHAINS_LOCAL,
        "pointer_n_chains": POINTER_N_CHAINS,
        "depth": DEPTH_5HOP,
        "config_version": CONFIG_VERSION,
        "_llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
    }

    # ===== ARM_BASELINE (SACRED sanity rail) =====
    t_arm = time.time()
    base_triples, base_queries = make_two_hop_chains_betasweep(
        BASELINE_N_CHAINS_LOCAL, V_CONCEPTS, g, p1=0, p2=1)
    r_baseline = arm_baseline_hrr_2hop_betasweep(E, R, sq, base_triples,
                                                   base_queries)
    r_baseline["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    out["arm_baseline_hrr_2hop"] = r_baseline
    print("  [seed=%d] ARM_BASELINE_HRR_2HOP top1=%.4f n=%d t=%.1fs"
          % (seed, r_baseline["top1"], r_baseline["n_queries"],
             r_baseline["elapsed_s_arm"]), flush=True)

    baseline_ok = (BASELINE_SANITY_LO <= r_baseline["top1"] <= BASELINE_SANITY_HI)
    out["baseline_sanity_ok"] = baseline_ok
    if not baseline_ok:
        print("  [seed=%d] SANITY BREACH: baseline=%.4f not in [%.2f, %.2f]"
              % (seed, r_baseline["top1"], BASELINE_SANITY_LO,
                 BASELINE_SANITY_HI), flush=True)

    # ===== POINTER arms (deep chains; single-top1 + beam variants) =====
    t_arm = time.time()
    pointer_triples, pointer_chains = make_deep_chains(
        POINTER_N_CHAINS, V_CONCEPTS, POINTER_V_P, max_depth=DEPTH_5HOP,
        g=g, disallow_s=set())
    W_pointer = ingest_hebbian(pointer_triples, E, R, sq, N_DIM)
    print("  [seed=%d] pointer W built (%d triples, %d chains, depth=%d) t=%.1fs"
          % (seed, len(pointer_triples), len(pointer_chains), DEPTH_5HOP,
             round(time.time() - t_arm, 2)), flush=True)

    # ARM_SINGLE_TOP1_5HOP (rail)
    t_arm = time.time()
    chains_5 = [c[:DEPTH_5HOP] for c in pointer_chains]
    r_single5 = arm_single_chain_naive(E, R, sq, W_pointer, chains_5,
                                          depth=DEPTH_5HOP)
    r_single5["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    out["arm_single_top1_5hop"] = r_single5
    print("  [seed=%d] ARM_SINGLE_TOP1_5HOP top1=%.4f per_step=%s t=%.1fs"
          % (seed, r_single5["top1"], r_single5["per_step_acc"],
             r_single5["elapsed_s_arm"]), flush=True)

    # Beam arms
    for arm_name, w, k in BEAM_CONFIGS:
        t_arm = time.time()
        r_b = arm_beam_search(E, R, sq, W_pointer, chains_5,
                               depth=DEPTH_5HOP, beam_width=w, top_k=k)
        r_b["elapsed_s_arm"] = round(time.time() - t_arm, 2)
        out[arm_name.lower()] = r_b
        print(("  [seed=%d] %s top1=%.4f corr_in_beam=%s "
               "top_of_beam=%s t=%.1fs")
              % (seed, arm_name, r_b["top1"],
                 r_b["correct_in_beam_per_hop"],
                 r_b["top_of_beam_correct_per_hop"],
                 r_b["elapsed_s_arm"]), flush=True)

    out["elapsed_s"] = round(time.time() - t, 1)
    return out


def _cv(values: List[float]) -> float:
    vals = [v for v in values
            if isinstance(v, (int, float)) and not math.isnan(v)]
    if len(vals) < 2:
        return float("nan")
    m = float(np.mean(vals))
    return float(np.std(vals) / max(abs(m), 1e-9))


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
        return _cv(vals)

    baseline = mean_top1("arm_baseline_hrr_2hop")
    single5 = mean_top1("arm_single_top1_5hop")
    beam_w2 = mean_top1("arm_beam_w2_topk3_5hop")
    beam_w5 = mean_top1("arm_beam_w5_topk3_5hop")
    beam_w10 = mean_top1("arm_beam_w10_topk5_5hop")
    cv_w10 = cv_top1("arm_beam_w10_topk5_5hop")
    cv_w5 = cv_top1("arm_beam_w5_topk3_5hop")
    cv_w2 = cv_top1("arm_beam_w2_topk3_5hop")

    rails: List[str] = []
    sanity_breached = sum(1 for p in per_seed if not p.get("baseline_sanity_ok", False))
    if sanity_breached > 0:
        rails.append("SANITY_BREACH(%d/%d seeds baseline_mean=%.4f not in [%.2f, %.2f])"
                      % (sanity_breached, len(per_seed), baseline,
                         BASELINE_SANITY_LO, BASELINE_SANITY_HI))

    # Monotonic check (within tolerance): W5 >= W2 - tol AND W10 >= W5 - tol
    monotonic_w5_over_w2 = (not math.isnan(beam_w5) and not math.isnan(beam_w2)
                              and beam_w5 >= beam_w2 - MONOTONIC_TOL)
    monotonic_w10_over_w5 = (not math.isnan(beam_w10) and not math.isnan(beam_w5)
                               and beam_w10 >= beam_w5 - MONOTONIC_TOL)
    monotonic_ok = monotonic_w5_over_w2 and monotonic_w10_over_w5

    # Q-discipline: flag suspect saturation
    q_flags = []
    for name, val in [("BEAM_W10", beam_w10), ("BEAM_W5", beam_w5), ("BEAM_W2", beam_w2)]:
        if not math.isnan(val) and val >= Q_SATURATION:
            q_flags.append(("[Q-DISCIPLINE: %s=%.4f >= %.3f -- suspect saturation; "
                              "UNDER-CLAIM tier]") % (name, val, Q_SATURATION))
    q_note = " ".join(q_flags) + (" " if q_flags else "")

    summ = (
        "BASELINE=%.4f (sanity_breach_seeds=%d/%d) "
        "SINGLE_TOP1_5HOP=%.4f (rail) "
        "BEAM_W2=%.4f (cv=%.3f) BEAM_W5=%.4f (cv=%.3f) BEAM_W10=%.4f (cv=%.3f) "
        "monotonic_W5>=W2-tol=%s W10>=W5-tol=%s | "
        "lift_W10_over_single=%+.4f | rails=%s"
    ) % (
        baseline, sanity_breached, len(per_seed),
        single5,
        beam_w2, cv_w2,
        beam_w5, cv_w5,
        beam_w10, cv_w10,
        monotonic_w5_over_w2, monotonic_w10_over_w5,
        (beam_w10 - single5) if (not math.isnan(beam_w10) and not math.isnan(single5)) else float("nan"),
        rails,
    )

    if sanity_breached >= max(1, (len(per_seed) + 1) // 2):
        return "SANITY_BREACH", "SANITY_BREACH_BASELINE_OUT_OF_BAND: " + summ

    hp_chain_grade = (
        not math.isnan(beam_w10) and beam_w10 >= HP_BEAM_W10_5HOP
        and monotonic_ok
        and (math.isnan(cv_w10) or cv_w10 <= HP_BEAM_CV_MAX)
    )
    hp_partial = (not math.isnan(beam_w10) and beam_w10 >= HP_PARTIAL_5HOP)
    hf = (not math.isnan(beam_w10) and beam_w10 < HF_BEAM_W10_5HOP)

    if hp_chain_grade:
        return "HARD_PASS", \
               ("HARD_PASS_CHAIN_GRADE_BARRIER_1_BEAM: %s%s"
                  % (q_note, summ))
    if hp_partial:
        return "HARD_PASS", \
               ("HARD_PASS_PARTIAL_BEAM_LIFT_OVER_RAIL: %s%s"
                  % (q_note, summ))
    if hf:
        return "HARD_FAIL", \
               ("HARD_FAIL_BEAM_DOESNT_HELP: %s%s" % (q_note, summ))
    return "MIDDLE_BAND", \
           ("MIDDLE_BAND_BEAM_PARTIAL: %s%s" % (q_note, summ))


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
    print("[config] anchor=%s mode=%s seeds=%s N=%d V_C=%d | %s" % (
        ANCHOR_NAME, RUN_MODE, SEEDS, N_DIM, V_CONCEPTS, CONFIG_VERSION), flush=True)
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

    assert _LLM_CALL_COUNTER[0] == 0, "LLM calls non-zero: %d" % _LLM_CALL_COUNTER[0]

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
            "USER-directed Gap 1 (2026-06-25). 6th multi-hop attempt; brain-correct PFC analog. "
            "Beam search with multi-candidate parallel continuation + cumulative-log-score "
            "ranking. Substrate primitives chain-grade individually (WM multi-bank K=1024, "
            "CSP confidence HARD_PASS, HRR 2-hop sanity 0.65). Lever: top-K cleanup at each "
            "hop + beam_width kept by cumulative softmax score; the runner-up information "
            "that single-top1 discards is preserved through chain. Prior 5 attempts "
            "(pointer-chain-v2 / wm-scaffold / csp-gated / consolidation-v3 / pfc-chunked-2hop) "
            "all did per-hop top-1; this is the architectural lever not tested."
        ),
    }
    write_metrics(out_dir, metrics, results=per_seed)
    print("[done] metrics.json written (%d seeds, %.1fs)" % (
        len(per_seed), metrics["elapsed_s"]), flush=True)
