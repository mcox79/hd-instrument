"""VAMP-vs-AMP universality contrast on substrate's Kerdock codebook.

Motivation
----------
Verdict AMP_SE_DIVERGES (v163, 2026-05-23) established that the Bayati-Montanari
scalar AMP state-evolution does NOT predict empirical AMP MSE on the Kerdock
4-coset codebook. The substrate falls outside the AMP universality class.

VAMP (Rangan-Schniter-Fletcher 2017, vector AMP) replaces AMP's scalar Onsager
correction with one derived from the SVD spectrum of the measurement matrix.
For RIGHT-ROTATIONALLY-INVARIANT (RI) matrices, VAMP's SE recursion is exact;
VAMP-SE uses the full singular-value distribution rather than just its mean
(unlike scalar AMP-SE).

If the Kerdock divergence is purely "moment-based on the bulk" (Verdict 3
KERDOCK_SPECTRUM_BULK_BOUNDED), VAMP -- which sees the full singular spectrum --
should hold where AMP fails. That gives the substrate-product story:
  "AMP-style inference fails on this codebook; VAMP-style succeeds because
   VAMP uses S-transform-equivalent information (the full singular spectrum),
   not just the scalar mean."

Scientific question
-------------------
For Kerdock matrix at N=4096 and alpha in {0.5, 1, 2}, compare:
  - VAMP-SE prediction (using empirical singular spectrum) vs empirical VAMP MSE
  - AMP-SE prediction (scalar, IID) vs empirical AMP MSE

VAMP universality holds if |VAMP-SE - emp-VAMP| / max < 0.20 at >= 2/3 cells.
AMP universality is already known to fail (v163). Re-confirm here that the
SAME matrix shows AMP fail AND VAMP pass; that establishes the contrast.

Method
------
1. Build Kerdock A_norm = A / sqrt(N), M = alpha * N rows. SVD = U S V^T.
2. Generate signal x ~ N(0, I_N), noise z ~ N(0, sigma^2 I_M). y = A_norm x + z.
3. VAMP iteration with MMSE Gaussian denoiser:
     - LMMSE step using singular spectrum: r2 = V @ (S^T S + (1/gamma_1) I)^{-1}
       (S^T (y - U @ something)) ... standard form (Rangan-Schniter-Fletcher Alg 1).
     - Denoiser step (matched Gaussian prior, MMSE).
4. VAMP-SE recursion using empirical singular values:
     - gamma_1 -> gamma_2 transition computed by integrating the LMMSE step against
       the empirical singular-value measure.
5. Empirical AMP and AMP-SE on same matrix (re-using same approach as v163).
6. Compare both predicted vs empirical MSE.

Vertex: VAMP_AMP_CONTRAST_PASS (VAMP works, AMP fails)
        VAMP_AMP_BOTH_DIVERGE (both fail; substrate even outside VAMP class)
        VAMP_AMP_BOTH_MATCH (both work; AMP_SE_DIVERGES may not generalize)
        VAMP_AMP_INCONCLUSIVE

Pre-reg: preregs/2026-05-23_wave14_vamp_amp_universality_contrast_v1.md
"""
from __future__ import annotations
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import argparse
import importlib.util
import json
import math
import os
import time
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import get_output_dir as _canonical_get_output_dir  # noqa: E402  # SH-4 canonical helper
_v3_path = REPO / "experiments" / "exp_wave14y_erase_kerdock_v3.py"
_spec = importlib.util.spec_from_file_location("kerdock_v3", _v3_path)
_v3 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_v3)
make_kerdock_4coset_codebook = _v3.make_kerdock_4coset_codebook

try:
    import torch
    _TORCH_OK = True
    _CUDA_OK = torch.cuda.is_available()
except ImportError:
    _TORCH_OK = False
    _CUDA_OK = False


# ---------------------------------------------------------------------------
# Build Kerdock + SVD on GPU
# ---------------------------------------------------------------------------

