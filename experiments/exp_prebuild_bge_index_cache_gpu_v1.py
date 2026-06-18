"""Experiment-shaped pre-build of the bge retrieval index cache (A2 v6 enabler; runner-dispatchable).

The standalone tool (tools/substrate_prebuild_bge_index_cache_2026-06-18.py) died silently via direct-ssh launch
(orphan-kill on ssh-session teardown, OR a silent bge-init crash). This cell-shaped version runs via the NORMAL runner
pipeline (persistent process -> ssh-disconnect-robust) + satisfies PROT-020 (literal import torch) + emits metrics.json
(queue_add gate). Running it via the runner ALSO disambiguates: if it dies at bge-init via the runner too -> a real
bge-init crash (deeper), not ssh-orphan.

Build = CHUNKED encode (encoder.encode_atoms per 1000 -> EXACT same per-atom embeddings, bounded memory -> fixes the
41k-at-once hang that killed v4/v5) -> write the warm cache in the rebuild_index_cached npz format at the same path.
Then A2 v6 (cell 4d62101a, unchanged) finds the EXACT warm cache -> ~5s load, no rebuild, no hang.

--self-test: exit 0, no bge (wiring). --smoke: bge-init + encode a SMALL chunk (validates bge init + encode cheaply,
catches an init crash for cents) + metrics, NO real cache write. full: chunked 41k -> warm cache -> metrics.
11th-rule (bge primitive, no LLM). ASCII-only. HDLAB_RUN_MODE smoke|full ; --smoke ; --self-test ; --full.
"""
from __future__ import annotations
import os
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
import argparse
import json
import sys
import time
from pathlib import Path

import torch  # noqa: F401  # PROT-020 static scanner (GPU cell; bge via AtomEncoder)
import numpy as np

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _cell_provenance import provenance_fields, now_utc, gate0_self_check

ANCHOR = "prebuild_bge_index_cache_gpu_v1"
_EXP_NAME = os.environ.get("HDLAB_EXP_NAME")
OUT = REPO / "data" / (f"exp_{_EXP_NAME}" if _EXP_NAME else ANCHOR)
DATA_ROOT = REPO / "data" / "substrate_index"
CHUNK = 1000
SMOKE_N = 200


