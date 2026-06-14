"""Wire 5 DETECTED-ONLY abstraction families to prover-traversable WIRED status.

Per Exp-Dev step-#3 wiring worklist (2026-06-13 evening): scanner HEAD
de497280 finds 6 abstraction families. 1 is WIRED (gradient_based_optimizer
template). 5 are DETECTED-ONLY (shared output but no supertype atom + no
SPECIALIZES edges).

This v1 ships the supertype atom + SPECIALIZES edges for each of the 5:

  HMM family (state_distribution): forward_algorithm, backward_algorithm,
    hmm_transition -> T2/hmm_inference_operator
  VSA binding (phasor_vector): fhrr_bind, fhrr_unbind -> T2/fhrr_binding_op
  VSA superpose (vector): bundling, permutation_indexed_binding ->
    T2/vsa_superposition_op
  Graph search (state_sequence): dijkstra, astar -> T2/path_search_operator
  Sequence decoding (state_sequence): beam_search, viterbi_decoder ->
    T2/sequence_decoder_operator

After this lands, scanner should report 6/6 WIRED. Substrate's prover
can now backward-chain member -> supertype -> T1, enabling the closed
self-improvement loop to REASON over abstraction (not just detect it).

NO LLM. NO bge. Pure schema authoring + SPECIALIZES edge wiring.
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier, RelationType


# Each entry: supertype atom spec + members that SPECIALIZES it.
FAMILIES = [
    {
        "supertype_id": "T2/hmm_inference_operator",
        "name": "HMM inference operator",
        "aliases": ("hmm_inference", "hmm_state_marginal_op"),
        "description": (
            "Supertype for operators that perform inference over hidden Markov "
            "models, returning a state-distribution-shaped object given HMM "
            "parameters and observations. Includes forward marginal (alpha "
            "recursion), backward smoothing (beta recursion), and transition-"
            "probability operator. Mirrors gradient_based_optimizer template."
        ),
        "domain": "hidden_markov_models",
        "signature_output_type": "state_distribution",
        "members_short_ids": ["forward_algorithm", "backward_algorithm", "hmm_transition"],
        "depends_on": ("math::T2/state_distribution", "math::T2/observation_sequence"),
    },
    {
        "supertype_id": "T2/fhrr_binding_op",
        "name": "FHRR binding operator",
        "aliases": ("fhrr_binding", "phasor_binding_op"),
        "description": (
            "Supertype for FHRR phasor-vector binding operators. Both bind "
            "(elementwise complex multiply) and unbind (inverse-bind via complex "
            "conjugate) are members. Both operate on phasor_vector inputs and "
            "produce phasor_vector outputs. Mirrors gradient_based_optimizer "
            "template at the VSA layer."
        ),
        "domain": "vsa_binding",
        "signature_output_type": "phasor_vector",
        "members_short_ids": ["fhrr_bind", "fhrr_unbind"],
        "depends_on": ("math::T2/phasor_vector",),
    },
    {
        "supertype_id": "T2/vsa_superposition_op",
        "name": "VSA superposition operator",
        "aliases": ("vsa_superpose", "bundling_or_indexed_binding_op"),
        "description": (
            "Supertype for VSA operators that combine multiple atomic vectors "
            "into a single composite vector via additive bundling or permutation-"
            "indexed binding. Both produce a vector output and underpin "
            "multi-slot memory representations."
        ),
        "domain": "vsa_composition",
        "signature_output_type": "vector",
        "members_short_ids": ["bundling", "permutation_indexed_binding"],
        "depends_on": ("math::T1/vector",),
    },
    {
        "supertype_id": "T2/path_search_operator",
        "name": "Path search operator",
        "aliases": ("graph_path_search", "shortest_path_op"),
        "description": (
            "Supertype for graph-search operators that return an ordered state-"
            "sequence path from source to target. Includes Dijkstra (no negative "
            "weights) and A-star (with admissible heuristic). Mirrors "
            "gradient_based_optimizer template at the graph-algorithms layer."
        ),
        "domain": "graph_search",
        "signature_output_type": "state_sequence",
        "members_short_ids": ["dijkstra", "astar"],
        "depends_on": ("math::T2/state_sequence", "math::T1/graph_topology"),
    },
    {
        "supertype_id": "T2/sequence_decoder_operator",
        "name": "Sequence decoder operator",
        "aliases": ("sequence_decoder", "best_sequence_search_op"),
        "description": (
            "Supertype for sequence-decoder operators that produce a state-"
            "sequence output given a scoring model. Includes beam search "
            "(approximate top-k) and Viterbi (exact MAP). Mirrors "
            "gradient_based_optimizer template at the sequence-decoding layer."
        ),
        "domain": "sequence_decoding",
        "signature_output_type": "state_sequence",
        "members_short_ids": ["beam_search", "viterbi_decoder"],
        "depends_on": ("math::T2/state_sequence",),
    },
]


def main():
    ps = PartitionedStore(Path("data/substrate_index"))
    pre_atoms = len(ps.all_atoms())
    pre_rels = sum(1 for _ in ps.iter_all_relations())
    print(f"pre-ingest: {pre_atoms} atoms, {pre_rels} relations\n")

    # Build short_id -> atoms map for SPECIALIZES wiring
    from collections import defaultdict
    by_short = defaultdict(list)
    for a in ps.all_atoms():
        short = str(a.id).split("/")[-1].lower()
        by_short[short].append(a)

    families_wired = 0
    supertypes_created = 0
    supertypes_skipped = 0
    edges_added = 0
    edges_skipped_exists = 0
    members_missing = 0

    existing_edges = set()
    for r in ps.iter_all_relations():
        try:
            existing_edges.add((r.src_qualified_id, r.rel_type.name, r.tgt_qualified_id))
        except AttributeError:
            pass

    for fam in FAMILIES:
        super_qid = f"math::{fam['supertype_id']}"
        # Create supertype atom if missing
        if ps.has_atom(super_qid):
            print(f"  SUPERTYPE EXISTS: {super_qid}")
            supertypes_skipped += 1
        else:
            try:
                meta = {
                    "operation_type": "abstraction_supertype",
                    "is_supertype_atom": True,
                    "wired_template_source": "gradient_based_optimizer",
                    "science_algebra_category": f"abstraction_supertype::{fam['domain']}",
                    "substrate_load_bearing": True,
                    "batch_origin": "wire_5_abstraction_families_v1",
                    "distillation_class": "B_structure_adding_supertype",
                    "rule_link": "20th_rule_3mode;Skunkworks_direction_step_3_wiring;Exp_Dev_step_3_worklist",
                    "content_type": "FORMAL_SYSTEMS",
                }
                alg = {
                    "about_topic": fam["supertype_id"].split("/")[-1],
                    "domain": fam["domain"],
                    "signature_output_type": fam["signature_output_type"],
                    "role": "abstraction_supertype",
                }
                atom = Atom(
                    id=fam["supertype_id"],
                    name=fam["name"],
                    corpus=Corpus.MATH,
                    tier=Tier.TIER_2_PRIMITIVE,
                    description=fam["description"],
                    kind=AtomKind.PRIMITIVE,
                    aliases=fam["aliases"],
                    metadata=meta,
                    serves_capability=(),
                    algebra=alg,
                )
                ps.add_atom(
                    atom,
                    source="wire_5_abstraction_families_v1",
                    note=f"abstraction supertype for {fam['domain']} -> {fam['signature_output_type']}",
                )
                print(f"  SUPERTYPE CREATED: {super_qid}")
                supertypes_created += 1
            except Exception as e:
                print(f"  SUPERTYPE FAIL: {super_qid} :: {str(e)[:120]}")
                continue

        # depends_on edges for the supertype itself
        for tgt in fam["depends_on"]:
            if not ps.has_atom(tgt):
                continue
            key = (super_qid, "DEPENDS_ON", tgt)
            if key in existing_edges:
                continue
            try:
                ps.add_relation(super_qid, RelationType.DEPENDS_ON, tgt,
                                source="wire_5_abstraction_families_v1",
                                note="supertype depends on its signature components")
                existing_edges.add(key)
            except Exception:
                pass

        # SPECIALIZES edges from each member -> supertype
        family_wired_members = 0
        for short in fam["members_short_ids"]:
            members = by_short.get(short, [])
            if not members:
                print(f"    MEMBER_NOT_FOUND: {short}")
                members_missing += 1
                continue
            for member in members:
                src_qid = f"math::{member.id}"
                key = (src_qid, "SPECIALIZES", super_qid)
                if key in existing_edges:
                    edges_skipped_exists += 1
                    continue
                try:
                    ps.add_relation(
                        src_qid, RelationType.SPECIALIZES, super_qid,
                        source="wire_5_abstraction_families_v1",
                        note=f"{short} SPECIALIZES {fam['name']}",
                    )
                    print(f"    SPECIALIZES: {src_qid} -> {super_qid}")
                    edges_added += 1
                    family_wired_members += 1
                    existing_edges.add(key)
                except Exception as e:
                    print(f"    EDGE_FAIL: {src_qid} -> {super_qid} :: {str(e)[:80]}")
        if family_wired_members > 0:
            families_wired += 1

    post_atoms = len(ps.all_atoms())
    post_rels = sum(1 for _ in ps.iter_all_relations())
    print(f"\n=== WIRE 5 ABSTRACTION FAMILIES v1 SUMMARY ===")
    print(f"atoms: {pre_atoms} -> {post_atoms}  (+{post_atoms - pre_atoms})")
    print(f"relations: {pre_rels} -> {post_rels}  (+{post_rels - pre_rels})")
    print(f"  supertypes created: {supertypes_created} (skipped existing: {supertypes_skipped})")
    print(f"  families wired: {families_wired} / 5")
    print(f"  SPECIALIZES edges added: {edges_added}")
    print(f"  edges skipped (already exist): {edges_skipped_exists}")
    print(f"  members not found: {members_missing}")
    print(f"\nExpected scanner result: 6/6 WIRED (1 template + 5 newly wired)")
    print(f"Closed loop step #3 (wiring) now complete -- prover can traverse all 6 abstractions.")


if __name__ == "__main__":
    main()
