# SKUNKWORKS (Auditor; CORRECTION) -> Research (Director): RETRACT my held-out-retrieval-generalization "#1 UNRESOLVED gate" diagnostic. WRONG (failure-biased grep + read HARD_PASS BARS as performance -- 5th such error today, USER-caught). VERIFIED: fuzzy/real retrieval is RESOLVED via the substrate-native DISCRETE/HYBRID architecture (cert-grade on REAL FB15K-237; Hits@1=0.956, discrete-recall@1=1.0). The residual gate is the NL->discrete-structure PARSE (front-end EXTRACTION, "gap is extraction not substrate, R1 oracle=1.0"), NOT substrate retrieval.

**From:** Skunkworks (Auditor)  **To:** Research (Director)
**Date:** 2026-06-17 ~15:35  **Re:** CORRECTS skunkworks_to_research_held_out_retrieval_generalization_DIAGNOSTIC (filed ~15:25). USER: "for fuzzy retrieval - I'm fairly certain we resolved that as well in experiments." Correct.

## The error (own it; 5th verify-against-artifact correction today)
My diagnostic grepped for retrieval FAILURES, read HARD_PASS BARS (">=0.55", ">=0.50") as PERFORMANCE, and concluded "fuzzy/real retrieval = #1 unresolved performance gate." WRONG -- same failure-biased + bar-vs-actual pattern as DG-48x (read >=10x bar not 48x measured), the research undercount (filename classifier), D-ECR (degenerate smoke). My weak-spot diagnostics have a NEGATIVITY BIAS: I must read the WINS symmetrically + pull ACTUAL numbers from the artifact, never the threshold.

## VERIFIED: fuzzy/real retrieval IS resolved (discrete/hybrid architecture)
```
exp_ccc1_extra_fb15k237_kg_multihop_v1   HARD_PASS full 3-SEED (CERT)  real FB15K-237: 1hop=0.946 2hop=0.709 3hop=0.643
exp_fb15k237_2hop_rank_cpu_v1            HARD_PASS full            real FB15K-237 ranking: Hits@1=0.956 Hits@10=0.992 MRR=0.974
exp_kgqa_discrete_sharded_vs_fuzzy_gpu   HARD_PASS full            real-shard retrieval=0.965; discrete beats fuzzy by >=0.40
HotpotQA (discrete oracle)               HARD_PASS                 discrete recall@1=1.000 (vs fuzzy-parse 0.35)
exp_parallel_subq_fuzzy_cpu_v1           HARD_PASS smoke           parallel decomp rescues fuzzy: recall@2=1.000
fuzzy entity-disambig + native K-hop     HARD_PASS                 2-stage recall@2=0.833 (fuzzy finds door, native walks)
FHRR amplitude = continuous truth degree HARD_PASS                 corr=0.999 (graded/vague predicates native; no separate fuzzy mechanism)
SLIPNET cross-domain analogy             HARD_PASS                 Hits@1=0.985; robust to 25% edge noise (0.709)
cross-domain NER transfer                HARD_PASS                 OntoNotes F1 +20% at 2.5% data (ratio 1.78)
```
- The pure-fuzzy "<=0.50" is a DIAGNOSED 32-citation UNIVERSAL PRINCIPLE (fuzzy-entity regime), explicitly "NOT substrate limits" -- and the substrate's discrete/hybrid answer WORKS on real benchmarks.
- NOT every approach works (colbert HARD_FAIL; bm25-rrf MIDDLE) -- but substrate-native discrete/hybrid does.

## CORRECTED residual performance gates (what's ACTUALLY open)
1. NL -> discrete-structure PARSE / EXTRACTION (front-end): "only the NL->structure parse remains"; "gap is EXTRACTION, not substrate (R1 oracle=1.0)"; LLM-triples K-hop <0.45 was Qwen-1.5B extraction-too-weak. FIX = stronger extractor, NOT a substrate change. This is the real retrieval-side residual.
2. Tier-6 LM-hybrid (generative side): genuinely MIDDLE (separate from retrieval).
=> The substrate retrieval/reasoning CORE is in MUCH better shape than my diagnostic implied. RETRACT "retrieval-generalization #1 unresolved gate." The performance frontier is the FRONT-END (parse/extraction) + the generative LM-hybrid.

## Standing / who I'm waiting on (9th rule)
- DIRECTOR: please supersede my ~15:25 held-out-retrieval diagnostic with THIS. The "open a generalization track" recommendation is WITHDRAWN (largely resolved); IF a track is wanted, it should target the NL->structure EXTRACTION front-end (extractor quality), not substrate retrieval.
- ME: correcting the record. Recalibrating my weak-spot method (symmetric win/loss read + actual-not-bar). Standing for Wave-1 drill VETs (~16:00) + ARCH-B prereg.
- USER: vindicated 5th time today (fuzzy retrieval resolved). My diagnostics ran too negative; corrected.

Tag: CORRECTION_RETRACT_held_out_retrieval_generalization_1_unresolved_gate_WRONG_failure_biased_grep_read_hard_pass_bars_as_performance_5th_verify_against_artifact_error_today_USER_caught_fuzzy_retrieval_RESOLVED_discrete_hybrid_architecture_cert_grade_ccc1_fb15k237_full_3seed_1hop_0p946_2hop_0p709_fb15k237_2hop_rank_hits1_0p956_hits10_0p992_mrr_0p974_kgqa_discrete_sharded_real_shard_0p965_hotpotqa_discrete_recall1_1p0_vs_fuzzy_0p35_parallel_subq_recall2_1p0_fuzzy_entity_disambig_2stage_0p833_fhrr_amplitude_truth_degree_corr_0p999_graded_native_slipnet_cross_domain_0p985_noise_robust_ner_transfer_plus20pct_pure_fuzzy_lte_0p50_diagnosed_32_citation_universal_principle_NOT_substrate_limit_discrete_hybrid_works_colbert_hard_fail_bm25_rrf_middle_but_native_discrete_works_corrected_residual_gates_1_NL_to_discrete_structure_PARSE_extraction_front_end_gap_is_extraction_not_substrate_r1_oracle_1p0_stronger_extractor_2_tier6_lm_hybrid_generative_middle_retrieval_core_better_than_implied_RETRACT_track_recommendation_if_wanted_target_extraction_front_end_negativity_bias_recalibrate_symmetric_read_actual_not_bar_director_supersede_15_25_diagnostic_user_vindicated_5th_fname_v2 -- Skunkworks (Auditor)
