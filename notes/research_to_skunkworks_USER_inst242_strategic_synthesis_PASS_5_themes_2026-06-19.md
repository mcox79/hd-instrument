# RESEARCH (Director) -> Skunkworks + USER: inst-242 strategic-synthesis pass (the 31 HIGH-rel non-cert wins grouped into 5 capability-themes per your routing). Recommend pull-up priority by THEME strategic-value: glass-box-LLM gold (11 atoms; product proof-points + confidence-tiering) > composition+reasoning (8) > substrate-native LM (5) > discipline (7). The glass-box-LLM gold theme is the program's strongest commercial-proof-points sitting un-cert-graded.

(Filename has to_USER per refined cap.)

## The 31 HIGH-rel non-cert wins grouped into 5 capability-themes

### THEME 1: Glass-box-LLM gold (11 atoms; HIGHEST strategic value)

**Substrate-beats-LLM head-to-heads (8) -- direct product proof-points; refute "can't predict" framing:**
- `EXP_ner_4type_headtohead_llm_gpu_v1` (NER substrate=0.711 vs Qwen-0.5B=0.202; +0.51 margin)
- `EXP_sentiment_headtohead_gpu_v1` (+ _calibrated_gpu_v1 + _calibrated_multiseed + _fair) -- sentiment substrate>=LLM AND ~5000x faster
- `EXP_textclass_headtohead_gpu_v1` (+ _calibrated_gpu_v1 + _calibrated_gpu_v1_smoke) -- text classification head-to-head

**Formal trust/integrity (3) -- the glass-box-LLM confidence-tiering layer:**
- `EXP_conformal_splitcp_cpu_v1` -- distribution-free coverage GUARANTEE >=0.95
- `EXP_calibration_isotonic_cpu_v1` -- calibrated probabilities ECE<0.05
- `EXP_uncertainty_math_cpu_v1` -- conformal + calibration on math op-classifier

**Strategic read:** these 11 atoms ARE the glass-box-LLM commercial proof story (substrate-beats-small-LLM + formal coverage guarantees + calibrated confidence). Un-cert-graded = un-defensible to external claims. This is the program's STRONGEST untapped commercial leverage.

### THEME 2: Composition + reasoning (8 atoms; q_b1 IMPROVE-track + COMPOSED tier)

- `EXP_phase4b_multistep_cpu_v1` (+ _multiseed_cpu_v1) -- substrate multi-step (2-op) >9x single-op baseline on MultiArith
- `EXP_phase4b_multibench_solver_cpu_v1` (+ _multiseed_cpu_v1) -- multi-benchmark solver composition
- `EXP_phase4d_code_fulldata_cpu_v1` (+ _multiseed_cpu_v1) -- code composition reasoning
- `EXP_e4_world_model_mwp_cpu_v1_smoke` -- world-model schema-simulation breaks discriminative plateau
- `EXP_substrate_concept_construct_1_carrier_extending_` -- substrate produces intensionally-novel proof-useful carriers INTERNALLY (NO LLM)

**Strategic read:** this IS the COMPOSED tier of the glass-box LLM + the q_b1 A/B-iterate IMPROVE-track ecosystem. composes with q_b1 candidate-2 cleanup-between-hops (the resonator/6x-depth smoke being cert-promoted via the active A/B).

### THEME 3: Substrate-native LM foundation (5 atoms; prediction-layer evidence)

- `EXP_substrate_tier1_ptb_accuracy_prover_cpu_v1` -- PTB accuracy
- `EXP_pos_discriminative_perceptron_cpu_v1` -- POS 0.92
- `EXP_ner_4type_multiseed_cpu_v1` -- NER multiseed (production-grade)
- `EXP_chunking_discriminative_cpu_v1` -- chunking
- `EXP_substrate_atis_slot_filling_fewshot_cpu_v1` -- ATIS slot-filling few-shot

**Strategic read:** Tier-1 NLP at production-grade. Composes with the 5 cert-grade native-LM PASS atoms I scouted earlier (kgram_xor + bigram + word-bigram + trigram). Together = robust short-context substrate-native LM evidence for the glass-box-LLM prediction-layer; supports NATIVE-path commitment.

### THEME 4: Substrate discipline + cycle-cleanup + audit quality (7 atoms; infrastructure)

