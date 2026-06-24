# Skunkworks Experiment Bias Audit -- 2026-06-24

Trigger: USER directive 2026-06-24. Triggering finding: n1_v3 chain-grade (top1=0.4455
"+61.6% over unigram") was measured on PYTHIA-160m RESIDUALS at TOKEN-grain
(V_TOK=50087, N_DIM=4096, MAX_DOCS=100000 token-level), while the cf-RPE family and
the rest of the substrate-as-LM portfolio measure on TEXT8 + WORD2VEC at WORD-grain
(VOCAB_CAP=4000, N_DIM=8192, N_TRAIN=100k tokens). The reported "+12% cap" for cf-RPE
is corpus-and-encoder-specific, not substrate-general. Two different worlds were
being compared as if substrate-general.

Audit scope: ~22 cells (recent landed + in-flight). Bias dimensions per the
USER spec: corpus, encoder, metric, baseline, sanity rails, scale, provenance,
corpus-metric interaction. Skunkworks default: assume bias present unless cell
explicitly addresses it.

## Reference scaffold (so the audits below can be read at a glance)

- fair_harness landed (chain-grade RAIL): text8 + word2vec-google-news-300 ->
  Gaussian-project N_DIM=8192 -> sparse-bipolar f=0.05; VOCAB_CAP=4000;
  N_TRAIN=100k; rank-1 Hebbian W; joint (T,lambda) sweep.
  ARM_SUBSTRATE_SPARSE_BIPOLAR: bpc=7.306 | top1=0.2134 | mrr=0.2917.
- n1_v3 cert anchor (separate world): Pythia-160m residuals at token-grain,
  V_TOK=50087, N_DIM=4096, f=0.006 (k=25-of-N Willshaw), V_C=256, MAX_DOCS=100k.
  top1=0.4455, but unigram on THAT corpus is top1=0.2761. "+61.6% lift" is
  Pythia-residual-token-decode vs Pythia-residual-token-unigram. Substrate
  ingests Pythia-160m embeddings at ingest -- the substrate's READOUT does most
  of the work, but the input distribution it operates on is a 160M-param LM's
  residual stream.

Anything that quotes both numbers in a single sentence is apples-to-oranges.

## Per-cell entries

### Recent (landed)

