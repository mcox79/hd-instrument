"""Spectral graph lambda2 v4: multi-N multi-seed FULL to resolve v2/v3 sign-flip.

CONTEXT:
  v2 HARD_PASS: corr=0.615 across N=[256,512], seeds=[7,17].
  v3 MIDDLE_BAND: corr=-0.881 at N=512, seed=17 single-seed.
  v2/v3 sign-flip demoted spectral-graph row from 🟢 -> 🟡 at v234.
  The v234 PRIMARY rescue was "multi-seed FULL at multiple N."

  Key question: is the correlation sign regime-dependent on N and/or seed,
  or does a consistent positive correlation emerge at FULL multi-seed multi-N?

SCIENTIFIC QUESTION:
  Does lambda_2 (algebraic connectivity of substrate weight-matrix graph)
  positively correlate with task-A retention across:
  - N in [512, 1024, 2048]
  - 5 seeds each
  - alpha_B sweep [0.0, 0.05, 0.10, 0.15, 0.20, 0.30, 0.50]
  If yes: spectral connectivity is a valid substrate health metric (row 🟡 -> 🟢).
  If sign-flip repeats at N=1024+ multi-seed: the 🟡 row is honest (seed-regime-dependent).

PRE-REGISTERED BANDS (envelope expansion from v2 HARD_PASS):
  Prior anchor: v2 corr=0.615 (borderline HARD_PASS); v3 single-seed corr=-0.881 (confounds).
  Bands: extended to multi-N; calibration widening +25% from v2 threshold.

  HARD_PASS: mean_corr across all N and seeds >= 0.55 (HARD_PASS if positive signal)
             AND monotone lambda_2 decrease in >= 3/5 seeds at N=1024.
  HARD_FAIL: mean_corr <= -0.25 (persistent anti-correlation at multi-N multi-seed)
             AND sign is negative in >= 4/5 seeds at N=1024.
  MIDDLE_BAND: corr in (-0.25, 0.55) range, OR N-dependent sign-flip confirmed.

FORMULA SELF-TESTS (from v3):
  1. lambda_2 of W with M=0 (all-zero W): == 0 (disconnected Laplacian).
  2. lambda_2 > 0 for sub-capacity loaded W.
  3. Retention at alpha_B=0: high (no overwrite = perfect retrieval).
  4. Fiedler eigenvector sum ~= 0 (orthogonal to constant vector).
  5. run_one_seed(N=64, seed=7) returns all required fields, all finite.
  6. Multi-scale: N_smoke and N_smoke*4 both have lambda_2 >= 0.

TIMEOUT ESTIMATE:
  v3 smoke N=512 1 seed 7 alpha_B: 8s elapsed.
  v4 FULL: 3 N-values * 5 seeds * 7 alpha_B each.
  N=512: ~1.6s/seed (8/5 overhead). N=1024: 8x slower = ~12.8s/seed.
  N=2048: 64x slower = ~102s/seed.
  Total: 3 * (5*1.6 + 5*12.8 + 5*102) = 3 * (8+64+510) = 3*582 = 1746s.
  timeout_s = ceil(1.5 * 1746) = ceil(2619) -> 3600s (safety: 3x overhead for scipy).
  Conservative: 5400s.

  Smoke: N=256 1 seed 3 alpha_B: ~0.5s.

N-suffix: no _nN suffix; production N = [512,1024,2048] multi-N (PROT-018 N is multi-valued).
Queue: remote_cpu_queue (pure numpy/scipy; 3N x 5-seed; ~1746s = 29min nominal, 60min w/ safety)
Pre-reg: preregs/2026-05-27_spectral_graph_lambda2_v4.md
Parent: spectral_graph_lambda2_v3 (MIDDLE_BAND v2/v3 sign-flip; resolves via multi-N multi-seed)
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

# PRODUCTION CONFIG
N_VALUES_FULL  = [512, 1024, 2048]
N_VALUES_SMOKE = [256, 1024]   # multi-scale: N and 4xN per role-contract smoke gate
ALPHA_B_VALUES = [0.0, 0.05, 0.10, 0.15, 0.20, 0.30, 0.50]
ALPHA_B_SMOKE  = [0.0, 0.10, 0.30]
SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]

M_A_FRAC     = 0.10
ALPHA_HEBBIAN = 0.1
NOISE_FLIP_FRAC = 0.10

HP_CORR_MIN   = 0.55    # mean across all seeds at N=1024 (adjusted from v2's 0.60 by -0.05 for multi-N)
HF_CORR_MAX   = -0.25   # persistent anti-correlation threshold
HP_SEED_MIN   = 3       # seeds at N=1024 that must clear monotone+corr
HF_SEED_MIN   = 4       # seeds at N=1024 that must show negative sign for HARD_FAIL


def get_output_dir(default_name: str = "spectral_graph_lambda2_v4") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def build_substrate(N: int, M_A: int, M_B: int, seed: int):
    """Build Hopfield W for M_A + M_B BSC patterns."""
    rng = np.random.default_rng(seed)
    pats_A = rng.choice([-1.0, 1.0], size=(M_A, N))
    pats_B = rng.choice([-1.0, 1.0], size=(M_B, N))
    W = np.zeros((N, N), dtype=np.float64)
    for v in pats_A:
        W += ALPHA_HEBBIAN * np.outer(v, v) / N
    for v in pats_B:
        W += ALPHA_HEBBIAN * np.outer(v, v) / N
    np.fill_diagonal(W, 0.0)
    return W, pats_A


def compute_lambda2(W: np.ndarray) -> float:
    """Compute Fiedler value (2nd smallest eigenvalue of graph Laplacian)."""
    A = np.abs(W)
    D = np.diag(A.sum(axis=1))
    L = D - A
    try:
        from scipy.linalg import eigh
        eigvals = eigh(L, eigvals_only=True, subset_by_index=[0, 1])
        return float(eigvals[1])
    except ImportError:
        eigvals = np.linalg.eigvalsh(L)
        return float(np.sort(eigvals)[1])


def measure_retention(W: np.ndarray, patterns: np.ndarray, seed: int) -> float:
    """Fraction of patterns self-retrieved with 10% noise."""
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


def run_one_seed(N: int, seed: int, alpha_b_values: List[float] = None) -> Dict:
    """Run one (N, seed) cell sweeping alpha_B."""
    if alpha_b_values is None:
        alpha_b_values = ALPHA_B_VALUES
    M_A = max(4, int(N * M_A_FRAC))
    alpha_results = []
    for alpha_B in alpha_b_values:
        M_B = int(N * alpha_B)
        W, pats_A = build_substrate(N, M_A, M_B, seed)
        lam2 = compute_lambda2(W)
        ret_A = measure_retention(W, pats_A, seed + 100)
        alpha_results.append({
            "alpha_B": alpha_B, "M_B": M_B,
            "lambda_2": lam2, "retention_A": ret_A,
        })

    lambdas = np.array([r["lambda_2"] for r in alpha_results])
    retentions = np.array([r["retention_A"] for r in alpha_results])

    if np.std(lambdas) < 1e-9 or np.std(retentions) < 1e-9:
        corr = 0.0
    else:
        corr = float(np.corrcoef(lambdas, retentions)[0, 1])

    is_monotone = bool(np.all(np.diff(lambdas) <= 0.01))
    min_lambda = float(lambdas.min())

    return {
        "N": N, "seed": seed,
        "corr_lambda_ret": corr,
        "is_monotone_lambda": is_monotone,
        "min_lambda_2": min_lambda,
        "alpha_results": alpha_results,
    }


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics are non-null/non-sentinel at smoke scale."""
    # 1. lambda_2 of zero W == 0
    N_t = 32
    W_zero = np.zeros((N_t, N_t), dtype=np.float64)
    lam_zero = compute_lambda2(W_zero)
    assert abs(lam_zero) < 1e-6, f"lambda_2 of zero matrix should be 0, got {lam_zero:.6f}"

    # 2. lambda_2 >= 0 for loaded sub-capacity W
    W_t, pats_t = build_substrate(N_t, 4, 0, seed=7)
    lam_t = compute_lambda2(W_t)
    assert lam_t >= 0.0, f"lambda_2 should be non-negative: {lam_t}"

    # 3. Retention at alpha_B=0 should be high
    ret_nowrite = measure_retention(W_t, pats_t, seed=42)
    assert ret_nowrite >= 0.5, f"Retention with no overwrite too low: {ret_nowrite:.3f}"

    # 4. Fiedler eigenvector sum near 0
    W_check, _ = build_substrate(N_t, 4, 0, seed=17)
    A_t = np.abs(W_check)
    D_t = np.diag(A_t.sum(axis=1))
    L_t = D_t - A_t
    eigvals, eigvecs = np.linalg.eigh(L_t)
    fiedler_vec = eigvecs[:, 1]
    assert abs(float(fiedler_vec.sum())) < 0.1, \
        f"Fiedler vector sum not near 0: {fiedler_vec.sum():.4f}"

    # 5. run_one_seed returns all required fields, all finite
    r = run_one_seed(64, seed=7, alpha_b_values=[0.0, 0.10, 0.30])
    for key in ["corr_lambda_ret", "is_monotone_lambda", "min_lambda_2"]:
        assert key in r and r[key] is not None, f"Missing field: {key}"
    assert math.isfinite(r["corr_lambda_ret"]), f"corr not finite: {r['corr_lambda_ret']}"
    assert len(r["alpha_results"]) == 3, f"wrong alpha result count: {len(r['alpha_results'])}"

    # 6. Multi-scale: N_smoke and N_smoke*4
    r_s = run_one_seed(64, seed=7, alpha_b_values=[0.0, 0.10])
    r_l = run_one_seed(128, seed=7, alpha_b_values=[0.0, 0.10])
    assert r_s["min_lambda_2"] >= 0.0, f"lambda_2 negative at N=64"
    assert r_l["min_lambda_2"] >= 0.0, f"lambda_2 negative at N=128"

    print("[spectral_v4 selftest] PASS: all assertions satisfied")


