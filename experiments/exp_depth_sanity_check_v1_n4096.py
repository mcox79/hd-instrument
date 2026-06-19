"""G13a DEPTH SANITY CHECK v1 at N=4096 (Path D only).

CONTEXT (G13a, user revision):
  U1 tested depths in [10, 20, 30, 50] at N=4096 with 5 seeds.
  G7 tested depths in [10, 20, 30, 50] at higher M=24N-32N.
  Neither tested the gap depth in [75, 100, 150] at production M=8192.

PURPOSE:
  Cheap sanity that Path D does NOT have a surprising depth-50 cliff that
  U1 missed. Per-depth Path D accuracy at production operating point.
  Strategically: confirms current depth envelope, scopes G13b agentic.

SETUP:
  N=4096, BSC codebook, M=8192 (production operating point per user spec).
  K_paths=500. Path D ONLY. Depths in [75, 100, 150]. 5 seeds.
  3 cells x 5 seeds = 15 cell-seeds.

PRE-REGISTERED BANDS:
  HARD_PASS = mean accuracy >= 0.85 at ALL 3 depths in >=3/5 seeds.
              (no cliff between depth 50 and depth 150).
  HARD_FAIL = any depth has mean accuracy < 0.40 in >=3/5 seeds.
  MIDDLE_BAND = otherwise.

OOM CHECK:
  N=4096, M=8192, K_paths=500, depth=150:
    keys+vals     = 8192 * 4096 * 4 * 2  = 256 MiB
    W             = 4096^2 * 4           =  64 MiB
    codebook      = 4*4096 * 4096 * 4    = 256 MiB
    Path D per query: K_paths * depth src/dst pairs = 500 * 150 = 75000
      stacked tensors src_v/dst_v: 75000 * 4096 * 4 = ~1.2 GiB
  Peak ~ 2 GiB. OK on 8 GiB GPU.

TIMEOUT ESTIMATE:
  smoke_wall_s = ~50s (small-N path D dominates).
  Cells: 3 depths x 5 seeds = 15.
  FULL/smoke ratios: N 4 (1024->4096), seeds 5 (1->5), depths 3 (1->3),
  M 32 (256->8192).
  Path D scaling exp ~1.5 (matmul-dominant per cell).
  ceil(1.5 * 50 * 4^1.5 * 5 * 3) = ceil(9000) = 9000.
  Round up to 14400 for headroom and depth=150 long-tail.

PROT-018: _n4096 binds N = 4096.
PROT-020: torch+cuda.
PROT-021: per-seed checkpoint.

Anchor: depth_sanity_check_v1_n4096
Queue: overnight_queue
Pre-reg: preregs/2026-05-30_depth_sanity_check_v1_n4096.md
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
    build_shared, path_d_run,
)

_ck_path = REPO / "experiments" / "_seed_checkpoint.py"
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_g13a", _ck_path)
_ck = importlib.util.module_from_spec(_ck_spec)
_ck_spec.loader.exec_module(_ck)
list_completed_keys = _ck.list_completed_keys
write_partial_key   = _ck.write_partial_key
load_partial_key    = _ck.load_partial_key


# PROT-018: _n4096 binds N = 4096.
N = 4096
N_FULL  = N
N_SMOKE = 1024
assert N_FULL == 4096

M_FULL  = 8192        # production operating point
M_SMOKE = 256

K_PATHS = 500
K_PATHS_SMOKE = 40

DEPTHS_FULL  = [75, 100, 150]
DEPTHS_SMOKE = [3, 5]

SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]

N_QUERIES = 24
N_QUERIES_SMOKE = 8

HP_ACC = 0.85
HP_SEEDS_MIN = 3
HF_ACC = 0.40
HF_SEEDS_MIN = 3


def get_output_dir(default_name: str = "depth_sanity_check_v1_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def measure_cell(N_use: int, M: int, depth: int, K: int, n_queries: int,
                  seed: int, device: torch.device) -> Dict:
    """One (depth, seed) cell at N_use, M. Return Path D accuracy + latency."""
    codebook, W, key_idx, val_idx, relation = build_shared(N_use, M, seed, device)
    keys_list = list(relation.keys())
    n_starts = min(n_queries, len(keys_list))
    starts = torch.tensor(keys_list[:n_starts], dtype=torch.long, device=device)

    if device.type == "cuda":
        torch.cuda.synchronize()
    t0 = time.perf_counter()
    correct = path_d_run(codebook, W, starts, relation, depth, K, seed, N_use)
    if device.type == "cuda":
        torch.cuda.synchronize()
    lat_s = time.perf_counter() - t0

    acc = float(correct.mean().item()) if correct.numel() > 0 else 0.0
    n_valid = int(correct.numel())

    mem_peak = 0
    if device.type == "cuda":
        mem_peak = int(torch.cuda.max_memory_allocated(device))
        torch.cuda.empty_cache()
    del codebook, W

    return {
        "depth": int(depth),
        "M": int(M),
        "K_paths": int(K),
        "n_queries_valid": int(n_valid),
        "acc": round(acc, 5),
        "latency_s": round(lat_s, 4),
        "mem_peak_b": int(mem_peak),
    }


def compute_verdict(cells: List[Dict], depths: List[int]) -> Tuple[str, str]:
    if not cells:
        return ("G13A_INCONCLUSIVE", "no cells")

    # group by depth, count seeds meeting thresholds
    by_depth: Dict[int, List[Dict]] = {d: [] for d in depths}
    for c in cells:
        d = int(c["depth"])
        if d in by_depth:
            by_depth[d].append(c)

    summary_parts = []
    hp_all_depths = True
    hf_any_depth = False

    for d in depths:
        cs = by_depth[d]
        if not cs:
            hp_all_depths = False
            summary_parts.append(f"d{d}=NO_DATA")
            continue
        accs = [c["acc"] for c in cs]
        n_hp = sum(1 for a in accs if a >= HP_ACC)
        n_hf = sum(1 for a in accs if a < HF_ACC)
        mean_acc = sum(accs) / len(accs)
        summary_parts.append(
            f"d{d}: n={len(accs)} mean={mean_acc:.3f} "
            f"n_hp={n_hp}/{len(accs)} n_hf={n_hf}/{len(accs)}"
        )
        if n_hp < HP_SEEDS_MIN:
            hp_all_depths = False
        if n_hf >= HF_SEEDS_MIN:
            hf_any_depth = True

    detail = "; ".join(summary_parts)

    if hf_any_depth:
        return ("G13A_HARD_FAIL", f"DEPTH_CLIFF: {detail}")
    if hp_all_depths:
        return ("G13A_HARD_PASS", f"NO_CLIFF: {detail}")
    return ("G13A_MIDDLE_BAND", f"PARTIAL: {detail}")


def _instrumentation_selftest() -> None:
    """Assert metrics non-null + selectivity at small scale."""
    assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096, got {N_FULL}"
    device = torch.device("cpu")
    # Multi-scale smoke: Kerdock 4-coset requires N in {1024, 4096, 16384}.
    out_small = measure_cell(N_use=1024, M=64, depth=2, K=20, n_queries=4,
                              seed=17, device=device)
    assert out_small["acc"] is not None, "acc null at N=1024"
    assert out_small["n_queries_valid"] > 0, \
        "n_queries_valid=0 at smoke scale - validity filter eliminated all"
    assert out_small["latency_s"] > 0.0, "latency_s not measured"
    # 4x is N=4096 (production); restrict M to keep selftest fast on CPU
    out_4x = measure_cell(N_use=4096, M=64, depth=2, K=20, n_queries=4,
                           seed=17, device=device)
    assert out_4x["acc"] is not None, "acc null at N=4096"
    assert out_4x["n_queries_valid"] > 0, "validity at 4x smoke"
    print(f"[selftest] depth_sanity_check_v1_n4096 PASS "
          f"small_acc={out_small['acc']:.3f} 4x_acc={out_4x['acc']:.3f}",
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

    device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
    smoke = args.smoke
    N_cfg     = N_SMOKE if smoke else N_FULL
    M_cfg     = 256 if smoke else M_FULL
    K_cfg     = K_PATHS_SMOKE if smoke else K_PATHS
    depths    = DEPTHS_SMOKE if smoke else DEPTHS_FULL
    seeds     = SEEDS_SMOKE if smoke else SEEDS_FULL
    n_queries = N_QUERIES_SMOKE if smoke else N_QUERIES

    out_dir = get_output_dir()
    done = set(list_completed_keys(out_dir))
    t0 = time.time()
    print(f"[run] depth_sanity_check smoke={smoke} N={N_cfg} M={M_cfg} "
          f"depths={depths} K={K_cfg} seeds={seeds} n_queries={n_queries} "
          f"device={device.type} done={len(done)}", flush=True)

    cells: List[Dict] = []
    for depth in depths:
        for seed in seeds:
            ck = f"d{depth}_s{seed}"
            if ck in done:
                body = load_partial_key(out_dir, ck)
                if body is not None:
                    cells.append(body)
                    continue
            try:
                out = measure_cell(N_cfg, M_cfg, depth, K_cfg, n_queries,
                                    seed, device)
                write_partial_key(out_dir, ck, out)
                cells.append(out)
                print(f"  d={depth} s={seed} acc={out['acc']:.3f} "
                      f"lat={out['latency_s']:.2f}s ({time.time()-t0:.1f}s)",
                      flush=True)
            except (RuntimeError, MemoryError) as e:
                print(f"  d={depth} s={seed} FAILED: {e}", flush=True)
                if device.type == "cuda":
                    torch.cuda.empty_cache()

    verdict, vm = compute_verdict(cells, depths)
    elapsed = round(time.time() - t0, 2)
    summary = {
        "anchor": "depth_sanity_check_v1_n4096",
        "N": N_cfg, "smoke": smoke, "M": M_cfg, "K_paths": K_cfg,
        "depths": depths, "seeds": seeds, "n_queries": n_queries,
        "cells": cells, "verdict": verdict, "verdict_msg": vm,
        "elapsed_s": elapsed,
    }
    payload = {"verdict": verdict, "verdict_msg": vm,
               "elapsed_s": elapsed, "summary": summary}
    with open(out_dir / "metrics.json", "w") as f:
        json.dump(payload, f, indent=2, default=str)
    print(f"\n[verdict] {verdict}\n[verdict_msg] {vm}\n[elapsed] {elapsed}s",
          flush=True)


if __name__ == "__main__":
    main()
