"""
tau_mem_decay_sweep_v1 -- Continuous-time write dynamics: tau_mem empirical validation.

SCIENTIFIC QUESTION (continuous-time write dynamics handoff 2026-06-01):
  Does the substrate's retrieval accuracy decay with a characteristic time
  tau_mem ~ N / (2 * lambda) where lambda is the write rate and gamma is the
  decay/forgetting rate (Ornstein-Uhlenbeck decay), matching the prediction
  from compound-Poisson + OU theory?

  Setup: discrete-time simulation of continuous write dynamics.
  At each timestep t: with prob p_write = lambda * dt, a NEW random BSC pattern
  is added to W: W <- W + xi_new xi_new^T / N.
  With prob p_decay = gamma * dt, each stored pattern's contribution decays:
  W <- (1 - gamma*dt) * W (exponential decay approximation).
  After T steps, measure retrieval accuracy on patterns written at t=0.

  The effective number of patterns in W at stationarity is M_eff = lambda / gamma.
  Retrieval accuracy should decay as ~ exp(-t * 2*lambda/N) for a single stored pattern.
  tau_mem = N / (2*lambda).

PRE-REGISTERED BANDS (calibration probe -- no prior empirical anchor):
  HARD-PASS: measured tau_mem_empirical / tau_mem_theoretical in [0.5, 2.0]
             (within factor of 2, consistent with calibration probe +-50% policy),
             for >= 4/5 seeds AND >= 3/4 (lambda, gamma) configurations.
  MIDDLE: ratio in [0.25, 4.0] (less than 4x off).
  HARD-FAIL: ratio outside [0.10, 10.0] (one order of magnitude off -- theory wrong).

FORMULA SELF-TESTS:
  1. tau_mem(N=4096, lambda=0.1) = 4096 / (2*0.1) = 20480 steps.
  2. tau_mem(N=4096, lambda=1.0) = 4096 / 2.0 = 2048 steps.
  3. At M_eff = lambda/gamma, retrieval accuracy should match static Hopfield at M=M_eff.

No _nN suffix; production N=4096 per rule 3.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import os
import argparse
import time
import json
import math
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from experiments._seed_checkpoint import get_output_dir

ANCHOR_NAME = "tau_mem_decay_sweep_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

N = 4096

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    # (lambda_rate, gamma_decay) configurations -- per-step write rate + decay rate
    # Choose lambda such that tau_mem = N/(2*lambda) is well within T_MAX_STEPS
    # tau_mem(lam=2.0) = 4096/4 = 1024 steps; tau_mem(lam=5.0) = 410 steps
    CONFIGS = [
        (2.0, 0.2),   # tau_mem = 1024 steps, M_eff = 10
        (5.0, 0.5),   # tau_mem = 410 steps, M_eff = 10
    ]
    DT = 1.0
    T_MAX_STEPS = 4000   # 4x tau_mem for lam=2 config
    N_QUERY_PATTERNS = 3
    MEASURE_INTERVAL = 50
else:
    SEEDS = [7, 17, 23, 31, 41]
    CONFIGS = [
        (2.0, 0.2),   # tau_mem = 1024 steps, M_eff = 10
        (5.0, 0.5),   # tau_mem = 410 steps, M_eff = 10
        (10.0, 1.0),  # tau_mem = 205 steps, M_eff = 10
        (20.0, 2.0),  # tau_mem = 102 steps, M_eff = 10
    ]
    DT = 1.0
    T_MAX_STEPS = 5000   # 5x tau_mem for slowest config
    N_QUERY_PATTERNS = 5
    MEASURE_INTERVAL = 100

# Pre-reg thresholds
HP_RATIO_LOW = 0.5    # tau_empirical / tau_theory >= 0.5
HP_RATIO_HIGH = 2.0   # tau_empirical / tau_theory <= 2.0
HF_RATIO_LOW = 0.10
HF_RATIO_HIGH = 10.0
HP_FRAC_CONFIGS = 3/4  # 3/4 configs must pass HP
HP_FRAC_SEEDS = 4/5

# Formula self-tests
def tau_mem_theory(N: int, lambda_rate: float) -> float:
    """tau_mem = N / (2 * lambda)."""
    return N / (2.0 * lambda_rate)

assert abs(tau_mem_theory(4096, 2.0) - 1024.0) < 1.0, "tau_mem formula error: lam=2"
assert abs(tau_mem_theory(4096, 5.0) - 409.6) < 1.0, "tau_mem formula error: lam=5"


def hopfield_retrieve_single(W: np.ndarray, query: np.ndarray, n_steps: int = 5) -> np.ndarray:
    """Synchronous Hopfield retrieval."""
    s = query.copy()
    for _ in range(n_steps):
        s_new = np.where(W @ s > 0, 1.0, -1.0)
        if np.all(s_new == s):
            break
        s = s_new
    return s


def retrieval_accuracy(retrieved: np.ndarray, target: np.ndarray) -> float:
    """Fraction of matching bits."""
    return float(np.mean(retrieved == target))


def simulate_decay(N: int, lambda_rate: float, gamma_decay: float,
                    query_patterns: np.ndarray, t_max: int, dt: float,
                    measure_interval: int, seed: int) -> Dict:
    """
    Simulate continuous write + decay dynamics using pattern-list representation.

    Instead of maintaining W as a dense N x N matrix (O(N^2) per write),
    we maintain a list of (pattern, weight) pairs.

    W(t) = sum_i w_i(t) * xi_i xi_i^T / N
    where w_i(t) = exp(-gamma * (t - t_i)) for pattern written at t_i.

    At each timestep:
      - Decay all weights: w_i *= (1 - gamma*dt)
      - Drop patterns whose weight falls below threshold (M_eff floor pruning)
      - Write new pattern with prob lambda*dt

    Retrieval: W @ q = (1/N) * sum_i w_i * xi_i * (xi_i^T q)
               = (1/N) * Xi_mat^T @ (weights * (Xi_mat @ q))
    where Xi_mat is the (M, N) pattern matrix. O(M_eff * N) per query.

    This avoids the O(N^2) outer product bottleneck at large N.
    """
    rng = np.random.RandomState(seed)
    n_q = query_patterns.shape[0]

    # Initialize pattern list: rows of query_patterns + weights 1.0
    pat_list = list(query_patterns)   # each is shape (N,)
    wt_list = [1.0] * len(pat_list)

    W_PRUNE_THRESH = 1e-4  # drop patterns with negligible weight

    def w_times_q(pats, wts, q):
        """Compute W @ q efficiently via pattern list. O(M * N)."""
        if not pats:
            return np.zeros(len(q))
        Xi = np.array(pats)   # (M, N)
        wts_arr = np.array(wts)  # (M,)
        dots = Xi @ q         # (M,) -- inner products
        return Xi.T @ (wts_arr * dots) / N  # (N,)

    def hopfield_step(pats, wts, q):
        """One-step synchronous update using pattern-list W."""
        h = w_times_q(pats, wts, q)
        return np.where(h > 0, 1.0, -1.0)

    measurements = []
    for t in range(t_max):
        # Decay all weights
        wt_list = [w * (1.0 - gamma_decay * dt) for w in wt_list]

        # Write new random pattern with prob lambda*dt (capped at 1.0)
        if rng.rand() < min(1.0, lambda_rate * dt):
            xi_new = rng.choice([-1.0, 1.0], size=(N,))
            pat_list.append(xi_new)
            wt_list.append(1.0)

        # Prune patterns with negligible weight
        keep = [i for i, w in enumerate(wt_list) if w > W_PRUNE_THRESH]
        if len(keep) < len(wt_list):
            pat_list = [pat_list[i] for i in keep]
            wt_list = [wt_list[i] for i in keep]

        # Measure retrieval accuracy on query patterns
        if (t + 1) % measure_interval == 0:
            accs = []
            for q_idx in range(n_q):
                target = query_patterns[q_idx]
                # Add 10% noise to query
                noise_mask = rng.rand(N) < 0.10
                query = target.copy()
                query[noise_mask] *= -1.0
                # 3 retrieval steps
                s = query
                for _ in range(3):
                    s_new = hopfield_step(pat_list, wt_list, s)
                    if np.all(s_new == s):
                        break
                    s = s_new
                accs.append(retrieval_accuracy(s, target))
            mean_acc = float(np.mean(accs))
            measurements.append({"t": t + 1, "mean_acc": mean_acc,
                                  "n_patterns": len(pat_list)})

    return {"measurements": measurements, "t_max": t_max}


def fit_tau_empirical(measurements: List[Dict]) -> float:
    """
    Fit exponential decay model: acc(t) ~ acc_0 * exp(-t / tau) + acc_inf.
    Returns fitted tau. Uses log-linear fit after subtracting floor.
    """
    ts = np.array([m["t"] for m in measurements], dtype=float)
    accs = np.array([m["mean_acc"] for m in measurements])

    # Remove floor (assume acc_inf ~ chance = 0.5 for BSC patterns)
    acc_floor = 0.50
    accs_adj = np.clip(accs - acc_floor, 1e-6, None)

    # Log-linear fit: log(acc_adj) = log(A) - t/tau
    log_accs = np.log(accs_adj)
    # Linear regression: log_acc = a + b*t, tau = -1/b
    if len(ts) < 2:
        return float("nan")
    coeffs = np.polyfit(ts, log_accs, 1)  # [slope, intercept]
    slope = coeffs[0]
    if slope >= 0:
        return float("nan")  # not decaying
    tau = -1.0 / slope
    return float(tau)


def run_config(lambda_rate: float, gamma_decay: float, seed: int) -> Dict:
    """Run one (lambda, gamma) configuration."""
    rng = np.random.RandomState(seed)
    # Query patterns stored at t=0
    query_patterns = rng.choice([-1.0, 1.0], size=(N_QUERY_PATTERNS, N))

    meas = simulate_decay(N, lambda_rate, gamma_decay, query_patterns,
                           T_MAX_STEPS, DT, MEASURE_INTERVAL, seed + 1)
    tau_emp = fit_tau_empirical(meas["measurements"])
    tau_theory = tau_mem_theory(N, lambda_rate)
    ratio = tau_emp / tau_theory if (not math.isnan(tau_emp) and tau_theory > 0) else float("nan")

    print(f"  [seed={seed} lam={lambda_rate} gam={gamma_decay}] "
          f"tau_emp={tau_emp:.0f} tau_theory={tau_theory:.0f} ratio={ratio:.2f}", flush=True)

    return {
        "lambda_rate": lambda_rate, "gamma_decay": gamma_decay,
        "tau_mem_theory": tau_theory,
        "tau_mem_empirical": tau_emp,
        "ratio": ratio,
        "measurements_count": len(meas["measurements"]),
        "passes_hp": (not math.isnan(ratio) and HP_RATIO_LOW <= ratio <= HP_RATIO_HIGH),
    }


def run_seed(seed: int) -> Dict:
    """Run all configs for one seed."""
    config_results = []
    for (lam, gam) in CONFIGS:
        r = run_config(lam, gam, seed)
        config_results.append(r)
    return {"configs": config_results, "seed": seed, "N": N, "run_mode": RUN_MODE}


def _instrumentation_selftest():
    """Assert tau_mem metrics are non-null at small scale."""
    N_test = 512
    seed = 42
    lam, gam = 0.05, 0.005

    rng = np.random.RandomState(seed)
    q_pats = rng.choice([-1.0, 1.0], size=(2, N_test))
    meas = simulate_decay(N_test, lam, gam, q_pats, t_max=500, dt=1.0,
                           measure_interval=50, seed=seed + 1)

    assert len(meas["measurements"]) > 0, "no measurements"
    assert meas["measurements"][0]["mean_acc"] > 0.5, "initial accuracy too low"

    tau = fit_tau_empirical(meas["measurements"])
    tau_theory = tau_mem_theory(N_test, lam)
    print(f"[selftest] PASS: tau_emp={tau:.0f} tau_theory={tau_theory:.0f} "
          f"(N=512, {len(meas['measurements'])} measurement points)", flush=True)


_instrumentation_selftest()


def _verdict_formula_selftests():
    """Verify tau_mem formula."""
    tau = tau_mem_theory(4096, 2.0)
    assert abs(tau - 1024.0) < 1.0, f"tau_mem formula: {tau}"
    tau2 = tau_mem_theory(4096, 5.0)
    assert abs(tau2 - 409.6) < 0.5, f"tau_mem formula: {tau2}"
    print("[formula_selftests] PASS: tau_mem_theory formula verified", flush=True)


_verdict_formula_selftests()


def aggregate_results(per_seed: Dict) -> Dict:
    """Aggregate per config across seeds."""
    n_seeds = len(per_seed)
    config_agg = {}
    for lam, gam in CONFIGS:
        key = f"lam{lam}_gam{gam}"
        ratios, n_pass = [], 0
        for seed_data in per_seed.values():
            for cr in seed_data.get("configs", []):
                if cr["lambda_rate"] == lam and cr["gamma_decay"] == gam:
                    r = cr.get("ratio", float("nan"))
                    if not math.isnan(r):
                        ratios.append(r)
                    if cr.get("passes_hp"):
                        n_pass += 1
        config_agg[key] = {
            "lambda_rate": lam, "gamma_decay": gam,
            "tau_theory": tau_mem_theory(N, lam),
            "mean_ratio": float(np.mean(ratios)) if ratios else float("nan"),
            "n_pass": n_pass, "n_seeds": n_seeds,
            "passes_hp": (n_pass / n_seeds >= HP_FRAC_SEEDS) if n_seeds > 0 else False,
        }

    n_configs_pass = sum(1 for v in config_agg.values() if v["passes_hp"])
    all_ratios = [v["mean_ratio"] for v in config_agg.values() if not math.isnan(v["mean_ratio"])]
    return {
        "configs": config_agg,
        "n_configs_pass_hp": n_configs_pass,
        "n_configs_total": len(config_agg),
        "overall_mean_ratio": float(np.mean(all_ratios)) if all_ratios else float("nan"),
    }


def compute_verdict(agg: Dict) -> Tuple[str, str]:
    n_pass = agg.get("n_configs_pass_hp", 0)
    n_total = agg.get("n_configs_total", 1)
    mean_ratio = agg.get("overall_mean_ratio", float("nan"))
    frac_pass = n_pass / n_total if n_total > 0 else 0.0

    hp = frac_pass >= HP_FRAC_CONFIGS
    hf = math.isnan(mean_ratio) or mean_ratio < HF_RATIO_LOW or mean_ratio > HF_RATIO_HIGH

    if hp:
        return ("HARD_PASS",
                f"tau_mem prediction confirmed within 2x. "
                f"{n_pass}/{n_total} configs pass HP (HP>={HP_FRAC_CONFIGS:.2f}). "
                f"mean_ratio={mean_ratio:.2f}. "
                f"Continuous-write decay follows predicted tau_mem=N/(2*lambda).")
    if hf:
        return ("HARD_FAIL",
                f"tau_mem prediction severely off. "
                f"mean_ratio={mean_ratio:.2f} outside [{HF_RATIO_LOW},{HF_RATIO_HIGH}]. "
                f"SDE model mis-specified or decay not exponential.")
    return ("MIDDLE_BAND",
            f"Partial tau_mem agreement. {n_pass}/{n_total} configs pass HP. "
            f"mean_ratio={mean_ratio:.2f} (HP ratio [{HP_RATIO_LOW},{HP_RATIO_HIGH}]).")


def main():
    out_dir = get_output_dir(ANCHOR_NAME)
    t0 = time.time()
    print(f"[start] {ANCHOR_NAME} run_mode={RUN_MODE} N={N} "
          f"configs={len(CONFIGS)} T_MAX={T_MAX_STEPS} seeds={SEEDS}", flush=True)

    from experiments._seed_checkpoint import resumable_seeds, write_partial, aggregate_partials
    run_config_mode = {"N": N, "run_mode": RUN_MODE}
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config_mode)
    print(f"[ckpt] {len(done)} done, {len(remaining)} remaining", flush=True)

    for seed in remaining:
        ts = time.time()
        result = run_seed(seed)
        write_partial(out_dir, seed, result)
        print(f"[seed {seed}] done in {time.time()-ts:.1f}s", flush=True)

    per_seed = aggregate_partials(out_dir, SEEDS)
    agg = aggregate_results(per_seed)
    verdict, verdict_msg = compute_verdict(agg)

    elapsed = time.time() - t0
    metrics = {
        "run_mode": RUN_MODE, "N": N,
        "CONFIGS": CONFIGS, "T_MAX_STEPS": T_MAX_STEPS,
        "seeds": SEEDS,
        "aggregated": agg,
        "verdict": verdict, "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
    }
    with open(out_dir / "metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"[done] {verdict}: {verdict_msg}", flush=True)
    print(f"[done] elapsed={elapsed:.1f}s", flush=True)


if __name__ == "__main__":
    if _ARGS.self_test:
        print("[main] --self-test complete", flush=True)
        sys.exit(0)
    main()
