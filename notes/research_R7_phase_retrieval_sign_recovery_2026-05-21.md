# Research R7 — Iterative phase retrieval + sign recovery for random ±1 substrate forensics

**Topic.** Strategy's R7 (rehab-routed, Bet 3 closed PROVISIONAL ❌):
random-key iterative charge-flipping forensics added only +0.03 cos over
single-pass SVD baseline (target +0.2). R7 asks: which iterative
algorithms for sign / phase recovery in random ±1 design matrices could
clear the +0.2 target? Per rehab-routing protocol, this note GENERATES
the ranking independently rather than vetting Strategy's 5 draft
sketches.

**Date.** 2026-05-21.

**Status.** Research note, two passes complete. Pass 1 used a **real
external literature scan** via Agent subagent (~5 min, 24 tool uses,
21+ verified citations 2018-2026). Seventh consecutive cycle following
post-audit protocol.

**HEADLINE finding from lit scan (front-and-center per
[[feedback-no-smoke]])**: the most parsimonious explanation for
charge-flipping's +0.03 result is **not** algorithm failure but
**BBP-threshold ceiling at substrate's SNR**. No iterative algorithm
can clear that ceiling without an additional prior (structured keys,
sparsity, semi-supervised labels). **Before algorithm-shopping, R7
recommends verifying the BBP ceiling.**

---

## Pass 1 — External literature scan (verified)

Generic signal-processing queries via subagent: "phase retrieval
iterative algorithm Wirtinger flow," "1-bit compressed sensing sign
recovery," "approximate message passing AMP," "charge flipping
crystallography algorithm," "BBP transition spiked matrix," etc.
No substrate fingerprint.

### 1.1 The honest BBP-ceiling diagnosis (most important finding)

**The lit scan's most important conclusion**: charge-flipping's +0.03
improvement over SVD is **in-distribution for iterative refinement
methods** applied to a problem near the BBP threshold (Baik-Ben Arous-
Péché 2005). Most iterative phase-retrieval methods buy 0.05–0.15
cosine on top of spectral init when the spectral init is suboptimal;
when the spectral init is *already near the information-theoretic
limit*, no refinement helps because the missing information isn't in
the measurements.

**The substrate-critical question** (per the lit scan's brutal-honesty
section): "is the cos=0.31 (low K) / 0.09 (high K) baseline already
near the information-theoretic limit at the substrate's operating
SNR? If yes, no algorithm in the literature will clear +0.2 without
additional priors."

**Per [[feedback-no-smoke]]**: this needs to be tested BEFORE
algorithm-shopping. The substrate's R7 target may be physically
unreachable.

### 1.2 Phase retrieval — the foundational algorithm landscape

Classical alternating-projection lineage (Gerchberg-Saxton 1972;
Fienup HIO 1982) generalized by **Elser difference map** (2003,
arXiv:math/0111080, J. Opt. Soc. Am. A20) — a one-parameter family
unifying many projection algorithms.

Modern lineages:
- **Convex SDP**: PhaseLift (Candès-Strohmer-Voroninski 2013) lifts
  x to xx*; O(n²-n³) cost prohibitive at moderate n. PhaseMax
  (Goldstein-Studer 2018, arXiv:1610.07531) non-lifting convex,
  whose dual is basis pursuit.
- **Non-convex gradient**: Wirtinger Flow (Candès-Li-Soltanolkotabi
  2015, arXiv:1407.1065) — O(n log n) Gaussian measurements via
  spectral init + gradient descent. Truncated/Reshaped WF
  (Zhang-Liang 2016, arXiv:1605.07719) drops to O(n).
- **Alternating minimization**: AltMin (Netrapalli-Jain-Sanghavi
  2013, arXiv:1306.0160) alternates phase estimation and
  least-squares.

### 1.3 1-bit compressed sensing — the closer match

The substrate has **sign measurements** (sign of cosine), not
amplitude. 1-bit CS theory:

- **Boufounos-Baraniuk 2008** introduced 1-bit CS.
- **Plan-Vershynin 2013** (arXiv:1109.4299) proved s-sparse vectors
  recoverable from O(s log(n/s)) single-bit LP measurements; robust
  to random bit flips up to rate 1/2 - ε.
