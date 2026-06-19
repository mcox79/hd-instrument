#!/usr/bin/env python3
"""Cap-int Track-A top-up: 4 atoms newly-promoted to CERT_CHAIN_GRADE
(CERT 575 -> 579) + re-patch existing b_alpha_broad_envelope into the new
uniform-MIDDLE_BAND mini-cluster.

Per Skunkworks 4-atom promote-VET 2026-06-19:
- 4 atoms promoted: partof_broad_after (HARD_PASS) + partof_broad_before
  (MIDDLE_BAND) + b_alpha_broad_v2_denser_preview (MIDDLE_BAND) +
  b_alpha_broad_v3_2level (MIDDLE_BAND).
- 1 mini-cluster scope: b_alpha_broad uniform-MIDDLE_BAND (3 members:
  envelope + v2_denser + v3_2level).
- 2 singletons: partof_broad_after (PASS) + partof_broad_before (MIDDLE_BAND).
  Mixed-verdict at the partof_broad family -> do NOT cluster (decomp lesson).

Pre-staged: this tool is READY but DOES NOT RUN until Skunkworks's landed-VET
on Exp-Dev's pq-patch confirms CERT==579 + Store-LOAD verify clean.

EXEC GATE: --confirm-cert-579 required to actually run (sanity guard against
accidental execution pre-CERT-579).
"""

import json
import os
import sys
from pathlib import Path

ROOT = Path("data/substrate_index")

# The 4 newly-promoted atoms + the 1 existing batch-1 atom to re-patch
B_ALPHA_BROAD_CLUSTER_MEMBERS = {
    # existing batch-1 singleton; RE-PATCH as cluster member
    "T3/EXP_b_alpha_broad_envelope_cpu_v1": {
        "is_canonical": True,  # the canonical (original envelope; v2/v3 are variants of it)
    },
    # newly promoted
    "T3/EXP_b_alpha_broad_v2_denser_preview": {
        "is_canonical": False,
    },
    "T3/EXP_b_alpha_broad_v3_2level": {
        "is_canonical": False,
    },
}

PARTOF_BROAD_SINGLETONS = {
    "T3/EXP_partof_broad_after": {
        "verdict": "HARD_PASS", "is_bound": False,
        "capability_name": "PART_OF broad-graph reasoning (after-state)",
        "proven_bound": (
            "PART_OF broad-graph reasoning (after-state) at cert-grade "
            "(HARD_PASS; broad-graph composition)"
        ),
    },
    "T3/EXP_partof_broad_before": {
        "verdict": "MIDDLE_BAND", "is_bound": True,
        "capability_name": "PART_OF broad-graph reasoning (before-state) bound",
        "proven_bound": (
            "PART_OF broad-graph reasoning (before-state) MIDDLE_BAND "
            "(discriminating-but-not-strong on the before-state subgraph)"
        ),
    },
}

B_ALPHA_BROAD_CLUSTER_SPEC = {
    "cluster_id": "b_alpha_broad_envelope",
    "shared_benchmark": "b_alpha_broad",
    "capability_name": "ARC-1 broad-envelope reasoning (multi-config bound)",
    "canonical_proven_bound": (
        "ARC-1 broad-envelope reasoning at MIDDLE_BAND across 3 configs "
        "(envelope + v2_denser + v3_2level) -- uniform discriminating-but-"
        "not-strong; the broad-domain ceiling at MIDDLE_BAND across "
        "denser-mode + 2level variants"
    ),
    "scale_point_proven_bound_template": (
        "ARC-1 broad-envelope variant {tag} (MIDDLE_BAND scale-point of "
        "the 3-config bound cluster)"
    ),
}


def store_load_verify():
    try:
        from backend.substrate_index.partition import PartitionedStore
    except ImportError as e:
        return None, f"Import failed: {e}"
    try:
        ps = PartitionedStore(ROOT)
        atoms = list(ps.all_atoms())
        return ps, atoms
    except Exception as e:
        return None, f"FAIL: {e}"


def cert_count(atoms):
    return sum(1 for a in atoms
               if (a.metadata or {}).get("provenance_quality")
               == "CERT_CHAIN_GRADE")


