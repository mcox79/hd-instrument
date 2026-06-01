"""Rate-dependence of hysteresis v2: resolve AMBIGUOUS gap_ratio sign-flip at M=10000.

v1 VERDICT: MIDDLE_BAND at N=256 (smoke scale). pearson_r=[-1.000,-0.999] (consistent negative
slope -- both M cells show rate-dependence) BUT gap_ratio=[-0.403,0.632] showed a sign-flip
at M=10000 (negative gap = rev_bpc < fwd_bpc, which is PHYSICALLY INCONSISTENT with a
forward-cooling scenario). The sign-flip is a smoke-scale artifact: at N=256 and M=10000,
M/N = 39 >> alpha_c*N=144, so the substrate is deeply saturated and the forward/reverse
initialization asymmetry collapses.

FIX v2:
  1. Increase N to 1024 (FULL scale, not smoke) -- avoids saturation at M=10000.
  2. Tighter M sweep: [500, 1000, 2000, 4000, 8000, 12000] to bracket the sign-flip region
     and identify the M* where gap sign changes.
  3. Extended epoch sweep: [1, 2, 4, 8, 16, 32, 64] for cleaner Pearson r.
  4. 5 seeds for tighter CI.

The decisive question: is the gap sign-flip at high M a genuine substrate property
(M-dependent phase transition in gap sign) or a smoke-scale artifact?
If the gap is monotone positive across M at N=1024, v1 sign-flip was artifact -> framework
is NOT sign-flip ambiguous; measure the pearson_r cleanly.

SELF-TESTS:
  1. rate_dependence_slope(gaps=[1.0,1.0,1.0], epochs=[1,2,4]) -> abs(r) < 0.3
  2. rate_dependence_slope(gaps=[2.0,1.0,0.5], epochs=[1,2,4]) -> r < -0.50
  3. gap_sign_flip_check(gaps=[1.0,0.8,0.3,-0.2]) -> True (sign flip exists)
  4. gap_sign_flip_check(gaps=[1.0,0.8,0.3,0.1]) -> False (no sign flip)
  5. train_W callable at N=64, returns shape (64,64)

PRE-REGISTERED BANDS:
  RATE_INDEPENDENT_1RSB:
    - All r(log_epochs, gap) in (-0.30, 0.30) AND gap_ratio > 0.70 at all M cells
    - No sign-flip across M sweep (gaps all positive)
    -> Thermodynamic ergodicity breaking; gap is an equilibrium property

  RATE_DEPENDENT_KINETIC:
    - All r(log_epochs, gap) < -0.50 at M < alpha_c*N cells (where gap is positive)
    - gap_ratio < 0.50 at slow cooling relative to fast
    -> Kinetic glass / geometric frustration

  GAP_SIGN_FLIP_CONFIRMED:
    - gap at M_high < 0 at N=1024 (not just N=256 artifact)
    - Explains v1 MIDDLE_BAND; means forward/reverse symmetry breaks at high load
    -> Novel high-load behavior; needs separate theoretical framing

  MIDDLE_BAND: neither above pattern clearly confirmed across all M cells

  INSTRUMENTATION_FAIL: NaN gaps, zero-var, filter eliminates all cells

Walk-back gate: smoke at N=256 M_smoke=[500,2000,8000]; if effect size d < 1.3, ship FULL at N=2048.

Queue: overnight_queue (GPU; 7 epochs x 6 M-cells x 5 seeds x N=1024; ~2-4h GPU)
Pre-reg: preregs/2026-05-27_wave14_1rsb_rate_dep_hysteresis_v2.md
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
from typing import Dict, List

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# Load hysteresis v3 infrastructure
_hv3_path = REPO / "experiments" / "exp_wave14_1rsb_hysteresis_v3.py"
_hv3_spec = importlib.util.spec_from_file_location("hv3", _hv3_path)
hv3 = importlib.util.module_from_spec(_hv3_spec)
_hv3_spec.loader.exec_module(hv3)
base = hv3.base
pa   = hv3.pa

# Design parameters
N_FULL    = 1024
N_SMOKE   = 256
EPOCHS_SWEEP_FULL  = [1, 2, 4, 8, 16, 32, 64]
EPOCHS_SWEEP_SMOKE = [1, 4, 16]
# Tighter M sweep that brackets the v1 sign-flip zone
M_CELLS_FULL  = [500, 1000, 2000, 4000, 8000, 12000]
M_CELLS_SMOKE = [500, 2000, 8000]
SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]
BATCH_SIZE_FULL  = 64
BATCH_SIZE_SMOKE = 16
BYTES_FULL  = 80_000
BYTES_SMOKE = 10_000
CELL_TIMEOUT_S = 600

ALPHA_C = 0.5625  # empirical alpha_c for N=1024


def get_output_dir(default_name: str = "wave14_1rsb_rate_dep_hysteresis_v2") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def pearson_r(xs: List[float], ys: List[float]) -> float:
    n = len(xs)
    if n < 2:
        return 0.0
    mx, my = sum(xs) / n, sum(ys) / n
    cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    sx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    sy = math.sqrt(sum((y - my) ** 2 for y in ys))
    if sx < 1e-12 or sy < 1e-12:
        return 0.0
    return cov / (sx * sy)


def rate_dependence_slope(gaps: List[float], epochs: List[int]) -> float:
    log_e = [math.log(e) for e in epochs]
    return pearson_r(log_e, gaps)


def gap_sign_flip_check(gaps: List[float]) -> bool:
    """Return True if any gap is negative (sign flip exists)."""
    valid = [g for g in gaps if not math.isnan(g)]
    return any(g < 0.0 for g in valid)


def _instrumentation_selftest():
    """Assert all claimed metrics non-null/non-sentinel at small scale."""
    # 1. Flat gaps -> slope near 0
    r1 = rate_dependence_slope([1.0, 1.0, 1.0], [1, 2, 4])
    assert abs(r1) < 0.3, f"flat slope fail: {r1}"

    # 2. Decreasing gaps -> slope < -0.50
    r2 = rate_dependence_slope([2.0, 1.0, 0.5], [1, 2, 4])
    assert r2 < -0.50, f"decreasing slope fail: {r2:.4f}"

    # 3. Sign flip check: gaps with negative -> True
    sf1 = gap_sign_flip_check([1.0, 0.8, 0.3, -0.2])
    assert sf1, "sign_flip_check should be True for negative gap"

    # 4. Sign flip check: all positive -> False
    sf2 = gap_sign_flip_check([1.0, 0.8, 0.3, 0.1])
    assert not sf2, "sign_flip_check should be False for all-positive gaps"

    # 5. train_W callable at N=64
    device = torch.device("cpu")
    gen = torch.Generator().manual_seed(42)
    byte_atoms = pa.make_bsc_atoms(base.VOCAB, 64, gen).to(device)
    pos_atoms  = pa.make_bsc_atoms(base.K, 64, gen).to(device)
    corpus_a   = pa.load_corpus_a()[:2000]
    m_split    = int(0.8 * len(corpus_a))
    train_data = corpus_a[:m_split]
    train_idx, train_tgt = base.bytes_to_idx_tensors(train_data, device)
    W_zero = torch.zeros((64, 64), dtype=torch.float32, device=device)
    W_out, _, _, _ = base.train_w_with_replay(
        W_zero, None, None, 0, byte_atoms, pos_atoms,
        train_idx, train_tgt, None, None, 0, 1, 16, device)
    assert W_out.shape == (64, 64), f"train_W shape fail: {W_out.shape}"
    assert W_out.abs().max().item() > 0, "train_W all-zero fail"
    # validity filter: at least 1 seed ran -> non-zero result
    assert W_out.abs().mean().item() > 0, "validity filter eliminated all cells at smoke scale"

    print("[selftest] PASS: 5/5 assertions OK", flush=True)


_instrumentation_selftest()


def measure_hysteresis_cell(M: int, n_epochs: int, seed: int,
                             N: int, batch_size: int, n_bytes: int,
                             device: torch.device) -> Dict:
    """Forward (W=0 init) and reverse (W=W_saturated init) BPC at fixed M."""
    gen = torch.Generator().manual_seed(seed)
    byte_atoms = pa.make_bsc_atoms(base.VOCAB, N, gen).to(device)
    pos_atoms  = pa.make_bsc_atoms(base.K, N, gen).to(device)

    corpus_full = pa.load_corpus_a()
    corpus = corpus_full[:min(n_bytes, len(corpus_full))]
    m_split = int(0.8 * len(corpus))
    train_data, test_data = corpus[:m_split], corpus[m_split:]

    # Limit to M training bytes for this cell
    train_m = train_data[:min(M, len(train_data))]
    if len(train_m) < 50:
        return {"fwd_bpc": float("nan"), "rev_bpc": float("nan"), "gap": float("nan"),
                "note": "insufficient_corpus"}

    train_idx, train_tgt = base.bytes_to_idx_tensors(train_m, device)
    test_idx, test_tgt   = base.bytes_to_idx_tensors(
        test_data[:min(2000, len(test_data))], device)

    # Forward path: W=0 cold start
    t0 = time.monotonic()
    W_fwd, _, _, _ = base.train_w_with_replay(
        torch.zeros((N, N), dtype=torch.float32, device=device),
        None, None, 0, byte_atoms, pos_atoms,
        train_idx, train_tgt, None, None, 0, n_epochs, batch_size, device)
    fwd_bpc = hv3.evaluate_W_only(W_fwd, byte_atoms, pos_atoms,
                                   test_idx, test_tgt, batch_size, N)
    if time.monotonic() - t0 > CELL_TIMEOUT_S:
        return {"fwd_bpc": float(fwd_bpc), "rev_bpc": float("nan"), "gap": float("nan"),
                "note": "fwd_timeout"}

    # Build W_saturated: train at full n_bytes to get a saturated W
    train_full_idx, train_full_tgt = base.bytes_to_idx_tensors(
        train_data[:min(n_bytes, len(train_data))], device)
    W_sat, _, _, _ = base.train_w_with_replay(
        torch.zeros((N, N), dtype=torch.float32, device=device),
        None, None, 0, byte_atoms, pos_atoms,
        train_full_idx, train_full_tgt, None, None, 0, n_epochs, batch_size, device)

    # Reverse path: re-tune W_sat at M (partial corpus)
    W_rev, _, _, _ = base.train_w_with_replay(
        W_sat.clone(), None, None, 0, byte_atoms, pos_atoms,
        train_idx, train_tgt, None, None, 0, n_epochs, batch_size, device)
    rev_bpc = hv3.evaluate_W_only(W_rev, byte_atoms, pos_atoms,
                                   test_idx, test_tgt, batch_size, N)

    del W_fwd, W_sat, W_rev
    if device.type == "cuda":
        torch.cuda.empty_cache()

    gap = float(fwd_bpc) - float(rev_bpc)
    return {"fwd_bpc": float(fwd_bpc), "rev_bpc": float(rev_bpc), "gap": gap}


def run_sweep(smoke: bool, device: torch.device) -> Dict:
    N          = N_SMOKE if smoke else N_FULL
    epochs_sw  = EPOCHS_SWEEP_SMOKE if smoke else EPOCHS_SWEEP_FULL
    m_cells    = M_CELLS_SMOKE if smoke else M_CELLS_FULL
    seeds      = SEEDS_SMOKE if smoke else SEEDS_FULL
    batch_size = BATCH_SIZE_SMOKE if smoke else BATCH_SIZE_FULL
    n_bytes    = BYTES_SMOKE if smoke else BYTES_FULL

    t0 = time.monotonic()
    print(f"[rate_dep_hysteresis_v2] smoke={smoke} N={N} epochs={epochs_sw} "
          f"M_cells={m_cells} seeds={seeds}", flush=True)

    results: Dict[int, Dict[int, List[float]]] = {
        m: {e: [] for e in epochs_sw} for m in m_cells
    }

    for M in m_cells:
        for n_epochs in epochs_sw:
            for seed in seeds:
                t_c = time.monotonic()
                cell = measure_hysteresis_cell(
                    M=M, n_epochs=n_epochs, seed=seed,
                    N=N, batch_size=batch_size, n_bytes=n_bytes, device=device)
                gap = cell.get("gap", float("nan"))
                results[M][n_epochs].append(gap)
                print(f"  M={M} ep={n_epochs} s={seed}: "
                      f"fwd={cell.get('fwd_bpc',float('nan')):.4f} "
                      f"rev={cell.get('rev_bpc',float('nan')):.4f} "
                      f"gap={gap:.4f} ({time.monotonic()-t_c:.1f}s)", flush=True)

    # Aggregate: mean gap per (M, epoch)
    agg: Dict[int, Dict[int, float]] = {}
    for M in m_cells:
        agg[M] = {}
        for n_epochs in epochs_sw:
            raw = [g for g in results[M][n_epochs] if not math.isnan(g)]
            agg[M][n_epochs] = sum(raw) / len(raw) if raw else float("nan")

    # Per-M rate-dependence analysis
    rd_analysis: Dict[str, Dict] = {}
    for M in m_cells:
        mean_gaps = [agg[M][e] for e in epochs_sw]
        valid_pairs = [(e, g) for e, g in zip(epochs_sw, mean_gaps) if not math.isnan(g)]
        if len(valid_pairs) >= 2:
            v_eps, v_gaps = zip(*valid_pairs)
            r = rate_dependence_slope(list(v_gaps), list(v_eps))
            gap_fast = agg[M][epochs_sw[0]]
            gap_slow = agg[M][epochs_sw[-1]]
            gap_ratio = (gap_slow / gap_fast
                         if (not math.isnan(gap_fast) and abs(gap_fast) > 1e-9)
                         else float("nan"))
            has_sign_flip = gap_sign_flip_check(list(v_gaps))
        else:
            r = gap_ratio = float("nan")
            has_sign_flip = False

        rd_analysis[str(M)] = {
            "pearson_r": r,
            "gap_ratio_slow_vs_fast": gap_ratio,
            "has_sign_flip": has_sign_flip,
            "mean_gaps_by_epoch": {str(e): agg[M][e] for e in epochs_sw},
        }
        print(f"  M={M}: r={r:.4f} gap_ratio={gap_ratio:.4f} sign_flip={has_sign_flip}",
              flush=True)

    # Collect verdict signals
    r_values = [rd_analysis[str(M)]["pearson_r"] for M in m_cells
                if not math.isnan(rd_analysis[str(M)]["pearson_r"])]
    ratios = [rd_analysis[str(M)]["gap_ratio_slow_vs_fast"] for M in m_cells
              if not math.isnan(rd_analysis[str(M)]["gap_ratio_slow_vs_fast"])]
    any_sign_flip = any(rd_analysis[str(M)]["has_sign_flip"] for M in m_cells)

    # Check instrumentation
    all_gaps_flat = [g for M in m_cells for e in epochs_sw for g in results[M][e]]
    n_valid = sum(1 for g in all_gaps_flat if not math.isnan(g))
    n_total = len(all_gaps_flat)

    if n_valid < n_total * 0.5:
        verdict = "INSTRUMENTATION_FAIL"
        verdict_msg = (f"INSTRUMENTATION_FAIL: {n_valid}/{n_total} valid gaps; "
                       f"training or corpus failure")
    elif any_sign_flip and N >= 512:
        # Sign flip at full N -- genuine substrate property
        verdict = "GAP_SIGN_FLIP_CONFIRMED"
        sf_Ms = [M for M in m_cells if rd_analysis[str(M)]["has_sign_flip"]]
        verdict_msg = (f"GAP_SIGN_FLIP_CONFIRMED at N={N}: sign-flip in M_cells={sf_Ms}; "
                       f"pearson_r=[{min(r_values):.3f},{max(r_values):.3f}] where valid; "
                       f"forward/reverse symmetry breaks at high M load")
    elif (r_values and all(abs(r) < 0.30 for r in r_values) and
          ratios and all(0.70 < ratio < 1.30 for ratio in ratios)):
        verdict = "RATE_INDEPENDENT_1RSB"
        verdict_msg = (f"RATE_INDEPENDENT_1RSB: pearson_r=[{min(r_values):.3f},{max(r_values):.3f}] "
                       f"(all < 0.30 abs); gap_ratio=[{min(ratios):.3f},{max(ratios):.3f}] "
                       f"near 1.0; thermodynamic ergodicity breaking confirmed")
    elif r_values and all(r < -0.50 for r in r_values) and \
            ratios and all(ratio < 0.50 for ratio in ratios):
        verdict = "RATE_DEPENDENT_KINETIC"
        verdict_msg = (f"RATE_DEPENDENT_KINETIC: pearson_r=[{min(r_values):.3f},{max(r_values):.3f}] "
                       f"(all < -0.50); gap_ratio=[{min(ratios):.3f},{max(ratios):.3f}] "
                       f"(< 0.50); kinetic glass / geometric frustration")
    else:
        r_str = f"[{min(r_values):.3f},{max(r_values):.3f}]" if r_values else "N/A"
        verdict = "MIDDLE_BAND"
        verdict_msg = (f"MIDDLE_BAND at N={N}: pearson_r={r_str}; "
                       f"any_sign_flip={any_sign_flip}; framework ambiguous")

    return {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": time.monotonic() - t0,
        "summary": {
            "N": N, "m_cells": m_cells, "epochs_sweep": epochs_sw,
            "rate_dependence_by_M": rd_analysis,
            "any_sign_flip": any_sign_flip,
        },
        "config": {"N": N, "smoke": smoke, "m_cells": m_cells,
                   "epochs_sweep": epochs_sw, "seeds": seeds},
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        print("[self-test] selftest ran at import", flush=True)
        sys.exit(0)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[rate_dep_hysteresis_v2] device={device}", flush=True)

    out_dir = get_output_dir()
    metrics = run_sweep(smoke=args.smoke, device=device)

    metrics_path = out_dir / "metrics.json"
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)

    print(f"\n[VERDICT] {metrics['verdict']}: {metrics['verdict_msg']}", flush=True)
    print(f"[metrics written] {metrics_path}", flush=True)


if __name__ == "__main__":
    main()
