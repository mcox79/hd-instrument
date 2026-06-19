#!/usr/bin/env python3
"""Backfill metrics_source + run_mode + cell_commit metadata into the 4
canonicalized cert-VET-pending atoms.

Per Skunkworks 4-atom verdict-VET ruling 2026-06-19: promotion-path (1) =
recover metrics_source from original remote run-output. The metrics.json
files exist locally (each contains metrics_source=measured_graph_bfs_held_out
+ run_mode=full + cell_commit). Original gap was in atomization not source
data.

Pattern: in-place metadata patch (safe; per Skunkworks's refined write-hold:
metadata-PATCH on existing atoms via raw-JSONL is safe + Store-LOAD verify
gate) + verify post-patch.
"""

import json
import os
from pathlib import Path

ROOT = Path("data/substrate_index")

ATOMS_TO_PATCH = {
    "T3/EXP_b_alpha_broad_v2_denser_preview": Path(
        "data/exp_b_alpha_broad_v2_denser_preview/metrics.json"),
    "T3/EXP_b_alpha_broad_v3_2level": Path(
        "data/exp_b_alpha_broad_v3_2level/metrics.json"),
    "T3/EXP_partof_broad_after": Path(
        "data/exp_partof_broad_after/metrics.json"),
    "T3/EXP_partof_broad_before": Path(
        "data/exp_partof_broad_before/metrics.json"),
}

# Fields to recover from metrics.json + write into atom metadata
RECOVER_FIELDS = ["metrics_source", "run_mode", "cell_commit"]


def load_recovered_fields():
    recovered = {}
    for atom_id, metrics_path in ATOMS_TO_PATCH.items():
        if not metrics_path.exists():
            print(f"WARN: metrics.json missing for {atom_id}: {metrics_path}")
            continue
        with metrics_path.open(encoding="utf-8") as f:
            m = json.load(f)
        recovered[atom_id] = {k: m.get(k) for k in RECOVER_FIELDS}
        recovered[atom_id]["_source_metrics_path"] = str(metrics_path)
    return recovered


def patch_partition(partition_path, recovered):
    tmp = partition_path.with_suffix(".jsonl.tmp")
    n_patched = 0
    n_lines = 0
    patches = []
    with partition_path.open(encoding="utf-8") as src, \
         tmp.open("w", encoding="utf-8") as dst:
        for line in src:
            stripped = line.strip()
            if not stripped:
                dst.write(line)
                continue
            try:
                a = json.loads(stripped)
            except json.JSONDecodeError:
                dst.write(line)
                continue
            n_lines += 1
            aid = a.get("id")
            if aid in recovered:
                md = a.get("metadata") or {}
                # Backfill the 3 recovered fields
                fields = recovered[aid]
                for k in RECOVER_FIELDS:
                    if fields.get(k) is not None:
                        md[k] = fields[k]
                # Update cert_vet_status: ready for verdict-VET (was pending)
                md["cert_vet_status"] = "ready_for_verdict_vet"
                md["metrics_source_backfilled_2026-06-19"] = True
                md["metrics_source_backfill_from"] = fields["_source_metrics_path"]
                a["metadata"] = md
                n_patched += 1
                patches.append((aid, fields))
            dst.write(json.dumps(a, ensure_ascii=False) + "\n")
    os.replace(tmp, partition_path)
    return n_patched, n_lines, patches


def store_load_verify():
    try:
        from backend.substrate_index.partition import PartitionedStore
    except ImportError as e:
        return False, f"Import failed: {e}"
    try:
        ps = PartitionedStore(ROOT)
        atoms = list(ps.all_atoms())
        return True, f"PASS ({len(atoms)} atoms; round-trip clean)"
    except Exception as e:
        return False, f"FAIL: {e}"


def main():
    print("=" * 80)
    print("BACKFILL 4-atom metrics_source (promotion-path 1)")
    print("Per Skunkworks 4-atom verdict-VET ruling 2026-06-19")
    print("=" * 80)
    print()

    recovered = load_recovered_fields()
    print(f"Recovered metrics_source from {len(recovered)} of {len(ATOMS_TO_PATCH)} metrics.json files:")
    for aid, fields in recovered.items():
        print(f"  {aid}:")
        for k in RECOVER_FIELDS:
            print(f"    {k}: {fields.get(k)}")
    print()

    if len(recovered) != len(ATOMS_TO_PATCH):
        print("HALT: some metrics.json files missing; cannot proceed.")
        return 1

    # Apply per-partition (all 4 atoms in math partition)
    total_patched = 0
    all_patches = []
    for partition_path in ROOT.glob("*/atoms.jsonl"):
        n_patched, n_lines, patches = patch_partition(partition_path, recovered)
        if n_patched:
            total_patched += n_patched
            all_patches.extend(patches)
            print(f"  {partition_path.parent.name}/atoms.jsonl: "
                  f"{n_patched} atoms patched / {n_lines} total lines")

    print()
    print(f"TOTAL patched: {total_patched}")
    if total_patched != len(ATOMS_TO_PATCH):
        print(f"WARN: expected {len(ATOMS_TO_PATCH)} patches, got {total_patched}")

    # Store-LOAD verify
    print()
    print("=" * 80)
    print("STORE-LOAD verify")
    print("=" * 80)
    ok, msg = store_load_verify()
    print(f"  {msg}")
    if not ok:
        return 1

    # Spot-check: verify metrics_source is now in metadata
    print()
    print("Spot-check: confirm metrics_source in metadata via Store-LOAD")
    try:
        from backend.substrate_index.partition import PartitionedStore
        ps = PartitionedStore(ROOT)
        for atom in ps.all_atoms():
            if atom.id in ATOMS_TO_PATCH:
                md = atom.metadata or {}
                print(f"  {atom.id[:55]:55s}  metrics_source={md.get('metrics_source')}  "
                      f"run_mode={md.get('run_mode')}  cell_commit={md.get('cell_commit')}")
    except Exception as e:
        print(f"  verification error: {e}")

    print()
    print("=" * 80)
    print("BACKFILL COMPLETE.")
    print("Route to Skunkworks for verdict-VET promotion (CERT 575 -> up to 579).")
    print("=" * 80)
    return 0


if __name__ == "__main__":
    main()
