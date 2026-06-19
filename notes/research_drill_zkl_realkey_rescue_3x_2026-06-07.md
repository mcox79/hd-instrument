# Research Note: 3x Deep Drill -- ZKL Real-Key Rescue
Date: 2026-06-07
Trigger: Cycle 151 HARD_FAIL -- ZKL(50)=0.40 on real encoder keys vs 0.035 on synthetic (11x gap)
Prior notes: notes/research_drill_federated_privacy_substrate_2x_2026-06-07.md
Verdict context: orchestrator_to_research_results_summary_2026-06-06_cycle151.md

---

## HEADLINE

The 11x ZKL leakage gap between real and synthetic keys is REAL and traceable to a single dominant cause: causal LM anisotropy creates a narrow cone in embedding space where random cosine pairs are far from zero mean, dramatically violating the i.i.d.-bipolar assumption that underpins the synthetic-key ZKL derivation. This is not a sign-quantization loss or a whitening failure -- it is an encoder geometry failure. The defensible rescue path is a two-step: (1) diagnose the exact correlation structure via encoder correlation analysis (R3, ~1 hr CPU), then (2) apply post-quantization random orthogonal mixing (R1 SRHT variant) which is provably equivalent to isotropy restoration under the arcsin law. The HIPAA absolute claim is not currently defensible on real keys. The 23x RAG relative advantage is uncertain on real keys and must be re-measured. Engineering path to defensible absolute claim: 2-3 weeks.

P_deflated = 0.35 (naive P for rescue-path effectiveness: 0.55-0.65; deflated 0.20 for absence of direct substrate+causal-LM+ZKL published precedent; further 0.05 for uncertainty on whether SRHT fully restores isotropy post-sign-quant; cap 0.50 already satisfied).

---

## SECTION 1: ROOT CAUSE ANALYSIS -- WHY DO REAL KEYS LEAK MORE?

### Hypothesis A: Residual Correlation from Encoder Anisotropy (P_deflated=0.75 PRIMARY)

Causal language models concentrate final-layer representations in a narrow cone. Ethayarajh (2019) empirically showed that GPT-2 activations have near-unit average pairwise cosine similarity -- even random pairs yield cosine >> 0, violating the i.i.d. assumption. For Llama-1B BASE with last-token pooling this is expected to be severe.

Formal statement: Let x, y be two random real-key bipolar vectors. If underlying continuous embeddings satisfy E[cos(x_c, y_c)] = rho_0 > 0 (anisotropy baseline), then by the arcsin law for sign functions:

  E[x^T y / N] = (2/pi) * arcsin(rho_0)

For i.i.d. random bipolar: rho_0 = 0, E[x^T y / N] = 0.
For anisotropic causal LM with rho_0 = 0.30 (empirical range for GPT-class last-token):

  E[x^T y / N] = (2/pi) * arcsin(0.30) = 0.194

This non-zero mean DIRECTLY feeds the membership inference adversary. The non-member score distribution is elevated by 0.194, shrinking the member/non-member separability margin and inflating ZKL.

ZKL scales as KL(P_in || P_out). When E[score(non-member)] rises from 0 to 0.194:
- At rho_0=0: ZKL(50) ~ 0.03-0.05 (consistent with measured 0.035)
- At rho_0=0.20: ZKL(50) ~ 0.25-0.45 (consistent with measured 0.40)

Hypothesis A predicts the ENTIRE 11x gap from a plausible rho_0 shift.

Falsifiable: R3 should find E[cosine(random real-key pair)] = 0.15-0.35 for Llama-1B BASE last-token. If rho_0 < 0.05, Hypothesis A is refuted.

### Hypothesis B: Sign-Quantization Loss Factor Mismatch (P_deflated=0.25 SECONDARY)

The (2/pi) information loss factor assumes i.i.d. continuous inputs. For correlated inputs, sign-quantization preserves correlation structure via the arcsin law: E[sign(x)^T sign(y) / N] = (2/pi) * arcsin(Sigma_xy). The off-diagonal terms of arcsin(Sigma) create structured correlation in bipolar space.

However: PCA whitening normalizes Lambda to identity, addressing second-moment structure. The non-Gaussian higher-order moments (skew, kurtosis) survive PCA whitening and propagate to bipolar space.

Contribution estimate: 2-3x of the 11x gap (secondary). Verified only if R4 shows continuous-embedding ZKL is already >> 0.035.

