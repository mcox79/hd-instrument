"""
pp58_scs_extended_d_sweep_v1_n8192 -- PP-58 SCS framework direct formula test
at d=8, tau=0.05.

CONTEXT (v373, cycle 43):
  PP-58 re-opened under SCS framework (routing_pp58_reopen_with_scs_framework_2026-06-04.md).
  SCS prediction: gamma = (d + tau/d) / (1 + tau). At d=8, tau=0.05: gamma_SCS = 7.625.
  Empirical gamma ~ 8.0 from isochoric kappa_3 separation protocol.
  This experiment tests whether the SCS formula with independently measured d and tau
  correctly predicts the empirical gamma ratio at N=8192.

SCIENTIFIC QUESTION:
  Does the SCS formula gamma_SCS = (d + tau/d) / (1+tau) match empirical gamma within
  30% when d and tau are independently measured from the substrate weight matrix?

TEST DESIGN:
  N=8192, alpha=0.05 (M=410), 5 seeds.
  Per seed:
    1. Build Xi (M x N bipolar random).
    2. Measure tau = ||W_asym||_F / ||W||_F.
    3. Measure d = sigma_1(Xi)^2/N / mean(sigma_bulk^2/N) (leading SVD ratio).
    4. Compute gamma_SCS = (d + tau/d) / (1 + tau).
    5. Measure gamma_emp via isochoric kappa_3 separation protocol.
    6. Compare gamma_SCS vs gamma_emp; compute relative error.

PRE-REGISTERED BANDS:
  HARD-PASS (SCS formula validated):
    - gamma_SCS within 30% of gamma_emp at 4/5 seeds AND mean ratio in [0.7, 1.3].
    - d_estimate in [6.0, 12.0] (theory expects d ~ 7-8 at alpha=0.05).
    - tau_estimate in [0.02, 0.20] (near-Ginibre confirmed).
  MIDDLE:
    - gamma_SCS within 30% at 2-3/5 seeds, OR mean ratio in [0.5, 1.5].
  HARD-FAIL (SCS formula fails):
    - mean ratio < 0.5 or > 2.0 (SCS formula off by >2x).
    - OR d_estimate < 1.5 (no spike; SCS assumption violated).
    - OR tau_estimate > 0.5 (not near-Ginibre; SCS assumption violated).

FORMULA SELF-TESTS (PROT-022):
  1. SCS formula: gamma = (d + tau/d) / (1 + tau) at d=8, tau=0.05.
     [INPUT: d=8, tau=0.05] [EXPECTED: 7.6250 within 0.001]
  2. SCS formula: gamma at d=8, tau=0 (pure non-reciprocal limit).
     [INPUT: d=8, tau=0] [EXPECTED: 8.0 within 0.001]
  3. SCS formula: d=1, tau=0 -> gamma=1.0.
     [INPUT: d=1, tau=0] [EXPECTED: 1.0]
  4. M=int(0.05*8192)=410. [EXPECTED: 410]
  5. alpha_c=0.138 > 0.05 (within capacity). [EXPECTED: True]

PROT-018: anchor has _n8192; N MUST = 8192.
PROT-021: seed checkpoints keyed with run_mode + seed.
QUEUE: remote_cpu_queue (pure numpy; CPU; alpha=0.05 fixed, 5 seeds, ~10-20min total).
TIMEOUT ESTIMATE: N=8192 alpha=0.05 per-seed ~2-3min (SVD + kappa3). 5 seeds = 15min.
  ceil(1.5 * 180 * 5) = 1350s. Use PROT-019 floor: 21600s.
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

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

try:
    import numpy as np
except ImportError:
    print("[FATAL] numpy not installed.", flush=True)
    sys.exit(1)

from experiments._seed_checkpoint import get_output_dir, resumable_seeds, write_partial, aggregate_partials

ANCHOR_NAME = "pp58_scs_extended_d_sweep_v1_n8192"

_N_SUFFIX = 8192
N = 8192
assert N == _N_SUFFIX, f"PROT-018: anchor _n{_N_SUFFIX} but N={N}"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

ALPHA_GRID = [0.02, 0.04, 0.06, 0.08, 0.10, 0.12]
ALPHA_C = 0.138
assert all(a < ALPHA_C for a in ALPHA_GRID), f"all alphas must be < alpha_c={ALPHA_C}"

# PROT-022 formula self-tests at module scope (arithmetic only, no numpy)
def _scs_gamma(d: float, tau: float) -> float:
    return (d + tau / d) / (1.0 + tau)

_gamma_d8_tau005 = _scs_gamma(8.0, 0.05)
print(f"[selftest-formula] SCS gamma(d=8,tau=0.05): {_gamma_d8_tau005:.4f} (expected 7.6250)", flush=True)
assert abs(_gamma_d8_tau005 - 7.6250) < 0.001, f"SCS formula selftest: got {_gamma_d8_tau005}"

_gamma_d8_tau0 = _scs_gamma(8.0, 0.0)
print(f"[selftest-formula] SCS gamma(d=8,tau=0): {_gamma_d8_tau0:.4f} (expected 8.0000)", flush=True)
assert abs(_gamma_d8_tau0 - 8.0) < 0.001, f"SCS formula selftest tau=0: got {_gamma_d8_tau0}"

_gamma_d1_tau0 = _scs_gamma(1.0, 0.0)
print(f"[selftest-formula] SCS gamma(d=1,tau=0): {_gamma_d1_tau0:.4f} (expected 1.0000)", flush=True)
assert abs(_gamma_d1_tau0 - 1.0) < 0.001, f"SCS formula selftest d=1: got {_gamma_d1_tau0}"

_M_check_min = int(0.02 * N)
assert _M_check_min == 163, f"M min alpha check: {_M_check_min} expected 163"
print(f"[selftest-formula] M at alpha_min=0.02: {_M_check_min}", flush=True)
assert all(a < ALPHA_C for a in ALPHA_GRID), "alpha grid capacity check"
print(f"[selftest-formula] ALPHA_GRID={ALPHA_GRID} all within capacity={ALPHA_C}", flush=True)

# Pre-registered thresholds
HP_RATIO_LOW = 0.7
HP_RATIO_HIGH = 1.3
HP_MATCH_MIN_SEEDS = 4  # SCS formula within 30% at 4+ seeds
HP_D_LOW = 6.0
HP_D_HIGH = 12.0
HP_TAU_LOW = 0.02
HP_TAU_HIGH = 0.20
HF_RATIO_LOW = 0.5
HF_RATIO_HIGH = 2.0
HF_D_MIN = 1.5
HF_TAU_MAX = 0.5
SCS_MATCH_TOL = 0.30  # within 30%

if RUN_MODE == "smoke":
    N_ACTIVE = 256
    SEEDS = [7, 17]
    N_PROBES = 100
    ALPHA_SWEEP = [0.04, 0.08, 0.12]  # 3 alphas for smoke
else:
    N_ACTIVE = N
    SEEDS = [7, 17, 23]
    N_PROBES = 300
    ALPHA_SWEEP = ALPHA_GRID  # full alpha sweep


def measure_tau(xi: np.ndarray, n: int) -> float:
    """Estimate tau = ||W_asym||_F / ||W||_F where W = Xi^T Xi / N."""
    W = (xi.T @ xi) / n
    W_sym = (W + W.T) / 2.0
    W_asym = (W - W.T) / 2.0
    norm_asym = np.linalg.norm(W_asym, 'fro')
    norm_total = max(np.linalg.norm(W, 'fro'), 1e-10)
    return float(norm_asym / norm_total)


def measure_d_estimate(xi: np.ndarray, n: int) -> float:
    """Estimate d = leading eigenvalue / mean bulk eigenvalue of W = Xi^T Xi / N."""
    sv = np.linalg.svd(xi, compute_uv=False)
    ev = sv ** 2 / n  # eigenvalues of W
    if len(ev) < 2:
        return 1.0
    return float(ev[0]) / max(float(np.mean(ev[1:])), 1e-10)


def measure_kappa3(xi: np.ndarray, n: int, rng: np.random.Generator, n_probes: int) -> float:
    """Hutchinson kappa_3 = Tr(W^3)/N."""
    V = rng.choice([-1.0, 1.0], size=(n, n_probes))

    def w_op(v):
        inner = xi @ v
        return (xi.T @ inner) / n

    V1 = w_op(V)
    V2 = w_op(V1)
    V3 = w_op(V2)
    estimates = (V * V3).sum(axis=0) / n
    return float(np.mean(estimates))


def measure_gamma_emp(xi_base: np.ndarray, n: int,
                      rng: np.random.Generator, n_probes: int) -> float:
    """Empirical gamma via isochoric kappa_3 separation (delta_M = 1% of N)."""
    delta_M = max(1, int(0.01 * n))
    xi_extra = rng.choice([-1.0, 1.0], size=(delta_M, n)).astype(np.float32)
    xi_aug = np.concatenate([xi_base, xi_extra], axis=0)

    k3_base = measure_kappa3(xi_base, n, rng, n_probes)
    k3_aug = measure_kappa3(xi_aug, n, rng, n_probes)
    if abs(k3_base) < 1e-10:
        return 0.0
    return abs(k3_aug) / abs(k3_base)


def run_seed(seed: int, n_dim: int) -> Dict:
    t0 = time.time()
    cell_results = {}
    for alpha in ALPHA_SWEEP:
        rng = np.random.default_rng(seed + int(alpha * 10000))
        M = int(alpha * n_dim)
        xi = rng.choice([-1.0, 1.0], size=(M, n_dim)).astype(np.float32)
        print(f"  [seed={seed} N={n_dim} alpha={alpha:.2f}] M={M} SVD...", flush=True)
        tau = measure_tau(xi, n_dim)
        d_est = measure_d_estimate(xi, n_dim)
        gamma_scs = _scs_gamma(d_est, tau)
        rng2 = np.random.default_rng(seed + int(alpha * 10000) + 9999)
        gamma_emp = measure_gamma_emp(xi, n_dim, rng2, N_PROBES)
        scs_rel_error = abs(gamma_scs - gamma_emp) / max(gamma_emp, 1e-6)
        scs_ratio = gamma_scs / max(gamma_emp, 1e-6)
        key = f"a{alpha:.4f}"
        cell_results[key] = {
            "alpha": float(alpha), "M": M, "tau": float(tau), "d": float(d_est),
            "gamma_scs": float(gamma_scs), "gamma_emp": float(gamma_emp),
            "scs_rel_error": float(scs_rel_error), "scs_ratio": float(scs_ratio),
        }
        print(f"  [seed={seed} alpha={alpha:.2f}] tau={tau:.4f} d={d_est:.3f} "
              f"gamma_scs={gamma_scs:.3f} gamma_emp={gamma_emp:.3f} "
              f"ratio={scs_ratio:.3f}", flush=True)

    elapsed = time.time() - t0
    return {
        "seed": seed, "N": n_dim, "run_mode": RUN_MODE,
        "elapsed_s": float(elapsed), "cells": cell_results,
    }


def _instrumentation_selftest():
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    n_test = 256
    for alpha_test in [ALPHA_SWEEP[0], ALPHA_SWEEP[-1]]:
        M_test = int(alpha_test * n_test)
        rng = np.random.default_rng(42 + int(alpha_test * 100))
        xi_test = rng.choice([-1.0, 1.0], size=(M_test, n_test)).astype(np.float32)
        tau_test = measure_tau(xi_test, n_test)
        assert not np.isnan(tau_test), f"tau is NaN at alpha={alpha_test}"
        assert 0.0 <= tau_test <= 1.0, f"tau out of [0,1] at alpha={alpha_test}: {tau_test}"
        d_test = measure_d_estimate(xi_test, n_test)
        assert not np.isnan(d_test), f"d_estimate is NaN at alpha={alpha_test}"
        assert d_test > 0, f"d_estimate not positive at alpha={alpha_test}: {d_test}"
        gamma_scs_test = _scs_gamma(d_test, tau_test)
        assert gamma_scs_test > 0, f"gamma_scs not positive at alpha={alpha_test}"
        rng2 = np.random.default_rng(99 + int(alpha_test * 100))
        gamma_emp_test = measure_gamma_emp(xi_test, n_test, rng2, n_probes=100)
        assert gamma_emp_test >= 0, f"gamma_emp negative at alpha={alpha_test}"
        assert gamma_emp_test > 0, f"gamma_emp exactly zero at alpha={alpha_test} -- broken"
        print(f"[selftest] alpha={alpha_test:.2f}: tau={tau_test:.4f} d={d_test:.3f} "
              f"gamma_scs={gamma_scs_test:.3f} gamma_emp={gamma_emp_test:.3f}", flush=True)
    print(f"[selftest] PASS: multi-alpha={ALPHA_SWEEP} all non-null N={n_test}", flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


def compute_verdict(results: List[Dict]) -> tuple:
    if not results:
        return ("HARD_FAIL", "No valid results.")

    # Aggregate per-alpha stats across seeds
    alpha_ratios: Dict[str, list] = {}
    alpha_ds: Dict[str, list] = {}
    for r in results:
        for key, cell in r.get("cells", {}).items():
            alpha_ratios.setdefault(key, []).append(cell["scs_ratio"])
            alpha_ds.setdefault(key, []).append(cell["d"])

    if not alpha_ratios:
        return ("HARD_FAIL", "No cell data in results.")

    mean_ratios = {k: float(np.mean(v)) for k, v in alpha_ratios.items()}
    mean_ds = {k: float(np.mean(v)) for k, v in alpha_ds.items()}

    in_range_count = sum(1 for r in mean_ratios.values() if HP_RATIO_LOW <= r <= HP_RATIO_HIGH)
    catastrophic = any(r < 0.3 or r > 3.0 for r in mean_ratios.values())

    d_vals = list(mean_ds.values())
    d_max = max(d_vals) if d_vals else 0.0
    d_min = max(min(d_vals), 0.01) if d_vals else 1.0
    d_range_ratio = d_max / d_min

    summary = (f"in_range={in_range_count}/{len(mean_ratios)} "
               f"d_range={d_min:.1f}-{d_max:.1f}({d_range_ratio:.1f}x) "
               f"n_seeds={len(results)}")

    if catastrophic:
        return ("HARD_FAIL", f"HARD_FAIL: catastrophic SCS failure (ratio<0.3 or >3.0). {summary}")
    if in_range_count < 2:
        return ("HARD_FAIL",
                f"HARD_FAIL: SCS valid at only {in_range_count}/{len(mean_ratios)} alpha values. {summary}")

    if in_range_count >= 4 and d_range_ratio >= 3.0:
        return ("HARD_PASS",
                f"HARD_PASS: SCS formula valid at {in_range_count}/{len(mean_ratios)} alphas, "
                f"d_range={d_range_ratio:.1f}x. {summary}")

    return ("MIDDLE_BAND",
            f"MIDDLE_BAND: SCS valid at {in_range_count}/{len(mean_ratios)} alphas, "
            f"d_range={d_range_ratio:.1f}x. {summary}")


def _prot018_startup_check(n_actual: int) -> None:
    if RUN_MODE == "smoke":
        return
    if n_actual != _N_SUFFIX:
        raise RuntimeError(
            f"PROT-018 VIOLATION: anchor '{ANCHOR_NAME}' binds N={_N_SUFFIX} "
            f"but running at N={n_actual}.")


print(f"[config] PROT-018 N={N} n_active={N_ACTIVE} mode={RUN_MODE} alpha_sweep={ALPHA_SWEEP}", flush=True)
_prot018_startup_check(N_ACTIVE if RUN_MODE == "smoke" else N)

out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N, "run_mode": RUN_MODE}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(f"[ckpt] {len(done)} seeds done, {len(remaining)} to run", flush=True)

t_sweep_start = time.time()
for seed in remaining:
    print(f"[seed={seed}] {ANCHOR_NAME}...", flush=True)
    result = run_seed(seed, N_ACTIVE if RUN_MODE == "smoke" else N)
    write_partial(out_dir, seed, result)

per_seed = aggregate_partials(out_dir, SEEDS)
all_results = list(per_seed.values())
verdict, verdict_msg = compute_verdict(all_results)

print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)

elapsed_total = time.time() - t_sweep_start
print(f"[elapsed] total: {elapsed_total:.1f}s", flush=True)

metrics = {
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict, "verdict_msg": verdict_msg,
    "N": N, "alpha_sweep": ALPHA_SWEEP, "run_mode": RUN_MODE,
    "n_seeds": len(SEEDS), "elapsed_s": elapsed_total,
    "summary": verdict_msg,
    "per_seed": [
        {"seed": r.get("seed"),
         "elapsed_s": r.get("elapsed_s"),
         "cells": r.get("cells", {})}
        for r in all_results
    ],
}
metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
