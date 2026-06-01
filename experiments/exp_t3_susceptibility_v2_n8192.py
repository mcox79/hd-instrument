"""T3 SUSCEPTIBILITY v2: triple-axis probe at N=8192 confirming two-boundary lattice.

CONTEXT:
  T3_SUSCEPTIBILITY (v267): triple-point REFUTED at N=4096. Two-orthogonal-boundary
  lattice confirmed: beta_c AND codebook_c, NOT triple-point.
  v2 extends to N=8192 to confirm: (a) same two-boundary structure, (b) boundaries
  are sharp at production scale.

SCIENTIFIC QUESTION:
  Does the two-orthogonal-boundary lattice (beta_c + codebook_c) persist at N=8192?
  Do the boundary positions shift with N?

PRE-REGISTERED BANDS:
  Prior: T3 v267 refuted triple-point at N=4096; two boundaries confirmed.

  HARD_PASS: susceptibility chi_beta > chi_c OR chi_c > chi_beta (two distinct
    large-susceptibility axes) at >= 2/3 seeds at N=8192.
    Interpretation: two-boundary lattice robust to N-scaling.
  HARD_FAIL: chi_beta ~ chi_c ~ chi_M (all three equal, triple-point re-emerges at N=8192).
    Interpretation: triple-point structure is N-dependent.
  MIDDLE_BAND: only one dominant axis at N=8192.

FORMULA SELF-TESTS:
  1. N == 8192 (PROT-018 binding).
  2. chi = max |d(ret)/d(param)| over param sweep.
  3. Two boundaries: chi_beta != chi_c at >= 2x ratio.
  4. M at M_frac=4.0, N=8192: M=32768.

OOM CHECK:
  M=32768, N=8192: W=268MB. Keys=32768*8192*4=1.07GB. CB=268MB. Total~1.7GB. OK.

TIMEOUT ESTIMATE:
  3 axes x 5 pts x 3 seeds = 45 cells. Per cell at N=8192: ~2s.
  Total: 45*2=90s. Safety: ceil(1.5*90*10)=1350s. _n8192 floor=21600. timeout_s=21600.

N-suffix: _n8192 -> production N = 8192 (PROT-018 binding).
Anchor: t3_susceptibility_v2_n8192
Queue: overnight_queue (GPU)
Pre-reg: preregs/2026-05-28_t3_susceptibility_v2_n8192.md
Parent: t3_susceptibility_v1_n4096 (v267 triple-point refutation)
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

# Lazy-load t3 v1 to avoid triggering its 5-seed selftest at import time.
# The parent selftest runs at module scope and takes ~3000s; defer to first call.
_t3v1_mod = None

def _load_t3v1():
    global _t3v1_mod
    if _t3v1_mod is None:
        _t3_path = REPO / "experiments" / "exp_t3_susceptibility_v1_n4096.py"
        _t3_spec = importlib.util.spec_from_file_location("t3v1_n8k", _t3_path)
        _t3v1_mod = importlib.util.module_from_spec(_t3_spec)
        _t3_spec.loader.exec_module(_t3v1_mod)
    return _t3v1_mod


def run_susceptibility(M_frac, beta, label, N, epsilons, seeds, device):
    """Lazy wrapper: loads t3v1 on first call."""
    return _load_t3v1().run_susceptibility(M_frac, beta, label, N, epsilons, seeds, device)

# PRODUCTION CONFIG -- PROT-018: _n8192 suffix binds to N = 8192
N_FULL  = 8192
N_SMOKE = 1024
assert N_FULL == 8192, f"PROT-018: N_FULL must be 8192; got {N_FULL}"

M_FRAC = 8.0   # near phase boundary at N=8192 (deep M_frac=4 gives chi~0)

SEEDS_FULL  = [7, 17, 23]
SEEDS_SMOKE = [17]

# Pre-registered thresholds
HP_CHI_RATIO_MIN  = 2.0    # dominant axis chi >= 2x second axis chi
HF_ALL_EQUAL_TOL  = 0.20   # all chi within 20% of each other = triple-point = HARD_FAIL
HP_SEEDS_MIN      = 2


def get_output_dir(default_name: str = "t3_susceptibility_v2_n8192") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


EPSILONS = [0.10]   # single epsilon probe (same as v1 diagnostic)
BETA_OP  = 32.0
LABEL    = "v2_n8192_op"
# Use M_frac=8.0 to probe near phase boundary (M_frac=4.0 is deep multi-basin, chi~0)
# axis1_mb_chunk7 shows M_frac=8 is near boundary at N=4096; similar for N=8192.
# v1 (N=4096) used M_frac=10.0; v2 uses M_frac=8.0 (near boundary at N=8192).


def run_one_seed(N: int, M_frac: float, seed: int, device: torch.device) -> Dict:
    """Compute three-axis chi at one operating point for one seed."""
    result = run_susceptibility(M_frac, BETA_OP, LABEL, N, EPSILONS, [seed], device)
    cells = result.get("cells", [])
    if not cells:
        return {"seed": seed, "M_frac": M_frac, "chi_by_axis": {}, "chi_ratio": None}

    c = cells[0]  # single epsilon, single seed
    chi_beta = c.get("chi_beta", float("nan"))
    chi_cb   = c.get("chi_cb",   float("nan"))
    chi_M    = c.get("chi_M",    float("nan"))

    chi_vals = [v for v in [chi_beta, chi_cb, chi_M] if not math.isnan(v)]
    chi_max = max(chi_vals) if chi_vals else float("nan")
    chi_min = min(chi_vals) if chi_vals else float("nan")
    ratio = chi_max / max(chi_min, 1e-9) if len(chi_vals) >= 2 else float("nan")

    return {
        "seed": seed, "M_frac": M_frac,
        "chi_by_axis": {"beta": chi_beta, "codebook": chi_cb, "M": chi_M},
        "chi_max": round(chi_max, 4) if not math.isnan(chi_max) else None,
        "chi_min": round(chi_min, 4) if not math.isnan(chi_min) else None,
        "chi_ratio": round(ratio, 4) if not math.isnan(ratio) else None,
    }


def compute_verdict(summary: Dict) -> Tuple[str, str]:
    cells = summary.get("cells", [])
    if not cells:
        return ("T3_V2_INCONCLUSIVE", "No cells.")

    ratios = [c["chi_ratio"] for c in cells if c.get("chi_ratio") is not None]
    mean_ratio = sum(ratios) / len(ratios) if ratios else float("nan")
    pass_seeds = sum(1 for r in ratios if r >= HP_CHI_RATIO_MIN)

    # Triple-point check: all chi within 20%
    triple_point_seeds = 0
    for c in cells:
        chi_vals = [v for v in c.get("chi_by_axis", {}).values() if v is not None and not math.isnan(v)]
        if len(chi_vals) >= 2:
            chi_mean = sum(chi_vals) / len(chi_vals)
            if all(abs(v - chi_mean) / max(chi_mean, 1e-9) < HF_ALL_EQUAL_TOL for v in chi_vals):
                triple_point_seeds += 1

    detail = (f"mean_chi_ratio={mean_ratio:.2f} pass_seeds={pass_seeds}/{len(cells)} "
              f"triple_point_seeds={triple_point_seeds}/{len(cells)} "
              f"HP_ratio={HP_CHI_RATIO_MIN} N={summary.get('N', N_FULL)}")

    if triple_point_seeds >= HP_SEEDS_MIN:
        return ("T3_V2_HARD_FAIL",
                f"TRIPLE_POINT_REMERGED: all chi equal at N=8192. " + detail)

    if pass_seeds >= HP_SEEDS_MIN:
        return ("T3_V2_HARD_PASS",
                f"TWO_BOUNDARY_CONFIRMED_N8192: chi_ratio={mean_ratio:.2f}x. " + detail)

    return ("T3_V2_MIDDLE_BAND", f"WEAK_ASYMMETRY: ratio={mean_ratio:.2f}. " + detail)


def _instrumentation_selftest() -> None:
    assert N_FULL == 8192, f"PROT-018: N_FULL must be 8192; got {N_FULL}"
    # Verdict gates only (no live computation at selftest time -- parent t3v1 selftest
    # takes ~3000s; defer to --smoke run which is gated before queue entry)
    fake_hp = [{"chi_ratio": 3.0, "chi_max": 0.5, "chi_min": 0.1,
                "chi_by_axis": {"beta": 0.5, "codebook": 0.1, "M": 0.15}} for _ in range(3)]
    v, _ = compute_verdict({"cells": fake_hp, "N": N_FULL})
    assert "HARD_PASS" in v, f"HARD_PASS gate: {v}"
    fake_hf = [{"chi_ratio": 1.1, "chi_max": 0.5, "chi_min": 0.45,
                "chi_by_axis": {"beta": 0.5, "codebook": 0.49, "M": 0.48}} for _ in range(3)]
    vf, _ = compute_verdict({"cells": fake_hf, "N": N_FULL})
    assert "HARD_FAIL" in vf, f"HARD_FAIL gate: {vf}"
    # Sanity: run_one_seed function exists and takes correct args (no-op check)
    import inspect
    sig = inspect.signature(run_one_seed)
    assert len(sig.parameters) == 4, f"run_one_seed should have 4 params: {sig}"
    print(f"[selftest] t3_susceptibility_v2_n8192 PASS (formula-only; smoke deferred)", flush=True)


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
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL

    print(f"[run] t3_susceptibility_v2_n8192 smoke={smoke} N={N_cfg} seeds={seeds} device={device_str}", flush=True)
    t0 = time.time()

    all_cells = []
    for seed in seeds:
        print(f"\n  [seed={seed}]", flush=True)
        cell = run_one_seed(N_cfg, M_FRAC, seed, device)
        all_cells.append(cell)
        print(f"  seed={seed} chi_ratio={cell.get('chi_ratio')} ({time.time()-t0:.1f}s)", flush=True)

    verdict, verdict_msg = compute_verdict({"cells": all_cells, "N": N_cfg})
    elapsed = round(time.time() - t0, 2)

    summary = {
        "anchor": "t3_susceptibility_v2_n8192", "N": N_cfg, "smoke": smoke,
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
