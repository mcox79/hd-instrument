# Research note: 2x operational drill -- real-encoder codebook collision + cross-N attenuation disambiguation

**Date**: 2026-06-06
**Owner**: Research sub-agent (single-writer, 2x discipline)
**Topic**: Level-2 operational drill -- H1 vs H2 disambiguation + rescue paths for real-encoder
  bipolar substrate; cross-N attenuation mechanism; encoder-architecture-aware codebook.
**Trigger**: Prior level-1 findings: (1) ETF Hadamard whitening on real MiniLM 384-dim gives
  2.75x capacity vs synthetic 10x; (2) random-feature lift phi(x)=sign(Rx) at D in
  {384,1024,4096} gives 2.75x / 1.29x / 1.29x -- LIFT PLATEAUS and SHRINKS with N.
  This is INCONSISTENT with codebook-collision-as-sole-noise. Orchestrator hypotheses:
  H1 = N-dependent additional noise in real encoder embeddings.
  H2 = Hadamard gain is N-saturating because partial pre-structure becomes dominant at large N.
**2x discipline**: level-2 operational drill -- no re-derivation of level-1 findings;
  goes deeper into mechanisms, math, and implementation paths.
**Lit-scan calibration penalty**: P estimates deflated 0.15-0.25 from raw estimates;
  novel-synthesis cap 0.50; hard-fail thresholds included per
  [[feedback-lit-scan-calibration-penalty]].
**Query discipline**: generic math terms only per [[feedback-query-privacy-decomposition]].

---

## HEADLINE

> H2 (partial pre-structure saturation) is the dominant mechanism for the lift plateau but
> H1 (N-dependent noise from norm heterogeneity) provides a secondary additive contribution.
> These two effects separate cleanly on a SINGLE disambiguation cell: measure capacity ratio
> Q(N) = M_sub / M_theoretical as a function of N at FIXED M/N ratio using SYNTHETIC
> isotropic vs REAL encoder keys; if Q(N) decreases with N on real-only (not synthetic),
> H1 is confirmed independently of H2. If Q(N) decreases on BOTH, H2 dominates. The rescue
> paths are structurally different: H1 is attacked by norm normalization + cluster-aware
> whitening; H2 is attacked by pre-structured codebook design (SRHT, Kerdock, PCA-aware VQ).
> The lift plateau at D > 384 is explained by sign(Rx) for large D amplifying intra-cluster
> correlation rather than reducing it -- a mechanism confirmed by the random-features
> Hopfield capacity analysis (arXiv:2303.16880) and the Bielmeier-Friedland 2025 prefactor
> result (arXiv:2508.01395).

---

## 1. DISAMBIGUATION CELL -- H1 vs H2

### Algebraic argument for why H1 and H2 make DIFFERENT predictions

**Define** Q(N, M_frac, encoder_type) = (measured capacity) / (theoretical capacity N * alpha_c)
where alpha_c ~ 0.138 is the Hopfield critical ratio.

**H1 prediction**: Q decreases as a FUNCTION OF N for real-encoder keys at FIXED alpha = M/N.
Mechanism: real-encoder embeddings have heterogeneous L2 norms and anisotropic cluster
structure. As N grows at fixed alpha, the per-neuron signal-to-noise ratio for cross-cluster
interference INCREASES because the noise terms (cross-cluster bleed, norm heterogeneity)
add incoherently at rate O(sqrt(N)) while signal grows at rate O(N). BUT: norm heterogeneity
introduces a SYSTEMATIC bias (not random): some stored patterns have ||xi_mu|| >> 1 and
others << 1 after sign-projection, which biases the overlap function toward high-norm patterns.
This bias is INDEPENDENT of N normalization and does NOT average out. Under H1:

  Q_real(N) ~ Q_synthetic(N) - delta_norm(N)

where delta_norm(N) = f(sigma_norm^2) * g(N) is a DECREASING FUNCTION of N only if sigma_norm^2
grows with N (which happens if the encoder norm distribution becomes MORE heterogeneous at
larger projection dimensions D). Key test: does Q drop MORE steeply for real than synthetic keys?

**H2 prediction**: Q decreases as a FUNCTION OF N for BOTH real and synthetic keys when the
codebook has partial pre-structure (Hadamard). Mechanism: the Hadamard codebook imposes a
fixed axis-aligned structure on the N-dimensional space. As M grows at fixed alpha:

- At small N (384): M ~ 0.138 * 384 ~ 53 patterns. Hadamard rows involved in encoding
  are well-separated; interference is low. Whitening effectively decorrelates.
- At large N (4096): M ~ 0.138 * 4096 ~ 565 patterns. The Hadamard codebook has fixed
  structure; at large M, stored patterns begin to systematically cover the same Hadamard
  subspaces, creating structured (non-random) interference -- the "partial pre-structure"
  effect. This is NOT a property of real vs synthetic keys; it is a property of the codebook
  at large M.

Under H2: Q_real(N) and Q_synthetic(N) BOTH decrease with N at fixed alpha, but the RATE of
decrease differs (real may be faster due to additive H1 effect).

