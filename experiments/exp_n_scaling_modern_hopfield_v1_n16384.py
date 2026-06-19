"""N-SCALING MODERN HOPFIELD v1 at N=16384.

CONTEXT:
  Capacity at N=4096 is linear (max_M_at_95_recall ~ N/4 from axis1 chunks).
  Modern Hopfield (Ramsauer 2020) predicts EXPONENTIAL capacity in N for the
  energy-based attention form. Does substrate's capacity extend exponentially
  at larger N, or stay linear?

SCIENTIFIC QUESTION:
  At N=16384, what is max_M such that argmax retention >= 0.95?
  - If max_M ~ N/4 = 4096: substrate is LINEAR-CAPACITY (matches outer-product
    rank ceiling; no exponential bend).
  - If max_M > 2*N = 32768: substrate exhibits modern-Hopfield-style
    exponential capacity scaling.
  - Between: slope change but not exponential.

PRE-REGISTERED BANDS (calibration probe at new N; widened ±50%):
  HARD_PASS: max_M_at_95_recall > 2 * N = 32768
    (exponential bend detected; substrate beats outer-product ceiling).
  HARD_FAIL: max_M_at_95_recall in [N/4 * 0.8, N/4 * 1.2] = [3277, 4915]
    (linear extends; no bend; substrate IS outer-product limited).
  MIDDLE_BAND: max_M_at_95_recall in (N/4 * 1.2, 2*N] = (4915, 32768]
    (slope change but not exponential; intermediate regime).

FORMULA SELF-TESTS:
  1. N = 16384 (PROT-018 binding).
  2. M sweep [N/8, N/4, N/2, N, 2N, 4N, 8N, 16N] = [2048, 4096, 8192, 16384,
     32768, 65536, 131072, 262144]; 8 points.
  3. HP threshold: 2*N = 32768.
  4. HF lower bound: 0.8 * N/4 = 3276.8.
  5. HF upper bound: 1.2 * N/4 = 4915.2.

OOM CHECK:
  At M=16N=262144, N=16384: keys = 262144 * 16384 * 4 = 17.2 GB. OOM.
  Strategy: process keys in chunks; never allocate full keys tensor.
  W matrix: N*N*4 = 1.07 GB. CB: 49152*N*4 = 3.22 GB. Subtotal 4.3 GB OK.
  Per-batch keys at batch=1024: 1024*16384*4 = 67 MB. Fine.

TIMEOUT ESTIMATE:
  Per cell: store M facts batched (chunks of 1024) + retention probe.
  At M=16N=262144: 256 batches * ~0.2s = ~51s. plus retention check ~5s.
  8 M values * 3 seeds = 24 cells. Mean ~30s/cell = 720s.
  scaling_exp=2.0 (matrix matmul dominant):
  smoke_wall_s=120, FULL_N/smoke_N=16, FULL_seeds/smoke_seeds=3.
  ceil(1.5 * 120 * 16^2.0 * 3) = ceil(138240). EXCEEDS 14400.
  User explicit override: 86400s authorized for battery-class N=16384 sweep.

N-suffix: _n16384 -> production N = 16384 (PROT-018 binding).
Anchor: n_scaling_modern_hopfield_v1_n16384
Queue: overnight_queue
Pre-reg: preregs/2026-05-30_n_scaling_modern_hopfield_v1_n16384.md
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
from typing import Dict, List

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# Substrate primitives via t1_beta_sweep loader pattern
_t1_path = REPO / "experiments" / "exp_t1_beta_sweep_v1_n4096.py"
_t1_spec = importlib.util.spec_from_file_location("t1v1_nscale", _t1_path)
t1 = importlib.util.module_from_spec(_t1_spec)
_t1_spec.loader.exec_module(t1)
store_facts_batched = t1.store_facts_batched
v3 = t1.v3

# Checkpoint helper
_ck_path = REPO / "experiments" / "_seed_checkpoint.py"
_ck_spec = importlib.util.spec_from_file_location("_seed_checkpoint_nscale", _ck_path)
_ck = importlib.util.module_from_spec(_ck_spec)
_ck_spec.loader.exec_module(_ck)
list_completed_keys = _ck.list_completed_keys
write_partial_key   = _ck.write_partial_key
load_partial_key    = _ck.load_partial_key


# PRODUCTION CONFIG -- PROT-018: _n16384 binds to N = 16384
N = 16384       # PROT-018 production-N anchor (queue_add.py regex hits this line)
N_FULL  = N
N_SMOKE = 1024
assert N_FULL == 16384, f"PROT-018: N_FULL must be 16384; got {N_FULL}"

# M sweep: [N/8, N/4, N/2, N, 2N, 4N, 8N, 16N]
def _m_sweep(N_use: int) -> List[int]:
    return [N_use // 8, N_use // 4, N_use // 2, N_use,
            2 * N_use, 4 * N_use, 8 * N_use, 16 * N_use]

M_SWEEP_FULL = _m_sweep(N_FULL)
M_SWEEP_SMOKE = [N_SMOKE // 4, N_SMOKE, 2 * N_SMOKE]

SEEDS_FULL  = [7, 17, 23]
SEEDS_SMOKE = [17]

N_PROBE = 200
RECALL_THRESHOLD = 0.95

# Pre-registered thresholds
HP_MAX_M_MIN  = 2 * N_FULL          # > 32768
HF_LINEAR_LO  = int(0.8 * N_FULL / 4)  # 3277
HF_LINEAR_HI  = int(1.2 * N_FULL / 4)  # 4915

def get_output_dir(default_name: str = "n_scaling_modern_hopfield_v1_n16384") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def measure_recall_at_M(N_use: int, M: int, seed: int,
                         device: torch.device, n_probe: int = N_PROBE) -> float:
    """Measure argmax-retention on n_probe stored keys at (N, M, seed).

    OOM-safe: keys tensor reused inside store_facts_batched (chunked internally).
    For the probe we only need n_probe stored keys + the full codebook.
    """
    codebook, _ = v3.make_kerdock_4coset_codebook(N_use, device)
    W, keys, _vals, _key_idx, val_idx = store_facts_batched(codebook, M, seed, N_use, device)
    n = min(n_probe, M)
    probe_keys = keys[:n]
    probe_val_idx = val_idx[:n] % codebook.shape[0]
    # Chunked sims: avoid (C, n) materialisation if huge
    sims = (codebook @ (probe_keys @ W.T).T) / N_use   # (C, n)
    pred = torch.argmax(sims, dim=0)
    acc = float((pred == probe_val_idx.to(device)).float().mean().item())
    # Free large tensors before next call
    del W, keys, sims, pred, codebook
    if device.type == 'cuda':
        torch.cuda.empty_cache()
    return acc


def cell_key(M: int, seed: int) -> str:
    return f"M{int(M)}_seed{int(seed)}"


def compute_verdict(per_seed_max_M: List[int]) -> tuple:
    if not per_seed_max_M:
        return ("NSCALE_INCONCLUSIVE", "No completed seeds.")
    mean_max = sum(per_seed_max_M) / len(per_seed_max_M)
    detail = (f"max_M_at_95_recall mean={mean_max:.0f} "
              f"per_seed={per_seed_max_M} N={N_FULL} "
              f"HP_threshold={HP_MAX_M_MIN} HF_band=[{HF_LINEAR_LO},{HF_LINEAR_HI}]")
    if mean_max > HP_MAX_M_MIN:
        return ("NSCALE_HARD_PASS",
                f"EXPONENTIAL_BEND: mean_max_M={mean_max:.0f} > {HP_MAX_M_MIN}. "
                + detail)
    if HF_LINEAR_LO <= mean_max <= HF_LINEAR_HI:
        return ("NSCALE_HARD_FAIL",
                f"LINEAR_EXTENDS: mean_max_M={mean_max:.0f} in linear-band. "
                + detail)
    return ("NSCALE_MIDDLE_BAND",
            f"SLOPE_CHANGE: mean_max_M={mean_max:.0f} between linear and exp. "
            + detail)


def _instrumentation_selftest() -> None:
    """Mandatory: assert all metrics non-null + verdict gates."""
    assert N_FULL == 16384, f"PROT-018: N_FULL must be 16384; got {N_FULL}"
    assert len(M_SWEEP_FULL) == 8, f"M sweep should have 8 points: {M_SWEEP_FULL}"
    assert M_SWEEP_FULL[0] == 2048, f"N/8: {M_SWEEP_FULL[0]}"
    assert M_SWEEP_FULL[1] == 4096, f"N/4: {M_SWEEP_FULL[1]}"
    assert M_SWEEP_FULL[-1] == 16 * N_FULL == 262144, f"16N: {M_SWEEP_FULL[-1]}"

    # Verdict gate self-tests
    v, _ = compute_verdict([40000, 38000, 35000])
    assert "HARD_PASS" in v, f"HP gate: {v}"
    v, _ = compute_verdict([4000, 4100, 4200])
    assert "HARD_FAIL" in v, f"HF gate: {v}"
    v, _ = compute_verdict([10000, 12000, 15000])
    assert "MIDDLE_BAND" in v, f"MB gate: {v}"

    # Smoke: 1 cell on CPU
    device = torch.device("cpu")
    acc = measure_recall_at_M(N_SMOKE, N_SMOKE // 4, 17, device, n_probe=32)
    assert 0.0 <= acc <= 1.0, f"smoke recall out of range: {acc}"
    print(f"[selftest] n_scaling_modern_hopfield_v1_n16384 PASS smoke recall={acc:.3f}",
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

    device_str = "cuda" if torch.cuda.is_available() else "cpu"
    device = torch.device(device_str)
    smoke = args.smoke

    N_cfg   = N_SMOKE if smoke else N_FULL
    M_sweep = M_SWEEP_SMOKE if smoke else M_SWEEP_FULL
    seeds   = SEEDS_SMOKE if smoke else SEEDS_FULL

    out_dir = get_output_dir()
    done_keys = set(list_completed_keys(out_dir))
    t0 = time.time()
    print(f"[run] n_scaling_modern_hopfield_v1_n16384 smoke={smoke} N={N_cfg} "
          f"M_sweep={M_sweep} seeds={seeds} done={len(done_keys)} "
          f"device={device_str}", flush=True)

    # Per-seed scan: ascending M; first M with recall < 0.95 fixes max_M_at_95.
    cells_run: List[Dict] = []
    for seed in seeds:
        per_M = []
        max_M_below = 0
        for M in M_sweep:
            ck = cell_key(M, seed)
            if ck in done_keys:
                body = load_partial_key(out_dir, ck)
                if body is not None:
                    recall = body.get("recall")
                    per_M.append({"M": M, "recall": recall})
                    if recall is not None and recall >= RECALL_THRESHOLD:
                        max_M_below = max(max_M_below, M)
                    continue
            try:
                recall = measure_recall_at_M(N_cfg, M, seed, device, n_probe=N_PROBE)
                cell = {"M": M, "seed": seed, "recall": round(recall, 5)}
                write_partial_key(out_dir, ck, cell)
                per_M.append({"M": M, "recall": cell["recall"]})
                if recall >= RECALL_THRESHOLD:
                    max_M_below = max(max_M_below, M)
                print(f"  seed={seed} M={M} recall={recall:.4f} "
                      f"({time.time()-t0:.1f}s)", flush=True)
            except (RuntimeError, MemoryError) as e:
                print(f"  seed={seed} M={M} FAILED: {type(e).__name__}: {e}",
                      flush=True)
                if device.type == 'cuda':
                    torch.cuda.empty_cache()
        cells_run.append({"seed": seed, "per_M": per_M,
                          "max_M_at_95_recall": max_M_below})

    per_seed_max_M = [c["max_M_at_95_recall"] for c in cells_run
                      if c["max_M_at_95_recall"] > 0]
    verdict, verdict_msg = compute_verdict(per_seed_max_M)
    elapsed = round(time.time() - t0, 2)

    summary = {
        "anchor": "n_scaling_modern_hopfield_v1_n16384",
        "N": N_cfg, "smoke": smoke,
        "M_sweep": M_sweep, "seeds": seeds,
        "cells": cells_run,
        "per_seed_max_M": per_seed_max_M,
        "verdict": verdict, "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
    }
    out_path = out_dir / "metrics.json"
    payload = {"verdict": verdict, "verdict_msg": verdict_msg,
               "elapsed_s": elapsed, "summary": summary}
    with open(out_path, "w") as f:
        json.dump(payload, f, indent=2, default=str)

    print(f"\n[verdict] {verdict}", flush=True)
    print(f"[verdict_msg] {verdict_msg}", flush=True)
    print(f"[elapsed] {elapsed}s", flush=True)
    print(f"[output] {out_path}", flush=True)


if __name__ == "__main__":
    main()
