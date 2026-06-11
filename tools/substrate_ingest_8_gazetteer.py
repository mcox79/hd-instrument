"""Ingest 8 NER gazetteer atoms (kind=lexicon; tier=T_lexicon)."""
from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, RelationType

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s | %(message)s")
log = logging.getLogger("ingest_gazetteer_8")

DATA_ROOT = Path("data/substrate_index")
JSONL = DATA_ROOT / "concept_corpus_ner_gazetteer_atoms.jsonl"


def main():
    pstore = PartitionedStore(DATA_ROOT)
    pre = len(pstore.all_atoms())
    log.info("pre-ingest: %d atoms", pre)
    ingested = skipped = uses_added = 0
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
                pstore.add_atom(atom, source="ner_gazetteer_8",
                                note="Research hand-authored substrate-self-referential gazetteer")
                ingested += 1
            except Exception as e:
                log.error("add failed %s: %s", atom.qualified_id, e)
                continue
            for tgt in atom.metadata.get("decomposes_to") or []:
                try:
                    pstore.add_relation(atom.qualified_id, RelationType.USES, tgt,
                                        source="ner_gazetteer_8_decomposes_to")
                    uses_added += 1
                except Exception as e:
                    log.warning("USES skip: %s", e)

    stats = pstore.stats()
    print(json.dumps({
        "pre": pre,
        "ingested": ingested,
        "skipped": skipped,
        "uses_added": uses_added,
        "total_atoms": stats["total_atoms"],
        "concept_atoms": stats["partitions"].get("concept", {}).get("n_atoms", 0),
    }, indent=2))


if __name__ == "__main__":
    main()
