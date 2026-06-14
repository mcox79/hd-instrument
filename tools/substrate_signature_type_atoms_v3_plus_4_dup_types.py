"""Signature type atoms v3 + type 4 remaining substantive UNDECIDABLE dups.

PHASE 3 of pivot. Combines:
  (A) Final 15th signature type atom: dynamical_system_type -> 15/15 gated ABSTRACTION
  (B) Type 4 remaining substantive UNDECIDABLE duplicates:
        cosine_similarity (T1/T3), default_mode_network (T1/T1),
        quantum_entanglement (T1/T1), answer_consistency_weak_labels (T3/T2)

The remaining 6 UNDECIDABLE are noise (4 routing-note files + 2 methodology
rules mis-registered as duplicate atoms) -- separate data hygiene task.

NO LLM. NO bge.
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier, RelationType


# (A) Final 15th type atom
NEW_TYPE_ATOMS = [
    {
        "id": "T1/dynamical_system_type",
        "name": "Dynamical system (type)",
        "aliases": ("evolution_system", "flow_or_map_on_state_space"),
        "description": (
            "Tuple (X, T, phi) where X is a state space (set/manifold), T a time "
            "monoid (R, Z, N), and phi: T x X -> X a flow/evolution map satisfying "
            "phi(0,x) = x and phi(t+s,x) = phi(t,phi(s,x)). Type underlying "
            "trajectories, attractors, ergodic_theorem, Lyapunov exponents, "
            "Poincare recurrence, edge-of-chaos."
        ),
        "depends_on": ("math::T1/measure_preserving_map",),
        "serves_capability": ("cap_type_dynamical_system",),
    },
]


# (B) Type 4 remaining substantive duplicate operator groups
TYPING_SPECS = {
    "cosine_similarity": {
        "domain": "vector_similarity",
        "operation_type": "normalized_inner_product",
        "signature_input_type": "two_vectors_same_dim",
        "signature_output_type": "scalar_in_minus1_to_plus1",
        "complexity_class": "O(d)_d_dim",
    },
    "default_mode_network": {
        "domain": "neuroscience_network",
        "operation_type": "task_negative_brain_network_baseline",
        "signature_input_type": "fmri_or_functional_connectivity_data",
        "signature_output_type": "DMN_node_set_with_connectivity_weights",
        "complexity_class": "depends_on_atlas_resolution",
    },
    "quantum_entanglement": {
        "domain": "quantum_mechanics",
        "operation_type": "nonseparable_joint_state",
        "signature_input_type": "composite_quantum_state",
        "signature_output_type": "entanglement_measure_concurrence_or_negativity",
        "complexity_class": "O(d_A * d_B)_for_bipartite",
    },
    "answer_consistency_weak_labels": {
        "domain": "weak_supervision",
        "operation_type": "consistency_check_across_label_sources",
        "signature_input_type": "weak_label_set_per_example",
        "signature_output_type": "consistency_score_or_aggregated_label",
        "complexity_class": "O(n*k)_n_examples_k_sources",
    },
}


def main():
    ps = PartitionedStore(Path("data/substrate_index"))
    pre_atoms = len(ps.all_atoms())
    pre_rels = sum(1 for _ in ps.iter_all_relations())
    print(f"pre-ingest: {pre_atoms} atoms, {pre_rels} relations\n")

    # (A) Ship final type atom
    print("=== (A) FINAL TYPE ATOM ===")
    created = 0
    for spec in NEW_TYPE_ATOMS:
        qid = f"math::{spec['id']}"
        if ps.has_atom(qid):
            print(f"  SKIP (exists): {qid}")
            continue
        try:
            metadata = {
                "operation_type": "signature_type_atom",
                "is_type_atom": True,
                "type_graph_terminator": True,
                "science_algebra_category": "foundations::type_atom",
                "is_axiom": False,
                "content_type": "FORMAL_SYSTEMS",
                "substrate_load_bearing": True,
                "batch_origin": "signature_type_atoms_v3",
                "distillation_class": "B_structure_adding",
                "rule_link": "20th_rule_3mode_distillation;21st_rule_type_graph_terminates_in_atoms",
            }
            atom = Atom(
                id=spec["id"], name=spec["name"], corpus=Corpus.MATH,
                tier=Tier.TIER_1_FOUNDATIONAL, description=spec["description"],
                kind=AtomKind.PRIMITIVE, aliases=spec["aliases"],
                metadata=metadata, serves_capability=spec["serves_capability"],
            )
            ps.add_atom(atom, source="signature_type_atoms_v3",
                        note="15/15 gated ABSTRACTION; type-graph terminator")
            print(f"  CREATED: {qid}")
            created += 1
        except Exception as e:
            print(f"  FAIL: {qid} :: {str(e)[:140]}")

        for tgt in spec["depends_on"]:
            if ps.has_atom(tgt):
                try:
                    ps.add_relation(f"math::{spec['id']}", RelationType.DEPENDS_ON, tgt,
                                    source="signature_type_atoms_v3",
                                    note="type composition v3")
                    print(f"  EDGE: math::{spec['id']} -> {tgt}")
                except Exception:
                    pass

    # (B) Type 4 remaining UNDECIDABLE substantive dups
    print("\n=== (B) TYPE 4 SUBSTANTIVE UNDECIDABLE DUPS ===")
    from collections import defaultdict
    by_short = defaultdict(list)
    for a in ps.all_atoms():
        short = str(a.id).split("::")[-1].split("/")[-1].strip().lower()
        by_short[short].append(a)

    typed_count = 0
    atoms_updated = 0
    for short_id, sig_dict in TYPING_SPECS.items():
        members = by_short.get(short_id, [])
        if len(members) < 2:
            print(f"  SKIP_NO_DUP: {short_id} (found {len(members)})")
            continue
        for a in members:
            try:
                existing_alg = dict(a.algebra) if a.algebra else {}
                merged = {**existing_alg, **sig_dict}
                meta = dict(a.metadata) if a.metadata else {}
                meta["typed_by"] = "signature_type_atoms_v3"
                meta["distillation_class"] = "A_atom_removing_unblock"
                updated = Atom(
                    id=a.id, name=a.name, corpus=a.corpus, tier=a.tier,
                    description=a.description, kind=a.kind, aliases=a.aliases,
                    metadata=meta, serves_capability=a.serves_capability,
                    algebra=merged,
                )
                ps.add_atom(updated, source="signature_type_atoms_v3",
                            note=f"backfill algebra for {short_id} Class A unblock")
                atoms_updated += 1
            except Exception as e:
                print(f"  UPDATE_FAIL {a.id}: {str(e)[:120]}")
        typed_count += 1
        print(f"  TYPED: {short_id} ({len(members)} atoms)")

    post_atoms = len(ps.all_atoms())
    post_rels = sum(1 for _ in ps.iter_all_relations())
    print(f"\n=== SUMMARY ===")
    print(f"atoms: {pre_atoms} -> {post_atoms} (+{post_atoms - pre_atoms})")
    print(f"relations: {pre_rels} -> {post_rels} (+{post_rels - pre_rels})")
    print(f"  (A) new type atom created: {created} (-> 15/15 gated ABSTRACTION)")
    print(f"  (B) dup groups typed: {typed_count} / 4")
    print(f"  (B) atoms updated: {atoms_updated}")


if __name__ == "__main__":
    main()
