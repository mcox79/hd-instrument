"""Signature type atoms v1 — composite types substrate operators reference
but that were not themselves atomized.

PIVOT per self-critique 2026-06-13:
  Memory `substrate_COMPOUND_optimization_story` names ABSTRACTION mode gated
  on 98% unatomized signature types. The unlock path is 10-15 composite
  type-atoms terminating the substrate type-graph.

  This is Class B structure-adding distillation (20th rule taxonomy), the
  ACTUAL gated lift — not more T3 derivation chains.

Type atoms describe SPACES / STRUCTURES (the domain of operators), distinct
from theorem atoms which describe IDENTITIES on those structures.

Flag: metadata.is_type_atom = True marks these as type-graph terminators.

NO LLM. NO bge. Pure schema authoring.
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier, RelationType


TYPE_ATOMS = [
    {
        "id": "T1/vector_space_over_field",
        "name": "Vector space over a field",
        "aliases": ("linear_space", "F_vector_space"),
        "description": (
            "A set V together with a field F and operations (+: V x V -> V, "
            "scalar mul: F x V -> V) satisfying the 8 vector-space axioms. "
            "Type underlying linear_combination, basis, dimension, linear_operator."
        ),
        "depends_on": ("math::T1/field_axioms",),
        "serves_capability": ("cap_type_vector_space",),
    },
    {
        "id": "T1/inner_product_space",
        "name": "Inner product space",
        "aliases": ("ip_space", "pre_hilbert_space"),
        "description": (
            "Vector space V over R or C with a positive-definite Hermitian form "
            "<.,.>: V x V -> F. Type underlying norm-from-inner-product, "
            "orthogonality, projection, Cauchy-Schwarz, Pythagoras-in-IP."
        ),
        "depends_on": ("math::T1/vector_space_over_field", "math::T1/inner_product"),
        "serves_capability": ("cap_type_inner_product_space",),
    },
    {
        "id": "T1/hilbert_space",
        "name": "Hilbert space",
        "aliases": ("complete_inner_product_space",),
        "description": (
            "Inner product space that is complete in the induced metric. Type "
            "underlying L2, spectral theorem, bounded operators, Riesz "
            "representation, orthonormal bases of separable infinite dim."
        ),
        "depends_on": ("math::T1/inner_product_space", "math::T1/metric_space"),
        "serves_capability": ("cap_type_hilbert_space",),
    },
    {
        "id": "T1/metric_space",
        "name": "Metric space",
        "aliases": ("metric_topology",),
        "description": (
            "Set X with distance d: X x X -> R+ satisfying positivity, symmetry, "
            "triangle inequality. Type underlying convergence, completeness, "
            "continuity, compactness, banach_space, hilbert_space."
        ),
        "depends_on": ("math::T1/triangle_inequality",),
        "serves_capability": ("cap_type_metric_space",),
    },
    {
        "id": "T1/topological_space",
        "name": "Topological space",
        "aliases": ("topology",),
        "description": (
            "Set X with a collection tau of open subsets closed under union and "
            "finite intersection (containing empty set + X). Type underlying "
            "continuous_map, homeomorphism, connectedness, compactness."
        ),
        "depends_on": (),
        "serves_capability": ("cap_type_topological_space",),
    },
    {
        "id": "T1/measurable_space",
        "name": "Measurable space",
        "aliases": ("sigma_algebra_space",),
        "description": (
            "Pair (X, Sigma) with sigma-algebra Sigma of subsets closed under "
            "complement and countable union. Type underlying measure, integration, "
            "probability_space, random_variable, conditional_expectation."
        ),
        "depends_on": (),
        "serves_capability": ("cap_type_measurable_space",),
    },
    {
        "id": "T1/probability_space",
        "name": "Probability space",
        "aliases": ("Kolmogorov_triple", "Omega_F_P"),
        "description": (
            "Triple (Omega, F, P) where (Omega, F) is measurable_space and P is "
            "a probability measure with P(Omega)=1. Type underlying random_variable, "
            "expectation, conditional_probability, Bayes_rule, CLT, ergodic_theorem."
        ),
        "depends_on": ("math::T1/measurable_space", "math::T1/probability_measure"),
        "serves_capability": ("cap_type_probability_space",),
    },
    {
        "id": "T1/linear_operator",
        "name": "Linear operator (between vector spaces)",
        "aliases": ("linear_map", "linear_transformation"),
        "description": (
            "Map T: V -> W between vector spaces over the same field such that "
            "T(a*x + b*y) = a*T(x) + b*T(y). Type underlying matrices, bounded "
            "operators, self_adjoint, unitary, eigenvalue_problems."
        ),
        "depends_on": ("math::T1/vector_space_over_field",),
        "serves_capability": ("cap_type_linear_operator",),
    },
    {
        "id": "T1/bilinear_form",
        "name": "Bilinear form",
        "aliases": ("V_times_V_to_F_bilinear",),
        "description": (
            "Map B: V x V -> F linear in each argument (with possible conjugation "
            "in 2nd arg over C). Type underlying inner_product, quadratic_form, "
            "Gram matrix, symmetric and Hermitian forms."
        ),
        "depends_on": ("math::T1/vector_space_over_field",),
        "serves_capability": ("cap_type_bilinear_form",),
    },
    {
        "id": "T1/continuous_map",
        "name": "Continuous map (between topological spaces)",
        "aliases": ("continuous_function",),
        "description": (
            "Function f: X -> Y between topological_spaces such that preimage "
            "of every open set is open. Type underlying homeomorphism, "
            "differentiable maps, integrable functions, paths."
        ),
        "depends_on": ("math::T1/topological_space",),
        "serves_capability": ("cap_type_continuous_map",),
    },
    {
        "id": "T1/bounded_linear_operator",
        "name": "Bounded linear operator",
        "aliases": ("bounded_operator",),
        "description": (
            "Linear operator T: X -> Y between normed spaces with finite operator "
            "norm sup_{||x||<=1} ||Tx||. On Hilbert space, equivalent to continuous. "
            "Type underlying spectrum, adjoint, compact_operator, self_adjoint, "
            "unitary, projection."
        ),
        "depends_on": ("math::T1/linear_operator", "math::T1/hilbert_space"),
        "serves_capability": ("cap_type_bounded_operator",),
    },
    {
        "id": "T1/self_adjoint_operator_type",
        "name": "Self-adjoint operator (type)",
        "aliases": ("hermitian_operator_type", "symmetric_operator_type"),
        "description": (
            "Bounded operator T on Hilbert space with <Tx, y> = <x, Ty> for all "
            "x, y. Type underlying spectral_theorem, real_eigenvalues, observable "
            "in quantum mechanics, covariance_operator. DISTINCT from "
            "T3/self_adjoint_operator_lemma which asserts the property."
        ),
        "depends_on": ("math::T1/bounded_linear_operator",),
        "serves_capability": ("cap_type_self_adjoint",),
    },
    {
        "id": "T1/random_variable_type",
        "name": "Random variable (type)",
        "aliases": ("measurable_function_to_R",),
        "description": (
            "Measurable function X: Omega -> R from probability_space (Omega, F, P) "
            "to R with Borel sigma-algebra. Type underlying expectation, variance, "
            "characteristic_function, distribution, conditional_expectation, CLT."
        ),
        "depends_on": ("math::T1/probability_space",),
        "serves_capability": ("cap_type_random_variable",),
    },
    {
        "id": "T1/measure_preserving_map",
        "name": "Measure-preserving map",
        "aliases": ("measure_preserving_transformation",),
        "description": (
            "Map T: (X, F, mu) -> (X, F, mu) on measure_space with mu(T^{-1}(A)) = "
            "mu(A) for all A in F. Type underlying ergodic_theorem, dynamical_systems, "
            "stationary_processes, Poincare_recurrence."
        ),
        "depends_on": ("math::T1/measurable_space",),
        "serves_capability": ("cap_type_measure_preserving_map",),
    },
    {
        "id": "T1/group_action_type",
        "name": "Group action (type)",
        "aliases": ("G_action_on_set",),
        "description": (
            "Map G x X -> X for group G and set X satisfying identity and "
            "compatibility axioms. Type underlying symmetry, orbit, stabilizer, "
            "representation_theory, equivariant_maps."
        ),
        "depends_on": ("math::T1/group_axioms",),
        "serves_capability": ("cap_type_group_action",),
    },
]


# Operator -> type-atom DEPENDS_ON edges: link existing operators to their
# signature type atoms. Only edges where BOTH endpoints exist are added.
OPERATOR_TYPE_EDGES = [
    ("math::T1/inner_product", "math::T1/inner_product_space"),
    ("math::T1/cosine_similarity", "math::T1/inner_product_space"),
    ("math::T1/orthogonality", "math::T1/inner_product_space"),
    ("math::T1/projection", "math::T1/inner_product_space"),
    ("math::T1/triangle_inequality", "math::T1/metric_space"),
    ("math::T1/cauchy_schwarz_inequality", "math::T1/inner_product_space"),
    ("math::T1/linear_combination", "math::T1/vector_space_over_field"),
    ("math::T1/basis", "math::T1/vector_space_over_field"),
    ("math::T1/eigenvalue", "math::T1/linear_operator"),
    ("math::T1/eigenvector", "math::T1/linear_operator"),
    ("math::T1/probability_measure", "math::T1/measurable_space"),
    ("math::T1/expectation", "math::T1/probability_space"),
    ("math::T1/variance", "math::T1/probability_space"),
    ("math::T1/conditional_probability", "math::T1/probability_space"),
    ("math::T1/characteristic_function", "math::T1/random_variable_type"),
    ("math::T1/singular_value_decomposition", "math::T1/linear_operator"),
    ("math::T1/spectral_decomposition", "math::T1/linear_operator"),
    # T3 derivations bind to type atoms too
    ("math::T3/self_adjoint_operator_lemma", "math::T1/self_adjoint_operator_type"),
    ("math::T3/self_adjoint_real_eigenvalues_lemma", "math::T1/self_adjoint_operator_type"),
    ("math::T3/spectral_theorem_synthesis", "math::T1/self_adjoint_operator_type"),
    ("math::T3/inner_product_bilinearity_lemma", "math::T1/bilinear_form"),
    ("math::T3/inner_product_positive_semidefinite_lemma", "math::T1/inner_product_space"),
    ("math::T3/cauchy_schwarz_synthesis", "math::T1/inner_product_space"),
    ("math::T3/pythagoras_inner_product_synthesis", "math::T1/inner_product_space"),
    ("math::T3/characteristic_function_iid_sum_lemma", "math::T1/random_variable_type"),
    ("math::T3/clt_synthesis", "math::T1/random_variable_type"),
    ("math::T3/bayes_rule_synthesis", "math::T1/probability_space"),
    ("math::T3/product_rule_probability_lemma", "math::T1/probability_space"),
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
                "batch_origin": "signature_type_atoms_v1",
                "distillation_class": "B_structure_adding",
                "rule_link": "20th_rule_3mode_distillation;21st_rule_candidate_type_graph_terminates_in_atoms",
            }
            atom = Atom(
                id=spec["id"],
                name=spec["name"],
                corpus=Corpus.MATH,
                tier=Tier.TIER_1_FOUNDATIONAL,
                description=spec["description"],
                kind=AtomKind.PRIMITIVE,
                aliases=spec["aliases"],
                metadata=metadata,
                serves_capability=spec["serves_capability"],
            )
            ps.add_atom(
                atom,
                source="signature_type_atoms_v1",
                note="Class B structure-adding distillation; type-graph terminator",
            )
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

    added_type_edges = 0
    miss_type_edges = 0
    for spec in TYPE_ATOMS:
        src = f"math::{spec['id']}"
        if not ps.has_atom(src):
            continue
        for tgt in spec["depends_on"]:
            if not ps.has_atom(tgt):
                print(f"  SKIP_MISS_TGT: {src} -> {tgt}")
                miss_type_edges += 1
                continue
            key = (src, "DEPENDS_ON", tgt)
            if key in existing_edges:
                continue
            try:
                ps.add_relation(
                    src,
                    RelationType.DEPENDS_ON,
                    tgt,
                    source="signature_type_atoms_v1",
                    note="type atom composition",
                )
                print(f"  TYPE_EDGE: {src} -> {tgt}")
                added_type_edges += 1
                existing_edges.add(key)
            except Exception as e:
                print(f"  TYPE_EDGE_FAIL: {str(e)[:80]}")

    print()
    added_op_edges = 0
    miss_op_edges = 0
    for src, tgt in OPERATOR_TYPE_EDGES:
        if not ps.has_atom(src) or not ps.has_atom(tgt):
            miss_op_edges += 1
            continue
        key = (src, "DEPENDS_ON", tgt)
        if key in existing_edges:
            continue
        try:
            ps.add_relation(
                src,
                RelationType.DEPENDS_ON,
                tgt,
                source="signature_type_atoms_v1",
                note="operator binds to its signature type atom",
            )
            print(f"  OP_TYPE_EDGE: {src} -> {tgt}")
            added_op_edges += 1
            existing_edges.add(key)
        except Exception as e:
            print(f"  OP_TYPE_EDGE_FAIL: {str(e)[:80]}")

    post_atoms = len(ps.all_atoms())
    post_rels = sum(1 for _ in ps.iter_all_relations())
    print(f"\n=== SIGNATURE TYPE ATOMS v1 SUMMARY ===")
    print(f"atoms: {pre_atoms} -> {post_atoms} (+{post_atoms - pre_atoms})")
    print(f"relations: {pre_rels} -> {post_rels} (+{post_rels - pre_rels})")
    print(f"  type atoms created: {created} (skipped existing: {skipped})")
    print(f"  type-type edges added: {added_type_edges} miss: {miss_type_edges}")
    print(f"  operator-type edges added: {added_op_edges} miss: {miss_op_edges}")
    print(f"\nDistillation class: B structure-adding (20th rule)")
    print(f"21st rule candidate empirical witness: type-graph terminates in atoms")
    print(f"Substrate composite-type atomization: was 0/15 -> now {created}/15 toward gated ABSTRACTION")


if __name__ == "__main__":
    main()
