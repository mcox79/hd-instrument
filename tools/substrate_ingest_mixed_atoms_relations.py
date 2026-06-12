"""Ingest mixed atom+relation JSONL.

Per Research INGEST_CROSS_DISC_BATCH 2026-06-12:
- cross_discipline_analogues_batch_01.jsonl: atoms (CROSSDISC/*) + relations (REL/*)
- meta_corpus_rule_metric_matches_semantic.jsonl: 1 atom + 2 relations

Detects line type:
- relation if has `source` + `target` + `relation_type`
- atom otherwise (Atom.from_dict)

Maps non-canonical relation types to canonical enums (per Cycle #27 Q1 conservative
expansion policy until 10+ uses justify schema addition):
- GROUNDS -> INFLUENCED_BY (preserves original in metadata.original_type)
- INSTANTIATES -> INSTANCE_OF
- Others: tries exact match; falls back to RELATES with subtype

NO encoder; pure index walk. Local-allowed.
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, RelationType

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s | %(message)s")
log = logging.getLogger("ingest_mixed")


def _normalize_qid(raw: str, pstore) -> str:
    """Normalize fake namespaces to real partition prefixes; ALWAYS return qualified id.

    - CROSSDISC/X -> science::CROSSDISC/X
    - substrate::Tn/X -> math::Tn/X (re-aim aspirational namespace)
    - PHYS/X / BIO/X / CHEM/X / NEURO/X -> science::PHYS/X
    - T2/X -> math::T2/X (raw math prefix)
    """
    KNOWN_PREFIXES = ("math::", "concept::", "meta::", "school::",
                       "methodology::", "science::",
                       "research_history::", "decision_history::",
                       "results_history::", "findings_history::",
                       "verdict_history::", "memory_history::")
    # Already qualified
    if raw.startswith(KNOWN_PREFIXES):
        return raw
    # Aspirational substrate:: -> try real partitions
    if raw.startswith("substrate::"):
        bare = raw.split("::", 1)[1]
        for corpus in ("math", "concept", "science", "meta", "school"):
            trial = f"{corpus}::{bare}"
            if pstore.has_atom(trial):
                return trial
        return f"math::{bare}"
    # Bare prefix (BIO/X, PHYS/X, T2/X, CROSSDISC/X, etc.)
    for corpus in ("science", "math", "concept", "meta", "school", "methodology"):
        trial = f"{corpus}::{raw}"
        if pstore.has_atom(trial):
            return trial
    # Heuristic default based on prefix style
    if raw.startswith(("T1/", "T2/", "T3/", "T4/")):
        return f"math::{raw}"
    return f"science::{raw}"


REL_TYPE_MAP = {
    "GROUNDS": RelationType.INFLUENCED_BY,
    "INSTANTIATES": RelationType.INSTANCE_OF,
    "REALIZES": RelationType.INSTANCE_OF,
    "EMBODIES": RelationType.INSTANCE_OF,
    "MODELS": RelationType.INSTANCE_OF,
}


def map_relation_type(rt_str: str) -> tuple[RelationType, str]:
    """Map possibly-non-canonical relation type to enum + preserved subtype."""
    rt_upper = rt_str.upper()
    # Exact enum match
    for rt in RelationType:
        if rt.value == rt_upper:
            return rt, ""
    # Mapped
    if rt_upper in REL_TYPE_MAP:
        return REL_TYPE_MAP[rt_upper], rt_upper
    # Substring match
    for rt in RelationType:
        if rt_upper in rt.value or rt.value in rt_upper:
            return rt, rt_upper
    # Fallback
    return RelationType.RELATES, rt_upper


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("jsonl_paths", nargs="+", type=Path)
    args = ap.parse_args()

    pstore = PartitionedStore(Path("data/substrate_index"))
    log.info("pre-ingest: %d atoms", len(pstore.all_atoms()))

    n_atoms_added = 0
    n_atoms_skipped = 0
    n_atoms_failed = 0
    n_rels_added = 0
    n_rels_failed = 0
    rel_type_distribution: Counter = Counter()

    for path in args.jsonl_paths:
        log.info("processing %s", path.name)
        with open(path, "r", encoding="utf-8") as f:
            for lineno, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except Exception as e:
                    log.error("%s:%d parse fail: %s", path.name, lineno, e)
                    continue

                # Detect relation vs atom
                if "source" in rec and "target" in rec and "relation_type" in rec:
                    # Relation
                    src = _normalize_qid(rec["source"], pstore)
                    tgt = _normalize_qid(rec["target"], pstore)
                    rt_str = rec["relation_type"]
                    rt_canonical, subtype = map_relation_type(rt_str)
                    rel_type_distribution[rt_str] += 1
                    if not pstore.has_atom(src):
                        log.warning("rel src missing: %s (raw=%s)", src, rec["source"])
                        n_rels_failed += 1
                        continue
                    if not pstore.has_atom(tgt):
                        log.warning("rel tgt missing: %s (raw=%s)", tgt, rec["target"])
                        n_rels_failed += 1
                        continue
                    try:
                        note = f"original_type={subtype}" if subtype else ""
                        pstore.add_relation(src, rt_canonical, tgt,
                                            source="ingest_mixed", note=note)
                        n_rels_added += 1
                    except Exception as e:
                        log.error("add_relation fail: %s", e)
                        n_rels_failed += 1
                else:
                    # Atom -- strip leading "<corpus>::" from id if present
                    rid = rec.get("id", "")
                    if "::" in rid:
                        rec = dict(rec)
                        rec["id"] = rid.split("::", 1)[1]
                    try:
                        atom = Atom.from_dict(rec)
                        if pstore.has_atom(atom.qualified_id):
                            n_atoms_skipped += 1
                            continue
                        pstore.add_atom(atom, source="ingest_mixed",
                                        note=f"from {path.name}")
                        n_atoms_added += 1
                    except Exception as e:
                        log.error("atom add fail %s:%d %s", path.name, lineno, e)
                        n_atoms_failed += 1

    print(f"\nINGEST COMPLETE")
    print(f"  atoms: +{n_atoms_added} (skip {n_atoms_skipped}, fail {n_atoms_failed})")
    print(f"  relations: +{n_rels_added} (fail {n_rels_failed})")
    print(f"  relation type distribution: {dict(rel_type_distribution)}")

    stats = pstore.stats()
    print(f"\nFINAL state: {stats['total_atoms']} atoms / {stats['total_relations']} relations")
    for cn, p in stats["partitions"].items():
        if p["n_atoms"] > 0:
            print(f"  {cn:20s} {p['n_atoms']:5d} atoms / {p['n_relations']:5d} relations")


if __name__ == "__main__":
    main()
