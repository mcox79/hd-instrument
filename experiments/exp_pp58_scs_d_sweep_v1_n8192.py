"""
pp58_scs_d_sweep_v1_n8192 -- PP-58 SCS spike threshold: d-sweep d=4..14 at N=8192.

CONTEXT (v375 cycle 43 rescue R2 for pp58_scs_formula_test HARD_FAIL):
  pp58_scs_formula_test_d8_tau005_v1_n8192: d_estimate=1.487 < 1.5 (SCS spike violated).
  SCS framework predicts gamma via spike structure requiring d > 1.5.
  At alpha=0.05 N=8192 M=410, the empirical d_estimate comes out below threshold.
  R2: sweep alpha to find where d_estimate crosses 1.5 (spike emerges).
  alpha grid: 0.01, 0.02, 0.03, 0.05, 0.075, 0.10, 0.12, 0.14 (below alpha_c=0.138).
  For each alpha: measure d_estimate, tau, gamma_scs, gamma_emp.

SCIENTIFIC QUESTION:
  At what alpha does the spectral spike (d_estimate >= 1.5) emerge?
  Is there a clear threshold in alpha-space separating sub-spike from spike regime?
  Does the SCS formula become predictive (ratio near 1.0) in the spike regime?

PRE-REGISTERED BANDS (d-sweep):
  HARD-PASS: spike_alpha found (at least 1 alpha with d_estimate >= 1.5 AND
             SCS ratio in [0.7, 1.3]) AND below alpha_c=0.138.
  MIDDLE:    d_estimate monotone increasing vs alpha (even if not crossing 1.5);
             OR spike at alpha > 0.10 only.
  HARD-FAIL: d_estimate flat vs alpha (no monotone trend); SCS formula consistently
             off by >2x in ALL alpha cells.

FORMULA SELF-TESTS (PROT-022):
  1. SCS formula: gamma(d=2.0, tau=0) = 2.0. [EXPECTED: 2.0]
  2. SCS formula: gamma(d=1.5, tau=0) = 1.5. [EXPECTED: 1.5]
  3. alpha_grid all < alpha_c=0.138. [EXPECTED: True for all]
  4. M = int(alpha * N) for each alpha; M >= 1 for all. [EXPECTED: all >= 1]

PROT-018: anchor has _n8192; N MUST = 8192.
PROT-021: seed checkpoints keyed with run_mode + seed.
QUEUE: remote_cpu_queue (CPU; pure numpy; alpha sweep ~20-30 min total).
TIMEOUT ESTIMATE: pp58_scs_formula_test ran 566s for spectral_gap probe.
  Estimate ~400s for this sweep. ceil(1.5 * 400) = 600s. Use PROT-019 floor: 21600s.

ASCII-only stdout per feedback_ascii_only_in_scripts.
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

ANCHOR_NAME = "pp58_scs_d_sweep_v1_n8192"

_N_SUFFIX = 8192
N = 8192
assert N == _N_SUFFIX, f"PROT-018: anchor _n{_N_SUFFIX} but N={N}"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

ALPHA_C = 0.138

# PROT-022 formula self-tests at module scope
def _scs_gamma(d: float, tau: float) -> float:
    if (1.0 + tau) < 1e-12:
        return float("nan")
    return (d + tau / max(d, 1e-10)) / (1.0 + tau)

_g_d2 = _scs_gamma(2.0, 0.0)
print(f"[selftest-formula] gamma(d=2,tau=0)={_g_d2:.4f} expected 2.0000", flush=True)
assert abs(_g_d2 - 2.0) < 0.001, f"SCS formula selftest d=2: {_g_d2}"

_g_d15 = _scs_gamma(1.5, 0.0)
print(f"[selftest-formula] gamma(d=1.5,tau=0)={_g_d15:.4f} expected 1.5000", flush=True)
assert abs(_g_d15 - 1.5) < 0.001, f"SCS formula selftest d=1.5: {_g_d15}"

if RUN_MODE == "smoke":
    ALPHA_GRID = [0.01, 0.05, 0.10]
    SEEDS = [7, 17]
    N_ACTIVE = 512
    N_PROBES = 100
else:
    ALPHA_GRID = [0.01, 0.02, 0.03, 0.05, 0.075, 0.10, 0.12, 0.13]
    SEEDS = [7, 17, 23]
    N_ACTIVE = N
    N_PROBES = 300

for _a in ALPHA_GRID:
    assert _a < ALPHA_C, f"alpha_grid entry {_a} >= alpha_c={ALPHA_C}"
    assert int(_a * N_ACTIVE) >= 1, f"alpha={_a} gives M=0 at N={N_ACTIVE}"
print(f"[selftest-formula] alpha_grid OK: {ALPHA_GRID}", flush=True)

# Pre-registered thresholds
SPIKE_THRESHOLD = 1.5       # d_estimate must exceed this for spike
HP_RATIO_LO = 0.7
HP_RATIO_HI = 1.3
HF_RATIO_MAX = 2.0
HF_RATIO_MIN = 0.5


def measure_tau(xi: np.ndarray, n: int) -> float:
    W = (xi.T @ xi) / n
    W_asym = (W - W.T) / 2.0
    norm_asym = float(np.linalg.norm(W_asym, 'fro'))
    norm_total = max(float(np.linalg.norm(W, 'fro')), 1e-10)
    return norm_asym / norm_total


def measure_d_estimate(xi: np.ndarray, n: int) -> float:
    sv = np.linalg.svd(xi, compute_uv=False)
    ev = sv ** 2 / n
    if len(ev) < 2:
        return 1.0
    return float(ev[0]) / max(float(np.mean(ev[1:])), 1e-10)


def measure_kappa3(xi: np.ndarray, n: int, rng: np.random.Generator, n_probes: int) -> float:
    V = rng.choice([-1.0, 1.0], size=(n, n_probes))
    def w_op(v):
        return (xi.T @ (xi @ v)) / n
    V3 = w_op(w_op(w_op(V)))
    return float(np.mean((V * V3).sum(axis=0) / n))


def measure_gamma_emp(xi: np.ndarray, n: int, rng: np.random.Generator, n_probes: int) -> float:
    delta_M = max(1, int(0.01 * n))
    xi_extra = rng.choice([-1.0, 1.0], size=(delta_M, n)).astype(np.float32)
    xi_aug = np.concatenate([xi, xi_extra], axis=0)
    k3_base = measure_kappa3(xi, n, rng, n_probes)
    k3_aug = measure_kappa3(xi_aug, n, rng, n_probes)
    if abs(k3_base) < 1e-10:
        return 0.0
    return abs(k3_aug) / abs(k3_base)


def _instrumentation_selftest():
    n_test = 128
    M_test = max(1, int(0.05 * n_test))
    rng = np.random.default_rng(42)
    xi_test = rng.choice([-1.0, 1.0], size=(M_test, n_test)).astype(np.float32)
    tau_t = measure_tau(xi_test, n_test)
    d_t = measure_d_estimate(xi_test, n_test)
    rng2 = np.random.default_rng(99)
    g_emp = measure_gamma_emp(xi_test, n_test, rng2, n_probes=50)
    assert not np.isnan(tau_t) and not np.isnan(d_t), "selftest: NaN in tau or d"
    assert d_t > 0, f"d_estimate non-positive: {d_t}"
    assert g_emp >= 0, f"gamma_emp negative: {g_emp}"
    print(f"[selftest] PASS: tau={tau_t:.4f} d={d_t:.3f} gamma_emp={g_emp:.3f}", flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int, n_dim: int) -> Dict:
    rng = np.random.default_rng(seed)
    t0 = time.time()
    cells = []
    for alpha in ALPHA_GRID:
        M = int(alpha * n_dim)
        xi = rng.choice([-1.0, 1.0], size=(M, n_dim)).astype(np.float32)
        tau = measure_tau(xi, n_dim)
        d_est = measure_d_estimate(xi, n_dim)
        g_scs = _scs_gamma(d_est, tau)
        rng2 = np.random.default_rng(seed + int(alpha * 10000))
        g_emp = measure_gamma_emp(xi, n_dim, rng2, N_PROBES)
        ratio = g_scs / max(g_emp, 1e-6)
        spike = d_est >= SPIKE_THRESHOLD
        print(
            f"  [seed={seed} alpha={alpha:.3f} M={M}] d={d_est:.3f} tau={tau:.4f} "
            f"g_scs={g_scs:.3f} g_emp={g_emp:.3f} ratio={ratio:.3f} spike={spike}",
            flush=True,
        )
        cells.append({
            "alpha": alpha, "M": M,
            "d_estimate": float(d_est), "tau_estimate": float(tau),
            "gamma_scs": float(g_scs), "gamma_emp": float(g_emp),
            "ratio": float(ratio), "spike": bool(spike),
        })
    elapsed = time.time() - t0
    print(f"  [seed={seed}] elapsed={elapsed:.1f}s", flush=True)
    return {"seed": seed, "N": n_dim, "run_mode": RUN_MODE, "cells": cells, "elapsed_s": float(elapsed)}


def compute_verdict(results: List[Dict]) -> tuple:
    if not results:
        return ("HARD_FAIL", "No valid results.")

    # Aggregate per alpha across seeds
    alpha_summary = {}
    for alpha in ALPHA_GRID:
        d_vals = []
        ratio_vals = []
        spike_count = 0
        for r in results:
            for c in r.get("cells", []):
                if abs(c["alpha"] - alpha) < 1e-6:
                    d_vals.append(c["d_estimate"])
                    ratio_vals.append(c["ratio"])
                    if c["spike"]:
                        spike_count += 1
        alpha_summary[alpha] = {
            "mean_d": float(np.mean(d_vals)) if d_vals else float("nan"),
            "mean_ratio": float(np.mean(ratio_vals)) if ratio_vals else float("nan"),
            "spike_count": spike_count,
            "n_seeds": len(results),
        }

    # Find spike alphas
    spike_alphas = [a for a, s in alpha_summary.items() if s["spike_count"] > 0]
    spike_validated = [
        a for a in spike_alphas
        if HP_RATIO_LO <= alpha_summary[a]["mean_ratio"] <= HP_RATIO_HI
    ]

    # Check monotone d vs alpha
    mean_ds = [alpha_summary[a]["mean_d"] for a in sorted(ALPHA_GRID)]
    monotone = all(mean_ds[i] <= mean_ds[i+1] + 0.05 for i in range(len(mean_ds)-1))

    summary_str = " ".join(
        f"a{a:.2f}:d{alpha_summary[a]['mean_d']:.2f}:r{alpha_summary[a]['mean_ratio']:.2f}"
        for a in sorted(ALPHA_GRID)
    )
    summary = (f"spike_alphas={spike_alphas} spike_validated={spike_validated} "
               f"monotone_d={monotone} cells: {summary_str}")

    if spike_validated:
        return ("HARD_PASS",
                f"HARD_PASS: spike found at alpha={spike_validated[0]:.3f} with "
                f"d>={SPIKE_THRESHOLD} AND SCS ratio in [{HP_RATIO_LO},{HP_RATIO_HI}]. {summary}")
    elif monotone or spike_alphas:
        return ("MIDDLE_BAND",
                f"MIDDLE_BAND: d monotone vs alpha={monotone}; spike_alphas={spike_alphas} "
                f"but ratio outside [{HP_RATIO_LO},{HP_RATIO_HI}]. {summary}")
    else:
        # Check HF: all ratios consistently bad
        all_ratios = [
            c["ratio"]
            for r in results
            for c in r.get("cells", [])
        ]
        if all_ratios and (float(np.mean(all_ratios)) > HF_RATIO_MAX or float(np.mean(all_ratios)) < HF_RATIO_MIN):
            return ("HARD_FAIL",
                    f"HARD_FAIL: d flat vs alpha AND SCS formula off by >2x across all cells. {summary}")
        return ("HARD_FAIL",
                f"HARD_FAIL: no spike found; d not monotone vs alpha. {summary}")


def _prot018_startup_check(n_actual: int) -> None:
    if RUN_MODE == "smoke":
        return
    if n_actual != _N_SUFFIX:
        raise RuntimeError(
            f"PROT-018 VIOLATION: anchor '{ANCHOR_NAME}' binds N={_N_SUFFIX} "
            f"but running at N={n_actual}.")


print(f"[config] anchor={ANCHOR_NAME} N={N} n_active={N_ACTIVE} mode={RUN_MODE}", flush=True)
print(f"[config] alpha_grid={ALPHA_GRID} seeds={SEEDS}", flush=True)
_prot018_startup_check(N_ACTIVE if RUN_MODE == "smoke" else N)

out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N, "run_mode": RUN_MODE, "alpha_grid": ALPHA_GRID}
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
    "N": N, "alpha_grid": ALPHA_GRID, "run_mode": RUN_MODE,
    "n_seeds": len(SEEDS), "n_cells_total": len(ALPHA_GRID) * len(SEEDS),
    "elapsed_s": elapsed_total,
    "summary": verdict_msg,
    "per_seed": [
        {"seed": r.get("seed"), "elapsed_s": r.get("elapsed_s"),
         "cells": r.get("cells", [])}
        for r in all_results
    ],
}
metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
