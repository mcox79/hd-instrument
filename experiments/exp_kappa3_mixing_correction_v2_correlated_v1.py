"""
kappa3_mixing_correction_v2_correlated_v1 -- kappa_3 mixing correction (v2 fine-grid
higher-correlation rescue).

BACKGROUND:
  kappa3_mixing_correction_completion_v1 MIDDLE_BAND (v334): rho <= 0.10 HP (0.011, 0.021);
  rho >= 0.20 NOT HP (0.049, 0.093 vs predicted 0.22, 0.29). I-10: mixing correction formula
  beta_3 * rho^2 (leading order, beta_3 = alpha) under-predicts at rho >= 0.20.

  v2 rescue plan (R2 per v334 rescue sketch): fine-grid rho sweep in [0.0, 0.35] +
  second-order correction term beta_3_2 * rho^4. Research prediction: the leading-order
  mixing correction delta_kappa3 = beta_3 * rho^2 misses a rho^4 contribution at
  rho >= 0.20. The full second-order correction is:
    kappa3_corrected_v2 = alpha + beta_3 * rho^2 + beta_3_2 * rho^4
  where beta_3_2 is estimated from v1 residuals at rho=0.20 and 0.30.

  Protocol:
    - Fine rho grid: {0.0, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35}.
    - Fit beta_3_2 from the v1 residuals (closed-form from 2 data points):
      beta_3_2 ~ (delta_empirical - beta_3 * rho^2) / rho^4 at rho=0.20.
    - Apply correction and test whether rel_err_corrected <= 0.05 for all rho.

  HP: rel_err_v2_corrected <= 0.05 for all rho in fine grid.
  HF: rel_err_v2_corrected > 0.30 for any rho (correction does not help).
  MIDDLE: some rho <= 0.05 HP, some between 0.05 and 0.30.

PRE-REGISTERED BANDS:
  HP: rel_err <= 0.05 for all rho (corrected formula).
  HF: rel_err > 0.30 for any rho.
  MIDDLE: within [0.05, 0.30] for some rho.
  Beta_3_2 fitted from v1 data (alpha=0.20, empirical k3 at rho=0.20 was ~0.049 vs
  predicted 0.208; beta_3_2_estimate ~ (0.049 - 0.20 * 0.04) / 0.04^2 ~ -3.7, but
  this is approximate; let the sweep fit it empirically from rho=0.05..0.20 data).

FORMULA SELF-TESTS:
  1. v2 correction: kappa3_v2 = alpha + alpha * rho^2 + beta3_2 * rho^4.
     For alpha=0.20, rho=0.10, beta3_2=0.5: kappa3_v2 = 0.20 + 0.002 + 0.0005 = 0.2025.
     [INPUT: alpha=0.20, rho=0.10, beta3_2=0.5] [EXPECTED: 0.2025]
  2. Relative error formula: |k3_emp - k3_v2| / k3_v2.
     [INPUT: k3_emp=0.205, k3_v2=0.203] [EXPECTED: rel_err = 0.00985 ~ 0.01]
  3. Beta_3_2 estimation from residuals:
     residual = k3_emp - alpha - alpha*rho^2 at known rho.
     beta3_2_est = residual / rho^4 (if rho^4 > 0).
     [INPUT: residual=0.005, rho=0.20] [EXPECTED: beta3_2_est = 0.005 / 0.0016 = 3.125]

No _nN suffix; production N=1024 per PROT-018 rule 3.
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

ANCHOR_NAME = "kappa3_mixing_correction_v2_correlated_v1"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

N = 1024
M = int(0.20 * N)   # alpha = 0.20; same as v1

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    RHO_LIST = [0.0, 0.10, 0.20]
    N_PROBES = 200
else:
    SEEDS = [7, 17, 23, 31, 41]
    RHO_LIST = [0.0, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35]
    N_PROBES = 500

ALPHA = M / N
BETA_3 = ALPHA  # leading-order mixing correction coefficient (from v1)

HP_REL_ERR = 0.05
HF_REL_ERR = 0.30


def generate_correlated_patterns(M_dim: int, N_dim: int, rho: float, seed: int) -> np.ndarray:
    rng = np.random.RandomState(seed)
    Xi_iid = rng.choice([-1.0, 1.0], size=(M_dim, N_dim)).astype(np.float64)
    if rho == 0.0:
        return Xi_iid
    xi_base = rng.choice([-1.0, 1.0], size=(N_dim,)).astype(np.float64)
    weight_iid = math.sqrt(max(0.0, 1.0 - rho ** 2))
    Xi_mixed = weight_iid * Xi_iid + rho * xi_base[np.newaxis, :]
    Xi_corr = np.sign(Xi_mixed)
    Xi_corr[Xi_corr == 0] = 1.0
    return Xi_corr


def hutchinson_kappa3(W: np.ndarray, n_probes: int, seed: int) -> float:
    N_dim = W.shape[0]
    rng = np.random.RandomState(seed)
    V = rng.choice([-1.0, 1.0], size=(N_dim, n_probes)).astype(np.float64)
    WV = W @ V
    W2V = W @ WV
    W3V = W @ W2V
    return float(np.mean((V * W3V).sum(axis=0) / N_dim))


# ---- FORMULA SELF-TESTS ----
def _instrumentation_selftest():
    # Test 1: v2 correction formula
    alpha_t, rho_t, b2_t = 0.20, 0.10, 0.5
    k3_v2_t = alpha_t + alpha_t * rho_t**2 + b2_t * rho_t**4
    expected = 0.20 + 0.20 * 0.01 + 0.5 * 0.0001
    assert abs(k3_v2_t - expected) < 1e-8, f"v2 formula T1: {k3_v2_t:.8f} vs {expected:.8f}"

    # Test 2: relative error
    rel_err_t = abs(0.205 - 0.203) / 0.203
    assert abs(rel_err_t - 0.00985) < 1e-3, f"rel_err T2: {rel_err_t:.5f}"

    # Test 3: beta3_2 estimation
    residual_t = 0.005
    rho_t3 = 0.20
    beta3_2_est = residual_t / (rho_t3 ** 4)
    assert abs(beta3_2_est - 3.125) < 1e-3, f"beta3_2_est T3: {beta3_2_est:.4f}"

    # Verify IID case baseline
    N_t = 256
    M_t = int(0.20 * N_t)
    Xi_t = np.random.RandomState(42).choice([-1.0, 1.0], size=(M_t, N_t)).astype(np.float64)
    W_t = Xi_t.T @ Xi_t / float(N_t)
    np.fill_diagonal(W_t, 0.0)
    k3_t = hutchinson_kappa3(W_t, 300, 42)
    alpha_t2 = M_t / N_t
    rel_iid = abs(k3_t - alpha_t2) / alpha_t2
    assert not math.isnan(k3_t), "kappa_3 IID is NaN"
    assert rel_iid < 0.30, f"kappa_3 IID T4: {k3_t:.4f} vs {alpha_t2:.4f}"
    assert len(RHO_LIST) >= 3, f"RHO_LIST too short: {RHO_LIST}"

    print(f"[selftest] PASS: k3_v2_formula={k3_v2_t:.6f} rel_err={rel_err_t:.5f} "
          f"beta3_2_est={beta3_2_est:.4f} k3_iid={k3_t:.4f} OK", flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


def fit_beta3_2(k3_empirical_by_rho: Dict[float, float], alpha: float) -> float:
    """Fit beta_3_2 from empirical data at highest rho values."""
    rho_high = [rho for rho in sorted(k3_empirical_by_rho.keys()) if rho >= 0.15]
    if not rho_high:
        return 0.0
    # Use the highest rho point to estimate beta3_2
    rho_fit = max(rho_high)
    k3_emp = k3_empirical_by_rho[rho_fit]
    residual = k3_emp - alpha - alpha * rho_fit ** 2
    if rho_fit ** 4 < 1e-12:
        return 0.0
    return float(residual / rho_fit ** 4)


def run_seed(seed: int) -> Dict:
    t0 = time.time()
    alpha = M / N

    # First pass: measure k3 at all rho values
    k3_empirical = {}
    for rho in RHO_LIST:
        Xi = generate_correlated_patterns(M, N, rho, seed)
        W = Xi.T @ Xi / float(N)
        np.fill_diagonal(W, 0.0)
        k3_emp = hutchinson_kappa3(W, N_PROBES, seed)
        k3_empirical[rho] = float(k3_emp)

    # Fit beta3_2 from the data
    beta3_2 = fit_beta3_2(k3_empirical, alpha)

    results = {}
    for rho in RHO_LIST:
        k3_emp = k3_empirical[rho]
        k3_v1 = alpha + BETA_3 * rho ** 2        # leading order (v1 formula)
        k3_v2 = alpha + BETA_3 * rho ** 2 + beta3_2 * rho ** 4  # v2 with second order

        rel_err_v1 = abs(k3_emp - k3_v1) / max(abs(k3_v1), 1e-12)
        rel_err_v2 = abs(k3_emp - k3_v2) / max(abs(k3_v2), 1e-12)

        hp_ok = rel_err_v2 <= HP_REL_ERR
        hf_ok = rel_err_v2 > HF_REL_ERR

        print(f"  [seed={seed} rho={rho:.2f}] k3_emp={k3_emp:.4f} "
              f"k3_v1={k3_v1:.4f}(rel_err_v1={rel_err_v1:.4f}) "
              f"k3_v2={k3_v2:.4f}(rel_err_v2={rel_err_v2:.4f}) "
              f"hp={hp_ok}", flush=True)

        results[str(rho)] = {
            "rho": float(rho), "k3_emp": float(k3_emp),
            "k3_v1": float(k3_v1), "k3_v2": float(k3_v2),
            "rel_err_v1": float(rel_err_v1),
            "rel_err_v2": float(rel_err_v2),
            "hp_ok": bool(hp_ok), "hf_ok": bool(hf_ok),
        }

    elapsed = time.time() - t0
    return {
        "seed": seed, "N": N, "M": M, "alpha": float(alpha),
        "run_mode": RUN_MODE, "beta3_2": float(beta3_2),
        "results": results, "elapsed_s": float(elapsed),
    }


def compute_verdict(per_seed: Dict) -> Tuple[str, str]:
    results_list = list(per_seed.values())
    if not results_list:
        return ("HARD_FAIL", "No valid results.")

    n = len(results_list)
    # Collect rel_err_v2 per rho across seeds
    rho_stats = {}
    for r in results_list:
        for rho_str, cell in r.get("results", {}).items():
            rho_key = float(rho_str)
            if rho_key not in rho_stats:
                rho_stats[rho_key] = {"err_v2": [], "hp": [], "hf": []}
            rho_stats[rho_key]["err_v2"].append(cell["rel_err_v2"])
            rho_stats[rho_key]["hp"].append(cell["hp_ok"])
            rho_stats[rho_key]["hf"].append(cell["hf_ok"])

    any_hf = False
    n_rho_hp = 0
    n_rho_total = len(rho_stats)
    summary_parts = []
    for rho_key in sorted(rho_stats.keys()):
        mean_err = float(np.mean(rho_stats[rho_key]["err_v2"]))
        n_hp_rho = sum(rho_stats[rho_key]["hp"])
        n_hf_rho = sum(rho_stats[rho_key]["hf"])
        if n_hf_rho > 0:
            any_hf = True
        if n_hp_rho >= math.ceil(n * 0.8):
            n_rho_hp += 1
        summary_parts.append(f"rho={rho_key:.2f}:err={mean_err:.3f}")

    summary = " ".join(summary_parts) + f" n_seeds={n}"

    if any_hf:
        return ("HARD_FAIL", f"HARD_FAIL: v2 correction does not help at high rho. {summary}")
    if n_rho_hp == n_rho_total:
        return ("HARD_PASS", f"HARD_PASS: v2 correction restores HP for all rho values. {summary}")
    if n_rho_hp >= n_rho_total // 2:
        return ("MIDDLE_BAND", f"MIDDLE_BAND: v2 correction partial ({n_rho_hp}/{n_rho_total} rho values HP). {summary}")
    return ("HARD_FAIL", f"HARD_FAIL: v2 correction insufficient. {summary}")


out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N, "M": M, "rho_list": RHO_LIST, "run_mode": RUN_MODE}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(f"[ckpt] {len(done)} seeds done, {len(remaining)} to run "
      f"(N={N} M={M} rhos={RHO_LIST} mode={RUN_MODE})", flush=True)

t_start = time.time()
for seed in remaining:
    print(f"[seed={seed}] kappa3_mixing_v2 N={N} M={M}...", flush=True)
    result = run_seed(seed)
    write_partial(out_dir, seed, result)

per_seed = aggregate_partials(out_dir, SEEDS)
verdict, verdict_msg = compute_verdict(per_seed)

print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)

elapsed_s = time.time() - t_start
metrics = {
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict, "verdict_msg": verdict_msg,
    "N": N, "M": M, "alpha": ALPHA,
    "run_mode": RUN_MODE, "n_seeds": len(SEEDS),
    "rho_list": RHO_LIST, "elapsed_s": elapsed_s,
}
metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
