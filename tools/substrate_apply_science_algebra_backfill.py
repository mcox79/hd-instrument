"""Apply science_algebra_category backfill to existing science atoms.

Per Research SCIENCE_ALGEBRA_TAXONOMY + Findings 18 Gap 6:
each science atom gets `science_algebra_category: List[int]` (multi-category).

Read JSONL: {"atom_id": "PHYS/foo", "science_algebra_category": [1, 2]}
Update atom.metadata["science_algebra_category"] field on each matching atom.

NO encoder load; pure index walk. Local-allowed per all-cpu-compute-remote rule.
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s | %(message)s")
log = logging.getLogger("apply_science_algebra")

DATA_ROOT = Path("data/substrate_index")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("backfill_jsonl", type=Path)
    args = ap.parse_args()

    pstore = PartitionedStore(DATA_ROOT)
    log.info("pre-backfill: %d atoms", len(pstore.all_atoms()))

    updated = no_match = 0
    with open(args.backfill_jsonl, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except Exception as e:
                log.error("parse fail: %s", e)
                continue
            atom_id = rec["atom_id"]
            categories = rec["science_algebra_category"]
            qid = f"science::{atom_id}"
            if not pstore.has_atom(qid):
                log.warning("no match: %s", qid)
                no_match += 1
                continue
            atom = pstore.get_atom(qid)
            new_meta = dict(atom.metadata)
            new_meta["science_algebra_category"] = categories
            new_atom = Atom(
                id=atom.id, name=atom.name, corpus=atom.corpus, tier=atom.tier,
                description=atom.description, kind=atom.kind, aliases=atom.aliases,
                metadata=new_meta, algebra=atom.algebra, signature=atom.signature,
                complexity=atom.complexity, equivalences=atom.equivalences,
                concept_links=atom.concept_links,
                current_best_solution=atom.current_best_solution,
                solution_history=atom.solution_history,
                serves_capability=atom.serves_capability,
            )
            pstore.add_atom(new_atom, source="apply_science_algebra_backfill",
                            note=f"science_algebra_category={categories}")
            updated += 1

    print(f"\nupdated: {updated}; no_match: {no_match}")


if __name__ == "__main__":
    main()
