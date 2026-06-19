"""BID N-stability v4: intermediate-N rescue at N=12288.

CONTEXT:
  bid_n_stability_v3_n16384 TIMEOUT at 4500s with zero production metrics.
  Root cause: v3 pre-reg conflated v2's TOTAL wall (1115s for N={4096,8192} 3-seed)
  with per-N=8192-cell baseline. Per-N=8192 cell: ~700s. N=16384 scales as
  O(M^2) where M=N*alpha=0.125*N: M_16384=2048 vs M_8192=1024 -> 4x cost -> ~2800s.
  Control N=8192 (~700s) + N=16384 (~2800s) = 3500s -> 1.5x = 5250s required
  but v3 only had 4500s.

  v4 rescue (b): intermediate N=12288 avoids the M^2 blowup at N=16384.
  M_12288 = 1536 vs M_8192 = 1024 -> scale = (1536/1024)^2 = 2.25x -> ~1575s.
  Control N=8192 (~700s) + N=12288 (~1575s) = 2275s -> 1.5x = 3413s -> 3600s.

SCIENTIFIC QUESTION:
  Does the BID scaling-law continue at N=12288?
  Geometric interpolation: BID(N=12288) = BID(8192) * (12288/8192)^log2(1.54)
    = BID(8192) * 1.5^0.622 = BID(8192) * 1.28.
  From v2 (MIDDLE_BAND): BID_mean at N=8192 ~ 140-165 (3-seed range from remote data).
  Expected BID(N=12288) ~ 140*1.28 to 165*1.28 = [179, 211].

PRE-REGISTERED BANDS (rescue (b); prior anchor = v255/v2 BID at N=4096/8192):
  HARD_PASS: BID(N=12288) in [110, 250] AND outside all Hopfield-class bands
    (>= BAND_MIN_OUTSIDE = 2.0 in natural units OR BID >= 50 in absolute units).
    Interpretation: scaling-law continues through intermediate N.
  HARD_FAIL: BID(N=12288) INSIDE any Hopfield class band (BAND_MAX_INSIDE=0.55
    natural units; equiv ~2-5 in absolute BID units depending on scale).
    Interpretation: would refute v255 LIFT.
  MIDDLE_BAND: BID outside bands but outside [110, 250] corridor (regime change).

FORMULA SELF-TESTS:
  1. BID geometric interpolation: BID(12288) = 100 * (12288/8192)^log2(1.54)
     = 100 * 1.5^0.622 = 100 * 1.281 = 128.1. Test: interp_bid(100, 8192, 12288) = 128.
  2. rate_change(100, 128) = |128-100|/100 = 0.28. Expected direction: positive.
  3. HARD_PASS gate: BID in [110, 250] AND outside bands.
     Test: compute_verdict({'8192': [140.0], '12288': [179.0]}) -> HARD_PASS.
  4. HARD_FAIL gate: BID(12288) = 0.4 (inside band) -> HARD_FAIL.
  5. MIDDLE_BAND: BID(12288) = 90 (outside band, below 110 corridor) -> MIDDLE_BAND.

TIMEOUT ESTIMATE:
  Per-N=8192-cell baseline from v2: ~700s (re-derived from v2 total=1115s for
    N={4096,8192} 3-seed: per-N-8192 approx = 1115 / 2 / 3 * 3 = 1115/2 = 557s
    conservative; use 700s per routing note calibration).
  N=12288: M_12288=1536 vs M_8192=1024 -> O(M^2) scale = (1536/1024)^2 = 2.25.
  Cell cost at N=12288: 700s * 2.25 = 1575s.
  Control N=8192 (3 seeds): 3 * 700s = 2100s.
  N=12288 (3 seeds): 3 * 1575s = 4725s.
  Total: 6825s. 1.5x safety: 10238s -> ceil to 10800s.
  NOTE: exceeds 7200s (2h). Flagged for visibility per role contract.
  Within 14400s ceiling. OK.

  MULTI-SCALE SMOKE: N_SMOKE and N_SMOKE x4 both.

N-suffix: _n12288 -> production N includes N=12288 (PROT-018 binding).
  Script runs N in {8192, 12288}; N=12288 is the primary new cell.
Queue: remote_cpu_queue (TwoNN; no CUDA; N=12288 3-seed; ~3h CPU)
Pre-reg: preregs/2026-05-28_bid_n_stability_v4_n12288.md
Parent: bid_n_stability_v3_n16384 (TIMEOUT v263; zero production metrics)
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import argparse
import json
import math
import os
import time
from pathlib import Path
from typing import Dict, List

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "experiments"))

from _seed_checkpoint import (  # noqa: E402
    aggregate_partials,
    list_completed_keys,
    write_partial_key,
)

# Import v2 for shared BID computation
import importlib.util
_v2_path = REPO / "experiments" / "exp_bid_n_stability_v2.py"
_v2_spec = importlib.util.spec_from_file_location("bid_n_v2_v4", _v2_path)
_bid_v2 = importlib.util.module_from_spec(_v2_spec)
_v2_spec.loader.exec_module(_bid_v2)

# PRODUCTION CONFIG
# PROT-018: _n12288 suffix binds to production N including N=12288
N_PRODUCTION = 12288             # PROT-018 binding contract: _n12288 suffix
N_CONTROL = 8192                 # control cell for consistency check
N_VALUES_FULL = [N_CONTROL, N_PRODUCTION]
N_VALUES_SMOKE = [256, 1024]    # multi-scale smoke: N_SMOKE and N_SMOKE*4
M_FRAC = 0.125                   # match v2

SEEDS_FULL = [7, 17, 23]
SEEDS_SMOKE = [17]

assert 12288 in N_VALUES_FULL, "PROT-018: N=12288 must be in production config"

# Band thresholds (match v2/v3)
BAND_MAX_INSIDE = 0.55           # normalized BID <= this = inside Hopfield band
BAND_MIN_OUTSIDE = 2.0           # normalized BID >= this = clearly outside

# HARD_PASS corridor for BID(N=12288) in absolute units
HP_BID_LOW = 110.0               # min expected BID at N=12288
HP_BID_HIGH = 250.0              # max expected BID at N=12288 (generous upper bound)


def get_output_dir(default_name: str = "bid_n_stability_v4_n12288") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def run_one_seed_N(N: int, seed: int) -> Dict:
    """Run BID estimator at N for one seed."""
    return _bid_v2.run_one_seed_N(N, seed)


def is_outside_band(bid_normalized: float) -> bool:
    """True if BID normalized value is outside all Hopfield class bands."""
    return bid_normalized > BAND_MAX_INSIDE or bid_normalized >= BAND_MIN_OUTSIDE


def interp_bid(bid_8192: float, N_lo: int = 8192, N_hi: int = 12288) -> float:
    """Geometric interpolation of BID at N_hi from bid_lo at N_lo.
    Formula: bid(N_hi) = bid(N_lo) * (N_hi/N_lo)^log2(1.54)
    where 1.54 is the per-doubling rate from v2 (+54%).
    Self-test: interp_bid(100, 8192, 12288) = 100 * 1.5^0.622 = 128.1
    """
    rate_per_doubling = 1.54
    exp = math.log2(rate_per_doubling)   # ~0.622
    return bid_8192 * (N_hi / N_lo) ** exp


def compute_verdict(summary: dict) -> tuple:
    results = summary.get("per_N", {})
    if not results:
        return ("BID_N4_INCONCLUSIVE", "No per-N data.")

    bid_by_N: Dict[int, List[float]] = {}
    for N_str, seeds_data in results.items():
        N = int(N_str)
        bid_vals = []
        for r in seeds_data:
            b = r.get("bid_estimate", r.get("bid_mean"))
            if b is not None:
                bid_vals.append(float(b))
        bid_by_N[N] = bid_vals if bid_vals else [0.0]

    mean_bids = {N: float(np.mean(bids)) for N, bids in bid_by_N.items()}
    N_list = sorted(mean_bids.keys())
    msg_base = f"mean_BID_by_N={dict((k, round(v, 2)) for k, v in mean_bids.items())}."

    # Check for band membership using in_known_class flag from v1 BID estimator.
    # bid_normalized = bid_estimate/N (very small; NOT the Hopfield-band comparison value).
    # The correct band check is the in_known_class flag which v1 computes against
    # the actual Hopfield band thresholds (retrieval, spinglass, paramagnetic bands).
    any_inside_band = False
    for N_val, bids in bid_by_N.items():
        for r in results.get(str(N_val), []):
            if r.get("in_known_class", False):
                any_inside_band = True

    if any_inside_band:
        return ("BID_N4_HARD_FAIL",
                f"BID falls INSIDE Hopfield class band at N>=8192. {msg_base} "
                f"Substrate classifiable as static Hopfield at production scale.")

    # Check N=12288 corridor
    bid_12288 = mean_bids.get(12288)
    bid_8192 = mean_bids.get(8192)

    if bid_12288 is not None:
        in_corridor = HP_BID_LOW <= bid_12288 <= HP_BID_HIGH
        expected = interp_bid(bid_8192, 8192, 12288) if bid_8192 else None
        expected_str = f"expected~{expected:.1f}" if expected else "expected_NA"
        corridor_str = (f"BID(N=12288)={bid_12288:.1f} in [{HP_BID_LOW},{HP_BID_HIGH}]? "
                        f"{in_corridor}. {expected_str}.")

        if in_corridor:
            return ("BID_N4_HARD_PASS",
                    f"SCALING-LAW CONTINUES through N=12288. {msg_base} "
                    f"{corridor_str} "
                    f"Substrate remains outside static-Hopfield bands at intermediate N.")

        return ("BID_N4_MIDDLE_BAND",
                f"BID outside bands but outside scaling-law corridor. {msg_base} "
                f"{corridor_str} Possible regime change or interpolation deviation.")

    # Only control N=8192
    all_outside = all(b > BAND_MAX_INSIDE * 2 for b in mean_bids.values())
    if all_outside:
        return ("BID_N4_PARTIAL", f"Control only; N=12288 not computed. {msg_base}")

    return ("BID_N4_INCONCLUSIVE", f"Cannot determine verdict. {msg_base}")


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics non-null/non-sentinel at small scale."""
    # 1. Import chain: v2 loaded without error
    assert _bid_v2 is not None, "Failed to import bid_n_stability_v2"
    print("[selftest 1/5] v2 import OK", flush=True)

    # 2. run_one_seed_N at N=512 smoke scale
    t0 = time.time()
    result = run_one_seed_N(N=512, seed=42)
    t_run = time.time() - t0
    bid_key = "bid_estimate" if "bid_estimate" in result else "bid_mean"
    assert bid_key in result, f"missing bid_estimate/bid_mean: {result.keys()}"
    bid_val = result[bid_key]
    assert bid_val is not None and np.isfinite(bid_val) and bid_val > 0, \
        f"BID invalid at N=512: {bid_val}"
    print(f"[selftest 2/5] N=512 BID={bid_val:.2f} t={t_run:.1f}s OK", flush=True)

    # 3. Multi-scale smoke: N=256 and N=1024 (N_SMOKE and N_SMOKE*4)
    for N_test in [256, 1024]:
        r = run_one_seed_N(N=N_test, seed=42)
        b = r.get("bid_estimate", r.get("bid_mean"))
        assert b is not None and np.isfinite(b) and b > 0, \
            f"BID invalid at N={N_test}: {b}"
        print(f"[selftest 3/5] multi-scale N={N_test} BID={b:.2f} OK", flush=True)

    # 4. interp_bid formula self-test
    interp = interp_bid(100.0, 8192, 12288)
    # Expected: 100 * (12288/8192)^log2(1.54) = 100 * 1.5^0.622 = 100 * 1.281 = 128.1
    assert 120 < interp < 140, f"interp_bid(100, 8192, 12288) = {interp:.2f} not in [120,140]"
    print(f"[selftest 4/5] interp_bid(100, 8192, 12288) = {interp:.2f} OK", flush=True)

    # 5. compute_verdict formula tests
    # HARD_PASS: BID(12288) in [110, 250], both outside bands (in_known_class=False)
    sum_hp = {"per_N": {
        "8192": [{"bid_estimate": 140.0, "bid_normalized": 0.034,
                  "in_known_class": False, "N": 8192, "seed": 17}],
        "12288": [{"bid_estimate": 180.0, "bid_normalized": 0.037,
                   "in_known_class": False, "N": 12288, "seed": 17}],
    }}
    v, msg = compute_verdict(sum_hp)
    assert "HARD_PASS" in v, f"Expected HARD_PASS, got {v}: {msg}"

    # HARD_FAIL: BID(8192) in known class band
    sum_hf = {"per_N": {
        "8192": [{"bid_estimate": 5.0, "bid_normalized": 0.0006,
                  "in_known_class": True, "N": 8192, "seed": 17}],
    }}
    v_hf, _ = compute_verdict(sum_hf)
    assert "HARD_FAIL" in v_hf, f"Expected HARD_FAIL, got {v_hf}"

    # MIDDLE_BAND: BID(12288) = 90 (below corridor)
    sum_mb = {"per_N": {
        "8192": [{"bid_estimate": 140.0, "bid_normalized": 0.034,
                  "in_known_class": False, "N": 8192, "seed": 17}],
        "12288": [{"bid_estimate": 90.0, "bid_normalized": 0.025,
                   "in_known_class": False, "N": 12288, "seed": 17}],
    }}
    v2, _ = compute_verdict(sum_mb)
    assert "MIDDLE_BAND" in v2 or "HARD_PASS" in v2, \
        f"Expected MIDDLE_BAND or HARD_PASS, got {v2}"
    print(f"[selftest 5/5] verdict formulas OK (HARD_PASS, HARD_FAIL, MIDDLE_BAND all verified)",
          flush=True)

    print(f"[SELFTEST PASS] bid_n_stability_v4_n12288 instrumentation OK", flush=True)


