"""Ingest 6 human-authored + 1 substrate-extracted methodology rules into meta partition."""
from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s | %(message)s")
log = logging.getLogger("ingest_meta_rules")

DATA_ROOT = Path("data/substrate_index")
JSONL = DATA_ROOT / "meta_corpus_methodology_rules.jsonl"


def main():
    pstore = PartitionedStore(DATA_ROOT)
    pre = len(pstore.all_atoms())
    log.info("pre-ingest: %d atoms (meta partition empty? %s)",
             pre, pstore.stats()["partitions"].get("meta", {}).get("n_atoms", 0) == 0)
    ingested = skipped = 0
    by_source: dict = {"human": 0, "substrate": 0}
    with JSONL.open("r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
                atom = Atom.from_dict(rec)
            except Exception as e:
                log.error("line %d: %s", line_no, e)
                continue
            if pstore.has_atom(atom.qualified_id):
                skipped += 1
                continue
            try:
                pstore.add_atom(atom, source="meta_rules_ingest",
                                note="6 human-authored + 1 substrate-extracted methodology rules")
                ingested += 1
                src = atom.metadata.get("extracted_by", "unknown")
                by_source[src] = by_source.get(src, 0) + 1
            except Exception as e:
                log.error("add failed %s: %s", atom.qualified_id, e)

    stats = pstore.stats()
    print(json.dumps({
        "ingested": ingested,
        "skipped": skipped,
        "by_source": by_source,
        "total_atoms": stats["total_atoms"],
        "meta_partition_atoms": stats["partitions"].get("meta", {}).get("n_atoms", 0),
    }, indent=2))


if __name__ == "__main__":
    main()