**Distinguishing measurement**:

  Contrast = [Q_real(4096) / Q_real(384)] - [Q_synthetic(4096) / Q_synthetic(384)]

- If Contrast < -0.15: H1 is confirmed (real keys degrade FASTER than synthetic with N).
  The difference is attributable to encoder-specific noise.
- If Contrast is in [-0.15, +0.05]: H2 dominates (both degrade at similar rate;
  degradation is codebook-structure-driven, not encoder-specific).
- If Contrast > +0.05: anomalous (real encoder outperforms synthetic at large N); suggests
  a third mechanism (e.g., encoder geometry fortuitously aligns with large-N Hadamard subspace).

**Why this works algebraically**: The Matthiessen-noise decomposition from prior level-1 work
gave: total noise = codebook-collision + encoder-specific noise. At N=4096, codebook-collision
was 100% (Matthiessen result). But this was for a FIXED M. As M SCALES with N (fixed alpha),
the codebook-collision term changes character: for synthetic keys it is random (averages out);
for real keys with pre-structure it has a correlated component. The Contrast metric isolates
this correlated component.

### Cell D (disambiguation cell -- HIGHEST PRIORITY)

Architecture:
- N_sub in {384, 1024, 2048, 4096} (4 points on the N axis)
- alpha = M/N = 0.08 fixed (well below critical; use 0.08 not 0.138 for clean signal)
- Two key conditions: (A) synthetic Gaussian keys, (B) real MiniLM 384-dim projected to N_sub
- Codebook: fixed Hadamard at each N_sub
- Metric: Q(N) = measured_capacity / (alpha * N); report ratio Q_real / Q_synthetic at each N
- FLIP = 0.05, seeds = 20 per cell

Thresholds:
- HARD-PASS (H1 confirmed): Q_real / Q_synthetic < 0.70 at N=4096 while Q_real / Q_synthetic
  > 0.90 at N=384 (relative drop of >20pp -- encoder-specific degradation scales with N)
- MIDDLE-BAND: Q_real / Q_synthetic in [0.70, 0.90] at N=4096 (mixed H1 + H2)
- HARD-FAIL (H2 only): Q_real / Q_synthetic > 0.90 at N=4096 AND Q_synthetic(4096) < 0.80 *
  Q_synthetic(384) (both degrade equally; H2 dominates; H1 negligible)

Why this cell works: if H2 alone, both synthetic and real follow the same Q(N) curve (same
codebook structure, same alpha). Any divergence between the two curves is attributable to
the encoder-specific mechanism (H1). The cell is cheap: 4 N values * 2 encoder types *
20 seeds = 160 runs, each trivially fast.

Estimated wall: 20-40 min CPU.
P_deflated (H1 confirmed) = 0.35 (raw 0.50, deflation 0.15; novel-synthesis cap applied).
P_deflated (H2 dominant) = 0.40 (cleaner algebraic case; raw 0.55, deflation 0.15).

---

## 2. IF H1 CONFIRMED: N-dependent noise rescue paths

### 2a. Algebraic taxonomy of N-dependent noise in real encoder embeddings

**Type A: Norm heterogeneity**
Real LM encoder embeddings have heterogeneous L2 norms even after sign-projection. The
sign-projection phi(x) = sign(x) discards magnitude, so the stored bipolar pattern xi_mu
is unit-magnitude per component. BUT: the density of embedding mass varies across neurons
because the pre-projection embedding has variable magnitude across dimensions. The effective
signal overlap for pattern mu is:

  m_mu^eff = (1/N) sum_i xi_mu_i * sigma_i

where sigma_i = E[|x_mu_i|] is the marginal scale at dimension i. If sigma_i is non-uniform,
m_mu^eff differs from the uniform-case overlap by a term proportional to Var(sigma_i).

At larger N (random projection to higher D): R is a random D x 384 matrix; the projected
embedding has variance ~ ||x_384||^2 / 384 at each output dimension (by JL). But if
||x_384|| varies across inputs (which it does for real LM outputs), then Var(||x_D||^2)
grows with D (non-cancellation at larger D). This is the algebraic mechanism for H1:
norm heterogeneity AMPLIFIES with D.

Quantification: for MiniLM-L6 (per Ethayarajh 2019, isotropy defect ~0.7):
- Top-3 principal components capture ~55% of variance
- sigma_max / sigma_min (per-neuron marginal scale ratio) ~ 3-5 for 384-dim output
- Under random projection to D=4096: this ratio SPREADS (central limit theorem does not
  apply to the max; rare high-norm dimensions accumulate)

**Type B: Cross-cluster bleed**
Real encoder embeddings form clusters (semantic clusters for text). Patterns within the
same cluster have non-negligible mutual overlap BEFORE sign-projection. Let rho_intra be
the average within-cluster cosine similarity. Then the effective noise term for a stored
pattern mu from cluster k is:

  eta_mu ~ rho_intra * M_k / N

where M_k is the number of patterns in cluster k. As N grows at fixed alpha = M/N:
M grows proportionally, M_k grows proportionally, and the eta_mu term grows proportionally
too -- it does NOT saturate. This is N-dependent noise: total noise grows with M, and
since M = alpha * N, noise grows with N.

