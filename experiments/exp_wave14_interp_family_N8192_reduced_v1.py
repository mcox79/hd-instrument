"""N=8192 retry with REDUCED configs — substrate-honest substitute for timed-out N=8192.

Motivation
----------
The full E2 stress anchor `wave14_interp_family_N8192_v1` runs 3 families x
3 N values x 5 alphas x 5 seeds = 225 cells incl. N=8192 SVDs and full AMP +
VAMP loops at 300 iterations. The N=8192 portion alone is expensive enough
that prior cycles' N=16384 attempt TIMED OUT (per cap_map v175 / E2 ship
note in exp_dev_decisions_2026-05-24).

This script runs JUST the N=8192 portion at REDUCED grid:
  - 2 families (SRHT, Hadamard; Kerdock structurally absent at N=8192 since
    log2(8192)=13 odd) — same as v1.
  - 3 alpha values (0.0, 0.5, 1.0) instead of 5 (covers endpoints + midpoint).
  - 3 seeds instead of 5.
  - n_iter = 200 instead of 300 (AMP usually converges in ~50-100; 200 is
    enough buffer for the Spearman test).

Total cells: 2 families * 3 alphas * 3 seeds = 18 SVDs of (8192, 8192). At
~30-40 sec per SVD that's ~10 min of SVD work plus AMP/VAMP ~ ~50 min total.
ETA 60-90 min on GPU.

If this PASSes (rho >= 0.50 on both families AT REDUCED CELLS), Cap 12 ✅
gets a thin N=8192 endorsement (N-scaling holds on SRHT + Hadamard, with the
caveat that 3 alphas may not give full Spearman power). If it FAILs, the
v1 full E2 run would be expected to fail too.

Pre-reg: preregs/2026-05-24_wave14_interp_family_N8192_reduced_v1.md
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

from experiments._seed_checkpoint import get_output_dir as _canonical_get_output_dir  # noqa: E402  # SH-4 canonical helper
# Reuse v1 (full) machinery
_v1_path = REPO / "experiments" / "exp_wave14_interp_family_N8192_v1.py"
_spec = importlib.util.spec_from_file_location("interp_v1", _v1_path)
_v1 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_v1)

build_W_alpha = _v1.build_W_alpha
bbmd_distance = _v1.bbmd_distance
compute_rho_per_family_N = _v1.compute_rho_per_family_N
compute_verdict = _v1.compute_verdict
self_test = _v1.self_test
moments_to_free_cumulants_general = _v1.moments_to_free_cumulants_general
amp_se_scalar = _v1.amp_se_scalar
vamp_se_closed = _v1.vamp_se_closed
run_amp = _v1.run_amp
run_vamp = _v1.run_vamp
N_MAX_MOMENT = _v1.N_MAX_MOMENT


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


def run_one_cell(family: str, alpha: float, N: int, M: int, seed: int,
                 sigma: float, signal_var: float, n_iter: int,
                 n_max: int, struct_cache: dict) -> dict:
    """Build W_alpha, compute spectrum / free cumulants, run AMP + VAMP, return cell dict."""
    W = build_W_alpha(family, alpha, N, M, seed, struct_cache)
    # eigenvalues of W^T W
    _, s, _ = np.linalg.svd(W, full_matrices=False)
    eig = (s ** 2).astype(np.float64)
    # Moments + free cumulants
    moments = []
    for n in range(1, n_max + 1):
        moments.append(float(np.mean(eig ** n)))
    kappas = moments_to_free_cumulants_general(moments)
    c_ref = M / N
    dist = bbmd_distance(kappas, c_ref, 2, n_max)
    # AMP + VAMP synthetic-signal (use signal_var, sigma)
    # run_amp / run_vamp return final MSE; rel_err = sqrt(MSE / signal_var)
    rng = np.random.default_rng(seed * 31 + 7)
    x_true = rng.standard_normal(N) * math.sqrt(signal_var)
    noise = rng.standard_normal(M) * sigma
    y = W @ x_true + noise
    try:
        mse_amp = run_amp(W, y, x_true, signal_var, sigma**2, n_iter)
        # VAMP needs SVD
        U, sv, Vt = np.linalg.svd(W, full_matrices=False)
        mse_vamp = run_vamp(U, sv, Vt, y, x_true, signal_var, sigma**2, n_iter)
        amp_rel_err = float(math.sqrt(max(mse_amp, 0.0) / max(signal_var, 1e-12)))
        vamp_rel_err = float(math.sqrt(max(mse_vamp, 0.0) / max(signal_var, 1e-12)))
    except Exception as e:
        print(f"  AMP/VAMP error: {e}", flush=True)
        amp_rel_err = float("nan")
        vamp_rel_err = float("nan")
    return {
        "family": family,
        "N": int(N),
        "alpha": float(alpha),
        "seed": int(seed),
        "amp_rel_err_mean": amp_rel_err,
        "vamp_rel_err_mean": vamp_rel_err,
        "bbmd_distance_mean": float(dist),
        "kappas": [float(x) for x in kappas],
    }


def run_experiment(smoke: bool) -> tuple[dict, str, str, float, dict]:
    t0 = time.monotonic()

    if smoke:
        config = {
            "mode": "smoke",
            "N_grid": [64],
            "M_over_N": 1.0,
            "alpha_interp_list": [0.0, 0.5, 1.0],
            "sigma_noise": 0.1,
            "signal_var": 1.0,
            "n_seeds": 1,
            "n_iter": 50,
            "n_max_moment": N_MAX_MOMENT,
            "families": ["srht", "hadamard"],
        }
    else:
        # REDUCED: only N=8192, 3 alphas, 3 seeds, 2 families.
        config = {
            "mode": "full",
            "N_grid": [8192],
            "M_over_N": 1.0,
            "alpha_interp_list": [0.0, 0.5, 1.0],
            "sigma_noise": 0.1,
            "signal_var": 1.0,
            "n_seeds": 3,
            "n_iter": 200,
            "n_max_moment": N_MAX_MOMENT,
            "families": ["srht", "hadamard"],
        }

    sigma = config["sigma_noise"]
    signal_var = config["signal_var"]
    n_max = config["n_max_moment"]
    n_seeds = config["n_seeds"]
    n_iter = config["n_iter"]
    alpha_list = config["alpha_interp_list"]

    print(
        f"[setup] families={config['families']} N_grid={config['N_grid']} "
        f"alpha_interp={alpha_list} seeds={n_seeds} mode={config['mode']}",
        flush=True,
    )

    struct_cache: dict = {}
    cells = []
    for family in config["families"]:
        for N in config["N_grid"]:
            M = int(config["M_over_N"] * N)
            for alpha in alpha_list:
                # Average over seeds
                seed_results = []
                for seed in range(n_seeds):
                    try:
                        cell = run_one_cell(family, alpha, N, M, seed, sigma,
                                            signal_var, n_iter, n_max,
                                            struct_cache)
                        seed_results.append(cell)
                        print(
                            f"[{family} N={N} alpha={alpha} seed={seed}] "
                            f"amp_re={cell['amp_rel_err_mean']:.4f} "
                            f"vamp_re={cell['vamp_rel_err_mean']:.4f} "
                            f"dist={cell['bbmd_distance_mean']:.4f}",
                            flush=True,
                        )
                    except Exception as e:
                        print(f"  ERR seed={seed}: {e}", flush=True)
                if not seed_results:
                    continue
                # Aggregate over seeds
                amp_mean = float(np.mean([c["amp_rel_err_mean"] for c in seed_results]))
                vamp_mean = float(np.mean([c["vamp_rel_err_mean"] for c in seed_results]))
                dist_mean = float(np.mean([c["bbmd_distance_mean"] for c in seed_results]))
                cells.append({
                    "family": family,
                    "N": int(N),
                    "alpha": float(alpha),
                    "amp_rel_err_mean": amp_mean,
                    "vamp_rel_err_mean": vamp_mean,
                    "bbmd_distance_mean": dist_mean,
                    "n_seeds": len(seed_results),
                })

    rho_map = compute_rho_per_family_N(cells)
    summary = {"cells": cells, "rho_per_family_N": rho_map, "config": config}
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic() - t0
    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)
    return summary, verdict, msg, elapsed, config


def write_metrics(out_dir: Path, summary: dict, verdict: str, msg: str,
                  elapsed: float, config: dict) -> None:
    # rho_per_family_N may have tuple key issues — already done in v1
    # via rho_per_family_N_serialized; we just dump
    summary_out = dict(summary)
    # Stringify any tuple keys
    if "rho_per_family_N" in summary_out:
        summary_out["rho_per_family_N"] = {
            (k if isinstance(k, str) else str(k)): v
            for k, v in summary_out["rho_per_family_N"].items()
        }
    metrics = {
        "verdict": verdict,
        "verdict_msg": msg,
        "elapsed_s": elapsed,
        "summary": summary_out,
        "config": config,
    }
    validate_metrics(metrics)
    tmp = out_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(metrics, indent=2, default=float))
    tmp.replace(out_dir / "metrics.json")
    print(f"wrote {out_dir / 'metrics.json'}", flush=True)


def run_smoke() -> None:
    self_test()
    out_dir = get_output_dir("wave14_interp_family_N8192_reduced_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main() -> None:
    self_test()
    out_dir = get_output_dir("wave14_interp_family_N8192_reduced_v1")
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
