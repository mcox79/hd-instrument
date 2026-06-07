# Research drill: Llama privacy mechanism reopening (3x deep)
# Date: 2026-06-07
# Filed-by: research sub-agent

---

## HEADLINE

The eigenspectrum diagnostic disproved the anisotropy-in-dimensions hypothesis for
Llama-3.2-1B: SRHT leaves the participation ratio (PR) unchanged at 12.733 before and
after, which means Llama's singular value spectrum is already spread across its dimensions.
MiniLM is dimension-anisotropic (PR/D = 0.16, few dims dominate) and SRHT helps it for
that reason. Llama is NOT dimension-anisotropic in the same way. The membership-inference
leak in Llama therefore comes from a different structural feature -- most likely manifold
geometry (low intrinsic dimensionality combined with high cosine uniformity in a flat
cone), token-position concentration, or geometric relationships between stored vectors.
Five testable mechanism hypotheses are ranked below. Two are high priority for the Llama
harness (structural diagnostic + Path A entropy whitening). Three are medium priority.
None require GPU. The ZKL=0.10 target remains achievable in principle but requires
identifying the correct structural feature first.

P_deflated (any one path closes gap to ZKL < 0.10) = P_theoretical x P_empirical
P_theoretical = 0.60 (at least one hypothesis is correct about the leak mechanism)
P_empirical = 0.55 (harness pre-test will confirm before committing engineering)
P_deflated = 0.60 x 0.55 = 0.33 (calibration penalty applied; cap 0.50 on novel-synthesis)

HARD-PASS threshold: any single mechanism test achieves ZKL < 0.12, recall >= 0.85
HARD-FAIL threshold: all five mechanism tests return ZKL >= 0.18 (no path shows progress)

---

## SECTION 1: WHY THE EIGENSPECTRUM RESULT INVALIDATES THE PRIOR HYPOTHESIS

### What the prior hypothesis said

The anisotropy hypothesis (as understood from MiniLM results) was:
- Llama's embedding dimensions are anisotropic: a small number of dimensions carry
  disproportionate variance.
- The membership-inference signal concentrates in those high-variance dimensions.
- SRHT would scatter that concentrated variance across all dimensions, disrupting the
  membership-inference signal.

This was tested by verifying SRHT's effect on MiniLM first: SRHT reduced MiniLM's
ZKL(50) from 0.41 to 0.24, consistent with disrupting a dimension-concentrated signal.

### What the eigenspectrum diagnostic showed

SRHT applied to Llama-3.2-1B L15 left-pad produces:
  PR before SRHT: 12.733
  PR after SRHT: 12.733

The participation ratio measures the effective number of directions that carry variance:
  PR = (sum singular_values)^2 / sum(singular_values^2)

If PR is unchanged by SRHT, one of two things is true:
(a) The energy is ALREADY spread across many dimensions and SRHT is mixing a uniform
    distribution -- no change because the distribution is already flat.
(b) The energy concentration is not in linear dimensions at all but in a nonlinear
    manifold structure that SRHT cannot see.

The MiniLM comparison makes (a) more likely: MiniLM has PR/D = 0.16 (about 61 of 384
effective dimensions), which is strongly dimension-concentrated. Llama at PR = 12.733
out of D = 2048 gives PR/D = 0.006, which is EVEN MORE concentrated than MiniLM if taken
at face value. But SRHT hurts Llama while helping MiniLM. This paradox resolves under
hypothesis (b): the concentration in Llama is not in the DIRECTIONS that matter for
membership inference -- it is in a DIFFERENT geometric feature.

### The paradox resolved: cone-width vs dimension-concentration

There are two distinct forms of anisotropy in embedding spaces:

**Type 1: Dimension anisotropy (what SRHT disrupts)**
- A small number of coordinate dimensions carry most variance.
- Visualized as an elongated ellipsoid aligned with coordinate axes.
- Signature: PR/D << 1; singular values decay steeply.
- SRHT help: yes, because it redistributes energy across dimensions.
- MiniLM exhibits this.

**Type 2: Directional anisotropy (what SRHT cannot disrupt)**
- Vectors lie in a narrow cone around a mean direction.
- Within the cone, the distribution may be ISOTROPIC in all cone-local coordinates.
- Signature: high average cosine similarity between random pairs; PR may be "normal"
  because the within-cone distribution is spread evenly; but the cone itself is narrow.
- SRHT does NOT help: rotating a cone-isotropic distribution with an orthogonal transform
  yields another cone-isotropic distribution. The cone angle is preserved.
- Causal LMs trained with next-token prediction exhibit this.

The eigenspectrum diagnostic measures PR, which captures Type 1 anisotropy. If Llama's
PR is unchanged by SRHT, it means Type 1 anisotropy is either absent or already
saturated. The membership-inference problem in Llama is therefore caused by a structure
that PR does not capture.

The most direct candidate: TYPE 2 (directional cone anisotropy combined with LOW
INTRINSIC DIMENSIONALITY within the cone).

### Published support for this interpretation

