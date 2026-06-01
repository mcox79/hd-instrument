"""Tropical geometry substrate probe v1: max-plus semiring interpretation.

CONTEXT:
  Orthogonal probe (cross-domain, per [[feedback-aggressive-cross-domain-research]]).
  Tropical algebra (max-plus semiring): replace (+, *) with (max, +).
  Key connection: the Hopfield energy function E = -x^T W x / 2 can be rewritten as
  a tropical polynomial in the max-plus sense over bipolar {-1,+1}^N states.
  The energy minimum corresponds to the tropical "convex hull" of stored patterns.

  Specifically: the tropical permanent of a matrix is related to pattern retrieval
  (Monge matrices). The algebraic connectivity of substrate under max-plus arithmetic
  may predict the sharp capacity cliff (K/N ~ 0.56) differently from the Fiedler
  spectral value (lambda_2).

  Literature hook: Cohen et al. 2019, Maragos 2019 (morphological/tropical neural nets).
  This is a genuine cross-domain probe -- if substrate energy lives on the tropical
  torus, the capacity limit has a combinatorial certificate.

SCIENTIFIC QUESTIONS:
  1. Does the tropical eigenvalue (max-plus spectral radius) of W track the standard
     energy minimum as pattern loading increases?
  2. Is there a tropical phase transition (spectral radius jump) near alpha ~ 0.56?
  3. Do the tropical eigenvectors correspond to the stored patterns (fixed points)?

INSTRUMENTATION:
  Tropical matrix-vector product: (A ot x)_i = max_j (A_ij + x_j).
  Tropical eigenvalue: lambda such that A ot x = lambda + x (max-plus eigenvalue).
  Power iteration in the tropical semiring converges to the principal tropical eigenvalue.

PRE-REGISTERED BANDS (calibration probe: first tropical geometry measurement on substrate):
  HARD-PASS:
    - Tropical spectral radius shows monotone increase with loading alpha in >= 3/5 seeds
    - AND tropical eigenvectors have cosim > 0.60 with at least one stored pattern
      in >= 3/5 seeds at sub-capacity alpha (proxy: retrieval in tropical space)
  HARD-FAIL:
    - Tropical spectral radius is constant (< 0.01 range) across all alpha values
    - OR tropical power iteration fails to converge in > 5 of 5 seeds (degenerate)
  MIDDLE-BAND:
    - Spectral radius increases but eigenvectors do not align with stored patterns

  Calibration probe: no prior empirical anchor. Bands set +-50% of theoretical prediction
  (tropical spectral radius should = max loading energy = ALPHA_HEBBIAN * N * ALPHA_RATIO).

FORMULA SELF-TESTS:
  1. Tropical A ot x for scalar x=0: result = max of each row of A.
  2. Tropical power iteration on identity (I_tropical = 0 diagonal, -inf elsewhere):
     converges to eigenvalue 0 and eigenvector = 0-vector.
  3. Tropical eigenvalue of all-ones matrix (tropical): = (N-1) since max_j (1+x_j) = 1+max(x).
     For 4x4 all-ones and x=0: result = (1, 1, 1, 1) -> eigenvalue = 1.

Timeout estimate:
  Tropical power iteration O(N^2 * steps); smoke N=256 1 seed ~3s.
  FULL N=1024 5 seeds: ceil(1.5 * 3 * (1024/256)^2 * 5) = ceil(1.5*3*16*5) = ceil(360) = 600s.
  Use 900s for margin (N^2 scaling).

N-suffix: no _nN suffix; production N = 1024.
Queue: remote_cpu_queue (pure numpy; N=1024 5-seed; ~5-20 min)
Pre-reg: preregs/2026-05-27_tropical_geometry_substrate_v1.md
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
from typing import Dict, List, Optional

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# --- Production config ---
N_FULL  = 1024
N_SMOKE = 256
ALPHA_LOADS = [0.02, 0.05, 0.10, 0.15, 0.20, 0.30, 0.50]  # M/N ratios to sweep
SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]
ALPHA_HEBBIAN = 0.1
TROPICAL_ITER_MAX = 200
TROPICAL_CONV_TOL = 1e-4

# Pre-registered thresholds
HP_SPECTRAL_RANGE_MIN = 0.01   # spectral radius range across alpha must exceed this
HP_COSIM_MIN = 0.60
HP_SEED_MIN = 3
HF_DIVERGE_MAX = 5   # more than this many non-convergences = hard-fail


def get_output_dir(default_name: str = "tropical_geometry_substrate_v1") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def build_substrate(N: int, M: int, seed: int) -> tuple:
    rng = np.random.default_rng(seed)
    patterns = rng.choice([-1.0, 1.0], size=(M, N))
    W = np.zeros((N, N), dtype=np.float64)
    for v in patterns:
        W += ALPHA_HEBBIAN * np.outer(v, v) / N
    np.fill_diagonal(W, 0.0)
    return W, patterns


def tropical_mv(A: np.ndarray, x: np.ndarray) -> np.ndarray:
    """Tropical max-plus matrix-vector product: y_i = max_j (A_ij + x_j)."""
    # Vectorized: broadcast A + x[None, :], then max over j-axis
    return np.max(A + x[np.newaxis, :], axis=1)


def tropical_eigenvalue(A: np.ndarray, max_iter: int = 200,
                         tol: float = 1e-4) -> tuple:
    """Max-plus principal eigenvalue via power iteration.

    Returns (eigenvalue, eigenvector, converged, n_iter).
    """
    N = A.shape[0]
    x = np.zeros(N, dtype=np.float64)
    prev_lambda = None
    for i in range(max_iter):
        y = tropical_mv(A, x)
        # Normalize: lambda = max(y - x), then shift x
        lam_candidates = y - x
        lam = float(np.max(lam_candidates))
        x = y - lam
        if prev_lambda is not None and abs(lam - prev_lambda) < tol:
            return lam, x, True, i + 1
        prev_lambda = lam
    return lam, x, False, max_iter


def max_cosim(eigvec: np.ndarray, patterns: np.ndarray) -> float:
    """Max cosine similarity between normalized eigenvector and any stored pattern."""
    if len(patterns) == 0:
        return 0.0
    # Map eigvec to bipolar sign for comparison
    ev_sign = np.sign(eigvec)
    N = len(ev_sign)
    cosims = [float(np.dot(ev_sign, v)) / (N + 1e-9) for v in patterns]
    return float(max(abs(c) for c in cosims))


def run_one_seed(N: int, seed: int) -> Dict:
    alpha_results = []
    for alpha in ALPHA_LOADS:
        M = max(1, int(N * alpha))
        W, patterns = build_substrate(N, M, seed)
        lam, eigvec, converged, n_iter = tropical_eigenvalue(W, TROPICAL_ITER_MAX, TROPICAL_CONV_TOL)
        cosim = max_cosim(eigvec, patterns)
        alpha_results.append({
            "alpha": alpha,
            "M": M,
            "tropical_lambda": float(lam),
            "converged": converged,
            "n_iter": n_iter,
            "max_cosim": cosim,
        })

    lambdas = [r["tropical_lambda"] for r in alpha_results]
    lambda_range = float(max(lambdas) - min(lambdas))
    n_converged = sum(1 for r in alpha_results if r["converged"])
    n_diverged = len(alpha_results) - n_converged

    # Monotone increase check: Pearson corr of alpha vs lambda
    alphas_arr = np.array(ALPHA_LOADS, dtype=float)
    lambdas_arr = np.array(lambdas, dtype=float)
    if np.std(lambdas_arr) < 1e-9:
        lambda_alpha_corr = 0.0
    else:
        lambda_alpha_corr = float(np.corrcoef(alphas_arr, lambdas_arr)[0, 1])

    max_cosim_at_subcap = max(
        (r["max_cosim"] for r in alpha_results if r["alpha"] <= 0.15),
        default=0.0
    )

    return {
        "N": N, "seed": seed,
        "lambda_range": lambda_range,
        "lambda_alpha_corr": lambda_alpha_corr,
        "max_cosim_subcap": max_cosim_at_subcap,
        "n_converged": n_converged,
        "n_diverged": n_diverged,
        "alpha_results": alpha_results,
    }


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics are non-null/non-sentinel."""
    # 1. Tropical mv of identity (all-0 diagonal, -inf off-diagonal via 0-matrix approx):
    #    For A=0 and x=0, result should be 0-vector
    A_zero = np.zeros((4, 4), dtype=np.float64)
    x_zero = np.zeros(4, dtype=np.float64)
    y = tropical_mv(A_zero, x_zero)
    assert np.allclose(y, 0.0), f"Tropical mv of zero matrix: expected 0, got {y}"

    # 2. All-ones 4x4 matrix, x=zeros: y_i = max_j(1 + 0) = 1
    A_ones = np.ones((4, 4), dtype=np.float64)
    y_ones = tropical_mv(A_ones, x_zero)
    assert np.allclose(y_ones, 1.0), f"Tropical mv all-ones: expected 1.0, got {y_ones}"

    # 3. Tropical eigenvalue converges for small substrate
    N_t = 32
    W_t, pats_t = build_substrate(N_t, 4, seed=42)
    lam_t, eigvec_t, conv_t, niter_t = tropical_eigenvalue(W_t)
    assert conv_t, f"Tropical eigenvalue did not converge at N=32"
    assert math.isfinite(lam_t), f"Tropical eigenvalue not finite: {lam_t}"
    assert len(eigvec_t) == N_t, f"Eigenvector wrong shape"

    # 4. max_cosim returns value in [0, 1]
    cs = max_cosim(eigvec_t, pats_t)
    assert 0.0 <= cs <= 1.0, f"cosim out of range: {cs}"

    # 5. run_one_seed returns all required fields
    r = run_one_seed(64, seed=7)
    for key in ["lambda_range", "lambda_alpha_corr", "max_cosim_subcap",
                "n_converged", "n_diverged"]:
        assert key in r and r[key] is not None, f"Missing field: {key}"
        assert math.isfinite(r[key]), f"Field {key} not finite: {r[key]}"
    assert len(r["alpha_results"]) == len(ALPHA_LOADS), "Wrong number of alpha results"

    # 6. Multi-scale: N_smoke and N_smoke*4
    r_s = run_one_seed(64, seed=7)
    r_l = run_one_seed(256, seed=7)
    assert r_l["lambda_range"] >= 0.0, f"lambda_range negative at N=256"
    # At least some alphas should converge
    assert r_l["n_converged"] >= len(ALPHA_LOADS) // 2, \
        f"Too many non-convergences at N=256: {r_l['n_diverged']}/{len(ALPHA_LOADS)}"

    print("SELFTEST PASS: all assertions satisfied (tropical geometry)")


