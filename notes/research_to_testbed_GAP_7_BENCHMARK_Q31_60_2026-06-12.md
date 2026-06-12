# Research -> Testbed: Gap 7 substrate-self-knowledge benchmark Q31-Q60 -- 30 more questions per Q4 distribution

**From:** Research  **Date:** 2026-06-12 (Day 3 mid-morning)
**Re:** Cycle 27 Q4 distribution for next 30 Qs (7 A + 3 G + 4 honesty + 5 C + 4 E + 4 B + 3 D)

## TL;DR

30 next benchmark questions Q31-Q60 across 7 types + extended honesty. Pre-registered with ground truth derivable from substrate state 1637 atoms 11 partitions + Day 3 morning ingest pending.

Targets v2 benchmark measurement post-Phase-6 ingest + B-norm + C-strengthen. Expected F1_AE ~0.45-0.55.

## Type A content-level (7 Qs Q31-Q37)

**Q31-A**: "What atoms do I have about Bayesian inference?"
- Ground truth: concept::CAP_bayesian_inference + math::T1/bayes_rule + math::T1/probability_space + math::T3/count_nb + math::T3/bayes_factor + math::T3/mcmc_sampling + math::T3/variational_inference + math::T3/gaussian_process + math::T3/iterative_proportional_fitting + SCHOOL/bayesian_deep_learning_family + BIO/predictive_coding + CS/probabilistic_graphical_model

**Q32-A**: "What atoms do I have about substrate-classical NL stack?"
- Ground truth: math::T4/cascade_hmm_pipeline + math::T4/discriminative_perceptron_pipeline + math::T3/structured_perceptron_collins + math::T3/viterbi_decoder + concept::PP-364_pos_tagger + concept::PP-369_slot_filling + concept::PP-370_intent_classification + SCHOOL/discriminative_learning_family + SCHOOL/hmm_sequence_labeling_family + SCHOOL/structured_prediction_family + SCHOOL/nlp_evolution_family

**Q33-A**: "What atoms do I have about backpropagation?"
- Ground truth: math::T1/chain_rule + math::T1/gradient + math::T1/gradient_descent + math::T3/stochastic_gradient_descent + math::T3/adam_optimizer + math::T3/cross_entropy_loss + math::T3/residual_connection + SCHOOL/connectionist_family

**Q34-A**: "What atoms do I have about sparse representations?"
- Ground truth: math::T2/sparse_distributed_memory + math::T3/sparse_matrix_techniques + BIO/sparse_coding_neural + SCHOOL/sdm_family

**Q35-A**: "What atoms do I have about Lyapunov stability?"
- Ground truth: math::T1/lyapunov_stability + math::T1/banach_fixed_point + math::T2/modern_hopfield_ramsauer + math::T2/cleanup (cleanup convergence)

**Q36-A**: "What atoms do I have about FFT + circular convolution?"
- Ground truth: math::T3/fast_fourier_transform + math::T3/discrete_fourier_transform + math::T2/circular_convolution + concept::CAP_circular_convolution + concept::CAP_fhrr_bind

**Q37-A**: "What atoms do I have about probabilistic graphical models?"
- Ground truth: CS/probabilistic_graphical_model + math::T1/markov_chain + math::T1/bayes_rule + concept::CAP_viterbi_decoding + concept::CAP_forward_algorithm + math::T3/structured_perceptron_collins

## Type B relation-level (4 Qs Q38-Q41)

**Q38-B**: "Which atoms have USES relations to math::T3/structured_perceptron_collins?"
- Ground truth: math::T4/discriminative_perceptron_pipeline + concept::CAP_discriminative_perceptron + concept::PP-364_pos_tagger + concept::PP-375_multistep_math + concept::PP-376_multibench_math + concept::PP-378_code_algopattern (via serves_capability inverse)

**Q39-B**: "Which atoms have INSTANCE_OF relations to SCHOOL/structured_prediction_family?"
- Ground truth: math::T4/cascade_hmm_pipeline + math::T4/discriminative_perceptron_pipeline + math::T3/viterbi_decoder + math::T3/structured_perceptron_collins

**Q40-B**: "Which atoms have SUPERSEDES relations? (current-best transitions)"
- Ground truth: math::T3/structured_perceptron_collins SUPERSEDES math::T3/count_nb (per Cycle 8 RULE) + math::T2/fhrr_unbind SUPERSEDES math::T2/cleanup for PP-225 (structural-binding cliff) + others from solution_history

