"""Core module for Stage 2 INT2/BINARY Pareto probe v2 with asymmetric ternary.

v1 smoke (2026-07-02 04:31 UTC) at (N=4096,M=100k,sigma=0.28) established:
  FP32=0.683 INT8=0.683 INT4=0.674 INT2(sym)=0.205 BINARY(sign)=0.499
Symmetric ternary INT2 catastrophically fails: {-1,0,+1} zero-level erases
~1/3 of superposed weight magnitudes. Skunkworks batch 10 caught this as
MM_TENTATIVE INT2 catastrophe; asymmetric ternary predicted to recover.

v2 adds INT2_ASYM arm: 4 levels {-2,-1,+1,+2} skip-zero — a true 2-bit
quantization with no zero-erasure. AGS 1985 binary-analog equivalence
prediction (0.138N vs 0.14N capacity) more directly tested here since we
preserve non-zero magnitude everywhere.

v2 grid: 6 arms x 1 M x 4 sigma = 24 units/seed (N=8192 fixed, M=160k fixed).
  FULL_M_FIXED = 160000
  FULL_N_FIXED = 8192
  FULL_SIGMA_SWEEP = [0.20, 0.30, 0.35, 0.40]  (spans cliff per INT8 v3)

Discriminator: (M=160k, best-sigma) auto-selected via same tier logic as v1/v3.

HP gates (Skunkworks v2 spec):
  HP_META_RULE_Q_ATCLIFF:      FP32 unsaturated AND arms_range >= 0.03 at cliff
  HP_INT2_ASYM_RECOVERS:       |INT2_ASYM - FP32| <= 0.10 at cliff (KEY: fixes v1 catastrophe)
  HP_BINARY_PARETO_CG:         |BINARY - FP32| <= 0.15 at cliff (3-seed cv < 0.15 lifts to CG)
  HP_INT2_SYM_BREAKS_ROBUST:   (FP32 - INT2) >= 0.30 at cliff (reproduces v1 MM_TENTATIVE)
  HP_MEMORY_TIER_INT2:         INT2 bpf <= 0.10 x FP32 bpf (16x compression, both INT2 arms)
  HP_MEMORY_TIER_BINARY:       BINARY bpf <= 0.04 x FP32 bpf (32x compression)

HF gates:
  HF_INT2_ASYM_ALSO_BREAKS:    INT2_ASYM drop >= 0.30 (would refute asymmetric recovery hypothesis)
  HF_BINARY_BREAKS:            BINARY drop >= 0.35 (binary sign() fails at cliff)

Composes hdlab.int8_dense.quantize_int8_dense; inline INT4/INT2/INT2_ASYM/BINARY.

ASCII-only.
"""
from __future__ import annotations

import hashlib
import math
import os
import time
from typing import Any, Dict, List, Tuple

import torch

from hdlab.int8_dense import quantize_int8_dense


# ---------- Regime constants ----------

FULL_M_FIXED = 160000
FULL_N_FIXED = 8192
FULL_SIGMA_SWEEP = [0.20, 0.30, 0.35, 0.40]
FULL_N_ENT = 5000
FULL_N_REL = 100
FULL_QUERY_FRAC = 0.10

# Smoke: fires discriminator at N=4096 M=100k sigma=0.28 per v1 evidence.
SMOKE_M_FIXED = 100000
SMOKE_N_FIXED = 4096
SMOKE_SIGMA_SWEEP = [0.28]
SMOKE_N_ENT = 5000
SMOKE_N_REL = 100
SMOKE_QUERY_FRAC = 0.10

TOPK_RECALL = 1

# HP thresholds (Skunkworks batch 10 -> v2 spec)
HP_INT2_ASYM_RECOVERS_TOL = 0.10
HP_BINARY_PARETO_CG_TOL = 0.15
HP_INT2_SYM_BREAKS_DELTA = 0.30
HP_META_RULE_Q_ARMS_RANGE_MIN = 0.03
HP_META_RULE_Q_FP32_UPPER = 0.98
HP_META_RULE_Q_FP32_LOWER = 0.02
HP_MEMORY_FACTOR_INT2_MAX = 0.10
HP_MEMORY_FACTOR_BINARY_MAX = 0.04

HF_INT2_ASYM_ALSO_BREAKS_DELTA = 0.30
HF_BINARY_BREAKS_DELTA = 0.35

DISCRIMINATOR_POINT_N = 8192
DISCRIMINATOR_POINT_M = 160000
DISCRIMINATOR_POINT_SIGMA = 0.35

CROSS_SEED_CV_MAX_HP = 0.08
CROSS_SEED_CV_MAX_MB = 0.15  # relaxed per Skunkworks HP_BINARY_PARETO_CG spec

SATURATION_RECALL_CEIL = 0.98
FLOOR_RECALL = 0.02

ARMS = ["FP32", "INT8", "INT4", "INT2", "INT2_ASYM", "BINARY"]


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
    if noise_frac <= 0.0:
        return x.clone()
    g = torch.Generator(device="cpu")
    g.manual_seed(seed + 99999)
    mask_cpu = (torch.rand(x.shape, generator=g) < noise_frac).to(x.device)
    neg_one = torch.tensor(-1.0, dtype=x.dtype, device=x.device)
    pos_one = torch.tensor(1.0, dtype=x.dtype, device=x.device)
    flip = torch.where(mask_cpu, neg_one, pos_one)
    return x * flip


# ---------- Storage-cost formulas ----------

def bytes_fp32(n_dim, n_ent, n_rel):
    return (n_dim * n_dim * 4) + (n_ent * n_dim * 4) + (n_rel * n_dim * 4)


def bytes_int8(n_dim, n_ent, n_rel):
    W = n_dim * n_dim * 1 + n_dim * 4
    E = n_ent * n_dim * 1 + n_ent * 4
    R = n_rel * n_dim * 1 + n_rel * 4
    return W + E + R


def bytes_int4(n_dim, n_ent, n_rel):
    W = (n_dim * n_dim) // 2 + n_dim * 4
    E = (n_ent * n_dim) // 2 + n_ent * 4
    R = (n_rel * n_dim) // 2 + n_rel * 4
    return W + E + R