- **BIHT** (Binary IHT; Jacques-Laska-Boufounos-Baraniuk 2013) —
  state-of-the-art empirically; projected sub-gradient.
- **NBIHT** (Friedlander-Jeong-Plan-Yilmaz 2020, arXiv:2012.12886) —
  optimal error decay O(k/ε) in measurements.
- **BIHT optimal sample complexity proved** (Matsumoto-Mazumdar 2022,
  arXiv:2207.03427).
- **Robust 1-bit IHT with heavy-ball momentum** (2023, arXiv:2310.08019).
- **AMP for 1-bit CS with parameter estimation** (Huang-Schniter 2020,
  arXiv:2007.07679).

**Sample complexity for random ±1 (Bernoulli) measurements**: same
scaling as Gaussian up to mild constants per Ai-Lyubarskii-Plan-
Vershynin.

### 1.4 Charge-flipping family (materials physics iterative)

The substrate's prior attempt used Oszlanyi-Suto charge flipping.
Better family members:

- **Elser difference map** (2003): generalization of HIO; works in
  arbitrary feasibility geometry.
- **RAAR** (Luke 2005): relaxed averaged alternating reflections;
  superior stagnation properties.
- **HPR (Hybrid Projection-Reflection)** (Bauschke-Combettes-Luke 2003).
- **Charge-flipping improvements**: Wu-Spence dynamical threshold,
  Coelho CF + tangent formula, **band-flipping** (relaxes positivity
  to allow negative scatterers — relevant for bipolar substrate).
- **IUCr 2024 review** (journals.iucr.org/d/issues/2024/11/00/nz5017):
  systematic comparison of HIO, RAAR, difference map, HPR in
  crystallographic phase retrieval.

**Critical observation from lit scan**: charge-flipping assumes
**atomicity/sparsity in direct space**. Substrate's recovery target
is **DENSE BIPOLAR codes**, not localized peaks. **The CF prior is the
wrong prior for the substrate's problem.** This may explain the +0.03
result more than algorithmic limits do.

### 1.5 Approximate Message Passing (AMP)

The modern Bayesian-flavored approach:

- **AMP** (Donoho-Maleki-Montanari 2009): canonical compressed-sensing
  algorithm.
- **GAMP** (Rangan 2011): generalized linear models including 1-bit.
- **VAMP** (Rangan-Schniter-Fletcher 2017, arXiv:1610.03082): works
  under **right-rotationally invariant matrices** (much broader than
  i.i.d. sub-Gaussian); per-iteration cost similar to AMP after an
  SVD. **THIS IS THE KEY FIT for random ±1 outer-product structure.**
- **1-bit AMP with parameter estimation** (Huang-Schniter 2020).
- **VAMP for sparse superposition codes** (arXiv:2202.04541, 2022).
- **AMP for rotationally invariant matrices** (Fan-Lelarge-Ma 2022).

**State evolution**: VAMP matches the replica-MMSE for
right-rotationally invariant A. **Tight to the information-theoretic
limit when prior is well-specified.**

### 1.6 Low-rank-plus-sparse and OptShrink

For rank-K signal recovery from a noisy matrix:

- **Robust PCA / PCP** (Candès-Li-Ma-Wright 2011, arXiv:0912.3599):
  convex L+S decomposition.
- **OptShrink** (Nadakuditi 2014, arXiv:1306.6042): data-driven
  optimal singular-value shrinkage via random-matrix theory;
  **outperforms convex regularization on rank-K recovery**.
- **Reweighted quasi-norm RPCA** (2024, arXiv:2403.18400).
- **Adaptive WLS RPCA** (2024, arXiv:2412.14629).

**Key gap from lit scan**: "for rank-K *signed* factorization
specifically, the literature is thin — no widely-adopted analog of
OptShrink that integrates a discrete-output prior. **This is a
genuine gap.**"

### 1.7 1-bit matrix completion (the family the lit scan flagged as
missed)

The substrate's recovery target is a RANK-K MATRIX (factor matrices
v_i, k_i), not sparse vectors. The right algorithmic family may be
**1-bit matrix completion** (Davenport-Plan-van den Berg-Wootters 2014,
arXiv:1209.3672). The lit scan acknowledged this thread was not fully
explored — it may be more relevant than 1-bit CS.

