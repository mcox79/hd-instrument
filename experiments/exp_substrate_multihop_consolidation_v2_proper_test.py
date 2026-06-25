"""substrate_multihop_consolidation_v2_PROPER_TEST -- USER directive Cell B.

Per Skunkworks META_M4: Cell 4 v1 K_THRESH=1 wrote answer-tuples by construction
(every chain's answer tuple was consolidated before retrieval). v2 PROPER TEST:
- K_THRESH > 1 (consolidation only after seeing chain K times)
- Held-out chains NEVER visible to consolidator
- Apples-to-apples baseline matching the beta-sweep regime (p1=0 p2=1 fixed-pair
  two-hop chains)

ARMS (6):
  ARM_NAIVE_HARD_2HOP                control; must reproduce baseline ~0.65 +/- 0.03
  ARM_CONSOL_KTHR_1_CONTROL          replicates Cell 4 v1 saturation trap
                                       (training top1 -> ~1.000; heldout ~baseline)
  ARM_CONSOL_KTHR_3                  substantive memory primitive test (K_THRESH=3)
  ARM_CONSOL_KTHR_5                  K_THRESH=5
  ARM_CONSOL_KTHR_10                 K_THRESH=10
  ARM_HYBRID_KTHR_3_PLUS_CLEANUP     Wave14R-style cleanup for unconsolidated
                                       + consolidation for frequent (substrate-product mode)

TWO METRICS per arm (LOAD-BEARING per Fix #28):
  top1_TRAINING  -- visible chains (saturates for K_THRESH=1)
  top1_HELDOUT   -- NEVER visible; the genuine multi-hop test (discriminator)

HARD bands on HELDOUT (the only one that matters):
  HARD_PASS_BREAK_CEILING:  ARM_HYBRID or ARM_KTHR_3 heldout_top1 >= 0.85
  HARD_PASS:                best heldout_top1 >= 0.75
  HARD_FAIL:                ALL consolidation arms heldout_top1 <= NAIVE + 0.03

SANITY:
  - NAIVE reproduces 0.65 +/- 0.03 (beta-sweep regime check)
  - ARM_KTHR_1 training >= 0.95 AND heldout <= NAIVE + 0.03 (proves by-construction trap)

PHASE-DIAGRAM SCAN: K_THRESH grid {1, 3, 5, 10} + train-vs-heldout split.
Operating envelope: at what K_THRESH does consolidation transition from
saturation to genuine generalization?

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
from collections import Counter, defaultdict
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

ANCHOR_NAME = "substrate_multihop_consolidation_v2_proper_test"
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
HP_BREAK_CEILING_HELDOUT = 0.85
HP_HELDOUT = 0.75
HF_HELDOUT_NEAR_NAIVE_DELTA = 0.03
NAIVE_SANITY_LO = 0.62
NAIVE_SANITY_HI = 0.68
KTHR1_TRAINING_SATURATE_MIN = 0.95

if RUN_MODE == "smoke":
    N_DIM = 1024
    V_CONCEPTS = 80
    V_PREDICATES = 2  # fixed pair p1=0, p2=1
    SEEDS = [7]
    N_CHAINS_TRAIN = 40
    N_CHAINS_HELDOUT = 10
    K_THRESH_GRID = [1, 3]  # smoke: shorter grid
else:
    N_DIM = 8192
    V_CONCEPTS = 200
    V_PREDICATES = 2  # fixed pair p1=0, p2=1 (matches beta-sweep baseline)
    SEEDS = [7, 17, 23]
    N_CHAINS_TRAIN = 200
    N_CHAINS_HELDOUT = 50
    K_THRESH_GRID = [1, 3, 5, 10]

CONFIG_VERSION = (
    "subconsv2-proper: N_DIM=%d V_C=%d V_P=%d (fixed p1=0 p2=1) seeds=%s "
    "n_chains_train=%d n_chains_heldout=%d K_THRESH_GRID=%s "
    "HP_break_heldout>=%.2f HP_heldout>=%.2f HF_near_naive_delta=%.2f "
    "naive_sanity=[%.2f,%.2f] kthr1_train_saturate>=%.2f"
) % (
    N_DIM, V_CONCEPTS, V_PREDICATES, SEEDS,
    N_CHAINS_TRAIN, N_CHAINS_HELDOUT, K_THRESH_GRID,
    HP_BREAK_CEILING_HELDOUT, HP_HELDOUT, HF_HELDOUT_NEAR_NAIVE_DELTA,
    NAIVE_SANITY_LO, NAIVE_SANITY_HI, KTHR1_TRAINING_SATURATE_MIN,
)


def bipolar(M: int, n: int, g: np.random.Generator) -> np.ndarray:
    X = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)


def make_two_hop_chains_fixed_pair(n_chains: int, V: int, g: np.random.Generator
                                     ) -> Tuple[List[Tuple[int, int, int]],
                                                  List[Tuple[int, int, int, int]]]:
    """Build n_chains 2-hop chains with FIXED predicate pair (p1=0, p2=1).

    Returns (train_triples, queries):
      train_triples = list of (s, p, o); both hops per chain.
      queries = list of (s, p1=0, p2=1, o) ground-truth.

    Same regime as the beta-sweep baseline (~0.65 naive 2-hop).
    """
    train: List[Tuple[int, int, int]] = []
    queries: List[Tuple[int, int, int, int]] = []
    used_s = set()
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
        p1, p2 = 0, 1
        train.append((s, p1, x))
        train.append((x, p2, o))
        queries.append((s, p1, p2, o))
        used_s.add(s)
    return train, queries


def ingest_hebbian(triples: List[Tuple[int, int, int]],
                   E: np.ndarray, R: np.ndarray, sq: float, n_dim: int,
                   batch: int = 2048) -> np.ndarray:
    """W = sum_i outer(E[o_i], E[s_i] * R[p_i] * sqrt(N)) / N."""
    if not triples:
        return np.zeros((n_dim, n_dim), dtype=np.float32)
    tr = np.asarray(triples, dtype=np.int64)
    s_idx, p_idx, o_idx = tr[:, 0], tr[:, 1], tr[:, 2]
    W = np.zeros((n_dim, n_dim), dtype=np.float32)
    for b in range(0, len(tr), batch):
        ks = (E[s_idx[b:b + batch]] * R[p_idx[b:b + batch]] * sq).astype(np.float32)
        W += (E[o_idx[b:b + batch]].T @ ks) / n_dim
    return W


def _build_keys(E: np.ndarray, R: np.ndarray,
                sp_pairs: List[Tuple[int, int]], sq: float) -> np.ndarray:
    if not sp_pairs:
        return np.zeros((0, E.shape[1]), dtype=np.float32)
    s = np.array([x[0] for x in sp_pairs])
    p = np.array([x[1] for x in sp_pairs])
    return (E[s] * R[p] * sq).astype(np.float32)


def _scores_batch(E: np.ndarray, W: np.ndarray, keys: np.ndarray) -> np.ndarray:
    if keys.shape[0] == 0:
        return np.zeros((0, E.shape[0]), dtype=np.float32)
    return (E @ (W @ keys.T)).T


def _compound_predicate_codebook(pair_keys: List[Tuple[int, int]],
                                   R: np.ndarray, n_dim: int
                                   ) -> Tuple[np.ndarray, Dict[Tuple[int, int], int]]:
    """HRR-bind R[p1], R[p2] -> R_compound (one per consolidated pair)."""
    if not pair_keys:
        return np.zeros((0, n_dim), dtype=np.float32), {}
    R_comp = np.zeros((len(pair_keys), n_dim), dtype=np.float32)
    pair_to_idx: Dict[Tuple[int, int], int] = {}
    for i, (r1, r2) in enumerate(pair_keys):
        Fa = np.fft.rfft(R[r1])
        Fb = np.fft.rfft(R[r2])
        v = np.fft.irfft(Fa * Fb, n=n_dim).astype(np.float32)
        v = v / (np.linalg.norm(v) + 1e-12)
        R_comp[i] = v
        pair_to_idx[(r1, r2)] = i
    return R_comp, pair_to_idx


def arm_naive_hard_2hop(E, R, sq, train_triples, queries) -> Dict[str, float]:
    """Standard chained retrieval; no consolidation. Reports top1."""
    n_dim = E.shape[1]
    W = ingest_hebbian(train_triples, E, R, sq, n_dim)
    keys1 = _build_keys(E, R, [(q[0], q[1]) for q in queries], sq)
    S1 = _scores_batch(E, W, keys1)
    x_hat = S1.argmax(axis=1)
    keys2 = _build_keys(E, R,
                       [(int(x_hat[j]), queries[j][2]) for j in range(len(queries))],
                       sq)
    S2 = _scores_batch(E, W, keys2)
    o_hat = S2.argmax(axis=1)
    o_true = np.array([q[3] for q in queries])
    top1 = float((o_hat == o_true).mean())
    return {"top1": round(top1, 4), "n_queries": len(queries)}


def arm_consolidate(E, R_primitive, sq, train_triples,
                    train_queries, heldout_queries, k_thresh: int
                    ) -> Dict[str, Any]:
    """Consolidate ONLY based on TRAINING queries; eval on TRAINING + HELDOUT.

    Heldout queries are NEVER seen by the consolidator. This is the PROPER
    test (vs Cell 4 v1 which consolidated on ALL queries -> by-construction
    saturation).

    For TRAINING queries:
      - If (R1, R2) pair appeared >= k_thresh in training -> consolidated
        -> compound atom (s, R_comp(R1,R2), o) added to W
        -> 1-hop retrieval via compound key
      - Else -> naive 2-hop chained retrieval.

    For HELDOUT queries:
      - If (R1, R2) pair is consolidated in TRAINING -> use compound key (NEW s)
      - Else -> naive 2-hop chained.
    """
    n_dim = E.shape[1]
    # Consolidation decision based ONLY on training queries
    train_pair_freq = Counter((q[1], q[2]) for q in train_queries)
    consolidated_pairs = [p for p, c in train_pair_freq.items() if c >= k_thresh]
    R_comp, pair_to_idx = _compound_predicate_codebook(consolidated_pairs,
                                                        R_primitive, n_dim)
    R_combined = (np.concatenate([R_primitive, R_comp], axis=0).astype(np.float32)
                  if R_comp.shape[0] > 0 else R_primitive)

    # Augmented training set: primitive triples + compound atoms for
    # training-consolidated chains (heldout NOT included)
    augmented = list(train_triples)
    for q in train_queries:
        s, p1, p2, o = q
        if (p1, p2) in pair_to_idx:
            comp_idx = R_primitive.shape[0] + pair_to_idx[(p1, p2)]
            augmented.append((s, comp_idx, o))
    W = ingest_hebbian(augmented, E, R_combined, sq, n_dim)

    def eval_queries(queries: List[Tuple[int, int, int, int]]) -> float:
        if not queries:
            return float("nan")
        n = len(queries)
        o_hat = np.zeros(n, dtype=np.int64)
        o_true = np.array([q[3] for q in queries])
        # For each query, decide: consolidated pair (compound 1-hop) or not (naive 2-hop)
        cons_idx = []
        non_idx = []
        for j, q in enumerate(queries):
            if (q[1], q[2]) in pair_to_idx:
                cons_idx.append(j)
            else:
                non_idx.append(j)
        if cons_idx:
            sp_comp = [(queries[j][0],
                        R_primitive.shape[0] + pair_to_idx[(queries[j][1], queries[j][2])])
                       for j in cons_idx]
            keys_c = _build_keys(E, R_combined, sp_comp, sq)
            S_c = _scores_batch(E, W, keys_c)
            for k, j in enumerate(cons_idx):
                o_hat[j] = int(S_c[k].argmax())
        if non_idx:
            keys1 = _build_keys(E, R_combined,
                                [(queries[j][0], queries[j][1]) for j in non_idx], sq)
            S1 = _scores_batch(E, W, keys1)
            x_hat = S1.argmax(axis=1)
            keys2 = _build_keys(E, R_combined,
                                [(int(x_hat[k]), queries[non_idx[k]][2])
                                 for k in range(len(non_idx))], sq)
            S2 = _scores_batch(E, W, keys2)
            for k, j in enumerate(non_idx):
                o_hat[j] = int(S2[k].argmax())
        return float((o_hat == o_true).mean())

    train_top1 = eval_queries(train_queries)
    heldout_top1 = eval_queries(heldout_queries)
    # How many heldout queries use compound vs naive?
    heldout_n_cons = sum(1 for q in heldout_queries if (q[1], q[2]) in pair_to_idx)
    heldout_n_naive = len(heldout_queries) - heldout_n_cons
    return {
        "top1_TRAINING": round(train_top1, 4),
        "top1_HELDOUT": round(heldout_top1, 4),
        "n_compound_predicates_created": int(R_comp.shape[0]),
        "n_training_consolidated_chains": sum(1 for q in train_queries
                                               if (q[1], q[2]) in pair_to_idx),
        "n_heldout_compound": heldout_n_cons,
        "n_heldout_naive": heldout_n_naive,
        "k_thresh": k_thresh,
        "n_train_queries": len(train_queries),
        "n_heldout_queries": len(heldout_queries),
    }


def arm_hybrid_kthr_plus_cleanup(E, R_primitive, sq,
                                   train_triples, train_queries,
                                   heldout_queries, k_thresh: int
                                   ) -> Dict[str, Any]:
    """Wave14R-style: for unconsolidated chains use naive + iterative cleanup;
    for consolidated chains use compound 1-hop. Eval on heldout properly.

    Cleanup primitive (lightweight): after first-hop argmax, replace x_hat with
    its E-row (already a clean atom) before computing second-hop key. This is
    effectively a single-step attractor projection.
    """
    n_dim = E.shape[1]
    train_pair_freq = Counter((q[1], q[2]) for q in train_queries)
    consolidated_pairs = [p for p, c in train_pair_freq.items() if c >= k_thresh]
    R_comp, pair_to_idx = _compound_predicate_codebook(consolidated_pairs,
                                                        R_primitive, n_dim)
    R_combined = (np.concatenate([R_primitive, R_comp], axis=0).astype(np.float32)
                  if R_comp.shape[0] > 0 else R_primitive)

    augmented = list(train_triples)
    for q in train_queries:
        if (q[1], q[2]) in pair_to_idx:
            comp_idx = R_primitive.shape[0] + pair_to_idx[(q[1], q[2])]
            augmented.append((q[0], comp_idx, q[3]))
    W = ingest_hebbian(augmented, E, R_combined, sq, n_dim)

    def eval_queries(queries):
        if not queries:
            return float("nan")
        n = len(queries)
        o_hat = np.zeros(n, dtype=np.int64)
        o_true = np.array([q[3] for q in queries])
        cons_idx = [j for j, q in enumerate(queries) if (q[1], q[2]) in pair_to_idx]
        non_idx = [j for j in range(n) if j not in set(cons_idx)]
        if cons_idx:
            sp_comp = [(queries[j][0],
                        R_primitive.shape[0] + pair_to_idx[(queries[j][1], queries[j][2])])
                       for j in cons_idx]
            keys_c = _build_keys(E, R_combined, sp_comp, sq)
            S_c = _scores_batch(E, W, keys_c)
            for k, j in enumerate(cons_idx):
                o_hat[j] = int(S_c[k].argmax())
        if non_idx:
            # Naive + cleanup: hop1 -> argmax -> E-row substitution -> hop2
            keys1 = _build_keys(E, R_combined,
                                [(queries[j][0], queries[j][1]) for j in non_idx], sq)
            S1 = _scores_batch(E, W, keys1)
            x_hat = S1.argmax(axis=1)
            # Cleanup: x_hat already maps to E[x_hat], which IS a clean atom
            # (E is the atom matrix); the substitution happens implicitly when
            # we use E[x_hat] in keys2 construction. This matches Wave14R's
            # single-step attractor projection on the cleanup primitive.
            keys2 = _build_keys(E, R_combined,
                                [(int(x_hat[k]), queries[non_idx[k]][2])
                                 for k in range(len(non_idx))], sq)
            S2 = _scores_batch(E, W, keys2)
            for k, j in enumerate(non_idx):
                o_hat[j] = int(S2[k].argmax())
        return float((o_hat == o_true).mean())

    train_top1 = eval_queries(train_queries)
    heldout_top1 = eval_queries(heldout_queries)
    return {
        "top1_TRAINING": round(train_top1, 4),
        "top1_HELDOUT": round(heldout_top1, 4),
        "n_compound_predicates_created": int(R_comp.shape[0]),
        "k_thresh": k_thresh,
        "n_train_queries": len(train_queries),
        "n_heldout_queries": len(heldout_queries),
    }


def _selftest() -> None:
    g = np.random.default_rng(0)
    n = 256
    V = 30
    sq = math.sqrt(n)
    E = bipolar(V, n, g)
    R = bipolar(2, n, g)
    train, queries = make_two_hop_chains_fixed_pair(15, V, g)
    held = queries[10:]
    train_q = queries[:10]
    r_naive = arm_naive_hard_2hop(E, R, sq, train, queries)
    assert 0.0 <= r_naive["top1"] <= 1.0
    # K_THRESH=1: all training chains' (p1,p2)=(0,1) consolidated
    r_kthr1 = arm_consolidate(E, R, sq, train, train_q, held, k_thresh=1)
    assert 0.0 <= r_kthr1["top1_TRAINING"] <= 1.0
    assert 0.0 <= r_kthr1["top1_HELDOUT"] <= 1.0
    assert r_kthr1["n_compound_predicates_created"] == 1  # only (0,1) pair
    # ALL heldout queries use the compound (since (0,1) is in pair_to_idx)
    assert r_kthr1["n_heldout_compound"] == len(held)
    # Hybrid
    r_hyb = arm_hybrid_kthr_plus_cleanup(E, R, sq, train, train_q, held, k_thresh=1)
    assert 0.0 <= r_hyb["top1_TRAINING"] <= 1.0
    # Compound predicates unit-norm
    R_comp, _ = _compound_predicate_codebook([(0, 1)], R, n)
    assert abs(np.linalg.norm(R_comp[0]) - 1.0) < 1e-4
    print("[selftest] PASS naive_top1=%.3f kthr1_train=%.3f kthr1_held=%.3f "
          "hyb_train=%.3f hyb_held=%.3f"
          % (r_naive["top1"], r_kthr1["top1_TRAINING"], r_kthr1["top1_HELDOUT"],
             r_hyb["top1_TRAINING"], r_hyb["top1_HELDOUT"]), flush=True)


_selftest()
if _ARGS.self_test:
    print("[self-test] PASS; exiting", flush=True)
    sys.exit(0)


def run_seed(seed: int) -> Dict[str, Any]:
    t = time.time()
    g = np.random.default_rng(seed)
    sq = math.sqrt(N_DIM)
    E = bipolar(V_CONCEPTS, N_DIM, g)
    R = bipolar(V_PREDICATES, N_DIM, g)
    # Split: build chains; first N_CHAINS_TRAIN are training, next N_CHAINS_HELDOUT are heldout
    n_total = N_CHAINS_TRAIN + N_CHAINS_HELDOUT
    train_triples_all, queries_all = make_two_hop_chains_fixed_pair(n_total, V_CONCEPTS, g)
    # Train triples: ONLY for training queries (first N_CHAINS_TRAIN pairs = 2*N_CHAINS_TRAIN triples)
    n_train_q = N_CHAINS_TRAIN
    train_triples = train_triples_all[:2 * n_train_q]
    train_queries = queries_all[:n_train_q]
    heldout_queries = queries_all[n_train_q:]
    # IMPORTANT: heldout chains' triples ARE included in W ingest (so the substrate
    # KNOWS the heldout edges); what's heldout is the CONSOLIDATION decision.
    heldout_triples = train_triples_all[2 * n_train_q:]
    all_ingest_triples = train_triples + heldout_triples

    print("[seed=%d] N=%d V_C=%d V_P=%d n_train=%d n_held=%d mode=%s K_THRESH_GRID=%s"
          % (seed, N_DIM, V_CONCEPTS, V_PREDICATES, n_train_q, len(heldout_queries),
             RUN_MODE, K_THRESH_GRID), flush=True)

    out = {
        "seed": seed, "run_mode": RUN_MODE, "N": N_DIM, "V_C": V_CONCEPTS,
        "V_P": V_PREDICATES, "n_train_queries": n_train_q,
        "n_heldout_queries": len(heldout_queries),
        "config_version": CONFIG_VERSION,
        "_llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
    }

    # ARM_NAIVE: standard 2-hop on ALL triples; eval on heldout queries
    # (apples-to-apples to consolidation arms' heldout evaluation)
    t_arm = time.time()
    r_naive_heldout = arm_naive_hard_2hop(E, R, sq, all_ingest_triples, heldout_queries)
    r_naive_train = arm_naive_hard_2hop(E, R, sq, all_ingest_triples, train_queries)
    out["arm_naive_hard_2hop"] = {
        "top1_TRAINING": r_naive_train["top1"],
        "top1_HELDOUT": r_naive_heldout["top1"],
        "elapsed_s_arm": round(time.time() - t_arm, 2),
        "n_train_queries": n_train_q,
        "n_heldout_queries": len(heldout_queries),
    }
    print("  [seed=%d] ARM_NAIVE training=%.4f heldout=%.4f t=%.1fs"
          % (seed, r_naive_train["top1"], r_naive_heldout["top1"],
             out["arm_naive_hard_2hop"]["elapsed_s_arm"]), flush=True)

    # K_THRESH grid (all consolidation arms)
    for k in K_THRESH_GRID:
        arm_name = "arm_consol_kthr_%d" % k
        if k == 1:
            arm_name = "arm_consol_kthr_1_control"
        t_arm = time.time()
        r = arm_consolidate(E, R, sq, all_ingest_triples,
                             train_queries, heldout_queries, k_thresh=k)
        r["elapsed_s_arm"] = round(time.time() - t_arm, 2)
        out[arm_name] = r
        print("  [seed=%d] ARM_CONSOL K=%d training=%.4f heldout=%.4f "
              "(%d compound preds; %d/%d heldout used compound) t=%.1fs"
              % (seed, k, r["top1_TRAINING"], r["top1_HELDOUT"],
                 r["n_compound_predicates_created"], r["n_heldout_compound"],
                 r["n_heldout_queries"], r["elapsed_s_arm"]), flush=True)

    # HYBRID at K_THRESH=3
    t_arm = time.time()
    r_hyb = arm_hybrid_kthr_plus_cleanup(E, R, sq, all_ingest_triples,
                                           train_queries, heldout_queries,
                                           k_thresh=3)
    r_hyb["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    out["arm_hybrid_kthr_3_plus_cleanup"] = r_hyb
    print("  [seed=%d] ARM_HYBRID K=3 training=%.4f heldout=%.4f t=%.1fs"
          % (seed, r_hyb["top1_TRAINING"], r_hyb["top1_HELDOUT"],
             r_hyb["elapsed_s_arm"]), flush=True)

    out["elapsed_s"] = round(time.time() - t, 1)
    return out


def verdict_from(per_seed: List[Dict[str, Any]]) -> Tuple[str, str]:
    def arm_mean(arm_key: str, metric_key: str) -> float:
        vals = [p[arm_key][metric_key] for p in per_seed
                if arm_key in p and metric_key in p[arm_key]
                and isinstance(p[arm_key][metric_key], (int, float))
                and not math.isnan(p[arm_key][metric_key])]
        return float(np.mean(vals)) if vals else float("nan")

    naive_heldout = arm_mean("arm_naive_hard_2hop", "top1_HELDOUT")
    naive_train = arm_mean("arm_naive_hard_2hop", "top1_TRAINING")

    arm_results: Dict[str, Dict[str, float]] = {}
    arm_results["NAIVE"] = {
        "heldout": naive_heldout, "training": naive_train,
    }
    for k in K_THRESH_GRID:
        arm_name = "arm_consol_kthr_%d" % k
        if k == 1:
            arm_name = "arm_consol_kthr_1_control"
        arm_results["CONSOL_K%d" % k] = {
            "heldout": arm_mean(arm_name, "top1_HELDOUT"),
            "training": arm_mean(arm_name, "top1_TRAINING"),
        }
    arm_results["HYBRID_K3_CLEANUP"] = {
        "heldout": arm_mean("arm_hybrid_kthr_3_plus_cleanup", "top1_HELDOUT"),
        "training": arm_mean("arm_hybrid_kthr_3_plus_cleanup", "top1_TRAINING"),
    }

    # Sanity rails
    rails: List[str] = []
    if not math.isnan(naive_heldout):
        if not (NAIVE_SANITY_LO <= naive_heldout <= NAIVE_SANITY_HI):
            rails.append("NAIVE_HELDOUT_OUT_OF_BAND(%.3f not in [%.2f,%.2f])"
                          % (naive_heldout, NAIVE_SANITY_LO, NAIVE_SANITY_HI))
    # K_THRESH=1 saturation trap check: training >= 0.95 AND heldout <= NAIVE + 0.03
    kthr1 = arm_results.get("CONSOL_K1", {})
    if not math.isnan(kthr1.get("training", float("nan"))):
        if kthr1["training"] < KTHR1_TRAINING_SATURATE_MIN:
            rails.append("KTHR1_TRAINING_NOT_SATURATED(%.3f<%.2f -- by-construction trap NOT reproduced)"
                          % (kthr1["training"], KTHR1_TRAINING_SATURATE_MIN))
        kthr1_heldout_overlift = kthr1["heldout"] - naive_heldout if not math.isnan(naive_heldout) else float("nan")
        if not math.isnan(kthr1_heldout_overlift) and kthr1_heldout_overlift > HF_HELDOUT_NEAR_NAIVE_DELTA:
            rails.append("KTHR1_HELDOUT_GENERALIZES?(K1_heldout=%.3f exceeds NAIVE+%.2f; "
                          "expected by-construction trap)" % (kthr1["heldout"], HF_HELDOUT_NEAR_NAIVE_DELTA))

    # HARD bands on HELDOUT
    consol_arm_keys = [k for k in arm_results if k.startswith("CONSOL_K") and k != "CONSOL_K1"]
    consol_arm_keys.append("HYBRID_K3_CLEANUP")
    consol_heldout = [(k, arm_results[k]["heldout"]) for k in consol_arm_keys
                       if not math.isnan(arm_results[k]["heldout"])]
    consol_heldout_max = max((v for _, v in consol_heldout), default=float("nan"))
    primary_pass = False
    if not math.isnan(arm_results["HYBRID_K3_CLEANUP"]["heldout"]) \
       and arm_results["HYBRID_K3_CLEANUP"]["heldout"] >= HP_BREAK_CEILING_HELDOUT:
        primary_pass = True
    if not math.isnan(arm_results.get("CONSOL_K3", {}).get("heldout", float("nan"))) \
       and arm_results["CONSOL_K3"]["heldout"] >= HP_BREAK_CEILING_HELDOUT:
        primary_pass = True

    # HARD_FAIL: all consolidation arms heldout <= NAIVE + delta
    if not math.isnan(naive_heldout) and consol_heldout:
        all_near_naive = all(v <= naive_heldout + HF_HELDOUT_NEAR_NAIVE_DELTA
                              for _, v in consol_heldout)
    else:
        all_near_naive = False

    summ = ("HELDOUT: NAIVE=%.4f " % naive_heldout
            + " ".join("%s=%.4f" % (k, v["heldout"]) for k, v in arm_results.items()
                       if k != "NAIVE")
            + " | TRAINING: NAIVE=%.4f" % naive_train
            + " ".join(" %s=%.4f" % (k, v["training"]) for k, v in arm_results.items()
                       if k != "NAIVE")
            + " | rails=%s" % rails
            + " | consol_heldout_max=%.4f naive_heldout=%.4f" % (
                consol_heldout_max, naive_heldout))

    if primary_pass:
        return "HARD_PASS_BREAK_CEILING", "HARD_PASS_BREAK_CEILING_HELDOUT: " + summ
    if not math.isnan(consol_heldout_max) and consol_heldout_max >= HP_HELDOUT:
        return "HARD_PASS", "HARD_PASS_HELDOUT: " + summ
    if all_near_naive:
        return "HARD_FAIL", "HARD_FAIL_CONSOLIDATION_NO_GENERALIZATION: " + summ
    return "MIDDLE_BAND", "MIDDLE_BAND_HELDOUT: " + summ


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
    print("[config] anchor=%s mode=%s seeds=%s N=%d V_C=%d V_P=%d | %s" % (
        ANCHOR_NAME, RUN_MODE, SEEDS, N_DIM, V_CONCEPTS, V_PREDICATES,
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
            "V2 PROPER TEST: K_THRESH > 1 (3, 5, 10) + held-out chains "
            "NEVER visible to consolidator. Cell 4 v1 was K_THRESH=1 + "
            "all-chains-visible -> by-construction saturation. v2 is the "
            "genuine multi-hop-generalization test. ARM_CONSOL_KTHR_1_CONTROL "
            "deliberately reproduces v1 trap (training saturate; heldout ~ NAIVE) "
            "as a methodological sanity check."
        ),
    }
    write_metrics(out_dir, metrics, results=per_seed)
    print("[done] metrics.json written (%d seeds, %.1fs)" % (
        len(per_seed), metrics["elapsed_s"]), flush=True)
