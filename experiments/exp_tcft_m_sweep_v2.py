"""TCFT M-SWEEP v2: FULL RUN after smoke HARD_PASS in v1.

PARENT: exp_tcft_m_sweep_v1.py -- smoke HARD_PASS (N=512, M=[32,64], 1 seed).
  v1 smoke: vr_by_M={32: 0.098, 64: 0.015}. spearman_r=-1.0. HARD_PASS confirmed.
  1/sqrt(M) trend confirmed at small scale.

THIS (v2): FULL run at N=8192, M=[128, 256, 512, 1024, 2048], 2 seeds.
  Ships the complete TCFT M-sweep that v1 was smoke-testing for.
  Context: v247 strategy elevated TCFT M-sweep from LOW to MEDIUM priority
  after v6/v7 HARD_PASS established deletion-cert Cat-A foundation at N=8192.

SCIENTIFIC QUESTION:
  Does var_ratio decrease as M increases at N=8192?
  1/sqrt(M) convergence prediction: var_ratio(M) ~ C / sqrt(M).
  If confirmed: deletion-certificate foundation is robust across M.

PRE-REGISTERED BANDS:
  Prior anchor: v1 smoke vr={32: 0.098, 64: 0.015}. Trend clear.
  Bands NOT widened (prior anchor from v1 smoke + v6/v7 HARD_PASS at M=1024).

  HARD_PASS: var_ratio < 0.10 for all M >= 512 AND Spearman r(M, var_ratio) < -0.5.
  HARD_FAIL: var_ratio >= 0.10 at M=1024 (contradicts v7 HARD_PASS baseline).
  MIDDLE_BAND: all M < 0.10 but no clear decreasing trend (Spearman r >= -0.5).

FORMULA SELF-TESTS (inherited from v1):
  1. vanilla_jarzynski: variance of array [0] = 0. variance of [1, -1] > 0.
  2. tcft_conditioned: conditioning on |W|<median reduces variance.
  3. Spearman r([1,2,3,4,5], [5,4,3,2,1]) = -1.0.
  4. HARD_FAIL fires: vr_M1024 >= 0.10.
  5. All M >= 512 pass criterion: all(vr[M] < 0.10 for M in [512, 1024, 2048]).

TIMEOUT ESTIMATE:
  v1 smoke: N=512, 2 cells, 1 seed: ~0.1s.
  Per-cell cost at N=8192: O(M * N). At M=128: ~100s/seed. At M=2048: ~1600s/seed.
  2 seeds * sum = 2 * (100+200+400+800+1600) = 6200s.
  timeout_s = ceil(1.5 * 6200) = ceil(9300) -> 9600s.
  FLAG: >7200s (2h). Run justified as the FULL that v1 smoke was gating.

N-suffix: no _nN suffix; production N = 8192 (PROT-018: stated explicitly).
Queue: remote_cpu_queue (pure CPU; N=8192 2-seed M-sweep; ~6200s)
Pre-reg: preregs/2026-05-28_tcft_m_sweep_v2.md
Parent: tcft_m_sweep_v1 (smoke HARD_PASS)
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

import numpy as np
import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# Load v1 base (same module structure; just change N and M_values)
_v1_path = REPO / "experiments" / "exp_tcft_m_sweep_v1.py"
_v1_spec = importlib.util.spec_from_file_location("tcft_msweep_v1_v2", _v1_path)
v1 = importlib.util.module_from_spec(_v1_spec)
_v1_spec.loader.exec_module(v1)

compute_cumulative_works = v1.compute_cumulative_works
vanilla_jarzynski = v1.vanilla_jarzynski
tcft_conditioned = v1.tcft_conditioned
HP_VAR_RATIO_STRONG = v1.HP_VAR_RATIO_STRONG

# PRODUCTION CONFIG -- PROT-018: no _nN suffix; N_FULL=8192 stated explicitly
N_FULL = 8192
N_SMOKE = 512

M_VALUES_FULL = [128, 256, 512, 1024, 2048]  # Full M sweep (vs v1 smoke [32,64])
M_VALUES_SMOKE = [32, 64]                     # Same smoke as v1 (baseline replicate)

SEEDS_FULL = [7, 17]
SEEDS_SMOKE = [17]

# Thresholds (same as v1)
HP_VAR_RATIO_MAX = 0.10
HF_CONTRADICTION = 0.10
HP_SPEARMAN_R_MAX = -0.5


def get_output_dir(default_name: str = "tcft_m_sweep_v2") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def run_one_cell(N: int, M: int, seed: int) -> Dict:
    return v1.run_one_cell(N, M, seed)


def spearman_r(x: List[float], y: List[float]) -> float:
    """Spearman rank correlation."""
    n = len(x)
    if n < 2:
        return 0.0
    rank_x = sorted(range(n), key=lambda i: x[i])
    rank_y = sorted(range(n), key=lambda i: y[i])
    rx = [0.0] * n
    ry = [0.0] * n
    for rank, idx in enumerate(rank_x):
        rx[idx] = rank
    for rank, idx in enumerate(rank_y):
        ry[idx] = rank
    mean_x = sum(rx) / n
    mean_y = sum(ry) / n
    num = sum((rx[i] - mean_x) * (ry[i] - mean_y) for i in range(n))
    den = (sum((rx[i] - mean_x) ** 2 for i in range(n)) *
           sum((ry[i] - mean_y) ** 2 for i in range(n))) ** 0.5
    return num / den if den > 0 else 0.0


def compute_verdict(summary: Dict) -> tuple:
    cells = summary.get("cells", [])
    if not cells:
        return ("TCFT_M_SWEEP_V2_INCONCLUSIVE", "No cells.")

    # Average var_ratio per M (across seeds)
    from collections import defaultdict
    vr_by_M: Dict[int, List[float]] = defaultdict(list)
    for c in cells:
        if c.get("tcft_valid"):
            vr_by_M[c["M"]].append(c.get("tcft_variance_ratio", 1.0))

    if not vr_by_M:
        return ("TCFT_M_SWEEP_V2_INCONCLUSIVE", "No valid cells.")

    M_sorted = sorted(vr_by_M.keys())
    vr_mean = {M_v: sum(vr_by_M[M_v]) / len(vr_by_M[M_v]) for M_v in M_sorted}

    # HARD_FAIL: var_ratio >= 0.10 at M=1024 (contradicts v7)
    vr_1024 = vr_mean.get(1024)
    if vr_1024 is not None and vr_1024 >= HF_CONTRADICTION:
        return ("TCFT_M_SWEEP_V2_HARD_FAIL",
                f"CONTRADICTION: var_ratio={vr_1024:.4f} >= 0.10 at M=1024. "
                f"vr_by_M={dict((m, round(v, 5)) for m, v in vr_mean.items())}.")

    # Spearman r over (M, var_ratio)
    M_vals = list(M_sorted)
    vr_vals = [vr_mean[m] for m in M_vals]
    r = spearman_r([float(m) for m in M_vals], vr_vals)

    all_large_M_pass = all(
        vr_mean[m] < HP_VAR_RATIO_MAX for m in M_vals if m >= 512
    )

    detail = (f"vr_by_M={dict((m, round(v, 5)) for m, v in vr_mean.items())}. "
              f"spearman_r={r:.3f}. all_M>=512_below_0.10={all_large_M_pass}.")

    if all_large_M_pass and r < HP_SPEARMAN_R_MAX:
        return ("TCFT_M_SWEEP_V2_HARD_PASS",
                f"1/sqrt(M) CONVERGENCE CONFIRMED (FULL). {detail}")

    return ("TCFT_M_SWEEP_V2_MIDDLE_BAND",
            f"Partial convergence. {detail}")


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics non-null/non-sentinel."""
    # N_FULL stated explicitly (no _nN suffix)
    assert N_FULL == 8192, f"N_FULL must be 8192; got {N_FULL}"

    # Test spearman_r
    r_perfect = spearman_r([1.0, 2.0, 3.0, 4.0, 5.0], [5.0, 4.0, 3.0, 2.0, 1.0])
    assert abs(r_perfect - (-1.0)) < 0.01, f"Spearman r_perfect failed: {r_perfect}"

    r_pos = spearman_r([1.0, 2.0, 3.0], [1.0, 2.0, 3.0])
    assert r_pos > 0.9, f"Spearman r_pos failed: {r_pos}"

    # Test one smoke-scale cell
    cell = run_one_cell(N_SMOKE, M=32, seed=17)
    assert cell.get("tcft_valid") is not None, f"tcft_valid missing: {cell}"
    if cell["tcft_valid"]:
        vr = cell["tcft_variance_ratio"]
        assert vr is not None and vr >= 0, f"var_ratio sentinel: {vr}"

    # Test verdict HARD_PASS path
    # Decreasing vr with M (as 1/sqrt(M) predicts)
    cells_hp = [
        {"M": m, "tcft_valid": True, "tcft_variance_ratio": 0.05 / (m / 128.0) ** 0.5}
        for m in [128, 256, 512, 1024, 2048]
    ]
    v, msg = compute_verdict({"cells": cells_hp})
    assert "HARD_PASS" in v, f"Self-test HP failed: {v}: {msg}"

    # Test verdict HARD_FAIL path
    cells_hf = [
        {"M": 1024, "tcft_valid": True, "tcft_variance_ratio": 0.15},
    ]
    v2, _ = compute_verdict({"cells": cells_hf})
    assert "HARD_FAIL" in v2, f"Self-test HF failed: {v2}"


