#!/usr/bin/env python3
"""Cap-int Track-A apply: UNCLASSIFIED → cognitive_capacity (Skunkworks DRILL_A VET'd).

Per Skunkworks's drill A per-row VET:
- pp48_nkt depth_3 + depth_11 → EXTEND existing PP48_NKT 2-axis cluster (now 13 members)
- pp49_hrc x3 (mixed verdict) → SINGLETONS per decomp lesson
- pp58_scs_tau x4 (mixed verdict) → SINGLETONS
- substrate_cfrpe x2 (mixed verdict) → SINGLETONS
- substrate_continual_learning x2 (mixed verdict) → SINGLETONS
- substrate_long_conversation x2 (uniform-PASS) → SINGLETONS (Skunkworks lean; no mini-cluster)
- substrate_task_complexity → SINGLETON

Total: 2 cluster extensions + 14 singletons = 16 atoms / 15 cap deltas
(net +14 caps because pp48_nkt cluster doesn't add a cap; it extends existing).

Includes self-assert + Store-LOAD verify + verdict-faithful per integration-check v1.1.
"""

import json
import os
from pathlib import Path

ROOT = Path("data/substrate_index")


# Existing PP48_NKT cluster (defined in cognitive_capacity batch-1):
# cluster_id = "pp48_nkt_depth_and_cross_n"
# canonical = T3/EXP_pp48_nkt_depth_23_v1_n4096 (deepest measured)
# These 2 atoms EXTEND it as scale_points
PP48_NKT_EXTENSIONS = {
    "T3/EXP_pp48_nkt_depth_3_baseline_verification_v1_n4096": {
        "verdict": "PASS",
        "tag_short": "depth_3_baseline",
    },
    "T3/EXP_pp48_nkt_depth_11_v1_n4096": {
        "verdict": "PASS",
        "tag_short": "depth_11",
    },
}

PP48_NKT_CLUSTER_REF = {
    "cluster_id": "pp48_nkt_depth_and_cross_n",
    "shared_benchmark": "pp48_nkt",
    "capability_name": "PP48 NKT 2-axis (depth + cross-n) scaling",
    "canonical_atom_id": "T3/EXP_pp48_nkt_depth_23_v1_n4096",  # existing canonical
}


# Singletons (cognitive_capacity domain; verdict-faithful)
SINGLETONS = {
    "T3/EXP_pp49_hrc_cf_depth_band_sweep_v1_n4096": {
        "verdict": "HARD_FAIL",
        "is_bound": True,
        "capability_name": "PP49 HRC CF depth-band sweep (HARD_FAIL bound)",
        "proven_bound": (
            "PP49 HRC cf depth-band sweep HARD_FAIL (proven ceiling on depth-"
            "band sweep configuration)"
        ),
    },
    "T3/EXP_pp49_hrc_cross_n_d4_d6_d8_v1_n16384": {
        "verdict": "HARD_FAIL",
        "is_bound": True,
        "capability_name": "PP49 HRC cross-n d4_d6_d8 (HARD_FAIL bound)",
        "proven_bound": (
            "PP49 HRC cross-n at d=4,6,8 HARD_FAIL (proven ceiling on cross-n + "
            "shallow-depth combination)"
        ),
    },
    "T3/EXP_pp49_hrc_deeper_d_d10_d12_d14_v1_n8192": {
        "verdict": "MIDDLE_BAND",
        "is_bound": True,
        "capability_name": "PP49 HRC deeper-d d10_d12_d14 (MIDDLE_BAND bound)",
        "proven_bound": (
            "PP49 HRC deeper-d at d=10,12,14 MIDDLE_BAND (discriminating-but-"
            "not-strong at deeper depths; Skunkworks per-atom: capability-claim "
            "not ablation-knob)"
        ),
    },
    "T3/EXP_pp58_scs_tau_sweep_d8_tau010_v1_n8192": {
        "verdict": "HARD_FAIL",
        "is_bound": True,
        "capability_name": "PP58 SCS tau010 at d8 (HARD_FAIL bound)",
        "proven_bound": "PP58 SCS tau-sweep at d8 tau=0.10 HARD_FAIL",
    },
    "T3/EXP_pp58_scs_tau_sweep_d8_tau020_v1_n8192": {
        "verdict": "HARD_FAIL",
        "is_bound": True,
        "capability_name": "PP58 SCS tau020 at d8 (HARD_FAIL bound)",
        "proven_bound": "PP58 SCS tau-sweep at d8 tau=0.20 HARD_FAIL",
    },
    "T3/EXP_pp58_scs_tau_sweep_d8_tau030_v1_n8192": {
        "verdict": "HARD_FAIL",
        "is_bound": True,
        "capability_name": "PP58 SCS tau030 at d8 (HARD_FAIL bound)",
        "proven_bound": "PP58 SCS tau-sweep at d8 tau=0.30 HARD_FAIL",
    },
    "T3/EXP_pp58_scs_tau_sweep_d8_tau050_v1_n8192": {
        "verdict": "MIDDLE_BAND",
        "is_bound": True,
        "capability_name": "PP58 SCS tau050 at d8 (MIDDLE_BAND bound)",
        "proven_bound": "PP58 SCS tau-sweep at d8 tau=0.50 MIDDLE_BAND",
    },
    "T3/EXP_substrate_cfrpe_sparse_superadditive_bigram_v1_n512_gpu": {
        "verdict": "MIDDLE_BAND",
        "is_bound": True,
        "capability_name": "Substrate cf-RPE sparse superadditive bigram (bound)",
        "proven_bound": "cf-RPE sparse superadditive bigram MIDDLE_BAND",
    },
    "T3/EXP_substrate_cfrpe_stdp_heterogeneous_superadditive_bigram_v1_n512": {
        "verdict": "PASS",
        "is_bound": False,
        "capability_name": "Substrate cf-RPE STDP heterogeneous superadditive bigram",
        "proven_bound": "cf-RPE STDP heterogeneous superadditive bigram at cert-grade",
    },
    "T3/EXP_substrate_continual_learning_30day_realistic_stream_v1": {
        "verdict": "PASS",
        "is_bound": False,
        "capability_name": "Substrate continual learning 30-day realistic stream",
        "proven_bound": (
            "Continual learning 30-day realistic stream at cert-grade"
        ),
    },
    "T3/EXP_substrate_continual_learning_empirical_10e9x_v1": {
        "verdict": "MIDDLE_BAND",
        "is_bound": True,
        "capability_name": "Substrate continual learning 10e9x empirical (bound)",
        "proven_bound": "Continual learning empirical 10e9x MIDDLE_BAND",
    },
    "T3/EXP_substrate_long_conversation_10k_exchanges_v1": {
        "verdict": "PASS",
        "is_bound": False,
        "capability_name": "Substrate long conversation 10k exchanges",
        "proven_bound": "Long conversation 10k exchanges at cert-grade",
    },
    "T3/EXP_substrate_long_conversation_scale_1000_exchanges_v1": {
        "verdict": "PASS",
        "is_bound": False,
        "capability_name": "Substrate long conversation scale 1000 exchanges",
        "proven_bound": "Long conversation scale 1000 exchanges at cert-grade",
    },
    "T3/EXP_substrate_task_complexity_sweep_v1_512_8192_gpu": {
        "verdict": "PASS",
        "is_bound": False,
        "capability_name": "Substrate task complexity sweep",
        "proven_bound": "Task complexity sweep 512-8192 at cert-grade",
    },
}


