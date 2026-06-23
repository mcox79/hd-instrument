# Encoder-side cleanup-ceiling-break: 6-candidate drill post 4-family decoder rejection

**Date:** 2026-06-23
**Author:** Research (Opus 4.7)
**Drill type:** Substrate-native encoder-side interventions (upstream of cleanup)
**Trigger:** META finding -- 4 decoder-side cleanup mechanism families (att1 Hopfield-iter v1; att1 Krotov-dense v2; OMP sparse-coding; multi-bump CAN) ALL fail to lift argmax baseline at N=512 M=200 sigma=1.5. cleanup-ceiling is **encoder-bound, not decoder-bound** at this regime.
**Parent conditional:** `research_alternative_cleanup_mechanisms_post_att1_rejection_2026-06-23.md` HARD_FAIL branch instantiated.
**Lit-scan calibration penalty:** applied (deflate raw P 0.15-0.25; cap novel-synthesis P at 0.50)
**Generic-terms-only queries** per query-privacy

---

## HEADLINE
Top-2 to dispatch: **(1) Fly-LSH WTA + median-subtract composed with CERT 591 projection (P_deflated=0.45; cerebellar K=5 sparse-fan-in as ARM A backup; already pre-registered in 5x-DEEPER drill 2026-06-21; ~1-2 hr CPU sweep)** and **(2) N=512 -> N=4096 codebook lift WITH STRUCTURED ENCODING (sparse fan-in + biased seed; ~30 min CPU)**. CRITICAL REFRAME: at sigma=1.5, N=512, M=200, **argmax baseline = 0.023 ~ random (1/200=0.005, expected random ~0.02)** -- the codebook signal is effectively destroyed in noise. This is NOT a cleanup problem at all; it is a signal-to-noise problem at the encoder. The four decoder mechanism HARD_FAILs were correctly diagnosed; the next move MUST be encoder-side. n10 whitening already HARD_FAILED at production scale (effective rank lifted 16.7 -> 230, but recall barely changed). The substrate's deepest finding (`research_2x_drill_d_eff_REFUTED_isotropy_REFRAME_2026-06-20`) says ISOTROPY (rho_mean) is the load-bearing encoder variable, NOT effective rank. Cleanup-ceiling-break = isotropy-injection, not dimension-lift.

---

## CHEAP DECISIVE TEST (top candidate: structured N-lift with discriminating control)

**Premise:** At sigma=1.5, the per-dimension noise std is fixed. Concentration of measure says random vectors in higher N are nearer-orthogonal AND the per-direction noise contribution to similarity goes as 1/sqrt(N). So a naive N=4096 lift should raise argmax recall mechanically (P=0.85). BUT n10 whitening already showed that dimension-lift via random rotation alone is INSUFFICIENT (effective rank to 230 with no recall lift). The substrate's `isotropy_REFRAME` finding says the WHY: encoder vectors live on a low-rank cone whose mean-direction (rho_mean) dominates similarity. So a meaningful test must DISCRIMINATE structural lift (sparse-fan-in + median-subtract) from dimension lift alone (Gaussian random rotation).

**Cell design `enc1_structured_n_lift_v1`:**
- M=200, N_EVAL=200, seeds=[7,17,23], sigmas=[0.0, 0.5, 1.0, 1.5, 2.0]
- Five ARMS (each fed same noisy cue + atom data, same argmax decoder):
  - **ARM_BASELINE_N512** (current substrate: dense bipolar random codebook at N=512; matches parent HARD_FAIL config)
  - **ARM_DENSE_N4096** (dense bipolar random codebook at N=4096; pure dimension lift via JL random projection; predicts argmax noise 1/sqrt(8)~0.35x lower per-dim if structureless)
  - **ARM_SPARSE_FANIN_K5_N4096** (each codebook row has only K=5 nonzero bipolar entries; substrate-native cerebellar-GC analog; per-row mu-contribution variance ~ K not N; **discriminating control** against ARM_DENSE_N4096)
  - **ARM_MEDIAN_SUB_N512** (current codebook at N=512 with median-subtract pre-decode on both cue and codebook rows; fly-LSH-style shift-invariance; tests whether the rank-1 mu is the dominant failure mode at N=512)
  - **ARM_MEDIAN_SUB_SPARSE_N4096** (composition: median-subtract + sparse-fan-in N=4096; predicted top performer)
