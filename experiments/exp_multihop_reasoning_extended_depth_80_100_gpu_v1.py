"""multihop_reasoning_extended_depth_80_100_gpu_v1.

USER directive 2026-07-01: extend Atom 11 (per-step scale-invariance in
partition-oracle multihop) to extreme depth d=80 and d=100. Atom 11 predicts
per-step 0.9853 -> d=155 -> 0.10 (mechanism death floor). This cell tests
Atom 11 expansion criterion (c): does the per-step law extend to extreme
depth, or does mechanism death manifest earlier than predicted?

PRIOR-WORK CHECK (substrate-KB concept-query 2026-07-01, exp_dev on spawn):
  Q1: "multihop reasoning depth 80 100 extended depth per step accuracy scale invariance"
      top hit cosine=0.286 (wave14yp_multihop_depth_100 prereg, stale
      exploratory from 2026-05-21, different substrate config; below novelty
      threshold 0.30)
  Q2: "multihop chain length 80 100 partition oracle beyond depth 60"
      top hit cosine=0.322 (phase_diagram_multihop_depth_extension_v1;
      predecessor lineage, not duplicate)
  Q3: predispatch_check.py: 0 matching landings/atoms; PROCEED
  Rediscovery-vs-novel: d15/30/60 rails reproduce prior chain-grade MEASURED;
  d80 and d100 with partition-oracle at N=8192/200-chains/V_C=200 are
  GENUINELY NEW phase points extending Landing 10 (d60 CG) by 67%.

CROSS-CELL RAILS (3, prior chain-grade MEASURED):
  - RAIL_DEPTH_15 must reproduce prior 0.808 +/- 0.05
  - RAIL_DEPTH_30 must reproduce prior 0.637 +/- 0.05
  - RAIL_DEPTH_60 must reproduce prior 0.480 +/- 0.05 (from Landing 10)

ATOM 11 EXTENSION DISCRIMINATOR:
  Predicted per-step 0.9853 (Atom 11 pin):
    d=80 -> 0.9853^80 = 0.3058
    d=100 -> 0.9853^100 = 0.2274
    d=155 -> 0.9853^155 = 0.10 (Atom 11 death floor)
  Empirical per-step from Landing 10 (d60 landing): 0.988 -> predicts
    d=80: 0.988^80 = 0.383
    d=100: 0.988^100 = 0.300
  Cell tests Atom 11's specific 0.9853 pin +/- 0.10 tolerance:
    HP_80: |PART_80HOP - 0.303| <= 0.10 (band [0.203, 0.403])
    HP_100: |PART_100HOP - 0.222| <= 0.10 (band [0.122, 0.322])
  Discriminator alternatives:
    HF_MECHANISM_DEATH_80: PART_80HOP < 0.10 (mechanism cliff before d=155)
    HF_LAW_BREAKS_80: |PART_80HOP - 0.303| > 0.15 (outside law-holds envelope)
    HF_LAW_BREAKS_100: |PART_100HOP - 0.222| > 0.15

ARMS (5):
  ARM_PART_ORACLE_15HOP   rail (reproduce prior 0.808)
  ARM_PART_ORACLE_30HOP   rail (reproduce prior 0.637)
  ARM_PART_ORACLE_60HOP   rail (reproduce prior 0.480 from Landing 10)
  ARM_PART_ORACLE_80HOP   NEW extreme phase point (Atom 11 predicts 0.303)
  ARM_PART_ORACLE_100HOP  NEW extreme phase point (Atom 11 predicts 0.222)

PRE-REG BANDS (LOCKED at module init):
  Sanity rails:
    RAIL_15: PART_15HOP in [0.758, 0.858]
    RAIL_30: PART_30HOP in [0.587, 0.687]
    RAIL_60: PART_60HOP in [0.430, 0.530]
  Novel extreme-depth phase points (Atom 11 test):
    HP_80HOP_ATOM11_EXTENDS: |PART_80HOP - 0.303| <= 0.10
    HP_100HOP_ATOM11_EXTENDS: |PART_100HOP - 0.222| <= 0.10
    HF_MECHANISM_DEATH_80: PART_80HOP < 0.10 (early death)
    HF_LAW_BREAKS_80: |PART_80HOP - 0.303| > 0.15
    HF_LAW_BREAKS_100: |PART_100HOP - 0.222| > 0.15
  Stability:
    cv across seeds <= 0.10 for HARD_PASS claim

DISCRIMINATOR TIERS (6-way):
  CHAIN_GRADE_LAW_EXTENDS_TO_EXTREME_DEPTH: all 3 rails + BOTH HP_80/100 + cv OK
    -> Atom 11 CG-lift on criterion (c); envelope extends 67% beyond d=60 CG
  PARTIAL_LAW_EXTENDS: rails + only ONE HP passes (d=80 XOR d=100)
    -> mechanism weakens between d=80 and d=100
  LAW_BREAKS_AT_EXTREME_DEPTH: rails + either HP fails outside +/- 0.15 band
    -> Atom 11's per-step formula does NOT extend to extreme depth (negative)
  MECHANISM_DEATH_EARLIER_THAN_155: PART_80HOP < 0.10 (rails clean)
    -> mechanism death boundary earlier than Atom 11 predicts (negative)
  RAIL_BREACH: any rail majority breach -> setup broken
  MIDDLE_BAND: partial passes, cv breach, or missing metrics

INFORMATIONAL FIELD:
  atom11_extension_verdict:
    - "CG_LIFT_C"       if CHAIN_GRADE_LAW_EXTENDS_TO_EXTREME_DEPTH
    - "PARTIAL_80_ONLY" if d=80 passes, d=100 fails outside 0.10 band
    - "PARTIAL_100_ONLY" if d=100 passes, d=80 fails outside 0.10 band
    - "LAW_BREAKS"      if LAW_BREAKS_AT_EXTREME_DEPTH
    - "EARLY_DEATH"     if MECHANISM_DEATH_EARLIER_THAN_155
    - "unknown"         otherwise

GPU IMPLEMENTATION (Fix #24 active GPU use):
  - All Ws (W_d15/30/60/80/100) built on torch.cuda via batched outer-product
    accumulation; E, R kept on GPU throughout.
  - Argmax cleanup is torch.argmax(E_part @ (W @ key)) on GPU.
  - Per-W memory at N=8192: 1 W = 268MB float32; 5 Ws = ~1.34GB resident;
    plus E (6.5MB) + R (0.3MB) = ~1.35GB peak; well under 8GB GPU.
  - Peak alloc measured per-seed; each W freed via del + empty_cache post-seed.
  - W_d100 requires make_deep_chains at max_depth=100 (200*100=20000 bindings);
    M/N = 20000/8192 = 2.44 (below unit); per-step 0.985 confirms operation.

DISCRIMINATOR-MUST-SURVIVE-SCALE (path A: full-N smoke):
  Smoke runs at N=8192 (production N, not down-sized). Only n_chains reduced
  to 25 (from 200) to keep smoke wall < 120s. Substrate tolerance regime
  preserved; Atom 11 discriminator fires on real full-N binding-density.

DEFENSIVE ERROR-CHECKING (META_RULE_AH + start-marker + heartbeat):
  - start_marker written at main() entry
  - crash_diagnostic in outer try/except (SystemExit + KeyboardInterrupt re-raise)
  - per-seed heartbeat via _cell_heartbeat helper
  - metrics.json atomic write via write_metrics helper

ASCII-only; per-seed checkpoint (PROT-021); atexit synthesizer;
zero-LLM-call assert. Author: exp_dev 2026-07-01 (Atom 11 extension test).
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
import json
import math
import os
import platform
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

# ----------------------------------------------------------------------------
# GPU GUARD (Fix #24: GPU dispatch must actually use GPU)
# ----------------------------------------------------------------------------
try:
    import torch
except ImportError:
    print("[FATAL] torch not installed; cannot run experiment.", flush=True)
    sys.exit(1)

GPU_AVAIL = torch.cuda.is_available()
if GPU_AVAIL:
    DEVICE = torch.device("cuda")
    GPU_NAME = torch.cuda.get_device_name(0)
    GPU_MAX_MEM_GB = torch.cuda.get_device_properties(0).total_memory / 1e9
    print("[GPU] device=%s name=%s total_mem=%.1fGB" % (
        DEVICE, GPU_NAME, GPU_MAX_MEM_GB), flush=True)
else:
    DEVICE = torch.device("cpu")
    GPU_NAME = "cpu_fallback"
    GPU_MAX_MEM_GB = 0.0
    print("[GPU] WARN: cuda not available; running on CPU. "
          "Smoke OK; full dispatch MUST be GPU per Fix #24.", flush=True)

from experiments._seed_checkpoint import (
    get_output_dir, resumable_seeds, write_partial_key, aggregate_partials,
    write_metrics,
)

ANCHOR_NAME = "multihop_reasoning_extended_depth_80_100_gpu_v1"
_LLM_CALL_COUNTER = [0]

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true", dest="self_test")
_ARGS, _ = _ap.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = ("smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE)
            else os.environ.get("HDLAB_RUN_MODE", "full").lower())

# ----------------------------------------------------------------------------
# PRE-REG BANDS (LOCKED at module init)
# ----------------------------------------------------------------------------
# Rails from prior chain-grade landings:
#   depth_extension_v1 + depth_ceiling_sweep_v1: PART_15HOP=0.808
#   depth_ceiling_sweep_v1: PART_30HOP=0.637
#   Landing 10 (depth_45_to_60_gpu_v1): PART_60HOP=0.480 (0.535+0.435+0.470)/3
RAIL_15_TARGET = 0.808
RAIL_15_LO = 0.758
RAIL_15_HI = 0.858
RAIL_30_TARGET = 0.637
RAIL_30_LO = 0.587
RAIL_30_HI = 0.687
RAIL_60_TARGET = 0.480
RAIL_60_LO = 0.430
RAIL_60_HI = 0.530

# Atom 11 predictions at per-step 0.9853:
#   0.9853^80 = 0.3058; 0.9853^100 = 0.2274; 0.9853^155 = 0.10 death floor
ATOM11_PER_STEP = 0.9853
ATOM11_TARGET_80 = 0.303   # 0.9853^80 rounded
ATOM11_TARGET_100 = 0.222  # 0.9853^100 rounded
ATOM11_TOL_HP = 0.10       # HP within +/- 0.10 of prediction
ATOM11_TOL_LAW_BREAKS = 0.15  # HF if outside +/- 0.15 of prediction

HP_80HOP_LO = ATOM11_TARGET_80 - ATOM11_TOL_HP   # 0.203
HP_80HOP_HI = ATOM11_TARGET_80 + ATOM11_TOL_HP   # 0.403
HP_100HOP_LO = ATOM11_TARGET_100 - ATOM11_TOL_HP # 0.122
HP_100HOP_HI = ATOM11_TARGET_100 + ATOM11_TOL_HP # 0.322

HF_MECHANISM_DEATH_80 = 0.10  # d80 HF if < this (mechanism early-death cliff)
HF_LAW_BREAKS_80_DEVIATION = ATOM11_TOL_LAW_BREAKS  # |d80 - 0.303| > 0.15
HF_LAW_BREAKS_100_DEVIATION = ATOM11_TOL_LAW_BREAKS  # |d100 - 0.222| > 0.15

PHASE_CV_MAX = 0.10  # per-arm seed cv cap for HARD_PASS claim

# CRLB / capacity-feasibility (META_RULE_9 CRLB gate):
# Partition-oracle argmax over PART_SIZE=10 items at N=8192.
# Per-hop random-guess floor = 1/PART_SIZE = 0.10 (argmax over 10 items).
CRLB_FLOOR_COMPUTED = 1.0 / 10.0  # = 0.10
CRLB_FORMULA = "per_hop_random_guess = 1/PART_SIZE = 1/10 = 0.10"

# Discriminator reachability (verified):
#   HP_80 requires d80 in [0.203, 0.403]; per-step 0.986 -> 0.328 (in band).
#     Broken mechanism hits floor 0.10 (0.20 out of band); alive at 0.986
#     hits 0.328 (in band). 3-way signal (pass/weak/broken) reachable.
#   HP_100 requires d100 in [0.122, 0.322]; per-step 0.986 -> 0.247 (in band).
#     Broken 0.10 (0.12 out of band, just outside HP but touches HF floor).
#     Alive at 0.986 hits 0.247 (in band). 3-way signal reachable.
#   HF_LAW_BREAKS_80: |d80 - 0.303| > 0.15 -> d80 < 0.153 or > 0.453.
#     Per-step 0.98 -> 0.199 (in-band); 0.97 -> 0.088 (fires HF); 0.99 -> 0.448
#     (in-band). Fires for per-step < 0.975 or > 0.994.
#   HF_MECHANISM_DEATH_80: d80 < 0.10 requires per-step < 0.9716 -> exists.
DISCRIMINATOR_REACHABILITY = True
DISCRIMINATOR_REACH_NOTE = (
    "HP_80 [0.203, 0.403] reachable at per-step [0.980, 0.989]; "
    "HP_100 [0.122, 0.322] reachable at per-step [0.979, 0.988]; "
    "HF_LAW_BREAKS_80 fires per-step < 0.975 or > 0.994; "
    "HF_MECHANISM_DEATH_80 fires per-step < 0.972. All gates on live-decay branch."
)

# Locked invariants (regression guards)
assert RAIL_15_LO < RAIL_15_TARGET < RAIL_15_HI
assert RAIL_30_LO < RAIL_30_TARGET < RAIL_30_HI
assert RAIL_60_LO < RAIL_60_TARGET < RAIL_60_HI
assert HP_80HOP_LO < ATOM11_TARGET_80 < HP_80HOP_HI
assert HP_100HOP_LO < ATOM11_TARGET_100 < HP_100HOP_HI
assert HF_MECHANISM_DEATH_80 < HP_80HOP_LO
assert HF_LAW_BREAKS_80_DEVIATION > ATOM11_TOL_HP  # HF band wider than HP band
assert 0.0 < PHASE_CV_MAX <= 0.20
assert 0.0 < ATOM11_PER_STEP < 1.0

# Cell config (mirror prior d45-60 v1 for rail reproduction)
V_CONCEPTS = 200
V_PRED = 10
K_SET = 20
N_CHAINS = 200
N_PARTITIONS = 20

# Phase point depths
DEPTHS = [15, 30, 60, 80, 100]
MAX_DEPTH = 100

assert V_CONCEPTS % N_PARTITIONS == 0
PART_SIZE = V_CONCEPTS // N_PARTITIONS  # 10

# Regimes for the FIVE Ws
D15_REGIME_MAX_DEPTH = 15   # W_d15: 200*15 = 3000 bindings
D30_REGIME_MAX_DEPTH = 30   # W_d30: 200*30 = 6000 bindings
D60_REGIME_MAX_DEPTH = 60   # W_d60: 200*60 = 12000 bindings
D80_REGIME_MAX_DEPTH = 80   # W_d80: 200*80 = 16000 bindings
D100_REGIME_MAX_DEPTH = 100 # W_d100: 200*100 = 20000 bindings

# CARDINALITY: 5 arms x 3 seeds = 15 unit measurements
CARDINALITY_OK = True
EXPECTED_N_UNITS = 3  # seeds

if RUN_MODE == "smoke":
    # DISCRIMINATOR-MUST-SURVIVE-SCALE path A: smoke at FULL-N=8192
    N_DIM = 8192
    SEEDS = [7]
    N_CHAINS_LOCAL = 25       # 25 chains for smoke wall < 120s at full-N
else:
    N_DIM = 8192
    SEEDS = [7, 13, 19]       # matching d45-60 for cross-cell rail reproducibility
    N_CHAINS_LOCAL = N_CHAINS  # 200

ENCODER_PROVENANCE = "SUBSTRATE_NATIVE"

CONFIG_VERSION = (
    "multihopReasoningExtendedDepth80100V1: N=%d V_C=%d V_P=%d K=%d N_PARTS=%d "
    "PART_SIZE=%d depths=%s max_depth=%d n_chains=%d "
    "W_d15=%d W_d30=%d W_d60=%d W_d80=%d W_d100=%d "
    "seeds=%s mode=%s encoder=%s "
    "rail_15=[%.3f,%.3f] rail_30=[%.3f,%.3f] rail_60=[%.3f,%.3f] "
    "atom11_per_step=%.4f atom11_tgt80=%.3f atom11_tgt100=%.3f "
    "HP_tol=%.2f HF_tol=%.2f HF_death80=%.2f "
    "phase_cv_max=%.2f crlb_floor=%.3f"
) % (
    N_DIM, V_CONCEPTS, V_PRED, K_SET, N_PARTITIONS, PART_SIZE,
    DEPTHS, MAX_DEPTH, N_CHAINS_LOCAL,
    D15_REGIME_MAX_DEPTH, D30_REGIME_MAX_DEPTH,
    D60_REGIME_MAX_DEPTH, D80_REGIME_MAX_DEPTH, D100_REGIME_MAX_DEPTH,
    SEEDS, RUN_MODE, ENCODER_PROVENANCE,
    RAIL_15_LO, RAIL_15_HI, RAIL_30_LO, RAIL_30_HI, RAIL_60_LO, RAIL_60_HI,
    ATOM11_PER_STEP, ATOM11_TARGET_80, ATOM11_TARGET_100,
    ATOM11_TOL_HP, ATOM11_TOL_LAW_BREAKS, HF_MECHANISM_DEATH_80,
    PHASE_CV_MAX, CRLB_FLOOR_COMPUTED,
)


# ----------------------------------------------------------------------------
# Primitives (GPU-native; VERBATIM port from d45-60 v1)
# ----------------------------------------------------------------------------

def bipolar_gpu(M: int, n: int, g: np.random.Generator) -> torch.Tensor:
    """Bipolar bit vectors on GPU; row-normalized."""
    arr = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    t = torch.from_numpy(arr).to(DEVICE)
    norms = t.norm(dim=1, keepdim=True).clamp(min=1e-8)
    return t / norms


def make_deep_chains(n_chains: int, V: int, P: int, max_depth: int,
                      g: np.random.Generator,
                      disallow_s: set) -> Tuple[List[Tuple[int, int, int]],
                                                  List[List[Tuple[int, int, int]]]]:
    """VERBATIM port of depth-extension v1's make_deep_chains."""
    all_triples = []
    chain_queries = []
    used_s = set(disallow_s)
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
        raise RuntimeError("make_deep_chains: only %d/%d at max_depth=%d"
                            % (len(chain_queries), n_chains, max_depth))
    return all_triples, chain_queries


