"""
pp58_scs_d_sweep_tau_actual_v1_n8192 -- PP-58 SCS d-sweep at substrate's actual tau (TAU_TARGET=0.71).

CONTEXT (v382 cycle 53 -- complements pp58_scs_tau_actual_d8_v1_n8192):
  Item A (tau_actual_d8) tests a SINGLE d point (d driven by alpha=0.05). Item B sweeps the d range
  by sweeping alpha (pattern count), which controls the spectral spike strength d, while building the
  controlled-asymmetry W at TAU_TARGET=0.71 (same convention as A). At each cell we measure the
  achieved d and tau_actual, then check whether SCS gamma=(d + tau_actual/d)/(1+tau_actual) agrees
  with the empirical isochoric-kappa3 gamma within 30%.

  NOTE (consistency with cycle 52 FLAG 1): d is a MEASURED quantity (leading/bulk eigenvalue ratio of
  W), not a free knob -- "sweep d in {2,4,6,8,10,12}" is realized by sweeping alpha so the achieved d
  spans a range; achieved d is reported per cell. TAU_TARGET=0.71 matches item A; if the orchestrator
  resolves FLAG 1 toward a calibrated tau_target (~0.50 -> tau_actual~0.71), the same change applies here.

SCIENTIFIC QUESTION:
  Across a range of spike strengths d (via alpha), does the SCS formula (evaluated at measured
  tau_actual) agree with empirical gamma within 30% in a majority of cells?

PRE-REGISTERED BANDS (orchestrator cycle 53 item B):
  HARD-PASS: SCS formula matches (rel_err < 0.30) in >= 4/6 d-cells (mean over seeds).
  MIDDLE:    matches in 2-3/6 d-cells.
  HARD-FAIL: matches in <= 1/6 d-cells.

FORMULA SELF-TESTS (PROT-022):
  1. SCS gamma(d=8, tau=0.71) = (8 + 0.71/8)/(1+0.71) = 8.08875/1.71 = 4.7303. [EXPECTED: 4.7303 +-0.001]
  2. SCS gamma(d=2, tau=0) = 2.0. [EXPECTED: 2.0]
  3. SCS gamma(d=1.5, tau=0) = 1.5. [EXPECTED: 1.5]
  4. alpha_grid all < alpha_c=0.138. [EXPECTED: True for all]
  5. 6 d-cells in the full grid. [EXPECTED: 6]

PROT-018: anchor has _n8192; N MUST = 8192.
PROT-021: seed checkpoints keyed with run_mode + seed.
QUEUE: remote_cpu_queue (pure numpy; CPU; ~45 min total).
TIMEOUT ESTIMATE: 6 cells x asymmetric-W build/eigvalsh; ~2400s. PROT-019 floor for _n8192: 21600s.
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

ANCHOR_NAME = "pp58_scs_d_sweep_tau_actual_v1_n8192"

_N_SUFFIX = 8192
N = 8192
assert N == _N_SUFFIX, f"PROT-018: anchor _n{_N_SUFFIX} but N={N}"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

TAU_TARGET = 0.71
ALPHA_C = 0.138
SCS_MATCH_TOL = 0.30

# PROT-022 formula self-tests at module scope (arithmetic only, no numpy)
def _scs_gamma(d: float, tau: float) -> float:
    return (d + tau / max(d, 1e-10)) / (1.0 + tau)

_g_d8_t071 = _scs_gamma(8.0, 0.71)
_expected_t071 = 8.08875 / 1.71
print(f"[selftest-formula] gamma(d=8,tau=0.71)={_g_d8_t071:.4f} expected {_expected_t071:.4f}", flush=True)
assert abs(_g_d8_t071 - _expected_t071) < 0.001, f"SCS formula selftest tau=0.71: {_g_d8_t071}"

_g_d2 = _scs_gamma(2.0, 0.0)
print(f"[selftest-formula] gamma(d=2,tau=0)={_g_d2:.4f} expected 2.0000", flush=True)
assert abs(_g_d2 - 2.0) < 0.001, f"SCS formula selftest d=2: {_g_d2}"

_g_d15 = _scs_gamma(1.5, 0.0)
print(f"[selftest-formula] gamma(d=1.5,tau=0)={_g_d15:.4f} expected 1.5000", flush=True)
assert abs(_g_d15 - 1.5) < 0.001, f"SCS formula selftest d=1.5: {_g_d15}"

# alpha grid: spans spike strength d (lower alpha -> spikier W -> higher d).
if RUN_MODE == "smoke":
    ALPHA_GRID = [0.01, 0.05, 0.10]
    SEEDS = [7, 17]
    N_ACTIVE = 256
    N_PROBES = 100
else:
    ALPHA_GRID = [0.01, 0.02, 0.04, 0.06, 0.08, 0.10]
    SEEDS = [7, 17, 23, 31, 41]
    N_ACTIVE = N
    N_PROBES = 500

for _a in ALPHA_GRID:
    assert _a < ALPHA_C, f"alpha_grid entry {_a} >= alpha_c={ALPHA_C}"
print(f"[selftest-formula] alpha_grid OK ({len(ALPHA_GRID)} cells): {ALPHA_GRID}", flush=True)

# Pre-registered band thresholds (orchestrator cycle 53 item B)
HP_MATCH_CELLS = 4   # >= 4/6 cells match -> HARD_PASS
HF_MATCH_CELLS = 1   # <= 1/6 cells match -> HARD_FAIL


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
    W_asym = (W - W.T) / 2.0
    norm_asym = np.linalg.norm(W_asym, 'fro')
    norm_total = max(np.linalg.norm(W, 'fro'), 1e-10)
    return float(norm_asym / norm_total)


def measure_d_from_W(W: np.ndarray) -> float:
    ev = np.linalg.eigvalsh(W)
    ev_sorted = np.sort(np.abs(ev))[::-1]
    if len(ev_sorted) < 2:
        return 1.0
    return float(ev_sorted[0]) / max(float(np.mean(ev_sorted[1:])), 1e-10)


def measure_kappa3_from_W(W: np.ndarray, n: int, rng: np.random.Generator, n_probes: int) -> float:
    V = rng.choice([-1.0, 1.0], size=(n, n_probes))
    V1 = W @ V
    V2 = W @ V1
    V3 = W @ V2
    estimates = (V * V3).sum(axis=0) / n
    return float(np.mean(estimates))


def measure_gamma_emp_from_W(W_base: np.ndarray, n: int,
                              rng: np.random.Generator, n_probes: int) -> float:
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
    cells = []
    for alpha in ALPHA_GRID:
        M = max(1, int(alpha * n_dim))
        xi = rng.choice([-1.0, 1.0], size=(M, n_dim)).astype(np.float32)
        W = build_asymmetric_W(xi, n_dim, TAU_TARGET)
        tau_actual = measure_tau_from_W(W)
        d_est = measure_d_from_W(W)
        gamma_scs = _scs_gamma(d_est, tau_actual)
        rng2 = np.random.default_rng(seed + int(alpha * 10000))
        gamma_emp = measure_gamma_emp_from_W(W, n_dim, rng2, N_PROBES)
        rel_err = abs(gamma_scs - gamma_emp) / max(gamma_emp, 1e-6)
        ratio = gamma_scs / max(gamma_emp, 1e-6)
        match = rel_err < SCS_MATCH_TOL
        print(f"  [seed={seed} alpha={alpha:.3f} M={M}] d={d_est:.3f} tau_actual={tau_actual:.4f} "
              f"g_scs={gamma_scs:.3f} g_emp={gamma_emp:.3f} rel_err={rel_err:.3f} "
              f"ratio={ratio:.3f} match={match}", flush=True)
        cells.append({
            "alpha": alpha, "M": M,
            "d_estimate": float(d_est), "tau_actual": float(tau_actual),
            "gamma_scs": float(gamma_scs), "gamma_emp": float(gamma_emp),
            "rel_err": float(rel_err), "ratio": float(ratio), "match": bool(match),
        })
    elapsed = time.time() - t0
    print(f"  [seed={seed}] elapsed={elapsed:.1f}s", flush=True)
    return {"seed": seed, "N": n_dim, "run_mode": RUN_MODE, "cells": cells, "elapsed_s": float(elapsed)}


def _instrumentation_selftest():
    n_test = 256
    M_test = max(1, int(0.05 * n_test))
    rng = np.random.default_rng(42)
    xi_test = rng.choice([-1.0, 1.0], size=(M_test, n_test)).astype(np.float32)
    W_test = build_asymmetric_W(xi_test, n_test, TAU_TARGET)
    assert W_test.shape == (n_test, n_test), f"W shape mismatch: {W_test.shape}"
    tau_t = measure_tau_from_W(W_test)
    d_t = measure_d_from_W(W_test)
    rng2 = np.random.default_rng(99)
    g_emp = measure_gamma_emp_from_W(W_test, n_test, rng2, n_probes=50)
    assert not np.isnan(tau_t) and not np.isnan(d_t), "selftest: NaN in tau or d"
    assert tau_t > 0.0, f"tau_actual zero (asymmetry injection failed): {tau_t}"
    assert d_t > 0, f"d_estimate non-positive: {d_t}"
    assert g_emp > 0, "gamma_emp exactly zero -- instrumentation broken"
    print(f"[selftest] PASS: tau_actual={tau_t:.4f} d={d_t:.3f} gamma_emp={g_emp:.3f} N={n_test}", flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


def compute_verdict(results: List[Dict]) -> tuple:
    if not results:
        return ("HARD_FAIL", "No valid results.")

    # Aggregate per alpha-cell across seeds: a cell "matches" if mean rel_err < tol.
    cell_match = {}
    cell_d = {}
    cell_ratio = {}
    for alpha in ALPHA_GRID:
        rel_errs = []
        ds = []
        ratios = []
        for r in results:
            for c in r.get("cells", []):
                if abs(c["alpha"] - alpha) < 1e-6:
                    rel_errs.append(c["rel_err"])
                    ds.append(c["d_estimate"])
                    ratios.append(c["ratio"])
        mean_rel = float(np.mean(rel_errs)) if rel_errs else float("nan")
        cell_match[alpha] = (mean_rel < SCS_MATCH_TOL)
        cell_d[alpha] = float(np.mean(ds)) if ds else float("nan")
        cell_ratio[alpha] = float(np.mean(ratios)) if ratios else float("nan")

    n_match = sum(1 for a in ALPHA_GRID if cell_match[a])
    summary = " ".join(
        f"a{a:.2f}:d{cell_d[a]:.2f}:r{cell_ratio[a]:.2f}:{'M' if cell_match[a] else 'x'}"
        for a in ALPHA_GRID
    )
    summary = f"n_match={n_match}/{len(ALPHA_GRID)} tau_target={TAU_TARGET} cells: {summary}"

    if n_match >= HP_MATCH_CELLS:
        return ("HARD_PASS",
                f"HARD_PASS: SCS formula matches in {n_match}/{len(ALPHA_GRID)} d-cells "
                f">= {HP_MATCH_CELLS}. SCS validated across d range at substrate actual tau. {summary}")
    if n_match <= HF_MATCH_CELLS:
        return ("HARD_FAIL",
                f"HARD_FAIL: SCS formula matches in only {n_match}/{len(ALPHA_GRID)} d-cells "
                f"<= {HF_MATCH_CELLS}. {summary}")
    return ("MIDDLE_BAND",
            f"MIDDLE_BAND: SCS formula matches in {n_match}/{len(ALPHA_GRID)} d-cells. {summary}")


def _prot018_startup_check(n_actual: int) -> None:
    if RUN_MODE == "smoke":
        return
    if n_actual != _N_SUFFIX:
        raise RuntimeError(
            f"PROT-018 VIOLATION: anchor '{ANCHOR_NAME}' binds N={_N_SUFFIX} "
            f"but running at N={n_actual}.")


print(f"[config] anchor={ANCHOR_NAME} N={N} n_active={N_ACTIVE} mode={RUN_MODE} "
      f"tau_target={TAU_TARGET}", flush=True)
print(f"[config] alpha_grid={ALPHA_GRID} seeds={SEEDS}", flush=True)
_prot018_startup_check(N_ACTIVE if RUN_MODE == "smoke" else N)

out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N, "run_mode": RUN_MODE, "tau_target": TAU_TARGET, "alpha_grid": ALPHA_GRID}
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
    "N": N, "alpha_grid": ALPHA_GRID, "tau_target": TAU_TARGET, "run_mode": RUN_MODE,
    "n_seeds": len(SEEDS), "n_cells_total": len(ALPHA_GRID) * len(SEEDS),
    "elapsed_s": elapsed_total,
    "summary": verdict_msg,
    "per_seed": [
        {"seed": r.get("seed"), "elapsed_s": r.get("elapsed_s"), "cells": r.get("cells", [])}
        for r in all_results
    ],
}
metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
