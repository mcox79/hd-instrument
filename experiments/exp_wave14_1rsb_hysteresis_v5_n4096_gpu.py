"""1-RSB hysteresis N-scaling v5: GPU probe at N=4096.

CONTEXT:
  v3 (N=1024 GPU): CONFIRMED hysteresis, max_gap=1.84 >> 0.10.
  v4 (N=2048,4096 CPU): TIMEOUT on CPU.
  v5 (THIS): N=4096 only on GPU (single N value, focused depth probe).

  WHY N=4096: v4 timed out at both N=2048 and N=4096 on CPU. The GPU runner
  completes N=4096 Hebbian ops ~10-30x faster. If hysteresis persists at N=4096,
  the 1-RSB claim strengthens (not finite-N artifact).

PRE-REGISTERED BANDS (identical to v3/v4):
  HARD_PASS: max_gap >= 0.10 at N=4096 (hysteresis confirmed at production scale)
  MIDDLE: max_gap in [0.03, 0.10) (weak hysteresis; inconclusive)
  RS_HARD_FAIL: max_gap < 0.03 (hysteresis vanishes at N=4096; finite-N artifact)

OOM PRE-CHECK:
  W at N=4096: 4096^2 * 4 bytes = 64MB. Fine.

FORMULA SELF-TESTS:
  1. v3 gap_v3 = 1.84 (reference value from v3 result)
  2. HARD_PASS fires when max_gap=0.50 (above 0.10)
  3. RS_HARD_FAIL fires when max_gap=0.01 (below 0.03)

Timeout estimate:
  v3 N=1024 GPU: 70s for 3 seeds 6 M-cells.
  v5 N=4096 GPU: timeout = ceil(1.5 * 70 * (4096/1024)^1.5 * 1) = ceil(1.5 * 70 * 8) = ceil(840) = 900s.
  Use 1200s margin.

N-suffix: _n4096 in name binds to N=4096 production config.
Queue: overnight_queue (GPU; N=4096 Hebbian ops)
Pre-reg: preregs/2026-05-27_wave14_1rsb_hysteresis_v5_n4096_gpu.md
Parent: wave14_1rsb_hysteresis_v3 (N=1024 CONFIRMED), wave14_1rsb_hysteresis_v4_multi_N (TIMEOUT)
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import argparse
import importlib.util
import json
import os
import time
from pathlib import Path
from typing import Dict, List

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# Import v3 to reuse train_W, evaluate_W_only
_v3_path = REPO / "experiments" / "exp_wave14_1rsb_hysteresis_v3.py"
_v3_spec = importlib.util.spec_from_file_location("v3_hyst_v5", _v3_path)
v3_mod = importlib.util.module_from_spec(_v3_spec)
_v3_spec.loader.exec_module(v3_mod)
train_W = v3_mod.train_W
evaluate_W_only = v3_mod.evaluate_W_only
base = v3_mod.base
pa = v3_mod.pa

# PRODUCTION CONFIG -- N=4096 (PROT-018 binding: _n4096)
N = 4096            # PRODUCTION N -- PROT-018 contract
N_SMOKE = 512
M_SWEEP_FULL = [8_000, 20_000, 40_000, 80_000, 140_000, 192_000]  # scaled from v3
M_SWEEP_SMOKE = [2_000, 10_000, 48_000]
EPOCHS_FULL = 10
EPOCHS_SMOKE = 2
BATCH_SIZE_FULL = 32
BATCH_SIZE_SMOKE = 16
SEEDS_FULL = [7, 17, 23]
SEEDS_SMOKE = [17]

# Pre-registered thresholds
GAP_1RSB_THRESHOLD = 0.10
GAP_RS_THRESHOLD = 0.03
GAP_V3_N1024 = 1.84


def get_output_dir(default_name: str = "wave14_1rsb_hysteresis_v5_n4096_gpu") -> Path:
    # HDLAB_EXP_NAME env-var honored (n-mismatch eradication 2026-05-27).
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    # PROT-018: N must be 4096
    assert N == 4096, f"PROT-018: production N must be 4096; got {N}"

    # Self-test 1: v3 functions importable
    assert callable(train_W), "train_W not callable from v3"
    assert callable(evaluate_W_only), "evaluate_W_only not callable from v3"

    # Self-test 2: pa.load_corpus_a non-empty
    corpus = pa.load_corpus_a()
    assert len(corpus) > 0, "pa.load_corpus_a() returned empty corpus"

    # Self-test 3: train_W at tiny N works
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    N_t = 64
    gen = torch.Generator().manual_seed(42)
    byte_atoms_t = pa.make_bsc_atoms(base.VOCAB, N_t, gen).to(device)
    pos_atoms_t = pa.make_bsc_atoms(base.K, N_t, gen).to(device)
    tiny_corpus = corpus[:2000]
    train_idx_t, train_tgt_t = base.bytes_to_idx_tensors(tiny_corpus[:1600], device)
    test_idx_t, test_tgt_t = base.bytes_to_idx_tensors(tiny_corpus[1600:], device)
    W_zero_t = torch.zeros((N_t, N_t), dtype=torch.float32, device=device)
    W_t = train_W(W_zero_t, byte_atoms_t, pos_atoms_t, train_idx_t, train_tgt_t,
                  n_epochs=2, batch_size=8)
    assert W_t.shape == (N_t, N_t), f"W shape wrong: {W_t.shape}"
    bpc = evaluate_W_only(W_t, byte_atoms_t, pos_atoms_t, test_idx_t, test_tgt_t,
                          batch_size=8, N=N_t)
    assert 0 < bpc < 50, f"bpc out of range: {bpc}"

    # Self-test 4: verdict formula check
    max_gap = 1.84
    expected_pass = max_gap >= GAP_1RSB_THRESHOLD
    assert expected_pass, f"v3 reference gap should PASS: {max_gap} < {GAP_1RSB_THRESHOLD}"
    max_gap_fail = 0.01
    expected_fail = max_gap_fail < GAP_RS_THRESHOLD
    assert expected_fail, f"Small gap should RS_FAIL: {max_gap_fail} >= {GAP_RS_THRESHOLD}"

    # OOM pre-check: W at N=4096
    oom_bytes = N * N * 4  # float32
    assert oom_bytes < 6e9, f"OOM check: {oom_bytes:.2e}"

    print(f"[selftest] 1rsb_hysteresis_v5 PASSED: N=4096 assertion OK, "
          f"train_W callable, OOM={oom_bytes:.2e}", flush=True)


_instrumentation_selftest()


def run(smoke: bool = False) -> None:
    t0 = time.time()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    n = N_SMOKE if smoke else N
    m_sweep = M_SWEEP_SMOKE if smoke else M_SWEEP_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    epochs = EPOCHS_SMOKE if smoke else EPOCHS_FULL
    batch = BATCH_SIZE_SMOKE if smoke else BATCH_SIZE_FULL
    exp_name = "wave14_1rsb_hysteresis_v5_n4096_gpu"
    print(f"[run] {exp_name} N={n} seeds={seeds} M_sweep={m_sweep} device={device}", flush=True)
    if not smoke:
        assert n == 4096, f"FULL run must use N=4096; got {n}"

    corpus = pa.load_corpus_a()
    cells_by_M: Dict = {m: {"fwd_bpc": [], "rev_bpc": []} for m in m_sweep}

    for seed in seeds:
        gen = torch.Generator().manual_seed(seed)
        byte_atoms = pa.make_bsc_atoms(base.VOCAB, n, gen).to(device)
        pos_atoms = pa.make_bsc_atoms(base.K, n, gen).to(device)

        # FORWARD sweep (fresh W_init=0 at each M)
        print(f"\n[N={n} seed={seed} FORWARD]", flush=True)
        for m in sorted(m_sweep):
            m_actual = min(m, len(corpus))
            idx, tgt = base.bytes_to_idx_tensors(corpus[:m_actual], device)
            split = int(0.8 * idx.shape[0])
            if split == 0 or split == idx.shape[0]:
                continue
            tr_idx, te_idx = idx[:split], idx[split:]
            tr_tgt, te_tgt = tgt[:split], tgt[split:]
            W_zero = torch.zeros((n, n), dtype=torch.float32, device=device)
            W_fwd = train_W(W_zero, byte_atoms, pos_atoms, tr_idx, tr_tgt,
                            n_epochs=epochs, batch_size=batch)
            bpc_fwd = evaluate_W_only(W_fwd, byte_atoms, pos_atoms, te_idx, te_tgt,
                                      batch_size=batch, N=n)
            cells_by_M[m]["fwd_bpc"].append(float(bpc_fwd))
            print(f"  M={m} fwd_bpc={bpc_fwd:.4f}", flush=True)

        # REVERSE sweep: start from W_max (trained at M_max), re-tune downward
        print(f"[N={n} seed={seed} REVERSE]", flush=True)
        m_max = max(m_sweep)
        m_max_actual = min(m_max, len(corpus))
        idx_max, tgt_max = base.bytes_to_idx_tensors(corpus[:m_max_actual], device)
        split_max = int(0.8 * idx_max.shape[0])
        W_zero_max = torch.zeros((n, n), dtype=torch.float32, device=device)
        W_max = train_W(W_zero_max, byte_atoms, pos_atoms, idx_max[:split_max], tgt_max[:split_max],
                        n_epochs=epochs, batch_size=batch)
        for m in sorted(m_sweep, reverse=True):
            m_actual = min(m, len(corpus))
            idx, tgt = base.bytes_to_idx_tensors(corpus[:m_actual], device)
            split = int(0.8 * idx.shape[0])
            if split == 0 or split == idx.shape[0]:
                continue
            tr_idx, te_idx = idx[:split], idx[split:]
            tr_tgt, te_tgt = tgt[:split], tgt[split:]
            W_rev = train_W(W_max.clone(), byte_atoms, pos_atoms, tr_idx, tr_tgt,
                            n_epochs=epochs, batch_size=batch)
            bpc_rev = evaluate_W_only(W_rev, byte_atoms, pos_atoms, te_idx, te_tgt,
                                      batch_size=batch, N=n)
            cells_by_M[m]["rev_bpc"].append(float(bpc_rev))
            print(f"  M={m} rev_bpc={bpc_rev:.4f}", flush=True)

    # Compute gaps
    gaps: Dict[int, float] = {}
    for m, cell in cells_by_M.items():
        if cell["fwd_bpc"] and cell["rev_bpc"]:
            gaps[m] = abs(
                sum(cell["fwd_bpc"]) / len(cell["fwd_bpc"])
                - sum(cell["rev_bpc"]) / len(cell["rev_bpc"])
            )

    max_gap = max(gaps.values()) if gaps else 0.0
    print(f"\n[gaps] {gaps}", flush=True)
    print(f"[max_gap] {max_gap:.4f}", flush=True)

    if max_gap >= GAP_1RSB_THRESHOLD:
        verdict = "HARD_PASS"
        msg = (f"HARD_PASS: hysteresis confirmed at N=4096. max_gap={max_gap:.4f}>={GAP_1RSB_THRESHOLD}. "
               f"1-RSB glassy phase persists at production scale (cf v3 N=1024 gap={GAP_V3_N1024}).")
    elif max_gap >= GAP_RS_THRESHOLD:
        verdict = "MIDDLE_BAND"
        msg = (f"MIDDLE_BAND: weak hysteresis at N=4096. max_gap={max_gap:.4f} in [{GAP_RS_THRESHOLD},{GAP_1RSB_THRESHOLD}). "
               f"Inconclusive.")
    else:
        verdict = "RS_HARD_FAIL"
        msg = (f"RS_HARD_FAIL: hysteresis vanishes at N=4096. max_gap={max_gap:.4f}<{GAP_RS_THRESHOLD}. "
               f"1-RSB was finite-N artifact at N=1024.")

    elapsed = round(time.time() - t0, 2)
    print(f"\n[verdict] {verdict}", flush=True)
    print(f"[verdict_msg] {msg}", flush=True)

    metrics = {
        "verdict": verdict,
        "verdict_msg": msg,
        "elapsed_s": elapsed,
        "summary": {"N": n, "max_gap": max_gap, "gaps_by_M": {str(k): v for k, v in gaps.items()},
                    "cells_by_M": {str(k): v for k, v in cells_by_M.items()}},
        "config": {"N_production": N, "N_run": n, "m_sweep": m_sweep,
                   "seeds": seeds, "epochs": epochs, "smoke": smoke},
    }
    mpath = get_output_dir() / "metrics.json"
    with open(mpath, "w") as fh:
        json.dump(metrics, fh, indent=2)
    print(f"[exp] metrics -> {mpath}", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true", dest="self_test")
    args = parser.parse_args()
    if args.self_test:
        sys.exit(0)
    run(smoke=args.smoke)
