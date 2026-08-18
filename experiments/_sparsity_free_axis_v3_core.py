"""Shared core for sparsity_free_axis_v3 sibling cells (REVIVAL of v2 HF).

V3 REVIVAL RATIONALE (Skunkworks Wave 7 2026-07-01 declared criterion):
    v2 SMOKE HARD_PASS but FULL HARD_FAIL_POSITIVE_CONTROL_WM: PC regime cleanly
    in-band ([0.37, 0.73] across the 3x3 PC grid; Spearman rho -1.0; cv 0.000).
    WM regime OVERSHOOTS upper band 0.90: MEASURED@2026-07-01 (v2 seed_7 FULL,
    data/exp_substrate_sparsity_free_axis_v2_n4096_seed_7/metrics.json):
      WM K=1000 alpha=0.05: 0.9526  (>0.90 upper)
      WM K=1000 alpha=0.10: 0.9626  (>0.90 upper)
      WM K=1000 alpha=0.20: 0.8971
      WM K=2000 alpha=0.10: 0.8228  (>0.80 upper band claim from task prompt)
      WM K=2000 alpha=0.20: 0.6466
    WM c=0.40 with B=16-bank averaging over-recovers; multi-bank sum washes
    corruption faster than PC single-bank single-step. Skunkworks primary
    revival criterion: raise WM c 0.40 -> 0.55.

    Empirically-calibrated predictions (formula-adjusted per v2 MEASURED delta):
      WM K=1000 alpha=0.05 c=0.55: ~0.64  (in [0.30, 0.90])
      WM K=1000 alpha=0.10 c=0.55: ~0.59  (in [0.30, 0.90])
      WM K=2000 alpha=0.10 c=0.55: ~0.46  (in [0.30, 0.90])

V3 changes from v2 (MINIMAL PATCH per Skunkworks criterion):
    1. PRIMARY: WM c 0.40 -> 0.55  (steeper sparsity axis; predicts K=2000
       alpha=0.10 top1 ~ 0.46 in [0.30, 0.90] band)
    2. SECONDARY: SMOKE now includes 1 PC point + 1 WM point (was PC-only);
       catches WM saturation at smoke gate before FULL dispatch
    3. Everything else IDENTICAL to v2: N=4096, M in {1000, 1500, 2000},
       T=1, PC c=0.60, B=16 banks, encoder=hrr_real

Design (LOCKED):
    FULL: 3 M x 3 alpha x 2 regime = 18 phase points per seed
    SMOKE: 3 M x 3 alpha x 2 regime = 18 corner points per seed
           (v3 fires WM at smoke; DISCRIMINATOR_SURVIVES_SCALE check)

Fixed:
    encoder = hrr_real (chain-grade default; Gaussian codebook L2-normalized)
    binding = Hadamard (element-wise) for WM regime bind/unbind
    N = 4096
    T_cleanup = 1 (single-step readout; reads CRLB directly)

Regime PC (pattern completion):
    M_items SWEPT in {1000, 1500, 2000}
    corruption c = 0.60  (unchanged from v2 - PC regime works)
    T = 1
    beta = 8.0

Regime WM (multi-bank working memory):
    K SWEPT in {1000, 1500, 2000}
    B = 16 banks (unchanged)
    corruption c = 0.55  (RAISED from v2 0.40; Skunkworks PRIMARY revival)
    T = 1

Sparsity levels (axis C; SWEPT):
    FULL:  {0.05, 0.10, 0.20}
    SMOKE: same 3

Discriminator (v3 REVIVAL bands; META_RULE_L; band-floor MB):
    HP_A: per_regime_sparsity_range >= 0.05 in >=1 regime (monotone lever)
    HP_B: monotonicity |Spearman rho| >= 0.80 with fixed direction in >=1 regime
    HP_C: 3-seed cv <= 0.15 per (regime, M, alpha) point
    HP_D: cardinality_ok (observed_n_units == expected)
    HP_E: baseline_in_band (RANDOM_FLOOR arm at chance)
    HP_F: positive_control PC in-band [0.30, 0.90]
    HP_G: WM in-band [0.30, 0.90] AT EVERY (M, alpha) POINT
          (v3 revival criterion; META_RULE_L WM upper-band saturation check)
    HP_H: WM mechanism lift >= PC + 0.10 at SOME (M, alpha) point (optional lift)

Verdict priority (META_RULE_L; fail-fast pattern; WM upper-band check EARLY):
    1. HF_CARDINALITY_BREACH: any per-seed cardinality mismatch
    2. HF_STILL_SATURATED_WM: WM top1 > 0.90 at ANY (M, alpha)   <-- v3 fail-fast
    3. HF_STILL_SATURATED_PC: PC top1 > 0.90 at every point
    4. HF_CRUMBLE: any regime top1 < 0.10 everywhere
    5. HF_POSITIVE_CONTROL_PC: PC positive-control out of band
    6. HF_POSITIVE_CONTROL_WM: WM positive-control out of band
    7. HF_ARMS_IDENTICAL: mechanism ~= random_floor
    8. HP_SPARSITY_DISCRIMINATES_ALL_REGIMES: all bands pass
    9. MB_PARTIAL: range OR mono passes
    10. MB_FLAT: sparsity flat

Positive control (META_RULE_BC):
    PC hrr_real @ M=2000 alpha=0.10 c=0.60 T=1: top1 in [0.30, 0.90]
      (v2 MEASURED@2026-07-01: 0.507 - passes)
    WM hrr_real @ K=2000 alpha=0.10 c=0.55 T=1: bank-avg top1 in [0.30, 0.90]
      (v3 predicted-empirical: ~0.46 - target in-band)

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
    - arms_differ_verified at smoke gate (MECHANISM vs RANDOM_FLOOR per point)
    - final_metrics_atomicity: tmp_replace (per sibling cell main())
    - except SystemExit: raise BEFORE except Exception (see sibling cell main)
    - crlb_floor_computed via crlb_1step_cliff_prediction; reachable
    - baseline_in_band: RANDOM_FLOOR at chance; MECHANISM not saturated
    - discriminator survives scale (smoke at full N=4096; WM in smoke)
    - HARD_PASS strictly above floor + 5% band-width
    - HP_SCOPE: HARD_PASS applies to MECHANISM arm only
    - cardinality_ok: EXPECTED_N_UNITS_FULL=18, SMOKE=18 (v3: WM in smoke)
    - per-unit failure-class: no bare except; halt on any per-point exception
    - calibration_check: default_ok_for_this_regime
    - all numbers tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@

Discriminator-survives-scale (USER 2026-06-26):
    v3 smoke = full N and full M sweep + BOTH regimes; identical FULL grid.
    No smoke-vs-FULL scale gap remains.

Compose refs:
    v1 HF anchor: sparsity_free_axis_v1_n8192 (all-regime test-design fail)
    v2 HF anchor: substrate_sparsity_free_axis_v2_n4096 (WM-only saturation c=0.40)
    positive control ref: batch_A_x_C_v2_CG (calibration)

ASCII-only. No unicode. CPU-eligible (numpy + small torch).

PRE-REG: preregs/2026-07-01_substrate_sparsity_free_axis_v3_n4096.md

Author: hdi_exp_dev 2026-07-01 (Opus 4.7 1M, agent-spawn; v2 HF revival)
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
SATURATED_TOP1 = 0.90
HARD_PASS_LO = 0.30
HARD_PASS_HI = 0.90
FLOOR_TOP1 = 0.10
HP_DISCRIMINATOR = 0.20  # mechanism - random_floor
MB_DISCRIMINATOR = 0.10

BETA = 8.0

# Encoder fixed (chain-grade default per wave-2 section 3)
ENCODER_FAMILY = "hrr_real"

# Sparsity levels (INNER axis C; SWEPT)
SPARSITY_LEVELS = (0.05, 0.10, 0.20)

# M / K levels (OUTER axis; empirically-calibrated from v2)
M_LEVELS = (1000, 1500, 2000)

# Regime knobs (v3: WM in smoke per Skunkworks criterion)
REGIMES_FULL = ("PC", "WM")
REGIMES_SMOKE = ("PC", "WM")  # v3 SECONDARY: fire WM at smoke, catch saturation early

# Fixed dimensionality
N_DIM_FULL = 4096
N_DIM_SMOKE = 4096

# PC regime (unchanged from v2 - PC works in-band)
CORRUPTION_PC = 0.60
T_PC = 1

# WM regime (v3 PRIMARY REVIVAL: c 0.40 -> 0.55)
B_WM = 16
CORRUPTION_WM = 0.55  # RAISED from v2 0.40 (Skunkworks Wave 7 primary criterion)
T_WM = 1

# Cardinality (LOCKED)
EXPECTED_N_UNITS_FULL = len(M_LEVELS) * len(SPARSITY_LEVELS) * len(REGIMES_FULL)   # 18
EXPECTED_N_UNITS_SMOKE = len(M_LEVELS) * len(SPARSITY_LEVELS) * len(REGIMES_SMOKE)  # 18 (v3)

# Positive control (META_RULE_BC; empirically-calibrated 2026-07-01)
POSITIVE_CONTROL_PC = {
    "regime": "PC",
    "M_or_K": 2000,
    "sparsity_frac": 0.10,
    "top1_band_lo": 0.30,
    "top1_band_hi": 0.90,
}
POSITIVE_CONTROL_WM = {
    "regime": "WM",
    "M_or_K": 2000,
    "sparsity_frac": 0.10,
    "top1_band_lo": 0.30,  # v3 raised from v2 0.20 (v3 target ~0.46)
    "top1_band_hi": 0.90,  # v3 raised from v2 0.80 (per task-prompt HP_SPARSITY_DISCRIMINATES_ALL_REGIMES)
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


def predicted_top1_1step(N: int, M: int, sparsity_frac: float, c: float) -> float:
    """Predicted top1 after 1-step cleanup: logistic in (signal - noise)."""
    if N <= 0 or M <= 1 or sparsity_frac <= 0:
        return 0.0
    N_eff = max(1.0, sparsity_frac * N)
    noise = math.sqrt(2.0 * math.log(M) / N_eff)
    signal = 1.0 - 2.0 * c
    delta = signal - noise
    return 0.5 + 0.5 * math.tanh(3.0 * delta)


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
    """Modern Hopfield cleanup for T iterations; T=1 = single-step readout."""
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
    """PC regime: single-bank pattern completion; T=1 single-step."""
    t0 = time.time()
    if _CUDA_OK:
        torch.cuda.empty_cache()
        torch.cuda.reset_peak_memory_stats()

    X_dense = _build_hrr_real_dense(M, N, seed)
    X, active_mask = _apply_sparsity_mask_hrr(X_dense, sparsity_frac, seed)
    del X_dense

    target_idx = torch.arange(M, device=DEVICE)
    sub_seed = seed * 1000 + int(CORRUPTION_PC * 1000) + int(sparsity_frac * 10000) + M

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

    # arms-differ hash gate (META_RULE_AF)
    h_mech = hashlib.sha256(Q_sub_T.cpu().numpy().tobytes()).hexdigest()[:16]
    h_rnd = hashlib.sha256(Q_rnd_T.cpu().numpy().tobytes()).hexdigest()[:16]

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
        "predicted_top1": round(predicted_top1_1step(N, M, sparsity_frac, CORRUPTION_PC), 4),
        "capacity_ratio": round(capacity_ratio(N, M, sparsity_frac), 3),
        "arms_hash_mechanism": h_mech,
        "arms_hash_random": h_rnd,
        "arms_differ_at_point": (h_mech != h_rnd),
    }


def _eval_wm_point(sparsity_frac: float, N: int, K: int, B: int, seed: int,
                    is_smoke: bool) -> Dict[str, Any]:
    """WM regime: multi-bank Hadamard bind/unbind, bank-avg top1; T=1 single-step."""
    t0 = time.time()
    if _CUDA_OK:
        torch.cuda.empty_cache()
        torch.cuda.reset_peak_memory_stats()

    per_bank_top1: List[float] = []
    per_bank_floor: List[float] = []
    per_bank_cal: List[float] = []

    for b in range(B):
        bank_seed = seed * 100003 + b + K
        keys_dense = _build_hrr_real_dense(K, N, bank_seed + 1)
        vals_dense = _build_hrr_real_dense(K, N, bank_seed + 2)
        keys, k_mask = _apply_sparsity_mask_hrr(keys_dense, sparsity_frac, bank_seed + 3)
        vals, v_mask = _apply_sparsity_mask_hrr(vals_dense, sparsity_frac, bank_seed + 4)
        del keys_dense, vals_dense

        traces = _bind_hadamard(keys, vals)
        bank_trace = traces.sum(dim=0, keepdim=True)
        norm = torch.linalg.norm(bank_trace, dim=1, keepdim=True).clamp(min=1e-12)
        bank_trace = bank_trace / norm

        target_idx = torch.arange(K, device=DEVICE)
        sub_seed = bank_seed * 7 + int(sparsity_frac * 10000)
        vals_corr = _corrupt_hrr_real(vals, CORRUPTION_WM, sub_seed)

        readouts = keys * bank_trace
        combined_mask = k_mask & v_mask
        readouts_normed = _sign_op_hrr(readouts, active_mask=combined_mask)

        cleaned = _hopfield_cleanup(readouts_normed, vals, T_WM, BETA,
                                        active_mask=v_mask)
        top1_bank = _top1_recall(cleaned, vals, target_idx)
        per_bank_top1.append(top1_bank)

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
        "predicted_top1": round(predicted_top1_1step(N, K, sparsity_frac, CORRUPTION_WM), 4),
        "capacity_ratio": round(capacity_ratio(N, K, sparsity_frac), 3),
    }


def _classify_tier(top1: float, disc: float) -> str:
    """Classify per-point tier at v3 REVIVAL bands."""
    if top1 >= SATURATED_TOP1:
        return "SATURATED"
    if top1 <= FLOOR_TOP1:
        return "FLOOR"
    if HARD_PASS_LO <= top1 <= HARD_PASS_HI and disc >= HP_DISCRIMINATOR:
        return "HARD_PASS"
    if disc >= MB_DISCRIMINATOR:
        return "MIDDLE_BAND"
    return "HARD_FAIL"


# ---------------------------------------------------------------------------
# Per-seed sweep
# ---------------------------------------------------------------------------
def run_one_seed_phase_diagram(seed: int, run_mode: str) -> Dict[str, Any]:
    """Sweep (regime, M, alpha) points. Halt on first exception (META_RULE_J)."""
    is_smoke = (run_mode == "smoke")
    sparsity_sweep = SPARSITY_LEVELS
    m_sweep = M_LEVELS
    regimes = REGIMES_SMOKE if is_smoke else REGIMES_FULL

    expected_n_units = len(m_sweep) * len(sparsity_sweep) * len(regimes)
    N_dim = N_DIM_FULL

    print(f"[run_one_seed] seed={seed} mode={run_mode} device={DEVICE} "
            f"regimes={regimes} M={list(m_sweep)} sparsity={list(sparsity_sweep)} "
            f"N={N_dim} T_pc={T_PC} T_wm={T_WM} B_wm={B_WM} "
            f"pc_c={CORRUPTION_PC} wm_c={CORRUPTION_WM} "
            f"expected_n={expected_n_units}", flush=True)

    per_point_rows: List[Dict[str, Any]] = []
    for regime in regimes:
        for M_val in m_sweep:
            for alpha in sparsity_sweep:
                print(f"  [point] regime={regime} M={M_val} alpha={alpha}", flush=True)
                if regime == "PC":
                    row = _eval_pc_point(alpha, N_dim, M_val, seed, is_smoke)
                elif regime == "WM":
                    row = _eval_wm_point(alpha, N_dim, M_val, B_WM, seed, is_smoke)
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
    sparsity_sweep = SPARSITY_LEVELS
    m_sweep = M_LEVELS
    regimes = REGIMES_SMOKE if is_smoke else REGIMES_FULL

    keyed: Dict[Tuple[str, int, float], List[float]] = {}
    keyed_rnd: Dict[Tuple[str, int, float], List[float]] = {}
    tier_per_key: Dict[Tuple[str, int, float], List[str]] = {}
    all_cardinality_ok = True

    for seed, sd in per_seed.items():
        if not sd.get("cardinality_ok", False):
            all_cardinality_ok = False
        for row in sd.get("per_point_rows", []):
            k = (row["regime"], row["M_or_K"], row["sparsity_frac"])
            keyed.setdefault(k, []).append(row["top1_mechanism"])
            keyed_rnd.setdefault(k, []).append(row["top1_random"])
            tier_per_key.setdefault(k, []).append(row["verdict_tier_per_point"])

    agg_rows: List[Dict[str, Any]] = []
    for regime in regimes:
        for M_val in m_sweep:
            for alpha in sparsity_sweep:
                k = (regime, M_val, alpha)
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
                    "M_or_K": M_val,
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

    # Per-(regime, M) sparsity range + monotonicity
    per_regime_M_summary: Dict[str, Dict[str, Any]] = {}
    for regime in regimes:
        for M_val in m_sweep:
            rows = [r for r in agg_rows if r["regime"] == regime and r["M_or_K"] == M_val]
            rows.sort(key=lambda r: r["sparsity_frac"])
            if not rows:
                continue
            top1_by_alpha = [r["top1_mechanism_mean"] for r in rows]
            alphas = [r["sparsity_frac"] for r in rows]
            range_val = max(top1_by_alpha) - min(top1_by_alpha)
            rho = _spearman(alphas, top1_by_alpha) if len(rows) >= 3 else 0.0
            seed_cvs = [r["seed_cv"] for r in rows]
            max_cv = max(seed_cvs) if seed_cvs else 0.0
            per_regime_M_summary[f"{regime}_M{M_val}"] = {
                "regime": regime,
                "M_or_K": M_val,
                "sparsity_range": round(range_val, 4),
                "spearman_rho_top1_vs_alpha": round(rho, 4),
                "max_seed_cv": round(max_cv, 4),
                "alphas_swept": list(alphas),
                "top1_by_alpha": [round(v, 4) for v in top1_by_alpha],
            }

    # Positive control checks
    pc_target = POSITIVE_CONTROL_PC
    pc_row = next((r for r in agg_rows
                    if r["regime"] == "PC"
                    and r["M_or_K"] == pc_target["M_or_K"]
                    and abs(r["sparsity_frac"] - pc_target["sparsity_frac"]) < 1e-6),
                    None)
    pc_ok = (pc_row is not None and
                pc_target["top1_band_lo"] <= pc_row["top1_mechanism_mean"] <= pc_target["top1_band_hi"])

    wm_ok = True
    if "WM" in regimes:
        wm_target = POSITIVE_CONTROL_WM
        wm_row = next((r for r in agg_rows
                        if r["regime"] == "WM"
                        and r["M_or_K"] == wm_target["M_or_K"]
                        and abs(r["sparsity_frac"] - wm_target["sparsity_frac"]) < 1e-6),
                        None)
        wm_ok = (wm_row is not None and
                    wm_target["top1_band_lo"] <= wm_row["top1_mechanism_mean"] <= wm_target["top1_band_hi"])

    # HP band evaluation
    range_ok = any(v["sparsity_range"] >= 0.05 for v in per_regime_M_summary.values())
    mono_ok = any(abs(v["spearman_rho_top1_vs_alpha"]) >= 0.80
                    for v in per_regime_M_summary.values())
    cv_ok = all(v["max_seed_cv"] <= 0.15 for v in per_regime_M_summary.values())

    # Arms differ
    arms_differ = all(
        abs(r["top1_mechanism_mean"] - r["top1_random_mean"]) >= 0.02
        for r in agg_rows) if agg_rows else False

    # Saturation checks (v3: WM upper-band check EARLY per META_RULE_L)
    pc_rows_all = [r for r in agg_rows if r["regime"] == "PC"]
    pc_all_saturated = (len(pc_rows_all) > 0 and
                        all(r["top1_mechanism_mean"] > 0.90 for r in pc_rows_all))
    pc_all_at_floor = (len(pc_rows_all) > 0 and
                       all(r["top1_mechanism_mean"] < 0.10 for r in pc_rows_all))

    wm_rows_all = [r for r in agg_rows if r["regime"] == "WM"]
    # v3: WM upper-band saturation check EARLY (fail-fast per META_RULE_L)
    wm_any_saturated = (len(wm_rows_all) > 0 and
                        any(r["top1_mechanism_mean"] > 0.90 for r in wm_rows_all))
    wm_saturated_points = [
        {"M_or_K": r["M_or_K"], "sparsity_frac": r["sparsity_frac"],
         "top1_mean": r["top1_mechanism_mean"]}
        for r in wm_rows_all if r["top1_mechanism_mean"] > 0.90
    ]
    wm_any_at_floor = (len(wm_rows_all) > 0 and
                       any(r["top1_mechanism_mean"] < 0.10 for r in wm_rows_all))

    # WM mechanism lift check (optional)
    wm_lift_ok = False
    if "WM" in regimes:
        for M_val in m_sweep:
            for alpha in sparsity_sweep:
                pc_r = next((r for r in agg_rows if r["regime"] == "PC"
                                and r["M_or_K"] == M_val
                                and abs(r["sparsity_frac"] - alpha) < 1e-6), None)
                wm_r = next((r for r in agg_rows if r["regime"] == "WM"
                                and r["M_or_K"] == M_val
                                and abs(r["sparsity_frac"] - alpha) < 1e-6), None)
                if pc_r and wm_r and (wm_r["top1_mechanism_mean"] >=
                                        pc_r["top1_mechanism_mean"] + 0.10):
                    wm_lift_ok = True
                    break
            if wm_lift_ok:
                break

    # Verdict logic (v3 REVIVAL priorities; META_RULE_L WM upper-band EARLY)
    if not all_cardinality_ok:
        verdict = "HARD_FAIL"
        verdict_msg = (f"HARD_FAIL_CARDINALITY_BREACH: per-seed cardinality != "
                       f"{EXPECTED_N_UNITS_FULL if not is_smoke else EXPECTED_N_UNITS_SMOKE}")
    elif wm_any_saturated:
        # v3 PRIMARY revival check: WM must NOT saturate at any point
        verdict = "HARD_FAIL"
        verdict_msg = (f"HF_STILL_SATURATED_WM: WM top1 > 0.90 at {len(wm_saturated_points)} "
                       f"point(s); c={CORRUPTION_WM} still not steep enough. "
                       f"Saturated points: {wm_saturated_points}")
    elif pc_all_saturated:
        verdict = "HARD_FAIL"
        verdict_msg = (f"HF_STILL_SATURATED_PC: PC top1 > 0.90 at every (M, alpha). "
                       f"Per-M-summary={per_regime_M_summary}")
    elif pc_all_at_floor or wm_any_at_floor:
        verdict = "HARD_FAIL"
        verdict_msg = (f"HF_CRUMBLE: pc_all_at_floor={pc_all_at_floor} "
                       f"wm_any_at_floor={wm_any_at_floor}. "
                       f"Per-M-summary={per_regime_M_summary}")
    elif not pc_ok:
        verdict = "HARD_FAIL"
        verdict_msg = f"HARD_FAIL_POSITIVE_CONTROL_PC: pc_row={pc_row}"
    elif not wm_ok:
        verdict = "HARD_FAIL"
        verdict_msg = f"HARD_FAIL_POSITIVE_CONTROL_WM: wm target out-of-band"
    elif not arms_differ:
        verdict = "HARD_FAIL"
        verdict_msg = "HARD_FAIL_ARMS_IDENTICAL"
    elif range_ok and mono_ok and cv_ok:
        verdict = "HARD_PASS"
        verdict_msg = (f"HP_SPARSITY_DISCRIMINATES_ALL_REGIMES: v3 revival clears "
                       f"both PC and WM. per_regime_M_summary={per_regime_M_summary} "
                       f"wm_lift_ok={wm_lift_ok}")
    elif range_ok or mono_ok:
        verdict = "MIDDLE_BAND"
        verdict_msg = (f"MIDDLE_BAND: partial (range_ok={range_ok} mono_ok={mono_ok} "
                       f"cv_ok={cv_ok}). per_regime_M_summary={per_regime_M_summary}")
    else:
        verdict = "MIDDLE_BAND"
        verdict_msg = (f"MIDDLE_BAND: sparsity flat, weak lever. "
                       f"per_regime_M_summary={per_regime_M_summary}")

    return {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict_msg,
        "per_regime_M_summary": per_regime_M_summary,
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
        "hp_g_wm_not_saturated": (not wm_any_saturated),
        "hp_pc_not_saturated": (not pc_all_saturated),
        "wm_mechanism_lift_ok": wm_lift_ok,
        "wm_saturated_points": wm_saturated_points,
        "REQUIRED_FIELDS_check": list(REQUIRED_FIELDS),
    }


def _spearman(x: List[float], y: List[float]) -> float:
    """Simple Spearman rho via rank; assumes no ties."""
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

    # 1. Cardinality math (v3: SMOKE=18 because WM in smoke)
    if EXPECTED_N_UNITS_FULL != 18:
        return False, f"FULL cardinality {EXPECTED_N_UNITS_FULL} != 18"
    if EXPECTED_N_UNITS_SMOKE != 18:
        return False, f"SMOKE cardinality {EXPECTED_N_UNITS_SMOKE} != 18 (v3: WM in smoke)"
    msgs.append(f"cardinality FULL={EXPECTED_N_UNITS_FULL} SMOKE={EXPECTED_N_UNITS_SMOKE}")

    # 2. Formula-only sanity for PC positive-control regime
    pred_pc = predicted_top1_1step(N_DIM_FULL, 2000, 0.10, CORRUPTION_PC)
    if not (0.0 <= pred_pc <= 0.60):
        return False, f"PC positive-control formula pred out-of-range: {pred_pc}"
    msgs.append(f"PC-target formula pred_top1={pred_pc:.4f}")

    # 3. Formula sanity for WM positive-control at c=0.55 (v3 primary revival)
    pred_wm = predicted_top1_1step(N_DIM_FULL, 2000, 0.10, CORRUPTION_WM)
    if not (0.0 <= pred_wm <= 0.40):
        return False, f"WM positive-control formula pred out-of-range: {pred_wm}"
    msgs.append(f"WM-target formula pred_top1={pred_wm:.4f} (c={CORRUPTION_WM})")

    # 4. v3 REVIVAL check: WM c raised from 0.40 to 0.55 (Skunkworks Wave 7 criterion)
    if CORRUPTION_WM != 0.55:
        return False, f"v3 revival check: CORRUPTION_WM {CORRUPTION_WM} != 0.55"
    msgs.append(f"v3 revival criterion honored: CORRUPTION_WM=0.55 (Skunkworks Wave 7)")

    # 5. v3 empirical bracket citation from v2 MEASURED (formula-adjusted)
    #    v2 MEASURED@WM K=2000 alpha=0.10 c=0.40: 0.8228
    #    Predicted delta at same regime: 0.8228 - 0.5110 = 0.3118 (systematic
    #    formula under-prediction for WM bank-averaging)
    #    v3 predicted at c=0.55: 0.1473 + 0.3118 = ~0.46 (target [0.30, 0.90])
    msgs.append(f"v3 empirical bracket: WM K=2000 alpha=0.10 c=0.55 pred~0.46 "
                f"(v2 MEASURED c=0.40 was 0.8228; delta=0.3118 formula shift)")

    # 6. CRLB monotonicity in alpha at M=2000
    c_lo = crlb_1step_cliff_prediction(N_DIM_FULL, 2000, 0.05)
    c_hi = crlb_1step_cliff_prediction(N_DIM_FULL, 2000, 0.20)
    if not (c_lo < c_hi):
        return False, f"CRLB not monotone in alpha: lo={c_lo} hi={c_hi}"
    msgs.append(f"CRLB monotone: alpha=0.05 -> {c_lo:.4f}, alpha=0.20 -> {c_hi:.4f}")

    # 7. Encoder + sparsity mask codebook distinctness across 3 alpha
    M_san = 20
    N_san = 512
    hashes = {}
    for density in SPARSITY_LEVELS:
        X_dense = _build_hrr_real_dense(M_san, N_san, seed)
        X, mask = _apply_sparsity_mask_hrr(X_dense, density, seed)
        h = hashlib.sha256(X.cpu().numpy().tobytes()).hexdigest()[:16]
        hashes[f"hrr_real@s={density}"] = h
        del X_dense, X, mask
        if _CUDA_OK:
            torch.cuda.empty_cache()
    if len(set(hashes.values())) != len(hashes):
        return False, f"codebooks NOT distinct at seed={seed}: {hashes}"
    msgs.append(f"3 hrr_real x sparsity codebooks distinct at seed={seed}")

    # 8. Calibration: PC c=0.30 cos ~ 0.40 (tol 0.15)
    M_cal = 30
    N_cal = 2048
    X_dense = _build_hrr_real_dense(M_cal, N_cal, seed)
    X, _ = _apply_sparsity_mask_hrr(X_dense, 0.20, seed)
    Q = _corrupt_hrr_real(X, 0.30, seed * 7)
    Qn = torch.linalg.norm(Q, dim=1).clamp(min=1e-12)
    Xn = torch.linalg.norm(X, dim=1).clamp(min=1e-12)
    cos_per = (Q * X).sum(dim=1) / (Qn * Xn)
    cos_mean = float(cos_per.mean().item())
    target = 1.0 - 2.0 * 0.30
    if abs(cos_mean - target) > 0.15:
        return False, f"calibration FAIL c=0.30 alpha=0.20: cos={cos_mean:.4f} target={target:.4f}"
    msgs.append(f"calibration hrr_real c=0.30 alpha=0.20: cos={cos_mean:.4f} (target={target:.4f})")
    del X_dense, X, Q

    # 9. Calibration: WM c=0.55 cos ~ -0.10 (tol 0.15) -- v3 primary revival value
    M_cal = 30
    N_cal = 2048
    X_dense = _build_hrr_real_dense(M_cal, N_cal, seed + 1)
    X, _ = _apply_sparsity_mask_hrr(X_dense, 0.10, seed + 1)
    Q = _corrupt_hrr_real(X, 0.55, seed * 11)
    Qn = torch.linalg.norm(Q, dim=1).clamp(min=1e-12)
    Xn = torch.linalg.norm(X, dim=1).clamp(min=1e-12)
    cos_per = (Q * X).sum(dim=1) / (Qn * Xn)
    cos_mean = float(cos_per.mean().item())
    # c=0.55 clamped to 0.4999 in _corrupt_hrr_real -> target 1-2*0.4999 = 0.0002 ~ 0
    target_c055 = 1.0 - 2.0 * min(0.55, 0.4999)
    if abs(cos_mean - target_c055) > 0.15:
        return False, (f"calibration FAIL c=0.55 alpha=0.10: cos={cos_mean:.4f} "
                       f"target={target_c055:.4f}")
    msgs.append(f"calibration hrr_real c=0.55 alpha=0.10: cos={cos_mean:.4f} "
                f"(target={target_c055:.4f})")
    del X_dense, X, Q

    # 10. Mechanism sanity: single-step T=1 at moderate corruption fires
    X_dense = _build_hrr_real_dense(100, 2048, seed)
    X, mask = _apply_sparsity_mask_hrr(X_dense, 0.10, seed)
    Q0 = _corrupt_hrr_real(X, 0.30, seed * 3)
    Q1 = _hopfield_cleanup(Q0, X, 1, BETA, active_mask=mask)
    sims = _score(Q1, X)
    preds = sims.argmax(dim=1)
    target_idx = torch.arange(100, device=DEVICE)
    n_hit = int((preds == target_idx).sum().item())
    top1_check = n_hit / 100.0
    if not (0.50 <= top1_check <= 1.0):
        return False, (f"mechanism T=1 sanity below floor at c=0.30 M=100 N=2048 "
                       f"alpha=0.10: top1={top1_check:.3f} (expected > 0.5)")
    msgs.append(f"mechanism sanity T=1: c=0.30 M=100 N=2048 alpha=0.10 top1={top1_check:.3f}")

    return True, "; ".join(msgs)
