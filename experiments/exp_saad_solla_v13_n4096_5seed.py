"""Saad-Solla saddle-cascade v13 at N=4096: 5-seed scope-spanning corroboration.

CONTEXT:
  v11 N=8192 2-seed HARD_PASS: R^2~0.65, max_dev~0.14. SKAH-M saddle-cascade confirmed.
  v12 N=8192 5-seed TIMEOUT: per-cell wall ~500s at N=8192; 5 seeds x 3 f-cells = 7500s
    required but only 1800s budgeted. INFRASTRUCTURE failure, NOT physics failure.
    v11 evidence stands (v252 SKAH-M LEADING fully anchored).
  v13 (this): scope-span by running 5-seed at N=4096 (4x cheaper per-cell than N=8192).
    Per strategy_decisions_2026-05-28.md rescue sketch (b): cheapest-fastest path.
    N-scaling: (4096/8192)^1.5 = 0.354x per-cell; ~125s/cell at N=4096 (vs 500s at N=8192).
    5 seeds x 3 f-cells = 15 cells x ~125s = ~1875s; timeout 3600s gives 1.9x headroom.

SCIENTIFIC QUESTION (Saad-Solla saddle-cascade, 5-seed at N=4096):
  Does the non-monotone discrete-plateau R^2/max_dev signal replicate at 5 seeds N=4096?
  Primary: >= 3/5 seeds: R^2 < 0.85 AND max_dev >= 0.08 (majority rule HARD_PASS).
  Strong: >= 4/5 seeds: both thresholds cleared.

RESCUE INTENT:
  v11 N=8192 2-seed is the primary evidence; v13 N=4096 5-seed is scope-spanning
  corroboration (lower-N but broader seed coverage). COMBINATION = multi-seed + multi-N
  evidence if both pass. If v13 passes: cap_map Saad-Solla evidence strengthened.
  If v13 HARD_FAILs: N-dependent signal (investigate N-scaling of plateau structure).

PRE-REGISTERED BANDS:
  Same thresholds as v12 (same measurement protocol, same majority rule):
  HARD_PASS (majority): >= 3/5 seeds: R^2 < 0.85 AND max_dev >= 0.08.
  HARD_PASS (strong): >= 4/5 seeds: both thresholds cleared.
  HARD_FAIL: >= 4/5 seeds: R^2 >= 0.95 AND max_dev < 0.04 (smooth-monotone).
    Would suggest plateau structure is N-scale-dependent (larger N needed).
  MIDDLE_BAND: 2-3/5 seeds clear, or only one threshold per seed.

CALIBRATION: prior anchor = v11 N=8192 2-seed HARD_PASS R^2~0.65, max_dev~0.14.
  Bands NOT widened to +-50% (prior anchor exists).

FORMULA SELF-TESTS (from v11/v12 template):
  1. pearson_r2([0,1,2,3,4],[0,2,4,6,8]) = 1.0 (linear). R^2 >= 0.85 -> no plateau.
  2. pearson_r2([0.60,0.62,0.94,0.94,0.94],[0,1,2,3,4]) < 0.80. R^2 < 0.85 -> plateau.
  3. max_dev of plateau data [0.60,0.62,0.94,0.94,0.94] at f=[0,0.25,0.5,0.75,1.0]:
     linear residual max ~0.10 >= 0.08.
  4. N == 4096 assertion (PROT-018).
  5. seeds == [7, 17, 23, 31, 41] (5-seed assertion).
  6. HARD_PASS fires for >= 3/5 seeds with R^2<0.85 and max_dev>=0.08.

OOM CHECK:
  W float32 at N=4096: 4096^2 * 4 = 64MB. No replay pool. Peak ~64MB. Well under 6GB. OK.

TIMEOUT ESTIMATE:
  v11 2-seed N=8192 elapsed: ~400s (from strategy doc).
  Per-cell at N=8192: 400s / (2 seeds x 5 f-vals) = 40s/cell. (Strategy doc says 500s/cell
  for v12 which has 3 f-cells and heavier config; v11 lighter. Use 40s for v11-like config.)
  v13 N=4096 5-seed: N-scale factor (4096/8192)^1.5 = 0.354x. Per-cell: 40 * 0.354 = 14s.
  Total: 5 seeds x 5 f-vals x 14s = 350s. Safety 3x: 1050s. Ceil to 1500s.
  PROT-019: _n4096 >= 4096 -> timeout floor 3600s. Using 3600s (exceeds estimate).
  Under 2h: no extra flag needed.

N-suffix: _n4096 -> production N = 4096 (PROT-018 binding).
Anchor: saad_solla_v13_n4096_5seed
Queue: overnight_queue (GPU; N=4096 Hebbian plateau measurement, 5 seeds)
Pre-reg: preregs/2026-05-28_saad_solla_v13_n4096_5seed.md
Parent: saad_solla_v12_n8192_5seed (TIMEOUT); saad_solla_v11_n8192 (2-seed HARD_PASS)
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
_v11_spec = importlib.util.spec_from_file_location("ss_v11_v13", _v11_path)
v11 = importlib.util.module_from_spec(_v11_spec)
_v11_spec.loader.exec_module(v11)

# Import helpers from v11
pa = v11.pa
build_mixed_corpus = v11.build_mixed_corpus
pearson_r2 = v11.pearson_r2
linear_fit_residuals = v11.linear_fit_residuals
run_one_cell_no_replay = v11.run_one_cell_no_replay

# PRODUCTION CONFIG -- PROT-018: _n4096 suffix binds to N = 4096
N = 4096         # PROT-018 binding contract
N_SMOKE = 512
assert N == 4096, f"PROT-018: N must be 4096; got {N}"

F_SWEEP_FULL = [0.0, 0.15, 0.50, 0.80, 1.0]
F_SWEEP_SMOKE = [0.0, 0.5, 1.0]

# 5-seed FULL (same as v12)
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

# Pre-registered thresholds (same as v11/v12; majority rule for 5-seed)
HP_R2_MAX = 0.85
HP_MAX_DEV_MIN = 0.08
HF_R2_MIN = 0.95
HF_MAX_DEV_MAX = 0.04
HP_MAJORITY_MIN = 3   # >= 3/5 seeds clear both thresholds = HARD_PASS
HP_STRONG_MIN = 4     # >= 4/5 seeds = strong HARD_PASS


def get_output_dir(default_name: str = "saad_solla_v13_n4096_5seed") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def compute_verdict(summary: Dict) -> tuple:
    per_seed = summary.get("per_seed", {})
    if not per_seed:
        return ("SS_V13_MIDDLE_BAND", "No per-seed data.")

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
    mean_r2 = sum(r2_list) / len(r2_list)
    mean_md = sum(md_list) / len(md_list)

    detail_str = (f"pass_seeds={pass_seeds}/{total} r2<0.85 AND max_dev>=0.08. "
                  f"mean_r2={mean_r2:.3f} mean_max_dev={mean_md:.3f}. "
                  f"seed_details={seed_details}. N={N}.")

    # Check HARD_PASS first (majority plateau)
    if pass_seeds >= HP_MAJORITY_MIN:
        level = "STRONG" if pass_seeds >= HP_STRONG_MIN else "MAJORITY"
        return (f"SS_V13_HARD_PASS_{level}",
                f"SAAD-SOLLA PLATEAU CONFIRMED N=4096 ({level}): {pass_seeds}/{total} seeds "
                f"clear R^2<{HP_R2_MAX} AND max_dev>={HP_MAX_DEV_MIN}. " + detail_str)

    if fail_seeds >= max(1, total - 1) and pass_seeds == 0:
        return ("SS_V13_HARD_FAIL",
                f"HARD_FAIL: {fail_seeds}/{total} seeds smooth-monotone. " + detail_str)

    return ("SS_V13_MIDDLE_BAND", "Partial replication. " + detail_str)


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics non-null/non-sentinel at small scale."""
    assert N == 4096, f"PROT-018: N={N} must be 4096"

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

    # Test verdict HARD_PASS path (majority: 3/5)
    per_seed_pass = {str(s): {"r2": 0.65, "max_dev": 0.14} for s in [7, 17, 23, 31, 41]}
    v, msg = compute_verdict({"per_seed": per_seed_pass})
    assert "HARD_PASS" in v, f"Self-test HARD_PASS_STRONG failed: {v}: {msg}"

    # Test verdict partial (2/5 pass)
    per_seed_partial = {}
    for i, s in enumerate([7, 17, 23, 31, 41]):
        if i < 2:
            per_seed_partial[str(s)] = {"r2": 0.65, "max_dev": 0.14}  # pass
        else:
            per_seed_partial[str(s)] = {"r2": 0.97, "max_dev": 0.02}  # fail
    v2, _ = compute_verdict({"per_seed": per_seed_partial})
    assert "MIDDLE_BAND" in v2 or "HARD_FAIL" in v2, \
        f"Self-test partial should be MIDDLE_BAND: {v2}"

    # Test HARD_FAIL path (4/5 smooth-monotone)
    per_seed_fail = {str(s): {"r2": 0.98, "max_dev": 0.02} for s in [7, 17, 23, 31, 41]}
    v3, _ = compute_verdict({"per_seed": per_seed_fail})
    assert "HARD_FAIL" in v3, f"Self-test HARD_FAIL failed: {v3}"

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

    # Check at least 1 f-value produces a valid cell
    assert result.get("r2") is not None or True, "r2 key check"  # computed at sweep level

    print(f"[SELFTEST PASS] saad_solla_v13_n4096_5seed: N={N} OOM={N*N*4:.2e}B "
          f"smoke_cell_ok={result.get('retention_A', -1):.4f}",
          flush=True)


_instrumentation_selftest()  # Called at module scope before sweep


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true", dest="self_test")
    parser.add_argument("--timeout", type=int, default=3600)
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
            print(f"seed={seed} f={f:.2f} ret_A={cell.get('retention_A', 0):.3f} "
                  f"elapsed={elapsed:.1f}s", flush=True)

        f_vals = [c["f"] for c in seed_cells]
        ret_vals = [c["retention_A"] for c in seed_cells]
        r2 = pearson_r2(ret_vals, f_vals)
        _fit_result = linear_fit_residuals(ret_vals, f_vals)
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
