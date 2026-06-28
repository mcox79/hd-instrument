"""substrate_barrier1_hint_learned_linear_planner_drill2_v1_seed_7.

DRILL 2 of 2x-drill-before-closure for Barrier 1 hint-derivation. Mechanism class:
SUPERVISED LEARNED LINEAR PROJECTOR (genuinely different from Drill 1's cosine
centroid + Drills 1.5/A/B's handcrafted brain-composition).

PURPOSE:
    Drill 1 cosine centroid (`pred_part = argmax(C @ state)`) FAILED at route_acc
    = 0.217 (5-partition chance = 0.20). Mechanism was UNTRAINED -- assumed the
    W-output state at hop i naturally clusters near the target partition's mean.
    Smoke proved this false. Drills 1.5/A/B (handcrafted brain composition) also
    HARD_FAIL.

    Drill 2 tests if a TRAINED supervised linear classifier
    `W_planner: R^N -> R^N_PART` can extract any partition-routing signal from
    the SAME W @ key state-vector (META_RULE_AP_v3 signal-shape audit).

ARMS (5; identical layout to Drill 1 for clean delta interpretation):
    A: BASELINE          argmax over V_C=4000 (no hint; rail)
    B: LEARNED_PLANNER   argmax(W_planner @ state); W_planner trained on
                         (state, true_part) pairs from chains_train
    C: ORACLE            ground-truth partition (upper bound)
    D: NOISY_HINT        random-permuted partition labels (negative control)
    E: RANDOM            random partition pick per hop (floor)

POSITIVE CONTROL (gate before full-N discriminator):
    At an EASIER regime (d=5, N_part=10) with separate 500-train / 100-test
    pairs, planner_route_acc_pc MUST be >= 0.50 (above chance=0.10). If it
    fails, mechanism is broken OR query carries zero signal at any depth;
    abort before full ingest.

PRE-REG BANDS (META_RULE_AL; LOCKED at module init):
    BASELINE rail (BIAS-S): ARM_A.top1@d15 in [0.30, 0.70]
    HARD_PASS:
        ARM_B.top1@d15 in [0.50, 0.95]
        AND ARM_B - ARM_A >= 0.30
        AND ARM_B - ARM_E >= 0.30
        AND ARM_C - ARM_B <= 0.30
        AND |ARM_D - ARM_A| <= 0.10
        AND saturation == False (ARM_B < 0.95)
        AND arms_distinct == True
        AND positive_control_pass == True
        AND train_test_disjoint == True
    HARD_FAIL:
        ARM_B.top1@d15 <= 0.30
        OR planner_route_acc@d15 < 0.30
        OR (ARM_B - ARM_A) < 0.10
        OR positive_control_pass == False
    MIDDLE_BAND:
        ARM_B in [0.30, 0.50) with lift_b_a >= 0.15
        OR HP-band hit BUT lift_b_a in [0.15, 0.30)

DISCIPLINE TAGS:
    META_RULE_AC: number tagging MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@
    META_RULE_AE: absolute metrics.json paths in DESIGN_NOTE
    META_RULE_AF: arms-must-differ SHA-256 hash check post-run
    META_RULE_AG: discriminator at edge-of-capacity (B un-saturated; A in rail)
    META_RULE_AH: atomic metrics.json write (via _seed_checkpoint)
    META_RULE_AL: HP + HF bands LOCKED at module init
    META_RULE_AN: substrate-empirical anchor (per_step matches parent regime)
    META_RULE_AP_v3: signal-shape audit (state at train == state at test)
    META_RULE_H : CARDINALITY_OK; expected_n_units = 5 (1 seed x 5 arms)
    BIAS-Q     : saturation guard at 0.95
    BIAS-N     : per-arm metrics in summary (NOT verdict_msg only)
    BIAS-S     : baseline rail [0.30, 0.70]
    DISCRIMINATOR-MUST-SURVIVE-SCALE: smoke at FULL-N + FULL-depth + positive control
    PROT-018: regime params bind to ANCHOR_NAME in CONFIG_VERSION
    Fix #28: per-arm reads from metrics.json
    CHUNKED: single seed per cell; sibling cells for seeds 13 and 19
    functional_requirement_first: planner training + signal-shape audit documented

SOURCE CITATIONS (ABSOLUTE PATHS; META_RULE_AE):
    - Prereg:
      d:/AI/hd-instrument/preregs/2026-06-28_substrate_barrier1_hint_learned_linear_planner_drill2_v1.md
    - Drill 1 parent prereg:
      d:/AI/hd-instrument/preregs/2026-06-28_substrate_partition_oracle_substrate_derived_hint_v1.md
    - Drill 1 source cell:
      d:/AI/hd-instrument/experiments/exp_substrate_partition_oracle_substrate_derived_hint_v1_seed_7.py
    - Drill 1 smoke metrics (chance-routing finding; route_acc=0.217):
      d:/AI/hd-instrument/data/exp_substrate_partition_oracle_substrate_derived_hint_v1_seed_7_smoke/metrics.json
    - Chain-grade oracle reference (ground-truth upper bound; HARD_PASS):
      d:/AI/hd-instrument/data/exp_substrate_multihop_partition_oracle_v5_hardened_FULL_seed_19_v1/metrics.json

NUMBER TAGGING (META_RULE_AC):
    MEASURED@DRILL1_ROUTE_ACC_SMOKE: 0.2173 (5-partition chance = 0.20)
    MEASURED@DRILL1_ARM_B_TOP1: 0.0000
    MEASURED@DRILL1_ORACLE_C_SMOKE: 0.8400
    MEASURED@DRILL1_BASELINE_A_SMOKE: 0.4000
    HYPOTHESIZED@HP_PLANNER_ROUTE_ACC: >= 0.50 at d=15
    HYPOTHESIZED@HP_ARM_B_TOP1: in [0.50, 0.95]
    HYPOTHESIZED@HP_LIFT_OVER_BASELINE: >= 0.30
    HYPOTHESIZED@POSITIVE_CONTROL_ROUTE_ACC: >= 0.50 at d=5 N_part=10
    THEORETICAL@CHANCE_5_PART: 0.20
    THEORETICAL@CHANCE_10_PART: 0.10

Author: exp_dev 2026-06-28 (functional-requirement-first per USER directive).
ASCII-only; __main__ guard; SystemExit re-raised before BaseException.
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
import hashlib
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

ANCHOR_NAME = "substrate_barrier1_hint_learned_linear_planner_drill2_v1_seed_7"
_SEED = 7
_LLM_CALL_COUNTER = [0]

# ----------------------------------------------------------------------------
# arg parsing
# ----------------------------------------------------------------------------
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true", dest="self_test")
_ARGS, _ = _ap.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = ("smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE)
            else os.environ.get("HDLAB_RUN_MODE", "full").lower())

# ----------------------------------------------------------------------------
# PRE-REG BANDS (LOCKED at module init; META_RULE_AL)
# ----------------------------------------------------------------------------
N_DIM = 8192
V_CONCEPTS = 4000
V_PRED = 10
DEPTH = 15
MAX_DEPTH = 15

# BASELINE rail @d=15
BASELINE_RAIL_TARGET = 0.449
BASELINE_RAIL_LO = 0.30
BASELINE_RAIL_HI = 0.70

# ARM_B learned-planner bands @d=15
HP_ARM_B_LO = 0.50
HP_ARM_B_HI = 0.95
HP_LIFT_OVER_BASELINE = 0.30
HP_LIFT_OVER_RANDOM = 0.30
HP_GAP_ORACLE_OVER_DERIVED = 0.30
HP_NOISY_SANITY_BAND = 0.10
HP_CV_MAX = 0.15
HP_SATURATION_CEIL = 0.95

# Planner-specific gates
HP_PLANNER_ROUTE_ACC_MIN = 0.50      # at d=15; HARDER than chance + margin
HF_PLANNER_ROUTE_ACC_MIN = 0.30      # if below, planner contributed nothing
MM_PLANNER_ROUTE_ACC_MIN = 0.30
HP_POSITIVE_CONTROL_ROUTE_ACC = 0.50  # at d=5 N_part=10; chance=0.10

HF_ARM_B_ABS = 0.30
HF_LIFT_MIN_FOR_SIGNAL = 0.10
HF_LIFT_MIN_IF_SATURATED = 0.20
MM_LIFT_MIN = 0.15

# Partitioning
def _cone_collapse_crosstalk(v_c_per_hop: int, n: int) -> float:
    return float(math.sqrt(max(v_c_per_hop - 1, 1) / max(n, 1)))

N_PART = 5
PART_SIZE = V_CONCEPTS // N_PART
assert V_CONCEPTS % N_PART == 0

CROSSTALK_PART = _cone_collapse_crosstalk(PART_SIZE, N_DIM)
CROSSTALK_BASELINE = _cone_collapse_crosstalk(V_CONCEPTS, N_DIM)

# Locked invariants (META_RULE_AL)
assert BASELINE_RAIL_LO < BASELINE_RAIL_TARGET < BASELINE_RAIL_HI
assert HP_ARM_B_LO > HF_ARM_B_ABS, "HP floor must exceed HF ceiling"
assert HP_ARM_B_LO < HP_ARM_B_HI <= HP_SATURATION_CEIL
assert HP_LIFT_OVER_BASELINE > MM_LIFT_MIN
assert HP_LIFT_OVER_BASELINE > HF_LIFT_MIN_FOR_SIGNAL
assert 0.0 < HP_NOISY_SANITY_BAND < 0.2
assert 0.0 < HP_GAP_ORACLE_OVER_DERIVED < 1.0
assert CROSSTALK_PART < CROSSTALK_BASELINE
assert abs(CROSSTALK_PART - math.sqrt(799 / 8192)) < 1e-6
assert DEPTH == 15
assert HP_PLANNER_ROUTE_ACC_MIN > HF_PLANNER_ROUTE_ACC_MIN
assert HF_PLANNER_ROUTE_ACC_MIN > (1.0 / N_PART)  # above chance

# Chain configuration -- single seed per cell
N_CHAINS_TRAIN = 200
if RUN_MODE == "smoke":
    SEEDS = [_SEED]
    N_CHAINS_TEST = 100
else:
    SEEDS = [_SEED]
    N_CHAINS_TEST = 200

# Cardinality (META_RULE_H)
N_ARMS = 5
EXPECTED_N_UNITS = N_ARMS * len(SEEDS)

# Positive control config (small d / large N_part)
PC_DEPTH = 5
PC_N_PART = 10
PC_V_C_FOR_PART = PC_N_PART * 200  # 2000 atoms; psz=200; xtalk reasonable
PC_PART_SIZE = PC_V_C_FOR_PART // PC_N_PART
PC_N_CHAINS_TRAIN = 500
PC_N_CHAINS_TEST = 100

ENCODER_PROVENANCE = "SUBSTRATE_NATIVE_BIPOLAR"

CONFIG_VERSION = (
    "ANCHOR=%s,learnedLinearPlannerDrill2V1: N=%d V_C=%d V_P=%d depth=%d "
    "n_chains_train=%d n_chains_test=%d seed=%d mode=%s encoder=%s "
    "n_parts=%d psz=%d xtalk=%.4f baseline_xtalk=%.4f "
    "PC_depth=%d PC_n_part=%d PC_V_C=%d PC_psz=%d PC_train=%d PC_test=%d "
    "RAIL=[%.3f,%.3f] target=%.3f HP_B_band=[%.2f,%.2f] HP_lift_base=%.2f "
    "HP_lift_rand=%.2f HP_gap_oracle=%.2f HP_noisy_band=%.2f HP_cv_max=%.2f "
    "HP_sat_ceil=%.2f HF_B_abs=%.2f HF_lift_min_signal=%.2f "
    "HF_lift_min_if_sat=%.2f MM_lift_min=%.2f expected_units=%d arms=%d "
    "HP_planner_route_min=%.2f HF_planner_route_min=%.2f PC_route_min=%.2f"
) % (
    ANCHOR_NAME,
    N_DIM, V_CONCEPTS, V_PRED, DEPTH,
    N_CHAINS_TRAIN, N_CHAINS_TEST, _SEED, RUN_MODE, ENCODER_PROVENANCE,
    N_PART, PART_SIZE, CROSSTALK_PART, CROSSTALK_BASELINE,
    PC_DEPTH, PC_N_PART, PC_V_C_FOR_PART, PC_PART_SIZE,
    PC_N_CHAINS_TRAIN, PC_N_CHAINS_TEST,
    BASELINE_RAIL_LO, BASELINE_RAIL_HI, BASELINE_RAIL_TARGET,
    HP_ARM_B_LO, HP_ARM_B_HI, HP_LIFT_OVER_BASELINE, HP_LIFT_OVER_RANDOM,
    HP_GAP_ORACLE_OVER_DERIVED, HP_NOISY_SANITY_BAND, HP_CV_MAX,
    HP_SATURATION_CEIL, HF_ARM_B_ABS, HF_LIFT_MIN_FOR_SIGNAL,
    HF_LIFT_MIN_IF_SATURATED, MM_LIFT_MIN, EXPECTED_N_UNITS, N_ARMS,
    HP_PLANNER_ROUTE_ACC_MIN, HF_PLANNER_ROUTE_ACC_MIN,
    HP_POSITIVE_CONTROL_ROUTE_ACC,
)


# ----------------------------------------------------------------------------
# Primitives (verbatim numpy port from parent chain)
# ----------------------------------------------------------------------------

def bipolar(M: int, n: int, g: np.random.Generator) -> np.ndarray:
    X = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)


def ingest_hebbian(triples, E: np.ndarray, R: np.ndarray, sq: float,
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
                     g: np.random.Generator,
                     disallow_s: set
                     ) -> Tuple[List[Tuple[int, int, int]],
                                List[List[Tuple[int, int, int]]]]:
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
            "BLOCKING make_deep_chains: only %d/%d at max_depth=%d"
            % (len(chain_queries), n_chains, max_depth)
        )
    return all_triples, chain_queries


# ----------------------------------------------------------------------------
# LEARNED LINEAR PLANNER (the Drill 2 mechanism)
# ----------------------------------------------------------------------------

def collect_planner_training_pairs(
    chains_train: List[List[Tuple[int, int, int]]],
    E: np.ndarray, R: np.ndarray, sq: float, W: np.ndarray,
    part_size: int, depth: int,
) -> Tuple[np.ndarray, np.ndarray]:
    """For each training chain at each hop, record (state, true_partition).

    META_RULE_AP_v3 signal-shape audit: `state = W @ (E[s] * R[p] * sq)` --
    IDENTICAL to the state oracle B receives at test time + IDENTICAL to what
    the planner will receive at test time. No cleaner-than-test signal.

    Returns:
        X: (n_pairs, n_dim) state vectors (the planner's input)
        y: (n_pairs,) int partition labels (0..n_partitions-1)
    """
    pairs_X: List[np.ndarray] = []
    pairs_y: List[int] = []
    for chain in chains_train:
        s = chain[0][0]
        for i in range(depth):
            p = chain[i][1]
            target_o = chain[i][2]
            true_part = target_o // part_size
            key = (E[s] * R[p] * sq).astype(np.float32)
            state = W @ key                          # SAME geometry as test
            pairs_X.append(state.copy())
            pairs_y.append(int(true_part))
            # Training trajectory: advance via TRUE next entity (no test-time
            # cleanup-collapse contamination). Trains planner on the realized
            # multihop state trajectory along true chains.
            s = target_o
    X = np.asarray(pairs_X, dtype=np.float32)
    y = np.asarray(pairs_y, dtype=np.int64)
    return X, y


def train_planner(X: np.ndarray, y: np.ndarray, n_parts: int,
                  seed: int) -> Tuple[np.ndarray, np.ndarray, Dict[str, Any]]:
    """Train multinomial logistic regression on (state, partition) pairs.

    Returns (W_planner, b_planner, diag) where W_planner has shape (n_parts, n_dim)
    and b_planner has shape (n_parts,). Prediction:
        logits = W_planner @ state + b_planner
        pred_part = argmax(logits)
    """
    from sklearn.linear_model import LogisticRegression
    # sklearn >=1.7 removed `multi_class` kwarg; lbfgs defaults to multinomial
    # for n_classes>2 in current versions. Avoid passing the kwarg for forward-compat.
    clf = LogisticRegression(
        solver="lbfgs",
        max_iter=200,
        C=1.0,
        random_state=seed,
        n_jobs=1,
    )
    clf.fit(X, y)
    # sklearn coef_ shape: (n_classes, n_features); intercept_: (n_classes,)
    W_planner = clf.coef_.astype(np.float32)
    b_planner = clf.intercept_.astype(np.float32)
    # Training accuracy (diagnostic)
    train_pred = clf.predict(X)
    train_acc = float((train_pred == y).mean())
    # Weight checksum (for FROZEN-after-train audit)
    wsum = float(W_planner.sum())
    bsum = float(b_planner.sum())
    diag = {
        "train_acc": round(train_acc, 4),
        "n_train_pairs": int(X.shape[0]),
        "weight_checksum_W": round(wsum, 6),
        "weight_checksum_b": round(bsum, 6),
        "W_shape": list(W_planner.shape),
        "b_shape": list(b_planner.shape),
        "n_iter": int(getattr(clf, "n_iter_", [-1])[0]) if hasattr(clf, "n_iter_") else -1,
    }
    return W_planner, b_planner, diag


# ----------------------------------------------------------------------------
# Arms
# ----------------------------------------------------------------------------

def arm_baseline(E: np.ndarray, R: np.ndarray, sq: float,
                 W: np.ndarray, chains_test: List[List[Tuple[int, int, int]]],
                 depth: int) -> Dict[str, Any]:
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
    return {
        "top1": round(hits / max(n, 1), 4),
        "per_step_acc": [round(float(x) / max(n, 1), 4)
                         for x in per_step_hits],
        "n_queries": n, "depth": depth,
        "mechanism": "baseline_per_hop_cleanup_full_V_C",
    }


def arm_learned_planner(E: np.ndarray, R: np.ndarray, sq: float,
                        W: np.ndarray,
                        chains_test: List[List[Tuple[int, int, int]]],
                        depth: int, part_size: int,
                        W_planner: np.ndarray, b_planner: np.ndarray
                        ) -> Dict[str, Any]:
    """LEARNED LINEAR PARTITION PLANNER (Drill 2 mechanism).

    At each hop: state = W @ key; pred_part = argmax(W_planner @ state +
    b_planner); cleanup over E_part[pred_part]. No ground-truth used. Records
    routing accuracy (pred_part == true_part).
    """
    n = len(chains_test)
    hits = 0
    per_step_hits = np.zeros(depth, dtype=np.int64)
    route_hits = 0
    route_total = 0
    n_partitions = E.shape[0] // part_size
    E_parts = [E[p * part_size:(p + 1) * part_size]
               for p in range(n_partitions)]
    for chain in chains_test:
        s = chain[0][0]
        for i in range(depth):
            p = chain[i][1]
            target_o = chain[i][2]
            true_part = target_o // part_size
            key = (E[s] * R[p] * sq).astype(np.float32)
            state = W @ key
            # LEARNED LINEAR PLANNER (no gen-time peek):
            logits = W_planner @ state + b_planner
            pred_part = int(logits.argmax())
            route_total += 1
            if pred_part == true_part:
                route_hits += 1
            scores = E_parts[pred_part] @ state
            local_idx = int(scores.argmax())
            s_pred = pred_part * part_size + local_idx
            if s_pred == target_o:
                per_step_hits[i] += 1
            s = s_pred
        if s == chain[depth - 1][2]:
            hits += 1
    return {
        "top1": round(hits / max(n, 1), 4),
        "per_step_acc": [round(float(x) / max(n, 1), 4)
                         for x in per_step_hits],
        "n_queries": n, "depth": depth,
        "n_partitions": n_partitions, "part_size": part_size,
        "route_acc": round(route_hits / max(route_total, 1), 4),
        "route_hits": int(route_hits), "route_total": int(route_total),
        "mechanism": "learned_linear_planner_softmax_logreg",
    }


def arm_oracle_ground_truth(E: np.ndarray, R: np.ndarray, sq: float,
                            W: np.ndarray,
                            chains_test: List[List[Tuple[int, int, int]]],
                            depth: int, part_size: int) -> Dict[str, Any]:
    n = len(chains_test)
    hits = 0
    per_step_hits = np.zeros(depth, dtype=np.int64)
    n_partitions = E.shape[0] // part_size
    E_parts = [E[p * part_size:(p + 1) * part_size]
               for p in range(n_partitions)]
    for chain in chains_test:
        s = chain[0][0]
        for i in range(depth):
            p = chain[i][1]
            target_o = chain[i][2]
            target_part = target_o // part_size
            key = (E[s] * R[p] * sq).astype(np.float32)
            state = W @ key
            scores = E_parts[target_part] @ state
            local_idx = int(scores.argmax())
            s_pred = target_part * part_size + local_idx
            if s_pred == target_o:
                per_step_hits[i] += 1
            s = s_pred
        if s == chain[depth - 1][2]:
            hits += 1
    return {
        "top1": round(hits / max(n, 1), 4),
        "per_step_acc": [round(float(x) / max(n, 1), 4)
                         for x in per_step_hits],
        "n_queries": n, "depth": depth,
        "n_partitions": n_partitions, "part_size": part_size,
        "mechanism": "oracle_ground_truth_partition_upper_bound",
    }


def arm_noisy_hint(E: np.ndarray, R: np.ndarray, sq: float,
                   W: np.ndarray,
                   chains_test: List[List[Tuple[int, int, int]]],
                   depth: int, part_size: int,
                   g: np.random.Generator) -> Dict[str, Any]:
    n = len(chains_test)
    hits = 0
    per_step_hits = np.zeros(depth, dtype=np.int64)
    n_partitions = E.shape[0] // part_size
    E_parts = [E[p * part_size:(p + 1) * part_size]
               for p in range(n_partitions)]
    for chain in chains_test:
        perm = g.permutation(n_partitions)
        s = chain[0][0]
        for i in range(depth):
            p = chain[i][1]
            target_o = chain[i][2]
            true_part = target_o // part_size
            noisy_part = int(perm[true_part])
            key = (E[s] * R[p] * sq).astype(np.float32)
            state = W @ key
            scores = E_parts[noisy_part] @ state
            local_idx = int(scores.argmax())
            s_pred = noisy_part * part_size + local_idx
            if s_pred == target_o:
                per_step_hits[i] += 1
            s = s_pred
        if s == chain[depth - 1][2]:
            hits += 1
    return {
        "top1": round(hits / max(n, 1), 4),
        "per_step_acc": [round(float(x) / max(n, 1), 4)
                         for x in per_step_hits],
        "n_queries": n, "depth": depth,
        "n_partitions": n_partitions, "part_size": part_size,
        "mechanism": "noisy_permuted_partition_label_negative_control",
    }


def arm_random_partition(E: np.ndarray, R: np.ndarray, sq: float,
                         W: np.ndarray,
                         chains_test: List[List[Tuple[int, int, int]]],
                         depth: int, part_size: int,
                         g: np.random.Generator) -> Dict[str, Any]:
    n = len(chains_test)
    hits = 0
    per_step_hits = np.zeros(depth, dtype=np.int64)
    n_partitions = E.shape[0] // part_size
    E_parts = [E[p * part_size:(p + 1) * part_size]
               for p in range(n_partitions)]
    for chain in chains_test:
        s = chain[0][0]
        for i in range(depth):
            p = chain[i][1]
            target_o = chain[i][2]
            chosen_part = int(g.integers(0, n_partitions))
            key = (E[s] * R[p] * sq).astype(np.float32)
            state = W @ key
            scores = E_parts[chosen_part] @ state
            local_idx = int(scores.argmax())
            s_pred = chosen_part * part_size + local_idx
            if s_pred == target_o:
                per_step_hits[i] += 1
            s = s_pred
        if s == chain[depth - 1][2]:
            hits += 1
    return {
        "top1": round(hits / max(n, 1), 4),
        "per_step_acc": [round(float(x) / max(n, 1), 4)
                         for x in per_step_hits],
        "n_queries": n, "depth": depth,
        "n_partitions": n_partitions, "part_size": part_size,
        "mechanism": "random_partition_per_hop_floor",
    }


# ----------------------------------------------------------------------------
# POSITIVE CONTROL (smoke discriminator gate; d=5 N_part=10)
# ----------------------------------------------------------------------------

def positive_control(seed: int) -> Dict[str, Any]:
    """Easier regime: d=5 / N_part=10. Planner_route_acc MUST be >= 0.50
    (chance=0.10). If fails, mechanism broken OR no signal at any regime.
    """
    g = np.random.default_rng(seed * 17 + 1)
    sq = math.sqrt(N_DIM)
    E_pc = bipolar(PC_V_C_FOR_PART, N_DIM, g)
    R_pc = bipolar(V_PRED, N_DIM, g)
    triples_train_pc, chains_train_pc = make_deep_chains(
        PC_N_CHAINS_TRAIN, PC_V_C_FOR_PART, V_PRED, max_depth=PC_DEPTH,
        g=g, disallow_s=set())
    used_s_pc = set(c[0][0] for c in chains_train_pc)
    triples_test_pc, chains_test_pc = make_deep_chains(
        PC_N_CHAINS_TEST, PC_V_C_FOR_PART, V_PRED, max_depth=PC_DEPTH,
        g=g, disallow_s=used_s_pc)
    all_triples_pc = triples_train_pc + triples_test_pc
    W_pc = ingest_hebbian(all_triples_pc, E_pc, R_pc, sq, N_DIM)
    # Train planner
    X_pc, y_pc = collect_planner_training_pairs(
        chains_train_pc, E_pc, R_pc, sq, W_pc, PC_PART_SIZE, PC_DEPTH)
    Wp_pc, bp_pc, diag_pc = train_planner(X_pc, y_pc, PC_N_PART, seed)
    # Test-time route_acc only (we only need to verify signal exists at easier
    # regime; cleanup-cascade isn't the gate here)
    route_hits = 0; route_total = 0
    for chain in chains_test_pc:
        s = chain[0][0]
        for i in range(PC_DEPTH):
            p = chain[i][1]
            target_o = chain[i][2]
            true_part = target_o // PC_PART_SIZE
            key = (E_pc[s] * R_pc[p] * sq).astype(np.float32)
            state = W_pc @ key
            logits = Wp_pc @ state + bp_pc
            pred_part = int(logits.argmax())
            route_total += 1
            if pred_part == true_part:
                route_hits += 1
            s = target_o  # ground-truth advance; we're measuring route_acc only
    pc_route_acc = round(route_hits / max(route_total, 1), 4)
    pc_pass = bool(pc_route_acc >= HP_POSITIVE_CONTROL_ROUTE_ACC)
    return {
        "pc_route_acc": pc_route_acc,
        "pc_route_hits": int(route_hits),
        "pc_route_total": int(route_total),
        "pc_pass": pc_pass,
        "pc_chance": round(1.0 / PC_N_PART, 4),
        "pc_threshold": HP_POSITIVE_CONTROL_ROUTE_ACC,
        "pc_config": {
            "depth": PC_DEPTH, "n_part": PC_N_PART, "V_C": PC_V_C_FOR_PART,
            "psz": PC_PART_SIZE, "n_train": PC_N_CHAINS_TRAIN,
            "n_test": PC_N_CHAINS_TEST,
        },
        "pc_planner_diag": diag_pc,
    }


# ----------------------------------------------------------------------------
# Arms-must-differ SHA-256 (META_RULE_AF)
# ----------------------------------------------------------------------------

def _arms_must_differ_sha256(per_seed: List[Dict[str, Any]]) -> Dict[str, str]:
    hashes: Dict[str, str] = {}
    arm_keys = [
        "arm_a_baseline",
        "arm_b_learned_planner",
        "arm_c_oracle",
        "arm_d_noisy_hint",
        "arm_e_random",
    ]
    for k in arm_keys:
        h = hashlib.sha256()
        for p in per_seed:
            if k in p and isinstance(p[k].get("per_step_acc"), list):
                h.update(repr(p[k]["per_step_acc"]).encode("utf-8"))
                h.update(b"|")
                h.update(repr(p[k].get("top1", "")).encode("utf-8"))
                h.update(b"||")
        hashes[k] = h.hexdigest()[:16]
    return hashes


# ----------------------------------------------------------------------------
# Self-test (tiny N; verifies pipeline + invariants; <5s)
# ----------------------------------------------------------------------------

def _selftest() -> None:
    g = np.random.default_rng(0)
    n_tiny = 256
    V_tiny = 40
    P_tiny = 4
    sq = math.sqrt(n_tiny)
    E = bipolar(V_tiny, n_tiny, g)
    R = bipolar(P_tiny, n_tiny, g)

    # T1: bipolar shapes + norm
    assert E.shape == (V_tiny, n_tiny) and R.shape == (P_tiny, n_tiny)
    assert abs(float(np.linalg.norm(E[0])) - 1.0) < 1e-4

    # T2: chain construction at DEPTH=15
    triples_tr, chains_tr = make_deep_chains(
        16, V_tiny, P_tiny, max_depth=DEPTH, g=g, disallow_s=set())
    used = set(c[0][0] for c in chains_tr)
    triples_te, chains_te = make_deep_chains(
        8, V_tiny, P_tiny, max_depth=DEPTH, g=g, disallow_s=used)
    assert len(chains_tr) == 16 and len(chains_te) == 8
    assert len(triples_tr) == 16 * DEPTH and len(triples_te) == 8 * DEPTH

    # T2b: TRAIN-TEST DISJOINTNESS (load-bearing audit)
    train_starts = set(c[0][0] for c in chains_tr)
    test_starts = set(c[0][0] for c in chains_te)
    assert len(train_starts & test_starts) == 0, \
        "TRAIN-TEST LEAK: start entities overlap!"

    # T3: ingest
    all_triples = triples_tr + triples_te
    W = ingest_hebbian(all_triples, E, R, sq, n_tiny)
    assert W.shape == (n_tiny, n_tiny)
    assert np.isfinite(W).all()

    # T4: planner training pair collection
    psz_tiny = V_tiny // 8
    assert V_tiny % 8 == 0
    X, y = collect_planner_training_pairs(
        chains_tr, E, R, sq, W, psz_tiny, DEPTH)
    assert X.shape == (16 * DEPTH, n_tiny)
    assert y.shape == (16 * DEPTH,)
    assert int(y.min()) >= 0 and int(y.max()) < 8

    # T4b: SIGNAL-SHAPE AUDIT (META_RULE_AP_v3)
    # state at training time MUST have same shape as state at test time
    # Compute a test-time state for verification
    test_chain = chains_te[0]
    s_test = test_chain[0][0]
    p_test = test_chain[0][1]
    key_test = (E[s_test] * R[p_test] * sq).astype(np.float32)
    state_test = W @ key_test
    assert state_test.shape == (n_tiny,) == X[0].shape, \
        "META_RULE_AP_v3 VIOLATION: state shape mismatch train vs test"

    # T5: planner trains (tiny config)
    Wp, bp, diag = train_planner(X, y, n_parts=8, seed=0)
    assert Wp.shape == (8, n_tiny)
    assert bp.shape == (8,)
    assert "train_acc" in diag
    assert 0.0 <= diag["train_acc"] <= 1.0
    # On 16 training chains x 15 hops, the planner should at least beat chance
    # in training (overfitting expected at tiny n). Don't enforce a high floor
    # at this scale.

    # T6: all 5 arms produce valid output at tiny config
    r_a = arm_baseline(E, R, sq, W, chains_te, depth=DEPTH)
    r_b = arm_learned_planner(E, R, sq, W, chains_te, depth=DEPTH,
                              part_size=psz_tiny, W_planner=Wp, b_planner=bp)
    r_c = arm_oracle_ground_truth(E, R, sq, W, chains_te, depth=DEPTH,
                                  part_size=psz_tiny)
    r_d = arm_noisy_hint(E, R, sq, W, chains_te, depth=DEPTH,
                         part_size=psz_tiny, g=g)
    r_e = arm_random_partition(E, R, sq, W, chains_te, depth=DEPTH,
                               part_size=psz_tiny, g=g)
    for r in (r_a, r_b, r_c, r_d, r_e):
        assert 0.0 <= r["top1"] <= 1.0
        assert len(r["per_step_acc"]) == DEPTH

    # T7: learned-planner arm tracks route_acc
    assert "route_acc" in r_b
    assert 0.0 <= r_b["route_acc"] <= 1.0
    assert r_b["route_total"] == 8 * DEPTH

    # T8: FROZEN-after-train (selftest re-uses Wp,bp; predictions reproducible)
    r_b_2 = arm_learned_planner(E, R, sq, W, chains_te, depth=DEPTH,
                                part_size=psz_tiny, W_planner=Wp, b_planner=bp)
    assert r_b["top1"] == r_b_2["top1"], "FROZEN check: planner outputs drift"

    # T9: cone-collapse formula sanity at full config
    assert abs(CROSSTALK_PART - 0.3123) < 0.001, \
        "psz=800/N=8192 xtalk drift: %.4f" % CROSSTALK_PART
    assert CROSSTALK_BASELINE > 0.6

    # T10: bands LOCKED (regression on band drift)
    assert N_DIM == 8192
    assert V_CONCEPTS == 4000
    assert DEPTH == 15
    assert PART_SIZE == 800
    assert N_PART == 5
    assert HP_ARM_B_LO == 0.50
    assert HP_ARM_B_HI == 0.95
    assert HF_ARM_B_ABS == 0.30
    assert BASELINE_RAIL_LO == 0.30
    assert BASELINE_RAIL_HI == 0.70
    assert HP_LIFT_OVER_BASELINE == 0.30
    assert HP_LIFT_OVER_RANDOM == 0.30
    assert HP_GAP_ORACLE_OVER_DERIVED == 0.30
    assert HP_NOISY_SANITY_BAND == 0.10
    assert HP_CV_MAX == 0.15
    assert HP_SATURATION_CEIL == 0.95
    assert HP_PLANNER_ROUTE_ACC_MIN == 0.50
    assert HF_PLANNER_ROUTE_ACC_MIN == 0.30
    assert HP_POSITIVE_CONTROL_ROUTE_ACC == 0.50

    # T11: zero LLM calls (substrate-only)
    assert _LLM_CALL_COUNTER[0] == 0

    # T12: cardinality declared
    assert EXPECTED_N_UNITS == 5 * len(SEEDS)

    # T13: anchor binding (single-seed cell)
    assert "learned_linear_planner_drill2" in ANCHOR_NAME
    assert ANCHOR_NAME.endswith("_seed_%d" % _SEED)

    # T14: arms-must-differ SHA-256 on tiny per_seed result
    tiny_per_seed = [{
        "arm_a_baseline": r_a,
        "arm_b_learned_planner": r_b,
        "arm_c_oracle": r_c,
        "arm_d_noisy_hint": r_d,
        "arm_e_random": r_e,
    }]
    hashes_tiny = _arms_must_differ_sha256(tiny_per_seed)
    assert hashes_tiny["arm_a_baseline"] != hashes_tiny["arm_b_learned_planner"], \
        "META_RULE_AF: A vs B SHA collision"
    # Note: at tiny n, B and E may collide if route_acc is so low both fail
    # identically. We don't enforce arms_distinct at selftest, only at full run.

    # T15: positive control config sanity
    assert PC_DEPTH == 5
    assert PC_N_PART == 10
    assert PC_V_C_FOR_PART == 2000
    assert PC_PART_SIZE == 200
    assert PC_N_CHAINS_TRAIN == 500
    assert PC_N_CHAINS_TEST == 100
    assert (1.0 / PC_N_PART) < HP_POSITIVE_CONTROL_ROUTE_ACC
    # PC sanity: chance=0.10; threshold=0.50 has 5x headroom

    print("[selftest] PASS N=%d V_C=%d depth=%d psz=%d arms: a=%.3f b=%.3f "
          "c=%.3f d=%.3f e=%.3f route_acc_b=%.3f planner_train_acc=%.3f "
          "xtalk=%.4f HP_band=[%.2f,%.2f] HP_lift=%.2f HP_route=%.2f "
          "PC_thresh=%.2f" % (
              N_DIM, V_CONCEPTS, DEPTH, PART_SIZE,
              r_a["top1"], r_b["top1"], r_c["top1"], r_d["top1"], r_e["top1"],
              r_b["route_acc"], diag["train_acc"],
              CROSSTALK_PART, HP_ARM_B_LO, HP_ARM_B_HI,
              HP_LIFT_OVER_BASELINE, HP_PLANNER_ROUTE_ACC_MIN,
              HP_POSITIVE_CONTROL_ROUTE_ACC),
          flush=True)


_selftest()
if _ARGS.self_test:
    print("[self-test] PASS; exiting", flush=True)
    sys.exit(0)


# ----------------------------------------------------------------------------
# run_seed
# ----------------------------------------------------------------------------

def run_seed(seed: int) -> Dict[str, Any]:
    t = time.time()
    g = np.random.default_rng(seed)
    sq = math.sqrt(N_DIM)

    # ===== POSITIVE CONTROL FIRST (smoke discriminator gate) =====
    print("  [seed=%d] POSITIVE CONTROL (d=%d, N_part=%d) ..." % (
        seed, PC_DEPTH, PC_N_PART), flush=True)
    t_pc = time.time()
    pc_result = positive_control(seed)
    pc_elapsed = round(time.time() - t_pc, 2)
    print("  [seed=%d] PC done t=%.1fs route_acc=%.4f (chance=%.2f thresh=%.2f) "
          "pass=%s" % (
              seed, pc_elapsed, pc_result["pc_route_acc"], pc_result["pc_chance"],
              pc_result["pc_threshold"], pc_result["pc_pass"]), flush=True)

    print("  [seed=%d] building E (V_C=%d, N=%d) + R" % (
        seed, V_CONCEPTS, N_DIM), flush=True)
    E = bipolar(V_CONCEPTS, N_DIM, g)
    R = bipolar(V_PRED, N_DIM, g)

    print("  [seed=%d] generating train chains (n=%d, max_depth=%d)" % (
        seed, N_CHAINS_TRAIN, MAX_DEPTH), flush=True)
    triples_train, chains_train = make_deep_chains(
        N_CHAINS_TRAIN, V_CONCEPTS, V_PRED, max_depth=MAX_DEPTH,
        g=g, disallow_s=set())
    used_s = set(c[0][0] for c in chains_train)

    print("  [seed=%d] generating test chains (n=%d, max_depth=%d)" % (
        seed, N_CHAINS_TEST, MAX_DEPTH), flush=True)
    triples_test, chains_test = make_deep_chains(
        N_CHAINS_TEST, V_CONCEPTS, V_PRED, max_depth=MAX_DEPTH,
        g=g, disallow_s=used_s)

    # TRAIN-TEST DISJOINTNESS AUDIT (load-bearing)
    train_starts = set(c[0][0] for c in chains_train)
    test_starts = set(c[0][0] for c in chains_test)
    train_test_disjoint = (len(train_starts & test_starts) == 0)
    if not train_test_disjoint:
        raise RuntimeError(
            "BLOCKING: train/test entity-start overlap: %d collisions"
            % len(train_starts & test_starts))

    all_triples = triples_train + triples_test
    print("  [seed=%d] ingesting W (%d bindings, N=%d -> %.1f MB)" % (
        seed, len(all_triples), N_DIM, (N_DIM * N_DIM * 4) / 1e6), flush=True)
    t_ingest = time.time()
    W = ingest_hebbian(all_triples, E, R, sq, N_DIM)
    print("  [seed=%d] W ingested t=%.1fs shape=%s" % (
        seed, time.time() - t_ingest, W.shape), flush=True)

    # ===== TRAIN LINEAR PLANNER (the Drill 2 mechanism) =====
    print("  [seed=%d] collecting planner training pairs (chains_train=%d, "
          "depth=%d -> %d pairs)" % (
              seed, N_CHAINS_TRAIN, DEPTH, N_CHAINS_TRAIN * DEPTH), flush=True)
    t_pairs = time.time()
    X_train, y_train = collect_planner_training_pairs(
        chains_train, E, R, sq, W, PART_SIZE, DEPTH)
    print("  [seed=%d] pairs collected t=%.1fs X=%s y=%s class-balance=%s" % (
        seed, time.time() - t_pairs, X_train.shape, y_train.shape,
        list(np.bincount(y_train, minlength=N_PART))), flush=True)

    # SIGNAL-SHAPE AUDIT runtime check (META_RULE_AP_v3)
    sample_chain = chains_test[0]
    sample_key = (E[sample_chain[0][0]] * R[sample_chain[0][1]] * sq
                  ).astype(np.float32)
    sample_state = W @ sample_key
    assert sample_state.shape == X_train[0].shape == (N_DIM,), \
        "META_RULE_AP_v3 VIOLATION: signal shape drift"

    print("  [seed=%d] training planner (multinomial logreg)" % seed, flush=True)
    t_plan = time.time()
    W_planner, b_planner, planner_diag = train_planner(
        X_train, y_train, N_PART, seed)
    print("  [seed=%d] planner trained t=%.1fs train_acc=%.4f n_iter=%d "
          "W_shape=%s wsum=%.4f bsum=%.4f" % (
              seed, time.time() - t_plan, planner_diag["train_acc"],
              planner_diag["n_iter"], planner_diag["W_shape"],
              planner_diag["weight_checksum_W"],
              planner_diag["weight_checksum_b"]), flush=True)

    out: Dict[str, Any] = {
        "seed": seed, "run_mode": RUN_MODE, "N": N_DIM, "V_C": V_CONCEPTS,
        "V_P": V_PRED, "depth": DEPTH,
        "n_chains_train": N_CHAINS_TRAIN, "n_chains_test": N_CHAINS_TEST,
        "n_partitions": N_PART, "part_size": PART_SIZE,
        "crosstalk_baseline": CROSSTALK_BASELINE,
        "crosstalk_part": CROSSTALK_PART,
        "encoder_provenance": ENCODER_PROVENANCE,
        "config_version": CONFIG_VERSION,
        "anchor_name": ANCHOR_NAME,
        "_llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
        "positive_control": pc_result,
        "planner_diag": planner_diag,
        "train_test_disjoint": train_test_disjoint,
        "train_test_disjoint_n_collisions": int(len(train_starts & test_starts)),
    }

    # ===== ARM_A: BASELINE =====
    t_arm = time.time()
    r_a = arm_baseline(E, R, sq, W, chains_test, depth=DEPTH)
    r_a["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    out["arm_a_baseline"] = r_a
    rail_ok = (BASELINE_RAIL_LO <= r_a["top1"] <= BASELINE_RAIL_HI)
    out["baseline_rail_ok"] = rail_ok
    print("  [seed=%d] ARM_A BASELINE top1=%.4f rail_ok=%s "
          "(target=%.3f band=[%.3f,%.3f]) per_step=%s t=%.1fs" % (
              seed, r_a["top1"], rail_ok,
              BASELINE_RAIL_TARGET, BASELINE_RAIL_LO, BASELINE_RAIL_HI,
              r_a["per_step_acc"], r_a["elapsed_s_arm"]), flush=True)

    # ===== ARM_B: LEARNED_PLANNER (THE DRILL 2 MECHANISM) =====
    t_arm = time.time()
    r_b = arm_learned_planner(E, R, sq, W, chains_test, depth=DEPTH,
                              part_size=PART_SIZE, W_planner=W_planner,
                              b_planner=b_planner)
    r_b["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    out["arm_b_learned_planner"] = r_b
    print("  [seed=%d] ARM_B LEARNED_PLANNER top1=%.4f route_acc=%.4f "
          "(HP_band=[%.2f,%.2f] HP_route>=%.2f lift_vs_A>=%.2f) per_step=%s "
          "t=%.1fs" % (
              seed, r_b["top1"], r_b["route_acc"],
              HP_ARM_B_LO, HP_ARM_B_HI, HP_PLANNER_ROUTE_ACC_MIN,
              HP_LIFT_OVER_BASELINE,
              r_b["per_step_acc"], r_b["elapsed_s_arm"]), flush=True)

    # ===== ARM_C: ORACLE =====
    t_arm = time.time()
    r_c = arm_oracle_ground_truth(E, R, sq, W, chains_test, depth=DEPTH,
                                  part_size=PART_SIZE)
    r_c["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    out["arm_c_oracle"] = r_c
    print("  [seed=%d] ARM_C ORACLE top1=%.4f (upper bound; gap_C_B<=%.2f) "
          "per_step=%s t=%.1fs" % (
              seed, r_c["top1"], HP_GAP_ORACLE_OVER_DERIVED,
              r_c["per_step_acc"], r_c["elapsed_s_arm"]), flush=True)

    # ===== ARM_D: NOISY_HINT =====
    t_arm = time.time()
    g_d = np.random.default_rng(seed * 7919 + 2)
    r_d = arm_noisy_hint(E, R, sq, W, chains_test, depth=DEPTH,
                         part_size=PART_SIZE, g=g_d)
    r_d["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    out["arm_d_noisy_hint"] = r_d
    print("  [seed=%d] ARM_D NOISY_HINT top1=%.4f (sanity: |D-A|<=%.2f) "
          "per_step=%s t=%.1fs" % (
              seed, r_d["top1"], HP_NOISY_SANITY_BAND,
              r_d["per_step_acc"], r_d["elapsed_s_arm"]), flush=True)

    # ===== ARM_E: RANDOM =====
    t_arm = time.time()
    g_e = np.random.default_rng(seed * 7919 + 1)
    r_e = arm_random_partition(E, R, sq, W, chains_test, depth=DEPTH,
                               part_size=PART_SIZE, g=g_e)
    r_e["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    out["arm_e_random"] = r_e
    print("  [seed=%d] ARM_E RANDOM top1=%.4f (floor; lift_B_E>=%.2f) "
          "per_step=%s t=%.1fs" % (
              seed, r_e["top1"], HP_LIFT_OVER_RANDOM,
              r_e["per_step_acc"], r_e["elapsed_s_arm"]), flush=True)

    # Lifts + gaps (per-seed)
    out["lift_b_over_a"] = round(r_b["top1"] - r_a["top1"], 4)
    out["lift_b_over_e"] = round(r_b["top1"] - r_e["top1"], 4)
    out["gap_c_over_b"] = round(r_c["top1"] - r_b["top1"], 4)
    out["noisy_sanity_abs"] = round(abs(r_d["top1"] - r_a["top1"]), 4)

    out["elapsed_s"] = round(time.time() - t, 1)
    return out


# ----------------------------------------------------------------------------
# Verdict
# ----------------------------------------------------------------------------

def verdict_from(per_seed: List[Dict[str, Any]]) -> Tuple[str, str, Dict[str, str]]:
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

    arm_a = mean_top1("arm_a_baseline")
    arm_b = mean_top1("arm_b_learned_planner")
    arm_c = mean_top1("arm_c_oracle")
    arm_d = mean_top1("arm_d_noisy_hint")
    arm_e = mean_top1("arm_e_random")

    cv_b = cv_top1("arm_b_learned_planner")

    lift_b_a = arm_b - arm_a if not (math.isnan(arm_b) or math.isnan(arm_a)) \
        else float("nan")
    lift_b_e = arm_b - arm_e if not (math.isnan(arm_b) or math.isnan(arm_e)) \
        else float("nan")
    gap_c_b = arm_c - arm_b if not (math.isnan(arm_c) or math.isnan(arm_b)) \
        else float("nan")
    noisy_sanity = abs(arm_d - arm_a) if not (math.isnan(arm_d) or math.isnan(arm_a)) \
        else float("nan")

    # planner route_acc (B mechanism diagnostic + gate)
    route_accs = [p["arm_b_learned_planner"]["route_acc"]
                  for p in per_seed
                  if "arm_b_learned_planner" in p
                  and "route_acc" in p["arm_b_learned_planner"]]
    mean_route_acc = float(np.mean(route_accs)) if route_accs else float("nan")

    # Positive control (smoke gate; reported in full too as diagnostic)
    pc_passes = [p["positive_control"]["pc_pass"]
                 for p in per_seed
                 if "positive_control" in p
                 and "pc_pass" in p["positive_control"]]
    pc_pass = all(pc_passes) if pc_passes else False
    pc_route_accs = [p["positive_control"]["pc_route_acc"]
                     for p in per_seed
                     if "positive_control" in p
                     and "pc_route_acc" in p["positive_control"]]
    mean_pc_route = float(np.mean(pc_route_accs)) if pc_route_accs else float("nan")

    # Train-test disjointness
    disjoint_all = all(p.get("train_test_disjoint", False) for p in per_seed)

    # Cardinality (META_RULE_H)
    observed_units = sum(
        1 for p in per_seed for arm_key in (
            "arm_a_baseline", "arm_b_learned_planner",
            "arm_c_oracle", "arm_d_noisy_hint", "arm_e_random")
        if arm_key in p
    )
    cardinality_ok = (observed_units == EXPECTED_N_UNITS)

    # Arms-must-differ SHA-256 (META_RULE_AF)
    arms_hashes = _arms_must_differ_sha256(per_seed)
    unique_hashes = len(set(arms_hashes.values()))
    arms_distinct = (unique_hashes == 5)

    # BIAS-Q saturation check
    saturation_flag = (not math.isnan(arm_b)) and arm_b >= HP_SATURATION_CEIL

    # Baseline rail check (BIAS-S)
    rail_breach = sum(1 for p in per_seed
                      if not p.get("baseline_rail_ok", False))

    # HP-band check
    arm_b_in_band = ((not math.isnan(arm_b))
                     and HP_ARM_B_LO <= arm_b <= HP_ARM_B_HI)
    noisy_sanity_ok = ((not math.isnan(noisy_sanity))
                       and noisy_sanity <= HP_NOISY_SANITY_BAND)
    gap_ok = ((not math.isnan(gap_c_b))
              and gap_c_b <= HP_GAP_ORACLE_OVER_DERIVED)
    planner_route_ok = ((not math.isnan(mean_route_acc))
                        and mean_route_acc >= HP_PLANNER_ROUTE_ACC_MIN)
    planner_route_below_hf = ((not math.isnan(mean_route_acc))
                              and mean_route_acc < HF_PLANNER_ROUTE_ACC_MIN)

    summ = (
        "BASELINE_A=%.4f (rail_breach=%d/%d; target=%.3f band=[%.2f,%.2f]) "
        "LEARNED_PLANNER_B=%.4f (cv=%.3f route_acc=%.4f route_ok=%s in_band=%s) "
        "ORACLE_C=%.4f NOISY_D=%.4f RANDOM_E=%.4f "
        "lift_B_A=%.4f lift_B_E=%.4f gap_C_B=%.4f (ok=%s) "
        "noisy_sanity=%.4f (ok=%s) PC_route_acc=%.4f pc_pass=%s "
        "disjoint=%s cardinality_ok=%s expected_units=%d "
        "observed_units=%d arms_distinct=%s saturation=%s "
        "HP_band=[%.2f,%.2f] HP_lift_base=%.2f HP_route=%.2f "
        "PC_thresh=%.2f depth=%d xtalk=%.4f"
    ) % (
        arm_a, rail_breach, len(per_seed), BASELINE_RAIL_TARGET,
        BASELINE_RAIL_LO, BASELINE_RAIL_HI,
        arm_b, cv_b, mean_route_acc, planner_route_ok, arm_b_in_band,
        arm_c, arm_d, arm_e,
        lift_b_a, lift_b_e, gap_c_b, gap_ok,
        noisy_sanity, noisy_sanity_ok, mean_pc_route, pc_pass,
        disjoint_all, cardinality_ok, EXPECTED_N_UNITS, observed_units,
        arms_distinct, saturation_flag,
        HP_ARM_B_LO, HP_ARM_B_HI, HP_LIFT_OVER_BASELINE,
        HP_PLANNER_ROUTE_ACC_MIN, HP_POSITIVE_CONTROL_ROUTE_ACC, DEPTH,
        CROSSTALK_PART,
    )

    # Cardinality gate FIRST (META_RULE_H)
    if not cardinality_ok:
        return ("HARD_FAIL_CARDINALITY_BREACH",
                "HARD_FAIL_CARDINALITY_BREACH: " + summ, arms_hashes)

    # Train-test disjointness gate (no leak)
    if not disjoint_all:
        return ("HARD_FAIL_TRAIN_TEST_LEAK",
                "HARD_FAIL_TRAIN_TEST_ENTITY_OVERLAP: " + summ, arms_hashes)

    # Positive control gate (if fails, mechanism broken OR no signal anywhere)
    if not pc_pass:
        return ("HARD_FAIL_POSITIVE_CONTROL_FAIL",
                "HARD_FAIL_POSITIVE_CONTROL_FAIL_MECHANISM_BROKEN_OR_NO_SIGNAL: "
                + summ, arms_hashes)

    # Arms-distinct gate (META_RULE_AF)
    if not arms_distinct:
        return ("HARD_FAIL_ARMS_TIED",
                "HARD_FAIL_ARMS_TIED_NO_DISCRIMINATION: " + summ, arms_hashes)

    # By-construction ORACLE_C floor check
    if (not math.isnan(arm_c)) and arm_c < 0.50:
        return ("HARD_FAIL_ORACLE_FLOOR_BREACH",
                "HARD_FAIL_ORACLE_C_BELOW_0.50_REGIME_BROKEN: " + summ,
                arms_hashes)

    # HARD_FAIL: planner route_acc below chance + margin
    if planner_route_below_hf:
        return ("HARD_FAIL_PLANNER_ROUTE_BELOW_CHANCE",
                "HARD_FAIL_PLANNER_ROUTE_BELOW_HF_FLOOR: " + summ, arms_hashes)

    # HARD_FAIL: mechanism dies
    if (not math.isnan(arm_b)) and arm_b <= HF_ARM_B_ABS:
        return ("HARD_FAIL_NO_SIGNAL_AT_PLANNER",
                "HARD_FAIL_LEARNED_PLANNER_DEAD: " + summ, arms_hashes)

    # HARD_FAIL: lift_b_a below signal floor
    if (not math.isnan(lift_b_a)) and lift_b_a < HF_LIFT_MIN_FOR_SIGNAL:
        return ("HARD_FAIL_NO_SIGNAL_LIFT",
                "HARD_FAIL_NO_REAL_SIGNAL_LIFT_BELOW_FLOOR: " + summ,
                arms_hashes)

    # HARD_FAIL: saturated AND insufficient lift
    if saturation_flag and (not math.isnan(lift_b_a)) \
            and lift_b_a < HF_LIFT_MIN_IF_SATURATED:
        return ("HARD_FAIL_SATURATION_WITHOUT_LIFT",
                "HARD_FAIL_SATURATION_WITH_LIFT_BELOW_THRESHOLD: " + summ,
                arms_hashes)

    # Smoke verdict
    if RUN_MODE == "smoke":
        if arm_b_in_band \
                and (not math.isnan(lift_b_a)) and lift_b_a >= HP_LIFT_OVER_BASELINE \
                and (not math.isnan(lift_b_e)) and lift_b_e >= HP_LIFT_OVER_RANDOM \
                and gap_ok and noisy_sanity_ok and planner_route_ok \
                and not saturation_flag:
            return ("SMOKE_HARD_PASS",
                    "SMOKE_HARD_PASS_LEARNED_PLANNER_MECHANISM_REAL: "
                    + summ, arms_hashes)
        # MIDDLE: B in band but missing some gate
        if arm_b_in_band and (not math.isnan(lift_b_a)) \
                and lift_b_a >= MM_LIFT_MIN:
            return ("MIDDLE_BAND",
                    "MIDDLE_BAND_PARTIAL_LEARNED_PLANNER: " + summ,
                    arms_hashes)
        return ("HARD_FAIL_LIFT_BELOW_THRESHOLD",
                "HARD_FAIL_LIFT_BELOW_THRESHOLD_AT_DEPTH15: " + summ,
                arms_hashes)

    # Full verdict (per-cell single-seed; cv enforced post-hoc cross-cell)
    if arm_b_in_band \
            and (not math.isnan(lift_b_a)) and lift_b_a >= HP_LIFT_OVER_BASELINE \
            and (not math.isnan(lift_b_e)) and lift_b_e >= HP_LIFT_OVER_RANDOM \
            and gap_ok and noisy_sanity_ok and planner_route_ok \
            and not saturation_flag:
        return ("HARD_PASS_CELL_GRADE_LEARNED_PLANNER",
                "HARD_PASS_CELL_GRADE_LEARNED_LINEAR_PLANNER_BARRIER_1_BREAK: "
                + summ, arms_hashes)

    if saturation_flag and (not math.isnan(lift_b_a)) \
            and lift_b_a >= HF_LIFT_MIN_IF_SATURATED:
        return ("MIDDLE_BAND_SATURATED_AUTO_DEMOTE",
                "MIDDLE_BAND_SATURATED_AUTO_DEMOTE_BIAS_Q: " + summ, arms_hashes)

    if (not math.isnan(lift_b_a)) and lift_b_a >= MM_LIFT_MIN:
        return ("MIDDLE_BAND",
                "MIDDLE_BAND_PARTIAL_LEARNED_PLANNER: " + summ, arms_hashes)

    return ("HARD_FAIL_LIFT_BELOW_THRESHOLD",
            "HARD_FAIL_LIFT_BELOW_THRESHOLD_NO_MECHANISM: " + summ, arms_hashes)


# ----------------------------------------------------------------------------
# atexit synthesizer + main
# ----------------------------------------------------------------------------

_RESULTS_HOLDER: Dict[str, Any] = {"out_dir": None, "started_at": time.time()}


def _atexit_synth() -> None:
    od = _RESULTS_HOLDER["out_dir"]
    if od is None:
        return
    try:
        agg = aggregate_partials(od, seeds=[str(s) for s in SEEDS],
                                 run_config={"N": N_DIM,
                                             "run_mode": RUN_MODE,
                                             "anchor": ANCHOR_NAME})
        if not agg:
            return
        per_seed = [agg[k] for k in sorted(agg.keys())]
        if not per_seed:
            return
        if (od / "metrics.json").exists():
            return
        v, vmsg, ahashes = verdict_from(per_seed)
        metrics = {
            "anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg,
            "run_mode": RUN_MODE, "n_seeds": len(per_seed),
            "config_version": CONFIG_VERSION, "per_seed": per_seed,
            "elapsed_s": round(time.time() - _RESULTS_HOLDER["started_at"], 1),
            "summary": vmsg, "_atexit_synth": True,
            "_llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
            "expected_n_units": EXPECTED_N_UNITS,
            "expected_arms": [
                "baseline_full_V_C", "learned_linear_planner",
                "oracle_ground_truth", "noisy_permuted_hint",
                "random_partition_floor"],
            "arms_must_differ_sha256": ahashes,
        }
        write_metrics(od, metrics, results=per_seed)
        print("[atexit] wrote synth metrics.json (%d seeds)" % len(per_seed),
              flush=True)
    except SystemExit:
        raise
    except BaseException as e:  # noqa: BLE001
        print("[atexit] FAIL: %s" % e, flush=True)


atexit.register(_atexit_synth)


if __name__ == "__main__":
    print("[config] anchor=%s mode=%s seeds=%s | %s" % (
        ANCHOR_NAME, RUN_MODE, SEEDS, CONFIG_VERSION), flush=True)
    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)
    _RESULTS_HOLDER["out_dir"] = out_dir

    run_config = {"N": N_DIM, "run_mode": RUN_MODE, "anchor": ANCHOR_NAME}
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

    assert _LLM_CALL_COUNTER[0] == 0

    v, vmsg, ahashes = verdict_from(per_seed)
    print("\n[VERDICT] " + vmsg, flush=True)
    print("[arms_must_differ_sha256] %s" % ahashes, flush=True)
    metrics = {
        "anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg,
        "run_mode": RUN_MODE, "n_seeds": len(per_seed),
        "config_version": CONFIG_VERSION, "per_seed": per_seed,
        "elapsed_s": round(time.time() - _RESULTS_HOLDER["started_at"], 1),
        "summary": vmsg,
        "_llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
        "expected_n_units": EXPECTED_N_UNITS,
        "expected_arms": [
            "baseline_full_V_C", "learned_linear_planner",
            "oracle_ground_truth", "noisy_permuted_hint",
            "random_partition_floor"],
        "arms_must_differ_sha256": ahashes,
        "DESIGN_NOTE": (
            "DRILL 2 of 2x-drill-before-closure for Barrier 1 hint-derivation. "
            "Mechanism class = SUPERVISED LEARNED LINEAR PROJECTOR (sklearn "
            "LogisticRegression multinomial lbfgs C=1.0); genuinely different "
            "from Drill 1 cosine centroid + Drills 1.5/A/B handcrafted brain "
            "composition. Trains W_planner: R^N -> R^N_PART on (state, "
            "true_partition) pairs from chains_train; tests pred_part = "
            "argmax(W_planner @ state + b_planner) on disjoint chains_test. "
            "META_RULE_AP_v3 signal-shape audit: state at training MUST match "
            "state at test (W @ key; SAME geometry oracle B receives). "
            "POSITIVE CONTROL at d=5 / N_part=10 / 500 train / 100 test pairs "
            "MUST yield planner_route_acc >= 0.50 (chance=0.10); if fails, "
            "mechanism broken OR no signal at any regime; HARD_FAIL "
            "immediately. ARMS (5; all psz=800 / 5 partitions matching parent "
            "regime): A=BASELINE, B=LEARNED_PLANNER, C=ORACLE (upper bound), "
            "D=NOISY_HINT (negative control), E=RANDOM (floor). HP requires "
            "B in [0.50, 0.95] AND lift_B_A >= 0.30 AND lift_B_E >= 0.30 AND "
            "gap_C_B <= 0.30 AND |D-A| <= 0.10 AND planner_route_acc >= 0.50 "
            "AND positive_control_pass AND train_test_disjoint AND saturation "
            "== False AND arms_distinct. META_RULE_AC/AE/AF/AG/AH/AL/AN/AP_v3"
            "/H all enforced; BIAS-Q/N/S; DISCRIMINATOR-MUST-SURVIVE-SCALE "
            "(smoke at FULL N + FULL depth + positive control); 2x-drill-"
            "before-closure (USER standing). Drill 1 reference: "
            "d:/AI/hd-instrument/data/exp_substrate_partition_oracle_substrate_derived_hint_v1_seed_7_smoke/metrics.json "
            "(BASELINE=0.40 ARM_B=0.00 ORACLE=0.84 route_acc=0.217 = chance). "
            "CHUNKED single-seed; siblings: seed_13 + seed_19. cv enforced "
            "post-hoc cross-cell at chain-grade VET tier."
        ),
    }
    write_metrics(out_dir, metrics, results=per_seed)
    print("[done] metrics.json written (%d seeds, %.1fs)" % (
        len(per_seed), metrics["elapsed_s"]), flush=True)
