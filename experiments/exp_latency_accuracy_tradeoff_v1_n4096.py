"""S8 LATENCY-ACCURACY TRADEOFF v1 at N=4096 (E2.2).

Pareto frontier across 4 tunable substrate operations:
  - cleanup_strength: [0.0, 0.25, 0.5, 1.0, 1.5, 2.0]
  - multi_hop_K_paths: [50, 100, 250, 500, 1000]
  - audit_chain_probe_count: [1, 5, 10, 25, 50]
  - multi_hop_depth: [3, 5, 8, 12]

SCIENTIFIC QUESTION:
  Do each of these 4 ops admit a Pareto frontier with >=3 distinct
  Pareto-optimal settings?

PRE-REGISTERED BANDS:
  HP = Pareto frontier exists for each of 4 ops AND each has >=3
       distinct Pareto-optimal settings.
  HF = no tradeoff visible (all configs equivalent on any op).
  MB = partial frontier (2-3 of 4 ops).

PROT-018: _n4096.
Anchor: latency_accuracy_tradeoff_v1_n4096
Queue: overnight_queue
Pre-reg: preregs/2026-05-30_latency_accuracy_tradeoff_v1_n4096.md
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import hashlib
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
    build_shared, path_b_run, path_d_run,
)

_ck_path = REPO / "experiments" / "_seed_checkpoint.py"
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_s8", _ck_path)
_ck = importlib.util.module_from_spec(_ck_spec)
_ck_spec.loader.exec_module(_ck)
list_completed_keys = _ck.list_completed_keys
write_partial_key   = _ck.write_partial_key
load_partial_key    = _ck.load_partial_key


N = 4096
N_FULL  = N
N_SMOKE = 1024
M_FULL = 2048
M_SMOKE = 256

CLEANUP_STRENGTHS_FULL = [0.0, 0.25, 0.5, 1.0, 1.5, 2.0]
K_PATHS_FULL = [50, 100, 250, 500, 1000]
AUDIT_PROBES_FULL = [1, 5, 10, 25, 50]
DEPTHS_FULL = [3, 5, 8, 12]

CLEANUP_SMOKE = [0.5, 1.0]
K_PATHS_SMOKE = [50]
AUDIT_SMOKE = [5]
DEPTHS_SMOKE = [3]

SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]
N_PATHS = 16

HP_MIN_PARETO = 3


def get_output_dir(default_name: str = "latency_accuracy_tradeoff_v1_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def measure_cleanup(codebook, W, starts, targets_valid, valid_mask,
                      depth, N_use, strength) -> Tuple[float, int]:
    """Retrieve via cleanup-modulated readout. strength scales the readout
    sharpness; tradeoff is latency (more sharpening = more work) vs acc."""
    t0 = time.perf_counter_ns()
    q = codebook[starts].clone()
    for _ in range(depth):
        q = q @ W.T
    sims = (codebook @ q.T) / N_use
    if strength > 0:
        sims = sims * strength
    pred = torch.argmax(sims, dim=0)
    dt = time.perf_counter_ns() - t0
    acc = float((pred[valid_mask] == targets_valid[valid_mask]).float().mean().item()) if valid_mask.any() else 0.0
    return acc, int(dt)


def measure_k_paths(codebook, W, starts, relation, depth, K, seed,
                      N_use) -> Tuple[float, int]:
    t0 = time.perf_counter_ns()
    correct = path_d_run(codebook, W, starts, relation, depth, K, seed, N_use)
    dt = time.perf_counter_ns() - t0
    return float(correct.mean().item()), int(dt)


def measure_audit_probes(W: torch.Tensor, n_probes: int) -> Tuple[float, int]:
    """Audit by hashing n_probes random rows of W. Accuracy = 1 if hash
    matches re-hash; latency = wall_ns. Tradeoff: more probes => higher
    confidence but slower."""
    rows = torch.randperm(W.shape[0])[:n_probes]
    t0 = time.perf_counter_ns()
    h1 = hashlib.sha256(W[rows].detach().cpu().to(torch.float32).numpy().tobytes()).hexdigest()
    h2 = hashlib.sha256(W[rows].detach().cpu().to(torch.float32).numpy().tobytes()).hexdigest()
    dt = time.perf_counter_ns() - t0
    return 1.0 if h1 == h2 else 0.0, int(dt)


def measure_cell(N_use: int, M: int, seed: int, cleanup_strs: List[float],
                  Ks: List[int], audit_probes: List[int], depths: List[int],
                  device: torch.device) -> Dict:
    codebook, W, key_idx, val_idx, relation = build_shared(N_use, M, seed, device)
    C = codebook.shape[0]
    starts = torch.tensor(list(relation.keys())[:N_PATHS],
                          dtype=torch.long, device=device)
    targets_list = []
    for k in starts.tolist():
        cur = int(k); ok = True
        for _ in range(5):
            nxt = relation.get(cur)
            if nxt is None: ok = False; break
            cur = int(nxt)
        targets_list.append(cur if ok else -1)
    tgt = torch.tensor(targets_list, dtype=torch.long, device=device)
    valid = tgt >= 0

    cleanup_results = []
    for s in cleanup_strs:
        acc, lat = measure_cleanup(codebook, W, starts, tgt, valid, 5, N_use, s)
        cleanup_results.append({"setting": s, "acc": acc, "lat_ns": lat})

    k_results = []
    for K in Ks:
        acc, lat = measure_k_paths(codebook, W, starts, relation, 5, K, seed, N_use)
        k_results.append({"setting": K, "acc": acc, "lat_ns": lat})

    audit_results = []
    for n_p in audit_probes:
        acc, lat = measure_audit_probes(W, n_p)
        audit_results.append({"setting": n_p, "acc": acc, "lat_ns": lat})

    depth_results = []
    for d in depths:
        targets_d = []
        for k in starts.tolist():
            cur = int(k); ok = True
            for _ in range(d):
                nxt = relation.get(cur)
                if nxt is None: ok = False; break
                cur = int(nxt)
            targets_d.append(cur if ok else -1)
        tgt_d = torch.tensor(targets_d, dtype=torch.long, device=device)
        valid_d = tgt_d >= 0
        acc, lat = measure_cleanup(codebook, W, starts, tgt_d, valid_d, d, N_use, 1.0)
        depth_results.append({"setting": d, "acc": acc, "lat_ns": lat})

    del codebook, W
    if device.type == "cuda":
        torch.cuda.empty_cache()

    return {"seed": int(seed), "M": int(M),
            "cleanup": cleanup_results, "k_paths": k_results,
            "audit": audit_results, "depth": depth_results}


def pareto_count(points: List[Tuple[float, float]]) -> int:
    """Count Pareto-optimal points (max acc, min latency)."""
    if not points:
        return 0
    n = len(points)
    is_pareto = [True] * n
    for i in range(n):
        ai, li = points[i]
        for j in range(n):
            if i == j: continue
            aj, lj = points[j]
            # j dominates i: aj >= ai AND lj <= li AND at least one strict
            if aj >= ai and lj <= li and (aj > ai or lj < li):
                is_pareto[i] = False
                break
    return sum(is_pareto)


def compute_verdict(cells: List[Dict]) -> Tuple[str, str]:
    if not cells:
        return ("S8_INCONCLUSIVE", "no cells")

    # Aggregate (acc, lat) by setting per op
    def agg(op_key):
        pts: Dict = {}
        for c in cells:
            for r in c.get(op_key, []):
                s = r["setting"]
                pts.setdefault(s, []).append((r["acc"], r["lat_ns"]))
        avg_pts = []
        for s, vals in pts.items():
            mean_a = sum(v[0] for v in vals) / len(vals)
            mean_l = sum(v[1] for v in vals) / len(vals)
            avg_pts.append((mean_a, mean_l))
        return avg_pts

    pf_cleanup = pareto_count(agg("cleanup"))
    pf_k = pareto_count(agg("k_paths"))
    pf_audit = pareto_count(agg("audit"))
    pf_depth = pareto_count(agg("depth"))

    pfs = {"cleanup": pf_cleanup, "k_paths": pf_k,
           "audit": pf_audit, "depth": pf_depth}
    n_ops_pass = sum(1 for v in pfs.values() if v >= HP_MIN_PARETO)
    n_ops_total = 4
    detail = f"pareto={pfs} n_pass={n_ops_pass}/{n_ops_total}"

    # No-tradeoff: any op has only 1 Pareto-optimal point but should have more
    any_collapsed = any(v == 1 for v in pfs.values())

    if n_ops_pass == n_ops_total:
        return ("S8_HARD_PASS", "PARETO_FRONTIER_ALL_OPS: " + detail)
    if any_collapsed and n_ops_pass <= 1:
        return ("S8_HARD_FAIL", "NO_TRADEOFF: " + detail)
    return ("S8_MIDDLE_BAND", "PARTIAL_FRONTIER: " + detail)


def _instrumentation_selftest() -> None:
    assert N_FULL == 4096
    device = torch.device("cpu")
    out = measure_cell(N_SMOKE, 64, 17,
                         [0.5, 1.0], [20, 50], [1, 5], [2, 3], device)
    assert len(out["cleanup"]) == 2
    assert len(out["k_paths"]) == 2
    assert len(out["audit"]) == 2
    assert len(out["depth"]) == 2
    print(f"[selftest] latency_accuracy_tradeoff_v1_n4096 PASS", flush=True)


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
    M = M_SMOKE if smoke else M_FULL
    cleanups = CLEANUP_SMOKE if smoke else CLEANUP_STRENGTHS_FULL
    Ks = K_PATHS_SMOKE if smoke else K_PATHS_FULL
    audits = AUDIT_SMOKE if smoke else AUDIT_PROBES_FULL
    depths = DEPTHS_SMOKE if smoke else DEPTHS_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL

    out_dir = get_output_dir()
    done = set(list_completed_keys(out_dir))
    t0 = time.time()
    print(f"[run] latency_accuracy_tradeoff smoke={smoke} N={N_cfg} M={M} "
          f"cleanups={cleanups} Ks={Ks} audits={audits} depths={depths} "
          f"seeds={seeds} done={len(done)} device={device.type}", flush=True)

    cells: List[Dict] = []
    for seed in seeds:
        ck = f"seed{seed}"
        if ck in done:
            body = load_partial_key(out_dir, ck)
            if body is not None:
                cells.append(body); continue
        try:
            out = measure_cell(N_cfg, M, seed, cleanups, Ks, audits, depths,
                                 device)
            write_partial_key(out_dir, ck, out)
            cells.append(out)
            print(f"  s={seed} done ({time.time()-t0:.1f}s)", flush=True)
        except (RuntimeError, MemoryError) as e:
            print(f"  s={seed} FAILED: {e}", flush=True)
            if device.type == "cuda":
                torch.cuda.empty_cache()

    verdict, vm = compute_verdict(cells)
    elapsed = round(time.time() - t0, 2)
    summary = {"anchor": "latency_accuracy_tradeoff_v1_n4096",
               "N": N_cfg, "smoke": smoke,
               "M": M, "cleanups": cleanups, "Ks": Ks,
               "audits": audits, "depths": depths, "seeds": seeds,
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
