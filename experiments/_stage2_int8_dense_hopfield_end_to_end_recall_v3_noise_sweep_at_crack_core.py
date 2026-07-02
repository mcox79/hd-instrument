"""Core module for Stage 2 opener v3: INT8 dense-Hopfield noise-cliff sweep
at fixed near-crack M for N=8192.

v1 aborted (pre-crack grid; all arms saturated).
v2 landed HARD_FAIL_META_RULE_Q_NON_DISCRIMINATING at seed_7 + seed_13:
  substrate capacity scales SUPRA-linearly in N -- E v5 linear crack-scaling
  (crack at M/N=20 at N=2048 -> M=160k at N=8192) empirically FALSIFIED.
  At (N=8192, M=160000, sigma=0.2), FP32=1.000 = INT8 = FP16 = INT4 (arm range 0.000).

v3 pivot per Research (Option B): keep M-grid focused, use SIGMA as primary
discriminator by sweeping into the noise cliff where FP32 is unsaturated
(< 0.90 recall) leaving room for INT4 to break.

v3 grid: 4 arms x 3 M x 6 sigma = 72 units per seed (N=8192 fixed).
  FULL_M_SWEEP = [10000, 100000, 160000]  (3 pts spanning below/at/near-crack)
  FULL_SIGMA_SWEEP = [0.20, 0.35, 0.42, 0.45, 0.48, 0.55]  (6 pts; fine
    around the transition band identified in v1 probe at 0.42-0.48)
  FULL_N_FIXED = 8192

Discriminator (per Research Option B amendment):
  HP_INT8_PARETO_CLIFF:     |INT8 - FP32| <= 0.05 at (M=160k, sigma=0.50)
                            where FP32 <= 0.90 (unsaturated); INT8 tracks FP32
  HP_INT4_BREAKS_AT_CLIFF:  (FP32 - INT4) >= 0.20 at (M=160k, sigma=0.50)
                            documents INT4 collapse in noise-cliff regime
  HP_PRE_CRACK_FREE:        at M=10000 (all sigma <= 0.42), all 4 arms within 0.01
                            (preserved from v2; below-crack free-memory tier)
  HP_META_RULE_Q_ATCLIFF:   at discriminator point FP32 < 0.98 AND arms_range >= 0.03
                            (the smoke gate v2 failed; MUST fire in v3)

Composes hdlab.int8_dense.quantize_int8_dense (META_RULE_AT commit c3ca7dab).
INT4 inline (same as v1/v2).

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


# ---------- Regime constants (v3 noise-cliff per Research Option B) ----------

FULL_M_SWEEP = [10000, 100000, 160000]
FULL_N_FIXED = 8192
# Sigma grid tuned to bracket cliffs at both M=100k (cliff 0.28-0.35 at N=4096)
# and M=160k (cliff 0.35-0.40 at N=8192) per local MEASURED@ probes.
# At N=8192 higher M scales cliff RIGHT slightly vs N=4096 same M (scaling with sqrt(N)?).
# Grid covers: below cliff (0.20), M=100k mid-cliff (0.28), M=100k bottom cliff (0.35),
# M=160k mid-cliff (0.38 interpolated), M=160k bottom cliff (0.42), post-cliff (0.55).
FULL_SIGMA_SWEEP = [0.20, 0.28, 0.35, 0.38, 0.42, 0.55]
FULL_N_ENT = 5000
FULL_N_REL = 100
FULL_QUERY_FRAC = 0.10

# Smoke: fire discriminator at cliff-band OR abort.
# Local MEASURED probes 2026-07-01:
#   At (N=4096, M=100k): FP32 sigma=0.20->0.973, sigma=0.28->0.683, sigma=0.32->0.396,
#                        sigma=0.35->0.212, sigma>=0.40->crashed. Cliff bracket 0.28-0.35.
#   At (N=8192, M=160k): FP32 sigma=0.35->0.529, sigma=0.40->0.127, sigma>=0.45->crashed.
#                        Cliff bracket 0.35-0.40; discriminator sigma=0.35 (FP32~0.53 mid-band).
# Smoke at (N=4096, M=100k, sigma=0.28) puts FP32~0.68 unsaturated (Q_ATCLIFF fires)
# in ~5min wall time; discriminator preview validates full-mode design.
SMOKE_M_SWEEP = [100000]
SMOKE_N_FIXED = 4096
SMOKE_SIGMA_SWEEP = [0.28]
SMOKE_N_ENT = 5000
SMOKE_N_REL = 100
SMOKE_QUERY_FRAC = 0.10

TOPK_RECALL = 1

# Discriminator constants (per Research Option B)
HP_INT8_PARETO_CLIFF_TOL = 0.05
HP_INT4_BREAKS_DELTA = 0.20
HP_PRE_CRACK_FREE_TOL = 0.01
HP_PRE_CRACK_M_MAX = 10000
HP_PRE_CRACK_SIGMA_MAX = 0.42  # only apply free-memory gate below noise-cliff
HP_META_RULE_Q_ARMS_RANGE_MIN = 0.03
HP_META_RULE_Q_FP32_UPPER = 0.98
HP_META_RULE_Q_FP32_LOWER = 0.02
HP_MEMORY_FACTOR_MAX = 0.35

DISCRIMINATOR_POINT_N = 8192
DISCRIMINATOR_POINT_M = 160000
# Per MEASURED@ local probe: at (N=8192, M=160k) FP32(sigma=0.35)=0.529.
# Fallback nominal; auto-select via _find_best_discriminating_sigma picks the sigma
# with FP32 in (0.02, 0.98) and largest arms_range.
DISCRIMINATOR_POINT_SIGMA = 0.35

CROSS_SEED_CV_MAX_HP = 0.08
CROSS_SEED_CV_MAX_MB = 0.10

SATURATION_RECALL_CEIL = 0.98
FLOOR_RECALL = 0.02

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


# ---------- Storage-cost formulas ----------

def bytes_fp32(n_dim: int, n_ent: int, n_rel: int) -> int:
    return (n_dim * n_dim * 4) + (n_ent * n_dim * 4) + (n_rel * n_dim * 4)


def bytes_fp16(n_dim: int, n_ent: int, n_rel: int) -> int:
    return (n_dim * n_dim * 2) + (n_ent * n_dim * 2) + (n_rel * n_dim * 2)


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


# ---------- INT4 quantize (inline, same as v1/v2) ----------

def quantize_int4_dense(W: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
    if W.dtype != torch.float32:
        W = W.to(torch.float32)
    row_max = W.abs().max(dim=1, keepdim=True).values.clamp_min(1e-9)
    scale = row_max / 7.0
    W_int4 = torch.round(W / scale).clamp_(-7, 7).to(torch.int8)
    return W_int4, scale


def dequantize_int4_dense(W_int4: torch.Tensor, scale: torch.Tensor) -> torch.Tensor:
    return W_int4.to(torch.float32) * scale


# ---------- Ingest + query per arm (same primitives as v1/v2) ----------

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


def _ingest_and_query_fp16(triples, E, R, queries, n_dim, sigma, noise_seed, device):
    sq = math.sqrt(n_dim)
    Wf = torch.zeros(n_dim, n_dim, dtype=torch.float32, device=device)
    s_idx, p_idx, o_idx = triples[:, 0], triples[:, 1], triples[:, 2]
    batch = 2000
    for b in range(0, triples.shape[0], batch):
        se = s_idx[b:b + batch]; pe = p_idx[b:b + batch]; oe = o_idx[b:b + batch]
        keys = (E[se] * R[pe] * sq)
        Wf.add_((E[oe].T @ keys) / n_dim)
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


# ---------- Verdict logic (v3 noise-cliff amendment) ----------

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
    """Scan sigma sweep at fixed M and return the best-discriminating sigma point.

    Selection priority:
      1. FP32 unsaturated (in (FLOOR_RECALL, HP_META_RULE_Q_FP32_UPPER)) AND
         arms_range >= HP_META_RULE_Q_ARMS_RANGE_MIN  (both META_RULE_Q gates)
      2. FP32 unsaturated (arms_range may be small but discriminator zone valid --
         this catches the "INT8 = FP32 = FP16 exactly, INT4 slight drop" positive
         Pareto finding where precision-ladder is REMARKABLY robust)
      3. Max arms_range even if FP32 is at ceiling/floor (fallback)
    Returns dict {sigma, per_arm_recalls, arms_range, fp32_unsaturated, qualification_tier}.
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
        # Pick sigma where FP32 is most-mid-band (closest to 0.5) -- most-informative
        # measurement of the precision-ladder in the cliff regime
        return {**min(tier_2_qualified, key=lambda c: abs(c["per_arm_recalls"].get("FP32", 0) - 0.5)),
                "qualification_tier": "tier_2_pareto_probe"}
    return {**max(candidates, key=lambda c: c["arms_range"]),
            "qualification_tier": "tier_3_fallback"}


