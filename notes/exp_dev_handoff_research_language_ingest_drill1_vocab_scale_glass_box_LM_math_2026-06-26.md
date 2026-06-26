# exp_dev hand-off -- research: language ingest drill 1 (vocab scale + glass-box LM math requirements)

**Filed-by:** Research (Opus 4.7 1M)
**Date:** 2026-06-26
**Trigger:** notes/research_language_ingest_drill1_vocab_scale_glass_box_LM_math_2026-06-26.md (drill 1 of 3 in language-ingest series; bigram-gap closure + vocab-scale capacity verification)

## Pause state

Check `data/orchestrator_paused.flag` before dispatching. If paused, file this hand-off, do NOT dispatch. Director will pick up post-resume.

Per [[feedback-no-experiment-design-in-prompts]]: anchors below are POINTERS not full cell specs. Author cells per substrate-physics + the research note's L3/L5/L7 composition guidance. Pre-reg bands in the research note's "Falsifiable predictions" section are LOAD-BEARING -- bake them into the prereg verbatim.

## Anchor candidates (rank-ordered)

### Anchor 1 (top priority): n5_trigram_concept_lm_v1

- **Anchor pointer:** `experiments/exp_n5_trigram_concept_lm_v1.py` (new cell; extends `exp_n1_concept_lm_substrate_native_token_decode_v3_1.py`)
- **Substrate-product reading:** "substrate-native trigram-CONCEPT-transition LM via HRR sequence-binding of 2-prior concepts; tests whether context-depth closes the 1.13-bit gap to text8 word-bigram; if HARD_PASS, substrate-LM crosses word-bigram parity -- the first measurable LM-class win on real text"
- **Tier hint:** chain-grade candidate IF substrate_bpc <= 4.3 (closes >= 0.66 of 1.13-bit gap) AND cv <= 0.05 AND zero LLM calls AND ARM_TRIGRAM_HRR_PLUS_BACKOFF wins; otherwise MIDDLE_BAND if substrate_bpc in (4.3, 4.7]; HARD_FAIL if substrate_bpc > 4.7 OR depth_gain negative
- **Why now:** USER directive 2026-06-26 to start substrate-native language ingest. n2 capacity-scaling already proved N-scaling alone reaches 4.96 floor; n3 MKN only +0.068 bits; n4 k-WTA HARD_FAIL; n10 whitening HARD_FAIL. Context-depth is the UNTESTED structural lever and Skunkworks PoC validates the closure direction.
- **Composition:** uses `hdlab/char_trigram_encoder.py` (basis; deterministic hash; no change) + V_C=1024 concept codebook (continued from n1v3) + `hdlab/sequence_memory.py` (c3 chain-grade primitive; HRR bind of 2 prior concepts) + `hdlab/iterative_attractor.py` (cleanup memory) + count-proportional decode + Jelinek-Mercer interpolation + Witten-Bell trigram backoff in ARM_TRIGRAM_HRR_PLUS_BACKOFF
- **Arms (3 mandatory):** ARM_BIGRAM_BASELINE (reproduces n2 N=16384 V_C=1024 at 4.96 BPC); ARM_TRIGRAM_HRR (HRR-bound 2-prior context); ARM_TRIGRAM_HRR_PLUS_BACKOFF (HRR + Witten-Bell backoff to bigram when trigram count below threshold)
- **Cost estimate:** ~5 min smoke / ~4-6 hr local_cpu full (3 seeds; text8 100k docs; N=16384; V_C=1024)
- **Pre-reg bands (verbatim from research note Section "Cheap decisive test" + Section 7):** HARD_PASS substrate_bpc <= 4.3 (P=0.25); MIDDLE_BAND in (4.3, 4.7] (P=0.45); HARD_FAIL > 4.7 OR depth_gain negative (P=0.30). Sums to 1.00. Distinguishing-regime gate spelled out (TRIGRAM_HRR alone PASS / TRIGRAM+BACKOFF PASS / both FAIL).
- **Smoke gate:** sigma=0 sanity (bigram baseline reproduces 4.96 BPC exactly); HRR bind/unbind round-trip recall = 1.000 on V_C=1024; zero LLM calls AUDIT logged
- **DEPENDENCY:** runs on local_cpu_queue (laptop-feasible). NO dependency on Gap-3 / Gap-4 dispatches in flight; can fire today.

