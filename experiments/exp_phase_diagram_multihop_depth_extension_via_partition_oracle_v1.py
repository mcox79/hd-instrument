"""phase_diagram_multihop_depth_extension_via_partition_oracle_v1.

Cell B v2 (substrate_multihop_compose_fly_lsh_multibank_partition_v2_META_M7_rail)
chain-graded the depth=5 multi-hop phase point at PART_ORACLE=0.9550 (cv=0.007;
META_M7 PASS at 0.122 reproduce). Known phase boundary point: depth=5 with
V_C=200, K_set=20, n_chains=200, partition-routed cleanup, N=8192.

UNKNOWN: where does the chain-grade envelope cliff as depth scales? Brain handles
10+ steps for reasoning. Substrate's per-hop accuracy at depth=5 is 0.95 per step
-> at depth=10, 0.95^10 = 0.60. Is that floor or chain-grade?

This cell maps the depth phase boundary by ADDING three new phase points:
ARM_PART_ORACLE_7HOP, _10HOP, _15HOP using oracle-routed partition cleanup,
while reproducing Cell B v2's cross-cell rail at 5HOP (must hit 0.9550 +/- 0.02).

GPU IMPLEMENTATION (Fix #24 active GPU use):
  - All Ws (W_v1_regime, W_pointer_v2, W_depth15_extended) built on torch.cuda
    via batched outer-product accumulation: K = E[s]*R[p]*sq; W += V.T @ K / N.
  - E, R, all Ws kept on GPU throughout; argmax cleanup is torch.argmax(E @ (W @ key)).
  - Encoder hoisted (E, R built once per seed, NOT per arm).
  - Memory budget per seed at N=8192: 3 Ws @ 805 MB total + E (6.5 MB) + R (0.3 MB)
    = ~812 MB resident; well under 8 GB GPU.

TWO-W CANONICAL DISCIPLINE (+ one extended W for depth-15 phase point):
  W_v1_regime          = ingest_hebbian(make_deep_chains(n_chains=200, max_depth=5))
                         = 1000 bindings. For ARM_PART_ORACLE_5HOP cross-cell rail
                         (Cell B v2 target 0.9550 +/- 0.02).
  W_pointer_v2         = ingest_hebbian(make_deep_chains(n_chains=200, max_depth=10))
                         = 2000 bindings. For META_M7 reproduce arm (depth=5 test of
                         pointer-chain-v2's verbatim primitive; band [0.08, 0.25]).
                         ALSO for the 7HOP and 10HOP phase points (chains[:7], [:10]).
  W_depth15_extended   = ingest_hebbian(make_deep_chains(n_chains=200, max_depth=15))
                         = 3000 bindings. For ARM_PART_ORACLE_15HOP phase point ONLY.
                         Deliberate extension beyond TWO-W canonical pair; documented
                         because depth-15 chains don't exist in W_pointer_v2.

ARMS (6):
  ARM_BASELINE_HRR_2HOP                     beta-sweep sanity rail [0.62, 0.68]
  ARM_REPRODUCE_POINTER_CHAIN_V2_5HOP       META_M7 mandatory [0.08, 0.25]
  ARM_PART_ORACLE_5HOP                      Cell B v2 reproduce; rail 0.9550 +/- 0.02
  ARM_PART_ORACLE_7HOP                      NEW phase point on W_pointer_v2
  ARM_PART_ORACLE_10HOP                     NEW phase point on W_pointer_v2
  ARM_PART_ORACLE_15HOP                     NEW phase point on W_depth15_extended

PRE-REG BANDS (per-depth, predicted by 0.95-per-step compounding; LOCKED at module init):
  Sanity rails (verdict pre-emption on majority-seed breach):
    RAIL_BASELINE             BASELINE   NOT in [0.62, 0.68] -> SANITY_BREACH
    RAIL_META_M7              REPRODUCE  NOT in [0.08, 0.25] -> META_M7_BREACH
    RAIL_CROSS_CELL_5HOP      PART_5HOP  NOT in [0.935, 0.975] -> CROSS_CELL_BREACH
                              (0.9550 +/- 0.02; the "within 0.02" directive bar)
  Phase points (per-arm; PASS/FAIL):
    7HOP:   HARD_PASS if mean >= 0.65   HARD_FAIL if mean < 0.40
    10HOP:  HARD_PASS if mean >= 0.50   HARD_FAIL if mean < 0.25
    15HOP:  HARD_PASS if mean >= 0.30   HARD_FAIL if mean < 0.15
  Stability:
    cv across seeds <= 0.10 for each phase point claimed HARD_PASS

VERDICTS (LOCKED at module init):
  CHAIN_GRADE_DEPTH_EXTENDS:        all 4 depths (5/7/10/15) HARD_PASS -> deep reasoning scales
  PARTIAL_DEPTH_EXTENDS_TO_10:      5+7+10 HARD_PASS, 15 below           -> cliff between 10-15
  PARTIAL_DEPTH_EXTENDS_TO_7:       5+7 HARD_PASS, 10 below              -> cliff between 7-10
  DEPTH_5_IS_CEILING:               depth=5 only                          -> Cell B v2 was the limit
  CROSS_CELL_BREACH:                5HOP rail breach majority of seeds    -> reproduce failed
  META_M7_BREACH:                   reproduce breach majority             -> regime drifted
  SANITY_BREACH:                    baseline breach majority              -> setup broken

ASCII-only; per-seed checkpoint; atexit synthesizer; zero-LLM-call assert.
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

# ----------------------------------------------------------------------------
# GPU GUARD (Fix #24: GPU dispatch must actually use GPU)
# ----------------------------------------------------------------------------
try:
    import torch
except ImportError:
    print("[FATAL] torch not installed; cannot run GPU experiment.", flush=True)
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
          "Smoke OK; full dispatch should be GPU.", flush=True)

from experiments._seed_checkpoint import (
    get_output_dir, resumable_seeds, write_partial_key, aggregate_partials,
    write_metrics,
)

ANCHOR_NAME = "phase_diagram_multihop_depth_extension_via_partition_oracle_v1"
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
# Sanity rails
BASELINE_SANITY_LO = 0.62
BASELINE_SANITY_HI = 0.68
META_M7_RAIL_LO = 0.08
META_M7_RAIL_HI = 0.25
CROSS_CELL_5HOP_LO = 0.935  # 0.9550 - 0.02
CROSS_CELL_5HOP_HI = 0.975  # 0.9550 + 0.02
CROSS_CELL_5HOP_TARGET = 0.9550

# Phase point bands (per-depth)
HP_7HOP = 0.65
HF_7HOP = 0.40
HP_10HOP = 0.50
HF_10HOP = 0.25
HP_15HOP = 0.30
HF_15HOP = 0.15
PHASE_CV_MAX = 0.10  # per-arm seed cv cap for HARD_PASS claim

# Locked invariants
assert BASELINE_SANITY_LO < BASELINE_SANITY_HI
assert META_M7_RAIL_LO < META_M7_RAIL_HI
assert CROSS_CELL_5HOP_LO < CROSS_CELL_5HOP_TARGET < CROSS_CELL_5HOP_HI
assert HP_7HOP > HF_7HOP and HP_10HOP > HF_10HOP and HP_15HOP > HF_15HOP
# Compounding-prediction sanity: HP bands should NOT be above pure 0.95-per-step
# (per-step accuracy at depth=5 was 0.95 -> 0.95^7=0.6983, 0.95^10=0.5987, 0.95^15=0.4633)
assert HP_7HOP <= 0.95 ** 7 + 0.01 and HP_10HOP <= 0.95 ** 10 + 0.01
assert HP_15HOP <= 0.95 ** 15 + 0.01

# Cell config (per directive)
V_CONCEPTS = 200
V_PRED = 10
K_SET = 20  # bindings-per-cue control
N_CHAINS = 200
N_PARTITIONS = 20  # PART_SIZE = V_C / N_PARTITIONS = 10

# Phase point depths
DEPTHS = [5, 7, 10, 15]
MAX_DEPTH = 15

assert V_CONCEPTS % N_PARTITIONS == 0
PART_SIZE = V_CONCEPTS // N_PARTITIONS  # 10

# Regimes for the THREE Ws
V1_REGIME_MAX_DEPTH = 5      # W_v1_regime: 200 * 5 = 1000 bindings
POINTER_V2_MAX_DEPTH = 10    # W_pointer_v2: 200 * 10 = 2000 bindings
DEPTH15_EXT_MAX_DEPTH = 15   # W_depth15_extended: 200 * 15 = 3000 bindings

# BASELINE regime (for sanity rail)
BASELINE_V_P = 2
BASELINE_N_CHAINS = 200

if RUN_MODE == "smoke":
    N_DIM = 2048
    SEEDS = [11]
    N_CHAINS_LOCAL = 30       # 30 chains for smoke
    BASELINE_N_LOCAL = 60
else:
    N_DIM = 8192
    SEEDS = [11, 13, 19]
    N_CHAINS_LOCAL = N_CHAINS  # 200
    BASELINE_N_LOCAL = BASELINE_N_CHAINS

ENCODER_PROVENANCE = "SUBSTRATE_NATIVE"

CONFIG_VERSION = (
    "phaseDiagramMultihopDepthExtensionV1: N=%d V_C=%d V_P=%d K=%d N_PARTS=%d "
    "PART_SIZE=%d depths=%s max_depth=%d n_chains=%d "
    "W_v1_depth=%d W_pv2_depth=%d W_d15_depth=%d "
    "baseline_v_p=%d baseline_n=%d "
    "seeds=%s mode=%s encoder=%s "
    "META_M7=[%.2f,%.2f] cross_cell_5hop=[%.3f,%.3f] target=%.4f "
    "HP_7=%.2f HF_7=%.2f HP_10=%.2f HF_10=%.2f HP_15=%.2f HF_15=%.2f "
    "phase_cv_max=%.2f baseline_sanity=[%.2f,%.2f]"
) % (
    N_DIM, V_CONCEPTS, V_PRED, K_SET, N_PARTITIONS, PART_SIZE,
    DEPTHS, MAX_DEPTH, N_CHAINS_LOCAL,
    V1_REGIME_MAX_DEPTH, POINTER_V2_MAX_DEPTH, DEPTH15_EXT_MAX_DEPTH,
    BASELINE_V_P, BASELINE_N_LOCAL,
    SEEDS, RUN_MODE, ENCODER_PROVENANCE,
    META_M7_RAIL_LO, META_M7_RAIL_HI,
    CROSS_CELL_5HOP_LO, CROSS_CELL_5HOP_HI, CROSS_CELL_5HOP_TARGET,
    HP_7HOP, HF_7HOP, HP_10HOP, HF_10HOP, HP_15HOP, HF_15HOP,
    PHASE_CV_MAX,
    BASELINE_SANITY_LO, BASELINE_SANITY_HI,
)


# ----------------------------------------------------------------------------
# Primitives (GPU-native)
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
    """VERBATIM port of Cell B v2's make_deep_chains."""
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
    """Batched outer-product Hebbian ingest on GPU.

    W += sum_j outer(E[o_j], E[s_j] * R[p_j] * sq) / n_dim

    Batched matmul: V (B,N) and K (B,N) -> V.T @ K (N,N) accumulated.
    """
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
        # outer-sum: V.T @ K = (N, N)
        W = W + (V_.T @ K) / n_dim
    return W