- Wall: ~5-10 min laptop CPU (numpy matmul only; no iteration).

**Decisive metric:** argmax recall@1 at sigma=1.5, across 3 seeds.

**Pre-reg thresholds (per ARM, vs ARM_BASELINE_N512 = 0.023):**
- HARD_PASS: arm_recall >= 0.20 at sigma=1.5 AND CV <= 0.30 (substrate-meaningful lift, ~8x baseline)
- HARD_FAIL: arm_recall <= 0.04 at sigma=1.5 (within 2x baseline noise; mechanism null)
- MIDDLE_BAND: arm_recall 0.04-0.20 (measured-mechanism, characterize)

**Discriminating-regime gate (mandatory):**
- If ARM_DENSE_N4096 >= 0.20 alone (pure dimension lift suffices): the whole sparse-fan-in / median-subtract framing is **wrong**; substrate noise problem is just N=512 over-capacity and the answer is dimension. Atomize "N=512 cleanup ceiling = N under-capacity at sigma>=1.5".
- If ARM_DENSE_N4096 < 0.20 AND ARM_SPARSE_FANIN_K5_N4096 >= 0.20: sparse-fan-in is load-bearing per `rank-1-anisotropy-trap discipline` (5x-DEEPER 2026-06-21). The mechanism transfers to current N=512 cleanup-ceiling.
- If both >= 0.20 BUT ARM_DENSE_N4096 > ARM_SPARSE_FANIN_K5_N4096: dimension dominates structure; sparse-fan-in is unnecessary.

**Sanity self-test (mandatory before dispatch):**
- At sigma=0.0, all 5 arms must achieve recall@1 = 1.000 (clean cue = atom-recovery is by construction). If any arm fails this, the cell has an implementation bug, NOT a mechanism rejection.

---

## FALSIFIABLE PREDICTIONS

### Top candidate: structured N-lift with discriminating sparse-fan-in vs dense-rotation control

**Quantitative predictions at sigma=1.5, M=200:**
1. ARM_BASELINE_N512 reproduces parent HARD_FAIL: recall 0.020-0.030 (~chance).
2. ARM_DENSE_N4096 lift: predict 0.05-0.20 (P=0.40 it hits HARD_PASS; raw lit P=0.65 from JL distance preservation deflated by 0.25 because (a) noise sigma scales independently of N, (b) atom-storage interference still scales as M/N=0.049 << over-capacity).
3. ARM_SPARSE_FANIN_K5_N4096: predict 0.30-0.60 (P=0.50 HARD_PASS, capped at novel-synthesis ceiling; per Litwin-Kumar 2017 + 5x-DEEPER 2026-06-21 K*~sqrt(N_pre)~22, so K=5 is in the operating regime).
4. ARM_MEDIAN_SUB_N512: predict 0.03-0.10 (P=0.20 HARD_PASS; isotropy_REFRAME says median-subtract alone DOES help if rho_mean dominates, but on random bipolar codebook (which substrate uses for the cleanup-ceiling test), mean ~ 0 by construction, so median-subtract is a no-op).
5. ARM_MEDIAN_SUB_SPARSE_N4096: predict 0.30-0.65 (P=0.50; composition rarely fully additive but here median-subtract is near-no-op so should match ARM_SPARSE_FANIN_K5_N4096).

**Falsifiers (mechanism truly null at encoder level):**
- **HARD_FAIL ALL 4 NON-BASELINE ARMS at sigma=1.5:** the substrate's cleanup-ceiling at this regime is a **fundamental information-theoretic floor**, not a mechanism gap. At sigma=1.5 with M=200 the cue's signal-to-noise is below recoverable threshold regardless of encoder geometry. Action: META atom `cleanup_ceiling_at_sigma_1.5_M_200_is_Shannon_floor_not_mechanism`; descope the sigma=1.5 stress-regime; substrate operates at sigma<=1.0 only.
- **HARD_PASS ARM_DENSE_N4096 but ALL OTHER ARMS NULL:** dimension is the only lever; structure is irrelevant. Atomize as "encoder dimension lift to N=4096 closes cleanup-ceiling; sparse-fan-in unnecessary"; deprioritize the rank-1-anisotropy-trap framing in this regime.
- **HARD_FAIL all 5 incl. baseline:** sigma=0 sanity broken; implementation bug. Re-test before mechanism conclusion.

