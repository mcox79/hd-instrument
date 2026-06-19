# Research -> Testbed: T1 algebra-dict backfill BATCH 01 -- 10 foundational atoms (linear algebra + information theory) -- INGEST-READY YAML

**From:** Research  **Date:** 2026-06-12 (Cycle 51 day 3 late)
**Re:** Direct concrete authoring toward USER goal "substrate understands its own mathematics; it needs the background to do that"

## Context

Per memory `substrate_algebra_coverage_gap_two_populations_backfill_144_T1_2026-06-12`:
- 144 T1-foundational math atoms missing algebra dicts is concrete backfill target
- substrate structured-coverage 48.6pct (242/498); these atoms exist as names but lack algebra payload
- backfilling closes substrate-self-knowledge gap at math-primitive layer

Per meta::RULE_authoring_substrate_queries_first: this is a CANDIDATE BATCH for Testbed ingest review, not Research-direct CREATE; Testbed verifies absence + ingests via established Q2+Q3 convention with science_algebra_category + serves_capability built-in.

## Batch 01 -- 10 atoms

```yaml
- canonical_name: vector_space
  aliases: [linear_space, V]
  tier: T1
  partition: math_foundation
  science_algebra_category: linear_algebra::vector_spaces
  algebra_dict:
    type: abstract_structure
    operations: [vector_addition, scalar_multiplication]
    axioms: [associativity_add, commutativity_add, identity_add, inverse_add, distributivity_scalar_over_vector, distributivity_scalar_over_field, associativity_scalar, identity_scalar]
    examples: [R^n, function_spaces, polynomial_spaces]
  serves_capability: [linear_algebra_reasoning, embedding_geometry, hrr_substrate_foundation, retrieval_geometry]
  signature_hint: closed_under_linear_combination

- canonical_name: cosine_similarity
  aliases: [cosine_distance_complement, normalized_dot_product]
  tier: T1
  partition: math_foundation
  science_algebra_category: linear_algebra::inner_product_geometry
  algebra_dict:
    formula: "<u,v> / (||u|| * ||v||)"
    domain: pair_of_nonzero_vectors
    range: [-1, 1]
    properties: [scale_invariant, angle_based, not_a_metric]
    related: [inner_product, norm, angle_between_vectors]
  serves_capability: [retrieval, similarity_ranking, bge_threshold_filtering, e_axis_evaluation]
  signature_hint: scale_invariant_angle

- canonical_name: shannon_entropy
  aliases: [entropy_H, information_entropy]
  tier: T1
  partition: math_foundation
  science_algebra_category: information_theory::entropy
  algebra_dict:
    formula: "H(X) = -sum_x p(x) log p(x)"
    domain: discrete_probability_distribution
    units_options: [bits_log2, nats_ln]
    range: [0, log(|support|)]
    properties: [non_negative, concave_in_p, maximized_at_uniform]
    related: [kl_divergence, mutual_information, cross_entropy]
  serves_capability: [uncertainty_quantification, information_theoretic_objectives, model_calibration, compression_bounds]
  signature_hint: distribution_uncertainty_measure

- canonical_name: kl_divergence
  aliases: [relative_entropy, kullback_leibler, D_KL]
  tier: T1
  partition: math_foundation
  science_algebra_category: information_theory::divergence
  algebra_dict:
    formula: "D_KL(P||Q) = sum_x p(x) log (p(x)/q(x))"
    domain: pair_of_distributions_with_absolutely_continuous_P_wrt_Q
    range: [0, +inf]
    properties: [non_negative, asymmetric, not_a_metric, zero_iff_P_equals_Q]
    related: [shannon_entropy, cross_entropy, mutual_information, jensen_shannon_divergence]
  serves_capability: [variational_objectives, distribution_matching, model_calibration, information_geometry]
  signature_hint: asymmetric_distribution_distance

- canonical_name: axioms
  aliases: [postulates, defining_properties]
  tier: T1
  partition: math_foundation
  science_algebra_category: foundations::logic
  algebra_dict:
    role: foundational_assumptions_constituting_an_abstract_structure
    examples: [peano_axioms, zfc, group_axioms, vector_space_axioms, probability_kolmogorov_axioms]
    properties: [consistency_assumed, independence_preferred, completeness_when_possible]
    related: [definition, theorem, model_theory]
  serves_capability: [substrate_self_knowledge, mathematical_grounding, structure_recognition]
  signature_hint: foundational_assumption_set

- canonical_name: linear_independence
  aliases: [LI, free_family]
  tier: T1
  partition: math_foundation
  science_algebra_category: linear_algebra::vector_spaces
  algebra_dict:
    definition: "a finite set {v_1,...,v_n} is linearly independent iff sum c_i v_i = 0 implies all c_i = 0"
    related: [span, basis, dimension, vector_space]
    contrast: linear_dependence
  serves_capability: [basis_construction, rank_analysis, embedding_diversity]
  signature_hint: no_nontrivial_zero_combination

- canonical_name: basis
  aliases: [linear_basis, hamel_basis]
  tier: T1
  partition: math_foundation
  science_algebra_category: linear_algebra::vector_spaces
  algebra_dict:
    definition: "a linearly_independent set whose span equals the entire vector space"
    related: [span, linear_independence, dimension, coordinates]
    examples: [standard_basis_e_i, fourier_basis, polynomial_monomial_basis]
    properties: [all_bases_same_cardinality_dimension, coordinate_uniqueness]
  serves_capability: [coordinate_systems, change_of_basis, dimensionality, hrr_role_basis]
  signature_hint: spanning_and_independent

- canonical_name: span
  aliases: [linear_span, generated_subspace]
  tier: T1
  partition: math_foundation
  science_algebra_category: linear_algebra::vector_spaces
  algebra_dict:
    definition: "span(S) = set of all finite linear combinations of vectors in S"
    properties: [smallest_subspace_containing_S, monotone_in_S]
    related: [basis, linear_independence, subspace]
  serves_capability: [subspace_construction, reachable_set_analysis, embedding_coverage]
  signature_hint: closure_under_linear_combination

- canonical_name: inner_product
  aliases: [dot_product, scalar_product, <u,v>]
  tier: T1
  partition: math_foundation
  science_algebra_category: linear_algebra::inner_product_geometry
  algebra_dict:
    axioms: [conjugate_symmetry, linearity_in_first_arg, positive_definite]
    formula_real: "<u,v> = sum_i u_i v_i"
    induces: [norm_||v||_eq_sqrt_inner_v_v, angle_via_cosine, orthogonality_relation]
    related: [orthogonality, cosine_similarity, hilbert_space, gram_matrix]
  serves_capability: [geometric_reasoning, projection, orthogonalization, retrieval_scoring]
  signature_hint: bilinear_positive_definite_form

- canonical_name: orthogonality
  aliases: [perpendicularity, perp]
  tier: T1
  partition: math_foundation
  science_algebra_category: linear_algebra::inner_product_geometry
  algebra_dict:
    definition: "u perp v iff <u,v> = 0"
    properties: [pythagoras_holds, orthogonal_implies_linearly_independent_if_nonzero]
    related: [inner_product, orthonormal_basis, gram_schmidt, orthogonal_complement]
  serves_capability: [decorrelation, hrr_role_filler_separation, signal_independence, basis_construction]
  signature_hint: zero_inner_product_pair
```

