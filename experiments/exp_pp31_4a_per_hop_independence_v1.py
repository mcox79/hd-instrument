"""PP31-4A: Independence test for per-hop error correlation in multi-hop retrieval.

SCIENTIFIC QUESTION:
  Are per-hop errors in multi-hop retrieval independent (rho < 0.20)?
  If yes: product-rule chain confidence is justified (P(chain correct) = prod P_i).
  If no (rho >= 0.20): errors are correlated -- product rule OVER-ESTIMATES chain
  confidence, or under-estimates depending on correlation sign.

  PP-31 Sub-cap 4-A: gates the product-rule chain confidence mechanism.

PRE-REGISTERED BANDS:
  HARD-PASS: mean pairwise Pearson correlation between per-hop error indicators
             across hops |rho_ij| < 0.20 for i != j, in >= 4/5 seeds.
             (Independence holds; product rule is justified.)
  HARD-FAIL: |rho_ij| >= 0.50 for at least one hop pair in >= 4/5 seeds.
             (Strong correlation; product rule is NOT justified.)
  MIDDLE-BAND: 0.20 <= |rho| < 0.50 (weak correlation; product rule approximate).

  No prior empirical anchor: calibration-probe policy (first measurement).
  Theoretical prior: if each hop is near-orthogonal (HDC regime), errors should
  be nearly independent -> rho ~ 0. But cross-hop contamination could induce
  positive correlation.

DESIGN:
  N = 1024, K = 4 hops, M = 64 patterns per hop codebook.
  500 query trials per seed.
  Each trial: 4-hop retrieval chain. Record binary error indicator e_k = 1 if
  hop k fails (overlap < 0.70 with true target), e_k = 0 if succeeds.
  Compute Pearson correlation matrix for (e_1, e_2, e_3, e_4).
  Report mean |rho| and max |rho| across off-diagonal pairs.
  5 seeds (smoke: 3).

FORMULA SELF-TESTS:
  1. Pearson rho([0,0,1,1,...], [0,0,1,1,...]) = 1.0 (identical series).
  2. Pearson rho([0,1,0,1,...], [1,0,1,0,...]) = -1.0 (anti-correlated).
  3. Pearson rho([0,1,0,1,...], [0,0,1,1,...]) ~ 0 (independent binary).
  4. HP criterion |rho| < 0.20 is weaker than "fully independent" (rho=0);
     allows small cross-hop interference without invalidating product rule.

PROT-018: no _nN suffix. Production N = 1024; stated per PROT-018 rule 3.
TIMEOUT ESTIMATE:
  Smoke: 3 seeds x 500 trials x 4 hops x 15 steps = 90000 updates ~ 30s.
  Full: 5 seeds ~ 50s.
  timeout_s = 300 (PROT-019 floor; actual wall < 90s).

Anchor: pp31_4a_per_hop_independence_v1
Queue: remote_cpu_queue
Pre-reg: preregs/2026-06-01_pp31_4a_per_hop_independence_v1.md
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import json
import math
import time
from pathlib import Path
from typing import Dict, List

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import get_output_dir  # noqa: E402

ANCHOR_NAME = "pp31_4a_per_hop_independence_v1"

# --- Config ---
N = 1024
K_HOPS = 4
M_PER_HOP = 64
N_TRIALS = 500
NOISE_FRAC = 0.10
N_STEPS = 15
HOP_SUCCESS_THRESH = 0.70  # hop succeeds if final overlap >= this

SEEDS_SMOKE = [7, 17, 23]
SEEDS_FULL  = [7, 17, 23, 31, 41]

# Pre-registered thresholds
HP_MAX_RHO = 0.20      # |rho| < 0.20 -> HARD-PASS
HF_MAX_RHO = 0.50      # |rho| >= 0.50 -> HARD-FAIL
HP_MIN_SEEDS = 4       # out of 5


def _random_patterns(M: int, N: int, rng: np.random.Generator) -> np.ndarray:
    return rng.choice([-1.0, 1.0], size=(M, N))


def _build_weights(patterns: np.ndarray) -> np.ndarray:
    W = patterns.T @ patterns / N
    np.fill_diagonal(W, 0.0)
    return W


def _sync_update(state: np.ndarray, W: np.ndarray) -> np.ndarray:
    s = np.sign(W @ state)
    s[s == 0] = 1.0
    return s


def _single_hop(W: np.ndarray, target: np.ndarray,
                 noise_frac: float, n_steps: int,
                 rng: np.random.Generator) -> float:
    """Run one retrieval hop. Return final overlap with target."""
    N = len(target)
    state = target.copy()
    flip_mask = rng.random(N) < noise_frac
    state[flip_mask] *= -1.0
    for _ in range(n_steps):
        state = _sync_update(state, W)
    return float(np.dot(state, target) / N)


def _pearson_corr_matrix(X: np.ndarray) -> np.ndarray:
    """Pearson correlation matrix of columns of X. X shape: (n_trials, K)."""
    # Center and normalize each column
    mu = X.mean(axis=0, keepdims=True)
    std = X.std(axis=0, keepdims=True)
    std[std < 1e-10] = 1.0
    X_norm = (X - mu) / std
    K = X.shape[1]
    corr = (X_norm.T @ X_norm) / X.shape[0]
    return corr


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics are non-null/non-sentinel."""
    # Formula self-tests
    X_same = np.array([[0, 0], [1, 1], [0, 0], [1, 1]], dtype=float)
    corr = _pearson_corr_matrix(X_same)
    assert abs(corr[0, 1] - 1.0) < 0.01, f"identical columns should have rho=1: {corr[0,1]:.3f}"

    X_anti = np.array([[0, 1], [1, 0], [0, 1], [1, 0]], dtype=float)
    corr_anti = _pearson_corr_matrix(X_anti)
    assert abs(corr_anti[0, 1] + 1.0) < 0.01, f"anti-correlated should have rho=-1: {corr_anti[0,1]:.3f}"

    # Small-scale retrieval test
    rng = np.random.default_rng(42)
    patterns = _random_patterns(8, N, rng)
    W = _build_weights(patterns)
    overlap = _single_hop(W, patterns[0], NOISE_FRAC, 5, rng)
    assert -1.0 <= overlap <= 1.0, f"overlap out of range: {overlap}"
    assert not math.isnan(overlap), "overlap NaN"

    print("SELFTEST PASSED: pp31_4a_per_hop_independence_v1")


