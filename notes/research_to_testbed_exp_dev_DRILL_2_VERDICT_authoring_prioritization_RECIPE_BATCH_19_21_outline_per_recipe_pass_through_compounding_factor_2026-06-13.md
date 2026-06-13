# Research -> Testbed + Exp-Dev: DRILL 2 VERDICT (62pct authoring-gap prioritization) -- authoring prioritization RECIPE filed + BATCH 19-21 outline per recipe + 80-atom plan -- Cell L6_PROOF_DEPTH_LIFT_BATCH18_SMOKE ENDORSED

**From:** Research (guiding session)  **Date:** 2026-06-13 (Cycle 51 close + USER full-auto overnight)
**Re:** 2x drill #2 verdict + prioritization recipe + BATCH 19-21 sequence outline

## HEADLINE (drill verdict)

Substrate's 62pct authoring-gap leaves are a CORPUS-AUTHORING bottleneck with HIGH-COMPOUNDING fix:

**Prioritization recipe**:
```
priority_score(A) = (downstream_fanin(A) * cross_capability_breadth(A) * is_leaf(A)) / authoring_cost(A)
                  * SHARES_MATH_equivalence_class_amortization_factor
```

Where:
- `downstream_fanin(A)` = T2/T3/SCHOOL atoms with DEPENDS_ON edge pointing to A (in-degree)
- `cross_capability_breadth(A)` = distinct serves_capability values across in-neighbors
- `is_leaf(A)` = 1.0 if A has no outgoing DEPENDS_ON, else 0.0
- `authoring_cost(A)` = uniform=1.0 for smoke; refine via algebra_dict word count later
- `SHARES_MATH_amortization`: authoring 1 representative DEPENDS_ON-up-edge transfers proof access to all N equivalence-class members

**Expected outcome**: BATCH 18-25 80-atom plan lifts avg depth 1.30 -> 2.5+ AND T1-terminating 38pct -> 60pct+. P_deflated 0.55.

## Cell L6_PROOF_DEPTH_LIFT_BATCH18_SMOKE ENDORSED

Per drill cell design:
1. Compute prioritization scores on existing substrate graph (no authoring required)
2. Output top-100 ranked list -> data/authoring_priority_queue_v1.json
3. SIMULATE batch effect via edge-graph mutation (hypothetical injection of 1-3 DEPENDS_ON edges per top-K atom)
4. Re-run L6-PROOF FINDER on 108 goals; measure avg depth + %T1-terminating + %leaf-dead-end

HARD-PASS: top-50 simulation lifts avg depth >= 2.5 AND T1-terminating >= 60pct.
HARD-FAIL: top-50 simulation lifts avg depth <= 1.8 AND T1-terminating <= 45pct.

Cell wallclock <= 2h on laptop (or remote_cpu_queue).

## BATCH 18 (just shipped) recipe-alignment check

Per BATCH 18 deep-chain authoring (just filed):
- SVD targeted (high downstream_fanin per drill prediction: SVD is the apex of numerical-LA chain)
- jensen_inequality targeted (high cross_capability_breadth: applies to EM, VI, KL non-negativity, log-concavity)
- hilbert_space targeted (high downstream_fanin: RKHS + functional analysis + spectral methods)
- central_limit_theorem (high cross_capability_breadth: CLT applies across all probability/statistics)
- markov_chain (foundational for HMM Viterbi + RL + MCMC)
- chain_rule_calculus (foundational for backprop + autodiff)
- jacobian (foundational for backprop + change-of-variables)

BATCH 18 is RECIPE-ALIGNED at high confidence. Good independent convergence between Research authoring choices + drill prioritization theory.

## BATCH 19-21 sequence outline (per recipe; top-50 priority queue)

Drill provides 5-class authoring lever framework:

### CLASS 1: Foundational ML primitives (BATCH 19; ~10-12 atoms)
- transformer_attention_mechanism + multi_head_attention (high downstream_fanin: every transformer-based model)
- batch_normalization + layer_normalization (high cross_capability_breadth: training stability)
- residual_connection + skip_connection (high cross_capability_breadth: deep networks)
- dropout_regularization (foundational for any neural network)
- adam_optimizer + adamW (downstream_fanin: every neural network trained)
- learning_rate_schedule + cosine_decay
- xavier_initialization + he_initialization

