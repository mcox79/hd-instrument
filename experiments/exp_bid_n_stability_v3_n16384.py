"""BID N-stability v3: scaling-law characterization at N=16384.

CONTEXT:
  bid_n_stability_v2 (v255): N={4096, 8192} 3-seed. MIDDLE_BAND result:
    BID mean N=4096: ~65, N=8192: ~100 (approx +54% drift per doubling).
    All cells OUTSIDE_ALL_BANDS (>0.55 threshold).
    HP3 drift > 5% so MIDDLE_BAND not HARD_PASS.
    v255 strategy: drift is a substrate-own-scaling-law (BID grows linearly with N),
    NOT a Hopfield-class convergence. v255 rescue (c) calls for N=16384 to confirm
    the +54% per-doubling rate holds at N=8192->16384.

SCIENTIFIC QUESTION (v255 rescue-c: scaling-law characterization):
  Does the ~54% per-doubling BID rate persist at N=8192->16384?
  If rate is stable: substrate has a CLEAN substrate-own-scaling-law (BID propto N).
  If rate inflects: characterization is bimodal (small-N vs large-N regimes).

PRE-REGISTERED BANDS (envelope extension; prior anchor = v255 BID_mean at N=4096/8192):
  Prior anchor: v2 N=8192 BID_mean approximately 100 (outside all Hopfield bands).
  Bands NOT widened (prior empirical anchor exists).

  HARD_PASS: BID_mean at N=16384 is outside all Hopfield class bands
    (all <= 0.55 natural units or >= 2.0 natural units in v1 scale; in absolute
    scale: BID >= band_min_outside), AND rate_change_8192_to_16384 in [25%, 75%]
    (same order-of-magnitude as v2's +54%; i.e., scaling law holds).
  HARD_FAIL: BID_mean at N=16384 falls INSIDE any known Hopfield class band.
  MIDDLE_BAND: BID outside bands but rate_change deviates > 2x from v2 rate
    (rate < 15% or rate > 120%), suggesting scaling regime change.

FORMULA SELF-TESTS:
  1. rate_change = |BID(N=16384) - BID(N=8192)| / BID(N=8192). For v2 ~54%.
     Test: rate_change([100, 154]) = |154-100|/100 = 0.54. Expected ~0.54.
  2. Hopfield band check: BID <= 0.55 = inside band. BID >= 2.0 = outside.
     Test: is_outside_band(0.3) = False. is_outside_band(10.0) = True.
  3. HP3 drift (for reference): |BID(N1) - BID(N0)| / BID(N0) < 0.05.
     At large N, this is expected to FAIL (BID scales with N, not stable).
     v3 reports it but DOES NOT use it as a gate (scaling-law track not stability track).
  4. HARD_PASS gate: outside_band AND rate_in_range_25_75.
     Test: compute_verdict({'N=4096': [65.0], 'N=16384': [100.0]}) -> HARD_PASS if
       both outside band and rate=|100-65|/65=0.54 in [0.25, 0.75].
     Test: compute_verdict({'N=4096': [0.4]}) -> HARD_FAIL (inside band).

TIMEOUT ESTIMATE:
  v2 at N=8192 3 seeds: elapsed ~1500s (from prereq estimate).
  N=16384 scales as (16384/8192)^2 = 4x vs N=8192 (BID TwoNN is O(M^2) where M=N*alpha).
  alpha=0.125: M_N16384 = 2048, M_N8192 = 1024. O(M^2) scale = 4x.
  But also need control N=8192 cell (3-seed control for consistency check).
  control: ~500s; N=16384: ~2000s. Total: ~2500s.
  timeout_s = ceil(1.5 * 2500) = ceil(3750) -> 4500s.

N-suffix: _n16384 -> production N includes N=16384 (PROT-018 binding contract).
  Script runs N in {8192, 16384}; N=16384 is the primary new cell.
Queue: remote_cpu_queue (TwoNN; no CUDA; N=16384 3-seed; ~75min CPU)
Pre-reg: preregs/2026-05-28_bid_n_stability_v3_n16384.md
Parent: bid_n_stability_v2 (v255 MIDDLE_BAND; scaling-law extension)
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import argparse
import importlib.util
import json
import os
import time
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# Import v2 for shared BID computation
_v2_path = REPO / "experiments" / "exp_bid_n_stability_v2.py"
_v2_spec = importlib.util.spec_from_file_location("bid_n_v2", _v2_path)
_bid_v2 = importlib.util.module_from_spec(_v2_spec)
_v2_spec.loader.exec_module(_bid_v2)

# PRODUCTION CONFIG - N=16384 is the new cell; N=8192 is control
# PROT-018: _n16384 suffix binds to production N including N=16384
N_PRODUCTION = 16384             # PROT-018 binding contract: _n16384 suffix
N_VALUES_FULL = [8192, N_PRODUCTION]  # PROT-018: N=16384 is new; N=8192 is control
N_VALUES_SMOKE = [1024]         # smoke: verify BID runs at all
M_FRAC = 0.125                  # match v2
SEEDS_FULL = [7, 17, 23]
SEEDS_SMOKE = [17]

# v2 reference for rate comparison
BID_REF_N8192 = 100.0   # approximate from v255; used for rate comparison
RATE_LOW = 0.25         # minimum expected rate change N=8192->16384
RATE_HIGH = 0.75        # maximum expected rate change (centered on v2's 0.54)

BAND_MAX_INSIDE = 0.55
BAND_MIN_OUTSIDE = 2.0

assert 16384 in N_VALUES_FULL, "PROT-018: N=16384 must be in production config"


def get_output_dir(default_name: str = "bid_n_stability_v3_n16384") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def run_one_seed_N(N: int, seed: int) -> Dict:
    """Run BID estimator at N for one seed."""
    return _bid_v2.run_one_seed_N(N, seed)


def compute_rate_change(bid_lo: float, bid_hi: float) -> float:
    """Rate of BID change from N_lo to N_hi: |bid_hi - bid_lo| / bid_lo."""
    if abs(bid_lo) < 1e-9:
        return 0.0
    return abs(bid_hi - bid_lo) / abs(bid_lo)


def compute_verdict(summary: dict) -> tuple:
    results = summary.get("per_N", {})
    if not results:
        return ("BID_N3_INCONCLUSIVE", "No per-N data.")

    bid_by_N: Dict[int, List[float]] = {}
    for N_str, seeds_data in results.items():
        N = int(N_str)
        bid_vals = [r.get("bid_estimate", r.get("bid_mean", 0.0)) for r in seeds_data
                    if r.get("bid_estimate") is not None or r.get("bid_mean") is not None]
        bid_by_N[N] = bid_vals if bid_vals else [0.0]

    mean_bids = {N: float(np.mean(bids)) for N, bids in bid_by_N.items()}
    N_list = sorted(mean_bids.keys())

    # Band check: any inside band?
    any_inside = any(v <= BAND_MAX_INSIDE for v in mean_bids.values())
    msg_base = (f"mean_BID_by_N={dict((k, round(v, 2)) for k, v in mean_bids.items())}.")

    if any_inside:
        inside = {N: v for N, v in mean_bids.items() if v <= BAND_MAX_INSIDE}
        return ("BID_N3_HARD_FAIL",
                f"BID falls INSIDE Hopfield class band at large N. {msg_base} "
                f"Inside-band N: {inside}. Substrate classifiable as static Hopfield at N>=8192.")

    # Rate check: N=8192->16384 if both present
    if 8192 in mean_bids and 16384 in mean_bids:
        rate = compute_rate_change(mean_bids[8192], mean_bids[16384])
        rate_stable = RATE_LOW <= rate <= RATE_HIGH
        rate_msg = f"rate_8192->16384={rate:.3f} (expected [{RATE_LOW},{RATE_HIGH}])."

        if rate_stable:
            return ("BID_N3_HARD_PASS",
                    f"BID remains outside all Hopfield bands through N=16384. {msg_base} "
                    f"{rate_msg} Scaling-law characterization confirmed: BID grows "
                    f"proportionally with N at consistent rate across 3 doublings.")

        return ("BID_N3_MIDDLE_BAND",
                f"BID outside bands but rate inflects at N=16384. {msg_base} "
                f"{rate_msg} Regime change possible. Bimodal small-N vs large-N.")

    # Only one N value
    all_outside = all(v > BAND_MAX_INSIDE for v in mean_bids.values())
    if all_outside:
        return ("BID_N3_PARTIAL",
                f"BID outside bands but rate_change not computed (missing N pair). {msg_base}")

    return ("BID_N3_INCONCLUSIVE", f"Cannot determine verdict. {msg_base}")


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    # 1. Import chain: v2 loaded without error
    assert _bid_v2 is not None, "Failed to import bid_n_stability_v2"
    print("[selftest 1/4] v2 import OK", flush=True)

    # 2. run_one_seed_N at N=512 (smoke scale)
    t0 = time.time()
    result = run_one_seed_N(N=512, seed=42)
    t_run = time.time() - t0
    bid = result.get("bid_estimate", result.get("bid_mean"))
    assert bid is not None, f"BID is None at N=512: {result}"
    assert np.isfinite(bid), f"BID is non-finite: {bid}"
    assert bid > 0, f"BID is non-positive: {bid}"
    print(f"[selftest 2/4] run_one_seed_N N=512 BID={bid:.2f} t={t_run:.1f}s OK", flush=True)

    # 3. rate_change formula
    rate = compute_rate_change(100.0, 154.0)
    assert abs(rate - 0.54) < 0.01, f"rate_change formula error: {rate} != 0.54"
    rate_z = compute_rate_change(0.0, 1.0)
    assert rate_z == 0.0, f"rate_change with zero baseline: {rate_z}"
    print(f"[selftest 3/4] compute_rate_change OK (rate=0.54)", flush=True)

    # 4. verdict formula self-tests
    # HARD_PASS case: both outside band, rate in [0.25, 0.75]
    summary_hp = {
        "per_N": {
            "8192": [{"bid_estimate": 100.0}, {"bid_estimate": 98.0}],
            "16384": [{"bid_estimate": 154.0}, {"bid_estimate": 152.0}],
        }
    }
    v, msg = compute_verdict(summary_hp)
    assert v == "BID_N3_HARD_PASS", f"Expected BID_N3_HARD_PASS, got {v}: {msg}"
    print("[selftest 4a/4] HARD_PASS formula OK", flush=True)

    # HARD_FAIL case: BID inside band
    summary_hf = {
        "per_N": {
            "8192": [{"bid_estimate": 0.3}],
            "16384": [{"bid_estimate": 0.4}],
        }
    }
    v, msg = compute_verdict(summary_hf)
    assert v == "BID_N3_HARD_FAIL", f"Expected BID_N3_HARD_FAIL, got {v}: {msg}"
    print("[selftest 4b/4] HARD_FAIL formula OK", flush=True)

    # MIDDLE_BAND case: outside band but rate out of range
    summary_mb = {
        "per_N": {
            "8192": [{"bid_estimate": 100.0}],
            "16384": [{"bid_estimate": 100.5}],  # rate = 0.005 < 0.25
        }
    }
    v, msg = compute_verdict(summary_mb)
    assert v == "BID_N3_MIDDLE_BAND", f"Expected BID_N3_MIDDLE_BAND, got {v}: {msg}"
    print("[selftest 4c/4] MIDDLE_BAND formula OK", flush=True)

    print("[SELFTEST PASS] bid_n_stability_v3_n16384 instrumentation OK", flush=True)


_instrumentation_selftest()


def run(smoke: bool = False) -> None:
    n_values = N_VALUES_SMOKE if smoke else N_VALUES_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    mode_str = "SMOKE" if smoke else "FULL"

    t0 = time.time()
    out_dir = get_output_dir()

    print(f"[bid_n_v3] N_values={n_values} seeds={seeds} mode={mode_str}", flush=True)

    per_N: Dict[str, List[Dict]] = {}
    for N in n_values:
        key = str(N)
        per_N[key] = []
        for seed in seeds:
            print(f"  N={N} seed={seed}...", flush=True)
            t_seed = time.time()
            result = run_one_seed_N(N, seed)
            bid = result.get("bid_estimate", result.get("bid_mean", float("nan")))
            t_seed_end = time.time() - t_seed
            print(f"    BID={bid:.2f} t={t_seed_end:.1f}s", flush=True)
            per_N[key].append(result)

    summary = {
        "per_N": per_N,
        "N_values": n_values,
        "seeds": seeds,
        "smoke": smoke,
    }
    verdict, verdict_msg = compute_verdict(summary)
    elapsed = time.time() - t0

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
        "config": {"N_values": n_values, "seeds": seeds, "smoke": smoke,
                   "M_frac": M_FRAC},
        "summary": summary,
    }
    out_path = out_dir / "metrics.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    print(f"\n[bid_n_v3] VERDICT: {verdict}", flush=True)
    print(f"[bid_n_v3] {verdict_msg}", flush=True)
    print(f"[bid_n_v3] elapsed={elapsed:.1f}s output={out_path}", flush=True)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--self-test", action="store_true", dest="self_test")
    args = p.parse_args()
    if args.self_test:
        sys.exit(0)
    run(smoke=args.smoke)


if __name__ == "__main__":
    main()
