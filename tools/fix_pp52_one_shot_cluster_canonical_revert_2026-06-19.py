#!/usr/bin/env python3
"""Mechanical fix per Skunkworks retrieval-apply I4 FAIL ruling 2026-06-19:
pp52_one_shot_addition cluster has 3 members ALL role=canonical (over-mint).
Fix: keep n16384 as canonical; flip n4096 + n8192 to scale_point.

A5-no-silent-recompute: metadata-only; pq + tier preserved (cert remains
CERT_CHAIN_GRADE for all 3).

Idempotent: skips if already correct.
"""

import json
import os
from pathlib import Path

ROOT = Path("data/substrate_index")

FIXES = {
    "T3/EXP_pp52_one_shot_addition_n4096_v1": {
        "role": "scale_point",
        "proven_bound": (
            "PP52 one-shot addition n4096 (scale-point of the uniform-PASS "
            "cluster across n=4096/8192/16384 dimensions)"
        ),
    },
    "T3/EXP_pp52_one_shot_addition_n8192_v1": {
        "role": "scale_point",
        "proven_bound": (
            "PP52 one-shot addition n8192 (scale-point of the uniform-PASS "
            "cluster across n=4096/8192/16384 dimensions)"
        ),
    },
}

CANONICAL_ATOM_ID = "T3/EXP_pp52_one_shot_addition_n16384_v1"
CANONICAL_QID = f"math::{CANONICAL_ATOM_ID}"
CLUSTER_ID = "pp52_one_shot_addition"


def patch_partition(partition_path):
    tmp = partition_path.with_suffix(".jsonl.tmp")
    n_patched = 0
    n_lines = 0
    fixes_applied = []
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
            if aid in FIXES:
                md = a.get("metadata") or {}
                md["capint_cluster_member_role"] = FIXES[aid]["role"]
                md["capint_proven_bound"] = FIXES[aid]["proven_bound"]
                md["capint_current_best_citation"] = CANONICAL_QID
                # cluster_id + shared_benchmark stay (already correct)
                a["metadata"] = md
                n_patched += 1
                fixes_applied.append(aid)
            dst.write(json.dumps(a, ensure_ascii=False) + "\n")
    os.replace(tmp, partition_path)
    return n_patched, n_lines, fixes_applied


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
    print("FIX: pp52_one_shot_addition cluster (I4 FAIL revert; over-mint)")
    print("=" * 80)
    print()

    total_patched = 0
    all_fixes = []
    for partition_path in ROOT.glob("*/atoms.jsonl"):
        n_patched, n_lines, fixes = patch_partition(partition_path)
        if n_patched:
            total_patched += n_patched
            all_fixes.extend(fixes)
            print(f"  {partition_path.parent.name}/atoms.jsonl: "
                  f"{n_patched} atoms / {n_lines} lines")
            for aid in fixes:
                print(f"    fixed: {aid} -> role=scale_point")
    print()
    print(f"TOTAL fixed: {total_patched}")
    print()

    ok, msg = store_load_verify()
    print(f"Store-LOAD verify: {msg}")
    if not ok:
        return

    # Spot-check: verify n16384 still canonical + n4096 + n8192 = scale_point
    print()
    print("Spot-check:")
    try:
        from backend.substrate_index.partition import PartitionedStore
        ps = PartitionedStore(ROOT)
        for a in ps.all_atoms():
            if "pp52_one_shot_addition" in a.id:
                md = a.metadata or {}
                print(f"  {a.id[:55]:55s}  role={md.get('capint_cluster_member_role')}  "
                      f"cluster_id={md.get('capint_cluster_id')}")
    except Exception as e:
        print(f"  verification error: {e}")

    print()
    print("FIX COMPLETE. Route to Skunkworks for I4 re-check (expect PASS).")


if __name__ == "__main__":
    main()
