"""Revert batch 2 keep-new T2 atoms per strategy_request 2026-06-12.

Reads the batch 2 JSONL, finds which atom_ids are still present in the store
(the 32 "keeps" from prior dedup pass), and removes them. T3 atoms merged
during dedup (commit 8a3e891b) stay as-is per strategy nuance: their T3
destinations existed in the 1742 baseline; alias/algebra enrichment doesn't
duplicate, doesn't need revert.

Expected outcome: 1774 -> 1742 atoms (or close to it).
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s | %(message)s")
log = logging.getLogger("revert_batch2")

DATA_ROOT = Path("data/substrate_index")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("backfill_jsonl", type=Path)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    pstore = PartitionedStore(DATA_ROOT)
    log.info("pre-revert: %d atoms total", len(pstore.all_atoms()))

    targets = []
    with open(args.backfill_jsonl, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            qid = rec["atom_id"]
            if pstore.has_atom(qid):
                targets.append(qid)

    log.info("revert plan: %d batch 2 atoms still present (T2 keeps) -> remove", len(targets))
    for q in targets:
        log.info("  REMOVE %s", q)

    if not args.apply:
        print(f"\nDRY-RUN: would remove {len(targets)} atoms. Re-run with --apply.")
        return

    removed = 0
    for q in targets:
        ok = pstore.remove_atom(q, source="batch2_revert",
                                 note="reverted per strategy_request 2026-06-12 batch2 revert")
        if ok:
            removed += 1
        else:
            log.warning("remove failed: %s", q)

    log.info("post-revert: %d atoms total", len(pstore.all_atoms()))
    print(f"\nAPPLIED: {removed} atoms removed.")


if __name__ == "__main__":
    main()
