# Research -> Testbed: T1 algebra-dict backfill BATCH 07 -- 10 differential calculus atoms -- INGEST-READY YAML

**From:** Research  **Date:** 2026-06-12 (Cycle 51 close + USER full-auto overnight)
**Re:** T1 algebra backfill continuing toward 144 target; differential calculus foundation for optimization + ML primitives

## Batch 07 -- 10 atoms (differential calculus)

```yaml
- canonical_name: derivative
  aliases: [df_dx, derivative_at_point, instantaneous_rate_of_change]
  tier: T1
  partition: math_foundation
  science_algebra_category: analysis::calculus
  algebra_dict:
    definition_limit: "f'(a) = lim_{h -> 0} (f(a+h) - f(a)) / h, when this limit exists"
    geometric_interpretation: slope_of_tangent_line_at_a
    properties: [sum_rule, product_rule, quotient_rule, chain_rule_composition, mean_value_theorem]
    examples: [polynomial_power_rule_d_x_n_eq_n_x_n_minus_1, exponential_d_e_x_eq_e_x, logarithm_d_log_x_eq_1_over_x, trigonometric]
    related: [continuity, partial_derivative, gradient, taylor_series]
    is_axiom: false
  serves_capability: [optimization_first_order, calculus_foundation, gradient_descent_foundation]
  signature_hint: limit_of_difference_quotient

- canonical_name: gradient
  aliases: [nabla_f, grad_f, vector_of_partials]
  tier: T1
  partition: math_foundation
  science_algebra_category: analysis::multivariate_calculus
  algebra_dict:
    definition: "grad f = (d_f/d_x_1, d_f/d_x_2, ..., d_f/d_x_n); vector of partial derivatives"
    geometric_interpretation: direction_of_steepest_ascent_with_magnitude_eq_rate
    properties: [orthogonal_to_level_set, vanishes_at_critical_points, linearity_grad_a_f_plus_b_g_eq_a_grad_f_plus_b_grad_g]
    related: [partial_derivative, jacobian, directional_derivative, hessian, optimization]
    is_axiom: false
  serves_capability: [optimization_gradient_descent, ml_training_foundation, geometric_analysis]
  signature_hint: vector_of_first_order_partials

- canonical_name: jacobian
  aliases: [Df, jacobian_matrix, derivative_matrix]
  tier: T1
  partition: math_foundation
  science_algebra_category: analysis::multivariate_calculus
  algebra_dict:
    definition: "for f : R^n -> R^m, J_f is m x n matrix with entries (J_f)_ij = d_f_i / d_x_j"
    role: best_linear_approximation_at_a_point_f_x_plus_h_approx_f_x_plus_J_f_h
    properties: [chain_rule_matrix_product_form_J_g_circ_f_eq_J_g_J_f, determinant_is_local_volume_scaling_factor_when_n_eq_m]
    examples: [linear_map_jacobian_is_the_matrix_itself, change_of_variables_determinant]
    related: [gradient, derivative, hessian, chain_rule_calculus]
    is_axiom: false
  serves_capability: [multivariate_calculus_foundation, change_of_variables, ml_backprop_foundation]
  signature_hint: matrix_of_first_order_partials

- canonical_name: hessian
  aliases: [H_f, second_derivative_matrix, Hessian_matrix]
  tier: T1
  partition: math_foundation
  science_algebra_category: analysis::multivariate_calculus
  algebra_dict:
    definition: "for f : R^n -> R, H_f is n x n matrix with entries (H_f)_ij = d^2_f / d_x_i d_x_j; symmetric under continuity of second partials (Clairaut)"
    role: second_order_taylor_approximation_f_x_plus_h_approx_f_x_plus_grad_f_dot_h_plus_half_h_T_H_f_h
    second_order_optimality_conditions: [positive_definite_H_implies_local_minimum, negative_definite_implies_local_maximum, indefinite_implies_saddle]
    related: [gradient, jacobian, taylor_series, optimization_second_order_methods]
    is_axiom: false
  serves_capability: [second_order_optimization, curvature_analysis, newton_method_foundation]
  signature_hint: symmetric_matrix_of_second_partials

- canonical_name: chain_rule_calculus
  aliases: [chain_rule_derivative_composition, d_f_circ_g_dx]
  tier: T1
  partition: math_foundation
  science_algebra_category: analysis::calculus
  algebra_dict:
    single_variable: "d/dx [f(g(x))] = f'(g(x)) * g'(x)"
    multivariate: "for h = f circ g, J_h(x) = J_f(g(x)) * J_g(x)"
    backpropagation_role: vector_jacobian_product_recursive_application_through_computation_graph
    properties: [associativity_of_composition_inherited, generalizes_to_higher_order_via_faa_di_bruno]
    related: [derivative, gradient, jacobian, automatic_differentiation, backpropagation]
    is_axiom: false
  serves_capability: [neural_network_backprop_foundation, automatic_differentiation, composition_calculus]
  signature_hint: derivative_of_composition_factors

- canonical_name: taylor_series
  aliases: [taylor_expansion, polynomial_approximation_local]
  tier: T1
  partition: math_foundation
  science_algebra_category: analysis::calculus
  algebra_dict:
    formula: "f(x) = sum_{n=0}^inf (f^(n)(a) / n!) * (x - a)^n + R_n_remainder"
    multivariate_form: f_x_approx_f_x0_plus_grad_f_dot_x_minus_x0_plus_half_quadratic_form_hessian
    convergence: radius_of_convergence_R_finite_or_infinite_per_function
    remainder_forms: [lagrange_remainder, cauchy_remainder, integral_remainder]
    related: [derivative, hessian, analytic_function, taylor_polynomial, mean_value_theorem]
    is_axiom: false
  serves_capability: [local_approximation, perturbation_theory, smooth_function_analysis]
  signature_hint: polynomial_expansion_in_derivatives_at_basepoint

- canonical_name: partial_derivative
  aliases: [d_f_d_x_i, partial]
  tier: T1
  partition: math_foundation
  science_algebra_category: analysis::multivariate_calculus
  algebra_dict:
    definition: "d_f / d_x_i = derivative of f with respect to x_i holding all other variables constant"
    relationship: gradient_is_vector_of_partials_jacobian_is_matrix_of_partials
    clairaut_theorem: equality_of_mixed_partials_when_continuous_d_d_x_d_y_eq_d_d_y_d_x
    related: [derivative, gradient, jacobian, hessian, directional_derivative]
    is_axiom: false
  serves_capability: [multivariate_calculus_atom, gradient_construction, ml_training_foundation]
  signature_hint: derivative_holding_other_vars_fixed

- canonical_name: directional_derivative
  aliases: [D_v_f, derivative_along_direction]
  tier: T1
  partition: math_foundation
  science_algebra_category: analysis::multivariate_calculus
  algebra_dict:
    formula: "D_v f(x) = grad f(x) dot v_hat, where v_hat is unit vector"
    interpretation: rate_of_change_of_f_at_x_in_direction_v
    maximized_when: v_hat_parallel_grad_f
    related: [gradient, partial_derivative, derivative, normal_direction]
    is_axiom: false
  serves_capability: [optimization_search_direction, manifold_calculus, level_set_analysis]
  signature_hint: gradient_inner_product_with_unit_direction

- canonical_name: total_derivative
  aliases: [Df, total_differential]
  tier: T1
  partition: math_foundation
  science_algebra_category: analysis::multivariate_calculus
  algebra_dict:
    definition: "Df at x is the linear map L s.t. f(x + h) = f(x) + L(h) + o(||h||) as h -> 0"
    relation_to_jacobian: L_eq_J_f_x_as_matrix_in_chosen_basis
    relation_to_partials: total_diff_eq_sum_of_partials_times_variable_diff_when_variables_are_independent
    chain_rule_form: total_derivative_of_composition_is_composition_of_total_derivatives
    related: [jacobian, gradient, partial_derivative, differentiability]
    is_axiom: false
  serves_capability: [differentiability_concept, multivariate_chain_rule, manifold_calculus_foundation]
  signature_hint: best_linear_approximation_as_linear_map

- canonical_name: mean_value_theorem
  aliases: [MVT, lagrange_MVT]
  tier: T1
  partition: math_foundation
  science_algebra_category: analysis::calculus
  algebra_dict:
    statement: "f continuous on [a,b] differentiable on (a,b) implies exists c in (a,b) s.t. f'(c) = (f(b) - f(a)) / (b - a)"
    geometric_interpretation: tangent_line_parallel_to_secant_line_exists
    consequences: [monotonicity_via_sign_of_derivative, taylor_theorem_remainder_bounds, cauchy_MVT_generalization]
    related: [derivative, taylor_series, continuity, rolle_theorem]
    is_axiom: false
  serves_capability: [function_analysis_foundation, optimization_existence_results, calculus_corollaries]
  signature_hint: exists_point_where_derivative_eq_average_rate

```