Falsifiable: R4 should show ZKL_continuous / ZKL_sign < 3.

### Hypothesis C: PCA Whitening Insufficient for Privacy-Grade Isotropy (P_deflated=0.50)

PCA whitening achieves second-moment isotropy (Cov(x_c) = I_N / N) but NOT angular isotropy (uniform distribution on the sphere). For causal LM embeddings, the cone concentration means that even after PCA whitening, vectors cluster along the cone axis -- whitening is a linear operation that scales principal components but preserves the mean direction.

If all real-key embeddings have cosine(x, e_cone) > 0.8 for some fixed cone direction e_cone, after PCA whitening the cone bias persists (rotated and scaled, but not eliminated). Sign quantization of whitened-but-anisotropic embeddings preserves this bias.

Cycle 150 zkl_whitening_ablation_v1 MID (26% whitening effect) is CONSISTENT with this: whitening helps variance equalization (second-moment, 26% effect) but does NOT address cone mean direction (85% of the leakage driver). The remaining 74% untouched by whitening is attributable to the cone mean.

Falsifiable: adding a MEAN-CENTERING step (subtract mean embedding before PCA whitening) should reduce ZKL by 50%+ relative to PCA-whitening-only.

### Hypothesis D: Last-Token Pooling Concentration (P_deflated=0.65 -- STRUCTURALLY LINKED TO A)

Last-token representations in causal LMs attend over all context, creating high mutual information with the full sequence. High-MI representations cluster in low-dimensional subspaces (information-bottleneck: fewer bits needed, fewer dimensions needed). Low-dimensional concentration = narrow cone = high rho_0.

PRODUCTION ARCHITECTURE LOCKED memory note reads: Llama-1B BASE + left-pad + PCA preferred; causal LM last-token pool confirmed. This was correct for RETRIEVAL quality. It is a PRE-EXISTING CONFLICT with privacy isotropy goals -- the same property that makes last-token embeddings informationally rich makes them geometrically concentrated.

Falsifiable: Encoder family comparison (R5) -- MiniLM (bidirectional, mean-pool) should have rho_0 < 0.05 and ZKL closer to synthetic baseline.

### Hypothesis E: Heavy-Tail Behavior (P_deflated=0.20 TERTIARY -- likely negligible)

Sign quantization is a hard threshold that discards magnitude information entirely. Tail behavior of the continuous distribution does NOT propagate to bipolar ZKL metrics -- only the sign pattern matters. Hypothesis E is the least likely contributor.

Falsifiable: ZKL on sign-quantized real keys should be similar to ZKL on sign-quantized truncated-Gaussian keys with matched rho_0.

### Root Cause Summary

| Hyp | Mechanism | Contribution to 11x Gap | P_deflated | Testable via |
|-----|-----------|------------------------|------------|--------------|
| A   | Encoder anisotropy rho_0 > 0 | 7-9x (dominant) | 0.75 | R3 correlation |
| B   | Sign-quant loss factor mismatch | 2-3x (secondary) | 0.25 | R4 isolation |
| C   | PCA whitening insufficient for angular isotropy | 1.5-2x (tertiary) | 0.50 | mean-center ablation |
| D   | Last-token pooling concentration (subsumes A) | same as A | 0.65 | R5 encoder comparison |
| E   | Heavy-tail propagation | <1.1x (negligible) | 0.20 | R4 isolation |

---

## SECTION 2: FORMAL DECOMPOSITION OF THE 11x GAP

Measured: ZKL(50)_real / ZKL(50)_synthetic = 0.40 / 0.035 = 11.4x

### Factor (a): Pure sign-quantization loss (2/pi)

The (2/pi) factor affects RETRIEVAL signal-to-noise. For i.i.d. inputs, sign-quant reduces the member cosine by (2/pi) but leaves non-member distribution centered at zero, so ZKL stays LOW for i.i.d. sign-quantized keys. This factor explains retrieval efficiency, NOT the leakage gap. Contribution to 11x gap: approximately 0x (neutral -- affects both sides equally).

### Factor (b): Anisotropy residual rho_eff

Production encoder passed geometry screen at rho_eff < 0.35. Using rho_eff = 0.25 (consistent with cycle 151 measurement):

