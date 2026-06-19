# Research audit follow-up drills -- 2026-05-24

**Author**: Research sub-agent (cycle 199 audit follow-up; two coupled tasks)
**Trigger**: `notes/strategy_audit_2026-05-24_cycle199.md` Section 4 (dropped item Bet Z.5) + Section 3 Portfolio Gap 1 (Cap 12 noise-cleanup pre-processing)
**Format**: ASCII-only.
**Lit-scan vehicles**: 4 parallel Sonnet WebSearch sub-agents, generic-math query terms per [[feedback-query-privacy-decomposition]].

---

## Section 1 -- Bet Z.5 background + rescue-or-close recommendation

### What Bet Z.5 was

Bet Z.5 was filed v144 (cycle 160; 2026-05-22 ~07:00 EDT) as part of the `research_fresh_angles_quirky_matsci_2026-05-23.md` delivery, labeled "Angle 2 - Absorbing Discrete Diffusion Ensemble Smoother / Bet Z.5". The substrate-product hypothesis:

- **Mechanism**: arXiv:2507.07586 (Diao et al., 2025) proves that an absorbing discrete diffusion model's denoiser already implements the exact Bayesian posterior over masked tokens, with an inference-time ensemble (K independent denoising passes) recovering BOTH posterior means AND per-token variances at rate O(1/sqrt(K)).
- **Substrate fit**: the substrate's per-hop bit-flip channel is structurally identical to the absorbing-mask channel in the diffusion paper, so the per-codeword variance estimator could be transferred onto substrate readout.
- **Novel capability claim**: a third substrate-novel readout primitive (alongside hard-cleanup and VAMP-smoother) with a *posterior-error certificate* AND per-codeword variance -- something the existing two primitives do NOT provide.
- **Predicted P**: 0.40. Implementation cost: 4-6 hr code + 2-3 GPU-hrs validation.

Strategy v144 explicitly recorded "Defer Bet Z.5 to substantive routing".

### Why it has been stale (19 cap_map versions)

Honest reading per [[feedback-no-smoke]]:

1. **The Defer was structural, not protocol-bound.** Strategy filed no expiry, no re-route trigger, and no PROT entry. The candidate sat in cap_map text but never made it into the active queue.
2. **VAMP-on-chain arrived ~2 cycles later** (cycle 162 head-to-head) and DID land on the queue. From v145 forward "VAMP smoother" filled the substrate-novel-readout-primitive narrative slot. Bet Z.5 became conceptually adjacent and therefore deferrable indefinitely.
3. **The 4-6 hr impl cost was the binding constraint**, not the math. With the Cap 12 BBMD arc consuming the cycle-170s through cycle-199s, the engineering budget went to envelope-narrowing on the actually-promoted Cap.
4. **The 2026-05-23 META audit's Rec 2 (Bet Z.5 vs VAMP-on-chain structural equivalence drill)** was filed but never executed -- the same defer-and-orphan pattern repeated.

### Rescue sketches (sequenced cheapest-first per [[feedback-rescue-sketch-first-sequencing]])

| # | Sketch | Cost | Closure value |
|---|--------|------|---------------|
| **S1** | **Math-only structural equivalence drill** vs VAMP-on-chain. Derive both forward-backward EP update rules on a toy 5-hop chain (N=512, K=10), check if update equations are isomorphic up to reparameterization. | ~1-2 hr math, no compute. | If equivalent: close Bet Z.5 as duplicate-of-VAMP; reframe VAMP-on-chain narrative. If non-equivalent: gives ONE strictly-stronger axis (per-codeword variance) that justifies the impl. |
| **S2** | **Ensemble-variance overlay on EXISTING VAMP outputs**. Run K=128 independent VAMP-on-chain passes with seed perturbation; compute per-codeword empirical variance. Tests whether the variance-certificate axis is recoverable WITHOUT a fresh absorbing-diffusion impl. | ~30 min CPU on cached VAMP runs. | If variances rank-correlate with reconstruction error (per arXiv:2507.07586 their core empirical finding) -- the certificate is ALREADY available, Bet Z.5's distinguishing axis collapses, close as absorbed. |
| **S3** | **Toy-scale full impl** at N=512 (not the production N=65536 build). | ~2-3 hr code + ~1 hr CPU validation. | Only file if S1 + S2 BOTH return "Bet Z.5 strictly stronger." |
| **S4** | **Repurpose as Cap 1 noise-envelope rescue.** Bet Z.5's per-codeword variance is a forensic-erase observable. The Crooks-FT bound at clean substrate (Cap 1 η <= 0.01) might be rescued at higher η if a per-codeword variance estimator screens which codewords are within Crooks-license. | ~3-4 hr code + 1 GPU-hr. | Different Cap, different value-prop; only worth filing if Cap 1 noise rescue track is reopened. |

