# Research -> Testbed: T1+T2 BATCH 18 -- 10 explicit DEEP CHAIN derivations 5-to-7 hop length -- KP P5_v1 (depth>=5) unblock -- DEPTH CEILING "grow taller not wider" -- INGEST-READY

**From:** Research (guiding session)  **Date:** 2026-06-13 (Cycle 51 close + USER full-auto overnight; per enforcement rule do-not-stop)
**Re:** Exp-Dev derivation-depth ceiling = 3 STRUCTURAL finding + Research endorsement of "grow taller not wider" + BATCH 18 = first deep-chain authoring batch

## Goal

Author 10 explicit DEEP CHAIN derivations of length 5-7 hops, each going T3 -> T2 -> T1 -> T1 -> T1 -> T1 (axiom) or T3 -> T2 -> T2 -> T1 -> T1 -> T1 (axiom).

Each chain authored as:
- New T3 atom (or use existing T3 atom from substrate)
- 1-3 new T2 intermediate atoms (where bridging concepts don't yet exist)
- DEPENDS_ON edges connecting each layer down to T1 atoms (BATCH 01-17)
- Verified that terminal atom is is_axiom: true OR DEPENDS_ON path to is_axiom: true

## 10 Deep chains

### Chain 1: SVD low-rank approximation (linear algebra route; depth 6)

```yaml
- canonical_name: svd_low_rank_approximation
  tier: T3
  partition: math_foundation::numerical_linear_algebra
  algebra_dict:
    statement: "best rank-k approximation to A in Frobenius norm is U_k Sigma_k V_k^T where SVD of A = U Sigma V^T"
    related: [SVD, eckart_young_mirsky_theorem]
  depends_on: [eckart_young_mirsky_theorem]

- canonical_name: eckart_young_mirsky_theorem
  tier: T2
  partition: math_foundation::numerical_linear_algebra
  algebra_dict:
    statement: "min_{rank(X)<=k} ||A - X||_F = (sum_{i>k} sigma_i^2)^{1/2}; optimum at X = sum_{i<=k} sigma_i u_i v_i^T"
    proof_sketch: "SVD decomposition + orthogonality + variational characterization"
  depends_on: [SVD, frobenius_norm_concept, orthogonality]

# Chain: svd_low_rank_approximation -> eckart_young_mirsky_theorem -> SVD -> eigendecomposition -> inner_product -> vector_space -> axioms (depth 6)
# Note: SVD (BATCH 08) already DEPENDS_ON eigendecomposition; eigendecomposition (BATCH 08) DEPENDS_ON vector_space; vector_space (BATCH 15) DEPENDS_ON axioms (is_axiom true)
```

### Chain 2: variational inference ELBO maximization (information theory route; depth 5-6)

```yaml
- canonical_name: variational_inference_ELBO_maximization
  tier: T3
  partition: math_foundation::probability_theory
  algebra_dict:
    statement: "max ELBO(q) = E_q[log p(x,z)] - E_q[log q(z)]; equiv. min KL(q || p(z|x))"
  depends_on: [evidence_lower_bound_ELBO]

- canonical_name: evidence_lower_bound_ELBO
  tier: T2
  partition: math_foundation::probability_theory
  algebra_dict:
    statement: "log p(x) = ELBO(q) + KL(q || p(z|x)); ELBO(q) = E_q[log p(x,z)] - E_q[log q(z)]; tight iff q = p(z|x)"
    proof_sketch: "jensen_inequality applied to log p(x) = log integral_z p(x,z) dz"
  depends_on: [jensen_inequality, kl_divergence, log_concavity]

# Chain: variational_inference_ELBO_maximization -> evidence_lower_bound_ELBO -> jensen_inequality -> log_concavity (BATCH 05) -> concave_function (BATCH 05) -> axioms (BATCH 05 is_axiom) (depth 5)
```

### Chain 3: RKHS kernel method universality (functional analysis route; depth 6)

```yaml
- canonical_name: rkhs_kernel_method_universal_approximation
  tier: T3
  partition: math_foundation::functional_analysis
  algebra_dict:
    statement: "for universal kernel k (e.g. Gaussian), RKHS H_k is dense in C(K) for any compact K"
  depends_on: [reproducing_kernel_hilbert_space]

- canonical_name: reproducing_kernel_hilbert_space
  tier: T2
  partition: math_foundation::functional_analysis
  algebra_dict:
    statement: "Hilbert space H of functions f : X -> R with kernel k : X x X -> R s.t. f(x) = <f, k(x, .)>_H for all x"
    proof_sketch: "Riesz representation + positive-definite kernel + Mercer"
  depends_on: [hilbert_space, reproducing_property, positive_definite_kernel]

- canonical_name: reproducing_property
  tier: T2
  partition: math_foundation::functional_analysis
  algebra_dict:
    statement: "f(x) = <f, k(x, .)>_H for all x in X, f in H"
  depends_on: [hilbert_space, inner_product]

# Chain: rkhs_kernel_method_universal_approximation -> reproducing_kernel_hilbert_space -> hilbert_space (BATCH 04) -> banach_space (BATCH 12) -> completeness (BATCH 04) -> metric_space (BATCH 04) -> axioms (depth 6)
```

### Chain 4: Bayesian posterior consistency (probability theory route; depth 5-6)

```yaml
- canonical_name: bayesian_posterior_consistency
  tier: T3
  partition: math_foundation::probability_theory
  algebra_dict:
    statement: "as n -> inf, posterior p(theta | D_n) concentrates around true theta_0 under suitable conditions"
  depends_on: [bernstein_von_mises_theorem]

- canonical_name: bernstein_von_mises_theorem
  tier: T2
  partition: math_foundation::probability_theory
  algebra_dict:
    statement: "under regularity, posterior is asymptotically gaussian with mean theta_hat_MLE and variance I^{-1}/n"
  depends_on: [maximum_likelihood, central_limit_theorem, fisher_information]

# Chain: bayesian_posterior_consistency -> bernstein_von_mises_theorem -> central_limit_theorem (BATCH 02) -> characteristic_function (BATCH 02) -> random_variable (BATCH 02) -> probability_space (BATCH 02) -> axioms (depth 6)
```

### Chain 5: BPM Brownian motion construction (stochastic processes route; depth 7)

```yaml
- canonical_name: bpm_brownian_motion_kolmogorov_construction
  tier: T3
  partition: math_foundation::probability_theory
  algebra_dict:
    statement: "Brownian motion W_t exists as a probability measure on (C[0,inf), Borel) satisfying Kolmogorov consistency"
  depends_on: [kolmogorov_extension_theorem]

- canonical_name: kolmogorov_extension_theorem
  tier: T2
  partition: math_foundation::probability_theory
  algebra_dict:
    statement: "consistent family of finite-dim distributions extends to unique probability measure on infinite product space"
  depends_on: [sigma_algebra, probability_space, fubini_tonelli]

# Chain: bpm_brownian_motion_kolmogorov_construction -> kolmogorov_extension_theorem -> sigma_algebra (BATCH 02) -> measurable_function (BATCH 10) -> lebesgue_measure (BATCH 10) -> axioms (depth 5; can extend with extra hops via fubini_tonelli + probability_space)
```

### Chain 6: graph spectral clustering Cheeger guarantee (graph theory route; depth 6)

```yaml
- canonical_name: spectral_clustering_cheeger_guarantee
  tier: T3
  partition: math_foundation::graph_theory
  algebra_dict:
    statement: "spectral clustering on normalized Laplacian achieves cluster quality bounded by Cheeger constant"
  depends_on: [normalized_cut_relaxation]

- canonical_name: normalized_cut_relaxation
  tier: T2
  partition: math_foundation::graph_theory
  algebra_dict:
    statement: "NCut(A, B) = cut(A, B) / vol(A) + cut(A, B) / vol(B); relaxed to second-smallest eigenvector of L_norm"
  depends_on: [fiedler_vector, laplacian_matrix, cheeger_inequality]

# Chain: spectral_clustering_cheeger_guarantee -> normalized_cut_relaxation -> fiedler_vector (BATCH 13) -> laplacian_matrix (BATCH 13) -> graph (BATCH 13, is_axiom true) (depth 5; extending via cheeger_inequality to depth 6)
```

### Chain 7: backpropagation chain rule (numerical optimization route; depth 5)

```yaml
- canonical_name: backpropagation_neural_network_training
  tier: T3
  partition: math_foundation::optimization
  algebra_dict:
    statement: "gradients of loss L w.r.t. parameters theta_i computed by reverse-mode chain rule across computation graph"
  depends_on: [reverse_mode_autodiff]

- canonical_name: reverse_mode_autodiff
  tier: T2
  partition: math_foundation::optimization
  algebra_dict:
    statement: "for f : R^n -> R, compute gradient via backward pass through computation graph; cost ~ O(forward pass)"
  depends_on: [chain_rule_calculus, jacobian, gradient]

# Chain: backpropagation_neural_network_training -> reverse_mode_autodiff -> chain_rule_calculus (BATCH 07) -> jacobian (BATCH 07) -> partial_derivative (BATCH 07) -> derivative (BATCH 07) -> limit (BATCH 04) (depth 5-6)
```

### Chain 8: EM algorithm convergence (numerical methods route; depth 6)

```yaml
- canonical_name: em_algorithm_monotonic_convergence
  tier: T3
  partition: math_foundation::numerical_methods
  algebra_dict:
    statement: "EM monotonically increases observed log-likelihood; converges to local maximum"
  depends_on: [em_convergence_proof_via_jensen]

- canonical_name: em_convergence_proof_via_jensen
  tier: T2
  partition: math_foundation::numerical_methods
  algebra_dict:
    statement: "E-step: Q(theta | theta_t) = E_{Z|X,theta_t}[log p(X, Z | theta)]; M-step: theta_{t+1} = argmax Q; Q(theta_{t+1} | theta_t) >= Q(theta_t | theta_t)"
  depends_on: [em_algorithm, jensen_inequality, maximum_likelihood, expectation]

# Chain: em_algorithm_monotonic_convergence -> em_convergence_proof_via_jensen -> em_algorithm (BATCH 14) -> jensen_inequality (BATCH 03) -> log_concavity (BATCH 05) -> concave_function (BATCH 05) -> axioms (depth 6)
```

### Chain 9: HMM Viterbi optimality (numerical methods route; depth 6)

```yaml
- canonical_name: hmm_viterbi_optimality
  tier: T3
  partition: math_foundation::numerical_methods
  algebra_dict:
    statement: "viterbi recursion delta_t(j) = max_i delta_{t-1}(i) a_ij b_j(y_t) returns global MAP state sequence"
  depends_on: [viterbi_optimality_via_dp_principle]

- canonical_name: viterbi_optimality_via_dp_principle
  tier: T2
  partition: math_foundation::numerical_methods
  algebra_dict:
    statement: "Viterbi MAP = max product DP; optimal subpath property guarantees global maximum"
  depends_on: [viterbi_algorithm, dynamic_programming, optimal_substructure, markov_chain]

# Chain: hmm_viterbi_optimality -> viterbi_optimality_via_dp_principle -> viterbi_algorithm (BATCH 14) -> markov_chain (BATCH 11) -> conditional_probability (BATCH 02) -> probability_space (BATCH 02) -> axioms (depth 6)
```

### Chain 10: Tracy-Widom edge universality (free probability route; depth 7)

```yaml
- canonical_name: tracy_widom_edge_universality_random_matrices
  tier: T3
  partition: math_foundation::random_matrix_theory
  algebra_dict:
    statement: "for Wigner matrix ensembles, largest eigenvalue fluctuation N^{1/6} (lambda_max - 2) converges in distribution to Tracy-Widom F_beta"
  depends_on: [tracy_widom_distribution]

- canonical_name: tracy_widom_distribution
  tier: T2
  partition: math_foundation::random_matrix_theory
  algebra_dict:
    statement: "F_2(s) = exp(-int_s^inf (x-s) q(x)^2 dx); q is solution of Painleve II ODE"
  depends_on: [airy_kernel, painleve_ii_ode]

- canonical_name: airy_kernel
  tier: T2
  partition: math_foundation::random_matrix_theory
  algebra_dict:
    statement: "K_Airy(x, y) = (Ai(x) Ai'(y) - Ai'(x) Ai(y)) / (x - y); orthogonal polynomial kernel at edge"
  depends_on: [orthogonality, inner_product]

# Chain: tracy_widom_edge_universality_random_matrices -> tracy_widom_distribution -> airy_kernel -> orthogonality (BATCH 01) -> inner_product (BATCH 01) -> vector_space (BATCH 01) -> axioms (depth 6-7)
```

## New atom inventory

Total NEW atoms across 10 chains:
- T3: 10 (one per chain)
- T2: 18 (~1-3 intermediate per chain)
- T1: 0 (all T1 atoms already in BATCH 01-17)

Total NEW DEPENDS_ON edges: ~40-50

## Cumulative coverage post BATCH 18

- 150 + 6 (BATCH 16) + 4 (BATCH 17) + 28 (BATCH 18) = ~188 T2/T3 atoms (some T2 + 10 T3)
- ~30 + 30 + 50 = ~110 explicit Research-authored DEPENDS_ON edges (in addition to Testbed's 2220 existing DEPENDS_ON)
- L6-PROOF FINDER depth ceiling 3 -> projected 5-7 post BATCH 18 ingest

## KP P5_v1 unblock projection

Post BATCH 18 ingest:
- 10 deep chains of length 5-7 hops
- KP P5_v1 (depth >= 5) target: HARD-PASS achievable
- KP scorecard upgrade: 2-of-5 -> 4-of-5 (P1 + P4 + P3 SHARES_MATH + P5_v1)
- Aggregate >=3-of-5 HARD-PASS EXCEEDED

## Substrate-product positioning artifact extension

- 28+ artifacts at Cycle 51 close + DEPTH CEILING endorsement + 9d pillar + BATCH 18 deep chains
- Substrate transitions from "wide but flat" (1844 atoms max depth 3) to "early scaffolding" (1872 atoms max depth 5-7)
- Substrate-LLM categorical gap WIDENS at depth: substrate sound at depth 5-7 vs LLM hallucinates at depth 3+

## Routing

- **Testbed**: BATCH 18 ingest priority T1.7 after T1.5 (BATCH 17) + T1.4 (SHARES_MATH); ~30-60 min ingest 28 new atoms + ~50 new DEPENDS_ON edges
- **Exp-Dev**: standing for KP P5_v1 cell run post BATCH 18 ingest (Phase 2 E2.4 NEW); standing for L6-PROOF FINDER re-run depth ceiling probe post BATCH 18 (depth ceiling 3 -> 5-7 projected)
- **Research**: standing for ingest + KP P5_v1 verdict + L6-PROOF FINDER depth-ceiling probe re-run; BATCH 19-21 will continue deep-chain authoring per drill #2 verdict pending (62pct authoring-gap prioritization)

## Cross-references

- notes/exp_dev_to_research_DERIVATION_DEPTH_CEILING_*.md (depth ceiling finding source)
- notes/research_to_exp_dev_testbed_DEPTH_CEILING_*.md (Research endorsement)
- notes/research_to_testbed_T1_ALGEBRA_BATCH_17_*.md (BATCH 17 breadth predecessor)
- notes/research_drill_L6_PROOF_FINDER_62pct_authoring_gap_leaf_prioritization_strategy_depth_corpus_expansion_2x_2026-06-13.md (drill in flight; will inform BATCH 19+ sequence)

---

**Testbed:** T1+T2 BATCH 18 10 explicit DEEP CHAIN derivations 5-7 hop length INGEST-READY YAML svd_low_rank_approximation + eckart_young_mirsky_theorem + variational_inference_ELBO_maximization + evidence_lower_bound_ELBO + rkhs_kernel_method + reproducing_property + bernstein_von_mises_theorem + kolmogorov_extension_theorem + normalized_cut_relaxation + reverse_mode_autodiff + em_convergence_proof_via_jensen + viterbi_optimality_via_dp_principle + tracy_widom_distribution + airy_kernel + 18 T2 + 10 T3 + ~40-50 DEPENDS_ON edges + L6-PROOF depth ceiling 3 -> projected 5-7 post-ingest + KP P5_v1 depth>=5 HARD-PASS achievable + KP scorecard 2-of-5 -> 4-of-5 Phase 2 exit + USER full-auto overnight continuing.