**Implications if HARD_PASS (ARM_SPARSE_FANIN_K5_N4096 or composition):**
- Substrate gets a NEW encoder primitive: `sparse_fanin_codebook(N=4096, K=5)` ships to `hdlab/`
- n4 k-WTA-VQ unblocked: the n4 cell at N=16384 dense was 0.000 ceiling-delta; rerun with sparse-fan-in encoding may break the bigram-gap floor
- n9 sparsemax + sparse-encoder composition opens compositional cleanup capability
- Path A pseudo-LM ALSO uses dense bipolar codebook; sparse-fan-in encoder may directly help the text8 v2 calibrated cell beat unigram BPC 8.024
- META atom: `cleanup_ceiling_break_via_structured_encoder_geometry_not_dimension_alone`

**Implications if HARD_FAIL all encoder arms:**
- Cleanup-ceiling at sigma>=1.5 is **fundamentally information-theoretic** at any substrate config tested
- Substrate operating envelope = sigma <= 1.0 for cleanup; document as honest envelope, do NOT chase higher noise
- META atom: `cleanup_ceiling_at_high_noise_is_shannon_floor_decoder_and_encoder_independent`
- Pivot: instead of cleanup-side, route to **reduce noise at source** (encoder upgrade pythia-160m -> 1B -> 2.8B per n10 conclusion; or contrastive learning to compress signal into low-noise subspace)

---

## RANK-ORDERED CANDIDATES (6 families)

### #1. Structured N-lift via sparse-fan-in K=5 + median-subtract (P_deflated=0.45-0.50)

**Mechanism:** each codebook row has only K=5 nonzero bipolar entries at random positions (cerebellar GC analog per Marr-Albus / Litwin-Kumar 2017); N expands from 512 to 4096. Per-row mu-contribution variance ~ K sigma_mu^2, NOT N sigma_mu^2 (as in dense projection); breaks rank-1 anisotropy trap qualitatively. Composes with median-subtract pre-decode for residual mu.

**Brain analog:** STRONG. Cerebellar GC layer is THE canonical biological expansion-recoding mechanism; K=4 mossy-fiber fan-in per GC empirically measured (Cayco-Gajic 2017; Litwin-Kumar 2017). Drosophila MB Kenyon cells use K=6-8 PN fan-in. Fly olfactory hashing (Dasgupta-Stevens-Navlakha 2017 Science) gives the WTA-shift-invariance variant.

**Substrate-native variant:** new encoder primitive. Codebook D shape becomes [M, N=4096] but each row is K=5-sparse bipolar. Inner-product decode unchanged.

**Cell to test:** ENC1 5-arm sweep as in "cheap decisive test" above. ~5-10 min laptop CPU.

**P_revival deflated:** 0.45-0.50 (capped). Raw P=0.60 from 5x-DEEPER 2026-06-21 anisotropy-rescue analysis (ARM A predicted HARD_PASS 0.30-0.40) plus dimension-lift compound benefit; deflated 0.10-0.15 because (a) the parent's M=200 N=512 regime is NOT the M=10k anisotropic learned-key regime the 5x-DEEPER was designed for (it is a SYNTHETIC random bipolar codebook with mu~0 by construction, where rank-1-mu trap may be already absent); (b) prior 5x-DEEPER drill is unfired (ARM A,B,C still pre-reg, not measured).

**Cost:** ~30min impl + ~10min smoke. Laptop CPU. Composes with existing `hdlab/whitening.py`.

**Structural orthogonality to four-rejected-decoders:** HIGH. Encoder-side (upstream of cleanup); fully orthogonal to argmax / softmax / krotov / OMP / multi-bump dynamics.

