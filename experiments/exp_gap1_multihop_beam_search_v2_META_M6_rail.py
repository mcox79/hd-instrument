"""gap1_multihop_beam_search_v2_META_M6_rail.

Cell X (beam search) v2 -- META_M6-compliant re-dispatch of Cell X v1 ("beam_search_with_WM_candidates").

STAGE-1 SANITY FINDING (Mode B, identical pattern to Cell B v2 / Cell C v2):
  Cell X v1 used the SAME forward-cleanup primitive as pointer-chain v2 at K=1.
  The 0.33 SINGLE_TOP1_5HOP in v1 vs pointer-v2's 0.122 (mean across seeds) is a
  REGIME ARTIFACT, not a mechanism gain:
    v1 ran with W = make_deep_chains(n_chains=200, V_P=10, max_depth=5) -> 1000 bindings
    pointer-chain v2 ran with W = make_deep_chains(n=200, V_P=10, max_depth=10) -> 2000 bindings
  2x crosstalk diff in the same (V_C=200, V_P=10) key space exactly matches the
  documented pointer-chain v1 -> v2 BUG PATTERN that drove Cell B v2 + Cell C v2.

V2 ARMS (6 by default; informational SINGLE arm preserved for reader sanity):
  ARM_BASELINE_HRR_2HOP             beta-sweep rail (sanity [0.62, 0.68])
  ARM_REPRODUCE_POINTER_CHAIN_V2    K=1 noise=0 mechanism; W_pointer_v2_regime (n=200, max_depth=10)
                                     -- target [0.08, 0.25] (META_M6 rail)
  ARM_SINGLE_TOP1_5HOP_V1_REGIME    K=1 noise=0 mechanism; W_v1_regime (n=200, max_depth=5; v1 setup)
                                     -- target [0.25, 0.45] (replicates v1's 0.33; informational)
  ARM_BEAM_W2_TOPK3_5HOP            beam_width=2 top_k=3; W_pointer_v2_regime
  ARM_BEAM_W5_TOPK3_5HOP            beam_width=5 top_k=3; W_pointer_v2_regime
  ARM_BEAM_W10_TOPK5_5HOP           beam_width=10 top_k=5; W_pointer_v2_regime (PRIMARY)

The BEAM arms all use the HARD regime (W_pointer_v2_regime) so any lift is the
actual mechanism contribution, NOT a low-crosstalk W shortcut.

PRE-REG (LOCKED via module-init asserts):

  SACRED SANITY RAILS (verdict pre-empted on majority-seed breach):
    RAIL_BASELINE:                  baseline in [0.62, 0.68]
    RAIL_META_M6_REPRODUCE_POINTER: REPRODUCE_POINTER_CHAIN_V2 in [0.08, 0.25] (THE rail)
    RAIL_V1_DOCUMENTED (advisory):  SINGLE_TOP1_5HOP_V1_REGIME in [0.20, 0.50] (informational; not pre-emptive)

  MODE B verdict ladder (RAIL_BASELINE + RAIL_META_M6 must pass):

    HARD_PASS_CHAIN_GRADE_BARRIER_1_BEAM:
      BEAM_W10 >= 0.50 AND
      REPRODUCE_POINTER_CHAIN_V2 in [0.08, 0.25] AND
      monotonic_W2_W5_W10 (W2 <= W5 <= W10 within MONOTONIC_TOL) AND
      cv_W10 <= 0.07

    HARD_PASS_WITH_META_M7_NOTE:
      BEAM_W10 >= 0.50 AND
      REPRODUCE_POINTER_CHAIN_V2 OUT of [0.08, 0.25]   (rail breach; advisory note)

    HARD_PASS_PARTIAL_BEAM_LIFT:
      BEAM_W10 >= 0.30 AND not chain-grade

    MIDDLE_BAND_BEAM_MARGINAL:
      BEAM_W10 in [0.20, 0.30)

    HARD_FAIL_BEAM_DOESNT_HELP:
      BEAM_W10 < 0.20

Author: exp_dev 2026-06-25 (cross-cell rail-mismatch fix; same pattern as Cell B v2 / Cell C v2).
Pre-reg: preregs/2026-06-25_gap1_multihop_beam_search_v2_META_M6_rail.md
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

ANCHOR_NAME = "gap1_multihop_beam_search_v2_meta_m6_rail"
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

# META_M6 rail: ARM_REPRODUCE_POINTER_CHAIN_V2 must reproduce pointer-chain v2.
# Pointer-chain v2 mean 0.122 across seeds; +/-~0.13 absorption upper / +/-~0.04 lower.
META_M6_RAIL_LO = 0.08
META_M6_RAIL_HI = 0.25

# V1-documented rail (informational; advisory only; not pre-emptive).
# v1 BEAM cell ran with n_chains=200 max_depth=5 -> 1000 bindings.
# Mean SINGLE_TOP1_5HOP across 3 seeds was 0.33 (seed7=0.275, seed17=0.33, seed23=0.385).
V1_DOC_RAIL_LO = 0.20
V1_DOC_RAIL_HI = 0.50

# Mode B verdict thresholds for BEAM_W10 (primary)
HP_BEAM_W10_5HOP_MIN = 0.50
HP_BEAM_CV_MAX = 0.07
HP_PARTIAL_5HOP_MIN = 0.30
MID_BEAM_W10_LO = 0.20
MID_BEAM_W10_HI = 0.30
HF_BEAM_W10_MAX = 0.20  # strictly less than
MONOTONIC_TOL = 0.02

# Q-discipline saturation guard
Q_SATURATION = 0.995

# Lock assertions (catch accidental edits to bands)
assert HP_BEAM_W10_5HOP_MIN > HP_PARTIAL_5HOP_MIN
assert HP_PARTIAL_5HOP_MIN == MID_BEAM_W10_HI  # MID band upper = HP_PARTIAL floor
assert MID_BEAM_W10_HI > MID_BEAM_W10_LO
assert MID_BEAM_W10_LO == HF_BEAM_W10_MAX  # HF strict-less-than HF_MAX; MID covers [MID_LO, MID_HI)
assert BASELINE_SANITY_LO < BASELINE_SANITY_HI
assert META_M6_RAIL_LO < META_M6_RAIL_HI
assert V1_DOC_RAIL_LO < V1_DOC_RAIL_HI
assert 0.0 < HP_BEAM_CV_MAX < 0.20
assert MONOTONIC_TOL > 0.0
assert Q_SATURATION > HP_BEAM_W10_5HOP_MIN

# =============================================================================
# Regime configs (the load-bearing diff vs Cell X v1)
# =============================================================================

# Baseline beta-sweep regime (matches pointer-chain v2 baseline rail)
BASELINE_V_P = 2
BASELINE_N_CHAINS = 200

# Pointer-chain v2 regime: HARD regime; n=200 max_depth=10 -> 2000 W bindings
POINTERV2_N_CHAINS = 200
POINTERV2_MAX_DEPTH = 10
POINTERV2_V_P = 10
POINTERV2_K_SET = 20

# Cell X v1 regime: EASIER regime; n=200 max_depth=5 -> 1000 W bindings
V1_N_CHAINS = 200
V1_MAX_DEPTH = 5
V1_V_P = 10

# Test depth (apples-to-apples comparison point)
TEST_DEPTH = 5

# Beam configs (locked, monotonic in beam_width)
BEAM_CONFIGS = [
    ("ARM_BEAM_W2_TOPK3_5HOP", 2, 3),
    ("ARM_BEAM_W5_TOPK3_5HOP", 5, 3),
    ("ARM_BEAM_W10_TOPK5_5HOP", 10, 5),
]

if RUN_MODE == "smoke":
    N_DIM = 2048
    V_CONCEPTS = 200
    SEEDS = [7]
    # Smoke: shrink chain counts but KEEP max_depth=10 for pointer-v2 regime so
    # W still has crosstalk-relevant size
    POINTERV2_N_CHAINS_LOCAL = 50
    V1_N_CHAINS_LOCAL = 40
    TEST_N_CHAINS = 20  # subsample for arm test queries
else:
    N_DIM = 8192
    V_CONCEPTS = 200
    SEEDS = [7, 17, 23]
    POINTERV2_N_CHAINS_LOCAL = POINTERV2_N_CHAINS
    V1_N_CHAINS_LOCAL = V1_N_CHAINS
    TEST_N_CHAINS = None  # use all chains

n_predicates = max(BASELINE_V_P, POINTERV2_V_P, V1_V_P)

CONFIG_VERSION = (
    "gap1MultihopBeamSearch-v2-META_M6_rail: "
    "N=%d V_C=%d "
    "BASELINE_V_P=%d BASELINE_N=%d "
    "POINTERV2_V_P=%d POINTERV2_N=%d POINTERV2_DEPTH=%d K_SET=%d "
    "V1_V_P=%d V1_N=%d V1_DEPTH=%d "
    "TEST_DEPTH=%d beam_configs=%s "
    "seeds=%s mode=%s "
    "HP_W10>=%.2f HP_partial>=%.2f mid_W10=[%.2f,%.2f) HF_W10<%.2f "
    "HP_cv<=%.2f monotonic_tol=%.3f "
    "baseline_sanity=[%.2f,%.2f] META_M6_rail=[%.2f,%.2f] V1_DOC_rail=[%.2f,%.2f]"
) % (
    N_DIM, V_CONCEPTS,
    BASELINE_V_P, BASELINE_N_CHAINS,
    POINTERV2_V_P, POINTERV2_N_CHAINS_LOCAL, POINTERV2_MAX_DEPTH, POINTERV2_K_SET,
    V1_V_P, V1_N_CHAINS_LOCAL, V1_MAX_DEPTH,
    TEST_DEPTH, [(n, w, k) for n, w, k in BEAM_CONFIGS],
    SEEDS, RUN_MODE,
    HP_BEAM_W10_5HOP_MIN, HP_PARTIAL_5HOP_MIN, MID_BEAM_W10_LO, MID_BEAM_W10_HI, HF_BEAM_W10_MAX,
    HP_BEAM_CV_MAX, MONOTONIC_TOL,
    BASELINE_SANITY_LO, BASELINE_SANITY_HI,
    META_M6_RAIL_LO, META_M6_RAIL_HI,
    V1_DOC_RAIL_LO, V1_DOC_RAIL_HI,
)


# =============================================================================
# Substrate primitives (verbatim from Cell X v1 + Cell B v2)
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
    """Verbatim from pointer-chain v2 / Cell X v1."""
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


def _retrieve_1hop(E, W, R, s: int, p: int, sq: float) -> int:
    key = (E[s] * R[p] * sq).astype(np.float32)
    scores = E @ (W @ key)
    return int(scores.argmax())


def arm_single_chain_naive(E, R, sq, W, chains_test, depth: int) -> Dict[str, Any]:
    """Verbatim from Cell X v1: monolithic chain via top-1 cleanup per hop.
    Algorithmically equivalent to pointer-chain v2 chain mechanism.
    """
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


# =============================================================================
# Beam search (verbatim from Cell X v1)
# =============================================================================

def _topk_cleanup(E: np.ndarray, W: np.ndarray, R: np.ndarray,
                   sq: float, s_idx: int, p: int, K: int) -> Tuple[np.ndarray, np.ndarray]:
    """Top-K cleanup with softmax-over-topK ranking. Substrate-only."""
    key = (E[s_idx] * R[p] * sq).astype(np.float32)
    scores = E @ (W @ key)
    if K >= len(scores):
        topk_idx = np.argsort(-scores)
    else:
        partition_idx = np.argpartition(-scores, K)[:K]
        topk_idx = partition_idx[np.argsort(-scores[partition_idx])]
    topk_scores = scores[topk_idx]
    s_shifted = topk_scores - topk_scores.max()
    exp_s = np.exp(s_shifted)
    softmax = exp_s / (exp_s.sum() + 1e-12)
    return topk_idx.astype(np.int64), softmax.astype(np.float32)


def arm_beam_search(E, R, sq, W, chains_test, depth: int,
                     beam_width: int, top_k: int) -> Dict[str, Any]:
    """Beam search with multi-candidate parallel continuation + cumulative log-score ranking.
    Verbatim from Cell X v1.
    """
    n = len(chains_test)
    hits = 0
    correct_in_beam_per_hop = np.zeros(depth, dtype=np.int64)
    top1_in_beam_top1_per_hop = np.zeros(depth, dtype=np.int64)

    for chain in chains_test:
        s_start = chain[0][0]
        beam: List[Tuple[int, float]] = [(s_start, 0.0)]

        for i in range(depth):
            p = chain[i][1]
            target_at_i = chain[i][2]
            candidates: List[Tuple[int, float]] = []
            for (s_idx, cum_log) in beam:
                topk_idx, topk_softmax = _topk_cleanup(E, W, R, sq, s_idx, p, top_k)
                for j in range(len(topk_idx)):
                    s_new = int(topk_idx[j])
                    sc = float(topk_softmax[j])
                    log_sc = math.log(max(sc, 1e-12))
                    candidates.append((s_new, cum_log + log_sc))
            candidates.sort(key=lambda t: -t[1])
            beam = candidates[:beam_width]
            beam_idxs = {b[0] for b in beam}
            if target_at_i in beam_idxs:
                correct_in_beam_per_hop[i] += 1
            if beam and beam[0][0] == target_at_i:
                top1_in_beam_top1_per_hop[i] += 1

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


# =============================================================================
# Self-test
# =============================================================================

def _selftest() -> None:
    g = np.random.default_rng(0)
    n = 1024
    V = 60
    sq = math.sqrt(n)
    E = bipolar(V, n, g)
    R = bipolar(4, n, g)

    # T1: construction self-consistency
    triples_d, chains_d = make_deep_chains(20, V, 4, max_depth=10, g=g,
                                            disallow_s=set())
    assert len(triples_d) == 20 * 10
    assert len(chains_d) == 20
    W = ingest_hebbian(triples_d, E, R, sq, n)
    assert W.shape == (n, n)
    assert not np.isnan(W).any()
    print("[selftest] T1 PASS: construction self-consistent")

    # T2: arm_single_chain_naive at depth=5 beats chance
    chains_d5 = [c[:5] for c in chains_d]
    r_single = arm_single_chain_naive(E, R, sq, W, chains_d5, depth=5)
    assert 0.0 <= r_single["top1"] <= 1.0
    assert r_single["top1"] > 5.0 / V, \
        "T2 single top1=%.3f below chance" % r_single["top1"]
    print("[selftest] T2 PASS: single-top1 5hop top1=%.3f beats chance %.3f"
          % (r_single["top1"], 5.0 / V))

    # T3: beam(W=1, K=1) per-hop top-of-beam MUST equal single per_step_acc
    r_beam1 = arm_beam_search(E, R, sq, W, chains_d5, depth=5, beam_width=1, top_k=1)
    for i in range(5):
        assert abs(r_beam1["top_of_beam_correct_per_hop"][i] - r_single["per_step_acc"][i]) < 1e-6, \
            "T3 beam(W=1,K=1) hop %d top-of-beam %.3f must match single per_step %.3f" % (
                i, r_beam1["top_of_beam_correct_per_hop"][i], r_single["per_step_acc"][i])
    print("[selftest] T3 PASS: beam(W=1,K=1) equivalent to single per-hop top-1")

    # T4: beam top-of-beam <= correct-in-beam invariant
    r_beam5 = arm_beam_search(E, R, sq, W, chains_d5, depth=5, beam_width=5, top_k=3)
    for i in range(5):
        assert r_beam5["top_of_beam_correct_per_hop"][i] <= r_beam5["correct_in_beam_per_hop"][i] + 1e-6, \
            "T4 top-of-beam cannot exceed correct-in-beam at hop %d" % i
    print("[selftest] T4 PASS: beam invariant top_of_beam <= correct_in_beam")

    # T5: arm_single equivalent to pointer-chain v2 _retrieve_1hop chained
    s_idx = int(chains_d5[0][0][0])
    p_idx = int(chains_d5[0][0][1])
    idx_v1 = _retrieve_1hop(E, W, R, s_idx, p_idx, sq)
    key_pv2 = (E[s_idx] * R[p_idx] * sq).astype(np.float32)
    idx_pv2 = int((E @ (W @ key_pv2)).argmax())
    assert idx_v1 == idx_pv2, \
        "T5 cleanup primitive equivalence broken: v1=%d vs pv2=%d" % (idx_v1, idx_pv2)
    print("[selftest] T5 PASS: _retrieve_1hop EQUIVALENT to pointer-chain v2 inline (idx=%d)" % idx_v1)

    # T6: NaN guard production-scale
    big_n = 4096
    big_V = 80
    big_E = bipolar(big_V, big_n, g)
    big_R = bipolar(4, big_n, g)
    big_triples, big_chains = make_deep_chains(
        20, big_V, 4, max_depth=5, g=g, disallow_s=set())
    big_W = ingest_hebbian(big_triples, big_E, big_R, math.sqrt(big_n), big_n)
    r_big = arm_beam_search(
        big_E, big_R, math.sqrt(big_n), big_W, big_chains[:5], depth=5,
        beam_width=5, top_k=3)
    assert not math.isnan(r_big["top1"]), "T6 NaN at production-scale"
    print("[selftest] T6 PASS: production-scale beam no-NaN top1=%.3f" % r_big["top1"])

    # T7: bands locked (exact numerics)
    assert HP_BEAM_W10_5HOP_MIN == 0.50
    assert HP_PARTIAL_5HOP_MIN == 0.30
    assert META_M6_RAIL_LO == 0.08 and META_M6_RAIL_HI == 0.25
    assert V1_DOC_RAIL_LO == 0.20 and V1_DOC_RAIL_HI == 0.50
    assert BASELINE_SANITY_LO == 0.62 and BASELINE_SANITY_HI == 0.68
    assert HF_BEAM_W10_MAX == 0.20
    print("[selftest] T7 PASS: bands locked (META_M6=[%.2f,%.2f] V1_DOC=[%.2f,%.2f])"
          % (META_M6_RAIL_LO, META_M6_RAIL_HI, V1_DOC_RAIL_LO, V1_DOC_RAIL_HI))

    # T8: substrate-only LLM counter
    assert _LLM_CALL_COUNTER[0] == 0, "T8 LLM counter non-zero"
    print("[selftest] T8 PASS: LLM counter = 0")

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
        "n_predicates": n_predicates,
        "baseline_n_chains": BASELINE_N_CHAINS,
        "pointerv2_n_chains": POINTERV2_N_CHAINS_LOCAL,
        "pointerv2_max_depth": POINTERV2_MAX_DEPTH,
        "v1_n_chains": V1_N_CHAINS_LOCAL,
        "v1_max_depth": V1_MAX_DEPTH,
        "test_depth": TEST_DEPTH,
        "K_SET": POINTERV2_K_SET,
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

    # ===== Build W_v1_regime (EASIER: n=200 max_depth=5 -> 1000 bindings) =====
    t_arm = time.time()
    v1_disallow = set(int(c[0][0]) for c in pv2_chains)
    v1_triples, v1_chains = make_deep_chains(
        V1_N_CHAINS_LOCAL, V_CONCEPTS, V1_V_P,
        max_depth=V1_MAX_DEPTH, g=g, disallow_s=v1_disallow)
    W_v1 = ingest_hebbian(v1_triples, E, R, sq, N_DIM)
    v1_w_build_s = round(time.time() - t_arm, 2)
    print("  [seed=%d] W_v1_regime built (%d triples, %d chains, max_depth=%d) t=%.1fs"
          % (seed, len(v1_triples), len(v1_chains), V1_MAX_DEPTH,
             v1_w_build_s), flush=True)

    # Test query sets (truncated to TEST_DEPTH=5)
    if TEST_N_CHAINS is not None:
        pv2_test = [c[:TEST_DEPTH] for c in pv2_chains[:TEST_N_CHAINS]]
        v1_test = [c[:TEST_DEPTH] for c in v1_chains[:TEST_N_CHAINS]]
    else:
        pv2_test = [c[:TEST_DEPTH] for c in pv2_chains]
        v1_test = [c[:TEST_DEPTH] for c in v1_chains]

    # ===== ARM_REPRODUCE_POINTER_CHAIN_V2 (META_M6 rail; W_pointer_v2 regime) =====
    t_arm = time.time()
    r = arm_single_chain_naive(E, R, sq, W_pointer_v2, pv2_test, depth=TEST_DEPTH)
    r["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    r["regime"] = "pointer_v2 (n_chains=%d max_depth=%d -> %d bindings)" % (
        POINTERV2_N_CHAINS_LOCAL, POINTERV2_MAX_DEPTH, len(pv2_triples))
    r["mechanism"] = "k1_noise0_pointer_chain_v2_equivalent"
    out["arm_reproduce_pointer_chain_v2"] = r
    meta_m6_ok = (META_M6_RAIL_LO <= r["top1"] <= META_M6_RAIL_HI)
    out["meta_m6_rail_ok"] = meta_m6_ok
    print("  [seed=%d] ARM_REPRODUCE_POINTER_CHAIN_V2 top1=%.4f (META_M6_ok=%s) per_step=%s t=%.1fs"
          % (seed, r["top1"], meta_m6_ok, r["per_step_acc"], r["elapsed_s_arm"]), flush=True)

    # ===== ARM_SINGLE_TOP1_5HOP_V1_REGIME (informational; W_v1 regime) =====
    t_arm = time.time()
    r = arm_single_chain_naive(E, R, sq, W_v1, v1_test, depth=TEST_DEPTH)
    r["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    r["regime"] = "v1 (n_chains=%d max_depth=%d -> %d bindings)" % (
        V1_N_CHAINS_LOCAL, V1_MAX_DEPTH, len(v1_triples))
    r["mechanism"] = "k1_noise0_v1_regime_single_top1"
    out["arm_single_top1_5hop_v1_regime"] = r
    v1_doc_ok = (V1_DOC_RAIL_LO <= r["top1"] <= V1_DOC_RAIL_HI)
    out["v1_doc_rail_ok"] = v1_doc_ok
    print("  [seed=%d] ARM_SINGLE_TOP1_5HOP_V1_REGIME top1=%.4f (V1_DOC_ok=%s) per_step=%s t=%.1fs"
          % (seed, r["top1"], v1_doc_ok, r["per_step_acc"], r["elapsed_s_arm"]), flush=True)

    # ===== Beam arms (ALL on W_pointer_v2 regime; pv2_test queries) =====
    for arm_name, w, k in BEAM_CONFIGS:
        t_arm = time.time()
        r_b = arm_beam_search(E, R, sq, W_pointer_v2, pv2_test,
                               depth=TEST_DEPTH, beam_width=w, top_k=k)
        r_b["elapsed_s_arm"] = round(time.time() - t_arm, 2)
        r_b["regime"] = "pointer_v2 (matched regime)"
        out[arm_name.lower()] = r_b
        print(("  [seed=%d] %s top1=%.4f corr_in_beam=%s "
               "top_of_beam=%s t=%.1fs")
              % (seed, arm_name, r_b["top1"],
                 r_b["correct_in_beam_per_hop"],
                 r_b["top_of_beam_correct_per_hop"],
                 r_b["elapsed_s_arm"]), flush=True)

    out["elapsed_s"] = round(time.time() - t, 1)
    return out


# =============================================================================
# Verdict
# =============================================================================

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
    reproduce_pv2 = mean_top1("arm_reproduce_pointer_chain_v2")
    single_v1 = mean_top1("arm_single_top1_5hop_v1_regime")
    beam_w2 = mean_top1("arm_beam_w2_topk3_5hop")
    beam_w5 = mean_top1("arm_beam_w5_topk3_5hop")
    beam_w10 = mean_top1("arm_beam_w10_topk5_5hop")
    cv_w10 = cv_top1("arm_beam_w10_topk5_5hop")
    cv_w5 = cv_top1("arm_beam_w5_topk3_5hop")
    cv_w2 = cv_top1("arm_beam_w2_topk3_5hop")
    cv_repro = cv_top1("arm_reproduce_pointer_chain_v2")

    n_seeds = len(per_seed)
    majority = max(1, (n_seeds + 1) // 2)
    baseline_breach = sum(1 for p in per_seed if not p.get("baseline_sanity_ok", False))
    meta_m6_breach = sum(1 for p in per_seed if not p.get("meta_m6_rail_ok", False))
    v1_doc_breach = sum(1 for p in per_seed if not p.get("v1_doc_rail_ok", False))

    # Monotonic (within tol): W5 >= W2 - tol AND W10 >= W5 - tol
    monotonic_w5_over_w2 = (not math.isnan(beam_w5) and not math.isnan(beam_w2)
                              and beam_w5 >= beam_w2 - MONOTONIC_TOL)
    monotonic_w10_over_w5 = (not math.isnan(beam_w10) and not math.isnan(beam_w5)
                               and beam_w10 >= beam_w5 - MONOTONIC_TOL)
    monotonic_ok = monotonic_w5_over_w2 and monotonic_w10_over_w5

    # Q-saturation
    q_flags = []
    for name, val in [("BEAM_W10", beam_w10), ("BEAM_W5", beam_w5), ("BEAM_W2", beam_w2)]:
        if not math.isnan(val) and val >= Q_SATURATION:
            q_flags.append("[Q-DISCIPLINE: %s=%.4f >= %.3f suspect saturation; UNDER-CLAIM tier]"
                            % (name, val, Q_SATURATION))
    q_note = (" ".join(q_flags) + " ") if q_flags else ""

    summ = (
        "BASELINE=%.4f (sanity_breach=%d/%d in [%.2f,%.2f]) | "
        "REPRODUCE_POINTER_CHAIN_V2=%.4f (cv=%.3f META_M6_breach=%d/%d rail=[%.2f,%.2f]) | "
        "SINGLE_V1_REGIME=%.4f (V1_DOC_breach=%d/%d rail=[%.2f,%.2f] advisory) | "
        "BEAM_W2=%.4f (cv=%.3f) BEAM_W5=%.4f (cv=%.3f) BEAM_W10=%.4f (cv=%.3f) | "
        "monotonic_W5>=W2-tol=%s W10>=W5-tol=%s | "
        "lift_W10_over_REPRODUCE=%+.4f | "
        "pointer_v2_5hop_ref=0.122"
    ) % (
        baseline, baseline_breach, n_seeds, BASELINE_SANITY_LO, BASELINE_SANITY_HI,
        reproduce_pv2, cv_repro, meta_m6_breach, n_seeds, META_M6_RAIL_LO, META_M6_RAIL_HI,
        single_v1, v1_doc_breach, n_seeds, V1_DOC_RAIL_LO, V1_DOC_RAIL_HI,
        beam_w2, cv_w2, beam_w5, cv_w5, beam_w10, cv_w10,
        monotonic_w5_over_w2, monotonic_w10_over_w5,
        (beam_w10 - reproduce_pv2) if (not math.isnan(beam_w10)
                                        and not math.isnan(reproduce_pv2)) else float("nan"),
    )

    # SACRED rails (pre-empt verdict ladder)
    if baseline_breach >= majority:
        return "SANITY_BREACH", "SANITY_BREACH_BASELINE_OUT_OF_BAND: " + summ

    # META_M6 breach: special-case HP_WITH_META_M7_NOTE if BEAM_W10>=0.50 still met
    meta_m6_violated = (meta_m6_breach >= majority)

    # MODE B verdict ladder
    hp_chain_grade = (
        not math.isnan(beam_w10) and beam_w10 >= HP_BEAM_W10_5HOP_MIN
        and not meta_m6_violated
        and monotonic_ok
        and (math.isnan(cv_w10) or cv_w10 <= HP_BEAM_CV_MAX)
    )
    if hp_chain_grade:
        return "HARD_PASS", \
               ("HARD_PASS_CHAIN_GRADE_BARRIER_1_BEAM: %s%s" % (q_note, summ))

    hp_with_meta_m7 = (
        not math.isnan(beam_w10) and beam_w10 >= HP_BEAM_W10_5HOP_MIN
        and meta_m6_violated
    )
    if hp_with_meta_m7:
        return "HARD_PASS_WITH_META_M7_NOTE", \
               ("HARD_PASS_WITH_META_M7_NOTE_REPRODUCE_RAIL_BREACH_BUT_BEAM_LIFTS: %s%s"
                  % (q_note, summ))

    hp_partial = (not math.isnan(beam_w10) and beam_w10 >= HP_PARTIAL_5HOP_MIN)
    if hp_partial:
        return "HARD_PASS", \
               ("HARD_PASS_PARTIAL_BEAM_LIFT_OVER_RAIL: %s%s" % (q_note, summ))

    if not math.isnan(beam_w10) and MID_BEAM_W10_LO <= beam_w10 < MID_BEAM_W10_HI:
        return "MIDDLE_BAND", \
               ("MIDDLE_BAND_BEAM_MARGINAL: %s%s" % (q_note, summ))

    if not math.isnan(beam_w10) and beam_w10 < HF_BEAM_W10_MAX:
        return "HARD_FAIL", \
               ("HARD_FAIL_BEAM_DOESNT_HELP: %s%s" % (q_note, summ))

    return "MIDDLE_BAND", ("MIDDLE_BAND_UNCLASSIFIED: %s%s" % (q_note, summ))


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

    agg = aggregate_partials(out_dir, seeds=[str(s) for s in SEEDS],
                              run_config=run_config)
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
            "Cell X (beam search) v2 META_M6_rail: stage-1 re-analysis of Cell X v1 "
            "(substrate_multihop_beam_search_with_WM_candidates_v1) shows v1's "
            "SINGLE_TOP1_5HOP=0.33 was a REGIME ARTIFACT vs pointer-chain v2's "
            "0.122 mean (META_M7 cross-cell mismatch). v1 ran with W = "
            "make_deep_chains(n=200, V_P=10, max_depth=5) -> 1000 bindings; "
            "pointer-chain v2 used max_depth=10 -> 2000 bindings. The forward "
            "K=1 cleanup primitive is algorithmically identical across cells; "
            "the 2x crosstalk diff in the (V_C=200, V_P=10) key space drove the "
            "gap. v2 introduces two-W discipline: ARM_REPRODUCE_POINTER_CHAIN_V2 "
            "uses W_pointer_v2_regime (HARD; n=200 max_depth=10) for the META_M6 "
            "rail. All BEAM arms (W2/W5/W10) run on the HARD W_pointer_v2_regime "
            "so any lift over REPRODUCE_POINTER_CHAIN_V2 is real beam-search "
            "mechanism contribution, NOT a low-crosstalk W shortcut. "
            "ARM_SINGLE_TOP1_5HOP_V1_REGIME on W_v1_regime is informational "
            "(reproduces v1's 0.33). Same fix pattern as Cell B v2 + Cell C v2. "
            "Pre-reg: preregs/2026-06-25_gap1_multihop_beam_search_v2_META_M6_rail.md."
        ),
    }
    write_metrics(out_dir, metrics, results=per_seed)
    print("[done] metrics.json written (%d seeds, %.1fs)" % (
        len(per_seed), metrics["elapsed_s"]), flush=True)
