"""GPU ACCELERATION BASELINE v1 at N up to 8192.

CONTEXT:
  Substrate runs torch+cuda but no systematic GPU vs CPU comparison is
  documented. Establish baseline to inform product positioning.

SCIENTIFIC QUESTION:
  At N in [2048, 4096, 8192], per-op (store, query, edit, delete) latency
  GPU vs CPU? Batched throughput at batch sizes [1, 16, 64, 256]?
  All killer features still pass on GPU?

PRE-REGISTERED BANDS:
  HARD_PASS: GPU >= 10x speedup vs CPU at N=8192 single-op AND all 6 KF
    metrics pass on GPU within +/-5% of CPU baseline.
  HARD_FAIL: GPU <= 2x speedup at N=8192 OR any KF metric breaks on GPU
    (delta from CPU > 10%).
  MIDDLE_BAND: otherwise.

FORMULA SELF-TESTS:
  1. N values [2048, 4096, 8192].
  2. Anchor name _n8192 suffix binds N_FULL_MAX = 8192 (PROT-018).
  3. Throughput = n_ops / wall_seconds (ops/s).
  4. Speedup = cpu_latency / gpu_latency (>1 means GPU faster).

OOM CHECK: N=8192 keys 8192*8192*4=268MB. CB at C=49152*8192*4=1.6GB. OK.

TIMEOUT ESTIMATE: 3 N values * 5 seeds * (CPU + GPU + 4 batch sizes). ~30s/cell.
  ~450s. Budget 14400s.

N-suffix: _n8192 (PROT-018) -- using MAX of N sweep as anchor binding.
Anchor: gpu_acceleration_baseline_v1_n8192.
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
    make_substrate, run_battery, METRIC_NAMES,
)

_ck_path = REPO / "experiments" / "_seed_checkpoint.py"
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_gpu", _ck_path)
_ck = importlib.util.module_from_spec(_ck_spec)
_ck_spec.loader.exec_module(_ck)
list_completed_keys = _ck.list_completed_keys
write_partial_key   = _ck.write_partial_key
load_partial_key    = _ck.load_partial_key


# PRODUCTION CONFIG -- PROT-018: _n8192 binds max-N
N = 8192        # PROT-018 production-N anchor (max of sweep)
N_FULL  = N
N_SWEEP_FULL  = [2048, 4096, 8192]
N_SWEEP_SMOKE = [1024]
M_FRAC = 0.25      # M = N/4 (production-relevant)
BATCH_SIZES = [1, 16, 64, 256]
BETA = 8.0
SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]
N_PROBE = 200

HP_SPEEDUP_MIN_AT_N8192 = 10.0
HP_KF_DELTA_MAX  = 0.05
HF_SPEEDUP_MAX_AT_N8192 = 2.0
HF_KF_DELTA_MIN  = 0.10


def get_output_dir(default_name: str = "gpu_acceleration_baseline_v1_n8192") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _time_op(fn, sync_fn=None, n_warmup: int = 2, n_iter: int = 5) -> float:
    """Time a callable; warm-up and synchronize. Returns mean wall-ns."""
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
    """Run ops + KF battery on one device at N_use; return latencies and metrics."""
    M = max(1, int(M_FRAC * N_use))
    sync_fn = (lambda: torch.cuda.synchronize()) if device.type == 'cuda' else None

    # Build substrate (we'll time the store separately, but reuse a built substrate
    # for query/edit/delete timings to avoid repeated allocation).
    codebook, W, keys, values, key_idx, val_idx = make_substrate(N_use, M, seed, device)
    C = codebook.shape[0]

    # Store latency: measure store_facts_batched on a NEW substrate at same M
    # Use a small M to keep store-timing tractable; report ns/fact.
    from experiments._metric_battery import _load_t1v1
    t1mod = _load_t1v1()
    M_store = max(1, M // 4)   # quarter-store for timing
    def store_op():
        _W, _k, _v, _ki, _vi = t1mod.store_facts_batched(
            codebook, M_store, seed + 1, N_use, device)
    store_ns = _time_op(store_op, sync_fn, n_warmup=1, n_iter=3)
    store_ns_per_fact = store_ns / M_store

    # Query latency: batched retrieval
    n_probe = min(N_PROBE, M)
    probe_keys = keys[:n_probe]
    def query_op():
        sims = (codebook @ (probe_keys @ W.T).T) / N_use
        _ = torch.argmax(sims, dim=0)
    query_ns = _time_op(query_op, sync_fn)
    query_ns_per_op = query_ns / n_probe

    # Edit latency: single rank-1 outer-product update
    new_val = codebook[0]
    old_val = values[0]
    key0   = keys[0]
    def edit_op():
        _W2 = W + torch.outer(new_val - old_val, key0) / N_use
    edit_ns = _time_op(edit_op, sync_fn)

    # Delete latency: subtract rank-1
    def del_op():
        _W2 = W - torch.outer(values[0], keys[0]) / N_use
    del_ns = _time_op(del_op, sync_fn)

    # Batched throughput
    throughput = {}
    for bs in BATCH_SIZES:
        n_b = min(bs, M)
        b_keys = keys[:n_b]
        def batch_op():
            sims = (codebook @ (b_keys @ W.T).T) / N_use
            _ = torch.argmax(sims, dim=0)
        bn = _time_op(batch_op, sync_fn, n_warmup=1, n_iter=3)
        throughput[bs] = round(n_b * 1e9 / bn, 2)   # ops/sec

    # KF battery
    kf_dict = run_battery(N_use, M, BETA, seed, device, n_probe=N_PROBE, n_edits=8)
    kfs = {k: kf_dict[k] for k in METRIC_NAMES}

    del W, keys, values, codebook
    if device.type == 'cuda':
        torch.cuda.empty_cache()

    return {"N": N_use, "M": M, "seed": seed,
            "device": device.type,
            "store_ns_per_fact": round(store_ns_per_fact, 2),
            "query_ns_per_op":   round(query_ns_per_op, 2),
            "edit_ns":           round(edit_ns, 2),
            "delete_ns":         round(del_ns, 2),
            "throughput_ops_per_sec": throughput,
            "kfs": kfs}


def compute_verdict(per_cell: List[Dict]) -> Tuple[str, str]:
    """Pair (CPU, GPU) measurements at same (N, seed); compute speedup at N=8192."""
    if not per_cell:
        return ("GPU_INCONCLUSIVE", "No cells.")
    # Group by (N, seed)
    by_key: Dict[Tuple[int, int], Dict[str, Dict]] = {}
    for c in per_cell:
        k = (c["N"], c["seed"])
        by_key.setdefault(k, {})[c["device"]] = c

    speedup_at_8192 = []
    kf_max_delta = 0.0
    detail = []
    for (Nv, sv), pair in by_key.items():
        if "cpu" not in pair or "cuda" not in pair:
            continue
        cpu = pair["cpu"]; gpu = pair["cuda"]
        sp = cpu["query_ns_per_op"] / max(gpu["query_ns_per_op"], 1e-9)
        if Nv == 8192:
            speedup_at_8192.append(sp)
        # KF deltas
        for k in METRIC_NAMES:
            if k == "retrieval_latency_ns":
                continue   # latency expected to differ; that's the whole point
            c_v = cpu["kfs"].get(k); g_v = gpu["kfs"].get(k)
            if c_v is None or g_v is None:
                continue
            denom = max(abs(c_v), 1e-6)
            d = abs(c_v - g_v) / denom
            kf_max_delta = max(kf_max_delta, d)
        detail.append(f"N={Nv}_seed{sv}:q_speedup={sp:.1f}x")

    mean_sp_8192 = (sum(speedup_at_8192) / len(speedup_at_8192)) if speedup_at_8192 else 0.0
    info = (f"speedup_N8192_query={mean_sp_8192:.2f}x "
            f"kf_max_delta={kf_max_delta:.4f} " + " ".join(detail))
    if mean_sp_8192 >= HP_SPEEDUP_MIN_AT_N8192 and kf_max_delta <= HP_KF_DELTA_MAX:
        return ("GPU_HARD_PASS", f"GPU_FAST: " + info)
    if mean_sp_8192 <= HF_SPEEDUP_MAX_AT_N8192 or kf_max_delta >= HF_KF_DELTA_MIN:
        return ("GPU_HARD_FAIL", f"GPU_SLOW_OR_BROKEN: " + info)
    return ("GPU_MIDDLE_BAND", f"PARTIAL: " + info)


def _instrumentation_selftest() -> None:
    assert N == 8192, f"PROT-018: N must be 8192; got {N}"
    assert N_SWEEP_FULL == [2048, 4096, 8192]
    # Speedup formula
    speedup = 1000.0 / 100.0
    assert speedup == 10.0

    # Verdict gates: synthesize CPU/GPU paired
    fake_hp = []
    for sd in [7, 17, 23]:
        cpu = {"N": 8192, "seed": sd, "device": "cpu",
               "query_ns_per_op": 1000.0,
               "kfs": {n: 0.5 for n in METRIC_NAMES}}
        gpu = {"N": 8192, "seed": sd, "device": "cuda",
               "query_ns_per_op": 80.0,
               "kfs": {n: 0.5 for n in METRIC_NAMES}}
        fake_hp.extend([cpu, gpu])
    v, _ = compute_verdict(fake_hp); assert "HARD_PASS" in v, v

    fake_hf = []
    for sd in [7, 17, 23]:
        cpu = {"N": 8192, "seed": sd, "device": "cpu",
               "query_ns_per_op": 1000.0,
               "kfs": {n: 0.5 for n in METRIC_NAMES}}
        gpu = {"N": 8192, "seed": sd, "device": "cuda",
               "query_ns_per_op": 800.0,    # only 1.25x speedup
               "kfs": {n: 0.5 for n in METRIC_NAMES}}
        fake_hf.extend([cpu, gpu])
    v, _ = compute_verdict(fake_hf); assert "HARD_FAIL" in v, v

    # Smoke: 1 N value on CPU
    device = torch.device("cpu")
    out = measure_one_n(1024, 17, device)
    for k in METRIC_NAMES:
        assert k in out["kfs"], f"KF battery missing {k}"
    assert out["query_ns_per_op"] > 0.0
    print(f"[selftest] gpu_acceleration_baseline_v1_n8192 PASS smoke "
          f"N=1024 q={out['query_ns_per_op']:.0f}ns/op", flush=True)


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

    # CPU always available; GPU only if torch.cuda.is_available().
    devices = [torch.device("cpu")]
    if torch.cuda.is_available():
        devices.append(torch.device("cuda"))
    out_dir = get_output_dir()
    done = set(list_completed_keys(out_dir))
    t0 = time.time()
    print(f"[run] gpu_acceleration_baseline smoke={smoke} N_sweep={N_sweep} "
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
                    print(f"  {ck} q={out['query_ns_per_op']:.0f}ns "
                          f"store={out['store_ns_per_fact']:.0f}ns/fact "
                          f"edit={out['edit_ns']:.0f}ns "
                          f"({time.time()-t0:.1f}s)", flush=True)
                except (RuntimeError, MemoryError) as e:
                    print(f"  {ck} FAILED: {e}", flush=True)
                    if device.type == 'cuda':
                        torch.cuda.empty_cache()

    verdict, vm = compute_verdict(cells)
    elapsed = round(time.time() - t0, 2)
    summary = {"anchor": "gpu_acceleration_baseline_v1_n8192",
               "N_sweep": N_sweep, "smoke": smoke, "seeds": seeds,
               "devices_run": [d.type for d in devices],
               "cells": cells,
               "verdict": verdict, "verdict_msg": vm, "elapsed_s": elapsed}
    payload = {"verdict": verdict, "verdict_msg": vm,
               "elapsed_s": elapsed, "summary": summary}
    with open(out_dir / "metrics.json", "w") as f:
        json.dump(payload, f, indent=2, default=str)
    print(f"\n[verdict] {verdict}\n[verdict_msg] {vm}\n[elapsed] {elapsed}s",
          flush=True)


if __name__ == "__main__":
    main()
