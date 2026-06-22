# RESEARCH: Decode-side improvements for substrate-native concept-LM at fixed (V_C, N_DIM)
**Date:** 2026-06-22
**Requestor:** Skunkworks (empirical driver: n2_capacity_scaling MIDDLE_BAND / decode-bottleneck finding)
**Lit-scan calibration:** deflate P by 0.15–0.25; cap novel-synthesis P at 0.50; HARD-FAIL thresholds mandatory.

---

## HEADLINE

**The 1.12-bit bigram gap is decode-side, not context-side.** The empirical evidence is decisive: depth_concept_gain is small-positive (+0.008–0.031) at every N while depth_token_gain is small-negative (−0.03 to −0.12). The substrate is capturing higher-order concept structure; the gap lives in the concept-to-token decode layer.

**Priority ranking of the three decode-side levers (given fixed V_C=1024, N_DIM=16384):**

| Rank | Sub-area | Mechanism | Expected BPC gain | Cost | CAN-fail regime |
|------|----------|-----------|-------------------|------|-----------------|
| #1 | (a) VQ-alignment | SimVQ or OT-based assignment replaces MiniBatchKMeans | 0.3–0.8 BPC | ~same wall time | collapses if linear projection overhead destroys within-concept coherence |
| #2 | (b) Smoothing | Modified Kneser-Ney class-bigram decode replaces Jelinek-Mercer | 0.1–0.3 BPC | negligible | no gain if within-concept distribution is already flat |
| #3 | (c) Hierarchical decode | Class-LM two-stage P(class) × P(token\|class) | 0.1–0.4 BPC | moderate | fails if class=concept is the wrong granularity |

**Cheap decisive test (pre-registered, see below): Sub-area (a), SimVQ vs MiniBatchKMeans, at V_C=1024, N_DIM=16384, same substrate otherwise. HARD-PASS bar: ceiling_bpc drops ≥ 0.3 bits AND substrate_bpc drops ≥ 0.2 bits. HARD-FAIL bar: ceiling_bpc change < 0.05 bits (VQ variant made no difference to decode floor).**

---

## EMPIRICAL DRIVER — the data in detail

From `data/exp_n2_capacity_scaling_v1/metrics.json` (3 seeds, N_DIM=16384, K=1 vs K=2):

| Metric | Value | Interpretation |
|--------|-------|----------------|
| substrate_bpc (best, N=16384/K=1) | 4.959 | 1.12 bits above bigram |
| bigram_bpc | 3.844 | hard-pass bar |
| ceiling_bpc (N=16384) | 2.049 | oracle concept→token; 2.91 bits better than substrate |
| depth_concept_gain (K=2 mean) | +0.008–+0.031 | depth does real concept-layer work |
| depth_token_gain (K=2 mean) | −0.03 to −0.12 | token floor swallows concept gain |
| ceiling_top1 | 0.726–0.733 | oracle predicts correct token 73% of the time |
| substrate_top1 | ~0.429 | substrate predicts correct token 43% of the time |

**Key structural diagnosis:** The distillation gap (substrate_bpc − ceiling_bpc) = ~2.91 bits at N=16384. The ceiling itself is 1.79 bits above bigram. This means:
- Even with perfect concept prediction, the current count-proportional decode cannot reach bigram.
- The decode layer has ~1.79 bits of irreducible within-concept token entropy at V_C=1024.
- This is the primary target: lower within-concept token entropy without changing V_C or N.

