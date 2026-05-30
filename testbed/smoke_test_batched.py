"""Smoke gate for batched substrate operations (Diagnostic 1).

Verifies:
  1. Correctness: store_batch produces the SAME W matrix (to within machine
     epsilon) as a single-item store sequence on the same input.
  2. Recall parity: retrieve_batch returns the same top-1 key_ids as a loop
     over single retrieve() calls.
  3. Speedup: batched throughput >= 10x single-item throughput on N=512.

Exits 0 on pass, 1 on fail. Wall budget < 30s on a laptop CPU.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np
import torch

_REPO = Path(__file__).resolve().parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from testbed.substrate_memory import SubstrateMemory  # noqa: E402


def _make_data(M: int, N: int, seed: int = 11):
    rng = np.random.default_rng(seed)
    raw = rng.integers(0, 2, size=(M, N), dtype=np.int8).astype(np.float32)
    key_vecs = raw * 2.0 - 1.0
    key_ids = [f"sb_{i:05d}" for i in range(M)]
    values = [f"sv_{i}" for i in range(M)]
    return key_ids, key_vecs, values


def main() -> int:
    N = 512
    C_scale = 4  # codebook size = 2048
    M = 1024
    B = 128
    n_repeats = 3  # smooth measurement noise
    print(f"[smoke-batched] N={N} C={C_scale*N} M={M} batch_size={B} repeats={n_repeats}")

    key_ids, key_vecs, values = _make_data(M, N, seed=11)

    # --- Single-item reference (for W parity and recall parity) ---
    # First build mem_single once (it's used for parity checks).
    mem_single = SubstrateMemory(
        N=N, codebook_kind="bsc", codebook_scale=C_scale, beta=32.0, seed=7
    )
    t0 = time.perf_counter_ns()
    for i in range(M):
        mem_single.store(key_ids[i], key_vecs[i], values[i])
    single_store_wall = (time.perf_counter_ns() - t0) / 1e9
    single_store_ops_one = M / single_store_wall if single_store_wall > 0 else 0.0

    # Single-item retrieve baseline (averaged over n_repeats passes).
    retr_walls: list[float] = []
    single_results: list = []
    for rep in range(n_repeats):
        t0 = time.perf_counter_ns()
        rep_results = [mem_single.retrieve(key_vecs[i]) for i in range(M)]
        retr_walls.append((time.perf_counter_ns() - t0) / 1e9)
        if rep == 0:
            single_results = rep_results
    single_retrieve_wall_min = min(retr_walls)
    single_retrieve_ops = (
        M / single_retrieve_wall_min if single_retrieve_wall_min > 0 else 0.0
    )

    print(f"[smoke-batched] single store wall {single_store_wall*1000:.1f} ms, "
          f"{single_store_ops_one:.1f} ops/s")
    print(f"[smoke-batched] single retrieve wall (best of {n_repeats}) "
          f"{single_retrieve_wall_min*1000:.1f} ms, {single_retrieve_ops:.1f} ops/s")
    single_recall = sum(
        1 for i, r in enumerate(single_results) if r.key_id == key_ids[i]
    ) / M
    print(f"[smoke-batched] single recall@1 {single_recall:.4f}")

    # --- Batched path ---
    # Run store_batch on a fresh substrate (parity-checked exactly once below).
    mem_batched = SubstrateMemory(
        N=N, codebook_kind="bsc", codebook_scale=C_scale, beta=32.0, seed=7
    )
    t0 = time.perf_counter_ns()
    for j in range(0, M, B):
        end = min(j + B, M)
        chunk = [(key_ids[i], key_vecs[i], values[i]) for i in range(j, end)]
        mem_batched.store_batch(chunk)
    batched_store_wall = (time.perf_counter_ns() - t0) / 1e9
    batched_store_ops = M / batched_store_wall if batched_store_wall > 0 else 0.0
    print(f"[smoke-batched] batched store wall {batched_store_wall*1000:.1f} ms, "
          f"{batched_store_ops:.1f} ops/s")

    # Compare against single-store wall measured under the same conditions:
    # rebuild the reference store once more and pick the min wall, so the
    # single number isn't penalized by a transient slow-down.
    rebuild_walls = [single_store_wall]
    for rep in range(n_repeats - 1):
        mem_tmp = SubstrateMemory(
            N=N, codebook_kind="bsc", codebook_scale=C_scale, beta=32.0, seed=7
        )
        t0 = time.perf_counter_ns()
        for i in range(M):
            mem_tmp.store(key_ids[i], key_vecs[i], values[i])
        rebuild_walls.append((time.perf_counter_ns() - t0) / 1e9)
    single_store_wall_min = min(rebuild_walls)
    single_store_ops = (
        M / single_store_wall_min if single_store_wall_min > 0 else 0.0
    )
    print(f"[smoke-batched] single store wall (best of {n_repeats}) "
          f"{single_store_wall_min*1000:.1f} ms, {single_store_ops:.1f} ops/s")

    # W parity check.
    W_diff = (mem_single.W - mem_batched.W).abs().max().item()
    W_frob = float(torch.linalg.norm(mem_single.W - mem_batched.W).item())
    print(f"[smoke-batched] W parity: max|delta|={W_diff:.3e}, "
          f"||delta||_F={W_frob:.3e}")
    parity_tol = 1e-4  # tolerant of fp32 matmul vs sequential outer-product reordering
    if W_diff > parity_tol:
        print(f"[smoke-batched] FAIL: W parity max|delta| {W_diff:.3e} > {parity_tol}")
        return 1

    # Registry parity.
    if mem_single.key_registry != mem_batched.key_registry:
        print("[smoke-batched] FAIL: key_registry mismatch between paths")
        return 1
    if mem_single.value_atom_registry != mem_batched.value_atom_registry:
        print("[smoke-batched] FAIL: value_atom_registry mismatch between paths")
        return 1
    if mem_single.value_registry != mem_batched.value_registry:
        print("[smoke-batched] FAIL: value_registry mismatch between paths")
        return 1

    # Path 9 occupancy-set invariant: persistent set must equal registry-derived set.
    for name, mem in (("single", mem_single), ("batched", mem_batched)):
        expected_k = set(mem.key_registry.values())
        expected_v = set(mem.value_atom_registry.values())
        if mem._used_key_rows != expected_k:
            print(f"[smoke-batched] FAIL: {name}._used_key_rows out of sync "
                  f"(persistent={len(mem._used_key_rows)} vs registry={len(expected_k)})")
            return 1
        if mem._used_value_rows != expected_v:
            print(f"[smoke-batched] FAIL: {name}._used_value_rows out of sync "
                  f"(persistent={len(mem._used_value_rows)} vs registry={len(expected_v)})")
            return 1
    print("[smoke-batched] occupancy-set invariant OK on both paths")

    # Batched retrieve (best of n_repeats).
    batched_retrieve_walls: list[float] = []
    batched_results: list = []
    for rep in range(n_repeats):
        t0 = time.perf_counter_ns()
        rep_results: list = []
        for j in range(0, M, B):
            end = min(j + B, M)
            Q = key_vecs[j:end]
            rep_results.extend(mem_batched.retrieve_batch(Q))
        batched_retrieve_walls.append((time.perf_counter_ns() - t0) / 1e9)
        if rep == 0:
            batched_results = rep_results
    batched_retrieve_wall = min(batched_retrieve_walls)
    batched_retrieve_ops = M / batched_retrieve_wall if batched_retrieve_wall > 0 else 0.0
    print(f"[smoke-batched] batched retrieve wall (best of {n_repeats}) "
          f"{batched_retrieve_wall*1000:.1f} ms, {batched_retrieve_ops:.1f} ops/s")

    batched_recall = sum(
        1 for i, r in enumerate(batched_results) if r.key_id == key_ids[i]
    ) / M
    print(f"[smoke-batched] batched recall@1 {batched_recall:.4f}")

    if abs(batched_recall - single_recall) > 1e-6:
        print(f"[smoke-batched] FAIL: recall parity broken "
              f"({batched_recall} vs {single_recall})")
        return 1

    # Top-1 key_id parity.
    mismatches = sum(
        1 for a, b in zip(single_results, batched_results)
        if a.key_id != b.key_id
    )
    print(f"[smoke-batched] top-1 key_id mismatches: {mismatches}/{M}")
    if mismatches > 0:
        print("[smoke-batched] FAIL: per-query top-1 differs between paths")
        return 1

    # Throughput gate.
    store_ratio = (
        batched_store_ops / single_store_ops if single_store_ops > 0 else 0.0
    )
    retrieve_ratio = (
        batched_retrieve_ops / single_retrieve_ops
        if single_retrieve_ops > 0 else 0.0
    )
    print(f"[smoke-batched] throughput ratios: store {store_ratio:.1f}x, "
          f"retrieve {retrieve_ratio:.1f}x")

    floor = 10.0
    if store_ratio < floor:
        print(f"[smoke-batched] FAIL: store batched/single {store_ratio:.1f}x < {floor}x")
        return 1
    if retrieve_ratio < floor:
        print(f"[smoke-batched] FAIL: retrieve batched/single {retrieve_ratio:.1f}x < {floor}x")
        return 1

    print(f"[smoke-batched] PASS: store {store_ratio:.1f}x, retrieve {retrieve_ratio:.1f}x")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