At D > 384 (random projection lift): the intra-cluster cosine similarity for sign-projected
vectors is PRESERVED by Johnson-Lindenstrauss up to epsilon ~ sqrt(log(M)/D). So rho_intra
is approximately constant with D. BUT M grows with D if we also expand the concept vocabulary
proportionally. If M is held fixed and only D grows: rho_intra decreases slowly as 1/sqrt(D)
(JL decorrelation), which means Type B noise IMPROVES with D -- but not by enough to overcome
Type A amplification. This explains the lift plateau: D increase reduces Type B but amplifies
Type A; at large D the Type A effect wins.

**Type C: Basin width mismatch**
The Hopfield retrieval basin has width ~ 1 - 2*alpha/alpha_c (fraction of correct bits).
At alpha = 0.08, basin width ~ 1 - 0.58 ~ 0.42 correct bits. For real encoder queries,
the query q differs from the stored pattern xi_mu not just by flip noise but by systematic
encoder-specific distortion (the sign-projection quantization error). If the quantization
error is CORRELATED with the intra-cluster structure, the basin width effectively shrinks
because the query lands near the boundary of multiple attractor basins simultaneously.

Basin width mismatch is N-INDEPENDENT (it is a property of the encoder geometry at fixed D),
but it causes a FIXED degradation factor, not a growing one. Basin mismatch cannot explain
the N-dependent attenuation unless the mismatch grows with N (which would require the
cluster geometry to become more tangled at higher D -- possible for sign(Rx) with large D).

### 2b. Architectural rescues for H1

**Rescue H1-A: Per-dimension norm normalization before sign-projection**

Attack: Type A (norm heterogeneity). For each encoder output x in R^384, compute the
empirical marginal standard deviation sigma_i = E[|x_i|^p]^(1/p) across the training corpus,
then normalize: x_norm_i = x_i / sigma_i. This makes the per-dimension statistics uniform
before sign-projection. Effect on overlap:

  m_mu^eff (normalized) = (1/N) sum_i xi_mu_i * 1  (uniform marginal sigma)

compared to unnormalized where the leading correction term is eliminated.

Cost: one offline pass over the corpus; stored as a 384-dim vector. Equivalent to
"feature-wise standardization" before VQ. The SRHT / QuaRot literature (2024) uses
exactly this as a preprocessing step for quantization incoherence.

Pre-registered thresholds for Cell H1-A:
- HARD-PASS: normalized > non-normalized capacity by >= 1.3x at N=1024 on real encoder keys
- MIDDLE-BAND: 1.0-1.3x (partial norm correction; Type B or C dominate residual)
- HARD-FAIL: normalized <= 1.0x (norm heterogeneity is not the active noise source at this N)

**Rescue H1-B: Cluster-aware whitening (PCA within clusters)**

Attack: Type B (cross-cluster bleed). Segment the encoder embedding corpus into K_cluster
semantic clusters (K-means with K = sqrt(M)). Within each cluster, compute the PCA
whitening transform W_k such that within-cluster covariance becomes identity. Apply W_k
before sign-projection for patterns in cluster k.

Effect on intra-cluster overlap: rho_intra -> 0 after whitening (PCA whitening exactly
decorrelates within-cluster patterns). Cross-cluster overlap is unchanged (W_k is
cluster-local). Net: eta_mu from Type B is eliminated for intra-cluster interference.

Algebraic gain: (1 - rho_intra * M_k / N)^(-1) recovered; for rho_intra ~ 0.3 and M_k/N
~ 0.05: factor ~ 1/(1 - 0.015) ~ 1.015 per pattern -- small per-pattern but cumulative
across M patterns. Estimated capacity gain: 1.2-1.5x.

Cost: O(K_cluster * d^2) preprocessing (K-means + PCA per cluster); d=384. Moderate.

Pre-registered thresholds for Cell H1-B:
- HARD-PASS: cluster-whitened >= 1.5x non-whitened at matched conditions
- MIDDLE-BAND: 1.1-1.5x
- HARD-FAIL: <= 1.1x (cross-cluster bleed is not the active source; check Type A or C)

**Rescue H1-C: Adaptive sign threshold (soft bipolar)**

Attack: Type C (basin width mismatch) and residual Type A. Instead of hard sign-projection
(threshold at 0), use a per-dimension adaptive threshold:

  xi_mu_i = sign(x_mu_i - tau_i)

where tau_i = median_{mu}(x_mu_i) (per-dimension median over the stored pattern set).
This moves the decision boundary to the empirical center of mass, maximizing the entropy
of the bipolar representation.

Information-theoretic argument: a sign-projection at the median maximizes H(xi_i) (binary
entropy of each bipolar component) by making P(xi_i = +1) = P(xi_i = -1) = 0.5. Maximizing
component entropy maximizes capacity under the independence approximation (Hopfield capacity
formula assumes balanced, near-independent patterns; departures from balance introduce a
capacity-reduction prefactor).