**Critical caveat:** the parent N=512 M=200 regime uses random bipolar codebook with mean ~ 0 BY CONSTRUCTION. The 5x-DEEPER drill assumed anisotropic LEARNED keys (from pythia/BGE/CERT 591 projection) where rank-1 mu was empirically large. If substrate's argmax-baseline failure at sigma=1.5 is due to per-dimension noise dominance (not anisotropy), only the **dimension lift** part of this candidate helps; the **sparse-fan-in** part is moot. The cell's discriminating control (ARM_DENSE_N4096 vs ARM_SPARSE_FANIN_K5_N4096) measures this directly.

---

### #2. Pure N=512 -> N=4096 codebook dimension lift (P_deflated=0.35-0.40)

**Mechanism:** higher N means random codebook vectors more nearly orthogonal (1 - |<u,v>| ~ 1/sqrt(N) for unit vectors) AND per-dimension noise std fixed at sigma means relative-to-signal noise on similarity score drops as 1/sqrt(N). Direct test: same M/N RATIO actually means less storage interference (M/N = 200/4096 = 0.049 << 0.39 at baseline). Both encoder geometry AND storage-interference improve.

**Brain analog:** mid; cortical-volume scaling shows higher dimensionality across mammalian species correlates with associative-memory capacity (Kanerva 1988; Plate 1995).

**Substrate-native variant:** trivial: re-instantiate codebook at N=4096 with same generation procedure (random bipolar).

**Cell to test:** ARM_DENSE_N4096 of the ENC1 cell above. Same compute cost.

**P_revival deflated:** 0.35-0.40. Raw P=0.65 from JL distance-preservation + lower M/N storage interference; deflated 0.25-0.30 because (a) noise sigma scales independently of N (the actual per-dimension noise contribution per cue is the same regardless of N -- it just spreads across more dimensions in higher N; the **per-cue signal-to-noise ratio is unchanged**); (b) n10 already tested dimension via effective-rank lift (16.7 -> 230) at production and recall barely changed.

**KEY REFRAME**: this is the **null hypothesis** of the cell. If it HARD_PASSES, the substrate's whole "encoder geometry matters" framing for this regime is wrong, and the answer is just "use bigger codebooks".

**Cost:** trivially in ENC1 cell. Free.

**Structural orthogonality:** HIGH. Encoder-side; fully orthogonal to decoder dynamics.

---

### #3. Median-subtract whitening (substrate-cheap variant) (P_deflated=0.20-0.30)

**Mechanism:** subtract median (or mean) of cue and codebook before decode; kills rank-1 common-mode mu. Fly-LSH-style shift invariance per Dasgupta-Stevens-Navlakha 2017. Cheap alternative to full ZCA whitening.

**Brain analog:** strong; cortical neurons compute relative-to-mean signals via lateral inhibition (Foldiak 1990 anti-Hebbian).

**Substrate-native variant:** one-line preprocessing on top of existing decode pipeline.

**P_revival deflated:** 0.20-0.30. Capped LOW because: (a) the parent's random bipolar codebook has mean ~ 0 BY CONSTRUCTION (each row drawn from {-1,+1}^N uniformly, so empirical mean -> 0 as N grows); rank-1 mu is structurally absent in this test regime. (b) Substrate's CERT 591 projection already partially decorrelates LEARNED keys upstream.

**HOWEVER**: median-subtract IS load-bearing for the production substrate pipeline (where encoder = pythia/BGE produces non-zero-mean keys). The cleanup-ceiling-break in the SYNTHETIC parent regime tells us little about the PRODUCTION regime.

**Cost:** trivial. ARM_MEDIAN_SUB_N512 in ENC1 cell.

---

### #4. Foldiak 1990 anti-Hebbian decorrelation (P_deflated=0.15-0.25)

**Mechanism:** codebook auto-whitens during ingest via anti-Hebbian lateral inhibition between codebook entries. Convergence proved (1511.09468 Pehlevan-Sengupta-Chklovskii 2015 -- Hebbian/anti-Hebbian networks compute PCA + whitening). Substrate-native; brain-grounded.

**Brain analog:** STRONG. Cortical lateral inhibition between pyramidal cells is the canonical example.

**Substrate-native variant:** new ingest rule. For each new atom v_new, subtract sum of anti-Hebb-weighted projections onto existing codebook entries: `v_new <- v_new - eta * sum_i <v_new, v_i> * v_i / ||v_i||^2`. Iterated until convergence (Gram-Schmidt-like online orthogonalization).

