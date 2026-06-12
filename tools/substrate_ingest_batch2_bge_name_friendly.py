"""Apply Research Cycle 49 batch 2 breadth backfill (40 bge-name-friendly atoms).

Format: {atom_id, aliases_add, algebra_additions}
- Existing atom: extend aliases (union) + merge algebra dict
- Missing atom: create with name=last_id_segment, corpus inferred from prefix,
  tier inferred from id middle, kind=concept_def, no description (bge-name encoder)

Per [[substrate-vsa-position-is-meaning-validated-2026-06-12]] + Research bge-name-friendly
authoring discipline. Local-allowed (no encoder load).
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s | %(message)s")
log = logging.getLogger("ingest_batch2")

DATA_ROOT = Path("data/substrate_index")

CORPUS_MAP = {
    "math": Corpus.MATH, "concept": Corpus.CONCEPT, "science": Corpus.SCIENCE,
    "BIO": Corpus.SCIENCE, "PHYS": Corpus.SCIENCE, "CHEM": Corpus.SCIENCE,
    "NEURO": Corpus.SCIENCE, "CROSSDISC": Corpus.SCIENCE, "SCHOOL": Corpus.MATH,
}

TIER_MAP = {
    "T1": Tier.TIER_1_FOUNDATIONAL,
    "T2": Tier.TIER_2_PRIMITIVE,
    "T3": Tier.TIER_3_ALGORITHM,
    "T4": Tier.TIER_4_COMPOSED,
}


def parse_qid(qid: str) -> tuple[Corpus, Tier]:
    if "::" not in qid:
        return Corpus.MATH, Tier.TIER_2
    cprefix, rest = qid.split("::", 1)
    corpus = CORPUS_MAP.get(cprefix, Corpus.MATH)
    tier = Tier.TIER_2_PRIMITIVE
    if "/" in rest:
        tprefix = rest.split("/", 1)[0]
        tier = TIER_MAP.get(tprefix, Tier.TIER_2_PRIMITIVE)
    return corpus, tier


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("backfill_jsonl", type=Path)
    args = ap.parse_args()

    pstore = PartitionedStore(DATA_ROOT)
    log.info("pre-ingest: %d atoms", len(pstore.all_atoms()))

    updated = created = errors = 0
    with open(args.backfill_jsonl, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except Exception as e:
                log.error("parse fail: %s", e)
                errors += 1
                continue
            qid = rec["atom_id"]
            new_aliases = rec.get("aliases_add", []) or []
            algebra_add = rec.get("algebra_additions", {}) or {}

            if pstore.has_atom(qid):
                atom = pstore.get_atom(qid)
                merged_algebra = dict(atom.algebra or {})
                merged_algebra.update(algebra_add)
                merged_aliases = list(dict.fromkeys(list(atom.aliases or []) + new_aliases))
                new_atom = Atom(
                    id=atom.id, name=atom.name, corpus=atom.corpus, tier=atom.tier,
                    description=atom.description, kind=atom.kind, aliases=merged_aliases,
                    metadata=atom.metadata, algebra=merged_algebra,
                    signature=atom.signature, complexity=atom.complexity,
                    equivalences=atom.equivalences, concept_links=atom.concept_links,
                    current_best_solution=atom.current_best_solution,
                    solution_history=atom.solution_history,
                    serves_capability=atom.serves_capability,
                )
                pstore.add_atom(new_atom, source="batch2_bge_name_friendly",
                                note=f"+{len(new_aliases)} aliases +{len(algebra_add)} algebra fields")
                updated += 1
            else:
                # Create new atom
                bare = qid.split("::", 1)[1] if "::" in qid else qid
                name = bare.split("/")[-1] if "/" in bare else bare
                corpus, tier = parse_qid(qid)
                new_atom = Atom(
                    id=bare, name=name, corpus=corpus, tier=tier,
                    description="", kind=AtomKind.PRIMITIVE,
                    aliases=new_aliases, metadata={},
                    algebra=algebra_add, signature=None, complexity=None,
                    equivalences=[], concept_links=[],
                    current_best_solution=None, solution_history=[],
                    serves_capability=(),
                )
                try:
                    pstore.add_atom(new_atom, source="batch2_bge_name_friendly",
                                    note=f"created with {len(new_aliases)} aliases + {len(algebra_add)} algebra fields")
                    created += 1
                except Exception as e:
                    log.warning("create fail %s: %s", qid, str(e)[:80])
                    errors += 1

    log.info("post-ingest: %d atoms", len(pstore.all_atoms()))
    print(f"\nupdated: {updated}; created: {created}; errors: {errors}")


if __name__ == "__main__":
    main()
