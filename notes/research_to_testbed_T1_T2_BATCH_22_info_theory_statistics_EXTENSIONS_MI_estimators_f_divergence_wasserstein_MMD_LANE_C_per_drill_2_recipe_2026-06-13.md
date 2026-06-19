# Research -> Testbed: T1+T2 BATCH 22 -- 10 info-theory + statistics extension atoms -- LANE C per drill #2 recipe -- INGEST-READY

**From:** Research (guiding session)  **Date:** 2026-06-13 (Cycle 51 close + USER full-auto overnight)
**Re:** MASTER PLAN LANE C BATCH 22 deliverable; info-theory + statistics extensions per drill #2 recipe

## Batch 22 -- 10 atoms (info theory + statistics extensions)

```yaml
- canonical_name: mutual_information_estimator_NCE
  aliases: [InfoNCE, contrastive_MI_estimator, noise_contrastive_estimation]
  tier: T2
  partition: math_foundation::information_theory
  science_algebra_category: information_theory::estimators
  algebra_dict:
    formula: "I_NCE = E[log(f(x,y) / (f(x,y) + sum_neg f(x, y_neg)))]"
    role: lower_bound_on_mutual_information_via_contrastive_classification
    related: [mutual_information, cross_entropy, softmax_function]
    is_axiom: false
  depends_on: [mutual_information, cross_entropy, softmax_function]
  serves_capability: [contrastive_learning, self_supervised_representation_learning, CPC]
  signature_hint: contrastive_classification_MI_lower_bound

- canonical_name: mutual_information_estimator_MINE
  aliases: [MINE, neural_MI_estimator, Donsker_Varadhan_MI]
  tier: T2
  partition: math_foundation::information_theory
  science_algebra_category: information_theory::estimators
  algebra_dict:
    formula: "I_MINE = sup_T [E_p(x,y)[T(x,y)] - log E_p(x)p(y)[exp T(x,y)]]"
    derivation: Donsker_Varadhan_variational_representation_of_KL
    related: [mutual_information, kl_divergence, variational_inference]
    is_axiom: false
  depends_on: [mutual_information, kl_divergence, variational_inference]
  serves_capability: [neural_MI_estimation, representation_learning]
  signature_hint: Donsker_Varadhan_neural_MI

- canonical_name: variational_information_bottleneck
  aliases: [VIB, information_bottleneck_VAE_style]
  tier: T2
  partition: math_foundation::information_theory
  science_algebra_category: information_theory::compression
  algebra_dict:
    formula: "min I(X;Z) - beta * I(Z;Y); maximize predictive MI while minimizing input MI"
    role: principled_representation_learning_balancing_compression_and_prediction
    related: [mutual_information, kl_divergence, variational_inference, evidence_lower_bound_ELBO]
    is_axiom: false
  depends_on: [mutual_information, kl_divergence, variational_inference]
  serves_capability: [disentangled_representation_learning, compressed_representations]
  signature_hint: tradeoff_input_MI_vs_target_MI

- canonical_name: f_divergence_family
  aliases: [f_divergence, Csiszar_divergence_family]
  tier: T2
  partition: math_foundation::information_theory
  science_algebra_category: information_theory::divergence
  algebra_dict:
    formula: "D_f(P||Q) = integral q(x) f(p(x)/q(x)) dx; f convex with f(1)=0"
    members: [KL_divergence_f_eq_t_log_t, reverse_KL_f_eq_minus_log_t, JS_divergence_f_eq_t_log_t_minus_t_plus_1_log_t_plus_1_over_2, total_variation_f_eq_abs_t_minus_1_over_2, chi_squared_f_eq_t_minus_1_squared]
    properties: [non_negative_by_jensen, generalized_KL_family, used_in_GAN_objectives]
    related: [kl_divergence, jensen_shannon_divergence, total_variation_distance, convex_function]
    is_axiom: false
  depends_on: [convex_function, jensen_inequality, kl_divergence]
  serves_capability: [unified_divergence_family, GAN_objective_design, statistical_distance_substrate]
  signature_hint: convex_f_pq_ratio_q_integration

- canonical_name: wasserstein_distance
  aliases: [optimal_transport_distance, earth_mover_distance, W_p]
  tier: T2
  partition: math_foundation::probability_theory
  science_algebra_category: probability_theory::optimal_transport
  algebra_dict:
    formula: "W_p(mu, nu) = (inf_{pi in Pi(mu,nu)} E[d(X,Y)^p])^(1/p)"
    properties: [metric_on_probability_measures, continuous_wrt_weak_convergence, sensitive_to_geometry_via_d]
    dual_form: kantorovich_rubinstein_W_1_eq_sup_lipschitz_1_E_f_mu_minus_E_f_nu
    related: [optimal_transport, monge_kantorovich_duality, lipschitz_continuity, metric_space]
    is_axiom: false
  depends_on: [metric_space, expectation, lipschitz_continuity, measurable_function]
  serves_capability: [optimal_transport_substrate, WGAN, distributional_alignment]
  signature_hint: inf_coupling_expected_distance

- canonical_name: maximum_mean_discrepancy
  aliases: [MMD, two_sample_test_kernel]
  tier: T2
  partition: math_foundation::probability_theory
  science_algebra_category: probability_theory::two_sample_tests
  algebra_dict:
    formula: "MMD^2(P, Q) = ||mu_P - mu_Q||^2_H = E_xx'[k(x,x')] + E_yy'[k(y,y')] - 2 E_xy[k(x,y)]"
    role: two_sample_test_via_kernel_mean_embedding_in_RKHS
    properties: [characteristic_kernel_yields_MMD_eq_0_iff_P_eq_Q, computable_from_samples, used_in_kernel_two_sample_tests]
    related: [reproducing_kernel_hilbert_space, kernel_methods, wasserstein_distance, two_sample_test]
    is_axiom: false
  depends_on: [reproducing_kernel_hilbert_space, expectation, inner_product]
  serves_capability: [two_sample_testing, generative_model_evaluation, kernel_distributional_distance]
  signature_hint: kernel_mean_embedding_distance_RKHS

- canonical_name: ranking_loss
  aliases: [pairwise_ranking_loss, learning_to_rank_loss]
  tier: T2
  partition: math_foundation::machine_learning
  science_algebra_category: machine_learning::loss_functions
  algebra_dict:
    formula: "L = sum_{(i,j) : y_i > y_j} max(0, m - (s_i - s_j))"
    variants: [pairwise_hinge, RankNet_logistic, RankSVM]
    use_cases: [learning_to_rank_information_retrieval, recommender_systems, search_relevance]
    related: [hinge_loss_concept, pairwise_comparison]
    is_axiom: false
  depends_on: [convex_function, gradient_descent]
  serves_capability: [learning_to_rank_substrate, IR_substrate, recommender_substrate]
  signature_hint: pairwise_margin_hinge_loss

- canonical_name: bradley_terry_model
  aliases: [BT_model, pairwise_logistic_preference_model]
  tier: T2
  partition: math_foundation::probability_theory
  science_algebra_category: probability_theory::pairwise_models
  algebra_dict:
    formula: "P(i beats j) = exp(theta_i) / (exp(theta_i) + exp(theta_j))"
    use_cases: [chess_ELO_rating, RLHF_preference_modeling, pairwise_preference_learning]
    properties: [logistic_in_skill_differences, identifiable_up_to_shift_of_thetas]
    related: [logistic_regression, plackett_luce_model, maximum_likelihood, ranking_loss]
    is_axiom: false
  depends_on: [softmax_function, maximum_likelihood, conditional_probability]
  serves_capability: [pairwise_preference_modeling, RLHF_reward_modeling, rating_systems]
  signature_hint: logistic_skill_difference_preference_probability

- canonical_name: plackett_luce_model
  aliases: [PL_model, listwise_ranking_model]
  tier: T2
  partition: math_foundation::probability_theory
  science_algebra_category: probability_theory::pairwise_models
  algebra_dict:
    formula: "P(pi | theta) = prod_t exp(theta_{pi(t)}) / sum_{j in remaining} exp(theta_j)"
    generalization: bradley_terry_to_listwise_ranking
    use_cases: [listwise_LTR, multi_agent_preference_aggregation, choice_modeling]
    related: [bradley_terry_model, softmax_function, ranking_loss]
    is_axiom: false
  depends_on: [bradley_terry_model, softmax_function, conditional_probability]
  serves_capability: [listwise_ranking_substrate, multi_agent_preference, choice_modeling_substrate]
  signature_hint: sequential_softmax_listwise_ranking

- canonical_name: total_variation_distance
  aliases: [TV_distance, statistical_distance]
  tier: T2
  partition: math_foundation::probability_theory
  science_algebra_category: probability_theory::distance_measures
  algebra_dict:
    formula: "TV(P, Q) = (1/2) sum_x |p(x) - q(x)| = sup_A |P(A) - Q(A)|"
    properties: [metric_on_probability_measures, bounded_in_0_1, weaker_than_KL_pinsker_inequality]
    related: [kl_divergence, jensen_shannon_divergence, wasserstein_distance, f_divergence_family]
    is_axiom: false
  depends_on: [absolute_continuity_of_measures, expectation, sigma_algebra]
  serves_capability: [statistical_distance_substrate, coupling_inequalities, mixing_time_analysis]
  signature_hint: sum_absolute_density_difference_over_2
```

