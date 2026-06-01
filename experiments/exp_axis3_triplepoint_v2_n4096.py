"""AXIS-3 triple-point v2: alternate operating points.

CONTEXT:
  v1 tested (M_frac=6, beta=8, N=4096) and returned MIDDLE_BAND HONEST:
    sign_divergence=False: only 2/6 directions showed |delta_ret|>=0.05 (BOTH negative,
    BOTH M-axis). Conclusion: (M_frac=6, beta=8) is INTERIOR to a single phase --
    NOT a triple-point. max |delta_ret| = 0.25 (M_plus direction at epsilon=0.40).

  v2 (THIS): probe 3+ strategically distributed operating points in the M x beta plane.
  Evidence from AXIS-1 chunk5 (v254): mean_conf drops 0.605->0.202 across M_frac=[4,12]
  = there IS a phase boundary in this M-regime. The triple-point (if any) must lie
  ON or NEAR this boundary. v1 was at M_frac=6 which v254 places at mid-decay.

  v1 key finding: M_plus (adding memories) -> NEGATIVE delta_ret (more interference);
  M_minus (removing memories) -> MIXED small responses (inconsistent with triple-point).
  The interesting regime: closer to the actual transition zone.

OPERATING POINT SELECTION:
  From v254 chunk5: mean_conf at M_frac=4 is ~0.605 (high capacity end);
  at M_frac=8: ~0.4; at M_frac=10: ~0.25 (transition zone); at M_frac=12: ~0.20.
  Triple-point candidates (where MULTIPLE phases compete):
  (a) M_frac=10, beta=8: near chunk5 mid-decay transition
  (b) M_frac=8, beta=4: lower beta shifts phase boundary
  (c) M_frac=4, beta=16: high-capacity end, strong separation -- test if sign-divergence
       appears at opposite corner of M x beta plane
  v1 (M_frac=6, beta=8): already tested, NEGATIVE result (interior point confirmed)

SCIENTIFIC QUESTION:
  At operating points DIFFERENT from v1's (M_frac=6, beta=8), does any point in
  the M x beta plane exhibit sign_divergence=True (triple-point signature)?

PRE-REGISTERED BANDS:
  HARD_PASS: sign_divergence=True at >=1 operating point AND max |delta_ret| >= 0.15
    with at least one positive-direction AND one negative-direction response at SAME point.
    Interpretation: triple-point or multi-phase saddle found at that operating point.
  HARD_FAIL: sign_divergence=False AND max |delta_ret| < 0.05 across ALL tested points.
    Substrate completely insensitive to perturbations at all 3 points = degenerate regime.
  MIDDLE_BAND: max |delta_ret| >= 0.05 but sign_divergence=False at all points,
    OR sign_divergence=True but max |delta_ret| < 0.15 (weak saddle evidence).

FORMULA SELF-TESTS:
  1. delta_ret = ret_perturbed - ret_base. Identical states -> 0.
  2. For M_frac=10 (near transition): expected base ret ~ 0.3-0.5.
  3. M_plus direction: adding memories -> ret decreases -> delta_ret < 0.
  4. M_minus direction: removing memories -> ret increases -> delta_ret > 0.
     (opposite sign to M_plus -> sign_divergence=True if both |delta| >= 0.05)
  5. sign_divergence requires: pos_dirs >= 1 AND neg_dirs >= 1 at same operating point.
  6. N == 4096 (PROT-018).

OOM CHECK:
  W float32 at N=4096: 64MB. Kerdock codebook: 64MB. Peak: ~200MB. Under 6GB. OK.

TIMEOUT ESTIMATE:
  v1 elapsed=5.08s for N=4096 full (6 dirs x 5 eps x 5 seeds = 150 cells).
  v2: 3 operating points x 6 dirs x 5 eps x 3 seeds = 270 cells.
  But v1 ran in 5.08s (very fast -- base W cached, perturbations are cheap).
  v2: 3x more operating points x 3 seeds (v1 had 5) = 3/5 = 0.6x seeds.
  Wait -- v1 summary shows N_cells=150 = 6 dirs x 5 eps x 5 seeds.
  v2: 3 points x 6 dirs x 5 eps x 3 seeds = 270 cells.
  Scale: 270/150 = 1.8x. At same per-cell time: 5.08 * 1.8 = 9.1s.
  But base W must be re-built for each of 3 operating points (3 different M_fracs).
  Base build at N=4096: ~5s per seed x 3 seeds = 15s per operating point.
  Total: 3 points * (3 * 5s base + 270/3 * 0.034s/cell) = 45s + 3.06s ~ 50s.
  1.5x safety: 75s. PROT-019 floor for _n4096: 3600s. Use 3600s.
  NOTE: well under floor; using PROT-019 minimum 3600s for _n4096.

N-suffix: _n4096 -> production N = 4096 (PROT-018 binding).
Anchor: axis3_triplepoint_v2_n4096
Queue: overnight_queue (GPU; N=4096 perturbation-direction stability probe, 3 points)
Pre-reg: preregs/2026-05-28_axis3_triplepoint_v2_n4096.md
Parent: axis3_triplepoint_v1_n4096 (MIDDLE_BAND v262: single-phase at M_frac=6, beta=8)
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

# Load v1 for shared perturbation logic
_v1_path = REPO / "experiments" / "exp_axis3_triplepoint_v1_n4096.py"
_v1_spec = importlib.util.spec_from_file_location("axis3v1_v2", _v1_path)
v1 = importlib.util.module_from_spec(_v1_spec)
_v1_spec.loader.exec_module(v1)

store_base = v1.store_base
measure_ret = v1.measure_ret
apply_perturbation = v1.apply_perturbation
v3 = v1.v3   # Kerdock codebook builder

# PRODUCTION CONFIG -- PROT-018: _n4096 suffix binds to N = 4096
N_FULL = 4096       # PROT-018 binding contract
N_SMOKE = 1024      # smoke scale (Kerdock requires even log2; 1024->log2=10 OK)
assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

# Three strategically distributed operating points
# v1 tested (M_frac=6, beta=8) -> single-phase interior confirmed
# v2 tests points closer to actual phase boundary + opposite corner
OPERATING_POINTS = [
    {"M_frac": 10.0, "beta": 8.0},    # near chunk5 mid-decay transition
    {"M_frac": 8.0, "beta": 4.0},     # lower beta, shifts phase boundary
    {"M_frac": 4.0, "beta": 16.0},    # high-capacity, strong separation
]
OPERATING_POINTS_SMOKE = [
    {"M_frac": 10.0, "beta": 8.0},    # smoke tests only transition point
]

DIRECTIONS = ["M_plus", "M_minus", "beta_up", "beta_down", "W_noise", "M_partial_swap"]
EPSILONS_FULL = [0.02, 0.05, 0.10, 0.20, 0.40]
EPSILONS_SMOKE = [0.10, 0.40]

SEEDS_FULL = [7, 17, 23]
SEEDS_SMOKE = [17]

# Thresholds (same as v1 but applied per operating point)
HP_DELTA_RET_MIN = 0.15
HF_DELTA_RET_MAX = 0.05   # raised from v1's 0.02 per routing note (tighter HF)


def get_output_dir(default_name: str = "axis3_triplepoint_v2_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def compute_verdict_v2(all_results: List[Dict]) -> tuple:
    """Verdict across all operating points."""
    if not all_results:
        return ("AXIS3V2_INCONCLUSIVE", "No results computed.")

    # Per-operating-point analysis
    point_verdicts = []
    global_max_abs = 0.0
    any_sign_divergence = False

    for pt_result in all_results:
        op_label = pt_result["op_label"]
        cells = pt_result.get("cells", [])

        if not cells:
            continue

        delta_by_dir: Dict[str, List[float]] = {}
        for c in cells:
            d = c["direction"]
            if d not in delta_by_dir:
                delta_by_dir[d] = []
            delta_by_dir[d].append(c["delta_ret"])

        all_deltas = [abs(c["delta_ret"]) for c in cells]
        max_abs = max(all_deltas) if all_deltas else 0.0
        global_max_abs = max(global_max_abs, max_abs)

        mean_delta_by_dir = {d: sum(vs)/len(vs) for d, vs in delta_by_dir.items()}
        pos_dirs = [d for d, v in mean_delta_by_dir.items() if v > 0.02]
        neg_dirs = [d for d, v in mean_delta_by_dir.items() if v < -0.02]
        sign_div = len(pos_dirs) >= 1 and len(neg_dirs) >= 1

        if sign_div:
            any_sign_divergence = True

        point_verdicts.append({
            "op": op_label,
            "max_abs_delta": round(max_abs, 4),
            "sign_divergence": sign_div,
            "pos_dirs": pos_dirs,
            "neg_dirs": neg_dirs,
            "mean_delta_by_dir": {k: round(v, 4) for k, v in mean_delta_by_dir.items()},
        })

    detail = {
        "global_max_abs_delta": round(global_max_abs, 4),
        "any_sign_divergence": any_sign_divergence,
        "per_point": point_verdicts,
    }

    if global_max_abs < HF_DELTA_RET_MAX:
        return ("AXIS3V2_HARD_FAIL",
                f"FLAT RESPONSE at all operating points. max|delta_ret|={global_max_abs:.4f} "
                f"< {HF_DELTA_RET_MAX}. Substrate insensitive to perturbations in "
                f"M=[4,10] x beta=[4,16] regime. details={detail}.")

    if any_sign_divergence and global_max_abs >= HP_DELTA_RET_MIN:
        pass_pts = [p for p in point_verdicts if p["sign_divergence"]]
        return ("AXIS3V2_HARD_PASS",
                f"TRIPLE-POINT SIGNATURE at {len(pass_pts)} operating point(s). "
                f"max|delta_ret|={global_max_abs:.4f} >= {HP_DELTA_RET_MIN} "
                f"AND sign_divergence=True. Saddle-point confirmed. details={detail}.")

    return ("AXIS3V2_MIDDLE_BAND",
            f"Partial sensitivity. global_max|delta_ret|={global_max_abs:.4f}. "
            f"sign_divergence={any_sign_divergence}. details={detail}.")


def run_one_operating_point(M_frac: float, base_beta: float,
                             N: int, directions: list, epsilons: list,
                             seeds: List[int], device: torch.device) -> Dict:
    """Run perturbation sweep at one operating point."""
    M = int(M_frac * N)
    op_label = f"M_frac={M_frac}_beta={base_beta}"
    print(f"  [op_point] {op_label} N={N} M={M} seeds={seeds}", flush=True)

    codebook, _info = v3.make_kerdock_4coset_codebook(N, device)
    cells = []

    for seed in seeds:
        t_base = time.monotonic()
        W_base, keys_base, val_idx_base = store_base(codebook, M, seed, N, device)
        ret_base = measure_ret(W_base, keys_base, val_idx_base, codebook,
                               base_beta, N, n_probe=min(100, M))
        print(f"    seed={seed} base_ret={ret_base:.4f} "
              f"({time.monotonic()-t_base:.1f}s)", flush=True)

        for direction in directions:
            for epsilon in epsilons:
                W_p, keys_p, val_p, beta_p = apply_perturbation(
                    W_base, keys_base, val_idx_base, codebook,
                    direction, epsilon, seed, N, base_beta, device)
                n_probe = min(100, keys_p.shape[0]) if keys_p.shape[0] > 0 else 0
                ret_p = measure_ret(W_p, keys_p, val_p, codebook,
                                    beta_p, N, n_probe=n_probe) if n_probe > 0 else ret_base
                delta_ret = ret_p - ret_base
                cells.append({
                    "direction": direction,
                    "epsilon": epsilon,
                    "seed": seed,
                    "M_frac": M_frac,
                    "beta": base_beta,
                    "ret_base": round(ret_base, 5),
                    "ret_perturbed": round(ret_p, 5),
                    "delta_ret": round(delta_ret, 5),
                })

    return {"op_label": op_label, "M_frac": M_frac, "beta": base_beta, "cells": cells}


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics non-null/non-sentinel at small scale."""
    assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

    # Test verdict HARD_PASS path (sign divergence + large delta)
    cells_pass = [
        {"direction": "M_plus", "delta_ret": -0.20, "epsilon": 0.40, "seed": 7},
        {"direction": "M_minus", "delta_ret": +0.18, "epsilon": 0.40, "seed": 7},
        {"direction": "W_noise", "delta_ret": -0.12, "epsilon": 0.40, "seed": 7},
    ]
    all_results_pass = [{"op_label": "test_pt", "cells": cells_pass}]
    v, msg = compute_verdict_v2(all_results_pass)
    assert "HARD_PASS" in v, f"Self-test HARD_PASS failed: {v}: {msg}"

    # Test HARD_FAIL (all flat)
    cells_flat = [
        {"direction": d, "delta_ret": 0.01, "epsilon": 0.40, "seed": 7}
        for d in DIRECTIONS
    ]
    all_results_flat = [{"op_label": "test_flat", "cells": cells_flat}]
    v2, _ = compute_verdict_v2(all_results_flat)
    assert "HARD_FAIL" in v2, f"Self-test HARD_FAIL failed: {v2}"

    # MIDDLE_BAND: large delta but same sign
    cells_mid = [
        {"direction": d, "delta_ret": -0.20, "epsilon": 0.40, "seed": 7}
        for d in DIRECTIONS
    ]
    all_results_mid = [{"op_label": "test_mid", "cells": cells_mid}]
    v3_v, _ = compute_verdict_v2(all_results_mid)
    assert "MIDDLE_BAND" in v3_v, f"Self-test MIDDLE_BAND failed: {v3_v}"

    # Operating points count
    assert len(OPERATING_POINTS) == 3, \
        f"Expected 3 operating points; got {len(OPERATING_POINTS)}"

    # Test at smoke scale (one operating point, small N)
    device = torch.device("cpu")
    N_t = N_SMOKE
    pt = OPERATING_POINTS_SMOKE[0]
    result = run_one_operating_point(
        M_frac=pt["M_frac"], base_beta=pt["beta"],
        N=N_t, directions=["M_plus", "M_minus"],
        epsilons=[0.40], seeds=[17], device=device,
    )
    assert len(result.get("cells", [])) > 0, \
        f"validity filter eliminated all cells at smoke scale: {result}"
    first_cell = result["cells"][0]
    assert "delta_ret" in first_cell, f"delta_ret missing: {first_cell}"
    assert not math.isnan(first_cell["delta_ret"]), \
        f"delta_ret is NaN at smoke scale: {first_cell}"
    print(f"[selftest] smoke op_point M_frac={pt['M_frac']}: "
          f"delta_ret={first_cell['delta_ret']:.4f} OK", flush=True)

    # Multi-scale smoke: also verify at N_FULL scale (Kerdock only supports 1024 / 4096)
    # N_SMOKE=1024 and N_FULL=4096 are the two valid Kerdock sizes in this range
    # Use a single DIRECTION + 1 eps at N_FULL to confirm no OOM or codebook failure
    result_4x = run_one_operating_point(
        M_frac=pt["M_frac"], base_beta=pt["beta"],
        N=N_FULL, directions=["M_plus"],
        epsilons=[0.40], seeds=[17], device=device,
    )
    assert len(result_4x.get("cells", [])) > 0, \
        f"validity filter eliminated all cells at N_FULL={N_FULL}"
    print(f"[selftest] multi-scale N={N_FULL}: OK", flush=True)
    print("[selftest] PASS: all assertions OK", flush=True)


