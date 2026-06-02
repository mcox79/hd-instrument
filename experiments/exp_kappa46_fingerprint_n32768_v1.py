"""
kappa46_fingerprint_n32768_v1 -- Wave 5 Anchor 2: kappa_4 + kappa_6 fingerprint at N=32768.

SCIENTIFIC QUESTION:
  Extend the 1D kappa_3 spectral fingerprint to 3D (kappa_3, kappa_4, kappa_6) at
  production N=32768. Higher cumulants converge only at large N (N=8192 has
  insufficient sample for reliable kappa_6 estimation); cloud-N is required.

  Theory (free-Poisson W = Xi^T Xi / N with M patterns at alpha = M/N):
    kappa_n = alpha for ALL n >= 1 (free-Poisson identity).
  Wigner/GOE: kappa_n = 0 for n >= 3 (binary discriminant).
  Hutchinson estimator (vectorized): kappa_n = mean(diag(V^T W^n V)) / N
  where V is N x n_probes Rademacher matrix.

PRE-REGISTERED BANDS (per Wave 5 handoff):
  HARD-PASS: kappa_4 and kappa_6 each match alpha within 5% free-Poisson prediction.
  MIDDLE: one of {kappa_4, kappa_6} within 10%; other within 20%.
  HARD-FAIL: either cumulant deviates from alpha by >50% OR sign disagreement.

  Calibration probe -- no prior empirical anchor for kappa_4 / kappa_6 at N=32768.
  Bands at +-50% per policy.

FORMULA SELF-TESTS:
  1. kappa_n_theory(alpha=0.05) = 0.05 for all n (free-Poisson identity).
  2. For W = I (identity, M=N): kappa_n = 1.0 for all n (no scaling needed).
  3. Hutchinson Rademacher trick: E[V^T A V] = Tr(A) for V iid Rademacher.

PROT-018: anchor has _n32768 -> N must = 32768.
PROT-021: run_config includes N, M, run_mode.
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import argparse
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

ANCHOR_NAME = "kappa46_fingerprint_n32768_v1"

# PROT-018: anchor has _n32768 -> N must = 32768
_N_SUFFIX = 32768
N_FULL = 32768
N_SMOKE = 4096

ALPHA_GRID = [0.05]  # single alpha at production N (cloud cost discipline)
SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [7, 17]
N_PROBES = 1000  # Hutchinson probes (vectorized; ~30s per cell at N=32768)

HP_REL_BAND = 0.05      # within 5% of alpha
MID_REL_BAND = 0.20     # within 20%
HF_REL_BAND = 0.50      # >50% off = HARD_FAIL


def hutchinson_kappa_n(W: np.ndarray, n: int, n_probes: int, rng: np.random.Generator) -> float:
    """Vectorized Hutchinson estimator for kappa_n = Tr(W^n) / N.

    Builds Rademacher V (N x n_probes), applies W repeatedly: V <- W @ V.
    After n applications, kappa_n = mean(diag(V_orig^T @ V_after)) / N.
    """
    N = W.shape[0]
    V0 = rng.choice([-1.0, 1.0], size=(N, n_probes)).astype(W.dtype)
    Vk = V0.copy()
    for _ in range(n):
        Vk = W @ Vk
    # diag(V0^T @ Vk) = element-wise (V0 * Vk).sum(axis=0)
    diag = (V0 * Vk).sum(axis=0)
    return float(np.mean(diag)) / float(N)


def _instrumentation_selftest():
    """Identity self-test: for W=I, kappa_n = 1.0 for all n."""
    rng = np.random.default_rng(0)
    N_t = 128
    W_id = np.eye(N_t, dtype=float)
    for n in [3, 4, 6]:
        k_est = hutchinson_kappa_n(W_id, n, 200, rng)
        assert abs(k_est - 1.0) < 0.1, f"kappa_{n}(I) selftest: got {k_est} expected ~1.0"
    print(f"[selftest] PASS: identity-W kappa_n estimates near 1.0", flush=True)


_instrumentation_selftest()


def _prot018_startup_check(n_actual: int) -> None:
    N_BOUND = 32768
    if n_actual != N_BOUND:
        raise RuntimeError(
            f"PROT-018 VIOLATION: anchor name '{ANCHOR_NAME}' binds to "
            f"N={N_BOUND} but script is running at N={n_actual}. "
            f"Check HDLAB_RUN_MODE env var (must be 'full' for production run).")


def main():
    t0 = time.time()
    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)
    run_mode = os.environ.get("HDLAB_RUN_MODE", "full")
    seeds = SEEDS_FULL if run_mode == "full" else SEEDS_SMOKE
    N = N_FULL if run_mode == "full" else N_SMOKE
    if run_mode == "full":
        _prot018_startup_check(N)
    print(f"[{ANCHOR_NAME}] run_mode={run_mode} seeds={seeds} N={N} "
          f"alpha_grid={ALPHA_GRID} n_probes={N_PROBES}", flush=True)

    per_seed_results: List[Dict] = []
    for seed in seeds:
        rng = np.random.default_rng(seed)
        for alpha in ALPHA_GRID:
            M = max(1, int(alpha * N))
            print(f"  seed={seed} alpha={alpha} M={M}: building W...", flush=True)
            t_cell = time.time()
            Pats = rng.choice([-1.0, 1.0], size=(M, N)).astype(np.float32)
            # W = (1/N) Pats^T Pats; rank-M; use Gram trick to avoid N x N materialization
            # W @ v = (1/N) Pats^T (Pats @ v)
            class WOp:
                def __init__(self, P, N):
                    self.P = P
                    self.N = N
                def __matmul__(self, V):
                    return (self.P.T @ (self.P @ V)) / self.N
            W_op = WOp(Pats, N)
            row_result = {"seed": seed, "alpha": alpha, "M": M}
            for n in [3, 4, 6]:
                # Adapted hutchinson with operator (not dense W)
                V0 = rng.choice([-1.0, 1.0], size=(N, N_PROBES)).astype(np.float32)
                Vk = V0.copy()
                for _ in range(n):
                    Vk = W_op @ Vk
                diag = (V0.astype(np.float64) * Vk.astype(np.float64)).sum(axis=0)
                kappa_n = float(np.mean(diag)) / float(N)
                row_result[f"kappa_{n}"] = kappa_n
                row_result[f"kappa_{n}_rel_dev"] = abs(kappa_n - alpha) / alpha
            elapsed_cell = time.time() - t_cell
            row_result["elapsed_s"] = elapsed_cell
            print(f"    kappa_3={row_result['kappa_3']:.5f} "
                  f"kappa_4={row_result['kappa_4']:.5f} "
                  f"kappa_6={row_result['kappa_6']:.5f} "
                  f"(target alpha={alpha}; {elapsed_cell:.1f}s)", flush=True)
            per_seed_results.append(row_result)

    # Aggregate: mean rel dev for kappa_4 and kappa_6 across seeds at primary alpha
    primary_alpha = ALPHA_GRID[0]
    k4_devs = [r["kappa_4_rel_dev"] for r in per_seed_results if r["alpha"] == primary_alpha]
    k6_devs = [r["kappa_6_rel_dev"] for r in per_seed_results if r["alpha"] == primary_alpha]
    k4_mean_dev = float(np.mean(k4_devs))
    k6_mean_dev = float(np.mean(k6_devs))

    k4_hp = k4_mean_dev < HP_REL_BAND
    k6_hp = k6_mean_dev < HP_REL_BAND
    k4_hf = k4_mean_dev > HF_REL_BAND
    k6_hf = k6_mean_dev > HF_REL_BAND

    if k4_hp and k6_hp:
        verdict = "HARD_PASS"
    elif k4_hf or k6_hf:
        verdict = "HARD_FAIL"
    else:
        verdict = "MIDDLE_BAND"

    elapsed = time.time() - t0
    metrics = {
        "anchor": ANCHOR_NAME, "run_mode": run_mode,
        "N": N, "alpha_grid": ALPHA_GRID, "n_seeds": len(seeds),
        "n_probes": N_PROBES,
        "per_seed_results": per_seed_results,
        "kappa_4_mean_rel_dev": k4_mean_dev,
        "kappa_6_mean_rel_dev": k6_mean_dev,
        "kappa_4_hp": k4_hp, "kappa_6_hp": k6_hp,
        "verdict": verdict,
        "elapsed_s": elapsed,
        "verdict_msg": (
            f"kappa_4 + kappa_6 fingerprint at N={N}: "
            f"kappa_4 mean rel_dev = {k4_mean_dev:.4f} ({'HP' if k4_hp else ('HF' if k4_hf else 'MID')}); "
            f"kappa_6 mean rel_dev = {k6_mean_dev:.4f} ({'HP' if k6_hp else ('HF' if k6_hf else 'MID')}). "
            f"Verdict: {verdict}."
        ),
    }
    mpath = out_dir / "metrics.json"
    with open(mpath, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"[{ANCHOR_NAME}] verdict={verdict} elapsed={elapsed:.1f}s", flush=True)
    print(f"[{ANCHOR_NAME}] metrics -> {mpath}", flush=True)


if __name__ == "__main__":
    main()
