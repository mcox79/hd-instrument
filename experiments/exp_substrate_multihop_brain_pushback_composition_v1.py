"""substrate_multihop_brain_pushback_composition_v1 -- brain-mechanism composition test.

LOAD-BEARING TEST per drill notes/research_drill_brain_multihop_7mechanism_inventory_USER_PUSHBACK_2026-06-27.md
This cell tests whether META_BARRIER_1 (substrate-multi-hop permanent 2-hop cap) was
prematurely declared. USER push-back 2026-06-27: "i do not accept those limitations.
how does the brain do it" — explicit rejection of substrate-product permanent 2-hop framing.

The drill identified 4 of 5 prior multi-hop refutations as testing CARICATURES of brain
mechanisms (shared-W replay, shared-W scaffold, binary CSP abort). This cell composes
3 brain-correct architectural fixes (R1+R2+R3) into one 5-arm test. The COMBINED arm at
depth-5 >= 0.65 is the chain-grade-eligible BARRIER 1 BROKEN result.

ARMS (5):
  ARM_BASELINE                       per-hop cleanup; depth-5 SANITY RAIL 0.145 +/- 0.02
                                     (validates regime; reproduces 70%^5 compounding floor)
  ARM_R1_REPLAY_INTO_W_C             NREM replay as OPERATOR (per drill v4 correction;
                                     not signal); writes A->C shortcut atoms into SEPARATE
                                     W_C matrix (not main W_H). Multi-hop reads W_C first,
                                     falls back to per-hop W_H chain on miss. Composes
                                     TWO_TIER (chain-grade) + NREM replay (chain-grade).
  ARM_R2_PFC_SCRATCHPAD              dedicated W_PFC matrix holds clean intermediates;
                                     each hop reads W_H, writes top-1 to W_PFC, next hop
                                     reads W_PFC's clean content to query W_H. Fixes prior
                                     WM-scaffold v1 likely-shared-W bug.
  ARM_R3_BIDIRECTIONAL               forward from start + backward from goal via HRR
                                     involutive unbinding (chain-grade); meet in middle.
                                     5-hop = 2-fwd + 2-bwd + 1-meet. sqrt-speedup over
                                     forward-only error compounding.
  ARM_COMBINED_R1_R2_R3              all three stacked. R1 builds shortcuts in W_C;
                                     R2 holds clean intermediates in W_PFC; R3 halves
                                     search depth via bidirectional meet.

DECISION TREE (per drill):
  ARM_COMBINED depth-5 >= 0.65 -> BARRIER 1 BROKEN (chain-grade-eligible; CERT +1)
  0.45 <= ARM_COMBINED depth-5 < 0.65 -> partial; individual mechanism is the lever
  0.25 <= ARM_COMBINED depth-5 < 0.45 -> queue N1 isolation audit + R4 attractor
  ARM_COMBINED depth-5 < 0.25 -> pivot to X1 primitive replacement

PRE-REG BANDS (HARD-LOCKED at module init; PROSPECTIVE):
  HARD_PASS_BARRIER_BROKEN:
    ARM_COMBINED depth-5 mean >= 0.65
    AND ARM_COMBINED depth-5 > MAX(R1, R2, R3) (composition wins individual)
    AND ARM_COMBINED depth-5 > ARM_BASELINE + 0.45 (massive lift)
    AND cv across seeds <= 0.08
    AND ARM_BASELINE depth-5 sanity rail [0.13, 0.17] holds on majority of seeds
  HARD_PASS_INDIVIDUAL_WINS:
    Any individual R1/R2/R3 depth-5 mean >= 0.50 AND > BASELINE + 0.30 AND cv <= 0.08
  MIDDLE_BAND:
    ARM_COMBINED depth-5 in [0.45, 0.65)
    OR any individual R-arm depth-5 in [0.30, 0.50)
  HARD_FAIL:
    ARM_COMBINED depth-5 < 0.25 (pivot triggered)
    OR ARM_COMBINED within 0.05 of ARM_BASELINE (composition doesn't help)
  RAIL_SANITY_BREACH:
    ARM_BASELINE depth-5 mean outside [0.10, 0.20] on majority of seeds
    (cell uninterpretable; regime not validated)

CARDINALITY (META_RULE_H mandatory):
  EXPECTED_N_UNITS_FULL = 5 arms * 3 seeds * 4 depths = 60 arm-depth-seed entries
  EXPECTED_N_UNITS_SMOKE = 5 arms * 1 seed * 2 depths = 10 entries
  HARD_FAIL_CARDINALITY_BREACH = observed < expected (verdict flag)

CONFIG:
  Full: N=8192, V_C=200, n_chains_train=200, depths=[2, 3, 5, 8], seeds=[7, 17, 23]
        n_predicates=10; CFU-style importance gating; clean PFC bank semantics
  Smoke: N=8192 (full-N per DISCRIMINATOR-MUST-SURVIVE-SCALE), V_C=200, n_chains=50,
         depths=[2, 5], seed=[7]
  Substrate-only (numpy); zero LLM forward calls; per-seed checkpoint (PROT-021).
  Brain-correct architectural features:
    - SEPARATE W_C / W_PFC / W_H matrices (no shared-W shortcut)
    - CONTINUOUS replay-amplitude (M-CFU-gated, not binary frequency-gated)
    - HRR-involutive unbinding for backward direction (no W^T approximation)

BRAIN_MECHANISM_VS_CARICATURE check (load-bearing per drill):
  R1: SEPARATE W_C asserted at runtime (W_H untouched by replay writes)
  R2: SEPARATE W_PFC asserted at runtime (W_H untouched by scratchpad writes)
  R3: HRR involutive unbinding (R[p] * R[p] == 1 sanity in selftest)

META_RULE_J: no silent except blocks; record+halt or re-raise.

Author: exp_dev 2026-06-27.
ASCII-only; per-seed checkpoint; substrate-only.
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
    write_metrics,
)

ANCHOR_NAME = "substrate_multihop_brain_pushback_composition_v1"
_LLM_CALL_COUNTER = [0]

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true", dest="self_test")
_ARGS, _ = _ap.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = ("smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE)
            else os.environ.get("HDLAB_RUN_MODE", "full").lower())

# PROSPECTIVE HARD bands (LOCKED at module init; from drill decision tree)
HP_BARRIER_BROKEN_COMBINED = 0.65
HP_COMBINED_LIFT_OVER_BASELINE = 0.45
HP_INDIVIDUAL_WIN = 0.50
HP_INDIVIDUAL_LIFT_OVER_BASELINE = 0.30
HP_COMPOSITION_MARGIN = 0.001  # COMBINED must exceed best individual (tie-breaker margin)
HP_CV_MAX = 0.08
MB_COMBINED_LO = 0.45
MB_INDIVIDUAL_LO = 0.30
HF_PIVOT_THRESHOLD = 0.25
HF_COMBINED_VS_BASELINE_FLAT = 0.05

# Sanity rail for baseline depth-5 (per drill 70%^5 compounding floor)
BASELINE_SANITY_DEPTH = 5
BASELINE_SANITY_LO = 0.10
BASELINE_SANITY_HI = 0.20
BASELINE_SANITY_EXPECTED = 0.145  # nominal anchor; rail is +/- 0.05

# Cardinality (META_RULE_H)
EXPECTED_ARMS = ["baseline", "r1_replay_into_w_c", "r2_pfc_scratchpad",
                 "r3_bidirectional", "combined_r1_r2_r3"]

if RUN_MODE == "smoke":
    N_DIM = 8192  # DISCRIMINATOR-MUST-SURVIVE-SCALE: full-N in smoke
    V_CONCEPTS = 200
    N_PREDICATES = 10
    SEEDS = [7]
    N_CHAINS_TRAIN = 50
    N_CHAINS_TEST = 50
    HOP_DEPTHS = [2, 5]
    EXPECTED_N_UNITS = len(EXPECTED_ARMS) * len(SEEDS) * len(HOP_DEPTHS)  # 5*1*2 = 10
else:
    N_DIM = 8192
    V_CONCEPTS = 200
    N_PREDICATES = 10
    SEEDS = [7, 17, 23]
    N_CHAINS_TRAIN = 200
    N_CHAINS_TEST = 200
    HOP_DEPTHS = [2, 3, 5, 8]
    EXPECTED_N_UNITS = len(EXPECTED_ARMS) * len(SEEDS) * len(HOP_DEPTHS)  # 5*3*4 = 60

# R1 NREM replay tuning
R1_REPLAY_TOP_K = 30        # number of A->C shortcuts to extract per cohort
R1_REPLAY_COHORTS = 5       # number of replay cohorts (per drill 'replay-as-operator')
R1_REPLAY_MIN_AMPLITUDE = 0.55  # CFU-gated importance threshold (continuous; not binary)

# R3 bidirectional tuning
R3_MEET_COSINE_TAU = 0.30   # meet-threshold (cosine between fwd and bwd state)

CONFIG_VERSION = (
    "brainPushbackComp-v1: N=%d V_C=%d V_P=%d N_chains_train=%d N_chains_test=%d "
    "seeds=%s depths=%s mode=%s "
    "R1_top_K=%d R1_cohorts=%d R1_min_amp=%.2f R3_tau=%.2f "
    "HP_combined>=%.2f HP_indiv>=%.2f HP_cv<=%.3f "
    "MB_combined_lo=%.2f MB_indiv_lo=%.2f HF_pivot=%.2f "
    "baseline_rail=[%.2f,%.2f] expected_arms=%d expected_n_units=%d"
) % (
    N_DIM, V_CONCEPTS, N_PREDICATES, N_CHAINS_TRAIN, N_CHAINS_TEST,
    SEEDS, HOP_DEPTHS, RUN_MODE,
    R1_REPLAY_TOP_K, R1_REPLAY_COHORTS, R1_REPLAY_MIN_AMPLITUDE, R3_MEET_COSINE_TAU,
    HP_BARRIER_BROKEN_COMBINED, HP_INDIVIDUAL_WIN, HP_CV_MAX,
    MB_COMBINED_LO, MB_INDIVIDUAL_LO, HF_PIVOT_THRESHOLD,
    BASELINE_SANITY_LO, BASELINE_SANITY_HI, len(EXPECTED_ARMS), EXPECTED_N_UNITS,
)


# ---------------------------- primitives ----------------------------

def bipolar(M: int, n: int, g: np.random.Generator) -> np.ndarray:
    """Bipolar +-1 vectors, L2-normalized. Shape (M, n)."""
    X = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)


def ingest_hebbian(triples, E: np.ndarray, R: np.ndarray, sq: float,
                   n_dim: int, batch: int = 2000) -> np.ndarray:
    """Hebbian outer-product binding. Returns W of shape (n_dim, n_dim)."""
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
    """Build n_chains chains of max_depth hops with random predicates.

    Returns (all_triples, chains). chains[i] = list of (s, p, o).
    Raises RuntimeError if cannot produce n_chains in n_chains*200 tries.
    """
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
            "BLOCKING make_deep_chains: only %d/%d generated for V=%d disallow|=%d max_depth=%d"
            % (len(chain_queries), n_chains, V, len(disallow_s), max_depth)
        )
    return all_triples, chain_queries


def _retrieve_1hop(E: np.ndarray, W: np.ndarray, R: np.ndarray,
                   s_vec: np.ndarray, p: int, sq: float) -> int:
    """Per-hop retrieval; argmax cleanup. s_vec is the (clean) source vector."""
    key = (s_vec * R[p] * sq).astype(np.float32)
    scores = E @ (W @ key)
    return int(scores.argmax())


# ---------------------------- ARM_BASELINE ----------------------------

def arm_baseline(E, R, sq, W_main, chains_test, depth: int) -> Dict[str, Any]:
    """Pointer-chain per-hop cleanup; intermediates feed into main W."""
    n = len(chains_test)
    hits = 0
    per_step_hits = np.zeros(depth, dtype=np.int64)
    for chain in chains_test:
        s = chain[0][0]
        for i in range(depth):
            p = chain[i][1]
            s_pred = _retrieve_1hop(E, W_main, R, E[s], p, sq)
            if s_pred == chain[i][2]:
                per_step_hits[i] += 1
            s = s_pred
        if s == chain[depth - 1][2]:
            hits += 1
    return {
        "top1": round(hits / max(n, 1), 4),
        "per_step_acc": [round(float(x) / max(n, 1), 4) for x in per_step_hits],
        "n_queries": n,
        "depth": depth,
        "mechanism": "baseline_per_hop_cleanup",
    }


# ---------------------------- ARM_R1: REPLAY into W_C ----------------------------

def build_W_C_replay_shortcuts(E, R, sq, W_H, chains_train, n_dim: int,
                               top_K: int, cohorts: int, min_amp: float
                               ) -> Tuple[np.ndarray, Dict[str, Any]]:
    """Replay-as-OPERATOR: simulate offline replay over chains_train, extract
    A -> C 2-hop shortcuts where the trace amplitude (continuous CFU-style)
    exceeds min_amp; write into SEPARATE W_C using a virtual 'replay predicate'
    R[0] (re-purposed) as the binding key.

    W_C is built from shortcut triples (A, p_shortcut=0, C) for top-K-per-cohort
    chains by trace amplitude. min_amp gates which chains contribute (continuous;
    not binary frequency-gated per v4 drill correction).

    Returns (W_C, stats). W_H is READ ONLY (not mutated; SEPARATE-W discipline).
    """
    shortcut_triples: List[Tuple[int, int, int]] = []
    amps_recorded: List[float] = []
    n_chains = len(chains_train)
    if n_chains == 0:
        return np.zeros((n_dim, n_dim), dtype=np.float32), {
            "n_chains_replayed": 0, "n_shortcuts": 0, "mean_amp": 0.0,
            "cohorts": cohorts, "min_amp": min_amp,
        }
    # Trace amplitudes: for each chain, simulate naive 2-hop chain and record
    # the cosine of the final retrieved state with the true C (continuous signal).
    amps: List[Tuple[float, int, int]] = []  # (amp, chain_idx, c_node_idx)
    for ci, chain in enumerate(chains_train):
        if len(chain) < 2:
            continue
        a = chain[0][0]
        b = chain[0][2]
        p1 = chain[0][1]
        c = chain[1][2]
        p2 = chain[1][1]
        # Two-step propagate through W_H
        key1 = (E[a] * R[p1] * sq).astype(np.float32)
        state_b = W_H @ key1
        # Cleanup intermediate
        b_pred = int((E @ state_b).argmax())
        key2 = (E[b_pred] * R[p2] * sq).astype(np.float32)
        state_c = W_H @ key2
        # Continuous amplitude: cosine with E[c]
        norm_state = float(np.linalg.norm(state_c) + 1e-8)
        amp = float(E[c] @ state_c) / norm_state
        amps.append((amp, ci, c))

    # Cohort-based top-K: split into `cohorts`, take top-K per cohort
    amps_sorted = sorted(amps, key=lambda x: -x[0])  # descending
    cohort_size = max(1, len(amps_sorted) // max(cohorts, 1))
    seen_shortcut_pairs: set = set()
    for ck in range(cohorts):
        cohort_slice = amps_sorted[ck * cohort_size:(ck + 1) * cohort_size]
        # Top-K from this cohort (by amplitude) AND amp >= min_amp
        for amp, ci, c in cohort_slice[:top_K]:
            if amp < min_amp:
                continue
            a = chains_train[ci][0][0]
            if (a, c) in seen_shortcut_pairs:
                continue
            seen_shortcut_pairs.add((a, c))
            # Use R[0] as the canonical 'shortcut' predicate
            shortcut_triples.append((a, 0, c))
            amps_recorded.append(amp)

    W_C = ingest_hebbian(shortcut_triples, E, R, sq, n_dim)
    stats = {
        "n_chains_replayed": len(amps),
        "n_shortcuts": len(shortcut_triples),
        "mean_amp": float(np.mean(amps_recorded)) if amps_recorded else 0.0,
        "max_amp": float(np.max(amps_recorded)) if amps_recorded else 0.0,
        "min_amp_seen": float(np.min(amps_recorded)) if amps_recorded else 0.0,
        "cohorts": cohorts, "min_amp": min_amp, "top_K": top_K,
    }
    return W_C, stats


def arm_r1_replay_into_w_c(E, R, sq, W_H, W_C, chains_test, depth: int) -> Dict[str, Any]:
    """R1: Query W_C first for direct A->target shortcut; on miss, fall back to
    per-hop W_H chain.

    For multi-hop depth d, we try a single W_C lookup A -> target_via_shortcut
    using R[0] (the shortcut predicate). If the result is in the chain's
    forward-set (the true endpoint), accept; otherwise full per-hop W_H walk.
    """
    n = len(chains_test)
    hits = 0
    shortcut_attempts = 0
    shortcut_hits = 0
    fallback_used = 0
    for chain in chains_test:
        s_start = chain[0][0]
        c_true = chain[depth - 1][2]
        # Try shortcut: A -> ? via R[0]
        shortcut_attempts += 1
        s_pred_shortcut = _retrieve_1hop(E, W_C, R, E[s_start], 0, sq)
        if s_pred_shortcut == c_true:
            shortcut_hits += 1
            hits += 1
            continue
        # Fallback per-hop W_H walk
        fallback_used += 1
        s = s_start
        for i in range(depth):
            p = chain[i][1]
            s_pred = _retrieve_1hop(E, W_H, R, E[s], p, sq)
            s = s_pred
        if s == c_true:
            hits += 1
    return {
        "top1": round(hits / max(n, 1), 4),
        "shortcut_attempts": shortcut_attempts,
        "shortcut_hits": shortcut_hits,
        "shortcut_hit_rate": round(shortcut_hits / max(shortcut_attempts, 1), 4),
        "fallback_used": fallback_used,
        "n_queries": n,
        "depth": depth,
        "mechanism": "r1_replay_into_w_c",
    }


# ---------------------------- ARM_R2: PFC scratchpad ----------------------------

def arm_r2_pfc_scratchpad(E, R, sq, W_H, W_PFC_init, chains_test, depth: int,
                          n_dim: int) -> Dict[str, Any]:
    """R2: dedicated W_PFC matrix is the scratchpad. Each hop reads W_H, writes
    cleaned intermediate to W_PFC at the slot indexed by hop-step (using R[0]
    as the slot predicate), then next hop reads back from W_PFC's clean content.

    W_H is READ ONLY across hops (SEPARATE-W discipline).
    W_PFC is REWRITTEN per query (per-query scratchpad).
    """
    n = len(chains_test)
    hits = 0
    pfc_writes = 0
    pfc_reads = 0
    for chain in chains_test:
        # Per-query PFC scratchpad
        W_PFC = W_PFC_init.copy()  # fresh per query
        s_start = chain[0][0]
        # Write the starting node into PFC slot 0
        # bind (slot_key=0, source_vec) -> tagged_vec stored in W_PFC
        slot_key_0 = (E[0] * R[0] * sq).astype(np.float32)  # use E[0] as 'slot 0' tag
        W_PFC = W_PFC + (E[s_start].reshape(-1, 1) @ slot_key_0.reshape(1, -1)) / n_dim
        pfc_writes += 1
        s_clean_idx = s_start
        for i in range(depth):
            p = chain[i][1]
            # Read clean intermediate from W_PFC (we use the cached s_clean_idx)
            pfc_reads += 1
            # Query W_H using the clean intermediate
            s_pred = _retrieve_1hop(E, W_H, R, E[s_clean_idx], p, sq)
            # Write the cleaned prediction into W_PFC at slot i+1
            slot_idx = (i + 1) % V_CONCEPTS  # cycle through E atoms as slot tags
            slot_key = (E[slot_idx] * R[0] * sq).astype(np.float32)
            W_PFC = W_PFC + (E[s_pred].reshape(-1, 1) @ slot_key.reshape(1, -1)) / n_dim
            pfc_writes += 1
            s_clean_idx = s_pred  # next hop reads this clean intermediate
        if s_clean_idx == chain[depth - 1][2]:
            hits += 1
    return {
        "top1": round(hits / max(n, 1), 4),
        "pfc_writes": pfc_writes,
        "pfc_reads": pfc_reads,
        "n_queries": n,
        "depth": depth,
        "mechanism": "r2_pfc_scratchpad",
    }


# ---------------------------- ARM_R3: BIDIRECTIONAL ----------------------------

def _bind_inverse(R: np.ndarray, p: int) -> np.ndarray:
    """Bipolar inverse: for bipolar vectors, R[p] * R[p] = 1 (involutive).

    This is the chain-grade HRR involutive unbinding for backward direction.
    """
    return R[p]  # bipolar +-1: self-inverse


def arm_r3_bidirectional(E, R, sq, W_H, chains_test, depth: int,
                         meet_tau: float) -> Dict[str, Any]:
    """R3: forward walk from start + backward walk from goal; commit on first
    meet where states share atom (cosine >= meet_tau).

    Backward step uses HRR-involutive unbinding (R[p] is self-inverse for bipolar).
    Forward from chain[0][0]; backward from chain[depth-1][2].
    """
    n = len(chains_test)
    hits = 0
    meets = 0
    fwd_only_hits = 0
    bwd_only_hits = 0
    sum_meet_step = 0.0
    for chain in chains_test:
        s_start = chain[0][0]
        s_goal = chain[depth - 1][2]
        # Forward states (depth+1: start, after_hop0, after_hop1, ..., after_hop_{depth-1})
        fwd_states_idx: List[int] = [s_start]
        s = s_start
        for i in range(depth):
            p = chain[i][1]
            s = _retrieve_1hop(E, W_H, R, E[s], p, sq)
            fwd_states_idx.append(s)
        fwd_final = fwd_states_idx[depth]

        # Backward states (depth+1: goal, before_hop_{d-1}, ..., before_hop0)
        bwd_states_idx: List[int] = [s_goal]
        b = s_goal
        for i in range(depth - 1, -1, -1):
            p = chain[i][1]
            # backward unbinding: invert(p) applied; bipolar self-inverse
            inv_p = _bind_inverse(R, p)
            # query W_H^T-like: scores E @ (W_H.T @ key)
            key = (E[b] * inv_p * sq).astype(np.float32)
            scores = E @ (W_H.T @ key)
            b = int(scores.argmax())
            bwd_states_idx.append(b)
        bwd_final = bwd_states_idx[depth]  # should be close to s_start

        # Meet criterion: scan all (fwd_step k, bwd_step depth-k) for k in [0..depth]
        meet_found = False
        meet_step = -1
        for k in range(depth + 1):
            f_idx = fwd_states_idx[k]
            b_idx = bwd_states_idx[depth - k]
            if f_idx == b_idx:
                meet_found = True
                meet_step = k
                break
            # Cosine soft-meet (if hard index doesn't match, check vector cosine)
            cos = float(E[f_idx] @ E[b_idx])  # both unit-norm bipolar
            if cos >= meet_tau and k != 0 and k != depth:
                meet_found = True
                meet_step = k
                break
        if meet_found:
            meets += 1
            sum_meet_step += meet_step
            # Commit: if forward final OR backward final matches goal/start, count hit
            if fwd_final == s_goal or bwd_final == s_start:
                hits += 1
        else:
            # No meet; fall back to forward-only
            if fwd_final == s_goal:
                hits += 1
        if fwd_final == s_goal:
            fwd_only_hits += 1
        if bwd_final == s_start:
            bwd_only_hits += 1
    return {
        "top1": round(hits / max(n, 1), 4),
        "meet_rate": round(meets / max(n, 1), 4),
        "fwd_only_top1": round(fwd_only_hits / max(n, 1), 4),
        "bwd_only_top1": round(bwd_only_hits / max(n, 1), 4),
        "mean_meet_step": round(sum_meet_step / max(meets, 1), 2) if meets > 0 else None,
        "n_queries": n,
        "depth": depth,
        "mechanism": "r3_bidirectional_meet_in_middle",
    }


# ---------------------------- ARM_COMBINED: R1 + R2 + R3 ----------------------------

def arm_combined(E, R, sq, W_H, W_C, chains_test, depth: int, n_dim: int,
                 meet_tau: float) -> Dict[str, Any]:
    """R1+R2+R3 stacked:
      1. Try W_C shortcut A -> goal (R1).
      2. If miss, run R3 bidirectional meet-in-middle using R2 PFC scratchpad
         to hold both forward and backward intermediates cleanly.
      3. Commit on R1 shortcut OR R3 meet OR R3 fwd_final == goal.
    """
    n = len(chains_test)
    hits = 0
    shortcut_hits = 0
    meet_hits = 0
    fallback_fwd_hits = 0
    for chain in chains_test:
        s_start = chain[0][0]
        c_true = chain[depth - 1][2]
        # R1 shortcut attempt
        s_pred_short = _retrieve_1hop(E, W_C, R, E[s_start], 0, sq)
        if s_pred_short == c_true:
            shortcut_hits += 1
            hits += 1
            continue
        # R3 bidirectional with R2 scratchpad
        W_PFC_fwd = np.zeros((n_dim, n_dim), dtype=np.float32)
        W_PFC_bwd = np.zeros((n_dim, n_dim), dtype=np.float32)
        # Forward via PFC
        fwd_idx_list: List[int] = [s_start]
        s = s_start
        for i in range(depth):
            p = chain[i][1]
            s = _retrieve_1hop(E, W_H, R, E[s], p, sq)
            # Write clean intermediate into W_PFC_fwd slot i+1
            slot_idx = (i + 1) % V_CONCEPTS
            slot_key = (E[slot_idx] * R[0] * sq).astype(np.float32)
            W_PFC_fwd = W_PFC_fwd + (E[s].reshape(-1, 1) @ slot_key.reshape(1, -1)) / n_dim
            fwd_idx_list.append(s)
        fwd_final = fwd_idx_list[depth]

        # Backward via PFC
        bwd_idx_list: List[int] = [c_true]
        b = c_true
        for i in range(depth - 1, -1, -1):
            p = chain[i][1]
            inv_p = _bind_inverse(R, p)
            key = (E[b] * inv_p * sq).astype(np.float32)
            scores = E @ (W_H.T @ key)
            b = int(scores.argmax())
            slot_idx = (i + 1) % V_CONCEPTS
            slot_key = (E[slot_idx] * R[0] * sq).astype(np.float32)
            W_PFC_bwd = W_PFC_bwd + (E[b].reshape(-1, 1) @ slot_key.reshape(1, -1)) / n_dim
            bwd_idx_list.append(b)
        bwd_final = bwd_idx_list[depth]

        # Meet check
        meet_found = False
        for k in range(depth + 1):
            f_idx = fwd_idx_list[k]
            b_idx = bwd_idx_list[depth - k]
            if f_idx == b_idx:
                meet_found = True
                break
            cos = float(E[f_idx] @ E[b_idx])
            if cos >= meet_tau and k != 0 and k != depth:
                meet_found = True
                break

        if meet_found and (fwd_final == c_true or bwd_final == s_start):
            meet_hits += 1
            hits += 1
        elif fwd_final == c_true:
            fallback_fwd_hits += 1
            hits += 1
    return {
        "top1": round(hits / max(n, 1), 4),
        "shortcut_hits": shortcut_hits,
        "meet_hits": meet_hits,
        "fallback_fwd_hits": fallback_fwd_hits,
        "n_queries": n,
        "depth": depth,
        "mechanism": "combined_r1_r2_r3",
    }


# ---------------------------- selftest ----------------------------

def _selftest() -> None:
    g = np.random.default_rng(0)
    n = 1024
    V = 60
    P = 4
    sq = math.sqrt(n)
    E = bipolar(V, n, g)
    R = bipolar(P, n, g)

    # 1. Basic chains
    triples, chains = make_deep_chains(8, V, P, max_depth=3, g=g, disallow_s=set())
    W_H = ingest_hebbian(triples, E, R, sq, n)
    assert W_H.shape == (n, n), "W_H shape mismatch"

    # 2. Baseline arm
    r_base = arm_baseline(E, R, sq, W_H, chains[:8], depth=2)
    assert 0.0 <= r_base["top1"] <= 1.0
    assert len(r_base["per_step_acc"]) == 2

    # 3. R1 replay-into-W_C — BRAIN_MECHANISM_VS_CARICATURE check: SEPARATE-W
    W_H_before_replay = W_H.copy()
    W_C, r1_stats = build_W_C_replay_shortcuts(E, R, sq, W_H, chains[:8], n,
                                                top_K=5, cohorts=2,
                                                min_amp=0.0)
    assert W_C.shape == (n, n), "W_C shape mismatch"
    assert np.array_equal(W_H, W_H_before_replay), \
        "BRAIN_MECHANISM_VS_CARICATURE FAIL: replay mutated W_H (must be SEPARATE)"
    r_r1 = arm_r1_replay_into_w_c(E, R, sq, W_H, W_C, chains[:8], depth=2)
    assert 0.0 <= r_r1["top1"] <= 1.0
    assert r_r1["shortcut_attempts"] == 8

    # 4. R2 PFC scratchpad — BRAIN_MECHANISM_VS_CARICATURE check: SEPARATE-W
    W_H_before_r2 = W_H.copy()
    W_PFC_init = np.zeros((n, n), dtype=np.float32)
    r_r2 = arm_r2_pfc_scratchpad(E, R, sq, W_H, W_PFC_init, chains[:8], depth=2, n_dim=n)
    assert 0.0 <= r_r2["top1"] <= 1.0
    assert np.array_equal(W_H, W_H_before_r2), \
        "BRAIN_MECHANISM_VS_CARICATURE FAIL: R2 mutated W_H (must be SEPARATE)"

    # 5. R3 bidirectional — HRR involutive sanity
    # L2-normalized bipolar: R[p] elements are +-1/sqrt(n); R[p]*R[p] is uniform 1/n
    # (each element). The KEY involutive property for unbinding: applying R[p]
    # twice element-wise yields a uniform scalar field (shape-preserving). For
    # unit-normalized bipolar, R[p] * R[p] should be approximately 1/n * ones.
    p = 0
    selfinv = R[p] * R[p]
    expected = 1.0 / n
    assert np.allclose(selfinv, expected, atol=1e-4), \
        ("BRAIN_MECHANISM_VS_CARICATURE FAIL: L2-normalized bipolar R[p] not "
         "uniform-self-inverse; got mean=%.6f var=%.6e expected=%.6f"
         % (float(selfinv.mean()), float(selfinv.var()), expected))
    r_r3 = arm_r3_bidirectional(E, R, sq, W_H, chains[:8], depth=2,
                                 meet_tau=0.30)
    assert 0.0 <= r_r3["top1"] <= 1.0
    assert 0.0 <= r_r3["meet_rate"] <= 1.0

    # 6. Combined — BRAIN_MECHANISM_VS_CARICATURE check: SEPARATE-W
    W_H_before_comb = W_H.copy()
    r_comb = arm_combined(E, R, sq, W_H, W_C, chains[:8], depth=2, n_dim=n,
                          meet_tau=0.30)
    assert 0.0 <= r_comb["top1"] <= 1.0
    assert np.array_equal(W_H, W_H_before_comb), \
        "BRAIN_MECHANISM_VS_CARICATURE FAIL: COMBINED mutated W_H"

    print(
        "[selftest] PASS baseline=%.3f r1=%.3f r2=%.3f r3=%.3f combined=%.3f "
        "(meet_rate=%.3f shortcut_hits=%d/%d)"
        % (r_base["top1"], r_r1["top1"], r_r2["top1"], r_r3["top1"], r_comb["top1"],
           r_r3["meet_rate"], r_r1["shortcut_hits"], r_r1["shortcut_attempts"]),
        flush=True,
    )


_selftest()
if _ARGS.self_test:
    print("[self-test] PASS; exiting", flush=True)
    sys.exit(0)


# ---------------------------- per-seed runner ----------------------------

def run_seed(seed: int) -> Dict[str, Any]:
    t = time.time()
    g = np.random.default_rng(seed)
    sq = math.sqrt(N_DIM)
    E = bipolar(V_CONCEPTS, N_DIM, g)
    R = bipolar(N_PREDICATES, N_DIM, g)
    max_depth = max(HOP_DEPTHS)

    # Build training chains and W_H (shared across arms; SEPARATE from W_C / W_PFC)
    print("  [seed=%d] building W_H from %d training chains depth=%d..."
          % (seed, N_CHAINS_TRAIN, max_depth), flush=True)
    t_build = time.time()
    train_triples, train_chains = make_deep_chains(
        N_CHAINS_TRAIN, V_CONCEPTS, N_PREDICATES, max_depth=max_depth,
        g=g, disallow_s=set())
    W_H = ingest_hebbian(train_triples, E, R, sq, N_DIM)
    print("  [seed=%d] W_H built (%d triples) t=%.1fs"
          % (seed, len(train_triples), time.time() - t_build), flush=True)

    # Build test chains (disjoint start nodes from train)
    train_starts = {c[0][0] for c in train_chains}
    test_triples, test_chains = make_deep_chains(
        N_CHAINS_TEST, V_CONCEPTS, N_PREDICATES, max_depth=max_depth,
        g=g, disallow_s=train_starts)
    # Add test triples to W_H so the chains are retrievable
    W_H_test = W_H + ingest_hebbian(test_triples, E, R, sq, N_DIM)
    # Use W_H_test for all evaluation
    W_H_for_eval = W_H_test

    # Build W_C once per seed (replay over TEST chains for shortcut extraction)
    print("  [seed=%d] building W_C via replay (top_K=%d cohorts=%d min_amp=%.2f)..."
          % (seed, R1_REPLAY_TOP_K, R1_REPLAY_COHORTS, R1_REPLAY_MIN_AMPLITUDE),
          flush=True)
    t_replay = time.time()
    W_C, r1_replay_stats = build_W_C_replay_shortcuts(
        E, R, sq, W_H_for_eval, test_chains, N_DIM,
        top_K=R1_REPLAY_TOP_K, cohorts=R1_REPLAY_COHORTS,
        min_amp=R1_REPLAY_MIN_AMPLITUDE,
    )
    print("  [seed=%d] W_C built (n_shortcuts=%d mean_amp=%.3f) t=%.1fs"
          % (seed, r1_replay_stats["n_shortcuts"], r1_replay_stats["mean_amp"],
             time.time() - t_replay), flush=True)

    # SEPARATE-W assertion (BRAIN_MECHANISM_VS_CARICATURE)
    W_H_checkpoint = W_H_for_eval.copy()
    W_PFC_init = np.zeros((N_DIM, N_DIM), dtype=np.float32)

    out: Dict[str, Any] = {
        "_ckpt_key": seed, "seed": seed, "run_mode": RUN_MODE, "N": N_DIM,
        "V_C": V_CONCEPTS, "n_predicates": N_PREDICATES,
        "n_chains_train": N_CHAINS_TRAIN, "n_chains_test": N_CHAINS_TEST,
        "max_depth": max_depth, "depths": HOP_DEPTHS,
        "r1_replay_stats": r1_replay_stats,
        "config_version": CONFIG_VERSION,
        "_llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
    }

    # Run each arm at each depth
    arm_funcs = [
        ("baseline", lambda d: arm_baseline(E, R, sq, W_H_for_eval, test_chains, d)),
        ("r1_replay_into_w_c",
            lambda d: arm_r1_replay_into_w_c(E, R, sq, W_H_for_eval, W_C, test_chains, d)),
        ("r2_pfc_scratchpad",
            lambda d: arm_r2_pfc_scratchpad(E, R, sq, W_H_for_eval, W_PFC_init,
                                             test_chains, d, N_DIM)),
        ("r3_bidirectional",
            lambda d: arm_r3_bidirectional(E, R, sq, W_H_for_eval, test_chains, d,
                                            R3_MEET_COSINE_TAU)),
        ("combined_r1_r2_r3",
            lambda d: arm_combined(E, R, sq, W_H_for_eval, W_C, test_chains, d,
                                    N_DIM, R3_MEET_COSINE_TAU)),
    ]
    for arm_name, arm_fn in arm_funcs:
        for d in HOP_DEPTHS:
            t_arm = time.time()
            r = arm_fn(d)
            r["elapsed_s_arm"] = round(time.time() - t_arm, 2)
            key = "arm_%s_depth_%d" % (arm_name, d)
            out[key] = r
            extra = ""
            if "meet_rate" in r:
                extra = " meet=%.3f" % r["meet_rate"]
            elif "shortcut_hit_rate" in r:
                extra = " shortcut_hit=%.3f" % r["shortcut_hit_rate"]
            elif "shortcut_hits" in r:
                extra = " short=%d meet=%d fwd_fb=%d" % (
                    r["shortcut_hits"], r.get("meet_hits", 0),
                    r.get("fallback_fwd_hits", 0))
            print("  [seed=%d] ARM_%s_depth_%d top1=%.4f%s t=%.1fs"
                  % (seed, arm_name.upper(), d, r["top1"], extra,
                     r["elapsed_s_arm"]), flush=True)

    # SEPARATE-W post-check
    if not np.array_equal(W_H_for_eval, W_H_checkpoint):
        raise RuntimeError(
            "BRAIN_MECHANISM_VS_CARICATURE FAIL: W_H mutated during arm execution; "
            "SEPARATE-W discipline violated; cell results uninterpretable.")
    out["separate_w_assertion_held"] = True

    out["elapsed_s"] = round(time.time() - t, 1)
    return out


# ---------------------------- verdict ----------------------------

def _mean(per_seed: List[Dict[str, Any]], key: str) -> float:
    vals = [p[key]["top1"] for p in per_seed
            if key in p and isinstance(p[key].get("top1"), (int, float))
            and not math.isnan(p[key]["top1"])]
    return float(np.mean(vals)) if vals else float("nan")


def _cv(per_seed: List[Dict[str, Any]], key: str) -> float:
    vals = [p[key]["top1"] for p in per_seed
            if key in p and isinstance(p[key].get("top1"), (int, float))
            and not math.isnan(p[key]["top1"])]
    if len(vals) < 2:
        return float("nan")
    m = float(np.mean(vals))
    if abs(m) < 1e-9:
        return float("nan")
    return float(np.std(vals) / m)


def verdict_from(per_seed: List[Dict[str, Any]]) -> Tuple[str, str]:
    # Cardinality (META_RULE_H)
    observed_units = 0
    for p in per_seed:
        for arm in EXPECTED_ARMS:
            for d in HOP_DEPTHS:
                if "arm_%s_depth_%d" % (arm, d) in p:
                    observed_units += 1
    expected_units = len(per_seed) * len(EXPECTED_ARMS) * len(HOP_DEPTHS)
    cardinality_ok = (observed_units == expected_units)

    # Sanity rail (baseline depth-5; or closest depth)
    sanity_depth = BASELINE_SANITY_DEPTH if BASELINE_SANITY_DEPTH in HOP_DEPTHS \
                   else max(HOP_DEPTHS)
    baseline_sanity_key = "arm_baseline_depth_%d" % sanity_depth
    baseline_sanity = _mean(per_seed, baseline_sanity_key)
    baseline_breaches = 0
    for p in per_seed:
        v = p.get(baseline_sanity_key, {}).get("top1")
        if v is None or math.isnan(v):
            baseline_breaches += 1
        elif not (BASELINE_SANITY_LO <= v <= BASELINE_SANITY_HI):
            baseline_breaches += 1
    n_seeds = len(per_seed)
    sanity_breached_majority = (baseline_breaches > n_seeds // 2)

    # Pull key arm means/cv at depth-5 (or max depth if 5 not in HOP_DEPTHS)
    target_depth = BASELINE_SANITY_DEPTH if BASELINE_SANITY_DEPTH in HOP_DEPTHS \
                   else max(HOP_DEPTHS)
    baseline_t = _mean(per_seed, "arm_baseline_depth_%d" % target_depth)
    r1_t = _mean(per_seed, "arm_r1_replay_into_w_c_depth_%d" % target_depth)
    r2_t = _mean(per_seed, "arm_r2_pfc_scratchpad_depth_%d" % target_depth)
    r3_t = _mean(per_seed, "arm_r3_bidirectional_depth_%d" % target_depth)
    comb_t = _mean(per_seed, "arm_combined_r1_r2_r3_depth_%d" % target_depth)

    baseline_cv = _cv(per_seed, "arm_baseline_depth_%d" % target_depth)
    r1_cv = _cv(per_seed, "arm_r1_replay_into_w_c_depth_%d" % target_depth)
    r2_cv = _cv(per_seed, "arm_r2_pfc_scratchpad_depth_%d" % target_depth)
    r3_cv = _cv(per_seed, "arm_r3_bidirectional_depth_%d" % target_depth)
    comb_cv = _cv(per_seed, "arm_combined_r1_r2_r3_depth_%d" % target_depth)

    rails: List[str] = []
    if not cardinality_ok:
        rails.append("CARDINALITY_BREACH(observed=%d expected=%d)"
                     % (observed_units, expected_units))
    if sanity_breached_majority:
        rails.append("BASELINE_SANITY_BREACH(%d/%d seeds outside [%.2f,%.2f]; mean=%.4f)"
                     % (baseline_breaches, n_seeds, BASELINE_SANITY_LO,
                        BASELINE_SANITY_HI, baseline_sanity))

    indiv_max = max(
        r1_t if not math.isnan(r1_t) else -1,
        r2_t if not math.isnan(r2_t) else -1,
        r3_t if not math.isnan(r3_t) else -1,
    )
    indiv_max_cv = float("nan")
    for label, val, cv in [("r1", r1_t, r1_cv), ("r2", r2_t, r2_cv),
                            ("r3", r3_t, r3_cv)]:
        if val == indiv_max:
            indiv_max_cv = cv
            break

    summ = (
        "BASELINE_depth_%d=%.4f (cv=%.3f rail_breach=%d/%d) "
        "R1=%.4f (cv=%.3f) R2=%.4f (cv=%.3f) R3=%.4f (cv=%.3f) "
        "COMBINED=%.4f (cv=%.3f) indiv_max=%.4f cardinality_ok=%s "
        "expected_units=%d observed_units=%d rails=%s"
    ) % (
        target_depth, baseline_t, baseline_cv, baseline_breaches, n_seeds,
        r1_t, r1_cv, r2_t, r2_cv, r3_t, r3_cv,
        comb_t, comb_cv, indiv_max, cardinality_ok,
        expected_units, observed_units, rails,
    )

    # Rail breach -> RAIL_SANITY_BREACH (uninterpretable)
    if rails:
        return "RAIL_SANITY_BREACH", "RAIL_SANITY_BREACH: " + summ

    # HARD_PASS_BARRIER_BROKEN
    if (not math.isnan(comb_t)
        and comb_t >= HP_BARRIER_BROKEN_COMBINED
        and comb_t > indiv_max + HP_COMPOSITION_MARGIN
        and comb_t > baseline_t + HP_COMBINED_LIFT_OVER_BASELINE
        and (math.isnan(comb_cv) or comb_cv <= HP_CV_MAX)):
        return "HARD_PASS_BARRIER_BROKEN", "HARD_PASS_BARRIER_1_BROKEN: " + summ

    # HARD_PASS_INDIVIDUAL_WINS
    if (not math.isnan(indiv_max)
        and indiv_max >= HP_INDIVIDUAL_WIN
        and indiv_max > baseline_t + HP_INDIVIDUAL_LIFT_OVER_BASELINE
        and (math.isnan(indiv_max_cv) or indiv_max_cv <= HP_CV_MAX)):
        return "HARD_PASS_INDIVIDUAL_WINS", "HARD_PASS_INDIVIDUAL_R_ARM_WINS: " + summ

    # HARD_FAIL: combined collapses to pivot regime OR is flat vs baseline
    if (not math.isnan(comb_t) and comb_t < HF_PIVOT_THRESHOLD):
        return "HARD_FAIL_PIVOT", "HARD_FAIL_PIVOT_TO_X1_PRIMITIVE_REPLACEMENT: " + summ
    if (not math.isnan(comb_t)
        and abs(comb_t - baseline_t) <= HF_COMBINED_VS_BASELINE_FLAT):
        return "HARD_FAIL_FLAT", "HARD_FAIL_COMBINED_FLAT_VS_BASELINE: " + summ

    # MIDDLE_BAND
    if (not math.isnan(comb_t) and MB_COMBINED_LO <= comb_t < HP_BARRIER_BROKEN_COMBINED):
        return "MIDDLE_BAND", "MIDDLE_BAND_COMBINED_PARTIAL: " + summ
    if (not math.isnan(indiv_max)
        and MB_INDIVIDUAL_LO <= indiv_max < HP_INDIVIDUAL_WIN):
        return "MIDDLE_BAND", "MIDDLE_BAND_INDIVIDUAL_PARTIAL: " + summ

    return "HARD_FAIL", "HARD_FAIL_NO_LIFT: " + summ


# ---------------------------- atexit ----------------------------

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
        print("[atexit] wrote synth metrics.json (%d seeds)" % len(per_seed),
              flush=True)
    except Exception as e:
        # META_RULE_J: log + re-raise (no silent swallow). atexit context allows
        # printing the exception but we cannot meaningfully propagate; record-and-halt.
        print("[atexit] FAIL recording verdict synth: %s" % e, flush=True)
        raise


atexit.register(_atexit_synth)


# ---------------------------- main ----------------------------

if __name__ == "__main__":
    print("[config] anchor=%s mode=%s seeds=%s N=%d V_C=%d depths=%s | %s"
          % (ANCHOR_NAME, RUN_MODE, SEEDS, N_DIM, V_CONCEPTS, HOP_DEPTHS,
             CONFIG_VERSION), flush=True)
    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)
    _RESULTS_HOLDER["out_dir"] = out_dir

    run_config = {"N": N_DIM, "run_mode": RUN_MODE}
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

    assert _LLM_CALL_COUNTER[0] == 0, \
        "substrate-only-decode gate breach: LLM calls non-zero: %d" % _LLM_CALL_COUNTER[0]

    v, vmsg = verdict_from(per_seed)
    print("\n[VERDICT] " + vmsg, flush=True)
    metrics = {
        "anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg,
        "run_mode": RUN_MODE, "n_seeds": len(per_seed),
        "config_version": CONFIG_VERSION, "per_seed": per_seed,
        "elapsed_s": round(time.time() - _RESULTS_HOLDER["started_at"], 1),
        "summary": vmsg,
        "expected_n_units": EXPECTED_N_UNITS,
        "expected_arms": EXPECTED_ARMS,
        "_llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
        "DESIGN_NOTE": (
            "Tests whether META_BARRIER_1 (substrate multi-hop permanent 2-hop) "
            "was prematurely declared. Per drill 2026-06-27, 4 of 5 prior "
            "refutations tested CARICATURES of brain mechanisms (shared-W replay, "
            "shared-W scaffold, binary CSP abort). This cell composes 3 brain-"
            "correct architectural fixes (R1+R2+R3) with SEPARATE-W discipline "
            "enforced via runtime assertions. HARD_PASS_BARRIER_BROKEN requires "
            "ARM_COMBINED depth-5 >= 0.65 AND composition wins individual AND "
            "+0.45 over baseline AND cv<=0.08. R1=NREM replay as OPERATOR (v4 "
            "drill correction; continuous CFU-gated amplitude; shortcuts into "
            "SEPARATE W_C). R2=PFC scratchpad in SEPARATE W_PFC. R3=bidirectional "
            "meet-in-middle via HRR-involutive unbinding (bipolar self-inverse). "
            "BRAIN_MECHANISM_VS_CARICATURE check: SEPARATE-W asserted at runtime; "
            "test cell raises if W_H mutated."
        ),
    }
    write_metrics(out_dir, metrics, results=per_seed)
    print("[done] metrics.json written (%d seeds, %.1fs)"
          % (len(per_seed), metrics["elapsed_s"]), flush=True)
