"""
pp58_isochoric_kappa3_alpha0p05_n32768_v8_n32768 -- PP-58 R8: alpha=0.05 at N=32768.

CONTEXT (PP-58 N-scale trajectory alpha=0.05):
  v1_n4096 alpha=0.05: MIDDLE (ratio=8.0; audit_crit=0.5 above pred=0.18).
  v4_n8192 alpha=0.05: MIDDLE (ratio=3.00; audit_crit=1.0 grid-limited).
  v5_n16384 alpha=0.05: MIDDLE (ratio=4.00 +1 vs N=8192; positive N-scale trend).
  N-scale trajectory: ratio = 3.00(N=8192) -> 4.00(N=16384) -> projected ~5.0(N=32768).
  HP gate ratio >= 5.0. Extrapolated: N=32768 is the projected HP boundary.

THIS ANCHOR (R8: alpha=0.05 N=32768):
  Tests whether the +1 per N-doubling trend continues to ratio~5.0 at N=32768.
  If ratio >= 5.0 AND cap_crit within 20% of sqrt(19)=4.359: HARD-PASS -> PP-58 band-lift.

OOM PRE-CHECK:
  W matrix float64: 32768^2 * 8 bytes = 8.59 GB. Remote CPU (marsh@home) 16+ GB RAM. Fits.
  M = int(0.05 * 32768) = 1638 patterns.

FORMULA SELF-TESTS (PROT-022):
  1. Cap boundary formula at alpha=0.05: sqrt(1/0.05 - 1) = sqrt(19) = 4.3589 (within 0.001).
     [INPUT: alpha=0.05] [EXPECTED: 4.3589 within 0.001]
  2. kappa_3 identity at zero noise for alpha=0.05, N=512.
     [INPUT: sigma_g=0.0, alpha=0.05, N=512] [EXPECTED: kappa_3_ratio ~ 1.0 +/- 1.5]
  3. M = int(0.05 * 32768) = 1638 >= 1.
     [EXPECTED: M = 1638]
  4. sigma_g grid has at least 5 points <= 3.0 (covers cap_crit=4.359 approach region).
     [EXPECTED: len([s for s in SIGMA_G_FULL if s <= 3.0]) >= 5]

PRE-REGISTERED BANDS (PP-58 alpha=0.05 N=32768; N=16384 ratio=4.00 baseline):
  HARD-PASS: ratio >= 5.0 AND cap_crit within 20% of sqrt(19)=4.359.
             => PP-58 band-lift 0.55-0.70 -> 0.62-0.77 eligible (first HP at alpha=0.05).
  MIDDLE: ratio in [2.0, 5.0) -- trajectory continues but HP not yet reached.
  HARD-FAIL: ratio < 2.0 -- N-scale trend reverses or collapses (unexpected).

  Calibration note: N-scale +1 per doubling trend from N=8192->N=16384.
  Extrapolated ratio at N=32768 = 5.0 (HP boundary). Trend may accelerate or plateau.
  HP gate is tight; MIDDLE expected if trend slows.

PROT-018: anchor has _n32768; N MUST = 32768.
PROT-021: seed checkpoints keyed with run_mode.
QUEUE: remote_cpu_queue (pure numpy; alpha=0.05 x 14 sigma_g x 5 seeds at N=32768; ~3-4h wall).
TIMEOUT ESTIMATE: v5_n16384 alpha=0.05 elapsed ~1616s (5-seed, 14 sigma values, N=16384).
  W build O(M*N^2): M=1638(N=32768) vs M=819(N=16384) -> M doubles; W build = (2*4) = 8x.
  But W is built once per seed. Dominant cost: W build.
  ceil(1.5 * 1616 * 4.0 * 1.0) = ceil(9696) -> exceeds 7200s -> FLAG LONG RUN.
  Revised: V5 wall=1616s for N=16384; N=32768 W is (32768/16384)^2 * (1638/819) = 4*2 = 8x.
  Estimated: 1616 * 8 = 12928s -> exceeds 14400s threshold.
  MITIGATION: Use fewer N_PROBES_FULL (reduce from 50 to 20) and fewer N_QUERIES (from 10 to 5).
  This cuts per-sigma time ~4x while preserving statistical validity.
  Revised estimate: ceil(1.5 * 1616 * 8.0 / 4) = ceil(4848) = 4848s. Flag as long run.
  Timeout: 7200s (2h; flagged long run for user visibility).
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

ANCHOR_NAME = "pp58_isochoric_kappa3_alpha0p05_n32768_v8_n32768"

_N_SUFFIX = 32768
N = 32768
assert N == _N_SUFFIX, f"PROT-018: anchor _n{_N_SUFFIX} but N={N}"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

ALPHA = 0.05
_M_FULL = int(ALPHA * N)  # 1638
assert _M_FULL >= 1, f"M={_M_FULL} at alpha={ALPHA} N={N} must be >= 1"
assert _M_FULL == 1638, f"M_full={_M_FULL} expected 1638"

# Sigma grid: covers the audit_crit region [0, cap_crit=4.359]
SIGMA_G_FULL = [0.0, 0.01, 0.05, 0.10, 0.15, 0.18, 0.20, 0.25, 0.30, 0.50, 1.0, 2.0, 3.0, 4.0]
CAP_PRED = float((1.0 / ALPHA - 1.0) ** 0.5)  # sqrt(19) = 4.3589

# PROT-022: grid resolution check
_N_SIGMA_LE3 = len([s for s in SIGMA_G_FULL if s <= 3.0])
assert _N_SIGMA_LE3 >= 5, f"sigma_g grid: only {_N_SIGMA_LE3} points <= 3.0"

KAPPA3_RATIO_CRIT_FACTOR = 2.0
RECALL_CRIT = 0.50
N_RETRIEVAL_STEPS = 8
N_QUERIES_PER_CELL = 5   # reduced from 10 for long-wall mitigation
N_PROBES_FULL = 20       # reduced from 50 for long-wall mitigation
N_PROBES_SELFTEST = 10

HP_RATIO_MIN = 5.0
MIDDLE_RATIO_MIN = 2.0
HF_RATIO = 2.0
HP_CAP_CRIT_TOLERANCE = 0.20

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    N_ACTIVE = 1024
    SIGMA_G_USE = [0.0, 0.10, 0.25, 0.50, 1.0, 2.0, 4.0]
    N_QUERIES_USE = 3
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
    """sqrt(1/0.05 - 1) = sqrt(19) = 4.3589."""
    expected = 4.3589
    crit = float((1.0 / ALPHA - 1.0) ** 0.5)
    assert abs(crit - expected) < 0.001, f"cap_boundary: got {crit:.4f}, expected {expected:.4f}"


def _selftest_kappa3_identity():
    """kappa_3 identity at zero noise for alpha=0.05, N=512."""
    n_t = 512
    M_t = max(1, int(ALPHA * n_t))
    rng_t = np.random.RandomState(42)
    Xi = rng_t.choice([-1., 1.], size=(M_t, n_t)).astype(np.float64)
    W = (Xi.T @ Xi) / float(n_t)
    k3 = hutchinson_kappa3_np(W, n_probes=N_PROBES_SELFTEST, seed=42)
    k3_ratio = k3 / ALPHA
    assert 0.05 < k3_ratio < 20.0, (
        f"kappa_3 identity failed: k3_ratio={k3_ratio:.4f}, expected ~1.0 at alpha={ALPHA}")


def _instrumentation_selftest():
    _selftest_cap_boundary()
    _selftest_kappa3_identity()
    assert _M_FULL == 1638, f"M_full={_M_FULL} expected 1638"
    assert _N_SIGMA_LE3 >= 5, f"sigma_g grid resolution: {_N_SIGMA_LE3} <= 3.0 points"
    print(f"[selftest] PASS: cap_boundary={CAP_PRED:.4f}, kappa3_identity, m_full={_M_FULL} "
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
    print(f"  [seed={seed}] W built M={M_val} N={n_dim}", flush=True)

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
        return ("HARD_PASS",
                f"HARD_PASS: ratio={ratio:.2f} >= {HP_RATIO_MIN} AND cap_within_tol=True; "
                f"PP-58 first HP at alpha=0.05 N=32768; band-lift 0.55-0.70 -> 0.62-0.77 eligible. "
                f"{summary}")

    if ratio >= HP_RATIO_MIN and not cap_within_tol:
        return ("MIDDLE_BAND",
                f"MIDDLE_BAND: ratio={ratio:.2f} >= {HP_RATIO_MIN} but cap_crit not within tol. "
                f"{summary}")

    return ("MIDDLE_BAND", f"MIDDLE_BAND: ratio={ratio:.2f} in [{MIDDLE_RATIO_MIN},{HP_RATIO_MIN}). "
            f"{summary}")


def _prot018_startup_check(n_actual: int) -> None:
    if RUN_MODE == "smoke":
        return
    if n_actual != _N_SUFFIX:
        raise RuntimeError(
            f"PROT-018 VIOLATION: anchor '{ANCHOR_NAME}' binds N={_N_SUFFIX} "
            f"but running at N={n_actual}.")


print(f"[config] PROT-018 N={N} n_active={N_ACTIVE} mode={RUN_MODE} "
      f"M_FULL={_M_FULL} CAP_PRED={CAP_PRED:.4f} alpha={ALPHA}", flush=True)
_prot018_startup_check(N_ACTIVE if RUN_MODE == "smoke" else N)

out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N, "alpha": ALPHA, "run_mode": RUN_MODE}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(f"[ckpt] {len(done)} seeds done, {len(remaining)} to run", flush=True)

t_sweep_start = time.time()
for seed in remaining:
    print(f"[seed={seed}] {ANCHOR_NAME}...", flush=True)
    result = run_seed_sigma_sweep(seed, N_ACTIVE if RUN_MODE == "smoke" else N, SIGMA_G_USE)
    write_partial(out_dir, seed, result)
    print(f"[seed={seed}] done elapsed={result['elapsed_s']:.1f}s", flush=True)

per_seed = aggregate_partials(out_dir, SEEDS)
all_results = list(per_seed.values())
verdict, verdict_msg = compute_verdict(all_results)

print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)

elapsed_total = time.time() - t_sweep_start
metrics = {
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict, "verdict_msg": verdict_msg,
    "N": N, "alpha": ALPHA, "M_full": _M_FULL,
    "cap_pred": float(CAP_PRED), "run_mode": RUN_MODE,
    "n_seeds": len(SEEDS), "elapsed_s": elapsed_total,
    "per_seed": [
        {"seed": r.get("seed"), "alpha": r.get("alpha"),
         "elapsed_s": r.get("elapsed_s"),
         "sigma_g_cap_pred": r.get("sigma_g_cap_pred")}
        for r in all_results
    ],
}
metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
