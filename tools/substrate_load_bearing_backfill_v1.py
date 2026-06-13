"""substrate_load_bearing axis backfill v1 -- per Research 13th methodology rule promotion.

Per AAA-3 INTRINSIC SUPPORT 3/3 signals (commit ab2c2efe + 6ee95c7e):
TOOLS:MATERIALS distinction is EMPIRICALLY REAL via intrinsic signals:
  - capability_span: 7.78x (tools serve ~8x more capabilities)
  - neighbor_reach: 27.85x mean / 6.0x median (tools connect 6-28x more architecture)
  - cross_domain_reach: 2.03x (tools span ~2x more domains)

13th methodology rule (substrate-load-bearing distinction) READY FOR PROMOTION
once Testbed backfills the `substrate_load_bearing` metadata field across prior
atoms. BATCH 26 (commit aa10849c) was first to populate this field (all 12 KNOWS-
not-USES = False). Other 1746+ pre-existing atoms have no value set.

Backfill heuristic (intrinsic; matches AAA-3 INTRINSIC operationalization):
  An atom is LOAD-BEARING (True) if:
    (cap_score >= 3) OR (neighbor_score >= 5) OR (cross_domain_score >= 2)
  where:
    cap_score = len(serves_capability)
    neighbor_score = total in+out neighbors via USES + DEPENDS_ON
    cross_domain_score = # distinct partitions reached via neighbors

Heuristic thresholds match AAA-3 INTRINSIC signal medians (rounded down for
inclusive 'load-bearing' classification). Atoms below all 3 thresholds are
KNOWS-not-USES (False).

Modes:
  --dry-run: print classifications without writing
  --execute: write metadata.substrate_load_bearing to each atom

Tolerant of atoms with existing substrate_load_bearing value (preserves BATCH 26).

NO LLM. NO bge. Pure graph metrics + metadata write.
"""
from __future__ import annotations
import sys
import argparse
import dataclasses
from pathlib import Path
from collections import defaultdict
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import RelationType


# Edge types that count toward neighbor_score (USES + DEPENDS_ON are the
# AAA-3 INTRINSIC signal).
USAGE_EDGE_TYPES = (RelationType.USES, RelationType.DEPENDS_ON)

# Thresholds (matched to AAA-3 median signals rounded down).
CAP_THRESHOLD = 3
NEIGHBOR_THRESHOLD = 5
CROSS_DOMAIN_THRESHOLD = 2


def classify_atom(atom, ps: PartitionedStore) -> tuple:
    """Returns (is_load_bearing: bool, scores: dict)."""
    cap_score = len(atom.serves_capability or ())
    qid = atom.qualified_id

    neighbors = set()
    for rt in USAGE_EDGE_TYPES:
        try:
            neighbors.update(ps.out_neighbors(qid, rt) or set())
            neighbors.update(ps.in_neighbors(qid, rt) or set())
        except Exception:
            pass
    neighbor_score = len(neighbors)

    # Cross-domain reach: distinct partitions reached via neighbors
    partitions = set()
    for n_qid in neighbors:
        n_atom = ps.get_atom(n_qid)
        if n_atom is None:
            continue
        # Use corpus + first segment of metadata.science_algebra_category as "domain"
        corpus = n_atom.corpus.value if hasattr(n_atom.corpus, "value") else str(n_atom.corpus)
        sac = (n_atom.metadata or {}).get("science_algebra_category", "")
        if isinstance(sac, list):
            sac = sac[0] if sac else ""
        domain = f"{corpus}::{str(sac).split('::')[0] if sac else 'unknown'}"
        partitions.add(domain)
    cross_domain_score = len(partitions)

    is_load_bearing = (
        cap_score >= CAP_THRESHOLD
        or neighbor_score >= NEIGHBOR_THRESHOLD
        or cross_domain_score >= CROSS_DOMAIN_THRESHOLD
    )
    return is_load_bearing, {
        "cap_score": cap_score,
        "neighbor_score": neighbor_score,
        "cross_domain_score": cross_domain_score,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--dry-run", action="store_true",
                    help="Print classification without writing metadata")
    ap.add_argument("--execute", action="store_true",
                    help="Write metadata.substrate_load_bearing to each atom")
    ap.add_argument("--respect-existing", action="store_true", default=True,
                    help="Skip atoms that already have substrate_load_bearing set (BATCH 26)")
    args = ap.parse_args()

    if not args.dry_run and not args.execute:
        print("ERROR: pass --dry-run or --execute")
        sys.exit(2)

    ps = PartitionedStore(Path("data/substrate_index"))
    atoms = ps.all_atoms()
    print(f"loaded {len(atoms)} atoms")

    counts = {"load_bearing_True": 0, "load_bearing_False": 0,
              "preserved_existing": 0, "updated": 0, "failed": 0}
    sample_classifications = {True: [], False: []}

    for atom in atoms:
        existing = (atom.metadata or {}).get("substrate_load_bearing")
        if args.respect_existing and existing is not None:
            counts["preserved_existing"] += 1
            if existing is True:
                counts["load_bearing_True"] += 1
            else:
                counts["load_bearing_False"] += 1
            continue

        is_lb, scores = classify_atom(atom, ps)
        if is_lb:
            counts["load_bearing_True"] += 1
            if len(sample_classifications[True]) < 8:
                sample_classifications[True].append((atom.qualified_id, scores))
        else:
            counts["load_bearing_False"] += 1
            if len(sample_classifications[False]) < 8:
                sample_classifications[False].append((atom.qualified_id, scores))

        if args.execute:
            try:
                new_meta = dict(atom.metadata or {})
                new_meta["substrate_load_bearing"] = is_lb
                new_meta.setdefault("load_bearing_backfill_scores", scores)
                new_atom = dataclasses.replace(atom, metadata=new_meta)
                # Remove + re-add (or use ps internal update if available)
                ps.remove_atom(atom.qualified_id)
                ps.add_atom(new_atom, source="substrate_load_bearing_backfill_v1",
                            note="13th methodology rule promotion; AAA-3 INTRINSIC heuristic backfill")
                counts["updated"] += 1
            except Exception as e:
                counts["failed"] += 1
                print(f"  FAIL {atom.qualified_id}: {str(e)[:120]}")

    print(f"\n=== LOAD-BEARING BACKFILL SUMMARY ===")
    print(f"atoms total: {len(atoms)}")
    print(f"  load_bearing=True:   {counts['load_bearing_True']}")
    print(f"  load_bearing=False:  {counts['load_bearing_False']}")
    print(f"  preserved (existing): {counts['preserved_existing']}")
    if args.execute:
        print(f"  metadata updated:     {counts['updated']}")
        print(f"  failed:               {counts['failed']}")
    print(f"\nSample LOAD_BEARING=True:")
    for qid, sc in sample_classifications[True]:
        print(f"  {qid:55s} cap={sc['cap_score']} nbr={sc['neighbor_score']} cd={sc['cross_domain_score']}")
    print(f"\nSample LOAD_BEARING=False (KNOWS not USES):")
    for qid, sc in sample_classifications[False]:
        print(f"  {qid:55s} cap={sc['cap_score']} nbr={sc['neighbor_score']} cd={sc['cross_domain_score']}")

    if args.dry_run:
        ratio = counts["load_bearing_True"] / max(counts["load_bearing_False"], 1)
        print(f"\n[DRY RUN] no metadata written. Would classify "
              f"{counts['load_bearing_True']} True / {counts['load_bearing_False']} False "
              f"(ratio {ratio:.2f}x)")
        print(f"Re-run with --execute to write metadata.substrate_load_bearing to each atom.")


if __name__ == "__main__":
    main()