### 1.8 Random ±1 measurement matrices

- ±1 (Bernoulli) random matrices satisfy RIP with m = O(K log(n/K))
  rows (Baraniuk-Davenport-DeVore-Wakin 2008).
- **Strong RIP** for Bernoulli matrices (Chen et al. arXiv:1702.01096).
- ±1 vs Gaussian for sparse recovery: <5% difference in transition
  curves; ±1 slightly higher worst-case coherence but identical
  scaling.
- Random ±1 keys saturate the **Welch bound** in expectation; concrete
  realizations leak factor-of-2.

### 1.9 Materials physics analog (BBP transition is the load-bearing one)

The substrate's W = Σ v_i k_i^T with random ±1 keys IS a spin-glass
outer-product matrix. The relevant physics:

- **BBP transition** (Baik-Ben Arous-Péché 2005): top eigenvalue of
  spiked matrix leaves bulk when signal SNR exceeds threshold;
  **governs fundamental recoverability of rank-K structure from W**.
  This is **exactly the regime** for SVD-then-sign-rounding.
- **Inverse Ising problem** (Roudi-Aurell-Hertz 2009; Cocco-Monasson
  2011 arXiv:0811.3574): recover J_ij couplings from samples;
  small-correlation expansion outperforms mean-field on SK model.
- **Replica method** (Mézard-Parisi-Virasoro): asymptotic analysis of
  spin-glass-like recovery.
- **AMP literally IS TAP equations** (Thouless-Anderson-Palmer) with
  Onsager correction. The spin-glass and AMP communities are talking
  about the same algorithm in different notation.
- **Fyodorov 2018** (arXiv:1805.06982): spin-glass reconstruction of
  nonlinearly encrypted signals; threshold γ_c with p_∞ ~ (γ_c - γ)^(3/4).

**The load-bearing claim**: substrate forensics performance is set by
where its SNR sits relative to the BBP threshold. Below BBP, no
algorithm helps. Above BBP, spectral init ± refinement asymptote at the
information-theoretic limit. **Charge-flipping's +0.03 is consistent
with operating near (but above) the BBP threshold.**

---

## Pass 2 — Substrate-specific drill (independent rescue ranking)

Per rehab-routing protocol, generate ranking from first principles +
lit scan, not from Strategy's draft.

### 2.1 Decomposing the rescue space

Three orthogonal axes:
- **Better spectral init** (BBP-aware): OptShrink, reweighted SVD
- **Bayesian iterative**: VAMP, 1-bit AMP — replica-tight when prior
  is well-specified
- **Discrete-constraint projection**: BIHT, AltMin with bipolar
  projection, difference-map with sign projection
- **Structured-key prior** (changes problem, not algorithm): use
  Kerdock keys per Bet C ✅; turns random-±1 into structured-±1

### 2.2 Independent rescue ranking (10 candidates)

Ranking criteria: (a) **predicted improvement over current cos=0.31
(low K) / 0.09 (high K) baseline**; (b) **implementation cost**;
(c) **literature anchor**; (d) **prior-match to substrate's
dense-bipolar target**.

