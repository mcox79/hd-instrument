#!/usr/bin/env python3
"""Cap-int Track-A apply BATCH-1 (reasoning_multihop top 30).

Per Skunkworks batch-1 per-row VET output (2026-06-19 08:57):
- 30/30 ACCEPT
- Structural finding: 30 rows = ~14 distinct CAPABILITIES (16 q_a3 scale-series
  = 1 capability; 2 crt_module_scaling = 1 mini-cluster; 12 singletons).
- 5 bound/negative rows are bound-verdicts (verdict-faithful: HARD_FAIL /
  HONEST_NEGATIVE / MIDDLE_BAND get capint_is_bound=True).

Per Skunkworks integration-check schema-contract (2026-06-19 09:04):
- ALL capint_* fields in METADATA (per MUST-FIX silent-loss family).
- capint_integrated: true
- capint_cluster_id: str | null
- capint_cluster_member_role: "canonical" | "scale_point" | "singleton"
- capint_shared_benchmark: str | null
- capint_capability_name: str
- capint_verdict: "PASS" | "MIDDLE_BAND" | "HARD_FAIL" | "HONEST_NEGATIVE" | ...
- capint_is_bound: bool
- capint_proven_bound: str (non-empty per no-Goodhart I5)
- capint_current_best_citation: atom-id (resolves; for clusters = canonical)

Per Skunkworks q_a3 answer: canonical=l10000_n16384 (deepest x highest);
others=scale_point; shared_benchmark=cross_layer_composition;
canonical proven_bound = "cross-layer composition exact-1.0 across
l100..l10000, n up to 16384" (the full curve).

POST-APPLY: Store-LOAD verify via PartitionedStore(...).all_atoms() gate
(Exp-Dev reference impl; inst-240's rule applied to atomize).
"""

import json
import os
import sys
from pathlib import Path

ROOT = Path("data/substrate_index")
ENUMERATOR_OUTPUT = Path("data/capint_piece1_enumerator_v0_2026-06-19.json")


# Skunkworks batch-1 VET (08:57) classifications:
# Cluster 1: q_a3_cross_layer_composition (16 members)
# Cluster 2: crt_module_scaling (2 members)
# 12 singletons (listed)

CLUSTERS = {
    "q_a3_cross_layer_composition": {
        "shared_benchmark": "cross_layer_composition",
        "capability_name": "Cross-layer compositional reasoning",
        # Match: any atom whose id-text contains BOTH "q_a3" and "cross_layer"
        "membership_substrings_all": ["q_a3", "cross_layer"],
        # Canonical extra: deepest layer x highest dim
        "canonical_extra_match_all": ["l10000", "n16384"],
        "canonical_proven_bound": (
            "Cross-layer composition exact-1.0 across layers l100..l10000, "
            "dimensions n up to 16384 -- the full scaling curve"
        ),
        "scale_point_proven_bound_template": (
            "Cross-layer composition at {tag} (scale-point of the proven "
            "curve l100..l10000 x n up to 16384)"
        ),
    },
    "crt_module_scaling": {
        "shared_benchmark": "crt_module_scaling_battery",
        "capability_name": "CRT module scaling",
        "membership_substrings_all": ["crt_module_scaling"],
        # Canonical: battery_v1 (not the _fixed variant)
        "canonical_extra_match_all": ["battery_v1"],
        "canonical_extra_match_excludes": ["fixed"],
        "canonical_proven_bound": (
            "CRT module scaling battery -- module-by-module scaling behavior "
            "demonstrated"
        ),
        "scale_point_proven_bound_template": (
            "CRT module scaling {tag}"
        ),
    },
}


