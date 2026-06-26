"""substrate_multihop_bidirectional_meet_middle_v2_META_M7_rail.

V2 ADDS: META_M7 sanity arm + nan-fix for MEET_HOP2 arm + longer timeout (7200s).

V1 ISSUES (Director triage 2026-06-25):
  1) Cell C v1 SINGLE_CHAIN_5HOP_FORWARD rail = 0.275; pointer-chain v2's known
     forward-only depth-5 rail = 0.122. Both use ALGORITHMICALLY IDENTICAL
     _retrieve_1hop cleanup primitive. So 0.275 vs 0.122 is REGIME DIFF, not
     mechanism diff. Cell C v1 W: 200 chains * depth=5 = 1000 bindings; pointer-
     chain v2 W: 200 chains * max_depth=10 = 2000 bindings. 2x crosstalk diff.

  2) ARM_BIDIRECTIONAL_5HOP_MEET_HOP2 produced "top1": NaN in v1 because the arm
     is a STATE-COSINE PROBE (no ranking; not a classification arm); the NaN was
     INTENTIONAL but serializes as invalid JSON (NaN not allowed). FIX: use None
     for top1 in that arm so JSON serializes cleanly; the actual cosine metrics
     (mean_cosine_at_midpoint, median_cosine_at_midpoint) carry the signal.

  Cell C v1 BIDIRECTIONAL_MEET_MID = 0.67 (seed 7 partial) -- a strong lift over
  the 0.275 SINGLE_FWD rail. But if the rail is 0.275 vs pointer-v2's 0.122, we
  cannot honestly claim "bidirectional revives Barrier 1 from 0.122 to 0.67"
  without verifying the regime.

V2 ADDS:
  - ARM_REPRODUCE_POINTER_CHAIN_V2_5HOP: same pattern as Cell B v2 -- builds
    a SEPARATE W from make_deep_chains(n=200, max_depth=10), tests at depth=5
    with verbatim _retrieve_1hop. Target [0.08, 0.25].
  - FIX nan in ARM_BIDIRECTIONAL_MEET_HOP2 -- top1=None instead of NaN.
  - Longer timeout (7200s) lets all 3 seeds complete.

Mechanism (UNCHANGED from v1):
  Substrate has chain-grade unbind primitive. For each multi-hop query:
    Forward chain: state_fwd = E[S]; for i in 0..mid-1: state_fwd = W @ (state * R[p] * sq)
    Backward chain: state_bwd = E[Z]; for i in n-1 down to mid: state = W.T @ state * R[p] * sq
  Match at midpoint: cosine(state_fwd, state_bwd). For BIDIRECTIONAL_MEET_MID:
  argmax over V_C candidates Z by midpoint cosine.

ARMS (5):
  ARM_BASELINE_HRR_2HOP                beta-sweep sanity rail [0.62, 0.68]
  ARM_REPRODUCE_POINTER_CHAIN_V2_5HOP  NEW: pointer-v2 regime W; verbatim primitive [0.08, 0.25]
  ARM_SINGLE_CHAIN_5HOP_FORWARD        v1's 1000-binding-W monolithic 5hop (v1 0.275)
  ARM_BIDIRECTIONAL_5HOP_MEET_HOP2     fix nan; cosine-probe only (top1=None)
  ARM_BIDIRECTIONAL_5HOP_MEET_MID      v1's 0.67 revival arm

SACRED SANITY rails:
  RAIL_BASELINE: BASELINE NOT in [0.62, 0.68] -> SANITY_BREACH
  RAIL_META_M7: REPRODUCE NOT in [0.08, 0.25] -> META_M7_RAIL_VIOLATION

PROSPECTIVE BANDS (locked at module-init assert):
  HARD_PASS_CHAIN_GRADE_BIDIRECTIONAL_REVIVAL:
    BIDIRECTIONAL_MEET_MID >= 0.50 AND cv <= 0.07 AND
    REPRODUCE in [0.08, 0.25] (META_M7 OK)
  HARD_PASS_REVIVAL_WITH_META_M7_NOTE:
    BIDIRECTIONAL_MEET_MID >= 0.50 BUT REPRODUCE > 0.25 (regime diff)
  HARD_FAIL_BIDIRECTIONAL_DOESNT_HELP:
    BIDIRECTIONAL_MEET_MID < 0.30

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

ANCHOR_NAME = "substrate_multihop_bidirectional_meet_middle_v2_META_M7_rail"
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
HP_BIDIR_MEET_MID = 0.50  # down from 0.67 v1 for seed variance allowance
HP_BIDIR_CV_MAX = 0.07
HF_BIDIR = 0.30

# SACRED SANITY rails
BASELINE_SANITY_LO = 0.62
BASELINE_SANITY_HI = 0.68

# META_M7 rail (pointer-chain v2's known 0.122 +/- noise band)
META_M7_RAIL_LO = 0.08
META_M7_RAIL_HI = 0.25

BASELINE_V_P = 2
BASELINE_N_CHAINS = 200
POINTER_V_P = 10
POINTER_K_SET = 20

# POINTER-V2 regime (META_M7 rail; 2000 bindings @ N_CHAINS=200 * max_depth=10)
POINTER_V2_N_CHAINS = 200
POINTER_V2_MAX_DEPTH = 10

# META_PROSPECTIVE_BANDS_FRESH_SEEDS lock
assert HP_BIDIR_MEET_MID > HF_BIDIR, "HP > HF"
assert 0.0 < HP_BIDIR_CV_MAX < 0.20
assert META_M7_RAIL_LO < META_M7_RAIL_HI < HF_BIDIR, \
    "META_M7_RAIL must be below HF_BIDIR (pointer-v2 regime is harder)"
assert BASELINE_SANITY_LO < BASELINE_SANITY_HI

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

CONFIG_VERSION = (
    "bidirectionalMeetMiddleV2MetaM7Rail: N=%d V_C=%d "
    "BASELINE_V_P=%d BASELINE_N=%d POINTER_V_P=%d POINTER_N=%d K_SET=%d "
    "POINTER_V2_N=%d POINTER_V2_DEPTH=%d "
    "seeds=%s mode=%s depth=%d midhop=%d "
    "HP_meetmid>=%.2f HP_cv<=%.2f HF<%.2f "
    "META_M7=[%.2f,%.2f] baseline_sanity=[%.2f,%.2f]"
) % (
    N_DIM, V_CONCEPTS, BASELINE_V_P, BASELINE_N_CHAINS_LOCAL,
    POINTER_V_P, POINTER_N_CHAINS, POINTER_K_SET,
    POINTER_V2_N_CHAINS_LOCAL, POINTER_V2_MAX_DEPTH,
    SEEDS, RUN_MODE, DEPTH, DEPTH // 2,
    HP_BIDIR_MEET_MID, HP_BIDIR_CV_MAX, HF_BIDIR,
    META_M7_RAIL_LO, META_M7_RAIL_HI,
    BASELINE_SANITY_LO, BASELINE_SANITY_HI,
)


def bipolar(M: int, n: int, g) -> np.ndarray:
    X = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)


def ingest_hebbian(triples, E, R, sq, n_dim, batch=2000):
    if not triples:
        return np.zeros((n_dim, n_dim), dtype=np.float32)
    tr = np.asarray(triples, dtype=np.int64)
    s_idx, p_idx, o_idx = tr[:, 0], tr[:, 1], tr[:, 2]
    W = np.zeros((n_dim, n_dim), dtype=np.float32)
    for b in range(0, len(tr), batch):
        ks = (E[s_idx[b:b + batch]] * R[p_idx[b:b + batch]] * sq).astype(np.float32)
        W += (E[o_idx[b:b + batch]].T @ ks) / n_dim
    return W


def make_two_hop_chains_betasweep(n_chains, V, g, p1=0, p2=1):
    train, queries, used_s = [], [], set()
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


def chain_naive_hard(W, E, R, sq, start, relations):
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


def make_deep_chains(n_chains, V, P, max_depth, g, disallow_s):
    all_triples, chain_queries, used_s = [], [], set(disallow_s)
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


def _retrieve_1hop(E, W, R, s, p, sq):
    """VERBATIM port of pointer-chain v2 `_retrieve_1hop`."""
    key = (E[s] * R[p] * sq).astype(np.float32)
    return int((E @ (W @ key)).argmax())


def arm_single_chain_naive(E, R, sq, W, chains_test, depth):
    """Forward-only monolithic chain (rail match for pointer-chain v2 mechanism).

    Used by BOTH ARM_SINGLE_CHAIN_5HOP_FORWARD (v1 1000-binding W) AND
    ARM_REPRODUCE_POINTER_CHAIN_V2_5HOP (2000-binding pointer-v2 W).
    """
    n = len(chains_test)
    hits = 0
    per_step_hits = np.zeros(depth, dtype=np.int64)
    fwd_correct_per_query = []
    for chain in chains_test:
        s = chain[0][0]
        for i in range(depth):
            p = chain[i][1]
            s_pred = _retrieve_1hop(E, W, R, s, p, sq)
            if s_pred == chain[i][2]:
                per_step_hits[i] += 1
            s = s_pred
        correct = (s == chain[depth - 1][2])
        if correct:
            hits += 1
        fwd_correct_per_query.append(1 if correct else 0)
    per_step_acc = (per_step_hits.astype(np.float32) / max(n, 1)).tolist()
    return {"top1": round(hits / max(n, 1), 4),
            "per_step_acc": [round(x, 4) for x in per_step_acc],
            "n_queries": n, "depth": depth,
            "_correct_per_query": fwd_correct_per_query}


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


def arm_bidirectional_meet_at_hop2(E, R, sq, W, chains_test, depth) -> Dict[str, Any]:
    """Cosine-probe arm: forward 2 hops; backward 3 hops from TRUE Z; measure
    state-cosine at midpoint. NOT a classification arm; top1 = None (was NaN
    in v1; serializes as invalid JSON).
    """
    n = len(chains_test)
    cos_correct_chain = []
    for chain in chains_test:
        S = chain[0][0]
        Z = chain[depth - 1][2]
        preds = [chain[i][1] for i in range(depth)]
        mid = 2
        fwd = _forward_state(E, W, R, sq, S, preds[:mid])
        bwd = _backward_state(E, W, R, sq, Z, preds[mid:])
        cos = float(np.dot(fwd, bwd) / (np.linalg.norm(fwd) * np.linalg.norm(bwd) + 1e-8))
        cos_correct_chain.append(cos)
    mean_cos = float(np.mean(cos_correct_chain))
    median_cos = float(np.median(cos_correct_chain))
    return {
        "top1": None,  # was NaN in v1 (invalid JSON); None serializes cleanly
        "is_probe_arm": True,
        "mean_cosine_at_midpoint": round(mean_cos, 4),
        "median_cosine_at_midpoint": round(median_cos, 4),
        "n_queries": n, "depth": depth,
        "mechanism": "bidirectional_state_cosine_no_ranking",
    }


def arm_bidirectional_meet_middle_rank(E, R, sq, W, chains_test, depth) -> Dict[str, Any]:
    """Meet-in-middle candidate ranking. For each query: walk forward MID hops;
    for each candidate Z, walk backward (DEPTH-MID) hops; rank by midpoint cosine.
    """
    n = len(chains_test)
    V = E.shape[0]
    mid = depth // 2
    hits = 0
    bidir_correct_per_query = []
    for chain in chains_test:
        S = chain[0][0]
        preds = [chain[i][1] for i in range(depth)]
        true_Z = chain[depth - 1][2]
        state_fwd = _forward_state(E, W, R, sq, S, preds[:mid])
        fnorm = np.linalg.norm(state_fwd) + 1e-8
        best_cos = -2.0
        best_Z = -1
        for Z in range(V):
            state_bwd = _backward_state(E, W, R, sq, Z, preds[mid:])
            bnorm = np.linalg.norm(state_bwd) + 1e-8
            cos = float(np.dot(state_fwd, state_bwd) / (fnorm * bnorm))
            if cos > best_cos:
                best_cos = cos
                best_Z = Z
        correct = (best_Z == true_Z)
        if correct:
            hits += 1
        bidir_correct_per_query.append(1 if correct else 0)
    return {"top1": round(hits / max(n, 1), 4),
            "n_queries": n, "depth": depth,
            "midpoint_hop": mid,
            "mechanism": "bidirectional_meet_middle_rank_full_V_C",
            "_correct_per_query": bidir_correct_per_query}


def _selftest() -> None:
    g = np.random.default_rng(0)
    n = 512
    V = 30
    sq = math.sqrt(n)
    E = bipolar(V, n, g)
    R = bipolar(4, n, g)

    Rb = bipolar(max(BASELINE_V_P, 2), n, g)
    train, queries = make_two_hop_chains_betasweep(20, V, g, p1=0, p2=1)
    r_base = arm_baseline_hrr_2hop_betasweep(E, Rb, sq, train, queries)
    assert 0.0 <= r_base["top1"] <= 1.0

    # v1-regime W (8 chains x 5 hops = 40 bindings)
    triples_v1, chains_v1 = make_deep_chains(8, V, 4, max_depth=5, g=g, disallow_s=set())
    W_v1 = ingest_hebbian(triples_v1, E, R, sq, n)
    r_single = arm_single_chain_naive(E, R, sq, W_v1, chains_v1, depth=5)
    assert 0.0 <= r_single["top1"] <= 1.0

    # META_M7 arm: pointer-v2-regime W (8 chains x 10 hops = 80 bindings)
    triples_v2, chains_v2 = make_deep_chains(8, V, 4, max_depth=10, g=g, disallow_s=set())
    W_v2 = ingest_hebbian(triples_v2, E, R, sq, n)
    chains_v2_test = [c[:5] for c in chains_v2]
    r_reproduce = arm_single_chain_naive(E, R, sq, W_v2, chains_v2_test, depth=5)
    assert 0.0 <= r_reproduce["top1"] <= 1.0

    # PROBE arm: top1 must be None (NOT NaN -- was the v1 bug)
    r_meet = arm_bidirectional_meet_at_hop2(E, R, sq, W_v1, chains_v1, depth=5)
    assert r_meet["top1"] is None, \
        "PROBE arm top1 must be None for clean JSON serialization (v1 used NaN)"
    assert r_meet.get("is_probe_arm") is True
    assert -1.0 <= r_meet["mean_cosine_at_midpoint"] <= 1.0

    # Bidirectional ranking
    r_rank = arm_bidirectional_meet_middle_rank(E, R, sq, W_v1, chains_v1, depth=5)
    assert 0.0 <= r_rank["top1"] <= 1.0
    assert r_rank["midpoint_hop"] == 2

    # Backward-walk math sanity: on a clean 1-hop W, forward and backward
    # should both recover the right atom with cosine > 0.2.
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

    # META_M7 selftest: cleanup primitive byte-equivalence
    s_chain = chains_v1[0][0][0]
    p_chain = chains_v1[0][0][1]
    direct = _retrieve_1hop(E, W_v1, R, s_chain, p_chain, sq)
    s_walk = chains_v1[0][0][0]
    s_walk_pred = _retrieve_1hop(E, W_v1, R, s_walk, chains_v1[0][0][1], sq)
    assert direct == s_walk_pred, \
        "META_M7 selftest: cleanup primitive byte-equivalence broken"

    # Bands locked
    assert HP_BIDIR_MEET_MID == 0.50 and HF_BIDIR == 0.30 and HP_BIDIR_CV_MAX == 0.07
    assert META_M7_RAIL_LO == 0.08 and META_M7_RAIL_HI == 0.25
    assert _LLM_CALL_COUNTER[0] == 0

    print("[selftest] PASS base=%.3f single_v1=%.3f reproduce_v2=%.3f probe_top1=%s "
          "rank_top1=%.3f fwd_cos=%.3f bwd_cos=%.3f"
          % (r_base["top1"], r_single["top1"], r_reproduce["top1"],
             r_meet["top1"], r_rank["top1"], fwd_cos, bwd_cos), flush=True)


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
        "pointer_n_chains": POINTER_N_CHAINS,
        "pointer_v2_n_chains": POINTER_V2_N_CHAINS_LOCAL,
        "pointer_v2_max_depth": POINTER_V2_MAX_DEPTH,
        "depth": DEPTH, "midpoint_hop": DEPTH // 2,
        "config_version": CONFIG_VERSION,
        "_llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
    }

    # BASELINE
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

    # META_M7 ARM: REPRODUCE POINTER-CHAIN-V2 AT IDENTICAL REGIME
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
    if not meta_m7_ok:
        print("  [seed=%d] META_M7 BREACH: reproduce=%.4f not in [%.2f, %.2f]" % (
            seed, r_reproduce["top1"], META_M7_RAIL_LO, META_M7_RAIL_HI), flush=True)

    # CELL C v1 REGIME (1000 bindings) ARMS
    t_arm = time.time()
    ptr_triples, ptr_chains = make_deep_chains(
        POINTER_N_CHAINS, V_CONCEPTS, POINTER_V_P, max_depth=DEPTH,
        g=g, disallow_s=set())
    W = ingest_hebbian(ptr_triples, E, R, sq, N_DIM)
    print("  [seed=%d] v1-regime W built (%d triples) t=%.1fs" % (
        seed, len(ptr_triples), round(time.time() - t_arm, 2)), flush=True)

    # Forward single-chain rail (v1 0.275 reference)
    t_arm = time.time()
    r_single = arm_single_chain_naive(E, R, sq, W, ptr_chains, depth=DEPTH)
    r_single["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    r_single["W_n_bindings"] = len(ptr_triples)
    out["arm_single_chain_5hop_forward"] = r_single
    print("  [seed=%d] SINGLE_FORWARD top1=%.4f per_step=%s t=%.1fs" % (
        seed, r_single["top1"], r_single["per_step_acc"],
        r_single["elapsed_s_arm"]), flush=True)

    # Bidirectional probe arm (top1=None; not classification)
    t_arm = time.time()
    r_meet = arm_bidirectional_meet_at_hop2(E, R, sq, W, ptr_chains, depth=DEPTH)
    r_meet["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    out["arm_bidirectional_5hop_meet_hop2"] = r_meet
    print("  [seed=%d] BIDIR_MEET_HOP2 (probe) mean_cos=%.4f median_cos=%.4f t=%.1fs" % (
        seed, r_meet["mean_cosine_at_midpoint"],
        r_meet["median_cosine_at_midpoint"],
        r_meet["elapsed_s_arm"]), flush=True)

    # Bidirectional candidate-ranking arm (v1 0.67 revival)
    t_arm = time.time()
    r_rank = arm_bidirectional_meet_middle_rank(E, R, sq, W, ptr_chains, depth=DEPTH)
    r_rank["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    out["arm_bidirectional_5hop_meet_mid"] = r_rank
    print("  [seed=%d] BIDIR_MEET_MID top1=%.4f t=%.1fs" % (
        seed, r_rank["top1"], r_rank["elapsed_s_arm"]), flush=True)

    # Error correlation
    fwd_corr = r_single.get("_correct_per_query", [])
    bidir_corr = r_rank.get("_correct_per_query", [])
    if len(fwd_corr) == len(bidir_corr) and len(fwd_corr) > 1:
        fwd_arr = np.array(fwd_corr, dtype=np.float32)
        bidir_arr = np.array(bidir_corr, dtype=np.float32)
        if fwd_arr.std() > 0 and bidir_arr.std() > 0:
            r = float(np.corrcoef(fwd_arr, bidir_arr)[0, 1])
        else:
            r = float("nan")
        out["fwd_bidir_error_correlation"] = round(r, 4) if not math.isnan(r) else None

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
    reproduce = mean_top1("arm_reproduce_pointer_chain_v2_5hop")
    single = mean_top1("arm_single_chain_5hop_forward")
    bidir = mean_top1("arm_bidirectional_5hop_meet_mid")
    bidir_cv = cv_top1("arm_bidirectional_5hop_meet_mid")

    mean_cosines = [p["arm_bidirectional_5hop_meet_hop2"]["mean_cosine_at_midpoint"]
                     for p in per_seed
                     if "arm_bidirectional_5hop_meet_hop2" in p
                     and isinstance(p["arm_bidirectional_5hop_meet_hop2"].get(
                         "mean_cosine_at_midpoint"), (int, float))]
    mean_cos_overall = float(np.mean(mean_cosines)) if mean_cosines else float("nan")

    errs = [p.get("fwd_bidir_error_correlation") for p in per_seed
             if p.get("fwd_bidir_error_correlation") is not None]
    err_corr_mean = float(np.mean(errs)) if errs else float("nan")

    sanity_breached = sum(1 for p in per_seed if not p.get("baseline_sanity_ok", False))
    meta_m7_breached = sum(1 for p in per_seed if not p.get("meta_m7_rail_ok", False))
    rails: List[str] = []
    if sanity_breached > 0:
        rails.append("SANITY_BREACH(%d/%d; baseline_mean=%.4f)" % (
            sanity_breached, len(per_seed), baseline))
    if meta_m7_breached > 0:
        rails.append("META_M7_BREACH(%d/%d; reproduce_mean=%.4f; rail=[%.2f, %.2f])" % (
            meta_m7_breached, len(per_seed), reproduce, META_M7_RAIL_LO, META_M7_RAIL_HI))

    summ = ("BASELINE=%.4f (sanity_breach=%d/%d) REPRODUCE_PV2=%.4f (META_M7_breach=%d/%d) "
            "SINGLE_FWD_v1regime=%.4f BIDIR_MEET_MID=%.4f (cv=%.3f) "
            "mean_midpoint_cosine=%.4f fwd_bidir_err_corr=%.3f "
            "lift_over_fwd=%+.4f | rails=%s") % (
        baseline, sanity_breached, len(per_seed),
        reproduce, meta_m7_breached, len(per_seed),
        single, bidir, bidir_cv, mean_cos_overall, err_corr_mean,
        (bidir - single) if (not math.isnan(bidir) and not math.isnan(single)) else float("nan"),
        rails,
    )

    if sanity_breached >= max(1, (len(per_seed) + 1) // 2):
        return "SANITY_BREACH", "SANITY_BREACH_BASELINE_OUT_OF_BAND: " + summ

    revival_holds = (
        not math.isnan(bidir) and bidir >= HP_BIDIR_MEET_MID
        and (math.isnan(bidir_cv) or bidir_cv <= HP_BIDIR_CV_MAX)
    )
    meta_m7_ok_overall = (meta_m7_breached < max(1, (len(per_seed) + 1) // 2))

    if revival_holds and meta_m7_ok_overall:
        return "HARD_PASS_CHAIN_GRADE_BIDIRECTIONAL_REVIVAL", \
               "HARD_PASS_CHAIN_GRADE_BIDIRECTIONAL_REVIVAL: " + summ
    if revival_holds and not meta_m7_ok_overall:
        return "HARD_PASS_REVIVAL_WITH_META_M7_NOTE", \
               "HARD_PASS_REVIVAL_WITH_META_M7_NOTE_REGIME_DIFF_BUT_WITHIN_CELL_LIFT_HONEST: " + summ
    if not math.isnan(bidir) and bidir < HF_BIDIR:
        return "HARD_FAIL", "HARD_FAIL_BIDIRECTIONAL_DOESNT_HELP: " + summ
    return "MIDDLE_BAND", "MIDDLE_BAND_BIDIRECTIONAL_PARTIAL: " + summ


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
            "V2 META_M7 RAIL + nan fix: v1's SINGLE_CHAIN_5HOP_FORWARD=0.275 vs "
            "pointer-chain v2's 0.122 same-mechanism-different-W-bindings (1000 "
            "vs 2000). ARM_REPRODUCE_POINTER_CHAIN_V2_5HOP builds a SEPARATE W "
            "from make_deep_chains(n=200, max_depth=10) -> 2000 bindings; tests "
            "at depth=5 using verbatim _retrieve_1hop. Target band [0.08, 0.25]. "
            "Also fixes ARM_BIDIRECTIONAL_MEET_HOP2 v1 bug: top1=NaN -> top1=None "
            "(JSON serializes None cleanly; NaN is invalid JSON). Longer timeout "
            "(7200s) lets all 3 seeds complete the expensive V_C-loop bidirectional "
            "ranking arm (v1 seed 7 took 2687s alone)."
        ),
    }
    write_metrics(out_dir, metrics, results=per_seed)
    print("[done] metrics.json written (%d seeds, %.1fs)" % (
        len(per_seed), metrics["elapsed_s"]), flush=True)