def ingest_hebbian_gpu(triples: List[Tuple[int, int, int]],
                        E: torch.Tensor, R: torch.Tensor,
                        sq: float, n_dim: int,
                        batch: int = 1000) -> torch.Tensor:
    """Batched outer-product Hebbian ingest on GPU. VERBATIM port."""
    W = torch.zeros((n_dim, n_dim), dtype=torch.float32, device=DEVICE)
    if not triples:
        return W
    tr = np.asarray(triples, dtype=np.int64)
    s_idx = torch.from_numpy(tr[:, 0]).to(DEVICE)
    p_idx = torch.from_numpy(tr[:, 1]).to(DEVICE)
    o_idx = torch.from_numpy(tr[:, 2]).to(DEVICE)
    n_total = len(tr)
    for b in range(0, n_total, batch):
        e = min(b + batch, n_total)
        s_slice = s_idx[b:e]
        p_slice = p_idx[b:e]
        o_slice = o_idx[b:e]
        K = E[s_slice] * R[p_slice] * sq  # (B, N)
        V_ = E[o_slice]                    # (B, N)
        W = W + (V_.T @ K) / n_dim
    return W


def arm_part_oracle_at_depth(E: torch.Tensor, R: torch.Tensor, sq: float,
                               W: torch.Tensor,
                               chains_test: List[List[Tuple[int, int, int]]],
                               depth: int,
                               part_size: int) -> Dict[str, Any]:
    """Partition-oracle routed cleanup at given depth. VERBATIM port."""
    n = len(chains_test)
    hits = 0
    per_step_hits = np.zeros(depth, dtype=np.int64)
    n_partitions = E.shape[0] // part_size
    E_parts = [E[p * part_size:(p + 1) * part_size] for p in range(n_partitions)]
    for chain in chains_test:
        s = chain[0][0]
        for i in range(depth):
            p = chain[i][1]
            target_o = chain[i][2]
            target_part = target_o // part_size
            key = E[s] * R[p] * sq
            state = W @ key
            scores = E_parts[target_part] @ state
            local_idx = int(torch.argmax(scores).item())
            s_pred = target_part * part_size + local_idx
            if s_pred == target_o:
                per_step_hits[i] += 1
            s = s_pred
        if s == chain[depth - 1][2]:
            hits += 1
    per_step_acc = (per_step_hits.astype(np.float32) / max(n, 1)).tolist()
    return {"top1": round(hits / max(n, 1), 4),
            "per_step_acc": [round(x, 4) for x in per_step_acc],
            "n_queries": n, "depth": depth, "n_partitions": n_partitions,
            "part_size": part_size,
            "mechanism": "partition_oracle_per_hop_gpu"}