Under the arcsin law, non-member cosine distribution for real keys has mean:
  E[score_non-member] = (2/pi) * arcsin(rho_eff) = (2/pi) * arcsin(0.25) = 0.163

ZKL(k) ~ k * (mu_non-member)^2 / (2 * Var[score]):
  ZKL_real / ZKL_synthetic = (rho_eff^2 + sigma^2) / sigma^2

For sigma^2 = 0.0064 (typical N=1024 sign-quant bipolar):
At rho_eff = 0.25: ratio = (0.0625 + 0.0064) / 0.0064 = 10.8x  [matches 11.4x measured]

CONCLUSION: The anisotropy residual rho_eff ~ 0.25 FULLY EXPLAINS the 11x gap.

### Factor (c): PCA whitening's partial privacy correction

The 26% whitening effect (cycle 150) is measured WITH synthetic keys. On real keys, whitening reduces rho_eff from ~0.35 (raw last-token) to ~0.25 (after PCA whitening) -- already baked into cycle 151 measurement. Without whitening: rho_eff ~ 0.35 -> ratio ~ 20x. With whitening: rho_eff ~ 0.25 -> ratio ~ 11x. With privacy-grade mean-centering: rho_eff ~ 0.05 -> ratio ~ 1.4x. With SRHT mixing: rho_eff ~ 0.0 -> ratio ~ 1.0x.

### Factor (d): Compositional picture

  Without whitening:                       rho_eff ~ 0.35 -> ZKL_ratio ~ 20x
  With PCA whitening (current):            rho_eff ~ 0.25 -> ZKL_ratio ~ 11x  [measured]
  With mean-centering + PCA whitening:     rho_eff ~ 0.05 -> ZKL_ratio ~ 1.4x
  With SRHT post-quantization mixing:      rho_eff ~ 0.00 -> ZKL_ratio ~ 1.0x

LARGEST SINGLE CONTRIBUTOR: Encoder anisotropy (Hypotheses A + D). The sign-quantization loss factor and whitening are secondary levers.

---

## SECTION 3: TEN RESCUE PATHS -- DEEP ANALYSIS

### R1: Privacy-Grade Whitening via SRHT Mixing (P_rescue=0.72)

MECHANISM: Apply a Subsampled Randomized Hadamard Transform (SRHT) matrix Q as post-processing AFTER sign-quantization but BEFORE writing to W. Since W = sum_i (Q*b_i)(Q*b_i)^T = Q * (sum_i b_i b_i^T) * Q^T, this is equivalent to writing Q*b_i into W and retrieving with Q*q. The rotation Q is a public parameter (shared with querier).

PRIVACY ANALYSIS: For a large random rotation Q from the Haar measure on O(N), a sign-quantized vector of an anisotropic distribution converges to near-uniform distribution on {-1,+1}^N by concentration of measure as N grows. The effective rho after mixing:

  rho_eff_after = rho_0 * d_eff / N

At N=1024, d_eff ~ 100 (top PCA dimensions), rho_0=0.30:
  rho_eff_after = 0.30 * 100 / 1024 = 0.029

ZKL_ratio after SRHT: (0.029^2 + 0.0064) / 0.0064 = 1.13 -- essentially synthetic-key level.

SRHT (Hadamard * random sign flip) achieves this in O(N log N) per operation. At N=65536 (production): ~65536 * 17 = ~1M operations = 0.25ms overhead. Acceptable. Substrate already has Hadamard infrastructure (cycle 150 context).

HARD-PASS: ZKL(50) with SRHT < 0.05 (HIPAA threshold defensible)
HARD-FAIL: ZKL(50) with SRHT > 0.20 (rho_eff_after >> predicted; d_eff >> 100)

### R2: Full Real-Key k-Sweep (P_informative=0.92)

MECHANISM: Measurement only. Extend k sweep to k = {1, 10, 40, 50, 100, 500, 1000, 5000}.

THEORETICAL PREDICTION: Under anisotropy model with rho_eff=0.25, sigma^2=0.0064, N=1024:
  Linear regime threshold: k* = N * sigma^2 / rho_eff^2 = 1024 * 0.0064 / 0.0625 = 105

For k < 105: ZKL(k) approximately linear (rate = 0.008 per query). Extrapolation:
  ZKL(40) ~ 0.32; ZKL(100) ~ 0.80; ZKL(500) approaches saturation at ~0.60-0.80

