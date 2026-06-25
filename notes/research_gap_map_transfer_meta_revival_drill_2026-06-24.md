# META 2x+3x revival drill: does gap-map "Store has solutions" transfer apples-to-apples to substrate-native?

date: 2026-06-24
trigger: Resonator integration cell (DISPATCH 1) HARD_FAIL — NAIVE 2HOP 0.65 ~= RESONATOR 2HOP 0.63 — the Stage-1 closure roadmap's central assumption (Store solutions are wirable) just got contradicted on Gap 1. USER directive: drill the shit out of it from disparate fields.
discipline: 2x+3x META revival, NOT lit-scan verification. Calibration penalty 0.20 on novel synthesis. Generic queries only off-platform.
cross-thread anchors: research_negative_N6_resonator_dense_V100_HF_2x_2026-06-20 (Frady-Sommer K_max algebra); research_2x_revival_comparator_resonator_HF_2026-06-23 (strictly-weaker-estimator pattern); director_stage1_gap_to_existing_solution_map_2026-06-24; director_stage1_closure_synthesis_2026-06-24

---

## HEADLINE

The gap-map's "Store solution proven => integration will close gap" inference is STRUCTURALLY UNSAFE for 5 of the 7 Stage-1 gaps. The Resonator HARD_FAIL is not a one-off — it is the predicted outcome of the Frady-Sommer K_max algebra under the apples-to-apples regime (M=500 / V_P=10 / N=8192 sits in a different point in the (V, K, N, alpha) phase diagram than wave14_multihop_resonator's chain-grade config), AND it instantiates a general pattern from coding-theory + signal-processing: a remedy that adds capacity / decoding-iterations only helps when the baseline is operating in the broken regime where the remedy's stronger-decoder hypothesis applies. When the baseline is unbroken (the smoke regime is too easy) OR when the failure mode is upstream of the remedy (encoder noise, not decoder weakness), the remedy is a strictly-weaker estimator and can tie or LOSE. Per-gap audit: Gaps 1 (Resonator), 5 (de-dup), 6 (multi-hop completeness) carry HIGH transfer-risk (the Store proof and the today-regime live at non-overlapping operating points). Gap 2 (tau-learning), Gap 3 (isotonic calibration), Gap 7 (whitening) carry MEDIUM transfer-risk (the underlying mechanisms are dataset-shift-sensitive per published lit). Gap 4 (audit-trail) is the lone LOW-risk integration (deterministic plumbing, not a statistical mechanism). VERDICT: pivot from "3-week wire-up" to "per-gap apples-to-apples micro-validation BEFORE 3-week integration" + adopt a 1-cell discriminator pattern that pre-registers the operating-point distance and predicts which gaps will close. P_deflated(at least 4 of 7 gaps fail to close on the first apples-to-apples wire-up at substrate regime) = 0.55. P_deflated(Gap 1 closes when reformulated as block-local sparse resonator at K<=K_max(V_P=10, N=8192)=7.2 with confidence-tier hop1->hop2 gating) = 0.45. P_deflated(Gap 4 audit-trail integration closes) = 0.65.

Plain English: when a Store cell proves mechanism X works on dataset/regime A, that is NOT a proof mechanism X works on dataset/regime B. The Resonator HARD_FAIL is a textbook case: wave14 proved Resonator works at N=65536 with anisotropic ConceptNet keys at one (V, K, alpha) point; today's apples-to-apples cell runs N=8192 random-bipolar keys at a different (V, K, alpha) point, AND the baseline (NAIVE 2HOP) is already at 0.65 which is high enough that the Resonator's iterative cleanup has very little room to add value. This is the same pattern the comparator_resonator_primitive_smoke HF showed yesterday (Section L7 of research_2x_revival_comparator_resonator_HF_2026-06-23): comparator was a strictly weaker estimator when raw lookup was unsaturated. Both failures share a single root cause: the smoke / apples-to-apples regime sits in the part of the phase diagram where the baseline already works, so the "more sophisticated" mechanism cannot help. The gap-map drill did not check the (V, K, alpha, anisotropy) coordinates of the Store proof vs the today-cell, so the closure prediction is unbacked.

