"""Ingest 5 substrate-evolution capability histories + re-ingest extracted methodology rule with structured kind=methodology_rule fields."""
from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, RelationType

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s | %(message)s")
log = logging.getLogger("ingest_evolution")

DATA_ROOT = Path("data/substrate_index")
CAPABILITIES = DATA_ROOT / "concept_corpus_substrate_evolution_capabilities.jsonl"
META_RULE_STRUCTURED = DATA_ROOT / "meta_corpus_extracted_rule_structured.jsonl"


def main():
    pstore = PartitionedStore(DATA_ROOT)
    pre = len(pstore.all_atoms())
    log.info("pre-ingest: %d atoms", pre)
    cap_ingested = cap_skipped = 0
    rule_replaced = 0
    supersedes_added = 0

    # Capability histories
    with CAPABILITIES.open("r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
                atom = Atom.from_dict(rec)
            except Exception as e:
                log.error("cap line %d: %s", line_no, e)
                continue
            if pstore.has_atom(atom.qualified_id):
                cap_skipped += 1
                continue
            try:
                pstore.add_atom(atom, source="substrate_evolution",
                                note="capability solution-history extending substrate's empirical base")
                cap_ingested += 1
            except Exception as e:
                log.error("add failed %s: %s", atom.qualified_id, e)
                continue
            entries = list(atom.solution_history)
            entries.sort(key=lambda e: e.get("adopted_date") or "")
            for i in range(1, len(entries)):
                old = entries[i - 1].get("solution_atom_id")
                new = entries[i].get("solution_atom_id")
                if old and new and old != new:
                    try:
                        pstore.add_relation(new, RelationType.SUPERSEDES, old,
                                            source="substrate_evolution",
                                            note=f"in {atom.qualified_id}")
                        supersedes_added += 1
                    except Exception:
                        pass

    # Re-ingest the methodology rule with structured kind
    with META_RULE_STRUCTURED.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
                atom = Atom.from_dict(rec)
            except Exception as e:
                log.error("rule line: %s", e)
                continue
            # Remove old version (kind=primitive)
            if pstore.has_atom(atom.qualified_id):
                pstore.remove_atom(atom.qualified_id, source="evolution_re_ingest",
                                   note="upgrading to kind=methodology_rule with structured fields")
            pstore.add_atom(atom, source="evolution_re_ingest",
                            note="kind=methodology_rule + structured fields per Findings 13 spec")
            rule_replaced += 1

    stats = pstore.stats()
    print(json.dumps({
        "capabilities_ingested": cap_ingested,
        "capabilities_skipped": cap_skipped,
        "rule_re_ingested": rule_replaced,
        "supersedes_added": supersedes_added,
        "total_atoms": stats["total_atoms"],
        "concept_atoms": stats["partitions"].get("concept", {}).get("n_atoms", 0),
        "meta_atoms": stats["partitions"].get("meta", {}).get("n_atoms", 0),
    }, indent=2))


if __name__ == "__main__":
    main()
