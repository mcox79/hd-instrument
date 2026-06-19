#!/usr/bin/env python3
"""Cap-int Track-A apply: knowledge_graph domain seed (CERT 580; first KG cap).

The ConceptNet KG inference-transfer atom (CERT_CHAIN_GRADE; landed 2026-06-19)
becomes the FIRST knowledge_graph cert-grade capability in cap-int Track-A.
Domain was 0 cert-atoms in Piece-1 enumerator; this seeds it.

Atom: T3/EXP_conceptnet_kg_inference_transfer_cpu_v1
Verdict: HARD_FAIL inference-transfer (primary) + HARD_PASS fact-fabrication-bound (sub-finding in same record)
Cert-grade: CERT_CHAIN_GRADE (Skunkworks landed-VET PASS)

Per Skunkworks: "cap-int can later mint TWO capability-views (completion-bound +
refuse-gate generalization) from this single record."
For now: ONE capability (the primary HARD_FAIL is_bound=True), with the sub-finding
recorded in proven_bound for transparency. Future A/B-iterate / refinement could
split into 2 views.

Pattern: singleton; verdict-faithful; cluster_id=None; Self-assert + Store-LOAD
verify post.
"""

import json
import os
from pathlib import Path

ROOT = Path("data/substrate_index")

KG_SEED_ATOM_ID = "T3/EXP_conceptnet_kg_inference_transfer_cpu_v1"

KG_SEED_PATCH = {
    "capint_integrated": True,
    "capint_cluster_id": None,
    "capint_cluster_member_role": "singleton",
    "capint_shared_benchmark": None,
    "capint_capability_name": (
        "ConceptNet KG inference-transfer (coverage-completion bound + "
        "refuse-gate generalization)"
    ),
    "capint_verdict": "HARD_FAIL",
    "capint_is_bound": True,  # HARD_FAIL = bound-verdict (cert-faithful)
    "capint_proven_bound": (
        "ConceptNet KG inference-transfer: substrate cf-RPE multi-hop "
        "completion HARD_FAIL vs frozen-bge single-hop on firewalled held-out "
        "(substrate Hits@10=0.4506 < bge 0.5021; AUROC 0.733 < 0.832; nontrivial_"
        "lift=-0.720). Coverage-completion-not-reasoning REPLICATES on a "
        "SECOND corpus (WordNet Item-1/M1/HYP-5 -> ConceptNet; multi-corpus "
        "robust). SUB-FINDING (same record, HARD_PASS): refuse-gate "
        "fact-fabrication-bound AUROC=0.812 (generalizes the A2-v6 refuse-"
        "gate to KG-completion). Cert-architecture + refuse-gate is the "
        "substrate's knowledge_graph value, NOT positive completion."
    ),
    "capint_current_best_citation": f"math::{KG_SEED_ATOM_ID}",
    "capint_primary_domain": "knowledge_graph",
}


def patch_partition(partition_path, target_id, patch):
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
            if aid == target_id:
                md = atom.get("metadata") or {}
                for k, v in patch.items():
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
        problems = []
        for cid, members in cluster_canonicals.items():
            if len(members) != 1:
                problems.append((cid, members))
        if problems:
            print("SELF-ASSERT FAIL:")
            for cid, members in problems:
                print(f"  {cid}: {len(members)} canonicals: {members}")
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
    print("CAP-INT TRACK-A APPLY: knowledge_graph SEED (CERT 580; first KG cap)")
    print("=" * 80)
    print()
    print(f"Target atom: {KG_SEED_ATOM_ID}")
    print()

    total = 0
    for partition_path in ROOT.glob("*/atoms.jsonl"):
        n_patched, n_lines = patch_partition(partition_path, KG_SEED_ATOM_ID, KG_SEED_PATCH)
        if n_patched:
            total += n_patched
            print(f"  {partition_path.parent.name}/atoms.jsonl: {n_patched} atom / {n_lines} lines")
    print()
    print(f"TOTAL: {total}")
    print()

    ok, msg = store_load_verify()
    print(f"Store-LOAD verify: {msg}")
    if not ok:
        return

    if not self_assert_one_canonical_per_cluster():
        print("ABORT: self-assert FAIL")
        return

    print()
    print("APPLY + Store-LOAD verify + self-assert COMPLETE.")
    print("Route to Skunkworks for integration-check (first knowledge_graph capability).")


if __name__ == "__main__":
    main()
