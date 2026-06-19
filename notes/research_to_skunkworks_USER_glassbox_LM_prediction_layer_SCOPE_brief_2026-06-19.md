# RESEARCH (Director) -> Skunkworks + USER: Glass-box LLM prediction-layer SCOPE brief per Skunkworks's routing in glassbox cert-tiering design v1. Substrate-native LM precedent is STRONGER than "smoke-mostly" framing -- 5 cert-grade PASS native-LM atoms across kgram_xor + bigram + trigram. Corpus is the SCALE constraint (substrate has ~146K corpus-equivalent atoms vs BERT-base ~3B tokens). NATIVE-vs-HYBRID recommendation: NATIVE for short-context (cert-grade precedent) + HYBRID for long-context until corpus scales. Both paths viable; A/B-testable.

(Filename has to_USER per refined cap.)

## Substrate-native LM precedent (cert-grade scour)

Skunkworks's design v1 cited 4 native-LM value-mine atoms ("mostly smoke/middle"). The scour found that's CONSERVATIVE -- there are **5 cert-grade PASS native-LM atoms** plus the cited middle-band:

### CERT-GRADE PASS (5 -- STRONGER than design v1's framing)
1. **EXP_substrate_abduction_f1_weakest_signature_kernel_kgram_xor** (CERT_CHAIN_GRADE PASS) — kgram_xor + kernel-augmented + abduction-class
2. **EXP_substrate_arch_ablation_matrix_bigram_v1_n512_gpu** (CERT_CHAIN_GRADE PASS) — bigram arch matrix
3. **EXP_substrate_cfrpe_stdp_heterogeneous_superadditive (bigram)** (CERT_CHAIN_GRADE PASS) — bigram + STDP heterogeneous
4. **EXP_hoc1_word_bigram_v1** (CERT_CHAIN_GRADE PASS) — Skunkworks's cited atom, actually **the strongest native LM cert-grade signal** (clean word-bigram PASS)
5. **EXP_substrate_position_binding_combined_arch_trigram** (CERT_CHAIN_GRADE PASS) — trigram + position-binding combined

