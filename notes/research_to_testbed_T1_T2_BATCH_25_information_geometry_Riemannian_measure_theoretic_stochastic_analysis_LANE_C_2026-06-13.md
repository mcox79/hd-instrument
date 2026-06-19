# Research -> Testbed: T1+T2 BATCH 25 -- 10 information geometry + Riemannian + measure-theoretic stochastic analysis atoms -- LANE C closing the drill #2 80-atom plan + extending toward 130+

**From:** Research (guiding session)  **Date:** 2026-06-13 (Cycle 51 close + USER full-auto overnight; per WHILE-USER-AWAY L4 priority queue + diversification rule applied)

## Batch 25 -- 10 atoms (information geometry + Riemannian + stochastic analysis)

```yaml
# Chain 1: information geometry advanced (statistical manifolds)
- canonical_name: statistical_manifold_information_geometry
  tier: T2
  partition: math_foundation::information_geometry
  algebra_dict:
    statement: "parametrized family {p(x|theta) : theta in Theta} forms differentiable manifold with Fisher information as Riemannian metric"
  depends_on: [fisher_information_metric_concept, riemannian_metric_concept, exponential_family]
- canonical_name: alpha_connection_amari
  tier: T2
  algebra_dict:
    statement: "Amari's alpha-family of affine connections on statistical manifolds; alpha=1 m-connection, alpha=-1 e-connection, alpha=0 Levi-Civita"
  depends_on: [statistical_manifold_information_geometry, riemannian_metric_concept]
# Chain: alpha_connection -> statistical_manifold -> fisher_information_metric -> fisher_information -> maximum_likelihood -> ... -> axioms (depth 6+)

# Chain 2: Riemannian geometry advanced
- canonical_name: riemannian_metric_concept
  tier: T2
  partition: math_foundation::differential_geometry
  algebra_dict:
    statement: "smooth assignment g_p of positive-definite inner product on each tangent space T_p M of manifold M"
  depends_on: [inner_product, vector_space, derivative]
- canonical_name: levi_civita_connection
  tier: T2
  algebra_dict:
    statement: "unique torsion-free metric-compatible connection on Riemannian manifold; defines parallel transport + geodesics"
  depends_on: [riemannian_metric_concept, covariant_derivative_concept, christoffel_symbols_concept]
# Chain: levi_civita -> riemannian_metric -> inner_product -> vector_space -> axioms (depth 4+)

# Chain 3: stochastic analysis Ito formula advanced
- canonical_name: ito_formula_multidimensional
  tier: T3
  partition: math_foundation::stochastic_analysis
  algebra_dict:
    statement: "for f in C^2 and Ito processes X_i: df(X) = sum_i (df/dx_i) dX_i + (1/2) sum_ij (d^2f/dx_i dx_j) d<X_i, X_j>"
  depends_on: [ito_integral, quadratic_covariation_concept, partial_derivative]
# Chain: ito_formula -> ito_integral -> brownian_motion -> martingale -> ... -> probability_space -> axioms (depth 6+)

# Chain 4: stochastic differential equations rigorous
- canonical_name: sde_strong_solution_existence_uniqueness
  tier: T3
  partition: math_foundation::stochastic_analysis
  algebra_dict:
    statement: "for SDE dX_t = b(X_t,t) dt + sigma(X_t,t) dW_t with Lipschitz + linear-growth b,sigma, exists unique strong solution X_t adapted to brownian filtration"
  depends_on: [sde, lipschitz_continuity, ito_integral, martingale_convergence_theorem]
# Chain: sde_existence -> sde -> ito_integral -> brownian_motion -> ... -> axioms (depth 6+)

# Chain 5: stationary point fluctuation theory
- canonical_name: kullback_leibler_geodesic_natural_gradient
  tier: T3
  partition: math_foundation::information_geometry
  algebra_dict:
    statement: "natural gradient descent on parameter manifold = covariant gradient = inverse Fisher metric times Euclidean gradient; geodesic step along KL-curve"
  depends_on: [amari_natural_gradient_fisher_metric, alpha_connection_amari, kl_divergence]
# Chain: KL_geodesic_natgrad -> amari_natural_gradient -> fisher_information_metric -> ... -> axioms (depth 6+)

# Chain 6: differential entropy + continuous distributions
- canonical_name: differential_entropy_continuous
  tier: T2
  partition: math_foundation::information_theory
  algebra_dict:
    statement: "h(X) = -integral f(x) log f(x) dx for continuous random variable X with density f"
    properties: [not_invariant_under_change_of_variables_unlike_discrete, can_be_negative, gaussian_maximum_entropy_under_variance_constraint]
  depends_on: [shannon_entropy, lebesgue_integral, random_variable]
# Chain: differential_entropy -> shannon_entropy -> kl_divergence -> ... -> axioms (depth 5+)

# Chain 7: KL barycenter information geometry
- canonical_name: kl_divergence_barycenter
  tier: T2
  partition: math_foundation::information_geometry
  algebra_dict:
    statement: "given distributions {P_i} with weights {w_i}, barycenter Q* = argmin sum_i w_i KL(P_i || Q) = weighted geometric mixture"
    use_case: federated_learning_FedAvg + distributional_clustering + mixture_model_initialization
  depends_on: [kl_divergence, statistical_manifold_information_geometry]
# Chain: KL_barycenter -> kl_divergence -> jensen_inequality -> log_concavity -> ... -> axioms (depth 5+)

# Chain 8: Wasserstein gradient flow
- canonical_name: wasserstein_gradient_flow_jko_scheme
  tier: T3
  partition: math_foundation::optimal_transport
  algebra_dict:
    statement: "Jordan-Kinderlehrer-Otto (JKO) scheme: discretize gradient flow on Wasserstein space via tau-step iterated minimization of (1/2tau) W_2^2 + F"
  depends_on: [wasserstein_distance, brenier_optimal_transport_theorem, variational_principle_continuum_action]
# Chain: JKO -> wasserstein_distance -> metric_space -> ... -> axioms (depth 5+)

# Chain 9: large deviation principle (Cramer + Sanov + Donsker-Varadhan)
- canonical_name: large_deviation_principle_LDP
  tier: T3
  partition: math_foundation::probability_theory
  algebra_dict:
    statement: "P(X_n in A) ~ exp(-n inf_{x in A} I(x)); I = rate function; Cramer theorem for sums; Sanov for empirical measures; Donsker-Varadhan for Markov chain occupation times"
  depends_on: [shannon_entropy, kl_divergence, characteristic_function]
# Chain: LDP -> kl_divergence -> jensen_inequality -> ... -> axioms (depth 5+)

# Chain 10: Schrodinger bridge problem
- canonical_name: schrodinger_bridge_problem
  tier: T3
  partition: math_foundation::optimal_transport
  algebra_dict:
    statement: "find Markov process X_t interpolating between distributions mu_0 and mu_1 with minimum KL divergence from prior Brownian motion -> equivalent to entropy-regularized optimal transport"
    use_case: generative_modeling_via_score_matching + flow_matching
  depends_on: [wasserstein_distance, kl_divergence, brownian_motion, large_deviation_principle_LDP]
# Chain: schrodinger_bridge -> wasserstein_distance + kl_divergence + brownian_motion (cross-chain depth 6+)
```