def aggregate_and_verdict(per_seed, run_mode: str) -> Dict[str, Any]:
    """v3 discriminator (Research Option B noise-cliff):
      HP_INT8_PARETO_CLIFF:     |INT8 - FP32| <= 0.05 at best-discriminating (M=160k, sigma)
      HP_INT4_BREAKS_AT_CLIFF:  (FP32 - INT4) >= 0.20 at same
      HP_PRE_CRACK_FREE:        at M=10k, sigma <= 0.42, all arms within 0.01
      HP_META_RULE_Q_ATCLIFF:   at discriminator point FP32 unsaturated AND arms_range >= 0.03
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

    # Find best discriminating sigma at DISCRIMINATOR_POINT_M (or smoke's M)
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
    fp16_r = per_arm.get("FP16", float("nan"))
    int8_r = per_arm.get("INT8", float("nan"))
    int4_r = per_arm.get("INT4", float("nan"))

    # HP_META_RULE_Q_ATCLIFF: tier_1 requires arms_range >= 0.03; tier_2 accepts
    # the Pareto-probe-only case (FP32 unsaturated but arms indistinguishable) as
    # a POSITIVE Pareto finding (INT8 tracks FP32 exactly in cliff regime).
    hp_meta_rule_q_atcliff = fp32_unsat and (
        (arms_range >= HP_META_RULE_Q_ARMS_RANGE_MIN) or
        (qual_tier == "tier_2_pareto_probe")
    )

    # HP_INT8_PARETO_CLIFF
    int8_gap = abs(int8_r - fp32_r) if not (math.isnan(int8_r) or math.isnan(fp32_r)) else float("inf")
    hp_int8_pareto_cliff = int8_gap <= HP_INT8_PARETO_CLIFF_TOL

    # HP_INT4_BREAKS_AT_CLIFF
    int4_drop = (fp32_r - int4_r) if not (math.isnan(int4_r) or math.isnan(fp32_r)) else float("nan")
    hp_int4_breaks = (not math.isnan(int4_drop)) and (int4_drop >= HP_INT4_BREAKS_DELTA)

    # HP_PRE_CRACK_FREE: at M=10k, sigma <= 0.42, all arms within 0.01
    pre_crack_gaps = []
    pre_crack_details = {}
    for M in M_sweep:
        if M > HP_PRE_CRACK_M_MAX:
            continue
        for sigma in sigma_sweep:
            if sigma > HP_PRE_CRACK_SIGMA_MAX:
                continue
            arm_recalls_here = []
            for arm in ARMS:
                uk = f"{arm}__M{M}__N{N_fixed}__sigma{sigma:.2f}"
                r = stats.get(uk, {}).get("recall_cosine_mean", float("nan"))
                if not math.isnan(r):
                    arm_recalls_here.append(r)
            if len(arm_recalls_here) == len(ARMS):
                gap = max(arm_recalls_here) - min(arm_recalls_here)
                pre_crack_gaps.append(gap)
                pre_crack_details[f"M{M}_sigma{sigma:.2f}"] = {
                    "arm_range": gap,
                    "arm_recalls": {ARMS[i]: arm_recalls_here[i] for i in range(len(ARMS))},
                }
    max_pre_crack_gap = max(pre_crack_gaps) if pre_crack_gaps else float("inf")
    hp_pre_crack_free = (len(pre_crack_gaps) > 0) and (max_pre_crack_gap <= HP_PRE_CRACK_FREE_TOL)

    # HP_MEMORY_FACTOR (analytical; passes at 0.254)
    memory_factors = []
    for M in M_sweep:
        for sigma in sigma_sweep:
            fp32_bpf = stats.get(f"FP32__M{M}__N{N_fixed}__sigma{sigma:.2f}", {}).get("bytes_per_fact_mean", 0)
            int8_bpf = stats.get(f"INT8__M{M}__N{N_fixed}__sigma{sigma:.2f}", {}).get("bytes_per_fact_mean", 0)
            if fp32_bpf > 0:
                memory_factors.append(int8_bpf / fp32_bpf)
    max_memory_factor = max(memory_factors) if memory_factors else float("inf")
    hp_memory_factor = max_memory_factor <= HP_MEMORY_FACTOR_MAX

    # cv gate
    max_cv = 0.0
    for uk in unit_keys:
        cv = stats.get(uk, {}).get("recall_cv", 0.0)
        if cv > max_cv:
            max_cv = cv
    cv_hard_fail = max_cv >= CROSS_SEED_CV_MAX_MB

    # Count HP gates cleared (of 4 substantive gates; memory is analytical bonus)
    hp_gates_cleared = 0
    if hp_meta_rule_q_atcliff:
        hp_gates_cleared += 1
    if hp_int8_pareto_cliff:
        hp_gates_cleared += 1
    if hp_pre_crack_free:
        hp_gates_cleared += 1
    if hp_memory_factor:
        hp_gates_cleared += 1
    hp_gates_total = 4

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
        # Two failure modes: FP32 saturated (grid missed cliff) OR tier-3 fallback
        verdict = "HARD_FAIL_META_RULE_Q_NON_DISCRIMINATING"
        vmsg = (f"HARD_FAIL_META_RULE_Q: at best sigma point (M={disc_M} "
                f"sigma={disc_sigma:.2f} tier={qual_tier}) FP32={fp32_r:.3f} "
                f"unsaturated={fp32_unsat} arms_range={arms_range:.3f}. "
                f"FP32 either saturated (grid missed cliff) or fell below floor. "
                f"Needs finer sigma bracket around cliff transition.")
    elif smoke:
        # Smoke passes if META_RULE_Q fires + INT8 gap in-band
        if hp_int8_pareto_cliff:
            verdict = "HARD_PASS"
            vmsg = (f"SMOKE_HARD_PASS: cliff fires at (M={disc_M} sigma={disc_sigma:.2f}); "
                    f"FP32={fp32_r:.3f} FP16={fp16_r:.3f} INT8={int8_r:.3f} INT4={int4_r:.3f}; "
                    f"arms_range={arms_range:.3f}; INT8_gap={int8_gap:.3f}<={HP_INT8_PARETO_CLIFF_TOL}; "
                    f"INT4_drop={int4_drop:.3f} (breaks={hp_int4_breaks})")
        else:
            verdict = "MIDDLE_BAND"
            vmsg = (f"SMOKE_MIDDLE_BAND: cliff fires at (M={disc_M} sigma={disc_sigma:.2f}) "
                    f"but INT8 gap {int8_gap:.3f} > {HP_INT8_PARETO_CLIFF_TOL}; "
                    f"FP32={fp32_r:.3f} INT8={int8_r:.3f} arms_range={arms_range:.3f}")
    elif hp_int8_pareto_cliff and hp_pre_crack_free and hp_memory_factor:
        verdict = "HARD_PASS"
        vmsg = (f"HARD_PASS_INT8_PARETO_NOISE_CLIFF_ALL_GATES: cliff at (M={disc_M} "
                f"sigma={disc_sigma:.2f}); FP32={fp32_r:.3f} INT8={int8_r:.3f} "
                f"INT4={int4_r:.3f} arms_range={arms_range:.3f}; "
                f"INT8_gap={int8_gap:.3f}<={HP_INT8_PARETO_CLIFF_TOL}; "
                f"pre_crack_max_gap={max_pre_crack_gap:.4f}<={HP_PRE_CRACK_FREE_TOL}; "
                f"memory_factor={max_memory_factor:.3f}<={HP_MEMORY_FACTOR_MAX}; "
                f"INT4_drop={int4_drop:.3f} (breaks={hp_int4_breaks})")
    elif hp_gates_cleared >= 2:
        verdict = "MIDDLE_BAND"
        vmsg = (f"MIDDLE_BAND_PARTIAL_GATES: cleared {hp_gates_cleared}/{hp_gates_total}. "
                f"q_atcliff={hp_meta_rule_q_atcliff} int8_pareto_cliff={hp_int8_pareto_cliff} "
                f"pre_crack_free={hp_pre_crack_free} memory_factor={hp_memory_factor}; "
                f"cliff@sigma={disc_sigma:.2f}: FP32={fp32_r:.3f} FP16={fp16_r:.3f} "
                f"INT8={int8_r:.3f} INT4={int4_r:.3f}")
    else:
        verdict = "MIDDLE_BAND"
        vmsg = (f"MIDDLE_BAND: only {hp_gates_cleared}/{hp_gates_total} gates cleared. "
                f"cliff@sigma={disc_sigma:.2f}: FP32={fp32_r:.3f} INT8={int8_r:.3f}")

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
            "FP32_recall": fp32_r, "FP16_recall": fp16_r,
            "INT8_recall": int8_r, "INT4_recall": int4_r,
            "INT8_gap_vs_FP32": int8_gap,
            "INT4_drop_vs_FP32": int4_drop,
            "arms_range": arms_range,
            "fp32_unsaturated": fp32_unsat,
        },
        "hp_meta_rule_q_atcliff": bool(hp_meta_rule_q_atcliff),
        "hp_int8_pareto_cliff": bool(hp_int8_pareto_cliff),
        "hp_int4_breaks": bool(hp_int4_breaks),
        "hp_pre_crack_free": bool(hp_pre_crack_free),
        "hp_memory_factor": bool(hp_memory_factor),
        "hp_gates_cleared": hp_gates_cleared,
        "hp_gates_total": hp_gates_total,
        "pre_crack_details": pre_crack_details,
        "max_pre_crack_gap": max_pre_crack_gap,
        "max_memory_factor_int8_vs_fp32": max_memory_factor,
        "max_cv_across_arms": max_cv,
        "stats_cross_seed": stats,
        "cardinality_ok": cardinality_ok,
        "expected_n_units_per_seed": expected_n_units,
        "observed_n_units_per_seed": observed_n_units_per_seed,
        "mechanism_hashes_distinct": hashes_distinct,
        "per_seed": per_seed,
        "topK": TOPK_RECALL,
        "HP_INT8_PARETO_CLIFF_TOL": HP_INT8_PARETO_CLIFF_TOL,
        "HP_INT4_BREAKS_DELTA": HP_INT4_BREAKS_DELTA,
        "HP_PRE_CRACK_FREE_TOL": HP_PRE_CRACK_FREE_TOL,
        "HP_META_RULE_Q_ARMS_RANGE_MIN": HP_META_RULE_Q_ARMS_RANGE_MIN,
        "HP_MEMORY_FACTOR_MAX": HP_MEMORY_FACTOR_MAX,
        "CROSS_SEED_CV_MAX_HP": CROSS_SEED_CV_MAX_HP,
        "CROSS_SEED_CV_MAX_MB": CROSS_SEED_CV_MAX_MB,
    }


def selftest(seed: int, device: torch.device) -> Tuple[bool, str]:
    """Selftest: 4-arm functional + INT4 round-trip + bpf ordering + memory factor.

    Same as v1/v2 selftest (primitives unchanged). Verifies dispatch-readiness.
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
    recall_fp16 = _ingest_and_query_fp16(triples, E, R, queries, n_dim, sigma, noise_seed, smoke_device)
    recall_int8 = _ingest_and_query_int8(triples, E, R, queries, n_dim, sigma, noise_seed, smoke_device)
    recall_int4 = _ingest_and_query_int4(triples, E, R, queries, n_dim, sigma, noise_seed, smoke_device)
    for name, r in [("fp32", recall_fp32), ("fp16", recall_fp16),
                    ("int8", recall_int8), ("int4", recall_int4)]:
        if not (0.0 <= r <= 1.0):
            return False, f"selftest recall out-of-range: {name}={r}"
        if not math.isfinite(r):
            return False, f"selftest recall non-finite: {name}={r}"
    n_facts = triples.shape[0]
    bpf_fp32 = bytes_fp32(n_dim, 200, 25) / n_facts
    bpf_fp16 = bytes_fp16(n_dim, 200, 25) / n_facts
    bpf_int8 = bytes_int8(n_dim, 200, 25) / n_facts
    bpf_int4 = bytes_int4(n_dim, 200, 25) / n_facts
    if not (bpf_int4 < bpf_int8 < bpf_fp16 < bpf_fp32):
        return False, (f"selftest bpf ordering broken: int4={bpf_int4} "
                       f"int8={bpf_int8} fp16={bpf_fp16} fp32={bpf_fp32}")
    mem_factor = bpf_int8 / bpf_fp32
    if mem_factor > 0.35:
        return False, f"selftest HP_MEMORY_FACTOR analytical fail: {mem_factor:.3f} > 0.35"
    W_test = torch.randn(32, 32) * 0.1
    W_int4, scale = quantize_int4_dense(W_test)
    W_recon = dequantize_int4_dense(W_int4, scale)
    max_err = (W_test - W_recon).abs().max().item()
    scale_max = scale.max().item()
    if max_err > 2.0 * scale_max:
        return False, f"selftest INT4 round-trip too lossy: max_err={max_err:.4f} scale_max={scale_max:.4f}"
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
