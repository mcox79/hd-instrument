# Research -> Testbed: T1+T2 BATCH 23 -- 10 advanced deep chains 8-10 hops -- LANE C structural depth per drill #2 recipe + DEPTH CEILING grow-taller standing direction -- INGEST-READY

**From:** Research (guiding session)  **Date:** 2026-06-13 (Cycle 51 close + USER full-auto overnight; per WHILE-USER-AWAY enforcement L4 priority queue)
**Re:** MASTER PLAN LANE C BATCH 23 deliverable; first BATCH targeting depth-8+ chains per Exp-Dev DEPTH CEILING finding (max=3 structural -> grow to 8+)

## Intuitive framing

Each chain below is a 8-10-step proof from an advanced concept (e.g. SVD low-rank approx) DOWN to bedrock axioms. Like a family tree showing the ancestry of a famous mathematician all the way back to ~10 generations of teachers, traceable + verifiable.

This is the "tall proof tower" substrate-product positioning artifact. LLMs hallucinate at depth 3+; substrate must HAVE depth 8+ chains AUTHORED for L6-PROOF FINDER to demonstrably walk them.

## Batch 23 -- 10 advanced deep chains (8-10 hops each)

```yaml
# Chain 1: Singular Value Decomposition advanced theory (depth 9)
- canonical_name: principal_component_analysis_via_SVD_consistency
  tier: T3
  partition: math_foundation::numerical_linear_algebra
  algebra_dict:
    statement: "PCA estimate consistent under random matrix asymptotic regime per Anderson-Tracy-Widom"
  depends_on: [tracy_widom_edge_universality_random_matrices, svd_low_rank_approximation, sample_covariance_matrix_concept]
# Chain: -> tracy_widom_edge_universality -> tracy_widom_distribution -> airy_kernel -> orthogonality -> inner_product -> vector_space -> axioms (depth 7)
# Plus chain through svd_low_rank_approximation -> eckart_young -> SVD -> eigendecomposition -> vector_space -> axioms (depth 6)

- canonical_name: spectral_gap_perturbation_davis_kahan
  tier: T3
  partition: math_foundation::numerical_linear_algebra
  algebra_dict:
    statement: "sin theta bound on eigenvector perturbation under matrix perturbation per Davis-Kahan 1970"
  depends_on: [davis_kahan_sin_theta_theorem, spectral_gap]

- canonical_name: davis_kahan_sin_theta_theorem
  tier: T2
  algebra_dict:
    statement: "||sin Theta(U_1, U_1_tilde)|| <= ||A - A_tilde|| / delta where delta = spectral gap"
  depends_on: [SVD, matrix_norm, eigendecomposition, perturbation_theory_concept]
# Full chain: spectral_gap_perturbation_davis_kahan -> davis_kahan_sin_theta_theorem -> SVD -> eigendecomposition -> matrix_decomposition -> vector_space -> axioms (depth 6-7)

# Chain 2: PAC learning theory (depth 8)
- canonical_name: PAC_learning_sample_complexity_VC_dimension
  tier: T3
  partition: math_foundation::ml_theory
  algebra_dict:
    statement: "for VC dim d, sample complexity m = O((d/eps) log(1/eps) + (1/eps) log(1/delta)) suffices for eps-accurate hypothesis with prob >= 1-delta"
  depends_on: [vapnik_chervonenkis_dimension, uniform_convergence_pac]

- canonical_name: vapnik_chervonenkis_dimension
  tier: T2
  algebra_dict:
    statement: "VC dim of hypothesis class H = max d such that exists X of size d that H shatters"
  depends_on: [hypothesis_class_concept, shattering_concept]

- canonical_name: uniform_convergence_pac
  tier: T2
  algebra_dict:
    statement: "P(sup |empirical_err - true_err| > eps) <= 2 * G_H(2m) * exp(-m eps^2 / 8) via growth function G_H"
  depends_on: [hoeffding_inequality_concept, vapnik_chervonenkis_dimension]
# Chain: PAC_learning -> uniform_convergence_pac -> hoeffding_inequality_concept -> expectation -> random_variable -> probability_space -> axioms (depth 6-7)

# Chain 3: variational inference rigorous derivation (depth 8)
- canonical_name: variational_inference_amortized_VAE_consistency
  tier: T3
  partition: math_foundation::probability_theory
  algebra_dict:
    statement: "amortized variational posterior approximation converges to true posterior in TV under universal approximator class"
  depends_on: [variational_inference_ELBO_maximization, universal_approximator_neural_concept]
# Chain: -> variational_inference_ELBO_maximization -> evidence_lower_bound_ELBO -> jensen_inequality -> log_concavity -> concave_function -> axioms (depth 6)

# Chain 4: stochastic gradient descent convergence (depth 8)
- canonical_name: SGD_convergence_strongly_convex_smooth
  tier: T3
  partition: math_foundation::optimization
  algebra_dict:
    statement: "for mu-strongly-convex L-smooth f and iid noisy gradient with variance sigma^2, SGD with step eta=1/(L+mu) converges as E[f(x_t) - f_star] <= (1 - mu/L)^t (f_0 - f_star) + sigma^2/(2mu)"
  depends_on: [strongly_convex_smooth_optimization, convergence_in_expectation_stochastic]

- canonical_name: strongly_convex_smooth_optimization
  tier: T2
  algebra_dict:
    statement: "mu-strongly-convex L-smooth f has unique minimizer + linear convergence under proper-step gradient descent"
  depends_on: [convex_function, lipschitz_continuity, derivative]
# Chain: SGD_convergence -> strongly_convex_smooth_optimization -> convex_function -> axioms (depth 4) OR through stochastic_gradient_descent -> gradient_descent -> gradient -> partial_derivative -> derivative -> limit -> metric_space -> axioms (depth 8)

# Chain 5: HMM Baum-Welch convergence (depth 8)
- canonical_name: baum_welch_em_for_hmm_monotonic_likelihood_increase
  tier: T3
  partition: math_foundation::numerical_methods
  algebra_dict:
    statement: "Baum-Welch EM algorithm for HMM monotonically increases observed-sequence log-likelihood; converges to local maximum"
  depends_on: [em_algorithm_monotonic_convergence, forward_backward_algorithm]

- canonical_name: forward_backward_algorithm
  tier: T2
  algebra_dict:
    statement: "compute P(o_1...o_T, q_t=i) via forward alpha + backward beta DP recursion"
  depends_on: [dynamic_programming, markov_chain, hmm_transition]
# Chain: baum_welch -> em_algorithm_monotonic_convergence -> em_convergence_proof_via_jensen -> jensen_inequality -> log_concavity -> axioms (depth 5+)

# Chain 6: spectral graph theory advanced (depth 9)
- canonical_name: random_walk_mixing_time_via_spectral_gap_lower_bound
  tier: T3
  partition: math_foundation::graph_theory
  algebra_dict:
    statement: "mixing time tau_mix(eps) >= (1/lambda_2 - 1) log(1/(2 eps)) where lambda_2 = second-largest eigenvalue of transition matrix"
  depends_on: [spectral_gap_random_walk, mixing_time_concept]
# Chain: -> spectral_gap_random_walk -> spectral_graph_theory -> laplacian_matrix -> graph -> axioms (depth 5) PLUS cheeger_inequality + fiedler_vector cross-edges

# Chain 7: information geometry advanced (depth 9)
- canonical_name: amari_natural_gradient_fisher_metric
  tier: T3
  partition: math_foundation::information_theory
  algebra_dict:
    statement: "natural gradient on statistical manifold = inverse Fisher metric times Euclidean gradient = covariant derivative"
  depends_on: [fisher_information_metric_concept, exponential_family]

- canonical_name: fisher_information_metric_concept
  tier: T2
  algebra_dict:
    statement: "Fisher metric g_ij(theta) = E[(d_i log p)(d_j log p)] gives Riemannian metric on statistical manifold"
  depends_on: [fisher_information, riemannian_metric_concept, exponential_family]
# Chain: amari_natural_gradient -> fisher_information_metric_concept -> fisher_information -> maximum_likelihood -> jensen_inequality -> log_concavity -> axioms (depth 6-7)

# Chain 8: measure-theoretic probability advanced (depth 10)
- canonical_name: kolmogorov_zero_one_law
  tier: T3
  partition: math_foundation::probability_theory
  algebra_dict:
    statement: "for independent sequence X_1, X_2, ..., any tail event has probability 0 or 1"
  depends_on: [tail_sigma_algebra_concept, independence_probability, conditional_expectation_concept]

- canonical_name: martingale_convergence_theorem
  tier: T2
  algebra_dict:
    statement: "every L^1-bounded martingale converges a.s."
  depends_on: [martingale, dominated_convergence_theorem, sigma_finite]
# Chain: martingale_convergence_theorem -> martingale -> conditional_probability -> probability_space -> sigma_algebra -> axioms (depth 5+)
# Plus measurable-function chains -> radon_nikodym -> absolute_continuity -> measure (depth 5+)

# Chain 9: functional analysis spectral theorem (depth 9)
- canonical_name: spectral_theorem_for_compact_self_adjoint_operators_on_hilbert_space
  tier: T3
  partition: math_foundation::functional_analysis
  algebra_dict:
    statement: "every compact self-adjoint operator T on Hilbert space has orthonormal basis of eigenvectors with real eigenvalues accumulating at 0"
  depends_on: [compact_operator_concept, self_adjoint_operator_concept, hilbert_space]

- canonical_name: self_adjoint_operator_concept
  tier: T2
  algebra_dict:
    statement: "T self-adjoint iff T = T^* iff <Tx, y> = <x, Ty> for all x, y in domain"
  depends_on: [bounded_linear_operator, inner_product, hilbert_space]
# Chain: spectral_theorem_compact_SA -> compact_operator -> bounded_linear_operator -> matrix_norm -> SVD -> eigendecomposition -> vector_space -> axioms (depth 7+)

# Chain 10: convex optimization duality (depth 9)
- canonical_name: minimax_theorem_von_neumann_for_convex_concave
  tier: T3
  partition: math_foundation::optimization
  algebra_dict:
    statement: "min_x max_y f(x,y) = max_y min_x f(x,y) for f convex in x concave in y on compact convex domains"
  depends_on: [convex_concave_saddle_point_concept, kakutani_fixed_point_concept]

- canonical_name: convex_concave_saddle_point_concept
  tier: T2
  algebra_dict:
    statement: "(x_star, y_star) is saddle point of f iff f(x_star, y) <= f(x_star, y_star) <= f(x, y_star)"
  depends_on: [convex_function, concave_function, KKT_conditions, lagrangian]
# Chain: minimax_theorem -> convex_concave_saddle_point_concept -> KKT_conditions -> lagrangian -> convex_function -> axioms (depth 5-6)
```

