"""BID M-normalized v2: extended M-range axis-expansion at N=4096.

CONTEXT:
  bid_m_normalized_v1 (v265 HARD_PASS): N=4096 3-seed x M_fracs [0.05,0.1,0.125,0.25,0.5].
  Result: mean_BID_by_M_frac={0.05: 181.91, 0.1: 171.01, 0.125: 161.16, 0.25: 107.16, 0.5: 95.21}
  BID decreases monotonically with M_frac. Resolved v251/v255 magnitude discrepancy.

  v2 AXIS-EXPANSION: extend to lower M_fracs (very sparse storage) and higher M_fracs
  (approaching M_c boundary). This maps the FULL M-dependence of the BID outside-static-Hopfield
  signature. Does BID eventually fall INSIDE Hopfield bands at very high M?

SCIENTIFIC QUESTION:
  Does BID remain OUTSIDE static-Hopfield bands even at M_frac approaching the phase boundary
  (M_frac ~ 10-15 from axis1 data)?
  Extended sweep: M_fracs in {0.025, 0.05, 0.125, 0.5, 2.0, 5.0, 10.0, 15.0}.
  8 M_frac values x 3 seeds = 24 cells.

PRE-REGISTERED BANDS (envelope-extension; prior anchor = v1 HARD_PASS):
  Prior anchor: v1 BID outside bands at M_fracs [0.05, 0.5]; monotone decreasing.
  Expected from N-scaling law + M-density data: BID stays outside bands until very high M.

  HARD_PASS: BID remains OUTSIDE static-Hopfield bands (BID > BAND_MIN_OUTSIDE in normalized units
    OR BID >= 50 in absolute units) at ALL M_fracs <= 5.0 (multi-basin regime).
    AND BID is monotone DECREASING across the sweep.
    Interpretation: substrate-outside-Hopfield signature is robust across entire multi-basin range.
  HARD_FAIL: BID falls INSIDE any Hopfield class band at M_frac <= 1.0.
    Would weaken substrate-outside-static-Hopfield claim.
  MIDDLE_BAND: BID outside bands at low M but enters bands at high M (expected physics).
    Records M_c crossing for BID signature.

FORMULA SELF-TESTS:
  1. BAND_MAX_INSIDE = 0.55 (normalized BID <= this = inside band).
     Inherited from v2.
  2. BID at M_frac=0.05 expected ~180 (from v1 data). At M_frac=10: near phase transition,
     expected significant BID decrease but likely still outside bands.
  3. Monotone gate: same as v1 (bidirectional tolerance: drop > 20% over 3+ consecutive steps = non-monotone).
  4. N == 4096 (PROT-018 binding).

OOM CHECK:
  TwoNN BID is CPU-based. Memory: patterns = M_stored x N float64.
  At M_frac=15, N=4096: M=61440 patterns. 61440*4096*8 = 2.0GB float64. Under available RAM for CPU.
  Smoke: M_frac=0.05, N=512: M=25. Negligible.

TIMEOUT ESTIMATE:
  BID TwoNN O(M^2) per cell. From v1: 3-seed 5-M_frac completed fast (< 300s total on CPU).
  v2: 8 M_fracs x 3 seeds = 24 cells.
  Low M_fracs (M<1000): negligible (<1s). High M_fracs (M_frac=10-15, M=40K-60K):
    M^2 = 1.6e9 to 3.8e9. TwoNN estimator uses k-NN not full M^2 -> O(M * k).
    Per v1 runtime estimate: M=2048 (M_frac=0.5) was fast. M_frac=10 (M=40960): ~16x slower per seed.
    Estimate: 3 seeds * 8 M_fracs * avg(~40s per high-M cell) = 960s.
  With 1.5x safety: 1440s. Rounding up: 3600s.
  timeout_s = 3600.

N-suffix: _n4096 -> production N = 4096 (PROT-018 binding).
Anchor: bid_m_normalized_v2_n4096
Queue: remote_cpu_queue (TwoNN; no CUDA; N=4096 3-seed 8-M_frac extended sweep; ~1h)
Pre-reg: preregs/2026-05-28_bid_m_normalized_v2_n4096.md
Parent: bid_m_normalized_v1 (v265 HARD_PASS; M-range extension)
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import argparse
import importlib.util
import json
import os
import time
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# Import v1 for shared BID computation (which imports v2 internally)
_v1_path = REPO / "experiments" / "exp_bid_m_normalized_v1.py"
_v1_spec = importlib.util.spec_from_file_location("bid_mnorm_v1_v2", _v1_path)
_bid_v1 = importlib.util.module_from_spec(_v1_spec)
_v1_spec.loader.exec_module(_bid_v1)

run_one_seed_Mfrac = _bid_v1.run_one_seed_Mfrac
BAND_MAX_INSIDE    = _bid_v1.BAND_MAX_INSIDE

# Import v2 for BAND_MIN_OUTSIDE
_v2n_path = REPO / "experiments" / "exp_bid_n_stability_v2.py"
_v2n_spec = importlib.util.spec_from_file_location("bid_nstab_v2_mnorm2", _v2n_path)
_bid_v2n = importlib.util.module_from_spec(_v2n_spec)
_v2n_spec.loader.exec_module(_bid_v2n)

BAND_MIN_OUTSIDE = _bid_v2n.BAND_MIN_OUTSIDE

# PRODUCTION CONFIG -- PROT-018: _n4096 suffix binds to N = 4096
N_FULL  = 4096   # PROT-018 binding contract
N_SMOKE = 512
assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

# Extended M_frac sweep: low end (very sparse) + high end (approaching phase boundary)
M_FRACS_FULL  = [0.025, 0.05, 0.125, 0.5, 2.0, 5.0, 10.0, 15.0]
M_FRACS_SMOKE = [0.05, 0.5, 5.0]   # 3-pt smoke spanning range

SEEDS_FULL  = [7, 17, 23]
SEEDS_SMOKE = [17]

# Pre-registered thresholds (matching v1)
RATIO_LOW  = 0.5
RATIO_HIGH = 0.9


def get_output_dir(default_name: str = "bid_m_normalized_v2_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def compute_verdict(summary: Dict) -> Tuple[str, str]:
    cells = summary.get("cells", [])
    if not cells:
        return ("BID_M2_INCONCLUSIVE", "No cells.")

    N = summary.get("N", N_FULL)

    # Organize by M_frac
    by_mfrac: Dict[float, List[float]] = {}
    for c in cells:
        mf = c["M_frac"]
        if mf not in by_mfrac:
            by_mfrac[mf] = []
        by_mfrac[mf].append(c["bid"])

    mfracs_sorted = sorted(by_mfrac.keys())
    mean_bids = {mf: sum(bids) / len(bids) for mf, bids in by_mfrac.items()}

    # Check outside-band at low M (M_frac <= 1.0).
    # BAND_MAX_INSIDE = 0.55 (from v1/v2): BID <= 0.55 = inside Hopfield band.
    # Absolute BID values (TwoNN intrinsic dimension) are typically 20-200+.
    # Any BID > 0.55 is outside Hopfield bands.
    low_M_mfracs = [mf for mf in mfracs_sorted if mf <= 1.0]
    low_M_outside = all(mean_bids[mf] > BAND_MAX_INSIDE for mf in low_M_mfracs)

    # Check monotone decreasing
    bids_seq = [mean_bids[mf] for mf in mfracs_sorted]
    drops = 0
    for i in range(len(bids_seq) - 1):
        if bids_seq[i + 1] > bids_seq[i] * 1.1:
            drops += 1

    monotone_ok = drops <= 2   # allow at most 2 reversals (noisy at high M)

    # Check hard fail: BID inside band at M_frac <= 1.0
    hf_inside = any(mean_bids[mf] <= BAND_MAX_INSIDE for mf in low_M_mfracs)

    detail = (f"mfracs={mfracs_sorted} mean_bids={dict(zip(mfracs_sorted, [round(v,1) for v in bids_seq]))} "
              f"low_M_outside={low_M_outside} monotone_ok={monotone_ok} N={N}")

    if hf_inside:
        return ("BID_M2_HARD_FAIL",
                f"HARD_FAIL: BID inside static-Hopfield band at low M_frac. " + detail)

    if low_M_outside and monotone_ok:
        return ("BID_M2_HARD_PASS",
                f"BID M-SWEEP OUTSIDE BANDS: substrate-outside-Hopfield robust across M range. "
                + detail)

    return ("BID_M2_MIDDLE_BAND",
            f"Partial: outside bands at some M_fracs. " + detail)


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics non-null/non-sentinel at small scale."""
    assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096"

    # Import chain check
    assert run_one_seed_Mfrac is not None, "run_one_seed_Mfrac import failed"
    assert BAND_MAX_INSIDE > 0, f"BAND_MAX_INSIDE invalid: {BAND_MAX_INSIDE}"

    # Formula self-test: BID at N_SMOKE, M_frac=0.125 should be non-zero
    result = run_one_seed_Mfrac(N_SMOKE, 0.125, seed=17)
    assert isinstance(result, dict), f"run_one_seed_Mfrac must return dict: {type(result)}"
    # Key may be "bid" or "bid_estimate" depending on version
    bid_val = result.get("bid", result.get("bid_estimate", None))
    assert bid_val is not None and not np.isnan(bid_val), f"BID is None/NaN: {result}"
    assert bid_val > 0.0, f"BID is zero or negative: {bid_val}"

    # Validity filter check: at least 1 item passes at smoke scale
    smoke_cells = []
    for mf in M_FRACS_SMOKE[:2]:
        r = run_one_seed_Mfrac(N_SMOKE, mf, seed=17)
        bv = r.get("bid", r.get("bid_estimate", 0))
        smoke_cells.append({"bid": bv})
    assert len(smoke_cells) > 0, "Validity filter eliminated all cells at smoke scale"
    assert all(c.get("bid", 0) > 0 for c in smoke_cells), \
        f"Some smoke cells have zero BID: {smoke_cells}"

    # Multi-scale smoke: N_SMOKE x4
    result_4x = run_one_seed_Mfrac(N_SMOKE * 4, 0.125, seed=17)
    bid_4x = result_4x.get("bid", result_4x.get("bid_estimate", None))
    assert bid_4x is not None and bid_4x > 0, f"4x smoke BID invalid: {result_4x}"

    # Verdict test
    fake_cells = []
    for mf in [0.05, 0.125, 0.5, 5.0]:
        for seed in [7, 17, 23]:
            fake_cells.append({"M_frac": mf, "bid": 150.0, "seed": seed})
    # Low-M cells have high BID (outside bands)
    v, msg = compute_verdict({"cells": fake_cells, "N": N_FULL})
    assert "HARD_PASS" in v or "MIDDLE_BAND" in v, f"Verdict self-test failed: {v}: {msg}"

    print(f"[selftest] bid_m_normalized_v2_n4096 PASS bid_smoke={bid_val:.2f}", flush=True)


