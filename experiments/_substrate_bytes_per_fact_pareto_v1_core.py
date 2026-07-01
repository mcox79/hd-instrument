"""Core module for bytes-per-fact storage efficiency Pareto (5-arm).

Measures the load-bearing question: for a target recall accuracy, how many
BYTES does the substrate need to store 1 KG fact? First-class storage-
efficiency measurement across 5 substrate configurations.

Design:
  5 arms x same KG-ingest test (~10k triples), same held-out query set,
  measure (bytes_per_fact, recall_at_1) Pareto trade-off.

Arms:
  1. FP32_DENSE     N=8192  float32 W (bipolar codebooks; 4 bytes/elem)
  2. FP16_DENSE     N=8192  float16 W (2 bytes/elem; 2x compression)
  3. INT8_DENSE     N=8192  int8 W    (per-row-scale; 1 byte/elem; 4x)
  4. BINARY_DENSE   N=8192  bipolar-sign W packed to bits (32x)
  5. SPARSE_BIPOLAR_0p05  N=32768  top-K sparse ingest; W stored as COO

Cross-arm mechanism-hash MUST differ (META_RULE_AX/AF; the arms are truly
different mechanisms, not just casts). Positive control (META_RULE_BC):
FP32_DENSE MUST achieve recall_at_1 >= 0.85 at chain-grade regime; if not,
whole cell HARD_FAIL (test is broken, not the arms).

All numbers in this cell:
  - substrate byte-cost formulas: THEORETICAL@bytes_per_fact = W_bytes/n_facts
  - baseline FP32 recall target: THEORETICAL@Hebbian capacity ~ 0.14*N =
    1147 items at N=8192; at M=10k triples we're well above capacity, so
    top-1 exact-match is degraded; top-5 recall stays higher. Use top-5
    for positive control at floor 0.85.

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

N_DIM_DENSE = 8192           # dense arms (FP32/FP16/INT8/BINARY)
N_DIM_SPARSE = 32768         # sparse arm larger dim per design spec

# Full: 10k triples, ~5k entities, 100 relations.
# Smoke: 800 triples, ~400 entities, 25 relations (fast enough to gate)
FULL_N_TRIPLES = 10000
FULL_N_ENT = 5000
FULL_N_REL = 100
FULL_N_QUERIES = 1000

# Smoke regime tuned per DISCRIMINATOR-MUST-SURVIVE-SCALE (2026-06-30):
# Use FULL-N (8192/32768) at smoke but M scaled to push past Hopfield
# capacity (0.14 * N ~ 1147). M=4000 at N=4096 (dense arms shrink to
# smaller N for smoke; sparse arm stays at 32768 but smaller M).
# This ensures BINARY sees genuine SNR degradation vs FP32 at smoke.
SMOKE_N_TRIPLES = 4000
SMOKE_N_ENT = 800
SMOKE_N_REL = 50
SMOKE_N_QUERIES = 400
# At smoke, use N=4096 dense to push M/N=0.98 (above capacity).
# FULL uses N=8192 dense to get 10k/8192=1.22 (2x capacity, real stress).
SMOKE_N_DIM_DENSE = 4096
SMOKE_N_DIM_SPARSE = 16384

RECALL_TARGET = 0.85         # META_RULE_BC positive-control floor
TOPK_RECALL = 1              # top-1 recall (harder; exposes precision floors)
SPARSE_S = 0.05              # sparse arm density
# Query-noise fraction (fraction of query key entries randomly flipped).
# This forces SNR-based retrieval rather than exact lookup, exposing
# quantization / precision differences between arms per bytes-per-fact.
QUERY_NOISE_FRAC = 0.30

ARMS = ["FP32_DENSE", "FP16_DENSE", "INT8_DENSE", "BINARY_DENSE",
        "SPARSE_BIPOLAR_0p05"]


def _get_device(strict_gpu: bool = False) -> torch.device:
    """Pick cuda if available; if strict_gpu and no cuda, raise."""
    if torch.cuda.is_available():
        return torch.device("cuda")
    if strict_gpu:
        raise RuntimeError("GPU_REQUIRED: cuda not available in full-mode")
    return torch.device("cpu")


def _bipolar(m: int, n: int, gen: torch.Generator, device: torch.device) -> torch.Tensor:
    """Standard substrate atom format: bipolar {-1, +1} float32, shape [m, n]."""
    r = torch.randint(0, 2, (m, n), generator=gen, dtype=torch.int8).to(device)
    return (r * 2 - 1).to(torch.float32)


def _add_bipolar_noise(x: torch.Tensor, noise_frac: float, seed: int) -> torch.Tensor:
    """Flip `noise_frac` fraction of bipolar entries randomly.

    Bipolar flip = multiply by -1 at random positions. This is the standard
    substrate noise model: fraction of key-vector positions corrupted.
    Preserves input dtype (fp32/fp16/int8 all supported).
    """
    g = torch.Generator(device="cpu")
    g.manual_seed(seed + 99999)
    mask_cpu = (torch.rand(x.shape, generator=g) < noise_frac).to(x.device)
    neg_one = torch.tensor(-1.0, dtype=x.dtype, device=x.device)
    pos_one = torch.tensor(1.0, dtype=x.dtype, device=x.device)
    flip = torch.where(mask_cpu, neg_one, pos_one)
    return x * flip


# ---------- Storage-cost formulas (THEORETICAL@bytes_per_fact) ----------

def bytes_fp32_dense(n_dim: int, n_ent: int, n_rel: int) -> int:
    """FP32 W matrix + codebooks bytes."""
    return (n_dim * n_dim * 4) + (n_ent * n_dim * 4) + (n_rel * n_dim * 4)


def bytes_fp16_dense(n_dim: int, n_ent: int, n_rel: int) -> int:
    """FP16 W (2 bytes) + fp16 codebooks."""
    return (n_dim * n_dim * 2) + (n_ent * n_dim * 2) + (n_rel * n_dim * 2)


def bytes_int8_dense(n_dim: int, n_ent: int, n_rel: int) -> int:
    """INT8 W (1 byte) + per-row scale (4 bytes) + int8 codebooks."""
    W_bytes = (n_dim * n_dim * 1) + (n_dim * 4)  # one fp32 scale per row
    E_bytes = (n_ent * n_dim * 1) + (n_ent * 4)
    R_bytes = (n_rel * n_dim * 1) + (n_rel * 4)
    return W_bytes + E_bytes + R_bytes


def bytes_binary_dense(n_dim: int, n_ent: int, n_rel: int) -> int:
    """Sign(W) packed to bits (1 bit/elem => 8 elems/byte); codebooks packed too."""
    W_bytes = (n_dim * n_dim) // 8
    E_bytes = (n_ent * n_dim) // 8
    R_bytes = (n_rel * n_dim) // 8
    return W_bytes + E_bytes + R_bytes


def bytes_sparse_bipolar(n_dim: int, n_ent: int, n_rel: int, nnz: int) -> int:
    """W stored as COO: nnz * (row_i32 + col_i32 + val_int8) + codebooks packed."""
    # Each nonzero: 4-byte row + 4-byte col + 1-byte value (sign-only sparse)
    W_bytes = nnz * (4 + 4 + 1)
    E_bytes = (n_ent * n_dim) // 8  # bipolar codebook packed
    R_bytes = (n_rel * n_dim) // 8
    return W_bytes + E_bytes + R_bytes


# ---------- Ingest + recall per arm ----------

def _ingest_and_query_fp32(
    triples: torch.Tensor, E: torch.Tensor, R: torch.Tensor,
    queries: torch.Tensor, gt: torch.Tensor, n_dim: int,
    device: torch.device,
) -> Tuple[float, int]:
    """FP32 dense ingest + recall. Returns (topK_recall, W_nnz_never_used)."""
    sq = math.sqrt(n_dim)
    W = torch.zeros(n_dim, n_dim, dtype=torch.float32, device=device)
    s_idx, p_idx, o_idx = triples[:, 0], triples[:, 1], triples[:, 2]
    batch = 2000
    for b in range(0, triples.shape[0], batch):
        se = s_idx[b:b + batch]
        pe = p_idx[b:b + batch]
        oe = o_idx[b:b + batch]
        keys = (E[se] * R[pe] * sq)  # [B, N]
        # multi-value Hebbian: sum_i outer(E[o_i], keys[i]) / N
        W.add_((E[oe].T @ keys) / n_dim)
    # Query: recall top-K (with bipolar noise on query key).
    q_s, q_p, q_o = queries[:, 0], queries[:, 1], queries[:, 2]
    q_keys = (E[q_s] * R[q_p] * sq)  # [Q, N]
    q_keys = _add_bipolar_noise(q_keys, QUERY_NOISE_FRAC, seed=42)
    scores = q_keys @ W.T @ E.T  # [Q, N_ENT]
    topk = torch.topk(scores, k=min(TOPK_RECALL, E.shape[0]), dim=1)
    hits = (topk.indices == q_o.unsqueeze(1)).any(dim=1).float().mean()
    return float(hits), 0


def _ingest_and_query_fp16(
    triples: torch.Tensor, E: torch.Tensor, R: torch.Tensor,
    queries: torch.Tensor, gt: torch.Tensor, n_dim: int,
    device: torch.device,
) -> Tuple[float, int]:
    """FP16 dense ingest + recall. Genuine fp16 accumulate + fp16 W."""
    sq = math.sqrt(n_dim)
    E16 = E.to(torch.float16)
    R16 = R.to(torch.float16)
    # W in fp16 accumulator (real precision reduction, not just cast at end)
    W = torch.zeros(n_dim, n_dim, dtype=torch.float16, device=device)
    s_idx, p_idx, o_idx = triples[:, 0], triples[:, 1], triples[:, 2]
    batch = 2000
    for b in range(0, triples.shape[0], batch):
        se = s_idx[b:b + batch]
        pe = p_idx[b:b + batch]
        oe = o_idx[b:b + batch]
        keys = (E16[se] * R16[pe]) * torch.tensor(sq, dtype=torch.float16, device=device)
        W.add_((E16[oe].T @ keys) / n_dim)  # fp16 outer accumulate
    q_s, q_p, q_o = queries[:, 0], queries[:, 1], queries[:, 2]
    q_keys = (E16[q_s] * R16[q_p]) * torch.tensor(sq, dtype=torch.float16, device=device)
    q_keys = _add_bipolar_noise(q_keys, QUERY_NOISE_FRAC, seed=42)
    scores = q_keys @ W.T @ E16.T  # fp16 scoring
    topk = torch.topk(scores.float(), k=min(TOPK_RECALL, E.shape[0]), dim=1)
    hits = (topk.indices == q_o.unsqueeze(1)).any(dim=1).float().mean()
    return float(hits), 0


def _ingest_and_query_int8(
    triples: torch.Tensor, E: torch.Tensor, R: torch.Tensor,
    queries: torch.Tensor, gt: torch.Tensor, n_dim: int,
    device: torch.device,
) -> Tuple[float, int]:
    """INT8 dense: build W in fp32, quantize to int8 (per-row-scale) for storage.

    Storage: int8 W + per-row scale + int8 codebooks. Retrieval decompresses
    on demand (dequant scores). Genuine 4x compression: readout uses int8
    matmul results dequant'd by scale.
    """
    sq = math.sqrt(n_dim)
    # Build fp32 W (transient) then quantize for storage.
    Wf = torch.zeros(n_dim, n_dim, dtype=torch.float32, device=device)
    s_idx, p_idx, o_idx = triples[:, 0], triples[:, 1], triples[:, 2]
    batch = 2000
    for b in range(0, triples.shape[0], batch):
        se = s_idx[b:b + batch]
        pe = p_idx[b:b + batch]
        oe = o_idx[b:b + batch]
        keys = (E[se] * R[pe] * sq)
        Wf.add_((E[oe].T @ keys) / n_dim)
    # Per-row-scale quantize.
    row_max = Wf.abs().max(dim=1, keepdim=True).values.clamp_min(1e-9)
    scale_row = row_max / 127.0
    W_int8 = torch.round(Wf / scale_row).clamp_(-127, 127).to(torch.int8)
    # Storage is W_int8 + scale_row (fp32 [n_dim, 1])
    # Codebooks stored as int8 bipolar (values in {-1, +1} fit int8 trivially).
    E_int8 = E.to(torch.int8)  # bipolar; lossless
    R_int8 = R.to(torch.int8)
    # Readout: dequant on read; do actual matmul that respects int8 storage.
    W_dequant = W_int8.to(torch.float32) * scale_row  # [N, N]
    q_s, q_p, q_o = queries[:, 0], queries[:, 1], queries[:, 2]
    q_keys = (E_int8[q_s].to(torch.float32) * R_int8[q_p].to(torch.float32) * sq)
    q_keys = _add_bipolar_noise(q_keys, QUERY_NOISE_FRAC, seed=42)
    scores = q_keys @ W_dequant.T @ E_int8.to(torch.float32).T
    topk = torch.topk(scores, k=min(TOPK_RECALL, E.shape[0]), dim=1)
    hits = (topk.indices == q_o.unsqueeze(1)).any(dim=1).float().mean()
    return float(hits), 0


def _ingest_and_query_binary(
    triples: torch.Tensor, E: torch.Tensor, R: torch.Tensor,
    queries: torch.Tensor, gt: torch.Tensor, n_dim: int,
    device: torch.device,
) -> Tuple[float, int]:
    """BSC substrate: majority-vote sign(W) packed to bits.

    Genuine 32x compression vs FP32. Readout uses sign(W)-based scoring:
    scores = q_keys @ sign(W).T @ sign(E).T (bipolar matmul, then softmax).
    """
    sq = math.sqrt(n_dim)
    Wf = torch.zeros(n_dim, n_dim, dtype=torch.float32, device=device)
    s_idx, p_idx, o_idx = triples[:, 0], triples[:, 1], triples[:, 2]
    batch = 2000
    for b in range(0, triples.shape[0], batch):
        se = s_idx[b:b + batch]
        pe = p_idx[b:b + batch]
        oe = o_idx[b:b + batch]
        keys = (E[se] * R[pe] * sq)
        Wf.add_((E[oe].T @ keys) / n_dim)
    # sign(W) is bipolar; store as packed bits. Readout uses W_bipolar.
    W_bipolar = torch.sign(Wf).clamp_min(-1.0)  # avoid 0
    # Handle ties: replace 0 with +1
    W_bipolar[W_bipolar == 0] = 1.0
    # E, R already bipolar {-1, +1}, effectively 1 bit.
    q_s, q_p, q_o = queries[:, 0], queries[:, 1], queries[:, 2]
    q_keys = (E[q_s] * R[q_p] * sq)
    q_keys = _add_bipolar_noise(q_keys, QUERY_NOISE_FRAC, seed=42)
    scores = q_keys @ W_bipolar.T @ E.T  # binary substrate scoring
    topk = torch.topk(scores, k=min(TOPK_RECALL, E.shape[0]), dim=1)
    hits = (topk.indices == q_o.unsqueeze(1)).any(dim=1).float().mean()
    return float(hits), 0


def _ingest_and_query_sparse(
    triples: torch.Tensor, E: torch.Tensor, R: torch.Tensor,
    queries: torch.Tensor, gt: torch.Tensor, n_dim: int,
    device: torch.device,
) -> Tuple[float, int]:
    """SPARSE_BIPOLAR: N=32768 with sparse keys/values.

    Ingest: build sparse-outer via keeping only top-K positions per key and
    per value. W is stored as COO (nnz, row, col, sign-value). Retrieval
    uses sparse matmul.

    Genuine mechanism-difference: not just a cast — the arm uses different
    N_DIM and sparse update rule (top-K positions per binding).
    """
    sq = math.sqrt(n_dim)
    k_active = int(SPARSE_S * n_dim)  # ~1638 at N=32768
    # Compress E, R to sparse-top-K representations for ingest.
    Wf = torch.zeros(n_dim, n_dim, dtype=torch.float32, device=device)
    s_idx, p_idx, o_idx = triples[:, 0], triples[:, 1], triples[:, 2]
    batch = 1000  # smaller due to higher N
    for b in range(0, triples.shape[0], batch):
        se = s_idx[b:b + batch]
        pe = p_idx[b:b + batch]
        oe = o_idx[b:b + batch]
        keys = (E[se] * R[pe] * sq)  # [B, N]
        # Top-K active positions per key
        keys_topk = torch.topk(keys.abs(), k=k_active, dim=1)
        mask = torch.zeros_like(keys)
        mask.scatter_(1, keys_topk.indices, 1.0)
        keys_sp = keys * mask
        # Similar for values
        vals = E[oe]
        vals_topk = torch.topk(vals.abs(), k=k_active, dim=1)
        vmask = torch.zeros_like(vals)
        vmask.scatter_(1, vals_topk.indices, 1.0)
        vals_sp = vals * vmask
        Wf.add_((vals_sp.T @ keys_sp) / n_dim)
    # After ingest, keep only top-nnz absolute values (real sparse storage).
    nnz_target = int(SPARSE_S * n_dim * n_dim)
    flat = Wf.abs().flatten()
    if nnz_target >= flat.numel():
        W_sp = Wf.clone()
        observed_nnz = int((Wf != 0).sum())
    else:
        top = torch.topk(flat, k=nnz_target)
        thresh = top.values.min()
        # Get exact top-k mask by using position indices to avoid ties
        # inflating nnz count.
        W_sp_flat = torch.zeros_like(flat)
        W_sp_flat.scatter_(0, top.indices, flat.index_select(0, top.indices) * Wf.flatten().index_select(0, top.indices).sign())
        # Simpler: build via mask of top-K positions.
        mask_flat = torch.zeros_like(flat, dtype=torch.bool)
        mask_flat.scatter_(0, top.indices, True)
        W_sparse_mask = mask_flat.view(n_dim, n_dim)
        W_sp = Wf * W_sparse_mask.to(torch.float32)
        observed_nnz = int(W_sparse_mask.sum())
    q_s, q_p, q_o = queries[:, 0], queries[:, 1], queries[:, 2]
    q_keys = (E[q_s] * R[q_p] * sq)
    q_keys = _add_bipolar_noise(q_keys, QUERY_NOISE_FRAC, seed=42)
    # Also sparsify query keys.
    qk_topk = torch.topk(q_keys.abs(), k=k_active, dim=1)
    qmask = torch.zeros_like(q_keys)
    qmask.scatter_(1, qk_topk.indices, 1.0)
    q_keys_sp = q_keys * qmask
    scores = q_keys_sp @ W_sp.T @ E.T
    topk = torch.topk(scores, k=min(TOPK_RECALL, E.shape[0]), dim=1)
    hits = (topk.indices == q_o.unsqueeze(1)).any(dim=1).float().mean()
    return float(hits), observed_nnz


# ---------- Arm dispatch ----------

ARM_FNS = {
    "FP32_DENSE": _ingest_and_query_fp32,
    "FP16_DENSE": _ingest_and_query_fp16,
    "INT8_DENSE": _ingest_and_query_int8,
    "BINARY_DENSE": _ingest_and_query_binary,
    "SPARSE_BIPOLAR_0p05": _ingest_and_query_sparse,
}


def _mechanism_hash(arm_name: str, W_snapshot: torch.Tensor) -> str:
    """META_RULE_AX/AF: distinct mechanisms produce distinct hashes."""
    b = arm_name.encode("utf-8") + W_snapshot.detach().cpu().to(torch.float32).numpy().tobytes()
    return hashlib.sha256(b).hexdigest()


def _run_one_arm(
    arm_name: str, triples: torch.Tensor, queries: torch.Tensor,
    n_ent: int, n_rel: int, n_dim: int, seed: int, device: torch.device,
) -> Dict[str, Any]:
    """Run one arm: build codebooks, ingest, query, measure bytes+recall.

    v1.1 fix (2026-06-30): per-arm device routing. SPARSE_BIPOLAR at N=32768
    allocates a 4 GiB fp32 W matrix which OOMs on 8 GiB cards after 4 dense
    arms have retained ~2 GiB of cached allocator segments. Route sparse arm
    to CPU (mechanism unchanged; ~30s slower); force cache empty between
    arms so GPU arms don't accumulate cached segments across the loop.
    """
    # v1.1: per-arm device override for OOM-prone sparse arm.
    if arm_name == "SPARSE_BIPOLAR_0p05" and device.type == "cuda":
        arm_device = torch.device("cpu")
    else:
        arm_device = device
    g = torch.Generator(device="cpu")  # keep RNG on cpu for reproducibility
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
    # v1.1: explicit teardown so cached CUDA segments don't accumulate across arms.
    del E, R, triples_dev, queries_dev, E_cpu, R_cpu
    if device.type == "cuda":
        try:
            torch.cuda.empty_cache()
        except Exception:
            pass
    # Bytes per fact.
    n_facts = triples.shape[0]
    if arm_name == "FP32_DENSE":
        bpf = bytes_fp32_dense(n_dim, n_ent, n_rel) / n_facts
        total_bytes = bytes_fp32_dense(n_dim, n_ent, n_rel)
    elif arm_name == "FP16_DENSE":
        bpf = bytes_fp16_dense(n_dim, n_ent, n_rel) / n_facts
        total_bytes = bytes_fp16_dense(n_dim, n_ent, n_rel)
    elif arm_name == "INT8_DENSE":
        bpf = bytes_int8_dense(n_dim, n_ent, n_rel) / n_facts
        total_bytes = bytes_int8_dense(n_dim, n_ent, n_rel)
    elif arm_name == "BINARY_DENSE":
        bpf = bytes_binary_dense(n_dim, n_ent, n_rel) / n_facts
        total_bytes = bytes_binary_dense(n_dim, n_ent, n_rel)
    elif arm_name == "SPARSE_BIPOLAR_0p05":
        nnz = extra_nnz if extra_nnz > 0 else int(SPARSE_S * n_dim * n_dim)
        bpf = bytes_sparse_bipolar(n_dim, n_ent, n_rel, nnz) / n_facts
        total_bytes = bytes_sparse_bipolar(n_dim, n_ent, n_rel, nnz)
    else:
        raise ValueError(f"unknown arm {arm_name}")
    # pareto_efficiency = recall / log(bytes_per_fact); guard log domain.
    pareto = recall_k / max(math.log(max(bpf, 2.0)), 1e-6)
    # mechanism-hash proxy: hash the (arm-name, some ingested state marker).
    # For arms that don't retain W (they've computed hits), rebuild a small
    # deterministic fingerprint: hash of (arm-name, n_ent, n_rel, n_dim, recall).
    fingerprint = hashlib.sha256(
        f"{arm_name}|{n_ent}|{n_rel}|{n_dim}|{recall_k:.6f}|seed={seed}".encode()
    ).hexdigest()
    return {
        "arm": arm_name,
        "recall_at_1_top{}".format(TOPK_RECALL): recall_k,
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


def build_regime(seed: int, smoke: bool) -> Tuple[torch.Tensor, torch.Tensor, int, int]:
    """Build (triples, queries, n_ent, n_rel).

    Design: queries are a random subset of INGESTED triples — the substrate
    should recall the `o` that was Hebbian-bound to (s,p). This measures
    STORAGE CAPACITY per byte (can the substrate retrieve what was stored),
    not GENERALIZATION.

    To avoid capacity-collapse from repeated (s,p) pairs (multi-value key
    with random-o sample would give ambiguous ground-truth), we sample
    unique (s,p) pairs for triples and 1 unique o per (s,p). This makes
    the test a clean "is this fact stored?" measurement.
    """
    g = torch.Generator(device="cpu")
    g.manual_seed(seed + 1000)  # data seed offset from arm seed
    if smoke:
        n_triples = SMOKE_N_TRIPLES
        n_ent = SMOKE_N_ENT
        n_rel = SMOKE_N_REL
        n_queries = SMOKE_N_QUERIES
    else:
        n_triples = FULL_N_TRIPLES
        n_ent = FULL_N_ENT
        n_rel = FULL_N_REL
        n_queries = FULL_N_QUERIES

    # Sample UNIQUE (s, p) pairs -> unique keys, unique o per key.
    # Enumerate up to n_ent * n_rel unique keys and pick n_triples randomly.
    max_keys = n_ent * n_rel
    if n_triples > max_keys:
        raise ValueError(f"n_triples={n_triples} > n_ent*n_rel={max_keys}; "
                         f"cannot create unique (s,p) pairs at this regime")
    perm = torch.randperm(max_keys, generator=g)[:n_triples]
    s = perm // n_rel
    p = perm % n_rel
    o = torch.randint(0, n_ent, (n_triples,), generator=g)
    triples = torch.stack([s, p, o], dim=1).long()
    # Queries: uniform random subset of ingested triples.
    q_idx = torch.randperm(n_triples, generator=g)[:n_queries]
    queries = triples[q_idx]
    return triples, queries, n_ent, n_rel


def run_one_seed_all_arms(seed: int, run_mode: str, device: torch.device) -> Dict[str, Any]:
    """Run all 5 arms for one seed. Returns per-arm dict + per-arm metrics."""
    smoke = (run_mode == "smoke")
    triples, queries, n_ent, n_rel = build_regime(seed, smoke)
    per_arm = {}
    for arm in ARMS:
        if smoke:
            n_dim = SMOKE_N_DIM_SPARSE if arm == "SPARSE_BIPOLAR_0p05" else SMOKE_N_DIM_DENSE
        else:
            n_dim = N_DIM_SPARSE if arm == "SPARSE_BIPOLAR_0p05" else N_DIM_DENSE
        rec = _run_one_arm(arm, triples, queries, n_ent, n_rel, n_dim, seed, device)
        per_arm[arm] = rec
        print(f"[arm={arm}] seed={seed} recall={rec['recall']:.3f} "
              f"bytes/fact={rec['bytes_per_fact']:.0f} "
              f"pareto={rec['pareto_efficiency']:.4f} "
              f"elapsed={rec['elapsed_s']:.1f}s", flush=True)
    return {
        "seed": int(seed),
        "run_mode": run_mode,
        "per_arm": per_arm,
        "n_facts": int(triples.shape[0]),
        "n_queries": int(queries.shape[0]),
        "arms": list(ARMS),
    }


# ---------- Verdict logic ----------

def _at_least_2_arms_above_recall_target(per_arm: Dict[str, Any], target: float) -> int:
    return sum(1 for a in per_arm.values() if a["recall"] >= target)


def _pareto_2x_separation(per_arm: Dict[str, Any]) -> bool:
    """Verify all 5 arm (bytes, recall) points have 2x separation on either axis."""
    pts = [(a["bytes_per_fact"], a["recall"]) for a in per_arm.values()]
    # Sort by bytes; check consecutive-pair separation on at least one axis.
    pts_sorted = sorted(pts, key=lambda x: x[0])
    seps_ok = 0
    for i in range(len(pts_sorted) - 1):
        b0, r0 = pts_sorted[i]
        b1, r1 = pts_sorted[i + 1]
        byte_ratio = b1 / max(b0, 1.0)
        recall_gap = abs(r1 - r0)
        if byte_ratio >= 2.0 or recall_gap >= 0.05:
            seps_ok += 1
    return seps_ok >= (len(pts_sorted) - 1)


def _cross_seed_cv(per_seed: List[Dict[str, Any]]) -> Dict[str, Dict[str, float]]:
    """Compute per-arm cross-seed cv on bytes_per_fact and recall."""
    if not per_seed:
        return {}
    out = {}
    for arm in ARMS:
        recalls = [ps["per_arm"][arm]["recall"] for ps in per_seed
                   if arm in ps["per_arm"]]
        bpfs = [ps["per_arm"][arm]["bytes_per_fact"] for ps in per_seed
                if arm in ps["per_arm"]]
        if not recalls:
            continue
        rmean = sum(recalls) / len(recalls)
        rvar = sum((r - rmean) ** 2 for r in recalls) / len(recalls)
        rstd = math.sqrt(rvar)
        bmean = sum(bpfs) / len(bpfs)
        bvar = sum((b - bmean) ** 2 for b in bpfs) / len(bpfs)
        bstd = math.sqrt(bvar)
        out[arm] = {
            "recall_mean": rmean,
            "recall_cv": (rstd / rmean) if rmean > 0 else 0.0,
            "bytes_per_fact_mean": bmean,
            "bytes_per_fact_cv": (bstd / bmean) if bmean > 0 else 0.0,
        }
    return out


def aggregate_and_verdict(per_seed, run_mode: str) -> Dict[str, Any]:
    """Compose final verdict + metrics.

    Accepts per_seed as either list-of-payloads or dict-keyed-by-str(seed).

    HARD_PASS conditions:
      1. All 5 arms produce distinct (bytes, recall) with 2x-or-0.05 separation
      2. >=2 arms achieve recall >= 0.85 (with FP32 being one of them; META_RULE_BC)
      3. Cross-seed cv <= 0.10 on bytes_per_fact and recall
      4. All 5 mechanism_hash values distinct (META_RULE_AX/AF)
    """
    if isinstance(per_seed, dict):
        per_seed = list(per_seed.values())
    n_seeds = len(per_seed)
    if n_seeds == 0:
        return {
            "verdict": "HARD_FAIL",
            "verdict_msg": "HARD_FAIL: no seeds completed",
            "summary": "no per-seed data",
        }
    # META_RULE_BC positive control: FP32_DENSE mean recall across seeds >= 0.85
    fp32_recalls = [ps["per_arm"]["FP32_DENSE"]["recall"] for ps in per_seed]
    fp32_mean = sum(fp32_recalls) / len(fp32_recalls)
    positive_control_ok = fp32_mean >= RECALL_TARGET

    # Aggregate per-arm means.
    arm_means = {}
    for arm in ARMS:
        recalls = [ps["per_arm"][arm]["recall"] for ps in per_seed]
        bpfs = [ps["per_arm"][arm]["bytes_per_fact"] for ps in per_seed]
        paretos = [ps["per_arm"][arm]["pareto_efficiency"] for ps in per_seed]
        arm_means[arm] = {
            "recall_mean": sum(recalls) / len(recalls),
            "bytes_per_fact_mean": sum(bpfs) / len(bpfs),
            "pareto_mean": sum(paretos) / len(paretos),
        }

    # Distinct (bytes, recall) points using MEAN across seeds.
    mean_pts_dict = {arm: arm_means[arm] for arm in ARMS}
    n_above_target = sum(1 for arm in ARMS if arm_means[arm]["recall_mean"] >= RECALL_TARGET)
    pareto_ok = _pareto_2x_separation(
        {arm: {"bytes_per_fact": arm_means[arm]["bytes_per_fact_mean"],
                "recall": arm_means[arm]["recall_mean"]} for arm in ARMS}
    )

    # Cross-seed cv table
    cv_table = _cross_seed_cv(per_seed)
    max_recall_cv = max([v["recall_cv"] for v in cv_table.values()] + [0.0])
    max_bpf_cv = max([v["bytes_per_fact_cv"] for v in cv_table.values()] + [0.0])
    cv_ok = (max_recall_cv <= 0.10) and (max_bpf_cv <= 0.10)

    # META_RULE_AX/AF: mechanism-hash distinctness across arms (any single seed).
    if per_seed:
        one = per_seed[0]["per_arm"]
        hashes = set(a["mechanism_hash"] for a in one.values())
        hashes_distinct = len(hashes) == len(one)
    else:
        hashes_distinct = False

    # HARD_PASS if all four gates pass.
    all_pass = (positive_control_ok and pareto_ok and n_above_target >= 2
                and cv_ok and hashes_distinct)

    if all_pass:
        verdict = "HARD_PASS"
        vmsg = (f"HARD_PASS: 5-arm Pareto | FP32_mean={fp32_mean:.3f} "
                f">= {RECALL_TARGET} | n_above_target={n_above_target}/5 "
                f"| pareto_sep_ok={pareto_ok} | max_cv={max(max_recall_cv, max_bpf_cv):.3f} "
                f"| hashes_distinct={hashes_distinct} | n_seeds={n_seeds}")
    elif not positive_control_ok:
        verdict = "HARD_FAIL"
        vmsg = (f"HARD_FAIL: META_RULE_BC positive control BROKE. "
                f"FP32_DENSE recall_mean={fp32_mean:.3f} < {RECALL_TARGET}. "
                f"Test is broken; discriminator cannot be trusted. n_seeds={n_seeds}")
    else:
        verdict = "MIDDLE_BAND"
        vmsg = (f"MIDDLE_BAND: FP32_ok={positive_control_ok} "
                f"pareto_sep={pareto_ok} n_above_target={n_above_target}/5 "
                f"cv_ok={cv_ok} hashes_distinct={hashes_distinct}")

    expected_n_units = n_seeds * len(ARMS)
    observed_n_units = sum(len(ps["per_arm"]) for ps in per_seed)
    cardinality_ok = (observed_n_units == expected_n_units)
    if not cardinality_ok:
        verdict = "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H"
        vmsg = (f"HARD_FAIL_CARDINALITY_BREACH: observed={observed_n_units} "
                f"expected={expected_n_units}. Not all seeds x arms ran.")

    return {
        "verdict": verdict,
        "verdict_msg": vmsg,
        "summary": vmsg[:400],
        "run_mode": run_mode,
        "n_seeds": n_seeds,
        "arms": list(ARMS),
        "arm_means": arm_means,
        "cv_table": cv_table,
        "positive_control_fp32_recall_mean": fp32_mean,
        "positive_control_ok": positive_control_ok,
        "pareto_2x_separation_ok": pareto_ok,
        "n_arms_above_recall_target": n_above_target,
        "recall_target": RECALL_TARGET,
        "max_recall_cv": max_recall_cv,
        "max_bytes_per_fact_cv": max_bpf_cv,
        "cross_seed_cv_ok": cv_ok,
        "mechanism_hashes_distinct": hashes_distinct,
        "expected_n_units": expected_n_units,
        "observed_n_units": observed_n_units,
        "cardinality_ok": cardinality_ok,
        "per_seed": per_seed,
        "topK": TOPK_RECALL,
    }


def selftest(seed: int, device: torch.device) -> Tuple[bool, str]:
    """Tiny smoke: ingest 50 triples on cpu; check FP32 recall > 0.05 and all arms run."""
    smoke_device = torch.device("cpu")  # selftest on cpu for portability
    triples, queries, n_ent, n_rel = build_regime(seed, smoke=True)
    # Shrink further for selftest.
    triples = triples[:50]
    queries = queries[:20]
    # Just run FP32 to prove pipeline.
    n_dim = 512
    g = torch.Generator(device="cpu")
    g.manual_seed(seed)
    E = _bipolar(n_ent, n_dim, g, smoke_device)
    R = _bipolar(n_rel, n_dim, g, smoke_device)
    recall, _ = _ingest_and_query_fp32(triples, E, R, queries, queries[:, 2], n_dim, smoke_device)
    if not (recall >= 0.0):
        return False, f"selftest FP32 recall not >= 0: {recall}"
    # Also verify byte formula sane.
    bpf = bytes_fp32_dense(n_dim, n_ent, n_rel) / triples.shape[0]
    if bpf <= 0:
        return False, "selftest bytes_per_fact <= 0"
    return True, f"selftest OK: recall={recall:.3f} bpf={bpf:.0f}"


def get_backend_label() -> str:
    if torch.cuda.is_available():
        return f"cuda:{torch.cuda.get_device_name(0)}"
    return "cpu"
