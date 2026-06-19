"""BBMD-VAMP correspondence sweep: Anchor 1 for the BBMD-regime proposal.

Motivation
----------
Research note 2026-05-23 (research_promising_direction) proposes Bulk-Bounded
Moment-Divergent (BBMD) as a 12th portfolio capability candidate. The unifying
claim is that scalar-Onsager AMP's state-evolution error scales MONOTONICALLY
with the empirical kappa_n divergence integral sum |kappa_n - kappa_n^MP|
(n=2..6) while VAMP's error stays bounded across the regime.

The existing 5-axis stack all lives at alpha_interp = 1.0 (pure Kerdock). An
INTERPOLATION test is what upgrades the stack from "5 quirks on one matrix"
to "a regime with predictive power".

Method
------
Interpolate measurement matrix
    W_alpha = (1 - alpha) * G + alpha * W_kerdock
for alpha in {0, 0.25, 0.5, 0.75, 1.0}, where G is iid Gaussian-normalized.
W_kerdock comes from the substrate's 4-coset Kerdock builder (M rows, N=4096).
The mixed family preserves the M x N shape.

For each alpha and seed:
  1. Build W_alpha; full SVD.
  2. Compute spectral moments m_2..m_6 of (1/N) W^T W and invert to kappa_n.
  3. BBMD-distance = sum_{n=2..6} | kappa_n - kappa_n^MP |  (MP has kappa_n = c).
  4. AMP-SE prediction: scalar Bayati-Montanari (Gaussian prior, Gaussian noise).
  5. Empirical AMP iteration on actual W_alpha; record final MSE.
  6. VAMP-SE prediction: closed-form Gauss-Gauss using empirical singular spectrum.
  7. Empirical VAMP iteration on actual W_alpha; record final MSE.
  8. AMP-error = |AMP-SE - empirical-AMP| / max; VAMP-error analogously.

Aggregate
---------
Across the 5 alphas (averaged across seeds): compute Spearman rho between
AMP-error and BBMD-distance; record max VAMP-error.

HARD PASS (BBMD survives):
  spearman_rho(AMP-error, BBMD-distance) > 0.8
  AND max VAMP-error < 0.05 across ALL alphas (including pure-Kerdock alpha=1).

HARD FAIL (BBMD as a regime axis is killed):
  spearman_rho < 0.4 (no monotonic relationship)
  OR max VAMP-error > 0.10 at any alpha (VAMP doesn't actually tame Kerdock).

INCONCLUSIVE: anything in between.

Vertex: BBMD_VAMP_CORRESPONDENCE_PASS / KILLED / INCONCLUSIVE

Pre-reg: preregs/2026-05-23_wave14_bbmd_vamp_correspondence_sweep_v1.md
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
from scipy.stats import spearmanr

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# Reuse Kerdock 4-coset builder
_v3_path = REPO / "experiments" / "exp_wave14y_erase_kerdock_v3.py"
_spec_v3 = importlib.util.spec_from_file_location("kerdock_v3", _v3_path)
_v3 = importlib.util.module_from_spec(_spec_v3)
_spec_v3.loader.exec_module(_v3)
make_kerdock_4coset_codebook = _v3.make_kerdock_4coset_codebook

# Reuse moment-to-free-cumulant inversion + MP reference
_v1_path = REPO / "experiments" / "exp_wave14_kappa_n_profile_v1.py"
_spec_v1 = importlib.util.spec_from_file_location("kappa_v1", _v1_path)
_v1 = importlib.util.module_from_spec(_spec_v1)
_spec_v1.loader.exec_module(_v1)
moments_to_free_cumulants_general = _v1.moments_to_free_cumulants_general
mp_reference_cumulants = _v1.mp_reference_cumulants

try:
    import torch
    _TORCH_OK = True
except ImportError:
    _TORCH_OK = False


# ---------------------------------------------------------------------------
# Matrix construction: W_alpha = (1 - alpha) G + alpha W_kerdock
# ---------------------------------------------------------------------------

def build_kerdock_block(N: int, M: int, seed: int) -> np.ndarray:
    """Subsample M rows from 4N Kerdock codebook (returns shape (M, N) float32)."""
    if not _TORCH_OK:
        raise RuntimeError("torch required")
    cb, _info = make_kerdock_4coset_codebook(N, torch.device("cpu"))
    rng = np.random.default_rng(seed)
    idx = rng.choice(cb.shape[0], size=M, replace=False)
    return cb[idx].float().numpy()


def build_W_alpha(alpha: float, N: int, M: int, seed: int,
                  kerdock_cache: dict) -> np.ndarray:
    """W_alpha = (1 - alpha) * G + alpha * W_kerdock, then normalize / sqrt(N).

    The Kerdock block for a given (N, M, seed) is cached so the same realization
    is used across alphas (cleaner interpolation: only alpha varies).

    Gaussian block at the same (N, M, seed): rng_gauss = seed + 10**6 to keep
    the iid-Gaussian baseline independent of the row-subsample seed.
    """
    cache_key = (N, M, seed)
    if cache_key not in kerdock_cache:
        kerdock_cache[cache_key] = build_kerdock_block(N, M, seed)
    W_kerdock = kerdock_cache[cache_key]
    rng_g = np.random.default_rng(seed + 1_000_000)
    G = rng_g.standard_normal(size=(M, N)).astype(np.float32)
    W = (1.0 - alpha) * G + alpha * W_kerdock
    return (W / math.sqrt(N)).astype(np.float32)


# ---------------------------------------------------------------------------
# Spectral moments + kappa profile
# ---------------------------------------------------------------------------

def kappa_profile(W: np.ndarray, n_max: int) -> tuple[list[float], np.ndarray]:
    """Compute spectral moments m_1..m_n_max of (1/M) W W^T eigenvalues,
    actually we want eigenvalues of the empirical covariance W^T W / N as
    standard MP normalization. We use eigenvalues of W W^T / 1 (W already
    pre-normalized by sqrt(N) at construction) which yields the same support.

    Returns (kappas, eigenvalues).
    """
    # SVD on the smaller side
    s = np.linalg.svd(W, compute_uv=False)
    eig = (s ** 2).astype(np.float64)
    moms = [float(np.mean(eig ** n)) for n in range(1, n_max + 1)]
    kappas = moments_to_free_cumulants_general(moms)
    return kappas, eig


def bbmd_distance(kappas: list[float], c_ref: float, n_min: int = 2,
                  n_max: int = 6) -> float:
    """sum_{n=n_min..n_max} | kappa_n - kappa_n^MP |, where kappa_n^MP = c.

    Note: kappas is 1-indexed in the list (kappas[0] = kappa_1). For n=2..n_max
    we index kappas[n-1].
    """
    if not kappas or len(kappas) < n_max:
        return float("nan")
    return float(sum(abs(kappas[n - 1] - c_ref) for n in range(n_min, n_max + 1)))


# ---------------------------------------------------------------------------
# AMP / VAMP (scalar SE + closed-form Gauss-Gauss VAMP-SE + empirical loops)
# ---------------------------------------------------------------------------

def amp_se_scalar(alpha_ratio: float, sigma_sq: float, signal_var: float,
                  n_iter: int = 500, tol: float = 1e-12) -> float:
    """Standard Bayati-Montanari scalar AMP-SE for matched Gaussian prior.

    alpha_ratio = M / N.
    """
    tau_sq = sigma_sq + signal_var
    for _ in range(n_iter):
        mse_t = signal_var * tau_sq / (signal_var + tau_sq)
        tau_new = sigma_sq + mse_t / alpha_ratio
        if abs(tau_new - tau_sq) < tol * max(abs(tau_sq), 1.0):
            tau_sq = tau_new
            break
        tau_sq = tau_new
    return float(signal_var * tau_sq / (signal_var + tau_sq))


def vamp_se_closed(s: np.ndarray, N: int, M: int, sigma_sq: float,
                   signal_var: float) -> float:
    """Closed-form Gauss-Gauss posterior MSE using empirical singular spectrum.

    Per RSF 2017 Sec 4 with matched Gaussian prior x ~ N(0, signal_var I) and
    Gaussian noise n ~ N(0, sigma_sq I), the LMMSE = MMSE = optimal estimator;
    posterior covariance has trace
        (1/N) * sum_i 1 / (s_i^2 / sigma_sq + 1 / signal_var)  for i in signal modes
        + ((N - K)/N) * signal_var                              for nullspace.
    """
    K = len(s)
    s2 = s ** 2
    zero_modes = N - K
    var_signal = 1.0 / (s2 / sigma_sq + 1.0 / signal_var)
    mean_var_signal = float(np.mean(var_signal)) if K > 0 else 0.0
    return float((K / N) * mean_var_signal + (zero_modes / N) * signal_var)


def run_amp(W: np.ndarray, y: np.ndarray, x_true: np.ndarray,
            signal_var: float, sigma_sq: float, n_iter: int) -> float:
    """GAMP-style scalar AMP with matched Gaussian denoiser. Returns final MSE."""
    M, N = W.shape
    alpha_ratio = M / N
    x_hat = np.zeros(N, dtype=np.float64)
    z = y.astype(np.float64).copy()
    mses = []
    for _ in range(n_iter):
        r = W.T @ z + x_hat
        tau_eff = max(float(np.mean(z ** 2)) / alpha_ratio, 1e-10)
        gain = signal_var / (signal_var + tau_eff)
        x_hat_new = gain * r
        b = gain
        z = y - W @ x_hat_new + (b / alpha_ratio) * z
        x_hat = x_hat_new
        mses.append(float(np.mean((x_hat - x_true) ** 2)))
        if len(mses) >= 5 and max(mses[-5:]) - min(mses[-5:]) < 1e-10:
            break
    return mses[-1] if mses else float("inf")


def run_vamp(U: np.ndarray, s: np.ndarray, Vt: np.ndarray,
             y: np.ndarray, x_true: np.ndarray, signal_var: float, sigma_sq: float,
             n_iter: int = 200) -> float:
    """Standard VAMP Alg 1 (RSF 2017) with MMSE Gaussian denoiser."""
    M, N = U.shape[0], Vt.shape[1]
    K = len(s)
    s2 = s ** 2
    y_tilde = U.T @ y

    r_1 = np.zeros(N, dtype=np.float64)
    gamma_1 = 1.0 / signal_var

    mses = []
    for _ in range(n_iter):
        prec = s2 / sigma_sq + gamma_1
        var_per = 1.0 / prec
        Vtr1 = Vt @ r_1
        mean_per = var_per * (s * y_tilde / sigma_sq + gamma_1 * Vtr1)

        x_hat_signal = Vt.T @ mean_per
        null_r1 = r_1 - Vt.T @ (Vt @ r_1)
        x_hat = x_hat_signal + null_r1

        avg_post_var = (K / N) * float(np.mean(var_per)) + ((N - K) / N) * (1.0 / gamma_1)
        inv_var = 1.0 / max(avg_post_var, 1e-15)
        gamma_2 = max(inv_var - gamma_1, 1e-12)
        r_2 = (inv_var * x_hat - gamma_1 * r_1) / gamma_2

        post_var_den = 1.0 / (gamma_2 + 1.0 / signal_var)
        x_hat_2 = post_var_den * gamma_2 * r_2

        inv_var_den = 1.0 / post_var_den
        gamma_1_new = max(inv_var_den - gamma_2, 1e-12)
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
    """Compute Spearman rho(AMP-error, BBMD-distance) and max VAMP-error.

    HARD PASS: rho > 0.8 AND max VAMP-error < 0.05.
    HARD FAIL: rho < 0.4 OR max VAMP-error > 0.10.
    Otherwise INCONCLUSIVE.
    """
    cells = summary.get("cells") or []
    n_cells = len(cells)
    if n_cells < 3:
        return ("BBMD_VAMP_CORRESPONDENCE_INCONCLUSIVE",
                f"Only {n_cells} alpha cells; need >=3 for trend test.")

    # Per-cell aggregates: BBMD-distance, mean AMP-error, mean VAMP-error
    dists = []
    amp_errs = []
    vamp_errs = []
    for c in cells:
        d = c.get("bbmd_distance_mean")
        ae = c.get("amp_rel_err_mean")
        ve = c.get("vamp_rel_err_mean")
        if d is None or ae is None or ve is None:
            continue
        if not (math.isfinite(d) and math.isfinite(ae) and math.isfinite(ve)):
            continue
        dists.append(d)
        amp_errs.append(ae)
        vamp_errs.append(ve)

    if len(dists) < 3:
        return ("BBMD_VAMP_CORRESPONDENCE_INCONCLUSIVE",
                f"Only {len(dists)} valid cells with finite metrics.")

    # Spearman rho. If BBMD-distances are all equal (degenerate), return INCONCLUSIVE.
    rho_result = spearmanr(amp_errs, dists)
    rho = float(rho_result.statistic) if hasattr(rho_result, "statistic") else float(rho_result[0])
    if not math.isfinite(rho):
        return ("BBMD_VAMP_CORRESPONDENCE_INCONCLUSIVE",
                f"Spearman rho not finite (likely degenerate BBMD-distances).")

    max_vamp = max(vamp_errs)
    summary["spearman_rho"] = rho
    summary["max_vamp_rel_err"] = max_vamp
    summary["bbmd_distances"] = dists
    summary["amp_rel_errs"] = amp_errs
    summary["vamp_rel_errs"] = vamp_errs

    if rho > 0.8 and max_vamp < 0.05:
        return ("BBMD_VAMP_CORRESPONDENCE_PASS",
                f"BBMD survives: rho(AMP-error, sum|delta_kappa_n|) = {rho:.3f} > 0.8 "
                f"across {len(dists)} alpha cells; max VAMP-rel-err = {max_vamp:.4f} < 0.05. "
                f"Anchor 1 of BBMD-regime promotion lands positive. AMP-error growth "
                f"is monotonically predicted by the BBMD-distance scalar; VAMP tames "
                f"the entire interpolation from iid Gaussian to pure Kerdock.")

    if rho < 0.4 or max_vamp > 0.10:
        return ("BBMD_VAMP_CORRESPONDENCE_KILLED",
                f"BBMD as a regime axis is killed: rho = {rho:.3f} (HARD FAIL if < 0.4); "
                f"max VAMP-rel-err = {max_vamp:.4f} (HARD FAIL if > 0.10). "
                f"Either no monotonic AMP-error vs BBMD-distance relationship "
                f"(rho<0.4) or VAMP itself diverges on Kerdock (vamp>0.10).")

    return ("BBMD_VAMP_CORRESPONDENCE_INCONCLUSIVE",
            f"Borderline: rho = {rho:.3f} (PASS>0.8, FAIL<0.4), max VAMP-rel-err = "
            f"{max_vamp:.4f} (PASS<0.05, FAIL>0.10). Inconclusive regime.")


def self_test() -> None:
    """Verify (i) BBMD-distance is zero for MP cumulants, (ii) verdict branches."""

    # Test 1: BBMD-distance on MP-like cumulants (all = c) -> 0
    c = 0.5
    mp_kappas = [c] * 6
    d = bbmd_distance(mp_kappas, c, 2, 6)
    assert abs(d) < 1e-12, f"BBMD-distance on MP should be 0, got {d}"

    # Test 2: BBMD-distance on deviating cumulants
    devs = [c, c + 0.1, c + 0.2, c + 0.3, c + 0.4, c + 0.5]  # kappa_2..6 each off by 0.1..0.5
    d = bbmd_distance(devs, c, 2, 6)
    expected = 0.1 + 0.2 + 0.3 + 0.4 + 0.5
    assert abs(d - expected) < 1e-9, f"BBMD-distance want {expected}, got {d}"

    # Test 3: verdict PASS
    cells_pass = [
        {"alpha_interp": 0.0, "bbmd_distance_mean": 0.01, "amp_rel_err_mean": 0.02, "vamp_rel_err_mean": 0.01},
        {"alpha_interp": 0.25, "bbmd_distance_mean": 0.20, "amp_rel_err_mean": 0.08, "vamp_rel_err_mean": 0.02},
        {"alpha_interp": 0.50, "bbmd_distance_mean": 0.50, "amp_rel_err_mean": 0.15, "vamp_rel_err_mean": 0.02},
        {"alpha_interp": 0.75, "bbmd_distance_mean": 0.80, "amp_rel_err_mean": 0.22, "vamp_rel_err_mean": 0.03},
        {"alpha_interp": 1.0, "bbmd_distance_mean": 1.20, "amp_rel_err_mean": 0.30, "vamp_rel_err_mean": 0.04},
    ]
    v, _ = compute_verdict({"cells": cells_pass})
    assert v == "BBMD_VAMP_CORRESPONDENCE_PASS", f"expected PASS got {v}"

    # Test 4: verdict KILLED via low rho
    cells_killed_rho = [
        {"alpha_interp": 0.0, "bbmd_distance_mean": 0.01, "amp_rel_err_mean": 0.20, "vamp_rel_err_mean": 0.02},
        {"alpha_interp": 0.25, "bbmd_distance_mean": 0.20, "amp_rel_err_mean": 0.05, "vamp_rel_err_mean": 0.02},
        {"alpha_interp": 0.50, "bbmd_distance_mean": 0.50, "amp_rel_err_mean": 0.15, "vamp_rel_err_mean": 0.02},
        {"alpha_interp": 0.75, "bbmd_distance_mean": 0.80, "amp_rel_err_mean": 0.10, "vamp_rel_err_mean": 0.03},
        {"alpha_interp": 1.0, "bbmd_distance_mean": 1.20, "amp_rel_err_mean": 0.08, "vamp_rel_err_mean": 0.04},
    ]
    v, _ = compute_verdict({"cells": cells_killed_rho})
    assert v == "BBMD_VAMP_CORRESPONDENCE_KILLED", f"expected KILLED via low rho got {v}"

    # Test 5: verdict KILLED via vamp blowup
    cells_killed_vamp = [
        {"alpha_interp": 0.0, "bbmd_distance_mean": 0.01, "amp_rel_err_mean": 0.02, "vamp_rel_err_mean": 0.01},
        {"alpha_interp": 0.5, "bbmd_distance_mean": 0.50, "amp_rel_err_mean": 0.15, "vamp_rel_err_mean": 0.02},
        {"alpha_interp": 1.0, "bbmd_distance_mean": 1.20, "amp_rel_err_mean": 0.30, "vamp_rel_err_mean": 0.30},
    ]
    v, _ = compute_verdict({"cells": cells_killed_vamp})
    assert v == "BBMD_VAMP_CORRESPONDENCE_KILLED", f"expected KILLED via vamp got {v}"

    # Test 6: INCONCLUSIVE
    cells_inc = [
        {"alpha_interp": 0.0, "bbmd_distance_mean": 0.01, "amp_rel_err_mean": 0.02, "vamp_rel_err_mean": 0.02},
        {"alpha_interp": 0.5, "bbmd_distance_mean": 0.50, "amp_rel_err_mean": 0.10, "vamp_rel_err_mean": 0.04},
        {"alpha_interp": 1.0, "bbmd_distance_mean": 1.20, "amp_rel_err_mean": 0.20, "vamp_rel_err_mean": 0.07},
    ]
    # rho=1.0 (monotone) but vamp=0.07 in (0.05, 0.10) -> INCONCLUSIVE
    v, _ = compute_verdict({"cells": cells_inc})
    assert v == "BBMD_VAMP_CORRESPONDENCE_INCONCLUSIVE", f"expected INCONCLUSIVE got {v}"

    # Test 7: too few cells
    v, _ = compute_verdict({"cells": cells_inc[:1]})
    assert v == "BBMD_VAMP_CORRESPONDENCE_INCONCLUSIVE", f"expected INCONCLUSIVE on 1 cell, got {v}"

    print("BBMD-VAMP correspondence self-test passed (7/7 cases)", flush=True)


# ---------------------------------------------------------------------------
# Main experiment
# ---------------------------------------------------------------------------

def run_experiment(smoke: bool) -> tuple[dict, str, str, float, dict]:
    t0 = time.monotonic()

    if smoke:
        config = {
            "mode": "smoke",
            "N": 64,
            "M_over_N": 1.0,
            "alpha_interp_list": [0.0, 0.5, 1.0],
            "sigma_noise": 0.1,
            "signal_var": 1.0,
            "n_seeds": 1,
            "n_iter": 100,
            "n_max_moment": 6,
        }
    else:
        config = {
            "mode": "full",
            "N": 4096,
            "M_over_N": 1.0,
            "alpha_interp_list": [0.0, 0.25, 0.5, 0.75, 1.0],
            "sigma_noise": 0.1,
            "signal_var": 1.0,
            "n_seeds": 10,
            "n_iter": 300,
            "n_max_moment": 6,
        }

    # Kerdock builder constraint: N must be 2^k with even k. N=64 -> k=6 -> t=3.
    # But PRIMITIVE_POLY supports only t in {5, 6, 7}. Smoke at N=64 fails.
    # For smoke, force N=1024 (t=5, smallest supported) and small M; smoke at
    # 1024 still <60s wallclock.
    if smoke:
        config["N"] = 1024  # forced; Kerdock builder constraint
        config["M_over_N"] = 0.5  # smaller smoke M
        # keep alpha_interp_list 3 points + 1 seed

    N = config["N"]
    M = max(1, int(config["M_over_N"] * N))
    sigma = config["sigma_noise"]
    sigma_sq = sigma ** 2
    signal_var = config["signal_var"]
    alpha_ratio = M / N
    n_max = config["n_max_moment"]

    print(f"[setup] N={N} M={M} M/N={alpha_ratio:.3f} sigma={sigma} signal_var={signal_var} "
          f"alpha_interp={config['alpha_interp_list']} seeds={config['n_seeds']}", flush=True)

    # Scalar AMP-SE depends only on alpha_ratio + sigma_sq + signal_var; compute once
    amp_se_pred = amp_se_scalar(alpha_ratio, sigma_sq, signal_var)

    kerdock_cache: dict = {}

    cells = []
    for alpha_int in config["alpha_interp_list"]:
        seed_records = []
        for seed in range(config["n_seeds"]):
            seed_val = seed * 1000 + 7

            W = build_W_alpha(alpha_int, N, M, seed_val, kerdock_cache)

            # SVD once; reuse for kappa profile + VAMP
            U, s, Vt = np.linalg.svd(W, full_matrices=False)
            eig = (s ** 2).astype(np.float64)
            # Spectral moments on (1/M) sum_i lambda_i^n (since SVD returns K=min(M,N) modes)
            moms = [float(np.mean(eig ** n)) for n in range(1, n_max + 1)]
            kappas = moments_to_free_cumulants_general(moms)
            d_bbmd = bbmd_distance(kappas, alpha_ratio, n_min=2, n_max=n_max)

            # VAMP-SE closed-form
            vamp_se_pred = vamp_se_closed(s, N, M, sigma_sq, signal_var)

            # Generate signal + noise
            rng_sig = np.random.default_rng(seed_val + 77)
            x_true = rng_sig.standard_normal(N).astype(np.float64) * math.sqrt(signal_var)
            noise = rng_sig.standard_normal(M).astype(np.float64) * sigma
            y = (W.astype(np.float64) @ x_true) + noise

            # Empirical AMP + VAMP
            amp_emp = run_amp(W, y, x_true, signal_var, sigma_sq, config["n_iter"])
            vamp_emp = run_vamp(U, s, Vt, y, x_true, signal_var, sigma_sq, config["n_iter"])

            amp_rel = abs(amp_emp - amp_se_pred) / max(amp_emp, amp_se_pred, 1e-12)
            vamp_rel = abs(vamp_emp - vamp_se_pred) / max(vamp_emp, vamp_se_pred, 1e-12)

            seed_records.append({
                "seed": seed_val,
                "kappas": kappas,
                "bbmd_distance": d_bbmd,
                "amp_se_pred": amp_se_pred,
                "amp_emp": amp_emp,
                "amp_rel_err": amp_rel,
                "vamp_se_pred": vamp_se_pred,
                "vamp_emp": vamp_emp,
                "vamp_rel_err": vamp_rel,
            })
            print(f"  alpha_int={alpha_int:.2f} seed={seed} bbmd={d_bbmd:.4f} "
                  f"AMP_SE={amp_se_pred:.5f} AMP_emp={amp_emp:.5f} (rel={amp_rel:.3f}) "
                  f"VAMP_SE={vamp_se_pred:.5f} VAMP_emp={vamp_emp:.5f} (rel={vamp_rel:.3f})",
                  flush=True)

        # Aggregate across seeds for this alpha
        d_mean = float(np.mean([r["bbmd_distance"] for r in seed_records]))
        amp_rel_mean = float(np.mean([r["amp_rel_err"] for r in seed_records]))
        vamp_rel_mean = float(np.mean([r["vamp_rel_err"] for r in seed_records]))
        kappa_mean = np.mean([r["kappas"] for r in seed_records], axis=0).tolist()

        cells.append({
            "alpha_interp": float(alpha_int),
            "bbmd_distance_mean": d_mean,
            "amp_rel_err_mean": amp_rel_mean,
            "vamp_rel_err_mean": vamp_rel_mean,
            "kappa_mean": kappa_mean,
            "per_seed": seed_records,
        })
        print(f"  AGG alpha_int={alpha_int:.2f}: bbmd_mean={d_mean:.4f} "
              f"amp_rel_mean={amp_rel_mean:.4f} vamp_rel_mean={vamp_rel_mean:.4f}",
              flush=True)

    summary = {"cells": cells, "config": config}
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic() - t0
    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)
    return summary, verdict, msg, elapsed, config


def get_output_dir(name: str) -> Path:
    env_name = os.environ.get("HDLAB_EXP_NAME", name)
    out = REPO / "data" / f"exp_{env_name}"
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
    out_dir = get_output_dir("wave14_bbmd_vamp_correspondence_sweep_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    assert len(summary["cells"]) >= 1, "smoke FAIL: no cells produced"
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main() -> None:
    self_test()
    out_dir = get_output_dir("wave14_bbmd_vamp_correspondence_sweep_v1")
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
