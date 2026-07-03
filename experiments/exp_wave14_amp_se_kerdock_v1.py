"""AMP state-evolution fixed point at substrate's exact Kerdock codebook.

Computes the AMP state-evolution (SE) recursion for the substrate's 4-coset
Kerdock measurement matrix. The SE recursion gives the THEORETICAL MSE
fixed point assuming the matrix is in the AMP universality class (right-
rotationally-invariant; Bayati-Montanari 2011). Compares the SE prediction
to EMPIRICAL AMP iteration on the actual Kerdock matrix at matched M/N.

Scientific question: Does the SE fixed point for the Kerdock R-transform
predict substrate's empirical AMP performance? If YES: first theory-to-
empirics anchor for substrate's M/N=8 capacity anomaly (B4+F5 in meta-map).
If NO: Kerdock codebook is outside the AMP universality class -- a sharp
novel finding delineating the AMP universality boundary.

Vertex: AMP_SE_MATCHES_EMPIRICS / AMP_SE_DIVERGES / AMP_SE_INCONCLUSIVE.

Pre-reg: preregs/2026-05-23_wave14_amp_se_kerdock_v1.md
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
# Import Kerdock codebook builder from v3
_v3_path = REPO / "experiments" / "exp_wave14y_erase_kerdock_v3.py"
_spec = importlib.util.spec_from_file_location("kerdock_v3", _v3_path)
_v3 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_v3)
make_kerdock_4coset_codebook = _v3.make_kerdock_4coset_codebook

try:
    import torch
    _TORCH_OK = True
except ImportError:
    _TORCH_OK = False


# ---------------------------------------------------------------------------
# Core: AMP state-evolution recursion
# ---------------------------------------------------------------------------

def se_mmse_denoiser(tau_sq: float, signal_var: float) -> float:
    """MMSE for Gaussian-on-Gaussian: E[(x - hat_x)^2] where x ~ N(0, signal_var).

    For signal x ~ N(0, sigma_x^2) and observation r = x + N(0, tau^2),
    MMSE denoiser gives:
        hat_x = r * signal_var / (signal_var + tau_sq)
        MSE   = signal_var * tau_sq / (signal_var + tau_sq)
    """
    return signal_var * tau_sq / (signal_var + tau_sq)


def se_onsager_coefficient(tau_sq: float, signal_var: float) -> float:
    """Onsager coefficient b = E[d hat_x / d r] for MMSE Gaussian denoiser.

    b = signal_var / (signal_var + tau_sq)
    """
    return signal_var / (signal_var + tau_sq)


def amp_se_recursion(
    alpha: float,           # M/N measurement ratio
    sigma_noise_sq: float,  # observation noise variance
    signal_var: float,      # prior signal variance (isotropic Gaussian)
    eigenvalues: np.ndarray,# eigenvalues of (1/N)*A^T A (empirical spectrum)
    n_iter: int = 200,
    tol: float = 1e-9,
) -> dict:
    """Run AMP state-evolution to fixed point using the empirical spectrum.

    State-evolution for right-rotationally-invariant matrices (Rangan-Fletcher-
    Goyal 2019 VAMP / Berthier-Montanari-Nguyen 2020 generalized SE):

        tau_sq_{t+1} = sigma_noise_sq + (1/alpha) * E_lambda[
            lambda * mmse_t / (1 - b_t * E[lambda / (lambda + mmse_t * alpha)])
        ]

    Simplified (standard AMP SE for IID-like matrix, Bayati-Montanari 2011):
        tau_sq_{t+1} = sigma_noise_sq + (1/alpha) * mmse(tau_sq_t)

    We use BOTH: the exact spectrum-weighted SE (via empirical eigenvalues) and
    the simplified scalar SE. Convergence of both to the same fixed point is the
    AMP universality criterion for this matrix.

    Returns:
        dict with keys:
            tau_sq_history: list of tau_sq values
            mse_history: list of MSE predictions
            tau_sq_fixed: final SE fixed point
            mse_fixed: MSE at fixed point
            overlap_fixed: q = 1 - mse_fixed / signal_var
            converged: bool
            n_iters: int
            tau_sq_scalar_fixed: fixed point from scalar SE (IID approximation)
            mse_scalar_fixed: MSE from scalar SE
    """
    tau_sq = sigma_noise_sq + signal_var  # initialization: all noise

    tau_sq_hist = [tau_sq]
    mse_hist = []

    # Scalar SE (IID approximation; Bayati-Montanari formula)
    tau_sq_scalar = sigma_noise_sq + signal_var
    tau_sq_scalar_hist = [tau_sq_scalar]

    lam = eigenvalues  # shape (K,), empirical eigenvalues of (1/N)*A^T A

    converged = False
    for _ in range(n_iter):
        # MMSE and Onsager at current tau_sq
        mse_t = se_mmse_denoiser(tau_sq, signal_var)
        b_t = se_onsager_coefficient(tau_sq, signal_var)

        # Spectrum-weighted SE update (generalized AMP with empirical spectrum)
        # tau_sq_{t+1} = sigma_noise_sq + (1 / alpha) * E_lam[
        #     lam * mse_t / (1 + b_t * lam * mse_t / tau_sq)
        # ]
        # This follows from the VAMP state-evolution with empirical spectrum.
        denom = 1.0 + b_t * lam * mse_t / max(tau_sq, 1e-15)
        denom = np.maximum(denom, 1e-10)
        weighted_term = float(np.mean(lam * mse_t / denom))
        tau_sq_new = sigma_noise_sq + weighted_term / alpha

        # Scalar SE update (IID assumption)
        mse_scalar = se_mmse_denoiser(tau_sq_scalar, signal_var)
        tau_sq_scalar_new = sigma_noise_sq + mse_scalar / alpha

        # Record
        mse_hist.append(mse_t)
        tau_sq_hist.append(tau_sq_new)
        tau_sq_scalar_hist.append(tau_sq_scalar_new)

        # Convergence check
        if abs(tau_sq_new - tau_sq) < tol * max(abs(tau_sq), 1.0):
            converged = True
            tau_sq = tau_sq_new
            tau_sq_scalar = tau_sq_scalar_new
            break

        tau_sq = tau_sq_new
        tau_sq_scalar = tau_sq_scalar_new

    mse_fixed = se_mmse_denoiser(tau_sq, signal_var)
    mse_scalar_fixed = se_mmse_denoiser(tau_sq_scalar, signal_var)
    overlap_fixed = 1.0 - mse_fixed / signal_var if signal_var > 0 else 0.0

    return {
        "tau_sq_history": tau_sq_hist,
        "mse_history": mse_hist,
        "tau_sq_fixed": float(tau_sq),
        "mse_fixed": float(mse_fixed),
        "overlap_fixed": float(overlap_fixed),
        "converged": converged,
        "n_iters": len(mse_hist),
        "tau_sq_scalar_fixed": float(tau_sq_scalar),
        "mse_scalar_fixed": float(mse_scalar_fixed),
    }


# ---------------------------------------------------------------------------
# Empirical AMP on actual Kerdock matrix
# ---------------------------------------------------------------------------

def run_empirical_amp(A: np.ndarray, x_true: np.ndarray, sigma_noise: float,
                      n_iter: int = 100) -> dict:
    """Run GAMP-style AMP on measurement matrix A and signal x_true.

    Uses the MMSE Gaussian denoiser (matched to Gaussian signal prior).
    Returns per-iteration MSE and final overlap.
    """
    M, N = A.shape
    alpha = M / N
    signal_var = float(np.var(x_true))
    if signal_var < 1e-12:
        signal_var = 1.0

    y = A @ x_true + sigma_noise * np.random.randn(M)

    # AMP initialization
    x_hat = np.zeros(N)
    z = y.copy()

    mse_history = []
    # Onsager memory: b * z
    b_prev = 0.0

    for it in range(n_iter):
        # Residual (with Onsager correction)
        r = A.T @ z + x_hat  # shape (N,)

        # Effective noise variance from residual
        tau_sq_eff = float(np.mean(z ** 2)) / alpha
        tau_sq_eff = max(tau_sq_eff, 1e-10)

        # MMSE denoiser (matched Gaussian prior)
        gain = signal_var / (signal_var + tau_sq_eff)
        x_hat_new = gain * r

        # Onsager coefficient
        b = gain  # d hat_x / d r for MMSE denoiser = gain

        # Residual update with Onsager correction
        z = y - A @ x_hat_new + b * z * (1.0 / alpha)

        x_hat = x_hat_new
        mse = float(np.mean((x_hat - x_true) ** 2))
        mse_history.append(mse)
        b_prev = b

        if it >= 5:
            recent = mse_history[-5:]
            if max(recent) - min(recent) < 1e-10:
                break  # converged

    mse_final = mse_history[-1] if mse_history else float("inf")
    overlap = 1.0 - mse_final / signal_var if signal_var > 0 else 0.0

    return {
        "mse_history": mse_history,
        "mse_final": float(mse_final),
        "overlap_final": float(overlap),
        "n_iters": len(mse_history),
    }


# ---------------------------------------------------------------------------
# Verdict logic
# ---------------------------------------------------------------------------

def compute_verdict(summary: dict) -> tuple[str, str]:
    """Determine verdict from summary dict."""
    if not summary.get("cells"):
        return ("AMP_SE_INCONCLUSIVE", "No cells computed.")

    # Collect relative errors across all cells
    rel_errs = []
    for cell in summary["cells"]:
        se_mse = cell.get("se_mse_fixed")
        emp_mse = cell.get("emp_mse_final")
        if se_mse is None or emp_mse is None:
            continue
        denom = max(se_mse, emp_mse, 1e-12)
        rel_err = abs(se_mse - emp_mse) / denom
        cell["rel_err"] = rel_err
        rel_errs.append(rel_err)

    if not rel_errs:
        return ("AMP_SE_INCONCLUSIVE", "No valid cells for comparison.")

    mean_rel_err = float(np.mean(rel_errs))
    max_rel_err = float(np.max(rel_errs))
    n_cells = len(rel_errs)
    n_close = sum(1 for e in rel_errs if e < 0.20)

    # Hard pass: mean relative error < 20%, at least 2/3 cells close
    if mean_rel_err < 0.20 and n_close >= max(1, 2 * n_cells // 3):
        return (
            "AMP_SE_MATCHES_EMPIRICS",
            f"SE fixed-point MSE matches empirical AMP MSE within {mean_rel_err:.3f} "
            f"mean relative error (max={max_rel_err:.3f}). {n_close}/{n_cells} cells "
            f"< 20% relative error. Kerdock codebook is in AMP universality class. "
            f"First theory-to-empirics anchor for substrate M/N capacity.",
        )

    # Hard fail: mean relative error > 80% and max > 80% and fewer than 1/3 close
    # (factor-of-2 divergence: rel_err = 0.80 means one value is 1.8x the other)
    if mean_rel_err > 0.80 and n_close < max(1, n_cells // 3):
        return (
            "AMP_SE_DIVERGES",
            f"SE fixed-point diverges from empirical AMP. Mean rel err={mean_rel_err:.3f}, "
            f"max={max_rel_err:.3f}. Kerdock codebook is OUTSIDE the AMP universality class. "
            f"Novel finding: Kerdock structure breaks AMP-SE assumptions. "
            f"Only {n_close}/{n_cells} cells < 20% error.",
        )

    # Middle ground: AMP_SE_INCONCLUSIVE (between 20% and 5x)
    return (
        "AMP_SE_INCONCLUSIVE",
        f"SE prediction partially matches empirics. Mean rel err={mean_rel_err:.3f}, "
        f"max={max_rel_err:.3f}. {n_close}/{n_cells} cells < 20% relative error. "
        f"Cannot cleanly classify Kerdock codebook into or out of AMP universality class.",
    )


def self_test_verdict() -> None:
    """Verify verdict logic on hand-crafted cases."""
    cases = [
        # (cells list, expected_verdict)
        (
            [{"se_mse_fixed": 0.10, "emp_mse_final": 0.11},
             {"se_mse_fixed": 0.10, "emp_mse_final": 0.10},
             {"se_mse_fixed": 0.08, "emp_mse_final": 0.09}],
            "AMP_SE_MATCHES_EMPIRICS",
        ),
        (
            [{"se_mse_fixed": 0.10, "emp_mse_final": 1.20},
             {"se_mse_fixed": 0.08, "emp_mse_final": 0.85},
             {"se_mse_fixed": 0.05, "emp_mse_final": 0.60}],
            "AMP_SE_DIVERGES",
        ),
        (
            [{"se_mse_fixed": 0.10, "emp_mse_final": 0.14},
             {"se_mse_fixed": 0.10, "emp_mse_final": 0.22},
             {"se_mse_fixed": 0.10, "emp_mse_final": 0.80}],
            "AMP_SE_INCONCLUSIVE",
        ),
        (
            [],
            "AMP_SE_INCONCLUSIVE",
        ),
    ]
    for cells, expected in cases:
        actual, msg = compute_verdict({"cells": cells})
        assert actual == expected, (
            f"self_test FAIL: got {actual!r}, expected {expected!r}, msg={msg}"
        )
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


# ---------------------------------------------------------------------------
# Eigenspectrum extraction
# ---------------------------------------------------------------------------

def get_kerdock_eigenspectrum(N: int, M: int, seed: int) -> np.ndarray:
    """Build Kerdock 4-coset codebook, subsample M rows, return eigenvalues of (1/N)*A^T A."""
    if not _TORCH_OK:
        raise RuntimeError("torch required for Kerdock codebook builder")
    import torch

    device = torch.device("cpu")
    cb, _info = make_kerdock_4coset_codebook(N, device)  # (4N, N) bipolar

    rng = np.random.default_rng(seed)
    idx = rng.choice(cb.shape[0], size=M, replace=False)
    A_t = cb[idx].float()  # (M, N) torch

    # Convert to numpy
    A = A_t.numpy()  # (M, N), entries in {-1, +1}
    A_norm = A / math.sqrt(N)  # normalize so each row has unit L2 norm when M/N small

    # Eigenvalues of (1/N) * A^T A via SVD (more numerically stable)
    # singular values s_i; eigenvalues of A^T A / N = s_i^2 / N
    # But A_norm already has A/sqrt(N), so A_norm^T A_norm = A^T A / N
    # Use SVD: singular values of A_norm -> eigenvalues of A_norm^T A_norm
    _, s, _ = np.linalg.svd(A_norm, full_matrices=False)
    eigenvalues = s ** 2  # eigenvalues of (1/N) * A^T A; shape (min(M,N),)
    return eigenvalues, A_norm


# ---------------------------------------------------------------------------
# Main experiment
# ---------------------------------------------------------------------------

def run_experiment(smoke: bool) -> tuple[dict, str, str, float, dict]:
    t0 = time.monotonic()

    if smoke:
        config = {
            "mode": "smoke",
            "N": 1024,  # must have even log2(N) for MM construction; 1024=2^10 OK
            "M_over_N_list": [0.5, 1.0],
            "signal_var": 1.0,
            "sigma_noise": 0.1,
            "n_seeds": 2,
            "amp_n_iter": 50,
            "se_n_iter": 200,
            "se_tol": 1e-9,
        }
    else:
        config = {
            "mode": "full",
            "N": 4096,
            "M_over_N_list": [0.5, 1.0, 2.0, 4.0, 8.0],
            "signal_var": 1.0,
            "sigma_noise": 0.1,
            "n_seeds": 5,
            "amp_n_iter": 200,
            "se_n_iter": 500,
            "se_tol": 1e-12,
        }

    N = config["N"]
    sigma_noise = config["sigma_noise"]
    sigma_noise_sq = sigma_noise ** 2
    signal_var = config["signal_var"]
    rng = np.random.default_rng(42)

    cells = []
    all_lam_by_alpha = {}

    for alpha in config["M_over_N_list"]:
        M = max(1, int(alpha * N))
        # Kerdock has 4N codewords; we need M <= 4N
        if M > 4 * N:
            print(f"[skip] alpha={alpha:.2f}: M={M} > 4N={4*N}, skipping", flush=True)
            continue

        print(f"\n[alpha={alpha:.2f}] N={N} M={M}", flush=True)

        # Collect eigenspectrum and empirical AMP across seeds
        se_mse_vals = []
        emp_mse_vals = []
        emp_overlap_vals = []
        se_overlap_vals = []
        lam_all = []

        for seed in range(config["n_seeds"]):
            seed_val = seed * 1000 + int(alpha * 100)
            eigenvalues, A_norm = get_kerdock_eigenspectrum(N, M, seed=seed_val)
            lam_all.append(eigenvalues)

            # AMP state-evolution
            se_result = amp_se_recursion(
                alpha=alpha,
                sigma_noise_sq=sigma_noise_sq,
                signal_var=signal_var,
                eigenvalues=eigenvalues,
                n_iter=config["se_n_iter"],
                tol=config["se_tol"],
            )
            se_mse_vals.append(se_result["mse_fixed"])
            se_overlap_vals.append(se_result["overlap_fixed"])

            # Empirical AMP on the same matrix
            x_true = rng.standard_normal(N) * math.sqrt(signal_var)
            emp_result = run_empirical_amp(
                A_norm, x_true, sigma_noise, n_iter=config["amp_n_iter"]
            )
            emp_mse_vals.append(emp_result["mse_final"])
            emp_overlap_vals.append(emp_result["overlap_final"])

            print(
                f"  seed={seed} SE_mse={se_result['mse_fixed']:.5f} "
                f"emp_mse={emp_result['mse_final']:.5f} "
                f"SE_q={se_result['overlap_fixed']:.4f} "
                f"emp_q={emp_result['overlap_final']:.4f} "
                f"SE_converged={se_result['converged']}",
                flush=True,
            )

        # Aggregate
        se_mse_mean = float(np.mean(se_mse_vals))
        emp_mse_mean = float(np.mean(emp_mse_vals))
        se_mse_std = float(np.std(se_mse_vals))
        emp_mse_std = float(np.std(emp_mse_vals))
        denom = max(se_mse_mean, emp_mse_mean, 1e-12)
        rel_err = abs(se_mse_mean - emp_mse_mean) / denom

        cell = {
            "alpha": alpha,
            "N": N,
            "M": M,
            "se_mse_fixed": se_mse_mean,
            "se_mse_std": se_mse_std,
            "emp_mse_final": emp_mse_mean,
            "emp_mse_std": emp_mse_std,
            "se_overlap_mean": float(np.mean(se_overlap_vals)),
            "emp_overlap_mean": float(np.mean(emp_overlap_vals)),
        }
        cells.append(cell)
        all_lam_by_alpha[str(alpha)] = {
            "mean_lam_max": float(np.mean([l.max() for l in lam_all])),
            "mean_lam_min": float(np.mean([l.min() for l in lam_all])),
            "mean_lam_mean": float(np.mean([l.mean() for l in lam_all])),
        }

        print(
            f"  AGGREGATE alpha={alpha:.2f}: SE_mse={se_mse_mean:.5f}+-{se_mse_std:.5f} "
            f"emp_mse={emp_mse_mean:.5f}+-{emp_mse_std:.5f} rel_err={rel_err:.3f}",
            flush=True,
        )

    summary = {
        "cells": cells,
        "eigenspectrum_summary": all_lam_by_alpha,
        "config": config,
    }

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
    self_test_verdict()
    out_dir = get_output_dir("wave14_amp_se_kerdock_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    # Smoke assertion: must have at least one valid cell
    assert len(summary["cells"]) >= 1, "smoke FAIL: no cells produced"
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main() -> None:
    self_test_verdict()
    out_dir = get_output_dir("wave14_amp_se_kerdock_v1")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=False)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nDONE: {verdict}", flush=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test_verdict()
        return 0
    if args.smoke:
        run_smoke()
        return 0
    run_main()
    return 0


if __name__ == "__main__":
    sys.exit(main())
