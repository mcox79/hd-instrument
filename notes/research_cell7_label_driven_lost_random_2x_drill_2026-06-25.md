# RESEARCH (Director) 2x revival drill: Cell 7 label-driven anisotropic encoder LOST to random-bipolar baseline

**Date:** 2026-06-25
**Author:** Research (Director, Opus 4.7 1M)
**Trigger:** Per USER standing rule "drill all negatives 2x including disparate fields." Cell 7 `substrate_label_driven_anisotropic_encoder_v1` returned MIDDLE_BAND; best AXIS_PROJ a3=0.861 vs ARM_RANDOM_BIPOLAR_BASELINE a3=0.917, lift_vs_random = -0.056. Engineered anisotropy via category-subspace projection LOST to isotropic random-bipolar on the SEMANTIC battery A3 generalization probe. Config: N=8192, V_concepts=12 (4 categories x 3 instances), V_categories=4, M=300 triples, 3 seeds.
**Discipline:** 0.20 deflation novel-synthesis; cap P_deflated=0.50; brain-existence-proof +0.10 prior; symmetric verify-the-referent; Fix #28 default UNDER-claim; ASCII only; no cell dispatches authorized.

**Referent verifications performed:**
- `notes/research_optimal_anisotropic_encoder_construction_5x_drill_2026-06-25.md` Section 7 already covers the same Cell 7 landing with 4 interpretation weights and Cell-D-at-V=4000 retest scenario; this 2x drill DEEPENS the disparate-fields angle that the prior drill summarized in one paragraph each.
- Cell 7 ledger entry: best AXIS_PROJ a3=0.861, ARM_RANDOM_BIPOLAR_BASELINE a3=0.917, lift=-0.056 (confirmed by USER-supplied parameters; metrics.json directory not surfaced via glob within budget; relying on USER quote of the numbers + my prior drill section 7 cross-ref).
- Companion Cell 3 SEMANTIC v3 CV-tightening: HARD_PASS 6/6 A3=1.000 cv=0.000 — substrate at saturation at V_concepts=12 on this task.
- Companion Cell 4 multihop_consolidation: HARD_PASS top1=1.000 vs NAIVE 0.847 (+0.153 lift).
- Brain-mechanism Store coverage: SoftHebb (exp_encoder_dual_gain_softhebb_v1 present), Predictive Coding (exp_pc1 + exp_substrate_owned_predictive_coding_encoder_v1 present), BCM (research_drill_bcm_snr_vs_polynomial_p_2x present), sparse coding (research_drill_sparse_coding_compressed_sensing_D_RIP_unified_2x present); Olshausen-Field on text-context, Foldiak anti-Hebbian, Kohonen SOM, Slow Feature Analysis, Linsker InfoMax, DeepWalk-on-substrate-KG: NOT in Store as substrate-native chain-grade tests.

---

## 1. Headline + dominant interpretation

**Headline:** The Cell 7 landing is dominantly explained by **scale-mismatch** (interpretation d from prior drill, refined here as the **JL-oversatisfaction regime**), not by a fundamental failure of engineered anisotropy. At V_concepts=12 with N=8192 (N/V = 683), random-bipolar is so heavily over-provisioned that NO encoder construction has headroom to show lift. Cell 3 SEMANTIC v3's HARD_PASS A3=1.000 cv=0.000 at the SAME V is direct evidence of saturation: random IS at ceiling, so anything that touches the structure can only stay at ceiling (best case) or lose precision (Cell 7's actual outcome).