CELL: substrate_cfrpe_n_steps_curve_extension_v2
  corpus: text8/word2vec | encoder: word2vec_sparse_bipolar_f0.05 | metric: BPC primary, top1 secondary | baseline: unigram + Hebbian rail
  sanity_rails: PASS (ARM_HEBBIAN bpc=7.3372 within +/-0.05 of 7.3065 rail) | provenance: traceable to fair_harness v1 + cfrpe_n_steps_curve_v1 | bias_concerns: BPC-primary verdict (Fix #28 risk); reports top1 only in detail; no comparison to bigram baseline; lift is over Hebbian-baseline ONLY (intra-encoder lift).
  framing_at_risk: PARTIAL -- this cell is honestly intra-family but if cited cross-cell as "cf-RPE caps at +12% top1" the encoder/corpus context must travel with the number.

CELL: substrate_K2_x_cfrpe_compose_word2vec_v2
  corpus: text8/word2vec | encoder: word2vec_sparse_bipolar_f0.05 | metric: BPC primary | baseline: unigram + ARM_BASELINE_RANK1_K1 rail
  sanity_rails: PASS (rail drift=0.000) | provenance: traceable | bias_concerns: clean rescue of v1 char-trigram methodology-confound -- explicitly converts encoder to match fair_harness chain-grade. THIS is the model for what a non-biased compose cell looks like.
  framing_at_risk: NO -- HARD_FAIL stands on its own evidence; the verdict_msg names the exact comparison ("ARM_K2_CFRPE vs ARM_CFRPE_K1") and does not extrapolate.

CELL: substrate_n1v3_readout_x_cfrpe_plasticity_compose_v1
  corpus: text8/word2vec (NOT Pythia-residuals!) | encoder: word2vec_sparse_bipolar_f0.05 + concept-sparse-Willshaw at f=0.05 (k=409) | metric: top1 primary per META C7 | baseline: unigram + provenance rails on n1_v3 (top1=0.4455) and cf-RPE (top1=0.2438)
  sanity_rails: FAIL -- ARM_N1_V3_READOUT_HEBBIAN_PLASTICITY top1=0.2189 off n1_v3 ref 0.4455 by 0.2266 | provenance: BROKEN -- "n1_v3 readout" cannot reproduce n1_v3 because (a) wrong corpus (text8 not Pythia-residuals), (b) wrong f (0.05 not 0.006), (c) wrong V (4000 vocab not 50087 tokens), (d) no Pythia at ingest. Verdict was correctly PROVENANCE_FAIL.
  framing_at_risk: HIGH if the PROVENANCE_FAIL is interpreted as "n1_v3 readout doesn't help". The truth is "the cell never actually ran an n1_v3 readout -- it ran a homonymous module on a different corpus". v2 BUGFIX also PROVENANCE_FAIL; same root cause survived bug-hunt. RECOMMENDED ACTION: n1v3 transfer requires either (i) port substrate-as-LM family TO Pythia-residual ingest or (ii) build new compose cell where the n1_v3 atom is RE-LANDED on text8 with word2vec ingest BEFORE composing. Until then ALL "n1_v3 x cf-RPE" claims are corpus-mismatched.

CELL: substrate_n1v3_readout_x_cfrpe_plasticity_compose_v2_BUGFIX
  corpus: text8/word2vec | encoder: word2vec_sparse_bipolar_f0.05 + concept-sparse f=0.003 (k=25) | metric: top1 primary | baseline: unigram + provenance rails
  sanity_rails: FAIL -- still PROVENANCE_FAIL (top1=0.2128) | provenance: BROKEN -- same corpus mismatch as v1, the f-fix alone cannot rescue the cross-corpus port.
  framing_at_risk: HIGH -- documents itself as "v2 BUGFIX did not restore provenance" which is honest but if the lesson is filed as "n1_v3 readout doesn't compose" rather than "cross-corpus port itself is the failure mode", future cells will repeat the trap.

CELL: substrate_compose_fair_harness_cfrpe_hetplasticity_K2_modern_hopfield_cleanup_v1 (A1)
  corpus: text8/word2vec | encoder: word2vec_sparse_bipolar_f0.05 N_DIM=8192 | metric: BPC primary | baseline: unigram + per-primitive sanity rails
  sanity_rails: PASS for all 4 included rails | provenance: traceable to fair_harness + het-plasticity chain-grade rows | bias_concerns: BPC-primary (Fix #28 risk on a 5-arm compose cell), but cell explicitly admits HARD_FAIL_SUB_ADDITIVE so no over-claim.
  framing_at_risk: NO. Clean cell. Sub-additive verdict is corpus-and-encoder-consistent within the fair_harness family.

CELL: substrate_dynamic_f_phase_shift_sparsity_v1
  corpus: text8/word2vec | encoder: word2vec sparse-bipolar with f varied per arm (0.02/0.05/0.50) | metric: BPC primary, top1+mrr secondary | baseline: unigram + ARM_STATIC_F_0p05 rail
  sanity_rails: PASS (drift=0.000) | provenance: traceable | bias_concerns: f is the variable under test, so the encoder is intentionally varied -- this is not bias, it is the cell's question. BPC-primary verdict but per-arm top1+mrr reported.
  framing_at_risk: NO. The +0.04 lift is honest and the verdict is HARD_FAIL precisely because pre-reg required +0.05.

CELL: substrate_pc_hierarchy_fair_harness_v1
  corpus: text8/word2vec | encoder: word2vec_sparse_bipolar_f0.05 N_DIM=8192 | metric: top1+BPC+MRR triplet | baseline: unigram + ARM_RANK_1_BASELINE rail
  sanity_rails: PASS | provenance: traceable | bias_concerns: HARD_PASS verdict on ARM_PC_HIERARCHY_2LEVEL_PLUS_CFRPE d_top1=+0.005 d_bpc=+0.085. The d_top1 is below CV; the "lift bar" is 0.05 OR-gated between top1 and bpc -- this OR-gating is a weak discriminator (one-of-three metric clears = HARD_PASS). Bigram baseline is absent. cf-RPE is in the compounded arm so the "PC contribution" cannot be isolated cleanly.
  framing_at_risk: MEDIUM. The cell's HARD_PASS verdict should be tiered to MIDDLE_BAND or MEASURED_MECHANISM until a 4-arm split isolates PC contribution from cf-RPE contribution. Top1 lift is +0.005 (essentially noise vs cv); the BPC lift is real but small and BPC is the rigged metric. Recommended: re-tier via Skunkworks sub-audit before propagating "PC hierarchy adds LM lift" framing.

CELL: substrate_brain_word_level_prediction_v1 (HARD_FAIL)
  corpus: text8 word-level | encoder: char-trigram-meanpool-bipolar N_DIM=2048 | metric: top1+BPW dual | baseline: word-unigram + word-bigram (THE strong baseline)
  sanity_rails: NONE explicit, but B1 word-unigram and B2 word-bigram are themselves baselines | provenance: parent fair_harness pattern but DIFFERENT encoder and N_DIM=2048 (smaller) | bias_concerns: char-trigram-meanpool encoder is known weak (META_HARNESS_RIGGED row); N_DIM=2048 is 4x smaller than chain-grade rail (8192). The HARD_FAIL is NOT informative about brain-word-grain question because the configuration is itself degraded.
  framing_at_risk: HIGH (in the LOSING direction). The cell mistakes a config-confound for a substrate-failure. Author honestly notes this and routes to v2.

CELL: substrate_brain_word_level_prediction_v2_production_config (IN-FLIGHT)
  corpus: text8 word-level | encoder: word2vec sparse-bipolar f=0.05 N_DIM=8192 | metric: top1+BPW | baseline: word-unigram + word-bigram
  sanity_rails: implicit | provenance: parent v1 + fair_harness | bias_concerns: GOOD CELL DESIGN. Uses production config matching fair_harness rail. Bigram baseline is the right strong baseline.
  framing_at_risk: LOW. This is the right re-test of v1. Watch: when it lands, the verdict must be propagated WITH the word-grain framing (it is a word-grain test, not char-grain).

CELL: substrate_arm2_capacity_respecting_pair_storage_v1
  corpus: synthetic (sparse-bipolar codebook) | encoder: sparse-bipolar f=0.05 N_DIM=8192 | metric: in_dist_top1 | baseline: M=20 capacity-respecting
  sanity_rails: PASS by-construction | provenance: clear | bias_concerns: NONE -- the DIAGNOSTIC_PASS by-construction tiering is exactly right; cv=0 + crosstalk far below discrimination floor.
  framing_at_risk: NO. Cell explicitly self-tiered to DIAGNOSTIC_PASS (not chain-grade).

CELL: substrate_compositional_K10_K20_reconfirm_n8192_v1
  corpus: synthetic (bipolar chains) | encoder: bipolar codebook N=8192 | metric: K-hop accuracy | baseline: pre-reg threshold (>=0.70 at K=15)
  sanity_rails: implicit via prior n4096 reproduction | provenance: traceable to compositional_K10_to_K20_v1_n4096 | bias_concerns: K10=K15=K20=1.0 across 3 seeds = by-construction-saturation candidate. Load is intentionally low (0.3 * alpha_c). The HARD_PASS as "substrate composes K=20" is true but the BAR is also low.
  framing_at_risk: MEDIUM. Cell is honest about "low load". But framings like "substrate compositional generalization chain-grade at scale" should be qualified with the load fraction. Recommended: when atomized, atomize as PROVEN-BOUND/by-construction tier; not a strong LM-relevant generalization claim.

CELL: substrate_brain_aligned_aliveness_shotgun_v1
  corpus: synthetic (sparse-bipolar codebook + HRR bind) | encoder: sparse-bipolar f=0.05 N=8192 | metric: per-arm specific (recovery, top1, capacity_k, top1) | baseline: pre-reg bands per arm
  sanity_rails: ARM 1 MUST PASS or whole cell HARD_FAIL; ARM 1 PASSED | provenance: traceable | bias_concerns: ARM 2 in_dist_top1 was 0.10 at chance = mechanism-broken not capability-broken (correctly tiered as the trigger for the CORRECTED_v1 follow-up). The cell is internally honest.
  framing_at_risk: LOW. The "3 of 4 HARD_PASS" framing is the verdict and ARM 2 was correctly flagged. Recommended: BRAIN_ALIGNED_PARTIAL atoms should not be cited as "substrate is alive on brain-canonical tests" without naming which dimensions; downstream readers easily lose that nuance.

CELL: substrate_continual_learning_spectrum_v1
  corpus: SYNTHETIC bipolar per-domain permutations (NOT real corpus) | encoder: bipolar N_DIM=4096 | metric: forgetting + transfer + capacity | baseline: ARM_BASELINE_STATIC + ARM_DISCRETE_ADD
  sanity_rails: ARM_BASELINE_STATIC retention rail | provenance: cf-RPE + CLS-replay primitive rows | bias_concerns: corpus is synthetic per-domain permutations of bipolar atoms -- the cell EXPLICITLY says "NOT cross-CORPUS continual learning". Compute_per_update is numpy-only and NOT apples-to-apples vs transformer. Cell is honest about both limits.
  framing_at_risk: HIGH (if cited as "substrate continual learning moat is real"). The honest framing is "substrate CL primitives compose on synthetic per-domain permutations". A transformer-comparison-grade CL claim requires real-corpus + GPU-flops + a transformer baseline.

CELL: substrate_cfrpe_per_token_adaptive_lr_v1 (MIDDLE_BAND)
  corpus: text8/word2vec | encoder: word2vec_sparse_bipolar_f0.05 N_DIM=8192 | metric: BPC primary | baseline: ARM_HEBBIAN_BASELINE rail
  sanity_rails: PASS | provenance: traceable | bias_concerns: BPC-primary. Best adaptive arm bpc=6.992 lift=0.345 over Hebbian. The cf-RPE+adaptive ladder is intra-family at fair_harness encoder, but the absolute bar (HARD_PASS lift>=0.40) is anchored to Hebbian only, NOT to bigram/real-LM.
  framing_at_risk: MEDIUM. Lift is real and intra-family-honest, but "substrate-as-LM single-arm record" should be qualified to "best-vs-Hebbian-rank1 at fair_harness encoder"; word-bigram has not been beaten in this family.

CELL: substrate_mh_beta_sweep_extended_T_grid_v1 (HARD_FAIL)
  corpus: text8/word2vec | encoder: word2vec_sparse_bipolar_f0.05 N_DIM=8192 | metric: BPC primary | baseline: ARM_BASELINE_NO_CLEANUP rail
  sanity_rails: PASS (NO_CLEANUP rail drift=+0.0032) | provenance: traceable | bias_concerns: structural diagnosis (not bias) -- the +0.7 BPC degradation with MH cleanup is real and verdict is correct.
  framing_at_risk: NO. Cell self-honest.

### In-flight

CELL: substrate_adaptive_cfrpe_x_k2_compose_v1 (HARD_FAIL just landed)
  corpus: text8/word2vec | encoder: word2vec_sparse_bipolar_f0.05 N_DIM=8192 | metric: BPC primary | baseline: ARM_BASELINE_RANK1_K1
  sanity_rails: PASS | provenance: traceable | bias_concerns: BPC-primary; ADAPT_K1 rail at 7.0090 (drift 0.017 from prior 6.992 reference -- acceptable). HARD_FAIL on K=2 compose is the third compose-saturation hit in a row.
  framing_at_risk: LOW. Verdict honest.

CELL: substrate_sequence_modeling_production_v1 (in-flight, local CPU)
  corpus: text8 word-level | encoder: word2vec sparse-bipolar f=0.05 | metric: BPC + top1 + MRR triplet | baseline: word-unigram + WORD-BIGRAM (the right strong baseline)
  sanity_rails: ARM_CONTEXT_FREE_SUBSTRATE within +/-0.10 of 7.31 ref | provenance: cites fair_harness + c3 + g1b | bias_concerns: GOOD CELL DESIGN. Explicit "honest re-cast" paragraph acknowledges char-bigram framing-error and pivots to word-bigram. Best methodology in the in-flight set.
  framing_at_risk: LOW. Watch when it lands: do not propagate the verdict cross-grain (this is a word-grain test).

CELL: substrate_cross_layer_compose_LM_v1 (in-flight, local CPU)
  corpus: text8/word2vec | encoder: word2vec_sparse_bipolar_f0.05 N_DIM=8192 | metric: BPC primary | baseline: cf-RPE rail
  sanity_rails: cf-RPE rail + raw_bpc_at_T1_L1 READOUT_DEGENERATE gate | provenance: traceable + cites q_a3_l100 cross-layer composition chain-grade | bias_concerns: BPC-primary, but READOUT_DEGENERATE gate is a strong sanity-rail addition. Cross-layer pattern transfer from q_a3 is a structural-discriminator design.
  framing_at_risk: LOW.

CELL: substrate_top1_targeted_plasticity_4arm_smoke_v1 (in-flight, local CPU)
  corpus: text8/word2vec | encoder: word2vec sparse-bipolar f=0.05 N_DIM=2048 (smoke) | metric: top1 PRIMARY (explicit, Fix #28) | baseline: ARM_CFRPE_REFERENCE
  sanity_rails: cf-RPE sanity rail | provenance: cf-RPE per-token adaptive heritage | bias_concerns: SMOKE CONFIG (N_DIM=2048 vs production 8192). Verdict bands only apply at smoke. Smoke result must NOT be propagated as substrate-general.
  framing_at_risk: LOW IF smoke-tier discipline preserved; HIGH if smoke result is cited as evidence of plasticity-as-top1-lever closure.

CELL: substrate_pcgrad_cfrpe_stdp_v1 (in-flight, remote CPU)
  corpus: text8/word2vec | encoder: word2vec_sparse_bipolar_f0.05 N_DIM=8192 | metric: BPC primary | baseline: ARM_CFRPE_ONLY rail + ARM_NAIVE_STDP rail
  sanity_rails: cf-RPE + hetplast rails | provenance: traceable to A1 reference | bias_concerns: BPC-primary, but gradient-cosine instrumentation gives a discriminator independent of BPC. Strong design.
  framing_at_risk: LOW.

CELL: substrate_compositional_generalization_CORRECTED_v1 (in-flight; was halted then re-dispatched)
  corpus: synthetic codebook | encoder: variants (sparse-no-norm / dense-norm / FHRR / sparse-norm) per arm | metric: in_dist_top1 + holdout_top1 | baseline: ARM_BROKEN_SPARSE_NO_NORM (provenance for shotgun ARM 2)
  sanity_rails: explicit -- in_dist > 0.70 GATE before holdout counts | provenance: traceable to shotgun ARM 2 failure | bias_concerns: NONE. The sanity floor gate is exactly the discipline the shotgun ARM 2 was missing.
  framing_at_risk: LOW.

### Not-yet-authored (mentioned but no cell file)

substrate_compose_heterogeneous_routing_v1 and substrate_n1v3_corpus_transfer_discriminator_v1 -- not present as cell files in experiments/. The latter is the explicit fix recommended below; treat as pending.

## Cross-cutting synthesis

Systematic biases observed (in priority order):

1. CORPUS-METRIC LANE-CROSSING is the dominant bias. The substrate-as-LM portfolio has at least three distinct corpus+encoder worlds being treated as if they were one substrate-general regime:
   - WORLD A: text8 + word2vec-google-news-300 -> sparse-bipolar f=0.05 -> N_DIM=8192 -> VOCAB_CAP=4000. (fair_harness rail; cf-RPE family; K2/PC/MH compose family; all in-flight LM cells.) The bpc=7.306 / top1=0.213 reference. Sanity rails are well-defined here.
   - WORLD B: Pythia-160m residuals -> sparse-Willshaw f=0.006 (k=25) -> N_DIM=4096 -> V_TOK=50087. (n1_v3 anchor.) top1=0.4455 is meaningful here but it is a Pythia-residual-token-decode test; the "+61.6%" is over Pythia-residual-token-unigram (0.2761), not over WORLD A's unigram (0.2171).
   - WORLD C: synthetic codebooks (HRR / bipolar chains / per-domain permutations). (brain_aligned_aliveness, compositional_K10_K20, continual_learning_spectrum, arm2_capacity_respecting.) Metrics here measure capacity / pattern-completion / by-construction primitives; CANNOT be expressed in BPC terms or compared to fair_harness numbers.
   The bias is treating numbers from World B and World C as comparable to World A. Two cells (n1v3_x_cfrpe v1 + v2_BUGFIX) actively tried to PORT the World B result into World A and both PROVENANCE_FAILed because the underlying corpus structure does not survive the port.

2. BPC-PRIMARY OVER-RELIANCE (Fix #28 recurring). 13 of 22 cells use BPC as primary verdict metric. Per META_HARNESS_RIGGED, BPC was the metric that produced the original 7+ false HARD_FAILs and remains the metric most sensitive to (T, lambda) calibration. The cells that paired BPC with top1+MRR triplet (fair_harness, pc_hierarchy_fair_harness, sequence_modeling_production, cross_layer_compose) are the model; the BPC-only ones (cfrpe family, K2 family, MH) are over-rotated. This is not always a defect (when the question IS "does BPC move") but the verdict should not generalize beyond BPC if the cell only measured BPC.

3. WEAK-BASELINE BIAS. The dominant baseline across the LM-relevant set is word-unigram + Hebbian-rank1 rail. Only TWO cells (substrate_brain_word_level_prediction_v1+v2; substrate_sequence_modeling_production_v1) test against word-bigram, which is the real strong baseline at this scale. The first of those HARD_FAILed at degraded config; v2 and sequence_modeling are in-flight. NONE of the chain-grade-eligible substrate-as-LM cells have beaten word-bigram. The "+12% cap" and "single-arm record 6.992" should be qualified as intra-family-vs-Hebbian-rail; NOT as substrate-vs-real-LM-baseline.

4. PROVENANCE PORT FAILURES. The n1v3 x cf-RPE compose family burned two cells trying to port a Pythia-residual-token-decode anchor onto the text8-word2vec harness without first re-landing the source atom on the target corpus. This bias is structural: any cross-anchor compose cell needs an explicit corpus-port verifier BEFORE the compose arm.

5. BY-CONSTRUCTION-SATURATION OVER-CLAIMING. compositional_K10_K20 (K=1.000 with cv=0 at load=0.3*alpha_c) and arm2_capacity_respecting (top1=1.000 with crosstalk 6e-6) are correctly tiered as DIAGNOSTIC_PASS / by-construction by Skunkworks. The Director-level recurrence (Fix #28 recurring) is still under control here -- cells were tiered down rather than up. Good.

Triage buckets:

  CLEAN (no bias concern): fair_harness_v1 (rail), K2_x_cfrpe_word2vec_v2, compose_fair_harness_A1, mh_beta_sweep, arm2_capacity_respecting, dynamic_f, compositional_generalization_CORRECTED, sequence_modeling_production, brain_word_level_v2, pcgrad_cfrpe_stdp, cross_layer_compose_LM.
  CRITICAL (findings may need re-interpretation): n1v3_x_cfrpe v1+v2_BUGFIX (PROVENANCE_FAIL is cross-corpus port failure, not mechanism failure); brain_word_level_v1 (config-confound); pc_hierarchy_fair_harness_v1 (HARD_PASS on +0.005 top1 + OR-gated metric -- recommend re-tier to MEASURED_MECHANISM pending sub-audit).
  MEDIUM (qualify framings): continual_learning_spectrum (synthetic-only; moat claim needs real-corpus + transformer baseline), compositional_K10_K20_n8192 (low load -- atomize as DIAGNOSTIC tier), cfrpe_per_token_adaptive (intra-family lift; do not propagate "single-arm record" without qualifier), brain_aligned_aliveness_shotgun (PARTIAL -- name which dimensions passed in cites).

## Recommended actions (priority-ordered)

A. STOP claiming "n1_v3 +61.6% top1" and "cf-RPE +12% top1 cap" in the same paragraph as comparable substrate-general numbers. The two numbers live in different corpus+encoder worlds and the difference is the world, not the substrate-mechanism. Until cross-corpus port lands chain-grade, treat them as two separate cert atoms with explicit corpus tags in citation.

B. AUTHOR substrate_n1v3_corpus_transfer_discriminator_v1 (already in director plan, just not yet a cell file). This cell should re-land n1_v3 (or its Pythia-residual-free analog) on text8 + word2vec ingest BEFORE any compose cell quotes the +61.6% number against fair_harness rail. The two v1 + v2_BUGFIX corpses are the cost of skipping this step.

C. RE-TIER pc_hierarchy_fair_harness_v1 to MIDDLE_BAND or MEASURED_MECHANISM pending sub-audit. The +0.005 top1 lift is noise-grade and the OR-gated metric clear is a weak discriminator.

D. ADD a word-bigram baseline to every BPC-primary cell at the fair_harness encoder going forward. The current chain-grade reference rails are all rank-1-Hebbian or cf-RPE; word-bigram is the real-LM-strong-baseline that has not yet been beaten in WORLD A.

E. CONTINUE the in-flight design pattern (sequence_modeling_production_v1, brain_word_level_v2, pcgrad). These cells have stronger bias controls than the median recent cell and should be the template for future LM-relevant compose cells.

F. CORPUS PROVENANCE on cert atoms. Every chain-grade atom should carry a corpus+encoder+N_DIM+VOCAB tag in its provenance so downstream readers cannot accidentally cross-pollinate WORLD A / WORLD B / WORLD C numbers. This is the cert_ledger.jsonl convention I flagged in the validation spawn -- the audit re-confirms its urgency.

End of audit.
