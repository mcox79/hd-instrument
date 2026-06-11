"""Ingest math batch 03 Phase A -- 30 foundational + Findings 11 ACCEPT atoms."""
from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s | %(message)s")
log = logging.getLogger("ingest_batch03_A")

DATA_ROOT = Path("data/substrate_index")
JSONL = DATA_ROOT / "math_corpus_batch03_phase_A.jsonl"


def main():
    pstore = PartitionedStore(DATA_ROOT)
    pre = len(pstore.all_atoms())
    pre_math = pstore.stats()["partitions"].get("math", {}).get("n_atoms", 0)
    log.info("pre-ingest: %d atoms; math partition %d", pre, pre_math)
    ingested = skipped = 0
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
                pstore.add_atom(atom, source="math_batch03_phase_A",
                                note="Research hand-authored per user math+science ingestion direction")
                ingested += 1
            except Exception as e:
                log.error("add failed %s: %s", atom.qualified_id, e)

    stats = pstore.stats()
    print(json.dumps({
        "ingested": ingested,
        "skipped": skipped,
        "total_atoms": stats["total_atoms"],
        "math_partition_atoms": stats["partitions"].get("math", {}).get("n_atoms", 0),
    }, indent=2))


if __name__ == "__main__":
    main()