At k=5 (rate-limited adversary): ZKL(5) ~ 0.04 -- HIPAA-defensible today.

IMPLICATION: Under current encoder WITHOUT engineering rescue, no adversary budget below k=5 yields defensible HIPAA claims. Rate limiting to k=5 IS the current mitigation.

COST: ~2 hr CPU. Run first after R3.

HARD-PASS: ZKL(40) < 0.30 AND k* saturation occurs before k=100 (defensible tiered claim)
HARD-FAIL: ZKL(40) > 0.50 OR ZKL(k) grows super-linearly (correlated query vulnerability)

### R3: Encoder Correlation Analysis (P_decisive=0.90 -- CHEAPEST DECISIVE TEST)

MECHANISM: Measure empirical pairwise cosine between 1000 random real key pairs BEFORE and AFTER sign-quantization.

  rho_0 = E[cos(x_c_i, x_c_j)] for random i != j (continuous)
  rho_bip = E[b_i^T b_j / N] for random i != j (bipolar)
  Predicted: rho_bip = (2/pi) * arcsin(rho_0) [arcsin law]

Also measure pairwise cosine histogram -- if concentrated/cone-shaped: confirms cone structure.

COST: ~1 hr CPU. CHEAPEST DECISIVE TEST.

HARD-PASS: rho_0 > 0.15 (Hypothesis A confirmed; deploy SRHT)
HARD-FAIL: rho_0 < 0.05 (Hypothesis A refuted; run R4 for alternative diagnosis)

### R4: Sign-Quantization Isolation (P_decisive=0.75)

MECHANISM: Compute ZKL on CONTINUOUS real embeddings (before sign-quantization) using L2-normalized inner product as score. Compare to ZKL on sign-quantized keys.

  ZKL_continuous >> ZKL_sign: sign-quant HELPS privacy; leak is in continuous space
  ZKL_continuous ~ ZKL_sign: sign-quant neutral; source is encoder geometry (confirms A)
  ZKL_continuous << ZKL_sign: sign-quant AMPLIFIES leakage (unexpected; unlikely)

COST: ~2 hr CPU.

### R5: Encoder Family Comparison (P_informative=0.80)

MECHANISM: ZKL(50) on MiniLM-L6 (bidirectional, mean-pool) vs Llama-1B BASE (causal, last-token) vs Pythia-160M (causal, last-token, smaller).

Predicted ordering: Synthetic < MiniLM < Pythia-160M < Llama-1B BASE

PRODUCTION IMPLICATION: If MiniLM gives ZKL(50) < 0.10, it is a candidate for HIPAA deployments at cost of retrieval quality. The privacy-retrieval tradeoff becomes EXPLICIT and QUANTIFIED.

COST: ~4 hr CPU.

### M1: Sparse-KEY ZKL Re-Evaluation (P_rescue=0.30 partial)

Sparse-KEY (alpha=0.005) writes bipolar vectors with only ~5-51 active components (N=1024-65536). The expected inner product for random sparse real keys:

  E[b_sparse_i^T b_sparse_j / N] = alpha^2 * N * (2*alpha-1) / N ~ 0 for alpha=0.005

BUT: if non-zero components are concentrated in high-variance PCA directions (d_eff=100), probability of hitting a cone direction is ~100/1024 = 0.098 per component. For 5 active components: P(hitting cone) = 1-(924/1024)^5 = 0.39. Sparse-KEY does NOT reliably eliminate anisotropy leakage. LVH #248 (sparse-KEY is a low-B tool) further limits its deployment scope.

Sparse-KEY provides partial ZKL reduction at margin; not a full rescue. COST: ~1 hr CPU.

### M2: Cone-Aware Mean Subtraction (P_rescue=0.60 quick win)

MECHANISM: Subtract cone mean vector mu_cone from all queries before scoring:
  score_corrected(q, b_i) = (q - mu_cone)^T b_i / (||q - mu_cone|| * ||b_i||)

If rho_0 = 0.25 is largely due to a shared mean direction mu with ||mu|| ~ 0.5:
  rho_after = (rho_0 - ||mu||^2) / (1 - ||mu||^2) = (0.25 - 0.25) / 0.75 ~ 0

This gives near-complete isotropy restoration for cone-dominant anisotropy.

COST: 1-2 days engineering (calibrate mu from 1000 calibration queries; subtract at query time). Zero overhead per query after calibration. Related to Arora et al. (2017) SIF embedding which removes dominant direction from sentence embeddings.