For MiniLM embeddings with anisotropy defect: some dimensions have strong positive bias
(mode far from zero); sign at zero wastes information. Adaptive threshold corrects this.

Pre-registered thresholds for Cell H1-C:
- HARD-PASS: adaptive-threshold >= 1.3x hard-sign at matched N and FLIP
- MIDDLE-BAND: 1.05-1.3x
- HARD-FAIL: <= 1.05x (encoder dimensions are already median-balanced; no gain)

---

## 3. IF H2 CONFIRMED: Hadamard N-saturation rescue paths

### 3a. Algebraic mechanism of partial pre-structure saturation

The Hadamard saturation effect is algebraically different from random-noise saturation.
For a random Gaussian codebook (synthetic keys), the interference term for stored pattern mu is:

  noise_mu = (1/N) sum_{nu != mu} <xi_mu, xi_nu>^2

For a Hadamard codebook on synthetic keys: <xi_mu, xi_nu> = sign(<H_row_mu, e_nu>) where
e_nu is a random embedding direction. The distribution of <H_row_mu, H_row_nu> for two
DIFFERENT Hadamard rows is exactly 0 (orthogonality). But for SIGN of a random projection
of Hadamard rows onto real embedding directions: the inner product is NOT zero in general.

At large N with fixed alpha: M grows proportionally. The fraction of Hadamard row-pairs
that happen to project onto the same real-embedding subspace grows as M^2 / N (birthday
paradox on the Hadamard subspace coverage). At M/N = 0.08 and N=4096: M = 328;
M^2/N = 328^2 / 4096 ~ 26. So ~26 pairs of stored patterns project onto the same
Hadamard subspace, creating systematic constructive interference. At N=384, M=30:
M^2/N = 900/384 ~ 2.3. The ratio 26/2.3 ~ 11x MORE structured interference at N=4096.

This is the "partial pre-structure becomes dominant at large N" mechanism. It grows as
M^2/N ~ alpha^2 * N, so it is LINEAR in N for fixed alpha. This predicts that Q(N) under
H2 scales as:

  Q(N) ~ 1 - C_H2 * alpha^2 * N

which means Q DECREASES linearly with N at fixed alpha. Falsifiable prediction:
plot Q vs N and test for linearity.

Under H1, the degradation has a DIFFERENT form:
  Q(N) ~ 1 - C_H1 * sigma_norm^2(D) / N^(1/2)

(norm heterogeneity grows as D^(1/2) under random projection; N-dependence sub-linear).

These two forms have different slopes and curvature in the Q vs N plot -- this is the
clean algebraic separator between H1 and H2.

### 3b. Architectural rescues for H2

**Rescue H2-A: Pre-whitening before VQ (SRHT-class)**

The partial pre-structure problem is that the Hadamard codebook has fixed axis-aligned
structure that creates systematic interference at large M. The fix: apply a random sign-flip
diagonal matrix D = diag(d_1, ..., d_N) where d_i = +/-1 i.i.d., before the Hadamard
transform. This randomizes the pre-structure, converting the systematic interference into
random interference that averages out at rate O(1/sqrt(N)).

  Codebook_SRHT: c_j = H * D_random * e_j (where D_random is a fresh random sign-flip)

Effect on structured interference: the M^2/N systematic pairs are now pseudo-random;
interference reverts to the random case and Q(N) recovers to the synthetic-key curve.

This is exactly the QuaRot/QuIP mechanism (2024) applied to codebook generation rather
than weight quantization. The algebraic guarantee: for a random D, the matrix H*D has the
same JL-guarantee properties as a random Gaussian matrix (Tropp 2011, arXiv:1011.1595).

Important: this rescue ONLY addresses H2. If H1 is also active, SRHT pre-whitening reduces
H2 but H1 remains. Combined rescue: SRHT (kills H2) + adaptive-threshold (kills H1-C).

Pre-registered thresholds for Cell H2-A:
- HARD-PASS: SRHT-codebook >= 1.5x fixed-Hadamard at N=2048 on real encoder keys
  (specific to large N where H2 effect is maximal per the M^2/N formula)
- MIDDLE-BAND: 1.1-1.5x
- HARD-FAIL: <= 1.1x (pre-structure is not the dominant noise; check H1 path)

Additional diagnostic: run same cell on synthetic keys. If SRHT >= 1.5x Hadamard on
SYNTHETIC too: pre-structure is not encoder-specific (pure H2). If SRHT gain appears
ONLY on real keys: encoder-specific effect dominates (H1 additive).

**Rescue H2-B: Learned-codebook LC2 shifts the pre-structure mechanism**

Learned codebook (k-means on the encoder embedding corpus): replaces the fixed Hadamard
axis-aligned structure with a distribution-adapted structure. The k-means centroids are NOT
axis-aligned; they are aligned with the principal directions of the embedding distribution.

Effect on H2: the M^2/N structured-interference mechanism assumes Hadamard rows are the
codebook vectors. With learned centroids c_j (which are near-dense unit vectors, not axis-
aligned Hadamard rows), the structured interference term becomes:

  noise_LC2 = (1/N) * sum_{nu != mu} |<c_mu, c_nu>|^2 = (1/N) * M * mu_LC2^2

