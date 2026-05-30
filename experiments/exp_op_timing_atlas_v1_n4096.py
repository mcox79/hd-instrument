"""S7 OP TIMING ATLAS v1 at N=4096 (E2.1).

Comprehensive substrate operation timing atlas (scaled-down per user spec
to 10 most common operations).

OPERATIONS:
  1. standard_store      (single fact insert)
  2. batched_store_B16   (16-fact batch insert)
  3. standard_retrieve   (single key retrieve)
  4. batched_retrieve_B16 (16-key batch retrieve)
  5. single_edit         (rank-1 edit one fact)
  6. single_delete       (rank-1 erasure of one fact with cert)
  7. audit_chain_verify  (re-hash + compare W)
  8. checkpoint_save     (write W bytes to disk)
  9. checkpoint_load     (read W bytes from disk)
 10. multi_hop_pathB_d5  (Path B depth-5 retrieve)

SCIENTIFIC QUESTION:
  At N=4096, M=2048: are all 10 op latencies characterized with
  p99/median < 5 AND throughput documented?

PRE-REGISTERED BANDS:
  HP = all 10 ops characterized AND p99/median ratio < 5 across all ops.
  HF = any op crashes mid-sweep OR p99 dominated by outliers (>50x).
  MB = most ops clean, 1-2 noisy.

PROT-018: _n4096.
Anchor: op_timing_atlas_v1_n4096
Queue: overnight_queue
Pre-reg: preregs/2026-05-30_op_timing_atlas_v1_n4096.md
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import hashlib
import importlib.util
import json
import os
import statistics
import tempfile
import time
from pathlib import Path
from typing import Dict, List, Tuple

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from experiments._multi_hop_mechanisms import (  # noqa: E402
    build_shared, path_b_run,
)

_ck_path = REPO / "experiments" / "_seed_checkpoint.py"
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_s7", _ck_path)
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
N_OPS_PER_CELL_FULL = 1000
N_OPS_PER_CELL_SMOKE = 50
SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]
BETA = 10.0

HP_P99_RATIO = 5.0
HF_P99_RATIO = 50.0


def get_output_dir(default_name: str = "op_timing_atlas_v1_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _stats(ns_list: List[int]) -> Dict:
    if not ns_list:
        return {"n": 0, "mean_ns": 0, "median_ns": 0, "p99_ns": 0,
                "throughput_ops": 0.0, "p99_med_ratio": 0.0}
    s = sorted(ns_list)
    n = len(s)
    mean_ns = sum(s) / n
    med = s[n // 2]
    p99 = s[min(n - 1, max(0, int(n * 0.99) - 1))]
    throughput = 1e9 / max(1, med)
    ratio = p99 / max(1, med)
    return {"n": n, "mean_ns": int(mean_ns), "median_ns": int(med),
            "p99_ns": int(p99),
            "throughput_ops": round(throughput, 2),
            "p99_med_ratio": round(ratio, 3)}


def measure_seed(N_use: int, M: int, n_ops: int, seed: int,
                  device: torch.device, tmp_dir: Path) -> Dict:
    """Run 10 op classes, return per-op timing distributions."""
    codebook, W0, key_idx, val_idx, relation = build_shared(N_use, M, seed, device)
    C = codebook.shape[0]
    g = torch.Generator(device=device).manual_seed(seed + 999)

    out: Dict[str, Dict] = {}

    # 1. standard_store: outer product update for 1 fact
    times = []
    for i in range(n_ops):
        k_idx = int(torch.randint(0, C, (1,), generator=g, device=device).item())
        v_idx = int(torch.randint(0, C, (1,), generator=g, device=device).item())
        k_v = codebook[k_idx]; v_v = codebook[v_idx]
        t0 = time.perf_counter_ns()
        _ = (v_v.unsqueeze(1) @ k_v.unsqueeze(0)) / N_use
        times.append(time.perf_counter_ns() - t0)
    out["standard_store"] = _stats(times)

    # 2. batched_store_B16
    times = []
    for i in range(n_ops):
        ki = torch.randint(0, C, (16,), generator=g, device=device, dtype=torch.long)
        vi = torch.randint(0, C, (16,), generator=g, device=device, dtype=torch.long)
        kv = codebook[ki]; vv = codebook[vi]
        t0 = time.perf_counter_ns()
        _ = (vv.T @ kv) / N_use
        times.append(time.perf_counter_ns() - t0)
    out["batched_store_B16"] = _stats(times)

    # 3. standard_retrieve: W q
    times = []
    for i in range(n_ops):
        k_idx = int(torch.randint(0, C, (1,), generator=g, device=device).item())
        q = codebook[k_idx]
        t0 = time.perf_counter_ns()
        _ = q @ W0.T
        times.append(time.perf_counter_ns() - t0)
    out["standard_retrieve"] = _stats(times)

    # 4. batched_retrieve_B16
    times = []
    for i in range(n_ops):
        ki = torch.randint(0, C, (16,), generator=g, device=device, dtype=torch.long)
        q = codebook[ki]
        t0 = time.perf_counter_ns()
        _ = q @ W0.T
        times.append(time.perf_counter_ns() - t0)
    out["batched_retrieve_B16"] = _stats(times)

    # 5. single_edit: -old + new outer product
    times = []
    W = W0.clone()
    for i in range(n_ops):
        ki = int(torch.randint(0, C, (1,), generator=g, device=device).item())
        old_vi = int(torch.randint(0, C, (1,), generator=g, device=device).item())
        new_vi = int(torch.randint(0, C, (1,), generator=g, device=device).item())
        k_v = codebook[ki]; ov = codebook[old_vi]; nv = codebook[new_vi]
        t0 = time.perf_counter_ns()
        W = W - (ov.unsqueeze(1) @ k_v.unsqueeze(0)) / N_use
        W = W + (nv.unsqueeze(1) @ k_v.unsqueeze(0)) / N_use
        times.append(time.perf_counter_ns() - t0)
    out["single_edit"] = _stats(times)

    # 6. single_delete: -old outer product + cert (sha256 of removed pair)
    times = []
    W = W0.clone()
    for i in range(n_ops):
        ki = int(torch.randint(0, C, (1,), generator=g, device=device).item())
        vi = int(torch.randint(0, C, (1,), generator=g, device=device).item())
        k_v = codebook[ki]; v_v = codebook[vi]
        t0 = time.perf_counter_ns()
        W = W - (v_v.unsqueeze(1) @ k_v.unsqueeze(0)) / N_use
        _ = hashlib.sha256(f"{ki}-{vi}".encode()).hexdigest()
        times.append(time.perf_counter_ns() - t0)
    out["single_delete"] = _stats(times)

    # 7. audit_chain_verify: sha256 of W bytes
    times = []
    W_bytes = W0.detach().cpu().to(torch.float32).numpy().tobytes()
    expected_hash = hashlib.sha256(W_bytes).hexdigest()
    for i in range(min(n_ops, 100)):  # cap; this is expensive
        t0 = time.perf_counter_ns()
        h = hashlib.sha256(W0.detach().cpu().to(torch.float32).numpy().tobytes()).hexdigest()
        _ = h == expected_hash
        times.append(time.perf_counter_ns() - t0)
    out["audit_chain_verify"] = _stats(times)

    # 8. checkpoint_save
    times = []
    ckpt_path = tmp_dir / f"ckpt_seed{seed}.pt"
    for i in range(min(n_ops, 50)):
        t0 = time.perf_counter_ns()
        torch.save(W0.detach().cpu(), str(ckpt_path))
        times.append(time.perf_counter_ns() - t0)
    out["checkpoint_save"] = _stats(times)

    # 9. checkpoint_load
    times = []
    for i in range(min(n_ops, 50)):
        t0 = time.perf_counter_ns()
        _ = torch.load(str(ckpt_path), map_location="cpu", weights_only=False)
        times.append(time.perf_counter_ns() - t0)
    out["checkpoint_load"] = _stats(times)

    # 10. multi_hop_pathB_d5
    times = []
    starts_list = list(relation.keys())[:16]
    starts = torch.tensor(starts_list, dtype=torch.long, device=device)
    for i in range(min(n_ops, 100)):
        t0 = time.perf_counter_ns()
        _ = path_b_run(codebook, W0, starts, 5, N_use)
        times.append(time.perf_counter_ns() - t0)
    out["multi_hop_pathB_d5"] = _stats(times)

    del codebook, W0
    try:
        os.unlink(ckpt_path)
    except Exception:
        pass
    if device.type == "cuda":
        torch.cuda.empty_cache()
    return {"seed": int(seed), "M": int(M), "ops": out}


def compute_verdict(cells: List[Dict]) -> Tuple[str, str]:
    if not cells:
        return ("S7_INCONCLUSIVE", "no cells")

    # Aggregate p99/median ratios per op across seeds
    ops_keys: List[str] = []
    if cells: ops_keys = sorted(cells[0]["ops"].keys())

    max_ratio_per_op: Dict[str, float] = {}
    for op in ops_keys:
        ratios = [c["ops"][op]["p99_med_ratio"] for c in cells
                    if op in c["ops"]]
        max_ratio_per_op[op] = max(ratios) if ratios else 0.0

    n_clean = sum(1 for op, r in max_ratio_per_op.items() if r <= HP_P99_RATIO)
    n_noisy = sum(1 for op, r in max_ratio_per_op.items() if r > HF_P99_RATIO)
    n_ops_total = len(max_ratio_per_op)

    detail = f"clean={n_clean}/{n_ops_total} noisy={n_noisy} ratios={max_ratio_per_op}"

    if n_clean == n_ops_total:
        return ("S7_HARD_PASS", "ATLAS_CLEAN: " + detail)
    if n_noisy >= 2 or n_clean < n_ops_total - 2:
        return ("S7_HARD_FAIL", "ATLAS_NOISY: " + detail)
    return ("S7_MIDDLE_BAND", "PARTIAL_CLEAN: " + detail)


def _instrumentation_selftest() -> None:
    assert N_FULL == 4096
    device = torch.device("cpu")
    tmp = Path(tempfile.gettempdir()) / "s7_selftest"
    tmp.mkdir(exist_ok=True)
    out = measure_seed(N_SMOKE, 64, 10, 17, device, tmp)
    assert len(out["ops"]) == 10, f"expected 10 ops, got {len(out['ops'])}"
    for k, v in out["ops"].items():
        assert v["n"] > 0, f"op {k} has 0 samples"
        assert v["median_ns"] > 0, f"op {k} median is 0"
    print(f"[selftest] op_timing_atlas_v1_n4096 PASS n_ops={len(out['ops'])}",
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
    M = M_SMOKE if smoke else M_FULL
    n_ops = N_OPS_PER_CELL_SMOKE if smoke else N_OPS_PER_CELL_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL

    tmp = Path(tempfile.gettempdir()) / "s7_ckpt"
    tmp.mkdir(exist_ok=True)

    out_dir = get_output_dir()
    done = set(list_completed_keys(out_dir))
    t0 = time.time()
    print(f"[run] op_timing_atlas smoke={smoke} N={N_cfg} M={M} "
          f"n_ops={n_ops} seeds={seeds} done={len(done)} "
          f"device={device.type}", flush=True)

    cells: List[Dict] = []
    for seed in seeds:
        ck = f"seed{seed}"
        if ck in done:
            body = load_partial_key(out_dir, ck)
            if body is not None:
                cells.append(body); continue
        try:
            out = measure_seed(N_cfg, M, n_ops, seed, device, tmp)
            write_partial_key(out_dir, ck, out)
            cells.append(out)
            print(f"  s={seed} done ({time.time()-t0:.1f}s)", flush=True)
        except (RuntimeError, MemoryError) as e:
            print(f"  s={seed} FAILED: {e}", flush=True)
            if device.type == "cuda":
                torch.cuda.empty_cache()

    verdict, vm = compute_verdict(cells)
    elapsed = round(time.time() - t0, 2)
    summary = {"anchor": "op_timing_atlas_v1_n4096",
               "N": N_cfg, "smoke": smoke,
               "M": M, "n_ops": n_ops, "seeds": seeds,
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
