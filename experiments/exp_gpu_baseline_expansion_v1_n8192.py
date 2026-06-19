"""GPU BASELINE EXPANSION v1 at N=8192 (T2.2).

CONTEXT:
  F-batch v2 rescue measured 22.67x GPU speedup at N=4096.
  v2 was scope-reduced from v1's N=8192 due to GPU memory constraints.
  This anchor reinstates N=8192 with improved instrumentation and verifies
  killer features (KF-1 hallucination, KF-2 edit-iso) still pass on GPU.

SCIENTIFIC QUESTION:
  At N=8192, M=2048, does GPU implementation deliver >= 10x speedup vs
  CPU at single-op AND batched throughput, AND all killer features pass?

PRE-REGISTERED BANDS:
  HP = GPU speedup >= 10x at single-op AND all KFs pass on GPU.
  HF = GPU speedup <= 2x OR any KF breaks on GPU.
  MIDDLE_BAND = speedup in [2, 10) or marginal KF.

FORMULA SELF-TESTS:
  1. N == 8192 (PROT-018 _n8192 binding).
  2. M = N // 4 = 2048.
  3. speedup = cpu_lat / gpu_lat (single-op).
  4. throughput at batch B = B / gpu_lat_batched(B).

OOM CHECK:
  N=8192, M=2048:
    W = 8192*8192*4 = 256 MiB.
    keys+vals = 2*M*N*4 = 128 MiB.
    CB = 4*N*N*4 = 1024 MiB.
    Total ~1.4 GiB. Under 6 GiB. OK.

TIMEOUT ESTIMATE:
  Smoke ~ 30s. FULL: 3 seeds x [single + 4 batch sizes] x ops = small.
  Wall ~ 600-1200s. PROT-019 _n8192 floor: 21600s.

N-suffix: _n8192 (PROT-018 / PROT-019).
Anchor: gpu_baseline_expansion_v1_n8192
Queue: overnight_queue
Pre-reg: preregs/2026-05-30_gpu_baseline_expansion_v1_n8192.md
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import importlib.util
import json
import os
import time
from pathlib import Path
from typing import Dict, List, Tuple

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from experiments._metric_battery import (  # noqa: E402
    metric_above_thresh_frac,
    metric_max_iso,
    metric_retention,
)


def make_bsc_substrate(N: int, M: int, seed: int, device: torch.device):
    """Build a BSC-codebook substrate. Returns (codebook, W, keys, values, key_idx, val_idx).

    BSC = random bipolar codewords. Supports any N (Kerdock requires
    N=2^even). This is the substrate the user spec named for N=8192.
    """
    C = N        # C = N codewords gives ample probe space
    gen = torch.Generator(device='cpu').manual_seed(seed + 50000)
    raw = (torch.randint(0, 2, (C, N), generator=gen, dtype=torch.float32) * 2 - 1)
    codebook = raw.to(device)
    gen2 = torch.Generator(device='cpu').manual_seed(seed + 51000)
    key_idx = torch.randperm(C, generator=gen2)[:M].to(device).to(torch.long)
    val_idx = torch.randint(0, C, (M,), generator=gen2,
                              dtype=torch.long).to(device)
    keys = codebook[key_idx]
    values = codebook[val_idx]
    W = (values.T @ keys) / N
    return codebook, W, keys, values, key_idx, val_idx

_ck_path = REPO / "experiments" / "_seed_checkpoint.py"
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_n5", _ck_path)
_ck = importlib.util.module_from_spec(_ck_spec)
_ck_spec.loader.exec_module(_ck)
list_completed_keys = _ck.list_completed_keys
write_partial_key   = _ck.write_partial_key
load_partial_key    = _ck.load_partial_key


# PRODUCTION CONFIG -- PROT-018: _n8192 binds N
N = 8192
N_FULL  = N
N_SMOKE = 1024
M_FULL  = N // 4    # 2048
M_SMOKE = N_SMOKE // 4   # 256
SEEDS_FULL  = [7, 17, 23]
SEEDS_SMOKE = [17]
BATCH_SIZES_FULL  = [1, 16, 64, 256]
BATCH_SIZES_SMOKE = [1, 16]
BETA = 8.0
N_TIMING_REPS = 5
N_OPS_PER_TIMING = 50

HP_SPEEDUP = 10.0
HF_SPEEDUP = 2.0
HP_RET = 0.95
HP_ABOVE = 0.10
HP_MAX_ISO = 0.10


def get_output_dir(default_name: str = "gpu_baseline_expansion_v1_n8192") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def time_query_batch(W: torch.Tensor, codebook: torch.Tensor,
                       keys: torch.Tensor, key_idx: torch.Tensor,
                       N_use: int, batch_size: int,
                       n_reps: int, n_ops: int,
                       device: torch.device) -> float:
    """Time batched query op. Returns mean latency per single op in seconds."""
    C = codebook.shape[0]
    # Warmup
    for _ in range(2):
        idxs = torch.randint(0, keys.shape[0], (batch_size,), device=device)
        q = keys[idxs]
        out = q @ W.T
        sims = (codebook @ out.T) / N_use
        _ = torch.argmax(sims, dim=0)
        if device.type == "cuda":
            torch.cuda.synchronize()

    times = []
    for _ in range(n_reps):
        if device.type == "cuda":
            torch.cuda.synchronize()
        t0 = time.perf_counter()
        for _ in range(n_ops):
            idxs = torch.randint(0, keys.shape[0], (batch_size,),
                                 device=device)
            q = keys[idxs]
            out = q @ W.T
            sims = (codebook @ out.T) / N_use
            _ = torch.argmax(sims, dim=0)
        if device.type == "cuda":
            torch.cuda.synchronize()
        t1 = time.perf_counter()
        per_op = (t1 - t0) / n_ops
        times.append(per_op)
    return float(sum(times) / len(times))


def measure_cell(N_use: int, M: int, seed: int,
                  batch_sizes: List[int], cpu_device: torch.device,
                  gpu_device: torch.device,
                  do_gpu: bool) -> Dict:
    # CPU substrate + timing
    cb_cpu, W_cpu, keys_cpu, _vals_cpu, ki_cpu, vi_cpu = make_bsc_substrate(
        N_use, M, seed, cpu_device)
    cpu_lats = {b: time_query_batch(W_cpu, cb_cpu, keys_cpu, ki_cpu,
                                     N_use, b, N_TIMING_REPS,
                                     N_OPS_PER_TIMING, cpu_device)
                 for b in batch_sizes}

    cell: Dict = {"M": int(M), "seed": int(seed), "N": int(N_use),
                   "cpu_lat_per_op_s": {str(b): cpu_lats[b]
                                          for b in batch_sizes}}

    if do_gpu:
        cb_g, W_g, keys_g, _vals_g, ki_g, vi_g = make_bsc_substrate(
            N_use, M, seed, gpu_device)
        gpu_lats = {b: time_query_batch(W_g, cb_g, keys_g, ki_g,
                                          N_use, b, N_TIMING_REPS,
                                          N_OPS_PER_TIMING, gpu_device)
                     for b in batch_sizes}
        cell["gpu_lat_per_op_s"] = {str(b): gpu_lats[b]
                                       for b in batch_sizes}
        cell["speedup_per_batch"] = {str(b): cpu_lats[b] / max(1e-9,
                                                                 gpu_lats[b])
                                        for b in batch_sizes}
        speedup_single = cpu_lats[1] / max(1e-9, gpu_lats[1])
        cell["speedup_single"] = round(float(speedup_single), 3)

        # KF-1 / KF-2 / retention on GPU
        m_ret = metric_retention(W_g, cb_g, ki_g, vi_g, N_use, BETA, seed,
                                  gpu_device, n_probe=200)
        m_above = metric_above_thresh_frac(W_g, cb_g, ki_g, vi_g, N_use,
                                            BETA, seed, gpu_device,
                                            n_probe=200)
        m_iso = metric_max_iso(W_g, cb_g, ki_g, vi_g, N_use, BETA, seed,
                                gpu_device, n_probe=200, n_edits=16)
        cell["gpu_retention"] = m_ret["retention"]
        cell["gpu_above_thresh_frac"] = m_above["above_thresh_frac"]
        cell["gpu_max_iso"] = m_iso["max_iso"]
        cell["gpu_kf_pass"] = (m_ret["retention"] >= HP_RET
                                 and m_above["above_thresh_frac"] <= HP_ABOVE
                                 and m_iso["max_iso"] <= HP_MAX_ISO)
        del cb_g, W_g, keys_g, ki_g, vi_g, _vals_g
        torch.cuda.empty_cache()
    else:
        cell["gpu_lat_per_op_s"] = None
        cell["speedup_per_batch"] = None
        cell["speedup_single"] = 0.0
        cell["gpu_retention"] = None
        cell["gpu_above_thresh_frac"] = None
        cell["gpu_max_iso"] = None
        cell["gpu_kf_pass"] = False

    del cb_cpu, W_cpu, keys_cpu, ki_cpu, vi_cpu
    return cell


def compute_verdict(cells: List[Dict]) -> Tuple[str, str]:
    if not cells:
        return ("GPU_BASE_INCONCLUSIVE", "No cells.")
    speedups = [c["speedup_single"] for c in cells if c["speedup_single"] > 0]
    if not speedups:
        return ("GPU_BASE_INCONCLUSIVE", "No GPU runs.")
    mean_speedup = sum(speedups) / len(speedups)
    kf_pass_count = sum(1 for c in cells if c.get("gpu_kf_pass"))

    detail = (f"mean_speedup_single={mean_speedup:.2f} "
              f"speedups={[round(s,2) for s in speedups]} "
              f"kf_pass={kf_pass_count}/{len(cells)}")

    all_kf_pass = (kf_pass_count == len(cells))
    if mean_speedup >= HP_SPEEDUP and all_kf_pass:
        return ("GPU_BASE_HARD_PASS", "GPU_FAST_AND_CORRECT: " + detail)
    if mean_speedup <= HF_SPEEDUP or not all_kf_pass:
        return ("GPU_BASE_HARD_FAIL", "GPU_INSUFFICIENT: " + detail)
    return ("GPU_BASE_MIDDLE_BAND", "PARTIAL: " + detail)


def _instrumentation_selftest() -> None:
    assert N_FULL == 8192, f"PROT-018: N_FULL must be 8192, got {N_FULL}"

    # Verdict gates
    fake_hp = [{"M": M_FULL, "seed": s, "N": N_FULL,
                  "cpu_lat_per_op_s": {"1": 0.05},
                  "gpu_lat_per_op_s": {"1": 0.005},
                  "speedup_single": 12.0,
                  "speedup_per_batch": {"1": 12.0},
                  "gpu_retention": 0.97,
                  "gpu_above_thresh_frac": 0.05,
                  "gpu_max_iso": 0.05,
                  "gpu_kf_pass": True} for s in SEEDS_FULL]
    v, _ = compute_verdict(fake_hp); assert "HARD_PASS" in v, v

    fake_hf = [{"M": M_FULL, "seed": s, "N": N_FULL,
                  "cpu_lat_per_op_s": {"1": 0.005},
                  "gpu_lat_per_op_s": {"1": 0.0040},
                  "speedup_single": 1.2,
                  "speedup_per_batch": {"1": 1.2},
                  "gpu_retention": 0.97,
                  "gpu_above_thresh_frac": 0.05,
                  "gpu_max_iso": 0.05,
                  "gpu_kf_pass": True} for s in SEEDS_FULL]
    v, _ = compute_verdict(fake_hf); assert "HARD_FAIL" in v, v

    # Forward pass on CPU (no GPU needed for selftest)
    device = torch.device("cpu")
    out = measure_cell(N_SMOKE, M_SMOKE, 17, [1], device, device, do_gpu=False)
    assert "cpu_lat_per_op_s" in out
    print(f"[selftest] gpu_baseline_expansion_v1_n8192 PASS "
          f"smoke cpu_lat[1]={out['cpu_lat_per_op_s']['1']*1e3:.2f}ms",
          flush=True)


_instrumentation_selftest()


def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--self-test", action="store_true", dest="self_test")
    args = p.parse_args()
    if args.self_test:
        sys.exit(0)
    has_cuda = torch.cuda.is_available()
    cpu_device = torch.device("cpu")
    gpu_device = torch.device("cuda" if has_cuda else "cpu")
    do_gpu = has_cuda
    smoke = args.smoke
    N_cfg = N_SMOKE if smoke else N_FULL
    M_cfg = M_SMOKE if smoke else M_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    batches = BATCH_SIZES_SMOKE if smoke else BATCH_SIZES_FULL

    out_dir = get_output_dir()
    done = set(list_completed_keys(out_dir))
    t0 = time.time()
    print(f"[run] gpu_baseline_expansion_v1 smoke={smoke} N={N_cfg} "
          f"M={M_cfg} seeds={seeds} batches={batches} do_gpu={do_gpu} "
          f"done={len(done)}", flush=True)

    cells: List[Dict] = []
    for seed in seeds:
        ck = f"seed{seed}"
        if ck in done:
            body = load_partial_key(out_dir, ck)
            if body is not None:
                cells.append(body); continue
        try:
            out = measure_cell(N_cfg, M_cfg, seed, batches,
                                 cpu_device, gpu_device, do_gpu)
            write_partial_key(out_dir, ck, out)
            cells.append(out)
            print(f"  seed={seed} speedup_single={out['speedup_single']:.2f} "
                  f"kf_pass={out.get('gpu_kf_pass')} "
                  f"({time.time()-t0:.1f}s)", flush=True)
        except (RuntimeError, MemoryError) as e:
            print(f"  seed={seed} FAILED: {e}", flush=True)
            if has_cuda:
                torch.cuda.empty_cache()

    verdict, vm = compute_verdict(cells)
    elapsed = round(time.time() - t0, 2)
    summary = {"anchor": "gpu_baseline_expansion_v1_n8192", "N": N_cfg,
               "smoke": smoke, "M": M_cfg, "seeds": seeds,
               "batches": batches, "cells": cells, "verdict": verdict,
               "verdict_msg": vm, "elapsed_s": elapsed}
    payload = {"verdict": verdict, "verdict_msg": vm,
               "elapsed_s": elapsed, "summary": summary}
    with open(out_dir / "metrics.json", "w") as f:
        json.dump(payload, f, indent=2, default=str)
    print(f"\n[verdict] {verdict}\n[verdict_msg] {vm}\n[elapsed] {elapsed}s",
          flush=True)


if __name__ == "__main__":
    main()