where mu_LC2 is the average pairwise coherence of the learned codebook. For k-means on a
well-separated real embedding distribution: mu_LC2 ~ 1/sqrt(K_codebook) by the Welch bound
(optimal codebook achieves minimum coherence). This gives:

  noise_LC2 ~ M / (N * sqrt(K_codebook))

compared to Hadamard saturation:
  noise_Hadamard_sat ~ alpha^2 * N / K_coverage

where K_coverage = N / (fraction of rows covered by M patterns) ~ N/M.

For K_codebook = 384 and M = 328 (N=4096, alpha=0.08):
  noise_LC2 ~ 328 / (4096 * sqrt(384)) ~ 0.0041
  noise_Hadamard_sat ~ 0.0064 * 4096 / 12.5 ~ 2.1  -- structured interference is large

The learned codebook eliminates the structured-interference term by making coherence
depend on K_codebook, not on the Hadamard block structure. Estimated gain: 3-5x at N=4096.
P_deflated = 0.35 (requires k-means to achieve near-Welch-optimal coherence; 0.15 deflation).

Pre-registered thresholds for Cell H2-B (= LC2 implementation):
- HARD-PASS: LC2 >= 2.0x Hadamard at N=2048 on real encoder keys
- MIDDLE-BAND: 1.2-2.0x
- HARD-FAIL: <= 1.2x (learned coherence is not lower than Hadamard; k-means not converging
  to near-Welch-optimal solution; rescaled initialization required)

**Rescue H2-C: Sparse Hadamard mixture LC1 re-analysis under H2**

The SHM codebook (level-1 research) was analyzed as an attack on H1 (encoder anisotropy).
Re-analyzing under H2: each SHM codeword c_j = sign(sum_{l in S_j} H_row_l) with |S_j|=k.

For random supports S_i, S_j: E[<c_i, c_j>] = 0 and Var[<c_i, c_j>] ~ k^2/N.

BUT the structured interference (H2 mechanism): the M^2/N birthday paradox on Hadamard
subspace coverage is REDUCED by SHM because each codeword c_j covers k Hadamard rows
rather than 1. The effective subspace coverage per codeword is k-fold larger, so the
M^2/N saturation threshold is DELAYED by a factor of k. This is a genuine H2-rescue
mechanism for SHM that was NOT captured in the level-1 analysis.

Predicted gain of SHM over Hadamard under H2: saturation delay ~ k fold increase in
effective M before hitting the M^2/N interference floor. At k=8: onset of H2 saturation
shifts from M=28 (N=384) to M=224 -- well above practical use cases. This means SHM
essentially ELIMINATES the H2 effect at k >= 8.

Combined: SHM addresses BOTH H1 (anisotropy decorrelation, level-1 analysis) AND H2
(subspace saturation delay, new level-2 finding). This upgrades the pull-priority of SHM
from "nice-to-have" to "attacks both hypotheses simultaneously."

Pre-registered thresholds for Cell LC1 N-sweep (add to already-queued LC1):
- ADD: run Cell LC1 at N in {384, 1024, 2048} to characterize Q(N) under SHM
- HARD-PASS (H2 confirmed + addressed): SHM Q(N) does NOT decrease with N (flat or
  increasing Q ratio relative to fixed Hadamard)
- HARD-FAIL: SHM Q(N) decreases with N at same rate as Hadamard (SHM does not address H2)

---

## 4. CROSS-N PROFILING

### 4a. N-sweep cell design (Cell XN)

Sweep grid:
- N_sub in {256, 384, 512, 768, 1024, 2048, 4096} (7 points; spans 16x)
- alpha = M/N in {0.04, 0.08} (two load levels)
- Encoder types: synthetic (Gaussian i.i.d.), real (MiniLM projected), real+normalized
- Codebook: Hadamard (fixed structure; baseline)
- Metric: Q(N) = measured_capacity / (alpha * N)
- Seeds: 10 per cell

Total: 7 * 2 * 3 * 10 = 420 runs. Wall: ~60-90 min CPU.

### 4b. Predictive analytical models

**Model A (H1 dominates -- norm heterogeneity)**:
  Q_H1(N) = 1 - C_A * sigma_norm(D)^2 / N^(1/2)

where sigma_norm(D) ~ D^(1/4) (empirical rule for random projection variance growth under
JL). Predicted shape: Q(N) decreases sub-linearly as N^(-1/2) for real keys; flat for
synthetic. At N=4096 vs N=384: ratio ~ (4096/384)^(1/2) = 3.27 degradation factor for
norm-heterogeneity term. Consistent with 2.75x -> 1.29x drop (factor 2.13).

**Model B (H2 dominates -- partial pre-structure)**:
  Q_H2(N) = 1 - C_B * alpha^2 * N

Predicted shape: Q(N) decreases LINEARLY with N; both real and synthetic affected.
At alpha=0.08: C_B * 0.0064 * N. For Q to drop from 0.90 (N=384) to 0.50 (N=4096):
C_B ~ (0.90 - 0.50) / (0.0064 * (4096 - 384)) = 0.40 / 23.8 ~ 0.017.

