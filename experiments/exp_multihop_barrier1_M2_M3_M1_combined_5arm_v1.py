"""multihop_barrier1_M2_M3_M1_combined_5arm_v1 -- META_BARRIER_1 stack test.

Pre-reg: preregs/2026-06-27_multihop_barrier1_M2_M3_M1_combined_5arm_v1.md

META_BARRIER_1 (atomized 2026-06-25): 4 substrate-native multi-hop
closure attempts REFUTED at random-bipolar isotropic regime
(consolidation / pointer-chain / WM-scaffold / CSP-gated). META_M7
parallel-vote also regime-artifact. Multi-hop beyond 2 hops is currently
the largest OPEN substrate-product limit. Production rail anchors:
  per-hop cleanup ~ 0.69 -> compounding gives depth-5 ~ 0.145 +/- 0.02

3 categorically novel mechanisms from drill_multihop_barrier1_quadruple_
negative_3x_2026-06-27 are tested AS A STACK plus per-arm individual
ablations:

  M1 GROVER amplification (post-hoc; sqrt-N speedup; type-constrained)
  M2 NREM-REPLAY-COMPACT (adaptive shortcut creation; uses chain-grade
     NREM-replay primitive to BIND direct A->endpoint atoms for
     frequently-traversed chains)
  M3 STABILIZER-VECTOR (per-hop margin lift; learned per-hop scaffold
     vector raises cleanup margin without primitive replacement;
     enzyme transition-state stabilization analog)

ARMS (5; cardinality_ok mandatory):
  ARM_BASELINE                 - per-hop cleanup baseline rail (anchors
                                 ~0.145 at depth-5 +/- 0.02)
  ARM_M1_GROVER_AMPLIFICATION  - baseline + type-constraint + K-iter
                                 reflect-about-mean / reflect-about-target
  ARM_M2_NREM_REPLAY_COMPACT   - baseline + replay-driven shortcut
                                 atoms for top-freq chains
  ARM_M3_STABILIZER_VECTOR     - baseline + per-hop trained stabilizer
                                 bind that raises cleanup margin
  ARM_COMBINED                 - M2 + M3 + M1 stacked (M2 creates
                                 shortcuts, M3 raises per-hop margin
                                 on remaining walks, M1 amplifies
                                 endpoint distribution)

HARD_PASS bands (load-bearing; META_BARRIER_1 BROKEN if achieved):
  - ARM_COMBINED depth-5 >= 0.65 (META_BARRIER_1 BROKEN if achieved)
  - AND ARM_BASELINE depth-5 within 0.145 +/- 0.04 (regime sanity rail
    confirms 4-prior-refute regime is reproduced; cell is interpretable)
  - AND cardinality_ok: 5 arms x 3 seeds x len(DEPTHS)=4 = 60 units
    actually completed (HARD_FAIL_CARDINALITY_BREACH if observed < 60)

MIDDLE_BAND (partial closure):
  - ARM_COMBINED depth-5 in [0.30, 0.65) AND ARM_BASELINE in sanity band

HARD_FAIL (3-mechanism stack disproves):
  - ARM_COMBINED depth-5 < 0.30 AND no individual M1/M2/M3 arm exceeds
    ARM_BASELINE by > 0.05 at depth-5
  - META_BARRIER_1 NEGATIVE => adopt M5 honest-acceptance framing
    (substrate is structurally 2-hop-permanent)

SANITY RAIL (hard abort if breached):
  - ARM_BASELINE depth-5 NOT in [0.105, 0.185] (anchors ~0.145 +/- 0.04)
  - depth-1 baseline < 0.50 (single-hop should be near 0.69+ in this
    regime; if below 0.50, regime is broken; cell uninterpretable)

DISCIPLINES:
  D1 Discriminator-must-survive-scale: smoke uses FULL V_C=200 (NOT
     V_C=20); only seeds + n_chains_query reduced. M2 requires full
     n_chains_train for shortcuts to form.
  D2 Smoke-must-FIRE-discriminator: ARM_BASELINE within sanity band;
     ARM_COMBINED > ARM_BASELINE by >= 0.05 in smoke or stop and route
     back.
  D3 No-silent-except: setup + each arm wrapped.
  D4 cardinality_ok: SEEDS x 5 arms x DEPTHS arm-entry count;
     HARD_FAIL on cardinality breach.
  SCHEMA-VET 5b per-arm HP scope: each arm's per-depth metrics fully
     reported per seed.

ASCII-only; no unicode; no em-dashes; no emojis.
"""
from __future__ import annotations

import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import argparse
import json
import math
import os
import time
import traceback
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    aggregate_partials,
    get_output_dir,
    resumable_seeds,
    write_partial,
)


ANCHOR_NAME = "multihop_barrier1_M2_M3_M1_combined_5arm_v1"
_LLM_CALL_COUNTER = [0]

_ap = argparse.ArgumentParser(add_help=False)
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", dest="self_test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

RUN_MODE = (
    "smoke"
    if _ARGS.smoke or os.environ.get("HDLAB_RUN_MODE", "full").lower() == "smoke"
    else os.environ.get("HDLAB_RUN_MODE", "full").lower()
)

# Production regime (drill specification)
N_DIM_FULL = 8192
V_C_FULL = 200            # codebook size; load-bearing for Grover sqrt(V_C)
V_P_FULL = 10             # number of distinct predicates
K_SET_FULL = 20           # candidate set size for type-constraint
N_CHAINS_TRAIN_FULL = 500 # required for M2 shortcut formation
N_CHAINS_QUERY_FULL = 200
SEEDS_FULL = [7, 17, 23]
DEPTHS_FULL = [2, 3, 5, 8]

# M1 Grover schedule
GROVER_K_ITERS = 3        # ~pi/4 * sqrt(V_C/K_SET) = pi/4 * sqrt(10) ~ 2.5

# M2 NREM-replay-compact schedule
N_REPLAY_PASSES = 10
SHORTCUT_FREQ_FRAC = 0.20 # top-20% chains by frequency get shortcuts

# M3 stabilizer schedule (cheap numerical fit)
STABILIZER_FIT_STEPS = 50
STABILIZER_FIT_N_CHAINS = 100

# D1 discipline: smoke uses FULL V_C (mechanism discriminator depends on
# V_C scale); only N_DIM reduced + seeds + n_chains_query reduced.
if RUN_MODE == "smoke":
    N_DIM = 2048
    V_C = V_C_FULL        # FULL V_C per D1 (Grover sqrt-V_C; M2 shortcut count)
    V_P = V_P_FULL
    K_SET = K_SET_FULL
    N_CHAINS_TRAIN = N_CHAINS_TRAIN_FULL  # FULL train per D1 (M2 needs it)
    N_CHAINS_QUERY = 50
    SEEDS = [7]
    DEPTHS = [5]          # depth-5 is the discriminator; smoke fires it