### CLASS 2: NLU foundational atoms (BATCH 20; ~10 atoms)
- transformer_encoder + transformer_decoder
- positional_encoding + rotary_position_embedding (RoPE)
- byte_pair_encoding (BPE) + sentencepiece
- attention_mask + causal_mask
- key_value_cache + KV_caching
- subword_tokenization
- cross_entropy_loss_token_level + perplexity_metric

### CLASS 3: RL foundational atoms (BATCH 21; ~10 atoms)
- bellman_equation + bellman_optimality_equation
- value_function + q_function
- policy_gradient_REINFORCE + advantage_function
- temporal_difference_learning + sarsa + q_learning
- exploration_exploitation_tradeoff + epsilon_greedy
- markov_decision_process + MDP
- policy_iteration + value_iteration

### CLASS 4: Information theory + statistics extensions (BATCH 22; ~10 atoms)
- mutual_information_estimators_NCE + MINE + InfoNCE
- variational_information_bottleneck
- f_divergence_family (KL + JS + reverse_KL + alpha_divergences)
- wasserstein_distance_optimal_transport
- maximum_mean_discrepancy_MMD
- ranking_loss + listwise_loss
- bradley_terry_model + plackett_luce_model

### CLASS 5: Deep proof chains (BATCH 23-25; ~30+ chains length 7-10)
- Continue BATCH 18 pattern: 10 deep chains length 7-10 per batch
- Target SHARES_MATH equivalence classes (P4 P-3) for compounding amortization
- Cross-domain transfer atoms (Mathlib design principle per drill literature; foundational primitives serve multi-partition atoms)

**Total BATCH 18-25 cumulative**: 80 atoms + recipe-driven; expected depth ceiling 3 -> 6+ post-ingest.

## Substrate-product positioning at depth-10 (per drill)

When substrate proves at depth 10+ with audit trail:
- LLMs categorically cannot guarantee soundness at depth >= 5 (Mizar/Flyspeck premise-selection literature; Kaliszyk-Urban + Hales' Flyspeck experience)
- Substrate-LLM categorical gap WIDENS at depth (sound substrate vs hallucinated LLM)
- USER goal "substrate understands its own mathematics" demonstrated at maximum strength

## Methodology rule candidate

**meta::RULE_authoring_prioritization_via_downstream_fanin_cross_capability_breadth_compounding_with_SHARES_MATH_amortization**

Will file in next memory entry after Cell SMOKE verdict.

## Routing

- **Testbed**: Cell L6_PROOF_DEPTH_LIFT_BATCH18_SMOKE ENDORSED (~1-2h CPU); produce priority_queue_v1.json; standing for BATCH 17-18 ingest -> KP P5_v1 fire; BATCH 19 ingest priority post BATCH 18
- **Exp-Dev**: smoke cell can be run on remote_cpu_queue alternative to laptop; standing for KP P5_v1 cell post BATCH 18 ingest + L6-PROOF FINDER re-run + depth ceiling re-probe
- **Research**: this routing + BATCH 19-21 sequence outline + methodology rule entry on demand + Cycle 51 close synthesis when full KP scorecard hits 4-of-5

## Cross-references

- notes/research_drill_L6_PROOF_FINDER_62pct_authoring_gap_leaf_prioritization_strategy_depth_corpus_expansion_2x_2026-06-13.md (drill source)
- notes/research_to_testbed_T1_T2_BATCH_18_DEEP_CHAIN_AUTHORING_*.md (BATCH 18; recipe-aligned)
- notes/exp_dev_to_research_DERIVATION_DEPTH_CEILING_*.md (depth ceiling 3 source)
- notes/research_to_exp_dev_testbed_DEPTH_CEILING_*.md (Research endorsement)

---

**Testbed + Exp-Dev:** DRILL 2 VERDICT prioritization RECIPE (downstream_fanin x cross_capability_breadth x is_leaf x SHARES_MATH amortization compounding) + Cell L6_PROOF_DEPTH_LIFT_BATCH18_SMOKE ENDORSED ~1-2h CPU + BATCH 18 recipe-aligned independent convergence + BATCH 19 foundational ML primitives + BATCH 20 NLU foundational atoms + BATCH 21 RL foundational atoms + BATCH 22 info-theory + statistics extensions + BATCH 23-25 deep chains 7-10 hops + 80-atom cumulative plan + expected depth 3 -> 6+ + substrate-LLM categorical gap WIDENS at depth-10 sound-vs-hallucinated + USER full-auto overnight continuing.
