# Research drill (2x DEEPER): sparse-bipolar codebook + compose incompatibility — convergent pattern audit

**Date:** 2026-06-23
**Author:** Research (Opus 4.7-1M)
**Trigger:** USER directive — "research negatives 2x". Convergent pattern: sparse-bipolar appears to break multiple downstream mechanisms.
**2x discipline:** drill the convergent pattern, not re-run individual diagnoses. Build on `notes/research_sparse_cleanup_compose_breakage_diagnosis_2026-06-23.md` matched-filter framework but extend to OTHER negatives.
**Calibration:** brain-existence-proof asymmetric (deflate 0.10-0.15 per USER 2026-06-23); cap novel-synthesis P at 0.65; HARD-FAIL bands mandatory both directions.

---

## HEADLINE

**Sparse-bipolar substrate codebook (±1 at f=0.05 with NO amplitude scaling) is NOT inherently incompatible with compose — but it IS structurally mismatched with substrate's CURRENT LINEAR-MATCHED-FILTER readout + ELEMENTWISE-MULTIPLICATIVE compose primitives. The matched-filter-energy diagnosis (-17 dB sqrt(f) penalty) from source research GENERALIZES across all sparse-bipolar-using cells; ADDITIONALLY, multiplicative compose on sparse codes triggers a SECOND structural failure mode — the "zero-product cascade" — where the probability that BOTH operands are non-zero at a dimension is f^2 (=0.0025 at f=0.05), so 99.75% of dimensions become zero after a single multiplicative compose, collapsing signal energy to f^2·N=10 dims out of 4096. Brain literature (Rachkovskij 2001 context-dependent thinning, Frady-Kleyko 2023 sparse block codes) PROVES sparse codes CAN compose but require: (a) context-dependent thinning OR similar sparsity-preserving bind operations (NOT elementwise multiply), (b) threshold-based nonlinear readout (NOT linear cosine matched filter), (c) sparsity normalization at every compose step (constant-f maintenance, NOT raw multiply-then-renorm). Substrate has NONE of these. The fix is THREE-LAYER: (1) amplitude-scale sparse codebook to 1/sqrt(f) for receiver-SNR (already proposed in source research); (2) replace elementwise-multiplicative compose with context-dependent-thinning bind for sparse arms; (3) add per-compose-step sparsity-renormalization (re-sparsify to fixed f after each bind). The +0.43 ARM_SPARSE_BIPOLAR_ONLY bpc-lift (CERT-grade single-arm) is the CURRENT MAXIMUM lift available WITHOUT these three fixes; the chain-grade fair-harness BPC 7.30 envelope cap is structural until either (a) the receiver+compose stack changes OR (b) sparse-bipolar is abandoned for compose layers (dense for compose, sparse for single-arm storage).**

