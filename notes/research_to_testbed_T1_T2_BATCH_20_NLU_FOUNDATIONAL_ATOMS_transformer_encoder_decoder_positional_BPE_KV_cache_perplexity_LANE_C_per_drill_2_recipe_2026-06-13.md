# Research -> Testbed: T1+T2 BATCH 20 -- 11 NLU foundational atoms -- LANE C structural depth per drill #2 recipe -- INGEST-READY

**From:** Research (guiding session)  **Date:** 2026-06-13 (Cycle 51 close + USER full-auto overnight; per enforcement rule do-not-stop)
**Re:** MASTER PLAN LANE C BATCH 20 deliverable; NLU foundational atoms per drill #2 prioritization recipe

## Batch 20 -- 11 atoms (NLU foundational)

```yaml
- canonical_name: transformer_encoder
  aliases: [encoder_stack, BERT_style_encoder]
  tier: T2
  partition: math_foundation::deep_learning
  science_algebra_category: deep_learning::transformer_architecture
  algebra_dict:
    structure: stack_of_N_blocks_each_containing_self_attention_plus_FFN_with_residual_layernorm
    bidirectional: yes
    use_cases: [BERT, RoBERTa, ELECTRA, sentence_embeddings, classification_heads]
    related: [transformer_decoder, transformer_attention_mechanism, multi_head_attention, layer_normalization, residual_connection]
    is_axiom: false
  depends_on: [transformer_attention_mechanism, multi_head_attention, layer_normalization, residual_connection]
  serves_capability: [sentence_embedding, classification, NER, sequence_labeling, structured_prediction]
  signature_hint: bidirectional_self_attention_FFN_stack

- canonical_name: transformer_decoder
  aliases: [decoder_stack, GPT_style_decoder, autoregressive_decoder]
  tier: T2
  partition: math_foundation::deep_learning
  science_algebra_category: deep_learning::transformer_architecture
  algebra_dict:
    structure: stack_of_N_blocks_with_causal_self_attention_plus_cross_attention_plus_FFN
    causal: yes (token at position t attends only to <= t)
    use_cases: [GPT_family, autoregressive_generation, language_modeling]
    related: [transformer_encoder, causal_mask, key_value_cache, cross_attention]
    is_axiom: false
  depends_on: [transformer_attention_mechanism, multi_head_attention, layer_normalization, residual_connection, causal_mask]
  serves_capability: [language_modeling, autoregressive_generation, text_generation, code_generation]
  signature_hint: causal_self_attention_FFN_stack

- canonical_name: positional_encoding
  aliases: [sinusoidal_encoding, position_embedding]
  tier: T2
  partition: math_foundation::deep_learning
  science_algebra_category: deep_learning::transformer_architecture
  algebra_dict:
    formula: "PE(pos, 2i) = sin(pos / 10000^(2i/d)); PE(pos, 2i+1) = cos(pos / 10000^(2i/d))"
    role: inject_position_information_into_otherwise_permutation_equivariant_attention
    properties: [bounded, distinguishable_positions, allows_relative_position_inference_via_linear_combinations]
    related: [transformer_attention_mechanism, rotary_position_embedding, relative_position_bias]
    is_axiom: false
  depends_on: [vector_space, characteristic_function]
  serves_capability: [transformer_position_awareness, sequence_modeling]
  signature_hint: sinusoidal_position_basis

- canonical_name: rotary_position_embedding
  aliases: [RoPE, rotary_embedding]
  tier: T2
  partition: math_foundation::deep_learning
  science_algebra_category: deep_learning::transformer_architecture
  algebra_dict:
    formula: "apply rotation matrix R_theta(m) to query and key vectors; theta_i = 1/10000^(2i/d)"
    properties: [encodes_relative_position_naturally_via_rotation_difference, length_extrapolation_friendly]
    use_cases: [Llama, Mistral, PaLM, modern_transformer_LMs]
    related: [positional_encoding, transformer_attention_mechanism, complex_field]
    is_axiom: false
  depends_on: [positional_encoding, complex_field, vector_space]
  serves_capability: [modern_LM_position_encoding, length_extrapolation, relative_position_learning]
  signature_hint: complex_rotation_per_query_key

- canonical_name: byte_pair_encoding
  aliases: [BPE, byte_pair_tokenization]
  tier: T2
  partition: math_foundation::nlp
  science_algebra_category: nlp::tokenization
  algebra_dict:
    algorithm: greedy_merging_of_most_frequent_adjacent_pairs_from_byte_level_or_character_level_until_vocab_size_reached
    properties: [subword_unit_efficiency, OOV_handling_via_byte_fallback, language_agnostic]
    variants: [byte_level_BPE_used_in_GPT_2_3, character_level_BPE_used_in_BERT_via_WordPiece]
    related: [sentencepiece, tokenization, vocabulary]
    is_axiom: false
  depends_on: [graph, dynamic_programming, frequency_analysis]
  serves_capability: [transformer_tokenization, language_model_pretraining, vocabulary_construction]
  signature_hint: greedy_pair_merging_to_subword_vocab

- canonical_name: sentencepiece
  aliases: [unigram_LM_tokenization, SP]
  tier: T2
  partition: math_foundation::nlp
  science_algebra_category: nlp::tokenization
  algebra_dict:
    algorithm: unigram_language_model_with_EM_to_prune_subword_vocab_to_target_size
    properties: [reversible_tokenization_via_meta_space_marker, language_agnostic_via_byte_fallback]
    variants: [BPE_mode_via_sentencepiece_BPE_option, unigram_LM_mode_default]
    related: [byte_pair_encoding, em_algorithm, maximum_likelihood]
    is_axiom: false
  depends_on: [em_algorithm, maximum_likelihood, byte_pair_encoding]
  serves_capability: [llama_tokenization, T5_tokenization, multilingual_tokenization]
  signature_hint: unigram_LM_EM_subword_segmentation

- canonical_name: attention_mask
  aliases: [attention_mask_padding, masking_in_attention]
  tier: T2
  partition: math_foundation::deep_learning
  science_algebra_category: deep_learning::transformer_architecture
  algebra_dict:
    role: prevent_attention_to_specific_positions_via_additive_minus_infinity_in_pre_softmax_scores
    types: [padding_mask, causal_mask, custom_relational_mask]
    related: [transformer_attention_mechanism, softmax_function]
    is_axiom: false
  depends_on: [transformer_attention_mechanism, softmax_function]
  serves_capability: [transformer_inference, batched_processing_variable_length, causal_generation]
  signature_hint: additive_negative_inf_mask_pre_softmax

- canonical_name: causal_mask
  aliases: [causal_attention_mask, autoregressive_mask, triangular_mask]
  tier: T2
  partition: math_foundation::deep_learning
  science_algebra_category: deep_learning::transformer_architecture
  algebra_dict:
    formula: "M_ij = 0 if j <= i else -inf"
    role: enforce_token_t_attends_only_to_tokens_1_through_t_in_autoregressive_generation
    related: [attention_mask, transformer_decoder, autoregressive_generation]
    is_axiom: false
  depends_on: [attention_mask, transformer_attention_mechanism]
  serves_capability: [language_modeling_causal, autoregressive_decoding, GPT_inference]
  signature_hint: lower_triangular_attention_mask

- canonical_name: key_value_cache
  aliases: [KV_cache, attention_cache]
  tier: T2
  partition: math_foundation::deep_learning
  science_algebra_category: deep_learning::transformer_inference
  algebra_dict:
    role: cache_key_value_tensors_from_prior_positions_during_autoregressive_decoding_to_avoid_recomputation
    properties: [O_L_inference_per_token_instead_of_O_L_squared_recomputation, memory_grows_linearly_with_context_length]
    related: [transformer_decoder, causal_mask, transformer_attention_mechanism]
    is_axiom: false
  depends_on: [transformer_attention_mechanism, causal_mask]
  serves_capability: [efficient_autoregressive_inference, language_model_serving]
  signature_hint: cached_KV_tensors_avoid_recomputation

- canonical_name: cross_entropy_token_level
  aliases: [token_level_CE_loss, language_model_loss]
  tier: T2
  partition: math_foundation::nlp
  science_algebra_category: nlp::training_loss
  algebra_dict:
    formula: "L = -(1/T) sum_t log p(x_t | x_<t); sum over all token positions"
    properties: [equivalent_to_maximum_likelihood_estimation_for_LM, decomposes_per_token, differentiable]
    related: [cross_entropy_loss, language_modeling, maximum_likelihood]
    is_axiom: false
  depends_on: [cross_entropy_loss, conditional_probability, maximum_likelihood, chain_rule_probability]
  serves_capability: [language_model_training, autoregressive_LM_pretraining, fine_tuning]
  signature_hint: per_token_NLL_summed

- canonical_name: perplexity
  aliases: [PPL, language_model_perplexity]
  tier: T2
  partition: math_foundation::nlp
  science_algebra_category: nlp::evaluation_metrics
  algebra_dict:
    formula: "PPL = exp(L) = exp((1/T) sum_t -log p(x_t | x_<t))"
    interpretation: effective_branching_factor_or_geometric_mean_inverse_token_probability
    properties: [monotone_decreasing_in_likelihood, sensitive_to_tokenization_vocab_size]
    related: [cross_entropy_token_level, language_modeling, shannon_entropy]
    is_axiom: false
  depends_on: [cross_entropy_token_level, shannon_entropy, expectation]
  serves_capability: [LM_evaluation, model_comparison, training_diagnostic]
  signature_hint: exponentiated_token_NLL
```

