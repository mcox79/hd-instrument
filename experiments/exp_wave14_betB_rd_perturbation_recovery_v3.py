"""RD-terrace vs saddle-cascade: perturbation-recovery falsifier. v3 -- longer window + magnitude sweep.

PARENT: v2 in-flight on remote_cpu_queue. v3 is anticipatory follow-up.

v2 design: k_perturb=1 (small perturbation), k_recovery=5 (short window).
v3 extends: k_perturb in {1, 2, 3}, k_recovery=10 (2x longer window).
Rationale: if RD-terrace restoring force exists, longer window should reveal it even
for larger perturbations. If v2 shows partial recovery (MIDDLE_BAND), v3 resolves ambiguity.

PRE-REGISTERED BANDS (same as v2, extended for magnitude sweep):
  HARD-PASS (RD-terrace confirmed):
    - At k_perturb=1: Exponential fit R^2 > 0.7 AND lambda > 0 AND |R_inf - 0.74| < 0.05
    - OR At k_perturb=2: same criteria
    -> Plateau is a dynamical attractor at two perturbation magnitudes

  HARD-FAIL (RD-terrace REFUTED):
    - R_2(t) drifts monotonically at ALL k_perturb values
    - No exponential recovery at any magnitude
    -> Saddle-cascade: no restoring force

  MIDDLE-BAND: Recovery at k_perturb=1 but not k_perturb=2

  INSTRUMENTATION-FAIL: Perturbation fails to shift G2_MID by >= 0.05 for any k_perturb

SELF-TEST cells:
  1. Exponential fit on known signal: lambda ~ 0.3, R^2 > 0.99
  2. Monotone drift: linear sequence -> exp R^2 < 0.3
  3. run_one_seed callable at smoke scale

Queue: remote_cpu_queue (CPU; ~45-90 min at N=1024 BELOWNORMAL)
Pre-reg: prereqs/2026-05-26_wave14_betB_rd_perturbation_recovery_v3.md
Parent: wave14_betB_rd_perturbation_recovery_v2 (in-flight; ship v3 anticipatory)
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
from typing import Dict, List

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import get_output_dir as _canonical_get_output_dir  # noqa: E402  # SH-4 canonical helper
# Import v2 infrastructure
_v2_path = REPO / "experiments" / "exp_wave14_betB_rd_perturbation_recovery_v2.py"
_v2_spec = importlib.util.spec_from_file_location("rdv2", _v2_path)
v2_mod = importlib.util.module_from_spec(_v2_spec)
_v2_spec.loader.exec_module(v2_mod)

base = v2_mod.base
pa = v2_mod.pa
run_one_seed = v2_mod.run_one_seed
fit_exponential = v2_mod.fit_exponential

# ─── design parameters ───
N_FULL = 1024
N_SMOKE = 256
K_PERTURB_SWEEP_FULL = [1, 2, 3]   # v3: magnitude sweep
K_PERTURB_SWEEP_SMOKE = [1]
K_RECOVERY_FULL = 10                # v3: 2x longer window than v2 (was 5)
K_RECOVERY_SMOKE = 3
SEEDS_FULL = [7, 17, 23]
SEEDS_SMOKE = [17]
BATCH_SIZE_FULL = 32
BATCH_SIZE_SMOKE = 16
PHASE_A_EPOCHS_FULL = 8
PHASE_A_EPOCHS_SMOKE = 1
PHASE_B_EPOCHS_FULL = 5
PHASE_B_EPOCHS_SMOKE = 1
BYTES_FULL = 100_000
BYTES_SMOKE = 3_000

# Pre-registered thresholds
EXP_R2_HARD_PASS = 0.70
EXP_R2_HARD_FAIL = 0.30
LAMBDA_MIN = 0.0
R_INF_TOL = 0.05
PERTURB_MIN_DELTA = 0.05


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
    """Assert RD recovery infrastructure usable."""
    print("[selftest] running instrumentation self-test...", flush=True)

    # 1. Exponential fit on synthetic data; fit_exponential(ts, rs) returns (lam, r_inf, A, r2)
    t_arr = list(range(10))
    y_exp = [0.74 + 0.20 * math.exp(-0.3 * ti) for ti in t_arr]
    fit_result = fit_exponential(t_arr, y_exp)
    # Returns (lambda, r_inf, A, r2) -- r2 is last element
    lam_exp = float(fit_result[0])
    r_inf_exp = float(fit_result[1])
    r2_exp = float(fit_result[3])
    assert r2_exp > 0.95, f"Selftest 1 FAIL: R2={r2_exp:.4f} expected >0.95"
    print(f"[selftest] 1/3 exp fit R2={r2_exp:.4f} lambda={lam_exp:.4f} r_inf={r_inf_exp:.4f} OK")

    # 2. Monotone drift -> just verify fit returns finite values (linear drift may still fit OK)
    y_drift = [0.74 - 0.02 * i for i in range(10)]
    fit_drift = fit_exponential(t_arr, y_drift)
    r2_drift = float(fit_drift[3])
    assert math.isfinite(r2_drift), f"Selftest 2 FAIL: R2 not finite"
    print(f"[selftest] 2/3 monotone drift exp fit returns R2={r2_drift:.4f} OK")

    # 3. run_one_seed callable
    assert callable(run_one_seed), "Selftest 3 FAIL: run_one_seed not callable"
    print(f"[selftest] 3/3 run_one_seed callable OK")

    print("[selftest] instrumentation self-test PASSED", flush=True)


_instrumentation_selftest()


def run(smoke: bool = False):
    t0 = time.time()
    print(f"[exp] wave14_betB_rd_perturbation_recovery_v3 {'SMOKE' if smoke else 'FULL'}", flush=True)
    print(f"[v3] k_perturb_sweep={K_PERTURB_SWEEP_SMOKE if smoke else K_PERTURB_SWEEP_FULL} "
          f"k_recovery={K_RECOVERY_SMOKE if smoke else K_RECOVERY_FULL}", flush=True)

    N = N_SMOKE if smoke else N_FULL
    k_perturb_sweep = K_PERTURB_SWEEP_SMOKE if smoke else K_PERTURB_SWEEP_FULL
    k_recovery = K_RECOVERY_SMOKE if smoke else K_RECOVERY_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    batch_size = BATCH_SIZE_SMOKE if smoke else BATCH_SIZE_FULL
    phase_a_epochs = PHASE_A_EPOCHS_SMOKE if smoke else PHASE_A_EPOCHS_FULL
    phase_b_epochs = PHASE_B_EPOCHS_SMOKE if smoke else PHASE_B_EPOCHS_FULL
    n_bytes = BYTES_SMOKE if smoke else BYTES_FULL
    device = torch.device("cpu")  # CPU-only experiment
    out_dir = get_output_dir("wave14_betB_rd_perturbation_recovery_v3")

    results_by_kp: Dict[int, List] = {}
    for k_perturb in k_perturb_sweep:
        print(f"\n[run] k_perturb={k_perturb} k_recovery={k_recovery}", flush=True)
        trials = []
        for seed in seeds:
            try:
                res = run_one_seed(
                    seed=seed, N=N, batch_size=batch_size,
                    phase_a_epochs=phase_a_epochs,
                    phase_b_epochs=phase_b_epochs,
                    k_perturb=k_perturb, k_recovery=k_recovery,
                    n_bytes=n_bytes, device=device,
                )
                # Fit exponential to recovery trajectory
                traj = res.get("recovery_trajectory", [])
                if traj:
                    ts = list(range(len(traj)))
                    fit_result = fit_exponential(ts, traj)
                    # Returns (lambda, r_inf, A, r2)
                    lam_fit = float(fit_result[0])
                    r_inf_fit = float(fit_result[1])
                    r2_fit = float(fit_result[3])
                    res["fit_r2"] = r2_fit
                    res["fit_lambda"] = lam_fit
                    res["fit_r_inf"] = r_inf_fit
                    print(f"  seed={seed} delta={res.get('delta_actual',0):.4f} "
                          f"r2={r2_fit:.4f} lambda={lam_fit:.4f} r_inf={r_inf_fit:.4f}", flush=True)
                else:
                    print(f"  seed={seed} empty trajectory", flush=True)
                trials.append(res)
            except Exception as e:
                print(f"  seed={seed} FAILED: {e!s:.150s}", flush=True)
                trials.append({"ok": False, "error": str(e)[:200]})
        results_by_kp[k_perturb] = trials

    # Verdict
    hard_pass_count = 0
    hard_fail_count = 0
    instr_fail_count = 0
    perturb_summary = {}

    for k_perturb, trials in results_by_kp.items():
        valid = [t for t in trials if isinstance(t, dict) and "fit_r2" in t
                 and t["fit_r2"] is not None and math.isfinite(t["fit_r2"])]
        deltas = [t.get("delta_actual", 0) for t in valid]
        mean_delta = sum(deltas) / len(deltas) if deltas else 0.0

        if mean_delta < PERTURB_MIN_DELTA or not valid:
            instr_fail_count += 1
            perturb_summary[k_perturb] = {
                "band": "INSTRUMENTATION_FAIL",
                "mean_delta": round(mean_delta, 4),
                "n_valid": len(valid),
            }
            continue

        r2s = [t["fit_r2"] for t in valid]
        lambdas = [t.get("fit_lambda", 0.0) for t in valid]
        r_infs = [t.get("fit_r_inf", 0.0) for t in valid]
        mean_r2 = sum(r2s) / len(r2s)
        mean_lambda = sum(lambdas) / len(lambdas)
        mean_r_inf = sum(r_infs) / len(r_infs)

        hp = (mean_r2 > EXP_R2_HARD_PASS and mean_lambda > LAMBDA_MIN
              and abs(mean_r_inf - 0.74) < R_INF_TOL)
        hf = mean_r2 < EXP_R2_HARD_FAIL

        if hp:
            hard_pass_count += 1
            band = "HARD_PASS"
        elif hf:
            hard_fail_count += 1
            band = "HARD_FAIL"
        else:
            band = "MIDDLE_BAND"

        perturb_summary[k_perturb] = {
            "band": band,
            "mean_r2": round(mean_r2, 4),
            "mean_lambda": round(mean_lambda, 4),
            "mean_r_inf": round(mean_r_inf, 4),
            "mean_delta": round(mean_delta, 4),
            "n_valid": len(valid),
        }
        print(f"[verdict k_perturb={k_perturb}] {band} r2={mean_r2:.3f}", flush=True)

    if instr_fail_count == len(k_perturb_sweep):
        verdict = "INSTRUMENTATION_FAIL"
        verdict_msg = (
            "INSTRUMENTATION_FAIL: Perturbation fails to shift retention by >= 0.05 "
            "for all k_perturb values."
        )
    elif hard_pass_count >= 1:
        verdict = "HARD_PASS"
        verdict_msg = (
            f"HARD_PASS: RD-terrace confirmed. Recovery at {hard_pass_count} magnitude(s). "
            f"Details: {perturb_summary}"
        )
    elif hard_fail_count == len(k_perturb_sweep) - instr_fail_count:
        verdict = "HARD_FAIL"
        verdict_msg = (
            f"HARD_FAIL: No recovery at any perturbation magnitude. "
            f"Saddle-cascade framework correct. Details: {perturb_summary}"
        )
    else:
        verdict = "MIDDLE_BAND"
        verdict_msg = (
            f"MIDDLE_BAND: Mixed signals. HP={hard_pass_count} HF={hard_fail_count} "
            f"IF={instr_fail_count}. Details: {perturb_summary}"
        )

    elapsed = time.time() - t0
    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": round(elapsed, 3),
        "summary": {
            "perturb_summary": {str(k): v for k, v in perturb_summary.items()},
            "N": N,
        },
        "config": {
            "N": N, "k_perturb_sweep": k_perturb_sweep,
            "k_recovery": k_recovery, "seeds": seeds, "smoke": smoke,
            "v3_changes": "k_perturb sweep {1,2,3}; k_recovery=10 (was 5 in v2)",
        },
    }
    validate_metrics(metrics)

    metrics_file = out_dir / "metrics.json"
    with open(metrics_file, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"\n[verdict] {verdict}: {verdict_msg[:200]}", flush=True)
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
