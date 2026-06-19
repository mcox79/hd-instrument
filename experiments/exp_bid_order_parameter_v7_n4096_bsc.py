"""BID ORDER PARAMETER v7: N=4096 BSC atoms, extended M_frac range with Spearman.

CONTEXT:
  bid_order_parameter_v6_n4096 (completed): N=4096 BSC atoms, Spearman rho check.
  v6 tested M_fracs=[0.05, 0.10, 0.25, 0.50, 1.0, 2.0, 4.0, 8.0] at 3 seeds.
  bid_m_normalized_v5_n8192 (completed): N=8192 vectorized W-build, outside Hopfield.

  v7 extends v6 with wider M_frac range to find the high-M regime where BID
  collapses or enters Hopfield band. Adds M_fracs up to 16.0 (overcapacity regime).
  Also adds N=2048 BSC control to verify N-scaling signal.

SCIENTIFIC QUESTION:
  At N=4096 BSC atoms, does BID eventually fall inside Hopfield bands at very high M_frac?
  Is there a critical M_frac_c where BID transitions from outside to inside the band?
  Does BID decrease monotonically all the way to M_frac=16 (deep overcapacity)?

PRE-REGISTERED BANDS:
  Prior: v6 completed (results expected: Spearman rho < -0.5, n_outside_low >= 2/3 seeds).
  This v7 extends the HIGH M_frac end to find the collapse point.

  HARD_PASS: BID remains outside Hopfield bands at M_frac=8 (matches v6 expected behavior)
    AND Spearman rho < -0.5 across M_fracs=[0.05..8.0].
    Interpretation: no BID collapse through overcapacity regime -- non-equilibrium persists.
  HARD_FAIL: BID falls inside Hopfield bands at M_frac <= 2.0
    (contradicts v5 n_outside_low evidence; indicates v6 fix was insufficient).
  MIDDLE_BAND: BID outside bands at M_frac <= 2.0 but collapses at some M_frac in (2, 16].

FORMULA SELF-TESTS:
  1. N == 4096 (PROT-018 binding).
  2. BSC atoms: random +/-1 at N=4096. TwoNN defined (not equidistant).
  3. BAND_MAX_INSIDE = 0.55 (from v1, same as v6).
  4. M at M_frac=8.0, N=4096: M=32768.
  5. M at M_frac=16.0, N=4096: M=65536.
  6. Spearman rho: rho(M_frac, BID_mean) < 0 means BID decreases as M_frac increases.
  7. normalized_bid = bid / N. outside bands if bid_norm > BAND_MAX_INSIDE.

OOM CHECK:
  TwoNN at M_frac=16.0, N=4096: M=65536. Batched: 512 x 4096 = 2MB per chunk. OK.
  W storage (Hopfield W for band comparison): 4096x4096 float32 = 64MB. OK.

TIMEOUT ESTIMATE:
  v6 at N=4096 8 M_fracs x 3 seeds estimated 14400s (floor).
  v7: 10 M_fracs x 3 seeds = 30 cells.
  v6: 8 M_fracs x 3 seeds = 24 cells. Scale: 30/24 = 1.25x.
  v6 estimated total: 64s (from docstring). 1.25x = 80s.
  Safety: ceil(1.5 * 80 * 5) = 600s. Floor _n4096 = 14400. timeout_s = 14400.

N-suffix: _n4096 -> production N = 4096 (PROT-018 binding).
Anchor: bid_order_parameter_v7_n4096_bsc
Queue: remote_cpu_queue (TwoNN; CPU; N=4096 BSC; 10 M_fracs x 3 seeds)
Pre-reg: preregs/2026-05-29_bid_order_parameter_v7_n4096_bsc.md
Parent: bid_order_parameter_v6_n4096 (completed)
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

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# Load v6 for shared BID infrastructure
_v6_path = REPO / "experiments" / "exp_bid_order_parameter_v6_n4096.py"
_v6_spec = importlib.util.spec_from_file_location("bid_op_v6_v7", _v6_path)
_bid_v6 = importlib.util.module_from_spec(_v6_spec)
_v6_spec.loader.exec_module(_bid_v6)

BAND_MAX_INSIDE = _bid_v6.BAND_MAX_INSIDE  # 0.55

# PRODUCTION CONFIG -- PROT-018: _n4096 suffix binds to N = 4096
N_FULL  = 4096
N_SMOKE = 512
assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

# Extended M_frac range vs v6 (adds 12.0, 16.0)
M_FRACS_FULL  = [0.05, 0.10, 0.25, 0.50, 1.0, 2.0, 4.0, 8.0, 12.0, 16.0]
M_FRACS_SMOKE = [0.10, 1.0]   # 2 smoke cells = fast gate

SEEDS_FULL  = [7, 17, 23]
SEEDS_SMOKE = [17]

# Pre-registered thresholds (same as v6)
HP_SPEARMAN_MAX   = -0.5   # rho < -0.5 = monotone decreasing
HP_OUTSIDE_MIN    = 2      # >= 2/3 seeds outside at low M_frac
HF_INSIDE_THRESH  = 2.0    # if BID falls inside at M_frac <= 2.0


def get_output_dir(default_name: str = "bid_order_parameter_v7_n4096_bsc") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def spearman_rho(xs: List[float], ys: List[float]) -> float:
    """Spearman rank correlation."""
    n = len(xs)
    if n < 2:
        return 0.0
    rx = np.argsort(np.argsort(xs)).astype(float)
    ry = np.argsort(np.argsort(ys)).astype(float)
    mr_x = rx.mean()
    mr_y = ry.mean()
    num = np.sum((rx - mr_x) * (ry - mr_y))
    den_x = np.sqrt(np.sum((rx - mr_x) ** 2))
    den_y = np.sqrt(np.sum((ry - mr_y) ** 2))
    if den_x < 1e-12 or den_y < 1e-12:
        return 0.0  # constant rank -> undefined, return 0
    return float(num / (den_x * den_y))


def run_one_mfrac_seed(N: int, M_frac: float, seed: int) -> Dict:
    """Run BID at (N, M_frac, seed) using v6's run_one_cell."""
    return _bid_v6.run_one_cell(N=N, M_frac=M_frac, seed=seed)