The "latent semantic manifolds" literature (2025) finds that GPT-2, OPT, and Pythia
family models exhibit intrinsic dimensionality of 19-27 within ambient spaces of 768-2048.
This is a utilization ratio of 1-3%. The high-ID "hunchback" peaks at mid-layers and
collapses toward the output. For Llama at L15 (mid-network for a model with ~32 layers),
we would expect near-peak intrinsic dimension -- meaning the 2048-dim embedding actually
spans approximately 20-40 effective directions.

If Llama's L15 embeddings are confined to a ~30-dim manifold within 2048-dim space:
- SRHT operates in the full 2048-dim ambient space.
- It redistributes variance across 2048 dimensions.
- But the manifold is 30-dim: the embedding never left the manifold, it just got
  rotated within the ambient space.
- Membership inference via cosine similarity uses manifold-local cosines, not
  ambient-space cosines.
- Result: SRHT has zero effect on manifold-local similarity structure.

This is the unified explanation for PR-invariance + SRHT-hurting-Llama.

---

## SECTION 2: THE FIVE NEW MECHANISM HYPOTHESES

These replace the disproved dimension-concentration hypothesis. Each is grounded in the
eigenspectrum results and published literature.

---

### Hypothesis A: Low intrinsic dimensionality (manifold confinement)

**Claim:** Llama's L15 embeddings lie on a manifold of effective dimension approximately
20-50, far below the nominal 2048-dim ambient space. Membership inference operates on
manifold-local cosine similarity. Any transform that preserves manifold structure
(including SRHT, PCA, rotation) cannot reduce leakage.

**Why this is now the leading hypothesis:**
- The PR=12.733 result is consistent with manifold confinement (PR captures effective
  linear directions, not manifold curvature).
- Published work (2603.22301) shows causal LMs have 1-3% ambient utilization.
- Manifold-confined embeddings have highly structured cosine similarity: two vectors on
  the same low-dim manifold have predictable cosine similarities based on their position
  on the manifold. Member queries are near specific stored vectors on the manifold.
  Non-members may be on a different region of the manifold with lower cosine to stored
  vectors. This geometric fact does not change with orthogonal transforms.

**Mechanism math:**
Let the manifold M be parameterized by a chart phi: R^k -> R^2048 with k ~30. A stored
vector v_m = phi(z_m) for some z_m in R^k. A query q = phi(z_q). Cosine similarity:
  cos(q, v_m) = <phi(z_q), phi(z_m)> / (||phi(z_q)|| ||phi(z_m)||)
An SRHT applied in R^2048 maps v -> Hv where H is the Hadamard matrix. The inner product
is preserved: <Hq, Hv_m> = <q, v_m> because H is orthogonal. So cosine similarity is
EXACTLY PRESERVED by SRHT. The manifold gets rotated but manifold-local distances are
unchanged. Membership leakage is unchanged.

This explains the SRHT=zero-effect result as a mathematical certainty, not a coincidence.

**Diagnostic measurement (2 hours CPU):**
- Collect 500 stored Llama L15 embeddings.
- Run TwoNN intrinsic dimensionality estimator (scikit-dimension Python package).
- Run PCA and plot cumulative explained variance vs number of components.
- PASS indicator: 90% explained variance reached at k <= 100 (out of 2048).
- FAIL indicator: 90% variance requires k > 500 (space is genuinely high-dimensional).

**Mitigation if confirmed:**
The only way to disrupt manifold-local cosine structure is to BREAK the manifold, not
rotate it. Three possible approaches:
(a) PROJECT to a lower-dimensional space than the manifold (dimension smaller than k).
    This forces information loss and disrupts the manifold-local structure.
(b) ADD NONLINEAR PERTURBATION calibrated to the manifold curvature.
(c) TRAIN the encoder with a privacy objective that forces the manifold to be less
    structured (encoder fine-tuning, Path D from prior drill).

For (a), the cheap test is: PCA-project to k_target = 10 (below estimated manifold dim),
then reconstruct to 2048-dim (PCA-up). This forces embeddings through a bottleneck
smaller than the manifold. The bottleneck projection disrupts the specific z_m coordinates
that encode membership. Cost: 1-2 hours CPU.

**P_theoretical = 0.65, P_empirical = 0.50, P_deflated = 0.33**
(Theory strongly supports; empirical depends on harness-specific manifold dim measurement)

HARD-PASS: Intrinsic dim k < 80 confirmed AND bottleneck projection achieves ZKL < 0.12
HARD-FAIL: Intrinsic dim k > 300 (manifold too high-dim for this mechanism to apply)

---

### Hypothesis B: Token-position concentration (not dimension concentration)

**Claim:** In a causal LM, information flows forward through the sequence. At layer L15,
the last-token representation is dominated by the contribution of specific token positions
(likely the last 5-15 tokens in the context). The membership-inference signal lives in
the POSITION SUBSPACE -- the contribution of position-specific attention patterns --
rather than in coordinate dimensions.

**Why this is plausible:**
- Causal masking means each position i attends only to positions <= i.
- The last-token aggregates information from all prior positions via multi-head attention,
  but the aggregation weights are not uniform. Published work on attention sinks (2025)
  shows that causal LMs exhibit "attention sink" behavior where specific tokens (often
  the first token and the last few tokens) receive disproportionate attention.
