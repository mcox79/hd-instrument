#!/usr/bin/env python3
"""Cap-int Track-A apply: 3 small standalone domains (Skunkworks batch-VET'd ACCEPT 2026-06-19).

Adds 7 atoms / 6 capabilities across audit_methodology + ingest_pipeline + dynamics:
- 1 CLUSTER: pp49_hrc_counterfactual_depth (2 members; mixed-verdict depth-cliff
  LOWER-bound at N=4096 cf_cos; canonical=depth_8 PASS + scale_point=depth_5
  HARD_FAIL = under-depth bound). MIRROR of q_b1's depth-cliff UPPER-bound.
- 5 SINGLETONS:
  * pp49_hrc_deeper_d (HARD_FAIL; SEPARATE benchmark root_cos N=16384 -> dynamics)
  * pp58_isochoric_bbp_protocol (MIDDLE_BAND; audit_methodology)
  * substrate_codebook_collapse_monitoring_recovery (HARD_FAIL; audit_methodology)
  * a2_decisive_test_untuned_auroc (ALREADY_SEPARATES -> WIN-class is_bound=False
    per Skunkworks; ingest_pipeline)
  * hp12_v1_demo_scale_10k_facts (PASS; ingest_pipeline)

Pattern: capint_track_a_apply_math_domain_2026-06-19.py
Discipline: A5-safe metadata-only + SELF-ASSERT 1-canonical/cluster + Store-LOAD
verify + version-disambiguating canonical_substring + verdict-faithful + multi-
domain primary_domain assignment.

Benchmark verification (Skunkworks's cluster gate): depth_5 + depth_8 share
cf_cos at N=4096 (CONFIRMED via metadata scour); deeper_d is root_cos at
N=16384 (DIFFERENT benchmark) -> deeper_d STAYS singleton not cluster member.
"""

import json
import os
from pathlib import Path

ROOT = Path("data/substrate_index")

# CLUSTER: pp49_hrc_counterfactual_depth (N=4096 cf_cos; depth-cliff LOWER-bound)
CLUSTER = {
    "cluster_id": "audit_methodology::pp49_hrc_counterfactual_depth_n4096_cf_cos",
    "capability_name": "PP49 HRC counterfactual abduction at N=4096 (depth-cliff LOWER-bound)",
    "shared_benchmark": "HRC counterfactual abduction cf_cos at N=4096 (depth-window finding)",
    "canonical_substring_all": [
        "pp49_hrc_counterfactual_depth_8_v1_n4096"
    ],
    "scale_point_canonical_substring_all": [
        "pp49_hrc_counterfactual_depth_5_v1_n4096"
    ],
    "canonical_proven_bound": (
        "PP49 HRC counterfactual abduction PASS at depth=8 (the WORKING regime; "
        "all 4 HP pass; cf_cos=1.0; the depth-cliff WINDOW upper-edge anchor)"
    ),
    "scale_point_proven_bound": (
        "PP49 HRC counterfactual abduction HARD_FAIL at depth=5 (UNDER-depth bound; "
        "cf_cos=0.0275 chain incoherent at d=5; the depth-cliff WINDOW lower-edge bound; "
        "MIRROR of q_b1's UPPER-bound depth-cliff)"
    ),
}

CLUSTER_MEMBERS = {
    "T3/EXP_pp49_hrc_counterfactual_depth_8_v1_n4096": {
        "role": "canonical",
        "verdict": "PASS",
        "is_bound": False,
    },
    "T3/EXP_pp49_hrc_counterfactual_depth_5_v1_n4096": {
        "role": "scale_point",
        "verdict": "HARD_FAIL",
        "is_bound": True,
    },
}

# 5 SINGLETONS across 3 small domains
SINGLETONS = {
    "T3/EXP_pp49_hrc_deeper_d_d10_d12_d14_v1_n16384": {
        "verdict": "HARD_FAIL",
        "is_bound": True,
        "capability_name": "PP49 HRC deeper-d chain coherence bound (root_cos)",
        "proven_bound": (
            "PP49 HRC deeper-d HARD_FAIL at d=10/12/14 (root_cos < 0.2; chain "
            "completely incoherent at N=16384; SEPARATE benchmark from cf_cos N=4096 "
            "cluster -> singleton; the depth-cliff WINDOW upper-edge bound at N=16384)"
        ),
        "primary_domain": "dynamics",
    },
    "T3/EXP_pp58_isochoric_bbp_protocol_v1_n8192": {
        "verdict": "MIDDLE_BAND",
        "is_bound": True,
        "capability_name": "PP58 isochoric BBP protocol bound",
        "proven_bound": (
            "PP58 isochoric BBP protocol MIDDLE_BAND (honest-bounded; "
            "discriminating-but-not-strong)"
        ),
        "primary_domain": "audit_methodology",
    },
    "T3/EXP_substrate_codebook_collapse_monitoring_recovery_v1": {
        "verdict": "HARD_FAIL",
        "is_bound": True,
        "capability_name": "Substrate codebook collapse monitoring + recovery bound",
        "proven_bound": (
            "Substrate codebook collapse monitoring + recovery HARD_FAIL (codebook "
            "collapse is a known degeneration mode; recovery did NOT fully work; "
            "honest-negative open-problem bound)"
        ),
        "primary_domain": "audit_methodology",
    },
    "T3/EXP_a2_decisive_test_untuned_auroc_gpu_v1": {
        "verdict": "ALREADY_SEPARATES",
        "is_bound": False,
        "capability_name": "A2 decisive test untuned AUROC (already-separates win)",
        "proven_bound": (
            "A2 decisive test untuned AUROC at cert-grade ALREADY_SEPARATES "
            "(WIN-class per integration-check v1.1 vocab; baseline-separates IS "
            "the positive finding; NOT a bound)"
        ),
        "primary_domain": "ingest_pipeline",
    },
    "T3/EXP_exp_hp12_v1_demo_scale_10k_facts_v1": {
        "verdict": "PASS",
        "is_bound": False,
        "capability_name": "HP12 v1 demo-scale 10k facts (ingest-pipeline win)",
        "proven_bound": (
            "HP12 v1 demo-scale 10k facts at cert-grade PASS (ingest-pipeline "
            "scale-demo win)"
        ),
        "primary_domain": "ingest_pipeline",
    },
}