---

## L1 -- TRANSFER LEARNING theory: when does method-X-on-dataset-A transfer to dataset-B?

The published OOD-generalization literature (Assaying OOD Generalization in Transfer Learning, Quantifying Transferability in Domain Generalization, Surrogate Models via Domain Affine Transformation) is clear that transfer guarantees REQUIRE one of:

1. **Distribution-overlap assumption** -- source and target have bounded KL or Wasserstein distance. The gap-map cells (ConceptNet, ad-hoc synthetic) vs apples-to-apples cell (random-bipolar V_P=10) live in distinct measure spaces; no overlap assumption holds.
2. **Invariant-mechanism assumption** -- the mechanism does not depend on the dataset-specific features. Resonator depends ON the codebook geometry (factor count V, codebook density, eigenvalue spectrum); it is NOT an invariant mechanism.
3. **Covariate-shift correction** -- whitening or domain-adaptive normalization that brings the target's covariate distribution to the source. Gap-map does not specify a covariate-shift step before the wire-up.

Without one of these three, transfer is empirically estimated, not theoretically guaranteed. The Resonator HARD_FAIL is the empirical "no transfer" outcome for assumption (2): the Store proof lived at one (V_P, K, N, anisotropy) point; the apples-to-apples cell lives at a different point; the mechanism does not invariantly close the gap.

**Implication for the 6 remaining gaps:** each gap-map "Store proof" sits at some (config, dataset, regime) point. The transfer-risk of each gap = distance(Store-proof regime, today-substrate regime) along the mechanism-sensitive axes. The gap-map drill of 2026-06-24 did not measure these distances.

---

## L2 -- INFORMATION GEOMETRY: why ConceptNet-anisotropic differs from random-bipolar-isotropic

The cell-author note ("gap-map's chain-grade ref was on ConceptNet anisotropic keys; doesn't transfer to random-bipolar synthetic") names the issue precisely. The published anisotropic-Marchenko-Pastur work (Asymptotics of Learning with Deep Structured Random Features arxiv 2402.13999; Gaussian Equivalence for Self-Attention arxiv 2510.06685) and the anisotropic-semantic-space literature establish:

