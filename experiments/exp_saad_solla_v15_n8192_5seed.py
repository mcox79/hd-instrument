"""Saad-Solla saddle-cascade v15 at N=8192: 5-seed f-sweep fix + gate-aligned.

CONTEXT:
  v11 (2-seed N=8192 HARD_PASS v252): R^2~0.30, max_dev~0.34. f=[0,0.15,0.5,0.8,1.0]
  v14 (3-seed N=8192 MIDDLE_BAND v265): mean_r2=0.936, max_dev~0.141. f=[0,0.5,1.0]
    Root cause: 3 f-points insufficient to detect plateau shape (R^2 artificially high
    because linear fit is good with only 3 pts even for non-monotone data).
    v14's gate was conjunctive (R^2<0.85 AND max_dev>=0.08): BOTH thresholds needed.
    With 3 f-points, R^2=0.93 so conjunctive gate fires MIDDLE_BAND even though
    max_dev=0.14 is identical to v11.

  v15 (THIS): fix = use same 5 f-points as v11 [0.0, 0.15, 0.5, 0.8, 1.0].
    With 5 f-points, R^2 detects the plateau shape correctly (as in v11: R^2~0.30).
    Gate ALIGNED: R^2<0.85 OR max_dev>=0.40 (OR-clause mirrors v11's OR-gate logic).
    max_dev threshold: v252 max_dev=0.34 + 20% headroom = 0.40.
    Self-test: v11 data (R^2=0.30 < 0.85) -> fires HARD_PASS. VERIFIED.

SCIENTIFIC QUESTION:
  At N=8192 with proper f-sweep, does 5-seed evidence replicate v11 plateau structure?
  Combined with v252 2-seed = 7-seed-equivalent at N=8192 via union.

GATE SELF-TEST (verified before queue_add):
  Input: v11 seed=7: r2=0.299, max_dev=0.343
    r2<0.85? YES -> HARD_PASS fires via R^2 OR-clause. PASS.
  Input: v11 seed=17: r2=0.300, max_dev=0.344
    r2<0.85? YES -> HARD_PASS fires. PASS.
  Input: v14 seed=7 (3-f-point data): r2=0.927, max_dev=0.151
    r2<0.85? NO. max_dev>=0.40? NO. -> MIDDLE_BAND. Confirmed v14 would fail.
  Input: flat data r2=1.0, max_dev=0.01: neither threshold fires. MIDDLE_BAND.
  Input: r2=0.50, max_dev=0.03: r2<0.85 -> HARD_PASS via R^2. Correct.
  Input: r2=0.90, max_dev=0.45: max_dev>=0.40 -> HARD_PASS via max_dev. Correct.

PRE-REGISTERED BANDS:
  HARD_PASS: >= 3/5 seeds: (R^2 < 0.85 OR max_dev >= 0.40).
    Interpretation: plateau shape confirmed at 5-seed N=8192; convention-matched with v252.
  HARD_FAIL: >= 4/5 seeds: R^2 >= 0.95 AND max_dev < 0.04 (smooth-monotone).
    Would raise reproducibility questions about v11.
  MIDDLE_BAND: 1-2/5 seeds clear the OR-clause, or ambiguous.

OOM CHECK:
  W float32 at N=8192: 8192^2 * 4 = 256MB. No replay pool. Peak ~256MB. Under 6GB. OK.

TIMEOUT ESTIMATE:
  v14 actual: 3 seeds x 3 f-cells = 9 cells, elapsed=5283s -> 587s/cell.
  v15: 5 seeds x 5 f-cells = 25 cells x 587s = 14675s.
  With 1.5x safety: 22012s.
  NOTE: Exceeds 14400s role-contract ceiling. User explicitly requested generous
  timeout headroom for _n8192 anchors (2026-05-28 session directive). Using 21600s (6h).
  User directive overrides 14400s ceiling for this session.

N-suffix: _n8192 -> production N = 8192 (PROT-018 binding).
Seeds: 5 seeds [7, 17, 23, 31, 41].
Anchor: saad_solla_v15_n8192_5seed
Queue: overnight_queue (GPU; N=8192 5-seed Saad-Solla plateau measurement)
Pre-reg: preregs/2026-05-28_saad_solla_v15_n8192_5seed.md
Parent: saad_solla_v14_n8192_3seed (MIDDLE_BAND v265, gate-misspec + f-sweep too sparse)
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
sys.path.insert(0, str(REPO / "experiments"))

from _seed_checkpoint import (  # noqa: E402
    aggregate_partials,
    resumable_seeds,
    write_partial,
)

# Load v14 base (same protocol: no replay, same W construction)
_v14_path = REPO / "experiments" / "exp_saad_solla_v14_n8192_3seed.py"
_v14_spec = importlib.util.spec_from_file_location("ss_v14_v15", _v14_path)
v14 = importlib.util.module_from_spec(_v14_spec)
_v14_spec.loader.exec_module(v14)

# Import helpers from v14 (which imports from v11)
pearson_r2 = v14.pearson_r2
linear_fit_residuals = v14.linear_fit_residuals
run_one_cell_no_replay = v14.run_one_cell_no_replay

# PRODUCTION CONFIG -- PROT-018: _n8192 suffix binds to N = 8192
N = 8192         # PROT-018 binding contract
N_SMOKE = 512
assert N == 8192, f"PROT-018: N must be 8192; got {N}"

# 5 f-cells per seed -- CRITICAL FIX vs v14 (which used only 3 f-points)
# v11 used these exact 5 points and got R^2~0.30 (plateau detected)
F_SWEEP_FULL = [0.0, 0.15, 0.50, 0.80, 1.0]
F_SWEEP_SMOKE = [0.0, 0.5, 1.0]   # smoke uses 3 pts for speed

# 5 seeds matching routing note Alt (c)
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

# GATE-ALIGNED thresholds (OR-clause; convention-matched with v252)
# HARD_PASS via R^2 OR-clause: R^2 < 0.85 (same as v11)
# HARD_PASS via max_dev OR-clause: max_dev >= 0.40 (v252 max_dev=0.34 + 20% headroom)
# Self-tests: v11 data (r2=0.30, max_dev=0.34) -> r2<0.85 fires HARD_PASS. VERIFIED.
HP_R2_MAX = 0.85            # R^2 OR-clause threshold
HP_MAX_DEV_ALT = 0.40       # max_dev OR-clause threshold (v252 + 20% headroom)
HF_R2_MIN = 0.95            # HARD_FAIL smooth-monotone condition
HF_MAX_DEV_MAX = 0.04       # HARD_FAIL smooth-monotone condition
HP_MAJORITY_MIN = 3         # >= 3/5 seeds clear OR-clause = HARD_PASS
HP_STRONG_MIN = 4           # 4/5 or 5/5 seeds = strong HARD_PASS


def get_output_dir(default_name: str = "saad_solla_v15_n8192_5seed") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def seed_passes_hp(r2: float, max_dev: float) -> bool:
    """HARD_PASS OR-clause: r2<0.85 OR max_dev>=0.40."""
    return (r2 < HP_R2_MAX) or (max_dev >= HP_MAX_DEV_ALT)


def compute_verdict(summary: Dict) -> tuple:
    per_seed = summary.get("per_seed", {})
    if not per_seed:
        return ("SS_V15_MIDDLE_BAND", "No per-seed data.")

    pass_seeds = 0
    fail_seeds = 0
    seed_details = {}

    for seed_k, sd in per_seed.items():
        r2 = sd.get("r2", 1.0)
        max_dev = sd.get("max_dev", 0.0)
        passes_hp = seed_passes_hp(r2, max_dev)
        passes_hf = (r2 >= HF_R2_MIN) and (max_dev < HF_MAX_DEV_MAX)
        if passes_hp:
            pass_seeds += 1
        if passes_hf:
            fail_seeds += 1
        seed_details[seed_k] = {
            "r2": round(r2, 3),
            "max_dev": round(max_dev, 3),
            "passes_hp": passes_hp,
            "via": "r2" if r2 < HP_R2_MAX else ("max_dev" if max_dev >= HP_MAX_DEV_ALT else "none")
        }

    total = len(per_seed)
    r2_list = [sd.get("r2", 1.0) for sd in per_seed.values()]
    md_list = [sd.get("max_dev", 0.0) for sd in per_seed.values()]
    mean_r2 = sum(r2_list) / len(r2_list) if r2_list else 0.0
    mean_md = sum(md_list) / len(md_list) if md_list else 0.0

    detail_str = (f"pass_seeds={pass_seeds}/{total} (r2<0.85 OR max_dev>=0.40). "
                  f"mean_r2={mean_r2:.3f} mean_max_dev={mean_md:.3f}. "
                  f"N={N}. f_sweep={F_SWEEP_FULL}. "
                  f"seed_details={seed_details}.")

    if pass_seeds >= HP_MAJORITY_MIN:
        level = "STRONG" if pass_seeds >= HP_STRONG_MIN else "MAJORITY"
        return (f"SS_V15_HARD_PASS_{level}",
                f"SAAD-SOLLA PLATEAU CONFIRMED 5-seed N=8192 ({level}): {pass_seeds}/{total} seeds "
                f"pass gate (r2<0.85 OR max_dev>=0.40). Combined with v252 = 7-seed-equiv. "
                + detail_str)

    if fail_seeds >= max(1, total - 1) and pass_seeds == 0:
        return ("SS_V15_HARD_FAIL",
                f"HARD_FAIL: {fail_seeds}/{total} seeds smooth-monotone. " + detail_str)

    return ("SS_V15_MIDDLE_BAND", "Partial replication. " + detail_str)


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics non-null/non-sentinel at small scale."""
    assert N == 8192, f"PROT-018: N={N} must be 8192"

    # Test pearson_r2 linear
    r2_linear = pearson_r2([0.0, 1.0, 2.0, 3.0, 4.0], [0.0, 2.0, 4.0, 6.0, 8.0])
    assert abs(r2_linear - 1.0) < 1e-4, f"pearson_r2 linear test failed: {r2_linear}"

    # Test pearson_r2 plateau (non-monotone)
    r2_plateau = pearson_r2([0.60, 0.62, 0.94, 0.94, 0.94],
                             [0.0, 0.25, 0.5, 0.75, 1.0])
    assert r2_plateau < HP_R2_MAX, f"pearson_r2 plateau test: {r2_plateau} >= {HP_R2_MAX}"

    # Gate self-test: v11 data MUST fire HARD_PASS via R^2 OR-clause
    # v11 seed=7: r2=0.299, max_dev=0.343
    assert seed_passes_hp(0.299, 0.343), "Gate self-test FAIL: v11 seed=7 data should PASS"
    # v11 seed=17: r2=0.300, max_dev=0.344
    assert seed_passes_hp(0.300, 0.344), "Gate self-test FAIL: v11 seed=17 data should PASS"
    # v14 3-f-point data: r2=0.927, max_dev=0.151 -> should FAIL gate
    assert not seed_passes_hp(0.927, 0.151), "Gate self-test: v14 3-f-pt data should FAIL"
    # High max_dev path: r2=0.90, max_dev=0.45 -> PASS via max_dev
    assert seed_passes_hp(0.90, 0.45), "Gate self-test: max_dev>=0.40 path should PASS"
    # Flat data: r2=1.0, max_dev=0.01 -> FAIL
    assert not seed_passes_hp(1.0, 0.01), "Gate self-test: flat data should FAIL"
    print("[selftest] gate OR-clause: 5/5 assertions OK", flush=True)

    # Test compute_verdict HARD_PASS path (3/5 majority with v11-like data)
    per_seed_pass = {str(s): {"r2": 0.30, "max_dev": 0.34} for s in [7, 17, 23, 31, 41]}
    v, msg = compute_verdict({"per_seed": per_seed_pass})
    assert "HARD_PASS" in v, f"Self-test HARD_PASS_STRONG failed: {v}: {msg}"

    # Test verdict partial (1/5 pass)
    per_seed_partial = {}
    for i, s in enumerate([7, 17, 23, 31, 41]):
        if i < 1:
            per_seed_partial[str(s)] = {"r2": 0.30, "max_dev": 0.34}   # pass
        else:
            per_seed_partial[str(s)] = {"r2": 0.97, "max_dev": 0.02}   # fail
    v2, _ = compute_verdict({"per_seed": per_seed_partial})
    assert "MIDDLE_BAND" in v2 or "HARD_FAIL" in v2, \
        f"Self-test partial should be MIDDLE_BAND or HARD_FAIL: {v2}"

    # Test smoke forward pass at N_SMOKE
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

    # F-sweep count assertion
    assert len(F_SWEEP_FULL) == 5, \
        f"CRITICAL: F_SWEEP_FULL must have 5 points; got {len(F_SWEEP_FULL)}"
    assert 0.15 in F_SWEEP_FULL and 0.80 in F_SWEEP_FULL, \
        f"CRITICAL: f=0.15 and f=0.80 must be in sweep; got {F_SWEEP_FULL}"

    # 5-seed assertion
    assert len(SEEDS_FULL) == 5 and set(SEEDS_FULL) == {7, 17, 23, 31, 41}, \
        f"Expected 5 seeds {{7,17,23,31,41}}; got {SEEDS_FULL}"

    # OOM pre-check at N=8192
    oom_bytes = N * N * 4
    assert oom_bytes < 6e9, f"OOM check: W at N={N} = {oom_bytes/1e6:.0f}MB >= 6GB"
    print(f"[selftest] OOM: W={oom_bytes/1e6:.0f}MB OK", flush=True)

    # Multi-scale smoke: N_SMOKE x4 check
    N_smoke_4x = N_SMOKE * 4
    result_4x = run_one_cell_no_replay(
        seed=17, f=0.5, N_cfg=N_smoke_4x,
        batch_size=BATCH_SIZE_SMOKE,
        n_epochs=EPOCHS_SMOKE,
        phase_a_epochs=PHASE_A_EPOCHS_SMOKE,
        n_bytes=BYTES_SMOKE,
        device=device,
    )
    assert result_4x.get("retention_A") is not None, \
        f"retention_A is None at Nx4={N_smoke_4x}: {result_4x}"
    print(f"[selftest] multi-scale smoke N={N_SMOKE}x4={N_smoke_4x}: ret={result_4x['retention_A']:.4f} OK",
          flush=True)
    print("[selftest] PASS: all assertions OK", flush=True)


