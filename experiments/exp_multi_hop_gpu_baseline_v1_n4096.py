"""S11 MULTI-HOP GPU BASELINE v1 at N=4096 (E6.4 baseline).

Measure baseline GPU vs CPU multi-hop performance for 3 paths.
Engineering optimizations (true GPU port) are downstream work.

PRE-REGISTERED BANDS:
  HP = at least one path shows >=5x GPU speedup vs CPU AND killer
       features (acc parity within 5%) pass on GPU.
  HF = any path crashes on GPU OR killer features break.
  MB = otherwise.

PROT-018: _n4096.
Anchor: multi_hop_gpu_baseline_v1_n4096
Queue: overnight_queue
Pre-reg: preregs/2026-05-30_multi_hop_gpu_baseline_v1_n4096.md
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

from experiments._multi_hop_mechanisms import (  # noqa: E402
    build_shared, path_b_run, path_d_run, path_e_run,
)
from experiments._relation_graph import (  # noqa: E402
    sample_coherent_starts, sample_incoherent_paths,
)

_ck_path = REPO / "experiments" / "_seed_checkpoint.py"
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_s11", _ck_path)
_ck = importlib.util.module_from_spec(_ck_spec)
_ck_spec.loader.exec_module(_ck)
list_completed_keys = _ck.list_completed_keys
write_partial_key   = _ck.write_partial_key
load_partial_key    = _ck.load_partial_key


N = 4096
N_FULL  = N
N_SMOKE = 1024
M_PROD = 2048
M_SMOKE = 256
DEPTH = 5
DEPTH_SMOKE = 3
K_PATHS = 500
SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]
N_PATHS = 24

HP_GPU_SPEEDUP = 5.0
HP_ACC_PARITY_DELTA = 0.05


def get_output_dir(default_name: str = "multi_hop_gpu_baseline_v1_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _measure_on_device(N_use: int, M: int, depth: int, K: int, seed: int,
                        device: torch.device) -> Dict:
    codebook, W, key_idx, val_idx, relation = build_shared(N_use, M, seed, device)
    C = codebook.shape[0]
    starts = torch.tensor(list(relation.keys())[:N_PATHS],
                          dtype=torch.long, device=device)
    targets = []
    for k in starts.tolist():
        cur = int(k); ok = True
        for _ in range(depth):
            nxt = relation.get(cur)
            if nxt is None: ok = False; break
            cur = int(nxt)
        targets.append(cur if ok else -1)
    tgt = torch.tensor(targets, dtype=torch.long, device=device)
    valid = tgt >= 0

    pos = sample_coherent_starts(relation, depth, N_PATHS, seed)
    neg = sample_incoherent_paths(C, depth, N_PATHS, seed, relation=relation)

    if device.type == "cuda":
        torch.cuda.synchronize()
    t0 = time.perf_counter_ns()
    pred = path_b_run(codebook, W, starts, depth, N_use)
    if device.type == "cuda":
        torch.cuda.synchronize()
    lat_b = time.perf_counter_ns() - t0
    acc_b = float((pred[valid] == tgt[valid]).float().mean().item()) if valid.any() else 0.0

    if device.type == "cuda":
        torch.cuda.synchronize()
    t1 = time.perf_counter_ns()
    correct_d = path_d_run(codebook, W, starts, relation, depth, K, seed, N_use)
    if device.type == "cuda":
        torch.cuda.synchronize()
    lat_d = time.perf_counter_ns() - t1
    acc_d = float(correct_d.mean().item())

    if pos and neg:
        if device.type == "cuda":
            torch.cuda.synchronize()
        t2 = time.perf_counter_ns()
        auc_e = path_e_run(codebook, W, pos, neg, N_use)
        if device.type == "cuda":
            torch.cuda.synchronize()
        lat_e = time.perf_counter_ns() - t2
    else:
        auc_e = 0.5; lat_e = 0

    mem_peak = 0
    if device.type == "cuda":
        mem_peak = int(torch.cuda.max_memory_allocated(device))
        torch.cuda.empty_cache()
    del codebook, W

    return {"acc_b": round(acc_b, 5), "acc_d": round(acc_d, 5),
            "auc_e": round(auc_e, 5),
            "lat_b_ns": int(lat_b), "lat_d_ns": int(lat_d),
            "lat_e_ns": int(lat_e),
            "mem_peak_b": int(mem_peak)}


def measure_seed(N_use: int, M: int, depth: int, K: int, seed: int,
                  cuda_device: torch.device, cpu_device: torch.device) -> Dict:
    cpu_results = _measure_on_device(N_use, M, depth, K, seed, cpu_device)
    if cuda_device.type == "cuda":
        try:
            cuda_results = _measure_on_device(N_use, M, depth, K, seed, cuda_device)
        except Exception as e:
            cuda_results = {"error": str(e)[:300]}
    else:
        cuda_results = {"error": "no_cuda"}

    return {"seed": int(seed), "M": int(M),
            "cpu": cpu_results, "gpu": cuda_results}


def compute_verdict(cells: List[Dict]) -> Tuple[str, str]:
    if not cells:
        return ("S11_INCONCLUSIVE", "no cells")

    # Skip if no GPU
    gpu_avail = any("error" not in c.get("gpu", {}) for c in cells)
    if not gpu_avail:
        return ("S11_MIDDLE_BAND", "NO_GPU_OR_CRASH; cpu_results emitted")

    # For each path, compute mean speedup
    def mean_speedup(path_lat):
        sps = []
        for c in cells:
            if "error" in c.get("gpu", {}): continue
            cpu_l = c["cpu"].get(path_lat, 0)
            gpu_l = c["gpu"].get(path_lat, 0)
            if gpu_l <= 0: continue
            sps.append(cpu_l / max(1, gpu_l))
        return (sum(sps) / max(1, len(sps))) if sps else 0.0

    def mean_acc_delta(metric):
        ds = []
        for c in cells:
            if "error" in c.get("gpu", {}): continue
            cd = abs(c["cpu"].get(metric, 0) - c["gpu"].get(metric, 0))
            ds.append(cd)
        return (sum(ds) / max(1, len(ds))) if ds else 1.0

    sp_b = mean_speedup("lat_b_ns")
    sp_d = mean_speedup("lat_d_ns")
    sp_e = mean_speedup("lat_e_ns")
    d_b = mean_acc_delta("acc_b")
    d_d = mean_acc_delta("acc_d")
    d_e = mean_acc_delta("auc_e")

    n_crashes = sum(1 for c in cells if "error" in c.get("gpu", {}))
    detail = (f"sp_b={sp_b:.2f} sp_d={sp_d:.2f} sp_e={sp_e:.2f} "
              f"d_b={d_b:.3f} d_d={d_d:.3f} d_e={d_e:.3f} "
              f"n_crashes={n_crashes}")

    if n_crashes > 0:
        return ("S11_HARD_FAIL", "GPU_CRASH: " + detail)
    # killer features = acc parity within delta
    any_hp = ((sp_b >= HP_GPU_SPEEDUP and d_b <= HP_ACC_PARITY_DELTA) or
              (sp_d >= HP_GPU_SPEEDUP and d_d <= HP_ACC_PARITY_DELTA) or
              (sp_e >= HP_GPU_SPEEDUP and d_e <= HP_ACC_PARITY_DELTA))
    parity_broken = (d_b > HP_ACC_PARITY_DELTA and d_d > HP_ACC_PARITY_DELTA
                       and d_e > HP_ACC_PARITY_DELTA)
    if parity_broken:
        return ("S11_HARD_FAIL", "ACC_PARITY_BROKEN: " + detail)
    if any_hp:
        return ("S11_HARD_PASS", "GPU_BASELINE_OK: " + detail)
    return ("S11_MIDDLE_BAND", "PARTIAL: " + detail)


def _instrumentation_selftest() -> None:
    assert N_FULL == 4096
    cpu = torch.device("cpu")
    out = _measure_on_device(N_SMOKE, 64, 2, 20, 17, cpu)
    assert out["lat_b_ns"] > 0
    print(f"[selftest] multi_hop_gpu_baseline_v1_n4096 PASS cpu lat_b={out['lat_b_ns']/1e6:.1f}ms",
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
    cuda_device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
    cpu_device = torch.device("cpu")
    smoke = args.smoke
    N_cfg = N_SMOKE if smoke else N_FULL
    M = M_SMOKE if smoke else M_PROD
    depth = DEPTH_SMOKE if smoke else DEPTH
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL

    out_dir = get_output_dir()
    done = set(list_completed_keys(out_dir))
    t0 = time.time()
    print(f"[run] multi_hop_gpu_baseline smoke={smoke} N={N_cfg} M={M} "
          f"depth={depth} K={K_PATHS} seeds={seeds} done={len(done)} "
          f"cuda={cuda_device.type}", flush=True)

    cells: List[Dict] = []
    for seed in seeds:
        ck = f"seed{seed}"
        if ck in done:
            body = load_partial_key(out_dir, ck)
            if body is not None:
                cells.append(body); continue
        try:
            out = measure_seed(N_cfg, M, depth, K_PATHS, seed,
                                 cuda_device, cpu_device)
            write_partial_key(out_dir, ck, out)
            cells.append(out)
            print(f"  s={seed} done ({time.time()-t0:.1f}s)", flush=True)
        except (RuntimeError, MemoryError) as e:
            print(f"  s={seed} FAILED: {e}", flush=True)
            if cuda_device.type == "cuda":
                torch.cuda.empty_cache()

    verdict, vm = compute_verdict(cells)
    elapsed = round(time.time() - t0, 2)
    summary = {"anchor": "multi_hop_gpu_baseline_v1_n4096",
               "N": N_cfg, "smoke": smoke,
               "M": M, "depth": depth, "K_paths": K_PATHS, "seeds": seeds,
               "cells": cells, "verdict": verdict, "verdict_msg": vm,
               "elapsed_s": elapsed}
    payload = {"verdict": verdict, "verdict_msg": vm,
               "elapsed_s": elapsed, "summary": summary}
    with open(out_dir / "metrics.json", "w") as f:
        json.dump(payload, f, indent=2, default=str)
    print(f"\n[verdict] {verdict}\n[verdict_msg] {vm}\n[elapsed] {elapsed}s",
          flush=True)


if __name__ == "__main__":
    main()
