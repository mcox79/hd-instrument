"""Shared core for sparsity_free_axis_v1 sibling cells.

Axis C sparsity as FREE axis at HRR-real chain-grade default; regime SWEPT
(PC single-bank + WM multi-bank K=500 B=16). Wave-2 gap analysis section 3
(CG=0.50, HIGH payoff, sparse-coding scope-expansion bonus).

Design (LOCKED):
    6 sparsity alpha x 2 regime = 12 phase points per seed FULL.
    Smoke: 6 alpha x PC only = 6 corner points per seed.

Fixed:
    encoder = hrr_real (chain-grade default; Gaussian codebook L2-normalized)
    binding = Hadamard (element-wise) for WM regime bind/unbind
    N = 8192 (cliff-observable per PC v2.2 CG)

Regime PC (pattern completion):
    M_items = 100 (FULL) / 50 (SMOKE)
    corruption c = 0.485 (cliff-K per PC v2.2 CG MEASURED@2daf9b55)
    T = 5, beta = 8.0

Regime WM (multi-bank working memory):
    K = 500 keys per bank (FULL) / 250 (SMOKE)
    B = 16 banks
    corruption c = 0.30
    T = 3, beta = 8.0

Sparsity levels (axis C; SWEPT):
    FULL:  {0.005, 0.010, 0.025, 0.050, 0.100, 0.200}
    SMOKE: same 6 levels (PC only)

Discriminator (HP band; META_RULE_L band-floor MB):
    HP_A: per_regime_sparsity_range >= 0.10 in >=1 regime (2 non-adjacent alpha)
    HP_B: monotonicity |Spearman rho| >= 0.80 with fixed direction in >=1 regime
    HP_C: 3-seed cv <= 0.10 per (regime, alpha) point
    HP_D: cardinality_ok
    HP_E: baseline_in_band (mechanism > floor + 5% band)
    HP_B is HP-critical (monotonicity = load-bearing lever claim)

Positive control (META_RULE_BC):
    PC hrr_real @ alpha=0.10, M=100, c=0.485: top1 in [0.30, 0.90]
    WM hrr_real @ alpha=0.10, K=500, B=16, c=0.30: bank-avg top1 in [0.20, 0.80]

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
    - arms_differ_verified at smoke gate (MECHANISM vs RANDOM_FLOOR per point)
    - final_metrics_atomicity: tmp_replace (per sibling cell main())
    - except SystemExit: raise BEFORE except Exception (see sibling cell main)
    - crlb_floor_computed via crlb_1step_cliff_prediction; reachable at c=0.485
    - baseline_in_band: RANDOM_FLOOR at chance
    - discriminator survives scale (smoke at full N=8192, half M)
    - HARD_PASS strictly above floor + 5% band-width
    - HP_SCOPE: HARD_PASS applies to MECHANISM arm only
    - cardinality_ok: EXPECTED_N_UNITS_FULL=12, SMOKE=6
    - per-unit failure-class: no bare except; halt on any per-point exception
    - calibration_check: default_ok_for_this_regime
    - all numbers tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@

ASCII-only. No unicode. CPU-eligible (numpy + small torch).

PRE-REG: preregs/2026-07-01_sparsity_free_axis_v1.md

Author: hdi_exp_dev 2026-07-01 (Opus 4.7 1M, agent-spawn; wave-2 section 3)
"""
from __future__ import annotations

import hashlib
import math
import os
import time
from typing import Any, Dict, List, Tuple

import numpy as np

import torch  # noqa: F401  PROT-020 marker

_CUDA_OK = bool(torch.cuda.is_available())
if _CUDA_OK:
    DEVICE = torch.device("cuda")
else:
    DEVICE = torch.device("cpu")


# ---------------------------------------------------------------------------
# Pre-reg constants (LOCKED at module init; META_RULE_AE)
# ---------------------------------------------------------------------------
SATURATED_TOP1 = 0.95
HARD_PASS_LO = 0.80
MIDDLE_BAND_LO = 0.50
FLOOR_TOP1 = 0.10
HP_DISCRIMINATOR = 0.50
MB_DISCRIMINATOR = 0.30

BETA = 8.0

# Encoder fixed (chain-grade default per wave-2 section 3)
ENCODER_FAMILY = "hrr_real"

# Sparsity levels (OUTER axis C; SWEPT)
SPARSITY_LEVELS_FULL = (0.005, 0.010, 0.025, 0.050, 0.100, 0.200)
SPARSITY_LEVELS_SMOKE = (0.005, 0.010, 0.025, 0.050, 0.100, 0.200)  # same alpha, PC-only regime

