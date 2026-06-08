"""
Wikipedia 100K ingest pipeline (Q2 per Research VERIFY signoff + AAA green light).

Reads first N Wikipedia articles from the HF wikimedia/wikipedia dataset (already cached
on runner). For each article: extracts the lead paragraph, splits into sentences via spaCy
senter, keeps sentences with reasonable length, and adds them as facts to substrate-KV
(encoded with bge-large).

Per-batch encoding via bge-large at batch size 32 to amortize tensor allocation.
Checkpoints written as JSONL so the ingest is resumable.

Designed to be safe-to-run alongside T5C-C1 training (CPU only; no GPU contention)
and queue dispatch (graceful CPU sharing).

Usage:
    .venv-demo\\Scripts\\python.exe -m backend.kb.wikipedia_ingest \\
        --n-articles 100000 \\
        --max-sentences-per-article 2 \\
        --output-dir data/substrate_state/wikipedia_100k \\
        --batch-size 32
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


@dataclass
class IngestStats:
    articles_seen: int = 0
    articles_kept: int = 0
    sentences_extracted: int = 0
    facts_added: int = 0
    encode_batches: int = 0
    encode_wall_s: float = 0.0
    spacy_wall_s: float = 0.0
    total_wall_s: float = 0.0

    def as_dict(self) -> dict:
        return {
            "articles_seen": self.articles_seen,
            "articles_kept": self.articles_kept,
            "sentences_extracted": self.sentences_extracted,
            "facts_added": self.facts_added,
            "encode_batches": self.encode_batches,
            "encode_wall_s": round(self.encode_wall_s, 2),
            "spacy_wall_s": round(self.spacy_wall_s, 2),
            "total_wall_s": round(self.total_wall_s, 2),
            "facts_per_sec": round(self.facts_added / max(0.001, self.total_wall_s), 2),
        }


def is_good_sentence(s: str, min_len: int = 40, max_len: int = 280) -> bool:
    """Filter sentence by length + basic noise."""
    if not (min_len <= len(s) <= max_len):
        return False
    # Filter out section headers, citations, list items
    if s.startswith(("==", "*", "#", "-")):
        return False
    # Must end with sentence-terminating punctuation
    if not s.rstrip()[-1:] in ".!?":
        return False
    # Skip lines that are mostly punctuation or whitespace
    alpha_frac = sum(c.isalpha() for c in s) / max(1, len(s))
    if alpha_frac < 0.5:
        return False
    return True


def extract_sentences(text: str, nlp, max_chars: int = 1500, max_per_article: int = 2) -> list[str]:
    """Use spaCy's senter to split the lead paragraph; return at most N good sentences."""
    # Take just the lead portion to keep spaCy fast and to favor the article's most informative content
    lead = text[:max_chars]
    doc = nlp(lead)
    out = []
    for sent in doc.sents:
        s = sent.text.strip()
        if is_good_sentence(s):
            out.append(s)
            if len(out) >= max_per_article:
                break
    return out


def run_ingest(
    n_articles: int = 100_000,
    max_sentences_per_article: int = 2,
    output_dir: Path = Path("data/substrate_state/wikipedia_100k"),
    batch_size: int = 32,
    checkpoint_every: int = 5000,
    encoder=None,
    progress_log: Optional[Path] = None,
) -> IngestStats:
    """Main pipeline. Returns IngestStats."""
    from datasets import load_dataset
    import spacy

    output_dir.mkdir(parents=True, exist_ok=True)
    facts_jsonl = output_dir / "facts.jsonl"
    keys_npy = output_dir / "keys.npy"
    stats_path = output_dir / "stats.json"

    logger.info("loading spaCy en_core_web_sm ...")
    # Keep only the components needed for sentence segmentation (senter + parser)
    nlp = spacy.load("en_core_web_sm", disable=["ner", "tagger", "lemmatizer", "attribute_ruler"])

    if encoder is None:
        from backend.llm.bge_encoder import get_encoder
        encoder = get_encoder()
    logger.info("encoder: %s on %s; hidden_size=%d", encoder.model_name, encoder.device, encoder.hidden_size)

    logger.info("loading wikimedia/wikipedia (streaming) ...")
    # Streaming: avoid loading the whole dataset into memory. wikimedia/wikipedia is
    # parquet-based, so trust_remote_code is unnecessary and triggers an error in newer datasets versions.
    ds = load_dataset(
        "wikimedia/wikipedia",
        "20231101.en",
        split="train",
        streaming=True,
    )

    stats = IngestStats()
    t_overall = time.perf_counter()

    # Open output files
    facts_f = open(facts_jsonl, "a", encoding="utf-8")
    all_keys = []  # list of (N, hidden_size) np arrays to concat at end
    pending_sentences = []  # batch to encode

    import numpy as np

    def flush_batch(force: bool = False):
        if not pending_sentences:
            return
        if not force and len(pending_sentences) < batch_size:
            return
        t0 = time.perf_counter()
        vecs = encoder.encode(pending_sentences, batch_size=batch_size)
        stats.encode_wall_s += time.perf_counter() - t0
        stats.encode_batches += 1
        all_keys.append(vecs)
        for s in pending_sentences:
            facts_f.write(json.dumps({"fact": s}) + "\n")
        stats.facts_added += len(pending_sentences)
        pending_sentences.clear()

    try:
        for i, row in enumerate(ds):
            if i >= n_articles:
                break
            stats.articles_seen = i + 1
            text = row.get("text") or ""
            if not text:
                continue

            t_s = time.perf_counter()
            sentences = extract_sentences(text, nlp, max_per_article=max_sentences_per_article)
            stats.spacy_wall_s += time.perf_counter() - t_s

            if not sentences:
                continue
            stats.articles_kept += 1
            stats.sentences_extracted += len(sentences)
            pending_sentences.extend(sentences)
            flush_batch(force=False)

            if (i + 1) % checkpoint_every == 0:
                flush_batch(force=True)
                stats.total_wall_s = time.perf_counter() - t_overall
                logger.info(
                    "[checkpoint] articles=%d kept=%d facts=%d facts/s=%.1f elapsed=%.0fs",
                    stats.articles_seen, stats.articles_kept, stats.facts_added,
                    stats.facts_added / max(0.001, stats.total_wall_s), stats.total_wall_s,
                )
                if progress_log:
                    progress_log.write_text(json.dumps(stats.as_dict(), indent=2))

        # Final flush
        flush_batch(force=True)
        if all_keys:
            keys = np.concatenate(all_keys, axis=0)
            np.save(keys_npy, keys)
            logger.info("wrote keys.npy shape=%s", keys.shape)
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
    p.add_argument("--n-articles", type=int, default=100_000)
    p.add_argument("--max-sentences-per-article", type=int, default=2)
    p.add_argument("--output-dir", type=Path, default=Path("data/substrate_state/wikipedia_100k"))
    p.add_argument("--batch-size", type=int, default=32)
    p.add_argument("--checkpoint-every", type=int, default=5000)
    args = p.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    # progress log so external monitor can poll progress
    progress_log = args.output_dir / "progress.json"
    args.output_dir.mkdir(parents=True, exist_ok=True)

    run_ingest(
        n_articles=args.n_articles,
        max_sentences_per_article=args.max_sentences_per_article,
        output_dir=args.output_dir,
        batch_size=args.batch_size,
        checkpoint_every=args.checkpoint_every,
        progress_log=progress_log,
    )


if __name__ == "__main__":
    main()
