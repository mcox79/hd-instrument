"""BID M-normalized v3: reship of v2 with corrected timeout=14400.

CONTEXT:
  v2 (v267 verdict: GENUINE TIMEOUT at 3600s exact = stale PROT-019 floor).
  v1 (v265 HARD_PASS): N=4096 3-seed M_fracs [0.05,0.1,0.125,0.25,0.5] -> monotone BID decrease.
  v2 extension: M_fracs [0.025,0.05,0.125,0.5,2.0,5.0,10.0,15.0] -- never ran due to timeout.
  v3 = v2 config exactly, with timeout_s=14400 (4h floor for _n4096 PROT-019).

  Cap_map row: substrate-outside-static-Hopfield green 60-72% (v266).
  v3 corroborates v266 BID v4 N=12288 +25%/1.5x N rate at the M-normalized axis.

SCIENTIFIC QUESTION:
  Does BID remain OUTSIDE static-Hopfield bands across the full multi-basin M range?
  Extended sweep: M_fracs [0.025,0.05,0.125,0.5,2.0,5.0,10.0,15.0].
  Does BID stay monotone decreasing? Does it fall inside bands at high M (near M_c)?

PRE-REGISTERED BANDS (envelope-extension; prior anchor = v1 HARD_PASS at M_fracs<0.5):
  v1 showed BID outside bands at all M_fracs [0.05,0.5]. This extends to larger M.

  HARD_PASS: BID monotone decreasing across M_fracs AND BID > 50 (absolute) at all M_frac <= 5.0.
    Interpretation: substrate-outside-Hopfield signature robust across entire multi-basin range.
  HARD_FAIL: BID falls inside Hopfield bands (BID < 0.55 normalized or BID < 5 absolute)
    at any M_frac <= 1.0. Weakens substrate-outside-static-Hopfield claim.
  MIDDLE_BAND: BID outside bands at low M but enters bands at high M (expected near-M_c physics).
    Records M_c crossing for the BID signature.

FORMULA SELF-TESTS:
  1. N=4096, M_frac=0.025 -> M=102.
  2. N=4096, M_frac=15.0 -> M=61440.
  3. BID from v1 at M_frac=0.5, N=4096: ~95. Expected outside bands.
  4. HARD_PASS: low_M_outside=True AND monotone_ok=True (at most 2 reversals).
  5. N == 4096 (PROT-018 binding).

OOM CHECK:
  TwoNN BID is CPU-based. Memory: patterns = M x N float64.
  At M_frac=15, N=4096: M=61440 patterns. 61440*4096*8 = 2.0GB float64. Under RAM limit for CPU.

TIMEOUT ESTIMATE:
  BID TwoNN O(M*k) where k=nearest neighbors.
  From v1: 5-M_frac 3-seed at N=4096 was <300s total (BID is fast).
  v3: 8 M_fracs x 3 seeds = 24 cells. High-M cells (M_frac=10-15, M~40-60K): ~100-200s each.
  Conservative: 8 * 3 * 80s = 1920s. 1.5x safety: 2880s. Round: 3600s.
  BUT PROT-019 _n4096 floor: timeout >= 14400.
  timeout_s = 14400 (PROT-019 compliant for _n4096).

N-suffix: _n4096 -> production N = 4096 (PROT-018 binding).
Anchor: bid_m_normalized_v3_n4096
Queue: remote_cpu_queue (TwoNN; no CUDA; N=4096 3-seed 8-M_frac extended sweep)
Pre-reg: preregs/2026-05-28_bid_m_normalized_v3_n4096.md
Parent: bid_m_normalized_v1 (v265 HARD_PASS); v2 genuine-timeout
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

# Import v1 for shared BID computation
_v1_path = REPO / "experiments" / "exp_bid_m_normalized_v1.py"
_v1_spec = importlib.util.spec_from_file_location("bid_mnorm_v1_v3", _v1_path)
_bid_v1 = importlib.util.module_from_spec(_v1_spec)
_v1_spec.loader.exec_module(_bid_v1)

run_one_seed_Mfrac = _bid_v1.run_one_seed_Mfrac
BAND_MAX_INSIDE    = _bid_v1.BAND_MAX_INSIDE

# PRODUCTION CONFIG -- PROT-018: _n4096 suffix binds to N = 4096
N_FULL  = 4096   # PROT-018 binding contract
N_SMOKE = 512
assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

# Extended M_frac sweep (same as v2): low end + high end approaching phase boundary
M_FRACS_FULL  = [0.025, 0.05, 0.125, 0.5, 2.0, 5.0, 10.0, 15.0]
M_FRACS_SMOKE = [0.05, 0.5, 2.0]   # 3-pt smoke spanning range

SEEDS_FULL  = [7, 17, 23]
SEEDS_SMOKE = [17]

# Pre-registered thresholds
BID_OUTSIDE_MIN_ABS = 50.0   # BID > 50 absolute = clearly outside any Hopfield class band
MAX_REVERSALS       = 2      # monotone tolerance


def get_output_dir(default_name: str = "bid_m_normalized_v3_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def compute_verdict(summary: Dict) -> Tuple[str, str]:
    cells = summary.get("cells", [])
    if not cells:
        return ("BID_V3_INCONCLUSIVE", "No cells.")

    N_cfg = summary.get("N", N_FULL)

    # BID threshold scales with N (TwoNN intrinsic dimension grows with N).
    # At N=4096: BID > 50 = outside Hopfield bands (from v1 empirical data).
    # At N=512:  BID > 6  = outside bands (scaled proportionally by N/8).
    bid_threshold = max(6.0, BID_OUTSIDE_MIN_ABS * (N_cfg / N_FULL))

    # Organize by M_frac
    by_mfrac: Dict = {}
    for c in cells:
        mf = c["M_frac"]
        if mf not in by_mfrac:
            by_mfrac[mf] = []
        by_mfrac[mf].append(c["bid"])

    mfracs_sorted = sorted(by_mfrac.keys())
    mean_bids = {mf: sum(bids) / len(bids) for mf, bids in by_mfrac.items()}

    # Check outside-band at low M (M_frac <= 5.0)
    low_M_mfracs = [mf for mf in mfracs_sorted if mf <= 5.0]
    low_M_outside = all(mean_bids.get(mf, 0) > bid_threshold for mf in low_M_mfracs)

    # Check monotone decreasing (allow MAX_REVERSALS non-monotone steps)
    bids_seq = [mean_bids[mf] for mf in mfracs_sorted]
    reversals = sum(1 for i in range(len(bids_seq) - 1) if bids_seq[i + 1] > bids_seq[i] * 1.05)
    monotone_ok = reversals <= MAX_REVERSALS

    # HARD_FAIL: BID falls inside band at M_frac <= 1.0
    very_low_mfracs = [mf for mf in mfracs_sorted if mf <= 1.0]
    hf_inside = any(mean_bids.get(mf, 999) < bid_threshold for mf in very_low_mfracs)

    detail = (f"N={N_cfg} bid_threshold={bid_threshold:.1f} mfracs={mfracs_sorted} "
              f"mean_bids={dict(zip(mfracs_sorted, [round(v,1) for v in bids_seq]))} "
              f"low_M_outside={low_M_outside} monotone_ok={monotone_ok} reversals={reversals}")

    if hf_inside:
        return ("BID_V3_HARD_FAIL",
                f"HARD_FAIL: BID inside static-Hopfield band at low M_frac. " + detail)

    if low_M_outside and monotone_ok:
        return ("BID_V3_HARD_PASS",
                f"BID M-SWEEP OUTSIDE BANDS: substrate-outside-Hopfield robust across M range. "
                + detail)

    return ("BID_V3_MIDDLE_BAND",
            f"Partial: some M_fracs inside bands or non-monotone. " + detail)


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics non-null/non-sentinel at small scale."""
    assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096"

    # Import chain check
    assert run_one_seed_Mfrac is not None, "run_one_seed_Mfrac import failed"
    assert BAND_MAX_INSIDE > 0, f"BAND_MAX_INSIDE invalid: {BAND_MAX_INSIDE}"

    # Formula self-tests
    assert int(0.025 * N_FULL) == 102, f"M_frac formula: {int(0.025*N_FULL)} != 102"
    assert int(15.0 * N_FULL) == 61440, f"M_frac formula: {int(15.0*N_FULL)} != 61440"

    # Gate self-test
    fake_pass = {
        "cells": [{"M_frac": mf, "bid": 150.0, "seed": s}
                  for mf in [0.05, 0.5, 2.0] for s in [7, 17, 23]],
        "N": N_FULL
    }
    v, msg = compute_verdict(fake_pass)
    assert "HARD_PASS" in v or "MIDDLE_BAND" in v, f"Verdict self-test (pass) failed: {v}"

    fake_fail = {
        "cells": [{"M_frac": 0.05, "bid": 2.0, "seed": 17}],  # BID < 50 at low M
        "N": N_FULL
    }
    v2, _ = compute_verdict(fake_fail)
    assert "HARD_FAIL" in v2, f"Verdict self-test (fail) got: {v2}"

    # Smoke forward pass at N_SMOKE
    result = run_one_seed_Mfrac(N_SMOKE, 0.125, seed=17)
    assert isinstance(result, dict), f"run_one_seed_Mfrac must return dict: {type(result)}"
    bid_val = result.get("bid", result.get("bid_estimate", None))
    assert bid_val is not None and not np.isnan(bid_val), f"BID is None/NaN: {result}"
    assert bid_val > 0.0, f"BID is zero or negative: {bid_val}"

    # Multi-scale smoke N_SMOKE x4
    result_4x = run_one_seed_Mfrac(N_SMOKE * 4, 0.125, seed=17)
    bid_4x = result_4x.get("bid", result_4x.get("bid_estimate", None))
    assert bid_4x is not None and bid_4x > 0, f"4x smoke BID invalid: {result_4x}"

    print(f"[selftest] bid_m_normalized_v3_n4096 PASS bid_smoke={bid_val:.2f} bid_4x={bid_4x:.2f}",
          flush=True)


