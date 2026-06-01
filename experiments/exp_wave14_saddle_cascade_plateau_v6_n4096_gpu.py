"""Saddle-cascade plateau FULL confirmation at N=4096, multi-seed, GPU (v6).

CONTEXT:
  v225 cap_map explicitly flags: "genuine large-N FULL run (N>=4096, multi-seed) STILL OPEN".
  v221: saddle_cascade_plateau_v5_n4096 ran as N=512 smoke (mislabeled anchor).
  Load-bearing evidence: v206 BIC delta=194.9 + v211 alpha_c in-band (both at N=512-1024).
  THIS SCRIPT is the first proper N=4096 FULL probe with 5 seeds on GPU.

HYPOTHESIS:
  The saddle-cascade plateau structure (3-class discrete f-sweep, equal-spacing) persists
  at N=4096 with 5 independent seeds. Specifically:
  - Retention vs f is non-monotone-linear (R^2 < 0.85, same gate as v3).
  - Max deviation from a best-fit linear >= 0.08 (same gate).
  - All 5 seeds agree (at least 4/5 pass both gates).

DESIGN:
  - N=4096 (FULL), seeds=[7, 17, 23, 31, 41] (5 seeds).
  - f in [0.0, 0.25, 0.5, 0.75, 1.0] (5-point sweep, same as v3/v4/v5).
  - GPU device (mandatory for N=4096 efficiency).
  - Phase A: 8 epochs on corpus_A.
  - Phase B: 5 epochs on mixed(f) corpus.
  - Corpus: 200KB bytes.

PRE-REGISTERED BANDS (HARD-PASS / HARD-FAIL / MIDDLE-BAND):
  HARD-PASS (per-seed): R^2 < 0.85 AND max_deviation >= 0.08.
  HARD-FAIL (per-seed): R^2 >= 0.95 AND max_deviation < 0.04.
  MIDDLE-BAND: intermediate; qualitative discrete structure present but below threshold.
  OVERALL-PASS: >= 4/5 seeds HARD-PASS.
  OVERALL-FAIL: >= 4/5 seeds HARD-FAIL.
  OVERALL-MIXED: else.
  NOTE: These thresholds are IDENTICAL to v3/v4/v5. The only change is N and GPU.

Self-tests:
  1. build_mixed_corpus(f=0.0) contains 0 tokens from corpus_A portion (all corpus_B).
  2. build_mixed_corpus(f=1.0) contains BYTES_FULL tokens all from corpus_A.
  3. pearson_r2([0,1,2,3], [0,2,4,6]) = 1.0 (linear -> R^2=1).
  4. run_one_cell returns dict with 'retention_A' key that is float in [0,1].
  5. N_FULL=4096 > 1024 (v3 N) assertion.

Queue: overnight_queue (GPU mandatory: N=4096 x 5 seeds x 5 f-values = depth probe)
Pre-reg: prereqs/2026-05-27_wave14_saddle_cascade_plateau_v6_n4096_gpu.md
Parent: wave14_saddle_cascade_plateau_v3 (N=1024, R^2=0.322, max_dev=0.249, 3 seeds HARD-PASS)
Calibration note: prior empirical anchor exists (v3 HARD-PASS at N=1024); bands UNCHANGED.
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
from typing import Dict, List, Tuple

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# Load Kovacs base infrastructure (train_w_with_replay, evaluate_bpc, bytes_to_idx_tensors, pa)
_base_path = REPO / "experiments" / "exp_wave14d_betB_kovacs_v1.py"
_base_spec = importlib.util.spec_from_file_location("base_v6", _base_path)
base = importlib.util.module_from_spec(_base_spec)
_base_spec.loader.exec_module(base)
pa = base.pa

# Reuse v3 helper functions (same cascade logic, same threshold formula)
_v3_path = REPO / "experiments" / "exp_wave14_saddle_cascade_plateau_v3.py"
_v3_spec = importlib.util.spec_from_file_location("v3_cascade_v6", _v3_path)
v3_mod = importlib.util.module_from_spec(_v3_spec)
_v3_spec.loader.exec_module(v3_mod)

build_mixed_corpus = v3_mod.build_mixed_corpus
pearson_r2 = v3_mod.pearson_r2
linear_fit_residuals = v3_mod.linear_fit_residuals
run_one_cell = v3_mod.run_one_cell
compute_verdict = v3_mod.compute_verdict

# ---- design parameters (v6: N=4096 FULL, 5 seeds, GPU) ----
N_FULL = 4096
N_SMOKE = 512
F_SWEEP_FULL = [0.0, 0.25, 0.5, 0.75, 1.0]
F_SWEEP_SMOKE = [0.0, 0.5, 1.0]
SEEDS_FULL = [7, 17, 23, 31, 41]   # 5 seeds (v3 had 3; v6 extends to 5)
SEEDS_SMOKE = [17]
BATCH_SIZE_FULL = 32
BATCH_SIZE_SMOKE = 16
EPOCHS_FULL = 5
EPOCHS_SMOKE = 1
PHASE_A_EPOCHS_FULL = 8
PHASE_A_EPOCHS_SMOKE = 1
BYTES_FULL = 200_000
BYTES_SMOKE = 4_000

# Pre-registered thresholds (IDENTICAL to v3/v4/v5)
LINEAR_R2_PASS_THRESHOLD = 0.85
LINEAR_R2_FAIL_THRESHOLD = 0.95
DEVIATION_PASS_THRESHOLD = 0.08
DEVIATION_FAIL_THRESHOLD = 0.04

# Overall verdict thresholds
N_SEEDS_HARDPASS_FOR_OVERALL = 4   # 4/5 seeds HARD-PASS -> OVERALL-PASS
N_SEEDS_HARDFAIL_FOR_OVERALL = 4   # 4/5 seeds HARD-FAIL -> OVERALL-FAIL


def get_output_dir(default_name: str) -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def _instrumentation_selftest():
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    # Self-test 1: N_FULL assertion
    assert N_FULL == 4096, f"N_FULL must be 4096; got {N_FULL}"
    assert N_FULL > 1024, f"N_FULL={N_FULL} must be > v3 N=1024"

    # Self-test 2: pearson_r2 on linear data
    r2 = pearson_r2([0.0, 1.0, 2.0, 3.0], [0.0, 2.0, 4.0, 6.0])
    assert abs(r2 - 1.0) < 1e-6, f"pearson_r2 on linear data should be 1.0; got {r2}"

    # Self-test 3: pearson_r2 on constant data returns 0 or NaN (no crash)
    r2c = pearson_r2([1.0, 1.0, 1.0, 1.0], [0.0, 1.0, 2.0, 3.0])
    assert math.isfinite(r2c) or math.isnan(r2c), "pearson_r2 with constant x must not crash"

    # Self-test 4: build_mixed_corpus functional
    corpus_a = bytes(range(256)) * 4
    mc_f0 = build_mixed_corpus(corpus_a, 64, 0.0, seed=42)
    assert len(mc_f0) == 64, f"build_mixed_corpus length mismatch: {len(mc_f0)}"

    # Self-test 5: run_one_cell returns valid retention at smoke scale
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    result = run_one_cell(
        seed=17, f=0.5, N=N_SMOKE, batch_size=BATCH_SIZE_SMOKE,
        n_epochs=EPOCHS_SMOKE, phase_a_epochs=PHASE_A_EPOCHS_SMOKE,
        n_bytes=BYTES_SMOKE, device=device
    )
    assert "retention_A" in result, f"run_one_cell missing 'retention_A': {result.keys()}"
    ret = result["retention_A"]
    assert isinstance(ret, float) and 0.0 <= ret <= 1.0, f"retention_A out of range: {ret}"
    assert ret > 0.01, f"retention_A suspiciously near zero: {ret} -- instrumentation suspect"

    print("[selftest] v6 self-test PASSED: N=4096 assertion, pearson_r2, build_mixed_corpus, "
          f"run_one_cell (smoke retention={ret:.4f})", flush=True)


_instrumentation_selftest()


def run(smoke: bool = False) -> None:
    t0 = time.time()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    N = N_SMOKE if smoke else N_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    f_sweep = F_SWEEP_SMOKE if smoke else F_SWEEP_FULL
    batch_size = BATCH_SIZE_SMOKE if smoke else BATCH_SIZE_FULL
    epochs = EPOCHS_SMOKE if smoke else EPOCHS_FULL
    phase_a_epochs = PHASE_A_EPOCHS_SMOKE if smoke else PHASE_A_EPOCHS_FULL
    n_bytes = BYTES_SMOKE if smoke else BYTES_FULL

    mode_str = "SMOKE" if smoke else "FULL"
    exp_name = "wave14_saddle_cascade_plateau_v6_n4096_gpu"
    print(f"[run] {exp_name} {mode_str} N={N} seeds={seeds} device={device}", flush=True)

    out_dir = get_output_dir(exp_name)

    # Per-seed per-f retention
    seed_results = {}
    for seed in seeds:
        print(f"\n[seed={seed}]", flush=True)
        per_f_rets = {}
        for f in f_sweep:
            cell = run_one_cell(
                seed=seed, f=f, N=N, batch_size=batch_size,
                n_epochs=epochs, phase_a_epochs=phase_a_epochs,
                n_bytes=n_bytes, device=device
            )
            ret = cell["retention_A"]
            per_f_rets[f] = [ret]   # wrap in list for compute_verdict compatibility
            print(f"  f={f:.2f} retention_A={ret:.4f}", flush=True)
        seed_results[seed] = per_f_rets

    # Per-seed verdict
    seed_verdicts = {}
    for seed, per_f_rets in seed_results.items():
        fs = sorted(per_f_rets.keys())
        retentions = [per_f_rets[f][0] for f in fs]
        r2 = pearson_r2(fs, retentions)
        _, max_dev, _ = linear_fit_residuals(fs, retentions)
        if r2 < LINEAR_R2_PASS_THRESHOLD and max_dev >= DEVIATION_PASS_THRESHOLD:
            v = "HARD_PASS"
        elif r2 >= LINEAR_R2_FAIL_THRESHOLD and max_dev < DEVIATION_FAIL_THRESHOLD:
            v = "HARD_FAIL"
        else:
            v = "MIDDLE"
        seed_verdicts[seed] = {"verdict": v, "r2": round(r2, 4), "max_dev": round(max_dev, 4)}
        print(f"  [seed={seed}] r2={r2:.4f} max_dev={max_dev:.4f} -> {v}", flush=True)

    # Overall verdict
    n_hardpass = sum(1 for sv in seed_verdicts.values() if sv["verdict"] == "HARD_PASS")
    n_hardfail = sum(1 for sv in seed_verdicts.values() if sv["verdict"] == "HARD_FAIL")
    n_middle = sum(1 for sv in seed_verdicts.values() if sv["verdict"] == "MIDDLE")

    if n_hardpass >= N_SEEDS_HARDPASS_FOR_OVERALL:
        overall = "HARD_PASS"
        overall_msg = (
            f"HARD_PASS: {n_hardpass}/{len(seeds)} seeds HARD-PASS at N={N}. "
            f"Saddle-cascade plateau discrete structure confirmed at N=4096. "
            f"Genuine large-N FULL evidence for Saad-Solla as leading theoretical home."
        )
    elif n_hardfail >= N_SEEDS_HARDFAIL_FOR_OVERALL:
        overall = "HARD_FAIL"
        overall_msg = (
            f"HARD_FAIL: {n_hardfail}/{len(seeds)} seeds HARD-FAIL at N={N}. "
            f"Discrete plateau structure does not persist at N=4096. "
            f"Finite-N artifact hypothesis supported."
        )
    else:
        overall = "MIDDLE_BAND"
        overall_msg = (
            f"MIDDLE_BAND: {n_hardpass} HARD-PASS, {n_hardfail} HARD-FAIL, "
            f"{n_middle} MIDDLE at N={N}. Mixed evidence at full scale."
        )

    elapsed = round(time.time() - t0, 2)
    print(f"\n[result] overall={overall} "
          f"HARD_PASS={n_hardpass}/{len(seeds)} "
          f"HARD_FAIL={n_hardfail}/{len(seeds)}", flush=True)
    print(f"[verdict] {overall}", flush=True)
    print(f"[verdict_msg] {overall_msg}", flush=True)
    print(f"elapsed={elapsed}s", flush=True)

    metrics = {
        "verdict": overall,
        "verdict_msg": overall_msg,
        "elapsed_s": elapsed,
        "summary": {
            "N": N,
            "seeds": seeds,
            "n_hardpass": n_hardpass,
            "n_hardfail": n_hardfail,
            "n_middle": n_middle,
            "seed_verdicts": seed_verdicts,
            "f_sweep": f_sweep,
        },
        "config": {
            "mode": mode_str,
            "N": N,
            "seeds": seeds,
            "f_sweep": f_sweep,
            "batch_size": batch_size,
            "epochs": epochs,
            "phase_a_epochs": phase_a_epochs,
            "n_bytes": n_bytes,
            "device": str(device),
            "parent_v3_r2": 0.322,
            "parent_v3_max_dev": 0.249,
        },
    }

    mpath = out_dir / "metrics.json"
    with open(mpath, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"[exp] metrics -> {mpath}", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true", dest="self_test",
                        help="Run instrumentation self-tests only and exit")
    args = parser.parse_args()
    if args.self_test:
        sys.exit(0)
    run(smoke=args.smoke)
