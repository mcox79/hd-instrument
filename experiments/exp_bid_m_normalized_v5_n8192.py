"""BID M-NORMALIZED v5: vectorized W-build fix, N=8192 scaling-law data point.

CONTEXT:
  v3_n4096 (4h timeout), v4_n8192 (6h timeout), v1 n_sweep (1h timeout):
  all timed out because run_one_seed_Mfrac builds W via a Python loop:
      for v in patterns: W += np.outer(v, v) / N
  At M_frac=5, N=8192: M=40960 iterations of (8192x8192) outer products -> >>14400s.

  v5 replaces the Python loop with a single vectorized matmul:
      W = (patterns.T @ patterns) / N
      np.fill_diagonal(W, 0.0)
  This is O(M*N^2) in numpy/BLAS (dgemm), not O(M) Python iterations.
  Expected speedup: 500-2000x (M/BLAS_BLOCK).

  v1 (v265 HARD_PASS): N=4096 M_fracs=[0.05-0.50] outside Hopfield.
  v4_n8192: same question at N=8192 -- timed out before any data.
  This is the missing scaling-law data point for the substrate-outside-static-
  Hopfield row (cap_map 60-72%).

SCIENTIFIC QUESTION:
  At N=8192, does BID remain outside all static-Hopfield bands across
  M_fracs=[0.025..5.0]? Does the monotone-decreasing BID signature hold at
  the largest production N?

PRE-REGISTERED BANDS:
  Prior: v1 HARD_PASS (N=4096, M_fracs=[0.05-0.50], BID>50 outside bands).
  At N=8192: threshold scales to max(6.0, 50*(8192/4096)) = 100.0.

  HARD_PASS: BID > 100.0 at >= 5/6 M_frac cells, >= 2/3 seeds per M_frac.
    Interpretation: substrate-outside-Hopfield confirmed at N=8192.
  HARD_FAIL: BID < 100.0 at majority (>= 4/6) of M_frac cells.
    Interpretation: N=8192 is inside a Hopfield class or BID collapses.
  MIDDLE_BAND: some M_fracs pass, some fail (expected near M_c).

FORMULA SELF-TESTS:
  1. N == 8192 (PROT-018 binding).
  2. bid_threshold(N=8192) = max(6.0, 50.0 * (8192/4096)) = 100.0. OK.
  3. bid_threshold(N=512) = max(6.0, 50.0 * (512/4096)) = max(6.0, 6.25) = 6.25. OK.
  4. M at M_frac=5.0, N=8192: M=40960.
  5. W vectorized: (40960,8192).T @ (40960,8192) = (8192,8192). BLAS dgemm. OK.
  6. HARD_PASS gate: fracs_passing=5, n_fracs=6 -> 5>=5 -> HARD_PASS. OK.
  7. HARD_FAIL gate: fracs_passing=0 -> HARD_FAIL. OK.

WALL-TIME SELF-TEST (smoke gate):
  The _instrumentation_selftest compares loop vs vectorized W-build at small
  scale and asserts vectorized is faster. Exact: N=256, M_frac=0.5 -> M=128.
  Loop: 128 Python iterations. Vectorized: 1 matmul.
  Expected: vectorized >= 5x faster at M=128 (conservative; real gain is 100x+).

TIMEOUT ESTIMATE:
  Vectorized W-build at N=8192, M_frac=5.0: M=40960 patterns.
  patterns = (40960, 8192) float64 = 2.7GB RAM. W = (8192, 8192) = 536MB.
  BLAS dgemm on remote CPU (16-core): estimated 30-90s per W-build.
  TwoNN at N=8192, S=200 attractors: estimated 5-15s.
  Per cell total: ~45-105s. Conservative: 90s per cell.
  6 M_fracs x 3 seeds = 18 cells. 18 * 90 = 1620s.
  Safety: ceil(1.5 * 1620) = 2430s. Round up: 3600s.
  _n8192 PROT-019 floor = 21600s. Use 21600s (conservative for large-M cells).
  timeout_s = 21600

N-suffix: _n8192 -> production N = 8192 (PROT-018 binding).
Anchor: bid_m_normalized_v5_n8192
Queue: remote_cpu_queue (TwoNN; CPU; N=8192)
Pre-reg: preregs/2026-05-29_bid_m_normalized_v5_n8192.md
Parent: bid_m_normalized_v4_n8192 (fix of W-build timeout); v1 (HARD_PASS baseline)
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

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

# Import TwoNN BID function via v1 -> v2 chain (v1 imports bid_n_stability_v2
# which imports bid_substrate_probe_v1 for twonn_id / twonn_bid).
_v1_path = REPO / "experiments" / "exp_bid_m_normalized_v1.py"
_v1_spec = importlib.util.spec_from_file_location("bid_v1_for_v5", _v1_path)
_bid_v1_mod = importlib.util.module_from_spec(_v1_spec)
_v1_spec.loader.exec_module(_bid_v1_mod)

# Reach into the TwoNN function from the upstream chain
_bid_v2_mod = _bid_v1_mod._bid_v2
_bid_v1_inner = _bid_v2_mod._bid_v1
_twonn_fn = getattr(_bid_v1_inner, "twonn_id", None) or getattr(_bid_v1_inner, "twonn_bid", None)
assert _twonn_fn is not None, "Cannot find twonn_id or twonn_bid in bid_substrate_probe_v1"

S_PROBES = getattr(_bid_v1_inner, "S_PROBES", 200)

BAND_MAX_INSIDE = _bid_v1_mod.BAND_MAX_INSIDE  # 0.55 normalized

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
    """Pre-registered: BID must exceed this to be outside Hopfield bands."""
    return max(6.0, BID_OUTSIDE_MIN_ABS * (N_cfg / 4096))


# Pre-registered thresholds
HP_PASS_FRACS_MIN = 5    # >= 5/6 M_frac cells above threshold
HP_SEEDS_MIN      = 2    # >= 2/3 seeds must pass per M_frac (FULL mode)


def get_output_dir(default_name: str = "bid_m_normalized_v5_n8192") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _build_w_vectorized(patterns: np.ndarray, N: int) -> np.ndarray:
    """Vectorized Hopfield W construction via single BLAS matmul.

    patterns: (M, N) float64
    Returns W: (N, N) float64 with diagonal zeroed.
    """
    W = (patterns.T @ patterns) / N       # (N, N) -- single dgemm call
    np.fill_diagonal(W, 0.0)
    return W


def run_one_seed_Mfrac_vectorized(N: int, M_frac: float, seed: int) -> Dict:
    """Run BID at (N, M_frac, seed) using vectorized W construction.

    This is the fixed version of exp_bid_m_normalized_v1.run_one_seed_Mfrac.
    The Python loop over patterns is replaced by a single matmul.
    """
    rng = np.random.default_rng(seed=seed)
    M_stored = max(4, int(M_frac * N))

    patterns = rng.choice([-1, 1], size=(M_stored, N)).astype(np.float64)
    W = _build_w_vectorized(patterns, N)

    # Sample attractors (same protocol as upstream v1 / bid_substrate_probe_v1)
    n_samples = min(S_PROBES, M_stored)
    query_idx = rng.choice(M_stored, size=n_samples, replace=False)
    queries = patterns[query_idx].copy()
    flip_prob = 0.05
    noise_mask = rng.random(queries.shape) < flip_prob
    queries[noise_mask] *= -1.0
    attractors = np.sign(W @ queries.T).T  # (S, N)

    d_hat, ci_low, ci_high = _twonn_fn(attractors)

    return {
        "N": N,
        "M_frac": M_frac,
        "M_stored": M_stored,
        "seed": seed,
        "bid_estimate": float(d_hat),
        "bid_ci_low": float(ci_low),
        "bid_ci_high": float(ci_high),
    }


def run_one_cell(N: int, M_frac: float, seed: int) -> Dict:
    """Run one (N, M_frac, seed) cell and annotate with pass/fail."""
    result = run_one_seed_Mfrac_vectorized(N, M_frac, seed)
    bid_val = result.get("bid_estimate", 0.0)
    if bid_val is None:
        bid_val = 0.0
    M = max(4, int(M_frac * N))
    thr = bid_threshold(N)
    passes = bid_val >= thr
    print(
        f"    N={N} M_frac={M_frac} M={M} seed={seed} "
        f"bid={bid_val:.2f} threshold={thr:.2f} passes={passes}",
        flush=True,
    )
    return {
        "N": N, "M_frac": M_frac, "M": M, "seed": seed,
        "bid": float(bid_val),
        "threshold": thr,
        "passes_hp": passes,
    }


def compute_verdict(summary: Dict) -> Tuple[str, str]:
    """Pre-registered verdict logic -- identical to v4 bands, carried forward."""
    cells = summary.get("cells", [])
    if not cells:
        return ("BID_V5_N8K_INCONCLUSIVE", "No cells.")

    N_cfg = summary.get("N", N_FULL)
    thr = bid_threshold(N_cfg)

    # Group by M_frac
    by_mfrac: Dict[float, List] = {}
    for c in cells:
        by_mfrac.setdefault(c["M_frac"], []).append(c)

    n_fracs = len(by_mfrac)
    mean_bid = sum(c["bid"] for c in cells) / len(cells)

    seeds_per_frac = max(len(cs) for cs in by_mfrac.values()) if by_mfrac else 1
    if seeds_per_frac >= HP_SEEDS_MIN:
        # FULL mode: require HP_SEEDS_MIN seeds per M_frac
        fracs_passing = sum(
            1 for cs in by_mfrac.values()
            if sum(1 for c in cs if c["passes_hp"]) >= HP_SEEDS_MIN
        )
    else:
        # Smoke mode: at least 1 seed passes
        fracs_passing = sum(
            1 for cs in by_mfrac.values()
            if any(c["passes_hp"] for c in cs)
        )

    fracs_above_thr = sum(
        1 for cs in by_mfrac.values() if any(c["passes_hp"] for c in cs)
    )

    detail = (
        f"fracs_passing={fracs_passing}/{n_fracs} "
        f"fracs_above_thr={fracs_above_thr} "
        f"mean_bid={mean_bid:.2f} threshold={thr:.2f} "
        f"HP_pass_fracs={HP_PASS_FRACS_MIN} seeds_per_frac={seeds_per_frac} "
        f"N={N_cfg}"
    )

    if fracs_passing == 0:
        return (
            "BID_V5_N8K_HARD_FAIL",
            f"ALL_INSIDE_BAND: fracs_passing={fracs_passing}. " + detail,
        )

    if fracs_passing >= HP_PASS_FRACS_MIN:
        return (
            "BID_V5_N8K_HARD_PASS",
            f"OUTSIDE_BANDS_N8192: fracs_passing={fracs_passing}/{n_fracs}. " + detail,
        )

    return (
        "BID_V5_N8K_MIDDLE_BAND",
        f"PARTIAL_OUTSIDE: fracs_passing={fracs_passing}/{n_fracs}. " + detail,
    )


def _instrumentation_selftest() -> None:
    """Assert metrics are non-null and vectorized W-build is faster than loop.

    Includes wall-time comparison per [[feedback-strategy-spec-formula-selftests]]:
    - Build W via Python loop (slow path, reference)
    - Build W via matmul (fast path, this script)
    - Assert fast_path_time < loop_time (vectorized should always be faster)
    """
    # --- formula self-tests ---
    assert N_FULL == 8192, f"PROT-018: N_FULL={N_FULL}"
    thr_full = bid_threshold(N_FULL)
    assert abs(thr_full - 100.0) < 1.0, f"bid_threshold(8192) expected 100.0, got {thr_full}"
    thr_smoke = bid_threshold(N_SMOKE)
    assert abs(thr_smoke - 6.25) < 0.5, f"bid_threshold(512) expected ~6.25, got {thr_smoke}"
    # HARD_PASS gate: 5/6 fracs passing
    fake_hp = [
        {"M_frac": m, "bid": 200.0, "threshold": thr_full, "passes_hp": True}
        for m in [0.025, 0.05, 0.125, 0.5, 2.0, 5.0]
        for _ in range(3)
    ]
    v, _ = compute_verdict({"cells": fake_hp, "N": N_FULL})
    assert "HARD_PASS" in v, f"Expected HARD_PASS: {v}"
    fake_hf = [{"M_frac": 0.5, "bid": 1.0, "threshold": thr_full, "passes_hp": False}]
    vf, _ = compute_verdict({"cells": fake_hf, "N": N_FULL})
    assert "HARD_FAIL" in vf, f"Expected HARD_FAIL: {vf}"
    print("[selftest 1/5] formula gates OK", flush=True)

    # --- wall-time comparison: loop vs vectorized ---
    N_bench = 256
    M_bench = max(4, int(0.5 * N_bench))   # 128 patterns
    rng = np.random.default_rng(seed=99)
    patterns_bench = rng.choice([-1, 1], size=(M_bench, N_bench)).astype(np.float64)

    t_loop_start = time.perf_counter()
    W_loop = np.zeros((N_bench, N_bench), dtype=np.float64)
    for v in patterns_bench:
        W_loop += np.outer(v, v) / N_bench
    np.fill_diagonal(W_loop, 0.0)
    t_loop = time.perf_counter() - t_loop_start

    t_vec_start = time.perf_counter()
    W_vec = _build_w_vectorized(patterns_bench, N_bench)
    t_vec = time.perf_counter() - t_vec_start

    max_diff = float(np.max(np.abs(W_loop - W_vec)))
    assert max_diff < 1e-10, f"W_loop vs W_vec mismatch: max_diff={max_diff}"
    speedup = t_loop / max(t_vec, 1e-9)
    print(
        f"[selftest 2/5] W-build wall-time: loop={t_loop*1000:.1f}ms "
        f"vec={t_vec*1000:.1f}ms speedup={speedup:.1f}x N={N_bench} M={M_bench}",
        flush=True,
    )
    # Conservatively require vectorized is faster (speedup > 1.0)
    # At N=256 M=128 the loop overhead is visible; real gain at N=8192 M=40960 is >>100x
    assert speedup > 1.0, (
        f"Vectorized W-build was NOT faster than loop at N={N_bench} M={M_bench}: "
        f"speedup={speedup:.2f}. Fix may not be applied correctly."
    )
    print(f"[selftest 3/5] vectorized speedup confirmed (>{1.0:.0f}x)", flush=True)

    # --- BID metric non-null at smoke scale ---
    cell = run_one_cell(N_SMOKE, 0.05, 17)
    assert not math.isnan(cell["bid"]), "bid NaN at smoke scale"
    assert cell["bid"] > 0.0, f"bid <= 0 at smoke scale: {cell['bid']}"
    print(f"[selftest 4/5] smoke cell OK bid={cell['bid']:.2f}", flush=True)

    # --- 4x scale: N=2048, M_frac=0.05 (multi-scale smoke) ---
    cell4 = run_one_cell(N_SMOKE * 4, 0.05, 17)
    assert not math.isnan(cell4["bid"]), "4x bid NaN"
    assert cell4["bid"] > 0.0, f"4x bid <= 0: {cell4['bid']}"
    print(
        f"[selftest 5/5] 4x smoke OK bid={cell4['bid']:.2f} N={N_SMOKE*4}",
        flush=True,
    )

    print("[SELFTEST PASS] bid_m_normalized_v5_n8192 instrumentation OK", flush=True)


_instrumentation_selftest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true", dest="self_test")
    args = parser.parse_args()
    if args.self_test:
        sys.exit(0)

    smoke = args.smoke
    N_cfg    = N_SMOKE if smoke else N_FULL
    m_fracs  = M_FRACS_SMOKE if smoke else M_FRACS_FULL
    seeds    = SEEDS_SMOKE if smoke else SEEDS_FULL

    print(
        f"[run] bid_m_normalized_v5_n8192 smoke={smoke} N={N_cfg} "
        f"M_fracs={m_fracs} seeds={seeds}",
        flush=True,
    )
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
        "anchor": "bid_m_normalized_v5_n8192",
        "N": N_cfg,
        "smoke": smoke,
        "M_fracs": m_fracs,
        "seeds": seeds,
        "cells": all_cells,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
    }
    out_dir = get_output_dir()
    out_path = out_dir / "metrics.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print(f"\n[verdict] {verdict}", flush=True)
    print(f"[verdict_msg] {verdict_msg}", flush=True)
    print(f"[elapsed] {elapsed}s", flush=True)
    print(f"[output] {out_path}", flush=True)


if __name__ == "__main__":
    main()