## Cumulative coverage post BATCH 25

- 10 new T2/T3 atoms (~7 T2 intermediates + 3 T3 advanced)
- ~30-40 new DEPENDS_ON edges
- LANE C cumulative: 116 + 10 = **126 atoms** (158pct of drill #2 80-atom plan)
- Math foundation depth coverage now spans information geometry + Riemannian + stochastic analysis + optimal transport advanced

## SHARES_MATH equivalence-class amortization

Three SHARES_MATH groups in BATCH 25:
- **Information geometry family**: {statistical_manifold_information_geometry, alpha_connection_amari, kullback_leibler_geodesic_natural_gradient, kl_divergence_barycenter}
- **Stochastic analysis family**: {ito_formula_multidimensional, sde_strong_solution_existence_uniqueness, schrodinger_bridge_problem}
- **Optimal transport family**: {wasserstein_gradient_flow_jko_scheme, brenier_optimal_transport_theorem, schrodinger_bridge_problem}

## Routing

- **Testbed**: BATCH 25 ingest priority T1.14
- **Exp-Dev**: standing for KP P5_v1 + L6-PROOF FINDER depth re-probe post BATCH 17-25 cumulative ingest
- **Research**: CELL 7 ProofWiki SKELETON next per priority queue (LANE B bedrock)

---

**Testbed:** T1+T2 BATCH 25 10 information geometry + Riemannian + measure-theoretic stochastic analysis atoms INGEST-READY statistical_manifold + alpha_connection_amari + riemannian_metric + levi_civita_connection + ito_formula_multidimensional + sde_strong_solution_existence_uniqueness + KL_geodesic_natgrad + differential_entropy_continuous + KL_barycenter + wasserstein_gradient_flow_jko + LDP + schrodinger_bridge + cumulative LANE C 126/80 atoms 158pct of drill recipe + 3 SHARES_MATH equivalence class seeds + multiple depth>=6 chains enabled + USER full-auto overnight continuing.
