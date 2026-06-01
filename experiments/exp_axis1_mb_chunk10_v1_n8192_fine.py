"""AXIS1 MB-CHUNK 10 v1: Fine M_frac boundary sweep at N=8192.

CONTEXT:
  axis1_mb_chunk9_v1_n8192: M_fracs=[1,2,4,8,12] at N=8192.
  Chunk 9 locates the boundary near M_frac=8 (ret_m8 in [0.20, 0.80]).
  Chunk 10 zooms in: fine sweep M_fracs=[4,6,8,10,12,16] at N=8192 and beta=32.
  Goal: pin the phase boundary M_frac precisely at N=8192.

SCIENTIFIC QUESTION:
  At N=8192, what is the precise M_frac where retention crosses 0.50?
  Is the boundary width (transition sharpness) the same as at N=4096?
  A sharper boundary at larger N = finite-size scaling (SKAH-M prediction).

PRE-REGISTERED BANDS:
  Prior: chunk9 shows ret_m8 in [0.20, 0.80] at N=8192.
  Expected: transition midpoint near M_frac~8-10.

  HARD_PASS: at least one M_frac with ret in [0.40, 0.60] (=boundary midpoint located)
    AND retention strictly decreasing from M_frac=4 to M_frac=16 at >= 2/3 seeds.
    Interpretation: phase boundary precisely located at N=8192.
  HARD_FAIL: all M_fracs have ret > 0.90 OR all < 0.10 (no boundary present).
  MIDDLE_BAND: transition present but midpoint not in [0.40, 0.60].

FORMULA SELF-TESTS:
  1. N == 8192 (PROT-018 binding).
  2. M at M_frac=10, N=8192: M=81920.
  3. OOM: W=268MB, keys=81920*8192*4=2.7GB. Total~3GB. Under 6GB. OK.
  4. Strict decrease check: all ret[i+1] <= ret[i] + 0.05.

TIMEOUT ESTIMATE:
  6 M_fracs x 3 seeds = 18 cells. Similar to chunk9 (5x3=15 cells, ~21600s floor).
  timeout_s = 21600 (PROT-019 _n8192 floor).

N-suffix: _n8192 -> production N = 8192 (PROT-018 binding).
Anchor: axis1_mb_chunk10_v1_n8192_fine
Queue: overnight_queue (GPU; N=8192 fine boundary sweep, 6 pts x 3 seeds)
Pre-reg: prereqs/2026-05-28_axis1_mb_chunk10_v1_n8192_fine.md
Parent: axis1_mb_chunk9_v1_n8192; axis1_mb_chunk1_v1 (store_facts_batched, v3 codebook)
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

# Load axis1_mb_chunk1 for store_facts_batched, compute_retention, v3 codebook
_c1_path = REPO / "experiments" / "exp_axis1_mb_chunk1_v1.py"
_c1_spec = importlib.util.spec_from_file_location("axis1c1_c10", _c1_path)
c1 = importlib.util.module_from_spec(_c1_spec)
_c1_spec.loader.exec_module(c1)

store_facts_batched = c1.store_facts_batched
compute_retention = c1.compute_retention
v3 = c1.v3

# PRODUCTION CONFIG -- PROT-018: _n8192 suffix binds to N = 8192
N_FULL  = 8192
N_SMOKE = 1024
assert N_FULL == 8192, f"PROT-018: N_FULL must be 8192; got {N_FULL}"

# Fine sweep: zoomed in on transition region
M_FRACS_FULL  = [4.0, 6.0, 8.0, 10.0, 12.0, 16.0]
M_FRACS_SMOKE = [4.0, 8.0, 12.0]

BETA = 32.0

SEEDS_FULL  = [7, 17, 23]
SEEDS_SMOKE = [17]

N_PROBE = 200

# Pre-registered thresholds
HP_MID_RANGE   = (0.40, 0.60)   # midpoint of transition
HF_ALL_HIGH    = 0.90           # all > 0.90 = no boundary
HF_ALL_LOW     = 0.10           # all < 0.10 = already collapsed
HP_SEEDS_MIN   = 2


def get_output_dir(default_name: str = "axis1_mb_chunk10_v1_n8192_fine") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def run_one_cell(N: int, M_frac: float, beta: float, seed: int, device: torch.device) -> Dict:
    """Run retention measurement at (N, M_frac, beta, seed)."""
    M = int(M_frac * N)
    codebook, _ = v3.make_kerdock_4coset_codebook(N, device)
    W, keys, _vals, _key_idx, val_idx = store_facts_batched(codebook, M, seed, N, device)
    ret = compute_retention(W, keys, val_idx, codebook, beta, N, n_probe=N_PROBE)
    print(f"    N={N} M_frac={M_frac} beta={beta} seed={seed} ret={ret:.5f}", flush=True)
    return {
        "N": N, "M_frac": M_frac, "M": M, "beta": beta, "seed": seed,
        "retention": round(ret, 5),
    }


def compute_verdict(summary: Dict) -> Tuple[str, str]:
    cells = summary.get("cells", [])
    if not cells:
        return ("C10_INCONCLUSIVE", "No cells.")

    N = summary.get("N", N_FULL)

    by_mfrac: Dict[float, List] = {}
    for c in cells:
        by_mfrac.setdefault(c["M_frac"], []).append(c)

    m_sorted = sorted(by_mfrac.keys())
    mean_ret: Dict[float, float] = {}
    for m in m_sorted:
        rets = [c["retention"] for c in by_mfrac[m]]
        mean_ret[m] = sum(rets) / len(rets)

    all_rets = [mean_ret[m] for m in m_sorted]

    # Boundary midpoint: any M_frac with mean ret in [0.40, 0.60]
    midpoint_located = any(HP_MID_RANGE[0] <= r <= HP_MID_RANGE[1] for r in all_rets)
    midpoint_mfrac = [m for m, r in mean_ret.items()
                      if HP_MID_RANGE[0] <= r <= HP_MID_RANGE[1]]

    # Strict decrease per seed
    by_seed_decrease: Dict[int, bool] = {}
    for c in cells:
        pass  # computed below

    # Check decrease per seed
    seed_ids = sorted(set(c["seed"] for c in cells))
    seed_decrease = []
    for seed in seed_ids:
        sc = [c for c in cells if c["seed"] == seed]
        sc_sorted = sorted(sc, key=lambda x: x["M_frac"])
        rets_s = [c["retention"] for c in sc_sorted]
        is_dec = all(rets_s[i] >= rets_s[i+1] - 0.05
                     for i in range(len(rets_s)-1))
        seed_decrease.append(is_dec)

    n_decrease = sum(seed_decrease)
    all_mean_rets = list(mean_ret.values())
    min_ret = min(all_mean_rets) if all_mean_rets else 0.0
    max_ret = max(all_mean_rets) if all_mean_rets else 0.0

    detail = (f"midpoint_located={midpoint_located} midpoint_mfracs={midpoint_mfrac} "
              f"n_decrease={n_decrease}/{len(seed_decrease)} "
              f"mean_rets={[round(mean_ret[m], 3) for m in m_sorted]} N={N}")

    # HARD_FAIL: all high or all low
    if max_ret < HF_ALL_LOW or min_ret > HF_ALL_HIGH:
        return ("C10_HARD_FAIL",
                f"NO_BOUNDARY_N8192: all retention out of transition range. " + detail)

    if midpoint_located and n_decrease >= HP_SEEDS_MIN:
        return ("C10_HARD_PASS",
                f"BOUNDARY_PINNED_N8192: transition midpoint located + monotone. " + detail)

    return ("C10_MIDDLE_BAND", f"PARTIAL_BOUNDARY: " + detail)


def _instrumentation_selftest() -> None:
    assert N_FULL == 8192, f"PROT-018: N_FULL must be 8192; got {N_FULL}"
    # Formula: M at M_frac=10, N=8192
    assert int(10.0 * N_FULL) == 81920, f"M at M_frac=10: {int(10.0*N_FULL)}"
    # Verdict gates
    fake_hp = [{"M_frac": m, "retention": max(0.0, 0.9 - m*0.06), "seed": 17}
               for m in M_FRACS_FULL]
    v, msg = compute_verdict({"cells": fake_hp, "N": N_FULL})
    assert "PASS" in v or "MIDDLE" in v, f"gate: {v}"
    fake_hf = [{"M_frac": m, "retention": 0.05, "seed": 17} for m in M_FRACS_FULL]
    vf, _ = compute_verdict({"cells": fake_hf, "N": N_FULL})
    assert "HARD_FAIL" in vf, f"HARD_FAIL gate: {vf}"
    # Smoke cell at N_SMOKE
    device = torch.device("cpu")
    cell = run_one_cell(N_SMOKE, 4.0, BETA, 17, device)
    assert "retention" in cell, "retention missing"
    assert not math.isnan(cell["retention"]), "retention NaN"
    # 4x smoke: N=4096
    cell4 = run_one_cell(N_SMOKE * 4, 4.0, BETA, 17, device)
    assert "retention" in cell4, "4x retention missing"
    print(f"[selftest] axis1_mb_chunk10_v1_n8192_fine PASS ret_smoke={cell['retention']:.4f}", flush=True)


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
    m_fracs = M_FRACS_SMOKE if smoke else M_FRACS_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL

    print(f"[run] axis1_mb_chunk10_v1_n8192_fine smoke={smoke} N={N_cfg} "
          f"M_fracs={m_fracs} beta={BETA} seeds={seeds}", flush=True)
    t0 = time.time()

    all_cells = []
    for M_frac in m_fracs:
        print(f"\n  [M_frac={M_frac}]", flush=True)
        for seed in seeds:
            cell = run_one_cell(N_cfg, M_frac, BETA, seed, device)
            all_cells.append(cell)
        print(f"  M_frac={M_frac} elapsed={time.time()-t0:.1f}s", flush=True)

    verdict, verdict_msg = compute_verdict({"cells": all_cells, "N": N_cfg})
    elapsed = round(time.time() - t0, 2)

    summary = {
        "anchor": "axis1_mb_chunk10_v1_n8192_fine", "N": N_cfg, "smoke": smoke,
        "M_fracs": m_fracs, "beta": BETA, "seeds": seeds,
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