- `EXP_substrate_79a_cycle_cleanup_capability_preservation`
- `EXP_substrate_82g_m4d_post_cleanup_f1_effect_cpu_v1`
- `EXP_substrate_aaa3_definitive_uniform_criterion_permutati`
- `EXP_substrate_distill_verify_3_1_inverse_pair_adversarial`
- `EXP_substrate_kp_p6_three_axis_tagging_crosstab_cpu_v1`
- `EXP_substrate_sr3_foundational_vs_frequency_curated_tools`
- `EXP_e1_substrate_crf_shared_lib_cpu_v1_smoke`

**Strategic read:** substrate quality + audit + cycle-cleanup. Important INFRASTRUCTURE but lower strategic-urgency vs themes 1-3. Pull up at-bandwidth.

## Recommended pull-up priority (value x cert-gap per Skunkworks ruling)

| Priority | Theme | Atoms | Value | Cert-gap | Action |
|----|----|----|----|----|----|
| 1 | Glass-box-LLM gold | 11 | HIGHEST (commercial proof story) | All LEGACY_EXCERPT (close-to-cert; need n_seeds + pre-reg) | RE-RUN priority cert-grade (the head-to-heads esp. ner_4type + sentiment + textclass + the 3 trust-layer) |
| 2 | Composition + reasoning | 8 | HIGH (COMPOSED tier + q_b1 ecosystem) | LEGACY_EXCERPT + 1 SMOKE | RE-RUN priority cert-grade (phase4b multistep + e4 world-model + concept_construct_1) |
| 3 | Substrate-native LM | 5 | HIGH (prediction-layer evidence) | LEGACY_EXCERPT | RE-RUN at-bandwidth |
| 4 | Discipline + cleanup | 7 | MEDIUM (infrastructure) | LEGACY_EXCERPT + 1 SMOKE | RE-RUN at-bandwidth |

## Strategic-synthesis recommendation (composes glass-box LLM design v1)

The glass-box-LLM gold theme (11 atoms) is **EXACTLY the product story** Skunkworks's glass-box-LLM design v1 articulates:
- substrate-beats-LLM head-to-heads = the KNOWN tier's RAW WIN
- conformal/calibration trust-layer = the KNOWN/COMPOSED/PREDICTED tier's confidence-tier mechanics
- combined = "fully-inspectable LLM that always knows + shows which words are known vs composed vs guessed, AND beats small LLMs at known structured tasks, AND has distribution-free coverage guarantees"

Pulling these 11 to cert-grade = the glass-box-LLM has its product proof-points cert-defensible. Without that, the design is conceptually-correct-but-empirically-uncertified.

## Top 3 immediate pull-up candidates (Tier-1 cert-grade RE-RUN)

1. **`EXP_ner_4type_headtohead_llm_gpu_v1`** -- highest-leverage substrate-beats-LLM proof; cert-grade RE-RUN = pre-reg the +0.51 margin band + n_seeds >=5 + same harness; Skunkworks per-atom verdict-VET
2. **`EXP_conformal_splitcp_cpu_v1`** -- distribution-free coverage GUARANTEE; cert-grade RE-RUN = pre-reg coverage band + held-out + n_seeds >=5
3. **`EXP_phase4b_multistep_cpu_v1`** -- composition >9x baseline; cert-grade RE-RUN = pre-reg multiplier band; aligns with q_b1 A/B-iterate ecosystem

## Routing
- **Skunkworks:** SCHEMA-VET this theme-grouping + pull-up priority ruling; atomize inst-242 with the value x cert-gap rule + the 5-theme grouping; first 3 candidates pre-reg SCHEMA-VET when Exp-Dev queues them
- **Exp-Dev:** standing reactive on Skunkworks pre-reg SCHEMA-VET -> cell-build cert-grade RE-RUN of top 3 candidates (post-reconciliation single-writer windows)
- **USER:** strategic-priority confirmation: glass-box-LLM gold theme TOP (11 atoms; direct product proof) OR redirect. My lean: glass-box-LLM gold top-priority; aligns with current glass-box LLM thread + Skunkworks's design v1 + commercial proof-points + un-cert-graded substrate's strongest leverage
- **Me (Director):** standing reactive on Skunkworks SCHEMA-VET + USER priority; reconciliation deferred until CLOSED then Track-A applies resume; standing reactive on q_b1 v3 cell-build verdict

-- Research (Director)
