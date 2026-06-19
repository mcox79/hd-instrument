#!/usr/bin/env python3
"""Cap-int Track-A apply: UNCLASSIFIED → reasoning_multihop (Skunkworks DRILL_A VET'd).

Adds ~13 atoms / ~9 capabilities to reasoning_multihop from the UNCLASSIFIED-65
bucket per Skunkworks's drill A per-row VET ruling.

Composition:
- 1 NEW cluster: q_b1_chain_depth_cliff (5 atoms; mixed-verdict legitimate
  depth-cliff per Skunkworks; expects I6 SOFT-flag review-not-fail)
- 8 singletons (hyp5_depth_ceiling + active_inference x2 + cognitive_core_counterfactual
  + combo2_p4_l3 + combo3 x3)

Includes self-assert `1 canonical per cluster` post-write (Skunkworks process
note from pp52 over-mint lesson; cheap front-line catch before routing).

A5-safe (metadata-only) + Store-LOAD verify post-write + verdict-faithful per
integration-check v1.1 vocab.
"""

import json
import os
from pathlib import Path

ROOT = Path("data/substrate_index")


# Q_B1 chain-depth cliff CLUSTER (Skunkworks: "legitimate depth-cliff" → I6 soft-flag)
Q_B1_CLUSTER = {
    "cluster_id": "q_b1_chain_depth_cliff",
    "shared_benchmark": "q_b1_chain_depth",
    "capability_name": "Q_B1 chain-depth reasoning (depth-cliff bound)",
    "canonical_proven_bound": (
        "Q_B1 chain reasoning succeeds at d=276 (boundary PASS) but fails at "
        "d>=287 (HARD_FAIL at d287/d293/d300/d400) -- the proven depth-cliff "
        "bound; canonical = d276 (deepest measured PASS = the discriminating-"
        "depth atom)"
    ),
    "scale_point_template": (
        "Q_B1 chain-depth scale-point at {tag} (cluster member of the proven "
        "depth-cliff bound at d~280)"
    ),
}

Q_B1_MEMBERS = {
    # canonical = deepest measured PASS (the discriminating-depth atom)
    "T3/EXP_q_b1_bisect_d276_v1_n16384": {
        "role": "canonical",
        "verdict": "PASS",
        "is_bound": False,  # canonical PASS = capability proven up to this depth
    },
    "T3/EXP_q_b1_bisect_d287_v1_n16384": {
        "role": "scale_point",
        "verdict": "HARD_FAIL",
        "is_bound": True,  # bound-verdict per v1.1
    },
    "T3/EXP_q_b1_bisect_d293_v1_n16384": {
        "role": "scale_point",
        "verdict": "HARD_FAIL",
        "is_bound": True,
    },
    "T3/EXP_q_b1_chain_depth_300_v1_n16384": {
        "role": "scale_point",
        "verdict": "HARD_FAIL",
        "is_bound": True,
    },
    "T3/EXP_q_b1_chain_depth_400_v1_n16384": {
        "role": "scale_point",
        "verdict": "HARD_FAIL",
        "is_bound": True,
    },
}


SINGLETONS = {
    "T3/EXP_hyp5_depth_ceiling_cpu_v1": {
        "verdict": "DISCRIMINATING_DEPTH_EXTENT",
        "is_bound": True,  # per v1.1 vocab
        "capability_name": "HYP-5 depth-ceiling discriminating bound",
        "proven_bound": (
            "HYP-5 depth-ceiling: DISCRIMINATING_DEPTH_EXTENT bound on the "
            "multi-relation-robust + depth-extended HYPERNYM held-out test"
        ),
    },
    "T3/EXP_active_inference_dpefe_h2_cpu_v1": {
        "verdict": "PASS",
        "is_bound": False,
        "capability_name": "Active inference DPEFE h2 reasoning",
        "proven_bound": (
            "Active inference DPEFE h2 reasoning at cert-grade"
        ),
    },
    "T3/EXP_active_inference_e2_tuned_cpu_v1": {
        "verdict": "MIDDLE_BAND",
        "is_bound": True,
        "capability_name": "Active inference E2 tuned reasoning bound",
        "proven_bound": (
            "Active inference E2 tuned reasoning MIDDLE_BAND "
            "(discriminating-but-not-strong)"
        ),
    },
    "T3/EXP_substrate_cognitive_core_counterfactual_v1": {
        "verdict": "PASS",
        "is_bound": False,
        "capability_name": "Cognitive core counterfactual reasoning",
        "proven_bound": (
            "Cognitive core counterfactual reasoning at cert-grade"
        ),
    },
    "T3/EXP_combo2_p4_l3_signed_am_v1_n32768_5seed_verification_v1": {
        "verdict": "PASS",
        "is_bound": False,
        "capability_name": "Combo2 p4 l3 signed-AM 5seed verification",
        "proven_bound": (
            "Combo2 p4 l3 signed-AM at cert-grade (5-seed verification "
            "at n=32768)"
        ),
    },
    "T3/EXP_combo3_pp51_5method_on_implicit_gram_v2_cert_fix_n4096": {
        "verdict": "MIDDLE_BAND",
        "is_bound": True,
        "capability_name": "Combo3 PP51 5-method on implicit gram (bound)",
        "proven_bound": (
            "Combo3 PP51 5-method on implicit gram MIDDLE_BAND "
            "(discriminating-but-not-strong; cert-fix v2 variant)"
        ),
    },
    "T3/EXP_combo3_unified_api_v1_n32768_5seed_verification_v1": {
        "verdict": "MIDDLE_BAND",
        "is_bound": True,
        "capability_name": "Combo3 unified API 5seed verification (bound)",
        "proven_bound": (
            "Combo3 unified API MIDDLE_BAND (5-seed verification at n=32768)"
        ),
    },
    "T3/EXP_combo3_unified_api_v1_n32768_local": {
        "verdict": "MIDDLE_BAND",
        "is_bound": True,
        "capability_name": "Combo3 unified API local-run (bound)",
        "proven_bound": (
            "Combo3 unified API MIDDLE_BAND (local-run at n=32768)"
        ),
    },
}


