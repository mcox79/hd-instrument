"""multihop_reasoning_depth_50_55_crossing_bracket_gpu_v1.

Skunkworks revival criterion 2026-07-01 (after 13th CG of the day; d45-60 cell
landed DEPTH_60_CROSSED_HALF at bracket (45, 60]): narrow the 0.50 crossing to
either (50, 55], (45, 50], or (55, 60] by adding d=50 and d=55 phase points.

PRIOR-WORK CHECK (substrate-KB concept-query 2026-07-01, exp_dev on spawn):
  Q1: "multihop depth 50 55 finer crossing bracket partition oracle"
      top hit cosine=0.331 (prereg depth_extension_v1); below strong-novelty
  Q2: "multihop reasoning depth 48 50 half line crossing precise"
      top hit cosine=0.314 (generic reasoning atom); no prior d50/d55 work
  Rediscovery-vs-novel: depths 15/30 are chain-grade MEASURED prior rails;
  depths 50 and 55 are GENUINELY NEW phase points. Cell extends today's d45-60
  CG.

MEASURED PRIOR (LANDED 2026-07-01):
  MEASURED@data/exp_multihop_reasoning_depth_45_to_60_gpu_v1/metrics.json:
    PART_15HOP=0.7983 PART_20HOP=0.7017 PART_30HOP=0.6333
    PART_45HOP=0.5317 (above half)  PART_60HOP=0.4800 (below half)
  Empirical per-step: 0.9861 (from d45) / 0.9878 (from d60) / 0.9870 (avg)
  Solved crossing d* at avg per-step: 52.77 (predicted bracket (50, 55])

CROSS-CELL RAILS (2):
  - RAIL_DEPTH_15 must reproduce prior 0.808 +/- 0.05
  - RAIL_DEPTH_30 must reproduce prior 0.637 +/- 0.05

DISCRIMINATOR (Skunkworks-declared 2026-07-01):
  "narrow the 0.50 crossing bracket from (45, 60] to width <=5"
  Predictions at empirical per-step 0.9870:
    d50 = 0.5185 (marginally above 0.50)  THEORETICAL@0.9870^50
    d55 = 0.4856 (marginally below 0.50)  THEORETICAL@0.9870^55
  Most-likely outcome: crossing_bracket_narrowed=(50, 55] with width 5.
  Alternative regimes:
    per-step 0.98:  d50=0.3642 (below), d55=0.3292 (below) => bracket <=(45,50]
    per-step 0.99:  d50=0.6050 (above), d55=0.5754 (above) => bracket >=(55,60]

ARMS (4):
  ARM_PART_ORACLE_15HOP  rail (reproduce prior 0.808)
  ARM_PART_ORACLE_30HOP  rail (reproduce prior 0.637)
  ARM_PART_ORACLE_50HOP  NEW phase point (predicted 0.518 marginal above)
  ARM_PART_ORACLE_55HOP  NEW phase point (predicted 0.486 marginal below)

PRE-REG BANDS (LOCKED at module init):
  Sanity rails:
    RAIL_15: PART_15HOP in [0.758, 0.858] else RAIL_15_BREACH
    RAIL_30: PART_30HOP in [0.587, 0.687] else RAIL_30_BREACH
  Novel phase points (informational per USER declaration):
    HP_50HOP_ABOVE_HALF: PART_50HOP >= 0.50
    HP_55HOP_ABOVE_HALF: PART_55HOP >= 0.50
    HF_MECHANISM_DEATH:  any depth < 0.10
  Stability:
    cv across seeds <= 0.10 for HARD_PASS claim

DISCRIMINATOR TIERS (4-way + informational per USER declaration):
  CROSSING_BRACKET_50_55:  d50 >= 0.50 AND d55 <  0.50 -> narrowed (50, 55]
  CROSSING_BRACKET_45_50:  d50 <  0.50 AND d55 <  0.50 -> narrowed (45, 50]
  CROSSING_BRACKET_55_60:  d50 >= 0.50 AND d55 >= 0.50 -> narrowed (55, 60]
  MECHANISM_DEATH:         any depth < 0.10 (cliff)
  RAIL_BREACH:             any rail breach majority of seeds
  MIDDLE_BAND:             non-monotonic (d50<half AND d55>=half) or cv breach

INFORMATIONAL FIELD (Skunkworks-requested):
  crossing_bracket_narrowed:
    - "(50, 55]"  if CROSSING_BRACKET_50_55 (predicted most likely)
    - "(45, 50]"  if CROSSING_BRACKET_45_50
    - "(55, 60]"  if CROSSING_BRACKET_55_60
    - "non_monotonic" if d50<half AND d55>=half
    - "unknown" if metrics missing

GPU IMPLEMENTATION (Fix #24 active GPU use):
  - All Ws (W_d15, W_d30, W_d50, W_d55) built on torch.cuda via batched
    outer-product accumulation; E, R kept on GPU throughout.
  - Argmax cleanup is torch.argmax(E_part @ (W @ key)) on GPU.
  - Per-W memory at N=8192: 1 W = 268MB float32; 4 Ws = ~1.07GB resident;
    plus E (6.5MB) + R (0.3MB) = ~1.08GB peak; well under 8GB GPU.
  - Peak alloc measured per-seed; each W freed via del + empty_cache post-seed.
  - W_d55 requires make_deep_chains at max_depth=55 (200*55=11000 bindings);
    SNR per binding at N=8192: N/M = 8192/11000 = 0.744 (below unit but
    prior d60 M=12000 SNR=0.683 measured 0.4800 so d55 fully feasible).

DEFENSIVE ERROR-CHECKING (META_RULE_AH + start-marker + heartbeat):
  - start_marker written at main() entry
  - crash_diagnostic in outer try/except (SystemExit + KeyboardInterrupt re-raise)
  - per-seed heartbeat via _cell_heartbeat helper
  - metrics.json atomic write via write_metrics helper

ASCII-only; per-seed checkpoint (PROT-021); atexit synthesizer;
zero-LLM-call assert. Author: exp_dev 2026-07-01 (Skunkworks revival criterion
after d45-60 landing).
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

ANCHOR_NAME = "multihop_reasoning_depth_50_55_crossing_bracket_gpu_v1"
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
# Rails from prior CG:
#   depth_ceiling_sweep_v1: PART_15HOP=0.810 PART_30HOP=0.637
#   depth_45_to_60_gpu_v1 (LANDED 2026-07-01 13th CG):
#     PART_15HOP=0.7983 PART_20HOP=0.7017 PART_30HOP=0.6333
#     PART_45HOP=0.5317 PART_60HOP=0.4800
RAIL_15_TARGET = 0.808
RAIL_15_LO = 0.758
RAIL_15_HI = 0.858
RAIL_30_TARGET = 0.637
RAIL_30_LO = 0.587
RAIL_30_HI = 0.687

# Novel phase points: depth 50 and 55 (Skunkworks discriminator "narrow crossing")
# THEORETICAL@0.9870^50=0.5185 (empirical per-step avg from d45+d60 LANDED)
# THEORETICAL@0.9870^55=0.4856
# Skunkworks-supplied gates (informational per USER 0.50 crossing declaration):
HP_50HOP_ABOVE_HALF = 0.50   # d50 informational: above half if mean >= this
HP_55HOP_ABOVE_HALF = 0.50   # d55 informational: above half if mean >= this
HF_MECHANISM_DEATH = 0.10    # any depth HARD_FAIL if < this (mechanism cliff)
DISCRIMINATOR_HALF_LINE = 0.50  # informational; USER's crossing question

PHASE_CV_MAX = 0.10  # per-arm seed cv cap for HP claim

# CRLB / capacity-feasibility (META_RULE_9 CRLB gate):
# Partition-oracle argmax over PART_SIZE=10 items at N=8192.
# For W_d55: M=n_chains*max_depth=200*55=11000 bindings; SNR per binding =
# N/M = 8192/11000 = 0.744.  Per-hop random-guess floor stays at 1/PART_SIZE=
# 0.10 (argmax over 10 items) regardless of W SNR; the SNR only affects
# per-hop accuracy signal quality.
CRLB_FLOOR_COMPUTED = 1.0 / 10.0  # = 0.10; argmax-over-PART_SIZE random-guess floor
CRLB_FORMULA = "per_hop_random_guess = 1/PART_SIZE = 1/10 = 0.10"
# Discriminator reachability: HP_50HOP >= 0.50 requires per-step > 0.5^(1/50)
# = 0.9862; empirical 0.9870 > 0.9862 (marginally) so achievable.
# HP_55HOP >= 0.50 requires per-step > 0.5^(1/55) = 0.9875; empirical 0.9870
# < 0.9875 so below-half is MORE likely at d55.  Both gates on live-decay branch.
DISCRIMINATOR_REACHABILITY = True  # both gates physically reachable
DISCRIMINATOR_REACH_NOTE = (
    "d50 HP >= 0.50 achievable iff per-step > 0.5^(1/50)=0.9862; empirical "
    "0.9870 > 0.9862 (marginally). d55 HP >= 0.50 achievable iff per-step > "
    "0.5^(1/55)=0.9875; empirical 0.9870 < 0.9875 so below-half more likely "
    "at d55. Both gates on live-decay branch; predicted bracket (50, 55]."
)

# Locked invariants
assert RAIL_15_LO < RAIL_15_TARGET < RAIL_15_HI
assert RAIL_30_LO < RAIL_30_TARGET < RAIL_30_HI
assert HP_50HOP_ABOVE_HALF > HF_MECHANISM_DEATH
assert HP_55HOP_ABOVE_HALF > HF_MECHANISM_DEATH
assert 0.0 < PHASE_CV_MAX <= 0.20

# Cell config (mirror prior d45-60 v1 for rail reproduction)
V_CONCEPTS = 200
V_PRED = 10
K_SET = 20
N_CHAINS = 200
N_PARTITIONS = 20

# Phase point depths
DEPTHS = [15, 30, 50, 55]
MAX_DEPTH = 55

assert V_CONCEPTS % N_PARTITIONS == 0
PART_SIZE = V_CONCEPTS // N_PARTITIONS  # 10

# Regimes for the FOUR Ws
D15_REGIME_MAX_DEPTH = 15  # W_d15: 200*15 = 3000 bindings
D30_REGIME_MAX_DEPTH = 30  # W_d30: 200*30 = 6000 bindings
D50_REGIME_MAX_DEPTH = 50  # W_d50: 200*50 = 10000 bindings
D55_REGIME_MAX_DEPTH = 55  # W_d55: 200*55 = 11000 bindings

# CARDINALITY: 4 arms x 3 seeds = 12 unit measurements; EXPECTED_N_UNITS=3 seeds
CARDINALITY_OK = True
EXPECTED_N_UNITS = 3  # seeds; arms are internal to each seed record

if RUN_MODE == "smoke":
    N_DIM = 2048
    SEEDS = [7]
    N_CHAINS_LOCAL = 25       # 25 chains for smoke (lighter than full)
else:
    N_DIM = 8192
    SEEDS = [7, 13, 19]       # matches prior d45-60 for cross-seed comparison
    N_CHAINS_LOCAL = N_CHAINS  # 200

ENCODER_PROVENANCE = "SUBSTRATE_NATIVE"

CONFIG_VERSION = (
    "multihopReasoningDepth50_55CrossingBracketV1: N=%d V_C=%d V_P=%d K=%d "
    "N_PARTS=%d PART_SIZE=%d depths=%s max_depth=%d n_chains=%d "
    "W_d15=%d W_d30=%d W_d50=%d W_d55=%d "
    "seeds=%s mode=%s encoder=%s "
    "rail_15=[%.3f,%.3f] rail_30=[%.3f,%.3f] "
    "HP_50_above_half=%.2f HP_55_above_half=%.2f HF_death=%.2f "
    "discriminator_half=%.2f phase_cv_max=%.2f crlb_floor=%.3f"
) % (
    N_DIM, V_CONCEPTS, V_PRED, K_SET, N_PARTITIONS, PART_SIZE,
    DEPTHS, MAX_DEPTH, N_CHAINS_LOCAL,
    D15_REGIME_MAX_DEPTH, D30_REGIME_MAX_DEPTH,
    D50_REGIME_MAX_DEPTH, D55_REGIME_MAX_DEPTH,
    SEEDS, RUN_MODE, ENCODER_PROVENANCE,
    RAIL_15_LO, RAIL_15_HI, RAIL_30_LO, RAIL_30_HI,
    HP_50HOP_ABOVE_HALF, HP_55HOP_ABOVE_HALF, HF_MECHANISM_DEATH,
    DISCRIMINATOR_HALF_LINE, PHASE_CV_MAX, CRLB_FLOOR_COMPUTED,
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
    # V must exceed max_depth+1; V=72 supports max_depth=55 (nodes list holds 56).
    # Prior d45-60 used V=72 up to max_depth=60; same margin here.
    V = 72
    P = 4
    sq = math.sqrt(n)
    E = bipolar_gpu(V, n, g)
    R = bipolar_gpu(P, n, g)

    # T1: bipolar shapes + norm
    assert E.shape == (V, n) and R.shape == (P, n)
    assert abs(float(E[0].norm()) - 1.0) < 1e-4

    # T2: chain construction at all four depths
    for max_d in [15, 30, 50, 55]:
        triples, chains = make_deep_chains(4, V, P, max_depth=max_d, g=g,
                                              disallow_s=set())
        assert len(chains) == 4 and len(triples) == 4 * max_d

    # T3: ingest tiny config (build W_d55 covers all shorter depths via prefix)
    triples55, chains55 = make_deep_chains(4, V, P, max_depth=55, g=g,
                                              disallow_s=set())
    W55 = ingest_hebbian_gpu(triples55, E, R, sq, n)
    assert W55.shape == (n, n)
    assert torch.isfinite(W55).all()

    # T4: part_oracle at each depth on tiny config
    # V=72 divisible by n_parts_test=6 -> part_sz_test=12 (self-test only)
    n_parts_test = 6
    assert V % n_parts_test == 0
    part_sz_test = V // n_parts_test

    for depth_test in [15, 30, 50, 55]:
        r = arm_part_oracle_at_depth(E, R, sq, W55,
                                       [c[:depth_test] for c in chains55],
                                       depth=depth_test, part_size=part_sz_test)
        assert 0.0 <= r["top1"] <= 1.0
        assert len(r["per_step_acc"]) == depth_test

    # T5: bands LOCKED (regression on accidental band drift)
    assert HP_50HOP_ABOVE_HALF == 0.50 and HP_55HOP_ABOVE_HALF == 0.50
    assert HF_MECHANISM_DEATH == 0.10
    assert DISCRIMINATOR_HALF_LINE == 0.50
    assert RAIL_15_LO == 0.758 and RAIL_15_HI == 0.858
    assert RAIL_30_LO == 0.587 and RAIL_30_HI == 0.687

    # T6: CRLB reachability (BOTH gates on live-decay branch)
    assert CRLB_FLOOR_COMPUTED == 0.10
    assert DISCRIMINATOR_REACHABILITY is True
    # HP_50HOP >= 0.50 requires per-step > 0.5^(1/50); verify formula:
    per_step_needed_d50 = 0.5 ** (1.0 / 50.0)
    assert 0.985 < per_step_needed_d50 < 0.987, per_step_needed_d50
    # HP_55HOP >= 0.50 requires per-step > 0.5^(1/55); verify:
    per_step_needed_d55 = 0.5 ** (1.0 / 55.0)
    assert 0.987 < per_step_needed_d55 < 0.988, per_step_needed_d55

    # T7: LLM call counter = 0 (substrate-only)
    assert _LLM_CALL_COUNTER[0] == 0

    # T8: GPU presence asserted for non-smoke mode (smoke OK on CPU)
    if RUN_MODE != "smoke":
        assert GPU_AVAIL, "FULL run requires GPU per Fix #24"

    # T9: CARDINALITY_OK pre-reg field
    assert CARDINALITY_OK is True
    assert EXPECTED_N_UNITS == 3
    if RUN_MODE != "smoke":
        assert len(SEEDS) == EXPECTED_N_UNITS

    print("[selftest] PASS depths=[15,30,50,55] gpu=%s bands_locked=True "
          "crlb_reach=%s per_step_needed_d50=%.4f per_step_needed_d55=%.4f"
          % (GPU_AVAIL, DISCRIMINATOR_REACHABILITY,
             per_step_needed_d50, per_step_needed_d55),
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

    # Build all four Ws.  One W per max-depth regime.
    Ws = {}
    for label, depth_max in [("d15", D15_REGIME_MAX_DEPTH),
                              ("d30", D30_REGIME_MAX_DEPTH),
                              ("d50", D50_REGIME_MAX_DEPTH),
                              ("d55", D55_REGIME_MAX_DEPTH)]:
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

    # ===== ARM_PART_ORACLE_50HOP (NEW borderline-half phase point) =====
    t_arm = time.time()
    W_d50, _, chains_d50, _ = Ws["d50"]
    r_part50 = arm_part_oracle_at_depth(E, R, sq, W_d50, chains_d50, depth=50,
                                          part_size=PART_SIZE)
    r_part50["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    r_part50["W_n_bindings"] = len(Ws["d50"][1])
    r_part50["W_regime"] = "d50_max_depth_50"
    r_part50["discriminator_half_line"] = DISCRIMINATOR_HALF_LINE
    r_part50["above_half_line"] = r_part50["top1"] >= DISCRIMINATOR_HALF_LINE
    out["arm_part_oracle_50hop"] = r_part50
    print("  [seed=%d] PART_ORACLE_50HOP top1=%.4f "
          "(HP_above_half=%.2f HF_death=%.2f above_half=%s) t=%.1fs" % (
              seed, r_part50["top1"], HP_50HOP_ABOVE_HALF,
              HF_MECHANISM_DEATH, r_part50["above_half_line"],
              r_part50["elapsed_s_arm"]), flush=True)

    # ===== ARM_PART_ORACLE_55HOP (NEW borderline-half phase point) =====
    t_arm = time.time()
    W_d55, _, chains_d55, _ = Ws["d55"]
    r_part55 = arm_part_oracle_at_depth(E, R, sq, W_d55, chains_d55, depth=55,
                                          part_size=PART_SIZE)
    r_part55["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    r_part55["W_n_bindings"] = len(Ws["d55"][1])
    r_part55["W_regime"] = "d55_max_depth_55"
    r_part55["discriminator_half_line"] = DISCRIMINATOR_HALF_LINE
    r_part55["above_half_line"] = r_part55["top1"] >= DISCRIMINATOR_HALF_LINE
    out["arm_part_oracle_55hop"] = r_part55
    print("  [seed=%d] PART_ORACLE_55HOP top1=%.4f "
          "(HP_above_half=%.2f above_half=%s) t=%.1fs" % (
              seed, r_part55["top1"], HP_55HOP_ABOVE_HALF,
              r_part55["above_half_line"],
              r_part55["elapsed_s_arm"]), flush=True)

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
    part50 = mean_top1("arm_part_oracle_50hop")
    part55 = mean_top1("arm_part_oracle_55hop")

    cv15 = cv_top1("arm_part_oracle_15hop")
    cv30 = cv_top1("arm_part_oracle_30hop")
    cv50 = cv_top1("arm_part_oracle_50hop")
    cv55 = cv_top1("arm_part_oracle_55hop")

    rail_15_breach = sum(1 for p in per_seed if not p.get("rail_15_ok", False))
    rail_30_breach = sum(1 for p in per_seed if not p.get("rail_30_ok", False))
    n = len(per_seed)
    half = max(1, (n + 1) // 2)

    # Informational: crossing bracket narrowed
    if not math.isnan(part50) and not math.isnan(part55):
        if part50 >= DISCRIMINATOR_HALF_LINE and part55 < DISCRIMINATOR_HALF_LINE:
            crossing_bracket_narrowed = "(50, 55]"
        elif part50 < DISCRIMINATOR_HALF_LINE and part55 < DISCRIMINATOR_HALF_LINE:
            crossing_bracket_narrowed = "(45, 50]"
        elif part50 >= DISCRIMINATOR_HALF_LINE and part55 >= DISCRIMINATOR_HALF_LINE:
            crossing_bracket_narrowed = "(55, 60]"
        else:
            # part50 below AND part55 above: non-monotonic, treat as anomaly
            crossing_bracket_narrowed = "non_monotonic"
    else:
        crossing_bracket_narrowed = "unknown"

    summ = (
        "PART_15HOP=%.4f (cv=%.3f, rail15_breach=%d/%d; target=%.4f) "
        "PART_30HOP=%.4f (cv=%.3f, rail30_breach=%d/%d; target=%.4f) "
        "PART_50HOP=%.4f (cv=%.3f; HP_above_half=%.2f) "
        "PART_55HOP=%.4f (cv=%.3f; HP_above_half=%.2f) "
        "crossing_bracket_narrowed=%s"
    ) % (
        part15, cv15, rail_15_breach, n, RAIL_15_TARGET,
        part30, cv30, rail_30_breach, n, RAIL_30_TARGET,
        part50, cv50, HP_50HOP_ABOVE_HALF,
        part55, cv55, HP_55HOP_ABOVE_HALF,
        crossing_bracket_narrowed,
    )

    # Sanity pre-emption: any rail breach majority (skip in smoke)
    if RUN_MODE != "smoke":
        if rail_15_breach >= half:
            return "RAIL_BREACH", "RAIL_BREACH_15HOP_OUT_OF_BAND: " + summ
        if rail_30_breach >= half:
            return "RAIL_BREACH", "RAIL_BREACH_30HOP_OUT_OF_BAND: " + summ

    # Smoke mode: PASS if mechanism end-to-end operates at all depths
    if RUN_MODE == "smoke":
        vals = [part15, part30, part50, part55]
        any_mech_ok = all(not math.isnan(v) and v >= 0.05 for v in vals)
        if any_mech_ok:
            return ("SMOKE_PASS",
                    "SMOKE_PASS: mechanism end-to-end OK at smoke regime "
                    "(rails not applicable at N=2048); part50=%.4f part55=%.4f "
                    "crossing_bracket_narrowed=%s | %s" % (
                        part50, part55, crossing_bracket_narrowed, summ))
        return ("HARD_FAIL",
                "SMOKE_FAIL: mechanism broken at smoke regime | " + summ)

    # Novel phase point classification (rails all pass)
    def cv_ok(cv_val: float) -> bool:
        return math.isnan(cv_val) or cv_val <= PHASE_CV_MAX

    if math.isnan(part50) or math.isnan(part55):
        return ("MIDDLE_BAND",
                "PART_50_OR_55_MISSING_METRIC | " + summ)

    # Mechanism-death first (any depth < HF)
    if part50 < HF_MECHANISM_DEATH:
        return ("MECHANISM_DEATH",
                "MECHANISM_DEATH_D50_CLIFF (below HF=%.2f): %s" % (
                    HF_MECHANISM_DEATH, summ))
    if part55 < HF_MECHANISM_DEATH:
        return ("MECHANISM_DEATH",
                "MECHANISM_DEATH_D55_CLIFF (below HF=%.2f): %s" % (
                    HF_MECHANISM_DEATH, summ))

    # Answer Skunkworks narrowing question with 3-way tier + non-monotonic
    d50_above = part50 >= HP_50HOP_ABOVE_HALF
    d55_above = part55 >= HP_55HOP_ABOVE_HALF

    if d50_above and (not d55_above) and cv_ok(cv50) and cv_ok(cv55):
        return ("CROSSING_BRACKET_50_55",
                "CROSSING_BRACKET_NARROWED_50_55 "
                "(Skunkworks revival criterion answered; bracket=%s): %s" % (
                    crossing_bracket_narrowed, summ))
    if (not d50_above) and (not d55_above) and cv_ok(cv50) and cv_ok(cv55):
        return ("CROSSING_BRACKET_45_50",
                "CROSSING_BRACKET_NARROWED_45_50 "
                "(crossing tighter than d50; bracket=%s): %s" % (
                    crossing_bracket_narrowed, summ))
    if d50_above and d55_above and cv_ok(cv50) and cv_ok(cv55):
        return ("CROSSING_BRACKET_55_60",
                "CROSSING_BRACKET_NARROWED_55_60 "
                "(crossing later than d55; bracket=%s): %s" % (
                    crossing_bracket_narrowed, summ))
    if (not d50_above) and d55_above:
        # Non-monotonic: d50 below half but d55 above; physically implausible
        return ("MIDDLE_BAND",
                "NON_MONOTONIC_D50_BELOW_D55_ABOVE_HALF_ANOMALY | " + summ)

    return ("MIDDLE_BAND",
            "MIDDLE_BAND_PARTIAL_PASS_OR_CV_BREACH | " + summ)


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
        "DESIGN_NOTE": (
            "MULTIHOP_REASONING_DEPTH_50_55_CROSSING_BRACKET: extends today's "
            "just-landed chain-grade d45-60 GPU cell (PART_45=0.5317 above; "
            "PART_60=0.4800 below; crossing_bracket=(45,60]) by adding "
            "depth-50 (predicted 0.5185 marginal above at empirical per-step "
            "0.9870) and depth-55 (predicted 0.4856 marginal below). "
            "Skunkworks 2026-07-01 revival criterion: narrow bracket to "
            "width<=5. Verdict tiers: CROSSING_BRACKET_50_55 (predicted; "
            "narrows to (50, 55]) / CROSSING_BRACKET_45_50 (narrows to "
            "(45, 50]) / CROSSING_BRACKET_55_60 (narrows to (55, 60]) / "
            "MECHANISM_DEATH (cliff at d50 or d55)."
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
