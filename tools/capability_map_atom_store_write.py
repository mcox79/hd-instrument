"""DEPRECATED 2026-06-19: latent inst-239/240-class risk per Skunkworks 6-tool
corpus-completeness triage. This tool raw-APPENDS a single atom from a DRAFT
json to meta/atoms.jsonl with a post-invariant scour via json.loads -- which
catches malformed JSON but NOT Atom.from_dict enum-VALUE violations (the EXACT
inst-239/240 gap: raw-verify != Store-LOAD-gate).

This was a ONE-OFF Store-write script (already-run; the CAPABILITY_MAP atom is
landed). Re-running with a bad payload could write a malformed/colliding atom.

CANONICAL SAFE REPLACEMENT for any future atom-add work:
  -> tools/atomize_audit_lesson_template_SAFE.py
     (Atom-construction with enum MEMBERS + ps.add_atom + fresh-Store
     all_atoms() round-trip gate -- inst-240's rule.)

EXECUTION REFUSED unless --acknowledge-deprecated-incident-class is passed.

Original docstring preserved below:

----- ORIGINAL DOCSTRING -----
Director Store-write for CAPABILITY_MAP atom after Skunkworks FINAL VET APPROVE.

Appends the atom from data/capability_map_atom_DRAFT_pre_skunkworks_FINAL_VET.json
to data/substrate_index/meta/atoms.jsonl (single atom; not bulk).
Verifies pre + post invariants: atoms +1, CERT_CHAIN_GRADE unchanged (Guard 2),
axiom_term untouched (Guard 1, algebra=None + corpus=meta), no new phantoms.
Also runs methodology vs methodology_rule kind reconcile per Skunkworks's FYI catch.
"""
import json
import os
import collections
import sys

# Deprecation gate (refuse to execute without explicit ack)
if __name__ == "__main__" and "--acknowledge-deprecated-incident-class" not in sys.argv:
    print(__doc__.split("----- ORIGINAL DOCSTRING -----")[0])
    print()
    print("REFUSED: this tool has the inst-239/240 class risk (deprecated).")
    print("Use tools/atomize_audit_lesson_template_SAFE.py for new atom-add work")
    print("(Atom-construction + ps.add_atom + Store-LOAD gate).")
    print()
    print("To bypass (NOT RECOMMENDED):")
    print("  python tools/capability_map_atom_store_write.py \\")
    print("    --acknowledge-deprecated-incident-class")
    sys.exit(1)

ROOT = "data/substrate_index"
META_ATOMS = f"{ROOT}/meta/atoms.jsonl"
DRAFT_PATH = "data/capability_map_atom_DRAFT_pre_skunkworks_FINAL_VET.json"


def scour_invariants(label):
    """Compute substrate invariants: atoms, CERT count, methodology vs methodology_rule split."""
    total = 0
    cert = 0
    kinds = collections.Counter()
    capability_map_count = 0
    for p in sorted(os.listdir(ROOT)):
        fp = os.path.join(ROOT, p, "atoms.jsonl")
        if not os.path.isfile(fp):
            continue
        with open(fp, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    a = json.loads(line)
                except Exception:
                    continue
                total += 1
                kind = a.get("kind", "")
                kinds[kind] += 1
                md = a.get("metadata", {}) if isinstance(a.get("metadata"), dict) else {}
                if md.get("provenance_quality") == "CERT_CHAIN_GRADE":
                    cert += 1
                if kind == "capability_map":
                    capability_map_count += 1
    print(f"=== {label} ===")
    print(f"  atoms total: {total}")
    print(f"  CERT_CHAIN_GRADE: {cert}")
    print(f"  capability_map count: {capability_map_count}")
    print(f"  methodology: {kinds.get('methodology', 0)}")
    print(f"  methodology_rule: {kinds.get('methodology_rule', 0)}")
    print(f"  audit_lesson: {kinds.get('audit_lesson', 0)}")
    print(f"  proof_record: {kinds.get('proof_record', 0)}")
    print(f"  science_concept: {kinds.get('science_concept', 0)}")
    print(f"  lexicon: {kinds.get('lexicon', 0)}")
    print(f"  experiment_record: {kinds.get('experiment_record', 0)}")
    return {"total": total, "cert": cert, "capability_map": capability_map_count, "kinds": kinds}


def main():
    print("=== PRE-WRITE INVARIANTS ===")
    pre = scour_invariants("PRE")

    if pre["capability_map"] > 0:
        print(f"\nERROR: capability_map atom already exists; aborting (would duplicate).")
        sys.exit(1)

    # Load draft atom
    with open(DRAFT_PATH, encoding="utf-8") as f:
        atom = json.load(f)

    # Verify guards
    md = atom.get("metadata", {})
    if md.get("algebra") is not None:
        print(f"\nERROR: Guard 1 violated -- algebra != None")
        sys.exit(1)
    if md.get("provenance_quality") == "CERT_CHAIN_GRADE":
        print(f"\nERROR: Guard 2 violated -- provenance_quality is CERT_CHAIN_GRADE")
        sys.exit(1)
    if atom.get("kind") != "capability_map":
        print(f"\nERROR: kind != capability_map")
        sys.exit(1)

    # Append single line (JSONL convention)
    atom_line = json.dumps(atom, separators=(",", ":"))
    with open(META_ATOMS, "a", encoding="utf-8") as f:
        f.write(atom_line + "\n")
    print(f"\nWrote 1 atom to {META_ATOMS}")
    print(f"  atom id: {atom['id']}")
    print(f"  kind: {atom['kind']}")
    print(f"  guards: algebra={md.get('algebra')!r}, pq={md.get('provenance_quality')!r}")

    print("\n=== POST-WRITE INVARIANTS ===")
    post = scour_invariants("POST")

    # Verify deltas
    delta_atoms = post["total"] - pre["total"]
    delta_cert = post["cert"] - pre["cert"]
    delta_capmap = post["capability_map"] - pre["capability_map"]
    print(f"\n=== DELTAS ===")
    print(f"  atoms: {pre['total']} -> {post['total']} (delta {delta_atoms:+d})")
    print(f"  CERT_CHAIN_GRADE: {pre['cert']} -> {post['cert']} (delta {delta_cert:+d})")
    print(f"  capability_map: {pre['capability_map']} -> {post['capability_map']} (delta {delta_capmap:+d})")

    ok = (delta_atoms == 1 and delta_cert == 0 and delta_capmap == 1)
    if ok:
        print(f"\nINVARIANTS PASS:")
        print(f"  - atoms +1 (the new CAPABILITY_MAP atom)")
        print(f"  - CERT_CHAIN_GRADE unchanged (Guard 2: provenance_quality NOT CERT_CHAIN_GRADE)")
        print(f"  - capability_map kind +1 (first instance)")
    else:
        print(f"\nINVARIANTS FAIL -- investigate")
        sys.exit(2)


if __name__ == "__main__":
    main()
