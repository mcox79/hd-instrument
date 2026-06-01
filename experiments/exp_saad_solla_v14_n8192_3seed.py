"""Saad-Solla saddle-cascade v14 at N=8192: 3-seed option-(c) re-ship.

CONTEXT:
  v11 (2-seed N=8192 HARD_PASS): R^2~0.65, max_dev~0.14. SKAH-M saddle-cascade confirmed.
  v12 (5-seed N=8192 TIMEOUT): per-cell wall ~500s at N=8192; 5 seeds x 3 f-cells = 7500s
    required but only 1800s budgeted. INFRASTRUCTURE failure, NOT physics failure.
  v13 (5-seed N=4096 TIMEOUT): per-cell wall ~240s at N=4096; 5 seeds x 5 f-cells = 6000s
    required but only 3600s budgeted. 2nd consecutive INFRA failure.
  v14 (THIS): option-(c) per strategy_request_to_exp_dev_v261_saad_solla_v14.md
    3 seeds {7, 17, 23} x 3 f-cells = 9 cells x ~960s/cell at N=8192 = ~8640s.
    timeout_s=12600 (45% headroom; from routing note recommendation).
    This is the 3rd rescue attempt; further infra-fails would PARK 5-seed envelope-extension.

SCIENTIFIC QUESTION:
  Does non-monotone discrete-plateau R^2/max_dev signal replicate at 3 seeds N=8192?
  Primary: >= 2/3 seeds: R^2 < 0.85 AND max_dev >= 0.08.
  Strong: 3/3 seeds.

PRE-REGISTERED BANDS (per routing note; prior anchor = v11 N=8192 2-seed HARD_PASS):
  HARD_PASS: >= 2/3 seeds: R^2 < 0.85 AND max_dev >= 0.08.
    Combined with v252 2-seed = 5-seed-equivalent via union at N=8192.
  HARD_FAIL: >= 2/3 seeds: R^2 >= 0.95 AND max_dev < 0.04 (smooth-monotone).
    Would raise reproducibility questions about v11.
  MIDDLE_BAND: 1/3 seeds clear, or only one threshold per seed.

CALIBRATION: prior anchor = v11 N=8192 2-seed HARD_PASS R^2~0.65, max_dev~0.14.
  Bands NOT widened to +-50% (prior anchor exists).

FORMULA SELF-TESTS:
  1. pearson_r2([0,1,2,3,4],[0,2,4,6,8]) = 1.0 (linear). R^2 >= 0.85 -> no plateau.
  2. pearson_r2([0.60,0.62,0.94,0.94,0.94],[0,1,2,3,4]) < 0.80. R^2 < 0.85 -> plateau.
  3. max_dev of plateau data [0.60,0.62,0.94,0.94,0.94] at f=[0,0.25,0.5,0.75,1.0]:
     linear residual max ~0.10 >= 0.08.
  4. N == 8192 assertion (PROT-018).
  5. seeds == [7, 17, 23] (3-seed option-c assertion).
  6. HARD_PASS fires for >= 2/3 seeds with R^2<0.85 and max_dev>=0.08.

OOM CHECK:
  W float32 at N=8192: 8192^2 * 4 = 256MB. No replay pool. Peak ~256MB. Under 6GB. OK.

TIMEOUT ESTIMATE:
  v13 hit timeout at 3600s with per-cell wall ~240s at N=4096.
  N-scale factor (8192/4096)^1.5 = 2.828x -> per-cell at N=8192 ~= 240 * 2.828 = 679s.
  Conservative: use routing note figure of 960s/cell (per v259 calibration: 3 f-cells x 960s).
  3 seeds x 3 f-cells = 9 cells x 960s = 8640s.
  timeout_s = ceil(8640 * 1.5 / 1.0) but routing note caps at 12600s (45% headroom over 8640s).
  Use timeout_s = 12600 (routing note recommendation; 3rd reship justifies cap).
  NOTE: exceeds 7200s (2h). Flagged for visibility per role contract.

N-suffix: _n8192 -> production N = 8192 (PROT-018 binding).
Seeds: 3 seeds {7, 17, 23} (option-c; NOT 5-seed).
Anchor: saad_solla_v14_n8192_3seed
Queue: overnight_queue (GPU; N=8192 3-seed Saad-Solla plateau measurement)
Pre-reg: preregs/2026-05-28_saad_solla_v14_n8192_3seed.md
Parent: saad_solla_v13_n4096_5seed (TIMEOUT); saad_solla_v11_n8192 (2-seed HARD_PASS v252)
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import importlib.util
import json
import os
import time
from pathlib import Path
from typing import Dict, List

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# Load v11 base (same protocol: no replay, same W construction)
_v11_path = REPO / "experiments" / "exp_saad_solla_v11_n8192.py"
_v11_spec = importlib.util.spec_from_file_location("ss_v11_v14", _v11_path)
v11 = importlib.util.module_from_spec(_v11_spec)
_v11_spec.loader.exec_module(v11)

# Import helpers from v11
pearson_r2 = v11.pearson_r2
linear_fit_residuals = v11.linear_fit_residuals
run_one_cell_no_replay = v11.run_one_cell_no_replay

# PRODUCTION CONFIG -- PROT-018: _n8192 suffix binds to N = 8192
N = 8192         # PROT-018 binding contract
N_SMOKE = 512
assert N == 8192, f"PROT-018: N must be 8192; got {N}"

# 3 f-cells per seed (minimal but valid: captures plateau across [0, 0.5, 1.0])
F_SWEEP_FULL = [0.0, 0.50, 1.0]
F_SWEEP_SMOKE = [0.0, 0.5, 1.0]

# option-(c): 3 seeds (NOT 5-seed) for safer timeout margin
SEEDS_FULL = [7, 17, 23]
SEEDS_SMOKE = [17]

BATCH_SIZE = 32
BATCH_SIZE_SMOKE = 16
EPOCHS = 3
EPOCHS_SMOKE = 1
PHASE_A_EPOCHS = 3
PHASE_A_EPOCHS_SMOKE = 1
BYTES = 150_000
BYTES_SMOKE = 4_000

# Pre-registered thresholds (3-seed adjusted; per routing note HF1/HF2/HF3)
HP_R2_MAX = 0.85
HP_MAX_DEV_MIN = 0.08
HF_R2_MIN = 0.95
HF_MAX_DEV_MAX = 0.04
HP_MAJORITY_MIN = 2   # >= 2/3 seeds clear both thresholds = HARD_PASS
HP_STRONG_MIN = 3     # 3/3 seeds = strong HARD_PASS


def get_output_dir(default_name: str = "saad_solla_v14_n8192_3seed") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def compute_verdict(summary: Dict) -> tuple:
    per_seed = summary.get("per_seed", {})
    if not per_seed:
        return ("SS_V14_MIDDLE_BAND", "No per-seed data.")

    pass_seeds = 0
    fail_seeds = 0
    seed_details = {}

    for seed_k, sd in per_seed.items():
        r2 = sd.get("r2", 1.0)
        max_dev = sd.get("max_dev", 0.0)
        passes_hp = (r2 < HP_R2_MAX) and (max_dev >= HP_MAX_DEV_MIN)
        passes_hf = (r2 >= HF_R2_MIN) and (max_dev < HF_MAX_DEV_MAX)
        if passes_hp:
            pass_seeds += 1
        if passes_hf:
            fail_seeds += 1
        seed_details[seed_k] = {"r2": round(r2, 3), "max_dev": round(max_dev, 3),
                                 "passes": passes_hp}

    total = len(per_seed)
    r2_list = [sd.get("r2", 1.0) for sd in per_seed.values()]
    md_list = [sd.get("max_dev", 0.0) for sd in per_seed.values()]
    mean_r2 = sum(r2_list) / len(r2_list) if r2_list else 0.0
    mean_md = sum(md_list) / len(md_list) if md_list else 0.0

    detail_str = (f"pass_seeds={pass_seeds}/{total} r2<0.85 AND max_dev>=0.08. "
                  f"mean_r2={mean_r2:.3f} mean_max_dev={mean_md:.3f}. "
                  f"seed_details={seed_details}. N={N}.")

    if pass_seeds >= HP_MAJORITY_MIN:
        level = "STRONG" if pass_seeds >= HP_STRONG_MIN else "MAJORITY"
        return (f"SS_V14_HARD_PASS_{level}",
                f"SAAD-SOLLA PLATEAU CONFIRMED N=8192 ({level}): {pass_seeds}/{total} seeds "
                f"clear R^2<{HP_R2_MAX} AND max_dev>={HP_MAX_DEV_MIN}. " + detail_str)

    if fail_seeds >= max(1, total - 1) and pass_seeds == 0:
        return ("SS_V14_HARD_FAIL",
                f"HARD_FAIL: {fail_seeds}/{total} seeds smooth-monotone. " + detail_str)

    return ("SS_V14_MIDDLE_BAND", "Partial replication. " + detail_str)


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics non-null/non-sentinel at small scale."""
    assert N == 8192, f"PROT-018: N={N} must be 8192"

    # Test pearson_r2
    r2_linear = pearson_r2([0.0, 1.0, 2.0, 3.0, 4.0], [0.0, 2.0, 4.0, 6.0, 8.0])
    assert abs(r2_linear - 1.0) < 1e-4, f"pearson_r2 linear test failed: {r2_linear}"

    r2_plateau = pearson_r2([0.60, 0.62, 0.94, 0.94, 0.94],
                             [0.0, 0.25, 0.5, 0.75, 1.0])
    assert r2_plateau < HP_R2_MAX, f"pearson_r2 plateau test failed: {r2_plateau} >= {HP_R2_MAX}"

    # Test linear_fit_residuals
    _fit = linear_fit_residuals([0.60, 0.62, 0.94, 0.94, 0.94],
                                 [0.0, 0.25, 0.5, 0.75, 1.0])
    residuals = _fit[2] if isinstance(_fit, tuple) else _fit
    max_dev_test = max(abs(r) for r in residuals) if residuals else 0.0
    assert max_dev_test >= HP_MAX_DEV_MIN, \
        f"Self-test max_dev: {max_dev_test} < {HP_MAX_DEV_MIN}"

    # Test verdict HARD_PASS path (majority: 2/3)
    per_seed_pass = {str(s): {"r2": 0.65, "max_dev": 0.14} for s in [7, 17, 23]}
    v, msg = compute_verdict({"per_seed": per_seed_pass})
    assert "HARD_PASS" in v, f"Self-test HARD_PASS_STRONG failed: {v}: {msg}"

    # Test verdict partial (1/3 pass)
    per_seed_partial = {}
    for i, s in enumerate([7, 17, 23]):
        if i < 1:
            per_seed_partial[str(s)] = {"r2": 0.65, "max_dev": 0.14}  # pass
        else:
            per_seed_partial[str(s)] = {"r2": 0.97, "max_dev": 0.02}  # fail
    v2, _ = compute_verdict({"per_seed": per_seed_partial})
    assert "MIDDLE_BAND" in v2 or "HARD_FAIL" in v2, \
        f"Self-test partial should be MIDDLE_BAND or HARD_FAIL: {v2}"

    # Test HARD_FAIL path (2/3 smooth-monotone, 0 plateau)
    per_seed_fail = {str(s): {"r2": 0.98, "max_dev": 0.02} for s in [7, 17, 23]}
    v3, _ = compute_verdict({"per_seed": per_seed_fail})
    assert "HARD_FAIL" in v3, f"Self-test HARD_FAIL failed: {v3}"

    # 3-seed assertion
    assert len(SEEDS_FULL) == 3 and set(SEEDS_FULL) == {7, 17, 23}, \
        f"Expected 3 seeds {{7,17,23}}; got {SEEDS_FULL}"

    # Test at smoke scale (one forward pass)
    device = torch.device("cpu")
    result = run_one_cell_no_replay(
        seed=17, f=0.5, N_cfg=N_SMOKE,
        batch_size=BATCH_SIZE_SMOKE,
        n_epochs=EPOCHS_SMOKE,
        phase_a_epochs=PHASE_A_EPOCHS_SMOKE,
        n_bytes=BYTES_SMOKE,
        device=device,
    )
    assert result.get("retention_A") is not None, \
        f"retention_A is None in selftest: {result}"
    assert 0 <= result.get("retention_A", -1.0) <= 1.0, \
        f"retention_A out of range: {result.get('retention_A')}"

    # OOM pre-check at N=8192
    oom_bytes = N * N * 4
    assert oom_bytes < 6e9, f"OOM pre-check failed: {oom_bytes:.2e} >= 6GB"

    print(f"[SELFTEST PASS] saad_solla_v14_n8192_3seed: N={N} seeds={SEEDS_FULL} "
          f"OOM={oom_bytes:.2e}B smoke_ret_A={result.get('retention_A', -1):.4f}",
          flush=True)