# ----------------------------------------------------------------------------
# BASELINE arm: beta-sweep 2-hop HRR sanity rail
# ----------------------------------------------------------------------------

def make_two_hop_chains_betasweep(n_chains: int, V: int, g: np.random.Generator,
                                    p1: int = 0, p2: int = 1):
    """VERBATIM port from Cell B v2."""
    train = []
    queries = []
    used_s = set()
    tries = 0
    while len(queries) < n_chains and tries < n_chains * 100:
        tries += 1
        s = int(g.integers(0, V))
        if s in used_s:
            continue
        x = int(g.integers(0, V))
        while x == s:
            x = int(g.integers(0, V))
        o = int(g.integers(0, V))
        while o == s or o == x:
            o = int(g.integers(0, V))
        train.append((s, p1, x))
        train.append((x, p2, o))
        queries.append((s, p1, p2, o, x))
        used_s.add(s)
    return train, queries


def arm_baseline_hrr_2hop(E: torch.Tensor, R: torch.Tensor, sq: float,
                           train_triples, queries) -> Dict[str, Any]:
    """beta-sweep 2-hop sanity. Build local W on the fly.

    VERBATIM port of Cell B v2's chain_naive_hard semantics:
      state = E[start]
      for p in relations:
        state = W @ (state * R[p] * sq)
        last = argmax(E @ state)
      return last == target
    """
    n_dim = E.shape[1]
    W = ingest_hebbian_gpu(train_triples, E, R, sq, n_dim)
    hits = 0
    for q in queries:
        s, p1, p2, o_true, _x = q
        state = E[s].clone()
        last = s
        for p in [p1, p2]:
            state = W @ (state * R[p] * sq)
            last = int(torch.argmax(E @ state).item())
        if last == o_true:
            hits += 1
    return {"top1": round(hits / max(len(queries), 1), 4),
            "n_queries": len(queries),
            "mechanism": "beta_sweep_naive_hard_gpu"}


