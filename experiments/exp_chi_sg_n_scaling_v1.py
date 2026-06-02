"""chi_SG N-scaling: spin-glass order parameter test for extensive FRSB phase.

SCIENTIFIC QUESTION:
  Does chi_SG = (1/N) * sum_{i,j} [<sigma_i sigma_j>^2 - <sigma_i>^2 <sigma_j>^2]
  scale as N^1 (extensive FRSB phase) or remain O(1) (replica-symmetric phase)?

  In the FRSB spin-glass phase: chi_SG ~ N (extensive).
  In the replica-symmetric phase: chi_SG ~ O(1) (non-extensive).
  HP criterion: log-log slope of chi_SG vs N in [0.8, 1.2].

  Simplified estimator (computational proxy):
  chi_SG = sum_{i,j} q_ij^2 / N^2 where q_ij = <sigma_i sigma_j> (thermal average).
  For finite-temperature Hopfield with Glauber dynamics:
  q_ij = time-average of sigma_i(t) sigma_j(t) over a long trajectory.
  But this is O(N^2) storage. Instead use the diagonal approximation:
  chi_SG_proxy = (N/M) * sum_mu q_mu^2 where q_mu = |<sigma, xi_mu> / N|.
  This is the standard GLASS ORDER PARAMETER in Hopfield models.
  In the spin-glass phase: chi_SG_proxy scales with N as the Edwards-Anderson parameter
  times N. In RS phase: chi_SG_proxy ~ constant.

PRE-REGISTERED BANDS:
  HARD-PASS: log-log slope of chi_SG vs N in [0.8, 1.2] (consistent with N^1 scaling)
             in >= 4/5 seeds across N-grid.
  MIDDLE: slope in [0.4, 1.5] (consistent with extensive but noisy).
  HARD-FAIL: slope < 0.3 (RS phase) or > 1.5 (anomalous) in >= 3/5 seeds.
  Note: calibration probe; +-50% HP bands. HP at [0.8,1.2]; HF outside [0.3, 1.5].

DESIGN:
  N_grid = [256, 512, 1024, 2048, 4096] at fixed alpha=0.15 (above alpha_c).
  Also N_grid at alpha=0.05 as CONTROL (should show chi_SG ~ O(1) or weaker scaling).
  M = int(alpha * N) for each N.
  T = 5 (beta=0.2, low temperature -> strong spin-glass).
  n_steps_thermalize = 2 * N (thermalization).
  n_steps_measure = 10 * N (measurement window).
  5 seeds per (N, alpha).

MEASUREMENT:
  Glauber dynamics: flip neuron i with prob sigmoid(-2 * beta * h_i * sigma_i).
  chi_SG proxy = (N/M) * sum_mu (1/T_meas * sum_t sigma(t) . xi_mu / N)^2
  where T_meas is number of measurement steps.
  This is the standard replica overlap summed over patterns.

GPU MEMORY:
  W: N^2 * 4B. At N=4096: 64MB. At N=2048: 16MB. Fine.
  States: N * n_seeds * 4B. Trivial.

PROT-018: no _nN suffix. Multiple N values are the sweep; production min N=256.
  Stated: N ranges from 256 to 4096; rationale: chi_SG N-scaling sweep.

MULTI-SCALE SMOKE: N=256 and N=1024 both run.

TIMEOUT ESTIMATE:
  GPU Glauber at N=4096: each step updates N neurons via GPU kernel.
  n_steps = 14*4096 = 57344 per (seed, N). At N=4096, GPU: ~0.5ms per step.
  5 seeds * 5 N_values * 57344 steps: but total step*N load scales as O(N^2) per seed.
  Dominant term: N=4096, 5 seeds, 14*4096 steps = 2.9M step*4096 = 12B ops. ~60s.
  Total: ~200s. timeout_s=ceil(1.5*200)=300 -> 600s.

Anchor: chi_sg_n_scaling_v1
Queue: overnight_queue
Pre-reg: preregs/2026-06-01_chi_sg_n_scaling_v1.md
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

try:
    import torch
    DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False
    DEVICE = None
    torch = None  # type: ignore

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import get_output_dir  # noqa: E402

ANCHOR_NAME = "chi_sg_n_scaling_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

# PROT-018: no _nN suffix. N sweep; rule 3.
BETA = 5.0  # inverse temperature (T=0.2, strongly coupled)

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    N_GRID = [256, 512]
    ALPHA_GRID = [0.15]
    N_THERM_FACTOR = 2
    N_MEAS_FACTOR = 5
else:
    SEEDS = [7, 17, 23, 31, 41]
    N_GRID = [256, 512, 1024, 2048, 4096]
    ALPHA_GRID = [0.15, 0.05]  # SG phase + control
    N_THERM_FACTOR = 2
    N_MEAS_FACTOR = 10


def build_W_torch(N: int, M: int, seed: int, device: "torch.device") -> "torch.Tensor":
    rng = np.random.RandomState(seed)
    Xi = rng.choice([-1, 1], size=(N, M)).astype(np.float32)
    Xi_t = torch.tensor(Xi, dtype=torch.float32, device=device)
    W = (Xi_t @ Xi_t.t()) / N
    return W, Xi_t


def run_glauber_chi_sg(N: int, M: int, seed: int, beta: float,
                       n_therm: int, n_meas: int,
                       device: "torch.device") -> Dict:
    rng_np = np.random.RandomState(seed + 1000)
    W, Xi_t = build_W_torch(N, M, seed, device)

    # Initial random state
    sigma = torch.tensor(
        rng_np.choice([-1.0, 1.0], size=N).astype(np.float32),
        device=device
    )

    # Thermalization: random sequential Glauber
    for _ in range(n_therm):
        h = W @ sigma  # (N,)
        flip_prob = 1.0 / (1.0 + torch.exp(2.0 * beta * h * sigma))
        rand_vals = torch.rand(N, device=device)
        flips = rand_vals < flip_prob
        sigma = torch.where(flips, -sigma, sigma)

    # Measurement: accumulate overlap with each pattern
    overlap_sum = torch.zeros(M, device=device)  # sum_t <sigma(t), xi_mu> / N
    overlap_sq_sum = torch.zeros(M, device=device)  # sum_t (<sigma(t), xi_mu>/N)^2

    for t in range(n_meas):
        h = W @ sigma
        flip_prob = 1.0 / (1.0 + torch.exp(2.0 * beta * h * sigma))
        rand_vals = torch.rand(N, device=device)
        flips = rand_vals < flip_prob
        sigma = torch.where(flips, -sigma, sigma)
        # Overlaps with all patterns
        m_vec = (Xi_t.t() @ sigma) / N  # (M,)
        overlap_sum += m_vec
        overlap_sq_sum += m_vec ** 2

    # Time-averaged overlaps
    q_mu = overlap_sum / n_meas  # (M,)
    q_mu2_avg = overlap_sq_sum / n_meas  # (M,)

    # chi_SG = (1/M) * sum_mu (q_mu^2 - (avg_q_mu)^2) * N
    # But commonly: chi_SG = N * mean_mu(q_mu^2 - <q_mu>^2)
    # Use: chi_SG_proxy = N * mean(q_mu^2) - N * mean(q_mu)^2
    # This is the variance of the overlap times N.
    mean_q2 = float(torch.mean(q_mu2_avg).cpu())
    mean_q = float(torch.mean(torch.abs(q_mu)).cpu())

    # Standard chi_SG = N * E[q^2] where q = time-average overlap (quenched)
    chi_sg = N * mean_q2
    # Also compute: (N/M) * ||q_mu||^2 = N * mean(q_mu^2)
    chi_sg_v2 = float(N * torch.mean(q_mu ** 2).cpu())

    return {
        "N": N,
        "M": M,
        "alpha": M / N,
        "seed": seed,
        "chi_sg": chi_sg,
        "chi_sg_v2": chi_sg_v2,
        "mean_q2": mean_q2,
        "mean_q_abs": mean_q,
        "n_meas": n_meas,
    }


def _instrumentation_selftest():
    """Assert chi_SG is non-null and non-zero at small scale."""
    if not HAS_TORCH:
        return
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    r = run_glauber_chi_sg(N=128, M=20, seed=999, beta=BETA,
                           n_therm=256, n_meas=512, device=device)
    assert r["chi_sg"] is not None, "chi_sg is None"
    assert not math.isnan(r["chi_sg"]), "chi_sg is NaN"
    assert r["chi_sg"] > 0, f"chi_sg={r['chi_sg']} <= 0 (non-zero by definition)"
    print(f"[selftest] PASS: chi_sg={r['chi_sg']:.4f} N=128 M=20", flush=True)


_instrumentation_selftest()


def main():
    t0 = time.time()
    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)

    if not HAS_TORCH:
        print(f"[{ANCHOR_NAME}] ERROR: torch required", flush=True)
        return

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[{ANCHOR_NAME}] RUN_MODE={RUN_MODE} device={device} seeds={SEEDS}",
          flush=True)
    print(f"  N_grid={N_GRID} alpha_grid={ALPHA_GRID} beta={BETA}", flush=True)

    all_results = []
    for alpha in ALPHA_GRID:
        for N in N_GRID:
            M = max(1, int(alpha * N))
            n_therm = N_THERM_FACTOR * N
            n_meas = N_MEAS_FACTOR * N
            for seed in SEEDS:
                print(f"  alpha={alpha} N={N} M={M} seed={seed}...", flush=True)
                r = run_glauber_chi_sg(N, M, seed, BETA, n_therm, n_meas, device)
                all_results.append(r)
                print(f"    chi_sg={r['chi_sg']:.4f} chi_sg_v2={r['chi_sg_v2']:.4f} "
                      f"mean_q2={r['mean_q2']:.4f}", flush=True)

    # Compute log-log slope for each (alpha, seed)
    from scipy.stats import linregress  # type: ignore

    slope_by_alpha_seed = {}
    for alpha in ALPHA_GRID:
        for seed in SEEDS:
            pts = [(r["N"], r["chi_sg"]) for r in all_results
                   if r["alpha"] == alpha and r["seed"] == seed
                   and r["chi_sg"] > 0]
            if len(pts) >= 2:
                log_N = np.log([p[0] for p in pts])
                log_chi = np.log([p[1] for p in pts])
                slope, _, r2, _, _ = linregress(log_N, log_chi)
                slope_by_alpha_seed[(alpha, seed)] = {
                    "slope": float(slope),
                    "r2": float(r2),
                }
                print(f"  alpha={alpha} seed={seed} slope={slope:.3f} r2={r2:.3f}",
                      flush=True)

    # Verdict based on alpha=0.15 (SG phase)
    sg_slopes = [v["slope"] for (a, s), v in slope_by_alpha_seed.items() if a == 0.15]
    ctrl_slopes = [v["slope"] for (a, s), v in slope_by_alpha_seed.items() if a == 0.05]

    if sg_slopes:
        mean_sg_slope = float(np.mean(sg_slopes))
        n_hp = sum(1 for s in sg_slopes if 0.8 <= s <= 1.2)
        n_seeds_sg = len(sg_slopes)
    else:
        mean_sg_slope = 0.0
        n_hp = 0
        n_seeds_sg = 0

    if n_hp >= max(4, n_seeds_sg - 1) and 0.8 <= mean_sg_slope <= 1.2:
        verdict = "HARD_PASS"
    elif n_hp >= 2 or (0.4 <= mean_sg_slope <= 1.5):
        verdict = "MIDDLE_BAND"
    elif mean_sg_slope < 0.3 or mean_sg_slope > 1.5:
        verdict = "HARD_FAIL"
    else:
        verdict = "MIDDLE_BAND"

    elapsed = time.time() - t0
    metrics = {
        "verdict": verdict,
        "verdict_msg": (
            f"chi_SG N-scaling: mean_slope={mean_sg_slope:.3f} [HP: 0.8-1.2], "
            f"n_hp_seeds={n_hp}/{n_seeds_sg}, "
            f"ctrl_slopes={ctrl_slopes}, N_grid={N_GRID}"
        ),
        "mean_log_log_slope_sg": mean_sg_slope,
        "sg_slopes_per_seed": sg_slopes,
        "ctrl_slopes_per_seed": ctrl_slopes,
        "n_hp_seeds": n_hp,
        "n_seeds_sg": n_seeds_sg,
        "N_grid": N_GRID,
        "alpha_sg": 0.15,
        "alpha_ctrl": 0.05,
        "elapsed_s": float(elapsed),
        "run_mode": RUN_MODE,
        "per_result": all_results,
    }

    metrics_path = out_dir / "metrics.json"
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)

    print(f"\n[{ANCHOR_NAME}] VERDICT: {verdict}", flush=True)
    print(f"  mean_sg_slope={mean_sg_slope:.3f} n_hp={n_hp}/{n_seeds_sg}", flush=True)
    print(f"  elapsed={elapsed:.1f}s", flush=True)
    print(f"  metrics -> {metrics_path}", flush=True)


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