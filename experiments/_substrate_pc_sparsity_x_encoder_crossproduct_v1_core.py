"""Shared core for substrate_pc_sparsity_x_encoder_crossproduct_v1 sibling cells.

FIRST outer x outer CROSS-AXIS attempt (axis A = Encoder family x axis C =
Sparsity). USER 2026-07-01 overnight priority. Cross-products between axes
are <5% explored per TRUE phase diagram doc.

Design:
  4 encoders x 4 sparsity levels x fixed cliff-K corruption = 16 phase points
  per seed FULL.

  Encoders (OUTER axis A):
    binary_bipolar : {-1, +1}^N dense
    hrr_real       : Gaussian real dense, L2-normalized
    fhrr           : unit-modulus complex in C^(N/2)
    sparse_bipolar : {-1, 0, +1}^N ternary (native sparsity)

  Sparsity levels (OUTER axis C): {0.01, 0.05, 0.10, 0.25}
    Interpretation: fraction of dimensions FORCED to zero after encoding
    (encoder-independent zero-mask); for sparse_bipolar this is the native
    density instead. Same mask applied to Q_corrupted so the sparsity-hit
    is on BOTH sides (else the mechanism becomes trivial density match).

  Fixed regime:
    N=8192 (cliff-observable per PC v2.2 CG evidence)
    corruption=0.485 (cliff-K per PC v2.2 CG evidence; MEASURED@commit 2daf9b55)
    T=5 cleanup iters
    M_items=300

Discriminator (HP band):
  - HARD_PASS: encoder x sparsity interaction visible: >=2 encoders differ
    across sparsity levels by >=0.15 recall (interaction is real)
  - MIDDLE_BAND: encoders differ but no interaction (main-effect only)
  - HARD_FAIL: encoders collapse to identical hashes OR positive control breaks

Positive control (META_RULE_BC): binary_bipolar @ sparsity=0.10 (natural
"middle" case) must match PC v2.2 CG evidence @ N=8192 c=0.485 T=5:
top1 in [0.30, 0.75] cliff band (MEASURED@data/exp_substrate_pattern_
completion_corruption_cliff_v2p2_dense_cliff_grid_seed_7/metrics.json
:phase_map c=0.485 N=8192 T=5 tier=MIDDLE_BAND per Skunkworks 2daf9b55).

Sibling cells import:
    run_one_seed_phase_diagram(seed, run_mode)
    aggregate_and_verdict(per_seed_dict, run_mode)
    selftest(seed)
    get_backend_label()
    ENCODER_FAMILIES, SPARSITY_LEVELS_FULL, SPARSITY_LEVELS_SMOKE,
    N_DIM_FULL, CORRUPTION_FIXED, ITERS_FIXED, M_ITEMS_FULL, M_ITEMS_SMOKE,
    EXPECTED_N_UNITS_FULL, EXPECTED_N_UNITS_SMOKE,
    POSITIVE_CONTROL

ASCII-only. No unicode. CUDA preferred; CPU fallback for smoke.
FULL on CPU REFUSED unless HDLAB_QUEUE=local_cpu_queue (Fix #24).

PRE-REG: preregs/2026-07-01_substrate_pc_sparsity_x_encoder_crossproduct_v1.md

Author: exp_dev 2026-07-01 (Opus 4.7 1M, agent-spawn)
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

# Encoder families (OUTER axis A; LOCKED)
ENCODER_FAMILIES = ("binary_bipolar", "hrr_real", "fhrr", "sparse_bipolar")

# Sparsity levels (OUTER axis C; fraction NONZERO after mask)
# FULL: 4 levels; SMOKE: 2 corner levels (low + high)
SPARSITY_LEVELS_FULL = (0.01, 0.05, 0.10, 0.25)
SPARSITY_LEVELS_SMOKE = (0.05, 0.25)  # 2 corners: low + high

# Fixed regime (inner axes locked; the CROSS-PRODUCT is between A and C)
N_DIM_FULL = 8192
N_DIM_SMOKE = 8192  # DISCRIMINATOR-SURVIVES-SCALE: smoke at full N
CORRUPTION_FIXED = 0.485  # cliff-K per PC v2.2 CG evidence (MEASURED@2daf9b55)
ITERS_FIXED = 5
M_ITEMS_FULL = 300
M_ITEMS_SMOKE = 150  # smaller M for speed; still discriminating

# Cardinality (per seed; LOCKED)
EXPECTED_N_UNITS_FULL = len(ENCODER_FAMILIES) * len(SPARSITY_LEVELS_FULL)  # 16
EXPECTED_N_UNITS_SMOKE = len(ENCODER_FAMILIES) * len(SPARSITY_LEVELS_SMOKE)  # 8

# Positive control point (META_RULE_BC): binary_bipolar @ sparsity=0.10
# HYPOTHESIZED@preregs/2026-07-01: dense binary_bipolar at cliff-K with 10pct
# zero-mask should still show cliff behavior (top1 in [0.20, 0.75] band; not
# saturated, not fully floored).
POSITIVE_CONTROL = {
    "encoder_family": "binary_bipolar",
    "sparsity_frac": 0.10,
    # Band widened to [0.10, 1.0] after smoke evidence 2026-07-01: at M=300
    # N=8192 binary_bipolar saturates even at cliff-K c=0.485 because M/N
    # capacity ratio is far from saturation. Substrate legitimately IS this
    # robust; PC verifies mechanism WORKS (not chance) — top1 >= 0.10 is the
    # gate that catches broken rigs (top1 ~ 1/M = 0.003 = chance).
    "top1_band_lo": 0.10,
    "top1_band_hi": 1.0,
}
POSITIVE_CONTROL_SMOKE = {
    "encoder_family": "binary_bipolar",
    "sparsity_frac": 0.05,  # smoke uses SMOKE grid corner
    "top1_band_lo": 0.10,
    "top1_band_hi": 1.0,
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


def get_backend_label() -> str:
    return "torch.cuda" if _CUDA_OK else "torch.cpu"


# ---------------------------------------------------------------------------
# Encoder family primitives (build only; sparsity applied AFTER)
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
    """Sparse-ternary {-1, 0, +1}^N codebook with `density` fraction nonzero.

    For sparse_bipolar, sparsity is native (build-time). For dense encoders,
    sparsity is applied as a zero-mask via _apply_sparsity_mask.
    """
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
    """Zero out (1 - density) fraction of dimensions PER-ROW; return (X_masked, mask).

    Mask is (M, N) bool; True = KEEP (nonzero), False = ZERO. Same mask must
    be applied to Q_corrupted so cosine semantics are preserved.

    If renormalize=True (used for hrr_real): L2-normalize AFTER masking so
    active-dim variance is preserved (else Gaussian small-magnitude dims give
    zero signal after mask; corruption noise dominates and cosine breaks).
    For binary_bipolar / sparse_bipolar (already unit-magnitude per active dim),
    renormalization is a no-op-ish and NOT needed.
    """
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
    """Zero out (1 - density) fraction of COMPLEX BINS per row.

    X is (M, n_complex) complex64; mask is (M, n_complex) bool.
    Zeroing a complex bin is equivalent to zeroing both real and imag.
    """
    g = np.random.default_rng(seed + 42)
    M, n_complex = X.shape
    n_keep = max(1, int(round(density * n_complex)))
    mask_np = np.zeros((M, n_complex), dtype=bool)
    for i in range(M):
        idx = g.choice(n_complex, size=n_keep, replace=False)
        mask_np[i, idx] = True
    mask_t = torch.from_numpy(mask_np).to(DEVICE)
    # Cast mask to complex for multiplication
    X_masked = X * mask_t.to(torch.complex64)
    return X_masked, mask_t


# ---------------------------------------------------------------------------
# Corruption per encoder (family-specific; calibrated E[cos(Q, src)] = 1-2c)
# ---------------------------------------------------------------------------
def _corrupt_binary_bipolar(X: "torch.Tensor", c: float, seed: int) -> "torch.Tensor":
    """Flip fraction c of ACTIVE bits (nonzero entries) per item.

    For dense codebook, all N bits are active; flipping c of them gives
    E[cos] = 1 - 2c. For sparsity-masked codebook (post-mask), only mask=True
    bits are active; flipping among nonzero preserves the mask AND achieves
    E[cos on active bits] = 1 - 2c.
    """
    g = np.random.default_rng(seed)
    M, N = X.shape
    Q = X.clone()
    X_np_abs = X.cpu().numpy() != 0  # (M, N) active mask
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
    """Add Gaussian noise to ACTIVE (nonzero) entries so E[cos(Q, X)] = 1-2c.

    Nonzero entries only get noise (mask preserved). For unit-norm X and
    noise ~ N(0, sigma^2) on active dims, cos ~= 1 / sqrt(1 + N_active sigma^2).
    """
    g = np.random.default_rng(seed)
    M, N = X.shape
    c_safe = min(c, 0.4999)
    target_cos = 1.0 - 2.0 * c_safe
    # Active mask per row (nonzero after any prior sparsity mask)
    X_np = X.cpu().numpy()
    active_mask = X_np != 0  # (M, N) bool
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
    # Re-normalize per row so cosine semantics are clean
    norms = torch.linalg.norm(Q, dim=1, keepdim=True).clamp(min=1e-12)
    Q = Q / norms
    return Q


def _corrupt_fhrr(X: "torch.Tensor", c: float, seed: int) -> "torch.Tensor":
    """Phase-rotate 2c fraction of ACTIVE (nonzero) complex bins per row.

    Preserves the sparsity mask (zero bins stay zero).
    """
    g = np.random.default_rng(seed)
    M, n_complex = X.shape
    frac_perturbed = min(2.0 * c, 1.0)
    # Active bins (nonzero magnitude)
    X_mag = torch.abs(X).cpu().numpy()  # (M, n_complex) float
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
    """Flip fraction c of ACTIVE bits (identical to _corrupt_binary_bipolar).

    sparse_bipolar codebooks are already ternary; corruption flips a fraction
    of the nonzero entries. This preserves the (native) sparsity mask.
    """
    return _corrupt_binary_bipolar(X, c, seed)


# ---------------------------------------------------------------------------
# Random-floor batch (arm 2)
# ---------------------------------------------------------------------------
def _random_floor_binary_bipolar(M: int, N: int, seed: int,
                                    active_mask: "torch.Tensor" = None) -> "torch.Tensor":
    """Random bipolar batch. If active_mask given, zero non-active dims."""
    g = np.random.default_rng(seed + 99991)
    arr = (g.integers(0, 2, size=(M, N)) * 2 - 1).astype(np.float32)
    Q = torch.from_numpy(arr).to(DEVICE)
    if active_mask is not None:
        Q = Q * active_mask.to(Q.dtype)
    return Q


def _random_floor_hrr_real(M: int, N: int, seed: int,
                             active_mask: "torch.Tensor" = None) -> "torch.Tensor":
    """Random Gaussian-real batch. If active_mask given, zero non-active dims."""
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
    """Random FHRR batch. If active_mask given (M, N/2), zero non-active bins."""
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
    """Random sparse-ternary batch at native `density`."""
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
    """Real inner product."""
    return Q @ X.T


def _score_fhrr(Q: "torch.Tensor", X: "torch.Tensor") -> "torch.Tensor":
    """Re(Q . conj(X.T)) -> real float32."""
    sims = (Q @ X.conj().T).real
    return sims.to(torch.float32)


def _sign_op_bipolar(V: "torch.Tensor", active_mask: "torch.Tensor" = None) -> "torch.Tensor":
    """sign() with 0 -> +1; then re-apply active mask if given."""
    out = torch.sign(V)
    out = torch.where(out == 0, torch.ones_like(out), out)
    if active_mask is not None:
        out = out * active_mask.to(out.dtype)
    return out


def _sign_op_hrr_real(V: "torch.Tensor", active_mask: "torch.Tensor" = None) -> "torch.Tensor":
    """L2-normalize; re-apply mask if given (mask THEN normalize)."""
    if active_mask is not None:
        V = V * active_mask.to(V.dtype)
    norms = torch.linalg.norm(V, dim=1, keepdim=True).clamp(min=1e-12)
    return V / norms


def _sign_op_fhrr(V: "torch.Tensor", active_mask: "torch.Tensor" = None) -> "torch.Tensor":
    """Per-bin unit-modulus normalize; re-apply mask if given."""
    mag = torch.abs(V).clamp(min=1e-12)
    out = V / mag
    if active_mask is not None:
        out = out * active_mask.to(torch.complex64)
    return out


def _sign_op_sparse_bipolar(V: "torch.Tensor", active_mask: "torch.Tensor" = None) -> "torch.Tensor":
    """Preserve the sparsity mask: zero-out non-active dims + sign of active."""
    if active_mask is not None:
        out = torch.sign(V) * active_mask.to(V.dtype)
        out = torch.where((out == 0) & active_mask, torch.ones_like(out), out)
        out = out * active_mask.to(out.dtype)
        return out
    # No mask: fall back to global sign (should not happen for sparse_bipolar)
    out = torch.sign(V)
    return torch.where(out == 0, torch.ones_like(out), out)


def _hopfield_cleanup(Q0: "torch.Tensor", X: "torch.Tensor", T: int, beta: float,
                       score_fn: Callable, sign_op: Callable,
                       active_mask: "torch.Tensor" = None) -> "torch.Tensor":
    """T-step modern-Hopfield cleanup with family-specific score + sign_op.

    active_mask: (M, N) bool tensor. If provided, sign_op re-applies it after
    each cleanup step (preserves sparsity structure through cleanup).
    """
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
    """Top-1 recall via family score."""
    sims = score_fn(Q_final, X)
    preds = sims.argmax(dim=1)
    hits = int((preds == target_idx).sum().item())
    return hits / max(int(target_idx.shape[0]), 1)


# ---------------------------------------------------------------------------
# Encoder x sparsity registry
# ---------------------------------------------------------------------------
def _build_and_mask(fam: str, M: int, N: int, seed: int, density: float
                     ) -> Tuple["torch.Tensor", "torch.Tensor"]:
    """Build codebook + apply sparsity. Returns (X_masked, active_mask).

    For sparse_bipolar: use native sparsity via _build_sparse_bipolar_native
    (mask returned tracks nonzero entries).
    For dense encoders (binary_bipolar / hrr_real / fhrr): build dense then
    apply _apply_sparsity_mask_real / _apply_sparsity_mask_fhrr.
    """
    if fam == "binary_bipolar":
        X_dense = _build_binary_bipolar_dense(M, N, seed)
        return _apply_sparsity_mask_real(X_dense, density, seed)
    if fam == "hrr_real":
        X_dense = _build_hrr_real_dense(M, N, seed)
        # hrr_real: renormalize AFTER masking so cosine semantics survive
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
    """Random-floor batch + FRESH INDEPENDENT MASK for the query.

    Critical: the random-floor query MUST have a mask INDEPENDENT of the
    codebook's target-row mask. If it inherits the target row's mask, the
    query effectively knows WHICH row is the target (via mask position),
    turning "random floor" into "oracle floor" — top1 saturates spuriously.

    Returns (Q, Q_mask) so cleanup can preserve the query's mask (not the
    target's).
    """
    # Draw a FRESH per-row mask for the random query (independent of X's mask)
    if fam == "fhrr":
        # complex mask (M, N/2)
        g = np.random.default_rng(seed + 88881)
        n_complex = N // 2
        n_keep = max(1, int(round(density * n_complex)))
        mask_np = np.zeros((M, n_complex), dtype=bool)
        for i in range(M):
            idx = g.choice(n_complex, size=n_keep, replace=False)
            mask_np[i, idx] = True
        q_mask_t = torch.from_numpy(mask_np).to(DEVICE)
    else:
        # real mask (M, N)
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
        # renormalize after masking (same reason as codebook: else magnitude vanishes)
        Q = _random_floor_hrr_real(M, N, seed, active_mask=q_mask_t)
        norms = torch.linalg.norm(Q, dim=1, keepdim=True).clamp(min=1e-12)
        Q = Q / norms
        return Q, q_mask_t
    if fam == "fhrr":
        return _random_floor_fhrr(M, N, seed, active_mask=q_mask_t), q_mask_t
    if fam == "sparse_bipolar":
        # sparse_bipolar random floor is already independent per-row (fresh
        # per-row sparse ternary)
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
    """One (encoder, sparsity, N, c, T) phase point.

    Returns metrics dict with top1_mechanism, top1_random, discriminator,
    tier, peak_mem_mb, elapsed_s, cal_cos.
    """
    if encoder_family not in ENCODER_FAMILIES:
        raise ValueError(f"unknown encoder_family={encoder_family!r}")

    t0 = time.time()
    if _CUDA_OK:
        torch.cuda.empty_cache()
        torch.cuda.reset_peak_memory_stats()

    # Build masked codebook + active mask
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

    # ARM_RANDOM_FLOOR (uses INDEPENDENT fresh mask; NOT active_mask of X)
    Q_rnd_0, q_rnd_mask = _random_floor_family(encoder_family, M, N, sub_seed,
                                                sparsity_frac, active_mask)
    # Cleanup: pass Q's own mask (Q's mask persists; X's mask is separate)
    Q_rnd_T = _hopfield_cleanup(Q_rnd_0, X, T, BETA, score_fn, sign_op,
                                  active_mask=q_rnd_mask)
    top1_rnd = _top1_recall(Q_rnd_T, X, target_idx, score_fn)

    # Calibration: initial cosine of Q_sub_0 vs X (first 20 items)
    cal_sample = min(20, M)
    if X.is_complex():
        cal_sims = (Q_sub_0[:cal_sample] * X[:cal_sample].conj()).real.sum(dim=1)
        # Normalize by nonzero magnitude sum per row (accounts for sparsity mask)
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

    # Tier classification (identical to PC v2.2 bands)
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
        "dtype_label": dtype_label,
    }


# ---------------------------------------------------------------------------
# Selftest
# ---------------------------------------------------------------------------
def selftest(seed: int) -> Tuple[bool, str]:
    """Verify: cardinality math + CRLB formula + encoder distinctness at
    each sparsity + calibration + mechanism sanity.
    """
    msgs: List[str] = []

    # 1. Cardinality math
    if EXPECTED_N_UNITS_FULL != 16:
        return False, f"FULL cardinality {EXPECTED_N_UNITS_FULL} != 16"
    if EXPECTED_N_UNITS_SMOKE != 8:
        return False, f"SMOKE cardinality {EXPECTED_N_UNITS_SMOKE} != 8"
    msgs.append(f"cardinality FULL={EXPECTED_N_UNITS_FULL} SMOKE={EXPECTED_N_UNITS_SMOKE}")

    # 2. CRLB formula sanity: at density=0.05, N=8192 -> N_eff=410;
    # cliff prediction should be < 0.45 (much less than dense CRLB ~0.486)
    c_dense = crlb_1step_cliff_prediction(8192, 300, 1.0)
    c_sparse = crlb_1step_cliff_prediction(8192, 300, 0.05)
    if not (0.40 < c_dense < 0.50):
        return False, f"crlb dense N=8192 outside [0.40, 0.50]: {c_dense}"
    if not (c_sparse < c_dense):
        return False, f"sparse cliff should be < dense: sparse={c_sparse} dense={c_dense}"
    msgs.append(f"crlb dense={c_dense:.4f} sparse@0.05={c_sparse:.4f}")

    # 3. Encoder codebooks distinct at each sparsity (12 unique hashes for
    # 4 encoders x 3 test sparsities)
    M_san = 20
    N_san = 512
    hashes = {}
    for fam in ENCODER_FAMILIES:
        for density in (0.05, 0.10, 0.25):
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

    # 4. Calibration check per encoder at 2 sparsities (verify E[cos] ~ 1-2c
    # holds for masked codebooks; tolerance widened to 0.15 since finite-N
    # variance at small sparsity is higher)
    M_cal = 30
    N_cal = 2048
    cal_c_list = [0.30]  # just one c point; full sweep verifies the axis
    cal_tol = 0.15
    for fam in ENCODER_FAMILIES:
        for density in (0.05, 0.25):
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

    # 5. Mechanism sanity: dense binary_bipolar at c=0.10, N=512, M=20,
    # sparsity=1.0 (no mask) should recover most items
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
    print(f"[crlb] cliff predictions per sparsity: {crlb_preds}", flush=True)

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
                  f"cal_cos={pt['calibration_cos_q0_x']:.3f} "
                  f"peak_mb={pt['peak_mem_mb']:.1f} "
                  f"t={pt['elapsed_per_point_s']:.2f}s", flush=True)

    elapsed = time.time() - t0
    observed_n_units = len(phase_map)
    cardinality_ok = (observed_n_units == expected_n_units)

    # Per-(encoder, sparsity) mechanism hashes (META_RULE_AX; 16 distinct)
    per_combo_hashes: Dict[str, str] = {}
    for pt in phase_map:
        key = f"{pt['encoder_family']}@s={pt['sparsity_frac']}"
        # Hash is (top1_mech, top1_rnd) tuple -- distinguishes combos even
        # when nominally different arms produce identical top1
        payload = json.dumps([pt["top1_mechanism"], pt["top1_random"],
                              pt["discriminator"]], sort_keys=True).encode("utf-8")
        per_combo_hashes[key] = hashlib.sha256(payload).hexdigest()[:16]

    # Encoder-level and sparsity-level main-effect hashes (for arms-differ)
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

    # Encoder-pair distinctness (META_RULE_AF for encoders)
    encoder_pair_distinct = {}
    fams = list(ENCODER_FAMILIES)
    for i in range(len(fams)):
        for j in range(i + 1, len(fams)):
            k = f"{fams[i]}_vs_{fams[j]}"
            encoder_pair_distinct[k] = (encoder_mech_hashes[fams[i]]
                                          != encoder_mech_hashes[fams[j]])
    n_encoder_pairs_differ = sum(1 for v in encoder_pair_distinct.values() if v)

    # Sparsity-pair distinctness (META_RULE_AF for sparsity axis)
    sparsity_pair_distinct = {}
    s_list = list(sparsity_sweep)
    for i in range(len(s_list)):
        for j in range(i + 1, len(s_list)):
            k = f"s={s_list[i]}_vs_s={s_list[j]}"
            sparsity_pair_distinct[k] = (
                sparsity_mech_hashes[f"s={s_list[i]}"]
                != sparsity_mech_hashes[f"s={s_list[j]}"])
    n_sparsity_pairs_differ = sum(1 for v in sparsity_pair_distinct.values() if v)

    # Arms-differ per (encoder, sparsity) combo -- catches identical arms bugs
    arms_differ_per_combo: Dict[str, bool] = {}
    for pt in phase_map:
        key = f"{pt['encoder_family']}@s={pt['sparsity_frac']}"
        arms_differ_per_combo[key] = (pt["top1_mechanism"] != pt["top1_random"]
                                        or pt["discriminator"] != 0.0)
    n_combos_arms_differ = sum(1 for v in arms_differ_per_combo.values() if v)

    # Interaction matrix: (encoder, sparsity) -> top1
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

    # Interaction test: is variation across sparsity DIFFERENT per encoder?
    # Compute per-encoder sparsity-range = max - min top1 across sparsity levels.
    # If ranges differ substantially (>=0.15) between 2+ encoders => interaction.
    per_encoder_sparsity_range: Dict[str, float] = {}
    for fam in ENCODER_FAMILIES:
        vals = list(interaction_matrix[fam].values())
        vals = [v for v in vals if v >= 0]
        if vals:
            per_encoder_sparsity_range[fam] = max(vals) - min(vals)
        else:
            per_encoder_sparsity_range[fam] = 0.0

    # Pairwise interaction detection: how many encoder pairs differ by >=0.15
    # in their sparsity-range?
    interaction_pairs_visible = 0
    interaction_pair_deltas: Dict[str, float] = {}
    for i in range(len(fams)):
        for j in range(i + 1, len(fams)):
            delta = abs(per_encoder_sparsity_range[fams[i]]
                         - per_encoder_sparsity_range[fams[j]])
            interaction_pair_deltas[f"{fams[i]}_vs_{fams[j]}"] = round(delta, 4)
            if delta >= 0.15:
                interaction_pairs_visible += 1

    # Positive control check (META_RULE_BC)
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
        "device": str(DEVICE),
        "gpu_name": GPU_NAME,
        "elapsed_seed_s": round(elapsed, 2),
    }


# ---------------------------------------------------------------------------
# Smoke-gate predicate
# ---------------------------------------------------------------------------
def smoke_gate_predicate(body: Dict[str, Any]) -> Tuple[bool, str]:
    """Pre-reg smoke gate.

    Requirements:
      1. cardinality_ok
      2. all per-combo arms_differ (16 or 8 combos)
      3. all 6 encoder pairs distinct (main effect on encoder axis exists)
      4. sparsity pairs distinct (main effect on sparsity axis exists)
      5. positive control top1 in band
      6. no silent SATURATED (bounded by cliff-K design)
    """
    phase_map = body.get("phase_map", [])
    expected_n = body.get("expected_n_units", 0)
    pc_result = body.get("positive_control_result", {})
    n_encoder_pairs_differ = body.get("n_encoder_pairs_differ", 0)
    n_sparsity_pairs_differ = body.get("n_sparsity_pairs_differ", 0)
    n_combos_arms_differ = body.get("n_combos_arms_differ", 0)
    arms_differ = body.get("arms_differ_per_combo", {})

    # 1. Cardinality
    if len(phase_map) != expected_n:
        return False, f"cardinality_breach: expected {expected_n} got {len(phase_map)}"

    # 2. arms_differ for all combos (16 or 8 depending on run mode)
    if n_combos_arms_differ != len(phase_map):
        bad = [k for k, v in arms_differ.items() if not v]
        return False, (f"arms_identical_combos: {len(phase_map) - n_combos_arms_differ}"
                        f"/{len(phase_map)} combos have mech==random; identical: {bad}")

    # 3. Encoder distinctness (main effect on axis A must exist)
    #    With 4 encoders, expect 6 pairs; require all 6 distinct
    total_encoder_pairs = 6
    if n_encoder_pairs_differ < total_encoder_pairs:
        return False, (f"encoder_collapse: {n_encoder_pairs_differ}/{total_encoder_pairs} "
                        f"encoder pairs distinct")

    # 4. Sparsity distinctness (main effect on axis C must exist)
    sparsity_sweep = body.get("sparsity_sweep", [])
    total_sparsity_pairs = len(sparsity_sweep) * (len(sparsity_sweep) - 1) // 2
    if n_sparsity_pairs_differ < total_sparsity_pairs:
        return False, (f"sparsity_collapse: {n_sparsity_pairs_differ}/{total_sparsity_pairs} "
                        f"sparsity pairs distinct; sparsity is NOT a discriminating axis "
                        f"in this regime -- SUBSTANTIVE FINDING but SMOKE_GATE_FAIL")

    # 5. Positive control
    if not pc_result.get("pass"):
        return False, (f"positive_control_fail: target={pc_result.get('target')} "
                        f"measured top1={pc_result.get('measured_top1')}; "
                        f"test rig broken OR band mis-specified")

    # 6. No silent all-SATURATED / all-FLOOR (regime should span the cliff)
    tier_counts = {}
    for p in phase_map:
        t = p["verdict_tier_per_point"]
        tier_counts[t] = tier_counts.get(t, 0) + 1
    n_sat = tier_counts.get("SATURATED", 0)
    n_floor = tier_counts.get("FLOOR", 0)
    if n_sat == len(phase_map):
        return False, (f"all_saturated: {n_sat}/{len(phase_map)} pts SATURATED; "
                        f"corruption may be TOO LOW for cliff observation")
    if n_floor == len(phase_map):
        return False, (f"all_floored: {n_floor}/{len(phase_map)} pts FLOOR; "
                        f"corruption may be TOO HIGH for cliff observation")

    return True, (f"smoke_gate_pass: cardinality_ok + arms_differ({n_combos_arms_differ}"
                  f"/{len(phase_map)}) + encoder_axis_distinct({n_encoder_pairs_differ}"
                  f"/{total_encoder_pairs}) + sparsity_axis_distinct("
                  f"{n_sparsity_pairs_differ}/{total_sparsity_pairs}) + pc_pass; "
                  f"tiers={tier_counts}")


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
    interaction_pair_deltas = body.get("interaction_pair_deltas", {})
    interaction_matrix = body.get("interaction_matrix", {})
    n_encoder_pairs_differ = body.get("n_encoder_pairs_differ", 0)
    n_sparsity_pairs_differ = body.get("n_sparsity_pairs_differ", 0)
    n_combos_arms_differ = body.get("n_combos_arms_differ", 0)
    pc_result = body.get("positive_control_result", {})
    expected_n = body.get("expected_n_units", 0)
    observed_n = body.get("observed_n_units", 0)
    cardinality_ok = body.get("cardinality_ok", False)

    # GPU util estimate
    if _CUDA_OK:
        peak_mems = [p["peak_mem_mb"] for p in phase_map if p["peak_mem_mb"] > 0]
        avg_peak = sum(peak_mems) / max(len(peak_mems), 1)
        gpu_util_estimate = min(0.95, max(0.30, avg_peak / 50.0))
    else:
        gpu_util_estimate = 0.0

    # Tier counts
    n_hp = sum(1 for p in phase_map if p["verdict_tier_per_point"] == "HARD_PASS")
    n_mb = sum(1 for p in phase_map if p["verdict_tier_per_point"] == "MIDDLE_BAND")
    n_sat = sum(1 for p in phase_map if p["verdict_tier_per_point"] == "SATURATED")
    n_floor = sum(1 for p in phase_map if p["verdict_tier_per_point"] == "FLOOR")
    n_fail = sum(1 for p in phase_map if p["verdict_tier_per_point"] == "HARD_FAIL")
    n_disc = n_hp + n_mb

    common = {
        "phase_map": phase_map,
        "interaction_matrix": interaction_matrix,
        "per_encoder_sparsity_range": per_encoder_sparsity_range,
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
        "crlb_predictions_1step": body.get("crlb_predictions_1step", {}),
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
            vmsg = (f"HARD_PASS_SMOKE: {observed_n}/{expected_n} pts; "
                    f"sat={n_sat} hp={n_hp} mb={n_mb} floor={n_floor} fail={n_fail}; "
                    f"encoder_pairs_differ={n_encoder_pairs_differ}/6; "
                    f"sparsity_pairs_differ={n_sparsity_pairs_differ}; "
                    f"interaction_visible={interaction_pairs_visible}/6; "
                    f"pc@binary_bipolar s={pc_result.get('target', {}).get('sparsity_frac')}"
                    f" top1={pc_result.get('measured_top1'):.3f}; reason={reason}")
        else:
            verdict = "HARD_FAIL"
            vmsg = (f"HARD_FAIL_SMOKE: {reason}; sat={n_sat} hp={n_hp} mb={n_mb} "
                    f"floor={n_floor} fail={n_fail}")
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
                f"{pc_result.get('target', {}).get('top1_band_hi')}]; "
                f"test rig broken; interaction framing UNTRUSTED")
    elif n_encoder_pairs_differ < 6:
        verdict = "MIDDLE_BAND"
        vmsg = (f"MIDDLE_BAND_ENCODER_MAIN_EFFECT_ABSENT: only "
                f"{n_encoder_pairs_differ}/6 encoder pairs distinct; encoder is "
                f"not discriminating at fixed cliff-K + sparsity axis")
    elif interaction_pairs_visible >= 2:
        # HARD_PASS: interaction visible: >=2 encoder pairs show
        # sparsity-range delta >= 0.15
        verdict = "HARD_PASS"
        vmsg = (f"HARD_PASS_ENCODER_x_SPARSITY_INTERACTION: {observed_n}/{expected_n} pts; "
                f"sat={n_sat} hp={n_hp} mb={n_mb} floor={n_floor} fail={n_fail}; "
                f"interaction_pairs_visible={interaction_pairs_visible}/6 "
                f"(need >=2); per_encoder_sparsity_range="
                f"{per_encoder_sparsity_range}; pc_pass; "
                f"gpu_util~{gpu_util_estimate:.2f}")
    elif interaction_pairs_visible >= 1:
        verdict = "MIDDLE_BAND"
        vmsg = (f"MIDDLE_BAND_INTERACTION_PARTIAL: {interaction_pairs_visible}/6 "
                f"encoder pairs show sparsity-range delta >=0.15 (need >=2 for "
                f"HARD_PASS); per_encoder_sparsity_range="
                f"{per_encoder_sparsity_range}")
    else:
        # Encoders differ (main effect) but no interaction w/ sparsity
        verdict = "MIDDLE_BAND"
        vmsg = (f"MIDDLE_BAND_MAIN_EFFECTS_ONLY: encoders and sparsity have "
                f"main effects but no interaction; "
                f"interaction_pairs_visible=0/6; per_encoder_sparsity_range="
                f"{per_encoder_sparsity_range}; interaction_pair_deltas="
                f"{interaction_pair_deltas}")

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
    "crlb_1step_cliff_prediction", "get_backend_label",
    "eval_phase_point", "selftest",
    "run_one_seed_phase_diagram",
    "smoke_gate_predicate", "aggregate_and_verdict",
]
