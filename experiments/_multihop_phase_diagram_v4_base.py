"""Shared engine for substrate_multihop_phase_diagram_depth_VC_NChains_v4.

CHUNKED across 3 seed siblings (seed_7 / seed_13 / seed_19). Each sibling
imports this module and calls run_one_seed(seed_int).

Pre-reg: preregs/2026-06-28_substrate_multihop_phase_diagram_depth_VC_NChains_v4.md
Supersedes: v1 / v3 (test-design issue per Skunkworks atomization eb7cfc4c,
atom 0bfdac9e73a27ed5).

V4 FIXES:
  1. Sweep effective_V_C directly (the per-step cleanup search size), not
     nominal V_C. N_PARTITIONS=4 fixed; V_C = 4 * effective_V_C.
  2. Bands derived from EMPIRICAL p_step back-solved from v3 data, NOT from
     cone-formula extrapolation. Cite Skunkworks commit + atom in code.
  3. sample_gpu_util() no-silent-except (META_RULE_J): on NVML failure record
     gpu_util=NaN + reason='NVML_UNAVAILABLE' and let runner fail Fix #24 gate
     LOUDLY, not silently.
  4. Three arms (per spawn directive): SUBSTRATE_BASELINE (no oracle; full V_C
     search), PARTITION_ORACLE (eff_V_C search; ground-truth partition),
     RANDOM_PARTITION (eff_V_C search; random partition; floor).

Sweep: effective_V_C in {200, 800, 4000, 16000} x depth in {5, 10, 15}
       = 4 x 3 = 12 points per seed.
Smoke: 4 corner points only (cardinality_ok=4).
N_chains = 200 fixed (production load on W matrix).

ASCII-only; no emojis; self-contained.
Author: exp_dev 2026-06-28.
"""
from __future__ import annotations

import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import hashlib
import json
import math
import os
import time
import traceback
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

# ---------------------------------------------------------------------------
# GPU GUARD (Fix #24)
# ---------------------------------------------------------------------------
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

ANCHOR_NAME_PREFIX = "substrate_multihop_phase_diagram_depth_VC_NChains_v4"

# Pre-reg LOCKED sweep
EFF_V_CS_FULL = [200, 800, 4000, 16000]
DEPTHS_FULL = [5, 10, 15]
N_CHAINS_FIXED = 200
N_PARTITIONS = 4               # FIXED across all points (cleanup search size = eff_V_C)
N_DIM = 8192                   # production scale per USER 2026-06-22 + Fix #24
V_PRED = 10                    # number of predicate / role atoms (relations)
MAX_W_DEPTH = 15               # always build W at max_depth=15

# Smoke corners (4 of 12 full points)
# Empirical from v3 (cited in pre-reg): part_size=10 -> p_step~0.987;
# part_size=800 -> p_step~0.999. Conservative model: p_step degrades only at
# eff_V_C >= 4000 where W resolution saturates.
SMOKE_CORNERS = [
    (5,  200),    # SAT_CORNER:           all arms saturate (PART_ORACLE >= 0.95)
    (15, 200),    # DISCRIM_LOW_EFFV:     PART+SUB saturate; RANDOM tiny
    (5,  16000),  # DISCRIM_HIGH_EFFV:    PART_ORACLE strong; SUB_BASELINE WEAK; RANDOM tiny
    (15, 16000),  # CLIFF_CORNER:         PART_ORACLE moderate; SUB_BASELINE collapse; RANDOM tiny
]

# Sanity rail thresholds
SAT_CORNER = (5, 200)
SAT_CORNER_HP = 0.90           # PART_ORACLE at SAT_CORNER >= 0.90

CLIFF_CORNER = (15, 16000)
CLIFF_BASELINE_HF = 0.40       # SUB_BASELINE at CLIFF_CORNER < 0.40 (proves V_C scaling cliff)

# GPU util gate (Fix #24)
GPU_UTIL_FLOOR = 50.0

# Cardinality
EXPECTED_N_FULL = len(EFF_V_CS_FULL) * len(DEPTHS_FULL)   # 12
EXPECTED_N_SMOKE = len(SMOKE_CORNERS)                      # 4
assert EXPECTED_N_FULL == 12
assert EXPECTED_N_SMOKE == 4

# Per-arm META_AM tolerance
META_AM_TOL = 0.02

# Discriminator threshold for smoke
DISCRIM_THRESHOLD = 0.20       # PART_ORACLE - RANDOM_PARTITION > 0.20

# LLM-call counter (substrate-only assert)
_LLM_CALL_COUNTER = [0]

# Skunkworks v3 atomization reference (load-bearing)
SKUNKWORKS_V3_COMMIT = "eb7cfc4c"
SKUNKWORKS_V3_ATOM = "0bfdac9e73a27ed5"