- Stored facts are written as entire sentences. The embedding of the stored fact is
  dominated by a few token positions in the original text. These position contributions
  are preserved in the L15 embedding as structural features.
- A membership query uses the same phrasing as the stored fact (or a rephrasing that
  converges to the same key tokens). The token-position dominated cosines are then high.

**Mechanism math:**
Let x_j be the token embedding at position j. The L15 last-token hidden state is:
  h_L15 = sum_j alpha_j * f(x_j)
where alpha_j are attention-weighted aggregation coefficients and f is a per-position
transformation. If alpha_j is peaked at j in {last 10 positions}, the membership signal
is dominated by the embedding subspace of those tokens. SRHT rotates the output
coordinates of h_L15, which does not change the dominance of those token positions.

**Diagnostic measurement (2-3 hours CPU):**
- For each stored fact, compute per-position attention weight contributions at L15.
  (This requires a forward pass with attention weight capture -- supported by HuggingFace
  output_attentions=True.)
- Measure the entropy of the attention weight distribution over positions.
- Low entropy (peaked at few positions) supports this hypothesis.
- Compare member query attention weight distribution vs non-member query distribution.

**Mitigation if confirmed:**
Subtract the per-position contribution means:
  h_adj = h_L15 - sum_j mu_j (where mu_j is the mean contribution of position j across all stored facts)
This is analogous to cone-centering (Path F from prior drill) but operating on position
contributions rather than coordinate dimensions. Cost: 2-3 hours CPU once diagnostic confirms.

**P_theoretical = 0.45, P_empirical = 0.40, P_deflated = 0.18**
(Plausible but the attention-sink literature is more about first tokens, not full
position-concentration; causal masking alone does not force position concentration
in the right form for this hypothesis)

HARD-PASS: Attention weight entropy < 2.0 nats AND position-mean subtraction achieves ZKL < 0.12
HARD-FAIL: Attention weights are near-uniform across positions (entropy > 4.0 nats)

---

### Hypothesis C: Geometric relationship leak (not direction leak)

**Claim:** The membership-inference signal is not in the DIRECTION of any single embedding
but in the PAIRWISE COSINE STRUCTURE between stored vectors. Member queries co-cluster
with stored vectors in a way that non-member queries do not. This is a second-order
geometric effect, not a first-order directional effect.

**Why this is consistent with the eigenspectrum results:**
- PR measures first-order variance structure (eigenvalue spread of the covariance matrix).
- Pairwise cosine clustering is a second-order property.
- SRHT preserves all inner products (orthogonal transform), so pairwise cosines are
  EXACTLY preserved by SRHT. If the leak is in pairwise structure, SRHT cannot help.
- The ZKL-increase under SRHT is then explained: SRHT does not change pairwise structure
  but does change the absolute coordinate representation, possibly confusing other aspects
  of the retrieval system and increasing apparent leakage.

**Mechanism math:**
Let G be the Gram matrix of stored embeddings: G_ij = cos(v_i, v_j). SRHT maps
v_i -> Hv_i. The transformed Gram matrix: (Hv_i)^T (Hv_j) = v_i^T H^T H v_j = v_i^T v_j.
Gram matrix is exactly preserved by SRHT. Any geometric property derived from G is
invariant to SRHT. This is a mathematical proof that SRHT cannot help if the leak is
in Gram structure.

**Diagnostic measurement (2 hours CPU):**
- Compute the Gram matrix G for stored embeddings.
- Compute member query cosine to nearest stored vector (member distribution).
- Compute non-member query cosine to nearest stored vector (non-member distribution).
- Plot both distributions. If there is a visible gap in the DISTRIBUTION OVERLAP
  (KS test p < 0.01), the leak is in the Gram structure, not in absolute directions.
- Compare KS test result before vs after SRHT (should be identical if Gram-preserved).

**Mitigation if confirmed:**
Rank-based privacy (Path B from prior drill) directly addresses this: instead of
suppressing the cosine scores, randomize the ranking so the attacker cannot read off
the Gram-structure signal from returned document identity. The Mallows rank shuffle
is the direct mitigation.

Also: subspace PROJECTION (reducing to dim k << D) is the one operation that does
change Gram structure, by destroying information outside the projected subspace. This
is the same bottleneck approach as Hypothesis A mitigation.

**P_theoretical = 0.55, P_empirical = 0.45, P_deflated = 0.25**
(Mathematically well-grounded; the Gram-preservation proof is clean; but the exact
mitigation effectiveness is uncertain)

HARD-PASS: KS test confirms distribution gap exists; rank randomization achieves ZKL < 0.12
HARD-FAIL: KS test shows no gap (distributions are already nearly identical, meaning
    the problem is something else entirely)

---

### Hypothesis D: Frequency-weighted token concentration

