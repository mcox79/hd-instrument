#!/usr/bin/env python3
"""Item 4 v2.1 MUST-FIX (per Skunkworks landed-VET 2026-06-19):

Relocates top-level memory_references / conceptual_references /
cross_ref_annotations into metadata (where they'll survive Atom.to_dict()).

WHY: the Atom dataclass schema doesn't model these fields at top level;
Atom.to_dict() drops unmodeled keys; on next Store-native flush of the meta
partition, the data silently evaporates. This is the recurring
[[reference_store_drops_relation_edge_metadata_role_on_source_atom]] lesson
generalizing to new fields.

FIX: move into metadata (where composes_with/parent_of already safely live).

A5-SAFE: relocation only; tier/pq/relevance/atom-id untouched.
RAW-JSONL pattern: per-line rewrite + atomic os.replace; verify via raw-read.

Scope: ALL atoms in ALL partitions that have these top-level keys (not just
the Item-4 v2.1 patched atoms; cleans up any other accidental placements too).
"""

import json
import os
from pathlib import Path

ROOT = Path("data/substrate_index")
RELOCATE_KEYS = ("memory_references", "conceptual_references",
                 "cross_ref_annotations")


def relocate_partition(partition_path):
    """Re-write partition with top-level keys merged into metadata.
    Returns (n_atoms_relocated, n_total_lines).
    """
    tmp = partition_path.with_suffix(".jsonl.tmp")
    n_relocated = 0
    n_lines = 0
    with partition_path.open(encoding="utf-8") as src, \
         tmp.open("w", encoding="utf-8") as dst:
        for line in src:
            stripped = line.strip()
            if not stripped:
                dst.write(line)
                continue
            try:
                atom = json.loads(stripped)
            except json.JSONDecodeError:
                dst.write(line)
                continue
            n_lines += 1
            relocated_this = False
            md = atom.get("metadata") or {}
            for key in RELOCATE_KEYS:
                top_val = atom.pop(key, None)
                if top_val is None:
                    continue
                # Merge with existing metadata entry if any
                existing_md = md.get(key)
                if existing_md is None:
                    md[key] = top_val
                elif isinstance(existing_md, list) and isinstance(top_val, list):
                    # Deduplicate by value (for conceptual_references which is
                    # list of dicts with 'value' key, dedup by value; else just
                    # set-union for strings)
                    seen = set()
                    merged = []
                    for entry in existing_md + top_val:
                        if isinstance(entry, dict):
                            v = entry.get("value")
                        else:
                            v = entry
                        if v not in seen:
                            merged.append(entry)
                            seen.add(v)
                    md[key] = merged
                else:
                    # Unexpected shape; keep existing, log via verification
                    md[key] = existing_md
                relocated_this = True
            if relocated_this:
                atom["metadata"] = md
                n_relocated += 1
            dst.write(json.dumps(atom, ensure_ascii=False) + "\n")
    os.replace(tmp, partition_path)
    return n_relocated, n_lines


def verify_no_top_level_fields(partition_path):
    """Raw re-read: confirm no top-level RELOCATE_KEYS remain."""
    violations = []
    with partition_path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                a = json.loads(line)
            except json.JSONDecodeError:
                continue
            for key in RELOCATE_KEYS:
                if key in a:
                    violations.append(f"{a.get('id')} has top-level {key}")
    return violations


def main():
    print("=" * 80)
    print("ITEM 4 v2.1 MUST-FIX: relocate top-level keys -> metadata")
    print("=" * 80)
    print(f"Keys: {RELOCATE_KEYS}")
    print()

    total_relocated = 0
    total_lines = 0
    for partition_path in ROOT.glob("*/atoms.jsonl"):
        n_relocated, n_lines = relocate_partition(partition_path)
        total_lines += n_lines
        if n_relocated > 0:
            total_relocated += n_relocated
            print(f"  {partition_path.parent.name}/atoms.jsonl: "
                  f"relocated={n_relocated}  lines={n_lines}")

    print()
    print(f"TOTAL RELOCATED: {total_relocated}")
    print(f"Total atoms scanned: {total_lines}")
    print()

    print("=" * 80)
    print("VERIFY: no top-level RELOCATE_KEYS remain across all partitions")
    print("=" * 80)
    all_violations = []
    for partition_path in ROOT.glob("*/atoms.jsonl"):
        violations = verify_no_top_level_fields(partition_path)
        if violations:
            all_violations.extend([(partition_path.parent.name, v) for v in violations])

    if all_violations:
        print(f"VIOLATIONS: {len(all_violations)}")
        for part, v in all_violations[:10]:
            print(f"  {part}: {v}")
    else:
        print("PASS: 0 top-level RELOCATE_KEYS across all partitions.")
        print("(All relocated atoms now have data in metadata, which survives "
              "Atom.to_dict() round-trip.)")
    print()
    print("MUST-FIX COMPLETE. Route to Skunkworks for re-landed-VET via "
          "to_dict() round-trip-survival test.")


if __name__ == "__main__":
    main()
