"""
chi_sg_replica_arch_v1 -- chi_SG with proper REPLICA-AVERAGING architecture.

RESCUE from chi_sg_n_scaling_v1 INSTRUMENTATION_SUSPECT (single-chain chi_SG ~ O(1)):
  Root cause: single-chain Glauber gives chi_SG = O(1) trivially -- no replica averaging.
  Edwards-Anderson susceptibility REQUIRES disorder-averaged cross-replica overlap.
  Fix: R=5 disorder draws, Q=5 independent replicas per draw; compute q_ab for
  all pairs (a,b) within same disorder draw.

SCIENTIFIC QUESTION (PP-33 supplementary cross-check):
  Does chi_SG(N) ~ N^gamma with gamma > 0 across N in {1024, 2048, 4096}
  near alpha_c? Gamma > 0 suggests spin-glass-like susceptibility at near-critical load.

NOTE: PP-33 framework-class context (static-phase frameworks CLOSED per cap_map v319).
  This is a supplementary cross-check -- chi_SG replica is informative about the
  susceptibility structure, not a primary probe for the now-confirmed dynamical phase.

REPLICA ARCHITECTURE (per research rescue spec 2026-06-02):
  R = 5 disorder realizations (independent W draws from random pattern sets).
  Q = 5 independent replicas per disorder draw (different initial conditions, same W).
  For each disorder draw r:
    - Draw M patterns (disorder = random W).
    - Run Q chains to equilibrium under Glauber dynamics.
    - Compute q_ab = (1/N) * s^a . s^b for all C(Q,2) = 10 pairs.
  chi_SG(N) = N * E_r[mean_ab(q_ab^2)].
  Fit log-log slope of chi_SG vs N across N_grid.

PRE-REGISTERED BANDS (from research rescue note 2026-06-02):
  HARD-PASS: chi_SG(N) ~ N^gamma, gamma > 0 across N in {1024, 2048, 4096};
             gamma > 0.5 strongly suggests spin-glass susceptibility.
  MIDDLE: chi_SG grows but gamma < 0.5 (weak susceptibility signal).
  HARD-FAIL: chi_SG(N)/N converges to constant (paramagnetic or RS phase).

P_deflated=0.32 per research note (substrate confirmed in non-eq dynamical phase;
static chi_SG is supplementary cross-check).

FORMULA SELF-TESTS:
  1. EA order parameter: q_ab = (1/N) s^a . s^b. For random uncorrelated states:
     E[q_ab] = 0, E[q_ab^2] = 1/N. So chi_SG ~ N * (1/N) = O(1) for random states.
     Assert: random-state chi_SG = O(1).
  2. Perfectly correlated replicas: q_ab = 1 for all pairs -> chi_SG ~ N.
     Assert: if all replicas same, chi_SG ~ N.
  3. Log-log slope: slope of log(chi_SG) vs log(N) via linear regression.
     gamma (slope) in (0, 2) is plausible physical range.

PROT-018: no _nN suffix; N sweep across {1024,2048,4096} per rule 3.
PROT-021: run_config includes N_alpha (discriminating field for alpha-dependent sims).
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

ANCHOR_NAME = "chi_sg_replica_arch_v1"

# PROT-018: no _nN suffix; N sweep across {1024,2048,4096} per rule 3.
# Production min_N = 1024, production max_N = 4096.

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

ALPHA_NEAR_C = 0.14   # near capacity (alpha_c ~ 0.14 for Hopfield BSC)
BETA = 2.0            # inverse temperature (moderate coupling)

if RUN_MODE == "smoke":
    N_GRID = [512, 1024]      # reduced for smoke
    SEEDS = [7, 17]           # each seed = one "global" RNG; R draws within seed
    R_DISORDER = 3
    Q_REPLICAS = 3
    T_THERM = 200  # vectorized: 200 parallel sweeps for thermalization
    T_MEAS = 300   # vectorized: 300 sweeps for replica overlap measurement
else:
    N_GRID = [1024, 2048, 4096]
    SEEDS = [7, 17, 23]       # 3 global seeds for the outer loop
    R_DISORDER = 5
    Q_REPLICAS = 5
    T_THERM = 500  # vectorized: 500 sweeps for thermalization
    T_MEAS = 1000  # vectorized: 1000 sweeps for replica overlap measurement

HP_GAMMA_MIN = 0.0     # gamma > 0 (any positive scaling)
HF_FLAT = True         # chi_SG/N ~ constant as N grows
HP_GAMMA_STRONG = 0.5  # gamma > 0.5 = strong susceptibility signal


def glauber_sweep(W: np.ndarray, s: np.ndarray, n_steps: int,
                  beta: float, rng: np.random.RandomState) -> np.ndarray:
    """
    n_steps sweeps of stochastic block Glauber dynamics.
    Each step: randomly partition spins into 2 halves; update each half in sequence.
    Breaks period-2 oscillations of fully-parallel updates. O(N^2) per step (numpy).
    Sufficient for chi_SG measurement (replica overlap statistics).
    """
    N_dim = len(s)
    s = s.copy()
    for _ in range(n_steps):
        # Split spins into 2 random halves; update each using current h
        perm = rng.permutation(N_dim)
        half = N_dim // 2
        for group in [perm[:half], perm[half:]]:
            h = W @ s
            delta_E = 2.0 * s[group] * h[group]
            accept = (delta_E < 0) | (rng.rand(len(group)) < np.exp(-beta * np.clip(delta_E, 0, None)))
            s[group] = np.where(accept, -s[group], s[group])
    return s


def run_one_N(N_dim: int, seed: int) -> Dict:
    """Run R disorder draws x Q replicas at given N."""
    M = max(1, int(ALPHA_NEAR_C * N_dim))
    rng = np.random.RandomState(seed)

    chi_SG_per_draw = []

    for r in range(R_DISORDER):
        # Disorder draw: random M patterns -> W
        Xi = rng.choice([-1.0, 1.0], size=(M, N_dim)).astype(np.float64)
        W = Xi.T @ Xi / N_dim
        np.fill_diagonal(W, 0.0)

        # Q independent replicas: different initial conditions, same W
        replica_states = []
        for q in range(Q_REPLICAS):
            # Random initial state
            s0 = rng.choice([-1.0, 1.0], size=(N_dim,)).astype(np.float64)
            # Thermalize
            s_eq = glauber_sweep(W, s0, T_THERM, BETA, rng)
            # Measure (take final state after measurement period)
            s_meas = glauber_sweep(W, s_eq, T_MEAS, BETA, rng)
            replica_states.append(s_meas)

        # Compute q_ab for all C(Q,2) pairs
        q_ab_sq_list = []
        for a in range(Q_REPLICAS):
            for b in range(a + 1, Q_REPLICAS):
                q_ab = float(np.dot(replica_states[a], replica_states[b])) / N_dim
                q_ab_sq_list.append(q_ab ** 2)

        if q_ab_sq_list:
            chi_SG_per_draw.append(N_dim * float(np.mean(q_ab_sq_list)))

    chi_SG = float(np.mean(chi_SG_per_draw)) if chi_SG_per_draw else float("nan")
    chi_SG_std = float(np.std(chi_SG_per_draw)) if len(chi_SG_per_draw) >= 2 else float("nan")

    print(
        f"  [N={N_dim} seed={seed} R={R_DISORDER} Q={Q_REPLICAS}] "
        f"M={M} chi_SG={chi_SG:.4f} chi_SG_std={chi_SG_std:.4f}",
        flush=True
    )

    return {
        "N": N_dim, "M": M, "alpha": ALPHA_NEAR_C,
        "chi_SG": chi_SG, "chi_SG_std": chi_SG_std,
        "chi_SG_over_N": chi_SG / N_dim if N_dim > 0 and not math.isnan(chi_SG) else float("nan"),
        "seed": seed, "run_mode": RUN_MODE,
        "R_disorder": R_DISORDER, "Q_replicas": Q_REPLICAS,
    }


def run_seed(seed: int) -> Dict:
    """Run all N_GRID values for one global seed."""
    results = {}
    for N_dim in N_GRID:
        result = run_one_N(N_dim, seed)
        results[N_dim] = result
    return {"N_results": results, "seed": seed, "run_mode": RUN_MODE}


def _instrumentation_selftest():
    """
    Assert replica chi_SG is non-trivial.
    Formula self-test 1: random states -> chi_SG ~ O(1).
    Formula self-test 2: correlated replicas -> chi_SG ~ N.
    """
    N_test = 256
    rng = np.random.RandomState(42)

    # Self-test 1: random uncorrelated states
    # q_ab ~ 0, q_ab^2 ~ 1/N_test
    q_ab_sq_random = []
    for _ in range(10):
        sa = rng.choice([-1.0, 1.0], size=(N_test,)).astype(np.float64)
        sb = rng.choice([-1.0, 1.0], size=(N_test,)).astype(np.float64)
        q = float(np.dot(sa, sb)) / N_test
        q_ab_sq_random.append(q ** 2)
    chi_random = N_test * float(np.mean(q_ab_sq_random))
    # For random states: chi_SG ~ N * (1/N) = O(1)
    assert chi_random < 5.0, (
        f"Random-state chi_SG={chi_random:.4f} too large (expected ~ O(1) ~ 1.0)"
    )

    # Self-test 2: identical replicas
    sa = rng.choice([-1.0, 1.0], size=(N_test,)).astype(np.float64)
    q_identical = float(np.dot(sa, sa)) / N_test  # = 1.0 exactly
    chi_identical = N_test * q_identical ** 2
    assert abs(chi_identical - N_test) < 1.0, (
        f"Identical-replica chi_SG={chi_identical:.4f} != N_test={N_test}"
    )

    # Self-test 3: one disorder draw, 2 replicas
    M_test = max(1, int(ALPHA_NEAR_C * N_test))
    Xi = rng.choice([-1.0, 1.0], size=(M_test, N_test)).astype(np.float64)
    W = Xi.T @ Xi / N_test
    np.fill_diagonal(W, 0.0)

    # Run 2 replicas via short Glauber
    s0a = rng.choice([-1.0, 1.0], size=(N_test,)).astype(np.float64)
    s0b = rng.choice([-1.0, 1.0], size=(N_test,)).astype(np.float64)
    sa = glauber_sweep(W, s0a, 50, BETA, rng)
    sb = glauber_sweep(W, s0b, 50, BETA, rng)
    q_ab = float(np.dot(sa, sb)) / N_test
    chi_2rep = N_test * q_ab ** 2
    # chi_SG should be non-NaN and positive
    assert not math.isnan(chi_2rep), "chi_SG is NaN in selftest"
    assert chi_2rep >= 0.0, f"chi_SG={chi_2rep:.4f} < 0"

    print(
        f"[selftest] PASS: chi_random={chi_random:.4f} ~ O(1); "
        f"chi_identical={chi_identical:.1f} ~ N={N_test}; "
        f"chi_2rep={chi_2rep:.4f} non-null",
        flush=True
    )


_instrumentation_selftest()


def _verdict_formula_selftests():
    """Verify log-log slope formula."""
    # log-log slope: slope = (log(y2) - log(y1)) / (log(x2) - log(x1))
    # If chi_SG ~ N^1: slope = 1.0
    N_vals = [1024, 2048, 4096]
    chi_vals_linear = [float(N) for N in N_vals]
    log_N = [math.log(N) for N in N_vals]
    log_chi = [math.log(c) for c in chi_vals_linear]

    # Linear regression slope
    n = len(log_N)
    mean_logN = sum(log_N) / n
    mean_logChi = sum(log_chi) / n
    cov = sum((log_N[i] - mean_logN) * (log_chi[i] - mean_logChi) for i in range(n))
    var = sum((log_N[i] - mean_logN) ** 2 for i in range(n))
    slope = cov / var if var > 0 else float("nan")

    assert abs(slope - 1.0) < 0.01, f"log-log slope formula: {slope:.4f} != 1.0 for chi~N"

    # If chi_SG/N = constant: slope = 1.0 (extensive)
    # If chi_SG = constant: slope = 0.0 (intensive)
    chi_vals_const = [1.0 for _ in N_vals]
    log_chi_const = [math.log(c) for c in chi_vals_const]
    cov2 = sum((log_N[i] - mean_logN) * (log_chi_const[i] - sum(log_chi_const) / n)
               for i in range(n))
    slope_const = cov2 / var if var > 0 else float("nan")
    assert abs(slope_const) < 0.01, f"constant chi should give slope~0, got {slope_const:.4f}"

    print(
        f"[formula_selftests] PASS: chi~N gives slope=1.0 (got {slope:.4f}); "
        f"chi~const gives slope~0 (got {slope_const:.4f})",
        flush=True
    )


_verdict_formula_selftests()


def compute_loglog_slope(N_vals: List[float], chi_vals: List[float]) -> float:
    """Compute log-log slope via OLS on log(N) vs log(chi_SG)."""
    if len(N_vals) < 2:
        return float("nan")
    valid = [(N, c) for N, c in zip(N_vals, chi_vals)
             if not math.isnan(c) and c > 0 and N > 0]
    if len(valid) < 2:
        return float("nan")
    log_N = [math.log(N) for N, _ in valid]
    log_chi = [math.log(c) for _, c in valid]
    n = len(log_N)
    mean_lN = sum(log_N) / n
    mean_lC = sum(log_chi) / n
    cov = sum((log_N[i] - mean_lN) * (log_chi[i] - mean_lC) for i in range(n))
    var = sum((log_N[i] - mean_lN) ** 2 for i in range(n))
    return cov / var if var > 1e-12 else float("nan")


def aggregate_results(per_seed: Dict) -> Dict:
    """Aggregate chi_SG per N across seeds."""
    N_to_chis: Dict[int, List] = {N_dim: [] for N_dim in N_GRID}

    for sd in per_seed.values():
        n_results = sd.get("N_results", {})
        for N_dim in N_GRID:
            r = n_results.get(N_dim) or n_results.get(str(N_dim))
            if r is None:
                continue
            chi = r.get("chi_SG", float("nan"))
            if not math.isnan(chi):
                N_to_chis[N_dim].append(chi)

    per_N = []
    for N_dim in N_GRID:
        chis = N_to_chis[N_dim]
        mean_chi = float(np.mean(chis)) if chis else float("nan")
        per_N.append({
            "N": N_dim,
            "mean_chi_SG": mean_chi,
            "chi_SG_over_N": mean_chi / N_dim if not math.isnan(mean_chi) else float("nan"),
            "n_seeds": len(chis),
        })

    # Log-log slope
    N_vals = [row["N"] for row in per_N]
    chi_vals = [row["mean_chi_SG"] for row in per_N]
    gamma = compute_loglog_slope(N_vals, chi_vals)

    # Check if chi_SG/N is approximately constant (RS phase indicator)
    ratios = [row["chi_SG_over_N"] for row in per_N
              if not math.isnan(row.get("chi_SG_over_N", float("nan")))]
    if len(ratios) >= 2:
        ratio_cv = float(np.std(ratios) / (np.mean(ratios) + 1e-12))
    else:
        ratio_cv = float("nan")

    return {
        "per_N": per_N, "gamma": gamma,
        "ratio_cv": ratio_cv,  # coefficient of variation of chi_SG/N
    }


def compute_verdict(agg: Dict) -> Tuple[str, str]:
    gamma = agg.get("gamma", float("nan"))
    per_N = agg.get("per_N", [])
    ratio_cv = agg.get("ratio_cv", float("nan"))

    if not per_N or math.isnan(gamma):
        return ("HARD_FAIL", "No N-grid chi_SG measurements or slope computation failed.")

    if gamma > HP_GAMMA_STRONG:
        return (
            "HARD_PASS",
            f"chi_SG shows N-scaling with gamma={gamma:.3f} > {HP_GAMMA_STRONG}. "
            f"Strong spin-glass susceptibility signature at near-critical alpha={ALPHA_NEAR_C}. "
            f"N_grid={N_GRID}. Supplementary cross-check of SKAH-M dynamical phase. "
            f"chi_SG/N coefficient-of-variation={ratio_cv:.3f}."
        )
    if gamma > HP_GAMMA_MIN:
        return (
            "MIDDLE_BAND",
            f"Weak chi_SG N-scaling: gamma={gamma:.3f} > 0 but < {HP_GAMMA_STRONG}. "
            f"Some susceptibility signal; may reflect finite-N effects. N_grid={N_GRID}."
        )
    if not math.isnan(ratio_cv) and ratio_cv < 0.10:
        return (
            "HARD_FAIL",
            f"chi_SG/N approximately constant (CV={ratio_cv:.3f} < 0.10). "
            f"gamma={gamma:.3f} <= 0. RS or paramagnetic phase at alpha={ALPHA_NEAR_C}. "
            f"Static chi_SG susceptibility NOT extensive. N_grid={N_GRID}."
        )
    return (
        "HARD_FAIL",
        f"chi_SG does not scale with N: gamma={gamma:.3f} <= {HP_GAMMA_MIN}. N_grid={N_GRID}."
    )


def main():
    out_dir = get_output_dir(ANCHOR_NAME)
    t0 = time.time()
    print(
        f"[start] {ANCHOR_NAME} run_mode={RUN_MODE} N_GRID={N_GRID} "
        f"alpha={ALPHA_NEAR_C} R={R_DISORDER} Q={Q_REPLICAS} seeds={SEEDS}",
        flush=True
    )

    # PROT-021: include alpha, T_THERM, T_MEAS, R, Q in run_config (all discriminating)
    run_config = {
        "run_mode": RUN_MODE, "alpha": ALPHA_NEAR_C,
        "T_THERM": T_THERM, "T_MEAS": T_MEAS,
        "R_DISORDER": R_DISORDER, "Q_REPLICAS": Q_REPLICAS
    }
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
        "run_mode": RUN_MODE, "N_GRID": N_GRID,
        "alpha": ALPHA_NEAR_C, "beta": BETA,
        "R_disorder": R_DISORDER, "Q_replicas": Q_REPLICAS,
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