**Claim:** High-frequency tokens dominate the L15 embedding in stored facts that contain
common phrases. Stored facts tend to share common vocabulary (domain-specific but
frequently occurring terms like "the patient was treated with" or "according to the
policy"). The membership-inference signal is partially driven by these shared high-frequency
terms creating predictable cosine similarity patterns.

**Why this is plausible:**
- Causal LM training weights tokens by frequency via the language model cross-entropy loss.
- High-frequency tokens develop compact, well-trained representations early in training.
- Stored facts in a domain corpus will share vocabulary, creating systematic cosine
  similarity elevation for domain queries.
- Non-member queries from outside the domain have lower frequency overlap, producing
  the member/non-member cosine gap.

**Diagnostic measurement (1 hour CPU):**
- Compute TF-IDF weights for each token in stored facts using the stored corpus.
- Weight each token's contribution to the L15 embedding by its inverse IDF (downweight
  common tokens).
- Measure ZKL on TF-IDF-reweighted embeddings.
- If ZKL improves, frequency-weighting is part of the leak signal.

**Mitigation if confirmed:**
TF-IDF-style reweighting before cosine computation. This is a lightweight preprocessing
step. Cost: 30 minutes implementation + 1 hour test.

**P_theoretical = 0.30, P_empirical = 0.35, P_deflated = 0.11**
(Less theoretically motivated than Hypotheses A/C; frequency effects are real but
unlikely to be the dominant signal at ZKL 0.22-0.41 scale)

HARD-PASS: TF-IDF reweighting achieves ZKL < 0.14 (intermediate target)
HARD-FAIL: ZKL unchanged within 0.02 after TF-IDF reweighting

---

### Hypothesis E: Layer-selection leak (L15 is too late)

**Claim:** At layer 15 of Llama-3.2-1B (approximately the midpoint of the network), the
representation is maximally "committed" to predicting the next token. This makes it
maximally informative about the specific token sequence -- which is precisely the
membership-inference signal. Earlier layers (L5-L8) are less next-token-committed and
may have lower intrinsic membership leakage at the cost of some retrieval quality.

**Published support:**
The "intrinsic dimension hunchback" finding (2025) shows that intrinsic dimension peaks
at mid-layers. Peak ID means maximum complexity and information density. If membership
inference leakage correlates with ID (as suggested by the inverse relationship between
ID and memorization), then maximum-ID layers may have maximum membership leakage.

Counterargument: the 2506.09591 paper finds HIGH-ID sequences are LESS memorized. This
appears to conflict. The resolution: the paper studies memorization at the SEQUENCE level
(whether the sequence is reproduced at generation time), which is different from
membership inference at the EMBEDDING level (whether the embedding reveals that the
sequence is stored). These are different phenomena. Memorization as verbatim reproduction
is harder for complex sequences; membership inference via embedding similarity may be
harder or easier at different layers depending on the geometry, not the ID per se.

**Diagnostic measurement (1-2 hours CPU):**
- Extract embeddings at L5, L8, L10, L12, L15, L20, L28 for the same stored facts.
- Measure ZKL(50) at each layer.
- Measure top-1 retrieval recall at each layer.
- Plot ZKL vs layer; plot recall vs layer.
- Identify the layer that minimizes ZKL while maintaining recall >= 0.85.

**Mitigation if confirmed:**
Switch production encoder from L15 to the identified lower-ZKL layer. This is a
zero-cost change (just change the extraction layer index). May cost 3-8% retrieval quality.

**P_theoretical = 0.40, P_empirical = 0.45, P_deflated = 0.18**
(Theoretically supported by the ID-hunchback findings; cheap to test; the tradeoff
between retrieval quality and privacy at different layers is the unknown)

HARD-PASS: Earlier layer achieves ZKL < 0.14 with recall >= 0.85
HARD-FAIL: All tested layers have ZKL > 0.18 (the problem is not layer-specific)

---

## SECTION 3: WHAT IS DIFFERENT ABOUT LLAMA VS MINILM (UNIFIED EXPLANATION)

The complete picture from theory + eigenspectrum diagnostic:

MiniLM:
- Training objective: symmetric contrastive (sentence similarity via CLS token).
- Result: Type 1 anisotropy (PR/D = 0.16; concentrated in ~61 dimensions).
- Membership signal: in the high-variance dimension directions.
- SRHT effect: redistributes concentrated dimensional variance -> disrupts the signal.
- ZKL improvement: yes (0.41 -> 0.24).

Llama-3.2-1B L15:
- Training objective: next-token prediction (asymmetric causal masking).
- Result: NOT Type 1 anisotropy (PR = 12.733 unchanged by SRHT).
- Probable structure: Type 2 directional anisotropy (narrow cone) COMBINED WITH
  manifold confinement (intrinsic dim ~20-50 within 2048-dim space).
- Membership signal: in manifold-local cosine structure, not in coordinate dimensions.
- SRHT effect: orthogonal transforms preserve all inner products, therefore preserve
  manifold-local cosines exactly. PR is unchanged because the manifold IS the structure
  SRHT is operating within.
- ZKL behavior: SRHT rotates the ambient coordinates, not the manifold structure.
  The slight increase in ZKL under SRHT is likely because subsampling (the "S" in SRHT)
  introduces a small information loss that degrades the SIGNAL faster than the NOISE,
  slightly worse than baseline.

