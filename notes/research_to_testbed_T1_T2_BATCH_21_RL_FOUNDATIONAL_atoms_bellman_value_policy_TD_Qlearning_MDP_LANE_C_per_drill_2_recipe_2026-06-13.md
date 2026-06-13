# Research -> Testbed: T1+T2 BATCH 21 -- 11 RL foundational atoms -- LANE C structural depth per drill #2 recipe -- INGEST-READY

**From:** Research (guiding session)  **Date:** 2026-06-13 (Cycle 51 close + USER full-auto overnight)
**Re:** MASTER PLAN LANE C BATCH 21 deliverable; RL foundational atoms per drill #2 recipe

## Batch 21 -- 11 atoms (RL foundational)

```yaml
- canonical_name: markov_decision_process
  aliases: [MDP, controlled_markov_process]
  tier: T1
  partition: math_foundation::reinforcement_learning
  science_algebra_category: reinforcement_learning::foundations
  algebra_dict:
    structure: tuple_S_A_P_R_gamma_with_S_states_A_actions_P_transition_prob_R_reward_gamma_discount
    properties: [markov_property_future_independent_of_past_given_present, optimality_via_dynamic_programming_bellman]
    examples: [gridworld, atari_games, robotic_control, recommender_systems]
    related: [markov_chain, dynamic_programming, bellman_equation, value_function]
    is_axiom: true
    note: foundational_axiom_RL_problem_formulation
  depends_on: [markov_chain, probability_space, axioms]
  serves_capability: [RL_problem_formulation, sequential_decision_making, optimal_control_substrate]
  signature_hint: 5_tuple_S_A_P_R_gamma_markov

- canonical_name: bellman_equation
  aliases: [bellman_recursion, value_recursion]
  tier: T2
  partition: math_foundation::reinforcement_learning
  science_algebra_category: reinforcement_learning::optimality_equations
  algebra_dict:
    formula: "V^pi(s) = sum_a pi(a|s) [R(s,a) + gamma sum_{s'} P(s'|s,a) V^pi(s')]"
    role: recursive_characterization_of_value_function_under_policy
    properties: [unique_fixed_point_via_contraction, basis_for_DP_algorithms]
    related: [bellman_optimality_equation, value_function, dynamic_programming, fixed_point_iteration]
    is_axiom: false
  depends_on: [markov_decision_process, dynamic_programming, fixed_point_iteration, conditional_probability]
  serves_capability: [value_function_computation, policy_evaluation, RL_algorithm_foundation]
  signature_hint: recursive_value_under_policy

- canonical_name: bellman_optimality_equation
  aliases: [bellman_max, V_star_recursion]
  tier: T2
  partition: math_foundation::reinforcement_learning
  science_algebra_category: reinforcement_learning::optimality_equations
  algebra_dict:
    formula: "V^*(s) = max_a [R(s,a) + gamma sum_{s'} P(s'|s,a) V^*(s')]"
    properties: [unique_fixed_point_via_contraction_when_gamma_lt_1, characterizes_optimal_policy_via_greedy]
    related: [bellman_equation, value_iteration, q_function, policy_iteration]
    is_axiom: false
  depends_on: [bellman_equation, fixed_point_iteration, dynamic_programming]
  serves_capability: [optimal_value_function, value_iteration_algorithm, optimal_policy_extraction]
  signature_hint: max_over_actions_value_recursion

- canonical_name: value_function
  aliases: [V_function, V_pi, state_value]
  tier: T2
  partition: math_foundation::reinforcement_learning
  science_algebra_category: reinforcement_learning::value_functions
  algebra_dict:
    definition: "V^pi(s) = E_pi[sum_t gamma^t R_t | s_0 = s]"
    role: expected_discounted_cumulative_reward_from_state_s_under_policy_pi
    properties: [bellman_recursion_holds, basis_for_policy_evaluation_and_improvement]
    related: [q_function, bellman_equation, expectation, markov_decision_process]
    is_axiom: false
  depends_on: [markov_decision_process, expectation, geometric_series_concept_if_present]
  serves_capability: [policy_evaluation, RL_substrate_value_estimation]
  signature_hint: expected_discounted_return_from_state

- canonical_name: q_function
  aliases: [Q_function, action_value_function, state_action_value]
  tier: T2
  partition: math_foundation::reinforcement_learning
  science_algebra_category: reinforcement_learning::value_functions
  algebra_dict:
    definition: "Q^pi(s, a) = E_pi[sum_t gamma^t R_t | s_0=s, a_0=a]"
    role: expected_discounted_cumulative_reward_from_state_s_taking_action_a_then_following_pi
    properties: [Q_star_satisfies_bellman_optimality_max_over_a, policy_extraction_via_greedy_argmax_Q]
    related: [value_function, bellman_optimality_equation, q_learning, temporal_difference_learning]
    is_axiom: false
  depends_on: [value_function, expectation, markov_decision_process]
  serves_capability: [q_learning_substrate, model_free_RL_foundation, deep_Q_network_substrate]
  signature_hint: expected_return_from_state_action_pair

- canonical_name: policy_gradient_REINFORCE
  aliases: [policy_gradient, REINFORCE, monte_carlo_policy_gradient]
  tier: T2
  partition: math_foundation::reinforcement_learning
  science_algebra_category: reinforcement_learning::policy_gradient
  algebra_dict:
    formula: "grad_theta J(theta) = E_pi_theta[sum_t grad_theta log pi_theta(a_t | s_t) * G_t]"
    role: stochastic_gradient_estimator_for_expected_return
    properties: [unbiased_estimator, high_variance_motivating_baseline_subtraction, on_policy]
    variants: [REINFORCE_with_baseline, actor_critic_replaces_G_t_with_advantage]
    related: [policy_function, advantage_function, value_function, stochastic_gradient_descent]
    is_axiom: false
  depends_on: [stochastic_gradient_descent, expectation, conditional_probability, gradient]
  serves_capability: [policy_optimization, deep_RL_substrate, on_policy_RL]
  signature_hint: log_policy_gradient_weighted_by_return

- canonical_name: advantage_function
  aliases: [A_function, advantage, A_pi]
  tier: T2
  partition: math_foundation::reinforcement_learning
  science_algebra_category: reinforcement_learning::value_functions
  algebra_dict:
    definition: "A^pi(s, a) = Q^pi(s, a) - V^pi(s)"
    role: relative_value_of_action_a_compared_to_average_under_policy
    properties: [reduces_variance_of_policy_gradient_estimator, zero_mean_under_policy]
    related: [q_function, value_function, policy_gradient_REINFORCE, actor_critic]
    is_axiom: false
  depends_on: [q_function, value_function, expectation]
  serves_capability: [variance_reduced_policy_gradient, actor_critic_substrate]
  signature_hint: action_value_minus_state_value

- canonical_name: temporal_difference_learning
  aliases: [TD_learning, TD_0, TD_lambda]
  tier: T2
  partition: math_foundation::reinforcement_learning
  science_algebra_category: reinforcement_learning::value_learning
  algebra_dict:
    update_rule: "V(s_t) <- V(s_t) + alpha [R_{t+1} + gamma V(s_{t+1}) - V(s_t)]"
    properties: [bootstraps_from_current_estimate, online_learning, lower_variance_than_monte_carlo, convergence_under_polyak_ruppert_or_decaying_alpha]
    related: [bellman_equation, value_function, q_learning, sarsa]
    is_axiom: false
  depends_on: [bellman_equation, value_function, fixed_point_iteration, stochastic_gradient_descent]
  serves_capability: [model_free_value_learning, online_RL_substrate, sample_efficient_value_estimation]
  signature_hint: bootstrap_value_update_one_step

- canonical_name: q_learning
  aliases: [Q_learning, off_policy_TD_control]
  tier: T2
  partition: math_foundation::reinforcement_learning
  science_algebra_category: reinforcement_learning::value_learning
  algebra_dict:
    update_rule: "Q(s_t, a_t) <- Q(s_t, a_t) + alpha [R_{t+1} + gamma max_a Q(s_{t+1}, a) - Q(s_t, a_t)]"
    properties: [off_policy_TD_control, converges_to_Q_star_under_GLIE_exploration, basis_for_deep_Q_network_DQN]
    related: [temporal_difference_learning, q_function, bellman_optimality_equation, epsilon_greedy]
    is_axiom: false
  depends_on: [temporal_difference_learning, q_function, bellman_optimality_equation]
  serves_capability: [off_policy_RL_substrate, deep_Q_network, atari_substrate]
  signature_hint: TD_with_max_over_next_action_off_policy

- canonical_name: policy_iteration
  aliases: [PI_algorithm, generalized_policy_iteration]
  tier: T2
  partition: math_foundation::reinforcement_learning
  science_algebra_category: reinforcement_learning::dp_algorithms
  algebra_dict:
    algorithm: alternate_policy_evaluation_compute_V_pi_via_bellman_eq + policy_improvement_pi_greedy_wrt_V
    properties: [monotone_improvement_of_policy_until_convergence, converges_to_optimal_policy_in_finite_MDPs_in_finitely_many_iterations]
    related: [value_iteration, bellman_equation, dynamic_programming]
    is_axiom: false
  depends_on: [bellman_equation, dynamic_programming, fixed_point_iteration]
  serves_capability: [planning_substrate_known_model, optimal_policy_finite_MDP, RL_baseline]
  signature_hint: alternate_evaluate_improve_until_stable

- canonical_name: value_iteration
  aliases: [VI_algorithm, bellman_iteration]
  tier: T2
  partition: math_foundation::reinforcement_learning
  science_algebra_category: reinforcement_learning::dp_algorithms
  algebra_dict:
    update_rule: "V_{k+1}(s) = max_a [R(s,a) + gamma sum_{s'} P(s'|s,a) V_k(s')]"
    properties: [contraction_under_gamma_lt_1, converges_geometrically_to_V_star, related_to_policy_iteration_via_partial_evaluation]
    related: [policy_iteration, bellman_optimality_equation, dynamic_programming, fixed_point_iteration]
    is_axiom: false
  depends_on: [bellman_optimality_equation, fixed_point_iteration, dynamic_programming]
  serves_capability: [planning_substrate, optimal_value_function_computation, RL_baseline]
  signature_hint: bellman_max_iteration_to_fixed_point
```

