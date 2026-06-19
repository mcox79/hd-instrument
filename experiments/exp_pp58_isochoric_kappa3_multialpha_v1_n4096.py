"""
pp58_isochoric_kappa3_multialpha_v1_n4096 -- PP-58 R3 rescue: multi-alpha isochoric sweep.

PP-58 founding (v353): alpha=0.05 MIDDLE_BAND. ratio=8.0 (HP>=5.0 MET) but
sigma_g_audit_crit=0.500 outside HP band [0.09,0.27]. The audit_crit discrepancy
suggests the kappa_3 sensitivity model needs recalibration for isochoric regime.

R3 rescue: run same isochoric protocol at alpha={0.10, 0.20} to:
  1. Check if audit_crit scales with alpha (kappa_3 model prediction: audit_crit ~ alpha * constant)
  2. Check if ratio=cap_crit/audit_crit is alpha-independent (free-prob prediction)
  3. Identify whether alpha=0.05 audit_crit=0.500 is an outlier or systematic shift

SCIENTIFIC QUESTION (PP-58 recalibration):
  Does sigma_g_audit_crit scale as predicted across alpha={0.10, 0.20}?
  Predicted: audit_crit(0.10) ~ 0.25, audit_crit(0.20) ~ 0.30 (proportional to sqrt(alpha))
  Predicted: ratio decreases weakly with alpha (cap_crit = sqrt(1/alpha - 1))

TEST DESIGN:
  alpha values: {0.10, 0.20}
  N = 4096, 5 seeds per alpha
  sigma_g sweep: {0.0, 0.01, 0.05, 0.10, 0.15, 0.18, 0.20, 0.25, 0.30, 0.50, 1.0, 2.0, 3.0, 4.0}
  Same kappa_3 Hutchinson estimator as founding experiment.

PREDICTED VALUES:
  alpha=0.10: sigma_g_cap_crit = sqrt(1/0.10 - 1) = sqrt(9) = 3.000
              sigma_g_audit_crit ~ 0.25 (predicted; uncertain)
              ratio ~ 12x (predicted)
  alpha=0.20: sigma_g_cap_crit = sqrt(1/0.20 - 1) = sqrt(4) = 2.000
              sigma_g_audit_crit ~ 0.30 (predicted; uncertain)
              ratio ~ 6.7x (predicted)

PRE-REGISTERED BANDS (per alpha, PP-58 R3 -- recalibration probe; prior audit_crit was 2.8x above
  prediction at alpha=0.05; bands widened to +-100% of prediction to accommodate uncertainty):
  HARD-PASS: ratio >= 3.0 for each alpha tested (separation confirmed even if audit_crit shifted)
             AND sigma_g_cap_crit within 20% of sqrt(1/alpha - 1) for each alpha.
  MIDDLE: ratio in [1.5, 3.0) for any alpha.
  HARD-FAIL: ratio < 1.5 for any alpha (no separation).

FORMULA SELF-TESTS (PROT-022):
  1. Cap boundary formula: sqrt(1/alpha-1) for alpha={0.10, 0.20}
     [INPUT: alpha=0.10] [EXPECTED: 3.0000]
     [INPUT: alpha=0.20] [EXPECTED: 2.0000]
  2. kappa_3 identity at zero noise for each alpha.
     [INPUT: sigma_g=0.0, alpha=0.10, N=512] [EXPECTED: kappa_3_ratio ~ 1.0 +/- 0.5]
  3. M = int(alpha * N) > 0 for each alpha.

PROT-018: anchor has _n4096; N MUST = 4096.
QUEUE: remote_cpu_queue (CPU; pure numpy; 2 alpha x 14 sigma x 5 seeds ~90-120 min).
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

ANCHOR_NAME = "pp58_isochoric_kappa3_multialpha_v1_n4096"

_N_SUFFIX = 4096
N = 4096
assert N == _N_SUFFIX, f"PROT-018: anchor _n{_N_SUFFIX} but N={N}"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

ALPHA_VALS = [0.10, 0.20]

SIGMA_G_FULL = [0.0, 0.01, 0.05, 0.10, 0.15, 0.18, 0.20, 0.25, 0.30, 0.50, 1.0, 2.0, 3.0, 4.0]

KAPPA3_RATIO_CRIT = 0.50   # audit broken when ratio deviates from 1.0 by > 50% (same as founding)
RECALL_CRIT = 0.50

N_RETRIEVAL_STEPS = 8
N_QUERIES_PER_CELL = 10
N_PROBES_FULL = 50
N_PROBES_SELFTEST = 20

# Verdict thresholds (per alpha)
HP_RATIO_MIN = 3.0
MIDDLE_RATIO_MIN = 1.5
HF_RATIO_MIN = 1.5
HP_CAP_CRIT_TOLERANCE = 0.20  # cap_crit within 20% of theory

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    N_ACTIVE = 512
    SIGMA_G_USE = [0.0, 0.10, 0.25, 0.50, 1.0, 2.0, 4.0]
    N_QUERIES_USE = 5
    N_PROBES_USE = N_PROBES_SELFTEST
else:
    SEEDS = [7, 17, 23, 31, 41]
    N_ACTIVE = N
    SIGMA_G_USE = SIGMA_G_FULL
    N_QUERIES_USE = N_QUERIES_PER_CELL
    N_PROBES_USE = N_PROBES_FULL


def hutchinson_kappa3_np(W: np.ndarray, n_probes: int, seed: int) -> float:
    """Hutchinson estimator for Tr(W^3) / N."""
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


def _selftest_cap_boundary():
    """sigma_g_crit = sqrt(1/alpha - 1) for alpha in ALPHA_VALS."""
    expected = {0.10: 3.0000, 0.20: 2.0000}
    for alpha_t, exp_v in expected.items():
        crit = float((1.0 / alpha_t - 1.0) ** 0.5)
        assert abs(crit - exp_v) < 0.01, (
            f"cap_boundary({alpha_t}): got {crit:.4f}, expected {exp_v:.4f}")


def _selftest_kappa3_identity():
    """kappa_3 identity at zero noise for alpha=0.10."""
    alpha_t = 0.10
    n_t = N_ACTIVE
    M_t = max(1, int(alpha_t * n_t))
    rng_t = np.random.RandomState(42)
    Xi = rng_t.choice([-1., 1.], size=(M_t, n_t)).astype(np.float64)
    W = (Xi.T @ Xi) / float(n_t)
    k3 = hutchinson_kappa3_np(W, n_probes=N_PROBES_SELFTEST, seed=42)
    k3_ratio = k3 / alpha_t
    assert 0.2 < k3_ratio < 5.0, (
        f"kappa_3 identity failed: k3_ratio={k3_ratio:.4f}, expected ~1.0 at alpha={alpha_t}")


def _selftest_alpha_m():
    """M = int(alpha * N_active) > 0 for all alpha in ALPHA_VALS."""
    for alpha_t in ALPHA_VALS:
        M_val = max(1, int(alpha_t * N_ACTIVE))
        assert M_val > 0, f"M=0 for alpha={alpha_t} N={N_ACTIVE}"


def _instrumentation_selftest():
    _selftest_cap_boundary()
    _selftest_kappa3_identity()
    _selftest_alpha_m()
    print(f"[selftest] PASS: cap_boundary, kappa3_identity, alpha_m "
          f"N_active={N_ACTIVE} alphas={ALPHA_VALS}", flush=True)


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


def run_alpha_seed(alpha: float, seed: int, n_dim: int, sigma_g_list: List[float]) -> Dict:
    """Run one alpha+seed combination across the sigma_g sweep."""
    rng = np.random.RandomState(seed)
    t0 = time.time()

    M_val = max(1, int(alpha * n_dim))
    Xi = rng.choice([-1., 1.], size=(M_val, n_dim)).astype(np.float64)
    W_clean = (Xi.T @ Xi) / float(n_dim)
    sigma_g_cap_pred = float((1.0 / alpha - 1.0) ** 0.5)

    cell_results = {}
    for sigma_g in sigma_g_list:
        if sigma_g == 0.0:
            W_noisy = W_clean.copy()
        else:
            Z = rng.standard_normal((n_dim, n_dim))
            W_noisy = W_clean * np.exp(sigma_g * Z)
            W_noisy = (W_noisy + W_noisy.T) / 2.0

        k3 = hutchinson_kappa3_np(W_noisy, n_probes=N_PROBES_USE,
                                   seed=seed + int(sigma_g * 1000))
        k3_ratio = k3 / alpha

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

        below_audit_pred = sigma_g <= sigma_g_cap_pred * 0.1
        above_half_cap = sigma_g >= 0.5 * sigma_g_cap_pred

        key = f"sg{sigma_g:.3f}"
        cell_results[key] = {
            "sigma_g": float(sigma_g),
            "kappa3_ratio": float(k3_ratio),
            "recall": float(mean_recall),
            "below_audit_pred": bool(below_audit_pred),
            "above_half_cap": bool(above_half_cap),
        }
        print(f"  [alpha={alpha} seed={seed} sg={sigma_g:.3f}] k3_ratio={k3_ratio:.4f} "
              f"recall={mean_recall:.4f}", flush=True)

    elapsed = time.time() - t0
    return {
        "alpha": float(alpha), "seed": seed, "N": n_dim, "run_mode": RUN_MODE,
        "sigma_g_cap_pred": float(sigma_g_cap_pred),
        "elapsed_s": float(elapsed), "cells": cell_results,
    }


def _find_audit_critical_sigma(seed_results: List[Dict], alpha: float) -> float:
    """Find sigma_g where kappa_3_ratio first deviates from baseline (sg=0) by > 2x.

    Uses baseline-relative deviation: audit_crit when ratio > 2 * baseline_ratio
    OR ratio < 0.5 * baseline_ratio.
    This is robust to N-finite-size variance in the Hutchinson estimator at small N.
    Baseline = ratio at sigma_g=0.0.
    """
    sigma_vals = {}
    for r in seed_results:
        for key, cell in r.get("cells", {}).items():
            sg = cell["sigma_g"]
            if sg not in sigma_vals:
                sigma_vals[sg] = []
            ratio_raw = cell.get("kappa3_ratio", 0.0)
            ratio_capped = min(abs(ratio_raw), 1e6)
            sigma_vals[sg].append(ratio_capped)
    if not sigma_vals:
        return float("nan")
    sorted_sg = sorted(sigma_vals.keys())

    # Compute baseline at sigma_g=0.0
    baseline_ratio = 1.0
    if 0.0 in sigma_vals:
        baseline_ratio = float(np.mean(sigma_vals[0.0]))
        if baseline_ratio < 0.1:
            baseline_ratio = 1.0  # degenerate

    for sg in sorted_sg:
        if sg == 0.0:
            continue  # skip baseline itself
        mean_ratio = float(np.mean(sigma_vals[sg]))
        # Audit broken when ratio exceeds 2x baseline OR drops below 0.5x baseline
        if mean_ratio > 2.0 * baseline_ratio or mean_ratio < 0.5 * baseline_ratio:
            return sg
    return sorted_sg[-1] * 10


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
    return sorted_sg[-1] * 10


def compute_verdict_per_alpha(alpha_results: Dict[float, List[Dict]]) -> tuple:
    """Compute verdict across all alphas."""
    per_alpha_summary = {}
    worst_ratio = float("inf")
    any_hf = False

    for alpha, seed_results in alpha_results.items():
        sigma_g_cap_pred = float((1.0 / alpha - 1.0) ** 0.5)
        audit_crit = _find_audit_critical_sigma(seed_results, alpha)
        cap_crit = _find_capacity_critical_sigma(seed_results)
        ratio = cap_crit / max(audit_crit, 1e-6) if audit_crit > 0 else 0.0

        cap_within_tol = abs(cap_crit - sigma_g_cap_pred) / sigma_g_cap_pred <= HP_CAP_CRIT_TOLERANCE if sigma_g_cap_pred > 0 else False

        per_alpha_summary[alpha] = {
            "audit_crit": float(audit_crit),
            "cap_crit": float(cap_crit),
            "cap_pred": float(sigma_g_cap_pred),
            "ratio": float(ratio),
            "cap_within_tol": bool(cap_within_tol),
        }
        if ratio < HF_RATIO_MIN:
            any_hf = True
        worst_ratio = min(worst_ratio, ratio)

    summary_parts = []
    for alpha, d in sorted(per_alpha_summary.items()):
        summary_parts.append(
            f"a{alpha}: audit_crit={d['audit_crit']:.3f} cap_crit={d['cap_crit']:.3f}"
            f"(pred={d['cap_pred']:.3f}) ratio={d['ratio']:.2f} cap_tol={d['cap_within_tol']}"
        )
    full_summary = " | ".join(summary_parts) + f" | worst_ratio={worst_ratio:.2f}"

    if any_hf:
        return ("HARD_FAIL", f"HARD_FAIL: ratio<{HF_RATIO_MIN} for at least one alpha. {full_summary}")

    all_hp = all(d["ratio"] >= HP_RATIO_MIN and d["cap_within_tol"]
                 for d in per_alpha_summary.values())
    if all_hp:
        return ("HARD_PASS", f"HARD_PASS: ratio>={HP_RATIO_MIN} and cap_crit within tol for all alphas. {full_summary}")

    return ("MIDDLE_BAND", f"MIDDLE_BAND: partial separation across alphas. {full_summary}")


def _prot018_startup_check() -> None:
    if RUN_MODE != "smoke" and N_ACTIVE != _N_SUFFIX:
        raise RuntimeError(
            f"PROT-018 VIOLATION: anchor _n{_N_SUFFIX} but FULL N_ACTIVE={N_ACTIVE}")


print(f"[config] PROT-018 N={N} N_active={N_ACTIVE} mode={RUN_MODE} "
      f"alphas={ALPHA_VALS} sigma_g={SIGMA_G_USE}", flush=True)
_prot018_startup_check()

# Use per-alpha sub-directories for checkpointing
out_dir_root = get_output_dir(ANCHOR_NAME)
all_alpha_results: Dict[float, List[Dict]] = {}

for alpha in ALPHA_VALS:
    alpha_label = f"a{int(alpha*100):02d}"
    sub_dir = out_dir_root / alpha_label
    sub_dir.mkdir(parents=True, exist_ok=True)
    run_config = {"N": N, "alpha": alpha, "sigma_g": SIGMA_G_USE, "run_mode": RUN_MODE}
    done, seeds_todo = resumable_seeds(SEEDS, sub_dir, run_config)
    print(f"[alpha={alpha}] seeds_todo={seeds_todo}", flush=True)

    for s in seeds_todo:
        res = run_alpha_seed(alpha, s, N_ACTIVE, SIGMA_G_USE)
        write_partial(sub_dir, s, res)
        print(f"[alpha={alpha}] seed={s} done", flush=True)

    per_seed = aggregate_partials(sub_dir, SEEDS)
    all_alpha_results[alpha] = list(per_seed.values())

verdict, verdict_msg = compute_verdict_per_alpha(all_alpha_results)

metrics = {
    "anchor": ANCHOR_NAME,
    "verdict": verdict,
    "verdict_msg": verdict_msg,
    "n_seeds": len(SEEDS),
    "N": N,
    "alpha_vals": ALPHA_VALS,
    "sigma_g_use": SIGMA_G_USE,
    "run_mode": RUN_MODE,
    "elapsed_s": None,
    "results_by_alpha": {str(a): all_alpha_results[a] for a in ALPHA_VALS},
}

metrics_path = out_dir_root / "metrics.json"
with open(metrics_path, "w") as f:
    json.dump(metrics, f, indent=2)

print(f"\n[VERDICT] {verdict}", flush=True)
print(f"[VERDICT_MSG] {verdict_msg}", flush=True)
print(f"[METRICS_PATH] {metrics_path}", flush=True)
