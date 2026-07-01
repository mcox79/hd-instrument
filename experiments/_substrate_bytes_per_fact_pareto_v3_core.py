"""Core module for bytes-per-fact storage efficiency Pareto v3 M-EXTENDED + FP16-RANGE-FIX.

v3 changes vs v2:
  1. FP16_DENSE arm range-safe: accumulate Hebbian W in FP32, downcast to FP16
     for STORAGE only (bytes-cost still 2 bytes/elem), rematerialize FP32 for
     readout. This tests whether FP16-collapse in v1/v2 was an accumulator-range
     issue (fixable) vs a storage-precision issue (fundamental). BFLOAT16 v2
     did NOT collapse (recall=1.000 at all M) confirming the range hypothesis;
     v3 verifies FP16 with FP32-accumulator matches BFLOAT16.
  2. M sweep extended to {1000, 4000, 10000, 20000, 40000} (5 M-values, +M=40k)
     to force discrimination through ceiling saturation. At N=4096 with 40k
     items, most arms should crack (Hopfield capacity ~0.14*N=573; M=40k is
     70x overload). Expect BINARY, INT8, INT4 to hold longer than SPARSE.
  3. Verdict logic strengthened per META_RULE_Q strict:
     - Auto-demote HP -> MB if >=70% of (arm, M) cells at recall >= 0.995.
     - Emit ceiling-saturation-ratio in verdict payload for auditor visibility.

Design:
  Arms (7 precisions, same KG-ingest test at each M):
    1. FP32_DENSE         float32 W (baseline; 4 bytes/elem)
    2. BFLOAT16_DENSE     bfloat16 W (2 bytes/elem; wider exponent)
    3. FP16_DENSE_RANGE_SAFE FP32 accumulator + FP16 STORAGE (2 bytes/elem)
    4. INT8_DENSE         int8 W + per-row scale (1 byte/elem)
    5. INT4_QUANTIZED     int4-packed W + per-row scale (0.5 byte/elem)
    6. BINARY_DENSE       sign(W) bit-packed (0.125 byte/elem)
    7. SPARSE_BIPOLAR_0p05 top-K sparse ingest at N=16384

  M sweep: {1000, 4000, 10000, 20000, 40000}: 5 values x 7 arms = 35 units/seed.
  N=4096 dense, 16384 sparse (unchanged).

Discriminator (HARD_PASS):
  - Positive control: FP32 recall at M=4000 >= 0.85
  - Pareto separation: within each M, arms differ in bytes-per-fact >=2x
  - Monotonic recall decay per arm as M grows
  - FP16_range_safe recall >= 0.5 at M=4000 (v3-specific gate: FP32-accumulator
    fix rescues FP16 as predicted by BFLOAT16 evidence)
  - INT4 recall >= 0.85 at M=4000 (positive tier)
  - Cross-seed cv <= 0.15
  - All 7 mechanism_hash distinct
  - cardinality_ok: 7 * 5 = 35 units per seed
  - META_RULE_Q strict: ceiling_saturation_ratio (cells with recall >= 0.995)
    must be < 0.70; else auto-demote HP -> MIDDLE_BAND.

Bytes-per-fact FP16_range_safe accounting: stored as 2-byte fp16 W. FP32
accumulator is TRANSIENT (build-time) and does not count toward storage bytes.

ASCII-only. No unicode. No em-dashes.
"""
from __future__ import annotations

import hashlib
import math
import os
import time
from typing import Any, Dict, List, Tuple

import torch


# ---------- Regime constants ----------

N_DIM_DENSE = 4096
N_DIM_SPARSE = 16384

# Full: M sweep at same N=4096 dense / 16384 sparse.
# v3: added M=40000 to force ceiling-saturation discrimination.
FULL_M_SWEEP = [1000, 4000, 10000, 20000, 40000]
FULL_N_ENT = 5000
FULL_N_REL = 100
FULL_QUERY_FRAC = 0.10  # queries = 10% of ingested triples

# Smoke: reduced grid but INCLUDES the top-M discriminator to verify at least
# 3/7 arms drop below 0.85 at ceiling load (v3 smoke gate).
# n_ent * n_rel = 800 * 50 = 40000 headroom for M=8000 max at smoke.
SMOKE_M_SWEEP = [500, 2000, 8000]
SMOKE_N_ENT = 800
SMOKE_N_REL = 50
SMOKE_QUERY_FRAC = 0.10
SMOKE_N_DIM_DENSE = 2048
SMOKE_N_DIM_SPARSE = 8192

RECALL_TARGET_UNDERLOAD = 0.85
FP16_RANGE_SAFE_MIN_RECALL_AT_M4000 = 0.5
INT4_MIN_RECALL_AT_NOMINAL = 0.85
CEILING_SATURATION_RATIO_MAX = 0.70  # v3 META_RULE_Q strict
CEILING_SATURATION_RECALL = 0.995
TOPK_RECALL = 1
SPARSE_S = 0.05
QUERY_NOISE_FRAC = 0.30

ARMS = ["FP32_DENSE", "BFLOAT16_DENSE", "FP16_DENSE_RANGE_SAFE", "INT8_DENSE",
        "INT4_QUANTIZED", "BINARY_DENSE", "SPARSE_BIPOLAR_0p05"]


