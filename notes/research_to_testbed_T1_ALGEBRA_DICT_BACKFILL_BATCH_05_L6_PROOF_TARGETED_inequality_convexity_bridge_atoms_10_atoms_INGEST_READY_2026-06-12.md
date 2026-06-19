# Research -> Testbed: T1 algebra-dict backfill BATCH 05 -- 10 inequality + convexity bridge atoms TARGETED at L6-PROOF G1-G4 proof chains -- INGEST-READY YAML

**From:** Research  **Date:** 2026-06-12 (Cycle 51 close + USER full-auto overnight)
**Re:** BATCH 05 sequenced after L6-PROOF coordination ship; directly unblocks PHASE 3 verification cell once Testbed ships PHASE 2 substrate_query.py prove subcommand

## Targeting rationale

L6-PROOF PHASE 3 pre-reg cell requires algebra-dict coverage of bridging atoms in 4 proof chains:
- G1 orthogonality_implies_zero_inner_product (depth-2) -- BATCH 01 already has inner_product + orthogonality
- G2 KL_divergence_non_negative (depth-3 jensen + log_concavity) -- BATCH 03 has kl_divergence + jensen + gibbs; **MISSING log_concavity bridge**
- G3 mutual_information_non_negative (depth-4 KL + chain_rule + entropy) -- BATCH 03 has mutual_information + shannon_entropy; **MISSING chain_rule_entropy + conditional_entropy bridges**
- G4 Cauchy_Schwarz_in_inner_product_space (depth-3 inner_product + non_negativity + quadratic) -- **MISSING cauchy_schwarz + holders + minkowski**

BATCH 05 closes these gaps.

## Batch 05 -- 10 atoms (L6-PROOF bridge atoms)