_instrumentation_selftest()  # Called at module scope before sweep


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true", dest="self_test")
    parser.add_argument("--timeout", type=int, default=12600)
    args = parser.parse_args()
    if args.self_test:
        sys.exit(0)

    smoke = args.smoke
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    N_use = N_SMOKE if smoke else N
    f_sweep = F_SWEEP_SMOKE if smoke else F_SWEEP_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL

    outdir = get_output_dir()
    t0 = time.time()
    per_seed: Dict = {}

    for seed in seeds:
        seed_cells = []
        for f in f_sweep:
            cell = run_one_cell_no_replay(
                seed=seed, f=f, N_cfg=N_use,
                batch_size=BATCH_SIZE_SMOKE if smoke else BATCH_SIZE,
                n_epochs=EPOCHS_SMOKE if smoke else EPOCHS,
                phase_a_epochs=PHASE_A_EPOCHS_SMOKE if smoke else PHASE_A_EPOCHS,
                n_bytes=BYTES_SMOKE if smoke else BYTES,
                device=device,
            )
            seed_cells.append(cell)
            elapsed = time.time() - t0
            print(f"seed={seed} f={f:.2f} ret_A={cell.get('retention_A', 0):.3f} "
                  f"elapsed={elapsed:.1f}s", flush=True)

        f_vals = [c["f"] for c in seed_cells]
        ret_vals = [c["retention_A"] for c in seed_cells]
        r2 = pearson_r2(ret_vals, f_vals)
        _fit_result = linear_fit_residuals(ret_vals, f_vals)
        residuals = _fit_result[2] if isinstance(_fit_result, tuple) else _fit_result
        max_dev = max(abs(r) for r in residuals) if residuals else 0.0
        per_seed[str(seed)] = {"r2": r2, "max_dev": max_dev, "cells": seed_cells}
        print(f"  -> seed={seed} r2={r2:.3f} max_dev={max_dev:.3f}", flush=True)

    elapsed_s = time.time() - t0
    summary = {"per_seed": per_seed, "N": N_use, "smoke": smoke}
    verdict, verdict_msg = compute_verdict(summary)

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": elapsed_s,
        "config": {
            "N": N_use,
            "seeds": seeds,
            "f_sweep": f_sweep,
            "smoke": smoke,
        },
        "summary": summary,
    }

    out = outdir / "metrics.json"
    with open(out, "w") as f_out:
        json.dump(metrics, f_out, indent=2)

    print(f"\nVERDICT: {verdict}")
    print(f"MSG: {verdict_msg}")
    print(f"elapsed={elapsed_s:.1f}s")
    print(f"metrics -> {out}")


if __name__ == "__main__":
    main()
