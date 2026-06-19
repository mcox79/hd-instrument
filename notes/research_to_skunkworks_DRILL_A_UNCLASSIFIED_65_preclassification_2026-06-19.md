# RESEARCH (Director) -> Skunkworks: DRILL A DONE -- UNCLASSIFIED-65 pre-classification routing table. 65 cert atoms grouped by proposed domain + role-classification (CAPABILITY vs METHODOLOGY/ENGINE-VERIFY vs OTHER); per-atom confidence flagged. Findings: ~13 atoms likely RE-BUCKETABLE to existing domains (PP48_NKT family + q_b1 chain-depth + PP52 rollback + ...), ~10 are CANDIDATES-for-not-cert (multiseed-sweep / batch-result methodology artifacts), ~42 cleanly map to existing domains.

(Filename has to_skunkworks per refined cap.)

## Headline: 65 atoms / proposed routing

### A. Likely RE-BUCKETABLE to existing cap-int domains (~45)

**REASONING_MULTIHOP candidates (~10):**
- T3/EXP_hyp5_depth_ceiling_cpu_v1 (DISCRIMINATING_DEPTH_EXTENT) -- HYP-5 family; already-cert-integrated extension
- T3/EXP_q_b1_bisect_d{276,287,293}_v1_n16384 (PASS + 2 HARD_FAIL) -- q_b1 chain-depth bisection
- T3/EXP_q_b1_chain_depth_{300,400}_v1_n16384 (HARD_FAIL x2) -- q_b1 chain-depth limits (mini-cluster candidate: q_b1_bisect + chain_depth; ALL bound-or-fail)
- T3/EXP_active_inference_dpefe_h2_cpu_v1 (PASS) + T3/EXP_active_inference_e2_tuned_cpu_v1 (MIDDLE_BAND)
- T3/EXP_substrate_cognitive_core_counterfactual_v1 (PASS)
- T3/EXP_combo2_p4_l3_signed_am_v1_n32768_5seed_verification_v1 (PASS)
- T3/EXP_combo3_pp51_5method_on_implicit_gram_v2_cert_fix_n4096 (MIDDLE_BAND) + T3/EXP_combo3_unified_api_v1_n32768_5seed_verification_v1 + T3/EXP_combo3_unified_api_v1_n32768_local (BOTH MIDDLE_BAND)

**COGNITIVE_CAPACITY candidates (~15):**
- T3/EXP_pp48_nkt_depth_{3_baseline, 11}_v1_n4096 (PASS x2) -- PP48_NKT cluster scale-points (would fold into existing 11-member cluster -> ~13 members)
- T3/EXP_pp49_hrc_{cf_depth_band_sweep, cross_n_d4_d6_d8, deeper_d_d10_d12_d14} -- 3 atoms; verdict-mixed (2 HARD_FAIL + 1 MIDDLE_BAND); SINGLETONS per decomp lesson
- T3/EXP_pp58_scs_tau_sweep_d8_tau{010,020,030,050}_v1_n8192 (3 HARD_FAIL + 1 MIDDLE_BAND) -- MIXED-verdict; SINGLETONS
- T3/EXP_substrate_cfrpe_sparse_superadditive_bigram_v1 (MIDDLE_BAND) + T3/EXP_substrate_cfrpe_stdp_heterogeneous_superadditive_bigram_v1 (PASS)
- T3/EXP_substrate_continual_learning_30day_realistic_stream_v1 (PASS) + T3/EXP_substrate_continual_learning_empirical_10e9x_v1 (MIDDLE_BAND)
- T3/EXP_substrate_long_conversation_10k_exchanges_v1 + T3/EXP_substrate_long_conversation_scale_1000_exchanges_v1 (PASS x2)
- T3/EXP_substrate_task_complexity_sweep_v1_512_8192_gpu (PASS)

**RETRIEVAL candidates (~5):**
- T3/EXP_pp52_exact_rollback_n{4096,8192,16384}_v1 (PASS x3) -- PP52 family scale-points; uniform-PASS mini-cluster candidate
- T3/EXP_substrate_hallucination_robustness_hard_negatives_v1 (PASS)
- T3/EXP_substrate_kf1_ngram_augmented_v1 (HARD_FAIL)

**REFUSE_GATE candidates (~3):**
- T3/EXP_deletion_cert_z_ratio_n16384{,_full_alpha}_v1 (PASS x2)
- T3/EXP_c_infty_seb_detection_full_v3 (PASS)

**NLP_LANGUAGE candidates (~2):**
- T3/EXP_substrate_direct_gen_lm_2ndorder_trigram_v2_n8192_gpu (MIDDLE_BAND)
- T3/EXP_substrate_friston_fep_trigram_cell_v1_n4096 (HARD_FAIL)

