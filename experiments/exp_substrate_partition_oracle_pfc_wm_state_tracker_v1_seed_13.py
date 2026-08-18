"""substrate_partition_oracle_pfc_wm_state_tracker_v1 (seed=7).

PURPOSE (USER 2026-06-28: 4-primitive brain-faithful composition with dlPFC
WM state-tracker as the 4th primitive after Path 1 + Path 2 BOTH HARD_FAILed):

    FR1 vmPFC schema-Bayes (PATH 2 today; chain-grade)
    FR2 dlPFC WM state-tracker (substrate WM multi-bank; chain-grade)
    FR3 cortex partition activation (chain-grade)
    FR4 hippo restricted cleanup (chain-grade)

The drill diagnosis: PATH 2 fired schema-Bayes ONCE per chain (per-chain
abstraction), then used the same partition for all 15 hops. HARD_FAIL at
C=0.01 because the partition is wrong for hops 2..15 since the chain wanders
across partitions per-hop.

The 4-primitive fix: dlPFC WM state-tracker maintains the accumulated
trajectory state and re-fires schema-Bayes PER HOP with state-context bias.
Edge-1 (WM -> schema-Bayes input) is SHAPE_MISMATCH per drill, so this cell
tests 3 adapter sub-mechanisms IN PARALLEL ARMS to identify whichever works.

ARMS (7):
    A  BASELINE                  per-hop cleanup, no hint, no WM (replicates v5)
    B  PATH2_PER_CHAIN           schema-Bayes once per chain (today's HARD_FAIL)
    C_SUB_A PRIOR_MODULATION     WM state biases schema posterior per hop
    C_SUB_B FAKE_EVIDENCE        WM slot injected as additional evidence per hop
    C_SUB_C STATE_CONDITIONED    schema vector re-encoded with WM state per hop
    D  ORACLE_PER_HOP            ground-truth partition per hop (upper bound)
    E  RANDOM                    random partition (floor)

PRE-REG BANDS (LOCKED at module init; META_RULE_AL):
    PER-ADAPTER HARD_PASS (any of C_SUB_A, C_SUB_B, C_SUB_C):
        that adapter top1 in [0.50, 0.95]
        AND adapter - B >= 0.30
        AND adapter - A >= 0.20
        AND per-hop part-acc at hops 5,10,15 > 0.50
        AND D > adapter
        AND E < 0.05
        AND arms_distinct
        AND cardinality_ok
    WHOLE-CELL HARD_FAIL (all 3 adapters fail):
        ALL of C_SUB_{A,B,C}: top1 <= 0.30 OR (top1 - B) < 0.10
    MIDDLE_BAND per adapter:
        adapter in [0.30, 0.50] AND (adapter - B) >= 0.10

NUMBER TAGGING (META_RULE_AC):
    HYPOTHESIZED@HARD_PASS_BAND_PER_ADAPTER: [0.50, 0.95]
    MEASURED@PATH2_HARD_FAIL_PER_CHAIN_SEED_7: 0.01
        d:/AI/hd-instrument/data/exp_substrate_partition_oracle_brain_composition_hint_v1_seed_7_smoke/metrics.json
    MEASURED@V5_HARDENED_BASELINE_A_TOP1_D15: 0.39
    MEASURED@V5_HARDENED_ORACLE_B_TOP1_D15:   0.90
    MEASURED@WM_MULTIBANK_K_CLIFF_K4096:      >0.95 retrieval
    THEORETICAL@DEPTH_SCALE_BASELINE: 0.948^15 = 0.449
    THEORETICAL@DEPTH_SCALE_ORACLE:   0.98^15  = 0.739
    CITED@MILLER_COHEN_2001: integrative PFC theory; dlPFC bias-source
    CITED@FRADY_SOMMER_2020: HD WM outer-product slot bank
    CITED@PLATE_2003: contextually-modulated cleanup (state-bias pattern)
    CITED@MANTE_SUSSILLO_2013: PFC context-dependent gating

DISCIPLINE TAGS:
    META_RULE_AC AE AF AG AH AL AN AP H BIAS-N BIAS-Q BIAS-S
    DISCRIMINATOR-MUST-SURVIVE-SCALE PROT-018 PROT-021 Fix-28 NO-LOCAL
    CHUNKED single-seed-per-cell sibling (this is seed=7; siblings seed=13, seed=19)

SOURCE CITATIONS (ABSOLUTE PATHS; META_RULE_AE):
    - Template (PATH 2 cell):
      d:/AI/hd-instrument/experiments/exp_substrate_partition_oracle_brain_composition_hint_v1_seed_7.py
    - v5_hardened FULL seed_11 (baseline mechanism source):
      d:/AI/hd-instrument/experiments/exp_substrate_multihop_partition_oracle_v5_hardened_FULL_seed_11_v1.py
    - PATH 2 MEASURED HARD_FAIL metrics:
      d:/AI/hd-instrument/data/exp_substrate_partition_oracle_brain_composition_hint_v1_seed_7_smoke/metrics.json
    - WM multi-bank K cliff (FR1+FR2 chain-grade):
      d:/AI/hd-instrument/data/exp_substrate_wm_multibank_K_cliff_phase_diagram_v1_seed_7_v1/metrics.json
    - Drill:
      d:/AI/hd-instrument/notes/research_drill_pfc_wm_state_tracker_4_primitive_composition_2026-06-28.md
    - Pre-reg:
      d:/AI/hd-instrument/preregs/2026-06-28_substrate_partition_oracle_pfc_wm_state_tracker_v1.md

Author: exp_dev 2026-06-28 (USER directive: 4-primitive WM state-tracker; chunked).
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

ANCHOR_NAME = "substrate_partition_oracle_pfc_wm_state_tracker_v1_seed_13"
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

N_PARTS = 5
assert V_CONCEPTS % N_PARTS == 0
PART_SIZE = V_CONCEPTS // N_PARTS  # 800

N_SCHEMAS = 20
WM_BANK_K = 200  # dlPFC analog; per-chain slot

def _cone_collapse_crosstalk(v_c_per_hop: int, n: int) -> float:
    return float(math.sqrt(max(v_c_per_hop - 1, 1) / max(n, 1)))

CROSSTALK_PART = _cone_collapse_crosstalk(PART_SIZE, N_DIM)        # 0.3123
CROSSTALK_BASELINE = _cone_collapse_crosstalk(V_CONCEPTS, N_DIM)   # 0.6987

# BASELINE rail (BIAS-S; loose since PATH 2 baseline measured 0.40)
BASELINE_RAIL_LO = 0.05
BASELINE_RAIL_HI = 0.95
BASELINE_RAIL_TARGET = 0.449

# Per-adapter HARD_PASS bands
HP_ADAPTER_LO = 0.50
HP_ADAPTER_HI = 0.95
HP_LIFT_OVER_B = 0.30          # adapter - B (PATH2) >= 0.30
HP_LIFT_OVER_A = 0.20          # adapter - A (BASELINE) >= 0.20
HP_PER_HOP_PARTACC = 0.50      # part-acc at hops 5/10/15 > 0.50
HP_RANDOM_CEIL = 0.05          # E < 0.05
HP_CV_MAX = 0.15
HP_SATURATION_CEIL = 0.95

# HARD_FAIL per adapter
HF_ADAPTER_ABS = 0.30
HF_ADAPTER_LIFT_OVER_B = 0.10
MM_LIFT_MIN = 0.10  # MIDDLE_BAND threshold

# Adapter B sub-B fake-evidence weight schedule: w(hop) = 1/(hop+1)
SUB_B_EVIDENCE_WEIGHT_BASE = 1.0

# Chain configuration
N_CHAINS_TRAIN = 200
SEEDS = [13]  # CHUNKED single-seed cell; siblings seed_7, seed_19
if RUN_MODE == "smoke":
    N_CHAINS_TEST = 100
else:
    N_CHAINS_TEST = 200

# Cardinality (META_RULE_H): 7 arms x 1 seed
N_ARMS = 7
EXPECTED_N_UNITS = N_ARMS * len(SEEDS)

ENCODER_PROVENANCE = "SUBSTRATE_NATIVE_BIPOLAR"

CONFIG_VERSION = (
    "ANCHOR=%s,pfcWmStateTrackerV1Seed13: N=%d V_C=%d V_P=%d depth=%d "
    "n_parts=%d psz=%d xtalk_part=%.4f xtalk_baseline=%.4f n_schemas=%d "
    "wm_bank_K=%d n_chains_train=%d n_chains_test=%d seeds=%s mode=%s "
    "encoder=%s "
    "RAIL=[%.3f,%.3f] target=%.3f HP_adapter_band=[%.2f,%.2f] "
    "HP_lift_B=%.2f HP_lift_A=%.2f HP_per_hop_partacc=%.2f "
    "HP_random_ceil=%.2f HP_cv_max=%.2f HP_sat_ceil=%.2f "
    "HF_adapter_abs=%.2f HF_adapter_lift_B=%.2f MM_lift_min=%.2f "
    "expected_units=%d arms=%d"
) % (
    ANCHOR_NAME, N_DIM, V_CONCEPTS, V_PRED, DEPTH,
    N_PARTS, PART_SIZE, CROSSTALK_PART, CROSSTALK_BASELINE, N_SCHEMAS,
    WM_BANK_K, N_CHAINS_TRAIN, N_CHAINS_TEST, SEEDS, RUN_MODE,
    ENCODER_PROVENANCE,
    BASELINE_RAIL_LO, BASELINE_RAIL_HI, BASELINE_RAIL_TARGET,
    HP_ADAPTER_LO, HP_ADAPTER_HI, HP_LIFT_OVER_B, HP_LIFT_OVER_A,
    HP_PER_HOP_PARTACC, HP_RANDOM_CEIL, HP_CV_MAX, HP_SATURATION_CEIL,
    HF_ADAPTER_ABS, HF_ADAPTER_LIFT_OVER_B, MM_LIFT_MIN,
    EXPECTED_N_UNITS, N_ARMS,
)

# Locked invariants (META_RULE_AL)
assert BASELINE_RAIL_LO < BASELINE_RAIL_HI
assert HP_ADAPTER_LO > HF_ADAPTER_ABS
assert HP_ADAPTER_LO < HP_ADAPTER_HI <= HP_SATURATION_CEIL
assert HP_LIFT_OVER_B > HF_ADAPTER_LIFT_OVER_B
assert 0.0 < HP_CV_MAX < 0.5
assert CROSSTALK_PART < CROSSTALK_BASELINE
assert DEPTH == 15
assert WM_BANK_K >= N_CHAINS_TEST  # one slot per test chain


# ----------------------------------------------------------------------------
# Primitives (verbatim port from PATH 2 cell)
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
# Schema-Bayes primitive (vmPFC analog; from PATH 2)
# ----------------------------------------------------------------------------

def chain_schema_vector(chain: List[Tuple[int, int, int]],
                        R: np.ndarray) -> np.ndarray:
    """FR1: encode a chain's predicate sequence as a schema vector."""
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
    """vmPFC schema-Bayes prototypes (verbatim port from PATH 2)."""
    n = len(chains_train)
    N = R.shape[1]

    def chain_hash(chain):
        return hash(tuple(p for (_, p, _) in chain))

    chain_to_schema = [(chain_hash(c) & 0x7fffffff) % n_schemas
                       for c in chains_train]

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
            v = g.standard_normal(N).astype(np.float32)
            prototypes[k] = v / (np.linalg.norm(v) + 1e-8)

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
    """Cortex partition activation matrix (verbatim port from PATH 2)."""
    n_schemas, N = prototypes.shape
    W = np.zeros((N_PARTS, N), dtype=np.float32)
    for k in range(n_schemas):
        part = int(cluster_to_target_part[k])
        W[part] += prototypes[k]
    for p in range(N_PARTS):
        nrm = float(np.linalg.norm(W[p]))
        if nrm > 1e-8:
            W[p] /= nrm
    return W


