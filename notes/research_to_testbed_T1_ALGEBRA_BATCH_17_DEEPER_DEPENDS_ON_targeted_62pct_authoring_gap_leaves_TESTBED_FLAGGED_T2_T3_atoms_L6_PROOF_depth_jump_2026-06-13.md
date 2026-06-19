# Research -> Testbed: T1 algebra BATCH 17 -- deeper DEPENDS_ON authoring targeted at TESTBED-FLAGGED 62pct authoring-gap T2/T3 leaves -- L6-PROOF depth jump unblocker -- INGEST-READY

**From:** Research (Phase 1 R1.1 per MASTER PLAN)  **Date:** 2026-06-13 (Cycle 51 close + USER full-auto overnight)
**Re:** Testbed prover-depth authoring target note (38pct genuine T1 / 62pct authoring-gap leaf); 10 specific T2/T3 atoms flagged

## Goal

Close the 62pct authoring-gap leaf caveat in L6-PROOF FINDER by authoring DEPENDS_ON edges from 10 specific T2/T3 atoms (Testbed-flagged) UPWARD to T1 foundational atoms (or to new T2 intermediates that themselves point to T1). Expected outcome: avg L6-PROOF FINDER proof depth jumps from 1.30 to 2.5+.

## Testbed-flagged atoms + Research-authored DEPENDS_ON