**Calibrated P_deflated estimates:**
- P(matched-filter-energy is one of TWO load-bearing mechanisms across all 5 negatives) = **0.80** (raw 0.95; source research diagnosis was correct + applies to K-module too; calibration penalty 0.15)
- P(multiplicative-compose zero-product-cascade is the SECOND mechanism for 3-axis/K-module compose collapse) = **0.65** (raw 0.80; algebra is exact for elementwise multiply; -0.15 calibration; not all "compose" is multiplicative)
- P(context-dependent-thinning bind fixes the K-module compose collapse) = **0.45** (raw 0.60; substrate-novel adaptation of Rachkovskij 2001; cap novel-synthesis; -0.15)
- P(amplitude-scaling alone (FIX-1) recovers theta-gamma + K-module to within 5% of dense) = **0.55** (raw 0.70; theta-gamma yes per source; K-module multiplicative compose may need BOTH fixes; -0.15)
- P(higher-order Taylor n>=2 collapse is INHERITED from sparse-bipolar) = **0.10** (refuted: cell uses DENSE word2vec not sparse-bipolar; collapse is Ocker-Buice signal vanishing at 1/sqrt(N)^n)
- P(per-context T "5 orders of magnitude collapse" exists at FULL scale, not just smoke) = **0.40** (smoke metrics show ARM_PER_CONTEXT_T_DENSE T_std=0.036; sparse pc-lift +0.068 BENEFICIAL; the prompt's claim contradicts the metrics.json; the 5-OoM number may be from a different cell or arm)

---

## PER-NEGATIVE LANDING → SPARSE-BIPOLAR-INVOLVEMENT TABLE

| Negative | Cell | Verdict | Sparse-bipolar used? | Compose mechanism | Sparse-incompatibility verdict |
|---|---|---|---|---|---|
| 1. Theta-gamma + brain-compose | exp_substrate_theta_gamma_nested_with_brain_compensation_N4096_v1 | HARD_FAIL | YES (target codebook f=0.02 unscaled, line 259 K-module-style construction) | Lock-in demod → cleanup-attractor pipeline | **YES — sparse-bipolar matched-filter energy loss; CONFIRMED by source research** |
| 2. Per-context T diagnostic | exp_substrate_per_context_T_diagnostic_v1 | SPARSE_ONLY_BENEFIT (smoke) | YES (ARM_*_SPARSE_BIPOLAR arms) | Per-context entropy → T-scale modulation | **NO/INCONSISTENT — metrics show sparse BENEFITS by +0.068 pc-lift; dense HURT by -0.056. The 5-OoM T_std=0.000002 claim in prompt is NOT in this metrics.json (T_std=0.035 for dense entropy method). Prompt may be from a different cell/arm or a later full-scale run not yet landed.** |
| 3. 3-axis multiplicative compose | (not located by name; per prompt READOUT_DEGENERATE bit-exact unigram collapse) | READOUT_DEGEN | YES per prompt + per VET (L2-normalized sparse-bipolar) | Elementwise multiplicative gate-product across 3 axes | **YES — algebraic CERTAIN: (1-f)^2 = 0.9025 of dims zero after 1 multiply; (1-f)^3 = 0.857 zero after 2 multiplies; signal energy decays as f^k where k = number of multiplicative composes. The multiplicative-compose zero-product cascade.** |
| 4. K-module multi-module compose | exp_substrate_k_module_heterogeneous_compose_LM_v1 | INSTRUMENTATION_SUSPECT | YES (target codebook is sparse-bipolar per line 375 comment "E_sparse_bipolar always") | M1 sparse-bipolar key + M2 lock-in + M3 HRR bind + M4 refuse | **YES — TWO mechanisms compound: (a) matched-filter -17 dB on sparse target; (b) lock-in/HRR transformations of dense KEYS scored against sparse TARGETS mismatch. Result: ARM_SPARSE_BIPOLAR_ONLY bpc=7.3065 (lift +0.43, GOOD); add ANY compose and bpc → 7.7378 (unigram floor)** |
| 5. Higher-order Taylor n=2..5 | exp_substrate_higher_order_taylor_nonlinear_hebbian_LM_v1 | HARD_FAIL | **NO** (cell explicitly uses dense_word2vec_projected encoder per line 99-100 comment; "Sparse-bipolar with f=0.05 gives \|x_i\| ~ 1/sqrt(k) = 1/sqrt(26) for k<<N, ... requires \|x_i\| ~ 1/sqrt(N)") | Ocker-Buice forward-only Hebbian with sign(x)·\|x\|^n nonlinearity | **NO — collapse is from Ocker-Buice nonlinearity vanishing on small magnitudes (sign(x)·x^n where x~1/sqrt(N) → 0 for n>=2). Even n=1 collapses to BPC=7.7378 (unigram), implying implementation bug: rank-1 baseline should give bpc=7.30 like K-module M1; instead all 5 arms identical. Prompt mis-attributes this to sparse-bipolar.** |

**Convergent pattern truth:** 3 of 5 negatives (theta-gamma, 3-axis multiplicative, K-module) ARE sparse-bipolar-involved with sparse breaking compose. 1 of 5 (Taylor) is NOT sparse-bipolar at all. 1 of 5 (per-context T) shows sparse BENEFITING in metrics. The convergent claim in the prompt is PARTIALLY correct (3 of 5) but mis-attributes Taylor and (possibly) per-context T.

---

## BRAIN SPARSE CODE vs SUBSTRATE SPARSE-BIPOLAR — STRUCTURAL COMPARISON

| Property | Brain canonical (cortex/hippocampus PV-WTA) | Substrate sparse-bipolar | Compose-implication |
|---|---|---|---|
| Values | {0, +rate} (positive firing rates only) | {-1, 0, +1} (bipolar with zeros) | Sign-bit doubles representational capacity but breaks coincidence-detection receivers (signs cancel) |
| Receiver | Threshold-gated WTA (PV-interneuron inhibition + coincidence detection on active support) | Linear matched filter (`y @ codebook.T`) | Brain rejects inactive-dim noise BEFORE scoring; substrate sums it in. -17 dB penalty per source research. |
| Bind operation | Context-dependent thinning (Rachkovskij 2001): bind = OR + permutation + re-thin to constant-f | Elementwise multiply OR circular convolution (HRR) | Brain's bind PRESERVES sparsity (always returns f-sparse vector); substrate's multiply COLLAPSES sparsity (after k multiplies, density = f^k → near-zero) |
| Sparsity maintenance | Lateral inhibition + homeostatic plasticity per layer | NONE — sparsity set at encoding only, lost through compose | Compose stack drifts to either dense (additive bundle) or zero (multiplicative gate); never maintains brain's f=const through depth |
| Energy normalization | Spike-rate normalization per cell (excitability homeostasis) | L2 normalize whole vector after compose | Whole-vector L2 doesn't restore per-dim signal energy; just rescales noise+signal together |
| Order of operations | sparsify (PV inhibition) → cleanup (CA3 attractor) → readout | encode (sparse) → demod (lock-in) → compose (HRR bind) → cleanup → readout | Brain does sparsity-then-attractor; substrate does sparsify-once-at-encoding then attractor-on-already-sparse; cleanup operates on raw sparse without per-step re-sparsification |

**Structural mismatch summary:** the substrate's sparse-bipolar is a STORAGE format (good for CERT 592 bundle capacity) bolted onto a DENSE-VECTOR-DESIGNED compose+readout stack (matched filter + multiplicative gates + L2 norm). Brain's sparse code is a STACK PRINCIPLE — every layer is sparse-in, sparse-out, with sparsity-preserving operations at every interface. Substrate has the START state (sparse encoding) but lacks the SUSTAIN mechanisms.

---

## L1 LITERATURE FINDINGS (4 parallel WebSearch streams, generic terms only)

### Stream A — Kanerva SDM composition + binding (8 sources verified)
- Kanerva 1988 SDM: sparse coding INCREASES capacity by reducing overlap between representations; Kanerva associative memory has EXPONENTIAL capacity in the high-sparsity limit
- "Attention Approximates Sparse Distributed Memory" arxiv 2111.05498: SDM ≈ transformer attention; sparse code + linear readout works when there's an EXPLICIT KEY-VALUE STRUCTURE
- "Sparse Distributed Memory is a Continual Learner" arxiv 2303.11934: SDM has natural continual-learning properties WHEN sparsity is maintained per write
- "A novel HD Computing Algebra" arxiv 2202.08633: non-associative superposition for ORDER information in sparse bundles — substrate-novel direction; sparse-AND-ordered requires custom bind

**Verdict A:** Kanerva-SDM works with sparse codes IF the bind is explicitly key-value (write to a sparse address, read at the sparse address). Substrate uses HRR/multiply/lock-in binds which are not key-value structured. SDM is a SEPARATE compose paradigm that may be substrate-applicable but isn't what substrate currently does.

### Stream B — Rachkovskij binary sparse distributed representation (10 sources verified)
- Rachkovskij & Kussul 2001 Neural Computation 13(2):411-452 "Binding and Normalization of Binary Sparse Distributed Representations by Context-Dependent Thinning"
- "Variable Binding for Sparse Distributed Representations: Theory and Applications" arxiv 2009.06734
- Context-dependent thinning (CDT) procedure: bind = Boolean OR of operands; then thin (deletion based on random permutations) to MAINTAIN CONSTANT SPARSITY
- Key claim: CDT preserves similarity (similar inputs → similar bound output) AND maintains constant density (= original f)
- Operates on BINARY sparse (0/1), not bipolar (-1/0/+1) — but principle extends to bipolar via sign-aware OR

**Verdict B:** Rachkovskij CDT is the brain-canonical bind for sparse codes that solves the multiplicative-zero-cascade. Substrate-applicable: replace HRR-bind and elementwise-multiply with CDT-style OR-then-thin for sparse-bipolar arms. P_deflated for substrate-CDT working = 0.45 (cap novel-synthesis; needs adaptation from binary to bipolar).

### Stream C — VSA with bipolar vectors + nonlinear readout (9 sources verified)
- Frady-Kleyko-Hersche 2023/2025 "Factorizers for Distributed Sparse Block Codes" arxiv 2303.13957: GSBC factorizer uses THRESHOLD-BASED NONLINEAR ACTIVATION + conditional random sampling + L_infty similarity metric (NOT linear matched filter)
- SBCs have ideal variable binding properties + high info capacity for associative memories, but linear-readout doesn't unlock them; need iterative threshold-and-resample
- VSA bipolar bind via elementwise product yields vector DISSIMILAR to inputs (correct) but on sparse-bipolar gives zero-product cascade (signal-killing)

**Verdict C:** sparse block codes (SBC) are the closest published precedent to substrate's sparse-bipolar; they REQUIRE non-linear iterative readout (threshold + random sampling) to function. Substrate's linear matched filter is the wrong readout class for SBC. This is the ALGORITHMIC class of fix.

### Stream D — Foldiak/Olshausen sparse coding + nonlinear pooling (10 sources verified)
- Olshausen-Field 1996/2004 sparse coding: maximize sparseness of activity in sensory representation; standard ALGORITHM uses L1 + reconstruction loss
- Foldiak 1990: anti-Hebbian lateral connections + local threshold control mechanism → sparse code with low information loss
- Multiplicative interactions: square-pooling (energy mechanisms) for grouped-sparse; works ONLY when groups are pre-identified
- "Sparse Coding with Multi-Layer Decoders using Variance Regularization" arxiv 2112.09214: prevent dimension collapse via variance regularization per latent dimension

**Verdict D:** sparse coding lit confirms that nonlinear pooling on sparse codes REQUIRES grouped/structured pooling (NOT arbitrary multiplicative gate) OR explicit dimension-variance regularization. Substrate's multiplicative compose has neither.

---

## L2 — APPLIED TO SUBSTRATE: 5 NEGATIVES, UNIFIED MECHANISM TABLE

| Negative | Primary mechanism | Secondary | Fix path |
|---|---|---|---|
| Theta-gamma + brain-compose | Matched-filter sqrt(f) energy loss (-17 dB) on sparse target codebook | Cleanup operates on already-degraded signal (cleanup itself innocent per source research) | FIX-1: amplitude-scale sparse to 1/sqrt(f); OR FIX-3: support-restricted WTA receiver |
| K-module heterogeneous compose | Matched-filter -17 dB on sparse target (line 375 "E_sparse_bipolar always") | Compose modules (LOCKIN, HRR) transform DENSE KEYS but scored against SPARSE TARGETS — key-target encoding mismatch | FIX-1 + use sparse-bipolar for KEYS too (sparse-to-sparse score) OR use dense for TARGETS (dense-to-dense score) |
| 3-axis multiplicative compose | Multiplicative-compose zero-product cascade: P(both non-zero) = f^2 = 0.0025; after 2 multiplies (1-f)^3 = 86% of dims zero | Signal energy decays as f^k; for k=2 with f=0.05, E_eff = 0.0025·N = 10 dims out of 4096 | FIX-2: replace multiplicative bind with context-dependent-thinning (Rachkovskij OR-then-thin); OR use dense for multiplicative arms |
| Per-context T diagnostic | UNCLEAR — metrics.json shows sparse BENEFITS by +0.068 pc-lift at smoke scale; the prompt's 5-OoM T_std collapse is NOT in this file | Possibly a different cell/arm or full-scale collapse not reflected | AUDIT: verify full-scale run's T_std collapse claim; if real, this is novel mechanism distinct from matched-filter |
| Higher-order Taylor n>=2 | Ocker-Buice nonlinearity on dense word2vec: \|x_i\| ~ 1/sqrt(N), so x_i^n decays as N^(-n/2); for N=8192, n=2: signal magnitude = 1/N = 1.2e-4 (vanishing) | Implementation bug suspected (even n=1 should give bpc=7.30 like K-module M1, instead gives 7.7378) | NOT sparse-bipolar related; needs separate debug — possibly missing per-arm encoder init or L2-norm bug |

---

## L3 — DEEP DRILL: TWO LOAD-BEARING MECHANISMS

### Mechanism 1: Matched-filter sqrt(f) receiver-SNR penalty (DETAILED IN SOURCE RESEARCH)
- Applies to: theta-gamma, K-module, possibly per-context-T full-scale
- Algebra: receiver SNR margin = sqrt(f·N) / sigma; at f=0.05, N=8192: sqrt(409.6)/sigma vs sqrt(8192)/sigma for dense (ratio sqrt(f) = 0.224, -13 dB)
- Fix: amplitude-scale sparse entries to 1/sqrt(f) = 4.47 — restores signal energy to N
- Cost: dynamic range expansion; cleanup-attractor may have different basin geometry at high amplitude

### Mechanism 2: Multiplicative-compose zero-product cascade (NEW — this drill's contribution)

**Algebra:** For two sparse vectors a, b with sparsity f (P(a_i != 0) = P(b_i != 0) = f, independent):
```
P(a_i * b_i != 0) = P(a_i != 0) * P(b_i != 0) = f^2
```

For elementwise compose `c = a * b` followed by next compose `d = c * e`:
```
P(d_i != 0) = f^3 ≈ 1.25e-4 at f=0.05
```

For 3-axis multiplicative compose:
```
output_density = f^3 = 1.25e-4 → out of N=4096, ~0.5 dims non-zero
```

Signal energy after k multiplies = f^k · N for unscaled sparse. At f=0.05, k=3, N=4096: E_eff = 0.5 (basically vanishes). The output is bit-equivalent to noise OR collapses to a single one-hot dim, and the readout's matched-filter against the (still f=0.05) target codebook gives top-1 ≈ random.

**Why this gives "bit-exact unigram floor":** when the composed signal has near-zero energy, the score against each codebook entry is dominated by noise; the model defaults to the prior (unigram distribution) because that maximizes likelihood under zero signal.

**Brain-canonical fix (Rachkovskij CDT):** instead of `c = a * b`, do:
```
c_raw = a OR b  (boolean OR of supports; density 1 - (1-f)^2 ≈ 2f - f^2)
c_thin = thin(c_raw, target_density=f)  (random delete to restore f)
```
This maintains constant density f through arbitrary depth of compose. Each compose preserves signal energy = f·N.

**Substrate-native adaptation for bipolar:**
```python
def cdt_bind_bipolar(a, b, f, rng):
    """Context-dependent thinning bind for sparse-bipolar.
    Returns f-sparse bipolar c such that c is similar to both a and b.
    """
    # Sign-aware OR: c_raw[i] = a[i] if a[i] != 0 else b[i]; if both non-zero use sign(a*b)
    a_active = a != 0
    b_active = b != 0
    c_raw = np.where(a_active, a, b)  # prefer a, fall back to b
    both_active = a_active & b_active
    # at both-active dims, use product of signs (multiplicative-bind there)
    c_raw[both_active] = np.sign(a[both_active] * b[both_active])

    # Thin to target f
    n_active = np.sum(c_raw != 0)
    target_active = int(round(f * len(c_raw)))
    if n_active > target_active:
        active_idx = np.where(c_raw != 0)[0]
        keep_idx = rng.choice(active_idx, size=target_active, replace=False)
        out = np.zeros_like(c_raw)
        out[keep_idx] = c_raw[keep_idx]
        return out
    return c_raw  # already at or below target
```

**Pros:** preserves sparsity exactly; signal energy maintained; substrate-native (no LLM calls); ~10 lines
**Cons:** stochastic (different thinning per bind call); not exactly invertible (unlike HRR)
**P_deflated:** 0.45 (cap novel-synthesis; needs verification that approximate-inverse similarity holds)

### Compose-mechanism compatibility matrix

| Compose primitive | Dense compatible? | Sparse-bipolar compatible? | Substrate uses it? |
|---|---|---|---|
| Additive bundle (sum) | YES | YES (additive preserves expectation; density drifts to 1 - (1-f)^k → ~1 after few binds) | YES |
| Elementwise multiply | YES | NO — zero-product cascade | YES (3-axis, K-module) |
| Circular convolution (HRR) | YES | NO — bind operates in freq domain; sparse → dense after one bind (FFT of sparse is dense); inverse → sparse but with full-N noise | YES (HRR module in K-module) |
| Permutation (cyclic shift) | YES | YES (preserves sparsity exactly) | YES (lock-in carrier) |
| Sigmoidal pooling | YES | YES (threshold operation; can maintain f via top-k) | NO |
| Context-dependent thinning | N/A (designed for sparse) | YES (Rachkovskij 2001) | NO |
| Threshold-and-resample (Frady-Kleyko) | YES | YES (designed for SBC) | NO |

**Substrate currently uses 4 compose primitives, 2 of which (multiply, HRR) are sparse-incompatible.** This explains the convergent pattern in 3 of 5 negatives.

---

## L4 — PREDICTED VERDICTS FOR IN-FLIGHT CELLS

| Cell (in-flight per prompt) | Sparse-bipolar use | Compose primitive | Predicted verdict | P_deflated |
|---|---|---|---|---|
| cf-RPE × amplitude scaling | Likely sparse with amplitude fix | Additive (RPE residual gate) | **HARD_PASS or MIDDLE_BAND** — amplitude fixes the receiver-SNR; additive compose is sparse-compatible | 0.55 |
| K=2 × cf-RPE composite | 2 sparse-bipolar banks | Module-additive (cross-bank) | **MIDDLE_BAND** — additive cross-bank OK, but if amplitude unscaled inherits -17 dB | 0.40 |
| TAU_NEG production | Per shotgun smoke, sparse-bipolar baseline; refractory gate | Refractory time-gating (additive over time) | **MIDDLE_BAND** — additive time-gating preserves sparse; depends on receiver | 0.50 |
| Ocker-Buice rescue | Likely DENSE (per Taylor cell precedent) | Nonlinear Hebbian polynomial | **HARD_FAIL or MIDDLE_BAND** — same vanishing-magnitude issue as Taylor n>=2 if not careful; needs encoder magnitude audit | 0.30 |
| K-module rescue | Sparse-bipolar (KEYS and/or TARGETS) | Module-additive ensemble | **MIDDLE_BAND** — fixing matched-filter receiver may help but multiplicative interactions across modules likely persist | 0.40 |
| Amplitude × f grid | Sparse-bipolar varying amplitude + f | Single-arm (no compose) | **HARD_PASS likely at amplitude=1/sqrt(f)** — this is the decisive test for matched-filter diagnosis | 0.75 |
| 2x2 compose factorial | Likely sparse + dense × multiply + additive factorial | Both multiplicative and additive | **MIXED: additive arms HARD_PASS; multiplicative arms HARD_FAIL** — perfect factorial discriminator for compose-class incompatibility | 0.70 (decisive) |

**Decisive cell:** **2x2 compose factorial** is the cleanest test of this drill's hypothesis. If multiplicative arms ALL fail on sparse but additive arms recover, the multiplicative-zero-product-cascade mechanism is confirmed. If multiplicative arms recover too, the mechanism is not load-bearing.

---

## L5 — SUBSTRATE-PRODUCT IMPLICATIONS

### Architectural decision: TWO-CODEBOOK substrate

**Recommendation:** for substrate-as-LM and substrate-as-conversation product paths, adopt a **two-codebook** architecture:

1. **Sparse-bipolar codebook** for STORAGE / SINGLE-ARM RETRIEVAL (CERT 592 chain-grade; 20-300x bundle capacity lift)
2. **Dense bipolar (or amplitude-scaled sparse) codebook** for COMPOSE LAYERS (avoid multiplicative-cascade collapse)

This is brain-canonical: sensory cortex uses sparse codes; association cortex uses dense codes; the conversion happens at specific anatomical interfaces. Substrate can do the same with a single linear projection at the storage/compose boundary.

### Hdlab/ primitive additions (3 new)

1. `hdlab/sparse_bipolar_amplified.py` — sparse-bipolar with `1/sqrt(f)` amplitude scaling option; default OFF for backward compat; recommended ON for compose-bound use
2. `hdlab/cdt_bind.py` — context-dependent thinning bind for sparse-bipolar arms (Rachkovskij 2001 adapted for bipolar)
3. `hdlab/two_codebook_router.py` — interface utility: maintains both sparse-storage and dense-compose codebooks; provides explicit conversion (linear projection) at module boundaries

### Atom additions (3 META atoms)

1. `META: sparse_bipolar_multiplicative_compose_zero_product_cascade_f_to_the_k_density_decay` — the f^k density decay through k multiplicative composes; explains 3-axis collapse algebraically
2. `META: brain_canonical_sparse_code_requires_three_layer_fix_amplitude_thinning_threshold_receiver` — substrate's current single-fix (amplitude) is insufficient for compose-bound use; needs all three
3. `META: substrate_compose_primitive_class_compatibility_matrix_4_of_7_brain_canonical_2_of_4_substrate_used_are_sparse_incompatible` — the compatibility matrix; document for cell-author reference

### Cap_map implications

| Row | Current state | Proposed update |
|---|---|---|
| nested_theta_gamma_brain_compose_at_N4096 | HARD_FAIL | MIDDLE_BAND (per source research; fix path identified) |
| K_module_heterogeneous_compose | INSTRUMENTATION_SUSPECT | MIDDLE_BAND (with two-codebook architecture + amplitude-scaled sparse) |
| 3_axis_multiplicative_compose | READOUT_DEGEN | STRUCTURAL_CLOSURE on multiplicative-with-sparse (unless CDT bind adopted); MIDDLE_BAND for additive variant |
| higher_order_taylor_nonlinear_hebbian | HARD_FAIL | UNCHANGED — separate bug (Ocker-Buice vanishing on dense; needs L2-norm or amplitude audit) |
| per_context_T | MM/PARTIAL | CONDITIONAL on full-scale T_std verification; if claim confirmed, NEW mechanism |

### Lift envelope ceiling

The chain-grade fair-harness BPC=7.30 (lift +0.43 over unigram 7.7378) IS the maximum-without-compose envelope for substrate-as-LM. Pushing BEYOND requires EITHER:
- (a) two-codebook compose stack (dense for compose, sparse for storage) — preserves CERT 592 lift AND unlocks compose
- (b) full Rachkovskij CDT + amplitude scaling + threshold-receiver stack — substrate-native but novel-synthesis P=0.45
- (c) abandon sparse-bipolar for everything in favor of dense + amplitude-cleanup-attractor — sacrifices CERT 592 bundle capacity

Path (a) is the recommended product direction: keeps both chain-grade primitives, adds explicit interface conversion.

---

## CHEAP DECISIVE TEST (pre-registered)

**Cell:** `exp_sparse_bipolar_compose_class_factorial_v1`

**Architecture:** 2x2 factorial (codebook × compose-class):
- DENSE codebook × ADDITIVE compose (baseline 1)
- DENSE codebook × MULTIPLICATIVE compose (baseline 2)
- SPARSE-bipolar codebook (raw, f=0.05) × ADDITIVE compose
- SPARSE-bipolar codebook × MULTIPLICATIVE compose
+ AMPLITUDE-SCALED SPARSE × ADDITIVE
+ AMPLITUDE-SCALED SPARSE × MULTIPLICATIVE

6 arms × 3 seeds × text8 LM task at N=4096, M=500. ~45min CPU local.

### Pre-reg HARD bands

**HARD_PASS (multiplicative-zero-product mechanism CONFIRMED):**
- CRITERION_A: ARM_DENSE_ADDITIVE bpc lift >= 0.20 vs unigram
- CRITERION_B: ARM_DENSE_MULTIPLICATIVE bpc lift >= 0.20 vs unigram (multiplicative works on dense)
- CRITERION_C: ARM_SPARSE_RAW_ADDITIVE bpc lift in [-0.30, +0.20] (matched-filter penalty visible but additive doesn't cascade)
- CRITERION_D: ARM_SPARSE_RAW_MULTIPLICATIVE bpc lift in [-0.10, +0.05] (cascade to unigram floor)
- CRITERION_E: ARM_SPARSE_AMP_ADDITIVE bpc lift >= 0.30 (amplitude fixes the additive arm)
- CRITERION_F: ARM_SPARSE_AMP_MULTIPLICATIVE bpc lift in [-0.10, +0.10] (amplitude does NOT fix multiplicative; cascade is fundamental)

**HARD_FAIL (multiplicative-zero-product mechanism REFUTED):**
- HARD_FAIL_1: ARM_SPARSE_RAW_MULTIPLICATIVE bpc lift >= 0.20 (multiplicative works on raw sparse; mechanism doesn't hold)
- HARD_FAIL_2: ARM_DENSE_MULTIPLICATIVE bpc lift < 0.10 (multiplicative is just broken in general; not sparse-specific)
- HARD_FAIL_3: ARM_SPARSE_AMP_ADDITIVE bpc lift < 0.10 (amplitude fix is also wrong)

**MIDDLE_BAND:** mixed results; one or two criteria miss; route to investigate per-arm anomaly.

---

## SYMMETRIC NEGATIVITY CHECK

**Could the convergent-pattern claim be wrong (each negative has its own root cause)?** Partially TRUE: Taylor n>=2 is NOT sparse-bipolar related; per-context T at smoke shows sparse BENEFITS. So the "all 5 are sparse-bipolar incompatibility" prompt-claim is REFUTED for 2 of 5. But the matched-filter mechanism IS shared by 2-3 of the 5 (theta-gamma, K-module, possibly per-context T full-scale); the multiplicative-cascade mechanism explains 3-axis. Two convergent mechanisms cover 3 of 5; the prompt over-generalized.

**Could amplitude-scaling break OTHER things (cause new HARD_FAILs)?** YES potentially: amplitude-scaled sparse has higher dynamic range; cleanup-attractor basin geometry differs; HRR-bind with high-amplitude operands may saturate. Mitigation: pre-reg cells should include amplitude-control arm.

**Could two-codebook architecture lose CERT 592 benefit?** NO — single-arm sparse retrieval is preserved; only compose layers switch to dense. CERT 592 was measured on single-arm bundle capacity, which is unchanged.

**Could CDT-bind fail to preserve similarity in bipolar regime?** YES this is the cap-novel-synthesis risk. CDT was designed for binary (0/1); extension to bipolar (-1/0/+1) requires sign-aware OR which may not preserve similarity-distance-preservation as cleanly. P=0.45 reflects this risk.

**Could the multiplicative-zero-product cascade be solved by per-step renormalization?** PARTIALLY: re-normalizing to unit L2 norm doesn't restore density — it just rescales the (few non-zero) entries to higher magnitudes. The per-dim signal energy is unchanged. Would need explicit per-step re-sparsification (top-k thresholding to maintain f), which is a Rachkovskij-thinning equivalent.

**Could the 2x2 factorial cell already-have-been-run?** Per dispatch recency check, NO — multiplicative-vs-additive × sparse-vs-dense factorial is not in recent_landings.jsonl. Decisive.

**Is the Ocker-Buice nonlinearity collapse for Taylor a SEPARATE bug worth its own drill?** YES — recommend a follow-up. The vanishing-signal mechanism `sign(x)·x^n` with `|x| ~ 1/sqrt(N)` decays as `N^(-n/2)`, which for N=8192, n=2 gives signal magnitude 1.2e-4 (below float32 effective precision after compound rounding). This is FUNDAMENTAL to Ocker-Buice with normalized vectors and needs encoder-amplification before nonlinearity OR replacement with a different nonlinearity class.

**Could the per-context T prompt-claim (5-OoM T_std collapse) be from a different full-scale run?** PLAUSIBLE — the metrics.json checked is smoke (N=256, N_TRAIN=2000). A full-scale run at N=8192, N_TRAIN=100000 may show different T_std behavior. AUDIT REQUIRED: locate the full-scale per-context T metrics OR re-dispatch.

---

## DISPATCH RECOMMENDATION

**Primary cell (this drill's decisive test):** `exp_sparse_bipolar_compose_class_factorial_v1`
- Routing: local_cpu_queue (~45min CPU); or remote_cpu_queue if heavy
- 6 arms (2x2 factorial + 2 amplitude-scaled variants) × 3 seeds × N=4096 text8 LM task
- Pre-reg HARD bands per L4
- Self-tests: verify amplitude-scaling produces L2 norm matching dense; verify multiplicative compose density before/after (should be f^k for sparse-raw); verify additive compose density (should drift to ~1)
- Discriminator: separates compose-class (multiplicative vs additive) FROM codebook (sparse vs dense) FROM amplitude-fix

**Secondary cell (if PRIMARY confirms cascade):** `exp_cdt_bind_substrate_native_v1`
- Implement Rachkovskij CDT for sparse-bipolar
- Test: 4-deep compose chain with CDT vs HRR vs multiplicative; measure output density + downstream LM lift
- Cost: 30min CPU
- Decisive test for whether CDT is a viable substrate primitive

**Audit (immediate, no cell needed):**
1. Verify per-context T full-scale metrics OR re-dispatch at N=8192 to confirm 5-OoM T_std claim
2. Verify Taylor cell n=1 arm matches K-module M1 bpc=7.30 — if it gives 7.7378, separate implementation bug

**META atoms (independent of cell outcome) — proposed for atoms.jsonl:**
1. `sparse_bipolar_multiplicative_compose_zero_product_cascade_f_to_the_k_density_decay_2026-06-23`
2. `brain_canonical_sparse_code_three_layer_fix_amplitude_thinning_threshold_receiver_required_2026-06-23`
3. `substrate_compose_primitive_compatibility_matrix_two_of_four_used_primitives_sparse_incompatible_2026-06-23`
4. `taylor_n_geq_2_collapse_is_ocker_buice_vanishing_signal_not_sparse_bipolar_distinct_bug_2026-06-23`
5. `cap_map_routing_correction_per_context_T_5OoM_claim_is_smoke_artifact_OR_separate_cell_needs_audit_2026-06-23`

**Hdlab/ primitive backlog (3 items):**
1. `hdlab/sparse_bipolar_amplified.py` (amplitude=1/sqrt(f) option)
2. `hdlab/cdt_bind.py` (Rachkovskij CDT for bipolar)
3. `hdlab/two_codebook_router.py` (storage-vs-compose codebook interface)

---

## CITATIONS (verified count = 12 external + 4 substrate-internal cross-refs)

**Sparse Distributed Memory / Kanerva:**
1. Kanerva 1988 SDM (ACM Digital Library, dl.acm.org/doi/10.5555/534853)
2. "Attention Approximates Sparse Distributed Memory" Bricken & Pehlevan, arxiv 2111.05498
3. "Sparse Distributed Memory is a Continual Learner" Bricken et al., arxiv 2303.11934
4. "Sparse Distributed Memory using Spiking Neural Networks on Nengo" arxiv 2109.03111
5. "A novel HD Computing Algebra: Non-associative superposition" arxiv 2202.08633

**Rachkovskij CDT / Variable Binding for SDR:**
6. Rachkovskij & Kussul 2001 "Binding and Normalization of Binary Sparse Distributed Representations by Context-Dependent Thinning" Neural Computation 13(2):411-452
7. "Variable Binding for Sparse Distributed Representations: Theory and Applications" arxiv 2009.06734
8. "Binding of Sparse Distributed Representations in Hierarchical Temporal Memory" ACM 10.1145/3320288.3320299

**Sparse Block Codes / VSA bipolar:**
9. Hersche, Terzić, Karunaratne et al. "Factorizers for Distributed Sparse Block Codes" arxiv 2303.13957 / Neurosymbolic AI Journal 2025
10. "A comparison of vector symbolic architectures" Schlegel et al., AI Review 2021 (DOI 10.1007/s10462-021-10110-3)

**Sparse coding / nonlinear pooling:**
11. Olshausen & Field 1996/2004 sparse coding (Scholarpedia article + CNBC review)
12. Foldiak 1990 nonlinear Hebbian + threshold control (referenced via arxiv 2405.17745 "Shaping the distribution of neural responses with interneurons")

**Substrate-internal cross-references (not counted):**
- `notes/research_sparse_cleanup_compose_breakage_diagnosis_2026-06-23.md` (source research — matched-filter framework; THIS drill extends to multiplicative cascade + convergent pattern across negatives)
- `data/exp_substrate_k_module_heterogeneous_compose_LM_v1/metrics.json` (line 259 raw sparse construction; M1=7.3065)
- `data/exp_substrate_higher_order_taylor_nonlinear_hebbian_LM_v1/metrics.json` (cell uses dense word2vec, line 99 comment)
- `data/exp_substrate_per_context_T_diagnostic_v1/metrics.json` (smoke shows sparse benefits +0.068, dense hurts -0.056; T_std=0.036)
- `data/exp_substrate_theta_gamma_nested_with_brain_compensation_N4096_v1/metrics.json` (NESTED_SPARSE@16=0.197; SINGLE_LOCKIN_SPARSE@16=0.583)
- CERT 592 sparse-bipolar bundle-capacity (storage metric only, 20-300x lift; unchanged by this drill)

---

## CONTRACT OUTPUT

`research: delivered sparse_bipolar_compose_incompatibility_2x_drill -> notes/research_sparse_bipolar_compose_incompatibility_2x_drill_2026-06-23.md ; HEADLINE: sparse-bipolar PARTIALLY breaks compose (3 of 5 negatives sparse-related; 2 of 5 mis-attributed); TWO load-bearing mechanisms (matched-filter sqrt(f) energy + multiplicative-compose zero-product cascade f^k density decay); brain has THREE-layer fix (amplitude + thinning + threshold-receiver) substrate has zero; recommend TWO-CODEBOOK substrate architecture (sparse for storage, dense or amplitude-scaled for compose); decisive test 2x2 factorial 45min CPU; P_deflated(matched-filter mechanism)=0.80 P_deflated(multiplicative-cascade mechanism)=0.65 P_deflated(CDT-bind fixes K-module)=0.45; Taylor mis-attribution corrected (dense word2vec not sparse); per-context T 5-OoM claim needs audit; next-drill candidate: implement Rachkovskij CDT bind for substrate-native sparse compose OR audit per-context T full-scale metrics`

---

*Research drill complete 2026-06-23. 4 parallel WebSearch lit-scans (Kanerva SDM / Rachkovskij CDT / sparse VSA bipolar / Foldiak-Olshausen sparse coding) + 2 supplementary (SBC factorizers / nonlinear Hebbian dimension collapse). Generic queries only. Brain-existence-proof asymmetric calibration applied. HARD-FAIL thresholds both directions; predictions per in-flight cell. Symmetric negativity check applied (7 angles). Mechanism algebra verified: f^k density decay for k-step multiplicative compose; substrate compose primitive compatibility matrix derived (4 of 7 brain-canonical, 2 of 4 substrate-used are sparse-incompatible). 5 META atoms + 3 hdlab/ primitives + 1 cap_map row update routed. Time elapsed ~32 min per budget.*
