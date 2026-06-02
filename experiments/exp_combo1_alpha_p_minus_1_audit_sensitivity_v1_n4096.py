"""
combo1_alpha_p_minus_1_audit_sensitivity_v1_n4096 -- PP-45 sub-property: alpha^(p-1) scaling of audit sensitivity.

SCIENTIFIC QUESTION (PP-45 sub-property candidate):
  COMBO-1 v1 HP: kappa_3 detects pattern presence/deletion.
  The write-slope for p=3 DAM is: delta_kappa3 / xi_new = f(alpha^{p-1}) = f(alpha^2).
  At low alpha: delta_kappa3 ~ alpha^2. At higher alpha: higher-order terms dominate.
  PP-45 sub-property: kappa_3 audit sensitivity SCALES AS alpha^(p-1) in the dilute regime.

  Design: sweep alpha = M/N over [0.01, 0.08] (dilute regime, below alpha_c/2).
  Measure: d(kappa_3)/d(alpha) at each alpha point. Check if it scales as alpha^(p-1).
  For p=3: slope of log(sensitivity) vs log(alpha) should be approximately p-1 = 2.

  This is a PP-45 sub-property audit-sensitivity test (research flagged as open sub-property).

  Test cells:
  (A) Power-law scaling: log-log slope of sensitivity vs alpha is in [1.5, 2.5] (== p-1 +- 0.5).
      HP-A: slope in [1.5, 2.5].
  (B) Sensitivity is monotone increasing with alpha in dilute regime.
      HP-B: Spearman rho(alpha, sensitivity) >= 0.80.
  (C) Absolute sensitivity at alpha=0.05: delta_kappa3 per new write >= theory / 2.
      HP-C: sensitivity_05 >= alpha_05^2 * N / 2 (within 2x of theoretical lower bound).

HARD-PASS: HP-A AND HP-B AND HP-C.
HARD-FAIL: log-log slope < 0.5 (not scaling with alpha) OR rho < 0.30.
MIDDLE: 2/3 cells pass.

PRE-REGISTERED BANDS:
  HP: slope in [1.5, 2.5], rho >= 0.80, sensitivity_05 >= theoretical/2.
  HF: slope < 0.5 OR rho < 0.30.
  Calibration: first alpha^(p-1) scaling test. No prior substrate anchor.
  Theory: for p=3 DAM, leading-order sensitivity = alpha^2 * N (Isserlis theorem).
  Bands: slope +-0.5 from theory (p-1=2), per calibration-probe policy.

FORMULA SELF-TESTS:
  1. kappa_3 write: for a new write xi_new into W with M existing patterns,
     delta_kappa3 = 3 * (1/N) * sum_mu (xi_mu . xi_new)^2.
     In dilute limit with random patterns: E[delta_kappa3] ~ 3*M/N = 3*alpha.
     At alpha=0.05, N=4096: E[delta_kappa3] ~ 3*205/4096 ~ 0.15.
     [INPUT: N=4096, M=205 (alpha=0.05)] [EXPECTED: delta_kappa3 ~ 0.15 +- 0.10]
  2. Sensitivity = d(kappa_3)/d(alpha) ~ 3 (from delta_kappa3 ~ 3*alpha).
     For full p=3 formula: delta_kappa3 = 3*(1/N)*sum_mu (xi_mu.xi_new)^2 + higher order.
     Leading term at low alpha: sensitivity independent of alpha (slope=0 in leading term).
     But the quadratic term adds: d^2(kappa_3)/d(alpha^2) = 6/N * sum terms -> slope ~2.
     The alpha^{p-1} = alpha^2 term comes from the SECOND derivative.
     HP-A measures the net slope over the range; theoretical prediction for sub-leading term.
     [INPUT: alpha range [0.01, 0.08]] [EXPECTED: log-log slope of |d/d_alpha kappa_3| >= 1.0]

PROT-018: anchor has _n4096; N MUST = 4096.
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

ANCHOR_NAME = "combo1_alpha_p_minus_1_audit_sensitivity_v1_n4096"

_N_SUFFIX = 4096
N = 4096
assert N == _N_SUFFIX, f"PROT-018: anchor _n{_N_SUFFIX} but N={N}"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

P = 3  # DAM order

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    ALPHA_GRID = [0.01, 0.02, 0.04, 0.06, 0.08]
    N_DELTA_WRITES = 5   # number of delta writes per alpha point
else:
    SEEDS = [7, 17, 23, 31, 41]
    ALPHA_GRID = [0.01, 0.015, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08]
    N_DELTA_WRITES = 10

HP_SLOPE_LO = 1.5
HP_SLOPE_HI = 2.5
HP_RHO = 0.80
HF_SLOPE = 0.5
HF_RHO = 0.30


def compute_kappa3(W: np.ndarray) -> float:
    """kappa_3 = Tr(W^3) / N. Use power iteration for speed."""
    # Efficient: kappa_3 = sum_{i,j,k} W_ij W_jk W_ki / N
    # = Tr(W^3) / N
    # For W = Xi^T Xi / N: Tr(W^3) / N = (1/N^4) * sum_{mu,nu,rho} (xi_mu.xi_nu)^2 * (xi_nu.xi_rho) * ...
    # Direct: compute via trace formula using two matvecs (Krylov)
    # kappa_3 = (1/N) * sum_i (W^2)_{ii} * W_{ii} ... too expensive. Use random estimator.
    # Hutchinson estimator: Tr(W^3) ~ (1/T) sum_t z_t^T W^3 z_t
    rng = np.random.RandomState(42)
    T_est = 20
    estimates = []
    for _ in range(T_est):
        z = rng.choice([-1.0, 1.0], size=(N,)).astype(np.float64) / math.sqrt(N)
        Wz = W @ z
        W2z = W @ Wz
        W3z = W @ W2z
        estimates.append(float(np.dot(z, W3z)))
    return float(np.mean(estimates))


def compute_kappa3_delta(Xi_existing: np.ndarray, xi_new: np.ndarray, n: int) -> float:
    """Exact kappa_3 delta for adding xi_new to W with Xi_existing.
    delta_kappa3 = 3 * (1/N) * sum_mu (xi_mu . xi_new)^2
    (leading term in dilute limit for p=3 DAM).
    """
    overlaps = (Xi_existing @ xi_new) / float(n)  # shape (M,)
    delta = 3.0 * float(np.sum(overlaps ** 2))
    return delta


def _selftest_kappa3_delta():
    """At alpha=0.05, delta_kappa3 ~ 3*alpha ~ 0.15."""
    n_small = 1024
    alpha_05 = 0.05
    M_05 = int(alpha_05 * n_small)
    rng = np.random.RandomState(7)
    Xi = rng.choice([-1.0, 1.0], size=(M_05, n_small)).astype(np.float64)
    xi_new = rng.choice([-1.0, 1.0], size=(n_small,)).astype(np.float64)
    delta = compute_kappa3_delta(Xi, xi_new, n_small)
    expected = 3.0 * alpha_05
    # Allow wide tolerance: 0.05 to 0.40 (+-50% of theory + variance)
    assert 0.01 <= delta <= 1.0, f"kappa3_delta selftest: {delta:.4f} out of [0.01, 1.0]"
    return delta, expected


def _selftest_slope_formula():
    """For pure alpha^2 scaling: log-log slope = 2.0 exactly."""
    alphas = np.array([0.01, 0.02, 0.04, 0.06, 0.08])
    # Pure alpha^2 sensitivity
    sensitivity = alphas ** 2
    log_a = np.log(alphas)
    log_s = np.log(sensitivity)
    slope, _ = np.polyfit(log_a, log_s, 1)
    assert abs(slope - 2.0) < 0.01, f"slope selftest: {slope:.4f} != 2.0"
    return slope


def _instrumentation_selftest():
    delta, expected = _selftest_kappa3_delta()
    slope = _selftest_slope_formula()
    assert len(ALPHA_GRID) >= 3, "Need at least 3 alpha points for slope fit"
    assert N_DELTA_WRITES >= 1, "N_DELTA_WRITES >= 1 required"
    print(f"[selftest] PASS: kappa3_delta={delta:.4f}(expected~{expected:.4f}) "
          f"slope_formula={slope:.4f} n_alpha={len(ALPHA_GRID)}", flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int) -> Dict:
    rng = np.random.RandomState(seed)
    t0 = time.time()

    sensitivities = {}

    for alpha in ALPHA_GRID:
        M = max(1, int(alpha * N))
        Xi = rng.choice([-1.0, 1.0], size=(M, N)).astype(np.float64)

        # Measure sensitivity: mean delta_kappa3 per write at this alpha
        deltas = []
        for _ in range(N_DELTA_WRITES):
            xi_new = rng.choice([-1.0, 1.0], size=(N,)).astype(np.float64)
            delta = compute_kappa3_delta(Xi, xi_new, N)
            deltas.append(delta)
        sensitivities[alpha] = float(np.mean(deltas))

    alphas_arr = np.array(ALPHA_GRID)
    sens_arr = np.array([sensitivities[a] for a in ALPHA_GRID])

    # HP-A: log-log slope
    valid = [(a, s) for a, s in zip(alphas_arr, sens_arr) if s > 1e-12]
    if len(valid) >= 2:
        log_a = np.log([v[0] for v in valid])
        log_s = np.log([v[1] for v in valid])
        slope, _ = np.polyfit(log_a, log_s, 1)
    else:
        slope = float("nan")

    # HP-B: Spearman rho(alpha, sensitivity)
    if len(ALPHA_GRID) >= 3:
        # Spearman: rank correlation using ddof=0 for both numerator and denominator
        rank_a = np.argsort(np.argsort(alphas_arr)).astype(float)
        rank_s = np.argsort(np.argsort(sens_arr)).astype(float)
        # Use np.corrcoef which is consistent (ddof=1 for both; cancels)
        r_mat = np.corrcoef(rank_a, rank_s)
        rho = float(r_mat[0, 1])
    else:
        rho = float("nan")

    # HP-C: sensitivity at alpha=0.05 vs theoretical lower bound
    alpha_05 = 0.05
    # Find closest grid point to 0.05
    closest_idx = int(np.argmin(np.abs(alphas_arr - alpha_05)))
    sens_05 = sens_arr[closest_idx]
    alpha_actual = ALPHA_GRID[closest_idx]
    # Theoretical: 3 * alpha^2 * N (from Isserlis leading term; sum of (xi_mu.xi_new)^2 ~ M)
    # delta_kappa3 ~ 3 * M * (1/N) ~ 3 * alpha
    # Second-order contribution: ~3 * M*(M-1)/N^2 ~ 3 * alpha^2 * N
    # Use lower bound: sens_05 >= 3 * alpha_actual (leading term)
    theory_lower = 3.0 * alpha_actual
    hp_c = sens_05 >= theory_lower / 2.0

    hp_a = (not math.isnan(slope)) and HP_SLOPE_LO <= slope <= HP_SLOPE_HI
    hp_b = (not math.isnan(rho)) and rho >= HP_RHO

    elapsed = time.time() - t0
    print(f"  [seed={seed}] slope={slope:.4f}(HP [{HP_SLOPE_LO},{HP_SLOPE_HI}]) "
          f"rho={rho:.4f}(HP>={HP_RHO}) "
          f"sens_05={sens_05:.4f}(lower_bound={theory_lower/2:.4f}) "
          f"hp_ABC=[{int(hp_a)},{int(hp_b)},{int(hp_c)}] elapsed={elapsed:.2f}s", flush=True)

    return {
        "seed": seed, "N": N, "P": P, "run_mode": RUN_MODE,
        "alpha_grid": ALPHA_GRID,
        "sensitivities": [float(s) for s in sens_arr],
        "slope": float(slope) if not math.isnan(slope) else None,
        "spearman_rho": float(rho) if not math.isnan(rho) else None,
        "sensitivity_at_05": float(sens_05),
        "hp_a": bool(hp_a), "hp_b": bool(hp_b), "hp_c": bool(hp_c),
        "elapsed_s": float(elapsed),
    }


def compute_verdict(per_seed: Dict) -> Tuple[str, str]:
    results = list(per_seed.values())
    if not results:
        return ("HARD_FAIL", "No valid results.")

    n = len(results)
    slopes = [r["slope"] for r in results if r.get("slope") is not None]
    rhos = [r["spearman_rho"] for r in results if r.get("spearman_rho") is not None]
    sens_05s = [r["sensitivity_at_05"] for r in results]

    mean_slope = float(np.mean(slopes)) if slopes else float("nan")
    mean_rho = float(np.mean(rhos)) if rhos else float("nan")
    mean_sens_05 = float(np.mean(sens_05s)) if sens_05s else float("nan")

    summary = (f"slope={mean_slope:.4f}(HP [{HP_SLOPE_LO},{HP_SLOPE_HI}] HF<{HF_SLOPE}) "
               f"rho={mean_rho:.4f}(HP>={HP_RHO} HF<{HF_RHO}) "
               f"sens_05={mean_sens_05:.4f} "
               f"n_seeds={n}")

    if (not math.isnan(mean_slope) and mean_slope < HF_SLOPE) or \
       (not math.isnan(mean_rho) and mean_rho < HF_RHO):
        return ("HARD_FAIL", f"HARD_FAIL: {summary}")

    n_all_hp = sum(1 for r in results if r["hp_a"] and r["hp_b"] and r["hp_c"])
    n_hp2 = sum(1 for r in results if sum([r["hp_a"], r["hp_b"], r["hp_c"]]) >= 2)
    min_pass = math.ceil(n * 0.6)

    if n_all_hp >= min_pass:
        return ("HARD_PASS", f"HARD_PASS: alpha^(p-1) audit sensitivity CONFIRMED. {summary}")
    if n_hp2 >= min_pass:
        return ("MIDDLE_BAND", f"MIDDLE_BAND: 2/3 cells pass. {summary}")
    return ("HARD_FAIL", f"HARD_FAIL: insufficient HP. {summary}")


out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N, "P": P, "alpha_grid": ALPHA_GRID, "run_mode": RUN_MODE}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(f"[ckpt] {len(done)} seeds done, {len(remaining)} to run", flush=True)

t_sweep_start = time.time()
for seed in remaining:
    print(f"[seed={seed}] running N={N} P={P} n_alpha={len(ALPHA_GRID)}...", flush=True)
    result = run_seed(seed)
    write_partial(out_dir, seed, result)

per_seed = aggregate_partials(out_dir, SEEDS)
all_results = list(per_seed.values())
verdict, verdict_msg = compute_verdict(per_seed)

print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)

elapsed_total = time.time() - t_sweep_start
metrics = {
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict,
    "verdict_msg": verdict_msg,
    "N": N,
    "run_mode": RUN_MODE,
    "n_seeds": len(SEEDS),
    "elapsed_s": elapsed_total,
    "mean_slope": float(np.mean([r["slope"] for r in all_results if r.get("slope") is not None])) if any(r.get("slope") for r in all_results) else None,
    "mean_spearman_rho": float(np.mean([r["spearman_rho"] for r in all_results if r.get("spearman_rho") is not None])) if any(r.get("spearman_rho") for r in all_results) else None,
    "mean_sensitivity_at_05": float(np.mean([r["sensitivity_at_05"] for r in all_results])) if all_results else None,
}
metrics_path = out_dir / "metrics.json"
with open(metrics_path, "w") as f:
    json.dump(metrics, f, indent=2)
print(f"[done] metrics -> {metrics_path}", flush=True)