| Rank | Candidate | Mechanism | Predicted Δcos | Cost | Substrate-fit | Literature |
|---|---|---|---|---|---|---|
| **1** | **VAMP with sign-quantized output channel** | Bayesian iterative; right-rotationally invariant ≈ ±1 outer-product | **+0.10 to +0.25** | Medium (SVD + iterations) | High — tight to replica-MMSE | Rangan-Schniter-Fletcher 2017 (arXiv:1610.03082); Huang-Schniter 2020 (arXiv:2007.07679) |
| **2** | **AltMin between rank-K factor + ±1 sign projection** | Discrete-constraint projection on rank-K | **+0.05 to +0.20** | Low (alternating LS + sign rounding) | High — natural for outer-product | Netrapalli-Jain-Sanghavi 2013 |
| **3** | **OptShrink + sign rounding** | Improved spectral init | **+0.03 to +0.10** | Low (closed-form shrinkage) | Medium — improves init, not refinement | Nadakuditi 2014 (arXiv:1306.6042) |
| **4** | **1-bit matrix completion (lit-scan-flagged miss)** | Rank-K from sign observations | **+0.10 to +0.20** | Medium | High — matches the substrate's problem structure | Davenport-Plan-van den Berg-Wootters 2014 (arXiv:1209.3672) |
| **5** | **Elser difference map with bipolar projection** | Replaces charge-flipping with band-flipping-style bipolar projection | **+0.05 to +0.15** | Low (modify CF projection step) | Medium — better than CF for bipolar | Elser 2003 (arXiv:math/0111080); IUCr 2024 review |
| **6** | **BIHT / NBIHT (if sparsity prior holds)** | Sign-measurement IHT | **+0.05 to +0.15** | Low | Low — substrate signals are DENSE, not sparse | Jacques-Laska 2013; Friedlander 2020 (arXiv:2012.12886) |
| **7** | **PhaseMax / convex LP relaxation** | Convex non-lifting phase retrieval | **+0.03 to +0.08** | Medium-high (LP solver) | Medium | Goldstein-Studer 2018 (arXiv:1610.07531) |
| **8** | **Robust PCA with sign constraint** | L+S decomposition | **+0.03 to +0.10** | Medium | Medium | Candès-Li-Ma-Wright 2011 |
| **9** | **Unrolled / score-based diffusion** | Learned-prior iterative | **+0.10 to +0.30** *IF* training data | High (training required) | High *if* trainable | DPS arXiv:2209.14687; UPrime 2024 |
| **10** | **Use Kerdock keys (changes problem)** | Structured-key prior; outer-product becomes Welch-bound-bounded | **+0.30 to +0.60** | High (substrate restructuring) | EXCELLENT — direct result | Bet C ✅; Hammons-Kumar-Calderbank-Sloane-Solé 1994 |

**Top recommendation: Candidate 1 (VAMP)** as the highest-leverage
model-based iterative. **Candidate 10 (Kerdock keys)** is the unequivocal
winner BUT changes the problem from "random-key forensics" to
"structured-key forensics" — the structured-key WHT forensics is already
✅, so this isn't strictly an R7 rescue but a substrate-redesign
recommendation.

### 2.3 Reordering vs Strategy's draft

Strategy's 5 sketches:
1. WH-sparsity → not in my top ranking. Substrate target is NOT
   Walsh-Hadamard sparse; doesn't match the operative prior.
2. Low-rank pre-projection → my **#3 (OptShrink)** family.
3. K-sparse storage → my **#6 (BIHT)** — but downranked because
   substrate signals are dense, not sparse.
4. Hybrid CF+SVD → my **#5 (difference map with bipolar projection)** —
   principled successor to charge-flipping for bipolar targets.
5. Semi-supervised Sayre → **no clear literature anchor**. The lit scan
   flagged this term as "not a standard literature concept."

