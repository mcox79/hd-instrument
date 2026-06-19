#!/usr/bin/env python3
"""Force-fix the 2 decomposition_resonator atoms per Skunkworks INTEGRATION-FAIL
ruling 2026-06-19.

The earlier Track-A apply mis-classified them as cluster scale_points (I3/I4
FAIL). Ruling: revert to 2 singletons with correct verdict-faithful semantics.

This is a targeted re-apply that OVERRIDES the existing capint_* fields (the
idempotency check in the main tool was correctly skipping them since they were
"already integrated" -- but their classification was wrong).

Per Skunkworks:
- decomposition_resonator_alpha05: singleton, PASS, is_bound=False
- decomposition_resonator_cpu: singleton, MIDDLE_BAND, is_bound=True

Pattern: raw-JSONL safe (no enum field; metadata override only) + Store-LOAD
verify per inst-240's rule.
"""

import json
import os
from pathlib import Path

ROOT = Path("data/substrate_index")

# Identify atoms by substring + override their capint_* metadata
FIXES = {
    "decomposition_resonator_alpha05": {
        # The PASS atom; happens to have "cpu" in name too but is the alpha05
        # variant (verdict=PASS confirmed in enumerator)
        "match_substrings_all": ["decomposition_resonator", "alpha05"],
        "match_substrings_excludes": [],  # match even if name also has cpu
        "capint_integrated": True,
        "capint_cluster_id": None,
        "capint_cluster_member_role": "singleton",
        "capint_shared_benchmark": None,
        "capint_capability_name": "Decomposition via resonator (alpha05)",
        "capint_verdict": "PASS",
        "capint_is_bound": False,
        "capint_proven_bound": (
            "Decomposition via resonator at cert-grade (alpha=0.05 "
            "hyperparameter configuration)"
        ),
    },
    "decomposition_resonator_cpu": {
        # The MIDDLE_BAND atom; has cpu only (no alpha05)
        "match_substrings_all": ["decomposition_resonator", "cpu"],
        "match_substrings_excludes": ["alpha05"],
        "capint_integrated": True,
        "capint_cluster_id": None,
        "capint_cluster_member_role": "singleton",
        "capint_shared_benchmark": None,
        "capint_capability_name": (
            "Decomposition via resonator (cpu execution-platform)"
        ),
        "capint_verdict": "MIDDLE_BAND",
        "capint_is_bound": True,
        "capint_proven_bound": (
            "Decomposition via resonator on cpu execution-platform "
            "MIDDLE_BAND (discriminating-but-not-strong; the cpu-platform "
            "bound, distinct from the alpha05 PASS variant)"
        ),
    },
}


def matches(atom_id, fix):
    aid = atom_id.lower()
    if not all(s in aid for s in fix["match_substrings_all"]):
        return False
    if any(s in aid for s in fix.get("match_substrings_excludes", [])):
        return False
    return True


def apply_fix(atom_dict, fix, qid):
    md = atom_dict.get("metadata") or {}
    # Override capint_* fields with the fix
    capint_keys = [k for k in fix if k.startswith("capint_")]
    for k in capint_keys:
        md[k] = fix[k]
    # Set current_best_citation to self (singleton pattern)
    md["capint_current_best_citation"] = qid
    atom_dict["metadata"] = md
    # Defense: remove any top-level capint_*
    for k in list(atom_dict.keys()):
        if k.startswith("capint_") and k != "metadata":
            del atom_dict[k]
    return atom_dict


def rewrite_partition(partition_path):
    tmp = partition_path.with_suffix(".jsonl.tmp")
    n_patched = 0
    n_lines = 0
    fixes_applied = []
    corpus = partition_path.parent.name
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
            aid = atom.get("id") or ""
            for fix_name, fix in FIXES.items():
                if matches(aid, fix):
                    qid = f"{corpus}::{aid}"
                    atom = apply_fix(atom, fix, qid)
                    n_patched += 1
                    fixes_applied.append((fix_name, aid))
                    break
            dst.write(json.dumps(atom, ensure_ascii=False) + "\n")
    os.replace(tmp, partition_path)
    return n_patched, n_lines, fixes_applied


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
    print("=" * 80)
    print("FIX: decomposition_resonator REVERT to 2 singletons")
    print("=" * 80)
    print()

    total_patched = 0
    all_fixes = []
    for partition_path in ROOT.glob("*/atoms.jsonl"):
        n_patched, n_lines, fixes = rewrite_partition(partition_path)
        if n_patched:
            total_patched += n_patched
            all_fixes.extend(fixes)
            print(f"  {partition_path.parent.name}/atoms.jsonl: "
                  f"{n_patched} atoms fixed / {n_lines} total lines")

    print()
    print(f"TOTAL fixed: {total_patched}")
    print()
    print("Fixes applied:")
    for fix_name, aid in all_fixes:
        print(f"  {fix_name:50s} -> {aid}")
    print()

    print("=" * 80)
    print("STORE-LOAD verify (inst-240's rule + Exp-Dev pattern)")
    print("=" * 80)
    ok, msg = store_load_verify()
    print(f"  {msg}")
    if not ok:
        print("FAILED Store-LOAD gate.")
        return

    # Spot-check: confirm both have capint_cluster_id=None + role=singleton
    print()
    print("Spot-check:")
    for partition_path in ROOT.glob("*/atoms.jsonl"):
        with partition_path.open(encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    a = json.loads(line)
                except json.JSONDecodeError:
                    continue
                aid = a.get("id") or ""
                if "decomposition_resonator" not in aid.lower():
                    continue
                md = a.get("metadata") or {}
                print(f"  {aid}")
                print(f"    cluster_id: {md.get('capint_cluster_id')}")
                print(f"    role: {md.get('capint_cluster_member_role')}")
                print(f"    verdict: {md.get('capint_verdict')}")
                print(f"    is_bound: {md.get('capint_is_bound')}")
    print()
    print("FIX COMPLETE. Route to Skunkworks for integration-check re-run.")


if __name__ == "__main__":
    main()
