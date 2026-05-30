"""GPU LARGE-N RESCUE SERIALIZED v1 -- composite N=8192 / N=4096 / N=16384.

CONTEXT:
  N-batch (commit e457f1e / 947b22e) returned 3 NO_METRICS due to PARALLEL-GPU
  CONTENTION on the runner (multiple python processes competing for the 8 GiB
  GPU):
    N5  : gpu_baseline_expansion_n8192   -> OOM under contention
    N11 : sparse_w_gpu_integration_n4096 -> STACK_BUFFER_OVERRUN under contention
    N12 : n_scaling_chunked_codebook_n16384 -> OOM under contention
  Each script's own _instrumentation_selftest + verdict gate is fine. The
  failure mode was the runner's parallel scheduling, not the scripts.

ENGINEERING RESCUE:
  Run all three sub-tests SEQUENTIALLY inside a SINGLE python process. This
  occupies exactly one runner slot but has NO internal GPU contention.
  Between sub-tests: torch.cuda.empty_cache() + gc.collect() + memory snapshot.
  Each sub-test produces its own partial metrics file, then we aggregate
  into one combined metrics.json with sub-verdicts.

SUB-TESTS:
  sub1: gpu_baseline_expansion_n8192     (N=8192,  M=2048,           3 seeds)
  sub2: sparse_w_gpu_integration_n4096   (N=4096,  M in [128, 1024, 4096],
                                          3 seeds)
  sub3: n_scaling_chunked_codebook_n16384 (N=16384, M sweep [N/8, N/4, N/2, N],
                                           3 seeds, chunked construction)

PRE-REGISTERED COMPOSITE BANDS:
  HP = all 3 sub-tests succeed AND each meets its individual HP gate:
        sub1: GPU >= 10x speedup at N=8192 single-op AND all KFs pass
        sub2: sparse_gpu_lat <= 2*dense AND mem_savings >= 4x AND KFs pass
        sub3: chunked construction succeeds AND
              max_M_at_95_recall > N/4 * 1.5 (exponential bend)
  HF = any sub-test crashes (OOM / RuntimeError) preventing metrics emission.
  MIDDLE_BAND = all 3 sub-tests succeed (metrics emitted) but not all meet HP.

  IMPORTANT: this anchor's "success" is INSTRUMENTATION_SUCCESS. Even a
  sub-test that HARD_FAILs its OWN HP gate but EMITS METRICS is a success
  for this rescue anchor; only crashes cause HARD_FAIL here.

  Concretely, this anchor's final verdict downgrades to MIDDLE_BAND if any
  sub-test reports its own HARD_FAIL/HF gate (because the gate was reached,
  not crashed), and only HARD_FAILs on actual runtime exception.

FORMULA SELF-TESTS:
  1. PROT-018 _n8192 nominal (composite covers N in {4096, 8192, 16384}).
  2. Inner runs reuse the v1 logic of each sub-test script verbatim.
  3. Composite verdict gate: HP/HF/MB triggered correctly by synthetic
     sub-test verdicts.

N-suffix: _n8192 (binding for the composite -- N=8192 is the canonical anchor
N; sub3's N=16384 is documented in the script body. Per PROT-018, the
production CONFIG at minimum N=8192 is the bind target.).

Anchor: gpu_large_n_rescue_serialized_v1_n8192
Queue: overnight_queue
Pre-reg: preregs/2026-05-30_gpu_large_n_rescue_serialized_v1_n8192.md
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import gc
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

from experiments._metric_battery import (  # noqa: E402
    make_substrate,
    metric_above_thresh_frac,
    metric_max_iso,
    metric_retention,
)

_ck_path = REPO / "experiments" / "_seed_checkpoint.py"
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_rescue", _ck_path)
_ck = importlib.util.module_from_spec(_ck_spec)
_ck_spec.loader.exec_module(_ck)
list_completed_keys = _ck.list_completed_keys
write_partial_key   = _ck.write_partial_key
load_partial_key    = _ck.load_partial_key

# Kerdock 4-coset builder from v3 (used by sub3 for the chunked builder)
_v3_path = REPO / "experiments" / "exp_wave14y_erase_kerdock_v3.py"
_v3_spec = importlib.util.spec_from_file_location("kerdock_v3_rescue", _v3_path)
v3 = importlib.util.module_from_spec(_v3_spec)
_v3_spec.loader.exec_module(v3)


# PRODUCTION CONFIG -- PROT-018: _n8192 binds the composite's nominal N
N = 8192

# ---- Sub 1: gpu_baseline_expansion (N=8192) -----------------------------
SUB1_N        = 8192
SUB1_N_SMOKE  = 1024
SUB1_M        = SUB1_N // 4   # 2048
SUB1_M_SMOKE  = SUB1_N_SMOKE // 4
SUB1_SEEDS_FULL  = [7, 17, 23]
SUB1_SEEDS_SMOKE = [17]
SUB1_BATCH_FULL  = [1, 16, 64, 256]
SUB1_BATCH_SMOKE = [1, 16]
SUB1_HP_SPEEDUP = 10.0
SUB1_HF_SPEEDUP = 2.0
SUB1_HP_RET = 0.95
SUB1_HP_ABOVE = 0.10
SUB1_HP_MAX_ISO = 0.10

# ---- Sub 2: sparse_w_gpu_integration (N=4096) ---------------------------
SUB2_N        = 4096
SUB2_N_SMOKE  = 1024
SUB2_M_SWEEP_FULL  = [128, 1024, 4096]
SUB2_M_SWEEP_SMOKE = [32, 128]
SUB2_SEEDS_FULL  = [7, 17, 23]
SUB2_SEEDS_SMOKE = [17]
SUB2_HP_LAT_RATIO = 2.0
SUB2_HP_MEM_SAV  = 4.0
SUB2_HP_RET      = 0.95
SUB2_HP_KF2      = 0.05

# ---- Sub 3: n_scaling_chunked_codebook (N=16384) ------------------------
SUB3_N        = 16384
SUB3_N_SMOKE  = 1024     # selftest scale
SUB3_M_FULL   = [SUB3_N // 8, SUB3_N // 4, SUB3_N // 2, SUB3_N]
SUB3_M_SMOKE  = [16, 32]
SUB3_SEEDS_FULL  = [7, 17, 23]
SUB3_SEEDS_SMOKE = [17]
SUB3_RECALL_THRESHOLD = 0.95
SUB3_N_PROBE = 100

BETA = 8.0
N_TIMING_REPS = 5
N_OPS_PER_TIMING = 30


def get_output_dir(default_name: str = "gpu_large_n_rescue_serialized_v1_n8192") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _mem_snapshot(device: torch.device, tag: str) -> Dict:
    info: Dict = {"tag": tag, "device_type": device.type}
    if device.type == "cuda":
        info["alloc_bytes"] = int(torch.cuda.memory_allocated(device))
        info["reserved_bytes"] = int(torch.cuda.memory_reserved(device))
        info["alloc_gib"] = round(info["alloc_bytes"] / (1024**3), 3)
        info["reserved_gib"] = round(info["reserved_bytes"] / (1024**3), 3)
    return info


def _free_gpu(device: torch.device, tag: str, log: List[Dict]):
    gc.collect()
    if device.type == "cuda":
        torch.cuda.empty_cache()
        torch.cuda.synchronize()
    log.append(_mem_snapshot(device, tag))


# --------------------- Sub1: GPU baseline expansion ---------------------
def make_bsc_substrate(N_use: int, M: int, seed: int, device: torch.device):
    C = N_use
    gen = torch.Generator(device='cpu').manual_seed(seed + 50000)
    raw = (torch.randint(0, 2, (C, N_use), generator=gen,
                          dtype=torch.float32) * 2 - 1)
    codebook = raw.to(device)
    gen2 = torch.Generator(device='cpu').manual_seed(seed + 51000)
    key_idx = torch.randperm(C, generator=gen2)[:M].to(device).to(torch.long)
    val_idx = torch.randint(0, C, (M,), generator=gen2,
                              dtype=torch.long).to(device)
    keys = codebook[key_idx]
    values = codebook[val_idx]
    W = (values.T @ keys) / N_use
    return codebook, W, keys, values, key_idx, val_idx


def _time_query_batch(W, codebook, keys, key_idx, N_use, batch_size,
                       n_reps, n_ops, device):
    for _ in range(2):
        idxs = torch.randint(0, keys.shape[0], (batch_size,), device=device)
        q = keys[idxs]
        out = q @ W.T
        sims = (codebook @ out.T) / N_use
        _ = torch.argmax(sims, dim=0)
        if device.type == "cuda":
            torch.cuda.synchronize()
    times: List[float] = []
    for _ in range(n_reps):
        if device.type == "cuda":
            torch.cuda.synchronize()
        t0 = time.perf_counter()
        for _ in range(n_ops):
            idxs = torch.randint(0, keys.shape[0], (batch_size,), device=device)
            q = keys[idxs]
            out = q @ W.T
            sims = (codebook @ out.T) / N_use
            _ = torch.argmax(sims, dim=0)
        if device.type == "cuda":
            torch.cuda.synchronize()
        t1 = time.perf_counter()
        times.append((t1 - t0) / n_ops)
    return float(sum(times) / len(times))


def sub1_cell(N_use, M, seed, batches, cpu_device, gpu_device, do_gpu):
    cb_cpu, W_cpu, keys_cpu, _v_cpu, ki_cpu, vi_cpu = make_bsc_substrate(
        N_use, M, seed, cpu_device)
    cpu_lats = {b: _time_query_batch(W_cpu, cb_cpu, keys_cpu, ki_cpu,
                                       N_use, b, N_TIMING_REPS,
                                       N_OPS_PER_TIMING, cpu_device)
                 for b in batches}
    cell: Dict = {"M": int(M), "seed": int(seed), "N": int(N_use),
                   "cpu_lat_per_op_s": {str(b): cpu_lats[b]
                                          for b in batches}}
    if do_gpu:
        cb_g, W_g, keys_g, _v_g, ki_g, vi_g = make_bsc_substrate(
            N_use, M, seed, gpu_device)
        gpu_lats = {b: _time_query_batch(W_g, cb_g, keys_g, ki_g,
                                           N_use, b, N_TIMING_REPS,
                                           N_OPS_PER_TIMING, gpu_device)
                     for b in batches}
        cell["gpu_lat_per_op_s"] = {str(b): gpu_lats[b] for b in batches}
        cell["speedup_per_batch"] = {str(b): cpu_lats[b] / max(1e-9, gpu_lats[b])
                                        for b in batches}
        cell["speedup_single"] = round(float(cpu_lats[1] / max(1e-9, gpu_lats[1])), 3)
        m_ret = metric_retention(W_g, cb_g, ki_g, vi_g, N_use, BETA, seed,
                                  gpu_device, n_probe=200)
        m_above = metric_above_thresh_frac(W_g, cb_g, ki_g, vi_g, N_use,
                                             BETA, seed, gpu_device, n_probe=200)
        m_iso = metric_max_iso(W_g, cb_g, ki_g, vi_g, N_use, BETA, seed,
                                gpu_device, n_probe=200, n_edits=16)
        cell["gpu_retention"] = m_ret["retention"]
        cell["gpu_above_thresh_frac"] = m_above["above_thresh_frac"]
        cell["gpu_max_iso"] = m_iso["max_iso"]
        cell["gpu_kf_pass"] = (m_ret["retention"] >= SUB1_HP_RET
                                 and m_above["above_thresh_frac"] <= SUB1_HP_ABOVE
                                 and m_iso["max_iso"] <= SUB1_HP_MAX_ISO)
        del cb_g, W_g, keys_g, ki_g, vi_g, _v_g
        if gpu_device.type == "cuda":
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


def sub1_verdict(cells: List[Dict]) -> Tuple[str, str]:
    if not cells:
        return ("SUB1_INCONCLUSIVE", "No cells.")
    speedups = [c["speedup_single"] for c in cells if c["speedup_single"] > 0]
    if not speedups:
        return ("SUB1_INCONCLUSIVE", "No GPU runs.")
    mean_speedup = sum(speedups) / len(speedups)
    kf_pass_count = sum(1 for c in cells if c.get("gpu_kf_pass"))
    all_kf_pass = (kf_pass_count == len(cells))
    detail = (f"mean_speedup={mean_speedup:.2f} "
              f"kf_pass={kf_pass_count}/{len(cells)}")
    if mean_speedup >= SUB1_HP_SPEEDUP and all_kf_pass:
        return ("SUB1_HARD_PASS", "GPU_FAST_AND_CORRECT: " + detail)
    if mean_speedup <= SUB1_HF_SPEEDUP or not all_kf_pass:
        return ("SUB1_HARD_FAIL", "GPU_INSUFFICIENT: " + detail)
    return ("SUB1_MIDDLE_BAND", "PARTIAL: " + detail)


def run_sub1(smoke: bool, device: torch.device, out_dir: Path,
              mem_log: List[Dict]) -> Dict:
    print("\n========== SUB1: gpu_baseline_expansion_n8192 ==========", flush=True)
    has_cuda = device.type == "cuda"
    cpu_device = torch.device("cpu")
    do_gpu = has_cuda
    N_use = SUB1_N_SMOKE if smoke else SUB1_N
    M = SUB1_M_SMOKE if smoke else SUB1_M
    seeds = SUB1_SEEDS_SMOKE if smoke else SUB1_SEEDS_FULL
    batches = SUB1_BATCH_SMOKE if smoke else SUB1_BATCH_FULL
    t0 = time.time()
    cells: List[Dict] = []
    crashed = False
    crash_msg = ""
    for seed in seeds:
        ck = f"sub1_seed{seed}"
        try:
            out = sub1_cell(N_use, M, seed, batches, cpu_device, device, do_gpu)
            write_partial_key(out_dir, ck, out)
            cells.append(out)
            print(f"  sub1 seed={seed} speedup_single={out['speedup_single']:.2f} "
                  f"kf_pass={out.get('gpu_kf_pass')} "
                  f"({time.time()-t0:.1f}s)", flush=True)
        except (RuntimeError, MemoryError) as e:
            crashed = True
            crash_msg = f"sub1 seed={seed}: {e}"
            print(f"  sub1 seed={seed} CRASH: {e}", flush=True)
            if has_cuda:
                torch.cuda.empty_cache()
            break
    _free_gpu(device, "after_sub1", mem_log)
    verdict, vm = sub1_verdict(cells)
    return {"sub": "sub1", "cells": cells, "verdict": verdict,
            "verdict_msg": vm, "crashed": crashed, "crash_msg": crash_msg,
            "elapsed_s": round(time.time() - t0, 2)}


# ----------------------- Sub2: sparse_w_gpu_integration -----------------
def _time_sparse(keys, values, codebook, key_idx, N_use, batch_size, device,
                  n_reps, n_ops):
    M = keys.shape[0]
    for _ in range(2):
        idxs = torch.randint(0, M, (batch_size,), device=device)
        q = keys[idxs]
        coeffs = (q @ keys.T) / N_use
        out = coeffs @ values
        sims = (codebook @ out.T) / N_use
        _ = torch.argmax(sims, dim=0)
        if device.type == "cuda":
            torch.cuda.synchronize()
    times: List[float] = []
    for _ in range(n_reps):
        if device.type == "cuda":
            torch.cuda.synchronize()
        t0 = time.perf_counter()
        for _ in range(n_ops):
            idxs = torch.randint(0, M, (batch_size,), device=device)
            q = keys[idxs]
            coeffs = (q @ keys.T) / N_use
            out = coeffs @ values
            sims = (codebook @ out.T) / N_use
            _ = torch.argmax(sims, dim=0)
        if device.type == "cuda":
            torch.cuda.synchronize()
        t1 = time.perf_counter()
        times.append((t1 - t0) / n_ops)
    return float(sum(times) / len(times))


def _time_dense(W, codebook, keys, N_use, batch_size, device, n_reps, n_ops):
    M = keys.shape[0]
    for _ in range(2):
        idxs = torch.randint(0, M, (batch_size,), device=device)
        q = keys[idxs]
        out = q @ W.T
        sims = (codebook @ out.T) / N_use
        _ = torch.argmax(sims, dim=0)
        if device.type == "cuda":
            torch.cuda.synchronize()
    times: List[float] = []
    for _ in range(n_reps):
        if device.type == "cuda":
            torch.cuda.synchronize()
        t0 = time.perf_counter()
        for _ in range(n_ops):
            idxs = torch.randint(0, M, (batch_size,), device=device)
            q = keys[idxs]
            out = q @ W.T
            sims = (codebook @ out.T) / N_use
            _ = torch.argmax(sims, dim=0)
        if device.type == "cuda":
            torch.cuda.synchronize()
        t1 = time.perf_counter()
        times.append((t1 - t0) / n_ops)
    return float(sum(times) / len(times))


def sub2_cell(N_use, M, seed, device):
    codebook, W, keys, values, key_idx, val_idx = make_substrate(
        N_use, M, seed, device)
    sparse_lat = _time_sparse(keys, values, codebook, key_idx, N_use, 1, device,
                                 N_TIMING_REPS, N_OPS_PER_TIMING)
    dense_lat  = _time_dense(W, codebook, keys, N_use, 1, device,
                                 N_TIMING_REPS, N_OPS_PER_TIMING)
    lat_ratio = sparse_lat / max(1e-9, dense_lat)
    n_probe = min(200, M)
    probe_keys = keys[:n_probe]
    probe_val_idx = val_idx[:n_probe] % codebook.shape[0]
    coeffs = (probe_keys @ keys.T) / N_use
    out = coeffs @ values
    sims = (codebook @ out.T) / N_use
    pred = torch.argmax(sims, dim=0)
    sparse_ret = float((pred == probe_val_idx.to(device)).float().mean().item())
    m_iso = metric_max_iso(W, codebook, key_idx, val_idx, N_use, BETA,
                            seed, device, n_probe=n_probe, n_edits=16)
    sparse_b = 2 * M * N_use * 4
    dense_b = N_use * N_use * 4
    mem_sav = dense_b / max(1, sparse_b)
    del codebook, W, keys, values
    if device.type == "cuda":
        torch.cuda.empty_cache()
    return {"M": int(M), "seed": int(seed), "N": int(N_use),
            "sparse_lat_s": sparse_lat, "dense_lat_s": dense_lat,
            "lat_ratio_sparse_over_dense": round(lat_ratio, 5),
            "sparse_retention": round(sparse_ret, 5),
            "kf2_max_iso": round(m_iso["max_iso"], 5),
            "sparse_bytes": int(sparse_b), "dense_bytes": int(dense_b),
            "mem_savings": round(mem_sav, 5)}


def sub2_verdict(cells: List[Dict]) -> Tuple[str, str]:
    if not cells:
        return ("SUB2_INCONCLUSIVE", "No cells.")
    by_seed: Dict[int, List[Dict]] = {}
    for c in cells:
        by_seed.setdefault(c["seed"], []).append(c)
    hp_seeds = 0
    hf_seeds = 0
    for s, cs in by_seed.items():
        hp_ok = all(c["lat_ratio_sparse_over_dense"] <= SUB2_HP_LAT_RATIO
                     and c["mem_savings"] >= SUB2_HP_MEM_SAV
                     and c["sparse_retention"] >= SUB2_HP_RET
                     and c["kf2_max_iso"] <= SUB2_HP_KF2 for c in cs)
        hf_ok = any(c["lat_ratio_sparse_over_dense"] > SUB2_HP_LAT_RATIO
                     or c["sparse_retention"] < SUB2_HP_RET
                     or c["kf2_max_iso"] > SUB2_HP_KF2 for c in cs)
        if hp_ok:
            hp_seeds += 1
        if hf_ok:
            hf_seeds += 1
    detail = f"hp={hp_seeds}/{len(by_seed)} hf={hf_seeds}/{len(by_seed)}"
    if hf_seeds >= 2:
        return ("SUB2_HARD_FAIL", "SPARSE_GPU_BROKE: " + detail)
    if hp_seeds >= 2:
        return ("SUB2_HARD_PASS", "SPARSE_GPU_INTEGRATES: " + detail)
    return ("SUB2_MIDDLE_BAND", "PARTIAL: " + detail)


def run_sub2(smoke: bool, device: torch.device, out_dir: Path,
              mem_log: List[Dict]) -> Dict:
    print("\n========== SUB2: sparse_w_gpu_integration_n4096 ==========", flush=True)
    N_use = SUB2_N_SMOKE if smoke else SUB2_N
    Ms = SUB2_M_SWEEP_SMOKE if smoke else SUB2_M_SWEEP_FULL
    seeds = SUB2_SEEDS_SMOKE if smoke else SUB2_SEEDS_FULL
    t0 = time.time()
    cells: List[Dict] = []
    crashed = False
    crash_msg = ""
    for M in Ms:
        for seed in seeds:
            ck = f"sub2_M{M}_seed{seed}"
            try:
                out = sub2_cell(N_use, M, seed, device)
                write_partial_key(out_dir, ck, out)
                cells.append(out)
                print(f"  sub2 M={M} seed={seed} "
                      f"lat_ratio={out['lat_ratio_sparse_over_dense']:.3f} "
                      f"ret={out['sparse_retention']:.3f} "
                      f"mem_sav={out['mem_savings']:.3f} "
                      f"({time.time()-t0:.1f}s)", flush=True)
            except (RuntimeError, MemoryError) as e:
                crashed = True
                crash_msg = f"sub2 M={M} seed={seed}: {e}"
                print(f"  sub2 M={M} seed={seed} CRASH: {e}", flush=True)
                if device.type == "cuda":
                    torch.cuda.empty_cache()
                break
        if crashed:
            break
    _free_gpu(device, "after_sub2", mem_log)
    verdict, vm = sub2_verdict(cells)
    return {"sub": "sub2", "cells": cells, "verdict": verdict,
            "verdict_msg": vm, "crashed": crashed, "crash_msg": crash_msg,
            "elapsed_s": round(time.time() - t0, 2)}


# ----------------- Sub3: n_scaling_chunked_codebook ---------------------
def _kerdock_chunked(N_use: int, device: torch.device,
                       mem_log: List[Dict] | None = None):
    n_log2 = int(round(math.log2(N_use)))
    if 2 ** n_log2 != N_use:
        raise ValueError(f"N={N_use} must be power of 2")
    if n_log2 % 2 != 0:
        raise ValueError(f"N={N_use} requires even log2(N)")
    t = n_log2 // 2
    log_tab, antilog_tab = v3.build_gf2t_tables(t)
    H = v3.v1.sylvester_hadamard(n_log2, device)
    if mem_log is not None:
        mem_log.append(_mem_snapshot(device, f"sub3_after_H_N{N_use}"))
    alpha = antilog_tab[1]
    alpha_squared = antilog_tab[2]
    b_values = [0, 1, alpha, alpha_squared]
    result = torch.empty((4 * N_use, N_use), dtype=torch.float32, device=device)
    if mem_log is not None:
        mem_log.append(_mem_snapshot(device, f"sub3_after_result_alloc_N{N_use}"))
    for i, b in enumerate(b_values):
        q_b = v3.build_q_b_signs(b, N_use, t, log_tab, antilog_tab, device)
        coset = H * q_b.unsqueeze(0)
        result[i * N_use:(i + 1) * N_use].copy_(coset)
        del coset
        if device.type == "cuda":
            torch.cuda.empty_cache()
        gc.collect()
        if mem_log is not None:
            mem_log.append(_mem_snapshot(device,
                f"sub3_after_coset_{i}_N{N_use}"))
    del H
    if device.type == "cuda":
        torch.cuda.empty_cache()
    gc.collect()
    return result, {"t": t, "b_values": b_values, "codebook_size": result.shape[0]}


def _store_facts_subset(codebook, M, seed, N_use, device):
    C = codebook.shape[0]
    gen = torch.Generator(device=device).manual_seed(seed + 23000)
    key_idx = torch.randperm(C, generator=gen, device=device)[:M].to(torch.long)
    val_idx = torch.randint(0, C, (M,), generator=gen, device=device,
                              dtype=torch.long)
    keys = codebook[key_idx]
    vals = codebook[val_idx]
    W = (vals.T @ keys) / N_use
    return W, key_idx, val_idx


def _retention_at_M(codebook, N_use, M, seed, device):
    W, key_idx, val_idx = _store_facts_subset(codebook, M, seed, N_use, device)
    n = min(SUB3_N_PROBE, M)
    probe_keys = codebook[key_idx[:n]]
    probe_val_idx = val_idx[:n]
    out = probe_keys @ W.T
    sims = (codebook @ out.T) / N_use
    pred = torch.argmax(sims, dim=0)
    acc = float((pred == probe_val_idx).float().mean().item())
    del W, probe_keys
    if device.type == "cuda":
        torch.cuda.empty_cache()
    return acc


def sub3_cell(codebook, N_use, M_sweep, seed, device):
    by_M: Dict[int, float] = {}
    max_M = 0
    for M in M_sweep:
        try:
            ret = _retention_at_M(codebook, N_use, M, seed, device)
            by_M[M] = round(ret, 5)
            if ret >= SUB3_RECALL_THRESHOLD:
                max_M = max(max_M, M)
        except (RuntimeError, MemoryError) as e:
            by_M[M] = -1.0
            print(f"    sub3 seed={seed} M={M} ret FAIL: {e}", flush=True)
            if device.type == "cuda":
                torch.cuda.empty_cache()
    return {"seed": int(seed), "N": int(N_use),
            "M_sweep": list(M_sweep),
            "retention_by_M": {str(k): v for k, v in by_M.items()},
            "max_M_at_95_recall": int(max_M)}


def sub3_verdict(cells: List[Dict], construct_ok: bool) -> Tuple[str, str]:
    if not construct_ok:
        return ("SUB3_INCONCLUSIVE",
                "Chunked construction OOM; chunking design needs rework.")
    if not cells:
        return ("SUB3_INCONCLUSIVE",
                "Construction succeeded but no retention cells ran.")
    per_seed_max = [c["max_M_at_95_recall"] for c in cells
                     if c["max_M_at_95_recall"] > 0]
    if not per_seed_max:
        return ("SUB3_INCONCLUSIVE", "No seed reached recall threshold.")
    mean_max = sum(per_seed_max) / len(per_seed_max)
    quarter_N = SUB3_N / 4.0
    HF_LO = quarter_N * 0.8
    HF_HI = quarter_N * 1.2
    detail = (f"mean_max={mean_max:.0f} N/4={quarter_N:.0f} "
              f"HF_band=[{HF_LO:.0f},{HF_HI:.0f}]")
    if mean_max > quarter_N * 1.5:
        return ("SUB3_HARD_PASS", "EXPONENTIAL_BEND_AT_N16384: " + detail)
    if HF_LO <= mean_max <= HF_HI:
        return ("SUB3_HARD_FAIL", "LINEAR_CAPACITY_AT_N16384: " + detail)
    return ("SUB3_MIDDLE_BAND", "PARTIAL: " + detail)


def run_sub3(smoke: bool, device: torch.device, out_dir: Path,
              mem_log: List[Dict]) -> Dict:
    print("\n========== SUB3: n_scaling_chunked_codebook_n16384 ==========", flush=True)
    # Smoke uses N=1024 to keep selftest fast and avoid heavy build
    N_use = 1024 if smoke else SUB3_N
    M_sweep = SUB3_M_SMOKE if smoke else SUB3_M_FULL
    seeds = SUB3_SEEDS_SMOKE if smoke else SUB3_SEEDS_FULL
    t0 = time.time()
    construct_ok = False
    codebook = None
    crashed = False
    crash_msg = ""
    cells: List[Dict] = []
    try:
        codebook, info = _kerdock_chunked(N_use, device, mem_log=mem_log)
        construct_ok = True
        print(f"  sub3 build OK codebook shape={tuple(codebook.shape)} dtype={codebook.dtype}",
              flush=True)
    except (RuntimeError, MemoryError) as e:
        crashed = True
        crash_msg = f"sub3 build CRASH: {e}"
        print(f"  sub3 BUILD CRASH: {e}", flush=True)
        if device.type == "cuda":
            torch.cuda.empty_cache()
    if construct_ok and codebook is not None:
        for seed in seeds:
            ck = f"sub3_seed{seed}"
            try:
                out = sub3_cell(codebook, N_use, M_sweep, seed, device)
                write_partial_key(out_dir, ck, out)
                cells.append(out)
                print(f"  sub3 seed={seed} max_M@95={out['max_M_at_95_recall']} "
                      f"by_M={out['retention_by_M']} "
                      f"({time.time()-t0:.1f}s)", flush=True)
            except (RuntimeError, MemoryError) as e:
                crashed = True
                crash_msg = f"sub3 seed={seed}: {e}"
                print(f"  sub3 seed={seed} CRASH: {e}", flush=True)
                if device.type == "cuda":
                    torch.cuda.empty_cache()
                break
    if codebook is not None:
        del codebook
    _free_gpu(device, "after_sub3", mem_log)
    verdict, vm = sub3_verdict(cells, construct_ok=construct_ok)
    return {"sub": "sub3", "cells": cells, "verdict": verdict,
            "verdict_msg": vm, "construct_ok": construct_ok,
            "crashed": crashed, "crash_msg": crash_msg,
            "elapsed_s": round(time.time() - t0, 2)}


# ----------------------- Composite verdict ------------------------------
def compute_composite_verdict(sub1, sub2, sub3) -> Tuple[str, str]:
    """Per pre-reg: HP if all 3 sub-tests hit their own HARD_PASS.
       HF if any crashed (failed to emit metrics).
       MIDDLE_BAND otherwise (metrics emitted but not all HP)."""
    any_crashed = sub1["crashed"] or sub2["crashed"] or sub3["crashed"]
    crash_detail = ""
    if sub1["crashed"]:
        crash_detail += f" sub1_crash={sub1['crash_msg']!r}"
    if sub2["crashed"]:
        crash_detail += f" sub2_crash={sub2['crash_msg']!r}"
    if sub3["crashed"]:
        crash_detail += f" sub3_crash={sub3['crash_msg']!r}"

    s1, s2, s3 = sub1["verdict"], sub2["verdict"], sub3["verdict"]
    detail = f"sub1={s1} sub2={s2} sub3={s3}{crash_detail}"

    if any_crashed:
        return ("RESCUE_HARD_FAIL", "INSTRUMENTATION_CRASH: " + detail)
    all_hp = ("HARD_PASS" in s1 and "HARD_PASS" in s2 and "HARD_PASS" in s3)
    if all_hp:
        return ("RESCUE_HARD_PASS", "ALL_SUB_PASS: " + detail)
    return ("RESCUE_MIDDLE_BAND", "METRICS_EMITTED_NOT_ALL_HP: " + detail)


def _instrumentation_selftest() -> None:
    # PROT-018: anchor _n8192 binds the composite's nominal N (sub1).
    assert SUB1_N == 8192, f"sub1 N must be 8192; got {SUB1_N}"
    # sub2 / sub3 N values are documented in script-level constants.
    assert SUB2_N == 4096
    assert SUB3_N == 16384

    # Composite verdict gates
    fake_hp_s1 = {"sub":"sub1","cells":[{}],"verdict":"SUB1_HARD_PASS",
                   "verdict_msg":"x","crashed":False,"crash_msg":"","elapsed_s":1}
    fake_hp_s2 = {"sub":"sub2","cells":[{}],"verdict":"SUB2_HARD_PASS",
                   "verdict_msg":"x","crashed":False,"crash_msg":"","elapsed_s":1}
    fake_hp_s3 = {"sub":"sub3","cells":[{}],"verdict":"SUB3_HARD_PASS",
                   "verdict_msg":"x","crashed":False,"crash_msg":"",
                   "construct_ok":True,"elapsed_s":1}
    v, _ = compute_composite_verdict(fake_hp_s1, fake_hp_s2, fake_hp_s3)
    assert "HARD_PASS" in v, f"composite HP gate: {v}"

    # HF: any crash
    fake_crash = dict(fake_hp_s2); fake_crash["crashed"] = True; fake_crash["crash_msg"] = "OOM"
    v, _ = compute_composite_verdict(fake_hp_s1, fake_crash, fake_hp_s3)
    assert "HARD_FAIL" in v, f"composite HF gate: {v}"

    # MB: all metrics, not all HP
    fake_mb_s1 = dict(fake_hp_s1); fake_mb_s1["verdict"] = "SUB1_MIDDLE_BAND"
    v, _ = compute_composite_verdict(fake_mb_s1, fake_hp_s2, fake_hp_s3)
    assert "MIDDLE_BAND" in v, f"composite MB gate: {v}"

    # Forward pass on CPU at smoke scale: just exercise sub2 inner kernel
    # (cheapest), to confirm imports + outer arithmetic functional.
    device = torch.device("cpu")
    out = sub2_cell(1024, 32, 17, device)
    assert out["sparse_retention"] is not None
    assert out["lat_ratio_sparse_over_dense"] > 0
    print(f"[selftest] gpu_large_n_rescue_serialized_v1_n8192 PASS "
          f"composite gates HP/HF/MB OK; sub2 inner kernel works",
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
    device = torch.device("cuda" if has_cuda else "cpu")
    smoke = args.smoke

    out_dir = get_output_dir()
    t0 = time.time()
    mem_log: List[Dict] = []
    mem_log.append(_mem_snapshot(device, "start"))
    print(f"[run] gpu_large_n_rescue_serialized_v1 smoke={smoke} "
          f"device={device.type} cuda={has_cuda}", flush=True)

    sub1 = run_sub1(smoke, device, out_dir, mem_log)
    sub2 = run_sub2(smoke, device, out_dir, mem_log)
    sub3 = run_sub3(smoke, device, out_dir, mem_log)

    composite_verdict, composite_vm = compute_composite_verdict(sub1, sub2, sub3)
    elapsed = round(time.time() - t0, 2)

    summary = {
        "anchor": "gpu_large_n_rescue_serialized_v1_n8192",
        "smoke": smoke,
        "device": device.type,
        "sub1": sub1, "sub2": sub2, "sub3": sub3,
        "mem_log": mem_log,
        "verdict": composite_verdict,
        "verdict_msg": composite_vm,
        "elapsed_s": elapsed,
    }
    payload = {"verdict": composite_verdict, "verdict_msg": composite_vm,
               "elapsed_s": elapsed, "summary": summary}
    with open(out_dir / "metrics.json", "w") as f:
        json.dump(payload, f, indent=2, default=str)
    print(f"\n[verdict] {composite_verdict}", flush=True)
    print(f"[verdict_msg] {composite_vm}", flush=True)
    print(f"[elapsed] {elapsed}s", flush=True)


if __name__ == "__main__":
    main()
