#!/usr/bin/env python3
"""Cap-int Track-A apply: reasoning_multihop FULL domain (cluster-first pattern).

Per Skunkworks's full mapping 2026-06-19:
- 297 reasoning_multihop rows = 34 distinct capabilities.
- ONE q_a3_cross_layer_composition cluster = 264 atoms (88% of rows).
- 33 singletons (14 done in batch-1 + 19 NEW VET'd ACCEPT).
- 2 mini-cluster candidates Director-judgment: decomposition_resonator
  (PASS + cpu MIDDLE_BAND); capacity_composition (b2xb4 + full + stress).

Director-judgment on sub-clusters:
- decomposition_resonator: YES mini-cluster (2 members; PASS canonical, cpu
  MIDDLE_BAND = scale_point). They're THE SAME capability with execution-mode
  variants.
- capacity_composition: YES mini-cluster (3 members; "full" canonical;
  "b2xb4" + "stress" = scale_points). They're variants of the SAME capacity-
  composition capability.

Net post-judgment: 1 q_a3 cluster (264) + 1 crt cluster (2; batch-1) + 1
decomposition_resonator cluster (2) + 1 capacity_composition cluster (3) +
~28 singletons (33 - 5 collapsed to 2 mini-clusters + 2 cluster-canonicals
re-counted) = ~32 capabilities. ~2 fewer than Skunkworks's 34 due to my
mini-cluster judgment.

Per cap-int spec + integration-check schema-contract:
- All capint_* fields IN metadata (MUST-FIX semantics).
- Idempotent: skip atoms already capint_integrated=True (preserves batch-1).
- Store-LOAD verify post-apply (inst-240's rule; Exp-Dev's PartitionedStore
  reference pattern).
"""

import json
import os
import re
from pathlib import Path

ROOT = Path("data/substrate_index")
ENUMERATOR_OUTPUT = Path("data/capint_piece1_enumerator_v0_2026-06-19.json")


