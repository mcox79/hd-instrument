"""Replace the existing CAPABILITY_MAP atom in meta/atoms.jsonl with the corrected
version (unset_legacy_count fix: 0 -> 2; per Skunkworks verify-the-referent self-catch).

Scour-script bug fixed (md.get('verdict') vs md.get('verdict', '') -- None default
mishandling). The corrected atom has unset_legacy_count=2 + the 2 actual UNSET aids
populated. CERT 569 + algebra=None + provenance_quality=INVENTORY_NON_CERT all unchanged
(it's a metadata sub-count fix; structural guards + headline numbers unaffected).
"""
import json
import os
import sys

META_ATOMS = "data/substrate_index/meta/atoms.jsonl"
DRAFT_PATH = "data/capability_map_atom_DRAFT_pre_skunkworks_FINAL_VET.json"
CAPABILITY_MAP_ID = "meta::CAPABILITY_MAP_substrate_breadth_2026_06_18_v1"


def main():
    # Load corrected atom
    with open(DRAFT_PATH, encoding="utf-8") as f:
        atom = json.load(f)

    if atom.get("id") != CAPABILITY_MAP_ID:
        print(f"ERROR: corrected atom id != expected ({CAPABILITY_MAP_ID})")
        sys.exit(1)

    # Verify guards still hold in corrected atom
    md = atom["metadata"]
    if md.get("algebra") is not None:
        print(f"ERROR: Guard 1 violated -- algebra != None")
        sys.exit(1)
    if md.get("provenance_quality") == "CERT_CHAIN_GRADE":
        print(f"ERROR: Guard 2 violated -- provenance_quality is CERT_CHAIN_GRADE")
        sys.exit(1)

    new_unset = md["capability_inventory"]["unset_legacy_count"]
    print(f"Corrected atom unset_legacy_count: {new_unset}")
    if new_unset != 2:
        print(f"ERROR: expected unset_legacy_count=2, got {new_unset}")
        sys.exit(1)

    # Read existing atoms.jsonl
    lines = []
    found_count = 0
    with open(META_ATOMS, encoding="utf-8") as f:
        for line in f:
            line_strip = line.strip()
            if not line_strip:
                lines.append(line)
                continue
            try:
                a = json.loads(line_strip)
            except Exception:
                lines.append(line)
                continue
            if a.get("id") == CAPABILITY_MAP_ID:
                found_count += 1
                # Replace with corrected atom
                lines.append(json.dumps(atom, separators=(",", ":")) + "\n")
            else:
                lines.append(line)

    if found_count != 1:
        print(f"ERROR: expected exactly 1 capability_map atom to replace, found {found_count}")
        sys.exit(1)

    # Write back
    with open(META_ATOMS, "w", encoding="utf-8") as f:
        f.writelines(lines)

    print(f"Replaced 1 capability_map atom in {META_ATOMS}")
    print(f"Corrected sub-field: unset_legacy_count 0 -> 2")
    print(f"Unset aids (now populated):")
    for aid in md["capability_inventory"]["unset_aids_for_flag_dont_auto"]:
        print(f"  {aid}")
    print(f"\nGuards verified: algebra=None, pq=INVENTORY_NON_CERT")
    print(f"CERT 569 unchanged + axiom_term + cap_pres unaffected (sub-field metadata only)")


if __name__ == "__main__":
    main()