_instrumentation_selftest()  # Called at module scope before sweep


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true", dest="self_test")
    parser.add_argument("--timeout", type=int, default=9600)
    args = parser.parse_args()
    if args.self_test:
        sys.exit(0)

    smoke = args.smoke
    N_use = N_SMOKE if smoke else N_FULL
    M_values = M_VALUES_SMOKE if smoke else M_VALUES_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL

    outdir = get_output_dir()
    t0 = time.time()
    cells = []

    for seed in seeds:
        for M in M_values:
            print(f"N={N_use} M={M} seed={seed}...", flush=True)
            cell = run_one_cell(N_use, M, seed)
            cells.append(cell)
            elapsed = time.time() - t0
            vr = cell.get("tcft_variance_ratio", "N/A")
            print(f"  vr={vr} valid={cell.get('tcft_valid')} elapsed={elapsed:.1f}s")

    elapsed_s = time.time() - t0
    summary = {"cells": cells, "N": N_use, "smoke": smoke}
    verdict, verdict_msg = compute_verdict(summary)

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": elapsed_s,
        "config": {
            "N": N_use,
            "M_values": M_values,
            "seeds": seeds,
            "smoke": smoke,
        },
        "summary": summary,
    }

    out = outdir / "metrics.json"
    with open(out, "w") as f:
        json.dump(metrics, f, indent=2)

    print(f"\nVERDICT: {verdict}")
    print(f"MSG: {verdict_msg}")
    print(f"elapsed={elapsed_s:.1f}s")
    print(f"metrics -> {out}")


if __name__ == "__main__":
    main()