# ----------------------------------------------------------------------------
# Partition-oracle multi-hop cleanup (the load-bearing primitive)
# ----------------------------------------------------------------------------

def arm_part_oracle_at_depth(E: torch.Tensor, R: torch.Tensor, sq: float,
                               W: torch.Tensor,
                               chains_test: List[List[Tuple[int, int, int]]],
                               depth: int,
                               part_size: int) -> Dict[str, Any]:
    """Partition-oracle routed cleanup at given depth.

    For each cue (s, p), we know target_o; route argmax to E[target_part]
    (target_part = target_o // part_size). Chain through depth hops with
    per-hop oracle routing.

    GPU-batched argmax over partition slice.
    """
    n = len(chains_test)
    hits = 0
    per_step_hits = np.zeros(depth, dtype=np.int64)
    # Pre-slice E by partition for fast access (kept on GPU)
    n_partitions = E.shape[0] // part_size
    E_parts = [E[p * part_size:(p + 1) * part_size] for p in range(n_partitions)]
    for chain in chains_test:
        s = chain[0][0]
        for i in range(depth):
            p = chain[i][1]
            target_o = chain[i][2]
            target_part = target_o // part_size
            key = E[s] * R[p] * sq
            # W @ key, then E_parts[target_part] @ that, argmax
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


