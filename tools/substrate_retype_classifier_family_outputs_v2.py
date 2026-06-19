"""Retype classifier-family operators to atomized supertypes (v2 of retype).

Per Exp-Dev V2 flip-confirmed note: F2 lifted 3.1% -> 18.8% via HMM +
sequence_decoder retyping. Exp-Dev surfaced that classifier family has
two SUB-families which already have atomized supertypes:
  count_nb -> probability_vector (already atomized)
  discriminative_perceptron / structured_perceptron -> weight_vector (already atomized)

This v2 retypes them. Result will be 2 single-output classifier families
rather than 1 heterogeneous DISTINCT group. Each yields a candidate
SHARED_ABSTRACTION on next V2 re-run.

NO LLM. NO bge. Pure algebra signature_output_type re-binding.
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom


# operator short_id -> new signature_output_type (atomized supertype)
RETYPE_SPECS = {
    # Generative-probability classifier family -> probability_vector
    "count_nb":                        "probability_vector",
    "naive_bayes":                     "probability_vector",
    "naive_bayes_classifier":          "probability_vector",

    # Discriminative-weight classifier family -> weight_vector
    "discriminative_perceptron":       "weight_vector",
    "structured_perceptron_collins":   "weight_vector",
    "collins_structured_perceptron":   "weight_vector",
    "perceptron_update":               "weight_vector",
}


def main():
    ps = PartitionedStore(Path("data/substrate_index"))
    atoms = ps.all_atoms()

    by_short = {}
    for a in atoms:
        short = str(a.id).split("/")[-1].lower()
        by_short.setdefault(short, []).append(a)

    atoms_updated = 0
    skipped_no_atom = 0
    for short_id, new_out_type in RETYPE_SPECS.items():
        members = by_short.get(short_id, [])
        if not members:
            print(f"  SKIP_NO_ATOM: {short_id}")
            skipped_no_atom += 1
            continue
        for a in members:
            try:
                existing = dict(a.algebra) if a.algebra else {}
                old_out = existing.get("signature_output_type", "(none)")
                if old_out == new_out_type:
                    print(f"  ALREADY: {a.id} -> {new_out_type}")
                    continue
                existing["signature_output_type"] = new_out_type
                existing["retyped_from"] = old_out
                meta = dict(a.metadata) if a.metadata else {}
                meta["retyped_by"] = "retype_classifier_family_v2"
                meta["distillation_class"] = "A_atom_removing_unlock_via_supertype_binding"
                updated = Atom(
                    id=a.id, name=a.name, corpus=a.corpus, tier=a.tier,
                    description=a.description, kind=a.kind, aliases=a.aliases,
                    metadata=meta, serves_capability=a.serves_capability,
                    algebra=existing,
                )
                ps.add_atom(updated, source="retype_classifier_family_v2",
                            note=f"classifier family supertype binding: -> {new_out_type}")
                print(f"  RETYPED: {a.id}  ({old_out} -> {new_out_type})")
                atoms_updated += 1
            except Exception as e:
                print(f"  FAIL {a.id}: {str(e)[:120]}")

    print(f"\n=== CLASSIFIER FAMILY RETYPE v2 SUMMARY ===")
    print(f"  atoms updated: {atoms_updated}")
    print(f"  skipped (no atom): {skipped_no_atom}")
    print(f"\nNext: Exp-Dev re-runs V2; expect 2 new SHARED_ABSTRACTION:")
    print(f"  (a) generative_classifier_family via probability_vector")
    print(f"  (b) discriminative_classifier_family via weight_vector")
    print(f"F2 projection: 18.8% -> ~22-25% if both flips materialize.")


if __name__ == "__main__":
    main()