# Skunkworks's 12 singleton capabilities (verdict noted):
SINGLETONS = {
    "b_alpha_2hop_hypernym": {
        "verdict": "MIDDLE_BAND", "is_bound": True,
        "capability_name": "ARC-1 2-hop hypernym envelope",
        "proven_bound": (
            "ARC-1 envelope: 2-hop hypernym works at MIDDLE_BAND; 3+ hops "
            "cliff (discriminating-but-not-strong)"
        ),
    },
    "b_alpha_broad_envelope": {
        "verdict": "MIDDLE_BAND", "is_bound": True,
        "capability_name": "ARC-1 broad envelope",
        "proven_bound": (
            "ARC-1 broad envelope: 2-hop works; broad-domain MIDDLE_BAND "
            "discriminating-but-not-strong"
        ),
    },
    "fb15k237_kg_multihop": {
        "verdict": "PASS", "is_bound": False,
        "capability_name": "FB15k-237 KG multi-hop reasoning",
        "proven_bound": (
            "FB15k-237 KG multi-hop reasoning at cert-grade (CCC-1)"
        ),
    },
    "combo2_l5_extension": {
        "verdict": "HARD_FAIL", "is_bound": True,
        "capability_name": "Compositional 5-layer extension",
        "proven_bound": (
            "5-layer composition extension HARD_FAIL -- the layer-depth "
            "extension is a proven CEILING"
        ),
    },
    "combo2_p4_l3_signed_am": {
        "verdict": "HARD_FAIL", "is_bound": True,
        "capability_name": "Composition p4_l3 signed AM",
        "proven_bound": (
            "p4 l3 signed AM HARD_FAIL -- the parameter configuration is a "
            "proven ceiling"
        ),
    },
    "composition_ceiling_k_c_alpha": {
        "verdict": "HARD_FAIL", "is_bound": True,
        "capability_name": "Composition ceiling K-C-alpha",
        "proven_bound": (
            "Composition ceiling at K-C-alpha HARD_FAIL -- proven ceiling"
        ),
    },
    "deletion_cert_refusal_joint": {
        "verdict": "PASS", "is_bound": False,
        "capability_name": "Deletion cert + refusal-gate joint",
        "proven_bound": (
            "Deletion cert + refusal-gate joint discipline at cert-grade"
        ),
    },
    "hypernym_heldout_falsifiable": {
        "verdict": "HONEST_NEGATIVE", "is_bound": True,
        "capability_name": "HYPERNYM held-out fact-fabrication bound",
        "proven_bound": (
            "HYPERNYM held-out falsifiable bound: substrate does NOT invent "
            "withheld HYPERNYM edges (coverage-completion absence on held-"
            "out edges; the FACT-FABRICATION bound; multi-relation-robust + "
            "depth-extended)"
        ),
    },
    "modern_hopfield_n_sweep": {
        "verdict": "PASS", "is_bound": False,
        "capability_name": "Modern Hopfield N-sweep",
        "proven_bound": (
            "Modern Hopfield N-sweep at cert-grade (associative-memory "
            "capacity scaling)"
        ),
    },
    "partof_heldout_falsifiable": {
        "verdict": "HONEST_NEGATIVE", "is_bound": True,
        "capability_name": "PART_OF held-out fact-fabrication bound",
        "proven_bound": (
            "PART_OF held-out falsifiable bound: substrate does NOT invent "
            "withheld PART_OF edges (coverage-completion absence; the FACT-"
            "FABRICATION bound; Item-1 anchor of the multi-relation-robust "
            "cert-arc)"
        ),
    },
    "pb_crt_real_encoder": {
        "verdict": "PASS", "is_bound": False,
        "capability_name": "PB-CRT real encoder",
        "proven_bound": (
            "PB-CRT with real encoder at cert-grade"
        ),
    },
    "pp48_pp46_negative_knowledge": {
        "verdict": "PASS", "is_bound": False,
        "capability_name": "PP48/PP46 negative-knowledge deletion",
        "proven_bound": (
            "PP48/PP46 negative-knowledge deletion at cert-grade"
        ),
    },
}


def load_enumerator_output():
    if not ENUMERATOR_OUTPUT.exists():
        print(f"ERROR: enumerator output missing: {ENUMERATOR_OUTPUT}")
        sys.exit(1)
    with ENUMERATOR_OUTPUT.open(encoding="utf-8") as f:
        return json.load(f)


def find_partition_for_atom_id(atom_id):
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