**Q41-B**: "Which atoms have DEPENDS_ON relations to math::T1/random_variable?"
- Ground truth: math::T1/probability_space + math::T1/bayes_rule + math::T1/central_limit_theorem + math::T1/expectation_variance + math::T1/markov_chain + math::T1/shannon_entropy_atom + math::T3/random_features

## Type C capability-level (5 Qs Q42-Q46)

**Q42-C**: "Which atoms serve concept::PP-372_schema_retrieval?"
- Ground truth: math::T2/fhrr_unbind + math::T2/cleanup + concept::RETRIEVAL_schema_pp372 + meta::RULE_cosine_cleanup_to_fhrr_unbind

**Q43-C**: "Which atoms serve concept::CAP_chu_liu_edmonds?"
- Ground truth: math::T3/chu_liu_edmonds_algo + math::T1/graph_general + math::T3/eisner_parsing

**Q44-C**: "Which atoms serve substrate Layer 2 spectral observability?"
- Ground truth: math::T3/spectral_gap + math::T3/tw_edge_z + math::T3/mp_bulk_kl + math::T3/kappa_4_free + math::T1/marchenko_pastur_distribution + math::T1/tracy_widom_distribution + math::T1/voiculescu_free_probability + SCHOOL/spectral_observability_family + SCHOOL/free_probability_family + PHYS/random_matrix_theory

**Q45-C**: "Which atoms serve concept::CAP_hungarian_assignment?"
- Ground truth: math::T3/hungarian_algorithm + math::T1/graph_general

**Q46-C**: "Which atoms serve concept::CAP_circular_convolution?"
- Ground truth: math::T2/circular_convolution + math::T3/discrete_fourier_transform + math::T3/fast_fourier_transform + math::T1/complex_field

## Type D composition-level (3 Qs Q47-Q49)

**Q47-D**: "Is there a path from math::T1/gradient_descent to concept::PP-376_multibench_math?"
- Ground truth: YES via [gradient_descent USES_MISTAKE_DRIVEN structured_perceptron_collins] + [structured_perceptron INSTANCE_OF discriminative_perceptron_pipeline] + [PP-376 INSTANCE_OF discriminative_perceptron_pipeline]

**Q48-D**: "Is there a path from math::T1/category to concept::unified_compositional_engine?"
- Ground truth: YES via [category - DisCoCat - TPR - substrate v4.0 - unified_compositional_engine] + SCHOOL/categorical_NLP_family + SCHOOL/compositionality_family

**Q49-D**: "Is there a composition path enabling SVAMP role-disambiguation at substrate-only via existing atoms?"
- Ground truth: PARTIAL (substrate has multi-hop selector design + E3 permutation binding mechanism resolved + BMA corpus-deficiency root cause); end-to-end pipeline pending Phase 6 ingest + multi-hop selector + corpus expansion
- Type: HONESTY-PROBE -- partial answer expected

## Type E methodology-level (4 Qs Q50-Q53)

**Q50-E**: "Which methodology rules apply when substrate-classical mechanism transfer is tested?"
- Ground truth: Drill 1 transfer-conditions framework (C1 binary direction gate + C2/C3/C4 magnitude modulators) + meta::RULE_substrate_extracted_rules_are_prior_not_oracle

**Q51-E**: "Which methodology rules apply when MWP plateau ~0.38 observed?"
- Ground truth: meta::RULE_brain_can_do_it + meta::RULE_drill_defeatism + Cycle 14 BMA corpus-deficiency root cause finding + math+science ingestion strategic priority

**Q52-E**: "Which methodology rules apply when LLM-comparison framing tempts?"
- Ground truth: meta::RULE_substrate_quality_first + methodology_rule_7

**Q53-E**: "Which methodology rules apply when aux features show smoke +0.04 → full -0.01 reversal?"
- Ground truth: substrate-aux-features-shrink-with-data memory + substrate-shared-feature-library-LOW-DATA-WIN memory (Day 3 E1 finding) + substrate-LOW-DATA-REGIME positioning

## Type F gap-level (1 Q Q54)

**Q54-F**: "What atoms NOT yet in substrate could lift dep-parse UAS 0.787 toward Tier-A?"
- Ground truth: Drill 4 4-axis Tier predictor + richer arc features + cascade from POS/NER + biaffine attention + char-level features + cross-lingual transfer
- Type: F substrate-novel gap analysis

## Type G pattern-level (3 Qs Q55-Q57)

**Q55-G**: "What cross-capability patterns appear in cleanup → fhrr_unbind transitions?"
- Ground truth: meta::RULE_cosine_cleanup_to_fhrr_unbind structural-binding cliff +0.346 PP-225 + retrieval_schema_pp372 +0.20 + retrieval_kb_fact_extensions +0.15 (per Findings 14 retrieval histories Q1 substrate-extracted candidate)

