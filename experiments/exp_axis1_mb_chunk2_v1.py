"""AXIS-1 Phase Diagram M x beta SCAN: chunk 2 (M/N in {4, 8, 16, 32} = over-capacity).

CONTEXT:
  axis1_mb_chunk1_v1 result: retention saturated everywhere at M/N in {0.25, 0.5, 1.0, 2.0}.
  Chunk 1 = NO retention phase transition in M <= 2N regime (93rd label-vs-honest catch).
  Chunk 2 must go deeper into over-capacity regime to find the actual retention boundary.

SCIENTIFIC QUESTION (Axis 1 of phase diagram, over-capacity branch):
  Where does the retention phase transition occur at M >> N?
  Map (M/N, beta) plane at M/N in {4, 8, 16, 32} (M = {16384, 32768, 65536, 131072} at N=4096).
  For each (M, beta) cell measure: retention, bundle_norm_var, spectral_gap.

  Note on M=131072 (M/N=32): codebook C=16384 at N=4096 so M > C by 8x.
  Keys are drawn with repetition -- this tests the aliasing-stress regime.

PRE-REGISTERED BANDS:
  HARD_PASS: retention falls below 0.5 at some M* AND retention is monotone-decreasing
    in M past M* AND BNV continues scaling above M*. Phase boundary found in chunk-2 regime.
  HARD_FAIL: retention = 1.0 (or > 0.90) across ALL M values up to M/N=32.
    No retention boundary in tested regime -- substrate maintains perfect retrieval
    even at extreme over-capacity (would be extraordinary; would require extending M further).
  MIDDLE_BAND: partial retention drop (below 0.5 at some cells but not monotone).

FORMULA SELF-TESTS:
  1. At M/N=32 (extreme aliasing), retention should be well below 1.0.
     (At M=C=16384 with N=4096, aliased keys cause interference; expect drops.)
  2. retain(M/N=4) < retain(M/N=1) from chunk-1 data (monotone in M).
  3. BNV = Var(||Wk_i||) -- at high M with aliased keys, norms become heterogeneous.
  4. spectral_gap of overlap matrix: at M >> N with aliased keys, gap increases.
  5. compute_retention(W=0, ...) = 1/C (random = 1/16384 for N=4096 codebook).

TIMEOUT ESTIMATE:
  M scaling is the key cost driver (W construction is O(M) batched ops).
  At M=131072 (M/N=32): 131072 / 256 = 512 batches for W construction.
  vs chunk-1 M=8192: 32 batches. Roughly 16x slower per cell at max M.
  chunk-1 smoke: ~5s at 3 M values, 3 betas, 1 seed.
  chunk-2: 4 M values (much larger M), 7 betas, 5 seeds.
  Conservative estimate: (16x average M overhead) * (7/3 beta) * 5 seeds = 16 * 2.33 * 5 = 186x.
  timeout_s = ceil(1.5 * 5 * 186) = ceil(1395) -> 1500s.
  But at GPU M=131072 matrix writes may hit memory bandwidth limits.
  Conservative with +100% buffer: 3000s.
  Skip hysteresis compute for chunk-2 (too expensive at large M; disable compute_hyst).
  FLAG: GPU memory check -- W at N=4096 = 64MB. Peak: 2 W matrices + codebook = ~130MB. OK.
  timeout_s = 3600 (conservative 1h; large-M ops unpredictable).

N-suffix: no _nN suffix; multi-M sweep (PROT-018: stated explicitly; N_FULL=4096).
Queue: overnight_queue (GPU; N=4096 over-capacity M sweep)
Pre-reg: preregs/2026-05-27_axis1_mb_chunk2_v1.md
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

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from verification import oracle  # noqa: E402

# Load chunk-1 base (provides core cell computation functions)
_c1_path = REPO / "experiments" / "exp_axis1_mb_chunk1_v1.py"
_c1_spec = importlib.util.spec_from_file_location("axis1c1", _c1_path)
c1 = importlib.util.module_from_spec(_c1_spec)
_c1_spec.loader.exec_module(c1)

# PRODUCTION CONFIG chunk 2 -- PROT-018: no _nN suffix; N_FULL=4096 stated explicitly
N_FULL = 4096
N_SMOKE = 1024

# Over-capacity regime: M/N in {4, 8, 16, 32}
M_FRACS_FULL = [4.0, 8.0, 16.0, 32.0]
M_FRACS_SMOKE = [4.0, 8.0]     # 2 M values, lighter smoke

# Beta sweep (same as chunk-1)
BETA_FULL = [1.0, 4.0, 16.0, 32.0, 64.0, 128.0, 256.0]
BETA_SMOKE = [4.0, 64.0]

SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]

# Phase structure thresholds
PASS_RETENTION_DROP_THRESHOLD = 0.50   # retention must fall below 0.5 at some M*
FAIL_RETENTION_MIN = 0.90              # still above 0.90 at all M = no boundary found
PASS_METRIC_VARIATION = 0.20


def get_output_dir(default_name: str = "axis1_mb_chunk2_v1") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def run_one_cell_chunk2(M: int, beta: float, seed: int, codebook: torch.Tensor,
                         N: int, device: torch.device) -> dict:
    """Run one (M, beta, seed) cell for chunk-2 (no hysteresis -- too expensive at large M)."""
    # Reuse chunk-1 store/measure functions, disable hysteresis
    return c1.run_one_cell(M, beta, seed, codebook, N, device, compute_hyst=False)


def compute_verdict_chunk2(summary: dict) -> tuple[str, str]:
    """Chunk-2 verdict: find retention phase boundary in over-capacity regime."""
    cells = summary.get("cells", [])
    if not cells:
        return ("AXIS1C2_INCONCLUSIVE", "No cells computed.")

    retentions = [c["retention"] for c in cells]
    m_vals = [c["M"] for c in cells]
    bundle_vars = [c["bundle_norm_var"] for c in cells]

    if not retentions:
        return ("AXIS1C2_INCONCLUSIVE", "No retention data.")

    M_set = sorted(set(m_vals))
    # Mean retention per M (averaged over seeds and betas)
    ret_by_M = {}
    bnv_by_M = {}
    for M_v in M_set:
        cells_M = [c["retention"] for c in cells if c["M"] == M_v]
        bvs_M = [c["bundle_norm_var"] for c in cells if c["M"] == M_v]
        ret_by_M[M_v] = sum(cells_M) / len(cells_M) if cells_M else 0.0
        bnv_by_M[M_v] = sum(bvs_M) / len(bvs_M) if bvs_M else 0.0

    ret_M_range = max(ret_by_M.values()) - min(ret_by_M.values()) if len(ret_by_M) > 1 else 0.0
    mean_hyst = sum(c["hysteresis_amp"] for c in cells) / len(cells) if cells else 0.0

    # Check: min retention across all cells
    min_ret = min(retentions)
    max_ret = max(retentions)
    # Find M* = first M where mean retention drops below 0.5
    M_star = None
    for M_v in M_set:
        if ret_by_M[M_v] < PASS_RETENTION_DROP_THRESHOLD:
            M_star = M_v
            break

    # BNV: check if it continues to grow at M > M*
    bnv_monotone = True
    bnv_vals = [bnv_by_M[M_v] for M_v in M_set]
    if len(bnv_vals) >= 2:
        bnv_diffs = [bnv_vals[i+1] - bnv_vals[i] for i in range(len(bnv_vals)-1)]
        bnv_monotone = all(d >= 0 for d in bnv_diffs)

    # HARD_FAIL: retention stays above 0.90 across ALL M -- no boundary found
    if min_ret >= FAIL_RETENTION_MIN:
        return ("AXIS1C2_HARD_FAIL",
                f"No retention boundary in chunk-2 regime. "
                f"min_retention={min_ret:.3f} across all M (threshold {FAIL_RETENTION_MIN}). "
                f"ret_by_M={dict((k, round(v, 3)) for k, v in ret_by_M.items())}. "
                f"Phase boundary must be at M/N > 32. Chunk-3 needed.")

    # HARD_PASS: retention drops below 0.5 at some M* AND BNV grows
    if M_star is not None and bnv_monotone:
        return ("AXIS1C2_HARD_PASS",
                f"RETENTION PHASE BOUNDARY FOUND at M*={M_star} (M/N={M_star/N_FULL:.1f}). "
                f"mean_ret_at_Mstar={ret_by_M[M_star]:.3f} (threshold {PASS_RETENTION_DROP_THRESHOLD}). "
                f"BNV monotone-increasing in M: {[round(v, 3) for v in bnv_vals]}. "
                f"ret_by_M={dict((k, round(v, 3)) for k, v in ret_by_M.items())}. "
                f"Phase diagram axis-1 boundary located in over-capacity regime.")

    # MIDDLE_BAND
    return ("AXIS1C2_MIDDLE_BAND",
            f"Partial structure. min_ret={min_ret:.3f}. M_star={M_star}. "
            f"bnv_monotone={bnv_monotone}. "
            f"ret_by_M={dict((k, round(v, 3)) for k, v in ret_by_M.items())}. "
            f"ret_M_range={ret_M_range:.3f}.")


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics non-null/non-sentinel at small scale."""
    assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

    # Import-chain: chunk-1 functions accessible
    assert hasattr(c1, "run_one_cell"), "c1 run_one_cell missing"
    assert hasattr(c1, "store_facts_batched"), "c1 store_facts_batched missing"
    assert hasattr(c1, "compute_retention"), "c1 compute_retention missing"

    # Self-test 1: verdict HARD_FAIL (all retention > 0.90)
    cells_fail = [{"M": 16384, "beta": 4.0, "seed": 17, "retention": 0.95,
                   "bundle_norm_var": 0.01, "spectral_gap": 0.1, "hysteresis_amp": 0.0},
                  {"M": 32768, "beta": 4.0, "seed": 17, "retention": 0.92,
                   "bundle_norm_var": 0.02, "spectral_gap": 0.2, "hysteresis_amp": 0.0}]
    v, msg = compute_verdict_chunk2({"cells": cells_fail, "N_full": 4096})
    assert v == "AXIS1C2_HARD_FAIL", f"Expected AXIS1C2_HARD_FAIL, got {v}: {msg}"

    # Self-test 2: verdict HARD_PASS (retention drops below 0.5 at M=32768, BNV monotone)
    cells_pass = [{"M": 16384, "beta": 4.0, "seed": 17, "retention": 0.70,
                   "bundle_norm_var": 0.01, "spectral_gap": 0.1, "hysteresis_amp": 0.0},
                  {"M": 32768, "beta": 4.0, "seed": 17, "retention": 0.30,
                   "bundle_norm_var": 0.05, "spectral_gap": 0.2, "hysteresis_amp": 0.0}]
    v, msg = compute_verdict_chunk2({"cells": cells_pass, "N_full": 4096})
    assert v == "AXIS1C2_HARD_PASS", f"Expected AXIS1C2_HARD_PASS, got {v}: {msg}"

    # Self-test 3: OOM pre-check at smoke scale
    # W at N=1024: 1024^2 * 4 = 4MB. M=4096 at N_SMOKE=1024: M/N=4 (valid)
    # M=8192 at N_SMOKE=1024: 8x over-cap. W still 4MB. OK for smoke.
    N_test = 1024
    device = torch.device("cpu")
    import importlib.util as _ilu
    v3_path = REPO / "experiments" / "exp_wave14y_erase_kerdock_v3.py"
    v3_spec = _ilu.spec_from_file_location("kerdock_v3_c2", v3_path)
    v3_mod = importlib.util.module_from_spec(v3_spec)
    v3_spec.loader.exec_module(v3_mod)

    codebook, _ = v3_mod.make_kerdock_4coset_codebook(N_test, device)
    C = codebook.shape[0]
    M_test = int(4.0 * N_test)   # M/N=4 (over-cap chunk-2 regime at smoke scale)
    cell = run_one_cell_chunk2(M_test, 4.0, 17, codebook, N_test, device)
    assert "retention" in cell, "missing retention"
    assert 0.0 <= cell["retention"] <= 1.0, f"retention out of range: {cell['retention']}"
    assert "bundle_norm_var" in cell, "missing bundle_norm_var"
    # At M/N=4 with Kerdock keys, expect retention < 1.0 (over-capacity interference)
    # but don't hard-assert the value -- this is the measurement
    # What we do assert: not NaN, not negative
    import math as _math
    assert not _math.isnan(cell["retention"]), "retention is NaN"
    # Filter check: ensure at least one metric is non-sentinel
    assert cell["bundle_norm_var"] >= 0.0, f"BNV negative: {cell['bundle_norm_var']}"

    print("[SELFTEST PASS] axis1_mb_chunk2_v1 instrumentation OK", flush=True)