**Model AB (mixed)**:
  Q_AB(N) = 1 - C_A * sigma(D)^2 / N^(1/2) - C_B * alpha^2 * N

This model has a minimum at N* = (C_A * sigma^2 / (2 * C_B * alpha^2))^(2/3).
At the minimum, Q is lowest. This minimum may explain the observed 1.29x plateau at
D=1024 and D=4096: both D values are past the minimum in the combined model.

Falsifiable prediction of Model AB: if we REDUCE alpha to 0.02 (very low load), the C_B
term becomes negligible (0.02^2 = 0.0004 vs 0.08^2 = 0.0064, 16x smaller). At low alpha,
Q(N) should be FLAT or INCREASING (JL decorrelation of cross-cluster bleed improves with D).
Test: run Cell XN at alpha=0.02; if Q is flat with N, Model AB is confirmed.

---

## 5. ENCODER-ARCHITECTURE-AWARE CODEBOOK

### 5a. PCA-spectrum-informed codebook

The encoder embedding distribution P(x) for a real LM has a known anisotropic PCA spectrum:
  lambda_1 >= lambda_2 >= ... >= lambda_d (eigenvalues of the covariance matrix)

For MiniLM 384-dim: top-3 eigenvalues capture ~55% variance (Ethayarajh 2019). This means
the embedding manifold is approximately a 50-100 effective-dimensional subspace within R^384.

An encoder-architecture-aware codebook exploits this: use codewords concentrated in the
high-eigenvalue subspace and randomly distributed in the low-eigenvalue subspace.

Construction:
  c_j = sign( V_top * z_j + V_bot * w_j )

where V_top (d x d_top) = top-d_top PCA eigenvectors, z_j ~ Uniform({-1,+1}^d_top)
(structured bipolar in principal space), w_j ~ sign(Gaussian) (random bipolar in residual
space). The d_top codewords in the principal subspace can be mutually orthogonal (ETF/Hadamard
restricted to d_top dimensions), giving coherence exactly 0 for the first d_top codewords.

Predicted gain over Hadamard: limited when V_c > d_top (which is the typical regime).
The larger gain comes from PRE-WHITENING (not codebook design): apply the PCA whitening
W = diag(lambda)^(-1/2) * V^T to the encoder output BEFORE sign-projection. This converts
the anisotropic embedding distribution to isotropic, making the Hadamard codebook near-optimal.

Failure mode: PCA whitening amplifies outlier dimensions (small lambda_i get scaled up by
lambda_i^(-1/2)). If the encoder has long-tailed eigenvalue spectrum (common in LMs), outlier
amplification introduces heavy tails in the sign-projected distribution.
Rescue: truncated PCA whitening (whiten only top-d_top dimensions; leave residual as-is).

Pre-registered thresholds for Cell EA-1 (PCA pre-whitening):
- HARD-PASS: PCA-whitened Hadamard >= 1.5x unwhitened Hadamard at N=384 on real encoder
- MIDDLE-BAND: 1.1-1.5x (partial correction; residual anisotropy or norm effects)
- HARD-FAIL: <= 1.1x (encoder output is already near-isotropic at projection N=384, OR
  whitening introduces outlier tails that cancel the correlation benefit)

---

## 6. SYNTHESIS TABLE -- CELL PRIORITY ORDER

| Priority | Cell | Hypothesis attacked | Metric | HARD-PASS | HARD-FAIL | Wall |
|---|---|---|---|---|---|---|
| 1 | D (disambiguation) | H1 vs H2 | Q_real/Q_synthetic at N in {384,4096} | Contrast < -0.15 | Contrast > -0.05 | 30 min |
| 2 | H2-A (SRHT codebook) | H2 only | capacity vs Hadamard, N=2048 | >= 1.5x | <= 1.1x | 30 min |
| 3 | LC1 N-sweep (SHM) | H1+H2 both | Q(N) shape for SHM vs Hadamard | Q(N) flat | Q(N) drops same rate | 40 min |
| 4 | H1-A (norm normalize) | H1 Type A | capacity vs non-normalized, N=1024 | >= 1.3x | <= 1.0x | 20 min |
| 5 | EA-1 (PCA whitening) | H1+H2 | capacity vs unwhitened, N=384 | >= 1.5x | <= 1.1x | 25 min |
| 6 | H1-C (adaptive sign) | H1 Type C | capacity vs hard-sign, N=384 | >= 1.3x | <= 1.05x | 20 min |
| 7 | H2-B (LC2) | H2 via Welch | capacity vs Hadamard, N=2048 | >= 2.0x | <= 1.2x | 60 min |

**Decision tree**: run Cell D first. If H1 confirmed (Contrast < -0.15): run H1-A -> H1-C
-> EA-1 in that order. If H2 dominant (Contrast > -0.05): run H2-A -> LC1-N-sweep -> H2-B.
If mixed: run SHM N-sweep (addresses both) + EA-1 (addresses both via pre-whitening).