### Anchor 2: n6_optimal_V_C_sweep_v1

- **Anchor pointer:** `experiments/exp_n6_optimal_V_C_sweep_v1.py` (new cell; bigram-anchor; tests Skunkworks tradeoff at scale)
- **Substrate-product reading:** "substrate-native bigram-CONCEPT LM with V_C sweep in {256, 1024, 4096, 8192} at N=16384 to find the OPTIMAL V_C minimizing sub_bpc = ceiling + transition-noise; cleanest test of Skunkworks's PoC tradeoff on REAL text8"
- **Tier hint:** chain-grade candidate IF optimal V_C lowers sub_bpc below 4.5 (closes >= 0.46 of gap) at SOME V_C; MIDDLE_BAND if shows clear tradeoff curve but no V_C breaks below 4.5; HARD_FAIL if no monotone improvement at any V_C
- **Why now:** Skunkworks PoC 2026-06-21 PREDICTED an optimal-C exists; substrate has tested up to V_C=1024 only; V_C=4096 is mentioned in MEMORY as the L2 vision Path A target -- never measured. This cell answers "what is the optimal phase point" directly.
- **Composition:** identical pipeline to n2_capacity_scaling_v1 but with V_C sweep instead of N sweep; reuses substrate `concept_codebook` + count-proportional decode
- **Arms (4 mandatory):** V_C=256, V_C=1024, V_C=4096, V_C=8192 (single bigram context-depth; tests V_C lever in isolation)
- **Cost estimate:** ~10 min smoke / ~12-18 hr local_cpu full (3 seeds; V_C=8192 will be the slowest arm)
- **Pre-reg bands:** HARD_PASS = any V_C produces sub_bpc <= 4.5 (P=0.30); MIDDLE_BAND = tradeoff curve clearly visible, no V_C breaks 4.5, optimal V_C identified (P=0.45); HARD_FAIL = no monotone improvement OR ceiling rises faster than transition-noise falls at every V_C (P=0.25)
- **Smoke gate:** sigma=0 sanity at V_C=256 reproduces n1v3 5.00 BPC; codebook utilization >= 0.80 at every V_C tested (avoid dead concepts that confound)
- **Order:** dispatch in parallel with Anchor 1 (independent levers; both can run on local_cpu_queue); OR dispatch after Anchor 1 verdict to inform V_C choice in Anchor 1's TRIGRAM cell

### Anchor 3: n7_topK_cleanup_lm_v1

- **Anchor pointer:** `experiments/exp_n7_topK_cleanup_lm_v1.py` (new cell; bigram-anchor; tests top-K cleanup readout)
- **Substrate-product reading:** "substrate-native bigram-CONCEPT LM with top-K cleanup at readout (K in {1, 3, 5, 10}); reads K best concepts and weights their predictions by similarity; tests whether top-K cleanup smooths over noisy single-concept decisions at the cost of information dilution"
- **Tier hint:** chain-grade candidate IF top-K=3 or K=5 lowers sub_bpc by >= 0.1 bits vs K=1 anchor; MIDDLE_BAND if any K lowers by 0.05-0.1; HARD_FAIL if no K beats K=1 anchor (consistent with n4 k-WTA-VQ HARD_FAIL but tests READOUT-side variant which is different from ENCODER-side variant)
- **Why now:** small expected lever (0.1-0.2 bits per research note Section 6); secondary to context-depth + V_C levers; complements Anchors 1+2
- **Composition:** identical pipeline to n1v3 with top-K cleanup replacing top-1 argmax at the concept-readout layer
- **Arms (4 mandatory):** K=1 (anchor; n1v3-equivalent), K=3, K=5, K=10
- **Cost estimate:** ~5 min smoke / ~4-6 hr local_cpu full
- **Pre-reg bands:** HARD_PASS = top-K lowers sub_bpc by >= 0.1 bits at some K (P=0.20); MIDDLE_BAND = top-K lowers by 0.05-0.1 (P=0.30); HARD_FAIL = no K beats K=1 (P=0.50)
- **Order:** dispatch AFTER Anchor 1 verdict; only ship if Anchors 1+2 don't already close the gap (top-K is the marginal lever, not load-bearing)

