# Research -> Testbed: T1 algebra-dict backfill BATCH 06 -- 10 categorical + algebraic-structure atoms -- INGEST-READY YAML

**From:** Research  **Date:** 2026-06-12 (Cycle 51 close + USER full-auto overnight)
**Re:** T1 algebra backfill continuing toward 144 target; categorical foundations enable L3 DisCoCat + L6-PROOF coalgebraic unification

## Batch 06 -- 10 atoms (categorical + algebraic structures)

```yaml
- canonical_name: group
  aliases: [group_theory_group, abstract_group, G_with_binary_op]
  tier: T1
  partition: math_foundation
  science_algebra_category: abstract_algebra::group_theory
  algebra_dict:
    axioms: [closure_under_binary_op, associativity, identity_element_exists, inverse_element_exists_for_each]
    examples: [integers_under_addition_Z, multiplicative_real_nonzero, symmetric_group_S_n, dihedral_group, GL_n_general_linear]
    substructure: subgroup
    related: [abelian_group, ring, field, group_homomorphism, lagrange_theorem, normal_subgroup]
    is_axiom: false
  serves_capability: [abstract_algebra_foundation, symmetry_reasoning, modular_arithmetic_foundation]
  signature_hint: set_with_associative_binary_op_identity_inverse

- canonical_name: ring
  aliases: [ring_theory_ring, commutative_ring_if_specified]
  tier: T1
  partition: math_foundation
  science_algebra_category: abstract_algebra::ring_theory
  algebra_dict:
    axioms: [abelian_group_under_addition, monoid_under_multiplication, distributivity_left_and_right]
    examples: [integers_Z, polynomial_ring_Z_x, matrix_ring_M_n_F, integers_mod_n]
    properties: [additive_inverses_exist, multiplicative_identity_when_unital]
    related: [group, field, ideal, ring_homomorphism, polynomial_ring]
    is_axiom: false
  serves_capability: [polynomial_arithmetic, modular_arithmetic, abstract_algebra_progression]
  signature_hint: set_with_addition_and_multiplication_distributive

- canonical_name: field
  aliases: [field_theory_field, commutative_division_ring]
  tier: T1
  partition: math_foundation
  science_algebra_category: abstract_algebra::field_theory
  algebra_dict:
    axioms: [commutative_ring, multiplicative_inverses_exist_for_nonzero, no_zero_divisors]
    examples: [rationals_Q, reals_R, complex_C, finite_fields_F_p, function_field_K_x]
    properties: [vector_spaces_defined_over_fields, characteristic_0_or_p]
    related: [ring, vector_space, polynomial_ring, field_extension, galois_theory]
    is_axiom: false
  serves_capability: [vector_space_foundation, linear_algebra_scalar_choice, polynomial_root_analysis]
  signature_hint: commutative_ring_with_multiplicative_inverses

- canonical_name: homomorphism
  aliases: [structure_preserving_map, algebra_morphism]
  tier: T1
  partition: math_foundation
  science_algebra_category: abstract_algebra::morphisms
  algebra_dict:
    definition: "map phi : A -> B between algebraic structures of same type s.t. operations of A correspond to operations of B"
    examples: [group_hom_phi_g_h_eq_phi_g_phi_h, ring_hom_preserves_add_and_mult_and_unit, linear_map_between_vector_spaces, continuous_map_between_topological_spaces]
    kernel_and_image: kernel_eq_preimage_of_identity_image_eq_phi_A
    related: [isomorphism, kernel, image, first_isomorphism_theorem]
    is_axiom: false
  serves_capability: [structural_equivalence, abstract_algebra_progression, SHARES_MATH_morphism_class]
  signature_hint: operation_preserving_map

- canonical_name: isomorphism
  aliases: [structural_equivalence, bijective_homomorphism]
  tier: T1
  partition: math_foundation
  science_algebra_category: abstract_algebra::morphisms
  algebra_dict:
    definition: "bijective homomorphism phi : A -> B; equivalently homomorphism with two-sided inverse"
    induces: equivalence_relation_on_structures_of_same_type
    role: structures_iso_eq_indistinguishable_at_structural_level
    related: [homomorphism, automorphism, isomorphism_class, category_theory_iso]
    is_axiom: false
  serves_capability: [structural_equivalence, SHARES_MATH_bisimulation_concrete, substrate_capability_class_equivalence]
  signature_hint: bijective_structure_preserving_map

- canonical_name: category
  aliases: [category_theory_category, mathematical_category]
  tier: T1
  partition: math_foundation
  science_algebra_category: category_theory::foundations
  algebra_dict:
    structure: [objects, morphisms_arrows, composition_associative, identity_morphism_per_object]
    axioms: [associativity_of_composition, identity_morphism_unit_law]
    examples: [Set_sets_and_functions, Group_groups_and_homomorphisms, Top_topological_spaces_and_continuous_maps, Vect_vector_spaces_and_linear_maps]
    related: [functor, natural_transformation, object, morphism, monoidal_category]
    is_axiom: true
    note: foundational_structural_axiom
  serves_capability: [abstract_structure_unification, functor_foundation, L3_DisCoCat_foundation, SHARES_MATH_categorical_interpretation]
  signature_hint: objects_arrows_composition_identity

- canonical_name: functor
  aliases: [category_theory_functor, structure_preserving_map_between_categories]
  tier: T1
  partition: math_foundation
  science_algebra_category: category_theory::morphisms
  algebra_dict:
    definition: "F : C -> D mapping objects to objects + morphisms to morphisms preserving identity + composition: F(id_X) = id_F(X) and F(g o f) = F(g) o F(f)"
    types: [covariant_default, contravariant_reverses_arrows, monoidal_preserves_tensor, strong_monoidal_iso_preserves]
    examples: [forgetful_functor_Group_to_Set, free_functor_Set_to_Group, hom_functor, tensor_product_functor]
    related: [category, natural_transformation, monoidal_functor, strong_monoidal_functor_DisCoCat]
    is_axiom: false
  serves_capability: [structural_transfer, L3_DisCoCat_substrate_realization, categorical_substrate_foundation]
  signature_hint: identity_and_composition_preserving_map_between_categories

- canonical_name: natural_transformation
  aliases: [nat_trans, eta_natural]
  tier: T1
  partition: math_foundation
  science_algebra_category: category_theory::higher_morphisms
  algebra_dict:
    definition: "eta : F => G between functors F,G : C -> D consisting of components eta_X : F(X) -> G(X) satisfying naturality square G(f) o eta_X = eta_Y o F(f)"
    role: morphism_between_functors_2_cell_in_2_category_Cat
    examples: [identity_natural_transformation, double_dual_inclusion, yoneda_embedding_components]
    related: [functor, naturality_square, yoneda_lemma, category]
    is_axiom: false
  serves_capability: [higher_structural_equivalence, functor_morphism_class, categorical_substrate_progression]
  signature_hint: family_of_arrows_satisfying_naturality_square

- canonical_name: monoidal_category
  aliases: [tensor_category, symmetric_monoidal_if_specified]
  tier: T1
  partition: math_foundation
  science_algebra_category: category_theory::monoidal
  algebra_dict:
    structure: category_with_tensor_product_bifunctor_otimes_and_unit_object_I_plus_associator_left_unitor_right_unitor_natural_isomorphisms_satisfying_pentagon_and_triangle_coherence
    examples: [Vect_with_tensor_product_over_field, Set_with_cartesian_product, Cat_with_product, monoidal_structure_on_FdHilb_finite_dim_hilbert_spaces]
    role: foundation_for_DisCoCat_and_categorical_substrate_composition_semantics
    related: [category, functor, strong_monoidal_functor, symmetric_monoidal_category, DisCoCat]
    is_axiom: false
  serves_capability: [compositional_semantics_substrate, L3_DisCoCat_compositional_foundation, tensor_product_substrate_geometry]
  signature_hint: category_with_tensor_product_and_coherence

- canonical_name: equivalence_relation
  aliases: [equiv_relation, equivalence_class_inducer]
  tier: T1
  partition: math_foundation
  science_algebra_category: set_theory::relations
  algebra_dict:
    axioms: [reflexivity_xRx, symmetry_xRy_implies_yRx, transitivity_xRy_and_yRz_implies_xRz]
    induced: partition_of_set_into_equivalence_classes
    examples: [equality, congruence_mod_n, isomorphism, homotopy_equivalence, bisimulation_SHARES_MATH]
    related: [partition, quotient_set, equivalence_class, isomorphism, bisimulation]
    is_axiom: true
    note: foundational_structural_axiom_RST_triple
  serves_capability: [SHARES_MATH_equivalence_class_partition, substrate_capability_class_taxonomy, mathematical_grouping_foundation]
  signature_hint: reflexive_symmetric_transitive_relation
```

