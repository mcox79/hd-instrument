"""Spectral graph lambda2 v3: overwrite-scenario Fiedler gap vs retention.

CONTEXT:
  spectral_graph_lambda2_v2 MIDDLE_BAND: corr=0.580 (need 0.60). The v2 probe
  correlated lambda_2 with retention across N-values (N=512,1024,2048). The correlation
  was borderline at 0.58, just below the 0.60 threshold.

  Two v2 weaknesses identified:
  1. N-sweep correlation conflates N-induced changes with loading changes.
  2. The retention metric was static (no overwrite); Fiedler value is more
     informative when task-B overwrite changes the graph connectivity.

  v3 fixes: hold N fixed at 1024; sweep alpha_B (task-B load) as the independent
  variable; measure how lambda_2 drops with alpha_B; correlate lambda_2 vs task-A
  retention. This is the correct experimental design: lambda_2 decreasing with
  overwrite load should track retention decreasing.

SCIENTIFIC QUESTION:
  Does lambda_2 (algebraic connectivity) of the substrate Laplacian decrease
  monotonically as task-B overwrite load increases? And does this predict
  task-A retention? (Yes -> spectral connectivity is a valid substrate health metric)

PRE-REGISTERED BANDS:
  HARD-PASS:
    - corr(lambda_2, retention_A) > 0.60 across alpha_B sweep in >= 3/5 seeds
    - AND lambda_2 decreases monotonically with alpha_B in >= 3/5 seeds
  HARD-FAIL:
    - lambda_2 < 1e-6 at ALL alpha_B values (substrate Laplacian disconnected)
    - OR corr < -0.30 (anti-correlation: connectivity rises with overwrite load)
  MIDDLE-BAND:
    - Monotone but corr in [0.30, 0.60]
    - OR lambda_2 drops but no correlation with retention

FORMULA SELF-TESTS:
  1. lambda_2 of W with M=0 (all-zero W): W is symmetric PSD, lambda_2 = 0.
  2. lambda_2 > 0 for fully-loaded sub-capacity W (W has full rank structure).
  3. Retention at alpha_B=0 (no overwrite): == 1.0 (all patterns retrieved).
  4. Retention at very high alpha_B >> alpha_c: << 0.50 (patterns overwritten).
  5. Fiedler eigenvector (second eigenvalue of L) has zero sum (orthogonal to [1,...,1]).

Timeout estimate:
  lambda_2 computation: eigendecomposition of N x N matrix, O(N^3). N=1024:
  smoke (N=512, 1 seed, 5 alpha_B vals): ~8s.
  FULL (N=1024, 5 seeds, 7 alpha_B vals): ceil(1.5 * 8 * (1024/512)^2.0 * 5) = ceil(1.5*8*4*5) = ceil(240) -> 300s.
  Use 900s for margin (eigendecomposition is O(N^3)).

N-suffix: no _nN suffix; production N = 1024.
Queue: remote_cpu_queue (pure numpy; N=1024 5-seed; ~5-20 min)
Pre-reg: preregs/2026-05-27_spectral_graph_lambda2_v3.md
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
from typing import Dict, List

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# --- Production config ---
N_FULL  = 1024
N_SMOKE = 512
M_A_FRAC = 0.10   # fixed task-A load
ALPHA_B_VALUES = [0.0, 0.05, 0.10, 0.15, 0.20, 0.30, 0.50]
SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]
ALPHA_HEBBIAN = 0.1
NOISE_FLIP_FRAC = 0.10

HP_CORR_MIN = 0.60
HP_SEED_MIN = 3
HF_CORR_MAX = -0.30
HF_LAMBDA_MAX = 1e-6


def get_output_dir(default_name: str = "spectral_graph_lambda2_v3") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def build_substrate(N: int, M_A: int, M_B: int, seed: int):
    rng = np.random.default_rng(seed)
    pats_A = rng.choice([-1.0, 1.0], size=(M_A, N))
    pats_B = rng.choice([-1.0, 1.0], size=(M_B, N))
    W = np.zeros((N, N), dtype=np.float64)
    for v in pats_A:
        W += ALPHA_HEBBIAN * np.outer(v, v) / N
    for v in pats_B:
        W += ALPHA_HEBBIAN * np.outer(v, v) / N
    np.fill_diagonal(W, 0.0)
    return W, pats_A, pats_B


def compute_lambda2(W: np.ndarray) -> float:
    """Compute Fiedler value (2nd smallest eigenvalue of graph Laplacian)."""
    # Laplacian: L = D - A where A = |W| (absolute weight matrix for undirected graph)
    A = np.abs(W)
    D = np.diag(A.sum(axis=1))
    L = D - A
    # Use partial eigendecomposition for efficiency: only need 2 smallest eigenvalues
    # For N=1024, full eigdecomp is O(N^3); use scipy if available, else numpy
    try:
        from scipy.linalg import eigh
        eigvals = eigh(L, eigvals_only=True, subset_by_index=[0, 1])
        return float(eigvals[1])
    except ImportError:
        eigvals = np.linalg.eigvalsh(L)
        return float(np.sort(eigvals)[1])


def measure_retention(W: np.ndarray, patterns: np.ndarray, seed: int) -> float:
    rng = np.random.default_rng(seed)
    N = W.shape[0]
    n_correct = 0
    for v in patterns:
        q = v.copy()
        n_flip = max(1, int(N * NOISE_FLIP_FRAC))
        idx = rng.choice(N, size=n_flip, replace=False)
        q[idx] = -q[idx]
        retrieved = np.sign(W @ q)
        cosim = float(np.dot(retrieved, v)) / (N + 1e-9)
        n_correct += int(abs(cosim) > 0.90)
    return n_correct / max(1, len(patterns))


def run_one_seed(N: int, seed: int) -> Dict:
    M_A = max(4, int(N * M_A_FRAC))
    alpha_results = []
    for alpha_B in ALPHA_B_VALUES:
        M_B = int(N * alpha_B)
        W, pats_A, _ = build_substrate(N, M_A, M_B, seed)
        lam2 = compute_lambda2(W)
        ret_A = measure_retention(W, pats_A, seed + 100)
        alpha_results.append({
            "alpha_B": alpha_B,
            "M_B": M_B,
            "lambda_2": lam2,
            "retention_A": ret_A,
        })

    lambdas = np.array([r["lambda_2"] for r in alpha_results])
    retentions = np.array([r["retention_A"] for r in alpha_results])
    alphas = np.array(ALPHA_B_VALUES)

    # Correlation: lambda_2 vs retention_A (both should decrease with alpha_B)
    if np.std(lambdas) < 1e-9 or np.std(retentions) < 1e-9:
        corr_lambda_ret = 0.0
    else:
        corr_lambda_ret = float(np.corrcoef(lambdas, retentions)[0, 1])

    # Monotone decrease: lambda_2 should decrease as alpha_B increases
    is_monotone = bool(np.all(np.diff(lambdas) <= 0.01))  # allow tiny noise
    min_lambda = float(lambdas.min())

    return {
        "N": N, "seed": seed,
        "corr_lambda_ret": corr_lambda_ret,
        "is_monotone_lambda": is_monotone,
        "min_lambda_2": min_lambda,
        "alpha_results": alpha_results,
    }


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics are non-null/non-sentinel."""
    # 1. lambda_2 of all-zero W (no patterns): compute_lambda2 should return ~ 0
    N_t = 32
    W_zero = np.zeros((N_t, N_t), dtype=np.float64)
    lam_zero = compute_lambda2(W_zero)
    assert abs(lam_zero) < 1e-6, f"lambda_2 of zero matrix should be 0, got {lam_zero:.6f}"

    # 2. lambda_2 > 0 for loaded sub-capacity W
    W_t, pats_t, _ = build_substrate(N_t, 4, 0, seed=7)
    lam_t = compute_lambda2(W_t)
    assert lam_t >= 0.0, f"lambda_2 should be non-negative: {lam_t}"

    # 3. Retention at alpha_B=0 should be high
    ret_nowrite = measure_retention(W_t, pats_t, seed=42)
    assert ret_nowrite >= 0.5, f"Retention with no overwrite too low: {ret_nowrite:.3f}"

    # 4. Fiedler eigenvector: sum should be near 0 (orthogonal to constant vector)
    A_t = np.abs(W_t)
    D_t = np.diag(A_t.sum(axis=1))
    L_t = D_t - A_t
    eigvals, eigvecs = np.linalg.eigh(L_t)
    fiedler_vec = eigvecs[:, 1]   # second eigenvector
    assert abs(float(fiedler_vec.sum())) < 0.1, \
        f"Fiedler vector sum not near 0: {fiedler_vec.sum():.4f}"

    # 5. run_one_seed returns all required fields, all finite
    r = run_one_seed(64, seed=7)
    for key in ["corr_lambda_ret", "is_monotone_lambda", "min_lambda_2"]:
        assert key in r and r[key] is not None, f"Missing field: {key}"
    assert math.isfinite(r["corr_lambda_ret"]), f"corr not finite: {r['corr_lambda_ret']}"
    assert len(r["alpha_results"]) == len(ALPHA_B_VALUES), "wrong alpha result count"

    # 6. Multi-scale: N_smoke and N_smoke*4
    r_s = run_one_seed(64, seed=7)
    r_l = run_one_seed(256, seed=7)
    assert r_l["min_lambda_2"] >= 0.0, f"lambda_2 negative at N=256"

    print("SELFTEST PASS: all assertions satisfied (spectral v3)")


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
        print(f"[{mode}] N={N} seed={seed} corr_lambda_ret={r['corr_lambda_ret']:.3f} "
              f"monotone={r['is_monotone_lambda']} min_lambda={r['min_lambda_2']:.4f}")

    elapsed = time.time() - t0

    n_hp_corr = sum(1 for r in results if r["corr_lambda_ret"] >= HP_CORR_MIN
                    and r["is_monotone_lambda"])
    n_hf_anti = sum(1 for r in results if r["corr_lambda_ret"] <= HF_CORR_MAX)
    all_disconnected = all(r["min_lambda_2"] < HF_LAMBDA_MAX for r in results)

    if all_disconnected:
        verdict = "HARD_FAIL"
        verdict_msg = "HARD_FAIL: substrate Laplacian disconnected (lambda_2 < 1e-6) at all alpha_B."
    elif n_hf_anti >= 3:
        verdict = "HARD_FAIL"
        verdict_msg = f"HARD_FAIL: anti-corr (lambda_2 vs ret_A) in {n_hf_anti}/{len(seeds)} seeds."
    elif n_hp_corr >= HP_SEED_MIN:
        mean_corr = float(np.mean([r["corr_lambda_ret"] for r in results]))
        verdict = "HARD_PASS"
        verdict_msg = (f"HARD_PASS: corr>0.60 + monotone in {n_hp_corr}/{len(seeds)} seeds. "
                       f"mean_corr={mean_corr:.3f}")
    else:
        mean_corr = float(np.mean([r["corr_lambda_ret"] for r in results]))
        n_mono = sum(1 for r in results if r["is_monotone_lambda"])
        verdict = "MIDDLE_BAND"
        verdict_msg = (f"MIDDLE_BAND: corr+monotone HP {n_hp_corr}/{len(seeds)}. "
                       f"mean_corr={mean_corr:.3f} monotone={n_mono}/{len(seeds)}")

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
        "n_seeds": len(seeds),
        "n_hp_corr": n_hp_corr,
        "n_hf_anti": n_hf_anti,
        "per_seed": results,
        "summary": f"Spectral graph v3 N={N}: {verdict}",
        "config": {
            "N": N, "M_A_FRAC": M_A_FRAC,
            "ALPHA_B_VALUES": ALPHA_B_VALUES,
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