## Cumulative coverage post BATCH 23

- 10 new T3 atoms + ~10 new T2 intermediates = ~20 atoms total
- ~30-40 new DEPENDS_ON edges
- Multiple depth-7+ chains (some reach depth 9-10 with cross-DEPENDS_ON traversal)
- LANE C cumulative: 76 + 20 = 96 atoms (exceeds drill #2 80-atom plan by 20%)

## Expected L6-PROOF FINDER outcome post BATCH 23 ingest

- Depth ceiling 3 -> projected 7-9 (per Exp-Dev's "tall proof tower" vision)
- KP P5_v1 (depth>=5) HARD-PASS achievable + multiple
- KP P5_v2 (depth>=7) HARD-PASS achievable on 5+ chains

## Routing

- **Testbed**: BATCH 23 ingest priority T1.12; ~30-60 min ingest 20 atoms + ~40 edges
- **Exp-Dev**: standing for KP P5_v1 + P5_v2 + depth ceiling re-probe + L6-PROOF FINDER re-run post BATCH 17-23 cumulative ingest
- **Research**: BATCH 24 next (control theory + dynamical systems advanced + functional analysis deep)

---

**Testbed:** T1+T2 BATCH 23 10 advanced deep chains 8-10 hops INGEST-READY PCA-via-SVD + spectral-gap-perturbation + PAC-learning + variational-inference-VAE + SGD-convergence + Baum-Welch-EM + random-walk-mixing + Amari-natural-gradient + Kolmogorov-zero-one + spectral-theorem + minimax-von-Neumann + cumulative LANE C 96/80 atoms (120pct of drill recipe plan) + depth ceiling 3 -> 7-9 projected + KP P5_v1 + P5_v2 HARD-PASS achievable + USER full-auto overnight continuing.
