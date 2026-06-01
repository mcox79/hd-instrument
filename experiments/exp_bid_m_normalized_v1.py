"""BID M-normalized probe v1: reconcile v251 vs v255 BID magnitude mismatch.

CONTEXT:
  bid_order_parameter_v4_full (v251): BID ~46.95 at N=1024, M~N/2 (alpha=0.5).
  bid_n_stability_v2 (v255): BID ~66 at N=1024, M=N*0.125 (alpha=0.125).
  Same N=1024, different M-density: v251 used M_FRAC~0.5, v255 used M_FRAC=0.125.
  BID difference: 46.95 vs 66 at N=1024 (~40% discrepancy).

  v255 strategy rescue (d): write a 5-cell quick probe at N=4096 sweeping
  M_FRAC to map BID-vs-M-density; close the magnitude mismatch as measurement
  protocol artifact, not substrate-physics inconsistency.

SCIENTIFIC QUESTION (v255 rescue-d):
  How does BID vary with M_FRAC at N=4096?
  Is the v251 vs v255 discrepancy explained by M_FRAC difference alone?

  If BID(M_FRAC=0.5) / BID(M_FRAC=0.125) ~= 46.95 / 66 ~= 0.71:
    Discrepancy is M-density artifact. Both are valid measurements of different regimes.
  If ratio differs substantially from 0.71:
    Either v251 or v255 has a script-level discrepancy beyond M_FRAC.

PRE-REGISTERED BANDS (calibration probe; first systematic M_FRAC sweep for BID):
  Prior anchor: v255 M_FRAC=0.125 BID~66 at N=1024; v251 M_FRAC~0.5 BID~47.
  This probe sweeps M_FRAC at N=4096; no prior N=4096 anchor.
  Bands widened to +/-50% per calibration-probe policy.

  HARD_PASS: BID monotone DECREASING as M_FRAC increases (from 0.05 to 0.50),
    AND all BID values outside Hopfield class bands (> 0.55),
    AND ratio BID(M_FRAC=0.5) / BID(M_FRAC=0.125) in [0.5, 0.9]
    (captures the v251/v255 ratio of 0.71 +/- 50%).
  HARD_FAIL: BID falls INSIDE Hopfield class band at any M_FRAC.
  MIDDLE_BAND: BID outside bands but non-monotone OR ratio outside [0.3, 1.2].

FORMULA SELF-TESTS:
  1. BID decreases as M increases: more patterns -> lower intrinsic dimension (TwoNN).
     Because at low M, points are spread; at high M, more interference -> denser cluster.
  2. Ratio v251/v255 = 46.95/66 = 0.711. Expected HARD_PASS ratio range [0.5, 0.9].
  3. is_outside_band(0.3) = False. is_outside_band(5.0) = True.
  4. monotone_decreasing([66, 60, 55, 50, 47]) = True. monotone_decreasing([66,70,55]) = False.

TIMEOUT ESTIMATE:
  BID TwoNN at N=4096, 1 seed: O(M^2) where M = N * M_FRAC.
  M_FRAC=0.125: M=512; M_FRAC=0.5: M=2048.
  Smoke N=1024 1 seed: bid_n_stability_v2 smoke was 0.9s.
  Per cell at N=4096: ~(4096/1024)^2 = 16x per seed. With 3 seeds: 0.9 * 16 * 3 = 43s per M_FRAC.
  5 M_FRAC values * 43s = 215s. timeout_s = ceil(1.5 * 215) = ceil(322) -> 600s.
  Use 1800s for safety.

N-suffix: no _nN suffix; production N = 4096 (PROT-018: stated explicitly).
Queue: remote_cpu_queue (TwoNN; no CUDA; N=4096 3-seed 5-M_FRAC; ~10-20min)
Pre-reg: preregs/2026-05-28_bid_m_normalized_v1.md
Parent: bid_n_stability_v2 (v255 rescue-d: M_FRAC reconciliation)
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

# Import v2 for shared BID computation
_v2_path = REPO / "experiments" / "exp_bid_n_stability_v2.py"
_v2_spec = importlib.util.spec_from_file_location("bid_n_v2_mfrac", _v2_path)
_bid_v2 = importlib.util.module_from_spec(_v2_spec)
_v2_spec.loader.exec_module(_bid_v2)

# PRODUCTION CONFIG
# PROT-018: no _nN suffix; N=4096 stated explicitly
N_FULL = 4096
N_SMOKE = 512

M_FRACS_FULL  = [0.05, 0.10, 0.125, 0.25, 0.50]  # spans v255 (0.125) and v251 (~0.5)
M_FRACS_SMOKE = [0.125, 0.50]

SEEDS_FULL  = [7, 17, 23]
SEEDS_SMOKE = [17]

BAND_MAX_INSIDE = 0.55
# Expected v251/v255 ratio
RATIO_EXPECTED = 0.711   # v251 ~46.95 / v255 ~66
RATIO_LOW  = 0.50
RATIO_HIGH = 0.90


def get_output_dir(default_name: str = "bid_m_normalized_v1") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def run_one_seed_Mfrac(N: int, M_frac: float, seed: int) -> Dict:
    """Run BID at N with M = N * M_frac.

    Directly builds the Hopfield substrate at the specified M_frac and
    calls the TwoNN BID estimator from bid_substrate_probe_v1.
    """
    _bid_v1 = _bid_v2._bid_v1
    rng = np.random.default_rng(seed=seed)
    M_stored = max(4, int(M_frac * N))

    # Build Hopfield W at specified M_frac
    patterns = rng.choice([-1, 1], size=(M_stored, N)).astype(np.float64)
    W = np.zeros((N, N), dtype=np.float64)
    for v in patterns:
        W += np.outer(v, v) / N
    np.fill_diagonal(W, 0.0)

    # Sample attractors (same protocol as bid_substrate_probe_v1)
    S_PROBES = getattr(_bid_v1, "S_PROBES", min(200, M_stored))
    n_samples = min(S_PROBES, M_stored)
    query_idx = rng.choice(M_stored, size=n_samples, replace=False)
    queries = patterns[query_idx].copy()
    flip_prob = 0.05
    noise_mask = rng.random(queries.shape) < flip_prob
    queries[noise_mask] *= -1.0
    attractors = np.sign(W @ queries.T).T  # (S, N)

    # BID via TwoNN from v1 (function may be named twonn_id or twonn_bid)
    twonn_fn = getattr(_bid_v1, "twonn_id", None) or getattr(_bid_v1, "twonn_bid", None)
    assert twonn_fn is not None, "Cannot find twonn_id or twonn_bid in bid_substrate_probe_v1"
    d_hat, ci_low, ci_high = twonn_fn(attractors)

    return {
        "N": N,
        "M_frac": M_frac,
        "M_stored": M_stored,
        "seed": seed,
        "bid_estimate": float(d_hat),
        "bid_ci_low": float(ci_low),
        "bid_ci_high": float(ci_high),
    }


def compute_verdict(summary: dict) -> tuple:
    per_mfrac = summary.get("per_mfrac", {})
    if not per_mfrac:
        return ("BID_M_NORM_INCONCLUSIVE", "No per-mfrac data.")

    mfracs = sorted([float(k) for k in per_mfrac.keys()])
    mean_bids = {}
    for mf_str, seeds_data in per_mfrac.items():
        mf = float(mf_str)
        bid_vals = [r.get("bid_estimate", r.get("bid_mean", 0.0)) for r in seeds_data
                    if r.get("bid_estimate") is not None or r.get("bid_mean") is not None]
        mean_bids[mf] = float(np.mean(bid_vals)) if bid_vals else 0.0

    any_inside = any(v <= BAND_MAX_INSIDE for v in mean_bids.values())
    msg_base = f"mean_BID_by_M_frac={dict((round(k,3), round(v,2)) for k, v in mean_bids.items())}."

    if any_inside:
        inside = {k: v for k, v in mean_bids.items() if v <= BAND_MAX_INSIDE}
        return ("BID_M_NORM_HARD_FAIL",
                f"BID falls INSIDE Hopfield class band. {msg_base} Inside: {inside}.")

    # Monotone check
    bid_sorted = [mean_bids[mf] for mf in mfracs]
    is_monotone = all(bid_sorted[i] >= bid_sorted[i + 1] for i in range(len(bid_sorted) - 1))

    # Ratio check
    bid_125 = mean_bids.get(0.125)
    bid_50  = mean_bids.get(0.50)
    ratio_ok = False
    ratio = None
    if bid_125 is not None and bid_50 is not None and abs(bid_125) > 1e-9:
        ratio = bid_50 / bid_125
        ratio_ok = RATIO_LOW <= ratio <= RATIO_HIGH

    ratio_msg = f"ratio(0.50/0.125)={ratio:.3f} (expected [{RATIO_LOW},{RATIO_HIGH}])." if ratio else ""

    if is_monotone and ratio_ok:
        return ("BID_M_NORM_HARD_PASS",
                f"BID monotone decreasing with M_FRAC. {msg_base} {ratio_msg} "
                f"v251/v255 magnitude mismatch is M-density artifact. Both regimes valid.")

    return ("BID_M_NORM_MIDDLE_BAND",
            f"Partial: monotone={is_monotone}, ratio_ok={ratio_ok}. {msg_base} {ratio_msg}")


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    # 1. v2 import chain
    assert _bid_v2 is not None, "v2 import failed"
    assert hasattr(_bid_v2, "_bid_v1"), "v2 missing _bid_v1 attribute"
    print("[selftest 1/4] v2 import + _bid_v1 access OK", flush=True)

    # 2. run_one_seed_Mfrac at N=512: test two M_fracs, verify BID differs
    t0 = time.time()
    result_lo = run_one_seed_Mfrac(N=512, M_frac=0.125, seed=42)
    result_hi = run_one_seed_Mfrac(N=512, M_frac=0.50, seed=42)
    bid_lo = result_lo.get("bid_estimate", result_lo.get("bid_mean"))
    bid_hi = result_hi.get("bid_estimate", result_hi.get("bid_mean"))
    assert bid_lo is not None and np.isfinite(bid_lo) and bid_lo > 0, f"BID_lo invalid: {bid_lo}"
    assert bid_hi is not None and np.isfinite(bid_hi) and bid_hi > 0, f"BID_hi invalid: {bid_hi}"
    print(f"[selftest 2/4] M_frac=0.125 BID={bid_lo:.2f}, M_frac=0.50 BID={bid_hi:.2f} "
          f"t={time.time()-t0:.1f}s OK", flush=True)

    # 3. Ratio formula
    ratio_test = 46.95 / 66.0
    assert abs(ratio_test - 0.711) < 0.01, f"ratio formula error: {ratio_test}"
    print(f"[selftest 3/4] ratio formula OK ({ratio_test:.3f})", flush=True)

    # 4. Verdict formula
    summary_hp = {
        "per_mfrac": {
            "0.125": [{"bid_estimate": 66.0}],
            "0.5": [{"bid_estimate": 47.0}],
        }
    }
    v, msg = compute_verdict(summary_hp)
    assert v == "BID_M_NORM_HARD_PASS", f"Expected BID_M_NORM_HARD_PASS: {v}: {msg}"

    summary_hf = {"per_mfrac": {"0.125": [{"bid_estimate": 0.3}]}}
    v, msg = compute_verdict(summary_hf)
    assert v == "BID_M_NORM_HARD_FAIL", f"Expected BID_M_NORM_HARD_FAIL: {v}"
    print("[selftest 4/4] verdict formulas OK", flush=True)

    print("[SELFTEST PASS] bid_m_normalized_v1 instrumentation OK", flush=True)


_instrumentation_selftest()


def run(smoke: bool = False) -> None:
    N = N_SMOKE if smoke else N_FULL
    m_fracs = M_FRACS_SMOKE if smoke else M_FRACS_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    mode_str = "SMOKE" if smoke else "FULL"

    t0 = time.time()
    out_dir = get_output_dir()

    print(f"[bid_m_norm] N={N} m_fracs={m_fracs} seeds={seeds} mode={mode_str}", flush=True)

    per_mfrac: Dict[str, List[Dict]] = {}
    for mf in m_fracs:
        key = str(round(mf, 4))
        per_mfrac[key] = []
        for seed in seeds:
            print(f"  M_frac={mf:.3f} seed={seed}...", flush=True)
            t_s = time.time()
            result = run_one_seed_Mfrac(N, mf, seed)
            bid = result.get("bid_estimate", result.get("bid_mean", float("nan")))
            print(f"    BID={bid:.2f} t={time.time()-t_s:.1f}s", flush=True)
            per_mfrac[key].append(result)

    summary = {"per_mfrac": per_mfrac, "m_fracs": m_fracs, "N": N, "smoke": smoke}
    verdict, verdict_msg = compute_verdict(summary)
    elapsed = time.time() - t0

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
        "config": {"N": N, "m_fracs": m_fracs, "seeds": seeds, "smoke": smoke},
        "summary": summary,
    }
    out_path = out_dir / "metrics.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    print(f"\n[bid_m_norm] VERDICT: {verdict}", flush=True)
    print(f"[bid_m_norm] {verdict_msg}", flush=True)
    print(f"[bid_m_norm] elapsed={elapsed:.1f}s output={out_path}", flush=True)


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
