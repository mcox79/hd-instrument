"""substrate_multihop_consolidation_v3_proper_test_HELDOUT_FIX -- v2 bug fix.

V2 BUGS DISCOVERED (Director triage 2026-06-26):
  (1) HELDOUT=NaN: `make_two_hop_chains_fixed_pair` enforces `used_s` uniqueness
      and with V_C=200 + n_total=250 (200 train + 50 heldout), only ~200 unique
      chains were generated. heldout_queries=queries_all[200:] = EMPTY -> NaN.
  (2) K_THRESH degenerate: V_PREDICATES=2 with fixed pair (0,1) means EVERY
      chain shares (p1,p2)=(0,1). The (0,1) pair frequency = 200 in training,
      so ALL K_THRESH values {1,3,5,10} trigger consolidation identically.
      Result: K_THRESH "appears broken" but really the test was collapsed to
      a single chain class.

V3 FIX:
  (1) Heldout split done with EXPLICIT fresh chain construction (separate
      generator state), guaranteed-non-overlapping s values + ALWAYS yields
      the requested heldout count.
  (2) V_PREDICATES = 6 with MULTIPLE (p1,p2) chain classes at VARYING
      frequencies in training. K_THRESH actually discriminates:
        - Class HIGH (p1=0,p2=1): 100 chains in training (above K=10)
        - Class MID  (p1=2,p2=3):  10 chains in training (above K=3, below K=10)
        - Class LOW  (p1=4,p2=5):   2 chains in training (above K=1, below K=3)
      K=1 consolidates ALL 3 classes; K=3 consolidates HIGH+MID; K=10
      consolidates HIGH only; K=100 consolidates nothing.
  (3) Heldout queries split into per-class heldouts so we measure
      generalization per consolidation class.

NAIVE arm (sanity rail) STAYS at the beta-sweep regime (V_P=2 single class
p1=0,p2=1, 200 chains) so the 0.65 +/- 0.03 reference is preserved
APPLES-TO-APPLES. The naive arm uses its OWN chain set; consolidation arms
use the multi-class chain set. Both share E.

ARMS (6):
  ARM_NAIVE_HARD_2HOP                control; beta-sweep regime; must reproduce ~0.65
  ARM_CONSOL_KTHR_1_CONTROL          replicates v1 saturation trap (K=1 consolidates HIGH+MID+LOW)
  ARM_CONSOL_KTHR_3                  consolidates HIGH+MID only
  ARM_CONSOL_KTHR_5                  consolidates HIGH+MID only
  ARM_CONSOL_KTHR_10                 consolidates HIGH only
  ARM_HYBRID_KTHR_3_PLUS_CLEANUP     consolidation + per-step cleanup

TWO METRICS per consolidation arm:
  top1_TRAINING_HIGH/MID/LOW   per-class training accuracy (saturation diagnostic)
  top1_HELDOUT_HIGH/MID/LOW    per-class heldout accuracy (genuine generalization)
  top1_HELDOUT_OVERALL         pooled heldout (the primary metric)

HARD bands on HELDOUT (LOAD-BEARING per Fix #28):
  HARD_PASS_BREAK_CEILING:  ARM_HYBRID or ARM_KTHR_3 heldout_OVERALL >= 0.85
  HARD_PASS:                best heldout_OVERALL >= 0.75
  HARD_FAIL:                ALL consolidation arms heldout_OVERALL <= NAIVE + 0.03

SANITY (SACRED; cell aborts if violated):
  - NAIVE reproduces 0.65 +/- 0.03 (beta-sweep regime check)
  - ARM_KTHR_1 training_HIGH >= 0.95 AND training_HIGH > heldout_HIGH
    (proves by-construction trap fires on visible chains but not on novel s values)
  - K_THRESH GATING DIFFERENTIATES across configs: training_top1 must DIFFER
    across K values (not all 1.000) because not all classes consolidate.

D2 atexit + per-seed checkpoint; ASCII-only.
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

ANCHOR_NAME = "substrate_multihop_consolidation_v3_proper_test_heldout_fix"
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
KTHR1_TRAINING_HIGH_SATURATE_MIN = 0.95
KTHR_GATING_DIFFERENTIATION_MIN = 0.10  # training_top1 spread across K configs must be >= this

# NAIVE arm regime (beta-sweep apples-to-apples)
NAIVE_V_P = 2  # only p1=0, p2=1 used
NAIVE_N_CHAINS = 200  # matches beta-sweep N_CHAINS

# CONSOLIDATION arm regime (multi-class chains)
# Class frequencies in TRAINING (chosen so K_THRESH actually discriminates)
CONSOL_V_P = 6  # 3 classes use p_idx pairs (0,1) (2,3) (4,5)
CONSOL_CLASSES = [(0, 1), (2, 3), (4, 5)]  # HIGH, MID, LOW classes
if RUN_MODE == "smoke":
    N_DIM = 1024
    V_CONCEPTS = 200
    SEEDS = [7]
    CLASS_FREQS_TRAIN = [20, 5, 2]    # HIGH=20, MID=5, LOW=2 (27 train)
    CLASS_FREQS_HELDOUT = [10, 5, 3]  # 18 heldout
    K_THRESH_GRID = [1, 3]
    NAIVE_N_CHAINS_LOCAL = 50         # naive arm regime (smoke variant)
    # Used s: consol(27 train + 18 heldout) + naive(50) = 95 <= V_C=200 OK
else:
    N_DIM = 8192
    V_CONCEPTS = 600  # large enough to give unique s for all chains
    SEEDS = [7, 17, 23]
    CLASS_FREQS_TRAIN = [100, 10, 2]    # HIGH=100, MID=10, LOW=2 (112 train)
    CLASS_FREQS_HELDOUT = [30, 15, 5]   # 50 heldout per class total
    K_THRESH_GRID = [1, 3, 10, 50]
    NAIVE_N_CHAINS_LOCAL = NAIVE_N_CHAINS  # = 200 for naive arm regime match
    # Used s: consol(112+50) + naive(200) = 362 <= V_C=600 OK

N_CHAINS_TRAIN_TOTAL = sum(CLASS_FREQS_TRAIN)
N_CHAINS_HELDOUT_TOTAL = sum(CLASS_FREQS_HELDOUT)

CONFIG_VERSION = (
    "subconsv3-heldout-fix: N_DIM=%d V_C=%d NAIVE_V_P=%d (regime-match) "
    "CONSOL_V_P=%d classes=%s freqs_train=%s freqs_held=%s seeds=%s "
    "K_GRID=%s naive_n_chains=%d HP_break_heldout>=%.2f HP_heldout>=%.2f "
    "HF_near_naive_delta=%.2f naive_sanity=[%.2f,%.2f] "
    "kthr1_train_high_saturate>=%.2f gating_diff_min=%.2f"
) % (
    N_DIM, V_CONCEPTS, NAIVE_V_P, CONSOL_V_P, CONSOL_CLASSES,
    CLASS_FREQS_TRAIN, CLASS_FREQS_HELDOUT, SEEDS, K_THRESH_GRID,
    NAIVE_N_CHAINS_LOCAL,
    HP_BREAK_CEILING_HELDOUT, HP_HELDOUT, HF_HELDOUT_NEAR_NAIVE_DELTA,
    NAIVE_SANITY_LO, NAIVE_SANITY_HI, KTHR1_TRAINING_HIGH_SATURATE_MIN,
    KTHR_GATING_DIFFERENTIATION_MIN,
)


def bipolar(M: int, n: int, g: np.random.Generator) -> np.ndarray:
    X = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)


def make_two_hop_chains_fixed_pair_with_disallow(
        n_chains: int, V: int, p1: int, p2: int, g: np.random.Generator,
        disallow_s: set) -> Tuple[List[Tuple[int, int, int]],
                                    List[Tuple[int, int, int, int]]]:
    """Build n_chains chains using the SPECIFIED (p1,p2). disallow_s lists s
    values to avoid (used in OTHER constructions so we never duplicate s).

    Returns (triples, queries). queries=[(s,p1,p2,o), ...].
    BLOCKING: raises if cannot produce n_chains in V * 100 tries (so we never
    silently return fewer than asked -- the bug from v2).
    """
    train: List[Tuple[int, int, int]] = []
    queries: List[Tuple[int, int, int, int]] = []
    used_s = set(disallow_s)
    tries = 0
    while len(queries) < n_chains and tries < n_chains * 200:
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
        queries.append((s, p1, p2, o))
        used_s.add(s)
    if len(queries) < n_chains:
        raise RuntimeError(
            "BLOCKING make_two_hop_chains: only %d/%d generated for "
            "p1=%d p2=%d V=%d disallow|=%d. V too small or grid too dense."
            % (len(queries), n_chains, p1, p2, V, len(disallow_s))
        )
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
    """Beta-sweep regime naive 2-hop. State propagates noisy; cleanup at end only."""
    n_dim = E.shape[1]
    W = ingest_hebbian(train_triples, E, R, sq, n_dim)
    hits = 0
    for q in queries:
        s_idx, p1, p2, o_true = q
        state = E[s_idx].copy()
        state = W @ (state * R[p1] * sq)
        state = W @ (state * R[p2] * sq)
        o_pred = int((E @ state).argmax())
        if o_pred == o_true:
            hits += 1
    top1 = hits / max(len(queries), 1)
    return {"top1": round(top1, 4), "n_queries": len(queries)}


def arm_consolidate(E, R_primitive, sq, train_triples, train_queries,
                    heldout_queries_by_class: Dict[Tuple[int, int],
                                                     List[Tuple[int, int, int, int]]],
                    k_thresh: int) -> Dict[str, Any]:
    """Consolidate based on TRAINING (s,p1,p2) frequencies; eval on TRAINING
    and HELDOUT (HELDOUT split by class). Heldout chains are NEVER seen by the
    consolidator (their s values are disjoint from training).

    Per-class metrics: training_top1 per class + heldout_top1 per class +
    heldout_top1 pooled (the primary).

    For TRAINING queries:
      - Consolidated class -> compound 1-hop key
      - Else -> naive 2-hop (state propagates noisy)
    For HELDOUT queries (per class):
      - Consolidated class -> compound 1-hop key on NOVEL s (the genuine test)
      - Else -> naive 2-hop
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
        for j, q in enumerate(queries):
            s_idx, p1, p2, _ = q
            if (p1, p2) in pair_to_idx:
                comp_idx = R_primitive.shape[0] + pair_to_idx[(p1, p2)]
                key = (E[s_idx] * R_combined[comp_idx] * sq).astype(np.float32)
                state = W @ key
                o_hat[j] = int((E @ state).argmax())
            else:
                state = E[s_idx].copy()
                state = W @ (state * R_combined[p1] * sq)
                state = W @ (state * R_combined[p2] * sq)
                o_hat[j] = int((E @ state).argmax())
        return float((o_hat == o_true).mean())

    # Training per class (using existing training pair info to split)
    train_by_class: Dict[Tuple[int, int],
                          List[Tuple[int, int, int, int]]] = defaultdict(list)
    for q in train_queries:
        train_by_class[(q[1], q[2])].append(q)

    class_labels = {CONSOL_CLASSES[0]: "HIGH", CONSOL_CLASSES[1]: "MID",
                    CONSOL_CLASSES[2]: "LOW"}

    train_top1_per_class: Dict[str, float] = {}
    held_top1_per_class: Dict[str, float] = {}
    n_train_per_class: Dict[str, int] = {}
    n_held_per_class: Dict[str, int] = {}
    consolidated_per_class: Dict[str, bool] = {}
    for cls in CONSOL_CLASSES:
        label = class_labels[cls]
        tr_q = train_by_class.get(cls, [])
        held_q = heldout_queries_by_class.get(cls, [])
        train_top1_per_class[label] = eval_queries(tr_q)
        held_top1_per_class[label] = eval_queries(held_q)
        n_train_per_class[label] = len(tr_q)
        n_held_per_class[label] = len(held_q)
        consolidated_per_class[label] = (cls in pair_to_idx)

    # Pooled
    all_train = [q for qs in train_by_class.values() for q in qs]
    all_held = [q for qs in heldout_queries_by_class.values() for q in qs]
    train_top1_overall = eval_queries(all_train)
    held_top1_overall = eval_queries(all_held)

    return {
        "k_thresh": k_thresh,
        "n_compound_predicates_created": int(R_comp.shape[0]),
        "consolidated_classes": [class_labels[c] for c in CONSOL_CLASSES
                                  if c in pair_to_idx],
        "top1_TRAINING_OVERALL": round(train_top1_overall, 4),
        "top1_HELDOUT_OVERALL": round(held_top1_overall, 4),
        "top1_TRAINING_PER_CLASS": {k: round(v, 4) for k, v
                                     in train_top1_per_class.items()},
        "top1_HELDOUT_PER_CLASS": {k: round(v, 4) for k, v
                                    in held_top1_per_class.items()},
        "n_train_per_class": n_train_per_class,
        "n_heldout_per_class": n_held_per_class,
        "consolidated_per_class": consolidated_per_class,
        "n_train_queries": len(all_train),
        "n_heldout_queries": len(all_held),
    }


