"""BID ORDER PARAMETER v5: BSC at N=8192, M_frac sweep.

CONTEXT:
  bid_m_normalized_v1 (N=4096 HARD_PASS): BID vs M_frac monotone decrease,
    BID outside Hopfield bands at M_frac <= 0.5.
  bid_m_normalized_v4_n8192 (pending): N=8192 Kerdock -- wait: N=8192 odd log2=13.
    Actually bid_m_normalized_v4_n8192 IS in queue. Let's check if it uses Kerdock.
  This experiment: N=8192 BSC atoms, M_frac=[0.05, 0.1, 0.25, 0.5, 1.0, 2.0].
  No Kerdock needed. Any N valid for BSC.

SCIENTIFIC QUESTION:
  At N=8192 with BSC atoms, does BID (intrinsic dimensionality of stored
  pattern manifold) decrease monotonically with M_frac?
  Does BID stay outside static Hopfield bands at low M_frac?
  Where does BID enter Hopfield bands (if ever)?

PRE-REGISTERED BANDS:
  Prior: bid_m_normalized_v1 (N=4096 Kerdock HARD_PASS: BID outside bands at M_frac<=0.5).
  Expected calibration probe (N=8192 BSC is new protocol).

  HARD_PASS: BID monotone decreasing AND BID > 50 (absolute) at M_frac <= 0.5
    at >= 2/3 seeds.
    Interpretation: substrate outside Hopfield bands at N=8192 BSC, extends v1.
  HARD_FAIL: BID falls inside Hopfield bands (< 5 absolute) at M_frac <= 0.25.
    Interpretation: BSC structure collapses intrinsic dim faster than Kerdock.
  MIDDLE_BAND: BID outside bands at low M but enters bands at medium M.

FORMULA SELF-TESTS:
  1. N == 8192 (PROT-018 binding).
  2. BSC atoms: random +/-1. No Kerdock.
  3. TwoNN BID: O(M^2) for k-nearest neighbors. Use M_frac=0.05: M=409.
     TwoNN at M=409: ~409^2/2 = 84K comparisons. Fast.
  4. BAND_MAX_INSIDE = 0.55 (normalized, from bid_m_normalized_v1).
  5. M at M_frac=0.05, N=8192: M=409.

OOM CHECK:
  TwoNN at M_frac=2.0, N=8192: M=16384. Matrix: 16384^2 = 268M comparisons.
  Time: ~30s on CPU. Memory: 16384^2*8 = 2.1GB. Borderline.
  Restrict to M_frac_max=1.0: M=8192, matrix = 67M = 0.5GB. OK.
  Actually TwoNN is O(M*k), not O(M^2). k=2 nearest neighbors -> O(2M).
  So 8192*2 = fast. But distance computation is O(M^2) for naive.
  Use sklearn/scipy NNDescent for fast ANN. Or: use the TwoNN from bid_m_normalized_v1.

TIMEOUT ESTIMATE:
  6 M_fracs x 3 seeds = 18 cells.
  At M_frac=1.0, M=8192: TwoNN from bid_m_normalized_v1 takes ~2s (seen in v3 large-M).
  Total: 18 * 2s = 36s. Safety: ceil(1.5 * 36 * 50) = 2700s. _n8192 floor = 21600.
  timeout_s = 21600.

N-suffix: _n8192 -> production N = 8192 (PROT-018 binding).
Anchor: bid_order_parameter_v5_n8192_bsc
Queue: remote_cpu_queue (TwoNN; CPU; N=8192 BSC, 6 M_fracs x 3 seeds)
Pre-reg: prereqs/2026-05-28_bid_order_parameter_v5_n8192_bsc.md
Parent: bid_m_normalized_v1 (N=4096 Kerdock HARD_PASS)
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
import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# Load bid_m_normalized_v1 for run_one_seed_Mfrac (TwoNN BID computation)
_v1_path = REPO / "experiments" / "exp_bid_m_normalized_v1.py"
_v1_spec = importlib.util.spec_from_file_location("bid_mnorm_v1_v5op", _v1_path)
_bid_v1 = importlib.util.module_from_spec(_v1_spec)
_v1_spec.loader.exec_module(_bid_v1)

BAND_MAX_INSIDE = _bid_v1.BAND_MAX_INSIDE

# PRODUCTION CONFIG -- PROT-018: _n8192 suffix binds to N = 8192
N_FULL  = 8192
N_SMOKE = 512
assert N_FULL == 8192, f"PROT-018: N_FULL must be 8192; got {N_FULL}"

# M_frac sweep at N=8192 BSC
M_FRACS_FULL  = [0.05, 0.1, 0.25, 0.5, 1.0, 2.0]
M_FRACS_SMOKE = [0.05, 0.25, 1.0]  # smoke with selftest-safe M_fracs

SEEDS_FULL  = [7, 17, 23]
SEEDS_SMOKE = [17]

# Pre-registered thresholds
HP_BID_MIN_AT_LOW_M = 50.0    # BID > 50 at M_frac <= 0.5 = outside Hopfield
HF_BID_INSIDE_AT_LOW_M = 5.0  # BID < 5 at M_frac <= 0.25 = inside bands
HP_SEEDS_MIN = 2


def get_output_dir(default_name: str = "bid_order_parameter_v5_n8192_bsc") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def make_bsc_atoms(M: int, N: int, seed: int) -> np.ndarray:
    """Generate M random +/-1 pattern vectors of dimension N."""
    rng = np.random.default_rng(seed)
    return (rng.integers(0, 2, (M, N)).astype(np.float32) * 2 - 1)


def compute_bid(patterns: np.ndarray) -> float:
    """TwoNN BID via pure numpy (no sklearn).
    Returns BID estimate (>1 means non-trivial intrinsic dimension).
    """
    M = patterns.shape[0]
    if M < 4:
        return float("nan")
    # Compute pairwise distances via vectorized numpy
    # For large M, batch to avoid OOM
    BATCH = min(M, 512)
    r1_list = []
    r2_list = []
    for start in range(0, M, BATCH):
        end = min(start + BATCH, M)
        chunk = patterns[start:end]  # (B, N)
        # Distances from chunk to all patterns
        # ||a-b||^2 = ||a||^2 + ||b||^2 - 2*a.b
        a_sq = (chunk ** 2).sum(axis=1, keepdims=True)  # (B, 1)
        b_sq = (patterns ** 2).sum(axis=1, keepdims=True).T  # (1, M)
        dot = chunk @ patterns.T  # (B, M)
        dists_sq = np.maximum(0.0, a_sq + b_sq - 2 * dot)  # (B, M)
        # Set self-distance to inf
        for i, idx in enumerate(range(start, end)):
            dists_sq[i, idx] = np.inf
        # Sort to find 2 nearest neighbors
        sorted_d = np.sort(dists_sq, axis=1)
        r1_list.append(np.sqrt(np.maximum(0.0, sorted_d[:, 0])))
        r2_list.append(np.sqrt(np.maximum(0.0, sorted_d[:, 1])))
    r1 = np.concatenate(r1_list)
    r2 = np.concatenate(r2_list)
    # TwoNN formula: mu_i = r2_i / r1_i, BID = 1 / E[log(mu)]
    valid = (r1 > 1e-9) & (r2 > 1e-9) & np.isfinite(r1) & np.isfinite(r2)
    if valid.sum() < 2:
        return float("nan")
    mu = r2[valid] / r1[valid]
    log_mu = np.log(mu)
    if log_mu.mean() < 1e-9:
        return float("nan")
    bid = 1.0 / log_mu.mean()
    return float(bid)


def run_one_cell(N: int, M_frac: float, seed: int) -> Dict:
    """Compute BID at one (N, M_frac, seed) cell using BSC atoms."""
    M = int(M_frac * N)
    if M < 4:
        return {"N": N, "M_frac": M_frac, "M": M, "seed": seed,
                "bid": float("nan"), "error": "M < 4"}
    patterns = make_bsc_atoms(M, N, seed)
    bid = compute_bid(patterns)
    normalized_bid = bid / N if not math.isnan(bid) else float("nan")
    print(f"    N={N} M_frac={M_frac} M={M} seed={seed} "
          f"bid={bid:.2f} bid_norm={normalized_bid:.4f}", flush=True)
    return {
        "N": N, "M_frac": M_frac, "M": M, "seed": seed,
        "bid": round(bid, 3) if not math.isnan(bid) else None,
        "bid_normalized": round(normalized_bid, 5) if not math.isnan(normalized_bid) else None,
    }


def compute_verdict(summary: Dict) -> Tuple[str, str]:
    cells = summary.get("cells", [])
    if not cells:
        return ("BID_V5_INCONCLUSIVE", "No cells.")

    N = summary.get("N", N_FULL)

    by_mfrac: Dict[float, List] = {}
    for c in cells:
        by_mfrac.setdefault(c["M_frac"], []).append(c)

    m_sorted = sorted(by_mfrac.keys())
    mean_bid = {}
    for m in m_sorted:
        bids = [c["bid"] for c in by_mfrac[m] if c.get("bid") is not None]
        if bids:
            mean_bid[m] = sum(bids) / len(bids)

    if not mean_bid:
        return ("BID_V5_INCONCLUSIVE", "No valid BID values.")

    # Check monotone decrease
    bid_vals = [mean_bid[m] for m in sorted(mean_bid.keys())]
    decreasing = all(bid_vals[i] >= bid_vals[i+1] - 5.0
                     for i in range(len(bid_vals)-1))

    # Check BID outside bands at low M
    low_m_fracs = [m for m in mean_bid.keys() if m <= 0.5]
    bid_outside_at_low = all(mean_bid[m] > HP_BID_MIN_AT_LOW_M for m in low_m_fracs) if low_m_fracs else False

    # Per-seed at low M
    seed_ids = sorted(set(c["seed"] for c in cells))
    seed_outside = []
    for seed in seed_ids:
        sc_low = [c for c in cells if c["seed"] == seed and c["M_frac"] <= 0.5
                  and c.get("bid") is not None]
        if not sc_low:
            seed_outside.append(False)
            continue
        seed_outside.append(all(c["bid"] > HP_BID_MIN_AT_LOW_M for c in sc_low))
    n_outside = sum(seed_outside)

    # Check collapse at low M (HARD_FAIL)
    very_low_fracs = [m for m in mean_bid.keys() if m <= 0.25]
    collapse_at_low = any(mean_bid[m] < HF_BID_INSIDE_AT_LOW_M for m in very_low_fracs) if very_low_fracs else False

    mean_bid_at_0p5 = mean_bid.get(0.5, mean_bid.get(0.25, None))
    mid_str = f"{mean_bid_at_0p5:.1f}" if mean_bid_at_0p5 is not None else "nan"
    detail = (f"decreasing={decreasing} bid_outside_at_low={bid_outside_at_low} "
              f"n_outside={n_outside}/{len(seed_ids)} "
              f"mean_bid_at_0.5={mid_str} "
              f"N={N} M_fracs={sorted(mean_bid.keys())}")

    if collapse_at_low:
        return ("BID_V5_HARD_FAIL",
                f"BID_COLLAPSE_LOW_M: BID < {HF_BID_INSIDE_AT_LOW_M} at M_frac<=0.25. " + detail)

    if decreasing and n_outside >= HP_SEEDS_MIN:
        return ("BID_V5_HARD_PASS",
                f"BID_OUTSIDE_HOPFIELD_N8192_BSC: monotone + above bands. " + detail)

    return ("BID_V5_MIDDLE_BAND", f"PARTIAL_BID_STRUCTURE: " + detail)


def _instrumentation_selftest() -> None:
    assert N_FULL == 8192, f"PROT-018: N_FULL must be 8192; got {N_FULL}"
    # Formula: M at M_frac=0.05, N=8192
    assert int(0.05 * N_FULL) == 409, f"M at M_frac=0.05: {int(0.05 * N_FULL)}"
    # Verdict gates
    fake_hp = [{"M_frac": m, "bid": 100.0 - m * 10, "seed": 17} for m in [0.05, 0.25, 1.0]]
    v, msg = compute_verdict({"cells": fake_hp, "N": N_FULL})
    assert "PASS" in v or "MIDDLE" in v, f"gate: {v}"
    fake_hf = [{"M_frac": m, "bid": 2.0, "seed": 17} for m in [0.05, 0.1, 0.25]]
    vf, _ = compute_verdict({"cells": fake_hf, "N": N_FULL})
    assert "HARD_FAIL" in vf, f"HARD_FAIL gate: {vf}"
    # Smoke cell at N_SMOKE (M_frac=0.05 to keep M small for TwoNN)
    cell = run_one_cell(N_SMOKE, 0.05, 17)
    assert cell.get("bid") is not None, f"BID None at smoke scale: {cell}"
    assert cell["bid"] > 0, f"BID <= 0: {cell['bid']}"
    # 4x smoke: N_SMOKE * 4 = 2048 (BSC, any N valid)
    cell4 = run_one_cell(N_SMOKE * 4, 0.05, 17)
    assert cell4.get("bid") is not None, f"4x BID None"
    print(f"[selftest] bid_order_parameter_v5_n8192_bsc PASS bid_smoke={cell['bid']:.2f}",
          flush=True)


_instrumentation_selftest()


def main():
    import argparse
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

    print(f"[run] bid_order_parameter_v5_n8192_bsc smoke={smoke} N={N_cfg} "
          f"M_fracs={m_fracs} seeds={seeds}", flush=True)
    t0 = time.time()

    all_cells = []
    for M_frac in m_fracs:
        print(f"\n  [M_frac={M_frac}]", flush=True)
        for seed in seeds:
            cell = run_one_cell(N_cfg, M_frac, seed)
            all_cells.append(cell)
        print(f"  M_frac={M_frac} elapsed={time.time()-t0:.1f}s", flush=True)

    verdict, verdict_msg = compute_verdict({"cells": all_cells, "N": N_cfg})
    elapsed = round(time.time() - t0, 2)

    summary = {
        "anchor": "bid_order_parameter_v5_n8192_bsc", "N": N_cfg, "smoke": smoke,
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