## SHARES_MATH equivalence-class amortization

Four SHARES_MATH groups in BATCH 22:
- **MI-estimator family**: {mutual_information_estimator_NCE, mutual_information_estimator_MINE} (SHARES_MATH neural-MI-bound)
- **Divergence-family family**: {f_divergence_family, kl_divergence, jensen_shannon_divergence, total_variation_distance} (SHARES_MATH non-negative-probability-distance)
- **Distance-via-kernel family**: {wasserstein_distance, maximum_mean_discrepancy} (SHARES_MATH probability-measure-distance)
- **Pairwise-preference family**: {bradley_terry_model, plackett_luce_model} (SHARES_MATH softmax-skill-difference)

## Cumulative coverage post BATCH 22

- 10 NEW atoms (all T2)
- ~30-40 new DEPENDS_ON edges
- 4 SHARES_MATH equivalence class seeds
- Info-theory + statistics extensions for modern ML substrate

## Cumulative LANE C BATCH 17-22

- Total atoms: 66 + 10 = **76 atoms** (95pct of 80-atom drill #2 recipe plan)
- 15+ SHARES_MATH equivalence class seeds across BATCH 19-22
- BATCH 23-25 ~4 atoms remaining (deep chains 8-10 hops; alternative would extend to ~30+ more for richer Tier 4)

## Deep chains enabled post BATCH 22

- f_divergence_family -> jensen_inequality -> log_concavity -> concave_function -> axioms (depth 4)
- wasserstein_distance -> metric_space -> non_negativity -> axioms (depth 3-4)
- variational_information_bottleneck -> variational_inference -> kl_divergence -> jensen_inequality -> log_concavity -> axioms (depth 5)
- maximum_mean_discrepancy -> reproducing_kernel_hilbert_space -> hilbert_space -> banach_space -> completeness -> metric_space -> axioms (depth 6)

## Routing

- **Testbed**: BATCH 22 ingest T1.11
- **Exp-Dev**: standing
- **Research**: BATCH 23-25 deep chains 8-10 hops next OR pivot to recursive self-improvement loop Stage 3-6 spec (Phase 3 R3.1) -- depends on Testbed throughput

---

**Testbed:** T1+T2 BATCH 22 10 info-theory + statistics extension atoms INGEST-READY NCE + MINE + VIB + f_divergence + Wasserstein + MMD + ranking_loss + Bradley-Terry + Plackett-Luce + total_variation + 4 SHARES_MATH equivalence class seeds + cumulative LANE C 76/80 atoms 95pct of drill recipe plan + USER full-auto overnight continuing.
