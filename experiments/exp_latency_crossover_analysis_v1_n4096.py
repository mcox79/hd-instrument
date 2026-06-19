"""S2 LATENCY CROSSOVER ANALYSIS v1 at N=4096 (E1.3).

Map latency surface across mechanism choices (B/D/E); identify crossover
points for LLM-orchestration mechanism selection.

SCIENTIFIC QUESTION:
  For each (depth, K, M) cell, which mechanism has minimum latency at
  >=95% best-accuracy? Are there distinct cells where each of B/D/E wins?

PRE-REGISTERED BANDS:
  HP = crossover boundaries identified; each mechanism has at least one
       cell where it has min-latency at >=95% best-accuracy.
  HF = one mechanism dominates all cells (no crossover; no selection
       logic needed).
  MB = partial crossover (2 of 3 mechanisms have winning cells).

PROT-018: _n4096.
Anchor: latency_crossover_analysis_v1_n4096
Queue: overnight_queue
Pre-reg: preregs/2026-05-30_latency_crossover_analysis_v1_n4096.md
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
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_s2", _ck_path)
_ck = importlib.util.module_from_spec(_ck_spec)
_ck_spec.loader.exec_module(_ck)
list_completed_keys = _ck.list_completed_keys
write_partial_key   = _ck.write_partial_key
load_partial_key    = _ck.load_partial_key


N = 4096
N_FULL  = N
N_SMOKE = 1024
DEPTHS_FULL  = [3, 5, 8, 12, 16, 20]
DEPTHS_SMOKE = [3]
K_PATHS_FULL  = [100, 500, 1000, 2000, 5000]
K_PATHS_SMOKE = [50]
M_FULL  = [512, 2048, 8192]
M_SMOKE = [128]
SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]
N_PATHS = 24

ACC_REL_THRESHOLD = 0.95


def get_output_dir(default_name: str = "latency_crossover_analysis_v1_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def measure_cell(N_use: int, M: int, depth: int, K_paths: int,
                  seed: int, device: torch.device) -> Dict:
    codebook, W, key_idx, val_idx, relation = build_shared(N_use, M, seed, device)
    starts = torch.tensor(list(relation.keys())[:N_PATHS],
                          dtype=torch.long, device=device)
    pos = sample_coherent_starts(relation, depth, N_PATHS, seed)
    neg = sample_incoherent_paths(codebook.shape[0], depth, N_PATHS,
                                    seed, relation=relation)

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

    t0 = time.perf_counter_ns()
    pred = path_b_run(codebook, W, starts, depth, N_use)
    lat_b = time.perf_counter_ns() - t0
    acc_b = float((pred[valid] == tgt[valid]).float().mean().item()) if valid.any() else 0.0

    t1 = time.perf_counter_ns()
    correct_d = path_d_run(codebook, W, starts, relation, depth, K_paths,
                            seed, N_use)
    lat_d = time.perf_counter_ns() - t1
    acc_d = float(correct_d.mean().item())

    if pos and neg:
        t2 = time.perf_counter_ns()
        auc_e = path_e_run(codebook, W, pos, neg, N_use)
        lat_e = time.perf_counter_ns() - t2
    else:
        auc_e = 0.5
        lat_e = 0

    del codebook, W
    if device.type == "cuda":
        torch.cuda.empty_cache()

    return {
        "M": int(M), "depth": int(depth), "K_paths": int(K_paths),
        "seed": int(seed),
        "lat_b_ns": int(lat_b), "lat_d_ns": int(lat_d), "lat_e_ns": int(lat_e),
        "acc_b": round(acc_b, 5), "acc_d": round(acc_d, 5),
        "auc_e": round(auc_e, 5),
    }


def compute_verdict(cells: List[Dict]) -> Tuple[str, str]:
    if not cells:
        return ("S2_INCONCLUSIVE", "no cells")

    # Aggregate by (M, depth, K) across seeds
    grp: Dict[Tuple[int, int, int], List[Dict]] = {}
    for c in cells:
        grp.setdefault((c["M"], c["depth"], c["K_paths"]), []).append(c)

    wins = {"B": 0, "D": 0, "E": 0}
    inconclusive_cells = 0
    for key, seedcells in grp.items():
        mean_b_lat = sum(c["lat_b_ns"] for c in seedcells) / len(seedcells)
        mean_d_lat = sum(c["lat_d_ns"] for c in seedcells) / len(seedcells)
        mean_e_lat = sum(c["lat_e_ns"] for c in seedcells) / len(seedcells)
        mean_b_acc = sum(c["acc_b"] for c in seedcells) / len(seedcells)
        mean_d_acc = sum(c["acc_d"] for c in seedcells) / len(seedcells)
        mean_e_auc = sum(c["auc_e"] for c in seedcells) / len(seedcells)

        # Normalize accuracy across heterogeneous metrics:
        # B/D are accuracy in [0,1]; E is AUC in [0.5,1]. Map E to acc-like via (auc-0.5)*2.
        e_acc_norm = max(0.0, (mean_e_auc - 0.5) * 2.0)
        best_acc = max(mean_b_acc, mean_d_acc, e_acc_norm)
        if best_acc <= 0.0:
            inconclusive_cells += 1
            continue
        thresh = ACC_REL_THRESHOLD * best_acc
        candidates = []
        if mean_b_acc >= thresh: candidates.append(("B", mean_b_lat))
        if mean_d_acc >= thresh: candidates.append(("D", mean_d_lat))
        if e_acc_norm >= thresh: candidates.append(("E", mean_e_lat))
        if candidates:
            winner = min(candidates, key=lambda kv: kv[1])[0]
            wins[winner] += 1

    n_wins = wins["B"] > 0 and wins["D"] > 0 and wins["E"] > 0
    n_with_win = sum(1 for k, v in wins.items() if v > 0)
    detail = f"wins={wins} n_groups={len(grp)} inconclusive={inconclusive_cells}"
    if n_wins:
        return ("S2_HARD_PASS", "CROSSOVER_IDENTIFIED: " + detail)
    if n_with_win == 1:
        return ("S2_HARD_FAIL", "SINGLE_MECHANISM_DOMINATES: " + detail)
    return ("S2_MIDDLE_BAND", "PARTIAL_CROSSOVER: " + detail)


def _instrumentation_selftest() -> None:
    assert N_FULL == 4096
    device = torch.device("cpu")
    out = measure_cell(N_SMOKE, 64, 3, 20, 17, device)
    assert out["lat_b_ns"] > 0 and out["lat_d_ns"] > 0
    assert 0.0 <= out["acc_b"] <= 1.0
    print(f"[selftest] latency_crossover_analysis_v1_n4096 PASS "
          f"lat_b={out['lat_b_ns']/1e6:.1f}ms lat_d={out['lat_d_ns']/1e6:.1f}ms "
          f"lat_e={out['lat_e_ns']/1e6:.1f}ms", flush=True)


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
    print(f"[run] latency_crossover_analysis smoke={smoke} N={N_cfg} "
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
                    except (RuntimeError, MemoryError) as e:
                        print(f"  M={M} d={d} K={K} s={seed} FAILED: {e}",
                              flush=True)
                        if device.type == "cuda":
                            torch.cuda.empty_cache()

    verdict, vm = compute_verdict(cells)
    elapsed = round(time.time() - t0, 2)
    summary = {"anchor": "latency_crossover_analysis_v1_n4096",
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