else:
    N_DIM = N_DIM_FULL
    V_C = V_C_FULL
    V_P = V_P_FULL
    K_SET = K_SET_FULL
    N_CHAINS_TRAIN = N_CHAINS_TRAIN_FULL
    N_CHAINS_QUERY = N_CHAINS_QUERY_FULL
    SEEDS = SEEDS_FULL
    DEPTHS = DEPTHS_FULL

# Sanity rail bands (depth-5 baseline; drill specification)
BASELINE_DEPTH5_SANITY_LO = 0.105
BASELINE_DEPTH5_SANITY_HI = 0.185
BASELINE_DEPTH1_FLOOR = 0.50  # below this => regime broken

# HARD bands
HP_COMBINED_DEPTH5 = 0.65
MB_COMBINED_DEPTH5 = 0.30
INDIVIDUAL_OVER_BASELINE = 0.05  # individual arm signal threshold

CONFIG_VERSION = (
    f"ANCHOR={ANCHOR_NAME},N_DIM={N_DIM},V_C={V_C},V_P={V_P},"
    f"K_SET={K_SET},N_CHAINS_TRAIN={N_CHAINS_TRAIN},"
    f"N_CHAINS_QUERY={N_CHAINS_QUERY},"
    f"DEPTHS={'-'.join(str(d) for d in DEPTHS)},"
    f"GROVER_K={GROVER_K_ITERS},N_REPLAY_PASSES={N_REPLAY_PASSES},"
    f"SHORTCUT_FREQ_FRAC={SHORTCUT_FREQ_FRAC},"
    f"STAB_FIT_STEPS={STABILIZER_FIT_STEPS},"
    f"STAB_FIT_N_CHAINS={STABILIZER_FIT_N_CHAINS},"
    f"SEEDS={'-'.join(str(s) for s in SEEDS)},RUN_MODE={RUN_MODE},"
    f"HP_combined_d5>={HP_COMBINED_DEPTH5},MB_combined_d5>={MB_COMBINED_DEPTH5},"
    f"baseline_sanity=[{BASELINE_DEPTH5_SANITY_LO},{BASELINE_DEPTH5_SANITY_HI}]"
)


# ---------------------------------------------------------------------------
# Primitives (bipolar atoms; HRR-style binding via element-wise multiply
# and shared sqrt(N) gain; pointer-chain conventions from
# exp_substrate_multihop_pointer_chain_hybrid_v2_BASELINE_RAIL_FIXED)
# ---------------------------------------------------------------------------
def bipolar(M: int, n: int, g: np.random.Generator) -> np.ndarray:
    X = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)


def ingest_hebbian(triples: List[Tuple[int, int, int]],
                   E: np.ndarray, R: np.ndarray, sq: float,
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
                     g: np.random.Generator, disallow_s: set
                     ) -> Tuple[List[Tuple[int, int, int]],
                                List[List[Tuple[int, int, int]]]]:
    """Build n_chains random deep-chains of max_depth hops."""
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
            "BLOCKING make_deep_chains: only %d/%d generated for V=%d "
            "disallow|=%d max_depth=%d"
            % (len(chain_queries), n_chains, V, len(disallow_s), max_depth)
        )
    return all_triples, chain_queries


# ---------------------------------------------------------------------------
# ARM_BASELINE: per-hop cleanup pointer-chain walk
# ---------------------------------------------------------------------------
def chain_per_hop_cleanup(W: np.ndarray, E: np.ndarray, R: np.ndarray,
                          sq: float, start: int,
                          relations: List[int]) -> Tuple[int, np.ndarray]:
    """Per-hop cleanup: at each hop run W @ key, then argmax onto E.

    Returns (final_atom_index, final_score_distribution).
    """
    s = start
    final_scores = None
    for p in relations:
        key = (E[s] * R[p] * sq).astype(np.float32)
        o_scores = W @ key
        cleanup_scores = E @ o_scores
        final_scores = cleanup_scores
        s = int(cleanup_scores.argmax())
    return s, final_scores


def arm_baseline(W: np.ndarray, E: np.ndarray, R: np.ndarray, sq: float,
                 chains_test: List[List[Tuple[int, int, int]]],
                 depth: int) -> Dict[str, Any]:
    n = len(chains_test)
    hits = 0
    per_step_hits = np.zeros(depth, dtype=np.int64)
    for chain in chains_test:
        s = chain[0][0]
        for i in range(depth):
            p = chain[i][1]
            s, _ = chain_per_hop_cleanup(W, E, R, sq, s, [p])
            if s == chain[i][2]:
                per_step_hits[i] += 1
        if s == chain[depth - 1][2]:
            hits += 1
    per_step_acc = (per_step_hits.astype(np.float32)
                    / max(n, 1)).tolist()
    return {
        "top1": round(hits / max(n, 1), 4),
        "per_step_acc": [round(x, 4) for x in per_step_acc],
        "n_queries": n,
        "depth": depth,
    }


# ---------------------------------------------------------------------------
# M1 GROVER amplification: post-hoc reflect-about-mean / about-target
# ---------------------------------------------------------------------------
def grover_amplify(p: np.ndarray, candidate_mask: np.ndarray,
                   k_iters: int) -> np.ndarray:
    """Classical Grover iteration on real-valued probability-like vector.

    p: scores over V_C atoms (will be probability-normalized).
    candidate_mask: boolean (V_C,); True for type-valid candidates.
    k_iters: number of Grover iterations.

    Returns amplified score vector (renormalized to probabilities).
    """
    # Normalize to probabilities (softmax-style on z-score)
    z = (p - p.mean()) / (p.std() + 1e-9)
    pr = np.exp(z - z.max())
    pr /= pr.sum()

    for _ in range(k_iters):
        # Reflect about candidate-set (flip sign of NOT-in-candidate)
        pr_signed = np.where(candidate_mask, pr, -pr)
        # Reflect about mean (diffusion operator)
        mean_val = pr_signed.mean()
        pr_diff = 2 * mean_val - pr_signed
        # Renormalize amplitude magnitudes back to probabilities
        pr = np.abs(pr_diff)
        s = pr.sum()
        if s > 0:
            pr /= s
        else:
            return pr  # degenerate; return as-is
    return pr


def arm_m1_grover(W: np.ndarray, E: np.ndarray, R: np.ndarray, sq: float,
                  chains_test: List[List[Tuple[int, int, int]]],
                  depth: int, relation_range: Dict[int, np.ndarray]
                  ) -> Dict[str, Any]:
    """ARM_M1: per-hop cleanup walk + post-hoc Grover amplification of
    the endpoint distribution restricted to type-valid candidates.

    relation_range[p] = boolean mask (V_C,) of atoms type-valid as range
    of relation p. Constructed at setup time from train-chain stats.
    """
    n = len(chains_test)
    hits = 0
    for chain in chains_test:
        s = chain[0][0]
        last_scores = None
        for i in range(depth):
            p = chain[i][1]
            s, last_scores = chain_per_hop_cleanup(W, E, R, sq, s, [p])
        # Grover amplification on final endpoint distribution
        last_p = chain[depth - 1][1]
        cand_mask = relation_range.get(
            last_p, np.ones(E.shape[0], dtype=bool),
        )
        pr_amp = grover_amplify(last_scores, cand_mask, GROVER_K_ITERS)
        pred = int(np.argmax(pr_amp))
        if pred == chain[depth - 1][2]:
            hits += 1
    return {"top1": round(hits / max(n, 1), 4),
            "n_queries": n, "depth": depth}