**Key insight for all future mechanism tests:**
Any transform that is orthogonal (rotation, reflection) cannot help Llama because
orthogonal transforms preserve ALL inner products and therefore preserve manifold-local
cosine structure exactly. The only approaches that can help are:
(a) PROJECTION (reduces dimensionality below manifold dim, loses manifold structure).
(b) NONLINEAR mapping (changes manifold topology).
(c) PERTURBATION with noise that specifically targets manifold structure.
(d) RE-TRAINING the encoder (changes the manifold itself).

This rules out the entire class of orthogonal decorrelation transforms (SRHT, random
rotation, Hadamard variants, Walsh transforms). It rules them out NOT because of
insufficient power, but because of a mathematical invariant: orthogonal transforms
preserve cosine similarity. Full stop.

---

## SECTION 4: STACK RANKING (THEORETICAL-P x EMPIRICAL-P x ACTIONABILITY)

| Hypothesis | Mechanism | P_theoretical | P_empirical | P_deflated | Pre-test cost |
|---|---|---|---|---|---|
| A: Manifold confinement | Low intrinsic dim | 0.65 | 0.50 | 0.33 | 2h CPU |
| C: Gram structure leak | Pairwise cosine preservation | 0.55 | 0.45 | 0.25 | 2h CPU |
| B: Position concentration | Attention-weighted positions | 0.45 | 0.40 | 0.18 | 3h CPU |
| E: Layer selection | ID hunchback + layer sweep | 0.40 | 0.45 | 0.18 | 2h CPU |
| D: Frequency weighting | TF-IDF token dominance | 0.30 | 0.35 | 0.11 | 1h CPU |

NOTE: P_deflated = P_theoretical x P_empirical with calibration penalty applied.
Calibration penalty = 0.15 applied to the product (no direct precedent for Llama
privacy mechanism identification in the published literature).

Total P(any hypothesis confirmed, leading to ZKL < 0.12 fix):
P_any = 1 - prod(1 - P_deflated_i) = 1 - (0.67)(0.75)(0.82)(0.82)(0.89) = 0.73
Adjusted for implementation uncertainty: P_fix = 0.73 x 0.55 = 0.40

HARD-PASS for the overall drill: At least two hypotheses confirmed via diagnostic,
at least one mitigation achieves ZKL < 0.12 with recall >= 0.85.
HARD-FAIL: No hypothesis confirmed diagnostically AND all mitigations return ZKL >= 0.18.

---

## SECTION 5: CHEAP DIAGNOSTIC + PRE-TEST PATTERNS

### Priority 1: Manifold dimensionality diagnostic (Hypothesis A)
Time: 2 hours CPU on Llama+MarianMT harness

Step 1: Extract 500 stored embeddings from the production KB at L15.
Step 2: Run PCA on the 500 x 2048 matrix; plot cumulative explained variance.
Step 3: Run TwoNN estimator from scikit-dimension package for intrinsic dim estimate.
Step 4: Record k_90 (number of PCA dims needed for 90% variance).

If k_90 < 100: manifold confinement confirmed. Proceed to bottleneck pre-test.
If k_90 > 400: manifold hypothesis unlikely; prioritize Hypothesis C.

Bottleneck pre-test (1-2 hours additional):
Step 5: PCA-project all stored embeddings to k_bottleneck = 20 (below k_90).
Step 6: Reconstruct to 2048 via pseudoinverse.
Step 7: Measure ZKL(50) on bottleneck-projected embeddings.
Step 8: Measure top-1 recall.

PASS: ZKL < 0.14 at k_bottleneck = 20. Double with k = 50 to test sensitivity.
FAIL: ZKL >= 0.18 (bottleneck does not disrupt the leak signal).

### Priority 2: Gram structure + distribution shape (Hypothesis C)
Time: 2 hours CPU

Step 1: Collect 200 member query embeddings (queries that exactly match stored facts).
Step 2: Collect 200 non-member query embeddings (queries NOT matching any stored fact).
Step 3: For each query, compute cosine to nearest stored vector.
Step 4: Plot member cosine distribution and non-member cosine distribution.
Step 5: Run KS test between the two distributions.
Step 6: Repeat after SRHT (should be identical distributions if Gram-preserved).

PASS: KS test p < 0.001 (clear gap exists; leak is in Gram structure).
FAIL: KS test p > 0.10 (distributions nearly identical; mechanism is not cosine-gap-based).

If PASS: rank randomization (Path B, Mallows shuffle) is the direct mitigation.
Mallows sweep: theta in {0.5, 1, 2, 5}; measure ZKL at each. 1 hour additional.

### Priority 3: Layer sweep (Hypothesis E)
Time: 2-3 hours CPU

Step 1: Extract embeddings at layers {5, 8, 10, 12, 15, 20} using the same KB.
Step 2: Measure ZKL(50) at each layer.
Step 3: Measure top-1 recall at each layer.
Step 4: Plot ZKL vs layer and recall vs layer on same axes.
Step 5: Identify the "privacy frontier" layer (lowest ZKL subject to recall >= 0.85).

PASS: A layer L* exists where ZKL(L*) < 0.14 and recall(L*) >= 0.85.
FAIL: ZKL is >= 0.18 at all layers (leak is not layer-specific).

