#!/usr/bin/env python3
"""Mechanical fix per Skunkworks 3-I-check note 2026-06-19:
pp52_hebbian_lora_speedup minor flag = pp52_hebbian_n4096 not yet integrated +
pp52_hebbian_n8192 missing capint_primary_domain.

Decision: 2-member uniform-HARD_FAIL mini-cluster (matches the
b_alpha_broad uniform-MIDDLE_BAND cluster pattern); canonical = n8192 (larger
N + already integrated as singleton; will be patched to canonical role).

A5-safe metadata-only.
"""

import json
import os
from pathlib import Path

ROOT = Path("data/substrate_index")
CLUSTER_ID = "pp52_hebbian_lora_speedup"
SHARED_BENCHMARK = "pp52_hebbian_lora_speedup"
CAPABILITY_NAME = "PP52 Hebbian-LoRA speedup (uniform-HARD_FAIL bound)"

CANONICAL_ATOM_ID = "T3/EXP_pp52_hebbian_lora_speedup_n8192_v1"
CANONICAL_QID = f"math::{CANONICAL_ATOM_ID}"
CANONICAL_PROVEN_BOUND = (
    "PP52 Hebbian-LoRA speedup uniform-HARD_FAIL across n=4096 + n=8192 "
    "(2-member uniform-HARD_FAIL cluster; proven ceiling on the hebbian-LoRA "
    "speedup approach at the measured n-scale)"
)

SCALE_POINT_ATOM_ID = "T3/EXP_pp52_hebbian_lora_speedup_n4096_v1"
SCALE_POINT_PROVEN_BOUND = (
    "PP52 Hebbian-LoRA speedup n=4096 scale-point (sibling-HARD_FAIL to n=8192; "
    "consistent uniform-HARD_FAIL across the measured scale)"
)


PATCHES = {
    CANONICAL_ATOM_ID: {
        "capint_integrated": True,
        "capint_cluster_id": CLUSTER_ID,
        "capint_cluster_member_role": "canonical",
        "capint_shared_benchmark": SHARED_BENCHMARK,
        "capint_capability_name": CAPABILITY_NAME,
        "capint_verdict": "HARD_FAIL",
        "capint_is_bound": True,  # HARD_FAIL = bound per v1.1
        "capint_proven_bound": CANONICAL_PROVEN_BOUND,
        "capint_current_best_citation": CANONICAL_QID,
        "capint_primary_domain": "retrieval",
    },
    SCALE_POINT_ATOM_ID: {
        "capint_integrated": True,
        "capint_cluster_id": CLUSTER_ID,
        "capint_cluster_member_role": "scale_point",
        "capint_shared_benchmark": SHARED_BENCHMARK,
        "capint_capability_name": CAPABILITY_NAME,
        "capint_verdict": "HARD_FAIL",
        "capint_is_bound": True,
        "capint_proven_bound": SCALE_POINT_PROVEN_BOUND,
        "capint_current_best_citation": CANONICAL_QID,
        "capint_primary_domain": "retrieval",
    },
}


def patch_partition(partition_path):
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
            aid = atom.get("id")
            if aid in PATCHES:
                md = atom.get("metadata") or {}
                for k, v in PATCHES[aid].items():
                    md[k] = v
                atom["metadata"] = md
                for k in list(atom.keys()):
                    if k.startswith("capint_") and k != "metadata":
                        del atom[k]
                n_patched += 1
            dst.write(json.dumps(atom, ensure_ascii=False) + "\n")
    os.replace(tmp, partition_path)
    return n_patched, n_lines


def self_assert_one_canonical_per_cluster():
    try:
        from backend.substrate_index.partition import PartitionedStore
        ps = PartitionedStore(ROOT)
        cluster_canonicals = {}
        for a in ps.all_atoms():
            md = a.metadata or {}
            cid = md.get("capint_cluster_id")
            role = md.get("capint_cluster_member_role")
            if cid and role == "canonical":
                cluster_canonicals.setdefault(cid, []).append(a.id)
        problems = [(cid, m) for cid, m in cluster_canonicals.items()
                    if len(m) != 1]
        if problems:
            print("SELF-ASSERT FAIL:")
            for cid, m in problems:
                print(f"  {cid}: {len(m)} canonicals: {m}")
            return False
        print(f"SELF-ASSERT PASS: all {len(cluster_canonicals)} clusters have exactly 1 canonical.")
        return True
    except Exception as e:
        print(f"SELF-ASSERT ERROR: {e}")
        return False


def store_load_verify():
    try:
        from backend.substrate_index.partition import PartitionedStore
        ps = PartitionedStore(ROOT)
        atoms = list(ps.all_atoms())
        return True, f"PASS ({len(atoms)} atoms)"
    except Exception as e:
        return False, f"FAIL: {e}"


def main():
    print("=" * 80)
    print("FIX: pp52_hebbian_lora_speedup minor flag (Skunkworks I-check note)")
    print("=" * 80)
    print(f"Cluster: {CLUSTER_ID}")
    print(f"Canonical: {CANONICAL_ATOM_ID}")
    print(f"Scale_point: {SCALE_POINT_ATOM_ID}")
    print()

    total = 0
    for partition_path in ROOT.glob("*/atoms.jsonl"):
        n, lines = patch_partition(partition_path)
        if n:
            total += n
            print(f"  {partition_path.parent.name}: {n} atoms / {lines} lines")
    print()
    print(f"TOTAL: {total}")

    ok, msg = store_load_verify()
    print(f"Store-LOAD: {msg}")
    if not ok:
        return

    if not self_assert_one_canonical_per_cluster():
        return

    print()
    print("FIX COMPLETE. Route to Skunkworks for re-check.")


if __name__ == "__main__":
    main()