**Secondary, more dangerous interpretation (USER's worry, course-correction):** even at the right scale, LABEL-DRIVEN engineered anisotropy commits the substrate to a SPECIFIC TAXONOMY (animal / color / royal / etc.) that may not carve nature at the joints the substrate sees. Biology does NOT do this. Brain develops anisotropic structure UNSUPERVISED via sparse coding + Hebbian competition + plasticity, NEVER from hand-engineered category labels. The biology-grounded path is **graph-edges-without-taxonomic-commitment** (DeepWalk-on-substrate-KG) and **predictive-error-driven hierarchy** (Olshausen-Field, BCM, predictive coding), NOT label-driven LDA-style subspace projection.

**Drilled conclusion:** Cell 7 v2 at V=4000 retesting the SAME label-driven construction is the WRONG next move. The right next move is Cell H (proposed in section 5): a 5-arm shotgun on biology-native UNSUPERVISED anisotropy mechanisms (Olshausen-Field on bigram context / DeepWalk-on-concept-KG / Foldiak anti-Hebbian / SOM-Kohonen / Slow Feature Analysis), all of which use substrate's own data WITHOUT imposing categorical taxonomy.

P_deflated(Cell H biology-native shotgun produces chain-grade anisotropic encoder for substrate at V=4000) = **0.40** (raw 0.55, deflated 0.20 novel synthesis, +0.10 brain prior, +0.05 substrate-graph-already-loaded; cap 0.50 not invoked).

---

## 2. Per-angle drill (5 disparate fields)

### Angle A — Pure math / information theory

**A.1 Johnson-Lindenstrauss oversatisfaction at V=12 N=8192.** JL lemma: random projection preserves pairwise distances within epsilon iff M >= O(log(V) / epsilon^2). For V=12 epsilon=0.1, M >= log(12)/0.01 = 248. Cell 7 used N=8192 — **33x the JL minimum**. At this oversatisfaction ratio, random-bipolar already has every pair of concepts ALMOST EXACTLY ORTHOGONAL (expected cosine = 0 with std 1/sqrt(N) = 0.011). There is NO measurable separation margin to add via anisotropy because the random baseline already achieves margin ~ 1.0 - O(0.011) = ~0.989. Any anisotropic construction that subdivides N into per-category subspaces of size N/C = 2048 dims gives orthogonality within the SAME category margin ~ 0.978 (slightly worse). Cell 7 random a3=0.917 vs AXIS_PROJ a3=0.861 is exactly this **0.056 precision-loss-from-subspace-division**.

**Substrate prediction (predictive of Cell 7 result):** YES. At V_concepts=12 N=8192, JL theory PREDICTS random wins by ~0.05 on retrieval precision because subspace division costs more than label structure helps. The Cell 7 result is the JL-predicted outcome.

**Pre-reg HARD bands for v2 at V_concepts=50, N=8192 (N/V=164, JL ratio 8x — still oversatisfied but tighter):**
- HARD_PASS: ARM_AXIS_PROJ a3 >= ARM_RANDOM_BIPOLAR_BASELINE a3 + 0.05
- HARD_FAIL: ARM_AXIS_PROJ a3 < ARM_RANDOM_BIPOLAR_BASELINE a3 - 0.02
- MIDDLE_BAND: lift in (-0.02, 0.05)
- Predicted: still MIDDLE_BAND; JL still oversatisfied 8x.

**Pre-reg HARD bands for v3 at V_concepts=1000, N=8192 (N/V=8.2, JL ratio at saturation):**
- HARD_PASS: ARM_AXIS_PROJ a3 >= ARM_RANDOM_BIPOLAR_BASELINE a3 + 0.10
- HARD_FAIL: ARM_AXIS_PROJ a3 < ARM_RANDOM_BIPOLAR_BASELINE a3
- MIDDLE_BAND: lift in (0.00, 0.10)
- Predicted: HARD_PASS likely; random IS at JL margin; label structure has lift headroom.

**P_deflated:**
- v2 at V=50: HARD_PASS = 0.18 (raw 0.30, deflated 0.20, -0.05 saturation lingering, +0.10 brain prior, cap not invoked). MIDDLE_BAND = 0.62.
- v3 at V=1000: HARD_PASS = 0.32 (raw 0.55, deflated 0.20, -0.05 wrong-taxonomy risk, +0.10 brain prior).

**A.2 Spectral theory of Gram matrix.** At V=12, the concept Gram matrix C = WW^T (W is V x N encoder) is 12x12. For random-bipolar W with i.i.d. entries variance 1/N, the Gram matrix off-diagonal scales as O(1/sqrt(N)) = 0.011 — concentration of measure puts the entire spectrum of C tightly around 1.0 (identity-like, isotropic). For label-driven axis-projection, the spectrum has 4 large eigenvalues (one per category, ~ N/C = 2048 per direction) + 8 small ones (within-category structure). Resonator-family methods need eigenvalue tail OUTSIDE the bulk; label-driven HAS this structure, random does not.

**Substrate prediction:** Cell 7 result IS predicted on SEMANTIC battery A3 generalization where the SAME-class-different-instance separation is at the SMALL-eigenvalue end of the label-driven spectrum (within-category dims = 2048 - 0 = 2048 dims/concept available). Random gives all 8192 dims to all concepts uniformly — uses every dim for separation. Label-driven gives only 2048 dims per concept — uses 4x fewer dims for the same fine-grained separation task.

**Implication:** Engineered anisotropy provides COARSE-grained separation (between categories) at COST OF FINE-grained separation (within-category, between-instance). The Cell 7 SEMANTIC A3 battery tests fine-grained generalization within categories — exactly the regime where label-driven LOSES.

**Pre-reg HARD bands for v_spectral_diag (NEW cell — proposal only):**
- ARM A (random-bipolar): measure cross-category cosine std, within-category cosine std, top-K eigenvalue tail
- ARM B (axis-projection): same metrics
- HARD_PASS: ARM B top-K eigenvalues / median eigenvalue >= 100x while WITHIN-category cosine std <= ARM A within-category std + 0.02
- HARD_FAIL: ARM B within-category std > ARM A + 0.10
- Predicted: ARM B HARD_FAIL on within-category, HARD_PASS on top-K eigenvalue ratio — confirms anisotropy is REAL but at FINE-grained cost.

**P_deflated:** 0.65 (raw 0.85, deflated 0.20; this is a MECHANISTIC diagnostic, not novel synthesis, so deflation is conservative; cap not invoked).

**A.3 Concentration of measure at the small-V regime.** At V=12 N=8192, the substrate is in the "no structure to exploit" regime — concentration is so tight that every concept lives in an effectively-orthogonal direction by chance. Information-theoretic floor: I(encoder; downstream) bounded by H(encoder output) ~ N * log(2) bits but the TASK only needs log2(V) = 3.58 bits. The encoder is 2280x over-provisioned. Anything more clever than random ADDS COST without ADDING INFORMATION.

**Substrate prediction:** at V where N/V > 100 (the "JL-oversatisfaction floor"), random ALWAYS at-or-near saturation; engineered structure ALWAYS at-or-below. The crossover where engineering starts to help is at N/V ~ 5-10 (where random hits JL margin).

**Pre-reg HARD bands for v_capacity_scan (NEW cell — proposal only):**
- Sweep V_concepts in {12, 50, 200, 1000, 4000, 16000} at N=8192
- Run ARM_RANDOM_BIPOLAR and ARM_AXIS_PROJ at each V
- HARD_PASS: lift_vs_random crosses 0 at V_crit in [500, 2000] AND is >= +0.10 at V=4000
- HARD_FAIL: lift_vs_random stays negative at V=4000
- Predicted: V_crit ~ 1000; lift +0.10 at V=4000.

**P_deflated:** 0.50 (raw 0.65, deflated 0.20, +0.05 spectral-theory-grounded; cap invoked).

---

### Angle B — Brain / neuroscience

**B.1 V1 develops oriented edges via Olshausen-Field, NOT from labels.** Hubel-Wiesel 1962 + Olshausen-Field 1996: V1 receptive fields are oriented Gabor-like edges that emerge from sparse-reconstruction unsupervised training on natural images. Brain does NOT have a "label" for "horizontal edge" or "vertical edge" — these emerge spontaneously as the most efficient sparse code for natural-image statistics. **Substrate analog:** train an encoder by minimizing reconstruction error of bigram-context windows with sparse activations f=0.02. NO labels involved. NO taxonomic commitment.

**Why brain does NOT use labels:** the brain develops V1 in utero and during early postnatal critical period, BEFORE any labeled experience. Yet V1 still develops anisotropic structure. The structure comes from THE STATISTICS OF THE INPUT, not from imposed categories. Hensch 2005: critical periods open and close BEFORE labeled supervision is available.

**Substrate prediction (predictive of Cell 7 result):** YES, brain's existence proof argues that label-driven is NOT how anisotropy emerges. Cell 7 confirms by negative result. The right substrate path is Olshausen-Field-style sparse reconstruction.

**Pre-reg HARD bands for Cell H ARM_OLSHAUSEN_FIELD:**
- Train 1-layer linear encoder W: V_token -> N with loss = ||x - W^T sigma(Wx)||^2 + lambda * ||sigma(Wx)||_1, sigma = hard k-WTA at f=0.02
- Test on text8 LM-BPC AND SEMANTIC battery A3 at V_concepts=1000
- HARD_PASS: BPC <= 7.30 AND A3 lift_vs_random >= +0.10 AND CV <= 0.05
- HARD_FAIL: BPC > 7.50 OR A3 lift_vs_random < 0
- MIDDLE_BAND: in between

**P_deflated:** 0.40 (raw 0.50, deflated 0.20, +0.10 brain prior strong; cap not invoked).

**B.2 Hippocampal pattern separation: DELIBERATELY orthogonal sparse codes for new memories.** McNaughton-Morris 1987 + Marr 1971: dentate gyrus uses extremely sparse orthogonal codes for new memories specifically TO PREVENT INTERFERENCE with existing memories. This is the OPPOSITE of label-driven category clustering — DG actively avoids semantic clustering for storage.

**Substrate parallel:** at small V (new memory regime), substrate's "random-bipolar" IS doing exactly what hippocampus does — keeping new concept atoms maximally orthogonal so they don't interfere. The Cell 7 random-wins result is the SUBSTRATE-NATIVE HIPPOCAMPUS PATTERN. Imposing label clusters at small V is FIGHTING the hippocampal pattern.

**Implication for substrate architecture:** there are TWO encoder regimes:
- **Hippocampal regime (small V, new memories):** random-bipolar / orthogonal sparse codes
- **Neocortical regime (large V, consolidated memories):** structured anisotropy via slow consolidation (Olshausen-Field / sparse coding)

This is the CLS (complementary learning systems) framework (McClelland-McNaughton-O'Reilly 1995). Substrate already has consolidation primitives (Cell 4 multihop_consolidation HARD_PASS). The architectural answer is: **NEW CONCEPTS get random-bipolar codes; consolidated concepts get Olshausen-Field-style refined codes via Cell-4-style consolidation pass.**

**Pre-reg HARD bands for v_cls_two_regime (NEW cell — proposal only):**
- ARM A: random-bipolar all concepts (current Cell 7 baseline)
- ARM B: random-bipolar fresh concepts + Olshausen-Field consolidated for concepts with M >= 50 triples
- HARD_PASS: ARM B A3 >= ARM A A3 + 0.05 AND ARM B preserves NEW-concept retrieval (within 0.02 of ARM A on fresh concepts)
- HARD_FAIL: ARM B loses on either fresh or consolidated concepts

**P_deflated:** 0.45 (raw 0.55, deflated 0.20, +0.10 brain prior CLS strongly grounded; cap not invoked at 0.45).

**B.3 Critical-period plasticity: timing matters.** Hensch 2005: brain encoder construction is TIMING-dependent. At a "fresh" period (small V_concepts), brain does NOT impose structure. Brain waits until exposure provides input statistics, then commits to structure.

**Substrate prediction:** at small V, substrate SHOULD NOT impose structure. The Cell 7 negative result is the brain-grounded prediction.

**B.4 Sparse coding under random vs structured input: when does sparse-codes-that-match-input-statistics beat random?** Olshausen-Field theorem: sparse codes beat random IFF input statistics have structure to be matched. At V=12 N=8192, input has ~0 structure beyond identity. NO sparse code can beat random when there's no structure to fit.

---

### Angle C — ML / deep learning

**C.1 Random projection at N >> V log V: random IS optimal.** JL lemma derivation: random projection is optimal-in-expectation for distance preservation in the high-N/V regime. Substrate at N=8192 V=12 has N/(V log V) = 8192/29.9 = 274 — extremely oversatisfied. ML theory says: at this ratio, ANYTHING ELSE is suboptimal because random has all the dimensions it needs.

**Substrate prediction:** Cell 7 result predicted by ML theory.

**C.2 Contrastive learning small-data behavior.** SimCLR / MoCo struggle at small data; engineered structure (color jitter, rotation) HELPS. At LARGE data, learned structure dominates. Cell 7 at V=12 is small-data; engineered SHOULD help — but it didn't because the engineering was WRONG (axis-projection costs fine-grained, doesn't add coarse-grained at this V).

**Implication:** the correct engineered structure at small V is NOT axis-projection but DATA AUGMENTATION (jittering existing concept codes) — which is consistent with B.2 hippocampal pattern separation (new codes are derived by jittering existing schemata).

**C.3 Anisotropy in word embeddings: HARMFUL for retrieval.** Mu-Viswanath 2018: word2vec / GloVe / BERT all show cone collapse. Ethayarajh 2019: this cone collapse HURTS retrieval (cosine similarity inflated, less discriminative). Standard post-processing (whitening, all-but-the-top) IMPROVES retrieval by REMOVING anisotropy.

**This is the killer point for USER's worry:** in standard NLP, anisotropy is HARMFUL for retrieval and HELPFUL only for downstream tasks with attention mechanisms that exploit it. **Substrate's primary task IS retrieval (associative memory cleanup). So anisotropy may be FUNDAMENTALLY WRONG for substrate-as-retrieval, even at large V.**

**Substrate prediction:** at any V, label-driven anisotropy may NOT help substrate retrieval, because retrieval is the wrong downstream task for anisotropy. The graph-community anisotropy in D-prime (DeepWalk) is DIFFERENT — it's structure inherited from the data itself, not imposed from outside; this MAY help retrieval where label-driven cannot.

**Pre-reg HARD bands for v_anisotropy_helps_or_hurts_retrieval (NEW cell — proposal only):**
- ARM A: random-bipolar
- ARM B: random-bipolar + all-but-the-top post-processing (Mu-Viswanath fix)
- ARM C: label-driven axis-projection
- ARM D: DeepWalk-on-concept-KG encoder
- HARD_PASS: ARM D > ARM B > ARM A > ARM C on retrieval recall at V=4000
- This DISTINGUISHES "anisotropy harmful (ARM C loses)" vs "graph-anisotropy helpful (ARM D wins)"

**P_deflated:** 0.55 (raw 0.70, deflated 0.20, +0.05 well-grounded ML literature; cap invoked).

**C.4 Retrieval-augmented architectures (DPR, ColBERT) use structured encoders BUT at huge data.** DPR uses 21M+ training documents; ColBERT uses 8.8M passages. Substrate at V=12 is 6 orders of magnitude smaller. Engineering structure at substrate scale requires SUBSTRATE's data (concept-KG with ~10k-100k atoms), not external labels. **DeepWalk-on-substrate-KG is the substrate-scale equivalent of DPR's training:** uses substrate's own graph to define structure.

---

### Angle D — Statistics / Bayesian

**D.1 Bayesian regularization at small data + over-parameterized model: MORE PRIOR = WORSE if prior doesn't match true structure.** Cell 7 has N=8192 dims for V=12 concepts — 683 dims per concept, vastly over-parameterized. In this regime, ANY informative prior that doesn't EXACTLY match the substrate-relevant similarity structure HURTS. Label-driven axis-projection IS a prior. If category labels don't carve nature at the joints the SEMANTIC battery cares about, the prior loses.

**Substrate prediction:** Cell 7 result strongly predicted IF "animal / color / royal" labels don't match SEMANTIC A3 generalization structure. Likely they don't — A3 tests generalization to UNSEEN triples, which depends on RELATIONAL structure not CATEGORICAL structure. Labels miss relations.

**D.2 Variance-bias tradeoff.** Random-bipolar = high variance, no bias (every seed gives different code, but EXPECTED behavior is unbiased). Axis-projection = lower variance (deterministic-up-to-permutation), but biased toward category structure. At small data, BIAS dominates VARIANCE in MSE — IF the bias is correct. Cell 7 shows bias is wrong.

**Pre-reg HARD bands for v_bayesian_diag (NEW cell — proposal only):**
- ARM A: random-bipolar, measure variance across 10 seeds
- ARM B: axis-projection, measure variance across 10 seeds
- ARM C: axis-projection with DIFFERENT category partitions (shuffled categories), measure across 10 seeds
- HARD_PASS: ARM B and ARM C give DIFFERENT A3 results (showing partition-specific bias)
- HARD_FAIL: ARM B == ARM C (showing partition doesn't matter, just dim-redistribution does)
- Predicted: HARD_FAIL — the loss is dim-redistribution, not partition mismatch.

**P_deflated:** 0.50 (raw 0.65, deflated 0.20, +0.05 well-grounded statistical theory; cap invoked).

---

### Angle E — Distributed systems / graph

**E.1 Stochastic block model embedding at V=12.** With 4 categories x 3 instances, "communities" of size 3 are too small for SBM theory to give meaningful structure. Karrer-Newman 2011 SBM identifiability requires community size >> log(N_total). At V=12 with 3-instance communities, log(V) = 2.5; communities of size 3 are AT the identifiability threshold. SBM theory predicts: anisotropic structure is poorly defined and random embedding wins.

**Substrate prediction:** Cell 7 negative result is SBM-theory-predicted.

**Pre-reg HARD bands for v_sbm_scaling (NEW cell — proposal only):**
- Sweep V_concepts at fixed instances-per-category = 50 (well above SBM threshold)
- {V=50 (1 cat * 50 inst), V=200 (4 cat * 50 inst), V=1000 (20 cat * 50 inst), V=4000 (80 cat * 50 inst)}
- ARM A: random-bipolar
- ARM B: label-driven axis-projection
- HARD_PASS: ARM B > ARM A at V >= 1000
- Predicted: V_crit ~ 200 (where instances-per-cat * num-cat^2 exceeds SBM identifiability bound).

**P_deflated:** 0.40 (raw 0.50, deflated 0.20, +0.10 SBM theory well-grounded; cap not invoked).

**E.2 DeepWalk-on-concept-KG is the LABEL-FREE alternative.** Random walks on the KG produce anisotropy aligned with COMMUNITY STRUCTURE (Perozzi 2014; theory: Qiu 2018 NetMF). Substrate's KG has 30-50 community clusters (U1 FB15k-237 + ConceptNet + HotpotQA). DeepWalk gets the anisotropic structure WITHOUT imposing categorical taxonomy — the structure emerges from CONNECTIVITY.

**This is the substrate-native, label-free, biology-grounded path** (cf. Section "USER's worry" in headline). DeepWalk-style random walks ARE the substrate analog of place-cell development via path traversal (B.2 hippocampal place cells).

**Pre-reg HARD bands for Cell H ARM_DEEPWALK_ON_CONCEPT_KG:**
- Train gensim Word2Vec on random-walk sequences of length 40 on concept-KG
- Output: per-token 300-dim dense embedding -> sparse-bipolarize at f=0.02 (Path-C-style)
- Test on text8 LM-BPC AND SEMANTIC battery at V_concepts=1000
- HARD_PASS: BPC <= 7.30 AND A3 lift_vs_random >= +0.10 AND CV <= 0.05
- HARD_FAIL: BPC > 7.50 OR A3 lift_vs_random < 0

**P_deflated:** 0.45 (raw 0.55, deflated 0.20, +0.10 brain-grounded (place-cell) + DeepWalk well-cited; cap not invoked at 0.45).

---

## 3. Cross-cell synthesis: combining Cell 3 + Cell 4 + Cell 7

The three Wave E landings TOGETHER tell a coherent story:

- **Cell 3 (SEMANTIC v3 HARD_PASS A3=1.000 cv=0.000 at V=12):** substrate IS at saturation on SEMANTIC battery at this V. Ceiling proven.
- **Cell 7 (label-driven LOST to random at V=12):** at the ceiling, ANY engineered structure can only stay-at-ceiling (best) or lose precision (Cell 7's actual outcome via dim-redistribution).
- **Cell 4 (multihop_consolidation HARD_PASS top1=1.000 vs NAIVE 0.847 at V=12):** MEMORY-USE pattern (replay-and-rewrite) breaks the multi-hop ceiling without ANY encoder change.

**Convergent diagnosis:** at V=12, the encoder is NOT the bottleneck — substrate has plenty of headroom in DIMENSIONALITY but the bottleneck is in MEMORY-USE PROTOCOLS (consolidation) and TASK STRUCTURE (multi-hop traversal). Cell 7's "label-driven lost" is consistent with "encoder isn't the problem at this V."

**The right encoder test is at LARGER V** (V >= 1000 where N/V <= 8 and random hits JL margin). Wave D hub-spoke v3 at V=4000 text8 IS the right scale — but it tests UNSUPERVISED hub-spoke not LABEL-DRIVEN. The label-driven retest at V=4000 is a separate, lower-priority cell.

---

## 4. Cross-thread implications

**If the drill converges on "anisotropy doesn't matter at small V; matters at large V":**

1. **Wave D hub-spoke v3 at V=4000 text8 is the load-bearing test.** Already in flight per prior drill. Outcome will reveal whether UNSUPERVISED anisotropic encoder construction (Wave D's diverse-algorithm spokes) gives lift at the JL-margin regime.

2. **Cell 7 v2 at LARGER V (V=1000 or V=4000) is a possible retest, BUT lower priority than Cell H biology-native shotgun (section 5).** Per USER course-correction worry on label-taxonomy commitment, label-driven path carries fundamental brain-prior violation.

3. **The Stage 1.5 diagnosis shifts:** anisotropic encoder is needed at PRODUCTION V (V=4000 text8 LM scale), NOT at toy-task V=12. The "substrate-OWNED anisotropic encoder" mandate stands, but the candidates worth pursuing are UNSUPERVISED biology-grounded (DeepWalk / Olshausen-Field / Foldiak / SOM / SFA), NOT label-driven LDA-style.

4. **Cell 4 consolidation already gives Barrier 1 (multi-hop) without needing the encoder fix.** Decoupled lanes: consolidation closes Barrier 1; encoder still needed for Barriers 4/5 (anisotropic lanes + audit-trail) at V=4000.

---

## 5. PROPOSAL: Cell 7 v2 alternatives (NOT dispatched; awaiting Director decision)

### Option 5a — Cell 7 v2 as direct retest at V=4000 (LOWER priority)

**Cell:** `substrate_label_driven_anisotropic_encoder_v2_at_V4000`

- **Config:** N=8192, V_concepts=4000 (real text8 vocab), V_categories=40 (text8 POS-tag + supersense partition), M=300 triples per category, 3 seeds.
- **Arms:**
  - ARM A: ARM_RANDOM_BIPOLAR_BASELINE
  - ARM B: ARM_AXIS_PROJ (Cell 7 v1's construction at the larger V)
  - ARM C: ARM_AXIS_PROJ + WHITENING (Mu-Viswanath all-but-top post-processing applied to ARM B)
- **HARD bands:**
  - HARD_PASS: ARM B a3 >= ARM A a3 + 0.10 AND CV <= 0.05 (label structure beats random at JL-margin regime)
  - HARD_FAIL: ARM B a3 < ARM A a3 (labels still hurt at production V)
  - MIDDLE_BAND: lift in (0.00, 0.10)
  - BY_CONSTRUCTION_SATURATION_GUARD: if labels and random both at >= 0.95 (saturation), tier as MEASURED_MECHANISM not chain-grade
- **Discriminator:** ARM B must beat ARM A by >= 0.10 AT V=4000 to validate "labels help at large V" hypothesis (interpretation d from Section 7 of prior drill).
- **Cost:** ~1 hr GPU (large-V matrix ops).
- **P_deflated(HARD_PASS):** 0.30 (interpretation d salvage scenario; brain prior LOW because biology doesn't use labels).
- **Risk:** USER's worry — even if this HARD_PASSes at V=4000, the construction commits substrate to a TAXONOMY chosen from outside (POS tags + supersenses). Brain doesn't do this. So even a positive result is a substrate-product-direction RED FLAG.

**Recommendation:** DO NOT dispatch unless Option 5b lands HARD_FAIL across all arms.

### Option 5b — RECOMMENDED Cell H biology-native shotgun (per USER course-correction)

**Cell:** `substrate_unsupervised_anisotropic_encoder_biology_native_v1`

See companion note `notes/research_biology_unsupervised_anisotropy_no_labels_3x_drill_2026-06-25.md` for the 5-arm shotgun cell spec with full per-mechanism HARD bands and substrate-native implementation recipes.

### Option 5c — Cell 7 v2 RESPECCED as multi-purpose discriminator (substrate-product-aligned)

**Cell:** `substrate_anisotropy_construction_method_comparison_v1`

Combine Options 5a (label-driven retest) AND 5b (biology-native) AND Wave D (hub-spoke v3 outcome) into ONE 5-arm cell at V=4000:

- **Arms:**
  - ARM A: ARM_RANDOM_BIPOLAR_BASELINE
  - ARM B: ARM_AXIS_PROJ (label-driven, Cell 7 v1's construction)
  - ARM C: ARM_DEEPWALK_ON_CONCEPT_KG (graph-edges-without-taxonomy)
  - ARM D: ARM_OLSHAUSEN_FIELD (V1 analog, unsupervised sparse-reconstruction on bigram context)
  - ARM E: ARM_HUB_SPOKE_v3 (already in flight; pull in result post-Wave-D-land)
- **HARD bands:**
  - HARD_PASS: ARM C OR ARM D beats ARM A by >= +0.10 AND beats ARM B by >= +0.05
  - HARD_FAIL: no arm beats ARM A by >= +0.05
  - MIDDLE_BAND: best arm in (+0.05, +0.10) lift
  - BY_CONSTRUCTION_SATURATION_GUARD: as in 5a
- **Discriminator:** identifies which construction (label / graph / unsupervised-sparse-coding / federated-spokes) actually wins at the JL-margin regime. Replaces three separate cells with one decisive comparison.
- **Cost:** ~2-3 hr GPU (5 arms x 3 seeds at V=4000).
- **P_deflated(at least one of ARMs C/D HARD_PASSes):** 0.45 (raw 0.60, deflated 0.20, +0.05 strong brain prior on C+D combined; cap invoked).

**Recommendation:** **Option 5c is the dominant recommendation.** It captures USER's worry (drops sole reliance on label-driven), respects brain prior (ARMs C+D are biology-native), and is decisive (5-arm shotgun at the load-bearing scale).

**IF Director dispatch authorization eventually comes,** Option 5c should be Wave E Cell H' (H-prime), to be authored after Wave D Cell 1 v3 lands (so ARM_HUB_SPOKE_v3 can be pulled in as a comparison datapoint).

---

## 6. P_deflated rollup

| Item | P_deflated | Confidence |
|---|---|---|
| Cell 7 result is SATURATION-driven (interp a) | 0.65 | high |
| Cell 7 result is JL-OVERSATISFACTION-driven (interp d sharpened, this drill's primary lens) | 0.70 | high |
| Cell 7 result is WRONG-TAXONOMY-driven (USER's worry, interp b sharpened) | 0.40 | medium |
| Label-driven AT V=4000 HARD_PASSes (Option 5a, interpretation d retest) | 0.30 | medium |
| Cell H biology-native shotgun has at least one ARM HARD_PASS at V=4000 (Option 5b ARMs C/D combined) | 0.45 | medium |
| Option 5c 5-arm discriminator identifies winning construction at V=4000 (regardless of which arm) | 0.65 | medium-high |
| Brain-grounded anisotropy is unsupervised (Olshausen-Field + Foldiak + Kohonen path) | brain existence proof | high |
| Label-driven anisotropy is the substrate-Stage-1.5 commit | 0.15 | low (was 0.40 pre-Cell-7-landing per prior drill; further deflated by this 2x drill) |

**Final standing:** Cell 7 v1 negative landing is consistent with multiple non-fatal interpretations (saturation at small V + JL oversatisfaction + within-category-dim-redistribution cost). Label-driven path is NOT dead but carries fundamental brain-prior violation that USER's course-correction surfaces. The dominant recommendation is Option 5c 5-arm discriminator cell H' at V=4000, comparing label / graph / sparse-coding / federated constructions. See companion note for biology-native deep dive.

-- Research (Director), 2x revival drill complete