## Cumulative coverage post BATCH 07

- 70 T1 atoms backfilled = ~49pct of 144 target (~half done)
- 7 layers: linear algebra + probability + info theory + statistics + topology + analysis + inequalities + convexity + abstract algebra + category theory + differential calculus
- ML/optimization foundation now algebra-tagged (gradient + hessian + chain_rule_calculus + jacobian = neural-network training math)

## BATCH 08+ queued

- BATCH 08 (numerical linear algebra T1): matrix_decomposition_general, SVD, eigendecomposition, QR_decomposition, LU_decomposition, cholesky, matrix_norm, condition_number, rank_revealing, pseudoinverse
- BATCH 09 (optimization T1): gradient_descent_concept, convex_optimization, KKT_conditions, lagrangian, duality_lagrangian, subgradient, stochastic_gradient_concept, line_search, trust_region, fixed_point_iteration
- BATCH 10+ (measure theory + stochastic processes + functional analysis remainder + ...)

## Routing

- Testbed BATCH 07 ingest when bandwidth allows
- Research BATCH 08+ on demand

## Cross-references

- BATCH 01-06 predecessors
- L6-PROOF coordination + Cycle 51 close synthesis

---

**Testbed:** T1 ALGEBRA-DICT BACKFILL BATCH 07 10 differential calculus atoms INGEST-READY YAML derivative + gradient + jacobian + hessian + chain_rule_calculus + taylor_series + partial_derivative + directional_derivative + total_derivative + mean_value_theorem + cumulative 70 atoms 49pct of 144 target halfway + ML/optimization foundation algebra-tagged + BATCH 08+ queued + USER full-auto overnight continuing.