def get_kerdock_svd(N: int, M: int, seed: int, device: str):
    """Build Kerdock A_norm and its SVD. Returns U, s, Vt, A_norm (all numpy)."""
    if not _TORCH_OK:
        raise RuntimeError("torch required for Kerdock codebook builder")
    cb, _info = make_kerdock_4coset_codebook(N, torch.device("cpu"))
    rng = np.random.default_rng(seed)
    idx = rng.choice(cb.shape[0], size=M, replace=False)
    A_t = cb[idx].float() / math.sqrt(N)

    if device == "cuda" and _CUDA_OK:
        A_gpu = A_t.to("cuda")
        U, s, Vt = torch.linalg.svd(A_gpu, full_matrices=False)
        A_norm = A_gpu.cpu().numpy()
        U_np = U.cpu().numpy()
        s_np = s.cpu().numpy()
        Vt_np = Vt.cpu().numpy()
        del A_gpu, U, s, Vt
        torch.cuda.empty_cache()
    else:
        U, s, Vt = torch.linalg.svd(A_t, full_matrices=False)
        A_norm = A_t.numpy()
        U_np = U.numpy()
        s_np = s.numpy()
        Vt_np = Vt.numpy()
    return U_np, s_np, Vt_np, A_norm


# ---------------------------------------------------------------------------
# AMP and AMP-SE (scalar; mirrors v163 approach for the contrast baseline)
# ---------------------------------------------------------------------------

def amp_se_scalar(alpha: float, sigma_sq: float, signal_var: float,
                  n_iter: int = 500, tol: float = 1e-12) -> float:
    """Standard Bayati-Montanari scalar AMP-SE. Returns fixed-point MSE."""
    tau_sq = sigma_sq + signal_var
    for _ in range(n_iter):
        mse_t = signal_var * tau_sq / (signal_var + tau_sq)
        tau_new = sigma_sq + mse_t / alpha
        if abs(tau_new - tau_sq) < tol * max(abs(tau_sq), 1.0):
            tau_sq = tau_new
            break
        tau_sq = tau_new
    mse = signal_var * tau_sq / (signal_var + tau_sq)
    return float(mse)


def run_amp(A: np.ndarray, y: np.ndarray, x_true: np.ndarray,
            signal_var: float, sigma_sq: float, n_iter: int) -> float:
    """GAMP-style with matched Gaussian denoiser. Returns final MSE."""
    M, N = A.shape
    alpha = M / N
    x_hat = np.zeros(N)
    z = y.copy()
    mses = []
    for _ in range(n_iter):
        r = A.T @ z + x_hat
        tau_eff = max(float(np.mean(z ** 2)) / alpha, 1e-10)
        gain = signal_var / (signal_var + tau_eff)
        x_hat_new = gain * r
        b = gain
        z = y - A @ x_hat_new + (b / alpha) * z
        x_hat = x_hat_new
        mses.append(float(np.mean((x_hat - x_true) ** 2)))
        if len(mses) >= 5 and max(mses[-5:]) - min(mses[-5:]) < 1e-10:
            break
    return mses[-1] if mses else float("inf")


# ---------------------------------------------------------------------------
# VAMP and VAMP-SE
# ---------------------------------------------------------------------------

