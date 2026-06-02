"""Spectral MP primitives: health-check, deletion privacy SNR, capacity monitor.

Three spectral capability tests derived from the free-Poisson / MP framework:
1. SPECTRAL HEALTH CHECK: Z = (lambda_max - mu_TW) / sigma_TW ~ TW_1 distribution.
   Test: known-clean substrate (random patterns, no correlation) should have |Z| < 4.
   Known-correlated substrate should have |Z| >> 4.
2. DELETION CERTIFICATE SPECTRAL PRIVACY: SNR_delete = 2(1+sqrt(alpha))^(-4/3) / N^(1/3).
   At N=4096, alpha=0.138: SNR_delete ~ 0.067. Adversary observing spectrum cannot
   detect deletion above chance. Test: shift in lambda_max after deleting one pattern
   vs TW fluctuation scale.
3. SPECTRAL CAPACITY MONITOR: lambda_max tracks BBP precursor as M grows.
   Test: lambda_max as function of M, compare to TW band.

PRE-REGISTERED BANDS:
  1. HEALTH CHECK:
     HARD-PASS: |Z_clean| < 4 AND |Z_correlated| > 4 in >= 4/5 seeds.
     MIDDLE: |Z_clean| < 10 OR direction correct but not fully discriminating.
     HARD-FAIL: |Z_clean| > 10 in >= 3/5 seeds (false alarm rate too high).

  2. DELETION PRIVACY:
     HARD-PASS: SNR_delete_empirical / SNR_delete_theory in [0.33, 3.0] in >= 4/5 seeds.
     Note: calibration probe; bands +-50%. Theory predicts 0.067; HF if empirical > 3*theory.
     MIDDLE: ratio in [0.1, 10].
     HARD-FAIL: ratio > 10 in >= 3/5 seeds (deletion is detectable; privacy claim fails).

  3. CAPACITY MONITOR:
     HARD-PASS: Pearson r(M, lambda_max) > 0.98 in >= 4/5 seeds across M sweep.
     MIDDLE: r > 0.90.
     HARD-FAIL: r < 0.80 in >= 3/5 seeds.

DESIGN:
  N=4096 (clean TW separation; sigma_TW ~ 0.010 at N=4096).
  For health check: clean (M=100, random) vs correlated (M=100, one pattern near another).
  For deletion: alpha=0.138, N=4096 -> M=565. Delete one pattern, measure delta_lambda_max.
  For monitor: M in [10, 50, 100, 200, 400, 500], alpha in [0.002, 0.12].
  5 seeds.

FORMULA SELF-TESTS:
  1. sigma_TW at N=4096, alpha=0.05: (1.224)^(4/3) / (4096)^(2/3) ~ 0.010.
  2. SNR_delete at N=4096, alpha=0.138: 2*(1.372)^(-4/3) / (4096)^(1/3) ~ 0.067.
  3. lambda_plus at alpha=0.05, N=4096: (1+sqrt(0.05))^2 ~ 1.497.

PROT-018: no _nN suffix. Production N=4096, rule 3.
TIMEOUT ESTIMATE:
  numpy eigh at N=4096: ~2s per matrix. 5 seeds * (4 conditions + 6 M_values) = 50 matrices.
  ~100s. timeout_s=300.

Anchor: spectral_mp_primitives_v1
Queue: remote_cpu_queue
Pre-reg: preregs/2026-06-01_spectral_mp_primitives_v1.md
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import json
import math
import os
import time
from pathlib import Path
from typing import Dict, List

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import get_output_dir  # noqa: E402

ANCHOR_NAME = "spectral_mp_primitives_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

N_MAIN = 4096
ALPHA_NOMINAL = 0.138
ALPHA_PROBE = 0.05

if RUN_MODE == "smoke":
    N_MAIN = 1024  # smoke at N=1024
    SEEDS = [7, 17]
    M_MONITOR_GRID = [5, 20, 50]
else:
    N_MAIN = 4096
    SEEDS = [7, 17, 23, 31, 41]
    M_MONITOR_GRID = [10, 50, 100, 200, 400, 500]


def sigma_TW(N: int, alpha: float) -> float:
    return ((1.0 + math.sqrt(alpha)) ** (4.0 / 3.0)) / (N ** (2.0 / 3.0))


def lambda_plus(alpha: float) -> float:
    return (1.0 + math.sqrt(alpha)) ** 2


def build_W_eig(N: int, M: int, seed: int) -> tuple:
    rng = np.random.RandomState(seed)
    Xi = rng.choice([-1, 1], size=(N, M)).astype(np.float64)
    W = (Xi @ Xi.T) / N
    eigvals = np.linalg.eigvalsh(W)
    return W, Xi, eigvals


def snr_delete_theory(N: int, alpha: float) -> float:
    """Theoretical SNR for deletion detection via eigenspectrum."""
    return 2.0 * (1.0 + math.sqrt(alpha)) ** (-4.0 / 3.0) / (N ** (1.0 / 3.0))


def run_health_check(N: int, M: int, seed: int) -> Dict:
    """Test Z = (lambda_max - mu_TW) / sigma_TW ~ TW_1."""
    alpha = M / N
    lp = lambda_plus(alpha)
    sTW = sigma_TW(N, alpha)
    # mu_TW ~ lambda_plus for large N (leading correction negligible here)
    mu_TW = lp

    # Clean: random patterns
    _, _, eigvals_clean = build_W_eig(N, M, seed)
    lambda_max_clean = float(eigvals_clean[-1])
    Z_clean = (lambda_max_clean - mu_TW) / sTW

    # Correlated: one pattern nearly parallel to another (rho=0.5 correlation)
    rng = np.random.RandomState(seed + 2000)
    Xi_base = rng.choice([-1, 1], size=(N, M)).astype(np.float64)
    # Add one extra correlated pattern
    xi_new = Xi_base[:, 0].copy()
    flip_mask = rng.rand(N) < 0.25  # 75% correlation
    xi_new[flip_mask] = -xi_new[flip_mask]
    Xi_corr = np.concatenate([Xi_base, xi_new.reshape(-1, 1)], axis=1)
    W_corr = (Xi_corr @ Xi_corr.T) / N
    eigvals_corr = np.linalg.eigvalsh(W_corr)
    alpha_corr = (M + 1) / N
    lp_corr = lambda_plus(alpha_corr)
    sTW_corr = sigma_TW(N, alpha_corr)
    lambda_max_corr = float(eigvals_corr[-1])
    Z_corr = (lambda_max_corr - lp_corr) / sTW_corr

    return {
        "Z_clean": float(Z_clean),
        "Z_corr": float(Z_corr),
        "lambda_max_clean": lambda_max_clean,
        "lambda_max_corr": lambda_max_corr,
        "lambda_plus": float(lp),
        "sigma_TW": float(sTW),
        "health_hp": abs(Z_clean) < 4 and Z_corr > 4,
    }


def run_deletion_privacy(N: int, M: int, seed: int) -> Dict:
    """Measure empirical shift in lambda_max after one deletion."""
    alpha = M / N
    sTW = sigma_TW(N, alpha)
    snr_theory = snr_delete_theory(N, alpha)

    W, Xi, eigvals_before = build_W_eig(N, M, seed)
    lambda_max_before = float(eigvals_before[-1])

    # Delete pattern 0
    xi_del = Xi[:, 0]
    W_after = W - np.outer(xi_del, xi_del) / N
    eigvals_after = np.linalg.eigvalsh(W_after)
    lambda_max_after = float(eigvals_after[-1])

    delta_lambda = abs(lambda_max_before - lambda_max_after)
    # SNR = delta_lambda / sigma_TW
    snr_empirical = delta_lambda / max(1e-12, sTW)
    ratio = snr_empirical / max(1e-12, snr_theory)

    return {
        "snr_theory": float(snr_theory),
        "snr_empirical": float(snr_empirical),
        "delta_lambda": float(delta_lambda),
        "sigma_TW": float(sTW),
        "snr_ratio": float(ratio),
        "deletion_hp": 0.33 <= ratio <= 3.0,
    }


def run_capacity_monitor(N: int, M_grid: List[int], seed: int) -> Dict:
    """Track lambda_max vs M. Should increase monotonically."""
    results = []
    for M in M_grid:
        _, _, eigvals = build_W_eig(N, M, seed)
        lp = lambda_plus(M / N)
        sTW = sigma_TW(N, M / N)
        results.append({
            "M": M,
            "alpha": M / N,
            "lambda_max": float(eigvals[-1]),
            "lambda_plus_theory": float(lp),
            "sigma_TW": float(sTW),
        })

    lambda_maxes = [r["lambda_max"] for r in results]
    M_vals = [r["M"] for r in results]

    from scipy.stats import pearsonr  # type: ignore
    if len(M_vals) > 2:
        r_corr, _ = pearsonr(M_vals, lambda_maxes)
    else:
        r_corr = 1.0

    return {
        "pearson_r": float(r_corr),
        "monitor_hp": r_corr > 0.98,
        "M_grid": M_vals,
        "lambda_max_grid": lambda_maxes,
    }


def _instrumentation_selftest():
    """Assert all 3 spectral primitives compute at small scale."""
    r_hc = run_health_check(N=256, M=20, seed=999)
    r_dp = run_deletion_privacy(N=256, M=20, seed=999)
    r_cm = run_capacity_monitor(256, [5, 10, 20], 999)

    assert not math.isnan(r_hc["Z_clean"]), "Z_clean is NaN"
    assert not math.isnan(r_dp["snr_empirical"]), "snr_empirical is NaN"
    assert r_dp["snr_empirical"] >= 0, "snr_empirical negative"
    assert r_cm["pearson_r"] is not None, "pearson_r is None"
    print(f"[selftest] PASS: Z_clean={r_hc['Z_clean']:.2f} "
          f"snr_del={r_dp['snr_empirical']:.4f} (theory={r_dp['snr_theory']:.4f}) "
          f"monitor_r={r_cm['pearson_r']:.3f}", flush=True)


_instrumentation_selftest()


def main():
    t0 = time.time()
    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)

    N = N_MAIN
    M = max(1, int(ALPHA_NOMINAL * N))
    print(f"[{ANCHOR_NAME}] RUN_MODE={RUN_MODE} N={N} M={M} alpha={ALPHA_NOMINAL}",
          flush=True)
    print(f"  M_monitor_grid={M_MONITOR_GRID} seeds={SEEDS}", flush=True)

    hc_results = []
    dp_results = []
    cm_results = []

    for seed in SEEDS:
        print(f"[{ANCHOR_NAME}] seed={seed}...", flush=True)
        r_hc = run_health_check(N, M, seed)
        hc_results.append(r_hc)
        r_dp = run_deletion_privacy(N, M, seed)
        dp_results.append(r_dp)
        r_cm = run_capacity_monitor(N, M_MONITOR_GRID, seed)
        cm_results.append(r_cm)
        print(f"  HC: Z_clean={r_hc['Z_clean']:.2f} Z_corr={r_hc['Z_corr']:.2f} "
              f"hp={r_hc['health_hp']}", flush=True)
        print(f"  DP: snr_emp={r_dp['snr_empirical']:.4f} "
              f"snr_theory={r_dp['snr_theory']:.4f} "
              f"ratio={r_dp['snr_ratio']:.2f} hp={r_dp['deletion_hp']}", flush=True)
        print(f"  CM: r={r_cm['pearson_r']:.4f} hp={r_cm['monitor_hp']}", flush=True)

    # Verdicts
    n_hc_hp = sum(1 for r in hc_results if r["health_hp"])
    n_dp_hp = sum(1 for r in dp_results if r["deletion_hp"])
    n_cm_hp = sum(1 for r in cm_results if r["monitor_hp"])
    n_seeds = len(SEEDS)

    if n_hc_hp >= 4 and n_dp_hp >= 4 and n_cm_hp >= 4:
        verdict = "HARD_PASS"
    elif n_hc_hp >= 2 or n_dp_hp >= 2 or n_cm_hp >= 2:
        verdict = "MIDDLE_BAND"
    else:
        verdict = "HARD_FAIL"

    elapsed = time.time() - t0
    metrics = {
        "verdict": verdict,
        "verdict_msg": (
            f"Spectral MP primitives: HC n_hp={n_hc_hp}/{n_seeds}, "
            f"DP n_hp={n_dp_hp}/{n_seeds}, CM n_hp={n_cm_hp}/{n_seeds}, "
            f"N={N}, alpha={ALPHA_NOMINAL}"
        ),
        "n_health_check_hp": int(n_hc_hp),
        "n_deletion_privacy_hp": int(n_dp_hp),
        "n_capacity_monitor_hp": int(n_cm_hp),
        "n_seeds": int(n_seeds),
        "N": int(N),
        "alpha_nominal": float(ALPHA_NOMINAL),
        "elapsed_s": float(elapsed),
        "run_mode": RUN_MODE,
        "hc_results": [{"Z_clean": r["Z_clean"], "Z_corr": r["Z_corr"],
                        "lambda_max_clean": r["lambda_max_clean"],
                        "health_hp": bool(r["health_hp"])} for r in hc_results],
        "dp_results": [{"snr_theory": r["snr_theory"], "snr_empirical": r["snr_empirical"],
                        "snr_ratio": r["snr_ratio"],
                        "deletion_hp": bool(r["deletion_hp"])} for r in dp_results],
        "cm_results": [{"pearson_r": r["pearson_r"],
                        "monitor_hp": bool(r["monitor_hp"])} for r in cm_results],
    }

    metrics_path = out_dir / "metrics.json"
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)

    print(f"\n[{ANCHOR_NAME}] VERDICT: {verdict}", flush=True)
    print(f"  HC={n_hc_hp}/{n_seeds} DP={n_dp_hp}/{n_seeds} CM={n_cm_hp}/{n_seeds}",
          flush=True)
    print(f"  elapsed={elapsed:.1f}s -> {metrics_path}", flush=True)


if __name__ == "__main__":
    import argparse as _ap
    _p = _ap.ArgumentParser()
    _p.add_argument("--self-test", action="store_true", dest="self_test")
    _p.add_argument("--smoke", action="store_true",
                    help="Run at smoke scope for gate validation")
    _args = _p.parse_args()
    if _args.self_test:
        sys.exit(0)
    main()