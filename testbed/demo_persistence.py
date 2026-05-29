"""Demo: substrate-as-persistent-memory on disk.

Creates a SubstrateMemory at N=2048 with M=512 stored facts, saves to
testbed_data/substrate_state/demo/, re-loads from disk, runs audit, and
prints metrics. Demonstrates the carved-storage portion of the testbed.

Run on remote:
   $env:KMP_DUPLICATE_LIB_OK = "TRUE"
   python testbed/demo_persistence.py
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

from testbed.api import MemoryBackend
from testbed.substrate_memory import SubstrateMemory


def main() -> int:
    print("=" * 60)
    print("Substrate persistence demo")
    print("=" * 60)

    N = 2048
    C = 8192
    M = 512
    seed = 7

    rng = np.random.default_rng(seed)

    # Phase 1: fresh substrate, store M facts, save to disk
    print(f"\nPhase 1: fresh SubstrateMemory N={N} C={C}, store M={M} facts.")
    t0 = time.perf_counter()
    sub = SubstrateMemory(N=N, codebook_kind="bsc", codebook_scale=4, beta=32.0)
    setup_s = time.perf_counter() - t0

    key_vecs = rng.standard_normal((M, N)).astype("float32")
    key_ids = [f"fact_{i:04d}" for i in range(M)]
    values = [f"payload_{i}" for i in range(M)]

    t0 = time.perf_counter()
    for kid, kv, v in zip(key_ids, key_vecs, values):
        sub.store(kid, kv, v)
    store_s = time.perf_counter() - t0
    print(f"  setup: {setup_s*1000:.1f}ms; store {M} items: {store_s*1000:.1f}ms")
    print(f"  per-store mean: {store_s*1e6/M:.1f}us")

    # Sanity: retrieve all and confirm recall
    hits = 0
    for kid, kv in zip(key_ids, key_vecs):
        r = sub.retrieve(kv)
        if r.key_id == kid:
            hits += 1
    recall = hits / M
    print(f"  recall_at_1 (in-memory): {recall:.4f}")

    # Audit before save
    audit_before = sub.audit()
    print(f"  pre-save audit: n_items={audit_before.n_items}")
    print(f"    KF-1 above_thresh_frac={audit_before.kf1_above_thresh_frac:.4f}")
    print(f"    KF-2 max_isolation={audit_before.kf2_max_isolation:.6f}")
    print(f"    TCFT mean_var_ratio={audit_before.tcft_mean_var_ratio:.4f}")
    print(f"    storage_bytes (pre-save mem footprint): {audit_before.storage_bytes:,}")

    # Save to carved location
    save_dir = Path("testbed_data/substrate_state/demo")
    save_dir.mkdir(parents=True, exist_ok=True)
    t0 = time.perf_counter()
    sub.save(save_dir)
    save_s = time.perf_counter() - t0
    print(f"\n  saved to {save_dir} in {save_s*1000:.1f}ms")

    # Inspect saved files
    saved_files = sorted(save_dir.iterdir())
    total_bytes = sum(p.stat().st_size for p in saved_files if p.is_file())
    print(f"  saved files ({total_bytes:,} bytes total):")
    for p in saved_files:
        if p.is_file():
            print(f"    {p.name:32s} {p.stat().st_size:>12,} bytes")

    # Phase 2: discard substrate, reload from disk, verify
    print(f"\nPhase 2: discard in-memory substrate, reload from disk, verify.")
    del sub

    t0 = time.perf_counter()
    sub2 = SubstrateMemory(N=N, codebook_kind="bsc", codebook_scale=4, beta=32.0)
    sub2.load(save_dir)
    load_s = time.perf_counter() - t0
    print(f"  load wall: {load_s*1000:.1f}ms")
    print(f"  n_items after load: {len(sub2)}")

    # Verify retrieval identity on the same key_vecs
    hits2 = 0
    sample_n = min(100, M)
    sample_idx = rng.choice(M, size=sample_n, replace=False)
    for idx in sample_idx:
        r = sub2.retrieve(key_vecs[idx])
        if r.key_id == key_ids[idx]:
            hits2 += 1
    recall2 = hits2 / sample_n
    print(f"  recall_at_1 (after reload, n={sample_n}): {recall2:.4f}")

    audit_after = sub2.audit()
    print(f"  post-load audit: n_items={audit_after.n_items}")
    print(f"    KF-1 above_thresh_frac={audit_after.kf1_above_thresh_frac:.4f}")
    print(f"    KF-2 max_isolation={audit_after.kf2_max_isolation:.6f}")
    print(f"    TCFT mean_var_ratio={audit_after.tcft_mean_var_ratio:.4f}")

    # Phase 3: edit and delete on reloaded substrate
    print(f"\nPhase 3: edit + delete operations on reloaded substrate.")
    target = key_ids[10]
    target_vec = key_vecs[10]
    print(f"  editing {target} value to 'edited_payload'")
    sub2.edit(target, "edited_payload")
    r = sub2.retrieve(target_vec)
    print(f"  retrieve after edit: key_id={r.key_id} value={r.value!r}")

    print(f"  deleting fact_0123")
    cert = sub2.delete("fact_0123")
    print(f"  certificate: erased={cert.erased} var_ratio={cert.var_ratio:.4f}")
    r = sub2.retrieve(key_vecs[123])
    print(f"  retrieve on deleted key vector: key_id={r.key_id} confidence={r.confidence:.4f}")
    print(f"  (the original fact_0123 should be GONE; either None or a different key_id)")

    # Final audit
    print(f"\nFinal substrate state: n_items={len(sub2)}")
    print("=" * 60)

    ok = recall >= 0.95 and recall2 >= 0.95 and audit_before.n_items == audit_after.n_items
    print(f"\nDEMO {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