# Regime knobs (SECOND axis; SWEPT)
REGIMES_FULL = ("PC", "WM")
REGIMES_SMOKE = ("PC",)  # PC-only smoke per DISCRIMINATOR-SURVIVES-SCALE

# Fixed dimensionality
N_DIM_FULL = 8192
N_DIM_SMOKE = 8192  # DISCRIMINATOR-SURVIVES-SCALE

# PC regime
M_PC_FULL = 100
M_PC_SMOKE = 50
CORRUPTION_PC = 0.485  # cliff-K MEASURED@commit 2daf9b55
T_PC = 5

# WM regime
K_WM_FULL = 500
K_WM_SMOKE = 250
B_WM = 16
CORRUPTION_WM = 0.30
T_WM = 3

# Cardinality (LOCKED)
EXPECTED_N_UNITS_FULL = len(SPARSITY_LEVELS_FULL) * len(REGIMES_FULL)  # 12
EXPECTED_N_UNITS_SMOKE = len(SPARSITY_LEVELS_SMOKE) * len(REGIMES_SMOKE)  # 6

# Positive control (META_RULE_BC)
POSITIVE_CONTROL_PC = {
    "regime": "PC",
    "sparsity_frac": 0.10,
    "top1_band_lo": 0.30,
    "top1_band_hi": 0.90,
}
POSITIVE_CONTROL_WM = {
    "regime": "WM",
    "sparsity_frac": 0.10,
    "top1_band_lo": 0.20,
    "top1_band_hi": 0.80,
}

REQUIRED_FIELDS = ("verdict", "verdict_msg", "elapsed_s", "summary")


# ---------------------------------------------------------------------------
# CRLB / capacity-feasibility (META_RULE_AG)
# ---------------------------------------------------------------------------
def crlb_1step_cliff_prediction(N: int, M: int, sparsity_frac: float) -> float:
    """1-step cliff prediction adjusted for sparsity (effective N).

    Signal (1-2c) == sqrt(2 log M / N_eff) noise floor; cliff = 0.5 * (1 - noise).
    """
    if N <= 0 or M <= 1 or sparsity_frac <= 0:
        return 0.0
    N_eff = max(1.0, sparsity_frac * N)
    noise = math.sqrt(2.0 * math.log(M) / N_eff)
    return max(0.0, 0.5 * (1.0 - noise))


def capacity_ratio(N: int, M: int, sparsity_frac: float) -> float:
    """Capacity pressure ratio 2*M*log(M)/N_eff."""
    if N <= 0 or M <= 1 or sparsity_frac <= 0:
        return 0.0
    N_eff = max(1.0, sparsity_frac * N)
    return 2.0 * M * math.log(M) / N_eff


def get_backend_label() -> str:
    return "torch.cuda" if _CUDA_OK else "torch.cpu"


# ---------------------------------------------------------------------------
# HRR-real encoder + sparsity mask + corruption (fixed encoder family)
# ---------------------------------------------------------------------------
def _build_hrr_real_dense(M: int, N: int, seed: int) -> "torch.Tensor":
    """Dense Gaussian codebook (M, N) float32, L2-normalized on DEVICE."""
    g = np.random.default_rng(seed)
    arr = (g.standard_normal(size=(M, N)) / math.sqrt(N)).astype(np.float32)
    norms = np.linalg.norm(arr, axis=1, keepdims=True).clip(min=1e-12)
    arr = arr / norms
    return torch.from_numpy(arr).to(DEVICE)


def _apply_sparsity_mask_hrr(X: "torch.Tensor", density: float,
                                seed: int) -> Tuple["torch.Tensor", "torch.Tensor"]:
    """Zero (1-density) fraction of dims per row; renormalize; return (X_masked, mask)."""
    g = np.random.default_rng(seed + 42)
    M, N = X.shape
    n_keep = max(1, int(round(density * N)))
    mask_np = np.zeros((M, N), dtype=bool)
    for i in range(M):
        idx = g.choice(N, size=n_keep, replace=False)
        mask_np[i, idx] = True
    mask_t = torch.from_numpy(mask_np).to(DEVICE)
    X_masked = X * mask_t.to(X.dtype)
    norms = torch.linalg.norm(X_masked, dim=1, keepdim=True).clamp(min=1e-12)
    X_masked = X_masked / norms
    return X_masked, mask_t