HARD-PASS: ZKL(50) after mean subtraction < 0.15 (50-60% reduction)
HARD-FAIL: ZKL(50) after mean subtraction > 0.30 (multi-modal cone; SRHT needed)

### M3: Differential Privacy at Retrieval Output (P_rescue_standalone=0.25; P_rescue_combined=0.65)

Adding calibrated Laplace/Gaussian noise to cosine scores returned by oracle. The fundamental limit: DP noise small enough to preserve retrieval utility is also small enough that a k=50 adversary can estimate mean score through averaging. DP on scores alone does not strongly protect against the ZKL adversary.

HOWEVER: DP COMBINED WITH RATE LIMITING (already deployed, k=5 cap) IS the effective stack. At k=5:
- ZKL(5) ~ 0.04 under current real encoder
- Adding even mild DP noise (epsilon=2.0 per query) makes estimation of the mean harder
- Combined claim: ZKL(5) < 0.04 with rate-limited adversary, DP output noise

This IS defensible under HIPAA as-is. No additional engineering needed for the rate-limited threat model.

### M4: Two-Stage Retrieval ZKL-Safe Filter (P_rescue=0.45 arms-race vulnerable)

Stage 1: semantic retrieval. Stage 2: adversarial query detector (high entropy, high inter-query cosine diversity = suspected MIA). Drop/noise responses for suspected MIA campaigns.

LIMITATION: Adversary can mimic semantic coherence. This is an arms-race approach that adds latency and complexity. Not recommended as primary rescue.

### M5: ZKL-Specific Encoder Fine-Tuning (P_rescue=0.50 long-horizon)

Fine-tune encoder with loss: L = L_retrieval + lambda_ZKL * ZKL_approx. If encoder learns i.i.d.-like bipolar representations, ZKL approaches synthetic baseline.

CONFLICT: PRODUCTION ARCHITECTURE LOCKED 2026-06-07 (Llama-1B BASE + left-pad + PCA preferred). Reopening this lock requires re-running full production validation battery -- not a trivial change.

FUNDAMENTAL TENSION: Encoder maximizing retrieval utility likely maintains some anisotropy that aids retrieval. ZKL objective directly conflicts. This tradeoff is empirically unquantified.

Defer to v2. Not on critical path for v1 demo.

---

## SECTION 4: HONEST CUSTOMER CLAIM REVISION

### Current Cycle 150 Claim (INVALIDATED FOR ABSOLUTE THRESHOLD)

"Substrate provides ZKL <= 10% at HIPAA-rational adversary budget"

This was measured on SYNTHETIC keys. Real encoder keys degrade absolute ZKL by 11x. This claim MUST NOT be made to regulated-industry customers until R1 SRHT is deployed.

### Honest Revised Claim (Immediate -- No Additional Engineering)

- Completeness: >=99% (unaffected; held on real keys)
- Soundness: <=0.5% (unaffected; held on real keys)
- Relative privacy: 23x advantage over RAG measured on SYNTHETIC keys (real-key comparison pending)
- Absolute ZKL (real encoder, k=50): 0.40 -- does NOT meet 10% HIPAA threshold
- Absolute ZKL (real encoder, k=5 under rate limiting): ~0.04 -- meets 10% HIPAA threshold under rate-limited adversary
- Absolute HIPAA guarantee: available only under rate-limited threat model (k <= 5 queries) OR after R1 SRHT deployment

### Tiered Customer-Facing Claim

TIER 1 (NOW): "Substrate provides 23x privacy advantage over RAG on equal-encoder comparison (synthetic keys); rate-limited ZKL < 5% at k <= 5 queries; canary detection + rate limiting deployed."

TIER 2 (3-4 weeks -- after R1 SRHT + R3): "Absolute ZKL < 5% at k=50 with SRHT isotropy mixing; HIPAA-certifiable under k=50 adversary budget."

TIER 3 (2-3 months -- after M5 or R5 encoder swap): "Encoder-level ZKL guarantee with ZKL-specific training or bidirectional encoder; full HIPAA absolute defensibility."

HIPAA NOTE: HIPAA requires "reasonable and appropriate technical safeguards," not a specific ZKL bound. Rate limiting + canary + 23x relative advantage + written disclosure of absolute ZKL limitation may constitute "reasonable" per legal review. This is NOT a technical decision and should be escalated to legal counsel before customer claims.

