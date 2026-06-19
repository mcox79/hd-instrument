#!/usr/bin/env python3
"""Cap-int Track-A apply: retrieval FULL domain (38 atoms; Skunkworks VET = 38 ACCEPT).

Per Skunkworks's per-row VET 2026-06-19:
- 1 cluster: pp52_one_shot_addition (3 members; uniform-PASS = WIN; clean; no I6-flag)
- 35 singletons (verdict-faithful)
- 17 bounds (9 MIDDLE_BAND + 7 HARD_FAIL + 1 HONEST_BOUNDED) -> is_bound=True
- 21 wins (PASS) -> is_bound=False
- HONEST_BOUNDED (primitive_2_hopfield_cleanup) is a BOUND per v1.1 vocab

Patterns:
- Cluster-first + singleton apply
- Verdict-faithful per integration-check v1.1 (incl. new vocab)
- Store-LOAD verify post (Exp-Dev pattern)
- Explicit-staging per the discipline
"""

import json
import os
from pathlib import Path

ROOT = Path("data/substrate_index")
ENUMERATOR_OUTPUT = Path("data/capint_piece1_enumerator_v0_2026-06-19.json")


CLUSTER_DEFS = {
    "pp52_one_shot_addition": {
        "shared_benchmark": "pp52_one_shot_addition",
        "capability_name": "PP52 one-shot addition retrieval",
        "membership_substrings_all": ["pp52_one_shot_addition"],
        "membership_substrings_excludes": [],
        # Canonical: the "main" / non-variant; use first by atom-id sort as canonical heuristic
        "canonical_substring_all": ["v1"],
        "canonical_substring_excludes": ["hebbian_lora"],  # pp52_hebbian_lora is a separate singleton
        "canonical_proven_bound": (
            "PP52 one-shot addition retrieval at cert-grade across 3 PASS "
            "variants (uniform-PASS cluster)"
        ),
        "scale_point_proven_bound_template": (
            "PP52 one-shot addition {tag} (scale-point of the uniform-PASS cluster)"
        ),
    },
}


# Bound classification per v1.1 vocab (Skunkworks's gate):
# BOUND_VERDICTS: MIDDLE_BAND, HARD_FAIL, HONEST_BOUNDED, HONEST_NEGATIVE,
#   REFUTED, SATURATION, DISCRIMINATING_DEPTH_EXTENT
# NEUTRAL_VERDICTS: SPARSITY_NEUTRAL, NEUTRAL, INVARIANT, NO_EFFECT,
#   DEGENERATE_REGIME, NON_TEST
# WIN_VERDICTS: PASS, HARD_PASS

BOUND_VERDICTS = {
    "MIDDLE_BAND", "HARD_FAIL", "HONEST_BOUNDED", "HONEST_NEGATIVE",
    "REFUTED", "SATURATION", "DISCRIMINATING_DEPTH_EXTENT",
}
NEUTRAL_VERDICTS = {
    "SPARSITY_NEUTRAL", "NEUTRAL", "INVARIANT", "NO_EFFECT",
    "DEGENERATE_REGIME", "NON_TEST",
}


def is_bound_for_verdict(verdict):
    if verdict in BOUND_VERDICTS:
        return True
    if verdict in NEUTRAL_VERDICTS:
        return False  # neutral, NOT a bound
    return False  # PASS / HARD_PASS = win


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


def make_singleton_capability_name(qid):
    """Derive a clean capability-name from the atom-id."""
    aid = qid.split("::")[-1] if "::" in qid else qid
    stem = aid.replace("T3/EXP_", "").replace("substrate_", "")
    # Simple title-case-ish
    return stem.replace("_", " ").title()