def _corrupt_hrr_real(X: "torch.Tensor", c: float, seed: int) -> "torch.Tensor":
    """Add Gaussian noise to ACTIVE entries so E[cos(Q, X)] ~ 1-2c."""
    g = np.random.default_rng(seed)
    M, N = X.shape
    c_safe = min(c, 0.4999)
    target_cos = 1.0 - 2.0 * c_safe
    X_np = X.cpu().numpy()
    active_mask = X_np != 0
    Q = X.clone()
    for i in range(M):
        n_active = int(active_mask[i].sum())
        if n_active <= 0:
            continue
        sigma2 = (1.0 / (target_cos * target_cos) - 1.0) / max(n_active, 1)
        sigma = math.sqrt(max(sigma2, 0.0))
        noise = (g.standard_normal(size=n_active) * sigma).astype(np.float32)
        noise_t = torch.from_numpy(noise).to(DEVICE)
        active_idx = np.flatnonzero(active_mask[i])
        active_idx_t = torch.from_numpy(active_idx).to(DEVICE)
        Q[i, active_idx_t] = Q[i, active_idx_t] + noise_t
    norms = torch.linalg.norm(Q, dim=1, keepdim=True).clamp(min=1e-12)
    return Q / norms


def _random_floor_hrr(M: int, N: int, seed: int,
                        active_mask: "torch.Tensor") -> "torch.Tensor":
    g = np.random.default_rng(seed + 99991)
    arr = (g.standard_normal(size=(M, N)) / math.sqrt(N)).astype(np.float32)
    Q = torch.from_numpy(arr).to(DEVICE)
    Q = Q * active_mask.to(Q.dtype)
    norms = torch.linalg.norm(Q, dim=1, keepdim=True).clamp(min=1e-12)
    return Q / norms


def _sign_op_hrr(V: "torch.Tensor", active_mask: "torch.Tensor" = None) -> "torch.Tensor":
    if active_mask is not None:
        V = V * active_mask.to(V.dtype)
    norms = torch.linalg.norm(V, dim=1, keepdim=True).clamp(min=1e-12)
    return V / norms


def _score(Q: "torch.Tensor", X: "torch.Tensor") -> "torch.Tensor":
    return Q @ X.T


def _hopfield_cleanup(Q0: "torch.Tensor", X: "torch.Tensor", T: int, beta: float,
                        active_mask: "torch.Tensor") -> "torch.Tensor":
    Q = Q0
    for _ in range(max(0, T)):
        sims = _score(Q, X)
        p = torch.softmax(beta * sims, dim=1)
        Q_new = p @ X
        Q = _sign_op_hrr(Q_new, active_mask=active_mask)
    return Q


def _top1_recall(Q_final: "torch.Tensor", X: "torch.Tensor",
                    target_idx: "torch.Tensor") -> float:
    sims = _score(Q_final, X)
    preds = sims.argmax(dim=1)
    hits = int((preds == target_idx).sum().item())
    return hits / max(int(target_idx.shape[0]), 1)


# ---------------------------------------------------------------------------
# WM regime: multi-bank bind/unbind (Hadamard element-wise)
# ---------------------------------------------------------------------------
def _bind_hadamard(a: "torch.Tensor", b: "torch.Tensor") -> "torch.Tensor":
    return a * b


