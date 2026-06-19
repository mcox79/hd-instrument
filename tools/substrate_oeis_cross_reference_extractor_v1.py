"""OEIS cross-reference DEPENDS_ON extractor v1.

Per Research depth-forecast correction (premise count 1.00 = single-parent
chains): the 20820-atom canonical substrate is dominated by ~18952 OEIS atoms
which currently all have depends_on=[] (per substrate_ingest_oeis_v1.py).
This kills average premise count.

OEIS sequences cross-reference each other extensively via A-numbers in their
formulas, examples, and notes (e.g. A001234 might say "Same as A005678 shifted").
Extracting these cross-refs as DEPENDS_ON edges adds multi-premise structure
WITHOUT any new atom authoring.

Strategy:
  1. Scan substrate for all atoms with partition matching OEIS pattern
     (canonical_name like "oeis_A012345" or partition like "oeis::*")
  2. For each, look in description/algebra_dict for other A-numbers
  3. Add DEPENDS_ON edge target -> if both atoms exist (canonical-remote will
     have them all)

Expected impact at 20820 scale:
  - 18952 OEIS atoms, average ~3-7 cross-refs per sequence (OEIS internal stats)
  - Estimated ~50K-130K new DEPENDS_ON edges
  - avg premise count: 1.00 -> 3-5+ (decisive multi-premise structure)
  - Hill alpha rebalances to ~1.6-1.7 from 1.45 (heavier tail flattens)

NO LLM. NO bge. Pure regex + graph authoring. Tolerant of missing target atoms.
Runs on canonical-remote where 18952 OEIS atoms live.

Usage:
  python tools/substrate_oeis_cross_reference_extractor_v1.py [--dry-run] [--limit N]
"""
from __future__ import annotations
import sys
import re
import argparse
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import RelationType


# OEIS A-number pattern. Matches A followed by 6+ digits (rare: A00001 onwards
# always 6 digits; we accept 5+ for safety).
A_NUMBER_PATTERN = re.compile(r"\bA(\d{5,7})\b")

# Heuristic for identifying OEIS atoms by qualified id pattern.
OEIS_QID_PATTERN = re.compile(r"::T[0-9]+/oeis_A\d+", re.IGNORECASE)


def extract_a_refs(text: str, self_a_num: str | None) -> set:
    """Find all A-numbers referenced in text; exclude self-reference."""
    refs = set()
    for m in A_NUMBER_PATTERN.finditer(text):
        digits = m.group(1)
        # Normalize to A + 6-digit zero-padded form
        a_norm = f"A{int(digits):06d}"
        if a_norm == self_a_num:
            continue
        refs.add(a_norm)
    return refs


def parse_self_a_num(atom) -> str | None:
    """Extract this atom's own A-number from id."""
    m = re.search(r"oeis_A(\d+)", atom.id, re.IGNORECASE)
    if not m:
        return None
    return f"A{int(m.group(1)):06d}"


def collect_text_to_scan(atom) -> str:
    """Aggregate atom fields where OEIS A-refs typically appear."""
    parts = [atom.description or ""]
    alg = atom.algebra or {}
    for k, v in alg.items():
        if isinstance(v, str):
            parts.append(v)
        elif isinstance(v, list):
            for item in v:
                parts.append(str(item))
    meta = atom.metadata or {}
    for k, v in meta.items():
        if isinstance(v, str):
            parts.append(v)
    return " ".join(parts)


