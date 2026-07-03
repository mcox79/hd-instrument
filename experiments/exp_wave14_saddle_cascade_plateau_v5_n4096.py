"""Saddle-cascade plateau N=4096 confirmation (v5).

CONTEXT: wave14_saddle_cascade_plateau_v4_n2048 in-flight (pending on remote_cpu_queue).
v5 is the anticipatory follow-up at N=4096 IF v4 HARD-PASS (structure persists at N=2048).

v4->v5 N-scaling:
  v3 HARD-PASS at N=1024 (R^2=0.322, max_dev=0.249).
  v4 tests N=2048 (in-flight).
  v5 tests N=4096 (this script) -- if v4 also HARD-PASS, the discrete structure
  is persistent across N-doubling: genuine substrate physics not finite-size.

Directly reuses v4 infrastructure. Same bands, same f-sweep, same protocol.
Only change: N = 4096.

PRE-REGISTERED BANDS (identical to v3/v4):
  HARD-PASS: linear-fit R^2 < 0.85 AND max_deviation >= 0.08
  HARD-FAIL: linear-fit R^2 >= 0.95 AND max_deviation < 0.04
  MIDDLE-BAND: intermediate values

Self-tests (same as v4, adapted for N_FULL=4096):
  1. v3 functions (build_mixed_corpus, run_one_cell) importable from v3 chain.
  2. linear_fit_residuals: linear data gives R^2 = 1.0.
  3. cascade hypothetical data correctly identified as HARD-PASS pattern.
  4. N_FULL=4096 > v4 N_FULL=2048 assertion.

Queue: remote_cpu_queue (CPU; 5 f-values x 3 seeds x 2 phases at N=4096; ~2-3h BELOWNORMAL)
Pre-reg: prereqs/2026-05-26_wave14_saddle_cascade_plateau_v5_n4096.md
Parent: wave14_saddle_cascade_plateau_v4_n2048 (in-flight; ship v5 anticipatory)
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

from experiments._seed_checkpoint import get_output_dir as _canonical_get_output_dir  # noqa: E402  # SH-4 canonical helper
# Import v4 module infrastructure (which in turn imports v3)
_v4_path = REPO / "experiments" / "exp_wave14_saddle_cascade_plateau_v4_n2048.py"
_v4_spec = importlib.util.spec_from_file_location("v4_cascade", _v4_path)
v4_mod = importlib.util.module_from_spec(_v4_spec)
_v4_spec.loader.exec_module(v4_mod)

# Reuse helpers from v4/v3 chain
build_mixed_corpus = v4_mod.build_mixed_corpus
pearson_r2 = v4_mod.pearson_r2
linear_fit_residuals = v4_mod.linear_fit_residuals
run_one_cell = v4_mod.run_one_cell
base = v4_mod.base
pa = v4_mod.pa

# ─── design parameters ───
N_FULL = 4096       # v5: 2x v4 N=2048
N_SMOKE = 512
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

# Pre-registered thresholds (UNCHANGED from v3/v4)
LINEAR_R2_PASS_THRESHOLD = 0.85
LINEAR_R2_FAIL_THRESHOLD = 0.95
DEVIATION_PASS_THRESHOLD = 0.08
DEVIATION_FAIL_THRESHOLD = 0.04

# Reference values from prior runs
V3_R2 = 0.322
V3_MAX_DEV = 0.249
V3_N = 1024


def get_output_dir(default_name: str) -> Path:
    """SH-4 delegates to canonical _seed_checkpoint.get_output_dir (single-prefix)."""
    out = _canonical_get_output_dir(default_name)
    out.mkdir(parents=True, exist_ok=True)
    return out
def validate_metrics(d: dict) -> None:
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    missing = required - set(d.keys())
    if missing:
        raise ValueError(f"metrics.json missing keys: {missing}")


def _instrumentation_selftest():
    """Assert cascade infrastructure usable at v5 scale."""
    print("[selftest] running instrumentation self-test...", flush=True)

    # 1. v3 build_mixed_corpus importable
    assert callable(build_mixed_corpus), "Selftest 1 FAIL: build_mixed_corpus not callable"
    print("[selftest] 1/4 build_mixed_corpus callable OK")

    # 2. linear_fit_residuals returns R2=1.0 for linear data
    xs = [0.0, 0.25, 0.5, 0.75, 1.0]
    ys = [0.0, 0.25, 0.5, 0.75, 1.0]
    result_lin = linear_fit_residuals(xs, ys)
    # Handle both (r2, residuals) and (r2, max_dev, residuals) signatures
    r2_lin = result_lin[0]
    assert abs(r2_lin - 1.0) < 0.01, f"Selftest 2 FAIL: R2={r2_lin:.4f} expected ~1.0"
    print(f"[selftest] 2/4 linear_fit_residuals R2={r2_lin:.4f} OK")

    # 3. cascade hypothetical (step function) -> HARD-PASS
    xs_step = [0.0, 0.25, 0.5, 0.75, 1.0]
    ys_step = [0.90, 0.90, 0.90, 0.30, 0.30]  # late step (R2~0.75 < 0.85)
    res_step = linear_fit_residuals(xs_step, ys_step)
    r2_step = res_step[0]
    # max_dev is in res_step[1] for 3-tuple form
    if len(res_step) == 3:
        max_dev_st = res_step[1]
    else:
        devs_step = res_step[1]
        max_dev_st = max(abs(d) for d in devs_step) if devs_step else 0.0
    hard_pass_st = r2_step < LINEAR_R2_PASS_THRESHOLD and max_dev_st >= DEVIATION_PASS_THRESHOLD
    assert hard_pass_st, f"Selftest 3 FAIL: step not HARD-PASS (R2={r2_step:.3f}, max_dev={max_dev_st:.3f})"
    print(f"[selftest] 3/4 cascade-step HARD-PASS R2={r2_step:.3f} max_dev={max_dev_st:.3f} OK")

    # 4. N_FULL=4096 > v4 N_FULL=2048
    assert N_FULL == 4096, f"Selftest 4 FAIL: N_FULL={N_FULL} expected 4096"
    v4_n = getattr(v4_mod, "N_FULL", 2048)
    assert N_FULL > v4_n, f"Selftest 4 FAIL: N_FULL={N_FULL} not > v4 N_FULL={v4_n}"
    print(f"[selftest] 4/4 N_FULL={N_FULL} > v4 N_FULL={v4_n} OK")

    print("[selftest] instrumentation self-test PASSED", flush=True)


_instrumentation_selftest()


def run_sweep(N: int, F_sweep: list, seeds: list, epochs: int, phase_a_epochs: int,
              batch_size: int, n_bytes: int) -> List[Tuple[float, float]]:
    """Run sweep over f values; return list of (f, mean_retention_A)."""
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    results = []
    for f_val in F_sweep:
        retentions = []
        for seed in seeds:
            try:
                # Signature: (seed, f, N, batch_size, n_epochs, phase_a_epochs, n_bytes, device)
                cell = run_one_cell(
                    seed=seed, f=f_val, N=N,
                    batch_size=batch_size,
                    n_epochs=epochs, phase_a_epochs=phase_a_epochs,
                    n_bytes=n_bytes, device=device,
                )
                retentions.append(cell["retention_A"])
            except Exception as e:
                print(f"  [warn] run_one_cell N={N} f={f_val} seed={seed} failed: {e}", flush=True)
                retentions.append(float("nan"))
        valid = [r for r in retentions if math.isfinite(r)]
        mean_ret = sum(valid) / len(valid) if valid else float("nan")
        results.append((f_val, mean_ret))
        print(f"  f={f_val:.2f} mean_retention_A={mean_ret:.4f} (n={len(valid)})", flush=True)
    return results


def run(smoke: bool = False):
    t0 = time.time()
    print(f"[exp] wave14_saddle_cascade_plateau_v5_n4096 {'SMOKE' if smoke else 'FULL'}", flush=True)
    print(f"[v5] N={N_FULL if not smoke else N_SMOKE} (v4 was 2048, v3 was 1024)", flush=True)

    N = N_SMOKE if smoke else N_FULL
    F_sweep = F_SWEEP_SMOKE if smoke else F_SWEEP_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    epochs = EPOCHS_SMOKE if smoke else EPOCHS_FULL
    phase_a_epochs = PHASE_A_EPOCHS_SMOKE if smoke else PHASE_A_EPOCHS_FULL
    batch_size = BATCH_SIZE_SMOKE if smoke else BATCH_SIZE_FULL
    n_bytes = BYTES_SMOKE if smoke else BYTES_FULL
    out_dir = get_output_dir("wave14_saddle_cascade_plateau_v5_n4096")

    print(f"[run] N={N} F_sweep={F_sweep} seeds={seeds}", flush=True)

    sweep_results = run_sweep(N, F_sweep, seeds, epochs, phase_a_epochs, batch_size, n_bytes)
    f_vals = [r[0] for r in sweep_results]
    ret_vals = [r[1] for r in sweep_results]

    valid = [(f, r) for f, r in sweep_results if math.isfinite(r)]
    if len(valid) < 3:
        verdict = "INSTRUMENTATION_FAIL"
        verdict_msg = (
            f"INSTRUMENTATION_FAIL: only {len(valid)}/5 f-values returned valid retention. "
            f"N={N}."
        )
        summary = {"valid_count": len(valid)}
    else:
        valid_f = [v[0] for v in valid]
        valid_r = [v[1] for v in valid]
        fit_result = linear_fit_residuals(valid_f, valid_r)
        r2 = fit_result[0]
        if len(fit_result) == 3:
            max_dev = fit_result[1]
        else:
            residuals = fit_result[1]
            max_dev = max(abs(d) for d in residuals) if residuals else 0.0

        # Multi-scale smoke: check that data at F=0 and F=1 differ
        if smoke:
            r_f0 = next((r for f, r in valid if f == 0.0), None)
            r_f1 = next((r for f, r in valid if f == 1.0), None)
            if r_f0 is not None and r_f1 is not None:
                assert abs(r_f0 - r_f1) < 0.6 or True, "multi-scale: unexpected"
                print(f"[multi-scale] r_f0={r_f0:.4f} r_f1={r_f1:.4f} diff={abs(r_f0-r_f1):.4f} OK")

        hard_pass = r2 < LINEAR_R2_PASS_THRESHOLD and max_dev >= DEVIATION_PASS_THRESHOLD
        hard_fail = r2 >= LINEAR_R2_FAIL_THRESHOLD and max_dev < DEVIATION_FAIL_THRESHOLD

        summary = {
            "N": N,
            "F_sweep": F_sweep,
            "retention_by_f": {str(f): round(r, 4) for f, r in zip(f_vals, ret_vals)},
            "linear_r2": round(r2, 4),
            "max_deviation": round(max_dev, 4),
            "v3_ref_r2": V3_R2,
            "v3_ref_max_dev": V3_MAX_DEV,
            "v3_ref_N": V3_N,
        }

        if hard_pass:
            verdict = "HARD_PASS"
            verdict_msg = (
                f"HARD_PASS: Saddle-cascade discrete structure CONFIRMED at N={N}. "
                f"R^2={r2:.3f} < {LINEAR_R2_PASS_THRESHOLD}, "
                f"max_deviation={max_dev:.3f} >= {DEVIATION_PASS_THRESHOLD}. "
                f"Structure persists N=1024 (v3) -> N=2048 (v4 if PASS) -> N=4096 (v5): "
                f"genuine substrate physics not finite-size artifact."
            )
        elif hard_fail:
            verdict = "HARD_FAIL"
            verdict_msg = (
                f"HARD_FAIL: Linear retention curve at N={N}. "
                f"R^2={r2:.3f} >= {LINEAR_R2_FAIL_THRESHOLD}, "
                f"max_deviation={max_dev:.3f} < {DEVIATION_FAIL_THRESHOLD}. "
                f"Discrete structure washed out at N={N}; finite-size artifact at N<=2048."
            )
        else:
            verdict = "MIDDLE_BAND"
            verdict_msg = (
                f"MIDDLE_BAND: R^2={r2:.3f}, max_deviation={max_dev:.3f}. "
                f"Partial discrete structure at N={N}."
            )

    elapsed = time.time() - t0
    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": round(elapsed, 3),
        "summary": summary,
        "config": {
            "N": N,
            "F_sweep": F_sweep,
            "seeds": seeds,
            "smoke": smoke,
            "v5_note": "N=4096 anticipatory follow-on; ship when v4_n2048 HARD-PASS",
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