```yaml
# Per Testbed exp_dev_to_research_PROVER_DEPTH_authoring_target_*.md flagged list + Testbed example deps

# 1. T2/cosine_cleanup
- atom: cosine_cleanup
  add_depends_on:
    - inner_product            # BATCH 01 (T1)
    - cosine_similarity        # BATCH 01 (T1)
    - matrix_norm              # BATCH 08 (T1)
    - axioms                   # BATCH 01 (T1, is_axiom)
  add_uses:
    - argmax_lookup            # T2 candidate (may need creation; cleanup picks argmax over codebook)
  rationale: cosine_cleanup picks max-cosine codebook entry; depends on inner-product geometry + normalization + axioms

# 2. T2/tier2_schema
- atom: tier2_schema
  add_depends_on:
    - axioms                   # T1 is_axiom
    - equivalence_relation     # BATCH 06 (T1, is_axiom)
    - category                 # BATCH 06 (T1, is_axiom)
  add_instance_of:
    - schema_general           # T2 if exists
  rationale: tier2 schemas are categorical structures grouping atoms by equivalence

# 3. T3/dynamic_programming (existing BATCH 14 T1; but Testbed says it's authoring-gap leaf -> add deeper deps)
- atom: dynamic_programming
  add_depends_on:
    - recursion                # T1 candidate (may need creation; fundamental computation primitive)
    - optimal_substructure     # T1 candidate (Bellman principle of optimality; may need creation)
    - bayes_rule               # BATCH 02 (Bellman equation = posterior recursion in RL value iteration)
    - fixed_point_iteration    # BATCH 09 (DP is fixed-point of Bellman operator)
  rationale: DP via optimal substructure + recursion + Bellman fixed point

# 4. T2/superposition
- atom: superposition
  add_depends_on:
    - vector_space             # BATCH 01 (T1)
    - axioms                   # T1 is_axiom
    - linear_independence      # BATCH 01 (T1; superposition cleanly decomposes only with LI components)
  add_uses:
    - fhrr_bind                # T2 if exists (superposition + binding = VSA composition)
  rationale: VSA superposition is vector addition in HRR/FHRR space

# 5. T2/fhrr_unbind (Testbed example: -> circular_convolution)
- atom: fhrr_unbind
  add_depends_on:
    - circular_convolution     # T2 per Testbed
    - inner_product            # BATCH 01 (T1)
    - vector_space             # BATCH 01 (T1)
  rationale: fhrr_unbind = inverse circular convolution in Fourier domain

# 6. T2/circular_convolution (Testbed example: -> discrete_fourier_transform + complex_field)
- atom: circular_convolution
  add_depends_on:
    - discrete_fourier_transform   # NEW T1 candidate (may need creation in BATCH 18; foundation of DFT-based convolution)
    - complex_field                # NEW T1 candidate (may need creation; complex_C field in BATCH 06 but explicit complex_field atom helpful)
    - vector_space                 # BATCH 01 (T1)
    - axioms                       # T1 is_axiom
  rationale: circular convolution = pointwise multiplication in DFT domain

# 7. SCHOOL/structured_prediction_family (Testbed example: appears in L6-PROOF FINDER as axiom-leaf for PP-376)
- atom: structured_prediction_family
  add_depends_on:
    - category                 # BATCH 06 (T1, is_axiom)
    - equivalence_relation     # BATCH 06 (T1, is_axiom)
    - axioms                   # T1 is_axiom
  rationale: SCHOOL atoms group capabilities sharing structural prediction math (e.g. CRF + structured perceptron + Viterbi share Viterbi-decoding family)

# 8. T3/forward_algorithm_atom
- atom: forward_algorithm_atom
  add_depends_on:
    - dynamic_programming      # BATCH 14 (T1)
    - markov_chain             # BATCH 11 (T1)
    - probability_space        # BATCH 02 (T1)
    - chain_rule_probability   # BATCH 16 (T1)
  rationale: forward algorithm in HMM uses DP + Markov property + chain rule

# 9. T3/hmm_transition
- atom: hmm_transition
  add_depends_on:
    - markov_chain             # BATCH 11 (T1)
    - conditional_probability  # BATCH 02 (T1)
    - random_variable          # BATCH 02 (T1)
  rationale: HMM transition matrix is conditional distribution per Markov property

# 10. T3/answer_consistency_weak_labels
- atom: answer_consistency_weak_labels
  add_depends_on:
    - bayes_rule               # BATCH 02 (T1)
    - conditional_probability  # BATCH 02 (T1)
    - expectation              # BATCH 02 (T1)
  rationale: weak supervision via Bayesian evidence aggregation

# Additional new T1 candidate atoms (if absent; needed for BATCH 17 closure)
- canonical_name: recursion
  aliases: [recursive_definition, self_referential_computation]
  tier: T1
  partition: math_foundation
  science_algebra_category: algorithms::recursion
  algebra_dict:
    definition: "self-referential computation: f(n) defined in terms of f(n-1) or smaller subproblems"
    base_case_required: true
    examples: [factorial, fibonacci, recursive_tree_traversal, recursive_proof_unfolding]
    related: [induction, fixed_point_iteration, dynamic_programming]
    is_axiom: false
  depends_on: [fixed_point_iteration, axioms]
  serves_capability: [algorithmic_substrate_foundation, recursive_definition_substrate]
  signature_hint: self_referential_computation_with_base_case

- canonical_name: optimal_substructure
  aliases: [bellman_principle_of_optimality]
  tier: T1
  partition: math_foundation
  science_algebra_category: optimization::dynamic_programming
  algebra_dict:
    statement: "optimal solution decomposes into optimal solutions of subproblems (Bellman 1957)"
    role: foundational_property_required_for_DP_correctness
    examples: [shortest_path_Dijkstra_correctness, knapsack_DP, Viterbi_DP, RL_value_iteration]
    related: [dynamic_programming, recursion, bayes_rule, bellman_equation]
    is_axiom: false
  depends_on: [recursion, axioms]
  serves_capability: [DP_correctness_substrate, RL_substrate_foundation, optimization_substructure]
  signature_hint: optimal_decomposes_into_optimal_subproblems

- canonical_name: discrete_fourier_transform
  aliases: [DFT, FFT_basis]
  tier: T1
  partition: math_foundation
  science_algebra_category: signal_processing::frequency_domain
  algebra_dict:
    formula: "X_k = sum_{n=0}^{N-1} x_n exp(-2*pi*i*k*n/N)"
    inverse: x_n = (1/N) sum X_k exp(+2pi*i*k*n/N)
    properties: [linear, parseval_norm_preservation, convolution_becomes_pointwise_multiplication]
    related: [circular_convolution, fhrr_unbind, complex_field, characteristic_function]
    is_axiom: false
  depends_on: [vector_space, complex_field, characteristic_function]
  serves_capability: [signal_processing_foundation, fhrr_substrate, frequency_domain_analysis]
  signature_hint: frequency_domain_decomposition_via_basis_exponentials

- canonical_name: complex_field
  aliases: [field_of_complex_numbers, C_field]
  tier: T1
  partition: math_foundation
  science_algebra_category: abstract_algebra::field_theory
  algebra_dict:
    definition: "C = {a + bi : a,b in R, i^2 = -1}; complex numbers form a field"
    operations: [addition_componentwise, multiplication_a_plus_bi_times_c_plus_di_eq_ac_minus_bd_plus_ad_plus_bc_i, conjugation, modulus]
    properties: [algebraically_closed_fundamental_theorem, characteristic_0, contains_R_as_subfield]
    related: [field, real_field, complex_analysis, fundamental_theorem_of_algebra]
    is_axiom: false
  depends_on: [field, vector_space, axioms]
  serves_capability: [complex_analysis_foundation, fourier_transform_foundation, fhrr_substrate]
  signature_hint: real_pair_with_i_squared_eq_minus_one
```

