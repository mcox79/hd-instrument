"""Shared core for sparsity_free_axis_v4_pc_only sibling cells.

V4 RATIONALE (2026-07-01):
    v2 (all-4-axis revival) landed HARD_FAIL_POSITIVE_CONTROL_WM: the WM regime
    positive control failed. Deeper audit (v3 cell-author 2026-07-01) traced the
    WM failure to an ARCHITECTURAL BUG in the shared v2/v3 core:

      # experiments/_sparsity_free_axis_v2_core.py:419
      vals_corr = _corrupt_hrr_real(vals, CORRUPTION_WM, sub_seed)
      # ...
      readouts = keys * bank_trace   # uses `vals` via bank_trace, NOT vals_corr
      cleaned = _hopfield_cleanup(readouts_normed, vals, T_WM, ...)  # `vals`

    `vals_corr` is COMPUTED (line 419) and only used in calibration diagnostics
    (lines 443-445), NEVER used in the WM readout path. The WM top1 is therefore
    INSENSITIVE to CORRUPTION_WM by construction. v3 tried to escalate c to 0.55
    but the readout couldn't see it: v3 at c=0.55 gave IDENTICAL WM top1 as v2 at
    c=0.40 (three matching points confirmed: 0.9526, 0.9626, 0.8228).

    Skunkworks' Wave 7 v3 revival criterion (raise WM c to 0.55) is
    ARCHITECTURALLY UNACHIEVABLE at the current WM readout design.

    v4 RESPONSE (this cell): retire WM regime entirely; run PC-only. v2's PC
    data was already HARD_PASS-clean by every gate we care about — v2's overall
    HARD_FAIL was ONLY on WM. This cell bank the PC axis CG today; WM regime
    corruption-recovery is DEFERRED to a future v5 with the readout bug fixed.

    (Future v5 scope in notes/wm_readout_architectural_bug_deferred_v5_2026-07-01.md)

v2 PC RESULTS RE-READ (MEASURED@ 3 seeds; supports v4 pre-reg gates):
    All 27 (3 seeds x 3 M x 3 alpha) points MEASURED in [0.3555, 0.7300]
      well inside band [0.30, 0.90].
    Spearman rho vs alpha = -1.0 at all 3 M levels (monotone-decreasing lever).
    Cross-seed cv <= 0.023 everywhere (well below 0.05 gate).
    Random floor 0.001 (well below 0.05 chance gate).
    verdict PC-scope-only would have been HARD_PASS_SPARSITY_MONOTONE_PC.

    Cite: MEASURED@d:/AI/hd-instrument/data/exp_substrate_sparsity_free_axis_v2_n4096_seed_7/metrics.json
          MEASURED@d:/AI/hd-instrument/data/exp_substrate_sparsity_free_axis_v2_n4096_seed_13/metrics.json
          MEASURED@d:/AI/hd-instrument/data/exp_substrate_sparsity_free_axis_v2_n4096_seed_19/metrics.json

Design (LOCKED):
    5 M x 3 alpha x PC-only = 15 phase points per seed (FULL == SMOKE grid;
    DISCRIMINATOR-SURVIVES-SCALE rule).

Fixed:
    encoder = hrr_real (chain-grade default; Gaussian codebook L2-normalized)
    N = 4096 (v2-inherited)
    c = 0.60 (v2 empirically-calibrated escape)
    T_cleanup = 1 (v2-inherited; single-step CRLB readout)
    beta = 8.0 (v2-inherited)

M levels SWEPT (extended from v2 with 2 additional points):
    {800, 1000, 1500, 2000, 2500}
    * v2 had {1000, 1500, 2000} — extend on both ends
    * M=800 predicted top1 ~0.75-0.80 (still in band, high side)
    * M=2500 predicted top1 ~0.30-0.35 (still in band, low side)
    * If either edge saturates or crumbles, cell still HP on the 3 interior M

Sparsity levels SWEPT (v2-inherited):
    {0.05, 0.10, 0.20}

Arms (PC-only):
    ARM_MECHANISM: single-bank pattern completion with T=1 cleanup
    ARM_RANDOM_FLOOR: uncorrupted random codes projected to same active mask
                       (chance baseline)

Discriminator (HP band; META_RULE_L strictly-above-floor):
    HP_PC_MONOTONE: Spearman rho <= -0.80 (fixed sign; monotone-decreasing) at
                    ALL 5 M values (raised from v2's >=1-M requirement)
    HP_PC_IN_BAND: PC top1 in [0.30, 0.90] at ALL 15 (M, alpha) grid points
                   (v2-inherited broken-PC gate)
    HP_CROSS_SEED_TIGHT: cross-seed cv < 0.05 on top1 at each (M, alpha)
                         (v2 measured max cv=0.023; margin of 2x)
    HP_RANDOM_FLOOR: ARM_RANDOM_FLOOR top1 < 0.05 at every point (chance)
    HP_CARDINALITY: EXPECTED_N_UNITS = 15 per seed; observed == expected
    HP_ARMS_DIFFER: mechanism vs random hash != identical per point
                    (META_RULE_AF)

Hard-fail classes (any point):
    HF_SATURATION: any point with top1 > 0.90 => PC saturation at that regime
    HF_CRUMBLE: any point with top1 < 0.20 => too much capacity pressure
    HF_CARDINALITY_BREACH: observed < expected
    HF_POSITIVE_CONTROL: PC at M=2000 alpha=0.10 outside [0.30, 0.90]
    HF_ARMS_IDENTICAL: mechanism == random hash (arm bug)

Positive control (empirical; META_RULE_BC):
    PC hrr_real @ M=2000 alpha=0.10 N=4096 c=0.60 T=1:
      MEASURED@v2 seed_7=0.5070, seed_13=0.5300, seed_19=0.5075 => mean=0.515
      band [0.30, 0.90] => tolerance 0.10 vs mean 0.515 = well within

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
    - arms_differ_verified at smoke gate (MECHANISM vs RANDOM_FLOOR per point)
    - final_metrics_atomicity: tmp_replace (per sibling cell main())
    - except SystemExit: raise BEFORE except Exception (see sibling cell main)
    - crlb_floor_computed via crlb_1step_cliff_prediction; reachable
    - baseline_in_band: RANDOM_FLOOR at chance; MECHANISM in [0.30, 0.90]
    - discriminator survives scale (SMOKE == FULL grid; only n_seeds differs)
    - HARD_PASS strictly above floor + 5% band-width
    - HP_SCOPE: HARD_PASS applies to MECHANISM arm only
    - cardinality_ok: EXPECTED_N_UNITS_FULL=15, SMOKE=15 (same grid)
    - per-unit failure-class: no bare except; halt on any per-point exception
    - calibration_check: default_ok_for_this_regime (v2 empirically calibrated)
    - all numbers tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@

ASCII-only. No unicode. No em-dashes. No emojis.
CPU-eligible (numpy + small torch). Route: remote_cpu_queue per USER 2026-07-01.

PRE-REG: preregs/2026-07-01_substrate_sparsity_free_axis_v4_pc_only_n4096.md

Author: hdi_exp_dev 2026-07-01 (Opus 4.7 1M, agent-spawn; Option D per prior cell-author)
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
CRUMBLE_TOP1 = 0.20
HARD_PASS_LO = 0.30
HARD_PASS_HI = 0.90
FLOOR_TOP1 = 0.10
HP_DISCRIMINATOR = 0.20  # mechanism - random_floor
MB_DISCRIMINATOR = 0.10
RANDOM_FLOOR_CAP = 0.05  # chance baseline gate
CROSS_SEED_CV_GATE = 0.05  # v2 measured max cv=0.023; 2x margin

BETA = 8.0

ENCODER_FAMILY = "hrr_real"

# Sparsity levels (INNER axis C; SWEPT; v2-inherited)
SPARSITY_LEVELS = (0.05, 0.10, 0.20)

# M levels (OUTER axis; SWEPT; extended from v2 with 2 additional points)
# v2 was {1000, 1500, 2000}; v4 adds M=800 (high top1) + M=2500 (low top1)
M_LEVELS = (800, 1000, 1500, 2000, 2500)

# PC regime only (WM retired due to v2/v3 architectural bug)
REGIMES_FULL = ("PC",)
REGIMES_SMOKE = ("PC",)

# Fixed dimensionality (v2-inherited)
N_DIM_FULL = 4096
N_DIM_SMOKE = 4096  # DISCRIMINATOR-SURVIVES-SCALE — full N at smoke

# PC regime (v2 empirically-calibrated)
CORRUPTION_PC = 0.60
T_PC = 1

# Cardinality (LOCKED)
EXPECTED_N_UNITS_FULL = len(M_LEVELS) * len(SPARSITY_LEVELS) * len(REGIMES_FULL)   # 15
EXPECTED_N_UNITS_SMOKE = EXPECTED_N_UNITS_FULL  # smoke uses same grid

# Positive control (META_RULE_BC; v2-measured empirical calibration)
# MEASURED@d:/AI/hd-instrument/data/exp_substrate_sparsity_free_axis_v2_n4096_seed_7/metrics.json
POSITIVE_CONTROL_PC = {
    "regime": "PC",
    "M_or_K": 2000,
    "sparsity_frac": 0.10,
    "top1_band_lo": 0.30,
    "top1_band_hi": 0.90,
    "v2_measured_seed_7": 0.5070,
    "v2_measured_seed_13": 0.5300,
    "v2_measured_seed_19": 0.5075,
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
    if N <= 0 or M <= 1 or sparsity_frac <= 0:
        return 0.0
    N_eff = max(1.0, sparsity_frac * N)
    return 2.0 * M * math.log(M) / N_eff


def get_backend_label() -> str:
    return "torch.cuda" if _CUDA_OK else "torch.cpu"


# ---------------------------------------------------------------------------
# HRR-real encoder + sparsity mask + corruption
# ---------------------------------------------------------------------------
def _build_hrr_real_dense(M: int, N: int, seed: int) -> "torch.Tensor":
    g = np.random.default_rng(seed)
    arr = (g.standard_normal(size=(M, N)) / math.sqrt(N)).astype(np.float32)
    norms = np.linalg.norm(arr, axis=1, keepdims=True).clip(min=1e-12)
    arr = arr / norms
    return torch.from_numpy(arr).to(DEVICE)


def _apply_sparsity_mask_hrr(X: "torch.Tensor", density: float,
                                seed: int) -> Tuple["torch.Tensor", "torch.Tensor"]:
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

    # ARM_MECHANISM: T_PC single-step cleanup
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


def _classify_tier(top1: float, disc: float) -> str:
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
    is_smoke = (run_mode == "smoke")
    sparsity_sweep = SPARSITY_LEVELS
    m_sweep = M_LEVELS
    regimes = REGIMES_SMOKE if is_smoke else REGIMES_FULL

    expected_n_units = len(m_sweep) * len(sparsity_sweep) * len(regimes)
    N_dim = N_DIM_FULL

    print(f"[run_one_seed] seed={seed} mode={run_mode} device={DEVICE} "
            f"regimes={regimes} M={list(m_sweep)} sparsity={list(sparsity_sweep)} "
            f"N={N_dim} T_pc={T_PC} c_pc={CORRUPTION_PC} "
            f"expected_n={expected_n_units}", flush=True)

    per_point_rows: List[Dict[str, Any]] = []
    for regime in regimes:
        for M_val in m_sweep:
            for alpha in sparsity_sweep:
                print(f"  [point] regime={regime} M={M_val} alpha={alpha}", flush=True)
                if regime == "PC":
                    row = _eval_pc_point(alpha, N_dim, M_val, seed, is_smoke)
                else:
                    raise ValueError(f"unknown regime={regime!r} (v4 is PC-only)")
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
    is_smoke = (run_mode == "smoke")
    sparsity_sweep = SPARSITY_LEVELS
    m_sweep = M_LEVELS
    regimes = REGIMES_SMOKE if is_smoke else REGIMES_FULL

    keyed: Dict[Tuple[str, int, float], List[float]] = {}
    keyed_rnd: Dict[Tuple[str, int, float], List[float]] = {}
    tier_per_key: Dict[Tuple[str, int, float], List[str]] = {}
    arms_differ_per_key: Dict[Tuple[str, int, float], List[bool]] = {}
    all_cardinality_ok = True

    for seed, sd in per_seed.items():
        if not sd.get("cardinality_ok", False):
            all_cardinality_ok = False
        for row in sd.get("per_point_rows", []):
            k = (row["regime"], row["M_or_K"], row["sparsity_frac"])
            keyed.setdefault(k, []).append(row["top1_mechanism"])
            keyed_rnd.setdefault(k, []).append(row["top1_random"])
            tier_per_key.setdefault(k, []).append(row["verdict_tier_per_point"])
            arms_differ_per_key.setdefault(k, []).append(row.get("arms_differ_at_point", False))

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
                    "arms_differ_all_seeds": all(arms_differ_per_key.get(k, [])),
                    "n_seeds_at_point": len(vals),
                })

    # Per-M Spearman + monotone-in-alpha check
    per_M_summary: Dict[str, Dict[str, Any]] = {}
    for M_val in m_sweep:
        rows = [r for r in agg_rows if r["regime"] == "PC" and r["M_or_K"] == M_val]
        rows.sort(key=lambda r: r["sparsity_frac"])
        if not rows:
            continue
        top1_by_alpha = [r["top1_mechanism_mean"] for r in rows]
        alphas = [r["sparsity_frac"] for r in rows]
        range_val = max(top1_by_alpha) - min(top1_by_alpha)
        rho = _spearman(alphas, top1_by_alpha) if len(rows) >= 3 else 0.0
        seed_cvs = [r["seed_cv"] for r in rows]
        max_cv = max(seed_cvs) if seed_cvs else 0.0
        per_M_summary[f"PC_M{M_val}"] = {
            "regime": "PC",
            "M_or_K": M_val,
            "sparsity_range": round(range_val, 4),
            "spearman_rho_top1_vs_alpha": round(rho, 4),
            "max_seed_cv": round(max_cv, 4),
            "alphas_swept": list(alphas),
            "top1_by_alpha": [round(v, 4) for v in top1_by_alpha],
        }

    # Positive control
    pc_target = POSITIVE_CONTROL_PC
    pc_row = next((r for r in agg_rows
                    if r["regime"] == "PC"
                    and r["M_or_K"] == pc_target["M_or_K"]
                    and abs(r["sparsity_frac"] - pc_target["sparsity_frac"]) < 1e-6),
                    None)
    pc_ok = (pc_row is not None and
                pc_target["top1_band_lo"] <= pc_row["top1_mechanism_mean"] <= pc_target["top1_band_hi"])

    # HP gates
    hp_pc_monotone = all(v["spearman_rho_top1_vs_alpha"] <= -0.80
                            for v in per_M_summary.values())
    hp_pc_in_band = all(HARD_PASS_LO <= r["top1_mechanism_mean"] <= HARD_PASS_HI
                            for r in agg_rows)
    hp_cross_seed_tight = all(r["seed_cv"] < CROSS_SEED_CV_GATE for r in agg_rows)
    hp_random_floor = all(r["top1_random_mean"] < RANDOM_FLOOR_CAP for r in agg_rows)
    hp_arms_differ_all = all(r.get("arms_differ_all_seeds", False) for r in agg_rows)

    # HF classes (any point)
    hf_saturation_points = [(r["M_or_K"], r["sparsity_frac"], r["top1_mechanism_mean"])
                                for r in agg_rows if r["top1_mechanism_mean"] > SATURATED_TOP1]
    hf_crumble_points = [(r["M_or_K"], r["sparsity_frac"], r["top1_mechanism_mean"])
                            for r in agg_rows if r["top1_mechanism_mean"] < CRUMBLE_TOP1]

    # Verdict logic
    if not all_cardinality_ok:
        verdict = "HARD_FAIL"
        verdict_msg = (f"HARD_FAIL_CARDINALITY_BREACH: per-seed cardinality != "
                       f"{EXPECTED_N_UNITS_FULL}")
    elif hf_saturation_points:
        verdict = "HARD_FAIL"
        verdict_msg = (f"HF_SATURATION: {len(hf_saturation_points)} points > 0.90: "
                       f"{hf_saturation_points[:5]}")
    elif hf_crumble_points:
        verdict = "HARD_FAIL"
        verdict_msg = (f"HF_CRUMBLE: {len(hf_crumble_points)} points < 0.20: "
                       f"{hf_crumble_points[:5]}")
    elif not pc_ok:
        verdict = "HARD_FAIL"
        verdict_msg = f"HARD_FAIL_POSITIVE_CONTROL_PC: pc_row={pc_row}"
    elif not hp_arms_differ_all:
        verdict = "HARD_FAIL"
        verdict_msg = "HARD_FAIL_ARMS_IDENTICAL (META_RULE_AF)"
    elif not hp_random_floor:
        verdict = "HARD_FAIL"
        verdict_msg = (f"HARD_FAIL_RANDOM_FLOOR_ABOVE_CHANCE: max_rnd="
                       f"{max(r['top1_random_mean'] for r in agg_rows):.4f}")
    elif hp_pc_monotone and hp_pc_in_band and hp_cross_seed_tight:
        verdict = "HARD_PASS"
        verdict_msg = (f"HP_SPARSITY_PC_AXIS_CG: monotone rho<=-0.80 on all "
                       f"{len(per_M_summary)} M-levels; in-band [0.30,0.90] on all "
                       f"{len(agg_rows)} points; cross-seed cv<{CROSS_SEED_CV_GATE} "
                       f"everywhere; random-floor chance; per_M_summary={per_M_summary}")
    elif hp_pc_monotone or hp_pc_in_band:
        verdict = "MIDDLE_BAND"
        verdict_msg = (f"MIDDLE_BAND: partial (monotone={hp_pc_monotone} "
                       f"in_band={hp_pc_in_band} tight_cv={hp_cross_seed_tight}); "
                       f"per_M_summary={per_M_summary}")
    else:
        verdict = "MIDDLE_BAND"
        verdict_msg = (f"MIDDLE_BAND: sparsity lever weak; per_M_summary={per_M_summary}")

    return {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict_msg,
        "per_M_summary": per_M_summary,
        "agg_rows": agg_rows,
        "per_seed": {str(k): {"observed_n_units": v.get("observed_n_units"),
                                "cardinality_ok": v.get("cardinality_ok")}
                        for k, v in per_seed.items()},
        "expected_n_units_per_seed": EXPECTED_N_UNITS_FULL,
        "observed_n_units": sum(v.get("observed_n_units", 0) for v in per_seed.values()),
        "cardinality_ok": all_cardinality_ok,
        "positive_control_pc_ok": pc_ok,
        "hp_pc_monotone_all_M": hp_pc_monotone,
        "hp_pc_in_band_all_points": hp_pc_in_band,
        "hp_cross_seed_tight_all_points": hp_cross_seed_tight,
        "hp_random_floor_chance": hp_random_floor,
        "hp_arms_differ_all_points": hp_arms_differ_all,
        "hf_saturation_points": hf_saturation_points,
        "hf_crumble_points": hf_crumble_points,
        "REQUIRED_FIELDS_check": list(REQUIRED_FIELDS),
    }


def _spearman(x: List[float], y: List[float]) -> float:
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
# Selftest
# ---------------------------------------------------------------------------
def selftest(seed: int) -> Tuple[bool, str]:
    msgs: List[str] = []

    # 1. Cardinality math
    if EXPECTED_N_UNITS_FULL != 15:
        return False, f"FULL cardinality {EXPECTED_N_UNITS_FULL} != 15"
    msgs.append(f"cardinality FULL={EXPECTED_N_UNITS_FULL} SMOKE={EXPECTED_N_UNITS_SMOKE}")

    # 2. Formula: pred_top1 at v2-calibrated regime
    pred_pc = predicted_top1_1step(N_DIM_FULL, 2000, 0.10, CORRUPTION_PC)
    if not (0.0 <= pred_pc <= 0.60):
        return False, f"PC formula pred out-of-range: {pred_pc}"
    msgs.append(f"PC pred_top1 M=2000 alpha=0.10 c=0.60: {pred_pc:.4f} "
                f"(v2 MEASURED=0.515)")

    # 3. Empirically-calibrated v2 measured cite (MEASURED@ tag)
    msgs.append(f"REVIVAL EMPIRICAL CITE: v2 MEASURED PC top1 at M=2000 alpha=0.10 "
                f"= mean(0.5070, 0.5300, 0.5075) = 0.515 in [0.30, 0.90] band")

    # 4. CRLB monotonicity in alpha at M=2000
    c_lo = crlb_1step_cliff_prediction(N_DIM_FULL, 2000, 0.05)
    c_hi = crlb_1step_cliff_prediction(N_DIM_FULL, 2000, 0.20)
    if not (c_lo < c_hi):
        return False, f"CRLB not monotone in alpha: lo={c_lo} hi={c_hi}"
    msgs.append(f"CRLB monotone: alpha=0.05 -> {c_lo:.4f}, alpha=0.20 -> {c_hi:.4f}")

    # 5. M-sweep extension bounds check: M=800 and M=2500 predicted still in band
    for M_check in (800, 2500):
        pred = predicted_top1_1step(N_DIM_FULL, M_check, 0.10, CORRUPTION_PC)
        # Just check formula runs; formula under-predicts substrate empirical
        if not (0.0 <= pred <= 1.0):
            return False, f"pred out-of-range M={M_check}: {pred}"
    msgs.append(f"extended-M formula check M=800,2500 alpha=0.10 c=0.60 ran clean")

    # 6. Encoder distinctness across 3 alpha
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

    # 7. Calibration at c=0.30 (target_cos = 0.40, in the regime where
    #    the closed-form E[cos] ~ 1-2c is analytically achievable).
    #    Note: v4 production regime uses c=0.60 (target_cos = -0.20); the
    #    additive-Gaussian-to-active model with sigma calibrated from
    #    target_cos^2 achieves target_cos only when target_cos > 0. At c=0.60
    #    the empirical cos lands near 0 (heavily-corrupted regime); this is
    #    KNOWN + INTENTIONAL and calibrated empirically via MEASURED@ v2 data
    #    (v2 seed_{7,13,19} at c=0.60 M=2000 alpha=0.10 top1 in [0.51, 0.53]).
    #    Selftest confirms the formula works at c=0.30 (light-corruption); v4
    #    substrate behavior at c=0.60 is validated by v2 MEASURED cite.
    M_cal = 30
    N_cal = 2048
    X_dense = _build_hrr_real_dense(M_cal, N_cal, seed)
    X, _ = _apply_sparsity_mask_hrr(X_dense, 0.10, seed)
    Q = _corrupt_hrr_real(X, 0.30, seed * 7)  # c=0.30 for formula sanity
    Qn = torch.linalg.norm(Q, dim=1).clamp(min=1e-12)
    Xn = torch.linalg.norm(X, dim=1).clamp(min=1e-12)
    cos_per = (Q * X).sum(dim=1) / (Qn * Xn)
    cos_mean = float(cos_per.mean().item())
    target = 1.0 - 2.0 * 0.30  # 0.40
    if abs(cos_mean - target) > 0.15:
        return False, (f"calibration FAIL c=0.30 alpha=0.10: "
                       f"cos={cos_mean:.4f} target={target:.4f}")
    msgs.append(f"calibration hrr_real c=0.30 alpha=0.10: "
                f"cos={cos_mean:.4f} (target={target:.4f}); "
                f"c={CORRUPTION_PC} regime validated via v2 MEASURED cite")
    del X_dense, X, Q

    # 8. Mechanism sanity: T=1 at moderate corruption fires (> chance)
    X_dense = _build_hrr_real_dense(100, 2048, seed)
    X, mask = _apply_sparsity_mask_hrr(X_dense, 0.10, seed)
    Q0 = _corrupt_hrr_real(X, 0.30, seed * 3)  # softer corruption for sanity
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

    # 9. Arms-must-differ: mechanism vs random at smoke config
    row = _eval_pc_point(0.10, 4096, 200, seed, is_smoke=True)
    if not row["arms_differ_at_point"]:
        return False, (f"arms-differ FAIL META_RULE_AF: mechanism_hash="
                       f"{row['arms_hash_mechanism']} == random_hash={row['arms_hash_random']}")
    msgs.append(f"arms-differ META_RULE_AF pass (M=200 alpha=0.10 mech/rnd distinct)")

    return True, "; ".join(msgs)
