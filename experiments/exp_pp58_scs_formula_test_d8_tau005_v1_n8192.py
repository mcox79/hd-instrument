"""
pp58_scs_formula_test_d8_tau005_v1_n8192 -- PP-58 SCS framework direct formula test
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

ANCHOR_NAME = "pp58_scs_formula_test_d8_tau005_v1_n8192"

_N_SUFFIX = 8192
N = 8192
assert N == _N_SUFFIX, f"PROT-018: anchor _n{_N_SUFFIX} but N={N}"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

ALPHA_FIXED = 0.05
ALPHA_C = 0.138
assert ALPHA_C > ALPHA_FIXED, f"alpha_c={ALPHA_C} must be > ALPHA_FIXED={ALPHA_FIXED}"

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

_M_check = int(ALPHA_FIXED * N)
assert _M_check == 409, f"M check: {_M_check} expected 409"
print(f"[selftest-formula] M = {_M_check} at N={N} alpha={ALPHA_FIXED}", flush=True)

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
else:
    N_ACTIVE = N
    SEEDS = [7, 17, 23, 31, 41]
    N_PROBES = 500


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
    rng = np.random.default_rng(seed)
    t0 = time.time()
    M = int(ALPHA_FIXED * n_dim)
    xi = rng.choice([-1.0, 1.0], size=(M, n_dim)).astype(np.float32)

    print(f"  [seed={seed} N={n_dim}] M={M} building W...", flush=True)
    tau = measure_tau(xi, n_dim)
    d_est = measure_d_estimate(xi, n_dim)
    gamma_scs = _scs_gamma(d_est, tau)

    rng2 = np.random.default_rng(seed + 1000)
    gamma_emp = measure_gamma_emp(xi, n_dim, rng2, N_PROBES)

    scs_rel_error = abs(gamma_scs - gamma_emp) / max(gamma_emp, 1e-6)
    scs_ratio = gamma_scs / max(gamma_emp, 1e-6)

    elapsed = time.time() - t0
    print(f"  [seed={seed}] tau={tau:.4f} d={d_est:.3f} "
          f"gamma_scs={gamma_scs:.3f} gamma_emp={gamma_emp:.3f} "
          f"rel_err={scs_rel_error:.3f} ratio={scs_ratio:.3f} "
          f"elapsed={elapsed:.1f}s", flush=True)

    return {
        "seed": seed, "N": n_dim, "run_mode": RUN_MODE,
        "tau_estimate": float(tau),
        "d_estimate": float(d_est),
        "gamma_scs": float(gamma_scs),
        "gamma_emp": float(gamma_emp),
        "scs_rel_error": float(scs_rel_error),
        "scs_ratio": float(scs_ratio),
        "elapsed_s": float(elapsed),
    }


def _instrumentation_selftest():
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    n_test = 256
    M_test = int(ALPHA_FIXED * n_test)
    rng = np.random.default_rng(42)
    xi_test = rng.choice([-1.0, 1.0], size=(M_test, n_test)).astype(np.float32)

    tau_test = measure_tau(xi_test, n_test)
    assert not np.isnan(tau_test), "tau is NaN"
    assert 0.0 <= tau_test <= 1.0, f"tau out of [0,1]: {tau_test}"

    d_test = measure_d_estimate(xi_test, n_test)
    assert not np.isnan(d_test), "d_estimate is NaN"
    assert d_test > 0, f"d_estimate is not positive: {d_test}"

    gamma_scs_test = _scs_gamma(d_test, tau_test)
    assert gamma_scs_test > 0, f"gamma_scs is not positive: {gamma_scs_test}"

    rng2 = np.random.default_rng(99)
    gamma_emp_test = measure_gamma_emp(xi_test, n_test, rng2, n_probes=100)
    assert gamma_emp_test >= 0, f"gamma_emp is negative: {gamma_emp_test}"
    assert gamma_emp_test > 0, f"gamma_emp is exactly zero -- instrumentation broken"

    print(f"[selftest] PASS: tau={tau_test:.4f} d={d_test:.3f} "
          f"gamma_scs={gamma_scs_test:.3f} gamma_emp={gamma_emp_test:.3f} N={n_test}", flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


def compute_verdict(results: List[Dict]) -> tuple:
    if not results:
        return ("HARD_FAIL", "No valid results.")

    taus = [r["tau_estimate"] for r in results]
    ds = [r["d_estimate"] for r in results]
    ratios = [r["scs_ratio"] for r in results]
    gamma_emps = [r["gamma_emp"] for r in results]
    gamma_scss = [r["gamma_scs"] for r in results]

    mean_tau = float(np.mean(taus))
    mean_d = float(np.mean(ds))
    mean_ratio = float(np.mean(ratios))
    mean_gamma_emp = float(np.mean(gamma_emps))
    mean_gamma_scs = float(np.mean(gamma_scss))

    match_count = sum(1 for r in results if r["scs_rel_error"] < SCS_MATCH_TOL)

    summary = (f"gamma_emp={mean_gamma_emp:.3f} gamma_scs={mean_gamma_scs:.3f} "
               f"ratio={mean_ratio:.3f} tau={mean_tau:.4f} d={mean_d:.3f} "
               f"match_{SCS_MATCH_TOL:.0%}={match_count}/{len(results)}")

    # HARD-FAIL checks
    if mean_d < HF_D_MIN:
        return ("HARD_FAIL",
                f"HARD_FAIL: d_estimate={mean_d:.3f} < {HF_D_MIN} (no spike; SCS assumption violated). "
                f"{summary}")
    if mean_tau > HF_TAU_MAX:
        return ("HARD_FAIL",
                f"HARD_FAIL: tau_estimate={mean_tau:.4f} > {HF_TAU_MAX} "
                f"(not near-Ginibre; SCS assumption violated). {summary}")
    if mean_ratio < HF_RATIO_LOW or mean_ratio > HF_RATIO_HIGH:
        return ("HARD_FAIL",
                f"HARD_FAIL: SCS ratio={mean_ratio:.3f} outside [{HF_RATIO_LOW},{HF_RATIO_HIGH}]. "
                f"SCS formula off by >2x. {summary}")

    # HARD-PASS
    d_in_range = HP_D_LOW <= mean_d <= HP_D_HIGH
    tau_in_range = HP_TAU_LOW <= mean_tau <= HP_TAU_HIGH
    ratio_in_range = HP_RATIO_LOW <= mean_ratio <= HP_RATIO_HIGH
    if (match_count >= HP_MATCH_MIN_SEEDS and d_in_range and
            tau_in_range and ratio_in_range):
        return ("HARD_PASS",
                f"HARD_PASS: SCS formula validated: match={match_count}/{len(results)} "
                f"ratio_in_range={ratio_in_range} d_ok={d_in_range} tau_ok={tau_in_range}. "
                f"{summary}")

    return ("MIDDLE_BAND",
            f"MIDDLE_BAND: match={match_count}/{len(results)} ratio={mean_ratio:.3f} "
            f"d_ok={d_in_range} tau_ok={tau_in_range}. {summary}")


def _prot018_startup_check(n_actual: int) -> None:
    if RUN_MODE == "smoke":
        return
    if n_actual != _N_SUFFIX:
        raise RuntimeError(
            f"PROT-018 VIOLATION: anchor '{ANCHOR_NAME}' binds N={_N_SUFFIX} "
            f"but running at N={n_actual}.")


print(f"[config] PROT-018 N={N} n_active={N_ACTIVE} mode={RUN_MODE} alpha={ALPHA_FIXED}", flush=True)
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
    "N": N, "alpha": ALPHA_FIXED, "run_mode": RUN_MODE,
    "n_seeds": len(SEEDS), "elapsed_s": elapsed_total,
    "summary": verdict_msg,
    "per_seed": [
        {"seed": r.get("seed"),
         "tau": r.get("tau_estimate"),
         "d": r.get("d_estimate"),
         "gamma_scs": r.get("gamma_scs"),
         "gamma_emp": r.get("gamma_emp"),
         "scs_rel_error": r.get("scs_rel_error"),
         "scs_ratio": r.get("scs_ratio"),
         "elapsed_s": r.get("elapsed_s")}
        for r in all_results
    ],
}
metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
