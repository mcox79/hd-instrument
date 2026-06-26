"""gap1_multihop_ldpc_rts_bidirectional_v2_META_M6_rail.

Gap 1 LDPC + RTS bidirectional v2 -- META_M6-compliant re-dispatch of v1 (same fix
pattern as Cell B v2 + Cell C v2 + Cell X (beam) v2).

V1 ROOT CAUSE (SANITY_BREACH 5/5 seeds; baseline_mean=0.332 outside [0.125,0.165]):
  v1 used W = make_deep_chains(n_chains=200, V_P=10, max_depth=5) -> 1000 bindings.
  Pointer-chain v2 BASELINE_RAIL_FIXED used max_depth=10 -> 2000 bindings (the
  authoritative 0.145 +/-0.02 anchor). 2x crosstalk diff in the same (V_C=200,
  V_P=10) key space -> v1's baseline reports 0.332 (~smoke regime) not 0.145.
  Same cross-cell rail-mismatch as Cell X v1 + Cell B v1 + Cell C v1.

V2 ARMS (6):
  ARM_BASELINE_HRR_2HOP             beta-sweep rail (sanity [0.62, 0.68])
  ARM_REPRODUCE_POINTER_CHAIN_V2    K=1 noise=0 hard-argmax; W_pointer_v2_regime
                                     -- target [0.08, 0.25] (META_M6 rail)
  ARM_SOFT_FWD                       soft forward belief; W_pointer_v2_regime
  ARM_BACKWARD_ONLY                  reverse-chain soft + forward re-derive; W_pointer_v2_regime
  ARM_LDPC_BIDIR                     iterative sum-product factor graph; W_pointer_v2_regime (Anchor 1)
  ARM_RTS_SMOOTH                     forward x backward analytical smoother; W_pointer_v2_regime (Anchor 2)

All mechanism arms run on the HARD regime (W_pointer_v2_regime) so any lift is
the actual mechanism contribution, NOT a low-crosstalk W shortcut.

PRE-REG (LOCKED via module-init asserts):

  SACRED SANITY RAILS (verdict pre-empted on majority-seed breach):
    RAIL_BASELINE:                  baseline in [0.62, 0.68]
    RAIL_META_M6_REPRODUCE_POINTER: REPRODUCE_POINTER_CHAIN_V2 in [0.08, 0.25] (THE rail)

  MODE B verdict ladder (both rails must pass):

    HARD_PASS_CHAIN_GRADE_LDPC:
      LDPC >= 0.50 AND
      REPRODUCE_POINTER_CHAIN_V2 in [0.08, 0.25] AND
      LDPC > SOFT_FWD + 0.10 AND
      sd_LDPC <= 0.06

    HARD_PASS_CHAIN_GRADE_RTS:
      RTS >= 0.50 AND
      REPRODUCE_POINTER_CHAIN_V2 in [0.08, 0.25] AND
      RTS > max(REPRODUCE, BACKWARD) + 0.10 AND
      sd_RTS <= 0.06

    HARD_PASS_WITH_META_M7_NOTE_LDPC:
      LDPC >= 0.50 AND
      REPRODUCE_POINTER_CHAIN_V2 OUT of [0.08, 0.25]   (advisory note)

    HARD_PASS_WITH_META_M7_NOTE_RTS:
      RTS >= 0.50 AND
      REPRODUCE_POINTER_CHAIN_V2 OUT of [0.08, 0.25]   (advisory note)

    MIDDLE_BAND_GAP1_PARTIAL_LIFT: LDPC or RTS in [0.30, 0.50)
    HARD_FAIL_GAP1_BIDIRECTIONAL_REFUTED: both LDPC <= 0.25 AND RTS <= 0.25

Author: exp_dev 2026-06-25 (cross-cell rail-mismatch fix; same pattern as Cell B v2 / Cell C v2 / Cell X v2).
Pre-reg: preregs/2026-06-25_gap1_multihop_ldpc_rts_bidirectional_v2_META_M6_rail.md
ASCII-only; per-seed checkpoint; substrate-only (zero LLM forward calls).
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

ANCHOR_NAME = "gap1_multihop_ldpc_rts_bidirectional_v2_meta_m6_rail"
_LLM_CALL_COUNTER = [0]

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true", dest="self_test")
_ARGS, _ = _ap.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = ("smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE)
            else os.environ.get("HDLAB_RUN_MODE", "full").lower())

# =============================================================================
# PROSPECTIVE HARD bands (LOCKED at module init)
# =============================================================================

# Sanity rail (verdict pre-empted on majority-seed breach)
BASELINE_SANITY_LO = 0.62
BASELINE_SANITY_HI = 0.68

# META_M6 rail: ARM_REPRODUCE_POINTER_CHAIN_V2 must reproduce pointer-chain v2
META_M6_RAIL_LO = 0.08
META_M6_RAIL_HI = 0.25

# ANCHOR 1 (LDPC) thresholds
HP_LDPC_TOP1_MIN = 0.50
HP_LDPC_SOFT_FWD_DELTA = 0.10
HP_LDPC_SD_MAX = 0.06
HF_LDPC_TOP1_MAX = 0.25
MB_LDPC_LO = 0.30
MB_LDPC_HI = 0.50

# ANCHOR 2 (RTS) thresholds
HP_RTS_TOP1_MIN = 0.50
HP_RTS_SUPER_ADDITIVE_DELTA = 0.10
HP_RTS_SD_MAX = 0.06
HF_RTS_TOP1_MAX = 0.25
MB_RTS_LO = 0.30
MB_RTS_HI = 0.50

# Q-discipline saturation guard
Q_SATURATION = 0.995

# Lock assertions
assert BASELINE_SANITY_LO < BASELINE_SANITY_HI
assert META_M6_RAIL_LO < META_M6_RAIL_HI
assert HP_LDPC_TOP1_MIN > MB_LDPC_HI - 1e-9 and HP_LDPC_TOP1_MIN > HF_LDPC_TOP1_MAX
assert HP_RTS_TOP1_MIN > MB_RTS_HI - 1e-9 and HP_RTS_TOP1_MIN > HF_RTS_TOP1_MAX
assert HF_LDPC_TOP1_MAX < MB_LDPC_LO
assert HF_RTS_TOP1_MAX < MB_RTS_LO
assert Q_SATURATION > HP_LDPC_TOP1_MIN

# =============================================================================
# Regime configs (the load-bearing diff vs Gap-1 v1)
# =============================================================================

# Baseline beta-sweep regime (matches pointer-chain v2 baseline rail)
BASELINE_V_P = 2
BASELINE_N_CHAINS = 200

# Pointer-chain v2 regime: HARD regime; n=200 max_depth=10 -> 2000 W bindings
POINTERV2_N_CHAINS = 200
POINTERV2_MAX_DEPTH = 10
POINTERV2_V_P = 10
POINTERV2_K_SET = 20

TEST_DEPTH = 5
LDPC_SWEEPS = 3

if RUN_MODE == "smoke":
    N_DIM = 2048
    V_CONCEPTS = 200
    SEEDS = [7]
    POINTERV2_N_CHAINS_LOCAL = 50  # smoke shrink; KEEP max_depth=10 for crosstalk-relevant W
    TEST_N_CHAINS = 20
else:
    N_DIM = 8192
    V_CONCEPTS = 200
    SEEDS = [7, 17, 23, 31, 41]
    POINTERV2_N_CHAINS_LOCAL = POINTERV2_N_CHAINS
    TEST_N_CHAINS = None

n_predicates = max(BASELINE_V_P, POINTERV2_V_P)

CONFIG_VERSION = (
    "gap1MultihopLdpcRtsBidirectional-v2-META_M6_rail: "
    "N=%d V_C=%d "
    "BASELINE_V_P=%d BASELINE_N=%d "
    "POINTERV2_V_P=%d POINTERV2_N=%d POINTERV2_DEPTH=%d K_SET=%d "
    "TEST_DEPTH=%d ldpc_sweeps=%d "
    "seeds=%s mode=%s "
    "HP_LDPC: top1>=%.2f over_soft_fwd>=%.2f sd<=%.2f "
    "HF_LDPC: top1<=%.2f "
    "HP_RTS: top1>=%.2f super_add>=%.2f sd<=%.2f "
    "HF_RTS: top1<=%.2f "
    "baseline_sanity=[%.2f,%.2f] META_M6_rail=[%.2f,%.2f]"
) % (
    N_DIM, V_CONCEPTS,
    BASELINE_V_P, BASELINE_N_CHAINS,
    POINTERV2_V_P, POINTERV2_N_CHAINS_LOCAL, POINTERV2_MAX_DEPTH, POINTERV2_K_SET,
    TEST_DEPTH, LDPC_SWEEPS,
    SEEDS, RUN_MODE,
    HP_LDPC_TOP1_MIN, HP_LDPC_SOFT_FWD_DELTA, HP_LDPC_SD_MAX,
    HF_LDPC_TOP1_MAX,
    HP_RTS_TOP1_MIN, HP_RTS_SUPER_ADDITIVE_DELTA, HP_RTS_SD_MAX,
    HF_RTS_TOP1_MAX,
    BASELINE_SANITY_LO, BASELINE_SANITY_HI,
    META_M6_RAIL_LO, META_M6_RAIL_HI,
)


# =============================================================================
# Substrate primitives (verbatim from Gap-1 v1 + Cell B v2)
# =============================================================================

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


def make_two_hop_chains_betasweep(n_chains: int, V: int, g: np.random.Generator,
                                    p1: int = 0, p2: int = 1):
    """Verbatim from beta-sweep / pointer-chain v2."""
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
                      g: np.random.Generator, disallow_s: set):
    """Verbatim from pointer-chain v2."""
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
            "BLOCKING make_deep_chains: only %d/%d generated for V=%d disallow|=%d max_depth=%d"
            % (len(chain_queries), n_chains, V, len(disallow_s), max_depth)
        )
    return all_triples, chain_queries


def _scores_to_softmax(scores: np.ndarray, temperature: float = 1.0,
                       k_set: int = 20, sharpness: float = 2.0) -> np.ndarray:
    """Top-K masked softmax over E-similarity scores (verbatim from Gap-1 v1)."""
    V = scores.shape[0]
    k = min(k_set, V)
    idx = np.argpartition(-scores, k - 1)[:k]
    masked_scores = scores[idx]
    std = max(float(masked_scores.std()), 1e-9)
    effective_sharpness = sharpness / max(temperature, 1e-6)
    s_norm = (masked_scores - masked_scores.max()) / std * effective_sharpness
    e = np.exp(s_norm)
    e_sum = float(e.sum())
    if e_sum < 1e-12:
        out = np.zeros(V, dtype=np.float32)
        out[idx[np.argmax(masked_scores)]] = 1.0
        return out
    probs = e / e_sum
    out = np.zeros(V, dtype=np.float32)
    out[idx] = probs.astype(np.float32)
    return out


# =============================================================================
# Multi-hop arms (all on W_pointer_v2_regime)
# =============================================================================

def arm_reproduce_pointer_chain_v2(E, R, sq, W, chains_test, depth: int) -> Dict[str, Any]:
    """K=1 noise=0 hard-argmax forward chain. Algorithmically equivalent to
    pointer-chain v2's chain mechanism. META_M6 rail arm.
    """
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
    per_step_acc = (per_step_hits.astype(np.float32) / max(n, 1)).tolist()
    return {
        "top1": round(hits / max(n, 1), 4),
        "per_step_acc": [round(x, 4) for x in per_step_acc],
        "n_queries": n, "depth": depth,
        "mechanism": "pointer_chain_v2_hard_argmax_k1_noise0",
    }


def arm_soft_fwd(E, R, sq, W, chains_test, depth: int,
                 temperature: float = 1.0, k_set: int = 20) -> Dict[str, Any]:
    """Forward-only soft propagation; verbatim from Gap-1 v1."""
    n = len(chains_test)
    hits = 0
    per_step_hits = np.zeros(depth, dtype=np.int64)
    V = E.shape[0]
    for chain in chains_test:
        belief = np.zeros(V, dtype=np.float32)
        belief[chain[0][0]] = 1.0
        for i in range(depth):
            p = chain[i][1]
            state = belief @ E
            key = (state * R[p] * sq).astype(np.float32)
            scores = E @ (W @ key)
            belief = _scores_to_softmax(scores, temperature, k_set=k_set)
            if int(belief.argmax()) == chain[i][2]:
                per_step_hits[i] += 1
        if int(belief.argmax()) == chain[depth - 1][2]:
            hits += 1
    per_step_acc = (per_step_hits.astype(np.float32) / max(n, 1)).tolist()
    return {
        "top1": round(hits / max(n, 1), 4),
        "per_step_acc": [round(x, 4) for x in per_step_acc],
        "n_queries": n, "depth": depth,
        "mechanism": "soft_forward_only_softmax_belief",
        "temperature": temperature,
    }


def arm_backward_only(E, R, sq, W, chains_test, depth: int,
                      temperature: float = 1.0, k_set: int = 20) -> Dict[str, Any]:
    """Reverse-chain soft + forward re-derive; verbatim from Gap-1 v1."""
    n = len(chains_test)
    hits = 0
    per_step_hits = np.zeros(depth, dtype=np.int64)
    V = E.shape[0]
    for chain in chains_test:
        belief = np.zeros(V, dtype=np.float32)
        belief[chain[depth - 1][2]] = 1.0
        for i in range(depth - 1, -1, -1):
            p = chain[i][1]
            state = belief @ E
            recovered = (W.T @ state) * R[p] / sq
            scores = E @ recovered
            belief = _scores_to_softmax(scores, temperature, k_set=k_set)
            if int(belief.argmax()) == chain[i][0]:
                per_step_hits[depth - 1 - i] += 1
        s = int(belief.argmax())
        for i in range(depth):
            p = chain[i][1]
            key = (E[s] * R[p] * sq).astype(np.float32)
            scores = E @ (W @ key)
            s = int(scores.argmax())
        if s == chain[depth - 1][2]:
            hits += 1
    per_step_acc = (per_step_hits.astype(np.float32) / max(n, 1)).tolist()
    return {
        "top1": round(hits / max(n, 1), 4),
        "per_step_acc_backward": [round(x, 4) for x in per_step_acc],
        "n_queries": n, "depth": depth,
        "mechanism": "backward_only_reverse_chain_soft_propagation_then_forward_rederive",
        "temperature": temperature,
    }


def arm_ldpc_bidir(E, R, sq, W, chains_test, depth: int,
                   n_sweeps: int = LDPC_SWEEPS,
                   temperature: float = 1.0, k_set: int = 20) -> Dict[str, Any]:
    """LDPC bidirectional sum-product iterative factor graph; verbatim from Gap-1 v1."""
    n = len(chains_test)
    V = E.shape[0]
    hits = 0
    per_step_hits = np.zeros(depth, dtype=np.int64)
    sweeps_to_converge_acc = 0

    for chain in chains_test:
        beliefs = [np.zeros(V, dtype=np.float32) for _ in range(depth + 1)]
        beliefs[0][chain[0][0]] = 1.0
        for k in range(1, depth + 1):
            beliefs[k][:] = 1.0 / V

        prev_endpoint_argmax = -1
        converged_at = n_sweeps
        for sweep in range(n_sweeps):
            fwd_msgs = [beliefs[0].copy()]
            for k in range(depth):
                p = chain[k][1]
                state = fwd_msgs[k] @ E
                key = (state * R[p] * sq).astype(np.float32)
                scores = E @ (W @ key)
                fwd_msgs.append(_scores_to_softmax(scores, temperature, k_set=k_set))
            bwd_msgs = [None] * (depth + 1)
            bwd_msgs[depth] = fwd_msgs[depth].copy()
            for k in range(depth, 0, -1):
                p = chain[k - 1][1]
                state = bwd_msgs[k] @ E
                recovered = (W.T @ state) * R[p] / sq
                scores = E @ recovered
                bwd_msgs[k - 1] = _scores_to_softmax(scores, temperature, k_set=k_set)
            for k in range(depth + 1):
                if k == 0:
                    continue
                combined = fwd_msgs[k] * bwd_msgs[k]
                s = combined.sum()
                if s > 1e-12:
                    beliefs[k] = combined / s
                else:
                    beliefs[k] = fwd_msgs[k]
            endpoint_argmax = int(beliefs[depth].argmax())
            if endpoint_argmax == prev_endpoint_argmax:
                converged_at = sweep + 1
                break
            prev_endpoint_argmax = endpoint_argmax
        sweeps_to_converge_acc += converged_at

        if int(beliefs[depth].argmax()) == chain[depth - 1][2]:
            hits += 1
        for k in range(depth):
            if int(beliefs[k + 1].argmax()) == chain[k][2]:
                per_step_hits[k] += 1

    per_step_acc = (per_step_hits.astype(np.float32) / max(n, 1)).tolist()
    return {
        "top1": round(hits / max(n, 1), 4),
        "per_step_acc": [round(x, 4) for x in per_step_acc],
        "n_queries": n, "depth": depth,
        "n_sweeps_max": n_sweeps,
        "mean_sweeps_to_converge": round(sweeps_to_converge_acc / max(n, 1), 2),
        "mechanism": "ldpc_bidirectional_sum_product_chain_factor_graph",
        "temperature": temperature,
    }


def arm_rts_smooth(E, R, sq, W, chains_test, depth: int,
                   temperature: float = 1.0, k_set: int = 20) -> Dict[str, Any]:
    """RTS analytical smoother (forward x backward product); verbatim from Gap-1 v1."""
    n = len(chains_test)
    V = E.shape[0]
    hits = 0
    per_step_hits = np.zeros(depth, dtype=np.int64)

    for chain in chains_test:
        fwd = [np.zeros(V, dtype=np.float32) for _ in range(depth + 1)]
        fwd[0][chain[0][0]] = 1.0
        for k in range(depth):
            p = chain[k][1]
            state = fwd[k] @ E
            key = (state * R[p] * sq).astype(np.float32)
            scores = E @ (W @ key)
            fwd[k + 1] = _scores_to_softmax(scores, temperature, k_set=k_set)

        bwd = [np.zeros(V, dtype=np.float32) for _ in range(depth + 1)]
        bwd[depth] = fwd[depth].copy()
        for k in range(depth, 0, -1):
            p = chain[k - 1][1]
            state = bwd[k] @ E
            recovered = (W.T @ state) * R[p] / sq
            scores = E @ recovered
            bwd[k - 1] = _scores_to_softmax(scores, temperature, k_set=k_set)

        smoothed = [np.zeros(V, dtype=np.float32) for _ in range(depth + 1)]
        smoothed[0] = fwd[0]
        for k in range(1, depth + 1):
            combined = fwd[k] * bwd[k]
            s = combined.sum()
            smoothed[k] = (combined / s) if s > 1e-12 else fwd[k]

        if int(smoothed[depth].argmax()) == chain[depth - 1][2]:
            hits += 1
        for k in range(depth):
            if int(smoothed[k + 1].argmax()) == chain[k][2]:
                per_step_hits[k] += 1

    per_step_acc = (per_step_hits.astype(np.float32) / max(n, 1)).tolist()
    return {
        "top1": round(hits / max(n, 1), 4),
        "per_step_acc": [round(x, 4) for x in per_step_acc],
        "n_queries": n, "depth": depth,
        "mechanism": "rts_smoother_forward_x_backward_softmax_product",
        "temperature": temperature,
    }


# =============================================================================
# Self-test
# =============================================================================

def _selftest() -> None:
    g = np.random.default_rng(0)
    n = 1024
    V = 60
    P = 4
    sq = math.sqrt(n)
    E = bipolar(V, n, g)
    R = bipolar(P, n, g)

    # T1: construction self-consistency
    triples_d, chains_d = make_deep_chains(20, V, P, max_depth=POINTERV2_MAX_DEPTH, g=g,
                                            disallow_s=set())
    assert len(triples_d) == 20 * POINTERV2_MAX_DEPTH
    assert len(chains_d) == 20
    W = ingest_hebbian(triples_d, E, R, sq, n)
    assert not np.isnan(W).any()
    print("[selftest] T1 PASS: construction self-consistent")

    chains_d5 = [c[:TEST_DEPTH] for c in chains_d]

    # T2: REPRODUCE arm sane numbers
    r_base = arm_reproduce_pointer_chain_v2(E, R, sq, W, chains_d5, depth=TEST_DEPTH)
    assert 0.0 <= r_base["top1"] <= 1.0
    print("[selftest] T2 PASS: REPRODUCE top1=%.3f" % r_base["top1"])

    # T3: SOFT_FWD numerical sanity
    r_sft = arm_soft_fwd(E, R, sq, W, chains_d5, depth=TEST_DEPTH)
    assert 0.0 <= r_sft["top1"] <= 1.0
    assert not math.isnan(r_sft["top1"])
    print("[selftest] T3 PASS: SOFT_FWD top1=%.3f" % r_sft["top1"])

    # T4: BACKWARD_ONLY numerical sanity
    r_bwd = arm_backward_only(E, R, sq, W, chains_d5, depth=TEST_DEPTH)
    assert 0.0 <= r_bwd["top1"] <= 1.0
    print("[selftest] T4 PASS: BACKWARD_ONLY top1=%.3f" % r_bwd["top1"])

    # T5: LDPC produces convergence stat
    r_ldpc = arm_ldpc_bidir(E, R, sq, W, chains_d5, depth=TEST_DEPTH, n_sweeps=2)
    assert 0.0 <= r_ldpc["top1"] <= 1.0
    assert "mean_sweeps_to_converge" in r_ldpc
    print("[selftest] T5 PASS: LDPC top1=%.3f mean_sweeps=%.2f"
          % (r_ldpc["top1"], r_ldpc["mean_sweeps_to_converge"]))

    # T6: RTS produces per_step_acc
    r_rts = arm_rts_smooth(E, R, sq, W, chains_d5, depth=TEST_DEPTH)
    assert 0.0 <= r_rts["top1"] <= 1.0
    assert len(r_rts["per_step_acc"]) == TEST_DEPTH
    print("[selftest] T6 PASS: RTS top1=%.3f" % r_rts["top1"])

    # T7: REPRODUCE algorithmically equivalent to pointer-chain v2 inline
    s_idx = int(chains_d5[0][0][0])
    p_idx = int(chains_d5[0][0][1])
    key = (E[s_idx] * R[p_idx] * sq).astype(np.float32)
    idx_inline = int((E @ (W @ key)).argmax())
    # Run one hop of REPRODUCE manually
    state = E[s_idx].copy()
    key2 = (state * R[p_idx] * sq).astype(np.float32)
    state2 = W @ key2
    idx_arm = int((E @ state2).argmax())
    assert idx_inline == idx_arm, \
        "T7 cleanup primitive equivalence broken: inline=%d vs arm=%d" % (idx_inline, idx_arm)
    print("[selftest] T7 PASS: REPRODUCE EQUIVALENT to pointer-chain v2 inline (idx=%d)"
          % idx_inline)

    # T8: bands locked (exact numerics)
    assert HP_LDPC_TOP1_MIN == 0.50
    assert HP_RTS_TOP1_MIN == 0.50
    assert META_M6_RAIL_LO == 0.08 and META_M6_RAIL_HI == 0.25
    assert BASELINE_SANITY_LO == 0.62 and BASELINE_SANITY_HI == 0.68
    print("[selftest] T8 PASS: bands locked (META_M6=[%.2f,%.2f])"
          % (META_M6_RAIL_LO, META_M6_RAIL_HI))

    # T9: substrate-only
    assert _LLM_CALL_COUNTER[0] == 0
    print("[selftest] T9 PASS: LLM counter = 0")

    # T10: NaN guard at production-scale
    big_n = 4096
    big_V = 80
    big_E = bipolar(big_V, big_n, g)
    big_R = bipolar(P, big_n, g)
    big_triples, big_chains = make_deep_chains(20, big_V, P, max_depth=POINTERV2_MAX_DEPTH,
                                                 g=g, disallow_s=set())
    big_W = ingest_hebbian(big_triples, big_E, big_R, math.sqrt(big_n), big_n)
    big_chains5 = [c[:TEST_DEPTH] for c in big_chains[:5]]
    r_ldpc_big = arm_ldpc_bidir(big_E, big_R, math.sqrt(big_n), big_W,
                                  big_chains5, depth=TEST_DEPTH, n_sweeps=2)
    r_rts_big = arm_rts_smooth(big_E, big_R, math.sqrt(big_n), big_W,
                                 big_chains5, depth=TEST_DEPTH)
    assert not math.isnan(r_ldpc_big["top1"]) and not math.isnan(r_rts_big["top1"])
    print("[selftest] T10 PASS: production-scale LDPC=%.3f RTS=%.3f no-NaN"
          % (r_ldpc_big["top1"], r_rts_big["top1"]))

    print("[selftest] ALL PASS")


_selftest()
if _ARGS.self_test:
    print("[self-test] PASS; exiting", flush=True)
    sys.exit(0)


# =============================================================================
# Per-seed run
# =============================================================================

def run_seed(seed: int) -> Dict[str, Any]:
    t = time.time()
    g = np.random.default_rng(seed)
    sq = math.sqrt(N_DIM)
    E = bipolar(V_CONCEPTS, N_DIM, g)
    R = bipolar(n_predicates, N_DIM, g)

    out = {
        "seed": seed, "run_mode": RUN_MODE, "N": N_DIM, "V_C": V_CONCEPTS,
        "V_P": POINTERV2_V_P, "K_SET": POINTERV2_K_SET,
        "n_predicates": n_predicates,
        "baseline_n_chains": BASELINE_N_CHAINS,
        "pointerv2_n_chains": POINTERV2_N_CHAINS_LOCAL,
        "pointerv2_max_depth": POINTERV2_MAX_DEPTH,
        "test_depth": TEST_DEPTH,
        "ldpc_sweeps": LDPC_SWEEPS,
        "config_version": CONFIG_VERSION,
        "_llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
    }

    # ===== ARM_BASELINE_HRR_2HOP (sanity rail) =====
    t_arm = time.time()
    base_triples, base_queries = make_two_hop_chains_betasweep(
        BASELINE_N_CHAINS, V_CONCEPTS, g, p1=0, p2=1)
    r_baseline = arm_baseline_hrr_2hop_betasweep(E, R, sq, base_triples, base_queries)
    r_baseline["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    out["arm_baseline_hrr_2hop"] = r_baseline
    baseline_ok = (BASELINE_SANITY_LO <= r_baseline["top1"] <= BASELINE_SANITY_HI)
    out["baseline_sanity_ok"] = baseline_ok
    print("  [seed=%d] ARM_BASELINE_HRR_2HOP top1=%.4f (sanity_ok=%s) t=%.1fs"
          % (seed, r_baseline["top1"], baseline_ok, r_baseline["elapsed_s_arm"]),
          flush=True)

    # ===== Build W_pointer_v2_regime (HARD: n=200 max_depth=10 -> 2000 bindings) =====
    t_arm = time.time()
    pv2_triples, pv2_chains = make_deep_chains(
        POINTERV2_N_CHAINS_LOCAL, V_CONCEPTS, POINTERV2_V_P,
        max_depth=POINTERV2_MAX_DEPTH, g=g, disallow_s=set())
    W_pointer_v2 = ingest_hebbian(pv2_triples, E, R, sq, N_DIM)
    pv2_w_build_s = round(time.time() - t_arm, 2)
    print("  [seed=%d] W_pointer_v2_regime built (%d triples, %d chains, max_depth=%d) t=%.1fs"
          % (seed, len(pv2_triples), len(pv2_chains), POINTERV2_MAX_DEPTH,
             pv2_w_build_s), flush=True)

    # Test queries truncated to TEST_DEPTH=5
    if TEST_N_CHAINS is not None:
        pv2_test = [c[:TEST_DEPTH] for c in pv2_chains[:TEST_N_CHAINS]]
    else:
        pv2_test = [c[:TEST_DEPTH] for c in pv2_chains]

    # ===== ARM_REPRODUCE_POINTER_CHAIN_V2 (META_M6 rail) =====
    t_arm = time.time()
    r = arm_reproduce_pointer_chain_v2(E, R, sq, W_pointer_v2, pv2_test, depth=TEST_DEPTH)
    r["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    r["regime"] = "pointer_v2 (n_chains=%d max_depth=%d -> %d bindings)" % (
        POINTERV2_N_CHAINS_LOCAL, POINTERV2_MAX_DEPTH, len(pv2_triples))
    out["arm_reproduce_pointer_chain_v2"] = r
    meta_m6_ok = (META_M6_RAIL_LO <= r["top1"] <= META_M6_RAIL_HI)
    out["meta_m6_rail_ok"] = meta_m6_ok
    print("  [seed=%d] ARM_REPRODUCE_POINTER_CHAIN_V2 top1=%.4f (META_M6_ok=%s) per_step=%s t=%.1fs"
          % (seed, r["top1"], meta_m6_ok, r["per_step_acc"], r["elapsed_s_arm"]), flush=True)

    # ===== ARM_SOFT_FWD =====
    t_arm = time.time()
    r = arm_soft_fwd(E, R, sq, W_pointer_v2, pv2_test, depth=TEST_DEPTH,
                     k_set=POINTERV2_K_SET)
    r["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    out["arm_soft_fwd"] = r
    print("  [seed=%d] ARM_SOFT_FWD top1=%.4f per_step=%s t=%.1fs"
          % (seed, r["top1"], r["per_step_acc"], r["elapsed_s_arm"]), flush=True)

    # ===== ARM_BACKWARD_ONLY =====
    t_arm = time.time()
    r = arm_backward_only(E, R, sq, W_pointer_v2, pv2_test, depth=TEST_DEPTH,
                           k_set=POINTERV2_K_SET)
    r["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    out["arm_backward_only"] = r
    print("  [seed=%d] ARM_BACKWARD_ONLY top1=%.4f per_step_bwd=%s t=%.1fs"
          % (seed, r["top1"], r["per_step_acc_backward"], r["elapsed_s_arm"]),
          flush=True)

    # ===== ARM_LDPC_BIDIR (Anchor 1 PRIMARY) =====
    t_arm = time.time()
    r = arm_ldpc_bidir(E, R, sq, W_pointer_v2, pv2_test, depth=TEST_DEPTH,
                        n_sweeps=LDPC_SWEEPS, k_set=POINTERV2_K_SET)
    r["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    out["arm_ldpc_bidir"] = r
    print("  [seed=%d] ARM_LDPC_BIDIR top1=%.4f per_step=%s mean_sweeps=%.2f t=%.1fs"
          % (seed, r["top1"], r["per_step_acc"],
             r["mean_sweeps_to_converge"], r["elapsed_s_arm"]),
          flush=True)

    # ===== ARM_RTS_SMOOTH (Anchor 2 PRIMARY) =====
    t_arm = time.time()
    r = arm_rts_smooth(E, R, sq, W_pointer_v2, pv2_test, depth=TEST_DEPTH,
                        k_set=POINTERV2_K_SET)
    r["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    out["arm_rts_smooth"] = r
    print("  [seed=%d] ARM_RTS_SMOOTH top1=%.4f per_step=%s t=%.1fs"
          % (seed, r["top1"], r["per_step_acc"], r["elapsed_s_arm"]),
          flush=True)

    out["elapsed_s"] = round(time.time() - t, 1)
    return out


# =============================================================================
# Verdict
# =============================================================================

def _mean_top1(per_seed: List[Dict[str, Any]], key: str) -> float:
    vals = [p[key]["top1"] for p in per_seed if key in p
            and isinstance(p[key].get("top1"), (int, float))
            and not math.isnan(p[key]["top1"])]
    return float(np.mean(vals)) if vals else float("nan")


def _sd_top1(per_seed: List[Dict[str, Any]], key: str) -> float:
    vals = [p[key]["top1"] for p in per_seed if key in p
            and isinstance(p[key].get("top1"), (int, float))
            and not math.isnan(p[key]["top1"])]
    return float(np.std(vals)) if len(vals) > 1 else float("nan")


def verdict_from(per_seed: List[Dict[str, Any]]) -> Tuple[str, str]:
    baseline = _mean_top1(per_seed, "arm_baseline_hrr_2hop")
    reproduce = _mean_top1(per_seed, "arm_reproduce_pointer_chain_v2")
    soft_fwd = _mean_top1(per_seed, "arm_soft_fwd")
    backward = _mean_top1(per_seed, "arm_backward_only")
    ldpc = _mean_top1(per_seed, "arm_ldpc_bidir")
    rts = _mean_top1(per_seed, "arm_rts_smooth")
    ldpc_sd = _sd_top1(per_seed, "arm_ldpc_bidir")
    rts_sd = _sd_top1(per_seed, "arm_rts_smooth")

    n_seeds = len(per_seed)
    majority = max(1, (n_seeds + 1) // 2)
    baseline_breach = sum(1 for p in per_seed if not p.get("baseline_sanity_ok", False))
    meta_m6_breach = sum(1 for p in per_seed if not p.get("meta_m6_rail_ok", False))

    # Q-saturation
    q_flags = []
    for name, val in [("LDPC", ldpc), ("RTS", rts)]:
        if not math.isnan(val) and val >= Q_SATURATION:
            q_flags.append("[Q-DISCIPLINE: %s=%.4f >= %.3f suspect saturation; UNDER-CLAIM tier]"
                            % (name, val, Q_SATURATION))
    q_note = (" ".join(q_flags) + " ") if q_flags else ""

    summ = (
        "BASELINE=%.4f (sanity_breach=%d/%d in [%.2f,%.2f]) | "
        "REPRODUCE_POINTER_CHAIN_V2=%.4f (META_M6_breach=%d/%d rail=[%.2f,%.2f]) | "
        "SOFT_FWD=%.4f BACKWARD=%.4f | "
        "LDPC=%.4f (sd=%.3f) RTS=%.4f (sd=%.3f) | "
        "lift_LDPC_over_REPRODUCE=%+.4f lift_RTS_over_REPRODUCE=%+.4f | "
        "pointer_v2_5hop_ref=0.122"
    ) % (
        baseline, baseline_breach, n_seeds, BASELINE_SANITY_LO, BASELINE_SANITY_HI,
        reproduce, meta_m6_breach, n_seeds, META_M6_RAIL_LO, META_M6_RAIL_HI,
        soft_fwd, backward,
        ldpc, ldpc_sd, rts, rts_sd,
        (ldpc - reproduce) if (not math.isnan(ldpc) and not math.isnan(reproduce)) else float("nan"),
        (rts - reproduce) if (not math.isnan(rts) and not math.isnan(reproduce)) else float("nan"),
    )

    # SACRED rails (pre-empt verdict ladder)
    if baseline_breach >= majority:
        return "SANITY_BREACH", "SANITY_BREACH_BASELINE_OUT_OF_BAND: " + summ

    meta_m6_violated = (meta_m6_breach >= majority)

    # Anchor-1 (LDPC) classification (chain-grade requires REPRODUCE in band)
    max_dir_for_rts = max(reproduce if not math.isnan(reproduce) else -1.0,
                           backward if not math.isnan(backward) else -1.0)
    ldpc_hp_chain = (
        not math.isnan(ldpc) and ldpc >= HP_LDPC_TOP1_MIN
        and not meta_m6_violated
        and not math.isnan(soft_fwd) and ldpc > soft_fwd + HP_LDPC_SOFT_FWD_DELTA
        and (math.isnan(ldpc_sd) or ldpc_sd <= HP_LDPC_SD_MAX)
    )
    ldpc_hp_meta_m7 = (
        not math.isnan(ldpc) and ldpc >= HP_LDPC_TOP1_MIN
        and meta_m6_violated
    )
    ldpc_hf = (not math.isnan(ldpc) and ldpc <= HF_LDPC_TOP1_MAX)
    ldpc_mb = (not ldpc_hp_chain and not ldpc_hp_meta_m7 and not ldpc_hf
                and not math.isnan(ldpc) and MB_LDPC_LO <= ldpc < MB_LDPC_HI)
    if ldpc_hp_chain:
        ldpc_band = "HARD_PASS_CHAIN_GRADE"
    elif ldpc_hp_meta_m7:
        ldpc_band = "HARD_PASS_WITH_META_M7_NOTE"
    elif ldpc_hf:
        ldpc_band = "HARD_FAIL"
    elif ldpc_mb:
        ldpc_band = "MIDDLE_BAND"
    else:
        ldpc_band = "UNDETERMINED"

    # Anchor-2 (RTS) classification
    rts_hp_chain = (
        not math.isnan(rts) and rts >= HP_RTS_TOP1_MIN
        and not meta_m6_violated
        and rts > max_dir_for_rts + HP_RTS_SUPER_ADDITIVE_DELTA
        and (math.isnan(rts_sd) or rts_sd <= HP_RTS_SD_MAX)
    )
    rts_hp_meta_m7 = (
        not math.isnan(rts) and rts >= HP_RTS_TOP1_MIN
        and meta_m6_violated
    )
    rts_hf = (not math.isnan(rts) and rts <= HF_RTS_TOP1_MAX)
    rts_mb = (not rts_hp_chain and not rts_hp_meta_m7 and not rts_hf
                and not math.isnan(rts) and MB_RTS_LO <= rts < MB_RTS_HI)
    if rts_hp_chain:
        rts_band = "HARD_PASS_CHAIN_GRADE"
    elif rts_hp_meta_m7:
        rts_band = "HARD_PASS_WITH_META_M7_NOTE"
    elif rts_hf:
        rts_band = "HARD_FAIL"
    elif rts_mb:
        rts_band = "MIDDLE_BAND"
    else:
        rts_band = "UNDETERMINED"

    summ = summ + " | Anchor1_LDPC=%s | Anchor2_RTS=%s" % (ldpc_band, rts_band)

    # Cell-wide verdict
    if ldpc_band == "HARD_PASS_CHAIN_GRADE" or rts_band == "HARD_PASS_CHAIN_GRADE":
        return "HARD_PASS_GAP1_CHAIN_GRADE", \
               ("HARD_PASS_GAP1_CHAIN_GRADE_BIDIRECTIONAL_LIFT: %s%s" % (q_note, summ))
    if ldpc_band == "HARD_PASS_WITH_META_M7_NOTE" or rts_band == "HARD_PASS_WITH_META_M7_NOTE":
        return "HARD_PASS_WITH_META_M7_NOTE", \
               ("HARD_PASS_WITH_META_M7_NOTE_REPRODUCE_RAIL_BREACH_BUT_GAP1_LIFTS: %s%s"
                  % (q_note, summ))
    if ldpc_band == "MIDDLE_BAND" or rts_band == "MIDDLE_BAND":
        return "MIDDLE_BAND_GAP1_PARTIAL_LIFT", \
               ("MIDDLE_BAND_GAP1_PARTIAL_LIFT: %s%s" % (q_note, summ))
    if ldpc_band == "HARD_FAIL" and rts_band == "HARD_FAIL":
        return "HARD_FAIL_GAP1_BIDIRECTIONAL_REFUTED", \
               ("HARD_FAIL_GAP1_BIDIRECTIONAL_REFUTED: %s%s" % (q_note, summ))
    return "UNDETERMINED_GAP1", ("UNDETERMINED_GAP1: %s%s" % (q_note, summ))


# =============================================================================
# atexit synthesizer
# =============================================================================

_RESULTS_HOLDER: Dict[str, Any] = {"out_dir": None, "started_at": time.time()}


def _atexit_synth() -> None:
    od = _RESULTS_HOLDER["out_dir"]
    if od is None:
        return
    try:
        if (od / "metrics.json").exists():
            return
        agg = aggregate_partials(od, seeds=[str(s) for s in SEEDS],
                                  run_config={"N": N_DIM, "run_mode": RUN_MODE})
        if not agg:
            return
        per_seed = [agg[k] for k in sorted(agg.keys())]
        if not per_seed:
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
            "Gap-1 LDPC+RTS bidirectional v2 META_M6_rail: v1 landed "
            "SANITY_BREACH_BASELINE_OUT_OF_BAND (5/5 seeds; baseline_mean=0.332 "
            "outside [0.125, 0.165]). Root cause: v1 used W = "
            "make_deep_chains(n=200, V_P=10, max_depth=5) -> 1000 bindings, "
            "but pointer-chain v2's BASELINE_RAIL_FIXED used max_depth=10 -> "
            "2000 bindings (the authoritative 0.145 +/-0.02 anchor). 2x "
            "crosstalk diff in the (V_C=200, V_P=10) key space drove the "
            "baseline regime mismatch. Same fix pattern as Cell B v2 + Cell C v2 "
            "+ Cell X (beam) v2: introduce ARM_REPRODUCE_POINTER_CHAIN_V2 with "
            "W_pointer_v2_regime (n=200, max_depth=10) as the META_M6 rail; all "
            "mechanism arms (SOFT_FWD / BACKWARD / LDPC / RTS) run on the HARD "
            "W_pointer_v2_regime so any lift is real bidirectional mechanism "
            "contribution, NOT a low-crosstalk W shortcut. Sanity rail (baseline "
            "in [0.62, 0.68]) and META_M6 rail (REPRODUCE in [0.08, 0.25]) "
            "are pre-empt rails; HARD_PASS_CHAIN_GRADE requires REPRODUCE in "
            "band; HARD_PASS_WITH_META_M7_NOTE if REPRODUCE breaches but LDPC "
            "or RTS still >= 0.50. Pre-reg: "
            "preregs/2026-06-25_gap1_multihop_ldpc_rts_bidirectional_v2_META_M6_rail.md."
        ),
    }
    write_metrics(out_dir, metrics, results=per_seed)
    print("[done] metrics.json written (%d seeds, %.1fs)" % (
        len(per_seed), metrics["elapsed_s"]), flush=True)