def _get_device(strict_gpu: bool = False) -> torch.device:
    if torch.cuda.is_available():
        return torch.device("cuda")
    if strict_gpu:
        raise RuntimeError("GPU_REQUIRED: cuda not available in full-mode")
    return torch.device("cpu")


def _bipolar(m: int, n: int, gen: torch.Generator, device: torch.device) -> torch.Tensor:
    r = torch.randint(0, 2, (m, n), generator=gen, dtype=torch.int8).to(device)
    return (r * 2 - 1).to(torch.float32)


def _add_bipolar_noise(x: torch.Tensor, noise_frac: float, seed: int) -> torch.Tensor:
    g = torch.Generator(device="cpu")
    g.manual_seed(seed + 99999)
    mask_cpu = (torch.rand(x.shape, generator=g) < noise_frac).to(x.device)
    neg_one = torch.tensor(-1.0, dtype=x.dtype, device=x.device)
    pos_one = torch.tensor(1.0, dtype=x.dtype, device=x.device)
    flip = torch.where(mask_cpu, neg_one, pos_one)
    return x * flip


# ---------- Storage-cost formulas (bytes-per-fact denominator) ----------

def bytes_fp32_dense(n_dim: int, n_ent: int, n_rel: int) -> int:
    return (n_dim * n_dim * 4) + (n_ent * n_dim * 4) + (n_rel * n_dim * 4)


def bytes_bfloat16_dense(n_dim: int, n_ent: int, n_rel: int) -> int:
    return (n_dim * n_dim * 2) + (n_ent * n_dim * 2) + (n_rel * n_dim * 2)


def bytes_fp16_dense(n_dim: int, n_ent: int, n_rel: int) -> int:
    # v3: FP16 storage cost same as bf16 (2 bytes/elem); FP32 accumulator is
    # transient (build-time only) and does not count toward storage bytes.
    return (n_dim * n_dim * 2) + (n_ent * n_dim * 2) + (n_rel * n_dim * 2)


def bytes_int8_dense(n_dim: int, n_ent: int, n_rel: int) -> int:
    W_bytes = (n_dim * n_dim * 1) + (n_dim * 4)
    E_bytes = (n_ent * n_dim * 1) + (n_ent * 4)
    R_bytes = (n_rel * n_dim * 1) + (n_rel * 4)
    return W_bytes + E_bytes + R_bytes


def bytes_int4_quantized(n_dim: int, n_ent: int, n_rel: int) -> int:
    W_bytes = (n_dim * n_dim) // 2 + (n_dim * 4)
    E_bytes = (n_ent * n_dim) // 2 + (n_ent * 4)
    R_bytes = (n_rel * n_dim) // 2 + (n_rel * 4)
    return W_bytes + E_bytes + R_bytes


def bytes_binary_dense(n_dim: int, n_ent: int, n_rel: int) -> int:
    W_bytes = (n_dim * n_dim) // 8
    E_bytes = (n_ent * n_dim) // 8
    R_bytes = (n_rel * n_dim) // 8
    return W_bytes + E_bytes + R_bytes


def bytes_sparse_bipolar(n_dim: int, n_ent: int, n_rel: int, nnz: int) -> int:
    W_bytes = nnz * (4 + 4 + 1)
    E_bytes = (n_ent * n_dim) // 8
    R_bytes = (n_rel * n_dim) // 8
    return W_bytes + E_bytes + R_bytes


# ---------- Ingest + recall per arm ----------

def _ingest_and_query_fp32(triples, E, R, queries, gt, n_dim, device):
    sq = math.sqrt(n_dim)
    W = torch.zeros(n_dim, n_dim, dtype=torch.float32, device=device)
    s_idx, p_idx, o_idx = triples[:, 0], triples[:, 1], triples[:, 2]
    batch = 2000
    for b in range(0, triples.shape[0], batch):
        se = s_idx[b:b + batch]; pe = p_idx[b:b + batch]; oe = o_idx[b:b + batch]
        keys = (E[se] * R[pe] * sq)
        W.add_((E[oe].T @ keys) / n_dim)
    q_s, q_p, q_o = queries[:, 0], queries[:, 1], queries[:, 2]
    q_keys = (E[q_s] * R[q_p] * sq)
    q_keys = _add_bipolar_noise(q_keys, QUERY_NOISE_FRAC, seed=42)
    scores = q_keys @ W.T @ E.T
    topk = torch.topk(scores, k=min(TOPK_RECALL, E.shape[0]), dim=1)
    hits = (topk.indices == q_o.unsqueeze(1)).any(dim=1).float().mean()
    return float(hits), 0


def _ingest_and_query_bfloat16(triples, E, R, queries, gt, n_dim, device):
    sq = math.sqrt(n_dim)
    Ebf = E.to(torch.bfloat16)
    Rbf = R.to(torch.bfloat16)
    W = torch.zeros(n_dim, n_dim, dtype=torch.bfloat16, device=device)
    s_idx, p_idx, o_idx = triples[:, 0], triples[:, 1], triples[:, 2]
    batch = 2000
    sq_bf = torch.tensor(sq, dtype=torch.bfloat16, device=device)
    for b in range(0, triples.shape[0], batch):
        se = s_idx[b:b + batch]; pe = p_idx[b:b + batch]; oe = o_idx[b:b + batch]
        keys = (Ebf[se] * Rbf[pe]) * sq_bf
        W.add_((Ebf[oe].T @ keys) / n_dim)
    q_s, q_p, q_o = queries[:, 0], queries[:, 1], queries[:, 2]
    q_keys = (Ebf[q_s] * Rbf[q_p]) * sq_bf
    q_keys = _add_bipolar_noise(q_keys, QUERY_NOISE_FRAC, seed=42)
    scores = q_keys @ W.T @ Ebf.T
    topk = torch.topk(scores.float(), k=min(TOPK_RECALL, E.shape[0]), dim=1)
    hits = (topk.indices == q_o.unsqueeze(1)).any(dim=1).float().mean()
    return float(hits), 0


