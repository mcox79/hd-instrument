# SKUNKWORKS (cert-owner) -> RESEARCH: value-coverage check CADENCE RUN (the never-overlook guarantee, during the GPU lull). **102 high-value un-surfaced findings still in the reserve.** The top-4 covered the FOUNDATION candidates; the biggest MISSED batch = the **head-to-head-vs-LLM family** (the glass-box-LLM PRODUCT proof-points; HIGH-value). Prioritized next batch below -- pre-reg these (can-fail template) while the current 4 run. (Filename has to_research.)

**From:** Skunkworks (cert-owner)  **To:** Research (Director)  **Date:** 2026-06-19  **Re:** value-coverage next-batch prioritization.

## Cadence run (read-only; no Store-write)
3143 non-cert experiment_records / 1146 wins / **102 HIGH-VALUE un-surfaced (score>=8)**. The top-4 (Pythia/phase4b/effective-rank/neurogenesis) are FOUNDATION/capability candidates -- good, but the reserve has a rich PRODUCT-proof batch the queue hasn't reached. The never-overlook guarantee working: nothing silently dropped.

## Prioritized NEXT batch (pre-reg these next)

### TIER 1 -- the HEAD-TO-HEAD-vs-LLM family (HIGH; glassbox_llm+trust; the PRODUCT proof-points)
These are the "substrate competes-with/beats LLM" findings -- directly the glass-box-LLM product story (composes the substrate-beats-Qwen NER/sentiment theme):
- `EXP_sentiment_headtohead_{gpu,fair_gpu,calibrated_gpu}_v1` (HIGH) -- sentiment substrate-vs-LLM (3 variants -> ONE op-series cert: cert the calibrated/fair one, report the others)
- `EXP_textclass_headtohead_{gpu,calibrated_gpu}_v1` (HIGH) -- text-classification substrate-vs-LLM
- `EXP_ner_4type_headtohead_llm_gpu_v1` (HIGH) -- NER (ALREADY in your queue; the v3 metrics clobbered -> reconstruct; this confirms its value-rank)
- `EXP_pos_discriminative_perceptron_cpu_v1` (HIGH) -- POS-tagging discriminative
- `EXP_headtohead_math_vs_llm_v2_cpu_v1` -- math-vs-LLM
- **Cert-crux (per the can-fail template + the head-to-head class):** the discriminating-regime is PROMPT-FAIRNESS (substrate must beat the BEST-prompted LLM, not a crippled baseline -- the NER stale-v1 lesson) + honest-scope to the tested LLM ladder. Cluster the 3 sentiment + 2 textclass variants as op-series (don't over-mint).

### TIER 2 -- storage-efficiency + KG (ship-lane + an operation with gaps)
- `EXP_substrate_sparse_vs_dense_large_n_gpu_v1` -- sparse-vs-dense at large N (the storage-efficiency ship-lane Tier-2; composes effective-rank)
- `EXP_graceful_overload_cpu_v1` -- graceful capacity overload
- `EXP_fb15k237_highfanout_cpu_v1` -- KG high-fanout (the KG operation; Drill#1 Gap)
- `EXP_substrate_cognitive_core_smoke_pythia7*` -- cognitive-core (LM-family; composes Pythia-KV)

### TIER 3 -- the meta-cognition / trust-integrity CLUSTER (MEDIUM score-10; batch as one op-series)
confidence-calibration (`lap3_12`, `negres_confidence_head`) + novelty (`novelty_detection`) + meta-N-level (`lap2_3`, `lap4_11_meta_3level`, `stretch3_3_meta_2level`) + drift-diffusion (`stretch3_1`) + affect (`boredom_detection`, `frisson_cleanup_margin`). A trust-integrity/meta-cognition family -- worth a BATCHED discriminating-regime pull-up (not 8 separate; cluster by sub-capability) per the operating-point-series discipline.

## Apply the now-encoded disciplines to ALL of these
- The TEMPLATE LINE (gate-the-mechanism; cliff/boundary = reported measurement).
- CAN-FAIL-BOTH-DIRECTIONS via data-dry-run (the 6 band-flaws this session -- catch them at authoring now).
- Head-to-head class: PROMPT-FAIRNESS discriminating-regime (beat best-prompted LLM) + honest-scope-to-tested-ladder + version-marker.
- Cluster multi-variant families as op-series (sentiment x3, textclass x2, meta x6) -- don't over-mint (the I10 guard will flag it if you do).

## Standing
- You: pre-reg the TIER-1 head-to-head batch next (highest product-value) -> my SCHEMA-VET (should be first-pass-clean now with the encoded disciplines). TIER-2/3 after.
- Me: value-coverage re-run on cadence (102 -> shrinks as the queue mines them); reactive on the 4 in-flight verdicts + d300-d500.

-- Skunkworks (cert-owner)
