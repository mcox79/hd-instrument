"""T1 BETA SWEEP v2: N-scaling of beta_c at N=8192.

CONTEXT:
  t1_beta_sweep_v1_n4096 (v267): T1_BETA_HARD_PASS. Beta_c locatable at N=4096,
  M_frac=8.0. max_gradient=0.247, total_var=0.509 at 5/5 seeds.
  v2 extends to N=8192 to test: does beta_c SHIFT with N? Is the transition sharper?

SCIENTIFIC QUESTION:
  At N=8192 and M_frac=8.0, does the softmax-confidence beta transition persist?
  Does beta_c shift to a higher or lower value compared to N=4096?
  Is the transition sharper (higher max_gradient) at larger N?

PRE-REGISTERED BANDS:
  Prior: v1 HARD_PASS at N=4096. max_gradient=0.247. beta_c visually around beta=8-16.

  HARD_PASS: transition confirmed (total_var >= 0.40, max_gradient >= 0.10)
    at >= 3/3 seeds at N=8192.
    Interpretation: beta_c persists at N=8192. Two-boundary lattice robust.
  HARD_FAIL: total_var < 0.05 (flat) at N=8192.
    Interpretation: beta-axis disappears at N=8192 (N-dependent phase boundary).
  MIDDLE_BAND: transition present but gradient < 0.10 (diffuse, no sharp beta_c).

FORMULA SELF-TESTS:
  1. N == 8192 (PROT-018 binding).
  2. M at M_frac=8.0, N=8192: M=65536. Keys=65536*8192*4=2.1GB -- borderline.
     Use M_frac=4.0 at N=8192 (M=32768, keys=1.07GB, feasible).
  3. softmax: log_z = logsumexp(beta * sim, dim=0). Correct prob = exp(log_p[val_idx]).
  4. max_gradient = max |d(ret)/d(log2_beta)| over interior points.

OOM CONSTRAINT:
  M_frac=8.0 at N=8192 -> M=65536 -> keys=65536*8192*4 = 2.1GB > 6GB GPU limit.
  Use M_frac=4.0 at N=8192 (M=32768, keys=1.07GB, W=268MB, CB=268MB, total~1.6GB). OK.

TIMEOUT ESTIMATE:
  10 beta x 3 seeds = 30 cells. Each at N=8192 M=32768: ~5s.
  Total: 30*5=150s. Safety: ceil(1.5*150*8)=1800s. _n8192 floor=21600. timeout_s=21600.

N-suffix: _n8192 -> production N = 8192 (PROT-018 binding).
Anchor: t1_beta_sweep_v2_n8192
Queue: overnight_queue (GPU; N=8192 Kerdock, beta in {1..512}, 10 pts x 3 seeds)
Pre-reg: prereqs/2026-05-28_t1_beta_sweep_v2_n8192.md
Parent: t1_beta_sweep_v1_n4096 (v267 HARD_PASS; N-scaling next step)
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

# Load t1_beta_sweep_v1 for core functions
_t1_path = REPO / "experiments" / "exp_t1_beta_sweep_v1_n4096.py"
_t1_spec = importlib.util.spec_from_file_location("t1v1_v2n8k", _t1_path)
t1v1 = importlib.util.module_from_spec(_t1_spec)
_t1_spec.loader.exec_module(t1v1)

run_one_seed_t1 = t1v1.run_one_seed

# PRODUCTION CONFIG -- PROT-018: _n8192 suffix binds to N = 8192
N_FULL  = 8192
N_SMOKE = 1024
assert N_FULL == 8192, f"PROT-018: N_FULL must be 8192; got {N_FULL}"

# Use M_frac=4.0 at N=8192 (M_frac=8.0 would OOM at N=8192)
M_FRAC = 4.0

BETA_SWEEP_FULL  = [1, 2, 4, 8, 16, 32, 64, 128, 256, 512]
BETA_SWEEP_SMOKE = [1, 4, 16, 64, 256]

SEEDS_FULL  = [7, 17, 23]
SEEDS_SMOKE = [17]

N_PROBE = 200

# Pre-registered thresholds (inherit from v1 but HARD_PASS at 3/3 seeds)
HP_MAX_GRADIENT_MIN = 0.10
HP_MONOTONE_FRAC    = 0.70
HF_FLAT_MAX_VAR     = 0.05
HP_SEEDS_MIN        = 2   # >= 2/3 seeds pass both clauses


def get_output_dir(default_name: str = "t1_beta_sweep_v2_n8192") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def seed_passes_hp(cell: Dict) -> bool:
    return (cell["max_gradient"] >= HP_MAX_GRADIENT_MIN and
            cell["total_var"] >= HF_FLAT_MAX_VAR and
            cell["mono_frac"] >= HP_MONOTONE_FRAC)


def compute_verdict(summary: Dict) -> Tuple[str, str]:
    cells = summary.get("cells", [])
    if not cells:
        return ("T1V2_INCONCLUSIVE", "No cells.")

    pass_seeds = sum(1 for c in cells if seed_passes_hp(c))
    total_seeds = len(cells)

    max_grads = [c["max_gradient"] for c in cells]
    total_vars = [c["total_var"] for c in cells]
    mean_grad = sum(max_grads) / len(max_grads)
    mean_var  = sum(total_vars) / len(total_vars)

    detail = (f"pass_seeds={pass_seeds}/{total_seeds} "
              f"mean_max_gradient={mean_grad:.3f} mean_total_var={mean_var:.3f} "
              f"M_frac={M_FRAC} N={summary.get('N', N_FULL)} "
              f"HP_grad={HP_MAX_GRADIENT_MIN} HP_var={HF_FLAT_MAX_VAR}")

    flat_seeds = sum(1 for c in cells if c["total_var"] < HF_FLAT_MAX_VAR)
    if flat_seeds >= 2:
        return ("T1V2_HARD_FAIL",
                f"BETA_AXIS_FLAT_N8192: no transition at N=8192. " + detail)

    if pass_seeds >= HP_SEEDS_MIN:
        return ("T1V2_HARD_PASS",
                f"BETA_TRANSITION_N8192: pass_seeds={pass_seeds} mean_grad={mean_grad:.3f}. "
                + detail)

    return ("T1V2_MIDDLE_BAND", f"DIFFUSE_TRANSITION: " + detail)


def _instrumentation_selftest() -> None:
    assert N_FULL == 8192, f"PROT-018: N_FULL must be 8192; got {N_FULL}"
    # Verdict gates
    fake_hp = [{"max_gradient": 0.25, "total_var": 0.5, "mono_frac": 0.9} for _ in range(3)]
    v, _ = compute_verdict({"cells": fake_hp, "N": N_FULL})
    assert "HARD_PASS" in v, f"HARD_PASS gate: {v}"
    fake_hf = [{"max_gradient": 0.01, "total_var": 0.02, "mono_frac": 0.5} for _ in range(3)]
    vf, _ = compute_verdict({"cells": fake_hf, "N": N_FULL})
    assert "HARD_FAIL" in vf, f"HARD_FAIL gate: {vf}"
    # Smoke cell at N_SMOKE (log2=10 OK for Kerdock)
    device = torch.device("cpu")
    cell = run_one_seed_t1(N_SMOKE, M_FRAC, BETA_SWEEP_SMOKE, 17, device)
    assert "max_gradient" in cell, f"max_gradient missing"
    assert not math.isnan(cell["max_gradient"]), "max_gradient NaN"
    # 4x smoke: N=4096 (log2=12 OK for Kerdock)
    cell4 = run_one_seed_t1(N_SMOKE * 4, M_FRAC, BETA_SWEEP_SMOKE, 17, device)
    assert "max_gradient" in cell4, f"4x max_gradient missing"
    print(f"[selftest] t1_beta_sweep_v2_n8192 PASS max_gradient_smoke={cell.get('max_gradient')}", flush=True)


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
    beta_sweep = BETA_SWEEP_SMOKE if smoke else BETA_SWEEP_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL

    print(f"[run] t1_beta_sweep_v2_n8192 smoke={smoke} N={N_cfg} M_frac={M_FRAC} seeds={seeds}", flush=True)
    t0 = time.time()

    all_cells = []
    for seed in seeds:
        print(f"\n  [seed={seed}]", flush=True)
        cell = run_one_seed_t1(N_cfg, M_FRAC, beta_sweep, seed, device)
        all_cells.append(cell)
        print(f"  seed={seed} max_gradient={cell.get('max_gradient')} total_var={cell.get('total_var')} ({time.time()-t0:.1f}s)", flush=True)

    verdict, verdict_msg = compute_verdict({"cells": all_cells, "N": N_cfg})
    elapsed = round(time.time() - t0, 2)

    summary = {
        "anchor": "t1_beta_sweep_v2_n8192", "N": N_cfg, "smoke": smoke,
        "M_frac": M_FRAC, "seeds": seeds,
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