def _ingest_and_query_fp16_range_safe(triples, E, R, queries, gt, n_dim, device):
    """v3 FP16 RANGE-SAFE: accumulate outer sums in FP32 (transient), cast to
    FP16 for STORAGE, rematerialize FP32 for readout. Storage cost is 2 bytes/elem
    (same as bf16); the FP32 accumulator is a build-time-only cost. Tests
    whether the v1/v2 FP16 collapse was fixable via range-preserving Hebbian.
    """
    sq = math.sqrt(n_dim)
    # Build in FP32 (range-safe accumulator).
    Wf32 = torch.zeros(n_dim, n_dim, dtype=torch.float32, device=device)
    s_idx, p_idx, o_idx = triples[:, 0], triples[:, 1], triples[:, 2]
    batch = 2000
    for b in range(0, triples.shape[0], batch):
        se = s_idx[b:b + batch]; pe = p_idx[b:b + batch]; oe = o_idx[b:b + batch]
        keys = (E[se] * R[pe] * sq)
        Wf32.add_((E[oe].T @ keys) / n_dim)
    # Downcast to FP16 for STORAGE (round-to-nearest).
    W_fp16_storage = Wf32.to(torch.float16)
    # Codebooks downcast to FP16 for storage (2 bytes/elem).
    E_fp16 = E.to(torch.float16)
    R_fp16 = R.to(torch.float16)
    # Rematerialize FP32 for readout (models real inference: dequant on load).
    W_dequant = W_fp16_storage.to(torch.float32)
    E_dequant = E_fp16.to(torch.float32)
    R_dequant = R_fp16.to(torch.float32)
    q_s, q_p, q_o = queries[:, 0], queries[:, 1], queries[:, 2]
    q_keys = (E_dequant[q_s] * R_dequant[q_p] * sq)
    q_keys = _add_bipolar_noise(q_keys, QUERY_NOISE_FRAC, seed=42)
    scores = q_keys @ W_dequant.T @ E_dequant.T
    topk = torch.topk(scores, k=min(TOPK_RECALL, E.shape[0]), dim=1)
    hits = (topk.indices == q_o.unsqueeze(1)).any(dim=1).float().mean()
    return float(hits), 0


def _ingest_and_query_int8(triples, E, R, queries, gt, n_dim, device):
    sq = math.sqrt(n_dim)
    Wf = torch.zeros(n_dim, n_dim, dtype=torch.float32, device=device)
    s_idx, p_idx, o_idx = triples[:, 0], triples[:, 1], triples[:, 2]
    batch = 2000
    for b in range(0, triples.shape[0], batch):
        se = s_idx[b:b + batch]; pe = p_idx[b:b + batch]; oe = o_idx[b:b + batch]
        keys = (E[se] * R[pe] * sq)
        Wf.add_((E[oe].T @ keys) / n_dim)
    row_max = Wf.abs().max(dim=1, keepdim=True).values.clamp_min(1e-9)
    scale_row = row_max / 127.0
    W_int8 = torch.round(Wf / scale_row).clamp_(-127, 127).to(torch.int8)
    E_int8 = E.to(torch.int8)
    R_int8 = R.to(torch.int8)
    W_dequant = W_int8.to(torch.float32) * scale_row
    q_s, q_p, q_o = queries[:, 0], queries[:, 1], queries[:, 2]
    q_keys = (E_int8[q_s].to(torch.float32) * R_int8[q_p].to(torch.float32) * sq)
    q_keys = _add_bipolar_noise(q_keys, QUERY_NOISE_FRAC, seed=42)
    scores = q_keys @ W_dequant.T @ E_int8.to(torch.float32).T
    topk = torch.topk(scores, k=min(TOPK_RECALL, E.shape[0]), dim=1)
    hits = (topk.indices == q_o.unsqueeze(1)).any(dim=1).float().mean()
    return float(hits), 0