## Cumulative coverage post BATCH 17

- 30 explicit DEPENDS_ON edges added across 10 Testbed-flagged T2/T3 atoms
- 4 NEW T1 atoms (recursion + optimal_substructure + discrete_fourier_transform + complex_field) authored as terminal bridges
- T1 algebra cumulative: 150 (BATCH 01-16) + 4 (BATCH 17 new) = **154 T1 atoms total**
- DEPENDS_ON edge count: ~250 (BATCH 15 depth-2) + 30 (BATCH 17 depth-3+4) = ~280 explicit Research-authored edges (in addition to Testbed's existing 2220 from prior corpus + new from BATCH 16 ingest)

## Expected L6-PROOF FINDER outcome post-BATCH 17 ingest

- Current avg depth: 1.30
- Projected avg depth: 2.5+ (depth-3 chains walkable through T3 atom -> T2 leaf -> T1 axiom)
- 38pct genuine-T1 termination -> projected 65pct+ (Testbed-flagged 10 atoms now have authored deps to T1)
- "Substrate understands own mathematics" demonstration: deeper multi-step lemma chains attainable

Phase 1 R1.1 deliverable + KPI tracking per MASTER PLAN.

## Testbed ingest checklist (per Q2+Q3 convention)

1. For each of 10 Testbed-flagged atoms: verify atom exists in substrate (via L6-PROOF FINDER goal pool)
2. Add the listed DEPENDS_ON edges; populate signature_hint where missing
3. For 4 NEW T1 atoms (recursion + optimal_substructure + discrete_fourier_transform + complex_field): verify absence; ingest with full algebra_dict + science_algebra_category + serves_capability + depends_on per Q2+Q3
4. Author SHARES_MATH edges where Testbed identifies bisimulation candidates (e.g. fhrr_unbind SHARES_MATH circular_convolution_inverse; would help KP P3 + Pi/Sigma + CHTV-2)
5. Post-ingest: re-run L6-PROOF FINDER on 20-trial pool; report avg depth + genuine-T1 rate

## Cross-references

- notes/exp_dev_to_research_PROVER_DEPTH_authoring_target_62pct_proofs_deadend_at_T2_T3_leaves_author_their_deps_2026-06-13.md (Testbed-flagged list source)
- notes/research_to_testbed_exp_dev_MASTER_PLAN_*.md (Phase 1 R1.1 deliverable)
- notes/research_to_testbed_T1_ALGEBRA_DEPTH_2_DEPENDS_ON_BATCH_15_*.md (BATCH 15 depth-2 predecessor)
- notes/research_to_testbed_T1_ALGEBRA_BATCH_16_SUPPLEMENTARY_*.md (BATCH 16 supplementary predecessor)

---

**Testbed:** T1 ALGEBRA BATCH 17 DEEPER DEPENDS_ON authoring targeted at TESTBED-FLAGGED 62pct authoring-gap T2/T3 leaves cosine_cleanup + tier2_schema + dynamic_programming + superposition + fhrr_unbind + circular_convolution + structured_prediction_family + forward_algorithm_atom + hmm_transition + answer_consistency_weak_labels + 4 NEW T1 atoms recursion + optimal_substructure + discrete_fourier_transform + complex_field + 30 DEPENDS_ON edges added + L6-PROOF FINDER depth jump 1.3 -> 2.5+ projected + 38pct genuine T1 -> 65pct+ projected + USER goal substrate-understands-own-mathematics deduction-depth substantially extended + Phase 1 R1.1 deliverable per MASTER PLAN + USER full-auto overnight continuing.