**Strategy missed entirely** (now in my top 4):
- **VAMP (my #1)** — the modern Bayesian-iterative match for ±1
  outer-product
- **AltMin with bipolar projection (my #2)** — natural for outer-product
- **1-bit matrix completion (my #4)** — exact problem-structure match

### 2.4 Drill on Candidate 1 — VAMP with sign-quantized output

**The substrate-specific math:**

Substrate's W = Σ v_i k_i^T = V K^T where V ∈ {±1}^{N×K}, K ∈ {±1}^{N×K}.
Forensics goal: recover V, K from observation Y = sign(W). This is a
**Generalized Linear Model** problem: y = sign(A·x + noise).

VAMP iterates (Rangan-Schniter-Fletcher 2017):
1. **LMMSE estimate** given prior on (V, K): closed-form via SVD.
2. **Denoising step**: apply prior (bipolar projection) to current
   estimate.
3. **Onsager correction**: subtract bias to maintain Gaussian-like
   distribution.
4. Repeat until convergence.

**Why this is the right tool**: VAMP is provably tight to the
information-theoretic limit (replica-MMSE) under right-rotationally
invariant matrices. The substrate's outer-product matrix is exactly
the regime VAMP was designed for — random ±1 keys give a
sub-Gaussian distribution with sub-Gaussian outer-product structure.

**Predicted Δcos**: +0.10 to +0.25 over SVD baseline. Per state-evolution
theory, VAMP recovers up to the information-theoretic limit; this
delta is what the lit scan predicts the BBP-ceiling allows.

**Critical caveat (per lit scan honest limits)**: "I could not verify
*direct* benchmark numbers for VAMP applied to bipolar outer-product
memories — that's a niche application, and the literature reports
performance on Gaussian/RRI matrices, not specifically on Bernoulli
±1 outer-product structures."

So VAMP is theoretically the right tool, but the substrate is a
specific regime that needs empirical validation. The substrate could
provide the first published characterization of VAMP-for-bipolar-outer-
product.

### 2.5 Drill on the BBP-ceiling verification (precondition)

**Per the lit scan's honest-limits section**, before deploying any
rescue algorithm, the substrate should **verify the BBP ceiling**:

```text
BBP_ceiling_verification:
  # Step 1: theoretical BBP threshold for substrate's regime
  # For W = V K^T + noise, BBP threshold (Baik-Ben Arous-Péché 2005):
  # λ_BBP = √(N · (1 + γ)) where γ = K/N
  # For substrate at K=627, N=4096: γ ≈ 0.153, λ_BBP ≈ 68.6

  # Step 2: measured top-K eigenvalues of W
  eigvals = SVD(W).singular_values[:K]
  # If eigvals[K] >> λ_BBP: information IS recoverable; refinement makes sense
  # If eigvals[K] ≈ λ_BBP: at the ceiling; iterative algorithms hit IT limit
  # If eigvals[K] < λ_BBP: information NOT recoverable from W alone

  # Step 3: information-theoretic minimum MSE via replica analysis
  # For Bernoulli ±1 outer product, replica-MMSE = MMSE_replica(γ, K)
  # Compare current best-cos to (1 - MMSE_replica)^(1/2)
```

**If verification shows substrate is near BBP ceiling**: R7 closes with
the honest finding "iterative algorithms cannot clear +0.2 target at
this SNR; only structural changes (Kerdock keys per Bet C ✅, or more
measurements) help." This is per-[[feedback-no-smoke]] brutal
honesty.

**If verification shows substrate is FAR above BBP ceiling**: deploy
VAMP (Candidate 1) with confidence; expected +0.10 to +0.25.

### 2.6 The Kerdock alternative (Candidate 10 redux)

**The lit scan's bonus finding**: if the substrate switched to
Kerdock-structured keys (per Bet C ✅), the forensics problem changes
fundamentally. Welch-bound coherence + perfect orthogonality at Welch
bound + WHT-spectrum forensics (already ✅) → near-perfect recovery
without iteration.

**Honest read**: R7 is asking the wrong question if the substrate can
adopt Kerdock keys. **Random-key forensics may simply not be a
productive direction** when structured-key forensics is already
✅-validated.

Per [[feedback-rehabilitation-after-rejection]]: I list this as the
high-value alternative axis (#10) not the recommended fix, because
it changes the substrate, not just the algorithm. Strategy should
decide whether random-key forensics is worth chasing further or
whether the structured-key alternative satisfies the use-case.

---

## Specific experimental design (pseudocode)

**Experiments**: Two-stage. Stage 1 verifies BBP ceiling (precondition).
Stage 2 deploys top candidate IFF Stage 1 supports it.

### Stage 1: BBP ceiling verification (`wave14r_R7_BBP_check`)

```text
config:
  N = 4096
  K_sweep = [50, 200, 500, 1000, 2000]  # match prior R7 baseline scan
  seeds = [7, 17, 23, 31, 41]
  bipolar_keys = sample_random_bipolar(N, K)
  bipolar_values = sample_random_bipolar(N, K)

per_seed_K(K, seed):
  V = bipolar_values(N, K, seed)
  K_mat = bipolar_keys(N, K, seed+1)
  W = V @ K_mat.T  # noise-free outer product
  # Note: substrate may add noise; for ceiling check, use noise-free

  # Compute top-K singular values
  U_W, s_W, V_W = SVD(W)
  top_K_singvals = s_W[:K]

  # Theoretical BBP for Bernoulli outer product
  gamma = K / N
  lambda_BBP = sqrt(N * (1 + gamma))

  # Distance from BBP threshold
  ratio = top_K_singvals[-1] / lambda_BBP  # smallest of top-K vs threshold

  # Information-theoretic MMSE bound (replica)
  # For Bernoulli ±1, MMSE_replica = MMSE_replica(gamma, K) (closed form)
  mmse_replica = compute_replica_MMSE(gamma, N)
  cos_information_theoretic_upper_bound = sqrt(1 - mmse_replica)

  return {
    'top_K_singvals_last': top_K_singvals[-1],
    'lambda_BBP': lambda_BBP,
    'ratio': ratio,
    'cos_IT_upper_bound': cos_information_theoretic_upper_bound,
    'cos_current_SVD_baseline': SVD_sign_rounding_cos(W, V, K_mat),
  }

verdict_logic:
  if ratio >= 2.0 and cos_IT_upper_bound > cos_current + 0.20:
    DEPLOY_STAGE_2 = True  # information IS there; refinement worth trying
  elif ratio < 1.5 OR cos_IT_upper_bound < cos_current + 0.05:
    DEPLOY_STAGE_2 = False  # at/near IT limit; no algorithm helps
    R7 CLOSES with finding: "iterative refinement cannot clear +0.2
       target at substrate's current SNR (BBP ratio = X.X, IT upper
       bound = Y.YY)"
```

### Stage 2: VAMP deployment (`wave14r_R7_VAMP_v1`)

ONLY runs if Stage 1 supports it.

```text
VAMP_for_bipolar_outer_product(W, K_init, max_iter=50):
  # Initialize from SVD
  U_W, s_W, V_W = SVD(W)
  V_estimate = sign(U_W[:, :K]) * sqrt(s_W[:K])
  K_estimate = sign(V_W[:, :K]) * sqrt(s_W[:K])

  for iter in range(max_iter):
    # LMMSE step
    V_LMMSE = lmmse_update(W, K_estimate, sigma_noise)
    # Onsager correction + denoising (sign projection)
    V_estimate = sign_project(V_LMMSE - onsager_term)

    # Same for K_estimate
    K_LMMSE = lmmse_update(W.T, V_estimate, sigma_noise)
    K_estimate = sign_project(K_LMMSE - onsager_term)

    if converged: break

  cos_V = cos(V_estimate, V_true)
  cos_K = cos(K_estimate, K_true)
  return mean(cos_V, cos_K)
```

### Smoke test (queue_add gate for Stage 1)

N=512, K_sweep=[50, 200], 1 seed. Target ~5s.
Oracle: BBP ratio computation produces a number; cos_IT_upper_bound is
in [0, 1].

### Self-test (4 synthetic cases)

- Pure rank-1 + zero noise: predict ratio >> 1; IT upper bound = 1.0;
  any algorithm recovers perfectly.
- Rank-K at α >> α_c (above BBP): predict ratio > 1; IT bound > 0.8.
- Rank-K near α = α_c: predict ratio ≈ 1; IT bound = current SVD baseline.
- Random ±1 matrix (no signal): predict ratio < 1; IT bound ≈ 0.

**Wall budget**: Stage 1 ~30s; Stage 2 ~10 min if it runs.

---

## Materials analog (load-bearing — BBP transition + AMP-as-TAP)

The substrate's forensics problem IS a textbook instance of two well-
studied physics phenomena:

**BBP transition** (Baik-Ben Arous-Péché 2005): for the spiked covariance
model, the top eigenvalue leaves the Marchenko-Pastur bulk when signal
SNR exceeds the threshold λ_BBP = √(N(1+γ)) where γ = K/N. This is
the **fundamental information-theoretic limit** for recovering rank-K
structure from a noisy outer-product matrix. **Below BBP, recovery is
impossible.** Above BBP, the limit is determined by the gap.

**AMP = TAP equations**: the lit scan made the connection explicit.
AMP (Donoho-Maleki-Montanari 2009) is mathematically the same as the
Thouless-Anderson-Palmer equations from spin-glass mean-field theory,
with an Onsager correction term to maintain Gaussian-like cavity
distributions. VAMP extends to right-rotationally invariant matrices
(the substrate's regime). **The TAP equations are state-evolution-tight
to the replica-MMSE bound** — i.e., AMP/VAMP achieves the information-
theoretic limit.

**Substrate-prediction consequence (load-bearing)**:

1. **If substrate's W is significantly above BBP threshold**: VAMP
   should achieve cos ≈ 1 - MMSE_replica^(1/2). This is the
   theoretical maximum.
2. **If substrate's W is at/near BBP threshold**: NO iterative
   algorithm can exceed the SVD baseline by more than O(1/√N).
   Charge-flipping's +0.03 is consistent with this regime.
3. **The actual answer depends on substrate's specific α/N/noise**.
   Stage 1 BBP verification answers it definitively.

**Recent rigorous reference**: Spectral Thresholds in Correlated Spiked
Models (2025, arXiv:2510.17561) provides sharper BBP-type thresholds
for non-i.i.d. matrices — substrate's outer-product has correlations
between rows/columns, and the recent literature has the right tools
for analyzing this.

---

## Falsifiable prediction

**Primary prediction (Stage 1, BBP verification):**

At N=4096, K=627 (substrate operating point), random ±1 keys:

- BBP threshold λ_BBP = √(N·(1+0.153)) ≈ √4720 ≈ **68.7**.
- Top-K singular values of noise-free W: predicted to range from
  λ_BBP·√(1+γ) ≈ 105 at top to λ_BBP at the K-th (boundary).
- **Ratio (top_K_singvals[-1] / λ_BBP) predicted ≈ 1.0–1.3** —
  substrate is **at or just above** the BBP ceiling.
- Information-theoretic cos upper bound (1 - MMSE_replica)^(1/2):
  predicted **0.35–0.55**.
- Substrate's current SVD baseline cos = 0.31 (low K) / 0.09 (high K).
- **Gap to IT bound: 0.04–0.24** — **smaller than R7's +0.2 target
  at high K**.

**Honest assessment**: substrate is operating near the BBP ceiling.
R7's +0.2 target is **achievable only at low K** (where the gap to IT
bound is 0.20+). At high K, the +0.2 target exceeds the
information-theoretic limit — **no algorithm can achieve it**.

**Stage 2 prediction (VAMP, conditional on Stage 1):**

If Stage 1 deploys Stage 2:
- VAMP achieves cos ≈ IT upper bound within ±0.05.
- Improvement over SVD baseline: +0.05 to +0.20 (depends on K and
  Stage 1's gap measurement).
- For low K (K ≤ 500): likely clears R7's +0.2 target.
- For high K (K ≥ 1000): likely does NOT clear +0.2 target.

**Kill criterion (R7 close)**:

If Stage 1 verification shows substrate at/below BBP threshold for
operating K, **R7 closes with the brutal-honesty finding**: "random-key
forensics is bounded by BBP; the +0.2 target is theoretically
unreachable. Substrate should adopt structured (Kerdock) keys per
Bet C ✅ if forensics is product-critical."

**Falsifier for the BBP-ceiling diagnosis**:

If Stage 1 shows ratio > 2.0 AND IT cos upper bound > 0.7, BUT Stage 2
VAMP still produces only +0.03 improvement: my diagnosis is wrong;
the BBP analysis isn't the right physics for substrate's regime.
Would warrant escalation to a deeper random-matrix-theory analysis of
the specific outer-product matrix.

**Honest probability calls**:
- P(Stage 1 verification shows substrate at/near BBP at high K)
  ≈ **65–80%**. The lit-scan finding is suggestive.
- P(R7 closes with "BBP-ceiling, no algorithm helps") ≈ **45–60%**.
- P(VAMP clears +0.2 at low K only) ≈ **30–45%**.
- P(VAMP clears +0.2 at high K) ≈ **10–20%**.

---

## Citations

1. **Baik, Ben Arous, Péché (2005). "Phase transition of the largest
   eigenvalue for nonnull complex sample covariance matrices."**
   *Ann. Probab.* 33(5):1643–1697.
   — **BBP transition: foundational result for the substrate's
   information-theoretic ceiling.**

2. **Rangan, Schniter, Fletcher (2017). "Vector Approximate Message
   Passing."** arXiv:1610.03082.
   — VAMP for right-rotationally invariant matrices; the
   substrate-relevant model-based iterative.

3. **Huang, Schniter (2020). "1-Bit Compressive Sensing via Approximate
   Message Passing with Built-in Parameter Estimation."**
   arXiv:2007.07679.
   — AMP variant for sign measurements; parameter estimation
   eliminates prior-misspecification risk.

4. **Donoho, Maleki, Montanari (2009). "Message-passing algorithms for
   compressed sensing."** *PNAS* 106(45):18914–18919.
   — Foundational AMP; the modern-iterative-recovery basis.

5. **Davenport, Plan, van den Berg, Wootters (2014). "1-Bit Matrix
   Completion."** *Inf. Inference* 3(3):189–223. arXiv:1209.3672.
   — **The literature family the lit scan flagged as the closest
   structural match to substrate's problem.** Not yet vetted for
   substrate, but theoretically the cleanest fit.

6. **Nadakuditi (2014). "OptShrink: An algorithm for improved low-rank
   signal matrix denoising by optimal, data-driven singular value
   shrinkage."** *IEEE Trans. Inform. Theory.* arXiv:1306.6042.
   — Data-driven SVD improvement; rank-K recovery via random-matrix
   theory.

7. **Friedlander, Jeong, Plan, Yilmaz (2020). "NBIHT: An Efficient
   Algorithm for 1-bit Compressed Sensing with Optimal Error Decay
   Rate."** arXiv:2012.12886.
   — Modern 1-bit IHT; optimal error decay.

8. **Elser (2003). "Phase retrieval by iterated projections."**
   *J. Opt. Soc. Am. A* 20(1):40–55. arXiv:math/0111080.
   — Difference map; principled successor to charge-flipping.

9. **Goldstein, Studer (2018). "PhaseMax: Convex Phase Retrieval via
   Basis Pursuit."** *IEEE Trans. Inform. Theory* 64(4):2675–2689.
   arXiv:1610.07531.
   — Non-lifting convex phase retrieval.

10. **Plan, Vershynin (2013). "One-bit compressed sensing by linear
    programming."** *Comm. Pure Appl. Math.* 66(8):1275–1297.
    arXiv:1109.4299.
    — Foundational 1-bit CS with LP recovery.

11. **Cocco, Monasson (2011). "Adaptive cluster expansion for inferring
    Boltzmann machines with noisy data."** *Phys. Rev. Lett.* 106,
    090601. arXiv:0811.3574.
    — Inverse Ising; substrate's outer-product W is the same
    mathematical object.

---

## Routing

- **Experiment Dev (E_R7, two-stage)**: this note recommends
  **TWO-STAGE** experiment:
  - **Stage 1: `wave14r_R7_BBP_check_v1`** (precondition,
    information-theoretic ceiling verification) — ~30s wall time.
  - **Stage 2: `wave14r_R7_VAMP_v1`** (VAMP deployment) — ONLY runs
    if Stage 1 supports it; ~10 min wall time.
  This is the cleanest test: Stage 1 either closes R7 ❌ on
  information-theoretic grounds, or unlocks Stage 2.

- **Strategy**: this note GENERATES rescue ranking independently per
  rehab-routing protocol. Reordering vs Strategy's draft:
  - Strategy's WH-sparsity, K-sparse storage: **downranked** —
    substrate signals are dense, not sparse.
  - Strategy's low-rank pre-project: matches my **#3** (OptShrink).
  - Strategy's hybrid CF+SVD: matches my **#5** (difference map with
    bipolar projection).
  - Strategy's semi-supervised Sayre: **no clear literature anchor**;
    excluded from my ranking.
  - **My #1 (VAMP), #2 (AltMin), #4 (1-bit matrix completion) were
    all missing from Strategy's draft.**
  Also proposes cap_map row update: Bet 3 random-key chargeflip
  reframed from "iterative refinement failed" to "iterative
  refinement near BBP ceiling — substrate-physics bound, not
  algorithm-failure". On Stage 1 result: either Bet 3 closes
  ❌-on-physics (clearer than ❌-on-algorithm), or Bet 3 reopens for
  Stage 2 VAMP test.

- **Research (this session, future cycles)**: if Stage 1 closes R7 on
  BBP ceiling, R7 ends with the honest finding "random-key forensics
  is structurally bounded; Kerdock structural change is the only
  path." If Stage 1 supports Stage 2 and VAMP clears +0.2, R7 closes
  ✅ with a substrate-novel VAMP-for-bipolar-outer-product result
  (publishable: lit-scan flagged the regime as unexplored). If VAMP
  also fails, R8 (1-bit matrix completion) is the next candidate.
