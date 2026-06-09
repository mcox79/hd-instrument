"""
EXTRACT-1 — ConceptNet ingest pipeline per Research OVERNIGHT_EXTRACTION_QUEUE.

ConceptNet 5.7 ships pre-structured triples (subject, relation, object) — no NER needed.
We download the english-only subset via HF datasets + encode each fact as a sentence
(template: "{subject} {relation_label} {object}") + add to the substrate-KV.

Writes:
  data/substrate_state/conceptnet_8m/
    facts.jsonl   one fact per line
    keys.npy      (N, 1024) bge-large embeddings
    stats.json    end-of-run summary
    progress.json updated at each checkpoint

Resumable via JSONL append.

Usage:
    .venv-demo\\Scripts\\python.exe -m backend.kb.conceptnet_ingest --n-triples 8000000 --output-dir data/substrate_state/conceptnet_8m
"""
from __future__ import annotations
import argparse
import json
import logging
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


# Friendly relation labels (ConceptNet uses URIs like /r/RelatedTo)
RELATION_LABEL = {
    "RelatedTo": "is related to",
    "IsA": "is a",
    "PartOf": "is part of",
    "HasA": "has",
    "UsedFor": "is used for",
    "CapableOf": "is capable of",
    "AtLocation": "is located at",
    "Causes": "causes",
    "HasSubevent": "has subevent",
    "HasPrerequisite": "requires",
    "HasProperty": "has the property",
    "MotivatedByGoal": "is motivated by",
    "ObstructedBy": "is obstructed by",
    "Desires": "desires",
    "CreatedBy": "is created by",
    "Synonym": "is synonymous with",
    "Antonym": "is opposite to",
    "DistinctFrom": "is distinct from",
    "DerivedFrom": "is derived from",
    "SymbolOf": "symbolizes",
    "DefinedAs": "is defined as",
    "MannerOf": "is a manner of",
    "LocatedNear": "is located near",
    "HasContext": "has the context",
    "SimilarTo": "is similar to",
    "EtymologicallyRelatedTo": "is etymologically related to",
    "EtymologicallyDerivedFrom": "is etymologically derived from",
    "CausesDesire": "causes desire for",
    "MadeOf": "is made of",
    "ReceivesAction": "receives action",
    "ExternalURL": "has external URL",
    "FormOf": "is a form of",
}


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


def normalize_concept(uri: str) -> str:
    """ConceptNet concept URI -> readable phrase. e.g. /c/en/dog -> 'dog'."""
    if not uri or not isinstance(uri, str):
        return ""
    parts = uri.split("/")
    if len(parts) < 4 or parts[1] != "c" or parts[2] != "en":
        return ""
    return parts[3].replace("_", " ")


def normalize_relation(uri: str) -> str:
    """ConceptNet relation URI -> friendly label."""
    if not uri:
        return ""
    name = uri.rsplit("/", 1)[-1] if "/" in uri else uri
    return RELATION_LABEL.get(name, name.lower())


def triple_to_fact(subj: str, rel: str, obj: str) -> Optional[str]:
    """Build a single-sentence fact from a ConceptNet triple."""
    s = normalize_concept(subj)
    r = normalize_relation(rel)
    o = normalize_concept(obj)
    if not (s and r and o):
        return None
    return f"{s} {r} {o}."


def run_ingest(
    n_triples: int = 8_000_000,
    output_dir: Path = Path("data/substrate_state/conceptnet_8m"),
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

    logger.info("loading ConceptNet via HF datasets ...")
    # peterwilli/conceptnet5 is an english slice; fall back to RyokoAI/Honyaku if not avail
    candidates = [
        ("peterwilli/conceptnet5", None, "train"),
        ("conceptnet5", None, "train"),
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
        raise RuntimeError("no ConceptNet dataset found via HF; consider direct CSV download from conceptnet.io")

    stats = IngestStats()
    t_overall = time.perf_counter()
    facts_f = open(facts_jsonl, "a", encoding="utf-8")
    all_keys = []
    pending = []

    import numpy as np

    def flush(force=False):
        if not pending or (not force and len(pending) < batch_size):
            return
        t0 = time.perf_counter()
        vecs = encoder.encode(pending, batch_size=batch_size)
        stats.encode_wall_s += time.perf_counter() - t0
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
            # Try common field names; ConceptNet rows usually have arg1/rel/arg2 or start/end/rel etc.
            subj = row.get("arg1") or row.get("subject") or row.get("start") or row.get("c1") or ""
            rel = row.get("rel") or row.get("relation") or row.get("predicate") or ""
            obj = row.get("arg2") or row.get("object") or row.get("end") or row.get("c2") or ""
            fact = triple_to_fact(subj, rel, obj)
            if not fact:
                continue
            pending.append(fact)
            flush(force=False)

            if (i + 1) % checkpoint_every == 0:
                flush(force=True)
                stats.total_wall_s = time.perf_counter() - t_overall
                logger.info("[ck] rows=%d facts=%d facts/s=%.1f elapsed=%.0fs",
                            stats.rows_seen, stats.facts_added,
                            stats.facts_added / max(0.001, stats.total_wall_s), stats.total_wall_s)
                if progress_log:
                    progress_log.write_text(json.dumps(stats.as_dict(), indent=2))

        flush(force=True)
        if all_keys:
            np.save(keys_npy, np.concatenate(all_keys, axis=0))
            logger.info("wrote keys.npy")
    finally:
        facts_f.close()
        stats.total_wall_s = time.perf_counter() - t_overall
        stats_path.write_text(json.dumps(stats.as_dict(), indent=2))
        if progress_log:
            progress_log.write_text(json.dumps(stats.as_dict(), indent=2))
        logger.info("DONE: %s", stats.as_dict())
    return stats


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--n-triples", type=int, default=8_000_000)
    p.add_argument("--output-dir", type=Path, default=Path("data/substrate_state/conceptnet_8m"))
    p.add_argument("--batch-size", type=int, default=64)
    p.add_argument("--checkpoint-every", type=int, default=25_000)
    args = p.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    progress_log = args.output_dir / "progress.json"
    args.output_dir.mkdir(parents=True, exist_ok=True)
    run_ingest(
        n_triples=args.n_triples,
        output_dir=args.output_dir,
        batch_size=args.batch_size,
        checkpoint_every=args.checkpoint_every,
        progress_log=progress_log,
    )


if __name__ == "__main__":
    main()