## SHARES_MATH equivalence-class amortization

Four high-confidence SHARES_MATH groups in BATCH 21:
- **Bellman family**: {bellman_equation, bellman_optimality_equation} (SHARES_MATH fixed-point-recursive-value)
- **Value-function family**: {value_function, q_function, advantage_function} (SHARES_MATH expected-discounted-return)
- **TD-control family**: {temporal_difference_learning, q_learning, sarsa-if-present} (SHARES_MATH bootstrap-value-update)
- **DP-algorithms family**: {policy_iteration, value_iteration} (SHARES_MATH iterate-bellman-to-fixed-point)

Per drill recipe: authoring 1 representative DEPENDS_ON-up-edge in each group transfers proof access via SHARES_MATH equivalence.

## Cumulative coverage post BATCH 21

- 11 NEW atoms (1 T1 markov_decision_process + 10 T2)
- ~30-40 new DEPENDS_ON edges
- 4 SHARES_MATH equivalence class seeds
- RL foundational coverage for value-based + policy-gradient methods

## Deep chains enabled post BATCH 21

- q_learning -> bellman_optimality_equation -> bellman_equation -> markov_decision_process -> markov_chain -> probability_space -> axioms (depth 7)
- policy_gradient_REINFORCE -> stochastic_gradient_descent -> gradient_descent -> gradient -> partial_derivative -> derivative -> limit -> sequence_convergence (depth 8)
- advantage_function -> q_function -> value_function -> markov_decision_process -> markov_chain -> probability_space -> axioms (depth 7)
- value_iteration -> bellman_optimality_equation -> fixed_point_iteration -> lipschitz_continuity -> continuity -> topology -> axioms (depth 7)