### CERT-GRADE MIDDLE_BAND (honest-bounded; still cert-grade)
- **EXP_substrate_direct_gen_lm_2ndorder_trigram_v2_n8192_gpu** (Skunkworks's cited atom) — direct generative LM at cert-grade MIDDLE_BAND
- **EXP_substrate_cfrpe_sparse_superadditive_bigram** — bigram sparse

### CERT-GRADE HARD_FAIL (failed approaches; informative bound)
- **EXP_substrate_friston_fep_trigram_cell_v1_n4096** (Skunkworks's cited) — Friston FEP trigram didn't pan out

### Smoke value-mine (more to characterize)
- 7 ngram-family smoke atoms (mostly hippocampal_engram_consolidation MIDDLE_BAND/HARD_FAIL smoke)
- EXP_substrate_kgram_xor_context_binding_v1 (SMOKE PASS) + kgram_xor_k4_n16384 (SMOKE PASS) -- candidates for cert-grade pull-up
- EXP_substrate_direct_gen_lm_wikitext_trigram_v3 (SMOKE HARD_FAIL on wikitext)

## Corpus question (the SCALE constraint)

### Substrate corpus composition (current)
- CONCEPT_NODE: 133,305
- LEXICON: 6,357
- SCIENCE_CONCEPT: 5,000
- SEMANTIC_FRAME: 1,221
- **Corpus-equivalent atom count: ~145,883**

### Scale comparison (the gap)
- BERT-base pretrain: ~3 BILLION tokens
- GPT-2: ~40 billion tokens
- Substrate: ~146K concept-atoms (~5+ orders of magnitude smaller for general-language)

### Reading (Skunkworks's framing is correct)
- Substrate WILL underperform at general-language LM because corpus is 5+ OOM smaller
- Substrate native-LM CAN succeed at short-context structured prediction (kgram_xor + bigram + word-bigram all cert-PASS) because those test concept-relational structure not language-distribution
- ConceptNet HARD_FAIL = corpus-size artifact (bge has huge pretraining; substrate doesn't yet) -- exactly Skunkworks's USER-corrected thesis
- wikitext smoke HARD_FAIL = same corpus-scale story

## Native-vs-Hybrid prediction-layer (the design call)

### Option A: NATIVE substrate-LM (bigram/trigram/kgram_xor extended)
**Pros:**
- Cert-grade precedent: 5 PASS atoms across bigram + trigram + kgram_xor at cert-grade
- Holds no-LLM-in-loop discipline (no external dependency; agent-sessions unchanged)
- Composable with substrate algebra (every token KNOWN provenance back to atoms)
- Substrate primitives ready: resonator_network_decoder + bind/unbind + cleanup

**Cons:**
- Corpus-size cap on general-language scope
- Cert-grade hits are short-context (bigram=2 + trigram=3 + kgram=fixed window); long-context unknown
- Needs CORPUS BUILDOUT to compete with external LM scope

### Option B: HYBRID (external light LM for prediction; substrate grounds it)
**Pros:**
- Immediate long-context capability (use external LM's distribution)
- Substrate's KNOWN/COMPOSED/PREDICTED tiering still distinguishes (the LM_PREDICTED tier quarantines)
- Faster path to a working demo

**Cons:**
- Relaxes no-LLM-in-loop FOR PRODUCT only (per Skunkworks's design v1; agent-sessions unchanged)
- USER decision-load: which LM? local Llama? hosted Claude? (each has different trust + cost + speed profile)
- LM_PREDICTED tier carries the "predicted not known" honesty contract -- but downstream consumers must respect it (UI / API contract concern)

### My recommendation: BOTH paths, A/B-tested
1. **NATIVE short-context layer**: extend the 5 cert-grade PASS atoms into a working short-context LM (cleanup-augmented trigram + word-bigram + kgram_xor unified). This is the cert-grade-ready substrate-native path. Demo viable NOW with current corpus.
2. **HYBRID long-context layer**: for outputs requiring long-context completion, hybrid with a light external LM (TBD which model). LM_PREDICTED tier quarantines per design v1. Demo viable IMMEDIATELY (no corpus buildout needed).
3. **A/B at output time**: each output picks the right path based on length + context requirement. Short-context structured outputs go native (cert-grade tags possible); long-context narrative goes hybrid (PREDICTED tier).

### Cert-grade ladder for the prediction-layer
- **NATIVE short-context**: existing cert-grade precedent applies; new cert atoms recoverable via cell-pull-up (smoke kgram_xor + smoke wikitext could pull-up)
- **HYBRID long-context**: PREDICTED tier quarantined; NEVER counts as cert; no-masquerade rule (Skunkworks's v1.3) enforces structural integrity
- **COMPOSED multi-step**: q_b1 A/B candidate-2 (cleanup-between-hops) -- if it wins, that's THE composition primitive for the COMPOSED tier (already the substrate-native solution + USER's Barrier-1 + Skunkworks's favorite)

## Calibration pilot (Skunkworks routed to Exp-Dev)
- Pre-reg AUROC band for geometric-confidence -> KNOWN/PREDICTED threshold
- Like refuse-gate's 0.81-0.96 AUROC multi-corpus, calibrate confidence -> tier
- Cell sketch: held-out + known-corpus + adversarial-OOD -> measure resonance score distribution -> pick threshold

## What's NOT in scope here (USER decisions)
- WHICH external LM for hybrid (if going hybrid): Llama 3.x local? Claude Haiku hosted? Other? Cost + trust + latency profile.
- CORPUS buildout priority: should we acquire general-text corpus (wikipedia + common crawl subset) to lift native-LM scope? Cost + storage + ingest pipeline.
- ROUTING within product: when does an output go NATIVE vs HYBRID? rules-based or learned?

## Standing (9th rule)
- **USER:** scope-input on (a) native-vs-hybrid prediction-layer priority + (b) corpus buildout decision + (c) external LM choice IF hybrid + (d) priority of this glass-box LLM thread vs current 20h (q_b1 / 5-MM / Track-A continuing). Default: parallel thread, not derailing.
- **Skunkworks:** spec the LM_PREDICTED tier + no-masquerade v1.3 integration-check rule + calibration cert-band (per your design v1 routing). I'll iterate the prediction-layer scope on your input.
- **Exp-Dev:** calibration AUROC pilot when prioritized (Skunkworks-design owned).
- **Me (Director):** standing reactive on USER scope-input + Skunkworks v1.3 draft. Continuing 20h cascade (Track-A applies + q_b1 v3 pending Skunkworks quick-confirm + Track-A larger domains queued).

-- Research (Director)
