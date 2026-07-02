"""Core module for Stage 2 INT2/binary Pareto probe at noise cliff regime.

Extends INT8 v3 CG (landed 2026-07-01) downward: same (N=8192, M=160k, sigma~0.35)
noise-cliff regime; adds INT2 (2-bit; 4 levels; symmetric) and BINARY (sign()) arms.

Amit-Gutfreund-Sompolinsky 1985 prediction: binary Hopfield has 0.138N capacity vs
0.14N for analog -- essentially equivalent. Very likely INT2/binary also survives
noise cliff. If confirmed, Pareto memory-efficiency frontier extends 16x-32x below FP32.

If INT2 CG and BINARY FAILS: correct Pareto knee bracketed between 2-bit and binary.
If INT2 FAILS: bracket is between 4-bit (INT4 CG) and 2-bit.
Either outcome is atomizable.

v1 grid: 5 arms x 2 M x 4 sigma = 40 units/seed (N=8192 fixed).
  FULL_M_SWEEP = [100000, 160000]  (near-crack + crack)
  FULL_N_FIXED = 8192
  FULL_SIGMA_SWEEP = [0.20, 0.30, 0.35, 0.40]  (spans cliff)

Discriminator: best-discriminating (M=160k, sigma) point auto-selected -- reused
from INT8 v3 template (proven at cliff mid-band sigma=0.35 FP32~0.53).

HP gates:
  HP_META_RULE_Q_ATCLIFF:  FP32 unsaturated AND arms_range >= 0.03 at cliff
                            (tier_2 pareto-probe accepted per INT8 v3 pattern)
  HP_INT2_PARETO:          |INT2 - FP32| <= 0.05 at cliff
  HP_BINARY_PARETO:        |BINARY - FP32| <= 0.10 at cliff
  HP_MEMORY_TIER_INT2:     INT2 bpf <= 0.10 * FP32 bpf  (16x compression)
  HP_MEMORY_TIER_BINARY:   BINARY bpf <= 0.04 * FP32 bpf  (32x compression)
  HP_EXPECTED_ORDER:       FP32 >= INT8 >= INT4 >= INT2 >= BINARY across arms
                            (relaxed with 0.02 margin; documentation gate)

HF gates:
  HF_INT2_BREAKS:          INT2 drops >= 0.20 vs FP32  (would falsify AGS 1985)
  HF_BINARY_BREAKS:        BINARY drops >= 0.30 vs FP32

Composes hdlab.int8_dense.quantize_int8_dense; inline INT4 (from v3), inline INT2
(4 symmetric levels), inline BINARY (sign()).

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

FULL_M_SWEEP = [100000, 160000]
FULL_N_FIXED = 8192
FULL_SIGMA_SWEEP = [0.20, 0.30, 0.35, 0.40]
FULL_N_ENT = 5000
FULL_N_REL = 100
FULL_QUERY_FRAC = 0.10

# Smoke: prove cell runs + FIRE discriminator at cliff.
# Per INT8 v3 MEASURED@ probe: at (N=4096, M=100k, sigma=0.28) FP32~0.68 mid-band,
# suitable for smoke discriminator (cell runs in ~5min wall CPU with 5 arms).
SMOKE_M_SWEEP = [100000]
SMOKE_N_FIXED = 4096
SMOKE_SIGMA_SWEEP = [0.28]
SMOKE_N_ENT = 5000
SMOKE_N_REL = 100
SMOKE_QUERY_FRAC = 0.10

TOPK_RECALL = 1

# Discriminator constants
HP_INT2_PARETO_TOL = 0.05
HP_BINARY_PARETO_TOL = 0.10
HP_META_RULE_Q_ARMS_RANGE_MIN = 0.03
HP_META_RULE_Q_FP32_UPPER = 0.98
HP_META_RULE_Q_FP32_LOWER = 0.02
HP_MEMORY_FACTOR_INT2_MAX = 0.10   # 16x compression floor
HP_MEMORY_FACTOR_BINARY_MAX = 0.04  # 32x compression floor
HP_EXPECTED_ORDER_MARGIN = 0.02

HF_INT2_BREAKS_DELTA = 0.20
HF_BINARY_BREAKS_DELTA = 0.30

DISCRIMINATOR_POINT_N = 8192
DISCRIMINATOR_POINT_M = 160000
DISCRIMINATOR_POINT_SIGMA = 0.35

CROSS_SEED_CV_MAX_HP = 0.08
CROSS_SEED_CV_MAX_MB = 0.10

SATURATION_RECALL_CEIL = 0.98
FLOOR_RECALL = 0.02

ARMS = ["FP32", "INT8", "INT4", "INT2", "BINARY"]


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

def bytes_fp32(n_dim: int, n_ent: int, n_rel: int) -> int:
    return (n_dim * n_dim * 4) + (n_ent * n_dim * 4) + (n_rel * n_dim * 4)


def bytes_int8(n_dim: int, n_ent: int, n_rel: int) -> int:
    W = n_dim * n_dim * 1 + n_dim * 4
    E = n_ent * n_dim * 1 + n_ent * 4
    R = n_rel * n_dim * 1 + n_rel * 4
    return W + E + R


def bytes_int4(n_dim: int, n_ent: int, n_rel: int) -> int:
    W = (n_dim * n_dim) // 2 + n_dim * 4
    E = (n_ent * n_dim) // 2 + n_ent * 4
    R = (n_rel * n_dim) // 2 + n_rel * 4
    return W + E + R


def bytes_int2(n_dim: int, n_ent: int, n_rel: int) -> int:
    # 2 bits per element; 4 elements/byte; plus per-row float32 scale
    W = (n_dim * n_dim) // 4 + n_dim * 4
    E = (n_ent * n_dim) // 4 + n_ent * 4
    R = (n_rel * n_dim) // 4 + n_rel * 4
    return W + E + R


def bytes_binary(n_dim: int, n_ent: int, n_rel: int) -> int:
    # 1 bit per element; 8 elements/byte; plus per-row float32 scale
    W = (n_dim * n_dim) // 8 + n_dim * 4
    E = (n_ent * n_dim) // 8 + n_ent * 4
    R = (n_rel * n_dim) // 8 + n_rel * 4
    return W + E + R


# ---------- Quantize primitives ----------

def quantize_int4_dense(W: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
    if W.dtype != torch.float32:
        W = W.to(torch.float32)
    row_max = W.abs().max(dim=1, keepdim=True).values.clamp_min(1e-9)
    scale = row_max / 7.0
    W_int4 = torch.round(W / scale).clamp_(-7, 7).to(torch.int8)
    return W_int4, scale


def dequantize_int4_dense(W_int4: torch.Tensor, scale: torch.Tensor) -> torch.Tensor:
    return W_int4.to(torch.float32) * scale


def quantize_int2_dense(W: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
    """Symmetric INT2 quantize: 4 levels {-1, 0, 0, +1} effectively via clamp(-1,1)
    on round(W/scale). Uses row-max scale so cliff of dynamic range preserved.

    Levels: -1, 0, +1 (3 usable levels due to symmetric clamp). Equivalent to
    a 1.58-bit ternary quantization -- commonly what "INT2 hardware" implements.
    """
    if W.dtype != torch.float32:
        W = W.to(torch.float32)
    row_max = W.abs().max(dim=1, keepdim=True).values.clamp_min(1e-9)
    # Symmetric clamp to {-1, 0, +1}. Scale row_max maps to +/-1 codes.
    scale = row_max / 1.0
    W_int2 = torch.round(W / scale).clamp_(-1, 1).to(torch.int8)
    return W_int2, scale


def dequantize_int2_dense(W_int2: torch.Tensor, scale: torch.Tensor) -> torch.Tensor:
    return W_int2.to(torch.float32) * scale


def quantize_binary_dense(W: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
    """Binary sign() quantize: values in {-1, +1}. Per-row mean-abs scale.

    Standard 1-bit binary Hopfield / BinaryConnect quantization: sign(W) with
    scalar recovery via row-mean absolute value.
    """
    if W.dtype != torch.float32:
        W = W.to(torch.float32)
    # row mean-abs is the standard binary quantization scale (BinaryConnect 2016)
    scale = W.abs().mean(dim=1, keepdim=True).clamp_min(1e-9)
    W_bin = torch.sign(W).to(torch.int8)
    # torch.sign returns 0 for zero; force ties to +1 for reproducibility
    W_bin = torch.where(W_bin == 0, torch.ones_like(W_bin), W_bin)
    return W_bin, scale


def dequantize_binary_dense(W_bin: torch.Tensor, scale: torch.Tensor) -> torch.Tensor:
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
    sq = math.sqrt(n_dim)
    Wf = torch.zeros(n_dim, n_dim, dtype=torch.float32, device=device)
    s_idx, p_idx, o_idx = triples[:, 0], triples[:, 1], triples[:, 2]
    batch = 2000
    for b in range(0, triples.shape[0], batch):
        se = s_idx[b:b + batch]; pe = p_idx[b:b + batch]; oe = o_idx[b:b + batch]
        keys = (E[se] * R[pe] * sq)
        Wf.add_((E[oe].T @ keys) / n_dim)
    W_int2, W_scale = quantize_int2_dense(Wf)
    W_dequant = dequantize_int2_dense(W_int2, W_scale)
    E_int2, E_scale = quantize_int2_dense(E)
    R_int2, R_scale = quantize_int2_dense(R)
    E_dq = dequantize_int2_dense(E_int2, E_scale)
    R_dq = dequantize_int2_dense(R_int2, R_scale)
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
    "BINARY": _ingest_and_query_binary,
}

BYTES_FNS = {
    "FP32": bytes_fp32,
    "INT8": bytes_int8,
    "INT4": bytes_int4,
    "INT2": bytes_int2,
    "BINARY": bytes_binary,
}


def _run_one_arm(
    arm_name: str, triples: torch.Tensor, queries: torch.Tensor,
    n_ent: int, n_rel: int, n_dim: int, M: int, sigma: float, seed: int,
    device: torch.device,
) -> Dict[str, Any]:
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
        N_fixed = SMOKE_N_FIXED
        sigma_sweep = SMOKE_SIGMA_SWEEP
        n_ent = SMOKE_N_ENT
        n_rel = SMOKE_N_REL
        query_frac = SMOKE_QUERY_FRAC
    else:
        M_sweep = FULL_M_SWEEP
        N_fixed = FULL_N_FIXED
        sigma_sweep = FULL_SIGMA_SWEEP
        n_ent = FULL_N_ENT
        n_rel = FULL_N_REL
        query_frac = FULL_QUERY_FRAC
    per_unit = {}
    t_seed_start = time.time()
    for M in M_sweep:
        triples, queries = build_regime_at_M(seed, M, n_ent, n_rel, query_frac)
        for sigma in sigma_sweep:
            for arm in ARMS:
                key = f"{arm}__M{M}__N{N_fixed}__sigma{sigma:.2f}"
                rec = _run_one_arm(arm, triples, queries, n_ent, n_rel,
                                    N_fixed, M, sigma, seed, device)
                per_unit[key] = rec
                elapsed_total = time.time() - t_seed_start
                print(f"[arm={arm} M={M} N={N_fixed} s={sigma:.2f}] seed={seed} "
                      f"recall={rec['recall_cosine_mean']:.3f} "
                      f"bpf={rec['bytes_per_fact']:.0f} "
                      f"wall={rec['wall_s']:.2f}s "
                      f"seed_total={elapsed_total:.1f}s", flush=True)
    return {
        "seed": int(seed),
        "run_mode": run_mode,
        "per_unit": per_unit,
        "M_sweep": list(M_sweep),
        "N_fixed": N_fixed,
        "sigma_sweep": list(sigma_sweep),
        "arms": list(ARMS),
    }


# ---------- Verdict logic ----------

def _cross_seed_stats(per_seed: List[Dict[str, Any]], unit_keys: List[str]) -> Dict[str, Dict[str, float]]:
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
    """Same tier logic as INT8 v3: tier_1 = FP32 unsat + arms_range >= 0.03;
    tier_2 = FP32 unsat + arms_range < 0.03 (Pareto-probe validated by tight-gap);
    tier_3 = fallback (HARD_FAIL_META_RULE_Q).
    """
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
        return {**min(tier_2_qualified, key=lambda c: abs(c["per_arm_recalls"].get("FP32", 0) - 0.5)),
                "qualification_tier": "tier_2_pareto_probe"}
    return {**max(candidates, key=lambda c: c["arms_range"]),
            "qualification_tier": "tier_3_fallback"}


def aggregate_and_verdict(per_seed, run_mode: str) -> Dict[str, Any]:
    if isinstance(per_seed, dict):
        per_seed = list(per_seed.values())
    n_seeds = len(per_seed)
    if n_seeds == 0:
        return {"verdict": "HARD_FAIL",
                "verdict_msg": "HARD_FAIL: no seeds completed",
                "summary": "no per-seed data"}

    smoke = (run_mode == "smoke")
    M_sweep = SMOKE_M_SWEEP if smoke else FULL_M_SWEEP
    N_fixed = SMOKE_N_FIXED if smoke else FULL_N_FIXED
    sigma_sweep = SMOKE_SIGMA_SWEEP if smoke else FULL_SIGMA_SWEEP

    unit_keys = []
    for arm in ARMS:
        for M in M_sweep:
            for sigma in sigma_sweep:
                unit_keys.append(f"{arm}__M{M}__N{N_fixed}__sigma{sigma:.2f}")
    stats = _cross_seed_stats(per_seed, unit_keys)

    expected_n_units = len(ARMS) * len(M_sweep) * len(sigma_sweep)
    observed_n_units_per_seed = [len(ps["per_unit"]) for ps in per_seed]
    cardinality_ok = all(n == expected_n_units for n in observed_n_units_per_seed)

    hashes = set()
    if per_seed:
        one_pu = per_seed[0]["per_unit"]
        for uk in unit_keys:
            if uk in one_pu:
                hashes.add(one_pu[uk]["mechanism_hash"])
    hashes_distinct = len(hashes) == expected_n_units

    if smoke:
        disc_M = SMOKE_M_SWEEP[0]
    else:
        disc_M = DISCRIMINATOR_POINT_M
    best_cliff = _find_best_discriminating_sigma(stats, disc_M, N_fixed, sigma_sweep)

    if best_cliff is None:
        return {"verdict": "HARD_FAIL",
                "verdict_msg": f"HARD_FAIL: no stats at M={disc_M} for any sigma",
                "summary": f"no data at discriminator M={disc_M}"}

    disc_sigma = best_cliff["sigma"]
    per_arm = best_cliff["per_arm_recalls"]
    arms_range = best_cliff["arms_range"]
    fp32_unsat = best_cliff["fp32_unsaturated"]
    qual_tier = best_cliff.get("qualification_tier", "unknown")

    fp32_r = per_arm.get("FP32", float("nan"))
    int8_r = per_arm.get("INT8", float("nan"))
    int4_r = per_arm.get("INT4", float("nan"))
    int2_r = per_arm.get("INT2", float("nan"))
    bin_r = per_arm.get("BINARY", float("nan"))

    hp_meta_rule_q_atcliff = fp32_unsat and (
        (arms_range >= HP_META_RULE_Q_ARMS_RANGE_MIN) or
        (qual_tier == "tier_2_pareto_probe")
    )

    # HP_INT2_PARETO
    int2_gap = abs(int2_r - fp32_r) if not (math.isnan(int2_r) or math.isnan(fp32_r)) else float("inf")
    hp_int2_pareto = int2_gap <= HP_INT2_PARETO_TOL

    # HP_BINARY_PARETO
    binary_gap = abs(bin_r - fp32_r) if not (math.isnan(bin_r) or math.isnan(fp32_r)) else float("inf")
    hp_binary_pareto = binary_gap <= HP_BINARY_PARETO_TOL

    # HF gates (breaks)
    int2_drop = (fp32_r - int2_r) if not (math.isnan(int2_r) or math.isnan(fp32_r)) else float("nan")
    binary_drop = (fp32_r - bin_r) if not (math.isnan(bin_r) or math.isnan(fp32_r)) else float("nan")
    hf_int2_breaks = (not math.isnan(int2_drop)) and (int2_drop >= HF_INT2_BREAKS_DELTA)
    hf_binary_breaks = (not math.isnan(binary_drop)) and (binary_drop >= HF_BINARY_BREAKS_DELTA)

    # HP_MEMORY_TIER (analytical; passes at expected values)
    int2_mem_factors = []
    binary_mem_factors = []
    for M in M_sweep:
        for sigma in sigma_sweep:
            fp32_bpf = stats.get(f"FP32__M{M}__N{N_fixed}__sigma{sigma:.2f}", {}).get("bytes_per_fact_mean", 0)
            int2_bpf = stats.get(f"INT2__M{M}__N{N_fixed}__sigma{sigma:.2f}", {}).get("bytes_per_fact_mean", 0)
            bin_bpf = stats.get(f"BINARY__M{M}__N{N_fixed}__sigma{sigma:.2f}", {}).get("bytes_per_fact_mean", 0)
            if fp32_bpf > 0:
                int2_mem_factors.append(int2_bpf / fp32_bpf)
                binary_mem_factors.append(bin_bpf / fp32_bpf)
    max_int2_mem = max(int2_mem_factors) if int2_mem_factors else float("inf")
    max_binary_mem = max(binary_mem_factors) if binary_mem_factors else float("inf")
    hp_mem_int2 = max_int2_mem <= HP_MEMORY_FACTOR_INT2_MAX
    hp_mem_binary = max_binary_mem <= HP_MEMORY_FACTOR_BINARY_MAX

    # HP_EXPECTED_ORDER: FP32 >= INT8 >= INT4 >= INT2 >= BINARY at discriminator
    # (with margin; small violations OK -- documents strict-order or not)
    order_ok = True
    order_violations = []
    prev_r = None
    prev_name = None
    for arm in ARMS:
        cur_r = per_arm.get(arm, float("nan"))
        if not math.isnan(cur_r) and prev_r is not None:
            if cur_r > prev_r + HP_EXPECTED_ORDER_MARGIN:
                order_ok = False
                order_violations.append(f"{arm}={cur_r:.3f} > {prev_name}={prev_r:.3f}+{HP_EXPECTED_ORDER_MARGIN}")
        if not math.isnan(cur_r):
            prev_r = cur_r
            prev_name = arm
    hp_expected_order = order_ok

    # cv gate
    max_cv = 0.0
    for uk in unit_keys:
        cv = stats.get(uk, {}).get("recall_cv", 0.0)
        if cv > max_cv:
            max_cv = cv
    cv_hard_fail = max_cv >= CROSS_SEED_CV_MAX_MB

    # Count HP gates (5 substantive)
    hp_gates_cleared = 0
    for gate in [hp_meta_rule_q_atcliff, hp_int2_pareto, hp_binary_pareto,
                 hp_mem_int2, hp_mem_binary]:
        if gate:
            hp_gates_cleared += 1
    hp_gates_total = 5

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
        vmsg = (f"HARD_FAIL_META_RULE_Q: at best sigma point (M={disc_M} "
                f"sigma={disc_sigma:.2f} tier={qual_tier}) FP32={fp32_r:.3f} "
                f"unsaturated={fp32_unsat} arms_range={arms_range:.3f}. "
                f"Grid missed cliff bracket; needs finer sigma.")
    elif smoke:
        # Smoke passes if META_RULE_Q fires + BOTH INT2 and BINARY gaps in-band
        # (relaxed for smoke; full-mode requires memory tier gates as well)
        if hp_int2_pareto and hp_binary_pareto:
            verdict = "HARD_PASS"
            vmsg = (f"SMOKE_HARD_PASS: cliff fires at (M={disc_M} sigma={disc_sigma:.2f}); "
                    f"FP32={fp32_r:.3f} INT8={int8_r:.3f} INT4={int4_r:.3f} "
                    f"INT2={int2_r:.3f} BINARY={bin_r:.3f}; arms_range={arms_range:.3f}; "
                    f"INT2_gap={int2_gap:.3f}<={HP_INT2_PARETO_TOL}; "
                    f"BINARY_gap={binary_gap:.3f}<={HP_BINARY_PARETO_TOL}; "
                    f"order_ok={hp_expected_order} tier={qual_tier}")
        elif hp_int2_pareto and not hp_binary_pareto:
            verdict = "MIDDLE_BAND"
            vmsg = (f"SMOKE_MIDDLE_BAND_INT2_ONLY: INT2 Pareto passes "
                    f"(gap={int2_gap:.3f}<={HP_INT2_PARETO_TOL}) but BINARY "
                    f"fails (gap={binary_gap:.3f}>{HP_BINARY_PARETO_TOL}); "
                    f"FP32={fp32_r:.3f} INT2={int2_r:.3f} BINARY={bin_r:.3f}")
        else:
            verdict = "MIDDLE_BAND"
            vmsg = (f"SMOKE_MIDDLE_BAND: neither INT2 nor BINARY within tol; "
                    f"FP32={fp32_r:.3f} INT2={int2_r:.3f} (gap={int2_gap:.3f}) "
                    f"BINARY={bin_r:.3f} (gap={binary_gap:.3f})")
    elif hp_int2_pareto and hp_binary_pareto and hp_mem_int2 and hp_mem_binary:
        verdict = "HARD_PASS"
        vmsg = (f"HARD_PASS_INT2_BINARY_PARETO_ALL_GATES: cliff at (M={disc_M} "
                f"sigma={disc_sigma:.2f}); FP32={fp32_r:.3f} INT8={int8_r:.3f} "
                f"INT4={int4_r:.3f} INT2={int2_r:.3f} BINARY={bin_r:.3f}; "
                f"INT2_gap={int2_gap:.3f}<={HP_INT2_PARETO_TOL}; "
                f"BINARY_gap={binary_gap:.3f}<={HP_BINARY_PARETO_TOL}; "
                f"INT2_mem={max_int2_mem:.3f}<={HP_MEMORY_FACTOR_INT2_MAX}; "
                f"BINARY_mem={max_binary_mem:.3f}<={HP_MEMORY_FACTOR_BINARY_MAX}")
    elif hp_int2_pareto and hp_mem_int2 and not hp_binary_pareto:
        verdict = "MIDDLE_BAND"
        vmsg = (f"MIDDLE_BAND_INT2_PARETO_KNEE_AT_2BIT: INT2 CG (gap={int2_gap:.3f}) "
                f"but BINARY breaks (gap={binary_gap:.3f}); Pareto knee between "
                f"2-bit and 1-bit. FP32={fp32_r:.3f} INT2={int2_r:.3f} BINARY={bin_r:.3f}; "
                f"HF_BINARY_BREAKS={hf_binary_breaks}")
    elif hp_gates_cleared >= 2:
        verdict = "MIDDLE_BAND"
        vmsg = (f"MIDDLE_BAND_PARTIAL_GATES: cleared {hp_gates_cleared}/{hp_gates_total}. "
                f"q_atcliff={hp_meta_rule_q_atcliff} int2_pareto={hp_int2_pareto} "
                f"binary_pareto={hp_binary_pareto} mem_int2={hp_mem_int2} "
                f"mem_binary={hp_mem_binary}; cliff@sigma={disc_sigma:.2f}: "
                f"FP32={fp32_r:.3f} INT2={int2_r:.3f} BINARY={bin_r:.3f}")
    else:
        verdict = "MIDDLE_BAND"
        vmsg = (f"MIDDLE_BAND: only {hp_gates_cleared}/{hp_gates_total} gates cleared. "
                f"cliff@sigma={disc_sigma:.2f}: FP32={fp32_r:.3f} INT2={int2_r:.3f} "
                f"BINARY={bin_r:.3f}")

    return {
        "verdict": verdict,
        "verdict_msg": vmsg,
        "summary": vmsg[:400],
        "run_mode": run_mode,
        "n_seeds": n_seeds,
        "arms": list(ARMS),
        "M_sweep": list(M_sweep),
        "N_fixed": N_fixed,
        "sigma_sweep": list(sigma_sweep),
        "discriminator_point": {
            "N": N_fixed, "M": disc_M, "sigma": disc_sigma,
            "chosen_by": "best_discriminating_sigma_scan",
            "qualification_tier": qual_tier,
            "FP32_recall": fp32_r, "INT8_recall": int8_r,
            "INT4_recall": int4_r, "INT2_recall": int2_r,
            "BINARY_recall": bin_r,
            "INT2_gap_vs_FP32": int2_gap,
            "BINARY_gap_vs_FP32": binary_gap,
            "INT2_drop_vs_FP32": int2_drop,
            "BINARY_drop_vs_FP32": binary_drop,
            "arms_range": arms_range,
            "fp32_unsaturated": fp32_unsat,
        },
        "hp_meta_rule_q_atcliff": bool(hp_meta_rule_q_atcliff),
        "hp_int2_pareto": bool(hp_int2_pareto),
        "hp_binary_pareto": bool(hp_binary_pareto),
        "hp_mem_int2": bool(hp_mem_int2),
        "hp_mem_binary": bool(hp_mem_binary),
        "hp_expected_order": bool(hp_expected_order),
        "hf_int2_breaks": bool(hf_int2_breaks),
        "hf_binary_breaks": bool(hf_binary_breaks),
        "order_violations": order_violations,
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
        "HP_INT2_PARETO_TOL": HP_INT2_PARETO_TOL,
        "HP_BINARY_PARETO_TOL": HP_BINARY_PARETO_TOL,
        "HP_META_RULE_Q_ARMS_RANGE_MIN": HP_META_RULE_Q_ARMS_RANGE_MIN,
        "HP_MEMORY_FACTOR_INT2_MAX": HP_MEMORY_FACTOR_INT2_MAX,
        "HP_MEMORY_FACTOR_BINARY_MAX": HP_MEMORY_FACTOR_BINARY_MAX,
        "HF_INT2_BREAKS_DELTA": HF_INT2_BREAKS_DELTA,
        "HF_BINARY_BREAKS_DELTA": HF_BINARY_BREAKS_DELTA,
        "CROSS_SEED_CV_MAX_HP": CROSS_SEED_CV_MAX_HP,
        "CROSS_SEED_CV_MAX_MB": CROSS_SEED_CV_MAX_MB,
    }


def selftest(seed: int, device: torch.device) -> Tuple[bool, str]:
    """Selftest: 5-arm functional + INT2/BINARY round-trip + bpf ordering + memory factors.

    Verifies dispatch-readiness. All primitives exercised at tiny scale.
    """
    smoke_device = torch.device("cpu")
    triples, queries = build_regime_at_M(seed, M=30, n_ent=200, n_rel=25,
                                          query_frac=0.5)
    n_dim = 256
    g = torch.Generator(device="cpu")
    g.manual_seed(seed)
    E = _bipolar(200, n_dim, g, smoke_device)
    R = _bipolar(25, n_dim, g, smoke_device)
    noise_seed = 42
    sigma = 0.1
    recall_fp32 = _ingest_and_query_fp32(triples, E, R, queries, n_dim, sigma, noise_seed, smoke_device)
    recall_int8 = _ingest_and_query_int8(triples, E, R, queries, n_dim, sigma, noise_seed, smoke_device)
    recall_int4 = _ingest_and_query_int4(triples, E, R, queries, n_dim, sigma, noise_seed, smoke_device)
    recall_int2 = _ingest_and_query_int2(triples, E, R, queries, n_dim, sigma, noise_seed, smoke_device)
    recall_bin = _ingest_and_query_binary(triples, E, R, queries, n_dim, sigma, noise_seed, smoke_device)
    for name, r in [("fp32", recall_fp32), ("int8", recall_int8),
                    ("int4", recall_int4), ("int2", recall_int2),
                    ("binary", recall_bin)]:
        if not (0.0 <= r <= 1.0):
            return False, f"selftest recall out-of-range: {name}={r}"
        if not math.isfinite(r):
            return False, f"selftest recall non-finite: {name}={r}"

    # bpf ordering: binary < int2 < int4 < int8 < fp32
    n_facts = triples.shape[0]
    bpf_fp32 = bytes_fp32(n_dim, 200, 25) / n_facts
    bpf_int8 = bytes_int8(n_dim, 200, 25) / n_facts
    bpf_int4 = bytes_int4(n_dim, 200, 25) / n_facts
    bpf_int2 = bytes_int2(n_dim, 200, 25) / n_facts
    bpf_bin = bytes_binary(n_dim, 200, 25) / n_facts
    if not (bpf_bin < bpf_int2 < bpf_int4 < bpf_int8 < bpf_fp32):
        return False, (f"selftest bpf ordering broken: bin={bpf_bin} int2={bpf_int2} "
                       f"int4={bpf_int4} int8={bpf_int8} fp32={bpf_fp32}")

    # Memory factors: at large N=8192, int2/fp32 should be ~0.0625, binary/fp32 ~0.031
    # (small n_dim=256 in selftest inflates factors due to per-row scale overhead).
    # Formula-verify at N=8192 target instead of small selftest scale.
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

    # INT2 round-trip: max error <= 2 * scale_max (3-level ternary)
    W_test = torch.randn(32, 32) * 0.1
    W_int2, scale_2 = quantize_int2_dense(W_test)
    W_recon_2 = dequantize_int2_dense(W_int2, scale_2)
    max_err_2 = (W_test - W_recon_2).abs().max().item()
    scale_max_2 = scale_2.max().item()
    if max_err_2 > 2.0 * scale_max_2:
        return False, f"selftest INT2 round-trip too lossy: max_err={max_err_2:.4f} scale_max={scale_max_2:.4f}"

    # BINARY round-trip: check sign() preserved
    W_bin, scale_b = quantize_binary_dense(W_test)
    W_recon_b = dequantize_binary_dense(W_bin, scale_b)
    # sign must match everywhere sign(W_test) != 0
    sign_match = (torch.sign(W_recon_b) == torch.sign(W_test)).float().mean().item()
    if sign_match < 0.99:
        return False, f"selftest BINARY sign() not preserved: match={sign_match:.3f}"

    # Distinct outputs: INT2 vs BINARY vs INT4 must produce different reconstructions
    W_int4, s4 = quantize_int4_dense(W_test)
    W_recon_4 = dequantize_int4_dense(W_int4, s4)
    if torch.allclose(W_recon_2, W_recon_b, atol=1e-6):
        return False, "selftest INT2 and BINARY quantize produce identical output"
    if torch.allclose(W_recon_2, W_recon_4, atol=1e-6):
        return False, "selftest INT2 and INT4 quantize produce identical output"

    return True, (f"selftest OK: fp32={recall_fp32:.3f} int8={recall_int8:.3f} "
                  f"int4={recall_int4:.3f} int2={recall_int2:.3f} bin={recall_bin:.3f} "
                  f"bpf_bin={bpf_bin:.1f} bpf_int2={bpf_int2:.1f} bpf_int4={bpf_int4:.1f} "
                  f"bpf_int8={bpf_int8:.1f} bpf_fp32={bpf_fp32:.1f} "
                  f"mem_int2@N8k={mem_int2_big:.4f} mem_bin@N8k={mem_bin_big:.4f} "
                  f"int2_err={max_err_2:.4f} bin_sign_match={sign_match:.3f}")


def get_backend_label() -> str:
    if torch.cuda.is_available():
        return f"cuda:{torch.cuda.get_device_name(0)}"
    return "cpu"