# ----------------------------------------------------------------------------
# Self-test (formula sanity check on tiny config)
# ----------------------------------------------------------------------------

def _selftest() -> None:
    g = np.random.default_rng(0)
    n = 512
    # V must exceed max_depth+1 so make_deep_chains can pick distinct nodes;
    # V=112 supports max_depth=100 with headroom (nodes list holds 101).
    V = 112
    P = 4
    sq = math.sqrt(n)
    E = bipolar_gpu(V, n, g)
    R = bipolar_gpu(P, n, g)

    # T1: bipolar shapes + norm
    assert E.shape == (V, n) and R.shape == (P, n)
    assert abs(float(E[0].norm()) - 1.0) < 1e-4

    # T2: chain construction at all five depths
    for max_d in [15, 30, 60, 80, 100]:
        triples, chains = make_deep_chains(4, V, P, max_depth=max_d, g=g,
                                              disallow_s=set())
        assert len(chains) == 4 and len(triples) == 4 * max_d

    # T3: ingest tiny config (build W_d100 covers all shorter depths via prefix)
    triples100, chains100 = make_deep_chains(4, V, P, max_depth=100, g=g,
                                                disallow_s=set())
    W100 = ingest_hebbian_gpu(triples100, E, R, sq, n)
    assert W100.shape == (n, n)
    assert torch.isfinite(W100).all()

    # T4: part_oracle at each depth on tiny config
    # V=112 divisible by n_parts_test=8 -> part_sz_test=14 (self-test only)
    n_parts_test = 8
    assert V % n_parts_test == 0
    part_sz_test = V // n_parts_test

    for depth_test in [15, 30, 60, 80, 100]:
        r = arm_part_oracle_at_depth(E, R, sq, W100,
                                       [c[:depth_test] for c in chains100],
                                       depth=depth_test, part_size=part_sz_test)
        assert 0.0 <= r["top1"] <= 1.0
        assert len(r["per_step_acc"]) == depth_test

    # T5: bands LOCKED (regression on accidental band drift)
    assert RAIL_15_LO == 0.758 and RAIL_15_HI == 0.858
    assert RAIL_30_LO == 0.587 and RAIL_30_HI == 0.687
    assert RAIL_60_LO == 0.430 and RAIL_60_HI == 0.530
    assert math.isclose(HP_80HOP_LO, 0.203, abs_tol=1e-6)
    assert math.isclose(HP_80HOP_HI, 0.403, abs_tol=1e-6)
    assert math.isclose(HP_100HOP_LO, 0.122, abs_tol=1e-6)
    assert math.isclose(HP_100HOP_HI, 0.322, abs_tol=1e-6)
    assert HF_MECHANISM_DEATH_80 == 0.10
    assert ATOM11_PER_STEP == 0.9853

    # T6: Atom 11 formula sanity (compute in code per META_RULE)
    computed_80 = ATOM11_PER_STEP ** 80
    computed_100 = ATOM11_PER_STEP ** 100
    computed_155 = ATOM11_PER_STEP ** 155
    # Target 0.303 approximates computed 0.3058 (0.01 rounding slack for pinned
    # target vs formula); target 0.222 approximates 0.2274.
    assert abs(computed_80 - ATOM11_TARGET_80) < 0.01, (computed_80, ATOM11_TARGET_80)
    assert abs(computed_100 - ATOM11_TARGET_100) < 0.01, (computed_100, ATOM11_TARGET_100)
    # d=155 should hit death floor 0.10 within 0.02 tolerance (Atom 11 pin)
    assert abs(computed_155 - 0.10) < 0.02, computed_155

    # T7: CRLB reachability
    assert CRLB_FLOOR_COMPUTED == 0.10
    assert DISCRIMINATOR_REACHABILITY is True
    # HP_80 reachable iff per-step in ~[0.980, 0.989]
    per_step_lo = HP_80HOP_LO ** (1.0 / 80.0)  # ~0.9800
    per_step_hi = HP_80HOP_HI ** (1.0 / 80.0)  # ~0.9887
    assert 0.978 < per_step_lo < 0.981, per_step_lo
    assert 0.988 < per_step_hi < 0.990, per_step_hi

    # T8: LLM call counter = 0 (substrate-only)
    assert _LLM_CALL_COUNTER[0] == 0

    # T9: GPU presence asserted for non-smoke mode (smoke OK on CPU)
    if RUN_MODE != "smoke":
        assert GPU_AVAIL, "FULL run requires GPU per Fix #24"

    # T10: CARDINALITY_OK pre-reg field
    assert CARDINALITY_OK is True
    assert EXPECTED_N_UNITS == 3
    if RUN_MODE != "smoke":
        assert len(SEEDS) == EXPECTED_N_UNITS

    # T11: smoke uses full-N (DISCRIMINATOR-MUST-SURVIVE-SCALE path A)
    if RUN_MODE == "smoke":
        assert N_DIM == 8192, "smoke must use full-N per DISCRIMINATOR discipline"

    print("[selftest] PASS depths=[15,30,60,80,100] gpu=%s bands_locked=True "
          "atom11_80=%.4f atom11_100=%.4f atom11_155=%.4f "
          "hp80_per_step=[%.4f,%.4f] crlb=%.3f"
          % (GPU_AVAIL, computed_80, computed_100, computed_155,
             per_step_lo, per_step_hi, CRLB_FLOOR_COMPUTED),
          flush=True)