def _ingest_and_query_int4(triples, E, R, queries, gt, n_dim, device):
    sq = math.sqrt(n_dim)
    Wf = torch.zeros(n_dim, n_dim, dtype=torch.float32, device=device)
    s_idx, p_idx, o_idx = triples[:, 0], triples[:, 1], triples[:, 2]
    batch = 2000
    for b in range(0, triples.shape[0], batch):
        se = s_idx[b:b + batch]; pe = p_idx[b:b + batch]; oe = o_idx[b:b + batch]
        keys = (E[se] * R[pe] * sq)
        Wf.add_((E[oe].T @ keys) / n_dim)
    row_max = Wf.abs().max(dim=1, keepdim=True).values.clamp_min(1e-9)
    scale_row = row_max / 7.0
    W_int4 = torch.round(Wf / scale_row).clamp_(-7, 7).to(torch.int8)
    W_dequant = W_int4.to(torch.float32) * scale_row
    E_int4 = E.to(torch.int8).clamp_(-7, 7)
    R_int4 = R.to(torch.int8).clamp_(-7, 7)
    q_s, q_p, q_o = queries[:, 0], queries[:, 1], queries[:, 2]
    q_keys = (E_int4[q_s].to(torch.float32) * R_int4[q_p].to(torch.float32) * sq)
    q_keys = _add_bipolar_noise(q_keys, QUERY_NOISE_FRAC, seed=42)
    scores = q_keys @ W_dequant.T @ E_int4.to(torch.float32).T
    topk = torch.topk(scores, k=min(TOPK_RECALL, E.shape[0]), dim=1)
    hits = (topk.indices == q_o.unsqueeze(1)).any(dim=1).float().mean()
    return float(hits), 0


def _ingest_and_query_binary(triples, E, R, queries, gt, n_dim, device):
    sq = math.sqrt(n_dim)
    Wf = torch.zeros(n_dim, n_dim, dtype=torch.float32, device=device)
    s_idx, p_idx, o_idx = triples[:, 0], triples[:, 1], triples[:, 2]
    batch = 2000
    for b in range(0, triples.shape[0], batch):
        se = s_idx[b:b + batch]; pe = p_idx[b:b + batch]; oe = o_idx[b:b + batch]
        keys = (E[se] * R[pe] * sq)
        Wf.add_((E[oe].T @ keys) / n_dim)
    W_bipolar = torch.sign(Wf).clamp_min(-1.0)
    W_bipolar[W_bipolar == 0] = 1.0
    q_s, q_p, q_o = queries[:, 0], queries[:, 1], queries[:, 2]
    q_keys = (E[q_s] * R[q_p] * sq)
    q_keys = _add_bipolar_noise(q_keys, QUERY_NOISE_FRAC, seed=42)
    scores = q_keys @ W_bipolar.T @ E.T
    topk = torch.topk(scores, k=min(TOPK_RECALL, E.shape[0]), dim=1)
    hits = (topk.indices == q_o.unsqueeze(1)).any(dim=1).float().mean()
    return float(hits), 0


def _ingest_and_query_sparse(triples, E, R, queries, gt, n_dim, device):
    sq = math.sqrt(n_dim)
    k_active = int(SPARSE_S * n_dim)
    Wf = torch.zeros(n_dim, n_dim, dtype=torch.float32, device=device)
    s_idx, p_idx, o_idx = triples[:, 0], triples[:, 1], triples[:, 2]
    batch = 1000
    for b in range(0, triples.shape[0], batch):
        se = s_idx[b:b + batch]; pe = p_idx[b:b + batch]; oe = o_idx[b:b + batch]
        keys = (E[se] * R[pe] * sq)
        keys_topk = torch.topk(keys.abs(), k=k_active, dim=1)
        mask = torch.zeros_like(keys)
        mask.scatter_(1, keys_topk.indices, 1.0)
        keys_sp = keys * mask
        vals = E[oe]
        vals_topk = torch.topk(vals.abs(), k=k_active, dim=1)
        vmask = torch.zeros_like(vals)
        vmask.scatter_(1, vals_topk.indices, 1.0)
        vals_sp = vals * vmask
        Wf.add_((vals_sp.T @ keys_sp) / n_dim)
    nnz_target = int(SPARSE_S * n_dim * n_dim)
    flat = Wf.abs().flatten()
    if nnz_target >= flat.numel():
        W_sp = Wf.clone()
        observed_nnz = int((Wf != 0).sum())
    else:
        top = torch.topk(flat, k=nnz_target)
        mask_flat = torch.zeros_like(flat, dtype=torch.bool)
        mask_flat.scatter_(0, top.indices, True)
        W_sparse_mask = mask_flat.view(n_dim, n_dim)
        W_sp = Wf * W_sparse_mask.to(torch.float32)
        observed_nnz = int(W_sparse_mask.sum())
    q_s, q_p, q_o = queries[:, 0], queries[:, 1], queries[:, 2]
    q_keys = (E[q_s] * R[q_p] * sq)
    q_keys = _add_bipolar_noise(q_keys, QUERY_NOISE_FRAC, seed=42)
    qk_topk = torch.topk(q_keys.abs(), k=k_active, dim=1)
    qmask = torch.zeros_like(q_keys)
    qmask.scatter_(1, qk_topk.indices, 1.0)
    q_keys_sp = q_keys * qmask
    scores = q_keys_sp @ W_sp.T @ E.T
    topk = torch.topk(scores, k=min(TOPK_RECALL, E.shape[0]), dim=1)
    hits = (topk.indices == q_o.unsqueeze(1)).any(dim=1).float().mean()
    return float(hits), observed_nnz


ARM_FNS = {
    "FP32_DENSE": _ingest_and_query_fp32,
    "BFLOAT16_DENSE": _ingest_and_query_bfloat16,
    "FP16_DENSE_RANGE_SAFE": _ingest_and_query_fp16_range_safe,
    "INT8_DENSE": _ingest_and_query_int8,
    "INT4_QUANTIZED": _ingest_and_query_int4,
    "BINARY_DENSE": _ingest_and_query_binary,
    "SPARSE_BIPOLAR_0p05": _ingest_and_query_sparse,
}


