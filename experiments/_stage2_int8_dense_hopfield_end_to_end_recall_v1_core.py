"""Core module for Stage 2 opener: INT8 dense-Hopfield end-to-end recall
Pareto-shape mapping across FP32 / FP16 / INT8 / INT4 precisions.

Stage 2 opener rationale: E v5 CG (2026-07-01) established INT8 Pareto-optimal
at M in {40k, 80k}, N=2048. This cell maps the Pareto SHAPE across:
  - 4 precision arms: FP32 / FP16 / INT8 / INT4
    (E v5 tested INT8 vs FP32 parity only; this extends the ladder)
  - 3 N: {2048, 4096, 8192}
  - 5 M: {100, 500, 1000, 5000, 10000} (LOWER range than E v5 to characterize
    pre-crack + crack-onset behavior; USER task spec Stage 2 opener)
  - 3 sigma (query noise, bipolar-flip fraction): {0.0, 0.2, 0.5}
    (E v5 fixed sigma=0.30; this maps the noise axis)
  - 3 seeds [7, 13, 19] via CHUNKED per-seed cells

Grid: 4 arms x 3 N x 5 M x 3 sigma = 180 units per seed = 540 across 3 seeds.

Discriminator (per USER task spec):
  HP_INT8_PARETO: INT8 recall within 0.05 of FP32 at (N=8192, M=1000, sigma=0.2)
  HP_INT4_BREAKS: INT4 recall drops >= 0.20 vs FP32 at same point
                  (documents where the precision ladder breaks)
  HP_MEMORY_FACTOR: INT8 total memory <= 0.35 * FP32 total memory at all arms
                    (INT8 = 4x smaller by construction; analytical verification)

Composes:
  - hdlab.int8_dense.quantize_int8_dense (INT8 arm; META_RULE_AT commit c3ca7dab)
  - Inline INT4 quantize (no hdlab primitive; 4-bit symmetric, per-row scale,
    packed 2 nibbles/byte)
  - torch.float16 / torch.float32 dtype-cast storage arms (no primitive
    composition; native torch dtype)

META_RULE compliance:
  - AT: composes hdlab/int8_dense.py
  - AX: distinct mechanism_hash per (arm, M, N, sigma)
  - H: CARDINALITY_OK = 180 units per seed; HARD_FAIL_CARDINALITY_BREACH
  - Q: at (N=8192, M=1000, sigma=0.2) discriminator point, FP32 recall must be
       < 0.98 (mechanism arm not saturated by construction) OR arms differ by
       at least 0.03 (there is a signal to measure)
  - AF: ARMS-MUST-DIFFER hash-test at smoke gate (bit-identical output = bug)
  - AH: atomic tmp + os.replace metrics writes

ASCII-only. No unicode.
"""
from __future__ import annotations

import hashlib
import math
import os
import time
from typing import Any, Dict, List, Tuple

import torch

from hdlab.int8_dense import quantize_int8_dense


# ---------- Regime constants (per USER task spec) ----------

FULL_M_SWEEP = [100, 500, 1000, 5000, 10000]
FULL_N_SWEEP = [2048, 4096, 8192]
FULL_SIGMA_SWEEP = [0.0, 0.2, 0.5]
FULL_N_ENT = 5000
FULL_N_REL = 100
FULL_QUERY_FRAC = 0.10  # 10% of M is query holdout

# Smoke: single discriminator-preview point at (N=4096, M=1000, sigma=0.2)
# All 4 arms must run so ARMS-MUST-DIFFER + INT8_vs_FP32 gap can be verified.
# N=4096 (between anchor 2048 and full 8192); M=1000 (mid-range); sigma=0.2
# (matches USER's HP_INT8_PARETO discriminator noise level).
# 4 arms x 1 N x 1 M x 1 sigma = 4 smoke units.
SMOKE_M_SWEEP = [1000]
SMOKE_N_SWEEP = [4096]
SMOKE_SIGMA_SWEEP = [0.2]
SMOKE_N_ENT = 2000
SMOKE_N_REL = 50
SMOKE_QUERY_FRAC = 0.10

TOPK_RECALL = 1

# Discriminator constants (per USER task spec)
HP_INT8_PARETO_TOL = 0.05                  # HP: |INT8 - FP32| <= 0.05
HP_INT4_BREAKS_DELTA = 0.20                # HP: (FP32 - INT4) >= 0.20 at gate point
HP_MEMORY_FACTOR_MAX = 0.35                # HP: INT8_bytes / FP32_bytes <= 0.35
DISCRIMINATOR_POINT_N = 8192
DISCRIMINATOR_POINT_M = 1000
DISCRIMINATOR_POINT_SIGMA = 0.2

