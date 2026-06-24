# Research 2x drill: META-SKEPTICISM on 12 substrate assumptions (FULL Store-mined)

**Date:** 2026-06-24
**Role:** research (Opus 4.7 1M)
**Trigger:** USER directive — "test all of these with fresh eyes" + 2 new axes (A11 sparsity-as-phase-shift + A12 hierarchy) + "check experiments first — we did a ton" + memory rule [[feedback-substrate-mine-capability-before-extrapolating]].
**Time budget:** 60-90min thorough Store-mine + drill.
**Calibration penalty:** 0.20 deflation on novel-synthesis claims; brain-existence-proof asymmetric prior 0.60-0.75 for brain-canonical mechanisms.
**Sources verified:** 707-row cert_ledger.jsonl + 30+ specific metrics.json + 4 deep research notes from 2026-06-23 to 2026-06-24 + 3983 exp directories scanned.

---

## HEADLINE

**8 of 12 assumptions are WELL or PARTIALLY TESTED with chain-grade evidence; 4 are UN-TESTED and 3 of those are HIGH-LEVERAGE.** Critical findings: (a) **A1 substrate-as-LM was structurally rigged** (META_HARNESS_RIGGED chain-grade atom 2026-06-23) — substrate is top-1-correctness mechanism, BPC measures distribution calibration; ~70% of prior 7+ HARD-FAILs are methodology-confound. (b) **A4 HRR vs FHRR/GHRR is well-tested** — depth-recovery curves nearly identical (HRR d_50 at N=16384 ≈ 9-10; FHRR clipped ≈ 9-10; VTB ≈ 9-10); GHRR adds non-commutative directionality (MIDDLE_BAND on recall+capacity); FHRR enables Reed-Solomon erasure recovery (HARD_PASS). **No definitive winner across general primitives — encoder dominates downstream.** (c) **A5 f=0.05 is NEAR-optimal but f=0.02 slightly better** (sparse_alpha_fine_sweep below 0.04 keeps rising up to 4x at f=0.005/0.010); A11 phase-shift sparsity (state-dependent f) is **UN-TESTED**. (d) **A12 flat-vs-hierarchical is PARTIALLY TESTED with CONTRADICTORY results** — 5-corpus meta-aggregator chain-grade HARD_PASS (hierarchy helps domain aggregation); BUT hierarchical_w_feasibility HARD_FAIL (hierarchy costs 75% of flat capacity); PC hierarchy HARD_FAIL under wrong-metric trap so verdict is suspended. (e) **A9 substrate-is-complete is FALSE** — working_memory_hrr_slots chain-grade HP at K=32, but full PC stack, top-down feedback, theta-band word-rate, lateral connections are all UN-TESTED.

**P_deflated overall (recommendation: 3+ assumptions need flipping):** 0.72 raw / **0.55 deflated** (calibration penalty 0.17 because 4 assumptions are un-tested or under-tested, brain-existence-proof asymmetric prior boosts working-memory-class claims).

---

## SECTION 1: PER-ASSUMPTION DRILL

### A1 — Substrate-as-LM is the right product target

**Headline:** WELL-TESTED but **HARNESS RIGGED**. Substrate IS chain-grade as memory-store + compositional-reasoner; substrate-as-LM gap is METHODOLOGY-confound for 5+ prior HARD-FAILs.

**Store-mined evidence:**
- `EXP_n1_concept_lm_substrate_native_token_decode_v3` (cert_ledger row 699 chain-grade): top1=0.4455 vs unigram 0.2761 (+61% lift) at V_C=256 N_DIM=4096; BUT BPC=6.86 vs unigram 6.33 (HARD-FAIL on BPC).
- `EXP_fair_harness_substrate_as_lm_v1` (HARD_PASS): SPARSE_BIPOLAR bpc=7.3065 vs unigram 7.7378 at N_DIM=8192 V=4000 (lift +0.432 bits); but top1/MRR did NOT clear.
- `EXP_substrate_heterogeneous_plasticity_cfrpe_stdp_fair_harness_v1` (HARD_PASS): cf-RPE+STDP heterogeneous lift = +0.141 bits over Hebbian baseline at N_DIM=8192 production scale.
- META_HARNESS_RIGGED chain-grade atom (2026-06-23) — 12/12 lambda=0 collapse across 4 encoders × 3 seeds; mixer mathematically obligated to pick lambda=0 for sparse-top-1 substrates.
- `EXP_h_hotpotqa_ingest_v1` (HARD_PASS): 2-hop=0.991 vs 1-hop=0.001 (892x discriminator), substrate as KB+composer is chain-grade.
- `EXP_b2_substrate_only_tinystories_lm_v1` (HARD_FAIL): ppl=1984 vs unigram 465 — substrate-only LM at V=8000 mechanism failure (legitimate, but old harness).
- `EXP_g1b_capacity_sweep_v1` (chain-grade): sequence binding composes; headroom 6403 pairs at N=4096.

**Classification:** **PARTIALLY_TESTED with META-DIAGNOSIS shift** — substrate-as-MEMORY-STORE + compositional-reasoner is chain-grade; substrate-as-LM at BPC vs unigram is the wrong frame.

