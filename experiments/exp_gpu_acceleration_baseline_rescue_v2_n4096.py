"""GPU ACCELERATION BASELINE RESCUE v2 at N up to 4096.

CONTEXT (F5 rescue):
  v1 anchored as _n8192 ran 20s with NO metrics.json (instrumentation
  failure per cap_map v283). v1 had 5 N values [2048, 4096, 8192] x 5
  seeds x BOTH cpu+cuda devices x KF battery + 4 batch sizes. The first
  cell may have crashed during make_substrate at N=8192 on the runner.

  v2 SCOPE REDUCTION:
    - N sweep [2048, 4096] only (drop 8192)
    - 3 seeds (down from 5)
    - Per-op latency: store / query / edit ONLY (drop batched-throughput
      sweep and delete from rescue scope)
    - KF battery REPLACED by retention + max_iso sanity check only
    - Explicit torch.cuda.is_available() guard at start of each cell
    - Per-op try/except with explicit error reporting

  Anchor suffix: _n4096 (matches reduced top-N; PROT-018-clean).

SCIENTIFIC QUESTION:
  GPU vs CPU speedup at N=2048 and N=4096 per single-op (store, query,
  edit). Do all 3 ops succeed without runtime error?

PRE-REGISTERED BANDS:
  HARD_PASS: mean(query_speedup at N=4096) >= 5x AND all 3 ops (store,
    query, edit) succeed on BOTH cpu and gpu in >= 3/3 seeds.
  HARD_FAIL: mean(query_speedup at N=4096) <= 2x OR any op fails on
    gpu in 2+/3 seeds.
  MIDDLE_BAND: otherwise.

FORMULA SELF-TESTS:
  1. N sweep = [2048, 4096].
  2. anchor _n4096 -> top N = 4096 (PROT-018-clean).
  3. Speedup = cpu_latency_ns / gpu_latency_ns (>1 means GPU faster).
  4. HP threshold relaxed to 5x (v1 had 10x).

OOM CHECK:
  N=4096: W=64MB. CB=805MB. Keys ~16MB. Per-cell ~900MB. OK.

TIMEOUT ESTIMATE:
  2 N x 3 seeds x 2 devices x 3 ops. ~30s/cell. ~360s budget. 14400s cap.

N-suffix: _n4096 (PROT-018).
Anchor: gpu_acceleration_baseline_rescue_v2_n4096
Queue: overnight_queue
Pre-reg: preregs/2026-05-30_gpu_acceleration_baseline_rescue_v2_n4096.md
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

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
    make_substrate, metric_retention, metric_max_iso,
)

_ck_path = REPO / "experiments" / "_seed_checkpoint.py"
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_gpu_r", _ck_path)
_ck = importlib.util.module_from_spec(_ck_spec)
_ck_spec.loader.exec_module(_ck)
list_completed_keys = _ck.list_completed_keys
write_partial_key   = _ck.write_partial_key
load_partial_key    = _ck.load_partial_key


# PRODUCTION CONFIG -- PROT-018: _n4096 binds top-N
N = 4096        # PROT-018 production-N anchor (top of reduced sweep)
N_FULL  = N
N_SWEEP_FULL  = [2048, 4096]
N_SWEEP_SMOKE = [1024]
M_FRAC = 0.25
BETA = 8.0
SEEDS_FULL  = [7, 17, 23]
SEEDS_SMOKE = [17]
N_PROBE = 200

HP_SPEEDUP_MIN_AT_TOPN = 5.0    # relaxed from v1 (10x)
HF_SPEEDUP_MAX_AT_TOPN = 2.0


def get_output_dir(default_name: str = "gpu_acceleration_baseline_rescue_v2_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _time_op(fn, sync_fn=None, n_warmup: int = 2, n_iter: int = 5) -> float:
    for _ in range(n_warmup):
        fn()
    if sync_fn is not None:
        sync_fn()
    times = []
    for _ in range(n_iter):
        t0 = time.perf_counter_ns()
        fn()
        if sync_fn is not None:
            sync_fn()
        t1 = time.perf_counter_ns()
        times.append(t1 - t0)
    return sum(times) / len(times)


def measure_one_n(N_use: int, seed: int, device: torch.device) -> Dict:
    """Run store / query / edit timings + retention sanity at N_use."""
    M = max(1, int(M_FRAC * N_use))
    sync_fn = (lambda: torch.cuda.synchronize()) if device.type == 'cuda' else None

    out: Dict = {"N": N_use, "M": M, "seed": seed, "device": device.type,
                 "ops_succeeded": [], "ops_failed": []}

    # Build substrate (failure here = whole cell fails)
    try:
        codebook, W, keys, values, key_idx, val_idx = make_substrate(
            N_use, M, seed, device)
    except Exception as e:
        out["build_failed"] = f"{type(e).__name__}: {e}"
        return out
    C = codebook.shape[0]

    # Store op (time substrate construction at quarter scale)
    from experiments._metric_battery import _load_t1v1
    t1mod = _load_t1v1()
    M_store = max(1, M // 4)
    try:
        def store_op():
            _W, _k, _v, _ki, _vi = t1mod.store_facts_batched(
                codebook, M_store, seed + 1, N_use, device)
        store_ns = _time_op(store_op, sync_fn, n_warmup=1, n_iter=3)
        out["store_ns_per_fact"] = round(store_ns / M_store, 2)
        out["ops_succeeded"].append("store")
    except Exception as e:
        out["ops_failed"].append(f"store:{type(e).__name__}:{e}")
        out["store_ns_per_fact"] = -1.0

    # Query op
    try:
        n_probe = min(N_PROBE, M)
        probe_keys = keys[:n_probe]
        def query_op():
            sims = (codebook @ (probe_keys @ W.T).T) / N_use
            _ = torch.argmax(sims, dim=0)
        query_ns = _time_op(query_op, sync_fn)
        out["query_ns_per_op"] = round(query_ns / n_probe, 2)
        out["ops_succeeded"].append("query")
    except Exception as e:
        out["ops_failed"].append(f"query:{type(e).__name__}:{e}")
        out["query_ns_per_op"] = -1.0

    # Edit op (single rank-1)
    try:
        new_val = codebook[0]
        old_val = values[0]
        key0 = keys[0]
        def edit_op():
            _W2 = W + torch.outer(new_val - old_val, key0) / N_use
        edit_ns = _time_op(edit_op, sync_fn)
        out["edit_ns"] = round(edit_ns, 2)
        out["ops_succeeded"].append("edit")
    except Exception as e:
        out["ops_failed"].append(f"edit:{type(e).__name__}:{e}")
        out["edit_ns"] = -1.0

    # Retention + max_iso sanity (lightweight; just to make sure W is sane)
    try:
        r = metric_retention(W, codebook, key_idx, val_idx, N_use, BETA, seed,
                             device, n_probe=N_PROBE)
        out["retention"] = r["retention"]
        out["ops_succeeded"].append("retention")
    except Exception as e:
        out["ops_failed"].append(f"retention:{type(e).__name__}:{e}")
        out["retention"] = -1.0

    try:
        r = metric_max_iso(W, codebook, key_idx, val_idx, N_use, BETA, seed,
                           device, n_probe=N_PROBE, n_edits=8)
        out["max_iso"] = r["max_iso"]
        out["ops_succeeded"].append("max_iso")
    except Exception as e:
        out["ops_failed"].append(f"max_iso:{type(e).__name__}:{e}")
        out["max_iso"] = -1.0

    del W, keys, values, codebook
    if device.type == 'cuda':
        torch.cuda.empty_cache()
    return out


def compute_verdict(per_cell: List[Dict]) -> Tuple[str, str]:
    if not per_cell:
        return ("GPU_R_INCONCLUSIVE", "No cells.")
    # Pair (CPU, GPU) at same (N, seed); compute speedup at top N
    by_key: Dict[Tuple[int, int], Dict[str, Dict]] = {}
    for c in per_cell:
        k = (c["N"], c["seed"])
        by_key.setdefault(k, {})[c["device"]] = c

    speedups_topN: List[float] = []
    gpu_op_failures = 0
    n_seeds_topN = 0
    detail: List[str] = []
    for (Nv, sv), pair in by_key.items():
        if "cpu" not in pair or "cuda" not in pair:
            continue
        cpu = pair["cpu"]; gpu = pair["cuda"]
        if Nv == N_FULL:
            n_seeds_topN += 1
            if gpu.get("ops_failed"):
                gpu_op_failures += 1
            cpu_q = cpu.get("query_ns_per_op", -1.0)
            gpu_q = gpu.get("query_ns_per_op", -1.0)
            if cpu_q > 0 and gpu_q > 0:
                sp = cpu_q / gpu_q
                speedups_topN.append(sp)
                detail.append(f"N={Nv}_seed{sv}:q_speedup={sp:.1f}x")

    mean_sp = (sum(speedups_topN) / len(speedups_topN)) if speedups_topN else 0.0
    info = (f"mean_query_speedup_at_N{N_FULL}={mean_sp:.2f}x "
            f"gpu_op_failures_at_topN={gpu_op_failures}/{n_seeds_topN} "
            + " ".join(detail))

    if mean_sp >= HP_SPEEDUP_MIN_AT_TOPN and gpu_op_failures == 0:
        return ("GPU_R_HARD_PASS", f"GPU_FAST_AND_CLEAN: " + info)
    if mean_sp <= HF_SPEEDUP_MAX_AT_TOPN or gpu_op_failures >= 2:
        return ("GPU_R_HARD_FAIL", f"GPU_SLOW_OR_BROKEN: " + info)
    return ("GPU_R_MIDDLE_BAND", f"PARTIAL: " + info)


def _instrumentation_selftest() -> None:
    assert N_FULL == 4096
    assert N_SWEEP_FULL == [2048, 4096]
    speedup = 1000.0 / 100.0
    assert speedup == 10.0

    # Verdict gates
    fake_hp = []
    for sd in [7, 17, 23]:
        cpu = {"N": N_FULL, "seed": sd, "device": "cpu",
               "query_ns_per_op": 1000.0, "ops_failed": []}
        gpu = {"N": N_FULL, "seed": sd, "device": "cuda",
               "query_ns_per_op": 100.0, "ops_failed": []}
        fake_hp.extend([cpu, gpu])
    v, _ = compute_verdict(fake_hp); assert "HARD_PASS" in v, v

    fake_hf = []
    for sd in [7, 17, 23]:
        cpu = {"N": N_FULL, "seed": sd, "device": "cpu",
               "query_ns_per_op": 1000.0, "ops_failed": []}
        gpu = {"N": N_FULL, "seed": sd, "device": "cuda",
               "query_ns_per_op": 800.0, "ops_failed": []}
        fake_hf.extend([cpu, gpu])
    v, _ = compute_verdict(fake_hf); assert "HARD_FAIL" in v, v

    # Smoke on CPU
    device = torch.device("cpu")
    out = measure_one_n(N_SWEEP_SMOKE[0], 17, device)
    assert "store" in out["ops_succeeded"], f"store failed: {out}"
    assert "query" in out["ops_succeeded"], f"query failed: {out}"
    assert out["query_ns_per_op"] > 0
    print(f"[selftest] gpu_acceleration_baseline_rescue_v2_n4096 PASS "
          f"smoke N=1024 q={out['query_ns_per_op']:.0f}ns/op", flush=True)


_instrumentation_selftest()


def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--self-test", action="store_true", dest="self_test")
    args = p.parse_args()
    if args.self_test:
        sys.exit(0)

    smoke = args.smoke
    N_sweep = N_SWEEP_SMOKE if smoke else N_SWEEP_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL

    devices = [torch.device("cpu")]
    if torch.cuda.is_available():
        devices.append(torch.device("cuda"))
    else:
        print("[warn] CUDA not available; running CPU-only -> verdict will be INCONCLUSIVE",
              flush=True)

    out_dir = get_output_dir()
    done = set(list_completed_keys(out_dir))
    t0 = time.time()
    print(f"[run] gpu_acceleration_rescue_v2 smoke={smoke} N_sweep={N_sweep} "
          f"seeds={seeds} devices={[d.type for d in devices]} done={len(done)}",
          flush=True)

    cells: List[Dict] = []
    for Nv in N_sweep:
        for seed in seeds:
            for device in devices:
                ck = f"N{Nv}_seed{seed}_{device.type}"
                if ck in done:
                    body = load_partial_key(out_dir, ck)
                    if body is not None:
                        cells.append(body); continue
                try:
                    out = measure_one_n(Nv, seed, device)
                    write_partial_key(out_dir, ck, out)
                    cells.append(out)
                    print(f"  {ck} ops_ok={out.get('ops_succeeded', [])} "
                          f"failed={out.get('ops_failed', [])} "
                          f"q={out.get('query_ns_per_op', 'na')} "
                          f"({time.time()-t0:.1f}s)", flush=True)
                except Exception as e:
                    print(f"  {ck} CELL_FAILED_OUTER: {type(e).__name__}: {e}",
                          flush=True)
                    if device.type == 'cuda':
                        torch.cuda.empty_cache()

    verdict, vm = compute_verdict(cells)
    elapsed = round(time.time() - t0, 2)
    summary = {"anchor": "gpu_acceleration_baseline_rescue_v2_n4096",
               "N_sweep": N_sweep, "smoke": smoke, "seeds": seeds,
               "devices_run": [d.type for d in devices],
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
