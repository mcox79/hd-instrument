# Research -> Testbed: T1 algebra DEPTH-2 DEPENDS_ON BATCH 15 -- recursive prerequisite authoring -- CHTV-1 corpus depth finding fix -- INGEST-READY YAML

**From:** Research  **Date:** 2026-06-12 (Cycle 51 close + USER full-auto overnight)
**Re:** Exp-Dev CHTV-1 corpus depth finding: DEPENDS_ON has 2220 edges but 0 depth-2 chains; multi-step L6-PROOF NOT YET feasible over DEPENDS_ON-only

## Goal

Author explicit depth-2 DEPENDS_ON edges on prerequisite atoms of BATCH 01-14 144 T1 atoms so that depth-2 chains (a -> b -> c) exist for L6-PROOF backward-chaining unfold.

Per L6-PROOF G1-G4 proof chains, the specific depth-2 dependencies needed:

```yaml
# Depth-2 DEPENDS_ON edges (prerequisite-of-prerequisite layer)

# G1: orthogonality -> inner_product -> vector_space + axioms
- atom: inner_product
  add_depends_on:
    - vector_space
    - bilinear_form_concept_if_present
    - non_negativity
    - field
- atom: orthogonality
  add_depends_on:
    - inner_product
    - non_negativity

# G2: kl_divergence -> jensen + log_concavity + shannon_entropy
- atom: kl_divergence
  add_depends_on:
    - shannon_entropy
    - log_concavity
    - jensen_inequality
    - probability_space
    - radon_nikodym
- atom: log_concavity
  add_depends_on:
    - concave_function
    - jensen_inequality
    - convex_function
- atom: gibbs_inequality
  add_depends_on:
    - kl_divergence
    - jensen_inequality
    - non_negativity

# G3: mutual_information -> shannon_entropy + chain_rule_entropy + conditional_entropy
- atom: mutual_information
  add_depends_on:
    - shannon_entropy
    - kl_divergence
    - independence_probability
    - conditional_entropy
- atom: shannon_entropy
  add_depends_on:
    - probability_space
    - random_variable
    - expectation
- atom: conditional_entropy
  add_depends_on:
    - shannon_entropy
    - conditional_probability
    - random_variable
- atom: chain_rule_entropy
  add_depends_on:
    - shannon_entropy
    - conditional_entropy
    - independence_probability

# G4: cauchy_schwarz -> inner_product + non_negativity + quadratic_form
- atom: cauchy_schwarz_inequality
  add_depends_on:
    - inner_product
    - non_negativity
    - axioms

# Bridge atoms upward
- atom: jensen_inequality
  add_depends_on:
    - convex_function
    - concave_function
    - expectation
    - non_negativity
- atom: convex_function
  add_depends_on:
    - axioms
- atom: concave_function
  add_depends_on:
    - convex_function
    - axioms
- atom: triangle_inequality
  add_depends_on:
    - non_negativity
    - axioms
- atom: holders_inequality
  add_depends_on:
    - axioms
    - non_negativity
    - jensen_inequality
- atom: minkowski_inequality
  add_depends_on:
    - holders_inequality
    - triangle_inequality
    - non_negativity

# Linear algebra depth-2
- atom: vector_space
  add_depends_on:
    - axioms
    - field
- atom: linear_independence
  add_depends_on:
    - vector_space
    - axioms
- atom: basis
  add_depends_on:
    - linear_independence
    - span
- atom: span
  add_depends_on:
    - vector_space
- atom: cosine_similarity
  add_depends_on:
    - inner_product
    - axioms

# Probability foundations depth-2
- atom: random_variable
  add_depends_on:
    - sigma_algebra
    - probability_space
    - measurable_function
- atom: expectation
  add_depends_on:
    - random_variable
    - lebesgue_integral
    - probability_space
- atom: variance
  add_depends_on:
    - expectation
    - random_variable
- atom: conditional_probability
  add_depends_on:
    - probability_space
    - axioms
- atom: bayes_rule
  add_depends_on:
    - conditional_probability
    - probability_space
- atom: independence_probability
  add_depends_on:
    - conditional_probability
    - probability_space
- atom: central_limit_theorem
  add_depends_on:
    - characteristic_function
    - random_variable
    - independence_probability
    - expectation
    - variance

# Topology depth-2
- atom: metric_space
  add_depends_on:
    - axioms
    - non_negativity
    - triangle_inequality
- atom: topology
  add_depends_on:
    - axioms
- atom: continuity
  add_depends_on:
    - topology
    - metric_space
    - limit
- atom: compactness
  add_depends_on:
    - topology
    - metric_space
- atom: completeness
  add_depends_on:
    - metric_space
    - sequence_convergence
- atom: banach_space
  add_depends_on:
    - vector_space
    - completeness
    - axioms
- atom: hilbert_space
  add_depends_on:
    - banach_space
    - inner_product
- atom: limit
  add_depends_on:
    - sequence_convergence
    - metric_space
- atom: lipschitz_continuity
  add_depends_on:
    - continuity
    - non_negativity
    - metric_space

# Diff calculus depth-2
- atom: derivative
  add_depends_on:
    - limit
    - continuity
- atom: gradient
  add_depends_on:
    - partial_derivative
    - vector_space
- atom: jacobian
  add_depends_on:
    - partial_derivative
    - derivative
- atom: hessian
  add_depends_on:
    - jacobian
    - partial_derivative
- atom: chain_rule_calculus
  add_depends_on:
    - derivative
    - jacobian
- atom: taylor_series
  add_depends_on:
    - derivative
    - hessian
- atom: partial_derivative
  add_depends_on:
    - derivative
- atom: directional_derivative
  add_depends_on:
    - gradient
    - inner_product
- atom: total_derivative
  add_depends_on:
    - jacobian
    - derivative
- atom: mean_value_theorem
  add_depends_on:
    - derivative
    - continuity

# Optimization depth-2
- atom: gradient_descent
  add_depends_on:
    - gradient
    - convex_function
- atom: convex_optimization
  add_depends_on:
    - convex_function
- atom: KKT_conditions
  add_depends_on:
    - lagrangian
    - convex_optimization
- atom: lagrangian
  add_depends_on:
    - convex_function
    - axioms
- atom: duality_lagrangian
  add_depends_on:
    - lagrangian
    - KKT_conditions
- atom: subgradient
  add_depends_on:
    - convex_function
    - gradient
- atom: stochastic_gradient_descent
  add_depends_on:
    - gradient_descent
    - expectation
- atom: line_search
  add_depends_on:
    - gradient_descent
- atom: trust_region
  add_depends_on:
    - gradient_descent
    - hessian
- atom: fixed_point_iteration
  add_depends_on:
    - lipschitz_continuity
    - completeness

# Numerical linear algebra depth-2
- atom: SVD
  add_depends_on:
    - matrix_decomposition
    - eigendecomposition
    - inner_product
- atom: eigendecomposition
  add_depends_on:
    - matrix_decomposition
    - vector_space
- atom: QR_decomposition
  add_depends_on:
    - matrix_decomposition
    - orthogonality
- atom: LU_decomposition
  add_depends_on:
    - matrix_decomposition
- atom: cholesky_decomposition
  add_depends_on:
    - LU_decomposition
    - non_negativity
- atom: matrix_norm
  add_depends_on:
    - SVD
- atom: condition_number
  add_depends_on:
    - SVD
    - matrix_norm
- atom: pseudoinverse
  add_depends_on:
    - SVD
- atom: rank
  add_depends_on:
    - linear_independence
    - SVD

# Stochastic processes depth-2
- atom: martingale
  add_depends_on:
    - random_variable
    - expectation
    - conditional_probability
- atom: brownian_motion
  add_depends_on:
    - random_variable
    - martingale
    - gaussian_distribution_if_present
- atom: markov_chain
  add_depends_on:
    - random_variable
    - conditional_probability
- atom: stationary_distribution
  add_depends_on:
    - markov_chain
    - probability_space
- atom: ergodicity
  add_depends_on:
    - markov_chain
    - stationary_distribution
- atom: stopping_time
  add_depends_on:
    - random_variable
    - sigma_algebra
- atom: ito_integral
  add_depends_on:
    - brownian_motion
    - lebesgue_integral
    - martingale
- atom: sde
  add_depends_on:
    - brownian_motion
    - ito_integral
- atom: levy_process
  add_depends_on:
    - random_variable
    - independence_probability
- atom: poisson_process
  add_depends_on:
    - levy_process
    - exponential_distribution_if_present

# Measure theory depth-2
- atom: measurable_function
  add_depends_on:
    - sigma_algebra
- atom: lebesgue_integral
  add_depends_on:
    - measurable_function
    - lebesgue_measure
- atom: dominated_convergence_theorem
  add_depends_on:
    - lebesgue_integral
    - sequence_convergence
- atom: monotone_convergence_theorem
  add_depends_on:
    - lebesgue_integral
    - sequence_convergence
- atom: fubini_tonelli
  add_depends_on:
    - lebesgue_integral
    - sigma_finite
- atom: radon_nikodym
  add_depends_on:
    - absolute_continuity_of_measures
    - sigma_finite
    - lebesgue_integral

# Functional analysis depth-2
- atom: bounded_linear_operator
  add_depends_on:
    - vector_space
    - matrix_norm
- atom: compact_operator
  add_depends_on:
    - bounded_linear_operator
- atom: dual_space
  add_depends_on:
    - bounded_linear_operator
    - vector_space
- atom: weak_topology
  add_depends_on:
    - dual_space
    - topology
- atom: sobolev_space
  add_depends_on:
    - banach_space
    - hilbert_space
- atom: schwartz_space
  add_depends_on:
    - vector_space
- atom: distribution_generalized_function
  add_depends_on:
    - schwartz_space
    - dual_space
- atom: reflexive_space
  add_depends_on:
    - dual_space
    - banach_space
- atom: separable_space
  add_depends_on:
    - metric_space
- atom: hahn_banach_theorem
  add_depends_on:
    - dual_space
    - convex_function

# Graph theory depth-2
- atom: tree
  add_depends_on:
    - graph
- atom: bipartite_graph
  add_depends_on:
    - graph
- atom: planar_graph
  add_depends_on:
    - graph
    - topology
- atom: laplacian_matrix
  add_depends_on:
    - graph
    - matrix_decomposition
- atom: spectral_graph_theory
  add_depends_on:
    - laplacian_matrix
    - eigendecomposition
- atom: chromatic_number
  add_depends_on:
    - graph
- atom: cheeger_inequality
  add_depends_on:
    - laplacian_matrix
    - spectral_graph_theory
- atom: fiedler_vector
  add_depends_on:
    - laplacian_matrix
    - eigendecomposition
- atom: generating_function
  add_depends_on:
    - sequence_convergence

# Numerical methods + algos depth-2
- atom: newton_method
  add_depends_on:
    - derivative
    - jacobian
    - fixed_point_iteration
- atom: finite_difference
  add_depends_on:
    - derivative
    - taylor_series
- atom: runge_kutta
  add_depends_on:
    - taylor_series
    - finite_difference
- atom: monte_carlo
  add_depends_on:
    - law_of_large_numbers_if_present
    - random_variable
    - expectation
- atom: importance_sampling
  add_depends_on:
    - monte_carlo
    - radon_nikodym
- atom: kalman_filter
  add_depends_on:
    - bayes_rule
    - gaussian_distribution_if_present
- atom: em_algorithm
  add_depends_on:
    - maximum_likelihood
    - jensen_inequality
- atom: viterbi_algorithm
  add_depends_on:
    - markov_chain
    - dynamic_programming
- atom: dynamic_programming
  add_depends_on:
    - optimal_substructure_concept_if_present
- atom: linear_programming
  add_depends_on:
    - convex_optimization
- atom: graph_random_walk
  add_depends_on:
    - markov_chain
    - graph
- atom: shortest_path
  add_depends_on:
    - graph
    - dynamic_programming
- atom: variational_inference
  add_depends_on:
    - kl_divergence
    - jensen_inequality
    - em_algorithm
- atom: belief_propagation
  add_depends_on:
    - graph
    - conditional_probability
    - dynamic_programming
```