```yaml
- canonical_name: cauchy_schwarz_inequality
  aliases: [CS_inequality, cauchy_bunyakovsky_schwarz]
  tier: T1
  partition: math_foundation
  science_algebra_category: analysis::inequalities
  algebra_dict:
    formula: "|<u,v>|^2 <= <u,u> * <v,v>"
    equivalent_norm_form: "|<u,v>| <= ||u|| * ||v||"
    equality_iff: u_and_v_linearly_dependent
    proof_sketch: non_negativity_of_quadratic_form_in_lambda_evaluated_via_inner_product_axioms
    properties: [tightest_for_aligned_vectors, bounds_correlation_in_probability_via_cov_E_XY_squared]
    related: [inner_product, norm, holders_inequality_p_eq_q_eq_2_case, triangle_inequality]
    is_axiom: false
    axioms: [inner_product_axioms, non_negativity, quadratic_form_minimization]
  serves_capability: [inner_product_geometry, correlation_bounds, L6_PROOF_G4_target]
  signature_hint: inner_product_bounded_by_norm_product

- canonical_name: log_concavity
  aliases: [log_concave_function, concave_log]
  tier: T1
  partition: math_foundation
  science_algebra_category: analysis::convexity
  algebra_dict:
    definition: "f is log-concave iff log(f) is concave (equivalently f(lambda x + (1-lambda) y) >= f(x)^lambda * f(y)^(1-lambda))"
    examples_log_concave: [gaussian_density, exponential_density, beta_density_alpha_beta_geq_1, log_function_itself]
    properties: [closed_under_marginalization, closed_under_convolution_with_log_concave, jensen_inequality_via_log_concavity]
    related: [concave_function, jensen_inequality, gaussian_distribution, exponential_family]
    is_axiom: false
    axioms: [concavity_definition, jensen_inequality, monotonicity_of_log]
  serves_capability: [variational_bounds, jensen_application_chains, L6_PROOF_G2_bridge]
  signature_hint: log_of_function_is_concave

- canonical_name: triangle_inequality
  aliases: [TI, subadditivity_of_norm_metric]
  tier: T1
  partition: math_foundation
  science_algebra_category: analysis::inequalities
  algebra_dict:
    norm_form: "||u + v|| <= ||u|| + ||v||"
    metric_form: "d(x,z) <= d(x,y) + d(y,z)"
    reverse: "| ||u|| - ||v|| | <= ||u - v||"
    related: [norm, metric_space, cauchy_schwarz_inequality_proves_TI_in_inner_product_space, holders_inequality, minkowski_inequality]
    is_axiom: true
    note: foundational_axiom_of_norm_and_metric_space
  serves_capability: [metric_foundations, optimization_bounds, retrieval_distance_consistency]
  signature_hint: distance_sum_bounds_direct_distance

- canonical_name: holders_inequality
  aliases: [holder_inequality, p_q_conjugate_exponents]
  tier: T1
  partition: math_foundation
  science_algebra_category: analysis::inequalities
  algebra_dict:
    formula: "sum_i |a_i * b_i| <= (sum_i |a_i|^p)^(1/p) * (sum_i |b_i|^q)^(1/q), where 1/p + 1/q = 1, p,q >= 1"
    integral_form: "integral |f g| <= (integral |f|^p)^(1/p) * (integral |g|^q)^(1/q)"
    special_case_p_q_2: cauchy_schwarz_inequality
    related: [L_p_spaces, minkowski_inequality, conjugate_exponents, cauchy_schwarz_inequality]
    is_axiom: false
    axioms: [young_inequality, conjugate_exponents_definition, non_negativity]
  serves_capability: [L_p_norm_analysis, functional_analysis_foundations, generalization_of_CS]
  signature_hint: p_norm_q_norm_product_bound

- canonical_name: minkowski_inequality
  aliases: [minkowski_p_norm_triangle, L_p_triangle]
  tier: T1
  partition: math_foundation
  science_algebra_category: analysis::inequalities
  algebra_dict:
    formula: "(sum_i |a_i + b_i|^p)^(1/p) <= (sum_i |a_i|^p)^(1/p) + (sum_i |b_i|^p)^(1/p), p >= 1"
    integral_form: "||f + g||_p <= ||f||_p + ||g||_p"
    role: triangle_inequality_for_L_p_norm
    related: [holders_inequality_used_in_proof, triangle_inequality, L_p_space_norm, normed_space]
    is_axiom: false
    axioms: [holders_inequality, conjugate_exponents, non_negativity_of_norm]
  serves_capability: [L_p_norm_triangle_inequality, normed_space_construction, functional_analysis]
  signature_hint: p_norm_subadditivity

- canonical_name: convex_function
  aliases: [convex_phi, jensen_arg_convex]
  tier: T1
  partition: math_foundation
  science_algebra_category: analysis::convexity
  algebra_dict:
    definition: "phi convex iff phi(lambda x + (1-lambda) y) <= lambda phi(x) + (1-lambda) phi(y) for lambda in [0,1]"
    equivalent_smooth: second_derivative_non_negative
    examples: [x_squared, exponential, negative_log, max_function, indicator_of_convex_set]
    properties: [closed_under_non_negative_combination, sum_of_convex_is_convex, jensen_inequality_applies]
    related: [concave_function, jensen_inequality, log_concavity_complement, optimization_global_optimum]
    is_axiom: false
    axioms: [convexity_definition_via_chord_above_curve, interval_definition]
  serves_capability: [optimization_global_minimum_guarantees, jensen_application, variational_bounds]
  signature_hint: chord_above_function_value

- canonical_name: concave_function
  aliases: [concave_phi, jensen_arg_concave]
  tier: T1
  partition: math_foundation
  science_algebra_category: analysis::convexity
  algebra_dict:
    definition: "phi concave iff -phi is convex; phi(lambda x + (1-lambda) y) >= lambda phi(x) + (1-lambda) phi(y)"
    examples: [log_x, sqrt_x_on_non_negative, -x_squared, shannon_entropy_as_function_of_p]
    properties: [closed_under_non_negative_combination, jensen_inequality_reverses, monotonic_implications]
    related: [convex_function, jensen_inequality, log_concavity, shannon_entropy]
    is_axiom: false
    axioms: [concavity_definition_via_chord_below_curve, interval_definition]
  serves_capability: [variational_upper_bounds, jensen_reverse_application, entropy_concavity_use]
  signature_hint: chord_below_function_value

- canonical_name: non_negativity
  aliases: [non_negative_predicate, f_geq_0]
  tier: T1
  partition: math_foundation
  science_algebra_category: order_theory::positivity
  algebra_dict:
    definition: "x >= 0 in an ordered field / real-valued function f satisfies f(x) >= 0 for all x in domain"
    examples: [norm, variance, kl_divergence, entropy, mutual_information, cosine_squared, modulus_squared]
    role: foundational_property_of_metric_norm_inner_product_information_theoretic_quantities
    related: [absolute_value, ordered_field, gibbs_inequality, jensen_inequality]
    is_axiom: true
    note: foundational_axiom_used_throughout_proofs
  serves_capability: [proof_chain_termination_atom, lower_bound_foundation, L6_PROOF_G4_bridge]
  signature_hint: greater_or_equal_zero_property

- canonical_name: conditional_entropy
  aliases: [H_X_given_Y, conditional_information]
  tier: T1
  partition: math_foundation
  science_algebra_category: information_theory::entropy
  algebra_dict:
    formula: "H(X | Y) = -sum_{x,y} p(x,y) log p(x | y) = H(X,Y) - H(Y)"
    properties: [non_negative, H_X_given_Y_leq_H_X_with_equality_iff_X_Y_independent, chain_rule_H_X_Y_eq_H_X_plus_H_Y_given_X]
    related: [shannon_entropy, mutual_information, chain_rule_entropy, joint_entropy]
    is_axiom: false
    axioms: [conditional_probability, expectation, shannon_entropy]
  serves_capability: [information_theoretic_decomposition, mutual_information_derivation_bridge, L6_PROOF_G3_bridge]
  signature_hint: entropy_after_conditioning_on_Y

- canonical_name: chain_rule_entropy
  aliases: [entropy_chain_rule, H_X_Y_decomposition]
  tier: T1
  partition: math_foundation
  science_algebra_category: information_theory::entropy
  algebra_dict:
    formula: "H(X_1, ..., X_n) = sum_i H(X_i | X_1, ..., X_{i-1})"
    binary_case: "H(X,Y) = H(X) + H(Y|X) = H(Y) + H(X|Y)"
    relation_to_mutual_information: "I(X;Y) = H(X) + H(Y) - H(X,Y) follows directly from chain rule applied twice"
    related: [shannon_entropy, conditional_entropy, joint_entropy, mutual_information]
    is_axiom: false
    axioms: [conditional_entropy, joint_entropy, expectation_linearity]
  serves_capability: [entropy_decomposition_proofs, mutual_information_derivation, L6_PROOF_G3_target]
  signature_hint: entropy_decomposes_along_chain
```