def resolve_oeis_qid(a_num: str, oeis_id_index: dict, ps: PartitionedStore) -> str | None:
    """Resolve A-number to qualified id; uses prebuilt index for speed."""
    hit = oeis_id_index.get(a_num)
    if hit and ps.has_atom(hit):
        return hit
    # Fall back to corpus prefix search
    for corpus in ("math", "concept", "science"):
        # Try a few tier prefixes
        for tier in ("T3", "T2", "T1"):
            qid = f"{corpus}::{tier}/oeis_{a_num}"
            if ps.has_atom(qid):
                return qid
    return None


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--dry-run", action="store_true",
                    help="Scan + report counts without writing edges")
    ap.add_argument("--limit", type=int, default=None,
                    help="Only process first N OEIS atoms (smoke)")
    ap.add_argument("--min-refs", type=int, default=1,
                    help="Only emit edges from atoms with >= N cross-refs")
    args = ap.parse_args()

    ps = PartitionedStore(Path("data/substrate_index"))
    print(f"loading atoms...")
    all_atoms = ps.all_atoms()
    print(f"total atoms in substrate: {len(all_atoms)}")

    # Identify OEIS atoms via id pattern
    oeis_atoms = []
    oeis_id_index = {}  # A-number -> qid
    for a in all_atoms:
        m = re.search(r"oeis_A(\d+)", a.id, re.IGNORECASE)
        if m:
            a_num = f"A{int(m.group(1)):06d}"
            oeis_atoms.append((a, a_num))
            oeis_id_index[a_num] = a.qualified_id
    print(f"OEIS atoms found: {len(oeis_atoms)}")

    if not oeis_atoms:
        print("\nNo OEIS atoms in this substrate. This script must run on")
        print("canonical-remote which has ~18,952 OEIS atoms post-ingest.")
        print("(Local sandbox typically has 0 OEIS atoms unless --full ingest done.)")
        return

    if args.limit:
        oeis_atoms = oeis_atoms[: args.limit]
        print(f"limited to first {len(oeis_atoms)}")

    # Existing edges (avoid duplicates)
    print(f"building existing edge set...")
    existing = set()
    for r in ps.iter_all_relations():
        try:
            existing.add((r.src_qualified_id, r.rel_type.name, r.tgt_qualified_id))
        except AttributeError:
            pass
    print(f"existing relations: {len(existing)}")

    # Process atoms
    candidates_total = 0
    edges_added = 0
    atoms_with_refs = 0
    skipped_miss_tgt = 0
    skipped_dup = 0
    failed = 0
    sample_extractions = []

    for atom, self_a_num in oeis_atoms:
        text = collect_text_to_scan(atom)
        refs = extract_a_refs(text, self_a_num)
        if len(refs) < args.min_refs:
            continue
        atoms_with_refs += 1
        candidates_total += len(refs)

        if len(sample_extractions) < 5:
            sample_extractions.append((atom.qualified_id, sorted(refs)[:10]))

        src_qid = atom.qualified_id
        for ref in refs:
            tgt_qid = resolve_oeis_qid(ref, oeis_id_index, ps)
            if tgt_qid is None:
                skipped_miss_tgt += 1
                continue
            key = (src_qid, "DEPENDS_ON", tgt_qid)
            if key in existing:
                skipped_dup += 1
                continue
            if args.dry_run:
                edges_added += 1
                existing.add(key)
                continue
            try:
                ps.add_relation(src_qid, RelationType.DEPENDS_ON, tgt_qid,
                                source="oeis_cross_reference_extractor_v1",
                                note=f"OEIS A-num cross-reference {self_a_num} -> {ref}")
                edges_added += 1
                existing.add(key)
            except Exception as e:
                msg = str(e)[:120]
                if any(k in msg.lower() for k in ("already", "duplicate")):
                    skipped_dup += 1
                else:
                    failed += 1
                    if failed < 5:
                        print(f"  FAIL: {src_qid} -> {tgt_qid}: {msg}")

    print(f"\n=== OEIS CROSS-REFERENCE EXTRACTION SUMMARY ===")
    print(f"OEIS atoms scanned: {len(oeis_atoms)}")
    print(f"atoms with >= {args.min_refs} cross-refs: {atoms_with_refs}")
    print(f"avg refs per atom (when present): {candidates_total / max(atoms_with_refs, 1):.2f}")
    print(f"edges added: {edges_added}")
    print(f"edges skipped (target absent): {skipped_miss_tgt}")
    print(f"edges skipped (duplicate): {skipped_dup}")
    print(f"edges failed: {failed}")
    print(f"\nsample extractions:")
    for qid, refs in sample_extractions:
        print(f"  {qid} -> refs: {refs}")

    if args.dry_run:
        print(f"\n[DRY RUN] no edges written. Re-run without --dry-run to author.")


if __name__ == "__main__":
    main()
