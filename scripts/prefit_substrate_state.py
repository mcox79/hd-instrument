"""
Pre-fit substrate state offline (Research's Option 2 from KILL_LOAD_PROFILE_PREFIT).

For each `data/substrate_state/<source>/` containing a keys.npy:
  1. Load and concatenate all sources' raw keys
  2. Compute global mu + W_whiten via ZCA on the combined set
  3. Apply per-source: write `<source>/keys_whitened.npy`
  4. Write global mu.npy + W_whiten.npy at data/substrate_state/

Backend's load_from_disk then mmaps these instead of re-fitting at startup
(12+ min ZCA cost eliminated; backend boot in <30 sec).

Usage:
    .venv-demo\\Scripts\\python.exe scripts\\prefit_substrate_state.py
    .venv-demo\\Scripts\\python.exe scripts\\prefit_substrate_state.py --skip wikidata_truthy_50m
"""
from __future__ import annotations
import argparse
import logging
import sys
import time
from pathlib import Path

import numpy as np

logger = logging.getLogger("prefit")


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )


def run_prefit(root: Path, skip: set, dim_check: int = 1024):
    """Pre-fit substrate state by computing global ZCA whitening over concatenated keys."""
    root = Path(root)
    sources = []
    for d in sorted(root.iterdir()):
        if not d.is_dir():
            continue
        if d.name.startswith("_"):
            continue
        if d.name in skip:
            logger.info("skip: %s", d.name)
            continue
        keys_p = d / "keys.npy"
        facts_p = d / "facts.jsonl"
        if not keys_p.exists() or not facts_p.exists():
            logger.info("skip %s: missing keys.npy or facts.jsonl", d.name)
            continue
        sources.append((d, keys_p, facts_p))

    if not sources:
        logger.error("no sources to prefit")
        return 1

    # Load all keys (raw)
    logger.info("loading raw keys from %d sources ...", len(sources))
    all_keys = []
    src_sizes = {}
    for d, keys_p, _ in sources:
        t0 = time.perf_counter()
        k = np.load(keys_p)
        if k.dtype != np.float32:
            k = k.astype(np.float32)
        if k.shape[1] != dim_check:
            logger.warning("%s: dim=%d does not match expected %d; skipping",
                           d.name, k.shape[1], dim_check)
            continue
        src_sizes[d.name] = k.shape[0]
        all_keys.append((d, k))
        logger.info("  %s: %d keys in %.1fs", d.name, k.shape[0], time.perf_counter() - t0)

    if not all_keys:
        logger.error("no valid keys loaded")
        return 1

    K = np.concatenate([k for _, k in all_keys], axis=0)
    N, D = K.shape
    logger.info("combined: %d keys at dim=%d (%.2f GB raw)",
                N, D, K.nbytes / (1024 ** 3))

    # Compute global mu + W_whiten via ZCA
    t0 = time.perf_counter()
    mu = K.mean(axis=0)
    logger.info("mean ok (%.1fs)", time.perf_counter() - t0)

    t0 = time.perf_counter()
    Kc = K - mu
    cov = (Kc.T @ Kc) / max(1, N) + 1e-3 * np.eye(D, dtype=np.float32)
    logger.info("covariance ok (%.1fs)", time.perf_counter() - t0)

    t0 = time.perf_counter()
    w, V = np.linalg.eigh(cov)
    w = np.clip(w, 1e-6, None)
    W_whiten = (V @ np.diag(1.0 / np.sqrt(w)) @ V.T).astype(np.float32)
    logger.info("eigendecomp + W_whiten ok (%.1fs)", time.perf_counter() - t0)

    # Apply to each source, write keys_whitened.npy + keys_normed.npy
    t0 = time.perf_counter()
    for d, k in all_keys:
        Kt = (k - mu) @ W_whiten
        norms = np.linalg.norm(Kt, axis=1, keepdims=True) + 1e-8
        Kt_normed = (Kt / norms).astype(np.float32)
        np.save(d / "keys_normed.npy", Kt_normed)
        logger.info("wrote %s (%.1f MB)", d / "keys_normed.npy",
                    Kt_normed.nbytes / (1024 ** 2))
    logger.info("apply + write ok (%.1fs total)", time.perf_counter() - t0)

    # Write global mu + W_whiten at root
    np.save(root / "mu.npy", mu.astype(np.float32))
    np.save(root / "W_whiten.npy", W_whiten)
    logger.info("wrote global mu.npy + W_whiten.npy at %s", root)

    # Metadata
    import json
    meta = {
        "total_keys": int(N),
        "dim": int(D),
        "sources": src_sizes,
        "raw_size_gb": round(K.nbytes / (1024 ** 3), 3),
        "use_whitening": True,
    }
    (root / "prefit_meta.json").write_text(json.dumps(meta, indent=2))
    logger.info("DONE: %s", meta)
    return 0


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path, default=Path("data/substrate_state"))
    p.add_argument("--skip", nargs="*", default=[],
                   help="source dir names to skip (e.g. wikidata_truthy_50m)")
    p.add_argument("--dim-check", type=int, default=1024)
    args = p.parse_args()
    setup_logging()
    return run_prefit(args.root, set(args.skip), args.dim_check)


if __name__ == "__main__":
    sys.exit(main() or 0)