**Cell to test:** ENC2 anti-Hebb codebook construction. Predict argmax recall lift at sigma=1.5 vs random codebook.

**P_revival deflated:** 0.15-0.25. Raw P=0.35-0.45 from Foldiak 1990 + Pehlevan 2015 + Krotov-Hopfield 2026 BTSP self-orthogonalizing (relative-floor / Oja-like; 5x-DEEPER 2026-06-21 depth-3); deflated 0.15-0.20 because (a) substrate's M=200 N=512 (M/N=0.39) is at over-capacity where strict orthogonalization fails (Gram-Schmidt rank-limited to min(M,N)); (b) Krotov 2026 BTSP is at d=N=64 small-scale demo, not 512.

**Cost:** ~1hr impl + ~30min smoke. CPU. Separate cell from ENC1.

**Structural orthogonality:** HIGH (encoder-side construction; orthogonal to decoder).

**Crucial:** this only helps if codebook entries are MEANINGFUL ATOMS to be orthogonalized (substrate's actual use), NOT if they are noise-pattern signals (the parent's synthetic test). For substrate-product, this is the more meaningful test.

---

### #5. Random projection lift + cleanup (cheaper than full N=4096 substrate) (P_deflated=0.15)

**Mechanism:** project N=512 cue through random N=4096 matrix; cleanup in lifted space then back-project. Johnson-Lindenstrauss style.

**Brain analog:** mid.

**Substrate-native variant:** `lift = random_bipolar(512, 4096); cue_lifted = lift @ cue; codebook_lifted = codebook @ lift.T; argmax(cue_lifted @ codebook_lifted.T)`.

**P_revival deflated:** 0.15. CRITICALLY LOW because random projection PRESERVES inner products in expectation (JL lemma) -- it does NOT improve them. By Cauchy-Schwarz-style invariants, the JL-projected argmax similarity is identical-in-expectation to the original argmax similarity. The only lift comes from variance reduction across the embedding dimension, which is 1/sqrt(8) ~ 0.35x for N=4096/N=512 ratio -- modest at best. **Substrate already saw this with n10 ZCA whitening.**

**Cost:** trivial.

**Structural orthogonality:** moderate (lift is a different operator than re-encoding from scratch; but mathematically near-equivalent).

**Recommend: SKIP** unless ARM_DENSE_N4096 in ENC1 fails -- this would just confirm the structural-encoding-needed conclusion.

---

### #6. Compositional encoding (entity + relation bind upstream) (P_deflated=0.10-0.15)

**Mechanism:** instead of cleaning up the noisy raw cue, bind the cue with a context vector first; cleanup post-bind. Substrate-native variant of contextual disambiguation.

**Brain analog:** weak-mid; place-cell + context-vector binding analogy.

**Substrate-native variant:** assumes a context vector exists in the cleanup task, which is NOT the case for the parent's pure single-atom cue test.

**P_revival deflated:** 0.10-0.15. The parent's cleanup test is genuinely context-free (single atom + noise -> recover atom); compositional binding does not apply structurally. Re-evaluate this candidate ONLY for downstream tasks where context exists (e.g. sequence-binding cleanup, multi-hop traversal).

**Cost:** N/A in this regime.

**Recommend: DEFER** to downstream-task drills.

---

## CROSS-THREAD SYNTHESIS

**With prior `research_alternative_cleanup_mechanisms_post_att1_rejection_2026-06-23` HARD_FAIL branch:**
- Branch correctly fired: all 4 decoder candidates failed at sigma=1.5; encoder-side is the indicated next move.
- BUT the branch's framing ("substrate's cue-to-codebook noise problem is structural -- noise at sigma=1.5 has effectively destroyed the codebook signal regardless of decoder") **anticipated the wrong fix**: it pointed to "whitening / lift to N=4096" without the discriminating control between dimension lift and structural geometry. This drill fixes that by including BOTH ARMs.

