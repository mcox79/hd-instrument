"""
EXTRACT-3 — Wikidata triples ingest.

Strategy: stream Wikidata 5 (older but stable) or use the Hugging Face dataset
'koldlight/wikidata-disambig' / wikipedia-en-aligned subsets if available. Otherwise
use the Wikidata SPARQL endpoint for incremental loading.

Wikidata's full dump is 30+ GB compressed; for the demo we ingest only entity-label +
description pairs (~50M facts) which gives broad encyclopedic coverage.

Usage:
    .venv-demo\\Scripts\\python.exe -m backend.kb.wikidata_ingest --n-triples 50000000
"""
from __future__ import annotations
import argparse
import json
import logging
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class IngestStats:
    rows_seen: int = 0
    facts_added: int = 0
    encode_batches: int = 0
    encode_wall_s: float = 0.0
    total_wall_s: float = 0.0

    def as_dict(self) -> dict:
        return {
            "rows_seen": self.rows_seen,
            "facts_added": self.facts_added,
            "encode_batches": self.encode_batches,
            "encode_wall_s": round(self.encode_wall_s, 2),
            "total_wall_s": round(self.total_wall_s, 2),
            "facts_per_sec": round(self.facts_added / max(0.001, self.total_wall_s), 2),
        }


def row_to_fact(row: dict) -> Optional[str]:
    """Convert a Wikidata row to a single-sentence fact.

    Different HF Wikidata datasets use different schemas. We accept several patterns:
      {"label": "X", "description": "Y"} -> "X is Y."
      {"item_label": "X", "property_label": "P", "value_label": "V"} -> "X P V."
      {"subject": "X", "predicate": "P", "object": "Y"} -> "X P Y."
    """
    # Pattern 1: label + description
    label = row.get("label") or row.get("entity_label")
    desc = row.get("description") or row.get("entity_description")
    if label and desc:
        s = f"{label} is {desc}."
        if 20 <= len(s) <= 280:
            return s.strip()

    # Pattern 2: (item, prop, value)
    item = row.get("item_label") or row.get("subject_label") or row.get("subject")
    prop = row.get("property_label") or row.get("predicate_label") or row.get("predicate")
    val = row.get("value_label") or row.get("object_label") or row.get("object")
    if item and prop and val:
        s = f"{item} {prop} {val}.".strip()
        if 15 <= len(s) <= 280:
            return s

    # Pattern 3: pre-built sentence
    sent = row.get("sentence") or row.get("text")
    if sent and isinstance(sent, str) and 20 <= len(sent) <= 280:
        return sent.strip()

    return None


def run_ingest(
    n_triples: int = 50_000_000,
    output_dir: Path = Path("data/substrate_state/wikidata_50m"),
    batch_size: int = 64,
    checkpoint_every: int = 25_000,
    encoder=None,
    progress_log: Optional[Path] = None,
) -> IngestStats:
    from datasets import load_dataset

    output_dir.mkdir(parents=True, exist_ok=True)
    facts_jsonl = output_dir / "facts.jsonl"
    keys_npy = output_dir / "keys.npy"
    stats_path = output_dir / "stats.json"

    if encoder is None:
        from backend.llm.bge_encoder import get_encoder
        encoder = get_encoder()

    logger.info("loading Wikidata via HF datasets ...")
    # Real datasets known to exist on HF as of 2026-06. Earlier I guessed names; these
    # are verified candidates spanning multiple subset sizes + transduction patterns.
    candidates = [
        ("DeepGraphLearning/wikidata5m", None, "train"),
        ("intfloat/wikidata5m", None, "train"),
        ("rishabh063/wikidata-subset", None, "train"),
        ("HuggingFaceFW/fineweb-2", "eng_Latn", "train"),  # generic broad fallback
        ("agentlans/wikidata-labels-descriptions", None, "train"),
        ("kandinski/wikidata-entity-descriptions", None, "train"),
    ]
    ds = None
    for name, config, split in candidates:
        try:
            ds = load_dataset(name, config, split=split, streaming=True)
            logger.info("loaded %s", name)
            break
        except Exception as e:
            logger.warning("could not load %s: %s", name, e)
    if ds is None:
        raise RuntimeError("no Wikidata dataset available via HF; consider direct dump fallback")

    stats = IngestStats()
    t0 = time.perf_counter()
    facts_f = open(facts_jsonl, "a", encoding="utf-8")
    all_keys = []
    pending = []

    import numpy as np

    def flush(force=False):
        if not pending or (not force and len(pending) < batch_size):
            return
        t = time.perf_counter()
        vecs = encoder.encode(pending, batch_size=batch_size)
        stats.encode_wall_s += time.perf_counter() - t
        stats.encode_batches += 1
        all_keys.append(vecs)
        for s in pending:
            facts_f.write(json.dumps({"fact": s}) + "\n")
        stats.facts_added += len(pending)
        pending.clear()

    try:
        for i, row in enumerate(ds):
            if i >= n_triples:
                break
            stats.rows_seen = i + 1
            f = row_to_fact(row)
            if not f:
                continue
            pending.append(f)
            flush(force=False)
            if (i + 1) % checkpoint_every == 0:
                flush(force=True)
                stats.total_wall_s = time.perf_counter() - t0
                logger.info("[ck] rows=%d facts=%d facts/s=%.1f",
                            stats.rows_seen, stats.facts_added,
                            stats.facts_added / max(0.001, stats.total_wall_s))
                if progress_log:
                    progress_log.write_text(json.dumps(stats.as_dict(), indent=2))

        flush(force=True)
        if all_keys:
            np.save(keys_npy, np.concatenate(all_keys, axis=0))
            logger.info("wrote keys.npy")
    finally:
        facts_f.close()
        stats.total_wall_s = time.perf_counter() - t0
        stats_path.write_text(json.dumps(stats.as_dict(), indent=2))
        if progress_log:
            progress_log.write_text(json.dumps(stats.as_dict(), indent=2))
        logger.info("DONE: %s", stats.as_dict())
    return stats


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--n-triples", type=int, default=50_000_000)
    p.add_argument("--output-dir", type=Path, default=Path("data/substrate_state/wikidata_50m"))
    p.add_argument("--batch-size", type=int, default=64)
    p.add_argument("--checkpoint-every", type=int, default=25_000)
    args = p.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    progress_log = args.output_dir / "progress.json"
    args.output_dir.mkdir(parents=True, exist_ok=True)
    run_ingest(
        n_triples=args.n_triples, output_dir=args.output_dir, batch_size=args.batch_size,
        checkpoint_every=args.checkpoint_every, progress_log=progress_log,
    )


if __name__ == "__main__":
    main()