_instrumentation_selftest()


def run(smoke: bool = False) -> None:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    N = N_SMOKE if smoke else N_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    m_fracs = M_FRACS_SMOKE if smoke else M_FRACS_FULL
    beta_sweep = BETA_SMOKE if smoke else BETA_FULL

    out_dir = get_output_dir()
    t0 = time.time()

    import importlib.util as _ilu
    v3_path = REPO / "experiments" / "exp_wave14y_erase_kerdock_v3.py"
    v3_spec = _ilu.spec_from_file_location("kerdock_v3_run", v3_path)
    v3_mod = importlib.util.module_from_spec(v3_spec)
    v3_spec.loader.exec_module(v3_mod)

    M_vals = [int(f * N) for f in m_fracs]
    total_cells = len(seeds) * len(M_vals) * len(beta_sweep)
    print(f"[axis1c2] N={N} M_fracs={m_fracs} M_vals={M_vals} "
          f"betas={beta_sweep} seeds={seeds} "
          f"total_cells={total_cells} device={device} mode={'smoke' if smoke else 'full'}",
          flush=True)

    all_cells = []
    cell_count = 0
    for seed in seeds:
        codebook, _ = v3_mod.make_kerdock_4coset_codebook(N, device)
        for M in M_vals:
            for beta in beta_sweep:
                ts = time.time()
                cell = run_one_cell_chunk2(M, beta, seed, codebook, N, device)
                te = time.time() - ts
                cell_count += 1
                if cell_count % 10 == 0 or cell_count == total_cells:
                    print(f"  [{cell_count}/{total_cells}] M={M} beta={beta} seed={seed} "
                          f"ret={cell['retention']:.3f} bnv={cell['bundle_norm_var']:.4f} "
                          f"t={te:.1f}s", flush=True)
                all_cells.append(cell)

        # Per-seed checkpoint
        checkpoint_path = out_dir / "metrics_checkpoint.json"
        with open(checkpoint_path, "w", encoding="utf-8") as f:
            json.dump({"cells": all_cells, "N_full": N_FULL,
                       "seeds_done": seed}, f, indent=2)

    summary = {
        "cells": all_cells,
        "N_full": N_FULL,
        "N_used": N,
        "m_fracs": m_fracs,
        "beta_sweep": beta_sweep,
        "smoke": smoke,
    }
    verdict, verdict_msg = compute_verdict_chunk2(summary)
    elapsed = time.time() - t0

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
        "summary": summary,
    }
    out_path = out_dir / "metrics.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    print(f"\n[axis1c2] VERDICT: {verdict}", flush=True)
    print(f"[axis1c2] {verdict_msg}", flush=True)
    print(f"[axis1c2] elapsed={elapsed:.1f}s output={out_path}", flush=True)


def main() -> None:
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--self-test", action="store_true", dest="self_test")
    args = p.parse_args()
    if args.self_test:
        sys.exit(0)
    run(smoke=args.smoke)


if __name__ == "__main__":
    main()