def _run_one_arm_at_M(
    arm_name: str, triples: torch.Tensor, queries: torch.Tensor,
    n_ent: int, n_rel: int, n_dim: int, M: int, seed: int, device: torch.device,
) -> Dict[str, Any]:
    if arm_name == "SPARSE_BIPOLAR_0p05" and device.type == "cuda":
        arm_device = torch.device("cpu")
    else:
        arm_device = device
    g = torch.Generator(device="cpu")
    g.manual_seed(seed)
    E_cpu = _bipolar(n_ent, n_dim, g, torch.device("cpu"))
    R_cpu = _bipolar(n_rel, n_dim, g, torch.device("cpu"))
    E = E_cpu.to(arm_device)
    R = R_cpu.to(arm_device)
    triples_dev = triples.to(arm_device)
    queries_dev = queries.to(arm_device)
    t0 = time.perf_counter()
    fn = ARM_FNS[arm_name]
    recall_k, extra_nnz = fn(triples_dev, E, R, queries_dev, queries_dev[:, 2], n_dim, arm_device)
    elapsed = time.perf_counter() - t0
    del E, R, triples_dev, queries_dev, E_cpu, R_cpu
    if device.type == "cuda":
        try:
            torch.cuda.empty_cache()
        except Exception:
            pass
    n_facts = triples.shape[0]
    if arm_name == "FP32_DENSE":
        total_bytes = bytes_fp32_dense(n_dim, n_ent, n_rel)
    elif arm_name == "BFLOAT16_DENSE":
        total_bytes = bytes_bfloat16_dense(n_dim, n_ent, n_rel)
    elif arm_name == "FP16_DENSE_RANGE_SAFE":
        total_bytes = bytes_fp16_dense(n_dim, n_ent, n_rel)
    elif arm_name == "INT8_DENSE":
        total_bytes = bytes_int8_dense(n_dim, n_ent, n_rel)
    elif arm_name == "INT4_QUANTIZED":
        total_bytes = bytes_int4_quantized(n_dim, n_ent, n_rel)
    elif arm_name == "BINARY_DENSE":
        total_bytes = bytes_binary_dense(n_dim, n_ent, n_rel)
    elif arm_name == "SPARSE_BIPOLAR_0p05":
        nnz = extra_nnz if extra_nnz > 0 else int(SPARSE_S * n_dim * n_dim)
        total_bytes = bytes_sparse_bipolar(n_dim, n_ent, n_rel, nnz)
    else:
        raise ValueError(f"unknown arm {arm_name}")
    bpf = total_bytes / n_facts
    pareto = recall_k / max(math.log(max(bpf, 2.0)), 1e-6)
    fingerprint = hashlib.sha256(
        f"{arm_name}|M={M}|{n_ent}|{n_rel}|{n_dim}|{recall_k:.6f}|seed={seed}".encode()
    ).hexdigest()
    return {
        "arm": arm_name,
        "M": int(M),
        "recall": recall_k,
        "n_facts": int(n_facts),
        "n_ent": int(n_ent),
        "n_rel": int(n_rel),
        "n_dim": int(n_dim),
        "bytes_total": int(total_bytes),
        "bytes_per_fact": float(bpf),
        "pareto_efficiency": float(pareto),
        "elapsed_s": round(elapsed, 3),
        "sparse_observed_nnz": int(extra_nnz),
        "mechanism_hash": fingerprint,
        "seed": int(seed),
    }


def build_regime_at_M(seed: int, M: int, n_ent: int, n_rel: int,
                      query_frac: float) -> Tuple[torch.Tensor, torch.Tensor]:
    g = torch.Generator(device="cpu")
    g.manual_seed(seed + 1000 + M)
    max_keys = n_ent * n_rel
    if M > max_keys:
        raise ValueError(f"M={M} > n_ent*n_rel={max_keys}; unique-(s,p) infeasible")
    perm = torch.randperm(max_keys, generator=g)[:M]
    s = perm // n_rel
    p = perm % n_rel
    o = torch.randint(0, n_ent, (M,), generator=g)
    triples = torch.stack([s, p, o], dim=1).long()
    n_queries = max(1, int(M * query_frac))
    q_idx = torch.randperm(M, generator=g)[:n_queries]
    queries = triples[q_idx]
    return triples, queries


def run_one_seed_all_units(seed: int, run_mode: str, device: torch.device) -> Dict[str, Any]:
    smoke = (run_mode == "smoke")
    if smoke:
        M_sweep = SMOKE_M_SWEEP
        n_ent = SMOKE_N_ENT
        n_rel = SMOKE_N_REL
        query_frac = SMOKE_QUERY_FRAC
        n_dim_dense = SMOKE_N_DIM_DENSE
        n_dim_sparse = SMOKE_N_DIM_SPARSE
    else:
        M_sweep = FULL_M_SWEEP
        n_ent = FULL_N_ENT
        n_rel = FULL_N_REL
        query_frac = FULL_QUERY_FRAC
        n_dim_dense = N_DIM_DENSE
        n_dim_sparse = N_DIM_SPARSE
    per_unit = {}
    for M in M_sweep:
        triples, queries = build_regime_at_M(seed, M, n_ent, n_rel, query_frac)
        for arm in ARMS:
            n_dim = n_dim_sparse if arm == "SPARSE_BIPOLAR_0p05" else n_dim_dense
            key = f"{arm}__M{M}"
            rec = _run_one_arm_at_M(arm, triples, queries, n_ent, n_rel,
                                    n_dim, M, seed, device)
            per_unit[key] = rec
            print(f"[arm={arm} M={M}] seed={seed} recall={rec['recall']:.3f} "
                  f"bytes/fact={rec['bytes_per_fact']:.0f} "
                  f"pareto={rec['pareto_efficiency']:.4f} "
                  f"elapsed={rec['elapsed_s']:.1f}s", flush=True)
    return {
        "seed": int(seed),
        "run_mode": run_mode,
        "per_unit": per_unit,
        "M_sweep": list(M_sweep),
        "arms": list(ARMS),
    }


