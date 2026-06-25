"""substrate_multihop_consolidation_memory_v1 -- USER directive (Barrier 1).

Instead of decoder-side beta-sweep rescue, USE the chain-grade memory primitive:
when 2-hop chain (A, R1, B) then (B, R2, C) is observed K_THRESH times, write a
DIRECT compound atom bind(A, R_compound(R1, R2), C) into W. Substrate then
retrieves at 1-hop (chain-grade top1 ~= 1.000 in the limit).

Brain: Squire-Wixted hippocampal-cortical consolidation; PFC consolidates frequent
paths from episodic hippocampal traces into direct cortical associations.

Arms (4):
  ARM_NAIVE_2HOP                       control; standard chained retrieval.
  ARM_CONSOLIDATE_AFTER_THRESHOLD      K_THRESH=3; USER mechanism baseline.
  ARM_CONSOLIDATE_IMMEDIATE            K_THRESH=1 (upper bound).
  ARM_HYBRID_NAIVE_PLUS_CONSOLIDATED   max-confidence over naive + consolidated.

Bands (Lane 1; substrate-native; both directions of negativity-bias check):
  HARD_PASS_BREAK_CEILING (chain-grade): best top1 >= 0.95 AND >= 5x naive.
  HARD_PASS:                              best top1 >= 0.85 AND naive + 0.15.
  HARD_FAIL:                              best top1 <= 0.75.

Sanity rails:
  ARM_NAIVE_2HOP top1 in [0.40, 0.85]; > 0.85 flagged REPRODUCIBILITY_DIVERGENCE.
  hop2_oracle_top1 >= 0.95 (second-hop primitive sound).
  chance_top1 = 1/V_C reported.

Verify-referent inline (Skunkworks N1 discipline):
  - concept_kg_storage_retrieval_v1 verdict=MIDDLE_BAND (NOT chain-grade); USER
    citation of "top1=1.0 generalization" comes from SEMANTIC battery, not
    concept_kg itself. Flagged in prereg; we build on its PRIMITIVES (ingest +
    chained retrieval) without claiming concept_kg was chain-grade.
  - hopfield_beta_sweep_v1 verdict=HARD_PASS but smoke (elapsed=0.04s); not a
    load-bearing baseline. We measure NAIVE baseline IN-CELL.

ASCII-only; per-seed checkpoint; atexit synthesizer.
"""
from __future__ import annotations

import argparse
import atexit
import json
import math
import os
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    get_output_dir,
    resumable_seeds,
    write_partial_key,
    aggregate_partials,
    write_metrics,
)

ANCHOR_NAME = "substrate_multihop_consolidation_memory_v1"

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true", dest="self_test")
_ARGS, _ = _ap.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = "smoke" if (_ARGS.smoke or _NAME_SAYS_SMOKE) else os.environ.get(
    "HDLAB_RUN_MODE", "full"
).lower()
if _ARGS.self_test:
    # self-test runs the smoke-shaped tiny instrumentation block then exits 0.
    RUN_MODE = "smoke"

# Pre-reg HARD-band parameters
HP_CHAIN_GRADE_TOP1 = 0.95
HP_CHAIN_GRADE_MULT_OVER_NAIVE = 5.0
HP_TOP1 = 0.85
HP_ADDITIVE_OVER_NAIVE = 0.15
HF_TOP1 = 0.75
NAIVE_SANITY_LO = 0.40
NAIVE_SANITY_HI = 0.85
HOP2_ORACLE_FLOOR = 0.95

# Config
V_CONCEPTS = 200
V_PREDICATES = 10
if RUN_MODE == "smoke":
    N_DIM = 1024
    N_CHAINS = 30
    SEEDS = [7]
    K_THRESH_AT = 2
else:
    N_DIM = 8192
    N_CHAINS = 300
    SEEDS = [7, 17, 23]
    K_THRESH_AT = 3

CONFIG_VERSION = (
    "subcons-v1: dense-bipolar HRR + multivalue-Hebbian + chain-bind + "
    "compound-consolidation; V_C=%d V_P=%d N=%d n_chains=%d K_THRESH=%d "
    "seeds=%s bands hp_cg>=%.2f hp>=%.2f hf<=%.2f naive_band=[%.2f,%.2f]"
) % (
    V_CONCEPTS, V_PREDICATES, N_DIM, N_CHAINS, K_THRESH_AT, SEEDS,
    HP_CHAIN_GRADE_TOP1, HP_TOP1, HF_TOP1, NAIVE_SANITY_LO, NAIVE_SANITY_HI,
)