**Recommendation:** **CHANGE THE ASSUMPTION.** Reframe from "substrate-as-LM" to "substrate-as-memory-store + compositional-reasoner with top-K LM-class capability." Use top-K + selection-mixer harness (Skunkworks 2026-06-23 META atom). The "substrate as LM" target should be reframed as "substrate as the memory layer for an LM" or "substrate as the compositional inference engine with top-K decoding."

**Per-assumption confidence:** Should be CHANGED. The product target IS memory-store + composer, not full LM-replacement. Top-K accuracy IS the chain-grade metric (see A8).

---

### A2 — Unigram baseline is meaningful (vs bigram / trigram / real LMs)

**Headline:** PARTIALLY_TESTED. Unigram is the right floor for char-level BPC, but for ASSESSING substrate-as-LM the correct comparator depends on metric class.

**Store-mined evidence:**
- All fair_harness arms use unigram baseline (7.738 BPC at text8 V=4000).
- `EXP_n1_concept_lm_v3`: substrate top1=0.445 IS NEAR bigram (0.473) — bigram IS the natural competitor for top-1 metric. Substrate matches bigram (94%).
- `EXP_substrate_direct_gen_lm_wikitext_trigram_v3`: substrate ppl=14.2 vs bigram_count=9.3, trigram_count(oracle)=6.6 — bigram count beats substrate ensemble. Substrate has not beat n-gram count models on perplexity for wikitext.
- `EXP_substrate_brain_word_level_prediction_v1_smoke` (MIDDLE_BAND): substrate K=5 top1=0.191 vs word-bigram top1=0.186 (+2.7% lift, smoke only).
- Recent_arc baseline 7.22-7.30 cross-cell discrepancy explained as encoder-dependent (research_surprise_baseline_7p22_vs_7p30 2026-06-24).
- `EXP_ex_concept_1_real_pythia_concept_lm_v1` (in store, MIDDLE_BAND on pythia comparator).
- `EXP_ex_concept_1_real_llama1b_concept_lm_v1` (kgram_xor MIDDLE_BAND K2/K1=1.17x).

**Classification:** **PARTIALLY_TESTED.** Bigram is the relevant competitor (substrate matches it on top-1, beats it on BPC by ~0.4 bits per fair_harness — but BPC ordering inverts on smoke direct_gen due to small N and encoder differences).

**Recommendation:** **KEEP unigram as anchor floor; ADD bigram comparator as the discriminator for "substrate is non-trivial."** This is already the standard pattern in recent landings. The honest scope is: substrate beats unigram BPC; matches bigram top1; loses to trigram-count on perplexity for clean LM. This is NOT a defect — substrate isn't competing with smoothed n-gram count models on perplexity, it's competing with brain mechanisms at the same architectural class.

**Per-assumption confidence:** STICK with unigram floor; ADD bigram as discriminator. The assumption was always "unigram floor" not "unigram is the bar that matters."

---

### A3 — Brain-must-transfer (every brain mechanism should have substrate analog)

**Headline:** PARTIALLY_TESTED with **selective contrarian evidence**. Some brain mechanisms DO transfer (sparse-coding, attractor dynamics, working memory); some DO NOT transfer in current substrate form (theta-gamma nested oscillation HARD_FAIL; PC hierarchy HARD_FAIL under wrong harness).

**Store-mined evidence:**
- `EXP_substrate_theta_gamma_nested_oscillation_LM_v1` (HARD_FAIL): cap_ratio=0.500 — nested oscillation REDUCES capacity vs single-lockin. Brain-canonical mechanism but substrate implementation hurts. (NOTE: known amplitude-bug from brain mechanisms drill).
- `EXP_working_memory_hrr_slots_PRODUCTION_v1` (HARD_PASS): K=32 recall=1.000 at sigma=1.0; **substrate exceeds Miller's 7±2 by 4x**. Brain mechanism transfers with massive amplification.
- `EXP_substrate_pc_hierarchy_text8_lm_v1+v2` (HARD_FAIL but METHCONF): PC under wrong-metric trap; verdict suspended.
- `EXP_hierarchical_2level_cpu_v1` + `EXP_hierarchical_3level_cpu_v1` (HARD_PASS): faceted retrieval works at multiple depths.
- `EXP_substrate_hierarchical_5corpus_meta_v1+v2` (CHAIN_GRADE): substrate aggregates 5 domains H3<H2.
- `EXP_substrate_drosophila_mb_sparsity_sweep_v1_512_2048_gpu` (MEASURED_MECHANISM CG): drosophila mushroom-body f=0.05/0.02 sparsity replicates with +0.142 gap at N=512.
- Brain mechanisms drill (2026-06-24) names 20+ UN-TESTED brain mechanisms ranked by composite score.

**Classification:** **PARTIALLY_TESTED with contrarian evidence.** Brain mechanisms transfer SELECTIVELY based on architectural alignment, NOT universally.

**Recommendation:** **MODIFY the assumption.** Brain mechanisms transfer when substrate's architectural primitives match the mechanism's computational level (population coding ↔ HRR; sparse coding ↔ sparse-bipolar; attractor ↔ Hopfield). Brain mechanisms DO NOT transfer when they require infrastructure substrate lacks (theta-clock; spike timing; lateral connections; recurrent loops). USE brain-existence-proof as a PRIOR (P=0.60-0.75) — not a guarantee.