**With `research_substrate_memory_density_DEEPER_5x_biology_brain_branching_2026-06-21`:**
- The 5x-DEEPER drill ALREADY pre-registered ARM A (cerebellar K=5) and ARM B (fly-LSH WTA) for the M=10k anisotropic LEARNED-key regime. The structural lift is the same; only the test regime differs (M=200 SYNTHETIC random bipolar vs M=10k LEARNED anisotropic).
- HIGH-PRIORITY REVIVAL CALL: the 5x-DEEPER ARM A,B,C cell was pre-registered but never dispatched. Doing the simpler ENC1 sweep first (5-10 min CPU) gives a fast read on whether the mechanism transfers to the parent regime BEFORE the more expensive 1-2hr M=10k learned-key cell. **Recommend: dispatch ENC1 as the cheap pre-screen; if HARD_PASS, the 5x-DEEPER full cell becomes much more credible.**

**With `research_2x_drill_d_eff_REFUTED_isotropy_REFRAME_2026-06-20`:**
- Substrate's deepest published finding: **isotropy (rho_mean) is the load-bearing encoder variable, NOT effective rank**. Pythia/BGE mean-pool fails because rho_mean is too high (vectors concentrated in narrow cone). MiniLM passes because vectors are more spread.
- For the parent regime (random bipolar codebook): rho_mean ~ 0 BY CONSTRUCTION. So this finding predicts the PARENT regime is NOT isotropy-limited and the median-subtract / Foldiak / fly-LSH-style fixes will NOT help much there. **They WILL help in the production regime with real encoder keys.**
- **Reframe:** the parent's HARD_FAIL is a **per-dimension noise floor** issue (the per-dimension signal IS being preserved; there is just too much per-dim noise relative to the per-dim signal at sigma=1.5 with M=200). The fix is **either dimension lift (to dilute noise across more dims) OR signal-injection (richer per-atom signal via sparse fan-in's larger atom-distinctness)**.

**With existing `hdlab/whitening.py` + n10 whitening cell:**
- n10 cell ran ZCA whitening at production with PRODUCTION encoder (pythia-160m projected); recall barely moved despite eff_rank 16.7 -> 230. Indicates whitening alone is INSUFFICIENT in production.
- For the parent SYNTHETIC regime, whitening is structurally a no-op (random bipolar codebook IS already approximately white).
- The combination of these two findings says: substrate's noise problem requires **richer per-atom signal (structural encoding via sparse-fan-in)** OR **dimension lift**. Pure whitening / median-subtract preprocessing is necessary but insufficient.

**With existing n4 k-WTA-VQ at N=16384 HARD_FAIL:**
- At N=16384 with V_C=1024 (M/N = 0.06 -- way below over-capacity), kWTA k=1,8,32 all give same ceiling 2.050 bits/char. This argues AGAINST the pure dimension-lift hypothesis -- at much larger N, the bigram-gap floor still holds.
- Compatible interpretation: dimension alone does NOT save us; substrate needs structural encoder change (sparse-fan-in IS structurally different from kWTA on dense; n4 was kWTA on dense).

**With existing chain-grade Hebbian-auto-associative finding (2026-06-20):**
- Hebbian-auto-associative (substrate auto-associates inputs into codebook via Hebb-rule outer product) is a **substrate-native encoder mechanism** that gives bounded mu-contribution per atom via the rank-bounded outer-product. Composes with sparse-fan-in.

---

## SUBSTRATE-PRODUCT IMPLICATIONS

**If ARM_SPARSE_FANIN_K5_N4096 HARD_PASSES (P=0.45-0.50):**
- New hdlab encoder primitive: `sparse_fanin_codebook(M, N, K)` ships substrate-flat.
- n4 k-WTA-VQ ceiling unblocked: rerun at sparse-fan-in encoding; potential bigram-gap closure (the 1.13 bits to text8 word-bigram referent might shrink).
- Path A pseudo-LM (which uses dense bipolar codebook for value-side) gains a structured encoder; v3 cell could test sparse-fan-in directly.
- n10 whitening composes: median-subtract -> sparse-fan-in -> ZCA-whiten on top. Production pipeline order: encoder pythia -> CERT 591 projection -> ZCA whiten -> sparse-fan-in re-encode (new step).
- META atom: `cleanup_ceiling_break_via_sparse_fanin_encoder_geometry`.
- Composes with continual-learning (CLS-replay) by giving each replayed atom a structurally-distinct encoding regardless of when ingested.

