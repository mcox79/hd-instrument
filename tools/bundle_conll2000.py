"""Bundle CoNLL-2000 chunking dataset for Exp-Dev Priority 3 chunking cell.

Per Research CONLL_2000_BUNDLE_HIGH_PRIORITY request 2026-06-12:
- Source: standard CoNLL-2000 distribution
- Format: experiments/data/conll2000.json with tokens/pos/chunk_bio fields
- Splits: train + test

Sentences are separated by blank lines in source files.
Each non-blank line is `word POS_tag chunk_BIO_tag`.
"""
from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s | %(message)s")
log = logging.getLogger("bundle_conll2000")


def parse_conll2000(file_path: Path) -> list[dict]:
    """Parse CoNLL-2000 file into list of sentences.

    Each sentence: {'tokens': [...], 'pos': [...], 'chunk_bio': [...]}
    """
    sentences = []
    current_tokens: list[str] = []
    current_pos: list[str] = []
    current_chunks: list[str] = []
    with file_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.rstrip()
            if not line:
                # blank line = sentence boundary
                if current_tokens:
                    sentences.append({
                        "tokens": current_tokens,
                        "pos": current_pos,
                        "chunk_bio": current_chunks,
                    })
                    current_tokens = []
                    current_pos = []
                    current_chunks = []
                continue
            parts = line.split()
            if len(parts) != 3:
                log.warning("malformed line: %s", line)
                continue
            word, pos, chunk = parts
            current_tokens.append(word)
            current_pos.append(pos)
            current_chunks.append(chunk)
    # final sentence
    if current_tokens:
        sentences.append({
            "tokens": current_tokens,
            "pos": current_pos,
            "chunk_bio": current_chunks,
        })
    return sentences


def main():
    train_file = Path("tmp_conll_train.txt")
    test_file = Path("tmp_conll_test.txt")
    output = Path("experiments/data/conll2000.json")

    log.info("parsing train...")
    train = parse_conll2000(train_file)
    log.info("  train: %d sentences", len(train))
    log.info("parsing test...")
    test = parse_conll2000(test_file)
    log.info("  test: %d sentences", len(test))

    # Validation
    train_tokens = sum(len(s["tokens"]) for s in train)
    test_tokens = sum(len(s["tokens"]) for s in test)
    chunk_label_set = set()
    for s in train + test:
        chunk_label_set.update(s["chunk_bio"])
    log.info("train: %d tokens / %d sentences", train_tokens, len(train))
    log.info("test: %d tokens / %d sentences", test_tokens, len(test))
    log.info("chunk labels (BIO): %d unique: %s",
             len(chunk_label_set), sorted(chunk_label_set))

    # Standard CoNLL-2000 expectations:
    # ~8936 train sentences, ~2012 test sentences, 23 BIO labels
    assert len(train) > 8000, f"train count {len(train)} seems too low for CoNLL-2000"
    assert len(test) > 1900, f"test count {len(test)} seems too low for CoNLL-2000"
    assert "B-NP" in chunk_label_set and "B-VP" in chunk_label_set, "missing standard BIO labels"

    output.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "name": "conll2000",
        "source": "Standard CoNLL-2000 chunking distribution (via teropa/nlp GitHub mirror)",
        "format": "Each sentence: tokens / pos / chunk_bio (BIO format chunk labels)",
        "splits": {
            "train": train,
            "test": test,
        },
        "stats": {
            "train_sentences": len(train),
            "train_tokens": train_tokens,
            "test_sentences": len(test),
            "test_tokens": test_tokens,
            "chunk_label_count": len(chunk_label_set),
            "chunk_labels": sorted(chunk_label_set),
        },
    }
    output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    size_mb = output.stat().st_size / (1024 * 1024)
    log.info("wrote %s (%.2f MB)", output, size_mb)
    print(json.dumps(payload["stats"], indent=2))


if __name__ == "__main__":
    main()
