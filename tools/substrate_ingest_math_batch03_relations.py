"""Ingest math batch 03 Phase A4 relations (105 fine-grained semantic relations).

Per Research math+science ingestion direction. Relations use 40 distinct types
mostly NOT in RelationType enum. Strategy:
- Try exact match against enum
- Fallback to RelationType.RELATES with specific type stored in metadata
- Atoms in src/dst can be unqualified (math::) or qualified

Usage:
    python tools/substrate_ingest_math_batch03_relations.py <jsonl_path>
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import RelationType

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s | %(message)s")
log = logging.getLogger("ingest_a4_relations")

DATA_ROOT = Path("data/substrate_index")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("jsonl_path", help="Path to A4 relations JSONL")
    args = parser.parse_args()

    pstore = PartitionedStore(DATA_ROOT)
    log.info("pre-ingest relations: %d", pstore.stats()["total_relations"])

    jsonl = Path(args.jsonl_path)
    enum_match = 0
    fallback_relates = 0
    failed = 0
    missing_atom = 0
    type_counts: Counter = Counter()
    fallback_subtypes: Counter = Counter()

    # Build enum-name lookup
    enum_names = {rt.name: rt for rt in RelationType}

    with jsonl.open("r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except Exception as e:
                log.error("line %d: %s", line_no, e)
                failed += 1
                continue
            src = rec.get("src") or rec.get("src_id")
            dst = rec.get("dst") or rec.get("tgt") or rec.get("tgt_id")
            rt_name = rec.get("type") or rec.get("rel_type")
            metadata = dict(rec.get("metadata") or {})

            if not src or not dst or not rt_name:
                log.warning("line %d: missing src/dst/type", line_no)
                failed += 1
                continue

            # Qualify ids (default math::)
            if "::" not in src:
                src = f"math::{src}"
            if "::" not in dst:
                dst = f"math::{dst}"

            # Skip if either atom missing
            if not pstore.has_atom(src):
                missing_atom += 1
                continue
            if not pstore.has_atom(dst):
                missing_atom += 1
                continue

            # Find relation type
            rt = enum_names.get(rt_name)
            if rt is not None:
                enum_match += 1
                type_counts[rt_name] += 1
            else:
                rt = RelationType.RELATES
                fallback_relates += 1
                fallback_subtypes[rt_name] += 1
                metadata["relation_subtype"] = rt_name

            note = json.dumps(metadata) if metadata else ""
            try:
                pstore.add_relation(src, rt, dst, source="batch03_A4",
                                    note=note[:200])
            except Exception as e:
                log.warning("rel skip %s -%s-> %s: %s", src, rt.value, dst, e)
                failed += 1

    stats = pstore.stats()
    print(json.dumps({
        "enum_match": enum_match,
        "fallback_to_RELATES": fallback_relates,
        "failed": failed,
        "missing_atom_skipped": missing_atom,
        "total_relations": stats["total_relations"],
        "type_counts": dict(type_counts),
        "fallback_subtypes": dict(fallback_subtypes),
    }, indent=2))


if __name__ == "__main__":
    main()