# ---------------------------------------------------------------------------
# Empirical p_step model (back-solved from v3 data; META_RULE_AH)
# ---------------------------------------------------------------------------
def p_step_empirical(eff_V_C: int) -> float:
    """Empirical per-step accuracy for PARTITION_ORACLE arm.

    Source: data/exp_substrate_multihop_phase_diagram_depth_VC_NChains_v1_smoke_v3/metrics.json
    (Skunkworks-verified commit eb7cfc4c; atom 0bfdac9e73a27ed5).

    Back-solved p_step = top1 ^ (1/depth):
      part_size=10  N_chains=200  p_step=0.987 (v3 corner 2; depth=15 top1=0.820)
      part_size=10  N_chains=50   p_step=0.988 (v3 corner 1; depth=5  top1=0.940)
      part_size=800 N_chains=50   p_step=1.000 (v3 corner 3; depth=5  top1=1.000)
      part_size=800 N_chains=200  p_step=0.9993 (v3 corner 4; depth=15 top1=0.990)

    Empirical p_step is roughly INDEPENDENT of eff_V_C in the 10-800 range
    (substrate-internal; W storage handles V_C up to 16000 cleanly with
    N_chains=200). Conservative extrapolation for eff_V_C > 800 with margin.
    """
    if eff_V_C <= 800:
        return 0.99
    if eff_V_C <= 4000:
        return 0.98
    return 0.95


def top1_pred_part_oracle(depth: int, eff_V_C: int) -> float:
    """Predicted top1 for PARTITION_ORACLE arm."""
    return p_step_empirical(eff_V_C) ** depth


def random_floor_eff_v_c(eff_V_C: int) -> float:
    return 1.0 / max(1, eff_V_C)


def random_floor_full_v_c(V_C: int) -> float:
    return 1.0 / max(1, V_C)


def bands_for(top1_pred: float, eff_V_C: int) -> Tuple[float, float]:
    """HP / HF per top1_pred; clamped above 5x random floor (eff_V_C)."""
    if top1_pred >= 0.60:
        HP, HF = 0.50, 0.25
    elif top1_pred >= 0.30:
        HP, HF = 0.25, 0.10
    elif top1_pred >= 0.10:
        HP, HF = 0.10, 0.05
    else:
        HP, HF = 0.05, 0.02
    rfloor = random_floor_eff_v_c(eff_V_C)
    HP = max(HP, 5.0 * rfloor)
    HF = max(HF, 2.0 * rfloor)
    return HP, HF


# ---------------------------------------------------------------------------
# GPU util sampler (FIXED per META_RULE_J / Fix #24 v4 spec)
# ---------------------------------------------------------------------------
_GPU_UTIL_SAMPLES: List[float] = []
_GPU_UTIL_FAIL_REASON: List[str] = []   # captures FIRST failure reason (loudly)


def sample_gpu_util_safe() -> float:
    """Sample GPU utilization. NO SILENT EXCEPT (META_RULE_J).

    On NVML failure, append the reason to _GPU_UTIL_FAIL_REASON so the runner
    knows the gate failed transparently (not silently as 0.0).

    Returns float or NaN on failure. The returned float is appended to
    _GPU_UTIL_SAMPLES ONLY on success; the failure-reason path does NOT pad
    the samples list with fake zeros.
    """
    if not GPU_AVAIL:
        if not _GPU_UTIL_FAIL_REASON:
            _GPU_UTIL_FAIL_REASON.append("CUDA_UNAVAILABLE")
        return float("nan")
    try:
        u = float(torch.cuda.utilization(0))
    except (RuntimeError, AttributeError, ModuleNotFoundError) as e:
        # NVML is the typical source of these failures. RuntimeError covers
        # NVML init failures; AttributeError covers older torch / no NVML;
        # ModuleNotFoundError covers missing pynvml. Log the FIRST one and
        # return NaN; do NOT append to _GPU_UTIL_SAMPLES (avoid lying-zero).
        if not _GPU_UTIL_FAIL_REASON:
            _GPU_UTIL_FAIL_REASON.append("NVML_UNAVAILABLE: %s: %s" % (
                type(e).__name__, str(e)[:120]))
            # NOTE: explicit print so the runner log shows the failure
            print("[gpu-util] NVML_UNAVAILABLE: %s: %s" % (
                type(e).__name__, str(e)[:120]), flush=True)
        return float("nan")
    _GPU_UTIL_SAMPLES.append(u)
    return u


# ---------------------------------------------------------------------------
# Primitives (verbatim from v1 anchor, GPU-batched)
# ---------------------------------------------------------------------------
def bipolar_gpu(M: int, n: int, g: np.random.Generator) -> torch.Tensor:
    arr = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    t = torch.from_numpy(arr).to(DEVICE)
    norms = t.norm(dim=1, keepdim=True).clamp(min=1e-8)
    return t / norms


def make_deep_chains(n_chains: int, V: int, P: int, max_depth: int,
                      g: np.random.Generator,
                      disallow_s: set) -> Tuple[List[Tuple[int, int, int]],
                                                List[List[Tuple[int, int, int]]]]:
    """Generate n_chains random walks of length max_depth over V codewords."""
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
    """Batched Hebbian outer-product ingest on GPU (Fix #24 batched matmul)."""
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
        K = E[s_idx[b:e]] * R[p_idx[b:e]] * sq
        V_ = E[o_idx[b:e]]
        W = W + (V_.T @ K) / n_dim
    return W


def sha256_of(seq: List[int]) -> str:
    h = hashlib.sha256()
    for x in seq:
        h.update(int(x).to_bytes(8, "little", signed=False))
    return h.hexdigest()[:16]


