"""
EXTRACT-4 — PubMed biomedical abstracts ingest (stretch).

Aligns with cycle 200 healthcare vertical (PP-209 DDI) demo asset. Uses HF mirror of
PubMed abstracts (pubmed dataset variants). spaCy senter is sufficient for sentence
extraction; full sciSpaCy NER is a future upgrade.

Usage:
    .venv-demo\\Scripts\\python.exe -m backend.kb.pubmed_ingest --n-abstracts 5000000
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


def is_good_sentence(s: str, min_len: int = 60, max_len: int = 320) -> bool:
    if not (min_len <= len(s) <= max_len):
        return False
    if s.startswith(("=", "*", "#", "-", "[", "(")):
        return False
    if not s.rstrip()[-1:] in ".!?":
        return False
    alpha = sum(c.isalpha() for c in s) / max(1, len(s))
    return alpha >= 0.55


def extract_sentences(text: str, nlp, max_chars: int = 1200, max_per_abstract: int = 2) -> list[str]:
    doc = nlp(text[:max_chars])
    out = []
    for sent in doc.sents:
        s = sent.text.strip()
        if is_good_sentence(s):
            out.append(s)
            if len(out) >= max_per_abstract:
                break
    return out


@dataclass
class IngestStats:
    abstracts_seen: int = 0
    abstracts_kept: int = 0
    facts_added: int = 0
    encode_batches: int = 0
    encode_wall_s: float = 0.0
    spacy_wall_s: float = 0.0
    total_wall_s: float = 0.0

    def as_dict(self) -> dict:
        return {
            "abstracts_seen": self.abstracts_seen,
            "abstracts_kept": self.abstracts_kept,
            "facts_added": self.facts_added,
            "encode_batches": self.encode_batches,
            "encode_wall_s": round(self.encode_wall_s, 2),
            "spacy_wall_s": round(self.spacy_wall_s, 2),
            "total_wall_s": round(self.total_wall_s, 2),
            "facts_per_sec": round(self.facts_added / max(0.001, self.total_wall_s), 2),
        }


def run_ingest(
    n_abstracts: int = 5_000_000,
    max_sentences_per_abstract: int = 2,
    output_dir: Path = Path("data/substrate_state/pubmed_5m"),
    batch_size: int = 64,
    checkpoint_every: int = 10_000,
    encoder=None,
    progress_log: Optional[Path] = None,
) -> IngestStats:
    from datasets import load_dataset
    import spacy

    output_dir.mkdir(parents=True, exist_ok=True)
    facts_jsonl = output_dir / "facts.jsonl"
    keys_npy = output_dir / "keys.npy"
    stats_path = output_dir / "stats.json"

    logger.info("loading spaCy ...")
    nlp = spacy.load("en_core_web_sm", disable=["ner", "tagger", "lemmatizer", "attribute_ruler"])

    if encoder is None:
        from backend.llm.bge_encoder import get_encoder
        encoder = get_encoder()

    logger.info("loading PubMed via HF datasets ...")
    candidates = [
        ("pubmed_qa", "pqa_unlabeled", "train"),
        ("ncbi_disease", None, "train"),
        ("scientific_papers", "pubmed", "train"),
        ("MedRAG/pubmed", None, "train"),
        ("ywchoi/pubmed_abstract_3", None, "train"),
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
        raise RuntimeError("no PubMed dataset available via HF")

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
            if i >= n_abstracts:
                break
            stats.abstracts_seen = i + 1
            text = (
                row.get("abstract") or row.get("text") or row.get("contexts") or row.get("question_long")
                or row.get("long_answer") or ""
            )
            if isinstance(text, list):
                text = " ".join(str(x) for x in text)
            if not text or len(text) < 80:
                continue
            ts = time.perf_counter()
            sents = extract_sentences(text, nlp, max_per_abstract=max_sentences_per_abstract)
            stats.spacy_wall_s += time.perf_counter() - ts
            if not sents:
                continue
            stats.abstracts_kept += 1
            pending.extend(sents)
            flush(force=False)
            if (i + 1) % checkpoint_every == 0:
                flush(force=True)
                stats.total_wall_s = time.perf_counter() - t0
                logger.info("[ck] abstracts=%d kept=%d facts=%d facts/s=%.1f",
                            stats.abstracts_seen, stats.abstracts_kept, stats.facts_added,
                            stats.facts_added / max(0.001, stats.total_wall_s))
                if progress_log:
                    progress_log.write_text(json.dumps(stats.as_dict(), indent=2))

        flush(force=True)
        if all_keys:
            np.save(keys_npy, np.concatenate(all_keys, axis=0))
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
    p.add_argument("--n-abstracts", type=int, default=5_000_000)
    p.add_argument("--max-sentences-per-abstract", type=int, default=2)
    p.add_argument("--output-dir", type=Path, default=Path("data/substrate_state/pubmed_5m"))
    p.add_argument("--batch-size", type=int, default=64)
    p.add_argument("--checkpoint-every", type=int, default=10_000)
    args = p.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    progress_log = args.output_dir / "progress.json"
    args.output_dir.mkdir(parents=True, exist_ok=True)
    run_ingest(
        n_abstracts=args.n_abstracts,
        max_sentences_per_abstract=args.max_sentences_per_abstract,
        output_dir=args.output_dir, batch_size=args.batch_size,
        checkpoint_every=args.checkpoint_every, progress_log=progress_log,
    )


if __name__ == "__main__":
    main()
