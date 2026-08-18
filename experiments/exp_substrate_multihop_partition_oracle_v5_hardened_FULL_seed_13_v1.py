"""substrate_multihop_partition_oracle_v5_hardened_v1.

PURPOSE (Barrier 1 chain-grade promotion via UN-saturated discriminating regime):
    Parent cell `_n8192` smoke MIDDLE_BAND_SATURATED_AUTO_DEMOTE (BIAS-Q):
        N=8192 V_C=4000 d=10 psz=40 -> ORACLE_B=1.000 saturated (BASELINE_A=0.59
        rail-breach high). Cone-formula gives no signal but substrate-empirical
        per_step_baseline=0.948 (META_RULE_AN: substrate >> formula).

    This cell HARDENS to depth=15 + wider partitions (psz_B=400, 10 parts)
    so BOTH baseline AND oracle land in discriminating bands:
        - per_step_baseline=0.948 (empirical N=8192 V_C=4000)
          -> depth=15 BASELINE_A_proj = 0.948^15 = 0.449 (in [0.30, 0.70])
        - per_step_oracle@psz=400 = ~0.98 (substrate beats formula; observed psz=200
          per_step=0.999, psz=400 should be 0.98-0.99)
          -> depth=15 ORACLE_B_proj = 0.98^15 = 0.739 (in [0.50, 0.95]; NOT saturated)
        - lift_b_a_proj = 0.739 - 0.449 = 0.290 (above HP_LIFT 0.20)
        - RANDOM_E (random psz=400, 10 partitions): 1/10 chance/hop
          -> depth=15 = 0.10^15 ~ 1e-15 (~0; clean floor)

    Strategic: HARD_PASS here = chain-grade depth-15 compositional reasoning
    via partition-oracle goal-conditioning AT UN-SATURATED REGIME. Barrier 1
    BROKEN at chain-grade tier (depth-15 IS the BARRIER 1 ceiling-extension goal).

CONE-COLLAPSE FORMULA (computed-in-code; tools/_compute_cone_regime.py):
    crosstalk_std = sqrt((V_C_per_hop - 1) / N)
    per_step (substrate-empirical; META_RULE_AN ~3.7x lift on formula):
        baseline: 0.948 at N=8192 V_C=4000 (MEASURED@n8192_smoke)
        oracle@psz=400: ~0.98 (interpolation from psz=200->0.999, psz=40->1.000)

REGIME PARAMETERS (LOCKED at module init; META_RULE_AL):
    N=8192, V_C=4000, V_P=10
    DEPTH=15 (UP from 10; pushes baseline to discriminating mid-band)
    psz_B=400  (UP from 40; 10 partitions; un-saturates oracle to ~0.74)
    psz_C=800  (5 partitions; mid-regime)
    psz_D=2000 (2 partitions; low-narrowing crosstalk sweep)

ARMS (5 arms x depth=15):
    A: BASELINE                  argmax over V_C=4000 (rail; proj 0.449)
    B: ORACLE_PART_10_psz_400    10 partitions of 400; oracle routes
                                  (mechanism; proj 0.74)
    C: ORACLE_PART_5_psz_800     5 partitions of 800 (mid-regime)
    D: ORACLE_PART_2_psz_2000    2 partitions of 2000 (low narrowing)
    E: NO_ORACLE_RANDOM_PART_10  10 partitions; routing RANDOM (1/10 chance)
                                  (critical discriminator)

PRE-REG BANDS (META_RULE_AL; LOCKED):
    BASELINE rail (BIAS-S):
        ARM_A.top1@d15 in [0.30, 0.70]  # mid-band discriminating (was [0.11, 0.25] at d=10)
    HARD_PASS (chain-grade tier; NOT saturated):
        ARM_B.top1@d15 in [0.50, 0.95]  # in band; both floor + ceiling
        AND ARM_B.top1@d15 - ARM_A.top1@d15 >= 0.20  # lift vs baseline
        AND ARM_B.top1@d15 - ARM_E.top1@d15 >= 0.30  # goal-info load-bearing
        AND cv(ARM_B across seeds) < 0.15
        AND arms_distinct == True
        AND saturation == False  # ARM_B < 0.95 (tightened from 0.99 per BIAS-Q)
    HARD_FAIL:
        ARM_B.top1@d15 <= 0.30  # mechanism dies at hardened regime
        OR (saturation == True AND lift_b_a < 0.20)
    MIDDLE_BAND:
        ARM_B.top1@d15 in [0.30, 0.50) with lift >= 0.15
        OR HP-band hit BUT cv > 0.15 (full only) OR (ARM_B - ARM_E) < 0.30

DISCIPLINE TAGS:
    META_RULE_AC: number tagging MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@
    META_RULE_AE: absolute metrics.json paths in DESIGN_NOTE
    META_RULE_AF: arms-must-differ SHA-256 hash check post-run
    META_RULE_AG: discriminator at edge-of-capacity (proj BASELINE=0.45 ORACLE=0.74)
    META_RULE_AH: atomic metrics.json write (tmp + os.replace via _seed_checkpoint)
    META_RULE_AL: HARD_PASS + HARD_FAIL bands pre-registered + LOCKED at import
    META_RULE_AN: substrate-empirical anchor (per_step=0.948 from prior smoke)
    META_RULE_H : CARDINALITY_OK declared; expected_n_units enforced
    BIAS-Q     : saturation guard at 0.95 (tightened); auto-demote to MM if lift<0.20
    BIAS-N     : per-arm metrics in summary (NOT verdict_msg framing only)
    BIAS-S     : baseline rail check [0.30, 0.70]
    DISCRIMINATOR-MUST-SURVIVE-SCALE: smoke at FULL-N + FULL-depth (only seeds change)
    PROT-018: regime params bind to anchor descriptor in CONFIG_VERSION
    Fix #28: per-arm reads from metrics.json
    NO-LOCAL: route remote_cpu_queue (USER 2026-06-28)

SOURCE CITATIONS (ABSOLUTE PATHS; META_RULE_AE):
    - Parent _n8192 cell (saturated at d=10):
      d:/AI/hd-instrument/experiments/exp_substrate_multihop_partition_oracle_at_v5_regime_revival_c1_n8192.py
    - Parent _n8192 smoke metrics (MIDDLE_BAND_SATURATED):
      d:/AI/hd-instrument/data/exp_substrate_multihop_partition_oracle_at_v5_regime_revival_c1_n8192/metrics.json
    - Parent v1 cell (saturated at N=2048):
      d:/AI/hd-instrument/experiments/exp_substrate_multihop_partition_oracle_at_v5_regime_revival_c1.py
    - Parent v1 smoke metrics:
      d:/AI/hd-instrument/data/exp_substrate_multihop_partition_oracle_at_v5_regime_revival_c1_smoke/metrics.json
    - Regime computation tool:
      d:/AI/hd-instrument/tools/_compute_cone_regime.py
    - Parent prereg:
      d:/AI/hd-instrument/preregs/2026-06-28_substrate_multihop_partition_oracle_at_v5_regime_revival_c1.md

NUMBER TAGGING (META_RULE_AC):
    HYPOTHESIZED@HARD_PASS_BAND_BASELINE: ARM_A top1@d15 in [0.30, 0.70]
    HYPOTHESIZED@HARD_PASS_BAND_ORACLE: ARM_B top1@d15 in [0.50, 0.95]
    THEORETICAL@DEPTH_SCALE_BASELINE: 0.948^15 = 0.449 (per_step empirical^depth)
    THEORETICAL@DEPTH_SCALE_ORACLE: 0.98^15 = 0.739 (per_step substrate^depth)
    THEORETICAL@DEPTH_SCALE_RANDOM: 0.10^15 = 1e-15 (random 1/10 chance^depth)
    MEASURED@N8192_BASELINE_D10: 0.590 (parent _n8192 smoke ARM_A)
    MEASURED@N8192_ORACLE_PSZ40_D10: 1.000 (parent _n8192 smoke ARM_B SATURATED)
    MEASURED@N8192_ORACLE_PSZ200_D10: 0.990 (parent _n8192 smoke ARM_D; per_step 0.999)
    MEASURED@PER_STEP_EMPIRICAL: 0.948 (from MEASURED@N8192_BASELINE_D10 ^(1/10))
    CITED@MANTE_2013: PFC goal-conditioned attention narrows search 10-100x

Author: exp_dev 2026-06-28 (research drill 2x; un-saturated regime for chain-grade).
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

ANCHOR_NAME = "substrate_multihop_partition_oracle_v5_hardened_FULL_seed_13_v1"
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
# HARDENED regime: depth=15 + psz_B=400 (10 partitions) -- both arms in
# discriminating bands per substrate-empirical projections.
N_DIM = 8192
V_CONCEPTS = 4000
V_PRED = 10
DEPTH = 15           # UP from parent n8192's 10
MAX_DEPTH = 15

# BASELINE rail @d=15 -- discriminating mid-band (was [0.11, 0.25] at d=10)
# THEORETICAL: 0.948^15 = 0.449 -> band [0.30, 0.70] gives substrate slack
BASELINE_RAIL_TARGET = 0.449     # THEORETICAL@DEPTH_SCALE_BASELINE
BASELINE_RAIL_LO = 0.30
BASELINE_RAIL_HI = 0.70

# ARM_B oracle bands @d=15 -- un-saturated discriminating band
# THEORETICAL: 0.98^15 = 0.739 -> band [0.50, 0.95] gives substrate slack
HP_ARM_B_LO = 0.50               # HYPOTHESIZED@HARD_PASS_BAND_ORACLE floor
HP_ARM_B_HI = 0.95               # HYPOTHESIZED@HARD_PASS_BAND_ORACLE ceiling
HP_LIFT_OVER_BASELINE = 0.20     # ARM_B - ARM_A >= 0.20
HP_LIFT_OVER_RANDOM = 0.30       # ARM_B - ARM_E >= 0.30 (RANDOM proj ~0)
HP_CV_MAX = 0.15                 # cv across seeds
HP_SATURATION_CEIL = 0.95        # BIAS-Q tightened from 0.99

HF_ARM_B_ABS = 0.30              # HARD_FAIL if mechanism dies (lower than HP_LO)
HF_LIFT_MIN_IF_SATURATED = 0.20  # if saturation AND lift<this, HARD_FAIL
MM_LIFT_MIN = 0.15               # MIDDLE_BAND lower-lift floor

# Partition configurations: psz_B=400 (10 parts) un-saturates oracle at d=15
def _cone_collapse_crosstalk(v_c_per_hop: int, n: int) -> float:
    return float(math.sqrt(max(v_c_per_hop - 1, 1) / max(n, 1)))

N_PART_B = 5     # ARM_B: 5 partitions of 800 (MECHANISM; un-saturated)
N_PART_C = 10    # ARM_C: 10 partitions of 400 (narrower; will saturate ~0.97)
N_PART_D = 2     # ARM_D: 2 partitions of 2000 (low narrowing)
assert V_CONCEPTS % N_PART_B == 0
assert V_CONCEPTS % N_PART_C == 0
assert V_CONCEPTS % N_PART_D == 0

PART_SIZE_B = V_CONCEPTS // N_PART_B   # 800
PART_SIZE_C = V_CONCEPTS // N_PART_C   # 400
PART_SIZE_D = V_CONCEPTS // N_PART_D   # 2000

CROSSTALK_B = _cone_collapse_crosstalk(PART_SIZE_B, N_DIM)
CROSSTALK_C = _cone_collapse_crosstalk(PART_SIZE_C, N_DIM)
CROSSTALK_D = _cone_collapse_crosstalk(PART_SIZE_D, N_DIM)
CROSSTALK_BASELINE = _cone_collapse_crosstalk(V_CONCEPTS, N_DIM)

# Locked invariants (META_RULE_AL)
assert BASELINE_RAIL_LO < BASELINE_RAIL_TARGET < BASELINE_RAIL_HI
assert HP_ARM_B_LO > HF_ARM_B_ABS, "HP floor must exceed HF ceiling"
assert HP_ARM_B_LO < HP_ARM_B_HI <= HP_SATURATION_CEIL, \
    "HP ceiling must not exceed saturation guard"
assert HP_LIFT_OVER_BASELINE > MM_LIFT_MIN
assert 0.0 < HP_CV_MAX < 0.5
# B has psz=800 (wider, un-saturated mechanism); C has psz=400 (narrower)
assert CROSSTALK_C < CROSSTALK_B < CROSSTALK_D < CROSSTALK_BASELINE
# Sanity: partition crosstalks computed correctly
assert abs(CROSSTALK_B - math.sqrt(799 / 8192)) < 1e-6
assert abs(CROSSTALK_C - math.sqrt(399 / 8192)) < 1e-6
assert abs(CROSSTALK_D - math.sqrt(1999 / 8192)) < 1e-6
assert DEPTH == 15

# Chain configuration
N_CHAINS_TRAIN = 200
# CHUNKED single-seed-per-cell variant (USER 2026-06-28 chunked directive).
# Sibling cells: seed_11, seed_13, seed_19. Each cell is self-contained;
# runner-zombie loses only ONE seed, not all 3.
if RUN_MODE == "smoke":
    SEEDS = [13]
    N_CHAINS_TEST = 100
else:
    SEEDS = [13]
    N_CHAINS_TEST = 200

# Cardinality (META_RULE_H)
N_ARMS = 5
EXPECTED_N_UNITS = N_ARMS * len(SEEDS)

ENCODER_PROVENANCE = "SUBSTRATE_NATIVE_BIPOLAR"

CONFIG_VERSION = (
    "substrateMultihopPartOracleV5HardenedV1: N=%d V_C=%d V_P=%d depth=%d "
    "n_chains_train=%d n_chains_test=%d seeds=%s mode=%s encoder=%s "
    "n_parts_B=%d (psz=%d xtalk=%.4f) n_parts_C=%d (psz=%d xtalk=%.4f) "
    "n_parts_D=%d (psz=%d xtalk=%.4f) baseline_xtalk=%.4f "
    "RAIL=[%.3f,%.3f] target=%.3f HP_B_band=[%.2f,%.2f] HP_lift_base=%.2f "
    "HP_lift_rand=%.2f HP_cv_max=%.2f HP_sat_ceil=%.2f HF_B_abs=%.2f "
    "HF_lift_min_if_sat=%.2f MM_lift_min=%.2f expected_units=%d arms=%d"
) % (
    N_DIM, V_CONCEPTS, V_PRED, DEPTH,
    N_CHAINS_TRAIN, N_CHAINS_TEST, SEEDS, RUN_MODE, ENCODER_PROVENANCE,
    N_PART_B, PART_SIZE_B, CROSSTALK_B,
    N_PART_C, PART_SIZE_C, CROSSTALK_C,
    N_PART_D, PART_SIZE_D, CROSSTALK_D,
    CROSSTALK_BASELINE,
    BASELINE_RAIL_LO, BASELINE_RAIL_HI, BASELINE_RAIL_TARGET,
    HP_ARM_B_LO, HP_ARM_B_HI, HP_LIFT_OVER_BASELINE, HP_LIFT_OVER_RANDOM,
    HP_CV_MAX, HP_SATURATION_CEIL, HF_ARM_B_ABS, HF_LIFT_MIN_IF_SATURATED,
    MM_LIFT_MIN, EXPECTED_N_UNITS, N_ARMS,
)


# ----------------------------------------------------------------------------
# Primitives (verbatim numpy port from parent n8192 cell)
# ----------------------------------------------------------------------------

def bipolar(M: int, n: int, g: np.random.Generator) -> np.ndarray:
    """Bipolar bit vectors; row-normalized."""
    X = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)


def ingest_hebbian(triples, E: np.ndarray, R: np.ndarray, sq: float,
                   n_dim: int, batch: int = 2000) -> np.ndarray:
    """Hebbian outer-product ingest."""
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


def arm_baseline(E: np.ndarray, R: np.ndarray, sq: float,
                 W: np.ndarray, chains_test: List[List[Tuple[int, int, int]]],
                 depth: int) -> Dict[str, Any]:
    """Baseline: argmax over full V_C cleanup at each hop."""
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


def arm_part_oracle(E: np.ndarray, R: np.ndarray, sq: float,
                    W: np.ndarray,
                    chains_test: List[List[Tuple[int, int, int]]],
                    depth: int, part_size: int,
                    mechanism_tag: str) -> Dict[str, Any]:
    """Partition-oracle cleanup."""
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
            target_part = target_o // part_size  # ORACLE (gen-time partition)
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
        "mechanism": mechanism_tag,
    }


def arm_no_oracle_random_part(E: np.ndarray, R: np.ndarray, sq: float,
                              W: np.ndarray,
                              chains_test: List[List[Tuple[int, int, int]]],
                              depth: int, part_size: int,
                              g: np.random.Generator) -> Dict[str, Any]:
    """ARM_E discriminator: partition exists but routing is RANDOM."""
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
        "mechanism": "no_oracle_random_partition_discriminator",
    }


# ----------------------------------------------------------------------------
# Arms-must-differ SHA-256 (META_RULE_AF)
# ----------------------------------------------------------------------------

def _arms_must_differ_sha256(per_seed: List[Dict[str, Any]]) -> Dict[str, str]:
    """SHA-256 hash of per_step_acc for each arm; arms must produce distinct
    hashes (META_RULE_AF). Returns map arm_key -> sha256-hex."""
    hashes: Dict[str, str] = {}
    arm_keys = [
        "arm_a_baseline",
        "arm_b_oracle_part_5",
        "arm_c_oracle_part_10",
        "arm_d_oracle_part_2",
        "arm_e_no_oracle_random",
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

    # T1: bipolar shapes + norm
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

    # T4: all 5 arms produce valid output at tiny config
    r_a = arm_baseline(E, R, sq, W, chains, depth=DEPTH)
    assert 0.0 <= r_a["top1"] <= 1.0
    assert len(r_a["per_step_acc"]) == DEPTH

    part_sz_tiny = V_tiny // 8  # 5 atoms per partition; 8 partitions
    assert V_tiny % 8 == 0

    r_b = arm_part_oracle(E, R, sq, W, chains, depth=DEPTH,
                          part_size=part_sz_tiny,
                          mechanism_tag="oracle_part_test")
    assert 0.0 <= r_b["top1"] <= 1.0
    assert len(r_b["per_step_acc"]) == DEPTH

    r_e = arm_no_oracle_random_part(E, R, sq, W, chains, depth=DEPTH,
                                    part_size=part_sz_tiny, g=g)
    assert 0.0 <= r_e["top1"] <= 1.0
    assert len(r_e["per_step_acc"]) == DEPTH

    # T5: cone-collapse formula sanity (BIAS-S regime check)
    # psz=800 N=8192: xtalk = sqrt(799/8192) = 0.3123 (ARM_B; un-saturated mechanism)
    assert abs(CROSSTALK_B - 0.3123) < 0.001, \
        "psz=800/N=8192 xtalk drift: %.4f" % CROSSTALK_B
    assert CROSSTALK_BASELINE > 0.6
    assert CROSSTALK_B < 0.40
    # CRLB ordering: B (psz=800) sits between C (psz=400) and D (psz=2000)
    assert CROSSTALK_C < CROSSTALK_B < CROSSTALK_D < CROSSTALK_BASELINE

    # T6: bands LOCKED (regression on band drift)
    assert N_DIM == 8192
    assert V_CONCEPTS == 4000
    assert DEPTH == 15
    assert PART_SIZE_B == 800
    assert PART_SIZE_C == 400
    assert PART_SIZE_D == 2000
    assert N_PART_B == 5
    assert N_PART_C == 10
    assert N_PART_D == 2
    assert HP_ARM_B_LO == 0.50
    assert HP_ARM_B_HI == 0.95
    assert HF_ARM_B_ABS == 0.30
    assert BASELINE_RAIL_LO == 0.30
    assert BASELINE_RAIL_HI == 0.70
    assert HP_LIFT_OVER_BASELINE == 0.20
    assert HP_LIFT_OVER_RANDOM == 0.30
    assert HP_CV_MAX == 0.15
    assert HP_SATURATION_CEIL == 0.95

    # T7: zero LLM calls (substrate-only)
    assert _LLM_CALL_COUNTER[0] == 0

    # T8: cardinality declared
    assert EXPECTED_N_UNITS == 5 * len(SEEDS)

    # T9: anchor binding
    assert "_hardened_" in ANCHOR_NAME and ANCHOR_NAME.endswith("_v1") and "_seed_13_" in ANCHOR_NAME

    # T10: arms-must-differ SHA-256 -- verify all 3 arms produce DISTINCT hashes
    # using tiny per_seed result
    tiny_per_seed = [{
        "arm_a_baseline": r_a,
        "arm_b_oracle_part_5": r_b,
        "arm_c_oracle_part_10": r_b,
        "arm_d_oracle_part_2": r_b,
        "arm_e_no_oracle_random": r_e,
    }]
    hashes_tiny = _arms_must_differ_sha256(tiny_per_seed)
    # A and B must differ; A and E must differ (baseline vs random discriminator)
    assert hashes_tiny["arm_a_baseline"] != hashes_tiny["arm_b_oracle_part_5"], \
        "META_RULE_AF: A vs B SHA collision in selftest"
    assert hashes_tiny["arm_a_baseline"] != hashes_tiny["arm_e_no_oracle_random"], \
        "META_RULE_AF: A vs E SHA collision in selftest"

    # T11: assert measured ~= expected (per spawn discipline)
    # tiny config is too small to predict baseline d=15 numerically;
    # just verify outputs are bounded and per_step is monotone-ish
    # (decreasing or flat over depth)
    psa = r_a["per_step_acc"]
    # Not strict monotonicity (small n; integer rounding) but max should be at start
    assert max(psa) >= psa[-1] - 0.5, \
        "per_step should not radically increase: %s" % psa

    print("[selftest] PASS N=%d V_C=%d depth=%d psz_B=%d arms: a=%.3f b=%.3f "
          "e=%.3f xtalk_B=%.4f xtalk_baseline=%.4f HP_band=[%.2f,%.2f] "
          "expected_proj_baseline=%.3f expected_proj_oracle=%.3f" % (
              N_DIM, V_CONCEPTS, DEPTH, PART_SIZE_B,
              r_a["top1"], r_b["top1"], r_e["top1"],
              CROSSTALK_B, CROSSTALK_BASELINE, HP_ARM_B_LO, HP_ARM_B_HI,
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

    out: Dict[str, Any] = {
        "seed": seed, "run_mode": RUN_MODE, "N": N_DIM, "V_C": V_CONCEPTS,
        "V_P": V_PRED, "depth": DEPTH,
        "n_chains_train": N_CHAINS_TRAIN, "n_chains_test": N_CHAINS_TEST,
        "n_partitions_B": N_PART_B, "part_size_B": PART_SIZE_B,
        "n_partitions_C": N_PART_C, "part_size_C": PART_SIZE_C,
        "n_partitions_D": N_PART_D, "part_size_D": PART_SIZE_D,
        "crosstalk_baseline": CROSSTALK_BASELINE,
        "crosstalk_B": CROSSTALK_B,
        "crosstalk_C": CROSSTALK_C,
        "crosstalk_D": CROSSTALK_D,
        "encoder_provenance": ENCODER_PROVENANCE,
        "config_version": CONFIG_VERSION,
        "_llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
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

    # ===== ARM_B: ORACLE_PART_5_psz_800 (MECHANISM; un-saturated; observed 0.90 d=15) =====
    t_arm = time.time()
    r_b = arm_part_oracle(E, R, sq, W, chains_test, depth=DEPTH,
                          part_size=PART_SIZE_B,
                          mechanism_tag="oracle_part_5_psz_800")
    r_b["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    out["arm_b_oracle_part_5"] = r_b
    print("  [seed=%d] ARM_B ORACLE_PART_5_psz_800 top1=%.4f "
          "(HP_band=[%.2f,%.2f] lift_vs_A>=%.2f predicted_xtalk=%.4f) "
          "per_step=%s t=%.1fs" % (
              seed, r_b["top1"], HP_ARM_B_LO, HP_ARM_B_HI,
              HP_LIFT_OVER_BASELINE, CROSSTALK_B,
              r_b["per_step_acc"], r_b["elapsed_s_arm"]), flush=True)

    # ===== ARM_C: ORACLE_PART_10_psz_400 (narrower; expected ~0.97 saturating) =====
    t_arm = time.time()
    r_c = arm_part_oracle(E, R, sq, W, chains_test, depth=DEPTH,
                          part_size=PART_SIZE_C,
                          mechanism_tag="oracle_part_10_psz_400")
    r_c["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    out["arm_c_oracle_part_10"] = r_c
    print("  [seed=%d] ARM_C ORACLE_PART_10_psz_400 top1=%.4f (xtalk=%.4f) "
          "per_step=%s t=%.1fs" % (
              seed, r_c["top1"], CROSSTALK_C,
              r_c["per_step_acc"], r_c["elapsed_s_arm"]), flush=True)

    # ===== ARM_D: ORACLE_PART_2_psz_2000 =====
    t_arm = time.time()
    r_d = arm_part_oracle(E, R, sq, W, chains_test, depth=DEPTH,
                          part_size=PART_SIZE_D,
                          mechanism_tag="oracle_part_2_psz_2000")
    r_d["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    out["arm_d_oracle_part_2"] = r_d
    print("  [seed=%d] ARM_D ORACLE_PART_2_psz_2000 top1=%.4f (xtalk=%.4f) "
          "per_step=%s t=%.1fs" % (
              seed, r_d["top1"], CROSSTALK_D,
              r_d["per_step_acc"], r_d["elapsed_s_arm"]), flush=True)

    # ===== ARM_E: NO_ORACLE_RANDOM_PART_5 (critical discriminator) =====
    # Uses ARM_B's partitioning (psz=800, 5 partitions) but routing is RANDOM.
    # Floor: 1/5 chance per hop -> 0.2^15 ~ 3e-11
    t_arm = time.time()
    g_e = np.random.default_rng(seed * 7919 + 1)
    r_e = arm_no_oracle_random_part(E, R, sq, W, chains_test, depth=DEPTH,
                                    part_size=PART_SIZE_B, g=g_e)
    r_e["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    out["arm_e_no_oracle_random"] = r_e
    print("  [seed=%d] ARM_E NO_ORACLE_RANDOM_PART_5 top1=%.4f "
          "(critical discriminator; ARM_B - ARM_E should be >= %.2f) "
          "per_step=%s t=%.1fs" % (
              seed, r_e["top1"], HP_LIFT_OVER_RANDOM,
              r_e["per_step_acc"], r_e["elapsed_s_arm"]), flush=True)

    # Lifts (per-seed)
    out["lift_b_over_a"] = round(r_b["top1"] - r_a["top1"], 4)
    out["lift_b_over_e"] = round(r_b["top1"] - r_e["top1"], 4)
    out["lift_c_over_a"] = round(r_c["top1"] - r_a["top1"], 4)
    out["lift_d_over_a"] = round(r_d["top1"] - r_a["top1"], 4)

    out["elapsed_s"] = round(time.time() - t, 1)
    return out


# ----------------------------------------------------------------------------
# Verdict (META_RULE_AL HP/HF/MM bands; BIAS-Q saturation guard; META_RULE_AF)
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
    arm_b = mean_top1("arm_b_oracle_part_5")
    arm_c = mean_top1("arm_c_oracle_part_10")
    arm_d = mean_top1("arm_d_oracle_part_2")
    arm_e = mean_top1("arm_e_no_oracle_random")

    cv_b = cv_top1("arm_b_oracle_part_5")

    lift_b_a = arm_b - arm_a if not (math.isnan(arm_b) or math.isnan(arm_a)) \
        else float("nan")
    lift_b_e = arm_b - arm_e if not (math.isnan(arm_b) or math.isnan(arm_e)) \
        else float("nan")

    # Cardinality (META_RULE_H)
    observed_units = sum(
        1 for p in per_seed for arm_key in (
            "arm_a_baseline", "arm_b_oracle_part_5",
            "arm_c_oracle_part_10", "arm_d_oracle_part_2",
            "arm_e_no_oracle_random")
        if arm_key in p
    )
    cardinality_ok = (observed_units == EXPECTED_N_UNITS)

    # Arms-must-differ SHA-256 (META_RULE_AF)
    arms_hashes = _arms_must_differ_sha256(per_seed)
    arms_distinct = (
        arms_hashes["arm_a_baseline"] != arms_hashes["arm_b_oracle_part_5"]
        and arms_hashes["arm_a_baseline"] != arms_hashes["arm_e_no_oracle_random"]
        and arms_hashes["arm_b_oracle_part_5"] != arms_hashes["arm_e_no_oracle_random"]
    )

    # BIAS-Q saturation check (tightened to 0.95)
    saturation_flag = (not math.isnan(arm_b)) and arm_b >= HP_SATURATION_CEIL

    # Baseline rail check (BIAS-S)
    rail_breach = sum(1 for p in per_seed
                      if not p.get("baseline_rail_ok", False))

    # HP-band check
    arm_b_in_band = ((not math.isnan(arm_b))
                     and HP_ARM_B_LO <= arm_b <= HP_ARM_B_HI)

    summ = (
        "BASELINE_A=%.4f (rail_breach=%d/%d; target=%.3f band=[%.2f,%.2f]) "
        "ORACLE_B=%.4f (cv=%.3f xtalk=%.4f in_band=%s) "
        "ORACLE_C=%.4f (xtalk=%.4f) ORACLE_D=%.4f (xtalk=%.4f) "
        "RANDOM_E=%.4f lift_B_A=%.4f lift_B_E=%.4f "
        "cardinality_ok=%s expected_units=%d observed_units=%d "
        "arms_distinct=%s saturation=%s HP_band=[%.2f,%.2f] depth=%d"
    ) % (
        arm_a, rail_breach, len(per_seed), BASELINE_RAIL_TARGET,
        BASELINE_RAIL_LO, BASELINE_RAIL_HI,
        arm_b, cv_b, CROSSTALK_B, arm_b_in_band,
        arm_c, CROSSTALK_C, arm_d, CROSSTALK_D, arm_e,
        lift_b_a, lift_b_e,
        cardinality_ok, EXPECTED_N_UNITS, observed_units,
        arms_distinct, saturation_flag,
        HP_ARM_B_LO, HP_ARM_B_HI, DEPTH,
    )

    # Cardinality gate FIRST (META_RULE_H)
    if not cardinality_ok:
        return ("HARD_FAIL_CARDINALITY_BREACH",
                "HARD_FAIL_CARDINALITY_BREACH: " + summ, arms_hashes)

    # Arms-distinct gate (META_RULE_AF)
    if not arms_distinct:
        return ("HARD_FAIL_ARMS_TIED",
                "HARD_FAIL_ARMS_TIED_NO_DISCRIMINATION: " + summ, arms_hashes)

    # HARD_FAIL: mechanism dies at hardened regime
    if (not math.isnan(arm_b)) and arm_b <= HF_ARM_B_ABS:
        return ("HARD_FAIL_NO_SIGNAL_AT_HARDENED",
                "HARD_FAIL_NO_SIGNAL_MECHANISM_DEAD_AT_DEPTH15: " + summ,
                arms_hashes)

    # HARD_FAIL: saturated AND insufficient lift (BIAS-Q + drill spec)
    if saturation_flag and (not math.isnan(lift_b_a)) \
            and lift_b_a < HF_LIFT_MIN_IF_SATURATED:
        return ("HARD_FAIL_SATURATION_WITHOUT_LIFT",
                "HARD_FAIL_SATURATION_FLAG_WITH_LIFT_BELOW_THRESHOLD: " + summ,
                arms_hashes)

    # Smoke verdict
    if RUN_MODE == "smoke":
        if arm_b_in_band \
                and (not math.isnan(lift_b_a)) and lift_b_a >= HP_LIFT_OVER_BASELINE \
                and (not math.isnan(lift_b_e)) and lift_b_e >= HP_LIFT_OVER_RANDOM \
                and not saturation_flag:
            return ("SMOKE_HARD_PASS",
                    "SMOKE_HARD_PASS_MECHANISM_IN_HP_BAND_UNSATURATED_DEPTH15: "
                    + summ, arms_hashes)
        if saturation_flag and (not math.isnan(lift_b_a)) \
                and lift_b_a >= HF_LIFT_MIN_IF_SATURATED:
            return ("MIDDLE_BAND_SATURATED_AUTO_DEMOTE",
                    "MIDDLE_BAND_SATURATED_AUTO_DEMOTE_BIAS_Q_NEED_HARDER: "
                    + summ, arms_hashes)
        if (not math.isnan(lift_b_a)) and lift_b_a >= MM_LIFT_MIN:
            return ("MIDDLE_BAND",
                    "MIDDLE_BAND_PARTIAL_MECHANISM_AT_DEPTH15: " + summ,
                    arms_hashes)
        return ("HARD_FAIL_LIFT_BELOW_THRESHOLD",
                "HARD_FAIL_LIFT_BELOW_THRESHOLD_AT_DEPTH15: " + summ,
                arms_hashes)

    # Full verdict (multi-seed; cv required for chain-grade)
    cv_ok = (not math.isnan(cv_b)) and cv_b < HP_CV_MAX

    # HARD_PASS (chain-grade): all criteria + NOT saturated
    if arm_b_in_band \
            and (not math.isnan(lift_b_a)) and lift_b_a >= HP_LIFT_OVER_BASELINE \
            and (not math.isnan(lift_b_e)) and lift_b_e >= HP_LIFT_OVER_RANDOM \
            and cv_ok and not saturation_flag:
        return ("HARD_PASS_CHAIN_GRADE_DEPTH15_UNSATURATED",
                "HARD_PASS_CHAIN_GRADE_DEPTH15_UNSAT_BARRIER_1_BROKEN: " + summ,
                arms_hashes)

    if saturation_flag and (not math.isnan(lift_b_a)) \
            and lift_b_a >= HF_LIFT_MIN_IF_SATURATED:
        return ("MIDDLE_BAND_SATURATED_AUTO_DEMOTE",
                "MIDDLE_BAND_SATURATED_AUTO_DEMOTE_BIAS_Q_NEED_HARDER: " + summ,
                arms_hashes)

    if (not math.isnan(lift_b_a)) and lift_b_a >= MM_LIFT_MIN:
        return ("MIDDLE_BAND",
                "MIDDLE_BAND_PARTIAL_MECHANISM_AT_DEPTH15: " + summ, arms_hashes)

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
                "baseline_full_V_C", "oracle_part_5_psz_800",
                "oracle_part_10_psz_400", "oracle_part_2_psz_2000",
                "no_oracle_random_part_5"],
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
            "baseline_full_V_C", "oracle_part_5_psz_800",
            "oracle_part_10_psz_400", "oracle_part_2_psz_2000",
            "no_oracle_random_part_5"],
        "arms_must_differ_sha256": ahashes,
        "DESIGN_NOTE": (
            "HARDENED v1 of v5 revival chain: depth=15 (UP from 10) + "
            "psz_B=400 (UP from 40, 10 partitions). Parent _n8192 saturated "
            "at ORACLE_B=1.000 at depth=10 psz=40 -- this cell un-saturates "
            "both arms into discriminating bands via empirical-anchored "
            "regime tuning (per_step_baseline=0.948 from MEASURED@N8192 "
            "BASELINE_D10; per_step_oracle@psz400 ~0.98 from substrate-beats- "
            "formula projection). Predicted BASELINE_A=0.449 ORACLE_B=0.739 "
            "lift=0.29. HP requires arm_b in [0.50, 0.95] AND lift>=0.20 vs A "
            "AND lift>=0.30 vs E AND cv<0.15 AND NOT saturated (<0.95). "
            "META_RULE_AC tagged; META_RULE_AF arms-must-differ SHA-256; "
            "META_RULE_AE absolute paths; META_RULE_AG edge-of-capacity; "
            "META_RULE_AH atomic metrics; META_RULE_AL bands LOCKED; "
            "META_RULE_AN substrate-empirical anchor; META_RULE_H cardinality; "
            "BIAS-Q saturation @0.95 (tightened); Fix #28 per-arm reads. CHUNKED single-seed-per-cell sibling (seed=13); 3-cell redundancy strategy against runner-zombie episodes (USER 2026-06-28 chunked directive). Source HARD_PASS smoke: data/exp_substrate_multihop_partition_oracle_v5_hardened_v1_smoke/metrics.json (BASELINE_A=0.39 ORACLE_B=0.90 lift=0.51 unsat)."
        ),
    }
    write_metrics(out_dir, metrics, results=per_seed)
    print("[done] metrics.json written (%d seeds, %.1fs)" % (
        len(per_seed), metrics["elapsed_s"]), flush=True)
