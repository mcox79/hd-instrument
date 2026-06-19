# Research -> Testbed: T1+T2 BATCH 19 -- 12 foundational ML primitives (transformer_attention + batchnorm + residual + adam + xentropy + etc) -- LANE C structural depth per drill #2 recipe -- INGEST-READY

**From:** Research (guiding session)  **Date:** 2026-06-13 (Cycle 51 close + USER full-auto overnight)
**Re:** MASTER PLAN Phase 2/3 LANE C BATCH 19 deliverable; foundational ML primitives per drill #2 prioritization recipe (high downstream_fanin + high cross_capability_breadth)

## Targeting rationale (per drill #2 recipe)

Foundational ML primitives have:
- **downstream_fanin** VERY HIGH: every transformer-based + neural-network-based capability DEPENDS_ON these
- **cross_capability_breadth** VERY HIGH: serve language modeling + computer vision + RL + recommendation + structured prediction
- **is_leaf** YES initially: currently leaf atoms in substrate; authoring deps to T1 atoms lifts proof chains
- **SHARES_MATH amortization** HIGH: groups (attention family + normalization family + optimizer family) compress as SHARES_MATH equivalence classes

Expected impact post BATCH 19 ingest: L6-PROOF FINDER avg depth + cross-capability coverage + KP P3 SHARES_MATH grouping seeds.

## Batch 19 -- 12 atoms (foundational ML primitives)

