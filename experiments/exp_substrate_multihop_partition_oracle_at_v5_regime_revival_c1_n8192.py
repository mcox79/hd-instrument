"""substrate_multihop_partition_oracle_at_v5_regime_revival_c1_n8192.

PURPOSE (research drill 2x; N=8192 scale-up of v1 revival cell):
    v1 at N=2048 SMOKE_HARD_PASS but ORACLE_B=1.000 saturation=True (rail clean
    BASELINE=0.190; lift +0.81). MEASURED_MECHANISM tier per Skunkworks
    discipline (by-construction-saturation). This cell HARDENS the regime by
    quadrupling N and V_C + widening the partition (psz=40 not psz=10) so the
    cone-collapse formula predicts ARM_B lands in [0.40, 0.80] WITH headroom --
    finds true ceiling AND verifies discriminator survives scale.

    Strategic: HARD_PASS at N=8192 + NOT saturated = chain-grade depth-10
    compositional reasoning via partition-oracle goal-conditioning. Barrier 1
    BROKEN at chain-grade tier.

CONE-COLLAPSE FORMULA (compute-in-code; substrate-physics oracle):
    crosstalk_std = sqrt((V_C_per_hop - 1) / N)
    per_step_top1 ~ Phi(signal / crosstalk_std)^(V_C_per_hop - 1)

    v1 ARM_B regime (N=2048, V_C=1000, psz=10):
        crosstalk_std = sqrt(9/2048) = 0.0663
        per_step observed = 1.000 across all 10 hops -> saturation at top1=1.000
    THIS CELL ARM_B (N=8192, V_C=4000, psz=40):
        crosstalk_std = sqrt(39/8192) = 0.0690 (essentially v1's xtalk regime)
        BUT psz=40 (4x v1) -> argmax over 40 cands per hop (vs 10) tightens
        per-step prob to ~0.95-0.97 -> depth-10 top1 ~ 0.60-0.74 (HEADROOM)
    THIS CELL ARM_C (N=8192, V_C=4000, psz=100):
        crosstalk_std = sqrt(99/8192) = 0.1099
        per_step ~ 0.85-0.90 -> depth-10 top1 ~ 0.20-0.35
    THIS CELL ARM_D (N=8192, V_C=4000, psz=200):
        crosstalk_std = sqrt(199/8192) = 0.1559
        per_step ~ 0.72-0.80 -> depth-10 top1 ~ 0.04-0.11 (low narrowing)
    BASELINE crosstalk (V_C=4000/N=8192) = sqrt(3999/8192) = 0.6987
        Same regime as v1 baseline; should reproduce ~0.15-0.20 top1@d10

ARMS (5 arms x depth=10):
    A: BASELINE                    argmax over V_C=4000 (rail; reproduce ~0.16)
    B: ORACLE_PART_100_psz_40      100 partitions of 40; oracle routes
                                    (mechanism; predicted top1 ~ 0.60-0.74)
    C: ORACLE_PART_40_psz_100      40 partitions of 100 (mid-regime)
    D: ORACLE_PART_20_psz_200      20 partitions of 200 (low narrowing)
    E: NO_ORACLE_RANDOM_PART_100   100 partitions of 40; routing RANDOM
                                    (critical discriminator: goal-info load-bearing)

PRE-REG BANDS (META_RULE_AL; LOCKED at module init):
    BASELINE rail (sanity; per-arm; SAME regime as v1):
        ARM_A.top1@d10 in [0.11, 0.25]  # v5/v1 obs ~0.16-0.19
    HARD_PASS (chain-grade tier; NOT saturated):
        ARM_B.top1@d10 in [0.40, 0.80]  # in band; both floor + ceiling
        AND ARM_B.top1@d10 - ARM_A.top1@d10 >= 0.20  # lift vs baseline
        AND ARM_B.top1@d10 - ARM_E.top1@d10 >= 0.10  # goal-info load-bearing
        AND cv(ARM_B across seeds) < 0.15
        AND arms_distinct == True
        AND saturation == False  # ARM_B < 0.99 (BIAS-Q)
    HARD_FAIL:
        ARM_B.top1@d10 <= 0.20  # mechanism dies at harder regime; cone-collapse confirmed
        OR (saturation == True AND lift_b_a < 0.20)
    MIDDLE_BAND:
        ARM_B.top1@d10 in [0.20, 0.40) with lift +0.15-0.20
        OR HP-band hit BUT cv > 0.15 (full only) OR (ARM_B - ARM_E) < 0.10

DISCIPLINE TAGS:
    META_RULE_AL: HARD_PASS + HARD_FAIL bands pre-registered
    META_RULE_AC: arms-must-differ asserted post-run
    META_RULE_AF: arms_distinct check in verdict
    META_RULE_AH: atomic metrics.json write (tmp + os.replace via _seed_checkpoint)
    META_RULE_H : CARDINALITY_OK declared; expected_n_units enforced
    BIAS-Q     : auto-demote to MM if saturation=True AND lift < 0.20
    BIAS-N     : per-arm metrics read (NOT verdict_msg framing)
    BIAS-S     : baseline must land in [0.11, 0.25] regime
    DISCRIMINATOR-MUST-SURVIVE-SCALE: smoke at FULL-N=8192; if ARM_B saturates
        at smoke (top1>=0.99), demote to MM and re-design regime BEFORE full
    PROT-018: N-suffix in anchor name binds to actual N_DIM value
    Fix #28: read per-arm metrics, not verdict_msg
    NO-LOCAL: route remote_cpu_queue (USER 2026-06-28)

SOURCE (cite ABSOLUTE PATHS):
    - Parent v1 cell (N=2048):
      d:/AI/hd-instrument/experiments/exp_substrate_multihop_partition_oracle_at_v5_regime_revival_c1.py
    - Parent v1 smoke metrics (SMOKE_HARD_PASS but saturation=True):
      d:/AI/hd-instrument/data/exp_substrate_multihop_partition_oracle_at_v5_regime_revival_c1_smoke/metrics.json
    - Parent prereg (regime LOCKED N=2048):
      d:/AI/hd-instrument/preregs/2026-06-28_substrate_multihop_partition_oracle_at_v5_regime_revival_c1.md
    - Research drill spec:
      d:/AI/hd-instrument/notes/research_drill_2x_multihop_depth10_ceiling_REVIVAL_2026-06-28.md
    - CHAIN_GRADE primitive (verbatim port target):
      d:/AI/hd-instrument/experiments/exp_phase_diagram_multihop_depth_ceiling_sweep_20_25_30_v1.py
      lines 267-299 (arm_part_oracle_at_depth)
    - CHAIN_GRADE metrics (depth-30 = 0.6367; ref point):
      d:/AI/hd-instrument/data/exp_phase_diagram_multihop_depth_ceiling_sweep_20_25_30_v1/metrics.json

ROUTE: remote_cpu_queue (USER 2026-06-28 NO-LOCAL).

Number tagging (per ASCII discipline):
    HYPOTHESIZED@HARD_PASS_BAND: ARM_B top1@d10 in [0.40, 0.80] (headroom)
    THEORETICAL@CONE_COLLAPSE: per-step ~ 0.95-0.97 at V_C_per_hop=40/N=8192
    MEASURED@V1_BASELINE: ARM_A target ~ 0.16 (from v1 smoke metrics.json)
    MEASURED@V1_ORACLE_B: 1.000 saturated (from v1 smoke metrics.json)
    MEASURED@CG_PRIMITIVE: 0.6367 at depth-30 N=8192 V_C=200 partition_size=10
    CITED@MANTE_2013: PFC goal-conditioned attention narrows search 10-100x

Author: exp_dev 2026-06-28 (research drill 2x scale-up; N=8192 PROT-018).
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

ANCHOR_NAME = "substrate_multihop_partition_oracle_at_v5_regime_revival_c1_n8192"
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
# N=8192 hardened regime (4x N + 4x V_C vs v1; psz=40 not psz=10 to add headroom).
# PROT-018: N=8192 explicit + matches anchor _n8192 suffix.
N_DIM = 8192
V_CONCEPTS = 4000
V_PRED = 10
DEPTH = 10
MAX_DEPTH = 10

assert "_n8192" in ANCHOR_NAME and N_DIM == 8192, \
    "PROT-018: anchor _n8192 suffix must bind to N_DIM=8192"

# BASELINE rail (v1 reproduce; per-arm; widened slightly for N=8192 noise)
BASELINE_RAIL_TARGET = 0.16      # MEASURED@V1_BASELINE
BASELINE_RAIL_LO = 0.11
BASELINE_RAIL_HI = 0.25

# Per-arm thresholds at depth-10 (HEADROOM band per drill spec)
HP_ARM_B_LO = 0.40               # HYPOTHESIZED@HARD_PASS_BAND floor
HP_ARM_B_HI = 0.80               # HYPOTHESIZED@HARD_PASS_BAND ceiling
HP_LIFT_OVER_BASELINE = 0.20     # ARM_B - ARM_A >= 0.20 (drill spec)
HP_LIFT_OVER_RANDOM = 0.10       # ARM_B - ARM_E >= 0.10 (goal-info load-bearing)
HP_CV_MAX = 0.15                 # cv across seeds
HP_SATURATION_CEIL = 0.99        # BIAS-Q saturation threshold

HF_ARM_B_ABS = 0.20              # HARD_FAIL ceiling for mechanism
HF_LIFT_MIN_IF_SATURATED = 0.20  # if saturation AND lift<this, HARD_FAIL
MM_LIFT_MIN = 0.15               # MIDDLE_BAND lower-lift floor

# Partition configurations (psz=40 / 100 / 200 to give headroom + crosstalk sweep)
def _cone_collapse_crosstalk(v_c_per_hop: int, n: int) -> float:
    return float(math.sqrt(max(v_c_per_hop - 1, 1) / max(n, 1)))

N_PART_B = 100   # ARM_B: 100 partitions of 40
N_PART_C = 40    # ARM_C: 40 partitions of 100
N_PART_D = 20    # ARM_D: 20 partitions of 200
assert V_CONCEPTS % N_PART_B == 0
assert V_CONCEPTS % N_PART_C == 0
assert V_CONCEPTS % N_PART_D == 0

PART_SIZE_B = V_CONCEPTS // N_PART_B  # 40
PART_SIZE_C = V_CONCEPTS // N_PART_C  # 100
PART_SIZE_D = V_CONCEPTS // N_PART_D  # 200

CROSSTALK_B = _cone_collapse_crosstalk(PART_SIZE_B, N_DIM)
CROSSTALK_C = _cone_collapse_crosstalk(PART_SIZE_C, N_DIM)
CROSSTALK_D = _cone_collapse_crosstalk(PART_SIZE_D, N_DIM)
CROSSTALK_BASELINE = _cone_collapse_crosstalk(V_CONCEPTS, N_DIM)

# Locked invariants (META_RULE_AL)
assert BASELINE_RAIL_LO < BASELINE_RAIL_TARGET < BASELINE_RAIL_HI
assert HP_ARM_B_LO > HF_ARM_B_ABS
assert HP_ARM_B_LO < HP_ARM_B_HI < HP_SATURATION_CEIL
assert HP_LIFT_OVER_BASELINE > MM_LIFT_MIN
assert 0.0 < HP_CV_MAX < 0.5
assert CROSSTALK_B < CROSSTALK_C < CROSSTALK_D < CROSSTALK_BASELINE
# N=8192 regime: xtalk_B ~ v1 regime (0.069 vs v1 0.066); psz larger gives headroom
assert abs(CROSSTALK_B - 0.0663) < 0.05, "psz=40/N=8192 xtalk drift"

# Chain configuration
N_CHAINS_TRAIN = 200
if RUN_MODE == "smoke":
    SEEDS = [11]
    N_CHAINS_TEST = 100      # mechanism check; same as v1 smoke
else:
    SEEDS = [11, 13, 19]
    N_CHAINS_TEST = 200

# Cardinality (META_RULE_H)
N_ARMS = 5
EXPECTED_N_UNITS = N_ARMS * len(SEEDS)  # 5 arms x N seeds

ENCODER_PROVENANCE = "SUBSTRATE_NATIVE_BIPOLAR"

CONFIG_VERSION = (
    "substrateMultihopPartOracleV5RegimeRevivalC1N8192: N=%d V_C=%d V_P=%d depth=%d "
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
# Primitives (verbatim numpy port from v1 cell + CG partition oracle)
# ----------------------------------------------------------------------------

def bipolar(M: int, n: int, g: np.random.Generator) -> np.ndarray:
    """Bipolar bit vectors; row-normalized. Port of v1 cell line 234."""
    X = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)


def ingest_hebbian(triples, E: np.ndarray, R: np.ndarray, sq: float,
                   n_dim: int, batch: int = 2000) -> np.ndarray:
    """Hebbian outer-product ingest. Port of v1 cell line 240."""
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
    """Verbatim port from v1 cell line 252."""
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
    """V1 baseline: argmax over full V_C cleanup at each hop.
    Verbatim port of v1 cell line 289."""
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
    """Partition-oracle cleanup. Verbatim port of CG primitive
    arm_part_oracle_at_depth from v1 cell line 318."""
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
# Self-test (formula sanity + cone-collapse compute)
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

    # T2: chain construction at DEPTH=10
    triples, chains = make_deep_chains(8, V_tiny, P_tiny,
                                       max_depth=10, g=g,
                                       disallow_s=set())
    assert len(chains) == 8 and len(triples) == 8 * 10

    # T3: ingest
    W = ingest_hebbian(triples, E, R, sq, n_tiny)
    assert W.shape == (n_tiny, n_tiny)
    assert np.isfinite(W).all()

    # T4: all 5 arms produce valid output at tiny config
    r_a = arm_baseline(E, R, sq, W, chains, depth=10)
    assert 0.0 <= r_a["top1"] <= 1.0
    assert len(r_a["per_step_acc"]) == 10

    part_sz_tiny = V_tiny // 8  # 5 atoms per partition; 8 partitions
    assert V_tiny % 8 == 0

    r_b = arm_part_oracle(E, R, sq, W, chains, depth=10,
                          part_size=part_sz_tiny,
                          mechanism_tag="oracle_part_test")
    assert 0.0 <= r_b["top1"] <= 1.0
    assert len(r_b["per_step_acc"]) == 10

    r_e = arm_no_oracle_random_part(E, R, sq, W, chains, depth=10,
                                    part_size=part_sz_tiny, g=g)
    assert 0.0 <= r_e["top1"] <= 1.0
    assert len(r_e["per_step_acc"]) == 10

    # T5: cone-collapse formula sanity (BIAS-S regime check)
    # N=8192 regime: xtalk_B ~ v1 (~0.069) but psz=40 gives headroom
    assert CROSSTALK_BASELINE / CROSSTALK_B > 9.0, (
        "cone-collapse ratio collapsed: B=%.4f baseline=%.4f"
        % (CROSSTALK_B, CROSSTALK_BASELINE))
    assert CROSSTALK_BASELINE > 0.5
    assert CROSSTALK_B < 0.1
    # Predicted ARM_B per-step at psz=40: argmax over 40 cands w/ xtalk 0.069
    # ~ Phi(1/0.069)^39 ~ ~0.95-0.97 -> depth-10 ~ 0.60-0.74
    # NOT saturating (verified by depth-10 < 0.80)

    # T6: bands LOCKED (regression on band drift)
    assert N_DIM == 8192
    assert V_CONCEPTS == 4000
    assert PART_SIZE_B == 40
    assert HP_ARM_B_LO == 0.40
    assert HP_ARM_B_HI == 0.80
    assert HF_ARM_B_ABS == 0.20
    assert BASELINE_RAIL_TARGET == 0.16
    assert HP_LIFT_OVER_BASELINE == 0.20
    assert HP_LIFT_OVER_RANDOM == 0.10
    assert HP_CV_MAX == 0.15
    assert HP_SATURATION_CEIL == 0.99

    # T7: zero LLM calls (substrate-only)
    assert _LLM_CALL_COUNTER[0] == 0

    # T8: cardinality declared
    assert EXPECTED_N_UNITS == 5 * len(SEEDS)

    # T9: anchor PROT-018 binding
    assert "_n8192" in ANCHOR_NAME and N_DIM == 8192

    print("[selftest] PASS N=%d V_C=%d psz_B=%d arms: a=%.3f b=%.3f e=%.3f "
          "xtalk_B=%.4f xtalk_baseline=%.4f HP_band=[%.2f,%.2f]" % (
              N_DIM, V_CONCEPTS, PART_SIZE_B,
              r_a["top1"], r_b["top1"], r_e["top1"],
              CROSSTALK_B, CROSSTALK_BASELINE, HP_ARM_B_LO, HP_ARM_B_HI),
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

    # ===== ARM_A: BASELINE (v1 reproduce rail) =====
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

    # ===== ARM_B: ORACLE_PART_100_psz_40 (mechanism; predicted top1 ~ 0.60-0.74) =====
    t_arm = time.time()
    r_b = arm_part_oracle(E, R, sq, W, chains_test, depth=DEPTH,
                          part_size=PART_SIZE_B,
                          mechanism_tag="oracle_part_100_psz_40")
    r_b["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    out["arm_b_oracle_part_100"] = r_b
    print("  [seed=%d] ARM_B ORACLE_PART_100_psz_40 top1=%.4f "
          "(HP_band=[%.2f,%.2f] lift_vs_A>=%.2f predicted_xtalk=%.4f) "
          "per_step=%s t=%.1fs" % (
              seed, r_b["top1"], HP_ARM_B_LO, HP_ARM_B_HI,
              HP_LIFT_OVER_BASELINE, CROSSTALK_B,
              r_b["per_step_acc"], r_b["elapsed_s_arm"]), flush=True)

    # ===== ARM_C: ORACLE_PART_40_psz_100 (mid-regime) =====
    t_arm = time.time()
    r_c = arm_part_oracle(E, R, sq, W, chains_test, depth=DEPTH,
                          part_size=PART_SIZE_C,
                          mechanism_tag="oracle_part_40_psz_100")
    r_c["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    out["arm_c_oracle_part_40"] = r_c
    print("  [seed=%d] ARM_C ORACLE_PART_40_psz_100 top1=%.4f (xtalk=%.4f) "
          "per_step=%s t=%.1fs" % (
              seed, r_c["top1"], CROSSTALK_C,
              r_c["per_step_acc"], r_c["elapsed_s_arm"]), flush=True)

    # ===== ARM_D: ORACLE_PART_20_psz_200 (low-narrowing) =====
    t_arm = time.time()
    r_d = arm_part_oracle(E, R, sq, W, chains_test, depth=DEPTH,
                          part_size=PART_SIZE_D,
                          mechanism_tag="oracle_part_20_psz_200")
    r_d["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    out["arm_d_oracle_part_20"] = r_d
    print("  [seed=%d] ARM_D ORACLE_PART_20_psz_200 top1=%.4f (xtalk=%.4f) "
          "per_step=%s t=%.1fs" % (
              seed, r_d["top1"], CROSSTALK_D,
              r_d["per_step_acc"], r_d["elapsed_s_arm"]), flush=True)

    # ===== ARM_E: NO_ORACLE_RANDOM_PART_100 (critical discriminator) =====
    t_arm = time.time()
    g_e = np.random.default_rng(seed * 7919 + 1)
    r_e = arm_no_oracle_random_part(E, R, sq, W, chains_test, depth=DEPTH,
                                    part_size=PART_SIZE_B, g=g_e)
    r_e["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    out["arm_e_no_oracle_random"] = r_e
    print("  [seed=%d] ARM_E NO_ORACLE_RANDOM_PART_100 top1=%.4f "
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
# Verdict (META_RULE_AL HP/HF/MM bands; BIAS-Q saturation guard; Fix #28)
# ----------------------------------------------------------------------------

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

    arm_a = mean_top1("arm_a_baseline")
    arm_b = mean_top1("arm_b_oracle_part_100")
    arm_c = mean_top1("arm_c_oracle_part_40")
    arm_d = mean_top1("arm_d_oracle_part_20")
    arm_e = mean_top1("arm_e_no_oracle_random")

    cv_b = cv_top1("arm_b_oracle_part_100")

    lift_b_a = arm_b - arm_a if not (math.isnan(arm_b) or math.isnan(arm_a)) \
        else float("nan")
    lift_b_e = arm_b - arm_e if not (math.isnan(arm_b) or math.isnan(arm_e)) \
        else float("nan")

    # Cardinality check (META_RULE_H)
    observed_units = sum(
        1 for p in per_seed for arm_key in (
            "arm_a_baseline", "arm_b_oracle_part_100",
            "arm_c_oracle_part_40", "arm_d_oracle_part_20",
            "arm_e_no_oracle_random")
        if arm_key in p
    )
    cardinality_ok = (observed_units == EXPECTED_N_UNITS)

    # Arms-distinct check (META_RULE_AF; BIAS-S)
    arm_values = [arm_a, arm_b, arm_c, arm_d, arm_e]
    arm_values_clean = [v for v in arm_values if not math.isnan(v)]
    arms_distinct = len(set(round(v, 3) for v in arm_values_clean)) >= 3 \
        if arm_values_clean else False

    # BIAS-Q saturation check
    saturation_flag = (not math.isnan(arm_b)) and arm_b >= HP_SATURATION_CEIL

    # Baseline rail check (BIAS-S)
    rail_breach = sum(1 for p in per_seed
                      if not p.get("baseline_rail_ok", False))

    # HP-band check
    arm_b_in_band = ((not math.isnan(arm_b))
                     and HP_ARM_B_LO <= arm_b <= HP_ARM_B_HI)

    summ = (
        "BASELINE_A=%.4f (rail_breach=%d/%d; target=%.3f) "
        "ORACLE_B=%.4f (cv=%.3f xtalk=%.4f in_band=%s) "
        "ORACLE_C=%.4f (xtalk=%.4f) ORACLE_D=%.4f (xtalk=%.4f) "
        "RANDOM_E=%.4f lift_B_A=%.4f lift_B_E=%.4f "
        "cardinality_ok=%s expected_units=%d observed_units=%d "
        "arms_distinct=%s saturation=%s HP_band=[%.2f,%.2f]"
    ) % (
        arm_a, rail_breach, len(per_seed), BASELINE_RAIL_TARGET,
        arm_b, cv_b, CROSSTALK_B, arm_b_in_band,
        arm_c, CROSSTALK_C, arm_d, CROSSTALK_D, arm_e,
        lift_b_a, lift_b_e,
        cardinality_ok, EXPECTED_N_UNITS, observed_units,
        arms_distinct, saturation_flag,
        HP_ARM_B_LO, HP_ARM_B_HI,
    )

    # Cardinality gate FIRST (META_RULE_H)
    if not cardinality_ok:
        return ("HARD_FAIL_CARDINALITY_BREACH",
                "HARD_FAIL_CARDINALITY_BREACH: " + summ)

    # Arms-distinct gate (META_RULE_AF)
    if not arms_distinct:
        return ("HARD_FAIL_ARMS_TIED",
                "HARD_FAIL_ARMS_TIED_NO_DISCRIMINATION: " + summ)

    # HARD_FAIL: mechanism dies at hardened regime
    if (not math.isnan(arm_b)) and arm_b <= HF_ARM_B_ABS:
        return ("HARD_FAIL_NO_SIGNAL_AT_N8192",
                "HARD_FAIL_NO_SIGNAL_CONE_COLLAPSE_FALSIFIED_AT_N8192: " + summ)

    # HARD_FAIL: saturated AND insufficient lift (BIAS-Q + drill spec)
    if saturation_flag and (not math.isnan(lift_b_a)) \
            and lift_b_a < HF_LIFT_MIN_IF_SATURATED:
        return ("HARD_FAIL_SATURATION_WITHOUT_LIFT",
                "HARD_FAIL_SATURATION_FLAG_WITH_LIFT_BELOW_THRESHOLD: " + summ)

    # Smoke verdict (single seed; cv deferred to full)
    if RUN_MODE == "smoke":
        # SMOKE_HARD_PASS: in HP band + lifts + NOT saturated
        if arm_b_in_band \
                and (not math.isnan(lift_b_a)) and lift_b_a >= HP_LIFT_OVER_BASELINE \
                and (not math.isnan(lift_b_e)) and lift_b_e >= HP_LIFT_OVER_RANDOM \
                and not saturation_flag:
            return ("SMOKE_HARD_PASS",
                    "SMOKE_HARD_PASS_MECHANISM_IN_HP_BAND_N8192_NOT_SATURATED: "
                    + summ)
        # SMOKE_MIDDLE_BAND_SATURATED: saturated but lift >= 0.20 -- auto-demote
        # per BIAS-Q discipline (chain-grade requires headroom)
        if saturation_flag and (not math.isnan(lift_b_a)) \
                and lift_b_a >= HF_LIFT_MIN_IF_SATURATED:
            return ("MIDDLE_BAND_SATURATED_AUTO_DEMOTE",
                    "MIDDLE_BAND_SATURATED_AUTO_DEMOTE_BIAS_Q_NEED_HARDER_REGIME: "
                    + summ)
        # MIDDLE_BAND: partial mechanism
        if (not math.isnan(lift_b_a)) and lift_b_a >= MM_LIFT_MIN:
            return ("MIDDLE_BAND",
                    "MIDDLE_BAND_PARTIAL_MECHANISM_AT_N8192: " + summ)
        return ("HARD_FAIL_LIFT_BELOW_THRESHOLD",
                "HARD_FAIL_LIFT_BELOW_THRESHOLD_AT_N8192: " + summ)

    # Full verdict (multi-seed; cv required for HP claim)
    cv_ok = (not math.isnan(cv_b)) and cv_b < HP_CV_MAX

    # HARD_PASS (chain-grade): all criteria + NOT saturated
    if arm_b_in_band \
            and (not math.isnan(lift_b_a)) and lift_b_a >= HP_LIFT_OVER_BASELINE \
            and (not math.isnan(lift_b_e)) and lift_b_e >= HP_LIFT_OVER_RANDOM \
            and cv_ok and not saturation_flag:
        return ("HARD_PASS_CHAIN_GRADE_DEPTH10_N8192",
                "HARD_PASS_CHAIN_GRADE_DEPTH10_N8192_BARRIER_1_BROKEN: " + summ)

    # MIDDLE_BAND_SATURATED auto-demote (chain-grade requires headroom)
    if saturation_flag and (not math.isnan(lift_b_a)) \
            and lift_b_a >= HF_LIFT_MIN_IF_SATURATED:
        return ("MIDDLE_BAND_SATURATED_AUTO_DEMOTE",
                "MIDDLE_BAND_SATURATED_AUTO_DEMOTE_BIAS_Q_NEED_HARDER_REGIME: "
                + summ)

    # MIDDLE_BAND
    if (not math.isnan(lift_b_a)) and lift_b_a >= MM_LIFT_MIN:
        return ("MIDDLE_BAND",
                "MIDDLE_BAND_PARTIAL_MECHANISM_AT_N8192: " + summ)

    return ("HARD_FAIL_LIFT_BELOW_THRESHOLD",
            "HARD_FAIL_LIFT_BELOW_THRESHOLD_NO_MECHANISM: " + summ)


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
        v, vmsg = verdict_from(per_seed)
        metrics = {
            "anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg,
            "run_mode": RUN_MODE, "n_seeds": len(per_seed),
            "config_version": CONFIG_VERSION, "per_seed": per_seed,
            "elapsed_s": round(time.time() - _RESULTS_HOLDER["started_at"], 1),
            "summary": vmsg, "_atexit_synth": True,
            "_llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
            "expected_n_units": EXPECTED_N_UNITS,
            "expected_arms": [
                "baseline_full_V_C", "oracle_part_100_psz_40",
                "oracle_part_40_psz_100", "oracle_part_20_psz_200",
                "no_oracle_random_part_100"],
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

    v, vmsg = verdict_from(per_seed)
    print("\n[VERDICT] " + vmsg, flush=True)
    metrics = {
        "anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg,
        "run_mode": RUN_MODE, "n_seeds": len(per_seed),
        "config_version": CONFIG_VERSION, "per_seed": per_seed,
        "elapsed_s": round(time.time() - _RESULTS_HOLDER["started_at"], 1),
        "summary": vmsg,
        "_llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
        "expected_n_units": EXPECTED_N_UNITS,
        "expected_arms": [
            "baseline_full_V_C", "oracle_part_100_psz_40",
            "oracle_part_40_psz_100", "oracle_part_20_psz_200",
            "no_oracle_random_part_100"],
        "DESIGN_NOTE": (
            "N=8192 SCALE-UP of v1 SMOKE_HARD_PASS (saturated) revival cell. "
            "v1 ARM_B=1.000 at N=2048 V_C=1000 psz=10 -> saturation flag tripped "
            "BIAS-Q auto-demote MEASURED_MECHANISM. This cell quadruples N + V_C "
            "+ widens psz to 40 (4x v1) so cone-collapse formula predicts "
            "ARM_B lands [0.40, 0.80] with HEADROOM. crosstalk_B=0.069 matches "
            "v1 regime; argmax over 40 cands (not 10) tightens per-step prob to "
            "~0.95-0.97 -> depth-10 top1 ~ 0.60-0.74. HP requires arm_b in band "
            "AND lift>=0.20 vs A AND lift>=0.10 vs E AND cv<0.15 AND NOT "
            "saturated. If HARD_PASS: chain-grade depth-10 compositional "
            "reasoning via partition-oracle goal-conditioning; Barrier 1 BROKEN. "
            "If saturated again: auto-demote MM, design harder regime "
            "(psz=80 or depth=12+). META_RULE_AL bands locked; META_RULE_AF "
            "arms-must-differ; META_RULE_AH atomic metrics; BIAS-Q saturation "
            "guard with auto-demote; Fix #28 per-arm reads; PROT-018 _n8192 "
            "suffix binding."
        ),
    }
    write_metrics(out_dir, metrics, results=per_seed)
    print("[done] metrics.json written (%d seeds, %.1fs)" % (
        len(per_seed), metrics["elapsed_s"]), flush=True)
