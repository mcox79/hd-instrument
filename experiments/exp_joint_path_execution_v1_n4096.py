"""S14 JOINT PATH EXECUTION v1 at N=4096 (E6.5 baseline).

Joint vs sequential execution of multi-hop paths. Measure baseline for
downstream composition / LLM-orchestration parallel execution.

SETUP:
  Sequential: run B, then D, then E (current default)
  Joint: run all 3 in parallel within one process (shared substrate
         state, shared codebook, batch where possible).

PRE-REGISTERED BANDS:
  HP = joint execution >=70% speedup vs sequential AND memory <=2x
       AND accuracy preserved.
  HF = joint shows no speedup OR memory explodes >5x.
  MB = otherwise.

PROT-018: _n4096.
Anchor: joint_path_execution_v1_n4096
Queue: overnight_queue
Pre-reg: preregs/2026-05-30_joint_path_execution_v1_n4096.md
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import gc
import importlib.util
import json
import os
import time
import tracemalloc
from pathlib import Path
from typing import Dict, List, Tuple

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from experiments._multi_hop_mechanisms import (  # noqa: E402
    build_shared, run_all_paths_sequential, run_all_paths_joint,
)

_ck_path = REPO / "experiments" / "_seed_checkpoint.py"
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_s14", _ck_path)
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
K_PATHS_SMOKE = 50
SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]
N_PATHS = 32

HP_SPEEDUP = 0.70   # >=70% speedup (joint time <= 30% of sequential)
HP_MEM_AMP = 2.0
HF_MEM_AMP = 5.0
HP_ACC_DELTA = 0.05


def get_output_dir(default_name: str = "joint_path_execution_v1_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _peak_mem_bytes(device: torch.device) -> int:
    if device.type == "cuda":
        return int(torch.cuda.max_memory_allocated(device))
    cur, peak = tracemalloc.get_traced_memory()
    return int(peak)


def _reset_mem(device: torch.device) -> None:
    if device.type == "cuda":
        torch.cuda.empty_cache()
        torch.cuda.reset_peak_memory_stats(device)
    gc.collect()
    if tracemalloc.is_tracing():
        tracemalloc.stop()
    tracemalloc.start()


def measure_seed(N_use: int, M: int, depth: int, K: int, seed: int,
                  device: torch.device) -> Dict:
    codebook, W, key_idx, val_idx, relation = build_shared(N_use, M, seed, device)

    _reset_mem(device)
    t0 = time.perf_counter_ns()
    seq = run_all_paths_sequential(codebook, W, key_idx, val_idx, relation,
                                     depth, N_PATHS, seed, N_use, K_paths=K)
    seq_total_ns = time.perf_counter_ns() - t0
    seq_mem_peak = _peak_mem_bytes(device)

    _reset_mem(device)
    t1 = time.perf_counter_ns()
    joint = run_all_paths_joint(codebook, W, key_idx, val_idx, relation,
                                  depth, N_PATHS, seed, N_use, K_paths=K)
    joint_total_ns = time.perf_counter_ns() - t1
    joint_mem_peak = _peak_mem_bytes(device)

    if seq_total_ns > 0:
        speedup_frac = 1.0 - (joint_total_ns / seq_total_ns)
    else:
        speedup_frac = 0.0
    mem_amp = joint_mem_peak / max(1, seq_mem_peak)

    # Accuracy preservation
    acc_delta_b = abs(seq.get("path_b_acc", 0) - joint.get("path_b_acc", 0))
    acc_delta_d = abs(seq.get("path_d_acc", 0) - joint.get("path_d_acc", 0))
    acc_delta_e = abs(seq.get("path_e_auc", 0.5) - joint.get("path_e_auc", 0.5))
    max_acc_delta = max(acc_delta_b, acc_delta_d, acc_delta_e)

    del codebook, W
    if device.type == "cuda":
        torch.cuda.empty_cache()
    if tracemalloc.is_tracing():
        tracemalloc.stop()

    return {"seed": int(seed), "M": int(M), "depth": int(depth), "K": int(K),
            "seq_total_ns": int(seq_total_ns),
            "joint_total_ns": int(joint_total_ns),
            "seq_mem_peak_b": int(seq_mem_peak),
            "joint_mem_peak_b": int(joint_mem_peak),
            "speedup_frac": round(speedup_frac, 4),
            "mem_amp": round(mem_amp, 4),
            "acc_delta_b": round(acc_delta_b, 5),
            "acc_delta_d": round(acc_delta_d, 5),
            "acc_delta_e": round(acc_delta_e, 5),
            "max_acc_delta": round(max_acc_delta, 5)}


def compute_verdict(cells: List[Dict]) -> Tuple[str, str]:
    if not cells:
        return ("S14_INCONCLUSIVE", "no cells")

    mean_sp = sum(c["speedup_frac"] for c in cells) / len(cells)
    max_amp = max(c["mem_amp"] for c in cells)
    max_delta = max(c["max_acc_delta"] for c in cells)
    detail = (f"mean_speedup_frac={mean_sp:.3f} max_mem_amp={max_amp:.2f} "
              f"max_acc_delta={max_delta:.4f}")

    if mean_sp >= HP_SPEEDUP and max_amp <= HP_MEM_AMP and max_delta <= HP_ACC_DELTA:
        return ("S14_HARD_PASS", "JOINT_FASTER: " + detail)
    if mean_sp <= 0.0 or max_amp >= HF_MEM_AMP:
        return ("S14_HARD_FAIL", "JOINT_SLOWER_OR_BLOATED: " + detail)
    return ("S14_MIDDLE_BAND", "PARTIAL: " + detail)


def _instrumentation_selftest() -> None:
    assert N_FULL == 4096
    device = torch.device("cpu")
    out = measure_seed(N_SMOKE, 64, 2, 20, 17, device)
    assert out["seq_total_ns"] > 0 and out["joint_total_ns"] > 0
    print(f"[selftest] joint_path_execution_v1_n4096 PASS "
          f"seq={out['seq_total_ns']/1e6:.1f}ms "
          f"joint={out['joint_total_ns']/1e6:.1f}ms "
          f"speedup={out['speedup_frac']:.3f} "
          f"amp={out['mem_amp']:.2f}", flush=True)


_instrumentation_selftest()


def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--self-test", action="store_true", dest="self_test")
    args = p.parse_args()
    if args.self_test:
        sys.exit(0)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    smoke = args.smoke
    N_cfg = N_SMOKE if smoke else N_FULL
    M = M_SMOKE if smoke else M_PROD
    depth = DEPTH_SMOKE if smoke else DEPTH
    K = K_PATHS_SMOKE if smoke else K_PATHS
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL

    out_dir = get_output_dir()
    done = set(list_completed_keys(out_dir))
    t0 = time.time()
    print(f"[run] joint_path_execution smoke={smoke} N={N_cfg} M={M} "
          f"depth={depth} K={K} seeds={seeds} done={len(done)} "
          f"device={device.type}", flush=True)

    cells: List[Dict] = []
    for seed in seeds:
        ck = f"seed{seed}"
        if ck in done:
            body = load_partial_key(out_dir, ck)
            if body is not None:
                cells.append(body); continue
        try:
            out = measure_seed(N_cfg, M, depth, K, seed, device)
            write_partial_key(out_dir, ck, out)
            cells.append(out)
            print(f"  s={seed} sp={out['speedup_frac']:.3f} "
                  f"amp={out['mem_amp']:.2f} ({time.time()-t0:.1f}s)", flush=True)
        except (RuntimeError, MemoryError) as e:
            print(f"  s={seed} FAILED: {e}", flush=True)
            if device.type == "cuda":
                torch.cuda.empty_cache()

    verdict, vm = compute_verdict(cells)
    elapsed = round(time.time() - t0, 2)
    summary = {"anchor": "joint_path_execution_v1_n4096",
               "N": N_cfg, "smoke": smoke,
               "M": M, "depth": depth, "K_paths": K, "seeds": seeds,
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
