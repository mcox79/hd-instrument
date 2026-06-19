"""T2 CODEBOOK BOUNDARY v2: codebook_c N-scaling at N=8192.

CONTEXT:
  t2_codebook_boundary_v1_n4096 (v267): T2_CB_HARD_PASS. slope=0.20/unit-c at N=4096.
  Codebook-order is a load-bearing axis: more codebook rows = higher retention monotonically.
  v2 extends to N=8192 to test: does the codebook-order transition persist? Does slope change?

SCIENTIFIC QUESTION:
  At N=8192 and M_frac=2.0, does retention increase monotonically with codebook_frac?
  Is the slope >= 0.10 per unit c (same ballpark as N=4096)?

PRE-REGISTERED BANDS:
  Prior: v1 HARD_PASS at N=4096. slope=0.202. mono_frac=0.875 at 3/3 seeds.

  HARD_PASS: slope >= 0.05 at >= 2/3 seeds at N=8192. (reduced from 0.10 because
    larger N may have less per-row discrimination -- calibration probe at this N).
    Interpretation: codebook-order axis persists at N=8192.
  HARD_FAIL: total_var < 0.03 (flat) at N=8192.
    Interpretation: codebook-order axis disappears at N=8192.
  MIDDLE_BAND: slope in [0.01, 0.05] or non-monotone.

FORMULA SELF-TESTS:
  1. N == 8192 (PROT-018 binding).
  2. C at N=8192 Kerdock: C = log2(8192) * 8192 = 13 * 8192 = 106496.
  3. codebook_frac=0.1: n_rows = max(4, int(0.1 * 106496)) = 10649.
  4. Slope: linear regression of ret vs c. Expected 0.05-0.30.
  5. M at M_frac=2.0, N=8192: M=16384.

OOM CHECK:
  M=16384 N=8192: keys=16384*8192*4=536MB. W=268MB. CB at full=106496*8192*4=3.5GB.
  FAIL: full CB is 3.5GB. Use fraction. max(n_rows) = int(0.8 * 106496) = 85196 rows.
  85196*8192*4=2.8GB still large. Use c_fracs_max=0.5: 53248*8192*4=1.74GB. Under 6GB. OK.
  Restrict c_fracs to max 0.5 at N=8192 to stay under memory.

TIMEOUT ESTIMATE:
  5 c_fracs x 3 seeds = 15 cells. Per cell: store M=16384 + retrieval.
  At N=8192: ~2s per cell. Total: 15*2=30s. Safety: ceil(1.5*30*8)=360s.
  _n8192 floor=21600. timeout_s=21600.

N-suffix: _n8192 -> production N = 8192 (PROT-018 binding).
Anchor: t2_codebook_boundary_v2_n8192
Queue: overnight_queue (GPU; N=8192 Kerdock, c_frac sweep, 5 pts x 3 seeds)
Pre-reg: prereqs/2026-05-28_t2_codebook_boundary_v2_n8192.md
Parent: t2_codebook_boundary_v1_n4096 (v267 HARD_PASS; N-scaling next step)
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

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

# Load t2_codebook_boundary_v1 for run_one_seed
_t2_path = REPO / "experiments" / "exp_t2_codebook_boundary_v1_n4096.py"
_t2_spec = importlib.util.spec_from_file_location("t2v1_v2n8k", _t2_path)
t2v1 = importlib.util.module_from_spec(_t2_spec)
_t2_spec.loader.exec_module(t2v1)

run_one_seed_t2 = t2v1.run_one_seed

# PRODUCTION CONFIG -- PROT-018: _n8192 suffix binds to N = 8192
N_FULL  = 8192
N_SMOKE = 1024
assert N_FULL == 8192, f"PROT-018: N_FULL must be 8192; got {N_FULL}"

M_FRAC = 2.0
BETA   = 32.0

# Restricted c_fracs (max 0.5 to stay under OOM at N=8192)
C_FRACS_FULL  = [0.05, 0.1, 0.2, 0.35, 0.5]
C_FRACS_SMOKE = [0.05, 0.2, 0.5]

SEEDS_FULL  = [7, 17, 23]
SEEDS_SMOKE = [17]

N_PROBE = 200

# Pre-registered thresholds
HP_SLOPE_MIN       = 0.05    # slope >= 0.05 per unit c (relaxed from v1's 0.10; calibration)
HP_MONOTONE_FRAC   = 0.50    # 50% of consecutive pairs non-decreasing
HF_FLAT_MAX_VAR    = 0.03    # max_ret - min_ret < 0.03 = flat = HARD_FAIL
HP_SEEDS_MIN       = 2


def get_output_dir(default_name: str = "t2_codebook_boundary_v2_n8192") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def seed_passes_hp(cell: Dict) -> bool:
    return (cell.get("slope", 0.0) >= HP_SLOPE_MIN and
            cell.get("total_var", 0.0) >= HF_FLAT_MAX_VAR and
            cell.get("mono_frac", 0.0) >= HP_MONOTONE_FRAC)


def compute_verdict(summary: Dict) -> Tuple[str, str]:
    cells = summary.get("cells", [])
    if not cells:
        return ("T2V2_INCONCLUSIVE", "No cells.")

    pass_seeds = sum(1 for c in cells if seed_passes_hp(c))
    total_seeds = len(cells)

    slopes = [c.get("slope", 0.0) for c in cells]
    total_vars = [c.get("total_var", 0.0) for c in cells]
    mean_slope = sum(slopes) / len(slopes)
    mean_var   = sum(total_vars) / len(total_vars)

    detail = (f"pass_seeds={pass_seeds}/{total_seeds} "
              f"mean_slope={mean_slope:.3f} mean_total_var={mean_var:.3f} "
              f"M_frac={M_FRAC} beta={BETA} N={summary.get('N', N_FULL)} "
              f"HP_slope={HP_SLOPE_MIN}")

    flat_seeds = sum(1 for c in cells if c.get("total_var", 0.0) < HF_FLAT_MAX_VAR)
    if flat_seeds >= 2:
        return ("T2V2_HARD_FAIL",
                f"CODEBOOK_AXIS_FLAT_N8192: no codebook-order sensitivity. " + detail)

    if pass_seeds >= HP_SEEDS_MIN:
        return ("T2V2_HARD_PASS",
                f"CODEBOOK_ORDER_TRANSITION_N8192: slope={mean_slope:.3f}. " + detail)

    return ("T2V2_MIDDLE_BAND", f"WEAK_CODEBOOK_SENSITIVITY: " + detail)


def _instrumentation_selftest() -> None:
    assert N_FULL == 8192, f"PROT-018: N_FULL must be 8192; got {N_FULL}"
    # Formula self-tests
    C_8192 = int(math.log2(8192)) * 8192
    assert C_8192 == 106496, f"C at N=8192 should be 106496; got {C_8192}"
    # Verdict gates
    fake_hp = [{"slope": 0.15, "total_var": 0.20, "mono_frac": 0.8} for _ in range(3)]
    v, _ = compute_verdict({"cells": fake_hp, "N": N_FULL})
    assert "HARD_PASS" in v, f"HARD_PASS gate: {v}"
    fake_hf = [{"slope": 0.01, "total_var": 0.01, "mono_frac": 0.5} for _ in range(3)]
    vf, _ = compute_verdict({"cells": fake_hf, "N": N_FULL})
    assert "HARD_FAIL" in vf, f"HARD_FAIL gate: {vf}"
    # Smoke cell at N_SMOKE (log2=10 OK for Kerdock)
    device = torch.device("cpu")
    cell = run_one_seed_t2(N_SMOKE, M_FRAC, BETA, C_FRACS_SMOKE, 17, device)
    assert "slope" in cell, f"slope missing: {list(cell.keys())}"
    # 4x smoke: N=4096 (log2=12 OK for Kerdock)
    cell4 = run_one_seed_t2(N_SMOKE * 4, M_FRAC, BETA, C_FRACS_SMOKE, 17, device)
    assert "slope" in cell4, f"4x slope missing"
    print(f"[selftest] t2_codebook_boundary_v2_n8192 PASS slope_smoke={cell.get('slope')}", flush=True)


_instrumentation_selftest()


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true", dest="self_test")
    args = parser.parse_args()
    if args.self_test:
        sys.exit(0)

    device_str = "cuda" if torch.cuda.is_available() else "cpu"
    device = torch.device(device_str)
    smoke = args.smoke

    N_cfg = N_SMOKE if smoke else N_FULL
    c_fracs = C_FRACS_SMOKE if smoke else C_FRACS_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL

    print(f"[run] t2_codebook_boundary_v2_n8192 smoke={smoke} N={N_cfg} M_frac={M_FRAC} seeds={seeds}", flush=True)
    t0 = time.time()

    all_cells = []
    for seed in seeds:
        print(f"\n  [seed={seed}]", flush=True)
        cell = run_one_seed_t2(N_cfg, M_FRAC, BETA, c_fracs, seed, device)
        all_cells.append(cell)
        print(f"  seed={seed} slope={cell.get('slope')} total_var={cell.get('total_var')} ({time.time()-t0:.1f}s)", flush=True)

    verdict, verdict_msg = compute_verdict({"cells": all_cells, "N": N_cfg})
    elapsed = round(time.time() - t0, 2)

    summary = {
        "anchor": "t2_codebook_boundary_v2_n8192", "N": N_cfg, "smoke": smoke,
        "M_frac": M_FRAC, "c_fracs": c_fracs, "seeds": seeds,
        "cells": all_cells, "verdict": verdict, "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
    }
    out_dir = get_output_dir()
    out_path = out_dir / "metrics.json"
    with open(out_path, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"\n[verdict] {verdict}", flush=True)
    print(f"[verdict_msg] {verdict_msg}", flush=True)
    print(f"[elapsed] {elapsed}s", flush=True)
    print(f"[output] {out_path}", flush=True)


if __name__ == "__main__":
    main()