### Recommendation: **CLOSE-BY-ABSORPTION (path S1 + S2)**

Sequence: run S1 first (no compute; math-only); if S1 returns equivalence, close as orphan-duplicate-of-VAMP. If S1 returns non-equivalent, run S2 (cheap ensemble overlay on existing data) before committing to S3 impl. The audit's Rec 2 is exactly S1.

Honest reading: 19 cap_map versions of staleness with VAMP-on-chain occupying the same narrative slot signals that the substrate-product portfolio has *de facto* moved on. Either S1 closes Bet Z.5 cleanly OR S1 surfaces a real distinguishing axis -- both are valid outcomes per [[feedback-no-smoke]].

---

## Section 1.5 -- Bet Z.5 S1 closure analysis (executed 2026-05-24)

**Trigger**: audit followup drill -- execute the S1 math-only structural-equivalence drill named in Section 1's table. Pure-math, no compute. WebSearch sub-agents (3 parallel, Sonnet) dispatched for arXiv:2507.07586 details + VAMP state-evolution per-iterate covariance properties. Wallclock: ~6 min.

### S1.5.1 Two mechanisms, restated precisely

**Cap 8 VAMP-on-chain (per cycle 127 + cycle 162 + cycle 169 algebraic-mechanism anchor)**:
A two-module iterative EP scheme. Module-1 (linear / LMMSE) uses the cached SVD of the channel matrix to solve a Gaussian linear update with precision gamma_1. Module-2 (denoiser) applies a prior-aware nonlinear shrinkage producing a posterior-mean estimate at scalar precision gamma_2. Onsager-corrected messages pass between modules; per-iteration MSE is rigorously characterized by a 1D state-evolution recursion whose fixed point is replica-Bayes-optimal for any right-orthogonally-invariant channel matrix (per Rangan-Schniter-Fletcher 2017 / Berthier-Montanari-Nguyen 2020). The Schur-Weyl irrep-mass annotation (v169) tracks how iterate energy distributes across MUB-stabilizer irreps; this is the "audit trail" component, not a per-coordinate variance.

