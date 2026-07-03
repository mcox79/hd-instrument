"""Hatano-Sasa Cap 3 NESS audit v2 — longer trajectories follow-up.

Motivation (v1 -> v2)
---------------------
v1 (`wave14_hatano_sasa_cap3_ness_crooks_v1`) landed MIDDLE BAND: the
empirical <exp(-W_ex)> on Cap 3's streaming-NESS substrate trajectories was
in [0.5, 2.0] but outside the [0.95, 1.05] hard-pass band. Per
[[feedback-rehabilitation-after-rejection]]: before concluding "Cap 3
acquires partial cert only," try axis-combination rescues.

Hypothesis for v2: v1's MIDDLE was a finite-trajectory-length artifact.
The Hatano-Sasa integral fluctuation theorem (HS-IFT) requires the chain
to sample its NESS distribution, which requires trajectories long enough
that the NESS distribution is reached. v1 used glauber_steps=60. v2
doubles this to 120 and also doubles n_traj_per_cell. If v2 lands inside
[0.95, 1.05], v1's MIDDLE was a length artifact and Cap 3 acquires the
full HS-IFT audit-cert. If v2 stays MIDDLE, the NESS deviation is real.

Key change vs v1
----------------
- glauber_steps: 60 -> 120 (longer trajectories per Markov chain).
- n_traj_per_cell: 150 -> 300 (more samples per noise/seed cell).
- 4 noise levels * 4 seeds = 16 cells (matches v1).
- Same beta=1.5, N=2048, M=50 substrate operating point.

Everything else (HS verdict bands, formula, Cap 3 substrate primitives)
is reused unchanged from v1 via import.

Vertices: HATANO_SASA_CAP3_LONG_TRAJ_V2_HARD_PASS / HARD_FAIL / MIDDLE_BAND.

Pre-reg: preregs/2026-05-24_wave14_hatano_sasa_cap3_long_traj_v2.md
"""
from __future__ import annotations
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import argparse
import importlib.util
import json
import math
import os
import time
from pathlib import Path

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir as _canonical_get_output_dir  # noqa: E402  # SH-4 canonical helper
from verification import oracle  # noqa: E402

# Import v1 machinery
_v1_path = REPO / "experiments" / "exp_wave14_hatano_sasa_cap3_ness_crooks_v1.py"
_spec = importlib.util.spec_from_file_location("hs_v1", _v1_path)
_v1 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_v1)

run_one_cell = _v1.run_one_cell
compute_hs_verdict = _v1.compute_hs_verdict
self_test_verdict = _v1.self_test_verdict
self_test_hatano_sasa_formula = _v1.self_test_hatano_sasa_formula
HARD_PASS_LOW = _v1.HARD_PASS_LOW
HARD_PASS_HIGH = _v1.HARD_PASS_HIGH
HARD_FAIL_LOW = _v1.HARD_FAIL_LOW
HARD_FAIL_HIGH = _v1.HARD_FAIL_HIGH
CROSS_BASIN_MIN = _v1.CROSS_BASIN_MIN


def get_output_dir(name: str) -> Path:
    """SH-4 delegates to canonical _seed_checkpoint.get_output_dir (single-prefix)."""
    out = _canonical_get_output_dir(name)
    out.mkdir(parents=True, exist_ok=True)
    return out
def validate_metrics(d: dict) -> None:
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    missing = required - set(d.keys())
    if missing:
        raise ValueError(f"metrics missing required fields: {missing}")