```yaml
- canonical_name: transformer_attention_mechanism
  aliases: [attention, self_attention, scaled_dot_product_attention]
  tier: T2
  partition: math_foundation::deep_learning
  science_algebra_category: deep_learning::attention
  algebra_dict:
    formula: "Attention(Q,K,V) = softmax(QK^T / sqrt(d_k)) V"
    properties: [permutation_equivariant_per_token, context_aware, parallel_computation]
    related: [multi_head_attention, softmax, dot_product, layer_normalization]
    is_axiom: false
  depends_on: [softmax_function, inner_product, matrix_decomposition, derivative]
  serves_capability: [language_modeling, sequence_to_sequence, computer_vision_transformer, structured_prediction_attention]
  signature_hint: softmax_weighted_value_aggregation

- canonical_name: multi_head_attention
  aliases: [MHA, parallel_attention_heads]
  tier: T2
  partition: math_foundation::deep_learning
  science_algebra_category: deep_learning::attention
  algebra_dict:
    formula: "MultiHead(Q,K,V) = Concat(head_1, ..., head_h) W^O where head_i = Attention(Q W_i^Q, K W_i^K, V W_i^V)"
    role: parallel_attention_subspaces_for_different_relations
    related: [transformer_attention_mechanism, linear_map, matrix_decomposition]
    is_axiom: false
  depends_on: [transformer_attention_mechanism, jacobian, vector_space]
  serves_capability: [language_modeling_multi_subspace, sequence_modeling, vision_transformer]
  signature_hint: parallel_attention_subspaces

- canonical_name: softmax_function
  aliases: [softmax, normalized_exponential]
  tier: T1
  partition: math_foundation::deep_learning
  science_algebra_category: deep_learning::activation
  algebra_dict:
    formula: "softmax(z)_i = exp(z_i) / sum_j exp(z_j)"
    properties: [sum_to_1, positive_outputs_probability_distribution, differentiable, max_extension_of_argmax]
    related: [cross_entropy_loss, exponential_family, log_partition_function]
    is_axiom: false
  depends_on: [exponential_family, log_partition_function, probability_space]
  serves_capability: [classification_output, attention_weights, multinomial_distribution_parameterization]
  signature_hint: probability_simplex_via_normalized_exponential

- canonical_name: batch_normalization
  aliases: [batchnorm, BN]
  tier: T2
  partition: math_foundation::deep_learning
  science_algebra_category: deep_learning::normalization
  algebra_dict:
    formula: "BN(x_i) = gamma * (x_i - mu_batch) / sqrt(sigma_batch^2 + eps) + beta"
    role: stabilize_training_via_per_minibatch_normalization
    related: [layer_normalization, weight_decay, gradient_descent, expectation, variance]
    is_axiom: false
  depends_on: [expectation, variance, gradient]
  serves_capability: [training_stability, deep_network_training, gradient_flow]
  signature_hint: per_batch_mean_variance_normalization

- canonical_name: layer_normalization
  aliases: [layernorm, LN]
  tier: T2
  partition: math_foundation::deep_learning
  science_algebra_category: deep_learning::normalization
  algebra_dict:
    formula: "LN(x) = gamma * (x - mu_layer) / sqrt(sigma_layer^2 + eps) + beta"
    role: normalize_per_layer_independent_of_batch_used_in_transformers
    properties: [batch_size_independent, sequence_length_independent, preserves_distribution_within_layer]
    related: [batch_normalization, transformer_attention_mechanism, expectation, variance]
    is_axiom: false
  depends_on: [expectation, variance, gradient]
  serves_capability: [transformer_training, autoregressive_models, sequence_models]
  signature_hint: per_layer_mean_variance_normalization

- canonical_name: residual_connection
  aliases: [skip_connection, ResNet_block, identity_shortcut]
  tier: T2
  partition: math_foundation::deep_learning
  science_algebra_category: deep_learning::architecture
  algebra_dict:
    formula: "y = F(x) + x; where F is learnable transformation"
    role: enables_training_of_very_deep_networks_via_identity_gradient_path
    properties: [gradient_vanishing_mitigation, identity_default_behavior, addition_in_vector_space]
    related: [batch_normalization, transformer_attention_mechanism, gradient_descent, vector_space]
    is_axiom: false
  depends_on: [vector_space, derivative, chain_rule_calculus]
  serves_capability: [deep_network_training, ResNet_architecture, transformer_architecture]
  signature_hint: identity_plus_residual_function

- canonical_name: dropout_regularization
  aliases: [dropout, stochastic_neurons_zeroing]
  tier: T2
  partition: math_foundation::deep_learning
  science_algebra_category: deep_learning::regularization
  algebra_dict:
    formula: "y = x * mask / (1 - p); mask_i ~ Bernoulli(1 - p)"
    role: prevent_overfitting_via_random_neuron_zeroing
    properties: [bayesian_approximation_via_mc_dropout, ensemble_approximation, scale_factor_during_training]
    related: [bernoulli_distribution, regularization, monte_carlo]
    is_axiom: false
  depends_on: [random_variable, bernoulli_distribution_concept_if_present, expectation]
  serves_capability: [overfitting_prevention, model_uncertainty_quantification, ensemble_approximation]
  signature_hint: stochastic_neuron_zeroing_during_training

- canonical_name: adam_optimizer
  aliases: [Adam, AdamW, adaptive_moment_estimation]
  tier: T2
  partition: math_foundation::optimization
  science_algebra_category: optimization::adaptive_first_order
  algebra_dict:
    formula: "m_t = beta_1 m_{t-1} + (1-beta_1) g_t; v_t = beta_2 v_{t-1} + (1-beta_2) g_t^2; theta_t = theta_{t-1} - eta * m_hat_t / (sqrt(v_hat_t) + eps)"
    properties: [per_parameter_adaptive_learning_rate, momentum_first_moment, second_moment_normalization, bias_corrected]
    related: [stochastic_gradient_descent, RMSProp, gradient_descent_momentum, exponential_moving_average]
    is_axiom: false
  depends_on: [stochastic_gradient_descent, gradient, expectation]
  serves_capability: [neural_network_training_default_optimizer, language_model_training, deep_learning_general]
  signature_hint: adaptive_first_second_moment_optimizer

- canonical_name: learning_rate_schedule
  aliases: [LR_schedule, learning_rate_decay, warmup]
  tier: T2
  partition: math_foundation::optimization
  science_algebra_category: optimization::learning_rate
  algebra_dict:
    schedules: [linear_warmup_then_decay, cosine_annealing, step_decay, constant, polynomial_decay, one_cycle]
    role: control_optimization_dynamics_via_time_varying_eta
    related: [stochastic_gradient_descent, adam_optimizer, line_search]
    is_axiom: false
  depends_on: [stochastic_gradient_descent, derivative]
  serves_capability: [training_stability, transformer_pretraining, neural_network_training_general]
  signature_hint: time_varying_step_size

- canonical_name: cross_entropy_loss
  aliases: [CE_loss, log_loss, supervised_classification_loss]
  tier: T2
  partition: math_foundation::deep_learning
  science_algebra_category: deep_learning::loss_functions
  algebra_dict:
    formula: "L = -sum_c y_c * log(p_c); where y is one-hot true label, p is softmax output"
    relation: cross_entropy_loss_minimization_equiv_maximum_likelihood_under_categorical
    properties: [convex_in_p, differentiable, calibrated_when_minimized]
    related: [cross_entropy, softmax_function, maximum_likelihood, categorical_distribution_concept]
    is_axiom: false
  depends_on: [cross_entropy, softmax_function, maximum_likelihood, expectation]
  serves_capability: [classification_training_default_loss, language_model_token_prediction, multinomial_classification]
  signature_hint: negative_log_likelihood_categorical

- canonical_name: xavier_initialization
  aliases: [Xavier_init, Glorot_init, normal_variance_scaling]
  tier: T2
  partition: math_foundation::deep_learning
  science_algebra_category: deep_learning::initialization
  algebra_dict:
    formula: "W ~ Uniform(-sqrt(6/(fan_in+fan_out)), +sqrt(6/(fan_in+fan_out)))"
    role: stabilize_variance_of_activations_through_layers_for_symmetric_activation_functions
    related: [he_initialization, batch_normalization, residual_connection, variance]
    is_axiom: false
  depends_on: [variance, random_variable, uniform_distribution_concept]
  serves_capability: [neural_network_training_initialization, gradient_flow_preservation]
  signature_hint: variance_scaled_uniform_initialization

- canonical_name: he_initialization
  aliases: [He_init, Kaiming_init, ReLU_init]
  tier: T2
  partition: math_foundation::deep_learning
  science_algebra_category: deep_learning::initialization
  algebra_dict:
    formula: "W ~ Normal(0, sqrt(2/fan_in))"
    role: variance_preserving_for_ReLU_activations_specifically
    related: [xavier_initialization, ReLU_activation_concept, variance, batch_normalization]
    is_axiom: false
  depends_on: [variance, random_variable, gaussian_distribution_concept]
  serves_capability: [ReLU_network_initialization, deep_network_training_with_ReLU]
  signature_hint: ReLU_aware_variance_preserving_initialization
```