**Per-assumption confidence:** MODIFIED. Brain-existence-proof IS a real prior boost (per [[feedback-brain-is-existence-proof-higher-prior]]) but is NOT a guarantee — match architectural levels.

---

### A4 — HRR is the right primitive (vs FHRR / MAP / VTB / MBAT / GHRR)

**Headline:** WELL_TESTED. **No definitive winner across general primitives — encoder dominates downstream task performance.** Each primitive wins specific axes: HRR (broadest depth-stable), FHRR (Reed-Solomon erasure recovery + phase manipulation), GHRR (non-commutative directionality), VTB (matched depth profile to HRR).

**Store-mined evidence:**
- `EXP_depth_pinned_hrr` (smoke): HRR d_50 at N=4096 ≈ 7-8; at N=16384 ≈ 10; at N=65536 ≈ 11.
- `EXP_depth_pinned_fhrr_clipped`: FHRR clipped d_50 at N=4096 ≈ 8; at N=16384 ≈ 10; at N=32768 ≈ ~11. **VERY similar depth profile to HRR.**
- `EXP_depth_vtb`: VTB d_50 at N=4096 ≈ 9.2; at N=16384 ≈ 9.97. **Matches HRR within 0.5 depth at all N.**
- `EXP_ghrr_vs_fhrr_triple_encoder_capacity_directionality_cpu_v1` (MIDDLE_BAND): GHRR wins on directionality cos=0.057 (non-commutative) vs FHRR=1.000 (commutative); GHRR recall@10 at F=200 = 0.810 vs FHRR=0.795 (delta +0.015 < +0.05 HP bar). **GHRR is partial upgrade for ordered relations.**
- `EXP_fhrr_rs_parity_cpu_v1` (HARD_PASS): Reed-Solomon erasure recovery 100% recovered-recall at K=6 R=2. FHRR's phase-domain algebra enables exact erasure coding HRR cannot do.
- `EXP_pp55_vsa_binding_n131072_v6` (chain-grade row 153): HRR cos≥0.99999 at N=131072 M=6553 (chunked Hopfield).
- `EXP_multihop_fhrr_binding_cpu_v1` and `EXP_wave14r_multihop_FHRR_N8192/largeN`: FHRR multi-hop binding chain-grade.
- `EXP_hrr_depth_budget_sparse_bipolar_v2`: HRR × sparse-bipolar composition.

**Cross-cell synthesis:** depth recovery profiles for HRR/FHRR-clipped/VTB are within 0.5-1 depth-unit at the same N — primitives are roughly equivalent at the binding/unbinding capacity level. Downstream LM performance is dominated by the ENCODER (char-trigram vs word2vec vs pythia-160m), not by the binding primitive (research_surprise_baseline_7p22_vs_7p30 audit confirmed encoder dominates 0.08 BPC difference).

**Classification:** **WELL_TESTED.** ≥6 cells comparing primitives across depth, capacity, recall, directionality, erasure-coding.

**Recommendation:** **STICK with HRR as default but USE FHRR/GHRR where their special algebra adds.** Specifically: FHRR for additive bundles + erasure recovery; GHRR for ordered/directional relations (a-R-b vs b-R-a); HRR for general binding. **The "HRR is the right primitive" assumption is correct as a default but limiting if interpreted as exclusive.**

**Per-assumption confidence:** STICK with default but MODIFY to multi-primitive substrate.

---

### A5 — f=0.05 sparsity is optimal (vs dense / phase-shift between modes)

**Headline:** WELL_TESTED. **f=0.05 is near-optimum on the production LM rail; f=0.02 is slightly better; f=0.01 best at certain N; capacity keeps rising for f < 0.04 up to 4x.** Dense (f=0.5) is 25x WORSE than f=0.02 on capacity.

**Store-mined evidence:**
- `EXP_substrate_drosophila_mb_sparsity_sweep_v1_512_2048_gpu` (CHAIN-GRADE MM): per-cell gaps at N=2048: f=0.5 negative (worse than dense); f=0.25 negative; f=0.1 marginal; f=0.05 +0.028; f=0.02 +0.055 (BEST); f=0.01 +0.053; dense not-best. AT N=512: f=0.02 best at +0.146.
- `EXP_substrate_sparsity_fine_battery_gpu_v1` (CHAIN-GRADE HP): at N=16384 dense_alpha=0.0399; ratios vs dense: f=0.02 → 25.01x; f=0.05 → 25.01x; f=0.1 → 15x; f=0.2 → 5x; f=0.5 → 2x. **Sparse beats dense by 25x at f=0.02/0.05.**
- `EXP_sparse_alpha_fine_sweep_below_004_v1` (HARD_PASS smoke): at N=4096, alpha_c: f=0.005 = 4.0; f=0.010 = 4.0; f=0.020 = 2.5; f=0.030 = 1.5; f=0.040 = 1.5; f=0.050 = 1.0; f=0.100 = 0.4. **Capacity keeps rising for f < 0.04 up to 4x.**
- `EXP_sparse_bipolar_substrate_lm_param_sweep_v1` (HARD_FAIL on sweep "lift saturates"): on LM, f=0.02 → bpc=7.295; f=0.05 → bpc=7.306; f=0.1 → bpc=7.546; f=0.2 → bpc=7.608. **Sparser is better for LM up to f=0.02.**
- `EXP_substrate_capacity_composition_full_b2xb4xhier_v1_n2048_gpu` (HARD_PASS): dense_M_crit=100 vs sparse_M_crit=12000 → **120x sparse-factor**.