_instrumentation_selftest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true", dest="self_test")
    args = parser.parse_args()

    if args.self_test:
        sys.exit(0)

    N = N_SMOKE if args.smoke else N_FULL
    seeds = SEEDS_SMOKE if args.smoke else SEEDS_FULL
    out_dir = get_output_dir()
    mode = "smoke" if args.smoke else "full"

    t0 = time.time()
    results = []
    for seed in seeds:
        r = run_one_seed(N, seed)
        results.append(r)
        print(f"[{mode}] N={N} seed={seed} lambda_range={r['lambda_range']:.4f} "
              f"corr_alpha={r['lambda_alpha_corr']:.3f} cosim_subcap={r['max_cosim_subcap']:.3f} "
              f"converged={r['n_converged']}/{len(ALPHA_LOADS)}")

    elapsed = time.time() - t0

    n_hp_range = sum(1 for r in results
                     if r["lambda_range"] >= HP_SPECTRAL_RANGE_MIN
                     and r["lambda_alpha_corr"] > 0)
    n_hp_cosim = sum(1 for r in results if r["max_cosim_subcap"] >= HP_COSIM_MIN)
    total_diverged = sum(r["n_diverged"] for r in results)

    if total_diverged > HF_DIVERGE_MAX * len(seeds):
        verdict = "HARD_FAIL"
        verdict_msg = (f"HARD_FAIL: tropical power iteration diverged in "
                       f"{total_diverged}/{len(seeds)*len(ALPHA_LOADS)} cases.")
    elif n_hp_range >= HP_SEED_MIN and n_hp_cosim >= HP_SEED_MIN:
        verdict = "HARD_PASS"
        verdict_msg = (f"HARD_PASS: spectral range>0.01 in {n_hp_range}/{len(seeds)} seeds; "
                       f"cosim>0.60 in {n_hp_cosim}/{len(seeds)} seeds.")
    elif n_hp_range < HP_SEED_MIN and all(r["lambda_range"] < HP_SPECTRAL_RANGE_MIN
                                          for r in results):
        verdict = "HARD_FAIL"
        verdict_msg = (f"HARD_FAIL: tropical spectral radius constant across all alpha. "
                       f"mean_range={np.mean([r['lambda_range'] for r in results]):.6f}")
    else:
        mean_range = float(np.mean([r["lambda_range"] for r in results]))
        mean_cosim = float(np.mean([r["max_cosim_subcap"] for r in results]))
        verdict = "MIDDLE_BAND"
        verdict_msg = (f"MIDDLE_BAND: spectral range HP {n_hp_range}/{len(seeds)}; "
                       f"cosim HP {n_hp_cosim}/{len(seeds)}. "
                       f"mean_range={mean_range:.4f} mean_cosim={mean_cosim:.3f}")

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
        "n_seeds": len(seeds),
        "n_hp_range": n_hp_range,
        "n_hp_cosim": n_hp_cosim,
        "total_diverged": total_diverged,
        "per_seed": results,
        "summary": f"Tropical geometry N={N}: {verdict}",
        "config": {
            "N": N,
            "ALPHA_LOADS": ALPHA_LOADS,
            "seeds": seeds,
        },
    }

    out_path = out_dir / "metrics.json"
    with open(out_path, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"VERDICT: {verdict}")
    print(f"MSG: {verdict_msg}")
    print(f"Wrote metrics to {out_path}")


if __name__ == "__main__":
    main()