CLUSTER_DEFS = {
    "q_a3_cross_layer_composition": {
        "shared_benchmark": "cross_layer_composition",
        "capability_name": "Cross-layer compositional reasoning",
        "membership_substrings_all": ["q_a3", "cross_layer"],
        "membership_substrings_excludes": [],
        "canonical_substring_all": ["l10000", "n16384"],
        "canonical_substring_excludes": [],
        "canonical_proven_bound": (
            "Cross-layer composition exact-1.0 across layers l100..l10000+, "
            "dimensions n up to 16384 -- the full scaling curve (264 measured "
            "scale-points)"
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
        "membership_substrings_excludes": [],
        "canonical_substring_all": ["battery_v1"],
        "canonical_substring_excludes": ["fixed"],
        "canonical_proven_bound": (
            "CRT module scaling battery -- module-by-module scaling behavior"
        ),
        "scale_point_proven_bound_template": "CRT module scaling {tag}",
    },
    # decomposition_resonator REVERTED to 2 singletons per Skunkworks's
    # integration-check FAIL ruling 2026-06-19:
    # - alpha05 = hyperparameter; cpu = execution-platform (different axes,
    #   not a scale-series like q_a3 layer-depth)
    # - mixed verdicts: alpha05 PASS vs cpu MIDDLE_BAND (cpu = distinct bound)
    # - cluster fold lost the cpu MIDDLE_BAND bound-semantics (I3 FAIL) +
    #   apply bug marked both as scale_point with 0 canonical (I4 FAIL)
    # - revert: handled via SINGLETONS dict below.
    "capacity_composition": {
        "shared_benchmark": "capacity_composition",
        "capability_name": "Capacity composition",
        # Match both contiguous "capacity_composition" + "capacity_stress_composition"
        "membership_substrings_all": ["capacity", "composition"],
        "membership_substrings_excludes": ["compositional_generalization",
                                            "ceiling", "cross_layer"],
        # Canonical = the "full" variant; b2xb4 + stress = scale_points
        "canonical_substring_all": ["full"],
        "canonical_substring_excludes": ["stress", "b2xb4"],
        "canonical_proven_bound": (
            "Capacity composition (full configuration) at cert-grade"
        ),
        "scale_point_proven_bound_template": (
            "Capacity composition {tag} (configuration-variant)"
        ),
    },
}


# All 33 singletons (combining batch-1 12 + 19 NEW per Skunkworks) plus the 2
# already in mini-clusters above (decomposition_resonator + capacity_composition
# are NOT in this singleton list -- they go to mini-cluster path).
# Skunkworks gave the 19 NEW + batch-1 had the 12 + 2 (b_alpha was singleton too).
# The singleton dict here defines capability-name + verdict + is_bound for
# each. The substring is used to MATCH the atom-id.
SINGLETONS = {
    # Batch-1 (already integrated; idempotent skip via capint_integrated check)
    "b_alpha_2hop_hypernym": {
        "verdict": "MIDDLE_BAND", "is_bound": True,
        "capability_name": "ARC-1 2-hop hypernym envelope",
        "proven_bound": "ARC-1 envelope: 2-hop hypernym works at MIDDLE_BAND; 3+ hops cliff",
    },
    "b_alpha_broad_envelope": {
        "verdict": "MIDDLE_BAND", "is_bound": True,
        "capability_name": "ARC-1 broad envelope",
        "proven_bound": "ARC-1 broad envelope: 2-hop works; broad-domain MIDDLE_BAND",
    },
    "fb15k237_kg_multihop": {
        "verdict": "PASS", "is_bound": False,
        "capability_name": "FB15k-237 KG multi-hop reasoning",
        "proven_bound": "FB15k-237 KG multi-hop reasoning at cert-grade (CCC-1)",
    },
    "combo2_l5_extension": {
        "verdict": "HARD_FAIL", "is_bound": True,
        "capability_name": "Compositional 5-layer extension",
        "proven_bound": "5-layer composition extension HARD_FAIL -- proven CEILING",
    },
    "combo2_p4_l3_signed_am": {
        "verdict": "HARD_FAIL", "is_bound": True,
        "capability_name": "Composition p4_l3 signed AM",
        "proven_bound": "p4 l3 signed AM HARD_FAIL -- proven ceiling",
    },
    "composition_ceiling_k_c_alpha": {
        "verdict": "HARD_FAIL", "is_bound": True,
        "capability_name": "Composition ceiling K-C-alpha",
        "proven_bound": "Composition ceiling at K-C-alpha HARD_FAIL -- proven ceiling",
    },
    "deletion_cert_refusal_joint": {
        "verdict": "PASS", "is_bound": False,
        "capability_name": "Deletion cert + refusal-gate joint",
        "proven_bound": "Deletion cert + refusal-gate joint discipline at cert-grade",
    },
    "hypernym_heldout_falsifiable": {
        "verdict": "HONEST_NEGATIVE", "is_bound": True,
        "capability_name": "HYPERNYM held-out fact-fabrication bound",
        "proven_bound": (
            "HYPERNYM held-out falsifiable bound: substrate does NOT invent "
            "withheld HYPERNYM edges (FACT-FABRICATION bound; multi-relation-"
            "robust + depth-extended)"
        ),
    },
    "modern_hopfield_n_sweep": {
        "verdict": "PASS", "is_bound": False,
        "capability_name": "Modern Hopfield N-sweep",
        "proven_bound": "Modern Hopfield N-sweep at cert-grade",
    },
    "partof_heldout_falsifiable": {
        "verdict": "HONEST_NEGATIVE", "is_bound": True,
        "capability_name": "PART_OF held-out fact-fabrication bound",
        "proven_bound": (
            "PART_OF held-out falsifiable bound: substrate does NOT invent "
            "withheld PART_OF edges (FACT-FABRICATION bound; Item-1 anchor)"
        ),
    },
    "pb_crt_real_encoder": {
        "verdict": "PASS", "is_bound": False,
        "capability_name": "PB-CRT real encoder",
        "proven_bound": "PB-CRT with real encoder at cert-grade",
    },
    "pp48_pp46_negative_knowledge": {
        "verdict": "PASS", "is_bound": False,
        "capability_name": "PP48/PP46 negative-knowledge deletion",
        "proven_bound": "PP48/PP46 negative-knowledge deletion at cert-grade",
    },
    # Batch-2 NEW (19 per Skunkworks; minus 5 going to mini-clusters)
    "compositional_generalization_K10_to_K20": {
        "verdict": "PASS", "is_bound": False,
        "capability_name": "Compositional generalization K10 to K20",
        "proven_bound": (
            "Compositional generalization composes NOVEL chains K10->K20 at "
            "cert-grade -- the load-bearing 'reasoning IS cert-proven' anchor"
        ),
    },
    "cognitive_core_multihop_hotpotqa": {
        "verdict": "HARD_FAIL", "is_bound": True,
        "capability_name": "HotpotQA multi-hop QA cognitive-core",
        "proven_bound": (
            "HotpotQA multi-hop QA via cognitive-core HARD_FAIL -- proven "
            "ceiling on this particular eval/approach"
        ),
    },
    "substrate_sq1_resonator_generative": {
        "verdict": "HARD_FAIL", "is_bound": True,
        "capability_name": "SQ1 resonator generative",
        "proven_bound": (
            "SQ1 resonator generative HARD_FAIL -- proven ceiling on "
            "generative-resonator at this configuration"
        ),
    },
    "t3_phaseA_completeness_1level_FLAT": {
        "verdict": "HONEST_NEGATIVE", "is_bound": True,
        "capability_name": "T3 PhaseA 1-level FLAT completeness",
        "proven_bound": (
            "T3 PhaseA 1-level FLAT completeness is an HONEST_NEGATIVE bound "
            "(not a win; the discriminating-regime caught it)"
        ),
    },
    "real_encoder": {
        "verdict": "PASS", "is_bound": False,
        "capability_name": "Real encoder",
        "proven_bound": "Real encoder at cert-grade",
    },
    "novel_assembly_2": {
        "verdict": "PASS", "is_bound": False,
        "capability_name": "Novel assembly 2",
        "proven_bound": "Novel assembly 2 at cert-grade",
    },
    "b6_x_sq2_audit_preserving": {
        "verdict": "PASS", "is_bound": False,
        "capability_name": "B6 x SQ2 audit-preserving",
        "proven_bound": "B6 x SQ2 audit-preserving at cert-grade",
    },
    "modern_hopfield_p_nthreshold": {
        "verdict": "MIDDLE_BAND", "is_bound": True,
        "capability_name": "Modern Hopfield P/N threshold",
        "proven_bound": "Modern Hopfield P/N threshold MIDDLE_BAND (discriminating-but-not-strong)",
    },
    "sparse_key_composition": {
        "verdict": "MIDDLE_BAND", "is_bound": True,
        "capability_name": "Sparse key composition",
        "proven_bound": "Sparse key composition MIDDLE_BAND",
    },
    "stage_a_bio_b36": {
        "verdict": "MIDDLE_BAND", "is_bound": True,
        "capability_name": "Stage A bio B36",
        "proven_bound": "Stage A bio B36 MIDDLE_BAND",
    },
    "q_a3_l19_n_scale": {
        "verdict": "PASS", "is_bound": False,
        "capability_name": "q_a3 l19 N-scaling",
        "proven_bound": (
            "q_a3 layer 19 N-scaling at cert-grade (SEPARATE from "
            "cross_layer_composition cluster -- N-axis scaling not depth-axis)"
        ),
    },
    "t5c_hybrid": {
        "verdict": "PASS", "is_bound": False,
        "capability_name": "T5C hybrid",
        "proven_bound": "T5C hybrid at cert-grade",
    },
    "wave4_full_streaming": {
        "verdict": "PASS", "is_bound": False,
        "capability_name": "Wave4 streaming",
        "proven_bound": "Wave4 streaming at cert-grade",
    },
    "codebook_near_duplicate": {
        "verdict": "PASS", "is_bound": False,
        "capability_name": "Codebook near-duplicate",
        "proven_bound": "Codebook near-duplicate at cert-grade",
    },
    # decomposition_resonator: REVERTED to 2 singletons (Skunkworks ruling
    # 2026-06-19 INTEGRATION-FAIL fix; not a scale-series; mixed verdicts;
    # cpu MIDDLE_BAND is its own bound).
    "decomposition_resonator_alpha05": {
        "verdict": "PASS", "is_bound": False,
        "capability_name": "Decomposition via resonator (alpha05)",
        "proven_bound": (
            "Decomposition via resonator at cert-grade (alpha=0.05 "
            "hyperparameter configuration)"
        ),
    },
    "decomposition_resonator_cpu": {
        "verdict": "MIDDLE_BAND", "is_bound": True,
        "capability_name": "Decomposition via resonator (cpu execution-platform)",
        "proven_bound": (
            "Decomposition via resonator on cpu execution-platform "
            "MIDDLE_BAND (discriminating-but-not-strong; the cpu-platform "
            "bound, distinct from the alpha05 PASS variant)"
        ),
    },
}


def load_enumerator():
    with ENUMERATOR_OUTPUT.open(encoding="utf-8") as f:
        return json.load(f)


def matches_cluster(text, spec):
    if not all(s in text for s in spec["membership_substrings_all"]):
        return False
    if any(s in text for s in spec.get("membership_substrings_excludes", [])):
        return False
    return True


def matches_canonical(text, spec):
    if not all(s in text for s in spec["canonical_substring_all"]):
        return False
    if any(s in text for s in spec.get("canonical_substring_excludes", [])):
        return False
    return True


def classify_row(row):
    qid = row.get("qid", "")
    text = (qid + " " + (row.get("name") or "")).lower()
    verdict = row.get("verdict") or "PASS"

    for cluster_id, spec in CLUSTER_DEFS.items():
        if not matches_cluster(text, spec):
            continue
        is_canonical = matches_canonical(text, spec)
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
            "capint_is_bound": False,  # cluster members are PASS (by Skunkworks's per-row VET)
            "capint_proven_bound": proven_bound,
            "capint_current_best_citation": None,
        }

    for singleton_key, spec in SINGLETONS.items():
        if singleton_key.lower() in text:
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


