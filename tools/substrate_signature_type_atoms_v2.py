"""Signature type atoms v2 — second batch toward 15/15 gated ABSTRACTION.

Continues v1 pivot. Adds 5 more composite signature type atoms to push
the type-graph terminator count to 15/15 per COMPOUND optimization memo.

NEW THIS BATCH:
  T1/banach_space (complete normed vector space)
  T1/sigma_algebra (the structural primitive on which measurable_space depends)
  T1/manifold_type (smooth manifold; underpins differential geometry / Lie theory)
  T1/lie_group_type (smooth manifold + group axioms)
  T1/normed_vector_space (vector_space + norm; bridge to metric_space)

Plus operator->type-atom edges for operators that depend on these types.

NO LLM. NO bge. Class B structure-adding distillation.
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier, RelationType


TYPE_ATOMS = [
    {
        "id": "T1/normed_vector_space",
        "name": "Normed vector space",
        "aliases": ("normed_space",),
        "description": (
            "Vector space V over R or C with a norm ||.||: V -> R+ satisfying "
            "positivity, homogeneity, triangle inequality. Norm induces a metric. "
            "Type underlying banach_space, bounded operators, normed-space duality."
        ),
        "depends_on": ("math::T1/vector_space_over_field", "math::T1/triangle_inequality"),
        "serves_capability": ("cap_type_normed_space",),
    },
    {
        "id": "T1/banach_space",
        "name": "Banach space",
        "aliases": ("complete_normed_space",),
        "description": (
            "Normed vector space that is complete in the induced metric. Type "
            "underlying L^p spaces, dual spaces, Hahn-Banach, open mapping, "
            "closed graph, Banach fixed point. Distinct from hilbert_space which "
            "additionally requires inner product."
        ),
        "depends_on": ("math::T1/normed_vector_space", "math::T1/metric_space"),
        "serves_capability": ("cap_type_banach_space",),
    },
    {
        "id": "T1/sigma_algebra_type",
        "name": "Sigma-algebra (type)",
        "aliases": ("sigma_field", "Borel_set_collection"),
        "description": (
            "Collection F of subsets of a set X containing X and closed under "
            "complement and countable union (hence countable intersection). Type "
            "underlying measurable_space, Borel sets, measurable functions, "
            "probability events. The structural primitive of measure theory."
        ),
        "depends_on": (),
        "serves_capability": ("cap_type_sigma_algebra",),
    },
    {
        "id": "T1/smooth_manifold_type",
        "name": "Smooth manifold (type)",
        "aliases": ("C_infinity_manifold", "differentiable_manifold"),
        "description": (
            "Topological space locally homeomorphic to R^n with smooth transition "
            "functions between charts. Type underlying differential geometry, "
            "Lie groups, tangent bundles, differential forms, Riemannian metrics, "
            "physics state spaces."
        ),
        "depends_on": ("math::T1/topological_space",),
        "serves_capability": ("cap_type_smooth_manifold",),
    },
    {
        "id": "T1/lie_group_type",
        "name": "Lie group (type)",
        "aliases": ("smooth_group",),
        "description": (
            "Smooth manifold with group structure such that multiplication and "
            "inversion are smooth maps. Type underlying continuous symmetries, "
            "representation theory of compact groups, exponential map, Lie "
            "algebras, gauge theories."
        ),
        "depends_on": ("math::T1/smooth_manifold_type", "math::T1/group_axioms"),
        "serves_capability": ("cap_type_lie_group",),
    },
]


# Operator-type binding edges
OPERATOR_TYPE_EDGES = [
    ("math::T1/triangle_inequality", "math::T1/normed_vector_space"),
    ("math::T1/projection", "math::T1/inner_product_space"),
    ("math::T1/eigenvalue", "math::T1/linear_operator"),
    ("math::T1/eigenvector", "math::T1/linear_operator"),
    ("math::T1/spectral_decomposition", "math::T1/self_adjoint_operator_type"),
    ("math::T1/measurable_space", "math::T1/sigma_algebra_type"),
    ("math::T1/probability_measure", "math::T1/sigma_algebra_type"),
    ("math::T1/expectation", "math::T1/probability_space"),
    ("math::T1/variance", "math::T1/probability_space"),
    # T3 chain atoms binding to new types
    ("math::T3/inner_product_bilinearity_lemma", "math::T1/inner_product_space"),
    ("math::T3/quadratic_nonnegative_discriminant_lemma", "math::T1/vector_space_over_field"),
]


def main():
    ps = PartitionedStore(Path("data/substrate_index"))
    pre_atoms = len(ps.all_atoms())
    pre_rels = sum(1 for _ in ps.iter_all_relations())
    print(f"pre-ingest: {pre_atoms} atoms, {pre_rels} relations\n")

    created = 0
    skipped = 0
    for spec in TYPE_ATOMS:
        qid = f"math::{spec['id']}"
        if ps.has_atom(qid):
            print(f"  ATOM SKIP (exists): {qid}")
            skipped += 1
            continue
        try:
            metadata = {
                "operation_type": "signature_type_atom",
                "is_type_atom": True,
                "type_graph_terminator": True,
                "science_algebra_category": "foundations::type_atom",
                "signature_hint": "type_constructor",
                "is_axiom": False,
                "content_type": "FORMAL_SYSTEMS",
                "substrate_load_bearing": True,
                "batch_origin": "signature_type_atoms_v2",
                "distillation_class": "B_structure_adding",
                "rule_link": "20th_rule_3mode_distillation;21st_rule_type_graph_terminates_in_atoms",
            }
            atom = Atom(
                id=spec["id"], name=spec["name"], corpus=Corpus.MATH,
                tier=Tier.TIER_1_FOUNDATIONAL, description=spec["description"],
                kind=AtomKind.PRIMITIVE, aliases=spec["aliases"],
                metadata=metadata, serves_capability=spec["serves_capability"],
            )
            ps.add_atom(atom, source="signature_type_atoms_v2",
                        note="Class B structure-adding distillation v2; type-graph terminator")
            print(f"  ATOM CREATED: {qid}")
            created += 1
        except Exception as e:
            print(f"  ATOM FAIL: {qid} :: {str(e)[:140]}")

    print()
    existing_edges = set()
    for r in ps.iter_all_relations():
        try:
            existing_edges.add((r.src_qualified_id, r.rel_type.name, r.tgt_qualified_id))
        except AttributeError:
            pass

    added_t = 0
    miss_t = 0
    for spec in TYPE_ATOMS:
        src = f"math::{spec['id']}"
        if not ps.has_atom(src):
            continue
        for tgt in spec["depends_on"]:
            if not ps.has_atom(tgt):
                miss_t += 1
                continue
            key = (src, "DEPENDS_ON", tgt)
            if key in existing_edges:
                continue
            try:
                ps.add_relation(src, RelationType.DEPENDS_ON, tgt,
                                source="signature_type_atoms_v2",
                                note="type atom composition v2")
                print(f"  TYPE_EDGE: {src} -> {tgt}")
                added_t += 1
                existing_edges.add(key)
            except Exception as e:
                pass

    print()
    added_op = 0
    miss_op = 0
    for src, tgt in OPERATOR_TYPE_EDGES:
        if not ps.has_atom(src) or not ps.has_atom(tgt):
            miss_op += 1
            continue
        key = (src, "DEPENDS_ON", tgt)
        if key in existing_edges:
            continue
        try:
            ps.add_relation(src, RelationType.DEPENDS_ON, tgt,
                            source="signature_type_atoms_v2",
                            note="operator binds to its signature type atom v2")
            print(f"  OP_EDGE: {src} -> {tgt}")
            added_op += 1
            existing_edges.add(key)
        except Exception as e:
            pass

    post_atoms = len(ps.all_atoms())
    post_rels = sum(1 for _ in ps.iter_all_relations())
    print(f"\n=== SIGNATURE TYPE ATOMS v2 SUMMARY ===")
    print(f"atoms: {pre_atoms} -> {post_atoms} (+{post_atoms - pre_atoms})")
    print(f"relations: {pre_rels} -> {post_rels} (+{post_rels - pre_rels})")
    print(f"  type atoms created: {created} (skipped existing: {skipped})")
    print(f"  type-type edges added: {added_t} miss: {miss_t}")
    print(f"  operator-type edges added: {added_op} miss: {miss_op}")
    print(f"\nCumulative composite-type atomization: 10/15 (v1) + {created}/5 (v2) toward 15/15 gated ABSTRACTION")


if __name__ == "__main__":
    main()
