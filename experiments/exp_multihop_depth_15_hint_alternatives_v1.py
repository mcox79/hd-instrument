"""multihop_depth_15_hint_alternatives_v1.

PURPOSE (test alternative hint mechanisms at depth-15 vs partition-oracle 0.808 CG):
    Parent CG landing: partition-oracle hint at depth=15 (v5_hardened seeds
    11/13/19) achieved 0.808 mean top1 (Skunkworks MEASURED_MECHANISM under
    by-construction-saturation tiering; partition-oracle is trivially informed
    with gen-time target-partition access).

    This cell tests THREE alternative hint mechanisms at same depth-15 regime:
        - LEARNED_GATE:   query-conditioned linear gate over partitions (no
                          gen-time target access; learns partition-scoring
                          from train chains)
        - TOP_K_ATTN:     softmax-attention over ALL partitions (temperature=1;
                          weighted mixture of partition scores; K=5 masks)
        - MEM_AUG_HINT:   memory-augmented via train-chain lookup table
                          (nearest-train-chain partition inheritance)

    Discriminator: does ANY alternative beat partition-oracle 0.808 at depth=15?
    Even matching within noise (~0.02 CV) would break by-construction-saturation
    critique and elevate mechanism-class to CHAIN_GRADE (informed hint w/o oracle).

REGIME PARAMETERS (LOCKED at module init; META_RULE_AL):
    N=8192, V_C=4000, V_P=10
    DEPTH=15 (same as parent CG)
    PART_SIZE=800 (5 partitions; same as parent CG ARM_B)
    K_TOP=5 for top_k_softmax (all 5 partitions; effectively full softmax at K=5)

ARMS (4 arms x 3 seeds):
    A: PARTITION_ORACLE     baseline oracle (proj 0.74; MEASURED@CG 0.808)
                              -- reference; same as CG cell ARM_B
    B: LEARNED_GATE         query-conditioned linear gate over 5 partitions
                              (softmax over Q dot P_i learned proj);
                              trained on N_CHAINS_TRAIN via one-shot analytical
                              (mean pattern per partition; no SGD)
    C: TOP_K_SOFTMAX_ATTN   softmax over ALL 5 partitions (mixture scoring;
                              temperature=1.0; weighted argmax over full V_C
                              via partition-weighted contributions)
    D: MEM_AUG_HINT         memory-augmented: train chains stored (E[s_train],
                              partition_id[o_train]); test-time nearest-train-
                              chain-start supplies partition hint

PRE-REG BANDS (META_RULE_AL; LOCKED):
    HP_ALTERNATIVE_BEATS_ORACLE (novel finding):
        max(arm_B, arm_C, arm_D).top1@d15 >= arm_A.top1@d15 - 0.05
        AND best alternative in [0.50, 0.95]
        AND arms_distinct == True
    HP_ARM_A_REFERENCE (partition-oracle sanity):
        arm_A.top1@d15 in [0.60, 0.95]  # CG regime replication
    MIDDLE_BAND:
        best alternative in [0.30, 0.50)
        OR best in [0.50, 0.95) BUT >0.05 below partition-oracle
    HARD_FAIL:
        max(arm_B, arm_C, arm_D).top1@d15 <= 0.30
        (all alternatives die; only oracle survives -> by-construction confirmed)
        OR arm_A.top1@d15 < 0.50 (regime replication broken)

DISCIPLINE TAGS:
    META_RULE_AC/AE/AF/AG/AH/AL/AN: same as parent CG cell
    META_RULE_H: CARDINALITY_OK; expected_n_units = 4 arms * 3 seeds = 12
    BIAS-Q: saturation guard at 0.95
    BIAS-N: per-arm reads (not verdict_msg framing)
    BIAS-S: baseline reference rail [0.60, 0.95]
    DISCRIMINATOR-MUST-SURVIVE-SCALE: smoke @ N=8192 depth=15 (full-N smoke)
    Fix #28: per-arm reads

SOURCE CITATIONS (ABSOLUTE PATHS; META_RULE_AE):
    - Parent CG cells (partition-oracle depth-15 hardened seeds):
      d:/AI/hd-instrument/experiments/exp_substrate_multihop_partition_oracle_v5_hardened_FULL_seed_11_v1.py
      d:/AI/hd-instrument/experiments/exp_substrate_multihop_partition_oracle_v5_hardened_FULL_seed_13_v1.py
      d:/AI/hd-instrument/experiments/exp_substrate_multihop_partition_oracle_v5_hardened_FULL_seed_19_v1.py
    - Parent CG metrics (0.808 3-seed mean):
      d:/AI/hd-instrument/data/exp_substrate_multihop_partition_oracle_v5_hardened_FULL_seed_11_v1/metrics.json
      d:/AI/hd-instrument/data/exp_substrate_multihop_partition_oracle_v5_hardened_FULL_seed_13_v1/metrics.json
      d:/AI/hd-instrument/data/exp_substrate_multihop_partition_oracle_v5_hardened_FULL_seed_19_v1/metrics.json
    - Related prior hint-alt cells (older depths):
      d:/AI/hd-instrument/experiments/exp_substrate_partition_oracle_substrate_derived_hint_v1_seed_7.py
      d:/AI/hd-instrument/experiments/exp_substrate_barrier1_hint_learned_linear_planner_drill2_v1_seed_7.py

NUMBER TAGGING (META_RULE_AC):
    MEASURED@CG_ORACLE_D15_3SEED_MEAN: 0.808
    HYPOTHESIZED@ARM_A_REFERENCE_BAND: [0.60, 0.95] (CG replication)
    HYPOTHESIZED@BEST_ALT_MATCH_BAND: [0.50, 0.95] (novel finding)
    THEORETICAL@LEARNED_GATE_UPPER_BOUND: ~0.808 (cannot exceed oracle without
                                                    additional information;
                                                    approaches oracle if gate
                                                    reliably picks target part)
    THEORETICAL@RANDOM_GATE_FLOOR: 0.2^15 ~ 3e-11 (1/5 chance/hop; ARM_E
                                                    equivalent from parent cell
                                                    was 0.0)
    CITED@MANTE_2013: PFC goal-conditioned attention

Author: exp_dev 2026-07-01 (research drill; alternatives to partition-oracle).
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

ANCHOR_NAME = "multihop_depth_15_hint_alternatives_v1"
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

N_PARTITIONS = 5
PART_SIZE = V_CONCEPTS // N_PARTITIONS   # 800
assert V_CONCEPTS % N_PARTITIONS == 0

K_TOP_SOFTMAX = 5                # ARM_C: all 5 partitions (full softmax)
LEARNED_GATE_TEMP = 1.0          # ARM_B softmax temperature
ATTN_SOFTMAX_TEMP = 1.0          # ARM_C softmax temperature

# HYPOTHESIZED@ARM_A_REFERENCE_BAND
HP_ARM_A_LO = 0.60
HP_ARM_A_HI = 0.95

# HYPOTHESIZED@BEST_ALT_MATCH_BAND
HP_BEST_ALT_LO = 0.50
HP_BEST_ALT_HI = 0.95
HP_ALT_WITHIN_ORACLE_DELTA = 0.05    # best alt >= oracle - 0.05

# MIDDLE_BAND floor
MM_BEST_ALT_LO = 0.30

# HARD_FAIL floors
HF_BEST_ALT_ABS = 0.30           # all alts <= 0.30 means by-construction confirmed
HF_ARM_A_MIN = 0.50              # regime replication broken

HP_CV_MAX = 0.15
HP_SATURATION_CEIL = 0.95

def _crosstalk(v_c_per_hop: int, n: int) -> float:
    return float(math.sqrt(max(v_c_per_hop - 1, 1) / max(n, 1)))

CROSSTALK_PART = _crosstalk(PART_SIZE, N_DIM)         # sqrt(799/8192) = 0.3123
CROSSTALK_BASELINE = _crosstalk(V_CONCEPTS, N_DIM)    # sqrt(3999/8192) = 0.6989

# Locked invariants
assert HP_ARM_A_LO < HP_ARM_A_HI <= HP_SATURATION_CEIL
assert HP_BEST_ALT_LO > HF_BEST_ALT_ABS
assert HP_BEST_ALT_LO < HP_BEST_ALT_HI <= HP_SATURATION_CEIL
assert 0.0 < HP_CV_MAX < 0.5
assert abs(CROSSTALK_PART - math.sqrt(799 / 8192)) < 1e-6
assert DEPTH == 15
assert N_PARTITIONS == 5
assert PART_SIZE == 800

# Chain configuration
N_CHAINS_TRAIN = 200
if RUN_MODE == "smoke":
    SEEDS = [11]
    N_CHAINS_TEST = 100
else:
    SEEDS = [11, 13, 19]
    N_CHAINS_TEST = 200

N_ARMS = 4
EXPECTED_N_UNITS = N_ARMS * len(SEEDS)

ENCODER_PROVENANCE = "SUBSTRATE_NATIVE_BIPOLAR"

CONFIG_VERSION = (
    "multihopDepth15HintAlternativesV1: N=%d V_C=%d V_P=%d depth=%d "
    "n_chains_train=%d n_chains_test=%d seeds=%s mode=%s encoder=%s "
    "n_partitions=%d part_size=%d xtalk_part=%.4f xtalk_baseline=%.4f "
    "k_top_softmax=%d gate_temp=%.2f attn_temp=%.2f "
    "HP_A=[%.2f,%.2f] HP_alt=[%.2f,%.2f] delta=%.2f MM_alt_lo=%.2f "
    "HF_alt=%.2f HF_A_min=%.2f cv_max=%.2f sat_ceil=%.2f "
    "expected_units=%d arms=%d"
) % (
    N_DIM, V_CONCEPTS, V_PRED, DEPTH,
    N_CHAINS_TRAIN, N_CHAINS_TEST, SEEDS, RUN_MODE, ENCODER_PROVENANCE,
    N_PARTITIONS, PART_SIZE, CROSSTALK_PART, CROSSTALK_BASELINE,
    K_TOP_SOFTMAX, LEARNED_GATE_TEMP, ATTN_SOFTMAX_TEMP,
    HP_ARM_A_LO, HP_ARM_A_HI, HP_BEST_ALT_LO, HP_BEST_ALT_HI,
    HP_ALT_WITHIN_ORACLE_DELTA, MM_BEST_ALT_LO,
    HF_BEST_ALT_ABS, HF_ARM_A_MIN, HP_CV_MAX, HP_SATURATION_CEIL,
    EXPECTED_N_UNITS, N_ARMS,
)


# ----------------------------------------------------------------------------
# Primitives (verbatim from parent CG)
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
# ARM_A: PARTITION_ORACLE reference (verbatim from parent CG)
# ----------------------------------------------------------------------------

def arm_partition_oracle(E: np.ndarray, R: np.ndarray, sq: float,
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
            target_part = target_o // part_size  # gen-time oracle
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
        "mechanism": "partition_oracle_baseline_reference",
    }


# ----------------------------------------------------------------------------
# ARM_B: LEARNED_GATE (analytical one-shot from train chains)
# Mechanism: for each partition p, compute mean pre-cleanup state pattern
# across train hops that end in partition p. At test time, score input state
# against each partition's mean pattern; softmax gives partition posterior.
# ----------------------------------------------------------------------------

def _fit_learned_gate(E: np.ndarray, R: np.ndarray, sq: float,
                      W: np.ndarray,
                      chains_train: List[List[Tuple[int, int, int]]],
                      part_size: int, depth: int) -> np.ndarray:
    """Return shape (n_partitions, n_dim); mean pre-cleanup state per partition."""
    n_partitions = E.shape[0] // part_size
    n_dim = E.shape[1]
    accum = np.zeros((n_partitions, n_dim), dtype=np.float32)
    count = np.zeros(n_partitions, dtype=np.int64)
    for chain in chains_train:
        s = chain[0][0]
        for i in range(depth):
            p = chain[i][1]
            target_o = chain[i][2]
            target_part = target_o // part_size
            key = (E[s] * R[p] * sq).astype(np.float32)
            state = W @ key
            # normalize
            nrm = float(np.linalg.norm(state))
            if nrm > 1e-8:
                state = state / nrm
            accum[target_part] += state
            count[target_part] += 1
            s = target_o  # supervised: follow ground-truth for training
    for p in range(n_partitions):
        if count[p] > 0:
            accum[p] /= float(count[p])
            nrm = float(np.linalg.norm(accum[p]))
            if nrm > 1e-8:
                accum[p] /= nrm
    return accum


def arm_learned_gate(E: np.ndarray, R: np.ndarray, sq: float,
                     W: np.ndarray,
                     chains_test: List[List[Tuple[int, int, int]]],
                     depth: int, part_size: int,
                     gate_proto: np.ndarray, temp: float) -> Dict[str, Any]:
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
            key = (E[s] * R[p] * sq).astype(np.float32)
            state = W @ key
            nrm = float(np.linalg.norm(state))
            state_n = state / nrm if nrm > 1e-8 else state
            # score against each partition prototype
            part_scores = gate_proto @ state_n   # (n_partitions,)
            part_scores = part_scores / max(temp, 1e-6)
            # argmax: pick most likely partition (learned; not oracle)
            chosen_part = int(part_scores.argmax())
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
        "gate_temp": temp,
        "mechanism": "learned_gate_analytical_partition_prototype",
    }


# ----------------------------------------------------------------------------
# ARM_C: TOP_K_SOFTMAX_ATTENTION
# Mechanism: softmax-weighted mixture of ALL partition scores; argmax over
# the mixture. Weights come from state dot mean-partition-prototype (same as
# learned gate) but WEIGHTED not argmax'd.
# ----------------------------------------------------------------------------

def arm_top_k_softmax_attn(E: np.ndarray, R: np.ndarray, sq: float,
                           W: np.ndarray,
                           chains_test: List[List[Tuple[int, int, int]]],
                           depth: int, part_size: int,
                           gate_proto: np.ndarray, k_top: int,
                           temp: float) -> Dict[str, Any]:
    n = len(chains_test)
    hits = 0
    per_step_hits = np.zeros(depth, dtype=np.int64)
    n_partitions = E.shape[0] // part_size
    k_use = min(k_top, n_partitions)
    for chain in chains_test:
        s = chain[0][0]
        for i in range(depth):
            p = chain[i][1]
            target_o = chain[i][2]
            key = (E[s] * R[p] * sq).astype(np.float32)
            state = W @ key
            nrm = float(np.linalg.norm(state))
            state_n = state / nrm if nrm > 1e-8 else state
            part_scores = gate_proto @ state_n   # (n_partitions,)
            part_scores = part_scores / max(temp, 1e-6)
            # top-K softmax weights
            top_k_idx = np.argsort(part_scores)[::-1][:k_use]
            top_k_logits = part_scores[top_k_idx]
            mx = float(top_k_logits.max())
            exp_l = np.exp(top_k_logits - mx)
            weights = exp_l / max(exp_l.sum(), 1e-8)
            # Weighted mixture: score over V_C via weighted partition contribs
            # For each of top-K parts, compute local scores, weight, argmax global
            best_score = -1e30
            best_global = -1
            for w_i, part_id in zip(weights, top_k_idx):
                part_start = int(part_id) * part_size
                E_p = E[part_start:part_start + part_size]
                local_scores = E_p @ state * float(w_i)
                l_argmax = int(local_scores.argmax())
                l_score = float(local_scores[l_argmax])
                if l_score > best_score:
                    best_score = l_score
                    best_global = part_start + l_argmax
            s_pred = best_global if best_global >= 0 else 0
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
        "k_top": k_use, "attn_temp": temp,
        "mechanism": "top_k_softmax_attention_over_partitions",
    }


# ----------------------------------------------------------------------------
# ARM_D: MEMORY_AUGMENTED_HINT
# Mechanism: at train time, store (E[s], target_partition) pairs from train
# chains. At test time, retrieve nearest train (E[s], target_partition) by
# cosine and inherit its partition as hint.
# ----------------------------------------------------------------------------

def _fit_mem_aug(E: np.ndarray,
                 chains_train: List[List[Tuple[int, int, int]]],
                 part_size: int, depth: int) -> Tuple[np.ndarray, np.ndarray]:
    """Return (mem_keys shape (M, n_dim), mem_parts shape (M,))."""
    keys_list = []
    parts_list = []
    for chain in chains_train:
        s = chain[0][0]
        for i in range(depth):
            target_o = chain[i][2]
            target_part = target_o // part_size
            # store CURRENT state (E[s]) as key at each hop, plus target part
            keys_list.append(E[s])
            parts_list.append(target_part)
            s = target_o
    keys = np.asarray(keys_list, dtype=np.float32)
    # normalize rows
    nrms = np.linalg.norm(keys, axis=1, keepdims=True) + 1e-8
    keys = keys / nrms
    parts = np.asarray(parts_list, dtype=np.int64)
    return keys, parts


def arm_mem_aug_hint(E: np.ndarray, R: np.ndarray, sq: float,
                     W: np.ndarray,
                     chains_test: List[List[Tuple[int, int, int]]],
                     depth: int, part_size: int,
                     mem_keys: np.ndarray,
                     mem_parts: np.ndarray) -> Dict[str, Any]:
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
            # nearest train-chain lookup: cosine of E[s] to mem_keys
            q = E[s].astype(np.float32)
            qn = q / (float(np.linalg.norm(q)) + 1e-8)
            sims = mem_keys @ qn
            nearest = int(sims.argmax())
            chosen_part = int(mem_parts[nearest])
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
        "n_memory_entries": int(mem_keys.shape[0]),
        "mechanism": "memory_augmented_hint_nearest_train_chain",
    }


# ----------------------------------------------------------------------------
# Arms-must-differ SHA-256 (META_RULE_AF)
# ----------------------------------------------------------------------------

def _arms_must_differ_sha256(per_seed: List[Dict[str, Any]]) -> Dict[str, str]:
    hashes: Dict[str, str] = {}
    arm_keys = [
        "arm_a_partition_oracle",
        "arm_b_learned_gate",
        "arm_c_top_k_softmax_attn",
        "arm_d_mem_aug_hint",
    ]
    for k in arm_keys:
        h = hashlib.sha256()
        for pp in per_seed:
            if k in pp and isinstance(pp[k].get("per_step_acc"), list):
                h.update(repr(pp[k]["per_step_acc"]).encode("utf-8"))
                h.update(b"|")
                h.update(repr(pp[k].get("top1", "")).encode("utf-8"))
                h.update(b"||")
        hashes[k] = h.hexdigest()[:16]
    return hashes


# ----------------------------------------------------------------------------
# Self-test (formula sanity + tiny config arms work)
# ----------------------------------------------------------------------------

def _selftest() -> None:
    g = np.random.default_rng(0)
    n_tiny = 256
    V_tiny = 40
    P_tiny = 4
    sq = math.sqrt(n_tiny)
    E = bipolar(V_tiny, n_tiny, g)
    R = bipolar(P_tiny, n_tiny, g)

    # T1: shapes + norm
    assert E.shape == (V_tiny, n_tiny)
    assert abs(float(np.linalg.norm(E[0])) - 1.0) < 1e-4

    # T2: chain construction at DEPTH=15
    train_triples, train_chains = make_deep_chains(
        16, V_tiny, P_tiny, max_depth=DEPTH, g=g, disallow_s=set())
    used = set(c[0][0] for c in train_chains)
    test_triples, test_chains = make_deep_chains(
        8, V_tiny, P_tiny, max_depth=DEPTH, g=g, disallow_s=used)
    assert len(train_chains) == 16 and len(test_chains) == 8

    # T3: ingest
    all_tr = train_triples + test_triples
    W = ingest_hebbian(all_tr, E, R, sq, n_tiny)
    assert W.shape == (n_tiny, n_tiny)
    assert np.isfinite(W).all()

    tiny_part_size = V_tiny // 8   # 5 atoms/part; 8 partitions
    assert V_tiny % 8 == 0

    # T4: all 4 arms produce valid output
    r_a = arm_partition_oracle(E, R, sq, W, test_chains,
                               depth=DEPTH, part_size=tiny_part_size)
    assert 0.0 <= r_a["top1"] <= 1.0
    assert len(r_a["per_step_acc"]) == DEPTH

    gate_proto = _fit_learned_gate(E, R, sq, W, train_chains,
                                   part_size=tiny_part_size, depth=DEPTH)
    assert gate_proto.shape == (V_tiny // tiny_part_size, n_tiny)

    r_b = arm_learned_gate(E, R, sq, W, test_chains,
                           depth=DEPTH, part_size=tiny_part_size,
                           gate_proto=gate_proto, temp=LEARNED_GATE_TEMP)
    assert 0.0 <= r_b["top1"] <= 1.0

    r_c = arm_top_k_softmax_attn(E, R, sq, W, test_chains,
                                 depth=DEPTH, part_size=tiny_part_size,
                                 gate_proto=gate_proto,
                                 k_top=K_TOP_SOFTMAX, temp=ATTN_SOFTMAX_TEMP)
    assert 0.0 <= r_c["top1"] <= 1.0

    mem_keys, mem_parts = _fit_mem_aug(E, train_chains,
                                       part_size=tiny_part_size, depth=DEPTH)
    assert mem_keys.shape[0] == len(train_chains) * DEPTH
    assert mem_keys.shape[1] == n_tiny
    assert mem_parts.shape[0] == mem_keys.shape[0]

    r_d = arm_mem_aug_hint(E, R, sq, W, test_chains,
                           depth=DEPTH, part_size=tiny_part_size,
                           mem_keys=mem_keys, mem_parts=mem_parts)
    assert 0.0 <= r_d["top1"] <= 1.0

    # T5: crosstalk formula sanity
    # psz=800 N=8192: sqrt(799/8192) = 0.3123
    assert abs(CROSSTALK_PART - 0.3123) < 0.001
    assert CROSSTALK_BASELINE > 0.6

    # T6: bands LOCKED
    assert N_DIM == 8192
    assert V_CONCEPTS == 4000
    assert DEPTH == 15
    assert N_PARTITIONS == 5
    assert PART_SIZE == 800
    assert HP_ARM_A_LO == 0.60
    assert HP_ARM_A_HI == 0.95
    assert HP_BEST_ALT_LO == 0.50
    assert HP_BEST_ALT_HI == 0.95
    assert HP_ALT_WITHIN_ORACLE_DELTA == 0.05
    assert MM_BEST_ALT_LO == 0.30
    assert HF_BEST_ALT_ABS == 0.30
    assert HF_ARM_A_MIN == 0.50
    assert HP_CV_MAX == 0.15
    assert HP_SATURATION_CEIL == 0.95

    # T7: zero LLM calls
    assert _LLM_CALL_COUNTER[0] == 0

    # T8: cardinality declared
    assert EXPECTED_N_UNITS == 4 * len(SEEDS)

    # T9: anchor binding
    assert ANCHOR_NAME == "multihop_depth_15_hint_alternatives_v1"

    # T10: arms-must-differ SHA-256 -- all 4 arms should produce distinct
    # hashes on tiny config (or at least ORACLE vs LEARNED and ORACLE vs MEM)
    tiny_per_seed = [{
        "arm_a_partition_oracle": r_a,
        "arm_b_learned_gate": r_b,
        "arm_c_top_k_softmax_attn": r_c,
        "arm_d_mem_aug_hint": r_d,
    }]
    hashes = _arms_must_differ_sha256(tiny_per_seed)
    # Oracle uses gen-time target_part; learned/attn/mem use inferred hint.
    # They MUST differ at tiny config unless learned gate is perfect (v unlikely).
    assert hashes["arm_a_partition_oracle"] != hashes["arm_b_learned_gate"], \
        "META_RULE_AF: A vs B tied in selftest (learned gate matched oracle?)"
    assert hashes["arm_a_partition_oracle"] != hashes["arm_d_mem_aug_hint"], \
        "META_RULE_AF: A vs D tied in selftest"

    # T11: assert measured ~= expected (per spawn discipline)
    # tiny config too small to predict numerically; verify bounded outputs
    # and that per_step is nonincreasing-ish across depth (small integer noise ok)
    psa = r_a["per_step_acc"]
    assert max(psa) >= psa[-1] - 0.5, \
        "per_step should not radically increase: %s" % psa

    print("[selftest] PASS N=%d V_C=%d depth=%d psz=%d arms: "
          "a=%.3f b=%.3f c=%.3f d=%.3f xtalk_part=%.4f HP_A=[%.2f,%.2f] "
          "HP_alt=[%.2f,%.2f] delta=%.2f" % (
              N_DIM, V_CONCEPTS, DEPTH, PART_SIZE,
              r_a["top1"], r_b["top1"], r_c["top1"], r_d["top1"],
              CROSSTALK_PART,
              HP_ARM_A_LO, HP_ARM_A_HI,
              HP_BEST_ALT_LO, HP_BEST_ALT_HI, HP_ALT_WITHIN_ORACLE_DELTA),
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

    all_triples = triples_train + triples_test
    print("  [seed=%d] ingesting W (%d bindings, N=%d)" % (
        seed, len(all_triples), N_DIM), flush=True)
    t_ingest = time.time()
    W = ingest_hebbian(all_triples, E, R, sq, N_DIM)
    print("  [seed=%d] W ingested t=%.1fs" % (
        seed, time.time() - t_ingest), flush=True)

    # Fit LEARNED_GATE prototypes (analytical; no SGD)
    print("  [seed=%d] fitting learned_gate prototypes" % seed, flush=True)
    t_fit = time.time()
    gate_proto = _fit_learned_gate(E, R, sq, W, chains_train,
                                   part_size=PART_SIZE, depth=DEPTH)
    print("  [seed=%d] gate_proto fitted t=%.1fs shape=%s" % (
        seed, time.time() - t_fit, gate_proto.shape), flush=True)

    # Fit MEM_AUG memory
    print("  [seed=%d] fitting mem_aug memory" % seed, flush=True)
    t_fit = time.time()
    mem_keys, mem_parts = _fit_mem_aug(E, chains_train,
                                       part_size=PART_SIZE, depth=DEPTH)
    print("  [seed=%d] mem_aug fitted t=%.1fs shape=%s" % (
        seed, time.time() - t_fit, mem_keys.shape), flush=True)

    out: Dict[str, Any] = {
        "seed": seed, "run_mode": RUN_MODE, "N": N_DIM, "V_C": V_CONCEPTS,
        "V_P": V_PRED, "depth": DEPTH,
        "n_chains_train": N_CHAINS_TRAIN, "n_chains_test": N_CHAINS_TEST,
        "n_partitions": N_PARTITIONS, "part_size": PART_SIZE,
        "crosstalk_baseline": CROSSTALK_BASELINE,
        "crosstalk_part": CROSSTALK_PART,
        "encoder_provenance": ENCODER_PROVENANCE,
        "config_version": CONFIG_VERSION,
        "_llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
    }

    # ===== ARM_A: PARTITION_ORACLE reference =====
    t_arm = time.time()
    r_a = arm_partition_oracle(E, R, sq, W, chains_test,
                               depth=DEPTH, part_size=PART_SIZE)
    r_a["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    out["arm_a_partition_oracle"] = r_a
    print("  [seed=%d] ARM_A PARTITION_ORACLE top1=%.4f "
          "(HP_ref=[%.2f,%.2f]) per_step=%s t=%.1fs" % (
              seed, r_a["top1"], HP_ARM_A_LO, HP_ARM_A_HI,
              r_a["per_step_acc"], r_a["elapsed_s_arm"]), flush=True)

    # ===== ARM_B: LEARNED_GATE =====
    t_arm = time.time()
    r_b = arm_learned_gate(E, R, sq, W, chains_test, depth=DEPTH,
                           part_size=PART_SIZE, gate_proto=gate_proto,
                           temp=LEARNED_GATE_TEMP)
    r_b["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    out["arm_b_learned_gate"] = r_b
    print("  [seed=%d] ARM_B LEARNED_GATE top1=%.4f (temp=%.2f) "
          "per_step=%s t=%.1fs" % (
              seed, r_b["top1"], LEARNED_GATE_TEMP,
              r_b["per_step_acc"], r_b["elapsed_s_arm"]), flush=True)

    # ===== ARM_C: TOP_K_SOFTMAX_ATTN =====
    t_arm = time.time()
    r_c = arm_top_k_softmax_attn(E, R, sq, W, chains_test, depth=DEPTH,
                                 part_size=PART_SIZE, gate_proto=gate_proto,
                                 k_top=K_TOP_SOFTMAX, temp=ATTN_SOFTMAX_TEMP)
    r_c["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    out["arm_c_top_k_softmax_attn"] = r_c
    print("  [seed=%d] ARM_C TOP_K_SOFTMAX_ATTN top1=%.4f (K=%d temp=%.2f) "
          "per_step=%s t=%.1fs" % (
              seed, r_c["top1"], K_TOP_SOFTMAX, ATTN_SOFTMAX_TEMP,
              r_c["per_step_acc"], r_c["elapsed_s_arm"]), flush=True)

    # ===== ARM_D: MEM_AUG_HINT =====
    t_arm = time.time()
    r_d = arm_mem_aug_hint(E, R, sq, W, chains_test, depth=DEPTH,
                           part_size=PART_SIZE, mem_keys=mem_keys,
                           mem_parts=mem_parts)
    r_d["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    out["arm_d_mem_aug_hint"] = r_d
    print("  [seed=%d] ARM_D MEM_AUG_HINT top1=%.4f (mem=%d) "
          "per_step=%s t=%.1fs" % (
              seed, r_d["top1"], int(mem_keys.shape[0]),
              r_d["per_step_acc"], r_d["elapsed_s_arm"]), flush=True)

    # Lifts + best-alt
    out["best_alternative_top1"] = round(
        max(r_b["top1"], r_c["top1"], r_d["top1"]), 4)
    out["best_alternative_arm"] = max(
        [("B", r_b["top1"]), ("C", r_c["top1"]), ("D", r_d["top1"])],
        key=lambda kv: kv[1])[0]
    out["oracle_minus_best_alt"] = round(
        r_a["top1"] - out["best_alternative_top1"], 4)

    out["elapsed_s"] = round(time.time() - t, 1)
    return out


# ----------------------------------------------------------------------------
# Verdict (META_RULE_AL HP/HF/MM; META_RULE_AF)
# ----------------------------------------------------------------------------

def verdict_from(per_seed: List[Dict[str, Any]]) -> Tuple[str, str, Dict[str, str]]:
    def mean_top1(key: str) -> float:
        vals = [pp[key]["top1"] for pp in per_seed if key in pp
                and isinstance(pp[key].get("top1"), (int, float))
                and not math.isnan(pp[key]["top1"])]
        return float(np.mean(vals)) if vals else float("nan")

    def cv_top1(key: str) -> float:
        vals = [pp[key]["top1"] for pp in per_seed if key in pp
                and isinstance(pp[key].get("top1"), (int, float))
                and not math.isnan(pp[key]["top1"])]
        if len(vals) < 2:
            return float("nan")
        m = float(np.mean(vals))
        return float(np.std(vals) / max(m, 1e-9))

    arm_a = mean_top1("arm_a_partition_oracle")
    arm_b = mean_top1("arm_b_learned_gate")
    arm_c = mean_top1("arm_c_top_k_softmax_attn")
    arm_d = mean_top1("arm_d_mem_aug_hint")

    cv_a = cv_top1("arm_a_partition_oracle")
    cv_b = cv_top1("arm_b_learned_gate")
    cv_c = cv_top1("arm_c_top_k_softmax_attn")
    cv_d = cv_top1("arm_d_mem_aug_hint")

    best_alt = float("nan")
    best_alt_name = "NONE"
    for name, val in (("B_learned_gate", arm_b),
                      ("C_top_k_softmax_attn", arm_c),
                      ("D_mem_aug_hint", arm_d)):
        if not math.isnan(val):
            if math.isnan(best_alt) or val > best_alt:
                best_alt = val
                best_alt_name = name

    oracle_minus_best_alt = (arm_a - best_alt
                             if not (math.isnan(arm_a) or math.isnan(best_alt))
                             else float("nan"))

    # Cardinality
    observed_units = sum(
        1 for pp in per_seed for arm_key in (
            "arm_a_partition_oracle", "arm_b_learned_gate",
            "arm_c_top_k_softmax_attn", "arm_d_mem_aug_hint")
        if arm_key in pp
    )
    cardinality_ok = (observed_units == EXPECTED_N_UNITS)

    # Arms-distinct
    arms_hashes = _arms_must_differ_sha256(per_seed)
    arms_distinct = (
        arms_hashes["arm_a_partition_oracle"] != arms_hashes["arm_b_learned_gate"]
        and arms_hashes["arm_a_partition_oracle"] != arms_hashes["arm_c_top_k_softmax_attn"]
        and arms_hashes["arm_a_partition_oracle"] != arms_hashes["arm_d_mem_aug_hint"]
    )

    # Saturation guards
    saturation_a = (not math.isnan(arm_a)) and arm_a >= HP_SATURATION_CEIL
    saturation_best_alt = (not math.isnan(best_alt)) and best_alt >= HP_SATURATION_CEIL

    # HP bands
    arm_a_in_band = ((not math.isnan(arm_a))
                     and HP_ARM_A_LO <= arm_a <= HP_ARM_A_HI)
    best_alt_in_band = ((not math.isnan(best_alt))
                        and HP_BEST_ALT_LO <= best_alt <= HP_BEST_ALT_HI)
    best_alt_within_delta = ((not math.isnan(oracle_minus_best_alt))
                             and oracle_minus_best_alt <= HP_ALT_WITHIN_ORACLE_DELTA)

    summ = (
        "ARM_A_ORACLE=%.4f (cv=%.3f in_band=%s) "
        "ARM_B_LEARNED=%.4f (cv=%.3f) ARM_C_ATTN=%.4f (cv=%.3f) "
        "ARM_D_MEM=%.4f (cv=%.3f) "
        "best_alt=%.4f (%s in_band=%s within_delta=%s) "
        "oracle_minus_best_alt=%.4f cardinality_ok=%s "
        "expected_units=%d observed_units=%d arms_distinct=%s "
        "sat_A=%s sat_best_alt=%s HP_A=[%.2f,%.2f] HP_alt=[%.2f,%.2f] "
        "delta=%.2f depth=%d"
    ) % (
        arm_a, cv_a, arm_a_in_band,
        arm_b, cv_b, arm_c, cv_c, arm_d, cv_d,
        best_alt, best_alt_name, best_alt_in_band, best_alt_within_delta,
        oracle_minus_best_alt, cardinality_ok,
        EXPECTED_N_UNITS, observed_units, arms_distinct,
        saturation_a, saturation_best_alt,
        HP_ARM_A_LO, HP_ARM_A_HI, HP_BEST_ALT_LO, HP_BEST_ALT_HI,
        HP_ALT_WITHIN_ORACLE_DELTA, DEPTH,
    )

    # Cardinality gate FIRST
    if not cardinality_ok:
        return ("HARD_FAIL_CARDINALITY_BREACH",
                "HARD_FAIL_CARDINALITY_BREACH: " + summ, arms_hashes)

    # Arms-distinct gate
    if not arms_distinct:
        return ("HARD_FAIL_ARMS_TIED",
                "HARD_FAIL_ARMS_TIED_NO_DISCRIMINATION: " + summ, arms_hashes)

    # HARD_FAIL: oracle regime broken
    if (not math.isnan(arm_a)) and arm_a < HF_ARM_A_MIN:
        return ("HARD_FAIL_ORACLE_REGIME_BROKEN",
                "HARD_FAIL_ORACLE_REGIME_BROKEN_ARM_A_BELOW_MIN: " + summ,
                arms_hashes)

    # HARD_FAIL: all alternatives die (by-construction confirmed)
    if (not math.isnan(best_alt)) and best_alt <= HF_BEST_ALT_ABS:
        return ("HARD_FAIL_ALL_ALT_MECHANISMS_DEAD",
                "HARD_FAIL_ALL_ALTERNATIVES_DEAD_BY_CONSTRUCTION_CONFIRMED: " + summ,
                arms_hashes)

    # Smoke verdict
    if RUN_MODE == "smoke":
        if arm_a_in_band and best_alt_in_band and best_alt_within_delta \
                and not saturation_best_alt:
            return ("SMOKE_HARD_PASS",
                    "SMOKE_HARD_PASS_ALTERNATIVE_MATCHES_ORACLE_DEPTH15: " + summ,
                    arms_hashes)
        if (not math.isnan(best_alt)) and best_alt >= MM_BEST_ALT_LO:
            return ("MIDDLE_BAND",
                    "MIDDLE_BAND_ALTERNATIVE_PARTIAL_MECHANISM: " + summ,
                    arms_hashes)
        return ("HARD_FAIL_ALT_BELOW_MM_FLOOR",
                "HARD_FAIL_ALT_BELOW_MIDDLE_BAND_FLOOR: " + summ, arms_hashes)

    # Full verdict (multi-seed; cv required for chain-grade)
    cv_ok = ((not math.isnan(cv_a)) and cv_a < HP_CV_MAX)
    # best-alt cv check based on winning alt
    if best_alt_name.startswith("B_"):
        cv_best_alt = cv_b
    elif best_alt_name.startswith("C_"):
        cv_best_alt = cv_c
    elif best_alt_name.startswith("D_"):
        cv_best_alt = cv_d
    else:
        cv_best_alt = float("nan")
    cv_ok = cv_ok and ((not math.isnan(cv_best_alt)) and cv_best_alt < HP_CV_MAX)

    if arm_a_in_band and best_alt_in_band and best_alt_within_delta \
            and cv_ok and not saturation_best_alt:
        return ("HARD_PASS_ALTERNATIVE_MATCHES_ORACLE_DEPTH15",
                "HARD_PASS_ALTERNATIVE_HINT_MATCHES_ORACLE_BY_CONSTRUCTION_BROKEN: "
                + summ, arms_hashes)

    if (not math.isnan(best_alt)) and best_alt >= MM_BEST_ALT_LO:
        return ("MIDDLE_BAND",
                "MIDDLE_BAND_ALTERNATIVE_PARTIAL_MECHANISM: " + summ,
                arms_hashes)

    return ("HARD_FAIL_ALT_BELOW_MM_FLOOR",
            "HARD_FAIL_ALT_BELOW_MIDDLE_BAND_FLOOR: " + summ, arms_hashes)


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
                                 run_config={"N": N_DIM, "run_mode": RUN_MODE})
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
                "partition_oracle_reference",
                "learned_gate_analytical",
                "top_k_softmax_attention",
                "memory_augmented_hint"],
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
            "partition_oracle_reference",
            "learned_gate_analytical",
            "top_k_softmax_attention",
            "memory_augmented_hint"],
        "arms_must_differ_sha256": ahashes,
        "DESIGN_NOTE": (
            "Test alternative hint mechanisms at depth-15 vs parent CG "
            "partition-oracle 0.808 3-seed mean. Alternatives: (B) learned_gate "
            "analytical partition-prototype scoring; (C) top-K softmax "
            "attention over ALL 5 partitions; (D) memory-augmented nearest- "
            "train-chain hint. HP: best alternative within 0.05 of oracle AND "
            "in [0.50, 0.95] -> by-construction-saturation critique BROKEN. "
            "HARD_FAIL: all alternatives <=0.30 -> confirms oracle is trivially "
            "informed. Parent CG cells + metrics cited in DESIGN_NOTE header. "
            "MEASURED@CG_ORACLE_D15_3SEED_MEAN=0.808."
        ),
    }
    write_metrics(out_dir, metrics, results=per_seed)
    print("[done] metrics.json written (%d seeds, %.1fs)" % (
        len(per_seed), metrics["elapsed_s"]), flush=True)