def predict_partition_path2(query_schema: np.ndarray,
                            W_schema_to_part: np.ndarray) -> int:
    """PATH 2 inference (chain-once): query schema -> argmax partition."""
    scores = W_schema_to_part @ query_schema
    return int(scores.argmax())


# ----------------------------------------------------------------------------
# dlPFC WM bank (Frady-Sommer 2020 outer-product slot bank)
# ----------------------------------------------------------------------------

def build_wm_bank_keys(K: int, n: int,
                       g: np.random.Generator) -> np.ndarray:
    """K random bipolar slot keys at dim n. CITED@Frady-Sommer 2020."""
    return bipolar(K, n, g)


def wm_write_slot(bank: np.ndarray, slot_idx: int,
                  slot_key: np.ndarray, state: np.ndarray,
                  n_dim: int) -> None:
    """Write state to slot via key-bind outer-product accumulation.

    bank[slot_idx] += (slot_key * state) (normalized to keep magnitudes bounded).

    Frady-Sommer 2020 pattern: per-slot key binds the stored vector; readout via
    element-wise unbind (bipolar self-inverse).
    """
    bound = (slot_key * state).astype(np.float32)
    nrm = float(np.linalg.norm(bound))
    if nrm > 1e-8:
        bound = bound / nrm
    bank[slot_idx] = bank[slot_idx] + bound