def run_experiment(smoke: bool) -> tuple:
    t0 = time.monotonic()

    if smoke:
        # Smoke: 2 seeds * 2 noise levels = 4 cells at near-critical beta
        N = 1024
        M = 30
        n_traj_per_cell = 80
        noise_levels = [0.30, 0.40]
        seeds = [17, 23]
        max_iter = 30
        beta = 1.5
        glauber_steps = 80   # already longer than v1 smoke (40)
    else:
        # FULL v2: same substrate operating point as v1 full, but
        # 2x glauber_steps + 2x n_traj.
        N = 2048
        M = 50
        n_traj_per_cell = 300       # v1 full: 150
        noise_levels = [0.30, 0.40, 0.50, 0.60]
        seeds = [17, 23, 31, 41]
        max_iter = 60
        beta = 1.5
        glauber_steps = 120         # v1 full: 60

    cfg = {
        "N": N, "M": M, "n_traj_per_cell": n_traj_per_cell,
        "noise_levels": noise_levels, "seeds": seeds, "max_iter": max_iter,
        "beta": beta, "glauber_steps": glauber_steps,
        "hard_pass_band": [HARD_PASS_LOW, HARD_PASS_HIGH],
        "hard_fail_outside": [HARD_FAIL_LOW, HARD_FAIL_HIGH],
        "cross_basin_min": CROSS_BASIN_MIN,
        "smoke": smoke,
        "v2_changes_from_v1_full": {
            "glauber_steps": "60 -> 120",
            "n_traj_per_cell": "150 -> 300",
        },
    }

    print(
        f"Config v2: N={N} M={M} n_traj_per_cell={n_traj_per_cell} "
        f"glauber_steps={glauber_steps} (v1 full used 60/150)",
        flush=True,
    )

    cells = []
    for noise_p in noise_levels:
        for seed in seeds:
            cell = run_one_cell(
                N, M, n_traj_per_cell, noise_p, seed, max_iter,
                beta=beta, glauber_steps=glauber_steps,
            )
            cells.append(cell)
            print(
                f"  cell p={noise_p:.2f} seed={seed}: "
                f"hs={cell['hs_identity_val']:.4f} "
                f"cb_frac={cell['cross_basin_frac']:.3f} "
                f"n_valid={cell['n_valid_traj']} "
                f"n_attr={cell['n_distinct_attractors']}",
                flush=True,
            )

    valid_cells = [c for c in cells if not c["degenerate"]]
    n_valid_cells = len(valid_cells)
    if n_valid_cells == 0:
        hs_mean = 1.0
        cross_basin_frac_mean = 0.0
        hs_sem = 0.0
    else:
        hs_mean = sum(c["hs_identity_val"] for c in valid_cells) / n_valid_cells
        cross_basin_frac_mean = (
            sum(c["cross_basin_frac"] for c in valid_cells) / n_valid_cells
        )
        if n_valid_cells > 1:
            var = sum(
                (c["hs_identity_val"] - hs_mean) ** 2 for c in valid_cells
            ) / (n_valid_cells - 1)
            hs_sem = math.sqrt(var / n_valid_cells)
        else:
            hs_sem = 0.0

    print(f"\nAggregate across {n_valid_cells} valid cells:", flush=True)
    print(f"  <exp(-W_ex)>     = {hs_mean:.4f}  (SEM={hs_sem:.4f})", flush=True)
    print(f"  cross_basin_frac = {cross_basin_frac_mean:.4f}", flush=True)

    verdict_v1, msg_v1 = compute_hs_verdict(
        hs_mean, cross_basin_frac_mean, n_valid_cells
    )
    # Re-label vertices for v2
    verdict_map = {
        "HATANO_SASA_CAP3_NESS_CROOKS_HARD_PASS": "HATANO_SASA_CAP3_LONG_TRAJ_V2_HARD_PASS",
        "HATANO_SASA_CAP3_NESS_CROOKS_HARD_FAIL": "HATANO_SASA_CAP3_LONG_TRAJ_V2_HARD_FAIL",
        "HATANO_SASA_CAP3_NESS_CROOKS_MIDDLE_BAND": "HATANO_SASA_CAP3_LONG_TRAJ_V2_MIDDLE_BAND",
    }
    verdict = verdict_map.get(verdict_v1, verdict_v1)
    msg = (
        f"v2 (longer trajectories: glauber_steps=120, n_traj=300) "
        f"vs v1 (60/150): {msg_v1.replace('Cap 3', 'Cap 3 [v2]')}"
    )
    elapsed = time.monotonic() - t0
    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)

    summary = {
        "hs_identity_val": hs_mean,
        "hs_identity_sem": hs_sem,
        "cross_basin_frac": cross_basin_frac_mean,
        "n_valid_cells": n_valid_cells,
        "n_cells_total": len(cells),
        "hard_pass_band": [HARD_PASS_LOW, HARD_PASS_HIGH],
        "hard_fail_outside": [HARD_FAIL_LOW, HARD_FAIL_HIGH],
        "cross_basin_min": CROSS_BASIN_MIN,
        "cells": [
            {
                "noise_p": c["noise_p"],
                "seed": c["seed"],
                "hs_identity_val": c["hs_identity_val"],
                "cross_basin_frac": c["cross_basin_frac"],
                "n_valid_traj": c["n_valid_traj"],
                "n_distinct_attractors": c["n_distinct_attractors"],
                "degenerate": c["degenerate"],
            }
            for c in cells
        ],
    }
    return summary, verdict, msg, elapsed, cfg


def write_metrics(out_dir: Path, summary: dict, verdict: str, msg: str,
                  elapsed: float, config: dict) -> None:
    metrics = {
        "verdict": verdict,
        "verdict_msg": msg,
        "elapsed_s": elapsed,
        "summary": summary,
        "config": config,
    }
    validate_metrics(metrics)
    tmp = out_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(metrics, indent=2, default=float))
    tmp.replace(out_dir / "metrics.json")


def run_smoke() -> None:
    out_dir = get_output_dir("wave14_hatano_sasa_cap3_long_traj_v2_smoke")
    s, v, m, e, c = run_experiment(smoke=True)
    oracle.assert_in_range("hs_identity_val", s["hs_identity_val"], (0.0, 100.0))
    oracle.assert_baseline_high("n_valid_cells", float(s["n_valid_cells"]), 0.0)
    write_metrics(out_dir, s, v, m, e, c)
    print(f"\nSMOKE OK: {v}", flush=True)


def run_main() -> None:
    out_dir = get_output_dir("wave14_hatano_sasa_cap3_long_traj_v2")
    s, v, m, e, c = run_experiment(smoke=False)
    write_metrics(out_dir, s, v, m, e, c)
    print(f"\nDONE: {v}", flush=True)


def main() -> int:
    ap = argparse.ArgumentParser(
        description="HS-IFT v2 longer-trajectory follow-up to v1 MIDDLE BAND"
    )
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test_verdict()
        self_test_hatano_sasa_formula()
        print("\nAll self-tests passed (reused from v1).", flush=True)
        return 0
    if args.smoke:
        run_smoke()
        return 0
    run_main()
    return 0


if __name__ == "__main__":
    sys.exit(main())
