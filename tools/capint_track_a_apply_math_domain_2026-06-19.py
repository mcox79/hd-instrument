#!/usr/bin/env python3
"""Cap-int Track-A apply: math domain (Skunkworks batch-VET'd ACCEPT 2026-06-19).

Adds 8 atoms / 7 capabilities to the math domain:
- 1 CLUSTER: substrate_hierarchical_5corpus_meta_n2048_gpu (2 members; uniform-PASS;
  canonical=v1 + scale_point=v2; version-disambiguating canonical_substring per pp52 lesson)
- 6 SINGLETONS (2 PASS + 2 MIDDLE_BAND + 2 HARD_FAIL; verdict-faithful is_bound)

Pattern reference: capint_track_a_apply_unclassified_reasoning_multihop_2026-06-19.py
Discipline: A5-safe (metadata-only) + self-assert 1-canonical/cluster post-write +
Store-LOAD verify + version-disambiguating canonical_substring + verdict-faithful.

Skunkworks's batch-VET note: skunkworks_to_research_domain_VET_batch_NLP_3small_math_2026-06-19.md
"""

import json
import os
from pathlib import Path

ROOT = Path("data/substrate_index")

# Cluster: substrate_hierarchical_5corpus_meta_n2048_gpu (uniform-PASS; 2 members)
CLUSTER = {
    "cluster_id": "math::substrate_hierarchical_5corpus_meta_n2048_gpu",
    "capability_name": "Substrate hierarchical 5-corpus meta-aggregation at n2048 GPU",
    "shared_benchmark": "5-corpus meta-aggregation at n2048 GPU (hierarchical)",
    # version-disambiguating canonical_substring (NOT ['v1'] catch-all per pp52 lesson)
    "canonical_substring_all": [
        "substrate_hierarchical_5corpus_meta_v1_n2048_gpu"
    ],
    "scale_point_canonical_substring_all": [
        "substrate_hierarchical_5corpus_meta_v2_n2048_gpu"
    ],
    "canonical_proven_bound": (
        "Substrate hierarchical 5-corpus meta-aggregation at cert-grade PASS "
        "(n2048 GPU; the canonical config)"
    ),
    "scale_point_proven_bound": (
        "Substrate hierarchical 5-corpus meta-aggregation REPLICATION at cert-grade PASS "
        "(n2048 GPU; v2 replication confirms v1 canonical)"
    ),
}

CLUSTER_MEMBERS = {
    "T3/EXP_substrate_hierarchical_5corpus_meta_v1_n2048_gpu": {
        "role": "canonical",
        "verdict": "PASS",
        "is_bound": False,
    },
    "T3/EXP_substrate_hierarchical_5corpus_meta_v2_n2048_gpu": {
        "role": "scale_point",
        "verdict": "PASS",
        "is_bound": False,
    },
}

