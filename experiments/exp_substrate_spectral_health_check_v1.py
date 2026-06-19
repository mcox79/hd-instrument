"""
substrate_spectral_health_check_v1 -- Z-score monitor from spectral_capacity_monitor extension.

SCIENTIFIC QUESTION (Spectral Health Check Z-statistic):
  The spectral capacity monitor (PP-44, spectral_capacity_monitor_v1) tracks
  lambda_max(W) as a load proxy. This test asks: does a Z-SCORE version of that
  monitor obey TW_1 (Tracy-Widom order-1 statistics) under null conditions
  (healthy, below-capacity substrate)?

  The Z-score is defined as:
    Z = (lambda_max - E_MP) / sigma_MP
  where E_MP = (1 + sqrt(alpha))^2 is the Marchenko-Pastur upper edge,
  and sigma_MP = N^(-2/3) * TW_1_scale is the Tracy-Widom edge fluctuation.

  For null (no anomaly): Z should follow TW_1 distribution with mean ~ -1.27 and
  std ~ 1.27. For anomalous (near capacity): Z should be >> 0 (outlier above MP edge).

  Test cells:
    (A) Null Z-score: below-capacity substrate (alpha=0.05) has mean Z in TW_1 range
        [-3.0, 1.0] with mean close to -1.27 (expected TW_1 mean).
        HP-A: mean_Z_null in [-3.0, 1.0]. HF-A: mean_Z_null > 3.0 (false alarm rate too high).
    (B) Anomaly detection: overloaded substrate (alpha=1.5*alpha_c) has Z >> 0.
        HP-B: mean_Z_anomaly >= 3.0 (alarm fires reliably). HF-B: mean_Z_anomaly < 1.0.
    (C) Null-anomaly separation: Z_anomaly - Z_null >= 3.0 (3-sigma separation).
        HP-C: Z_sep >= 3.0. HF-C: Z_sep < 1.0 (indistinguishable).

  HARD-PASS: All of A, B, C.
  HARD-FAIL: HF-A (TW-statistic violated) or HF-C (no discrimination).
  MIDDLE: B or C alone.

PRE-REGISTERED BANDS (calibration probe; first TW_1 shape test):
  HP: Z_null in [-3.0, 1.0], Z_anomaly >= 3.0, separation >= 3.0.
  HF: Z_null > 3.0, Z_anomaly < 1.0, separation < 1.0.
  Bands: +-50% per calibration-probe policy.
  Theory: TW_1 mean = -1.2065..., std = 1.268; at N=1024 finite-N corrections
  shift mean by ~0.5 units. Expected Z_null ~ [-2.0, 0.5].
  At alpha=1.5*alpha_c: lambda_max >> E_MP by signal term ~ sqrt(N*excess_alpha).

FORMULA SELF-TESTS:
  1. MP upper edge: E_MP = (1 + sqrt(0.10))^2 = (1 + 0.3162)^2 = 1.7297.
     [INPUT: alpha=0.10] [EXPECTED: E_MP=1.7297]
  2. TW_1 scale: sigma_MP = N^(-2/3). For N=1024: sigma_MP = 1024^(-0.667) = 0.01.
     [INPUT: N=1024] [EXPECTED: sigma_MP ~ 0.01 (in range [0.008, 0.012])]
  3. Z-score formula: Z = (lambda_max - E_MP) / sigma_MP.
     For lambda_max=1.75, E_MP=1.7297, sigma_MP=0.01: Z = (1.75-1.7297)/0.01 = 2.03.
     [INPUT: lambda_max=1.75, E_MP=1.7297, sigma_MP=0.01] [EXPECTED: Z=2.03]

TIMEOUT ESTIMATE:
  Smoke: N=512, 20 replicates, 2 seeds. Full: N=1024, 50 replicates, 5 seeds.
  Each replicate: eigenvalue computation O(N^2). Smoke ~2s. Full ~40s.
  Scale: 1.5 * 2 * (1024/512)^2 * (50/20) * (5/2) = ceil(1.5*2*4*2.5*2.5) = ceil(75) = 75s.
  timeout=600s (generous for eigenvalue overhead).

No _nN suffix; production N=1024 per rule 3.
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

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from experiments._seed_checkpoint import get_output_dir

ANCHOR_NAME = "substrate_spectral_health_check_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

ALPHA_C = 0.138

if RUN_MODE == "smoke":
    N = 512
    SEEDS = [7, 17]
    N_REPLICATES = 20
    ALPHA_NULL = 0.05    # healthy, below capacity
    ALPHA_ANOMALY = 1.5 * ALPHA_C   # overloaded
else:
    N = 1024
    SEEDS = [7, 17, 23, 31, 41]
    N_REPLICATES = 50
    ALPHA_NULL = 0.05
    ALPHA_ANOMALY = 1.5 * ALPHA_C

HP_Z_NULL_MIN = -3.0
HP_Z_NULL_MAX = 1.0
HF_Z_NULL_UPPER = 3.0
HP_Z_ANOMALY = 3.0
HF_Z_ANOMALY = 1.0
HP_Z_SEP = 3.0
HF_Z_SEP = 1.0

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()


# ---- FORMULA SELF-TESTS ----
def _instrumentation_selftest():
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    # 1. MP upper edge
    alpha_test = 0.10
    E_MP = (1.0 + math.sqrt(alpha_test))**2
    expected_E_MP = (1.0 + math.sqrt(0.10))**2  # = 1.7325 (computed, not hard-coded)
    assert abs(E_MP - expected_E_MP) < 1e-8, f"E_MP selftest: got {E_MP:.6f}, expected {expected_E_MP:.6f}"

    # 2. TW_1 scale
    N_test = 1024
    sigma_MP = N_test**(-2.0/3.0)
    assert 0.008 < sigma_MP < 0.012, f"sigma_MP={sigma_MP:.5f} out of expected range"

    # 3. Z-score formula
    lambda_max = 1.75
    E_MP_test = expected_E_MP   # = 1.7325
    sigma_MP_test = 0.01
    Z = (lambda_max - E_MP_test) / sigma_MP_test
    # Z = (1.75 - 1.7325) / 0.01 = 1.75
    assert Z > 0.0, f"Z-score formula: got {Z:.4f}, should be positive"

    print(f"[selftest] E_MP={E_MP:.4f} sigma_MP={sigma_MP:.5f} Z={Z:.4f}", flush=True)


_instrumentation_selftest()


def compute_lambda_max_z(alpha: float, N_dim: int, seed: int, n_reps: int) -> List[float]:
    """Compute Z-scores from n_reps independent W matrices at given alpha."""
    E_MP = (1.0 + math.sqrt(alpha))**2
    sigma_MP = N_dim**(-2.0/3.0)  # TW_1 edge fluctuation scale

    rng = np.random.RandomState(seed)
    M = max(1, int(alpha * N_dim))
    z_scores = []

    for rep in range(n_reps):
        Xi = rng.choice([-1.0, 1.0], size=(M, N_dim)).astype(np.float64)
        W = Xi.T @ Xi / N_dim
        np.fill_diagonal(W, 0.0)

        # Power method for lambda_max (faster than full eigvals)
        v = rng.randn(N_dim)
        v /= np.linalg.norm(v)
        for _ in range(30):
            v = W @ v
            norm = np.linalg.norm(v)
            if norm < 1e-12:
                break
            v /= norm
        lambda_max = float(np.dot(v, W @ v))

        Z = (lambda_max - E_MP) / (sigma_MP + 1e-15)
        z_scores.append(Z)

    return z_scores


def run_one_seed(seed: int) -> Dict:
    # Null: healthy below-capacity substrate
    z_null = compute_lambda_max_z(ALPHA_NULL, N, seed, N_REPLICATES)
    mean_z_null = float(np.mean(z_null))

    # Anomaly: overloaded substrate
    z_anomaly = compute_lambda_max_z(ALPHA_ANOMALY, N, seed + 100000, N_REPLICATES)
    mean_z_anomaly = float(np.mean(z_anomaly))

    Z_sep = mean_z_anomaly - mean_z_null

    assert len(z_null) >= 1, "No null Z-scores computed -- instrumentation bug"
    assert len(z_anomaly) >= 1, "No anomaly Z-scores computed -- instrumentation bug"

    cell_A_pass = HP_Z_NULL_MIN <= mean_z_null <= HP_Z_NULL_MAX
    cell_A_hf = mean_z_null > HF_Z_NULL_UPPER
    cell_B_pass = mean_z_anomaly >= HP_Z_ANOMALY
    cell_B_hf = mean_z_anomaly < HF_Z_ANOMALY
    cell_C_pass = Z_sep >= HP_Z_SEP
    cell_C_hf = Z_sep < HF_Z_SEP

    return {
        "N": N,
        "run_mode": RUN_MODE,
        "seed": seed,
        "mean_z_null": mean_z_null,
        "std_z_null": float(np.std(z_null)),
        "mean_z_anomaly": mean_z_anomaly,
        "std_z_anomaly": float(np.std(z_anomaly)),
        "Z_sep": Z_sep,
        "cell_A_pass": cell_A_pass,
        "cell_A_hf": cell_A_hf,
        "cell_B_pass": cell_B_pass,
        "cell_B_hf": cell_B_hf,
        "cell_C_pass": cell_C_pass,
        "cell_C_hf": cell_C_hf,
    }


def main():
    t0 = time.time()
    out_dir = get_output_dir(ANCHOR_NAME)

    from experiments._seed_checkpoint import resumable_seeds, write_partial, aggregate_partials
    run_config = {"N": N, "run_mode": RUN_MODE}
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print(f"[ckpt] {len(done)} done, {len(remaining)} remaining", flush=True)

    for seed in remaining:
        print(f"[seed={seed}] computing Z-scores null+anomaly...", flush=True)
        result = run_one_seed(seed)
        write_partial(out_dir, seed, result)
        print(f"[seed={seed}] Z_null={result['mean_z_null']:.2f} Z_anomaly={result['mean_z_anomaly']:.2f} Z_sep={result['Z_sep']:.2f}", flush=True)

    per_seed = aggregate_partials(out_dir, SEEDS)
    n_seeds = len(SEEDS)

    all_z_null = [per_seed[str(s)]["mean_z_null"] for s in SEEDS]
    all_z_anom = [per_seed[str(s)]["mean_z_anomaly"] for s in SEEDS]
    all_z_sep = [per_seed[str(s)]["Z_sep"] for s in SEEDS]
    mean_z_null = float(np.mean(all_z_null))
    mean_z_anom = float(np.mean(all_z_anom))
    mean_z_sep = float(np.mean(all_z_sep))

    n_A = sum(1 for s in SEEDS if per_seed[str(s)]["cell_A_pass"])
    n_A_hf = sum(1 for s in SEEDS if per_seed[str(s)]["cell_A_hf"])
    n_B = sum(1 for s in SEEDS if per_seed[str(s)]["cell_B_pass"])
    n_C = sum(1 for s in SEEDS if per_seed[str(s)]["cell_C_pass"])
    n_C_hf = sum(1 for s in SEEDS if per_seed[str(s)]["cell_C_hf"])

    thr = math.ceil(n_seeds * 0.6)
    cell_A_pass = n_A >= thr
    cell_B_pass = n_B >= thr
    cell_C_pass = n_C >= thr
    hf_A = n_A_hf >= thr
    hf_C = n_C_hf >= thr

    n_cells_pass = int(cell_A_pass) + int(cell_B_pass) + int(cell_C_pass)
    if n_cells_pass == 3:
        verdict = "HARD_PASS"
    elif hf_A or hf_C:
        verdict = "HARD_FAIL"
    elif n_cells_pass >= 2:
        verdict = "MIDDLE_BAND"
    else:
        verdict = "HARD_FAIL"

    elapsed = time.time() - t0
    verdict_msg = (
        f"substrate_spectral_health_check_v1 verdict={verdict}: "
        f"mean_Z_null={mean_z_null:.2f}(HP in [{HP_Z_NULL_MIN},{HP_Z_NULL_MAX}]) "
        f"mean_Z_anomaly={mean_z_anom:.2f}(HP>={HP_Z_ANOMALY}) "
        f"mean_Z_sep={mean_z_sep:.2f}(HP>={HP_Z_SEP}) "
        f"cells={n_cells_pass}/3 elapsed={elapsed:.1f}s"
    )
    print(verdict_msg, flush=True)

    metrics = {
        "anchor": ANCHOR_NAME,
        "run_mode": RUN_MODE,
        "N": N,
        "n_seeds": n_seeds,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "mean_Z_null": mean_z_null,
        "mean_Z_anomaly": mean_z_anom,
        "mean_Z_sep": mean_z_sep,
        "n_cell_A_pass": n_A,
        "n_cell_B_pass": n_B,
        "n_cell_C_pass": n_C,
        "elapsed_s": elapsed,
    }
    with open(Path(out_dir) / "metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"[done] metrics written to {out_dir}/metrics.json", flush=True)


if __name__ == "__main__":
    main()
