"""multihop_reasoning_depth_45_to_60_gpu_v1.

USER directive 2026-07-01 (10th CG of the day): extend today's just-landed
depth-20-to-40 CG envelope. Prior d20-40 landed CHAIN_GRADE at d20/30/40 =
0.708/0.637/0.533; per-step ~0.985 empirical. USER discriminator: locate the
0.50 crossing depth d*. Predicted at per-step 0.985: d45=0.5066 (borderline);
d60=0.4038 (below). Cell probes both.

USER-declared informational tier for the 0.50 crossing depth: report d* even
if it's between 45 and 60 (no hard gate).

PRIOR-WORK CHECK (substrate-KB concept-query 2026-07-01, exp_dev on spawn):
  Q1: "multihop reasoning depth 45 50 60 half line crossing partition oracle"
      top hit cosine=0.28 (prereg depth_extension_v1); below novelty threshold
  Q2: "multihop depth ceiling extension beyond 40 substrate cliff"
      top hit cosine=0.37 (director_cell_H_extended_multihop_consolidation);
      no cell has probed depths 45-60 with partition-oracle chain routing
  Rediscovery-vs-novel: depths 15/20/30 are chain-grade MEASURED rails; depths
  45 and 60 are GENUINELY NEW phase points. Cell extends today's d20-40 CG.

CROSS-CELL RAILS (3):
  - RAIL_DEPTH_15 must reproduce prior 0.808 +/- 0.05
  - RAIL_DEPTH_20 must reproduce prior 0.708 +/- 0.05
  - RAIL_DEPTH_30 must reproduce prior 0.637 +/- 0.05

DISCRIMINATOR (USER-declared 2026-07-01):
  "find the actual 0.50 crossing depth"
  Prior chain-grade data:
    depth=30 mean 0.637 (above 0.50)
    depth=40 mean 0.533 (above 0.50; empirical per-step = (0.533)^(1/40) = 0.9843)
  Empirical per-step 0.985; extrapolating:
    depth=45: 0.985^45 = 0.5066 (BORDERLINE HALF LINE)
    depth=60: 0.985^60 = 0.4038 (BELOW HALF LINE)
  If per-step is closer to 0.98:
    depth=45: 0.98^45 = 0.4029 (BELOW)
    depth=60: 0.98^60 = 0.2976 (BELOW)
  If per-step is closer to 0.99:
    depth=45: 0.99^45 = 0.6362 (ABOVE)
    depth=60: 0.99^60 = 0.5472 (ABOVE)
  Two-point probe (d45, d60) brackets the 0.50 crossing under all plausible
  per-step decay regimes.

ARMS (5):
  ARM_PART_ORACLE_15HOP  rail (reproduce prior 0.808)
  ARM_PART_ORACLE_20HOP  rail (reproduce prior 0.708)
  ARM_PART_ORACLE_30HOP  rail (reproduce prior 0.637)
  ARM_PART_ORACLE_45HOP  NEW phase point (predicted borderline half at 0.985)
  ARM_PART_ORACLE_60HOP  NEW phase point (predicted below half at 0.985)

PRE-REG BANDS (LOCKED at module init):
  Sanity rails:
    RAIL_15: PART_15HOP in [0.758, 0.858] else RAIL_15_BREACH
    RAIL_20: PART_20HOP in [0.658, 0.758] else RAIL_20_BREACH
    RAIL_30: PART_30HOP in [0.587, 0.687] else RAIL_30_BREACH
  Novel phase points (USER-supplied gate design):
    HP_45HOP_STILL_ABOVE_HALF: PART_45HOP >= 0.50
    HP_60HOP_CROSSED:          PART_60HOP <= 0.50 -> answers USER's crossing q
    HF_MECHANISM_DEATH:        PART_45HOP < 0.10 (mechanism cliff)
  Stability:
    cv across seeds <= 0.10 for HARD_PASS claim

DISCRIMINATOR TIERS (5-way; USER-declared 0.50 crossing informational):
  DEPTH_60_CROSSED_HALF:    d45 >= 0.50 AND d60 <= 0.50 (crossing between 45 and 60)
                            -> answers USER's question with 15-hop resolution
  DEPTH_45_ALREADY_CROSSED: d45 < 0.50 AND d60 < 0.50 (crossing at or before 45)
                            -> crossing tighter than 45; informational d* < 45
  DEPTH_60_STILL_ABOVE_HALF: d45 >= 0.50 AND d60 >= 0.50
                            -> envelope open beyond depth 60; ceiling not found
  DEPTH_45_MECHANISM_DEATH: d45 < 0.10 (per-step < 0.94)
                            -> cliff before d45; mechanism failure
  RAIL_BREACH:              any rail breach majority of seeds -> setup broken
  MIDDLE_BAND:              other partial passes or cv breach

INFORMATIONAL FIELD (USER-requested):
  crossing_depth_located:
    - "45-60"     if DEPTH_60_CROSSED_HALF (bracket, d* in (45, 60])
    - "<45"       if DEPTH_45_ALREADY_CROSSED (d* < 45, needs finer sweep)
    - ">60"       if DEPTH_60_STILL_ABOVE_HALF (d* > 60, envelope open)
    - "unknown"   otherwise

GPU IMPLEMENTATION (Fix #24 active GPU use):
  - All Ws (W_d15, W_d20, W_d30, W_d45, W_d60) built on torch.cuda via batched
    outer-product accumulation; E, R kept on GPU throughout.
  - Argmax cleanup is torch.argmax(E_part @ (W @ key)) on GPU.
  - Per-W memory at N=8192: 1 W = 268MB float32; 5 Ws = ~1.34GB resident;
    plus E (6.5MB) + R (0.3MB) = ~1.35GB peak; well under 8GB GPU.
  - Peak alloc measured per-seed; each W freed via del + empty_cache post-seed.
  - W_d60 requires make_deep_chains at max_depth=60 (200*60=12000 bindings);
    SNR per binding at N=8192: N/M = 8192/12000 = 0.683 (below unit but
    per-step 0.985 confirms operation; d60 arm quality tests this).

DEFENSIVE ERROR-CHECKING (META_RULE_AH + start-marker + heartbeat):
  - start_marker written at main() entry
  - crash_diagnostic in outer try/except (SystemExit + KeyboardInterrupt re-raise)
  - per-seed heartbeat via _cell_heartbeat helper
  - metrics.json atomic write via write_metrics helper

ASCII-only; per-seed checkpoint (PROT-021); atexit synthesizer;
zero-LLM-call assert. Author: exp_dev 2026-07-01 (USER-directed extension of
d20-40 CG).
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

ANCHOR_NAME = "multihop_reasoning_depth_45_to_60_gpu_v1"
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
#   depth_extension_v1 + depth_ceiling_sweep_v1: PART_15HOP=0.808
#   depth_ceiling_sweep_v1: PART_20HOP=0.708, PART_30HOP=0.637
#   depth_20_to_40_gpu_v1 (landed 2026-07-01): PART_20HOP=0.708, PART_30HOP=0.637
RAIL_15_TARGET = 0.808
RAIL_15_LO = 0.758
RAIL_15_HI = 0.858
RAIL_20_TARGET = 0.708
RAIL_20_LO = 0.658
RAIL_20_HI = 0.758
RAIL_30_TARGET = 0.637
RAIL_30_LO = 0.587
RAIL_30_HI = 0.687

# Novel phase points: depth 45 and 60 (USER discriminator "0.50 crossing")
# THEORETICAL@0.985^45=0.5066 (empirical per-step from d20-40 landing)
# THEORETICAL@0.985^60=0.4038
# USER-supplied gates:
HP_45HOP_STILL_ABOVE_HALF = 0.50  # d45 HARD_PASS if >= this
HP_60HOP_CROSSED = 0.50           # d60 HARD_PASS if <= this
HF_MECHANISM_DEATH_45 = 0.10      # d45 HARD_FAIL if < this (mechanism cliff)
DISCRIMINATOR_HALF_LINE = 0.50    # informational; USER's crossing question

PHASE_CV_MAX = 0.10  # per-arm seed cv cap for HARD_PASS claim

# CRLB / capacity-feasibility (META_RULE_9 CRLB gate):
# Partition-oracle argmax over PART_SIZE=10 items at N=8192.
# For W_d60: M=n_chains*max_depth=200*60=12000 bindings; SNR per binding =
# N/M = 8192/12000 = 0.683.  Per-hop random-guess floor (Cramer-Rao adjacent)
# stays at 1/PART_SIZE=0.10 (argmax over 10 items) regardless of W SNR;
# the SNR only affects per-hop accuracy signal quality.
CRLB_FLOOR_COMPUTED = 1.0 / 10.0  # = 0.10; argmax-over-PART_SIZE random-guess floor
CRLB_FORMULA = "per_hop_random_guess = 1/PART_SIZE = 1/10 = 0.10"
# Discriminator reachability: HP_60HOP_CROSSED requires PART_60HOP <= 0.50; the
# random-guess floor 0.10 satisfies this trivially (a broken mechanism would
# hit floor at 0.10; a working one at 0.985 per-step would hit 0.40; both
# below 0.50 => discriminator gate reachable from both mechanism-alive and
# mechanism-broken sides).  For d45, HP >= 0.50 is only reachable if per-step
# > 0.5^(1/45) = 0.9847; empirical 0.985 is above this so achievable.
DISCRIMINATOR_REACHABILITY = True  # both gates physically reachable
DISCRIMINATOR_REACH_NOTE = (
    "d45 HP >= 0.50 achievable iff per-step > 0.5^(1/45)=0.9847; empirical "
    "0.985 > 0.9847 (marginally). d60 HP <= 0.50 achievable at 0.985 per-step "
    "(pred 0.404). Both gates on live-decay branch."
)

# Locked invariants
assert RAIL_15_LO < RAIL_15_TARGET < RAIL_15_HI
assert RAIL_20_LO < RAIL_20_TARGET < RAIL_20_HI
assert RAIL_30_LO < RAIL_30_TARGET < RAIL_30_HI
assert HP_45HOP_STILL_ABOVE_HALF > HF_MECHANISM_DEATH_45
assert HP_60HOP_CROSSED > HF_MECHANISM_DEATH_45
assert 0.0 < PHASE_CV_MAX <= 0.20

# Cell config (mirror prior d20-40 v1 for rail reproduction)
V_CONCEPTS = 200
V_PRED = 10
K_SET = 20
N_CHAINS = 200
N_PARTITIONS = 20

# Phase point depths
DEPTHS = [15, 20, 30, 45, 60]
MAX_DEPTH = 60

assert V_CONCEPTS % N_PARTITIONS == 0
PART_SIZE = V_CONCEPTS // N_PARTITIONS  # 10

# Regimes for the FIVE Ws
D15_REGIME_MAX_DEPTH = 15  # W_d15: 200*15 = 3000 bindings
D20_REGIME_MAX_DEPTH = 20  # W_d20: 200*20 = 4000 bindings
D30_REGIME_MAX_DEPTH = 30  # W_d30: 200*30 = 6000 bindings
D45_REGIME_MAX_DEPTH = 45  # W_d45: 200*45 = 9000 bindings
D60_REGIME_MAX_DEPTH = 60  # W_d60: 200*60 = 12000 bindings

# CARDINALITY: 5 arms x 3 seeds = 15 unit measurements; EXPECTED_N_UNITS=3 seeds
CARDINALITY_OK = True
EXPECTED_N_UNITS = 3  # seeds; arms are internal to each seed record

if RUN_MODE == "smoke":
    N_DIM = 2048
    SEEDS = [7]
    N_CHAINS_LOCAL = 25       # 25 chains for smoke (lighter than full)
else:
    N_DIM = 8192
    SEEDS = [7, 13, 19]       # USER-specified [7, 13, 19]
    N_CHAINS_LOCAL = N_CHAINS  # 200

ENCODER_PROVENANCE = "SUBSTRATE_NATIVE"

CONFIG_VERSION = (
    "multihopReasoningDepth45to60V1: N=%d V_C=%d V_P=%d K=%d N_PARTS=%d "
    "PART_SIZE=%d depths=%s max_depth=%d n_chains=%d "
    "W_d15=%d W_d20=%d W_d30=%d W_d45=%d W_d60=%d "
    "seeds=%s mode=%s encoder=%s "
    "rail_15=[%.3f,%.3f] rail_20=[%.3f,%.3f] rail_30=[%.3f,%.3f] "
    "HP_45_above_half=%.2f HP_60_crossed=%.2f HF_death=%.2f "
    "discriminator_half=%.2f phase_cv_max=%.2f crlb_floor=%.3f"
) % (
    N_DIM, V_CONCEPTS, V_PRED, K_SET, N_PARTITIONS, PART_SIZE,
    DEPTHS, MAX_DEPTH, N_CHAINS_LOCAL,
    D15_REGIME_MAX_DEPTH, D20_REGIME_MAX_DEPTH,
    D30_REGIME_MAX_DEPTH, D45_REGIME_MAX_DEPTH, D60_REGIME_MAX_DEPTH,
    SEEDS, RUN_MODE, ENCODER_PROVENANCE,
    RAIL_15_LO, RAIL_15_HI, RAIL_20_LO, RAIL_20_HI, RAIL_30_LO, RAIL_30_HI,
    HP_45HOP_STILL_ABOVE_HALF, HP_60HOP_CROSSED, HF_MECHANISM_DEATH_45,
    DISCRIMINATOR_HALF_LINE, PHASE_CV_MAX, CRLB_FLOOR_COMPUTED,
)


# ----------------------------------------------------------------------------
# Primitives (GPU-native; VERBATIM port from d20-40 v1)
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
    # V=72 supports max_depth=60 with headroom (nodes list holds 61 concepts).
    V = 72
    P = 4
    sq = math.sqrt(n)
    E = bipolar_gpu(V, n, g)
    R = bipolar_gpu(P, n, g)

    # T1: bipolar shapes + norm
    assert E.shape == (V, n) and R.shape == (P, n)
    assert abs(float(E[0].norm()) - 1.0) < 1e-4

    # T2: chain construction at all five depths
    for max_d in [15, 20, 30, 45, 60]:
        triples, chains = make_deep_chains(4, V, P, max_depth=max_d, g=g,
                                              disallow_s=set())
        assert len(chains) == 4 and len(triples) == 4 * max_d

    # T3: ingest tiny config (build W_d60 covers all shorter depths via prefix)
    triples60, chains60 = make_deep_chains(4, V, P, max_depth=60, g=g,
                                              disallow_s=set())
    W60 = ingest_hebbian_gpu(triples60, E, R, sq, n)
    assert W60.shape == (n, n)
    assert torch.isfinite(W60).all()

    # T4: part_oracle at each depth on tiny config
    # V=72 divisible by n_parts_test=6 -> part_sz_test=12 (self-test only)
    n_parts_test = 6
    assert V % n_parts_test == 0
    part_sz_test = V // n_parts_test

    for depth_test in [15, 20, 30, 45, 60]:
        r = arm_part_oracle_at_depth(E, R, sq, W60,
                                       [c[:depth_test] for c in chains60],
                                       depth=depth_test, part_size=part_sz_test)
        assert 0.0 <= r["top1"] <= 1.0
        assert len(r["per_step_acc"]) == depth_test

    # T5: bands LOCKED (regression on accidental band drift)
    assert HP_45HOP_STILL_ABOVE_HALF == 0.50 and HP_60HOP_CROSSED == 0.50
    assert HF_MECHANISM_DEATH_45 == 0.10
    assert DISCRIMINATOR_HALF_LINE == 0.50
    assert RAIL_15_LO == 0.758 and RAIL_15_HI == 0.858
    assert RAIL_20_LO == 0.658 and RAIL_20_HI == 0.758
    assert RAIL_30_LO == 0.587 and RAIL_30_HI == 0.687

    # T6: CRLB reachability (BOTH gates on live-decay branch)
    assert CRLB_FLOOR_COMPUTED == 0.10
    assert DISCRIMINATOR_REACHABILITY is True
    # HP_45HOP >= 0.50 requires per-step > 0.5^(1/45); verify formula:
    per_step_needed_d45 = 0.5 ** (1.0 / 45.0)
    assert 0.984 < per_step_needed_d45 < 0.986, per_step_needed_d45

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

    print("[selftest] PASS depths=[15,20,30,45,60] gpu=%s bands_locked=True "
          "crlb_reach=%s per_step_needed_d45=%.4f"
          % (GPU_AVAIL, DISCRIMINATOR_REACHABILITY, per_step_needed_d45),
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
                              ("d20", D20_REGIME_MAX_DEPTH),
                              ("d30", D30_REGIME_MAX_DEPTH),
                              ("d45", D45_REGIME_MAX_DEPTH),
                              ("d60", D60_REGIME_MAX_DEPTH)]:
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

    # ===== ARM_PART_ORACLE_20HOP (rail: reproduce prior 0.708) =====
    t_arm = time.time()
    W_d20, _, chains_d20, _ = Ws["d20"]
    r_part20 = arm_part_oracle_at_depth(E, R, sq, W_d20, chains_d20, depth=20,
                                          part_size=PART_SIZE)
    r_part20["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    r_part20["W_n_bindings"] = len(Ws["d20"][1])
    r_part20["W_regime"] = "d20_max_depth_20"
    out["arm_part_oracle_20hop"] = r_part20
    rail_20_ok = (RAIL_20_LO <= r_part20["top1"] <= RAIL_20_HI)
    out["rail_20_ok"] = rail_20_ok
    print("  [seed=%d] PART_ORACLE_20HOP top1=%.4f "
          "(rail_ok=%s; band=[%.3f,%.3f]; target=%.4f) t=%.1fs" % (
              seed, r_part20["top1"],
              rail_20_ok, RAIL_20_LO, RAIL_20_HI, RAIL_20_TARGET,
              r_part20["elapsed_s_arm"]), flush=True)

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

    # ===== ARM_PART_ORACLE_45HOP (NEW borderline-half phase point) =====
    t_arm = time.time()
    W_d45, _, chains_d45, _ = Ws["d45"]
    r_part45 = arm_part_oracle_at_depth(E, R, sq, W_d45, chains_d45, depth=45,
                                          part_size=PART_SIZE)
    r_part45["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    r_part45["W_n_bindings"] = len(Ws["d45"][1])
    r_part45["W_regime"] = "d45_max_depth_45"
    r_part45["discriminator_half_line"] = DISCRIMINATOR_HALF_LINE
    r_part45["above_half_line"] = r_part45["top1"] >= DISCRIMINATOR_HALF_LINE
    out["arm_part_oracle_45hop"] = r_part45
    print("  [seed=%d] PART_ORACLE_45HOP top1=%.4f "
          "(HP_above_half=%.2f HF_death=%.2f above_half=%s) t=%.1fs" % (
              seed, r_part45["top1"], HP_45HOP_STILL_ABOVE_HALF,
              HF_MECHANISM_DEATH_45, r_part45["above_half_line"],
              r_part45["elapsed_s_arm"]), flush=True)

    # ===== ARM_PART_ORACLE_60HOP (NEW below-half phase point) =====
    t_arm = time.time()
    W_d60, _, chains_d60, _ = Ws["d60"]
    r_part60 = arm_part_oracle_at_depth(E, R, sq, W_d60, chains_d60, depth=60,
                                          part_size=PART_SIZE)
    r_part60["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    r_part60["W_n_bindings"] = len(Ws["d60"][1])
    r_part60["W_regime"] = "d60_max_depth_60"
    r_part60["discriminator_half_line"] = DISCRIMINATOR_HALF_LINE
    r_part60["above_half_line"] = r_part60["top1"] >= DISCRIMINATOR_HALF_LINE
    out["arm_part_oracle_60hop"] = r_part60
    print("  [seed=%d] PART_ORACLE_60HOP top1=%.4f "
          "(HP_crossed=%.2f (<=); above_half=%s) t=%.1fs" % (
              seed, r_part60["top1"], HP_60HOP_CROSSED,
              r_part60["above_half_line"],
              r_part60["elapsed_s_arm"]), flush=True)

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
    part20 = mean_top1("arm_part_oracle_20hop")
    part30 = mean_top1("arm_part_oracle_30hop")
    part45 = mean_top1("arm_part_oracle_45hop")
    part60 = mean_top1("arm_part_oracle_60hop")

    cv15 = cv_top1("arm_part_oracle_15hop")
    cv20 = cv_top1("arm_part_oracle_20hop")
    cv30 = cv_top1("arm_part_oracle_30hop")
    cv45 = cv_top1("arm_part_oracle_45hop")
    cv60 = cv_top1("arm_part_oracle_60hop")

    rail_15_breach = sum(1 for p in per_seed if not p.get("rail_15_ok", False))
    rail_20_breach = sum(1 for p in per_seed if not p.get("rail_20_ok", False))
    rail_30_breach = sum(1 for p in per_seed if not p.get("rail_30_ok", False))
    n = len(per_seed)
    half = max(1, (n + 1) // 2)

    # Informational: crossing depth bracket
    if not math.isnan(part45) and not math.isnan(part60):
        if part45 >= DISCRIMINATOR_HALF_LINE and part60 <= DISCRIMINATOR_HALF_LINE:
            crossing_bracket = "45-60"
        elif part45 < DISCRIMINATOR_HALF_LINE and part60 < DISCRIMINATOR_HALF_LINE:
            crossing_bracket = "<45"
        elif part45 >= DISCRIMINATOR_HALF_LINE and part60 >= DISCRIMINATOR_HALF_LINE:
            crossing_bracket = ">60"
        else:
            # part45 below and part60 above: non-monotonic, treat as anomaly
            crossing_bracket = "non_monotonic"
    else:
        crossing_bracket = "unknown"

    summ = (
        "PART_15HOP=%.4f (cv=%.3f, rail15_breach=%d/%d; target=%.4f) "
        "PART_20HOP=%.4f (cv=%.3f, rail20_breach=%d/%d; target=%.4f) "
        "PART_30HOP=%.4f (cv=%.3f, rail30_breach=%d/%d; target=%.4f) "
        "PART_45HOP=%.4f (cv=%.3f; HP_above_half=%.2f) "
        "PART_60HOP=%.4f (cv=%.3f; HP_crossed<=%.2f) "
        "crossing_bracket=%s"
    ) % (
        part15, cv15, rail_15_breach, n, RAIL_15_TARGET,
        part20, cv20, rail_20_breach, n, RAIL_20_TARGET,
        part30, cv30, rail_30_breach, n, RAIL_30_TARGET,
        part45, cv45, HP_45HOP_STILL_ABOVE_HALF,
        part60, cv60, HP_60HOP_CROSSED,
        crossing_bracket,
    )

    # Sanity pre-emption: any rail breach majority (skip in smoke)
    if RUN_MODE != "smoke":
        if rail_15_breach >= half:
            return "RAIL_BREACH", "RAIL_BREACH_15HOP_OUT_OF_BAND: " + summ
        if rail_20_breach >= half:
            return "RAIL_BREACH", "RAIL_BREACH_20HOP_OUT_OF_BAND: " + summ
        if rail_30_breach >= half:
            return "RAIL_BREACH", "RAIL_BREACH_30HOP_OUT_OF_BAND: " + summ

    # Smoke mode: PASS if mechanism end-to-end operates at all depths
    if RUN_MODE == "smoke":
        vals = [part15, part20, part30, part45, part60]
        any_mech_ok = all(not math.isnan(v) and v >= 0.05 for v in vals)
        if any_mech_ok:
            return ("SMOKE_PASS",
                    "SMOKE_PASS: mechanism end-to-end OK at smoke regime "
                    "(rails not applicable at N=2048); part45=%.4f part60=%.4f "
                    "crossing_bracket=%s | %s" % (
                        part45, part60, crossing_bracket, summ))
        return ("HARD_FAIL",
                "SMOKE_FAIL: mechanism broken at smoke regime | " + summ)

    # Novel phase point classification (rails all pass)
    def cv_ok(cv_val: float) -> bool:
        return math.isnan(cv_val) or cv_val <= PHASE_CV_MAX

    if math.isnan(part45) or math.isnan(part60):
        return ("MIDDLE_BAND",
                "PART_45_OR_60_MISSING_METRIC | " + summ)

    # Mechanism-death first (d45 < HF)
    if part45 < HF_MECHANISM_DEATH_45:
        return ("DEPTH_45_MECHANISM_DEATH",
                "DEPTH_45_MECHANISM_DEATH_CLIFF_BEFORE_45 "
                "(mechanism cliff below HF=%.2f): %s" % (
                    HF_MECHANISM_DEATH_45, summ))

    # Answer USER's crossing question with 5-way tier
    d45_above = part45 >= HP_45HOP_STILL_ABOVE_HALF
    d60_crossed = part60 <= HP_60HOP_CROSSED

    if d45_above and d60_crossed and cv_ok(cv45) and cv_ok(cv60):
        return ("DEPTH_60_CROSSED_HALF",
                "DEPTH_60_CROSSED_HALF_LINE_LOCATED_BETWEEN_45_AND_60 "
                "(USER discriminator answered; crossing_bracket=%s): %s" % (
                    crossing_bracket, summ))
    if (not d45_above) and d60_crossed and cv_ok(cv45) and cv_ok(cv60):
        return ("DEPTH_45_ALREADY_CROSSED",
                "DEPTH_45_ALREADY_BELOW_HALF_CROSSING_TIGHTER_THAN_45 "
                "(needs finer sweep at 40-45; crossing_bracket=%s): %s" % (
                    crossing_bracket, summ))
    if d45_above and (not d60_crossed) and cv_ok(cv45) and cv_ok(cv60):
        return ("DEPTH_60_STILL_ABOVE_HALF",
                "DEPTH_60_STILL_ABOVE_HALF_ENVELOPE_OPEN_BEYOND_60 "
                "(ceiling not found; crossing_bracket=%s): %s" % (
                    crossing_bracket, summ))
    if (not d45_above) and (not d60_crossed):
        # Non-monotonic: d45 below half but d60 above; anomaly
        return ("MIDDLE_BAND",
                "NON_MONOTONIC_D45_BELOW_D60_ABOVE_HALF_ANOMALY | " + summ)

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
            "MULTIHOP_REASONING_DEPTH_45_TO_60: extends today's just-landed "
            "chain-grade d20-40 GPU cell (PART_20/30/40=0.708/0.637/0.533; "
            "per-step empirical ~0.985) by adding depth-45 (predicted "
            "borderline half at 0.985 per-step -> 0.507) and depth-60 "
            "(predicted below half at 0.985 per-step -> 0.404). USER "
            "2026-07-01: 'find the actual 0.50 crossing depth'. Two-point "
            "probe brackets the crossing informationally. Verdict tiers: "
            "DEPTH_60_CROSSED_HALF (bracket 45-60; answers question) / "
            "DEPTH_45_ALREADY_CROSSED (bracket <45; needs finer) / "
            "DEPTH_60_STILL_ABOVE_HALF (bracket >60; envelope open) / "
            "DEPTH_45_MECHANISM_DEATH (cliff before 45)."
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
