"""S3 MULTI-HOP MEMORY EFFICIENCY v1 at N=4096 (E1.4).

Memory profile for multi-hop. Detect non-obvious memory cliffs at
production scale.

SCIENTIFIC QUESTION:
  Does any path's peak memory exceed 4x single-hop peak? Are there
  within-operation memory spikes >2x?

PRE-REGISTERED BANDS:
  HP = no path exceeds 4x single-hop peak AND no >2x within-op spikes.
  HF = >10x single-hop OR spikes suggesting cliffs.
  MB = moderate amplification.

PROT-018: _n4096.
Anchor: multi_hop_memory_efficiency_v1_n4096
Queue: overnight_queue
Pre-reg: preregs/2026-05-30_multi_hop_memory_efficiency_v1_n4096.md
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
    build_shared, path_b_run, path_d_run, path_e_run,
)
from experiments._relation_graph import (  # noqa: E402
    sample_coherent_starts, sample_incoherent_paths,
)

_ck_path = REPO / "experiments" / "_seed_checkpoint.py"
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_s3", _ck_path)
_ck = importlib.util.module_from_spec(_ck_spec)
_ck_spec.loader.exec_module(_ck)
list_completed_keys = _ck.list_completed_keys
write_partial_key   = _ck.write_partial_key
load_partial_key    = _ck.load_partial_key


N = 4096
N_FULL  = N
N_SMOKE = 1024
M_PROD  = 8192
M_SMOKE = 256
DEPTH_PROD  = 5
K_PATHS_PROD = 1000
DEPTH_SMOKE = 3
K_PATHS_SMOKE = 50
SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]
N_PATHS = 32

HP_AMP_FACTOR = 4.0
HF_AMP_FACTOR = 10.0
HP_SPIKE_RATIO = 2.0


def get_output_dir(default_name: str = "multi_hop_memory_efficiency_v1_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _peak_mem_bytes(device: torch.device) -> int:
    if device.type == "cuda":
        return int(torch.cuda.max_memory_allocated(device))
    # CPU: rely on tracemalloc peak
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


def measure_cell(N_use: int, M: int, depth: int, K_paths: int,
                  seed: int, device: torch.device) -> Dict:
    codebook, W, key_idx, val_idx, relation = build_shared(N_use, M, seed, device)
    starts = torch.tensor(list(relation.keys())[:N_PATHS],
                          dtype=torch.long, device=device)
    pos = sample_coherent_starts(relation, depth, N_PATHS, seed)
    neg = sample_incoherent_paths(codebook.shape[0], depth, N_PATHS,
                                    seed, relation=relation)

    # Single-hop baseline (path B at depth 1)
    _reset_mem(device)
    _ = path_b_run(codebook, W, starts, 1, N_use)
    single_hop_peak = _peak_mem_bytes(device)

    _reset_mem(device)
    _ = path_b_run(codebook, W, starts, depth, N_use)
    b_peak = _peak_mem_bytes(device)

    _reset_mem(device)
    _ = path_d_run(codebook, W, starts, relation, depth, K_paths, seed, N_use)
    d_peak = _peak_mem_bytes(device)

    _reset_mem(device)
    if pos and neg:
        _ = path_e_run(codebook, W, pos, neg, N_use)
        e_peak = _peak_mem_bytes(device)
    else:
        e_peak = 0

    amp_b = b_peak / max(1, single_hop_peak)
    amp_d = d_peak / max(1, single_hop_peak)
    amp_e = e_peak / max(1, single_hop_peak)

    del codebook, W
    if device.type == "cuda":
        torch.cuda.empty_cache()
    if tracemalloc.is_tracing():
        tracemalloc.stop()

    return {
        "M": int(M), "depth": int(depth), "K_paths": int(K_paths),
        "seed": int(seed),
        "single_hop_peak_b": int(single_hop_peak),
        "path_b_peak_b": int(b_peak),
        "path_d_peak_b": int(d_peak),
        "path_e_peak_b": int(e_peak),
        "amp_b": round(amp_b, 4),
        "amp_d": round(amp_d, 4),
        "amp_e": round(amp_e, 4),
    }


def compute_verdict(cells: List[Dict]) -> Tuple[str, str]:
    if not cells:
        return ("S3_INCONCLUSIVE", "no cells")

    max_amp_b = max(c["amp_b"] for c in cells)
    max_amp_d = max(c["amp_d"] for c in cells)
    max_amp_e = max(c["amp_e"] for c in cells)
    max_amp = max(max_amp_b, max_amp_d, max_amp_e)

    detail = (f"max_amp B={max_amp_b:.2f} D={max_amp_d:.2f} E={max_amp_e:.2f} "
              f"n_cells={len(cells)}")

    if max_amp >= HF_AMP_FACTOR:
        return ("S3_HARD_FAIL", "MEMORY_CLIFF: " + detail)
    if max_amp <= HP_AMP_FACTOR:
        return ("S3_HARD_PASS", "MEMORY_BOUNDED: " + detail)
    return ("S3_MIDDLE_BAND", "MODERATE_AMP: " + detail)


def _instrumentation_selftest() -> None:
    assert N_FULL == 4096
    device = torch.device("cpu")
    out = measure_cell(N_SMOKE, M_SMOKE, DEPTH_SMOKE, K_PATHS_SMOKE, 17, device)
    assert out["single_hop_peak_b"] >= 0
    assert out["path_b_peak_b"] >= 0
    print(f"[selftest] multi_hop_memory_efficiency_v1_n4096 PASS "
          f"amp_b={out['amp_b']:.2f} amp_d={out['amp_d']:.2f} "
          f"amp_e={out['amp_e']:.2f}", flush=True)


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
    depth = DEPTH_SMOKE if smoke else DEPTH_PROD
    K = K_PATHS_SMOKE if smoke else K_PATHS_PROD
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL

    out_dir = get_output_dir()
    done = set(list_completed_keys(out_dir))
    t0 = time.time()
    print(f"[run] multi_hop_memory_efficiency smoke={smoke} N={N_cfg} "
          f"M={M} depth={depth} K={K} seeds={seeds} "
          f"done={len(done)} device={device.type}", flush=True)

    cells: List[Dict] = []
    for seed in seeds:
        ck = f"M{M}_d{depth}_K{K}_seed{seed}"
        if ck in done:
            body = load_partial_key(out_dir, ck)
            if body is not None:
                cells.append(body); continue
        try:
            out = measure_cell(N_cfg, M, depth, K, seed, device)
            write_partial_key(out_dir, ck, out)
            cells.append(out)
            print(f"  s={seed} amp_b={out['amp_b']:.2f} amp_d={out['amp_d']:.2f} "
                  f"amp_e={out['amp_e']:.2f} ({time.time()-t0:.1f}s)", flush=True)
        except (RuntimeError, MemoryError) as e:
            print(f"  s={seed} FAILED: {e}", flush=True)
            if device.type == "cuda":
                torch.cuda.empty_cache()

    verdict, vm = compute_verdict(cells)
    elapsed = round(time.time() - t0, 2)
    summary = {"anchor": "multi_hop_memory_efficiency_v1_n4096",
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
