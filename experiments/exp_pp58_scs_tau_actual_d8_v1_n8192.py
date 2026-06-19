"""
pp58_scs_tau_actual_d8_v1_n8192 -- PP-58 SCS R1 rescue: evaluate at substrate's ACTUAL tau, not target.

CONTEXT (v382 cycle 52 -- R1 rescue):
  Cycle 50 (PP-58 SCS tau_target=0.50 sweep) found ratio=1.416 -- the FIRST close fit across the
  entire tau sweep -- but discovered tau_target=0.50 produced tau_actual=0.71 (41% overshoot).
  Per orchestrator priorities cycle 52: re-run with the controlled-asymmetry build TARGETING
  tau=0.71 (the substrate's actual operating tau from cycle 50), so the substrate genuinely
  operates at tau~0.71, and check whether the SCS formula gamma=(d + tau/d)/(1+tau) -- evaluated
  at the measured tau_actual -- agrees with the empirical isochoric-kappa3 gamma within 30%.
  This is the cheapest path to either CONFIRMING the SCS substrate-physics framework or retiring it.

  INTERPRETATION NOTE (surfaced to orchestrator): the spec "set TAU = tau_actual (~0.71)" is read
  here as setting the build target TAU_TARGET=0.71 so the substrate operates in the tau~0.71 regime.
  gamma_SCS is computed from the *measured* tau_actual of the resulting W (not from the target),
  matching "evaluate at substrate's actual tau". If the orchestrator intended instead to reproduce
  the cycle-50 W (tau_target=0.50 -> tau_actual=0.71) unchanged, that is redundant with cycle 50.

DESIGN (same controlled-asymmetry approach as tau050):
  W = (1 - tau_target) * W_sym + tau_target * W_asym
  where W_sym = Xi^T Xi / N (standard Hopfield), W_asym = (W_rand - W_rand^T) / 2.
  gamma_SCS = (d + tau_actual/d) / (1 + tau_actual), evaluated at measured tau_actual.

SCIENTIFIC QUESTION:
  With the substrate operating at tau~0.71, does gamma_SCS (at measured tau_actual) agree with
  the empirical gamma within 30%, closing the gap that the tau-sweep approached at tau=0.50?

PRE-REGISTERED BANDS (orchestrator cycle 52 spec):
  HARD-PASS: ratio in [0.85, 1.18] OR match_30% >= 0.6 (formula within 30% on >= 3/5 seeds).
  MIDDLE:    ratio in [0.5, 2.0] but match_30% < 0.6.
  HARD-FAIL: ratio < 0.5 OR ratio > 2.0.

FORMULA SELF-TESTS (PROT-022):
  1. SCS formula at d=8, tau=0.71: gamma = (8 + 0.71/8) / (1 + 0.71) = 8.08875 / 1.71 = 4.7303.
     [INPUT: d=8, tau=0.71] [EXPECTED: 4.7303 within 0.001]
  2. SCS formula at d=8, tau=0: gamma=8.0. [EXPECTED: 8.0]
  3. SCS formula at d=1, tau=0: gamma=1.0. [EXPECTED: 1.0]
  4. M = int(0.05 * 8192) = 409. [EXPECTED: 409]
  5. tau_target * N > 0 (asymmetry scale check). [EXPECTED: True]

PROT-018: anchor has _n8192; N MUST = 8192.
PROT-021: seed checkpoints keyed with run_mode + seed.
QUEUE: remote_cpu_queue (pure numpy; CPU; controlled-asymmetry W construction).
TIMEOUT ESTIMATE: Similar to tau=0.50 test (~9000s). Use floor: 14400s.
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

ANCHOR_NAME = "pp58_scs_tau_actual_d8_v1_n8192"

_N_SUFFIX = 8192
N = 8192
assert N == _N_SUFFIX, f"PROT-018: anchor _n{_N_SUFFIX} but N={N}"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

ALPHA_FIXED = 0.05
TAU_TARGET = 0.71
ALPHA_C = 0.138
assert ALPHA_C > ALPHA_FIXED

# PROT-022 formula self-tests at module scope (arithmetic only, no numpy)
def _scs_gamma(d: float, tau: float) -> float:
    return (d + tau / d) / (1.0 + tau)

_gamma_d8_tau071 = _scs_gamma(8.0, 0.71)
_expected_tau071 = 8.08875 / 1.71
print(f"[selftest-formula] SCS gamma(d=8,tau=0.71): {_gamma_d8_tau071:.4f} (expected {_expected_tau071:.4f})", flush=True)
assert abs(_gamma_d8_tau071 - _expected_tau071) < 0.001, f"SCS formula selftest tau=0.71: got {_gamma_d8_tau071}"

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

# Pre-registered thresholds (orchestrator cycle 52 spec)
HP_RATIO_LOW = 0.85
HP_RATIO_HIGH = 1.18
HP_MATCH_FRAC = 0.6
MID_RATIO_LOW = 0.5
MID_RATIO_HIGH = 2.0
HF_RATIO_LOW = 0.5
HF_RATIO_HIGH = 2.0
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
    match_frac = match_count / len(results)

    summary = (f"gamma_emp={mean_gamma_emp:.3f} gamma_scs={mean_gamma_scs:.3f} "
               f"ratio={mean_ratio:.3f} tau_actual={mean_tau:.4f} d={mean_d:.3f} "
               f"match_{SCS_MATCH_TOL:.0%}={match_count}/{len(results)} "
               f"tau_target={TAU_TARGET}")

    if mean_ratio < HF_RATIO_LOW or mean_ratio > HF_RATIO_HIGH:
        return ("HARD_FAIL",
                f"HARD_FAIL: SCS ratio={mean_ratio:.3f} outside [{HF_RATIO_LOW},{HF_RATIO_HIGH}]. "
                f"{summary}")

    ratio_ok = HP_RATIO_LOW <= mean_ratio <= HP_RATIO_HIGH
    if ratio_ok or match_frac >= HP_MATCH_FRAC:
        return ("HARD_PASS",
                f"HARD_PASS: ratio_ok={ratio_ok} (ratio={mean_ratio:.3f} in "
                f"[{HP_RATIO_LOW},{HP_RATIO_HIGH}]) OR match_frac={match_frac:.2f}>={HP_MATCH_FRAC}. "
                f"SCS formula validated at substrate actual tau. {summary}")

    return ("MIDDLE_BAND",
            f"MIDDLE_BAND: ratio={mean_ratio:.3f} in [{MID_RATIO_LOW},{MID_RATIO_HIGH}] but "
            f"match_frac={match_frac:.2f}<{HP_MATCH_FRAC}. {summary}")


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
