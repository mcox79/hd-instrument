"""Ingest the 18 Research-validated ACCEPT atoms from Findings 09 closed-loop."""
from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, RelationType

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s | %(message)s")
log = logging.getLogger("ingest_18")

DATA_ROOT = Path("data/substrate_index")
JSONL = DATA_ROOT / "concept_corpus_findings_09_type_A_18_accept.jsonl"


def main():
    pstore = PartitionedStore(DATA_ROOT)
    log.info("pre-ingest atom count: %d", len(pstore.all_atoms()))
    ingested = 0
    skipped = 0
    uses_added = 0
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
                pstore.add_atom(atom, source="findings_09_18_accept",
                                note="Research-validated Type A closed-loop cycle #5")
                ingested += 1
            except Exception as e:
                log.error("add failed %s: %s", atom.qualified_id, e)
                continue
            # decomposes_to -> USES edges
            for tgt in atom.metadata.get("decomposes_to") or []:
                try:
                    pstore.add_relation(atom.qualified_id, RelationType.USES, tgt,
                                        source="findings_09_18_accept_decomposes_to")
                    uses_added += 1
                except Exception as e:
                    log.warning("USES skip %s -> %s: %s", atom.qualified_id, tgt, e)

    stats = pstore.stats()
    log.info("ingested=%d skipped=%d uses_added=%d", ingested, skipped, uses_added)
    print(json.dumps({
        "ingested": ingested,
        "skipped": skipped,
        "uses_added": uses_added,
        "total_atoms_post": stats["total_atoms"],
        "total_relations_post": stats["total_relations"],
        "concept_partition_atoms": stats["partitions"].get("concept", {}).get("n_atoms", 0),
    }, indent=2))


if __name__ == "__main__":
    main()