def build_patches():
    patches = {}

    # CLUSTER members (audit_methodology domain; depth-cliff LOWER-bound)
    canonical_qid = None
    for atom_id, info in CLUSTER_MEMBERS.items():
        if info["role"] == "canonical":
            canonical_qid = f"math::{atom_id}"
            break

    for atom_id, info in CLUSTER_MEMBERS.items():
        if info["role"] == "canonical":
            proven_bound = CLUSTER["canonical_proven_bound"]
            canonical_substring_all = CLUSTER["canonical_substring_all"]
        else:
            proven_bound = CLUSTER["scale_point_proven_bound"]
            canonical_substring_all = CLUSTER["scale_point_canonical_substring_all"]
        patches[atom_id] = {
            "capint_integrated": True,
            "capint_cluster_id": CLUSTER["cluster_id"],
            "capint_cluster_member_role": info["role"],
            "capint_shared_benchmark": CLUSTER["shared_benchmark"],
            "capint_capability_name": CLUSTER["capability_name"],
            "capint_verdict": info["verdict"],
            "capint_is_bound": info["is_bound"],
            "capint_proven_bound": proven_bound,
            "capint_current_best_citation": canonical_qid,
            "capint_canonical_substring_all": canonical_substring_all,
            "capint_primary_domain": "audit_methodology",
        }

    # SINGLETONS (multi-domain; per-atom primary_domain)
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
            "capint_canonical_substring_all": [atom_id],
            "capint_primary_domain": spec["primary_domain"],
        }
    return patches


def patch_partition(partition_path, patches, applied_ids):
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
            if aid in patches and aid not in applied_ids:
                md = atom.get("metadata") or {}
                for k, v in patches[aid].items():
                    md[k] = v
                atom["metadata"] = md
                for k in list(atom.keys()):
                    if k.startswith("capint_") and k != "metadata":
                        del atom[k]
                n_patched += 1
                applied_ids.add(aid)
            dst.write(json.dumps(atom, ensure_ascii=False) + "\n")
    os.replace(tmp, partition_path)
    return n_patched, n_lines


def main():
    patches = build_patches()
    print(f"Built {len(patches)} patches (1 cluster: 2 members + 5 singletons).")

    # Patches may be in multiple partitions (math + meta cross-partition).
    # Scan ALL partitions; track applied_ids to avoid double-apply.
    applied_ids = set()
    total_patched = 0
    for part_dir in sorted(ROOT.iterdir()):
        if not part_dir.is_dir():
            continue
        atoms_file = part_dir / "atoms.jsonl"
        if not atoms_file.exists():
            continue
        n_patched, n_lines = patch_partition(atoms_file, patches, applied_ids)
        if n_patched > 0:
            print(f"  Patched {n_patched}/{len(patches)} in {part_dir.name} "
                  f"({n_lines} lines scanned).")
        total_patched += n_patched

    print(f"Total patched: {total_patched}/{len(patches)}")

    if total_patched != len(patches):
        print("WARNING: not all patches applied. Missing atom IDs:")
        for pid in patches:
            if pid not in applied_ids:
                print(f"  Missing: {pid}")
        return 2

    # Self-assert: 1 canonical per cluster
    print("\n--- SELF-ASSERT: 1 canonical per cluster ---")
    from backend.substrate_index.partition import PartitionedStore
    ps = PartitionedStore(ROOT)
    cluster_canonicals = {}
    for a in ps.all_atoms():
        md = a.metadata or {}
        cid = md.get("capint_cluster_id")
        role = md.get("capint_cluster_member_role")
        if cid and role == "canonical":
            cluster_canonicals.setdefault(cid, []).append(a.id)
    problems = [(cid, m) for cid, m in cluster_canonicals.items() if len(m) != 1]
    if problems:
        print("FAIL: clusters with != 1 canonical:")
        for cid, members in problems:
            print(f"  {cid}: {members}")
        return 3
    else:
        print(f"PASS: all {len(cluster_canonicals)} cap-int clusters "
              f"have exactly 1 canonical.")

    # Store-LOAD verify
    print("\n--- Store-LOAD verify ---")
    print(f"all_atoms loadable: {len(list(ps.all_atoms()))} atoms.")

    # Show 3 domains final state
    print("\n--- 3 small domain cert cap-int integrated ---")
    for dom in ["audit_methodology", "ingest_pipeline", "dynamics"]:
        dom_atoms = [a for a in ps.all_atoms()
                     if str(getattr(a, 'kind', '?')) == 'AtomKind.EXPERIMENT_RECORD'
                     and (a.metadata or {}).get('provenance_quality') == 'CERT_CHAIN_GRADE'
                     and (a.metadata or {}).get('capint_primary_domain') == dom]
        print(f"  {dom}: {len(dom_atoms)} atoms")
        for a in dom_atoms:
            md = a.metadata or {}
            role = md.get('capint_cluster_member_role', '?')
            cap_name = (md.get('capint_capability_name') or '')[:50]
            print(f"    {a.id[:55]:55} | role={role:11} | cap={cap_name}")

    print("\nAPPLY + Store-LOAD verify + 1-canonical self-assert COMPLETE.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