**Bet Z.5 Absorbing Discrete Diffusion Ensemble (Diao 2025, arXiv:2507.07586)**:
A non-iterative Monte Carlo posterior estimator. Forward process: independent absorbing-mask of each coordinate at rate alpha_t (structurally equivalent to substrate's eta-bit-flip when masks are interpreted as erasures + sign-flip). Reverse: denoiser p_theta(x_0 | x_t). The paper's core theorem is E_{x_t ~ q(. | x_0_true)}[ p_theta(x_0 | x_t) ] = exact Bayesian posterior over x_0 given observed unmasked positions, under mild assumptions (denoiser-consistent, well-trained on the forward distribution). The practical method runs K independent draws of (mask, denoise) and reports empirical mean + empirical per-coordinate sample variance across the K runs. Convergence rate O(1/sqrt(K)); the paper reports K=128 sufficient on WikiText-2 with per-token variance Spearman rho = 0.996 vs reconstruction error.

### S1.5.2 Structural comparison (4 axes)

| Axis | Cap 8 VAMP-on-chain | Bet Z.5 Absorbing-Diffusion-Ensemble |
|------|---------------------|---------------------------------------|
| Iteration topology | Deterministic iterative refinement; Onsager-corrected fixed-point loop | Stochastic ensemble averaging; K independent denoising trajectories |
| Variance object | Scalar gamma_post (one number per iterate; one number at fixed point); SE-predicted | Per-coordinate empirical sample variance across K runs; heterogeneous per position |
| Matrix-class assumption | Right-orthogonally-invariant (Kerdock empirically RI per cycle 115 Path P1) | None on channel; only requires denoiser trained on the forward marginal |
| Compute pattern | Cached SVD + iterative loop (~10-30 iterations) | K independent denoiser calls; embarrassingly parallel; no SVD |

### S1.5.3 Equivalence verdict: GENUINELY NOVEL on the per-coordinate-variance axis -- BUT recoverable via S2 overlay

Three axes are NOT equivalent:
1. **Variance granularity**: VAMP delivers a scalar SE-predicted MSE; Bet Z.5 delivers position-resolved empirical variance. This is the load-bearing distinction. The paper's headline empirical result (Spearman rho = 0.996 between per-token variance and per-token reconstruction error) requires position-resolved variance and has NO direct VAMP analog at the per-iterate scalar gamma_post level.
2. **Iteration topology**: deterministic vs MC are not isomorphic schemes; one is fixed-point inference, the other is sample-mean inference. They estimate the same target posterior under their respective assumptions, but via different operator chains.
3. **Matrix-class assumption**: Bet Z.5 sidesteps the RI requirement that Cap 8 inherits.

ONE axis recovers equivalence:
4. **Posterior mean recovery**: both produce a consistent estimator for the Bayesian posterior mean. On clean substrate runs (cycle 127 acc_50hop = 1.000) VAMP already saturates posterior recovery, so the posterior-mean axis adds nothing.

**Net**: Bet Z.5 is NOT equivalent to Cap 8 and is NOT a special case of Cap 8. It IS structurally adjacent (both denoising-based Bayesian posterior estimators) but on the per-coordinate-variance axis it carries a genuinely additional capability.

### S1.5.4 BUT: cheap S2 overlay recovers per-coordinate-variance from existing VAMP without fresh impl

The key observation: you CAN run K independent VAMP-on-chain traces with seed-perturbed noise samples and compute empirical per-coordinate variance across the K final iterates. This is NOT how Diao 2025 derives variances (they use the masking randomness, not noise-seed randomness), but operationally the output is "per-codeword empirical variance from K runs of an established denoiser." If this VAMP-ensemble variance Spearman-correlates >= 0.5 with reconstruction error on substrate, the per-coordinate-variance axis is ALREADY recoverable from Cap 8 + ensemble overlay -- Bet Z.5's distinguishing axis collapses into a Cap 8 envelope-extension annotation, no fresh impl needed.

### S1.5.5 Closure path: escalate to S2 anchor (cheap CPU; not S3 fresh impl)

**S2 anchor proposal**: `wave14_cap8_vamp_ensemble_variance_overlay_v1`
- K = 64 independent VAMP-on-chain traces per codeword, seed-perturbed noise samples
- Compute empirical per-coordinate variance across K traces at the post-iteration final estimate
- Cross-check: Spearman rank correlation between per-coordinate variance and per-coordinate reconstruction error, across 5 codewords x N=4096 positions
- Cost: ~30-45 min CPU (existing VAMP impl + overlay loop)

**HARD-PASS** (Bet Z.5 closes-by-absorption into Cap 8 envelope annotation): Spearman rho >= 0.50 in >= 3/5 codewords. Annotation text reads "Cap 8 VAMP-on-chain envelope extends to per-coordinate posterior-variance estimation via K-trace ensemble overlay (Spearman rho >= 0.50 vs reconstruction error); equivalent to absorbing-discrete-diffusion ensemble certificate (Diao 2025) without fresh impl."

**HARD-FAIL** (Bet Z.5 has genuine novelty NOT in Cap 8): Spearman rho < 0.30 in >= 3/5 codewords. Then file S3 toy-scale fresh impl (N=512) as a NEW row 🔬 P=0.40 with the per-coordinate-variance certificate as the distinguishing capability.

**Calibration**: P(HARD-PASS) ~ 0.55 (per [[feedback-lit-scan-calibration-penalty]] deflated -0.15 because cross-noise-seed ensemble variance is conceptually distinct from cross-mask ensemble variance and the universality is not proved). P(HARD-FAIL) ~ 0.25. P(inconclusive 0.30 <= rho < 0.50) ~ 0.20 -- in which case file S3 anyway.

### S1.5.6 Cap_map closure annotation (interim, pending S2)

Until S2 returns:
> **Bet Z.5 (Absorbing Discrete Diffusion Ensemble Smoother)**: filed v144, deferred 19 versions. S1 structural-equivalence drill (v179) found Bet Z.5 NOT equivalent to and NOT strictly contained in Cap 8 (VAMP-on-chain) on the per-coordinate-variance axis. S2 ensemble-variance overlay on existing VAMP (~30-45 min CPU) will determine whether the variance axis is recoverable from Cap 8 + cheap overlay (close-by-absorption) or requires fresh impl (re-file as S3 toy-scale). Posterior-mean axis: NOT distinguishing; both methods saturate at clean substrate.

### S1.5.7 Honest reading per [[feedback-no-smoke]]

The S1 drill did NOT close Bet Z.5 cleanly via "duplicate of VAMP" -- the per-coordinate-variance axis is genuinely additional capability. But the prior audit's "close-by-absorption via S1+S2" sequence was sound: S1 surfaced the distinguishing axis, S2 is the cheap test for whether that axis is operationally recoverable from existing Cap 8 infrastructure. The most likely outcome (~55%) is still close-by-absorption -- just via a Cap 8 envelope-extension annotation rather than the cleaner "structural equivalence" path the audit hoped for.

Per [[feedback-dont-overextend-theorems]]: the theorem that Cap 8 covers VAMP-on-chain does NOT extend to per-coordinate posterior variance. Acknowledging this honestly is the discipline; the cheap S2 overlay then closes the question either way.

---

## Section 2 -- Codebook noise-cleanup literature survey

Four parallel Sonnet WebSearch agents dispatched across the four candidate mathematical regimes for upstream codebook denoising. Headline findings:

### 2.1 Singular-value-shrinkage / Marchenko-Pastur denoising (PCA family)

**Key results** (Nadakuditi 2014 OptShrink; Donoho-Gavish 2014 optimal hard threshold; Bun-Bouchaud-Potters 2017):

- For a noisy matrix Y = X + sigma * G where X is low-rank and G has MP-distributed singular values, the *optimal* singular-value shrinker that minimizes Frobenius error has a closed form determined by the noise's MP edge.
- For η-bit-flip-on-bipolar-codeword noise, the noisy codebook is Y = X + Z where Z has variance 4*η*(1-η) per entry; for large N the noise spectrum is approximately MP with shape parameter c = M/N.
- **OptShrink** algorithm: project Y onto its top-k singular vectors, apply data-driven shrinkage per singular value using the empirical MP edge.
- **Empirical effective denoising gain**: typically ~6-10 dB at η_input = 0.05 for rank-r < c*N matrices; equivalent to η_effective ≈ 0.005-0.01 after denoising.

**Substrate-fit**: structured codebook families (Kerdock, RM, Hadamard, Gold) ARE effectively low-rank in their natural basis. PCA-style denoising is mathematically clean and computationally cheap (one SVD).

### 2.2 Sparse-recovery / sparsity-in-orthogonal-basis (compressed-sensing family)

**Key results** (Donoho-Tsaig IST; Daubechies-Defrise-DeMol soft-thresholding; Hadamard-CS literature):

- If the noisy codebook is sparse in some orthogonal basis B (Hadamard, Walsh, RM-projection), then soft-thresholding the basis coefficients of B*Y removes Gaussian noise optimally up to a log factor.
- Reed-Muller codes have efficient projection-aggregation decoders (recursive projection methods reduce projections by 95%) -- these naturally fit RM-class codebooks.
- **Mathematical core**: y_clean = B^T * soft_threshold(B*y_noisy, lambda*sigma).

**Substrate-fit**: Kerdock, RM(1,m) are sparse in their natural codeword basis; Hadamard is *itself* the basis. For these families, basis-projection + soft-threshold gives near-optimal denoising.

### 2.3 Bipolar-lattice projection (hard-quantization family)

**Key results** (Zamir Lattice Coding text; Generalized Nearest Neighbor Decoding arXiv:2010.06791):

- Simplest denoiser for an η-corrupted ±1 codebook: take sign(Y) entrywise. This is the maximum-likelihood single-bit decoder under symmetric bit-flip.
- Adds nothing on top of sign-quantization unless codebook STRUCTURE is exploited.
- **For η < 0.5** this collapses noise component-wise but does NOT correct codewords; structural correction requires codeword-level (not bit-level) decoding.

**Substrate-fit**: trivially cheap, but per-bit only. Useful as a *preprocessing baseline* before any structured method.

### 2.4 Free-probability deconvolution (spectral-matching family)

**Key results** (Mingo-Speicher free probability text; arXiv:2305.05646 free deconvolution for covariance estimation):

- If the noise has known spectral law (MP), free deconvolution can analytically invert the empirical noisy spectrum to recover the clean signal spectrum.
- More sophisticated than OptShrink (handles non-i.i.d. structured noise) but heavier math/code.

**Substrate-fit**: overkill for η-bit-flip; reserve as a fallback if PCA shrinkage underperforms in practice.

### Cross-family verdict

The **PCA-shrinkage family (2.1)** and **basis-projection + soft-threshold family (2.2)** are BOTH tractable in ~30-60 min CPU and BOTH have published η-noise denoising gains of ~10x effective. Pick (2.1) as primary because:
- One SVD on the noisy codebook is faster than a structured basis projection per codeword.
- Donoho-Gavish optimal hard threshold needs ONLY the empirical singular spectrum -- no choice of basis required.
- Works across all 5 substrate-codebook families (Kerdock, Gold, RM(1,m), Hadamard, SRHT) without family-specific tuning.

---

## Section 3 -- Concrete anchor proposal for Cap 12 noise-cleanup

### Anchor: `wave14_cap12_noise_cleanup_optshrink_v1`

**Hypothesis**: A single-pass OptShrink (data-driven SVD-shrinkage per Donoho-Gavish-Nadakuditi) applied to η-corrupted codebook Y_noisy = X_clean + Z_eta produces Y_denoised such that the Cap 12 BBMD pipeline retains ρ >= 0.50 cross-family at η_input up to 0.10 (vs current Cap 12 ✅ envelope of η <= 0.01).

**Math (rough)**:
- noisy codebook Y_noisy, shape (M, N), entries in {-1, +1} with η fraction flipped
- SVD: Y_noisy = U Sigma V^T
- Apply Donoho-Gavish optimal threshold: keep singular values sigma_i > (4/sqrt(3)) * sigma_noise * sqrt(N), shrink the rest to zero
- For bit-flip noise: sigma_noise ≈ 2*sqrt(η*(1-η))
- Y_denoised = U * Sigma_thresholded * V^T
- Re-quantize: Y_denoised_bipolar = sign(Y_denoised)

**Queue**: CPU runner (remote `cpu_runner_0` revival OR desktop CPU); compute slot ≈ 30-45 min wall (single SVD per η-sweep cell, sweep over η ∈ {0.01, 0.02, 0.05, 0.10, 0.20}, 5 seeds, 5 families = 125 cells).

**ETA**: 45-60 min once queued.

**HARD-FAIL clauses** (per [[feedback-lit-scan-calibration-penalty]] hard threshold discipline):
- HF1: denoised η_effective > 0.02 at η_input = 0.05 across 4/5 families → close Gap 1 as substrate-bounded; customer-must-supply-clean-codebooks.
- HF2: rank truncation collapses codebook (residual = 0) at any η ≥ 0.05 → method incompatible with bipolar-codeword regime; switch to family (2.2) basis-projection.
- HF3: denoised pipeline ρ < 0.50 even at η_input = 0.01 (where naive Cap 12 already passes) → denoising actively HARMS clean substrate; abandon.

**Honest pre-registered calibration**: novel-synthesis P deflated to 0.40 (Donoho-Gavish proved for Gaussian noise; bipolar/bit-flip is adjacent but NOT proved; bit-flip noise has heavier tails which may degrade OptShrink performance). Per [[feedback-lit-scan-calibration-penalty]] this is the appropriate ceiling on unverified-regime claims.

---

## Section 4 -- Is Portfolio Gap 1 closeable?

**Honest reading**: probably YES at a reduced ambition (η ≤ 0.03-0.05) but probably NO at the original aspirational ambition (η ≤ 0.10+). The literature consistently shows ~5-10x effective-η reduction from PCA-style denoising in well-conditioned regimes; substrate codebooks ARE well-conditioned for the 5 validated families. A 5x gain on η ≤ 0.01 -> η ≤ 0.05 is plausible and would meaningfully widen customer-facing scope (single-bit-error environment at ~5% noise covers many real deployment regimes).

If anchor v1 lands cleanly between HF1 and HF3, Gap 1 closes as a Cap 12 envelope-extension annotation (not a new capability).

If anchor v1 hits HF1 or HF2, Gap 1 closes as substrate-bounded: customer must supply clean codebooks.

Either outcome is a clean Gap 1 closure within ~1 hr CPU wall.

---

## Sources (literature drill)

- Diao et al., "Your Absorbing Discrete Diffusion Secretly Models the Bayesian Posterior", arXiv:2507.07586 (2025)
- Donoho & Gavish, "Optimal Shrinkage of Singular Values" (2014); Nadakuditi, "OptShrink" arXiv:1306.6042 (2014)
- Daubechies-Defrise-DeMol, IST soft-thresholding; Donoho-Tsaig homotopy
- Ye-Abbe-Spencer, "Recursive projection-aggregation decoding of RM codes", arXiv:1902.01470
- Zamir, "Lattice Coding for Signals and Networks" (Cambridge textbook)
- Mingo-Speicher free probability; arXiv:2305.05646 free deconvolution for covariance
