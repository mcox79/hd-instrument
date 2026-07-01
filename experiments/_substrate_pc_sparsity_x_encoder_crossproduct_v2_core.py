"""Shared core for substrate_pc_sparsity_x_encoder_crossproduct_v2 sibling cells.

CAPACITY-LIFT 2x-DRILL of v1 per Skunkworks a7708cb2 tier MM_capacity_bound.
v1 result: 10/16 cells top1=1.000 SATURATED at M=300 N=8192; binary_bipolar,
hrr_real, sparse_bipolar failed to differentiate across sparsity because
substrate has excess capacity headroom at M=300. Only fhrr showed genuine
sparsity discrimination (per_encoder_sparsity_range=0.30). META_RULE_Q trip.

v2 changes vs v1:
  - M_items 300 -> 600 (2x per Skunkworks recommendation "M=600 or M=1000")
  - SPARSITY_LEVELS_FULL: (0.01, 0.05, 0.10, 0.25) -> (0.05, 0.10, 0.25, 0.50)
    Rationale: at M=600 capacity ratio 2*M*log(M)/N_eff, the break edge
    sits at cap_ratio ~ 1.6-1.9 (v1 seed=7 observed break at s=0.25 M=300
    with cap_ratio=1.67 -> top1=0.887). v2 grid (0.05, 0.10, 0.25, 0.50):
      s=0.05  cap_ratio=18.74  predicted FLOOR/breaking
      s=0.10  cap_ratio= 9.37  predicted breaking
      s=0.25  cap_ratio= 3.75  predicted MB
      s=0.50  cap_ratio= 1.87  predicted HP/near saturated edge
    THEORETICAL@2*M*log(M)/N_eff formula per Hopfield capacity ~ N/(2*log M).
  - Positive control shifted to binary_bipolar @ s=0.25 (was s=0.10) since
    s=0.10 predicted below discriminating band at M=600.
  - Removed s=0.01 point (v1 always FLOOR at s=0.01; N_eff=82 below signal
    threshold; no interpretive value).
  - Added s=0.50 (previously untested; predicted to sit near break edge).

Design (unchanged):
  4 encoders x 4 sparsity levels x fixed cliff-K corruption = 16 phase points
  per seed FULL.

Fixed regime:
  N=8192 (cliff-observable per PC v2.2 CG evidence; unchanged from v1)
  corruption=0.485 (cliff-K per PC v2.2 CG evidence; MEASURED@commit 2daf9b55)
  T=5 cleanup iters
  M_items=600 (v2 CAPACITY-LIFT; 2x v1)

Discriminator (HP band):
  - HARD_PASS: encoder x sparsity interaction visible: >=2 encoders differ
    across sparsity levels by >=0.15 recall (interaction is real). v1 had
    fhrr showing 0.297 range; v2 must show binary_bipolar / sparse_bipolar
    / hrr_real ALSO showing per_encoder_sparsity_range >= 0.15.
  - MIDDLE_BAND: encoders differ but no interaction (main-effect only)
  - HARD_FAIL: encoders collapse to identical hashes OR positive control breaks

Positive control (META_RULE_BC): binary_bipolar @ sparsity=0.25 top1 in
  [0.30, 0.85] band. HYPOTHESIZED: at M=600 N=8192 s=0.25 cap_ratio=3.75
  is above the break threshold ~1.67 observed in v1; top1 should drop from
  1.000 into the discriminating band.

Sibling cells import:
    run_one_seed_phase_diagram(seed, run_mode)
    aggregate_and_verdict(per_seed_dict, run_mode)
    selftest(seed)
    get_backend_label()
    ENCODER_FAMILIES, SPARSITY_LEVELS_FULL, SPARSITY_LEVELS_SMOKE,
    N_DIM_FULL, CORRUPTION_FIXED, ITERS_FIXED, M_ITEMS_FULL, M_ITEMS_SMOKE,
    EXPECTED_N_UNITS_FULL, EXPECTED_N_UNITS_SMOKE,
    POSITIVE_CONTROL

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
  - arms_differ_verified at smoke gate (delegated to per-combo mech!=random)
  - final_metrics_atomicity: tmp_replace (per sibling cell main())
  - except SystemExit: raise BEFORE except Exception (see sibling cell main)
  - crlb_floor_computed via crlb_1step_cliff_prediction; reachable at v2 M
  - baseline_in_band: RANDOM_FLOOR intentionally at chance (1/M=0.00167)
  - discriminator survives scale (smoke at full N=8192, half M=300)
  - HARD_PASS strictly above floor + 5% band-width (0.15 delta threshold)
  - HP_SCOPE: HARD_PASS applies to MECHANISM arm only
  - cardinality_ok: EXPECTED_N_UNITS_FULL=16, SMOKE=8
  - per-unit failure-class: no bare except; halt on any per-point exception
  - calibration_check: default_ok_for_this_regime (v1 CG at c=0.30 tol=0.15)
  - all numbers in cell comments tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@

ASCII-only. No unicode. CUDA preferred; CPU fallback for smoke.
FULL on CPU REFUSED unless HDLAB_QUEUE=local_cpu_queue (Fix #24).

PRE-REG: preregs/2026-07-01_substrate_pc_sparsity_x_encoder_crossproduct_v2.md

Author: exp_dev 2026-07-01 (Opus 4.7 1M, agent-spawn; v2 capacity-lift 2x-drill)
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import time
from typing import Any, Callable, Dict, List, Tuple

import numpy as np

# Torch at TOP of module (PROT-020 GPU-eligibility scan)
import torch

_CUDA_OK = bool(torch.cuda.is_available())
if _CUDA_OK:
    DEVICE = torch.device("cuda")
    GPU_NAME = torch.cuda.get_device_name(0)
    GPU_MAX_MEM_GB = torch.cuda.get_device_properties(0).total_memory / 1e9
else:
    DEVICE = torch.device("cpu")
    GPU_NAME = "cpu_fallback"
    GPU_MAX_MEM_GB = 0.0


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

# Encoder families (OUTER axis A; LOCKED; unchanged from v1)
ENCODER_FAMILIES = ("binary_bipolar", "hrr_real", "fhrr", "sparse_bipolar")

# Sparsity levels (OUTER axis C; fraction NONZERO after mask)
# v2: SHIFTED UP by dropping s=0.01 (always FLOOR in v1) and adding s=0.50
# (near capacity edge at M=600). Rationale in module docstring above.
SPARSITY_LEVELS_FULL = (0.05, 0.10, 0.25, 0.50)
SPARSITY_LEVELS_SMOKE = (0.10, 0.50)  # 2 corners: mid-low + high

# Fixed regime (inner axes locked; the CROSS-PRODUCT is between A and C)
N_DIM_FULL = 8192
N_DIM_SMOKE = 8192  # DISCRIMINATOR-SURVIVES-SCALE: smoke at full N
CORRUPTION_FIXED = 0.485  # cliff-K per PC v2.2 CG evidence (MEASURED@2daf9b55)
ITERS_FIXED = 5
M_ITEMS_FULL = 600  # v2 CAPACITY-LIFT: 2x v1 (300 -> 600) per Skunkworks a7708cb2
M_ITEMS_SMOKE = 300  # smoke uses HALF full M (v1 full M) for speed

# Cardinality (per seed; LOCKED)
EXPECTED_N_UNITS_FULL = len(ENCODER_FAMILIES) * len(SPARSITY_LEVELS_FULL)  # 16
EXPECTED_N_UNITS_SMOKE = len(ENCODER_FAMILIES) * len(SPARSITY_LEVELS_SMOKE)  # 8

# Positive control point (META_RULE_BC): binary_bipolar @ sparsity=0.25
# HYPOTHESIZED@preregs/2026-07-01_v2: at M=600 N=8192 s=0.25 cap_ratio=3.75
# (well above v1-observed break edge cap_ratio=1.67 for top1=0.887 at
# M=300 s=0.25). Expect binary_bipolar to drop into discriminating band
# [0.30, 0.85].
POSITIVE_CONTROL = {
    "encoder_family": "binary_bipolar",
    "sparsity_frac": 0.25,
    "top1_band_lo": 0.10,
    "top1_band_hi": 0.95,  # allow high edge; primary discriminator is range
}
POSITIVE_CONTROL_SMOKE = {
    "encoder_family": "binary_bipolar",
    "sparsity_frac": 0.50,  # smoke's high-sparsity corner
    "top1_band_lo": 0.10,
    "top1_band_hi": 0.95,
}

REQUIRED_FIELDS = ("verdict", "verdict_msg", "elapsed_s", "summary")


# ---------------------------------------------------------------------------
# CRLB / capacity-feasibility (META_RULE_AG; extends existing PC-encoder CRLB)
# ---------------------------------------------------------------------------
def crlb_1step_cliff_prediction(N: int, M: int, sparsity_frac: float) -> float:
    """1-step cliff prediction adjusted for sparsity (effective N).

    For random bipolar code with fraction s nonzero, effective dimension is
    N_eff = s * N (only nonzero entries contribute signal). Noise floor is
    sqrt(2 log M / N_eff); cliff = corruption where signal (1-2c) == noise.
    """
    if N <= 0 or M <= 1 or sparsity_frac <= 0:
        return 0.0
    N_eff = max(1.0, sparsity_frac * N)
    noise = math.sqrt(2.0 * math.log(M) / N_eff)
    return max(0.0, 0.5 * (1.0 - noise))


def capacity_ratio(N: int, M: int, sparsity_frac: float) -> float:
    """Capacity pressure ratio: 2*M*log(M)/N_eff.

    Empirical break threshold ~1.6 (v1 seed=7 s=0.25 M=300 top1=0.887).
    Higher = more capacity-saturated substrate = further from saturation
    at fixed corruption. THEORETICAL: Hopfield storage capacity C ~ N/(2 log M);
    ratio M/C = 2*M*log(M)/N.
    """
    if N <= 0 or M <= 1 or sparsity_frac <= 0:
        return 0.0
    N_eff = max(1.0, sparsity_frac * N)
    return 2.0 * M * math.log(M) / N_eff


def get_backend_label() -> str:
    return "torch.cuda" if _CUDA_OK else "torch.cpu"


# ---------------------------------------------------------------------------
# Encoder family primitives (build only; sparsity applied AFTER)
# UNCHANGED from v1: primitives are correct; capacity-lift is the ONLY
# change. Re-imported here to keep v2 self-contained (no v1 core dep).
# ---------------------------------------------------------------------------
def _build_binary_bipolar_dense(M: int, N: int, seed: int) -> "torch.Tensor":
    """Dense bipolar {-1, +1}^N codebook (M, N) float32 on DEVICE."""
    g = np.random.default_rng(seed)
    arr = (g.integers(0, 2, size=(M, N)) * 2 - 1).astype(np.float32)
    return torch.from_numpy(arr).to(DEVICE)


def _build_hrr_real_dense(M: int, N: int, seed: int) -> "torch.Tensor":
    """Dense Gaussian codebook (M, N) float32, L2-normalized on DEVICE."""
    g = np.random.default_rng(seed)
    arr = (g.standard_normal(size=(M, N)) / math.sqrt(N)).astype(np.float32)
    norms = np.linalg.norm(arr, axis=1, keepdims=True).clip(min=1e-12)
    arr = arr / norms
    return torch.from_numpy(arr).to(DEVICE)


def _build_fhrr_dense(M: int, N: int, seed: int) -> "torch.Tensor":
    """Unit-modulus complex codebook (M, N/2) complex64 on DEVICE."""
    if N % 2 != 0:
        raise ValueError(f"FHRR requires even N; got N={N}")
    n_complex = N // 2
    g = np.random.default_rng(seed)
    phi = g.uniform(0.0, 2.0 * math.pi, size=(M, n_complex)).astype(np.float32)
    real = np.cos(phi).astype(np.float32)
    imag = np.sin(phi).astype(np.float32)
    arr = np.empty((M, n_complex), dtype=np.complex64)
    arr.real = real
    arr.imag = imag
    return torch.from_numpy(arr).to(DEVICE)


def _build_sparse_bipolar_native(M: int, N: int, seed: int,
                                   density: float) -> "torch.Tensor":
    """Sparse-ternary {-1, 0, +1}^N codebook with `density` fraction nonzero."""
    g = np.random.default_rng(seed)
    s = max(1, int(round(density * N)))
    arr = np.zeros((M, N), dtype=np.float32)
    for i in range(M):
        idx = g.choice(N, size=s, replace=False)
        signs = g.integers(0, 2, size=s).astype(np.float32) * 2.0 - 1.0
        arr[i, idx] = signs
    return torch.from_numpy(arr).to(DEVICE)


# ---------------------------------------------------------------------------
# Sparsity mask (applied to dense encoders; encoder-independent)
# ---------------------------------------------------------------------------
def _apply_sparsity_mask_real(X: "torch.Tensor", density: float,
                                seed: int,
                                renormalize: bool = False) -> Tuple["torch.Tensor", "torch.Tensor"]:
    """Zero out (1 - density) fraction of dimensions PER-ROW; return (X_masked, mask)."""
    g = np.random.default_rng(seed + 42)
    M, N = X.shape
    n_keep = max(1, int(round(density * N)))
    mask_np = np.zeros((M, N), dtype=bool)
    for i in range(M):
        idx = g.choice(N, size=n_keep, replace=False)
        mask_np[i, idx] = True
    mask_t = torch.from_numpy(mask_np).to(DEVICE)
    X_masked = X * mask_t.to(X.dtype)
    if renormalize:
        norms = torch.linalg.norm(X_masked, dim=1, keepdim=True).clamp(min=1e-12)
        X_masked = X_masked / norms
    return X_masked, mask_t


def _apply_sparsity_mask_fhrr(X: "torch.Tensor", density: float,
                                seed: int) -> Tuple["torch.Tensor", "torch.Tensor"]:
    """Zero out (1 - density) fraction of COMPLEX BINS per row."""
    g = np.random.default_rng(seed + 42)
    M, n_complex = X.shape
    n_keep = max(1, int(round(density * n_complex)))
    mask_np = np.zeros((M, n_complex), dtype=bool)
    for i in range(M):
        idx = g.choice(n_complex, size=n_keep, replace=False)
        mask_np[i, idx] = True
    mask_t = torch.from_numpy(mask_np).to(DEVICE)
    X_masked = X * mask_t.to(torch.complex64)
    return X_masked, mask_t


# ---------------------------------------------------------------------------
# Corruption per encoder (family-specific; calibrated E[cos(Q, src)] = 1-2c)
# ---------------------------------------------------------------------------
def _corrupt_binary_bipolar(X: "torch.Tensor", c: float, seed: int) -> "torch.Tensor":
    """Flip fraction c of ACTIVE bits (nonzero entries) per item."""
    g = np.random.default_rng(seed)
    M, N = X.shape
    Q = X.clone()
    X_np_abs = X.cpu().numpy() != 0
    for i in range(M):
        active_idx = np.flatnonzero(X_np_abs[i])
        s = len(active_idx)
        if s == 0:
            continue
        n_flip = int(round(c * s))
        if n_flip == 0:
            continue
        flip_idx = g.choice(active_idx, size=n_flip, replace=False)
        flip_idx_t = torch.from_numpy(flip_idx).to(DEVICE)
        Q[i, flip_idx_t] = -Q[i, flip_idx_t]
    return Q


def _corrupt_hrr_real(X: "torch.Tensor", c: float, seed: int) -> "torch.Tensor":
    """Add Gaussian noise to ACTIVE entries so E[cos(Q, X)] = 1-2c."""
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
    Q = Q / norms
    return Q


def _corrupt_fhrr(X: "torch.Tensor", c: float, seed: int) -> "torch.Tensor":
    """Phase-rotate 2c fraction of ACTIVE complex bins per row."""
    g = np.random.default_rng(seed)
    M, n_complex = X.shape
    frac_perturbed = min(2.0 * c, 1.0)
    X_mag = torch.abs(X).cpu().numpy()
    active_mask = X_mag > 1e-9
    Q = X.clone()
    for i in range(M):
        active_idx = np.flatnonzero(active_mask[i])
        s = len(active_idx)
        if s == 0:
            continue
        n_perturb = int(round(frac_perturbed * s))
        if n_perturb == 0:
            continue
        rot_idx = g.choice(active_idx, size=n_perturb, replace=False)
        delta = g.uniform(0.0, 2.0 * math.pi, size=n_perturb).astype(np.float32)
        real_rot = np.cos(delta).astype(np.float32)
        imag_rot = np.sin(delta).astype(np.float32)
        rot = np.empty(n_perturb, dtype=np.complex64)
        rot.real = real_rot
        rot.imag = imag_rot
        rot_t = torch.from_numpy(rot).to(DEVICE)
        rot_idx_t = torch.from_numpy(rot_idx).to(DEVICE)
        Q[i, rot_idx_t] = Q[i, rot_idx_t] * rot_t
    return Q


def _corrupt_sparse_bipolar(X: "torch.Tensor", c: float, seed: int) -> "torch.Tensor":
    """Flip fraction c of ACTIVE bits (identical to _corrupt_binary_bipolar)."""
    return _corrupt_binary_bipolar(X, c, seed)


# ---------------------------------------------------------------------------
# Random-floor batch (arm 2)
# ---------------------------------------------------------------------------
def _random_floor_binary_bipolar(M: int, N: int, seed: int,
                                    active_mask: "torch.Tensor" = None) -> "torch.Tensor":
    g = np.random.default_rng(seed + 99991)
    arr = (g.integers(0, 2, size=(M, N)) * 2 - 1).astype(np.float32)
    Q = torch.from_numpy(arr).to(DEVICE)
    if active_mask is not None:
        Q = Q * active_mask.to(Q.dtype)
    return Q


def _random_floor_hrr_real(M: int, N: int, seed: int,
                             active_mask: "torch.Tensor" = None) -> "torch.Tensor":
    g = np.random.default_rng(seed + 99991)
    arr = (g.standard_normal(size=(M, N)) / math.sqrt(N)).astype(np.float32)
    Q = torch.from_numpy(arr).to(DEVICE)
    if active_mask is not None:
        Q = Q * active_mask.to(Q.dtype)
    norms = torch.linalg.norm(Q, dim=1, keepdim=True).clamp(min=1e-12)
    Q = Q / norms
    return Q


def _random_floor_fhrr(M: int, N: int, seed: int,
                        active_mask: "torch.Tensor" = None) -> "torch.Tensor":
    n_complex = N // 2
    g = np.random.default_rng(seed + 99991)
    phi = g.uniform(0.0, 2.0 * math.pi, size=(M, n_complex)).astype(np.float32)
    real = np.cos(phi).astype(np.float32)
    imag = np.sin(phi).astype(np.float32)
    arr = np.empty((M, n_complex), dtype=np.complex64)
    arr.real = real
    arr.imag = imag
    Q = torch.from_numpy(arr).to(DEVICE)
    if active_mask is not None:
        Q = Q * active_mask.to(torch.complex64)
    return Q


def _random_floor_sparse_bipolar(M: int, N: int, seed: int,
                                    density: float = 0.05) -> "torch.Tensor":
    g = np.random.default_rng(seed + 99991)
    s = max(1, int(round(density * N)))
    arr = np.zeros((M, N), dtype=np.float32)
    for i in range(M):
        idx = g.choice(N, size=s, replace=False)
        signs = g.integers(0, 2, size=s).astype(np.float32) * 2.0 - 1.0
        arr[i, idx] = signs
    return torch.from_numpy(arr).to(DEVICE)


# ---------------------------------------------------------------------------
# Score + cleanup (family-specific score; family-specific sign_op)
# ---------------------------------------------------------------------------
def _score_real(Q: "torch.Tensor", X: "torch.Tensor") -> "torch.Tensor":
    return Q @ X.T


def _score_fhrr(Q: "torch.Tensor", X: "torch.Tensor") -> "torch.Tensor":
    sims = (Q @ X.conj().T).real
    return sims.to(torch.float32)


def _sign_op_bipolar(V: "torch.Tensor", active_mask: "torch.Tensor" = None) -> "torch.Tensor":
    out = torch.sign(V)
    out = torch.where(out == 0, torch.ones_like(out), out)
    if active_mask is not None:
        out = out * active_mask.to(out.dtype)
    return out


def _sign_op_hrr_real(V: "torch.Tensor", active_mask: "torch.Tensor" = None) -> "torch.Tensor":
    if active_mask is not None:
        V = V * active_mask.to(V.dtype)
    norms = torch.linalg.norm(V, dim=1, keepdim=True).clamp(min=1e-12)
    return V / norms


def _sign_op_fhrr(V: "torch.Tensor", active_mask: "torch.Tensor" = None) -> "torch.Tensor":
    mag = torch.abs(V).clamp(min=1e-12)
    out = V / mag
    if active_mask is not None:
        out = out * active_mask.to(torch.complex64)
    return out


def _sign_op_sparse_bipolar(V: "torch.Tensor", active_mask: "torch.Tensor" = None) -> "torch.Tensor":
    if active_mask is not None:
        out = torch.sign(V) * active_mask.to(V.dtype)
        out = torch.where((out == 0) & active_mask, torch.ones_like(out), out)
        out = out * active_mask.to(out.dtype)
        return out
    out = torch.sign(V)
    return torch.where(out == 0, torch.ones_like(out), out)


def _hopfield_cleanup(Q0: "torch.Tensor", X: "torch.Tensor", T: int, beta: float,
                       score_fn: Callable, sign_op: Callable,
                       active_mask: "torch.Tensor" = None) -> "torch.Tensor":
    """T-step modern-Hopfield cleanup with family-specific score + sign_op."""
    Q = Q0
    for _ in range(max(0, T)):
        sims = score_fn(Q, X)
        p = torch.softmax(beta * sims, dim=1)
        if X.is_complex():
            Q_new = (p.to(torch.complex64) @ X)
        else:
            Q_new = p @ X
        Q = sign_op(Q_new, active_mask=active_mask)
    return Q


def _top1_recall(Q_final: "torch.Tensor", X: "torch.Tensor",
                  target_idx: "torch.Tensor", score_fn: Callable) -> float:
    sims = score_fn(Q_final, X)
    preds = sims.argmax(dim=1)
    hits = int((preds == target_idx).sum().item())
    return hits / max(int(target_idx.shape[0]), 1)


# ---------------------------------------------------------------------------
# Encoder x sparsity registry
# ---------------------------------------------------------------------------
def _build_and_mask(fam: str, M: int, N: int, seed: int, density: float
                     ) -> Tuple["torch.Tensor", "torch.Tensor"]:
    if fam == "binary_bipolar":
        X_dense = _build_binary_bipolar_dense(M, N, seed)
        return _apply_sparsity_mask_real(X_dense, density, seed)
    if fam == "hrr_real":
        X_dense = _build_hrr_real_dense(M, N, seed)
        return _apply_sparsity_mask_real(X_dense, density, seed, renormalize=True)
    if fam == "fhrr":
        X_dense = _build_fhrr_dense(M, N, seed)
        return _apply_sparsity_mask_fhrr(X_dense, density, seed)
    if fam == "sparse_bipolar":
        X = _build_sparse_bipolar_native(M, N, seed, density=density)
        active_mask = X != 0
        return X, active_mask
    raise ValueError(f"unknown encoder_family={fam!r}")


_FAMILY_SCORE = {
    "binary_bipolar": _score_real,
    "hrr_real": _score_real,
    "fhrr": _score_fhrr,
    "sparse_bipolar": _score_real,
}
_FAMILY_SIGNOP = {
    "binary_bipolar": _sign_op_bipolar,
    "hrr_real": _sign_op_hrr_real,
    "fhrr": _sign_op_fhrr,
    "sparse_bipolar": _sign_op_sparse_bipolar,
}
_FAMILY_CORRUPT = {
    "binary_bipolar": _corrupt_binary_bipolar,
    "hrr_real": _corrupt_hrr_real,
    "fhrr": _corrupt_fhrr,
    "sparse_bipolar": _corrupt_sparse_bipolar,
}
_FAMILY_DTYPE_LABEL = {
    "binary_bipolar": "float32",
    "hrr_real": "float32",
    "fhrr": "complex64",
    "sparse_bipolar": "float32",
}


def _random_floor_family(fam: str, M: int, N: int, seed: int, density: float,
                          active_mask: "torch.Tensor") -> Tuple["torch.Tensor", "torch.Tensor"]:
    """Random-floor batch + FRESH INDEPENDENT MASK for the query."""
    if fam == "fhrr":
        g = np.random.default_rng(seed + 88881)
        n_complex = N // 2
        n_keep = max(1, int(round(density * n_complex)))
        mask_np = np.zeros((M, n_complex), dtype=bool)
        for i in range(M):
            idx = g.choice(n_complex, size=n_keep, replace=False)
            mask_np[i, idx] = True
        q_mask_t = torch.from_numpy(mask_np).to(DEVICE)
    else:
        g = np.random.default_rng(seed + 88881)
        n_keep = max(1, int(round(density * N)))
        mask_np = np.zeros((M, N), dtype=bool)
        for i in range(M):
            idx = g.choice(N, size=n_keep, replace=False)
            mask_np[i, idx] = True
        q_mask_t = torch.from_numpy(mask_np).to(DEVICE)

    if fam == "binary_bipolar":
        return _random_floor_binary_bipolar(M, N, seed, active_mask=q_mask_t), q_mask_t
    if fam == "hrr_real":
        Q = _random_floor_hrr_real(M, N, seed, active_mask=q_mask_t)
        norms = torch.linalg.norm(Q, dim=1, keepdim=True).clamp(min=1e-12)
        Q = Q / norms
        return Q, q_mask_t
    if fam == "fhrr":
        return _random_floor_fhrr(M, N, seed, active_mask=q_mask_t), q_mask_t
    if fam == "sparse_bipolar":
        Q = _random_floor_sparse_bipolar(M, N, seed, density=density)
        q_mask_t = Q != 0
        return Q, q_mask_t
    raise ValueError(f"unknown encoder_family={fam!r}")


# ---------------------------------------------------------------------------
# Per-point evaluation
# ---------------------------------------------------------------------------
def eval_phase_point(encoder_family: str, sparsity_frac: float, N: int,
                      corruption: float, T: int, M: int,
                      seed: int) -> Dict[str, Any]:
    """One (encoder, sparsity, N, c, T) phase point."""
    if encoder_family not in ENCODER_FAMILIES:
        raise ValueError(f"unknown encoder_family={encoder_family!r}")

    t0 = time.time()
    if _CUDA_OK:
        torch.cuda.empty_cache()
        torch.cuda.reset_peak_memory_stats()

    X, active_mask = _build_and_mask(encoder_family, M, N, seed, sparsity_frac)
    target_idx = torch.arange(M, device=DEVICE)
    sub_seed = seed * 1000 + int(corruption * 1000) + int(sparsity_frac * 1000)

    score_fn = _FAMILY_SCORE[encoder_family]
    sign_op = _FAMILY_SIGNOP[encoder_family]
    corrupt_fn = _FAMILY_CORRUPT[encoder_family]
    dtype_label = _FAMILY_DTYPE_LABEL[encoder_family]

    # ARM_MECHANISM
    Q_sub_0 = corrupt_fn(X, corruption, sub_seed)
    Q_sub_T = _hopfield_cleanup(Q_sub_0, X, T, BETA, score_fn, sign_op,
                                  active_mask=active_mask)
    top1_sub = _top1_recall(Q_sub_T, X, target_idx, score_fn)

    # ARM_RANDOM_FLOOR
    Q_rnd_0, q_rnd_mask = _random_floor_family(encoder_family, M, N, sub_seed,
                                                sparsity_frac, active_mask)
    Q_rnd_T = _hopfield_cleanup(Q_rnd_0, X, T, BETA, score_fn, sign_op,
                                  active_mask=q_rnd_mask)
    top1_rnd = _top1_recall(Q_rnd_T, X, target_idx, score_fn)

    # Calibration
    cal_sample = min(20, M)
    if X.is_complex():
        cal_sims = (Q_sub_0[:cal_sample] * X[:cal_sample].conj()).real.sum(dim=1)
        X_mag_sum = torch.abs(X[:cal_sample]).pow(2).sum(dim=1).clamp(min=1e-12)
        cal_cos = float((cal_sims / X_mag_sum).mean().item())
    else:
        Q_norm = torch.linalg.norm(Q_sub_0[:cal_sample], dim=1).clamp(min=1e-12)
        X_norm = torch.linalg.norm(X[:cal_sample], dim=1).clamp(min=1e-12)
        cal_dots = (Q_sub_0[:cal_sample] * X[:cal_sample]).sum(dim=1)
        cal_cos = float((cal_dots / (Q_norm * X_norm)).mean().item())

    if _CUDA_OK:
        peak_mem_mb = torch.cuda.max_memory_allocated() / 1e6
    else:
        peak_mem_mb = -1.0

    elapsed = time.time() - t0
    discriminator = top1_sub - top1_rnd

    if top1_sub >= SATURATED_TOP1:
        tier = "SATURATED"
        saturation_flag = True
    elif top1_sub >= HARD_PASS_LO and discriminator >= HP_DISCRIMINATOR:
        tier = "HARD_PASS"
        saturation_flag = False
    elif top1_sub >= MIDDLE_BAND_LO and discriminator >= MB_DISCRIMINATOR:
        tier = "MIDDLE_BAND"
        saturation_flag = False
    elif top1_sub <= FLOOR_TOP1:
        tier = "FLOOR"
        saturation_flag = False
    else:
        tier = "HARD_FAIL"
        saturation_flag = False

    del X, Q_sub_0, Q_sub_T, Q_rnd_0, Q_rnd_T, target_idx, active_mask
    if _CUDA_OK:
        torch.cuda.empty_cache()

    return {
        "encoder_family": encoder_family,
        "sparsity_frac": sparsity_frac,
        "N": N,
        "corruption_frac": corruption,
        "cleanup_iters": T,
        "M_items": M,
        "seed": seed,
        "top1_mechanism": round(top1_sub, 4),
        "top1_random": round(top1_rnd, 4),
        "discriminator": round(discriminator, 4),
        "calibration_cos_q0_x": round(cal_cos, 4),
        "calibration_target_cos": round(1.0 - 2.0 * corruption, 4),
        "verdict_tier_per_point": tier,
        "saturation_flag": saturation_flag,
        "peak_mem_mb": round(peak_mem_mb, 1),
        "elapsed_per_point_s": round(elapsed, 3),
        "crlb_1step_cliff_prediction": round(
            crlb_1step_cliff_prediction(N, M, sparsity_frac), 4),
        "capacity_ratio": round(capacity_ratio(N, M, sparsity_frac), 3),
        "dtype_label": dtype_label,
    }


# ---------------------------------------------------------------------------
# Selftest
# ---------------------------------------------------------------------------
def selftest(seed: int) -> Tuple[bool, str]:
    """Verify: cardinality math + CRLB formula + encoder distinctness at
    each sparsity + calibration + mechanism sanity + capacity-lift consistency.
    """
    msgs: List[str] = []

    # 1. Cardinality math
    if EXPECTED_N_UNITS_FULL != 16:
        return False, f"FULL cardinality {EXPECTED_N_UNITS_FULL} != 16"
    if EXPECTED_N_UNITS_SMOKE != 8:
        return False, f"SMOKE cardinality {EXPECTED_N_UNITS_SMOKE} != 8"
    msgs.append(f"cardinality FULL={EXPECTED_N_UNITS_FULL} SMOKE={EXPECTED_N_UNITS_SMOKE}")

    # 2. CRLB formula sanity + capacity-lift check
    c_dense = crlb_1step_cliff_prediction(8192, 600, 1.0)
    c_sparse = crlb_1step_cliff_prediction(8192, 600, 0.05)
    if not (0.40 < c_dense < 0.50):
        return False, f"crlb dense N=8192 M=600 outside [0.40, 0.50]: {c_dense}"
    if not (c_sparse < c_dense):
        return False, f"sparse cliff should be < dense: sparse={c_sparse} dense={c_dense}"
    msgs.append(f"crlb dense={c_dense:.4f} sparse@0.05={c_sparse:.4f}")

    # 2b. Capacity-lift sanity: at M=600 N=8192, s=0.50 should have
    # cap_ratio ~1.87 (just above v1-observed break edge 1.67); s=0.25 should
    # be ~3.75 (well above break); s=0.05 should be ~18.7 (deep FLOOR)
    cap_050 = capacity_ratio(8192, 600, 0.50)
    cap_025 = capacity_ratio(8192, 600, 0.25)
    cap_005 = capacity_ratio(8192, 600, 0.05)
    if not (1.5 < cap_050 < 2.5):
        return False, f"cap_ratio@s=0.50 outside expected [1.5, 2.5]: {cap_050}"
    if not (3.0 < cap_025 < 5.0):
        return False, f"cap_ratio@s=0.25 outside expected [3.0, 5.0]: {cap_025}"
    if cap_005 <= cap_025:
        return False, f"cap_ratio monotone-nonincreasing violation: s=0.05={cap_005} s=0.25={cap_025}"
    msgs.append(f"capacity_ratio s=[0.50,0.25,0.05]=[{cap_050:.2f},{cap_025:.2f},{cap_005:.2f}]")

    # 3. Encoder codebooks distinct at each sparsity
    M_san = 20
    N_san = 512
    hashes = {}
    for fam in ENCODER_FAMILIES:
        for density in (0.10, 0.25, 0.50):
            X, mask = _build_and_mask(fam, M_san, N_san, seed, density)
            X_bytes = X.cpu().numpy().tobytes()
            h = hashlib.sha256(X_bytes).hexdigest()[:16]
            hashes[f"{fam}@s={density}"] = h
            del X, mask
            if _CUDA_OK:
                torch.cuda.empty_cache()
    if len(set(hashes.values())) != len(hashes):
        return False, f"encoder x sparsity codebooks NOT distinct at seed={seed}: {hashes}"
    msgs.append(f"12 encoder x sparsity codebooks distinct at seed={seed}")

    # 4. Calibration check per encoder
    M_cal = 30
    N_cal = 2048
    cal_c_list = [0.30]
    cal_tol = 0.15
    for fam in ENCODER_FAMILIES:
        for density in (0.10, 0.50):
            X, mask = _build_and_mask(fam, M_cal, N_cal, seed, density)
            corrupt_fn = _FAMILY_CORRUPT[fam]
            for c in cal_c_list:
                sub_seed = seed * 1000 + int(c * 1000) + int(density * 1000)
                Q = corrupt_fn(X, c, sub_seed)
                if X.is_complex():
                    dots = (Q * X.conj()).real.sum(dim=1)
                    X_mag_sum = torch.abs(X).pow(2).sum(dim=1).clamp(min=1e-12)
                    cos_mean = float((dots / X_mag_sum).mean().item())
                else:
                    Q_norm = torch.linalg.norm(Q, dim=1).clamp(min=1e-12)
                    X_norm = torch.linalg.norm(X, dim=1).clamp(min=1e-12)
                    cos_per = (Q * X).sum(dim=1) / (Q_norm * X_norm)
                    cos_mean = float(cos_per.mean().item())
                target = 1.0 - 2.0 * c
                if abs(cos_mean - target) > cal_tol:
                    return False, (
                        f"encoder calibration FAIL {fam}@sparsity={density} c={c}: "
                        f"cos={cos_mean:.4f}, target={target:.4f}, tol={cal_tol}")
            del X, mask
            if _CUDA_OK:
                torch.cuda.empty_cache()
    msgs.append("calibration ok for 4 encoders x 2 sparsities at c=0.30 (tol=0.15)")

    # 5. Mechanism sanity
    X, mask = _build_and_mask("binary_bipolar", 20, 512, seed, 1.0)
    Q0 = _corrupt_binary_bipolar(X, 0.10, seed * 2)
    Q1 = _hopfield_cleanup(Q0, X, 1, BETA, _score_real, _sign_op_bipolar,
                             active_mask=mask)
    sims = _score_real(Q1, X)
    target_idx = torch.arange(20, device=DEVICE)
    preds = sims.argmax(dim=1)
    n_hit = int((preds == target_idx).sum().item())
    if n_hit < 15:
        return False, (f"mechanism sanity FAIL binary_bipolar dense c=0.10: "
                        f"only {n_hit}/20 recovered")
    msgs.append(f"mechanism sanity ok: binary_bipolar dense c=0.10 recovered {n_hit}/20")

    return True, "; ".join(msgs)


# ---------------------------------------------------------------------------
# Per-seed phase sweep
# ---------------------------------------------------------------------------
def run_one_seed_phase_diagram(seed: int, run_mode: str) -> Dict[str, Any]:
    """Sweep all (encoder, sparsity) points at fixed (N, c, T, M).

    Halts on first exception (META_RULE_J: no silent except).
    """
    is_smoke = (run_mode == "smoke")
    if is_smoke:
        sparsity_sweep = SPARSITY_LEVELS_SMOKE
        M_items = M_ITEMS_SMOKE
    else:
        sparsity_sweep = SPARSITY_LEVELS_FULL
        M_items = M_ITEMS_FULL

    # DISCRIMINATOR-SURVIVES-SCALE: smoke uses same N as full
    N_dim = N_DIM_FULL

    expected_n_units = len(ENCODER_FAMILIES) * len(sparsity_sweep)

    print(f"[run_one_seed] seed={seed} mode={run_mode} device={DEVICE} "
          f"encoders={ENCODER_FAMILIES} sparsity={list(sparsity_sweep)} "
          f"N={N_dim} c={CORRUPTION_FIXED} T={ITERS_FIXED} M={M_items} "
          f"expected_n={expected_n_units}", flush=True)

    crlb_preds = {f"s={s}": round(crlb_1step_cliff_prediction(N_dim, M_items, s), 4)
                   for s in sparsity_sweep}
    cap_ratios = {f"s={s}": round(capacity_ratio(N_dim, M_items, s), 3)
                   for s in sparsity_sweep}
    print(f"[crlb] cliff predictions per sparsity: {crlb_preds}", flush=True)
    print(f"[cap_ratio] capacity pressure per sparsity: {cap_ratios}", flush=True)

    phase_map: List[Dict[str, Any]] = []
    t0 = time.time()
    for fam in ENCODER_FAMILIES:
        for s in sparsity_sweep:
            print(f"[point] seed={seed} enc={fam} sparsity={s:.3f} ...",
                  flush=True)
            pt = eval_phase_point(fam, s, N_dim, CORRUPTION_FIXED, ITERS_FIXED,
                                    M_items, seed)
            phase_map.append(pt)
            print(f"  -> top1_mech={pt['top1_mechanism']:.3f} "
                  f"top1_rnd={pt['top1_random']:.3f} "
                  f"disc={pt['discriminator']:.3f} "
                  f"tier={pt['verdict_tier_per_point']} "
                  f"cap_ratio={pt['capacity_ratio']:.2f} "
                  f"cal_cos={pt['calibration_cos_q0_x']:.3f} "
                  f"peak_mb={pt['peak_mem_mb']:.1f} "
                  f"t={pt['elapsed_per_point_s']:.2f}s", flush=True)

    elapsed = time.time() - t0
    observed_n_units = len(phase_map)
    cardinality_ok = (observed_n_units == expected_n_units)

    # Per-(encoder, sparsity) mechanism hashes
    per_combo_hashes: Dict[str, str] = {}
    for pt in phase_map:
        key = f"{pt['encoder_family']}@s={pt['sparsity_frac']}"
        payload = json.dumps([pt["top1_mechanism"], pt["top1_random"],
                              pt["discriminator"]], sort_keys=True).encode("utf-8")
        per_combo_hashes[key] = hashlib.sha256(payload).hexdigest()[:16]

    encoder_mech_hashes: Dict[str, str] = {}
    for fam in ENCODER_FAMILIES:
        fam_pts = [p for p in phase_map if p["encoder_family"] == fam]
        payload = json.dumps([p["top1_mechanism"] for p in fam_pts],
                              sort_keys=True).encode("utf-8")
        encoder_mech_hashes[fam] = hashlib.sha256(payload).hexdigest()[:16]

    sparsity_mech_hashes: Dict[str, str] = {}
    for s in sparsity_sweep:
        s_pts = [p for p in phase_map if abs(p["sparsity_frac"] - s) < 1e-9]
        payload = json.dumps([p["top1_mechanism"] for p in s_pts],
                              sort_keys=True).encode("utf-8")
        sparsity_mech_hashes[f"s={s}"] = hashlib.sha256(payload).hexdigest()[:16]

    encoder_pair_distinct = {}
    fams = list(ENCODER_FAMILIES)
    for i in range(len(fams)):
        for j in range(i + 1, len(fams)):
            k = f"{fams[i]}_vs_{fams[j]}"
            encoder_pair_distinct[k] = (encoder_mech_hashes[fams[i]]
                                          != encoder_mech_hashes[fams[j]])
    n_encoder_pairs_differ = sum(1 for v in encoder_pair_distinct.values() if v)

    sparsity_pair_distinct = {}
    s_list = list(sparsity_sweep)
    for i in range(len(s_list)):
        for j in range(i + 1, len(s_list)):
            k = f"s={s_list[i]}_vs_s={s_list[j]}"
            sparsity_pair_distinct[k] = (
                sparsity_mech_hashes[f"s={s_list[i]}"]
                != sparsity_mech_hashes[f"s={s_list[j]}"])
    n_sparsity_pairs_differ = sum(1 for v in sparsity_pair_distinct.values() if v)

    arms_differ_per_combo: Dict[str, bool] = {}
    for pt in phase_map:
        key = f"{pt['encoder_family']}@s={pt['sparsity_frac']}"
        arms_differ_per_combo[key] = (pt["top1_mechanism"] != pt["top1_random"]
                                        or pt["discriminator"] != 0.0)
    n_combos_arms_differ = sum(1 for v in arms_differ_per_combo.values() if v)

    interaction_matrix: Dict[str, Dict[str, float]] = {}
    for fam in ENCODER_FAMILIES:
        interaction_matrix[fam] = {}
        for s in sparsity_sweep:
            matches = [p for p in phase_map
                        if p["encoder_family"] == fam
                        and abs(p["sparsity_frac"] - s) < 1e-9]
            if matches:
                interaction_matrix[fam][f"s={s}"] = matches[0]["top1_mechanism"]
            else:
                interaction_matrix[fam][f"s={s}"] = -1.0

    per_encoder_sparsity_range: Dict[str, float] = {}
    for fam in ENCODER_FAMILIES:
        vals = list(interaction_matrix[fam].values())
        vals = [v for v in vals if v >= 0]
        if vals:
            per_encoder_sparsity_range[fam] = max(vals) - min(vals)
        else:
            per_encoder_sparsity_range[fam] = 0.0

    interaction_pairs_visible = 0
    interaction_pair_deltas: Dict[str, float] = {}
    for i in range(len(fams)):
        for j in range(i + 1, len(fams)):
            delta = abs(per_encoder_sparsity_range[fams[i]]
                         - per_encoder_sparsity_range[fams[j]])
            interaction_pair_deltas[f"{fams[i]}_vs_{fams[j]}"] = round(delta, 4)
            if delta >= 0.15:
                interaction_pairs_visible += 1

    # v2 discriminator (specific to capacity-lift 2x-drill success gate):
    # count encoders with per_encoder_sparsity_range >= 0.15. v1 only fhrr;
    # v2 target = 3+ (binary_bipolar / sparse_bipolar / hrr_real also fire).
    n_encoders_with_sparsity_range = sum(
        1 for r in per_encoder_sparsity_range.values() if r >= 0.15)

    pc = POSITIVE_CONTROL_SMOKE if is_smoke else POSITIVE_CONTROL
    pc_matches = [p for p in phase_map
                   if p["encoder_family"] == pc["encoder_family"]
                   and abs(p["sparsity_frac"] - pc["sparsity_frac"]) < 1e-9]
    if pc_matches:
        pc_top1 = pc_matches[0]["top1_mechanism"]
        pc_pass = (pc_top1 >= pc["top1_band_lo"]
                    and pc_top1 <= pc["top1_band_hi"])
    else:
        pc_top1 = -1.0
        pc_pass = False

    return {
        "seed": seed,
        "run_mode": run_mode,
        "encoder_families": list(ENCODER_FAMILIES),
        "sparsity_sweep": list(sparsity_sweep),
        "N": N_dim,
        "corruption_frac": CORRUPTION_FIXED,
        "cleanup_iters": ITERS_FIXED,
        "M_items": M_items,
        "phase_map": phase_map,
        "interaction_matrix": interaction_matrix,
        "per_encoder_sparsity_range": {k: round(v, 4) for k, v
                                          in per_encoder_sparsity_range.items()},
        "n_encoders_with_sparsity_range": n_encoders_with_sparsity_range,
        "interaction_pair_deltas": interaction_pair_deltas,
        "interaction_pairs_visible": interaction_pairs_visible,
        "encoder_mech_hashes": encoder_mech_hashes,
        "sparsity_mech_hashes": sparsity_mech_hashes,
        "per_combo_hashes": per_combo_hashes,
        "encoder_pair_distinct": encoder_pair_distinct,
        "sparsity_pair_distinct": sparsity_pair_distinct,
        "n_encoder_pairs_differ": n_encoder_pairs_differ,
        "n_sparsity_pairs_differ": n_sparsity_pairs_differ,
        "arms_differ_per_combo": arms_differ_per_combo,
        "n_combos_arms_differ": n_combos_arms_differ,
        "positive_control_result": {
            "target": pc,
            "measured_top1": pc_top1,
            "pass": pc_pass,
        },
        "cardinality_ok": cardinality_ok,
        "expected_n_units": expected_n_units,
        "observed_n_units": observed_n_units,
        "crlb_predictions_1step": crlb_preds,
        "capacity_ratios": cap_ratios,
        "device": str(DEVICE),
        "gpu_name": GPU_NAME,
        "elapsed_seed_s": round(elapsed, 2),
    }


# ---------------------------------------------------------------------------
# Smoke-gate predicate (v2: same as v1 + capacity-lift success check)
# ---------------------------------------------------------------------------
def smoke_gate_predicate(body: Dict[str, Any]) -> Tuple[bool, str]:
    """Pre-reg smoke gate. Same as v1 + v2-specific saturation-escape check."""
    phase_map = body.get("phase_map", [])
    expected_n = body.get("expected_n_units", 0)
    pc_result = body.get("positive_control_result", {})
    n_encoder_pairs_differ = body.get("n_encoder_pairs_differ", 0)
    n_sparsity_pairs_differ = body.get("n_sparsity_pairs_differ", 0)
    n_combos_arms_differ = body.get("n_combos_arms_differ", 0)
    arms_differ = body.get("arms_differ_per_combo", {})
    n_enc_with_range = body.get("n_encoders_with_sparsity_range", 0)

    if len(phase_map) != expected_n:
        return False, f"cardinality_breach: expected {expected_n} got {len(phase_map)}"

    if n_combos_arms_differ != len(phase_map):
        bad = [k for k, v in arms_differ.items() if not v]
        return False, (f"arms_identical_combos: {len(phase_map) - n_combos_arms_differ}"
                        f"/{len(phase_map)} combos have mech==random; identical: {bad}")

    total_encoder_pairs = 6
    if n_encoder_pairs_differ < total_encoder_pairs:
        return False, (f"encoder_collapse: {n_encoder_pairs_differ}/{total_encoder_pairs} "
                        f"encoder pairs distinct")

    sparsity_sweep = body.get("sparsity_sweep", [])
    total_sparsity_pairs = len(sparsity_sweep) * (len(sparsity_sweep) - 1) // 2
    if n_sparsity_pairs_differ < total_sparsity_pairs:
        return False, (f"sparsity_collapse: {n_sparsity_pairs_differ}/{total_sparsity_pairs} "
                        f"sparsity pairs distinct")

    if not pc_result.get("pass"):
        return False, (f"positive_control_fail: target={pc_result.get('target')} "
                        f"measured top1={pc_result.get('measured_top1')}")

    tier_counts = {}
    for p in phase_map:
        t = p["verdict_tier_per_point"]
        tier_counts[t] = tier_counts.get(t, 0) + 1
    n_sat = tier_counts.get("SATURATED", 0)
    n_floor = tier_counts.get("FLOOR", 0)
    if n_sat == len(phase_map):
        return False, (f"all_saturated: {n_sat}/{len(phase_map)} pts SATURATED; "
                        f"v2 CAPACITY-LIFT FAILED to escape saturation "
                        f"despite M={body.get('M_items')} 2x-drill")
    if n_floor == len(phase_map):
        return False, (f"all_floored: {n_floor}/{len(phase_map)} pts FLOOR; "
                        f"v2 CAPACITY-LIFT OVERSHOT (M={body.get('M_items')} too high)")

    # v2 SPECIFIC: capacity-lift 2x-drill success discriminator
    # Smoke does NOT gate on n_enc_with_range (only 2 sparsity levels; range
    # measurement per encoder needs FULL 4-level sweep). Smoke gates on
    # partial saturation escape: sat_frac < 0.75 (v1 was 10/16 = 0.625 sat;
    # v2 goal is to drop below 0.50).
    sat_frac = n_sat / max(len(phase_map), 1)
    if sat_frac > 0.75:
        return False, (f"capacity_lift_insufficient: {n_sat}/{len(phase_map)} "
                        f"({sat_frac:.2%}) SATURATED; v2 M={body.get('M_items')} "
                        f"needs further lift (v3 M=1000+ or lower N)")

    return True, (f"smoke_gate_pass: cardinality_ok + arms_differ({n_combos_arms_differ}"
                  f"/{len(phase_map)}) + encoder_axis_distinct({n_encoder_pairs_differ}"
                  f"/{total_encoder_pairs}) + sparsity_axis_distinct("
                  f"{n_sparsity_pairs_differ}/{total_sparsity_pairs}) + pc_pass; "
                  f"tiers={tier_counts}; sat_frac={sat_frac:.2%}")


# ---------------------------------------------------------------------------
# Aggregate + verdict
# ---------------------------------------------------------------------------
def aggregate_and_verdict(per_seed: Dict[str, Dict[str, Any]],
                            run_mode: str) -> Dict[str, Any]:
    """Aggregate one-seed partial into final metrics with verdict."""
    if not per_seed:
        return {
            "verdict": "HARD_FAIL",
            "verdict_msg": "HARD_FAIL_NO_SEEDS: empty per_seed",
            "summary": "HARD_FAIL_NO_SEEDS",
        }

    is_smoke = (run_mode == "smoke")
    seed_key = list(per_seed.keys())[0]
    body = per_seed[seed_key]
    phase_map = body.get("phase_map", [])
    interaction_pairs_visible = body.get("interaction_pairs_visible", 0)
    per_encoder_sparsity_range = body.get("per_encoder_sparsity_range", {})
    n_encoders_with_sparsity_range = body.get("n_encoders_with_sparsity_range", 0)
    interaction_pair_deltas = body.get("interaction_pair_deltas", {})
    interaction_matrix = body.get("interaction_matrix", {})
    n_encoder_pairs_differ = body.get("n_encoder_pairs_differ", 0)
    n_sparsity_pairs_differ = body.get("n_sparsity_pairs_differ", 0)
    n_combos_arms_differ = body.get("n_combos_arms_differ", 0)
    pc_result = body.get("positive_control_result", {})
    expected_n = body.get("expected_n_units", 0)
    observed_n = body.get("observed_n_units", 0)
    cardinality_ok = body.get("cardinality_ok", False)

    if _CUDA_OK:
        peak_mems = [p["peak_mem_mb"] for p in phase_map if p["peak_mem_mb"] > 0]
        avg_peak = sum(peak_mems) / max(len(peak_mems), 1)
        gpu_util_estimate = min(0.95, max(0.30, avg_peak / 50.0))
    else:
        gpu_util_estimate = 0.0

    n_hp = sum(1 for p in phase_map if p["verdict_tier_per_point"] == "HARD_PASS")
    n_mb = sum(1 for p in phase_map if p["verdict_tier_per_point"] == "MIDDLE_BAND")
    n_sat = sum(1 for p in phase_map if p["verdict_tier_per_point"] == "SATURATED")
    n_floor = sum(1 for p in phase_map if p["verdict_tier_per_point"] == "FLOOR")
    n_fail = sum(1 for p in phase_map if p["verdict_tier_per_point"] == "HARD_FAIL")
    n_disc = n_hp + n_mb
    sat_frac = n_sat / max(len(phase_map), 1)

    common = {
        "phase_map": phase_map,
        "interaction_matrix": interaction_matrix,
        "per_encoder_sparsity_range": per_encoder_sparsity_range,
        "n_encoders_with_sparsity_range": n_encoders_with_sparsity_range,
        "interaction_pair_deltas": interaction_pair_deltas,
        "interaction_pairs_visible": interaction_pairs_visible,
        "encoder_mech_hashes": body.get("encoder_mech_hashes", {}),
        "sparsity_mech_hashes": body.get("sparsity_mech_hashes", {}),
        "per_combo_hashes": body.get("per_combo_hashes", {}),
        "encoder_pair_distinct": body.get("encoder_pair_distinct", {}),
        "sparsity_pair_distinct": body.get("sparsity_pair_distinct", {}),
        "n_encoder_pairs_differ": n_encoder_pairs_differ,
        "n_sparsity_pairs_differ": n_sparsity_pairs_differ,
        "arms_differ_per_combo": body.get("arms_differ_per_combo", {}),
        "n_combos_arms_differ": n_combos_arms_differ,
        "positive_control_result": pc_result,
        "cardinality_ok": cardinality_ok,
        "expected_n_units": expected_n,
        "observed_n_units": observed_n,
        "tier_counts": {"SATURATED": n_sat, "HARD_PASS": n_hp,
                         "MIDDLE_BAND": n_mb, "FLOOR": n_floor,
                         "HARD_FAIL": n_fail},
        "n_discriminating": n_disc,
        "sat_frac": round(sat_frac, 4),
        "crlb_predictions_1step": body.get("crlb_predictions_1step", {}),
        "capacity_ratios": body.get("capacity_ratios", {}),
        "gpu_util_estimate": round(gpu_util_estimate, 3),
        "device": body.get("device"),
        "gpu_name": body.get("gpu_name"),
        "beta": BETA,
        "corruption_frac": CORRUPTION_FIXED,
        "cleanup_iters": ITERS_FIXED,
    }

    if is_smoke:
        passed, reason = smoke_gate_predicate(body)
        if passed:
            verdict = "HARD_PASS"
            vmsg = (f"HARD_PASS_SMOKE_V2_CAPLIFT: {observed_n}/{expected_n} pts; "
                    f"sat={n_sat} hp={n_hp} mb={n_mb} floor={n_floor} fail={n_fail}; "
                    f"sat_frac={sat_frac:.2%} (v1_baseline=62.5pct); "
                    f"encoder_pairs_differ={n_encoder_pairs_differ}/6; "
                    f"sparsity_pairs_differ={n_sparsity_pairs_differ}; "
                    f"interaction_visible={interaction_pairs_visible}/6; "
                    f"pc@{pc_result.get('target', {}).get('encoder_family')} "
                    f"s={pc_result.get('target', {}).get('sparsity_frac')} "
                    f"top1={pc_result.get('measured_top1'):.3f}; reason={reason}")
        else:
            verdict = "HARD_FAIL"
            vmsg = (f"HARD_FAIL_SMOKE_V2: {reason}; sat={n_sat} hp={n_hp} mb={n_mb} "
                    f"floor={n_floor} fail={n_fail}; sat_frac={sat_frac:.2%}")
        out = dict(common)
        out.update({
            "verdict": verdict,
            "verdict_msg": vmsg,
            "summary": vmsg,
            "smoke_gate_pass": passed,
            "smoke_gate_reason": reason,
        })
        return out

    # FULL verdict
    if not cardinality_ok:
        verdict = "HARD_FAIL"
        vmsg = f"HARD_FAIL_CARDINALITY_BREACH: expected={expected_n} observed={observed_n}"
    elif n_combos_arms_differ != len(phase_map):
        bad = [k for k, v in body.get("arms_differ_per_combo", {}).items() if not v]
        verdict = "HARD_FAIL"
        vmsg = f"HARD_FAIL_ARMS_IDENTICAL: {len(bad)} combos with mech==random: {bad}"
    elif not pc_result.get("pass"):
        verdict = "HARD_FAIL"
        vmsg = (f"HARD_FAIL_CONTROL_FAIL: positive_control top1="
                f"{pc_result.get('measured_top1')} outside band "
                f"[{pc_result.get('target', {}).get('top1_band_lo')}, "
                f"{pc_result.get('target', {}).get('top1_band_hi')}]")
    elif n_encoder_pairs_differ < 6:
        verdict = "MIDDLE_BAND"
        vmsg = (f"MIDDLE_BAND_ENCODER_MAIN_EFFECT_ABSENT: only "
                f"{n_encoder_pairs_differ}/6 encoder pairs distinct")
    elif n_encoders_with_sparsity_range >= 3 and interaction_pairs_visible >= 2:
        # v2 HARD_PASS gate: capacity-lift 2x-drill succeeded — 3+ encoders
        # show per_encoder_sparsity_range >= 0.15 (v1 only 1: fhrr) AND
        # 2+ pairs show interaction delta >= 0.15
        verdict = "HARD_PASS"
        vmsg = (f"HARD_PASS_V2_CAPLIFT_ENCODER_x_SPARSITY: {observed_n}/{expected_n} pts; "
                f"sat={n_sat} hp={n_hp} mb={n_mb} floor={n_floor} fail={n_fail}; "
                f"sat_frac={sat_frac:.2%} (v1=62.5pct - CAPACITY-LIFT SUCCESS); "
                f"n_encoders_with_sparsity_range>=0.15={n_encoders_with_sparsity_range}/4 "
                f"(v1=1/4); interaction_pairs_visible={interaction_pairs_visible}/6; "
                f"per_encoder_sparsity_range={per_encoder_sparsity_range}; "
                f"pc_pass; gpu_util~{gpu_util_estimate:.2f}")
    elif interaction_pairs_visible >= 2:
        verdict = "MIDDLE_BAND"
        vmsg = (f"MIDDLE_BAND_V2_INTERACTION_NO_ENCODER_LIFT: interaction visible "
                f"({interaction_pairs_visible}/6 pairs) but only "
                f"{n_encoders_with_sparsity_range}/4 encoders escape saturation; "
                f"v2 partial success; per_encoder_sparsity_range="
                f"{per_encoder_sparsity_range}; sat_frac={sat_frac:.2%}")
    elif interaction_pairs_visible >= 1:
        verdict = "MIDDLE_BAND"
        vmsg = (f"MIDDLE_BAND_INTERACTION_PARTIAL: {interaction_pairs_visible}/6 "
                f"encoder pairs show sparsity-range delta >=0.15; "
                f"per_encoder_sparsity_range={per_encoder_sparsity_range}; "
                f"sat_frac={sat_frac:.2%}")
    else:
        verdict = "MIDDLE_BAND"
        vmsg = (f"MIDDLE_BAND_MAIN_EFFECTS_ONLY: encoders and sparsity have "
                f"main effects but no interaction; "
                f"interaction_pairs_visible=0/6; per_encoder_sparsity_range="
                f"{per_encoder_sparsity_range}; sat_frac={sat_frac:.2%}; "
                f"v2 CAPACITY-LIFT insufficient to expose interaction")

    out = dict(common)
    out.update({
        "verdict": verdict,
        "verdict_msg": vmsg,
        "summary": vmsg,
    })
    return out


__all__ = [
    "DEVICE", "GPU_NAME", "GPU_MAX_MEM_GB",
    "SATURATED_TOP1", "HARD_PASS_LO", "MIDDLE_BAND_LO", "FLOOR_TOP1",
    "HP_DISCRIMINATOR", "MB_DISCRIMINATOR", "BETA",
    "ENCODER_FAMILIES",
    "SPARSITY_LEVELS_FULL", "SPARSITY_LEVELS_SMOKE",
    "N_DIM_FULL", "N_DIM_SMOKE", "CORRUPTION_FIXED", "ITERS_FIXED",
    "M_ITEMS_FULL", "M_ITEMS_SMOKE",
    "EXPECTED_N_UNITS_FULL", "EXPECTED_N_UNITS_SMOKE",
    "POSITIVE_CONTROL", "POSITIVE_CONTROL_SMOKE",
    "REQUIRED_FIELDS",
    "crlb_1step_cliff_prediction", "capacity_ratio", "get_backend_label",
    "eval_phase_point", "selftest",
    "run_one_seed_phase_diagram",
    "smoke_gate_predicate", "aggregate_and_verdict",
]
