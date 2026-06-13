# Research -> Testbed: T1 algebra-dict backfill BATCH 03 -- 10 information-theory + statistics atoms -- INGEST-READY YAML

**From:** Research  **Date:** 2026-06-12 (Cycle 51 day 3 late)
**Re:** T1 algebra backfill continuation; substrate-self-knowledge goal

## Batch 03 -- 10 atoms (information theory + statistics)

```yaml
- canonical_name: mutual_information
  aliases: [I_X_Y, MI]
  tier: T1
  partition: math_foundation
  science_algebra_category: information_theory::mutual_information
  algebra_dict:
    formula: "I(X;Y) = H(X) + H(Y) - H(X,Y) = D_KL(P_XY || P_X * P_Y)"
    properties: [non_negative, symmetric, zero_iff_independent, chain_rule]
    related: [shannon_entropy, kl_divergence, conditional_entropy, independence_probability]
  serves_capability: [feature_selection, information_bottleneck, dependency_measurement, representation_learning_foundation]
  signature_hint: kl_between_joint_and_product_of_marginals

- canonical_name: cross_entropy
  aliases: [H_P_Q, log_loss]
  tier: T1
  partition: math_foundation
  science_algebra_category: information_theory::divergence
  algebra_dict:
    formula: "H(P,Q) = -sum_x p(x) log q(x) = H(P) + D_KL(P||Q)"
    properties: [asymmetric_in_P_Q, lower_bound_H_P_when_Q_eq_P, used_as_supervised_loss]
    related: [shannon_entropy, kl_divergence, log_loss_classification]
  serves_capability: [classification_loss, supervised_training_objective, distribution_matching]
  signature_hint: expected_negative_log_q_under_p

- canonical_name: jensen_shannon_divergence
  aliases: [JSD, symmetric_KL_smoothed]
  tier: T1
  partition: math_foundation
  science_algebra_category: information_theory::divergence
  algebra_dict:
    formula: "JSD(P,Q) = (1/2) D_KL(P||M) + (1/2) D_KL(Q||M), M = (P+Q)/2"
    properties: [symmetric, bounded_by_log_2, square_root_is_a_true_metric]
    related: [kl_divergence, shannon_entropy, total_variation_distance]
  serves_capability: [symmetric_distribution_distance, gan_objective, embedding_distance_proper_metric]
  signature_hint: symmetric_kl_via_midpoint

- canonical_name: fisher_information
  aliases: [I_theta, score_variance]
  tier: T1
  partition: math_foundation
  science_algebra_category: statistics::information
  algebra_dict:
    formula: "I(theta) = E[(d/d_theta log p(X|theta))^2] = -E[d^2/d_theta^2 log p(X|theta)]"
    properties: [non_negative, additive_for_iid_samples, cramer_rao_lower_bound_on_unbiased_estimator_variance]
    related: [maximum_likelihood, cramer_rao_bound, information_geometry, score_function]
  serves_capability: [estimator_efficiency, information_geometry, natural_gradient_foundation]
  signature_hint: variance_of_score_function

- canonical_name: maximum_likelihood
  aliases: [MLE, hat_theta_MLE]
  tier: T1
  partition: math_foundation
  science_algebra_category: statistics::estimation
  algebra_dict:
    definition: "theta_hat = argmax_theta sum_i log p(x_i | theta)"
    properties: [consistent_under_regularity, asymptotically_normal, asymptotically_efficient_under_regularity, invariant_under_reparam]
    related: [fisher_information, cramer_rao_bound, likelihood_function, sufficient_statistic]
  serves_capability: [parameter_estimation, model_fitting, log_loss_minimization_classification]
  signature_hint: argmax_of_log_likelihood

- canonical_name: sufficient_statistic
  aliases: [T_X_carrying_all_inference, fisher_neyman_factorization]
  tier: T1
  partition: math_foundation
  science_algebra_category: statistics::sufficiency
  algebra_dict:
    definition: "T(X) sufficient for theta iff conditional distribution of X given T(X) does not depend on theta"
    fisher_neyman_factorization: "p(x|theta) = g(T(x), theta) * h(x)"
    related: [exponential_family, minimal_sufficient_statistic, rao_blackwell_theorem, maximum_likelihood]
  serves_capability: [dimensionality_reduction_inference, data_summarization, efficient_estimation]
  signature_hint: data_summary_preserving_likelihood_information

- canonical_name: exponential_family
  aliases: [natural_parameter_family, regular_family]
  tier: T1
  partition: math_foundation
  science_algebra_category: statistics::distribution_families
  algebra_dict:
    canonical_form: "p(x|eta) = h(x) exp(eta^T T(x) - A(eta))"
    members: [gaussian, bernoulli, categorical, poisson, gamma, beta, dirichlet, multivariate_gaussian_with_natural_params]
    properties: [T_X_is_sufficient_statistic, A_eta_is_log_partition_strictly_convex, gradient_of_A_equals_E_T_X, hessian_of_A_equals_cov_T_X]
    related: [sufficient_statistic, log_partition_function, fisher_information, conjugate_prior]
  serves_capability: [generalized_linear_models, variational_inference, conjugate_bayesian_inference]
  signature_hint: natural_param_inner_product_minus_log_partition

- canonical_name: jensen_inequality
  aliases: [E_phi_X_geq_phi_E_X_for_convex]
  tier: T1
  partition: math_foundation
  science_algebra_category: probability_theory::inequalities
  algebra_dict:
    statement: "phi convex => phi(E[X]) <= E[phi(X)]; phi concave => phi(E[X]) >= E[phi(X)]"
    consequences: [kl_non_negativity, log_concavity_for_evidence_lower_bound, generalized_means_inequality]
    related: [convexity, concavity, kl_divergence, ELBO_variational_inference]
  serves_capability: [variational_lower_bounds, kl_non_negativity_proof, inequality_derivations]
  signature_hint: convex_function_swap_inequality

- canonical_name: log_partition_function
  aliases: [cumulant_generating_function, A_eta, log_Z]
  tier: T1
  partition: math_foundation
  science_algebra_category: statistics::distribution_families
  algebra_dict:
    definition: "A(eta) = log integral h(x) exp(eta^T T(x)) dx"
    properties: [strictly_convex_in_eta, derivatives_give_cumulants_of_T_X, gradient_eq_E_T_X, hessian_eq_cov_T_X_eq_fisher_info]
    related: [exponential_family, fisher_information, partition_function_statistical_mechanics]
  serves_capability: [variational_inference, mean_field_approximation, normalizing_constant_estimation]
  signature_hint: cumulant_generator_of_sufficient_statistic

- canonical_name: gibbs_inequality
  aliases: [D_KL_geq_0_information_inequality]
  tier: T1
  partition: math_foundation
  science_algebra_category: information_theory::inequalities
  algebra_dict:
    statement: "D_KL(P || Q) >= 0 with equality iff P = Q (a.e.)"
    proof_sketch: jensen_inequality_applied_to_log
    consequences: [cross_entropy_lower_bound_eq_entropy, mle_consistency, information_processing_inequality]
    related: [kl_divergence, jensen_inequality, shannon_entropy, cross_entropy]
  serves_capability: [kl_non_negativity_proof, information_theoretic_lower_bounds, ELBO_derivation]
  signature_hint: non_negativity_of_kl_divergence
```

## Testbed ingest checklist (same protocol)

1. Verify absence; skip already-present.
2. Ingest with full algebra_dict + science_algebra_category + serves_capability.
3. signature_hint -> signature/complexity channel.
4. DEPENDS_ON edges per algebra_dict "related" field.
5. Report rejected for catalog refinement.

## Cross-references

- BATCH 01 + 02 predecessors
- BATCH 04 queue (topology + analysis T1): metric_space, topology, continuity, compactness, completeness, banach_space, hilbert_space, sequence_convergence, limit, lipschitz_continuity

## Cumulative coverage

- 30 T1 atoms backfilled = ~21pct of 144 target
- Three foundational layers covered: linear algebra + information theory + probability foundations + statistics
- Substrate self-knowledge now spans most-queried math primitives

---

**Testbed:** T1 ALGEBRA-DICT BACKFILL BATCH 03 10 info-theory + statistics atoms INGEST-READY YAML mutual_information + cross_entropy + jensen_shannon_divergence + fisher_information + maximum_likelihood + sufficient_statistic + exponential_family + jensen_inequality + log_partition_function + gibbs_inequality + cumulative 30 atoms 21pct of 144 target + BATCH 04 topology + analysis queued + USER full-auto continuing.
