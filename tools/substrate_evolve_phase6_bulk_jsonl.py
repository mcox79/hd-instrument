"""evolve.py Phase 6: parameterized bulk JSONL ingest.

Per Research FINDINGS_16 Q2 endorsement + USER directive math+science ingestion priority.

Handles structured-atom JSONL batches (math / science / capability / school / etc.):
- Accepts file_glob pattern
- Reads JSONL; converts each line via Atom.from_dict
- Ingests into appropriate partition (driven by corpus field on atom)
- Tracks new vs duplicate via has_atom()
- Wires SUPERSEDES from solution_history if present
- Wires USES from decomposes_to if present
- Reports per-file stats + total

Usage:
    python tools/substrate_evolve_phase6_bulk_jsonl.py \\
        "data/substrate_index/math_corpus_batch*.jsonl"

Or with specific files:
    python tools/substrate_evolve_phase6_bulk_jsonl.py \\
        data/substrate_index/specific.jsonl
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, RelationType

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s | %(message)s")
log = logging.getLogger("evolve_phase6")

DATA_ROOT = Path("data/substrate_index")


def ingest_jsonl(pstore: PartitionedStore, jsonl_path: Path, source_label: str) -> dict:
    """Ingest one JSONL file; return stats dict."""
    ingested = 0
    skipped = 0
    failed = 0
    supersedes_added = 0
    uses_added = 0
    by_partition: Counter = Counter()

    with jsonl_path.open("r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
                atom = Atom.from_dict(rec)
            except Exception as e:
                log.error("%s line %d: %s", jsonl_path.name, line_no, e)
                failed += 1
                continue
            if pstore.has_atom(atom.qualified_id):
                skipped += 1
                continue
            try:
                pstore.add_atom(atom, source=source_label,
                                note=f"Phase 6 bulk JSONL ingest from {jsonl_path.name}")
                ingested += 1
                by_partition[atom.corpus.value] += 1
            except Exception as e:
                log.error("add failed %s: %s", atom.qualified_id, e)
                failed += 1
                continue

            # Wire SUPERSEDES from solution_history
            if atom.solution_history:
                entries = list(atom.solution_history)
                entries.sort(key=lambda e: e.get("adopted_date") or "")
                for i in range(1, len(entries)):
                    old = entries[i - 1].get("solution_atom_id")
                    new = entries[i].get("solution_atom_id")
                    if old and new and old != new:
                        try:
                            pstore.add_relation(new, RelationType.SUPERSEDES, old,
                                                source=f"{source_label}_supersedes")
                            supersedes_added += 1
                        except Exception:
                            pass

            # Wire USES from decomposes_to (in metadata or top-level)
            decomp = atom.metadata.get("decomposes_to") or []
            for tgt in decomp:
                try:
                    pstore.add_relation(atom.qualified_id, RelationType.USES, tgt,
                                        source=f"{source_label}_decomposes_to")
                    uses_added += 1
                except Exception:
                    pass

    return {
        "file": str(jsonl_path),
        "ingested": ingested,
        "skipped": skipped,
        "failed": failed,
        "supersedes_added": supersedes_added,
        "uses_added": uses_added,
        "by_partition": dict(by_partition),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("globs", nargs="+", help="JSONL file(s) or glob pattern(s) to ingest")
    parser.add_argument("--source", default="evolve_phase6_bulk_jsonl",
                        help="Source label for provenance tracking")
    args = parser.parse_args()

    pstore = PartitionedStore(DATA_ROOT)
    pre_total = len(pstore.all_atoms())
    pre_stats = pstore.stats()["partitions"]
    log.info("pre-ingest: %d atoms total", pre_total)

    # Resolve all matching files
    all_files: list[Path] = []
    for g in args.globs:
        p = Path(g)
        if p.is_file():
            all_files.append(p)
        else:
            # glob from project root
            matches = list(Path(".").glob(g))
            all_files.extend(matches)
    all_files = sorted(set(all_files))
    log.info("resolved %d JSONL files: %s", len(all_files), [f.name for f in all_files])

    all_results = []
    grand_ingested = grand_skipped = grand_failed = 0
    grand_supersedes = grand_uses = 0
    for fp in all_files:
        result = ingest_jsonl(pstore, fp, args.source)
        all_results.append(result)
        grand_ingested += result["ingested"]
        grand_skipped += result["skipped"]
        grand_failed += result["failed"]
        grand_supersedes += result["supersedes_added"]
        grand_uses += result["uses_added"]
        log.info("  %s: +%d (skip %d, fail %d)", fp.name, result["ingested"],
                 result["skipped"], result["failed"])

    post_stats = pstore.stats()
    print("\n" + "=" * 80)
    print("EVOLVE.PY PHASE 6 BULK JSONL INGEST")
    print("=" * 80)
    print(f"\nFiles processed: {len(all_files)}")
    print(f"  TOTAL ingested: {grand_ingested}")
    print(f"  TOTAL skipped (duplicates): {grand_skipped}")
    print(f"  TOTAL failed: {grand_failed}")
    print(f"  SUPERSEDES relations added: {grand_supersedes}")
    print(f"  USES relations added: {grand_uses}")
    print(f"\nPartition state (pre -> post):")
    for partition in sorted(set(list(pre_stats.keys()) + list(post_stats["partitions"].keys()))):
        pre = pre_stats.get(partition, {}).get("n_atoms", 0)
        post = post_stats["partitions"].get(partition, {}).get("n_atoms", 0)
        if pre != post:
            print(f"  {partition:25s}  {pre:5d} -> {post:5d}  (+{post-pre})")

    print(f"\nTotal atoms: {pre_total} -> {post_stats['total_atoms']}")
    print(f"Total relations: -> {post_stats['total_relations']}")

    out = DATA_ROOT / "bench_reports" / f"evolve_phase6_{int(time.time())}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({
        "files": all_results,
        "totals": {
            "ingested": grand_ingested,
            "skipped": grand_skipped,
            "failed": grand_failed,
            "supersedes_added": grand_supersedes,
            "uses_added": grand_uses,
            "pre_total": pre_total,
            "post_total": post_stats["total_atoms"],
        },
    }, indent=2), encoding="utf-8")
    log.info("wrote phase6 report -> %s", out)


if __name__ == "__main__":
    main()
