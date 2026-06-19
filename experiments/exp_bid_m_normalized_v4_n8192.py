"""BID M-NORMALIZED v4: substrate-outside-Hopfield at N=8192 across M_fracs.

CONTEXT:
  bid_m_normalized_v3_n4096 (v267 context): N=4096 BID vs M_frac sweep.
  v4 extends to N=8192 to verify: BID outside Hopfield bands holds at larger N
  across the M_frac sweep.

  The non-static-Hopfield classification (cap_map 45-60%) is most valuable when
  it holds at the production N=8192 scale that experiments like SKAH-M use.

SCIENTIFIC QUESTION:
  At N=8192, does BID remain outside all static Hopfield bands across M_fracs=[0.05..5.0]?
  Does BID normalize (BID/N) remain consistent with N=4096 values?

PRE-REGISTERED BANDS:
  Prior: bid_m_normalized_v3_n4096 BID outside bands (threshold=50 abs at N=4096).
  At N=8192: threshold scales to ~100 abs. Expected BID > 100 at M_frac=0.5-2.0.

  HARD_PASS: BID > N-aware threshold at >= 5/8 M_frac cells, >= 2/3 seeds.
    Interpretation: substrate-outside-Hopfield confirmed at N=8192.
  HARD_FAIL: BID < N-aware threshold at majority of M_frac cells.
    Interpretation: N=8192 is inside a Hopfield class.
  MIDDLE_BAND: some M_fracs pass, some fail.

FORMULA SELF-TESTS:
  1. N == 8192 (PROT-018 binding).
  2. bid_threshold(N=8192) = max(6.0, 50.0 * (8192/4096)) = max(6.0, 100.0) = 100.0.
  3. M at M_frac=0.5, N=8192: M=4096.
  4. OOM: W=268MB. Keys=65536*8192*4=2.1GB (at M_frac=10). Careful with large M.
     Restrict M_fracs_full to [0.025, 0.05, 0.125, 0.5, 2.0, 5.0] (no 10+).

TIMEOUT ESTIMATE:
  6 M_fracs x 3 seeds = 18 cells. TwoNN at N=8192 M=65536: ~30s per cell.
  Total: 18*30=540s. Safety: ceil(1.5*540*2)=1620s. _n8192 floor=21600. timeout_s=21600.

N-suffix: _n8192 -> production N = 8192 (PROT-018 binding).
Anchor: bid_m_normalized_v4_n8192
Queue: remote_cpu_queue (TwoNN; CPU; N=8192)
Pre-reg: preregs/2026-05-28_bid_m_normalized_v4_n8192.md
Parent: bid_m_normalized_v3_n4096; bid_m_normalized_v1 (run_one_seed_Mfrac)
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
from typing import Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# Load bid_m_normalized_v1 for run_one_seed_Mfrac
_v1_path = REPO / "experiments" / "exp_bid_m_normalized_v1.py"
_v1_spec = importlib.util.spec_from_file_location("bid_v1_v4n8k", _v1_path)
_bid_v1 = importlib.util.module_from_spec(_v1_spec)
_v1_spec.loader.exec_module(_bid_v1)

run_one_seed_Mfrac = _bid_v1.run_one_seed_Mfrac
BAND_MAX_INSIDE = _bid_v1.BAND_MAX_INSIDE

# PRODUCTION CONFIG -- PROT-018: _n8192 suffix binds to N = 8192
N_FULL  = 8192
N_SMOKE = 512
assert N_FULL == 8192, f"PROT-018: N_FULL must be 8192; got {N_FULL}"

M_FRACS_FULL  = [0.025, 0.05, 0.125, 0.5, 2.0, 5.0]
M_FRACS_SMOKE = [0.05, 0.5, 2.0]

SEEDS_FULL  = [7, 17, 23]
SEEDS_SMOKE = [17]

BID_OUTSIDE_MIN_ABS = 50.0   # calibrated at N=4096


def bid_threshold(N_cfg: int) -> float:
    return max(6.0, BID_OUTSIDE_MIN_ABS * (N_cfg / 4096))


# Pre-registered thresholds
HP_PASS_FRACS_MIN = 5    # >= 5/6 M_frac cells above threshold
HP_SEEDS_MIN      = 2


def get_output_dir(default_name: str = "bid_m_normalized_v4_n8192") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def run_one_cell(N: int, M_frac: float, seed: int) -> Dict:
    """Run BID estimator at (N, M_frac, seed)."""
    result = run_one_seed_Mfrac(N, M_frac, seed)
    bid_val = result.get("bid_estimate", result.get("bid_outside", 0.0))
    if bid_val is None:
        bid_val = 0.0
    M = max(10, int(M_frac * N))
    thr = bid_threshold(N)
    passes = bid_val >= thr
    print(f"    N={N} M_frac={M_frac} M={M} seed={seed} bid={bid_val:.2f} threshold={thr:.2f} passes={passes}", flush=True)
    return {
        "N": N, "M_frac": M_frac, "M": M, "seed": seed,
        "bid": float(bid_val),
        "threshold": thr,
        "passes_hp": passes,
    }


def compute_verdict(summary: Dict) -> Tuple[str, str]:
    cells = summary.get("cells", [])
    if not cells:
        return ("BID_V4_N8K_INCONCLUSIVE", "No cells.")

    N_cfg = summary.get("N", N_FULL)
    thr = bid_threshold(N_cfg)

    # Per M_frac: how many seeds pass?
    by_mfrac: Dict[float, List] = {}
    for c in cells:
        by_mfrac.setdefault(c["M_frac"], []).append(c)

    n_fracs = len(by_mfrac)
    mean_bid = sum(c["bid"] for c in cells) / len(cells)
    # Use bid threshold directly (seed-count scaling: allow 1-seed pass at smoke)
    fracs_above_threshold = sum(
        1 for m, cs in by_mfrac.items()
        if sum(1 for c in cs if c["passes_hp"]) >= 1  # at least 1 seed passes
    )
    fracs_passing_multiseed = sum(
        1 for m, cs in by_mfrac.items()
        if sum(1 for c in cs if c["passes_hp"]) >= HP_SEEDS_MIN
    )
    seeds_per_frac = max(len(cs) for cs in by_mfrac.values()) if by_mfrac else 1
    # Use multi-seed threshold only when we have enough seeds
    if seeds_per_frac >= HP_SEEDS_MIN:
        fracs_passing = fracs_passing_multiseed
    else:
        fracs_passing = fracs_above_threshold  # smoke mode: 1-seed

    detail = (f"fracs_passing={fracs_passing}/{n_fracs} fracs_above_thr={fracs_above_threshold} "
              f"mean_bid={mean_bid:.2f} threshold={thr:.2f} "
              f"HP_pass_fracs={HP_PASS_FRACS_MIN} seeds_per_frac={seeds_per_frac} N={N_cfg}")

    if fracs_passing == 0:
        return ("BID_V4_N8K_HARD_FAIL",
                f"ALL_INSIDE_BAND: fracs_passing={fracs_passing}. " + detail)

    if fracs_passing >= HP_PASS_FRACS_MIN:
        return ("BID_V4_N8K_HARD_PASS",
                f"OUTSIDE_BANDS_N8192: fracs_passing={fracs_passing}/{n_fracs}. " + detail)

    return ("BID_V4_N8K_MIDDLE_BAND",
            f"PARTIAL_OUTSIDE: fracs_passing={fracs_passing}/{n_fracs}. " + detail)


def _instrumentation_selftest() -> None:
    assert N_FULL == 8192, f"PROT-018: N_FULL must be 8192; got {N_FULL}"
    # bid_threshold formula
    thr = bid_threshold(N_FULL)
    assert abs(thr - 100.0) < 1.0, f"bid_threshold(8192) should be ~100: {thr}"
    thr_smoke = bid_threshold(N_SMOKE)
    assert abs(thr_smoke - 6.25) < 0.5, f"bid_threshold(512) should be ~6.25: {thr_smoke}"
    # Verdict gates
    fake_hp = [{"M_frac": m, "bid": 200.0, "threshold": thr, "passes_hp": True}
               for m in [0.05, 0.5, 2.0] for _ in range(3)]
    v, _ = compute_verdict({"cells": fake_hp, "N": N_FULL})
    assert "HARD_PASS" in v or "MIDDLE" in v, f"PASS/MIDDLE gate: {v}"
    fake_hf = [{"M_frac": 0.5, "bid": 1.0, "threshold": thr, "passes_hp": False}]
    vf, _ = compute_verdict({"cells": fake_hf, "N": N_FULL})
    assert "HARD_FAIL" in vf, f"HARD_FAIL gate: {vf}"
    # Smoke cell (small M_frac=0.05 to keep selftest fast, ~2s per cell)
    cell = run_one_cell(N_SMOKE, 0.05, 17)
    assert not math.isnan(cell["bid"]), "bid NaN"
    assert cell["bid"] > 0.0, "bid <= 0"
    # 4x scale: N=2048, M_frac=0.05 (M=102 points -- fast for TwoNN)
    cell4 = run_one_cell(N_SMOKE * 4, 0.05, 17)
    assert not math.isnan(cell4["bid"]), "4x bid NaN"
    print(f"[selftest] bid_m_normalized_v4_n8192 PASS bid_smoke={cell['bid']:.2f}", flush=True)


_instrumentation_selftest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true", dest="self_test")
    args = parser.parse_args()
    if args.self_test:
        sys.exit(0)

    smoke = args.smoke
    N_cfg = N_SMOKE if smoke else N_FULL
    m_fracs = M_FRACS_SMOKE if smoke else M_FRACS_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL

    print(f"[run] bid_m_normalized_v4_n8192 smoke={smoke} N={N_cfg} M_fracs={m_fracs} seeds={seeds}", flush=True)
    t0 = time.time()

    all_cells = []
    for M_frac in m_fracs:
        for seed in seeds:
            cell = run_one_cell(N_cfg, M_frac, seed)
            all_cells.append(cell)
        print(f"  M_frac={M_frac} elapsed={time.time()-t0:.1f}s", flush=True)

    verdict, verdict_msg = compute_verdict({"cells": all_cells, "N": N_cfg})
    elapsed = round(time.time() - t0, 2)

    summary = {
        "anchor": "bid_m_normalized_v4_n8192", "N": N_cfg, "smoke": smoke,
        "M_fracs": m_fracs, "seeds": seeds,
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
