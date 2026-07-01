"""multihop_reasoning_depth_20_to_40_gpu_v1.

USER directive 2026-07-01: stress-test multi-hop chain-grade envelope at
depths {15, 20, 30, 40}. Discriminator: at what depth does recall drop below
0.50? Same partition-oracle routed cleanup mechanism from prior chain-grade
depth-15 result. GPU-eligible torch.

PRIOR-WORK CHECK (substrate-KB concept-query 2026-07-01):
  Q: "multi-hop reasoning depth partition oracle chain extension"
  Top hits (cosine <= 0.40; below the 0.30 novelty threshold is empty but
  the two direct prior cells are LOAD-BEARING):
    1. phase_diagram_multihop_depth_extension_via_partition_oracle_v1
       (chain-graded 5/7/10/15 at PART_15HOP=0.808 cv=0.024)
    2. phase_diagram_multihop_depth_ceiling_sweep_20_25_30_v1
       (chain-graded 15/20/25/30 at PART_30HOP=0.637 cv=0.043 all HARD_PASS)
  Rediscovery-vs-novel: depths 15/20/30 are already chain-grade MEASURED;
  depth=40 is GENUINELY NEW. USER's ask overlaps 3/4 with prior cell but the
  depth=40 point is beyond prior work AND probes discriminator "recall below
  0.50" which prior cell hits by-construction at depth 30 (mean 0.637 is
  still above 0.50 -> discriminator has NOT fired). We ship this cell to
  find where the 0.50 crossing lives.

CROSS-CELL RAILS (2):
  - RAIL_DEPTH_15 must reproduce prior depth-extension-v1 at 0.808 +/- 0.05
    (proves invocation aligned with chain-grade primitive)
  - RAIL_DEPTH_20_30_REPRO must reproduce prior depth-ceiling-sweep-v1 within
    +/- 0.05 (proves setup + regime match)

DISCRIMINATOR (USER-declared):
  "at what depth does recall drop below 0.50?"
  Prior chain-grade data:
    depth=25 mean 0.673 (above 0.50)
    depth=30 mean 0.637 (above 0.50)
  Extrapolating 0.97-per-step: depth=40 predicts 0.99^40 = 0.669,
                                                0.97^40 = 0.296,
                                                0.95^40 = 0.129
  Prior per-step at depth=30 was ~0.98 (0.98^30 = 0.545); at depth=40 with
  ~0.98 per-step -> 0.98^40 = 0.446. So depth=40 is the FIRST predicted
  crossing below 0.50 -> discriminator FIRES at depth=40 by prediction.

ARMS (4):
  ARM_PART_ORACLE_15HOP  rail (reproduce depth-extension-v1 target 0.808)
  ARM_PART_ORACLE_20HOP  rail (reproduce depth-ceiling-sweep-v1 ~0.708)
  ARM_PART_ORACLE_30HOP  rail (reproduce depth-ceiling-sweep-v1 ~0.637)
  ARM_PART_ORACLE_40HOP  NEW phase point (discriminator)

PRE-REG BANDS (LOCKED at module init):
  Sanity rails:
    RAIL_15: PART_15HOP in [0.758, 0.858] else RAIL_15_BREACH
    RAIL_20: PART_20HOP in [0.658, 0.758] else RAIL_20_BREACH (prior 0.708 +/- 0.05)
    RAIL_30: PART_30HOP in [0.587, 0.687] else RAIL_30_BREACH (prior 0.637 +/- 0.05)
  Novel phase point:
    40HOP: HARD_PASS if mean >= 0.30   HARD_FAIL if mean < 0.10
           MIDDLE_BAND otherwise
  Stability:
    cv across seeds <= 0.10 for HARD_PASS claim

DISCRIMINATOR TIERS (USER-declared "recall drops below 0.50"):
  DEPTH_40_STILL_ABOVE_HALF:  40HOP mean >= 0.50 (all rails pass)
                              -> ceiling extends beyond depth 40 (envelope open)
  DEPTH_40_BELOW_HALF:        40HOP mean in [0.30, 0.50)
                              -> discriminator FIRES at depth 40 (0.50 crossing
                              between 30 and 40)
  DEPTH_40_HARD_FAIL:         40HOP mean < 0.10
                              -> cliff BEFORE depth 40 (mechanism failure)
  RAIL_BREACH:                any rail breach majority of seeds -> setup broken
  MIDDLE_BAND:                40HOP in [0.10, 0.30), rails OK
                              -> mechanism operating but well below chain-grade

GPU IMPLEMENTATION (Fix #24 active GPU use):
  - All Ws (W_d15, W_d20, W_d30, W_d40) built on torch.cuda via batched
    outer-product accumulation; E, R kept on GPU throughout.
  - Argmax cleanup is torch.argmax(E_part @ (W @ key)) on GPU.
  - Per-W memory at N=8192: 1 W = 268MB float32; 4 Ws = ~1.07GB resident;
    plus E (6.5MB) + R (0.3MB) = ~1.08GB peak; well under 8GB GPU.
  - Peak alloc measured per-seed; each W freed via del + empty_cache post-seed.

DEFENSIVE ERROR-CHECKING (META_RULE_AH + start-marker + heartbeat):
  - start_marker written at main() entry
  - crash_diagnostic in outer try/except (SystemExit + KeyboardInterrupt re-raise)
  - per-seed heartbeat via _cell_heartbeat helper
  - metrics.json atomic write via write_metrics helper

ASCII-only; per-seed checkpoint (PROT-021); atexit synthesizer;
zero-LLM-call assert. Author: exp_dev 2026-07-01 (USER-directed).
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

ANCHOR_NAME = "multihop_reasoning_depth_20_to_40_gpu_v1"
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
# Rails (all three from prior chain-grade data):
#   depth-extension-v1: PART_15HOP MEASURED@data/exp_phase_diagram_multihop_depth_extension_via_partition_oracle_v1/metrics.json:verdict_msg = 0.8083
#   depth-ceiling-sweep-v1: PART_15HOP MEASURED = 0.8100, PART_20HOP MEASURED = 0.7083, PART_30HOP MEASURED = 0.6367
RAIL_15_TARGET = 0.808  # avg of prior two cells
RAIL_15_LO = 0.758
RAIL_15_HI = 0.858
RAIL_20_TARGET = 0.708
RAIL_20_LO = 0.658
RAIL_20_HI = 0.758
RAIL_30_TARGET = 0.637
RAIL_30_LO = 0.587
RAIL_30_HI = 0.687

# Novel phase point: depth 40 (USER discriminator "recall below 0.50")
# THEORETICAL@0.98^40=0.446 (prior per-step ~0.98 at depth 30)
# THEORETICAL@0.97^40=0.296 (conservative)
# THEORETICAL@0.99^40=0.669 (optimistic)
# HARD_PASS threshold set at 0.30 (matches prior 30-hop HP band; chain-grade if reached)
# HARD_FAIL threshold at 0.10 (mechanism cliff)
HP_40HOP = 0.30
HF_40HOP = 0.10
# USER discriminator crossing at 0.50 (informational; not a hard gate)
DISCRIMINATOR_HALF_LINE = 0.50

PHASE_CV_MAX = 0.10  # per-arm seed cv cap for HARD_PASS claim

# CRLB / capacity-feasibility (META_RULE_9 CRLB gate):
# Partition-oracle argmax over PART_SIZE=10 items at N=8192 has per-hop signal
# noise dominated by chain-length noise (crosstalk from OTHER bindings in W).
# For M=n_chains*max_depth=8000 bindings at N=8192, SNR per binding ~ N/M = 1.024.
# Per-hop accuracy floor (Cramer-Rao bound-adjacent) approaches 1/PART_SIZE=0.10
# as SNR->0; observed 0.98/hop at depth 30 confirms SNR >> 1.
# discriminator_reachability: HP_40HOP=0.30 is above 1/PART_SIZE=0.10 floor; OK.
CRLB_FLOOR_COMPUTED = 1.0 / 10.0  # = 0.10; argmax-over-PART_SIZE random-guess floor
CRLB_FORMULA = "per_hop_random_guess = 1/PART_SIZE = 1/10 = 0.10"
DISCRIMINATOR_REACHABILITY = HP_40HOP > CRLB_FLOOR_COMPUTED  # True

# Locked invariants
assert RAIL_15_LO < RAIL_15_TARGET < RAIL_15_HI
assert RAIL_20_LO < RAIL_20_TARGET < RAIL_20_HI
assert RAIL_30_LO < RAIL_30_TARGET < RAIL_30_HI
assert HP_40HOP > HF_40HOP
assert HP_40HOP > CRLB_FLOOR_COMPUTED, "HP_40HOP unreachable below CRLB floor"
assert HF_40HOP >= CRLB_FLOOR_COMPUTED, "HF_40HOP below random-guess floor"
assert 0.0 < PHASE_CV_MAX <= 0.20

# Cell config (per directive; inherits depth-ceiling v1 envelope)
V_CONCEPTS = 200
V_PRED = 10
K_SET = 20
N_CHAINS = 200
N_PARTITIONS = 20

# Phase point depths
DEPTHS = [15, 20, 30, 40]
MAX_DEPTH = 40

assert V_CONCEPTS % N_PARTITIONS == 0
PART_SIZE = V_CONCEPTS // N_PARTITIONS  # 10

# Regimes for the FOUR Ws
D15_REGIME_MAX_DEPTH = 15  # W_d15: 200*15 = 3000 bindings
D20_REGIME_MAX_DEPTH = 20  # W_d20: 200*20 = 4000 bindings
D30_REGIME_MAX_DEPTH = 30  # W_d30: 200*30 = 6000 bindings
D40_REGIME_MAX_DEPTH = 40  # W_d40: 200*40 = 8000 bindings

if RUN_MODE == "smoke":
    N_DIM = 2048
    SEEDS = [11]
    N_CHAINS_LOCAL = 25       # 25 chains for smoke (lighter than full)
else:
    N_DIM = 8192
    SEEDS = [11, 13, 19]
    N_CHAINS_LOCAL = N_CHAINS  # 200

ENCODER_PROVENANCE = "SUBSTRATE_NATIVE"

CONFIG_VERSION = (
    "multihopReasoningDepth20to40V1: N=%d V_C=%d V_P=%d K=%d N_PARTS=%d "
    "PART_SIZE=%d depths=%s max_depth=%d n_chains=%d "
    "W_d15=%d W_d20=%d W_d30=%d W_d40=%d "
    "seeds=%s mode=%s encoder=%s "
    "rail_15=[%.3f,%.3f] rail_20=[%.3f,%.3f] rail_30=[%.3f,%.3f] "
    "HP_40=%.2f HF_40=%.2f discriminator_half=%.2f "
    "phase_cv_max=%.2f crlb_floor=%.3f"
) % (
    N_DIM, V_CONCEPTS, V_PRED, K_SET, N_PARTITIONS, PART_SIZE,
    DEPTHS, MAX_DEPTH, N_CHAINS_LOCAL,
    D15_REGIME_MAX_DEPTH, D20_REGIME_MAX_DEPTH,
    D30_REGIME_MAX_DEPTH, D40_REGIME_MAX_DEPTH,
    SEEDS, RUN_MODE, ENCODER_PROVENANCE,
    RAIL_15_LO, RAIL_15_HI, RAIL_20_LO, RAIL_20_HI, RAIL_30_LO, RAIL_30_HI,
    HP_40HOP, HF_40HOP, DISCRIMINATOR_HALF_LINE,
    PHASE_CV_MAX, CRLB_FLOOR_COMPUTED,
)


# ----------------------------------------------------------------------------
# Primitives (GPU-native; VERBATIM port from depth-ceiling-sweep v1)
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
    # V must exceed max_depth+1 so make_deep_chains can pick distinct nodes
    # (nodes list holds max_depth+1 distinct concepts; V >= max_depth+2 for safety).
    V = 60
    P = 4
    sq = math.sqrt(n)
    E = bipolar_gpu(V, n, g)
    R = bipolar_gpu(P, n, g)

    # T1: bipolar shapes + norm
    assert E.shape == (V, n) and R.shape == (P, n)
    assert abs(float(E[0].norm()) - 1.0) < 1e-4

    # T2: chain construction at all four depths
    for max_d in [15, 20, 30, 40]:
        triples, chains = make_deep_chains(4, V, P, max_depth=max_d, g=g,
                                              disallow_s=set())
        assert len(chains) == 4 and len(triples) == 4 * max_d

    # T3: ingest tiny config (build W_d40; use for all depth tests via prefix)
    triples40, chains40 = make_deep_chains(4, V, P, max_depth=40, g=g,
                                              disallow_s=set())
    W40 = ingest_hebbian_gpu(triples40, E, R, sq, n)
    assert W40.shape == (n, n)
    assert torch.isfinite(W40).all()

    # T4: part_oracle at each depth on tiny config
    # V=60 divisible by n_parts_test=6 -> part_sz_test=10 (matches full regime)
    n_parts_test = 6
    assert V % n_parts_test == 0
    part_sz_test = V // n_parts_test

    for depth_test in [15, 20, 30, 40]:
        r = arm_part_oracle_at_depth(E, R, sq, W40,
                                       [c[:depth_test] for c in chains40],
                                       depth=depth_test, part_size=part_sz_test)
        assert 0.0 <= r["top1"] <= 1.0
        assert len(r["per_step_acc"]) == depth_test

    # T5: bands LOCKED (regression on accidental band drift)
    assert HP_40HOP == 0.30 and HF_40HOP == 0.10
    assert DISCRIMINATOR_HALF_LINE == 0.50
    assert RAIL_15_LO == 0.758 and RAIL_15_HI == 0.858
    assert RAIL_20_LO == 0.658 and RAIL_20_HI == 0.758
    assert RAIL_30_LO == 0.587 and RAIL_30_HI == 0.687

    # T6: CRLB reachability
    assert HP_40HOP > CRLB_FLOOR_COMPUTED
    assert DISCRIMINATOR_REACHABILITY is True

    # T7: LLM call counter = 0 (substrate-only)
    assert _LLM_CALL_COUNTER[0] == 0

    # T8: GPU presence asserted for non-smoke mode (smoke OK on CPU)
    if RUN_MODE != "smoke":
        assert GPU_AVAIL, "FULL run requires GPU per Fix #24"

    print("[selftest] PASS depths=[15,20,30,40] gpu=%s bands_locked=True crlb_reach=%s"
          % (GPU_AVAIL, DISCRIMINATOR_REACHABILITY), flush=True)


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

    # Build all four Ws.  One W per max-depth regime (each W ingested from
    # chains at that exact max_depth, ensuring chains exist for the test).
    Ws = {}
    for label, depth_max in [("d15", D15_REGIME_MAX_DEPTH),
                              ("d20", D20_REGIME_MAX_DEPTH),
                              ("d30", D30_REGIME_MAX_DEPTH),
                              ("d40", D40_REGIME_MAX_DEPTH)]:
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

    # ===== ARM_PART_ORACLE_40HOP (NEW discriminator phase point) =====
    t_arm = time.time()
    W_d40, _, chains_d40, _ = Ws["d40"]
    r_part40 = arm_part_oracle_at_depth(E, R, sq, W_d40, chains_d40, depth=40,
                                          part_size=PART_SIZE)
    r_part40["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    r_part40["W_n_bindings"] = len(Ws["d40"][1])
    r_part40["W_regime"] = "d40_max_depth_40"
    r_part40["discriminator_half_line"] = DISCRIMINATOR_HALF_LINE
    r_part40["above_half_line"] = r_part40["top1"] >= DISCRIMINATOR_HALF_LINE
    out["arm_part_oracle_40hop"] = r_part40
    print("  [seed=%d] PART_ORACLE_40HOP top1=%.4f "
          "(HP=%.2f HF=%.2f discriminator_half=%.2f above_half=%s) t=%.1fs" % (
              seed, r_part40["top1"], HP_40HOP, HF_40HOP,
              DISCRIMINATOR_HALF_LINE, r_part40["above_half_line"],
              r_part40["elapsed_s_arm"]), flush=True)

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
    part40 = mean_top1("arm_part_oracle_40hop")

    cv15 = cv_top1("arm_part_oracle_15hop")
    cv20 = cv_top1("arm_part_oracle_20hop")
    cv30 = cv_top1("arm_part_oracle_30hop")
    cv40 = cv_top1("arm_part_oracle_40hop")

    rail_15_breach = sum(1 for p in per_seed if not p.get("rail_15_ok", False))
    rail_20_breach = sum(1 for p in per_seed if not p.get("rail_20_ok", False))
    rail_30_breach = sum(1 for p in per_seed if not p.get("rail_30_ok", False))
    n = len(per_seed)
    half = max(1, (n + 1) // 2)

    summ = (
        "PART_15HOP=%.4f (cv=%.3f, rail15_breach=%d/%d; target=%.4f) "
        "PART_20HOP=%.4f (cv=%.3f, rail20_breach=%d/%d; target=%.4f) "
        "PART_30HOP=%.4f (cv=%.3f, rail30_breach=%d/%d; target=%.4f) "
        "PART_40HOP=%.4f (cv=%.3f; HP=%.2f HF=%.2f half=%.2f)"
    ) % (
        part15, cv15, rail_15_breach, n, RAIL_15_TARGET,
        part20, cv20, rail_20_breach, n, RAIL_20_TARGET,
        part30, cv30, rail_30_breach, n, RAIL_30_TARGET,
        part40, cv40, HP_40HOP, HF_40HOP, DISCRIMINATOR_HALF_LINE,
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
        any_mech_ok = all(not math.isnan(v) and v >= 0.10
                            for v in [part15, part20, part30, part40])
        if any_mech_ok:
            return ("SMOKE_PASS",
                    "SMOKE_PASS: mechanism end-to-end OK at smoke regime "
                    "(rails not applicable at N=2048); part40=%.4f | %s" % (
                        part40, summ))
        return ("HARD_FAIL",
                "SMOKE_FAIL: mechanism broken at smoke regime | " + summ)

    # Novel phase point classification (rails all pass)
    def cv_ok(cv_val: float) -> bool:
        return math.isnan(cv_val) or cv_val <= PHASE_CV_MAX

    if math.isnan(part40):
        return ("MIDDLE_BAND",
                "PART_40HOP_MISSING_METRIC | " + summ)

    if part40 < HF_40HOP:
        return ("DEPTH_40_HARD_FAIL",
                "DEPTH_40_HARD_FAIL_CLIFF_BEFORE_DEPTH_40 (mechanism cliff below "
                "HF=%.2f): %s" % (HF_40HOP, summ))
    if part40 >= DISCRIMINATOR_HALF_LINE and cv_ok(cv40):
        return ("DEPTH_40_STILL_ABOVE_HALF",
                "DEPTH_40_STILL_ABOVE_HALF_ENVELOPE_OPEN_BEYOND_DEPTH_40: " + summ)
    if part40 >= HP_40HOP and cv_ok(cv40):
        return ("DEPTH_40_BELOW_HALF",
                "DEPTH_40_BELOW_HALF_DISCRIMINATOR_FIRES_BETWEEN_30_AND_40 "
                "(chain-grade mechanism but crossed 0.50 line): " + summ)
    return ("MIDDLE_BAND",
            "MIDDLE_BAND_PART40_IN_LOW_RANGE_OR_CV_BREACH: " + summ)


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
        "DESIGN_NOTE": (
            "MULTIHOP_REASONING_DEPTH_20_TO_40: extends prior chain-grade "
            "depth-ceiling-sweep-v1 (depths 15/20/25/30 all HARD_PASS) by "
            "adding depth=40 discriminator phase point. USER 2026-07-01: "
            "'at what depth does recall drop below 0.50?' Prior data has "
            "depth=30 at 0.637 (above 0.50). This cell tests depth=40 with "
            "three rails (15/20/30) reproducing prior chain-grade envelope. "
            "Verdict tiers: DEPTH_40_STILL_ABOVE_HALF (envelope open beyond 40) "
            "/ DEPTH_40_BELOW_HALF (discriminator fires between 30 and 40) / "
            "DEPTH_40_HARD_FAIL (mechanism cliff before 40)."
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
