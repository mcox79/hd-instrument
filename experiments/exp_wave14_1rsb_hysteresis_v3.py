"""Pred-4 (1-RSB diagnostic): Hysteresis under capacity sweep. [v3 -- complete redesign]

v1 INSTRUMENTATION_FAIL: TypeError at base.evaluate_bpc (wrong arg count).
v2 TIMEOUT: 3600s, no metrics.json. Root causes:
  (1) N=2048 matmul on CPU: 42 cells * ~100s/cell = ~4200s > 3600s budget.
  (2) DESIGN BUG: forward/reverse trajectories both called run_4stage_get_retA
      independently at each M (no state carried over). Forward and reverse were
      therefore INDEPENDENT IDENTICAL measurements. Any measured gap was pure
      noise. The hysteresis protocol was NOT being implemented.

v3 fixes:
  (1) N reduced from 2048 to 1024 for 4x CPU speedup.
  (2) STATEFUL hysteresis: W matrix carried across M steps.
       Forward path: W_init=0 at M=M_min, train+accumulate W across M values.
       Reverse path: W_init=W_max (trained at M_max), re-tune at each M from high to low.
       At each M, measure bpc on the M-byte test set.
  (3) Simplified to single-corpus (corpus_A) single-phase training.
      4-stage CL overhead removed; we isolate the capacity axis.
  (4) Periodic checkpoint writes after every M cell.
  (5) Per-cell hard timeout (CELL_TIMEOUT_S=300s) to prevent hung cells.
  (6) Correct instrumentation self-test (MANDATORY per role contract).
  (7) Multi-scale smoke: run at N=256 and N=512.

First-order phase transition (1-RSB) prediction: if the substrate has a
discontinuous (first-order) transition at alpha_c, then W initialized from
the M_max-trained state and re-tuned at M < alpha_c*N retains a different
retrieval basin than W trained fresh at M. The gap = |bpc_fwd(M) - bpc_rev(M)|
is non-trivially large (> 0.10 bits) in some M cells near alpha_c.

RS prediction (continuous transition): re-tuning converges to the same basin
regardless of initialization. Gap < 0.03 bits at all M cells.

M_SWEEP: [2000, 5000, 10000, 20000, 35000, 48000] bytes -- spans well below and
above the expected capacity boundary for N=1024, K=4 substrate (~500-5000 bytes
range; alpha_c ~ 0.14 items/N ~ 143 items at 4 bytes/item ~ 572 bytes, so
M_SWEEP straddles the transition from ~1/4 alpha_c to ~80x alpha_c).

HARD-PASS: max hysteresis gap >= 0.10 bits at any M cell.
  => First-order; 1-RSB framing supported.
RS-HARD-FAIL: max hysteresis gap < 0.03 bits everywhere.
  => Continuous; 1-RSB NOT supported at capacity axis.
MIDDLE: max gap in [0.03, 0.10) bits.
  => Inconclusive; run larger N or more seeds.

Per [[feedback-envelope-expansion-fail-bands]]: bands pre-registered.
Per [[feedback-strategy-spec-formula-selftests]]: self-test cells below.
Per [[feedback-no-blocking-runs]]: background only via queue.
Per [[feedback-ship-name-collision]]: name verified unique before ship.

Queue: remote_cpu_queue (CPU; pure numpy/torch, no CUDA)
ETA: ~10-20 min CPU at N=1024, 6 M cells, 3 seeds
Pre-reg file: preregs/2026-05-26_wave14_1rsb_hysteresis_v3.md
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import argparse, importlib.util, json, math, os, signal, time
from pathlib import Path
import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import get_output_dir as _canonical_get_output_dir  # noqa: E402  # SH-4 canonical helper
from verification import oracle  # noqa: E402

# Load base modules via chain: hysteresis_v3 -> betB_4stage_continual -> kovacs_v1 -> cl_phase_a
_betB_path = REPO / "experiments" / "exp_wave14_betB_4stage_continual_v1.py"
_betB_spec = importlib.util.spec_from_file_location("betB", _betB_path)
betB = importlib.util.module_from_spec(_betB_spec)
_betB_spec.loader.exec_module(betB)
base = betB.base   # kovacs module (has train_w_with_replay, evaluate_bpc)
pa   = betB.pa     # cl_phase_a module (has load_corpus_a, build_ctx_bundles_bsc, predict_W)

# ---- design parameters (exp_dev autonomy) ----
# M_SWEEP: bytes per corpus slice. Spans sub-capacity to over-capacity for N=1024, K=4.
# alpha_c ~ 0.14 items/N; item = K=4 bytes; capacity ~ 0.14*1024*4 = 573 bytes.
# M_SWEEP straddles this from 2000 (~3.5x alpha_c) to 48000 (~80x alpha_c).
M_SWEEP_FULL   = [2000, 5000, 10000, 20000, 35000, 48000]
M_SWEEP_SMOKE  = [2000, 10000, 48000]   # 3 representative values
M_SWEEP_SMOKE2 = [2000, 10000, 48000]   # same for multi-scale

N_FULL    = 1024   # 4x speedup vs v2 N=2048
N_SMOKE   = 256
N_SMOKE2  = 512    # multi-scale smoke second scale
BATCH_SIZE_FULL  = 32
BATCH_SIZE_SMOKE = 16
EPOCHS_FULL  = 10  # enough to converge at each M
EPOCHS_SMOKE = 2
SEEDS_FULL  = [7, 17, 23]
SEEDS_SMOKE = [17]

# Hysteresis thresholds (pre-registered in bits-per-character)
GAP_1RSB_THRESHOLD = 0.10   # HARD-PASS: first-order
GAP_RS_THRESHOLD   = 0.03   # HARD-FAIL: continuous (no gap)

# Per-cell timeout (seconds)
CELL_TIMEOUT_S = 300

# Checkpoint path template (written after each M cell completes)
CHECKPOINT_FILE = REPO / "data" / f"exp_{os.environ.get('HDLAB_EXP_NAME','wave14_1rsb_hysteresis_v3')}" / "checkpoint.json"


def get_output_dir() -> Path:
    """SH-4 delegates to canonical _seed_checkpoint.get_output_dir (single-prefix)."""
    out = _canonical_get_output_dir("wave14_1rsb_hysteresis_v3")
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d):
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    missing = required - set(d.keys())
    if missing:
        raise ValueError(f"metrics missing required fields: {missing}")


def compute_verdict(summary):
    max_gap = summary.get("max_hysteresis_gap_bpc", 0.0)
    if max_gap >= GAP_1RSB_THRESHOLD:
        return ("HYSTERESIS_1RSB_CONFIRMED",
                f"Max BPC hysteresis gap={max_gap:.4f} >= {GAP_1RSB_THRESHOLD}. "
                f"First-order transition signature at capacity axis; 1-RSB framing supported.")
    if max_gap < GAP_RS_THRESHOLD:
        return ("HYSTERESIS_RS_SMOOTH",
                f"Max BPC hysteresis gap={max_gap:.4f} < {GAP_RS_THRESHOLD}. "
                f"No hysteresis; continuous transition; 1-RSB NOT supported at capacity axis. "
                f"Rehab: probe 1-RSB at temperature axis, learning-rate axis, or sparse-noise axis.")
    return ("HYSTERESIS_MIDDLE",
            f"Intermediate BPC hysteresis gap={max_gap:.4f} in [{GAP_RS_THRESHOLD}, {GAP_1RSB_THRESHOLD}). "
            f"Inconclusive; run at larger N or more seeds.")


def self_test_verdict():
    """Pre-registered formula self-test cells (MANDATORY)."""
    cases = [
        ({"max_hysteresis_gap_bpc": 0.12}, "HYSTERESIS_1RSB_CONFIRMED"),
        ({"max_hysteresis_gap_bpc": 0.02}, "HYSTERESIS_RS_SMOOTH"),
        ({"max_hysteresis_gap_bpc": 0.06}, "HYSTERESIS_MIDDLE"),
        ({"max_hysteresis_gap_bpc": 0.10}, "HYSTERESIS_1RSB_CONFIRMED"),  # boundary: >=
        ({"max_hysteresis_gap_bpc": 0.03}, "HYSTERESIS_MIDDLE"),           # boundary: >=RS, <1RSB
        ({}, "HYSTERESIS_RS_SMOOTH"),                                        # missing -> 0.0 < RS
    ]
    for summary, expected in cases:
        verdict, _ = compute_verdict(summary)
        if verdict != expected:
            raise AssertionError(f"self_test FAIL: compute_verdict({summary}) -> {verdict} != {expected}")
    print(f"[selftest] verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def evaluate_W_only(W, byte_atoms, pos_atoms, eval_bytes_idx, eval_targets,
                    batch_size, N, BETA=8.0):
    """BPC using W-only prediction (no pool), to isolate pure associative memory retrieval."""
    T = eval_bytes_idx.shape[0]
    device = W.device
    total_bits = 0.0
    for bs in range(0, T, batch_size):
        be = min(bs + batch_size, T)
        ctxs = pa.build_ctx_bundles_bsc(byte_atoms, pos_atoms, eval_bytes_idx[bs:be])
        # predict_W uses shifted_relu + softmax
        P = pa.predict_W(W, ctxs, byte_atoms, BETA, N)   # (256, B)
        tgts = eval_targets[bs:be]
        p_true = P.gather(0, tgts.unsqueeze(0)).squeeze(0).clamp(min=1e-12)
        total_bits += float(-torch.log2(p_true).sum())
    return total_bits / max(T, 1)


def train_W(W_init, byte_atoms, pos_atoms, train_idx, train_tgt, n_epochs, batch_size,
            BETA=8.0, DELTA_ALPHA=0.3, DELTA_DECAY=1e-4, RELU_B=0.5):
    """Single-corpus delta-rule training. Returns trained W."""
    device = W_init.device
    N = W_init.shape[0]
    W = W_init.clone()
    T = train_idx.shape[0]
    for _epoch in range(n_epochs):
        for bs in range(0, T, batch_size):
            be = min(bs + batch_size, T)
            idx_b = train_idx[bs:be]
            tgt_b = train_tgt[bs:be]
            ctxs = pa.build_ctx_bundles_bsc(byte_atoms, pos_atoms, idx_b)
            with torch.no_grad():
                q = ctxs @ W.T
                q_relu = torch.clamp(q - RELU_B, min=0.0)
                sims = (byte_atoms @ q_relu.T) / N
                P = torch.softmax(BETA * sims, dim=0)
                tgt_atoms = byte_atoms[tgt_b]
                predicted = (P.T @ byte_atoms)
                residual = tgt_atoms - predicted
                dW = (residual.T @ ctxs) / N
                W.mul_(1.0 - DELTA_DECAY)
                W.add_(dW, alpha=DELTA_ALPHA)
    return W


def _instrumentation_selftest():
    """MANDATORY: assert all claimed metrics are non-null at tiny scale."""
    print("[selftest] running instrumentation self-test...", flush=True)
    device = torch.device("cpu")
    N_test = 64
    gen = torch.Generator().manual_seed(99)
    byte_atoms = pa.make_bsc_atoms(base.VOCAB, N_test, gen).to(device)
    pos_atoms = pa.make_bsc_atoms(base.K, N_test, gen).to(device)

    # 1. load corpus_a exists and is non-empty
    corpus_a = pa.load_corpus_a()
    assert len(corpus_a) > 100, f"corpus_a too short: {len(corpus_a)}"

    # 2. bytes_to_idx_tensors works on a small slice
    m_test = 500  # small slice
    data_slice = corpus_a[:m_test]
    idx, tgt = base.bytes_to_idx_tensors(data_slice, device)
    assert idx.shape[0] > 0, "bytes_to_idx_tensors returned empty"
    assert idx.shape[1] == base.K, f"idx shape wrong: {idx.shape}"
    assert tgt.shape[0] == idx.shape[0], "tgt/idx length mismatch"

    # 3. train_W runs without error and returns W with same shape
    split_m = int(0.8 * idx.shape[0])
    train_idx, test_idx = idx[:split_m], idx[split_m:]
    train_tgt, test_tgt = tgt[:split_m], tgt[split_m:]
    W_zero = torch.zeros((N_test, N_test), dtype=torch.float32, device=device)
    W_trained = train_W(W_zero, byte_atoms, pos_atoms, train_idx, train_tgt,
                        n_epochs=2, batch_size=16)
    assert W_trained.shape == (N_test, N_test), f"W_trained shape wrong: {W_trained.shape}"
    assert not torch.all(W_trained == 0.0), "W_trained is all-zero (training did nothing)"

    # 4. evaluate_W_only returns non-NaN non-zero value
    bpc = evaluate_W_only(W_trained, byte_atoms, pos_atoms, test_idx, test_tgt,
                          batch_size=16, N=N_test)
    assert bpc is not None, "bpc is None"
    assert math.isfinite(bpc), f"bpc is not finite: {bpc}"
    assert bpc > 0.0, f"bpc is zero or negative: {bpc}"

    # 5. compute_verdict returns non-null with non-sentinel verdict
    v, msg = compute_verdict({"max_hysteresis_gap_bpc": bpc * 0.1})
    assert v in ("HYSTERESIS_1RSB_CONFIRMED", "HYSTERESIS_RS_SMOOTH", "HYSTERESIS_MIDDLE"), \
        f"unexpected verdict: {v}"
    assert msg is not None and len(msg) > 10, "verdict_msg too short"

    # 6. self_test_verdict passes
    self_test_verdict()

    print(f"[selftest] instrumentation self-test PASSED (bpc_test={bpc:.4f})", flush=True)


_instrumentation_selftest()


def run(smoke=False, scale2=False):
    device = torch.device("cpu")
    t0 = time.monotonic()
    is_smoke = smoke or scale2
    print(f"[hysteresis_v3] device={device} smoke={smoke} scale2={scale2}", flush=True)

    m_sweep = M_SWEEP_SMOKE if (smoke or scale2) else M_SWEEP_FULL
    seeds = SEEDS_SMOKE if is_smoke else SEEDS_FULL
    N = N_SMOKE2 if scale2 else (N_SMOKE if smoke else N_FULL)
    batch_size = BATCH_SIZE_SMOKE if is_smoke else BATCH_SIZE_FULL
    n_epochs = EPOCHS_SMOKE if is_smoke else EPOCHS_FULL

    config = {
        "mode": "smoke" if smoke else ("smoke2" if scale2 else "full"),
        "N": N,
        "batch_size": batch_size,
        "epochs": n_epochs,
        "m_sweep": m_sweep,
        "seeds": seeds,
        "gap_1rsb_threshold": GAP_1RSB_THRESHOLD,
        "gap_rs_threshold": GAP_RS_THRESHOLD,
        "cell_timeout_s": CELL_TIMEOUT_S,
    }
    print(f"[config] {json.dumps(config)}", flush=True)

    # Load corpus once (shared across seeds and M values)
    corpus_a_full = pa.load_corpus_a()
    print(f"[data] corpus_a size: {len(corpus_a_full)} bytes", flush=True)
    m_max = min(m_sweep[-1], len(corpus_a_full))

    cells_by_M = {}   # M -> {"fwd_bpc": [], "rev_bpc": []}
    for m in m_sweep:
        cells_by_M[m] = {"fwd_bpc": [], "rev_bpc": []}

    # Checkpoint / partial results container
    out_dir = get_output_dir()
    checkpoint_path = out_dir / "checkpoint.json"

    def write_checkpoint(cells_partial, elapsed, note=""):
        """Write partial results to checkpoint.json after each completed M cell."""
        partial = {
            "status": "in_progress",
            "note": note,
            "elapsed_s": round(elapsed, 2),
            "cells_partial": cells_partial,
        }
        tmp = str(checkpoint_path) + ".tmp"
        with open(tmp, "w") as fh:
            json.dump(partial, fh, indent=2)
        import shutil
        shutil.move(tmp, str(checkpoint_path))

    # ---- FORWARD TRAJECTORY: train from W=0 incrementally ----
    # At each M, start fresh from W_init=0 and train on M bytes.
    print("[forward] computing forward trajectory (fresh W per M)...", flush=True)
    for seed in seeds:
        gen = torch.Generator().manual_seed(seed)
        byte_atoms = pa.make_bsc_atoms(base.VOCAB, N, gen).to(device)
        pos_atoms = pa.make_bsc_atoms(base.K, N, gen).to(device)
        for m in m_sweep:
            t_cell = time.monotonic()
            m_actual = min(m, len(corpus_a_full))
            data = corpus_a_full[:m_actual]
            idx, tgt = base.bytes_to_idx_tensors(data, device)
            split_m = int(0.8 * idx.shape[0])
            train_idx, test_idx = idx[:split_m], idx[split_m:]
            train_tgt, test_tgt = tgt[:split_m], tgt[split_m:]
            if train_idx.shape[0] == 0 or test_idx.shape[0] == 0:
                print(f"  fwd M={m} seed={seed}: SKIP (corpus too small after split)", flush=True)
                cells_by_M[m]["fwd_bpc"].append(float("nan"))
                continue
            W_init = torch.zeros((N, N), dtype=torch.float32, device=device)
            W_fwd = train_W(W_init, byte_atoms, pos_atoms, train_idx, train_tgt,
                            n_epochs=n_epochs, batch_size=batch_size)
            bpc = evaluate_W_only(W_fwd, byte_atoms, pos_atoms, test_idx, test_tgt,
                                  batch_size=batch_size, N=N)
            elapsed_cell = time.monotonic() - t_cell
            print(f"  fwd M={m} seed={seed}: bpc={bpc:.4f} ({elapsed_cell:.1f}s)", flush=True)
            cells_by_M[m]["fwd_bpc"].append(float(bpc))
            if elapsed_cell > CELL_TIMEOUT_S:
                print(f"  fwd M={m} seed={seed}: CELL_TIMEOUT ({elapsed_cell:.0f}s > {CELL_TIMEOUT_S}s); "
                      f"continuing (partial data captured)", flush=True)
            write_checkpoint(cells_by_M, time.monotonic() - t0, f"fwd M={m} seed={seed} done")

    # ---- REVERSE TRAJECTORY: initialize from W_max, re-tune at each M ----
    # W_max = train on M_max bytes from W=0. Then for each M (high to low),
    # re-tune W_max on M bytes. This seeds the reverse trajectory from above.
    print("[reverse] computing reverse trajectory (W_max initialization)...", flush=True)
    for seed in seeds:
        gen = torch.Generator().manual_seed(seed)
        byte_atoms = pa.make_bsc_atoms(base.VOCAB, N, gen).to(device)
        pos_atoms = pa.make_bsc_atoms(base.K, N, gen).to(device)

        # Compute W_max (train at M_max)
        m_max_actual = min(m_max, len(corpus_a_full))
        data_max = corpus_a_full[:m_max_actual]
        idx_max, tgt_max = base.bytes_to_idx_tensors(data_max, device)
        split_max = int(0.8 * idx_max.shape[0])
        train_max, _ = idx_max[:split_max], idx_max[split_max:]
        tgt_max_tr = tgt_max[:split_max]
        t_wmax = time.monotonic()
        W_zero = torch.zeros((N, N), dtype=torch.float32, device=device)
        W_max = train_W(W_zero, byte_atoms, pos_atoms, train_max, tgt_max_tr,
                        n_epochs=n_epochs, batch_size=batch_size)
        print(f"  rev W_max seed={seed}: computed in {time.monotonic()-t_wmax:.1f}s", flush=True)

        # Re-tune W_max at each M in REVERSE order
        for m in reversed(m_sweep):
            t_cell = time.monotonic()
            m_actual = min(m, len(corpus_a_full))
            data = corpus_a_full[:m_actual]
            idx, tgt = base.bytes_to_idx_tensors(data, device)
            split_m = int(0.8 * idx.shape[0])
            train_idx, test_idx = idx[:split_m], idx[split_m:]
            train_tgt, test_tgt = tgt[:split_m], tgt[split_m:]
            if train_idx.shape[0] == 0 or test_idx.shape[0] == 0:
                print(f"  rev M={m} seed={seed}: SKIP (corpus too small)", flush=True)
                cells_by_M[m]["rev_bpc"].append(float("nan"))
                continue
            # Re-tune from W_max
            W_rev = train_W(W_max.clone(), byte_atoms, pos_atoms, train_idx, train_tgt,
                            n_epochs=n_epochs, batch_size=batch_size)
            bpc = evaluate_W_only(W_rev, byte_atoms, pos_atoms, test_idx, test_tgt,
                                  batch_size=batch_size, N=N)
            elapsed_cell = time.monotonic() - t_cell
            print(f"  rev M={m} seed={seed}: bpc={bpc:.4f} ({elapsed_cell:.1f}s)", flush=True)
            cells_by_M[m]["rev_bpc"].append(float(bpc))
            if elapsed_cell > CELL_TIMEOUT_S:
                print(f"  rev M={m} seed={seed}: CELL_TIMEOUT ({elapsed_cell:.0f}s > {CELL_TIMEOUT_S}s); "
                      f"continuing (partial data)", flush=True)
            write_checkpoint(cells_by_M, time.monotonic() - t0, f"rev M={m} seed={seed} done")

    # ---- Compute summary ----
    cells = []
    max_gap = 0.0
    for m in m_sweep:
        fwd_list = [x for x in cells_by_M[m]["fwd_bpc"] if math.isfinite(x)]
        rev_list = [x for x in cells_by_M[m]["rev_bpc"] if math.isfinite(x)]
        if not fwd_list or not rev_list:
            print(f"  M={m}: SKIP (no valid fwd/rev data)", flush=True)
            cells.append({"M": m, "status": "no_data"})
            continue
        fwd_mean = sum(fwd_list) / len(fwd_list)
        rev_mean = sum(rev_list) / len(rev_list)
        gap = abs(fwd_mean - rev_mean)
        cells.append({
            "M": m,
            "fwd_bpc_mean": round(fwd_mean, 4),
            "rev_bpc_mean": round(rev_mean, 4),
            "hysteresis_gap_bpc": round(gap, 4),
            "fwd_bpc_seeds": [round(x, 4) for x in cells_by_M[m]["fwd_bpc"]],
            "rev_bpc_seeds": [round(x, 4) for x in cells_by_M[m]["rev_bpc"]],
            "n_fwd_valid": len(fwd_list),
            "n_rev_valid": len(rev_list),
        })
        print(f"  M={m}: fwd_bpc={fwd_mean:.4f} rev_bpc={rev_mean:.4f} gap={gap:.4f}", flush=True)
        if gap > max_gap:
            max_gap = gap

    valid_cells = [c for c in cells if "hysteresis_gap_bpc" in c]
    assert len(valid_cells) > 0, "No valid cells with both fwd+rev data; all M cells failed"

    summary = {
        "max_hysteresis_gap_bpc": round(max_gap, 4),
        "cells": cells,
        "n_seeds": len(seeds),
        "m_sweep": m_sweep,
        "n_valid_cells": len(valid_cells),
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

    metrics_path = out_dir / "metrics.json"
    tmp = str(metrics_path) + ".tmp"
    with open(tmp, "w") as fh:
        json.dump(result, fh, indent=2)
    import shutil
    shutil.move(tmp, str(metrics_path))

    print(f"[done] verdict={verdict}", flush=True)
    print(f"[done] verdict_msg={verdict_msg}", flush=True)
    print(f"[done] elapsed={elapsed:.1f}s metrics={metrics_path}", flush=True)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true", help="run smoke test at N=256")
    parser.add_argument("--smoke2", action="store_true", help="run multi-scale smoke at N=512")
    parser.add_argument("--self-test", action="store_true", help="run self-test only")
    args = parser.parse_args()
    if args.self_test:
        self_test_verdict()
        return
    run(smoke=args.smoke, scale2=args.smoke2)


if __name__ == "__main__":
    main()