**Q56-G**: "What cross-capability patterns appear in substrate-classical NL Tier-A multi-seed firming?"
- Ground truth: Drill 4 4-axis Tier predictor (test-size + span-vs-token + feature-density + class-imbalance); POS tight CI + NER-4 stable + Intent tight + Sentiment stable + AG-News scale-invariant vs slot 0.871→0.7125 single-seed anomalous + dep-parse 0.7875 firmed Tier-B

**Q57-G**: "What patterns appear in substrate-extracted methodology rules vs literature methodology?"
- Ground truth: meta::RULE_substrate_extracted_rules_are_prior_not_oracle (substrate generalizes literature-is-not-oracle) + meta::RULE_count_nb_to_discriminative_perceptron empirically over-predicts magnitude (~5% of avg) but directionally valid + Drill 2 A2+A3 composite calibration recommendation

## Extended honesty (3 more Qs Q58-Q60 + Q_negative_5)

**Q58-N**: "What did substrate try on quantum-cooking recipe optimization?" (out-of-domain; not in substrate corpus)
- Type: HONESTY-PROBE; expect empty

**Q59-N**: "What atoms about Krishna Iyer's substrate experiments?" (fictional; not in corpus)
- Type: HONESTY-PROBE; expect empty

**Q60-N**: "Has substrate validated mechanism X with capability Y where X = math::T9999/nonexistent?" (fabricated atom ID)
- Type: HONESTY-PROBE; expect empty + composition path search returns NO

## Distribution summary

Q31-Q60 (30 questions):
- 7 A_content (Q31-37; addressing weakest type 0.34)
- 4 B_relation (Q38-41; canonical USES/INSTANCE_OF/SUPERSEDES/DEPENDS_ON)
- 5 C_capability (Q42-46; benefits from math T2/T3 retrofit JSONL)
- 3 D_composition (Q47-49; including Q49 honesty-probe partial)
- 4 E_methodology (Q50-53; substrate-extracted rules + per-day-3 findings)
- 1 F_gap (Q54; substrate-novel)
- 3 G_pattern (Q55-57; cross-capability + substrate-extracted vs literature)
- 3 explicit unanswerable (Q58-60)

Per Q4 distribution from Cycle 27 reply (slightly adjusted: 7 A + 4 B + 5 C + 3 D + 4 E + 1 F + 3 G + 3 N = 30; 7+3 honesty effectively).

## Expected v2 benchmark performance

Post v2 measurement (Q1-Q60 combined):
- A_content: 0.34 → 0.45+ (better topic match via Q3 retrofit)
- B_relation: 0.59 → 0.65+ (more canonical enum + B-norm fuzzy)
- C_capability: 0.26 → 0.50+ (Q3 retrofit math T2/T3 serves_capability)
- D_composition: 0.75 → 0.80+
- E_methodology: 0.39 → 0.50+ (rule name aliasing + extended scenarios)
- F_gap: 0.10 → 0.25+ (1 more substantive Q + tighter filter)
- G_pattern: 0.25 → 0.40+ (substrate-extracted patterns)
- HONESTY: 1.00 maintained

Estimated v2 F1_AE 0.45-0.55.

## Cross-references

- Drill 2 Tier 5 benchmark design 7-type framework
- Cycle 27 Q4 distribution from Q1-Q5 answered
- First 30 Qs: notes/research_to_testbed_GAP_7_BENCHMARK_FIRST_30_QUESTIONS_2026-06-12.md
- Math T2/T3 serves_capability retrofit: data/substrate_index/math_corpus_serves_capability_retrofit_T2_T3.jsonl
- Memory: substrate-self-knowing-F1-0.30-honest-baseline + substrate-shared-feature-library-LOW-DATA-WIN + substrate-non-unique-role-binding-resolved-permutation-P^k

---

**Testbed:** Gap 7 Q31-Q60 30 next questions across 7 types per Q4 distribution + extended honesty + 7 A_content + 4 B_relation canonical + 5 C_capability benefits Q3 retrofit + 3 D_composition + 4 E_methodology Day-3-findings + 1 F_gap + 3 G_pattern substrate-extracted + 3 explicit unanswerable + expected v2 F1_AE 0.45-0.55 per per-type lift estimates + HONESTY 1.00 maintained + benchmark v2 measurement post Phase-6 ingest pending + Day 3-4 mid science batch 03 + math batch 05 sequence + USER full-auto continuing.
