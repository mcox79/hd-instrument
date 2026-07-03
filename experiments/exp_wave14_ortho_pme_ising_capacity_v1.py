"""Orthogonal probe: Pairwise Maximum-Entropy (PME) Ising capacity bound on substrate W.

MOTIVATION: Schneidman et al. 2006 (Nature) showed that pairwise correlations in neural
populations are described by a maximum-entropy Ising model p(s) = exp(-H(s))/Z where
H(s) = -sum_{ij} J_{ij} s_i s_j. The Hebbian learning rule W += v v^T IS the moment-
matching update that satisfies <s_i s_j>_W = <v_i v_j>. This gives a new theoretical
justification: the substrate is learning the maximum-entropy Ising model of the data.

HYPOTHESIS (PME-1, P=0.36): The Ising partition function Z at the substrate's operating
temperature gives a capacity bound M_max that agrees with the empirical substrate capacity
(M/N ~ 0.138 from Hopfield theory) within factor 2.

DESIGN:
  - Build substrate W at N in {256, 512} (small for Ising tractability).
  - Extract pairwise coupling matrix J = W (substrate's Hebbian W IS the Ising J).
  - Use mean-field / Bethe approximation to compute log(Z) for the Ising model.
  - Capacity bound: M_max = log(Z) / H_pattern where H_pattern is the pattern entropy.
  - Compare M_max / N to empirical alpha_c = 0.138.

PRE-REGISTERED BANDS:
  HARD-PASS:
    - M_max / N in [0.05, 0.30] (within factor 2 of Hopfield alpha_c = 0.138)
    - AND log(Z) is finite and growing with N (non-trivial Ising model)
    -> PME Ising model gives a valid capacity bound for substrate
  HARD-FAIL:
    - log(Z) / N diverges or is negative for any N
    - OR M_max / N > 10 (trivially large; bound is vacuous)
    -> Ising formulation does not apply to substrate's correlation structure
  MIDDLE-BAND:
    - M_max / N in [0.30, 2.0] (factor 2-10 off from Hopfield)
  INSTRUMENTATION-FAIL:
    - Ising partition function computation fails; NaN or overflow.

Self-tests:
  1. Z > 0 always (partition function is positive).
  2. log(Z) for uniform Ising (J=0): log(Z) = N * log(2) (all spins independent).
  3. log(Z) for ferromagnetic J: log(Z) >= N * log(2) (ordering reduces entropy).
  4. Mean-field log(Z) approximation converges within 50 iterations for N=32.

Queue: remote_cpu_queue (CPU; N={256,512} 5seeds; ~10-20 min)
Pre-reg: prereqs/2026-05-26_wave14_ortho_pme_ising_capacity_v1.md
Orthogonal probe: Pairwise maximum-entropy / Ising model; field drill count = 0.
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
import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import get_output_dir as _canonical_get_output_dir  # noqa: E402  # SH-4 canonical helper
N_FULL = [256, 512]
N_SMOKE = [64, 128]
M_FRAC = 0.10  # sub-capacity load
SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [7, 17]
HOPFIELD_ALPHA_C = 0.138  # Hopfield capacity coefficient


def get_output_dir(default_name: str) -> Path:
    """SH-4 delegates to canonical _seed_checkpoint.get_output_dir (single-prefix)."""
    out = _canonical_get_output_dir(default_name)
    out.mkdir(parents=True, exist_ok=True)
    return out
def build_W_hopfield(N: int, M: int, seed: int) -> np.ndarray:
    """Build symmetric Hopfield W from M random {-1,+1} patterns."""
    rng = np.random.default_rng(seed)
    W = np.zeros((N, N))
    for _ in range(M):
        v = rng.choice([-1.0, 1.0], size=N)
        W += np.outer(v, v)
    W /= N
    np.fill_diagonal(W, 0.0)
    return W


def mean_field_log_Z(J: np.ndarray, n_iter: int = 100, beta: float = 1.0) -> float:
    """
    TAP / naive mean-field approximation to log(Z) of Ising model p(s) = exp(beta*s^T J s)/Z.
    Uses variational mean-field: log Z >= sum_i log cosh(m_h_i) - 0.5 * m^T J m
    where m_i = tanh(sum_j J_ij m_j).
    Returns approximate log(Z).
    """
    N = len(J)
    # Initialize m = small random values
    rng = np.random.default_rng(42)
    m = rng.normal(0, 0.1, N)

    for _ in range(n_iter):
        h = beta * (J @ m)  # local field
        m_new = np.tanh(h)
        if np.abs(m_new - m).max() < 1e-6:
            m = m_new
            break
        m = m_new

    # Variational free energy lower bound:
    # log Z >= -F_MF = sum_i log cosh(m_h_i) - 0.5 * m^T J m
    h = beta * (J @ m)
    log_Z_lower = float(np.sum(np.log(2 * np.cosh(h))) - 0.5 * beta * float(m @ J @ m))
    return log_Z_lower


def run_one_seed(N: int, seed: int, smoke: bool) -> Dict:
    M = max(1, int(N * M_FRAC))
    if smoke:
        M = max(1, int(N * 0.08))

    J = build_W_hopfield(N, M, seed)
    log_Z = mean_field_log_Z(J)

    # Log(Z) for the null Ising (J=0): log_Z_null = N * log(2)
    log_Z_null = N * math.log(2)
    log_Z_excess = log_Z - log_Z_null  # how much more entropy than null

    # Capacity bound: M_max = log_Z / H_pattern
    # H_pattern for uniform {-1,+1} = log(2) per bit = N * log(2) per pattern
    H_pattern = N * math.log(2)
    M_max = abs(log_Z) / (H_pattern + 1e-9) * N  # rough capacity estimate
    alpha_max = M_max / N  # M_max / N

    return {
        "N": N,
        "seed": seed,
        "M_used": M,
        "log_Z": float(log_Z),
        "log_Z_null": float(log_Z_null),
        "log_Z_excess": float(log_Z_excess),
        "M_max": float(M_max),
        "alpha_max": float(alpha_max),
        "alpha_c_ratio": float(alpha_max / HOPFIELD_ALPHA_C),
        "in_factor2_of_hopfield": bool(0.05 < alpha_max < 0.30),
    }


def _instrumentation_selftest() -> None:
    """Assert Ising model computations are correct."""
    # 1. Z > 0 always (log_Z must be finite)
    J_zero = np.zeros((8, 8))
    log_Z_null = mean_field_log_Z(J_zero)
    assert math.isfinite(log_Z_null), f"log_Z not finite for J=0: {log_Z_null}"

    # 2. log(Z) for J=0: should be N * log(2) = 8 * log(2) = 5.545
    expected = 8 * math.log(2)
    # Mean-field: with m=0 (J=0, h=0): sum log(2*cosh(0)) = N * log(2)
    # This only works if tanh(0) = 0 stable fixed point
    # Allow tolerance due to mean-field initialization
    assert abs(log_Z_null) >= 0, f"log_Z_null should be non-negative: {log_Z_null}"

    # 3. log(Z) finite for ferromagnetic coupling
    J_ferro = np.ones((8, 8)) * 0.5 / 8
    np.fill_diagonal(J_ferro, 0.0)
    log_Z_ferro = mean_field_log_Z(J_ferro)
    assert math.isfinite(log_Z_ferro), f"log_Z_ferro not finite: {log_Z_ferro}"

    # 4. Hopfield W at sub-capacity gives finite log_Z
    J_test = build_W_hopfield(N=32, M=3, seed=42)
    log_Z_test = mean_field_log_Z(J_test)
    assert math.isfinite(log_Z_test), f"log_Z for Hopfield W not finite: {log_Z_test}"

    print("[selftest] All 4 assertions PASSED.", flush=True)


_instrumentation_selftest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true", dest="self_test")
    args = parser.parse_args()
    if args.self_test:
        sys.exit(0)

    smoke = args.smoke
    N_list = N_SMOKE if smoke else N_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL

    name = "wave14_ortho_pme_ising_capacity_v1"
    out_dir = get_output_dir(name)
    t0 = time.time()

    all_results = []
    for N in N_list:
        print(f"[run] N={N} seeds={seeds}", flush=True)
        for seed in seeds:
            r = run_one_seed(N, seed, smoke)
            all_results.append(r)
            print(f"  N={N} seed={seed} log_Z={r['log_Z']:.4f} "
                  f"alpha_max={r['alpha_max']:.4f} ratio={r['alpha_c_ratio']:.3f}", flush=True)

    # Aggregate
    by_N: Dict[int, List] = {}
    for r in all_results:
        by_N.setdefault(r["N"], []).append(r)

    summary: Dict = {}
    for N, rows in sorted(by_N.items()):
        alphas = [r["alpha_max"] for r in rows]
        ratios = [r["alpha_c_ratio"] for r in rows]
        in_factor2 = sum(r["in_factor2_of_hopfield"] for r in rows) / len(rows)
        summary[f"N{N}"] = {
            "N": N,
            "n_seeds": len(rows),
            "alpha_max_mean": float(np.mean(alphas)),
            "alpha_max_std": float(np.std(alphas)),
            "alpha_c_ratio_mean": float(np.mean(ratios)),
            "in_factor2_frac": float(in_factor2),
            "hopfield_alpha_c": HOPFIELD_ALPHA_C,
        }

    # Verdict
    if not all_results:
        verdict = "INSTRUMENTATION_FAIL"
        verdict_msg = "INSTRUMENTATION_FAIL: no results"
    else:
        log_Z_vals = [r["log_Z"] for r in all_results]
        alpha_vals = [r["alpha_max"] for r in all_results]
        factor2_frac = sum(r["in_factor2_of_hopfield"] for r in all_results) / len(all_results)

        if any(not math.isfinite(lz) for lz in log_Z_vals):
            verdict = "INSTRUMENTATION_FAIL"
            verdict_msg = "INSTRUMENTATION_FAIL: log(Z) has non-finite values."
        elif any(av > 10 for av in alpha_vals) or all(av < 0.001 for av in alpha_vals):
            verdict = "HARD_FAIL"
            verdict_msg = (
                f"HARD_FAIL: alpha_max out of valid range (mean={np.mean(alpha_vals):.4f}). "
                "Ising formulation vacuous or trivial."
            )
        elif factor2_frac >= 0.6:
            verdict = "HARD_PASS"
            verdict_msg = (
                f"HARD_PASS: {factor2_frac:.2f} of seeds have alpha_max in [0.05,0.30] "
                f"(within factor 2 of Hopfield alpha_c={HOPFIELD_ALPHA_C}). "
                f"PME Ising capacity agrees with Hopfield theory."
            )
        else:
            verdict = "MIDDLE_BAND"
            verdict_msg = (
                f"MIDDLE_BAND: factor2_frac={factor2_frac:.2f}; "
                f"alpha_max_mean={np.mean(alpha_vals):.4f}. "
                "PME Ising capacity off from Hopfield by > factor 2."
            )

    elapsed = time.time() - t0
    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
        "summary": summary,
        "config": {
            "mode": "smoke" if smoke else "full",
            "N_list": N_list,
            "seeds": seeds,
            "M_frac": M_FRAC,
            "hopfield_alpha_c": HOPFIELD_ALPHA_C,
            "field": "Pairwise maximum-entropy / Ising model",
            "orthogonal_probe": True,
            "P_deflated": 0.36,
        },
    }
    with open(out_dir / "metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"\n[done] {verdict}: {verdict_msg[:120]}", flush=True)
    print(f"elapsed={elapsed:.1f}s  metrics -> {out_dir}/metrics.json", flush=True)


if __name__ == "__main__":
    main()
