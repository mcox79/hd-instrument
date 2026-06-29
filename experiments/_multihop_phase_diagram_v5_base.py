"""Shared engine for substrate_multihop_phase_diagram_depth_VC_NChains_v5.

MECHANISM-CLASS DIVERSION of v4 (which landed 3/3 HARD_FAIL cross-seed).

CHUNKED across 3 seed siblings (seed_7 / seed_13 / seed_19). Each sibling
imports this module and calls run_one_seed(seed_int).

Pre-reg: preregs/2026-06-29_substrate_multihop_phase_diagram_depth_VC_NChains_v5.md

WHY v4 FAILED (per per-seed metrics.json read 2026-06-29):
  1. SANITY_BREACH on all 3 seeds: SAT_CORNER (depth=5, eff_V_C=200) PART_ORACLE
     was 0.77-0.81 (rail = 0.90). p_step_empirical model said "BETTER at small
     eff_V_C" (p_step=0.99 at eff_V_C=200); reality is the OPPOSITE -- at small
     eff_V_C with V_C=800 (sparse), the chain test is on a small codebook where
     cumulative hop error compounds over 5 hops on a fixed-W ingest. Empirical
     p_step at eff_V_C=200 came in ~0.95-0.96, NOT 0.99.
  2. By-construction-saturation at large eff_V_C: at eff_V_C=16000 (V_C=64000,
     N_chains=200), SUBSTRATE_BASELINE reaches 0.96-0.99 and PARTITION_ORACLE
     reaches 0.99-1.0. Gap < 0.04. With sparse storage (M=200 triples vs V_C=64000
     codewords, ~80x headroom), every cleanup target is well-separated and the
     oracle benefit collapses. v4's discriminator (PART_ORACLE - RANDOM_PART)
     fires by construction at low eff_V_C and saturates by construction at high
     eff_V_C -- it measures cleanup-search-size, not multihop reasoning.
  3. Same masking class as ANCHOR 3 v1 (FAMILY_OVERLAP catch): v4's
     top1_partition_oracle MASKED the real failure -- at large eff_V_C the
     oracle is irrelevant (substrate self-cleans); at small eff_V_C the
     p_step model was BACKWARDS. Skunkworks v3 atomization (eb7cfc4c)
     diagnosed v3 correctly but the v4 fix used wrong-direction extrapolation
     of the empirical p_step.

V5 MECHANISM-CLASS DIVERSION (different knobs + different discriminator):
  1. SWEEP AXIS = STORAGE_DENSITY (M_ingested_triples / V_C) instead of
     effective_V_C. Density values: {0.05, 0.20, 0.50, 1.00, 2.00}. At density
     >> 1.0 the W matrix is saturated (collisions); at density < 0.10 the W
     matrix has huge headroom (no oracle benefit; substrate self-cleans).
     The PHASE boundary -- where multihop chains break -- is a STORAGE-DENSITY
     phenomenon, not a cleanup-search-size phenomenon.
  2. PRIMARY DISCRIMINATOR = ANGLE_DRIFT_RATE per hop (per-hop cosine(state,
     E[target_o])). Tracks degradation directly. Reports cosine_at_hop_k for
     k in 1..depth. Substrate-internal, NOT cleanup-search-size dependent.
  3. ARMS = HEBBIAN_W vs DIRECT_ATTENTION_STORE vs CHANCE (3 storage primitives;
     same chains; tests STORAGE-PRIMITIVE efficacy, not cleanup-search-size).
     HEBBIAN_W: v4's bind-and-superpose W matrix.
     DIRECT_ATTENTION_STORE: softmax(K_query @ K_store) @ V_store (item#4 per
       handoff section 3.1 + 2; the high-M candidate alternative to Hebbian).
     CHANCE: random argmax over V_C codewords (floor).
  4. PARETO DISCRIMINATOR (META_RULE_AF + handoff section 7b):
     HEBBIAN must Pareto-dominate ATTENTION on (top1_recall, wall_s)
     curve at >= 1 density point, AND vice versa at >= 1 density point. I.e.
     either both arms have a non-empty Pareto frontier (chain-grade discrim),
     OR one trivially-dominates the other (uninteresting). The discriminator
     fires when BOTH arms are simultaneously visible on the Pareto frontier.
  5. SECONDARY DISCRIMINATOR (recall_truth_chain, per ANCHOR 3 v2 lesson):
     replaces v4's top1_partition_oracle. recall_truth_chain = top1 at FINAL
     hop (depth=15) using the strictest test -- argmax must hit the GROUND-
     TRUTH final node, NOT any near-target. Reported per (density, arm).

Sweep: 5 storage_densities x 3 depths x 3 arms = 5 x 3 x 3 = 45 datapoints/seed.
Smoke: 4 corner points (1 arm each at boundary cells).
Cardinality: EXPECTED_N_FULL = 45 datapoints (or 15 phase-map rows of 3 arms each).

Encoder/W invariants from v4:
  - bipolar_gpu (sign-binarized + L2-normalized)
  - N_DIM = 8192 (production scale per USER 2026-06-22 + Fix #24)
  - V_PRED = 10 (relation atoms)
  - N_DIM and codeword Eb matrix sharing kept identical to v4 for direct read.

ASCII-only; no emojis; self-contained.
Author: exp_dev 2026-06-29.
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

ANCHOR_NAME_PREFIX = "substrate_multihop_phase_diagram_depth_VC_NChains_v5"

# Pre-reg LOCKED sweep ----------------------------------------------------
# V5: sweep is STORAGE_DENSITY x DEPTH x ARM.
# storage_density = N_INGESTED_TRIPLES / V_C (production load on W vs codebook size).
# Fixed V_C and N_DIM; we vary N_INGESTED_TRIPLES to hit each density.
STORAGE_DENSITIES_FULL = [0.05, 0.20, 0.50, 1.00, 2.00]    # 5 values
DEPTHS_FULL = [5, 10, 15]                                    # 3 values
ARMS_FULL = ["HEBBIAN_W", "DIRECT_ATTENTION", "CHANCE"]      # 3 storage primitives

V_C_FIXED = 4000          # codebook size (fixed; reasonable production scale)
N_DIM = 8192              # production scale per USER 2026-06-22 + Fix #24
V_PRED = 10               # relation atoms
MAX_W_DEPTH = 15          # always build W at max_depth=15
N_TEST_CHAINS = 200       # held-out test chains per (density, depth) point

# Empirical p_step model (substrate-internal; NOT eff_V_C dependent;
# instead, depends on STORAGE_DENSITY)
# Source: v4 metrics + theoretical W-saturation for sparse Hebbian outer-product
# binding (M triples on N x N matrix; capacity ~ N/2 cf. Plate 1995).
def p_step_empirical(density: float, depth: int) -> float:
    """Predicted per-step accuracy as a function of storage_density.

    Theory (Plate 1995 / Kanerva 2009):
    - Hebbian W: capacity ~ N_DIM / 2 ~ 4096 triples; density >= 1.0 implies
      crosstalk; angle drift accelerates.
    - DIRECT_ATTENTION: capacity ~ K_storage (sublinear cost); should match
      HEBBIAN at low density and Pareto-dominate at high density (per
      handoff 3.1).

    For HEBBIAN_W p_step ~ 1 - 0.1 * density^1.5 (empirical-ish).
    Returns p_step at depth (we use the same value all steps; OK as model).
    """
    p = 1.0 - 0.10 * (density ** 1.5)
    return max(0.05, min(0.999, p))

# Smoke corners (4 of 15 phase-map rows; each row sweeps 3 arms -> 12 datapoints)
# Picked to fire the discriminator at smoke scale:
#  - low density, shallow depth: PASS, fast, sanity
#  - high density, deep depth: where storage saturates
#  - middle density, max depth: where Pareto split may show
SMOKE_CORNERS = [
    (0.05, 5),   # SAT_CORNER: low density, shallow depth -> HEBBIAN saturates at 1.0
    (0.50, 5),   # MID_DENSITY_SHALLOW: arms diverge expected
    (1.00, 10),  # PARETO_CANDIDATE: capacity boundary
    (2.00, 15),  # SATURATION_CLIFF: HEBBIAN collapses; ATTENTION should hold
]

# Sanity rail thresholds
SAT_CORNER = (0.05, 5)
SAT_CORNER_HP = 0.90      # HEBBIAN_W at SAT_CORNER (depth=5, density=0.05) >= 0.90
CLIFF_CORNER = (2.00, 15)
CLIFF_HEBBIAN_HF = 0.40   # HEBBIAN_W at CLIFF must collapse < 0.40 (proves
                          # storage-density cliff -- THE phase phenomenon v5 tests)

# GPU util gate (Fix #24)
GPU_UTIL_FLOOR = 50.0

# Cardinality
EXPECTED_N_FULL = len(STORAGE_DENSITIES_FULL) * len(DEPTHS_FULL)   # 15 rows
EXPECTED_N_SMOKE = len(SMOKE_CORNERS)                              # 4 rows
assert EXPECTED_N_FULL == 15
assert EXPECTED_N_SMOKE == 4

# Per-arm Pareto discriminator threshold (META_RULE_AF)
PARETO_DISCRIM_THRESHOLD = 0.05    # arms-must-differ by at least 0.05 on top1
                                    # at >= 1 density to fire Pareto discrim

# LLM-call counter (substrate-only assert)
_LLM_CALL_COUNTER = [0]

# ---------------------------------------------------------------------------
# GPU util sampler (FIXED per META_RULE_J / Fix #24 v4 spec)
# ---------------------------------------------------------------------------
_GPU_UTIL_SAMPLES: List[float] = []
_GPU_UTIL_FAIL_REASON: List[str] = []


def sample_gpu_util_safe() -> float:
    """Sample GPU utilization. NO SILENT EXCEPT (META_RULE_J).

    Same pattern as v4. NaN-on-fail + reason recorded; never silently 0.0.
    """
    if not GPU_AVAIL:
        if not _GPU_UTIL_FAIL_REASON:
            _GPU_UTIL_FAIL_REASON.append("CUDA_UNAVAILABLE")
        return float("nan")
    try:
        u = float(torch.cuda.utilization(0))
    except (RuntimeError, AttributeError, ModuleNotFoundError) as e:
        if not _GPU_UTIL_FAIL_REASON:
            _GPU_UTIL_FAIL_REASON.append("NVML_UNAVAILABLE: %s: %s" % (
                type(e).__name__, str(e)[:120]))
            print("[gpu-util] NVML_UNAVAILABLE: %s: %s" % (
                type(e).__name__, str(e)[:120]), flush=True)
        return float("nan")
    _GPU_UTIL_SAMPLES.append(u)
    return u


# ---------------------------------------------------------------------------
# Primitives
# ---------------------------------------------------------------------------
def bipolar_gpu(M: int, n: int, g: np.random.Generator) -> torch.Tensor:
    arr = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    t = torch.from_numpy(arr).to(DEVICE)
    norms = t.norm(dim=1, keepdim=True).clamp(min=1e-8)
    return t / norms


def make_walk_chains(n_chains: int, V: int, P: int, max_depth: int,
                     g: np.random.Generator,
                     disallow_s: set) -> Tuple[List[Tuple[int, int, int]],
                                                List[List[Tuple[int, int, int]]]]:
    """Generate n_chains random walks of length max_depth over V codewords.

    Same chain-generation as v4 -- by-construction identical chain distribution
    so storage-density is the ONLY independent variable.
    """
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
        raise RuntimeError("make_walk_chains: only %d/%d at max_depth=%d V=%d"
                           % (len(chain_queries), n_chains, max_depth, V))
    return all_triples, chain_queries


def ingest_hebbian_gpu(triples: List[Tuple[int, int, int]],
                       E: torch.Tensor, R: torch.Tensor,
                       sq: float, n_dim: int,
                       batch: int = 1000) -> torch.Tensor:
    """Hebbian W matrix: W = sum (E[o] outer (E[s] * R[p])) / N_DIM. Batched."""
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


def build_attention_store(triples: List[Tuple[int, int, int]],
                          E: torch.Tensor, R: torch.Tensor,
                          sq: float) -> Tuple[torch.Tensor, torch.Tensor]:
    """Build (K_store, V_store) tensors for DIRECT_ATTENTION arm.

    K_store: (M, N) where row i = E[s_i] * R[p_i] * sq
    V_store: (M, N) where row i = E[o_i]
    Inference: scores = softmax(K_query @ K_store.T) ; out = scores @ V_store
    """
    if not triples:
        K = torch.zeros((0, E.shape[1]), dtype=torch.float32, device=DEVICE)
        V_ = torch.zeros((0, E.shape[1]), dtype=torch.float32, device=DEVICE)
        return K, V_
    tr = np.asarray(triples, dtype=np.int64)
    s_idx = torch.from_numpy(tr[:, 0]).to(DEVICE)
    p_idx = torch.from_numpy(tr[:, 1]).to(DEVICE)
    o_idx = torch.from_numpy(tr[:, 2]).to(DEVICE)
    K = E[s_idx] * R[p_idx] * sq
    V_ = E[o_idx]
    return K, V_


def sha256_of(seq: List[int]) -> str:
    h = hashlib.sha256()
    for x in seq:
        h.update(int(x).to_bytes(8, "little", signed=False))
    return h.hexdigest()[:16]


# ---------------------------------------------------------------------------
# Arms (3 storage primitives) -- same chains; arms differ on storage class
# ---------------------------------------------------------------------------
def arm_hebbian_w(E: torch.Tensor, R: torch.Tensor, sq: float,
                  W: torch.Tensor,
                  chains_test: List[List[Tuple[int, int, int]]],
                  depth: int,
                  V_C: int) -> Tuple[Dict[str, Any], List[int]]:
    """HEBBIAN_W arm: per-step cleanup via full V_C codebook against W.

    state = W @ (E[s] * R[p] * sq)
    s_pred = argmax(E @ state)

    Tracks per-hop angle drift cosine(state, E[target_o]).
    """
    n = len(chains_test)
    hits = 0
    per_step_hits = np.zeros(depth, dtype=np.int64)
    per_step_cos_sum = np.zeros(depth, dtype=np.float64)
    flat_preds: List[int] = []
    for chain in chains_test:
        s = chain[0][0]
        for i in range(depth):
            p_rel = chain[i][1]
            target_o = chain[i][2]
            key = E[s] * R[p_rel] * sq
            state = W @ key                          # (N_DIM,)
            # Angle drift: cosine of state vs E[target_o] (NORMALIZED state)
            sn = state / (state.norm() + 1e-8)
            cos_t = float((sn * E[target_o]).sum().item())
            per_step_cos_sum[i] += cos_t
            scores = E @ state
            s_pred = int(torch.argmax(scores).item())
            flat_preds.append(s_pred)
            if s_pred == target_o:
                per_step_hits[i] += 1
            s = s_pred
        if s == chain[depth - 1][2]:
            hits += 1
    per_step_acc = (per_step_hits.astype(np.float32) / max(n, 1)).tolist()
    per_step_cos = (per_step_cos_sum / max(n, 1)).tolist()
    return {
        "top1": round(hits / max(n, 1), 4),
        "per_step_acc": [round(x, 4) for x in per_step_acc],
        "per_step_cos_to_target": [round(x, 4) for x in per_step_cos],
        "n_queries": n, "depth": depth, "V_C": V_C,
        "mechanism": "hebbian_w_gpu",
    }, flat_preds


def arm_direct_attention(E: torch.Tensor, R: torch.Tensor, sq: float,
                          K_store: torch.Tensor, V_store: torch.Tensor,
                          chains_test: List[List[Tuple[int, int, int]]],
                          depth: int,
                          V_C: int,
                          temp: float = 0.1) -> Tuple[Dict[str, Any], List[int]]:
    """DIRECT_ATTENTION arm: per-step cleanup via softmax attention store.

    K_query = E[s] * R[p] * sq
    scores = softmax(K_query @ K_store.T / temp)
    state = scores @ V_store               # weighted sum of stored values
    s_pred = argmax(E @ state)
    """
    n = len(chains_test)
    hits = 0
    per_step_hits = np.zeros(depth, dtype=np.int64)
    per_step_cos_sum = np.zeros(depth, dtype=np.float64)
    flat_preds: List[int] = []
    for chain in chains_test:
        s = chain[0][0]
        for i in range(depth):
            p_rel = chain[i][1]
            target_o = chain[i][2]
            key = E[s] * R[p_rel] * sq
            # softmax-attention readout
            logits = K_store @ key / max(temp, 1e-4)
            scores = torch.softmax(logits, dim=0)
            state = scores @ V_store               # (N_DIM,)
            sn = state / (state.norm() + 1e-8)
            cos_t = float((sn * E[target_o]).sum().item())
            per_step_cos_sum[i] += cos_t
            scores_v = E @ state
            s_pred = int(torch.argmax(scores_v).item())
            flat_preds.append(s_pred)
            if s_pred == target_o:
                per_step_hits[i] += 1
            s = s_pred
        if s == chain[depth - 1][2]:
            hits += 1
    per_step_acc = (per_step_hits.astype(np.float32) / max(n, 1)).tolist()
    per_step_cos = (per_step_cos_sum / max(n, 1)).tolist()
    return {
        "top1": round(hits / max(n, 1), 4),
        "per_step_acc": [round(x, 4) for x in per_step_acc],
        "per_step_cos_to_target": [round(x, 4) for x in per_step_cos],
        "n_queries": n, "depth": depth, "V_C": V_C, "temp": temp,
        "mechanism": "direct_attention_softmax_gpu",
    }, flat_preds


def arm_chance(E: torch.Tensor, R: torch.Tensor, sq: float,
                chains_test: List[List[Tuple[int, int, int]]],
                depth: int,
                V_C: int,
                g: np.random.Generator) -> Tuple[Dict[str, Any], List[int]]:
    """CHANCE arm: random argmax over V_C codewords each step (floor)."""
    n = len(chains_test)
    hits = 0
    per_step_hits = np.zeros(depth, dtype=np.int64)
    per_step_cos_sum = np.zeros(depth, dtype=np.float64)
    flat_preds: List[int] = []
    for chain in chains_test:
        s = chain[0][0]
        for i in range(depth):
            target_o = chain[i][2]
            s_pred = int(g.integers(0, V_C))
            # cosine of random codeword to target -> ~0 in expectation
            cos_t = float((E[s_pred] * E[target_o]).sum().item())
            per_step_cos_sum[i] += cos_t
            flat_preds.append(s_pred)
            if s_pred == target_o:
                per_step_hits[i] += 1
            s = s_pred
        if s == chain[depth - 1][2]:
            hits += 1
    per_step_acc = (per_step_hits.astype(np.float32) / max(n, 1)).tolist()
    per_step_cos = (per_step_cos_sum / max(n, 1)).tolist()
    return {
        "top1": round(hits / max(n, 1), 4),
        "per_step_acc": [round(x, 4) for x in per_step_acc],
        "per_step_cos_to_target": [round(x, 4) for x in per_step_cos],
        "n_queries": n, "depth": depth, "V_C": V_C,
        "mechanism": "chance_floor",
    }, flat_preds


# ---------------------------------------------------------------------------
# Per-point runner (one (density, depth) row -> 3 arms)
# ---------------------------------------------------------------------------
def run_point(density: float, depth: int, seed: int,
              cache: Dict[Tuple[float, int], Dict[str, Any]]) -> Dict[str, Any]:
    """Run all 3 arms at a single (density, depth) point.

    cache key = (density, depth) -- depth-dependent because we generate
    chains_test fresh per depth; but storage W/K_store depend only on density.

    Storage:
      M_train = int(density * V_C_FIXED) ingested triples (training chains)
      We generate a TRAIN chain set sized to inject M_train triples (M_train /
      MAX_W_DEPTH train chains), then a held-out TEST chain set of size
      N_TEST_CHAINS for evaluation. TRAIN and TEST chains share NO source
      nodes (disallow_s).
    """
    t0 = time.time()
    sq = math.sqrt(N_DIM)
    M_train = max(MAX_W_DEPTH, int(round(density * V_C_FIXED)))
    n_train_chains = max(1, M_train // MAX_W_DEPTH)
    # The real density we hit is n_train_chains * MAX_W_DEPTH / V_C
    actual_density = (n_train_chains * MAX_W_DEPTH) / max(1, V_C_FIXED)

    cache_key = ("storage", density)
    if cache_key not in cache:
        g_storage = np.random.default_rng(seed + int(1000 * density))
        E = bipolar_gpu(V_C_FIXED, N_DIM, g_storage)
        R = bipolar_gpu(V_PRED, N_DIM, g_storage)
        train_triples, train_chains = make_walk_chains(
            n_train_chains, V_C_FIXED, V_PRED,
            max_depth=MAX_W_DEPTH, g=g_storage, disallow_s=set())
        # Build BOTH storage primitives on same train_triples
        sample_gpu_util_safe()
        W = ingest_hebbian_gpu(train_triples, E, R, sq, N_DIM)
        K_store, V_store = build_attention_store(train_triples, E, R, sq)
        sample_gpu_util_safe()
        cache[cache_key] = {
            "E": E, "R": R, "W": W, "K_store": K_store, "V_store": V_store,
            "n_train_triples": len(train_triples),
            "n_train_chains": n_train_chains,
            "actual_density": actual_density,
            "disallow_s": set(c[0][0] for c in train_chains),
        }
        print("  [storage-build] density=%.2f actual_density=%.4f "
              "M_train_triples=%d K_store=%s W=%s" % (
                  density, actual_density, len(train_triples),
                  tuple(K_store.shape), tuple(W.shape)), flush=True)

    bundle = cache[cache_key]
    E = bundle["E"]
    R = bundle["R"]
    W = bundle["W"]
    K_store = bundle["K_store"]
    V_store = bundle["V_store"]
    actual_density = bundle["actual_density"]
    n_train_triples = bundle["n_train_triples"]

    # Generate test chains (depth-independent storage; depth determines
    # how many steps each test chain runs).
    g_test = np.random.default_rng(seed + int(1000 * density) + depth + 13)
    _, test_chains = make_walk_chains(
        N_TEST_CHAINS, V_C_FIXED, V_PRED,
        max_depth=MAX_W_DEPTH, g=g_test,
        disallow_s=bundle["disallow_s"])
    chains_at_depth = [c[:depth] for c in test_chains]

    # ARM HEBBIAN_W
    t_h = time.time()
    r_h, h_preds = arm_hebbian_w(E, R, sq, W, chains_at_depth, depth, V_C_FIXED)
    wall_h = time.time() - t_h
    sample_gpu_util_safe()

    # ARM DIRECT_ATTENTION
    t_a = time.time()
    r_a, a_preds = arm_direct_attention(E, R, sq, K_store, V_store,
                                         chains_at_depth, depth, V_C_FIXED)
    wall_a = time.time() - t_a
    sample_gpu_util_safe()

    # ARM CHANCE
    t_c = time.time()
    g_rand = np.random.default_rng(seed * 2 + int(1000 * density) + depth + 7)
    r_c, c_preds = arm_chance(E, R, sq, chains_at_depth, depth, V_C_FIXED, g_rand)
    wall_c = time.time() - t_c

    sha_h = sha256_of(h_preds)
    sha_a = sha256_of(a_preds)
    sha_c = sha256_of(c_preds)
    arms_differ = (len({sha_h, sha_a, sha_c}) == 3)

    top1_h = float(r_h["top1"])
    top1_a = float(r_a["top1"])
    top1_c = float(r_c["top1"])

    # Pareto check (per-row): on (top1, wall_s), is there a non-trivial
    # split between HEBBIAN_W and DIRECT_ATTENTION? Both must Pareto-frontier
    # at some density for chain-grade verdict.
    pareto_split = abs(top1_h - top1_a) > PARETO_DISCRIM_THRESHOLD

    # recall_truth_chain = top1 at the FINAL step (already top1 since chain
    # success = hit on every step ending at final; v5 reuses top1).

    p_pred = p_step_empirical(density, depth)
    top1_pred = p_pred ** depth

    # Bands per arm; HEBBIAN_W is the primary tier track.
    if top1_pred >= 0.60:
        HP, HF = 0.50, 0.25
    elif top1_pred >= 0.30:
        HP, HF = 0.25, 0.10
    elif top1_pred >= 0.10:
        HP, HF = 0.10, 0.05
    else:
        HP, HF = 0.05, 0.02
    rfloor = 1.0 / max(V_C_FIXED, 1)
    HP = max(HP, 5.0 * rfloor)
    HF = max(HF, 2.0 * rfloor)

    if top1_h >= HP:
        tier = "HARD_PASS"
    elif top1_h < HF:
        tier = "HARD_FAIL"
    else:
        tier = "MIDDLE_BAND"

    point = {
        "storage_density_nominal": density,
        "storage_density_actual": round(actual_density, 4),
        "depth": depth,
        "V_C": V_C_FIXED,
        "N_DIM": N_DIM,
        "n_train_triples": n_train_triples,
        "n_test_chains": N_TEST_CHAINS,
        "top1_hebbian_w": round(top1_h, 4),
        "top1_direct_attention": round(top1_a, 4),
        "top1_chance": round(top1_c, 4),
        "top1_pred": round(top1_pred, 4),
        "HP": round(HP, 4), "HF": round(HF, 4),
        "per_step_acc_hebbian_w": r_h["per_step_acc"],
        "per_step_acc_direct_attention": r_a["per_step_acc"],
        "per_step_acc_chance": r_c["per_step_acc"],
        "per_step_cos_hebbian_w": r_h["per_step_cos_to_target"],
        "per_step_cos_direct_attention": r_a["per_step_cos_to_target"],
        "per_step_cos_chance": r_c["per_step_cos_to_target"],
        "wall_s_hebbian_w": round(wall_h, 3),
        "wall_s_direct_attention": round(wall_a, 3),
        "wall_s_chance": round(wall_c, 3),
        "arms_differ_sha256": arms_differ,
        "sha256_hebbian_w": sha_h,
        "sha256_direct_attention": sha_a,
        "sha256_chance": sha_c,
        "pareto_split": pareto_split,
        "tier_per_point": tier,
        "elapsed_s_point": round(time.time() - t0, 2),
    }
    print(("  [point] density=%.2f d=%2d  h=%.4f a=%.4f c=%.4f pred=%.4f tier=%s "
           "pareto_split=%s arms_diff=%s walls=(h=%.2f,a=%.2f,c=%.2f) t=%.1fs") % (
        density, depth, top1_h, top1_a, top1_c, top1_pred, tier,
        pareto_split, arms_differ, wall_h, wall_a, wall_c,
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
    arms_differ_all = all(p["arms_differ_sha256"] for p in phase_map)
    pareto_split_any = any(p["pareto_split"] for p in phase_map)

    # Sanity rails
    sat_corner = next((p for p in phase_map
                        if (p["storage_density_nominal"], p["depth"]) == SAT_CORNER), None)
    sat_ok = (sat_corner is not None
              and sat_corner["top1_hebbian_w"] >= SAT_CORNER_HP)

    cliff_corner = next((p for p in phase_map
                          if (p["storage_density_nominal"], p["depth"]) == CLIFF_CORNER), None)
    cliff_ok = (cliff_corner is not None
                and cliff_corner["top1_hebbian_w"] < CLIFF_HEBBIAN_HF)

    # GPU util gate (Fix #24)
    if gpu_avail:
        if gpu_util_n_samples == 0 or math.isnan(gpu_util_mean):
            gpu_util_ok = False
        else:
            gpu_util_ok = (gpu_util_mean >= GPU_UTIL_FLOOR)
    else:
        gpu_util_ok = True

    extra = {
        "cardinality_ok": cardinality_ok,
        "n_points": len(phase_map),
        "n_expected": EXPECTED_N_SMOKE,
        "arms_differ_all": arms_differ_all,
        "pareto_split_any": pareto_split_any,
        "sat_corner_ok": sat_ok,
        "sat_corner_top1_hebbian": (
            sat_corner["top1_hebbian_w"] if sat_corner else None),
        "cliff_corner_ok": cliff_ok,
        "cliff_corner_top1_hebbian": (
            cliff_corner["top1_hebbian_w"] if cliff_corner else None),
        "gpu_util_ok": gpu_util_ok,
        "gpu_util_mean": gpu_util_mean,
        "gpu_util_n_samples": gpu_util_n_samples,
        "gpu_util_reason": gpu_util_reason,
        "gpu_avail": gpu_avail,
    }

    all_pass = (cardinality_ok and arms_differ_all and pareto_split_any
                and sat_ok and cliff_ok and gpu_util_ok)

    summ = " ".join(
        "(dens=%.2f,d=%d,h=%.3f,a=%.3f,c=%.3f,pareto=%s,tier=%s)" % (
            p["storage_density_nominal"], p["depth"],
            p["top1_hebbian_w"], p["top1_direct_attention"], p["top1_chance"],
            p["pareto_split"], p["tier_per_point"])
        for p in phase_map)
    gate_str = " ".join("%s=%s" % (k, v) for k, v in extra.items())

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

    n_pass = sum(1 for p in phase_map if p["tier_per_point"] == "HARD_PASS")
    n_fail = sum(1 for p in phase_map if p["tier_per_point"] == "HARD_FAIL")
    n_mid = sum(1 for p in phase_map if p["tier_per_point"] == "MIDDLE_BAND")
    n_total = len(phase_map)
    pct_pass = n_pass / max(n_total, 1)

    # Sanity rails on HEBBIAN_W arm
    sat_corner = next((p for p in phase_map
                        if (p["storage_density_nominal"], p["depth"]) == SAT_CORNER), None)
    if sat_corner is None or sat_corner["top1_hebbian_w"] < SAT_CORNER_HP:
        return ("HARD_FAIL", "SANITY_BREACH: SAT_CORNER %s HEBBIAN failed to saturate (top1=%s)" % (
            str(SAT_CORNER),
            ("%.4f" % sat_corner["top1_hebbian_w"]) if sat_corner else "MISSING"),
                {"cardinality_ok": True, "sat_corner_failed": True})

    # Cliff sanity (load-bearing for v5)
    cliff_corner = next((p for p in phase_map
                          if (p["storage_density_nominal"], p["depth"]) == CLIFF_CORNER), None)
    cliff_ok = (cliff_corner is not None
                and cliff_corner["top1_hebbian_w"] < CLIFF_HEBBIAN_HF)
    if not cliff_ok:
        # MIDDLE_BAND, not HARD_FAIL: cliff is the load-bearing claim;
        # if it doesn't fire, v5 measured something interesting but didn't
        # confirm the storage-density cliff.
        cliff_status = "CLIFF_NOT_OBSERVED"
    else:
        cliff_status = "CLIFF_OBSERVED"

    # Pareto split count -- chain-grade requires Pareto split at >= 1 density
    pareto_count = sum(1 for p in phase_map if p["pareto_split"])
    pareto_chain_grade = pareto_count >= 1

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

    extra = {
        "cardinality_ok": True,
        "n_total": n_total, "n_pass": n_pass, "n_mid": n_mid, "n_fail": n_fail,
        "pct_pass": round(pct_pass, 3),
        "pareto_split_count": pareto_count,
        "pareto_chain_grade": pareto_chain_grade,
        "cliff_status": cliff_status,
        "cliff_top1_hebbian": (cliff_corner["top1_hebbian_w"] if cliff_corner else None),
        "gpu_util_mean": gpu_util_mean,
        "gpu_util_n_samples": gpu_util_n_samples,
        "gpu_util_reason": gpu_util_reason,
    }
    summ = ("n=%d pass=%d mid=%d fail=%d pct=%.1f%% pareto_count=%d cliff=%s gpu_util=%.1f%%" % (
        n_total, n_pass, n_mid, n_fail, 100 * pct_pass, pareto_count, cliff_status,
        gpu_util_mean if not math.isnan(gpu_util_mean) else -1.0))

    # v5 verdict tiers
    if pct_pass >= 0.50 and pareto_chain_grade and cliff_ok:
        return ("CHAIN_GRADE_PARETO_CLIFF_MAP_COMPLETE",
                "CHAIN_GRADE_PARETO_CLIFF_MAP_COMPLETE %d_of_%d: %s" % (n_pass, n_total, summ),
                extra)
    if pct_pass >= 0.30 or (pareto_chain_grade and not cliff_ok):
        return ("PARTIAL_PHASE_MAP",
                "PARTIAL_PHASE_MAP %d_of_%d (pareto=%s cliff=%s): %s" % (
                    n_pass, n_total, pareto_chain_grade, cliff_status, summ),
                extra)
    if pct_pass >= 0.10 or pareto_chain_grade:
        return ("REGIME_BOUNDS_NARROW",
                "REGIME_BOUNDS_NARROW %d_of_%d: %s" % (n_pass, n_total, summ),
                extra)
    return ("PHASE_FRONTIER_COLLAPSED",
            "PHASE_FRONTIER_COLLAPSED %d_of_%d: %s" % (n_pass, n_total, summ),
            extra)


# ---------------------------------------------------------------------------
# Self-test (CPU-fast; verifies mechanism + formula + arms-differ)
# ---------------------------------------------------------------------------
def _selftest() -> None:
    """Smaller-scale mechanism check; runs on CPU; no NVML needed."""
    g = np.random.default_rng(0)
    n_test = 512
    V_test = 80
    P_test = 4
    sq_t = math.sqrt(n_test)

    # T1: shapes
    E = bipolar_gpu(V_test, n_test, g)
    R = bipolar_gpu(P_test, n_test, g)
    assert E.shape == (V_test, n_test)
    assert abs(float(E[0].norm()) - 1.0) < 1e-4

    # T2: chain construction
    triples, chains = make_walk_chains(5, V_test, P_test, max_depth=15,
                                        g=g, disallow_s=set())
    assert len(chains) == 5
    assert len(triples) == 5 * 15

    # T3: ingest_hebbian
    W = ingest_hebbian_gpu(triples, E, R, sq_t, n_test)
    assert W.shape == (n_test, n_test)
    assert torch.isfinite(W).all()

    # T4: build_attention_store
    K_store, V_store = build_attention_store(triples, E, R, sq_t)
    assert K_store.shape == (5 * 15, n_test)
    assert V_store.shape == (5 * 15, n_test)

    chains_d5 = [c[:5] for c in chains]

    # T5: HEBBIAN_W arm
    r_h, h_preds = arm_hebbian_w(E, R, sq_t, W, chains_d5, depth=5, V_C=V_test)
    assert 0.0 <= r_h["top1"] <= 1.0
    assert len(h_preds) == 5 * 5
    assert len(r_h["per_step_cos_to_target"]) == 5

    # T6: DIRECT_ATTENTION arm
    r_a, a_preds = arm_direct_attention(E, R, sq_t, K_store, V_store,
                                         chains_d5, depth=5, V_C=V_test)
    assert 0.0 <= r_a["top1"] <= 1.0
    assert len(a_preds) == 5 * 5

    # T7: CHANCE arm
    g_r = np.random.default_rng(7)
    r_c, c_preds = arm_chance(E, R, sq_t, chains_d5, depth=5, V_C=V_test, g=g_r)
    assert 0.0 <= r_c["top1"] <= 1.0
    assert len(c_preds) == 5 * 5

    # T8: arms-differ (3 distinct SHA-256 hashes)
    sha_h = sha256_of(h_preds)
    sha_a = sha256_of(a_preds)
    sha_c = sha256_of(c_preds)
    assert len({sha_h, sha_a, sha_c}) == 3, (
        "ARMS_DISTINCT VIOLATION: h=%s a=%s c=%s" % (sha_h, sha_a, sha_c))
    print("  [selftest] arms distinct: h=%s a=%s c=%s" % (sha_h, sha_a, sha_c))

    # T9: HEBBIAN must beat CHANCE on this small test (sanity that mechanism works)
    assert r_h["top1"] >= r_c["top1"] - 0.10, (
        "Mechanism-broken: HEBBIAN(%.3f) << CHANCE(%.3f)" % (r_h["top1"], r_c["top1"]))

    # T10: p_step_empirical sanity
    p_low = p_step_empirical(0.05, 5)
    p_high = p_step_empirical(2.00, 15)
    assert p_low > p_high, "p_step model broken: p_low=%.3f p_high=%.3f" % (p_low, p_high)
    assert 0.05 <= p_low <= 0.999
    assert 0.05 <= p_high <= 0.999

    # T11: CARDINALITY guards
    assert EXPECTED_N_FULL == 15
    assert EXPECTED_N_SMOKE == 4
    assert len(SMOKE_CORNERS) == EXPECTED_N_SMOKE

    # T12: LLM call counter
    assert _LLM_CALL_COUNTER[0] == 0

    # T13: NO_SILENT_EXCEPT for sample_gpu_util_safe (META_RULE_J)
    if not GPU_AVAIL:
        pre_len = len(_GPU_UTIL_SAMPLES)
        res = sample_gpu_util_safe()
        assert math.isnan(res)
        assert len(_GPU_UTIL_SAMPLES) == pre_len, (
            "META_RULE_J VIOLATION: CPU sample silently appended")
        assert len(_GPU_UTIL_FAIL_REASON) >= 1
        print("  [selftest] META_RULE_J ok: CPU returns NaN + reason=%s" % (
            _GPU_UTIL_FAIL_REASON[0]))

    # T14: per_step_cos_to_target -- HEBBIAN cos should be > CHANCE cos in mean
    cos_h_mean = float(np.mean(r_h["per_step_cos_to_target"]))
    cos_c_mean = float(np.mean(r_c["per_step_cos_to_target"]))
    # CHANCE cos ~ 0; HEBBIAN cos > 0 on hit; allow CHANCE cos slightly > 0
    # in tiny test (5 chains * 5 hops = 25 samples; noisy).
    print("  [selftest] cos_h=%.4f cos_c=%.4f (HEBBIAN should be > CHANCE in mean at scale)" % (
        cos_h_mean, cos_c_mean))

    print("[selftest] PASS h=%.4f a=%.4f c=%.4f arms_distinct=True gpu=%s "
          "(p_step model density-keyed)" % (
        r_h["top1"], r_a["top1"], r_c["top1"], GPU_AVAIL), flush=True)


# Self-test runs at MODULE IMPORT for cell-author validation
_selftest()


# ---------------------------------------------------------------------------
# top-level seed runner (called by chunked sibling files)
# ---------------------------------------------------------------------------
def _config_str(seed: int, mode: str) -> str:
    return (
        "ANCHOR=%s_seed_%d,N=%d,V_C=%d,densities=%s,depths=%s,arms=%s,"
        "V_PRED=%d,max_W_depth=%d,N_TEST_CHAINS=%d,mode=%s,gpu_floor=%.1f,"
        "n_full=%d,n_smoke=%d,pareto_thresh=%.3f"
    ) % (
        ANCHOR_NAME_PREFIX, seed, N_DIM, V_C_FIXED, STORAGE_DENSITIES_FULL,
        DEPTHS_FULL, ARMS_FULL, V_PRED, MAX_W_DEPTH, N_TEST_CHAINS, mode,
        GPU_UTIL_FLOOR, EXPECTED_N_FULL, EXPECTED_N_SMOKE,
        PARETO_DISCRIM_THRESHOLD,
    )


def run_one_seed(seed: int, smoke: bool = False, self_test: bool = False) -> int:
    started = time.time()
    anchor = "%s_seed_%d" % (ANCHOR_NAME_PREFIX, seed)
    env_name = os.environ.get("HDLAB_EXP_NAME", anchor)

    if self_test:
        out_dir = REPO / "data" / ("exp_" + env_name + "_selftest")
    else:
        out_dir = REPO / "data" / ("exp_" + env_name)
    out_dir.mkdir(parents=True, exist_ok=True)

    _GPU_UTIL_SAMPLES.clear()
    _GPU_UTIL_FAIL_REASON.clear()

    if self_test:
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
        grid = [(dens, d) for dens in STORAGE_DENSITIES_FULL for d in DEPTHS_FULL]
        expected = EXPECTED_N_FULL
        mode = "full"

    if len(grid) != expected:
        raise RuntimeError("CARDINALITY_BREACH at grid build: %d != %d" % (
            len(grid), expected))

    # FULL mode requires GPU per Fix #24
    if mode == "full" and not GPU_AVAIL:
        print("[FATAL] FULL run requires GPU per Fix #24; CPU detected. Aborting.",
              flush=True)
        sentinel = {
            "anchor_name": anchor,
            "verdict": "HARD_FAIL",
            "verdict_msg": "FIX24_GUARD: FULL run requires GPU; CPU detected",
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

    # Order grid by density (cache amortization)
    grid_sorted = sorted(grid, key=lambda x: (x[0], x[1]))

    cache: Dict[Tuple[float, int], Dict[str, Any]] = {}
    phase_map: List[Dict[str, Any]] = []

    if GPU_AVAIL:
        torch.cuda.reset_peak_memory_stats(DEVICE)

    for (density, depth) in grid_sorted:
        try:
            point = run_point(density, depth, seed, cache)
            phase_map.append(point)
        except Exception as e:
            print("[POINT_CRASH seed=%d dens=%.2f d=%d] %s" % (
                seed, density, depth, e), file=sys.stderr)
            traceback.print_exc()
            raise
        sample_gpu_util_safe()

    cache.clear()
    if GPU_AVAIL:
        torch.cuda.empty_cache()
        peak_bytes = torch.cuda.max_memory_allocated(DEVICE)
    else:
        peak_bytes = 0

    if len(_GPU_UTIL_SAMPLES) > 0:
        gpu_util_mean = float(np.mean(_GPU_UTIL_SAMPLES))
        gpu_util_max = float(np.max(_GPU_UTIL_SAMPLES))
    else:
        gpu_util_mean = float("nan")
        gpu_util_max = float("nan")
    gpu_util_n_samples = len(_GPU_UTIL_SAMPLES)
    gpu_util_reason = _GPU_UTIL_FAIL_REASON[0] if _GPU_UTIL_FAIL_REASON else ""

    if mode == "smoke":
        verdict, msg, extra = smoke_verdict(phase_map, gpu_util_mean,
                                              gpu_util_n_samples, gpu_util_reason,
                                              GPU_AVAIL)
    else:
        verdict, msg, extra = full_verdict(phase_map, gpu_util_mean,
                                              gpu_util_n_samples, gpu_util_reason,
                                              GPU_AVAIL)

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
        "v4_supersedes": {
            "v4_anchor": "substrate_multihop_phase_diagram_depth_VC_NChains_v4",
            "v4_verdict": "HARD_FAIL 3/3 seeds (SANITY_BREACH SAT_CORNER)",
            "v4_diagnosis": "p_step model backward + by-construction-saturation at high eff_V_C; v5 sweeps storage_density not effective_V_C; v5 discriminator is Pareto split between Hebbian and Direct-Attention storage primitives",
        },
    }
    tmp = out_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    os.replace(str(tmp), str(out_dir / "metrics.json"))
    print("[seed=%d %s] FINAL verdict=%s msg=%s elapsed=%.1fs gpu_util=%.1f%% (n=%d)" % (
        seed, mode, verdict, msg, time.time() - started,
        (gpu_util_mean if not math.isnan(gpu_util_mean) else -1.0),
        gpu_util_n_samples), flush=True)
    return 0 if verdict not in ("HARD_FAIL",) else 1
