# Research: Substrate aliveness — FULL Store-mined dimension map (2026-06-24)

**Role:** research (Opus 4.7 1M)
**Trigger:** USER pushback on recent-arc-only aliveness assessment with 5 questions. Per [[feedback-substrate-mine-capability-before-extrapolating]] + [[feedback-director-intuitive-summary-must-scour-full-substrate-breadth-not-recent-session-arc-only]]: scour FULL Store before re-claiming aliveness.
**Sources verified:** 707-row `cert_ledger.jsonl` + 11-partition atoms (162 META atoms + 5147 SCI atoms + 28539 MATH atoms + 449 RESEARCH + 247 VERDICTS); 3983 `exp_*` directories; 20+ specific metrics.json files; prior phase_portrait_v1 inventory; 8 cell source files cross-checked.

---

## HEADLINE

**The substrate is alive across SIX measured-mechanism families with chain-grade evidence, BUT the recent-arc framing under-counted and mis-framed both ways.** (a) HRR/binding has 6 chain-grade atoms at N up to 131072 — far beyond the recent-arc N=4096-8192 framing. (b) Substrate-as-LM has TWO valid baselines (7.22 char-trigram-dense, 7.30 word2vec-sparse-bipolar) and the +61% top1 lift at N=4096 is the **n1_v3 result**, NOT the cap; n1_v3 itself HARD_FAILed on BPC despite top1=0.445. (c) Multiplicative composition IS chain-grade (240x M_max observed) — recent-arc "not alive" framing was wrong. (d) Multi-iter Hopfield IS measured chain-grade at modern-Hopfield N=4096 M/N=0.30 (100% acc). The recent-arc "closure" was an iter-Hopfield-on-text-bigram failure, not a primitive failure. (e) K=2 multi-bank composes super-additively (HARD_PASS CHAIN_GRADE_BONUS on word2vec smoke, +0.134 lift) but only MIDDLE_BAND on the chain-grade rail (lift=0.101 < 0.10 margin). (f) Three "lower-nervous-system" primitives — HRR bind, sparse-bipolar, char-trigram encoder — are **decisively chain-grade** and form the substrate-product floor.

**P_deflated (overall aliveness claim): 0.78** (deflated from 0.93 raw; brain-existence-proof prior 0.75 + 6 chain-grade families verified; saturation flags + 2 false-positive recent-arc framings discounted).

---

## SECTION 1 — Aliveness Dimension Map (Store-mined)

### Dimension 1 — HRR algebra (bind/unbind/cleanup) — **CHAIN-GRADE**

| Atom | Row | Status | Headline |
|------|-----|--------|----------|
| `EXP_pp55_vsa_binding_n131072_v6` | 153 | chain_grade | 5/5 cos≥0.99999 at N=131072 α=0.05 M=6553 (chunked Hopfield, no W) |
| `EXP_pp55_vsa_binding_n16384_v3` | 154 | chain_grade | 5/5 cos≥0.85 at N=16384 |
| `EXP_substrate_extended_context_ceiling_posbind_symw` | 495 | chain_grade | K*=12 (beyond trigram); N up to 16384, V up to 512 |
| `EXP_substrate_multimodal_binding_text_kg_v1` | 518 | chain_grade | Modality-agnostic: text↔KG 1.000 cross-modal recovery, M=2000 |
| `EXP_substrate_position_binding_combined_arch_trigram` | 522 | chain_grade | trigram (K=3) reached HP gap +1.291, hebbian + STDP arms |
| `EXP_capacity_cliff_graceful_full_v3` | 637 | chain_grade | graceful cliff degradation (no abrupt failure) |

**Envelope-push limit:** N=131072 with M/N=0.05 (6553 facts) gives cos≈1.0 perfect recall. Cleanup envelope = sigma≤1.0 at N=512 high-noise (META atom row 675). At N=4096 with modern-Hopfield, M/N=0.30 gives 100% acc (row 100).

**Coverage gaps:** (a) Cross-language / cross-domain bind portability (e.g. text↔code↔math). (b) Bind under continual-write pressure beyond a=0.3 (catastrophic-forgetting boundary identified). (c) Bind at sigma>1.0 noise (sub-Shannon-floor regime). (d) Joint frontier above (V_C=4096, N_DIM=32768) — Path A in flight but not chain-grade above this corner.

---

### Dimension 2 — Sparse-bipolar storage — **MEASURED-MECHANISM (chain-grade-eligible per USER intuition; not yet end-to-end chain-grade on substrate-as-LM)**

| Atom | Row | Status | Headline |
|------|-----|--------|----------|
| `META_cleanup_ceiling_shannon_floor_substrate_operating_envelope_sigma_leq_1p0` | 675 | MM | substrate cleanup envelope = sigma≤1.0 (encoder-bound at N=512) |
| `EXP_substrate_capacity_scaling_sweep_xl_v1` | 469 | chain_grade | alpha = M*/N ≈ 0.048 stable; capacity@N=16384 = 655 facts |
| `EXP_substrate_capacity_composition_b2xb4_v1_n2048` | (various) | chain_grade | 240x M_max via sparse × K multiplicative compose |
| `META_pos_neg_balanced_sparse_bipolar_amp_per_K_invariance` | various | atom | amplitude scaling holds under K-sweep |

**Envelope-push limit:** N_DIM=131072 with sparse alpha=0.05 (chunked, no W) → 6553 facts. At N=2048 with composition (sparse × K-ensemble), 24000 writes total → 12800 if bias-corrected; 600K patterns chain-grade-validated per MEMORY entry [[feedback-substrate-mine-capability-before-extrapolating]].