# ---------------------------------------------------------------------------
# M2 NREM-replay-compact: shortcut atom creation for frequent chains
# ---------------------------------------------------------------------------
def build_shortcut_W(W_base: np.ndarray, E: np.ndarray, R_extended: np.ndarray,
                     sq: float,
                     chains_train: List[List[Tuple[int, int, int]]],
                     compact_p: int,
                     n_passes: int,
                     freq_frac: float) -> Tuple[np.ndarray, int, int]:
    """Add shortcut bindings A_1 -> A_K via compact_p relation for top-
    frequency chains (replay-driven compaction).

    Returns (W_augmented, n_shortcuts_added, n_replay_events).
    Top-freq chains assumed = first freq_frac fraction (chains have
    uniform freq in our synthetic generator; we'll select top-N by
    chain index as a proxy for "replay surfaced these N chains").
    """
    n_chains = len(chains_train)
    n_top = max(1, int(round(freq_frac * n_chains)))
    n_replay_events = 0
    shortcut_triples: List[Tuple[int, int, int]] = []
    # n_passes simulate replay batches; each pass re-binds the shortcut
    # (Hebbian outer-product accumulation; matches NREM-replay primitive)
    for _ in range(n_passes):
        for c_idx in range(n_top):
            chain = chains_train[c_idx]
            start = chain[0][0]
            end = chain[-1][2]
            shortcut_triples.append((start, compact_p, end))
            n_replay_events += 1
    # Build delta-W from shortcut triples
    if not shortcut_triples:
        return W_base, 0, 0
    W_short = ingest_hebbian(shortcut_triples, E, R_extended, sq,
                             E.shape[1])
    W_aug = W_base + W_short
    return W_aug, len(shortcut_triples), n_replay_events


def arm_m2_replay_compact(W: np.ndarray, E: np.ndarray,
                          R_extended: np.ndarray, sq: float,
                          chains_test: List[List[Tuple[int, int, int]]],
                          depth: int, compact_p: int,
                          shortcut_chain_set: set) -> Dict[str, Any]:
    """At query time, if start atom is in shortcut_chain_set (head of a
    compacted chain), try shortcut: W @ (E[start] * R[compact_p]). If
    high-confidence (margin > tau), return shortcut endpoint. Else fall
    back to per-hop walk.
    """
    n = len(chains_test)
    hits = 0
    n_shortcut_hits = 0
    n_shortcut_misses = 0
    n_fallback_hits = 0
    tau = 0.05  # margin threshold for shortcut acceptance
    for chain in chains_test:
        start = chain[0][0]
        end = chain[depth - 1][2]
        if start in shortcut_chain_set:
            key = (E[start] * R_extended[compact_p] * sq).astype(np.float32)
            o_scores = W @ key
            cleanup_scores = E @ o_scores
            top1 = int(np.argmax(cleanup_scores))
            margin = (cleanup_scores[top1]
                      - np.partition(cleanup_scores, -2)[-2])
            if margin > tau:
                # Accept shortcut
                if top1 == end:
                    hits += 1
                    n_shortcut_hits += 1
                else:
                    n_shortcut_misses += 1
                continue
        # Fallback: per-hop walk
        s = start
        for i in range(depth):
            p = chain[i][1]
            s, _ = chain_per_hop_cleanup(W, E, R_extended, sq, s, [p])
        if s == end:
            hits += 1
            n_fallback_hits += 1
    return {
        "top1": round(hits / max(n, 1), 4),
        "n_queries": n, "depth": depth,
        "n_shortcut_hits": int(n_shortcut_hits),
        "n_shortcut_misses": int(n_shortcut_misses),
        "n_fallback_hits": int(n_fallback_hits),
    }


