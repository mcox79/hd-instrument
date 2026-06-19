"""Ingest 10 math-world-knowledge LEX atoms (with members_named_values in metadata)."""
from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, RelationType

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s | %(message)s")
log = logging.getLogger("ingest_math_wk_lex")

DATA_ROOT = Path("data/substrate_index")
JSONL = DATA_ROOT / "concept_corpus_math_world_knowledge_lex_atoms.jsonl"


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
                # members_named_values goes into metadata so existing Atom.from_dict handles it
                if "members_named_values" in rec:
                    rec.setdefault("metadata", {})["members_named_values"] = rec.pop("members_named_values")
                atom = Atom.from_dict(rec)
            except Exception as e:
                log.error("line %d: %s", line_no, e)
                continue
            if pstore.has_atom(atom.qualified_id):
                skipped += 1
                continue
            try:
                pstore.add_atom(atom, source="math_wk_lex_10",
                                note="Research hand-authored math-world-knowledge lexicon (members_named_values in metadata)")
                ingested += 1
            except Exception as e:
                log.error("add failed %s: %s", atom.qualified_id, e)
                continue
            for tgt in atom.metadata.get("decomposes_to") or []:
                try:
                    pstore.add_relation(atom.qualified_id, RelationType.USES, tgt,
                                        source="math_wk_lex_10_decomposes_to")
                    uses_added += 1
                except Exception:
                    pass

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