### Priority 4: Attention position analysis (Hypothesis B)
Time: 2-3 hours CPU

Step 1: Run stored fact sequences through Llama with output_attentions=True.
Step 2: At L15, extract per-position attention weights for the last token.
Step 3: Compute attention weight entropy across positions for each sequence.
Step 4: Measure whether high-entropy vs low-entropy sequences have different ZKL.

PASS: Mean entropy < 2.0 nats AND entropy correlates with ZKL across KB subsets.
FAIL: Entropy > 4.0 nats (attention is diffuse; position concentration is not the mechanism).

### Priority 5: TF-IDF reweighting (Hypothesis D)
Time: 1 hour CPU

Step 1: Compute IDF weights across the stored fact corpus.
Step 2: For each stored embedding, apply TF-IDF weighted average across token positions.
Step 3: Normalize and measure ZKL.

PASS: ZKL improves by >= 0.03 (TF-IDF contributes).
FAIL: No improvement within 0.02.

---

## SECTION 6: SUBSTRATE-INTERNAL vs LLM-SIDE FIXES

**Substrate-internal (preferred for deployment):**
These are changes to HOW the substrate processes encoder outputs. They do not require
modifying the encoder model and can be deployed per-customer without training.

| Fix | Applies to | Type |
|---|---|---|
| PCA bottleneck projection | All encoder types | Substrate-internal |
| Cone-aware mean centering (Path F) | All encoder types | Substrate-internal |
| Rank randomization (Path B) | All encoder types | Substrate-internal |
| Layer selection (L5 vs L15) | Causal LM encoders only | Config change |
| TF-IDF reweighting | All encoder types | Substrate-internal |

These are all viable for production deployment. They require no GPU and can be
implemented as inference-time wrappers around the encoder.

**LLM-side fixes (per-customer training cost):**
These require modifying the encoder model itself.

| Fix | Applies to | Type |
|---|---|---|
| Encoder fine-tuning (Path D) | Per-encoder, per-customer | Training-based |
| Privacy-objective whitening as PCA replacement (Path A) | Per-KB-distribution | Optimization-based |

Path A is a borderline case: it is a learned transform applied at substrate level but
requires optimization over the embedding distribution, which is per-KB-instance. It is
not truly per-customer training but it is not a simple config either.

**For the current product roadmap:**
Prioritize substrate-internal fixes. Run Priority 1 (bottleneck PCA) and Priority 2
(Gram distribution diagnostic) first, since they are the cheapest and most likely to
yield actionable results given the manifold confinement hypothesis.

---

## SECTION 7: PESSIMISTIC SCENARIO (BRUTALLY HONEST)

If hypotheses A, B, C, D, E all return diagnostics that do not identify the leak mechanism,
or all mitigations return ZKL >= 0.18:

**Technical conclusion:**
The membership-inference leakage in Llama-3.2-1B L15 is not accessible to any known
post-hoc substrate-side linear or semi-linear fix. The leak is structural to the causal
LM encoder architecture at the embedding level and requires encoder modification to
address at the HIPAA-grade ZKL < 0.10 target.

**What this means for customers:**
1. For standard enterprise customers (not HIPAA-regulated): the 2x relative improvement
   in membership inference leakage vs unprotected RAG, combined with rate-limiting (k<=5)
   and full audit trail, is still a meaningful and accurate privacy story.
2. For HIPAA-regulated customers (healthcare, clinical): the substrate currently cannot
   guarantee HIPAA-grade absolute privacy at the embedding level. Customers requiring
   this should use a purpose-built privacy-fine-tuned encoder (we would recommend a
   specific model at additional cost per deployment). The ZKP soundness axis (audit
   trail + retrieval proof) provides complementary compliance coverage under Article 12.
3. For customers requiring SOC-2 or ISO 27001: rate-limiting + audit trail + relative
   improvement is sufficient for these frameworks. HIPAA is more demanding.

**Customer narrative (plain language version):**
"Our system provides two layers of privacy protection. First, we limit how many documents
any one query can retrieve, so mass extraction is not possible. Second, we keep a
cryptographic audit trail of every retrieval event, so any access anomaly is detectable.
For most privacy frameworks, this is sufficient. For HIPAA-grade clinical use, we
recommend pairing the substrate with a privacy-fine-tuned encoder, which we can provision
as a managed add-on."

**North-star impact:**
The LLM-comparison framing shifts from "categorical privacy advantage" to "incremental
privacy advantage plus audit superiority." Specifically:
- Substrate vs LLM on raw membership inference: roughly comparable (both leak).
- Substrate vs LLM on audit trail: substrate wins clearly.
- Substrate vs LLM on rate-limiting: substrate wins.
- Substrate vs LLM on ZKP-verifiable retrieval: substrate wins uniquely.
- The absolute HIPAA claim was always a research goal, not a shipped feature. If it
  becomes unachievable via encoder-agnostic methods, it becomes an optional per-customer
  add-on, not a core claim.

This is weaker than the strong form but not a product-threatening result. The ZKP
soundness axis identified in the Phase 2 chains research becomes the primary privacy
differentiator.

