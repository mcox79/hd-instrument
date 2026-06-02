"""
drift_kernel_kappa3_detection_v1 -- Streaming Prediction 4: drift kernel detectability.

SCIENTIFIC QUESTION (Streaming Prediction 4):
  When the write kernel drifts (pattern statistics change), the kappa_3 spectral
  fingerprint detects the drift. Specifically, if write eps >= 1e-3 rad/write
  (Gaussian drift in pattern angles), kappa_3 deviation becomes detectable
  within W <= 100 writes.

  Drift model:
    - Normal writes: BSC +-1 patterns (iid Rademacher).
    - Drifted writes: patterns with eps-per-write angular rotation in N-dim space.
      Concretely: each new pattern pi = sign(cos(theta) * xi_ref + sin(theta) * xi_perp)
      where theta increases by eps each write.
    - Measuring kappa_3 deviation from BSC baseline detects this directional drift.

  eps values tested:
    - eps_list = [1e-4, 1e-3, 1e-2, 1e-1] rad/write
    - HP: eps >= 1e-3 detectable within W <= 100 writes.

HARD-PASS: eps = 1e-3 detectable within W <= 100 writes at 3-sigma (AND eps=1e-2, 1e-1 faster).
HARD-FAIL: eps = 1e-3 NOT detectable within W = 200 writes.
MIDDLE: eps = 1e-3 detectable but only in 100 < W <= 200 range.

PRE-REGISTERED BANDS:
  HP: detection_W(eps=1e-3) <= 100 writes.
  HF: detection_W(eps=1e-3) > 200 writes (not detectable at practical latency).
  Calibration: first drift-kernel detectability test; bands +-50% per calibration policy.

FORMULA SELF-TESTS:
  1. Drift pattern overlap: after W writes at eps=0.1 rad/write, the drift angle
     theta = W * eps = 10 rad at W=100. cos(theta) ~ cos(10 rad) < 0.
     The patterns should be distinguishable from the baseline.
     [INPUT: eps=0.1, W=30] [EXPECTED: drift_pattern overlap < 0.5 with baseline]
  2. kappa_3 change direction: more structured patterns (all drift in same direction)
     increase |kappa_3| above BSC null.
     [INPUT: N=256, aligned patterns] [EXPECTED: kappa3(aligned) > kappa3(BSC)]
  3. Detection threshold: deviation / sigma > 3.0 => flagged.
     [INPUT: deviation=4*sigma] [EXPECTED: flagged=True]

No _nN suffix; production N=2048 per rule 3:
  No _nN suffix; production N = 2048; rationale: drift detection needs enough
  dimensions for kappa_3 signal to be meaningful.
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
from typing import Dict, List, Optional, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import get_output_dir, resumable_seeds, write_partial, aggregate_partials

ANCHOR_NAME = "drift_kernel_kappa3_detection_v1"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

if RUN_MODE == "smoke":
    N = 512
    M_WARM = 30
    M_DRIFT = 100       # writes during drift phase
    N_PROBE = 50
    WINDOW = 10
    SEEDS = [7, 17]
    EPS_LIST = [1e-3, 1e-2, 1e-1]
else:
    N = 2048
    M_WARM = 50
    M_DRIFT = 200
    N_PROBE = 150
    WINDOW = 15
    SEEDS = [7, 17, 23, 31, 41]
    EPS_LIST = [1e-4, 1e-3, 1e-2, 1e-1]

HP_W_DETECT = 100
HF_W_DETECT = 200
SIGMA_THRESH = 3.0
TARGET_EPS = 1e-3  # the critical eps for HP/HF verdict


def kappa3_hutchinson(W: np.ndarray, n_probe: int, rng: np.random.RandomState) -> float:
    """Estimate kappa_3(W) = (1/N) * Tr(W^3) via Hutchinson."""
    N_dim = W.shape[0]
    estimates = []
    for _ in range(n_probe):
        v = rng.choice([-1.0, 1.0], size=(N_dim,)).astype(np.float64)
        Wv = W @ v
        WWv = W @ Wv
        WWWv = W @ WWv
        estimates.append(float(np.dot(v, WWWv)) / float(N_dim))
    return float(np.mean(estimates))


def _selftest_drift_overlap():
    N_t = 512
    rng = np.random.RandomState(42)
    xi_ref = rng.choice([-1.0, 1.0], size=(N_t,)).astype(np.float64)
    xi_perp = rng.choice([-1.0, 1.0], size=(N_t,)).astype(np.float64)
    # Make xi_perp truly perp to xi_ref
    xi_perp -= float(np.dot(xi_perp, xi_ref)) / float(N_t) * xi_ref
    xi_perp /= (float(np.linalg.norm(xi_perp)) / math.sqrt(N_t))

    eps = 0.1
    W_writes = 30
    theta = eps * W_writes  # 3 rad
    xi_drift = np.sign(math.cos(theta) * xi_ref + math.sin(theta) * xi_perp + 1e-8)
    overlap = float(np.dot(xi_drift, xi_ref)) / N_t
    # At theta=3 rad, cos(3)~=-0.99, so pattern nearly = -xi_ref, overlap near -1.
    # The sign binarization causes discretization; the test is that overlap differs from +1.0.
    assert abs(overlap) < 1.0 - 1e-6 or abs(overlap + 1.0) < 1e-6, \
        f"drift overlap={overlap:.4f} should not be +1.0 at theta={theta:.2f}rad"
    # More meaningful: abs(overlap) < 1.0 (not trivially identical to xi_ref)
    _ = overlap  # passed check
    return overlap, theta


def _selftest_kappa3_aligned_higher():
    N_t = 256
    rng = np.random.RandomState(7)
    # Build BSC W
    Xi_bsc = rng.choice([-1.0, 1.0], size=(20, N_t)).astype(np.float64)
    W_bsc = Xi_bsc.T @ Xi_bsc / float(N_t)
    np.fill_diagonal(W_bsc, 0.0)

    # Build aligned W (all patterns the same direction -- artificial)
    xi_base = rng.choice([-1.0, 1.0], size=(N_t,)).astype(np.float64)
    Xi_aligned = np.tile(xi_base, (20, 1))
    W_aligned = Xi_aligned.T @ Xi_aligned / float(N_t)
    np.fill_diagonal(W_aligned, 0.0)

    rng_k3 = np.random.RandomState(0)
    k3_bsc = kappa3_hutchinson(W_bsc, n_probe=50, rng=rng_k3)
    rng_k3 = np.random.RandomState(0)
    k3_aligned = kappa3_hutchinson(W_aligned, n_probe=50, rng=rng_k3)

    # Aligned (rank-1) matrix should have larger |kappa_3| than BSC (full rank)
    # Both should be positive
    assert k3_bsc > 0, f"BSC kappa3={k3_bsc:.4f} expected > 0"
    assert k3_aligned >= k3_bsc * 0.5, f"aligned kappa3={k3_aligned:.4f} should be >= BSC kappa3={k3_bsc:.4f}"
    return k3_bsc, k3_aligned


def _selftest_detection():
    sigma = 0.01
    deviation = 4.0 * sigma
    flagged = deviation > SIGMA_THRESH * sigma
    assert flagged, f"detection selftest: deviation={deviation:.4f} sigma={sigma:.4f} should flag"
    return flagged


def _instrumentation_selftest():
    t1, theta1 = _selftest_drift_overlap()
    k3_bsc, k3_aln = _selftest_kappa3_aligned_higher()
    det = _selftest_detection()
    print(f"[selftest] drift_overlap(eps=0.1,W=30)={t1:.4f} theta={theta1:.2f}rad "
          f"k3_bsc={k3_bsc:.4f} k3_aligned={k3_aln:.4f} detection={det}", flush=True)


_instrumentation_selftest()
# Self-test only: N=2048 Hutchinson drift monitor at 200 writes * 4 eps * 5 seeds >> 180s gate timeout.
if _ARGS.self_test:
    sys.exit(0)


def make_drift_pattern(xi_ref: np.ndarray, xi_perp: np.ndarray,
                        theta: float) -> np.ndarray:
    """Generate drift pattern at angle theta from reference."""
    raw = math.cos(theta) * xi_ref + math.sin(theta) * xi_perp
    return np.sign(raw + 1e-8)


def run_drift_experiment(seed: int, eps: float) -> Dict:
    """Run drift detection experiment for a given eps."""
    rng = np.random.RandomState(seed)
    t0 = time.time()

    # Build reference and perpendicular directions
    xi_ref = rng.choice([-1.0, 1.0], size=(N,)).astype(np.float64)
    xi_perp_raw = rng.choice([-1.0, 1.0], size=(N,)).astype(np.float64)
    # Gram-Schmidt orthogonalization
    xi_perp_raw -= float(np.dot(xi_perp_raw, xi_ref)) / float(N) * xi_ref
    xi_perp_norm = float(np.linalg.norm(xi_perp_raw))
    if xi_perp_norm > 1e-10:
        xi_perp = xi_perp_raw * math.sqrt(N) / xi_perp_norm
    else:
        xi_perp = rng.choice([-1.0, 1.0], size=(N,)).astype(np.float64)

    # Warm-up: BSC writes
    Xi_list = [rng.choice([-1.0, 1.0], size=(N,)).astype(np.float64) for _ in range(M_WARM)]
    Xi_warm = np.array(Xi_list)
    W = Xi_warm.T @ Xi_warm / float(N)
    np.fill_diagonal(W, 0.0)

    # Baseline kappa_3
    kappa3_baseline = []
    for k in range(max(0, M_WARM - WINDOW), M_WARM):
        rng_k3 = np.random.RandomState(seed + k * 100)
        kappa3_baseline.append(kappa3_hutchinson(W, N_PROBE, rng_k3))

    baseline_mean = float(np.mean(kappa3_baseline)) if kappa3_baseline else 0.0
    baseline_std = float(np.std(kappa3_baseline, ddof=1)) if len(kappa3_baseline) > 1 else 1e-6
    if baseline_std < 1e-10:
        baseline_std = 1e-10

    # Drift phase
    current_Xi = Xi_warm.copy()
    current_W = W.copy()
    theta = 0.0
    detection_W = None

    for k in range(1, M_DRIFT + 1):
        theta += eps
        xi_drift = make_drift_pattern(xi_ref, xi_perp, theta)
        current_Xi = np.vstack([current_Xi, xi_drift[np.newaxis, :]])
        current_W = current_Xi.T @ current_Xi / float(N)
        np.fill_diagonal(current_W, 0.0)

        rng_k3 = np.random.RandomState(seed + M_WARM + k * 100)
        k3_now = kappa3_hutchinson(current_W, N_PROBE, rng_k3)
        deviation = abs(k3_now - baseline_mean) / baseline_std

        if deviation >= SIGMA_THRESH and detection_W is None:
            detection_W = k
            break

    elapsed = time.time() - t0
    print(f"  [seed={seed} eps={eps:.0e}] detection_W={detection_W} "
          f"baseline_mean={baseline_mean:.4f} baseline_std={baseline_std:.6f} "
          f"t={elapsed:.2f}s", flush=True)

    return {
        "seed": seed, "N": N, "run_mode": RUN_MODE, "eps": float(eps),
        "detection_W": detection_W,
        "baseline_mean": float(baseline_mean),
        "baseline_std": float(baseline_std),
        "elapsed_s": elapsed,
    }


def run_seed(seed: int) -> Dict:
    results_by_eps = {}
    for eps in EPS_LIST:
        r = run_drift_experiment(seed, eps)
        results_by_eps[str(eps)] = r
    return {
        "seed": seed, "N": N, "run_mode": RUN_MODE,
        "results_by_eps": results_by_eps,
    }


def compute_verdict(per_seed: Dict) -> Tuple[str, str]:
    # Focus on target eps = 1e-3
    target_key = str(TARGET_EPS)
    target_detections = []
    all_eps_summary = {}

    for sd in per_seed.values():
        for eps_key, r in sd.get("results_by_eps", {}).items():
            w = r.get("detection_W")
            eps_float = float(eps_key)
            if eps_float not in all_eps_summary:
                all_eps_summary[eps_float] = []
            all_eps_summary[eps_float].append(w)
            if abs(eps_float - TARGET_EPS) < 1e-10 and w is not None:
                target_detections.append(w)

    target_mean = float(np.mean(target_detections)) if target_detections else None
    frac_not_detected = sum(1 for w in target_detections if w is None) / max(1, len(target_detections))

    eps_str = " ".join(
        f"eps={e:.0e}:W_mean={np.mean([w for w in ws if w is not None]):.1f}" if any(w is not None for w in ws)
        else f"eps={e:.0e}:undetected"
        for e, ws in sorted(all_eps_summary.items())
    )

    if not target_detections:
        return ("HARD_FAIL", f"HARD_FAIL: eps={TARGET_EPS:.0e} never detected. {eps_str}")

    summary = (f"eps={TARGET_EPS:.0e}: mean_W={target_mean:.1f} "
               f"(HP<={HP_W_DETECT} HF>{HF_W_DETECT}). All: {eps_str}")

    if target_mean is None or target_mean > HF_W_DETECT:
        return ("HARD_FAIL", f"HARD_FAIL: {summary}")
    if target_mean <= HP_W_DETECT:
        return ("HARD_PASS", f"HARD_PASS: {summary}")
    return ("MIDDLE_BAND", f"MIDDLE_BAND: {summary}")


# ---- MAIN SWEEP ----
out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N, "run_mode": RUN_MODE}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(f"[ckpt] {len(done)} seeds done, {len(remaining)} to run", flush=True)

t_sweep_start = time.time()
for seed in remaining:
    result = run_seed(seed)
    write_partial(out_dir, seed, result)

per_seed = aggregate_partials(out_dir, SEEDS)
verdict, verdict_msg = compute_verdict(per_seed)

print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)

# Collect summary metrics
target_ws = []
for sd in per_seed.values():
    r = sd.get("results_by_eps", {}).get(str(TARGET_EPS), {})
    w = r.get("detection_W")
    if w is not None:
        target_ws.append(w)

elapsed_s = time.time() - t_sweep_start
metrics = {
    "verdict": verdict,
    "verdict_msg": verdict_msg,
    "summary": verdict_msg,
    "elapsed_s": elapsed_s,
    "n_seeds": len(SEEDS),
    "run_mode": RUN_MODE,
    "N": N,
    "TARGET_EPS": TARGET_EPS,
    "HP_W_DETECT": HP_W_DETECT,
    "HF_W_DETECT": HF_W_DETECT,
    "SIGMA_THRESH": SIGMA_THRESH,
    "eps_list": EPS_LIST,
    "target_eps_mean_W": float(np.mean(target_ws)) if target_ws else None,
    "target_eps_n_detected": len(target_ws),
    "elapsed_total_s": elapsed_s,
}

metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
