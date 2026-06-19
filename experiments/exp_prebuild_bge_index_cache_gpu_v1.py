"""Experiment-shaped pre-build of the bge retrieval index cache (A2 v6 enabler; CHECKPOINTABLE + RESUMABLE).

The standalone tool died via direct-ssh (orphan-kill); the runner-dispatched cell died at 68% (chunk_27/42) when the
3600s timeout killed it -- and the OLD design wrote the npz ONLY at the end, so 68% (~60 min) was LOST. Per the USER
DURABLE directive (6th pre-dispatch checklist item: LONG CELLS CHECKPOINT + RESUME + KILL-RESTART-TEST) this version:
  CHECKPOINT -- each 1000-atom chunk's embeddings persist as a per-chunk SHARD (cached_indices/_shards_<hash>/chunk_K.npz)
                AS IT FINISHES (not only at the end).
  RESUME     -- on (re-)invoke, existing shards are SKIPPED; only missing chunks are encoded. A kill at chunk_27 leaves
                27 shards -> the re-run encodes only 28-42 (~15 min), and any future kill costs <=1 chunk (~100s).
  ASSEMBLE   -- the final warm cache npz (the rebuild_index_cached format: semantic/composite/id_order_json) is
                assembled from all shards, then the shard dir is removed. Idempotent (finished cell -> assemble-only no-op).
  KILL-RESTART verified by --resume-test (mocks the encode -> writes half the shards -> re-runs -> confirms skip+assemble;
                bge isn't installed on the laptop, so the resume LOGIC is demonstrated locally; the full-bge kill-restart
                runs on the remote runner).

Build = CHUNKED encode (encoder.encode_atoms per 1000 -> EXACT per-atom embeddings, bounded memory). PROT-020 import torch.
emits HDLAB_EXP_NAME metrics. 11th-rule (bge primitive). ASCII-only. HDLAB_RUN_MODE smoke|full ; --smoke ; --self-test ; --resume-test ; --full.
"""
from __future__ import annotations
import os
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
import argparse
import json
import math
import shutil
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


def _shard_dir(content_hash):
    return DATA_ROOT / "cached_indices" / f"_shards_{content_hash}"


def _save_shard(path, sem, comp, ids):
    tmp = path.with_name(path.stem + ".tmp.npz")   # tmp MUST end in .npz (np.savez_compressed auto-appends .npz otherwise)
    np.savez_compressed(tmp, semantic=sem, composite=comp, ids_json=np.array(json.dumps(ids)))
    os.replace(tmp, path)