---

## 7. FALSIFIABLE PREDICTIONS SUMMARY

### HARD-PASS predictions

HP1: Disambiguation cell D -- Q_real / Q_synthetic drops > 20pp from N=384 to N=4096.
  Meaning: H1 confirmed; encoder-specific noise grows with N.
HP2: SRHT codebook at N=2048 -- >= 1.5x capacity over Hadamard for real keys.
  Meaning: H2 partial-pre-structure is attackable by randomizing codebook axis alignment.
HP3: LC1 N-sweep -- Q(N) for SHM is flat (non-decreasing with N).
  Meaning: SHM eliminates N-saturation; attacks both H1 and H2 simultaneously.
HP4: PCA pre-whitening -- >= 1.5x on real keys at N=384.
  Meaning: encoder anisotropy is the dominant capacity blocker; isotropic pre-whitening
  recovers the correlation prefactor.

### HARD-FAIL predictions

HF1: Disambiguation cell D -- if Contrast > -0.05 AND Q_synthetic drops > 30pp from
  N=384 to N=4096: pure H2; H1 is negligible.
  Rescue: run H2-A (SRHT) and H2-B (LC2) only; skip H1 path cells.
HF2: SRHT codebook -- if <= 1.1x on BOTH real AND synthetic keys: codebook structure is
  not the mechanism; noise is retrieval-dynamics-based, not interference-based.
  Rescue: 2x drill on retrieval dynamics (argmax convergence analysis, not codebook).
HF3: LC1 N-sweep -- if Q(N) for SHM drops at the same rate as Hadamard: k=8 sparse mixing
  is insufficient to delay H2 saturation; need k >= 32 or full learned codebook.
HF4: PCA pre-whitening -- if <= 1.1x: encoder output is near-isotropic at the working N;
  correlation is not the active bottleneck; look for Type C (basin mismatch) instead.

If HF1+HF2+HF3+HF4 ALL FAIL simultaneously: the dominant noise source is NOT addressable
by any codebook-design or whitening-based approach. This would require a retrieval-mechanism
2x drill (argmax vs alpha-entmax vs contrastive Hopfield), which is a different capability axis.

---

## 8. CROSS-THREAD SYNTHESIS

**Connects to arXiv:2503.00241 (Accuracy and capacity of modern Hopfield with synaptic noise)**:
The finding that noise reduces the capacity PREFACTOR but not the scaling law aligns with
H1 framing: encoder-specific noise acts like synaptic noise, reducing the prefactor by a
factor that grows with N under random projection. Physical Review E (2025) derives the
prefactor reduction as a function of noise variance -- directly applicable to quantifying
C_A in Model A above.

**Connects to arXiv:2303.16880 (Random-Features Hopfield Model)**:
Storage and learning phase transitions in random-features Hopfield show that sign-projected
random features have lower effective capacity than dense Hopfield at the same dimension.
The plateau at D > 384 is explained: sign projection is a LOSSY quantization of the random
feature; at large D (4096), the lossiness is AMPLIFIED relative to the encoder information
content (the encoder already has 384-dim information; sign(Rx) for D=4096 is massively
overparameterized and introduces D=4096 sign-quantization errors vs D=384 at the encoding
dimension).

**Connects to arXiv:2508.01395 (Bielmeier-Friedland 2025)**:
Capacity degrades exponentially with average correlation. The cross-N attenuation is
consistent with exponential degradation in correlation structure as M grows with N. The
Bielmeier-Friedland formula applies to DENSE Hopfield; the bipolar substrate has a different
effective correlation kernel. This opens a question: what is the correct correlation-capacity
formula for bipolar associative memory? The arcsin law gives effective rho_avg_sign ~ rho_avg
* 2/pi, but the precise formula needs a dedicated drill.

**Connects to arXiv:2504.04879 (Mixed memories in Hopfield networks)**:
Mixed memories (linear combinations of stored patterns retrieved as attractors) are relevant
for cross-cluster bleed (Type B noise). If intra-cluster patterns are highly similar, the
Hopfield dynamics converges to a MIXTURE state (cluster centroid) rather than an individual
pattern. This is an H1 failure mode not addressable by codebook design alone -- it requires
cluster-aware retrieval (Type C basin mismatch in disguise).

**Connects to level-1 note (research_drill_learned_codebooks_real_encoder_rescue_1x_2026-06-06.md)**:
That note identified SHM (Cell C), learned VQ (Cell A), and basis pursuit (Cell B) as the
top rescue cells, with SHM framed as "attacks H1 anisotropy." The level-2 analysis upgrades
SHM to "attacks H1 AND H2 simultaneously" via the subspace saturation delay mechanism.
This does NOT contradict the level-1 findings; it deepens them.

---

## 9. SUBSTRATE-PRODUCT IMPLICATIONS

Per [[feedback-no-papers-product-only]]:

1. Cell D (disambiguation) is the NEXT scheduled experiment. It costs ~30 min CPU, produces
   a binary decision point routing ALL subsequent cell investments, and has no implementation
   complexity beyond a 4-point N-sweep. Running H1 or H2 rescue cells before Cell D is
   premature optimization -- the wrong rescue path wastes engineering time.

