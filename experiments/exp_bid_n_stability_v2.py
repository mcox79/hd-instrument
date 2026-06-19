"""BID N-stability v2: HP3 gate at N=4096 and N=8192.

CONTEXT (from v247 strategy priorities, item 1):
  exp_bid_substrate_probe_v1 (v247) added HP3 stability gate
  (BID variance-across-N < 5%) but ONLY tested N=512-2048.
  v229/v230 tested N=1024-8192 but WITHOUT the HP3 gate.

  This probe fills the gap: run the v1 HP3-gated script at N=4096 and N=8192
  to confirm BID remains stable (low variance) at production scales.

SCIENTIFIC QUESTION:
  At N in {4096, 8192}: does BID remain outside all three Hopfield class bands
  (symmetric-HN band ~0.35-0.55 natural units; dense-AM band ~0.25-0.45;
  pattern-retrieval-Hopfield band ~0.15-0.35) with < 5% variance across seeds?

  v1 HARD_PASS at N=1024-2048: BID_mean ~46.95 +- 5.90 (all outside Hopfield bands).
  This probe extends to N=4096 and N=8192 to confirm N-scaling does not push
  BID into any known class band.

PRE-REGISTERED BANDS (envelope extension, prior anchor exists):
  Prior anchor: v1 BID_mean ~46.95 at N=512-2048.
  Bands NOT widened (prior anchor exists per calibration-probe policy).

  HARD_PASS (HP3): BID_mean at N=4096 and N=8192 BOTH outside all 3 Hopfield class
    bands (all <= 0.55 natural units or >= 2.0 natural units), AND
    variance_across_N_seeds < 5% of mean.
    Confirms substrate remains classifiably outside static Hopfield taxonomy at production scale.
  HARD_FAIL: BID_mean at N=4096 OR N=8192 falls INSIDE any known Hopfield class band
    (0.15 <= BID <= 0.55 natural units).
  MIDDLE_BAND: BID outside bands but variance >= 5% (unstable N-scaling).

FORMULA SELF-TESTS:
  1. BID estimator converges to dimension d of intrinsic manifold.
  2. For random BSC vectors in R^N with M patterns: intrinsic dimension near log(M) or N.
     At N=4096, M=512 (ALPHA=0.125): intrinsic dim != random dimension.
  3. Hopfield class bands in natural units: symmetric-HN [0.35, 0.55], dense-AM [0.25, 0.45],
     pattern-retrieval-Hopfield [0.15, 0.35]. Substrate HARD_PASS requires BID outside all.
  4. variance_across_seeds = std(BID_seeds) / mean(BID_seeds). For v1 at N=1024:
     BID=46.95+-5.90 -> variance = 5.90/46.95 = 12.6% (this is MIDDLE_BAND by HP3).
     NOTE: v247 verdict_msg says BID=46.95+-5.90 but HP3 is < 5% variance...
     Actually check: v247 says "bid=46.95+/-5.90 outside Hopfield static bands" and
     "sigma_margin=7.54" = 7.54 sigma away from nearest band. HP3 is about N-stability
     (BID doesn't drift as N increases), not seed-variance. Re-read: "HP3: BID mean
     does not change by > 5% as N doubles (N=512 -> N=1024 -> N=2048)."
     Correction: HP3 = N-scaling stability, not seed variance.
  5. HP3 formula: |BID(N_high) - BID(N_low)| / BID(N_low) < 0.05 (< 5% drift as N doubles).

TIMEOUT ESTIMATE:
  BID TwoNN estimator at N=4096, 3 seeds: O(N^2) distance matrix computation.
  N=4096: 4096^2 * 4 bytes = 64MB per seed. Feasible.
  smoke N=1024 1 seed: ~3s.
  Full N=4096+8192, 3 seeds each: scale = (4096/1024)^2 * 3 = 48 at N=4096,
    (8192/1024)^2 * 3 = 192 at N=8192. Total = 3 + 48*3 + 192*3 = 3 + 144 + 576 = 723s.
  timeout_s = ceil(1.5 * 723) = ceil(1084) -> 1500s.
  Note: BID at N=8192 requires distance matrix O(M^2) where M=1024. O(N^2) for W store.

N-suffix: no _nN suffix; production N in {4096, 8192} (PROT-018: stated explicitly).
Queue: remote_cpu_queue (TwoNN; no CUDA; N={4096,8192} 3-seed each)
Pre-reg: preregs/2026-05-27_bid_n_stability_v2.md
Parent: bid_substrate_probe_v1 (v247 HARD_PASS at N=512-2048; this extends to N=4096+8192)
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
from typing import Dict, List

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# Load BID estimator from bid_substrate_probe_v1
_bid_path = REPO / "experiments" / "exp_bid_substrate_probe_v1.py"
_bid_spec = importlib.util.spec_from_file_location("bid_v1", _bid_path)
_bid_v1 = importlib.util.module_from_spec(_bid_spec)
_bid_spec.loader.exec_module(_bid_v1)

# PRODUCTION CONFIG
N_VALUES_FULL = [4096, 8192]   # PROT-018: stated explicitly
N_VALUES_SMOKE = [1024]         # smoke at N=1024 (already in v1's range; cheap verification)
M_FRAC = 0.125                  # M = N * M_FRAC (matches v1)
SEEDS_FULL = [7, 17, 23]
SEEDS_SMOKE = [17]

# Hopfield class bands (in natural units): all <= 0.55 or >= 2.0 = outside all
BAND_MAX_INSIDE = 0.55          # <= this = inside some Hopfield band
BAND_MIN_OUTSIDE = 2.0          # >= this = clearly outside all Hopfield bands (BID >2)

# HP3: N-scaling stability gate
HP3_DRIFT_FRAC = 0.05           # BID drift < 5% as N doubles

# HARD_PASS: outside bands + stable
HP_SIGMA_MARGIN = 2.0           # BID at least 2-sigma from nearest band
HF_INSIDE_BAND = 0.55           # HARD_FAIL: BID inside this threshold


def get_output_dir(default_name: str = "bid_n_stability_v2") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def run_one_seed_N(N: int, seed: int) -> Dict:
    """Run BID estimator at N for one seed."""
    return _bid_v1.run_one_seed(N, seed)


def compute_n_drift(bid_by_N: dict) -> float:
    """Compute max BID drift as N doubles."""
    N_vals = sorted(bid_by_N.keys())
    if len(N_vals) < 2:
        return 0.0
    drifts = []
    for i in range(len(N_vals) - 1):
        N_lo, N_hi = N_vals[i], N_vals[i + 1]
        bid_lo = np.mean(bid_by_N[N_lo])
        bid_hi = np.mean(bid_by_N[N_hi])
        if abs(bid_lo) > 1e-9:
            drifts.append(abs(bid_hi - bid_lo) / abs(bid_lo))
    return max(drifts) if drifts else 0.0


def compute_verdict(summary: dict) -> tuple:
    results = summary.get("per_N", {})
    if not results:
        return ("BID_N_STABILITY_INCONCLUSIVE", "No per-N data.")

    bid_by_N = {}
    for N_str, seeds_data in results.items():
        N = int(N_str)
        bid_vals = [r.get("bid_estimate", r.get("bid_mean", 0.0)) for r in seeds_data
                    if r.get("bid_estimate") is not None or r.get("bid_mean") is not None]
        bid_by_N[N] = bid_vals if bid_vals else [0.0]

    # Check band membership
    any_inside_band = False
    mean_bids = {}
    for N, bids in bid_by_N.items():
        m = float(np.mean(bids))
        mean_bids[N] = m
        if m <= BAND_MAX_INSIDE:
            any_inside_band = True

    # N-drift HP3
    n_drift = compute_n_drift(bid_by_N)

    n_list = sorted(mean_bids.keys())
    bid_vals_all = [mean_bids[N] for N in n_list]
    msg_base = (f"mean_BID_by_N={dict((k, round(v, 2)) for k, v in mean_bids.items())}. "
                f"n_drift={n_drift:.3f}. any_inside_band={any_inside_band}.")

    if any_inside_band:
        return ("BID_N_HARD_FAIL",
                f"BID falls INSIDE Hopfield class band at large N. {msg_base} "
                f"Substrate is classifiable as static Hopfield at N>=4096.")

    all_outside = all(v > BAND_MAX_INSIDE for v in bid_vals_all)
    hp3_stable = n_drift < HP3_DRIFT_FRAC

    if all_outside and hp3_stable:
        return ("BID_N_HARD_PASS",
                f"BID remains OUTSIDE all Hopfield class bands through N=8192. {msg_base} "
                f"HP3 N-stability confirmed (drift={n_drift:.3f} < {HP3_DRIFT_FRAC}). "
                f"Non-static-Hopfield classification holds at production scale.")

    if all_outside and not hp3_stable:
        return ("BID_N_MIDDLE_BAND",
                f"BID outside bands but drifts significantly with N. {msg_base} "
                f"N-stability weak (drift={n_drift:.3f} >= {HP3_DRIFT_FRAC}).")

    return ("BID_N_INCONCLUSIVE", f"Unexpected result. {msg_base}")


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    # Self-test 1: run_one_seed at small N
    t0 = time.time()
    r = run_one_seed_N(512, seed=17)
    t1 = time.time() - t0
    bid_key = "bid_estimate" if "bid_estimate" in r else "bid_mean"
    assert bid_key in r, f"missing bid_estimate/bid_mean: {r.keys()}"
    assert r[bid_key] > 0, f"bid <= 0: {r[bid_key]}"
    print(f"[selftest 1/3] run_one_seed N=512 bid={r[bid_key]:.2f} t={t1:.1f}s OK",
          flush=True)

    # Self-test 2: n_drift formula
    bid_by_N_test = {1024: [40.0, 41.0], 2048: [42.0, 43.0]}
    drift = compute_n_drift(bid_by_N_test)
    expected = abs(42.5 - 40.5) / 40.5
    assert abs(drift - expected) < 0.01, f"n_drift formula: {drift} vs {expected}"
    print(f"[selftest 2/3] n_drift formula OK ({drift:.3f})", flush=True)

    # Self-test 3: verdict formula
    # HARD_PASS: outside bands, stable
    summary_hp = {"per_N": {
        "4096": [{"bid_estimate": 45.0, "N": 4096, "seed": 17}],
        "8192": [{"bid_estimate": 46.0, "N": 8192, "seed": 17}],
    }}
    v, msg = compute_verdict(summary_hp)
    assert v == "BID_N_HARD_PASS", f"Expected HARD_PASS, got {v}: {msg}"

    # HARD_FAIL: BID inside band
    summary_hf = {"per_N": {
        "4096": [{"bid_estimate": 0.40, "N": 4096, "seed": 17}],
    }}
    v, msg = compute_verdict(summary_hf)
    assert v == "BID_N_HARD_FAIL", f"Expected HARD_FAIL, got {v}: {msg}"
    print(f"[selftest 3/3] verdict formulas OK", flush=True)

    print("[SELFTEST PASS] bid_n_stability_v2 instrumentation OK", flush=True)


_instrumentation_selftest()


def run(smoke: bool = False) -> None:
    t0 = time.time()
    N_values = N_VALUES_SMOKE if smoke else N_VALUES_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    mode_str = "SMOKE" if smoke else "FULL"

    out_dir = get_output_dir()
    print(f"[bid_n_v2] N_values={N_values} seeds={seeds} mode={mode_str}", flush=True)

    per_N = {}
    for N in N_values:
        per_N[str(N)] = []
        for seed in seeds:
            t_seed = time.time()
            r = run_one_seed_N(N, seed)
            per_N[str(N)].append(r)
            bid_val = r.get("bid_estimate", r.get("bid_mean", float("nan")))
            print(f"  N={N} seed={seed}: bid={bid_val:.2f} "
                  f"t={time.time()-t_seed:.1f}s", flush=True)

    summary = {"per_N": per_N, "N_values": N_values, "seeds": seeds, "smoke": smoke}
    verdict, verdict_msg = compute_verdict(summary)
    elapsed = time.time() - t0

    metrics = {
        "verdict": verdict, "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
        "config": {"N_values": N_values, "seeds": seeds, "smoke": smoke},
        "summary": summary,
    }
    out_path = out_dir / "metrics.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    print(f"\n[bid_n_v2] VERDICT: {verdict}", flush=True)
    print(f"[bid_n_v2] {verdict_msg}", flush=True)
    print(f"[bid_n_v2] elapsed={elapsed:.1f}s output={out_path}", flush=True)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--self-test", action="store_true", dest="self_test")
    p.add_argument("--timeout", type=float, default=5400.0)
    args = p.parse_args()
    if args.self_test:
        sys.exit(0)
    run(smoke=args.smoke)


if __name__ == "__main__":
    main()