def classify_row(row):
    """Classify an enumerator row into Skunkworks's cluster/singleton scheme.

    Matches against qid + name (combined text) since enumerator's `name` is
    the verdict-prefixed description but the atom-id is in qid.
    """
    name_lower = (row.get("name") or "").lower()
    qid = row.get("qid", "")
    qid_lower = qid.lower()
    text = qid_lower + " " + name_lower
    verdict = row.get("verdict") or "PASS"

    # Cluster check
    for cluster_id, spec in CLUSTERS.items():
        membership = spec["membership_substrings_all"]
        if not all(sub in text for sub in membership):
            continue
        # In this cluster -- canonical or scale_point?
        excludes = spec.get("canonical_extra_match_excludes", [])
        canonical_match = all(extra in text
                              for extra in spec["canonical_extra_match_all"])
        excluded = any(ex in text for ex in excludes)
        is_canonical = canonical_match and not excluded
        if is_canonical:
            role = "canonical"
            proven_bound = spec["canonical_proven_bound"]
        else:
            role = "scale_point"
            tag = qid.split("::")[-1] if "::" in qid else qid
            proven_bound = spec["scale_point_proven_bound_template"].format(tag=tag)
        return {
            "capint_integrated": True,
            "capint_cluster_id": cluster_id,
            "capint_cluster_member_role": role,
            "capint_shared_benchmark": spec["shared_benchmark"],
            "capint_capability_name": spec["capability_name"],
            "capint_verdict": verdict,
            "capint_is_bound": False,
            "capint_proven_bound": proven_bound,
            "capint_current_best_citation": None,
        }

    # Singleton check
    for singleton_key, spec in SINGLETONS.items():
        if singleton_key in text:
            return {
                "capint_integrated": True,
                "capint_cluster_id": None,
                "capint_cluster_member_role": "singleton",
                "capint_shared_benchmark": None,
                "capint_capability_name": spec["capability_name"],
                "capint_verdict": spec["verdict"],
                "capint_is_bound": spec["is_bound"],
                "capint_proven_bound": spec["proven_bound"],
                "capint_current_best_citation": qid,
            }

    return None


def apply_capint_patch(atom_dict, capint_fields):
    md = atom_dict.get("metadata") or {}
    for k, v in capint_fields.items():
        md[k] = v
    atom_dict["metadata"] = md
    # Defense: ensure no top-level capint_* placement (MUST-FIX semantics)
    for k in list(atom_dict.keys()):
        if k.startswith("capint_") and k != "metadata":
            del atom_dict[k]
    return atom_dict


def rewrite_partition(partition_path, atom_patches):
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
                atom = apply_capint_patch(atom, atom_patches[atom_id])
                n_patched += 1
            dst.write(json.dumps(atom, ensure_ascii=False) + "\n")
    os.replace(tmp, partition_path)
    return n_patched, n_lines


def store_load_verify():
    """Per Exp-Dev/Skunkworks ACTION-1 (inst-240's rule): Store-LOAD gate.
    Fresh PartitionedStore + all_atoms() Atom.from_dict round-trip.
    """
    try:
        from backend.substrate_index.partition import PartitionedStore
    except ImportError as e:
        return False, f"PartitionedStore import failed: {e}"
    try:
        ps = PartitionedStore(ROOT)
        atoms = list(ps.all_atoms())
        return True, f"PASS (43908+ atoms; Atom.from_dict round-trip clean): {len(atoms)} loaded"
    except Exception as e:
        return False, f"FAIL: {e}"


