"""Shared core for substrate_pc_encoder_family_phase_diagram_v1 sibling cells.

First COMPONENT-SUBSTITUTION phase diagram (vs prior parameter-sweep phase
diagrams within fixed mechanisms). USER directive 2026-06-28 (Research):
fill out comprehensive phase diagrams across COMPONENTS, not just config
parameters. Encoder family is the most load-bearing lever; pattern completion
is the most-characterized primitive.

Encoder families (OUTER axis):
    binary_bipolar  : {-1, +1}^N dense, score = Q @ X.T (PC v2.2 default; POSITIVE CONTROL)
    hrr_real        : N(0, 1/N)^N dense Gaussian real, score = Q @ X.T
    fhrr            : unit-modulus complex exp(i*phi) in C^(N/2), score = Re(Q . conj(X))
    sparse_bipolar  : {-1, 0, +1}^N dense, s/N=0.05 active, score = Q @ X.T

Inner axes: N (2048, 8192) x corruption (5 pts) x cleanup_iters (1, 5).
4 encoders * 2 N * 5 c * 2 T = 80 phase points per seed FULL.
4 encoders * 1 N * 3 c * 1 T = 12 corner points per seed SMOKE.

Corruption MODEL is family-specific but normalized to produce equivalent
initial cosine 1 - 2c between Q_corrupted and source — apples-to-apples.

Cleanup is identical across encoders (modern-Hopfield softmax with beta=8.0);
only sign_op / unit-modulus normalize differs per family.

PRE-REG: preregs/2026-06-28_substrate_pc_encoder_family_phase_diagram_v1.md

Sibling cells import:
    run_one_seed_phase_diagram(seed, run_mode)
    aggregate_and_verdict(per_seed_dict, run_mode)
    selftest(seed)
    get_backend_label()
    ENCODER_FAMILIES,
    N_SWEEP_FULL, CORRUPTION_FULL, ITERS_FULL,
    N_SWEEP_SMOKE, CORRUPTION_SMOKE, ITERS_SMOKE,
    M_ITEMS_FULL, M_ITEMS_SMOKE

ASCII-only. No unicode. CUDA preferred; CPU fallback for smoke.
FULL on CPU REFUSED unless HDLAB_QUEUE=local_cpu_queue (Fix #24).

Author: exp_dev 2026-06-28 (Opus 4.7 1M, agent-spawn)
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import time
from pathlib import Path
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
SPARSE_DENSITY = 0.05  # s/N for sparse_bipolar; 5% nonzero

# Encoder families (OUTER axis; LOCKED at module init)
ENCODER_FAMILIES = ("binary_bipolar", "hrr_real", "fhrr", "sparse_bipolar")

# Sweep axes
N_SWEEP_FULL = [2048, 8192]
CORRUPTION_FULL = [0.20, 0.35, 0.45, 0.475, 0.50]
ITERS_FULL = [1, 5]
M_ITEMS_FULL = 300

N_SWEEP_SMOKE = [2048]
CORRUPTION_SMOKE = [0.20, 0.45, 0.50]
ITERS_SMOKE = [1]
M_ITEMS_SMOKE = 200

# Cardinality (per seed; LOCKED)
EXPECTED_N_UNITS_FULL = (len(ENCODER_FAMILIES) * len(N_SWEEP_FULL)
                          * len(CORRUPTION_FULL) * len(ITERS_FULL))  # 80
EXPECTED_N_UNITS_SMOKE = (len(ENCODER_FAMILIES) * len(N_SWEEP_SMOKE)
                           * len(CORRUPTION_SMOKE) * len(ITERS_SMOKE))  # 12

# Positive control point: binary_bipolar @ N=8192, c=0.475, T=5 must reproduce
# PC v2.2 measured top1 >= 0.50 (PC v2.2 commit 2daf9b55 evidence at this
# point: top1 ~ 0.55-0.65; SAFE FLOOR for control PASS = 0.50)
POSITIVE_CONTROL = {
    "encoder_family": "binary_bipolar",
    "N": 8192,
    "corruption_frac": 0.475,
    "cleanup_iters": 5,
    "top1_floor": 0.50,
}
# Smoke variant of positive control (smaller N, easier c)
POSITIVE_CONTROL_SMOKE = {
    "encoder_family": "binary_bipolar",
    "N": 2048,
    "corruption_frac": 0.20,
    "cleanup_iters": 1,
    "top1_floor": 0.80,
}

REQUIRED_FIELDS = ("verdict", "verdict_msg", "elapsed_s", "summary")


# ---------------------------------------------------------------------------
# CRLB / overlap-floor prediction (META_RULE_AG)
# ---------------------------------------------------------------------------
def crlb_1step_cliff_prediction(N: int, M: int, encoder_family: str) -> float:
    """1-step cliff prediction for random codes.

    For all four encoder families: effective dimension N_eff is N for
    bipolar / hrr_real / sparse_bipolar; N for fhrr (N/2 complex pairs =
    N real degrees of freedom). Noise floor sqrt(2 log M / N_eff); cliff
    = corruption where signal (1 - 2c) == noise floor.
    """
    if N <= 0 or M <= 1:
        return 0.0
    N_eff = N  # all four families have N real DoF
    noise = math.sqrt(2.0 * math.log(M) / N_eff)
    return max(0.0, 0.5 * (1.0 - noise))


def get_backend_label() -> str:
    return "torch.cuda" if _CUDA_OK else "torch.cpu"


# ---------------------------------------------------------------------------
# Encoder family primitives (each: build_codebook, corrupt, score, sign_op)
# ---------------------------------------------------------------------------
def _build_binary_bipolar(M: int, N: int, seed: int) -> "torch.Tensor":
    """Dense bipolar {-1, +1}^N codebook (M, N) float32 on DEVICE."""
    g = np.random.default_rng(seed)
    arr = (g.integers(0, 2, size=(M, N)) * 2 - 1).astype(np.float32)
    return torch.from_numpy(arr).to(DEVICE)


def _build_hrr_real(M: int, N: int, seed: int) -> "torch.Tensor":
    """Dense Gaussian N(0, 1/sqrt(N))^N codebook (M, N) float32 on DEVICE.

    Variance 1/N so each codeword has expected squared norm 1.0 (matches
    bipolar's norm sqrt(N) after L2-normalize).
    """
    g = np.random.default_rng(seed)
    arr = (g.standard_normal(size=(M, N)) / math.sqrt(N)).astype(np.float32)
    # L2-normalize per row so all codes have unit norm (apples-to-apples
    # cosine semantics across encoders)
    norms = np.linalg.norm(arr, axis=1, keepdims=True).clip(min=1e-12)
    arr = arr / norms
    return torch.from_numpy(arr).to(DEVICE)


def _build_fhrr(M: int, N: int, seed: int) -> "torch.Tensor":
    """Unit-modulus complex codebook exp(i * phi) in C^(N/2) (M, N/2) complex64 on DEVICE.

    Each codeword has N/2 complex bins; each bin is exp(i*phi) for phi uniform
    in [0, 2*pi). Total real DoF = N (matches other encoders' N real DoF).
    """
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


def _build_sparse_bipolar(M: int, N: int, seed: int) -> "torch.Tensor":
    """Sparse-ternary {-1, 0, +1}^N codebook (M, N) float32 on DEVICE.

    Each row has exactly s = round(SPARSE_DENSITY * N) nonzero entries
    (half +1, half -1, half-rounded-up for odd s). Cosine semantics:
    Q . X / (|Q| |X|) — both have norm sqrt(s).
    """
    g = np.random.default_rng(seed)
    s = max(1, int(round(SPARSE_DENSITY * N)))
    arr = np.zeros((M, N), dtype=np.float32)
    for i in range(M):
        idx = g.choice(N, size=s, replace=False)
        signs = g.integers(0, 2, size=s).astype(np.float32) * 2.0 - 1.0
        arr[i, idx] = signs
    return torch.from_numpy(arr).to(DEVICE)


# ---------------------------------------------------------------------------
# Corruption per encoder (family-specific; calibrated to E[cos(Q, src)] = 1-2c)
# ---------------------------------------------------------------------------
def _corrupt_binary_bipolar(X: "torch.Tensor", c: float, seed: int) -> "torch.Tensor":
    """Flip fraction c of bits independently per item. E[cos(Q, src)] = 1 - 2c."""
    g = np.random.default_rng(seed)
    M, N = X.shape
    flips = g.random((M, N)) < c
    flips_t = torch.from_numpy(flips).to(DEVICE)
    Q = X.clone()
    Q[flips_t] = -Q[flips_t]
    return Q


def _corrupt_hrr_real(X: "torch.Tensor", c: float, seed: int) -> "torch.Tensor":
    """Add Gaussian noise to X so that E[cos(Q, X)] = 1 - 2c.

    cos(X + noise, X) = X . (X + noise) / (|X| |X + noise|)
    For X unit-norm and noise ~ N(0, sigma^2 I), E[noise . X] = 0, |X + noise|^2 ~= 1 + N sigma^2.
    cos ~= 1 / sqrt(1 + N sigma^2). Set = 1 - 2c -> sigma^2 = (1/(1-2c)^2 - 1) / N.
    Cap c at 0.4999 to avoid division-by-zero at c=0.5 (cos -> 0).
    """
    g = np.random.default_rng(seed)
    M, N = X.shape
    c_safe = min(c, 0.4999)
    target_cos = 1.0 - 2.0 * c_safe
    sigma2 = (1.0 / (target_cos * target_cos) - 1.0) / N
    sigma = math.sqrt(max(sigma2, 0.0))
    noise = (g.standard_normal(size=(M, N)) * sigma).astype(np.float32)
    noise_t = torch.from_numpy(noise).to(DEVICE)
    Q = X + noise_t
    # Re-normalize so cosine semantics are clean
    norms = torch.linalg.norm(Q, dim=1, keepdim=True).clamp(min=1e-12)
    Q = Q / norms
    return Q


def _corrupt_fhrr(X: "torch.Tensor", c: float, seed: int) -> "torch.Tensor":
    """Phase-rotate fraction c of bins by a random phase. E[Re(Q . X*)] / (N/2) = 1 - 2c.

    For complex unit-modulus X_k and corrupted Q_k = X_k * exp(i*delta_k):
    Re(Q . X*) = sum_k cos(delta_k). If fraction c of bins get delta uniform
    in [0, 2*pi) (mean cos = 0) and remaining (1-c) stay (cos = 1), then
    E[Re(Q . X*) / (N/2)] = (1-c)*1 + c*0 = 1 - c.
    BUT the apples-to-apples target is E[cos] = 1 - 2c. We thus perturb
    fraction (2c) of bins (capped at 1.0) — match expected cosine to
    1 - min(2c, 1.0) = max(1 - 2c, 0).
    """
    g = np.random.default_rng(seed)
    M, n_complex = X.shape
    frac_perturbed = min(2.0 * c, 1.0)
    mask = (g.random((M, n_complex)) < frac_perturbed)
    delta = g.uniform(0.0, 2.0 * math.pi, size=(M, n_complex)).astype(np.float32)
    delta = delta * mask  # only perturb selected bins
    real_rot = np.cos(delta).astype(np.float32)
    imag_rot = np.sin(delta).astype(np.float32)
    rot = np.empty((M, n_complex), dtype=np.complex64)
    rot.real = real_rot
    rot.imag = imag_rot
    rot_t = torch.from_numpy(rot).to(DEVICE)
    Q = X * rot_t
    return Q


def _corrupt_sparse_bipolar(X: "torch.Tensor", c: float, seed: int) -> "torch.Tensor":
    """Flip fraction c of the ACTIVE (nonzero) bits per item. E[cos(Q, src)] = 1 - 2c.

    Cosine is X.Q / (|X| |Q|) = (#agree - #disagree) / |X|^2 (norms equal).
    With s active bits, flipping (c*s) of them gives s - 2*c*s agreements,
    cosine = (s - 2*c*s) / s = 1 - 2c.
    """
    g = np.random.default_rng(seed)
    Q = X.clone()
    M, N = X.shape
    X_np = X.cpu().numpy()
    for i in range(M):
        active_idx = np.flatnonzero(X_np[i])
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


# ---------------------------------------------------------------------------
# Random-floor batch (arm 2: fresh-random instead of corrupted source)
# ---------------------------------------------------------------------------
def _random_floor_binary_bipolar(M: int, N: int, seed: int) -> "torch.Tensor":
    g = np.random.default_rng(seed + 99991)
    arr = (g.integers(0, 2, size=(M, N)) * 2 - 1).astype(np.float32)
    return torch.from_numpy(arr).to(DEVICE)


def _random_floor_hrr_real(M: int, N: int, seed: int) -> "torch.Tensor":
    g = np.random.default_rng(seed + 99991)
    arr = (g.standard_normal(size=(M, N)) / math.sqrt(N)).astype(np.float32)
    norms = np.linalg.norm(arr, axis=1, keepdims=True).clip(min=1e-12)
    arr = arr / norms
    return torch.from_numpy(arr).to(DEVICE)


def _random_floor_fhrr(M: int, N: int, seed: int) -> "torch.Tensor":
    n_complex = N // 2
    g = np.random.default_rng(seed + 99991)
    phi = g.uniform(0.0, 2.0 * math.pi, size=(M, n_complex)).astype(np.float32)
    real = np.cos(phi).astype(np.float32)
    imag = np.sin(phi).astype(np.float32)
    arr = np.empty((M, n_complex), dtype=np.complex64)
    arr.real = real
    arr.imag = imag
    return torch.from_numpy(arr).to(DEVICE)


def _random_floor_sparse_bipolar(M: int, N: int, seed: int) -> "torch.Tensor":
    g = np.random.default_rng(seed + 99991)
    s = max(1, int(round(SPARSE_DENSITY * N)))
    arr = np.zeros((M, N), dtype=np.float32)
    for i in range(M):
        idx = g.choice(N, size=s, replace=False)
        signs = g.integers(0, 2, size=s).astype(np.float32) * 2.0 - 1.0
        arr[i, idx] = signs
    return torch.from_numpy(arr).to(DEVICE)


# ---------------------------------------------------------------------------
# Score + cleanup per encoder
# ---------------------------------------------------------------------------
def _score_real(Q: "torch.Tensor", X: "torch.Tensor") -> "torch.Tensor":
    """Real inner product (binary_bipolar, hrr_real, sparse_bipolar)."""
    return Q @ X.T


def _score_fhrr(Q: "torch.Tensor", X: "torch.Tensor") -> "torch.Tensor":
    """Re(Q . conj(X.T)) for FHRR complex codes; returns real float32."""
    # Q is (M, n_complex) complex64; X.T is (n_complex, M) complex64
    # Want sim[i, j] = Re(sum_k Q[i, k] * conj(X[j, k]))
    sims = (Q @ X.conj().T).real  # (M, M) complex64 -> .real -> float32
    return sims.to(torch.float32)


def _sign_op_bipolar(V: "torch.Tensor") -> "torch.Tensor":
    """sign() with 0 -> +1 to stay bipolar."""
    out = torch.sign(V)
    return torch.where(out == 0, torch.ones_like(out), out)


def _sign_op_hrr_real(V: "torch.Tensor") -> "torch.Tensor":
    """L2-normalize per row (HRR-real stays in real unit-sphere space)."""
    norms = torch.linalg.norm(V, dim=1, keepdim=True).clamp(min=1e-12)
    return V / norms


def _sign_op_fhrr(V: "torch.Tensor") -> "torch.Tensor":
    """Per-bin unit-modulus normalize (FHRR stays on torus)."""
    mag = torch.abs(V).clamp(min=1e-12)
    return V / mag


def _sign_op_sparse_bipolar(V: "torch.Tensor") -> "torch.Tensor":
    """Top-s-magnitude active + sign; sparse-bipolar projection.

    Keep top-s entries by magnitude per row; set rest to 0; sign of kept.
    """
    M, N = V.shape
    s = max(1, int(round(SPARSE_DENSITY * N)))
    out = torch.zeros_like(V)
    # topk by abs
    abs_V = torch.abs(V)
    _, idx = torch.topk(abs_V, k=s, dim=1)
    # gather signs at top-k positions
    src_signs = torch.sign(torch.gather(V, 1, idx))
    src_signs = torch.where(src_signs == 0, torch.ones_like(src_signs), src_signs)
    out.scatter_(1, idx, src_signs)
    return out


def _hopfield_cleanup(Q0: "torch.Tensor", X: "torch.Tensor", T: int, beta: float,
                       score_fn: Callable, sign_op: Callable) -> "torch.Tensor":
    """T-step modern-Hopfield cleanup with family-specific score + sign_op.

    Q_{t+1} = sign_op( softmax(beta * score(Q_t, X)) @ X ).
    """
    Q = Q0
    for _ in range(max(0, T)):
        sims = score_fn(Q, X)  # (M, M_items) real float32
        p = torch.softmax(beta * sims, dim=1)  # (M, M_items)
        # mix codes back: for complex (FHRR), p (real) @ X (complex) works
        # because complex tensors support real-matrix multiply
        if X.is_complex():
            # broadcast: p is float32 (M, M); X is complex64 (M, n_complex)
            Q_new = (p.to(torch.complex64) @ X)  # (M, n_complex) complex64
        else:
            Q_new = p @ X  # (M, N) float32
        Q = sign_op(Q_new)
    return Q


def _top1_recall(Q_final: "torch.Tensor", X: "torch.Tensor",
                  target_idx: "torch.Tensor", score_fn: Callable) -> float:
    """Top-1 recall: fraction where argmax(score(Q, X)) == target_idx."""
    sims = score_fn(Q_final, X)
    preds = sims.argmax(dim=1)
    hits = int((preds == target_idx).sum().item())
    return hits / max(int(target_idx.shape[0]), 1)


# ---------------------------------------------------------------------------
# Encoder family registry
# ---------------------------------------------------------------------------
_ENCODER_REGISTRY = {
    "binary_bipolar": {
        "build": _build_binary_bipolar,
        "corrupt": _corrupt_binary_bipolar,
        "random_floor": _random_floor_binary_bipolar,
        "score": _score_real,
        "sign_op": _sign_op_bipolar,
        "dtype_label": "float32",
    },
    "hrr_real": {
        "build": _build_hrr_real,
        "corrupt": _corrupt_hrr_real,
        "random_floor": _random_floor_hrr_real,
        "score": _score_real,
        "sign_op": _sign_op_hrr_real,
        "dtype_label": "float32",
    },
    "fhrr": {
        "build": _build_fhrr,
        "corrupt": _corrupt_fhrr,
        "random_floor": _random_floor_fhrr,
        "score": _score_fhrr,
        "sign_op": _sign_op_fhrr,
        "dtype_label": "complex64",
    },
    "sparse_bipolar": {
        "build": _build_sparse_bipolar,
        "corrupt": _corrupt_sparse_bipolar,
        "random_floor": _random_floor_sparse_bipolar,
        "score": _score_real,
        "sign_op": _sign_op_sparse_bipolar,
        "dtype_label": "float32",
    },
}


# ---------------------------------------------------------------------------
# Per-point evaluation
# ---------------------------------------------------------------------------
def eval_phase_point(encoder_family: str, N: int, corruption: float, T: int,
                      M: int, seed: int) -> Dict[str, Any]:
    """Run one (encoder, N, c, T) phase point with both arms.

    Returns dict with top1_mechanism, top1_random, discriminator, tier,
    peak_mem_mb, elapsed_s, and per-arm hashes.
    """
    if encoder_family not in _ENCODER_REGISTRY:
        raise ValueError(f"unknown encoder_family={encoder_family!r}")
    reg = _ENCODER_REGISTRY[encoder_family]

    t0 = time.time()
    if _CUDA_OK:
        torch.cuda.empty_cache()
        torch.cuda.reset_peak_memory_stats()

    # Build codebook + targets (encoder hoisted once per phase point)
    X = reg["build"](M, N, seed)
    target_idx = torch.arange(M, device=DEVICE)
    sub_seed = seed * 1000 + int(corruption * 1000)

    # ARM_MECHANISM: encoder's corruption -> encoder's cleanup
    Q_sub_0 = reg["corrupt"](X, corruption, sub_seed)
    Q_sub_T = _hopfield_cleanup(Q_sub_0, X, T, BETA, reg["score"], reg["sign_op"])
    top1_sub = _top1_recall(Q_sub_T, X, target_idx, reg["score"])

    # ARM_RANDOM_FLOOR: fresh-random codebook entry instead of corrupted source
    Q_rnd_0 = reg["random_floor"](M, N, sub_seed)
    Q_rnd_T = _hopfield_cleanup(Q_rnd_0, X, T, BETA, reg["score"], reg["sign_op"])
    top1_rnd = _top1_recall(Q_rnd_T, X, target_idx, reg["score"])

    # Calibration check: initial cosine of Q_sub_0 vs X (sanity per META_RULE_AG)
    # Just first 20 items for speed; full calibration is in selftest
    cal_sample = min(20, M)
    if X.is_complex():
        cal_sims = (Q_sub_0[:cal_sample] * X[:cal_sample].conj()).real.sum(dim=1)
        # Normalize: |X| = sqrt(n_complex) for unit-modulus
        n_complex = X.shape[1]
        cal_cos = float(cal_sims.mean().item()) / max(n_complex, 1)
    else:
        # Real cosine
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

    # Per-point verdict tier
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

    del X, Q_sub_0, Q_sub_T, Q_rnd_0, Q_rnd_T, target_idx
    if _CUDA_OK:
        torch.cuda.empty_cache()

    return {
        "encoder_family": encoder_family,
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
            crlb_1step_cliff_prediction(N, M, encoder_family), 4),
        "dtype_label": reg["dtype_label"],
    }


# ---------------------------------------------------------------------------
# Selftest (encoder calibration + CRLB + cardinality + sanity)
# ---------------------------------------------------------------------------
def selftest(seed: int) -> Tuple[bool, str]:
    """Encoder calibration + CRLB formula + cardinality + sanity.

    For each encoder: verify mean cos(Q_corrupted, source) within
    [1 - 2c - 0.10, 1 - 2c + 0.10] at c in {0.10, 0.30, 0.50}, N=2048, M=50.
    """
    msgs: List[str] = []

    # 1. Cardinality math
    if EXPECTED_N_UNITS_FULL != 80:
        return False, f"FULL cardinality {EXPECTED_N_UNITS_FULL} != 80"
    if EXPECTED_N_UNITS_SMOKE != 12:
        return False, f"SMOKE cardinality {EXPECTED_N_UNITS_SMOKE} != 12"
    msgs.append(f"cardinality FULL={EXPECTED_N_UNITS_FULL} SMOKE={EXPECTED_N_UNITS_SMOKE}")

    # 2. CRLB formula sanity (N=2048, M=300 cliff in [0.40, 0.50])
    c1 = crlb_1step_cliff_prediction(2048, M_ITEMS_FULL, "binary_bipolar")
    c2 = crlb_1step_cliff_prediction(8192, M_ITEMS_FULL, "binary_bipolar")
    if not (0.40 < c1 < 0.50):
        return False, f"crlb N=2048 M=300 outside [0.40, 0.50]: {c1}"
    if not (0.40 < c2 < 0.50):
        return False, f"crlb N=8192 M=300 outside [0.40, 0.50]: {c2}"
    if not (c2 > c1):
        return False, f"cliff should shift right with N: c1={c1} c2={c2}"
    msgs.append(f"crlb N=2048 cliff={c1:.4f}; N=8192 cliff={c2:.4f}")

    # 3. Encoder calibration (the LOAD-BEARING selftest)
    # For each encoder at N=2048, M=50, verify E[cos(Q_corrupted, source)]
    # is in [1-2c - 0.10, 1-2c + 0.10] at c in {0.10, 0.30, 0.50}.
    M_cal = 50
    N_cal = 2048
    cal_c_list = [0.10, 0.30, 0.50]
    cal_tol = 0.10

    for fam in ENCODER_FAMILIES:
        reg = _ENCODER_REGISTRY[fam]
        X = reg["build"](M_cal, N_cal, seed)
        for c in cal_c_list:
            sub_seed = seed * 1000 + int(c * 1000)
            Q = reg["corrupt"](X, c, sub_seed)
            # Compute mean cosine
            if X.is_complex():
                dots = (Q * X.conj()).real.sum(dim=1)
                # FHRR: unit-modulus per bin; |X|^2 = n_complex
                n_complex = X.shape[1]
                cos_mean = float(dots.mean().item()) / max(n_complex, 1)
            else:
                Q_norm = torch.linalg.norm(Q, dim=1).clamp(min=1e-12)
                X_norm = torch.linalg.norm(X, dim=1).clamp(min=1e-12)
                cos_per = (Q * X).sum(dim=1) / (Q_norm * X_norm)
                cos_mean = float(cos_per.mean().item())
            target = 1.0 - 2.0 * c
            if abs(cos_mean - target) > cal_tol:
                return False, (
                    f"encoder calibration FAIL {fam}@c={c}: measured cos="
                    f"{cos_mean:.4f}, target={target:.4f}, tol={cal_tol}")
            msgs.append(f"cal {fam}@c={c}: cos={cos_mean:.4f} target={target:.4f} OK")
        del X
        if _CUDA_OK:
            torch.cuda.empty_cache()

    # 4. Mechanism sanity: at c=0.10, N=512, M=20, each encoder must
    # recover item 0 after T=1 cleanup
    M_san = 20
    N_san = 512
    for fam in ENCODER_FAMILIES:
        reg = _ENCODER_REGISTRY[fam]
        X = reg["build"](M_san, N_san, seed)
        Q0 = reg["corrupt"](X, 0.10, seed * 2)
        Q1 = _hopfield_cleanup(Q0, X, 1, BETA, reg["score"], reg["sign_op"])
        sims = reg["score"](Q1, X)
        target_idx = torch.arange(M_san, device=DEVICE)
        preds = sims.argmax(dim=1)
        n_hit = int((preds == target_idx).sum().item())
        if n_hit < M_san * 0.5:
            return False, (
                f"mechanism sanity FAIL {fam}: at c=0.10 N=512 M=20 only "
                f"{n_hit}/20 recovered after T=1 cleanup")
        msgs.append(f"sanity {fam}: c=0.10 N=512 M=20 T=1 recovered {n_hit}/20")
        del X, Q0, Q1
        if _CUDA_OK:
            torch.cuda.empty_cache()

    # 5. Encoder hashes differ at fixed seed (sanity: 4 encoders produce
    # distinct codebooks)
    hashes = {}
    for fam in ENCODER_FAMILIES:
        reg = _ENCODER_REGISTRY[fam]
        X = reg["build"](M_san, N_san, seed)
        # Hash the bytes (complex stored as interleaved real/imag)
        X_bytes = X.cpu().numpy().tobytes()
        h = hashlib.sha256(X_bytes).hexdigest()[:16]
        hashes[fam] = h
        del X
        if _CUDA_OK:
            torch.cuda.empty_cache()
    if len(set(hashes.values())) != len(ENCODER_FAMILIES):
        return False, f"encoder codebooks NOT distinct at seed={seed}: {hashes}"
    msgs.append(f"encoder hashes distinct: {hashes}")

    return True, "; ".join(msgs)


# ---------------------------------------------------------------------------
# Per-seed phase sweep
# ---------------------------------------------------------------------------
def run_one_seed_phase_diagram(seed: int, run_mode: str) -> Dict[str, Any]:
    """Run all (encoder, N, c, T) phase points for one seed; return result dict.

    Halts on first exception (META_RULE_J: no silent except).
    """
    is_smoke = (run_mode == "smoke")
    if is_smoke:
        N_sweep = N_SWEEP_SMOKE
        c_sweep = CORRUPTION_SMOKE
        T_sweep = ITERS_SMOKE
        M_items = M_ITEMS_SMOKE
    else:
        N_sweep = N_SWEEP_FULL
        c_sweep = CORRUPTION_FULL
        T_sweep = ITERS_FULL
        M_items = M_ITEMS_FULL

    expected_n_units = (len(ENCODER_FAMILIES) * len(N_sweep)
                         * len(c_sweep) * len(T_sweep))

    print(f"[run_one_seed] seed={seed} mode={run_mode} device={DEVICE} "
          f"encoders={ENCODER_FAMILIES} N_sweep={N_sweep} c={c_sweep} T={T_sweep} "
          f"M={M_items} expected_n={expected_n_units}", flush=True)

    crlb_preds = {f"{fam}_N{N}": round(
        crlb_1step_cliff_prediction(N, M_items, fam), 4)
        for fam in ENCODER_FAMILIES for N in N_sweep}
    print(f"[crlb] 1-step cliff predictions: {crlb_preds}", flush=True)

    phase_map: List[Dict[str, Any]] = []
    t0 = time.time()
    for fam in ENCODER_FAMILIES:
        for N in N_sweep:
            for T in T_sweep:
                for c in c_sweep:
                    print(f"[point] seed={seed} enc={fam} N={N} c={c:.3f} T={T} ...",
                          flush=True)
                    pt = eval_phase_point(fam, N, c, T, M_items, seed)
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

    # Per-encoder arms-differ hashes
    arms_differ_per_enc: Dict[str, Dict[str, Any]] = {}
    encoder_mech_hashes: Dict[str, str] = {}
    for fam in ENCODER_FAMILIES:
        fam_pts = [p for p in phase_map if p["encoder_family"] == fam]
        sub_payload = json.dumps([p["top1_mechanism"] for p in fam_pts],
                                  sort_keys=True).encode("utf-8")
        rnd_payload = json.dumps([p["top1_random"] for p in fam_pts],
                                  sort_keys=True).encode("utf-8")
        sub_hash = hashlib.sha256(sub_payload).hexdigest()
        rnd_hash = hashlib.sha256(rnd_payload).hexdigest()
        arms_differ_per_enc[fam] = {
            "mechanism_hash": sub_hash,
            "random_hash": rnd_hash,
            "differ": sub_hash != rnd_hash,
        }
        encoder_mech_hashes[fam] = sub_hash

    # Encoder-pair distinctness (META_RULE_AF extension)
    pairs_differ = {}
    fams = list(ENCODER_FAMILIES)
    for i in range(len(fams)):
        for j in range(i + 1, len(fams)):
            key = f"{fams[i]}_vs_{fams[j]}"
            pairs_differ[key] = (encoder_mech_hashes[fams[i]]
                                  != encoder_mech_hashes[fams[j]])
    n_pairs_differ = sum(1 for v in pairs_differ.values() if v)

    # Per-encoder summary (cliff locator + top1_mean + tier classification)
    per_encoder_summary: Dict[str, Dict[str, Any]] = {}
    for fam in ENCODER_FAMILIES:
        fam_pts = [p for p in phase_map if p["encoder_family"] == fam]
        top1s = [p["top1_mechanism"] for p in fam_pts]
        top1_mean = float(np.mean(top1s)) if top1s else 0.0
        n_sat = sum(1 for p in fam_pts if p["verdict_tier_per_point"] == "SATURATED")
        n_hp = sum(1 for p in fam_pts if p["verdict_tier_per_point"] == "HARD_PASS")
        n_mb = sum(1 for p in fam_pts if p["verdict_tier_per_point"] == "MIDDLE_BAND")
        n_floor = sum(1 for p in fam_pts if p["verdict_tier_per_point"] == "FLOOR")
        n_fail = sum(1 for p in fam_pts if p["verdict_tier_per_point"] == "HARD_FAIL")
        # Cliff locator: per (N, T), smallest c where top1 < 0.50
        cliff_locator: Dict[str, float] = {}
        for N in N_sweep:
            for T in T_sweep:
                cliff = -1.0
                for c in c_sweep:
                    matches = [p for p in fam_pts
                               if p["N"] == N and p["cleanup_iters"] == T
                               and abs(p["corruption_frac"] - c) < 1e-6]
                    if matches and matches[0]["top1_mechanism"] < MIDDLE_BAND_LO:
                        cliff = c
                        break
                cliff_locator[f"N{N}_T{T}"] = cliff
        per_encoder_summary[fam] = {
            "top1_mean": round(top1_mean, 4),
            "tier_counts": {"SATURATED": n_sat, "HARD_PASS": n_hp,
                            "MIDDLE_BAND": n_mb, "FLOOR": n_floor,
                            "HARD_FAIL": n_fail},
            "cliff_locator": cliff_locator,
        }

    # Tier the encoders (DOMINANT / COMPETITIVE / DOMINATED)
    means = {fam: per_encoder_summary[fam]["top1_mean"] for fam in ENCODER_FAMILIES}
    best_mean = max(means.values()) if means else 0.0
    encoder_tiers: Dict[str, str] = {}
    for fam in ENCODER_FAMILIES:
        m = means[fam]
        if m >= best_mean - 0.05:
            if m == best_mean:
                # Check if strictly dominant (> 0.10 above next best)
                others = [v for k, v in means.items() if k != fam]
                next_best = max(others) if others else 0.0
                if m - next_best > 0.10:
                    encoder_tiers[fam] = "DOMINANT_ENCODER"
                else:
                    encoder_tiers[fam] = "COMPETITIVE_ENCODER"
            else:
                encoder_tiers[fam] = "COMPETITIVE_ENCODER"
        else:
            encoder_tiers[fam] = "DOMINATED_ENCODER"

    # Positive control check
    pc_target = POSITIVE_CONTROL_SMOKE if is_smoke else POSITIVE_CONTROL
    pc_matches = [p for p in phase_map
                  if p["encoder_family"] == pc_target["encoder_family"]
                  and p["N"] == pc_target["N"]
                  and abs(p["corruption_frac"] - pc_target["corruption_frac"]) < 1e-6
                  and p["cleanup_iters"] == pc_target["cleanup_iters"]]
    if pc_matches:
        pc_top1 = pc_matches[0]["top1_mechanism"]
        pc_pass = pc_top1 >= pc_target["top1_floor"]
    else:
        pc_top1 = -1.0
        pc_pass = False

    positive_control_result = {
        "target": pc_target,
        "measured_top1": pc_top1,
        "pass": pc_pass,
    }

    return {
        "seed": seed,
        "run_mode": run_mode,
        "encoder_families": list(ENCODER_FAMILIES),
        "N_sweep": N_sweep,
        "corruption_sweep": c_sweep,
        "iters_sweep": T_sweep,
        "M_items": M_items,
        "N": max(N_sweep),  # PROT-021 N stamp (highest N in sweep)
        "phase_map": phase_map,
        "per_encoder_summary": per_encoder_summary,
        "encoder_tiers": encoder_tiers,
        "encoder_pair_distinctness": pairs_differ,
        "n_pairs_differ": n_pairs_differ,
        "arms_differ_per_encoder": arms_differ_per_enc,
        "positive_control_result": positive_control_result,
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
    """Pre-reg smoke gate. Return (passed, reason)."""
    phase_map = body.get("phase_map", [])
    arms_differ = body.get("arms_differ_per_encoder", {})
    pairs_differ = body.get("encoder_pair_distinctness", {})
    expected_n = body.get("expected_n_units", 0)
    pc_result = body.get("positive_control_result", {})
    per_enc = body.get("per_encoder_summary", {})

    # 1. Cardinality
    if len(phase_map) != expected_n:
        return False, f"cardinality_breach: expected {expected_n} got {len(phase_map)}"

    # 2. arms_differ for ALL encoders
    for fam in ENCODER_FAMILIES:
        ad = arms_differ.get(fam, {})
        if not ad.get("differ"):
            return False, f"arms_identical_encoder_{fam}: mech and random hashes match"

    # 3. 4 distinct encoder mechanism hashes (all 6 pairs differ)
    n_pairs = len(pairs_differ)
    n_distinct = sum(1 for v in pairs_differ.values() if v)
    if n_distinct < n_pairs:
        # Find which pair collapsed
        collapsed = [k for k, v in pairs_differ.items() if not v]
        return False, (f"encoder_collapse: {n_distinct}/{n_pairs} encoder pairs "
                        f"distinct; identical pairs: {collapsed}")

    # 4. Positive control
    if not pc_result.get("pass"):
        return False, (f"positive_control_fail: target={pc_result.get('target')} "
                        f"measured={pc_result.get('measured_top1')}; "
                        f"test rig broken")

    # 5. Cliff observable: at least 1 encoder shows top1 in [0.10, 0.95] at c=0.45
    cliff_pts = [p for p in phase_map
                  if abs(p["corruption_frac"] - 0.45) < 1e-6
                  and 0.10 < p["top1_mechanism"] < 0.95]
    if not cliff_pts:
        cliff_vals = {f"{p['encoder_family']}_N{p['N']}": p["top1_mechanism"]
                      for p in phase_map if abs(p["corruption_frac"] - 0.45) < 1e-6}
        return False, (f"discriminator_fails_scale: c=0.45 produced no cliff-edge "
                        f"values at any encoder/N; all in [0, 0.10] or [0.95, 1.0]: "
                        f"{cliff_vals}; ABORT FULL DISPATCH")

    return True, (f"smoke_gate_pass: cardinality_ok + arms_differ(4 encs) + "
                  f"4-distinct-encoders + positive_control_pass + cliff_observable")


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
    arms_differ = body.get("arms_differ_per_encoder", {})
    pairs_differ = body.get("encoder_pair_distinctness", {})
    n_pairs_differ = body.get("n_pairs_differ", 0)
    pc_result = body.get("positive_control_result", {})
    per_enc_summary = body.get("per_encoder_summary", {})
    encoder_tiers = body.get("encoder_tiers", {})
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

    # Tier counts (overall)
    n_hp = sum(1 for p in phase_map if p["verdict_tier_per_point"] == "HARD_PASS")
    n_mb = sum(1 for p in phase_map if p["verdict_tier_per_point"] == "MIDDLE_BAND")
    n_sat = sum(1 for p in phase_map if p["verdict_tier_per_point"] == "SATURATED")
    n_floor = sum(1 for p in phase_map if p["verdict_tier_per_point"] == "FLOOR")
    n_fail = sum(1 for p in phase_map if p["verdict_tier_per_point"] == "HARD_FAIL")
    n_disc = n_hp + n_mb

    common = {
        "phase_map": phase_map,
        "per_encoder_summary": per_enc_summary,
        "encoder_tiers": encoder_tiers,
        "encoder_pair_distinctness": pairs_differ,
        "n_pairs_differ": n_pairs_differ,
        "arms_differ_per_encoder": arms_differ,
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
        "sparse_density": SPARSE_DENSITY,
    }

    if is_smoke:
        passed, reason = smoke_gate_predicate(body)
        if passed:
            verdict = "HARD_PASS"
            vmsg = (f"HARD_PASS_SMOKE: {observed_n}/{expected_n} pts; "
                    f"sat={n_sat} hp={n_hp} mb={n_mb} floor={n_floor} fail={n_fail}; "
                    f"4-encoder-distinct; positive_control@"
                    f"{pc_result.get('target', {}).get('encoder_family')}"
                    f" top1={pc_result.get('measured_top1'):.3f}; "
                    f"encoder_tiers={encoder_tiers}; "
                    f"gpu_util~{gpu_util_estimate:.2f}")
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
        vmsg = (f"HARD_FAIL_CARDINALITY_BREACH: expected={expected_n} "
                f"observed={observed_n}")
    elif any(not ad.get("differ") for ad in arms_differ.values()):
        bad = [fam for fam in ENCODER_FAMILIES
               if not arms_differ.get(fam, {}).get("differ")]
        verdict = "HARD_FAIL"
        vmsg = f"HARD_FAIL_ARMS_IDENTICAL: encoders with mech==random: {bad}"
    elif not pc_result.get("pass"):
        verdict = "HARD_FAIL"
        vmsg = (f"HARD_FAIL_CONTROL_FAIL: positive_control "
                f"{pc_result.get('target')} measured top1="
                f"{pc_result.get('measured_top1')}; test rig broken; "
                f"any encoder-discrimination framing UNTRUSTED")
    elif n_pairs_differ == 0:
        verdict = "MIDDLE_BAND"
        vmsg = (f"MIDDLE_BAND_NULL_ENCODER_INVARIANCE: all 4 encoders produced "
                f"identical mechanism hashes; encoder is NOT a discriminating "
                f"lever for PC in this regime; honest negative; n_disc={n_disc}/80; "
                f"sat={n_sat} hp={n_hp} mb={n_mb} floor={n_floor} fail={n_fail}")
    elif n_disc >= 24 and n_pairs_differ >= 2:
        # Check at least one encoder has a real interior cliff
        any_real_cliff = False
        for fam, summ in per_enc_summary.items():
            for cliff_key, cliff_val in summ.get("cliff_locator", {}).items():
                if 0.20 < cliff_val < 0.50:
                    any_real_cliff = True
                    break
            if any_real_cliff:
                break
        if any_real_cliff:
            verdict = "HARD_PASS"
            vmsg = (f"HARD_PASS_ENCODER_DISCRIMINATION: {observed_n}/{expected_n} pts; "
                    f"sat={n_sat} hp={n_hp} mb={n_mb} floor={n_floor} fail={n_fail}; "
                    f"n_pairs_differ={n_pairs_differ}/6; encoder_tiers={encoder_tiers}; "
                    f"positive_control_pass; gpu_util~{gpu_util_estimate:.2f}")
        else:
            verdict = "MIDDLE_BAND"
            vmsg = (f"MIDDLE_BAND_ENCODER_DIFFERS_BUT_NO_CLIFF: encoders distinguish "
                    f"but no interior cliff at any encoder; n_disc={n_disc}/80; "
                    f"n_pairs_differ={n_pairs_differ}/6; encoder_tiers={encoder_tiers}")
    else:
        verdict = "MIDDLE_BAND"
        vmsg = (f"MIDDLE_BAND_ENCODER_DIFFERS_BUT_LOW_DISC: n_disc={n_disc}/80 "
                f"(need >=24); n_pairs_differ={n_pairs_differ}/6 (need >=2); "
                f"sat={n_sat} hp={n_hp} mb={n_mb} floor={n_floor} fail={n_fail}; "
                f"encoder_tiers={encoder_tiers}")

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
    "HP_DISCRIMINATOR", "MB_DISCRIMINATOR", "BETA", "SPARSE_DENSITY",
    "ENCODER_FAMILIES",
    "N_SWEEP_FULL", "CORRUPTION_FULL", "ITERS_FULL", "M_ITEMS_FULL",
    "N_SWEEP_SMOKE", "CORRUPTION_SMOKE", "ITERS_SMOKE", "M_ITEMS_SMOKE",
    "EXPECTED_N_UNITS_FULL", "EXPECTED_N_UNITS_SMOKE",
    "POSITIVE_CONTROL", "POSITIVE_CONTROL_SMOKE",
    "REQUIRED_FIELDS",
    "crlb_1step_cliff_prediction", "get_backend_label",
    "eval_phase_point", "selftest",
    "run_one_seed_phase_diagram",
    "smoke_gate_predicate", "aggregate_and_verdict",
]
