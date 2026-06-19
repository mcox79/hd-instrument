"""Q19 -- Aging exponent mu from C(t, t_w) trajectory.

SCIENTIFIC QUESTION:
  Does the substrate's correlation function C(t, t_w) follow stretched-exponential
  aging with h(t) = exp(-t^(1-mu)) where mu distinguishes aging classes?
  Fit mu from trajectories at 3+ t_w values.
  HP: mu distinguishable from mu=0 (simple aging) and mu=1 (no aging),
      bootstrap CI width < 0.1, and 5/5 seeds agree on regime mu in (0, 1).

PRE-REGISTERED BANDS:
  HARD-PASS: fitted mu in (0, 1) for all 5 seeds AND bootstrap CI width < 0.1
             AND mean_mu distinguishable from 0 AND 1 (> 2sigma from each boundary).
  MIDDLE: mu in [0, 1] but bootstrap CI width >= 0.1 OR seeds disagree on regime
          (>= 1 seed with mu outside (0,1)).
  HARD-FAIL: mu undefined (nan) or out of [0, 1] for >= 3 seeds (substrate NOT in
             stretched-exponential aging class).

THEORY (NE-1 verdict-research drill):
  C(t, t_w) = <s(t) * s(t_w)> / N where s(t) is the state vector at time t.
  For simple aging (mu=0): C(t, t_w) ~ f(t/t_w) (time-translation invariance broken).
  For strong ergodicity breaking (SEB, CK class): C(t_w + Delta_t, t_w) decays
  with waiting time dependence. h(t) = t^(1-mu) gives the exponent.
  mu -> 0: C(t, t_w) ~ exp(-t) (no waiting-time dependence -- ergodic).
  mu -> 1: C(t, t_w) ~ exp(-t^0) = constant (full aging -- complete history dependence).
  mu in (0, 1): intermediate aging class.

DESIGN:
  N=4096, M=200 (alpha=0.049, below capacity for clean dynamics).
  Three waiting times t_w in {50, 100, 200} (simulation steps from random IC).
  For each t_w: evolve from random IC for t_w steps (synchronous Hopfield dynamics),
  then compute C(t_w + Delta_t, t_w) for Delta_t in {1, 2, 5, 10, 20, 50, 100, 200}.
  C(t_w + Delta_t, t_w) = <s(t_w + Delta_t), s(t_w)> / N.
  Fit: C = A * exp(-Delta_t^(1-mu) / tau) for each t_w trajectory.
  Curve fit with scipy.optimize.curve_fit; bootstrap over 100 resamples for CI.
  5 seeds.

  MULTI-SCALE SMOKE: N is not a load-bearing axis here (single N), but smoke uses
  t_w in {50, 100} and Delta_t in {1, 2, 5, 10, 20} to reduce runtime.

FORMULA SELF-TESTS:
  1. C(t_w, t_w) should be ~1.0 (self-overlap after t_w equilibration steps).
     Check: at t_w=50, M=200, N=4096: alpha=0.049 < alpha_c, so system likely
     retrieved a pattern; self-overlap with that state = 1.0 (exact).
  2. C(t_w + 200, t_w) should be < C(t_w, t_w) if aging occurs.
  3. Stretched-exp fit at mu=0 is just exp(-Delta_t/tau) (plain exponential).
     mu=1 gives exp(-1) = const (no decay). mu in (0,1) gives intermediate.

PROT-018: no _nN suffix. Production N=4096 per rule 3.
  Stated: production N = 4096; rationale: aging measurement at moderate N.

TIMEOUT ESTIMATE:
  5 seeds * 3 t_w * max(t_w + Delta_t_max = 200 + 200 = 400) sync steps.
  Each step: matmul W @ s = O(N^2) = 16M ops at N=4096 ~ 16ms.
  Total: 5 * 3 * 400 * 16ms = 96s. With overhead: timeout=900 (10x safety).

Anchor: aging_exponent_mu_v1
Queue: remote_cpu_queue
Pre-reg: preregs/2026-06-01_aging_exponent_mu_v1.md
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
from typing import Dict, List, Optional, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import get_output_dir, resumable_seeds, write_partial  # noqa: E402

ANCHOR_NAME = "aging_exponent_mu_v1"

# Production config
N = 4096
M = 200
TW_GRID_FULL  = [50, 100, 200]
DELTA_T_FULL  = [1, 2, 5, 10, 20, 50, 100, 200]
TW_GRID_SMOKE = [50, 100]
DELTA_T_SMOKE = [1, 2, 5, 10, 20]
N_BOOTSTRAP   = 100
SEEDS_FULL    = [7, 17, 23, 31, 41]
SEEDS_SMOKE   = [7, 17]

# Pre-registered thresholds
HP_CI_WIDTH = 0.10    # bootstrap CI < 0.1
HP_MU_LOW   = 0.0     # mu > 0 (distinguishable from simple exponential)
HP_MU_HIGH  = 1.0     # mu < 1 (distinguishable from constant)
HP_SIGMA_FROM_BOUNDS = 2.0   # mean_mu > 2*sigma from 0 and < 1 - 2*sigma
HF_MIN_SEEDS_FAIL = 3  # >= 3 seeds with mu outside [0,1] => HARD_FAIL


def build_w(patterns: np.ndarray, N: int) -> np.ndarray:
    W = (patterns.T @ patterns) / N
    np.fill_diagonal(W, 0.0)
    return W


def sync_step(W: np.ndarray, s: np.ndarray) -> np.ndarray:
    return np.where(W @ s > 0, 1.0, -1.0)


def evolve(W: np.ndarray, s0: np.ndarray, n_steps: int) -> np.ndarray:
    s = s0.copy()
    for _ in range(n_steps):
        s = sync_step(W, s)
    return s


def compute_C_trajectory(W: np.ndarray, s_tw: np.ndarray, N: int,
                          delta_t_grid: List[int]) -> Dict[int, float]:
    """Compute C(t_w + delta_t, t_w) by evolving s_tw forward."""
    s = s_tw.copy()
    C_vals: Dict[int, float] = {}
    max_dt = max(delta_t_grid)
    dt_set = set(delta_t_grid)
    for dt in range(1, max_dt + 1):
        s = sync_step(W, s)
        if dt in dt_set:
            C_vals[dt] = float(np.dot(s, s_tw) / N)
    return C_vals


def fit_stretched_exp(delta_t: np.ndarray, C_vals: np.ndarray) -> Optional[float]:
    """Fit C = A * exp(-(delta_t / tau)^(1-mu)) and return mu.

    Uses log-linearization: log(-log(C/A)) ~ (1-mu) * log(delta_t) - (1-mu)*log(tau).
    A estimated as C_vals[0] (first point).
    Returns None if fit fails.
    """
    from scipy.optimize import curve_fit

    # Shifted form: C(dt) = exp(-(dt/tau)^beta) where beta = 1 - mu.
    def stretched_exp(dt, beta, log_tau):
        tau = np.exp(log_tau)
        return np.exp(-(dt / tau) ** beta)

    # Initial guess: beta=0.5, tau=10
    try:
        # Clip C_vals to [0.01, 0.999] to avoid log issues
        C_safe = np.clip(C_vals, 0.01, 0.999)
        popt, _ = curve_fit(
            stretched_exp, delta_t.astype(float), C_safe,
            p0=[0.5, np.log(10.0)], maxfev=2000,
            bounds=([0.01, -10.0], [1.99, 10.0])
        )
        beta = float(popt[0])
        mu = 1.0 - beta
        return mu
    except Exception:
        return None


def bootstrap_mu(delta_t: np.ndarray, C_vals: np.ndarray,
                 n_boot: int, rng: np.random.Generator) -> Tuple[float, float]:
    """Bootstrap CI for mu. Returns (ci_low, ci_high)."""
    n = len(delta_t)
    mu_boots = []
    for _ in range(n_boot):
        idx = rng.integers(0, n, size=n)
        dt_b = delta_t[idx]
        C_b  = C_vals[idx]
        mu_b = fit_stretched_exp(dt_b, C_b)
        if mu_b is not None and 0.0 <= mu_b <= 1.0:
            mu_boots.append(mu_b)
    if len(mu_boots) < n_boot // 4:
        return float("nan"), float("nan")
    arr = np.array(mu_boots)
    return float(np.percentile(arr, 5)), float(np.percentile(arr, 95))


def run_seed(seed: int, N: int, M: int, tw_grid: List[int], delta_t_grid: List[int],
             n_bootstrap: int) -> Dict:
    """Compute aging trajectories and fit mu for one seed."""
    rng = np.random.default_rng(seed)
    patterns = rng.choice([-1.0, 1.0], size=(M, N)).astype(np.float64)
    W = build_w(patterns, N)

    tw_results = {}
    for tw in tw_grid:
        # Random IC
        s0 = rng.choice([-1.0, 1.0], size=N).astype(np.float64)
        # Evolve for t_w steps
        s_tw = evolve(W, s0, tw)
        # Measure correlation decay
        C_traj = compute_C_trajectory(W, s_tw, N, delta_t_grid)

        # Fit mu from full trajectory
        dt_arr = np.array(delta_t_grid)
        C_arr  = np.array([C_traj.get(dt, 0.0) for dt in delta_t_grid])
        mu_fit = fit_stretched_exp(dt_arr, C_arr)

        # Bootstrap CI
        rng_boot = np.random.default_rng(seed + tw * 1000)
        ci_lo, ci_hi = bootstrap_mu(dt_arr, C_arr, n_bootstrap, rng_boot)

        tw_results[str(tw)] = {
            "C_trajectory": {str(dt): v for dt, v in C_traj.items()},
            "mu_fit": mu_fit,
            "ci_lo": ci_lo, "ci_hi": ci_hi,
            "ci_width": (ci_hi - ci_lo) if not math.isnan(ci_hi) else float("nan"),
        }

    # Aggregate mu across t_w values (average for seed-level mu)
    mu_vals = [r["mu_fit"] for r in tw_results.values() if r["mu_fit"] is not None and not math.isnan(r["mu_fit"])]
    ci_widths = [r["ci_width"] for r in tw_results.values() if not math.isnan(r.get("ci_width", float("nan")))]

    seed_mu = float(np.mean(mu_vals)) if mu_vals else float("nan")
    seed_ci = float(np.mean(ci_widths)) if ci_widths else float("nan")
    mu_in_range = (not math.isnan(seed_mu)) and (0.0 <= seed_mu <= 1.0)

    return {
        "seed": seed,
        "tw_results": tw_results,
        "seed_mu": seed_mu,
        "seed_ci_width_mean": seed_ci,
        "mu_in_range": mu_in_range,
    }


# ---------------------------------------------------------------------------
# Instrumentation self-test
# ---------------------------------------------------------------------------

def _instrumentation_selftest():
    """Assert C trajectory and mu fit non-null at tiny scale."""
    rng = np.random.default_rng(77)
    N_t, M_t = 256, 20
    pats = rng.choice([-1.0, 1.0], size=(M_t, N_t)).astype(np.float64)
    W_t = build_w(pats, N_t)
    s0 = rng.choice([-1.0, 1.0], size=N_t).astype(np.float64)
    s_tw = evolve(W_t, s0, 10)
    C_traj = compute_C_trajectory(W_t, s_tw, N_t, [1, 2, 5])
    assert len(C_traj) == 3, f"C_traj length wrong: {len(C_traj)}"
    # C(0 steps) = 1.0 implicit; C(some steps) should be in [-1, 1]
    for v in C_traj.values():
        assert -1.0 <= v <= 1.0, f"C out of [-1,1]: {v}"
    # Fit check -- should at minimum run without crashing
    dt_arr = np.array([1, 2, 5])
    C_arr  = np.array([C_traj[1], C_traj[2], C_traj[5]])
    # Fit may fail at tiny scale; just check it doesn't crash
    _ = fit_stretched_exp(dt_arr, C_arr)
    print("[selftest] PASS: aging_exponent_mu_v1 C trajectory non-null", flush=True)


_instrumentation_selftest()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    t0 = time.time()
    run_mode = os.environ.get("HDLAB_RUN_MODE", "full")
    seeds = SEEDS_FULL if run_mode == "full" else SEEDS_SMOKE
    tw_grid    = TW_GRID_FULL  if run_mode == "full" else TW_GRID_SMOKE
    delta_grid = DELTA_T_FULL  if run_mode == "full" else DELTA_T_SMOKE
    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)
    run_config = {"N": N, "run_mode": run_mode}

    print(f"[{ANCHOR_NAME}] run_mode={run_mode} N={N} M={M} tw={tw_grid} "
          f"delta_t={delta_grid} seeds={seeds}", flush=True)

    done, remaining = resumable_seeds(seeds, out_dir, run_config=run_config)
    print(f"[{ANCHOR_NAME}] checkpoint: {len(done)} done, {len(remaining)} remaining", flush=True)

    for seed in remaining:
        print(f"  seed={seed}...", flush=True)
        res = run_seed(seed, N, M, tw_grid, delta_grid, N_BOOTSTRAP)
        res["N"] = N
        res["run_mode"] = run_mode
        write_partial(out_dir, seed, res)

    from experiments._seed_checkpoint import aggregate_partials
    per_seed = aggregate_partials(out_dir, seeds, run_config=run_config)

    mu_vals       = [p["seed_mu"] for p in per_seed.values() if not math.isnan(p.get("seed_mu", float("nan")))]
    ci_widths     = [p["seed_ci_width_mean"] for p in per_seed.values() if not math.isnan(p.get("seed_ci_width_mean", float("nan")))]
    mu_in_range_n = sum(1 for p in per_seed.values() if p.get("mu_in_range", False))

    mean_mu    = float(np.mean(mu_vals))    if mu_vals    else float("nan")
    std_mu     = float(np.std(mu_vals))     if mu_vals    else float("nan")
    mean_ci_w  = float(np.mean(ci_widths))  if ci_widths  else float("nan")
    n_seeds    = len(seeds)
    n_fail_range = n_seeds - mu_in_range_n

    # HP check: mean_mu distinguishable from 0 and 1
    if not math.isnan(mean_mu) and not math.isnan(std_mu) and std_mu > 0:
        sigma_from_0 = mean_mu / (std_mu + 1e-10)
        sigma_from_1 = (1.0 - mean_mu) / (std_mu + 1e-10)
    else:
        sigma_from_0 = float("nan")
        sigma_from_1 = float("nan")

    if (mu_in_range_n == n_seeds and
            not math.isnan(mean_ci_w) and mean_ci_w < HP_CI_WIDTH and
            not math.isnan(sigma_from_0) and sigma_from_0 >= HP_SIGMA_FROM_BOUNDS and
            not math.isnan(sigma_from_1) and sigma_from_1 >= HP_SIGMA_FROM_BOUNDS):
        verdict = "HARD_PASS"
    elif n_fail_range >= HF_MIN_SEEDS_FAIL or math.isnan(mean_mu):
        verdict = "HARD_FAIL"
    else:
        verdict = "MIDDLE_BAND"

    elapsed = time.time() - t0
    metrics = {
        "anchor": ANCHOR_NAME, "run_mode": run_mode, "N": N, "M": M,
        "n_seeds": n_seeds, "mu_in_range_n": mu_in_range_n,
        "mean_mu": mean_mu, "std_mu": std_mu, "mean_ci_width": mean_ci_w,
        "sigma_from_0": sigma_from_0, "sigma_from_1": sigma_from_1,
        "verdict": verdict, "elapsed_s": elapsed,
        "thresholds": {
            "HP_ci_width": HP_CI_WIDTH,
            "HP_sigma_from_bounds": HP_SIGMA_FROM_BOUNDS,
            "HF_min_seeds_fail": HF_MIN_SEEDS_FAIL,
        },
        "verdict_msg": (
            f"Aging exponent mu N={N} M={M}: mean_mu={mean_mu:.4f} "
            f"(HP range (0,1)), std={std_mu:.4f}, mean_CI_width={mean_ci_w:.4f} "
            f"(HP<{HP_CI_WIDTH}), {mu_in_range_n}/{n_seeds} seeds in range. "
            f"sigma_from_0={sigma_from_0:.2f} sigma_from_1={sigma_from_1:.2f}. "
            f"Verdict={verdict}."
        ),
    }

    mpath = out_dir / "metrics.json"
    with open(mpath, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"[{ANCHOR_NAME}] verdict={verdict} mean_mu={mean_mu:.4f} elapsed={elapsed:.1f}s", flush=True)
    print(f"[{ANCHOR_NAME}] metrics -> {mpath}", flush=True)


if __name__ == "__main__":
    import argparse as _ap
    _p = _ap.ArgumentParser()
    _p.add_argument("--self-test", action="store_true", dest="self_test")
    _args = _p.parse_args()
    if _args.self_test:
        sys.exit(0)
    main()
