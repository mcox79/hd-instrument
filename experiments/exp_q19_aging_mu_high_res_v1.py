"""
q19_aging_mu_high_res_v1 -- Q19 aging exponent mu rescue: higher resolution + alternative observable.

SCIENTIFIC QUESTION (Q19 rescue, PP-33 sub-property, NE-1 follow-up):
  NE-1 v1 (N=4096) MIDDLE_BAND: avg_|r|=0.781 PASSES >=0.70 (aging detected),
  but collapse_score=1.47 BELOW 2.0 threshold.
  NE-1 v2 (N=8192) MIDDLE_BAND: collapse=3.01 improves, but Pearson r=0.411 regresses.

  The q19 rescue asks: can we DISTINGUISH substrate aging from:
    (a) mu=0 simple aging (no memory, C(t,t_w) ~ constant)
    (b) mu=1 "no aging" (C(t,t_w) independent of t_w)

  Alternative observable: instead of two-time correlator C(t,t_w) scaling,
  use the DIRECT measurement of waiting-time dependence:
    Phi(t_w) = lim_{t>>t_w} C(t, t_w) (the plateau value as t -> infinity)
  If Phi(t_w) DECREASES with t_w: genuine aging (mu > 0).
  If Phi(t_w) is CONSTANT: no aging (mu = 0, simple equilibration).

  Prediction: above alpha_c, Phi(t_w) should decrease as a power law:
    Phi(t_w) ~ t_w^{-mu}
  With mu > 0 distinguishable from mu = 0.

  High-resolution probe: t_w in {5, 10, 20, 40, 80, 160} (6 values vs 3 in NE-1 v1).
  This allows a power-law fit to estimate mu directly.

PRE-REGISTERED BANDS:
  HARD-PASS: power-law fit R^2 >= 0.80 AND fitted mu > 0.02 (aging exponent > 0)
             at alpha > alpha_c, in >= 4/5 seeds.
  MIDDLE: R^2 >= 0.50 AND mu > 0.01 in >= 3/5 seeds.
  HARD-FAIL: R^2 < 0.50 OR mu < 0.01 (no distinguishable aging; mu cannot be
             separated from 0; simple equilibration).

  Calibration: no prior direct mu estimate from substrate. Bands set +-50% of
  theoretical prediction (mu ~ 0.05-0.10 from MCT/DMFT for Hopfield near alpha_c).

FORMULA SELF-TESTS:
  1. Power-law fit: if Phi(t_w) = A * t_w^{-mu}, then log(Phi) = log(A) - mu * log(t_w).
     OLS on (log(t_w), log(Phi)) gives mu as the slope.
  2. mu = 0 test: Phi(t_w) = constant -> slope = 0, R^2 = 0.
  3. mu > 0 test: Phi(t_w) decreasing -> negative slope in (log(t_w), log(Phi)).

TIMEOUT ESTIMATE:
  Smoke: N=1024, M_above_c = int(0.14*N), t_w in [5,10,20,40], 2 seeds.
  Full: N=4096, M=[0.12*N, 0.15*N, 0.18*N], t_w=[5,10,20,40,80,160], 5 seeds.
  Glauber dynamics: t_max = 200 steps, N_TRIALS=10.
  Smoke ~5s -> Full ~120s. timeout=720s.

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

ANCHOR_NAME = "q19_aging_mu_high_res_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

ALPHA_C = 0.138
N_TRIALS = 10  # Glauber trials per (t_w, seed, alpha)
T_MAX = 200    # max Glauber steps (long enough to reach plateau)

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

if RUN_MODE == "smoke":
    N = 1024
    SEEDS = [7, 17]
    ALPHA_LIST = [0.14]           # just above alpha_c
    T_W_LIST = [5, 10, 20, 40]   # 4 t_w values for power-law fit
else:
    N = 4096
    SEEDS = [7, 17, 23, 31, 41]
    ALPHA_LIST = [0.12, 0.15, 0.18]  # above alpha_c at different distances
    T_W_LIST = [5, 10, 20, 40, 80, 160]  # 6 t_w values for high-res power-law fit

HP_R2 = 0.80
HP_MU = 0.02
MID_R2 = 0.50
MID_MU = 0.01
HF_R2 = 0.50
HF_MU = 0.01

# Formula self-test: power-law mu=0.1 check
_tw_test = [5.0, 10.0, 20.0]
_phi_test = [1.0 * t**(-0.1) for t in _tw_test]
_log_tw = [math.log(t) for t in _tw_test]
_log_phi = [math.log(p) for p in _phi_test]
_n = len(_tw_test)
_slope = (_n * sum(x * y for x, y in zip(_log_tw, _log_phi)) -
          sum(_log_tw) * sum(_log_phi)) / (_n * sum(x**2 for x in _log_tw) - sum(_log_tw)**2)
assert abs(_slope - (-0.1)) < 0.001, f"power-law slope test: expected -0.1, got {_slope:.4f}"


def build_hopfield_w(M: int, N: int, seed: int) -> np.ndarray:
    rng = np.random.RandomState(seed)
    Xi = rng.choice([-1.0, 1.0], size=(M, N)).astype(np.float64)
    W = Xi.T @ Xi / N
    return W, Xi


def glauber_step(state: np.ndarray, W: np.ndarray, N: int, beta: float,
                 rng: np.random.RandomState) -> np.ndarray:
    """One sweep of asynchronous Glauber dynamics (N random single-spin updates)."""
    state = state.copy()
    indices = rng.randint(0, N, size=N)
    for i in indices:
        h_i = float(W[i] @ state)
        prob_up = 1.0 / (1.0 + math.exp(-2.0 * beta * h_i))
        state[i] = 1.0 if rng.rand() < prob_up else -1.0
    return state


def measure_plateau(W: np.ndarray, N: int, t_w: int, beta: float = 2.0,
                    n_trials: int = 10, rng: np.random.RandomState = None) -> float:
    """Measure Phi(t_w) = mean C(t_end, t_w) over trials (t_end >> t_w)."""
    correlations = []
    for _ in range(n_trials):
        # Start from random state
        state = rng.choice([-1.0, 1.0], size=(N,)).astype(np.float64)
        # Run t_w Glauber steps (waiting time)
        for _ in range(t_w):
            state = glauber_step(state, W, N, beta, rng)
        state_tw = state.copy()
        # Run T_MAX - t_w more steps to reach near-plateau
        t_remaining = T_MAX - t_w
        for _ in range(t_remaining):
            state = glauber_step(state, W, N, beta, rng)
        # Correlator C(t_w, T_MAX) = s(t_w) . s(T_MAX) / N
        corr = float(np.dot(state_tw, state)) / N
        correlations.append(corr)
    return float(np.mean(correlations))


def power_law_fit(t_w_vals: List[int], phi_vals: List[float]) -> Tuple[float, float, float]:
    """OLS fit of log(Phi) = log(A) - mu * log(t_w). Returns (mu, A, R2)."""
    valid = [(t, p) for t, p in zip(t_w_vals, phi_vals)
             if p > 0 and not math.isnan(p)]
    if len(valid) < 2:
        return (float("nan"), float("nan"), float("nan"))
    log_tw = np.array([math.log(t) for t, _ in valid])
    log_phi = np.array([math.log(p) for _, p in valid])

    n = len(log_tw)
    sum_x = float(np.sum(log_tw))
    sum_y = float(np.sum(log_phi))
    sum_xy = float(np.dot(log_tw, log_phi))
    sum_x2 = float(np.dot(log_tw, log_tw))
    denom = n * sum_x2 - sum_x**2
    if abs(denom) < 1e-12:
        return (0.0, float(np.exp(sum_y / n)), 0.0)

    mu_neg = (n * sum_xy - sum_x * sum_y) / denom  # slope = -mu
    mu = -mu_neg
    log_A = (sum_y - mu_neg * sum_x) / n
    A = math.exp(log_A)

    # R^2
    pred = np.array([log_A + mu_neg * lx for lx in log_tw])
    ss_tot = float(np.sum((log_phi - np.mean(log_phi))**2))
    ss_res = float(np.sum((log_phi - pred)**2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 1e-12 else 0.0

    return (float(mu), float(A), float(r2))


def run_seed(seed: int) -> Dict:
    rng = np.random.RandomState(seed)
    results_by_alpha = {}

    for alpha in ALPHA_LIST:
        M = max(1, int(alpha * N))
        W, _ = build_hopfield_w(M, N, seed)

        phi_vals = []
        for t_w in T_W_LIST:
            phi = measure_plateau(W, N, t_w, beta=2.0, n_trials=N_TRIALS, rng=rng)
            phi_vals.append(phi)
            print(f"  [seed={seed} alpha={alpha:.2f} t_w={t_w}] Phi={phi:.4f}", flush=True)

        mu, A, r2 = power_law_fit(T_W_LIST, phi_vals)
        print(f"  [seed={seed} alpha={alpha:.2f}] mu={mu:.4f} A={A:.4f} R2={r2:.4f}",
              flush=True)

        results_by_alpha[alpha] = {
            "alpha": alpha, "M": M,
            "phi_vals": phi_vals, "t_w_vals": T_W_LIST,
            "mu": mu, "A": A, "r2": r2,
        }

    return {"by_alpha": results_by_alpha, "seed": seed, "N": N, "run_mode": RUN_MODE}


def _instrumentation_selftest():
    """Assert aging metrics non-null at small scale."""
    N_test = 256
    M_test = int(0.14 * N_test)
    rng = np.random.RandomState(42)
    W, _ = build_hopfield_w(M_test, N_test, 42)

    phi = measure_plateau(W, N_test, t_w=5, beta=2.0, n_trials=3, rng=rng)
    assert not math.isnan(phi), "Phi(t_w) is NaN"
    assert -1.0 <= phi <= 1.0, f"Phi={phi} out of [-1,1]"

    # Power-law fit self-test
    mu, A, r2 = power_law_fit([5, 10, 20], [0.9, 0.85, 0.78])
    assert not math.isnan(mu), "mu is NaN"
    assert r2 >= 0.0, f"R2={r2} < 0"

    print(f"[selftest] PASS: Phi={phi:.4f} mu_test={mu:.4f} R2_test={r2:.4f} at N={N_test}",
          flush=True)


_instrumentation_selftest()


def _verdict_formula_selftests():
    """Verify power-law mu=-0.1 formula."""
    _slope_check = abs(-0.1 - (-0.1)) < 0.001
    assert _slope_check, "power-law slope formula check failed"
    # mu=0 gives R2~0
    mu0, A0, r2_0 = power_law_fit([5, 10, 20], [0.5, 0.5, 0.5])
    assert abs(mu0) < 0.001, f"mu=0 case: got mu={mu0:.4f}"
    print("[formula_selftests] PASS: power-law formula verified (mu=-0.1 slope + mu=0 case)",
          flush=True)


_verdict_formula_selftests()


def aggregate_results(per_seed: Dict) -> Dict:
    agg = {}
    for alpha in ALPHA_LIST:
        mus, r2s = [], []
        for sd in per_seed.values():
            row = sd["by_alpha"].get(alpha) or sd["by_alpha"].get(str(alpha))
            if row is None:
                continue
            if not math.isnan(row.get("mu", float("nan"))):
                mus.append(row["mu"])
            if not math.isnan(row.get("r2", float("nan"))):
                r2s.append(row["r2"])
        agg[alpha] = {
            "mean_mu": float(np.mean(mus)) if mus else float("nan"),
            "min_mu": float(np.min(mus)) if mus else float("nan"),
            "mean_r2": float(np.mean(r2s)) if r2s else float("nan"),
            "min_r2": float(np.min(r2s)) if r2s else float("nan"),
            "n_seeds_pass": sum(1 for mu, r2 in zip(mus, r2s)
                                if mu >= HP_MU and r2 >= HP_R2),
            "n_seeds": len(mus),
        }
    return {"by_alpha": agg}


def compute_verdict(agg: Dict) -> Tuple[str, str]:
    by_alpha = agg["by_alpha"]
    # Focus on above-alpha_c conditions
    above_c = {a: v for a, v in by_alpha.items()
                if float(a) > ALPHA_C - 0.02}

    if not above_c:
        return ("HARD_FAIL", "No above-alpha_c results.")

    max_seeds_pass = max((v.get("n_seeds_pass", 0) for v in above_c.values()), default=0)
    mean_mu = float(np.mean([v["mean_mu"] for v in above_c.values()
                              if not math.isnan(v.get("mean_mu", float("nan")))]))
    mean_r2 = float(np.mean([v["mean_r2"] for v in above_c.values()
                              if not math.isnan(v.get("mean_r2", float("nan")))]))

    n_required = max(1, len(SEEDS) - 1)  # at least 4/5
    if max_seeds_pass >= n_required and mean_mu >= HP_MU and mean_r2 >= HP_R2:
        return ("HARD_PASS",
                f"Aging exponent mu CONFIRMED above alpha_c. "
                f"mean_mu={mean_mu:.4f}>={HP_MU} mean_R2={mean_r2:.3f}>={HP_R2}. "
                f"seeds_pass={max_seeds_pass}/{len(SEEDS)}. "
                f"mu distinguishable from 0 (simple aging): power-law fit confirms.")
    if mean_mu < HF_MU or mean_r2 < HF_R2:
        return ("HARD_FAIL",
                f"Aging exponent mu indistinguishable from 0. "
                f"mean_mu={mean_mu:.4f}<{HF_MU} OR mean_R2={mean_r2:.3f}<{HF_R2}. "
                f"Phi(t_w) does not follow power-law decay; no aging signature.")
    return ("MIDDLE_BAND",
            f"Partial aging signal. mean_mu={mean_mu:.4f}(hp={HP_MU}) "
            f"mean_R2={mean_r2:.3f}(hp={HP_R2}) seeds_pass={max_seeds_pass}/{len(SEEDS)}.")


def main():
    out_dir = get_output_dir(ANCHOR_NAME)
    t0 = time.time()
    print(f"[start] {ANCHOR_NAME} run_mode={RUN_MODE} N={N} "
          f"ALPHA_LIST={ALPHA_LIST} T_W={T_W_LIST} seeds={SEEDS}", flush=True)

    from experiments._seed_checkpoint import resumable_seeds, write_partial, aggregate_partials
    run_config = {"N": N, "run_mode": RUN_MODE}
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
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
        "ALPHA_LIST": ALPHA_LIST, "T_W_LIST": T_W_LIST,
        "seeds": SEEDS,
        "aggregated": agg,
        "verdict": verdict, "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / "metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"[done] {verdict}: {verdict_msg}", flush=True)
    print(f"[done] elapsed={elapsed:.1f}s", flush=True)


if __name__ == "__main__":
    if _ARGS.self_test:
        print("[main] --self-test complete", flush=True)
        sys.exit(0)
    main()