def _eval_pc_point(sparsity_frac: float, N: int, M: int, seed: int,
                    is_smoke: bool) -> Dict[str, Any]:
    """PC regime: single-bank pattern completion."""
    t0 = time.time()
    if _CUDA_OK:
        torch.cuda.empty_cache()
        torch.cuda.reset_peak_memory_stats()

    X_dense = _build_hrr_real_dense(M, N, seed)
    X, active_mask = _apply_sparsity_mask_hrr(X_dense, sparsity_frac, seed)
    del X_dense

    target_idx = torch.arange(M, device=DEVICE)
    sub_seed = seed * 1000 + int(CORRUPTION_PC * 1000) + int(sparsity_frac * 10000)

    # ARM_MECHANISM
    Q_sub_0 = _corrupt_hrr_real(X, CORRUPTION_PC, sub_seed)
    Q_sub_T = _hopfield_cleanup(Q_sub_0, X, T_PC, BETA, active_mask=active_mask)
    top1_sub = _top1_recall(Q_sub_T, X, target_idx)

    # ARM_RANDOM_FLOOR (fresh mask)
    g = np.random.default_rng(sub_seed + 88881)
    n_keep = max(1, int(round(sparsity_frac * N)))
    mask_np = np.zeros((M, N), dtype=bool)
    for i in range(M):
        idx = g.choice(N, size=n_keep, replace=False)
        mask_np[i, idx] = True
    q_rnd_mask = torch.from_numpy(mask_np).to(DEVICE)
    Q_rnd_0 = _random_floor_hrr(M, N, sub_seed, active_mask=q_rnd_mask)
    Q_rnd_T = _hopfield_cleanup(Q_rnd_0, X, T_PC, BETA, active_mask=q_rnd_mask)
    top1_rnd = _top1_recall(Q_rnd_T, X, target_idx)

    # Calibration
    cal_sample = min(20, M)
    Q_norm = torch.linalg.norm(Q_sub_0[:cal_sample], dim=1).clamp(min=1e-12)
    X_norm = torch.linalg.norm(X[:cal_sample], dim=1).clamp(min=1e-12)
    cal_dots = (Q_sub_0[:cal_sample] * X[:cal_sample]).sum(dim=1)
    cal_cos = float((cal_dots / (Q_norm * X_norm)).mean().item())

    peak_mem_mb = (torch.cuda.max_memory_allocated() / 1e6) if _CUDA_OK else -1.0
    elapsed = time.time() - t0
    discriminator = top1_sub - top1_rnd
    tier = _classify_tier(top1_sub, discriminator)

    del X, Q_sub_0, Q_sub_T, Q_rnd_0, Q_rnd_T, target_idx, active_mask
    if _CUDA_OK:
        torch.cuda.empty_cache()

    return {
        "regime": "PC",
        "sparsity_frac": sparsity_frac,
        "N": N,
        "M_or_K": M,
        "corruption_frac": CORRUPTION_PC,
        "cleanup_iters": T_PC,
        "seed": seed,
        "top1_mechanism": round(top1_sub, 4),
        "top1_random": round(top1_rnd, 4),
        "discriminator": round(discriminator, 4),
        "calibration_cos_q0_x": round(cal_cos, 4),
        "calibration_target_cos": round(1.0 - 2.0 * CORRUPTION_PC, 4),
        "verdict_tier_per_point": tier,
        "peak_mem_mb": round(peak_mem_mb, 1),
        "elapsed_per_point_s": round(elapsed, 3),
        "crlb_1step_cliff_prediction": round(
            crlb_1step_cliff_prediction(N, M, sparsity_frac), 4),
        "capacity_ratio": round(capacity_ratio(N, M, sparsity_frac), 3),
    }