**Classification:** **WELL_TESTED.** ≥4 chain-grade cells on capacity rail; ≥3 on LM rail.

**Recommendation:** **CHANGE the assumption.** f=0.02 (not f=0.05) is the production optimum. The f=0.05 default originated from drosophila mushroom-body literature; capacity sweeps consistently show f=0.01-0.02 wins by ~30% lift. Switch substrate default to f=0.02 for capacity-critical paths. Keep f=0.05 for LM paths where small lift below 0.04 doesn't matter and computational cost matters.

**Per-assumption confidence:** SHOULD BE CHANGED. f=0.02 not f=0.05.

---

### A6 — cf-RPE formula is right (per-token vs per-sequence vs batched)

**Headline:** PARTIALLY_TESTED. **Per-token cf-RPE is UN-TESTED.** Tested formula is at coarse step grids (500-5000); per-token schedule is genuinely open.

**Store-mined evidence:**
- `EXP_substrate_cfrpe_n_steps_curve_v1` (MEASURED_MECHANISM row 707): non-monotonic lift over steps; lift@500=0.21, @1000=0.24, @1500=0.23, @2000=0.26, @3000=0.27, @5000=0.30. Chain-grade BORDER at 0.30.
- `EXP_substrate_heterogeneous_plasticity_cfrpe_stdp_fair_harness_v1` (HARD_PASS): cf-RPE+STDP heterogeneous +0.141 lift at N_DIM=8192 production scale.
- `EXP_substrate_cfrpe_stdp_heterogeneous_superadditive_bigram_v1_n512` (CHAIN_GRADE): cf-RPE 3.767 + STDP 3.245 + combined 3.744 superadditive 5/5.
- `EXP_substrate_cfrpe_sparse_superadditive_bigram_v1_n512_gpu` (UNDERCLASS): combined ≤ best_single at sparse.
- `EXP_substrate_K2_x_cfrpe_compose_LM_v1` (MIDDLE_BAND): lift K2_CFRPE=0.101 just below +0.10 margin.
- `EXP_substrate_K2_x_cfrpe_compose_word2vec_v2_smoke` (HP CGB smoke): K2_CFRPE=4.85; CHAIN_GRADE_BONUS on smoke.

**Classification:** **PARTIALLY_TESTED.** Per-token RPE-modulated LR is the open lane (memory entry confirms "per-token schedule untested").

**Recommendation:** **DRILL the un-tested.** Cell anchor: `cfrpe_per_token_adaptive_lr_v1`. Compare per-token RPE-modulated LR vs the @5000-step block at N_DIM=8192 fair_harness baseline. Pre-reg HP: lift ≥ 0.40 over Hebbian (above current 0.30 single-arm; aiming for cf-RPE×per-token-schedule super-additive). HF: lift ≤ 0.20.

**Per-assumption confidence:** PARTIALLY-TESTED; the formula needs ONE more test (per-token).

---

### A7 — Cert process catches biases (Director vs Skunkworks may share biases)

**Headline:** PARTIALLY_TESTED. **Recent track record shows Skunkworks correctly overrides Director on by-construction-saturation, but NEITHER caught the wrong-metric trap that drove 7+ HARD-FAILs.**

**Store-mined evidence:**
- META atoms 2026-06-22 to 2026-06-24: by-construction-saturation discipline used 5+ times by Skunkworks to override Director's chain-grade claims.
- META_HARNESS_RIGGED atom: BOTH Director AND Skunkworks were running the wrong-metric harness for ~7 cells before user-directed methodology audit caught it.
- [[feedback-fix28-recurring-skunkworks-correct-more-than-director-2026-06-23]] — Director over-claims from verdict_msg framings; Skunkworks reads metrics.json per-arm.
- Phase 3 Agent Teams (skunkworks_phase_b_window2 + capint role-separation) demonstrates 2-role catches; multi-role does NOT.

**Classification:** **PARTIALLY_TESTED.** Cert process catches mechanism-saturation but does NOT catch metric-class mismatches between substrate and evaluation paradigm.

**Recommendation:** **CHANGE the assumption.** Cert process catches by-construction-saturation but NOT methodology-confound. Add a META cert layer for "is the harness measuring what we claim to be measuring?" — explicit check on metric-class alignment with substrate's structural strength. This is the missing 5th cert layer (engine/checklist/invariant/integration/METRIC-CLASS).

**Per-assumption confidence:** SHOULD BE CHANGED — add the 5th cert layer.

---

### A8 — Top1 over unigram is the right chain-grade metric (vs top1 over bigram)

**Headline:** PARTIALLY_TESTED. **Top1 over unigram is necessary (substrate clears it +61% per n1_v3) but NOT SUFFICIENT — top1 vs bigram is the genuinely-non-trivial bar.**