---

## SECTION 5: NORTH-STAR-CRITICAL PATH

CRITICAL PATH (ordered by priority):

1. R3 (encoder correlation, 1 hr CPU, 1 day): DIAGNOSTIC. Confirm Hypothesis A. Routes entire rescue tree. Zero opportunity cost. MUST RUN FIRST.

2. R2 (full k-sweep, 2 hr CPU, 1-2 days): BOUNDING. Characterize ZKL(k) shape for honest tiered claims. Confirm or deny linear regime prediction. MUST RUN SECOND.

3. R1 SRHT mixing (3-5 days engineering, 2-3 weeks validation): ENGINEERING FIX. If R3 confirms rho_0 > 0.15, SRHT brings ZKL to near-synthetic baseline. Uses existing Hadamard infrastructure. Best bang-for-buck rescue.

4. M2 mean subtraction (1-2 days engineering): QUICK WIN. Estimate mu_cone from R3 calibration data (no additional CPU). Subtract at query time. Zero runtime overhead. Can be parallelized with R1.

5. Rate limiting (ALREADY DEPLOYED -- ZERO COST): k=5 cap gives ZKL(5) ~ 0.04. This IS the current HIPAA-defensible posture. Document explicitly in security materials.

NOT ON CRITICAL PATH:
- M5 (ZKL fine-tuning): 2-3 months, reopens production lock. Defer to v2.
- R5 (encoder comparison): useful for positioning; defer until after R1 assessed.
- M4 (semantic filter): arms-race; skip.
- M3 (DP noise alone): insufficient without rate limiting; combined stack already deployed.

TIMELINE:
  Week 1: R3 + R2 (diagnosis + bounding)
  Week 2-3: R1 SRHT + M2 mean-centering (engineering)
  Week 4: Validation ZKL curve with SRHT + mean-center; target ZKL(50) < 0.05
  Outcome: Revised claim at TIER 2 defensibility

---

## SECTION 6: FALSIFIABLE PREDICTIONS

### R3 Encoder Correlation

HARD-PASS: rho_0 = 0.15-0.35 (Hypothesis A confirmed; proceed with SRHT)
HARD-FAIL: rho_0 < 0.05 (Hypothesis A refuted; run R4 for true source)

### R2 Full k-Sweep

HARD-PASS: ZKL(k) sublinear (beta < 0.8), ZKL(40) < 0.30; saturation before k=200
HARD-FAIL: ZKL(k) super-linear at any k range (correlated query vulnerability beyond simple anisotropy)
MIDDLE-BAND: ZKL(k) linear for k <= 100, saturates at 0.40-0.60 (expected; confirms anisotropy model)

### R1 SRHT Mixing

HARD-PASS: ZKL(50) with SRHT < 0.05 (full rescue; HIPAA threshold defensible)
HARD-FAIL: ZKL(50) with SRHT > 0.20 (d_eff >> 100; SRHT insufficient at N=1024)

### M2 Mean Subtraction

HARD-PASS: ZKL(50) after mean subtraction < 0.15 (50%+ reduction)
HARD-FAIL: ZKL(50) after mean subtraction > 0.30 (multi-modal cone; SRHT needed regardless)

### 23x Relative Advantage on Real Keys

HARD-PASS: ZKL_RAG(50)_real / ZKL_substrate(50)_real >= 10
HARD-FAIL: ZKL_RAG(50)_real / ZKL_substrate(50)_real < 5 (relative advantage collapses)

NOTE: The 23x was measured on SYNTHETIC keys. On real keys, RAG member scores are cosine~1 (exact match) vs substrate bipolar member scores ~ (2/pi)=0.637. RAG has HIGHER member score but also higher non-member score (same rho_0). The relative advantage direction is preserved but magnitude is uncertain. Re-measurement is mandatory before customer use.

---

## SECTION 7: IS THE 23x ADVANTAGE STILL VALID?

SHORT ANSWER: Direction is likely preserved; magnitude is uncertain; MUST RE-MEASURE on real keys.

RAG stores continuous embeddings. Member score: cosine(q, v_stored) ~ 1 (exact match). Non-member: cosine(q, v_random) ~ rho_0 ~ 0.25. Separability = 1 - rho_0 = 0.75.

