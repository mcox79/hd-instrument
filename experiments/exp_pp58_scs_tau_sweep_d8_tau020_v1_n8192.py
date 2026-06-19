"""
pp58_scs_tau_sweep_d8_tau020_v1_n8192 -- PP-58 SCS framework tau sweep at d=8, tau_target=0.20.

CONTEXT (v378 cycle 48 all-night burst):
  tau=0.05 HARD_FAILed (d_estimate=1.487 < 1.5, spike condition violated).
  tau=0.10 completed. tau=0.15 completed. Continuing tau sweep to tau=0.20.
  This experiment constructs Xi with explicit asymmetry mixing to target tau_target=0.20.
  The SCS formula gamma = (d + tau/d) / (1+tau) at d=8, tau=0.20.
  gamma = (8 + 0.20/8) / (1.20) = (8.025) / 1.20 = 6.6875.
  Key question: does tau=0.20 asymmetry enable spike condition d >= 1.5?

DESIGN (same controlled-asymmetry approach as tau=0.15):
  W = (1 - tau_target) * W_sym + tau_target * W_asym
  where W_sym = Xi^T Xi / N (standard Hopfield), W_asym = (W_rand - W_rand^T) / 2.

SCIENTIFIC QUESTION:
  At tau_target=0.20, does controlled asymmetric W produce d >= 1.5
  and does SCS formula gamma_SCS = (d + tau/d) / (1+tau) match gamma_emp?

PRE-REGISTERED BANDS:
  HARD-PASS (SCS formula with controlled tau):
    - mean d_estimate >= 1.5 (spike condition met with asymmetric W).
    - gamma_SCS within 30% of gamma_emp at 4/5 seeds AND mean ratio in [0.7, 1.3].
    - tau_actual in [0.13, 0.28] (within 40% of tau_target=0.20).
  MIDDLE:
    - d_estimate in [1.2, 1.5) (marginal spike) OR ratio in [0.5, 1.5).
    - tau_actual outside [0.13, 0.28] but d_estimate >= 1.2.
  HARD-FAIL:
    - mean d_estimate < 1.2 (no spike even with asymmetric W).
    - OR mean ratio < 0.5 or > 2.0 (SCS formula off by >2x).
    - OR tau_actual < 0.09 (asymmetry injection failed).

FORMULA SELF-TESTS (PROT-022):
  1. SCS formula at d=8, tau=0.20: gamma = (8 + 0.20/8) / (1 + 0.20).
     (8 + 0.025) / 1.20 = 8.025 / 1.20 = 6.6875.
     [INPUT: d=8, tau=0.20] [EXPECTED: 6.6875 within 0.001]
  2. SCS formula at d=8, tau=0: gamma=8.0. [EXPECTED: 8.0]
  3. SCS formula at d=1, tau=0: gamma=1.0. [EXPECTED: 1.0]
  4. M = int(0.05 * 8192) = 409. [EXPECTED: 409]
  5. tau_target * N_dims > 0 (asymmetry scale check). [EXPECTED: True]

PROT-018: anchor has _n8192; N MUST = 8192.
PROT-021: seed checkpoints keyed with run_mode + seed.
QUEUE: remote_cpu_queue (pure numpy; CPU; controlled-asymmetry W construction).
TIMEOUT ESTIMATE: Similar to tau=0.15 test (~9000s). Use floor: 21600s.
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
    import numpy as np
except ImportError:
    print("[FATAL] numpy not installed.", flush=True)
    sys.exit(1)

from experiments._seed_checkpoint import get_output_dir, resumable_seeds, write_partial, aggregate_partials

ANCHOR_NAME = "pp58_scs_tau_sweep_d8_tau020_v1_n8192"

_N_SUFFIX = 8192
N = 8192
assert N == _N_SUFFIX, f"PROT-018: anchor _n{_N_SUFFIX} but N={N}"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

ALPHA_FIXED = 0.05
TAU_TARGET = 0.20
ALPHA_C = 0.138
assert ALPHA_C > ALPHA_FIXED

# PROT-022 formula self-tests at module scope (arithmetic only, no numpy)
def _scs_gamma(d: float, tau: float) -> float:
    return (d + tau / d) / (1.0 + tau)

_gamma_d8_tau020 = _scs_gamma(8.0, 0.20)
print(f"[selftest-formula] SCS gamma(d=8,tau=0.20): {_gamma_d8_tau020:.4f} (expected 6.6875)", flush=True)
assert abs(_gamma_d8_tau020 - 6.6875) < 0.001, f"SCS formula selftest tau=0.20: got {_gamma_d8_tau020}"

_gamma_d8_tau0 = _scs_gamma(8.0, 0.0)
print(f"[selftest-formula] SCS gamma(d=8,tau=0): {_gamma_d8_tau0:.4f} (expected 8.0000)", flush=True)
assert abs(_gamma_d8_tau0 - 8.0) < 0.001, f"SCS formula selftest tau=0: got {_gamma_d8_tau0}"

_gamma_d1_tau0 = _scs_gamma(1.0, 0.0)
print(f"[selftest-formula] SCS gamma(d=1,tau=0): {_gamma_d1_tau0:.4f} (expected 1.0000)", flush=True)
assert abs(_gamma_d1_tau0 - 1.0) < 0.001, f"SCS formula selftest d=1: got {_gamma_d1_tau0}"

_M_check = int(ALPHA_FIXED * N)
assert _M_check == 409, f"M check: {_M_check} expected 409"
print(f"[selftest-formula] M = {_M_check} at N={N} alpha={ALPHA_FIXED}", flush=True)
print(f"[selftest-formula] TAU_TARGET * N = {TAU_TARGET * N:.1f} > 0: True", flush=True)

# Pre-registered thresholds
HP_D_MIN = 1.5
HP_RATIO_LOW = 0.7
HP_RATIO_HIGH = 1.3
HP_MATCH_MIN_SEEDS = 4
HP_TAU_ACT_LOW = 0.13
HP_TAU_ACT_HIGH = 0.28
MID_D_MIN = 1.2
HF_D_MIN = 1.2
HF_RATIO_LOW = 0.5
HF_RATIO_HIGH = 2.0
HF_TAU_ACT_MIN = 0.09
SCS_MATCH_TOL = 0.30

if RUN_MODE == "smoke":
    N_ACTIVE = 256
    SEEDS = [7, 17]
    N_PROBES = 100
else:
    N_ACTIVE = N
    SEEDS = [7, 17, 23, 31, 41]
    N_PROBES = 500


def build_asymmetric_W(xi: np.ndarray, n: int, tau_t: float) -> np.ndarray:
    """Build W with controlled asymmetry: W = (1-tau_t)*W_sym + tau_t*W_rand_asym."""
    W_sym = (xi.T @ xi) / n
    rng_asym = np.random.default_rng(seed=999)
    W_rand = rng_asym.standard_normal((n, n)).astype(np.float32) / math.sqrt(n)
    W_rand_asym = (W_rand - W_rand.T) / 2.0
    scale = np.linalg.norm(W_sym, 'fro') / max(np.linalg.norm(W_rand_asym, 'fro'), 1e-10)
    W_rand_asym_scaled = W_rand_asym * scale
    W = (1.0 - tau_t) * W_sym + tau_t * W_rand_asym_scaled
    return W


def measure_tau_from_W(W: np.ndarray) -> float:
    """Measure tau = ||W_asym||_F / ||W||_F from an existing W."""
    W_sym = (W + W.T) / 2.0
    W_asym = (W - W.T) / 2.0
    norm_asym = np.linalg.norm(W_asym, 'fro')
    norm_total = max(np.linalg.norm(W, 'fro'), 1e-10)
    return float(norm_asym / norm_total)


def measure_d_from_W(W: np.ndarray) -> float:
    """Estimate d = leading eigenvalue / mean bulk eigenvalue of W."""
    ev = np.linalg.eigvalsh(W)
    ev_sorted = np.sort(np.abs(ev))[::-1]
    if len(ev_sorted) < 2:
        return 1.0
    return float(ev_sorted[0]) / max(float(np.mean(ev_sorted[1:])), 1e-10)


def measure_kappa3_from_W(W: np.ndarray, n: int, rng: np.random.Generator, n_probes: int) -> float:
    """Hutchinson kappa_3 = Tr(W^3)/N using existing W."""
    V = rng.choice([-1.0, 1.0], size=(n, n_probes))
    V1 = W @ V
    V2 = W @ V1
    V3 = W @ V2
    estimates = (V * V3).sum(axis=0) / n
    return float(np.mean(estimates))


def measure_gamma_emp_from_W(W_base: np.ndarray, n: int,
                              rng: np.random.Generator, n_probes: int) -> float:
    """Empirical gamma via isochoric kappa_3 separation (delta_M = 1% of N)."""
    delta_M = max(1, int(0.01 * n))
    xi_extra = rng.choice([-1.0, 1.0], size=(delta_M, n)).astype(np.float32)
    W_extra = (xi_extra.T @ xi_extra) / n
    W_aug = W_base + W_extra

    k3_base = measure_kappa3_from_W(W_base, n, rng, n_probes)
    k3_aug = measure_kappa3_from_W(W_aug, n, rng, n_probes)
    if abs(k3_base) < 1e-10:
        return 0.0
    return abs(k3_aug) / abs(k3_base)


def run_seed(seed: int, n_dim: int) -> Dict:
    rng = np.random.default_rng(seed)
    t0 = time.time()
    M = int(ALPHA_FIXED * n_dim)
    xi = rng.choice([-1.0, 1.0], size=(M, n_dim)).astype(np.float32)

    print(f"  [seed={seed} N={n_dim}] M={M} building asymmetric W (tau_target={TAU_TARGET})...",
          flush=True)
    W = build_asymmetric_W(xi, n_dim, TAU_TARGET)

    tau_actual = measure_tau_from_W(W)
    print(f"  [seed={seed}] tau_actual={tau_actual:.4f} (target={TAU_TARGET})", flush=True)

    print(f"  [seed={seed}] measuring d via eigvalsh...", flush=True)
    d_est = measure_d_from_W(W)
    gamma_scs = _scs_gamma(d_est, tau_actual)

    rng2 = np.random.default_rng(seed + 1000)
    print(f"  [seed={seed}] measuring gamma_emp via kappa3...", flush=True)
    gamma_emp = measure_gamma_emp_from_W(W, n_dim, rng2, N_PROBES)

    scs_rel_error = abs(gamma_scs - gamma_emp) / max(gamma_emp, 1e-6)
    scs_ratio = gamma_scs / max(gamma_emp, 1e-6)

    elapsed = time.time() - t0
    print(f"  [seed={seed}] tau_actual={tau_actual:.4f} d={d_est:.3f} "
          f"gamma_scs={gamma_scs:.3f} gamma_emp={gamma_emp:.3f} "
          f"rel_err={scs_rel_error:.3f} ratio={scs_ratio:.3f} "
          f"elapsed={elapsed:.1f}s", flush=True)

    return {
        "seed": seed, "N": n_dim, "run_mode": RUN_MODE,
        "tau_target": float(TAU_TARGET),
        "tau_actual": float(tau_actual),
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

    W_test = build_asymmetric_W(xi_test, n_test, TAU_TARGET)
    assert W_test.shape == (n_test, n_test), f"W shape mismatch: {W_test.shape}"

    tau_test = measure_tau_from_W(W_test)
    assert not np.isnan(tau_test), "tau_actual is NaN"
    assert tau_test > 0.0, f"tau_actual is zero (asymmetry injection failed): {tau_test}"
    print(f"[selftest] tau_actual={tau_test:.4f} at test scale N={n_test}", flush=True)

    d_test = measure_d_from_W(W_test)
    assert not np.isnan(d_test), "d_estimate is NaN"
    assert d_test > 0, f"d_estimate is not positive: {d_test}"

    gamma_scs_test = _scs_gamma(d_test, tau_test)
    assert gamma_scs_test > 0, f"gamma_scs is not positive: {gamma_scs_test}"

    rng2 = np.random.default_rng(99)
    gamma_emp_test = measure_gamma_emp_from_W(W_test, n_test, rng2, n_probes=50)
    assert gamma_emp_test >= 0, f"gamma_emp is negative: {gamma_emp_test}"
    assert gamma_emp_test > 0, f"gamma_emp is exactly zero -- instrumentation broken"

    print(f"[selftest] PASS: tau_actual={tau_test:.4f} d={d_test:.3f} "
          f"gamma_scs={gamma_scs_test:.3f} gamma_emp={gamma_emp_test:.3f} N={n_test}", flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


def compute_verdict(results: List[Dict]) -> tuple:
    if not results:
        return ("HARD_FAIL", "No valid results.")

    taus_actual = [r["tau_actual"] for r in results]
    ds = [r["d_estimate"] for r in results]
    ratios = [r["scs_ratio"] for r in results]
    gamma_emps = [r["gamma_emp"] for r in results]
    gamma_scss = [r["gamma_scs"] for r in results]

    mean_tau = float(np.mean(taus_actual))
    mean_d = float(np.mean(ds))
    mean_ratio = float(np.mean(ratios))
    mean_gamma_emp = float(np.mean(gamma_emps))
    mean_gamma_scs = float(np.mean(gamma_scss))

    match_count = sum(1 for r in results if r["scs_rel_error"] < SCS_MATCH_TOL)

    summary = (f"gamma_emp={mean_gamma_emp:.3f} gamma_scs={mean_gamma_scs:.3f} "
               f"ratio={mean_ratio:.3f} tau_actual={mean_tau:.4f} d={mean_d:.3f} "
               f"match_{SCS_MATCH_TOL:.0%}={match_count}/{len(results)} "
               f"tau_target={TAU_TARGET}")

    if mean_d < HF_D_MIN:
        return ("HARD_FAIL",
                f"HARD_FAIL: d_estimate={mean_d:.3f} < {HF_D_MIN} (no spike even with asymmetric W). "
                f"{summary}")
    if mean_tau < HF_TAU_ACT_MIN:
        return ("HARD_FAIL",
                f"HARD_FAIL: tau_actual={mean_tau:.4f} < {HF_TAU_ACT_MIN} "
                f"(asymmetry injection failed). {summary}")
    if mean_ratio < HF_RATIO_LOW or mean_ratio > HF_RATIO_HIGH:
        return ("HARD_FAIL",
                f"HARD_FAIL: SCS ratio={mean_ratio:.3f} outside [{HF_RATIO_LOW},{HF_RATIO_HIGH}]. "
                f"SCS formula off by >2x. {summary}")

    d_ok = mean_d >= HP_D_MIN
    tau_ok = HP_TAU_ACT_LOW <= mean_tau <= HP_TAU_ACT_HIGH
    ratio_ok = HP_RATIO_LOW <= mean_ratio <= HP_RATIO_HIGH
    if d_ok and tau_ok and ratio_ok and match_count >= HP_MATCH_MIN_SEEDS:
        return ("HARD_PASS",
                f"HARD_PASS: spike ok (d={mean_d:.3f}>={HP_D_MIN}), tau_ok={tau_ok}, "
                f"ratio_ok={ratio_ok}, match={match_count}/{len(results)}. {summary}")

    return ("MIDDLE_BAND",
            f"MIDDLE_BAND: d_ok={d_ok} tau_ok={tau_ok} ratio_ok={ratio_ok} "
            f"match={match_count}/{len(results)}. {summary}")


def _prot018_startup_check(n_actual: int) -> None:
    if RUN_MODE == "smoke":
        return
    if n_actual != _N_SUFFIX:
        raise RuntimeError(
            f"PROT-018 VIOLATION: anchor '{ANCHOR_NAME}' binds N={_N_SUFFIX} "
            f"but running at N={n_actual}.")


print(f"[config] PROT-018 N={N} n_active={N_ACTIVE} mode={RUN_MODE} "
      f"alpha={ALPHA_FIXED} tau_target={TAU_TARGET}", flush=True)
_prot018_startup_check(N_ACTIVE if RUN_MODE == "smoke" else N)

out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N, "run_mode": RUN_MODE, "tau_target": TAU_TARGET}
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
    "N": N, "alpha": ALPHA_FIXED, "tau_target": TAU_TARGET,
    "run_mode": RUN_MODE,
    "n_seeds": len(SEEDS), "elapsed_s": elapsed_total,
    "summary": verdict_msg,
    "per_seed": [
        {"seed": r.get("seed"),
         "tau_target": r.get("tau_target"),
         "tau_actual": r.get("tau_actual"),
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