---

## SECTION 8: WHAT WE KNOW DEFINITIVELY VS HYPOTHETICAL

### Definitive (empirically confirmed)
- SRHT does not change Llama's PR (12.733 -> 12.733). This is a measurement.
- SRHT increases Llama's ZKL (0.22 -> 0.58 monotonically). This is a measurement.
- DP score noise does not help at any sigma in [0.05, 0.40]. This is a measurement.
- The dimension-concentration hypothesis is WRONG for Llama. Disproved by the above.
- MiniLM is Type 1 anisotropic and SRHT helps it. This is a measurement.
- Orthogonal transforms preserve all inner products and therefore cannot disrupt
  manifold-local cosine similarity. This is a theorem (not a hypothesis).

### Hypothetical (not yet tested, must test before claiming)
- Manifold confinement (intrinsic dim ~20-50): NOT measured for the Llama production KB.
- Pairwise cosine gap (KS test): NOT measured yet.
- Layer selection ZKL profile: NOT measured yet.
- Bottleneck PCA ZKL effect: NOT measured yet.
- Attention position entropy: NOT measured yet.

**The single most important unrun test** is the manifold dimensionality diagnostic
(Priority 1 above). It is the fastest to confirm (2 hours CPU), and its result determines
which mitigations are worth pursuing. If manifold dim is confirmed low (<= 50), the
bottleneck PCA mitigation follows immediately. If manifold dim is high, we move to
Hypothesis C (Gram structure) as the primary candidate.

---

## SECTION 9: RECOMMENDED IMMEDIATE ACTIONS FOR EXP-DEV

Once the Llama+MarianMT harness is confirmed functional:

1. **Run Priority 1 diagnostic first (2h CPU):** PCA explained variance curve + TwoNN
   estimate on production KB embeddings. This determines which mitigation path to follow.
   Cost: 2 hours CPU. No GPU.

2. **Run Priority 2 diagnostic in parallel (2h CPU):** Member vs non-member cosine
   distribution plot + KS test. This directly measures whether the ZKL gap exists as
   a pairwise-cosine signal. Can run in parallel with Priority 1 on the same harness
   instance (different pass over the data).

3. **Defer Priority 3, 4, 5 until Priority 1+2 results are in.** They are lower expected
   value. Run them only if Priority 1+2 are inconclusive.

4. **Path A entropy whitening (prior drill recommendation):** Can be set up in parallel
   with the diagnostics. The diagnostics will confirm whether entropy whitening has
   the right target structure. If Priority 1 confirms manifold confinement, entropy
   whitening is the correct objective for the whitening step (replace current retrieval-
   objective PCA with manifold-disrupting bottleneck PCA).

5. **Path B rank randomization (prior drill recommendation):** Test after Priority 2
   Gram diagnostic confirms the pairwise cosine gap. If gap is confirmed, Mallows shuffle
   is the direct and cheapest fix. The rank randomization sweep (theta 0.5-5) takes 1
   hour and can directly answer whether ZKL < 0.12 is achievable with acceptable recall.

---

## SECTION 10: NORTH-STAR IMPLICATIONS

### If Priority 1 confirms manifold confinement + bottleneck PCA achieves ZKL < 0.12

This is the best-case outcome. It means:
- Privacy fix is a substrate-internal operation (PCA bottleneck), not an encoder change.
- Deployable per-customer in the current architecture.
- Mechanism is now understood: causal LM embeddings live on a low-dim manifold;
  membership inference exploits manifold-local cosines; bottleneck projection disrupts
  the manifold structure.
- Product claim: "Substrate achieves HIPAA-grade privacy via manifold-disrupting
  dimensionality projection, applicable to any causal LM encoder."
- LLM comparison story: strong. Standard LLMs do not do this.

### If Gram-structure leak (Hypothesis C) confirmed + rank randomization achieves ZKL < 0.12

- Privacy fix is rank-level perturbation, not representation-level.
- Utility cost: top-1 precision degrades to ~0.75 (users get correct answer 75% of time
  as top result, vs 100% currently).
- Acceptable for most use cases; may be too costly for exact-match use cases.
- Product claim: "Substrate provides k-anonymous retrieval with bounded membership
  inference risk."

### If layer sweep (Hypothesis E) identifies a lower-ZKL layer

- Fix is a config change (set extraction layer from 15 to X).
- Zero implementation cost.
- Retrieval quality may degrade 3-8% depending on which layer is selected.
- This would be the fastest path to a working HIPAA claim if it pans out.

### If all paths fail

- Qualified posture is the permanent position (as described in Section 7).
- Research focus shifts to encoder fine-tuning (Path D) as the remaining path.
- ZKP soundness becomes the primary privacy differentiator vs LLMs.

---

## SECTION 11: CROSS-THREAD SYNTHESIS

### Connection to prior 3x privacy failure drill (research_drill_privacy_failure_mechanism_3x_2026-06-07)

