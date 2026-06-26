"""substrate_multihop_bidirectional_meet_middle_v1.

REVIVAL ANGLE 3 (Research 2026-06-25 drill) -- bidirectional meet-in-middle.

Background:
  Pointer-chain v2 per-step accuracy [0.69, 0.485, 0.31, 0.205, 0.145] at hops
  1-5 reflects compounding error. A 5-hop chain forward-only gives 0.145 top1.
  Halving the effective chain depth via meet-in-middle (forward 2-3 hops; backward
  2-3 hops; match at midpoint) lets each half compound only 2-3x instead of 5x.

Mechanism (this cell):
  Substrate has chain-grade unbind primitive (hdlab/binding.py:30). For each
  multi-hop query (S, [p_1, ..., p_5], answer_candidate Z):
    Forward chain: state_fwd = E[S]; for i in 0..mid-1: state_fwd = W @ (state_fwd * R[p_i] * sq)
    Backward chain: state_bwd = E[Z]; for i in n-1 down to mid: state_bwd = W.T @ (state_bwd) * INV(R[p_i]) * sq
      (using HRR involutive unbind property: bipolar R is its own inverse since R*R=1 elementwise)
  Match at midpoint: cosine(state_fwd, state_bwd_target_midpoint). Accept if
  argmax over candidates Z gives the true Z.

  For bipolar HRR with elementwise mul: bind(a, b) = a * b; unbind(c, b) = c * b
  since b * b = 1 elementwise. So forward W @ (E[s] * R[p] * sq) -> retrieves
  o; reverse: W.T @ E[o] -> retrieves (E[s] * R[p] * sq), then multiply by R[p]
  and divide by sq to get noisy E[s].

ARMS (4):
  ARM_BASELINE_HRR_2HOP        beta-sweep sanity rail [0.62, 0.68]
  ARM_SINGLE_CHAIN_5HOP_FORWARD  pointer-chain v2 monolithic 5hop (rail)
  ARM_BIDIRECTIONAL_5HOP_MEET_HOP2  forward 2 hops; backward 3 hops; meet at hop 2
  ARM_BIDIRECTIONAL_5HOP_MEET_MID  forward floor(5/2)=2 hops; backward 3 hops;
                                    rank V_C candidates by meet-cosine; top1 argmax

PROSPECTIVE BANDS (locked):
  HARD_PASS_CHAIN_GRADE_BIDIRECTIONAL:
    BIDIRECTIONAL_MEET_MID top1 >= 0.50 AND cv <= 0.07
  HARD_PASS_PARTIAL:
    BIDIRECTIONAL_MEET_MID top1 >= 0.25
  HARD_FAIL_BIDIRECTIONAL_DOESNT_HELP:
    BIDIRECTIONAL_MEET_MID top1 < 0.15

ALSO: report error-correlation between forward-error and backward-error across
seeds; if r > 0.5, meet-in-middle has limited additional info beyond forward.

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

ANCHOR_NAME = "substrate_multihop_bidirectional_meet_middle_v1"
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
HP_BIDIR_MEET_MID = 0.50
HP_BIDIR_CV_MAX = 0.07
HP_BIDIR_PARTIAL = 0.25
HF_BIDIR = 0.15

# SACRED SANITY
BASELINE_SANITY_LO = 0.62
BASELINE_SANITY_HI = 0.68

BASELINE_V_P = 2
BASELINE_N_CHAINS = 200
POINTER_V_P = 10
POINTER_K_SET = 20

# Lock bands
assert HP_BIDIR_MEET_MID > HP_BIDIR_PARTIAL > HF_BIDIR
assert 0.0 < HP_BIDIR_CV_MAX < 0.20

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

CONFIG_VERSION = (
    "bidirectionalMeetMiddleV1: N=%d V_C=%d "
    "BASELINE_V_P=%d BASELINE_N=%d POINTER_V_P=%d POINTER_N=%d K_SET=%d "
    "seeds=%s mode=%s depth=%d midhop=%d "
    "HP_meetmid>=%.2f HP_cv<=%.2f HP_partial>=%.2f HF<%.2f "
    "baseline_sanity=[%.2f,%.2f]"
) % (
    N_DIM, V_CONCEPTS, BASELINE_V_P, BASELINE_N_CHAINS_LOCAL,
    POINTER_V_P, POINTER_N_CHAINS, POINTER_K_SET,
    SEEDS, RUN_MODE, DEPTH, DEPTH // 2,
    HP_BIDIR_MEET_MID, HP_BIDIR_CV_MAX, HP_BIDIR_PARTIAL, HF_BIDIR,
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
    key = (E[s] * R[p] * sq).astype(np.float32)
    return int((E @ (W @ key)).argmax())


def arm_single_chain_naive(E, R, sq, W, chains_test, depth):
    """Forward-only monolithic chain (rail match for pointer-chain v2)."""
    n = len(chains_test)
    hits = 0
    per_step_hits = np.zeros(depth, dtype=np.int64)
    fwd_correct_per_query = []  # for error-correlation computation
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
    """Walk forward from E[start_idx] through predicates, NO cleanup (noisy state)."""
    state = E[start_idx].copy()
    for p in predicates:
        state = W @ (state * R[p] * sq)
    return state


def _backward_state(E, W, R, sq, end_idx: int, predicates: List[int]) -> np.ndarray:
    """Walk backward from E[end_idx] through predicates in REVERSE order.

    Substrate W is built via W += outer(E[o], E[s] * R[p] * sq) / n_dim.
    Forward: W @ key recovers (approximately) E[o] where key = E[s] * R[p] * sq.
    Reverse: W.T @ E[o] recovers (approximately) E[s] * R[p] * sq.
    So to recover E[s] from E[o]: state_intermediate = W.T @ E[o]; then
    state_s_noisy = state_intermediate * R[p] * sq (since bipolar R is its
    own multiplicative inverse: R * R = 1 elementwise; and sq * sq = n_dim
    which is absorbed into the normalisation).

    For multi-hop backward: end -> ... -> midpoint. predicates is in CHAIN
    order (predicates[0] is hop 0, the LAST predicate we unbind from end).
    The reverse iteration unbinds from end_idx backward:
      state = E[end_idx]
      for i in reversed(range(len(predicates))):
          state = W.T @ state              # recovers (E[s_i] * R[p_i] * sq)
          state = state * R[p_i] * sq      # unbind R[p_i] -> E[s_i] noisy
    """
    state = E[end_idx].copy()
    for i in range(len(predicates) - 1, -1, -1):
        p = predicates[i]
        state = W.T @ state
        state = state * R[p] * sq
    return state


def arm_bidirectional_meet_at_hop2(E, R, sq, W, chains_test, depth) -> Dict[str, Any]:
    """Forward 2 hops from S; backward 3 hops from Z (TRUE end). Cosine-match
    forward_state to backward_state at midpoint = hop 2.

    For this arm, Z = chain[depth-1][2] is provided (the ground-truth answer).
    The arm tests whether the meet-in-middle COSINE itself is high when chain
    is followed correctly. NOT a candidate-ranking arm; this is the "does
    bidirectional state-similarity work at all" arm.
    """
    n = len(chains_test)
    cos_correct_chain = []  # cosine when Z is correct end
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
    return {"top1": float("nan"),  # not a classification arm
            "mean_cosine_at_midpoint": round(mean_cos, 4),
            "median_cosine_at_midpoint": round(median_cos, 4),
            "n_queries": n, "depth": depth,
            "mechanism": "bidirectional_state_cosine_no_ranking"}


def arm_bidirectional_meet_middle_rank(E, R, sq, W, chains_test, depth) -> Dict[str, Any]:
    """Meet-in-middle candidate ranking.

    For each query (S, predicate-chain, true_Z): walk forward MID hops to
    state_fwd. For each candidate Z in V_C, walk backward (DEPTH-MID) hops
    from E[Z] to state_bwd_Z. Rank candidates by cosine(state_fwd, state_bwd_Z);
    top1 = argmax.
    """
    n = len(chains_test)
    V = E.shape[0]
    mid = depth // 2
    hits = 0
    per_step_hits = np.zeros(depth, dtype=np.int64)  # legacy placeholder
    bidir_correct_per_query = []
    for chain in chains_test:
        S = chain[0][0]
        preds = [chain[i][1] for i in range(depth)]
        true_Z = chain[depth - 1][2]
        # Forward MID hops (no cleanup; raw state)
        state_fwd = _forward_state(E, W, R, sq, S, preds[:mid])
        fnorm = np.linalg.norm(state_fwd) + 1e-8
        # Backward (depth - mid) hops from each candidate Z
        # Batched: build all candidate backward-states then cosine
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

    triples_d, chains_d = make_deep_chains(8, V, 4, max_depth=5, g=g, disallow_s=set())
    W = ingest_hebbian(triples_d, E, R, sq, n)
    r_single = arm_single_chain_naive(E, R, sq, W, chains_d, depth=5)
    assert 0.0 <= r_single["top1"] <= 1.0

    # Bidirectional check
    r_meet = arm_bidirectional_meet_at_hop2(E, R, sq, W, chains_d, depth=5)
    assert -1.0 <= r_meet["mean_cosine_at_midpoint"] <= 1.0
    r_rank = arm_bidirectional_meet_middle_rank(E, R, sq, W, chains_d, depth=5)
    assert 0.0 <= r_rank["top1"] <= 1.0
    assert r_rank["midpoint_hop"] == 2

    # Critical: verify backward-walk math is correct. For a 1-hop chain where
    # forward retrieves correctly, backward from the answer should retrieve
    # something close to the start. We test on a CLEAN chain with no W crosstalk:
    g2 = np.random.default_rng(1)
    E1 = bipolar(V, n, g2)
    R1 = bipolar(4, n, g2)
    triple_1hop = [(0, 0, 1)]
    W1 = ingest_hebbian(triple_1hop, E1, R1, sq, n)
    # Forward: W1 @ (E1[0] * R1[0] * sq) should give E1[1] approx
    fwd_state = W1 @ (E1[0] * R1[0] * sq)
    fwd_cos = float(np.dot(fwd_state, E1[1]) / (np.linalg.norm(fwd_state) * np.linalg.norm(E1[1]) + 1e-8))
    # Backward: W1.T @ E1[1] gives (E1[0] * R1[0] * sq); times R1[0] * sq gives E1[0] noisy
    bwd_state = (W1.T @ E1[1]) * R1[0] * sq
    bwd_cos = float(np.dot(bwd_state, E1[0]) / (np.linalg.norm(bwd_state) * np.linalg.norm(E1[0]) + 1e-8))
    # On a single-triple W, both should be reasonably positive (>0.2)
    assert fwd_cos > 0.2, "selftest forward-cos=%.3f too low" % fwd_cos
    assert bwd_cos > 0.2, "selftest backward-cos=%.3f too low" % bwd_cos

    print("[selftest] PASS base=%.3f single=%.3f meet_mean_cos=%.3f rank_top1=%.3f "
          "fwd_cos=%.3f bwd_cos=%.3f"
          % (r_base["top1"], r_single["top1"], r_meet["mean_cosine_at_midpoint"],
             r_rank["top1"], fwd_cos, bwd_cos), flush=True)


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
        "pointer_n_chains": POINTER_N_CHAINS, "depth": DEPTH,
        "midpoint_hop": DEPTH // 2,
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
    out["baseline_sanity_ok"] = (BASELINE_SANITY_LO <= r_baseline["top1"] <= BASELINE_SANITY_HI)

    # POINTER chains
    t_arm = time.time()
    ptr_triples, ptr_chains = make_deep_chains(
        POINTER_N_CHAINS, V_CONCEPTS, POINTER_V_P, max_depth=DEPTH,
        g=g, disallow_s=set())
    W = ingest_hebbian(ptr_triples, E, R, sq, N_DIM)
    print("  [seed=%d] pointer W built (%d triples) t=%.1fs" % (
        seed, len(ptr_triples), round(time.time() - t_arm, 2)), flush=True)

    # Forward single-chain rail
    t_arm = time.time()
    r_single = arm_single_chain_naive(E, R, sq, W, ptr_chains, depth=DEPTH)
    r_single["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    out["arm_single_chain_5hop_forward"] = r_single
    print("  [seed=%d] SINGLE_FORWARD top1=%.4f per_step=%s t=%.1fs" % (
        seed, r_single["top1"], r_single["per_step_acc"],
        r_single["elapsed_s_arm"]), flush=True)

    # Bidirectional state-cosine probe (no ranking)
    t_arm = time.time()
    r_meet = arm_bidirectional_meet_at_hop2(E, R, sq, W, ptr_chains, depth=DEPTH)
    r_meet["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    out["arm_bidirectional_5hop_meet_hop2"] = r_meet
    print("  [seed=%d] BIDIR_MEET_HOP2 mean_cos=%.4f median_cos=%.4f t=%.1fs" % (
        seed, r_meet["mean_cosine_at_midpoint"],
        r_meet["median_cosine_at_midpoint"],
        r_meet["elapsed_s_arm"]), flush=True)

    # Bidirectional candidate-ranking arm (top1)
    t_arm = time.time()
    r_rank = arm_bidirectional_meet_middle_rank(E, R, sq, W, ptr_chains, depth=DEPTH)
    r_rank["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    out["arm_bidirectional_5hop_meet_mid"] = r_rank
    print("  [seed=%d] BIDIR_MEET_MID top1=%.4f t=%.1fs" % (
        seed, r_rank["top1"], r_rank["elapsed_s_arm"]), flush=True)

    # Error correlation between forward and bidirectional
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
    single = mean_top1("arm_single_chain_5hop_forward")
    bidir = mean_top1("arm_bidirectional_5hop_meet_mid")
    bidir_cv = cv_top1("arm_bidirectional_5hop_meet_mid")

    # Mean cosine probe
    mean_cosines = [p["arm_bidirectional_5hop_meet_hop2"]["mean_cosine_at_midpoint"]
                     for p in per_seed
                     if "arm_bidirectional_5hop_meet_hop2" in p]
    mean_cos_overall = float(np.mean(mean_cosines)) if mean_cosines else float("nan")

    # Error correlation across seeds
    errs = [p.get("fwd_bidir_error_correlation") for p in per_seed
             if p.get("fwd_bidir_error_correlation") is not None]
    err_corr_mean = float(np.mean(errs)) if errs else float("nan")

    sanity_breached = sum(1 for p in per_seed if not p.get("baseline_sanity_ok", False))
    rails: List[str] = []
    if sanity_breached > 0:
        rails.append("SANITY_BREACH(%d/%d seeds; baseline_mean=%.4f)" % (
            sanity_breached, len(per_seed), baseline))

    summ = ("BASELINE=%.4f (sanity_breach=%d/%d) "
            "SINGLE_FWD=%.4f BIDIR_MEET_MID=%.4f (cv=%.3f) "
            "mean_midpoint_cosine=%.4f fwd_bidir_err_corr=%.3f "
            "lift_over_fwd=%+.4f | rails=%s") % (
        baseline, sanity_breached, len(per_seed),
        single, bidir, bidir_cv, mean_cos_overall, err_corr_mean,
        (bidir - single) if (not math.isnan(bidir) and not math.isnan(single)) else float("nan"),
        rails,
    )

    if sanity_breached >= max(1, (len(per_seed) + 1) // 2):
        return "SANITY_BREACH", "SANITY_BREACH_BASELINE_OUT_OF_BAND: " + summ

    hp_chain_grade = (
        not math.isnan(bidir) and bidir >= HP_BIDIR_MEET_MID
        and (math.isnan(bidir_cv) or bidir_cv <= HP_BIDIR_CV_MAX)
    )
    if hp_chain_grade:
        return "HARD_PASS_CHAIN_GRADE_BIDIRECTIONAL", \
               "HARD_PASS_CHAIN_GRADE_BIDIRECTIONAL: " + summ
    if not math.isnan(bidir) and bidir >= HP_BIDIR_PARTIAL:
        return "HARD_PASS_PARTIAL", "HARD_PASS_PARTIAL_BIDIRECTIONAL_LIFT: " + summ
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
            "ANGLE 3 revival: bidirectional meet-in-middle. Substrate unbind "
            "primitive (hdlab/binding.py:30) supports walking chain in reverse: "
            "given the answer Z, unbind via W.T then R[p] (bipolar HRR R is "
            "involutive) to recover the predecessor. Forward MID hops; "
            "backward (depth-MID) hops from each V_C candidate; rank candidates "
            "by midpoint state-cosine. Mean-cosine probe arm (no ranking) "
            "verifies whether forward and backward states actually CONVERGE "
            "on correct chains. Error-correlation between fwd-only and "
            "bidirectional surfaces whether bidirectional gives INDEPENDENT "
            "signal (low correlation = high info gain)."
        ),
    }
    write_metrics(out_dir, metrics, results=per_seed)
    print("[done] metrics.json written (%d seeds, %.1fs)" % (
        len(per_seed), metrics["elapsed_s"]), flush=True)
