"""T1 algebra-dict batches 06 (categorical algebraic structures) + 07 (differential calculus).

11 absent atoms (substrate already has group/ring/field/category/derivative/gradient/jacobian/hessian/taylor_series).
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier


ATOMS = [
    # BATCH 06 (categorical algebraic structures)
    {"id": "T1/homomorphism", "name": "Homomorphism", "aliases": ("structure_preserving_map",),
     "description": "Map f: G -> H between algebraic structures preserving operations: f(a * b) = f(a) * f(b). Foundation for category theory + universal algebra.",
     "serves_capability": ("algebraic_structure_morphisms", "category_theory_foundations", "substrate_self_knowledge"),
     "metadata": {"science_algebra_category": "algebra::structure_morphisms", "signature_hint": "operation_preserving_map",
                  "related": "isomorphism functor group ring field", "batch_origin": "batch_06"}},
    {"id": "T1/isomorphism", "name": "Isomorphism", "aliases": ("structure_identity", "bijective_homomorphism"),
     "description": "Bijective homomorphism. Two structures are isomorphic iff there exists an isomorphism between them; structurally indistinguishable.",
     "serves_capability": ("algebraic_structure_equivalence", "category_theory_foundations", "substrate_self_knowledge"),
     "metadata": {"science_algebra_category": "algebra::structure_morphisms", "signature_hint": "bijective_homomorphism",
                  "related": "homomorphism category equivalence_relation", "batch_origin": "batch_06"}},
    {"id": "T1/functor", "name": "Functor", "aliases": ("category_morphism", "F_C_to_D"),
     "description": "F: C -> D between categories preserving identity + composition. Foundation for natural transformations + category theory + DisCoCat.",
     "serves_capability": ("category_theory_foundations", "compositional_semantics", "substrate_self_knowledge"),
     "metadata": {"science_algebra_category": "category_theory::core_constructs", "signature_hint": "category_to_category_map",
                  "related": "category natural_transformation monoidal_category homomorphism", "batch_origin": "batch_06"}},
    {"id": "T1/natural_transformation", "name": "Natural transformation", "aliases": ("eta_F_to_G", "functor_morphism"),
     "description": "eta: F -> G between functors with naturality square commuting. Foundation for higher category theory + 2-categories.",
     "serves_capability": ("category_theory_foundations", "higher_categorical_structure", "substrate_self_knowledge"),
     "metadata": {"science_algebra_category": "category_theory::core_constructs", "signature_hint": "naturality_square",
                  "related": "functor category 2_category", "batch_origin": "batch_06"}},
    {"id": "T1/monoidal_category", "name": "Monoidal category", "aliases": ("tensor_category", "C_tensor_I"),
     "description": "Category with tensor product (x) + unit object I + associator + unitors satisfying coherence axioms. Foundation for DisCoCat + quantum mechanics + Frobenius algebra.",
     "serves_capability": ("compositional_semantics", "DisCoCat_foundations", "substrate_self_knowledge"),
     "metadata": {"science_algebra_category": "category_theory::monoidal_structures", "signature_hint": "tensor_unit_associator_coherence",
                  "related": "category functor frobenius_algebra discocat", "batch_origin": "batch_06"}},
    {"id": "T1/equivalence_relation", "name": "Equivalence relation", "aliases": ("equiv_rel", "reflexive_symmetric_transitive"),
     "description": "Binary relation ~ that is reflexive (a~a), symmetric (a~b => b~a), transitive (a~b ^ b~c => a~c). Foundation for quotient sets + partitions.",
     "serves_capability": ("set_partition_foundations", "quotient_construction", "substrate_self_knowledge"),
     "metadata": {"science_algebra_category": "algebra::foundational_relations", "signature_hint": "reflexive_symmetric_transitive",
                  "related": "isomorphism equivalence_class_quotient_graph partition", "batch_origin": "batch_06"}},
    # BATCH 07 (differential calculus)
    {"id": "T1/chain_rule_calculus", "name": "Chain rule (calculus)", "aliases": ("composition_derivative", "d_f_g_x"),
     "description": "(f o g)'(x) = f'(g(x)) * g'(x). Foundation for backpropagation + automatic differentiation.",
     "serves_capability": ("calculus_foundations", "backpropagation_foundation", "substrate_self_knowledge"),
     "metadata": {"science_algebra_category": "calculus::differentiation_rules", "signature_hint": "composition_derivative",
                  "related": "derivative gradient backpropagation chain_rule", "batch_origin": "batch_07"}},
    {"id": "T1/partial_derivative", "name": "Partial derivative", "aliases": ("d_f_d_x_i", "f_x_i"),
     "description": "partial f / partial x_i = derivative of f w.r.t. x_i holding others constant. Foundation for gradient + Jacobian + Hessian.",
     "serves_capability": ("multivariate_calculus_foundations", "gradient_construction", "substrate_self_knowledge"),
     "metadata": {"science_algebra_category": "calculus::multivariate_differentiation", "signature_hint": "single_variable_derivative_holding_others",
                  "related": "derivative gradient jacobian total_derivative", "batch_origin": "batch_07"}},
    {"id": "T1/directional_derivative", "name": "Directional derivative", "aliases": ("D_v_f", "rate_of_change_along_direction"),
     "description": "D_v f(x) = lim_{h->0} (f(x + h*v) - f(x)) / h. Equals gradient . v for differentiable f.",
     "serves_capability": ("multivariate_calculus_foundations", "gradient_descent_geometry", "substrate_self_knowledge"),
     "metadata": {"science_algebra_category": "calculus::multivariate_differentiation", "signature_hint": "rate_along_unit_vector",
                  "related": "gradient partial_derivative", "batch_origin": "batch_07"}},
    {"id": "T1/total_derivative", "name": "Total derivative", "aliases": ("Df", "linear_approximation"),
     "description": "Best linear approximation Df: T_x M -> T_y N. For f: R^n -> R^m it's the Jacobian matrix.",
     "serves_capability": ("multivariate_calculus_foundations", "linearization", "substrate_self_knowledge"),
     "metadata": {"science_algebra_category": "calculus::multivariate_differentiation", "signature_hint": "best_linear_approximation",
                  "related": "jacobian partial_derivative differentiability", "batch_origin": "batch_07"}},
    {"id": "T1/mean_value_theorem", "name": "Mean value theorem", "aliases": ("MVT", "lagrange_MVT"),
     "description": "For continuous f on [a,b], differentiable on (a,b): exists c in (a,b) s.t. f'(c) = (f(b) - f(a)) / (b - a).",
     "serves_capability": ("calculus_foundations", "Taylor_theorem_proof", "substrate_self_knowledge"),
     "metadata": {"science_algebra_category": "calculus::core_theorems", "signature_hint": "instantaneous_equals_average_slope",
                  "related": "derivative taylor_series lipschitz_continuity", "batch_origin": "batch_07"}},
]


def main():
    ps = PartitionedStore(Path("data/substrate_index"))
    print(f"pre-ingest: {len(ps.all_atoms())} atoms\n")
    c = s = f = 0
    for spec in ATOMS:
        qid = f"math::{spec['id']}"
        if ps.has_atom(qid):
            print(f"SKIP: {qid}"); s += 1; continue
        try:
            atom = Atom(id=spec["id"], name=spec["name"], corpus=Corpus.MATH, tier=Tier.TIER_1_FOUNDATIONAL,
                        description=spec["description"], kind=AtomKind.PRIMITIVE, aliases=spec["aliases"],
                        metadata=spec["metadata"], serves_capability=spec["serves_capability"])
            ps.add_atom(atom, source="t1_algebra_dict_batches_06_07", note=f"per {spec['metadata']['batch_origin']}")
            print(f"CREATED: {qid}"); c += 1
        except Exception as e:
            print(f"FAIL: {qid}: {str(e)[:100]}"); f += 1
    print(f"\npost-ingest: {len(ps.all_atoms())}; created={c} skipped={s} failed={f}")


if __name__ == "__main__":
    main()