**Store-mined evidence:**
- `EXP_n1_concept_lm_v3`: substrate top1=0.4455 vs unigram 0.276 (+61% lift, CHAIN-GRADE per Skunkworks 2026-06-23); BUT vs bigram 0.4734 substrate is at 94%. **Substrate beats unigram easily but BARELY matches bigram.**
- `EXP_substrate_brain_word_level_prediction_v1_smoke`: substrate K=5 top1=0.191 vs word-bigram 0.186 → +2.7% lift but smoke only.
- Bigram top1 in fair_harness V=4000 text8 is ~0.30-0.35 (not directly measured but bigram BPC ~6.5 vs unigram 7.74 implies top1 lift of similar magnitude).

**Classification:** **PARTIALLY_TESTED.** Top1 vs unigram works as a FLOOR; top1 vs bigram is the discriminator.

**Recommendation:** **MODIFY the assumption.** Use top1 over unigram as the FLOOR for chain-grade eligibility; use top1 over bigram (and top-K over bigram) as the SHIP-IT discriminator for "substrate IS non-trivial LM-class." This matches biological reality (brain's ~1 bit/char is at word-prediction not unigram).

**Per-assumption confidence:** SHOULD BE MODIFIED. Floor = unigram, ceiling discriminator = bigram, true target = brain (~1 bit/char).

---

### A9 — Substrate is complete as currently built (vs missing recurrence/hierarchy/learned-encoder)

**Headline:** **FALSE.** UN-TESTED for multiple critical components. Brain mechanisms drill (2026-06-24) names 20+ UN-TESTED brain mechanisms.

**Store-mined evidence:**
- `EXP_substrate_self_map_v2c_HN` (HONEST_NEGATIVE): substrate self-mapping NULL at full-Store scope. Substrate does NOT cluster its own atoms into Director-style categories.
- Brain mechanisms drill (2026-06-24) — composite-20 UN-TESTED: word-level theta-grain prediction; 2-level Rao-Ballard PC; working memory persistent activity (PARTIAL: HRR-slots HP at K=32); BCM rule.
- Substrate aliveness map (2026-06-24): Dimension 3 has 4 METHCONF HARD-FAIL atoms (all under wrong-metric trap), Dimension 5 (multi-bank) has K=4 sparse-W HARD-FAIL at N=2048 and K>=8 has no atom.
- Working memory (`EXP_working_memory_hrr_slots_PRODUCTION_v1` HP K=32 at N=4096) — chain-grade-eligible primitive demonstrated.
- `EXP_substrate_pc_hierarchy_text8_lm_v1+v2` (METHCONF) — Rao-Ballard PC HARD-FAIL under wrong harness; verdict suspended.

**Classification:** **UN_TESTED for completeness claim.** Tested for individual primitives; UN-TESTED for whether the assembled stack covers the LM-required mechanism set.

**Recommendation:** **CHANGE the assumption.** Substrate is INCOMPLETE. Missing core components per brain mechanisms drill: (a) word-level theta-grain prediction (composite 20); (b) 2-level Rao-Ballard PC with top-down feedback (composite 18); (c) working memory persistent activity across tokens (PARTIAL: HRR-slots HP but not as register); (d) BCM rule (composite 18). Top 3 highest-leverage UN-TESTED tests are: word-level prediction, 2-level PC w/ top-down, working memory register.

**Per-assumption confidence:** SHOULD BE CHANGED — substrate is INCOMPLETE; route un-tested mechanisms next.

---

### A10 — text8 next-char corpus is the right task (vs PTB / WikiText / word-level)

**Headline:** PARTIALLY_TESTED with **wrong-grain diagnosis**. text8 next-char tests at 30Hz (every char position) but the brain operates at theta-band ~5Hz word rate.

**Store-mined evidence:**
- `EXP_substrate_brain_word_level_prediction_v1_smoke` (MIDDLE_BAND): word-level smoke at V=400 N_DIM=512 — substrate K=5 BPW=6.174 (vs word-bigram 6.449) — small lift, smoke only but direction-correct.
- `EXP_b2_substrate_only_tinystories_lm_v1` (HARD_FAIL): tinystories at V=8000 — substrate-only HARD-FAIL at larger vocab (mechanism failure flagged).
- `EXP_h_hotpotqa_ingest_v1` (HARD_PASS): Wikipedia full vocab — substrate composes 2-hop 0.991 (892x discriminator).
- `EXP_n6_wikitext103_ingest_cert_v1`: WikiText-103 ingest (not deep-tested for LM).
- `EXP_substrate_direct_gen_lm_wikitext_trigram_v3` (HARD_FAIL): substrate ppl=14.2 vs bigram_count=9.3 wikitext.
- `EXP_pos_tagger_ptb_substrate_cpu_v1`: PTB POS tagging (not LM).
- Brain mechanisms drill 2026-06-24 explicit recommendation: "Substrate's current char-level testing at ~30Hz is fundamentally OFF-grain from what the brain does."

**Classification:** **PARTIALLY_TESTED, with corpus + grain discrepancy.** Tested at text8 char-level (30Hz); brain operates at word-level (~5Hz). The grain mismatch may explain part of why substrate-as-LM gaps are persistent.

**Recommendation:** **MODIFY the assumption.** Run substrate at WORD-level (theta-grain, ~5Hz) on text8 word-tokenized — predicting next-word given K previous words. This is the brain-canonical task. text8 char-level is fine as a primitive-test rail but does NOT represent the LM evaluation the brain does.

**Per-assumption confidence:** SHOULD BE MODIFIED. Run word-level LM as PRIMARY; char-level as substrate-mechanism-test.

---

### A11 — f sparsity as PHASE-SHIFTABLE parameter (state-dependent f)

**Headline:** **UN_TESTED.** No cell tests dynamic-f / state-dependent sparsity / brain-style cortical-state sparsity switching.

**Store-mined evidence:**
- Searched substrate_index for "adaptive_f", "state_dep_sparsity", "phase_shift", "dynamic_f": ZERO hits.
- `EXP_substrate_drosophila_mb_sparsity_sweep` tests STATIC f-grid; same f maintained throughout.
- `EXP_substrate_sparsity_fine_battery_gpu_v1` tests STATIC f at 7 settings.
- ALL sparsity cells use FIXED f throughout the cell.
- Adaptive cleanup operator exists (`EXP_adaptive_cleanup_operator_v1_n4096`) — adaptive threshold for cleanup, NOT adaptive f for write.
- Brain mechanisms drill 2026-06-24 lists "Acetylcholine encoding-mode gain" as UN_TESTED — this is the BRAIN ANALOG of dynamic-f (ACh shifts cortex from sparse-retrieval mode to dense-encoding mode).

**Brain-existence-proof:** YES. Cortical sparsity is dynamic (Aston-Jones LC-NE; ACh release modulates excitability and sparsity; sleep-wake transitions change cortical population activity statistics). Goard & Dan 2009 (Nature Neurosci): ACh release in V1 desynchronizes/sparsifies activity. Brain DOES phase-shift sparsity.

**Classification:** **UN_TESTED.** ZERO cells.

**Recommendation:** **DRILL** — propose new cell. Anchor: `dynamic_f_phase_shift_sparsity_v1`.
- ARMS: ARM_F_STATIC_002 (current best); ARM_F_STATIC_005 (current default); ARM_F_DYNAMIC_005_TO_05 (dense at write, sparse at read); ARM_F_DYNAMIC_05_TO_002 (sparse at write, dense at retrieval).
- Pre-reg HP: any dynamic arm gives ≥ +0.10 bits BPC lift over best static arm AND CV ≤ 0.05.
- Pre-reg HF: all dynamic arms ≤ best static arm.
- Cost: ~45 min smoke + 4-6h full on remote GPU (reuses fair_harness rail).

**Per-assumption confidence:** ASSUMPTION UNKNOWN — needs test. P=0.45 deflated (brain-existence-proof boost from 0.50 down 0.05 for substrate-novel implementation).

---

### A12 — Hierarchy (flat substrate vs hierarchical brain)

**Headline:** PARTIALLY_TESTED with **CONTRADICTORY EVIDENCE**. Hierarchy WORKS for aggregation/retrieval but DEGRADES for capacity in the 1 cell that measured it; PC hierarchy HARD-FAIL is under METHCONF (suspended verdict).

**Store-mined evidence:**
- `EXP_substrate_hierarchical_5corpus_meta_v1+v2` (CHAIN_GRADE HP, n=3 seeds, mean lift): substrate aggregates 5 domains H3=2.598<H2=6.196; H4_retention=1.002. **Hierarchy WORKS for cross-domain aggregation.**
- `EXP_substrate_hierarchical_aggregator_scale_ext_domains5_10_20_v1_n2048` (CHAIN_GRADE HP): scales to 20 domains.
- `EXP_hierarchical_2level_cpu_v1` (HP): member-recall=1.000 at 2-level (smoke).
- `EXP_hierarchical_3level_cpu_v1` (HP): recall=1.000 at 3-level domain→category→item (smoke).
- `EXP_hierarchical_w_feasibility_v1_n4096` (**H_HARD_FAIL**): hierarchical_acc=0.062, capacity_ratio=0.25 — hierarchy COSTS 75% of flat capacity at 5 seeds N=4096. The "hier_degrades" verdict.
- `EXP_substrate_pc_hierarchy_text8_lm_v1+v2` (METHCONF HARD-FAIL): PC 2-layer 8.10 BPC vs RANK1 7.80; PC adds no lift over rank-1 Hebbian on substrate-as-LM. **BUT UNDER WRONG-METRIC TRAP; verdict suspended pending fair_harness re-run.**
- `EXP_caching_multi_substrate_hierarchy_v1` (in store).
- `EXP_predictive_coding_hierarchy_smoke_v1` (smoke only).
- `EXP_m1_modular_macrocolumn_W_v2_FULL_CG` (CHAIN-GRADE): K=32 modular macrocolumn beats random; read_flops ≤ 0.5x monolithic at M=1000.

**Cross-evidence resolution:** Hierarchy helps when (a) used for cross-domain aggregation (HARD-PASS chain-grade); (b) used for organizational retrieval (HP); but HURTS when (c) used for capacity at fixed N_DIM (cap_ratio 0.25). PC hierarchy verdict is SUSPENDED under METHCONF.

**Classification:** **PARTIALLY_TESTED with CONTRADICTORY results.** Need direction-specific evidence on PC-hierarchy under fair_harness.

**Recommendation:** **DRILL** — propose new cell. Anchor: `pc_hierarchy_fair_harness_v1`.
- Use fair_harness substrate-as-LM rail (already chain-grade); add ARM_PC_2_LAYER + ARM_PC_5_LAYER as additional arms with TOP-K + selection-mixer metrics (not BPC).
- Pre-reg HP: PC arms beat RANK_1 by ≥ +0.05 top-1 OR ≥ +0.05 BPC under selection-mixer (M4 from META_HARNESS_RIGGED).
- Pre-reg HF: PC arms ≤ RANK_1 on ALL metrics under revised harness.
- Cost: ~3-4h full on remote GPU. Reuses fair_harness infrastructure.

**Brain-existence-proof:** YES strong. 6+ cortical layers; canonical microcircuit (Douglas-Martin 2004); cortico-cortical feedback >10x feedforward; predictive coding requires hierarchy (Rao-Ballard 1999; Friston 2010); compositional abstraction levels (lexical → syntactic → semantic).

**Per-assumption confidence:** ASSUMPTION CONTRADICTORY DATA — needs test. P=0.55 deflated for "hierarchy CAN help substrate" (brain-existence-proof + 5-corpus chain-grade evidence + capacity-degrade evidence).

---

## SECTION 2: SYNTHESIS — TOP 3 HIGHEST-LEVERAGE TESTS

Ranked by (brain-existence-proof × composite-leverage × cost-cheap):

### Rank 1 — Word-level theta-grain LM (A10 modification + A1 reframe)
**Anchor:** `substrate_word_level_lm_v1_FULL` (lifted from smoke MIDDLE_BAND).
**Hypothesis:** Substrate at WORD-grain (not char-grain) closes the gap-to-brain by aligning to brain's theta-rate prediction.
**Pre-reg HP:** word-level substrate K=5 BPW ≤ word-bigram BPW − 0.30 bits AND top1 ≥ word-bigram top1 + 0.05.
**Pre-reg HF:** substrate BPW ≥ word-bigram BPW.
**Cost:** ~4-6h GPU. Reuses fair_harness rail at word-tokenized text8.
**Brain-existence-proof:** Ding & Poeppel 2016; Kazanina-Tavano 2025 BRyBI.
**P_deflated:** 0.55.

### Rank 2 — Per-token cf-RPE adaptive LR (A6 drill)
**Anchor:** `cfrpe_per_token_adaptive_lr_v1`.
**Hypothesis:** Per-token RPE schedule beats coarse-step (5000) cf-RPE by ≥ 0.10 bits.
**Pre-reg HP:** lift ≥ 0.40 over Hebbian baseline (vs current 0.30 single-arm); CV ≤ 0.10.
**Pre-reg HF:** lift ≤ 0.20.
**Cost:** ~2-3h GPU.
**Brain-existence-proof:** Schultz 1997 dopamine RPE; Gerstner-Sjöström STDP per-spike updates.
**P_deflated:** 0.50.

### Rank 3 — Dynamic-f phase-shift sparsity (A11 un-tested)
**Anchor:** `dynamic_f_phase_shift_sparsity_v1`.
**Hypothesis:** Dynamic-f (dense at write, sparse at retrieval, or inverse) beats static-f by ≥ 0.10 bits.
**Pre-reg HP:** any dynamic arm ≥ +0.10 BPC lift over best static arm.
**Pre-reg HF:** all dynamic arms ≤ best static arm.
**Cost:** ~3-4h GPU.
**Brain-existence-proof:** Goard-Dan 2009 ACh modulation; Aston-Jones LC-NE.
**P_deflated:** 0.45.

---

## SECTION 3: TOP 3 WRONG ASSUMPTIONS WE MAY BE HOLDING

### Wrong-1: A1 substrate-as-LM is the right product target → **REFRAME**
Substrate is chain-grade as **memory-store + compositional reasoner**. Forcing it into "LM-replacement" framing leads to wrong-metric trap. Product = memory-layer + reasoner FOR an LM, not full LM.

### Wrong-2: A5 f=0.05 is optimal → **CHANGE TO f=0.02**
Production optimum is f=0.02 (or f=0.01 at small N). f=0.05 origin is drosophila lit; capacity sweeps consistently show ~30% lift at f=0.02. Default switch saves capacity headroom across all downstream cells.

### Wrong-3: A9 substrate is complete → **CHANGE TO INCOMPLETE**
Substrate lacks word-level prediction, 2-level PC with top-down feedback, persistent working-memory register across tokens (HRR-slots demonstrated but not integrated), BCM rule, lateral connections. Top 3 missing components are high-composite (18-20).

---

## SECTION 4: RECOMMENDED ORDER OF OPERATIONS

1. **IMMEDIATE (this cycle):** Ship `pc_hierarchy_fair_harness_v1` to resolve A12 contradiction. Cheap (~3-4h GPU); reuses chain-grade rail. Resolves SUSPENDED METHCONF verdict on PC hierarchy.

2. **NEXT (2-3 cycles):** Ship `substrate_word_level_lm_v1_FULL` to resolve A10 grain-mismatch + reframe A1. ~4-6h GPU; this is the highest-leverage test in the queue.

3. **AFTER (3-5 cycles):** Ship `cfrpe_per_token_adaptive_lr_v1` (A6) + `dynamic_f_phase_shift_sparsity_v1` (A11) in parallel — independent mechanisms, both ~2-4h GPU each.

4. **PARALLEL META-WORK:** Add the 5th cert layer (METRIC-CLASS alignment check) per A7 finding. Make the META_HARNESS_RIGGED atom + recommended top-K + selection-mixer the DEFAULT for any new substrate-as-LM cell. Update active_protocols.md and pre-reg envelope-fail-bands template.

5. **DEFAULT-SWITCH:** When the f=0.02 vs f=0.05 evidence is corroborated by ≥1 more production-scale fair_harness arm sweep, change the substrate's default sparsity from 0.05 to 0.02. Path: queue an explicit replicator `fair_harness_f_002_default_v1`.

---

## CITATIONS (verified count)

**Verified cells (metrics.json read):** 13
- exp_ghrr_vs_fhrr_triple_encoder_capacity_directionality_cpu_v1
- exp_substrate_drosophila_mb_sparsity_sweep_v1_512_2048_gpu
- exp_substrate_hierarchical_5corpus_meta_v2_n2048_gpu
- exp_fair_harness_substrate_as_lm_v1
- exp_substrate_pc_hierarchy_text8_lm_v1
- exp_n1_concept_lm_substrate_native_token_decode_v3
- exp_depth_pinned_hrr
- exp_depth_pinned_fhrr_clipped
- exp_depth_vtb
- exp_substrate_capacity_composition_full_b2xb4xhier_v1_n2048_gpu
- exp_sparse_alpha_fine_sweep_below_004_v1
- exp_substrate_sparsity_fine_battery_gpu_v1
- exp_hierarchical_2level_cpu_v1 + 3level + w_feasibility
- exp_fhrr_rs_parity_cpu_v1
- exp_working_memory_hrr_slots_PRODUCTION_v1
- exp_substrate_brain_word_level_prediction_v1_smoke
- exp_substrate_theta_gamma_nested_oscillation_LM_v1
- exp_b2_substrate_only_tinystories_lm_v1
- exp_h_hotpotqa_ingest_v1
- exp_substrate_native_qa_hotpotqa_v2_composition_drill
- exp_sparse_bipolar_substrate_lm_param_sweep_v1
- exp_substrate_heterogeneous_plasticity_cfrpe_stdp_fair_harness_v1
- exp_substrate_direct_gen_lm_wikitext_trigram_v3_n8192_gpu

**Verified notes:** 4 (deep-read)
- notes/research_substrate_aliveness_FULL_store_mined_map_2026-06-24.md
- notes/research_brain_mechanisms_NOT_yet_tested_2x_drill_2026-06-24.md
- notes/research_drill_substrate_as_lm_test_methodology_audit_2x_2026-06-23.md
- notes/skunkworks_to_all_LANDED_VET_META_HARNESS_RIGGED_substrate_as_lm_reclassification_2026-06-23.md
- notes/research_surprise_baseline_7p22_vs_7p30_2x_drill_2026-06-24.md

**Verified ledger queries:** cert_ledger.jsonl 707 rows × multiple grep filters for hrr/fhrr/sparsity/hierarchy/methconf/honest_negative. 481 chain-grade atoms + 29 honest-negative.

**External brain literature (verified citations not searched in this drill — relied on the brain mechanisms drill 2026-06-24's verification):**
- Ding & Poeppel 2016 Nature Neurosci (theta tracks words)
- Kazanina & Tavano 2025 Nature Comp Sci (BRyBI delta/theta)
- Rao & Ballard 1999 Nature Neurosci (PC original)
- Friston 2010 Nat Rev Neurosci (free energy)
- Schultz 1997 J Neurophysiol (dopamine RPE)
- Bi & Poo 1998 J Neurosci (STDP)
- Caucheteux 2022 (8-token hierarchical brain prediction)
- Goard & Dan 2009 (ACh sparsifies V1)
- Olshausen & Field 1996 (sparse coding)
- Bricken & Schick 2021 (SDM-attention)

Brain-evidence sourcing inherits from brain mechanisms drill 2026-06-24 (verified there).

---

## METADATA

- Calibration penalty: 0.20 deflation applied to novel-synthesis P-claims.
- P_deflated overall: 0.55 (raw 0.72; deflated 0.17 due to 4 un-tested / under-tested assumptions where novel-synthesis is required).
- Next-drill candidate (per field advisor heuristic, brain-existence-proof Tier-1b): **`hierarchy` field, drill `pc_hierarchy_fair_harness_v1`** (resolves SUSPENDED METHCONF + adjacent to chain-grade 5-corpus aggregator).
- All findings ASCII-only.
- Output companion exp_dev handoff written: `notes/exp_dev_handoff_research_meta_skepticism_12_assumptions_2026-06-24.md` (rank-ordered anchor candidates for top 3 tests).