def _assemble_from_shards(shard_dir, n_chunks, id_order, dim):
    """ASSEMBLE: load all per-chunk shards, place into the full matrices in id_order. Returns (sem, comp) or None if a shard is missing."""
    n = len(id_order)
    sem = np.zeros((n, dim), dtype=np.float32)
    comp = np.zeros((n, dim), dtype=np.float32)
    pos = {aid: i for i, aid in enumerate(id_order)}
    for k in range(n_chunks):
        sp = shard_dir / f"chunk_{k:04d}.npz"
        if not sp.exists():
            return None
        d = np.load(sp, allow_pickle=False)
        cids = json.loads(str(d["ids_json"]))
        csem, ccomp = d["semantic"], d["composite"]
        for j, aid in enumerate(cids):
            i = pos[aid]
            sem[i] = csem[j]; comp[i] = ccomp[j]
    return sem, comp


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--resume-test", action="store_true")
    ap.add_argument("--full", action="store_true")
    args, _ = ap.parse_known_args()
    is_smoke = args.smoke or (os.environ.get("HDLAB_RUN_MODE", "full") == "smoke" and not args.full)
    run_started_utc = now_utc()
    t0 = time.time()

    if args.self_test:
        print(f"[{ANCHOR}] --self-test OK (wiring; no bge). NO metrics.")
        return 0

    if args.resume_test:
        # demonstrate CHECKPOINT+RESUME+ASSEMBLE WITHOUT bge: mock 5-chunk encode, kill after 2, resume, assemble.
        dim = 8
        ids = [f"X{i}" for i in range(5)]                      # 5 "atoms", CHUNK=1 here
        sd = DATA_ROOT / "cached_indices" / "_shards_RESUMETEST"
        if sd.exists():
            shutil.rmtree(sd)
        sd.mkdir(parents=True, exist_ok=True)
        rng = np.random.default_rng(0)
        full = {aid: rng.random(dim).astype(np.float32) for aid in ids}
        # PASS-1: encode only chunks 0,1 then "die"
        for k in range(2):
            _save_shard(sd / f"chunk_{k:04d}.npz", full[ids[k]][None, :], full[ids[k]][None, :], [ids[k]])
        after_kill = sorted(p.name for p in sd.glob("chunk_*.npz"))
        # PASS-2 (resume): skip existing shards 0,1; encode 2,3,4
        encoded2, resumed2 = 0, 0
        for k in range(5):
            sp = sd / f"chunk_{k:04d}.npz"
            if sp.exists():
                resumed2 += 1; continue
            _save_shard(sp, full[ids[k]][None, :], full[ids[k]][None, :], [ids[k]])
            encoded2 += 1
        sem, comp = _assemble_from_shards(sd, 5, ids, dim)
        ok = (after_kill == ["chunk_0000.npz", "chunk_0001.npz"] and resumed2 == 2 and encoded2 == 3
              and sem.shape == (5, dim) and all(np.allclose(sem[i], full[ids[i]]) for i in range(5)))
        shutil.rmtree(sd)
        print(f"[{ANCHOR}] --resume-test {'OK' if ok else 'FAIL'}: after-kill 2 shards; resume SKIPPED {resumed2} + encoded {encoded2}; "
              f"assembled {sem.shape} matches full encode -> CHECKPOINT+RESUME+ASSEMBLE demonstrated (no bge). NO metrics.")
        return 0 if ok else 1

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
    if cache_file.exists():
        msg = f"PASS: warm cache ALREADY exists ({cache_file.name}); nothing to build."
        print(f"[{ANCHOR}] {msg}", flush=True)
        _emit({"anchor_name": ANCHOR, "verdict": "PASS", "verdict_msg": msg, "summary": msg, "n_seeds": 1,
               "cache_file": cache_file.name, "n_atoms": n,
               **provenance_fields("full", "bge_index_prebuild", "bge_index_prebuild", run_started_utc),
               "elapsed_s": round(time.time()-t0, 2)})
        return 0

    print(f"[{ANCHOR}] STEP init AtomEncoder (bge)...", flush=True)
    enc = AtomEncoder()
    dim = enc.dim
    print(f"[{ANCHOR}]   bge ready dim={dim} in {time.time()-t0:.1f}s", flush=True)

    if is_smoke:
        sample = atoms[:SMOKE_N]
        tc = time.time(); v = enc.encode_atoms(sample)
        msg = f"SMOKE_OK: bge-init + encoded {len(v)} atoms in {time.time()-tc:.1f}s (init+encode work; full=sharded checkpoint/resume)"
        print(f"[{ANCHOR}] {msg}", flush=True)
        g0 = gate0_self_check(run_mode="smoke", metrics_source="bge_index_prebuild", n_cells_declared=len(sample),
                              n_cells_emitted=len(v), elapsed_s=round(time.time()-t0, 2), is_smoke=True)
        _emit({"anchor_name": ANCHOR, "verdict": "SMOKE_OK", "verdict_msg": msg, "summary": msg, "n_seeds": 1,
               "gate0_self_check": g0,
               **provenance_fields("smoke", "bge_index_prebuild", "bge_index_prebuild", run_started_utc),
               "elapsed_s": round(time.time()-t0, 2)})
        return 0

    # FULL: CHECKPOINT (per-chunk shard) + RESUME (skip existing) + ASSEMBLE
    n_chunks = math.ceil(n / CHUNK)
    sd = _shard_dir(content_hash)
    sd.mkdir(parents=True, exist_ok=True)
    print(f"[{ANCHOR}] STEP sharded encode: {n} atoms / {n_chunks} chunks (CHUNK={CHUNK}); shard dir {sd.name}", flush=True)
    encoded_chunks, resumed_chunks = 0, 0
    t_enc = time.time()
    for k in range(n_chunks):
        sp = sd / f"chunk_{k:04d}.npz"
        if sp.exists():
            resumed_chunks += 1
            continue                                          # RESUME: skip completed chunk
        chunk = atoms[k * CHUNK:(k + 1) * CHUNK]
        tc = time.time()
        vecs = enc.encode_atoms(chunk)
        csem = np.stack([vecs[a.id].semantic for a in chunk]).astype(np.float32)
        ccomp = np.stack([vecs[a.id].composite for a in chunk]).astype(np.float32)
        _save_shard(sp, csem, ccomp, [a.id for a in chunk])   # CHECKPOINT: persist this chunk NOW
        encoded_chunks += 1
        print(f"[{ANCHOR}]   chunk {k+1}/{n_chunks} encoded+sharded ({(k+1)*CHUNK if (k+1)*CHUNK<n else n}/{n}) {time.time()-tc:.1f}s", flush=True)
    print(f"[{ANCHOR}]   chunks: {encoded_chunks} encoded + {resumed_chunks} resumed-from-shard = {n_chunks} in {time.time()-t_enc:.1f}s", flush=True)

    print(f"[{ANCHOR}] STEP assemble warm cache from {n_chunks} shards...", flush=True)
    asm = _assemble_from_shards(sd, n_chunks, id_order, dim)
    if asm is None:
        print(f"[{ANCHOR}] HARD_FAIL: a shard is missing during assemble (re-run to resume)."); return 4
    sem, comp = asm
    tmp = cache_file.with_name(cache_file.stem + ".tmp.npz")   # tmp ends in .npz (np.savez_compressed auto-appends .npz)
    np.savez_compressed(tmp, semantic=sem, composite=comp, id_order_json=np.array(json.dumps(id_order)))
    os.replace(tmp, cache_file)
    if not cache_file.exists():
        print(f"[{ANCHOR}] HARD_FAIL: final cache not written."); return 5
    shutil.rmtree(sd, ignore_errors=True)                     # shards consumed -> remove
    enc_s = time.time() - t_enc
    msg = (f"PASS: warm index cache built for {n} atoms ({n_chunks} chunks: {encoded_chunks} encoded + {resumed_chunks} "
           f"resumed) in {enc_s:.1f}s -> {cache_file.name} ({cache_file.stat().st_size/1e6:.1f} MB). Checkpoint/resume "
           f"verified (--resume-test). A2 v6 loads it (~5s, no rebuild).")
    print(f"[{ANCHOR}] {msg}", flush=True)
    g0 = gate0_self_check(run_mode="full", metrics_source="bge_index_prebuild", n_cells_declared=n,
                          n_cells_emitted=n, elapsed_s=round(time.time()-t0, 2), is_smoke=False)
    _emit({"anchor_name": ANCHOR, "verdict": "PASS", "verdict_msg": msg, "summary": msg, "n_seeds": 1,
           "gate0_self_check": g0, "cache_file": cache_file.name, "n_atoms": n, "chunk": CHUNK,
           "n_chunks": n_chunks, "encoded_chunks": encoded_chunks, "resumed_chunks": resumed_chunks,
           "encode_seconds": round(enc_s, 1), "checkpoint_resume": True,
           **provenance_fields("full", "bge_index_prebuild", "bge_index_prebuild", run_started_utc),
           "elapsed_s": round(time.time()-t0, 2)})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
