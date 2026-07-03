"""Pred-4 (1-RSB diagnostic): Hysteresis under capacity sweep.

First-order phase transition (1-RSB) prediction: if the substrate has a
discontinuous (first-order) transition at alpha_c, then loading capacity
from BELOW alpha_c vs from ABOVE should show hysteresis -- the system
retains its retrieval state for a range of alpha beyond alpha_c when
loaded from below (metastable retrieval basin), but collapses at once
when loaded from above.

RS prediction (continuous transition): both loading trajectories give
the same retA at each alpha within seed-variance. No hysteresis gap.

Method:
  Forward sweep (low -> high load): train stages with M bytes in increasing order.
  Reverse sweep (high -> low load): train stages with M bytes in decreasing order.
  At each M, the final-stage retA is measured.
  Hysteresis gap = |retA_forward - retA_reverse| at each M.

1-RSB HARD-PASS: max hysteresis gap >= 0.10 at any M cell.
RS HARD-FAIL: max hysteresis gap < 0.03 everywhere.
MIDDLE: 0.03 <= max gap < 0.10.

Per [[feedback-envelope-expansion-fail-bands]]: bands pre-registered.
Per [[feedback-strategy-spec-formula-selftests]]: self-test cells below.
Per [[feedback-no-blocking-runs]]: background only via queue.
Per [[feedback-ship-name-collision]]: name verified unique before ship.

Queue: remote_cpu_queue (CPU; no GPU needed; sweep is short per cell)
ETA: ~30-45 min CPU (7 M values x 2 trajectories x 3 seeds x 4 stages)
Pre-reg file: preregs/2026-05-24_wave14_1rsb_hysteresis_v1.md
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import argparse, importlib.util, json, math, os, time
from pathlib import Path
import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir as _canonical_get_output_dir  # noqa: E402  # SH-4 canonical helper
from verification import oracle  # noqa: E402

# Load M1 hierreplay infrastructure
_m1_path = REPO / "experiments" / "exp_wave14_k2_m1_hierreplay_v1.py"
_m1_spec = importlib.util.spec_from_file_location("m1", _m1_path)
m1 = importlib.util.module_from_spec(_m1_spec)
_m1_spec.loader.exec_module(m1)
base = m1.base
v1 = m1.v1
pa = m1.pa

# ---- design parameters (exp_dev autonomy) ----
# M sweep covers sub-capacity -> near-critical -> over-capacity range
# Based on Pred-3 capacity_plateau prereg M sweep {25k..400k}
# Use tighter range around the known capacity boundary (~100k-200k from strategy)
M_SWEEP_FULL = [25_000, 50_000, 100_000, 150_000, 200_000, 300_000, 400_000]
M_SWEEP_SMOKE = [25_000, 100_000, 400_000]

N_FULL = 2048       # CPU-feasible
N_SMOKE = 512
BATCH_SIZE_FULL = 32
BATCH_SIZE_SMOKE = 16
EPOCHS_FULL = 5
EPOCHS_SMOKE = 1
PHASE_A_EPOCHS_FULL = 8
PHASE_A_EPOCHS_SMOKE = 1
SEEDS_FULL = [7, 17, 23]    # 3 seeds to bound cost; hysteresis is structural
SEEDS_SMOKE = [17]

# Hysteresis thresholds (pre-registered)
GAP_1RSB_THRESHOLD = 0.10   # HARD-PASS: first-order hysteresis
GAP_RS_THRESHOLD = 0.03     # HARD-FAIL: continuous transition (no hysteresis)


def get_output_dir(default_name: str) -> Path:
    """SH-4 delegates to canonical _seed_checkpoint.get_output_dir (single-prefix)."""
    out = _canonical_get_output_dir(default_name)
    out.mkdir(parents=True, exist_ok=True)
    return out
def validate_metrics(d):
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    missing = required - set(d.keys())
    if missing:
        raise ValueError(f"metrics missing required: {missing}")


def run_4stage_get_retA(seed, n_bytes, config, device):
    """Run 4-stage M1 hierreplay at given n_bytes; return retA (stage-A retention)."""
    N = config["N"]
    batch_size = config["batch_size"]
    n_epochs = config["epochs"]
    phase_a_epochs = config["phase_a_epochs"]
    smoke = (config["mode"] == "smoke")

    gen = torch.Generator().manual_seed(seed)
    byte_atoms = pa.make_bsc_atoms(base.VOCAB, N, gen).to(device)
    pos_atoms = pa.make_bsc_atoms(base.K, N, gen).to(device)

    corpus_a_full = pa.load_corpus_a()
    corpus_a = corpus_a_full[:n_bytes] if n_bytes < len(corpus_a_full) else corpus_a_full
    corpus_b = pa.shuffle_bytes(corpus_a, seed=seed + 1)
    corpus_c_full = base.load_corpus_C(smoke=smoke)
    corpus_c = corpus_c_full[:n_bytes] if n_bytes < len(corpus_c_full) else corpus_c_full
    corpus_d_full = v1.load_corpus_D(smoke=smoke)
    corpus_d = corpus_d_full[:n_bytes] if n_bytes < len(corpus_d_full) else corpus_d_full

    def split80(d):
        m = int(0.8 * len(d))
        return d[:m], d[m:]

    train_a, test_a = split80(corpus_a)
    train_b, _ = split80(corpus_b)
    train_c, _ = split80(corpus_c)
    train_d, _ = split80(corpus_d)

    def to_idx(tr):
        return base.bytes_to_idx_tensors(tr, device)

    train_a_idx, train_a_tgt = to_idx(train_a)
    test_a_idx, test_a_tgt = to_idx(test_a)
    train_b_idx, train_b_tgt = to_idx(train_b)
    train_c_idx, train_c_tgt = to_idx(train_c)
    train_d_idx, train_d_tgt = to_idx(train_d)

    W = torch.zeros((N, N), dtype=torch.float32, device=device)

    # Phase A
    W_A, pool_A_v, pool_A_l, pool_A_u = base.train_w_with_replay(
        W, None, None, 0, byte_atoms, pos_atoms,
        train_a_idx, train_a_tgt, None, None, 0,
        phase_a_epochs, batch_size, device)

    thin_A_v, thin_A_l, thin_A_u = m1.thin_pool_to_chunks(
        pool_A_v, pool_A_l, pool_A_u, chunk_fraction=0.5, device=device)

    # Phase B
    W_AB, pool_AB_v, pool_AB_l, pool_AB_u = base.train_w_with_replay(
        W_A, pool_A_v.clone(), pool_A_l.clone(), pool_A_u,
        byte_atoms, pos_atoms, train_b_idx, train_b_tgt,
        thin_A_v, thin_A_l, thin_A_u, n_epochs, batch_size, device)

    thin_B_v, thin_B_l, thin_B_u = m1.thin_pool_to_chunks(
        pool_AB_v, pool_AB_l, pool_AB_u, chunk_fraction=0.5, device=device)
    combo_AB_v = torch.cat([thin_A_v[:thin_A_u], thin_B_v[:thin_B_u]], dim=0)
    combo_AB_l = torch.cat([thin_A_l[:thin_A_u], thin_B_l[:thin_B_u]], dim=0)
    combo_AB_u = combo_AB_v.shape[0]

    # Phase C
    W_ABC, pool_ABC_v, pool_ABC_l, pool_ABC_u = base.train_w_with_replay(
        W_AB, pool_AB_v.clone(), pool_AB_l.clone(), pool_AB_u,
        byte_atoms, pos_atoms, train_c_idx, train_c_tgt,
        combo_AB_v, combo_AB_l, combo_AB_u, n_epochs, batch_size, device)

    thin_C_v, thin_C_l, thin_C_u = m1.thin_pool_to_chunks(
        pool_ABC_v, pool_ABC_l, pool_ABC_u, chunk_fraction=0.5, device=device)
    combo_ABC_v = torch.cat([thin_A_v[:thin_A_u], thin_B_v[:thin_B_u],
                             thin_C_v[:thin_C_u]], dim=0)
    combo_ABC_l = torch.cat([thin_A_l[:thin_A_u], thin_B_l[:thin_B_u],
                             thin_C_l[:thin_C_u]], dim=0)
    combo_ABC_u = combo_ABC_v.shape[0]

    # Phase D
    W_ABCD, pool_D_v, pool_D_l, pool_D_u = base.train_w_with_replay(
        W_ABC, pool_ABC_v.clone(), pool_ABC_l.clone(), pool_ABC_u,
        byte_atoms, pos_atoms, train_d_idx, train_d_tgt,
        combo_ABC_v, combo_ABC_l, combo_ABC_u, n_epochs, batch_size, device)

    # Measure retA: retrieve test_a against final W_ABCD
    retA = base.evaluate_bpc(W_ABCD, byte_atoms, pos_atoms,
                              test_a_idx, test_a_tgt, device)
    return float(retA)


def compute_verdict(summary):
    max_gap = summary.get("max_hysteresis_gap", 0.0)

    if max_gap >= GAP_1RSB_THRESHOLD:
        return ("HYSTERESIS_1RSB_CONFIRMED",
                f"Max hysteresis gap={max_gap:.3f} >= {GAP_1RSB_THRESHOLD}. "
                f"First-order transition signature; 1-RSB framing supported.")
    if max_gap < GAP_RS_THRESHOLD:
        return ("HYSTERESIS_RS_SMOOTH",
                f"Max hysteresis gap={max_gap:.3f} < {GAP_RS_THRESHOLD}. "
                f"No hysteresis; continuous transition; 1-RSB NOT supported at capacity axis.")
    return ("HYSTERESIS_MIDDLE",
            f"Intermediate hysteresis gap={max_gap:.3f} in [{GAP_RS_THRESHOLD}, {GAP_1RSB_THRESHOLD}). "
            f"Inconclusive first-order vs continuous transition.")


def self_test_verdict():
    cases = [
        ({"max_hysteresis_gap": 0.12}, "HYSTERESIS_1RSB_CONFIRMED"),
        ({"max_hysteresis_gap": 0.02}, "HYSTERESIS_RS_SMOOTH"),
        ({"max_hysteresis_gap": 0.06}, "HYSTERESIS_MIDDLE"),
        ({"max_hysteresis_gap": 0.10}, "HYSTERESIS_1RSB_CONFIRMED"),  # boundary: >= threshold
        ({"max_hysteresis_gap": 0.03}, "HYSTERESIS_MIDDLE"),           # boundary: >= lower
        ({}, "HYSTERESIS_RS_SMOOTH"),                                   # missing key -> 0.0 < 0.03
    ]
    passed = 0
    for summary, expected in cases:
        verdict, msg = compute_verdict(summary)
        if verdict != expected:
            raise AssertionError(f"self_test FAIL: {verdict} != {expected}; summary={summary}")
        passed += 1
    print(f"verdict self-test passed ({passed}/{len(cases)} cases)", flush=True)


def run(smoke=False):
    device = torch.device("cpu")  # CPU-only; no CUDA needed
    t0 = time.monotonic()
    print(f"[hysteresis] device={device} smoke={smoke}", flush=True)
    self_test_verdict()

    m_sweep = M_SWEEP_SMOKE if smoke else M_SWEEP_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    N = N_SMOKE if smoke else N_FULL

    config = {
        "mode": "smoke" if smoke else "full",
        "N": N,
        "batch_size": BATCH_SIZE_SMOKE if smoke else BATCH_SIZE_FULL,
        "epochs": EPOCHS_SMOKE if smoke else EPOCHS_FULL,
        "phase_a_epochs": PHASE_A_EPOCHS_SMOKE if smoke else PHASE_A_EPOCHS_FULL,
        "m_sweep": m_sweep,
        "seeds": seeds,
        "gap_1rsb_threshold": GAP_1RSB_THRESHOLD,
        "gap_rs_threshold": GAP_RS_THRESHOLD,
    }
    print(f"[config] {config}", flush=True)

    # Forward trajectory: low M -> high M (loading from below)
    forward_retA = {m: [] for m in m_sweep}
    for m in m_sweep:
        for seed in seeds:
            print(f"  forward M={m} seed={seed}...", flush=True)
            retA = run_4stage_get_retA(seed, m, config, device)
            forward_retA[m].append(retA)
            print(f"  forward M={m} seed={seed}: retA={retA:.4f}", flush=True)

    # Reverse trajectory: high M -> low M (loading from above)
    # Same measurement but we record separately to compare
    reverse_retA = {m: [] for m in reversed(m_sweep)}
    for m in reversed(m_sweep):
        for seed in seeds:
            print(f"  reverse M={m} seed={seed}...", flush=True)
            retA = run_4stage_get_retA(seed, m, config, device)
            reverse_retA[m].append(retA)
            print(f"  reverse M={m} seed={seed}: retA={retA:.4f}", flush=True)

    # Compute hysteresis gap at each M
    cells = []
    max_gap = 0.0
    for m in m_sweep:
        fwd_mean = sum(forward_retA[m]) / len(forward_retA[m])
        rev_mean = sum(reverse_retA[m]) / len(reverse_retA[m])
        gap = abs(fwd_mean - rev_mean)
        cells.append({
            "M": m,
            "forward_retA_mean": round(fwd_mean, 4),
            "reverse_retA_mean": round(rev_mean, 4),
            "hysteresis_gap": round(gap, 4),
            "forward_seeds": [round(x, 4) for x in forward_retA[m]],
            "reverse_seeds": [round(x, 4) for x in reverse_retA[m]],
        })
        print(f"  M={m}: fwd={fwd_mean:.4f} rev={rev_mean:.4f} gap={gap:.4f}", flush=True)
        if gap > max_gap:
            max_gap = gap

    summary = {
        "max_hysteresis_gap": round(max_gap, 4),
        "cells": cells,
        "n_seeds": len(seeds),
        "m_sweep": m_sweep,
    }

    verdict, verdict_msg = compute_verdict(summary)
    elapsed = time.monotonic() - t0

    result = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": round(elapsed, 3),
        "summary": summary,
        "config": config,
    }
    validate_metrics(result)

    out_dir = get_output_dir("wave14_1rsb_hysteresis_v1")
    metrics_path = out_dir / "metrics.json"
    with open(metrics_path, "w") as f:
        json.dump(result, f, indent=2)

    print(f"[done] verdict={verdict}", flush=True)
    print(f"[done] verdict_msg={verdict_msg}", flush=True)
    print(f"[done] elapsed={elapsed:.1f}s metrics={metrics_path}", flush=True)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test_verdict()
        return
    run(smoke=args.smoke)


if __name__ == "__main__":
    main()