# 6 singletons (verdict-faithful is_bound per integration-check v1.1 vocab)
# BOUND verdicts (HARD_FAIL + MIDDLE_BAND -> is_bound=True)
# WIN verdicts (PASS -> is_bound=False)
SINGLETONS = {
    "T3/EXP_active_gating_8a_break_even_v1_measured": {
        "verdict": "HARD_FAIL",
        "is_bound": True,
        "capability_name": "Active gating 8a break-even bound",
        "proven_bound": (
            "Active gating 8a break-even HARD_FAIL (measured; "
            "honest-negative bound; gating-overhead exceeds break-even)"
        ),
    },
    "T3/EXP_hp12_v2_crypto_2048_gmpy2_latency_v1": {
        "verdict": "MIDDLE_BAND",
        "is_bound": True,
        "capability_name": "HP12 v2 crypto 2048-bit gmpy2 latency bound",
        "proven_bound": (
            "HP12 v2 crypto 2048-bit gmpy2 latency MIDDLE_BAND "
            "(honest-bounded latency; not strong-PASS)"
        ),
    },
    "T3/EXP_kf1_paraphrase_robustness_marianmt_v1": {
        "verdict": "PASS",
        "is_bound": False,
        "capability_name": "KF1 paraphrase robustness with MarianMT",
        "proven_bound": (
            "KF1 paraphrase robustness MarianMT at cert-grade PASS"
        ),
    },
    "T3/EXP_phase_6_1_h3_distractor_relevance_cpu_v1": {
        "verdict": "HARD_FAIL",
        "is_bound": True,
        "capability_name": "Phase 6.1 H3 distractor relevance bound",
        "proven_bound": (
            "Phase 6.1 H3 distractor relevance HARD_FAIL (CPU; "
            "honest-negative; distractor distinction not robust)"
        ),
    },
    "T3/EXP_pp50_lambda1_nsweep_tw_vs_hadamard_v4_gpu": {
        "verdict": "MIDDLE_BAND",
        "is_bound": True,
        "capability_name": "PP50 lambda1 n-sweep TW-vs-Hadamard bound",
        "proven_bound": (
            "PP50 lambda1 n-sweep TW-vs-Hadamard MIDDLE_BAND "
            "(v4 GPU; honest-bounded; discriminating-but-not-strong)"
        ),
    },
    "T3/EXP_substrate_hierarchical_aggregator_scale_ext_domains5_10_20_v1_n2048": {
        "verdict": "PASS",
        "is_bound": False,
        "capability_name": "Substrate hierarchical aggregator-scale ext-domains5",
        "proven_bound": (
            "Substrate hierarchical aggregator-scale ext-domains5 at cert-grade PASS"
        ),
    },
}


def build_patches():
    patches = {}

    # CLUSTER members
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
            "capint_primary_domain": "math",
        }

    # SINGLETONS
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
            "capint_primary_domain": "math",
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


def main():
    patches = build_patches()
    print(f"Built {len(patches)} patches (1 cluster: 2 members + 6 singletons).")

    # Find the partition holding T3/EXP_* atoms (math/atoms.jsonl)
    math_partition = ROOT / "math" / "atoms.jsonl"
    if not math_partition.exists():
        print(f"ERROR: math partition not found at {math_partition}")
        return 1

    n_patched, n_lines = patch_partition(math_partition, patches)
    print(f"Patched {n_patched}/{len(patches)} atoms in {math_partition} ({n_lines} lines scanned).")

    if n_patched != len(patches):
        print("WARNING: not all patches applied. Investigating:")
        # Find which atom IDs are missing
        from backend.substrate_index.partition import PartitionedStore
        ps = PartitionedStore(ROOT)
        all_atoms = list(ps.all_atoms())
        all_ids = {a.id for a in all_atoms}
        for pid in patches:
            if pid not in all_ids:
                print(f"  Missing atom ID: {pid}")
            else:
                # In Store but not in math partition? check which partition
                for a in all_atoms:
                    if a.id == pid:
                        # find partition
                        for part_dir in ROOT.iterdir():
                            if part_dir.is_dir():
                                pfile = part_dir / "atoms.jsonl"
                                if pfile.exists():
                                    with pfile.open(encoding="utf-8") as f:
                                        for line in f:
                                            if pid in line:
                                                print(f"  {pid} -> found in {part_dir.name}")
                                                break
                        break
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
        print(f"PASS: all {len(cluster_canonicals)} cap-int clusters have exactly 1 canonical.")

    # Store-LOAD verify
    print("\n--- Store-LOAD verify ---")
    print(f"all_atoms loadable: {len(list(ps.all_atoms()))} atoms.")

    # Show math domain final state
    math_cert = [a for a in ps.all_atoms()
                 if str(getattr(a, 'kind', '?')) == 'AtomKind.EXPERIMENT_RECORD'
                 and (a.metadata or {}).get('provenance_quality') == 'CERT_CHAIN_GRADE'
                 and (a.metadata or {}).get('capint_primary_domain') == 'math']
    print(f"\n--- math cert cap-int integrated: {len(math_cert)} atoms ---")
    for a in math_cert:
        md = a.metadata or {}
        role = md.get('capint_cluster_member_role', '?')
        cap_name = (md.get('capint_capability_name') or '')[:40]
        print(f"  {a.id[:55]:55} | role={role:11} | cap={cap_name}")

    print("\nAPPLY + Store-LOAD verify + 1-canonical self-assert COMPLETE.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