def _retrieve_1hop_naive(E: torch.Tensor, W: torch.Tensor, R: torch.Tensor,
                          s: int, p: int, sq: float) -> int:
    """VERBATIM port of pointer-chain v2 _retrieve_1hop for META_M7 reproduce."""
    key = E[s] * R[p] * sq
    return int(torch.argmax(E @ (W @ key)).item())


def arm_single_chain_naive(E: torch.Tensor, R: torch.Tensor, sq: float,
                            W: torch.Tensor,
                            chains_test: List[List[Tuple[int, int, int]]],
                            depth: int) -> Dict[str, Any]:
    """Forward-only per-step cleanup (no oracle routing).

    Used by META_M7 reproduce arm at depth=5 with W_pointer_v2.
    """
    n = len(chains_test)
    hits = 0
    per_step_hits = np.zeros(depth, dtype=np.int64)
    for chain in chains_test:
        s = chain[0][0]
        for i in range(depth):
            p = chain[i][1]
            s_pred = _retrieve_1hop_naive(E, W, R, s, p, sq)
            if s_pred == chain[i][2]:
                per_step_hits[i] += 1
            s = s_pred
        if s == chain[depth - 1][2]:
            hits += 1
    per_step_acc = (per_step_hits.astype(np.float32) / max(n, 1)).tolist()
    return {"top1": round(hits / max(n, 1), 4),
            "per_step_acc": [round(x, 4) for x in per_step_acc],
            "n_queries": n, "depth": depth,
            "mechanism": "verbatim_pointer_chain_v2_naive_forward_only"}


# ----------------------------------------------------------------------------
# Self-test (formula sanity check on tiny config)
# ----------------------------------------------------------------------------