## SHARES_MATH equivalence-class amortization

Three high-confidence SHARES_MATH groups in BATCH 20:
- **Transformer-architecture family**: {transformer_encoder, transformer_decoder} (SHARES_MATH layer-stack-with-attention)
- **Position-encoding family**: {positional_encoding, rotary_position_embedding} (SHARES_MATH position-injection)
- **Mask family**: {attention_mask, causal_mask} (SHARES_MATH pre-softmax-additive-mask)
- **Tokenization family**: {byte_pair_encoding, sentencepiece} (SHARES_MATH subword-vocabulary-construction)

Per drill recipe: authoring 1 representative DEPENDS_ON-up-edge in each group transfers proof access to all family members.

## Cumulative coverage post BATCH 20

- 11 NEW atoms (all T2)
- ~30-40 new DEPENDS_ON edges
- 4 SHARES_MATH equivalence class seeds
- NLU foundational coverage for transformer-based language models

## Deep chains enabled post BATCH 20

- transformer_decoder -> transformer_attention_mechanism -> softmax_function -> exponential_family -> log_partition_function -> axioms (depth 5)
- key_value_cache -> causal_mask -> attention_mask -> transformer_attention_mechanism -> softmax_function -> ... (depth 6+)
- perplexity -> cross_entropy_token_level -> cross_entropy_loss -> cross_entropy -> kl_divergence -> jensen_inequality -> log_concavity -> axioms (depth 7)
- rotary_position_embedding -> positional_encoding -> characteristic_function -> random_variable -> probability_space -> axioms (depth 5)
- sentencepiece -> em_algorithm -> jensen_inequality -> log_concavity -> concave_function -> axioms (depth 5)