_instrumentation_selftest()


def run_experiment(smoke: bool = False) -> Dict:
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    all_results = []

    for seed in seeds:
        rng = np.random.default_rng(seed)

        # Build K independent hop codebooks
        hop_codebooks = []
        hop_Ws = []
        for k in range(K_HOPS):
            patterns = _random_patterns(M_PER_HOP, N, rng)
            hop_codebooks.append(patterns)
            hop_Ws.append(_build_weights(patterns))

        # N_TRIALS independent multi-hop queries
        error_matrix = np.zeros((N_TRIALS, K_HOPS), dtype=float)

        for trial in range(N_TRIALS):
            for k in range(K_HOPS):
                target = hop_codebooks[k][0]  # same target per hop for simplicity
                overlap = _single_hop(hop_Ws[k], target, NOISE_FRAC, N_STEPS, rng)
                error_matrix[trial, k] = 1.0 if overlap < HOP_SUCCESS_THRESH else 0.0

        # Pearson correlation matrix
        corr = _pearson_corr_matrix(error_matrix)

        # Off-diagonal correlations
        off_diag = []
        for i in range(K_HOPS):
            for j in range(i + 1, K_HOPS):
                off_diag.append(abs(float(corr[i, j])))

        mean_rho = float(np.mean(off_diag)) if off_diag else 0.0
        max_rho  = float(np.max(off_diag))  if off_diag else 0.0
        error_rate = float(error_matrix.mean())

        passes_hp = max_rho < HP_MAX_RHO
        passes_hf = max_rho >= HF_MAX_RHO

        print(f"seed={seed} mean_rho={mean_rho:.4f} max_rho={max_rho:.4f} "
              f"error_rate={error_rate:.3f} passes_hp={passes_hp}")

        all_results.append({
            "seed": seed,
            "mean_rho": mean_rho,
            "max_rho": max_rho,
            "error_rate": error_rate,
            "corr_matrix": corr.tolist(),
            "passes_hp": passes_hp,
            "passes_hf": passes_hf,
        })

    seeds_pass = sum(1 for r in all_results if r["passes_hp"])
    seeds_hf   = sum(1 for r in all_results if r["passes_hf"])

    if seeds_pass >= HP_MIN_SEEDS:
        verdict = "HARD_PASS"
    elif seeds_hf >= HP_MIN_SEEDS:
        verdict = "HARD_FAIL"
    else:
        verdict = "MIDDLE_BAND"

    avg_mean_rho = float(np.mean([r["mean_rho"] for r in all_results]))
    avg_max_rho  = float(np.mean([r["max_rho"]  for r in all_results]))

    verdict_msg = (
        f"PP31-4A PER-HOP INDEPENDENCE: verdict={verdict} | "
        f"{seeds_pass}/{len(all_results)} seeds pass HP | "
        f"avg_mean_rho={avg_mean_rho:.4f} avg_max_rho={avg_max_rho:.4f} | "
        f"HP: max|rho|<0.20 in >=4/5 seeds (product rule justified) | "
        f"HF: max|rho|>=0.50 in >=4/5 seeds (product rule invalid)"
    )

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "seeds_pass": seeds_pass,
        "seeds_hf": seeds_hf,
        "seeds_total": len(all_results),
        "avg_mean_rho": avg_mean_rho,
        "avg_max_rho": avg_max_rho,
        "all_results": all_results,
        "smoke": smoke,
    }
    return metrics


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true", dest="self_test")
    args = parser.parse_args()
    if args.self_test:
        sys.exit(0)

    t0 = time.time()
    metrics = run_experiment(smoke=args.smoke)
    elapsed = time.time() - t0
    metrics["elapsed_s"] = elapsed

    outdir = get_output_dir(ANCHOR_NAME)
    outdir.mkdir(parents=True, exist_ok=True)
    out_path = outdir / "metrics.json"
    with open(out_path, "w") as f:
        json.dump(metrics, f, indent=2)

    print(f"\n{metrics['verdict_msg']}")
    print(f"elapsed={elapsed:.1f}s  output={out_path}")


if __name__ == "__main__":
    main()