## L6-PROOF G1-G4 coverage post BATCH 05

| Goal | Atoms needed | Coverage |
|---|---|---|
| G1 orthogonality_implies_zero_inner_product | inner_product, orthogonality | BATCH 01 COMPLETE |
| G2 KL_divergence_non_negative | kl_divergence, jensen_inequality, log_concavity, gibbs_inequality | BATCH 03 + 05 COMPLETE |
| G3 mutual_information_non_negative | mutual_information, shannon_entropy, chain_rule_entropy, conditional_entropy, kl_divergence | BATCH 03 + 05 COMPLETE |
| G4 Cauchy_Schwarz_in_inner_product_space | inner_product, non_negativity, cauchy_schwarz_inequality | BATCH 01 + 05 COMPLETE |

L6-PROOF PHASE 3 verification cell can now run as soon as Testbed ships PHASE 2 substrate_query.py prove subcommand + BATCH 05 ingested.

## algebra_dict.is_axiom flag convention introduced

BATCH 05 introduces `is_axiom: true/false` field per algebra_dict per L6-PROOF drill cell spec. Atoms with `is_axiom: true` are terminal in backward-chaining proof (no further unfolding). BATCH 05 axiom-leaves: `triangle_inequality`, `non_negativity`. Future BATCH atoms should set this flag per algebra-foundational role.

Testbed: please retro-flag BATCH 01-04 atoms with `is_axiom` field during ingest:
- axiom atoms (BATCH 01-04 candidates): `axioms` (concept itself), nothing else terminal at this layer
- All other BATCH 01-04 atoms: `is_axiom: false` (derived from more-foundational axioms)

## Cumulative coverage post BATCH 05

- 50 T1 atoms backfilled = ~35pct of 144 target
- 5 layers: linear algebra + probability + info theory + statistics + topology + analysis + inequalities + convexity
- L6-PROOF G1-G4 proof chains COMPLETE at corpus level (PHASE 2 subcommand + PHASE 3 verification still gated)

## Routing

- Testbed BATCH 05 ingest when bandwidth allows; coordinate with L6-PROOF PHASE 2 subcommand work
- Research BATCH 06 on demand (categorical structures + algebraic structures + numerical linear algebra remainder)
- Exp-Dev PHASE 3 verification cell ready to run once PHASE 2 ships

## Cross-references

- BATCH 01-04 predecessors
- notes/research_to_testbed_exp_dev_L6_PROOF_substrate_query_prove_subcommand_USER_GOAL_ALIGNED_HIGHEST_PRIORITY_2026-06-12.md (PHASE 2 + 3 ship plan)
- notes/research_drill_substrate_as_differentiable_theorem_prover_surface_USER_goal_aligned_2x_2026-06-12.md (drill source)

---

**Testbed:** T1 ALGEBRA-DICT BACKFILL BATCH 05 10 L6-PROOF-targeted bridge atoms INGEST-READY YAML cauchy_schwarz_inequality + log_concavity + triangle_inequality + holders_inequality + minkowski_inequality + convex_function + concave_function + non_negativity + conditional_entropy + chain_rule_entropy + algebra_dict.is_axiom flag convention introduced + L6-PROOF G1-G4 proof chains corpus COMPLETE PHASE 3 verification gated only by PHASE 2 substrate_query.py prove subcommand + cumulative 50 atoms 35pct of 144 target + BATCH 06+ on demand + USER full-auto overnight continuing.