# ---------------------------------------------------------------------------
# Arms (3, per spawn directive)
# ---------------------------------------------------------------------------
def arm_partition_oracle(E: torch.Tensor, R: torch.Tensor, sq: float,
                          W: torch.Tensor,
                          chains_test: List[List[Tuple[int, int, int]]],
                          depth: int, part_size: int,
                          n_partitions: int) -> Tuple[Dict[str, Any], List[int]]:
    """PARTITION_ORACLE arm: goal-conditioning with ground-truth target partition.

    Per-step cleanup over part_size codewords (the partition containing the target).
    """
    n = len(chains_test)
    hits = 0
    per_step_hits = np.zeros(depth, dtype=np.int64)
    E_parts = [E[p * part_size:(p + 1) * part_size] for p in range(n_partitions)]
    flat_preds: List[int] = []
    for chain in chains_test:
        s = chain[0][0]
        for i in range(depth):
            p_rel = chain[i][1]
            target_o = chain[i][2]
            target_part = target_o // part_size
            key = E[s] * R[p_rel] * sq
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


def arm_substrate_baseline(E: torch.Tensor, R: torch.Tensor, sq: float,
                            W: torch.Tensor,
                            chains_test: List[List[Tuple[int, int, int]]],
                            depth: int,
                            V_C: int) -> Tuple[Dict[str, Any], List[int]]:
    """SUBSTRATE_BASELINE arm: per-step cleanup over FULL V_C codebook (no oracle).

    Per-step search size = V_C (full codebook). Upper bound at small V_C;
    falls off as V_C grows beyond W's effective resolution.
    """
    n = len(chains_test)
    hits = 0
    per_step_hits = np.zeros(depth, dtype=np.int64)
    flat_preds: List[int] = []
    for chain in chains_test:
        s = chain[0][0]
        for i in range(depth):
            p_rel = chain[i][1]
            target_o = chain[i][2]
            key = E[s] * R[p_rel] * sq
            state = W @ key
            scores = E @ state                 # full V_C search
            s_pred = int(torch.argmax(scores).item())
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
        "n_queries": n, "depth": depth, "V_C": V_C,
        "mechanism": "substrate_baseline_full_VC_cleanup_gpu",
    }, flat_preds


def arm_random_partition(E: torch.Tensor, R: torch.Tensor, sq: float,
                          W: torch.Tensor,
                          chains_test: List[List[Tuple[int, int, int]]],
                          depth: int, part_size: int,
                          n_partitions: int,
                          g: np.random.Generator) -> Tuple[Dict[str, Any],
                                                            List[int]]:
    """RANDOM_PARTITION arm: per-step cleanup over a RANDOM partition (floor).

    Random partition assignment; sanity floor. Per-step accuracy bounded
    above by 1/N_PARTITIONS (chance of right partition) times in-partition
    cleanup success. The 'partition' for this arm is chosen at random
    per-step, ignoring the ground-truth target_part.
    """
    n = len(chains_test)
    hits = 0
    per_step_hits = np.zeros(depth, dtype=np.int64)
    E_parts = [E[p * part_size:(p + 1) * part_size] for p in range(n_partitions)]
    flat_preds: List[int] = []
    for chain in chains_test:
        s = chain[0][0]
        for i in range(depth):
            p_rel = chain[i][1]
            target_o = chain[i][2]
            # RANDOM partition (NOT the ground-truth one)
            random_part = int(g.integers(0, n_partitions))
            key = E[s] * R[p_rel] * sq
            state = W @ key
            scores = E_parts[random_part] @ state
            local_idx = int(torch.argmax(scores).item())
            s_pred = random_part * part_size + local_idx
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
        "mechanism": "random_partition_floor_gpu",
    }, flat_preds