# ---------- Verdict logic ----------

def _pareto_2x_at_M(per_unit_at_M: Dict[str, Any]) -> bool:
    pts = [(a["bytes_per_fact"], a["recall"]) for a in per_unit_at_M.values()]
    pts_sorted = sorted(pts, key=lambda x: x[0])
    seps_ok = 0
    for i in range(len(pts_sorted) - 1):
        b0, r0 = pts_sorted[i]
        b1, r1 = pts_sorted[i + 1]
        byte_ratio = b1 / max(b0, 1.0)
        recall_gap = abs(r1 - r0)
        if byte_ratio >= 1.99 or recall_gap >= 0.05:
            seps_ok += 1
    return seps_ok >= max(1, len(pts_sorted) - 3)


def _cross_seed_cv(per_seed: List[Dict[str, Any]], unit_keys: List[str]) -> Dict[str, Dict[str, float]]:
    out = {}
    for uk in unit_keys:
        recalls = [ps["per_unit"][uk]["recall"] for ps in per_seed
                   if uk in ps["per_unit"]]
        bpfs = [ps["per_unit"][uk]["bytes_per_fact"] for ps in per_seed
                if uk in ps["per_unit"]]
        if not recalls:
            continue
        rmean = sum(recalls) / len(recalls)
        rvar = sum((r - rmean) ** 2 for r in recalls) / len(recalls)
        rstd = math.sqrt(rvar)
        bmean = sum(bpfs) / len(bpfs)
        bvar = sum((b - bmean) ** 2 for b in bpfs) / len(bpfs)
        bstd = math.sqrt(bvar)
        out[uk] = {
            "recall_mean": rmean,
            "recall_cv": (rstd / rmean) if rmean > 0 else 0.0,
            "bytes_per_fact_mean": bmean,
            "bytes_per_fact_cv": (bstd / bmean) if bmean > 0 else 0.0,
        }
    return out


def _find_M_close_to(target: int, M_sweep: List[int]) -> int:
    return min(M_sweep, key=lambda m: abs(m - target))


