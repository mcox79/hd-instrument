"""Ingest 5 cycle-238 capability atoms (PP-393 through PP-397) with solution histories."""
from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, RelationType

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s | %(message)s")
log = logging.getLogger("ingest_cycle238")

DATA_ROOT = Path("data/substrate_index")
JSONL = DATA_ROOT / "concept_corpus_cycle238_capabilities.jsonl"


def main():
    pstore = PartitionedStore(DATA_ROOT)
    pre = len(pstore.all_atoms())
    log.info("pre-ingest: %d atoms", pre)
    ingested = skipped = supersedes_added = 0
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
                pstore.add_atom(atom, source="cycle238_capabilities",
                                note="5 PP capability atoms from cap_map cycle 238 verdicts")
                ingested += 1
            except Exception as e:
                log.error("add failed %s: %s", atom.qualified_id, e)
                continue
            # Wire SUPERSEDES relations from solution_history
            entries = list(atom.solution_history)
            entries.sort(key=lambda e: e.get("adopted_date") or "")
            for i in range(1, len(entries)):
                old = entries[i - 1].get("solution_atom_id")
                new = entries[i].get("solution_atom_id")
                if old and new and old != new:
                    try:
                        pstore.add_relation(new, RelationType.SUPERSEDES, old,
                                            source="cycle238_capabilities",
                                            note=f"in {atom.qualified_id}")
                        supersedes_added += 1
                    except Exception:
                        pass

    stats = pstore.stats()
    print(json.dumps({
        "ingested": ingested,
        "skipped": skipped,
        "supersedes_added": supersedes_added,
        "total_atoms": stats["total_atoms"],
        "concept_atoms": stats["partitions"].get("concept", {}).get("n_atoms", 0),
    }, indent=2))


if __name__ == "__main__":
    main()