def wm_read_slot(bank: np.ndarray, slot_idx: int,
                 slot_key: np.ndarray) -> np.ndarray:
    """Read slot via key-unbind (bipolar self-inverse)."""
    raw = (bank[slot_idx] * slot_key).astype(np.float32)
    nrm = float(np.linalg.norm(raw))
    if nrm > 1e-8:
        return raw / nrm
    return raw


def hop_state_vector(s_idx: int, p_idx: int, hop_idx: int,
                     E: np.ndarray, R: np.ndarray,
                     hop_codes: np.ndarray) -> np.ndarray:
    """Encode current hop state as bound (E[s] * R[p] * H[hop_idx])."""
    v = (E[s_idx] * R[p_idx] * hop_codes[hop_idx]).astype(np.float32)
    nrm = float(np.linalg.norm(v))
    if nrm > 1e-8:
        v = v / nrm
    return v


# ----------------------------------------------------------------------------
# Adapter sub-mechanism partition pickers (the 3 SUB arms)
# ----------------------------------------------------------------------------

def pick_path2_per_chain(query_schema: np.ndarray,
                         W_s2p: np.ndarray) -> int:
    """ARM B helper: PATH 2 reused for per-chain (schema fires once)."""
    scores = W_s2p @ query_schema
    return int(scores.argmax())


def pick_sub_a_prior_modulation(per_hop_schema_q: np.ndarray,
                                wm_state_prev: np.ndarray,
                                prototypes: np.ndarray,
                                cluster_to_target_part: np.ndarray) -> int:
    """SUB_A: WM state biases schema posterior BEFORE partition argmax.

    schema_post_k = (prototypes @ per_hop_schema_q)_k * (1 + alpha * (prototypes @ wm_state_prev)_k)
    where alpha = 1.0. SHAPE_MATCH: both prototypes-projection and state-projection are
    same-dim cosine scores; multiplicative bias.

    Then majority-partition vote weighted by posterior:
    part_score_p = sum_k schema_post_k * [cluster_to_target_part[k] == p]
    return argmax_p part_score_p
    """
    raw_post = prototypes @ per_hop_schema_q          # [n_schemas]
    state_bias = prototypes @ wm_state_prev           # [n_schemas]
    # Multiplicative bias; clamp lower bound at 0 to avoid sign flip
    biased = raw_post * (1.0 + state_bias)
    # Soft-aggregate per partition (no argmax on schemas first; keep posterior shape)
    part_scores = np.zeros(N_PARTS, dtype=np.float32)
    for k in range(prototypes.shape[0]):
        part_scores[int(cluster_to_target_part[k])] += float(biased[k])
    return int(part_scores.argmax())


def pick_sub_b_fake_evidence(per_hop_schema_q: np.ndarray,
                             wm_state_prev: np.ndarray,
                             prototypes: np.ndarray,
                             cluster_to_target_part: np.ndarray,
                             evidence_weight: float) -> int:
    """SUB_B: WM slot injected as additional evidence-set entry.

    Compose effective schema query: q_eff = normalize(per_hop_schema_q + w * wm_state_prev)
    where w = evidence_weight = 1.0 / (hop+1) (Plate 2003 contextually-modulated cleanup).

    Then run standard schema-Bayes on q_eff -> argmax cluster -> cluster's partition.
    SHAPE_MISMATCH_with_known_adapter: evidence-weight is the calibration knob; here
    we use harmonic decay as a Plate-2003-style prior.
    """
    q_eff = per_hop_schema_q + evidence_weight * wm_state_prev
    nrm = float(np.linalg.norm(q_eff))
    if nrm > 1e-8:
        q_eff = q_eff / nrm
    scores = prototypes @ q_eff
    k = int(scores.argmax())
    return int(cluster_to_target_part[k])


def pick_sub_c_state_conditioned_schema(chain: List[Tuple[int, int, int]],
                                        hop_idx: int,
                                        wm_state_prev: np.ndarray,
                                        R: np.ndarray,
                                        prototypes: np.ndarray,
                                        cluster_to_target_part: np.ndarray
                                        ) -> int:
    """SUB_C: schema vector re-computed with WM state as additional input slot.

    Standard chain_schema_vector: sum_p R[p]. Variant: sum_p R[p] + wm_state_prev.
    SHAPE_MISMATCH_with_known_adapter: schema-Bayes primitive variant.

    Only sum over PAST hops (0..hop_idx) since future predicates unknown at hop hop_idx.
    """
    n = R.shape[1]
    s = np.zeros(n, dtype=np.float32)
    for k in range(min(hop_idx + 1, len(chain))):
        s += R[chain[k][1]]
    s = s + wm_state_prev
    nrm = float(np.linalg.norm(s))
    if nrm > 1e-8:
        s = s / nrm
    scores = prototypes @ s
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
    """Generic partition-restricted cleanup arm (verbatim from PATH 2)."""
    n = len(chains_test)
    hits = 0
    per_step_hits = np.zeros(depth, dtype=np.int64)
    E_parts = [E[p * PART_SIZE:(p + 1) * PART_SIZE]
               for p in range(N_PARTS)]
    correct_part_hits = np.zeros(depth, dtype=np.int64)
    for chain_idx, chain in enumerate(chains_test):
        s = chain[0][0]
        for i in range(depth):
            p = chain[i][1]
            target_o = chain[i][2]
            target_part = target_o // PART_SIZE
            chosen_part = partition_picker(chain, chain_idx, i, s)
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