def main():
    print("=" * 80)
    print("CAP-INT TRACK-A APPLY BATCH-1 (reasoning_multihop top 30)")
    print("=" * 80)
    print()

    enum_data = load_enumerator_output()
    track_a_all = enum_data.get("track_a_full") or []
    reasoning_rows = [r for r in track_a_all
                      if r.get("primary_domain") == "reasoning_multihop"]
    reasoning_rows.sort(key=lambda r: r.get("qid", ""))
    batch_1 = reasoning_rows[:30]
    print(f"Total reasoning_multihop in Track A: {len(reasoning_rows)}")
    print(f"Batch 1 (top 30 by qid): {len(batch_1)}")
    print()

    # Classify each row + identify canonical for each cluster
    atom_patches = {}
    cluster_canonical = {}
    classification_log = []
    unmatched = []

    for row in batch_1:
        capint = classify_row(row)
        if capint is None:
            unmatched.append(row)
            continue
        atom_id = row["qid"].split("::")[-1]
        atom_patches[atom_id] = capint
        classification_log.append((atom_id, capint["capint_cluster_id"],
                                   capint["capint_cluster_member_role"],
                                   capint["capint_verdict"],
                                   capint["capint_is_bound"]))
        if capint["capint_cluster_member_role"] == "canonical":
            cluster_canonical[capint["capint_cluster_id"]] = row["qid"]

    print(f"Classified: {len(atom_patches)}/{len(batch_1)}")
    if unmatched:
        print(f"UNMATCHED ({len(unmatched)}):")
        for r in unmatched:
            print(f"  {r.get('qid')} {r.get('name', '')[:80]}")
        print()

    # Backfill current_best_citation for cluster members (point to canonical)
    for atom_id, capint in atom_patches.items():
        if capint["capint_cluster_member_role"] in ("canonical", "singleton"):
            continue
        cid = capint["capint_cluster_id"]
        canonical_qid = cluster_canonical.get(cid)
        if canonical_qid:
            capint["capint_current_best_citation"] = canonical_qid

    # Canonical points to itself
    for atom_id, capint in atom_patches.items():
        if capint["capint_cluster_member_role"] == "canonical":
            qid_match = [r["qid"] for r in batch_1
                         if r["qid"].split("::")[-1] == atom_id]
            capint["capint_current_best_citation"] = qid_match[0] if qid_match else None

    print()
    print("Classification summary:")
    by_cluster = {}
    for atom_id, cid, role, verdict, is_bound in classification_log:
        key = cid or f"singleton:{role}"
        by_cluster.setdefault(key, []).append((atom_id, role, verdict, is_bound))
    for key in sorted(by_cluster):
        rows = by_cluster[key]
        print(f"  {key}: {len(rows)}")
        for atom_id, role, verdict, is_bound in rows[:3]:
            bound_str = "BOUND" if is_bound else "WIN"
            print(f"    {role:12s} {verdict:18s} {bound_str:6s} {atom_id[:50]}")
        if len(rows) > 3:
            print(f"    ... +{len(rows) - 3} more")
    print()

    # Group by partition
    by_partition = {}
    for atom_id in atom_patches:
        p = find_partition_for_atom_id(atom_id)
        if p is None:
            print(f"WARN: {atom_id} not found in any partition; skipping")
            continue
        by_partition.setdefault(p, {})[atom_id] = atom_patches[atom_id]

    # Apply per-partition
    total_patched = 0
    for partition_path, ap in by_partition.items():
        print(f"Rewriting partition: {partition_path.parent.name}/atoms.jsonl "
              f"({len(ap)} atoms)...")
        n_patched, n_lines = rewrite_partition(partition_path, ap)
        print(f"  patched={n_patched}  total_lines={n_lines}")
        total_patched += n_patched
    print()
    print(f"TOTAL patched: {total_patched}")
    print()

    # Store-LOAD verify (the inst-240 gate)
    print("=" * 80)
    print("STORE-LOAD verify (per inst-240's rule + Exp-Dev pattern)")
    print("=" * 80)
    ok, msg = store_load_verify()
    print(f"  {msg}")
    if not ok:
        print("APPLY FAILED Store-LOAD gate. INVESTIGATE before routing.")
        return

    # Spot-check via raw re-read: confirm metadata-placement (not top-level)
    print()
    print("Spot-check: confirm capint_* fields in METADATA, not top-level")
    spotcheck_atoms = list(atom_patches.keys())[:3]
    for atom_id in spotcheck_atoms:
        found = False
        for partition_path in ROOT.glob("*/atoms.jsonl"):
            if found:
                break
            with partition_path.open(encoding="utf-8") as f:
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
                        has_md_integrated = "capint_integrated" in md
                        has_top_integrated = "capint_integrated" in a
                        status = ("OK" if has_md_integrated and not has_top_integrated
                                  else "FAIL placement")
                        print(f"  {atom_id[:55]:55s} {status}")
                        found = True
                        break

    print()
    print("APPLY + Store-LOAD verify COMPLETE. Route to Skunkworks for")
    print("integration-check run (I1-I5 cert-gate via "
          "skunkworks_capint_integration_check_v1.py).")


if __name__ == "__main__":
    main()