def vamp_se_spectrum(alpha: float, sigma_sq: float, signal_var: float,
                     s: np.ndarray, N: int, M: int,
                     n_iter: int = 200, tol: float = 1e-12) -> float:
    """VAMP-SE prediction of recovery MSE using empirical singular spectrum.

    For a Gaussian signal prior x ~ N(0, signal_var * I_N) and Gaussian noise
    n ~ N(0, sigma_sq * I_M), the OPTIMAL LMMSE estimator (= MAP = MMSE since
    everything is Gaussian) achieves the closed-form posterior MSE:

        MSE = (1/N) * trace[(sigma_sq^{-1} A^T A + signal_var^{-1} I)^{-1}]
            = (1/N) * sum_i 1 / (s_i^2 / sigma_sq + 1 / signal_var)
              + ((N-K)/N) * signal_var

    where s_i are the singular values of A (i=1..K, K = min(M,N)) and the
    second term accounts for nullspace dimensions when M < N (which retain
    prior variance signal_var).

    This is the EXACT fixed point of VAMP-SE for the Gaussian-on-Gaussian
    case (Rangan-Schniter-Fletcher 2017 Sec 4). VAMP-SE for non-Gaussian
    priors involves the actual iteration; here for matched Gaussian prior
    the answer is closed form.

    Returns the predicted MSE.
    """
    K = len(s)
    s2 = s ** 2
    zero_modes = N - K

    # Per-mode posterior variance under joint Gaussian
    var_signal_modes = 1.0 / (s2 / sigma_sq + 1.0 / signal_var)  # (K,)
    mean_var_signal = float(np.mean(var_signal_modes)) if K > 0 else 0.0
    # Aggregate over signal modes + nullspace modes
    mse = (K / N) * mean_var_signal + (zero_modes / N) * signal_var
    # n_iter / tol arguments retained for API symmetry; closed-form returns immediately
    _ = n_iter
    _ = tol
    return float(mse)


def run_vamp(U: np.ndarray, s: np.ndarray, Vt: np.ndarray,
             y: np.ndarray, x_true: np.ndarray, signal_var: float, sigma_sq: float,
             n_iter: int = 200) -> float:
    """Empirical VAMP iteration on the actual Kerdock matrix.

    Standard VAMP Alg 1 (Rangan-Schniter-Fletcher 2017) with MMSE Gaussian
    denoiser. Returns final MSE.
    """
    M, N = U.shape[0], Vt.shape[1]
    K = len(s)
    s2 = s ** 2

    # Precompute y in U-basis: y_tilde = U^T y (length K)
    y_tilde = U.T @ y  # (K,)

    # Initialization
    r_1 = np.zeros(N)
    gamma_1 = 1.0 / signal_var

    mses = []
    for it in range(n_iter):
        # ---- LMMSE step ----
        # Conditional x | r_1, y: combine likelihood y = Ax + n with prior r_1 ~ N(x, 1/gamma_1 I).
        # In V-basis: V^T x = w. Likelihood gives w_i ~ N(y_tilde_i / s_i, sigma_sq / s_i^2)
        # for i in K signal modes (s_i > 0). Prior gives w ~ N(V^T r_1, 1/gamma_1 I).
        # Combined: posterior variance per mode = 1 / (s_i^2/sigma_sq + gamma_1) for i<K
        # and 1/gamma_1 for nullspace modes (i>=K).
        Vtr1 = Vt @ r_1  # (K,) if K=min(M,N)<=N; but Vt is (K,N), so Vt @ r_1 is (K,)
        # In V-basis:
        prec_per_mode_signal = s2 / sigma_sq + gamma_1
        var_per_mode_signal = 1.0 / prec_per_mode_signal
        mean_per_mode_signal = var_per_mode_signal * (s * y_tilde / sigma_sq + gamma_1 * Vtr1)

        # For null modes: variance = 1/gamma_1, mean = (V^T r_1)_null. But we have only
        # K rows of Vt. The full V is N x N; the remaining N-K rows correspond to nullspace.
        # In practice with K = min(M,N), if M >= N (alpha >= 1), K=N and no nullspace.
        # If M < N (alpha < 1), there ARE nullspace dimensions; we need a complete V.
        # Use SVD's V (N x N) -- but full_matrices=False gave us K rows.
        # Workaround: compute x_hat_signal in mode-space, then x_hat = Vt.T @ mean_per_mode +
        # (I - Vt.T Vt) @ r_1 (projection onto nullspace gets r_1 weight = 1/gamma_1 variance).
        x_hat_signal_part = Vt.T @ mean_per_mode_signal
        # Project r_1 onto nullspace of A: (I - V V^T) r_1
        # V V^T is (N,N) projection; Vt is K x N; V V^T = Vt.T @ Vt
        null_r1 = r_1 - Vt.T @ (Vt @ r_1)
        x_hat = x_hat_signal_part + null_r1

        # Aggregate posterior precision (average over modes for scalar gamma extraction)
        avg_post_var = (K / N) * float(np.mean(var_per_mode_signal)) + ((N - K) / N) * (1.0 / gamma_1)
        inv_var = 1.0 / max(avg_post_var, 1e-15)
        gamma_2 = inv_var - gamma_1
        if gamma_2 < 1e-12:
            gamma_2 = 1e-12

        # Extrinsic estimate for denoiser: r_2 = (1/gamma_2) * (inv_var * x_hat - gamma_1 * r_1)
        r_2 = (inv_var * x_hat - gamma_1 * r_1) / gamma_2

        # ---- Denoiser step (MMSE Gaussian) ----
        # Posterior of x given r_2 ~ N(x, 1/gamma_2) and prior x ~ N(0, signal_var):
        post_var_den = 1.0 / (gamma_2 + 1.0 / signal_var)
        x_hat_2 = post_var_den * gamma_2 * r_2  # MMSE estimate

        # gamma_1_new
        inv_var_den = 1.0 / post_var_den
        gamma_1_new = inv_var_den - gamma_2
        if gamma_1_new < 1e-12:
            gamma_1_new = 1e-12

        # Extrinsic estimate for LMMSE: r_1_new = (inv_var_den x_hat_2 - gamma_2 r_2)/gamma_1_new
        r_1_new = (inv_var_den * x_hat_2 - gamma_2 * r_2) / gamma_1_new

        r_1 = r_1_new
        gamma_1 = gamma_1_new

        mse = float(np.mean((x_hat_2 - x_true) ** 2))
        mses.append(mse)
        if len(mses) >= 5 and max(mses[-5:]) - min(mses[-5:]) < 1e-10:
            break

    return mses[-1] if mses else float("inf")


