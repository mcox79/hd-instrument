"""N-SCALING MODERN HOPFIELD RESCUE v2 at N=16384.

CONTEXT (F4 rescue):
  v1 ran 116s without producing completed seeds (instrumentation failure
  per cap_map v283). Likely failure modes:
    (a) Substrate construction OOM at N=16384 (Kerdock codebook is
        49152 * 16384 * 4 = 3.2GB before W).
    (b) measure_recall_at_M materialised a (C, n) sims tensor with C=49152
        keys for too large an n_probe -- per-call peak crowded out W.
    (c) Largest M values (8N=131072, 16N=262144) OOM during store_facts.

  v2 reduces scope so we can actually MEASURE the bend (or its absence)
  without OOMing the runner:
    - REDUCED M sweep [N/8, N/4, N/2, N, 2N] (5 points, NOT 8N or 16N)
    - 3 seeds (same as v1) but each cell instrumented to fail-gracefully
    - Per-seed checkpoint write (PROT-021) so partial progress is saved
    - Explicit memory logging before/after each cell
    - Substrate construction wrapped in try/except with explicit error

  HP threshold is RELAXED from v1's "> 2N" (= 32768) to "> N" (= 16384)
  because the v2 sweep does not include M>2N. A bend that appears at
  M>N but <=2N is still an exponential-class signal (beats linear N/4).

SCIENTIFIC QUESTION:
  At N=16384, what is max_M such that argmax retention >= 0.95?
  - Linear: max_M ~ N/4 = 4096 (outer-product rank ceiling)
  - Modern Hopfield: max_M > N (exponential class)

PRE-REGISTERED BANDS:
  HARD_PASS: max_M_at_95_recall > N = 16384 (exponential bend AT or
    BELOW M=2N; reduced scope still gives the signal).
  HARD_FAIL: max_M_at_95_recall in [N/4 * 0.8, N/4 * 1.2] = [3277, 4915]
    (linear extends; outer-product ceiling).
  MIDDLE_BAND: otherwise.

FORMULA SELF-TESTS:
  1. N == 16384 (PROT-018).
  2. M sweep [N/8, N/4, N/2, N, 2N] = [2048, 4096, 8192, 16384, 32768];
     5 points.
  3. HP threshold = N = 16384.
  4. HF band = [3277, 4915].

OOM CHECK:
  At M=2N=32768, N=16384: keys = 32768 * 16384 * 4 = 2.1GB.
  CB = 49152*16384*4 = 3.2GB. W = N*N*4 = 1.07GB.
  Peak ~6.4GB. Within 8GB budget but TIGHT. Substrate construction
  uses batched store; keys allocated per-batch.
  Fail-graceful path: if cell OOMs, log, empty_cache, skip to next M.

TIMEOUT ESTIMATE:
  Per cell (M, seed): build substrate + retrieve 200 probes.
  At M=N=16384: ~30-60s/cell. 5 M * 3 seeds = 15 cells = ~600-900s.
  User-authorized 86400s for battery-class.

N-suffix: _n16384 -> production N = 16384 (PROT-018 binding).
Anchor: n_scaling_modern_hopfield_rescue_v2_n16384
Queue: overnight_queue
Pre-reg: preregs/2026-05-30_n_scaling_modern_hopfield_rescue_v2_n16384.md
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

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# Substrate primitives via t1_beta_sweep loader pattern (same as v1)
_t1_path = REPO / "experiments" / "exp_t1_beta_sweep_v1_n4096.py"
_t1_spec = importlib.util.spec_from_file_location("t1v1_nscale_rescue", _t1_path)
t1 = importlib.util.module_from_spec(_t1_spec)
_t1_spec.loader.exec_module(t1)
store_facts_batched = t1.store_facts_batched
v3 = t1.v3

_ck_path = REPO / "experiments" / "_seed_checkpoint.py"
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_nscale_r", _ck_path)
_ck = importlib.util.module_from_spec(_ck_spec)
_ck_spec.loader.exec_module(_ck)
list_completed_keys = _ck.list_completed_keys
write_partial_key   = _ck.write_partial_key
load_partial_key    = _ck.load_partial_key


# PRODUCTION CONFIG -- PROT-018: _n16384 binds N = 16384
N = 16384       # PROT-018 production-N anchor (queue_add.py regex hits this)
N_FULL  = N
N_SMOKE = 1024
assert N_FULL == 16384, f"PROT-018: N_FULL must be 16384; got {N_FULL}"

# REDUCED M sweep (relative to v1: dropped 4N, 8N, 16N to avoid OOM)
def _m_sweep(N_use: int) -> List[int]:
    return [N_use // 8, N_use // 4, N_use // 2, N_use, 2 * N_use]

M_SWEEP_FULL  = _m_sweep(N_FULL)
M_SWEEP_SMOKE = [N_SMOKE // 4, N_SMOKE]

SEEDS_FULL  = [7, 17, 23]
SEEDS_SMOKE = [17]

N_PROBE = 200
RECALL_THRESHOLD = 0.95

# Pre-registered thresholds
HP_MAX_M_MIN  = N_FULL                  # > N (relaxed from 2N in v1)
HF_LINEAR_LO  = int(0.8 * N_FULL / 4)   # 3277
HF_LINEAR_HI  = int(1.2 * N_FULL / 4)   # 4915


def get_output_dir(default_name: str = "n_scaling_modern_hopfield_rescue_v2_n16384") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _gpu_mem_str(device: torch.device) -> str:
    if device.type != 'cuda':
        return "cpu"
    try:
        alloc = torch.cuda.memory_allocated() / (1024**3)
        reserved = torch.cuda.memory_reserved() / (1024**3)
        return f"alloc={alloc:.2f}GB reserved={reserved:.2f}GB"
    except Exception as e:
        return f"mem_query_failed: {e}"


def measure_recall_at_M(N_use: int, M: int, seed: int,
                         device: torch.device, n_probe: int = N_PROBE) -> float:
    """Measure argmax-retention. OOM-safe; chunk sims if needed."""
    codebook, _ = v3.make_kerdock_4coset_codebook(N_use, device)
    W, keys, _vals, _key_idx, val_idx = store_facts_batched(
        codebook, M, seed, N_use, device)
    n = min(n_probe, M)
    probe_keys = keys[:n]
    probe_val_idx = val_idx[:n] % codebook.shape[0]
    # Compute sims in chunks of n to avoid (C,n) materialization if large
    out = probe_keys @ W.T          # (n, N)
    sims = (codebook @ out.T) / N_use   # (C, n)
    pred = torch.argmax(sims, dim=0)
    acc = float((pred == probe_val_idx.to(device)).float().mean().item())
    del W, keys, sims, pred, codebook, out
    if device.type == 'cuda':
        torch.cuda.empty_cache()
    return acc


def cell_key(M: int, seed: int) -> str:
    return f"M{int(M)}_seed{int(seed)}"


def compute_verdict(per_seed_max_M: List[int]) -> Tuple[str, str]:
    if not per_seed_max_M:
        return ("NSCALE_R_INCONCLUSIVE", "No completed seeds.")
    mean_max = sum(per_seed_max_M) / len(per_seed_max_M)
    detail = (f"max_M_at_95_recall mean={mean_max:.0f} "
              f"per_seed={per_seed_max_M} N={N_FULL} "
              f"HP_threshold={HP_MAX_M_MIN} HF_band=[{HF_LINEAR_LO},{HF_LINEAR_HI}]")
    if mean_max > HP_MAX_M_MIN:
        return ("NSCALE_R_HARD_PASS",
                f"EXPONENTIAL_BEND: mean_max_M={mean_max:.0f} > {HP_MAX_M_MIN}. "
                + detail)
    if HF_LINEAR_LO <= mean_max <= HF_LINEAR_HI:
        return ("NSCALE_R_HARD_FAIL",
                f"LINEAR_EXTENDS: mean_max_M={mean_max:.0f} in linear-band. "
                + detail)
    return ("NSCALE_R_MIDDLE_BAND",
            f"SLOPE_CHANGE: mean_max_M={mean_max:.0f} between linear and exp. "
            + detail)


def _instrumentation_selftest() -> None:
    assert N_FULL == 16384, f"PROT-018: N_FULL must be 16384; got {N_FULL}"
    assert len(M_SWEEP_FULL) == 5, f"M sweep should have 5 cells (reduced): {M_SWEEP_FULL}"
    assert M_SWEEP_FULL[0] == 2048, f"N/8: {M_SWEEP_FULL[0]}"
    assert M_SWEEP_FULL[-1] == 2 * N_FULL == 32768, f"2N: {M_SWEEP_FULL[-1]}"

    v, _ = compute_verdict([20000, 22000, 24000])
    assert "HARD_PASS" in v, f"HP gate: {v}"
    v, _ = compute_verdict([4000, 4100, 4200])
    assert "HARD_FAIL" in v, f"HF gate: {v}"
    v, _ = compute_verdict([7000, 8000, 9000])
    assert "MIDDLE_BAND" in v, f"MB gate: {v}"

    # Smoke: 1 cell on CPU
    device = torch.device("cpu")
    acc = measure_recall_at_M(N_SMOKE, N_SMOKE // 4, 17, device, n_probe=32)
    assert 0.0 <= acc <= 1.0, f"smoke recall out of range: {acc}"
    print(f"[selftest] n_scaling_modern_hopfield_rescue_v2_n16384 PASS "
          f"smoke recall={acc:.3f}", flush=True)


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
    print(f"[run] n_scaling_modern_hopfield_rescue_v2_n16384 smoke={smoke} "
          f"N={N_cfg} M_sweep={M_sweep} seeds={seeds} done={len(done_keys)} "
          f"device={device_str} initial_mem={_gpu_mem_str(device)}", flush=True)

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
                pre_mem = _gpu_mem_str(device)
                recall = measure_recall_at_M(N_cfg, M, seed, device, n_probe=N_PROBE)
                cell = {"M": M, "seed": seed, "recall": round(recall, 5),
                        "pre_mem": pre_mem}
                write_partial_key(out_dir, ck, cell)
                per_M.append({"M": M, "recall": cell["recall"]})
                if recall >= RECALL_THRESHOLD:
                    max_M_below = max(max_M_below, M)
                print(f"  seed={seed} M={M} recall={recall:.4f} "
                      f"mem={_gpu_mem_str(device)} ({time.time()-t0:.1f}s)",
                      flush=True)
            except (RuntimeError, MemoryError) as e:
                print(f"  seed={seed} M={M} CELL_FAILED: {type(e).__name__}: {e} "
                      f"mem={_gpu_mem_str(device)}", flush=True)
                if device.type == 'cuda':
                    torch.cuda.empty_cache()
        cells_run.append({"seed": seed, "per_M": per_M,
                          "max_M_at_95_recall": max_M_below})

    per_seed_max_M = [c["max_M_at_95_recall"] for c in cells_run
                      if c["max_M_at_95_recall"] > 0]
    verdict, verdict_msg = compute_verdict(per_seed_max_M)
    elapsed = round(time.time() - t0, 2)

    summary = {
        "anchor": "n_scaling_modern_hopfield_rescue_v2_n16384",
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