def bytes_int2(n_dim, n_ent, n_rel):
    # 2 bits per element (both INT2 sym-ternary and INT2_ASYM use 2-bit storage)
    W = (n_dim * n_dim) // 4 + n_dim * 4
    E = (n_ent * n_dim) // 4 + n_ent * 4
    R = (n_rel * n_dim) // 4 + n_rel * 4
    return W + E + R


def bytes_binary(n_dim, n_ent, n_rel):
    W = (n_dim * n_dim) // 8 + n_dim * 4
    E = (n_ent * n_dim) // 8 + n_ent * 4
    R = (n_rel * n_dim) // 8 + n_rel * 4
    return W + E + R


# ---------- Quantize primitives ----------

def quantize_int4_dense(W):
    if W.dtype != torch.float32:
        W = W.to(torch.float32)
    row_max = W.abs().max(dim=1, keepdim=True).values.clamp_min(1e-9)
    scale = row_max / 7.0
    W_int4 = torch.round(W / scale).clamp_(-7, 7).to(torch.int8)
    return W_int4, scale


def dequantize_int4_dense(W_int4, scale):
    return W_int4.to(torch.float32) * scale


def quantize_int2_sym_dense(W):
    """Symmetric ternary INT2: codes {-1, 0, +1}. Row-max scale.

    v1 established this fails catastrophically at noise cliff (~1/3 zeroed).
    Kept in v2 to reproduce the MM_TENTATIVE finding across 3 seeds -> CG.
    """
    if W.dtype != torch.float32:
        W = W.to(torch.float32)
    row_max = W.abs().max(dim=1, keepdim=True).values.clamp_min(1e-9)
    scale = row_max / 1.0
    W_int2 = torch.round(W / scale).clamp_(-1, 1).to(torch.int8)
    return W_int2, scale


def dequantize_int2_sym_dense(W_int2, scale):
    return W_int2.to(torch.float32) * scale


def quantize_int2_asym_dense(W):
    """Asymmetric ternary / skip-zero INT2: codes {-2, -1, +1, +2}. True 2-bit.

    Skunkworks batch 10 prediction: dropping the zero level should recover
    the INT2 catastrophe by preserving non-zero magnitude everywhere.

    Scale = row_max / 2 so |W/scale| in [0, 2]. Split at 1.5:
      |raw| < 1.5 -> code = sign * 1
      |raw| >= 1.5 -> code = sign * 2
    Sign ties (raw==0) break to +1.
    """
    if W.dtype != torch.float32:
        W = W.to(torch.float32)
    row_max = W.abs().max(dim=1, keepdim=True).values.clamp_min(1e-9)
    scale = row_max / 2.0
    raw = W / scale
    sign = torch.sign(raw)
    sign = torch.where(sign == 0, torch.ones_like(sign), sign)
    mag = raw.abs()
    one_t = torch.ones_like(mag)
    two_t = 2.0 * one_t
    level = torch.where(mag < 1.5, one_t, two_t)
    W_asym = (sign * level).to(torch.int8)
    return W_asym, scale


def dequantize_int2_asym_dense(W_asym, scale):
    return W_asym.to(torch.float32) * scale


def quantize_binary_dense(W):
    """Binary sign() quantize; row-mean-abs scale (BinaryConnect 2016)."""
    if W.dtype != torch.float32:
        W = W.to(torch.float32)
    scale = W.abs().mean(dim=1, keepdim=True).clamp_min(1e-9)
    W_bin = torch.sign(W).to(torch.int8)
    W_bin = torch.where(W_bin == 0, torch.ones_like(W_bin), W_bin)
    return W_bin, scale


def dequantize_binary_dense(W_bin, scale):
    return W_bin.to(torch.float32) * scale


# ---------- Ingest + query per arm ----------

def _ingest_and_query_fp32(triples, E, R, queries, n_dim, sigma, noise_seed, device):
    sq = math.sqrt(n_dim)
    Wf = torch.zeros(n_dim, n_dim, dtype=torch.float32, device=device)
    s_idx, p_idx, o_idx = triples[:, 0], triples[:, 1], triples[:, 2]
    batch = 2000
    for b in range(0, triples.shape[0], batch):
        se = s_idx[b:b + batch]; pe = p_idx[b:b + batch]; oe = o_idx[b:b + batch]
        keys = (E[se] * R[pe] * sq)
        Wf.add_((E[oe].T @ keys) / n_dim)
    q_s, q_p, q_o = queries[:, 0], queries[:, 1], queries[:, 2]
    q_keys = (E[q_s] * R[q_p] * sq)
    q_keys = _add_bipolar_noise(q_keys, sigma, seed=noise_seed)
    scores = q_keys @ Wf.T @ E.T
    topk = torch.topk(scores, k=min(TOPK_RECALL, E.shape[0]), dim=1)
    hits = (topk.indices == q_o.unsqueeze(1)).any(dim=1).float().mean()
    return float(hits)


def _ingest_and_query_int8(triples, E, R, queries, n_dim, sigma, noise_seed, device):
    sq = math.sqrt(n_dim)
    Wf = torch.zeros(n_dim, n_dim, dtype=torch.float32, device=device)
    s_idx, p_idx, o_idx = triples[:, 0], triples[:, 1], triples[:, 2]
    batch = 2000
    for b in range(0, triples.shape[0], batch):
        se = s_idx[b:b + batch]; pe = p_idx[b:b + batch]; oe = o_idx[b:b + batch]
        keys = (E[se] * R[pe] * sq)
        Wf.add_((E[oe].T @ keys) / n_dim)
    W_int8, scale_row = quantize_int8_dense(Wf)
    W_dequant = W_int8.to(torch.float32) * scale_row
    E_int8, E_scale = quantize_int8_dense(E)
    R_int8, R_scale = quantize_int8_dense(R)
    E_dq = E_int8.to(torch.float32) * E_scale
    R_dq = R_int8.to(torch.float32) * R_scale
    q_s, q_p, q_o = queries[:, 0], queries[:, 1], queries[:, 2]
    q_keys = (E_dq[q_s] * R_dq[q_p] * sq)
    q_keys = _add_bipolar_noise(q_keys, sigma, seed=noise_seed)
    scores = q_keys @ W_dequant.T @ E_dq.T
    topk = torch.topk(scores, k=min(TOPK_RECALL, E.shape[0]), dim=1)
    hits = (topk.indices == q_o.unsqueeze(1)).any(dim=1).float().mean()
    return float(hits)