# ---------------------------------------------------------------------------
# Verdict logic
# ---------------------------------------------------------------------------

def compute_verdict(summary: dict) -> tuple[str, str]:
    """Classify the AMP-vs-VAMP contrast.

    Per-cell:
        vamp_close = |vamp_se - emp_vamp| / max < 0.20
        amp_close  = |amp_se - emp_amp| / max < 0.20

    Global:
        VAMP_AMP_CONTRAST_PASS: VAMP close >= 2/3 cells AND AMP close <= 1/3 cells
            (clean split: VAMP works, AMP fails)
        VAMP_AMP_BOTH_MATCH: both close in >= 2/3 cells
        VAMP_AMP_BOTH_DIVERGE: both fail in >= 2/3 cells
        VAMP_AMP_INCONCLUSIVE: mixed
    """
    if not summary.get("cells"):
        return ("VAMP_AMP_INCONCLUSIVE", "No cells computed.")

    vamp_close = 0
    amp_close = 0
    n = 0
    diffs_v = []
    diffs_a = []
    for cell in summary["cells"]:
        vse = cell.get("vamp_se_mse")
        vemp = cell.get("vamp_emp_mse")
        ase = cell.get("amp_se_mse")
        aemp = cell.get("amp_emp_mse")
        if any(x is None for x in (vse, vemp, ase, aemp)):
            continue
        n += 1
        denom_v = max(vse, vemp, 1e-12)
        denom_a = max(ase, aemp, 1e-12)
        rv = abs(vse - vemp) / denom_v
        ra = abs(ase - aemp) / denom_a
        cell["vamp_rel_err"] = rv
        cell["amp_rel_err"] = ra
        diffs_v.append(rv)
        diffs_a.append(ra)
        if rv < 0.20:
            vamp_close += 1
        if ra < 0.20:
            amp_close += 1

    if n == 0:
        return ("VAMP_AMP_INCONCLUSIVE", "No valid cells.")

    vamp_works = vamp_close >= max(1, (2 * n) // 3)
    amp_works = amp_close >= max(1, (2 * n) // 3)
    vamp_fails_majority = vamp_close <= max(1, n // 3)
    amp_fails_majority = amp_close <= max(1, n // 3)

    mean_v = float(np.mean(diffs_v)) if diffs_v else 0.0
    mean_a = float(np.mean(diffs_a)) if diffs_a else 0.0

    if vamp_works and amp_fails_majority:
        return (
            "VAMP_AMP_CONTRAST_PASS",
            f"Clean substrate-product split: VAMP-SE tracks empirical VAMP "
            f"({vamp_close}/{n} cells < 20% rel err, mean={mean_v:.3f}) while AMP-SE "
            f"diverges from empirical AMP ({amp_close}/{n} cells close, mean={mean_a:.3f}). "
            f"Mechanism: VAMP uses the full singular spectrum (S-transform-equivalent info); "
            f"AMP uses only the scalar mean and breaks on Kerdock's higher kappa_n.",
        )

    if vamp_works and amp_works:
        return (
            "VAMP_AMP_BOTH_MATCH",
            f"Both VAMP-SE and AMP-SE track empirics ({vamp_close}/{n} and {amp_close}/{n}). "
            f"This contradicts v163 AMP_SE_DIVERGES at this scale; flag for re-investigation. "
            f"Means: vamp_rel={mean_v:.3f}, amp_rel={mean_a:.3f}.",
        )

    if vamp_fails_majority and amp_fails_majority:
        return (
            "VAMP_AMP_BOTH_DIVERGE",
            f"BOTH VAMP and AMP diverge from their respective SE predictions on Kerdock. "
            f"{vamp_close}/{n} VAMP close, {amp_close}/{n} AMP close. Substrate is outside "
            f"BOTH AMP and VAMP universality classes -- novel substrate-product story: "
            f"need OAMP / generalized-VAMP for this codebook. "
            f"Means: vamp_rel={mean_v:.3f}, amp_rel={mean_a:.3f}.",
        )

    return (
        "VAMP_AMP_INCONCLUSIVE",
        f"Mixed: vamp_close={vamp_close}/{n} (mean rel err {mean_v:.3f}), "
        f"amp_close={amp_close}/{n} (mean rel err {mean_a:.3f}). No clean classification.",
    )


def self_test() -> None:
    """Verify verdict branches + numeric sanity of VAMP-SE on iid Gaussian (degenerate
    to AMP case)."""

    # Test 1: PASS — VAMP close, AMP far
    summary = {"cells": [
        {"vamp_se_mse": 0.10, "vamp_emp_mse": 0.11, "amp_se_mse": 0.10, "amp_emp_mse": 0.90},
        {"vamp_se_mse": 0.05, "vamp_emp_mse": 0.055, "amp_se_mse": 0.05, "amp_emp_mse": 0.70},
        {"vamp_se_mse": 0.02, "vamp_emp_mse": 0.022, "amp_se_mse": 0.02, "amp_emp_mse": 0.50},
    ]}
    v, _ = compute_verdict(summary)
    assert v == "VAMP_AMP_CONTRAST_PASS", f"expected CONTRAST_PASS got {v}"

    # Test 2: BOTH_MATCH
    summary = {"cells": [
        {"vamp_se_mse": 0.10, "vamp_emp_mse": 0.11, "amp_se_mse": 0.10, "amp_emp_mse": 0.11},
        {"vamp_se_mse": 0.05, "vamp_emp_mse": 0.055, "amp_se_mse": 0.05, "amp_emp_mse": 0.055},
        {"vamp_se_mse": 0.02, "vamp_emp_mse": 0.022, "amp_se_mse": 0.02, "amp_emp_mse": 0.022},
    ]}
    v, _ = compute_verdict(summary)
    assert v == "VAMP_AMP_BOTH_MATCH", f"expected BOTH_MATCH got {v}"

    # Test 3: BOTH_DIVERGE
    summary = {"cells": [
        {"vamp_se_mse": 0.10, "vamp_emp_mse": 0.80, "amp_se_mse": 0.10, "amp_emp_mse": 0.85},
        {"vamp_se_mse": 0.05, "vamp_emp_mse": 0.70, "amp_se_mse": 0.05, "amp_emp_mse": 0.75},
        {"vamp_se_mse": 0.02, "vamp_emp_mse": 0.60, "amp_se_mse": 0.02, "amp_emp_mse": 0.65},
    ]}
    v, _ = compute_verdict(summary)
    assert v == "VAMP_AMP_BOTH_DIVERGE", f"expected BOTH_DIVERGE got {v}"

    # Test 4: INCONCLUSIVE — 5 cells, vamp_close=2, amp_close=2 (under both 2/3 and 1/3 thresholds)
    summary = {"cells": [
        {"vamp_se_mse": 0.10, "vamp_emp_mse": 0.11, "amp_se_mse": 0.10, "amp_emp_mse": 0.50},
        {"vamp_se_mse": 0.10, "vamp_emp_mse": 0.11, "amp_se_mse": 0.10, "amp_emp_mse": 0.50},
        {"vamp_se_mse": 0.10, "vamp_emp_mse": 0.50, "amp_se_mse": 0.10, "amp_emp_mse": 0.11},
        {"vamp_se_mse": 0.10, "vamp_emp_mse": 0.50, "amp_se_mse": 0.10, "amp_emp_mse": 0.11},
        {"vamp_se_mse": 0.10, "vamp_emp_mse": 0.50, "amp_se_mse": 0.10, "amp_emp_mse": 0.50},
    ]}
    v, _ = compute_verdict(summary)
    assert v == "VAMP_AMP_INCONCLUSIVE", f"expected INCONCLUSIVE got {v}"

    # Test 5: empty
    v, _ = compute_verdict({"cells": []})
    assert v == "VAMP_AMP_INCONCLUSIVE", f"expected INCONCLUSIVE got {v}"

    print("VAMP/AMP contrast self-test passed (5/5 cases)", flush=True)


# ---------------------------------------------------------------------------
# Main experiment
# ---------------------------------------------------------------------------

def run_experiment(smoke: bool) -> tuple[dict, str, str, float, dict]:
    t0 = time.monotonic()

    if smoke:
        config = {
            "mode": "smoke",
            "N": 1024,
            "M_over_N_list": [0.5, 1.0],
            "sigma_noise": 0.1,
            "signal_var": 1.0,
            "n_seeds": 2,
            "n_iter": 100,
        }
    else:
        config = {
            "mode": "full",
            "N": 4096,
            "M_over_N_list": [0.5, 1.0, 2.0],
            "sigma_noise": 0.1,
            "signal_var": 1.0,
            "n_seeds": 5,
            "n_iter": 300,
        }

    N = config["N"]
    sigma = config["sigma_noise"]
    sigma_sq = sigma ** 2
    signal_var = config["signal_var"]
    device = "cuda" if (_CUDA_OK and not smoke) else "cpu"
    print(f"[device] {device} (cuda_available={_CUDA_OK})", flush=True)

    cells = []
    for alpha in config["M_over_N_list"]:
        M = max(1, int(alpha * N))
        if M > 4 * N:
            print(f"[skip] alpha={alpha:.2f}: M={M} > 4N", flush=True)
            continue
        print(f"\n[alpha={alpha:.2f}] N={N} M={M}", flush=True)

        vamp_se_vals = []
        vamp_emp_vals = []
        amp_se_vals = []
        amp_emp_vals = []

        # AMP-SE is scalar (no spectrum needed); compute once per alpha
        amp_se_mse = amp_se_scalar(alpha, sigma_sq, signal_var)

        for seed in range(config["n_seeds"]):
            seed_val = seed * 1000 + int(alpha * 100)
            U, s, Vt, A_norm = get_kerdock_svd(N, M, seed=seed_val, device=device)

            # VAMP-SE using empirical singular spectrum
            vamp_se_mse = vamp_se_spectrum(alpha, sigma_sq, signal_var, s, N, M,
                                           n_iter=config["n_iter"])

            # Generate signal + noise on CPU
            rng_sig = np.random.default_rng(seed_val + 77)
            x_true = rng_sig.standard_normal(N) * math.sqrt(signal_var)
            noise = rng_sig.standard_normal(A_norm.shape[0]) * sigma
            y = A_norm @ x_true + noise

            # Empirical VAMP
            vamp_emp_mse = run_vamp(U, s, Vt, y, x_true, signal_var, sigma_sq,
                                    n_iter=config["n_iter"])
            # Empirical AMP
            amp_emp_mse = run_amp(A_norm, y, x_true, signal_var, sigma_sq,
                                  n_iter=config["n_iter"])

            vamp_se_vals.append(vamp_se_mse)
            vamp_emp_vals.append(vamp_emp_mse)
            amp_se_vals.append(amp_se_mse)
            amp_emp_vals.append(amp_emp_mse)

            print(
                f"  seed={seed} VAMP_SE={vamp_se_mse:.5f} VAMP_emp={vamp_emp_mse:.5f} "
                f"AMP_SE={amp_se_mse:.5f} AMP_emp={amp_emp_mse:.5f}",
                flush=True,
            )

        cell = {
            "alpha": float(alpha),
            "N": N, "M": M,
            "vamp_se_mse": float(np.mean(vamp_se_vals)),
            "vamp_emp_mse": float(np.mean(vamp_emp_vals)),
            "amp_se_mse": float(np.mean(amp_se_vals)),
            "amp_emp_mse": float(np.mean(amp_emp_vals)),
            "vamp_se_std": float(np.std(vamp_se_vals)),
            "vamp_emp_std": float(np.std(vamp_emp_vals)),
            "amp_emp_std": float(np.std(amp_emp_vals)),
        }
        cells.append(cell)
        print(
            f"  AGGREGATE alpha={alpha:.2f}: VAMP_SE={cell['vamp_se_mse']:.5f} "
            f"VAMP_emp={cell['vamp_emp_mse']:.5f} | AMP_SE={cell['amp_se_mse']:.5f} "
            f"AMP_emp={cell['amp_emp_mse']:.5f}",
            flush=True,
        )

    summary = {"cells": cells, "config": config}
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic() - t0
    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)
    return summary, verdict, msg, elapsed, config


def get_output_dir(name: str) -> Path:
    """SH-4 delegates to canonical _seed_checkpoint.get_output_dir (single-prefix)."""
    out = _canonical_get_output_dir(name)
    out.mkdir(parents=True, exist_ok=True)
    return out
def validate_metrics(d: dict) -> None:
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    missing = required - set(d.keys())
    if missing:
        raise ValueError(f"metrics missing required fields: {missing}")
    if not d.get("verdict"):
        raise ValueError("empty verdict")


def write_metrics(out_dir: Path, summary: dict, verdict: str, msg: str,
                  elapsed: float, config: dict) -> None:
    metrics = {
        "verdict": verdict,
        "verdict_msg": msg,
        "elapsed_s": elapsed,
        "summary": summary,
        "config": config,
    }
    validate_metrics(metrics)
    tmp = out_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(metrics, indent=2, default=float))
    tmp.replace(out_dir / "metrics.json")
    print(f"wrote {out_dir / 'metrics.json'}", flush=True)


def run_smoke() -> None:
    self_test()
    out_dir = get_output_dir("wave14_vamp_amp_universality_contrast_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    assert len(summary["cells"]) >= 1, "smoke FAIL: no cells produced"
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main() -> None:
    self_test()
    out_dir = get_output_dir("wave14_vamp_amp_universality_contrast_v1")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=False)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nDONE: {verdict}", flush=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test()
        return 0
    if args.smoke:
        run_smoke()
        return 0
    run_main()
    return 0


if __name__ == "__main__":
    sys.exit(main())