_PARTITION_INDEX = None
_INTEGRATED_INDEX = None


def build_partition_index():
    """Single pass: map atom_id -> partition_path + integrated_status."""
    partition_index = {}
    integrated_index = {}
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
                aid = a.get("id")
                if not aid:
                    continue
                partition_index[aid] = atoms_file
                md = a.get("metadata") or {}
                integrated_index[aid] = md.get("capint_integrated") is True
    return partition_index, integrated_index


def find_partition_for_atom_id(atom_id):
    global _PARTITION_INDEX
    if _PARTITION_INDEX is None:
        _PARTITION_INDEX, _ = build_partition_index()
    return _PARTITION_INDEX.get(atom_id)


def is_already_integrated(partition_path, atom_id):
    global _INTEGRATED_INDEX
    if _INTEGRATED_INDEX is None:
        _, _INTEGRATED_INDEX = build_partition_index()
    return _INTEGRATED_INDEX.get(atom_id, False)


def apply_capint_patch(atom_dict, capint_fields):
    md = atom_dict.get("metadata") or {}
    for k, v in capint_fields.items():
        md[k] = v
    atom_dict["metadata"] = md
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
    try:
        from backend.substrate_index.partition import PartitionedStore
    except ImportError as e:
        return False, f"PartitionedStore import failed: {e}"
    try:
        ps = PartitionedStore(ROOT)
        atoms = list(ps.all_atoms())
        return True, f"PASS ({len(atoms)} atoms; Atom.from_dict round-trip clean)"
    except Exception as e:
        return False, f"FAIL: {e}"