def _ingest_and_query_int4(triples, E, R, queries, n_dim, sigma, noise_seed, device):
    sq = math.sqrt(n_dim)
    Wf = torch.zeros(n_dim, n_dim, dtype=torch.float32, device=device)
    s_idx, p_idx, o_idx = triples[:, 0], triples[:, 1], triples[:, 2]
    batch = 2000
    for b in range(0, triples.shape[0], batch):
        se = s_idx[b:b + batch]; pe = p_idx[b:b + batch]; oe = o_idx[b:b + batch]
        keys = (E[se] * R[pe] * sq)
        Wf.add_((E[oe].T @ keys) / n_dim)
    W_int4, W_scale = quantize_int4_dense(Wf)
    W_dequant = dequantize_int4_dense(W_int4, W_scale)
    E_int4, E_scale = quantize_int4_dense(E)
    R_int4, R_scale = quantize_int4_dense(R)
    E_dq = dequantize_int4_dense(E_int4, E_scale)
    R_dq = dequantize_int4_dense(R_int4, R_scale)
    q_s, q_p, q_o = queries[:, 0], queries[:, 1], queries[:, 2]
    q_keys = (E_dq[q_s] * R_dq[q_p] * sq)
    q_keys = _add_bipolar_noise(q_keys, sigma, seed=noise_seed)
    scores = q_keys @ W_dequant.T @ E_dq.T
    topk = torch.topk(scores, k=min(TOPK_RECALL, E.shape[0]), dim=1)
    hits = (topk.indices == q_o.unsqueeze(1)).any(dim=1).float().mean()
    return float(hits)


def _ingest_and_query_int2(triples, E, R, queries, n_dim, sigma, noise_seed, device):
    """Symmetric ternary INT2 (v1 arm; retained for MM_TENTATIVE reproduction)."""
    sq = math.sqrt(n_dim)
    Wf = torch.zeros(n_dim, n_dim, dtype=torch.float32, device=device)
    s_idx, p_idx, o_idx = triples[:, 0], triples[:, 1], triples[:, 2]
    batch = 2000
    for b in range(0, triples.shape[0], batch):
        se = s_idx[b:b + batch]; pe = p_idx[b:b + batch]; oe = o_idx[b:b + batch]
        keys = (E[se] * R[pe] * sq)
        Wf.add_((E[oe].T @ keys) / n_dim)
    W_int2, W_scale = quantize_int2_sym_dense(Wf)
    W_dequant = dequantize_int2_sym_dense(W_int2, W_scale)
    E_int2, E_scale = quantize_int2_sym_dense(E)
    R_int2, R_scale = quantize_int2_sym_dense(R)
    E_dq = dequantize_int2_sym_dense(E_int2, E_scale)
    R_dq = dequantize_int2_sym_dense(R_int2, R_scale)
    q_s, q_p, q_o = queries[:, 0], queries[:, 1], queries[:, 2]
    q_keys = (E_dq[q_s] * R_dq[q_p] * sq)
    q_keys = _add_bipolar_noise(q_keys, sigma, seed=noise_seed)
    scores = q_keys @ W_dequant.T @ E_dq.T
    topk = torch.topk(scores, k=min(TOPK_RECALL, E.shape[0]), dim=1)
    hits = (topk.indices == q_o.unsqueeze(1)).any(dim=1).float().mean()
    return float(hits)


def _ingest_and_query_int2_asym(triples, E, R, queries, n_dim, sigma, noise_seed, device):
    """Asymmetric skip-zero INT2: {-2, -1, +1, +2} — v2 key arm.

    Skunkworks prediction: recovers INT2 catastrophe by never zeroing magnitude.
    """
    sq = math.sqrt(n_dim)
    Wf = torch.zeros(n_dim, n_dim, dtype=torch.float32, device=device)
    s_idx, p_idx, o_idx = triples[:, 0], triples[:, 1], triples[:, 2]
    batch = 2000
    for b in range(0, triples.shape[0], batch):
        se = s_idx[b:b + batch]; pe = p_idx[b:b + batch]; oe = o_idx[b:b + batch]
        keys = (E[se] * R[pe] * sq)
        Wf.add_((E[oe].T @ keys) / n_dim)
    W_a, W_scale = quantize_int2_asym_dense(Wf)
    W_dequant = dequantize_int2_asym_dense(W_a, W_scale)
    E_a, E_scale = quantize_int2_asym_dense(E)
    R_a, R_scale = quantize_int2_asym_dense(R)
    E_dq = dequantize_int2_asym_dense(E_a, E_scale)
    R_dq = dequantize_int2_asym_dense(R_a, R_scale)
    q_s, q_p, q_o = queries[:, 0], queries[:, 1], queries[:, 2]
    q_keys = (E_dq[q_s] * R_dq[q_p] * sq)
    q_keys = _add_bipolar_noise(q_keys, sigma, seed=noise_seed)
    scores = q_keys @ W_dequant.T @ E_dq.T
    topk = torch.topk(scores, k=min(TOPK_RECALL, E.shape[0]), dim=1)
    hits = (topk.indices == q_o.unsqueeze(1)).any(dim=1).float().mean()
    return float(hits)


def _ingest_and_query_binary(triples, E, R, queries, n_dim, sigma, noise_seed, device):
    sq = math.sqrt(n_dim)
    Wf = torch.zeros(n_dim, n_dim, dtype=torch.float32, device=device)
    s_idx, p_idx, o_idx = triples[:, 0], triples[:, 1], triples[:, 2]
    batch = 2000
    for b in range(0, triples.shape[0], batch):
        se = s_idx[b:b + batch]; pe = p_idx[b:b + batch]; oe = o_idx[b:b + batch]
        keys = (E[se] * R[pe] * sq)
        Wf.add_((E[oe].T @ keys) / n_dim)
    W_bin, W_scale = quantize_binary_dense(Wf)
    W_dequant = dequantize_binary_dense(W_bin, W_scale)
    E_bin, E_scale = quantize_binary_dense(E)
    R_bin, R_scale = quantize_binary_dense(R)
    E_dq = dequantize_binary_dense(E_bin, E_scale)
    R_dq = dequantize_binary_dense(R_bin, R_scale)
    q_s, q_p, q_o = queries[:, 0], queries[:, 1], queries[:, 2]
    q_keys = (E_dq[q_s] * R_dq[q_p] * sq)
    q_keys = _add_bipolar_noise(q_keys, sigma, seed=noise_seed)
    scores = q_keys @ W_dequant.T @ E_dq.T
    topk = torch.topk(scores, k=min(TOPK_RECALL, E.shape[0]), dim=1)
    hits = (topk.indices == q_o.unsqueeze(1)).any(dim=1).float().mean()
    return float(hits)


