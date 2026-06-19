#!/usr/bin/env python3
"""Cap-int Piece 3: Track-A metadata-population apply tool.

Takes a JSON file of Skunkworks-VET'd ACCEPT rows + applies metadata patches
to the target capability atoms in-place (raw-JSONL pattern; proven on Item 4).

INPUT schema (the per-row VET output Skunkworks streams):
  {
    "vet_ts": "2026-06-19",
    "vet_batch": "reasoning_multihop_top_30_batch_1",
    "accepted_rows": [
      {
        "capability_atom_id": "PP-371_reasoning_routing",  # which atom to patch
        "current_best_citation": "math::T3/EXP_<id>",      # cert-grade record-ID
        "cluster_id": "reasoning_multihop",                # cluster classification
        "interface_contract_slot": "narrow_qa",            # contract slot per Item-7
        "proven_bound": "...",                             # honest-scoped bound
        "evidence_atom_ids": ["..."],                      # cert-grade record IDs
        "shared_benchmark": "narrow_qa_v1",                # benchmark per Item-7
        "is_new_capability_atom": false,                   # else route to Exp-Dev for atom-add
        "skunkworks_vet_notes": "..."
      },
      ...
    ],
    "bounced_rows": [...],  # rows Skunkworks REJECTED (headline-vs-bound mismatch); FYI for Director
    "needs_rework_rows": [...]
  }

Each ACCEPT row patches the capability atom's metadata:
  metadata.current_best = current_best_citation
  metadata.cluster_id = cluster_id
  metadata.interface_contract_slot = interface_contract_slot
  metadata.proven_bound = proven_bound
  metadata.evidence_atom_ids = evidence_atom_ids
  metadata.shared_benchmark = shared_benchmark
  metadata.capint_vet_ts = vet_ts
  metadata.capint_vet_batch = vet_batch

A5-SAFE: tier/pq/relevance/atom-id/composes_with untouched.
Per MUST-FIX semantics: all new fields go INTO metadata (NOT top-level).
RAW-JSONL pattern: per-line rewrite + atomic os.replace; verify via raw-read.

NEW capability atoms (is_new_capability_atom=true): ROUTE to Exp-Dev (proven
pattern for new atom-add; avoids Director silent-fail id-FORM readback risk).
"""

import json
import os
import sys
from pathlib import Path

ROOT = Path("data/substrate_index")


def load_vet_output(vet_file):
    with open(vet_file, encoding="utf-8") as f:
        return json.load(f)


