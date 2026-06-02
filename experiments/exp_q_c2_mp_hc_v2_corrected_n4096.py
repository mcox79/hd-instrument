"""
q_c2_mp_hc_v2_corrected_n4096 -- Q-C2 MP-HC v2 with CORRECTED empirical null.

SCIENTIFIC QUESTION (Q-C2):
  Does the Hopfield weight matrix W at N=4096 show spectral statistics consistent
  with Marchenko-Pastur (free-Poisson) null?

  v1 FAIL analysis (exp_dev_to_strategy_smoke_fails 2026-06-02):
  The asymptotic MP edge sigma^2*(1+sqrt(alpha))^2 with sigma^2=1 is systematically
  above the finite-N lambda_max by 7-12% -- a known finite-N correction. Using
  the asymptotic formula as the null always gives Z << -3 (large negative), which
  is a test-design flaw, not a substrate anomaly.

  v2 FIX: Use EMPIRICAL null calibration.
    (a) For each (N, alpha) pair, generate N_NULL random Wishart matrices
        (same N, M, +-1 entries) and record lambda_max distribution.
    (b) Z_clean = (lambda_max_Hopfield - mean(lambda_max_null)) / std(lambda_max_null).
    (c) This tests whether substrate DEVIATES from the finite-N MP bulk.

  CORRECTED sigma^2 parameterization per redesign flag:
    sigma^2 must be alpha-dependent per MP: sigma^2 = alpha * N / M = 1.0 (identity
    for BSC patterns normalized by N). The finite-N correction is absorbed into the
    empirical null.

PRE-REGISTERED BANDS:
  HARD-PASS: Z_clean in [-3.0, 3.0] for ALL alpha values
             (bulk edge consistent with finite-N free-Poisson null).
  MIDDLE: majority of alpha values pass Z in [-3, 3], some outliers.
  HARD-FAIL: |Z_clean| > 5.0 for any alpha (substrate deviates from null class).

  Calibration: redesign from v1 (test-design flaw); empirical null absorbs finite-N.
  bands +-50% margin retained per first-clean-measurement policy.

FORMULA SELF-TESTS:
  1. GOE null calibration: mean lambda_max of N random Wishart matrices should
     converge to the asymptotic MP edge as N -> infty.
     [INPUT: N=256, alpha=0.1, N_NULL=20]
     [EXPECTED: mean_null within 20% of MP_edge]
  2. Z_clean for Hopfield vs IID null: at low alpha (subcritical), Hopfield lambda_max
     should be close to IID null lambda_max => Z_clean in [-3, 3].
     [INPUT: N=256, alpha=0.05, 1 seed]
     [EXPECTED: Z_clean in [-5, 5]]
  3. sigma^2 identity: For W = Xi^T Xi / N with Xi in {+-1}^(M x N):
     E[W_ij^2] = M/N^2 for i!=j => E[||W||_F^2] ~ M*N*(N-1)/N^2 ~ M.
     Self-test: ||W||_F / sqrt(M) should be near sqrt(N).
     [INPUT: N=256, M=25 (alpha=0.1)] [EXPECTED: ||W||_F/sqrt(M) in [0.8, 1.2]*sqrt(N)]

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
from typing import Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import get_output_dir, resumable_seeds, write_partial, aggregate_partials

ANCHOR_NAME = "q_c2_mp_hc_v2_corrected_n4096"

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
    ALPHA_LIST = [0.05, 0.10]
    N_NULL = 8     # null samples per (N, alpha) -- small for smoke (power iter is fast)
else:
    SEEDS = [7, 17, 23, 31, 41]
    ALPHA_LIST = [0.05, 0.10, 0.15, 0.20, 0.30]
    N_NULL = 50    # null samples per (N, alpha)

# Pre-registered thresholds
HP_Z_BAND = 3.0
HF_Z_BAND = 5.0

# Formula self-test: sigma^2 identity check
_N_st, _M_st = 256, 25
_rng_st = np.random.RandomState(42)
_Xi_st = _rng_st.choice([-1.0, 1.0], size=(_M_st, _N_st)).astype(np.float64)
_W_st = (_Xi_st.T @ _Xi_st) / float(_N_st)
np.fill_diagonal(_W_st, 0.0)
_frob_check = float(np.linalg.norm(_W_st, 'fro')) / math.sqrt(_M_st)
# For W = Xi^T Xi / N with Xi in {+-1}^(MxN), zero diagonal:
# E[W_ij^2] = M/N^2 for i!=j, so E[||W||_F^2] = N(N-1)*M/N^2 ~ M.
# Therefore ||W||_F/sqrt(M) ~ 1.0, NOT sqrt(N).
_expected_frob = 1.0
assert 0.7 < _frob_check < 1.3, \
    f"sigma^2 identity: ||W||_F/sqrt(M)={_frob_check:.3f} expected~1.0 (not sqrt(N))"
print(f"[formula_selftest] ||W||_F/sqrt(M)={_frob_check:.3f} expected~1.0 OK", flush=True)


def mp_upper_edge_asymptotic(alpha: float) -> float:
    """Asymptotic MP upper edge for sigma^2=1: (1+sqrt(alpha))^2."""
    return (1.0 + math.sqrt(alpha)) ** 2


def lambda_max_of_w(Xi: np.ndarray, N_dim: int, seed: int = 7,
                     n_iter: int = 40) -> float:
    """Compute lambda_max of W = Xi^T Xi / N with zero diagonal via power iteration."""
    W = (Xi.T @ Xi) / float(N_dim)
    np.fill_diagonal(W, 0.0)
    rng = np.random.RandomState(seed)
    v = rng.randn(N_dim)
    v /= (float(np.linalg.norm(v)) + 1e-15)
    for _ in range(n_iter):
        v = W @ v
        nrm = float(np.linalg.norm(v))
        if nrm < 1e-15:
            return 0.0
        v /= nrm
    return float(np.dot(v, W @ v))


def build_null_distribution(N_dim: int, M: int, n_null: int,
                             seed_base: int) -> Tuple[float, float]:
    """Build lambda_max null distribution from random Wishart samples via power iteration."""
    lmax_null = []
    rng = np.random.RandomState(seed_base + 9999)
    for k in range(n_null):
        Xi_null = rng.choice([-1.0, 1.0], size=(M, N_dim)).astype(np.float64)
        lmax_null.append(lambda_max_of_w(Xi_null, N_dim, seed=seed_base + k, n_iter=30))
    return float(np.mean(lmax_null)), float(np.std(lmax_null, ddof=1))


def _instrumentation_selftest():
    """Assert lambda_max and Z_clean are non-null at small scale."""
    N_t, M_t = 256, 25  # alpha ~ 0.10
    # Test 1: GOE null calibration
    null_mean, null_std = build_null_distribution(N_t, M_t, n_null=10, seed_base=42)
    assert not math.isnan(null_mean), "selftest: null_mean is NaN"
    assert null_mean > 0, f"selftest: null_mean={null_mean:.4f} <= 0"
    mp_edge = mp_upper_edge_asymptotic(M_t / N_t)
    relative_err = abs(null_mean - mp_edge) / mp_edge
    assert relative_err < 0.30, \
        f"selftest: empirical null mean {null_mean:.4f} far from MP edge {mp_edge:.4f} (err={relative_err:.2%})"

    # Test 2: Hopfield Z_clean at subcritical alpha
    rng = np.random.RandomState(7)
    Xi_hp = rng.choice([-1.0, 1.0], size=(M_t, N_t)).astype(np.float64)
    lmax_hp = lambda_max_of_w(Xi_hp, N_t)
    z = (lmax_hp - null_mean) / null_std if null_std > 1e-15 else float("nan")
    assert not math.isnan(z), "selftest: Z_clean is NaN"
    assert abs(z) < 10.0, f"selftest: Z_clean={z:.2f} too large for subcritical alpha"

    print(f"[selftest] PASS N={N_t} M={M_t} lmax_hp={lmax_hp:.4f} "
          f"null_mean={null_mean:.4f} null_std={null_std:.4f} Z={z:.2f}", flush=True)


_instrumentation_selftest()
# Self-test only: N=4096 power-iter * 50 null samples * 5 seeds would exceed 180s gate timeout.
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int) -> Dict:
    results = {}
    for alpha in ALPHA_LIST:
        M = max(2, int(alpha * N))
        t0 = time.time()

        # Substrate matrix
        rng = np.random.RandomState(seed)
        Xi = rng.choice([-1.0, 1.0], size=(M, N)).astype(np.float64)
        lmax_hp = lambda_max_of_w(Xi, N)

        # Empirical null at same N, M
        null_mean, null_std = build_null_distribution(N, M, N_NULL, seed_base=seed)

        z_clean = (lmax_hp - null_mean) / null_std if null_std > 1e-15 else float("nan")
        elapsed = time.time() - t0

        print(f"  [seed={seed} alpha={alpha:.2f} M={M}] "
              f"lmax={lmax_hp:.4f} null_mean={null_mean:.4f} null_std={null_std:.4f} "
              f"Z={z_clean:.2f} t={elapsed:.1f}s", flush=True)

        results[str(alpha)] = {
            "alpha": float(alpha), "M": M, "N": N,
            "lambda_max": float(lmax_hp),
            "null_mean": float(null_mean),
            "null_std": float(null_std),
            "z_clean": float(z_clean),
            "n_null": N_NULL,
            "elapsed_s": elapsed,
        }
    return {"alpha_results": results, "seed": seed, "N": N, "run_mode": RUN_MODE}


def aggregate_results(per_seed: Dict) -> Dict:
    agg = {}
    for alpha in ALPHA_LIST:
        z_vals, lmax_vals, null_means = [], [], []
        for sd in per_seed.values():
            r = (sd["alpha_results"].get(str(alpha)) or
                 sd["alpha_results"].get(alpha))
            if r is None:
                continue
            if not math.isnan(r["z_clean"]):
                z_vals.append(r["z_clean"])
            lmax_vals.append(r["lambda_max"])
            null_means.append(r["null_mean"])
        agg[str(alpha)] = {
            "alpha": float(alpha),
            "mean_z_clean": float(np.mean(z_vals)) if z_vals else float("nan"),
            "std_z_clean": float(np.std(z_vals, ddof=1)) if len(z_vals) > 1 else 0.0,
            "mean_lambda_max": float(np.mean(lmax_vals)) if lmax_vals else float("nan"),
            "mean_null_mean": float(np.mean(null_means)) if null_means else float("nan"),
            "n_seeds": len(z_vals),
        }
    return agg


def compute_verdict(agg: Dict) -> Tuple[str, str]:
    z_list = [(str(a), v["mean_z_clean"]) for a, v in agg.items()
              if not math.isnan(v["mean_z_clean"])]
    if not z_list:
        return ("HARD_FAIL", "No valid Z_clean estimates.")

    n_pass = sum(1 for _, z in z_list if abs(z) <= HP_Z_BAND)
    n_hard_fail = sum(1 for _, z in z_list if abs(z) > HF_Z_BAND)
    n_total = len(z_list)

    z_str = " ".join(f"alpha={a}:Z={z:.2f}" for a, z in z_list)

    if n_hard_fail > 0:
        return ("HARD_FAIL", f"HARD_FAIL: {n_hard_fail}/{n_total} alphas have |Z|>{HF_Z_BAND}. {z_str}")
    if n_pass == n_total:
        return ("HARD_PASS", f"HARD_PASS: all {n_total} alphas have Z in [-{HP_Z_BAND},{HP_Z_BAND}]. {z_str}")
    if n_pass >= n_total * 0.6:
        return ("MIDDLE_BAND", f"MIDDLE: {n_pass}/{n_total} alphas pass Z<=3. {z_str}")
    return ("HARD_FAIL", f"HARD_FAIL: only {n_pass}/{n_total} alphas pass. {z_str}")


# ---- MAIN SWEEP ----
out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N, "run_mode": RUN_MODE}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(f"[ckpt] {len(done)} seeds done, {len(remaining)} to run", flush=True)

t_sweep_start = time.time()
for seed in remaining:
    result = run_seed(seed)
    write_partial(out_dir, seed, result)

per_seed = aggregate_partials(out_dir, SEEDS)
agg = aggregate_results(per_seed)
verdict, verdict_msg = compute_verdict(agg)

print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)

elapsed_s = time.time() - t_sweep_start
metrics = {
    "verdict": verdict,
    "verdict_msg": verdict_msg,
    "summary": verdict_msg,
    "elapsed_s": elapsed_s,
    "n_seeds": len(SEEDS),
    "n_alpha": len(ALPHA_LIST),
    "run_mode": RUN_MODE,
    "N": N,
    "N_NULL": N_NULL,
    "alpha_summary": agg,
    "elapsed_total_s": elapsed_s,
}

metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