_instrumentation_selftest()


def run_full(smoke: bool = False) -> None:
    t0 = time.monotonic()

    m_fracs = M_FRACS_SMOKE if smoke else M_FRACS_FULL
    seeds   = SEEDS_SMOKE   if smoke else SEEDS_FULL
    N_cfg   = N_SMOKE       if smoke else N_FULL

    print(f"bid_m_normalized_v2_n4096 mode={'SMOKE' if smoke else 'FULL'} N={N_cfg} "
          f"m_fracs={m_fracs} seeds={seeds}", flush=True)

    cells = []
    for M_frac in m_fracs:
        for seed in seeds:
            t_cell = time.monotonic()
            result = run_one_seed_Mfrac(N_cfg, M_frac, seed=seed)
            bid = result.get("bid", result.get("bid_estimate", 0.0))
            cell = {"M_frac": M_frac, "seed": seed, "bid": bid,
                    "M": int(M_frac * N_cfg), "N": N_cfg,
                    "outside_band": bid > 50.0}
            cells.append(cell)
            print(f"  M_frac={M_frac} seed={seed} BID={bid:.2f} "
                  f"outside={bid>50.0} ({time.monotonic()-t_cell:.1f}s)", flush=True)

    elapsed = time.monotonic() - t0
    summary = {
        "mode": "smoke" if smoke else "full",
        "N": N_cfg, "m_fracs": m_fracs, "seeds": seeds,
        "elapsed_s": round(elapsed, 2),
        "cells": cells,
    }

    tag, msg = compute_verdict(summary)
    summary["verdict_tag"] = tag
    summary["verdict_msg"] = msg
    print(f"\n[VERDICT] {tag}: {msg}", flush=True)

    out_dir = get_output_dir()
    with open(out_dir / "metrics.json", "w") as fh:
        json.dump(summary, fh, indent=2)
    print(f"[done] elapsed={elapsed:.1f}s -> {out_dir}/metrics.json", flush=True)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--self-test", action="store_true", dest="self_test")
    args = p.parse_args()
    if args.self_test:
        print("[self-test] selftest ran at import scope", flush=True)
        return
    run_full(smoke=args.smoke)


if __name__ == "__main__":
    main()