## SHARES_MATH equivalence-class amortization (per drill #2 recipe)

Three high-confidence SHARES_MATH groups in BATCH 19 atoms:
- **Normalization family**: {batch_normalization, layer_normalization} (SHARES_MATH variance-mean-normalization)
- **Optimizer family**: {adam_optimizer, stochastic_gradient_descent, learning_rate_schedule} (SHARES_MATH first-order-stochastic-optimization)
- **Initialization family**: {xavier_initialization, he_initialization} (SHARES_MATH variance-preserving-initialization)

Per drill recipe: authoring 1 representative DEPENDS_ON-up-edge in each group transfers proof access to all family members via SHARES_MATH equivalence.

## Cumulative coverage post BATCH 19

- 12 NEW atoms (10 T2 + 1 T1 softmax_function + 1 T2 layer_normalization)
- ~40-50 new DEPENDS_ON edges
- 3 SHARES_MATH equivalence class seeds (normalization + optimizer + initialization)
- Foundational ML primitive coverage for transformer-based + neural-network-based capabilities

## L6-PROOF FINDER depth projection post BATCH 19

BATCH 18 already projected depth 3 -> 5-7. BATCH 19 adds 12 high-fanin atoms with depth-3+ chains:
- transformer_attention -> softmax_function -> exponential_family -> log_partition_function -> axioms (depth 4)
- batch_normalization -> variance -> expectation -> random_variable -> probability_space -> axioms (depth 5)
- adam_optimizer -> stochastic_gradient_descent -> gradient_descent -> gradient -> partial_derivative -> derivative -> limit -> sequence_convergence -> metric_space (depth 8)
- cross_entropy_loss -> cross_entropy -> kl_divergence -> jensen_inequality -> log_concavity -> concave_function -> axioms (depth 6)

KP P5_v1 (depth>=5) has multiple new HARD-PASS-eligible chains post BATCH 19 ingest.

## Routing

- **Testbed**: BATCH 19 ingest priority T1.8 (after T1.5 BATCH 17 + T1.7 BATCH 18); ~30-60 min ingest 12 atoms + 40-50 edges; SHARES_MATH equivalence-class authoring per drill #2 amortization
- **Exp-Dev**: standing for KP P5_v1 cell post BATCH 18 + 19 ingest; standing for L6-PROOF FINDER depth ceiling re-probe (3 -> 5-8 projected)
- **Research**: BATCH 20 NLU foundational atoms next (transformer_encoder/decoder + positional encoding + BPE + KV cache + cross_entropy_token + perplexity); LANE C continuing

## Cross-references

- notes/research_drill_L6_PROOF_FINDER_62pct_authoring_gap_leaf_prioritization_strategy_depth_corpus_expansion_2x_2026-06-13.md (drill #2 recipe source)
- notes/research_to_testbed_exp_dev_DRILL_2_VERDICT_*.md (BATCH 19-21 sequence outline)
- notes/research_to_testbed_T1_T2_BATCH_18_*.md (BATCH 18 deep chains predecessor)
- notes/research_to_testbed_exp_dev_MATH_SCIENCE_CORPUS_PARALLEL_INGEST_*.md (3-LANE coordination)

---

**Testbed:** T1+T2 BATCH 19 12 foundational ML primitives INGEST-READY transformer_attention_mechanism + multi_head_attention + softmax_function (T1) + batch_normalization + layer_normalization + residual_connection + dropout_regularization + adam_optimizer + learning_rate_schedule + cross_entropy_loss + xavier_initialization + he_initialization + 3 SHARES_MATH equivalence class seeds normalization + optimizer + initialization + drill #2 recipe high downstream_fanin + cross_capability_breadth + KP P5_v1 depth>=5 multiple HARD-PASS-eligible chains projected + USER full-auto overnight continuing.
