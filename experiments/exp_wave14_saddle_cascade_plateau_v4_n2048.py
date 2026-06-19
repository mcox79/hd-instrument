"""Saddle-cascade plateau N=2048 confirmation (v4).

CONTEXT: wave14_saddle_cascade_plateau_v3 HARD-PASS at N=1024 (R^2=0.322 < 0.85,
max_deviation=0.249 >= 0.08). Discrete step structure confirmed at N=1024.

v4 tests whether the discrete structure PERSISTS at N=2048. If the saddle-cascade
framework reflects true substrate physics (not finite-size effects), the result
should replicate: non-smooth retention(f) curve with R^2 < 0.85.

Directly reuses v3 infrastructure. Same bands, same f-sweep, same protocol.
Only change: N = 2048 (2x larger than v3).

PRE-REGISTERED BANDS (identical to v3):
  HARD-PASS: linear-fit R^2 < 0.85 AND max_deviation >= 0.08
  HARD-FAIL: linear-fit R^2 >= 0.95 AND max_deviation < 0.04
  MIDDLE-BAND: intermediate values

Self-tests:
  1. v3 functions (build_mixed_corpus, run_one_cell) importable
  2. linear_fit_residuals: linear data gives R^2 = 1.0
  3. cascade hypothetical correctly identified as HARD-PASS pattern
  4. N_FULL=2048 > v3 N_FULL=1024

Queue: remote_cpu_queue (CPU; 5 f-values x 3 seeds x 2 phases at N=2048; ~90-120 min)
Pre-reg: prereqs/2026-05-26_wave14_saddle_cascade_plateau_v4_n2048.md
Parent: wave14_saddle_cascade_plateau_v3 N=1024 HARD-PASS
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import argparse
import importlib.util
import json
import math
import os
import time
from pathlib import Path
from typing import List, Tuple

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# Import v3 module infrastructure
_v3_path = REPO / "experiments" / "exp_wave14_saddle_cascade_plateau_v3.py"
_v3_spec = importlib.util.spec_from_file_location("v3_cascade", _v3_path)
v3_mod = importlib.util.module_from_spec(_v3_spec)
_v3_spec.loader.exec_module(v3_mod)

# Reuse helpers from v3
build_mixed_corpus = v3_mod.build_mixed_corpus
pearson_r2 = v3_mod.pearson_r2
linear_fit_residuals = v3_mod.linear_fit_residuals
run_one_cell = v3_mod.run_one_cell  # returns dict with retention_A key
base = v3_mod.base
pa = v3_mod.pa

# ─── design parameters ───
N_FULL = 2048       # 2x v3 N=1024
N_SMOKE = 512       # same as v3 smoke
F_SWEEP_FULL = [0.0, 0.25, 0.5, 0.75, 1.0]
F_SWEEP_SMOKE = [0.0, 0.5, 1.0]
SEEDS_FULL = [7, 17, 23]
SEEDS_SMOKE = [17]
BATCH_SIZE_FULL = 32
BATCH_SIZE_SMOKE = 16
EPOCHS_FULL = 5
EPOCHS_SMOKE = 1
PHASE_A_EPOCHS_FULL = 8
PHASE_A_EPOCHS_SMOKE = 1
BYTES_FULL = 200_000
BYTES_SMOKE = 4_000

# Pre-registered thresholds (UNCHANGED from v3)
LINEAR_R2_PASS_THRESHOLD = 0.85
LINEAR_R2_FAIL_THRESHOLD = 0.95
DEVIATION_PASS_THRESHOLD = 0.08
DEVIATION_FAIL_THRESHOLD = 0.04

# v3 reference (for comparison annotation)
V3_R2 = 0.322
V3_MAX_DEV = 0.249
V3_N = 1024


def get_output_dir(default_name: str) -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d: dict) -> None:
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    missing = required - set(d.keys())
    if missing:
        raise ValueError(f"metrics missing: {missing}")


def _instrumentation_selftest():
    """Assert all claimed metrics non-null at small scale."""
    print("[selftest] running instrumentation self-test...", flush=True)

    # 1. v3 helpers importable
    assert callable(build_mixed_corpus), "Selftest 1 FAIL: build_mixed_corpus not callable"
    assert callable(run_one_cell), "Selftest 1 FAIL: run_one_cell not callable"
    print("[selftest] 1/4 v3 helpers importable OK")

    # 2. linear_fit_residuals on perfect linear data: R^2 = 1.0
    xs = [0.0, 0.25, 0.5, 0.75, 1.0]
    ys = [0.60, 0.67, 0.74, 0.81, 0.88]  # perfect linear
    r2, max_dev, _ = linear_fit_residuals(xs, ys)
    assert math.isfinite(r2) and abs(r2 - 1.0) < 0.01, f"Selftest 2 FAIL: r2={r2}"
    print(f"[selftest] 2/4 linear_fit_residuals perfect data r2={r2:.4f} OK")

    # 3. Cascade hypothetical correctly identified as HARD-PASS
    ys_cascade = [0.60, 0.62, 0.94, 0.94, 0.94]
    r2_c, dev_c, _ = linear_fit_residuals(xs, ys_cascade)
    is_hardpass = (r2_c < LINEAR_R2_PASS_THRESHOLD and dev_c >= DEVIATION_PASS_THRESHOLD)
    assert is_hardpass, f"Selftest 3 FAIL: cascade not HARD-PASS: r2={r2_c:.3f} dev={dev_c:.3f}"
    print(f"[selftest] 3/4 cascade hypothetical HARD-PASS r2={r2_c:.3f} dev={dev_c:.3f} OK")

    # 4. N_FULL > v3 N_FULL
    assert N_FULL > V3_N, f"Selftest 4 FAIL: N_FULL={N_FULL} <= V3_N={V3_N}"
    print(f"[selftest] 4/4 N_FULL={N_FULL} > v3 N={V3_N} OK")

    print("[selftest] instrumentation self-test PASSED", flush=True)


_instrumentation_selftest()


def run(smoke: bool = False):
    t0 = time.time()
    print(f"[exp] wave14_saddle_cascade_plateau_v4_n2048 {'SMOKE' if smoke else 'FULL'}", flush=True)
    print(f"[ref] v3 N={V3_N} HARD-PASS: R^2={V3_R2} max_dev={V3_MAX_DEV}", flush=True)

    N = N_SMOKE if smoke else N_FULL
    f_sweep = F_SWEEP_SMOKE if smoke else F_SWEEP_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    batch_size = BATCH_SIZE_SMOKE if smoke else BATCH_SIZE_FULL
    epochs = EPOCHS_SMOKE if smoke else EPOCHS_FULL
    phase_a_epochs = PHASE_A_EPOCHS_SMOKE if smoke else PHASE_A_EPOCHS_FULL
    n_bytes = BYTES_SMOKE if smoke else BYTES_FULL
    out_dir = get_output_dir("wave14_saddle_cascade_plateau_v4_n2048")

    print(f"[run] N={N} f_sweep={f_sweep} seeds={seeds}", flush=True)

    # results_per_f[f] = list of retention values (one per seed)
    results_per_f: dict = {f: [] for f in f_sweep}

    for seed in seeds:
        for f in f_sweep:
            print(f"\n[run] f={f} seed={seed} N={N}", flush=True)
            try:
                device = torch.device("cpu")
                cell = run_one_cell(
                    seed=seed, f=f, N=N,
                    batch_size=batch_size,
                    n_epochs=epochs,
                    phase_a_epochs=phase_a_epochs,
                    n_bytes=n_bytes,
                    device=device,
                )
                ret = cell["retention_A"]
                results_per_f[f].append(ret)
                print(f"  retention_A={ret:.4f}", flush=True)
            except Exception as e:
                print(f"  FAILED: {e}", flush=True)
                results_per_f[f].append(float("nan"))

    # Compute mean retention per f
    mean_ret = {}
    for f in f_sweep:
        vals = [v for v in results_per_f[f] if math.isfinite(v)]
        mean_ret[f] = sum(vals) / len(vals) if vals else float("nan")
        print(f"  f={f}: mean_ret={mean_ret[f]:.4f} (seeds={vals})", flush=True)

    # Linear fit
    valid_pairs = [(f, mean_ret[f]) for f in f_sweep if math.isfinite(mean_ret[f])]
    if len(valid_pairs) < 3:
        verdict = "INSTRUMENTATION_FAIL"
        verdict_msg = (
            f"INSTRUMENTATION_FAIL: only {len(valid_pairs)} valid f-values. "
            f"Insufficient for linear-fit verdict."
        )
        summary = {"valid_f_count": len(valid_pairs)}
    else:
        fs = [p[0] for p in valid_pairs]
        rets = [p[1] for p in valid_pairs]
        r2, max_dev, residuals = linear_fit_residuals(fs, rets)

        hard_pass = (r2 < LINEAR_R2_PASS_THRESHOLD and max_dev >= DEVIATION_PASS_THRESHOLD)
        hard_fail = (r2 >= LINEAR_R2_FAIL_THRESHOLD and max_dev < DEVIATION_FAIL_THRESHOLD)

        ret_strs = " ".join(f"f={f:.2f}:ret={mean_ret[f]:.4f}" for f in f_sweep)

        if hard_pass:
            verdict = "CASCADE_HARD_PASS"
            verdict_msg = (
                f"Discrete step structure confirmed at N={N}. "
                f"linear-fit R^2={r2:.3f} < {LINEAR_R2_PASS_THRESHOLD}, "
                f"max_deviation={max_dev:.3f} >= {DEVIATION_PASS_THRESHOLD}. "
                f"v3 N=1024 result REPLICATES at N=2048. | {ret_strs}"
            )
        elif hard_fail:
            verdict = "CASCADE_HARD_FAIL"
            verdict_msg = (
                f"Smooth-monotone at N={N}. "
                f"R^2={r2:.3f} >= {LINEAR_R2_FAIL_THRESHOLD}, "
                f"max_dev={max_dev:.3f} < {DEVIATION_FAIL_THRESHOLD}. "
                f"v3 N=1024 result does NOT replicate. | {ret_strs}"
            )
        else:
            verdict = "CASCADE_MIDDLE"
            verdict_msg = (
                f"Intermediate at N={N}. R^2={r2:.3f}, max_dev={max_dev:.3f}. "
                f"| {ret_strs}"
            )

        summary = {
            "N": N,
            "f_sweep": f_sweep,
            "mean_ret_per_f": {str(f): round(mean_ret[f], 4) for f in f_sweep
                               if math.isfinite(mean_ret[f])},
            "linear_fit_r2": round(r2, 4),
            "max_deviation_from_linear": round(max_dev, 4),
            "v3_reference_r2": V3_R2,
            "v3_reference_max_dev": V3_MAX_DEV,
        }

    elapsed = time.time() - t0
    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": round(elapsed, 3),
        "summary": summary,
        "config": {
            "N": N,
            "f_sweep": f_sweep,
            "seeds": seeds,
            "smoke": smoke,
            "v3_N": V3_N,
        },
    }
    validate_metrics(metrics)
    metrics_file = out_dir / "metrics.json"
    with open(metrics_file, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"\n[verdict] {verdict}: {verdict_msg}", flush=True)
    print(f"Metrics saved to {metrics_file}", flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true", dest="self_test")
    args = parser.parse_args()
    if args.self_test:
        sys.exit(0)
    run(smoke=args.smoke)


if __name__ == "__main__":
    main()