# Cross-seed cv gate (per E v5 + META_RULE_L)
CROSS_SEED_CV_MAX_HP = 0.08
CROSS_SEED_CV_MAX_MB = 0.10

# Saturation ceiling for META_RULE_Q + baseline-in-band check
SATURATION_RECALL_CEIL = 0.98
FLOOR_RECALL = 0.05

ARMS = ["FP32", "FP16", "INT8", "INT4"]


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


# ---------- Storage-cost formulas (analytical, per arm) ----------

def bytes_fp32(n_dim: int, n_ent: int, n_rel: int) -> int:
    """FP32: 4 bytes per element, no metadata."""
    W = n_dim * n_dim * 4
    E = n_ent * n_dim * 4
    R = n_rel * n_dim * 4
    return W + E + R


def bytes_fp16(n_dim: int, n_ent: int, n_rel: int) -> int:
    """FP16 (float16): 2 bytes per element."""
    W = n_dim * n_dim * 2
    E = n_ent * n_dim * 2
    R = n_rel * n_dim * 2
    return W + E + R


def bytes_int8(n_dim: int, n_ent: int, n_rel: int) -> int:
    """INT8: 1 byte per element + 4 bytes per row scale."""
    W = n_dim * n_dim * 1 + n_dim * 4
    E = n_ent * n_dim * 1 + n_ent * 4
    R = n_rel * n_dim * 1 + n_rel * 4
    return W + E + R


def bytes_int4(n_dim: int, n_ent: int, n_rel: int) -> int:
    """INT4: 0.5 byte per element (packed 2 nibbles/byte) + 4 bytes per row scale."""
    W = (n_dim * n_dim) // 2 + n_dim * 4
    E = (n_ent * n_dim) // 2 + n_ent * 4
    R = (n_rel * n_dim) // 2 + n_rel * 4
    return W + E + R


# ---------- INT4 quantize (inline; no hdlab primitive yet) ----------

