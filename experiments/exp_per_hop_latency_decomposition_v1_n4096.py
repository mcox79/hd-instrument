"""S1 PER-HOP LATENCY DECOMPOSITION v1 at N=4096 (E1.1).

Per-op timing breakdown for each multi-hop path mechanism (B/D/E).
Identifies dominant bottleneck operation per path at production scale.

SCIENTIFIC QUESTION:
  Which operation dominates wall_s for each of paths B, D, E across
  M in {512, 2048, 4096, 8192}, depth in {3, 5, 8, 12}, K_paths in
  {100, 500, 1000}?

PRE-REGISTERED BANDS:
  HP = per-path bottleneck op identified (>50% wall_s) AND breakdown
       consistent across cells.
  HF = instrumentation noise dominates (per-op times below measurement
       resolution; cv > 50% within a single cell).
  MB = mixed; some paths clean, others noisy.

PROT-018: _n4096 binds N = 4096.
Anchor: per_hop_latency_decomposition_v1_n4096
Queue: overnight_queue
Pre-reg: preregs/2026-05-30_per_hop_latency_decomposition_v1_n4096.md
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
    TimingTrace, build_shared, path_b_run, path_d_run, path_e_run,
)
from experiments._relation_graph import (  # noqa: E402
    sample_coherent_starts, sample_incoherent_paths,
)

_ck_path = REPO / "experiments" / "_seed_checkpoint.py"
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_s1", _ck_path)
_ck = importlib.util.module_from_spec(_ck_spec)
_ck_spec.loader.exec_module(_ck)
list_completed_keys = _ck.list_completed_keys
write_partial_key   = _ck.write_partial_key
load_partial_key    = _ck.load_partial_key


N = 4096
N_FULL  = N
N_SMOKE = 1024
M_FULL  = [512, 2048, 4096, 8192]
M_SMOKE = [256]
DEPTHS_FULL  = [3, 5, 8, 12]
DEPTHS_SMOKE = [3]
K_PATHS_FULL  = [100, 500, 1000]
K_PATHS_SMOKE = [50]
SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]
N_PATHS_PER_CELL = 32

HP_DOM_FRAC = 0.50


def get_output_dir(default_name: str = "per_hop_latency_decomposition_v1_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def measure_cell(N_use: int, M: int, depth: int, K_paths: int,
                  seed: int, device: torch.device) -> Dict:
    codebook, W, key_idx, val_idx, relation = build_shared(N_use, M, seed, device)
    starts = torch.tensor(list(relation.keys())[:N_PATHS_PER_CELL],
                          dtype=torch.long, device=device)
    pos = sample_coherent_starts(relation, depth, N_PATHS_PER_CELL, seed)
    neg = sample_incoherent_paths(codebook.shape[0], depth, N_PATHS_PER_CELL,
                                    seed, relation=relation)

    tr_b = TimingTrace(); tr_d = TimingTrace(); tr_e = TimingTrace()

    t0 = time.perf_counter_ns()
    _ = path_b_run(codebook, W, starts, depth, N_use, trace=tr_b)
    wall_b_ns = time.perf_counter_ns() - t0

    t1 = time.perf_counter_ns()
    _ = path_d_run(codebook, W, starts, relation, depth, K_paths, seed,
                    N_use, trace=tr_d)
    wall_d_ns = time.perf_counter_ns() - t1

    if pos and neg:
        t2 = time.perf_counter_ns()
        _ = path_e_run(codebook, W, pos, neg, N_use, trace=tr_e)
        wall_e_ns = time.perf_counter_ns() - t2
    else:
        wall_e_ns = 0

    dom_b_op, dom_b_frac = tr_b.dominant_op()
    dom_d_op, dom_d_frac = tr_d.dominant_op()
    dom_e_op, dom_e_frac = tr_e.dominant_op()

    del codebook, W
    if device.type == "cuda":
        torch.cuda.empty_cache()

    return {
        "M": int(M), "depth": int(depth), "K_paths": int(K_paths),
        "seed": int(seed),
        "wall_b_ns": int(wall_b_ns), "wall_d_ns": int(wall_d_ns),
        "wall_e_ns": int(wall_e_ns),
        "path_b_breakdown": tr_b.summary(),
        "path_d_breakdown": tr_d.summary(),
        "path_e_breakdown": tr_e.summary(),
        "dom_b_op": dom_b_op, "dom_b_frac": round(dom_b_frac, 4),
        "dom_d_op": dom_d_op, "dom_d_frac": round(dom_d_frac, 4),
        "dom_e_op": dom_e_op, "dom_e_frac": round(dom_e_frac, 4),
    }


def compute_verdict(cells: List[Dict]) -> Tuple[str, str]:
    if not cells:
        return ("S1_INCONCLUSIVE", "no cells")

    # Aggregate dominant op per path
    dom_counts_b: Dict[str, int] = {}
    dom_counts_d: Dict[str, int] = {}
    dom_counts_e: Dict[str, int] = {}
    n_strong_b = n_strong_d = n_strong_e = 0
    for c in cells:
        dom_counts_b[c["dom_b_op"]] = dom_counts_b.get(c["dom_b_op"], 0) + 1
        dom_counts_d[c["dom_d_op"]] = dom_counts_d.get(c["dom_d_op"], 0) + 1
        dom_counts_e[c["dom_e_op"]] = dom_counts_e.get(c["dom_e_op"], 0) + 1
        if c["dom_b_frac"] >= HP_DOM_FRAC: n_strong_b += 1
        if c["dom_d_frac"] >= HP_DOM_FRAC: n_strong_d += 1
        if c["dom_e_frac"] >= HP_DOM_FRAC: n_strong_e += 1

    top_b = max(dom_counts_b.items(), key=lambda kv: kv[1])
    top_d = max(dom_counts_d.items(), key=lambda kv: kv[1])
    top_e = max(dom_counts_e.items(), key=lambda kv: kv[1])

    n = len(cells)
    b_consistent = top_b[1] >= 0.5 * n
    d_consistent = top_d[1] >= 0.5 * n
    e_consistent = top_e[1] >= 0.5 * n
    b_strong = n_strong_b >= 0.5 * n
    d_strong = n_strong_d >= 0.5 * n
    e_strong = n_strong_e >= 0.5 * n

    detail = (f"top_b={top_b[0]}({top_b[1]}/{n}) "
              f"top_d={top_d[0]}({top_d[1]}/{n}) "
              f"top_e={top_e[0]}({top_e[1]}/{n})")

    if (b_consistent and d_consistent and e_consistent and
        b_strong and d_strong and e_strong):
        return ("S1_HARD_PASS", "BOTTLENECKS_IDENTIFIED: " + detail)
    if not (b_consistent or d_consistent or e_consistent):
        return ("S1_HARD_FAIL", "NOISE_DOMINATES: " + detail)
    return ("S1_MIDDLE_BAND", "PARTIAL: " + detail)


def _instrumentation_selftest() -> None:
    assert N_FULL == 4096
    device = torch.device("cpu")
    out = measure_cell(N_SMOKE, 64, 3, 20, 17, device)
    assert out["wall_b_ns"] > 0 and out["wall_d_ns"] > 0
    assert out["dom_b_op"] in out["path_b_breakdown"] or out["dom_b_op"] == "none"
    assert 0.0 <= out["dom_b_frac"] <= 1.0
    print(f"[selftest] per_hop_latency_decomposition_v1_n4096 PASS "
          f"dom_b={out['dom_b_op']}({out['dom_b_frac']:.2f}) "
          f"dom_d={out['dom_d_op']}({out['dom_d_frac']:.2f}) "
          f"dom_e={out['dom_e_op']}({out['dom_e_frac']:.2f})", flush=True)


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
    Ms = M_SMOKE if smoke else M_FULL
    depths = DEPTHS_SMOKE if smoke else DEPTHS_FULL
    Ks = K_PATHS_SMOKE if smoke else K_PATHS_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL

    out_dir = get_output_dir()
    done = set(list_completed_keys(out_dir))
    t0 = time.time()
    print(f"[run] per_hop_latency_decomposition smoke={smoke} N={N_cfg} "
          f"M={Ms} depths={depths} K={Ks} seeds={seeds} "
          f"done={len(done)} device={device.type}", flush=True)

    cells: List[Dict] = []
    for M in Ms:
        for d in depths:
            for K in Ks:
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
                        print(f"  M={M} d={d} K={K} s={seed} "
                              f"wb={out['wall_b_ns']/1e6:.1f}ms "
                              f"wd={out['wall_d_ns']/1e6:.1f}ms "
                              f"we={out['wall_e_ns']/1e6:.1f}ms "
                              f"({time.time()-t0:.1f}s)", flush=True)
                    except (RuntimeError, MemoryError) as e:
                        print(f"  M={M} d={d} K={K} s={seed} FAILED: {e}",
                              flush=True)
                        if device.type == "cuda":
                            torch.cuda.empty_cache()

    verdict, vm = compute_verdict(cells)
    elapsed = round(time.time() - t0, 2)
    summary = {"anchor": "per_hop_latency_decomposition_v1_n4096",
               "N": N_cfg, "smoke": smoke,
               "Ms": Ms, "depths": depths, "Ks": Ks, "seeds": seeds,
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
