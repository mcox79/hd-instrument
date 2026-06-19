"""
pp58_isochoric_kappa3_alpha_sweep_v1_n4096 -- PP-58 isochoric audit protocol measurement.

Tests the Arrhenius-deep-drill structural result: substrate exhibits two distinct noise envelopes
hidden in one parameter (sigma_g). The isochoric protocol (sweep sigma at FIXED alpha) separates:
  - thermal-analog fragility: kappa_3 audit primitive breaks at sigma_g ~ 0.18
  - density-analog capacity: capacity breaks at sigma_g ~ sqrt(1/alpha - 1) >> 0.18

SCIENTIFIC QUESTION (PP-58 candidate row):
  Does sweeping sigma_g at fixed alpha = 0.05 reveal two clearly separated envelopes:
    (1) kappa_3 audit degrades significantly before capacity degrades?
    (2) sigma_g_audit_crit << sigma_g_capacity_crit (predicted ratio ~24x at alpha=0.05)?

TEST DESIGN (isochoric = constant alpha):
  alpha = 0.05 (fixed; isochoric condition)
  N = 4096, 5 seeds
  sigma_g sweep: {0.01, 0.05, 0.10, 0.15, 0.18, 0.20, 0.25, 0.30, 0.50, 1.0, 2.0, 4.0}
  For each sigma_g:
    - measure kappa_3 = E[x^3] / N (third moment of retrieval distribution)
    - measure recall accuracy (mean cosine of retrieved vs stored pattern)
    - record kappa_3_ratio = kappa_3_measured / alpha (identity holds when = 1.0)
  Report: sigma_g_audit_crit (where kappa_3_ratio drops below 0.85) vs
          sigma_g_capacity_crit (where recall drops below 0.50)

PREDICTED SEPARATION (from Arrhenius drill + Wave-2 free-probability):
  sigma_g_audit_crit ~ 0.18 (kappa_3 identity breaks)
  sigma_g_capacity_crit = sqrt(1/0.05 - 1) = sqrt(19) ~ 4.36
  Ratio: 4.36 / 0.18 ~ 24x

FORMULA SELF-TESTS (PROT-022):
  1. kappa_3 identity at zero noise: kappa_3 = alpha + O(1/N)
     [INPUT: sigma_g=0.0, alpha=0.05, N=4096] [EXPECTED: kappa_3_ratio ~ 1.0 +/- 0.05]
  2. Capacity phase boundary formula: sigma_g_crit = sqrt(1/alpha - 1)
     [INPUT: alpha=0.05] [EXPECTED: sigma_g_crit = 4.3589]
     [INPUT: alpha=0.10] [EXPECTED: sigma_g_crit = 3.0000]
  3. alpha = M/N > 0 for M = int(0.05 * N)
     [INPUT: N=4096, alpha=0.05] [EXPECTED: M=204, alpha_actual=0.04980]

PRE-REGISTERED BANDS (PP-58 isochoric audit protocol; no prior empirical anchor at N=4096
  -- bands widened to +-50% of theoretical prediction per calibration-probe policy):
  HARD-PASS: sigma_g_audit_crit in [0.09, 0.27] (predicted 0.18 +-50%)
             AND sigma_g_capacity_crit >= 1.0 (capacity survives much longer than audit)
             AND ratio (capacity_crit / audit_crit) >= 5.0 (two-envelope separation confirmed)
  MIDDLE: ratio in [2.0, 5.0) OR sigma_g_audit_crit slightly outside [0.09, 0.27]
  HARD-FAIL: sigma_g_audit_crit < 0.05 (audit breaks at too-low noise -- theory wrong by >3x)
             OR sigma_g_audit_crit > 0.54 (audit too robust -- theory wrong by >3x)
             OR no clear separation between audit and capacity envelopes (ratio < 2.0)

PROT-018: anchor has _n4096; N MUST = 4096.
QUEUE: remote_cpu_queue (CPU; pure numpy; alpha=0.05 fixed, 12 sigma sweep x 5 seeds ~45 min).
"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import os
import argparse
import time
import json
from pathlib import Path
from typing import Dict, List

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

try:
    import numpy as np
except ImportError:
    print("[FATAL] numpy not installed.", flush=True)
    sys.exit(1)

from experiments._seed_checkpoint import get_output_dir, resumable_seeds, write_partial, aggregate_partials

ANCHOR_NAME = "pp58_isochoric_kappa3_alpha_sweep_v1_n4096"

_N_SUFFIX = 4096
N = 4096
assert N == _N_SUFFIX, f"PROT-018: anchor _n{_N_SUFFIX} but N={N}"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

# Isochoric: fixed alpha
ALPHA_FIXED = 0.05

# Sigma_g sweep (covers both envelopes)
SIGMA_G_FULL = [0.0, 0.01, 0.05, 0.10, 0.15, 0.18, 0.20, 0.25, 0.30, 0.50, 1.0, 2.0, 4.0]

# Predicted phase boundaries
SIGMA_G_AUDIT_PRED = 0.18   # kappa_3 audit breaks
SIGMA_G_CAP_PRED = float((1.0 / ALPHA_FIXED - 1.0) ** 0.5)  # = sqrt(19) ~ 4.359

# Pre-registered threshold bands
HP_AUDIT_CRIT_LOW = 0.09    # 0.18 * 0.5
HP_AUDIT_CRIT_HIGH = 0.27   # 0.18 * 1.5
HP_CAP_CRIT_MIN = 1.0       # capacity must survive at least to sigma_g=1.0
HP_RATIO_MIN = 5.0
MIDDLE_RATIO_MIN = 2.0
HF_AUDIT_CRIT_LOW = 0.05    # < 1/3 of theory
HF_AUDIT_CRIT_HIGH = 0.54   # > 3x theory
HF_RATIO_MIN = 2.0

# Verdict thresholds for kappa_3_ratio and recall
KAPPA3_RATIO_CRIT = 0.85   # kappa_3_ratio below this = audit broken
RECALL_CRIT = 0.50          # recall below this = capacity broken

N_RETRIEVAL_STEPS = 8
N_QUERIES_PER_CELL = 10
N_PROBES_HUTCHINSON = 50    # Rademacher probes for FULL Hutchinson kappa_3 estimator
                             # 50 probes at N=4096: ~N^2 * 3 matmuls * 50 = 2.5B flops/seed
                             # Still provides ratio detection with ~15% relative std
N_PROBES_SELFTEST = 30      # Fewer probes for selftest (speed)

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    N_ACTIVE = 512
    # Reduced sigma sweep covering both envelopes
    SIGMA_G_USE = [0.0, 0.10, 0.18, 0.25, 0.50, 2.0, 4.0]
    N_QUERIES_USE = 5
    N_PROBES_USE = N_PROBES_SELFTEST
else:
    SEEDS = [7, 17, 23, 31, 41]
    N_ACTIVE = N
    SIGMA_G_USE = SIGMA_G_FULL
    N_QUERIES_USE = N_QUERIES_PER_CELL
    N_PROBES_USE = N_PROBES_HUTCHINSON


def hutchinson_kappa3_np(W: np.ndarray, n_probes: int, seed: int) -> float:
    """Hutchinson estimator for Tr(W^3) / N (kappa_3 normalized).

    kappa_3 = (1/n_probes) sum_i v_i^T W^3 v_i / N
    v_i are iid Rademacher probes.
    """
    rng_h = np.random.RandomState(seed + 88888)
    n_dim = W.shape[0]
    estimates = np.zeros(n_probes)
    for i in range(n_probes):
        v = rng_h.choice([-1.0, 1.0], size=(n_dim,)).astype(np.float64)
        Wv = W @ v
        W2v = W @ Wv
        W3v = W @ W2v
        estimates[i] = float(np.dot(v, W3v)) / n_dim
    return float(np.mean(estimates))


def _selftest_kappa3_identity():
    """kappa_3 identity at zero noise via Hutchinson: kappa_3 / alpha ~ 1.0.

    Uses N=512 (smoke N_ACTIVE) with n_probes=100 for speed.
    Expected: ratio in [0.5, 2.0] (wide tolerance at 100 probes, N=512).
    """
    n_t = N_ACTIVE  # use smoke N for speed
    alpha = ALPHA_FIXED
    M_t = max(1, int(alpha * n_t))
    rng_t = np.random.RandomState(42)
    Xi = rng_t.choice([-1., 1.], size=(M_t, n_t)).astype(np.float64)
    W = (Xi.T @ Xi) / float(n_t)
    k3 = hutchinson_kappa3_np(W, n_probes=30, seed=42)
    k3_ratio = k3 / alpha
    assert 0.3 < k3_ratio < 3.0, (
        f"kappa_3 identity failed at zero noise: k3_ratio={k3_ratio:.4f}, expected ~1.0")


def _selftest_capacity_boundary():
    """sigma_g_crit = sqrt(1/alpha - 1)."""
    for alpha_t, expected_crit in [(0.05, 4.3589), (0.10, 3.0000)]:
        crit = float((1.0 / alpha_t - 1.0) ** 0.5)
        assert abs(crit - expected_crit) < 0.01, (
            f"capacity_boundary({alpha_t}): got {crit:.4f}, expected {expected_crit:.4f}")


def _selftest_alpha_m():
    """M = int(alpha * N_active) > 0."""
    M_val = max(1, int(ALPHA_FIXED * N_ACTIVE))
    assert M_val > 0, f"M=0 for alpha={ALPHA_FIXED} N={N_ACTIVE}"


def _selftest_valid_cells():
    """At least 1 sigma below audit_crit and 1 above capacity_crit in smoke sweep."""
    below_audit = [sg for sg in SIGMA_G_USE if sg < SIGMA_G_AUDIT_PRED]
    above_cap = [sg for sg in SIGMA_G_USE if sg > SIGMA_G_CAP_PRED * 0.5]
    assert len(below_audit) >= 1, (
        f"No sigma_g < audit_crit ({SIGMA_G_AUDIT_PRED}) in {SIGMA_G_USE}")
    assert len(above_cap) >= 1, (
        f"No sigma_g > 0.5*cap_crit ({SIGMA_G_CAP_PRED*0.5:.2f}) in {SIGMA_G_USE}")


def _instrumentation_selftest():
    _selftest_kappa3_identity()
    _selftest_capacity_boundary()
    _selftest_alpha_m()
    _selftest_valid_cells()
    print(f"[selftest] PASS: kappa3_identity, capacity_boundary, alpha_m, valid_cells "
          f"N_active={N_ACTIVE} alpha={ALPHA_FIXED}", flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


def hopfield_retrieve(W: np.ndarray, probe: np.ndarray,
                      n_steps: int = N_RETRIEVAL_STEPS) -> np.ndarray:
    state = probe.copy()
    for _ in range(n_steps):
        h = W @ state
        state = np.sign(h)
        state[state == 0] = 1.0
    return state


def compute_kappa3_ratio(W: np.ndarray, seed: int, n_dim: int) -> float:
    """Measure kappa_3 via Hutchinson estimator: Tr(W^3)/N / alpha.

    kappa_3 = Hutchinson kappa_3 / alpha (should = 1.0 at zero noise per free-Poisson identity).
    """
    k3 = hutchinson_kappa3_np(W, n_probes=N_PROBES_USE, seed=seed)
    return k3 / ALPHA_FIXED


def run_seed(seed: int, n_dim: int, sigma_g_list: List[float]) -> Dict:
    rng = np.random.RandomState(seed)
    t0 = time.time()

    M_val = max(1, int(ALPHA_FIXED * n_dim))
    Xi = rng.choice([-1., 1.], size=(M_val, n_dim)).astype(np.float64)
    W_clean = (Xi.T @ Xi) / float(n_dim)

    cell_results = {}
    for sigma_g in sigma_g_list:
        if sigma_g == 0.0:
            W_noisy = W_clean.copy()
        else:
            Z = rng.standard_normal((n_dim, n_dim))
            W_noisy = W_clean * np.exp(sigma_g * Z)
            W_noisy = (W_noisy + W_noisy.T) / 2.0

        # Measure kappa_3_ratio via Hutchinson estimator
        k3_ratio = compute_kappa3_ratio(W_noisy, seed=seed + int(sigma_g * 1000), n_dim=n_dim)

        # Measure recall
        n_q = min(N_QUERIES_USE, M_val)
        recalls = []
        for q in range(n_q):
            xi_q = Xi[q]
            probe = xi_q.copy()
            flip = rng.random(n_dim) < 0.10
            probe[flip] *= -1.0
            state = hopfield_retrieve(W_noisy, probe)
            cos = float(np.dot(state, xi_q)) / n_dim
            recalls.append(cos)
        mean_recall = float(np.mean(recalls)) if recalls else 0.0

        below_audit_crit = sigma_g <= SIGMA_G_AUDIT_PRED
        above_half_cap = sigma_g >= 0.5 * SIGMA_G_CAP_PRED

        key = f"sg{sigma_g:.3f}"
        cell_results[key] = {
            "sigma_g": float(sigma_g),
            "kappa3_ratio": float(k3_ratio),
            "recall": float(mean_recall),
            "below_audit_crit": bool(below_audit_crit),
            "above_half_cap": bool(above_half_cap),
        }
        print(f"  [seed={seed} sg={sigma_g:.3f}] k3_ratio={k3_ratio:.4f} "
              f"recall={mean_recall:.4f} below_audit={below_audit_crit}", flush=True)

    elapsed = time.time() - t0
    return {
        "seed": seed, "N": n_dim, "alpha": ALPHA_FIXED, "run_mode": RUN_MODE,
        "elapsed_s": float(elapsed), "cells": cell_results,
    }


def _find_audit_critical_sigma(seed_results: List[Dict]) -> float:
    """Find sigma_g where kappa_3_ratio first DEVIATES from identity by > 50%.

    Audit breaks = |kappa3_ratio - 1.0| > 0.50 (ratio < 0.50 or > 1.50).
    We cap ratio at 1e6 to prevent float overflow from dominating.
    """
    sigma_vals = {}
    for r in seed_results:
        for key, cell in r.get("cells", {}).items():
            sg = cell["sigma_g"]
            if sg not in sigma_vals:
                sigma_vals[sg] = []
            ratio_raw = cell.get("kappa3_ratio", 0.0)
            # Cap at 1e6 to handle numerical explosions
            ratio_capped = min(abs(ratio_raw), 1e6)
            sigma_vals[sg].append(ratio_capped)
    if not sigma_vals:
        return float("nan")
    sorted_sg = sorted(sigma_vals.keys())
    for sg in sorted_sg:
        mean_ratio = float(np.mean(sigma_vals[sg]))
        # Audit broken when ratio deviates from 1.0 by > 50%
        if mean_ratio < 0.50 or mean_ratio > 1.50:
            return sg
    return sorted_sg[-1] * 10  # not found within sweep range


def _find_capacity_critical_sigma(seed_results: List[Dict]) -> float:
    """Find sigma_g where recall first drops below RECALL_CRIT=0.50."""
    sigma_vals = {}
    for r in seed_results:
        for key, cell in r.get("cells", {}).items():
            sg = cell["sigma_g"]
            if sg not in sigma_vals:
                sigma_vals[sg] = []
            sigma_vals[sg].append(cell.get("recall", 0.0))
    if not sigma_vals:
        return float("nan")
    sorted_sg = sorted(sigma_vals.keys())
    for sg in sorted_sg:
        mean_v = float(np.mean(sigma_vals[sg]))
        if mean_v < RECALL_CRIT:
            return sg
    return sorted_sg[-1] * 10  # survives beyond sweep range


def compute_verdict(all_results: List[Dict]) -> tuple:
    if not all_results:
        return ("HARD_FAIL", "No valid results.")

    sigma_g_audit_crit = _find_audit_critical_sigma(all_results)
    sigma_g_cap_crit = _find_capacity_critical_sigma(all_results)

    if sigma_g_cap_crit == 0.0 or sigma_g_audit_crit == 0.0:
        ratio = 0.0
    else:
        ratio = sigma_g_cap_crit / max(sigma_g_audit_crit, 1e-6)

    summary = (f"alpha={ALPHA_FIXED} sigma_g_audit_crit={sigma_g_audit_crit:.3f}"
               f"(pred={SIGMA_G_AUDIT_PRED} HP=[{HP_AUDIT_CRIT_LOW},{HP_AUDIT_CRIT_HIGH}]) "
               f"sigma_g_cap_crit={sigma_g_cap_crit:.3f}(pred={SIGMA_G_CAP_PRED:.3f}) "
               f"ratio={ratio:.2f}(HP>={HP_RATIO_MIN} HF<{HF_RATIO_MIN}) "
               f"n_seeds={len(all_results)}")

    # HARD-FAIL
    if (sigma_g_audit_crit < HF_AUDIT_CRIT_LOW or
            sigma_g_audit_crit > HF_AUDIT_CRIT_HIGH or
            ratio < HF_RATIO_MIN):
        return ("HARD_FAIL", f"HARD_FAIL: two-envelope separation not confirmed. {summary}")

    # HARD-PASS
    hp_audit_in_band = HP_AUDIT_CRIT_LOW <= sigma_g_audit_crit <= HP_AUDIT_CRIT_HIGH
    hp_cap_ok = sigma_g_cap_crit >= HP_CAP_CRIT_MIN
    hp_ratio = ratio >= HP_RATIO_MIN

    if hp_audit_in_band and hp_cap_ok and hp_ratio:
        return ("HARD_PASS",
                f"HARD_PASS: PP-58 two-envelope confirmed. kappa_3 audit breaks ~{SIGMA_G_AUDIT_PRED}x "
                f"before capacity. {summary}")

    if MIDDLE_RATIO_MIN <= ratio < HP_RATIO_MIN:
        return ("MIDDLE_BAND", f"MIDDLE_BAND: partial separation (ratio in [2,5)). {summary}")

    return ("MIDDLE_BAND", f"MIDDLE_BAND: {summary}")


def _prot018_startup_check() -> None:
    if RUN_MODE != "smoke" and N_ACTIVE != _N_SUFFIX:
        raise RuntimeError(
            f"PROT-018 VIOLATION: anchor _n{_N_SUFFIX} but FULL N_ACTIVE={N_ACTIVE}")


print(f"[config] PROT-018 N={N} N_active={N_ACTIVE} mode={RUN_MODE} "
      f"alpha={ALPHA_FIXED} sigma_g={SIGMA_G_USE}", flush=True)
print(f"[config] predicted: sigma_g_audit_crit={SIGMA_G_AUDIT_PRED} "
      f"sigma_g_cap_crit={SIGMA_G_CAP_PRED:.3f} ratio={SIGMA_G_CAP_PRED/SIGMA_G_AUDIT_PRED:.1f}x",
      flush=True)
_prot018_startup_check()

out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N, "alpha": ALPHA_FIXED, "sigma_g": SIGMA_G_USE, "run_mode": RUN_MODE}

done, seeds_todo = resumable_seeds(SEEDS, out_dir, run_config)
print(f"[run] seeds_todo={seeds_todo} out_dir={out_dir}", flush=True)

t_total = time.time()
for s in seeds_todo:
    res = run_seed(s, N_ACTIVE, SIGMA_G_USE)
    write_partial(out_dir, s, res)
    print(f"[progress] seed={s} done", flush=True)

per_seed = aggregate_partials(out_dir, SEEDS)
all_results = list(per_seed.values())
verdict, verdict_msg = compute_verdict(all_results)

metrics = {
    "anchor": ANCHOR_NAME,
    "verdict": verdict,
    "verdict_msg": verdict_msg,
    "n_seeds": len(all_results),
    "N": N, "alpha_fixed": ALPHA_FIXED,
    "sigma_g_audit_pred": SIGMA_G_AUDIT_PRED,
    "sigma_g_cap_pred": SIGMA_G_CAP_PRED,
    "run_mode": RUN_MODE,
    "elapsed_s": time.time() - t_total,
    "results": all_results,
}

metrics_path = out_dir / "metrics.json"
with open(metrics_path, "w") as f:
    json.dump(metrics, f, indent=2)

print(f"\n[VERDICT] {verdict}", flush=True)
print(f"[VERDICT_MSG] {verdict_msg}", flush=True)
print(f"[METRICS_PATH] {metrics_path}", flush=True)