# ---------------------------------------------------------------------------
# Per-point runner
# ---------------------------------------------------------------------------
def run_point(depth: int, eff_V_C: int, seed: int,
              cache: Dict[int, Dict[str, Any]]) -> Dict[str, Any]:
    """Run all 3 arms at a single (depth, eff_V_C) point.

    Caches E + R + W per eff_V_C (V_C is derived deterministically from eff_V_C
    via V_C = N_PARTITIONS * eff_V_C; cache key is eff_V_C).
    """
    t = time.time()
    V_C = N_PARTITIONS * eff_V_C
    sq = math.sqrt(N_DIM)
    g = np.random.default_rng(seed + 1000 * eff_V_C + N_CHAINS_FIXED)

    if V_C % N_PARTITIONS != 0:
        raise RuntimeError("V_C=%d not divisible by N_PARTITIONS=%d" % (
            V_C, N_PARTITIONS))
    part_size = V_C // N_PARTITIONS
    assert part_size == eff_V_C, "part_size %d != eff_V_C %d" % (part_size, eff_V_C)

    if eff_V_C not in cache:
        E = bipolar_gpu(V_C, N_DIM, g)
        R = bipolar_gpu(V_PRED, N_DIM, g)
        triples, chains = make_deep_chains(N_CHAINS_FIXED, V_C, V_PRED,
                                            max_depth=MAX_W_DEPTH,
                                            g=g, disallow_s=set())
        sample_gpu_util_safe()
        W = ingest_hebbian_gpu(triples, E, R, sq, N_DIM)
        sample_gpu_util_safe()
        cache[eff_V_C] = {"E": E, "R": R, "W": W, "chains": chains,
                          "n_triples": len(triples), "V_C": V_C}
        print("  [cache-build] eff_V_C=%d V_C=%d E=%s R=%s W=%s n_triples=%d" % (
            eff_V_C, V_C, tuple(E.shape), tuple(R.shape), tuple(W.shape),
            len(triples)), flush=True)

    bundle = cache[eff_V_C]
    E = bundle["E"]
    R = bundle["R"]
    W = bundle["W"]
    chains = bundle["chains"]
    chains_at_depth = [c[:depth] for c in chains]

    # SUBSTRATE_BASELINE arm (full V_C search)
    r_sub, sub_preds = arm_substrate_baseline(E, R, sq, W, chains_at_depth,
                                                depth, V_C)
    sample_gpu_util_safe()

    # PARTITION_ORACLE arm (eff_V_C search; ground-truth partition)
    r_part, part_preds = arm_partition_oracle(E, R, sq, W, chains_at_depth,
                                                depth, part_size, N_PARTITIONS)
    sample_gpu_util_safe()

    # RANDOM_PARTITION arm (eff_V_C search; random partition; floor)
    g_rand = np.random.default_rng(seed * 2 + eff_V_C + 7)
    r_rand, rand_preds = arm_random_partition(E, R, sq, W, chains_at_depth,
                                                depth, part_size, N_PARTITIONS,
                                                g_rand)

    # Arms-differ check (META_RULE_AF; 3 distinct hashes)
    sha_sub = sha256_of(sub_preds)
    sha_part = sha256_of(part_preds)
    sha_rand = sha256_of(rand_preds)
    arms_differ = (len({sha_sub, sha_part, sha_rand}) == 3)

    pred_part = top1_pred_part_oracle(depth, eff_V_C)
    HP, HF = bands_for(pred_part, eff_V_C)
    top1_sub = float(r_sub["top1"])
    top1_part = float(r_part["top1"])
    top1_rand = float(r_rand["top1"])
    rfloor_eff = random_floor_eff_v_c(eff_V_C)
    rfloor_full = random_floor_full_v_c(V_C)

    # PART_ORACLE arm is the primary tier track (per pre-reg)
    if top1_part >= HP:
        tier = "HARD_PASS"
    elif top1_part < HF:
        tier = "HARD_FAIL"
    else:
        tier = "MIDDLE_BAND"

    saturated = (top1_part > 0.95)
    discriminator_fires = (top1_part - top1_rand) > DISCRIM_THRESHOLD

    point = {
        "depth": depth, "eff_V_C": eff_V_C, "V_C": V_C, "N_chains": N_CHAINS_FIXED,
        "N_PARTITIONS": N_PARTITIONS, "part_size": part_size,
        "top1_substrate_baseline": round(top1_sub, 4),
        "top1_partition_oracle": round(top1_part, 4),
        "top1_random_partition": round(top1_rand, 4),
        "top1_pred_part_oracle": round(pred_part, 4),
        "HP": round(HP, 4), "HF": round(HF, 4),
        "random_floor_eff_V_C": round(rfloor_eff, 6),
        "random_floor_full_V_C": round(rfloor_full, 6),
        "per_step_acc_substrate_baseline": r_sub["per_step_acc"],
        "per_step_acc_partition_oracle": r_part["per_step_acc"],
        "per_step_acc_random_partition": r_rand["per_step_acc"],
        "arms_differ_sha256": arms_differ,
        "sha256_substrate_baseline": sha_sub,
        "sha256_partition_oracle": sha_part,
        "sha256_random_partition": sha_rand,
        "verdict_tier_per_point": tier,
        "saturated": saturated,
        "discriminator_fires": discriminator_fires,
        "elapsed_s_point": round(time.time() - t, 2),
    }
    print(("  [point] d=%2d effV_C=%5d V_C=%6d  "
           "sub=%.4f part=%.4f rand=%.4f pred=%.4f tier=%s "
           "arms_diff=%s sat=%s discrim=%s t=%.1fs") % (
        depth, eff_V_C, V_C, top1_sub, top1_part, top1_rand, pred_part,
        tier, arms_differ, saturated, discriminator_fires,
        point["elapsed_s_point"]), flush=True)
    return point