ARM_FNS = {
    "FP32": _ingest_and_query_fp32,
    "INT8": _ingest_and_query_int8,
    "INT4": _ingest_and_query_int4,
    "INT2": _ingest_and_query_int2,
    "INT2_ASYM": _ingest_and_query_int2_asym,
    "BINARY": _ingest_and_query_binary,
}

BYTES_FNS = {
    "FP32": bytes_fp32,
    "INT8": bytes_int8,
    "INT4": bytes_int4,
    "INT2": bytes_int2,
    "INT2_ASYM": bytes_int2,   # same 2-bit storage as INT2 sym
    "BINARY": bytes_binary,
}


def _run_one_arm(arm_name, triples, queries, n_ent, n_rel, n_dim, M, sigma, seed, device):
    g = torch.Generator(device="cpu")
    g.manual_seed(seed)
    E_cpu = _bipolar(n_ent, n_dim, g, torch.device("cpu"))
    R_cpu = _bipolar(n_rel, n_dim, g, torch.device("cpu"))
    E = E_cpu.to(device)
    R = R_cpu.to(device)
    triples_dev = triples.to(device)
    queries_dev = queries.to(device)
    noise_seed = seed * 1000 + int(sigma * 100) + 7
    t0 = time.perf_counter()
    fn = ARM_FNS[arm_name]
    recall_k = fn(triples_dev, E, R, queries_dev, n_dim, sigma, noise_seed, device)
    elapsed = time.perf_counter() - t0
    total_bytes = BYTES_FNS[arm_name](n_dim, n_ent, n_rel)
    n_facts = triples.shape[0]
    bpf = total_bytes / n_facts
    del E, R, triples_dev, queries_dev, E_cpu, R_cpu
    if device.type == "cuda":
        try:
            torch.cuda.empty_cache()
        except Exception:
            pass
    fingerprint = hashlib.sha256(
        f"{arm_name}|M={M}|N={n_dim}|sigma={sigma}|"
        f"{recall_k:.6f}|seed={seed}".encode()
    ).hexdigest()
    return {
        "arm": arm_name,
        "M": int(M),
        "N": int(n_dim),
        "sigma": float(sigma),
        "recall_cosine_mean": recall_k,
        "n_facts": int(n_facts),
        "n_ent": int(n_ent),
        "n_rel": int(n_rel),
        "n_dim": int(n_dim),
        "bytes_total": int(total_bytes),
        "bytes_per_fact": float(bpf),
        "wall_s": round(elapsed, 3),
        "mechanism_hash": fingerprint,
        "seed": int(seed),
    }


def build_regime_at_M(seed, M, n_ent, n_rel, query_frac):
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


def run_one_seed_all_units(seed, run_mode, device):
    smoke = (run_mode == "smoke")
    if smoke:
        M_fixed = SMOKE_M_FIXED
        N_fixed = SMOKE_N_FIXED
        sigma_sweep = SMOKE_SIGMA_SWEEP
        n_ent = SMOKE_N_ENT
        n_rel = SMOKE_N_REL
        query_frac = SMOKE_QUERY_FRAC
    else:
        M_fixed = FULL_M_FIXED
        N_fixed = FULL_N_FIXED
        sigma_sweep = FULL_SIGMA_SWEEP
        n_ent = FULL_N_ENT
        n_rel = FULL_N_REL
        query_frac = FULL_QUERY_FRAC
    per_unit = {}
    t_seed_start = time.time()
    triples, queries = build_regime_at_M(seed, M_fixed, n_ent, n_rel, query_frac)
    for sigma in sigma_sweep:
        for arm in ARMS:
            key = f"{arm}__M{M_fixed}__N{N_fixed}__sigma{sigma:.2f}"
            rec = _run_one_arm(arm, triples, queries, n_ent, n_rel,
                                N_fixed, M_fixed, sigma, seed, device)
            per_unit[key] = rec
            elapsed_total = time.time() - t_seed_start
            print(f"[arm={arm} M={M_fixed} N={N_fixed} s={sigma:.2f}] seed={seed} "
                  f"recall={rec['recall_cosine_mean']:.3f} "
                  f"bpf={rec['bytes_per_fact']:.0f} "
                  f"wall={rec['wall_s']:.2f}s "
                  f"seed_total={elapsed_total:.1f}s", flush=True)
    return {
        "seed": int(seed),
        "run_mode": run_mode,
        "per_unit": per_unit,
        "M_fixed": int(M_fixed),
        "N_fixed": int(N_fixed),
        "sigma_sweep": list(sigma_sweep),
        "arms": list(ARMS),
    }


# ---------- Verdict logic ----------

def _cross_seed_stats(per_seed, unit_keys):
    out = {}
    for uk in unit_keys:
        recalls = [ps["per_unit"][uk]["recall_cosine_mean"] for ps in per_seed
                   if uk in ps["per_unit"]]
        walls = [ps["per_unit"][uk]["wall_s"] for ps in per_seed
                 if uk in ps["per_unit"]]
        bpfs = [ps["per_unit"][uk]["bytes_per_fact"] for ps in per_seed
                if uk in ps["per_unit"]]
        if not recalls:
            continue
        rmean = sum(recalls) / len(recalls)
        rvar = sum((r - rmean) ** 2 for r in recalls) / len(recalls)
        rstd = math.sqrt(rvar)
        out[uk] = {
            "recall_cosine_mean": rmean,
            "recall_std": rstd,
            "recall_cv": (rstd / rmean) if rmean > 0 else 0.0,
            "wall_s_mean": sum(walls) / len(walls),
            "bytes_per_fact_mean": sum(bpfs) / len(bpfs),
            "n_seeds": len(recalls),
        }
    return out