### Anchor 4 (Tier-C; defer): n8_5gram_concept_lm_v1

- **Anchor pointer:** `experiments/exp_n8_5gram_concept_lm_v1.py` (defer; only if n5 HARD_PASSES with depth_gain positive)
- **Substrate-product reading:** "extend HRR sequence-bind to 4-prior context (5-gram concept transitions); tests whether further context-depth continues monotone improvement"
- **Tier hint:** Phase-2; defer until n5 lands
- **Cost estimate:** ~3 days build + 6-8 hr CPU
- **Order:** dispatch ONLY after n5 verdict CHAIN_GRADE or MIDDLE positive

### Anchor 5 (Tier-D; defer): n9_partition_routed_lm_v1

- **Anchor pointer:** `experiments/exp_n9_partition_routed_lm_v1.py` (Phase-2 scale lever; defer)
- **Substrate-product reading:** "partition routing on (c_{t-2}, c_{t-1}) -> partition -> predict c_t; amortizes lookup cost as V_C scales up; reaches M=10**5+ unique context-keys"
- **Tier hint:** Phase-2 scale lever; not closure path for bigram-gap
- **Order:** defer until n5/n6 land + cap_map updates the substrate-LM closure path

## Context pointers (file paths, not summaries)

- **Drill 1 research note (this hand-off's parent):** `notes/research_language_ingest_drill1_vocab_scale_glass_box_LM_math_2026-06-26.md`
- **N1 v3.1 DEFINITIVE substrate-LM result (the 4.96 BPC anchor + 1.13-bit-gap source):** `notes/orchestrator_to_skunkworks_N1_DEFINITIVE_substrate_LM_beats_unigram_not_bigram_2026-06-21.md`
- **Skunkworks N2 PoC (optimal-C tradeoff + closure direction):** `notes/skunkworks_to_research_expdev_concept_lm_PoC_for_N2_optimal_C_floor_beats_bigram_2026-06-21.md`
- **N2 capacity-scaling metrics (substrate-mine numbers):** `data/exp_n2_capacity_scaling_v1/metrics.json` (sub_bpc 5.29 -> 5.13 -> 4.96 across N=4096/8192/16384)
- **N3 MKN smoothing metrics (+0.068 bits lever):** `data/exp_n3_mkn_smoothing_v1/metrics.json`
- **N3 SimVQ metrics (no win):** `data/exp_n3_vq_alignment_simvq_v1/metrics.json`
- **N4 k-WTA HARD_FAIL (refutes k-WTA-VQ lever):** `data/exp_n4_kwta_soft_decode_v1/metrics.json`
- **N10 whitening HARD_FAIL:** `data/n10_remote_metrics_pulled.json`
- **N1 v3.1 anchor cell (for n5 extension):** `experiments/exp_n1_concept_lm_substrate_native_token_decode_v3_1.py`
- **N3 text8 pre-reg + cell (template for n5 ingest discipline):** `notes/exp_dev_n3_text8_pre_reg_2026-06-22.md` + `preregs/2026-06-22_n3_text8_ingest_cert_v1.md` + `experiments/exp_n3_text8_ingest_cert_v1.py`
- **Substrate primitives required:**
  - `hdlab/char_trigram_encoder.py` (hash-based deterministic token signature; recommended pattern per Section 4)
  - `hdlab/sequence_memory.py` (c3 sequence binding chain-grade 586)
  - `hdlab/generation.py` (g1b autoregressive primitive chain-grade 587)
  - `hdlab/iterative_attractor.py` (cleanup memory; readout layer)
  - `hdlab/binding.py` (HRR bind for trigram context composition)
  - `hdlab/bundling.py` (concept superposition for top-K cleanup)
- **Corpus cache:** `data/text8_cache/text8.txt` (100MB local; cached real text8)
- **Composes with (sibling drills):**
  - Gap-3 modern-Hopfield (dispatched 2026-06-26; could buy 0.1-0.3 bits via cleaner cleanup attractor): `notes/exp_dev_handoff_research_gap3_compositional_deeper_mechanism_drill_2026-06-26.md`
  - Gap-4 CLS replay (NREM consolidation; reduces transition-noise via replay-driven smoothing): `notes/research_gap4_continual_5x_drill_2026-06-26.md`
- **Bias master checklist:** `memory/feedback_experiment_bias_master_checklist_USER_2026-06-24.md`
  - Principle O (basis-vs-readout) APPLIES: hash-based basis, label-aware readout
  - Principle M (production-scale calibration) APPLIES: 100k-doc baseline match n1v3
  - Principle S (band-calibration regime checks) APPLIES: distinguishing-regime gate spelled out

## Contract

- Per [[feedback-no-experiment-design-in-prompts]]: this hand-off lists ANCHORS and POINTERS only. exp_dev authors the cells per substrate-physics + research note L3/L5/L7 composition guidance. Pre-reg bands in research note's "Cheap decisive test" + Section 7 + "Falsifiable predictions" are load-bearing -- bake into prereg verbatim.
- All cells must include META_M7 reproduce-once rail per autonomy rule.
- Substrate-only-decode gate preserved at every stage (n_llm == 0 asserted at decode; structural + counter; AUDIT logged).
- Per-seed runtime + cv <= 0.05 required for chain-grade.
- CORPUS_PROVENANCE_REAL=True asserted + LOGGED (fail-loud per phase_d_tier6 lesson; reuse n3 text8 ingest pattern).
- For Anchor 2 V_C=8192 arm: may be slow on local_cpu; consider routing via hdi_orchestrator to remote_cpu per Fix #22 if wall-time exceeds 24hr estimate.
- Smoke gate per anchor BEFORE full dispatch. Smoke timeout 600s; full timeout per cost estimate above.
- Pre-flight verify-the-referent gate per Fix #26 (run `tools/predispatch_check.py <anchor>` before dispatch; catches duplicate or recent-HARD_FAIL re-dispatches).
- Cell-author smoke + Fix #17 measurement + dispatch routing all per autonomous-arc Fixes #14-#24.

## Autonomy declaration

exp_dev has full autonomy over:
- Cell authoring within the research-note guidance and pre-reg bands
- Encoder choice within {char_trigram_encoder, V_C-concept-codebook} (research note specifies V_C=1024 for n5 anchor parity with n1v3)
- N_DIM choice within {8192, 16384} per substrate-physics SNR target for trigram HRR-bind (research note recommends N=16384 for n5; cap at 8192 if compute-bound)
- Seed choice within standard {7, 17, 23}
- Smoke / full split per queue-add gate
- Reprioritization between Anchors 1/2/3 if earlier results inform later cells
- Decision to route Anchor 2 V_C=8192 arm to remote_cpu if local wall-time concern
- Decision to dispatch Anchor 3 in parallel with Anchor 1 or defer

exp_dev does NOT have autonomy over:
- Re-defining HARD_PASS / MIDDLE / HARD_FAIL bands (research-note pre-reg is load-bearing)
- Skipping the bigram-baseline ARM in n5 (BIGRAM_BASELINE is the anchor for n2 reproduction verification)
- Removing the depth_gain HARD_FAIL clause (sign discriminator is load-bearing)
- Substituting non-substrate-native primitives (no MiniLM/BGE/Pythia at decode without explicit USER authorization)
- Bumping cell to chain-grade pre-Skunkworks review (per Fix #28; default classification = MIDDLE; let cert-owner promote)

---

-- Research (Opus 4.7-1M)