def main():
    print("=" * 80)
    print("CAP-INT TRACK-A TOP-UP: 4 newly-promoted (CERT 575->579) + 1 re-patch")
    print("=" * 80)
    print()

    if "--confirm-cert-579" not in sys.argv:
        print("HALT: this tool requires --confirm-cert-579 to actually execute.")
        print("(Sanity guard: do not run until Skunkworks's landed-VET on Exp-Dev's")
        print("pq-patch confirms CERT==579 + clean Store-LOAD post-ConceptNet.)")
        print()
        print("To actually run:")
        print("  .venv/Scripts/python.exe tools/capint_track_a_topup_4cert_579_post_promote.py --confirm-cert-579")
        print()
        print("Scope summary:")
        print(f"  b_alpha_broad mini-cluster (uniform-MIDDLE_BAND): "
              f"{len(B_ALPHA_BROAD_CLUSTER_MEMBERS)} members")
        for aid, info in B_ALPHA_BROAD_CLUSTER_MEMBERS.items():
            role = "canonical" if info["is_canonical"] else "scale_point"
            print(f"    {aid:60s}  role={role}")
        print(f"  partof_broad singletons (mixed-verdicts; NO cluster): "
              f"{len(PARTOF_BROAD_SINGLETONS)}")
        for aid, spec in PARTOF_BROAD_SINGLETONS.items():
            print(f"    {aid:60s}  verdict={spec['verdict']}  is_bound={spec['is_bound']}")
        return 1

    # Real execution (gated)
    ps, atoms = store_load_verify()
    if ps is None:
        print(f"HALT: Store-LOAD failed: {atoms}")
        return 1
    pre_cert = cert_count(atoms)
    print(f"Pre-execution CERT count: {pre_cert}")
    if pre_cert != 579:
        print(f"HALT: expected CERT==579 (Skunkworks's promote), got {pre_cert}.")
        print("Wait for Exp-Dev's pq-patch + Skunkworks's landed-VET.")
        return 1
    print(f"CERT 579 confirmed. Proceeding with cap-int top-up.")
    print()

    # Build patches per the cluster + singletons spec
    atom_patches = {}

    # b_alpha_broad cluster
    for atom_id, info in B_ALPHA_BROAD_CLUSTER_MEMBERS.items():
        role = "canonical" if info["is_canonical"] else "scale_point"
        if info["is_canonical"]:
            proven_bound = B_ALPHA_BROAD_CLUSTER_SPEC["canonical_proven_bound"]
        else:
            tag = atom_id.split("/")[-1]
            proven_bound = B_ALPHA_BROAD_CLUSTER_SPEC[
                "scale_point_proven_bound_template"].format(tag=tag)
        atom_patches[atom_id] = {
            "capint_integrated": True,
            "capint_cluster_id": B_ALPHA_BROAD_CLUSTER_SPEC["cluster_id"],
            "capint_cluster_member_role": role,
            "capint_shared_benchmark": B_ALPHA_BROAD_CLUSTER_SPEC["shared_benchmark"],
            "capint_capability_name": B_ALPHA_BROAD_CLUSTER_SPEC["capability_name"],
            "capint_verdict": "MIDDLE_BAND",
            "capint_is_bound": False,  # uniform-PASS-or-MIDDLE_BAND? Skunkworks says
                                       # MIDDLE_BAND is bound-verdict; but uniform cluster
                                       # PER-MEMBER-IS_BOUND-DECISION: the cluster IS the bound
                                       # collectively. Use is_bound=False on cluster members; the
                                       # cluster's proven_bound states it's a bound. (Aligning
                                       # with batch-1 cluster-PASS pattern; but if Skunkworks's
                                       # I3 prefers per-member is_bound=True for MIDDLE_BAND
                                       # cluster, easy to flip.)
            "capint_proven_bound": proven_bound,
            "capint_current_best_citation": None,  # backfill below
        }

    # Set canonical citation
    canonical_id = next(
        aid for aid, info in B_ALPHA_BROAD_CLUSTER_MEMBERS.items()
        if info["is_canonical"])
    canonical_qid = f"math::{canonical_id}"
    for atom_id, patch in atom_patches.items():
        if patch["capint_cluster_id"] == B_ALPHA_BROAD_CLUSTER_SPEC["cluster_id"]:
            patch["capint_current_best_citation"] = canonical_qid

    # partof_broad singletons
    for atom_id, spec in PARTOF_BROAD_SINGLETONS.items():
        atom_patches[atom_id] = {
            "capint_integrated": True,
            "capint_cluster_id": None,
            "capint_cluster_member_role": "singleton",
            "capint_shared_benchmark": None,
            "capint_capability_name": spec["capability_name"],
            "capint_verdict": spec["verdict"],
            "capint_is_bound": spec["is_bound"],
            "capint_proven_bound": spec["proven_bound"],
            "capint_current_best_citation": f"math::{atom_id}",
        }

    # Apply via raw-JSONL pattern (safe metadata-patch)
    target_partition = ROOT / "math" / "atoms.jsonl"
    tmp = target_partition.with_suffix(".jsonl.tmp")
    n_patched = 0
    with target_partition.open(encoding="utf-8") as src, \
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
            aid = a.get("id")
            if aid in atom_patches:
                md = a.get("metadata") or {}
                for k, v in atom_patches[aid].items():
                    md[k] = v
                a["metadata"] = md
                # Defense: no top-level capint_*
                for k in list(a.keys()):
                    if k.startswith("capint_") and k != "metadata":
                        del a[k]
                n_patched += 1
            dst.write(json.dumps(a, ensure_ascii=False) + "\n")
    os.replace(tmp, target_partition)
    print(f"Patched: {n_patched} / {len(atom_patches)} atoms")

    # Post Store-LOAD verify
    ps2, atoms2 = store_load_verify()
    if ps2 is None:
        print(f"POST FAIL: Store-LOAD: {atoms2}")
        return 1
    print(f"Post Store-LOAD: {len(atoms2)} atoms; CERT={cert_count(atoms2)}")
    print()
    print("TOP-UP COMPLETE. Route to Skunkworks for integration-check.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