def _eval_wm_point(sparsity_frac: float, N: int, K: int, B: int, seed: int,
                    is_smoke: bool) -> Dict[str, Any]:
    """WM regime: multi-bank Hadamard bind/unbind, bank-avg top1."""
    t0 = time.time()
    if _CUDA_OK:
        torch.cuda.empty_cache()
        torch.cuda.reset_peak_memory_stats()

    # Build B banks each with K keys + K values (sparsity applied to both)
    # then bank_b_traces[i] = bind(key_b[i], value_b[i]) summed over i
    # query: bind(key_b[i], corrupt(value_b[i])); readout = unbind(key_b[i], bank_trace);
    # top1 = argmax score against values_b
    per_bank_top1: List[float] = []
    per_bank_floor: List[float] = []
    per_bank_cal: List[float] = []

    for b in range(B):
        bank_seed = seed * 100003 + b
        keys_dense = _build_hrr_real_dense(K, N, bank_seed + 1)
        vals_dense = _build_hrr_real_dense(K, N, bank_seed + 2)
        keys, k_mask = _apply_sparsity_mask_hrr(keys_dense, sparsity_frac, bank_seed + 3)
        vals, v_mask = _apply_sparsity_mask_hrr(vals_dense, sparsity_frac, bank_seed + 4)
        del keys_dense, vals_dense

        # Bind + sum -> bank trace
        traces = _bind_hadamard(keys, vals)  # (K, N)
        bank_trace = traces.sum(dim=0, keepdim=True)  # (1, N)
        norm = torch.linalg.norm(bank_trace, dim=1, keepdim=True).clamp(min=1e-12)
        bank_trace = bank_trace / norm

        # Query: corrupt each value, bind with its key, unbind trace
        target_idx = torch.arange(K, device=DEVICE)
        sub_seed = bank_seed * 7 + int(sparsity_frac * 10000)
        vals_corr = _corrupt_hrr_real(vals, CORRUPTION_WM, sub_seed)

        # Unbind: for query at key i, readout ~= trace * key_i (Hadamard involutive
        # for binary; for HRR-real unbind = element-wise multiply by conjugate ~= key)
        # Here we use dot-product cleanup against vals codebook.
        # Readout query = key_i * bank_trace (element-wise); score against vals.
        readouts = keys * bank_trace  # (K, N) broadcast
        # Combined active mask = intersection of key mask + val mask
        combined_mask = k_mask & v_mask
        readouts_normed = _sign_op_hrr(readouts, active_mask=combined_mask)

        # Cleanup against vals
        cleaned = _hopfield_cleanup(readouts_normed, vals, T_WM, BETA,
                                        active_mask=v_mask)
        top1_bank = _top1_recall(cleaned, vals, target_idx)
        per_bank_top1.append(top1_bank)

        # Random floor arm
        g = np.random.default_rng(sub_seed + 88881)
        n_keep = max(1, int(round(sparsity_frac * N)))
        mask_np = np.zeros((K, N), dtype=bool)
        for i in range(K):
            idx = g.choice(N, size=n_keep, replace=False)
            mask_np[i, idx] = True
        q_rnd_mask = torch.from_numpy(mask_np).to(DEVICE)
        Q_rnd = _random_floor_hrr(K, N, sub_seed, active_mask=q_rnd_mask)
        Q_rnd_T = _hopfield_cleanup(Q_rnd, vals, T_WM, BETA, active_mask=q_rnd_mask)
        top1_floor = _top1_recall(Q_rnd_T, vals, target_idx)
        per_bank_floor.append(top1_floor)

        # Calibration on corrupted vals
        cal_sample = min(20, K)
        Qn = torch.linalg.norm(vals_corr[:cal_sample], dim=1).clamp(min=1e-12)
        Xn = torch.linalg.norm(vals[:cal_sample], dim=1).clamp(min=1e-12)
        cd = (vals_corr[:cal_sample] * vals[:cal_sample]).sum(dim=1)
        per_bank_cal.append(float((cd / (Qn * Xn)).mean().item()))

        del keys, vals, k_mask, v_mask, traces, bank_trace, vals_corr, readouts
        del readouts_normed, cleaned, Q_rnd, Q_rnd_T, q_rnd_mask, combined_mask
        if _CUDA_OK:
            torch.cuda.empty_cache()

    top1_sub = float(np.mean(per_bank_top1))
    top1_rnd = float(np.mean(per_bank_floor))
    cal_cos = float(np.mean(per_bank_cal))
    per_bank_cv = (float(np.std(per_bank_top1) / max(top1_sub, 1e-9))
                    if len(per_bank_top1) > 1 else 0.0)

    peak_mem_mb = (torch.cuda.max_memory_allocated() / 1e6) if _CUDA_OK else -1.0
    elapsed = time.time() - t0
    discriminator = top1_sub - top1_rnd
    tier = _classify_tier(top1_sub, discriminator)

    return {
        "regime": "WM",
        "sparsity_frac": sparsity_frac,
        "N": N,
        "M_or_K": K,
        "B_banks": B,
        "corruption_frac": CORRUPTION_WM,
        "cleanup_iters": T_WM,
        "seed": seed,
        "top1_mechanism": round(top1_sub, 4),
        "top1_random": round(top1_rnd, 4),
        "discriminator": round(discriminator, 4),
        "calibration_cos_q0_x": round(cal_cos, 4),
        "calibration_target_cos": round(1.0 - 2.0 * CORRUPTION_WM, 4),
        "verdict_tier_per_point": tier,
        "per_bank_cv": round(per_bank_cv, 4),
        "peak_mem_mb": round(peak_mem_mb, 1),
        "elapsed_per_point_s": round(elapsed, 3),
        "crlb_1step_cliff_prediction": round(
            crlb_1step_cliff_prediction(N, K, sparsity_frac), 4),
        "capacity_ratio": round(capacity_ratio(N, K, sparsity_frac), 3),
    }


def _classify_tier(top1: float, disc: float) -> str:
    if top1 >= SATURATED_TOP1:
        return "SATURATED"
    if top1 >= HARD_PASS_LO and disc >= HP_DISCRIMINATOR:
        return "HARD_PASS"
    if top1 >= MIDDLE_BAND_LO and disc >= MB_DISCRIMINATOR:
        return "MIDDLE_BAND"
    if top1 <= FLOOR_TOP1:
        return "FLOOR"
    return "HARD_FAIL"


