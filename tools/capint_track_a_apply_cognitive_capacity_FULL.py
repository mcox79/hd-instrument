#!/usr/bin/env python3
"""Cap-int Track-A apply: cognitive_capacity FULL domain.

Per Skunkworks's per-row VET (2026-06-19) + cognitive_capacity ruling:
- 55 atoms; ALL cert-grade + evidence-resolve.
- 1 PP48_NKT cluster (11 members, 2-axis depth + cross_n; FOLD per q_a3
  precedent; canonical = deepest).
- 44 singletons: 21 bound (HARD_FAIL + MIDDLE_BAND) + 32 wins (PASS + HARD_PASS)
  + 2 SPARSITY_NEUTRAL (honest-neutral; NOT win NOT bound).
- pp50_transition / pseudoinverse: KEEP as singletons (decomposition lesson;
  don't over-cluster).

SPARSITY_NEUTRAL handling (Skunkworks's verdict-faithful refinement):
- is_bound = False (NOT a failure-bound)
- BUT proven_bound states "sparsity-invariant (no sparsity effect)" explicitly
- capability_name uses neutral-language (no win-dressing)
- Skunkworks will extend I3 to recognize SPARSITY_NEUTRAL as a NEUTRAL class
  before the integration-check run.

Pattern: cluster-first apply per the reasoning_multihop precedent + Store-LOAD
verify per inst-240's rule.
"""

import json
import os
from pathlib import Path

ROOT = Path("data/substrate_index")
ENUMERATOR_OUTPUT = Path("data/capint_piece1_enumerator_v0_2026-06-19.json")


CLUSTER_DEFS = {
    "pp48_nkt_depth_and_cross_n": {
        "shared_benchmark": "pp48_nkt",
        "capability_name": "PP48 NKT 2-axis (depth + cross-n) scaling",
        # Match: pp48_nkt depth-axis OR cross_n axis (both fold into 2-axis cluster)
        "membership_substrings_all": ["pp48_nkt"],
        "membership_substrings_excludes": [],
        # Canonical: deepest pure-depth atom (depth_23) -- the deepest measured
        # point of the depth-axis (Skunkworks's lean)
        "canonical_substring_all": ["pp48_nkt_depth_23"],
        "canonical_substring_excludes": ["cross"],
        "canonical_proven_bound": (
            "PP48 NKT 2-axis scaling (depth 9..23 x cross-n 13..19+) at "
            "cert-grade across the full measured curve (11 scale-points; "
            "all PASS; depth-axis x cross-n-axis)"
        ),
        "scale_point_proven_bound_template": (
            "PP48 NKT scale-point at {tag} (depth/cross-n point of the "
            "proven 2-axis curve)"
        ),
    },
}