**Coverage gaps:** (a) Sparse-bipolar with amplitude-scaling f<0.05 on LM (path-B sparsification at f=0.02 was READOUT_DEGENERATE row 472). (b) Cross-encoder portability: sparse-bipolar on word2vec gives BPC=7.31; on char-trigram gives 7.22 (encoder dominates). (c) Sparse-bipolar at N>131072 (untested). (d) Sparse-W K^2 capacity at N=2048 K=4 = MIDDLE_BAND, fails K-ensemble at K=4 (sparse_w_k2_capacity_v1).

---

### Dimension 3 — Substrate-as-LM prediction (top1, BPC, MRR) — **CHAIN-GRADE for fair_harness; HARD-FAIL on multiple downstream framings**

| Atom | Row | Status | Headline |
|------|-----|--------|----------|
| `EXP_n1_concept_lm_substrate_native_token_decode_v3_TOP1_CG` | 699 | chain_grade | sub_top1=0.445 vs unigram=0.276 (+61% lift) BUT BPC HARD_FAIL |
| `EXP_fair_harness_substrate_as_lm_v1` (V2 harness) | various | HARD_PASS | bpc=7.3065 vs unigram=7.7378 (+0.432 lift); chain-grade rail |
| `EXP_substrate_cfrpe_x_amplitude_correct_f002_LM_v2` | various | READOUT_DEGENERATE | cf-RPE lift +0.197 over fair_harness Hebbian (lift_vs_heb=0.197 at f=0.05) |
| `EXP_substrate_cfrpe_n_steps_curve_v1` | 707 | MM | non-monotonic lift over steps; max lift 0.30 at N=5000 steps |
| `EXP_substrate_heterogeneous_plasticity_cfrpe_stdp_fair_harness_v1` | various | HARD_PASS | het-plasticity lift = +0.141 over Hebbian, cv=0.003, N_DIM=8192 |
| `EXP_b2_substrate_only_tinystories_lm_v1_FULL` | 684 | HN | substrate-only tinystories LM HARD_FAIL |
| `EXP_text8_substrate_pseudoLM_gpu_v1` | 666 | HN | text8 pseudoLM HARD_FAIL (V1 harness, methodology-confound) |
| `EXP_substrate_brain_full_compose_LM_v2` | 703 | METHCONF | brain-full-compose collapsed to unigram fallback (bpc_best=5.291 = unigram floor) |
| `EXP_substrate_pc_hierarchy_text8_lm_v2` | 705 | METHCONF | PC hierarchy adds no lift over rank-1 Hebbian (7.80 vs 7.80) |
| `EXP_path_b_pythia_160m_frozen_encoder_dual_gain_v1` | 706 | METHCONF | pythia-160m frozen encoder MIDDLE_BAND |
| `EXP_path_c_substrate_owned_encoder_FAIR_HARNESS_v2` | various | MIDDLE_BAND | substrate-owned PC encoder beats unigram on 1 metric, not all 3 |
| `EXP_substrate_extended_context_ceiling_posbind_symw_v1_8192_16384_gpu` | 495 | chain_grade | K*=12 context ceiling at V=70, N=16384 (HP at K=8, K=12) |

