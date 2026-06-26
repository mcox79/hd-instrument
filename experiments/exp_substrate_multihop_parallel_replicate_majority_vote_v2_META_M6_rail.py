"""substrate_multihop_parallel_replicate_majority_vote_v2_META_M6_rail.

Cell X v2 -- META_M6-compliant re-dispatch of Cell X v1's parallel-replicate
majority-vote Barrier-1 attempt.

STAGE-1 SANITY FINDING (Mode B):
  Cell X v1 used the SAME cleanup primitive as pointer-chain v2 (verbatim
  algorithmically equivalent: key = E[s]*R[p]*sq; readout = W @ key; argmax
  over E; cleaned-atom index seeds next hop). The 0.78 single-chain 5HOP in
  v1 vs 0.122 in pointer-chain v2 was a REGIME ARTIFACT:
    v1 ran SMOKE (N=2048; n_chains=50 max_depth=5) -> W has 250 bindings
    pointer-chain v2 ran FULL (N=8192; n_chains=200 max_depth=10) -> W has 2000 bindings
  8x crosstalk diff in the same (V_C=200, V_P=10) key space exactly matches
  the documented pointer-chain v1 -> v2 BUG PATTERN.

V2 ARMS (5):
  ARM_BASELINE_HRR_2HOP             beta-sweep rail (sanity [0.62, 0.68])
  ARM_REPRODUCE_POINTER_CHAIN_V2    K=1 noise=0; W_pointer_v2_regime (n=200, max_depth=10); test depth=5
                                     -- target [0.08, 0.25] (META_M6 rail)
  ARM_CELLX_V1_AS_DOC               K=1 noise=0; W_v1_regime (n=50, max_depth=5); test depth=5
                                     -- target [0.60, 0.90] (replicates v1's 0.78)
  ARM_PARALLEL_K5_PERHOP_5HOP       K=5 noise=0.05 per-hop vote; W_pointer_v2_regime
  ARM_PARALLEL_K15_PERHOP_5HOP      K=15 noise=0.05 per-hop vote; W_pointer_v2_regime (primary)

The parallel arms use the HARD regime (W_pointer_v2_regime) so the lift (if
any) is the actual mechanism contribution, NOT a low-crosstalk W shortcut.

PRE-REG (LOCKED via module-init asserts):

  SACRED SANITY RAILS:
    RAIL_BASELINE:        baseline in [0.62, 0.68]                    (verdict pre-empt)
    RAIL_META_M6:         REPRODUCE_POINTER_CHAIN_V2 in [0.08, 0.25]  (verdict pre-empt; THE rail)
    RAIL_V1_DOCUMENTED:   CELLX_V1_AS_DOC in [0.60, 0.90]             (Stage-1 reproducibility check)

  MODE B verdict ladder (all 3 rails MUST pass):
    HARD_PASS_BARRIER_1_REVIVAL_VIA_PARALLEL_VOTE:
      K15 >= 0.70 AND K5 >= 0.50 AND monotonic K1<K5<K15 AND cv_K15 <= 0.07
    HARD_PASS_PARTIAL_BARRIER_1_LIFT:
      K15 >= 0.50 AND monotonic K1<K5<K15
    MIDDLE_BAND_VOTING_MARGINAL:
      K15 in [0.30, 0.50)
    HARD_FAIL_PARALLEL_DOESNT_HELP:
      K15 < 0.30

Author: exp_dev 2026-06-25 (Stage-1 sanity-check + Mode-B re-dispatch).
Pre-reg: preregs/2026-06-25_substrate_multihop_parallel_replicate_majority_vote_v2_META_M6_rail.md
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

ANCHOR_NAME = "substrate_multihop_parallel_replicate_majority_vote_v2_meta_m6_rail"
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

# Sanity rails (verdict pre-empted on majority-seed breach)
BASELINE_SANITY_LO = 0.62
BASELINE_SANITY_HI = 0.68

# META_M6 rail: ARM_REPRODUCE_POINTER_CHAIN_V2 must reproduce pointer-chain v2
# at IDENTICAL regime. Pointer-chain v2 seed=7=0.145, seed=17=0.11, seed=23=0.11
# (mean 0.122). +/-0.05 absorption.
META_M6_RAIL_LO = 0.08
META_M6_RAIL_HI = 0.25

# V1-documented rail: ARM_CELLX_V1_AS_DOC must reproduce Cell X v1's 0.78
# at v1's regime (smoke; N=2048; n_chains=50; depth=5). +/-0.10 absorption.
# (Full mode runs at N=8192 not N=2048; the 0.78 came from N=2048 + n=50 +
# depth-5 W; N=8192 + n=50 + depth=5 W should be in similar regime or BETTER
# because smaller W with larger N has even less crosstalk -> ceiling.)
V1_DOC_RAIL_LO = 0.60
V1_DOC_RAIL_HI = 0.90

# MODE B verdict thresholds
HP_K15_5HOP_MIN = 0.70
HP_K5_5HOP_MIN = 0.50
HP_CV_MAX = 0.07
HP_PARTIAL_K15_MIN = 0.50
MID_K15_LO = 0.30
MID_K15_HI = 0.50
HF_K15_MAX = 0.30  # strictly less than

# Lock assertions (catch accidental edits to bands)
assert HP_K15_5HOP_MIN > HP_K5_5HOP_MIN
assert HP_K5_5HOP_MIN >= MID_K15_HI
assert MID_K15_HI == HP_PARTIAL_K15_MIN
assert MID_K15_LO == HF_K15_MAX
assert BASELINE_SANITY_LO < BASELINE_SANITY_HI
assert META_M6_RAIL_LO < META_M6_RAIL_HI
assert V1_DOC_RAIL_LO < V1_DOC_RAIL_HI
# Stage-1 prediction asserts (predicting at-dispatch-time, locked)
assert META_M6_RAIL_HI < V1_DOC_RAIL_LO, \
    "META_M6 ceiling (%.2f) must be below V1_DOC floor (%.2f) -- stage-1 says regimes are different" % (
        META_M6_RAIL_HI, V1_DOC_RAIL_LO)

# =============================================================================
# Regime configs (the load-bearing diff vs Cell X v1)
# =============================================================================

# Baseline (verbatim beta-sweep regime; matches pointer-chain v2 baseline rail)
BASELINE_V_P = 2
BASELINE_N_CHAINS = 200

# Pointer-chain v2 regime: HARD regime; n=200 max_depth=10 -> 2000 W bindings
POINTERV2_N_CHAINS = 200
POINTERV2_MAX_DEPTH = 10
POINTERV2_V_P = 10
POINTERV2_K_SET = 20

# Cell X v1 regime: EASIER regime; n=50 max_depth=5 -> 250 W bindings
V1_N_CHAINS = 50
V1_MAX_DEPTH = 5
V1_V_P = 10

# Parallel-vote noise (verbatim from Cell X v1)
REPLICATE_NOISE_FRAC = 0.05

# Test depth (apples-to-apples comparison point across REPRODUCE + V1_DOC + PARALLEL)
TEST_DEPTH = 5

if RUN_MODE == "smoke":
    N_DIM = 2048
    V_CONCEPTS = 200
    SEEDS = [7]
    # Smoke: shrink chain counts but KEEP max_depth=10 for pointer-v2 regime (so
    # W has crosstalk-relevant size)
    POINTERV2_N_CHAINS_LOCAL = 50
    V1_N_CHAINS_LOCAL = 20
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
    "substrateMultihopParallelReplicateMajorityVote-v2-META_M6_rail: "
    "N=%d V_C=%d "
    "BASELINE_V_P=%d (p1=0/p2=1) BASELINE_N=%d "
    "POINTERV2_V_P=%d POINTERV2_N=%d POINTERV2_DEPTH=%d K_SET=%d "
    "V1_V_P=%d V1_N=%d V1_DEPTH=%d "
    "TEST_DEPTH=%d REPLICATE_NOISE_FRAC=%.3f "
    "K_REPLICATE_GRID=[1,5,15] "
    "seeds=%s mode=%s "
    "HP_K15>=%.2f HP_K5>=%.2f HP_cv<=%.2f HP_partial_K15>=%.2f "
    "mid_K15=[%.2f,%.2f] HF_K15<%.2f "
    "baseline_sanity=[%.2f,%.2f] META_M6_rail=[%.2f,%.2f] V1_DOC_rail=[%.2f,%.2f]"
) % (
    N_DIM, V_CONCEPTS,
    BASELINE_V_P, BASELINE_N_CHAINS,
    POINTERV2_V_P, POINTERV2_N_CHAINS_LOCAL, POINTERV2_MAX_DEPTH, POINTERV2_K_SET,
    V1_V_P, V1_N_CHAINS_LOCAL, V1_MAX_DEPTH,
    TEST_DEPTH, REPLICATE_NOISE_FRAC,
    SEEDS, RUN_MODE,
    HP_K15_5HOP_MIN, HP_K5_5HOP_MIN, HP_CV_MAX, HP_PARTIAL_K15_MIN,
    MID_K15_LO, MID_K15_HI, HF_K15_MAX,
    BASELINE_SANITY_LO, BASELINE_SANITY_HI,
    META_M6_RAIL_LO, META_M6_RAIL_HI,
    V1_DOC_RAIL_LO, V1_DOC_RAIL_HI,
)


# =============================================================================
# Substrate primitives (verbatim from pointer-chain v2 + Cell X v1)
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
    """Verbatim from beta-sweep / pointer-chain v2 L169-194. Fixed-pair (p1, p2)."""
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
    """Verbatim from beta-sweep / pointer-chain v2 L197-207."""
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
                      g: np.random.Generator, disallow_s: set
                      ) -> Tuple[List[Tuple[int, int, int]], List[List[Tuple[int, int, int]]]]:
    """Verbatim from pointer-chain v2 L230-267 / Cell X v1 L246-276."""
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
            "BLOCKING make_deep_chains: only %d/%d generated for V=%d max_depth=%d"
            % (len(chain_queries), n_chains, V, max_depth))
    return all_triples, chain_queries


# =============================================================================
# Multi-hop arms: K=1 (rail) and K=K (parallel-vote, verbatim from Cell X v1)
# =============================================================================

def _one_chain_step(W: np.ndarray, E: np.ndarray, R: np.ndarray, sq: float,
                     cur_state: np.ndarray, p: int,
                     noise: np.ndarray) -> Tuple[int, np.ndarray]:
    """Verbatim from Cell X v1 L283-298. One hop for ONE chain."""
    key = (cur_state * R[p] * sq).astype(np.float32)
    key_noisy = key + noise
    readout = W @ key_noisy
    scores = E @ readout
    next_idx = int(scores.argmax())
    new_state = E[next_idx].copy()
    return next_idx, new_state


def arm_parallel_replicate_majority_vote(
    E, R, sq, W, chains_test, depth: int, K_replicate: int,
    vote_protocol: str, seed: int
) -> Dict[str, Any]:
    """Verbatim from Cell X v1 L301-401. K=1 noise=0 degenerates to single-chain
    pointer-chain v2 mechanism.

    Per chain:
      Spawn K_replicate parallel chains, all starting at E[s_0].
      For hop i in 0..depth-1:
        Each of K chains independently:
          - Add per-chain independent noise to the key
          - Run one hop (W projection + cleanup)
          - Get candidate next-node idx
        Vote across K candidates -> consensus_idx_i
        If vote_protocol == "per_hop":
          All K chains adopt consensus_idx_i for next hop
        If vote_protocol == "at_end":
          Each chain keeps its own cleanup output
      Final answer:
        per_hop: consensus_idx at last hop
        at_end: majority vote across K chains' final outputs

    K_replicate=1 degenerates to single-chain (no voting, no noise per the
    K_replicate > 1 noise gate).
    """
    assert vote_protocol in ("per_hop", "at_end")
    g = np.random.default_rng(int(seed) * 7919 + 41 + hash(vote_protocol) % 1000)
    n = len(chains_test)
    n_dim = E.shape[1]
    hits = 0
    per_step_hits = np.zeros(depth, dtype=np.int64)
    diversity_sum = 0.0
    diversity_n = 0

    for chain in chains_test:
        s_idx = chain[0][0]
        chain_states = np.tile(E[s_idx], (K_replicate, 1)).astype(np.float32)
        chain_last_idx = np.full(K_replicate, s_idx, dtype=np.int64)

        for i in range(depth):
            p = chain[i][1]
            if K_replicate > 1 and REPLICATE_NOISE_FRAC > 0.0:
                noises = REPLICATE_NOISE_FRAC * g.standard_normal(
                    (K_replicate, n_dim)).astype(np.float32)
            else:
                noises = np.zeros((K_replicate, n_dim), dtype=np.float32)

            candidates = np.zeros(K_replicate, dtype=np.int64)
            for ck in range(K_replicate):
                next_idx, new_state = _one_chain_step(
                    W, E, R, sq, chain_states[ck], p, noises[ck])
                candidates[ck] = next_idx
                chain_states[ck] = new_state

            unique, counts = np.unique(candidates, return_counts=True)
            consensus_idx = int(unique[int(counts.argmax())])
            diversity_n += 1
            consensus_agreement = float(counts.max()) / max(K_replicate, 1)
            diversity_sum += (1.0 - consensus_agreement)

            if vote_protocol == "per_hop":
                chain_states[:] = E[consensus_idx]
                chain_last_idx[:] = consensus_idx
                hop_pred = consensus_idx
            else:
                chain_last_idx[:] = candidates
                hop_pred = consensus_idx

            if hop_pred == chain[i][2]:
                per_step_hits[i] += 1

        if vote_protocol == "per_hop":
            final_pred = int(chain_last_idx[0])
        else:
            unique, counts = np.unique(chain_last_idx, return_counts=True)
            final_pred = int(unique[int(counts.argmax())])

        if final_pred == chain[depth - 1][2]:
            hits += 1

    per_step_acc = (per_step_hits.astype(np.float32) / max(n, 1)).tolist()
    mean_diversity = diversity_sum / max(diversity_n, 1)
    return {
        "top1": round(hits / max(n, 1), 4),
        "per_step_acc": [round(x, 4) for x in per_step_acc],
        "n_queries": n,
        "depth": depth,
        "K_replicate": K_replicate,
        "vote_protocol": vote_protocol,
        "mean_diversity": round(float(mean_diversity), 4),
        "replicate_noise_frac": REPLICATE_NOISE_FRAC,
        "mechanism": "parallel_replicate_majority_vote",
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

    # T1: bipolar / ingest_hebbian / make_deep_chains construction
    triples_d, chains_d = make_deep_chains(20, V, 4, max_depth=2, g=g,
                                            disallow_s=set())
    assert len(triples_d) == 20 * 2
    assert len(chains_d) == 20
    W = ingest_hebbian(triples_d, E, R, sq, n)
    assert W.shape == (n, n)
    assert not np.isnan(W).any()
    print("[selftest] T1 PASS: construction self-consistent")

    # T2: K=1 noise=0 at small-W regime beats chance
    r_easy = arm_parallel_replicate_majority_vote(
        E, R, sq, W, chains_d, depth=2, K_replicate=1,
        vote_protocol="at_end", seed=42)
    assert 0.0 <= r_easy["top1"] <= 1.0
    assert r_easy["top1"] > 5.0 / V, \
        "T2 K=1 small-W top1=%.3f below chance" % r_easy["top1"]
    print("[selftest] T2 PASS: K=1 small-W top1=%.3f beats chance %.3f"
          % (r_easy["top1"], 5.0 / V))

    # T3: K=1 noise=0 at LARGER-W regime is LOWER than small-W (crosstalk hurts;
    # mechanism identical). WARN-only at selftest scale (V=60 may saturate).
    triples_h, chains_h = make_deep_chains(40, V, 4, max_depth=4, g=g,
                                            disallow_s=set())
    W_hard = ingest_hebbian(triples_h, E, R, sq, n)
    chains_h_d2 = [c[:2] for c in chains_h]
    r_hard = arm_parallel_replicate_majority_vote(
        E, R, sq, W_hard, chains_h_d2, depth=2, K_replicate=1,
        vote_protocol="at_end", seed=42)
    if r_hard["top1"] >= r_easy["top1"]:
        print("[selftest] T3 WARN: large-W top1=%.3f >= small-W top1=%.3f at "
              "selftest scale (V=%d small). Full run validates."
              % (r_hard["top1"], r_easy["top1"], V))
    else:
        print("[selftest] T3 PASS: large-W top1=%.3f < small-W top1=%.3f "
              "(crosstalk hurts; regime is load-bearing)"
              % (r_hard["top1"], r_easy["top1"]))

    # T4: K=5 noise>0 produces nonzero diversity
    r_k5 = arm_parallel_replicate_majority_vote(
        E, R, sq, W_hard, chains_h_d2, depth=2, K_replicate=5,
        vote_protocol="per_hop", seed=42)
    assert 0.0 <= r_k5["top1"] <= 1.0
    # diversity may be 0 if all chains agree (good case); just check no NaN
    assert not math.isnan(r_k5["mean_diversity"])
    print("[selftest] T4 PASS: K=5 per_hop top1=%.3f diversity=%.3f"
          % (r_k5["top1"], r_k5["mean_diversity"]))

    # T5: vote_at_end and vote_per_hop are distinct protocols
    r_end = arm_parallel_replicate_majority_vote(
        E, R, sq, W_hard, chains_h_d2, depth=2, K_replicate=5,
        vote_protocol="at_end", seed=42)
    r_per = arm_parallel_replicate_majority_vote(
        E, R, sq, W_hard, chains_h_d2, depth=2, K_replicate=5,
        vote_protocol="per_hop", seed=42)
    assert 0.0 <= r_end["top1"] <= 1.0
    assert 0.0 <= r_per["top1"] <= 1.0
    print("[selftest] T5 PASS: vote_at_end=%.3f vote_per_hop=%.3f"
          % (r_end["top1"], r_per["top1"]))

    # T6: NaN guard on production-scale
    big_n = 4096
    big_V = 80
    big_E = bipolar(big_V, big_n, g)
    big_R = bipolar(4, big_n, g)
    big_triples, big_chains = make_deep_chains(
        20, big_V, 4, max_depth=3, g=g, disallow_s=set())
    big_W = ingest_hebbian(big_triples, big_E, big_R, math.sqrt(big_n), big_n)
    r_big = arm_parallel_replicate_majority_vote(
        big_E, big_R, math.sqrt(big_n), big_W, big_chains[:5], depth=3,
        K_replicate=5, vote_protocol="per_hop", seed=99)
    assert not math.isnan(r_big["top1"]), "T6 NaN at production-scale"
    print("[selftest] T6 PASS: production-scale no-NaN top1=%.3f" % r_big["top1"])

    # T7: bands locked
    assert HP_K15_5HOP_MIN == 0.70
    assert HP_PARTIAL_K15_MIN == 0.50
    assert MID_K15_LO == HF_K15_MAX
    assert META_M6_RAIL_LO == 0.08 and META_M6_RAIL_HI == 0.25
    assert V1_DOC_RAIL_LO == 0.60 and V1_DOC_RAIL_HI == 0.90
    assert BASELINE_SANITY_LO == 0.62 and BASELINE_SANITY_HI == 0.68
    print("[selftest] T7 PASS: bands locked (META_M6=[%.2f,%.2f] V1_DOC=[%.2f,%.2f])"
          % (META_M6_RAIL_LO, META_M6_RAIL_HI, V1_DOC_RAIL_LO, V1_DOC_RAIL_HI))

    # T8: substrate-only-decode gate
    assert _LLM_CALL_COUNTER[0] == 0, "T8 LLM counter non-zero"
    print("[selftest] T8 PASS: LLM counter = 0")

    # T9: cleanup primitive equivalence math (Cell X v1 _one_chain_step vs
    # pointer-chain v2 _retrieve_1hop produce IDENTICAL index for K=1 noise=0)
    s_idx = int(chains_d[0][0][0])
    p_idx = int(chains_d[0][0][1])
    # Cell X v1 mechanism (via _one_chain_step)
    cur_state = E[s_idx].copy()
    noise_zero = np.zeros(n, dtype=np.float32)
    idx_v1, _ = _one_chain_step(W, E, R, sq, cur_state, p_idx, noise_zero)
    # pointer-chain v2 mechanism (inline)
    key_pv2 = (E[s_idx] * R[p_idx] * sq).astype(np.float32)
    idx_pv2 = int((E @ (W @ key_pv2)).argmax())
    assert idx_v1 == idx_pv2, (
        "T9 cleanup primitive equivalence broken: Cell X v1 idx=%d vs "
        "pointer-chain v2 idx=%d" % (idx_v1, idx_pv2))
    print("[selftest] T9 PASS: Cell X v1 _one_chain_step (K=1 noise=0) "
          "EQUIVALENT to pointer-chain v2 _retrieve_1hop (idx=%d)" % idx_v1)

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
        "replicate_noise_frac": REPLICATE_NOISE_FRAC,
        "config_version": CONFIG_VERSION,
        "_llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
    }

    # ===== ARM_BASELINE_HRR_2HOP (sanity rail; verbatim beta-sweep) =====
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

    # ===== Build W_v1_regime (EASIER: n=50 max_depth=5 -> 250 bindings) =====
    # Use fresh chain generator + disallow_s so v1 chains don't overlap pv2
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

    # ===== ARM_REPRODUCE_POINTER_CHAIN_V2 (META_M6 rail; K=1 noise=0; W_pointer_v2) =====
    t_arm = time.time()
    r = arm_parallel_replicate_majority_vote(
        E, R, sq, W_pointer_v2, pv2_test, depth=TEST_DEPTH, K_replicate=1,
        vote_protocol="at_end", seed=seed)
    r["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    r["regime"] = "pointer_v2 (n_chains=%d max_depth=%d -> %d bindings)" % (
        POINTERV2_N_CHAINS_LOCAL, POINTERV2_MAX_DEPTH, len(pv2_triples))
    out["arm_reproduce_pointer_chain_v2"] = r
    meta_m6_ok = (META_M6_RAIL_LO <= r["top1"] <= META_M6_RAIL_HI)
    out["meta_m6_rail_ok"] = meta_m6_ok
    print("  [seed=%d] ARM_REPRODUCE_POINTER_CHAIN_V2 top1=%.4f (META_M6_ok=%s) t=%.1fs"
          % (seed, r["top1"], meta_m6_ok, r["elapsed_s_arm"]), flush=True)

    # ===== ARM_CELLX_V1_AS_DOC (K=1 noise=0; W_v1) =====
    t_arm = time.time()
    r = arm_parallel_replicate_majority_vote(
        E, R, sq, W_v1, v1_test, depth=TEST_DEPTH, K_replicate=1,
        vote_protocol="at_end", seed=seed)
    r["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    r["regime"] = "v1 (n_chains=%d max_depth=%d -> %d bindings)" % (
        V1_N_CHAINS_LOCAL, V1_MAX_DEPTH, len(v1_triples))
    out["arm_cellx_v1_as_doc"] = r
    v1_doc_ok = (V1_DOC_RAIL_LO <= r["top1"] <= V1_DOC_RAIL_HI)
    out["v1_doc_rail_ok"] = v1_doc_ok
    print("  [seed=%d] ARM_CELLX_V1_AS_DOC top1=%.4f (V1_DOC_ok=%s) t=%.1fs"
          % (seed, r["top1"], v1_doc_ok, r["elapsed_s_arm"]), flush=True)

    # ===== ARM_PARALLEL_K5_PERHOP_5HOP (K=5; W_pointer_v2 regime) =====
    t_arm = time.time()
    r = arm_parallel_replicate_majority_vote(
        E, R, sq, W_pointer_v2, pv2_test, depth=TEST_DEPTH, K_replicate=5,
        vote_protocol="per_hop", seed=seed)
    r["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    r["regime"] = "pointer_v2 (matched regime)"
    out["arm_parallel_k5_perhop_5hop"] = r
    print("  [seed=%d] ARM_PARALLEL_K5_PERHOP_5HOP top1=%.4f diversity=%.3f t=%.1fs"
          % (seed, r["top1"], r["mean_diversity"], r["elapsed_s_arm"]), flush=True)

    # ===== ARM_PARALLEL_K15_PERHOP_5HOP (K=15; W_pointer_v2 regime; PRIMARY) =====
    t_arm = time.time()
    r = arm_parallel_replicate_majority_vote(
        E, R, sq, W_pointer_v2, pv2_test, depth=TEST_DEPTH, K_replicate=15,
        vote_protocol="per_hop", seed=seed)
    r["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    r["regime"] = "pointer_v2 (matched regime)"
    out["arm_parallel_k15_perhop_5hop"] = r
    print("  [seed=%d] ARM_PARALLEL_K15_PERHOP_5HOP top1=%.4f diversity=%.3f t=%.1fs"
          % (seed, r["top1"], r["mean_diversity"], r["elapsed_s_arm"]), flush=True)

    out["elapsed_s"] = round(time.time() - t, 1)
    return out


# =============================================================================
# Verdict
# =============================================================================

def verdict_from(per_seed: List[Dict[str, Any]]) -> Tuple[str, str]:
    def mean_field(key: str, field: str) -> float:
        vals = [p[key][field] for p in per_seed if key in p
                and isinstance(p[key].get(field), (int, float))
                and not math.isnan(p[key][field])]
        return float(np.mean(vals)) if vals else float("nan")

    def cv_field(key: str, field: str) -> float:
        vals = [p[key][field] for p in per_seed if key in p
                and isinstance(p[key].get(field), (int, float))
                and not math.isnan(p[key][field])]
        if len(vals) < 2:
            return 0.0
        m = float(np.mean(vals))
        return float(np.std(vals) / max(abs(m), 1e-9))

    baseline = mean_field("arm_baseline_hrr_2hop", "top1")
    reproduce_pv2 = mean_field("arm_reproduce_pointer_chain_v2", "top1")
    v1_doc = mean_field("arm_cellx_v1_as_doc", "top1")
    k5_perhop = mean_field("arm_parallel_k5_perhop_5hop", "top1")
    k15_perhop = mean_field("arm_parallel_k15_perhop_5hop", "top1")

    cv_k5 = cv_field("arm_parallel_k5_perhop_5hop", "top1")
    cv_k15 = cv_field("arm_parallel_k15_perhop_5hop", "top1")
    cv_repro = cv_field("arm_reproduce_pointer_chain_v2", "top1")
    cv_v1doc = cv_field("arm_cellx_v1_as_doc", "top1")

    # Rail breach counts (majority pre-empts verdict)
    n_seeds = len(per_seed)
    baseline_breach = sum(1 for p in per_seed if not p.get("baseline_sanity_ok", False))
    meta_m6_breach = sum(1 for p in per_seed if not p.get("meta_m6_rail_ok", False))
    v1_doc_breach = sum(1 for p in per_seed if not p.get("v1_doc_rail_ok", False))

    # Monotonicity K1 < K5 < K15 (K1 = reproduce_pv2 at matched regime)
    monotonic = (not math.isnan(reproduce_pv2) and not math.isnan(k5_perhop)
                 and not math.isnan(k15_perhop)
                 and reproduce_pv2 < k5_perhop < k15_perhop)

    summ = ("BASELINE=%.4f (sanity_breach=%d/%d in [%.2f,%.2f]) | "
            "REPRODUCE_POINTER_CHAIN_V2=%.4f (cv=%.3f META_M6_breach=%d/%d rail=[%.2f,%.2f]) | "
            "CELLX_V1_AS_DOC=%.4f (cv=%.3f V1_DOC_breach=%d/%d rail=[%.2f,%.2f]) | "
            "K5_PERHOP_5HOP=%.4f (cv=%.3f) K15_PERHOP_5HOP=%.4f (cv=%.3f) | "
            "monotonic_K1<K5<K15=%s | "
            "pointer_v2_5hop_full=0.122 v1_smoke_5hop=0.78 (reference)"
            ) % (
        baseline, baseline_breach, n_seeds,
        BASELINE_SANITY_LO, BASELINE_SANITY_HI,
        reproduce_pv2, cv_repro, meta_m6_breach, n_seeds,
        META_M6_RAIL_LO, META_M6_RAIL_HI,
        v1_doc, cv_v1doc, v1_doc_breach, n_seeds,
        V1_DOC_RAIL_LO, V1_DOC_RAIL_HI,
        k5_perhop, cv_k5,
        k15_perhop, cv_k15,
        monotonic,
    )

    # SACRED rails (pre-empt verdict ladder)
    majority = max(1, (n_seeds + 1) // 2)
    if baseline_breach >= majority:
        return "RAIL_BASELINE_BREACH", "RAIL_BASELINE_BREACH_OUT_OF_BAND: " + summ
    if meta_m6_breach >= majority:
        return "META_M6_RAIL_VIOLATION", \
               "META_M6_RAIL_VIOLATION_REPRODUCE_POINTER_CHAIN_V2_OUT_OF_RAIL: " + summ
    if v1_doc_breach >= majority:
        return "RAIL_V1_DOC_BREACH", \
               "RAIL_V1_DOC_BREACH_CELLX_V1_AS_DOC_OUT_OF_RAIL: " + summ

    # MODE B verdict ladder
    # HARD_PASS_CHAIN_GRADE
    hp_chain = (
        not math.isnan(k15_perhop) and k15_perhop >= HP_K15_5HOP_MIN
        and not math.isnan(k5_perhop) and k5_perhop >= HP_K5_5HOP_MIN
        and monotonic
        and cv_k15 <= HP_CV_MAX
        and cv_k5 <= HP_CV_MAX
    )
    if hp_chain:
        return "HARD_PASS_BARRIER_1_REVIVAL_VIA_PARALLEL_VOTE", \
               "HARD_PASS_BARRIER_1_REVIVAL_VIA_PARALLEL_VOTE_AT_MATCHED_REGIME: " + summ

    # HARD_PASS_PARTIAL
    hp_partial = (not math.isnan(k15_perhop) and k15_perhop >= HP_PARTIAL_K15_MIN
                   and monotonic)
    if hp_partial:
        return "HARD_PASS_PARTIAL_BARRIER_1_LIFT", \
               "HARD_PASS_PARTIAL_PARALLEL_VOTE_LIFTS_AT_MATCHED_REGIME: " + summ

    # MIDDLE_BAND
    if not math.isnan(k15_perhop) and MID_K15_LO <= k15_perhop < MID_K15_HI:
        return "MIDDLE_BAND_VOTING_MARGINAL", \
               "MIDDLE_BAND_VOTING_MARGINAL_AT_MATCHED_REGIME: " + summ

    # HARD_FAIL
    if not math.isnan(k15_perhop) and k15_perhop < HF_K15_MAX:
        return "HARD_FAIL_PARALLEL_DOESNT_HELP", \
               "HARD_FAIL_PARALLEL_VOTING_DOESNT_HELP_AT_MATCHED_REGIME_ERRORS_CORRELATE: " + summ

    return "MIDDLE_BAND_VOTING_MARGINAL", "MIDDLE_BAND_UNCLASSIFIED: " + summ


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
            "Cell X v2 META_M6_rail: stage-1 sanity-check of Cell X v1 found "
            "v1's 0.78 single-chain 5HOP was a REGIME ARTIFACT (v1 ran SMOKE "
            "with N=2048 n_chains=50 max_depth=5 -> 250 W bindings, vs "
            "pointer-chain v2 FULL with N=8192 n_chains=200 max_depth=10 -> "
            "2000 W bindings; 8x crosstalk diff in same V_C=200, V_P=10 key "
            "space). Cell X v1 and pointer-chain v2 use the SAME cleanup "
            "primitive (verbatim algorithmically equivalent: key=E[s]*R[p]*sq; "
            "readout=W@key; argmax over E; cleaned-atom index seeds next hop). "
            "v2 introduces two-W discipline: ARM_REPRODUCE_POINTER_CHAIN_V2 "
            "uses W_pointer_v2_regime (HARD; n=200 max_depth=10); "
            "ARM_CELLX_V1_AS_DOC uses W_v1_regime (EASIER; n=50 max_depth=5). "
            "Parallel arms (K=5, K=15 per_hop vote) use the HARD regime so "
            "any lift is real mechanism contribution, NOT low-crosstalk W "
            "shortcut. META_M6_RAIL ([0.08, 0.25]) enforces that REPRODUCE "
            "actually reproduces pointer-chain v2 at identical regime; "
            "otherwise all comparisons are uninterpretable. Pre-reg: "
            "preregs/2026-06-25_substrate_multihop_parallel_replicate_majority_vote_v2_META_M6_rail.md."
        ),
    }
    write_metrics(out_dir, metrics, results=per_seed)
    print("[done] metrics.json written (%d seeds, %.1fs)" % (
        len(per_seed), metrics["elapsed_s"]), flush=True)