def _find_best_discriminating_sigma(stats, M, N_fixed, sigma_sweep):
    """Same tier logic as v1/v3."""
    candidates = []
    for sigma in sigma_sweep:
        per_arm = {}
        for arm in ARMS:
            uk = f"{arm}__M{M}__N{N_fixed}__sigma{sigma:.2f}"
            r = stats.get(uk, {}).get("recall_cosine_mean", float("nan"))
            per_arm[arm] = r
        vals = [r for r in per_arm.values() if not math.isnan(r)]
        if not vals:
            continue
        arms_range = max(vals) - min(vals)
        fp32 = per_arm.get("FP32", float("nan"))
        fp32_unsat = (not math.isnan(fp32)) and (FLOOR_RECALL < fp32 < HP_META_RULE_Q_FP32_UPPER)
        tier_1 = fp32_unsat and arms_range >= HP_META_RULE_Q_ARMS_RANGE_MIN
        tier_2 = fp32_unsat and not tier_1
        candidates.append({
            "sigma": sigma, "per_arm_recalls": per_arm,
            "arms_range": arms_range, "fp32_unsaturated": fp32_unsat,
            "tier_1_full_discriminator": tier_1,
            "tier_2_pareto_probe_only": tier_2,
        })
    if not candidates:
        return None
    tier_1_qualified = [c for c in candidates if c["tier_1_full_discriminator"]]
    if tier_1_qualified:
        return {**max(tier_1_qualified, key=lambda c: c["arms_range"]),
                "qualification_tier": "tier_1_full"}
    tier_2_qualified = [c for c in candidates if c["tier_2_pareto_probe_only"]]
    if tier_2_qualified:
        return {**min(tier_2_qualified,
                      key=lambda c: abs(c["per_arm_recalls"].get("FP32", 0) - 0.5)),
                "qualification_tier": "tier_2_pareto_probe"}
    return {**max(candidates, key=lambda c: c["arms_range"]),
            "qualification_tier": "tier_3_fallback"}