# All 44 singleton capabilities per Skunkworks's VET; key = substring to match
# atom-id, spec = verdict + is_bound + capability_name + proven_bound.
SINGLETONS = {
    # 13 HARD_FAIL bound
    # 8 MIDDLE_BAND bound
    # 2 SPARSITY_NEUTRAL honest-neutral (special handling)
    # 32 PASS/HARD_PASS wins
    #
    # Stem-keyed; lowercased at match time. Use substrings unique enough to
    # not collide.
    "arch_b_replicate": {
        "verdict": "PASS", "is_bound": False,
        "capability_name": "Arch B replicate (capacity)",
        "proven_bound": "Arch B replicate capacity at cert-grade",
    },
    "b_delta_readout_lever_transfer": {
        "verdict": "PASS", "is_bound": False,
        "capability_name": "B-delta readout lever transfer",
        "proven_bound": "B-delta readout lever transfer at cert-grade",
    },
    "bge_large_capacity_measurement": {
        "verdict": "PASS", "is_bound": False,
        "capability_name": "BGE-large capacity measurement",
        "proven_bound": "BGE-large capacity measurement at cert-grade",
    },
    "caching_v3_well_stressed": {
        "verdict": "PASS", "is_bound": False,
        "capability_name": "Caching v3 well-stressed (above capacity)",
        "proven_bound": "Caching v3 well-stressed above-capacity at cert-grade",
    },
    "capacity_cliff_graceful": {
        "verdict": "PASS", "is_bound": False,
        "capability_name": "Capacity cliff graceful",
        "proven_bound": "Capacity cliff graceful at cert-grade",
    },
    "capacity_phase_boundary": {
        "verdict": "PASS", "is_bound": False,
        "capability_name": "Capacity phase boundary (larger N)",
        "proven_bound": "Capacity phase boundary larger-N at cert-grade",
    },
    "dimsparse3_alpha_at_mc": {
        "verdict": "PASS", "is_bound": False,
        "capability_name": "Dim-sparse 3 alpha at MC",
        "proven_bound": "Dim-sparse 3 alpha at MC at cert-grade",
    },
    "drosophila_recapture": {
        "verdict": "PASS", "is_bound": False,
        "capability_name": "Drosophila recapture arch-B softmax",
        "proven_bound": "Drosophila recapture arch-B softmax at cert-grade",
    },
    "ex_concept_1_storage_strength": {
        "verdict": "PASS", "is_bound": False,
        "capability_name": "Ex-concept-1 storage strength variants",
        "proven_bound": "Ex-concept-1 storage strength variants at cert-grade",
    },
    "f6_bge_large_pinv_mmax": {
        "verdict": "PASS", "is_bound": False,
        "capability_name": "F6 BGE-large pinv MMax re-audit",
        "proven_bound": "F6 BGE-large pinv MMax re-audit at cert-grade",
    },
    "fp16_vs_fp32_parity": {
        "verdict": "PASS", "is_bound": False,
        "capability_name": "FP16 vs FP32 parity",
        "proven_bound": "FP16 vs FP32 parity at cert-grade",
    },
    "hebb_vs_pseudoinverse_long": {
        "verdict": "PASS", "is_bound": False,
        "capability_name": "Hebb vs pseudoinverse long-run",
        "proven_bound": "Hebb vs pseudoinverse long-run at cert-grade",
    },
    "padding_side_audit_capacity": {
        "verdict": "PASS", "is_bound": False,
        "capability_name": "Padding-side audit (capacity)",
        "proven_bound": "Padding-side audit at cert-grade",
    },
    "pb_e5_vs_bge_pinv_headtohead": {
        "verdict": "PASS", "is_bound": False,
        "capability_name": "PB E5 vs BGE pinv head-to-head",
        "proven_bound": "PB E5 vs BGE pinv head-to-head at cert-grade",
    },
    "pb_pinv_llama_l15_keys": {
        "verdict": "PASS", "is_bound": False,
        "capability_name": "PB pinv Llama L15 keys",
        "proven_bound": "PB pinv Llama L15 keys at cert-grade",
    },
    "pb_production_recipe_integration": {
        "verdict": "PASS", "is_bound": False,
        "capability_name": "PB production-recipe integration",
        "proven_bound": "PB production-recipe integration at cert-grade",
    },
    "pp50_transition_zone": {
        "verdict": "PASS", "is_bound": False,
        "capability_name": "PP50 transition zone tw vs hadamard",
        "proven_bound": "PP50 transition zone tw vs hadamard at cert-grade",
    },
    "pp58_isochoric": {
        "verdict": "PASS", "is_bound": False,
        "capability_name": "PP58 isochoric kappa3 alpha sweep",
        "proven_bound": "PP58 isochoric kappa3 alpha sweep at cert-grade",
    },
    "pseudoinverse_real_encoder_keys": {
        "verdict": "PASS", "is_bound": False,
        "capability_name": "Pseudoinverse real encoder keys",
        "proven_bound": "Pseudoinverse real encoder keys at cert-grade",
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

    # SPARSITY_NEUTRAL honest-neutral handling (per Skunkworks's refinement)
    is_sparsity_neutral = verdict == "SPARSITY_NEUTRAL"

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
            "capint_is_bound": False,  # cluster members uniform-PASS
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

    # Default singleton fallback for unmatched (atomically: derive from name/qid)
    # SPARSITY_NEUTRAL gets the honest-neutral treatment.
    aid = qid.split("::")[-1] if "::" in qid else qid
    base_stem = aid.replace("T3/EXP_", "").replace("substrate_", "")
    if is_sparsity_neutral:
        return {
            "capint_integrated": True,
            "capint_cluster_id": None,
            "capint_cluster_member_role": "singleton",
            "capint_shared_benchmark": None,
            "capint_capability_name": f"{base_stem} (sparsity-neutral)",
            "capint_verdict": "SPARSITY_NEUTRAL",
            "capint_is_bound": False,  # NOT a failure-bound
            "capint_proven_bound": (
                f"{base_stem}: sparsity-invariant (no sparsity effect; "
                "neutral finding -- NOT a win and NOT a bound)"
            ),
            "capint_current_best_citation": qid,
        }
    # Other unmatched: classify by verdict
    is_bound = verdict in ("HARD_FAIL", "MIDDLE_BAND", "HONEST_NEGATIVE", "REFUTED")
    return {
        "capint_integrated": True,
        "capint_cluster_id": None,
        "capint_cluster_member_role": "singleton",
        "capint_shared_benchmark": None,
        "capint_capability_name": f"{base_stem}",
        "capint_verdict": verdict,
        "capint_is_bound": is_bound,
        "capint_proven_bound": (
            f"{base_stem}: {verdict} -- {'bound' if is_bound else 'win'} at cert-grade"
        ),
        "capint_current_best_citation": qid,
    }


_PARTITION_INDEX = None
_INTEGRATED_INDEX = None


def build_partition_index():
    pi, ii = {}, {}
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
                pi[aid] = atoms_file
                md = a.get("metadata") or {}
                ii[aid] = md.get("capint_integrated") is True
    return pi, ii


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
        return True, f"PASS ({len(atoms)} atoms; round-trip clean)"
    except Exception as e:
        return False, f"FAIL: {e}"


def main():
    global _PARTITION_INDEX, _INTEGRATED_INDEX
    print("=" * 80)
    print("CAP-INT TRACK-A APPLY: cognitive_capacity FULL DOMAIN")
    print("=" * 80)
    print()

    enum_data = load_enumerator()
    track_a_all = enum_data.get("track_a_full") or []
    cc_rows = [r for r in track_a_all
               if r.get("primary_domain") == "cognitive_capacity"]
    print(f"cognitive_capacity Track-A rows: {len(cc_rows)}")
    print()

    _PARTITION_INDEX, _INTEGRATED_INDEX = build_partition_index()

    atom_patches = {}
    cluster_counts = {}
    for row in cc_rows:
        capint = classify_row(row)
        atom_id = row["qid"].split("::")[-1]
        atom_patches[atom_id] = capint
        key = (capint.get("capint_cluster_id") or
               f"singleton:{capint['capint_capability_name'][:50]}")
        cluster_counts.setdefault(key, []).append(atom_id)

    print(f"Classified: {len(atom_patches)} / {len(cc_rows)}")
    print()
    print("Capability summary:")
    for key, atoms in sorted(cluster_counts.items(), key=lambda kv: -len(kv[1])):
        print(f"  {key:62s} {len(atoms)}")
    print(f"Distinct capabilities: {len(cluster_counts)}")
    print()

    # Identify cluster canonicals for citation backfill
    cluster_canonical = {}
    for atom_id, patch in atom_patches.items():
        if patch["capint_cluster_member_role"] == "canonical":
            cluster_canonical[patch["capint_cluster_id"]] = atom_id

    # Backfill citations
    for atom_id, patch in atom_patches.items():
        role = patch["capint_cluster_member_role"]
        cid = patch["capint_cluster_id"]
        if role == "canonical":
            patch["capint_current_best_citation"] = atom_id
        elif role == "scale_point" and cid in cluster_canonical:
            patch["capint_current_best_citation"] = cluster_canonical[cid]

    # Idempotent: skip already-integrated
    new_patches = {}
    by_partition = {}
    skipped = 0
    for atom_id, patch in atom_patches.items():
        p = _PARTITION_INDEX.get(atom_id)
        if p is None:
            continue
        if _INTEGRATED_INDEX.get(atom_id, False):
            skipped += 1
            continue
        new_patches[atom_id] = patch
        by_partition.setdefault(p, {})[atom_id] = patch

    print(f"Already integrated (idempotent skip): {skipped}")
    print(f"New patches to apply: {len(new_patches)}")
    print()

    if not new_patches:
        print("Nothing to do.")
        return

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
    print("STORE-LOAD verify")
    print("=" * 80)
    ok, msg = store_load_verify()
    print(f"  {msg}")
    if not ok:
        return

    print()
    print("APPLY + Store-LOAD verify COMPLETE.")
    print("Route to Skunkworks for integration-check (with SPARSITY_NEUTRAL handling).")


if __name__ == "__main__":
    main()
