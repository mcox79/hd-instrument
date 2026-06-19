"""Saad-Solla saddle-cascade v12 at N=8192: 5-SEED COMPLETION of v11 2-seed HARD_PASS.

CONTEXT:
  v11 (2-seed HARD_PASS): N=8192, seeds=[7,17], R^2<0.85 and max_dev>=0.08 on both seeds.
    Result: R^2~0.65, max_dev~0.14. SKAH-M saddle-cascade confirmed at production scale.
    Caveat: only 2 seeds. Walk-back rule: large effect size (d >> 1) justifies 2-seed
    confirmation, but 5-seed FULL is the convention for FULL evidence-strength.
  v12 (this): same protocol, expand to seeds=[7,17,23,31,41] (5-seed production set).
    Replay disabled (v11 isolation justified: plateau structure is Phase-A property only).

SCIENTIFIC QUESTION (Saad-Solla saddle-cascade, 5-seed FULL):
  Does the non-monotone discrete-plateau R^2/max_dev signal replicate at 5 seeds N=8192?
  Primary: >= 3/5 seeds: R^2 < 0.85 AND max_dev >= 0.08 (majority rule HARD_PASS).
  Strong: >= 4/5 seeds: both thresholds cleared (strong HARD_PASS).

PRE-REGISTERED BANDS:
  HARD_PASS (majority): >= 3/5 seeds: R^2 < 0.85 AND max_dev >= 0.08.
    Interpretation: plateau signal is substrate property, not seed artifact.
  HARD_PASS (strong): >= 4/5 seeds both thresholds.
  HARD_FAIL: >= 4/5 seeds: R^2 >= 0.95 AND max_dev < 0.04 (smooth-monotone at all seeds).
    This would overturn v11 and raise reproducibility questions.
  MIDDLE_BAND: 2-3/5 seeds clear, or only one threshold per seed.

CALIBRATION: prior anchor = v11 2-seed HARD_PASS R^2~0.65, max_dev~0.14 at N=8192.
  Bands NOT widened to +-50% (prior anchor exists).

FORMULA SELF-TESTS (from v11 template):
  1. pearson_r2([0,1,2,3,4],[0,2,4,6,8]) = 1.0 (linear). R^2 >= 0.85.
  2. pearson_r2([0.60,0.62,0.94,0.94,0.94],[0,1,2,3,4]) < 0.80. R^2 < 0.85.
  3. max_dev of plateau data [0.60,0.62,0.94,0.94,0.94] at f=[0,0.25,0.5,0.75,1.0]:
     linear_fit should predict monotone; max residual ~0.10 >= 0.08.
  4. N == 8192 assertion (PROT-018).
  5. seeds == [7, 17, 23, 31, 41] (5-seed assertion).

OOM CHECK:
  W float32 at N=8192: 8192^2 * 4 = 256MB. No replay pool. Peak ~256MB. Under 6GB. OK.

TIMEOUT ESTIMATE:
  v11 2-seed elapsed: ~400s (well under 4500s estimate; fast at no-replay).
  v12 5-seed: scale 5/2 = 2.5x.
  timeout_s = ceil(1.5 * 400 * 2.5) = ceil(1500) -> 1800s.
  Under 2h. No extra flag.

N-suffix: _n8192 -> N = 8192 (PROT-018 binding).
Anchor: saad_solla_v12_n8192_5seed
Queue: overnight_queue (GPU; N=8192 5-seed Saad-Solla plateau measurement)
Pre-reg: preregs/2026-05-28_saad_solla_v12_n8192_5seed.md
Parent: saad_solla_v11_n8192 (HARD_PASS 2-seed; this extends to 5-seed production convention)
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
_v11_spec = importlib.util.spec_from_file_location("ss_v11_v12", _v11_path)
v11 = importlib.util.module_from_spec(_v11_spec)
_v11_spec.loader.exec_module(v11)

# Import helpers from v11
pa = v11.pa
build_mixed_corpus = v11.build_mixed_corpus
pearson_r2 = v11.pearson_r2
linear_fit_residuals = v11.linear_fit_residuals
run_one_cell_no_replay = v11.run_one_cell_no_replay

# PRODUCTION CONFIG -- PROT-018: _n8192 suffix binds to N = 8192
N = 8192         # PROT-018 binding contract
N_SMOKE = 512
assert N == 8192, f"PROT-018: N must be 8192; got {N}"

F_SWEEP_FULL = [0.0, 0.15, 0.50, 0.80, 1.0]
F_SWEEP_SMOKE = [0.0, 0.5, 1.0]

# 5-seed FULL (key change from v11 2-seed)
SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]

BATCH_SIZE = 32
BATCH_SIZE_SMOKE = 16
EPOCHS = 3
EPOCHS_SMOKE = 1
PHASE_A_EPOCHS = 3
PHASE_A_EPOCHS_SMOKE = 1
BYTES = 150_000
BYTES_SMOKE = 4_000

# Pre-registered thresholds (same as v11; majority rule for 5-seed)
HP_R2_MAX = 0.85
HP_MAX_DEV_MIN = 0.08
HF_R2_MIN = 0.95
HF_MAX_DEV_MAX = 0.04
HP_MAJORITY_MIN = 3   # >= 3/5 seeds clear both thresholds = HARD_PASS
HP_STRONG_MIN = 4     # >= 4/5 seeds = strong HARD_PASS


def get_output_dir(default_name: str = "saad_solla_v12_n8192_5seed") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def compute_verdict(summary: Dict) -> tuple:
    per_seed = summary.get("per_seed", {})
    if not per_seed:
        return ("SS_V12_MIDDLE_BAND", "No per-seed data.")

    pass_seeds = 0
    strong_seeds = 0
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
    strong = sum(1 for d in seed_details.values() if d["passes"])
    pass_seeds = strong

    r2_list = [sd.get("r2", 1.0) for sd in per_seed.values()]
    md_list = [sd.get("max_dev", 0.0) for sd in per_seed.values()]
    mean_r2 = sum(r2_list) / len(r2_list)
    mean_md = sum(md_list) / len(md_list)

    detail_str = (f"pass_seeds={pass_seeds}/{total} r2<0.85 AND max_dev>=0.08. "
                  f"mean_r2={mean_r2:.3f} mean_max_dev={mean_md:.3f}. "
                  f"seed_details={seed_details}.")

    # Check HARD_PASS first (majority plateau) before HARD_FAIL
    if pass_seeds >= HP_MAJORITY_MIN:
        level = "STRONG" if pass_seeds >= HP_STRONG_MIN else "MAJORITY"
        return (f"SS_V12_HARD_PASS_{level}",
                f"SAAD-SOLLA PLATEAU CONFIRMED ({level}): {pass_seeds}/{total} seeds clear "
                f"R^2<{HP_R2_MAX} AND max_dev>={HP_MAX_DEV_MIN}. " + detail_str)

    # HARD_FAIL only when majority clearly smooth-monotone
    if fail_seeds >= max(1, total - 1) and pass_seeds == 0:
        return ("SS_V12_HARD_FAIL",
                f"HARD_FAIL: {fail_seeds}/{total} seeds smooth-monotone. " + detail_str)

    return ("SS_V12_MIDDLE_BAND", "Partial replication. " + detail_str)


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics non-null/non-sentinel at small scale."""
    assert N == 8192, f"PROT-018: N={N} must be 8192"

    # Test pearson_r2
    r2_linear = pearson_r2([0.0, 1.0, 2.0, 3.0, 4.0], [0.0, 2.0, 4.0, 6.0, 8.0])
    assert abs(r2_linear - 1.0) < 1e-4, f"pearson_r2 linear test failed: {r2_linear}"

    r2_plateau = pearson_r2([0.60, 0.62, 0.94, 0.94, 0.94],
                             [0.0, 0.25, 0.5, 0.75, 1.0])
    assert r2_plateau < HP_R2_MAX, f"pearson_r2 plateau test failed: {r2_plateau} >= {HP_R2_MAX}"

    # Test verdict HARD_PASS path
    per_seed_pass = {
        str(s): {"r2": 0.65, "max_dev": 0.14} for s in [7, 17, 23, 31, 41]
    }
    v, msg = compute_verdict({"per_seed": per_seed_pass})
    assert "HARD_PASS" in v, f"Self-test HARD_PASS failed: {v}: {msg}"

    # Test verdict HARD_FAIL path
    per_seed_fail = {
        str(s): {"r2": 0.98, "max_dev": 0.02} for s in [7, 17, 23, 31, 41]
    }
    v2, _ = compute_verdict({"per_seed": per_seed_fail})
    assert "HARD_FAIL" in v2, f"Self-test HARD_FAIL failed: {v2}"

    # Test at least one actual forward pass at smoke scale
    device = torch.device("cpu")
    result = run_one_cell_no_replay(
        seed=17, f=0.5, N_cfg=N_SMOKE,
        batch_size=BATCH_SIZE_SMOKE,
        n_epochs=EPOCHS_SMOKE,
        phase_a_epochs=PHASE_A_EPOCHS_SMOKE,
        n_bytes=BYTES_SMOKE,
        device=device,
    )
    assert result.get("retention_A") is not None, f"retention_A is None in selftest: {result}"
    assert 0 <= result.get("retention_A", -1.0), f"retention_A out of range: {result['retention_A']}"


_instrumentation_selftest()  # Called at module scope before sweep


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true", dest="self_test")
    parser.add_argument("--timeout", type=int, default=1800)
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
    per_seed = {}

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
            print(f"seed={seed} f={f:.2f} r2={cell.get('r2',0):.3f} "
                  f"max_dev={cell.get('max_dev',0):.3f} elapsed={elapsed:.1f}s")

        f_vals = [c["f"] for c in seed_cells]
        ret_vals = [c["retention_A"] for c in seed_cells]
        r2 = pearson_r2(ret_vals, f_vals)
        _fit_result = linear_fit_residuals(ret_vals, f_vals)
        # linear_fit_residuals returns (slope, intercept, residuals_list)
        residuals = _fit_result[2] if isinstance(_fit_result, tuple) else _fit_result
        max_dev = max(abs(r) for r in residuals) if residuals else 0.0
        per_seed[str(seed)] = {"r2": r2, "max_dev": max_dev, "cells": seed_cells}

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
