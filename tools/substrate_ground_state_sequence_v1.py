"""Ground T2/state_sequence to T1 via new T1/sequence type atom.

Per Exp-Dev WIRING VERIFIED note (2026-06-13 evening, 6/6 WIRED but
sequence_decoder_operator backward-chain dead-ends at T2/state_sequence
because state_sequence has no outgoing structural edges).

Patch in 2 steps:
  1. Author T1/sequence -- generic ordered finite collection type, parallel
     to T1/vector / T1/scalar. Fills genuine gap in the type-graph (no
     T1 sequence-type existed pre-patch).
  2. Add T2/state_sequence DEPENDS_ON T1/sequence -- closes the chain.

After this, backward-chain succeeds:
  sequence_decoder_operator -> T2/state_sequence -> T1/sequence -> [T1 axiom terminus]

NO LLM. NO bge. Pure schema authoring.
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier, RelationType


T1_SEQUENCE_SPEC = {
    "id": "T1/sequence",
    "name": "Sequence (type)",
    "aliases": ("finite_sequence", "ordered_tuple", "list_type"),
    "description": (
        "Ordered finite collection of elements indexed by 0..N-1, where each "
        "element belongs to a base type. Base type underpins all path / state-"
        "sequence / token-sequence / observation-sequence specializations. "
        "Distinct from set (unordered) and stream (infinite). Type-graph "
        "terminator at T1 mathematical first-principles level."
    ),
    "depends_on": (),  # T1 axiom-level type; terminates the chain
}


def main():
    ps = PartitionedStore(Path("data/substrate_index"))
    pre_atoms = len(ps.all_atoms())
    pre_rels = sum(1 for _ in ps.iter_all_relations())
    print(f"pre-ingest: {pre_atoms} atoms, {pre_rels} relations\n")

    # Step 1: ship T1/sequence
    qid = f"math::{T1_SEQUENCE_SPEC['id']}"
    created = False
    if ps.has_atom(qid):
        print(f"  T1/sequence ALREADY EXISTS: {qid}")
    else:
        try:
            metadata = {
                "operation_type": "signature_type_atom",
                "is_type_atom": True,
                "type_graph_terminator": True,
                "science_algebra_category": "foundations::type_atom",
                "is_axiom": False,
                "content_type": "FORMAL_SYSTEMS",
                "substrate_load_bearing": True,
                "batch_origin": "ground_state_sequence_v1",
                "distillation_class": "B_structure_adding",
                "rule_link": "21st_rule_type_graph_terminates_in_atoms;Exp_Dev_patch_state_sequence_grounding",
            }
            alg = {
                "about_topic": "sequence",
                "domain": "foundations",
                "structure": "ordered_finite_tuple",
                "role": "type",
            }
            atom = Atom(
                id=T1_SEQUENCE_SPEC["id"],
                name=T1_SEQUENCE_SPEC["name"],
                corpus=Corpus.MATH,
                tier=Tier.TIER_1_FOUNDATIONAL,
                description=T1_SEQUENCE_SPEC["description"],
                kind=AtomKind.PRIMITIVE,
                aliases=T1_SEQUENCE_SPEC["aliases"],
                metadata=metadata,
                serves_capability=("cap_type_sequence",),
                algebra=alg,
            )
            ps.add_atom(
                atom,
                source="ground_state_sequence_v1",
                note="T1 foundational sequence type; grounds state_sequence/observation_sequence/path",
            )
            print(f"  T1/sequence CREATED: {qid}")
            created = True
        except Exception as e:
            print(f"  T1/sequence FAIL: {str(e)[:140]}")
            sys.exit(1)

    # Step 2: add T2/state_sequence DEPENDS_ON T1/sequence
    state_seq_qid = "math::T2/state_sequence"
    if not ps.has_atom(state_seq_qid):
        print(f"  STATE_SEQUENCE NOT FOUND: {state_seq_qid}")
        sys.exit(2)

    target_qid = "math::T1/sequence"
    existing_edges = set()
    for r in ps.iter_all_relations():
        try:
            existing_edges.add((r.src_qualified_id, r.rel_type.name, r.tgt_qualified_id))
        except AttributeError:
            pass

    key = (state_seq_qid, "DEPENDS_ON", target_qid)
    if key in existing_edges:
        print(f"  GROUNDING EDGE ALREADY EXISTS: {state_seq_qid} -> {target_qid}")
    else:
        try:
            ps.add_relation(
                state_seq_qid, RelationType.DEPENDS_ON, target_qid,
                source="ground_state_sequence_v1",
                note="ground state_sequence to T1/sequence for prover backward-chain (Exp-Dev patch)",
            )
            print(f"  GROUNDING EDGE ADDED: {state_seq_qid} -> {target_qid}")
        except Exception as e:
            print(f"  GROUNDING EDGE FAIL: {str(e)[:120]}")
            sys.exit(3)

    # Also ground T2/observation_sequence + T2/path-like atoms while at it
    extra_groundings = [
        ("math::T2/observation_sequence", "math::T1/sequence"),
    ]
    extra_added = 0
    for src, tgt in extra_groundings:
        if not ps.has_atom(src):
            continue
        key = (src, "DEPENDS_ON", tgt)
        if key in existing_edges:
            continue
        try:
            ps.add_relation(src, RelationType.DEPENDS_ON, tgt,
                            source="ground_state_sequence_v1",
                            note="ground observation_sequence to T1/sequence (uniform sequence grounding)")
            print(f"  EXTRA GROUNDING: {src} -> {tgt}")
            extra_added += 1
        except Exception:
            pass

    post_atoms = len(ps.all_atoms())
    post_rels = sum(1 for _ in ps.iter_all_relations())
    print(f"\n=== GROUND state_sequence v1 SUMMARY ===")
    print(f"atoms: {pre_atoms} -> {post_atoms}  (+{post_atoms - pre_atoms})")
    print(f"relations: {pre_rels} -> {post_rels}  (+{post_rels - pre_rels})")
    print(f"  T1/sequence created: {created}")
    print(f"  state_sequence grounded: True")
    print(f"  observation_sequence grounded: {extra_added}")
    print(f"\nExpected scanner result: 5/5 new supertypes backward-chain to T1.")
    print(f"sequence_decoder_operator -> state_sequence -> T1/sequence -> terminus.")


if __name__ == "__main__":
    main()
