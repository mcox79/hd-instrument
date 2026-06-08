"""Incremental checkpoint helper for LONG-running experiment cells (structural fix 2026-06-08).

Any cell whose wall time may exceed ~5 min, or that ingests/encodes large data, MUST use this so that:
  (1) progress is persisted as it goes (per-unit JSONL) -> partial results survive a kill/crash,
  (2) large arrays (e.g. embeddings) are saved in chunks to disk -> the output is REUSABLE + the run is RESUMABLE,
  (3) the run can resume from disk instead of recomputing everything.

Rationale: the standard cell template only writes metrics ONCE at the end (fine for fast cells, catastrophic for long
ones -- wikipedia_ingest_1m / f1_substrate_kv_m50000 / legal_citation_1000seed all lost everything on kill). See
memory feedback-vet-experiments-before-queue.

Usage:
    from experiments._stream import StreamWriter
    sw = StreamWriter(out_dir)                       # out_dir from get_output_dir(ANCHOR_NAME)
    done = sw.done_units()                           # set of unit indices already completed (resume)
    for i, item in enumerate(items):
        if i in done:  continue                      # skip already-done units (resume)
        emb = encode(item)
        sw.save_chunk("emb", i, emb)                 # chunked .npy on disk (reusable KB)
        sw.append({"i": i, "ok": True})              # per-unit JSONL + flush
    arr = sw.load_chunks("emb")                      # reassemble saved chunks (np.concatenate)
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np


class StreamWriter:
    def __init__(self, out_dir, name: str = "progress"):
        self.dir = Path(out_dir); self.dir.mkdir(parents=True, exist_ok=True)
        self.jsonl = self.dir / (name + ".jsonl")
        self.chunkdir = self.dir / "chunks"; self.chunkdir.mkdir(exist_ok=True)
        self._f = open(self.jsonl, "a", encoding="utf-8")

    def append(self, rec: dict):
        """Append one unit's result to progress.jsonl and flush (durable per-unit)."""
        self._f.write(json.dumps(rec) + "\n"); self._f.flush()

    def save_chunk(self, name: str, idx: int, array):
        """Save a numpy array chunk to disk (reusable + resumable)."""
        np.save(self.chunkdir / ("%s_%08d.npy" % (name, idx)), np.asarray(array))

    def load_chunks(self, name: str):
        """Reassemble all saved chunks for `name` in index order (np.concatenate), or None if none."""
        fs = sorted(self.chunkdir.glob("%s_*.npy" % name))
        if not fs:
            return None
        return np.concatenate([np.load(f) for f in fs], axis=0)

    def done_units(self) -> set:
        """Set of unit indices already recorded in progress.jsonl (for resume). Expects records with key 'i'."""
        done = set()
        if self.jsonl.exists():
            for line in open(self.jsonl, encoding="utf-8"):
                line = line.strip()
                if not line:
                    continue
                try:
                    r = json.loads(line)
                    if "i" in r:
                        done.add(int(r["i"]))
                except Exception:
                    pass
        return done

    def records(self) -> list:
        """All progress records (for final aggregation)."""
        out = []
        if self.jsonl.exists():
            for line in open(self.jsonl, encoding="utf-8"):
                line = line.strip()
                if line:
                    try:
                        out.append(json.loads(line))
                    except Exception:
                        pass
        return out

    def close(self):
        try:
            self._f.flush(); self._f.close()
        except Exception:
            pass