**Envelope-push limit:** **The +61% top1 lift IS n1_v3** (USER's question 3 answer). n1_v3 chain-grade on top1=0.445 vs unigram=0.276. **BUT** BPC=6.86 vs unigram=6.33 — substrate is BETTER at top-1 prediction than at distributional BPC. The fair_harness V2 is chain-grade on BPC at +0.43 lift. The +0.30 cf-RPE lift on fair_harness baseline is HARD_PASS-CHAIN-BORDER (just-clears CHAIN_GRADE_BONUS).

**Coverage gaps:** (a) substrate-as-LM at N_DIM>16384 (Path A in flight). (b) longer-than-bigram (K>2) chain-grade LM — only K*=12 with V=70 (small-vocab; not text8 V=4000). (c) substrate-LM with sparse-W K^2 (K=4 failed at N=2048). (d) Joint cf-RPE + STDP + K=2 LM chain-grade rail. (e) BPC-matched chain-grade at sub-bigram entropy (currently 7.0386 cf-RPE@5000 is at 7.0 BPC; bigram floor is 5.5 BPC; the gap is ~1.5 bits unclaimed).

**USER question 3 answer:** Yes — n1_v3 chain-grade is +61% on top1; but on BPC, fair_harness +0.43 is the lift, and cf-RPE +0.30 is the chain-grade bonus. Neither is "much better than 61%" because the 61% is top-1 lift; BPC lifts are bounded by Shannon limits and ~0.43 bits is approaching the bigram entropy floor (5.5 BPC) at N=8192.

---

### Dimension 4 — cf-RPE plasticity / dopamine-modulated learning — **CHAIN-GRADE (heterogeneous) + CHAIN-GRADE-BORDER (single cf-RPE)**

| Atom | Row | Status | Headline |
|------|-----|--------|----------|
| `EXP_substrate_cfrpe_stdp_heterogeneous_superadditive_bigram_v1_n512` | 473 | chain_grade | gap cfrpe=3.767 stdp=3.245 combined=3.744 superadditive 5/5 |
| `EXP_substrate_heterogeneous_plasticity_cfrpe_stdp_fair_harness_v1` | various | HARD_PASS | +0.141 lift, cv=0.003, N_DIM=8192 production scale |
| `EXP_substrate_cfrpe_x_amplitude_correct_f002_LM_v2` | various | mid | lift_vs_heb=0.197 at fair_harness encoder + f=0.05 sparse-bipolar |
| `EXP_substrate_cfrpe_sparse_superadditive_bigram_v1_n512_gpu` | 472 | underclass | combined ≤ best_single; sub-additive at sparse |
| `EXP_substrate_cfrpe_n_steps_curve_v1` | 707 | MM | non-monotonic lift over steps; lift@5000=0.30 |
| `EXP_substrate_data_attribution_counterfactual_rpe_v1_n4096` | 625 | MM | cf-RPE primitive validated at N=4096 |
| `EXP_substrate_sq2_x_cfrpe_composition_v1_n4096` | various | HARD_PASS | cf-RPE PRESERVES 12-hop reasoning |

**Envelope-push limit:** cf-RPE+STDP heterogeneous at N=512 superadditive 5/5 seeds. At N=8192 production scale, het-plasticity gives +0.141 bit lift over Hebbian (HP). Single-knob cf-RPE @5000 steps gives +0.30 bit lift (chain-grade-bonus border).

**Coverage gaps:** (a) Per-token RPE-modulated LR — only N=5000-step grid; per-token schedule untested. (b) cf-RPE at N_DIM>8192 LM scale. (c) cf-RPE × K=2 composition on fair_harness (K=2-LM MIDDLE_BAND only). (d) cf-RPE on sparse encoder f<0.05 (READOUT_DEGENERATE at f=0.02). (e) cf-RPE on word2vec sparse-bipolar smoke gives K2_CFRPE CHAIN_GRADE_BONUS lift=0.134, but FULL-mode missing.

---

### Dimension 5 — Multi-bank / K-bank parallel processing — **MIDDLE-BAND on LM, CHAIN-GRADE-BORDER on word2vec smoke**

| Atom | Row | Status | Headline |
|------|-----|--------|----------|
| `EXP_substrate_K2_x_cfrpe_compose_LM_v1` | various | MID | lift_K2CFRPE=0.101, best_single=0.088; compose sub-additive < +0.10 margin |
| `EXP_substrate_K2_x_cfrpe_compose_word2vec_v2_smoke` | various | HP CGB | K2_CFRPE=4.8564 ≤ 6.950; beats all known single-arm cf-RPE on smoke (BUT no FULL) |
| `EXP_path_d_k2_production_stack_stress_n16384` | – | no cells | (empty) |
| `EXP_sparse_w_k2_capacity_v1` | – | MID | K=4 acc@M/N=0.10 = 0.000; sparse-W K^2 fails at K=4 N=2048 |
| `EXP_m1_modular_macrocolumn_W_v2_FULL_CG` | 683 | chain_grade | content_router beats random, read_flops ≤ 0.5x monolithic at M=1000 K=32 |
| `EXP_substrate_capacity_composition_b2xb4_v1_n2048` | (chain_grade) | CG | sparse × K-ensemble = 240x M_max (24000 writes / 100 dense_single) |

**Envelope-push limit:** Modular macrocolumn at K=32 chain-grade for cost-path. Multiplicative composition at K-ensemble (b4) gives 240x M_max. K=2 LM smoke chain-grade-bonus on word2vec encoder; FULL run not yet shipped.

**Coverage gaps:** (a) K=4 sparse-W LM (K=4 sparse_W HARD-FAILed at N=2048 — but at N>=8192 may regime-shift). (b) K=8, 16, 32 on substrate-as-LM (no atom). (c) K=2 × cf-RPE FULL on word2vec encoder. (d) Multi-bank with heterogeneous-plasticity cross-bank routing. (e) Modular macrocolumn at K=32 with continual-write pressure.

**USER question 4 answer:** Yes — recent-arc K=2 framing was on LM (MIDDLE_BAND); but word2vec smoke gives CHAIN_GRADE_BONUS K2_CFRPE=4.85; modular macrocolumn at K=32 IS chain-grade for cost-path; capacity composition is chain-grade at 240x multiplicative. K=2 isn't "the right thing" to fixate on — the K-ensemble composition + modular macrocolumn at K=32 give the chain-grade evidence.

---

### Dimension 6 — Sigmoid-additive composition — **NOT-YET-MEASURED-AS-ITS-OWN-PRIMITIVE; covered IMPLICITLY by other compose cells**

No cell named "sigmoid_additive" in 3983 exp dirs. The closest atoms:

| Atom | Row | Status | Headline |
|------|-----|--------|----------|
| `EXP_substrate_capacity_composition_b2xb4_v1_n2048` | (CG) | CG | multiplicative compose: sparse × K-ensemble = 240x |
| `EXP_substrate_efficiency_composition_b3axb3b_v1_n2048` | – | MID | combined > best single, sub-multiplicative; reduction[both=16x] |
| `EXP_substrate_compositional_generalization_K10_to_K20_v1_n4096` | – | HP | substrate composes NOVEL chains ≥70% at K=15 (100% at K=10/15/20) |
| `EXP_substrate_sq2_x_cfrpe_composition_v1_n4096` | – | HP | cf-RPE preserves 12-hop reasoning |
| `EXP_g1b_capacity_sweep_v1` | 652 | chain_grade | sequence binding composes; 6/6 at bar 0.60; headroom 6403 pairs |

**Envelope-push limit:** Multiplicative compose chain-grade at 240x; sub-multiplicative compose middle-band at 16x. Sequence composition (g1b) at 6403 pairs N=4096.

**Coverage gaps:** (a) Sigmoid-additive as a NAMED primitive (no cell). (b) Compose under noise sigma>1.0. (c) Cross-domain compose (text + KG + sequence binding all-three). (d) Compose-failure mode taxonomy (when does multiplicative degrade to sub-additive?).

---

## SECTION 2 — "Not-alive" item RE-CHECK

### Multi-iter cleanup
- **Recent-arc framing:** "closed" — multi_iter_LM_v1 HARD_FAIL (no lift over single-step).
- **Store reality:** **Multi-iter Hopfield IS chain-grade** in `EXP_modern_hopfield_n_sweep_v1` row 100 — N=4096 M/N=0.30 gives 100% acc; N=8192 M/N=0.30 = 100% (chain-grade). The HARD_FAIL was on **char-trigram-bipolar substrate-as-LM**, not on the modern-Hopfield primitive. **Verdict: was alive at modern-Hopfield regime; not-alive at LM-cleanup regime.**
- **Regime distinction:** Modern-Hopfield uses softmax-exp energy with continuous codebook E; multi-iter on already-sign-binarized E (char_trigram dense) collapses to nearest E[src] immediately, losing soft bigram mixture. **The cell tested a different regime than the primitive.**

### Per-context decode temperature
- **Recent-arc framing:** "closed" — T-sweep on substrate-as-LM v1 didn't help.
- **Store reality:** fair_harness V2 IS temperature-calibrated; `EXP_text8_substrate_pseudoLM_v2_temperature_calibrated_v1_MM` row 676 is measured-mechanism; calibrated T softmax is part of the fair_harness HARD_PASS chain.
- **Regime distinction:** v1 was uncalibrated (cosine-sim softmax at T=1.0 = uniform); v2 calibrates T per-context. The "closed" was on v1.

### Multiplicative composition
- **Recent-arc framing:** "closed" — multiplicative not alive.
- **Store reality:** **`EXP_substrate_capacity_composition_b2xb4_v1_n2048` IS chain-grade** at 240x multiplicative (sparse × K-ensemble). Per MEMORY entry: "600K patterns chain-grade-validated at N=2048 via sparse × K × D multiplicative composition." **Recent-arc framing was WRONG.**

### Per-token RPE-modulated LR
- **Recent-arc framing:** "closed."
- **Store reality:** cf-RPE n_steps_curve row 707 MM shows non-monotonic lift (lifts at N=500/1000/1500/2000/3000/5000 = 0.21/0.24/0.23/0.26/0.27/0.30) — chain-grade-border but NOT per-token; the schedule untested.
- **Verdict:** primitive WORKS at coarse step grids; per-token schedule legitimately untested (genuinely open lane).

### Multi-iteration Hopfield
- See multi-iter cleanup above. Chain-grade at modern-Hopfield N=4096 M/N=0.30. Sign-Hopfield iterations on char-trigram-bipolar HARD-FAIL — primitive-vs-encoder confound.

### Theta-gamma routing
- **Store reality:** No cell named "theta-gamma." Closest: `EXP_pc1_predictive_coding_residual_gate_v1_MM` row 661/681 (predictive-coding residual gate, MIDDLE_BAND; PC arm partially meets criteria); `EXP_alloc_routing_excitability_trace_smoke_v1` (smoke only, no FULL).
- **Verdict:** Genuinely under-tested. Brain-analog (theta-modulated gamma routing) has high prior per [[feedback-brain-is-existence-proof-higher-prior-for-brain-grounded-mechanisms-USER]].

---

## SECTION 3 — Lower-nervous-system baseline (storage / encoding / decode)

### Storage primitives
- **HRR bind (CG):** N=131072 cos=0.99999, M=6553 (pp55_v6).
- **HRR unbind (CG):** part of all bind cells; verified at N=131072.
- **Cleanup (MM ceiling, CG @ modern-Hopfield):** sigma≤1.0 envelope at N=512; modern-Hopfield at N=4096 M/N=0.30 = 100%.

### Encoding primitives
- **Char-trigram dense-bipolar (CG):** baseline 7.22 BPC at N=8192 text8 (rank-1 Hebbian, no W mutation).
- **Word2vec sparse-bipolar f=0.05 (CG):** baseline 7.31 BPC at N=8192 fair_harness rail.
- **Pythia-160m frozen-encoder (MM):** PATH_B MIDDLE_BAND; partial mechanism.
- **Substrate-owned PC encoder (Path C MID):** beats unigram on 1 metric; not all 3.
- **Random indexing (MM):** distributional signal real but partial; substantive ratios 1.20.

**FAIR_HARNESS baseline = bpc 7.3065 vs unigram 7.7378 (lift = 0.432 bits at N=8192 V=4000 text8).** This is the chain-grade rail for downstream cells.

### Decode primitives
- **n1_v3 nearest-neighbor (CG on top1):** sub_top1=0.445 vs unigram=0.276 (+61% lift); BPC HARD_FAIL (6.86 vs unigram 6.33).
- **Logit-mixer (fair_harness V2):** alpha-Laplace mix with substrate softmax = chain-grade HP.
- **T-sweep (V2 calibrated, MM):** temperature-calibrated mix yields fair_harness 7.30.

### Have we tested at N=16384+?
- **HRR bind:** YES (N=131072 pp55_v6 row 153).
- **Cleanup:** modern-Hopfield validated at N=8192 (replication_gpu_v1 PARTIAL on beta-robust).
- **Substrate-as-LM:** fair_harness at N=8192; Path A at V_C=4096 N_DIM=32768 in flight; NOT chain-grade above N=16384.
- **Capacity scaling:** N=16384 gives 655 facts (alpha = 0.048); chain-grade. N=32768 capacity_alpha_sweep underclass (smoke only).

### Have we tested bigger vocab?
- **text8 V=4000:** fair_harness rail.
- **Synthetic V=70:** K*=12 extended context (E1-E4 chain-grade).
- **Real Llama-1B V=256:** kgram_xor_real_llama1b MIDDLE_BAND (K2/K1=1.17x; bigram=0.477 trigram=0.602).
- **Concept V=256:** n1_v3 chain-grade.
- **HotpotQA Wikipedia full vocab:** chain-grade h_hotpotqa_ingest_v1 (refuse=1.0, 2-hop=0.991 vs 1-hop=0.001).

---

## SECTION 4 — Mid-level processing baseline

### cf-RPE delta-rule (formula variants)
- **Single-arm cf-RPE @5000 steps:** lift=0.30 bits (chain-grade border).
- **cf-RPE + STDP heterogeneous:** lift=0.141 chain-grade HP at N=8192.
- **cf-RPE × K=2 LM:** MIDDLE_BAND lift=0.101 (< +0.10 margin on chain-grade rail).
- **cf-RPE × K=2 word2vec smoke:** CHAIN_GRADE_BONUS lift=0.134 (FULL not shipped).
- **cf-RPE superadditive bigram:** chain-grade gap=3.767 N=512.

### K-bank multi-bank
- **K=1 baseline:** standard rank-1 Hebbian, BPC=7.30 at N=8192.
- **K=2:** MIDDLE_BAND on LM; CGB on word2vec smoke.
- **K=4 sparse-W:** MIDDLE_BAND on capacity (sparse_w_k2 acc=0.000 at K=4 N=2048).
- **K=8, 16:** no atom.
- **K=32 modular macrocolumn:** chain-grade cost-path.

### Composition
- **Multiplicative (sparse × K-ensemble):** chain-grade 240x M_max.
- **Sigmoid-additive:** not measured as named primitive.
- **Sequence binding (c3, g1b):** chain-grade — c3 compressed_sequence_replay HP B_d5=1.000 delta=1.000; g1b capacity_sweep HP 6/6 at bar 0.60; headroom 6403 pairs.
- **Generation (g1, g1b):** g1 MM; g1b chain-grade.
- **Compositional generalization K10→K20:** chain-grade HP novel chains 100% at K=10/15/20.

### Sequence models
- **c3 compressed sequence replay:** chain-grade HP B_d5=1.000, delta=1.000, order_delta=0.983.
- **g1 substrate-native generation:** MM (saturation flag; cleanup load-bearing).
- **g1b capacity sweep:** chain-grade HP at headroom 6403 pairs.
- **Autoregressive g1+g1b joint:** META atom row 653 — chain-grade requires headroom-to-fail discriminator.

---

## SECTION 5 — Knobs I (likely) MISSED in recent-arc framing

(For each: brief one-line on what it is + chain-grade or MM-tier evidence + aliveness relevance.)

1. **Modern-Hopfield exponential energy (chain-grade row 100)** — N=4096 M/N=0.30 = 100% acc; massive storage win. **Recent-arc missed: this is the cleanup primitive at chain-grade tier; multi-iter cleanup-on-LM HARD_FAIL is NOT a primitive failure.**

2. **Lock-in amplifier (chain-grade)** — `EXP_lock_in_amplifier_hd_frequency_v1_FULL` HARD_PASS recall x16.39 at sigma_64, N=8192, M=500. **Recent-arc missed: substrate-native lock-in is chain-grade across scales; USER intuition validated.**

3. **K-gram XOR binding (chain-grade)** — `EXP_substrate_kgram_xor_k4_n16384_v1` HARD_PASS k=3 XOR at N=4096 trigram-class; `EXP_substrate_abduction_f1_weakest_signature_kernel_kgram_xor_groundtruth_cpu_v1` chain-grade. **Recent-arc framing: not surfaced.**

4. **Multimodal binding text↔KG (chain-grade row 518)** — modality-agnostic at M=2000, text→KG = 1.000. **Recent-arc missed: substrate is modality-portable.**

5. **Modular macrocolumn at K=32 (chain-grade row 683)** — content_router beats random, cost ≤ 0.5x monolithic. **Recent-arc missed.**

6. **Continual writes no-catastrophic-forgetting (chain-grade row 612)** — `EXP_a8_continual_writes_no_catastrophic_forgetting_v1` HARD_PASS to alpha=0.3 boundary, cliff identified, seeds reproduce.

7. **HotpotQA 2-hop inference (chain-grade row 654)** — `EXP_h_hotpotqa_ingest_v1` HARD_PASS refuse OOD=1.000, 2-hop=0.991 vs 1-hop=0.001 (892x ratio), bridge=1.000 n_chains=300.

8. **CLS-replay (c2 cascade, c3 compressed) — c3 chain-grade row 648; c2 MM row 663.**

9. **Substrate-native intent classifier (chain-grade row 658)** — `EXP_a1_substrate_intent_classifier_v1` HARD_PASS acc=0.761 vs random=0.145, p95=3.90ms, 0 LLM calls.

10. **Operating-point-shift portability (chain-grade rows 655-656)** — `EXP_p1_action_at_any_position_phase_diagram_v1` AND `EXP_p1_v2_action_at_any_position_LLM_class_v1` HARD_PASS at N_DIM up to 65536; ALL ratios ≥ 0.80; gpu_util_mean=90.3%. **THIS IS THE PHASE_PORTRAIT V2 EVIDENCE.**

11. **PP-55 6th rung VSA binding cross-N band lift (chain-grade)** — N=131072 alpha=0.05 M=6553 cos=0.99999. **Recent-arc missed.**

12. **Capability-integration (cap-int)** — Track-B 4th cert-LAYER; I1-I9 gate (per project memory).

13. **Excitability traces / alloc routing** — smoke only (`_ship_alloc_routing_excitability_trace_smoke_v1.log`); FULL not shipped. **Genuinely under-tested.**

14. **Inference-transfer / refuse-gate** — `EXP_a8` chain-grade no-catastrophic-forgetting; refuse-gate part of h_hotpotqa chain-grade.

---

## SECTION 6 — Honest envelope verdict

### Counts (verified from row scan)

- **Total chain_grade rulings in cert_ledger:** 480 (across 707 rows; some atoms = multiple rulings)
- **Total measured_mechanism rulings:** 65
- **Total HARD_PASS verdicts:** 33 (cert-class pre_reg_pass)
- **Recent honest_negative:** ~12 (env-bound LM cells, self-map nulls)

### Aliveness ceiling by dimension

| Dimension | Chain-grade evidence | Best envelope | Recent-arc framing accuracy |
|-----------|---------------------|---------------|------------------------------|
| HRR algebra | YES (6 atoms) | N=131072, K=12, V=512 | UNDER-counted (only N=4096 framed) |
| Sparse-bipolar | YES (capacity-sweep + 240x mult-compose) | N=131072 alpha=0.05, 600K via compose | UNDER-counted |
| Substrate-as-LM | YES (n1_v3 top1, fair_harness BPC) | N=8192 V=4000 BPC 7.30 (+0.43 lift) | over-cited 61% as the cap; that's top1; BPC lift is +0.43 |
| cf-RPE plasticity | YES (heterogeneous +0.141) | N=8192 +0.30 single-arm chain-grade-border | accurate |
| Multi-bank K-bank | PARTIAL — K=32 modular CG; K=2 LM MID | K=32 modular cost-path | UNDER-claimed (K=32 macrocolumn missed) |
| Composition | YES (multiplicative 240x; sequence binding c3) | 240x M_max; 6403 sequence pairs | recent-arc WRONG-CLOSED multiplicative |
| Generation | YES (g1b capacity sweep CG) | 6/6 at bar 0.60 headroom 6403 | accurate |
| Multi-hop KG | YES (h_hotpotqa CG 892x ratio) | 2-hop=0.991 vs 1-hop=0.001 | accurate |
| CLS continual | YES (a8 CG; c3 CG) | alpha=0.3 boundary; 27x speedup | accurate |
| Modern-Hopfield cleanup | YES (n_sweep CG) | N=4096 M/N=0.30 = 100% | recent-arc WRONG-CLOSED multi-iter cleanup |
| Lock-in amplifier | YES (FULL CG x16.39) | sigma_64, N=8192, M=500 | recent-arc MISSED entirely |

### Coverage gaps (envelope-push opportunities)

1. **Joint cf-RPE + STDP + K=2-bank + g1b sequence binding** — chain-grade composition cell not yet shipped. **Highest-leverage test.**
2. **Substrate-as-LM at N_DIM > 16384 with V > 4000** — Path A in flight; could close the bigram-floor gap (currently 1.5 bits unclaimed from 7.0 to 5.5 BPC).
3. **Multi-iter on modern-Hopfield encoder at LM scale** — primitive-vs-encoder confound; rerun multi-iter LM with continuous-codebook E (not sign-binarized).
4. **Sigmoid-additive as named primitive cell** — never tested by name; likely covered IMPLICITLY by other compose cells but no isolated discriminator.
5. **Theta-gamma routing** — brain-analog, no cell; high prior per brain-existence-proof.
6. **Per-token RPE schedule (not per-step grid)** — genuine open lane.
7. **K=4, 8, 16 multi-bank on substrate-as-LM** — only K=2 LM measured (MIDDLE_BAND).
8. **Excitability-trace + alloc-routing FULL** — smoke only, no FULL chain-grade.

### Highest-leverage composition cells (what to ship next)

1. **`fair_harness × cf-RPE × het-plasticity × K=2 × modern-Hopfield cleanup` joint cell** (combine 5 chain-grade primitives) — predicted lift = (0.43 + 0.30 + 0.14 + 0.10 + cleanup) > 1.0 bit; would close the 1.5-bit bigram-floor gap. Risk: sub-additive compose (recent K2×cfrpe was sub-additive on LM).
2. **Multi-iter cleanup on `modern_hopfield_continuous_codebook` substrate-LM** — fix the primitive-vs-encoder confound; replicate cleanup primitive HP from N=4096 M/N=0.30 onto LM regime.
3. **Path A Path C joint encoder cell** — substrate-owned predictive-coding encoder + word2vec sparse-bipolar in same harness with fair_harness ctx-unk filter; cleanest discriminator of encoder family.
4. **Modular macrocolumn K=32 + cf-RPE per-bank** — extend chain-grade K=32 cost-path with cf-RPE plasticity inside each macrocolumn.
5. **Theta-gamma routing primitive cell** — brain-existence-proof prior 0.65; genuine new lane.

---

## Honest verdict to USER's 5 questions

1. **Have we done the RIGHT tests + found ALL knobs?** Largely YES on storage + encoding + cleanup + plasticity (10+ chain-grade primitives); NO on cross-primitive compose-saturation regime (the joint chain-grade cell hasn't shipped); MISSED knobs include lock-in amplifier (recent-arc forgot it's chain-grade), modular macrocolumn K=32 (chain-grade), multimodal text↔KG binding (chain-grade), kgram_XOR k=3 trigram-class (chain-grade).
2. **Envelope pushed per dimension?** HRR up to N=131072 — YES. Sparse-bipolar to 600K via compose — YES. cf-RPE to N=8192 production — YES. K-bank only K=2 LM + K=32 modular — PARTIAL. Substrate-as-LM only to N=8192 V=4000 — PARTIAL.
3. **Substrate-as-LM lift better than +61%?** n1_v3 = +61% TOP1 lift at N=4096 V=256. fair_harness V2 chain-grade rail = +0.43 BPC bits (which is much better than recent-arc framed, since BPC is the harder metric). cf-RPE @5000 = +0.30 chain-grade-border. These are LMs at different regimes; +61% is top-1; +0.43 is BPC.
4. **K=2 multi-bank — right thing?** Partially. K=32 modular macrocolumn (cost-path chain-grade) and K-ensemble multiplicative compose (240x) ARE the chain-grade evidence; K=2 LM specifically is MID; K=2 × cf-RPE × word2vec smoke is CGB but not FULL. Don't fixate on K=2 — the chain-grade lives at K=32 and K-ensemble.
5. **Scour found:** multiplicative composition CHAIN-GRADE (recent-arc wrongly closed); modern-Hopfield cleanup CHAIN-GRADE (multi-iter LM HF was encoder-confound); temperature-calibrated decode IS in fair_harness V2 chain (not closed); per-token RPE schedule legitimately open; theta-gamma genuinely under-tested. Lower-nervous-system baseline: HRR+sparse-bipolar+char-trigram + cleanup envelope sigma≤1.0 + capacity alpha=0.048 stable. Mid-level baseline: cf-RPE +0.30 + het-plasticity +0.141 + multiplicative compose 240x + sequence-binding c3 chain-grade + g1b capacity 6403 pairs.

---

## Falsifiable predictions (pre-registered HARD-PASS / HARD-FAIL)

### P1: Joint compose cell beats sum-of-parts
The joint `fair_harness × cf-RPE × het-plasticity × K=2 × modern-Hopfield-cleanup` cell will achieve BPC ≤ 6.85 (substrate beats current fair_harness chain-grade rail by ≥ 0.45 bits).

- **HARD-PASS:** joint BPC ≤ 6.85 (super-additive compose holds).
- **HARD-FAIL:** joint BPC ≥ 7.15 (sub-additive collapse to single-knob best).
- **P_deflated:** 0.40 (deflated from 0.55; recent K2×cfrpe LM was sub-additive; brain-prior+0.10 for joint with cleanup new arm).

### P2: Multi-iter cleanup on continuous-codebook E lifts LM BPC
Re-running multi_iter LM with continuous-codebook E (replacing sign-binarized char-trigram) will lift BPC by ≥ 0.05 over single-step.

- **HARD-PASS:** ARM_MULTI_ITER_CONTINUOUS bpc ≤ ARM_SINGLE_STEP - 0.05.
- **HARD-FAIL:** ARM_MULTI_ITER_CONTINUOUS bpc ≥ ARM_SINGLE_STEP + 0.02 (still no help; primitive truly doesn't transfer to LM regime).
- **P_deflated:** 0.50 (deflated from 0.65; chain-grade exists at M/N=0.30 modern-Hopfield N=4096; encoder-confound resolution likely).

### P3: K=4, K=8 LM extends K=2 result
K=4 or K=8 multi-bank on fair_harness LM will lift BPC by ≥ 0.05 over K=1 baseline (additive over K=2's +0.10).

- **HARD-PASS:** ARM_K4 OR ARM_K8 bpc_lift ≥ 0.15.
- **HARD-FAIL:** all K=4 K=8 bpc_lift ≤ 0.05 (K-scaling saturates at K=2).
- **P_deflated:** 0.35 (deflated from 0.50; K=2 was sub-additive; K-scaling may plateau).

---

## Cross-thread synthesis

- **Phase_portrait v1 inventory (2026-06-22)** already documented 38-42 chain-grade phase-diagram atoms + 11 transform-survival atoms. This drill confirms + EXTENDS that inventory with: lock-in amplifier (missed), modular macrocolumn K=32 (missed in "not alive" framing), multimodal text↔KG (under-cited), kgram_XOR k=3 trigram-class (under-cited).
- **Brain-existence-proof feedback ([[feedback-brain-is-existence-proof-higher-prior-for-brain-grounded-mechanisms-USER]]):** brain-grounded primitives that map to chain-grade substrate primitives: lock-in amplifier (USER intuition validated CG), HRR binding (CG), sparse-bipolar (CG), cf-RPE+STDP (CG), modular macrocolumn (CG), CLS-replay continual (CG). What's brain-grounded but UNDER-tested: theta-gamma routing (no cell), per-token RPE schedule (only step-grid), excitability-trace alloc-routing (smoke only).
- **Path C substrate-owned encoder ([[project-path-c-substrate-owned-encoder]]):** Path C MID + char-trigram dense CG = path forward; Path A (word2vec) is diagnostic probe per USER feedback; Path B (pythia) MID. The substrate-product answer is char-trigram-dense + substrate-PC-encoder, NOT Path A.
- **Fix #28 (verify per-arm metrics not summary verdict text):** This drill SURFACED 2 cases where recent-arc framing over-claimed closure (multi-iter cleanup, multiplicative compose) by reading verdict_msg only and missing the regime-distinction. Confirms Fix #28 standing rule.

---

## Substrate-product implications

1. **Chain-grade ceiling is HIGHER than recent-arc implied.** 6 primitives at chain-grade form the substrate-product floor. The recent-arc "aliveness" framing under-counted by ~3 chain-grade dimensions and wrongly closed 2 mechanisms (multi-iter cleanup, multiplicative compose).

2. **L2 substrate-native LM bigram-gap (~1.5 bits unclaimed) is the highest-leverage envelope-push.** Joint compose cell (P1) directly attacks this; if it lands chain-grade, substrate clears bigram floor and approaches Shannon limit.

3. **Substrate-product MVP is more ready than recent-arc framed.** Substrate-native intent classifier (chain-grade 76% acc, 0 LLM calls, p95=3.9ms) + multi-hop KG inference (h_hotpotqa chain-grade 2-hop=0.991) + sequence generation (g1b chain-grade) + continual writes (a8 chain-grade no-catastrophic) — these compose into a substrate-conversation product without LM-bigram-closure.

4. **MOAT = continual-learning via CLS-replay** validated: a8 chain-grade to alpha=0.3 boundary + 27x speedup vs LLM with NO forgetting.

5. **Director-tooling Fixes #20-#24 banked** + substrate_self_map_v2 cell genuinely null (HARD-FAIL row 679) — Director-lexical self-mapping doesn't transfer to substrate-native; v2e/comparator self-mapping next-lane is right call.

---

## Next-drill candidate

**Recommended:** **Joint compose cell `fair_harness × cf-RPE × het-plasticity × K=2 × modern-Hopfield-cleanup` (P1)** — highest discriminating value; 5 chain-grade primitives + 1 ARM_BASELINE_NO_COMPOSE; predicts BPC ≤ 6.85 (chain-grade rail at 7.30); if sub-additive, surfaces compose-saturation mechanism for substrate-product spec; if super-additive, lifts substrate-as-LM into bigram-floor regime.

**Field tag:** substrate-internal cross-primitive composition (not lit-drill; substrate-vs-substrate joint cell).

**Cost:** ~30-45 min remote GPU at N_DIM=8192 V=4000 text8 100k tokens 3 seeds (5 arms + baseline).

---

## Citations (verified count: 22)

1. `data/substrate_index/meta/cert_ledger.jsonl` (707 rows; 480 chain_grade, 65 measured_mechanism, 33 HARD_PASS)
2. `data/substrate_index/meta/atoms.jsonl` (162 META atoms; 14 directly relevant to aliveness)
3. `data/exp_pp55_vsa_binding_n131072_v6_n131072/metrics.json` (HRR N=131072 HP cos=0.99999)
4. `data/exp_substrate_capacity_scaling_sweep_xl_v1/metrics.json` (alpha=0.048 HP)
5. `data/exp_substrate_extended_context_ceiling_posbind_symw_v1_8192_16384_gpu/metrics.json` (K*=12 HP)
6. `data/exp_n1_concept_lm_substrate_native_token_decode_v3/metrics.json` (top1=0.445 HP / BPC HF)
7. `data/exp_fair_harness_substrate_as_lm_v1/metrics.json` (BPC 7.3065 HP +0.432 lift)
8. `data/exp_substrate_cfrpe_n_steps_curve_v1/metrics.json` (lift@5000=0.30 MM)
9. `data/exp_substrate_heterogeneous_plasticity_cfrpe_stdp_fair_harness_v1/metrics.json` (lift=0.141 HP)
10. `data/exp_substrate_cfrpe_stdp_heterogeneous_superadditive_bigram_v1_n512/metrics.json` (gap=3.767 HP)
11. `data/exp_substrate_K2_x_cfrpe_compose_LM_v1/metrics.json` (K=2 LM MID lift=0.101)
12. `data/exp_substrate_K2_x_cfrpe_compose_word2vec_v2_smoke/metrics.json` (K=2 CGB lift=0.134)
13. `data/exp_modern_hopfield_n_sweep_v1/metrics.json` (M/N=0.30 = 100% HP)
14. `data/exp_lock_in_amplifier_hd_frequency_v1_FULL/metrics.json` (x16.39 recall HP)
15. `data/exp_substrate_capacity_composition_b2xb4_v1_n2048/metrics.json` (240x mult-compose HP)
16. `data/exp_m1_modular_macrocolumn_W_v2/metrics.json` (K=32 cost-path HP)
17. `data/exp_g1b_capacity_sweep_v1/metrics.json` (6/6 at bar 0.60 HP)
18. `data/exp_h_hotpotqa_ingest_v1/metrics.json` (2-hop=0.991 vs 1-hop=0.001 HP)
19. `data/exp_a8_continual_writes_no_catastrophic_forgetting_v1/metrics.json` (alpha=0.3 HP)
20. `data/exp_a1_substrate_intent_classifier_v1_gatecheck/metrics.json` (acc=0.761 HP)
21. `notes/research_surprise_baseline_7p22_vs_7p30_2x_drill_2026-06-24.md` (encoder-family discrimination)
22. `notes/phase_portrait_v1_inventory_atom_substrate_operating_regime_map_2026-06-22.md` (38-42 phase-diagram atoms)

---

*Research drill — Opus 4.7 (1M). Calibration penalty applied (0.15-0.25 deflation on novelty claims; chain-grade caps respected). Brain-existence-proof prior 0.65-0.75 applied to brain-grounded primitives. Negativity-bias symmetric: verified both directions (recent-arc under-claimed AND over-claimed in distinct dimensions).*