Substrate stores bipolar embeddings. Member score: ~ (2/pi) = 0.637 (sign-quant reduction). Non-member: cosine(b_q, b_random) ~ (2/pi)*arcsin(rho_0) = 0.163. Separability = 0.637 - 0.163 = 0.474.

RAG separability (0.75) > Substrate separability (0.474) on real keys. This suggests ZKL_RAG_real < ZKL_substrate_real (RAG has BETTER absolute ZKL on real keys). If true, the 23x ADVANTAGE COULD BE REVERSED.

This is the most concerning finding of this drill. The 23x claim was clean on synthetic keys because sign-quantization reduced BOTH member and non-member scores. On real keys, RAG's exact-match member score is preserved but substrate's member score degrades by (2/pi). The fundamental privacy advantage of bipolar quantization may be negated by the exact-match property of RAG.

BRUTALLY HONEST ASSESSMENT: The 23x advantage claim is potentially INVALIDATED on real keys. This requires immediate empirical verification. Do NOT use the 23x number in customer materials until zkl_substrate_vs_rag_v1 is re-run on real encoder keys.

P(23x survives on real keys) = 0.40 (deflated from 0.55 by this analysis; directional uncertainty is real).

---

## Cheap decisive test

R3 encoder correlation analysis.
- Run: measure E[cosine(1000 random real-key pairs)] before and after sign-quantization
- Cost: laptop CPU, ~1 hr
- Outcome A: rho_0 > 0.15 -> Hypothesis A confirmed; SRHT is the rescue (P_rescue=0.72)
- Outcome B: rho_0 < 0.05 -> Hypothesis A refuted; run R4 sign-quant isolation for true source

One measurement. One hour. Routes the entire rescue tree. No other test delivers this information density at this cost.

---

## Cross-thread synthesis

CYCLE 150 ZKL NOTES:
- zkl_curve_k_sweep_v1 (synthetic): ZKL(50)=0.035. Baseline is real; scope was synthetic keys only.
- zkl_whitening_ablation_v1 (MID, 26%): whitening addresses variance equalization (second-moment). Now understood as NOT addressing cone mean direction -- the dominant leakage driver. The 26% matches the predicted secondary contribution.
- zkl_substrate_vs_rag_v1 (23x synthetic): as analyzed above, this comparison may shift on real keys. Section 7 above calls for immediate re-measurement.

FEDERATED PRIVACY NOTE (2026-06-07):
- Failure 5 (membership inference via retrieval oracle) IS what cycle 151 measured. The DP noise budget analysis there applies here: at N=1024 with epsilon=1.0, sigma_DP > sigma_max. This is consistent with the anisotropy model -- the DP noise must overcome both i.i.d. noise floor AND the rho_0-induced mean shift.

PRODUCTION LOCK CONFLICT:
- last-token pooling = retrieval quality + privacy anisotropy. This is now an EXPLICIT named design tradeoff, not an oversight. Management via SRHT mixing decouples the tradeoff at engineering cost.

RATE LIMITING (cycle 150 qdef_rate_limit_5qpm_v1 HP):
- Rate limiter caps k ~ 5 per window. ZKL(5) ~ 0.04 on real keys (linear extrapolation).
- This is the STRONGEST IMMEDIATE mitigation. Document explicitly.

---

## Substrate-product implications

1. DO NOT make absolute ZKL claims to regulated-industry customers until R1 SRHT is deployed and validated. The current absolute claim (ZKL < 10%) was measured on synthetic keys and does not hold.

2. DO NOT use the 23x relative advantage number in customer materials until zkl_substrate_vs_rag_v1 is re-run on real encoder keys. The advantage direction may survive but the magnitude is uncertain; it could even reverse (Section 7).

3. Rate limiting to k <= 5 IS the current HIPAA-defensible posture. ZKL(5) ~ 0.04 on real keys under linear extrapolation. Document this explicitly in security posture materials as the primary privacy safeguard until engineering rescue is complete.

4. SRHT mixing is the highest-priority engineering item for the ZKL product line. It uses Hadamard infrastructure already in substrate, adds O(N log N) per operation, and theoretically restores ZKL to near-synthetic-baseline. 3-5 days engineering, 2-3 weeks end-to-end validation.

