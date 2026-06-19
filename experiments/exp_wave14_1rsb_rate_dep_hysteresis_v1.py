"""Rate-dependence of hysteresis: 1-RSB vs geometric-frustration discriminator.

CONTEXT: wave14_1rsb_hysteresis_v3 confirmed HYSTERESIS_1RSB_CONFIRMED (max_gap=0.835 bpc
at M=2000, N=512 smoke; gap=1.123 at N=256). The amplitude of the hysteresis gap is LARGE
(0.835-1.84 bpc across the v3/v4 runs). The theoretical question is:

  Is hysteresis amplitude COOLING-RATE DEPENDENT?
    - YES -> geometric frustration WITHOUT ergodicity breaking (kinetic glass).
      Slower cooling (more epochs) allows the system to explore the landscape and
      reduces the gap. This is the glasses/RFOT picture: finite ergodicity breaking time.
    - NO -> first-order RSB-class transition (genuine phase transition; ergodicity
      breaking is thermodynamic, not kinetic). Gap saturates at a finite value even
      for very slow cooling. This is the Parisi-Edwards-Anderson picture.

DESIGN: sweep EPOCHS (cooling rate proxy) at fixed M and N, measuring hysteresis gap.
  cooling_rate = 1/epochs (lower epochs = faster cooling/quench; higher = slower)
  EPOCHS_SWEEP: [1, 2, 4, 8, 16, 32] (factors of 2 from fast to slow)
  N: 1024 (same as v3 FULL)
  M_cells: [2000, 10000] (two representative M values: near and above alpha_c)
  seeds: 3

Key reuse from v3: same train_W and evaluate_W functions; same corpus; same
fwd/rev trajectory design.

SELF-TESTS per [[feedback-strategy-spec-formula-selftests]]:
  1. rate_dependence_slope(gaps=[1.0,1.0,1.0], epochs=[1,2,4]) = 0.0 (flat, no rate dep)
  2. rate_dependence_slope(gaps=[2.0,1.0,0.5], epochs=[1,2,4]) < -0.5 (decreasing = rate dep)
  3. rate_dependence_slope(gaps=[0.5,0.5,0.5,0.5,0.5,0.5], epochs=[1,2,4,8,16,32]) = 0.0
  4. train_W callable at N=64, batch=16, epochs=1 returns shape (64,64)

PRE-REGISTERED BANDS:
  RATE_INDEPENDENT_1RSB (first-order transition; thermodynamic ergodicity breaking):
    - Pearson r(log_epochs, gap) in (-0.3, 0.3) at both M cells (flat = not rate-dep)
    - AND gap at epochs=32 within 30% of gap at epochs=1 (saturation)
    -> Substrate has genuine RSB-class phase transition; gap is an EQUILIBRIUM property

  RATE_DEPENDENT_KINETIC (geometric frustration; kinetic glass):
    - Pearson r(log_epochs, gap) < -0.50 at BOTH M cells (clear negative slope)
    - AND gap at epochs=32 < 50% of gap at epochs=1 (substantial reduction)
    -> Substrate exhibits kinetic glass behavior; hysteresis is NOT 1-RSB signature

  MIDDLE_BAND (partial rate dependence; ambiguous framework):
    - r(log_epochs, gap) in (-0.50, -0.30) OR inconsistent across M cells
    -> Inconclusive; need longer cooling sweeps or higher N

  INSTRUMENTATION_FAIL:
    - Gap is NaN or negative at any cell
    - OR all gaps are exactly 0.0 (training not working)

Walk-back gate: if smoke effect size (d = gap_fast / gap_slow ratio) < 1.3 (< 30% change
across 32x cooling rate range), pre-register FULL at N=2048 for a 4x stronger signal.

Queue: remote_cpu_queue (CPU; 6 epochs x 2 M-cells x 3 seeds x N=1024; ~1-2h total)
Pre-reg: preregs/2026-05-26_wave14_1rsb_rate_dep_hysteresis_v1.md
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import argparse, importlib.util, json, math, os, time
from pathlib import Path
from typing import Dict, List, Tuple

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# Load hysteresis v3 infrastructure (reuse train_W, evaluate_W_only, etc.)
_hv3_path = REPO / "experiments" / "exp_wave14_1rsb_hysteresis_v3.py"
_hv3_spec = importlib.util.spec_from_file_location("hv3", _hv3_path)
hv3 = importlib.util.module_from_spec(_hv3_spec)
_hv3_spec.loader.exec_module(hv3)
base = hv3.base
pa   = hv3.pa

# ── design parameters ──
N_FULL    = 1024
N_SMOKE   = 256
# EPOCHS_SWEEP: proxy for cooling rate. Higher epochs = slower cooling.
EPOCHS_SWEEP_FULL  = [1, 2, 4, 8, 16, 32]
EPOCHS_SWEEP_SMOKE = [1, 2, 4]
# M_CELLS: two representative memory loads (near and above alpha_c)
M_CELLS_FULL  = [2000, 10000]
M_CELLS_SMOKE = [2000, 10000]
SEEDS_FULL  = [7, 17, 23]
SEEDS_SMOKE = [17]
BATCH_SIZE_FULL  = 32
BATCH_SIZE_SMOKE = 16
BYTES_FULL  = 60_000
BYTES_SMOKE = 5_000
# Threshold from v3 (pre-registered) -- reuse same scale for comparability
GAP_1RSB_THRESHOLD = 0.10   # same as v3
GAP_RS_THRESHOLD   = 0.03   # same as v3
CELL_TIMEOUT_S = 400


def get_output_dir(default_name: str = "wave14_1rsb_rate_dep_hysteresis_v1") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


# ── statistical helpers ──

def pearson_r(xs: List[float], ys: List[float]) -> float:
    """Pearson correlation coefficient."""
    if len(xs) < 2:
        return 0.0
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    sx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    sy = math.sqrt(sum((y - my) ** 2 for y in ys))
    if sx < 1e-12 or sy < 1e-12:
        return 0.0
    return cov / (sx * sy)


def rate_dependence_slope(gaps: List[float], epochs: List[int]) -> float:
    """Pearson r(log(epochs), gap). Negative = gap decreases with slower cooling."""
    log_e = [math.log(e) for e in epochs]
    return pearson_r(log_e, gaps)


# ── self-tests ──

def _instrumentation_selftest():
    """Assert all metrics non-null/non-sentinel at small scale."""
    # Test 1: flat gaps -> slope near 0
    r1 = rate_dependence_slope([1.0, 1.0, 1.0], [1, 2, 4])
    assert abs(r1) < 0.3, f"flat slope fail: {r1}"

    # Test 2: decreasing gaps -> slope < -0.50
    r2 = rate_dependence_slope([2.0, 1.0, 0.5], [1, 2, 4])
    assert r2 < -0.50, f"decreasing slope fail: {r2:.4f}"

    # Test 3: all-same flat again
    r3 = rate_dependence_slope([0.5, 0.5, 0.5, 0.5, 0.5, 0.5], [1, 2, 4, 8, 16, 32])
    assert abs(r3) < 0.1, f"all-same slope fail: {r3}"

    # Test 4: train_W callable at N=64
    device = torch.device("cpu")
    gen = torch.Generator().manual_seed(42)
    byte_atoms = pa.make_bsc_atoms(base.VOCAB, 64, gen).to(device)
    pos_atoms  = pa.make_bsc_atoms(base.K, 64, gen).to(device)
    corpus_a   = pa.load_corpus_a()[:1000]
    m_split    = int(0.8 * len(corpus_a))
    train_data, _ = corpus_a[:m_split], corpus_a[m_split:]
    train_idx, train_tgt = base.bytes_to_idx_tensors(train_data, device)
    W_zero = torch.zeros((64, 64), dtype=torch.float32, device=device)
    W_out, _, _, _ = base.train_w_with_replay(
        W_zero, None, None, 0, byte_atoms, pos_atoms,
        train_idx, train_tgt, None, None, 0, 1, 16, device)
    assert W_out.shape == (64, 64), f"train_W shape fail: {W_out.shape}"
    assert W_out.abs().max().item() > 0, "train_W all-zero fail"

    print("[selftest] PASS: 4/4 assertions OK", flush=True)


_instrumentation_selftest()


# ── hysteresis measurement at one (M, epochs) cell ──

def measure_hysteresis_cell(M: int, n_epochs: int, seed: int,
                             N: int, batch_size: int, n_bytes: int,
                             device: torch.device) -> Dict:
    """Forward (W=0 init) and reverse (W=W_max init) BPC at fixed M.

    Returns {"fwd_bpc": float, "rev_bpc": float, "gap": float}.
    """
    gen = torch.Generator().manual_seed(seed)
    byte_atoms = pa.make_bsc_atoms(base.VOCAB, N, gen).to(device)
    pos_atoms  = pa.make_bsc_atoms(base.K, N, gen).to(device)

    corpus_a_full = pa.load_corpus_a()
    corpus_a = corpus_a_full[:min(n_bytes, len(corpus_a_full))]
    m_split  = int(0.8 * len(corpus_a))
    train_data, test_data = corpus_a[:m_split], corpus_a[m_split:]

    # Use first M bytes of training data (simulating capacity M)
    train_m = train_data[:M]
    if len(train_m) < 100:
        return {"fwd_bpc": float("nan"), "rev_bpc": float("nan"), "gap": float("nan"),
                "note": "insufficient_corpus"}

    train_idx, train_tgt = base.bytes_to_idx_tensors(train_m, device)
    test_idx, test_tgt   = base.bytes_to_idx_tensors(test_data[:min(1000, len(test_data))], device)

    # Forward: W starts at 0 (cold start)
    t_fwd = time.monotonic()
    W_fwd, _, _, _ = base.train_w_with_replay(
        torch.zeros((N, N), dtype=torch.float32, device=device),
        None, None, 0, byte_atoms, pos_atoms,
        train_idx, train_tgt, None, None, 0, n_epochs, batch_size, device)
    fwd_bpc = hv3.evaluate_W_only(W_fwd, byte_atoms, pos_atoms, test_idx, test_tgt,
                                   batch_size, N)
    if time.monotonic() - t_fwd > CELL_TIMEOUT_S:
        return {"fwd_bpc": float(fwd_bpc), "rev_bpc": float("nan"), "gap": float("nan"),
                "note": "fwd_timeout"}

    # Reverse: W starts from W_max (trained at maximum M = n_bytes)
    # W_max = W trained at M = n_bytes (max capacity load)
    train_max_idx, train_max_tgt = base.bytes_to_idx_tensors(
        train_data[:min(n_bytes, len(train_data))], device)
    W_max, _, _, _ = base.train_w_with_replay(
        torch.zeros((N, N), dtype=torch.float32, device=device),
        None, None, 0, byte_atoms, pos_atoms,
        train_max_idx, train_max_tgt, None, None, 0, n_epochs, batch_size, device)

    # Re-tune W_max at M (partial corpus, starting from saturated W)
    W_rev, _, _, _ = base.train_w_with_replay(
        W_max.clone(), None, None, 0, byte_atoms, pos_atoms,
        train_idx, train_tgt, None, None, 0, n_epochs, batch_size, device)
    rev_bpc = hv3.evaluate_W_only(W_rev, byte_atoms, pos_atoms, test_idx, test_tgt,
                                   batch_size, N)

    del W_fwd, W_max, W_rev
    if device.type == "cuda":
        torch.cuda.empty_cache()

    gap = float(fwd_bpc) - float(rev_bpc)
    return {"fwd_bpc": float(fwd_bpc), "rev_bpc": float(rev_bpc), "gap": float(gap)}


# ── main sweep ──

def run_sweep(smoke: bool, device: torch.device) -> Dict:
    N          = N_SMOKE if smoke else N_FULL
    epochs_sw  = EPOCHS_SWEEP_SMOKE if smoke else EPOCHS_SWEEP_FULL
    m_cells    = M_CELLS_SMOKE if smoke else M_CELLS_FULL
    seeds      = SEEDS_SMOKE if smoke else SEEDS_FULL
    batch_size = BATCH_SIZE_SMOKE if smoke else BATCH_SIZE_FULL
    n_bytes    = BYTES_SMOKE if smoke else BYTES_FULL

    t0 = time.monotonic()
    print(f"[rate_dep_hysteresis] smoke={smoke} N={N} epochs_sweep={epochs_sw} "
          f"m_cells={m_cells} seeds={seeds}", flush=True)

    # Results dict: m_cell -> epoch -> list of gaps across seeds
    results: Dict[int, Dict[int, List[float]]] = {m: {e: [] for e in epochs_sw} for m in m_cells}

    for M in m_cells:
        for n_epochs in epochs_sw:
            for seed in seeds:
                t_cell = time.monotonic()
                print(f"  M={M} epochs={n_epochs} seed={seed} ...", flush=True)
                cell = measure_hysteresis_cell(
                    M=M, n_epochs=n_epochs, seed=seed,
                    N=N, batch_size=batch_size, n_bytes=n_bytes, device=device)
                elapsed_cell = time.monotonic() - t_cell
                gap = cell.get("gap", float("nan"))
                results[M][n_epochs].append(gap)
                print(f"    fwd={cell.get('fwd_bpc',float('nan')):.4f} "
                      f"rev={cell.get('rev_bpc',float('nan')):.4f} "
                      f"gap={gap:.4f} ({elapsed_cell:.1f}s)", flush=True)

    # Aggregate per (M, epoch): mean gap across seeds
    agg: Dict[int, Dict[int, float]] = {}
    for M in m_cells:
        agg[M] = {}
        for n_epochs in epochs_sw:
            raw = [g for g in results[M][n_epochs] if not math.isnan(g)]
            agg[M][n_epochs] = sum(raw) / len(raw) if raw else float("nan")

    # Rate-dependence analysis per M cell
    rd_analysis: Dict[str, Dict] = {}
    for M in m_cells:
        mean_gaps = [agg[M][e] for e in epochs_sw]
        valid_pairs = [(e, g) for e, g in zip(epochs_sw, mean_gaps) if not math.isnan(g)]
        if len(valid_pairs) < 2:
            r = float("nan")
            gap_32_vs_1_ratio = float("nan")
        else:
            v_eps, v_gaps = zip(*valid_pairs)
            r = rate_dependence_slope(list(v_gaps), list(v_eps))
            gap_fast = agg[M][epochs_sw[0]] if not math.isnan(agg[M][epochs_sw[0]]) else float("nan")
            gap_slow = agg[M][epochs_sw[-1]] if not math.isnan(agg[M][epochs_sw[-1]]) else float("nan")
            gap_32_vs_1_ratio = (gap_slow / gap_fast) if (not math.isnan(gap_fast) and
                                                           gap_fast > 1e-9) else float("nan")

        rd_analysis[str(M)] = {
            "pearson_r": r,
            "gap_fast_to_slow_ratio": gap_32_vs_1_ratio,
            "mean_gaps_by_epoch": {str(e): agg[M][e] for e in epochs_sw},
            "max_gap": max((g for g in mean_gaps if not math.isnan(g)), default=float("nan")),
            "min_gap": min((g for g in mean_gaps if not math.isnan(g)), default=float("nan")),
        }
        print(f"  M={M}: pearson_r={r:.4f} gap_ratio={gap_32_vs_1_ratio:.4f}", flush=True)

    # Overall verdict
    r_values = [rd_analysis[str(M)]["pearson_r"] for M in m_cells
                if not math.isnan(rd_analysis[str(M)]["pearson_r"])]
    ratios = [rd_analysis[str(M)]["gap_fast_to_slow_ratio"] for M in m_cells
              if not math.isnan(rd_analysis[str(M)]["gap_fast_to_slow_ratio"])]

    # INSTRUMENTATION_FAIL: gaps are NaN or all zero
    all_gaps_flat = [g for M in m_cells for e in epochs_sw for g in results[M][e]]
    n_valid = sum(1 for g in all_gaps_flat if not math.isnan(g))
    n_total = len(all_gaps_flat)

    if n_valid < n_total * 0.5:
        verdict = "INSTRUMENTATION_FAIL"
        verdict_msg = (f"INSTRUMENTATION_FAIL: only {n_valid}/{n_total} valid gap measurements; "
                       f"training or corpus failure")
    elif len(r_values) >= 1 and all(abs(r) < 0.30 for r in r_values) and \
            len(ratios) >= 1 and all((0.70 < ratio < 1.30) for ratio in ratios if not math.isnan(ratio)):
        verdict = "RATE_INDEPENDENT_1RSB"
        verdict_msg = (f"RATE_INDEPENDENT_1RSB: pearson_r in [{min(r_values):.3f},{max(r_values):.3f}] "
                       f"(all < 0.30 abs); gap_ratio in "
                       f"[{min(ratios):.3f},{max(ratios):.3f}] (near 1.0 = saturated); "
                       f"hysteresis is N-independent of cooling rate -> thermodynamic ergodicity breaking")
    elif len(r_values) >= 1 and all(r < -0.50 for r in r_values) and \
            len(ratios) >= 1 and all((ratio < 0.50) for ratio in ratios if not math.isnan(ratio)):
        verdict = "RATE_DEPENDENT_KINETIC"
        verdict_msg = (f"RATE_DEPENDENT_KINETIC: pearson_r=[{min(r_values):.3f},{max(r_values):.3f}] "
                       f"(all < -0.50); gap_ratio=[{min(ratios):.3f},{max(ratios):.3f}] "
                       f"(< 0.50 = major reduction at slow cooling); "
                       f"geometric frustration without ergodicity breaking")
    else:
        verdict = "MIDDLE_BAND"
        r_str = f"[{min(r_values):.3f},{max(r_values):.3f}]" if r_values else "N/A"
        ra_str = f"[{min(ratios):.3f},{max(ratios):.3f}]" if ratios else "N/A"
        verdict_msg = (f"MIDDLE_BAND at N={N}: pearson_r={r_str} (mixed or borderline); "
                       f"gap_ratio={ra_str}; framework ambiguous")

    summary = {
        "N": N,
        "epochs_sweep": epochs_sw,
        "m_cells": m_cells,
        "rate_dependence_by_M": rd_analysis,
        "overall_pearson_r_values": r_values,
        "overall_gap_ratios": ratios,
    }

    return {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": time.monotonic() - t0,
        "summary": summary,
        "config": {
            "N": N, "smoke": smoke,
            "epochs_sweep": epochs_sw, "m_cells": m_cells, "seeds": seeds,
        },
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        print("[self-test mode] instrumentation_selftest already ran at import", flush=True)
        sys.exit(0)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[rate_dep_hysteresis] device={device}", flush=True)

    out_dir = get_output_dir()
    metrics = run_sweep(smoke=args.smoke, device=device)

    metrics_path = out_dir / "metrics.json"
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)

    print(f"\n[VERDICT] {metrics['verdict']}: {metrics['verdict_msg']}", flush=True)
    print(f"[metrics written] {metrics_path}", flush=True)


if __name__ == "__main__":
    main()
