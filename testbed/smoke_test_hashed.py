"""Smoke gate for Path 9: hashed-codebook O(1) allocation lookups.

Validates that the persistent _used_key_rows / _used_value_rows sets eliminate
the O(C) set-build that bottlenecked production-scale batched writes
(N=1024, C=20K, batch=64 was 113 ops/s; smoke at C=2048 was 22x faster).

Checks:
  1. Throughput at N=1024 C=8192 batch=64 >= 565 ops/s (5x the 113 ops/s
     production baseline). We expect much higher.
  2. W parity: store_batch produces a W bit-close to a single-item store
     sequence on the same inputs (tolerance 1e-4 to absorb fp32 reordering).
  3. Persistent-set invariant: _used_key_rows == set(key_registry.values())
     and likewise for value rows, on both substrates after all stores.
  4. recall_at_1 >= 0.85 across all 2000 stored keys.

Exits 0 on pass, 1 on fail. Wall budget < 15s on a laptop CPU.
ASCII only; no emojis; no em dashes per CLAUDE.md / feedback_ascii_only.
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


# Baseline established at N=1024 C=20K batch=64 = 113 ops/s in production
# write_heavy_stream bench (per the Path 9 problem statement).
BASELINE_OPS = 113.0
THROUGHPUT_FLOOR = 5.0 * BASELINE_OPS  # 565 ops/s


def _make_data(M: int, N: int, seed: int = 23):
    rng = np.random.default_rng(seed)
    raw = rng.integers(0, 2, size=(M, N), dtype=np.int8).astype(np.float32)
    key_vecs = raw * 2.0 - 1.0
    key_ids = [f"h_{i:06d}" for i in range(M)]
    values = [f"hv_{i}" for i in range(M)]
    return key_ids, key_vecs, values


def _check_invariant(name: str, mem: SubstrateMemory) -> bool:
    expected_k = set(mem.key_registry.values())
    expected_v = set(mem.value_atom_registry.values())
    if mem._used_key_rows != expected_k:
        print(f"[smoke-hashed] FAIL: {name}._used_key_rows out of sync "
              f"(persistent={len(mem._used_key_rows)} "
              f"registry={len(expected_k)})")
        return False
    if mem._used_value_rows != expected_v:
        print(f"[smoke-hashed] FAIL: {name}._used_value_rows out of sync "
              f"(persistent={len(mem._used_value_rows)} "
              f"registry={len(expected_v)})")
        return False
    return True


def main() -> int:
    N = 1024
    C_scale = 8  # C = 8 * 1024 = 8192 (production-scale codebook)
    M = 2000
    B = 64
    print(f"[smoke-hashed] N={N} C={C_scale*N} M={M} batch_size={B}")
    print(f"[smoke-hashed] baseline={BASELINE_OPS:.0f} ops/s "
          f"floor={THROUGHPUT_FLOOR:.0f} ops/s (5x)")

    key_ids, key_vecs, values = _make_data(M, N, seed=23)

    # --- Batched path (post-fix throughput measurement) ---
    mem_batched = SubstrateMemory(
        N=N, codebook_kind="bsc", codebook_scale=C_scale, beta=32.0, seed=29
    )
    assert mem_batched.C == C_scale * N, (
        f"codebook size mismatch: got C={mem_batched.C}, "
        f"expected {C_scale*N}"
    )

    t0 = time.perf_counter_ns()
    for j in range(0, M, B):
        end = min(j + B, M)
        chunk = [(key_ids[i], key_vecs[i], values[i]) for i in range(j, end)]
        mem_batched.store_batch(chunk)
    batched_wall = (time.perf_counter_ns() - t0) / 1e9
    batched_ops = M / batched_wall if batched_wall > 0 else 0.0
    print(f"[smoke-hashed] batched store wall {batched_wall*1000:.1f} ms, "
          f"{batched_ops:.1f} ops/s")

    ratio = batched_ops / BASELINE_OPS if BASELINE_OPS > 0 else 0.0
    print(f"[smoke-hashed] throughput ratio vs 113 ops/s baseline: {ratio:.1f}x")

    # --- Single-item reference (for W parity) ---
    mem_single = SubstrateMemory(
        N=N, codebook_kind="bsc", codebook_scale=C_scale, beta=32.0, seed=29
    )
    t0 = time.perf_counter_ns()
    for i in range(M):
        mem_single.store(key_ids[i], key_vecs[i], values[i])
    single_wall = (time.perf_counter_ns() - t0) / 1e9
    single_ops = M / single_wall if single_wall > 0 else 0.0
    print(f"[smoke-hashed] single-item reference store wall "
          f"{single_wall*1000:.1f} ms, {single_ops:.1f} ops/s")

    # --- W parity (bit-close) ---
    W_diff = (mem_single.W - mem_batched.W).abs().max().item()
    W_frob = float(torch.linalg.norm(mem_single.W - mem_batched.W).item())
    print(f"[smoke-hashed] W parity: max|delta|={W_diff:.3e}, "
          f"||delta||_F={W_frob:.3e}")
    parity_tol = 1e-4
    if W_diff > parity_tol:
        print(f"[smoke-hashed] FAIL: W parity max|delta| {W_diff:.3e} "
              f"> {parity_tol}")
        return 1

    # Registry parity (both paths must allocate the same rows).
    if mem_single.key_registry != mem_batched.key_registry:
        print("[smoke-hashed] FAIL: key_registry mismatch")
        return 1
    if mem_single.value_atom_registry != mem_batched.value_atom_registry:
        print("[smoke-hashed] FAIL: value_atom_registry mismatch")
        return 1

    # --- Persistent-set invariant ---
    if not _check_invariant("single", mem_single):
        return 1
    if not _check_invariant("batched", mem_batched):
        return 1
    print("[smoke-hashed] occupancy-set invariant OK on both paths")

    # --- Recall@1 on all stored keys ---
    # Use retrieve_batch for speed; correctness is what we are checking.
    hits = 0
    for j in range(0, M, B):
        end = min(j + B, M)
        Q = key_vecs[j:end]
        results = mem_batched.retrieve_batch(Q)
        for off, r in enumerate(results):
            if r.key_id == key_ids[j + off]:
                hits += 1
    recall = hits / M
    print(f"[smoke-hashed] recall_at_1 = {recall:.4f} ({hits}/{M})")
    if recall < 0.85:
        print(f"[smoke-hashed] FAIL: recall {recall:.4f} < 0.85")
        return 1

    # --- Throughput gate ---
    if batched_ops < THROUGHPUT_FLOOR:
        print(f"[smoke-hashed] FAIL: throughput {batched_ops:.1f} ops/s "
              f"< floor {THROUGHPUT_FLOOR:.1f} ops/s "
              f"(ratio {ratio:.1f}x < 5x)")
        return 1

    print(f"[smoke-hashed] PASS: {batched_ops:.1f} ops/s ({ratio:.1f}x baseline), "
          f"recall {recall:.4f}, W parity OK, invariant OK")
    return 0


if __name__ == "__main__":
    try:
        rc = main()
    except AssertionError as e:
        print(f"[smoke-hashed] FAIL assertion: {e}", file=sys.stderr)
        rc = 2
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"[smoke-hashed] FAIL exception: {e}", file=sys.stderr)
        rc = 3
    sys.exit(rc)