def build_patches():
    patches = {}
    canonical_qid = f"math::{PP48_NKT_CLUSTER_REF['canonical_atom_id']}"

    # PP48_NKT cluster extensions (scale_points)
    for atom_id, info in PP48_NKT_EXTENSIONS.items():
        patches[atom_id] = {
            "capint_integrated": True,
            "capint_cluster_id": PP48_NKT_CLUSTER_REF["cluster_id"],
            "capint_cluster_member_role": "scale_point",
            "capint_shared_benchmark": PP48_NKT_CLUSTER_REF["shared_benchmark"],
            "capint_capability_name": PP48_NKT_CLUSTER_REF["capability_name"],
            "capint_verdict": info["verdict"],
            "capint_is_bound": False,  # cluster uniform-PASS
            "capint_proven_bound": (
                f"PP48 NKT scale-point at {info['tag_short']} (extension to "
                f"the existing 11-member 2-axis cluster; depth+cross_n axes)"
            ),
            "capint_current_best_citation": canonical_qid,
            "capint_primary_domain": "cognitive_capacity",
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
            "capint_primary_domain": "cognitive_capacity",
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
                print(f"  {cid}: {len(m)} canonicals")
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
        return True, f"PASS ({len(atoms)} atoms; round-trip clean)"
    except Exception as e:
        return False, f"FAIL: {e}"


def main():
    print("=" * 80)
    print("CAP-INT TRACK-A APPLY: UNCLASSIFIED -> cognitive_capacity")
    print("=" * 80)
    print()

    patches = build_patches()
    print(f"Patches: {len(patches)} atoms")
    print(f"  PP48_NKT cluster extensions: {len(PP48_NKT_EXTENSIONS)}")
    print(f"  Singletons: {len(SINGLETONS)}")
    print()

    total = 0
    for partition_path in ROOT.glob("*/atoms.jsonl"):
        n, lines = patch_partition(partition_path, patches)
        if n:
            total += n
            print(f"  {partition_path.parent.name}: {n} atoms / {lines} lines")
    print()
    print(f"TOTAL: {total}")
    print()

    ok, msg = store_load_verify()
    print(f"Store-LOAD: {msg}")
    if not ok:
        return

    if not self_assert_one_canonical_per_cluster():
        print("ABORT")
        return

    print()
    print("APPLY COMPLETE. Route to Skunkworks for integration-check v1.1.")


if __name__ == "__main__":
    main()