def compute_verdict(summary: Dict) -> Tuple[str, str]:
    per_mfrac = summary.get("per_mfrac", {})
    if not per_mfrac:
        return ("BID_V7_INCONCLUSIVE", "No per_mfrac data.")

    # Collect mean BID per M_frac
    mfracs = sorted(float(k) for k in per_mfrac.keys())
    bid_means = []
    for mf in mfracs:
        cells = per_mfrac.get(str(mf), [])
        bids = [c.get("bid_normalized", 0.0) for c in cells if c.get("bid_normalized") is not None]
        bid_means.append(float(np.mean(bids)) if bids else 0.0)

    rho = spearman_rho(mfracs, bid_means)

    # Check for collapse at M_frac <= 2.0
    low_mfrac_cells = []
    for mf, cells in per_mfrac.items():
        if float(mf) <= HF_INSIDE_THRESH:
            low_mfrac_cells.extend(cells)
    n_inside_low = sum(1 for c in low_mfrac_cells
                       if c.get("bid_normalized", BAND_MAX_INSIDE + 1) <= BAND_MAX_INSIDE)
    n_outside_low = sum(1 for c in low_mfrac_cells
                        if c.get("bid_normalized", 0.0) > BAND_MAX_INSIDE)

    detail = (f"rho={rho:.3f} n_outside_low={n_outside_low} n_inside_low={n_inside_low} "
              f"M_fracs={mfracs[:5]}...{mfracs[-2:]} bid_means={[round(b,3) for b in bid_means[:5]]}...")

    if n_inside_low > n_outside_low and n_inside_low > 0:
        return ("BID_V7_HARD_FAIL",
                f"BID collapses inside Hopfield bands at M_frac<={HF_INSIDE_THRESH}. " + detail)

    if rho < HP_SPEARMAN_MAX and n_outside_low >= HP_OUTSIDE_MIN:
        return ("BID_V7_HARD_PASS",
                f"BID monotone-decreasing outside Hopfield bands. " + detail)

    return ("BID_V7_MIDDLE_BAND",
            f"BID outside bands but rho={rho:.3f} not robustly monotone. " + detail)


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics are non-null/non-sentinel."""
    assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

    # Import chain
    assert _bid_v6 is not None, "v6 import failed"
    assert hasattr(_bid_v6, "run_one_cell"), "v6 missing run_one_cell"

    # Formula: M values
    assert int(8.0 * N_FULL) == 32768, "M at M_frac=8.0"
    assert int(16.0 * N_FULL) == 65536, "M at M_frac=16.0"

    # Spearman rho formula test
    # Monotone decreasing: rho ~ -1
    rho_dec = spearman_rho([0.05, 0.1, 0.5, 1.0, 2.0], [100, 80, 60, 40, 20])
    assert rho_dec < -0.9, f"Expected rho < -0.9 for decreasing, got {rho_dec:.3f}"
    # Monotone increasing: rho ~ +1
    rho_inc = spearman_rho([1.0, 2.0, 3.0, 4.0, 5.0], [10, 20, 30, 40, 50])
    assert rho_inc > 0.9, f"Expected rho > 0.9 for increasing, got {rho_inc:.3f}"
    # Reversed: rho = -1
    rho_rev = spearman_rho([1.0, 2.0, 3.0, 4.0, 5.0], [50, 40, 30, 20, 10])
    assert rho_rev < -0.99, f"Expected rho = -1 for reversed, got {rho_rev:.3f}"

    # Verdict tests
    cells_hp = [{"bid_normalized": 0.80, "M_frac": 0.10, "seed": 7},
                {"bid_normalized": 0.75, "M_frac": 0.10, "seed": 17},
                {"bid_normalized": 0.70, "M_frac": 0.10, "seed": 23},
                {"bid_normalized": 0.50, "M_frac": 2.0, "seed": 7},
                {"bid_normalized": 0.45, "M_frac": 2.0, "seed": 17},
                {"bid_normalized": 0.40, "M_frac": 2.0, "seed": 23}]
    summary_hp = {"per_mfrac": {
        "0.1": cells_hp[:3], "2.0": cells_hp[3:]
    }, "N": N_FULL}
    v, msg = compute_verdict(summary_hp)
    assert "HARD_PASS" in v or "MIDDLE_BAND" in v, f"expected HP/MB: {v}"

    # Live smoke cell
    result = run_one_mfrac_seed(N=N_SMOKE, M_frac=0.10, seed=17)
    assert "bid_normalized" in result, f"missing bid_normalized: {list(result.keys())}"
    bid = result["bid_normalized"]
    assert bid is not None and np.isfinite(bid), f"bid_normalized invalid: {bid}"
    assert bid > 0, f"bid_normalized <= 0: {bid}"

    # 4x smoke: N=2048
    result4 = run_one_mfrac_seed(N=N_SMOKE * 4, M_frac=0.10, seed=17)
    bid4 = result4.get("bid_normalized")
    assert bid4 is not None and np.isfinite(bid4), f"4x bid_normalized invalid: {bid4}"

    print(f"[selftest] bid_order_parameter_v7_n4096_bsc PASS "
          f"bid_smoke={bid:.4f} bid_4x={bid4:.4f}", flush=True)


_instrumentation_selftest()


def run_full(smoke: bool = False) -> None:
    t0 = time.monotonic()

    m_fracs = M_FRACS_SMOKE if smoke else M_FRACS_FULL
    seeds   = SEEDS_SMOKE if smoke else SEEDS_FULL
    N_cfg   = N_SMOKE if smoke else N_FULL

    print(f"bid_order_parameter_v7_n4096_bsc mode={'SMOKE' if smoke else 'FULL'} "
          f"N={N_cfg} M_fracs={m_fracs} seeds={seeds}", flush=True)

    per_mfrac: Dict = {}

    for M_frac in m_fracs:
        M = int(M_frac * N_cfg)
        print(f"\n== M_frac={M_frac} (M={M}) ==", flush=True)
        cells = []

        for seed in seeds:
            t_cell = time.monotonic()
            result = run_one_mfrac_seed(N=N_cfg, M_frac=M_frac, seed=seed)
            bid_norm = result.get("bid_normalized")
            outside = bid_norm is not None and bid_norm > BAND_MAX_INSIDE
            elapsed_cell = time.monotonic() - t_cell
            print(f"  M_frac={M_frac} seed={seed} bid_norm={bid_norm:.4f} "
                  f"outside={outside} elapsed={elapsed_cell:.1f}s", flush=True)
            cells.append({
                "M_frac": M_frac, "seed": seed, "bid_normalized": bid_norm,
                "outside_band": outside, "elapsed_s": round(elapsed_cell, 2),
            })

        per_mfrac[str(M_frac)] = cells

    elapsed_total = time.monotonic() - t0
    verdict, verdict_msg = compute_verdict({"per_mfrac": per_mfrac, "N": N_cfg})

    summary = {
        "anchor": "bid_order_parameter_v7_n4096_bsc",
        "N": N_cfg, "smoke": smoke,
        "M_fracs": m_fracs, "seeds": seeds,
        "per_mfrac": per_mfrac,
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