**ARCHITECTURE candidates (~3):**
- T3/EXP_substrate_last_token_vs_whitening_mean_pool_v1 (PASS) -- pooling strategy
- T3/EXP_substrate_concept_level_lm_proxy_v1_n2048_gpu (MIDDLE_BAND)
- T3/EXP_matrix_trace_primitives_full_v3 (PASS) + T3/EXP_symbolic_prim_battery_v1 (PASS) + T3/EXP_spectral_mp_primitives_full_v3 (MIDDLE_BAND)

**SUBSTRATE_INTEGRITY candidates (~2):**
- T3/EXP_caching_eviction_cost_amortized_v1 (MIDDLE_BAND)
- T3/EXP_r_alpha_throughput_full_v3 (PASS)

**OTHER candidates (~5):**
- T3/EXP_multiagent_coord_full_v3 (PASS) -- multi-agent (no current domain match)
- T3/EXP_planted_csp_viability_full_v3 (PASS) -- CSP planted; could be reasoning or substrate
- T3/EXP_csp_memory_warm_start_full_v3 (PASS)
- T3/EXP_hoc1_word_bigram_v1 (PASS) -- bigram-related
- T3/EXP_substrate_stage_a_training_speed_full_shakespeare_extctx_K8_v1_n8192_gpu (MIDDLE_BAND) -- training-speed
- T3/EXP_substrate_abduction_f3_hmm_headroom_realgap_deployment_cpu_v1 (PASS) -- abduction
- T3/EXP_substrate_kgram_xor_k4_sweep_v1 (MIDDLE_BAND) -- kgram-xor sweep

### B. CANDIDATES-FOR-NOT-CERT (~10; Skunkworks may exclude from Track-A)

These look like ENGINE-VERIFICATION / METHODOLOGY runs, not capability claims per se:
- T3/EXP_lambda_batch_results_deletion_cert_zratio_n32768_v1_bd9c5a0f_data_exp_del (PASS) -- batch-result metadata; not a capability per se
- T3/EXP_lambda_batch_results_q_b1_depth_extended_n32768_bd9c5a0f_data_exp_q_b1_de (PASS) -- batch-result metadata
- T3/EXP_lambda_batch_results_qd1_spectral_primitives_n32768_v1_bd9c5a0f_data_exp_ (MIDDLE_BAND) -- batch-result metadata
- T3/EXP_tier4_multiseed_sweep_cpu_v1 (PASS) -- multiseed-sweep verification (engine-test pattern?)
- T3/EXP_v32_multiseed_cpu_v1 (MIDDLE_BAND) -- multiseed verification
- T3/EXP_wave1_multiseed_sweep_cpu_v1 (PASS) -- multiseed-sweep verification
- T3/EXP_wave1_tier1_sweep_cpu_v1 (PASS)
- T3/EXP_wave2_rescue_multiseed_sweep_cpu_v1 (PASS) -- multiseed-sweep rescue
- T3/EXP_pp33_mfpt_glauber_n32768_v2_n32768 (MIDDLE_BAND) -- pp33 family; possible scale-point
- T3/EXP_pp49_hrc_deeper_d_d10_d12_d14_v1_n8192 (MIDDLE_BAND) -- could be capability OR ablation
- T3/EXP_pp52_hebbian_lora_speedup_n4096_v1 (HARD_FAIL) -- HRC speedup; could be infrastructure metric
- T3/EXP_membership_auroc_mapping_v1 (PASS) -- AUROC mapping (likely cert-eval methodology)

### C. Discipline-flag

- **t5c family already in retrieval cap-int** (existing). UNCLASSIFIED has NO t5c atoms = good (no cross-domain duplication).
- **pp52 family**: 3 atoms in cognitive_capacity (existing pp52_one_shot_addition cluster); 3 atoms here (pp52_exact_rollback) -- different sub-capability; SEPARATE cluster recommended.
- **pp48_nkt** atoms in UNCLASSIFIED (depth_3_baseline + depth_11) are SCALE-POINTS of the existing 11-member cluster -> integrate via cluster-extend (not new cluster).
- **q_b1 chain-depth** family (6 atoms) is a NATURAL cluster candidate (uniform-bound-on-deep + PASS-on-shallow; depth-cliff pattern; reasoning_multihop domain).

## Routing recommendation

- **Skunkworks per-row VET:** validate my proposed-domain assignments (especially for the OTHER + CANDIDATES-FOR-NOT-CERT buckets); confirm cluster-extends; per-row verdict-faithful as usual.
- **My follow-on (post-VET):** apply Track-A on the re-bucketed UNCLASSIFIED atoms domain-by-domain (alongside the remaining 8 domains).

## Drills schedule
- A (UNCLASSIFIED-65): DONE (this note).
- B (ConceptNet eval design): SUFFICIENT (covered by Exp-Dev pre-reg v1.1 + Skunkworks SCHEMA-VET PASS via the freeze-window online drills).
- C (Track-B at-scale gap classification): NEXT (after A).
- D (A/B-iterate mechanism spec): after C.
- E (Substrate-as-product positioning): after D.

-- Research (Director)
