"""Bge retrieval index cache (Cycle 47/48 infrastructure).

Per Research CYCLE_47_HARDPASS_APPROVE Q3 + Cycle 48 unstick Q4 GO:
15-minute rebuild_index() wall-clock dominates iteration cadence. Cache the
semantic + composite matrices + id_order keyed by corpus content hash so the
NEXT load is ~5s instead of ~15min.

Cache files:
- {root}/cached_indices/bge_large_{n_atoms}_{hash8}.npz
  Contains: semantic_matrix (n, dim), composite_matrix (n, dim), id_order (list)
- Invalidation: content_hash of sorted atom_ids changes => rebuild
- Also supports --rebuild flag to force fresh build

Load path: rebuild_index_cached(retriever) tries cache first; falls back to full
rebuild on miss, then saves the result.
"""
from __future__ import annotations

import hashlib
import json
import logging
import time
from pathlib import Path
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)


def _compute_content_hash(id_order: list[str]) -> str:
    """Stable hash of the sorted atom id list (cache key)."""
    payload = json.dumps(sorted(id_order)).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()[:8]


def _cache_dir(root: Path) -> Path:
    out = root / "cached_indices"
    out.mkdir(parents=True, exist_ok=True)
    return out


_ENCODING_VERSION = "v2_name"  # bumped Cycle 49 Option 1: bge-NAME encoding (name + id_tokens + aliases) replaces description-based v1


def _cache_path(root: Path, n_atoms: int, content_hash: str) -> Path:
    return _cache_dir(root) / f"bge_large_{_ENCODING_VERSION}_{n_atoms}_{content_hash}.npz"


def rebuild_index_cached(retriever, data_root: Path, force_rebuild: bool = False) -> bool:
    """Build retriever index, using cache if available.

    Returns True if loaded from cache, False if rebuilt from scratch.
    Caller still owns the retriever object; this just populates its internal state.
    """
    atoms = retriever.store.all_atoms()
    if not atoms:
        retriever.rebuild_index()
        return False
    id_order = [a.id for a in atoms]
    content_hash = _compute_content_hash(id_order)
    n_atoms = len(atoms)

    cache_file = _cache_path(data_root, n_atoms, content_hash)
    if not force_rebuild and cache_file.exists():
        t0 = time.time()
        try:
            data = np.load(cache_file, allow_pickle=False)
            sem = data["semantic"]
            comp = data["composite"]
            cached_ids = json.loads(str(data["id_order_json"]))
            if cached_ids == id_order and sem.shape[0] == n_atoms:
                retriever._semantic_matrix = sem
                retriever._composite_matrix = comp
                retriever._id_order = cached_ids
                # Reconstruct minimal _vectors dict (some callers expect it)
                # We skip full re-population since callers mostly use semantic()
                retriever._vectors = {}
                logger.info("retriever index loaded from cache (%d atoms; %.2fs)",
                            n_atoms, time.time() - t0)
                return True
            else:
                logger.warning("cache hash matched but content mismatched; rebuilding")
        except Exception as e:
            logger.warning("cache load failed (%s); rebuilding", str(e)[:80])

    # Full rebuild
    t0 = time.time()
    retriever.rebuild_index()
    elapsed = time.time() - t0
    logger.info("retriever index FULL rebuild done in %.1fs (%d atoms)", elapsed, n_atoms)

    # Save to cache
    try:
        sem = retriever._semantic_matrix
        comp = retriever._composite_matrix
        if sem is None or comp is None:
            return False
        np.savez_compressed(
            cache_file,
            semantic=sem,
            composite=comp,
            id_order_json=np.array(json.dumps(retriever._id_order)),
        )
        logger.info("cached retriever index -> %s (%d atoms)", cache_file.name, n_atoms)
    except Exception as e:
        logger.warning("cache save failed (%s)", str(e)[:80])

    return False


def list_caches(data_root: Path) -> list[dict]:
    """List existing cache files with metadata."""
    out = []
    for f in sorted(_cache_dir(data_root).glob("bge_large_*.npz")):
        out.append({
            "file": f.name,
            "size_mb": round(f.stat().st_size / 1024 / 1024, 2),
            "mtime": time.strftime("%Y-%m-%d %H:%M",
                                    time.localtime(f.stat().st_mtime)),
        })
    return out


def prune_caches(data_root: Path, keep_latest_n: int = 3) -> int:
    """Drop oldest cache files; keep N most recent. Returns number deleted."""
    files = sorted(_cache_dir(data_root).glob("bge_large_*.npz"),
                   key=lambda f: f.stat().st_mtime)
    if len(files) <= keep_latest_n:
        return 0
    to_delete = files[:-keep_latest_n]
    for f in to_delete:
        f.unlink()
    return len(to_delete)
