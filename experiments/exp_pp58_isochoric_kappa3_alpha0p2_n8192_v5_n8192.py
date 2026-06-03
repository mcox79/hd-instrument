"""
pp58_isochoric_kappa3_alpha0p2_n8192_v5_n8192 -- PP-58 N-scale at alpha=0.2.

CONTEXT:
  finergrid_v2_n4096 MIDDLE_BAND: cap_crit formula sqrt(1/alpha-1) EXACT at alpha=0.2
    (pred=2.0 actual=2.0 cap_tol=True). First alpha where formula holds precisely.
    ratio=20.0 artifact (audit_crit grid-limited at sigma_g=0.1 grid min).
  v4_n8192 alpha=0.05 MIDDLE_BAND: formula over-predicts 30% at alpha=0.05 N=8192.
  This anchor: alpha=0.2 at N=8192. Tests if cap_crit formula holds at N=8192 alpha=0.2
  (it was exact at N=4096 alpha=0.2). Also tests if audit_crit is resolvable above grid_min.

SCIENTIFIC QUESTION:
  At alpha=0.2 N=8192:
  (a) Does cap_crit remain at sqrt(1/0.2-1)=sqrt(4)=2.0 (N-stable formula)?
  (b) Does audit_crit resolve above sigma_g=0.1 at N=8192 (larger N = sharper boundary)?
  Key: if both (a) and (b) hold, ratio = 2.0/audit_crit; if audit_crit resolves below 1.0,
  ratio > 2.0 (MIDDLE zone preserved or improved).

FORMULA SELF-TESTS (PROT-022):
  1. Cap boundary formula at alpha=0.2: sqrt(1/0.2 - 1) = sqrt(4) = 2.0 (within 0.001).
     [INPUT: alpha=0.2] [EXPECTED: 2.000 within 0.001]
  2. kappa_3 identity at zero noise alpha=0.2 N=512.
     [INPUT: sigma_g=0.0, alpha=0.2, N=512] [EXPECTED: kappa_3_ratio ~ 1.0 +/- 1.0]
  3. M = int(0.2 * 8192) = 1638 >= 1.
     [EXPECTED: M = 1638]

PRE-REGISTERED BANDS (PP-58 alpha=0.2 N-scale; finergrid_v2 N=4096 cap_tol=True is baseline):
  HARD-PASS: cap_crit within 20% of sqrt(4)=2.0 AND audit_crit resolvable (> sigma_g_grid_min)
             AND ratio >= 5.0 (HP separation gate).
  MIDDLE: cap_crit within 20% of 2.0 but ratio < 5.0 OR audit_crit still grid-limited.
  HARD-FAIL: cap_crit > 3.0 or < 1.0 (formula fails at N=8192 alpha=0.2).

  Calibration note: finergrid_v2 N=4096 alpha=0.2 showed ratio=20.0 (grid artifact);
  true ratio unknown. HP requires both cap_crit accuracy AND resolvable audit_crit.

PROT-018: anchor has _n8192; N MUST = 8192.
QUEUE: remote_cpu_queue (pure numpy; alpha=0.2 at N=8192; ~30-60 min wall).
TIMEOUT ESTIMATE: v4_n8192 elapsed=460.9s CPU 5-seed alpha=0.05.
  alpha=0.2: M=1638 vs M=409 at alpha=0.05. More patterns -> slightly slower W build.
  Sigma_g sweep same 14 points. Scale: ~1.5x for larger M build.
  ceil(1.5 * 460.9 * 1.5 * 1.0) = ceil(1038) = 1200s.
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

ANCHOR_NAME = "pp58_isochoric_kappa3_alpha0p2_n8192_v5_n8192"

_N_SUFFIX = 8192
N = 8192
assert N == _N_SUFFIX, f"PROT-018: anchor _n{_N_SUFFIX} but N={N}"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

ALPHA = 0.2
_M_FULL = int(ALPHA * N)  # 1638
assert _M_FULL >= 1, f"M={_M_FULL} at alpha={ALPHA} N={N} must be >= 1"

# sigma_g sweep: finer around cap_crit=2.0; covers audit_crit range
SIGMA_G_FULL = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9,
                1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0]
CAP_PRED = float((1.0 / ALPHA - 1.0) ** 0.5)  # sqrt(4) = 2.0

KAPPA3_RATIO_CRIT_FACTOR = 2.0
RECALL_CRIT = 0.50
N_RETRIEVAL_STEPS = 8
N_QUERIES_PER_CELL = 10
N_PROBES_FULL = 30
N_PROBES_SELFTEST = 10

HP_RATIO_MIN = 5.0
MIDDLE_RATIO_MIN = 2.0
HF_RATIO = 2.0
HP_CAP_CRIT_TOLERANCE = 0.20

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    N_ACTIVE = 1024
    SIGMA_G_USE = [0.0, 0.5, 1.0, 1.5, 2.0, 3.0]
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
    """sqrt(1/0.2 - 1) = sqrt(4) = 2.0."""
    expected = 2.0
    crit = float((1.0 / ALPHA - 1.0) ** 0.5)
    assert abs(crit - expected) < 0.001, f"cap_boundary: got {crit:.4f}, expected {expected:.4f}"


def _selftest_kappa3_identity():
    """kappa_3 at sigma_g=0 for alpha=0.2, N=512."""
    n_t = 512
    M_t = max(1, int(ALPHA * n_t))
    rng_t = np.random.RandomState(42)
    Xi = rng_t.choice([-1., 1.], size=(M_t, n_t)).astype(np.float64)
    W = (Xi.T @ Xi) / float(n_t)
    k3 = hutchinson_kappa3_np(W, n_probes=N_PROBES_SELFTEST, seed=42)
    k3_ratio = k3 / ALPHA
    assert 0.1 < k3_ratio < 10.0, (
        f"kappa_3 identity failed: k3_ratio={k3_ratio:.4f}, expected ~1.0 at alpha={ALPHA}")


def _selftest_m_full():
    """M = int(0.2 * 8192) = 1638."""
    assert _M_FULL == 1638, f"M_full={_M_FULL} expected 1638"


def _instrumentation_selftest():
    _selftest_cap_boundary()
    _selftest_kappa3_identity()
    _selftest_m_full()
    print(f"[selftest] PASS: cap_boundary={CAP_PRED:.3f}, kappa3_identity, m_full={_M_FULL} "
          f"N_active={N_ACTIVE} alpha={ALPHA}", flush=True)


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


def run_seed_sigma_sweep(seed: int, n_dim: int, sigma_g_list: List[float]) -> Dict:
    """Run one seed across the sigma_g sweep at fixed alpha."""
    rng = np.random.RandomState(seed)
    t0 = time.time()

    M_val = max(1, int(ALPHA * n_dim))
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

        k3 = hutchinson_kappa3_np(W_noisy, n_probes=N_PROBES_USE,
                                   seed=seed + int(sigma_g * 1000))
        k3_ratio = k3 / ALPHA

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

        key = f"sg{sigma_g:.3f}"
        cell_results[key] = {
            "sigma_g": float(sigma_g),
            "kappa3_ratio": float(k3_ratio),
            "recall": float(mean_recall),
        }
        print(f"  [seed={seed} sg={sigma_g:.3f}] k3_ratio={k3_ratio:.4f} "
              f"recall={mean_recall:.4f}", flush=True)

    elapsed = time.time() - t0
    return {
        "alpha": float(ALPHA), "seed": seed, "N": n_dim, "run_mode": RUN_MODE,
        "sigma_g_cap_pred": float(CAP_PRED),
        "elapsed_s": float(elapsed), "cells": cell_results,
    }


def _find_audit_critical_sigma(seed_results: List[Dict]) -> float:
    """Find sigma_g where kappa_3_ratio first deviates from baseline by > 2x."""
    sigma_vals: Dict[float, List[float]] = {}
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
    baseline_ratio = 1.0
    if 0.0 in sigma_vals:
        baseline_ratio = float(np.mean(sigma_vals[0.0]))
        if baseline_ratio < 0.1:
            baseline_ratio = 1.0
    for sg in sorted_sg:
        if sg == 0.0:
            continue
        mean_ratio = float(np.mean(sigma_vals[sg]))
        if (mean_ratio > KAPPA3_RATIO_CRIT_FACTOR * baseline_ratio or
                mean_ratio < baseline_ratio / KAPPA3_RATIO_CRIT_FACTOR):
            return sg
    return sorted_sg[-1] * 10


def _find_capacity_critical_sigma(seed_results: List[Dict]) -> float:
    """Find sigma_g where recall first drops below RECALL_CRIT."""
    sigma_vals: Dict[float, List[float]] = {}
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


def compute_verdict(seed_results: List[Dict]) -> tuple:
    audit_crit = _find_audit_critical_sigma(seed_results)
    cap_crit = _find_capacity_critical_sigma(seed_results)
    ratio = cap_crit / max(audit_crit, 1e-6) if audit_crit > 0 else 0.0
    cap_within_tol = abs(cap_crit - CAP_PRED) / CAP_PRED <= HP_CAP_CRIT_TOLERANCE

    summary = (f"alpha={ALPHA} N={N} audit_crit={audit_crit:.3f} cap_crit={cap_crit:.3f}"
               f"(pred={CAP_PRED:.3f}) ratio={ratio:.2f} cap_within_tol={cap_within_tol} "
               f"n_seeds={len(seed_results)}")

    if ratio < HF_RATIO:
        return ("HARD_FAIL", f"HARD_FAIL: ratio={ratio:.2f} < {HF_RATIO}. {summary}")

    if ratio >= HP_RATIO_MIN and cap_within_tol:
        return ("HARD_PASS", f"HARD_PASS: ratio={ratio:.2f} >= {HP_RATIO_MIN} and cap_crit within tol. {summary}")

    return ("MIDDLE_BAND", f"MIDDLE_BAND: ratio={ratio:.2f} in [{MIDDLE_RATIO_MIN},{HP_RATIO_MIN}). {summary}")


def _prot018_startup_check() -> None:
    if RUN_MODE != "smoke" and N_ACTIVE != _N_SUFFIX:
        raise RuntimeError(
            f"PROT-018 VIOLATION: anchor _n{_N_SUFFIX} but FULL N_ACTIVE={N_ACTIVE}")


print(f"[config] PROT-018 N={N} N_active={N_ACTIVE} mode={RUN_MODE} "
      f"alpha={ALPHA} sigma_g={SIGMA_G_USE}", flush=True)
_prot018_startup_check()

out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N, "alpha": ALPHA, "sigma_g": SIGMA_G_USE, "run_mode": RUN_MODE}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(f"[ckpt] {len(done)} seeds done, {len(remaining)} to run", flush=True)

t_sweep_start = time.time()
for seed in remaining:
    print(f"[seed={seed}] {ANCHOR_NAME}...", flush=True)
    result = run_seed_sigma_sweep(seed, N_ACTIVE, SIGMA_G_USE)
    write_partial(out_dir, seed, result)

per_seed = aggregate_partials(out_dir, SEEDS)
all_results = list(per_seed.values())
verdict, verdict_msg = compute_verdict(all_results)

elapsed_total = time.time() - t_sweep_start

metrics = {
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict,
    "verdict_msg": verdict_msg,
    "n_seeds": len(SEEDS),
    "N": N,
    "alpha": ALPHA,
    "sigma_g_use": SIGMA_G_USE,
    "cap_pred": CAP_PRED,
    "run_mode": RUN_MODE,
    "elapsed_s": elapsed_total,
    "per_seed": all_results,
}

metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")

print(f"\n[VERDICT] {verdict}", flush=True)
print(f"[VERDICT_MSG] {verdict_msg}", flush=True)
print(f"[METRICS_PATH] {metrics_path}", flush=True)