def quantize_int4_dense(W: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
    """Per-row max-scale symmetric quantize FP32 (N, N) -> INT4 stored as int8
    in range [-7, 7] + scale (N, 1). The int8 tensor uses only 4 bits of range
    per element (bytes_int4 formula counts 0.5 byte/elem for the packed
    storage cost). Compute path uses dequant to FP32 for matmul.

    Storage cost model: 0.5 byte/elem + 4-byte scale/row (see bytes_int4).
    """
    if W.dtype != torch.float32:
        W = W.to(torch.float32)
    row_max = W.abs().max(dim=1, keepdim=True).values.clamp_min(1e-9)
    scale = row_max / 7.0  # symmetric 4-bit: range [-7, 7]
    W_int4 = torch.round(W / scale).clamp_(-7, 7).to(torch.int8)
    return W_int4, scale


def dequantize_int4_dense(W_int4: torch.Tensor, scale: torch.Tensor) -> torch.Tensor:
    return W_int4.to(torch.float32) * scale


# ---------- Ingest + query per arm ----------

def _ingest_and_query_fp32(triples, E, R, queries, n_dim, sigma, noise_seed, device):
    """FP32 arm: baseline W accumulation + query in float32 throughout."""
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


def _ingest_and_query_fp16(triples, E, R, queries, n_dim, sigma, noise_seed, device):
    """FP16 arm: W stored as float16 (0.5x FP32 memory); matmul in fp32 via
    cast-on-load (production pattern; captures storage-fidelity loss only).

    Rationale (same as BFLOAT16 arm in v1): CPU fp16 matmul is slow without
    AVX512; production usage is fp16 storage + fp32 accumulator. Round-trip
    cast models the storage-fidelity loss faithfully.
    """
    sq = math.sqrt(n_dim)
    Wf = torch.zeros(n_dim, n_dim, dtype=torch.float32, device=device)
    s_idx, p_idx, o_idx = triples[:, 0], triples[:, 1], triples[:, 2]
    batch = 2000
    for b in range(0, triples.shape[0], batch):
        se = s_idx[b:b + batch]; pe = p_idx[b:b + batch]; oe = o_idx[b:b + batch]
        keys = (E[se] * R[pe] * sq)
        Wf.add_((E[oe].T @ keys) / n_dim)
    # Model fp16 storage via round-trip
    W_fp16 = Wf.to(torch.float16)
    W_dequant = W_fp16.to(torch.float32)
    E_rt = E.to(torch.float16).to(torch.float32)
    R_rt = R.to(torch.float16).to(torch.float32)
    q_s, q_p, q_o = queries[:, 0], queries[:, 1], queries[:, 2]
    q_keys = (E_rt[q_s] * R_rt[q_p] * sq)
    q_keys = _add_bipolar_noise(q_keys, sigma, seed=noise_seed)
    scores = q_keys @ W_dequant.T @ E_rt.T
    topk = torch.topk(scores, k=min(TOPK_RECALL, E.shape[0]), dim=1)
    hits = (topk.indices == q_o.unsqueeze(1)).any(dim=1).float().mean()
    return float(hits)


def _ingest_and_query_int8(triples, E, R, queries, n_dim, sigma, noise_seed, device):
    """INT8 arm: composes hdlab.int8_dense.quantize_int8_dense (META_RULE_AT)."""
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
    # E, R stored INT8 via same primitive (round-trip cast)
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
    """INT4 arm: inline quantize + dequant matmul path (0.25x FP32 memory)."""
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


ARM_FNS = {
    "FP32": _ingest_and_query_fp32,
    "FP16": _ingest_and_query_fp16,
    "INT8": _ingest_and_query_int8,
    "INT4": _ingest_and_query_int4,
}

BYTES_FNS = {
    "FP32": bytes_fp32,
    "FP16": bytes_fp16,
    "INT8": bytes_int8,
    "INT4": bytes_int4,
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
    # Memory estimate (analytical, per formula)
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
        "recall_cosine_mean": recall_k,   # per USER task spec
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
        N_sweep = SMOKE_N_SWEEP
        sigma_sweep = SMOKE_SIGMA_SWEEP
        n_ent = SMOKE_N_ENT
        n_rel = SMOKE_N_REL
        query_frac = SMOKE_QUERY_FRAC
    else:
        M_sweep = FULL_M_SWEEP
        N_sweep = FULL_N_SWEEP
        sigma_sweep = FULL_SIGMA_SWEEP
        n_ent = FULL_N_ENT
        n_rel = FULL_N_REL
        query_frac = FULL_QUERY_FRAC
    per_unit = {}
    for M in M_sweep:
        # Build M-regime once per M value; reuse across N x sigma x arm
        triples, queries = build_regime_at_M(seed, M, n_ent, n_rel, query_frac)
        for N in N_sweep:
            for sigma in sigma_sweep:
                for arm in ARMS:
                    key = f"{arm}__M{M}__N{N}__sigma{sigma:.2f}"
                    rec = _run_one_arm(arm, triples, queries, n_ent, n_rel,
                                        N, M, sigma, seed, device)
                    per_unit[key] = rec
                    print(f"[arm={arm} M={M} N={N} s={sigma:.2f}] seed={seed} "
                          f"recall={rec['recall_cosine_mean']:.3f} "
                          f"bpf={rec['bytes_per_fact']:.0f} "
                          f"wall={rec['wall_s']:.2f}s", flush=True)
    return {
        "seed": int(seed),
        "run_mode": run_mode,
        "per_unit": per_unit,
        "M_sweep": list(M_sweep),
        "N_sweep": list(N_sweep),
        "sigma_sweep": list(sigma_sweep),
        "arms": list(ARMS),
    }


# ---------- Verdict logic (per USER task spec) ----------

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


def aggregate_and_verdict(per_seed, run_mode: str) -> Dict[str, Any]:
    """v1 discriminator per USER task spec:
      HP_INT8_PARETO: |INT8_recall - FP32_recall| <= 0.05 at discriminator point
      HP_INT4_BREAKS: FP32_recall - INT4_recall >= 0.20 at discriminator point
                      (documents where the ladder breaks)
      HP_MEMORY_FACTOR: INT8_bytes / FP32_bytes <= 0.35 at all arms (analytical)
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
    N_sweep = SMOKE_N_SWEEP if smoke else FULL_N_SWEEP
    sigma_sweep = SMOKE_SIGMA_SWEEP if smoke else FULL_SIGMA_SWEEP

    unit_keys = []
    for arm in ARMS:
        for M in M_sweep:
            for N in N_sweep:
                for sigma in sigma_sweep:
                    unit_keys.append(f"{arm}__M{M}__N{N}__sigma{sigma:.2f}")
    stats = _cross_seed_stats(per_seed, unit_keys)

    expected_n_units = len(ARMS) * len(M_sweep) * len(N_sweep) * len(sigma_sweep)
    observed_n_units_per_seed = [len(ps["per_unit"]) for ps in per_seed]
    cardinality_ok = all(n == expected_n_units for n in observed_n_units_per_seed)

    # Mechanism hash distinctness
    hashes = set()
    if per_seed:
        one_pu = per_seed[0]["per_unit"]
        for uk in unit_keys:
            if uk in one_pu:
                hashes.add(one_pu[uk]["mechanism_hash"])
    hashes_distinct = len(hashes) == expected_n_units

    # Discriminator point evaluation
    # (in smoke, discriminator point = smoke point since smoke=1 point)
    if smoke:
        disc_N = SMOKE_N_SWEEP[0]
        disc_M = SMOKE_M_SWEEP[0]
        disc_sigma = SMOKE_SIGMA_SWEEP[0]
    else:
        disc_N = DISCRIMINATOR_POINT_N
        disc_M = DISCRIMINATOR_POINT_M
        disc_sigma = DISCRIMINATOR_POINT_SIGMA

    disc_recalls = {}
    for arm in ARMS:
        uk = f"{arm}__M{disc_M}__N{disc_N}__sigma{disc_sigma:.2f}"
        s = stats.get(uk, {})
        disc_recalls[arm] = s.get("recall_cosine_mean", float("nan"))

    fp32_r = disc_recalls.get("FP32", float("nan"))
    fp16_r = disc_recalls.get("FP16", float("nan"))
    int8_r = disc_recalls.get("INT8", float("nan"))
    int4_r = disc_recalls.get("INT4", float("nan"))

    # HP_INT8_PARETO
    int8_gap = abs(int8_r - fp32_r) if not (math.isnan(int8_r) or math.isnan(fp32_r)) else float("inf")
    hp_int8_pareto = int8_gap <= HP_INT8_PARETO_TOL

    # HP_INT4_BREAKS (documents breakage)
    int4_drop = (fp32_r - int4_r) if not (math.isnan(int4_r) or math.isnan(fp32_r)) else float("nan")
    hp_int4_breaks = (not math.isnan(int4_drop)) and (int4_drop >= HP_INT4_BREAKS_DELTA)

    # HP_MEMORY_FACTOR (analytical across ALL M/N; check any/all)
    memory_factors = []
    for M in M_sweep:
        for N in N_sweep:
            for sigma in sigma_sweep:
                fp32_bpf = stats.get(f"FP32__M{M}__N{N}__sigma{sigma:.2f}", {}).get("bytes_per_fact_mean", 0)
                int8_bpf = stats.get(f"INT8__M{M}__N{N}__sigma{sigma:.2f}", {}).get("bytes_per_fact_mean", 0)
                if fp32_bpf > 0:
                    memory_factors.append(int8_bpf / fp32_bpf)
    max_memory_factor = max(memory_factors) if memory_factors else float("inf")
    hp_memory_factor = max_memory_factor <= HP_MEMORY_FACTOR_MAX

    # cv gate (any storage arm cv >= 0.10 = HF; 0.08-0.10 = MB downgrade)
    max_cv = 0.0
    for uk in unit_keys:
        cv = stats.get(uk, {}).get("recall_cv", 0.0)
        if cv > max_cv:
            max_cv = cv
    cv_hard_fail = max_cv >= CROSS_SEED_CV_MAX_MB

    # META_RULE_Q: baseline-in-band at discriminator point
    # FP32 recall must be < 0.98 (not saturated) OR arms must differ by >= 0.03
    arm_recalls = [r for r in [fp32_r, fp16_r, int8_r, int4_r] if not math.isnan(r)]
    arms_range = (max(arm_recalls) - min(arm_recalls)) if arm_recalls else 0.0
    baseline_saturated = fp32_r >= SATURATION_RECALL_CEIL
    baseline_at_floor = fp32_r <= FLOOR_RECALL
    baseline_in_band = (not baseline_saturated) and (not baseline_at_floor)
    q_ok = baseline_in_band or (arms_range >= 0.03)

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
    elif not q_ok:
        verdict = "HARD_FAIL_META_RULE_Q_NON_DISCRIMINATING"
        vmsg = (f"HARD_FAIL_META_RULE_Q: at discriminator point (N={disc_N} "
                f"M={disc_M} sigma={disc_sigma}) baseline FP32={fp32_r:.3f} "
                f"saturated={baseline_saturated} at_floor={baseline_at_floor} "
                f"arms_range={arms_range:.3f}")
    elif hp_int8_pareto and hp_memory_factor:
        verdict = "HARD_PASS"
        vmsg = (f"HARD_PASS_INT8_PARETO_LADDER: at (N={disc_N} M={disc_M} "
                f"sigma={disc_sigma}) FP32={fp32_r:.3f} FP16={fp16_r:.3f} "
                f"INT8={int8_r:.3f} INT4={int4_r:.3f}; "
                f"INT8_gap={int8_gap:.3f}<={HP_INT8_PARETO_TOL}; "
                f"max_memory_factor(INT8/FP32)={max_memory_factor:.3f}<="
                f"{HP_MEMORY_FACTOR_MAX}; "
                f"INT4_drop={int4_drop:.3f} (breaks={hp_int4_breaks}); "
                f"max_cv={max_cv:.3f}")
    elif hp_int8_pareto:
        verdict = "MIDDLE_BAND"
        vmsg = (f"MIDDLE_BAND_INT8_PARETO_ONLY: INT8 Pareto holds (gap={int8_gap:.3f}) "
                f"but memory factor {max_memory_factor:.3f} > {HP_MEMORY_FACTOR_MAX}; "
                f"INT8={int8_r:.3f} FP32={fp32_r:.3f} INT4={int4_r:.3f}")
    elif hp_memory_factor:
        verdict = "MIDDLE_BAND"
        vmsg = (f"MIDDLE_BAND_MEMORY_ONLY: memory factor OK ({max_memory_factor:.3f}) "
                f"but INT8 Pareto gap {int8_gap:.3f} > {HP_INT8_PARETO_TOL}; "
                f"INT8={int8_r:.3f} FP32={fp32_r:.3f}")
    else:
        verdict = "MIDDLE_BAND"
        vmsg = (f"MIDDLE_BAND: neither INT8 Pareto nor memory factor gate cleared. "
                f"FP32={fp32_r:.3f} FP16={fp16_r:.3f} INT8={int8_r:.3f} "
                f"INT4={int4_r:.3f} int8_gap={int8_gap:.3f} "
                f"max_memory_factor={max_memory_factor:.3f}")

    return {
        "verdict": verdict,
        "verdict_msg": vmsg,
        "summary": vmsg[:400],
        "run_mode": run_mode,
        "n_seeds": n_seeds,
        "arms": list(ARMS),
        "M_sweep": list(M_sweep),
        "N_sweep": list(N_sweep),
        "sigma_sweep": list(sigma_sweep),
        "discriminator_point": {
            "N": disc_N, "M": disc_M, "sigma": disc_sigma,
            "FP32_recall": fp32_r, "FP16_recall": fp16_r,
            "INT8_recall": int8_r, "INT4_recall": int4_r,
            "INT8_gap_vs_FP32": int8_gap,
            "INT4_drop_vs_FP32": int4_drop,
        },
        "hp_int8_pareto": bool(hp_int8_pareto),
        "hp_int4_breaks": bool(hp_int4_breaks),
        "hp_memory_factor": bool(hp_memory_factor),
        "max_memory_factor_int8_vs_fp32": max_memory_factor,
        "max_cv_across_arms": max_cv,
        "meta_rule_q_baseline_in_band": bool(baseline_in_band),
        "meta_rule_q_arms_range": arms_range,
        "stats_cross_seed": stats,
        "cardinality_ok": cardinality_ok,
        "expected_n_units_per_seed": expected_n_units,
        "observed_n_units_per_seed": observed_n_units_per_seed,
        "mechanism_hashes_distinct": hashes_distinct,
        "per_seed": per_seed,
        "topK": TOPK_RECALL,
        "HP_INT8_PARETO_TOL": HP_INT8_PARETO_TOL,
        "HP_INT4_BREAKS_DELTA": HP_INT4_BREAKS_DELTA,
        "HP_MEMORY_FACTOR_MAX": HP_MEMORY_FACTOR_MAX,
        "CROSS_SEED_CV_MAX_HP": CROSS_SEED_CV_MAX_HP,
        "CROSS_SEED_CV_MAX_MB": CROSS_SEED_CV_MAX_MB,
    }


def selftest(seed: int, device: torch.device) -> Tuple[bool, str]:
    """Selftest: verify all 4 arms + formulas + INT4 quantize + memory ordering.

    Expected:
      - Recall in [0, 1] for all arms
      - bytes-per-fact ordering: INT4 < INT8 < FP16 < FP32 (analytical)
      - INT4 quantize round-trip: |W - dequant(quantize(W))| bounded by scale
      - HP_MEMORY_FACTOR analytical: INT8_bpf / FP32_bpf ~ 0.25 + O(N)/N^2 -> <= 0.35
      - INT4 quantize distinct from INT8 quantize (ARMS-MUST-DIFFER precursor)
    """
    smoke_device = torch.device("cpu")
    triples, queries = build_regime_at_M(seed, M=30, n_ent=200, n_rel=25,
                                          query_frac=0.5)
    n_dim = 256
    g = torch.Generator(device="cpu")
    g.manual_seed(seed)
    E = _bipolar(200, n_dim, g, smoke_device)
    R = _bipolar(25, n_dim, g, smoke_device)
    # noise_seed constant for selftest determinism
    noise_seed = 42
    sigma = 0.1
    recall_fp32 = _ingest_and_query_fp32(triples, E, R, queries, n_dim, sigma, noise_seed, smoke_device)
    recall_fp16 = _ingest_and_query_fp16(triples, E, R, queries, n_dim, sigma, noise_seed, smoke_device)
    recall_int8 = _ingest_and_query_int8(triples, E, R, queries, n_dim, sigma, noise_seed, smoke_device)
    recall_int4 = _ingest_and_query_int4(triples, E, R, queries, n_dim, sigma, noise_seed, smoke_device)
    for name, r in [("fp32", recall_fp32), ("fp16", recall_fp16),
                    ("int8", recall_int8), ("int4", recall_int4)]:
        if not (0.0 <= r <= 1.0):
            return False, f"selftest recall out-of-range: {name}={r}"
        if not math.isfinite(r):
            return False, f"selftest recall non-finite: {name}={r}"
    # Bytes-per-fact ordering (analytical): INT4 < INT8 < FP16 < FP32
    n_facts = triples.shape[0]
    bpf_fp32 = bytes_fp32(n_dim, 200, 25) / n_facts
    bpf_fp16 = bytes_fp16(n_dim, 200, 25) / n_facts
    bpf_int8 = bytes_int8(n_dim, 200, 25) / n_facts
    bpf_int4 = bytes_int4(n_dim, 200, 25) / n_facts
    if not (bpf_int4 < bpf_int8 < bpf_fp16 < bpf_fp32):
        return False, (f"selftest bpf ordering broken: int4={bpf_int4} "
                       f"int8={bpf_int8} fp16={bpf_fp16} fp32={bpf_fp32}")
    # HP_MEMORY_FACTOR analytical check
    mem_factor = bpf_int8 / bpf_fp32
    if mem_factor > 0.35:
        return False, f"selftest HP_MEMORY_FACTOR analytical fail: {mem_factor:.3f} > 0.35"
    # INT4 quantize round-trip: verify dequant close to original within scale
    W_test = torch.randn(32, 32) * 0.1
    W_int4, scale = quantize_int4_dense(W_test)
    W_recon = dequantize_int4_dense(W_int4, scale)
    max_err = (W_test - W_recon).abs().max().item()
    scale_max = scale.max().item()
    if max_err > 2.0 * scale_max:
        return False, f"selftest INT4 round-trip too lossy: max_err={max_err:.4f} scale_max={scale_max:.4f}"
    # INT4 vs INT8 quantize distinct (ARMS-MUST-DIFFER precursor)
    W_int8, s8 = quantize_int8_dense(W_test)
    W_int8_recon = W_int8.to(torch.float32) * s8
    if torch.allclose(W_recon, W_int8_recon, atol=1e-6):
        return False, "selftest INT4 and INT8 quantize produce identical output (ARMS bug)"
    return True, (f"selftest OK: fp32={recall_fp32:.3f} fp16={recall_fp16:.3f} "
                  f"int8={recall_int8:.3f} int4={recall_int4:.3f} "
                  f"bpf_int4={bpf_int4:.1f} bpf_int8={bpf_int8:.1f} "
                  f"bpf_fp16={bpf_fp16:.1f} bpf_fp32={bpf_fp32:.1f} "
                  f"mem_factor(int8/fp32)={mem_factor:.3f} "
                  f"int4_err={max_err:.4f}")


def get_backend_label() -> str:
    if torch.cuda.is_available():
        return f"cuda:{torch.cuda.get_device_name(0)}"
    return "cpu"
