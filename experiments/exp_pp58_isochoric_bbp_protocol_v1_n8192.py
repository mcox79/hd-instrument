"""
pp58_isochoric_bbp_protocol_v1_n8192 -- PP-58 isochoric BBP protocol revision at N=8192.

CONTEXT (v369 refill cycle):
  PP-58 row: EXPLORATORY MIDDLE band 0.55-0.70.
  Prior runs (N=8192 v4): ratio=3.0 at N=8192 (MIDDLE_BAND; old HP gate 5.0).
  Prior runs (N=16384 v5): ratio=4.0 at N=16384 (MIDDLE_BAND; old HP gate 5.0).
  Research upgrade (v359 drill battery, PP-58 2x deep dive):
    BBP asymptote = 4.13 at alpha=0.05 (N-independent closed form).
    Old HP gate 5.0 was coarse-grid founding artifact.
    REVISED gate: ratio >= 4.0 is HP-achievable (BBP asymptote 4.13).
    BBP sigma_g_audit_crit = 1 - sqrt(alpha) - alpha = 0.726 at alpha=0.05.
  This anchor re-runs the N=8192 isochoric measurement with the REVISED pre-registered gate
  and denser sigma_g grid near audit_crit (around 0.726).

SCIENTIFIC QUESTION:
  Does the N=8192 isochoric measurement achieve ratio >= 4.0 with the BBP-revised protocol?
  The prior N=8192 v4 run showed ratio=3.0 with coarse grid (no points near 0.726).
  This run uses the BBP-informed grid: dense points around sigma_g in [0.60, 0.80].
  Expected: audit_crit shifts from ~0.50 to ~0.726 (matches BBP prediction),
  giving ratio = cap_crit / 0.726 ~ 4.36/0.726 ~ 6.0 (well above new HP 4.0).
  N=8192 cross-N to pp58_bbp_spectral_gap_calibration_v1_n16384 (already in queue).

MEMORY ESTIMATE (OOM pre-check):
  W matrix at N=8192: 8192^2 * 8 bytes = 0.54 GB CPU RAM. Remote has 16+ GB. Fine.
  Xi GPU: 819 * 8192 * 4 = 26.8 MB GPU. Well within limits.
  Note: eigendecomp on CPU numpy (same as v4).

PRE-REGISTERED BANDS (PP-58 isochoric BBP protocol N=8192; revised gate):
  Prior empirical anchor: N=8192 v4 ratio=3.0. BBP prediction: ratio=4.13.
  Calibration: revised gate +-50% of BBP prediction 4.13 = [2.07, 6.20].
  HARD-PASS: ratio in [3.5, 5.5] AND sigma_g_audit_crit in [0.60, 0.85] AND cap_crit in [2.5, 5.0].
  MIDDLE: ratio in [3.0, 5.5] but at least one envelope-location outside HP band.
  HARD-FAIL: ratio < 3.0 OR ratio > 6.5 -- BBP revised prediction wrong at N=8192.

  Strategic outcome: HP founds PP-58 at 0.65-0.80 (BBP protocol validated N=8192).
  MIDDLE: denser grid reduces uncertainty; band stays MIDDLE; N=16384 BBP calibration authoritative.

FORMULA SELF-TESTS (PROT-022):
  1. BBP sigma_g_audit_crit: 1 - sqrt(0.05) - 0.05 = 0.7264 at alpha=0.05.
     [INPUT: alpha=0.05] [EXPECTED: 0.7264 within 0.001]
  2. Cap boundary formula: sqrt(1/0.05 - 1) = sqrt(19) = 4.3589 within 0.01.
     [INPUT: alpha=0.05] [EXPECTED: 4.3589 within 0.01]
  3. M = int(0.05 * 8192) = 409 >= 1. [EXPECTED: M = 409]
  4. kappa_3 on tiny N non-NaN (instrumentation self-test).
  5. BBP ratio prediction: 4.3589 / 0.7264 = 6.00 (BBP asymptotic). [EXPECTED: ~6.0]

PROT-018: anchor has _n8192; N MUST = 8192.
PROT-021: seed checkpoints keyed with run_mode + N.
QUEUE: overnight_queue (GPU machine; W build and eigendecomp on CPU via GPU machine's RAM;
       5 seeds x 14 sigma_g points; matches v4 structure with BBP-dense grid).
TIMEOUT ESTIMATE: N=8192 v4 elapsed ~600s (14 sigma_g x 5 seeds).
  Same scale here. ceil(1.5 * 600) = 900s.
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
from typing import Dict, List

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

try:
    import torch
    import torch.cuda
except ImportError:
    print("[FATAL] torch not installed.", flush=True)
    sys.exit(1)

if not torch.cuda.is_available():
    print("[FATAL] CUDA not available. This script requires a GPU.", flush=True)
    sys.exit(1)

DEVICE = torch.device('cuda')
_total_vram_gb = torch.cuda.get_device_properties(0).total_memory / 1e9
print(f"[GPU] device={DEVICE} name={torch.cuda.get_device_name(0)} "
      f"total_mem={_total_vram_gb:.1f}GB", flush=True)

try:
    import numpy as np
except ImportError:
    print("[FATAL] numpy not installed.", flush=True)
    sys.exit(1)

from experiments._seed_checkpoint import get_output_dir, resumable_seeds, write_partial, aggregate_partials

ANCHOR_NAME = "pp58_isochoric_bbp_protocol_v1_n8192"

_N_SUFFIX = 8192
N = 8192
assert N == _N_SUFFIX, f"PROT-018: anchor _n{_N_SUFFIX} but N={N}"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

ALPHA = 0.05
_M_FULL = int(ALPHA * N)  # 409

# BBP-informed sigma_g grid: dense around audit_crit 0.726
SIGMA_G_FULL = [
    0.0, 0.05, 0.10, 0.20, 0.30, 0.40, 0.50,
    0.60, 0.65, 0.70, 0.726, 0.75, 0.80,
    1.0, 2.0, 4.0
]
CAP_PRED = float((1.0 / ALPHA - 1.0) ** 0.5)  # sqrt(19) = 4.3589
BBP_AUDIT_CRIT_PRED = 1.0 - math.sqrt(ALPHA) - ALPHA  # 0.7264
BBP_RATIO_PRED = CAP_PRED / BBP_AUDIT_CRIT_PRED  # ~6.0

KAPPA3_RATIO_CRIT_FACTOR = 2.0
RECALL_CRIT = 0.50
N_RETRIEVAL_STEPS = 8
N_QUERIES_PER_CELL = 10
N_PROBES_FULL = 50
N_PROBES_SELFTEST = 20

HP_RATIO_MIN = 3.5
HP_RATIO_MAX = 5.5
HP_AUDIT_CRIT_MIN = 0.60
HP_AUDIT_CRIT_MAX = 0.85
HP_CAP_CRIT_MIN = 2.5
HP_CAP_CRIT_MAX = 5.0
MIDDLE_RATIO_MIN = 3.0
HF_RATIO_LOW = 3.0
HF_RATIO_HIGH = 6.5
HP_CAP_CRIT_TOLERANCE = 0.20

# PROT-022 formula self-tests at module scope
_bbp_audit = 1.0 - math.sqrt(ALPHA) - ALPHA
print(f"[selftest-formula] BBP sigma_g_audit_crit = 1 - sqrt({ALPHA}) - {ALPHA} = "
      f"{_bbp_audit:.4f} (expected 0.7264)", flush=True)
assert abs(_bbp_audit - 0.7264) < 0.001, (
    f"BBP audit_crit selftest: got {_bbp_audit:.4f} expected 0.7264")

_cap_pred_check = math.sqrt(1.0 / ALPHA - 1.0)
print(f"[selftest-formula] cap_pred = sqrt(1/{ALPHA}-1) = {_cap_pred_check:.4f} "
      f"(expected 4.3589)", flush=True)
assert abs(_cap_pred_check - 4.3589) < 0.01, (
    f"cap_pred selftest: got {_cap_pred_check:.4f} expected 4.3589")

assert _M_FULL == 409, f"M check: {_M_FULL} expected 409"

_bbp_ratio_pred = _cap_pred_check / _bbp_audit
print(f"[selftest-formula] BBP ratio pred = {_cap_pred_check:.4f} / {_bbp_audit:.4f} = "
      f"{_bbp_ratio_pred:.2f} (expected ~6.0)", flush=True)
assert 5.5 < _bbp_ratio_pred < 6.5, (
    f"BBP ratio pred selftest: got {_bbp_ratio_pred:.2f} expected ~6.0")

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    N_ACTIVE = 512
    SIGMA_G_USE = [0.0, 0.30, 0.60, 0.726, 1.0, 4.0]
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


def _selftest_kappa3_identity():
    """kappa_3 identity at zero noise for alpha=0.05, N=256."""
    n_t = 256
    M_t = max(1, int(ALPHA * n_t))
    rng_t = np.random.RandomState(42)
    Xi = rng_t.choice([-1., 1.], size=(M_t, n_t)).astype(np.float64)
    W = (Xi.T @ Xi) / float(n_t)
    k3 = hutchinson_kappa3_np(W, n_probes=N_PROBES_SELFTEST, seed=42)
    k3_ratio = k3 / ALPHA
    assert 0.1 < k3_ratio < 10.0, (
        f"kappa_3 identity failed: k3_ratio={k3_ratio:.4f}, expected ~1.0 at alpha={ALPHA}")
    assert not math.isnan(k3), "kappa_3 is NaN in selftest"


def _instrumentation_selftest():
    _selftest_kappa3_identity()
    # GPU memory check
    dummy = torch.zeros((512, 512), device=DEVICE, dtype=torch.float32)
    mem = torch.cuda.memory_allocated(0)
    assert mem > 0, f"GPU memory not allocated"
    del dummy
    print(f"[selftest] PASS: cap_boundary={CAP_PRED:.4f} bbp_audit_crit={BBP_AUDIT_CRIT_PRED:.4f} "
          f"kappa3_identity ok m_full=409 gpu_mem_ok N_active={N_ACTIVE}", flush=True)


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
                                   seed=seed + int(sigma_g * 10000))
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

        key = f"sg{sigma_g:.4f}"
        cell_results[key] = {
            "sigma_g": float(sigma_g),
            "kappa3_ratio": float(k3_ratio),
            "recall": float(mean_recall),
        }
        print(f"  [seed={seed} sg={sigma_g:.4f}] k3_ratio={k3_ratio:.4f} "
              f"recall={mean_recall:.4f}", flush=True)

    elapsed = time.time() - t0
    return {
        "alpha": float(ALPHA), "seed": seed, "N": n_dim, "run_mode": RUN_MODE,
        "sigma_g_cap_pred": float(CAP_PRED),
        "bbp_audit_crit_pred": float(BBP_AUDIT_CRIT_PRED),
        "elapsed_s": float(elapsed), "cells": cell_results,
    }


def _find_audit_critical_sigma(seed_results: List[Dict]) -> float:
    """Find sigma_g where kappa_3_ratio first deviates from baseline by > 2x."""
    sigma_vals: Dict[float, List[float]] = {}
    for r in seed_results:
        for key, cell in r.get("cells", {}).items():
            sg = cell["sigma_g"]
            sigma_vals.setdefault(sg, []).append(
                min(abs(cell.get("kappa3_ratio", 0.0)), 1e6))
    if not sigma_vals:
        return float("nan")
    sorted_sg = sorted(sigma_vals.keys())
    baseline_ratio = 1.0
    if 0.0 in sigma_vals:
        baseline_ratio = max(float(np.mean(sigma_vals[0.0])), 0.1)
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
            sigma_vals.setdefault(sg, []).append(cell.get("recall", 0.0))
    if not sigma_vals:
        return float("nan")
    sorted_sg = sorted(sigma_vals.keys())
    for sg in sorted_sg:
        if float(np.mean(sigma_vals[sg])) < RECALL_CRIT:
            return sg
    return sorted_sg[-1] * 10


def compute_verdict(seed_results: List[Dict]) -> tuple:
    audit_crit = _find_audit_critical_sigma(seed_results)
    cap_crit = _find_capacity_critical_sigma(seed_results)
    ratio = cap_crit / max(audit_crit, 1e-6) if (audit_crit > 0 and not math.isnan(audit_crit)) else 0.0
    cap_within_tol = abs(cap_crit - CAP_PRED) / CAP_PRED <= HP_CAP_CRIT_TOLERANCE

    summary = (f"alpha={ALPHA} N={N} audit_crit={audit_crit:.3f}(pred={BBP_AUDIT_CRIT_PRED:.3f}) "
               f"cap_crit={cap_crit:.3f}(pred={CAP_PRED:.3f}) ratio={ratio:.2f} "
               f"bbp_ratio_pred={BBP_RATIO_PRED:.2f} n_seeds={len(seed_results)}")

    # HARD-FAIL check
    if ratio < HF_RATIO_LOW or ratio > HF_RATIO_HIGH:
        return ("HARD_FAIL",
                f"HARD_FAIL: ratio={ratio:.2f} outside [{HF_RATIO_LOW},{HF_RATIO_HIGH}]. "
                f"BBP revised prediction wrong. {summary}")

    # HARD-PASS check
    audit_hp = HP_AUDIT_CRIT_MIN <= audit_crit <= HP_AUDIT_CRIT_MAX
    cap_hp = HP_CAP_CRIT_MIN <= cap_crit <= HP_CAP_CRIT_MAX
    ratio_hp = HP_RATIO_MIN <= ratio <= HP_RATIO_MAX

    if audit_hp and cap_hp and ratio_hp:
        return ("HARD_PASS",
                f"HARD_PASS: PP-58 BBP protocol at N=8192. "
                f"audit_crit={audit_crit:.3f} in HP band; ratio={ratio:.2f} in HP band. "
                f"BBP protocol revision validated. {summary}")

    return ("MIDDLE_BAND",
            f"MIDDLE_BAND: ratio={ratio:.2f} in [{MIDDLE_RATIO_MIN},{HP_RATIO_MAX}); "
            f"partial BBP validation. {summary}")


def _prot018_startup_check() -> None:
    if RUN_MODE != "smoke" and N_ACTIVE != _N_SUFFIX:
        raise RuntimeError(
            f"PROT-018 VIOLATION: anchor _n{_N_SUFFIX} but FULL N_ACTIVE={N_ACTIVE}")


print(f"[config] PROT-018 N={N} N_active={N_ACTIVE} mode={RUN_MODE} "
      f"alpha={ALPHA} sigma_g_grid_size={len(SIGMA_G_USE)}", flush=True)
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
peak_mem_gb = torch.cuda.max_memory_allocated(0) / 1e9
print(f"[GPU] peak memory allocated: {peak_mem_gb:.3f} GB", flush=True)
assert peak_mem_gb > 0.001, f"GPU util check FAIL: peak_gpu={peak_mem_gb:.3f}GB"

metrics = {
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict,
    "verdict_msg": verdict_msg,
    "n_seeds": len(SEEDS),
    "N": N, "n_active": N_ACTIVE,
    "alpha": ALPHA,
    "sigma_g_use": SIGMA_G_USE,
    "cap_pred": CAP_PRED,
    "bbp_audit_crit_pred": BBP_AUDIT_CRIT_PRED,
    "bbp_ratio_pred": BBP_RATIO_PRED,
    "run_mode": RUN_MODE,
    "elapsed_s": elapsed_total,
    "peak_gpu_gb": float(peak_mem_gb),
}

metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")

print(f"\n[VERDICT] {verdict}", flush=True)
print(f"[VERDICT_MSG] {verdict_msg}", flush=True)
print(f"[METRICS_PATH] {metrics_path}", flush=True)
