"""Pred-4 (1-RSB): Hysteresis N-sweep -- confirm at N=2048 and N=4096.

CONTEXT: wave14_1rsb_hysteresis_v3 CONFIRMED at N=1024 (max BPC gap=1.84 >> 0.10).
This runs the identical stateful protocol at larger N to test whether hysteresis
PERSISTS (1-RSB) or SHRINKS toward zero (RS finite-size artifact).

Directly reuses v3 infrastructure: train_W, evaluate_W_only, pa.load_corpus_a,
pa.make_bsc_atoms, base.bytes_to_idx_tensors.

PRE-REGISTERED BANDS:
  HARD_PASS: max_gap >= 0.10 at >= 1 N value AND both show gap > 0.03
    (hysteresis confirmed at N > 1024; not shrinking with N)
  MIDDLE: max_gap in [0.03, 0.10) at >= 1 N value
  RS_HARD_FAIL: max_gap < 0.03 at ALL N values
    (v3 N=1024 result was finite-size artifact; RS continuous transition)

Self-tests:
  1. v3 functions (train_W, evaluate_W_only) importable from v3 module
  2. pa.load_corpus_a() non-empty
  3. train_W + evaluate_W_only return finite bpc at tiny N_test=64
  4. GAP_V3_N1024=1.84 positive finite

Queue: remote_cpu_queue (CPU; 2 N values x 6 M cells x 3 seeds; ~60-120 min)
Pre-reg: prereqs/2026-05-26_wave14_1rsb_hysteresis_v4_multi_N.md
Parent: wave14_1rsb_hysteresis_v3 N=1024 gap=1.84 CONFIRMED
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

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# Import v3 module to reuse its infrastructure directly
_v3_path = REPO / "experiments" / "exp_wave14_1rsb_hysteresis_v3.py"
_v3_spec = importlib.util.spec_from_file_location("v3_hysteresis", _v3_path)
v3_mod = importlib.util.module_from_spec(_v3_spec)
_v3_spec.loader.exec_module(v3_mod)

# Extract the helper functions from v3
train_W = v3_mod.train_W
evaluate_W_only = v3_mod.evaluate_W_only
base = v3_mod.base
pa = v3_mod.pa

# ─── design parameters ───
N_SWEEP_FULL = [2048, 4096]
N_SWEEP_SMOKE = [256, 512]

# M_SWEEP scaled to bracket capacity at each N relative to v3 N=1024 sweep
# v3 M_SWEEP_FULL = [2000, 5000, 10000, 20000, 35000, 48000]
# Scale by N/1024 to maintain same relative-to-capacity coverage
M_SWEEP_PER_N_FULL = {
    2048: [4000, 10000, 20000, 40000, 70000, 96000],
    4096: [8000, 20000, 40000, 80000, 140000, 192000],
}
M_SWEEP_SMOKE = [2000, 10000, 48000]  # same as v3 smoke

EPOCHS_FULL = 10
EPOCHS_SMOKE = 2
BATCH_SIZE_FULL = 32
BATCH_SIZE_SMOKE = 16
SEEDS_FULL = [7, 17, 23]
SEEDS_SMOKE = [17]
CELL_TIMEOUT_S = 900   # larger N needs more time

# Pre-registered thresholds (same as v3)
GAP_1RSB_THRESHOLD = 0.10
GAP_RS_THRESHOLD = 0.03
GAP_V3_N1024 = 1.84    # v3 reference


def get_output_dir(default_name: str) -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d: dict) -> None:
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    missing = required - set(d.keys())
    if missing:
        raise ValueError(f"metrics missing: {missing}")


def run_one_N(N: int, m_sweep: list, seeds: list, epochs: int, batch_size: int,
              out_dir: Path, global_t0: float) -> dict:
    """Run stateful hysteresis at one N value, all seeds. Returns per-N result."""
    device = torch.device("cpu")
    print(f"\n[run_one_N] N={N} m_sweep={m_sweep} seeds={seeds}", flush=True)

    corpus_a_full = pa.load_corpus_a()
    print(f"[data] corpus_a size: {len(corpus_a_full)} bytes", flush=True)
    m_max = min(m_sweep[-1], len(corpus_a_full))

    cells_by_M: dict = {m: {"fwd_bpc": [], "rev_bpc": []} for m in m_sweep}

    for seed in seeds:
        gen = torch.Generator().manual_seed(seed)
        byte_atoms = pa.make_bsc_atoms(base.VOCAB, N, gen).to(device)
        pos_atoms = pa.make_bsc_atoms(base.K, N, gen).to(device)

        # FORWARD: W_init=0 at M_min, fresh train at each M
        print(f"\n[N={N} seed={seed} FORWARD]", flush=True)
        for m in sorted(m_sweep):
            t_cell = time.monotonic()
            m_actual = min(m, len(corpus_a_full))
            data = corpus_a_full[:m_actual]
            idx, tgt = base.bytes_to_idx_tensors(data, device)
            split_m = int(0.8 * idx.shape[0])
            train_idx, test_idx = idx[:split_m], idx[split_m:]
            train_tgt, test_tgt = tgt[:split_m], tgt[split_m:]
            if train_idx.shape[0] == 0 or test_idx.shape[0] == 0:
                cells_by_M[m]["fwd_bpc"].append(float("nan"))
                continue
            W_zero = torch.zeros((N, N), dtype=torch.float32, device=device)
            W_fwd = train_W(W_zero, byte_atoms, pos_atoms, train_idx, train_tgt,
                            n_epochs=epochs, batch_size=batch_size)
            bpc = evaluate_W_only(W_fwd, byte_atoms, pos_atoms, test_idx, test_tgt,
                                   batch_size=batch_size, N=N)
            elapsed_cell = time.monotonic() - t_cell
            cells_by_M[m]["fwd_bpc"].append(float(bpc))
            print(f"  fwd N={N} M={m} seed={seed}: bpc={bpc:.4f} ({elapsed_cell:.0f}s)",
                  flush=True)
            if elapsed_cell > CELL_TIMEOUT_S:
                print(f"  [TIMEOUT] fwd cell M={m} took {elapsed_cell:.0f}s", flush=True)

        # REVERSE: W_init = W_max (train at M_max), re-tune descending
        print(f"\n[N={N} seed={seed} REVERSE]", flush=True)
        m_max_actual = min(m_max, len(corpus_a_full))
        data_max = corpus_a_full[:m_max_actual]
        idx_max, tgt_max = base.bytes_to_idx_tensors(data_max, device)
        split_max = int(0.8 * idx_max.shape[0])
        train_max = idx_max[:split_max]
        tgt_max_tr = tgt_max[:split_max]
        W_zero = torch.zeros((N, N), dtype=torch.float32, device=device)
        W_max = train_W(W_zero, byte_atoms, pos_atoms, train_max, tgt_max_tr,
                        n_epochs=epochs, batch_size=batch_size)
        print(f"  [W_max] N={N} seed={seed} computed", flush=True)

        for m in sorted(m_sweep, reverse=True):
            t_cell = time.monotonic()
            m_actual = min(m, len(corpus_a_full))
            data = corpus_a_full[:m_actual]
            idx, tgt = base.bytes_to_idx_tensors(data, device)
            split_m = int(0.8 * idx.shape[0])
            train_idx, test_idx = idx[:split_m], idx[split_m:]
            train_tgt, test_tgt = tgt[:split_m], tgt[split_m:]
            if train_idx.shape[0] == 0 or test_idx.shape[0] == 0:
                cells_by_M[m]["rev_bpc"].append(float("nan"))
                continue
            W_rev = train_W(W_max.clone(), byte_atoms, pos_atoms, train_idx, train_tgt,
                            n_epochs=epochs, batch_size=batch_size)
            bpc = evaluate_W_only(W_rev, byte_atoms, pos_atoms, test_idx, test_tgt,
                                   batch_size=batch_size, N=N)
            elapsed_cell = time.monotonic() - t_cell
            cells_by_M[m]["rev_bpc"].append(float(bpc))
            print(f"  rev N={N} M={m} seed={seed}: bpc={bpc:.4f} ({elapsed_cell:.0f}s)",
                  flush=True)

    # Compute per-M gaps
    max_gap = 0.0
    cells_summary = []
    for m in m_sweep:
        fwd_list = [x for x in cells_by_M[m]["fwd_bpc"] if math.isfinite(x)]
        rev_list = [x for x in cells_by_M[m]["rev_bpc"] if math.isfinite(x)]
        if not fwd_list or not rev_list:
            cells_summary.append({"M": m, "status": "no_data"})
            continue
        fwd_mean = sum(fwd_list) / len(fwd_list)
        rev_mean = sum(rev_list) / len(rev_list)
        gap = abs(fwd_mean - rev_mean)
        max_gap = max(max_gap, gap)
        cells_summary.append({
            "M": m,
            "fwd_bpc_mean": round(fwd_mean, 4),
            "rev_bpc_mean": round(rev_mean, 4),
            "gap_bpc": round(gap, 4),
        })
        print(f"  GAP N={N} M={m}: {gap:.4f} (fwd={fwd_mean:.4f} rev={rev_mean:.4f})", flush=True)

    print(f"[N={N} SUMMARY] max_gap={max_gap:.4f}", flush=True)
    return {
        "N": N,
        "max_hysteresis_gap_bpc": round(max_gap, 4),
        "cells": cells_summary,
    }


def _instrumentation_selftest():
    """Assert all claimed metrics non-null at small scale."""
    print("[selftest] running instrumentation self-test...", flush=True)

    # 1. Import sanity -- v3 functions loaded
    assert callable(train_W), "Selftest 1 FAIL: train_W not callable"
    assert callable(evaluate_W_only), "Selftest 1 FAIL: evaluate_W_only not callable"
    print("[selftest] 1/4 train_W, evaluate_W_only imported from v3 OK")

    # 2. load_corpus_a non-empty
    corpus = pa.load_corpus_a()
    assert len(corpus) > 100, f"Selftest 2 FAIL: corpus len={len(corpus)}"
    print(f"[selftest] 2/4 load_corpus_a OK ({len(corpus)} bytes)")

    # 3. train + eval at tiny N
    device = torch.device("cpu")
    N_tiny = 64
    gen = torch.Generator().manual_seed(42)
    byte_atoms = pa.make_bsc_atoms(base.VOCAB, N_tiny, gen).to(device)
    pos_atoms = pa.make_bsc_atoms(base.K, N_tiny, gen).to(device)
    data = corpus[:500]
    idx, tgt = base.bytes_to_idx_tensors(data, device)
    split = int(0.8 * idx.shape[0])
    W0 = torch.zeros((N_tiny, N_tiny), dtype=torch.float32, device=device)
    W_t = train_W(W0, byte_atoms, pos_atoms, idx[:split], tgt[:split],
                  n_epochs=2, batch_size=16)
    bpc = evaluate_W_only(W_t, byte_atoms, pos_atoms, idx[split:], tgt[split:],
                          batch_size=16, N=N_tiny)
    assert math.isfinite(bpc) and bpc > 0, f"Selftest 3 FAIL: bpc={bpc}"
    print(f"[selftest] 3/4 train+eval N=64 bpc={bpc:.4f} OK")

    # 4. Reference gap from v3
    assert math.isfinite(GAP_V3_N1024) and GAP_V3_N1024 > 0, \
        f"Selftest 4 FAIL: GAP_V3_N1024={GAP_V3_N1024}"
    print(f"[selftest] 4/4 v3 reference gap={GAP_V3_N1024} OK")

    print("[selftest] instrumentation self-test PASSED", flush=True)


_instrumentation_selftest()


def run(smoke: bool = False):
    t0 = time.monotonic()
    print(f"[exp] wave14_1rsb_hysteresis_v4_multi_N {'SMOKE' if smoke else 'FULL'}", flush=True)
    print(f"[ref] v3 N=1024 gap={GAP_V3_N1024} CONFIRMED", flush=True)

    N_sweep = N_SWEEP_SMOKE if smoke else N_SWEEP_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    epochs = EPOCHS_SMOKE if smoke else EPOCHS_FULL
    batch_size = BATCH_SIZE_SMOKE if smoke else BATCH_SIZE_FULL
    out_dir = get_output_dir("wave14_1rsb_hysteresis_v4_multi_N")

    results_per_N = {}

    for N in N_sweep:
        m_sweep = M_SWEEP_SMOKE if smoke else M_SWEEP_PER_N_FULL.get(N, M_SWEEP_SMOKE)
        r = run_one_N(N, m_sweep, seeds, epochs, batch_size, out_dir, t0)
        results_per_N[N] = r

        # Checkpoint after each N
        checkpoint = {"results_so_far": {str(k): v for k, v in results_per_N.items()},
                      "elapsed_s": round(time.monotonic() - t0, 1)}
        with open(out_dir / "checkpoint.json", "w") as f:
            json.dump(checkpoint, f, indent=2)

    # Verdict
    gaps = {N: r["max_hysteresis_gap_bpc"] for N, r in results_per_N.items()
            if math.isfinite(r["max_hysteresis_gap_bpc"])}

    n_pass = sum(1 for g in gaps.values() if g >= GAP_1RSB_THRESHOLD)
    n_rs_fail = sum(1 for g in gaps.values() if g < GAP_RS_THRESHOLD)
    n_total = len(gaps)
    gap_strs = " ".join(f"N={N}:gap={g:.4f}" for N, g in sorted(gaps.items()))

    if n_pass >= 1 and n_rs_fail == 0:
        verdict = "HYSTERESIS_1RSB_CONFIRMED_MULTI_N"
        verdict_msg = (
            f"HARD_PASS: 1-RSB hysteresis confirmed at {n_pass}/{n_total} N values >= {GAP_1RSB_THRESHOLD}. "
            f"All N show gap > {GAP_RS_THRESHOLD}. v3 N=1024 result generalizes. | {gap_strs}"
        )
    elif n_rs_fail == n_total and n_total > 0:
        verdict = "RS_HARD_FAIL_ALL_N"
        verdict_msg = (
            f"RS_HARD_FAIL: gap < {GAP_RS_THRESHOLD} at ALL N. "
            f"v3 N=1024 was finite-size artifact. RS continuous transition. | {gap_strs}"
        )
    else:
        verdict = "MIDDLE_BAND"
        verdict_msg = (
            f"MIDDLE_BAND: {n_pass}/{n_total} N pass, {n_rs_fail}/{n_total} RS-fail. | {gap_strs}"
        )

    elapsed = time.monotonic() - t0
    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": round(elapsed, 3),
        "summary": {
            "N_sweep": N_sweep,
            "gaps_by_N": {str(N): v for N, v in gaps.items()},
            "gap_v3_n1024_reference": GAP_V3_N1024,
            "results_per_N": {str(k): v for k, v in results_per_N.items()},
        },
        "config": {
            "N_sweep": N_sweep,
            "seeds": seeds,
            "epochs": epochs,
            "smoke": smoke,
        },
    }
    validate_metrics(metrics)
    metrics_file = out_dir / "metrics.json"
    with open(metrics_file, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"\n[verdict] {verdict}: {verdict_msg}", flush=True)
    print(f"Metrics saved to {metrics_file}", flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true", dest="self_test")
    args = parser.parse_args()
    if args.self_test:
        sys.exit(0)
    run(smoke=args.smoke)


if __name__ == "__main__":
    main()