# ---------------------------------------------------------------------------
# Verdict computation
# ---------------------------------------------------------------------------
def smoke_verdict(phase_map: List[Dict[str, Any]],
                   gpu_util_mean: float,
                   gpu_util_n_samples: int,
                   gpu_util_reason: str,
                   gpu_avail: bool) -> Tuple[str, str, Dict[str, Any]]:
    cardinality_ok = (len(phase_map) == EXPECTED_N_SMOKE)
    arm_discrim_count = sum(1 for p in phase_map if p["discriminator_fires"])
    arm_discrim_ok = (arm_discrim_count >= 2)
    arms_differ_all = all(p["arms_differ_sha256"] for p in phase_map)

    # META_AM: PART_ORACLE >= RANDOM_PARTITION at every point (tol 0.02)
    am_breaches = [(p["depth"], p["eff_V_C"]) for p in phase_map
                   if p["top1_partition_oracle"] < p["top1_random_partition"] + META_AM_TOL]
    am_ok = len(am_breaches) == 0

    # Sanity rails
    sat_corner = next((p for p in phase_map
                        if (p["depth"], p["eff_V_C"]) == SAT_CORNER), None)
    sat_ok = (sat_corner is not None
              and sat_corner["top1_partition_oracle"] >= SAT_CORNER_HP)
    cliff_corner = next((p for p in phase_map
                          if (p["depth"], p["eff_V_C"]) == CLIFF_CORNER), None)
    cliff_ok = (cliff_corner is not None
                and cliff_corner["top1_substrate_baseline"] < CLIFF_BASELINE_HF)

    # GPU util gate (Fix #24; v4 fixed: NaN failure is LOUD not silent)
    if gpu_avail:
        # If we got NaN (no samples), the gate FAILS LOUDLY (META_RULE_J).
        if gpu_util_n_samples == 0 or math.isnan(gpu_util_mean):
            gpu_util_ok = False
        else:
            gpu_util_ok = (gpu_util_mean >= GPU_UTIL_FLOOR)
    else:
        gpu_util_ok = True  # CPU smoke: util gate N/A; full requires GPU

    extra = {
        "cardinality_ok": cardinality_ok,
        "n_points": len(phase_map),
        "n_expected": EXPECTED_N_SMOKE,
        "arm_discrim_count": arm_discrim_count,
        "arm_discrim_ok": arm_discrim_ok,
        "arms_differ_all": arms_differ_all,
        "META_AM_breaches": am_breaches,
        "META_AM_ok": am_ok,
        "sat_corner_ok": sat_ok,
        "sat_corner_top1": (sat_corner["top1_partition_oracle"]
                             if sat_corner else None),
        "cliff_corner_ok": cliff_ok,
        "cliff_corner_substrate_baseline": (
            cliff_corner["top1_substrate_baseline"] if cliff_corner else None),
        "gpu_util_ok": gpu_util_ok,
        "gpu_util_mean": gpu_util_mean,
        "gpu_util_n_samples": gpu_util_n_samples,
        "gpu_util_reason": gpu_util_reason,
        "gpu_avail": gpu_avail,
    }

    all_pass = (cardinality_ok and arm_discrim_ok and arms_differ_all
                and am_ok and sat_ok and cliff_ok and gpu_util_ok)

    summ = " ".join(
        "(d=%d,effV=%d,sub=%.3f,part=%.3f,rand=%.3f,tier=%s)" % (
            p["depth"], p["eff_V_C"], p["top1_substrate_baseline"],
            p["top1_partition_oracle"], p["top1_random_partition"],
            p["verdict_tier_per_point"])
        for p in phase_map)
    gate_str = " ".join("%s=%s" % (k, v) for k, v in extra.items()
                        if k not in ("META_AM_breaches",))

    if all_pass:
        return ("HARD_PASS", "SMOKE_GATE_PASS: " + gate_str + " | " + summ, extra)
    return ("HARD_FAIL", "SMOKE_GATE_FAIL: " + gate_str + " | " + summ, extra)


def full_verdict(phase_map: List[Dict[str, Any]],
                  gpu_util_mean: float,
                  gpu_util_n_samples: int,
                  gpu_util_reason: str,
                  gpu_avail: bool) -> Tuple[str, str, Dict[str, Any]]:
    cardinality_ok = (len(phase_map) == EXPECTED_N_FULL)
    if not cardinality_ok:
        return ("HARD_FAIL", "CARDINALITY_BREACH n=%d expected=%d" % (
            len(phase_map), EXPECTED_N_FULL), {"cardinality_ok": False})

    n_pass = sum(1 for p in phase_map if p["verdict_tier_per_point"] == "HARD_PASS")
    n_fail = sum(1 for p in phase_map if p["verdict_tier_per_point"] == "HARD_FAIL")
    n_mid = sum(1 for p in phase_map if p["verdict_tier_per_point"] == "MIDDLE_BAND")
    n_total = len(phase_map)
    pct_pass = n_pass / max(n_total, 1)

    # Sanity rails on PART_ORACLE arm
    sat_corner = next((p for p in phase_map
                        if (p["depth"], p["eff_V_C"]) == SAT_CORNER), None)
    if sat_corner is None or not sat_corner["saturated"]:
        return ("HARD_FAIL", "SANITY_BREACH: SAT_CORNER %s failed to saturate (top1_part=%.4f)" % (
            str(SAT_CORNER),
            sat_corner["top1_partition_oracle"] if sat_corner else float("nan")),
                {"cardinality_ok": True, "sat_corner_failed": True})

    # GPU util sanity (full requires GPU)
    if gpu_avail and (gpu_util_n_samples == 0 or math.isnan(gpu_util_mean)):
        return ("HARD_FAIL",
                "GPU_UTIL_BREACH: n_samples=%d mean=%s reason=%s" % (
                    gpu_util_n_samples, gpu_util_mean, gpu_util_reason),
                {"gpu_util_ok": False})
    if gpu_avail and gpu_util_mean < GPU_UTIL_FLOOR:
        return ("HARD_FAIL",
                "GPU_UTIL_BREACH: mean=%.1f < floor=%.1f" % (
                    gpu_util_mean, GPU_UTIL_FLOOR), {"gpu_util_ok": False})

    # Cliff summary
    cliff_summary = []
    for eff_V_C in EFF_V_CS_FULL:
        depths_pass = sorted([p["depth"] for p in phase_map
                              if p["eff_V_C"] == eff_V_C
                              and p["verdict_tier_per_point"] == "HARD_PASS"])
        cliff_summary.append("effV_C=%d:pass_depths=%s" % (eff_V_C, depths_pass))

    extra = {
        "cardinality_ok": True,
        "n_total": n_total, "n_pass": n_pass, "n_mid": n_mid, "n_fail": n_fail,
        "pct_pass": round(pct_pass, 3),
        "gpu_util_mean": gpu_util_mean,
        "gpu_util_n_samples": gpu_util_n_samples,
        "gpu_util_reason": gpu_util_reason,
        "cliff_summary": cliff_summary,
    }
    summ = ("n_total=%d n_pass=%d n_mid=%d n_fail=%d pct=%.1f%% | cliffs: %s | gpu_util=%.1f%%" % (
        n_total, n_pass, n_mid, n_fail, 100 * pct_pass,
        " || ".join(cliff_summary), gpu_util_mean))

    if pct_pass >= 0.50:
        return ("CHAIN_GRADE_PHASE_MAP_COMPLETE",
                "CHAIN_GRADE_PHASE_MAP_COMPLETE %d_of_%d: %s" % (n_pass, n_total, summ),
                extra)
    if pct_pass >= 0.30:
        return ("PARTIAL_PHASE_MAP_SHALLOW",
                "PARTIAL_PHASE_MAP_SHALLOW %d_of_%d: %s" % (n_pass, n_total, summ),
                extra)
    if pct_pass >= 0.10:
        return ("REGIME_BOUNDS_NARROW",
                "REGIME_BOUNDS_NARROW %d_of_%d: %s" % (n_pass, n_total, summ),
                extra)
    return ("PHASE_FRONTIER_COLLAPSED",
            "PHASE_FRONTIER_COLLAPSED %d_of_%d: %s" % (n_pass, n_total, summ),
            extra)