def build_patches():
    patches = {}

    # Q_B1 cluster
    canonical_qid = None
    for atom_id, info in Q_B1_MEMBERS.items():
        if info["role"] == "canonical":
            canonical_qid = f"math::{atom_id}"
            break

    for atom_id, info in Q_B1_MEMBERS.items():
        if info["role"] == "canonical":
            proven_bound = Q_B1_CLUSTER["canonical_proven_bound"]
        else:
            tag = atom_id.split("/")[-1]
            proven_bound = Q_B1_CLUSTER["scale_point_template"].format(tag=tag)
        patches[atom_id] = {
            "capint_integrated": True,
            "capint_cluster_id": Q_B1_CLUSTER["cluster_id"],
            "capint_cluster_member_role": info["role"],
            "capint_shared_benchmark": Q_B1_CLUSTER["shared_benchmark"],
            "capint_capability_name": Q_B1_CLUSTER["capability_name"],
            "capint_verdict": info["verdict"],
            "capint_is_bound": info["is_bound"],
            "capint_proven_bound": proven_bound,
            "capint_current_best_citation": canonical_qid,
            # Also re-bucket domain (was UNCLASSIFIED -> reasoning_multihop;
            # update via metadata.primary_domain if your enumerator output references it)
            "capint_primary_domain": "reasoning_multihop",
        }

    # Singletons
    for atom_id, spec in SINGLETONS.items():
        qid = f"math::{atom_id}"
        patches[atom_id] = {
            "capint_integrated": True,
            "capint_cluster_id": None,
            "capint_cluster_member_role": "singleton",
            "capint_shared_benchmark": None,
            "capint_capability_name": spec["capability_name"],
            "capint_verdict": spec["verdict"],
            "capint_is_bound": spec["is_bound"],
            "capint_proven_bound": spec["proven_bound"],
            "capint_current_best_citation": qid,
            "capint_primary_domain": "reasoning_multihop",
        }
    return patches


def patch_partition(partition_path, patches):
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
            if aid in patches:
                md = atom.get("metadata") or {}
                for k, v in patches[aid].items():
                    md[k] = v
                atom["metadata"] = md
                # Defense: no top-level capint_*
                for k in list(atom.keys()):
                    if k.startswith("capint_") and k != "metadata":
                        del atom[k]
                n_patched += 1
            dst.write(json.dumps(atom, ensure_ascii=False) + "\n")
    os.replace(tmp, partition_path)
    return n_patched, n_lines


def self_assert_one_canonical_per_cluster():
    """Per Skunkworks's process note: self-assert AFTER write that each
    cluster has exactly 1 canonical member. Catches over-mint before routing."""
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
        problems = []
        for cid, members in cluster_canonicals.items():
            if len(members) != 1:
                problems.append((cid, members))
        if problems:
            print("SELF-ASSERT FAIL: clusters with != 1 canonical:")
            for cid, members in problems:
                print(f"  {cid}: {len(members)} canonicals: {members}")
            return False
        print(f"SELF-ASSERT PASS: all {len(cluster_canonicals)} clusters "
              f"have exactly 1 canonical.")
        return True
    except Exception as e:
        print(f"SELF-ASSERT ERROR: {e}")
        return False


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
    print("CAP-INT TRACK-A APPLY: UNCLASSIFIED -> reasoning_multihop")
    print("=" * 80)
    print()

    patches = build_patches()
    print(f"Patches to apply: {len(patches)} atoms")
    print(f"  Q_B1 cluster: {len(Q_B1_MEMBERS)} members")
    print(f"  Singletons: {len(SINGLETONS)}")
    print()

    total_patched = 0
    for partition_path in ROOT.glob("*/atoms.jsonl"):
        n_patched, n_lines = patch_partition(partition_path, patches)
        if n_patched:
            total_patched += n_patched
            print(f"  {partition_path.parent.name}/atoms.jsonl: "
                  f"{n_patched} atoms / {n_lines} total lines")
    print()
    print(f"TOTAL patched: {total_patched}")
    print()

    # Store-LOAD verify
    ok, msg = store_load_verify()
    print(f"Store-LOAD verify: {msg}")
    if not ok:
        return

    # Self-assert 1-canonical-per-cluster
    if not self_assert_one_canonical_per_cluster():
        print("ABORT: self-assert FAIL; do not route to Skunkworks.")
        return

    print()
    print("APPLY + Store-LOAD verify + 1-canonical self-assert COMPLETE.")
    print("Route to Skunkworks for integration-check (q_b1 cluster expects "
          "I6 SOFT-flag review-not-fail per Skunkworks).")


if __name__ == "__main__":
    main()
