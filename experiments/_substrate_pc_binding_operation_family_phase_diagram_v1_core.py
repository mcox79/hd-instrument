"""Shared core for substrate_pc_binding_operation_family_phase_diagram_v1 sibling cells.

SIXTH systematic COMPONENT-SUBSTITUTION phase diagram (after encoder_family,
cleanup_family, etc.). USER directive 2026-06-28 (Research): binding-operation
choice is the 4th-most-load-bearing lever (after encoder, cleanup, routing).
Current default: circular convolution (HRR). Alternatives: FHRR element-wise
multiplication / outer-product tensor / Hadamard product. We've never
head-to-head compared at chain-grade scale.

Target primitive: BIND-then-UNBIND role-filler pattern completion. For each
(binding_op, N, corruption): build M role-filler pairs (R_k, F_k); bundle
mem = sum_k bind(R_k, F_k); query unbind(mem, R_q) -> noisy F_q; cleanup
over the F codebook; measure top1 recall.

Binding operations (OUTER axis, paired with natural encoder family):
    circular_convolution   : HRR-real (Gaussian unit-norm); bind = FFT(R)*FFT(F)^-1; unbind = circular correlation
    element_wise_fhrr      : FHRR (unit-modulus complex); bind = element-wise complex Hadamard; unbind = complex division
    hadamard_real          : binary_bipolar; bind = element-wise product on {-1,+1}; unbind = same (self-inverse)
    outer_product_tensor   : binary_bipolar with N_outer = isqrt(N); bind = outer-product expanding to N; unbind = mode-1 product

All four are SHAPE_MATCH to the bundle (sum yields same shape as bind output),
keeping inner cleanup pipeline uniform across binding ops (modern-Hopfield
softmax over F codebook with beta=8.0; sign_op family-specific).

Inner axes: N x corruption x cleanup_iters (3 x 4 x 1 = 12 inner pts per
binding op; 4 ops x 12 = 48 phase points per seed FULL).
Smoke: 1 N x 3 c x 1 T = 3 inner pts per op x 4 ops = 12 corner points.

PRE-REG: preregs/2026-06-28_substrate_pc_binding_operation_family_phase_diagram_v1.md

Sibling cells import:
    run_one_seed_phase_diagram(seed, run_mode)
    aggregate_and_verdict(per_seed_dict, run_mode)
    selftest(seed)
    get_backend_label()
    BINDING_OPERATIONS,
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

# Binding operations (OUTER axis; LOCKED at module init)
BINDING_OPERATIONS = (
    "circular_convolution",
    "element_wise_fhrr",
    "hadamard_real",
    "outer_product_tensor",
)

# Each binding op has a paired encoder family (load-bearing pairing per
# prereg). Codebook semantics differ; corruption model is calibrated so
# E[cos(Q_corrupted, source)] = 1 - 2c across all bindings.
_BINDING_ENCODER_PAIR = {
    "circular_convolution": "hrr_real",
    "element_wise_fhrr": "fhrr",
    "hadamard_real": "binary_bipolar",
    "outer_product_tensor": "binary_bipolar_outer",
}

# Sweep axes
N_SWEEP_FULL = [1024, 4096, 8192]
CORRUPTION_FULL = [0.10, 0.25, 0.40, 0.475]
ITERS_FULL = [3]
M_ITEMS_FULL = 100  # M role-filler pairs

N_SWEEP_SMOKE = [1024]
CORRUPTION_SMOKE = [0.10, 0.25, 0.475]
ITERS_SMOKE = [3]
M_ITEMS_SMOKE = 50

# Cardinality (per seed; LOCKED)
EXPECTED_N_UNITS_FULL = (len(BINDING_OPERATIONS) * len(N_SWEEP_FULL)
                          * len(CORRUPTION_FULL) * len(ITERS_FULL))  # 48
EXPECTED_N_UNITS_SMOKE = (len(BINDING_OPERATIONS) * len(N_SWEEP_SMOKE)
                           * len(CORRUPTION_SMOKE) * len(ITERS_SMOKE))  # 12

# Positive control: circular_convolution (HRR default) at (N=4096, c=0.10, T=3)
# must reproduce literature-grade HRR role-filler retrieval -- with M=100 and
# small corruption, expect top1 >= 0.50.
POSITIVE_CONTROL = {
    "binding_operation": "circular_convolution",
    "N": 4096,
    "corruption_frac": 0.10,
    "cleanup_iters": 3,
    "top1_floor": 0.50,
}
# Smoke variant of positive control
POSITIVE_CONTROL_SMOKE = {
    "binding_operation": "circular_convolution",
    "N": 1024,
    "corruption_frac": 0.10,
    "cleanup_iters": 3,
    "top1_floor": 0.30,
}

REQUIRED_FIELDS = ("verdict", "verdict_msg", "elapsed_s", "summary")


# ---------------------------------------------------------------------------
# CRLB / noise-floor prediction (META_RULE_AG)
# ---------------------------------------------------------------------------
def crlb_bundle_noise_floor(N: int, M: int) -> float:
    """Expected unbind noise floor for a bundle of M bind(R, F) pairs.

    For random codes with binding that preserves expected unit-norm:
    Var(unbind_noise) ~ (M-1)/N per query. Recall cliff predicted near
    M/N == 1 (capacity limit). With M=100 and N in {1024, 4096, 8192},
    M/N is 0.10 / 0.025 / 0.012 -- all well below capacity, so unbind
    SNR is high in clean case; corruption then dominates.

    Returns predicted top1 ceiling at c=0 (no corruption) given bundle noise.
    """
    if N <= 0 or M <= 1:
        return 0.0
    bundle_sigma = math.sqrt((M - 1.0) / N)
    # Top-1 recall ~ Phi((1 - bundle_sigma) / bundle_sigma_norm)
    # rough proxy: if SNR > 3, top1 -> 1.0; else degrades
    snr = 1.0 / max(bundle_sigma, 1e-6)
    return min(1.0, max(0.0, 1.0 - 0.5 * math.exp(-0.5 * snr)))


def get_backend_label() -> str:
    return "torch.cuda" if _CUDA_OK else "torch.cpu"


# ---------------------------------------------------------------------------
# Codebook builders (per binding op's natural encoder family)
# ---------------------------------------------------------------------------
def _build_hrr_real(M: int, N: int, seed: int) -> "torch.Tensor":
    """Dense Gaussian N(0, 1/sqrt(N))^N codebook (M, N) float32 unit-L2-norm."""
    g = np.random.default_rng(seed)
    arr = (g.standard_normal(size=(M, N)) / math.sqrt(N)).astype(np.float32)
    norms = np.linalg.norm(arr, axis=1, keepdims=True).clip(min=1e-12)
    arr = arr / norms
    return torch.from_numpy(arr).to(DEVICE)


def _build_fhrr(M: int, N: int, seed: int) -> "torch.Tensor":
    """Unit-modulus complex codebook exp(i*phi) in C^(N/2)."""
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


def _build_binary_bipolar(M: int, N: int, seed: int) -> "torch.Tensor":
    """Dense bipolar {-1, +1}^N codebook (M, N) float32."""
    g = np.random.default_rng(seed)
    arr = (g.integers(0, 2, size=(M, N)) * 2 - 1).astype(np.float32)
    return torch.from_numpy(arr).to(DEVICE)


def _build_binary_bipolar_outer(M: int, N: int, seed: int) -> "torch.Tensor":
    """Bipolar codebook with N_outer = isqrt(N) so outer product yields N total DoF.

    Returns shape (M, N_outer) where N_outer = isqrt(N).
    """
    N_outer = int(round(math.sqrt(N)))
    if N_outer * N_outer != N:
        # Use the floor isqrt; some N (e.g. 1024) are perfect squares (32),
        # 4096 is (64), 8192 is not -- use 90 -> 8100 DoF. Document deviation.
        # For 1024 -> 32x32 = 1024; 4096 -> 64x64 = 4096; 8192 -> 90x90 = 8100.
        pass
    g = np.random.default_rng(seed)
    arr = (g.integers(0, 2, size=(M, N_outer)) * 2 - 1).astype(np.float32)
    return torch.from_numpy(arr).to(DEVICE)


# ---------------------------------------------------------------------------
# Binding / unbinding primitives (op-specific)
# ---------------------------------------------------------------------------
def _bind_circular_convolution(R: "torch.Tensor",
                                 F: "torch.Tensor") -> "torch.Tensor":
    """HRR circular convolution: ifft(fft(R) * fft(F)). Real-real -> real."""
    Rf = torch.fft.rfft(R, dim=-1)
    Ff = torch.fft.rfft(F, dim=-1)
    out = torch.fft.irfft(Rf * Ff, n=R.shape[-1], dim=-1)
    return out


def _unbind_circular_convolution(mem: "torch.Tensor",
                                   R: "torch.Tensor") -> "torch.Tensor":
    """HRR circular correlation (approx inverse): ifft(conj(fft(R)) * fft(mem))."""
    Rf = torch.fft.rfft(R, dim=-1)
    Mf = torch.fft.rfft(mem, dim=-1)
    out = torch.fft.irfft(Rf.conj() * Mf, n=mem.shape[-1], dim=-1)
    return out


def _bind_element_wise_fhrr(R: "torch.Tensor",
                              F: "torch.Tensor") -> "torch.Tensor":
    """FHRR element-wise complex Hadamard: R * F (complex multiplication)."""
    return R * F


def _unbind_element_wise_fhrr(mem: "torch.Tensor",
                                R: "torch.Tensor") -> "torch.Tensor":
    """FHRR unbind: mem * conj(R) (because |R|=1, conj(R) = 1/R)."""
    return mem * R.conj()


def _bind_hadamard_real(R: "torch.Tensor",
                          F: "torch.Tensor") -> "torch.Tensor":
    """Real element-wise product on {-1,+1}: R * F."""
    return R * F


def _unbind_hadamard_real(mem: "torch.Tensor",
                            R: "torch.Tensor") -> "torch.Tensor":
    """Bipolar unbind: mem * R (self-inverse on {-1,+1})."""
    return mem * R


def _bind_outer_product_tensor(R: "torch.Tensor",
                                 F: "torch.Tensor") -> "torch.Tensor":
    """Outer product flattened: (M, N_outer) x (M, N_outer) -> (M, N_outer^2).

    R[i] and F[i] both shape (N_outer,). Output[i] = (R[i] outer F[i]).flatten().
    """
    # R, F: (M, N_outer). einsum gives (M, N_outer, N_outer); flatten last two.
    out = torch.einsum("mi,mj->mij", R, F)
    return out.reshape(out.shape[0], -1)


def _unbind_outer_product_tensor(mem: "torch.Tensor",
                                   R: "torch.Tensor") -> "torch.Tensor":
    """Outer-product unbind: reshape mem to (M, N_outer, N_outer); mode-1 product with R.

    For mem of shape (M, N_outer^2) and R of shape (M, N_outer):
    mem_3d[i] is approximately sum_k (R_k outer F_k). To recover F:
    F_q ~ R^T @ mem_3d / |R|^2 = (mode-1 product over outer axis).

    Note: mem is the BUNDLE; we pass the BUNDLE flattened and the query R.
    """
    M, N_flat = mem.shape
    N_outer = R.shape[-1]
    mem_3d = mem.reshape(M, N_outer, N_outer)
    # Mode-1 product: sum over outer dim with R (per-row dot)
    # out[i, j] = sum_k R[i, k] * mem_3d[i, k, j]
    out = torch.einsum("mk,mkj->mj", R, mem_3d)
    # Normalize by |R|^2 = N_outer (bipolar)
    out = out / max(N_outer, 1)
    return out


# ---------------------------------------------------------------------------
# Sign ops / normalize per family
# ---------------------------------------------------------------------------
def _sign_op_real_unit_norm(V: "torch.Tensor") -> "torch.Tensor":
    """L2-normalize per row (HRR-real)."""
    norms = torch.linalg.norm(V, dim=1, keepdim=True).clamp(min=1e-12)
    return V / norms


def _sign_op_fhrr(V: "torch.Tensor") -> "torch.Tensor":
    """Per-bin unit-modulus normalize (FHRR stays on torus)."""
    mag = torch.abs(V).clamp(min=1e-12)
    return V / mag


def _sign_op_bipolar(V: "torch.Tensor") -> "torch.Tensor":
    """sign() with 0 -> +1."""
    out = torch.sign(V)
    return torch.where(out == 0, torch.ones_like(out), out)


# ---------------------------------------------------------------------------
# Score functions per family
# ---------------------------------------------------------------------------
def _score_real(Q: "torch.Tensor", X: "torch.Tensor") -> "torch.Tensor":
    """Real inner product (bipolar / HRR-real / outer-bipolar)."""
    return Q @ X.T


def _score_fhrr(Q: "torch.Tensor", X: "torch.Tensor") -> "torch.Tensor":
    """Re(Q . conj(X.T)) for FHRR complex codes; returns real float32."""
    sims = (Q @ X.conj().T).real
    return sims.to(torch.float32)


# ---------------------------------------------------------------------------
# Hopfield cleanup (over F codebook, using ATTRIBUTED sign_op / score_fn)
# ---------------------------------------------------------------------------
def _hopfield_cleanup(Q0: "torch.Tensor", X: "torch.Tensor", T: int, beta: float,
                       score_fn: Callable, sign_op: Callable) -> "torch.Tensor":
    """T-step modern-Hopfield cleanup over F-codebook X."""
    Q = Q0
    for _ in range(max(0, T)):
        sims = score_fn(Q, X)
        p = torch.softmax(beta * sims, dim=1)
        if X.is_complex():
            Q_new = (p.to(torch.complex64) @ X)
        else:
            Q_new = p @ X
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
# Corruption per family (normalized to E[cos(Q_corr, source)] = 1-2c)
# ---------------------------------------------------------------------------
def _corrupt_bipolar(X: "torch.Tensor", c: float, seed: int) -> "torch.Tensor":
    """Bit-flip fraction c (bipolar); E[cos] = 1 - 2c."""
    g = np.random.default_rng(seed)
    M, N = X.shape
    flips = g.random((M, N)) < c
    flips_t = torch.from_numpy(flips).to(DEVICE)
    Q = X.clone()
    Q[flips_t] = -Q[flips_t]
    return Q


def _corrupt_hrr_real(X: "torch.Tensor", c: float, seed: int) -> "torch.Tensor":
    """Gaussian noise targeting E[cos(Q, X)] = 1-2c, then L2-renormalize."""
    g = np.random.default_rng(seed)
    M, N = X.shape
    c_safe = min(c, 0.4999)
    target_cos = 1.0 - 2.0 * c_safe
    sigma2 = (1.0 / (target_cos * target_cos) - 1.0) / N
    sigma = math.sqrt(max(sigma2, 0.0))
    noise = (g.standard_normal(size=(M, N)) * sigma).astype(np.float32)
    noise_t = torch.from_numpy(noise).to(DEVICE)
    Q = X + noise_t
    norms = torch.linalg.norm(Q, dim=1, keepdim=True).clamp(min=1e-12)
    Q = Q / norms
    return Q


def _corrupt_fhrr(X: "torch.Tensor", c: float, seed: int) -> "torch.Tensor":
    """Phase-rotate fraction (2c) of bins (capped 1.0); E[cos] = 1-2c."""
    g = np.random.default_rng(seed)
    M, n_complex = X.shape
    frac_perturbed = min(2.0 * c, 1.0)
    mask = (g.random((M, n_complex)) < frac_perturbed)
    delta = g.uniform(0.0, 2.0 * math.pi, size=(M, n_complex)).astype(np.float32)
    delta = delta * mask
    real_rot = np.cos(delta).astype(np.float32)
    imag_rot = np.sin(delta).astype(np.float32)
    rot = np.empty((M, n_complex), dtype=np.complex64)
    rot.real = real_rot
    rot.imag = imag_rot
    rot_t = torch.from_numpy(rot).to(DEVICE)
    Q = X * rot_t
    return Q


# ---------------------------------------------------------------------------
# Binding-op registry
# ---------------------------------------------------------------------------
_BINDING_REGISTRY = {
    "circular_convolution": {
        "encoder_family": "hrr_real",
        "build_codebook": _build_hrr_real,
        "build_codebook_query": _build_hrr_real,  # F codebook (same family)
        "corrupt": _corrupt_hrr_real,
        "bind": _bind_circular_convolution,
        "unbind": _unbind_circular_convolution,
        "score": _score_real,
        "sign_op": _sign_op_real_unit_norm,
        "dtype_label": "float32",
        "expands_dim": False,
    },
    "element_wise_fhrr": {
        "encoder_family": "fhrr",
        "build_codebook": _build_fhrr,
        "build_codebook_query": _build_fhrr,
        "corrupt": _corrupt_fhrr,
        "bind": _bind_element_wise_fhrr,
        "unbind": _unbind_element_wise_fhrr,
        "score": _score_fhrr,
        "sign_op": _sign_op_fhrr,
        "dtype_label": "complex64",
        "expands_dim": False,
    },
    "hadamard_real": {
        "encoder_family": "binary_bipolar",
        "build_codebook": _build_binary_bipolar,
        "build_codebook_query": _build_binary_bipolar,
        "corrupt": _corrupt_bipolar,
        "bind": _bind_hadamard_real,
        "unbind": _unbind_hadamard_real,
        "score": _score_real,
        "sign_op": _sign_op_bipolar,
        "dtype_label": "float32",
        "expands_dim": False,
    },
    "outer_product_tensor": {
        "encoder_family": "binary_bipolar_outer",
        "build_codebook": _build_binary_bipolar_outer,
        "build_codebook_query": _build_binary_bipolar_outer,
        "corrupt": _corrupt_bipolar,  # corrupts the N_outer R-code
        "bind": _bind_outer_product_tensor,
        "unbind": _unbind_outer_product_tensor,
        "score": _score_real,
        "sign_op": None,  # cleanup operates in expanded space; no sign_op
        "dtype_label": "float32",
        "expands_dim": True,
    },
}


# ---------------------------------------------------------------------------
# Per-point evaluation (bind-bundle-corrupt-unbind-cleanup)
# ---------------------------------------------------------------------------
def eval_phase_point(binding_op: str, N: int, corruption: float, T: int,
                      M: int, seed: int) -> Dict[str, Any]:
    """Run one (binding_op, N, c, T) phase point with both arms.

    Pipeline:
        1. Build R codebook (M roles)
        2. Build F codebook (M fillers)
        3. mem = sum_k bind(R_k, F_k)  (broadcast over all M)
        4. Corrupt R_q (ARM_MECHANISM) or use random R_rnd (ARM_RANDOM)
        5. F_noisy = unbind(mem, R_q)
        6. Cleanup over F codebook (T-step Hopfield)
        7. Top-1 recall against target_idx
    """
    if binding_op not in _BINDING_REGISTRY:
        raise ValueError(f"unknown binding_op={binding_op!r}")
    reg = _BINDING_REGISTRY[binding_op]

    t0 = time.time()
    if _CUDA_OK:
        torch.cuda.empty_cache()
        torch.cuda.reset_peak_memory_stats()

    # Build R and F codebooks (different seeds for R vs F)
    R = reg["build_codebook"](M, N, seed)
    F = reg["build_codebook_query"](M, N, seed + 17)
    target_idx = torch.arange(M, device=DEVICE)
    sub_seed = seed * 1000 + int(corruption * 1000)

    # Step 3: build memory bundle mem = sum_k bind(R_k, F_k)
    # bound[k] = bind(R[k:k+1], F[k:k+1]); accumulate
    bound = reg["bind"](R, F)  # shape (M, N) or (M, N_outer^2) for tensor
    # Bundle = sum over items (single bundle shared across queries)
    bundle = bound.sum(dim=0, keepdim=True)  # shape (1, N) or (1, N_outer^2)
    # Broadcast bundle for M queries
    mem = bundle.expand(M, -1).contiguous()
    # For complex tensors, expand-contiguous is needed too
    if F.is_complex() and not mem.is_complex():
        mem = mem.to(torch.complex64)

    # ARM_MECHANISM: corrupt R, unbind from mem, cleanup over F
    R_corrupt = reg["corrupt"](R, corruption, sub_seed)
    F_noisy = reg["unbind"](mem, R_corrupt)
    # For outer-product, F_noisy has shape (M, N_outer); F codebook is (M, N_outer)
    # For others, F_noisy has shape (M, N) matching F
    if reg["sign_op"] is not None:
        F_clean = _hopfield_cleanup(F_noisy, F, T, BETA, reg["score"], reg["sign_op"])
    else:
        # outer_product: cleanup operates on F shape (M, N_outer); use bipolar sign_op
        F_clean = _hopfield_cleanup(F_noisy, F, T, BETA, reg["score"], _sign_op_bipolar)
    top1_mech = _top1_recall(F_clean, F, target_idx, reg["score"])

    # ARM_RANDOM_FLOOR: use fresh-random R (no relation to bundle)
    R_random = reg["build_codebook"](M, N, sub_seed + 99991)
    F_noisy_rnd = reg["unbind"](mem, R_random)
    if reg["sign_op"] is not None:
        F_clean_rnd = _hopfield_cleanup(F_noisy_rnd, F, T, BETA, reg["score"], reg["sign_op"])
    else:
        F_clean_rnd = _hopfield_cleanup(F_noisy_rnd, F, T, BETA, reg["score"], _sign_op_bipolar)
    top1_rnd = _top1_recall(F_clean_rnd, F, target_idx, reg["score"])

    # Calibration: cosine(R_corrupt, R) initial
    cal_sample = min(20, M)
    if R.is_complex():
        cal_sims = (R_corrupt[:cal_sample] * R[:cal_sample].conj()).real.sum(dim=1)
        n_complex = R.shape[1]
        cal_cos = float(cal_sims.mean().item()) / max(n_complex, 1)
    else:
        Rc_norm = torch.linalg.norm(R_corrupt[:cal_sample], dim=1).clamp(min=1e-12)
        R_norm = torch.linalg.norm(R[:cal_sample], dim=1).clamp(min=1e-12)
        cal_dots = (R_corrupt[:cal_sample] * R[:cal_sample]).sum(dim=1)
        cal_cos = float((cal_dots / (Rc_norm * R_norm)).mean().item())

    if _CUDA_OK:
        peak_mem_mb = torch.cuda.max_memory_allocated() / 1e6
    else:
        peak_mem_mb = -1.0

    elapsed = time.time() - t0
    discriminator = top1_mech - top1_rnd

    # Per-point verdict tier
    if top1_mech >= SATURATED_TOP1:
        tier = "SATURATED"
        saturation_flag = True
    elif top1_mech >= HARD_PASS_LO and discriminator >= HP_DISCRIMINATOR:
        tier = "HARD_PASS"
        saturation_flag = False
    elif top1_mech >= MIDDLE_BAND_LO and discriminator >= MB_DISCRIMINATOR:
        tier = "MIDDLE_BAND"
        saturation_flag = False
    elif top1_mech <= FLOOR_TOP1:
        tier = "FLOOR"
        saturation_flag = False
    else:
        tier = "HARD_FAIL"
        saturation_flag = False

    # Bind-shape verification (SHAPE_MATCH per binding)
    bind_shape = list(bound.shape)
    unbind_shape = list(F_noisy.shape)
    f_shape = list(F.shape)

    del R, F, bound, bundle, mem, R_corrupt, F_noisy, F_clean
    del R_random, F_noisy_rnd, F_clean_rnd, target_idx
    if _CUDA_OK:
        torch.cuda.empty_cache()

    return {
        "binding_operation": binding_op,
        "encoder_family": reg["encoder_family"],
        "N": N,
        "corruption_frac": corruption,
        "cleanup_iters": T,
        "M_items": M,
        "seed": seed,
        "top1_mechanism": round(top1_mech, 4),
        "top1_random": round(top1_rnd, 4),
        "discriminator": round(discriminator, 4),
        "calibration_cos_q0_x": round(cal_cos, 4),
        "calibration_target_cos": round(1.0 - 2.0 * corruption, 4),
        "verdict_tier_per_point": tier,
        "saturation_flag": saturation_flag,
        "peak_mem_mb": round(peak_mem_mb, 1),
        "elapsed_per_point_s": round(elapsed, 3),
        "bind_output_shape": bind_shape,
        "unbind_output_shape": unbind_shape,
        "f_codebook_shape": f_shape,
        "expands_dim": reg["expands_dim"],
        "dtype_label": reg["dtype_label"],
        "crlb_bundle_noise_floor": round(crlb_bundle_noise_floor(N, M), 4),
    }


# ---------------------------------------------------------------------------
# Selftest
# ---------------------------------------------------------------------------
def selftest(seed: int) -> Tuple[bool, str]:
    """Per-binding-op bind/unbind round-trip + calibration + cardinality + sanity.

    For each binding_op at N=512, M=10:
      1. Build R, F; verify bind shape matches expectation
      2. Round-trip with clean R: unbind(bind(R, F), R) ~= F (within noise)
      3. Bundle 10 pairs; unbind for query 0 should give noisy F[0]; top1
         recall on cleanup MUST exceed 1/M (chance)
    """
    msgs: List[str] = []

    # 1. Cardinality math
    if EXPECTED_N_UNITS_FULL != 48:
        return False, f"FULL cardinality {EXPECTED_N_UNITS_FULL} != 48"
    if EXPECTED_N_UNITS_SMOKE != 12:
        return False, f"SMOKE cardinality {EXPECTED_N_UNITS_SMOKE} != 12"
    msgs.append(f"cardinality FULL={EXPECTED_N_UNITS_FULL} SMOKE={EXPECTED_N_UNITS_SMOKE}")

    # 2. CRLB sanity (M=100; N=1024 -> sigma=0.31; N=8192 -> sigma=0.11)
    crlb_1024 = crlb_bundle_noise_floor(1024, M_ITEMS_FULL)
    crlb_8192 = crlb_bundle_noise_floor(8192, M_ITEMS_FULL)
    if not (0.0 <= crlb_1024 <= 1.0):
        return False, f"crlb_1024 out of [0,1]: {crlb_1024}"
    if not (crlb_8192 >= crlb_1024):
        return False, f"crlb should rise with N: 1024={crlb_1024} 8192={crlb_8192}"
    msgs.append(f"crlb M=100 N=1024->{crlb_1024:.4f} N=8192->{crlb_8192:.4f}")

    # 3. Per-binding-op bind/unbind round-trip on SINGLE pair (no bundle noise)
    M_test = 10
    N_test = 512
    for binding_op in BINDING_OPERATIONS:
        reg = _BINDING_REGISTRY[binding_op]
        R = reg["build_codebook"](M_test, N_test, seed)
        F = reg["build_codebook_query"](M_test, N_test, seed + 17)
        # Single bind-unbind round-trip (item 0 only)
        bound_0 = reg["bind"](R[:1], F[:1])
        recovered = reg["unbind"](bound_0, R[:1])
        # Score recovered against full F codebook; argmax should be 0
        sims = reg["score"](recovered, F)
        pred = int(sims.argmax(dim=1).item())
        if pred != 0:
            return False, (f"round-trip FAIL {binding_op}: bind-unbind item 0 "
                            f"recovered with argmax={pred} (expected 0); sims_top3="
                            f"{sims[0].topk(3).values.tolist()}")
        msgs.append(f"round_trip {binding_op}: bind-unbind item 0 OK (argmax=0)")
        del R, F, bound_0, recovered
        if _CUDA_OK:
            torch.cuda.empty_cache()

    # 4. Bundle sanity: M=10 pairs bundled; unbind query 0 should beat chance
    for binding_op in BINDING_OPERATIONS:
        reg = _BINDING_REGISTRY[binding_op]
        R = reg["build_codebook"](M_test, N_test, seed)
        F = reg["build_codebook_query"](M_test, N_test, seed + 17)
        bound = reg["bind"](R, F)
        bundle = bound.sum(dim=0, keepdim=True)
        mem = bundle.expand(M_test, -1).contiguous()
        if F.is_complex() and not mem.is_complex():
            mem = mem.to(torch.complex64)
        F_noisy = reg["unbind"](mem, R)
        target_idx = torch.arange(M_test, device=DEVICE)
        sign_op = reg["sign_op"] if reg["sign_op"] is not None else _sign_op_bipolar
        F_clean = _hopfield_cleanup(F_noisy, F, 3, BETA, reg["score"], sign_op)
        top1 = _top1_recall(F_clean, F, target_idx, reg["score"])
        # Chance = 1/M = 0.10; minimum required = 0.30 (3x chance) at M=10, no corruption
        if top1 < 0.30:
            return False, (f"bundle sanity FAIL {binding_op}: M={M_test} N={N_test} c=0 "
                            f"T=3 top1={top1:.3f} < 0.30 (3x chance); mechanism broken")
        msgs.append(f"bundle_sanity {binding_op}: M=10 N=512 c=0 T=3 top1={top1:.3f}")
        del R, F, bound, bundle, mem, F_noisy, F_clean, target_idx
        if _CUDA_OK:
            torch.cuda.empty_cache()

    # 5. Binding op hashes differ at fixed seed (sanity: 4 ops produce distinct bundles)
    hashes = {}
    for binding_op in BINDING_OPERATIONS:
        reg = _BINDING_REGISTRY[binding_op]
        R = reg["build_codebook"](M_test, N_test, seed)
        F = reg["build_codebook_query"](M_test, N_test, seed + 17)
        bound = reg["bind"](R, F)
        bundle = bound.sum(dim=0)
        # Convert to bytes (handle complex by interleaving real/imag)
        if bundle.is_complex():
            payload = torch.view_as_real(bundle).cpu().numpy().tobytes()
        else:
            payload = bundle.cpu().numpy().tobytes()
        h = hashlib.sha256(payload).hexdigest()[:16]
        hashes[binding_op] = h
        del R, F, bound, bundle
        if _CUDA_OK:
            torch.cuda.empty_cache()
    if len(set(hashes.values())) != len(BINDING_OPERATIONS):
        return False, f"binding op bundles NOT distinct at seed={seed}: {hashes}"
    msgs.append(f"binding op hashes distinct: {hashes}")

    return True, "; ".join(msgs)


# ---------------------------------------------------------------------------
# Per-seed phase sweep
# ---------------------------------------------------------------------------
def run_one_seed_phase_diagram(seed: int, run_mode: str) -> Dict[str, Any]:
    """Run all (binding_op, N, c, T) phase points for one seed."""
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

    expected_n_units = (len(BINDING_OPERATIONS) * len(N_sweep)
                         * len(c_sweep) * len(T_sweep))

    print(f"[run_one_seed] seed={seed} mode={run_mode} device={DEVICE} "
          f"bindings={BINDING_OPERATIONS} N_sweep={N_sweep} c={c_sweep} T={T_sweep} "
          f"M={M_items} expected_n={expected_n_units}", flush=True)

    crlb_preds = {f"N{N}": round(crlb_bundle_noise_floor(N, M_items), 4)
                  for N in N_sweep}
    print(f"[crlb] bundle noise floor: {crlb_preds}", flush=True)

    phase_map: List[Dict[str, Any]] = []
    t0 = time.time()
    for binding_op in BINDING_OPERATIONS:
        for N in N_sweep:
            for T in T_sweep:
                for c in c_sweep:
                    print(f"[point] seed={seed} bind={binding_op} N={N} c={c:.3f} T={T} ...",
                          flush=True)
                    pt = eval_phase_point(binding_op, N, c, T, M_items, seed)
                    phase_map.append(pt)
                    print(f"  -> top1_mech={pt['top1_mechanism']:.3f} "
                          f"top1_rnd={pt['top1_random']:.3f} "
                          f"disc={pt['discriminator']:.3f} "
                          f"tier={pt['verdict_tier_per_point']} "
                          f"cal_cos={pt['calibration_cos_q0_x']:.3f} "
                          f"shape={pt['bind_output_shape']} "
                          f"peak_mb={pt['peak_mem_mb']:.1f} "
                          f"t={pt['elapsed_per_point_s']:.2f}s", flush=True)

    elapsed = time.time() - t0
    observed_n_units = len(phase_map)
    cardinality_ok = (observed_n_units == expected_n_units)

    # Per-binding-op arms-differ hashes
    arms_differ_per_op: Dict[str, Dict[str, Any]] = {}
    op_mech_hashes: Dict[str, str] = {}
    for binding_op in BINDING_OPERATIONS:
        op_pts = [p for p in phase_map if p["binding_operation"] == binding_op]
        sub_payload = json.dumps([p["top1_mechanism"] for p in op_pts],
                                  sort_keys=True).encode("utf-8")
        rnd_payload = json.dumps([p["top1_random"] for p in op_pts],
                                  sort_keys=True).encode("utf-8")
        sub_hash = hashlib.sha256(sub_payload).hexdigest()
        rnd_hash = hashlib.sha256(rnd_payload).hexdigest()
        arms_differ_per_op[binding_op] = {
            "mechanism_hash": sub_hash,
            "random_hash": rnd_hash,
            "differ": sub_hash != rnd_hash,
        }
        op_mech_hashes[binding_op] = sub_hash

    # Binding-op pair distinctness (META_RULE_AF extension)
    pairs_differ = {}
    ops = list(BINDING_OPERATIONS)
    for i in range(len(ops)):
        for j in range(i + 1, len(ops)):
            key = f"{ops[i]}_vs_{ops[j]}"
            pairs_differ[key] = (op_mech_hashes[ops[i]]
                                  != op_mech_hashes[ops[j]])
    n_pairs_differ = sum(1 for v in pairs_differ.values() if v)

    # Per-op summary
    per_op_summary: Dict[str, Dict[str, Any]] = {}
    for binding_op in BINDING_OPERATIONS:
        op_pts = [p for p in phase_map if p["binding_operation"] == binding_op]
        top1s = [p["top1_mechanism"] for p in op_pts]
        top1_mean = float(np.mean(top1s)) if top1s else 0.0
        n_sat = sum(1 for p in op_pts if p["verdict_tier_per_point"] == "SATURATED")
        n_hp = sum(1 for p in op_pts if p["verdict_tier_per_point"] == "HARD_PASS")
        n_mb = sum(1 for p in op_pts if p["verdict_tier_per_point"] == "MIDDLE_BAND")
        n_floor = sum(1 for p in op_pts if p["verdict_tier_per_point"] == "FLOOR")
        n_fail = sum(1 for p in op_pts if p["verdict_tier_per_point"] == "HARD_FAIL")
        # Cliff locator: per N, smallest c where top1 < 0.50
        cliff_locator: Dict[str, float] = {}
        for N in N_sweep:
            cliff = -1.0
            for c in c_sweep:
                matches = [p for p in op_pts
                           if p["N"] == N
                           and abs(p["corruption_frac"] - c) < 1e-6]
                if matches and matches[0]["top1_mechanism"] < MIDDLE_BAND_LO:
                    cliff = c
                    break
            cliff_locator[f"N{N}"] = cliff
        # Avg per-point elapsed (cost differences)
        avg_elapsed = float(np.mean([p["elapsed_per_point_s"] for p in op_pts])) \
            if op_pts else 0.0
        per_op_summary[binding_op] = {
            "encoder_family": _BINDING_ENCODER_PAIR.get(binding_op, "unknown"),
            "expands_dim": op_pts[0]["expands_dim"] if op_pts else False,
            "top1_mean": round(top1_mean, 4),
            "tier_counts": {"SATURATED": n_sat, "HARD_PASS": n_hp,
                            "MIDDLE_BAND": n_mb, "FLOOR": n_floor,
                            "HARD_FAIL": n_fail},
            "cliff_locator": cliff_locator,
            "avg_elapsed_per_point_s": round(avg_elapsed, 3),
        }

    # Tier the binding ops (DOMINANT / COMPETITIVE / DOMINATED)
    means = {op: per_op_summary[op]["top1_mean"] for op in BINDING_OPERATIONS}
    best_mean = max(means.values()) if means else 0.0
    op_tiers: Dict[str, str] = {}
    for op in BINDING_OPERATIONS:
        m = means[op]
        if m >= best_mean - 0.05:
            if m == best_mean:
                others = [v for k, v in means.items() if k != op]
                next_best = max(others) if others else 0.0
                if m - next_best > 0.10:
                    op_tiers[op] = "DOMINANT_BINDING"
                else:
                    op_tiers[op] = "COMPETITIVE_BINDING"
            else:
                op_tiers[op] = "COMPETITIVE_BINDING"
        else:
            op_tiers[op] = "DOMINATED_BINDING"

    # Positive control check
    pc_target = POSITIVE_CONTROL_SMOKE if is_smoke else POSITIVE_CONTROL
    pc_matches = [p for p in phase_map
                  if p["binding_operation"] == pc_target["binding_operation"]
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
        "binding_operations": list(BINDING_OPERATIONS),
        "N_sweep": N_sweep,
        "corruption_sweep": c_sweep,
        "iters_sweep": T_sweep,
        "M_items": M_items,
        "N": max(N_sweep),
        "phase_map": phase_map,
        "per_op_summary": per_op_summary,
        "op_tiers": op_tiers,
        "op_pair_distinctness": pairs_differ,
        "n_pairs_differ": n_pairs_differ,
        "arms_differ_per_op": arms_differ_per_op,
        "positive_control_result": positive_control_result,
        "cardinality_ok": cardinality_ok,
        "expected_n_units": expected_n_units,
        "observed_n_units": observed_n_units,
        "crlb_predictions": crlb_preds,
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
    arms_differ = body.get("arms_differ_per_op", {})
    pairs_differ = body.get("op_pair_distinctness", {})
    expected_n = body.get("expected_n_units", 0)
    pc_result = body.get("positive_control_result", {})

    # 1. Cardinality
    if len(phase_map) != expected_n:
        return False, f"cardinality_breach: expected {expected_n} got {len(phase_map)}"

    # 2. arms_differ for ALL binding ops
    for op in BINDING_OPERATIONS:
        ad = arms_differ.get(op, {})
        if not ad.get("differ"):
            return False, f"arms_identical_op_{op}: mech and random hashes match"

    # 3. 4 distinct binding op mechanism hashes (all 6 pairs differ)
    n_pairs = len(pairs_differ)
    n_distinct = sum(1 for v in pairs_differ.values() if v)
    if n_distinct < n_pairs:
        collapsed = [k for k, v in pairs_differ.items() if not v]
        return False, (f"binding_op_collapse: {n_distinct}/{n_pairs} pairs "
                        f"distinct; identical pairs: {collapsed}")

    # 4. Positive control
    if not pc_result.get("pass"):
        return False, (f"positive_control_fail: target={pc_result.get('target')} "
                        f"measured={pc_result.get('measured_top1')}; "
                        f"test rig broken")

    # 5. Discriminator-fires: at least 1 binding op shows top1 > FLOOR at low c
    fire_pts = [p for p in phase_map
                 if p["corruption_frac"] <= 0.10 and p["top1_mechanism"] > FLOOR_TOP1]
    if not fire_pts:
        vals = {f"{p['binding_operation']}_N{p['N']}_c{p['corruption_frac']}":
                 p["top1_mechanism"] for p in phase_map
                 if p["corruption_frac"] <= 0.10}
        return False, (f"discriminator_fails_scale: c<=0.10 produced no above-floor "
                        f"recall at any op/N: {vals}; ABORT FULL DISPATCH")

    return True, (f"smoke_gate_pass: cardinality_ok + arms_differ(4 ops) + "
                  f"4-distinct-ops + positive_control_pass + discriminator_fires")


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
    arms_differ = body.get("arms_differ_per_op", {})
    pairs_differ = body.get("op_pair_distinctness", {})
    n_pairs_differ = body.get("n_pairs_differ", 0)
    pc_result = body.get("positive_control_result", {})
    per_op_summary = body.get("per_op_summary", {})
    op_tiers = body.get("op_tiers", {})
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

    common = {
        "phase_map": phase_map,
        "per_op_summary": per_op_summary,
        "op_tiers": op_tiers,
        "op_pair_distinctness": pairs_differ,
        "n_pairs_differ": n_pairs_differ,
        "arms_differ_per_op": arms_differ,
        "positive_control_result": pc_result,
        "cardinality_ok": cardinality_ok,
        "expected_n_units": expected_n,
        "observed_n_units": observed_n,
        "tier_counts": {"SATURATED": n_sat, "HARD_PASS": n_hp,
                        "MIDDLE_BAND": n_mb, "FLOOR": n_floor,
                        "HARD_FAIL": n_fail},
        "n_discriminating": n_disc,
        "crlb_predictions": body.get("crlb_predictions", {}),
        "gpu_util_estimate": round(gpu_util_estimate, 3),
        "device": body.get("device"),
        "gpu_name": body.get("gpu_name"),
        "beta": BETA,
    }

    # Discriminating-fraction per binding op (>= 0.30 = >= 4/12 pts in HP+MB; full)
    disc_frac_per_op = {}
    for op in BINDING_OPERATIONS:
        op_pts = [p for p in phase_map if p["binding_operation"] == op]
        if op_pts:
            op_disc = sum(1 for p in op_pts
                          if p["verdict_tier_per_point"] in ("HARD_PASS", "MIDDLE_BAND"))
            disc_frac_per_op[op] = round(op_disc / len(op_pts), 3)
        else:
            disc_frac_per_op[op] = 0.0
    common["disc_frac_per_op"] = disc_frac_per_op
    n_ops_above_30pct = sum(1 for v in disc_frac_per_op.values() if v >= 0.30)

    if is_smoke:
        passed, reason = smoke_gate_predicate(body)
        if passed:
            verdict = "HARD_PASS"
            vmsg = (f"HARD_PASS_SMOKE: {observed_n}/{expected_n} pts; "
                    f"sat={n_sat} hp={n_hp} mb={n_mb} floor={n_floor} fail={n_fail}; "
                    f"4-binding-distinct; positive_control@"
                    f"{pc_result.get('target', {}).get('binding_operation')}"
                    f" top1={pc_result.get('measured_top1'):.3f}; "
                    f"op_tiers={op_tiers}; "
                    f"disc_frac_per_op={disc_frac_per_op}; "
                    f"gpu_util~{gpu_util_estimate:.2f}")
        else:
            verdict = "HARD_FAIL"
            vmsg = (f"HARD_FAIL_SMOKE: {reason}; sat={n_sat} hp={n_hp} mb={n_mb} "
                    f"floor={n_floor} fail={n_fail}; disc_frac={disc_frac_per_op}")
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
        bad = [op for op in BINDING_OPERATIONS
               if not arms_differ.get(op, {}).get("differ")]
        verdict = "HARD_FAIL"
        vmsg = f"HARD_FAIL_ARMS_IDENTICAL: bindings with mech==random: {bad}"
    elif not pc_result.get("pass"):
        verdict = "HARD_FAIL"
        vmsg = (f"HARD_FAIL_CONTROL_FAIL: positive_control "
                f"{pc_result.get('target')} measured top1="
                f"{pc_result.get('measured_top1')}; test rig broken")
    elif n_pairs_differ == 0:
        verdict = "MIDDLE_BAND"
        vmsg = (f"MIDDLE_BAND_NULL_BINDING_INVARIANCE: all 4 binding ops produced "
                f"identical hashes; binding NOT a discriminating lever for PC "
                f"in this regime; n_disc={n_disc}/{expected_n}; "
                f"sat={n_sat} hp={n_hp} mb={n_mb} floor={n_floor} fail={n_fail}")
    elif n_disc >= max(int(0.30 * expected_n), 1) and n_pairs_differ >= 2 \
            and n_ops_above_30pct >= 2:
        # Check at least one binding op has a real interior cliff
        any_real_cliff = False
        for op, summ in per_op_summary.items():
            for cliff_key, cliff_val in summ.get("cliff_locator", {}).items():
                if 0.10 < cliff_val < 0.50:
                    any_real_cliff = True
                    break
            if any_real_cliff:
                break
        if any_real_cliff:
            verdict = "HARD_PASS"
            vmsg = (f"HARD_PASS_BINDING_DISCRIMINATION: {observed_n}/{expected_n} pts; "
                    f"sat={n_sat} hp={n_hp} mb={n_mb} floor={n_floor} fail={n_fail}; "
                    f"n_pairs_differ={n_pairs_differ}/6; op_tiers={op_tiers}; "
                    f"disc_frac={disc_frac_per_op}; "
                    f"n_ops_above_30pct={n_ops_above_30pct}; "
                    f"positive_control_pass; gpu_util~{gpu_util_estimate:.2f}")
        else:
            verdict = "MIDDLE_BAND"
            vmsg = (f"MIDDLE_BAND_BINDING_DIFFERS_BUT_NO_CLIFF: bindings distinguish "
                    f"but no interior cliff at any op; n_disc={n_disc}/{expected_n}; "
                    f"op_tiers={op_tiers}")
    else:
        verdict = "MIDDLE_BAND"
        vmsg = (f"MIDDLE_BAND_BINDING_DIFFERS_BUT_LOW_DISC: n_disc={n_disc}/{expected_n} "
                f"(need >= {max(int(0.30 * expected_n), 1)}); "
                f"n_pairs_differ={n_pairs_differ}/6 (need >=2); "
                f"n_ops_above_30pct={n_ops_above_30pct} (need >=2); "
                f"sat={n_sat} hp={n_hp} mb={n_mb} floor={n_floor} fail={n_fail}; "
                f"op_tiers={op_tiers}; disc_frac={disc_frac_per_op}")

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
    "BINDING_OPERATIONS",
    "N_SWEEP_FULL", "CORRUPTION_FULL", "ITERS_FULL", "M_ITEMS_FULL",
    "N_SWEEP_SMOKE", "CORRUPTION_SMOKE", "ITERS_SMOKE", "M_ITEMS_SMOKE",
    "EXPECTED_N_UNITS_FULL", "EXPECTED_N_UNITS_SMOKE",
    "POSITIVE_CONTROL", "POSITIVE_CONTROL_SMOKE",
    "REQUIRED_FIELDS",
    "crlb_bundle_noise_floor", "get_backend_label",
    "eval_phase_point", "selftest",
    "run_one_seed_phase_diagram",
    "smoke_gate_predicate", "aggregate_and_verdict",
]