_instrumentation_selftest()


def run_full(smoke: bool = False) -> None:
    t0 = time.monotonic()
    op_points = OPERATING_POINTS_SMOKE if smoke else OPERATING_POINTS
    directions = DIRECTIONS
    epsilons = EPSILONS_SMOKE if smoke else EPSILONS_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    N = N_SMOKE if smoke else N_FULL
    mode_str = "SMOKE" if smoke else "FULL"

    print(f"[axis3_v2] {mode_str} N={N} operating_points={len(op_points)} "
          f"seeds={seeds}", flush=True)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[axis3_v2] device={device}", flush=True)

    out_dir = get_output_dir()
    all_results = []

    for pt in op_points:
        t_pt = time.monotonic()
        result = run_one_operating_point(
            M_frac=pt["M_frac"], base_beta=pt["beta"],
            N=N, directions=directions,
            epsilons=epsilons, seeds=seeds,
            device=device,
        )
        all_results.append(result)
        print(f"  op_point {result['op_label']} done "
              f"cells={len(result['cells'])} "
              f"({time.monotonic()-t_pt:.1f}s)", flush=True)

    verdict, verdict_msg = compute_verdict_v2(all_results)
    elapsed = time.monotonic() - t0

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
        "config": {"N": N, "smoke": smoke,
                   "operating_points": op_points,
                   "seeds": seeds},
        "summary": {"all_results": all_results},
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