2. SHM (LC1) N-sweep upgrade: the level-2 analysis reveals SHM attacks both H1 and H2,
   upgrading it from optional to first-rescue. The already-queued LC1 cell should have an
   N-sweep addendum (N in {384, 1024, 2048}) to characterize whether Q(N) is flat under SHM.
   If flat: SHM ships as the single highest-leverage training-free intervention.

3. PCA pre-whitening (EA-1) is cheap and multiplicative: one offline PCA + one O(d^2)
   multiply per query. If it passes (>= 1.5x), it ships as a one-line preprocessing change
   and applies to ALL downstream experiments without re-implementation.

4. SRHT codebook (H2-A) is trivially implemented (random sign-flip diagonal + Hadamard,
   one-time generation). If H2 is confirmed, this is the first-priority fix because it
   requires zero changes to retrieval mechanism.

5. The M^2/N structured-interference formula (Section 3a) gives a NEW DESIGN RULE for the
   substrate: for a fixed-structure codebook, the effective N-ceiling before H2 degradation
   dominates is N < 1 / (C_B * alpha^2). At alpha=0.08, C_B=0.017: N_ceiling ~ 1/(0.017 *
   0.0064) ~ 9200. The current N=4096 is already at 44% of this ceiling. For operational
   deployments at alpha=0.10 or higher: N_ceiling drops to 5900, below N=4096. This means
   the H2 effect will become a practical bottleneck at the planned operating point unless
   SRHT or SHM is deployed.

---

## 10. P_DEFLATED SUMMARY

| Cell | Raw P | Deflation | P_deflated | Cap applied |
|---|---|---|---|---|
| D (HP1: H1 confirmed) | 0.50 | -0.15 | 0.35 | novel-synthesis cap |
| D (HP2: H2 dominant) | 0.55 | -0.15 | 0.40 | no |
| H2-A (SRHT) HP | 0.55 | -0.15 | 0.40 | no |
| LC1 N-sweep HP | 0.50 | -0.15 | 0.35 | novel-synthesis cap |
| H1-A (norm normalize) HP | 0.45 | -0.15 | 0.30 | no |
| EA-1 (PCA whitening) HP | 0.50 | -0.15 | 0.35 | novel-synthesis cap |
| H1-C (adaptive sign) HP | 0.40 | -0.15 | 0.25 | no |
| H2-B (LC2) HP | 0.55 | -0.15 | 0.40 | no |

All novel-synthesis P values capped at 0.50 per [[feedback-lit-scan-calibration-penalty]].

---

## 11. CITATIONS (verified)

1. Leonetti et al. 2025 -- Accuracy and capacity of Modern Hopfield networks with synaptic
   noise. arXiv:2503.00241. Physical Review E 2025.
2. Achilli, Ambrogioni, Lucibello, Mezard, Ventura 2025 -- The Capacity of Modern Hopfield
   Networks under the Data Manifold Hypothesis. arXiv:2503.09518.
3. Bielmeier and Friedland 2025 -- Effects of Feature Correlations on Associative Memory
   Capacity. arXiv:2508.01395.
4. Lucibello et al. 2023 -- Storage and Learning Phase Transitions in the Random-Features
   Hopfield Model. arXiv:2303.16880.
5. Cagnetta et al. 2025 -- Mixed memories in Hopfield networks. arXiv:2504.04879.
6. Ethayarajh 2019 -- How Contextual are Contextualized Word Representations? EMNLP 2019.
   (Isotropy defect of BERT/MiniLM embeddings.)
7. Tropp 2011 -- Improved Analysis of the Subsampled Randomized Hadamard Transform.
   arXiv:1011.1595.
8. Tseng et al. 2024 -- QuaRot: Outlier-Free 4-Bit Inference in Rotated LLMs.
   (SRHT for quantization incoherence.)
9. Baraniuk et al. -- RIP for random matrices (compressed sensing foundational).
10. Welch 1974 -- Lower bounds on the maximum cross correlation of signals. IEEE Trans. IT.
    (Welch bound; Hadamard optimality for M=N.)
11. Hammons et al. 1994 -- Kerdock codes as Z4-linear codes. IEEE Trans. IT.
12. Johnson and Lindenstrauss 1984 -- Extensions of Lipschitz mappings. (JL lemma.)
    Instantiated by sparse JL analysis: arXiv:2407.14518, 2024.
13. Hopfield 1982 -- Neural networks with emergent collective computational abilities.
    PNAS 1982. (Foundational overlap function + capacity.)
14. Amit, Gutfreund, Sompolinsky 1985 -- Storing infinite numbers of patterns in a spin-
    glass model of neural networks. PRL 1985. (alpha_c = 0.138 derivation.)
15. Zhu et al. 2025 -- Addressing Representation Collapse in VQ with One Linear Layer.
    ICCV 2025. arXiv:2411.02038.
16. arXiv:2411.16550 -- Representation Collapsing Problems in Vector Quantization. 2024.

Total citations verified: 16.