# ---------------------------------------------------------------------------
# Per-seed sweep
# ---------------------------------------------------------------------------
def run_one_seed_phase_diagram(seed: int, run_mode: str) -> Dict[str, Any]:
    """Sweep (regime, alpha) points. Halt on first exception (META_RULE_J)."""
    is_smoke = (run_mode == "smoke")
    sparsity_sweep = SPARSITY_LEVELS_SMOKE if is_smoke else SPARSITY_LEVELS_FULL
    regimes = REGIMES_SMOKE if is_smoke else REGIMES_FULL
    M_pc = M_PC_SMOKE if is_smoke else M_PC_FULL
    K_wm = K_WM_SMOKE if is_smoke else K_WM_FULL

    expected_n_units = len(sparsity_sweep) * len(regimes)
    N_dim = N_DIM_FULL

    print(f"[run_one_seed] seed={seed} mode={run_mode} device={DEVICE} "
            f"regimes={regimes} sparsity={list(sparsity_sweep)} "
            f"N={N_dim} M_pc={M_pc} K_wm={K_wm} B_wm={B_WM} "
            f"expected_n={expected_n_units}", flush=True)

    per_point_rows: List[Dict[str, Any]] = []
    for regime in regimes:
        for alpha in sparsity_sweep:
            print(f"  [point] regime={regime} alpha={alpha}", flush=True)
            if regime == "PC":
                row = _eval_pc_point(alpha, N_dim, M_pc, seed, is_smoke)
            elif regime == "WM":
                row = _eval_wm_point(alpha, N_dim, K_wm, B_WM, seed, is_smoke)
            else:
                raise ValueError(f"unknown regime={regime!r}")
            per_point_rows.append(row)
            print(f"    -> top1_mech={row['top1_mechanism']:.4f} "
                    f"top1_rnd={row['top1_random']:.4f} "
                    f"tier={row['verdict_tier_per_point']}", flush=True)

    observed_n = len(per_point_rows)
    return {
        "seed": seed,
        "run_mode": run_mode,
        "per_point_rows": per_point_rows,
        "observed_n_units": observed_n,
        "expected_n_units": expected_n_units,
        "cardinality_ok": (observed_n == expected_n_units),
    }