**If ARM_DENSE_N4096 HARD_PASSES BUT structured arms HARD_FAIL:**
- Pure dimension lift suffices; substrate operational recommendation = use N=4096 as new default for codebook regime; reserve N=8192 for over-capacity / high-noise stress regimes.
- META atom: `cleanup_ceiling_break_via_dimension_lift_alone_at_sigma_1.5`.
- Does NOT immediately help Path A (which already uses N=16384) but DOES help all n4/n9/n10/p1 cells running at N=512 substrate-config.

**If ALL ENCODER ARMS HARD_FAIL at sigma=1.5:**
- Cleanup-ceiling at sigma>=1.5 with M=200 is a **Shannon information-theoretic floor** -- not addressable by either encoder OR decoder change.
- Substrate operational envelope = sigma <= 1.0 for cleanup; this becomes a documented envelope, not a capability claim.
- META atom: `cleanup_ceiling_at_sigma_1.5_M_200_is_shannon_floor`.
- Pivot to noise-reduction at source: encoder upgrade (pythia-160m -> 1B -> 2.8B per n10) OR contrastive learning to compress signal into low-noise subspace upstream of substrate ingest.

**For bigram-gap closure (~1.13 bits to text8 word-bigram):**
- If sparse-fan-in encoder HARD_PASSES at parent regime, Path A pseudo-LM (which is bottlenecked on similar argmax-cleanup at N=16384) **may close 0.3-0.7 bits** of the bigram-gap by switching encoder.
- If ONLY dimension-lift HARD_PASSES, Path A (already at N=16384) is already past the dimension regime; this drill does not help Path A.
- Either way, ENC1 cheap sweep gives a fast read.

---

## CITATIONS (verified)