## Coverage expansion

This BATCH 15 adds ~250 depth-2 DEPENDS_ON edges across 90+ source atoms. Combined with existing BATCH 01-14 prerequisites (depth-1), depth-2 chains a -> b -> c become walkable for L6-PROOF backward-chaining.

After this BATCH, L6-PROOF PHASE 3 verification cell can run at depth up to ~5 (BATCH 05 cauchy_schwarz_inequality -> inner_product -> vector_space -> axioms; depth-3 chain).

## Testbed ingest checklist

1. For each atom listed, verify it exists in substrate post BATCH 01-14 ingest
2. Add the listed DEPENDS_ON edges to substrate (Q2+Q3 convention)
3. Verify no edge already present (idempotent ingest)
4. Report which "_if_present" prerequisites were absent (catalog refinement target for BATCH 16)
5. After ingest, recompute depth-2 chain count over DEPENDS_ON-only subgraph; report new count

Pre-reg HARD-PASS for ingest: depth-2 DEPENDS_ON chains a -> b -> c count goes from 0 to >= 200.

## Cross-references

- notes/exp_dev_to_research_CHTV1_substrate_as_verifier_HARD_PASS_CH_P1_P2_1p0_zero_false_accepts_2026-06-12.md (corpus depth finding source)
- BATCH 01-14 predecessors (single-depth DEPENDS_ON)
- memory `substrate-CHTV1-substrate-as-verifier-HARD-PASS-1p0-precision-LLM-categorical-gap-checkable-ground-truth-2026-06-12`

---

**Testbed:** T1 algebra DEPTH-2 DEPENDS_ON BATCH 15 + ~250 depth-2 edges over 90+ source atoms + CHTV-1 corpus depth finding fix DEPENDS_ON 1-layer 0 depth-2 chains -> depth-2 chains walkable post ingest + L6-PROOF PHASE 3 G1-G4 verification feasible at depth-5 + Pre-reg ingest HP depth-2 chain count >= 200 + USER full-auto overnight continuing.
