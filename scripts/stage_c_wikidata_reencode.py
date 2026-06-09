"""
Stage C: re-encode Wikidata triples.jsonl through the FHRR substrate library.

Per Research STAGE_C_5_ANSWERS:
  Reads `triples.jsonl` (subj_Q, pred_P, obj_Q-or-literal) emitted by Stage A
  retrofitted `wikidata_dump_ingest.py`. Feeds each triple to
  substrate.wikidata_substrate.WikidataSubstrate via add_triple(). Optionally applies
  REC-5 1-bit quantization (compact mode). Persists per-predicate sharded codebook +
  Q-code FHRR cache to disk.

Output:
  data/substrate_state/wikidata_truthy_50m_v2/
    shards/<predicate_code>.npz   per-predicate keys.npy (full precision OR 1-bit packed)
    shards/<predicate_code>.json  per-predicate {objects, subject_codes} parallel arrays
    qcode_cache.npz               full-precision Q-code -> FHRR cache for retrieval
    meta.json                     {dim, block_size, use_ghrr, compact, source_path, n_triples}

Usage:
    .venv-demo\\Scripts\\python.exe scripts\\stage_c_wikidata_reencode.py \\
        --triples data/substrate_state/wikidata_truthy_50m/triples.jsonl \\
        --output-dir data/substrate_state/wikidata_truthy_50m_v2 \\
        --compact
"""
from __future__ import annotations
import argparse
import json
import logging
import sys
import time
from pathlib import Path
from typing import Optional

import numpy as np

logger = logging.getLogger("stage_c_reencode")


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )


def persist_substrate(ws, output_dir: Path, compact: bool, meta_extra: dict) -> dict:
    """Persist per-predicate shards + Q-code cache to disk."""
    shards_dir = output_dir / "shards"
    shards_dir.mkdir(parents=True, exist_ok=True)

    counts = {}
    for predicate, shard in ws._shards.items():
        if shard._keys_matrix is None or shard._keys_matrix.shape[0] == 0:
            continue
        keys_path = shards_dir / f"{predicate}.npz"
        if compact and predicate in ws._quantized_shards:
            np.savez_compressed(keys_path, keys_quant=ws._quantized_shards[predicate])
        else:
            np.savez_compressed(keys_path, keys=shard._keys_matrix)
        meta_path = shards_dir / f"{predicate}.json"
        meta_path.write_text(json.dumps({
            "predicate": predicate,
            "n_triples": len(shard.objects),
            "objects": shard.objects,
            "subject_codes": shard.subject_codes,
        }, ensure_ascii=False))
        counts[predicate] = len(shard.objects)

    # Persist Q-code FHRR cache (full precision; only codes actually encountered)
    qcache_path = output_dir / "qcode_cache.npz"
    ws.qcode_mapper.save_to_disk(qcache_path)

    meta = {
        "dim": ws.dim,
        "block_size": ws.block_size,
        "use_ghrr": ws.use_ghrr,
        "compact": compact,
        "n_triples_total": sum(counts.values()),
        "n_predicates": len(counts),
        "shard_sizes": counts,
        "qcode_cache_size": len(ws.qcode_mapper),
        **meta_extra,
    }
    meta_path = output_dir / "meta.json"
    meta_path.write_text(json.dumps(meta, indent=2))
    return meta


def reencode(triples_path: Path, output_dir: Path, dim: int, use_ghrr: bool,
             block_size: int, compact: bool, batch_size: int = 50_000,
             checkpoint_every: int = 250_000, max_triples: Optional[int] = None) -> dict:
    """Stream triples.jsonl; feed each to WikidataSubstrate; persist."""
    from substrate.wikidata_substrate import WikidataSubstrate

    output_dir.mkdir(parents=True, exist_ok=True)
    progress_path = output_dir / "progress.json"

    ws = WikidataSubstrate(dim=dim, use_ghrr=use_ghrr, block_size=block_size)
    n_seen = 0
    n_added = 0
    t0 = time.perf_counter()

    logger.info("reading %s ...", triples_path)
    with open(triples_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            n_seen += 1
            try:
                tri = json.loads(line)
                ws.add_triple(tri["s"], tri["p"], tri["o"])
                n_added += 1
            except (KeyError, ValueError, json.JSONDecodeError):
                continue
            if max_triples and n_added >= max_triples:
                logger.info("max_triples=%d reached", max_triples)
                break
            if n_added % checkpoint_every == 0:
                elapsed = time.perf_counter() - t0
                rate = n_added / max(0.001, elapsed)
                logger.info("[ck] added=%d seen=%d rate=%.0f triples/s predicates=%d cache=%d",
                            n_added, n_seen, rate, len(ws._shards), len(ws.qcode_mapper))
                progress_path.write_text(json.dumps({
                    "n_seen": n_seen,
                    "n_added": n_added,
                    "elapsed_s": round(elapsed, 1),
                    "rate_triples_per_s": round(rate, 1),
                    "n_predicates": len(ws._shards),
                    "qcode_cache_size": len(ws.qcode_mapper),
                }, indent=2))

    logger.info("finalizing %s ...", "compact" if compact else "full-precision")
    if compact:
        ws.finalize_compact()
    else:
        ws.finalize()

    meta = persist_substrate(ws, output_dir, compact=compact, meta_extra={
        "source_path": str(triples_path),
        "n_seen": n_seen,
        "n_added": n_added,
        "elapsed_s": round(time.perf_counter() - t0, 1),
    })
    progress_path.write_text(json.dumps(meta, indent=2))
    logger.info("DONE: %s", meta)
    return meta


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--triples", type=Path, required=True)
    p.add_argument("--output-dir", type=Path, required=True)
    p.add_argument("--dim", type=int, default=8192)
    p.add_argument("--use-ghrr", action="store_true",
                   help="non-commutative block-diagonal binding (REC-4); slower but multi-hop ordered")
    p.add_argument("--block-size", type=int, default=2, help="GHRR block size (only if --use-ghrr)")
    p.add_argument("--compact", action="store_true",
                   help="apply REC-5 1-bit quantization for 32x storage compression")
    p.add_argument("--batch-size", type=int, default=50_000)
    p.add_argument("--checkpoint-every", type=int, default=250_000)
    p.add_argument("--max-triples", type=int, default=None,
                   help="optional cap; default is read everything")
    args = p.parse_args()

    setup_logging()
    reencode(
        triples_path=args.triples,
        output_dir=args.output_dir,
        dim=args.dim,
        use_ghrr=args.use_ghrr,
        block_size=args.block_size,
        compact=args.compact,
        batch_size=args.batch_size,
        checkpoint_every=args.checkpoint_every,
        max_triples=args.max_triples,
    )


if __name__ == "__main__":
    sys.exit(main() or 0)