1. Litwin-Kumar et al. 2017 Neuron "Optimal Degrees of Synaptic Connectivity" (cerebellar K=5 fan-in theory)
2. Cayco-Gajic et al. 2017 PMC5729189 "Morphological Constraints on Cerebellar Granule Cell Combinatorial Diversity" (K~4 empirical)
3. Dasgupta, Stevens, Navlakha 2017 Science "A neural algorithm for a fundamental computing problem" (fly-LSH WTA hash)
4. Foldiak 1990 Biol Cybern "Forming sparse representations by local anti-Hebbian learning"
5. Pehlevan, Sengupta, Chklovskii 2015 arXiv:1511.09468 "Optimization theory of Hebbian/anti-Hebbian networks for PCA and whitening" (convergence proof; PCA + whitening duality)
6. Pehlevan, Sengupta 2018 arXiv:1812.11581 "Unsupervised learning by a nonlinear network with Hebbian excitatory and anti-Hebbian inhibitory neurons"
7. Babadi & Sompolinsky 2014 (rank-1 trap in dense expansion + kWTA; cited from 5x-DEEPER drill 2026-06-21)
8. Bell & Sejnowski 1997 (ZCA whitening canonical reference; cited from `hdlab/whitening.py`)
9. Krotov-Hopfield 2026 BTSP (self-orthogonalizing relative-floor; cited from 5x-DEEPER depth-3)
10. Johnson-Lindenstrauss lemma (m = O(eps^-2 log n) embedding dimension; multiple sources)
11. Frady-Kleyko-Sommer 2018 (sparse-VSA / Bloom-VSA capacity)
12. Aoki, Noest 1988 + Plate 1995 (phase-coding / complex-Hopfield HRR; phase tags from uniform-S^1 break rank-1 by construction; cited 5x-DEEPER depth-2)
13. Bittner-Magee 2017 + Milstein 2021 (BTSP relative-floor empirical; cited 5x-DEEPER depth-3)
14. Salvatori 2021 NeurIPS (predictive coding associative memory iterative inference)
15. Kanerva 2009 / 1988 (Hyperdimensional Computing capacity / SDM)
16. Internal: `research_2x_drill_d_eff_REFUTED_isotropy_REFRAME_2026-06-20` (substrate's rho_mean as load-bearing encoder variable, not d_eff)
17. Internal: `research_substrate_memory_density_DEEPER_5x_biology_brain_branching_2026-06-21` (cerebellar K=5 + fly-LSH compositing with CERT 591 for anisotropic learned-key regime)
18. Internal: `notes/research_alternative_cleanup_mechanisms_post_att1_rejection_2026-06-23` (parent drill HARD_FAIL conditional branch)
19. Internal: `data/exp_n10_whitening_projection_revival_v1/metrics.json` (ZCA whitening HARD_FAIL at production; eff_rank 16.7 -> 230 with no recall lift)
20. Internal: `hdlab/whitening.py` (ZCA + PCA whitening primitives already shipped)
21. Internal: `data/exp_omp_sparse_coding_cleanup_v1/metrics.json` (OMP HARD_FAIL; argmax baseline 0.023 at sigma=1.5)
22. Internal: `data/exp_multi_bump_can_ensemble_cleanup_v1/metrics.json` (multi-bump CAN MIDDLE_BAND lift +0.002)
23. Internal: `data/exp_att1_iterative_attractor_v2_low_storage_ratio_krotov_v1/metrics.json` (Krotov HARD_FAIL)
24. CERT 591 dense-projected-KV (substrate's learned contrastive projection)

**Verified count: 24 sources spanning 6 candidate-mechanism families + 8 substrate-internal cross-references.**

---

## OPERATIONAL DRILL SUMMARY

- **Dispatch IMMEDIATELY:** ENC1 5-arm sweep (ARM_BASELINE_N512 + ARM_DENSE_N4096 + ARM_SPARSE_FANIN_K5_N4096 + ARM_MEDIAN_SUB_N512 + ARM_MEDIAN_SUB_SPARSE_N4096). ~5-10 min laptop CPU. Discriminating-regime gate: ARM_DENSE_N4096 vs ARM_SPARSE_FANIN_K5_N4096 measures dimension-vs-structure. Pre-flight sanity: sigma=0 recall = 1.000 across all arms.
- **Dispatch second (if ENC1 HARD_PASSES sparse-fan-in):** revive 5x-DEEPER 2026-06-21 cell at M=10k anisotropic LEARNED keys (ARMs A,B,C against CERT 591 projection); full validation in production regime.
- **Dispatch third (if ENC1 HARD_FAILS or MIDDLE_BAND on structured arms):** Foldiak anti-Hebb codebook construction (ENC2; ~1hr CPU); tests whether the structural-encoder approach needs MEANINGFUL ATOMS not random bipolar to manifest.
- **Defer / skip:** #5 random projection lift (redundant with dimension lift baseline); #6 compositional encoding (no context in parent regime).
- **Annotate `hdlab/whitening.py` docstring:** add note that n10 cell HARD_FAILED at production (eff_rank 16.7 -> 230 with no recall lift) -- whitening is necessary but insufficient; sparse-fan-in or dimension-lift is the next layer.

**Cross-thread synthesis -- substrate noise tolerance at sigma>=1.0:**
- At sigma=1.5 N=512 M=200: argmax baseline = 0.023 ~ random. Cue signal effectively destroyed by per-dim noise.
- At sigma=1.5 N=512 M=50 (low storage; att1_v2): argmax = 0.093 -- 4x better with same noise but 4x less storage. Confirms M/N ratio (interference) AND sigma jointly determine signal floor.
- The cleanup-ceiling at sigma>=1.5 sits at the boundary of recoverable signal; the substrate's working envelope is sigma<=1.0 unless encoder structure can rescue.
- This is NOT a fundamental capacity bound of HD computing -- it is a specific N=512 M=200 sigma=1.5 over-capacity-at-high-noise issue. ENC1 measures whether structural encoder or dimension lift can rescue.

**Substrate-product summary:** the cleanup ceiling unblocks downstream substrate primitives (n4 / n9 / n10 / p1 + Path A pseudo-LM) IF the structured encoder hypothesis (sparse-fan-in + median-subtract) HARD_PASSES at the parent regime. The 5-10 min ENC1 sweep is the cheapest decisive test of this hypothesis available. Subsequent revival of the 5x-DEEPER 2026-06-21 cell at production regime gives the chain-grade validation.