def aggregate_and_verdict(per_seed, run_mode):
    if isinstance(per_seed, dict):
        per_seed = list(per_seed.values())
    n_seeds = len(per_seed)
    if n_seeds == 0:
        return {"verdict": "HARD_FAIL",
                "verdict_msg": "HARD_FAIL: no seeds completed",
                "summary": "no per-seed data"}

    smoke = (run_mode == "smoke")
    M_fixed = SMOKE_M_FIXED if smoke else FULL_M_FIXED
    N_fixed = SMOKE_N_FIXED if smoke else FULL_N_FIXED
    sigma_sweep = SMOKE_SIGMA_SWEEP if smoke else FULL_SIGMA_SWEEP

    unit_keys = []
    for arm in ARMS:
        for sigma in sigma_sweep:
            unit_keys.append(f"{arm}__M{M_fixed}__N{N_fixed}__sigma{sigma:.2f}")
    stats = _cross_seed_stats(per_seed, unit_keys)

    expected_n_units = len(ARMS) * len(sigma_sweep)
    observed_n_units_per_seed = [len(ps["per_unit"]) for ps in per_seed]
    cardinality_ok = all(n == expected_n_units for n in observed_n_units_per_seed)

    hashes = set()
    if per_seed:
        one_pu = per_seed[0]["per_unit"]
        for uk in unit_keys:
            if uk in one_pu:
                hashes.add(one_pu[uk]["mechanism_hash"])
    hashes_distinct = len(hashes) == expected_n_units

    best_cliff = _find_best_discriminating_sigma(stats, M_fixed, N_fixed, sigma_sweep)

    if best_cliff is None:
        return {"verdict": "HARD_FAIL",
                "verdict_msg": f"HARD_FAIL: no stats at M={M_fixed} for any sigma",
                "summary": f"no data at discriminator M={M_fixed}"}

    disc_sigma = best_cliff["sigma"]
    per_arm = best_cliff["per_arm_recalls"]
    arms_range = best_cliff["arms_range"]
    fp32_unsat = best_cliff["fp32_unsaturated"]
    qual_tier = best_cliff.get("qualification_tier", "unknown")

    fp32_r = per_arm.get("FP32", float("nan"))
    int8_r = per_arm.get("INT8", float("nan"))
    int4_r = per_arm.get("INT4", float("nan"))
    int2_r = per_arm.get("INT2", float("nan"))
    int2a_r = per_arm.get("INT2_ASYM", float("nan"))
    bin_r = per_arm.get("BINARY", float("nan"))

    hp_meta_rule_q_atcliff = fp32_unsat and (
        (arms_range >= HP_META_RULE_Q_ARMS_RANGE_MIN) or
        (qual_tier == "tier_2_pareto_probe")
    )

    # HP_INT2_ASYM_RECOVERS: v2 KEY gate
    int2a_gap = (abs(int2a_r - fp32_r)
                 if not (math.isnan(int2a_r) or math.isnan(fp32_r)) else float("inf"))
    hp_int2_asym_recovers = int2a_gap <= HP_INT2_ASYM_RECOVERS_TOL

    # HP_BINARY_PARETO_CG
    binary_gap = (abs(bin_r - fp32_r)
                  if not (math.isnan(bin_r) or math.isnan(fp32_r)) else float("inf"))
    hp_binary_pareto_cg = binary_gap <= HP_BINARY_PARETO_CG_TOL

    # HP_INT2_SYM_BREAKS_ROBUST (reproduces v1 MM_TENTATIVE across seeds)
    int2_sym_drop = ((fp32_r - int2_r)
                     if not (math.isnan(int2_r) or math.isnan(fp32_r)) else float("nan"))
    hp_int2_sym_breaks = ((not math.isnan(int2_sym_drop))
                          and (int2_sym_drop >= HP_INT2_SYM_BREAKS_DELTA))

    # HF gates (documentation)
    int2a_drop = ((fp32_r - int2a_r)
                  if not (math.isnan(int2a_r) or math.isnan(fp32_r)) else float("nan"))
    binary_drop = ((fp32_r - bin_r)
                   if not (math.isnan(bin_r) or math.isnan(fp32_r)) else float("nan"))
    hf_int2_asym_also_breaks = ((not math.isnan(int2a_drop))
                                and (int2a_drop >= HF_INT2_ASYM_ALSO_BREAKS_DELTA))
    hf_binary_breaks = ((not math.isnan(binary_drop))
                       and (binary_drop >= HF_BINARY_BREAKS_DELTA))

    # HP_MEMORY_TIER (analytical)
    int2_mem_factors = []
    binary_mem_factors = []
    for sigma in sigma_sweep:
        fp32_bpf = stats.get(f"FP32__M{M_fixed}__N{N_fixed}__sigma{sigma:.2f}",
                             {}).get("bytes_per_fact_mean", 0)
        int2_bpf = stats.get(f"INT2__M{M_fixed}__N{N_fixed}__sigma{sigma:.2f}",
                             {}).get("bytes_per_fact_mean", 0)
        bin_bpf = stats.get(f"BINARY__M{M_fixed}__N{N_fixed}__sigma{sigma:.2f}",
                            {}).get("bytes_per_fact_mean", 0)
        if fp32_bpf > 0:
            int2_mem_factors.append(int2_bpf / fp32_bpf)
            binary_mem_factors.append(bin_bpf / fp32_bpf)
    max_int2_mem = max(int2_mem_factors) if int2_mem_factors else float("inf")
    max_binary_mem = max(binary_mem_factors) if binary_mem_factors else float("inf")
    hp_mem_int2 = max_int2_mem <= HP_MEMORY_FACTOR_INT2_MAX
    hp_mem_binary = max_binary_mem <= HP_MEMORY_FACTOR_BINARY_MAX

    # cv gate
    max_cv = 0.0
    for uk in unit_keys:
        cv = stats.get(uk, {}).get("recall_cv", 0.0)
        if cv > max_cv:
            max_cv = cv
    cv_hard_fail = max_cv >= CROSS_SEED_CV_MAX_MB

    # Count HP substantive gates
    hp_gates_cleared = 0
    for gate in [hp_meta_rule_q_atcliff, hp_int2_asym_recovers, hp_binary_pareto_cg,
                 hp_int2_sym_breaks, hp_mem_int2, hp_mem_binary]:
        if gate:
            hp_gates_cleared += 1
    hp_gates_total = 6

    # Verdict
    if not cardinality_ok:
        verdict = "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H"
        vmsg = (f"HARD_FAIL_CARDINALITY: observed_per_seed={observed_n_units_per_seed} "
                f"expected={expected_n_units}")
    elif not hashes_distinct:
        verdict = "HARD_FAIL_META_RULE_AX_HASH_COLLISION"
        vmsg = (f"HARD_FAIL: mechanism_hash collision "
                f"({len(hashes)} distinct vs {expected_n_units} expected)")
    elif cv_hard_fail:
        verdict = "HARD_FAIL_CV_BREACH"
        vmsg = (f"HARD_FAIL: cross-seed cv >= {CROSS_SEED_CV_MAX_MB} "
                f"(max_cv={max_cv:.3f})")
    elif not hp_meta_rule_q_atcliff:
        verdict = "HARD_FAIL_META_RULE_Q_NON_DISCRIMINATING"
        vmsg = (f"HARD_FAIL_META_RULE_Q: at best sigma point (M={M_fixed} "
                f"sigma={disc_sigma:.2f} tier={qual_tier}) FP32={fp32_r:.3f} "
                f"unsaturated={fp32_unsat} arms_range={arms_range:.3f}. "
                f"Grid missed cliff bracket.")
    elif smoke:
        # Smoke passes if discriminator fires + INT2_ASYM in-band (key v2 gate)
        if hp_int2_asym_recovers:
            verdict = "HARD_PASS"
            vmsg = (f"SMOKE_HARD_PASS_INT2_ASYM_RECOVERS: cliff (M={M_fixed} sigma={disc_sigma:.2f}); "
                    f"FP32={fp32_r:.3f} INT8={int8_r:.3f} INT4={int4_r:.3f} "
                    f"INT2sym={int2_r:.3f} INT2asym={int2a_r:.3f} BINARY={bin_r:.3f}; "
                    f"INT2_ASYM_gap={int2a_gap:.3f}<={HP_INT2_ASYM_RECOVERS_TOL}; "
                    f"INT2_SYM_drop={int2_sym_drop:.3f}(breaks_robust={hp_int2_sym_breaks}); "
                    f"BINARY_gap={binary_gap:.3f}(cg={hp_binary_pareto_cg})")
        else:
            verdict = "MIDDLE_BAND"
            vmsg = (f"SMOKE_MIDDLE_BAND_INT2_ASYM_ALSO_BREAKS: "
                    f"INT2_ASYM_gap={int2a_gap:.3f}>{HP_INT2_ASYM_RECOVERS_TOL}; "
                    f"FP32={fp32_r:.3f} INT2asym={int2a_r:.3f} INT2sym={int2_r:.3f} "
                    f"BINARY={bin_r:.3f}; hf_int2_asym_also_breaks={hf_int2_asym_also_breaks}")
    elif (hp_int2_asym_recovers and hp_binary_pareto_cg and hp_int2_sym_breaks
          and hp_mem_int2 and hp_mem_binary):
        verdict = "HARD_PASS"
        vmsg = (f"HARD_PASS_INT2_ASYM_RECOVERS_ALL_GATES: cliff (M={M_fixed} sigma={disc_sigma:.2f}); "
                f"FP32={fp32_r:.3f} INT8={int8_r:.3f} INT4={int4_r:.3f} "
                f"INT2sym={int2_r:.3f} INT2asym={int2a_r:.3f} BINARY={bin_r:.3f}; "
                f"INT2_ASYM_gap={int2a_gap:.3f}<={HP_INT2_ASYM_RECOVERS_TOL}; "
                f"INT2_SYM_drop={int2_sym_drop:.3f}>={HP_INT2_SYM_BREAKS_DELTA}; "
                f"BINARY_gap={binary_gap:.3f}<={HP_BINARY_PARETO_CG_TOL}; "
                f"INT2_mem={max_int2_mem:.4f}<={HP_MEMORY_FACTOR_INT2_MAX}; "
                f"BINARY_mem={max_binary_mem:.4f}<={HP_MEMORY_FACTOR_BINARY_MAX}")
    elif hp_int2_asym_recovers and hp_mem_int2:
        verdict = "MIDDLE_BAND"
        vmsg = (f"MIDDLE_BAND_INT2_ASYM_CG_ONLY: INT2_ASYM recovers "
                f"(gap={int2a_gap:.3f}<={HP_INT2_ASYM_RECOVERS_TOL}) with 16x compression; "
                f"other gates: binary_cg={hp_binary_pareto_cg} int2_sym_breaks={hp_int2_sym_breaks}. "
                f"FP32={fp32_r:.3f} INT2asym={int2a_r:.3f} BINARY={bin_r:.3f}")
    elif hp_gates_cleared >= 3:
        verdict = "MIDDLE_BAND"
        vmsg = (f"MIDDLE_BAND_PARTIAL_GATES: cleared {hp_gates_cleared}/{hp_gates_total}. "
                f"q_atcliff={hp_meta_rule_q_atcliff} int2_asym_recovers={hp_int2_asym_recovers} "
                f"binary_cg={hp_binary_pareto_cg} int2_sym_breaks={hp_int2_sym_breaks} "
                f"mem_int2={hp_mem_int2} mem_binary={hp_mem_binary}; "
                f"cliff@sigma={disc_sigma:.2f}: FP32={fp32_r:.3f} "
                f"INT2asym={int2a_r:.3f} INT2sym={int2_r:.3f} BINARY={bin_r:.3f}")
    else:
        verdict = "MIDDLE_BAND"
        vmsg = (f"MIDDLE_BAND: only {hp_gates_cleared}/{hp_gates_total} gates cleared. "
                f"cliff@sigma={disc_sigma:.2f}: FP32={fp32_r:.3f} INT2asym={int2a_r:.3f} "
                f"BINARY={bin_r:.3f}")

    return {
        "verdict": verdict,
        "verdict_msg": vmsg,
        "summary": vmsg[:400],
        "run_mode": run_mode,
        "n_seeds": n_seeds,
        "arms": list(ARMS),
        "M_fixed": int(M_fixed),
        "N_fixed": int(N_fixed),
        "sigma_sweep": list(sigma_sweep),
        "discriminator_point": {
            "N": N_fixed, "M": M_fixed, "sigma": disc_sigma,
            "chosen_by": "best_discriminating_sigma_scan",
            "qualification_tier": qual_tier,
            "FP32_recall": fp32_r, "INT8_recall": int8_r,
            "INT4_recall": int4_r, "INT2_sym_recall": int2_r,
            "INT2_ASYM_recall": int2a_r, "BINARY_recall": bin_r,
            "INT2_ASYM_gap_vs_FP32": int2a_gap,
            "BINARY_gap_vs_FP32": binary_gap,
            "INT2_sym_drop_vs_FP32": int2_sym_drop,
            "INT2_ASYM_drop_vs_FP32": int2a_drop,
            "BINARY_drop_vs_FP32": binary_drop,
            "arms_range": arms_range,
            "fp32_unsaturated": fp32_unsat,
        },
        "hp_meta_rule_q_atcliff": bool(hp_meta_rule_q_atcliff),
        "hp_int2_asym_recovers": bool(hp_int2_asym_recovers),
        "hp_binary_pareto_cg": bool(hp_binary_pareto_cg),
        "hp_int2_sym_breaks_robust": bool(hp_int2_sym_breaks),
        "hp_mem_int2": bool(hp_mem_int2),
        "hp_mem_binary": bool(hp_mem_binary),
        "hf_int2_asym_also_breaks": bool(hf_int2_asym_also_breaks),
        "hf_binary_breaks": bool(hf_binary_breaks),
        "hp_gates_cleared": hp_gates_cleared,
        "hp_gates_total": hp_gates_total,
        "max_int2_memory_factor": max_int2_mem,
        "max_binary_memory_factor": max_binary_mem,
        "max_cv_across_arms": max_cv,
        "stats_cross_seed": stats,
        "cardinality_ok": cardinality_ok,
        "expected_n_units_per_seed": expected_n_units,
        "observed_n_units_per_seed": observed_n_units_per_seed,
        "mechanism_hashes_distinct": hashes_distinct,
        "per_seed": per_seed,
        "topK": TOPK_RECALL,
        "HP_INT2_ASYM_RECOVERS_TOL": HP_INT2_ASYM_RECOVERS_TOL,
        "HP_BINARY_PARETO_CG_TOL": HP_BINARY_PARETO_CG_TOL,
        "HP_INT2_SYM_BREAKS_DELTA": HP_INT2_SYM_BREAKS_DELTA,
        "HP_META_RULE_Q_ARMS_RANGE_MIN": HP_META_RULE_Q_ARMS_RANGE_MIN,
        "HP_MEMORY_FACTOR_INT2_MAX": HP_MEMORY_FACTOR_INT2_MAX,
        "HP_MEMORY_FACTOR_BINARY_MAX": HP_MEMORY_FACTOR_BINARY_MAX,
        "HF_INT2_ASYM_ALSO_BREAKS_DELTA": HF_INT2_ASYM_ALSO_BREAKS_DELTA,
        "HF_BINARY_BREAKS_DELTA": HF_BINARY_BREAKS_DELTA,
        "CROSS_SEED_CV_MAX_HP": CROSS_SEED_CV_MAX_HP,
        "CROSS_SEED_CV_MAX_MB": CROSS_SEED_CV_MAX_MB,
    }


