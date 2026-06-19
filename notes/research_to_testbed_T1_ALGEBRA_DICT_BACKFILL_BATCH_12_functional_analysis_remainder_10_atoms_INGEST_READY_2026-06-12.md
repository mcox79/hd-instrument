# Research -> Testbed: T1 algebra-dict backfill BATCH 12 -- 10 functional analysis remainder atoms -- INGEST-READY YAML

**From:** Research  **Date:** 2026-06-12 (Cycle 51 close + USER full-auto overnight)

## Batch 12 -- 10 atoms (functional analysis remainder)

```yaml
- canonical_name: bounded_linear_operator
  aliases: [BLO, continuous_linear_map_normed_spaces]
  tier: T1
  partition: math_foundation
  science_algebra_category: functional_analysis::operators
  algebra_dict:
    definition: "T : X -> Y linear with ||T x||_Y <= C ||x||_X for some C >= 0; equivalently continuous"
    operator_norm: ||T||_op_eq_sup_x_nonzero_T_x_norm_over_x_norm
    space_of_BLO: B_X_Y_is_banach_when_Y_is_banach
    examples: [matrix_multiplication_finite_dim, integral_operator_with_continuous_kernel, differential_operator_on_appropriate_domain]
    related: [matrix_norm, operator_theory, banach_space, hilbert_space, compact_operator]
    is_axiom: false
  serves_capability: [linear_operator_substrate, functional_analysis_foundation, banach_steinhaus_uniform_boundedness]
  signature_hint: linear_with_bounded_norm_ratio

- canonical_name: compact_operator
  aliases: [completely_continuous_operator, K_X_Y]
  tier: T1
  partition: math_foundation
  science_algebra_category: functional_analysis::operators
  algebra_dict:
    definition: "T : X -> Y is compact iff T maps bounded sets to relatively compact sets"
    spectral_theory_compact_self_adjoint: spectrum_purely_discrete_eigenvalues_accumulate_only_at_zero_eigenvectors_orthonormal_basis_of_eigenspaces
    examples: [integral_operators_with_L_2_kernel, finite_rank_operators_norm_closure]
    related: [bounded_linear_operator, spectral_theorem_compact, fredholm_alternative]
    is_axiom: false
  serves_capability: [spectral_theory_substrate, integral_equation_substrate, finite_rank_approximation]
  signature_hint: maps_bounded_to_precompact_sets

- canonical_name: dual_space
  aliases: [X_star, continuous_linear_functionals, X_prime]
  tier: T1
  partition: math_foundation
  science_algebra_category: functional_analysis::duality
  algebra_dict:
    definition: "X^* = space of continuous linear functionals f : X -> scalar field"
    riesz_representation_hilbert: for_hilbert_space_H_every_continuous_linear_functional_is_inner_product_with_unique_element_H_iso_H_star
    examples: [L_p_dual_eq_L_q_with_conjugate_exponents, sequence_l_p_dual_eq_l_q, C_K_dual_eq_radon_measures_riesz_markov]
    bidual_canonical_embedding: X_to_X_star_star_isometric_reflexive_iff_image_is_all]
    related: [hahn_banach_extension, reflexive_space, weak_topology, riesz_representation_theorem]
    is_axiom: false
  serves_capability: [duality_substrate, lagrangian_duality_foundation, weak_topology_construction]
  signature_hint: space_of_continuous_linear_functionals

- canonical_name: weak_topology
  aliases: [sigma_X_X_star_topology, weak_convergence]
  tier: T1
  partition: math_foundation
  science_algebra_category: functional_analysis::topologies
  algebra_dict:
    definition: "coarsest topology on X making every f in X^* continuous; x_n -> x weakly iff f(x_n) -> f(x) for all f in X^*"
    weak_star_topology_on_X_star: "coarsest topology making evaluation at every x in X continuous"
    banach_alaoglu_theorem: closed_unit_ball_of_X_star_is_weak_star_compact
    compactness_implications: bounded_sequences_in_reflexive_spaces_have_weakly_convergent_subsequences
    related: [dual_space, reflexive_space, banach_alaoglu, weak_convergence_probability]
    is_axiom: false
  serves_capability: [compactness_in_function_spaces, convergence_in_optimization_substrate, banach_alaoglu_substrate]
  signature_hint: coarsest_topology_making_dual_continuous

- canonical_name: sobolev_space
  aliases: [W_k_p, H_k_for_hilbert_case]
  tier: T1
  partition: math_foundation
  science_algebra_category: functional_analysis::pde_spaces
  algebra_dict:
    definition: "W^{k,p}(Omega) = {f in L^p(Omega) : weak derivatives D^alpha f in L^p(Omega) for all |alpha| <= k}"
    norm: f_W_kp_norm_eq_sum_alpha_leq_k_D_alpha_f_Lp_norm
    H_k_hilbert_case: W_k_2_hilbert_with_inner_product_sum_alpha_int_D_alpha_f_D_alpha_g
    sobolev_embedding: W_kp_embeds_into_L_q_or_C_alpha_under_dimension_conditions
    related: [weak_derivative, distribution_generalized_function, hilbert_space, banach_space, PDE_theory]
    is_axiom: false
  serves_capability: [PDE_substrate, weak_solution_concept, regularity_theory_substrate]
  signature_hint: function_space_with_weak_derivatives_in_Lp

- canonical_name: schwartz_space
  aliases: [S_R_n, rapidly_decreasing_functions]
  tier: T1
  partition: math_foundation
  science_algebra_category: functional_analysis::test_function_spaces
  algebra_dict:
    definition: "S(R^n) = smooth functions whose derivatives decay faster than any polynomial reciprocal: sup_x (1 + |x|^N) |D^alpha f(x)| < inf for all N, alpha"
    closed_under: fourier_transform_isomorphism, multiplication_by_polynomial, differentiation
    dual_tempered_distributions: S_prime_used_for_fourier_analysis_of_distributions
    examples: [gaussian_density_e_minus_x_squared, hermite_functions]
    related: [distribution_generalized_function, tempered_distribution, fourier_transform, sobolev_space]
    is_axiom: false
  serves_capability: [fourier_analysis_substrate, distribution_theory_test_function_space, harmonic_analysis_foundation]
  signature_hint: smooth_rapidly_decreasing

- canonical_name: distribution_generalized_function
  aliases: [distribution_schwartz_sense, generalized_function]
  tier: T1
  partition: math_foundation
  science_algebra_category: functional_analysis::distributions
  algebra_dict:
    definition: continuous_linear_functional_on_test_function_space_D_C_infinity_compactly_supported_or_S_schwartz
    examples: [dirac_delta_at_x_0_test_function_f_to_f_x_0, derivative_of_dirac_delta_test_function_f_to_minus_f_prime_x_0, locally_integrable_function_acting_via_integration_pairing]
    operations: [differentiation_extending_classical_via_integration_by_parts, multiplication_by_smooth_function, convolution_with_compactly_supported_distribution]
    related: [schwartz_space, dirac_delta, weak_derivative, sobolev_space, tempered_distribution]
    is_axiom: false
  serves_capability: [pde_solution_concept_substrate, dirac_delta_substrate, weak_derivative_foundation]
  signature_hint: linear_functional_on_test_function_space

- canonical_name: reflexive_space
  aliases: [reflexive_banach_space, X_eq_X_star_star]
  tier: T1
  partition: math_foundation
  science_algebra_category: functional_analysis::dual_structures
  algebra_dict:
    definition: canonical_embedding_X_to_X_star_star_is_surjective
    examples_reflexive: [hilbert_spaces, L_p_spaces_for_1_lt_p_lt_inf, finite_dimensional_normed_spaces]
    examples_not_reflexive: [L_1, L_inf, C_K, c_0_sequence_space]
    consequences: bounded_sequences_have_weakly_convergent_subsequences_via_banach_alaoglu
    related: [dual_space, weak_topology, banach_alaoglu, banach_space]
    is_axiom: false
  serves_capability: [variational_methods_substrate, weak_compactness_use, banach_steinhaus_application]
  signature_hint: bidual_equals_space_via_canonical_embedding

- canonical_name: separable_space
  aliases: [separable_metric_space, countable_dense_subset]
  tier: T1
  partition: math_foundation
  science_algebra_category: topology::separability
  algebra_dict:
    definition: contains_a_countable_dense_subset
    examples_separable: [R_n_with_rationals_dense, L_p_R_n_1_leq_p_lt_inf, continuous_functions_C_K_polynomial_approximation_via_stone_weierstrass]
    examples_non_separable: [L_inf, bounded_continuous_functions_on_unbounded_domain]
    consequences: [exists_countable_orthonormal_basis_in_separable_hilbert_space, computability_friendly]
    related: [hilbert_space, banach_space, metric_space, dense_subset]
    is_axiom: false
  serves_capability: [countable_basis_use, computability_substrate, hilbert_space_orthonormal_basis]
  signature_hint: countable_dense_subset_exists

- canonical_name: hahn_banach_theorem
  aliases: [HB_extension, hahn_banach_extension_theorem]
  tier: T1
  partition: math_foundation
  science_algebra_category: functional_analysis::core_theorems
  algebra_dict:
    extension_form: "continuous linear functional on subspace extends to continuous linear functional on whole space with same norm"
    geometric_form: separation_of_convex_sets_by_hyperplane_under_convexity_conditions
    consequences: [dual_space_X_star_is_nontrivial_for_nonzero_X, characterization_of_weak_topology, banach_alaoglu_uses_HB]
    related: [dual_space, weak_topology, convex_function, banach_space, separating_hyperplane]
    is_axiom: false
  serves_capability: [duality_substrate_existence, separating_hyperplane_substrate, dual_space_nontrivially]
  signature_hint: linear_functional_extension_preserving_norm
```

## Cumulative coverage post BATCH 12

- 120 T1 atoms backfilled = ~83pct of 144 target
- Functional analysis remainder algebra-tagged (BLO + compact + dual + weak topology + Sobolev + Schwartz + distributions + reflexive + separable + Hahn-Banach = functional-analysis substrate)

## BATCH 13-14 queued (24 atoms remaining)

- BATCH 13 (graph theory + combinatorics T1)
- BATCH 14 (numerical methods + remaining T1)

## Cross-references

- BATCH 01-11 predecessors

---

**Testbed:** T1 ALGEBRA-DICT BACKFILL BATCH 12 10 functional analysis remainder atoms INGEST-READY YAML bounded_linear_operator + compact_operator + dual_space + weak_topology + sobolev_space + schwartz_space + distribution_generalized_function + reflexive_space + separable_space + hahn_banach_theorem + cumulative 120 atoms 83pct of 144 target + functional analysis substrate algebra-tagged + BATCH 13-14 queued 24 remaining + USER full-auto overnight continuing.