# ---------------------------------------------------------------------------
# Self-test (CPU-fast; verifies mechanism + formula + arms-differ + NO_SILENT_EXCEPT)
# ---------------------------------------------------------------------------
def _selftest() -> None:
    """Smaller-scale mechanism check; runs on CPU; no NVML needed."""
    g = np.random.default_rng(0)
    n_test = 512
    V_test = 80          # V_test % N_PARTITIONS=4 == 0
    part_sz_test = V_test // N_PARTITIONS
    assert part_sz_test == 20
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

    chains_d5 = [c[:5] for c in chains]

    # T4: SUBSTRATE_BASELINE arm
    r_sub, sub_preds = arm_substrate_baseline(E, R, sq_t, W, chains_d5,
                                               depth=5, V_C=V_test)
    assert 0.0 <= r_sub["top1"] <= 1.0
    assert len(sub_preds) == 5 * 5
    assert len(r_sub["per_step_acc"]) == 5

    # T5: PARTITION_ORACLE arm
    r_part, part_preds = arm_partition_oracle(E, R, sq_t, W, chains_d5,
                                                depth=5, part_size=part_sz_test,
                                                n_partitions=N_PARTITIONS)
    assert 0.0 <= r_part["top1"] <= 1.0
    assert len(part_preds) == 5 * 5

    # T6: RANDOM_PARTITION arm
    g_r = np.random.default_rng(7)
    r_rand, rand_preds = arm_random_partition(E, R, sq_t, W, chains_d5,
                                                depth=5, part_size=part_sz_test,
                                                n_partitions=N_PARTITIONS, g=g_r)
    assert 0.0 <= r_rand["top1"] <= 1.0
    assert len(rand_preds) == 5 * 5

    # T7: arms-differ (3 distinct SHA-256 hashes)
    sha_sub = sha256_of(sub_preds)
    sha_part = sha256_of(part_preds)
    sha_rand = sha256_of(rand_preds)
    assert len({sha_sub, sha_part, sha_rand}) == 3, (
        "ARMS_DISTINCT VIOLATION: sub=%s part=%s rand=%s" % (
            sha_sub, sha_part, sha_rand))
    print("  [selftest] arms distinct: sub=%s part=%s rand=%s" % (
        sha_sub, sha_part, sha_rand))

    # T8: empirical p_step at eff_V_C=10 (matches v3 anchor); back-solve
    p_anchor = 0.808 ** (1.0 / 15.0)
    assert abs(p_anchor - 0.98590) < 1e-4
    # p_step_empirical at eff_V_C=200 is 0.99 (matches v3 corner 2 0.987 within 0.01)
    p_eff_200 = p_step_empirical(200)
    assert abs(p_eff_200 - 0.99) < 1e-9
    p_eff_4000 = p_step_empirical(4000)
    assert abs(p_eff_4000 - 0.98) < 1e-9
    p_eff_16000 = p_step_empirical(16000)
    assert abs(p_eff_16000 - 0.95) < 1e-9

    # T9: bands_for sanity
    HP, HF = bands_for(0.9, 200)
    assert HP > HF
    assert HP > 5.0 * random_floor_eff_v_c(200)
    HP2, HF2 = bands_for(0.001, 16000)
    assert HP2 > HF2

    # T10: CARDINALITY guard
    assert EXPECTED_N_FULL == 12
    assert EXPECTED_N_SMOKE == 4
    assert len(SMOKE_CORNERS) == EXPECTED_N_SMOKE

    # T11: LLM call counter
    assert _LLM_CALL_COUNTER[0] == 0

    # T12: NO_SILENT_EXCEPT for sample_gpu_util_safe (META_RULE_J)
    # On CPU we expect NaN + reason=CUDA_UNAVAILABLE; the function must NOT
    # silently return 0.0 and pollute _GPU_UTIL_SAMPLES.
    pre_len = len(_GPU_UTIL_SAMPLES)
    pre_reason = list(_GPU_UTIL_FAIL_REASON)
    res = sample_gpu_util_safe()
    if not GPU_AVAIL:
        assert math.isnan(res), "CPU sample_gpu_util_safe must return NaN; got %r" % res
        assert len(_GPU_UTIL_SAMPLES) == pre_len, (
            "META_RULE_J VIOLATION: CPU sample silently appended to _GPU_UTIL_SAMPLES")
        assert len(_GPU_UTIL_FAIL_REASON) >= 1, (
            "META_RULE_J VIOLATION: CPU sample didn't record fail reason")
        print("  [selftest] META_RULE_J ok: CPU returns NaN + reason=%s" % (
            _GPU_UTIL_FAIL_REASON[0]))

    # T13: shape-audit (partition_oracle composition with multihop)
    # part_size * N_PARTITIONS == V_C; E_parts cover E exactly
    n_parts_test = N_PARTITIONS
    E_parts = [E[p * part_sz_test:(p + 1) * part_sz_test]
               for p in range(n_parts_test)]
    assert sum(p.shape[0] for p in E_parts) == V_test
    assert all(p.shape[1] == n_test for p in E_parts)

    # T14: sanity on PARTITION_ORACLE >> RANDOM_PARTITION
    # In tiny test, PART may not strictly beat RAND, but at production scale
    # (per pre-reg) it must. The test asserts mechanism integrity, not full-scale
    # discriminator. So we only check arms produce different outputs (T7) here.

    print("[selftest] PASS sub=%.4f part=%.4f rand=%.4f arms_distinct=True gpu=%s "
          "(p_step model 0.99/0.98/0.95)" % (
        r_sub["top1"], r_part["top1"], r_rand["top1"], GPU_AVAIL), flush=True)