_instrumentation_selftest()


def run_full(smoke: bool = False) -> None:
    t0 = time.monotonic()

    m_fracs = M_FRACS_SMOKE if smoke else M_FRACS_FULL
    seeds   = SEEDS_SMOKE   if smoke else SEEDS_FULL
    N_cfg   = N_SMOKE       if smoke else N_FULL

    print(f"bid_m_normalized_v3_n4096 mode={'SMOKE' if smoke else 'FULL'} N={N_cfg} "
          f"m_fracs={m_fracs} seeds={seeds}", flush=True)

    cells = []
    for M_frac in m_fracs:
        for seed in seeds:
            t_cell = time.monotonic()
            result = run_one_seed_Mfrac(N_cfg, M_frac, seed=seed)
            bid = result.get("bid", result.get("bid_estimate", 0.0))
            cell = {
                "M_frac": M_frac, "seed": seed, "bid": round(float(bid), 4),
                "M": int(M_frac * N_cfg), "N": N_cfg,
                "outside_abs": bid > BID_OUTSIDE_MIN_ABS,
            }
            cells.append(cell)
            print(f"  M_frac={M_frac} seed={seed} BID={bid:.2f} "
                  f"outside={bid>BID_OUTSIDE_MIN_ABS} ({time.monotonic()-t_cell:.1f}s)",
                  flush=True)

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