_selftest()
if _ARGS.self_test:
    print("[self-test] PASS; exiting", flush=True)
    sys.exit(0)


# ----------------------------------------------------------------------------
# Defensive error-checking helpers
# ----------------------------------------------------------------------------

def _write_start_marker(output_dir: Path, anchor_name: str, run_mode: str,
                          expected_n_units: int) -> None:
    marker = {
        "pid": os.getpid(),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": anchor_name,
        "run_mode": run_mode,
        "expected_n_units": expected_n_units,
        "host": platform.node(),
    }
    os.makedirs(output_dir, exist_ok=True)
    tmp = output_dir / "_start_marker.json.tmp"
    final = output_dir / "_start_marker.json"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir: Path, anchor_name: str, exc: Exception) -> None:
    diag = {
        "verdict": "CELL_CRASHED",
        "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:500]),
        "summary": "CELL_CRASHED: %s" % type(exc).__name__,
        "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "anchor_name": anchor_name,
    }
    os.makedirs(output_dir, exist_ok=True)
    tmp_path = output_dir / "metrics.json.tmp"
    final_path = output_dir / "metrics.json"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp_path, final_path)


# ----------------------------------------------------------------------------
# run_seed
# ----------------------------------------------------------------------------

def run_seed(seed: int) -> Dict[str, Any]:
    t = time.time()
    g = np.random.default_rng(seed)
    sq = math.sqrt(N_DIM)

    if GPU_AVAIL:
        torch.cuda.reset_peak_memory_stats(DEVICE)

    print("  [seed=%d] building E (V_C=%d, N=%d)" % (
        seed, V_CONCEPTS, N_DIM), flush=True)
    E = bipolar_gpu(V_CONCEPTS, N_DIM, g)
    R = bipolar_gpu(V_PRED, N_DIM, g)

    out = {
        "seed": seed, "run_mode": RUN_MODE, "N": N_DIM, "V_C": V_CONCEPTS,
        "V_P": V_PRED, "K_set": K_SET, "n_partitions": N_PARTITIONS,
        "part_size": PART_SIZE,
        "encoder_provenance": ENCODER_PROVENANCE,
        "n_chains": N_CHAINS_LOCAL, "depths": DEPTHS,
        "config_version": CONFIG_VERSION,
        "gpu_avail": GPU_AVAIL,
        "gpu_name": GPU_NAME,
        "_llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
    }

    # Build all five Ws.  One W per max-depth regime.
    Ws = {}
    for label, depth_max in [("d15", D15_REGIME_MAX_DEPTH),
                              ("d30", D30_REGIME_MAX_DEPTH),
                              ("d60", D60_REGIME_MAX_DEPTH),
                              ("d80", D80_REGIME_MAX_DEPTH),
                              ("d100", D100_REGIME_MAX_DEPTH)]:
        t_arm = time.time()
        triples, chains = make_deep_chains(
            N_CHAINS_LOCAL, V_CONCEPTS, V_PRED, max_depth=depth_max,
            g=g, disallow_s=set())
        W = ingest_hebbian_gpu(triples, E, R, sq, N_DIM)
        Ws[label] = (W, triples, chains, depth_max)
        print("  [seed=%d] W_%s built (%d triples, max_depth=%d) t=%.1fs" % (
            seed, label, len(triples), depth_max,
            round(time.time() - t_arm, 2)), flush=True)

    # ===== ARM_PART_ORACLE_15HOP (rail: reproduce prior 0.808) =====
    t_arm = time.time()
    W_d15, _, chains_d15, _ = Ws["d15"]
    r_part15 = arm_part_oracle_at_depth(E, R, sq, W_d15, chains_d15, depth=15,
                                          part_size=PART_SIZE)
    r_part15["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    r_part15["W_n_bindings"] = len(Ws["d15"][1])
    r_part15["W_regime"] = "d15_max_depth_15"
    out["arm_part_oracle_15hop"] = r_part15
    rail_15_ok = (RAIL_15_LO <= r_part15["top1"] <= RAIL_15_HI)
    out["rail_15_ok"] = rail_15_ok
    print("  [seed=%d] PART_ORACLE_15HOP top1=%.4f "
          "(rail_ok=%s; band=[%.3f,%.3f]; target=%.4f) t=%.1fs" % (
              seed, r_part15["top1"],
              rail_15_ok, RAIL_15_LO, RAIL_15_HI, RAIL_15_TARGET,
              r_part15["elapsed_s_arm"]), flush=True)

    # ===== ARM_PART_ORACLE_30HOP (rail: reproduce prior 0.637) =====
    t_arm = time.time()
    W_d30, _, chains_d30, _ = Ws["d30"]
    r_part30 = arm_part_oracle_at_depth(E, R, sq, W_d30, chains_d30, depth=30,
                                          part_size=PART_SIZE)
    r_part30["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    r_part30["W_n_bindings"] = len(Ws["d30"][1])
    r_part30["W_regime"] = "d30_max_depth_30"
    out["arm_part_oracle_30hop"] = r_part30
    rail_30_ok = (RAIL_30_LO <= r_part30["top1"] <= RAIL_30_HI)
    out["rail_30_ok"] = rail_30_ok
    print("  [seed=%d] PART_ORACLE_30HOP top1=%.4f "
          "(rail_ok=%s; band=[%.3f,%.3f]; target=%.4f) t=%.1fs" % (
              seed, r_part30["top1"],
              rail_30_ok, RAIL_30_LO, RAIL_30_HI, RAIL_30_TARGET,
              r_part30["elapsed_s_arm"]), flush=True)

    # ===== ARM_PART_ORACLE_60HOP (rail: reproduce Landing 10 0.480) =====
    t_arm = time.time()
    W_d60, _, chains_d60, _ = Ws["d60"]
    r_part60 = arm_part_oracle_at_depth(E, R, sq, W_d60, chains_d60, depth=60,
                                          part_size=PART_SIZE)
    r_part60["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    r_part60["W_n_bindings"] = len(Ws["d60"][1])
    r_part60["W_regime"] = "d60_max_depth_60"
    out["arm_part_oracle_60hop"] = r_part60
    rail_60_ok = (RAIL_60_LO <= r_part60["top1"] <= RAIL_60_HI)
    out["rail_60_ok"] = rail_60_ok
    print("  [seed=%d] PART_ORACLE_60HOP top1=%.4f "
          "(rail_ok=%s; band=[%.3f,%.3f]; target=%.4f) t=%.1fs" % (
              seed, r_part60["top1"],
              rail_60_ok, RAIL_60_LO, RAIL_60_HI, RAIL_60_TARGET,
              r_part60["elapsed_s_arm"]), flush=True)

    # ===== ARM_PART_ORACLE_80HOP (NEW Atom 11 test phase point) =====
    t_arm = time.time()
    W_d80, _, chains_d80, _ = Ws["d80"]
    r_part80 = arm_part_oracle_at_depth(E, R, sq, W_d80, chains_d80, depth=80,
                                          part_size=PART_SIZE)
    r_part80["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    r_part80["W_n_bindings"] = len(Ws["d80"][1])
    r_part80["W_regime"] = "d80_max_depth_80"
    r_part80["atom11_target"] = ATOM11_TARGET_80
    r_part80["atom11_deviation"] = abs(r_part80["top1"] - ATOM11_TARGET_80)
    r_part80["atom11_hp_ok"] = r_part80["atom11_deviation"] <= ATOM11_TOL_HP
    r_part80["atom11_hf_law_breaks"] = r_part80["atom11_deviation"] > ATOM11_TOL_LAW_BREAKS
    r_part80["hf_mechanism_death"] = r_part80["top1"] < HF_MECHANISM_DEATH_80
    out["arm_part_oracle_80hop"] = r_part80
    print("  [seed=%d] PART_ORACLE_80HOP top1=%.4f "
          "(atom11_tgt=%.3f dev=%.3f hp_ok=%s law_breaks=%s death=%s) t=%.1fs" % (
              seed, r_part80["top1"], ATOM11_TARGET_80,
              r_part80["atom11_deviation"], r_part80["atom11_hp_ok"],
              r_part80["atom11_hf_law_breaks"], r_part80["hf_mechanism_death"],
              r_part80["elapsed_s_arm"]), flush=True)

    # ===== ARM_PART_ORACLE_100HOP (NEW Atom 11 test phase point) =====
    t_arm = time.time()
    W_d100, _, chains_d100, _ = Ws["d100"]
    r_part100 = arm_part_oracle_at_depth(E, R, sq, W_d100, chains_d100, depth=100,
                                           part_size=PART_SIZE)
    r_part100["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    r_part100["W_n_bindings"] = len(Ws["d100"][1])
    r_part100["W_regime"] = "d100_max_depth_100"
    r_part100["atom11_target"] = ATOM11_TARGET_100
    r_part100["atom11_deviation"] = abs(r_part100["top1"] - ATOM11_TARGET_100)
    r_part100["atom11_hp_ok"] = r_part100["atom11_deviation"] <= ATOM11_TOL_HP
    r_part100["atom11_hf_law_breaks"] = r_part100["atom11_deviation"] > ATOM11_TOL_LAW_BREAKS
    out["arm_part_oracle_100hop"] = r_part100
    print("  [seed=%d] PART_ORACLE_100HOP top1=%.4f "
          "(atom11_tgt=%.3f dev=%.3f hp_ok=%s law_breaks=%s) t=%.1fs" % (
              seed, r_part100["top1"], ATOM11_TARGET_100,
              r_part100["atom11_deviation"], r_part100["atom11_hp_ok"],
              r_part100["atom11_hf_law_breaks"],
              r_part100["elapsed_s_arm"]), flush=True)

    # GPU mem peak
    if GPU_AVAIL:
        peak_bytes = torch.cuda.max_memory_allocated(DEVICE)
        out["gpu_max_mem_alloc_mb"] = round(peak_bytes / 1e6, 2)
        print("  [seed=%d] GPU peak alloc: %.2f MB" % (
            seed, out["gpu_max_mem_alloc_mb"]), flush=True)
        for label in list(Ws.keys()):
            del Ws[label]
        torch.cuda.empty_cache()
    else:
        out["gpu_max_mem_alloc_mb"] = 0.0

    out["elapsed_s"] = round(time.time() - t, 1)
    return out


# ----------------------------------------------------------------------------
# Verdict
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

    part15 = mean_top1("arm_part_oracle_15hop")
    part30 = mean_top1("arm_part_oracle_30hop")
    part60 = mean_top1("arm_part_oracle_60hop")
    part80 = mean_top1("arm_part_oracle_80hop")
    part100 = mean_top1("arm_part_oracle_100hop")

    cv15 = cv_top1("arm_part_oracle_15hop")
    cv30 = cv_top1("arm_part_oracle_30hop")
    cv60 = cv_top1("arm_part_oracle_60hop")
    cv80 = cv_top1("arm_part_oracle_80hop")
    cv100 = cv_top1("arm_part_oracle_100hop")

    rail_15_breach = sum(1 for p in per_seed if not p.get("rail_15_ok", False))
    rail_30_breach = sum(1 for p in per_seed if not p.get("rail_30_ok", False))
    rail_60_breach = sum(1 for p in per_seed if not p.get("rail_60_ok", False))
    n = len(per_seed)
    half = max(1, (n + 1) // 2)

    # Atom 11 deviation checks (using cross-seed means)
    dev_80 = abs(part80 - ATOM11_TARGET_80) if not math.isnan(part80) else float("nan")
    dev_100 = abs(part100 - ATOM11_TARGET_100) if not math.isnan(part100) else float("nan")
    d80_hp_ok = (not math.isnan(dev_80)) and dev_80 <= ATOM11_TOL_HP
    d100_hp_ok = (not math.isnan(dev_100)) and dev_100 <= ATOM11_TOL_HP
    d80_law_breaks = (not math.isnan(dev_80)) and dev_80 > ATOM11_TOL_LAW_BREAKS
    d100_law_breaks = (not math.isnan(dev_100)) and dev_100 > ATOM11_TOL_LAW_BREAKS
    d80_death = (not math.isnan(part80)) and part80 < HF_MECHANISM_DEATH_80

    # Informational atom11 verdict
    if d80_death:
        atom11_verdict = "EARLY_DEATH"
    elif d80_hp_ok and d100_hp_ok:
        atom11_verdict = "CG_LIFT_C"
    elif d80_hp_ok and not d100_hp_ok:
        atom11_verdict = "PARTIAL_80_ONLY"
    elif d100_hp_ok and not d80_hp_ok:
        atom11_verdict = "PARTIAL_100_ONLY"
    elif d80_law_breaks or d100_law_breaks:
        atom11_verdict = "LAW_BREAKS"
    else:
        atom11_verdict = "unknown"

    summ = (
        "PART_15HOP=%.4f (cv=%.3f, rail15_breach=%d/%d; target=%.4f) "
        "PART_30HOP=%.4f (cv=%.3f, rail30_breach=%d/%d; target=%.4f) "
        "PART_60HOP=%.4f (cv=%.3f, rail60_breach=%d/%d; target=%.4f) "
        "PART_80HOP=%.4f (cv=%.3f; atom11_tgt=%.3f dev=%.3f hp_ok=%s) "
        "PART_100HOP=%.4f (cv=%.3f; atom11_tgt=%.3f dev=%.3f hp_ok=%s) "
        "atom11_verdict=%s"
    ) % (
        part15, cv15, rail_15_breach, n, RAIL_15_TARGET,
        part30, cv30, rail_30_breach, n, RAIL_30_TARGET,
        part60, cv60, rail_60_breach, n, RAIL_60_TARGET,
        part80, cv80, ATOM11_TARGET_80, dev_80, d80_hp_ok,
        part100, cv100, ATOM11_TARGET_100, dev_100, d100_hp_ok,
        atom11_verdict,
    )

    # Sanity pre-emption: any rail breach majority (skip in smoke)
    if RUN_MODE != "smoke":
        if rail_15_breach >= half:
            return "RAIL_BREACH", "RAIL_BREACH_15HOP_OUT_OF_BAND: " + summ
        if rail_30_breach >= half:
            return "RAIL_BREACH", "RAIL_BREACH_30HOP_OUT_OF_BAND: " + summ
        if rail_60_breach >= half:
            return "RAIL_BREACH", "RAIL_BREACH_60HOP_OUT_OF_BAND: " + summ

    # Smoke mode: PASS if mechanism end-to-end operates at all depths
    if RUN_MODE == "smoke":
        vals = [part15, part30, part60, part80, part100]
        # DISCRIMINATOR-MUST-SURVIVE-SCALE: smoke fires Atom 11 discriminator
        # even at 25 chains (10% of full n_chains); if mechanism operates but
        # atom11 verdict is unknown/LAW_BREAKS at N=8192, that IS the signal.
        any_mech_ok = all(not math.isnan(v) and v >= CRLB_FLOOR_COMPUTED
                          for v in vals)
        if any_mech_ok:
            return ("SMOKE_PASS",
                    "SMOKE_PASS: mechanism end-to-end OK at full-N=8192 smoke "
                    "(25 chains); part80=%.4f part100=%.4f "
                    "atom11_verdict=%s | %s" % (
                        part80, part100, atom11_verdict, summ))
        return ("HARD_FAIL",
                "SMOKE_FAIL: mechanism at or below CRLB floor %.2f at full-N | %s" %
                (CRLB_FLOOR_COMPUTED, summ))

    # Novel extreme-depth classification (rails all pass)
    def cv_ok(cv_val: float) -> bool:
        return math.isnan(cv_val) or cv_val <= PHASE_CV_MAX

    if math.isnan(part80) or math.isnan(part100):
        return ("MIDDLE_BAND",
                "PART_80_OR_100_MISSING_METRIC | " + summ)

    # Mechanism-death first (d80 < HF)
    if d80_death:
        return ("MECHANISM_DEATH_EARLIER_THAN_155",
                "MECHANISM_DEATH_CLIFF_BEFORE_D80_ATOM11_PREDICTED_D155 "
                "(mechanism cliff below HF=%.2f): %s" % (
                    HF_MECHANISM_DEATH_80, summ))

    # Both HP pass + cv OK -> CG lift on Atom 11 criterion (c)
    if d80_hp_ok and d100_hp_ok and cv_ok(cv80) and cv_ok(cv100):
        return ("CHAIN_GRADE_LAW_EXTENDS_TO_EXTREME_DEPTH",
                "CHAIN_GRADE_ATOM11_LAW_EXTENDS_D80_AND_D100 "
                "(CG-lift on Atom 11 criterion c; envelope extends 67%% beyond "
                "d=60 Landing 10 CG; atom11_verdict=%s): %s" % (
                    atom11_verdict, summ))

    # One HP passes, one fails outside HP band but within HF band
    if d80_hp_ok and not d100_hp_ok and not d100_law_breaks and cv_ok(cv80):
        return ("PARTIAL_LAW_EXTENDS",
                "PARTIAL_ATOM11_EXTENDS_D80_ONLY_D100_WEAKENS "
                "(mechanism weakens between d=80 and d=100; atom11_verdict=%s): %s" % (
                    atom11_verdict, summ))
    if d100_hp_ok and not d80_hp_ok and not d80_law_breaks and cv_ok(cv100):
        return ("PARTIAL_LAW_EXTENDS",
                "PARTIAL_ATOM11_EXTENDS_D100_ONLY_D80_ANOMALY "
                "(non-monotonic; atom11_verdict=%s): %s" % (
                    atom11_verdict, summ))

    # Either HP fails outside law-breaks band -> Atom 11 does NOT extend
    if d80_law_breaks or d100_law_breaks:
        return ("LAW_BREAKS_AT_EXTREME_DEPTH",
                "ATOM11_LAW_DOES_NOT_EXTEND_TO_EXTREME_DEPTH "
                "(d80 law_breaks=%s d100 law_breaks=%s; atom11_verdict=%s): %s" % (
                    d80_law_breaks, d100_law_breaks, atom11_verdict, summ))

    return ("MIDDLE_BAND",
            "MIDDLE_BAND_PARTIAL_PASS_OR_CV_BREACH atom11_verdict=%s | %s" % (
                atom11_verdict, summ))


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
            "gpu_avail": GPU_AVAIL,
            "gpu_name": GPU_NAME,
        }
        write_metrics(od, metrics, results=per_seed)
        print("[atexit] wrote synth metrics.json (%d seeds)" % len(per_seed),
              flush=True)
    except Exception as e:
        print("[atexit] FAIL: %s" % e, flush=True)


atexit.register(_atexit_synth)


def main() -> None:
    print("[config] anchor=%s mode=%s seeds=%s N=%d gpu=%s | %s" % (
        ANCHOR_NAME, RUN_MODE, SEEDS, N_DIM, GPU_AVAIL, CONFIG_VERSION),
        flush=True)
    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)
    _RESULTS_HOLDER["out_dir"] = out_dir

    # Start-marker (defensive: proves cell was invoked)
    _write_start_marker(out_dir, ANCHOR_NAME, RUN_MODE,
                          expected_n_units=len(SEEDS))

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
        "gpu_avail": GPU_AVAIL,
        "gpu_name": GPU_NAME,
        "cardinality_ok": CARDINALITY_OK,
        "expected_n_units": EXPECTED_N_UNITS,
        "crlb_floor_computed": CRLB_FLOOR_COMPUTED,
        "crlb_formula": CRLB_FORMULA,
        "discriminator_reachability": DISCRIMINATOR_REACHABILITY,
        "discriminator_reach_note": DISCRIMINATOR_REACH_NOTE,
        "atom11_per_step": ATOM11_PER_STEP,
        "atom11_target_80": ATOM11_TARGET_80,
        "atom11_target_100": ATOM11_TARGET_100,
        "atom11_tol_hp": ATOM11_TOL_HP,
        "atom11_tol_law_breaks": ATOM11_TOL_LAW_BREAKS,
        "DESIGN_NOTE": (
            "MULTIHOP_REASONING_EXTENDED_DEPTH_80_100: Atom 11 (per-step "
            "scale-invariance in partition-oracle multihop) predicts per-step "
            "0.9853 -> d=80 -> 0.303; d=100 -> 0.222; d=155 -> 0.10 (death "
            "floor). This cell tests Atom 11 expansion criterion (c) at extreme "
            "depth. Rails d=15/30/60 reproduce prior CG at 0.808/0.637/0.480. "
            "HP gates: |PART_80 - 0.303| <= 0.10 AND |PART_100 - 0.222| <= "
            "0.10. Verdict tiers: CHAIN_GRADE_LAW_EXTENDS_TO_EXTREME_DEPTH "
            "(CG-lift criterion c) / PARTIAL_LAW_EXTENDS (one HP passes) / "
            "LAW_BREAKS_AT_EXTREME_DEPTH (Atom 11 fails at extreme depth, "
            "substantive negative) / MECHANISM_DEATH_EARLIER_THAN_155 (early "
            "cliff, substantive negative)."
        ),
    }
    write_metrics(out_dir, metrics, results=per_seed)
    print("[done] metrics.json written (%d seeds, %.1fs)" % (
        len(per_seed), metrics["elapsed_s"]), flush=True)


if __name__ == "__main__":
    _OUT_DIR_FOR_CRASH = get_output_dir(ANCHOR_NAME)
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(_OUT_DIR_FOR_CRASH, ANCHOR_NAME, e)
        raise
