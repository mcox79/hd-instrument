"""substrate_partition_oracle_brain_composition_hint_v1 (seed=19).

PURPOSE (USER 2026-06-28: "can cortex derive the hint better? how does the brain do it?"):
    BRAIN-FAITHFUL composition of 3 chain-grade primitives to derive partition
    restriction WITHOUT an oracle:
        FR1 vmPFC schema-Bayes (schema_exemplar_bayes_ANCHOR_3 K_NEAREST_K20=0.728)
        FR2 cortex partition activation (cortex routing routing_acc=0.97 at M=10M)
        FR3 hippo restricted cleanup (hippo top1=1.000 from 50% corruption)
    The brain has NO ORACLE. CLS architecture (McClelland-O'Reilly-McNaughton 1995)
    composes these three primitives. This cell tests whether multiplicative
    composition preserves enough accuracy to approach the oracle bound at depth-15.

    PATH 1 (sibling cell-author a976aca436f1177d6): partition-routing-only hint
    (single-primitive: direct query -> partition map).
    PATH 2 (this cell): vmPFC + cortex + hippo composition (3-primitive
    brain-faithful).
    Both should land for comparison.

REGIME (matches v5 hardened + Path 1 for comparability):
    N_DIM=8192, V_CONCEPTS=4000, V_PRED=10, DEPTH=15
    N_PARTS=5, PART_SIZE=800 (PATH2/PATH1/ORACLE partition granularity)
    N_CHAINS_TRAIN=200, N_CHAINS_TEST=200(full)/100(smoke)
    N_SCHEMAS=20 (vmPFC schema cluster count)

ARMS (6 comparison-rich):
    A: BASELINE                full V_C=4000 cleanup (no hint)
    B: PATH1_ROUTING_ONLY      direct query -> partition map (single-primitive)
    C: PATH2_CORTEX_COMPOSITION vmPFC + cortex partition + hippo (3-primitive)
    D: ORACLE_GROUND_TRUTH     ground-truth partition (upper bound)
    E: SCHEMA_ONLY             schema posterior used directly (ablation: no cortex)
    F: RANDOM                  random partition (1/N_PARTS chance/hop; floor)

PRE-REG BANDS (LOCKED at module init; META_RULE_AL):
    HARD_PASS (chain-grade composition; un-saturated):
        PATH2_C top1 in [0.50, 0.95]   # META_RULE_AG un-saturated
        AND PATH2_C - BASELINE_A >= 0.30
        AND ORACLE_D - PATH2_C <= 0.05  # composition retains oracle lift
        AND PATH2_C - PATH1_B >= 0.05  # cortex adds value over routing-only
        AND PATH2_C - SCHEMA_ONLY_E >= 0.10 # partition adds value over schema
        AND BASELINE_A in [0.30, 0.70]
        AND cv(PATH2_C) < 0.15 (full)
        AND arms_distinct == True
        AND saturation == False  # PATH2_C < 0.95
    HARD_FAIL:
        PATH2_C <= 0.30  # composition collapses at depth-15
        OR (saturation AND lift_C_A < 0.20)
        OR PATH2_C - RANDOM_F < 0.20  # no goal-info
    MIDDLE_BAND:
        PATH2_C in [0.30, 0.50) with lift_C_A >= 0.15
        OR HP-band hit BUT PATH2_C - PATH1_B < 0.05  # composition adds nothing

NUMBER TAGGING (META_RULE_AC):
    HYPOTHESIZED@HARD_PASS_BAND_PATH2: [0.50, 0.95]
    THEORETICAL@SCHEMA_CORRECT_PER_HOP: 0.728 * 0.97 = 0.706
    THEORETICAL@DEPTH_SCALE_BASELINE: 0.948^15 = 0.449
    THEORETICAL@DEPTH_SCALE_ORACLE:   0.98^15 = 0.739
    MEASURED@V5_HARDENED_SMOKE_BASELINE_A_TOP1_D15: 0.39
    MEASURED@V5_HARDENED_SMOKE_ORACLE_B_TOP1_D15:   0.90
    MEASURED@VMPFC_SCHEMA_BAYES_K20: 0.728
    MEASURED@CORTEX_PARTITION_ROUTING_ACC: 0.97
    MEASURED@HIPPO_PATTERN_COMPLETION_TOP1: 1.000
    CITED@MCCLELLAND_OREILLY_MCNAUGHTON_1995: complementary learning systems
    CITED@MARR_1971: hippocampal pattern completion theory
    CITED@MANTE_2013: PFC goal-conditioned attention
    CITED@OREILLY_2014: vmPFC schema prototype matching

DISCIPLINE TAGS:
    META_RULE_AC: number tagging MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@
    META_RULE_AE: absolute metrics.json paths in DESIGN_NOTE
    META_RULE_AF: arms-must-differ SHA-256 hash check post-run (6 arms)
    META_RULE_AG: discriminator at edge-of-capacity (PATH2 target 0.74; not saturated)
    META_RULE_AH: atomic metrics.json write (tmp + os.replace via _seed_checkpoint)
    META_RULE_AL: HARD_PASS + HARD_FAIL bands pre-registered + LOCKED at import
    META_RULE_AN: substrate-empirical anchor (per_step=0.948 from v5_hardened smoke)
    META_RULE_H : CARDINALITY_OK declared; EXPECTED_N_UNITS=6*len(SEEDS) enforced
    BIAS-N     : per-arm metrics in summary (NOT verdict_msg framing only)
    BIAS-Q     : saturation guard at 0.95 (tightened); auto-demote MM if lift<0.20
    BIAS-S     : baseline rail check [0.30, 0.70]
    DISCRIMINATOR-MUST-SURVIVE-SCALE: smoke at FULL-N + FULL-depth
    PROT-018: regime params bind to anchor descriptor in CONFIG_VERSION
    Fix #28: per-arm reads from metrics.json
    NO-LOCAL: route remote_cpu_queue for FULL (USER 2026-06-28)
    CHUNKED single-seed-per-cell sibling (this is seed=7; siblings seed=13, seed=19)

SOURCE CITATIONS (ABSOLUTE PATHS; META_RULE_AE):
    - Sibling template (v5 hardened FULL seed_11):
      d:/AI/hd-instrument/experiments/exp_substrate_multihop_partition_oracle_v5_hardened_FULL_seed_11_v1.py
    - v5 hardened smoke metrics (regime calibration source):
      d:/AI/hd-instrument/data/exp_substrate_multihop_partition_oracle_v5_hardened_v1_smoke/metrics.json
    - Pre-reg:
      d:/AI/hd-instrument/preregs/2026-06-28_substrate_partition_oracle_brain_composition_hint_v1.md

Author: exp_dev 2026-06-28 (USER directive: brain-faithful hint composition).
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

ANCHOR_NAME = "substrate_partition_oracle_brain_composition_hint_v1_seed_19"
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

N_PARTS = 5           # 5 partitions of 800 (matches v5_hardened ORACLE_B; un-sat)
assert V_CONCEPTS % N_PARTS == 0
PART_SIZE = V_CONCEPTS // N_PARTS  # 800

N_SCHEMAS = 20        # vmPFC schema cluster count (~10 chains/schema in train)

def _cone_collapse_crosstalk(v_c_per_hop: int, n: int) -> float:
    return float(math.sqrt(max(v_c_per_hop - 1, 1) / max(n, 1)))

CROSSTALK_PART = _cone_collapse_crosstalk(PART_SIZE, N_DIM)        # 0.3123
CROSSTALK_BASELINE = _cone_collapse_crosstalk(V_CONCEPTS, N_DIM)   # 0.6987

# BASELINE rail @d=15 (BIAS-S; matches v5_hardened)
BASELINE_RAIL_TARGET = 0.449       # THEORETICAL@DEPTH_SCALE_BASELINE
BASELINE_RAIL_LO = 0.30
BASELINE_RAIL_HI = 0.70

# PATH2 cortex-composition bands (HYPOTHESIZED@HARD_PASS_BAND_PATH2)
HP_PATH2_LO = 0.50
HP_PATH2_HI = 0.95
HP_LIFT_OVER_BASELINE = 0.30       # PATH2 - BASELINE >= 0.30
HP_GAP_TO_ORACLE_MAX = 0.05        # ORACLE - PATH2 <= 0.05 (composition retains)
HP_LIFT_OVER_PATH1 = 0.05          # PATH2 - PATH1 >= 0.05 (cortex adds value)
HP_LIFT_OVER_SCHEMA_ONLY = 0.10    # PATH2 - SCHEMA_ONLY >= 0.10
HP_LIFT_OVER_RANDOM = 0.20         # PATH2 - RANDOM >= 0.20 (goal-info; loose)
HP_CV_MAX = 0.15                   # cv across seeds (full only)
HP_SATURATION_CEIL = 0.95          # BIAS-Q

HF_PATH2_ABS = 0.30                # HARD_FAIL if composition collapses
HF_LIFT_MIN_IF_SATURATED = 0.20
MM_LIFT_MIN = 0.15

# Chain configuration
N_CHAINS_TRAIN = 200
SEEDS = [19]  # CHUNKED single-seed cell; siblings: seeds_7_13_19_minus_this
if RUN_MODE == "smoke":
    N_CHAINS_TEST = 100
else:
    N_CHAINS_TEST = 200

# Cardinality (META_RULE_H): 6 arms x 1 seed
N_ARMS = 6
EXPECTED_N_UNITS = N_ARMS * len(SEEDS)

ENCODER_PROVENANCE = "SUBSTRATE_NATIVE_BIPOLAR"

CONFIG_VERSION = (
    "ANCHOR=%s,substratePartOracleBrainCompV1Seed19: N=%d V_C=%d V_P=%d depth=%d "
    "n_parts=%d psz=%d xtalk_part=%.4f xtalk_baseline=%.4f n_schemas=%d "
    "n_chains_train=%d n_chains_test=%d seeds=%s mode=%s encoder=%s "
    "RAIL=[%.3f,%.3f] target=%.3f HP_PATH2_band=[%.2f,%.2f] "
    "HP_lift_base=%.2f HP_gap_oracle_max=%.2f HP_lift_path1=%.2f "
    "HP_lift_schema_only=%.2f HP_lift_rand=%.2f HP_cv_max=%.2f "
    "HP_sat_ceil=%.2f HF_path2_abs=%.2f HF_lift_min_if_sat=%.2f "
    "MM_lift_min=%.2f expected_units=%d arms=%d"
) % (
    ANCHOR_NAME, N_DIM, V_CONCEPTS, V_PRED, DEPTH,
    N_PARTS, PART_SIZE, CROSSTALK_PART, CROSSTALK_BASELINE, N_SCHEMAS,
    N_CHAINS_TRAIN, N_CHAINS_TEST, SEEDS, RUN_MODE, ENCODER_PROVENANCE,
    BASELINE_RAIL_LO, BASELINE_RAIL_HI, BASELINE_RAIL_TARGET,
    HP_PATH2_LO, HP_PATH2_HI, HP_LIFT_OVER_BASELINE, HP_GAP_TO_ORACLE_MAX,
    HP_LIFT_OVER_PATH1, HP_LIFT_OVER_SCHEMA_ONLY, HP_LIFT_OVER_RANDOM,
    HP_CV_MAX, HP_SATURATION_CEIL, HF_PATH2_ABS, HF_LIFT_MIN_IF_SATURATED,
    MM_LIFT_MIN, EXPECTED_N_UNITS, N_ARMS,
)

# Locked invariants (META_RULE_AL)
assert BASELINE_RAIL_LO < BASELINE_RAIL_TARGET < BASELINE_RAIL_HI
assert HP_PATH2_LO > HF_PATH2_ABS
assert HP_PATH2_LO < HP_PATH2_HI <= HP_SATURATION_CEIL
assert HP_LIFT_OVER_BASELINE > MM_LIFT_MIN
assert 0.0 < HP_CV_MAX < 0.5
assert CROSSTALK_PART < CROSSTALK_BASELINE
assert abs(CROSSTALK_PART - math.sqrt(799 / 8192)) < 1e-6
assert DEPTH == 15


# ----------------------------------------------------------------------------
# Primitives (verbatim port from v5_hardened)
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
# Brain-composition mechanism: 3 chain-grade primitives
# ----------------------------------------------------------------------------

def chain_schema_vector(chain: List[Tuple[int, int, int]],
                        R: np.ndarray) -> np.ndarray:
    """FR1 helper: encode a chain's PREDICATE SEQUENCE as a schema vector.

    The schema is the brain's abstraction over a chain's relational pattern
    (CITED@OReilly2014 vmPFC schema prototype matching). We encode it by
    superposing the predicate vectors of all hops in the chain. This is
    permutation-invariant over hops (the schema captures WHICH predicates
    appear, not their order) - a defensible brain-faithful encoding given
    that vmPFC abstracts task relations.
    """
    s = np.zeros(R.shape[1], dtype=np.float32)
    for (_, p, _) in chain:
        s += R[p]
    return s / (np.linalg.norm(s) + 1e-8)


def build_schema_prototypes(chains_train: List[List[Tuple[int, int, int]]],
                            R: np.ndarray,
                            n_schemas: int,
                            g: np.random.Generator) -> Tuple[np.ndarray,
                                                              List[int],
                                                              np.ndarray]:
    """FR1: vmPFC schema-Bayes prototype construction.

    1. Compute schema vector for each train chain.
    2. Assign each chain to a schema cluster (here: deterministic hash mod
       n_schemas over the predicate-sequence; equivalent to kmeans on the
       schema vector under random-projection identification at scale).
    3. Compute prototype = mean of cluster members' schema vectors.
    4. Compute per-chain target partition = MAJORITY partition of the chain's
       hop-1 target (the partition the chain ROUTES TO at hop 1).

    Returns (schema_prototypes [n_schemas, N], chain_to_schema [n_chains],
    cluster_to_target_part [n_schemas]).
    """
    n = len(chains_train)
    N = R.shape[1]

    # Hash assignment (deterministic; resembles kmeans+hash trick)
    def chain_hash(chain):
        # Use predicate-tuple as hash key
        return hash(tuple(p for (_, p, _) in chain))

    chain_to_schema = [(chain_hash(c) & 0x7fffffff) % n_schemas
                       for c in chains_train]

    # Compute prototypes
    prototypes = np.zeros((n_schemas, N), dtype=np.float32)
    counts = np.zeros(n_schemas, dtype=np.int64)
    for ci, c in enumerate(chains_train):
        s = chain_schema_vector(c, R)
        k = chain_to_schema[ci]
        prototypes[k] += s
        counts[k] += 1
    for k in range(n_schemas):
        if counts[k] > 0:
            prototypes[k] /= counts[k]
            nrm = float(np.linalg.norm(prototypes[k]))
            if nrm > 1e-8:
                prototypes[k] /= nrm
        else:
            # Empty cluster -> random unit vector (avoids zero-prototype)
            v = g.standard_normal(N).astype(np.float32)
            prototypes[k] = v / (np.linalg.norm(v) + 1e-8)

    # Cluster -> target partition (majority vote of first-hop target partitions)
    cluster_to_target_part = np.zeros(n_schemas, dtype=np.int64)
    for k in range(n_schemas):
        member_parts = [chains_train[ci][0][2] // PART_SIZE
                        for ci in range(n) if chain_to_schema[ci] == k]
        if member_parts:
            counts_per_part = np.bincount(member_parts, minlength=N_PARTS)
            cluster_to_target_part[k] = int(counts_per_part.argmax())
        else:
            cluster_to_target_part[k] = int(g.integers(0, N_PARTS))

    return prototypes, chain_to_schema, cluster_to_target_part


def build_schema_to_partition_W(prototypes: np.ndarray,
                                cluster_to_target_part: np.ndarray,
                                n_dim: int) -> np.ndarray:
    """FR2: cortex partition activation matrix.

    Hebbian outer-product: W = sum_k schema_proto_k OUTER partition_onehot_k.
    Inference: W @ schema_query gives soft partition prediction
    (after argmax = single partition).

    Equivalent to schema_proto_k bind partition_k in HD-binding terms (CITED@
    Mante2013 PFC goal-conditioned narrowing).
    """
    n_schemas, N = prototypes.shape
    W = np.zeros((N_PARTS, N), dtype=np.float32)
    for k in range(n_schemas):
        part = int(cluster_to_target_part[k])
        W[part] += prototypes[k]
    # Normalize rows so dot-product yields cosine-like score
    for p in range(N_PARTS):
        nrm = float(np.linalg.norm(W[p]))
        if nrm > 1e-8:
            W[p] /= nrm
    return W


def predict_partition_path2(query_schema: np.ndarray,
                            W_schema_to_part: np.ndarray) -> int:
    """FR2 inference: query schema -> argmax cortex partition prediction."""
    scores = W_schema_to_part @ query_schema  # [N_PARTS]
    return int(scores.argmax())


def build_routing_only_W(chains_train: List[List[Tuple[int, int, int]]],
                         E: np.ndarray,
                         R: np.ndarray,
                         sq: float,
                         n_dim: int) -> np.ndarray:
    """PATH1 (single-primitive baseline): direct query -> partition map.

    Per Path 1 spec (sibling cell a976aca): learn a Hebbian map from query
    (E[s] * R[p] * sq) to partition_onehot. No schema abstraction.
    """
    W = np.zeros((N_PARTS, n_dim), dtype=np.float32)
    for chain in chains_train:
        s, p, o = chain[0]
        key = (E[s] * R[p] * sq).astype(np.float32)
        target_part = o // PART_SIZE
        W[target_part] += key / n_dim
    # Normalize
    for pp in range(N_PARTS):
        nrm = float(np.linalg.norm(W[pp]))
        if nrm > 1e-8:
            W[pp] /= nrm
    return W


def predict_partition_path1(query_key: np.ndarray,
                            W_routing_only: np.ndarray) -> int:
    """PATH1 inference: direct query -> argmax partition."""
    scores = W_routing_only @ query_key
    return int(scores.argmax())


def predict_partition_schema_only(query_schema: np.ndarray,
                                  prototypes: np.ndarray,
                                  cluster_to_target_part: np.ndarray) -> int:
    """SCHEMA_ONLY ablation: schema posterior (argmax cluster) -> cluster's
    majority partition. NO cortex composition - just the schema-Bayes
    primitive feeding partition assignment directly (no Hebbian outer-product
    schema->partition map).
    """
    scores = prototypes @ query_schema  # [N_SCHEMAS]
    k = int(scores.argmax())
    return int(cluster_to_target_part[k])


# ----------------------------------------------------------------------------
# Arms
# ----------------------------------------------------------------------------

def arm_baseline(E: np.ndarray, R: np.ndarray, sq: float,
                 W: np.ndarray, chains_test: List[List[Tuple[int, int, int]]],
                 depth: int) -> Dict[str, Any]:
    """ARM A: baseline argmax over full V_C cleanup."""
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


def arm_part_restricted(E: np.ndarray, R: np.ndarray, sq: float,
                        W: np.ndarray,
                        chains_test: List[List[Tuple[int, int, int]]],
                        depth: int,
                        partition_picker,
                        mechanism_tag: str) -> Dict[str, Any]:
    """Generic partition-restricted cleanup.

    `partition_picker(chain, hop_idx, current_s) -> int` returns a partition
    index in [0, N_PARTS). The arm restricts the cleanup readout to that
    partition's atoms.
    """
    n = len(chains_test)
    hits = 0
    per_step_hits = np.zeros(depth, dtype=np.int64)
    E_parts = [E[p * PART_SIZE:(p + 1) * PART_SIZE]
               for p in range(N_PARTS)]
    correct_part_hits = np.zeros(depth, dtype=np.int64)
    for chain in chains_test:
        s = chain[0][0]
        for i in range(depth):
            p = chain[i][1]
            target_o = chain[i][2]
            target_part = target_o // PART_SIZE
            chosen_part = partition_picker(chain, i, s)
            if chosen_part == target_part:
                correct_part_hits[i] += 1
            key = (E[s] * R[p] * sq).astype(np.float32)
            state = W @ key
            scores = E_parts[chosen_part] @ state
            local_idx = int(scores.argmax())
            s_pred = chosen_part * PART_SIZE + local_idx
            if s_pred == target_o:
                per_step_hits[i] += 1
            s = s_pred
        if s == chain[depth - 1][2]:
            hits += 1
    return {
        "top1": round(hits / max(n, 1), 4),
        "per_step_acc": [round(float(x) / max(n, 1), 4)
                         for x in per_step_hits],
        "partition_correct_per_step": [round(float(x) / max(n, 1), 4)
                                       for x in correct_part_hits],
        "n_queries": n, "depth": depth,
        "n_partitions": N_PARTS, "part_size": PART_SIZE,
        "mechanism": mechanism_tag,
    }


# ----------------------------------------------------------------------------
# Arms-must-differ SHA-256 (META_RULE_AF)
# ----------------------------------------------------------------------------

ARM_KEYS = [
    "arm_a_baseline",
    "arm_b_path1_routing_only",
    "arm_c_path2_cortex_composition",
    "arm_d_oracle_ground_truth",
    "arm_e_schema_only",
    "arm_f_random",
]


def _arms_must_differ_sha256(per_seed: List[Dict[str, Any]]) -> Dict[str, str]:
    hashes: Dict[str, str] = {}
    for k in ARM_KEYS:
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
# Self-test (formula + mechanism sanity)
# ----------------------------------------------------------------------------

def _selftest() -> None:
    g = np.random.default_rng(0)
    n_tiny = 256
    V_tiny = 40
    P_tiny = 4
    n_parts_tiny = 4
    psz_tiny = V_tiny // n_parts_tiny  # 10
    n_schemas_tiny = 4
    sq = math.sqrt(n_tiny)
    E = bipolar(V_tiny, n_tiny, g)
    R = bipolar(P_tiny, n_tiny, g)

    # T1: bipolar shapes
    assert E.shape == (V_tiny, n_tiny) and R.shape == (P_tiny, n_tiny)
    assert abs(float(np.linalg.norm(E[0])) - 1.0) < 1e-4

    # T2: chain construction at DEPTH=15
    triples, chains = make_deep_chains(8, V_tiny, P_tiny,
                                       max_depth=DEPTH, g=g,
                                       disallow_s=set())
    assert len(chains) == 8 and len(triples) == 8 * DEPTH

    # T3: ingest
    W = ingest_hebbian(triples, E, R, sq, n_tiny)
    assert W.shape == (n_tiny, n_tiny)
    assert np.isfinite(W).all()

    # T4: schema vector + prototypes (tiny config but operational)
    sv = chain_schema_vector(chains[0], R)
    assert sv.shape == (n_tiny,)
    assert abs(float(np.linalg.norm(sv)) - 1.0) < 1e-4

    # Use module-level PART_SIZE temporarily (selftest patches)
    global PART_SIZE, N_PARTS
    _saved_psz = PART_SIZE
    _saved_np = N_PARTS
    try:
        PART_SIZE = psz_tiny
        N_PARTS = n_parts_tiny
        protos, chain2sch, cl2part = build_schema_prototypes(
            chains, R, n_schemas_tiny, g)
        assert protos.shape == (n_schemas_tiny, n_tiny)
        assert len(chain2sch) == 8
        assert cl2part.shape == (n_schemas_tiny,)
        assert all(0 <= p < n_parts_tiny for p in cl2part)

        # T5: cortex W_schema_to_part shape
        W_s2p = build_schema_to_partition_W(protos, cl2part, n_tiny)
        assert W_s2p.shape == (n_parts_tiny, n_tiny)

        # T6: PATH1 routing-only W shape
        W_r1 = build_routing_only_W(chains, E, R, sq, n_tiny)
        assert W_r1.shape == (n_parts_tiny, n_tiny)

        # T7: predict_partition_path2 returns valid partition
        qs = chain_schema_vector(chains[0], R)
        pp2 = predict_partition_path2(qs, W_s2p)
        assert 0 <= pp2 < n_parts_tiny

        # T8: predict_partition_path1 returns valid partition
        s0, p0, _ = chains[0][0]
        qk = (E[s0] * R[p0] * sq).astype(np.float32)
        pp1 = predict_partition_path1(qk, W_r1)
        assert 0 <= pp1 < n_parts_tiny

        # T9: schema-only predict
        pps = predict_partition_schema_only(qs, protos, cl2part)
        assert 0 <= pps < n_parts_tiny

        # T10: all 6 arms produce valid output at tiny config
        r_a = arm_baseline(E, R, sq, W, chains, depth=DEPTH)
        assert 0.0 <= r_a["top1"] <= 1.0

        def pick_oracle(chain, i, s_now):
            return chain[i][2] // PART_SIZE

        def pick_random(chain, i, s_now):
            return int(g.integers(0, n_parts_tiny))

        def pick_path2(chain, i, s_now):
            qs_chain = chain_schema_vector(chain, R)
            return predict_partition_path2(qs_chain, W_s2p)

        def pick_path1(chain, i, s_now):
            p_pred = chain[i][1]
            qk_local = (E[s_now] * R[p_pred] * sq).astype(np.float32)
            return predict_partition_path1(qk_local, W_r1)

        def pick_schema_only(chain, i, s_now):
            qs_chain = chain_schema_vector(chain, R)
            return predict_partition_schema_only(qs_chain, protos, cl2part)

        r_b = arm_part_restricted(E, R, sq, W, chains, DEPTH, pick_path1,
                                  "path1_routing_only_test")
        r_c = arm_part_restricted(E, R, sq, W, chains, DEPTH, pick_path2,
                                  "path2_cortex_composition_test")
        r_d = arm_part_restricted(E, R, sq, W, chains, DEPTH, pick_oracle,
                                  "oracle_ground_truth_test")
        r_e = arm_part_restricted(E, R, sq, W, chains, DEPTH, pick_schema_only,
                                  "schema_only_test")
        r_f = arm_part_restricted(E, R, sq, W, chains, DEPTH, pick_random,
                                  "random_test")
        for r in (r_b, r_c, r_d, r_e, r_f):
            assert 0.0 <= r["top1"] <= 1.0
            assert len(r["per_step_acc"]) == DEPTH
            assert len(r["partition_correct_per_step"]) == DEPTH
    finally:
        PART_SIZE = _saved_psz
        N_PARTS = _saved_np

    # T11: cone-collapse formula sanity
    assert abs(CROSSTALK_PART - 0.3123) < 0.001, \
        "psz=800/N=8192 xtalk drift: %.4f" % CROSSTALK_PART
    assert CROSSTALK_BASELINE > 0.6

    # T12: bands LOCKED
    assert N_DIM == 8192
    assert V_CONCEPTS == 4000
    assert DEPTH == 15
    assert PART_SIZE == 800
    assert N_PARTS == 5
    assert N_SCHEMAS == 20
    assert HP_PATH2_LO == 0.50
    assert HP_PATH2_HI == 0.95
    assert HF_PATH2_ABS == 0.30
    assert BASELINE_RAIL_LO == 0.30
    assert BASELINE_RAIL_HI == 0.70
    assert HP_LIFT_OVER_BASELINE == 0.30
    assert HP_GAP_TO_ORACLE_MAX == 0.05
    assert HP_LIFT_OVER_PATH1 == 0.05
    assert HP_LIFT_OVER_SCHEMA_ONLY == 0.10
    assert HP_LIFT_OVER_RANDOM == 0.20
    assert HP_CV_MAX == 0.15
    assert HP_SATURATION_CEIL == 0.95

    # T13: zero LLM calls
    assert _LLM_CALL_COUNTER[0] == 0

    # T14: cardinality declared
    assert EXPECTED_N_UNITS == N_ARMS * len(SEEDS) == 6

    # T15: anchor binding (seed=19 sibling)
    assert "_seed_19" in ANCHOR_NAME
    assert ANCHOR_NAME.endswith("_seed_19")
    assert "brain_composition_hint" in ANCHOR_NAME

    print(("[selftest] PASS N=%d V_C=%d depth=%d n_parts=%d psz=%d n_schemas=%d "
           "tiny_arms: a=%.3f b=%.3f c=%.3f d=%.3f e=%.3f f=%.3f "
           "xtalk_part=%.4f xtalk_baseline=%.4f HP_PATH2=[%.2f,%.2f] "
           "expected_proj_baseline=%.3f expected_proj_oracle=%.3f") % (
              N_DIM, V_CONCEPTS, DEPTH, N_PARTS, PART_SIZE, N_SCHEMAS,
              r_a["top1"], r_b["top1"], r_c["top1"], r_d["top1"],
              r_e["top1"], r_f["top1"],
              CROSSTALK_PART, CROSSTALK_BASELINE, HP_PATH2_LO, HP_PATH2_HI,
              0.948 ** DEPTH, 0.98 ** DEPTH),
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
    print("[start_marker] seed=%d anchor=%s mode=%s" % (
        seed, ANCHOR_NAME, RUN_MODE), flush=True)
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
    print("  [seed=%d] ingesting W (%d bindings, N=%d -> %.1f MB)" % (
        seed, len(all_triples), N_DIM, (N_DIM * N_DIM * 4) / 1e6), flush=True)
    t_ingest = time.time()
    W = ingest_hebbian(all_triples, E, R, sq, N_DIM)
    print("  [seed=%d] W ingested t=%.1fs shape=%s" % (
        seed, time.time() - t_ingest, W.shape), flush=True)

    # FR1 + FR2: vmPFC schema-Bayes + cortex partition activation
    print("  [seed=%d] building schema prototypes (n_schemas=%d)" % (
        seed, N_SCHEMAS), flush=True)
    prototypes, chain_to_schema, cluster_to_target_part = build_schema_prototypes(
        chains_train, R, N_SCHEMAS, g)
    print("  [seed=%d] building W_schema_to_part (cortex composition)" % seed,
          flush=True)
    W_schema_to_part = build_schema_to_partition_W(
        prototypes, cluster_to_target_part, N_DIM)

    # PATH1 single-primitive routing-only W
    print("  [seed=%d] building W_routing_only (PATH1 single-primitive)" % seed,
          flush=True)
    W_routing_only = build_routing_only_W(chains_train, E, R, sq, N_DIM)

    out: Dict[str, Any] = {
        "seed": seed, "run_mode": RUN_MODE, "N": N_DIM, "V_C": V_CONCEPTS,
        "V_P": V_PRED, "depth": DEPTH,
        "n_chains_train": N_CHAINS_TRAIN, "n_chains_test": N_CHAINS_TEST,
        "n_partitions": N_PARTS, "part_size": PART_SIZE,
        "n_schemas": N_SCHEMAS,
        "crosstalk_baseline": CROSSTALK_BASELINE,
        "crosstalk_part": CROSSTALK_PART,
        "encoder_provenance": ENCODER_PROVENANCE,
        "config_version": CONFIG_VERSION,
        "anchor_name": ANCHOR_NAME,
        "_llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
    }

    # Partition pickers (closures over per-seed state)
    g_arm_f = np.random.default_rng(seed * 7919 + 1)

    def pick_oracle(chain, i, s_now):
        return chain[i][2] // PART_SIZE

    def pick_random(chain, i, s_now):
        return int(g_arm_f.integers(0, N_PARTS))

    # For PATH2: schema is computed ONCE per chain (vmPFC abstracts the
    # whole task; CITED@OReilly2014)
    _schema_cache_path2: Dict[int, np.ndarray] = {}

    def pick_path2(chain, i, s_now):
        cid = id(chain)
        if cid not in _schema_cache_path2:
            _schema_cache_path2[cid] = chain_schema_vector(chain, R)
        qs = _schema_cache_path2[cid]
        return predict_partition_path2(qs, W_schema_to_part)

    def pick_path1(chain, i, s_now):
        p_pred = chain[i][1]
        qk = (E[s_now] * R[p_pred] * sq).astype(np.float32)
        return predict_partition_path1(qk, W_routing_only)

    _schema_cache_e: Dict[int, np.ndarray] = {}

    def pick_schema_only(chain, i, s_now):
        cid = id(chain)
        if cid not in _schema_cache_e:
            _schema_cache_e[cid] = chain_schema_vector(chain, R)
        qs = _schema_cache_e[cid]
        return predict_partition_schema_only(
            qs, prototypes, cluster_to_target_part)

    # ===== ARM A: BASELINE =====
    t_arm = time.time()
    r_a = arm_baseline(E, R, sq, W, chains_test, depth=DEPTH)
    r_a["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    out["arm_a_baseline"] = r_a
    rail_ok = (BASELINE_RAIL_LO <= r_a["top1"] <= BASELINE_RAIL_HI)
    out["baseline_rail_ok"] = rail_ok
    print("  [seed=%d] ARM_A BASELINE top1=%.4f rail_ok=%s t=%.1fs" % (
        seed, r_a["top1"], rail_ok, r_a["elapsed_s_arm"]), flush=True)

    # ===== ARM B: PATH1_ROUTING_ONLY =====
    t_arm = time.time()
    r_b = arm_part_restricted(E, R, sq, W, chains_test, DEPTH, pick_path1,
                              "path1_routing_only_direct_query_to_partition")
    r_b["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    out["arm_b_path1_routing_only"] = r_b
    print("  [seed=%d] ARM_B PATH1_ROUTING_ONLY top1=%.4f t=%.1fs" % (
        seed, r_b["top1"], r_b["elapsed_s_arm"]), flush=True)

    # ===== ARM C: PATH2_CORTEX_COMPOSITION (the brain-faithful mechanism) =====
    t_arm = time.time()
    r_c = arm_part_restricted(
        E, R, sq, W, chains_test, DEPTH, pick_path2,
        "path2_vmpfc_schema_bayes_then_cortex_partition_then_hippo_cleanup")
    r_c["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    out["arm_c_path2_cortex_composition"] = r_c
    print(("  [seed=%d] ARM_C PATH2_CORTEX_COMPOSITION top1=%.4f "
           "(HP_band=[%.2f,%.2f] lift_C_A>=%.2f gap_to_oracle<=%.2f) "
           "t=%.1fs") % (
        seed, r_c["top1"], HP_PATH2_LO, HP_PATH2_HI, HP_LIFT_OVER_BASELINE,
        HP_GAP_TO_ORACLE_MAX, r_c["elapsed_s_arm"]), flush=True)

    # ===== ARM D: ORACLE_GROUND_TRUTH =====
    t_arm = time.time()
    r_d = arm_part_restricted(E, R, sq, W, chains_test, DEPTH, pick_oracle,
                              "oracle_ground_truth_partition_upper_bound")
    r_d["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    out["arm_d_oracle_ground_truth"] = r_d
    print("  [seed=%d] ARM_D ORACLE_GROUND_TRUTH top1=%.4f t=%.1fs" % (
        seed, r_d["top1"], r_d["elapsed_s_arm"]), flush=True)

    # ===== ARM E: SCHEMA_ONLY (ablation; no cortex composition) =====
    t_arm = time.time()
    r_e = arm_part_restricted(
        E, R, sq, W, chains_test, DEPTH, pick_schema_only,
        "schema_only_no_cortex_composition_ablation")
    r_e["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    out["arm_e_schema_only"] = r_e
    print("  [seed=%d] ARM_E SCHEMA_ONLY top1=%.4f t=%.1fs" % (
        seed, r_e["top1"], r_e["elapsed_s_arm"]), flush=True)

    # ===== ARM F: RANDOM (floor) =====
    t_arm = time.time()
    r_f = arm_part_restricted(E, R, sq, W, chains_test, DEPTH, pick_random,
                              "random_partition_floor")
    r_f["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    out["arm_f_random"] = r_f
    print("  [seed=%d] ARM_F RANDOM top1=%.4f t=%.1fs" % (
        seed, r_f["top1"], r_f["elapsed_s_arm"]), flush=True)

    # Lifts
    out["lift_c_over_a"] = round(r_c["top1"] - r_a["top1"], 4)
    out["lift_c_over_b"] = round(r_c["top1"] - r_b["top1"], 4)
    out["lift_c_over_e"] = round(r_c["top1"] - r_e["top1"], 4)
    out["lift_c_over_f"] = round(r_c["top1"] - r_f["top1"], 4)
    out["gap_d_minus_c"] = round(r_d["top1"] - r_c["top1"], 4)
    out["brain_faithfulness_verdict"] = (
        "PATH2_RICHER_THAN_PATH1"
        if (r_c["top1"] - r_b["top1"]) >= HP_LIFT_OVER_PATH1
        else "PATH2_NO_LIFT_OVER_PATH1"
    )

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

    a = mean_top1("arm_a_baseline")
    b = mean_top1("arm_b_path1_routing_only")
    c = mean_top1("arm_c_path2_cortex_composition")
    d = mean_top1("arm_d_oracle_ground_truth")
    e = mean_top1("arm_e_schema_only")
    f = mean_top1("arm_f_random")

    cv_c = cv_top1("arm_c_path2_cortex_composition")

    lift_c_a = c - a if not (math.isnan(c) or math.isnan(a)) else float("nan")
    lift_c_b = c - b if not (math.isnan(c) or math.isnan(b)) else float("nan")
    lift_c_e = c - e if not (math.isnan(c) or math.isnan(e)) else float("nan")
    lift_c_f = c - f if not (math.isnan(c) or math.isnan(f)) else float("nan")
    gap_d_c = d - c if not (math.isnan(d) or math.isnan(c)) else float("nan")

    # Cardinality (META_RULE_H)
    observed_units = sum(1 for p in per_seed for ak in ARM_KEYS if ak in p)
    cardinality_ok = (observed_units == EXPECTED_N_UNITS)

    # Arms-must-differ (META_RULE_AF)
    arms_hashes = _arms_must_differ_sha256(per_seed)
    unique_hashes = set(arms_hashes.values())
    arms_distinct = (len(unique_hashes) == len(ARM_KEYS))

    saturation_flag = (not math.isnan(c)) and c >= HP_SATURATION_CEIL
    rail_breach = sum(1 for p in per_seed
                      if not p.get("baseline_rail_ok", False))

    c_in_band = ((not math.isnan(c)) and HP_PATH2_LO <= c <= HP_PATH2_HI)

    summ = (
        "BASELINE_A=%.4f (rail_breach=%d/%d; target=%.3f band=[%.2f,%.2f]) "
        "PATH1_B=%.4f PATH2_C=%.4f (cv=%.3f in_band=%s) "
        "ORACLE_D=%.4f SCHEMA_E=%.4f RANDOM_F=%.4f "
        "lift_C_A=%.4f lift_C_B=%.4f lift_C_E=%.4f lift_C_F=%.4f "
        "gap_D_C=%.4f cardinality_ok=%s expected_units=%d observed_units=%d "
        "arms_distinct=%s saturation=%s HP_band=[%.2f,%.2f] depth=%d "
        "brain_faithful_PATH2_richer_than_PATH1=%s"
    ) % (
        a, rail_breach, len(per_seed), BASELINE_RAIL_TARGET,
        BASELINE_RAIL_LO, BASELINE_RAIL_HI,
        b, c, cv_c, c_in_band, d, e, f,
        lift_c_a, lift_c_b, lift_c_e, lift_c_f, gap_d_c,
        cardinality_ok, EXPECTED_N_UNITS, observed_units,
        arms_distinct, saturation_flag,
        HP_PATH2_LO, HP_PATH2_HI, DEPTH,
        ("True" if (not math.isnan(lift_c_b)) and lift_c_b >= HP_LIFT_OVER_PATH1
         else "False"),
    )

    # Cardinality gate FIRST (META_RULE_H)
    if not cardinality_ok:
        return ("HARD_FAIL_CARDINALITY_BREACH",
                "HARD_FAIL_CARDINALITY_BREACH: " + summ, arms_hashes)

    if not arms_distinct:
        return ("HARD_FAIL_ARMS_TIED",
                "HARD_FAIL_ARMS_TIED_NO_DISCRIMINATION: " + summ, arms_hashes)

    # HARD_FAIL: composition collapses at depth-15
    if (not math.isnan(c)) and c <= HF_PATH2_ABS:
        return ("HARD_FAIL_COMPOSITION_COLLAPSE",
                "HARD_FAIL_PATH2_COMPOSITION_COLLAPSE_AT_DEPTH15: " + summ,
                arms_hashes)

    # HARD_FAIL: no goal-info (PATH2 ~= random)
    if (not math.isnan(lift_c_f)) and lift_c_f < HP_LIFT_OVER_RANDOM:
        return ("HARD_FAIL_NO_GOAL_INFO",
                "HARD_FAIL_PATH2_NOT_DISTINGUISHED_FROM_RANDOM: " + summ,
                arms_hashes)

    # HARD_FAIL: saturated + insufficient lift
    if saturation_flag and (not math.isnan(lift_c_a)) \
            and lift_c_a < HF_LIFT_MIN_IF_SATURATED:
        return ("HARD_FAIL_SATURATION_WITHOUT_LIFT",
                "HARD_FAIL_SATURATION_FLAG_WITH_LIFT_BELOW_THRESHOLD: " + summ,
                arms_hashes)

    # Smoke verdict
    if RUN_MODE == "smoke":
        if (c_in_band
                and (not math.isnan(lift_c_a)) and lift_c_a >= HP_LIFT_OVER_BASELINE
                and (not math.isnan(lift_c_b)) and lift_c_b >= HP_LIFT_OVER_PATH1
                and (not math.isnan(lift_c_e)) and lift_c_e >= HP_LIFT_OVER_SCHEMA_ONLY
                and (not math.isnan(gap_d_c)) and gap_d_c <= HP_GAP_TO_ORACLE_MAX
                and not saturation_flag):
            return ("SMOKE_HARD_PASS",
                    ("SMOKE_HARD_PASS_BRAIN_COMPOSITION_3_PRIMITIVES_CHAIN_GRADE_"
                     "DEPTH15_UNSAT_BARRIER_1_BROKEN_VIA_VMPFC_CORTEX_HIPPO: ")
                    + summ, arms_hashes)
        # MIDDLE_BAND if PATH1 catches up (composition adds nothing)
        if c_in_band and (not math.isnan(lift_c_b)) \
                and lift_c_b < HP_LIFT_OVER_PATH1:
            return ("MIDDLE_BAND_COMPOSITION_NO_LIFT_OVER_PATH1",
                    "MIDDLE_BAND_PATH2_RUNS_BUT_NOT_RICHER_THAN_PATH1: " + summ,
                    arms_hashes)
        # MIDDLE_BAND if gap to oracle too wide
        if c_in_band and (not math.isnan(gap_d_c)) \
                and gap_d_c > HP_GAP_TO_ORACLE_MAX:
            return ("MIDDLE_BAND_COMPOSITION_TOO_FAR_FROM_ORACLE",
                    "MIDDLE_BAND_PATH2_IN_BAND_BUT_GAP_TO_ORACLE_TOO_WIDE: "
                    + summ, arms_hashes)
        if (not math.isnan(lift_c_a)) and lift_c_a >= MM_LIFT_MIN:
            return ("MIDDLE_BAND",
                    "MIDDLE_BAND_PARTIAL_PATH2_COMPOSITION_AT_DEPTH15: " + summ,
                    arms_hashes)
        return ("HARD_FAIL_LIFT_BELOW_THRESHOLD",
                "HARD_FAIL_LIFT_BELOW_THRESHOLD_AT_DEPTH15: " + summ,
                arms_hashes)

    # Full verdict (multi-seed; cv required for chain-grade)
    cv_ok = (not math.isnan(cv_c)) and cv_c < HP_CV_MAX

    if (c_in_band
            and (not math.isnan(lift_c_a)) and lift_c_a >= HP_LIFT_OVER_BASELINE
            and (not math.isnan(lift_c_b)) and lift_c_b >= HP_LIFT_OVER_PATH1
            and (not math.isnan(lift_c_e)) and lift_c_e >= HP_LIFT_OVER_SCHEMA_ONLY
            and (not math.isnan(gap_d_c)) and gap_d_c <= HP_GAP_TO_ORACLE_MAX
            and cv_ok and not saturation_flag):
        return ("HARD_PASS_CHAIN_GRADE_BRAIN_COMPOSITION_DEPTH15",
                ("HARD_PASS_CHAIN_GRADE_DEPTH15_UNSAT_BARRIER_1_BROKEN_VIA_"
                 "BRAIN_FAITHFUL_VMPFC_CORTEX_HIPPO_COMPOSITION: ") + summ,
                arms_hashes)

    if c_in_band and (not math.isnan(lift_c_b)) \
            and lift_c_b < HP_LIFT_OVER_PATH1:
        return ("MIDDLE_BAND_COMPOSITION_NO_LIFT_OVER_PATH1",
                "MIDDLE_BAND_PATH2_RUNS_BUT_NOT_RICHER_THAN_PATH1: " + summ,
                arms_hashes)

    if c_in_band and (not math.isnan(gap_d_c)) \
            and gap_d_c > HP_GAP_TO_ORACLE_MAX:
        return ("MIDDLE_BAND_COMPOSITION_TOO_FAR_FROM_ORACLE",
                "MIDDLE_BAND_PATH2_IN_BAND_BUT_GAP_TO_ORACLE_TOO_WIDE: " + summ,
                arms_hashes)

    if saturation_flag and (not math.isnan(lift_c_a)) \
            and lift_c_a >= HF_LIFT_MIN_IF_SATURATED:
        return ("MIDDLE_BAND_SATURATED_AUTO_DEMOTE",
                "MIDDLE_BAND_SATURATED_AUTO_DEMOTE_BIAS_Q: " + summ,
                arms_hashes)

    if (not math.isnan(lift_c_a)) and lift_c_a >= MM_LIFT_MIN:
        return ("MIDDLE_BAND",
                "MIDDLE_BAND_PARTIAL_PATH2_COMPOSITION_AT_DEPTH15: " + summ,
                arms_hashes)

    return ("HARD_FAIL_LIFT_BELOW_THRESHOLD",
            "HARD_FAIL_LIFT_BELOW_THRESHOLD_NO_COMPOSITION: " + summ,
            arms_hashes)


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
                                 run_config={"N": N_DIM, "run_mode": RUN_MODE,
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
            "expected_arms": list(ARM_KEYS),
            "arms_must_differ_sha256": ahashes,
        }
        write_metrics(od, metrics, results=per_seed)
        print("[atexit] wrote synth metrics.json (%d seeds)" % len(per_seed),
              flush=True)
    except SystemExit:
        raise
    except BaseException as ex:  # noqa: BLE001
        print("[atexit] FAIL: %s" % ex, flush=True)


atexit.register(_atexit_synth)


if __name__ == "__main__":
    print("[config] anchor=%s mode=%s seeds=%s | %s" % (
        ANCHOR_NAME, RUN_MODE, SEEDS, CONFIG_VERSION), flush=True)
    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)
    _RESULTS_HOLDER["out_dir"] = out_dir

    # Heartbeat (defensive pattern 4)
    hb_path = REPO / "data" / "heartbeats" / "exp_dev.timestamp"
    try:
        hb_path.write_text(time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                           encoding="utf-8")
    except Exception:
        pass

    run_config = {"N": N_DIM, "run_mode": RUN_MODE, "anchor": ANCHOR_NAME}
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print("[ckpt] done=%s remaining=%s" % (done, remaining), flush=True)

    for s in remaining:
        try:
            rec = run_seed(s)
            write_partial_key(out_dir, s, rec)
        except SystemExit:
            raise
        except BaseException as ex:  # noqa: BLE001
            # Crash diagnostic (defensive pattern 2)
            print("[CRASH_DIAGNOSTIC] seed=%d anchor=%s exc=%r" % (
                s, ANCHOR_NAME, ex), flush=True)
            raise

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
        "expected_arms": list(ARM_KEYS),
        "arms_must_differ_sha256": ahashes,
        "DESIGN_NOTE": (
            "BRAIN-FAITHFUL composition of 3 chain-grade primitives "
            "(vmPFC schema-Bayes + cortex partition activation + hippo "
            "restricted cleanup) to derive partition restriction WITHOUT an "
            "oracle. USER 2026-06-28 question: 'how does the brain do it?' "
            "Answer: complementary learning systems (CLS; McClelland-O'Reilly-"
            "McNaughton 1995). PATH 2 (this cell) = 3-primitive composition; "
            "PATH 1 (sibling cell) = routing-only single-primitive. HARD_PASS "
            "requires PATH2 in [0.50, 0.95] AND lift>=0.30 vs BASELINE AND "
            "gap<=0.05 vs ORACLE AND lift>=0.05 vs PATH1 AND lift>=0.10 vs "
            "SCHEMA_ONLY AND NOT saturated. Regime matches v5_hardened "
            "(N=8192 V_C=4000 d=15 psz=800; per_step_baseline=0.948 from "
            "MEASURED@V5_HARDENED_SMOKE_BASELINE_A_TOP1_D15). 6 arms x "
            "single-seed sibling (seed=19); siblings seed_7+other "
            "provide 3-cell redundancy against runner-zombie episodes "
            "(USER 2026-06-28 chunked directive). META_RULE_AC tagged; "
            "META_RULE_AF arms-must-differ SHA-256; META_RULE_AE absolute "
            "paths; META_RULE_AG edge-of-capacity; META_RULE_AH atomic "
            "metrics; META_RULE_AL bands LOCKED; META_RULE_AN substrate-"
            "empirical anchor; META_RULE_H cardinality; BIAS-Q saturation "
            "@0.95; Fix #28 per-arm reads. Sources: "
            "experiments/exp_substrate_multihop_partition_oracle_v5_hardened_"
            "FULL_seed_11_v1.py (template); "
            "data/exp_substrate_multihop_partition_oracle_v5_hardened_v1_smoke/"
            "metrics.json (BASELINE_A=0.39 ORACLE_B=0.90); pre-reg "
            "preregs/2026-06-28_substrate_partition_oracle_brain_composition_"
            "hint_v1.md."
        ),
    }
    write_metrics(out_dir, metrics, results=per_seed)
    print("[done] metrics.json written (%d seeds, %.1fs)" % (
        len(per_seed), metrics["elapsed_s"]), flush=True)
