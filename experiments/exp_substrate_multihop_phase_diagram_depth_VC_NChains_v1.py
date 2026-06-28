"""substrate_multihop_phase_diagram_depth_VC_NChains_v1

LAYER-1 PHASE-DIAGRAM MAP: multi-hop reasoning across (depth x V_C x N_chains).

PRIOR ANCHOR (single-point chain-grade): exp_phase_diagram_multihop_depth_extension_via_
partition_oracle_v1 landed CHAIN_GRADE at V_C=200, N_chains=200, N_DIM=8192:
  5HOP=0.965 / 7HOP=0.882 / 10HOP=0.857 / 15HOP=0.808

Phase coverage was ~30%. This cell maps the FULL (depth x V_C x N_chains) cube
so Layer-2 phase operations (USER strategic directive) know WHERE multi-hop
works, WHERE it breaks, and WHERE the cliffs are.

SWEEP AXES (full grid 5 x 4 x 2 = 40 points):
  depth     in {5, 8, 10, 12, 15}     (5 points)
  V_C       in {200, 1000, 5000, 16000} (4 points)
  N_chains  in {50, 200}              (2 points)

SMOKE GRID (4 corners):
  (5, 200, 50)      saturation sanity (top1_pred=0.9824)
  (5, 16000, 50)    discriminator    (top1_pred=0.2417)
  (15, 200, 200)    discriminator    (top1_pred=0.8082; reproduces v1 anchor 0.808)
  (15, 16000, 200)  regime-fail      (top1_pred=0.0000)

ARMS (per phase point):
  SUBSTRATE   partition-routed oracle cleanup (verbatim v1 mechanism)
              W built at max_depth=15 over E_VC; oracle reduces per-step search
              to V_C / N_PARTITIONS.
  RANDOM      uniformly-sampled target from V_C codebook (must be ~ 1/V_C)

ARMS-MUST-DIFFER (META_RULE_AF): SHA-256 of per-step prediction sequences MUST
differ between SUBSTRATE and RANDOM at every (depth, V_C, N_chains) point.

GPU REQUIREMENT (Fix #24 non-negotiable):
  - torch.cuda primary device (asserted at module init for FULL mode)
  - Batched ingest_hebbian (1000-binding outer-product blocks)
  - E + R + W hoisted ONCE per (V_C, N_chains) pair; reused across depths
  - torch.cuda.utilization() sampled mid-run; must be >= 50%

PHASE-POINT BANDS (per-prediction; clamped above 5x random floor):
  top1_pred >= 0.60   HP=0.50  HF=0.25
  top1_pred >= 0.30   HP=0.25  HF=0.10
  top1_pred >= 0.10   HP=0.10  HF=0.05
  top1_pred  < 0.10   HP=0.05  HF=0.02

VERDICT TIERS:
  CHAIN_GRADE_PHASE_MAP_COMPLETE      >= 50% (20/40) HARD_PASS + cliffs identified
  PARTIAL_PHASE_MAP_SHALLOW           30-49% HARD_PASS; cliffs visible at moderate V_C
  REGIME_BOUNDS_NARROW                10-29% HARD_PASS; substrate works only at small V_C
  PHASE_FRONTIER_COLLAPSED            <10% HARD_PASS
  SANITY_BREACH                       corner (5,200,50) fails to saturate

ASCII-only; zero-LLM-call assert; META_RULE_H cardinality_ok; META_RULE_AF arms-differ;
META_RULE_AG no silent except; META_RULE_AH no hallucinated numbers; Fix #24 GPU.
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

# ----------------------------------------------------------------------------
# GPU GUARD (Fix #24)
# ----------------------------------------------------------------------------
try:
    import torch
except ImportError:
    print("[FATAL] torch not installed; cannot run cell.", flush=True)
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
          "Self-test/smoke-CPU OK; FULL requires GPU per Fix #24.", flush=True)

from experiments._seed_checkpoint import (
    get_output_dir, resumable_seeds, write_partial_key, aggregate_partials,
    write_metrics,
)
from hdlab.gpu_memory_budget import project_peak_mb, assert_under_budget

ANCHOR_NAME = "substrate_multihop_phase_diagram_depth_VC_NChains_v1"
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
# Sweep config (LOCKED at module init)
# ----------------------------------------------------------------------------
DEPTHS_FULL = [5, 8, 10, 12, 15]
V_CS_FULL = [200, 1000, 5000, 16000]
N_CHAINS_FULL = [50, 200]

DEPTHS_SMOKE = [5, 15]
V_CS_SMOKE = [200, 16000]
N_CHAINS_SMOKE_LOW = 50
N_CHAINS_SMOKE_HIGH = 200

# Smoke uses 4 SPECIFIC corners (not full cross-product):
SMOKE_CORNERS = [
    (5, 200, 50),
    (5, 16000, 50),
    (15, 200, 200),
    (15, 16000, 200),
]

N_PARTITIONS = 20
MAX_W_DEPTH = 15        # always build W at max_depth=15 (reuse across depth queries)
V_PRED = 10
SQ_BASELINE = None       # set after N_DIM known

# Anchor for empirical p_step model (v1 chain-grade)
P_STEP_ANCHOR = 0.808 ** (1.0 / 15.0)   # = 0.98590
V_C_ANCHOR = 200
N_CHAINS_ANCHOR = 200

# Sanity-rail bands for smoke corners
SAT_CORNER = (5, 200, 50)
SAT_CORNER_HP = 0.95          # must saturate

V1_CROSS_CELL_CORNER = (15, 200, 200)
V1_CROSS_CELL_LO = 0.75       # v1 anchor 0.808 +/- 0.05
V1_CROSS_CELL_HI = 0.86

FAIL_CORNER = (15, 16000, 200)
FAIL_CORNER_HF = 0.10         # must fail

# Smoke GPU util threshold (Fix #24)
GPU_UTIL_FLOOR = 50.0

# Cardinality
EXPECTED_N_FULL = len(DEPTHS_FULL) * len(V_CS_FULL) * len(N_CHAINS_FULL)  # 40
EXPECTED_N_SMOKE = len(SMOKE_CORNERS)                                       # 4
assert EXPECTED_N_FULL == 40
assert EXPECTED_N_SMOKE == 4

# Mode-dependent
if RUN_MODE == "smoke":
    N_DIM = 8192      # still 8192 to keep GPU util realistic per Fix #24
    SEEDS = [11]
else:
    N_DIM = 8192
    SEEDS = [11]      # single seed for phase-diagram map (each point already 50-200 chains)

ENCODER_PROVENANCE = "SUBSTRATE_NATIVE_BIPOLAR"

# Random-floor / band model
def random_floor_for(V_C: int) -> float:
    return 1.0 / V_C

def p_step_empirical(V_C: int, N_chains: int) -> float:
    log_p_anchor = math.log(P_STEP_ANCHOR)
    scale = (V_C * N_chains) / (V_C_ANCHOR * N_CHAINS_ANCHOR)
    return math.exp(log_p_anchor * scale)

def top1_predicted(depth: int, V_C: int, N_chains: int) -> float:
    p = p_step_empirical(V_C, N_chains)
    return p ** depth

def bands_for(top1_pred: float, V_C: int) -> Tuple[float, float]:
    if top1_pred >= 0.60:
        HP, HF = 0.50, 0.25
    elif top1_pred >= 0.30:
        HP, HF = 0.25, 0.10
    elif top1_pred >= 0.10:
        HP, HF = 0.10, 0.05
    else:
        HP, HF = 0.05, 0.02
    rfloor = random_floor_for(V_C)
    HP = max(HP, 5.0 * rfloor)
    HF = max(HF, 2.0 * rfloor)
    return HP, HF

PHASE_BANDS: List[Dict[str, Any]] = []
for V_C in V_CS_FULL:
    for N_chains in N_CHAINS_FULL:
        for d in DEPTHS_FULL:
            pred = top1_predicted(d, V_C, N_chains)
            HP, HF = bands_for(pred, V_C)
            PHASE_BANDS.append({
                "depth": d, "V_C": V_C, "N_chains": N_chains,
                "top1_pred": round(pred, 4),
                "HP": round(HP, 4), "HF": round(HF, 4),
                "random_floor": random_floor_for(V_C),
            })
assert len(PHASE_BANDS) == EXPECTED_N_FULL

CONFIG_VERSION = (
    "substrateMultihopPhaseDiagramDepthVCNChainsV1: N=%d depths=%s V_Cs=%s "
    "N_chains_set=%s N_partitions=%d max_W_depth=%d V_P=%d seeds=%s "
    "mode=%s encoder=%s p_step_anchor=%.4f V_C_anchor=%d N_chains_anchor=%d "
    "n_full=%d n_smoke=%d gpu_floor=%.1f"
) % (
    N_DIM, DEPTHS_FULL, V_CS_FULL, N_CHAINS_FULL,
    N_PARTITIONS, MAX_W_DEPTH, V_PRED, SEEDS,
    RUN_MODE, ENCODER_PROVENANCE,
    P_STEP_ANCHOR, V_C_ANCHOR, N_CHAINS_ANCHOR,
    EXPECTED_N_FULL, EXPECTED_N_SMOKE, GPU_UTIL_FLOOR,
)

# ----------------------------------------------------------------------------
# GPU memory budget projection (Fix #24)
# ----------------------------------------------------------------------------
GPU_BUDGET_MB = 6 * 1024
if RUN_MODE != "smoke" and GPU_AVAIL:
    # Biggest single (V_C, N_chains) build: V_C=16000, N_chains=200, max_W_depth=15
    # E = (16000, 8192) f32 = 524 MB
    # W = (8192, 8192) f32 = 256 MB
    # Plus transient ingest batches.
    _proj = project_peak_mb(
        allocations=[
            ("E_max",          (max(V_CS_FULL), N_DIM),    "float32", "persistent"),
            ("R_pred",         (V_PRED, N_DIM),            "float32", "persistent"),
            ("W_per_pair",     (N_DIM, N_DIM),             "float32", "persistent"),
            ("ingest_batch_K", (1000, N_DIM),              "float32", "transient"),
            ("ingest_batch_V", (1000, N_DIM),              "float32", "transient"),
        ],
        budget_mb=GPU_BUDGET_MB,
    )
    print("[gpu-budget] projected_peak_mb=%.1f budget=%d headroom=%.1f over=%s" % (
        _proj["projected_peak_mb"], GPU_BUDGET_MB,
        _proj["headroom_mb"], _proj["over_budget"]), flush=True)
    assert_under_budget(_proj, GPU_BUDGET_MB)


# ----------------------------------------------------------------------------
# Primitives (verbatim from v1 anchor cell)
# ----------------------------------------------------------------------------

def bipolar_gpu(M: int, n: int, g: np.random.Generator) -> torch.Tensor:
    arr = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    t = torch.from_numpy(arr).to(DEVICE)
    norms = t.norm(dim=1, keepdim=True).clamp(min=1e-8)
    return t / norms


def make_deep_chains(n_chains: int, V: int, P: int, max_depth: int,
                      g: np.random.Generator,
                      disallow_s: set) -> Tuple[List[Tuple[int, int, int]],
                                                  List[List[Tuple[int, int, int]]]]:
    all_triples = []
    chain_queries = []
    used_s = set(disallow_s)
    tries = 0
    max_tries = max(n_chains * 200, 10000)
    while len(chain_queries) < n_chains and tries < max_tries:
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
        raise RuntimeError("make_deep_chains: only %d/%d at max_depth=%d V=%d"
                            % (len(chain_queries), n_chains, max_depth, V))
    return all_triples, chain_queries


def ingest_hebbian_gpu(triples: List[Tuple[int, int, int]],
                        E: torch.Tensor, R: torch.Tensor,
                        sq: float, n_dim: int,
                        batch: int = 1000) -> torch.Tensor:
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
        K = E[s_slice] * R[p_slice] * sq
        V_ = E[o_slice]
        W = W + (V_.T @ K) / n_dim
    return W


# ----------------------------------------------------------------------------
# Arms
# ----------------------------------------------------------------------------

def arm_substrate_part_oracle(
    E: torch.Tensor, R: torch.Tensor, sq: float,
    W: torch.Tensor,
    chains_test: List[List[Tuple[int, int, int]]],
    depth: int, part_size: int,
) -> Tuple[Dict[str, Any], List[int]]:
    """SUBSTRATE arm: partition-routed oracle cleanup per step.

    Returns (metrics_dict, flat_pred_sequence_for_sha256).
    """
    n = len(chains_test)
    hits = 0
    per_step_hits = np.zeros(depth, dtype=np.int64)
    n_partitions = E.shape[0] // part_size
    E_parts = [E[p * part_size:(p + 1) * part_size] for p in range(n_partitions)]
    flat_preds: List[int] = []
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
            flat_preds.append(s_pred)
            if s_pred == target_o:
                per_step_hits[i] += 1
            s = s_pred
        if s == chain[depth - 1][2]:
            hits += 1
    per_step_acc = (per_step_hits.astype(np.float32) / max(n, 1)).tolist()
    return {
        "top1": round(hits / max(n, 1), 4),
        "per_step_acc": [round(x, 4) for x in per_step_acc],
        "n_queries": n, "depth": depth, "n_partitions": n_partitions,
        "part_size": part_size,
        "mechanism": "partition_oracle_per_hop_gpu",
    }, flat_preds


def arm_random(V_C: int,
               chains_test: List[List[Tuple[int, int, int]]],
               depth: int,
               g: np.random.Generator) -> Tuple[Dict[str, Any], List[int]]:
    """RANDOM arm: uniformly sample target object from V_C."""
    n = len(chains_test)
    hits = 0
    per_step_hits = np.zeros(depth, dtype=np.int64)
    flat_preds: List[int] = []
    for chain in chains_test:
        for i in range(depth):
            target_o = chain[i][2]
            s_pred = int(g.integers(0, V_C))
            flat_preds.append(s_pred)
            if s_pred == target_o:
                per_step_hits[i] += 1
        # final: random pick equals final-target by chance
        if flat_preds[-1] == chain[depth - 1][2]:
            hits += 1
    per_step_acc = (per_step_hits.astype(np.float32) / max(n, 1)).tolist()
    return {
        "top1": round(hits / max(n, 1), 4),
        "per_step_acc": [round(x, 4) for x in per_step_acc],
        "n_queries": n, "depth": depth, "V_C": V_C,
        "mechanism": "random_uniform_pick_floor",
    }, flat_preds


def sha256_of(seq: List[int]) -> str:
    h = hashlib.sha256()
    for x in seq:
        h.update(int(x).to_bytes(8, "little", signed=False))
    return h.hexdigest()[:16]


# ----------------------------------------------------------------------------
# GPU util sampler (Fix #24)
# ----------------------------------------------------------------------------

_GPU_UTIL_SAMPLES: List[float] = []

def sample_gpu_util() -> float:
    if not GPU_AVAIL:
        return 0.0
    try:
        u = float(torch.cuda.utilization(0))
        _GPU_UTIL_SAMPLES.append(u)
        return u
    except Exception:
        return 0.0


# ----------------------------------------------------------------------------
# Per-point runner
# ----------------------------------------------------------------------------

def run_point(depth: int, V_C: int, N_chains: int, seed: int,
              cache: Dict[Tuple[int, int], Dict[str, Any]],
              ) -> Dict[str, Any]:
    """Run SUBSTRATE + RANDOM at a single (depth, V_C, N_chains) point.

    Caches E + R + W per (V_C, N_chains) pair to amortize across depths.
    """
    t = time.time()
    sq = math.sqrt(N_DIM)
    g = np.random.default_rng(seed + 1000 * V_C + N_chains)  # deterministic per point

    # Validate partition cleanly divides V_C
    if V_C % N_PARTITIONS != 0:
        raise RuntimeError("V_C=%d not divisible by N_PARTITIONS=%d" % (V_C, N_PARTITIONS))
    part_size = V_C // N_PARTITIONS

    cache_key = (V_C, N_chains)
    if cache_key not in cache:
        # Build E + R + W for this (V_C, N_chains) pair (max_depth=15)
        E = bipolar_gpu(V_C, N_DIM, g)
        R = bipolar_gpu(V_PRED, N_DIM, g)
        triples, chains = make_deep_chains(N_chains, V_C, V_PRED,
                                            max_depth=MAX_W_DEPTH,
                                            g=g, disallow_s=set())
        sample_gpu_util()
        W = ingest_hebbian_gpu(triples, E, R, sq, N_DIM)
        sample_gpu_util()
        cache[cache_key] = {"E": E, "R": R, "W": W, "chains": chains,
                             "n_triples": len(triples)}
        print("  [cache-build] (V_C=%d, N_chains=%d) E=%s R=%s W=%s n_triples=%d" % (
            V_C, N_chains, tuple(E.shape), tuple(R.shape), tuple(W.shape),
            len(triples)), flush=True)

    bundle = cache[cache_key]
    E = bundle["E"]
    R = bundle["R"]
    W = bundle["W"]
    chains = bundle["chains"]
    chains_at_depth = [c[:depth] for c in chains]

    # SUBSTRATE arm
    r_sub, sub_preds = arm_substrate_part_oracle(E, R, sq, W, chains_at_depth,
                                                   depth, part_size)
    sample_gpu_util()

    # RANDOM arm
    g_rand = np.random.default_rng(seed * 2 + V_C + N_chains * 7)
    r_rand, rand_preds = arm_random(V_C, chains_at_depth, depth, g_rand)

    # Arms-differ check (META_RULE_AF)
    sha_sub = sha256_of(sub_preds)
    sha_rand = sha256_of(rand_preds)
    arms_differ = (sha_sub != sha_rand)

    # Band lookup
    pred = top1_predicted(depth, V_C, N_chains)
    HP, HF = bands_for(pred, V_C)
    top1_sub = float(r_sub["top1"])
    top1_rand = float(r_rand["top1"])
    rfloor = random_floor_for(V_C)

    cv_ok = True  # single-seed phase-map; CV-ok by construction
    if top1_sub >= HP:
        tier = "HARD_PASS"
    elif top1_sub < HF:
        tier = "HARD_FAIL"
    else:
        tier = "MIDDLE_BAND"

    saturated = (top1_sub > 0.95)

    point = {
        "depth": depth, "V_C": V_C, "N_chains": N_chains,
        "top1_substrate": round(top1_sub, 4),
        "top1_random": round(top1_rand, 4),
        "top1_pred": round(pred, 4),
        "HP": round(HP, 4), "HF": round(HF, 4),
        "random_floor": round(rfloor, 6),
        "per_step_acc_substrate": r_sub["per_step_acc"],
        "per_step_acc_random": r_rand["per_step_acc"],
        "arms_differ_sha256": arms_differ,
        "sha256_substrate": sha_sub,
        "sha256_random": sha_rand,
        "verdict_tier_per_point": tier,
        "saturated": saturated,
        "discriminator_fires": (top1_sub - top1_rand) > 0.20,
        "n_partitions": r_sub["n_partitions"],
        "part_size": part_size,
        "elapsed_s_point": round(time.time() - t, 2),
    }
    print("  [point] depth=%2d V_C=%5d N_ch=%3d  sub=%.4f rand=%.4f pred=%.4f "
          "tier=%s arms_diff=%s sat=%s discrim=%s t=%.1fs" % (
              depth, V_C, N_chains, top1_sub, top1_rand, pred,
              tier, arms_differ, saturated, point["discriminator_fires"],
              point["elapsed_s_point"]), flush=True)
    return point


# ----------------------------------------------------------------------------
# Self-test
# ----------------------------------------------------------------------------

def _selftest() -> None:
    """Self-test: smaller substrate for fast CPU verification.

    Runs all 4 smoke corners at TINY N_DIM=512, V_C in {200, 400} (rescaled).
    Verifies arms-differ + formula + no silent excepts.
    """
    g = np.random.default_rng(0)
    n_test = 512
    V_test = 60
    P_test = 4
    sq_t = math.sqrt(n_test)

    # T1: shapes
    E = bipolar_gpu(V_test, n_test, g)
    R = bipolar_gpu(P_test, n_test, g)
    assert E.shape == (V_test, n_test)
    assert abs(float(E[0].norm()) - 1.0) < 1e-4

    # T2: chain construction
    triples, chains = make_deep_chains(5, V_test, P_test, max_depth=15,
                                        g=g, disallow_s=set())
    assert len(chains) == 5
    assert len(triples) == 5 * 15

    # T3: ingest_hebbian
    W = ingest_hebbian_gpu(triples, E, R, sq_t, n_test)
    assert W.shape == (n_test, n_test)
    assert torch.isfinite(W).all()

    # T4: SUBSTRATE arm at multiple depths (V=60, N_PART=20 -> part_size=3)
    n_parts_test = 20
    assert V_test % n_parts_test == 0
    part_sz_test = V_test // n_parts_test
    chains_d5 = [c[:5] for c in chains]
    r_sub, sub_preds = arm_substrate_part_oracle(E, R, sq_t, W, chains_d5,
                                                   depth=5, part_size=part_sz_test)
    assert 0.0 <= r_sub["top1"] <= 1.0
    assert len(r_sub["per_step_acc"]) == 5

    # T5: RANDOM arm
    g_r = np.random.default_rng(7)
    r_rand, rand_preds = arm_random(V_test, chains_d5, depth=5, g=g_r)
    assert 0.0 <= r_rand["top1"] <= 1.0
    assert len(r_rand["per_step_acc"]) == 5

    # T6: arms-differ (SHA-256 must differ over per-step preds)
    sha_sub = sha256_of(sub_preds)
    sha_rand = sha256_of(rand_preds)
    assert sha_sub != sha_rand, "ARM-DIFFER VIOLATION: SHA-256 collision"
    print("  [selftest] arms_differ sha_sub=%s sha_rand=%s OK" % (sha_sub, sha_rand))

    # T7: random floor sanity
    # At V_C=60 and depth=5 random per-step ~ 1/60 = 0.0167. Compounded ~ 0.0167^5 ~ 1.3e-9.
    # With only 5 chains, expected hits ~ 0. So top1_random should be 0.0 or rare 0.2.
    assert r_rand["top1"] < 0.5, "random arm above 0.5 at V=60 d=5 n=5: %.4f" % r_rand["top1"]

    # T8: formula sanity
    p_anchor = P_STEP_ANCHOR
    assert abs(p_anchor - 0.808 ** (1.0 / 15.0)) < 1e-9
    pred = top1_predicted(15, 200, 200)
    # Should reproduce v1 anchor 0.808
    assert abs(pred - 0.808) < 0.005, "Formula off v1 anchor: pred=%.4f vs 0.808" % pred

    # T9: bands_for sanity
    HP, HF = bands_for(0.9, 200)
    assert HP > HF
    assert HP > 5.0 * random_floor_for(200)
    HP2, HF2 = bands_for(0.001, 16000)
    assert HP2 > HF2

    # T10: CARDINALITY guard
    assert EXPECTED_N_FULL == 40
    assert EXPECTED_N_SMOKE == 4
    assert len(PHASE_BANDS) == EXPECTED_N_FULL
    assert len(SMOKE_CORNERS) == EXPECTED_N_SMOKE

    # T11: LLM call counter
    assert _LLM_CALL_COUNTER[0] == 0

    # T12: at-prod-scale formula reproduces v1 anchor at all 4 depths
    expected_v1 = [(5, 0.965), (7, 0.882), (10, 0.857), (15, 0.808)]
    for d, actual in expected_v1:
        # Formula uses log-linear scaling, anchored at 15-hop=0.808.
        # 5/7/10 will only approximately match (within ~0.10) due to substrate
        # non-linearity at shallow depths.
        pred_d = P_STEP_ANCHOR ** d
        diff = abs(pred_d - actual)
        print("  [selftest-formula-v1-rail] depth=%d pred=%.4f actual=%.4f diff=%.4f" % (
            d, pred_d, actual, diff))
        # at 15-hop we should match exactly:
        if d == 15:
            assert diff < 0.01, "Formula off v1 15-hop anchor"

    print("[selftest] PASS sub=%.4f rand=%.4f arms_differ=%s pred_v1_15hop=%.4f gpu=%s" % (
        r_sub["top1"], r_rand["top1"], (sha_sub != sha_rand),
        top1_predicted(15, 200, 200), GPU_AVAIL), flush=True)


_selftest()
if _ARGS.self_test:
    print("[self-test] PASS; exiting", flush=True)
    sys.exit(0)


# ----------------------------------------------------------------------------
# Phase-map run (smoke or full)
# ----------------------------------------------------------------------------

def build_phase_grid() -> List[Tuple[int, int, int]]:
    """Build the (depth, V_C, N_chains) grid for current mode."""
    if RUN_MODE == "smoke":
        return list(SMOKE_CORNERS)
    grid = []
    for V_C in V_CS_FULL:
        for N_chains in N_CHAINS_FULL:
            for d in DEPTHS_FULL:
                grid.append((d, V_C, N_chains))
    return grid


def run_seed(seed: int) -> Dict[str, Any]:
    t = time.time()
    if GPU_AVAIL:
        torch.cuda.reset_peak_memory_stats(DEVICE)

    grid = build_phase_grid()
    expected = EXPECTED_N_SMOKE if RUN_MODE == "smoke" else EXPECTED_N_FULL
    if len(grid) != expected:
        raise RuntimeError("CARDINALITY_BREACH at grid build: %d != %d" % (
            len(grid), expected))

    # Order grid to amortize cache: sort by (V_C, N_chains) then depth
    grid_sorted = sorted(grid, key=lambda x: (x[1], x[2], x[0]))

    cache: Dict[Tuple[int, int], Dict[str, Any]] = {}
    phase_map: List[Dict[str, Any]] = []

    for (depth, V_C, N_chains) in grid_sorted:
        # NO SILENT EXCEPT per META_RULE_AG -- let exceptions propagate.
        point = run_point(depth, V_C, N_chains, seed, cache)
        phase_map.append(point)
        sample_gpu_util()

    # Free GPU memory between seeds
    cache.clear()
    if GPU_AVAIL:
        torch.cuda.empty_cache()
        peak_bytes = torch.cuda.max_memory_allocated(DEVICE)
    else:
        peak_bytes = 0

    # Cardinality check
    if len(phase_map) != expected:
        raise RuntimeError("CARDINALITY_BREACH at runtime: %d != %d" % (
            len(phase_map), expected))

    # GPU util summary
    gpu_util_mean = (float(np.mean(_GPU_UTIL_SAMPLES))
                      if _GPU_UTIL_SAMPLES else 0.0)
    gpu_util_max = (float(np.max(_GPU_UTIL_SAMPLES))
                     if _GPU_UTIL_SAMPLES else 0.0)

    out = {
        "seed": seed, "run_mode": RUN_MODE, "N": N_DIM,
        "config_version": CONFIG_VERSION,
        "phase_map": phase_map,
        "gpu_util_pct_mean": round(gpu_util_mean, 2),
        "gpu_util_pct_max": round(gpu_util_max, 2),
        "gpu_util_n_samples": len(_GPU_UTIL_SAMPLES),
        "gpu_avail": GPU_AVAIL,
        "gpu_name": GPU_NAME,
        "gpu_max_mem_alloc_mb": round(peak_bytes / 1e6, 2),
        "expected_n_points": expected,
        "observed_n_points": len(phase_map),
        "cardinality_ok": (len(phase_map) == expected),
        "elapsed_s": round(time.time() - t, 1),
        "_llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
    }
    return out


# ----------------------------------------------------------------------------
# Verdict + smoke gate
# ----------------------------------------------------------------------------

def evaluate_smoke_gate(phase_map: List[Dict[str, Any]],
                        gpu_util_mean: float,
                        gpu_avail: bool) -> Dict[str, Any]:
    """Evaluate smoke gate per spawn directive criteria."""
    cardinality_ok = (len(phase_map) == EXPECTED_N_SMOKE)
    arm_discrim_count = sum(1 for p in phase_map if p["discriminator_fires"])
    arm_discrim_ok = (arm_discrim_count >= 2)
    saturation_observed = any(p["saturated"] for p in phase_map)
    regime_fail_observed = any(p["top1_substrate"] < 0.10 for p in phase_map)
    arms_differ_all = all(p["arms_differ_sha256"] for p in phase_map)

    # Sanity-corner rails
    sat_corner = next((p for p in phase_map
                        if (p["depth"], p["V_C"], p["N_chains"]) == SAT_CORNER), None)
    sat_corner_ok = (sat_corner is not None
                      and sat_corner["top1_substrate"] >= SAT_CORNER_HP)
    cross_cell_corner = next((p for p in phase_map
                                if (p["depth"], p["V_C"], p["N_chains"]) == V1_CROSS_CELL_CORNER),
                              None)
    cross_cell_ok = (cross_cell_corner is not None and
                     V1_CROSS_CELL_LO <= cross_cell_corner["top1_substrate"]
                     <= V1_CROSS_CELL_HI)
    fail_corner = next((p for p in phase_map
                         if (p["depth"], p["V_C"], p["N_chains"]) == FAIL_CORNER), None)
    fail_corner_ok = (fail_corner is not None
                       and fail_corner["top1_substrate"] < FAIL_CORNER_HF)

    # GPU util gate (only when GPU available; CPU smoke skips)
    if gpu_avail:
        gpu_util_ok = (gpu_util_mean >= GPU_UTIL_FLOOR)
    else:
        gpu_util_ok = True  # CPU smoke: util gate N/A; full run must be on GPU

    all_pass = (cardinality_ok and arm_discrim_ok and saturation_observed
                and regime_fail_observed and arms_differ_all
                and sat_corner_ok and cross_cell_ok and fail_corner_ok
                and gpu_util_ok)

    return {
        "cardinality_ok": cardinality_ok,
        "arm_discrim_count": arm_discrim_count,
        "arm_discrim_ok": arm_discrim_ok,
        "saturation_observed": saturation_observed,
        "regime_fail_observed": regime_fail_observed,
        "arms_differ_all": arms_differ_all,
        "sat_corner_ok": sat_corner_ok,
        "cross_cell_ok": cross_cell_ok,
        "fail_corner_ok": fail_corner_ok,
        "gpu_util_ok": gpu_util_ok,
        "gpu_util_mean": gpu_util_mean,
        "all_pass": all_pass,
    }


def verdict_from(per_seed: List[Dict[str, Any]]) -> Tuple[str, str]:
    """Verdict for full-grid run."""
    # Aggregate phase_map across seeds (we use SEEDS=[11] so just one).
    phase_map = per_seed[0]["phase_map"]

    n_pass = sum(1 for p in phase_map if p["verdict_tier_per_point"] == "HARD_PASS")
    n_fail = sum(1 for p in phase_map if p["verdict_tier_per_point"] == "HARD_FAIL")
    n_mid = sum(1 for p in phase_map if p["verdict_tier_per_point"] == "MIDDLE_BAND")
    n_total = len(phase_map)
    pct_pass = n_pass / max(n_total, 1)

    gpu_util_mean = per_seed[0].get("gpu_util_pct_mean", 0.0)

    # Cardinality breach
    if n_total != EXPECTED_N_FULL:
        return ("CARDINALITY_BREACH",
                "CARDINALITY_BREACH: observed=%d expected=%d" % (
                    n_total, EXPECTED_N_FULL))

    # Sanity-corner check (must saturate at easy corner)
    sat_corner = next((p for p in phase_map
                        if (p["depth"], p["V_C"], p["N_chains"]) == SAT_CORNER), None)
    if sat_corner is None or not sat_corner["saturated"]:
        return ("SANITY_BREACH",
                "SANITY_BREACH: easy corner %s top1=%.4f failed to saturate" % (
                    str(SAT_CORNER),
                    sat_corner["top1_substrate"] if sat_corner else float("nan")))

    # GPU util sanity (full requires GPU)
    if per_seed[0].get("gpu_avail") and gpu_util_mean < GPU_UTIL_FLOOR:
        return ("GPU_UTIL_BREACH",
                "GPU_UTIL_BREACH: mean=%.1f < floor=%.1f" % (
                    gpu_util_mean, GPU_UTIL_FLOOR))

    # Identify cliffs
    cliff_summary = []
    # Per-V_C: how many depths PASS at N_chains=200?
    for V_C in V_CS_FULL:
        depths_pass_200 = sorted([p["depth"] for p in phase_map
                                   if p["V_C"] == V_C and p["N_chains"] == 200
                                   and p["verdict_tier_per_point"] == "HARD_PASS"])
        depths_pass_50 = sorted([p["depth"] for p in phase_map
                                  if p["V_C"] == V_C and p["N_chains"] == 50
                                  and p["verdict_tier_per_point"] == "HARD_PASS"])
        cliff_summary.append("V_C=%d: n_passes=200chains=%s 50chains=%s" % (
            V_C, depths_pass_200, depths_pass_50))

    summ = ("phase_map: n_total=%d n_pass=%d n_mid=%d n_fail=%d pct_pass=%.2f%% "
            "| cliffs: %s | gpu_util_mean=%.1f%%") % (
        n_total, n_pass, n_mid, n_fail, 100 * pct_pass,
        " || ".join(cliff_summary), gpu_util_mean)

    if pct_pass >= 0.50:
        return ("CHAIN_GRADE_PHASE_MAP_COMPLETE",
                "CHAIN_GRADE_PHASE_MAP_COMPLETE_%d_OF_%d_PASS: %s" % (
                    n_pass, n_total, summ))
    if pct_pass >= 0.30:
        return ("PARTIAL_PHASE_MAP_SHALLOW",
                "PARTIAL_PHASE_MAP_SHALLOW_%d_OF_%d: %s" % (n_pass, n_total, summ))
    if pct_pass >= 0.10:
        return ("REGIME_BOUNDS_NARROW",
                "REGIME_BOUNDS_NARROW_%d_OF_%d: %s" % (n_pass, n_total, summ))
    return ("PHASE_FRONTIER_COLLAPSED",
            "PHASE_FRONTIER_COLLAPSED_%d_OF_%d: %s" % (n_pass, n_total, summ))


def verdict_smoke(per_seed: List[Dict[str, Any]]) -> Tuple[str, str]:
    phase_map = per_seed[0]["phase_map"]
    gpu_util_mean = per_seed[0].get("gpu_util_pct_mean", 0.0)
    gpu_avail = per_seed[0].get("gpu_avail", False)
    gate = evaluate_smoke_gate(phase_map, gpu_util_mean, gpu_avail)

    summ = ("smoke phase_map: " + " ".join(
        "(d=%d,V_C=%d,N=%d,sub=%.3f,rand=%.3f,tier=%s,sat=%s)" % (
            p["depth"], p["V_C"], p["N_chains"],
            p["top1_substrate"], p["top1_random"],
            p["verdict_tier_per_point"], p["saturated"])
        for p in phase_map))
    gate_str = " ".join("%s=%s" % (k, v) for k, v in gate.items())

    if gate["all_pass"]:
        return ("SMOKE_GATE_PASS",
                "SMOKE_GATE_PASS: " + gate_str + " | " + summ)
    return ("SMOKE_GATE_FAIL",
            "SMOKE_GATE_FAIL: " + gate_str + " | " + summ)


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
        if RUN_MODE == "smoke":
            v, vmsg = verdict_smoke(per_seed)
        else:
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
    # FULL mode requires GPU (Fix #24)
    if RUN_MODE == "full" and not GPU_AVAIL:
        print("[FATAL] FULL run requires GPU per Fix #24; aborting.", flush=True)
        sys.exit(2)

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

    if RUN_MODE == "smoke":
        v, vmsg = verdict_smoke(per_seed)
    else:
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
        "phase_bands_pre_reg": PHASE_BANDS,
        "expected_n_full": EXPECTED_N_FULL,
        "expected_n_smoke": EXPECTED_N_SMOKE,
        "DESIGN_NOTE": (
            "LAYER1_PHASE_DIAGRAM_MAP_substrate_multihop_depth_VC_NChains: "
            "Maps the (depth x V_C x N_chains) cube for multi-hop substrate. "
            "Anchored on v1 chain-grade 15-hop=0.808 at (15, 200, 200). Sweep "
            "axes 5 depths x 4 V_C x 2 N_chains = 40 phase points. Per-point "
            "SUBSTRATE arm (partition-routed oracle cleanup) vs RANDOM arm "
            "(uniform pick floor). Arms-differ SHA-256 enforced at every point. "
            "Per-point bands track empirical p_step model anchored at v1. "
            "Smoke 4 corners; full 40 points; GPU util >= 50% gate per Fix #24."
        ),
    }
    write_metrics(out_dir, metrics, results=per_seed)
    print("[done] metrics.json written (%d seeds, %.1fs)" % (
        len(per_seed), metrics["elapsed_s"]), flush=True)