# ---------------------------------------------------------------------------
# Aggregate + verdict
# ---------------------------------------------------------------------------
def aggregate_and_verdict(per_seed: Dict[int, Dict[str, Any]],
                            run_mode: str) -> Dict[str, Any]:
    """Aggregate across seeds; compute HP/MB/HF verdict per pre-reg."""
    is_smoke = (run_mode == "smoke")
    sparsity_sweep = SPARSITY_LEVELS_SMOKE if is_smoke else SPARSITY_LEVELS_FULL
    regimes = REGIMES_SMOKE if is_smoke else REGIMES_FULL

    # Aggregate per (regime, alpha): mean top1_mech, mean top1_rnd, seed cv
    keyed: Dict[Tuple[str, float], List[float]] = {}
    keyed_rnd: Dict[Tuple[str, float], List[float]] = {}
    tier_per_key: Dict[Tuple[str, float], List[str]] = {}
    all_cardinality_ok = True

    for seed, sd in per_seed.items():
        if not sd.get("cardinality_ok", False):
            all_cardinality_ok = False
        for row in sd.get("per_point_rows", []):
            k = (row["regime"], row["sparsity_frac"])
            keyed.setdefault(k, []).append(row["top1_mechanism"])
            keyed_rnd.setdefault(k, []).append(row["top1_random"])
            tier_per_key.setdefault(k, []).append(row["verdict_tier_per_point"])

    agg_rows: List[Dict[str, Any]] = []
    for regime in regimes:
        for alpha in sparsity_sweep:
            k = (regime, alpha)
            vals = keyed.get(k, [])
            vals_rnd = keyed_rnd.get(k, [])
            if not vals:
                continue
            m = float(np.mean(vals))
            s = float(np.std(vals))
            cv = s / max(abs(m), 1e-9)
            m_rnd = float(np.mean(vals_rnd)) if vals_rnd else 0.0
            agg_rows.append({
                "regime": regime,
                "sparsity_frac": alpha,
                "top1_mechanism_mean": round(m, 4),
                "top1_mechanism_std": round(s, 4),
                "seed_cv": round(cv, 4),
                "top1_random_mean": round(m_rnd, 4),
                "discriminator_mean": round(m - m_rnd, 4),
                "per_seed_top1": [round(v, 4) for v in vals],
                "per_seed_tier": tier_per_key.get(k, []),
                "n_seeds_at_point": len(vals),
            })

    # Per-regime sparsity range + monotonicity (Spearman rho by rank)
    per_regime_summary: Dict[str, Dict[str, Any]] = {}
    for regime in regimes:
        rows = [r for r in agg_rows if r["regime"] == regime]
        rows.sort(key=lambda r: r["sparsity_frac"])
        if not rows:
            continue
        top1_by_alpha = [r["top1_mechanism_mean"] for r in rows]
        alphas = [r["sparsity_frac"] for r in rows]
        range_val = max(top1_by_alpha) - min(top1_by_alpha)
        # Spearman rho against alpha rank
        rho = _spearman(alphas, top1_by_alpha) if len(rows) >= 3 else 0.0
        seed_cvs = [r["seed_cv"] for r in rows]
        max_cv = max(seed_cvs) if seed_cvs else 0.0
        per_regime_summary[regime] = {
            "sparsity_range": round(range_val, 4),
            "spearman_rho_top1_vs_alpha": round(rho, 4),
            "max_seed_cv": round(max_cv, 4),
            "alphas_swept": list(alphas),
            "top1_by_alpha": [round(v, 4) for v in top1_by_alpha],
        }

    # Positive control check
    pc_target = POSITIVE_CONTROL_PC
    pc_row = next((r for r in agg_rows
                    if r["regime"] == "PC" and abs(r["sparsity_frac"] - pc_target["sparsity_frac"]) < 1e-6),
                    None)
    pc_ok = (pc_row is not None and
                pc_target["top1_band_lo"] <= pc_row["top1_mechanism_mean"] <= pc_target["top1_band_hi"])

    wm_ok = True
    if "WM" in regimes:
        wm_target = POSITIVE_CONTROL_WM
        wm_row = next((r for r in agg_rows
                        if r["regime"] == "WM" and abs(r["sparsity_frac"] - wm_target["sparsity_frac"]) < 1e-6),
                        None)
        wm_ok = (wm_row is not None and
                    wm_target["top1_band_lo"] <= wm_row["top1_mechanism_mean"] <= wm_target["top1_band_hi"])

    # HP band evaluation
    range_ok = any(v["sparsity_range"] >= 0.10 for v in per_regime_summary.values())
    mono_ok = any(abs(v["spearman_rho_top1_vs_alpha"]) >= 0.80
                    for v in per_regime_summary.values())
    cv_ok = all(v["max_seed_cv"] <= 0.10 for v in per_regime_summary.values())

    # Arms differ (mechanism_hash distinct at smoke gate)
    arms_differ = all(
        abs(r["top1_mechanism_mean"] - r["top1_random_mean"]) >= 0.02
        for r in agg_rows)

    if not all_cardinality_ok:
        verdict = "HARD_FAIL"
        verdict_msg = f"HARD_FAIL_CARDINALITY_BREACH: per-seed cardinality != {EXPECTED_N_UNITS_FULL if not is_smoke else EXPECTED_N_UNITS_SMOKE}"
    elif not pc_ok:
        verdict = "HARD_FAIL"
        verdict_msg = f"HARD_FAIL_POSITIVE_CONTROL_PC: pc_row={pc_row}"
    elif not wm_ok:
        verdict = "HARD_FAIL"
        verdict_msg = "HARD_FAIL_POSITIVE_CONTROL_WM"
    elif not arms_differ:
        verdict = "HARD_FAIL"
        verdict_msg = "HARD_FAIL_ARMS_IDENTICAL"
    elif range_ok and mono_ok and cv_ok:
        verdict = "HARD_PASS"
        verdict_msg = (f"HARD_PASS: sparsity as free axis lever confirmed. "
                        f"per_regime_summary={per_regime_summary}")
    elif range_ok or mono_ok:
        verdict = "MIDDLE_BAND"
        verdict_msg = (f"MIDDLE_BAND: partial (range_ok={range_ok} mono_ok={mono_ok} cv_ok={cv_ok}). "
                        f"per_regime_summary={per_regime_summary}")
    else:
        verdict = "MIDDLE_BAND"
        verdict_msg = f"MIDDLE_BAND: sparsity flat, weak lever. per_regime_summary={per_regime_summary}"

    return {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict_msg,
        "per_regime_summary": per_regime_summary,
        "agg_rows": agg_rows,
        "per_seed": {str(k): {"observed_n_units": v.get("observed_n_units"),
                                "cardinality_ok": v.get("cardinality_ok")}
                        for k, v in per_seed.items()},
        "expected_n_units": (EXPECTED_N_UNITS_SMOKE if is_smoke
                                else EXPECTED_N_UNITS_FULL),
        "observed_n_units": sum(v.get("observed_n_units", 0) for v in per_seed.values()),
        "cardinality_ok": all_cardinality_ok,
        "positive_control_pc_ok": pc_ok,
        "positive_control_wm_ok": wm_ok,
        "arms_differ_verified": arms_differ,
        "hp_range_ok": range_ok,
        "hp_monotonicity_ok": mono_ok,
        "hp_cv_ok": cv_ok,
        "REQUIRED_FIELDS_check": list(REQUIRED_FIELDS),
    }


def _spearman(x: List[float], y: List[float]) -> float:
    """Simple Spearman rho via rank; assumes no ties (alpha grid strictly increasing)."""
    if len(x) != len(y) or len(x) < 2:
        return 0.0
    rx = _rank(x)
    ry = _rank(y)
    n = len(x)
    d2 = sum((rx[i] - ry[i]) ** 2 for i in range(n))
    return 1.0 - (6.0 * d2) / (n * (n * n - 1))