- **Anisotropic embeddings** (ConceptNet, word2vec, transformer residuals) have heavy-tailed singular value spectra: ~10 dominant singular values carry >50% of the variance; the rest live in a low-amplitude tail. Multi-hop retrieval on anisotropic keys has a specific structure: the dominant-singular directions act as "lanes" that route signal through the W matrix with low cross-talk; iterative methods (Resonator) converge quickly because the high-singular-value directions are nearly-invariant subspaces.
- **Random-bipolar embeddings** (the substrate's synthetic regime) have Marchenko-Pastur spectra: all singular values cluster in a tight band around sqrt(N/M); there are NO dominant directions; cross-talk is uniformly distributed. Multi-hop retrieval on isotropic random-bipolar keys has uniform interference between any two stored facts; iterative methods (Resonator) cannot exploit dominant-direction lanes because none exist.

**The information-geometric reason Resonator helped on ConceptNet but not on random-bipolar:** Resonator's iterative cleanup converges fast when there are dominant subspaces to converge TOWARD. On Marchenko-Pastur isotropic keys, every direction is an equal candidate; iterative cleanup has no preferred basin to settle into. The convergence rate per Frady-Sommer Theorem 1 is `log(M_max) / log(V)` iterations, BUT this bound assumes the convergence dynamics exploits structural anisotropy; on isotropic codebooks the per-iteration error reduction is much smaller.

**This predicts:** Resonator will help on substrate-native if and only if substrate adopts an anisotropic encoder (the encoding-drill's "hub-and-spoke federation" or learned sparse-bipolar-with-amplitude). Resonator on raw random-bipolar substrate-native keys is structurally limited to the same regime where the comparator_resonator_primitive failed: a strictly-weaker estimator of what NAIVE 2HOP recovers cleanly.

Citation: Marchenko-Pastur edge law (arxiv 2402.13999, 2510.06685); anisotropic-semantic-space pathological-similarity result (emergentmind.com/topics/anisotropic-semantic-space).

---

## L3 -- DISTRIBUTED SYSTEMS / CONSENSUS: multi-hop chained retrieval as a consensus problem

The published multi-hop RAG literature (Reasoning in Trees RT-RAG arxiv 2601.11255; PRISM arxiv 2510.14278; Generative Multi-hop Retrieval ACL 2022) converges on a single architectural insight: **error propagation in sequential hops is irreversible without explicit consensus / verification at each hop**. Naive sequential retrieval (hop1 -> argmax -> hop2 -> argmax) has compound error 1 - (1-p1)(1-p2) which at p1=p2=0.10 already gives ~19% chain failure; the substrate's 0.40 chain completeness at 0.643 hop1 is the apples-to-apples instantiation.

The RT-RAG mechanism is NOT another decoder (Resonator family) -- it is a **consensus-based selection** between MULTIPLE CANDIDATE retrievals, scored by tree-frequency. This is structurally different from Resonator's single-decoder iterative cleanup. The substrate's parallel here would be:

- Generate K=5 candidate hop1 outputs (top-K instead of top-1)
- Generate K=5 candidate hop2 outputs CONDITIONED on each hop1 candidate
- Score each chain by joint confidence (sum or product of per-hop confidence)
- Return the highest-scoring chain

This is the brain's hippocampus-PFC consensus mechanism (L6 below): the hippocampus produces relational hypotheses; the PFC scores them via confidence-tier gating. The published transitive-inference work (PMC 2858584, PMC 2858584, PMC 2801762) shows hippocampal+rostrolateral-PFC dual-region consensus is REQUIRED for multi-hop, not just hippocampal pattern completion alone.

**Substrate-applicable consensus mechanisms beyond Resonator:**
1. **Top-K + joint-confidence rescore** (cheap; ~2x compute; brain-aligned)
2. **Bidirectional beam-search** (run hop1->hop2 AND hop2-reverse-key->hop1; intersect candidates)
3. **Hub-routing with tier gating** (use the substrate_72b_R0R1R2_tier_proof_walk_cpu_v1 confidence-threshold mechanism but applied per-hop, not just final)

Citation: Reasoning in Trees RT-RAG arxiv 2601.11255; PRISM arxiv 2510.14278; transitive-inference PMC 2858584.

---

## L4 -- SIGNAL PROCESSING: decision feedback equalization, iterative interference cancellation

The DFE / IIC literature (Decision Feedback Equalization with Feedback Error Detection; Iterative Soft Decision Interference Cancellation in DS-CDMA; Matched-filter based iterative soft DIC) names a critical phenomenon: **decision feedback creates error propagation when the first stage's hard decision is wrong** -- the subtracted "interference estimate" is itself wrong, AMPLIFYING the residual error in subsequent stages. The substrate's hop2-given-hop1 = 0.61 / hop1 = 0.643 is exactly this failure mode: hop1 hard-argmax outputs go into hop2's bind operation; when hop1 is wrong, hop2 cleans up an irrelevant key.

The signal-processing remedy is SOFT FEEDBACK: instead of hard-deciding hop1's argmax then feeding into hop2, pass the FULL probability vector (or top-K with weights) into hop2 and marginalize. This is mathematically equivalent to L3's consensus mechanism, but framed at the per-hop level rather than the chain level.

**Substrate-applicable DFE patterns:**
- **Soft hop1 -> hop2** (do not collapse to argmax; pass top-K confidence-weighted unbinding probes; sum the resulting hop2 evidence vectors before argmax)
- **Decision-feedback with hop1 error detection** (skip the chain if hop1 confidence is below tau; refuse rather than propagate)
- **Iterative re-decoding** (after hop2, USE hop2's result to refine hop1's estimate; iterate 2-3 times; this is the substrate's iterated multihop pretest which HARD_FAILed -- BUT that test was on the wrong regime; soft-feedback variant has not been tested)

**Operational read:** the substrate's gap 6 (40% chain completeness) is a textbook DFE error-propagation problem. The Store has the iterative-multihop_pretest cell (HARD_FAILed at recall@2 single=0.333 iter=0.373) which IS the hard-feedback variant. The soft-feedback variant has NOT been tested; this is a genuine missing experiment, not a Store solution. The gap-map's "Hybrid: resonator + pointer-chain + hub-routing -- proven" claim is incorrect: NONE of those individually proves soft-feedback; the substrate has not built that mechanism yet.

Citation: Matched-filter based iterative soft DIC (researchgate 4019785); Iterative Equalization with Soft Feedback (researchgate 3156708); DFE error propagation (sciencedirect engineering DFE overview).

---

## L5 -- CATEGORY THEORY: morphism composition is associative but information-lossy under quotient maps

Category theory (PMC 2908697 Categorial Compositionality; PLOS One Second-Order Systematicity Coalgebraic Resolution) gives a precise frame: HRR bind/unbind is a morphism in the category of high-dimensional vectors; multi-hop chained bind is morphism composition `f . g` where f = bind-with-R2 and g = bind-with-R1. Composition is associative by HRR algebra. BUT: each morphism is a *quotient map* (it loses information; the inverse is not unique up to the codebook resolution); composing two quotient maps multiplies the information loss.

The categorical reading of substrate's 2-hop interference: each unbind is `unbind = bind^{-1}` which exists only up to within-codebook ambiguity = quotient by similarity-band. Composing two unbinds gives a quotient-by-(similarity-band-squared) which is the chain-grade information loss. Resonator does NOT fix this; it provides iterative refinement WITHIN one quotient class, not collapse across multiple compositions.

**The category-theoretic missing structure for lossless multi-hop:** a **left adjoint** to bind -- specifically, a retraction `r` such that `r . bind = identity`. HRR has no such retraction at finite N (it would require N >> V * K, which only holds at N=65536 for V=100 K=2 -- the wave14 regime). At N=8192 V_P=10 K=2 substrate is BELOW the retraction-existence threshold.

**Operational read:** the substrate's multi-hop ceiling at 0.65 is a category-theoretic boundary, not a decoder-weakness boundary. Adding more iterations (Resonator) cannot pass it. Only either (a) increasing N to support the retraction (N >= 100k), or (b) explicit pointer-chains (the exp_pointer_chain HARD_PASS uses external indices to bypass the morphism-composition) can close it.

The gap-map's "pointer-chain + hub-routing" recommendation for gap 6 is correct at this level -- but it is the NON-COMPOSITIONAL escape hatch, not the compositional integration the prompt assumed. This needs to be made explicit in the closure plan.

Citation: PMC 2908697 Categorial Compositionality; PLOS One Second-Order Systematicity (journals.plos.org/plosone 10.1371/pone.0160619).

---

## L6 -- PER-GAP TRANSFER AUDIT: does each Store solution apples-to-apples transfer?

| Gap | Store proof regime | Apples-to-apples regime | Transfer-distance axes | Risk |
|---|---|---|---|---|
| 1 (2-hop interference) | wave14: N=65536, anisotropic keys, V eff small, depth=2-50 | M=500, N=8192, random-bipolar V_P=10 | N (8x), key-isotropy (anisotropic->isotropic), alpha (low->high) | HIGH -- ALREADY REFUTED |
| 2 (refuse-gate tau=0.70) | 61b: 4/7 novel queries refused; tau cal on small set | M=500 with unknown predicate distribution | tau threshold tuned on small distribution; cross-distribution calibration | MEDIUM -- tau likely off |
| 3 (isotonic calibration) | lap4_3: ran full route, mechanism known | M=500 conf vector; pearson_r=0.072 baseline | sample size for isotonic fit; distribution shift between fit-set and test-set | MEDIUM -- lit (arxiv 2006.16405, 2102.10395) shows isotonic does NOT survive covariate shift |
| 4 (provenance audit) | wave14_cap12 audit-trail v1-v5; program_exec_audit | Forward-walk reconstruction on 2-hop chain | Deterministic plumbing; no statistical mechanism | LOW -- pure deterministic; should transfer |
| 5 (predicate de-dup, V_P=10) | codebook_near_duplicate (HARD_PASS at K=241->209 on REAL anisotropic data) | V_P=10 RANDOM bipolar (independence implies orthogonality up to 1/sqrt(N)) | RANDOM-BIPOLAR is ALREADY orthogonal at N=8192; de-dup finds 0 duplicates by construction | HIGH -- the mechanism does NOT apply to the substrate's regime; this is a NULL operation |
| 6 (chain completeness 40%) | iterative_multihop_pretest (HARD_FAIL); hub_census (RESEARCH-GRADE); traceable_multi_hop (CAUSALITY only, not chain completion) | hop2_given_hop1 = 0.61 | NONE of the Store cells actually PROVES chain completion; gap-map mislabeled them | HIGH -- no genuine Store solution |
| 7 (sanity-gate variance) | C2 whitening (HARD_PASS); bio_smoke seeding | Random-bipolar codebook with seed-dependent init | Whitening removes initialization bias; this DOES apply; lit confirms (ZCA covariate-shift OK) | MEDIUM -- whitening transfers but seed-determinism plumbing is the gating step |

**Summary of per-gap risk:**
- **HIGH (3 gaps):** Gap 1, Gap 5, Gap 6 -- each Store "solution" is structurally inapplicable to the apples-to-apples regime or already-refuted. Closure on these three at the 3-week wire-up timeline has P=0.20 each.
- **MEDIUM (3 gaps):** Gap 2, Gap 3, Gap 7 -- mechanism transfers in principle but is sensitive to distribution shift / fit-set quality. Closure has P=0.45 each.
- **LOW (1 gap):** Gap 4 -- deterministic plumbing. Closure has P=0.85.

Expected number of closed gaps at 3-week mark = 3*0.20 + 3*0.45 + 0.85 = 2.80 out of 7. The "all 7 gaps closed in 3 weeks" framing of the gap-map is unsupported by the per-gap evidence.

---

## L7 -- SYNTHESIS: top alternative architectures + META verdict + strategy

### Top 3 alternative architectures for 2-hop interference (beyond Resonator)

1. **Soft-feedback hop1 -> hop2 (DFE soft-decision variant)** -- pass top-K hop1 candidates as confidence-weighted superposition into hop2 bind; sum hop2 evidence; final argmax. NOT in Store. Cheap to test (~2x naive compute). Brain-aligned (PFC marginalizes over hippocampal hypotheses). P_deflated(lifts 0.65 -> 0.78) = 0.45.

2. **Top-K consensus chain scoring (RT-RAG analog)** -- generate K=5 chains hop1xhop2; score each by sum(log_conf_per_hop); return argmax-chain. NOT in Store. Brain-aligned (consensus selection in PFC). Tests the LITERATURE's preferred multi-hop architecture. P_deflated(lifts 0.65 -> 0.80) = 0.50.

3. **Anisotropic-encoder + Resonator (geometry-fix)** -- replace random-bipolar predicate codebook with sparse-with-amplitude (encoding-drill E2 SoftHebb) creating Marchenko-Pastur-Plus dominant-direction structure; THEN apply Resonator. Tests whether Resonator failure is geometry-based or fundamental. P_deflated(lifts 0.65 -> 0.75 AND validates information-geometry hypothesis) = 0.40.

### META verdict: should we proceed with the gap-map integration plan?

**NO -- pivot required.** The gap-map approach assumes "Store proof => integration closure" but the Resonator HARD_FAIL falsified that on Gap 1, and the per-gap audit (L6) shows 3 of 7 are HIGH-risk for the same reason. Continuing the 3-week wire-up on the original plan will produce ~3/7 closures (60% miss rate) and burn the cell-author bandwidth.

### Strategic next-steps

1. **Replace the closure plan with a 1-cell per-gap discriminator pattern.** Each apples-to-apples test cell pre-registers: (a) the Store-proof regime coordinates, (b) the today-regime coordinates, (c) the transfer-distance along mechanism-sensitive axes, (d) the HARD-PASS threshold ABOVE which integration is justified. If the discriminator fails (NAIVE ~= REMEDY), pivot to the L7 alternatives for that gap rather than burn integration time.

2. **For Gap 1 specifically, dispatch the L7-Alt-1 (soft-feedback hop1->hop2) cell next.** Cost: ~1 cell-author hour. If it lifts NAIVE 2HOP 0.65 -> 0.78+, that is the genuine Gap 1 closure. If it fails, dispatch L7-Alt-2 (top-K consensus). If both fail, gap 1 is genuinely architectural-limit (per L5 category-theory boundary at N=8192), and the substrate-product story needs to either accept the 0.65 ceiling OR scale N to 65536.

3. **For Gaps 5 and 6, mark gap-map's Store solutions as INVALID and route to research for genuine architecture.** Gap 5: de-dup on random-bipolar is a no-op; the real solution is V_P expansion + orthogonalization (Gram-Schmidt or Hadamard predicate codebook). Gap 6: no Store cell genuinely proves multi-hop completion; this needs the L3/L4 soft-feedback or top-K consensus mechanism (same as Gap 1 family).

4. **Run Gap 4 (audit-trail) integration FIRST as the cheapest LOW-risk win.** Deterministic plumbing only; high P=0.85 closure; gives the Stage-1 substrate-product story the "auditable retrieval" pillar without depending on the gap-map transfer assumption.

5. **Adopt a META discipline going forward: "Store-proof regime annotation" is mandatory for every gap-map row.** The gap-map drill of 2026-06-24 listed Store cells without their (V, K, N, alpha, encoding) coordinates. Any future closure-prediction note must include those coordinates and quantify transfer-distance, otherwise the prediction is unbacked.

---

## FALSIFIABLE PREDICTIONS

### HARD-PASS (META verdict and per-gap reframing are correct)

HP1: Soft-feedback hop1->hop2 cell at M=500 / N=8192 / V_P=10 lifts 2HOP from 0.65 to >= 0.75 (passes Gap 1 with the L7-Alt-1 mechanism). Falsifies "Resonator was the right Gap 1 mechanism."
HP2: De-dup cell run on random-bipolar V_P=10 codebook (cosine threshold 0.95) returns 0 merges. Falsifies gap-map's "Gap 5 has Store solution"; confirms the no-op pattern.
HP3: Multi-hop completion at HOP=2 with naive sequential chain stays at 0.40 +- 0.03 across 3 seeds even after wiring wave14_multihop_hub_census + traceable_multi_hop. Confirms "Store does not actually contain a Gap 6 mechanism."
HP4: Gap 4 audit-trail integration achieves provenance >= 0.85 on first wire-up. Confirms LOW-risk per-gap classification.
HP5: Anisotropic-encoder + Resonator (L7-Alt-3) at M=500 / N=8192 lifts 2HOP from 0.65 to >= 0.72. Confirms the information-geometric explanation for the Resonator-failure-on-isotropic regime.

### HARD-FAIL (META verdict is wrong; gap-map's transfer assumption holds after all)

HF1: A re-run of resonator wire-up with N scaled to 32768 (4x) AND V_P=10 (unchanged) lifts 2HOP from 0.65 to >= 0.75. Would suggest the failure was an N-scaling issue, not a regime/anisotropy issue; reopen Resonator as Gap 1 closure with N scaling as the fix.
HF2: De-dup on V_P=10 at N=8192 actually finds >= 3 near-duplicates and lifts top1_chained by >= 0.05. Would suggest random-bipolar is NOT as orthogonal as the L6 analysis claims; reopen Gap 5 with the gap-map solution.
HF3: Naive sequential 2-hop achieves 0.80+ on the audit-trail-wired apples-to-apples cell (without any L7-Alt mechanism). Would suggest the apples-to-apples regime is itself buggy / over-easy; revisit cell discriminator before drawing META conclusions.
HF4: Soft-feedback variant gives the SAME 0.65 as hard-feedback NAIVE. Would suggest the multi-hop ceiling is at the encoder/storage level, not the decoder level; pivot the Gap 1 / 6 closure target to the encoding-drill mechanisms (hub-and-spoke, SoftHebb-deepened).

### Pre-registered HARD-FAIL thresholds (negativity-symmetric per [[feedback-negativity-bias-user-caught-5x-symmetric-verify-both-directions]])

If 4+ of HP1..HP5 fail, META verdict is wrong, gap-map approach is rescued. If 4+ pass, META verdict is confirmed and gap-map approach is dead as a closure-prediction tool.

---

## CROSS-THREAD SYNTHESIS

This is the THIRD failure-of-transfer in 5 days:
- 2026-06-20: research_negative_N6_resonator_dense_V100_HF_2x -- Resonator V=100 dense HF is algebraically expected by Frady-Sommer K_max; the "negative" was a regime issue, not a mechanism issue.
- 2026-06-23: research_2x_revival_comparator_resonator_HF -- Comparator primitive HF on smoke regime is the strictly-weaker-estimator pattern; smoke was too easy AND test was upstream of the real bottleneck.
- 2026-06-24 (today): Resonator integration cell HF on apples-to-apples regime is the same pattern: Store proof at one (V, K, N, anisotropy) point; today-cell at a different point; no transfer guarantee was checked.

**The convergent finding:** the substrate has a SYSTEMATIC drift wherein cells that work at one (V, K, N, anisotropy, dataset) point are claimed to "prove the mechanism" without specifying the regime envelope. This is the same META failure mode the Skunkworks cert-owner has caught Director on 4x in one session ([[feedback-fix28-violation-count-internalize-harder]]): over-claiming from verdict-summary text vs per-arm metrics. The gap-map drill instantiated it at the closure-prediction level. The fix is the discipline named in L7 strategy step 5.

**This also validates the encoding-drill direction** (research_optimal_substrate_encoding_design_space_2x_drill_2026-06-24): hub-and-spoke / sparse-with-amplitude / SoftHebb-deepened encoders create the anisotropic structure that L2 identified as a prerequisite for Resonator-family mechanisms to add value. The encoding-drill's "Path C substrate-owned encoder" is the SHARED foundation for closing multiple gaps; the gap-map's per-gap fixes are downstream of getting that right.

---

## SUBSTRATE-PRODUCT IMPLICATIONS

1. The "3-week integration closure" framing in director_stage1_closure_synthesis_2026-06-24 is unsupported. Replace with "per-gap discriminator + alternative-mechanism dispatch" cycle (estimated 2-4 weeks per HIGH-risk gap, 1-2 weeks per MEDIUM, 0.5 week for Gap 4).
2. The substrate-product story does NOT require all 7 gaps closed at Stage 1. Gap 4 (auditable retrieval) is the marquee differentiator vs vector-DBs and is the LOW-risk near-term win. Ship that first.
3. The Resonator-family is NOT the universal multi-hop mechanism. The substrate needs to adopt EITHER the encoding-drill's anisotropic encoder (enabling Resonator) OR the L7-Alt soft-feedback / top-K consensus mechanism (decoder-side). These are different research lanes; choose one or run both as parallel discriminator cells.
4. The gap-map should be RETIRED as a closure-prediction artifact and replaced with a per-gap discriminator cell pattern that pre-registers regime coordinates and transfer distance.

---

## CITATIONS (verified count: 21)

1. Assaying Out-Of-Distribution Generalization in Transfer Learning -- arxiv 2207.09239 (verified)
2. Quantifying and Improving Transferability in Domain Generalization -- arxiv 2106.03632 (verified)
3. Transfer Learning of Surrogate Models via Domain Affine Transformation -- arxiv 2501.14012 (verified)
4. Resonator Networks 2 Factorization Performance and Capacity (Frady-Kent-Olshausen-Sommer 2020) -- ar5iv 1906.11684; MIT direct neco/article/32/12/2332 (verified)
5. Recent Advances in Resonator Networks for Neuro-symbolic Computing -- openreview FNrZd3Ls1d (verified)
6. Neuromorphic visual scene understanding with resonator networks -- Nature Machine Intelligence s42256-024-00848-0 (verified)
7. Torchhd Python Library for HDC / VSA -- arxiv 2205.09208 (verified)
8. Asymptotics of Learning with Deep Structured Random Features (anisotropic MP) -- arxiv 2402.13999 (verified)
9. Gaussian Equivalence for Self-Attention Spectral Analysis -- arxiv 2510.06685 (verified)
10. Anisotropic semantic space and pathological similarity -- emergentmind.com/topics/anisotropic-semantic-space (verified)
11. Reasoning in Trees RT-RAG Multi-Hop QA -- arxiv 2601.11255 (verified)
12. PRISM Agentic Retrieval for Multi-Hop QA -- arxiv 2510.14278 (verified)
13. Generative Multi-hop Retrieval (Lee et al EMNLP 2022) -- aclanthology 2022.emnlp-main.92 (verified)
14. Matched-filter based iterative soft DIC -- researchgate 4019785 (verified)
15. Iterative Equalization With Soft Feedback -- researchgate 3156708 (verified)
16. Decision Feedback Equalizers overview -- sciencedirect engineering DFE topic (verified)
17. Categorial Compositionality (Phillips & Wilson) -- PMC 2908697 (verified)
18. Second-Order Systematicity of Associative Learning Coalgebraic Resolution -- PLOS ONE 10.1371/pone.0160619 (verified)
19. Hippocampus in transitive inference (Heckers) -- PMC 2693094 + PMC 2801762 + PMC 2858584 (verified, 3 sources)
20. Unsupervised Calibration under Covariate Shift -- arxiv 2006.16405 (verified)
21. On Calibration and Out-of-domain Generalization -- arxiv 2102.10395 (verified)

Substrate-internal anchors (not external citations, for cross-thread synthesis):
- research_negative_N6_resonator_dense_V100_HF_2x_2026-06-20 (Frady-Sommer K_max algebra)
- research_2x_revival_comparator_resonator_HF_2026-06-23 (strictly-weaker-estimator pattern)
- director_stage1_gap_to_existing_solution_map_2026-06-24 (the gap-map under audit)
- director_stage1_closure_synthesis_2026-06-24 (the 3-week plan under audit)
- research_optimal_substrate_encoding_design_space_2x_drill_2026-06-24 (encoding lane for anisotropic-encoder path)
- substrate_72b_R0R1R2_claim12_tier_proof_walk_cpu_v1 (confidence-tier gating chain-grade)
- exp_pointer_chain (HARD_PASS depth 100; non-compositional escape hatch)
- exp_substrate_iterative_multihop_pretest_v1 (HARD_FAIL; the hard-feedback variant that exists in Store)

End of drill.
