"""
q_c2_mp_hc_v1_n4096 -- Q-C2 Marchenko-Pastur HC at N=4096.

Resolves v323 smoke FAIL by using v324-confirmed free-Poisson null distribution.
Spectral-audit production readiness test.

SCIENTIFIC QUESTION (Q-C2):
  Does the Hopfield weight matrix W at N=4096 show spectral statistics consistent
  with Marchenko-Pastur (free-Poisson) null, and is the bulk-edge Z-score within
  +-3 sigma_TW of the free-Poisson predicted edge?

  v323 smoke FAIL analysis: the null distribution was incorrect (used GOE/Wigner
  instead of free-Poisson). v324 confirmed: kappa_n(W) = alpha (free-Poisson identity
  for ALL free cumulants). The correct null is Marchenko-Pastur with parameter alpha = M/N.

  v2 design (this script): use v324-confirmed free-Poisson bulk edge as the null.
  Compute Z_clean = (lambda_max - lambda_MP_edge) / sigma_TW.
  HP: Z_clean within +-3*sigma_TW of free-Poisson predicted edge.

PRE-REGISTERED BANDS:
  HARD-PASS: Z_clean in [-3.0, 3.0] (bulk edge consistent with free-Poisson null).
  MIDDLE: Z_clean in [-5.0, 5.0] (marginal consistency).
  HARD-FAIL: |Z_clean| > 5.0 (bulk edge far from free-Poisson; spectral anomaly present).

  The free-Poisson edge: lambda_MP_plus = sigma^2 * (1 + sqrt(alpha))^2
  where sigma^2 = 1/N for BSC +-1 patterns.
  Tracy-Widom width: sigma_TW ~ N^(-2/3) * lambda_MP_plus.

  Calibration: v323 was FAIL but on wrong null. v324 fixes null. bands set per
  free-Poisson theory + +-50% for first clean measurement.

FORMULA SELF-TESTS:
  1. MP upper edge: lambda_plus(alpha, sigma^2) = sigma^2 * (1 + sqrt(alpha))^2.
     At alpha=0.1, sigma^2=1: lambda_plus = (1 + sqrt(0.1))^2 ~ 1.725.
  2. sigma^2 for BSC Hopfield = 1/N (since patterns are normalized; W = Xi^T Xi / N,
     so eigenvalue scale is 1). At N=4096, M=409 (alpha=0.1):
     lambda_plus ~ (1 + sqrt(0.1))^2 ~ 1.725.
  3. Tracy-Widom: sigma_TW = N^(-2/3) * lambda_plus.
     At N=4096: sigma_TW = 4096^(-2/3) * 1.725 ~ 0.0265.
  4. Z_clean = (lambda_max - lambda_plus) / sigma_TW.

PROT-018: anchor name has _n4096; N MUST = 4096.
PROT-021: run_config includes N, M, run_mode.
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
from typing import Dict, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import get_output_dir, resumable_seeds, write_partial, aggregate_partials

ANCHOR_NAME = "q_c2_mp_hc_v1_n4096"

# PROT-018: anchor has _n4096 -> N must = 4096
_N_SUFFIX = 4096
N = 4096
assert N == _N_SUFFIX, f"PROT-018: anchor _n{_N_SUFFIX} but N={N}"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    ALPHA_LIST = [0.1, 0.3]
    USE_POWER_ITER = True    # cheap eigenvalue estimate
else:
    SEEDS = [7, 17, 23, 31, 41]
    ALPHA_LIST = [0.05, 0.1, 0.2, 0.3, 0.5]
    USE_POWER_ITER = False   # full eigendecomposition

# Pre-reg thresholds
HP_Z_LO = -3.0
HP_Z_HI = 3.0
MID_Z_LO = -5.0
MID_Z_HI = 5.0
HF_Z_ABS = 5.0

# Formula self-tests
def mp_upper_edge(alpha: float, sigma2: float = 1.0) -> float:
    """Marchenko-Pastur upper edge: sigma^2 * (1 + sqrt(alpha))^2."""
    return sigma2 * (1.0 + math.sqrt(alpha)) ** 2

def tw_sigma(N: int, lambda_plus: float) -> float:
    """Tracy-Widom width estimate: N^(-2/3) * lambda_plus."""
    return (N ** (-2.0/3.0)) * lambda_plus

# Self-test numerical check
_edge_test = mp_upper_edge(0.1, 1.0)
assert abs(_edge_test - 1.725) < 0.01, f"MP edge selftest: {_edge_test:.4f}"
_tw_test = tw_sigma(4096, 1.725)
# sigma_TW(N=4096) = 4096^(-2/3) * 1.725 = (2^12)^(-2/3) * 1.725 = 2^(-8) * 1.725 ~ 0.00674
# Correct expected: ~0.0067 (not 0.0265 which was the N=1024 value)
assert 0.003 < _tw_test < 0.015, f"TW selftest: {_tw_test:.5f} out of expected (0.003, 0.015)"
print(f"[formula_selftest] MP edge(alpha=0.1)={_edge_test:.4f}, "
      f"sigma_TW(N=4096)={_tw_test:.5f} OK", flush=True)


def compute_lambda_max_power(W: np.ndarray, n_iter: int = 100, seed: int = 0) -> float:
    """Power iteration for largest eigenvalue magnitude."""
    rng = np.random.RandomState(seed)
    v = rng.randn(W.shape[0])
    v /= np.linalg.norm(v)
    for _ in range(n_iter):
        v = W @ v
        nrm = float(np.linalg.norm(v))
        if nrm < 1e-15:
            return 0.0
        v /= nrm
    # Rayleigh quotient
    return float(np.dot(v, W @ v))


def compute_lambda_max_exact(W: np.ndarray) -> float:
    """Full eigendecomposition. Symmetric W."""
    eigvals = np.linalg.eigvalsh(W)
    return float(np.max(eigvals))


def run_seed(seed: int) -> Dict:
    results = {}
    for alpha in ALPHA_LIST:
        M = max(2, int(alpha * N))
        t0 = time.time()
        rng = np.random.RandomState(seed)
        Xi = rng.choice([-1.0, 1.0], size=(M, N)).astype(np.float64)
        W = (Xi.T @ Xi) / float(N)
        np.fill_diagonal(W, 0.0)

        if USE_POWER_ITER:
            lmax = compute_lambda_max_power(W, n_iter=50, seed=seed)
        else:
            lmax = compute_lambda_max_exact(W)

        # Free-Poisson null (sigma^2 = 1 since W ~ Xi^T Xi / N with +-1 entries)
        sigma2 = 1.0   # scale: eigenvalue of W near 1+sqrt(alpha) for loaded patterns
        lambda_plus = mp_upper_edge(alpha, sigma2)
        sigma_tw = tw_sigma(N, lambda_plus)
        z_clean = (lmax - lambda_plus) / sigma_tw if sigma_tw > 1e-15 else float("nan")
        elapsed = time.time() - t0

        print(f"  [seed={seed} alpha={alpha:.2f} M={M}] "
              f"lambda_max={lmax:.4f} lambda_MP={lambda_plus:.4f} "
              f"sigma_TW={sigma_tw:.4f} Z={z_clean:.2f} t={elapsed:.1f}s", flush=True)

        results[alpha] = {
            "alpha": alpha, "M": M, "N": N,
            "lambda_max": float(lmax),
            "lambda_mp_plus": lambda_plus,
            "sigma_tw": sigma_tw,
            "z_clean": float(z_clean),
            "elapsed_s": elapsed,
        }
    return {"alpha_results": results, "seed": seed, "N": N, "run_mode": RUN_MODE}


def _instrumentation_selftest():
    """Assert lambda_max and Z_clean are non-null at small scale."""
    N_t = 256
    M_t = 25   # alpha ~ 0.10
    seed = 42
    rng = np.random.RandomState(seed)
    Xi_t = rng.choice([-1.0, 1.0], size=(M_t, N_t)).astype(np.float64)
    W_t = (Xi_t.T @ Xi_t) / float(N_t)
    np.fill_diagonal(W_t, 0.0)
    lmax = compute_lambda_max_power(W_t, n_iter=30, seed=seed)
    assert not math.isnan(lmax), "selftest: lambda_max is NaN"
    assert lmax > 0, f"selftest: lambda_max={lmax} <= 0"
    alpha_t = M_t / N_t
    edge = mp_upper_edge(alpha_t, 1.0)
    tw = tw_sigma(N_t, edge)
    z = (lmax - edge) / tw if tw > 1e-12 else float("nan")
    assert not math.isnan(z), "selftest: Z_clean is NaN"
    print(f"[selftest] PASS N={N_t} lmax={lmax:.4f} edge={edge:.4f} Z={z:.2f}", flush=True)


_instrumentation_selftest()


def aggregate_results(per_seed: Dict) -> Dict:
    agg = {}
    for alpha in ALPHA_LIST:
        z_vals, lmax_vals = [], []
        for sd in per_seed.values():
            r = sd["alpha_results"].get(alpha) or sd["alpha_results"].get(str(alpha))
            if r is None:
                continue
            if not math.isnan(r["z_clean"]):
                z_vals.append(r["z_clean"])
            lmax_vals.append(r["lambda_max"])
        agg[alpha] = {
            "alpha": alpha,
            "mean_z_clean": float(np.mean(z_vals)) if z_vals else float("nan"),
            "std_z_clean": float(np.std(z_vals, ddof=1)) if len(z_vals) > 1 else float("nan"),
            "mean_lambda_max": float(np.mean(lmax_vals)) if lmax_vals else float("nan"),
            "n_seeds": len(z_vals),
        }
    return agg


def compute_verdict(agg: Dict) -> Tuple[str, str]:
    z_vals = [v["mean_z_clean"] for v in agg.values() if not math.isnan(v["mean_z_clean"])]
    if not z_vals:
        return ("HARD_FAIL", "No valid Z_clean estimates.")
    max_abs_z = max(abs(z) for z in z_vals)
    min_z = min(z_vals)
    max_z = max(z_vals)
    if max_abs_z <= 3.0:
        return ("HARD_PASS",
                f"Q-C2 spectral-audit confirmed at N={N}. max_|Z|={max_abs_z:.2f} <= 3.0. "
                f"Z range [{min_z:.2f}, {max_z:.2f}] within +-3 sigma_TW of free-Poisson edge. "
                f"Spectral-audit production readiness at N={N} confirmed.")
    if max_abs_z > HF_Z_ABS:
        return ("HARD_FAIL",
                f"Q-C2 bulk edge far from free-Poisson null. max_|Z|={max_abs_z:.2f} > {HF_Z_ABS}. "
                f"Spectral anomaly present; audit API not ready at N={N}.")
    return ("MIDDLE_BAND",
            f"Q-C2 marginal spectral consistency. max_|Z|={max_abs_z:.2f} in "
            f"({HP_Z_HI:.0f}, {HF_Z_ABS:.0f}]. Z range [{min_z:.2f}, {max_z:.2f}].")


def main():
    t_start = time.time()
    print(f"[{ANCHOR_NAME}] run_mode={RUN_MODE} N={N} alpha_list={ALPHA_LIST} "
          f"seeds={SEEDS} use_power_iter={USE_POWER_ITER}", flush=True)

    out_dir = get_output_dir(ANCHOR_NAME)
    run_config = {"N": N, "run_mode": RUN_MODE}
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print(f"[ckpt] {len(done)}/{len(SEEDS)} done; running {remaining}", flush=True)

    for seed in remaining:
        print(f"[{ANCHOR_NAME}] seed={seed} starting", flush=True)
        r = run_seed(seed)
        write_partial(out_dir, seed, r)
        print(f"[{ANCHOR_NAME}] seed={seed} done", flush=True)

    per_seed = aggregate_partials(out_dir, SEEDS)
    agg = aggregate_results(per_seed)
    verdict, verdict_msg = compute_verdict(agg)

    total_elapsed = time.time() - t_start
    metrics = {
        "anchor_name": ANCHOR_NAME,
        "run_mode": RUN_MODE,
        "N": N,
        "alpha_list": ALPHA_LIST,
        "seeds": SEEDS,
        "aggregate": {str(k): v for k, v in agg.items()},
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": total_elapsed,
    }
    metrics_path = get_output_dir(ANCHOR_NAME) / "metrics.json"
    with open(metrics_path, "w", encoding="utf-8") as fh:
        json.dump(metrics, fh, indent=2)
    print(f"[{ANCHOR_NAME}] verdict={verdict}", flush=True)
    print(f"[{ANCHOR_NAME}] {verdict_msg}", flush=True)
    print(f"[{ANCHOR_NAME}] elapsed={total_elapsed:.1f}s", flush=True)


if __name__ == "__main__":
    main()