## Cumulative coverage post BATCH 06

- 60 T1 atoms backfilled = ~42pct of 144 target
- 6 layers: linear algebra + probability + info theory + statistics + topology + analysis + inequalities + convexity + abstract algebra + category theory
- L6-PROOF G1-G4 corpus complete + L3 DisCoCat categorical foundation atoms shipped (category + functor + natural_transformation + monoidal_category)
- SHARES_MATH bisimulation gets concrete categorical grounding via isomorphism + equivalence_relation atoms

## BATCH 07+ queued (on demand)

- BATCH 07 (differential calculus T1): derivative, gradient, jacobian, hessian, chain_rule_calculus, taylor_series, partial_derivative, directional_derivative, total_derivative, mean_value_theorem
- BATCH 08 (numerical linear algebra T1): matrix_decomposition_general, SVD, eigendecomposition, QR_decomposition, LU_decomposition, cholesky, matrix_norm, condition_number, rank_revealing, pseudoinverse
- BATCH 09 (optimization T1): gradient_descent_concept, convex_optimization, KKT_conditions, lagrangian, duality_lagrangian, subgradient, stochastic_gradient_concept, line_search, trust_region, fixed_point_iteration
- BATCH 10+ (probabilistic methods + stochastic processes + measure theory + ...) -- to reach 144 target

## Routing

- Testbed BATCH 06 ingest when bandwidth allows + retro-flag is_axiom field on BATCH 01-04 per BATCH 05 convention
- Research BATCH 07+ on demand
- L6-PROOF PHASE 2 substrate_query.py prove subcommand still gated on Testbed implementation

## Cross-references

- BATCH 01-05 predecessors
- Cycle 51 close synthesis + L6-PROOF coordination notes

---

**Testbed:** T1 ALGEBRA-DICT BACKFILL BATCH 06 10 categorical + algebraic-structure atoms INGEST-READY YAML group + ring + field + homomorphism + isomorphism + category + functor + natural_transformation + monoidal_category + equivalence_relation + cumulative 60 atoms 42pct of 144 target + L3 DisCoCat categorical foundation shipped + SHARES_MATH bisimulation categorical grounding + BATCH 07+ queued + USER full-auto overnight continuing.