def classify_row(row):
    qid = row.get("qid", "")
    text = (qid + " " + (row.get("name") or "")).lower()
    verdict = row.get("verdict") or "PASS"

    # Cluster check
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
            # Cluster is uniform-PASS -> is_bound=False per integration-check v1.1
            "capint_is_bound": False,
            "capint_proven_bound": proven_bound,
            "capint_current_best_citation": None,
        }

    # Singleton: verdict-faithful per v1.1 vocab
    is_bound = is_bound_for_verdict(verdict)
    cap_name = make_singleton_capability_name(qid)
    aid = qid.split("::")[-1] if "::" in qid else qid
    stem = aid.replace("T3/EXP_", "")
    if is_bound:
        proven_bound = f"{stem}: {verdict} (verdict-faithful bound)"
        cap_name = f"{cap_name} ({verdict.lower()} bound)"
    elif verdict in NEUTRAL_VERDICTS:
        proven_bound = f"{stem}: {verdict} (honest-neutral; not a win, not a bound)"
        cap_name = f"{cap_name} ({verdict.lower()} neutral)"
    else:
        proven_bound = f"{stem}: {verdict} cert-grade win"
    return {
        "capint_integrated": True,
        "capint_cluster_id": None,
        "capint_cluster_member_role": "singleton",
        "capint_shared_benchmark": None,
        "capint_capability_name": cap_name,
        "capint_verdict": verdict,
        "capint_is_bound": is_bound,
        "capint_proven_bound": proven_bound,
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
        return False, f"Import failed: {e}"
    try:
        ps = PartitionedStore(ROOT)
        atoms = list(ps.all_atoms())
        return True, f"PASS ({len(atoms)} atoms; round-trip clean)"
    except Exception as e:
        return False, f"FAIL: {e}"


def main():
    global _PARTITION_INDEX, _INTEGRATED_INDEX
    print("=" * 80)
    print("CAP-INT TRACK-A APPLY: retrieval FULL DOMAIN")
    print("=" * 80)
    print()

    enum_data = load_enumerator()
    track_a_all = enum_data.get("track_a_full") or []
    rt_rows = [r for r in track_a_all
               if r.get("primary_domain") == "retrieval"]
    print(f"retrieval Track-A rows: {len(rt_rows)}")
    print()

    _PARTITION_INDEX, _INTEGRATED_INDEX = build_partition_index()

    atom_patches = {}
    cluster_counts = {}
    for row in rt_rows:
        capint = classify_row(row)
        atom_id = row["qid"].split("::")[-1]
        atom_patches[atom_id] = capint
        key = (capint.get("capint_cluster_id") or
               f"singleton:{capint['capint_capability_name'][:50]}")
        cluster_counts.setdefault(key, []).append(atom_id)

    print(f"Classified: {len(atom_patches)} / {len(rt_rows)}")
    print()
    print("Capability summary:")
    for key, atoms in sorted(cluster_counts.items(), key=lambda kv: -len(kv[1])):
        print(f"  {key:62s} {len(atoms)}")
    print(f"Distinct capabilities: {len(cluster_counts)}")
    print()

    # Verdict-faithful counts
    bound_count = sum(1 for p in atom_patches.values() if p["capint_is_bound"])
    win_count = sum(1 for p in atom_patches.values()
                    if not p["capint_is_bound"] and
                    p["capint_verdict"] not in NEUTRAL_VERDICTS)
    print(f"Verdict-faithful: {bound_count} bounds / {win_count} wins")
    print()

    # Cluster canonicals (citation backfill)
    cluster_canonical = {}
    for atom_id, patch in atom_patches.items():
        if patch["capint_cluster_member_role"] == "canonical":
            cluster_canonical[patch["capint_cluster_id"]] = atom_id

    for atom_id, patch in atom_patches.items():
        role = patch["capint_cluster_member_role"]
        cid = patch["capint_cluster_id"]
        if role == "canonical":
            patch["capint_current_best_citation"] = atom_id
        elif role == "scale_point" and cid in cluster_canonical:
            patch["capint_current_best_citation"] = cluster_canonical[cid]

    # Idempotency
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
    print("APPLY + Store-LOAD verify COMPLETE. Route to Skunkworks for integration-check v1.1.")


if __name__ == "__main__":
    main()