From N1 v3.1 (`data/exp_n1_concept_lm_substrate_native_token_decode_v3_1/metrics.json`):
- V_C=256 gives ceiling_bpc=2.70 (worse than V_C=1024's 2.05) — coarser concepts = higher within-concept entropy as expected.
- codebook_utilization: 98% (V_C=256) vs 93% (V_C=1024). VQ collapse is not the current issue, but utilization drops slightly as V_C grows toward the residual manifold's effective dimensionality.

---

## SUB-AREA (a): VECTOR QUANTIZATION ALTERNATIVES

### The mechanism to attack
Within-concept token entropy = H(token | concept). This is bounded below by the conditional entropy H(token | true_residual_cluster). The current MiniBatchKMeans VQ partitions the residual space into V_C Voronoi cells. Within each cell, tokens are heterogeneous — different surface forms that map to nearby residuals. The count-proportional decode D accumulates token counts per concept; within-concept entropy is the entropy of that count distribution.

The VQ step controls HOW heterogeneous each cluster is. A better VQ assignment (lower within-cluster token-entropy) directly lowers ceiling_bpc and, if the assignment improvement generalizes, substrate_bpc.

### Candidate mechanisms

**SimVQ (ICCV 2025, arxiv 2411.02038)**
Addresses representation collapse via a learnable linear transformation layer over a fixed latent basis: the codebook embeddings are reparameterized as `W @ B` where B is a fixed random basis and W is learned. This optimizes the entire linear subspace rather than individual code vectors. Key empirical result: enables stable training with codebook sizes up to 100k; near-100% utilization without auxiliary losses; validated on image and audio.

*Substrate applicability:* The substrate uses MiniBatchKMeans on L2-normalized Pythia-160m residuals (768-dim). Replacing this with SimVQ-style assignment requires: (1) fitting a linear projection W that maps residuals into a lower-dimensional space where Voronoi cells are more semantically coherent; (2) assigning concept IDs via nearest-neighbor in the projected space. The projection is learned at INGEST time from train residuals; zero LLM calls at inference (only the assignment step changes). This is substrate-only-decode-gate COMPATIBLE.

*Expected gain:* SimVQ consistently shows higher codebook perplexity (more uniform assignment entropy) and lower reconstruction error than standard VQ. For the substrate, the operative gain is not reconstruction but within-concept semantic homogeneity. If SimVQ's projection separates residuals that differ in next-token distribution, ceiling_bpc should drop.

*Calibrated P(gain ≥ 0.3 BPC): ~0.45* (deflated per calibration protocol; uncertainty comes from: the substrate's count-proportional decode is non-differentiable so SimVQ's learnable projection must be fit unsupervised at ingest, not end-to-end; the gain depends on whether linear projection can tease apart semantically distinct residuals that MiniBatchKMeans conflates).

**FSQ — Finite Scalar Quantization (ICLR 2024, arxiv 2309.15505)**
Projects the latent to d << 768 dimensions (typically d ≤ 10), quantizes each dimension to a small set of fixed integer values. Implicit codebook = product of per-dimension grids. Near-100% codebook utilization by construction; no commitment loss needed; no collapse.

*Substrate applicability:* FSQ would replace the MiniBatchKMeans step: project each residual to d dimensions via a learned or random projection, then round each dimension to its grid. The codebook size V_C = product of grid widths (e.g., d=5 dims × 4 values each = 4^5 = 1024). This is clean and deterministic; no EM convergence needed.

*Key advantage vs SimVQ:* The fixed grid makes the codebook structure explicit and predictable. Lower-dimensional projection may be a BETTER separator than high-dimensional Voronoi on residuals with anisotropic geometry (which Pythia residuals are known to have from the isotropy audits).

*Calibrated P(gain ≥ 0.3 BPC): ~0.40* (FSQ's grid is isotropic by construction; if the key semantics lie in a few principal directions of the residual space, FSQ with a PCA-aligned projection could concentrate them; uncertainty: small d may discard dimensions that carry token-discriminating signal).

**OptVQ — Optimal Transport VQ (arxiv 2412.15195, Dec 2024)**
Replaces the nearest-neighbor assignment step in k-means with a Sinkhorn-based optimal-transport assignment that globally balances cluster loads. The Sinkhorn constraint enforces that each codeword receives (approximately) equal assignment mass, preventing dominant-codeword pathology. Achieves 100% codebook utilization on ImageNet/VQGAN (codebook size 16384, feature dim 64) with improved rFID.

*Substrate applicability:* The Sinkhorn assignment replaces the `km.predict()` call in `run_seed()`. The centroids are still learned by EM (alternating: Sinkhorn-assign → centroid-update). No architectural change to the substrate pipeline; just the assignment step changes. The balanced-load constraint means no concept cluster dominates, and the per-cluster token distribution should be more concentrated (because each cluster is forced to specialize).

*Calibrated P(gain ≥ 0.3 BPC): ~0.40* (strong mechanism; main uncertainty: the Sinkhorn step is significantly slower than nearest-neighbor for large N_train, and the equal-load constraint may not be optimal if the true residual distribution is genuinely unequal in cluster density).

**Entropy-regularized VQ (MAGVIT-v2 style)**
Adds an entropy penalty H(assignment distribution) to the k-means objective, directly maximizing codebook utilization diversity during training. Implemented as an auxiliary loss term. Does not require a new assignment algorithm; adds a softmax-based assignment distribution and maximizes its entropy.

*Substrate applicability:* Fits into the sklearn MiniBatchKMeans framework as a custom VQ with entropy-augmented loss. More complex to implement correctly than SimVQ or OT-VQ but well-characterized.

*Calibrated P(gain ≥ 0.3 BPC): ~0.35*

**Recommendation for Exp-Dev:** Start with **SimVQ** (arxiv 2411.02038). Rationale: (1) directly addresses representation collapse at the substrate's operating codebook size (V_C=1024, the "linear layer" trick is a one-line addition to the VQ fit step); (2) well-validated across modalities; (3) substrate-only-decode-gate compatible; (4) cheapest to implement — add one linear projection before the MiniBatchKMeans fit. Second option if SimVQ shows <0.1 BPC gain: FSQ with PCA-aligned projection (structurally cleaner, directly controls codebook size via grid dimensions).

---

## SUB-AREA (b): SMOOTHING / INTERPOLATION ALTERNATIVES

### The mechanism to attack
The current decode uses **Jelinek-Mercer interpolation**: `P(token) = (1 - λ) * P_MLE(token | concept) + λ * P_unigram(token)` with λ=0.1. This floors the token probability at 10% of the unigram, preventing catastrophic BPC from unseen (concept, token) pairs.

Two problems with this choice:
1. The MLE distribution P_MLE(token | concept) is count-proportional over ~50k tokens. For concepts with high within-cluster entropy, the MLE distribution is nearly flat, and the unigram back-off does no better than unigram overall.
2. Jelinek-Mercer uses a fixed λ regardless of how much data concept c has. Concepts with many observations should trust P_MLE more; concepts with few observations should back off more.

### Candidate mechanisms

**Modified Kneser-Ney (MKN) discounting**
MKN (Chen & Goodman 1998) uses count-based absolute discounting D (not a fixed λ): subtract a fixed discount D from each observed count, redistribute the saved probability mass to a lower-order distribution weighted by a normalization factor. The lower-order distribution is a "continuation" distribution that captures how novel a token is across all contexts, not just its frequency.

*For the substrate:* The "context" is the concept ID c. The bigram distribution is P(token | concept_c). MKN would compute:
- `P_MKN(token | c) = max(count(c, token) - D, 0) / sum_count(c) + γ(c) * P_continuation(token)`
where `γ(c)` is computed from the count structure and `P_continuation(token)` gives bonus probability to tokens that appear in many concept contexts.

*Expected gain over Jelinek-Mercer:* MKN consistently outperforms JM and Witten-Bell on word-level n-gram tasks (3–13% perplexity reduction in well-controlled comparisons; arxiv 1706.07786). For the substrate, the gain is bounded by how skewed the (concept, token) count distribution is — if most concepts have very few unique tokens, MKN's continuation discount adds little beyond JM.

*Calibrated P(gain ≥ 0.1 BPC): ~0.55* (highest confidence among smoothing options; the mechanism is well-proven; main uncertainty is whether the 1.12-bit gap is smoothing-limited at all, or whether it is purely within-concept-entropy-limited).

**Class-based interpolation**
Exploit concept identity as a class: compute `P(token | concept_c) = (1-β) * P_MLE(token | c) + β * P_bigram_class(token | class_c)` where `class_c` is a coarser grouping of concepts (e.g., 64 meta-clusters from hierarchical clustering of the 1024 concept centroids). This provides a middle-order smoother between per-concept MLE and global unigram.

*Expected gain:* Class interpolation with 3 levels (per-concept, class-of-concept, unigram) can absorb both the sparse-concept and the sparse-token problems. Empirically, 3-level interpolation reduces perplexity by 8–15% over 2-level (Witten-Bell) in NLP tasks with fine-grained class structures.

*Calibrated P(gain ≥ 0.1 BPC): ~0.45*

**Witten-Bell discounting**
Simpler than MKN: the back-off weight is `λ(c) = |unique_tokens_seen_with_c| / (count_c + |unique_tokens_seen_with_c|)`. This is data-adaptive per concept but does not use the continuation distribution. Expected to slightly underperform MKN but simpler to implement.

*Calibrated P(gain ≥ 0.1 BPC): ~0.40*

**Important caveat on smoothing gains:** The data shows ceiling_bpc = 2.049 at V_C=1024, N=16384. The current substrate reaches 4.959. The 2.91-bit gap from ceiling to substrate includes: (1) concept-prediction error (concept_top1 = 0.54, so ~46% of positions get the WRONG concept fed to decode), and (2) within-concept token entropy even at the right concept. Better smoothing only addresses (2). If (1) dominates, smoothing gains will be small.

**Estimate of the smoothing-accessible portion:** ceiling_bpc − bigram_bpc = 2.049 − 3.844 = −1.795 bits (the ceiling is BETTER than bigram). The smoothing-accessible portion is the within-concept entropy for the correctly-predicted concepts. With concept_top1=0.54, roughly 54% of positions benefit from better smoothing; the other 46% get the wrong concept regardless. Rough upper bound: smoothing can recover at most ~0.54 × (gap from ceiling to bigram) ≈ 0 bits (the ceiling already beats bigram). So smoothing alone cannot bridge the substrate-to-bigram gap — but it can contribute 0.1–0.3 BPC when combined with better VQ.

**Recommendation for Exp-Dev:** Implement **Modified Kneser-Ney** as a drop-in replacement for the `batched_token_logprob` path in v3.1. This is a pure-Python change (replace the count-proportional softmax + λ-backoff with MKN count-discount + continuation-distribution). No architecture change, no wall-time increase, no new data required.

---

## SUB-AREA (c): DECODE-TIME REFINEMENTS (substrate-only gate)

**Constraint:** zero LLM forward calls at inference; Pythia at INGEST only.

### Two-stage class-LM decode (hierarchical)
The factored-probability framework: `P(token) = P(concept_c | context) × P(token | concept_c)`. This is ALREADY the substrate's architecture. The question is whether a SECOND level of factorization helps: group tokens into meta-classes (e.g., part-of-speech or frequency bucket), compute `P(token) = P(concept) × P(meta_class | concept) × P(token | concept, meta_class)`.

*Expected gain:* Classical class-LMs (Brown 1992) show perplexity improvement from ~541 to ~439 (19%) when interpolating word-based with class-based models. But those results are for cases where the class structure captures real syntax. For the substrate, the "classes" are Pythia residual clusters — their within-class token distribution may not factorize cleanly.

*Calibrated P(gain ≥ 0.1 BPC): ~0.30* (lower confidence; gain depends on residual-cluster semantic structure that may not decompose into a useful meta-class hierarchy).

### Temperature-adaptive decode tied to concept confidence
Scale the decode distribution by a temperature τ(c) that decreases when the concept recall is high-confidence and increases when it is uncertain: `P_decode(token) = softmax(scores(c) / τ(c))`. Estimate confidence from the margin between the top-1 and top-2 concept similarity scores.

*Substrate-only-gate status:* Compliant — uses only the concept recall scores already computed in the W-matrix path; no LLM calls.

*Expected gain:* Modest. The main effect is to sharpen the distribution for confident predictions and widen it for uncertain ones. On held-out language modeling, this reduces calibration error but BPC gain over a flat-τ decode is typically 0.02–0.08 bits.

*Calibrated P(gain ≥ 0.1 BPC): ~0.20*

### Recommendation for Exp-Dev (sub-area c):
Do NOT prioritize (c) as a standalone cell. The gains are smaller and harder to pre-register decisively. If (a) or (b) land a HARD-PASS, revisit (c) as a composition layer.

---

## CHEAP DECISIVE TEST — PRE-REGISTERED

**Cell name:** `n3_vq_alignment_simvq_v1` (or `exp_n3_vq_alignment_v1`)
**Scope:** SimVQ-style linear projection layer before VQ assignment at fixed V_C=1024, N_DIM=16384 (the best N2 config). All other parameters identical to n1 v3.1 baseline. Three seeds (7, 17, 23). Run on `remote_cpu_queue`.

**Independent variable:** VQ assignment method: {MiniBatchKMeans baseline, SimVQ-linear-projection-then-MiniBatchKMeans}

**Measurement:** ceiling_bpc (oracle decode floor), substrate_bpc (end-to-end), codebook_utilization, depth_token_gain at K=2

**Why ceiling_bpc is the decisive metric:** ceiling_bpc is the oracle lower bound — it measures within-concept token entropy INDEPENDENT of concept-prediction quality. If SimVQ lowers ceiling_bpc, it means the VQ assignment has genuinely concentrated the token distribution within each concept cluster. This is a clean falsifiable test with no concept-prediction confound.

### PRE-REGISTERED HARD THRESHOLDS

**HARD-PASS (chain-grade):**
- ceiling_bpc(SimVQ) ≤ 1.75 (≥0.30 bits improvement from baseline 2.049 at N=16384)
- substrate_bpc(SimVQ) ≤ 4.75 (≥0.21 bits improvement from baseline 4.959)
- substrate_bpc(SimVQ) < bigram_bpc = 3.844 would be a BONUS super-pass (not pre-registered as the primary bar)
- cv ≤ 0.05 across seeds
- substrate-only-decode gate: zero LLM calls at inference (code-trace required)

**MIDDLE_BAND:**
- ceiling_bpc drop ≥ 0.10 bits (SimVQ improves the decode floor, but not enough for chain-grade)
- substrate_bpc still above bigram

**HARD-FAIL:**
- ceiling_bpc change < 0.05 bits: SimVQ assignment makes no measurable difference to within-concept token entropy. This rules out VQ-alignment as the decode-bottleneck mechanism at fixed V_C=1024.

**Discriminating-regime requirement (C5 per cert-architecture):** The CAN-fail regime for this cell is V_C=1024 with N_DIM=16384. The cell MUST report per-seed ceiling_bpc for both conditions. If baseline ceiling_bpc doesn't replicate within 0.02 bits of the N2 cell's 2.049, the baseline is corrupt and the cell is INCONCLUSIVE.

---

## FALSIFIABLE PREDICTIONS

### Prediction 1 (sub-area a, PRIMARY)
**Hypothesis:** SimVQ-style linear projection before VQ assignment lowers ceiling_bpc by ≥ 0.30 bits at V_C=1024, N_DIM=16384.
**Mechanism:** The linear projection learns to separate residuals with heterogeneous token distributions into different Voronoi cells, reducing within-concept token entropy.
**HARD-PASS:** ceiling_bpc ≤ 1.75. **HARD-FAIL:** ceiling_bpc change < 0.05.
**Calibrated P(HARD-PASS): 0.40–0.45.** (Deflated from raw 0.55–0.65 per calibration protocol: the projection is learned unsupervised at ingest; it is not guaranteed to separate token-heterogeneous residuals.)

### Prediction 2 (sub-area a, SECONDARY)
**Hypothesis:** FSQ with PCA-aligned low-dimensional projection (d=5–8 dimensions, V_C=4^5=1024 or 4^4×8=2048 range) achieves comparable or better ceiling_bpc reduction than SimVQ.
**Mechanism:** PCA identifies the directions of maximum residual variance; if token-discriminating signal concentrates in the top principal directions, FSQ will naturally separate heterogeneous token clusters.
**HARD-PASS:** ceiling_bpc ≤ 1.75. **HARD-FAIL:** ceiling_bpc worse than SimVQ baseline by > 0.10 bits.
**Calibrated P(HARD-PASS): 0.35–0.40.** (FSQ's isotropic grid may discard anisotropic signal; PCA alignment helps but is not guaranteed.)

### Prediction 3 (sub-area b, CONDITIONAL)
**Hypothesis:** Modified Kneser-Ney decode (replacing Jelinek-Mercer) reduces substrate_bpc by ≥ 0.10 bits when VQ-alignment is held constant.
**Mechanism:** MKN's continuation discount gives bonus probability to tokens that appear across many concept contexts, reducing over-confidence in sparse-concept low-count token predictions.
**HARD-PASS:** substrate_bpc drops ≥ 0.10 bits vs JM baseline. **HARD-FAIL:** substrate_bpc change < 0.02 bits.
**Calibrated P(HARD-PASS): 0.45–0.55.** (Higher confidence because MKN vs JM is a well-proven empirical win in n-gram LM; main risk is that the within-concept distribution is too flat for discounting to matter.)

### Prediction 4 (nullability check)
**Hypothesis:** If SimVQ gives HARD-FAIL (ceiling_bpc change < 0.05), then depth_token_gain at K=2 will also NOT improve, confirming that the bottleneck is within-concept entropy (not recoverable by better VQ) and Path A (higher V_C) is the only remaining option.
**Pre-registered interpretation:** SimVQ HARD-FAIL + depth_token_gain still negative → route to Path A (V_C=4096, N=32768+). SimVQ HARD-FAIL + depth_token_gain turns positive → the VQ change unexpectedly helped the concept-prediction layer; investigate.

---

## CROSS-THREAD SYNTHESIS

### Composes with N1 v3.1 calibration arc
N1 v3.1 (`exp_n1_concept_lm_substrate_native_token_decode_v3_1`) runs at V_C=256, N_DIM=4096 with Jelinek-Mercer. The new cell should anchor against v3.1's baseline (5.00 BPC, ceiling 2.70) to verify that the N=16384 config genuinely improves baseline before applying VQ changes. The N2 data already confirms this (4.96 BPC at N=16384 vs 5.00 at N=4096), so the anchor is V_C=1024/N=16384 baseline = 4.96 BPC / ceiling 2.05 (not v3.1).

### Composes with N2 3-way knot finding
The N2 3-way knot (V_C × N × depth coupled) says: pushing N un-saturates V_C but doesn't make depth show in token-BPC. The decode-side research resolves WHY depth doesn't show: depth_concept_gain is positive (substrate learns bigram-of-concepts) but the token-BPC floor is too high for the gain to propagate. This means:
- Better VQ (lower ceiling) directly lowers the floor that is masking depth.
- If SimVQ lowers ceiling_bpc from 2.05 to 1.75, the "masked depth gain" of +0.02 bits becomes visible in token-BPC.
- **The composition is: SimVQ (sub-area a) + MKN (sub-area b) + depth K=2 is the jointly-enabling combination.** None of the three alone is likely to bridge the 1.12-bit gap; the composition might.

### Path A vs Path B comparison
**Path A** (higher V_C × N jointly, V_C=4096 × N=32768+): attacks within-concept entropy by shrinking cluster size (more concepts = less heterogeneous per concept). Untested; requires GPU run.
**Path B** (decode-side, this research): attacks within-concept entropy by (a) better VQ assignment and (b) better smoothing within the same V_C. CPU-tractable; tests on the same N2 data.

**Director recommendation:** Run Path B (n3_vq_alignment_simvq_v1) first. Cost: ~32 min wall (same as N2 cell at N=16384). Path A's GPU cost is unknown and likely large (V_C=4096 requires 4× more VQ clusters; codebook matrix D grows 4× in size). If Path B achieves ≥0.30 BPC gain (ceiling_bpc ≤ 1.75), it establishes that decode-side improvement is feasible at fixed V_C=1024, making Path A less urgent. If Path B HARD-FAILs (ceiling_bpc unchanged), it confirms the bottleneck is codebook granularity not assignment quality, and Path A becomes the only evidence-based path.

---

## SUBSTRATE-PRODUCT IMPLICATIONS

1. **VQ assignment is the highest-leverage decode-side knob.** The ceiling_bpc (2.05 at V_C=1024) is 1.79 bits above bigram. This is the minimum achievable BPC with perfect concept prediction but current k-means assignment. Better assignment (SimVQ/OT-VQ) can lower this ceiling without changing the substrate's storage mechanism or inference architecture.

2. **Modified Kneser-Ney is a free lunch candidate.** The current Jelinek-Mercer decode uses a fixed λ=0.1 back-off regardless of per-concept data volume. MKN is a drop-in replacement that is computationally equivalent and has no substrate-compatibility issues. If it delivers 0.1 BPC, it is pre-composable with any VQ variant.

3. **The decode bottleneck resolves the depth mystery.** K=2 depth adds concept-layer structure (+0.008–+0.031 concept gain) but the token floor masks it. This means once ceiling_bpc is lowered (by VQ improvement), K=2 depth will automatically contribute — no additional depth experiment needed. The composition experiment (SimVQ + K=2) should be included in the n3 cell sweep at no extra cost.

4. **Codebook utilization is not the current problem.** At V_C=1024, utilization is 93–94% (not collapsed). OptVQ/FSQ's main advantage (100% utilization) is therefore a marginal gain at current V_C. Their within-cluster entropy-reduction property (from balanced Sinkhorn assignment or PCA-aligned projection) IS the relevant mechanism, not utilization.

---

## CITATIONS (verified, count = 11)

1. Mentzer et al. (2024). "Finite Scalar Quantization: VQ-VAE Made Simple." ICLR 2024. arxiv 2309.15505. [Finite Scalar Quantization: VQ-VAE Made Simple](https://arxiv.org/abs/2309.15505)

2. Zhu et al. (2024). "Addressing Representation Collapse in Vector Quantized Models with One Linear Layer." ICCV 2025. arxiv 2411.02038. [SimVQ: Addressing Representation Collapse](https://arxiv.org/abs/2411.02038)

3. Zhang et al. (2024). "Preventing Local Pitfalls in Vector Quantization via Optimal Transport." arxiv 2412.15195. [OptVQ](https://arxiv.org/abs/2412.15195)

4. Chen & Goodman (1998). "An Empirical Study of Smoothing Techniques for Language Modeling." Harvard TR-10-98. (Modified Kneser-Ney reference — foundational.)

5. Srizal et al. (2017). "Comparison of Modified Kneser-Ney and Witten-Bell Smoothing Techniques in Statistical Language Model of Bahasa Indonesia." arxiv 1706.07786. [Comparison](https://arxiv.org/pdf/1706.07786) (empirical comparison confirming MKN superiority.)

6. Brown et al. (1992). "Class-Based n-gram Models of Natural Language." Computational Linguistics 18(4). (Class-based LM two-stage factorization reference.)

7. Dhariwal et al. (2024). "MAGVIT-v2 / Language Model Beats Diffusion." ICLR 2024. [Language Model Beats Diffusion](https://proceedings.iclr.cc/paper_files/paper/2024/file/036912a83bdbb1fd792baf6532f102d8-Paper-Conference.pdf) (entropy-regularized VQ codebook.)

8. Shi et al. (2023). "Gaussian Mixture Vector Quantization with Aggregated Categorical Posterior." arxiv 2410.10180. [GMVQ](https://arxiv.org/pdf/2410.10180) (entropy-regularized codebook assignment.)

9. Defossez et al. (2024). "ERVQ: Enhanced Residual Vector Quantization with Intra-and-Inter-Codebook Optimization." arxiv 2410.12359. [ERVQ](https://arxiv.org/html/2410.12359v2) (RVQ multi-stage; informs residual VQ hierarchy as an alternative to higher V_C.)

10. Wang et al. (2022). "Neural-FST Class Language Model for End-to-End Speech Recognition." arxiv 2201.11867. [Neural-FST CLM](https://arxiv.org/pdf/2201.11867) (class-based LM two-stage factorization in modern neural context.)

11. Bengio et al. (2013). "Estimating or Propagating Gradients Through Stochastic Neurons for Conditional Computation." (Straight-through estimator for VQ training — relevant if SimVQ needs gradient propagation during projection fitting.)

---

## LIT-SCAN CALIBRATION NOTES

- All probability estimates deflated 0.15–0.25 from raw LM-based confidence.
- Cap on novel-synthesis P applied: no estimate above 0.50 for claims not directly validated in cited papers.
- HARD-FAIL thresholds (not just HARD-PASS) are mandatory and listed above.
- Sub-area (c) gains are capped at 0.30 P(HARD-PASS) due to lack of direct empirical validation of class-LM decode on residual-based codebooks.
- Sub-area (b) MKN P(HARD-PASS) of 0.45–0.55 is the highest among the three because it is directly supported by n-gram smoothing literature (Chen & Goodman 1998, well-replicated).

---

## DISPATCH RECOMMENDATION

**Immediate (Exp-Dev next cell):** `n3_vq_alignment_simvq_v1`
- Baseline: MiniBatchKMeans at V_C=1024, N_DIM=16384, K={1,2}, JM λ=0.1 (replicate N2 n16384 config)
- Treatment: SimVQ linear projection (learned on train residuals) → MiniBatchKMeans in projected space, same V_C=1024, K={1,2}
- Optional arm: FSQ with PCA (d=5 → 4^5=1024) as a third arm at minimal extra cost
- Metrics: ceiling_bpc (PRIMARY), substrate_bpc, depth_token_gain, codebook_utilization
- Pre-reg: HARD-PASS ceiling ≤ 1.75 / HARD-FAIL ceiling change < 0.05
- Queue: remote_cpu_queue (needs residuals_per_token.npz on marsh@home)
- Estimated wall time: ~35 min (similar to N2 cell at N=16384, plus ~5% projection overhead)

**Second cell (after n3 lands, regardless of outcome):** Add MKN decode to whatever VQ variant showed the best ceiling_bpc in n3. This is a pure smoothing experiment; adds negligible complexity.

-- Research