def main():
    print("=" * 80)
    print("CAP-INT TRACK-A APPLY: reasoning_multihop FULL DOMAIN (cluster-first)")
    print("=" * 80)
    print()

    enum_data = load_enumerator()
    track_a_all = enum_data.get("track_a_full") or []
    reasoning_rows = [r for r in track_a_all
                      if r.get("primary_domain") == "reasoning_multihop"]
    print(f"Total reasoning_multihop in Track A: {len(reasoning_rows)}")

    # Classify everything
    atom_patches = {}
    unmatched = []
    cluster_counts = {}
    for row in reasoning_rows:
        capint = classify_row(row)
        if capint is None:
            unmatched.append(row)
            continue
        atom_id = row["qid"].split("::")[-1]
        atom_patches[atom_id] = capint
        key = (capint.get("capint_cluster_id") or
               f"singleton:{capint['capint_capability_name'][:40]}")
        cluster_counts.setdefault(key, []).append(atom_id)

    print(f"Classified: {len(atom_patches)} / {len(reasoning_rows)}")
    if unmatched:
        print(f"UNMATCHED ({len(unmatched)}; FIRST 10):")
        for r in unmatched[:10]:
            print(f"  {r.get('qid')} {r.get('name', '')[:80]}")
        print()

    print("Capability summary:")
    for key, atoms in sorted(cluster_counts.items(), key=lambda kv: -len(kv[1])):
        print(f"  {key:55s} {len(atoms)}")
    print(f"Distinct capabilities (clusters + singletons): {len(cluster_counts)}")
    print()

    # Idempotent: skip already-integrated atoms
    new_patches = {}
    skipped = 0
    by_partition = {}
    for atom_id, patch in atom_patches.items():
        p = find_partition_for_atom_id(atom_id)
        if p is None:
            continue
        if is_already_integrated(p, atom_id):
            skipped += 1
            continue
        new_patches[atom_id] = patch
        by_partition.setdefault(p, {})[atom_id] = patch

    print(f"Already integrated (idempotent skip): {skipped}")
    print(f"New patches to apply: {len(new_patches)}")
    print()

    if not new_patches:
        print("Nothing to do. Domain fully integrated.")
        return

    # Cluster canonicals lookup (for current_best_citation backfill)
    cluster_canonical = {}
    for atom_id, patch in atom_patches.items():
        if patch["capint_cluster_member_role"] == "canonical":
            cluster_canonical[patch["capint_cluster_id"]] = atom_id

    # Backfill citations
    for atom_id, patch in new_patches.items():
        role = patch["capint_cluster_member_role"]
        cid = patch["capint_cluster_id"]
        if role == "canonical":
            patch["capint_current_best_citation"] = atom_id
        elif role == "scale_point" and cid in cluster_canonical:
            patch["capint_current_best_citation"] = cluster_canonical[cid]
        # singleton -> already set to qid

    # Apply per-partition
    total_patched = 0
    for partition_path, ap in by_partition.items():
        print(f"Rewriting partition: {partition_path.parent.name}/atoms.jsonl "
              f"({len(ap)} atoms)...")
        n_patched, n_lines = rewrite_partition(partition_path, ap)
        print(f"  patched={n_patched}  total_lines={n_lines}")
        total_patched += n_patched
    print()
    print(f"TOTAL new patches applied: {total_patched}")
    print()

    print("=" * 80)
    print("STORE-LOAD verify (inst-240's rule + Exp-Dev pattern)")
    print("=" * 80)
    ok, msg = store_load_verify()
    print(f"  {msg}")
    if not ok:
        print("APPLY FAILED Store-LOAD gate. INVESTIGATE.")
        return

    print()
    print("APPLY + Store-LOAD verify COMPLETE.")
    print("Route to Skunkworks for integration-check on the FULL domain.")


if __name__ == "__main__":
    main()