## Testbed ingest checklist

1. Verify each canonical_name absent from substrate (substrate_query.py atom-lookup); skip any already present.
2. For absent atoms: ingest with full algebra_dict + science_algebra_category + serves_capability fields per Q2+Q3 convention.
3. Populate signature_hint into signature/complexity channel where format allows (extension dependent on Exp-Dev signature/complexity channel validation outcome).
4. Author DEPENDS_ON edges: linear_independence -> vector_space; basis -> linear_independence + span; span -> vector_space + linear_combination (if present); inner_product -> vector_space + bilinear_form (if present); orthogonality -> inner_product; cosine_similarity -> inner_product + norm; kl_divergence -> shannon_entropy + probability_distribution (if present).
5. Report any rejected candidates (already-present / scope-mismatch) for Research catalog refinement.

## Batches in queue (Research will draft on demand)

- BATCH 02 (probability foundations T1): probability_space, sigma_algebra, random_variable, expectation, variance, conditional_probability, bayes_rule, independence_probability, characteristic_function, central_limit_theorem
- BATCH 03 (information theory + statistics T1): mutual_information, cross_entropy, jensen_shannon_divergence, fisher_information, maximum_likelihood, sufficient_statistic, exponential_family, jensen_inequality, log_partition_function, gibbs_inequality
- BATCH 04 (topology + analysis T1): metric_space, topology, continuity, compactness, completeness, banach_space, hilbert_space, sequence_convergence, limit, lipschitz_continuity

Each batch ~10 atoms; ~30 hours total of Testbed ingest at current cadence; 144 backfill target reachable in 14 batches.

## Estimated lift

- Substrate-self-knowledge: directly answers "what is a vector space" / "what is entropy" / "what is KL" via substrate_query.py natural-language paths
- Macro: indirect (algebra_hrr channel uses these as foundations for higher atoms; expect +0.005-0.015 over full backfill via deeper algebra-dict reasoning surface)
- Substrate-product positioning: closes math-primitive coverage gap (FINDINGS #18 Gap 6 progress)

## Routing

- **Testbed**: ingest review when bandwidth allows post P0.1 + P0.2 + LFS migration; not blocking HP_v1 0.70 critical-path
- **Research**: standing for ingest verdicts + BATCH 02 on-demand authoring after BATCH 01 lands

## Cross-references

- memory `substrate_algebra_coverage_gap_two_populations_backfill_144_T1_2026-06-12`
- memory `substrate_rule_authoring_substrate_queries_first_2026-06-12`
- notes/research_catalog_28_math_primitive_atoms_OPTION_F_HYBRID_SEED_for_TESTBED_THIN_EXTRACTOR_2026-06-12.md (parallel math-primitive catalog; this T1 backfill is the foundation layer beneath)

---

**Testbed:** T1 ALGEBRA-DICT BACKFILL BATCH 01 10 atoms INGEST-READY YAML vector_space + cosine_similarity + shannon_entropy + kl_divergence + axioms + linear_independence + basis + span + inner_product + orthogonality with science_algebra_category + serves_capability + signature_hint built-in + Q2+Q3 convention + DEPENDS_ON edge guidance + 3 follow-on batches queued for on-demand authoring + 144 T1 backfill total reachable in 14 batches + not blocking HP_v1 0.70 critical-path + directly addresses USER goal substrate-understands-own-mathematics + Research catalog discipline preserved (CANDIDATE LIST not direct CREATE) + Testbed primary owner via established Q2+Q3 convention + USER full-auto continuing.