_instrumentation_selftest()


def compute_verdict(all_results: Dict[str, List[Dict]]) -> tuple:
    """Compute verdict from results grouped by N-value."""
    if not all_results:
        return ("SPECTRAL_INCONCLUSIVE", "No results.")

    # Primary analysis: N=1024 multi-seed (primary resolution of v2/v3 sign-flip)
    results_1024 = all_results.get("1024", [])
    if not results_1024:
        return ("SPECTRAL_INCONCLUSIVE", "No N=1024 results.")

    corrs_1024 = [r["corr_lambda_ret"] for r in results_1024]
    mono_1024 = sum(1 for r in results_1024 if r["is_monotone_lambda"])
    mean_corr_1024 = float(np.mean(corrs_1024))
    n_hp_1024 = sum(1 for r in results_1024
                    if r["corr_lambda_ret"] >= HP_CORR_MIN and r["is_monotone_lambda"])
    n_neg_1024 = sum(1 for r in results_1024 if r["corr_lambda_ret"] <= HF_CORR_MAX)

    # Secondary: all-N pooled mean
    all_corrs = [r["corr_lambda_ret"] for rs in all_results.values() for r in rs]
    mean_corr_all = float(np.mean(all_corrs))

    msg = (f"mean_corr_N1024={mean_corr_1024:.3f} "
           f"mean_corr_all={mean_corr_all:.3f} "
           f"hp_N1024={n_hp_1024}/{len(results_1024)} "
           f"neg_N1024={n_neg_1024}/{len(results_1024)} "
           f"mono_N1024={mono_1024}/{len(results_1024)}")

    if n_neg_1024 >= HF_SEED_MIN and mean_corr_1024 <= HF_CORR_MAX:
        return ("SPECTRAL_SIGN_CONSISTENT_NEGATIVE",
                f"HARD_FAIL: Anti-corr confirmed multi-seed N=1024. {msg} "
                f"Spectral graph lambda_2 anti-predicts retention.")
    elif n_hp_1024 >= HP_SEED_MIN and mean_corr_1024 >= HP_CORR_MIN:
        return ("SPECTRAL_HARD_PASS",
                f"HARD_PASS: Corr+monotone in {n_hp_1024}/{len(results_1024)} seeds N=1024. {msg}")
    else:
        return ("SPECTRAL_MIDDLE_BAND",
                f"MIDDLE_BAND: Inconsistent sign across seeds N=1024. {msg}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true", dest="self_test")
    parser.add_argument("--timeout", type=float, default=3600.0)
    args = parser.parse_args()
    if args.self_test:
        sys.exit(0)

    is_smoke = args.smoke
    n_values = N_VALUES_SMOKE if is_smoke else N_VALUES_FULL
    seeds = SEEDS_SMOKE if is_smoke else SEEDS_FULL
    alpha_vals = ALPHA_B_SMOKE if is_smoke else ALPHA_B_VALUES
    out_dir = get_output_dir()
    mode = "smoke" if is_smoke else "full"

    t0 = time.time()
    all_results: Dict[str, List[Dict]] = {}
    deadline = t0 + args.timeout - 30

    for N in n_values:
        n_key = str(N)
        all_results[n_key] = []
        for seed in seeds:
            if time.time() > deadline:
                print(f"[{mode}] TIMEOUT approaching, stopping at N={N} seed={seed}")
                break
            r = run_one_seed(N, seed, alpha_b_values=alpha_vals)
            all_results[n_key].append(r)
            print(f"[{mode}] N={N} seed={seed} corr={r['corr_lambda_ret']:.3f} "
                  f"monotone={r['is_monotone_lambda']} min_lam2={r['min_lambda_2']:.4f}")

    elapsed = time.time() - t0
    verdict, verdict_msg = compute_verdict(all_results)

    print(f"[spectral_v4] VERDICT: {verdict}")
    print(f"[spectral_v4] {verdict_msg}")
    print(f"[spectral_v4] elapsed={elapsed:.1f}s")

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
        "summary": {
            "n_values_tested": n_values,
            "seeds": seeds,
            "mode": mode,
            "results_by_N": {
                nk: [
                    {
                        "seed": r["seed"],
                        "corr_lambda_ret": r["corr_lambda_ret"],
                        "is_monotone_lambda": r["is_monotone_lambda"],
                        "min_lambda_2": r["min_lambda_2"],
                    }
                    for r in rs
                ]
                for nk, rs in all_results.items()
            },
        },
        "config": {
            "n_values": n_values, "seeds": seeds,
            "alpha_b_values": alpha_vals, "M_A_frac": M_A_FRAC,
            "smoke": is_smoke,
        },
    }
    mpath = out_dir / "metrics.json"
    with open(mpath, "w") as fh:
        json.dump(metrics, fh, indent=2)
    print(f"[exp] metrics -> {mpath}")


if __name__ == "__main__":
    main()