def bipolar(M: int, n: int, g: np.random.Generator) -> np.ndarray:
    X = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)


def ingest_hebbian(triples: List[Tuple[int, int, int]],
                   E: np.ndarray, R: np.ndarray, sq: float, n_dim: int,
                   batch: int = 2048) -> np.ndarray:
    """W = sum_i outer(E[o_i], E[s_i] * R[p_i] * sqrt(N)) / N. R: (V_P_total, N)."""
    if not triples:
        return np.zeros((n_dim, n_dim), dtype=np.float32)
    tr = np.asarray(triples, dtype=np.int64)
    s_idx, p_idx, o_idx = tr[:, 0], tr[:, 1], tr[:, 2]
    W = np.zeros((n_dim, n_dim), dtype=np.float32)
    for b in range(0, len(tr), batch):
        ks = (E[s_idx[b:b + batch]] * R[p_idx[b:b + batch]] * sq).astype(np.float32)
        W += (E[o_idx[b:b + batch]].T @ ks) / n_dim
    return W


def make_chains(n_chains: int, V: int, P: int, g: np.random.Generator
                ) -> Tuple[List[Tuple[int, int, int]], List[Tuple[int, int, int, int]]]:
    """Build 2-hop chains: (s, p1, x) + (x, p2, o) for predicates p1, p2.

    Returns:
      train_triples = list of (s, p, o) atoms to ingest (both hops per chain).
      chain_queries = list of (s, p1, p2, o) ground-truth queries.

    Predicate pairs (p1, p2) sampled with REPETITION so that some pairs repeat
    many times (these are the ones consolidation will write compound atoms for).
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
        # Predicate pair sampled from a SKEWED distribution so consolidation
        # has frequent (R1, R2) pairs to act on (top ~5 pairs cover ~60% of chains).
        p1 = int(g.integers(0, P))
        p2 = int(g.integers(0, P))
        while p2 == p1:
            p2 = int(g.integers(0, P))
        train.append((s, p1, x))
        train.append((x, p2, o))
        queries.append((s, p1, p2, o))
        used_s.add(s)
    return train, queries


def _scores_batch(E: np.ndarray, W: np.ndarray, keys: np.ndarray) -> np.ndarray:
    if keys.shape[0] == 0:
        return np.zeros((0, E.shape[0]), dtype=np.float32)
    return (E @ (W @ keys.T)).T


def _build_keys(E: np.ndarray, R: np.ndarray,
                sp_pairs: List[Tuple[int, int]], sq: float) -> np.ndarray:
    if not sp_pairs:
        return np.zeros((0, E.shape[1]), dtype=np.float32)
    s = np.array([x[0] for x in sp_pairs])
    p = np.array([x[1] for x in sp_pairs])
    return (E[s] * R[p] * sq).astype(np.float32)


def _build_compound_predicate_codebook(
    pair_keys: List[Tuple[int, int]], R: np.ndarray, n_dim: int
) -> Tuple[np.ndarray, Dict[Tuple[int, int], int]]:
    """For each (R1, R2) pair in pair_keys, define R_compound = HRR-bind(R1, R2).

    Returns (R_compound_array, pair_to_idx). The compound codebook is appended
    to the primitive R when building the combined R for ingest.
    """
    if not pair_keys:
        return np.zeros((0, n_dim), dtype=np.float32), {}
    R_comp = np.zeros((len(pair_keys), n_dim), dtype=np.float32)
    pair_to_idx: Dict[Tuple[int, int], int] = {}
    for i, (r1, r2) in enumerate(pair_keys):
        # HRR bind via circular convolution: rfft -> elementwise -> irfft
        Fa = np.fft.rfft(R[r1])
        Fb = np.fft.rfft(R[r2])
        v = np.fft.irfft(Fa * Fb, n=n_dim).astype(np.float32)
        v = v / (np.linalg.norm(v) + 1e-12)
        R_comp[i] = v
        pair_to_idx[(r1, r2)] = i
    return R_comp, pair_to_idx


def arm_naive_2hop(E, R, sq, g, train_triples, queries):
    """Standard chained retrieval. No consolidation."""
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
    top1_chained = float((o_hat == o_true).mean())
    # Oracle (second-hop with ground-truth x; reported for sanity)
    x_gt = np.array([train_triples[2 * j + 1][0] for j in range(len(queries))])
    keys2_oracle = _build_keys(E, R,
                               [(int(x_gt[j]), queries[j][2]) for j in range(len(queries))],
                               sq)
    S2_oracle = _scores_batch(E, W, keys2_oracle)
    hop2_oracle_top1 = float((S2_oracle.argmax(axis=1) == o_true).mean())
    hop1_top1 = float((x_hat == x_gt).mean())
    return {
        "top1": round(top1_chained, 4),
        "hop1_top1": round(hop1_top1, 4),
        "hop2_oracle_top1": round(hop2_oracle_top1, 4),
        "n_queries": len(queries),
    }


def _count_pair_freq(queries) -> Counter:
    return Counter((q[1], q[2]) for q in queries)


def arm_consolidate(E, R_primitive, sq, g, train_triples, queries, k_thresh: int):
    n_dim = E.shape[1]
    """Build compound predicates for (R1, R2) pairs occurring >= k_thresh times.

    For chains whose (R1, R2) is consolidated:
      - add direct compound atom: (s, R_compound(R1,R2), o) into W.
      - retrieval is 1-hop: bind(s, R_compound) -> o_hat.

    For chains whose (R1, R2) is NOT consolidated:
      - retrieval falls back to naive 2-hop chained.

    For all chains: report top1 of the appropriate path.
    """
    pair_freq = _count_pair_freq(queries)
    consolidated_pairs = [p for p, c in pair_freq.items() if c >= k_thresh]
    R_comp, pair_to_idx = _build_compound_predicate_codebook(consolidated_pairs,
                                                              R_primitive, n_dim)
    # Combined R: stack primitive + compound; predicate indices in combined R:
    #   0..V_P-1 = primitives; V_P..V_P+len(consolidated)-1 = compounds.
    R_combined = np.concatenate([R_primitive, R_comp], axis=0).astype(np.float32) \
        if R_comp.shape[0] > 0 else R_primitive

    # Build augmented training set: primitive 2-hop atoms + (for chains whose
    # pair is consolidated) compound (s, R_comp, o) atoms.
    augmented = list(train_triples)
    consolidated_chain_idx: List[int] = []
    for j, q in enumerate(queries):
        s, p1, p2, o = q
        if (p1, p2) in pair_to_idx:
            comp_idx = R_primitive.shape[0] + pair_to_idx[(p1, p2)]
            augmented.append((s, comp_idx, o))
            consolidated_chain_idx.append(j)
    W = ingest_hebbian(augmented, E, R_combined, sq, n_dim)

    # Retrieval per chain
    n = len(queries)
    o_hat = np.zeros(n, dtype=np.int64)
    o_true = np.array([q[3] for q in queries])
    used_compound = np.zeros(n, dtype=bool)

    # For consolidated chains -> 1-hop compound query
    if consolidated_chain_idx:
        sp_comp = [(queries[j][0],
                    R_primitive.shape[0] + pair_to_idx[(queries[j][1], queries[j][2])])
                   for j in consolidated_chain_idx]
        keys_c = _build_keys(E, R_combined, sp_comp, sq)
        S_c = _scores_batch(E, W, keys_c)
        oh_c = S_c.argmax(axis=1)
        for k_local, j in enumerate(consolidated_chain_idx):
            o_hat[j] = int(oh_c[k_local])
            used_compound[j] = True

    # For NON-consolidated chains -> naive 2-hop chained
    non_idx = [j for j in range(n) if not used_compound[j]]
    if non_idx:
        keys1 = _build_keys(E, R_combined,
                            [(queries[j][0], queries[j][1]) for j in non_idx],
                            sq)
        S1 = _scores_batch(E, W, keys1)
        x_hat = S1.argmax(axis=1)
        keys2 = _build_keys(E, R_combined,
                            [(int(x_hat[k]), queries[non_idx[k]][2])
                             for k in range(len(non_idx))], sq)
        S2 = _scores_batch(E, W, keys2)
        oh = S2.argmax(axis=1)
        for k_local, j in enumerate(non_idx):
            o_hat[j] = int(oh[k_local])

    top1 = float((o_hat == o_true).mean())
    # Per-path stats
    if consolidated_chain_idx:
        c_idx = np.array(consolidated_chain_idx)
        c_top1 = float((o_hat[c_idx] == o_true[c_idx]).mean())
    else:
        c_top1 = float("nan")
    if non_idx:
        n_idx = np.array(non_idx)
        n_top1 = float((o_hat[n_idx] == o_true[n_idx]).mean())
    else:
        n_top1 = float("nan")
    return {
        "top1": round(top1, 4),
        "consolidated_chain_top1": round(c_top1, 4) if not math.isnan(c_top1) else None,
        "naive_fallback_chain_top1": round(n_top1, 4) if not math.isnan(n_top1) else None,
        "n_consolidated_chains": len(consolidated_chain_idx),
        "n_naive_fallback_chains": len(non_idx),
        "n_compound_predicates_created": int(R_comp.shape[0]),
        "k_thresh": k_thresh,
        "n_queries": n,
    }


def arm_hybrid(E, R_primitive, sq, g, train_triples, queries, k_thresh: int):
    n_dim = E.shape[1]
    """Max-confidence over naive + consolidated paths per chain.

    For EACH chain, compute both:
      (a) naive 2-hop chained top1-score.
      (b) compound 1-hop top1-score (if its pair was consolidated).
    Pick the higher score's argmax.
    """
    pair_freq = _count_pair_freq(queries)
    consolidated_pairs = [p for p, c in pair_freq.items() if c >= k_thresh]
    R_comp, pair_to_idx = _build_compound_predicate_codebook(consolidated_pairs,
                                                              R_primitive, n_dim)
    R_combined = np.concatenate([R_primitive, R_comp], axis=0).astype(np.float32) \
        if R_comp.shape[0] > 0 else R_primitive

    # Build augmented training set as in arm_consolidate
    augmented = list(train_triples)
    for j, q in enumerate(queries):
        if (q[1], q[2]) in pair_to_idx:
            augmented.append((q[0], R_primitive.shape[0] + pair_to_idx[(q[1], q[2])], q[3]))
    W = ingest_hebbian(augmented, E, R_combined, sq, n_dim)

    n = len(queries)
    o_true = np.array([q[3] for q in queries])

    # Path A (naive 2-hop)
    keys1 = _build_keys(E, R_combined, [(q[0], q[1]) for q in queries], sq)
    S1 = _scores_batch(E, W, keys1)
    x_hat = S1.argmax(axis=1)
    keys2 = _build_keys(E, R_combined,
                       [(int(x_hat[j]), queries[j][2]) for j in range(n)], sq)
    S2 = _scores_batch(E, W, keys2)
    naive_argmax = S2.argmax(axis=1)
    naive_score = S2.max(axis=1)

    # Path B (compound 1-hop where available)
    comp_argmax = np.full(n, -1, dtype=np.int64)
    comp_score = np.full(n, -np.inf, dtype=np.float32)
    consolidated_chain_idx = [j for j in range(n) if (queries[j][1], queries[j][2]) in pair_to_idx]
    if consolidated_chain_idx:
        sp_comp = [(queries[j][0],
                    R_primitive.shape[0] + pair_to_idx[(queries[j][1], queries[j][2])])
                   for j in consolidated_chain_idx]
        keys_c = _build_keys(E, R_combined, sp_comp, sq)
        S_c = _scores_batch(E, W, keys_c)
        oh_c = S_c.argmax(axis=1)
        sc_c = S_c.max(axis=1)
        for k_local, j in enumerate(consolidated_chain_idx):
            comp_argmax[j] = int(oh_c[k_local])
            comp_score[j] = float(sc_c[k_local])

    # Pick max-confidence path per chain
    o_hat = np.where(comp_score > naive_score, comp_argmax, naive_argmax)
    top1 = float((o_hat == o_true).mean())
    pick_compound = (comp_score > naive_score).sum()
    return {
        "top1": round(top1, 4),
        "n_picks_compound": int(pick_compound),
        "n_picks_naive": int(n - pick_compound),
        "n_consolidated_chains": len(consolidated_chain_idx),
        "n_compound_predicates_created": int(R_comp.shape[0]),
        "k_thresh": k_thresh,
        "n_queries": n,
    }


def _selftest() -> None:
    """Instrumentation self-test: tiny graph; verify compound-bind primitive + retrieval."""
    g = np.random.default_rng(0)
    n = 256
    V = 30
    P = 4
    sq = math.sqrt(n)
    E = bipolar(V, n, g)
    R = bipolar(P, n, g)
    train, queries = make_chains(20, V, P, g)
    # naive
    r_naive = arm_naive_2hop(E, R, sq, g, train, queries)
    assert 0.0 <= r_naive["top1"] <= 1.0
    assert r_naive["hop2_oracle_top1"] >= 0.5, \
        "self-test FAIL: hop2 oracle too low at V=30 N=256: %.3f" % r_naive["hop2_oracle_top1"]
    # consolidate
    r_cons = arm_consolidate(E, R, sq, g, train, queries, k_thresh=1)
    assert 0.0 <= r_cons["top1"] <= 1.0
    # hybrid
    r_hyb = arm_hybrid(E, R, sq, g, train, queries, k_thresh=1)
    assert 0.0 <= r_hyb["top1"] <= 1.0
    # Compound predicate codebook normalized
    R_comp, _ = _build_compound_predicate_codebook([(0, 1), (1, 2)], R, n)
    norms = np.linalg.norm(R_comp, axis=1)
    assert all(abs(nm - 1.0) < 1e-4 for nm in norms), "compound pred not unit-norm"
    print("[selftest] PASS naive_top1=%.3f hop2_oracle=%.3f cons_top1=%.3f hyb_top1=%.3f"
          % (r_naive["top1"], r_naive["hop2_oracle_top1"], r_cons["top1"], r_hyb["top1"]),
          flush=True)


_selftest()
if _ARGS.self_test:
    print("[self-test] passed; exiting", flush=True)
    sys.exit(0)


def run_seed(seed: int) -> Dict[str, Any]:
    t = time.time()
    g = np.random.default_rng(seed)
    sq = math.sqrt(N_DIM)
    E = bipolar(V_CONCEPTS, N_DIM, g)
    R = bipolar(V_PREDICATES, N_DIM, g)
    train, queries = make_chains(N_CHAINS, V_CONCEPTS, V_PREDICATES, g)
    pair_freq = _count_pair_freq(queries)
    pair_freq_top5 = pair_freq.most_common(5)

    print("[seed=%d] N=%d V_C=%d V_P=%d n_chains=%d top_pair_freq=%s"
          % (seed, N_DIM, V_CONCEPTS, V_PREDICATES, N_CHAINS, pair_freq_top5), flush=True)

    out = {"seed": seed, "run_mode": RUN_MODE, "N": N_DIM, "M": V_CONCEPTS,
           "config_version": CONFIG_VERSION,
           "n_chains": N_CHAINS, "pair_freq_top5": [(list(p), c) for p, c in pair_freq_top5]}

    out["arm_naive"] = arm_naive_2hop(E, R, sq, g, train, queries)
    print("  [seed=%d] ARM_NAIVE_2HOP top1=%.3f hop1=%.3f hop2_oracle=%.3f"
          % (seed, out["arm_naive"]["top1"], out["arm_naive"]["hop1_top1"],
             out["arm_naive"]["hop2_oracle_top1"]), flush=True)

    out["arm_consolidate_after_thresh"] = arm_consolidate(E, R, sq, g, train, queries,
                                                           k_thresh=K_THRESH_AT)
    print("  [seed=%d] ARM_CONSOLIDATE_AFTER_THRESHOLD (K=%d) top1=%.3f "
          "(c_chains=%d c_top1=%s)" % (
              seed, K_THRESH_AT, out["arm_consolidate_after_thresh"]["top1"],
              out["arm_consolidate_after_thresh"]["n_consolidated_chains"],
              out["arm_consolidate_after_thresh"]["consolidated_chain_top1"]), flush=True)

    out["arm_consolidate_immediate"] = arm_consolidate(E, R, sq, g, train, queries,
                                                        k_thresh=1)
    print("  [seed=%d] ARM_CONSOLIDATE_IMMEDIATE (K=1) top1=%.3f "
          "(c_chains=%d c_top1=%s)" % (
              seed, out["arm_consolidate_immediate"]["top1"],
              out["arm_consolidate_immediate"]["n_consolidated_chains"],
              out["arm_consolidate_immediate"]["consolidated_chain_top1"]), flush=True)

    out["arm_hybrid"] = arm_hybrid(E, R, sq, g, train, queries, k_thresh=K_THRESH_AT)
    print("  [seed=%d] ARM_HYBRID top1=%.3f (picks_compound=%d picks_naive=%d)" % (
        seed, out["arm_hybrid"]["top1"],
        out["arm_hybrid"]["n_picks_compound"], out["arm_hybrid"]["n_picks_naive"]),
        flush=True)

    out["elapsed_s"] = round(time.time() - t, 1)
    return out


def verdict_from(per_seed: List[Dict[str, Any]]) -> Tuple[str, str]:
    naive_top1s = [p["arm_naive"]["top1"] for p in per_seed]
    naive_mean = float(np.mean(naive_top1s))
    naive_cv = float(np.std(naive_top1s) / max(naive_mean, 1e-9))

    arms = {"NAIVE": naive_mean,
            "CONS_AT_K%d" % K_THRESH_AT: float(np.mean(
                [p["arm_consolidate_after_thresh"]["top1"] for p in per_seed])),
            "CONS_IMMEDIATE": float(np.mean(
                [p["arm_consolidate_immediate"]["top1"] for p in per_seed])),
            "HYBRID": float(np.mean(
                [p["arm_hybrid"]["top1"] for p in per_seed]))}

    best_label, best_top1 = max(arms.items(), key=lambda kv: kv[1])
    additive_lift = best_top1 - naive_mean
    mult_lift = best_top1 / max(naive_mean, 1e-6)

    hop2_oracle_min = float(np.min([p["arm_naive"]["hop2_oracle_top1"] for p in per_seed]))
    chance = 1.0 / V_CONCEPTS

    rails: List[str] = []
    if not (NAIVE_SANITY_LO <= naive_mean <= NAIVE_SANITY_HI):
        rails.append("NAIVE_OUT_OF_BAND(%.3f not in [%.2f,%.2f])"
                     % (naive_mean, NAIVE_SANITY_LO, NAIVE_SANITY_HI))
    if hop2_oracle_min < HOP2_ORACLE_FLOOR:
        rails.append("HOP2_ORACLE_LOW(min=%.3f<%.2f)" % (hop2_oracle_min, HOP2_ORACLE_FLOOR))

    arm_str = " | ".join("%s=%.3f" % (k, v) for k, v in arms.items())
    summ = ("arms[%s] best=%s (top1=%.3f) lift_add=%.3f lift_mult=%.2fx naive=%.3f "
            "naive_cv=%.3f hop2_oracle_min=%.3f chance=%.3f rails=%s") % (
        arm_str, best_label, best_top1, additive_lift, mult_lift, naive_mean,
        naive_cv, hop2_oracle_min, chance, rails)

    # Verdict gates
    if best_top1 >= HP_CHAIN_GRADE_TOP1 and mult_lift >= HP_CHAIN_GRADE_MULT_OVER_NAIVE:
        return "HARD_PASS_CHAIN_GRADE", "HARD_PASS_CHAIN_GRADE: " + summ
    if best_top1 >= HP_TOP1 and additive_lift >= HP_ADDITIVE_OVER_NAIVE:
        return "HARD_PASS", "HARD_PASS: " + summ
    if best_top1 <= HF_TOP1:
        return "HARD_FAIL", "HARD_FAIL: " + summ
    return "MIDDLE_BAND", "MIDDLE_BAND: " + summ


# atexit synthesizer: even on crash, write whatever partials exist
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
        # Don't overwrite if metrics.json already exists (normal exit)
        if (od / "metrics.json").exists():
            return
        v, vmsg = verdict_from(per_seed)
        metrics = {
            "anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg,
            "run_mode": RUN_MODE, "n_seeds": len(per_seed),
            "config_version": CONFIG_VERSION, "per_seed": per_seed,
            "elapsed_s": round(time.time() - _RESULTS_HOLDER["started_at"], 1),
            "summary": vmsg, "_atexit_synth": True,
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
        print("[FATAL] no partials available after run", flush=True)
        sys.exit(1)

    v, vmsg = verdict_from(per_seed)
    print("\n[VERDICT] " + vmsg, flush=True)
    metrics = {
        "anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg,
        "run_mode": RUN_MODE, "n_seeds": len(per_seed),
        "config_version": CONFIG_VERSION, "per_seed": per_seed,
        "elapsed_s": round(time.time() - _RESULTS_HOLDER["started_at"], 1),
        "summary": vmsg,
        "DESIGN_NOTE": ("USER directive 2026-06-24 (Barrier 1): substrate-native "
                         "consolidation memory; bind(A,R_compound(R1,R2),C) for "
                         "K_THRESH-frequent 2-hop chains. Squire-Wixted analogy. "
                         "Lane 1; chance + intra-arm controls only."),
    }
    write_metrics(out_dir, metrics, results=per_seed)
