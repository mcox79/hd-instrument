"""
Stage C dep: build label cache (SQLite) for Q-code -> English label lookup.

Per Research STAGE_C_5_ANSWERS Q4:
  - SQLite schema: labels(qid TEXT PRIMARY KEY, label_en TEXT, label_count INTEGER,
                          lazy_resolved INTEGER DEFAULT 0)
  - Top-1M Q-codes by occurrence count in OUR filtered triples eager-resolved
  - Long tail: stored with label_count + lazy_resolved=0 (API resolved at query time)
  - English-only for v1

Three-pass build:
  Pass 1: count Q-code occurrences in triples.jsonl
  Pass 2: select top-1M; eager-fill labels (currently from a labels source TBD;
          API fallback or labels-dump if available)
  Pass 3: write long-tail entries with label_count for later lazy resolution

If no labels source is provided (default), the script writes the counts table only;
lookups will fall back to API at query time when enabled in the runtime.

Usage:
    .venv-demo\\Scripts\\python.exe scripts\\build_label_cache.py \\
        --triples data/substrate_state/wikidata_truthy_50m/triples.jsonl \\
        --db data/substrate_state/wikidata_truthy_50m_v2/label_cache.db \\
        --top-k 1000000
"""
from __future__ import annotations
import argparse
import json
import logging
import sqlite3
import sys
import time
from pathlib import Path
from typing import Optional

logger = logging.getLogger("build_label_cache")


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS labels (
    qid TEXT PRIMARY KEY,
    label_en TEXT,
    label_count INTEGER NOT NULL,
    lazy_resolved INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_labels_count ON labels(label_count DESC);
"""


def count_qcodes(triples_path: Path, checkpoint_every: int = 1_000_000) -> dict:
    """Pass 1: stream triples.jsonl + count Q-code occurrences (subject + object)."""
    counts: dict = {}
    n_lines = 0
    t0 = time.perf_counter()
    logger.info("counting Q-code occurrences in %s ...", triples_path)
    with open(triples_path, encoding="utf-8") as f:
        for line in f:
            n_lines += 1
            try:
                t = json.loads(line)
                s, o = t.get("s"), t.get("o")
                if s and s.startswith("Q"):
                    counts[s] = counts.get(s, 0) + 1
                if o and isinstance(o, str) and o.startswith("Q"):
                    counts[o] = counts.get(o, 0) + 1
            except (ValueError, json.JSONDecodeError):
                continue
            if n_lines % checkpoint_every == 0:
                logger.info("[ck] lines=%d unique-codes=%d rate=%.0f lines/s",
                            n_lines, len(counts), n_lines / max(0.001, time.perf_counter() - t0))
    logger.info("DONE pass 1: %d lines / %d unique Q-codes (%.0fs)",
                n_lines, len(counts), time.perf_counter() - t0)
    return counts


def write_counts_to_db(counts: dict, db_path: Path, top_k: Optional[int]) -> int:
    """Pass 2/3: write counts to SQLite. Top-k eager-marked (lazy_resolved=1 placeholder);
    long tail (rank > top_k) stored with lazy_resolved=0 + empty label.

    Returns number of rows written.
    """
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.executescript(SCHEMA_SQL)
    conn.commit()

    items = sorted(counts.items(), key=lambda kv: -kv[1])
    if top_k is None:
        top_k = len(items)

    t0 = time.perf_counter()
    inserts_eager = []
    inserts_lazy = []
    for rank, (qid, c) in enumerate(items):
        if rank < top_k:
            # Eager candidate: marked for label lookup (empty label_en for now;
            # populated by a follow-up labels-dump pass when source is downloaded)
            inserts_eager.append((qid, None, c, 0))
        else:
            inserts_lazy.append((qid, None, c, 0))

    cur = conn.cursor()
    cur.executemany(
        "INSERT OR REPLACE INTO labels (qid, label_en, label_count, lazy_resolved) VALUES (?, ?, ?, ?)",
        inserts_eager + inserts_lazy,
    )
    conn.commit()
    n_rows = len(inserts_eager) + len(inserts_lazy)
    logger.info("wrote %d rows to %s (top_k=%d eager-marked) in %.1fs",
                n_rows, db_path, top_k, time.perf_counter() - t0)
    conn.close()
    return n_rows


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--triples", type=Path, required=True)
    p.add_argument("--db", type=Path, required=True)
    p.add_argument("--top-k", type=int, default=1_000_000)
    args = p.parse_args()

    setup_logging()

    counts = count_qcodes(args.triples)
    n_rows = write_counts_to_db(counts, args.db, top_k=args.top_k)
    logger.info("label cache built: %s (%d Q-codes; top-%d eager-marked)",
                args.db, n_rows, args.top_k)


if __name__ == "__main__":
    sys.exit(main() or 0)