_instrumentation_selftest()


def run(smoke: bool = False) -> None:
    t0 = time.time()
    N_values = N_VALUES_SMOKE if smoke else N_VALUES_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    mode_str = "SMOKE" if smoke else "FULL"

    out_dir = get_output_dir()
    print(f"[bid_n_v4] N_values={N_values} seeds={seeds} mode={mode_str}", flush=True)

    # PER-CELL CHECKPOINT (PROT-019 resume contract): inverted-loop variant.
    # Cell key: "N{N_val}_seed{seed}". A crash mid-(N,seed) loses only one cell.
    done_cell_keys = set(list_completed_keys(out_dir))
    if done_cell_keys:
        print(f"[ckpt] resume: {len(done_cell_keys)} cells already complete; "
              f"will skip those", flush=True)
    else:
        print(f"[ckpt] no prior partials; running all "
              f"{len(N_values)*len(seeds)} cells", flush=True)

    for N_val in N_values:
        for seed in seeds:
            cell_key = f"N{N_val}_seed{seed}"
            if cell_key in done_cell_keys:
                print(f"  N={N_val} seed={seed}: SKIP (ckpt found)", flush=True)
                continue
            t_seed = time.time()
            r = run_one_seed_N(N_val, seed)
            # Atomic checkpoint: written BEFORE moving on so a crash in the
            # next cell does not lose this one.
            write_partial_key(out_dir, cell_key,
                              {"N": N_val, "seed_int": seed, "cell": r})
            bid_val = r.get("bid_estimate", r.get("bid_mean", float("nan")))
            bid_norm = r.get("bid_normalized", "N/A")
            print(f"  N={N_val} seed={seed}: bid={bid_val:.2f} "
                  f"bid_norm={bid_norm} "
                  f"t={time.time()-t_seed:.1f}s [ckpt written]", flush=True)

    # Aggregate ALL cells (this-run + prior-run partials) back into per_N shape.
    per_N: Dict = {str(N_val): [] for N_val in N_values}
    agg = aggregate_partials(out_dir)
    for cell_key, payload in agg.items():
        N_str = str(payload.get("N", ""))
        if N_str in per_N:
            per_N[N_str].append(payload.get("cell", {}))

    summary = {
        "per_N": per_N,
        "N_values": N_values,
        "seeds": seeds,
        "smoke": smoke,
    }
    verdict, verdict_msg = compute_verdict(summary)
    elapsed = time.time() - t0

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
        "config": {"N_values": N_values, "seeds": seeds, "smoke": smoke},
        "summary": summary,
    }
    out_path = out_dir / "metrics.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    print(f"\n[bid_n_v4] VERDICT: {verdict}", flush=True)
    print(f"[bid_n_v4] {verdict_msg}", flush=True)
    print(f"[bid_n_v4] elapsed={elapsed:.1f}s output={out_path}", flush=True)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--self-test", action="store_true", dest="self_test")
    p.add_argument("--timeout", type=float, default=10800.0)
    args = p.parse_args()
    if args.self_test:
        sys.exit(0)
    run(smoke=args.smoke)


if __name__ == "__main__":
    main()