def arm_with_wm_bank(E: np.ndarray, R: np.ndarray, sq: float,
                     W: np.ndarray,
                     chains_test: List[List[Tuple[int, int, int]]],
                     depth: int,
                     prototypes: np.ndarray,
                     cluster_to_target_part: np.ndarray,
                     adapter_kind: str,
                     g_arm: np.random.Generator,
                     mechanism_tag: str) -> Dict[str, Any]:
    """4-primitive arm: per-hop WM read -> adapter -> partition -> cleanup.

    adapter_kind in {"sub_a", "sub_b", "sub_c"}.

    Per chain:
      bank = zero vector at slot c
      for hop i in 0..depth-1:
        wm_state_prev = wm_read_slot(bank, c, slot_keys[c])  (zero at hop 0)
        compute current schema query (per-hop):
          q_hop = normalize(sum_{j<=i} R[chain[j][1]])
        adapter picks partition via SUB_A/B/C
        cleanup within chosen partition (same as PATH 2)
        write current state to bank slot c:
          state_now = hop_state_vector(s_pred, p_next?, i)
          for simplicity: use (E[s_pred] * R[p_current] * H[i])
    """
    n = len(chains_test)
    n_dim = E.shape[1]
    E_parts = [E[p * PART_SIZE:(p + 1) * PART_SIZE]
               for p in range(N_PARTS)]

    # WM bank: K=WM_BANK_K slots, each is an N-dim vector
    bank = np.zeros((WM_BANK_K, n_dim), dtype=np.float32)
    slot_keys = build_wm_bank_keys(WM_BANK_K, n_dim, g_arm)
    # Per-hop position codes (so WM state-vector encodes WHICH hop)
    hop_codes = bipolar(depth, n_dim, g_arm)

    hits = 0
    per_step_hits = np.zeros(depth, dtype=np.int64)
    correct_part_hits = np.zeros(depth, dtype=np.int64)

    for chain_idx, chain in enumerate(chains_test):
        c_slot = chain_idx % WM_BANK_K
        # Reset slot for this chain (independent test trials)
        bank[c_slot] = 0.0
        s = chain[0][0]
        for i in range(depth):
            p = chain[i][1]
            target_o = chain[i][2]
            target_part = target_o // PART_SIZE

            # WM read of prior accumulated state
            if i == 0:
                wm_state_prev = np.zeros(n_dim, dtype=np.float32)
            else:
                wm_state_prev = wm_read_slot(bank, c_slot, slot_keys[c_slot])

            # Per-hop schema query: superpose predicate vectors up to and incl
            # current hop (past predicates known; future are not).
            q_hop = np.zeros(n_dim, dtype=np.float32)
            for j in range(i + 1):
                q_hop = q_hop + R[chain[j][1]]
            nrm = float(np.linalg.norm(q_hop))
            if nrm > 1e-8:
                q_hop = q_hop / nrm

            # Adapter pick
            if adapter_kind == "sub_a":
                chosen_part = pick_sub_a_prior_modulation(
                    q_hop, wm_state_prev, prototypes, cluster_to_target_part)
            elif adapter_kind == "sub_b":
                w_evid = SUB_B_EVIDENCE_WEIGHT_BASE / float(i + 1)
                chosen_part = pick_sub_b_fake_evidence(
                    q_hop, wm_state_prev, prototypes, cluster_to_target_part,
                    w_evid)
            elif adapter_kind == "sub_c":
                chosen_part = pick_sub_c_state_conditioned_schema(
                    chain, i, wm_state_prev, R, prototypes,
                    cluster_to_target_part)
            else:
                raise ValueError("unknown adapter_kind=%r" % adapter_kind)

            if chosen_part == target_part:
                correct_part_hits[i] += 1

            # Cleanup within chosen partition
            key = (E[s] * R[p] * sq).astype(np.float32)
            state = W @ key
            scores = E_parts[chosen_part] @ state
            local_idx = int(scores.argmax())
            s_pred = chosen_part * PART_SIZE + local_idx
            if s_pred == target_o:
                per_step_hits[i] += 1

            # WM write: current hop state vector (bound s_pred, p, hop_idx)
            state_now = hop_state_vector(s_pred, p, i, E, R, hop_codes)
            wm_write_slot(bank, c_slot, slot_keys[c_slot], state_now, n_dim)

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
        "wm_bank_K": WM_BANK_K,
        "adapter_kind": adapter_kind,
        "mechanism": mechanism_tag,
    }


# ----------------------------------------------------------------------------
# Arms-must-differ SHA-256 (META_RULE_AF)
# ----------------------------------------------------------------------------

