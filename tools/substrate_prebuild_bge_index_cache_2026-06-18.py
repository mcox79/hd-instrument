"""Pre-build the bge retrieval index cache (A2 v6 fix; Skunkworks robustness item 2).

v4/v5 hung at rebuild_index_cached: today's +13k atoms invalidated the cache -> A2 hits a COLD 41k rebuild that hangs
(GPU 0%, log frozen). This DECOUPLES the expensive index build from the cert run: build + cache the index ONCE here
(monitored, CHUNKED, fine-grained progress), then the A2 cell's rebuild_index_cached finds the WARM cache (~5s load,
no rebuild) -> no hang in the cert run.

Diagnostic-first: FINE progress prints pinpoint WHERE v5 stalled --
  (a) loading all_atoms (CPU/IO) ? (b) the bge.encode of 41k-at-once (memory/GPU) ?
CHUNKED encode (reuses encoder.encode_atoms per chunk -> EXACT same encoding logic, no divergence) bounds memory + shows
per-chunk progress. If it stalls at chunk-1 -> the bge encode itself is the issue (deeper). If it completes -> warm cache
written in the SAME npz format rebuild_index_cached reads (semantic, composite, id_order_json) at the SAME path.

HF_HUB_OFFLINE (bge cached locally). GPU step (encodes 41k) -> remote dispatch. ASCII-only. No LLM-reasoning (bge primitive, 11th-rule).
"""
from __future__ import annotations
import os
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
import json
import sys
import time
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
DATA_ROOT = REPO / "data" / "substrate_index"
CHUNK = 1000


def main() -> int:
    t_all = time.time()
    from backend.substrate_index.partition import PartitionedStore
    from backend.substrate_index.encode import AtomEncoder
    from backend.substrate_index.retrieve_cache import _compute_content_hash, _cache_path, _ENCODING_VERSION

    print(f"[prebuild] STEP load PartitionedStore (HF_HUB_OFFLINE={os.environ.get('HF_HUB_OFFLINE')})...", flush=True)
    ps = PartitionedStore(DATA_ROOT)
    print(f"[prebuild] STEP store.all_atoms() (v5-suspected-stall point A: CPU/IO load)...", flush=True)
    t0 = time.time()
    atoms = ps.all_atoms()
    n = len(atoms)
    print(f"[prebuild]   all_atoms loaded: {n} atoms in {time.time()-t0:.1f}s", flush=True)
    if n == 0:
        print("[prebuild] ERROR: 0 atoms"); return 1

    id_order = [a.id for a in atoms]
    content_hash = _compute_content_hash(id_order)
    cache_file = _cache_path(DATA_ROOT, n, content_hash)
    print(f"[prebuild] cache target: {cache_file.name} (n={n}, hash={content_hash}, enc={_ENCODING_VERSION})", flush=True)
    if cache_file.exists():
        print(f"[prebuild] cache ALREADY EXISTS -> warm; nothing to build. ({cache_file})"); return 0

    print(f"[prebuild] STEP init AtomEncoder (bge)...", flush=True)
    enc = AtomEncoder()
    dim = enc.dim
    print(f"[prebuild]   bge ready (dim={dim}). STEP CHUNKED encode (v5-suspected-stall point B: 41k-at-once bge.encode)...", flush=True)

    sem = np.zeros((n, dim), dtype=np.float32)
    comp = np.zeros((n, dim), dtype=np.float32)
    pos = {aid: i for i, aid in enumerate(id_order)}
    done = 0
    t_enc = time.time()
    for start in range(0, n, CHUNK):
        chunk = atoms[start:start + CHUNK]
        tc = time.time()
        vecs = enc.encode_atoms(chunk)               # EXACT encode logic, bounded to CHUNK texts
        for a in chunk:
            v = vecs[a.id]
            i = pos[a.id]
            sem[i] = v.semantic
            comp[i] = v.composite
        done += len(chunk)
        print(f"[prebuild]   encoded {done}/{n} ({100.0*done/n:.0f}%) chunk_{start//CHUNK} in {time.time()-tc:.1f}s", flush=True)
    print(f"[prebuild]   encode complete: {n} atoms in {time.time()-t_enc:.1f}s", flush=True)

    tmp = cache_file.with_suffix(".npz.tmp")
    np.savez_compressed(tmp, semantic=sem, composite=comp, id_order_json=np.array(json.dumps(id_order)))
    os.replace(tmp, cache_file)
    print(f"[prebuild] STEP saved warm cache -> {cache_file.name} ({cache_file.stat().st_size/1e6:.1f} MB)", flush=True)
    print(f"[prebuild] DONE: warm index cache built for {n} atoms in {time.time()-t_all:.1f}s. A2 cell will now load it (~5s, no rebuild).", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