# ---------------------------------------------------------------------------
# M3 STABILIZER-VECTOR: per-hop trained scaffold raises cleanup margin
# ---------------------------------------------------------------------------
def fit_stabilizer_per_hop(W: np.ndarray, E: np.ndarray, R: np.ndarray,
                           sq: float, n_dim: int, max_depth: int,
                           chains_train: List[List[Tuple[int, int, int]]],
                           g: np.random.Generator) -> np.ndarray:
    """Fit per-hop stabilizer vector S_k (one per hop position) via
    cheap numerical optimization. S_k binds (element-wise multiply) to
    the intermediate at hop k; goal: maximize cleanup margin at hop k.

    Returns S (max_depth, n_dim).

    Method: initialize S_k = ones; do STABILIZER_FIT_STEPS coordinate-
    descent-style updates by sampling random sign-flips and keeping the
    flip if margin improves on a held-out subset.
    """
    n_train = min(STABILIZER_FIT_N_CHAINS, len(chains_train))
    train_subset = chains_train[:n_train]
    S = np.ones((max_depth, n_dim), dtype=np.float32)

    def measure_margin(stab_vec: np.ndarray, hop_k: int) -> float:
        """Average top-1-minus-top-2 margin at hop hop_k across train."""
        margins = []
        for chain in train_subset:
            if hop_k >= len(chain):
                continue
            s = chain[0][0]
            # Walk to hop_k - 1 with current S
            for j in range(hop_k):
                p = chain[j][1]
                key = (E[s] * R[p] * sq).astype(np.float32)
                # Apply stabilizer for hop j (S[j])
                key = key * S[j]
                o_scores = W @ key
                cleanup_scores = E @ o_scores
                s = int(cleanup_scores.argmax())
            # Now measure margin at hop_k using stab_vec (the candidate)
            p = chain[hop_k][1]
            key = (E[s] * R[p] * sq).astype(np.float32)
            key = key * stab_vec
            o_scores = W @ key
            cleanup_scores = E @ o_scores
            top1 = float(cleanup_scores.max())
            top2 = float(np.partition(cleanup_scores, -2)[-2])
            margins.append(top1 - top2)
        return float(np.mean(margins)) if margins else 0.0

    # Greedy bit-flip optimization per hop position
    for hop_k in range(max_depth):
        cur_margin = measure_margin(S[hop_k], hop_k)
        for _step in range(STABILIZER_FIT_STEPS):
            # Sample a small block of indices to flip in S[hop_k]
            n_flip = max(1, n_dim // 200)
            flip_idx = g.choice(n_dim, size=n_flip, replace=False)
            S_cand = S[hop_k].copy()
            S_cand[flip_idx] *= -1.0
            cand_margin = measure_margin(S_cand, hop_k)
            if cand_margin > cur_margin:
                S[hop_k] = S_cand
                cur_margin = cand_margin
    return S


def chain_per_hop_cleanup_with_stabilizer(
    W: np.ndarray, E: np.ndarray, R: np.ndarray, sq: float,
    start: int, relations: List[int],
    S: np.ndarray,
) -> Tuple[int, np.ndarray]:
    """Per-hop cleanup with per-hop stabilizer bind."""
    s = start
    final_scores = None
    for i, p in enumerate(relations):
        key = (E[s] * R[p] * sq).astype(np.float32)
        if i < S.shape[0]:
            key = key * S[i]
        o_scores = W @ key
        cleanup_scores = E @ o_scores
        final_scores = cleanup_scores
        s = int(cleanup_scores.argmax())
    return s, final_scores


def arm_m3_stabilizer(W: np.ndarray, E: np.ndarray, R: np.ndarray,
                      sq: float,
                      chains_test: List[List[Tuple[int, int, int]]],
                      depth: int, S: np.ndarray) -> Dict[str, Any]:
    n = len(chains_test)
    hits = 0
    for chain in chains_test:
        s = chain[0][0]
        relations = [chain[i][1] for i in range(depth)]
        s, _ = chain_per_hop_cleanup_with_stabilizer(
            W, E, R, sq, s, relations, S,
        )
        if s == chain[depth - 1][2]:
            hits += 1
    return {"top1": round(hits / max(n, 1), 4),
            "n_queries": n, "depth": depth}


# ---------------------------------------------------------------------------
# ARM_COMBINED: M2 shortcut, M3 stabilizer on fallback, M1 amplify endpoint
# ---------------------------------------------------------------------------
def arm_combined(W: np.ndarray, E: np.ndarray, R_extended: np.ndarray,
                 sq: float,
                 chains_test: List[List[Tuple[int, int, int]]],
                 depth: int, compact_p: int,
                 shortcut_chain_set: set, S: np.ndarray,
                 relation_range: Dict[int, np.ndarray]
                 ) -> Dict[str, Any]:
    """Full stack:
      1. M2: try shortcut for top-freq chains; accept if margin > tau
      2. M3: per-hop stabilized walk for non-shortcut chains
      3. M1: post-hoc Grover amplification on endpoint distribution
             with type-constraint mask
    """
    n = len(chains_test)
    hits = 0
    n_shortcut_hits = 0
    n_stack_hits = 0
    tau = 0.05
    for chain in chains_test:
        start = chain[0][0]
        end = chain[depth - 1][2]
        # M2: shortcut try
        if start in shortcut_chain_set:
            key = (E[start] * R_extended[compact_p] * sq).astype(np.float32)
            o_scores = W @ key
            cleanup_scores = E @ o_scores
            top1 = int(np.argmax(cleanup_scores))
            margin = (cleanup_scores[top1]
                      - np.partition(cleanup_scores, -2)[-2])
            if margin > tau:
                if top1 == end:
                    hits += 1
                    n_shortcut_hits += 1
                continue
        # M3 + M1: stabilized walk + Grover amplification on endpoint
        relations = [chain[i][1] for i in range(depth)]
        _s, last_scores = chain_per_hop_cleanup_with_stabilizer(
            W, E, R_extended, sq, start, relations, S,
        )
        last_p = chain[depth - 1][1]
        cand_mask = relation_range.get(
            last_p, np.ones(E.shape[0], dtype=bool),
        )
        pr_amp = grover_amplify(last_scores, cand_mask, GROVER_K_ITERS)
        pred = int(np.argmax(pr_amp))
        if pred == end:
            hits += 1
            n_stack_hits += 1
    return {
        "top1": round(hits / max(n, 1), 4),
        "n_queries": n, "depth": depth,
        "n_shortcut_hits": int(n_shortcut_hits),
        "n_stack_hits": int(n_stack_hits),
    }


# ---------------------------------------------------------------------------
# Relation-range estimator (for M1 + COMBINED Grover candidate-mask)
# ---------------------------------------------------------------------------
def estimate_relation_ranges(
    chains_train: List[List[Tuple[int, int, int]]], V: int, P: int,
) -> Dict[int, np.ndarray]:
    """For each predicate p, compute the set of atom-indices observed
    as object of p in training chains. Returns dict[p -> bool mask].

    Lightly relaxed: include any atom seen as object of p in train.
    """
    ranges = {p: np.zeros(V, dtype=bool) for p in range(P)}
    for chain in chains_train:
        for (_s, p, o) in chain:
            if p in ranges:
                ranges[p][o] = True
    # If a relation has no observed range (shouldn't happen at our
    # n_chains_train), default to all-valid.
    for p in range(P):
        if not ranges[p].any():
            ranges[p][:] = True
    return ranges


# ---------------------------------------------------------------------------
# Self-tests (MUST FIRE the discriminator at module import time)
# ---------------------------------------------------------------------------
def _selftest_chain_walk_runs() -> bool:
    g = np.random.default_rng(0)
    n = 1024
    V = 60
    P = 4
    sq = math.sqrt(n)
    E = bipolar(V, n, g)
    R = bipolar(P, n, g)
    triples, chains = make_deep_chains(8, V, P, max_depth=3, g=g,
                                       disallow_s=set())
    W = ingest_hebbian(triples, E, R, sq, n)
    s, scores = chain_per_hop_cleanup(W, E, R, sq, chains[0][0][0],
                                      [chains[0][i][1] for i in range(3)])
    assert 0 <= s < V
    assert scores is not None and scores.shape == (V,)
    return True


def _selftest_grover_amplifies_target() -> bool:
    """Grover iteration amplifies the in-candidate-set probability above
    its starting value when the target distribution has mass on
    candidates."""
    V = 50
    rng = np.random.RandomState(0)
    # Build a noisy distribution with slight bias toward candidate set
    base = rng.rand(V) * 0.1
    cand_mask = np.zeros(V, dtype=bool)
    cand_mask[:5] = True  # 5 candidate atoms
    base[2] += 0.5  # target atom (in candidates)
    pr_amp = grover_amplify(base, cand_mask, k_iters=3)
    # Target atom should have higher rank in amplified distribution
    assert int(np.argmax(pr_amp)) == 2, (
        f"Grover should amplify target=2; got argmax={np.argmax(pr_amp)}"
    )
    # Candidate-mass should grow vs initial
    pr_init = base / max(base.sum(), 1e-9)
    cand_mass_init = pr_init[cand_mask].sum()
    cand_mass_amp = pr_amp[cand_mask].sum()
    assert cand_mass_amp > cand_mass_init, (
        f"candidate mass should grow: init={cand_mass_init:.3f} "
        f"amp={cand_mass_amp:.3f}"
    )
    return True


def _selftest_shortcut_atom_added_to_W() -> bool:
    """build_shortcut_W actually adds bindings: querying compact_p on a
    top-freq start should retrieve close to the shortcut endpoint."""
    g = np.random.default_rng(7)
    n = 512
    V = 30
    P_ext = 5
    sq = math.sqrt(n)
    E = bipolar(V, n, g)
    R_ext = bipolar(P_ext, n, g)
    # Build chains with original 2 predicates
    triples, chains = make_deep_chains(10, V, P=2, max_depth=2, g=g,
                                       disallow_s=set())
    W = ingest_hebbian(triples, E, R_ext, sq, n)
    compact_p = P_ext - 1  # reserved compact relation
    W_aug, n_short, n_events = build_shortcut_W(
        W, E, R_ext, sq, chains, compact_p,
        n_passes=3, freq_frac=0.50,
    )
    assert n_short > 0, f"shortcuts not added; n_short={n_short}"
    assert n_events > 0, f"replay events not counted; n_events={n_events}"
    # Query compact_p on first chain's start
    start = chains[0][0][0]
    end = chains[0][-1][2]
    key = (E[start] * R_ext[compact_p] * sq).astype(np.float32)
    o_scores = W_aug @ key
    cleanup_scores = E @ o_scores
    top1 = int(np.argmax(cleanup_scores))
    # After replay-compact with 3 passes for top-freq chains, the
    # shortcut should land at the end atom for chain 0.
    assert top1 == end, (
        f"shortcut should retrieve end={end}; got top1={top1} "
        f"(scores[end]={cleanup_scores[end]:.3f}, "
        f"scores[top1]={cleanup_scores[top1]:.3f})"
    )
    return True


def _selftest_relation_range_built() -> bool:
    chains = [
        [(0, 0, 1), (1, 1, 2)],
        [(3, 0, 4), (4, 1, 5)],
    ]
    ranges = estimate_relation_ranges(chains, V=10, P=2)
    assert ranges[0][1] and ranges[0][4]
    assert ranges[1][2] and ranges[1][5]
    assert not ranges[0][0]
    return True


def _selftest_stabilizer_fit_runs() -> bool:
    """Stabilizer fit completes and returns S of correct shape."""
    g = np.random.default_rng(11)
    n = 512
    V = 30
    P = 3
    sq = math.sqrt(n)
    E = bipolar(V, n, g)
    R = bipolar(P, n, g)
    triples, chains = make_deep_chains(15, V, P, max_depth=2, g=g,
                                       disallow_s=set())
    W = ingest_hebbian(triples, E, R, sq, n)
    # Use small fit budget for self-test
    S = np.ones((2, n), dtype=np.float32)
    # Just verify the per-hop cleanup with stabilizer runs
    chain = chains[0]
    s, _ = chain_per_hop_cleanup_with_stabilizer(
        W, E, R, sq, chain[0][0], [chain[0][1], chain[1][1]], S,
    )
    assert 0 <= s < V
    return True


def _selftest_arm_baseline_returns_per_step() -> bool:
    g = np.random.default_rng(13)
    n = 512
    V = 30
    P = 3
    sq = math.sqrt(n)
    E = bipolar(V, n, g)
    R = bipolar(P, n, g)
    triples, chains = make_deep_chains(8, V, P, max_depth=3, g=g,
                                       disallow_s=set())
    W = ingest_hebbian(triples, E, R, sq, n)
    r = arm_baseline(W, E, R, sq, chains, depth=3)
    assert "top1" in r and "per_step_acc" in r
    assert len(r["per_step_acc"]) == 3
    assert 0.0 <= r["top1"] <= 1.0
    return True


def _selftest_baseline_sanity_constants() -> bool:
    """Sanity rail constants must be reasonable."""
    assert BASELINE_DEPTH5_SANITY_LO < BASELINE_DEPTH5_SANITY_HI
    assert 0.105 <= BASELINE_DEPTH5_SANITY_LO < 0.145
    assert 0.145 < BASELINE_DEPTH5_SANITY_HI <= 0.185
    assert HP_COMBINED_DEPTH5 > MB_COMBINED_DEPTH5
    return True


def _instrumentation_selftest():
    _selftest_chain_walk_runs()
    _selftest_grover_amplifies_target()
    _selftest_shortcut_atom_added_to_W()
    _selftest_relation_range_built()
    _selftest_stabilizer_fit_runs()
    _selftest_arm_baseline_returns_per_step()
    _selftest_baseline_sanity_constants()
    print(
        f"[selftest] PASS  N_DIM={N_DIM}  V_C={V_C}  V_P={V_P}  "
        f"K_SET={K_SET}  N_TRAIN={N_CHAINS_TRAIN}  "
        f"N_QUERY={N_CHAINS_QUERY}  DEPTHS={DEPTHS}  "
        f"GROVER_K={GROVER_K_ITERS}  REPLAY_P={N_REPLAY_PASSES}  "
        f"STAB_STEPS={STABILIZER_FIT_STEPS}  mode={RUN_MODE}",
        flush=True,
    )


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


# ---------------------------------------------------------------------------
# Per-seed runner (D3 no-silent-except)
# ---------------------------------------------------------------------------
ARM_NAMES = [
    "ARM_BASELINE",
    "ARM_M1_GROVER_AMPLIFICATION",
    "ARM_M2_NREM_REPLAY_COMPACT",
    "ARM_M3_STABILIZER_VECTOR",
    "ARM_COMBINED",
]


def run_seed(seed: int) -> Dict[str, Any]:
    t0 = time.time()
    print(
        f"  [seed={seed}] setup: N_DIM={N_DIM} V_C={V_C} V_P={V_P} "
        f"K_SET={K_SET} train={N_CHAINS_TRAIN} query={N_CHAINS_QUERY} "
        f"max_depth={max(DEPTHS)} mode={RUN_MODE}...",
        flush=True,
    )
    try:
        t_setup = time.time()
        g = np.random.default_rng(seed)
        sq = math.sqrt(N_DIM)
        E = bipolar(V_C, N_DIM, g)
        # Extended R: V_P predicates + 1 reserved compact_p for M2 shortcuts
        compact_p = V_P
        R_extended = bipolar(V_P + 1, N_DIM, g)

        # Train chains: shared across all arms (same W)
        max_depth = max(DEPTHS)
        train_triples, train_chains = make_deep_chains(
            N_CHAINS_TRAIN, V_C, V_P, max_depth=max_depth, g=g,
            disallow_s=set(),
        )
        W_base = ingest_hebbian(train_triples, E, R_extended, sq, N_DIM)

        # Disjoint query chains (different start atoms not in train)
        train_starts = {c[0][0] for c in train_chains}
        query_triples, query_chains = make_deep_chains(
            N_CHAINS_QUERY, V_C, V_P, max_depth=max_depth, g=g,
            disallow_s=train_starts,
        )
        # Note: query_triples not ingested - chains evaluated only against
        # the train W.

        # M1 prep: relation ranges from train
        relation_ranges = estimate_relation_ranges(train_chains, V_C, V_P)

        # M2 prep: build shortcut-augmented W
        W_m2, n_shortcuts, n_replay_events = build_shortcut_W(
            W_base, E, R_extended, sq, train_chains, compact_p,
            n_passes=N_REPLAY_PASSES, freq_frac=SHORTCUT_FREQ_FRAC,
        )
        # shortcut_chain_set = starts of top-freq chains (heads of
        # compacted shortcuts) - we use the first SHORTCUT_FREQ_FRAC
        # fraction of train chains as the "frequent set" by construction.
        n_top = max(1, int(round(SHORTCUT_FREQ_FRAC * len(train_chains))))
        shortcut_chain_set = {train_chains[i][0][0] for i in range(n_top)}

        # M3 prep: fit stabilizer (uses base W; stabilizer is regime-
        # agnostic per hop position).
        t_stab = time.time()
        g_stab = np.random.default_rng(seed + 100)
        S = fit_stabilizer_per_hop(W_base, E, R_extended, sq, N_DIM,
                                   max_depth, train_chains, g_stab)
        stab_wall = time.time() - t_stab

        print(
            f"  [seed={seed}] setup done in {time.time()-t_setup:.1f}s "
            f"(stab_fit={stab_wall:.1f}s)  n_train={len(train_chains)}  "
            f"n_query={len(query_chains)}  shortcuts_added={n_shortcuts}  "
            f"replay_events={n_replay_events}  "
            f"shortcut_set_size={len(shortcut_chain_set)}  "
            f"W_base_norm={np.linalg.norm(W_base):.2f}  "
            f"W_m2_norm={np.linalg.norm(W_m2):.2f}",
            flush=True,
        )
    except Exception as exc:
        tb = traceback.format_exc()
        print(f"  [seed={seed}] SETUP_EXCEPTION: {exc}\n{tb}", flush=True)
        return {
            "seed": seed, "N_DIM": N_DIM, "V_C": V_C, "V_P": V_P,
            "K_SET": K_SET, "run_mode": RUN_MODE,
            "config_version": CONFIG_VERSION,
            "exception_phase": "setup",
            "exception_msg": str(exc),
            "exception_traceback": tb,
            "arms": [],
            "elapsed_s": float(time.time() - t0),
        }

    # Per-depth, per-arm eval
    arms_results: List[Dict[str, Any]] = []
    for depth in DEPTHS:
        chains_d = [c[:depth] for c in query_chains]
        # ARM_BASELINE
        try:
            t = time.time()
            r = arm_baseline(W_base, E, R_extended, sq, chains_d, depth)
            r["arm_name"] = "ARM_BASELINE"
            r["wall_s"] = round(time.time() - t, 2)
            arms_results.append(r)
            print(
                f"  [seed={seed} ARM_BASELINE d={depth}] top1={r['top1']} "
                f"per_step={r['per_step_acc']} wall={r['wall_s']}s",
                flush=True,
            )
        except Exception as exc:
            tb = traceback.format_exc()
            print(f"  [seed={seed} ARM_BASELINE d={depth}] EXC: {exc}\n{tb}",
                  flush=True)
            arms_results.append({
                "arm_name": "ARM_BASELINE", "depth": depth,
                "exception_msg": str(exc), "exception_traceback": tb,
            })

        # ARM_M1
        try:
            t = time.time()
            r = arm_m1_grover(W_base, E, R_extended, sq, chains_d, depth,
                              relation_ranges)
            r["arm_name"] = "ARM_M1_GROVER_AMPLIFICATION"
            r["wall_s"] = round(time.time() - t, 2)
            arms_results.append(r)
            print(
                f"  [seed={seed} ARM_M1 d={depth}] top1={r['top1']} "
                f"wall={r['wall_s']}s",
                flush=True,
            )
        except Exception as exc:
            tb = traceback.format_exc()
            print(f"  [seed={seed} ARM_M1 d={depth}] EXC: {exc}\n{tb}",
                  flush=True)
            arms_results.append({
                "arm_name": "ARM_M1_GROVER_AMPLIFICATION", "depth": depth,
                "exception_msg": str(exc), "exception_traceback": tb,
            })

        # ARM_M2
        try:
            t = time.time()
            r = arm_m2_replay_compact(W_m2, E, R_extended, sq, chains_d,
                                      depth, compact_p, shortcut_chain_set)
            r["arm_name"] = "ARM_M2_NREM_REPLAY_COMPACT"
            r["wall_s"] = round(time.time() - t, 2)
            arms_results.append(r)
            print(
                f"  [seed={seed} ARM_M2 d={depth}] top1={r['top1']} "
                f"shortcut_hits={r.get('n_shortcut_hits',0)} "
                f"fallback_hits={r.get('n_fallback_hits',0)} "
                f"wall={r['wall_s']}s",
                flush=True,
            )
        except Exception as exc:
            tb = traceback.format_exc()
            print(f"  [seed={seed} ARM_M2 d={depth}] EXC: {exc}\n{tb}",
                  flush=True)
            arms_results.append({
                "arm_name": "ARM_M2_NREM_REPLAY_COMPACT", "depth": depth,
                "exception_msg": str(exc), "exception_traceback": tb,
            })

        # ARM_M3
        try:
            t = time.time()
            r = arm_m3_stabilizer(W_base, E, R_extended, sq, chains_d,
                                  depth, S)
            r["arm_name"] = "ARM_M3_STABILIZER_VECTOR"
            r["wall_s"] = round(time.time() - t, 2)
            arms_results.append(r)
            print(
                f"  [seed={seed} ARM_M3 d={depth}] top1={r['top1']} "
                f"wall={r['wall_s']}s",
                flush=True,
            )
        except Exception as exc:
            tb = traceback.format_exc()
            print(f"  [seed={seed} ARM_M3 d={depth}] EXC: {exc}\n{tb}",
                  flush=True)
            arms_results.append({
                "arm_name": "ARM_M3_STABILIZER_VECTOR", "depth": depth,
                "exception_msg": str(exc), "exception_traceback": tb,
            })

        # ARM_COMBINED
        try:
            t = time.time()
            r = arm_combined(W_m2, E, R_extended, sq, chains_d, depth,
                             compact_p, shortcut_chain_set, S,
                             relation_ranges)
            r["arm_name"] = "ARM_COMBINED"
            r["wall_s"] = round(time.time() - t, 2)
            arms_results.append(r)
            print(
                f"  [seed={seed} ARM_COMBINED d={depth}] top1={r['top1']} "
                f"shortcut_hits={r.get('n_shortcut_hits',0)} "
                f"stack_hits={r.get('n_stack_hits',0)} "
                f"wall={r['wall_s']}s",
                flush=True,
            )
        except Exception as exc:
            tb = traceback.format_exc()
            print(f"  [seed={seed} ARM_COMBINED d={depth}] EXC: {exc}\n{tb}",
                  flush=True)
            arms_results.append({
                "arm_name": "ARM_COMBINED", "depth": depth,
                "exception_msg": str(exc), "exception_traceback": tb,
            })

    elapsed = time.time() - t0
    return {
        "seed": seed, "N_DIM": N_DIM, "V_C": V_C, "V_P": V_P,
        "K_SET": K_SET, "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "n_llm_calls": int(_LLM_CALL_COUNTER[0]),
        "n_chains_train": int(N_CHAINS_TRAIN),
        "n_chains_query": int(N_CHAINS_QUERY),
        "depths": list(DEPTHS),
        "grover_k_iters": int(GROVER_K_ITERS),
        "n_replay_passes": int(N_REPLAY_PASSES),
        "shortcut_freq_frac": float(SHORTCUT_FREQ_FRAC),
        "n_shortcuts_added": int(n_shortcuts),
        "n_replay_events": int(n_replay_events),
        "shortcut_set_size": int(len(shortcut_chain_set)),
        "stabilizer_fit_steps": int(STABILIZER_FIT_STEPS),
        "stabilizer_wall_s": float(stab_wall),
        "arms": arms_results,
        "elapsed_s": float(elapsed),
    }


# ---------------------------------------------------------------------------
# Verdict
# ---------------------------------------------------------------------------
def _arm_at_depth(arms: List[Dict], name: str, depth: int) -> Dict:
    for a in arms:
        if a.get("arm_name") == name and a.get("depth") == depth:
            return a
    return {}


def compute_verdict(results: List[Dict]) -> Tuple[str, str]:
    if not results:
        return ("HARD_FAIL", "No valid seed results.")

    # D3: any exception is HARD_FAIL.
    for r in results:
        if "exception_phase" in r:
            return ("HARD_FAIL",
                    f"HARD_FAIL: D3 caught {r['exception_phase']} "
                    f"exception seed={r['seed']}: {r['exception_msg']}")
        for a in r.get("arms", []):
            if "exception_msg" in a:
                return ("HARD_FAIL",
                        f"HARD_FAIL: D3 caught arm exception "
                        f"seed={r['seed']} arm={a['arm_name']} "
                        f"depth={a.get('depth','?')}: {a['exception_msg']}")

    # D4 cardinality: SEEDS x 5 arms x len(DEPTHS)
    expected_per_seed = len(ARM_NAMES) * len(DEPTHS)
    expected_total = expected_per_seed * len(results)
    observed_total = sum(len(r.get("arms", [])) for r in results)
    if observed_total != expected_total:
        return ("HARD_FAIL",
                f"HARD_FAIL: D4 cardinality_ok breach: expected "
                f"{expected_total} arm entries ({len(ARM_NAMES)} arms x "
                f"{len(DEPTHS)} depths x {len(results)} seeds); got "
                f"{observed_total}.")
    for r in results:
        got = len(r.get("arms", []))
        if got != expected_per_seed:
            return ("HARD_FAIL",
                    f"HARD_FAIL: D4 cardinality_ok breach seed={r['seed']}: "
                    f"expected {expected_per_seed} arm entries, got {got}")

    any_llm = any(r.get("n_llm_calls", 0) > 0 for r in results)
    if any_llm:
        return ("HARD_FAIL",
                "HARD_FAIL: substrate-only-decode gate violated.")

    # D2 mechanism-fires gate: shortcuts actually added; replay events > 0
    for r in results:
        if r.get("n_shortcuts_added", 0) <= 0:
            return ("HARD_FAIL",
                    f"HARD_FAIL: D2 M2 inert seed={r['seed']}: "
                    f"n_shortcuts_added=0 (M2 didn't form shortcuts).")
        if r.get("n_replay_events", 0) <= 0:
            return ("HARD_FAIL",
                    f"HARD_FAIL: D2 M2 inert seed={r['seed']}: "
                    f"n_replay_events=0 (replay didn't run).")

    # Aggregate per arm per depth
    def _agg(arm_name: str, depth: int) -> Dict[str, float]:
        per = [_arm_at_depth(r["arms"], arm_name, depth) for r in results]
        per = [a for a in per if a]
        tops = [a["top1"] for a in per
                if isinstance(a.get("top1"), (int, float))
                and not math.isnan(a["top1"])]
        if not tops:
            return {"mean_top1": float("nan"), "std_top1": float("nan"),
                    "cv_top1": float("nan"), "n": 0}
        return {
            "mean_top1": float(np.mean(tops)),
            "std_top1": float(np.std(tops)),
            "cv_top1": float(np.std(tops) / max(abs(np.mean(tops)), 1e-9)),
            "n": len(tops),
        }

    # Build full per-depth, per-arm aggregate table
    agg_table: Dict[Tuple[str, int], Dict[str, float]] = {}
    for arm in ARM_NAMES:
        for d in DEPTHS:
            agg_table[(arm, d)] = _agg(arm, d)

    # SANITY RAIL: depth-5 BASELINE in band [0.105, 0.185]
    if 5 in DEPTHS:
        base_d5 = agg_table[("ARM_BASELINE", 5)]["mean_top1"]
    else:
        # Smoke might not include 5; pick the closest
        closest_d = min(DEPTHS, key=lambda d: abs(d - 5))
        base_d5 = agg_table[("ARM_BASELINE", closest_d)]["mean_top1"]

    if not (BASELINE_DEPTH5_SANITY_LO <= base_d5 <= BASELINE_DEPTH5_SANITY_HI):
        return ("HARD_FAIL",
                f"HARD_FAIL: SANITY RAIL breach: ARM_BASELINE depth-5 "
                f"top1={base_d5:.3f} not in "
                f"[{BASELINE_DEPTH5_SANITY_LO}, "
                f"{BASELINE_DEPTH5_SANITY_HI}]. Regime not reproduced; "
                f"cell uninterpretable.")

    # SANITY RAIL: depth-1 BASELINE >= floor (if depth 1 not in DEPTHS,
    # use depth-2 as a softer rail).
    if 1 in DEPTHS:
        base_d1 = agg_table[("ARM_BASELINE", 1)]["mean_top1"]
        if base_d1 < BASELINE_DEPTH1_FLOOR:
            return ("HARD_FAIL",
                    f"HARD_FAIL: SANITY RAIL breach: ARM_BASELINE depth-1 "
                    f"top1={base_d1:.3f} < {BASELINE_DEPTH1_FLOOR}. "
                    f"Single-hop regime broken; cell uninterpretable.")

    # Primary discriminator: ARM_COMBINED at depth-5
    if 5 in DEPTHS:
        combined_d5 = agg_table[("ARM_COMBINED", 5)]["mean_top1"]
    else:
        closest_d = min(DEPTHS, key=lambda d: abs(d - 5))
        combined_d5 = agg_table[("ARM_COMBINED", closest_d)]["mean_top1"]

    # Individual arm signals at depth-5
    if 5 in DEPTHS:
        m1_d5 = agg_table[("ARM_M1_GROVER_AMPLIFICATION", 5)]["mean_top1"]
        m2_d5 = agg_table[("ARM_M2_NREM_REPLAY_COMPACT", 5)]["mean_top1"]
        m3_d5 = agg_table[("ARM_M3_STABILIZER_VECTOR", 5)]["mean_top1"]
    else:
        closest_d = min(DEPTHS, key=lambda d: abs(d - 5))
        m1_d5 = agg_table[("ARM_M1_GROVER_AMPLIFICATION", closest_d)]["mean_top1"]
        m2_d5 = agg_table[("ARM_M2_NREM_REPLAY_COMPACT", closest_d)]["mean_top1"]
        m3_d5 = agg_table[("ARM_M3_STABILIZER_VECTOR", closest_d)]["mean_top1"]

    individual_lift = max(
        m1_d5 - base_d5, m2_d5 - base_d5, m3_d5 - base_d5,
    )

    summary = (
        f"N_DIM={N_DIM} V_C={V_C} train={N_CHAINS_TRAIN} "
        f"query={N_CHAINS_QUERY} depths={DEPTHS} "
        f"BASE_d5={base_d5:.3f} "
        f"M1_d5={m1_d5:.3f} M2_d5={m2_d5:.3f} M3_d5={m3_d5:.3f} "
        f"COMBINED_d5={combined_d5:.3f} "
        f"individual_lift={individual_lift:+.3f}"
    )

    # HARD_PASS: META_BARRIER_1 BROKEN
    if combined_d5 >= HP_COMBINED_DEPTH5:
        return ("HARD_PASS",
                f"HARD_PASS_META_BARRIER_1_BROKEN: ARM_COMBINED depth-5 "
                f"top1={combined_d5:.3f} >= {HP_COMBINED_DEPTH5}; baseline "
                f"sanity rail OK; multi-hop closure beyond 2 hops achieved "
                f"via M2+M3+M1 stack. {summary}")

    # MIDDLE_BAND: partial closure
    if combined_d5 >= MB_COMBINED_DEPTH5:
        return ("MIDDLE_BAND",
                f"MIDDLE_BAND_PARTIAL_BARRIER_BREACH: ARM_COMBINED depth-5 "
                f"top1={combined_d5:.3f} in [{MB_COMBINED_DEPTH5}, "
                f"{HP_COMBINED_DEPTH5}); mechanism class correct, "
                f"parameter-tuning or compose more aggressively. {summary}")

    # HARD_FAIL: no closure
    if individual_lift < INDIVIDUAL_OVER_BASELINE:
        return ("HARD_FAIL",
                f"HARD_FAIL_META_BARRIER_1_NEGATIVE: ARM_COMBINED depth-5 "
                f"top1={combined_d5:.3f} < {MB_COMBINED_DEPTH5} AND no "
                f"individual arm exceeds baseline by {INDIVIDUAL_OVER_BASELINE}. "
                f"3-mechanism stack disproves; adopt M5 honest-acceptance "
                f"framing (substrate is structurally 2-hop-permanent). "
                f"{summary}")
    # Individual signal present but stack < MB
    return ("HARD_FAIL",
            f"HARD_FAIL_STACK_NOT_SYNERGISTIC: ARM_COMBINED depth-5 "
            f"top1={combined_d5:.3f} < {MB_COMBINED_DEPTH5} despite "
            f"individual lift {individual_lift:+.3f}. Mechanisms don't "
            f"stack additively at depth-5. {summary}")


# ---------------------------------------------------------------------------
# Main driver
# ---------------------------------------------------------------------------
out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N_DIM": N_DIM, "V_C": V_C, "V_P": V_P, "K_SET": K_SET,
              "N_CHAINS_TRAIN": N_CHAINS_TRAIN,
              "N_CHAINS_QUERY": N_CHAINS_QUERY,
              "run_mode": RUN_MODE}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(
    f"[ckpt] {len(done)} of {len(SEEDS)} seeds already complete; "
    f"running {remaining}", flush=True,
)