def _selftest() -> None:
    g = np.random.default_rng(0)
    n = 512
    V = 40
    P = 4
    sq = math.sqrt(n)
    E = bipolar_gpu(V, n, g)
    R = bipolar_gpu(P, n, g)

    # T1: bipolar shapes + norm
    assert E.shape == (V, n) and R.shape == (P, n)
    assert abs(float(E[0].norm()) - 1.0) < 1e-4
    assert abs(float(R[0].norm()) - 1.0) < 1e-4

    # T2: BASELINE arm
    Rb = bipolar_gpu(max(BASELINE_V_P, 2), n, g)
    train_b, q_b = make_two_hop_chains_betasweep(15, V, g)
    r_base = arm_baseline_hrr_2hop(E, Rb, sq, train_b, q_b)
    assert 0.0 <= r_base["top1"] <= 1.0

    # T3: chain construction
    triples5, chains5 = make_deep_chains(8, V, P, max_depth=5, g=g, disallow_s=set())
    assert len(chains5) == 8
    assert len(triples5) == 8 * 5

    triples10, chains10 = make_deep_chains(8, V, P, max_depth=10, g=g, disallow_s=set())
    assert len(chains10) == 8
    assert len(triples10) == 8 * 10

    triples15, chains15 = make_deep_chains(8, V, P, max_depth=15, g=g, disallow_s=set())
    assert len(chains15) == 8
    assert len(triples15) == 8 * 15

    # T4: ingest + part_oracle on tiny config
    W5 = ingest_hebbian_gpu(triples5, E, R, sq, n)
    assert W5.shape == (n, n)
    assert torch.isfinite(W5).all()

    W10 = ingest_hebbian_gpu(triples10, E, R, sq, n)
    W15 = ingest_hebbian_gpu(triples15, E, R, sq, n)

    # T5: part_oracle at various depths. Need V divisible by n_partitions.
    n_parts_test = 4
    assert V % n_parts_test == 0
    part_sz_test = V // n_parts_test

    r5 = arm_part_oracle_at_depth(E, R, sq, W5, chains5, depth=5,
                                    part_size=part_sz_test)
    assert 0.0 <= r5["top1"] <= 1.0
    assert len(r5["per_step_acc"]) == 5

    r7 = arm_part_oracle_at_depth(E, R, sq, W10, [c[:7] for c in chains10],
                                    depth=7, part_size=part_sz_test)
    assert 0.0 <= r7["top1"] <= 1.0
    assert len(r7["per_step_acc"]) == 7

    r10 = arm_part_oracle_at_depth(E, R, sq, W10, chains10, depth=10,
                                     part_size=part_sz_test)
    assert 0.0 <= r10["top1"] <= 1.0
    assert len(r10["per_step_acc"]) == 10

    r15 = arm_part_oracle_at_depth(E, R, sq, W15, chains15, depth=15,
                                     part_size=part_sz_test)
    assert 0.0 <= r15["top1"] <= 1.0
    assert len(r15["per_step_acc"]) == 15

    # T6: META_M7 reproduce primitive
    r_repro = arm_single_chain_naive(E, R, sq, W10, [c[:5] for c in chains10], depth=5)
    assert 0.0 <= r_repro["top1"] <= 1.0

    # T7: bands LOCKED (regression on accidental band drift)
    assert HP_7HOP == 0.65 and HF_7HOP == 0.40
    assert HP_10HOP == 0.50 and HF_10HOP == 0.25
    assert HP_15HOP == 0.30 and HF_15HOP == 0.15
    assert CROSS_CELL_5HOP_LO == 0.935 and CROSS_CELL_5HOP_HI == 0.975
    assert META_M7_RAIL_LO == 0.08 and META_M7_RAIL_HI == 0.25
    assert BASELINE_SANITY_LO == 0.62 and BASELINE_SANITY_HI == 0.68

    # T8: PHASE_CV_MAX in (0, 0.20]
    assert 0.0 < PHASE_CV_MAX <= 0.20

    # T9: LLM call counter = 0 (substrate-only)
    assert _LLM_CALL_COUNTER[0] == 0

    # T10: GPU presence asserted for non-smoke mode (smoke OK on CPU)
    if RUN_MODE != "smoke":
        assert GPU_AVAIL, "FULL run requires GPU per Fix #24"

    print("[selftest] PASS base=%.3f part5=%.3f part7=%.3f part10=%.3f part15=%.3f "
          "repro=%.3f gpu=%s" % (
              r_base["top1"], r5["top1"], r7["top1"], r10["top1"], r15["top1"],
              r_repro["top1"], GPU_AVAIL), flush=True)


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

    if GPU_AVAIL:
        torch.cuda.reset_peak_memory_stats(DEVICE)

    print("  [seed=%d] building E (V_C=%d, N=%d)" % (
        seed, V_CONCEPTS, N_DIM), flush=True)
    E = bipolar_gpu(V_CONCEPTS, N_DIM, g)
    n_pred_total = max(BASELINE_V_P, V_PRED)
    R = bipolar_gpu(n_pred_total, N_DIM, g)

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

    # ===== BASELINE sanity =====
    t_arm = time.time()
    base_triples, base_queries = make_two_hop_chains_betasweep(
        BASELINE_N_LOCAL, V_CONCEPTS, g)
    r_baseline = arm_baseline_hrr_2hop(E, R, sq, base_triples, base_queries)
    r_baseline["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    out["arm_baseline_hrr_2hop"] = r_baseline
    baseline_ok = (BASELINE_SANITY_LO <= r_baseline["top1"] <= BASELINE_SANITY_HI)
    out["baseline_sanity_ok"] = baseline_ok
    print("  [seed=%d] BASELINE top1=%.4f (sanity_ok=%s; band=[%.2f,%.2f]) t=%.1fs" % (
        seed, r_baseline["top1"], baseline_ok,
        BASELINE_SANITY_LO, BASELINE_SANITY_HI,
        r_baseline["elapsed_s_arm"]), flush=True)

    # ===== Build W_v1_regime (1000 bindings; max_depth=5) =====
    t_arm = time.time()
    v1_triples, v1_chains = make_deep_chains(
        N_CHAINS_LOCAL, V_CONCEPTS, V_PRED, max_depth=V1_REGIME_MAX_DEPTH,
        g=g, disallow_s=set())
    W_v1 = ingest_hebbian_gpu(v1_triples, E, R, sq, N_DIM)
    print("  [seed=%d] W_v1_regime built (%d triples, max_depth=%d) t=%.1fs" % (
        seed, len(v1_triples), V1_REGIME_MAX_DEPTH,
        round(time.time() - t_arm, 2)), flush=True)

    # ===== Build W_pointer_v2 (2000 bindings; max_depth=10) =====
    t_arm = time.time()
    pv2_triples, pv2_chains = make_deep_chains(
        N_CHAINS_LOCAL, V_CONCEPTS, V_PRED, max_depth=POINTER_V2_MAX_DEPTH,
        g=g, disallow_s=set())
    W_pv2 = ingest_hebbian_gpu(pv2_triples, E, R, sq, N_DIM)
    print("  [seed=%d] W_pointer_v2 built (%d triples, max_depth=%d) t=%.1fs" % (
        seed, len(pv2_triples), POINTER_V2_MAX_DEPTH,
        round(time.time() - t_arm, 2)), flush=True)

    # ===== Build W_depth15_extended (3000 bindings; max_depth=15) =====
    t_arm = time.time()
    d15_triples, d15_chains = make_deep_chains(
        N_CHAINS_LOCAL, V_CONCEPTS, V_PRED, max_depth=DEPTH15_EXT_MAX_DEPTH,
        g=g, disallow_s=set())
    W_d15 = ingest_hebbian_gpu(d15_triples, E, R, sq, N_DIM)
    print("  [seed=%d] W_depth15_extended built (%d triples, max_depth=%d) t=%.1fs" % (
        seed, len(d15_triples), DEPTH15_EXT_MAX_DEPTH,
        round(time.time() - t_arm, 2)), flush=True)

    # ===== META_M7 ARM: reproduce pointer-chain-v2 at depth=5 on W_pointer_v2 =====
    t_arm = time.time()
    pv2_chains_d5 = [c[:5] for c in pv2_chains]
    r_reproduce = arm_single_chain_naive(E, R, sq, W_pv2, pv2_chains_d5, depth=5)
    r_reproduce["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    r_reproduce["W_n_bindings"] = len(pv2_triples)
    out["arm_reproduce_pointer_chain_v2_5hop"] = r_reproduce
    meta_m7_ok = (META_M7_RAIL_LO <= r_reproduce["top1"] <= META_M7_RAIL_HI)
    out["meta_m7_rail_ok"] = meta_m7_ok
    print("  [seed=%d] REPRODUCE_PV2_5HOP top1=%.4f per_step=%s "
          "(meta_m7_ok=%s; band=[%.2f,%.2f]) t=%.1fs" % (
              seed, r_reproduce["top1"], r_reproduce["per_step_acc"],
              meta_m7_ok, META_M7_RAIL_LO, META_M7_RAIL_HI,
              r_reproduce["elapsed_s_arm"]), flush=True)

    # ===== ARM_PART_ORACLE_5HOP (Cell B v2 cross-cell rail; W_v1_regime) =====
    t_arm = time.time()
    r_part5 = arm_part_oracle_at_depth(E, R, sq, W_v1, v1_chains, depth=5,
                                          part_size=PART_SIZE)
    r_part5["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    r_part5["W_n_bindings"] = len(v1_triples)
    r_part5["W_regime"] = "v1_regime_max_depth_5"
    out["arm_part_oracle_5hop"] = r_part5
    cross_cell_ok = (CROSS_CELL_5HOP_LO <= r_part5["top1"] <= CROSS_CELL_5HOP_HI)
    out["cross_cell_5hop_ok"] = cross_cell_ok
    print("  [seed=%d] PART_ORACLE_5HOP top1=%.4f per_step=%s "
          "(cross_cell_ok=%s; band=[%.3f,%.3f]; target=%.4f) t=%.1fs" % (
              seed, r_part5["top1"], r_part5["per_step_acc"],
              cross_cell_ok, CROSS_CELL_5HOP_LO, CROSS_CELL_5HOP_HI,
              CROSS_CELL_5HOP_TARGET, r_part5["elapsed_s_arm"]), flush=True)

    # ===== ARM_PART_ORACLE_7HOP (W_pointer_v2; chains[:7]) =====
    t_arm = time.time()
    pv2_chains_d7 = [c[:7] for c in pv2_chains]
    r_part7 = arm_part_oracle_at_depth(E, R, sq, W_pv2, pv2_chains_d7, depth=7,
                                          part_size=PART_SIZE)
    r_part7["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    r_part7["W_n_bindings"] = len(pv2_triples)
    r_part7["W_regime"] = "pointer_v2_max_depth_10"
    out["arm_part_oracle_7hop"] = r_part7
    print("  [seed=%d] PART_ORACLE_7HOP top1=%.4f per_step=%s "
          "(HP=%.2f, HF=%.2f) t=%.1fs" % (
              seed, r_part7["top1"], r_part7["per_step_acc"],
              HP_7HOP, HF_7HOP, r_part7["elapsed_s_arm"]), flush=True)

    # ===== ARM_PART_ORACLE_10HOP (W_pointer_v2; full depth=10) =====
    t_arm = time.time()
    r_part10 = arm_part_oracle_at_depth(E, R, sq, W_pv2, pv2_chains, depth=10,
                                           part_size=PART_SIZE)
    r_part10["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    r_part10["W_n_bindings"] = len(pv2_triples)
    r_part10["W_regime"] = "pointer_v2_max_depth_10"
    out["arm_part_oracle_10hop"] = r_part10
    print("  [seed=%d] PART_ORACLE_10HOP top1=%.4f per_step=%s "
          "(HP=%.2f, HF=%.2f) t=%.1fs" % (
              seed, r_part10["top1"], r_part10["per_step_acc"],
              HP_10HOP, HF_10HOP, r_part10["elapsed_s_arm"]), flush=True)

    # ===== ARM_PART_ORACLE_15HOP (W_depth15_extended) =====
    t_arm = time.time()
    r_part15 = arm_part_oracle_at_depth(E, R, sq, W_d15, d15_chains, depth=15,
                                           part_size=PART_SIZE)
    r_part15["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    r_part15["W_n_bindings"] = len(d15_triples)
    r_part15["W_regime"] = "depth15_extended_max_depth_15"
    out["arm_part_oracle_15hop"] = r_part15
    print("  [seed=%d] PART_ORACLE_15HOP top1=%.4f per_step=%s "
          "(HP=%.2f, HF=%.2f) t=%.1fs" % (
              seed, r_part15["top1"], r_part15["per_step_acc"],
              HP_15HOP, HF_15HOP, r_part15["elapsed_s_arm"]), flush=True)

    # GPU mem peak
    if GPU_AVAIL:
        peak_bytes = torch.cuda.max_memory_allocated(DEVICE)
        out["gpu_max_mem_alloc_mb"] = round(peak_bytes / 1e6, 2)
        print("  [seed=%d] GPU peak alloc: %.2f MB" % (
            seed, out["gpu_max_mem_alloc_mb"]), flush=True)
        # Free Ws to allow next seed to fit
        del W_v1, W_pv2, W_d15
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

    baseline = mean_top1("arm_baseline_hrr_2hop")
    reproduce = mean_top1("arm_reproduce_pointer_chain_v2_5hop")
    part5 = mean_top1("arm_part_oracle_5hop")
    part7 = mean_top1("arm_part_oracle_7hop")
    part10 = mean_top1("arm_part_oracle_10hop")
    part15 = mean_top1("arm_part_oracle_15hop")

    cv5 = cv_top1("arm_part_oracle_5hop")
    cv7 = cv_top1("arm_part_oracle_7hop")
    cv10 = cv_top1("arm_part_oracle_10hop")
    cv15 = cv_top1("arm_part_oracle_15hop")

    sanity_breached = sum(1 for p in per_seed
                            if not p.get("baseline_sanity_ok", False))
    meta_m7_breached = sum(1 for p in per_seed
                            if not p.get("meta_m7_rail_ok", False))
    cross_cell_breached = sum(1 for p in per_seed
                                if not p.get("cross_cell_5hop_ok", False))

    summ = (
        "BASELINE=%.4f (sanity_breach=%d/%d) "
        "REPRO_PV2=%.4f (meta_m7_breach=%d/%d) "
        "PART_5HOP=%.4f (cv=%.3f, cross_cell_breach=%d/%d; target=%.4f) "
        "PART_7HOP=%.4f (cv=%.3f) "
        "PART_10HOP=%.4f (cv=%.3f) "
        "PART_15HOP=%.4f (cv=%.3f)"
    ) % (
        baseline, sanity_breached, len(per_seed),
        reproduce, meta_m7_breached, len(per_seed),
        part5, cv5, cross_cell_breached, len(per_seed), CROSS_CELL_5HOP_TARGET,
        part7, cv7, part10, cv10, part15, cv15,
    )

    half = max(1, (len(per_seed) + 1) // 2)

    # Sanity pre-emption
    if sanity_breached >= half:
        return "SANITY_BREACH", "SANITY_BREACH_BASELINE_OUT_OF_BAND: " + summ
    if meta_m7_breached >= half:
        return "META_M7_BREACH", "META_M7_BREACH_REPRODUCE_OUT_OF_BAND: " + summ
    if cross_cell_breached >= half:
        return "CROSS_CELL_BREACH", "CROSS_CELL_BREACH_PART_5HOP_OUT_OF_BAND: " + summ

    # Phase-point classification
    def hp_at_depth(mean_val: float, cv_val: float, hp: float) -> bool:
        if math.isnan(mean_val):
            return False
        cv_ok = math.isnan(cv_val) or cv_val <= PHASE_CV_MAX
        return (mean_val >= hp) and cv_ok

    def hf_at_depth(mean_val: float, hf: float) -> bool:
        return (not math.isnan(mean_val)) and (mean_val < hf)

    pass5 = (not math.isnan(part5)) and (part5 >= CROSS_CELL_5HOP_LO)
    pass7 = hp_at_depth(part7, cv7, HP_7HOP)
    pass10 = hp_at_depth(part10, cv10, HP_10HOP)
    pass15 = hp_at_depth(part15, cv15, HP_15HOP)

    fail7 = hf_at_depth(part7, HF_7HOP)
    fail10 = hf_at_depth(part10, HF_10HOP)
    fail15 = hf_at_depth(part15, HF_15HOP)

    if pass5 and pass7 and pass10 and pass15:
        return ("CHAIN_GRADE_DEPTH_EXTENDS",
                "CHAIN_GRADE_DEPTH_EXTENDS_ALL_4_PHASE_POINTS_HARD_PASS: " + summ)
    if pass5 and pass7 and pass10 and fail15:
        return ("PARTIAL_DEPTH_EXTENDS_TO_10",
                "PARTIAL_DEPTH_EXTENDS_TO_10_CLIFF_BETWEEN_10_AND_15: " + summ)
    if pass5 and pass7 and not pass10 and not pass15:
        return ("PARTIAL_DEPTH_EXTENDS_TO_7",
                "PARTIAL_DEPTH_EXTENDS_TO_7_CLIFF_BETWEEN_7_AND_10: " + summ)
    if pass5 and (fail7 or not pass7) and (fail10 or not pass10) \
            and (fail15 or not pass15):
        return ("DEPTH_5_IS_CEILING",
                "DEPTH_5_IS_CEILING_CELL_B_V2_WAS_THE_LIMIT: " + summ)
    return ("MIDDLE_BAND",
            "MIDDLE_BAND_MIXED_PHASE_POINTS: " + summ)


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


if __name__ == "__main__":
    print("[config] anchor=%s mode=%s seeds=%s N=%d gpu=%s | %s" % (
        ANCHOR_NAME, RUN_MODE, SEEDS, N_DIM, GPU_AVAIL, CONFIG_VERSION),
        flush=True)
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
        "gpu_avail": GPU_AVAIL,
        "gpu_name": GPU_NAME,
        "DESIGN_NOTE": (
            "PHASE_DIAGRAM_DEPTH_EXTENSION: Cell B v2's depth=5 phase point at "
            "PART_ORACLE=0.9550 reproduced as cross-cell rail (W_v1_regime; "
            "band=[0.935,0.975] = target+/-0.02). META_M7 reproduce arm at "
            "depth=5 on W_pointer_v2 retains pointer-chain-v2's band [0.08,0.25]. "
            "Three NEW phase points (7HOP/10HOP/15HOP) probe the depth phase "
            "boundary: predicted by 0.95-per-step compounding (~0.70/~0.60/~0.46). "
            "TWO-W canonical (W_v1_regime + W_pointer_v2) plus one extended W "
            "(W_depth15_extended) for 15HOP because pointer_v2's max_depth=10 "
            "doesn't contain 15-hop chains. Disallow_s=set() preserved across "
            "all three W constructions. Verdict tiers the phase boundary cleanly: "
            "CHAIN_GRADE_DEPTH_EXTENDS (all 4 PASS) / PARTIAL_DEPTH_EXTENDS_TO_10 "
            "(cliff 10-15) / PARTIAL_DEPTH_EXTENDS_TO_7 (cliff 7-10) / "
            "DEPTH_5_IS_CEILING. GPU-required at full per Fix #24."
        ),
    }
    write_metrics(out_dir, metrics, results=per_seed)
    print("[done] metrics.json written (%d seeds, %.1fs)" % (
        len(per_seed), metrics["elapsed_s"]), flush=True)