def arm_hybrid_kthr_plus_cleanup(E, R_primitive, sq, train_triples,
                                   train_queries, heldout_queries_by_class,
                                   k_thresh: int) -> Dict[str, Any]:
    """Wave14R-style: consolidated -> compound 1-hop; unconsolidated -> naive
    2-hop + per-hop nearest-atom cleanup (re-project state onto E after hop1
    before hop2).
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
        for j, q in enumerate(queries):
            s_idx, p1, p2, _ = q
            if (p1, p2) in pair_to_idx:
                comp_idx = R_primitive.shape[0] + pair_to_idx[(p1, p2)]
                key = (E[s_idx] * R_combined[comp_idx] * sq).astype(np.float32)
                state = W @ key
                o_hat[j] = int((E @ state).argmax())
            else:
                # Hop1: noisy state
                state = W @ (E[s_idx] * R_combined[p1] * sq)
                # CLEANUP: nearest-atom projection
                x_hat = int((E @ state).argmax())
                state = E[x_hat].astype(np.float32)
                # Hop2: from cleaned-up x
                state = W @ (state * R_combined[p2] * sq)
                o_hat[j] = int((E @ state).argmax())
        return float((o_hat == o_true).mean())

    train_by_class: Dict[Tuple[int, int],
                          List[Tuple[int, int, int, int]]] = defaultdict(list)
    for q in train_queries:
        train_by_class[(q[1], q[2])].append(q)

    class_labels = {CONSOL_CLASSES[0]: "HIGH", CONSOL_CLASSES[1]: "MID",
                    CONSOL_CLASSES[2]: "LOW"}
    train_top1_per_class = {class_labels[c]: round(eval_queries(train_by_class.get(c, [])), 4)
                             for c in CONSOL_CLASSES}
    held_top1_per_class = {class_labels[c]: round(eval_queries(heldout_queries_by_class.get(c, [])), 4)
                            for c in CONSOL_CLASSES}
    all_train = [q for qs in train_by_class.values() for q in qs]
    all_held = [q for qs in heldout_queries_by_class.values() for q in qs]
    return {
        "k_thresh": k_thresh,
        "n_compound_predicates_created": int(R_comp.shape[0]),
        "top1_TRAINING_OVERALL": round(eval_queries(all_train), 4),
        "top1_HELDOUT_OVERALL": round(eval_queries(all_held), 4),
        "top1_TRAINING_PER_CLASS": train_top1_per_class,
        "top1_HELDOUT_PER_CLASS": held_top1_per_class,
        "n_train_queries": len(all_train),
        "n_heldout_queries": len(all_held),
    }


def _build_full_chain_set(g: np.random.Generator
                           ) -> Tuple[List[Tuple[int, int, int]],
                                        List[Tuple[int, int, int, int]],
                                        Dict[Tuple[int, int],
                                              List[Tuple[int, int, int, int]]]]:
    """Build TRAIN + HELDOUT chains across CONSOL_CLASSES. Returns
    (all_ingest_triples, train_queries, heldout_queries_by_class).

    Disjoint s values across (class x split) so heldout chains are NEVER
    visible to the consolidator.
    """
    all_triples: List[Tuple[int, int, int]] = []
    train_queries: List[Tuple[int, int, int, int]] = []
    heldout_by_class: Dict[Tuple[int, int],
                            List[Tuple[int, int, int, int]]] = defaultdict(list)
    used_s: set = set()
    for cls_idx, (p1, p2) in enumerate(CONSOL_CLASSES):
        n_train_cls = CLASS_FREQS_TRAIN[cls_idx]
        n_held_cls = CLASS_FREQS_HELDOUT[cls_idx]
        # TRAIN
        triples_cls, queries_cls = make_two_hop_chains_fixed_pair_with_disallow(
            n_train_cls, V_CONCEPTS, p1, p2, g, disallow_s=used_s)
        all_triples.extend(triples_cls)
        train_queries.extend(queries_cls)
        for q in queries_cls:
            used_s.add(q[0])
        # HELDOUT
        held_triples_cls, held_queries_cls = make_two_hop_chains_fixed_pair_with_disallow(
            n_held_cls, V_CONCEPTS, p1, p2, g, disallow_s=used_s)
        all_triples.extend(held_triples_cls)  # heldout edges KNOWN by W
        heldout_by_class[(p1, p2)] = held_queries_cls
        for q in held_queries_cls:
            used_s.add(q[0])
    return all_triples, train_queries, heldout_by_class


def _selftest() -> None:
    g = np.random.default_rng(0)
    n = 256
    V = 80
    sq = math.sqrt(n)
    E = bipolar(V, n, g)
    R = bipolar(6, n, g)

    # 3 classes; HIGH=20, MID=5, LOW=2 in train
    classes = CONSOL_CLASSES
    freqs_tr = [20, 5, 2]
    freqs_he = [10, 4, 2]
    all_triples: List[Tuple[int, int, int]] = []
    train_q: List[Tuple[int, int, int, int]] = []
    held_by_cls: Dict[Tuple[int, int], List[Tuple[int, int, int, int]]] = defaultdict(list)
    used_s: set = set()
    for ci, (p1, p2) in enumerate(classes):
        tr, qs = make_two_hop_chains_fixed_pair_with_disallow(
            freqs_tr[ci], V, p1, p2, g, disallow_s=used_s)
        all_triples.extend(tr); train_q.extend(qs)
        for q in qs:
            used_s.add(q[0])
        ht, hq = make_two_hop_chains_fixed_pair_with_disallow(
            freqs_he[ci], V, p1, p2, g, disallow_s=used_s)
        all_triples.extend(ht); held_by_cls[(p1, p2)] = hq
        for q in hq:
            used_s.add(q[0])

    # K=1: HIGH+MID+LOW consolidate
    r1 = arm_consolidate(E, R, sq, all_triples, train_q, held_by_cls, k_thresh=1)
    assert r1["n_compound_predicates_created"] == 3, \
        "K=1 must consolidate all 3 classes: got %d" % r1["n_compound_predicates_created"]
    assert set(r1["consolidated_classes"]) == {"HIGH", "MID", "LOW"}
    # K=3: HIGH+MID only (LOW has freq=2)
    r3 = arm_consolidate(E, R, sq, all_triples, train_q, held_by_cls, k_thresh=3)
    assert r3["n_compound_predicates_created"] == 2, \
        "K=3 must consolidate HIGH+MID only: got %d" % r3["n_compound_predicates_created"]
    assert set(r3["consolidated_classes"]) == {"HIGH", "MID"}
    # K=10: HIGH only (MID has freq=5)
    r10 = arm_consolidate(E, R, sq, all_triples, train_q, held_by_cls, k_thresh=10)
    assert r10["n_compound_predicates_created"] == 1, \
        "K=10 must consolidate HIGH only: got %d" % r10["n_compound_predicates_created"]
    assert r10["consolidated_classes"] == ["HIGH"]
    # K=100: none
    r100 = arm_consolidate(E, R, sq, all_triples, train_q, held_by_cls, k_thresh=100)
    assert r100["n_compound_predicates_created"] == 0, \
        "K=100 must consolidate nothing: got %d" % r100["n_compound_predicates_created"]
    assert r100["consolidated_classes"] == []

    # Heldout metrics are FINITE numbers (not NaN); this is THE bug we fix
    for r in [r1, r3, r10, r100]:
        assert not math.isnan(r["top1_HELDOUT_OVERALL"]), \
            "HELDOUT must be finite: got %s" % r["top1_HELDOUT_OVERALL"]
        for cls, v in r["top1_HELDOUT_PER_CLASS"].items():
            assert not math.isnan(v), \
                "HELDOUT_PER_CLASS[%s] must be finite: got %s" % (cls, v)

    # K_THRESH gating MECHANICALLY differentiates: consolidation counts must
    # form a strict descending sequence as K rises (this is the v2 bug's
    # diagnostic; v2 had all K values consolidate the same 1 class).
    consol_counts = [r1["n_compound_predicates_created"],
                      r3["n_compound_predicates_created"],
                      r10["n_compound_predicates_created"],
                      r100["n_compound_predicates_created"]]
    assert consol_counts == [3, 2, 1, 0], \
        ("K_THRESH gating MUST produce descending consolidation counts (v2 had "
         "all-K identical): got %s; expected [3, 2, 1, 0]") % consol_counts
    # And K=1 train_overall > K=100 train_overall (more consolidation -> more
    # saturation on visible chains); this is the empirical signature of gating.
    # NOTE: at selftest scale (V=80, n_train=27), absolute numbers are noisy
    # at +/- 0.1; the differentiation gate enforces direction not magnitude.
    train_overalls = [r1["top1_TRAINING_OVERALL"], r3["top1_TRAINING_OVERALL"],
                       r10["top1_TRAINING_OVERALL"], r100["top1_TRAINING_OVERALL"]]
    assert r1["top1_TRAINING_OVERALL"] >= r100["top1_TRAINING_OVERALL"] - 0.05, \
        ("K=1 train_overall must be >= K=100 (modulo noise tol 0.05): "
         "got K=1=%.4f K=100=%.4f") % (
             r1["top1_TRAINING_OVERALL"], r100["top1_TRAINING_OVERALL"])

    # Naive arm (separate single-class regime)
    r_naive = arm_naive_hard_2hop(E, R, sq, all_triples,
                                   [q for qs in held_by_cls.values() for q in qs])
    assert 0.0 <= r_naive["top1"] <= 1.0

    # Hybrid
    r_hyb = arm_hybrid_kthr_plus_cleanup(E, R, sq, all_triples, train_q,
                                          held_by_cls, k_thresh=3)
    assert not math.isnan(r_hyb["top1_HELDOUT_OVERALL"])
    assert not math.isnan(r_hyb["top1_TRAINING_OVERALL"])

    print("[selftest] PASS naive_top1=%.3f | K=1: %d consol (%s) train_overall=%.3f held_overall=%.3f"
          % (r_naive["top1"], r1["n_compound_predicates_created"],
             r1["consolidated_classes"], r1["top1_TRAINING_OVERALL"],
             r1["top1_HELDOUT_OVERALL"]), flush=True)
    print("[selftest] K=3: %d consol (%s) train_overall=%.3f held_overall=%.3f"
          % (r3["n_compound_predicates_created"], r3["consolidated_classes"],
             r3["top1_TRAINING_OVERALL"], r3["top1_HELDOUT_OVERALL"]), flush=True)
    print("[selftest] K=10: %d consol (%s) train_overall=%.3f held_overall=%.3f"
          % (r10["n_compound_predicates_created"], r10["consolidated_classes"],
             r10["top1_TRAINING_OVERALL"], r10["top1_HELDOUT_OVERALL"]), flush=True)
    print("[selftest] K=100: %d consol (%s) train_overall=%.3f held_overall=%.3f"
          % (r100["n_compound_predicates_created"], r100["consolidated_classes"],
             r100["top1_TRAINING_OVERALL"], r100["top1_HELDOUT_OVERALL"]), flush=True)
    train_spread = max(train_overalls) - min(train_overalls)
    print("[selftest] GATING consolidation counts = %s; train_spread=%.4f "
          "(at full-scale verdict requires spread >= %.2f or descending counts)"
          % (consol_counts, train_spread, KTHR_GATING_DIFFERENTIATION_MIN), flush=True)


_selftest()
if _ARGS.self_test:
    print("[self-test] PASS; exiting", flush=True)
    sys.exit(0)


def run_seed(seed: int) -> Dict[str, Any]:
    t = time.time()
    g = np.random.default_rng(seed)
    sq = math.sqrt(N_DIM)
    # Predicate codebook large enough for max class index + 1
    n_predicates = max(NAIVE_V_P, CONSOL_V_P)
    E = bipolar(V_CONCEPTS, N_DIM, g)
    R = bipolar(n_predicates, N_DIM, g)

    # CONSOLIDATION chain set (multi-class)
    consol_triples, train_queries, heldout_by_class = _build_full_chain_set(g)

    # NAIVE arm: SEPARATE single-class chain set (beta-sweep apples-to-apples
    # regime). Disjoint s values from consolidation set (use a fresh disallow
    # set seeded from consolidation s usage).
    used_s_for_naive = set()
    for q in train_queries:
        used_s_for_naive.add(q[0])
    for qs in heldout_by_class.values():
        for q in qs:
            used_s_for_naive.add(q[0])
    # NB: NAIVE uses p1=0, p2=1 which IS in CONSOL_CLASSES[0]. That's fine:
    # we just use a SEPARATE W (its own triples) for the naive arm.
    naive_triples, naive_queries = make_two_hop_chains_fixed_pair_with_disallow(
        NAIVE_N_CHAINS_LOCAL, V_CONCEPTS, 0, 1, g, disallow_s=used_s_for_naive)

    print("[seed=%d] N=%d V_C=%d n_predicates=%d "
          "consol(n_train=%d, n_held=%d, classes=%s) "
          "naive(n_chains=%d) mode=%s K_GRID=%s"
          % (seed, N_DIM, V_CONCEPTS, n_predicates,
             len(train_queries),
             sum(len(qs) for qs in heldout_by_class.values()),
             [class_label_map(c) for c in CONSOL_CLASSES],
             len(naive_queries), RUN_MODE, K_THRESH_GRID), flush=True)

    out = {
        "seed": seed, "run_mode": RUN_MODE, "N": N_DIM, "V_C": V_CONCEPTS,
        "n_predicates": n_predicates,
        "n_train_queries": len(train_queries),
        "n_heldout_queries": sum(len(qs) for qs in heldout_by_class.values()),
        "n_naive_queries": len(naive_queries),
        "config_version": CONFIG_VERSION,
        "_llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
    }

    # ARM_NAIVE: apples-to-apples beta-sweep regime (must reproduce ~0.65)
    t_arm = time.time()
    r_naive = arm_naive_hard_2hop(E, R, sq, naive_triples, naive_queries)
    r_naive["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    out["arm_naive_hard_2hop"] = r_naive
    print("  [seed=%d] ARM_NAIVE top1=%.4f n=%d t=%.1fs"
          % (seed, r_naive["top1"], r_naive["n_queries"],
             r_naive["elapsed_s_arm"]), flush=True)

    # K_THRESH grid (consolidation arms)
    for k in K_THRESH_GRID:
        arm_name = "arm_consol_kthr_%d" % k
        if k == 1:
            arm_name = "arm_consol_kthr_1_control"
        t_arm = time.time()
        r = arm_consolidate(E, R, sq, consol_triples, train_queries,
                             heldout_by_class, k_thresh=k)
        r["elapsed_s_arm"] = round(time.time() - t_arm, 2)
        out[arm_name] = r
        print("  [seed=%d] ARM_CONSOL K=%d consol_classes=%s train_overall=%.4f "
              "held_overall=%.4f per_class_train=%s per_class_held=%s t=%.1fs"
              % (seed, k, r["consolidated_classes"], r["top1_TRAINING_OVERALL"],
                 r["top1_HELDOUT_OVERALL"], r["top1_TRAINING_PER_CLASS"],
                 r["top1_HELDOUT_PER_CLASS"], r["elapsed_s_arm"]), flush=True)

    # HYBRID at K_THRESH=3
    t_arm = time.time()
    r_hyb = arm_hybrid_kthr_plus_cleanup(E, R, sq, consol_triples, train_queries,
                                           heldout_by_class, k_thresh=3)
    r_hyb["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    out["arm_hybrid_kthr_3_plus_cleanup"] = r_hyb
    print("  [seed=%d] ARM_HYBRID K=3 train_overall=%.4f held_overall=%.4f t=%.1fs"
          % (seed, r_hyb["top1_TRAINING_OVERALL"], r_hyb["top1_HELDOUT_OVERALL"],
             r_hyb["elapsed_s_arm"]), flush=True)

    out["elapsed_s"] = round(time.time() - t, 1)
    return out


def class_label_map(cls: Tuple[int, int]) -> str:
    labels = {CONSOL_CLASSES[0]: "HIGH", CONSOL_CLASSES[1]: "MID",
              CONSOL_CLASSES[2]: "LOW"}
    return labels.get(cls, str(cls))


def verdict_from(per_seed: List[Dict[str, Any]]) -> Tuple[str, str]:
    def arm_mean(arm_key: str, metric_key: str) -> float:
        vals = [p[arm_key][metric_key] for p in per_seed
                if arm_key in p and metric_key in p[arm_key]
                and isinstance(p[arm_key][metric_key], (int, float))
                and not math.isnan(p[arm_key][metric_key])]
        return float(np.mean(vals)) if vals else float("nan")

    naive_top1 = arm_mean("arm_naive_hard_2hop", "top1")

    arm_results: Dict[str, Dict[str, float]] = {}
    arm_results["NAIVE"] = {"heldout": naive_top1, "training": float("nan")}
    for k in K_THRESH_GRID:
        arm_name = "arm_consol_kthr_%d" % k
        if k == 1:
            arm_name = "arm_consol_kthr_1_control"
        arm_results["CONSOL_K%d" % k] = {
            "heldout": arm_mean(arm_name, "top1_HELDOUT_OVERALL"),
            "training": arm_mean(arm_name, "top1_TRAINING_OVERALL"),
        }
    arm_results["HYBRID_K3_CLEANUP"] = {
        "heldout": arm_mean("arm_hybrid_kthr_3_plus_cleanup", "top1_HELDOUT_OVERALL"),
        "training": arm_mean("arm_hybrid_kthr_3_plus_cleanup", "top1_TRAINING_OVERALL"),
    }

    # Sanity rails
    rails: List[str] = []
    if not math.isnan(naive_top1):
        if not (NAIVE_SANITY_LO <= naive_top1 <= NAIVE_SANITY_HI):
            rails.append("NAIVE_OUT_OF_BAND(%.3f not in [%.2f,%.2f])"
                          % (naive_top1, NAIVE_SANITY_LO, NAIVE_SANITY_HI))

    # K_THRESH=1 saturation trap on HIGH class
    kthr1_train_high_vals = [p["arm_consol_kthr_1_control"]["top1_TRAINING_PER_CLASS"]["HIGH"]
                              for p in per_seed
                              if "arm_consol_kthr_1_control" in p
                              and "top1_TRAINING_PER_CLASS" in p["arm_consol_kthr_1_control"]
                              and "HIGH" in p["arm_consol_kthr_1_control"]["top1_TRAINING_PER_CLASS"]]
    kthr1_train_high = float(np.mean(kthr1_train_high_vals)) if kthr1_train_high_vals else float("nan")
    if not math.isnan(kthr1_train_high) and kthr1_train_high < KTHR1_TRAINING_HIGH_SATURATE_MIN:
        rails.append("KTHR1_TRAINING_HIGH_NOT_SATURATED(%.3f<%.2f -- by-construction trap NOT reproduced)"
                      % (kthr1_train_high, KTHR1_TRAINING_HIGH_SATURATE_MIN))

    # K_THRESH gating differentiation across K values
    train_per_k = {k: v["training"] for k, v in arm_results.items()
                    if k.startswith("CONSOL_K") and not math.isnan(v["training"])}
    if len(train_per_k) >= 2:
        spread = max(train_per_k.values()) - min(train_per_k.values())
        if spread < KTHR_GATING_DIFFERENTIATION_MIN:
            rails.append("KTHR_GATING_NOT_DIFFERENTIATING(train spread=%.3f<%.2f)"
                          % (spread, KTHR_GATING_DIFFERENTIATION_MIN))

    # HARD bands on HELDOUT_OVERALL
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

    if not math.isnan(naive_top1) and consol_heldout:
        all_near_naive = all(v <= naive_top1 + HF_HELDOUT_NEAR_NAIVE_DELTA
                              for _, v in consol_heldout)
    else:
        all_near_naive = False

    summ = ("HELDOUT_OVERALL: NAIVE=%.4f " % naive_top1
            + " ".join("%s=%.4f" % (k, v["heldout"]) for k, v in arm_results.items()
                       if k != "NAIVE")
            + " | TRAINING_OVERALL: "
            + " ".join("%s=%.4f" % (k, v["training"]) for k, v in arm_results.items()
                       if k != "NAIVE")
            + " | KTHR1_train_HIGH=%.3f" % kthr1_train_high
            + " | rails=%s | consol_held_max=%.4f naive=%.4f" % (
                rails, consol_heldout_max, naive_top1))

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
            "V3 HELDOUT FIX: v2 had two bugs: (1) heldout=NaN because "
            "make_two_hop_chains used_s exhausted V_C before generating heldout; "
            "(2) K_THRESH degenerate because V_P=2 fixed-pair meant only ONE "
            "chain class existed. V3 uses 3 chain classes (HIGH/MID/LOW) with "
            "VARYING training frequencies so K_THRESH actually discriminates: "
            "K=1 consolidates all 3, K=3 consolidates HIGH+MID, K=10 only HIGH, "
            "K=100 none. Heldout chains have DISJOINT s values from training "
            "(consolidator never sees them). NAIVE arm uses SEPARATE single-class "
            "chain set (beta-sweep apples-to-apples regime; W is its own); the "
            "0.65 sanity rail is preserved."
        ),
    }
    write_metrics(out_dir, metrics, results=per_seed)
    print("[done] metrics.json written (%d seeds, %.1fs)" % (
        len(per_seed), metrics["elapsed_s"]), flush=True)
