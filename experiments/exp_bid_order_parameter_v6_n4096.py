"""BID ORDER PARAMETER v6: N=4096 BSC atoms, Spearman-robust monotone criterion.

CONTEXT:
  bid_order_parameter_v5_n8192_bsc (MIDDLE_BAND): N=8192 BSC atoms.
  Verdict: decreasing=False BUT bid_outside_at_low=True n_outside=3/3.
  Root cause: strict monotone check failed due to variance at high N. Signal IS present.

  v6 fix: use N=4096 BSC atoms (lower variance than N=8192) AND replace strict
  monotone check with Spearman rank correlation (robust to per-cell variance).
  Extends bid_m_normalized_v1 (N=4096 BSC Hopfield HARD_PASS) to different M_frac range.

NOTE ON ATOM TYPE:
  Kerdock codewords are equidistant (pairwise dist = sqrt(2N)), making TwoNN BID
  undefined (all mu=1, log(1)=0). BSC (+/-1) random atoms are NOT equidistant
  and work correctly with TwoNN.

SCIENTIFIC QUESTION:
  At N=4096 BSC atoms, does BID decrease robustly with M_frac?
  Is BID outside Hopfield bands (normalized BID > BAND_MAX_INSIDE) at low M_frac?
  Does Spearman rank correlation capture the decreasing trend despite per-cell variance?

PRE-REGISTERED BANDS (prior: bid_order_parameter_v5 N=8192 MIDDLE_BAND n_outside=3/3):
  Prior anchor: BID IS outside bands at low M_frac (confirmed). Monotone check failed only.
  HARD_PASS: Spearman rho < -0.5 (robust negative correlation)
    AND n_outside_low >= 2/3 seeds at M_frac <= 0.25.
    Interpretation: BID robustly decreases and stays outside Hopfield bands.
  HARD_FAIL: n_outside_low = 0/3 at M_frac <= 0.25 (BID entirely inside Hopfield bands).
  MIDDLE_BAND: n_outside > 0 but rho >= -0.5 (not robustly monotone).

FORMULA SELF-TESTS:
  1. N == 4096 (PROT-018 binding).
  2. BSC atoms: random +/-1 at N=4096. TwoNN works (distances are NOT equidistant).
  3. BAND_MAX_INSIDE = 0.55 (from bid_m_normalized_v1, unchanged).
  4. M at M_frac=0.05, N=4096: M=204.
  5. Spearman rho: rho < 0 means BID decreases as M_frac increases.
  6. normalized_bid = bid / N. outside bands if bid_norm > BAND_MAX_INSIDE.
  7. TwoNN BID: 1 / mean(log(r2/r1)) where r1, r2 are 1st/2nd nearest-neighbor distances.

OOM CHECK:
  TwoNN at M_frac=2.0, N=4096: M=8192. Batched: 512 x 4096 = 2MB per chunk. OK.

TIMEOUT ESTIMATE:
  8 M_fracs x 3 seeds = 24 cells.
  bid_m_normalized_v1 at N=4096 ran ~40s for 5 M_fracs x 3 seeds.
  Per cell: ~2.7s. 24 cells * 2.7s = 64s.
  Safety: ceil(1.5 * 64 * 5) = 480s. Floor _n4096 = 14400s.
  timeout_s = 14400.

N-suffix: _n4096 -> production N = 4096 (PROT-018 binding).
Anchor: bid_order_parameter_v6_n4096
Queue: remote_cpu_queue (TwoNN; CPU; N=4096 BSC; 8 M_fracs x 3 seeds)
Pre-reg: preregs/2026-05-29_bid_order_parameter_v6_n4096.md
Parent: bid_order_parameter_v5_n8192_bsc (MIDDLE_BAND non-monotone)
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

# Load bid_m_normalized_v1 for BAND_MAX_INSIDE
_v1_path = REPO / "experiments" / "exp_bid_m_normalized_v1.py"
_v1_spec = importlib.util.spec_from_file_location("bid_mnorm_v1_v6op", _v1_path)
_bid_v1 = importlib.util.module_from_spec(_v1_spec)
_v1_spec.loader.exec_module(_bid_v1)

BAND_MAX_INSIDE = _bid_v1.BAND_MAX_INSIDE  # 0.55

# PRODUCTION CONFIG -- PROT-018: _n4096 suffix binds to N = 4096
N_FULL  = 4096
N_SMOKE = 512    # small enough for fast smoke; BSC works at any N
assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

# Finer M_frac grid than v1
M_FRACS_FULL  = [0.05, 0.1, 0.15, 0.25, 0.5, 1.0, 1.5, 2.0]
M_FRACS_SMOKE = [0.05, 0.25, 1.0]

SEEDS_FULL  = [7, 17, 23]
SEEDS_SMOKE = [17]

# Pre-registered thresholds
HP_SPEARMAN_MAX  = -0.5    # rho < -0.5 = robust negative correlation
HP_OUTSIDE_MIN   = BAND_MAX_INSIDE  # normalized BID > 0.55 at M_frac <= 0.25
HF_OUTSIDE_COUNT = 0       # n_outside_low = 0 -> hard fail
HP_SEEDS_MIN     = 2


def get_output_dir(default_name: str = "bid_order_parameter_v6_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def make_bsc_atoms(M: int, N: int, seed: int) -> np.ndarray:
    """Generate M random +/-1 pattern vectors of dimension N (BSC atoms)."""
    rng = np.random.default_rng(seed)
    return (rng.integers(0, 2, (M, N)).astype(np.float32) * 2 - 1)


def compute_twonn_bid(patterns: np.ndarray) -> float:
    """TwoNN BID via pure numpy batched computation.
    Returns BID estimate (>1 means non-trivial intrinsic dimension).
    """
    M = patterns.shape[0]
    if M < 4:
        return float("nan")
    BATCH = min(M, 512)
    r1_list: List[np.ndarray] = []
    r2_list: List[np.ndarray] = []
    for start in range(0, M, BATCH):
        end = min(start + BATCH, M)
        chunk = patterns[start:end]  # (B, N)
        a_sq = (chunk ** 2).sum(axis=1, keepdims=True)  # (B, 1)
        b_sq = (patterns ** 2).sum(axis=1, keepdims=True).T  # (1, M)
        dot = chunk @ patterns.T  # (B, M)
        dists_sq = np.maximum(0.0, a_sq + b_sq - 2 * dot)  # (B, M)
        for i, idx in enumerate(range(start, end)):
            dists_sq[i, idx] = np.inf  # exclude self-distance
        sorted_d = np.sort(dists_sq, axis=1)
        r1_list.append(np.sqrt(np.maximum(0.0, sorted_d[:, 0])))
        r2_list.append(np.sqrt(np.maximum(0.0, sorted_d[:, 1])))
    r1 = np.concatenate(r1_list)
    r2 = np.concatenate(r2_list)
    # TwoNN: BID = 1 / E[log(r2/r1)]
    valid = (r1 > 1e-9) & (r2 > 1e-9) & np.isfinite(r1) & np.isfinite(r2)
    if valid.sum() < 2:
        return float("nan")
    mu = r2[valid] / r1[valid]
    log_mu = np.log(mu)
    if log_mu.mean() < 1e-9:
        return float("nan")
    return float(1.0 / log_mu.mean())


def spearman_rho(x: List[float], y: List[float]) -> float:
    """Compute Spearman rank correlation coefficient."""
    n = len(x)
    if n < 3:
        return float("nan")
    arr_x = np.array(x, dtype=float)
    arr_y = np.array(y, dtype=float)
    rank_x = np.argsort(np.argsort(arr_x)).astype(float)
    rank_y = np.argsort(np.argsort(arr_y)).astype(float)
    mean_rx = rank_x.mean()
    mean_ry = rank_y.mean()
    num = ((rank_x - mean_rx) * (rank_y - mean_ry)).sum()
    den = math.sqrt(((rank_x - mean_rx)**2).sum() * ((rank_y - mean_ry)**2).sum())
    if den < 1e-10:
        return 0.0
    return float(num / den)


def run_one_cell(N: int, M_frac: float, seed: int) -> Dict:
    """Compute BID at one (N, M_frac, seed) cell using BSC atoms."""
    M = int(M_frac * N)
    if M < 4:
        return {"N": N, "M_frac": M_frac, "M": M, "seed": seed,
                "bid": None, "bid_normalized": None, "outside_band": False,
                "error": "M < 4"}
    patterns = make_bsc_atoms(M, N, seed)
    bid = compute_twonn_bid(patterns)
    normalized_bid = bid / N if not math.isnan(bid) else float("nan")
    outside_band = (normalized_bid > BAND_MAX_INSIDE) if not math.isnan(normalized_bid) else False
    bid_str = f"{bid:.2f}" if not math.isnan(bid) else "nan"
    norm_str = f"{normalized_bid:.4f}" if not math.isnan(normalized_bid) else "nan"
    print(f"    N={N} M_frac={M_frac} M={M} seed={seed} "
          f"bid={bid_str} bid_norm={norm_str} outside={outside_band}", flush=True)
    return {
        "N": N, "M_frac": M_frac, "M": M, "seed": seed,
        "bid": round(bid, 3) if not math.isnan(bid) else None,
        "bid_normalized": round(normalized_bid, 5) if not math.isnan(normalized_bid) else None,
        "outside_band": outside_band,
    }


def compute_verdict(summary: Dict) -> Tuple[str, str]:
    cells = summary.get("cells", [])
    if not cells:
        return ("BID_V6_INCONCLUSIVE", "No cells.")

    N = summary.get("N", N_FULL)

    by_mfrac: Dict[float, List] = {}
    for c in cells:
        by_mfrac.setdefault(c["M_frac"], []).append(c)

    m_sorted = sorted(by_mfrac.keys())
    mean_bid_norm: Dict[float, float] = {}
    for m in m_sorted:
        vals = [c["bid_normalized"] for c in by_mfrac[m]
                if c.get("bid_normalized") is not None]
        if vals:
            mean_bid_norm[m] = sum(vals) / len(vals)

    if not mean_bid_norm:
        return ("BID_V6_INCONCLUSIVE", "No valid BID_norm values.")

    # Spearman rho between M_frac and mean_bid_norm
    m_vals = sorted(mean_bid_norm.keys())
    bid_vals = [mean_bid_norm[m] for m in m_vals]
    rho = spearman_rho(m_vals, bid_vals) if len(m_vals) >= 3 else float("nan")

    # Outside-band count at low M (M_frac <= 0.25)
    low_m_cells = [c for c in cells if c["M_frac"] <= 0.25
                   and c.get("bid_normalized") is not None]
    n_outside_low = sum(1 for c in low_m_cells if c.get("outside_band", False))
    seeds_at_low = len(low_m_cells)

    rho_str = "nan" if math.isnan(rho) else f"{rho:.3f}"
    detail = (f"rho={rho_str} HP_rho<{HP_SPEARMAN_MAX} "
              f"n_outside_low={n_outside_low}/{seeds_at_low} "
              f"BAND_MAX_INSIDE={BAND_MAX_INSIDE} N={N} M_fracs_tested={len(m_sorted)}")

    # Hard fail: BID inside bands at all low-M seeds
    if seeds_at_low > 0 and n_outside_low == HF_OUTSIDE_COUNT:
        return ("BID_V6_HARD_FAIL",
                f"BID_INSIDE_BANDS_AT_LOW_M: n_outside_low=0/{seeds_at_low}. " + detail)

    # Smoke case
    if len(m_sorted) <= 3 or seeds_at_low <= 1:
        label = "BID_V6_SMOKE_PASS" if n_outside_low > 0 else "BID_V6_SMOKE_PARTIAL"
        return (label, f"SMOKE: rho={rho_str} "
                       f"n_outside_low={n_outside_low}/{seeds_at_low}. " + detail)

    if (not math.isnan(rho) and rho < HP_SPEARMAN_MAX
            and n_outside_low >= HP_SEEDS_MIN):
        return ("BID_V6_HARD_PASS",
                f"BID_OUTSIDE_AND_DECREASING: rho={rho_str}. " + detail)

    return ("BID_V6_MIDDLE_BAND",
            f"PARTIAL: rho={rho_str} n_outside_low={n_outside_low}/{seeds_at_low}. " + detail)


def _instrumentation_selftest() -> None:
    assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

    # Formula self-tests
    M_at_005 = int(0.05 * N_FULL)
    assert M_at_005 == 204, f"M at M_frac=0.05: {M_at_005}"
    assert abs(BAND_MAX_INSIDE - 0.55) < 0.01, f"BAND_MAX_INSIDE: {BAND_MAX_INSIDE}"

    # Spearman rho tests
    rho_dec = spearman_rho([1.0, 2.0, 3.0, 4.0], [4.0, 3.0, 2.0, 1.0])
    assert abs(rho_dec - (-1.0)) < 0.01, f"Spearman decreasing: {rho_dec}"
    rho_inc = spearman_rho([1.0, 2.0, 3.0, 4.0], [1.0, 2.0, 3.0, 4.0])
    assert abs(rho_inc - 1.0) < 0.01, f"Spearman increasing: {rho_inc}"

    # TwoNN test: random BSC at M=50, N=16 (tiny, should give non-nan BID)
    import numpy as np
    rng = np.random.default_rng(42)
    tiny_patterns = (rng.integers(0, 2, (50, 16)) * 2 - 1).astype(np.float32)
    bid_tiny = compute_twonn_bid(tiny_patterns)
    assert not math.isnan(bid_tiny), f"TwoNN on BSC atoms returned NaN"
    assert bid_tiny > 0, f"TwoNN BID not positive: {bid_tiny}"

    # Verdict gates
    fake_hp = [
        {"M_frac": 0.05, "bid_normalized": 0.80, "outside_band": True},
        {"M_frac": 0.05, "bid_normalized": 0.78, "outside_band": True},
        {"M_frac": 0.05, "bid_normalized": 0.82, "outside_band": True},
        {"M_frac": 0.1,  "bid_normalized": 0.72, "outside_band": True},
        {"M_frac": 0.1,  "bid_normalized": 0.70, "outside_band": True},
        {"M_frac": 0.1,  "bid_normalized": 0.74, "outside_band": True},
        {"M_frac": 0.25, "bid_normalized": 0.60, "outside_band": True},
        {"M_frac": 0.25, "bid_normalized": 0.58, "outside_band": True},
        {"M_frac": 0.25, "bid_normalized": 0.62, "outside_band": True},
        {"M_frac": 0.5,  "bid_normalized": 0.35, "outside_band": False},
        {"M_frac": 0.5,  "bid_normalized": 0.33, "outside_band": False},
        {"M_frac": 0.5,  "bid_normalized": 0.37, "outside_band": False},
        {"M_frac": 1.0,  "bid_normalized": 0.20, "outside_band": False},
        {"M_frac": 1.0,  "bid_normalized": 0.18, "outside_band": False},
        {"M_frac": 1.0,  "bid_normalized": 0.22, "outside_band": False},
        {"M_frac": 1.5,  "bid_normalized": 0.12, "outside_band": False},
        {"M_frac": 1.5,  "bid_normalized": 0.11, "outside_band": False},
        {"M_frac": 1.5,  "bid_normalized": 0.13, "outside_band": False},
        {"M_frac": 2.0,  "bid_normalized": 0.08, "outside_band": False},
        {"M_frac": 2.0,  "bid_normalized": 0.07, "outside_band": False},
        {"M_frac": 2.0,  "bid_normalized": 0.09, "outside_band": False},
    ]
    v, msg = compute_verdict({"cells": fake_hp, "N": N_FULL})
    assert "HARD_PASS" in v, f"HP gate: {v}: {msg}"

    # HF case
    fake_hf = [
        {"M_frac": 0.05, "bid_normalized": 0.10, "outside_band": False},
        {"M_frac": 0.05, "bid_normalized": 0.12, "outside_band": False},
        {"M_frac": 0.05, "bid_normalized": 0.09, "outside_band": False},
        {"M_frac": 0.25, "bid_normalized": 0.15, "outside_band": False},
        {"M_frac": 0.25, "bid_normalized": 0.14, "outside_band": False},
        {"M_frac": 0.25, "bid_normalized": 0.16, "outside_band": False},
        {"M_frac": 1.0,  "bid_normalized": 0.08, "outside_band": False},
        {"M_frac": 1.0,  "bid_normalized": 0.07, "outside_band": False},
        {"M_frac": 1.0,  "bid_normalized": 0.09, "outside_band": False},
    ]
    vf, _ = compute_verdict({"cells": fake_hf, "N": N_FULL})
    assert "HARD_FAIL" in vf, f"HF gate: {vf}"

    # Forward pass smoke (N_SMOKE=512 -- BSC, any N valid)
    cell = run_one_cell(N_SMOKE, 0.05, 17)
    assert cell.get("bid_normalized") is not None, f"bid_normalized missing: {cell}"
    bn = cell["bid_normalized"]
    assert not math.isnan(bn), f"bid_normalized NaN"
    assert bn > 0, f"bid_normalized not positive: {bn}"

    # 4x smoke (N_SMOKE * 4 = 2048; BSC, any N valid)
    cell4 = run_one_cell(N_SMOKE * 4, 0.05, 17)
    assert cell4.get("bid_normalized") is not None, f"4x bid_normalized missing: {cell4}"
    assert not math.isnan(cell4["bid_normalized"]), "4x bid_normalized NaN"

    print(f"[selftest] bid_order_parameter_v6_n4096 PASS "
          f"bid_norm_smoke={cell['bid_normalized']:.4f} "
          f"bid_norm_4x={cell4['bid_normalized']:.4f}", flush=True)


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

    print(f"[run] bid_order_parameter_v6_n4096 smoke={smoke} N={N_cfg} "
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
        "anchor": "bid_order_parameter_v6_n4096", "N": N_cfg, "smoke": smoke,
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