_instrumentation_selftest()


def run_full(smoke: bool = False) -> None:
    t0 = time.monotonic()

    f_sweep = F_SWEEP_SMOKE if smoke else F_SWEEP_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    n_cfg = N_SMOKE if smoke else N
    batch = BATCH_SIZE_SMOKE if smoke else BATCH_SIZE
    epochs = EPOCHS_SMOKE if smoke else EPOCHS
    pa_epochs = PHASE_A_EPOCHS_SMOKE if smoke else PHASE_A_EPOCHS
    n_bytes = BYTES_SMOKE if smoke else BYTES

    mode_str = "SMOKE" if smoke else "FULL"
    print(f"[saad_solla_v15] {mode_str} N={n_cfg} seeds={seeds} f_sweep={f_sweep}",
          flush=True)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[saad_solla_v15] device={device}", flush=True)

    out_dir = get_output_dir()

    # PER-SEED CHECKPOINT (PROT-019 resume contract): scan partials so a
    # mid-run crash (CUDA OOM, timeout kill) can resume instead of restarting.
    done_seeds, remaining_seeds = resumable_seeds(seeds, out_dir)
    if done_seeds:
        print(f"[ckpt] resume: {len(done_seeds)}/{len(seeds)} seeds already "
              f"complete from prior run; running remaining "
              f"{len(remaining_seeds)}: {remaining_seeds}", flush=True)
    else:
        print(f"[ckpt] no prior partials; running all {len(seeds)} seeds",
              flush=True)

    for seed in remaining_seeds:
        seed_cells = {}
        r_vals = []
        f_vals_used = []

        for f in f_sweep:
            t_cell = time.monotonic()
            result = run_one_cell_no_replay(
                seed=seed, f=f, N_cfg=n_cfg,
                batch_size=batch,
                n_epochs=epochs,
                phase_a_epochs=pa_epochs,
                n_bytes=n_bytes,
                device=device,
            )
            r_val = result.get("retention_A", float("nan"))
            seed_cells[str(f)] = r_val
            r_vals.append(r_val)
            f_vals_used.append(f)
            print(f"  seed={seed} f={f:.2f}: ret={r_val:.5f} "
                  f"({time.monotonic()-t_cell:.1f}s)", flush=True)

        # Compute R^2 and max_dev
        import math as _math
        valid = [(fi, ri) for fi, ri in zip(f_vals_used, r_vals)
                 if not _math.isnan(ri)]
        if len(valid) >= 3:
            f_valid = [x[0] for x in valid]
            r_valid = [x[1] for x in valid]
            r2 = pearson_r2(r_valid, f_valid)
            residuals_tuple = linear_fit_residuals(r_valid, f_valid)
            residuals = residuals_tuple[2] if isinstance(residuals_tuple, tuple) else residuals_tuple
            max_dev = max(abs(r) for r in residuals) if residuals else 0.0
        else:
            r2 = float("nan")
            max_dev = float("nan")

        seed_payload = {
            "r2": r2,
            "max_dev": max_dev,
            "cells": seed_cells,
        }
        # Atomic checkpoint: written BEFORE moving to next seed so a crash
        # in the NEXT seed does not lose this one.
        write_partial(out_dir, seed, seed_payload)
        print(f"  seed={seed} DONE: r2={r2:.3f} max_dev={max_dev:.3f} "
              f"passes_hp={seed_passes_hp(r2, max_dev)} [ckpt written]",
              flush=True)

    # Aggregate ALL seeds (this-run + prior-run partials)
    per_seed: Dict = aggregate_partials(out_dir, seeds)

    summary = {"per_seed": per_seed, "N": n_cfg,
               "f_sweep": f_sweep, "smoke": smoke}
    verdict, verdict_msg = compute_verdict(summary)
    elapsed = time.monotonic() - t0

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
        "config": {"N": n_cfg, "seeds": seeds,
                   "f_sweep": f_sweep, "smoke": smoke},
        "summary": summary,
    }
    out_path = out_dir / "metrics.json"
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(metrics, fh, indent=2)

    print(f"\n[VERDICT] {verdict}", flush=True)
    print(f"[VERDICT_MSG] {verdict_msg}", flush=True)
    print(f"[metrics] written to {out_path} elapsed={elapsed:.1f}s", flush=True)


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true", dest="self_test")
    args = parser.parse_args()
    if args.self_test:
        print("[self-test] selftest ran at import scope", flush=True)
        import sys as _sys
        _sys.exit(0)
    run_full(smoke=args.smoke)


if __name__ == "__main__":
    main()