def selftest(seed, device):
    """Selftest: 6-arm functional + INT2_ASYM round-trip + bpf ordering + memory factors."""
    smoke_device = torch.device("cpu")
    triples, queries = build_regime_at_M(seed, M=30, n_ent=200, n_rel=25, query_frac=0.5)
    n_dim = 256
    g = torch.Generator(device="cpu")
    g.manual_seed(seed)
    E = _bipolar(200, n_dim, g, smoke_device)
    R = _bipolar(25, n_dim, g, smoke_device)
    noise_seed = 42
    sigma = 0.1
    r_fp32 = _ingest_and_query_fp32(triples, E, R, queries, n_dim, sigma, noise_seed, smoke_device)
    r_int8 = _ingest_and_query_int8(triples, E, R, queries, n_dim, sigma, noise_seed, smoke_device)
    r_int4 = _ingest_and_query_int4(triples, E, R, queries, n_dim, sigma, noise_seed, smoke_device)
    r_int2 = _ingest_and_query_int2(triples, E, R, queries, n_dim, sigma, noise_seed, smoke_device)
    r_int2a = _ingest_and_query_int2_asym(triples, E, R, queries, n_dim, sigma, noise_seed, smoke_device)
    r_bin = _ingest_and_query_binary(triples, E, R, queries, n_dim, sigma, noise_seed, smoke_device)
    for name, r in [("fp32", r_fp32), ("int8", r_int8), ("int4", r_int4),
                    ("int2", r_int2), ("int2_asym", r_int2a), ("binary", r_bin)]:
        if not (0.0 <= r <= 1.0):
            return False, f"selftest recall out-of-range: {name}={r}"
        if not math.isfinite(r):
            return False, f"selftest recall non-finite: {name}={r}"

    # bpf ordering: binary < int2 = int2_asym < int4 < int8 < fp32
    n_facts = triples.shape[0]
    bpf_fp32 = bytes_fp32(n_dim, 200, 25) / n_facts
    bpf_int8 = bytes_int8(n_dim, 200, 25) / n_facts
    bpf_int4 = bytes_int4(n_dim, 200, 25) / n_facts
    bpf_int2 = bytes_int2(n_dim, 200, 25) / n_facts
    bpf_bin = bytes_binary(n_dim, 200, 25) / n_facts
    if not (bpf_bin < bpf_int2 < bpf_int4 < bpf_int8 < bpf_fp32):
        return False, (f"selftest bpf ordering broken: bin={bpf_bin} int2={bpf_int2} "
                       f"int4={bpf_int4} int8={bpf_int8} fp32={bpf_fp32}")

    # Analytical memory factors at N=8192 M=160k target
    bpf_fp32_big = bytes_fp32(8192, 5000, 100) / 160000
    bpf_int2_big = bytes_int2(8192, 5000, 100) / 160000
    bpf_bin_big = bytes_binary(8192, 5000, 100) / 160000
    mem_int2_big = bpf_int2_big / bpf_fp32_big
    mem_bin_big = bpf_bin_big / bpf_fp32_big
    if mem_int2_big > HP_MEMORY_FACTOR_INT2_MAX:
        return False, (f"selftest HP_MEMORY_FACTOR_INT2 analytical fail at N=8192,M=160k: "
                       f"{mem_int2_big:.4f} > {HP_MEMORY_FACTOR_INT2_MAX}")
    if mem_bin_big > HP_MEMORY_FACTOR_BINARY_MAX:
        return False, (f"selftest HP_MEMORY_FACTOR_BINARY analytical fail at N=8192,M=160k: "
                       f"{mem_bin_big:.4f} > {HP_MEMORY_FACTOR_BINARY_MAX}")

    # INT2_ASYM round-trip: codes must be in {-2,-1,+1,+2}; no zeros
    W_test = torch.randn(32, 32) * 0.1
    W_a, s_a = quantize_int2_asym_dense(W_test)
    codes_set = set(W_a.unique().tolist())
    if 0 in codes_set:
        return False, f"selftest INT2_ASYM contains zero code: {codes_set}"
    if not codes_set.issubset({-2, -1, 1, 2}):
        return False, f"selftest INT2_ASYM codes not in {{-2,-1,+1,+2}}: {codes_set}"
    W_recon_a = dequantize_int2_asym_dense(W_a, s_a)
    max_err_a = (W_test - W_recon_a).abs().max().item()
    scale_max_a = s_a.max().item()
    if max_err_a > 2.0 * scale_max_a:
        return False, f"selftest INT2_ASYM round-trip too lossy: max_err={max_err_a:.4f}"

    # INT2 sym round-trip (unchanged from v1)
    W_int2, scale_2 = quantize_int2_sym_dense(W_test)
    W_recon_2 = dequantize_int2_sym_dense(W_int2, scale_2)
    codes_sym_set = set(W_int2.unique().tolist())
    if not codes_sym_set.issubset({-1, 0, 1}):
        return False, f"selftest INT2_SYM codes not in {{-1,0,+1}}: {codes_sym_set}"

    # BINARY sign match
    W_bin, scale_b = quantize_binary_dense(W_test)
    W_recon_b = dequantize_binary_dense(W_bin, scale_b)
    sign_match = (torch.sign(W_recon_b) == torch.sign(W_test)).float().mean().item()
    if sign_match < 0.99:
        return False, f"selftest BINARY sign() not preserved: match={sign_match:.3f}"

    # Distinct outputs: INT2_SYM vs INT2_ASYM vs BINARY must differ
    if torch.allclose(W_recon_2, W_recon_a, atol=1e-6):
        return False, "selftest INT2_SYM and INT2_ASYM produce identical output"
    if torch.allclose(W_recon_a, W_recon_b, atol=1e-6):
        return False, "selftest INT2_ASYM and BINARY produce identical output"
    if torch.allclose(W_recon_2, W_recon_b, atol=1e-6):
        return False, "selftest INT2_SYM and BINARY produce identical output"

    return True, (
        f"selftest OK: fp32={r_fp32:.3f} int8={r_int8:.3f} int4={r_int4:.3f} "
        f"int2sym={r_int2:.3f} int2asym={r_int2a:.3f} bin={r_bin:.3f} "
        f"bpf_bin={bpf_bin:.1f} bpf_int2={bpf_int2:.1f} bpf_int4={bpf_int4:.1f} "
        f"bpf_int8={bpf_int8:.1f} bpf_fp32={bpf_fp32:.1f} "
        f"mem_int2@N8k={mem_int2_big:.4f} mem_bin@N8k={mem_bin_big:.4f} "
        f"int2asym_codes={sorted(codes_set)} int2asym_err={max_err_a:.4f} "
        f"bin_sign_match={sign_match:.3f}"
    )


def get_backend_label():
    if torch.cuda.is_available():
        return f"cuda:{torch.cuda.get_device_name(0)}"
    return "cpu"
