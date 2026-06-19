# Research -> Testbed: T1 algebra BATCH 16 supplementary -- 6 atoms gap-fill for original Curry-Howard drill BATCH-02 spec -- L6-PROOF unblock -- INGEST-READY YAML

**From:** Research  **Date:** 2026-06-13 (Cycle 51 close + USER full-auto overnight)
**Re:** Coverage gap on original Curry-Howard drill BATCH-02 30-atom spec (5-6 missing); ensures L6-PROOF G3 mutual_information chain runs through explicit probability-foundation atoms

## Batch 16 -- 6 supplementary atoms

```yaml
- canonical_name: monotonicity
  aliases: [monotone_function, monotonically_increasing_or_decreasing]
  tier: T1
  partition: math_foundation
  science_algebra_category: analysis::order_properties
  algebra_dict:
    definition_increasing: "f is monotonically increasing iff x <= y implies f(x) <= f(y)"
    definition_decreasing: "f is monotonically decreasing iff x <= y implies f(x) >= f(y)"
    strict_variants: strict_inequalities_for_strict_monotonicity
    properties: [composition_of_increasing_is_increasing, derivative_sign_test_when_differentiable, monotone_function_a_s_continuous]
    examples: [exponential_increasing, logarithm_increasing, square_on_non_negative_increasing, expectation_under_stochastic_dominance]
    related: [convex_function, concave_function, mean_value_theorem, derivative]
    is_axiom: false
  depends_on: [mean_value_theorem, derivative]
  serves_capability: [monotone_function_substrate, stochastic_dominance, expectation_monotonicity, jensen_inequality_proof_lemma]
  signature_hint: order_preserving_or_reversing_map

- canonical_name: chain_rule_probability
  aliases: [probability_chain_rule, joint_decomposition]
  tier: T1
  partition: math_foundation
  science_algebra_category: probability_theory::conditioning
  algebra_dict:
    formula: "P(X_1, X_2, ..., X_n) = P(X_1) * P(X_2 | X_1) * P(X_3 | X_1, X_2) * ... * P(X_n | X_1, ..., X_{n-1})"
    binary_case: "P(A, B) = P(A) * P(B | A) = P(B) * P(A | B)"
    role: decompose_joint_distribution_into_chain_of_conditionals_used_throughout_bayesian_networks_HMM_decoding
    related: [conditional_probability, joint_distribution, bayes_rule, chain_rule_entropy, hidden_markov_model]
    is_axiom: false
  depends_on: [conditional_probability, probability_space]
  serves_capability: [bayesian_network_substrate, sequence_decomposition, joint_factoring, L6_PROOF_G3_chain]
  signature_hint: joint_factors_into_conditional_chain

- canonical_name: total_probability
  aliases: [law_of_total_probability, marginalization_via_partition]
  tier: T1
  partition: math_foundation
  science_algebra_category: probability_theory::conditioning
  algebra_dict:
    statement: "for disjoint partition {B_i} of sample space with P(B_i) > 0, P(A) = sum_i P(A | B_i) * P(B_i)"
    role: compute_marginal_via_conditional_chain_through_partition_used_in_bayes_rule_denominator
    examples: [bayes_marginal_likelihood_computation, mixture_model_marginal_density]
    related: [conditional_probability, bayes_rule, partition, marginal_distribution]
    is_axiom: false
  depends_on: [conditional_probability, probability_space, sigma_algebra]
  serves_capability: [marginal_computation_substrate, bayes_rule_denominator, mixture_model_substrate]
  signature_hint: marginal_via_conditional_partition_sum

- canonical_name: marginal_distribution
  aliases: [marginal_pdf_or_pmf, single_variable_distribution_from_joint]
  tier: T1
  partition: math_foundation
  science_algebra_category: probability_theory::distributions
  algebra_dict:
    discrete_formula: "P(X = x) = sum_y P(X = x, Y = y)"
    continuous_formula: "p_X(x) = integral p_X_Y(x, y) dy"
    relation_to_joint: marginal_eq_sum_or_integral_of_joint_over_other_variables
    related: [joint_distribution, conditional_probability, total_probability, fubini_tonelli]
    is_axiom: false
  depends_on: [random_variable, total_probability, fubini_tonelli]
  serves_capability: [marginal_inference_substrate, posterior_marginalization, variable_elimination_substrate]
  signature_hint: sum_or_integrate_joint_over_other_variables

- canonical_name: joint_distribution
  aliases: [joint_pdf_or_pmf, multivariate_distribution]
  tier: T1
  partition: math_foundation
  science_algebra_category: probability_theory::distributions
  algebra_dict:
    definition_discrete: "P(X_1 = x_1, ..., X_n = x_n) over product space"
    definition_continuous: "joint density p_X_1...X_n(x_1, ..., x_n) over R^n"
    properties: [non_negative, integrates_or_sums_to_1, factors_under_independence]
    relation_to_marginal_conditional: [marginal_via_summing_or_integrating_out_variables, conditional_via_joint_divided_by_marginal]
    related: [random_variable, marginal_distribution, conditional_probability, independence_probability, chain_rule_probability]
    is_axiom: false
  depends_on: [random_variable, probability_space, sigma_algebra]
  serves_capability: [multivariate_modeling_substrate, dependence_substrate, joint_inference]
  signature_hint: distribution_over_multiple_variables_jointly

- canonical_name: conditional_independence
  aliases: [CI, X_perp_Y_given_Z]
  tier: T1
  partition: math_foundation
  science_algebra_category: probability_theory::dependence_structure
  algebra_dict:
    definition: "X and Y are conditionally independent given Z iff P(X, Y | Z) = P(X | Z) * P(Y | Z)"
    equivalent: P_X_given_Y_Z_eq_P_X_given_Z_when_P_Y_Z_gt_0
    role: foundational_for_graphical_models_dseparation_bayesian_network_factorization_markov_property
    examples: [markov_blanket, causal_independence_separation, hidden_markov_model_state_separation]
    related: [independence_probability, conditional_probability, graphical_model, bayesian_network, markov_chain]
    is_axiom: false
  depends_on: [conditional_probability, independence_probability, joint_distribution]
  serves_capability: [graphical_model_substrate, bayesian_network_d_separation, markov_blanket_substrate]
  signature_hint: independence_factoring_under_conditioning
```

