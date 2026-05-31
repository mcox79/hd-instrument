"""G1 PATH D LATENCY PROFILING v1 at N=4096.

CONTEXT (Batch 1 #1):
  Path D is production-default per v289. S1 already identified
  time_posterior_max as suspect bottleneck. This anchor characterizes the
  full per-operation latency breakdown across (M, depth, K) at production
  operating points and identifies the dominant op per cell. Prerequisite
  for Testbed Test 10 (posterior maximization optimization).

SCIENTIFIC QUESTION:
  Across M in {2048, 8192, 16384} x depth in {3, 5, 10, 15} x K_paths in
  {100, 500, 1000} at N=4096 BSC, what operation dominates Path D wall_s
  in each cell, and is the dominance pattern stable across seeds/families?

PER-CELL CHECKPOINT (PROT-021): yes.

INSTRUMENTATION (time.perf_counter_ns wrapping each op via TimingTrace):
  - t_enumerate_paths          (path enumeration / decoy sampling)
  - t_likelihood_query_per_hop (per-hop substrate W-query + sim)
  - t_bayesian_update          (log-posterior accumulation)
  - t_posterior_max            (argmax)
  - mem_alloc per cell         (tracemalloc current + torch.cuda.memory_allocated)
  - dominant_op (>50% wall)    (string label per cell)

PRE-REGISTERED BANDS:
  HP = dominant_op identified in >=80% of cells (>50% of wall_s) AND
       dominance pattern is consistent (same dominant op across same
       M/depth/K family, mode_frac >= 0.6 per family)
  HF = instrumentation noise dominates: per-op times below resolution
       (max op total < 10x per-op-call minimum) OR seed-disagreement >=0.5
       (same family disagrees on dominant op across half of seeds)
  MB = otherwise

OOM CHECK:
  N=4096. M max=16384. W = 4096x4096 float32 = 64 MiB. Codebook C=4N=16384 x
  4096 = 256 MiB. K=1000 path enum = ~4 MiB. Peak ~350 MiB. Fits 8 GiB GPU.

TIMEOUT ESTIMATE:
  Per cell: depth=15 K=1000 N_STARTS=16 -> 16 * 1000 = 16k path scores;
  approx 30-60s per cell. 36 cells * 5 seeds = 180 cell-seeds.
  Mid-estimate 40s/cell-seed * 180 = 7200s. Worst-case 90s/cell-seed = 16200s
  -> exceeds 14400 hard cap; reduce headroom by capping at 21600 per user
  spec for Batch 1 #1 explicit budget.

N-suffix: _n4096 (PROT-018).
Anchor: path_d_latency_profiling_v1_n4096
Queue: overnight_queue
Pre-reg: preregs/2026-05-30_path_d_latency_profiling_v1_n4096.md
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import importlib.util
import json
import os
import time
import tracemalloc
from collections import Counter
from pathlib import Path
from typing import Dict, List, Tuple

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from experiments._metric_battery import make_substrate  # noqa: E402
from experiments._relation_graph import build_relation_facts  # noqa: E402
from experiments._multi_hop_mechanisms import (  # noqa: E402
    path_d_run,
    TimingTrace,
)

_ck_path = REPO / "experiments" / "_seed_checkpoint.py"
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_g1", _ck_path)
_ck = importlib.util.module_from_spec(_ck_spec)
_ck_spec.loader.exec_module(_ck)
list_completed_keys = _ck.list_completed_keys
write_partial_key   = _ck.write_partial_key
load_partial_key    = _ck.load_partial_key


# PROT-018: _n4096 binds N = 4096
N = 4096
N_FULL  = N
N_SMOKE = 1024
assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

M_GRID_FULL  = [2048, 8192, 16384]
M_GRID_SMOKE = [512, 1024]
DEPTH_GRID_FULL  = [3, 5, 10, 15]
DEPTH_GRID_SMOKE = [3, 5]
K_GRID_FULL  = [100, 500, 1000]
K_GRID_SMOKE = [20, 50]
SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]
N_STARTS = 16

BETA_D = 4.0

# Pre-registered thresholds
HP_DOM_FRAC = 0.80   # fraction of cells where a dominant op > 50% wall is found
HP_FAMILY_MODE_FRAC = 0.60  # within (M, K) family across depths, mode dominance fraction
HF_RESOLUTION_RATIO = 10  # if max-op-total < HF_RESOLUTION_RATIO * min-op-call -> noise-dominated
HF_SEED_DISAGREE = 0.50


def get_output_dir(default_name: str = "path_d_latency_profiling_v1_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def build_substrate_with_relation(N_use: int, M: int, seed: int,
                                    device: torch.device):
    codebook, _W, _keys, _vals, _ki, _vi = make_substrate(N_use, M, seed, device)
    C = codebook.shape[0]
    M_eff = min(M, C)
    key_idx, val_idx, relation = build_relation_facts(
        n_idx=C, M=M_eff, seed=seed, device=device, closed=True)
    keys_vec = codebook[key_idx]
    vals_vec = codebook[val_idx]
    W = (vals_vec.T @ keys_vec) / N_use
    return codebook, W, key_idx, val_idx, relation


def measure_cell(N_use: int, M: int, depth: int, K_paths: int,
                  seed: int, device: torch.device) -> Dict:
    tracemalloc.start()
    cuda_mem_start = (torch.cuda.memory_allocated(device)
                       if device.type == "cuda" else 0)

    codebook, W, key_idx, val_idx, relation = build_substrate_with_relation(
        N_use, M, seed, device)
    starts_list = list(relation.keys())[:N_STARTS]
    if not starts_list:
        cur_mem, peak_mem = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        del codebook, W
        if device.type == "cuda":
            torch.cuda.empty_cache()
        return {"M": int(M), "depth": int(depth), "K_paths": int(K_paths),
                "seed": int(seed), "accuracy": 0.0, "n_eval": 0,
                "wall_s": 0.0, "op_breakdown_ns": {}, "dominant_op": "none",
                "dominant_frac": 0.0,
                "mem_cpu_peak_mib": round(peak_mem / 1024 / 1024, 3),
                "mem_cuda_delta_mib": 0.0}

    starts = torch.tensor(starts_list, dtype=torch.long, device=device)
    trace = TimingTrace()
    t0 = time.perf_counter_ns()
    correct = path_d_run(codebook, W, starts, relation, depth, K_paths,
                          seed, N_use, beta=BETA_D, trace=trace)
    wall_ns = time.perf_counter_ns() - t0
    acc = float(correct.mean().item())
    n_eval = int(correct.shape[0])

    cur_mem, peak_mem = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    cuda_mem_peak = (torch.cuda.max_memory_allocated(device)
                      if device.type == "cuda" else 0)
    cuda_delta = cuda_mem_peak - cuda_mem_start

    op_summary = trace.summary()
    dom_op, dom_frac = trace.dominant_op()

    del codebook, W
    if device.type == "cuda":
        torch.cuda.empty_cache()
        torch.cuda.reset_peak_memory_stats(device)

    return {"M": int(M), "depth": int(depth), "K_paths": int(K_paths),
            "seed": int(seed), "accuracy": round(acc, 5), "n_eval": n_eval,
            "wall_s": round(wall_ns / 1e9, 5),
            "op_breakdown_ns": op_summary,
            "dominant_op": dom_op,
            "dominant_frac": round(dom_frac, 4),
            "mem_cpu_peak_mib": round(peak_mem / 1024 / 1024, 3),
            "mem_cuda_delta_mib": round(cuda_delta / 1024 / 1024, 3)}


def compute_verdict(cells: List[Dict]) -> Tuple[str, str]:
    if not cells:
        return ("G1_INCONCLUSIVE", "no cells")

    n_cells = len(cells)
    # 1) HP fraction: dominant_op identified (>50%) per cell
    n_with_dom = sum(1 for c in cells if c["dominant_frac"] > 0.50)
    dom_fraction = n_with_dom / n_cells

    # 2) Family consistency: group by (M, K), within each family check
    #    whether the dominant_op mode covers >= HP_FAMILY_MODE_FRAC across
    #    its depth-and-seed members.
    families: Dict[Tuple[int, int], List[str]] = {}
    for c in cells:
        families.setdefault((c["M"], c["K_paths"]), []).append(c["dominant_op"])
    family_mode_fracs: List[float] = []
    for k, ops in families.items():
        if not ops:
            continue
        cnt = Counter(ops)
        mode_op, mode_n = cnt.most_common(1)[0]
        family_mode_fracs.append(mode_n / len(ops))
    mean_family_mode_frac = (sum(family_mode_fracs) / len(family_mode_fracs)
                              if family_mode_fracs else 0.0)

    # 3) Resolution sanity for HF: any cell with all op totals trivially small?
    res_violations = 0
    for c in cells:
        ops = c.get("op_breakdown_ns", {})
        if not ops:
            continue
        totals = [v.get("total_ns", 0) for v in ops.values()]
        per_calls = [v.get("mean_ns", 1) for v in ops.values()]
        if totals and per_calls:
            max_total = max(totals)
            min_call = max(1, min(per_calls))
            if max_total < HF_RESOLUTION_RATIO * min_call:
                res_violations += 1
    res_violation_frac = res_violations / n_cells

    # 4) Seed-disagreement HF: per (M, depth, K) check whether seeds agree
    #    on dominant op. Disagreement frac = 1 - mode_frac per family.
    by_full: Dict[Tuple[int, int, int], List[str]] = {}
    for c in cells:
        by_full.setdefault((c["M"], c["depth"], c["K_paths"]), []).append(
            c["dominant_op"])
    seed_disagree_fracs: List[float] = []
    for k, ops in by_full.items():
        if not ops:
            continue
        cnt = Counter(ops)
        _, mode_n = cnt.most_common(1)[0]
        seed_disagree_fracs.append(1.0 - mode_n / len(ops))
    mean_seed_disagree = (sum(seed_disagree_fracs) / len(seed_disagree_fracs)
                           if seed_disagree_fracs else 0.0)

    detail = (f"dom_frac={dom_fraction:.3f} (target>={HP_DOM_FRAC}); "
              f"family_mode={mean_family_mode_frac:.3f} "
              f"(target>={HP_FAMILY_MODE_FRAC}); "
              f"res_violations={res_violation_frac:.3f}; "
              f"seed_disagree={mean_seed_disagree:.3f}; "
              f"n_cells={n_cells}")

    # HF first (instrumentation noise)
    if res_violation_frac >= 0.50 or mean_seed_disagree >= HF_SEED_DISAGREE:
        return ("G1_HARD_FAIL", "INSTRUMENTATION_NOISE: " + detail)
    if (dom_fraction >= HP_DOM_FRAC
            and mean_family_mode_frac >= HP_FAMILY_MODE_FRAC):
        return ("G1_HARD_PASS", "DOMINANT_OP_IDENTIFIED: " + detail)
    return ("G1_MIDDLE_BAND", "PARTIAL_DOMINANCE: " + detail)


def _instrumentation_selftest() -> None:
    assert N_FULL == 4096, "PROT-018: _n4096"
    assert len(M_GRID_FULL) == 3
    assert len(DEPTH_GRID_FULL) == 4
    assert len(K_GRID_FULL) == 3
    assert len(SEEDS_FULL) == 5

    # Verdict HP gate
    fake_hp: List[Dict] = []
    for M in M_GRID_FULL:
        for d in DEPTH_GRID_FULL:
            for K in K_GRID_FULL:
                for s in SEEDS_FULL:
                    fake_hp.append({
                        "M": M, "depth": d, "K_paths": K, "seed": s,
                        "accuracy": 0.9, "n_eval": 16, "wall_s": 1.0,
                        "op_breakdown_ns": {
                            "time_likelihood_query_per_hop": {
                                "n_calls": 10, "mean_ns": 1000,
                                "median_ns": 1000, "total_ns": 600_000_000,
                                "p99_ns": 1000},
                            "time_enumerate_paths": {
                                "n_calls": 10, "mean_ns": 500,
                                "median_ns": 500, "total_ns": 50_000_000,
                                "p99_ns": 500},
                        },
                        "dominant_op": "time_likelihood_query_per_hop",
                        "dominant_frac": 0.85,
                        "mem_cpu_peak_mib": 1.0, "mem_cuda_delta_mib": 0.0})
    v, _ = compute_verdict(fake_hp); assert "HARD_PASS" in v, v

    # Verdict HF gate (seed disagreement)
    fake_hf: List[Dict] = []
    seed_idx = 0
    ops_pool = ["time_likelihood_query_per_hop", "time_enumerate_paths",
                "time_posterior_max", "time_bayesian_update"]
    for M in M_GRID_FULL:
        for d in DEPTH_GRID_FULL:
            for K in K_GRID_FULL:
                for s in SEEDS_FULL:
                    dom = ops_pool[seed_idx % len(ops_pool)]
                    seed_idx += 1
                    fake_hf.append({
                        "M": M, "depth": d, "K_paths": K, "seed": s,
                        "accuracy": 0.9, "n_eval": 16, "wall_s": 1.0,
                        "op_breakdown_ns": {
                            dom: {"n_calls": 10, "mean_ns": 1000,
                                  "median_ns": 1000, "total_ns": 600_000_000,
                                  "p99_ns": 1000}},
                        "dominant_op": dom, "dominant_frac": 0.85,
                        "mem_cpu_peak_mib": 1.0, "mem_cuda_delta_mib": 0.0})
    v, _ = compute_verdict(fake_hf); assert "HARD_FAIL" in v, f"HF gate: {v}"

    # Smoke forward pass on CPU
    device = torch.device("cpu")
    out = measure_cell(N_SMOKE, M_GRID_SMOKE[0], DEPTH_GRID_SMOKE[0],
                        K_GRID_SMOKE[0], 17, device)
    assert out["n_eval"] > 0, "selftest: no starts"
    assert out["wall_s"] > 0.0, "selftest: zero wall"
    assert isinstance(out["op_breakdown_ns"], dict)
    assert len(out["op_breakdown_ns"]) > 0, "selftest: no op_breakdown"
    for op_name, body in out["op_breakdown_ns"].items():
        assert body["total_ns"] > 0, f"selftest: zero total for {op_name}"
    assert out["dominant_op"] != "none", "selftest: no dominant op identified"
    print(f"[selftest] path_d_latency_profiling_v1_n4096 PASS "
          f"smoke M={M_GRID_SMOKE[0]} d={DEPTH_GRID_SMOKE[0]} "
          f"K={K_GRID_SMOKE[0]} dom={out['dominant_op']} "
          f"frac={out['dominant_frac']:.3f} wall={out['wall_s']:.3f}s",
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
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    smoke = args.smoke
    N_cfg = N_SMOKE if smoke else N_FULL
    M_grid = M_GRID_SMOKE if smoke else M_GRID_FULL
    depths = DEPTH_GRID_SMOKE if smoke else DEPTH_GRID_FULL
    K_grid = K_GRID_SMOKE if smoke else K_GRID_FULL
    seeds  = SEEDS_SMOKE if smoke else SEEDS_FULL

    out_dir = get_output_dir()
    done = set(list_completed_keys(out_dir))
    t0 = time.time()
    print(f"[run] path_d_latency_profiling smoke={smoke} N={N_cfg} "
          f"M_grid={M_grid} depths={depths} K_grid={K_grid} "
          f"seeds={seeds} done={len(done)} device={device.type}", flush=True)

    cells: List[Dict] = []
    for M in M_grid:
        for d in depths:
            for K in K_grid:
                for seed in seeds:
                    ck = f"M{M}_d{d}_K{K}_seed{seed}"
                    if ck in done:
                        body = load_partial_key(out_dir, ck)
                        if body is not None:
                            cells.append(body); continue
                    try:
                        out = measure_cell(N_cfg, M, d, K, seed, device)
                        write_partial_key(out_dir, ck, out)
                        cells.append(out)
                        print(f"  M={M} d={d} K={K} seed={seed} "
                              f"dom={out['dominant_op']} "
                              f"frac={out['dominant_frac']:.3f} "
                              f"wall={out['wall_s']:.3f}s "
                              f"({time.time()-t0:.1f}s)", flush=True)
                    except (RuntimeError, MemoryError) as e:
                        print(f"  M={M} d={d} K={K} seed={seed} FAILED: {e}",
                              flush=True)
                        if device.type == "cuda":
                            torch.cuda.empty_cache()

    verdict, vm = compute_verdict(cells)
    elapsed = round(time.time() - t0, 2)
    summary = {"anchor": "path_d_latency_profiling_v1_n4096", "N": N_cfg,
               "smoke": smoke, "M_grid": M_grid, "depth_grid": depths,
               "K_grid": K_grid, "seeds": seeds,
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