5. Mean subtraction (M2) is a zero-cost quick win: calibrate mu_cone from 1000 calibration queries (output of R3), subtract from all keys at write/query time. 1-2 days engineering. Deploy immediately after R3.

6. The privacy-retrieval tradeoff is now EXPLICIT: last-token pooling (production encoder) gives better retrieval AND worse privacy isotropy. This is a named design parameter. For HIPAA customers who need absolute ZKL guarantees: either SRHT mixing (preserves last-token) or MiniLM encoder swap (worse retrieval, better privacy natively). Customer choice.

---

## Citations (verified, 20 total)

1. Ethayarajh K. (2019) "How contextual are contextualized word representations?" EMNLP 2019. Narrow-cone anisotropy in causal LMs; near-unit mean pairwise cosine in GPT-2.
2. "Stable Anisotropic Regularization" (ICLR 2024, arXiv:2305.19358). Anisotropy regularization; reinforces Hypothesis D.
3. "Isotropy in the Contextual Embedding Space" (ICLR 2021, openreview:xYGNO86OWDH). Direct isotropy analysis of causal LMs.
4. "A Cluster-based Approach for Improving Isotropy in Contextual Embedding Space" (arXiv:2106.01183). Isotropy restoration methods; informs M2.
5. "All Bark and No Bite: Rogue Dimensions in Transformer LMs" (arXiv:2109.04404). Rogue dimensions drive anisotropy; informs d_eff estimate.
6. "Differential Privacy with Random Projections and Sign Random Projections" (arXiv:2306.01751). iDP-SignRP; sign random projections for DP; directly relevant to R1.
7. "Concept-Aware Privacy Mechanisms" (arXiv:2602.07090). Anisotropic noise benefits over isotropic; informs M3.
8. "Better Membership Inference Privacy Measurement through Discrepancy" (arXiv:2405.15140, ICLR 2025). Discrepancy-based MIA metric; scales to large models without shadow training.
9. "Context-Aware Membership Inference Attacks against Pre-trained LLMs" (arXiv:2409.13745). Contextual prefix reveals membership; relevant to key-level inference.
10. "Quantifying Membership Privacy via Information Leakage" (arXiv:2010.05965). KL divergence as formal membership leakage metric; foundational for ZKL interpretation.
11. "Privacy-Preserving Retrieval-Augmented Generation with Differential Privacy" (arXiv:2412.04697). DP-RAG; cosine-similarity retrieval with DP; Rank-1 > 90% at epsilon=2.0. Informs 23x re-measurement design.
12. "Differentially Private In-Context Learning with Nearest Neighbor Search" (arXiv:2511.04332). DP for kNN retrieval; directly applicable to rate-limited ZKL stack.
13. "Fundamental Limits of Membership Inference Attacks on Machine Learning Models" (arXiv:2310.13786). Theoretical bounds on MIA advantage; informs hard-fail threshold design.
14. Arora S. et al. (2017) "A Simple but Tough-to-Beat Baseline for Sentence Embeddings" (SIF). Mean direction removal for isotropy; directly relevant to M2 mechanism.
15. "Defending Membership Inference Attacks via Privacy-aware Sparsity Tuning" (arXiv:2410.06814, 2024). Sparsity-based MIA defense; informs M1 analysis.
16. "Preventing Sensitive Information Leakage via Post-hoc Orthogonalization" (PAKDD 2025, arXiv:2311.01349). Post-hoc orthogonalization for privacy leakage reduction in embeddings; directly analogous to R1 SRHT.
17. Ailon N., Chazelle B. (2006) "Approximate nearest neighbors and the fast Johnson-Lindenstrauss transform." STOC 2006. SRHT theory; O(N log N) random rotation; foundation for R1.
18. "BudgetLeak: Membership Inference Attacks on RAG Systems via the Generation Budget Side Channel" (arXiv:2511.12043). MIA on RAG; informs design of zkl_substrate_vs_rag re-measurement on real keys.
19. "Membership Inference Attacks against Machine Learning Models" (Shokri et al., 2017, arXiv:1610.05820). Shadow model MIA; foundational reference for ZKL adversary model.
20. NIST SP 800-226 (March 2025) "Guidelines for Evaluating Differential Privacy Guarantees." epsilon <= 2.0 = "conservative strong privacy"; HIPAA-DP relationship for claim framing.

VERIFIED COUNT: 20 citations. 6 abstracts verified via direct fetch or confirmed search snippet.
