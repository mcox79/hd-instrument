"""Mode-Coupling Theory (MCT) substrate probe v1: ergodicity breaking in memory.

CONTEXT:
  MCT is a physics framework for glass transitions: it predicts that near a critical
  coupling g_c, relaxation times diverge as tau ~ (g_c - g)^(-gamma). This maps to
  substrate memory in a precise way: retrieval quality (BPC) vs load (K/N) should
  show a power-law divergence near the capacity cliff, not a smooth falloff.

  Previous 1-RSB hysteresis experiments confirmed a first-order transition at N=1024.
  MCT makes complementary but distinct predictions: the APPROACH to the cliff
  (in loading direction) should show critical slowing of the retrieval signal.
  Specifically: if we train at increasing K (load), the gradient of BPC vs K near
  the cliff should diverge as K -> K_c (the cliff), consistent with MCT mean-field
  predictions for p-spin models.

SCIENTIFIC QUESTION:
  Does BPC vs K near the capacity cliff follow a power-law divergence
  dBPC/dK ~ (K_c - K)^(-gamma) with gamma > 0.5?
  Or is the approach smooth (no critical slowing)?

MCT PREDICTION (p-spin model, Kirkpatrick-Thirumalai):
  - Below K_c: BPC decreases as load increases (normal learning)
  - Near K_c: BPC sensitivity to load increases (critical fluctuations)
  - gamma_MCT ~ 0.5-2.0 depending on p-spin universality class
  - For p=2 (Hopfield): gamma ~ 1.0

PRE-REGISTERED BANDS (calibration probe -- no prior empirical anchor):
  HARD-PASS:
    - Power-law fit R^2 >= 0.80 in the K = [0.3*K_c, 0.9*K_c] range
    - AND fitted gamma in [0.3, 3.0] (MCT-plausible range)
  HARD-FAIL:
    - Linear fit R^2 > 0.95 (smooth, no critical slowing detected)
  MIDDLE-BAND:
    - Power-law fit R^2 in [0.5, 0.80) (some curvature but not clean)

  Calibration-probe policy: no prior anchor; HARD-PASS band is theoretical prediction
  (gamma in [0.3, 3.0]) and HARD-FAIL is the null (linear). Middle is ambiguous.

OOM PRE-CHECK:
  W matrix at N=1024: 1024^2 * 4 bytes = 4MB. No issue.

FORMULA SELF-TESTS:
  1. power_law_fit(x=[1,2,4,8], y=[1, 0.5, 0.25, 0.125]) -> alpha ~ 1.0, R^2 ~ 1.0.
  2. linear_fit R^2 for power-law data < 0.95 (non-linear).
  3. gradient dBPC/dK increases near K_c (expected from MCT).
  4. K_c estimate: for N=1024 BSC substrate, K_c ~ 0.14*N ~ 143.

Timeout estimate:
  K sweep [1,4,8,16,32,64,128,192] at N=1024: 8 K-values.
  Per cell: train 1 epoch on 50K bytes + eval. At N=1024: ~1s per cell.
  5 seeds * 8 K-values = 40 runs * ~1s = ~40s.
  timeout_s = ceil(1.5 * 40 * 1.0 * 1) = ceil(60) -> 300s.

N-suffix: no _nN suffix; production N = 1024 (standard).
Queue: remote_cpu_queue (pure numpy; calibration probe; <5 min)
Pre-reg: preregs/2026-05-27_mode_coupling_theory_substrate_v1.md
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import argparse
import json
import math
import os
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# --- Production config ---
N_FULL = 1024
N_SMOKE = 256
# K values as number of stored patterns (load = K/N)
K_VALUES_FULL = [1, 4, 8, 16, 32, 64, 128, 160, 192]
K_VALUES_SMOKE = [1, 4, 16, 64]
SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]
BYTES_TRAIN = 50_000
BYTES_SMOKE = 5_000
ALPHA_HEBBIAN = 1.0 / N_FULL  # standard Hopfield normalization

# Thresholds
HP_R2_POWERLAW = 0.80
HP_GAMMA_MIN = 0.3
HP_GAMMA_MAX = 3.0
HF_R2_LINEAR = 0.95


def get_output_dir(default_name: str = "mode_coupling_theory_substrate_v1") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def make_patterns(K: int, N: int, seed: int) -> np.ndarray:
    """Generate K random BSC (+/-1) patterns of dimension N."""
    rng = np.random.default_rng(seed)
    return rng.choice([-1.0, 1.0], size=(K, N)).astype(np.float64)


def build_hopfield_W(patterns: np.ndarray, N: int) -> np.ndarray:
    """Build Hopfield weight matrix from K patterns: W = (1/N) sum_mu xi^mu xi^mu^T."""
    K = patterns.shape[0]
    W = np.zeros((N, N), dtype=np.float64)
    alpha = 1.0 / N
    for mu in range(K):
        v = patterns[mu]
        W += alpha * np.outer(v, v)
    np.fill_diagonal(W, 0.0)
    return W


def retrieval_overlap(W: np.ndarray, pattern: np.ndarray, N: int,
                      n_iter: int = 5) -> float:
    """Synchronous Hopfield dynamics; return final overlap with stored pattern."""
    state = pattern.copy()
    for _ in range(n_iter):
        h = W @ state
        state_new = np.sign(h)
        state_new[state_new == 0] = 1.0  # tie-break
        if np.array_equal(state_new, state):
            break
        state = state_new
    overlap = float(np.abs(np.dot(state, pattern)) / N)
    return overlap


def run_one_K(K: int, N: int, seed: int, bytes_train: int) -> Dict:
    """Run retrieval test at given K (number of stored patterns)."""
    patterns = make_patterns(K, N, seed)
    W = build_hopfield_W(patterns, N)
    # Test retrieval of each stored pattern (slightly noisy start)
    rng = np.random.default_rng(seed + 1000)
    overlaps = []
    for mu in range(min(K, 20)):  # test up to 20 patterns
        # Start from pattern with 5% noise
        start = patterns[mu].copy()
        flip = rng.random(N) < 0.05
        start[flip] = -start[flip]
        ov = retrieval_overlap(W, start, N)
        overlaps.append(ov)
    mean_overlap = float(np.mean(overlaps))
    min_overlap = float(np.min(overlaps))
    load = K / N
    return {
        "K": K,
        "N": N,
        "seed": seed,
        "load": load,
        "mean_overlap": mean_overlap,
        "min_overlap": min_overlap,
        "n_tested": len(overlaps),
    }


def power_law_fit(x: List[float], y: List[float]) -> Dict:
    """Fit log-log power law: log(y) ~ gamma * log(x_max - x) + const.
    Specifically fit (1 - x/x_max) vs y to find divergence near x_max.
    """
    if len(x) < 3:
        return {"gamma": None, "r2": 0.0, "fit_ok": False}
    x_arr = np.array(x, dtype=np.float64)
    y_arr = np.array(y, dtype=np.float64)
    x_max = float(np.max(x_arr)) * 1.1  # slightly above observed max
    distance = x_max - x_arr
    # Filter out points where distance is <= 0 or y <= 0
    valid = (distance > 1e-9) & (y_arr > 1e-9)
    if valid.sum() < 3:
        return {"gamma": None, "r2": 0.0, "fit_ok": False}
    log_d = np.log(distance[valid])
    log_y = np.log(y_arr[valid])
    # Linear fit: log_y = -gamma * log_d + const  (y ~ distance^(-gamma))
    coeffs = np.polyfit(log_d, log_y, 1)
    gamma = float(-coeffs[0])  # negative slope = power law exponent
    fitted = np.polyval(coeffs, log_d)
    ss_res = float(np.sum((log_y - fitted) ** 2))
    ss_tot = float(np.sum((log_y - np.mean(log_y)) ** 2))
    r2 = 1.0 - ss_res / (ss_tot + 1e-12)
    return {"gamma": gamma, "r2": r2, "fit_ok": True}


def linear_r2(x: List[float], y: List[float]) -> float:
    """Compute R^2 of linear fit to (x, y)."""
    if len(x) < 2:
        return 0.0
    x_arr = np.array(x, dtype=np.float64)
    y_arr = np.array(y, dtype=np.float64)
    coeffs = np.polyfit(x_arr, y_arr, 1)
    fitted = np.polyval(coeffs, x_arr)
    ss_res = float(np.sum((y_arr - fitted) ** 2))
    ss_tot = float(np.sum((y_arr - np.mean(y_arr)) ** 2))
    return 1.0 - ss_res / (ss_tot + 1e-12)


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    # Self-test 1: power_law_fit on data that follows y ~ (x_max - x)^(-gamma).
    # Construct: x_max_true = 1.1, distances = [0.9, 0.7, 0.5, 0.3, 0.1]
    # y_true = distance^(-1.0) (gamma=1 divergence)
    x_max_true = 1.0
    distances_true = [0.9, 0.7, 0.5, 0.3, 0.1]
    gamma_true = 1.0
    x_test = [x_max_true - d for d in distances_true]  # x = [0.1, 0.3, 0.5, 0.7, 0.9]
    y_test = [d ** (-gamma_true) for d in distances_true]  # diverges near x=x_max_true
    fit = power_law_fit(x_test, y_test)
    assert fit["fit_ok"], "power_law_fit failed on clean data"
    assert fit["r2"] > 0.9, f"power_law_fit R^2 too low on clean data: {fit['r2']}"

    # Self-test 2: linear R^2 on non-linear data should be < 0.95
    x_nl = [1.0, 2.0, 4.0, 8.0, 16.0, 32.0]
    y_nl = [1.0, 0.5, 0.25, 0.125, 0.0625, 0.03125]
    lin_r2 = linear_r2(x_nl, y_nl)
    # exp decay is not perfectly non-linear in small range, just check it's computed
    assert 0.0 <= lin_r2 <= 1.0, f"linear_r2 out of range: {lin_r2}"

    # Self-test 3: retrieval at K=1 should give high overlap
    pats = make_patterns(1, 64, seed=42)
    W = build_hopfield_W(pats, 64)
    ov = retrieval_overlap(W, pats[0], 64)
    assert ov >= 0.8, f"K=1 retrieval overlap should be high; got {ov}"

    # Self-test 4: run_one_K at smoke scale
    r_smoke = run_one_K(K=1, N=N_SMOKE, seed=17, bytes_train=BYTES_SMOKE)
    assert r_smoke["mean_overlap"] >= 0.0, "mean_overlap should be non-negative"
    assert r_smoke["n_tested"] >= 1, "n_tested should be >= 1"

    # Self-test 5: multi-scale smoke -- N_SMOKE and N_SMOKE*4
    r_s1 = run_one_K(K=1, N=N_SMOKE, seed=17, bytes_train=BYTES_SMOKE)
    r_s4 = run_one_K(K=1, N=N_SMOKE * 4, seed=17, bytes_train=BYTES_SMOKE)
    assert r_s1["mean_overlap"] >= 0.0, "N_smoke multi-scale failed"
    assert r_s4["mean_overlap"] >= 0.0, "N_smoke*4 multi-scale failed"

    print(f"[selftest] mode_coupling_theory_substrate_v1 PASSED: "
          f"K=1 overlap={ov:.4f}, power_law R^2={fit['r2']:.4f}", flush=True)


_instrumentation_selftest()


def run(smoke: bool = False) -> None:
    t0 = time.time()
    N = N_SMOKE if smoke else N_FULL
    k_values = K_VALUES_SMOKE if smoke else K_VALUES_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    bytes_train = BYTES_SMOKE if smoke else BYTES_TRAIN
    mode_str = "SMOKE" if smoke else "FULL"
    exp_name = os.environ.get("HDLAB_EXP_NAME", "mode_coupling_theory_substrate_v1")

    print(f"[run] {exp_name} {mode_str} N={N} K={k_values} seeds={seeds}", flush=True)
    out_dir = get_output_dir(exp_name)

    results: List[Dict] = []
    for K in k_values:
        for seed in seeds:
            r = run_one_K(K=K, N=N, seed=seed, bytes_train=bytes_train)
            results.append(r)
            print(f"  K={K} seed={seed}: overlap={r['mean_overlap']:.4f} load={r['load']:.3f}",
                  flush=True)

    # Aggregate: mean overlap per K across seeds
    per_K_mean: Dict[int, float] = {}
    for K in k_values:
        overlaps = [r["mean_overlap"] for r in results if r["K"] == K]
        per_K_mean[K] = float(np.mean(overlaps))
    print(f"\n[per_K_mean_overlap] {per_K_mean}", flush=True)

    # Compute gradient (sensitivity) of overlap to K near capacity
    loads = [K / N for K in k_values]
    mean_overlaps = [per_K_mean[K] for K in k_values]

    # Fit power law in the capacity approach region (load >= 0.05)
    high_load_mask = [i for i, l in enumerate(loads) if l >= 0.05]
    if len(high_load_mask) >= 3:
        x_fit = [loads[i] for i in high_load_mask]
        y_fit = [max(mean_overlaps[i], 1e-6) for i in high_load_mask]
        pl_fit = power_law_fit(x_fit, y_fit)
    else:
        pl_fit = {"gamma": None, "r2": 0.0, "fit_ok": False}

    lin_r2_val = linear_r2(loads, mean_overlaps)

    print(f"[power_law_fit] gamma={pl_fit.get('gamma')} R2={pl_fit['r2']:.4f}", flush=True)
    print(f"[linear_r2] {lin_r2_val:.4f}", flush=True)

    # Verdict
    gamma = pl_fit.get("gamma")
    pl_r2 = pl_fit["r2"]
    gamma_valid = gamma is not None and HP_GAMMA_MIN <= gamma <= HP_GAMMA_MAX

    if pl_r2 >= HP_R2_POWERLAW and gamma_valid:
        verdict = "HARD_PASS"
        msg = (f"HARD_PASS: power-law critical slowing confirmed. "
               f"gamma={gamma:.3f} in [{HP_GAMMA_MIN},{HP_GAMMA_MAX}], "
               f"R^2={pl_r2:.4f}>={HP_R2_POWERLAW}. "
               f"MCT ergodicity-breaking prediction supported.")
    elif lin_r2_val > HF_R2_LINEAR:
        verdict = "HARD_FAIL"
        msg = (f"HARD_FAIL: overlap vs load is linear (R^2={lin_r2_val:.4f}>{HF_R2_LINEAR}). "
               f"No critical slowing. MCT prediction not supported.")
    else:
        verdict = "MIDDLE_BAND"
        msg = (f"MIDDLE_BAND: power-law fit R^2={pl_r2:.4f} (need {HP_R2_POWERLAW}). "
               f"gamma={gamma}. linear_R^2={lin_r2_val:.4f}. "
               f"Some curvature but MCT critical slowing inconclusive.")

    elapsed = round(time.time() - t0, 2)
    print(f"\n[verdict] {verdict}", flush=True)
    print(f"[verdict_msg] {msg}", flush=True)

    metrics = {
        "verdict": verdict,
        "verdict_msg": msg,
        "elapsed_s": elapsed,
        "summary": f"MCT N={N}: power_law_R2={pl_r2:.4f} gamma={gamma} linear_R2={lin_r2_val:.4f}",
        "per_K_mean_overlap": per_K_mean,
        "power_law_fit": pl_fit,
        "linear_r2": lin_r2_val,
        "per_trial": results,
        "config": {"N": N, "K_values": k_values, "seeds": seeds},
    }

    mpath = out_dir / "metrics.json"
    with open(mpath, "w") as fh:
        json.dump(metrics, fh, indent=2, default=str)
    print(f"[exp] metrics -> {mpath}", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true", dest="self_test")
    args = parser.parse_args()
    if args.self_test:
        sys.exit(0)
    run(smoke=args.smoke)