def find_partition_for_atom(atom_id):
    for atoms_file in ROOT.glob("*/atoms.jsonl"):
        with atoms_file.open(encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    a = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if a.get("id") == atom_id:
                    return atoms_file
    return None


METADATA_FIELDS = [
    "current_best", "cluster_id", "interface_contract_slot",
    "proven_bound", "evidence_atom_ids", "shared_benchmark",
    "capint_vet_ts", "capint_vet_batch",
]


def apply_track_a_patch(atom_dict, row, vet_ts, vet_batch):
    """Mutate atom_dict's metadata in-place per Track-A row."""
    md = atom_dict.get("metadata") or {}
    md["current_best"] = row.get("current_best_citation")
    md["cluster_id"] = row.get("cluster_id")
    md["interface_contract_slot"] = row.get("interface_contract_slot")
    md["proven_bound"] = row.get("proven_bound")
    md["evidence_atom_ids"] = row.get("evidence_atom_ids") or []
    md["shared_benchmark"] = row.get("shared_benchmark")
    md["capint_vet_ts"] = vet_ts
    md["capint_vet_batch"] = vet_batch
    atom_dict["metadata"] = md

    # Cleanup any stale top-level placements (defense-in-depth per MUST-FIX)
    for key in METADATA_FIELDS:
        if key in atom_dict and key != "metadata":
            del atom_dict[key]
    return atom_dict


def rewrite_partition(partition_path, atom_patches, vet_ts, vet_batch):
    """Re-write partition with patched atoms."""
    tmp = partition_path.with_suffix(".jsonl.tmp")
    n_patched = 0
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
            atom_id = atom.get("id")
            if atom_id in atom_patches:
                atom = apply_track_a_patch(atom, atom_patches[atom_id],
                                           vet_ts, vet_batch)
                n_patched += 1
            dst.write(json.dumps(atom, ensure_ascii=False) + "\n")
    os.replace(tmp, partition_path)
    return n_patched, n_lines


def verify_atom_post_patch(atom_id, row):
    """RAW jsonl re-read to verify patch landed in metadata.
    Per MUST-FIX semantics: must be in metadata, NOT top-level.
    """
    for atoms_file in ROOT.glob("*/atoms.jsonl"):
        with atoms_file.open(encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    a = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if a.get("id") == atom_id:
                    md = a.get("metadata") or {}
                    # Cleanup verification: NO top-level placement
                    for key in METADATA_FIELDS:
                        if key in a and key != "metadata":
                            return False, (f"TOP-LEVEL {key} still present "
                                           f"(silent-loss risk)")
                    # Value verification
                    if md.get("current_best") != row.get("current_best_citation"):
                        return False, "metadata.current_best mismatch"
                    if md.get("cluster_id") != row.get("cluster_id"):
                        return False, "metadata.cluster_id mismatch"
                    if md.get("proven_bound") != row.get("proven_bound"):
                        return False, "metadata.proven_bound mismatch"
                    return True, "OK"
    return False, "atom not found"


def main(vet_file):
    print("=" * 80)
    print("CAP-INT PIECE 3: Track-A metadata-population APPLY")
    print(f"VET file: {vet_file}")
    print("=" * 80)
    print()

    vet_data = load_vet_output(vet_file)
    vet_ts = vet_data.get("vet_ts")
    vet_batch = vet_data.get("vet_batch")
    accepted = vet_data.get("accepted_rows") or []
    bounced = vet_data.get("bounced_rows") or []
    needs_rework = vet_data.get("needs_rework_rows") or []

    print(f"VET timestamp: {vet_ts}")
    print(f"VET batch: {vet_batch}")
    print(f"  accepted: {len(accepted)}")
    print(f"  bounced: {len(bounced)}")
    print(f"  needs_rework: {len(needs_rework)}")
    print()

    if not accepted:
        print("No accepted rows to apply. Done.")
        return

    # Filter: existing-capability-atom rows we can patch directly
    existing_patches = {}
    new_atoms_routing = []
    for row in accepted:
        if row.get("is_new_capability_atom"):
            new_atoms_routing.append(row)
            continue
        cap_id = row.get("capability_atom_id")
        if not cap_id:
            print(f"  WARN: row missing capability_atom_id; skipping")
            continue
        existing_patches[cap_id] = row

    print(f"Existing-atom patches: {len(existing_patches)}")
    print(f"New-atom routings (to Exp-Dev): {len(new_atoms_routing)}")
    print()

    # Group by partition + apply
    by_partition = {}
    not_found = []
    for atom_id in existing_patches:
        p = find_partition_for_atom(atom_id)
        if p is None:
            not_found.append(atom_id)
            continue
        by_partition.setdefault(p, {})[atom_id] = existing_patches[atom_id]

    if not_found:
        print(f"WARN: {len(not_found)} atoms not found in any partition:")
        for aid in not_found:
            print(f"  {aid}")
        print()

    total_patched = 0
    for partition_path, atom_patches in by_partition.items():
        print(f"Rewriting partition: {partition_path.parent.name}/atoms.jsonl "
              f"({len(atom_patches)} atoms)...")
        n_patched, n_lines = rewrite_partition(partition_path, atom_patches,
                                               vet_ts, vet_batch)
        print(f"  patched={n_patched}  total_lines={n_lines}")
        total_patched += n_patched

    print()
    print(f"TOTAL existing-atom patches applied: {total_patched}")
    print()

    # Verify
    print("=" * 80)
    print("VERIFY (raw JSONL re-read; no get_atom; no silent-fail risk)")
    print("=" * 80)
    n_pass = 0
    n_fail = 0
    failures = []
    for atom_id, row in existing_patches.items():
        ok, msg = verify_atom_post_patch(atom_id, row)
        if ok:
            n_pass += 1
        else:
            n_fail += 1
            failures.append((atom_id, msg))
    print(f"PASS: {n_pass}/{len(existing_patches)}")
    print(f"FAIL: {n_fail}/{len(existing_patches)}")
    if failures:
        print()
        print("Failures:")
        for aid, msg in failures[:10]:
            print(f"  {aid}: {msg}")
    print()

    if new_atoms_routing:
        print(f"{len(new_atoms_routing)} new-capability-atom additions need "
              "routing to Exp-Dev (proven pattern for atom-add):")
        for row in new_atoms_routing[:5]:
            print(f"  proven_bound: {row.get('proven_bound', '')[:80]}")
            print(f"    cluster: {row.get('cluster_id')}")
            print(f"    evidence: {row.get('evidence_atom_ids', [])[:3]}")

    print()
    print("APPLY COMPLETE. Route to Skunkworks for landed-VET (to_dict "
          "round-trip-survival on metadata fields).")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: capint_piece3_track_a_apply.py <vet_output.json>")
        sys.exit(1)
    main(sys.argv[1])