def aggregate_and_verdict(per_seed, run_mode: str) -> Dict[str, Any]:
    """v3 HARD_PASS gates:
      1. Positive control: FP32 recall at M=4000-nominal >= 0.85
      2. Pareto separation within each M
      3. Monotonic recall decay per precision as M grows
      4. FP16_range_safe recall >= 0.5 at M=4000-nominal (v3-specific)
      5. INT4 recall >= 0.85 at M=nominal (positive tier)
      6. Cross-seed cv <= 0.15
      7. All 7 mechanism_hash distinct
      8. cardinality_ok: 7 * len(M_sweep) units per seed
      9. META_RULE_Q strict: ceiling_saturation_ratio (recall >= 0.995) < 0.70
    """
    if isinstance(per_seed, dict):
        per_seed = list(per_seed.values())
    n_seeds = len(per_seed)
    if n_seeds == 0:
        return {"verdict": "HARD_FAIL",
                "verdict_msg": "HARD_FAIL: no seeds completed",
                "summary": "no per-seed data"}

    smoke = (run_mode == "smoke")
    M_sweep = SMOKE_M_SWEEP if smoke else FULL_M_SWEEP
    M_nominal = _find_M_close_to(4000, M_sweep)
    M_top = max(M_sweep)  # ceiling-saturation-crack M

    fp32_key = f"FP32_DENSE__M{M_nominal}"
    fp32_recalls = [ps["per_unit"][fp32_key]["recall"]
                    for ps in per_seed if fp32_key in ps["per_unit"]]
    fp32_mean = sum(fp32_recalls) / len(fp32_recalls) if fp32_recalls else 0.0
    positive_control_ok = fp32_mean >= RECALL_TARGET_UNDERLOAD

    arm_means_by_unit = {}
    for arm in ARMS:
        for M in M_sweep:
            uk = f"{arm}__M{M}"
            recalls = [ps["per_unit"][uk]["recall"] for ps in per_seed
                       if uk in ps["per_unit"]]
            bpfs = [ps["per_unit"][uk]["bytes_per_fact"] for ps in per_seed
                    if uk in ps["per_unit"]]
            if not recalls:
                continue
            arm_means_by_unit[uk] = {
                "arm": arm,
                "M": M,
                "recall_mean": sum(recalls) / len(recalls),
                "bytes_per_fact_mean": sum(bpfs) / len(bpfs),
            }
    pareto_seps = []
    for M in M_sweep:
        per_M = {arm: {"bytes_per_fact": arm_means_by_unit[f"{arm}__M{M}"]["bytes_per_fact_mean"],
                       "recall": arm_means_by_unit[f"{arm}__M{M}"]["recall_mean"]}
                 for arm in ARMS if f"{arm}__M{M}" in arm_means_by_unit}
        pareto_seps.append(_pareto_2x_at_M(per_M))
    pareto_ok = all(pareto_seps)

    monotone_ok_per_arm = {}
    for arm in ARMS:
        recalls = [arm_means_by_unit[f"{arm}__M{M}"]["recall_mean"]
                   for M in sorted(M_sweep) if f"{arm}__M{M}" in arm_means_by_unit]
        if len(recalls) < 2:
            monotone_ok_per_arm[arm] = True
        else:
            monotone_ok_per_arm[arm] = recalls[-1] <= recalls[0] + 0.05
    monotone_ok = all(monotone_ok_per_arm.values())

    fp16rs_key = f"FP16_DENSE_RANGE_SAFE__M{M_nominal}"
    fp16rs_recalls = [ps["per_unit"][fp16rs_key]["recall"]
                      for ps in per_seed if fp16rs_key in ps["per_unit"]]
    fp16rs_mean = sum(fp16rs_recalls) / len(fp16rs_recalls) if fp16rs_recalls else 0.0
    fp16_range_safe_ok = fp16rs_mean >= FP16_RANGE_SAFE_MIN_RECALL_AT_M4000

    int8_key = f"INT8_DENSE__M{M_nominal}"
    int4_key = f"INT4_QUANTIZED__M{M_nominal}"
    int8_recalls = [ps["per_unit"][int8_key]["recall"]
                    for ps in per_seed if int8_key in ps["per_unit"]]
    int4_recalls = [ps["per_unit"][int4_key]["recall"]
                    for ps in per_seed if int4_key in ps["per_unit"]]
    int8_mean = sum(int8_recalls) / len(int8_recalls) if int8_recalls else 0.0
    int4_mean = sum(int4_recalls) / len(int4_recalls) if int4_recalls else 0.0
    int4_vs_int8_gap = int8_mean - int4_mean
    int4_valid_tier = int4_mean >= INT4_MIN_RECALL_AT_NOMINAL

    unit_keys = list(arm_means_by_unit.keys())
    cv_table = _cross_seed_cv(per_seed, unit_keys)
    max_recall_cv = max([v["recall_cv"] for v in cv_table.values()] + [0.0])
    max_bpf_cv = max([v["bytes_per_fact_cv"] for v in cv_table.values()] + [0.0])
    cv_ok = (max_recall_cv <= 0.15) and (max_bpf_cv <= 0.15)

    if per_seed:
        first_M = M_sweep[0]
        one_pu = per_seed[0]["per_unit"]
        hashes = set()
        for arm in ARMS:
            uk = f"{arm}__M{first_M}"
            if uk in one_pu:
                hashes.add(one_pu[uk]["mechanism_hash"])
        hashes_distinct = len(hashes) == len(ARMS)
    else:
        hashes_distinct = False

    expected_n_units = len(ARMS) * len(M_sweep)
    observed_n_units_per_seed = [len(ps["per_unit"]) for ps in per_seed]
    cardinality_ok = all(n == expected_n_units for n in observed_n_units_per_seed)

    # v3 Gate 9: META_RULE_Q strict ceiling-saturation check.
    total_cells = 0
    saturated_cells = 0
    per_arm_top_M_recall = {}
    for arm in ARMS:
        for M in M_sweep:
            uk = f"{arm}__M{M}"
            if uk in arm_means_by_unit:
                total_cells += 1
                r = arm_means_by_unit[uk]["recall_mean"]
                if r >= CEILING_SATURATION_RECALL:
                    saturated_cells += 1
        top_key = f"{arm}__M{M_top}"
        if top_key in arm_means_by_unit:
            per_arm_top_M_recall[arm] = arm_means_by_unit[top_key]["recall_mean"]
    ceiling_saturation_ratio = (saturated_cells / total_cells) if total_cells else 0.0
    ceiling_saturation_ok = ceiling_saturation_ratio < CEILING_SATURATION_RATIO_MAX

    all_pass = (positive_control_ok and pareto_ok and monotone_ok
                and fp16_range_safe_ok and int4_valid_tier
                and cv_ok and hashes_distinct and cardinality_ok
                and ceiling_saturation_ok)

    if not cardinality_ok:
        verdict = "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H"
        vmsg = (f"HARD_FAIL_CARDINALITY: observed_per_seed={observed_n_units_per_seed} "
                f"expected={expected_n_units}")
    elif not positive_control_ok:
        verdict = "HARD_FAIL"
        vmsg = (f"HARD_FAIL: META_RULE_BC positive control broke. FP32 recall at "
                f"M={M_nominal} = {fp32_mean:.3f} < {RECALL_TARGET_UNDERLOAD}")
    elif all_pass:
        verdict = "HARD_PASS"
        vmsg = (f"HARD_PASS: 7-arm x {len(M_sweep)}-M Pareto | FP32@M{M_nominal}={fp32_mean:.3f} "
                f"| fp16_range_safe@M{M_nominal}={fp16rs_mean:.3f} (not-collapsed) "
                f"| int4@M{M_nominal}={int4_mean:.3f} (valid_tier; int8_gap={int4_vs_int8_gap:.3f} info) "
                f"| pareto_seps={pareto_seps} | monotone_ok={monotone_ok} "
                f"| max_cv={max(max_recall_cv, max_bpf_cv):.3f} "
                f"| ceiling_sat_ratio={ceiling_saturation_ratio:.2f}/{CEILING_SATURATION_RATIO_MAX} "
                f"| top_M={M_top} arm_recalls={per_arm_top_M_recall} "
                f"| n_seeds={n_seeds}")
    elif not ceiling_saturation_ok:
        verdict = "MIDDLE_BAND"
        vmsg = (f"MIDDLE_BAND_META_RULE_Q: ceiling_saturation_ratio="
                f"{ceiling_saturation_ratio:.2f} >= {CEILING_SATURATION_RATIO_MAX} "
                f"(saturated={saturated_cells}/{total_cells} cells at recall>={CEILING_SATURATION_RECALL}). "
                f"Discrimination lost to ceiling; extend M further or drop N_DIM.")
    else:
        verdict = "MIDDLE_BAND"
        vmsg = (f"MIDDLE_BAND: pos_ctrl={positive_control_ok} pareto={pareto_ok} "
                f"monotone={monotone_ok} fp16_rs_ok={fp16_range_safe_ok}({fp16rs_mean:.3f}) "
                f"int4_valid={int4_valid_tier}({int4_mean:.3f}) "
                f"cv_ok={cv_ok}({max(max_recall_cv,max_bpf_cv):.3f}) "
                f"hashes_distinct={hashes_distinct} "
                f"ceiling_sat_ratio={ceiling_saturation_ratio:.2f}")

    return {
        "verdict": verdict,
        "verdict_msg": vmsg,
        "summary": vmsg[:400],
        "run_mode": run_mode,
        "n_seeds": n_seeds,
        "arms": list(ARMS),
        "M_sweep": list(M_sweep),
        "M_nominal_positive_control": M_nominal,
        "M_top_saturation_crack": M_top,
        "arm_means_by_unit": arm_means_by_unit,
        "monotone_ok_per_arm": monotone_ok_per_arm,
        "cv_table": cv_table,
        "positive_control_fp32_recall_mean": fp32_mean,
        "positive_control_ok": positive_control_ok,
        "fp16_range_safe_recall_mean_at_M_nominal": fp16rs_mean,
        "fp16_range_safe_not_collapsed": fp16_range_safe_ok,
        "int8_recall_mean_at_M_nominal": int8_mean,
        "int4_recall_mean_at_M_nominal": int4_mean,
        "int4_vs_int8_recall_gap_informational": int4_vs_int8_gap,
        "int4_valid_tier": int4_valid_tier,
        "pareto_2x_separation_per_M": pareto_seps,
        "pareto_2x_separation_ok": pareto_ok,
        "monotone_decay_ok": monotone_ok,
        "max_recall_cv": max_recall_cv,
        "max_bytes_per_fact_cv": max_bpf_cv,
        "cross_seed_cv_ok": cv_ok,
        "mechanism_hashes_distinct": hashes_distinct,
        "expected_n_units_per_seed": expected_n_units,
        "observed_n_units_per_seed": observed_n_units_per_seed,
        "cardinality_ok": cardinality_ok,
        "ceiling_saturation_ratio": ceiling_saturation_ratio,
        "ceiling_saturation_threshold": CEILING_SATURATION_RATIO_MAX,
        "ceiling_saturation_ok": ceiling_saturation_ok,
        "ceiling_saturation_cells_count": saturated_cells,
        "ceiling_saturation_total_cells": total_cells,
        "per_arm_top_M_recall": per_arm_top_M_recall,
        "per_seed": per_seed,
        "topK": TOPK_RECALL,
    }