## Cumulative coverage post BATCH 16

- 150 T1 atoms backfilled across BATCH 01-16 (144 base + 6 supplementary)
- BATCH-02 30-atom spec from original Curry-Howard drill now FULLY COVERED (24-25 explicit in BATCH 01-15 + 5-6 supplementary in BATCH 16)
- L6-PROOF G3 mutual_information chain now has explicit chain_rule_probability + total_probability + joint_distribution + marginal_distribution as bridging atoms
- conditional_independence enables graphical model + Bayesian network substrate extensions (Cycle 52 candidate)

## Depth-2 DEPENDS_ON for BATCH 16

Each atom carries explicit `depends_on:` field at filing time (depth-1) for Testbed ingest convenience. Per BATCH 15 convention, prerequisite atoms have their own recursive DEPENDS_ON.

## Testbed ingest checklist

1. Verify absence of each canonical_name in substrate
2. Ingest with full algebra_dict + science_algebra_category + serves_capability + depends_on per Q2+Q3 convention
3. Author DEPENDS_ON edges per depends_on field
4. Report rejected for catalog refinement
5. After ingest, BATCH-02 30-atom spec L6-PROOF corpus precondition COMPLETE (per Exp-Dev L6-PROOF gating question)

## Routing

- **Testbed**: BATCH 16 ingest priority HIGH (unblocks Exp-Dev L6-PROOF cell on remote queue)
- **Exp-Dev**: L6-PROOF cell can start once Testbed BATCH 16 ingest lands (combined with BATCH 01 + 03 + 05 + 10 + 15)
- **Research**: standing; T1 algebra BATCH 01-16 now total 150 atoms

## Cross-references

- notes/research_to_exp_dev_RESUME_REMOTE_QUEUE_ACK_plus_BATCH_02_COVERAGE_*.md (BATCH-02 gap analysis source)
- notes/exp_dev_to_research_RESUMING_queued_handoffs_on_REMOTE_desktop_heat_was_laptop_only_2026-06-13.md (Exp-Dev resume + L6-PROOF BATCH-02 question)
- notes/research_drill_curry_howard_atoms_as_types_*.md (drill cell BATCH-02 30-atom spec source)
- BATCH 01-15 predecessors

---

**Testbed:** T1 ALGEBRA BATCH 16 SUPPLEMENTARY 6 BATCH-02 gap-fill atoms INGEST-READY YAML monotonicity + chain_rule_probability + total_probability + marginal_distribution + joint_distribution + conditional_independence with science_algebra_category + serves_capability + depends_on + L6-PROOF G3 mutual_information chain explicit bridging unblocked + Cumulative 150 atoms across BATCH 01-16 + BATCH-02 30-atom spec L6-PROOF corpus precondition COMPLETE per Exp-Dev L6-PROOF gating question + USER full-auto overnight continuing.