# Self-test runs at MODULE IMPORT for cell-author validation (matches v1 pattern)
_selftest()


# ---------------------------------------------------------------------------
# top-level seed runner (called by chunked sibling files)
# ---------------------------------------------------------------------------
def _config_str(seed: int, mode: str) -> str:
    return (
        "ANCHOR=%s_seed_%d,N=%d,eff_V_Cs=%s,depths=%s,N_chains=%d,"
        "N_PARTITIONS=%d,V_PRED=%d,max_W_depth=%d,mode=%s,gpu_floor=%.1f,"
        "n_full=%d,n_smoke=%d,skunkworks_v3_commit=%s,skunkworks_v3_atom=%s"
    ) % (
        ANCHOR_NAME_PREFIX, seed, N_DIM, EFF_V_CS_FULL, DEPTHS_FULL,
        N_CHAINS_FIXED, N_PARTITIONS, V_PRED, MAX_W_DEPTH, mode,
        GPU_UTIL_FLOOR, EXPECTED_N_FULL, EXPECTED_N_SMOKE,
        SKUNKWORKS_V3_COMMIT, SKUNKWORKS_V3_ATOM,
    )


def run_one_seed(seed: int, smoke: bool = False, self_test: bool = False) -> int:
    """Run all 12 (or 4 smoke) points for a single seed; write metrics.json.

    Returns exit code (0 ok, non-zero fail).
    """
    started = time.time()
    anchor = "%s_seed_%d" % (ANCHOR_NAME_PREFIX, seed)
    env_name = os.environ.get("HDLAB_EXP_NAME", anchor)

    # METRICS-PATH-DISAMBIGUATION (selftest/smoke/full siblings; per
    # feedback_metrics_path_disambiguation_selftest_smoke_full_2026-06-27):
    # self_test MUST write to a sibling _selftest dir, NOT the FULL anchor's
    # dir. Otherwise queue_add.py's gate (which runs --self-test with
    # HDLAB_EXP_NAME=<full_anchor>) overwrites the FULL anchor's metrics.json
    # with a 668-byte SELFTEST_PASS payload, which downstream auditors then
    # mistake for "the cell ran and produced selftest results" (Skunkworks
    # caught this 2026-06-28). The smoke path is already disambiguated via
    # the _smoke suffix injected by queue_add.py; self_test needs the same.
    if self_test:
        out_dir = REPO / "data" / ("exp_" + env_name + "_selftest")
    else:
        out_dir = REPO / "data" / ("exp_" + env_name)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Reset per-seed instrumentation
    _GPU_UTIL_SAMPLES.clear()
    _GPU_UTIL_FAIL_REASON.clear()

    # self-test path: tiny mechanism verification (handled by _selftest at
    # module import; this exits cleanly so the queue gate passes).
    if self_test:
        # _selftest already ran at import; we got here -> PASS
        res = {
            "anchor_name": anchor + "_selftest",
            "verdict": "HARD_PASS",
            "verdict_msg": "SELFTEST_PASS (module-import self-test ran successfully)",
            "summary": "selftest seed=%d PASS" % seed,
            "elapsed_s": round(time.time() - started, 2),
            "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "run_mode": "self_test",
            "config_version": _config_str(seed, "self_test"),
            "seed": seed,
            "n_seeds": 1,
        }
        tmp = out_dir / "metrics.json.tmp"
        tmp.write_text(json.dumps(res, indent=2), encoding="utf-8")
        os.replace(str(tmp), str(out_dir / "metrics.json"))
        print("[selftest seed=%d] PASS -> %s" % (seed, out_dir / "metrics.json"),
              flush=True)
        return 0

    if smoke:
        grid = list(SMOKE_CORNERS)
        expected = EXPECTED_N_SMOKE
        mode = "smoke"
    else:
        # FULL: cross-product of EFF_V_CS_FULL x DEPTHS_FULL
        grid = [(d, eff) for eff in EFF_V_CS_FULL for d in DEPTHS_FULL]
        expected = EXPECTED_N_FULL
        mode = "full"

    if len(grid) != expected:
        raise RuntimeError("CARDINALITY_BREACH at grid build: %d != %d" % (
            len(grid), expected))

    # FULL mode requires GPU per Fix #24 (refuse to silently fall back)
    if mode == "full" and not GPU_AVAIL:
        print("[FATAL] FULL run requires GPU per Fix #24; CPU detected. Aborting.",
              flush=True)
        sentinel = {
            "anchor_name": anchor,
            "verdict": "HARD_FAIL",
            "verdict_msg": "FIX24_GUARD: FULL run requires GPU; CPU detected (cuda_available=False)",
            "summary": "fix24_guard_cpu_in_full",
            "elapsed_s": round(time.time() - started, 2),
            "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "run_mode": "full",
            "config_version": _config_str(seed, mode),
            "seed": seed, "n_seeds": 1,
            "gpu_avail": False,
        }
        tmp = out_dir / "metrics.json.tmp"
        tmp.write_text(json.dumps(sentinel, indent=2), encoding="utf-8")
        os.replace(str(tmp), str(out_dir / "metrics.json"))
        return 2

    # Order grid to amortize cache: sort by eff_V_C then depth
    grid_sorted = sorted(grid, key=lambda x: (x[1], x[0]))

    cache: Dict[int, Dict[str, Any]] = {}
    phase_map: List[Dict[str, Any]] = []

    if GPU_AVAIL:
        torch.cuda.reset_peak_memory_stats(DEVICE)

    for (depth, eff_V_C) in grid_sorted:
        # NO SILENT EXCEPT per META_RULE_AG: let exceptions propagate.
        # We catch ONLY to log + re-raise (provides per-point crash diagnostics).
        try:
            point = run_point(depth, eff_V_C, seed, cache)
            phase_map.append(point)
        except Exception as e:
            print("[POINT_CRASH seed=%d depth=%d eff_V_C=%d] %s" % (
                seed, depth, eff_V_C, e), file=sys.stderr)
            traceback.print_exc()
            raise   # propagate -> outer crash sentinel writes metrics.json
        sample_gpu_util_safe()

    # Free GPU memory
    cache.clear()
    if GPU_AVAIL:
        torch.cuda.empty_cache()
        peak_bytes = torch.cuda.max_memory_allocated(DEVICE)
    else:
        peak_bytes = 0

    # GPU util summary (LOUD on failure per META_RULE_J)
    if len(_GPU_UTIL_SAMPLES) > 0:
        gpu_util_mean = float(np.mean(_GPU_UTIL_SAMPLES))
        gpu_util_max = float(np.max(_GPU_UTIL_SAMPLES))
    else:
        gpu_util_mean = float("nan")
        gpu_util_max = float("nan")
    gpu_util_n_samples = len(_GPU_UTIL_SAMPLES)
    gpu_util_reason = _GPU_UTIL_FAIL_REASON[0] if _GPU_UTIL_FAIL_REASON else ""

    # Verdict
    if mode == "smoke":
        verdict, msg, extra = smoke_verdict(phase_map, gpu_util_mean,
                                              gpu_util_n_samples, gpu_util_reason,
                                              GPU_AVAIL)
    else:
        verdict, msg, extra = full_verdict(phase_map, gpu_util_mean,
                                              gpu_util_n_samples, gpu_util_reason,
                                              GPU_AVAIL)

    # NaN-safe serialization: replace float('nan') with None for JSON
    def _nan_to_none(x: Any) -> Any:
        if isinstance(x, float) and math.isnan(x):
            return None
        return x

    metrics = {
        "anchor_name": anchor,
        "verdict": verdict,
        "verdict_msg": msg,
        "summary": msg,
        "elapsed_s": round(time.time() - started, 2),
        "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "run_mode": mode,
        "n_seeds": 1,
        "seed": seed,
        "config_version": _config_str(seed, mode),
        "phase_map": phase_map,
        "extra": extra,
        "gpu_util_pct_mean": _nan_to_none(gpu_util_mean),
        "gpu_util_pct_max": _nan_to_none(gpu_util_max),
        "gpu_util_n_samples": gpu_util_n_samples,
        "gpu_util_reason_if_failed": gpu_util_reason if gpu_util_reason else None,
        "gpu_avail": GPU_AVAIL,
        "gpu_name": GPU_NAME,
        "gpu_max_mem_alloc_mb": round(peak_bytes / 1e6, 2),
        "_llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
        "expected_n_points": expected,
        "observed_n_points": len(phase_map),
        "cardinality_ok": (len(phase_map) == expected),
        "skunkworks_v3_atomization": {
            "commit": SKUNKWORKS_V3_COMMIT,
            "atom_sha256_16": SKUNKWORKS_V3_ATOM,
            "diagnosis": "v3 test-design issue: bands derived from cone-formula on nominal V_C; v4 sweeps effective_V_C directly",
        },
    }
    # META_RULE_AG atomic write
    tmp = out_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    os.replace(str(tmp), str(out_dir / "metrics.json"))
    print("[seed=%d %s] FINAL verdict=%s msg=%s elapsed=%.1fs gpu_util=%.1f%% (n=%d)" % (
        seed, mode, verdict, msg, time.time() - started,
        (gpu_util_mean if not math.isnan(gpu_util_mean) else -1.0),
        gpu_util_n_samples), flush=True)
    return 0 if verdict in ("HARD_PASS", "MIDDLE_BAND",
                              "CHAIN_GRADE_PHASE_MAP_COMPLETE",
                              "PARTIAL_PHASE_MAP_SHALLOW",
                              "REGIME_BOUNDS_NARROW") else 1