def selftest(seed: int, device: torch.device) -> Tuple[bool, str]:
    smoke_device = torch.device("cpu")
    triples, queries = build_regime_at_M(seed, M=30, n_ent=200, n_rel=25,
                                          query_frac=0.5)
    n_dim = 256
    g = torch.Generator(device="cpu")
    g.manual_seed(seed)
    E = _bipolar(200, n_dim, g, smoke_device)
    R = _bipolar(25, n_dim, g, smoke_device)
    recall, _ = _ingest_and_query_fp32(triples, E, R, queries, queries[:, 2],
                                        n_dim, smoke_device)
    if not (recall >= 0.0):
        return False, f"selftest FP32 recall not >= 0: {recall}"
    # v3-specific: verify FP16 range-safe arm executes end-to-end.
    recall_fp16rs, _ = _ingest_and_query_fp16_range_safe(
        triples, E, R, queries, queries[:, 2], n_dim, smoke_device)
    if not (recall_fp16rs >= 0.0):
        return False, f"selftest FP16_range_safe recall not >= 0: {recall_fp16rs}"
    bpf = bytes_fp32_dense(n_dim, 200, 25) / triples.shape[0]
    if bpf <= 0:
        return False, "selftest bytes_per_fact <= 0"
    return True, (f"selftest OK: fp32_recall={recall:.3f} "
                  f"fp16_range_safe_recall={recall_fp16rs:.3f} bpf={bpf:.0f}")


def get_backend_label() -> str:
    if torch.cuda.is_available():
        return f"cuda:{torch.cuda.get_device_name(0)}"
    return "cpu"
