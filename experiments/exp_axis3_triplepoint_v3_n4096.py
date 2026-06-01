"""AXIS-3 triple-point v3: broader M x beta grid sweep at N=4096.

CONTEXT:
  axis3_triplepoint_v2_n4096 (completed on remote_cpu_queue): tested 3 operating points,
  found sign_divergence=False at all points. MIDDLE_BAND verdict.
  v3 (THIS): broader grid with 6 operating points to find any sign_divergence region.
  Expands from 3 to 6 (M_frac, beta) pairs based on v2 evidence:
  - v2 found max|delta_ret|=0.25 in M_plus direction at M_frac=10, beta=8.
  - Sign divergence requires BOTH positive AND negative responses.
  - Test at lower M_frac (near capacity) and higher beta (stronger separation).

SCIENTIFIC QUESTION:
  In the M x beta parameter space at N=4096, does any operating point show
  sign_divergence=True (competing attractor basins)?

PRE-REGISTERED BANDS:
  Prior: v2 N=4096 max|delta_ret|=0.25 at (M_frac=10, beta=8).
  v3 probes 6 points distributed across M x beta plane.

  HARD_PASS: sign_divergence=True at >= 1 operating point
    AND max|delta_ret| >= 0.15 with opposing-sign responses.
    Interpretation: triple-point or multi-phase saddle found.
  HARD_FAIL: max|delta_ret| < 0.05 at ALL 6 tested points.
    Interpretation: substrate completely insensitive to perturbations.
  MIDDLE_BAND: max|delta_ret| >= 0.05 but sign_divergence=False at all points.

FORMULA SELF-TESTS:
  1. N == 4096 (PROT-018 binding).
  2. sign_divergence: pos_dirs >= 1 AND neg_dirs >= 1 at same operating point.
  3. delta_ret = ret_perturbed - ret_base. Range: [-1, 1].
  4. 6 operating points: (M_frac, beta) pairs distributed in high-signal region.

OOM CHECK:
  W float32 at N=4096: 64MB. 6 operating points sequential (no simultaneous). OK.

TIMEOUT ESTIMATE:
  v2 elapsed=9.1s for 3 points. v3: 6 points. Scale: 2x -> ~18s.
  Safety: ceil(1.5 * 18 * 5) = 135s. Floor 14400. timeout_s = 14400.

N-suffix: _n4096 -> production N = 4096 (PROT-018 binding).
Anchor: axis3_triplepoint_v3_n4096
Queue: remote_cpu_queue (CPU; N=4096 Kerdock; 6-point triple-point grid)
Pre-reg: preregs/2026-05-29_axis3_triplepoint_v3_n4096.md
Parent: axis3_triplepoint_v2_n4096 (MIDDLE_BAND sign_divergence=False)
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

# Load v2 for run_one_operating_point
_v2_path = REPO / "experiments" / "exp_axis3_triplepoint_v2_n4096.py"
_v2_spec = importlib.util.spec_from_file_location("axis3v2_v3", _v2_path)
_v2_mod = importlib.util.module_from_spec(_v2_spec)
_v2_spec.loader.exec_module(_v2_mod)

# PRODUCTION CONFIG -- PROT-018: _n4096 suffix binds to N = 4096
N_FULL  = 4096
N_SMOKE = 1024
assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

# 6 operating points: (M_frac, beta) pairs in high-signal region
OPERATING_POINTS_FULL = [
    (4.0,  8.0),   # v1's INTERIOR point (near transition from v254)
    (8.0,  4.0),   # lower beta, mid-overcapacity
    (4.0, 16.0),   # higher beta, near-capacity
    (12.0, 8.0),   # v2's point (a), near transition zone
    (8.0, 16.0),   # higher beta + mid-overcapacity
    (4.0, 32.0),   # strong beta at near-capacity
]
OPERATING_POINTS_SMOKE = [(4.0, 8.0), (8.0, 4.0)]  # 2 smoke points

SEEDS_FULL  = [7, 17, 23]
SEEDS_SMOKE = [17]

N_DIRECTIONS = 6   # perturbation directions (same as v1/v2)
N_EPS        = 5   # epsilon values per direction

# Pre-registered thresholds
HP_DELTA_MIN    = 0.15   # max|delta_ret| >= 0.15
HP_SIGNEDGE_MIN = 1      # >= 1 operating point with sign divergence
HF_DELTA_MAX    = 0.05   # max|delta_ret| < 0.05 = hard fail


def get_output_dir(default_name: str = "axis3_triplepoint_v3_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def run_one_operating_point(N: int, M_frac: float, beta: float, seeds: List[int]) -> Dict:
    """Run perturbation analysis at (M_frac, beta) using v2 infrastructure.

    v2 signature: run_one_operating_point(M_frac, base_beta, N, directions, epsilons, seeds, device)
    """
    run_fn = getattr(_v2_mod, "run_one_operating_point", None)
    if run_fn is None:
        raise RuntimeError("v2 missing run_one_operating_point")

    # v2's directions and epsilons (from v2 config)
    directions = getattr(_v2_mod, "DIRECTIONS", None) or getattr(_v2_mod, "directions", None)
    epsilons   = getattr(_v2_mod, "EPSILONS", None) or getattr(_v2_mod, "epsilons", None)

    if directions is None:
        directions = getattr(_v2_mod, "DIRECTIONS",
                             ["M_plus", "M_minus", "beta_up", "beta_down",
                              "W_noise", "M_partial_swap"])
    if epsilons is None:
        epsilons = getattr(_v2_mod, "EPSILONS_FULL", [0.02, 0.05, 0.10, 0.20, 0.40])

    device = torch.device("cpu")
    return run_fn(M_frac=M_frac, base_beta=beta, N=N,
                  directions=directions, epsilons=epsilons,
                  seeds=seeds, device=device)


def compute_verdict(summary: Dict) -> Tuple[str, str]:
    """Compute verdict from list of operating-point result dicts (each has 'cells' list)."""
    results = summary.get("results", [])
    if not results:
        return ("AXIS3_V3_INCONCLUSIVE", "No results.")

    # Analyze each operating point: check sign divergence in cells
    n_sign_div = 0
    global_max_delta = 0.0

    for r in results:
        cells = r.get("cells", [])
        if not cells:
            continue
        deltas = [abs(c.get("delta_ret", 0.0)) for c in cells]
        max_d = max(deltas) if deltas else 0.0
        global_max_delta = max(global_max_delta, max_d)

        # Sign divergence: any direction with delta > 0 AND any with delta < 0 at same eps
        for eps_val in set(c.get("epsilon", 0) for c in cells):
            cells_eps = [c for c in cells if c.get("epsilon") == eps_val]
            pos_dirs = sum(1 for c in cells_eps if c.get("delta_ret", 0) >= 0.05)
            neg_dirs = sum(1 for c in cells_eps if c.get("delta_ret", 0) <= -0.05)
            if pos_dirs >= 1 and neg_dirs >= 1:
                n_sign_div += 1
                break

    N = summary.get("N", N_FULL)
    detail = (f"n_sign_div={n_sign_div}/{len(results)} max_abs_delta={global_max_delta:.4f} "
              f"HP_delta={HP_DELTA_MIN} HF_delta={HF_DELTA_MAX} N={N}")

    if global_max_delta < HF_DELTA_MAX:
        return ("AXIS3_V3_HARD_FAIL",
                f"ALL_INSENSITIVE: max|delta|={global_max_delta:.4f} < {HF_DELTA_MAX}. " + detail)

    if n_sign_div >= HP_SIGNEDGE_MIN and global_max_delta >= HP_DELTA_MIN:
        return ("AXIS3_V3_HARD_PASS",
                f"SIGN_DIVERGENCE FOUND at {n_sign_div} operating points. " + detail)

    return ("AXIS3_V3_MIDDLE_BAND",
            f"PARTIAL: n_sign_div={n_sign_div} max_delta={global_max_delta:.4f}. " + detail)


def _instrumentation_selftest() -> None:
    assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

    # Import chain
    assert _v2_mod is not None, "v2 import failed"
    assert hasattr(_v2_mod, "run_one_operating_point"), "v2 missing run_one_operating_point"

    # Formula tests
    assert OPERATING_POINTS_FULL[0] == (4.0, 8.0), "First operating point check"

    # Verdict tests: pass dicts with cells list (current compute_verdict format)
    # HP: one operating point with sign divergence (pos and neg dirs at same epsilon)
    cells_hp = [
        {"delta_ret": 0.20, "epsilon": 0.10},
        {"delta_ret": -0.20, "epsilon": 0.10},
    ]
    results_hp = [{"cells": cells_hp}]
    v, msg = compute_verdict({"results": results_hp, "N": N_FULL})
    assert "HARD_PASS" in v, f"Expected HP: {v} | {msg}"

    # HF: all deltas < HF_DELTA_MAX (0.05)
    cells_hf = [{"delta_ret": 0.02, "epsilon": 0.10}, {"delta_ret": 0.01, "epsilon": 0.10}]
    results_hf = [{"cells": cells_hf} for _ in range(6)]
    v_hf, _ = compute_verdict({"results": results_hf, "N": N_FULL})
    assert "HARD_FAIL" in v_hf, f"Expected HF: {v_hf}"

    # Live smoke cell at N=1024
    result = run_one_operating_point(N_SMOKE, 4.0, 8.0, [17])
    assert "cells" in result, f"missing cells key: {list(result.keys())}"
    cells = result["cells"]
    assert len(cells) > 0, "cells is empty (filter bug)"
    deltas = [abs(c.get("delta_ret", 0.0)) for c in cells]
    delta = max(deltas) if deltas else 0.0
    assert delta >= 0.0, f"max_abs_delta negative: {delta}"

    # 4x smoke: N=4096
    result4 = run_one_operating_point(N_SMOKE * 4, 4.0, 8.0, [17])
    assert "cells" in result4, f"4x missing cells: {list(result4.keys())}"
    cells4 = result4["cells"]
    assert len(cells4) > 0, "4x cells empty"

    print(f"[selftest] axis3_triplepoint_v3_n4096 PASS "
          f"n_cells_smoke={len(cells)} delta_smoke={delta:.4f}", flush=True)


_instrumentation_selftest()


def run_full(smoke: bool = False) -> None:
    t0 = time.monotonic()

    op_points = OPERATING_POINTS_SMOKE if smoke else OPERATING_POINTS_FULL
    seeds     = SEEDS_SMOKE if smoke else SEEDS_FULL
    N_cfg     = N_SMOKE if smoke else N_FULL

    print(f"axis3_triplepoint_v3_n4096 mode={'SMOKE' if smoke else 'FULL'} "
          f"N={N_cfg} operating_points={op_points} seeds={seeds}", flush=True)

    all_results = []

    for M_frac, beta in op_points:
        print(f"\n== (M_frac={M_frac}, beta={beta}) ==", flush=True)
        t_op = time.monotonic()
        result = run_one_operating_point(N_cfg, M_frac, beta, seeds)
        elapsed_op = time.monotonic() - t_op
        sign_div = result.get("any_sign_divergence", False)
        max_delta = result.get("global_max_abs_delta", 0.0)
        print(f"  sign_divergence={sign_div} max_delta={max_delta:.4f} elapsed={elapsed_op:.1f}s",
              flush=True)
        result["M_frac"] = M_frac
        result["beta"]   = beta
        result["elapsed_s"] = round(elapsed_op, 2)
        all_results.append(result)

    elapsed_total = time.monotonic() - t0
    verdict, verdict_msg = compute_verdict({"results": all_results, "N": N_cfg})

    summary = {
        "anchor": "axis3_triplepoint_v3_n4096",
        "N": N_cfg, "smoke": smoke,
        "operating_points": op_points, "seeds": seeds,
        "results": all_results,
        "verdict": verdict, "verdict_msg": verdict_msg,
        "elapsed_s": round(elapsed_total, 2),
    }
    out_dir = get_output_dir()
    out_path = out_dir / "metrics.json"
    with open(out_path, "w") as fp:
        json.dump(summary, fp, indent=2)

    print(f"\n[verdict] {verdict}", flush=True)
    print(f"[verdict_msg] {verdict_msg}", flush=True)
    print(f"[elapsed] {elapsed_total:.1f}s", flush=True)
    print(f"[output] {out_path}", flush=True)


def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--self-test", action="store_true", dest="self_test")
    args = p.parse_args()
    if args.self_test:
        sys.exit(0)
    run_full(smoke=args.smoke)


if __name__ == "__main__":
    main()
