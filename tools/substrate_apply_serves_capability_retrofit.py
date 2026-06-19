"""Apply serves_capability retrofit JSONL to existing math T2/T3 atoms.

Per Research CYCLE_27 Q3 + RELATIONTYPE Q3: Research authors serves_capability
for math T2/T3 atoms. This tool applies the retrofit.

Format: {"atom_id": "math::T2/foo", "serves_capability": ["concept::CAP_X", ...]}

Union semantic: combines retrofit list with any existing serves_capability
(from prior backfill) without overwriting.

NO encoder; pure index walk. Local-allowed.
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
log = logging.getLogger("retrofit_serves_capability")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("retrofit_jsonl", type=Path)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    pstore = PartitionedStore(Path("data/substrate_index"))
    log.info("pre-retrofit: %d atoms", len(pstore.all_atoms()))

    updated = no_match = unchanged = 0
    with open(args.retrofit_jsonl, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            atom_qid = rec["atom_id"]
            new_caps = rec["serves_capability"]
            if not pstore.has_atom(atom_qid):
                # try bare lookup
                bare = atom_qid.split("::", 1)[-1]
                found = False
                for corpus_name in ("math", "concept", "meta", "school", "methodology", "science"):
                    trial = f"{corpus_name}::{bare}"
                    if pstore.has_atom(trial):
                        atom_qid = trial
                        found = True
                        break
                if not found:
                    log.warning("no match: %s", atom_qid)
                    no_match += 1
                    continue
            atom = pstore.get_atom(atom_qid)
            existing = set(atom.serves_capability)
            merged = existing | set(new_caps)
            if merged == existing:
                unchanged += 1
                continue
            if not args.dry_run:
                new_atom = Atom(
                    id=atom.id, name=atom.name, corpus=atom.corpus, tier=atom.tier,
                    description=atom.description, kind=atom.kind, aliases=atom.aliases,
                    metadata=atom.metadata, algebra=atom.algebra, signature=atom.signature,
                    complexity=atom.complexity, equivalences=atom.equivalences,
                    concept_links=atom.concept_links,
                    current_best_solution=atom.current_best_solution,
                    solution_history=atom.solution_history,
                    serves_capability=tuple(sorted(merged)),
                )
                pstore.add_atom(new_atom, source="retrofit_serves_capability",
                                note=f"Q3 retrofit: added {len(merged - existing)} caps")
            updated += 1

    print(f"\nupdated: {updated}  unchanged: {unchanged}  no_match: {no_match}")


if __name__ == "__main__":
    main()
