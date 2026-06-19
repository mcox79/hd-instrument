"""
EXTRACT-2 — arXiv abstracts ingest pipeline.

Loads arXiv from HF (CShorten/ML-ArXiv-Papers or arxiv_dataset). For each abstract:
extract 2-3 informative sentences via spaCy senter, encode with bge-large, append to
substrate-KV state.

Note: full sciSpaCy would be better for scientific NER but adds an install dependency.
For Phase 1 we extract sentences (sufficient for fact retrieval); upgrade to sciSpaCy
later if needed.

Usage:
    .venv-demo\\Scripts\\python.exe -m backend.kb.arxiv_ingest --n-papers 2000000 --output-dir data/substrate_state/arxiv_2m
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


def is_good_sentence(s: str, min_len: int = 50, max_len: int = 320) -> bool:
    if not (min_len <= len(s) <= max_len):
        return False
    if s.startswith(("=", "*", "#", "-", "[")):
        return False
    if not s.rstrip()[-1:] in ".!?":
        return False
    alpha = sum(c.isalpha() for c in s) / max(1, len(s))
    return alpha >= 0.5


def extract_sentences(text: str, nlp, max_chars: int = 1200, max_per_paper: int = 2) -> list[str]:
    lead = text[:max_chars]
    doc = nlp(lead)
    out = []
    for sent in doc.sents:
        s = sent.text.strip()
        if is_good_sentence(s):
            out.append(s)
            if len(out) >= max_per_paper:
                break
    return out


@dataclass
class IngestStats:
    papers_seen: int = 0
    papers_kept: int = 0
    facts_added: int = 0
    encode_batches: int = 0
    encode_wall_s: float = 0.0
    spacy_wall_s: float = 0.0
    total_wall_s: float = 0.0

    def as_dict(self) -> dict:
        return {
            "papers_seen": self.papers_seen,
            "papers_kept": self.papers_kept,
            "facts_added": self.facts_added,
            "encode_batches": self.encode_batches,
            "encode_wall_s": round(self.encode_wall_s, 2),
            "spacy_wall_s": round(self.spacy_wall_s, 2),
            "total_wall_s": round(self.total_wall_s, 2),
            "facts_per_sec": round(self.facts_added / max(0.001, self.total_wall_s), 2),
        }


def run_ingest(
    n_papers: int = 2_000_000,
    max_sentences_per_paper: int = 2,
    output_dir: Path = Path("data/substrate_state/arxiv_2m"),
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

    logger.info("loading arXiv via HF datasets ...")
    candidates = [
        ("CShorten/ML-ArXiv-Papers", None, "train"),
        ("ccdv/arxiv-classification", None, "train"),
        ("scientific_papers", "arxiv", "train"),
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
        raise RuntimeError("no arXiv dataset available; try Kaggle dump fallback")

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
            if i >= n_papers:
                break
            stats.papers_seen = i + 1
            abstract = row.get("abstract") or row.get("text") or row.get("summary") or ""
            if not abstract or len(abstract) < 100:
                continue
            t_s = time.perf_counter()
            sents = extract_sentences(abstract, nlp, max_per_paper=max_sentences_per_paper)
            stats.spacy_wall_s += time.perf_counter() - t_s
            if not sents:
                continue
            stats.papers_kept += 1
            pending.extend(sents)
            flush(force=False)

            if (i + 1) % checkpoint_every == 0:
                flush(force=True)
                stats.total_wall_s = time.perf_counter() - t_overall
                logger.info("[ck] papers=%d kept=%d facts=%d facts/s=%.1f",
                            stats.papers_seen, stats.papers_kept, stats.facts_added,
                            stats.facts_added / max(0.001, stats.total_wall_s))
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
    p.add_argument("--n-papers", type=int, default=2_000_000)
    p.add_argument("--max-sentences-per-paper", type=int, default=2)
    p.add_argument("--output-dir", type=Path, default=Path("data/substrate_state/arxiv_2m"))
    p.add_argument("--batch-size", type=int, default=64)
    p.add_argument("--checkpoint-every", type=int, default=10_000)
    args = p.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    progress_log = args.output_dir / "progress.json"
    args.output_dir.mkdir(parents=True, exist_ok=True)
    run_ingest(
        n_papers=args.n_papers,
        max_sentences_per_paper=args.max_sentences_per_paper,
        output_dir=args.output_dir,
        batch_size=args.batch_size,
        checkpoint_every=args.checkpoint_every,
        progress_log=progress_log,
    )


if __name__ == "__main__":
    main()