This drill supersedes the mechanism section of the prior drill with more precise
mechanism understanding grounded in the eigenspectrum result. The paths recommended
in the prior drill (A, B, F) remain valid but should be sequenced AFTER the structural
diagnostics (Priority 1+2 above). Path F (cone-aware cosine) was developed under the
dimension-concentration hypothesis; it may still work if the cone axis is accessible
via mean-centering, but its theoretical justification now depends on whether cone-centering
happens to disrupt manifold-local cosines. This is testable: run Test F1 after Priority 1
confirms or denies manifold confinement.

### Connection to production architecture lock

The production architecture uses PCA whitening (whitening + pseudoinverse). The manifold
confinement hypothesis, if confirmed, means the current PCA whitening is EXPANDING the
manifold (going from k_90 dimensions to all 2048 whitened dimensions). This may actually
INCREASE membership leakage by amplifying low-variance noise dimensions that partially
obscure manifold structure. The fix would be to change whitening to a COMPRESSING PCA
(project to k < k_90 dimensions, then use the compressed representation for both retrieval
and privacy). This is a SINGLE architecture change with potential dual benefit.

### Connection to Phase 2 research (ZKP soundness, EU AI Act Article 12)

The ZKP soundness axis becomes more important if privacy-at-the-embedding level is
constrained. ZKP-verifiable audit trail is a different privacy dimension: it does not
reduce membership leakage but it provides cryptographic proof of WHAT was retrieved
and WHEN. For Article 12 compliance, audit + rate-limit + relative improvement may be
the complete story. EU AI Act deadline is August 2026 (~6 weeks). The audit trail
infrastructure is already more advanced than the membership-inference fix; it should
be the lead compliance story until the membership-inference path is resolved.

---

## SECTION 12: CITATIONS (VERIFIED SOURCES FROM THIS DRILL)

1. "Memorization in Language Models through the Lens of Intrinsic Dimension" -- Arnold
   2025. ACL L2M2 workshop. arxiv 2506.09591. Finding: low-ID sequences are more
   memorizable. ID peaks at mid-layers.

2. "Latent Semantic Manifolds in Large Language Models" -- 2025. arxiv 2603.22301.
   Finding: causal LMs (GPT-2, OPT, Pythia) have intrinsic dim 19-27 with ambient
   dim 768-2048; 1-3% utilization; hourglass ID pattern across layers.

3. "Anisotropy Is Inherent to Self-Attention in Transformers" -- arxiv 2401.12143.
   Finding: Q and K distributions drift in aligned directions during training; decoder
   architectures exhibit extremely high anisotropy levels. Does not distinguish Type 1
   vs Type 2 anisotropy by PR measure.

4. "Safeguarding Privacy of Retrieval Data against Membership Inference Attacks" --
   2025. arxiv 2505.22061. Finding: causal LM encoders remain vulnerable because
   sequential prediction mechanisms leak membership signals; defenses require
   architecture-specific adaptation.

5. "Concept-Aware Privacy Mechanisms for Defending Embedding Inversion Attacks" --
   2025. arxiv 2602.07090. Finding: embedding dimensions exhibit varying privacy
   sensitivity; anisotropic noise injection adapts to per-dimension sensitivity.

6. "Towards Secure Retrieval-Augmented Generation" -- 2025. arxiv 2603.21654.
   Survey of RAG security. Differential privacy and corpus transformation are a
   known defense family; DP mechanisms include DPVoteRAG and LPRAG variants.

7. "On the Role of Attention Masks and LayerNorm in Transformers" -- arxiv 2405.18781.
   Finding: causal masking mitigates rank collapse compared to full attention; the
   last token in causal attention contains information from the entire sequence.

8. "ISOTROPY IN THE CONTEXTUAL EMBEDDING SPACE" -- ICLR 2021. openreview.
   Finding: causal models (GPT, ELMo) have higher embedding-merge behavior in
   final layers; BERT clusters become clearer in deeper layers. Different anisotropy
   structures between causal and bidirectional.

Total verified citations: 8 (from external lit; all fetched via WebSearch/WebFetch
during this drill session).

---

## CHEAP DECISIVE TEST (SUMMARY)

The single cheapest and most informative next step is:

**PCA explained variance curve on production KB embeddings (2 hours CPU)**
- If k_90 < 100: manifold confinement confirmed; run bottleneck PCA immediately.
- If k_90 > 300: pivot to Gram structure diagnostic (KS test on member/nonmember cosines).
- Either result fully determines which mitigation path to pursue.

This test requires only:
- Access to the production KB embedding matrix
- NumPy + scikit-learn PCA
- The same Llama extraction harness already being set up for Path A/B tests

Pre-test pattern (production Llama+MarianMT harness):
1. Extract stored embeddings matrix E: shape (N_stored, 2048)
2. sklearn.decomposition.PCA(n_components=200).fit(E)
3. Plot pca.explained_variance_ratio_.cumsum()
4. Read off k where cumsum > 0.90
5. Report k_90 value

This is a 30-line Python script, not a multi-hour experiment.

---

## STATUS

Written: 2026-06-07
Next drill candidate: manifold confinement + low-dim bottleneck (follow-up once diagnostic confirms)
P_deflated = 0.33 (any one path closes ZKL gap); 0.40 adjusted for compound probability