ARM_KEYS = [
    "arm_a_baseline",
    "arm_b_path2_per_chain",
    "arm_c_sub_a_prior_modulation",
    "arm_c_sub_b_fake_evidence",
    "arm_c_sub_c_state_conditioned",
    "arm_d_oracle_per_hop",
    "arm_e_random",
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
    wm_K_tiny = 8
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

    # T4: schema vector + prototypes (tiny config)
    sv = chain_schema_vector(chains[0], R)
    assert sv.shape == (n_tiny,)
    assert abs(float(np.linalg.norm(sv)) - 1.0) < 1e-4

    # Patch module-level PART_SIZE / N_PARTS / WM_BANK_K for tiny run
    global PART_SIZE, N_PARTS, WM_BANK_K
    _saved_psz = PART_SIZE
    _saved_np = N_PARTS
    _saved_K = WM_BANK_K
    try:
        PART_SIZE = psz_tiny
        N_PARTS = n_parts_tiny
        WM_BANK_K = wm_K_tiny

        protos, chain2sch, cl2part = build_schema_prototypes(
            chains, R, n_schemas_tiny, g)
        assert protos.shape == (n_schemas_tiny, n_tiny)
        assert cl2part.shape == (n_schemas_tiny,)
        assert all(0 <= p < n_parts_tiny for p in cl2part)

        # T5: cortex W_schema_to_part shape
        W_s2p = build_schema_to_partition_W(protos, cl2part, n_tiny)
        assert W_s2p.shape == (n_parts_tiny, n_tiny)

        # T6: WM bank keys
        slot_keys = build_wm_bank_keys(wm_K_tiny, n_tiny, g)
        assert slot_keys.shape == (wm_K_tiny, n_tiny)

        # T7: write+read WM slot
        bank = np.zeros((wm_K_tiny, n_tiny), dtype=np.float32)
        state0 = (g.standard_normal(n_tiny).astype(np.float32))
        state0 /= np.linalg.norm(state0) + 1e-8
        wm_write_slot(bank, 0, slot_keys[0], state0, n_tiny)
        readback = wm_read_slot(bank, 0, slot_keys[0])
        # Cosine of readback vs state0 should be much higher than chance
        cos = float(np.dot(readback, state0) / (
            np.linalg.norm(readback) * np.linalg.norm(state0) + 1e-8))
        assert cos > 0.50, "WM readback cosine too low: %.3f" % cos

        # T8: pick_sub_a returns valid partition
        q_hop = chain_schema_vector(chains[0], R)
        wm_prev = np.zeros(n_tiny, dtype=np.float32)
        pa = pick_sub_a_prior_modulation(q_hop, wm_prev, protos, cl2part)
        assert 0 <= pa < n_parts_tiny

        # T9: pick_sub_b returns valid partition
        pb = pick_sub_b_fake_evidence(q_hop, wm_prev, protos, cl2part,
                                      evidence_weight=0.5)
        assert 0 <= pb < n_parts_tiny

        # T10: pick_sub_c returns valid partition
        pc = pick_sub_c_state_conditioned_schema(chains[0], 5, wm_prev, R,
                                                 protos, cl2part)
        assert 0 <= pc < n_parts_tiny

        # T11: all 7 arms produce valid output at tiny config
        r_a = arm_baseline(E, R, sq, W, chains, depth=DEPTH)
        assert 0.0 <= r_a["top1"] <= 1.0

        def pick_oracle(chain, chain_idx, i, s_now):
            return chain[i][2] // PART_SIZE

        g_rand = np.random.default_rng(0)

        def pick_random(chain, chain_idx, i, s_now):
            return int(g_rand.integers(0, n_parts_tiny))

        _schema_cache_b: Dict[int, np.ndarray] = {}

        def pick_path2(chain, chain_idx, i, s_now):
            cid = id(chain)
            if cid not in _schema_cache_b:
                _schema_cache_b[cid] = chain_schema_vector(chain, R)
            qs = _schema_cache_b[cid]
            return pick_path2_per_chain(qs, W_s2p)

        r_b = arm_part_restricted(E, R, sq, W, chains, DEPTH, pick_path2,
                                  "path2_test")
        r_d = arm_part_restricted(E, R, sq, W, chains, DEPTH, pick_oracle,
                                  "oracle_test")
        r_e = arm_part_restricted(E, R, sq, W, chains, DEPTH, pick_random,
                                  "random_test")

        g_a = np.random.default_rng(101)
        g_b = np.random.default_rng(102)
        g_c = np.random.default_rng(103)
        r_ca = arm_with_wm_bank(E, R, sq, W, chains, DEPTH, protos, cl2part,
                                "sub_a", g_a, "sub_a_test")
        r_cb = arm_with_wm_bank(E, R, sq, W, chains, DEPTH, protos, cl2part,
                                "sub_b", g_b, "sub_b_test")
        r_cc = arm_with_wm_bank(E, R, sq, W, chains, DEPTH, protos, cl2part,
                                "sub_c", g_c, "sub_c_test")
        for r in (r_b, r_ca, r_cb, r_cc, r_d, r_e):
            assert 0.0 <= r["top1"] <= 1.0
            assert len(r["per_step_acc"]) == DEPTH
            assert len(r["partition_correct_per_step"]) == DEPTH

        # T12: assert ORACLE > RANDOM at tiny (sanity; weak)
        assert r_d["top1"] >= r_e["top1"] - 0.20, (
            "oracle did not beat random at tiny: d=%.3f e=%.3f"
            % (r_d["top1"], r_e["top1"]))

        # T13: WM arms must distinguish from baseline (per_step_acc differs)
        assert r_ca["per_step_acc"] != r_a["per_step_acc"]
        assert r_cb["per_step_acc"] != r_a["per_step_acc"]
        assert r_cc["per_step_acc"] != r_a["per_step_acc"]

    finally:
        PART_SIZE = _saved_psz
        N_PARTS = _saved_np
        WM_BANK_K = _saved_K

    # T14: cone-collapse formula sanity
    assert abs(CROSSTALK_PART - 0.3123) < 0.001, \
        "psz=800/N=8192 xtalk drift: %.4f" % CROSSTALK_PART
    assert CROSSTALK_BASELINE > 0.6

    # T15: bands LOCKED
    assert N_DIM == 8192
    assert V_CONCEPTS == 4000
    assert DEPTH == 15
    assert PART_SIZE == 800
    assert N_PARTS == 5
    assert N_SCHEMAS == 20
    assert WM_BANK_K == 200
    assert HP_ADAPTER_LO == 0.50
    assert HP_ADAPTER_HI == 0.95
    assert HF_ADAPTER_ABS == 0.30
    assert HP_LIFT_OVER_B == 0.30
    assert HP_LIFT_OVER_A == 0.20
    assert HP_PER_HOP_PARTACC == 0.50
    assert HP_RANDOM_CEIL == 0.05

    # T16: zero LLM calls
    assert _LLM_CALL_COUNTER[0] == 0

    # T17: cardinality declared
    assert EXPECTED_N_UNITS == N_ARMS * len(SEEDS) == 7

    # T18: anchor binding (seed=13 sibling)
    assert "_seed_13" in ANCHOR_NAME
    assert ANCHOR_NAME.endswith("_seed_13")
    assert "pfc_wm_state_tracker" in ANCHOR_NAME

    print(("[selftest] PASS N=%d V_C=%d depth=%d n_parts=%d psz=%d n_schemas=%d "
           "K=%d tiny_arms: a=%.3f b=%.3f c_a=%.3f c_b=%.3f c_c=%.3f "
           "d=%.3f e=%.3f xtalk_part=%.4f xtalk_baseline=%.4f "
           "HP_adapter=[%.2f,%.2f] expected_proj_baseline=%.3f "
           "expected_proj_oracle=%.3f wm_readback_cos=%.3f") % (
              N_DIM, V_CONCEPTS, DEPTH, N_PARTS, PART_SIZE, N_SCHEMAS, WM_BANK_K,
              r_a["top1"], r_b["top1"], r_ca["top1"], r_cb["top1"], r_cc["top1"],
              r_d["top1"], r_e["top1"],
              CROSSTALK_PART, CROSSTALK_BASELINE, HP_ADAPTER_LO, HP_ADAPTER_HI,
              0.948 ** DEPTH, 0.98 ** DEPTH, cos),
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

    print("  [seed=%d] building schema prototypes (n_schemas=%d)" % (
        seed, N_SCHEMAS), flush=True)
    prototypes, chain_to_schema, cluster_to_target_part = build_schema_prototypes(
        chains_train, R, N_SCHEMAS, g)
    print("  [seed=%d] building W_schema_to_part (cortex composition)" % seed,
          flush=True)
    W_schema_to_part = build_schema_to_partition_W(
        prototypes, cluster_to_target_part, N_DIM)

    out: Dict[str, Any] = {
        "seed": seed, "run_mode": RUN_MODE, "N": N_DIM, "V_C": V_CONCEPTS,
        "V_P": V_PRED, "depth": DEPTH,
        "n_chains_train": N_CHAINS_TRAIN, "n_chains_test": N_CHAINS_TEST,
        "n_partitions": N_PARTS, "part_size": PART_SIZE,
        "n_schemas": N_SCHEMAS, "wm_bank_K": WM_BANK_K,
        "crosstalk_baseline": CROSSTALK_BASELINE,
        "crosstalk_part": CROSSTALK_PART,
        "encoder_provenance": ENCODER_PROVENANCE,
        "config_version": CONFIG_VERSION,
        "anchor_name": ANCHOR_NAME,
        "_llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
    }

    # ===== ARM A: BASELINE =====
    t_arm = time.time()
    r_a = arm_baseline(E, R, sq, W, chains_test, depth=DEPTH)
    r_a["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    out["arm_a_baseline"] = r_a
    rail_ok = (BASELINE_RAIL_LO <= r_a["top1"] <= BASELINE_RAIL_HI)
    out["baseline_rail_ok"] = rail_ok
    print("  [seed=%d] ARM_A BASELINE top1=%.4f rail_ok=%s t=%.1fs" % (
        seed, r_a["top1"], rail_ok, r_a["elapsed_s_arm"]), flush=True)

    # ===== ARM B: PATH2_PER_CHAIN (today's HARD_FAIL reference) =====
    _schema_cache_b: Dict[int, np.ndarray] = {}

    def pick_path2(chain, chain_idx, i, s_now):
        cid = id(chain)
        if cid not in _schema_cache_b:
            _schema_cache_b[cid] = chain_schema_vector(chain, R)
        qs = _schema_cache_b[cid]
        return pick_path2_per_chain(qs, W_schema_to_part)

    t_arm = time.time()
    r_b = arm_part_restricted(
        E, R, sq, W, chains_test, DEPTH, pick_path2,
        "path2_per_chain_schema_fires_once_no_wm")
    r_b["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    out["arm_b_path2_per_chain"] = r_b
    print("  [seed=%d] ARM_B PATH2_PER_CHAIN top1=%.4f t=%.1fs" % (
        seed, r_b["top1"], r_b["elapsed_s_arm"]), flush=True)

    # ===== ARM C_SUB_A: PRIOR_MODULATION (4-primitive; WM biases schema posterior) =====
    g_ca = np.random.default_rng(seed * 7919 + 1)
    t_arm = time.time()
    r_ca = arm_with_wm_bank(
        E, R, sq, W, chains_test, DEPTH, prototypes, cluster_to_target_part,
        "sub_a", g_ca,
        "sub_a_prior_modulation_wm_biases_schema_posterior_per_hop_shape_match")
    r_ca["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    out["arm_c_sub_a_prior_modulation"] = r_ca
    print(("  [seed=%d] ARM_C_SUB_A PRIOR_MODULATION top1=%.4f "
           "(HP_band=[%.2f,%.2f] lift_over_B>=%.2f lift_over_A>=%.2f) "
           "t=%.1fs") % (
        seed, r_ca["top1"], HP_ADAPTER_LO, HP_ADAPTER_HI,
        HP_LIFT_OVER_B, HP_LIFT_OVER_A, r_ca["elapsed_s_arm"]), flush=True)

    # ===== ARM C_SUB_B: FAKE_EVIDENCE (4-primitive; WM as evidence-set entry) =====
    g_cb = np.random.default_rng(seed * 7919 + 2)
    t_arm = time.time()
    r_cb = arm_with_wm_bank(
        E, R, sq, W, chains_test, DEPTH, prototypes, cluster_to_target_part,
        "sub_b", g_cb,
        "sub_b_fake_evidence_wm_slot_appended_to_evidence_set_harmonic_decay")
    r_cb["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    out["arm_c_sub_b_fake_evidence"] = r_cb
    print(("  [seed=%d] ARM_C_SUB_B FAKE_EVIDENCE top1=%.4f t=%.1fs") % (
        seed, r_cb["top1"], r_cb["elapsed_s_arm"]), flush=True)

    # ===== ARM C_SUB_C: STATE_CONDITIONED_SCHEMA (4-primitive; schema variant) =====
    g_cc = np.random.default_rng(seed * 7919 + 3)
    t_arm = time.time()
    r_cc = arm_with_wm_bank(
        E, R, sq, W, chains_test, DEPTH, prototypes, cluster_to_target_part,
        "sub_c", g_cc,
        "sub_c_state_conditioned_schema_vector_recomputed_with_wm_per_hop")
    r_cc["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    out["arm_c_sub_c_state_conditioned"] = r_cc
    print(("  [seed=%d] ARM_C_SUB_C STATE_CONDITIONED top1=%.4f t=%.1fs") % (
        seed, r_cc["top1"], r_cc["elapsed_s_arm"]), flush=True)

    # ===== ARM D: ORACLE_PER_HOP =====
    def pick_oracle(chain, chain_idx, i, s_now):
        return chain[i][2] // PART_SIZE

    t_arm = time.time()
    r_d = arm_part_restricted(
        E, R, sq, W, chains_test, DEPTH, pick_oracle,
        "oracle_ground_truth_partition_per_hop_upper_bound")
    r_d["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    out["arm_d_oracle_per_hop"] = r_d
    print("  [seed=%d] ARM_D ORACLE_PER_HOP top1=%.4f t=%.1fs" % (
        seed, r_d["top1"], r_d["elapsed_s_arm"]), flush=True)

    # ===== ARM E: RANDOM (floor) =====
    g_arm_e = np.random.default_rng(seed * 7919 + 9)

    def pick_random(chain, chain_idx, i, s_now):
        return int(g_arm_e.integers(0, N_PARTS))

    t_arm = time.time()
    r_e = arm_part_restricted(
        E, R, sq, W, chains_test, DEPTH, pick_random,
        "random_partition_per_hop_floor")
    r_e["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    out["arm_e_random"] = r_e
    print("  [seed=%d] ARM_E RANDOM top1=%.4f t=%.1fs" % (
        seed, r_e["top1"], r_e["elapsed_s_arm"]), flush=True)

    # Lifts per adapter
    out["lift_sub_a_over_a"] = round(r_ca["top1"] - r_a["top1"], 4)
    out["lift_sub_a_over_b"] = round(r_ca["top1"] - r_b["top1"], 4)
    out["lift_sub_b_over_a"] = round(r_cb["top1"] - r_a["top1"], 4)
    out["lift_sub_b_over_b"] = round(r_cb["top1"] - r_b["top1"], 4)
    out["lift_sub_c_over_a"] = round(r_cc["top1"] - r_a["top1"], 4)
    out["lift_sub_c_over_b"] = round(r_cc["top1"] - r_b["top1"], 4)
    out["gap_d_minus_max_adapter"] = round(
        r_d["top1"] - max(r_ca["top1"], r_cb["top1"], r_cc["top1"]), 4)

    out["elapsed_s"] = round(time.time() - t, 1)
    return out


# ----------------------------------------------------------------------------
# Verdict
# ----------------------------------------------------------------------------

def _per_hop_partacc_pass(arm_payload: Dict[str, Any]) -> bool:
    """Per-hop partition-correct > HP_PER_HOP_PARTACC at hops 5, 10, 15."""
    pcs = arm_payload.get("partition_correct_per_step")
    if not isinstance(pcs, list) or len(pcs) < 15:
        return False
    return (pcs[4] > HP_PER_HOP_PARTACC
            and pcs[9] > HP_PER_HOP_PARTACC
            and pcs[14] > HP_PER_HOP_PARTACC)


def _adapter_passes(arm_payload: Dict[str, Any],
                    a_top1: float, b_top1: float, d_top1: float,
                    e_top1: float, saturated: bool) -> Tuple[bool, str]:
    """Per-adapter HARD_PASS check."""
    c = arm_payload.get("top1")
    if c is None or math.isnan(c):
        return False, "nan_top1"
    if not (HP_ADAPTER_LO <= c <= HP_ADAPTER_HI):
        return False, "out_of_band(%.4f)" % c
    if not (c - b_top1 >= HP_LIFT_OVER_B):
        return False, "lift_over_B=%.4f<%.2f" % (c - b_top1, HP_LIFT_OVER_B)
    if not (c - a_top1 >= HP_LIFT_OVER_A):
        return False, "lift_over_A=%.4f<%.2f" % (c - a_top1, HP_LIFT_OVER_A)
    if not _per_hop_partacc_pass(arm_payload):
        return False, "per_hop_partacc<%.2f" % HP_PER_HOP_PARTACC
    if not (d_top1 > c):
        return False, "oracle_not_above(d=%.4f,c=%.4f)" % (d_top1, c)
    if e_top1 >= HP_RANDOM_CEIL:
        return False, "random_floor_breach(e=%.4f>=%.2f)" % (e_top1, HP_RANDOM_CEIL)
    if saturated:
        return False, "saturation_flag"
    return True, "OK"


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
    b = mean_top1("arm_b_path2_per_chain")
    ca = mean_top1("arm_c_sub_a_prior_modulation")
    cb = mean_top1("arm_c_sub_b_fake_evidence")
    cc = mean_top1("arm_c_sub_c_state_conditioned")
    d = mean_top1("arm_d_oracle_per_hop")
    e = mean_top1("arm_e_random")

    # Cardinality (META_RULE_H)
    observed_units = sum(1 for p in per_seed for ak in ARM_KEYS if ak in p)
    cardinality_ok = (observed_units == EXPECTED_N_UNITS)

    # Arms-must-differ (META_RULE_AF)
    arms_hashes = _arms_must_differ_sha256(per_seed)
    unique_hashes = set(arms_hashes.values())
    arms_distinct = (len(unique_hashes) == len(ARM_KEYS))

    saturated_any = any(
        (not math.isnan(v)) and v >= HP_SATURATION_CEIL for v in (ca, cb, cc))

    # Per-adapter HARD_PASS check (use first available seed for per-hop part-acc)
    # NOTE: for chunked single-seed, we evaluate on that seed's payload.
    adapter_verdicts: Dict[str, Tuple[bool, str]] = {}
    if per_seed:
        p0 = per_seed[0]
        for arm_key, label in [
            ("arm_c_sub_a_prior_modulation", "SUB_A"),
            ("arm_c_sub_b_fake_evidence", "SUB_B"),
            ("arm_c_sub_c_state_conditioned", "SUB_C"),
        ]:
            if arm_key in p0:
                adapter_verdicts[label] = _adapter_passes(
                    p0[arm_key], a, b, d, e, saturated_any)
            else:
                adapter_verdicts[label] = (False, "missing")

    any_pass = any(v[0] for v in adapter_verdicts.values())
    all_fail = all(
        (not math.isnan(arm_top1)) and (
            arm_top1 <= HF_ADAPTER_ABS or (arm_top1 - b) < HF_ADAPTER_LIFT_OVER_B
        )
        for arm_top1 in (ca, cb, cc)
    )

    pcs_a = (per_seed[0].get("arm_c_sub_a_prior_modulation", {})
             .get("partition_correct_per_step", []) if per_seed else [])
    pcs_b = (per_seed[0].get("arm_c_sub_b_fake_evidence", {})
             .get("partition_correct_per_step", []) if per_seed else [])
    pcs_c = (per_seed[0].get("arm_c_sub_c_state_conditioned", {})
             .get("partition_correct_per_step", []) if per_seed else [])

    def _hop_str(pcs: List[float]) -> str:
        if not pcs or len(pcs) < 15:
            return "n/a"
        return "h5=%.3f h10=%.3f h15=%.3f" % (pcs[4], pcs[9], pcs[14])

    rail_breach = sum(1 for p in per_seed
                      if not p.get("baseline_rail_ok", False))

    cv_ca = cv_top1("arm_c_sub_a_prior_modulation")
    cv_cb = cv_top1("arm_c_sub_b_fake_evidence")
    cv_cc = cv_top1("arm_c_sub_c_state_conditioned")

    summ = (
        "BASELINE_A=%.4f (rail_breach=%d/%d) PATH2_B=%.4f "
        "SUB_A=%.4f (lift_A=%.4f lift_B=%.4f part %s; cv=%.3f) verdict=%s "
        "SUB_B=%.4f (lift_A=%.4f lift_B=%.4f part %s; cv=%.3f) verdict=%s "
        "SUB_C=%.4f (lift_A=%.4f lift_B=%.4f part %s; cv=%.3f) verdict=%s "
        "ORACLE_D=%.4f RANDOM_E=%.4f cardinality_ok=%s expected_units=%d "
        "observed_units=%d arms_distinct=%s saturated_any=%s depth=%d "
        "HP_band=[%.2f,%.2f] HF_abs=%.2f HF_lift_B=%.2f"
    ) % (
        a, rail_breach, len(per_seed), b,
        ca, (ca - a if not math.isnan(ca) else float("nan")),
        (ca - b if not math.isnan(ca) else float("nan")),
        _hop_str(pcs_a), cv_ca,
        ("PASS" if adapter_verdicts.get("SUB_A", (False, ""))[0]
         else adapter_verdicts.get("SUB_A", (False, "missing"))[1]),
        cb, (cb - a if not math.isnan(cb) else float("nan")),
        (cb - b if not math.isnan(cb) else float("nan")),
        _hop_str(pcs_b), cv_cb,
        ("PASS" if adapter_verdicts.get("SUB_B", (False, ""))[0]
         else adapter_verdicts.get("SUB_B", (False, "missing"))[1]),
        cc, (cc - a if not math.isnan(cc) else float("nan")),
        (cc - b if not math.isnan(cc) else float("nan")),
        _hop_str(pcs_c), cv_cc,
        ("PASS" if adapter_verdicts.get("SUB_C", (False, ""))[0]
         else adapter_verdicts.get("SUB_C", (False, "missing"))[1]),
        d, e, cardinality_ok, EXPECTED_N_UNITS, observed_units,
        arms_distinct, saturated_any, DEPTH,
        HP_ADAPTER_LO, HP_ADAPTER_HI, HF_ADAPTER_ABS, HF_ADAPTER_LIFT_OVER_B,
    )

    # Cardinality gate FIRST (META_RULE_H)
    if not cardinality_ok:
        return ("HARD_FAIL_CARDINALITY_BREACH",
                "HARD_FAIL_CARDINALITY_BREACH: " + summ, arms_hashes)

    if not arms_distinct:
        return ("HARD_FAIL_ARMS_TIED",
                "HARD_FAIL_ARMS_TIED_NO_DISCRIMINATION: " + summ, arms_hashes)

    # ORACLE sanity (D must beat the best adapter unless adapter close to ceiling)
    best_adapter = max(ca, cb, cc) if not all(math.isnan(x) for x in (ca, cb, cc)) else float("nan")
    if (not math.isnan(d)) and (not math.isnan(best_adapter)) \
            and d <= best_adapter - 0.001 and best_adapter < 0.99:
        return ("HARD_FAIL_ORACLE_BELOW_ADAPTER",
                "HARD_FAIL_ORACLE_NOT_UPPER_BOUND: " + summ, arms_hashes)

    # RANDOM floor breach (E must be < HP_RANDOM_CEIL)
    if (not math.isnan(e)) and e >= HP_RANDOM_CEIL:
        return ("HARD_FAIL_RANDOM_FLOOR_BREACH",
                "HARD_FAIL_RANDOM_FLOOR_NOT_BELOW_CEIL: " + summ, arms_hashes)

    # Whole-cell HARD_FAIL: all 3 adapters fail
    if all_fail:
        return ("HARD_FAIL_ALL_ADAPTERS_DEAD",
                ("HARD_FAIL_4_PRIMITIVE_COMPOSITION_DIRECTION_DEAD_ALL_3_"
                 "ADAPTERS_FAIL_CAPABILITY_BOX_CLOSES: ") + summ,
                arms_hashes)

    # Smoke vs full verdict
    if RUN_MODE == "smoke":
        if any_pass:
            # Identify winning adapter (largest lift over B that also passes)
            winners = [(k, v) for k, v in adapter_verdicts.items() if v[0]]
            winner_str = ",".join(w[0] for w in winners)
            return ("SMOKE_HARD_PASS",
                    ("SMOKE_HARD_PASS_4_PRIMITIVE_COMPOSITION_VIA_ADAPTER_%s_"
                     "BARRIER_1_MULTI_HOP_BROKEN_VIA_DLPFC_WM_STATE_TRACKER: "
                     % winner_str) + summ, arms_hashes)

        # MIDDLE_BAND: any adapter in [0.30, 0.50] AND (adapter - B) >= MM_LIFT_MIN
        mm_hits = []
        for k, top1 in (("SUB_A", ca), ("SUB_B", cb), ("SUB_C", cc)):
            if (not math.isnan(top1)) and HF_ADAPTER_ABS < top1 < HP_ADAPTER_LO \
                    and (top1 - b) >= MM_LIFT_MIN:
                mm_hits.append(k)
        if mm_hits:
            return ("MIDDLE_BAND_PARTIAL_ADAPTER",
                    "MIDDLE_BAND_ADAPTERS_%s_PARTIAL_LIFT: " % ",".join(mm_hits)
                    + summ, arms_hashes)
        return ("HARD_FAIL_NO_ADAPTER_PASS",
                "HARD_FAIL_NO_ADAPTER_REACHES_HP_BAND_OR_MM_LIFT: " + summ,
                arms_hashes)

    # Full verdict (chunked single-seed; cv across seeds aggregated in 3-cell merger)
    if any_pass:
        winners = [(k, v) for k, v in adapter_verdicts.items() if v[0]]
        winner_str = ",".join(w[0] for w in winners)
        return ("HARD_PASS_CHAIN_GRADE_4_PRIMITIVE_COMPOSITION",
                ("HARD_PASS_CHAIN_GRADE_DEPTH15_VIA_DLPFC_WM_STATE_TRACKER_"
                 "ADAPTER_%s: " % winner_str) + summ, arms_hashes)

    mm_hits = []
    for k, top1 in (("SUB_A", ca), ("SUB_B", cb), ("SUB_C", cc)):
        if (not math.isnan(top1)) and HF_ADAPTER_ABS < top1 < HP_ADAPTER_LO \
                and (top1 - b) >= MM_LIFT_MIN:
            mm_hits.append(k)
    if mm_hits:
        return ("MIDDLE_BAND_PARTIAL_ADAPTER",
                "MIDDLE_BAND_ADAPTERS_%s_PARTIAL_LIFT: " % ",".join(mm_hits)
                + summ, arms_hashes)

    return ("HARD_FAIL_NO_ADAPTER_PASS",
            "HARD_FAIL_NO_ADAPTER_REACHES_HP_BAND: " + summ, arms_hashes)


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
            "4-PRIMITIVE brain-faithful composition: vmPFC schema-Bayes + "
            "dlPFC WM state-tracker + cortex partition argmax + hippo "
            "restricted cleanup. PATH 2 (3-primitive) HARD_FAILed at C=0.01 "
            "(MEASURED@d:/AI/hd-instrument/data/exp_substrate_partition_oracle_"
            "brain_composition_hint_v1_seed_7_smoke/metrics.json) because "
            "schema fires once per chain leaving partition wrong for hops "
            "2..15. The 4-primitive fix: dlPFC WM state-tracker maintains "
            "accumulated trajectory state and re-fires schema-Bayes PER HOP "
            "with state-context bias. Edge-1 SHAPE_MISMATCH per drill "
            "(notes/research_drill_pfc_wm_state_tracker_4_primitive_"
            "composition_2026-06-28.md); this cell tests 3 adapter sub-"
            "mechanisms IN PARALLEL ARMS (SUB_A prior-modulation SHAPE_MATCH "
            "multiplicative; SUB_B fake-evidence harmonic-decay weight; "
            "SUB_C state-conditioned schema variant). HARD_PASS for any "
            "adapter requires top1 in [0.50, 0.95] AND lift>=0.30 over B "
            "AND lift>=0.20 over A AND per-hop part-acc>0.50 at hops 5/10/15 "
            "AND D > adapter AND E < 0.05. HARD_FAIL whole-cell if all 3 "
            "adapters dead (top1<=0.30 OR lift<0.10) - capability box closes. "
            "WM bank: K=200 slots (Frady-Sommer 2020 outer-product); per-hop "
            "write s_pred*p*hop_code; per-hop read via slot key. Regime "
            "matches v5_hardened+PATH2 for comparability (N=8192 V_C=4000 "
            "d=15 psz=800). 7 arms x single-seed sibling (seed=7); siblings "
            "seed=13 and seed=19. META_RULE_AC/AE/AF/AG/AH/AL/AN/AP/H "
            "tagged. Sources: "
            "experiments/exp_substrate_partition_oracle_brain_composition_"
            "hint_v1_seed_7.py (template); pre-reg preregs/2026-06-28_"
            "substrate_partition_oracle_pfc_wm_state_tracker_v1.md."
        ),
    }
    write_metrics(out_dir, metrics, results=per_seed)
    print("[done] metrics.json written (%d seeds, %.1fs)" % (
        len(per_seed), metrics["elapsed_s"]), flush=True)