KP P5_v2 (depth>=7) HARD-PASS-eligible chains EMERGE post BATCH 21 ingest.

## Cumulative LANE C BATCH 17-21

- BATCH 17: depth-2 breadth + 4 new T1 atoms (recursion + optimal_substructure + DFT + complex_field)
- BATCH 18: 10 explicit deep chains 5-7 hop (math/probability/topology/functional analysis)
- BATCH 19: 12 foundational ML primitives (transformer_attention + softmax T1 + batch/layernorm + residual + dropout + adam + LR schedule + xentropy + xavier + he)
- BATCH 20: 11 NLU foundational atoms (transformer encoder/decoder + positional/RoPE + BPE/SP + masks + KV cache + token-level CE + PPL)
- BATCH 21: 11 RL foundational atoms (MDP T1 + bellman family + value family + TD family + DP family)

**Total LANE C cumulative**: 4 + 28 + 12 + 11 + 11 = **66 atoms** + ~150-200 explicit DEPENDS_ON edges + 11 SHARES_MATH equivalence class seeds.

Per drill #2 recipe target: 80 atoms BATCH 18-25 plan -> 66/80 = 82pct of LANE C plan shipped post BATCH 21. BATCH 22-25 (info theory extensions + 3 more deep-chain batches) ~14 atoms remaining.

## Routing

- **Testbed**: BATCH 21 ingest priority T1.10 (after BATCH 17/18/19/20)
- **Exp-Dev**: standing for KP P5_v1 + P5_v2 + L6-PROOF FINDER depth re-probe + CELL SC Option A scaling-curve study
- **Research**: BATCH 22 info-theory + statistics extensions next per drill #2 recipe (mutual_information estimators + variational_information_bottleneck + f_divergence + wasserstein + MMD + ranking_loss)

## Cross-references

- notes/research_to_testbed_T1_T2_BATCH_19_*.md (predecessor; ML primitives)
- notes/research_to_testbed_T1_T2_BATCH_20_*.md (predecessor; NLU foundational)
- notes/research_to_testbed_exp_dev_DRILL_2_VERDICT_*.md (BATCH 19-21 sequence outline)

---

**Testbed:** T1+T2 BATCH 21 11 RL foundational atoms INGEST-READY markov_decision_process T1 + bellman_equation + bellman_optimality_equation + value_function + q_function + policy_gradient_REINFORCE + advantage_function + temporal_difference_learning + q_learning + policy_iteration + value_iteration + 4 SHARES_MATH equivalence class seeds + multiple depth>=7 chains enabled for KP P5_v2 + cumulative LANE C BATCH 17-21 = 66 atoms 82pct of 80-atom plan + USER full-auto overnight continuing.