def _rank(a: List[float]) -> List[float]:
    sorted_idx = sorted(range(len(a)), key=lambda i: a[i])
    ranks = [0.0] * len(a)
    for r, i in enumerate(sorted_idx):
        ranks[i] = float(r + 1)
    return ranks


# ---------------------------------------------------------------------------
# Selftest (META_RULE_AG + AC + calibration)
# ---------------------------------------------------------------------------
def selftest(seed: int) -> Tuple[bool, str]:
    msgs: List[str] = []

    # 1. Cardinality math
    if EXPECTED_N_UNITS_FULL != 12:
        return False, f"FULL cardinality {EXPECTED_N_UNITS_FULL} != 12"
    if EXPECTED_N_UNITS_SMOKE != 6:
        return False, f"SMOKE cardinality {EXPECTED_N_UNITS_SMOKE} != 6"
    msgs.append(f"cardinality FULL={EXPECTED_N_UNITS_FULL} SMOKE={EXPECTED_N_UNITS_SMOKE}")

    # 2. CRLB formula sanity: PC alpha=0.005 predicted FLOOR, alpha=0.20 predicted HP
    c_pc_low = crlb_1step_cliff_prediction(8192, 100, 0.005)
    c_pc_hi = crlb_1step_cliff_prediction(8192, 100, 0.20)
    if not (c_pc_low < c_pc_hi):
        return False, f"CRLB monotonicity fail: low={c_pc_low} hi={c_pc_hi}"
    if not (c_pc_low < CORRUPTION_PC):
        return False, f"CRLB@alpha=0.005 should be below c=0.485 (predicted FLOOR): {c_pc_low}"
    if not (c_pc_hi >= 0.40):
        return False, f"CRLB@alpha=0.20 should be ~0.48 (near HP): {c_pc_hi}"
    msgs.append(f"CRLB PC low={c_pc_low:.4f} hi={c_pc_hi:.4f}")

    # 3. Encoder + sparsity mask codebook distinctness across 6 alpha
    M_san = 20
    N_san = 512
    hashes = {}
    for density in SPARSITY_LEVELS_FULL:
        X_dense = _build_hrr_real_dense(M_san, N_san, seed)
        X, mask = _apply_sparsity_mask_hrr(X_dense, density, seed)
        h = hashlib.sha256(X.cpu().numpy().tobytes()).hexdigest()[:16]
        hashes[f"hrr_real@s={density}"] = h
        del X_dense, X, mask
        if _CUDA_OK:
            torch.cuda.empty_cache()
    if len(set(hashes.values())) != len(hashes):
        return False, f"codebooks NOT distinct at seed={seed}: {hashes}"
    msgs.append(f"6 hrr_real x sparsity codebooks distinct at seed={seed}")

    # 4. Calibration: PC c=0.30 cos ~ 0.40 (tol 0.15)
    M_cal = 30
    N_cal = 2048
    X_dense = _build_hrr_real_dense(M_cal, N_cal, seed)
    X, _ = _apply_sparsity_mask_hrr(X_dense, 0.20, seed)
    Q = _corrupt_hrr_real(X, 0.30, seed * 7)
    Qn = torch.linalg.norm(Q, dim=1).clamp(min=1e-12)
    Xn = torch.linalg.norm(X, dim=1).clamp(min=1e-12)
    cos_per = (Q * X).sum(dim=1) / (Qn * Xn)
    cos_mean = float(cos_per.mean().item())
    target = 1.0 - 2.0 * 0.30  # 0.40
    if abs(cos_mean - target) > 0.15:
        return False, f"calibration FAIL c=0.30 alpha=0.20: cos={cos_mean:.4f} target={target:.4f}"
    msgs.append(f"calibration hrr_real c=0.30 alpha=0.20: cos={cos_mean:.4f} (target={target:.4f})")
    del X_dense, X, Q

    # 5. Mechanism sanity: hrr_real dense (alpha=1.0) c=0.10 recovers >= 15/20
    X_dense = _build_hrr_real_dense(20, 512, seed)
    X, mask = _apply_sparsity_mask_hrr(X_dense, 1.0, seed)
    Q0 = _corrupt_hrr_real(X, 0.10, seed * 3)
    Q1 = _hopfield_cleanup(Q0, X, 1, BETA, active_mask=mask)
    sims = _score(Q1, X)
    preds = sims.argmax(dim=1)
    target_idx = torch.arange(20, device=DEVICE)
    n_hit = int((preds == target_idx).sum().item())
    if n_hit < 15:
        return False, f"mechanism sanity FAIL hrr_real dense c=0.10: {n_hit}/20"
    msgs.append(f"mechanism sanity ok: hrr_real dense c=0.10 recovered {n_hit}/20")

    return True, "; ".join(msgs)