def _emit(metrics):
    OUT.mkdir(parents=True, exist_ok=True)
    tmp = OUT / "metrics.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2); f.flush(); os.fsync(f.fileno())
    os.replace(tmp, OUT / "metrics.json")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--full", action="store_true")
    args, _ = ap.parse_known_args()
    is_smoke = args.smoke or (os.environ.get("HDLAB_RUN_MODE", "full") == "smoke" and not args.full)
    run_started_utc = now_utc()
    t0 = time.time()

    if args.self_test:
        print(f"[{ANCHOR}] --self-test OK (wiring; no bge). NO metrics.")
        return 0

    from backend.substrate_index.partition import PartitionedStore
    from backend.substrate_index.encode import AtomEncoder
    from backend.substrate_index.retrieve_cache import _compute_content_hash, _cache_path

    print(f"[{ANCHOR}] STEP load store (HF_HUB_OFFLINE={os.environ.get('HF_HUB_OFFLINE')})...", flush=True)
    ps = PartitionedStore(DATA_ROOT)
    print(f"[{ANCHOR}] STEP all_atoms()...", flush=True)
    atoms = ps.all_atoms(); n = len(atoms)
    print(f"[{ANCHOR}]   {n} atoms in {time.time()-t0:.1f}s", flush=True)
    id_order = [a.id for a in atoms]
    content_hash = _compute_content_hash(id_order)
    cache_file = _cache_path(DATA_ROOT, n, content_hash)
    print(f"[{ANCHOR}] cache target: {cache_file.name} (exists={cache_file.exists()})", flush=True)

    print(f"[{ANCHOR}] STEP init AtomEncoder (bge)...", flush=True)
    enc = AtomEncoder()
    dim = enc.dim
    print(f"[{ANCHOR}]   bge ready dim={dim} in {time.time()-t0:.1f}s", flush=True)

    if is_smoke:
        # validate bge-init + encode on a SMALL chunk (catches an init/encode crash cheaply); NO real cache write
        sample = atoms[:SMOKE_N]
        tc = time.time()
        v = enc.encode_atoms(sample)
        msg = f"SMOKE_OK: bge-init + encoded {len(v)} atoms in {time.time()-tc:.1f}s (init+encode work; full build will run chunked)"
        print(f"[{ANCHOR}] {msg}", flush=True)
        g0 = gate0_self_check(run_mode="smoke", metrics_source="bge_index_prebuild",
                              n_cells_declared=len(sample), n_cells_emitted=len(v),
                              elapsed_s=round(time.time()-t0, 2), is_smoke=True)
        _emit({"anchor_name": ANCHOR, "verdict": "SMOKE_OK", "verdict_msg": msg, "summary": msg,
               "n_seeds": 1, "gate0_self_check": g0,
               **provenance_fields("smoke", "bge_index_prebuild", "bge_index_prebuild", run_started_utc),
               "elapsed_s": round(time.time()-t0, 2)})
        return 0

    if cache_file.exists():
        msg = f"PASS: warm cache ALREADY exists ({cache_file.name}); nothing to build."
        print(f"[{ANCHOR}] {msg}", flush=True)
        _emit({"anchor_name": ANCHOR, "verdict": "PASS", "verdict_msg": msg, "summary": msg, "n_seeds": 1,
               "cache_file": cache_file.name, "n_atoms": n,
               **provenance_fields("full", "bge_index_prebuild", "bge_index_prebuild", run_started_utc),
               "elapsed_s": round(time.time()-t0, 2)})
        return 0

    print(f"[{ANCHOR}] STEP CHUNKED encode {n} atoms ({CHUNK}/chunk)...", flush=True)
    sem = np.zeros((n, dim), dtype=np.float32)
    comp = np.zeros((n, dim), dtype=np.float32)
    pos = {aid: i for i, aid in enumerate(id_order)}
    done = 0
    t_enc = time.time()
    for start in range(0, n, CHUNK):
        chunk = atoms[start:start + CHUNK]
        tc = time.time()
        vecs = enc.encode_atoms(chunk)
        for a in chunk:
            v = vecs[a.id]; i = pos[a.id]
            sem[i] = v.semantic; comp[i] = v.composite
        done += len(chunk)
        print(f"[{ANCHOR}]   encoded {done}/{n} ({100.0*done/n:.0f}%) chunk_{start//CHUNK} {time.time()-tc:.1f}s", flush=True)
    enc_s = time.time() - t_enc

    tmp = cache_file.with_suffix(".npz.tmp")
    np.savez_compressed(tmp, semantic=sem, composite=comp, id_order_json=np.array(json.dumps(id_order)))
    os.replace(tmp, cache_file)
    msg = (f"PASS: warm index cache built for {n} atoms ({CHUNK}/chunk) in {enc_s:.1f}s encode -> {cache_file.name} "
           f"({cache_file.stat().st_size/1e6:.1f} MB). A2 v6 loads it (~5s, no rebuild).")
    print(f"[{ANCHOR}] {msg}", flush=True)
    g0 = gate0_self_check(run_mode="full", metrics_source="bge_index_prebuild",
                          n_cells_declared=n, n_cells_emitted=done, elapsed_s=round(time.time()-t0, 2), is_smoke=False)
    _emit({"anchor_name": ANCHOR, "verdict": "PASS", "verdict_msg": msg, "summary": msg, "n_seeds": 1,
           "gate0_self_check": g0, "cache_file": cache_file.name, "n_atoms": n, "chunk": CHUNK,
           "encode_seconds": round(enc_s, 1),
           **provenance_fields("full", "bge_index_prebuild", "bge_index_prebuild", run_started_utc),
           "elapsed_s": round(time.time()-t0, 2)})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