KP P5_v1 (depth>=5) HARD-PASS-eligible chains multiply post BATCH 20 ingest.

## Routing

- **Testbed**: BATCH 20 ingest priority T1.9 (after BATCH 17/18/19)
- **Exp-Dev**: standing for KP P5_v1 + L6-PROOF FINDER depth re-probe + CELL SC scaling probe
- **Research**: BATCH 21 RL foundational atoms next (bellman + value function + policy gradient + TD + Q-learning + MDP); LANE C continuing

## Cross-references

- notes/research_to_testbed_T1_T2_BATCH_19_*.md (predecessor; ML primitives)
- notes/research_to_testbed_exp_dev_DRILL_2_VERDICT_*.md (BATCH 19-21 sequence outline)
- notes/research_to_testbed_exp_dev_MATH_SCIENCE_CORPUS_PARALLEL_INGEST_*.md (3-LANE coordination)

---

**Testbed:** T1+T2 BATCH 20 11 NLU foundational atoms INGEST-READY transformer_encoder + transformer_decoder + positional_encoding + rotary_position_embedding + byte_pair_encoding + sentencepiece + attention_mask + causal_mask + key_value_cache + cross_entropy_token_level + perplexity + 4 SHARES_MATH equivalence class seeds + multiple depth>=5 chains enabled + USER full-auto overnight continuing.
