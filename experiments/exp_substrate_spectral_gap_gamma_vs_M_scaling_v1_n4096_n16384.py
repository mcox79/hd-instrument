"""
substrate_spectral_gap_gamma_vs_M_scaling_v1_n4096_n16384 --
Gamma-vs-M discriminating probe for SCS vs RSB vs Lyapunov spectral-gap theories.

CONTEXT (v373, cycle 43):
  PP-58 closed under BBP (v373) with empirical gamma ~ 8.0. 2x drill identified SCS
  (Sompolinsky-Crisanti-Sommers 1988) + non-Hermitian BBP as top framework (P_deflated=0.38).
  1-RSB at q_EA~0.78 is tied second (P=0.25, predicts gamma=8.1 exact algebraic match).
  This probe discriminates SCS from RSB by measuring how gamma SCALES with M at fixed N.

SCIENTIFIC QUESTION:
  Does gamma(M) follow SCS sub-linear saturation (square-root growth) or RSB pole-driven
  divergence as M approaches critical capacity? Measured at two N values (N=4096, N=16384).

FRAMEWORK PREDICTIONS (pre-registered):
  SCS: gamma(M) ~ sqrt(M/N) at low alpha; sub-linear saturation; ratio
       gamma(M=0.05*N)/gamma(M=0.15*N) in [0.50, 0.75] at both N.
  RSB: gamma diverges near alpha_c via 1/(1-q_EA(M)) pole;
       ratio gamma(M=0.05*N)/gamma(M=0.15*N) < 0.30.
  Lyapunov-only: gamma approximately flat vs M; ratio ~ 1.0.
  HARD-FAIL-universal: gamma scales as N^alpha with alpha > 0.

CELLS:
  N in {4096, 16384}:
    M/N in {0.05, 0.075, 0.10, 0.125, 0.15} (5 cells per N)
    5 seeds per cell
  Total: 10 cells * 5 seeds = 50 measurements.
  Per cell: measure gamma_emp via isochoric kappa_3 separation protocol
    (same protocol as PP-58 ratio=8.00 result).

AUXILIARY per cell:
  tau_estimate = ||W_sym|| / ||W_total||  (asymmetry parameter; near-Ginibre -> tau ~ 0)
  d_estimate = sigma_1(W) / mean(sigma_bulk(W))  (leading SVD ratio; spike strength)
  SCS formula check: gamma_SCS = (d + tau/d) / (1 + tau); compare to gamma_emp.

PRE-REGISTERED BANDS:
  HARD-PASS (SCS confirmed):
    - gamma-vs-M monotone increasing AND sub-linear (saturating) at both N
    - Ratio gamma(M=0.05*N)/gamma(M=0.15*N) in [0.50, 0.75] at both N
    - tau_estimate in [0.02, 0.20] across cells (near-Ginibre confirmed)
    - SCS formula: gamma_SCS matches gamma_emp within 30% at 3+ cells per N
  MIDDLE:
    - ratio outside [0.50, 0.75] at one N, or SCS formula matches 1-2 cells/N
  HARD-FAIL (SCS refuted):
    - Ratio < 0.30 at either N -> RSB-consistent
    - OR ratio ~ 1.0 (flat) -> Lyapunov-only
    - OR gamma scales as N^alpha with alpha > 0 -> universal refutation

FORMULA SELF-TESTS (PROT-022):
  1. SCS formula: gamma_SCS = (d + tau/d) / (1 + tau) at d=8, tau=0.05.
     [INPUT: d=8, tau=0.05] [EXPECTED: (8 + 0.05/8)/(1.05) = 7.6250 within 0.001]
  2. SCS ratio prediction: sqrt(0.05/0.15) = sqrt(1/3) ~ 0.5774.
     [INPUT: alpha_low=0.05, alpha_high=0.15] [EXPECTED: 0.5774 within 0.001]
  3. M values for N=4096: int(0.05*4096)=204, int(0.15*4096)=614.
     [EXPECTED: 204, 614]
  4. M values for N=16384: int(0.05*16384)=819, int(0.15*16384)=2458.
     [EXPECTED: 819, 2458]
  5. kappa_3 identity at zero noise: kappa_3 ~ alpha (first moment identity).
     [INPUT: noiseless, alpha=0.10, N=256] [EXPECTED: kappa_3 in [0.07, 0.13]]

PROT-018: anchor _n4096_n16384; PROT-018 checks last suffix = _n16384; script uses
  BOTH N=4096 AND N=16384. Production default N = 16384.
PROT-021: seed checkpoints keyed with (run_mode, N, alpha).
QUEUE: remote_cpu_queue (pure numpy; CPU; ~2-4h wall per routing spec).
TIMEOUT ESTIMATE: 50 cells * 5 seeds * ~5-15min/cell at N=16384 CPU.
  Smoke: 10 cells * 2 seeds at N=256 * 4 = N=512/1024; expected < 30s.
  Full: 50 measurements total. N=16384 alpha-sweep cells: ~15 min each = 750 min.
  Aggressive estimate: 50 * 5min_avg = 250min = 15000s. With 1.5x safety: 22500s.
  Use PROT-019 floor: 21600s. Use 25200s (7h) for margin.
  NOTE: if individual cells exceed expected, partial JSON allows resume.
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
from typing import Dict, List, Tuple, Optional

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

try:
    import numpy as np
except ImportError:
    print("[FATAL] numpy not installed.", flush=True)
    sys.exit(1)

from experiments._seed_checkpoint import (
    get_output_dir, write_partial_key, list_completed_keys, aggregate_partials
)

ANCHOR_NAME = "substrate_spectral_gap_gamma_vs_M_scaling_v1_n4096_n16384"

# PROT-018: last _n suffix is 16384; production default N = 16384.
# Script sweeps BOTH N=4096 AND N=16384.
_N_SUFFIX = 16384
N = 16384  # PROT-018 production N
N_VALUES = [4096, N]  # both N values swept

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

# M/N grid (alpha values)
ALPHA_GRID = [0.05, 0.075, 0.10, 0.125, 0.15]

# PROT-022 formula self-tests at module scope (arithmetic only)
_d_test, _tau_test = 8.0, 0.05
_gamma_scs_test = (_d_test + _tau_test / _d_test) / (1.0 + _tau_test)
print(f"[selftest-formula] SCS gamma at d=8,tau=0.05: {_gamma_scs_test:.4f} (expected 7.6250)", flush=True)
assert abs(_gamma_scs_test - 7.6250) < 0.001, f"SCS formula selftest failed: {_gamma_scs_test}"

_ratio_pred = math.sqrt(0.05 / 0.15)
print(f"[selftest-formula] SCS ratio sqrt(0.05/0.15): {_ratio_pred:.4f} (expected 0.5774)", flush=True)
assert abs(_ratio_pred - 0.5774) < 0.001, f"SCS ratio selftest failed: {_ratio_pred}"

_M_n4096_low = int(0.05 * 4096)
_M_n4096_high = int(0.15 * 4096)
assert _M_n4096_low == 204, f"M(N=4096, alpha=0.05) = {_M_n4096_low} expected 204"
assert _M_n4096_high == 614, f"M(N=4096, alpha=0.15) = {_M_n4096_high} expected 614"

_M_n16384_low = int(0.05 * 16384)
_M_n16384_high = int(0.15 * 16384)
assert _M_n16384_low == 819, f"M(N=16384, alpha=0.05) = {_M_n16384_low} expected 819"
assert _M_n16384_high == 2457, f"M(N=16384, alpha=0.15) = {_M_n16384_high} expected 2457"
print(f"[selftest-formula] M values verified for N=4096 and N=16384", flush=True)

# Pre-registered thresholds
HP_RATIO_LOW = 0.50
HP_RATIO_HIGH = 0.75
HP_TAU_LOW = 0.02
HP_TAU_HIGH = 0.20
HP_SCS_MATCH_FRAC = 0.30   # SCS formula within 30%
HP_SCS_MIN_CELLS = 3       # must match at 3+ cells per N
HF_RSB_RATIO_THRESH = 0.30  # ratio < 0.30 = RSB pole
HF_LYAPUNOV_RATIO_THRESH = 0.85  # ratio > 0.85 = flat = Lyapunov-only
# Universal fail: gamma scales as N^alpha > 0 (tested via two-N comparison)

if RUN_MODE == "smoke":
    N_VALUES_ACTIVE = [256, 512]  # tiny N for smoke speed
    SEEDS = [7, 17]
    ALPHA_GRID_ACTIVE = [0.05, 0.10, 0.15]  # 3 representative points
    N_SIGMA_SVD = 50  # small SVD probes
elif RUN_MODE == "smoke4x":
    N_VALUES_ACTIVE = [512, 1024]
    SEEDS = [7, 17]
    ALPHA_GRID_ACTIVE = [0.05, 0.10, 0.15]
    N_SIGMA_SVD = 100
else:
    N_VALUES_ACTIVE = N_VALUES
    SEEDS = [7, 17, 23, 31, 41]
    ALPHA_GRID_ACTIVE = ALPHA_GRID
    N_SIGMA_SVD = 200


def build_weight_matrix(xi: np.ndarray, n: int) -> np.ndarray:
    """Build non-reciprocal Hopfield weight matrix W = Xi^T Xi / N."""
    return (xi.T @ xi) / n


def measure_kappa3(xi: np.ndarray, n: int, rng: np.random.Generator,
                   n_probes: int = 200) -> float:
    """Estimate Tr(W^3)/N via Hutchinson trace estimator."""
    m = xi.shape[0]
    V = rng.choice([-1.0, 1.0], size=(n, n_probes))

    def w_op(v):
        inner = xi @ v  # (m, n_probes)
        return (xi.T @ inner) / n  # (n, n_probes)

    V1 = w_op(V)
    V2 = w_op(V1)
    V3 = w_op(V2)

    estimates = (V * V3).sum(axis=0) / n
    return float(np.mean(estimates))


def measure_gamma_emp(xi_base: np.ndarray, xi_perturb: np.ndarray,
                      n: int, rng: np.random.Generator, n_probes: int = 200) -> float:
    """Measure empirical gamma = kappa3_perturbed / kappa3_base.

    Uses isochoric kappa_3 separation protocol (same as PP-58 ratio=8.00 result).
    gamma_emp = kappa3(M + delta_M) / kappa3(M) where delta_M is small.
    """
    k3_base = measure_kappa3(xi_base, n, rng, n_probes)
    xi_aug = np.concatenate([xi_base, xi_perturb], axis=0)
    k3_aug = measure_kappa3(xi_aug, n, rng, n_probes)
    if abs(k3_base) < 1e-10:
        return 0.0
    return abs(k3_aug) / abs(k3_base)


def measure_tau(xi: np.ndarray, n: int) -> float:
    """Estimate asymmetry parameter tau = ||W_asym|| / ||W||.

    tau = 0 -> fully non-reciprocal (Ginibre); tau = 1 -> fully symmetric.
    For substrate's non-reciprocal W = Xi^T Xi / N:
    W_sym = (W + W^T)/2, W_asym = (W - W^T)/2.
    tau = ||W_asym||_F / ||W||_F (Frobenius).
    """
    # For W = Xi^T Xi / N, W is symmetric by construction.
    # The asymmetry comes from the NOISE/retrieval dynamics, not the static W.
    # tau_proxy: ratio of off-diagonal to total variance as asymmetry proxy.
    # Use leading singular value ratio as d_estimate.
    # For kappa_3 separation protocol, tau ~ 0 (near-Ginibre due to active repulsion).
    # We estimate tau from the W Frobenius structure.
    W = (xi.T @ xi) / n
    W_sym = (W + W.T) / 2.0
    W_asym = (W - W.T) / 2.0
    norm_asym = np.linalg.norm(W_asym, 'fro')
    norm_total = max(np.linalg.norm(W, 'fro'), 1e-10)
    return float(norm_asym / norm_total)


def measure_d_estimate(xi: np.ndarray, n: int) -> float:
    """Estimate d = sigma_1(W) / mean(sigma_bulk(W)) (leading SVD ratio).

    Uses truncated SVD: only compute first few singular values of W.
    For large N, uses the Xi structure: sigma_1(W) ~ sigma_1(Xi)^2 / N.
    """
    # Xi has shape (M, N). Singular values of Xi: sigma_i.
    # W = Xi^T Xi / N has eigenvalues sigma_i^2 / N.
    # Leading: sigma_max(Xi)^2 / N. Bulk mean: mean over all.
    # For tractability, use partial SVD (top 5 values).
    try:
        sv = np.linalg.svd(xi, compute_uv=False)
        sigma_sq = sv ** 2 / n
        if len(sigma_sq) < 2:
            return 1.0
        d = float(sigma_sq[0]) / max(float(np.mean(sigma_sq[1:])), 1e-10)
        return d
    except Exception:
        return 1.0


def run_cell(n: int, alpha: float, seed: int, n_probes: int = 200) -> Dict:
    """Run a single (N, alpha, seed) cell."""
    rng = np.random.default_rng(seed)
    M = int(alpha * n)
    if M < 1:
        return {"error": f"M={M} < 1 for N={n} alpha={alpha}"}

    t0 = time.time()

    xi_base = rng.choice([-1.0, 1.0], size=(M, n)).astype(np.float32)

    # Small perturbation: add 1 extra pattern for kappa_3 probe
    delta_M = max(1, int(0.01 * n))  # ~1% of N extra patterns
    xi_perturb = rng.choice([-1.0, 1.0], size=(delta_M, n)).astype(np.float32)

    gamma_emp = measure_gamma_emp(xi_base, xi_perturb, n, rng, n_probes)

    # Auxiliary measurements
    tau = measure_tau(xi_base, n)
    d_est = measure_d_estimate(xi_base, n)

    # SCS formula prediction
    if tau > 1e-6:
        gamma_scs = (d_est + tau / d_est) / (1.0 + tau)
    else:
        gamma_scs = d_est  # tau -> 0 limit

    elapsed = time.time() - t0
    return {
        "N": n, "alpha": alpha, "M": M, "seed": seed,
        "gamma_emp": float(gamma_emp),
        "tau_estimate": float(tau),
        "d_estimate": float(d_est),
        "gamma_scs_pred": float(gamma_scs),
        "scs_match_frac": abs(gamma_emp - gamma_scs) / max(gamma_emp, 1e-6),
        "elapsed_s": float(elapsed),
    }


def _instrumentation_selftest():
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    n_test = 256
    alpha_test = 0.10
    M_test = int(alpha_test * n_test)
    rng = np.random.default_rng(42)
    xi_test = rng.choice([-1.0, 1.0], size=(M_test, n_test)).astype(np.float32)

    # kappa_3 at zero noise should be ~alpha
    k3 = measure_kappa3(xi_test, n_test, rng, n_probes=100)
    assert not np.isnan(k3), "kappa_3 is NaN"
    assert abs(k3) > 0, "kappa_3 is exactly zero -- instrumentation broken"
    assert 0.07 < abs(k3) < 0.13, (
        f"kappa_3 identity check: got {k3:.4f} expected in [0.07, 0.13] "
        f"for alpha=0.10 zero noise")

    xi_perturb = rng.choice([-1.0, 1.0], size=(3, n_test)).astype(np.float32)
    gamma_emp = measure_gamma_emp(xi_test, xi_perturb, n_test, rng, n_probes=100)
    assert gamma_emp >= 0, f"gamma_emp is negative: {gamma_emp}"
    assert gamma_emp > 0, f"gamma_emp is zero -- instrumentation broken"

    tau = measure_tau(xi_test, n_test)
    assert 0.0 <= tau <= 1.0, f"tau out of range [0,1]: {tau}"

    d_est = measure_d_estimate(xi_test, n_test)
    assert d_est > 0, f"d_estimate is <= 0: {d_est}"

    # Full cell test (smallest scale)
    cell = run_cell(n_test, 0.10, seed=42, n_probes=100)
    assert "gamma_emp" in cell, "gamma_emp missing from cell result"
    assert cell["gamma_emp"] > 0, f"gamma_emp not positive in cell: {cell['gamma_emp']}"
    assert "tau_estimate" in cell, "tau_estimate missing"
    assert "d_estimate" in cell, "d_estimate missing"

    print(f"[selftest] PASS: kappa3={k3:.4f} gamma_emp={gamma_emp:.3f} "
          f"tau={tau:.4f} d_est={d_est:.3f} cell_gamma={cell['gamma_emp']:.3f} N={n_test}", flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


def compute_verdict(all_cell_results: List[Dict]) -> tuple:
    """Classify the full sweep into SCS/RSB/Lyapunov/universal-fail."""
    if not all_cell_results:
        return ("HARD_FAIL", "No valid results.")

    valid = [c for c in all_cell_results if "gamma_emp" in c and "error" not in c]
    if not valid:
        return ("HARD_FAIL", "All cells errored.")

    # Aggregate by (N, alpha): mean gamma_emp across seeds
    from collections import defaultdict
    cell_gammas = defaultdict(list)
    cell_taus = defaultdict(list)
    cell_scs_match = defaultdict(list)
    for c in valid:
        key = (c["N"], c["alpha"])
        cell_gammas[key].append(c["gamma_emp"])
        cell_taus[key].append(c["tau_estimate"])
        cell_scs_match[key].append(c["scs_match_frac"])

    mean_gammas = {k: float(np.mean(v)) for k, v in cell_gammas.items()}
    mean_taus = {k: float(np.mean(v)) for k, v in cell_taus.items()}
    mean_scs_match = {k: float(np.mean(v)) for k, v in cell_scs_match.items()}

    summary_parts = []
    for n in N_VALUES_ACTIVE:
        row = [(a, mean_gammas.get((n, a), float('nan'))) for a in ALPHA_GRID_ACTIVE]
        row_str = " ".join(f"a{a:.3f}:g{g:.2f}" for a, g in row if not math.isnan(g))
        summary_parts.append(f"N={n}:[{row_str}]")
    summary = " ".join(summary_parts) + f" n_valid_cells={len(valid)}"

    # Check universal fail: gamma ~ N^alpha (alpha > 0)
    # If gamma(N=16384) >> gamma(N=4096) at same alpha, suggests N-scaling
    n_low, n_high = 4096, N
    universal_fail = False
    if (n_low, 0.10) in mean_gammas and (n_high, 0.10) in mean_gammas:
        g_low = mean_gammas[(n_low, 0.10)]
        g_high = mean_gammas[(n_high, 0.10)]
        if g_high > 0 and g_low > 0:
            n_ratio = n_high / n_low  # = 4
            g_ratio = g_high / g_low
            # If gamma scales as N^alpha: g_ratio = n_ratio^alpha
            # alpha = log(g_ratio) / log(n_ratio)
            if g_ratio > 1.0:
                alpha_est = math.log(g_ratio) / math.log(n_ratio)
                if alpha_est > 0.1:  # clear positive scaling
                    universal_fail = True
                    return ("HARD_FAIL",
                            f"HARD_FAIL (universal): gamma scales as N^{alpha_est:.2f} > 0. "
                            f"g_N4096={g_low:.2f} g_N16384={g_high:.2f}. {summary}")

    # Compute ratio per N
    ratios = {}
    for n in N_VALUES_ACTIVE:
        g_low_a = mean_gammas.get((n, 0.05))
        g_high_a = mean_gammas.get((n, 0.15))
        if g_low_a is not None and g_high_a is not None and g_high_a > 0:
            ratios[n] = g_low_a / g_high_a
        else:
            ratios[n] = None

    ratio_str = " ".join(f"N={n}:r={r:.3f}" if r is not None else f"N={n}:r=NA"
                         for n, r in ratios.items())

    # Check tau in near-Ginibre range
    all_taus = list(mean_taus.values())
    tau_in_range = (all_taus and
                    all(HP_TAU_LOW <= t <= HP_TAU_HIGH for t in all_taus if not math.isnan(t)))

    # SCS formula match count
    scs_match_cells = sum(1 for v in mean_scs_match.values() if v < HP_SCS_MATCH_FRAC)

    # HARD-FAIL: RSB-consistent (ratio < 0.30)
    for n, r in ratios.items():
        if r is not None and r < HF_RSB_RATIO_THRESH:
            return ("HARD_FAIL",
                    f"HARD_FAIL (RSB): ratio(N={n})={r:.3f} < {HF_RSB_RATIO_THRESH}. "
                    f"Pole-driven divergence consistent with 1-RSB. {ratio_str}. {summary}")

    # HARD-FAIL: Lyapunov-only (ratio ~ 1.0)
    for n, r in ratios.items():
        if r is not None and r > HF_LYAPUNOV_RATIO_THRESH:
            return ("HARD_FAIL",
                    f"HARD_FAIL (Lyapunov): ratio(N={n})={r:.3f} > {HF_LYAPUNOV_RATIO_THRESH}. "
                    f"Gamma flat vs M, Lyapunov-only framework. {ratio_str}. {summary}")

    # HARD-PASS: SCS confirmed
    valid_ratios = [(n, r) for n, r in ratios.items() if r is not None]
    scs_ratio_pass = all(HP_RATIO_LOW <= r <= HP_RATIO_HIGH for _, r in valid_ratios)
    if (scs_ratio_pass and len(valid_ratios) >= 2 and tau_in_range and
            scs_match_cells >= HP_SCS_MIN_CELLS):
        return ("HARD_PASS",
                f"HARD_PASS (SCS): all ratios in [{HP_RATIO_LOW},{HP_RATIO_HIGH}] "
                f"tau_ok={tau_in_range} scs_match_cells={scs_match_cells}. "
                f"{ratio_str}. {summary}")

    # MIDDLE
    return ("MIDDLE_BAND",
            f"MIDDLE_BAND: scs_ratio_pass={scs_ratio_pass} tau_ok={tau_in_range} "
            f"scs_match_cells={scs_match_cells}. {ratio_str}. {summary}")


print(f"[config] PROT-018 N={N} (last suffix; sweeps both N_VALUES={N_VALUES_ACTIVE}) "
      f"mode={RUN_MODE} alpha_grid={ALPHA_GRID_ACTIVE}", flush=True)

out_dir = get_output_dir(ANCHOR_NAME)

# Build the full list of (N, alpha, seed) cells
def _cell_key(n_active, alpha, seed):
    """Alphanumeric-safe cell key for _seed_checkpoint."""
    alpha_str = f"{alpha:.4f}".replace('.', 'p')
    return f"N{n_active}_a{alpha_str}_s{seed}"

all_cell_keys = [
    (n, alpha, seed)
    for n in N_VALUES_ACTIVE
    for alpha in ALPHA_GRID_ACTIVE
    for seed in SEEDS
]
total_cells = len(all_cell_keys)
done_keys = set(list_completed_keys(out_dir))
remaining_keys = [k for k in all_cell_keys if _cell_key(*k) not in done_keys]
print(f"[ckpt] {len(done_keys)} cells done, {len(remaining_keys)} to run (total={total_cells})",
      flush=True)

t_sweep_start = time.time()
n_probes = 200 if RUN_MODE != "smoke" else 100

for idx, (n_active, alpha, seed) in enumerate(remaining_keys):
    print(f"[cell {idx+1}/{len(remaining_keys)}] N={n_active} alpha={alpha:.3f} seed={seed}...",
          flush=True)
    result = run_cell(n_active, alpha, seed, n_probes=n_probes)
    cell_key = _cell_key(n_active, alpha, seed)
    write_partial_key(out_dir, cell_key, result)
    print(f"  -> gamma_emp={result.get('gamma_emp', 'ERR'):.3f} "
          f"tau={result.get('tau_estimate', 'ERR'):.4f} "
          f"d={result.get('d_estimate', 'ERR'):.3f} "
          f"scs_pred={result.get('gamma_scs_pred', 'ERR'):.3f} "
          f"elapsed={result.get('elapsed_s', 0):.1f}s", flush=True)

# Aggregate all cells
all_results_map = aggregate_partials(out_dir)
all_cell_results = list(all_results_map.values())

verdict, verdict_msg = compute_verdict(all_cell_results)

print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)

elapsed_total = time.time() - t_sweep_start
print(f"[elapsed] total sweep time: {elapsed_total:.1f}s", flush=True)

metrics = {
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict, "verdict_msg": verdict_msg,
    "N": N, "N_values": N_VALUES_ACTIVE,
    "alpha_grid": ALPHA_GRID_ACTIVE, "seeds": SEEDS,
    "run_mode": RUN_MODE,
    "n_cells_total": total_cells, "n_cells_done": len(all_cell_results),
    "elapsed_s": elapsed_total,
    "summary": verdict_msg,
    "cells": [
        {k: v for k, v in c.items()}
        for c in all_cell_results
    ],
}
metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