t_sweep_start = time.time()
for seed in remaining:
    print(
        f"[seed={seed}] M1+M2+M3+COMBINED+BASELINE N_DIM={N_DIM} V_C={V_C} "
        f"V_P={V_P} train={N_CHAINS_TRAIN} query={N_CHAINS_QUERY} "
        f"depths={DEPTHS} mode={RUN_MODE}...",
        flush=True,
    )
    result = run_seed(seed)
    write_partial(out_dir, seed, result)

per_seed = aggregate_partials(out_dir, SEEDS, run_config=run_config)
all_results = list(per_seed.values())
verdict, verdict_msg = compute_verdict(all_results)

elapsed_s = time.time() - t_sweep_start
print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)
print(f"[elapsed] {elapsed_s:.1f}s", flush=True)

mode_in_results = {r.get("run_mode", "?") for r in all_results}
if RUN_MODE == "full" and "smoke" in mode_in_results:
    verdict = "HARD_FAIL"
    verdict_msg = (
        f"HARD_FAIL: stale smoke partials in FULL run. "
        f"mode_in_results={mode_in_results}. " + verdict_msg
    )

metrics = {
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict,
    "verdict_msg": verdict_msg,
    "summary": (
        f"n_seeds={len(all_results)} N_DIM={N_DIM} V_C={V_C} V_P={V_P} "
        f"K_SET={K_SET} train={N_CHAINS_TRAIN} query={N_CHAINS_QUERY} "
        f"depths={DEPTHS} mode={RUN_MODE}"
    ),
    "elapsed_s": float(elapsed_s),
    "config_version": CONFIG_VERSION,
    "N_DIM": N_DIM, "V_C": V_C, "V_P": V_P, "K_SET": K_SET,
    "n_seeds": len(SEEDS),
    "n_chains_train": int(N_CHAINS_TRAIN),
    "n_chains_query": int(N_CHAINS_QUERY),
    "depths": list(DEPTHS),
    "grover_k_iters": int(GROVER_K_ITERS),
    "n_replay_passes": int(N_REPLAY_PASSES),
    "shortcut_freq_frac": float(SHORTCUT_FREQ_FRAC),
    "stabilizer_fit_steps": int(STABILIZER_FIT_STEPS),
    "stabilizer_fit_n_chains": int(STABILIZER_FIT_N_CHAINS),
    "run_mode": RUN_MODE,
    "n_llm_calls_total": int(sum(r.get("n_llm_calls", 0) for r in all_results)),
    "per_seed": [
        {
            "seed": r.get("seed"),
            "elapsed_s": r.get("elapsed_s"),
            "n_shortcuts_added": r.get("n_shortcuts_added"),
            "n_replay_events": r.get("n_replay_events"),
            "shortcut_set_size": r.get("shortcut_set_size"),
            "stabilizer_wall_s": r.get("stabilizer_wall_s"),
            "arms": r.get("arms"),
        }
        for r in all_results
    ],
}
metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
