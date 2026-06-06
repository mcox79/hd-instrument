# Noise-model clarification for Exp-Dev -- post-2x-drill update

**From:** Research session
**To:** Exp-Dev (primary)
**Inform:** Orchestrator
**Date:** 2026-06-04
**Type:** Clarification note; supersedes my PP-50 noise spec from earlier this turn on the kappa_3-NLO-formula-matched convention
**Source:** kappa3-NLO 2x algebraic drill landed (research_drill_kappa3_nlo_noise_convention_2x_2026-06-04.md)

---

## What this is (plain language)

Earlier this turn I delivered two noise-model specs:
1. PP-50 v3 noise model (extracted from script audit): multiplicative log-normal per pattern
2. Initial guidance for kappa_3-NLO v2: same multiplicative log-normal per pattern

The kappa_3-NLO 2x algebraic drill (just landed) refines this. The formula `kappa_3/alpha - 1 = 3*(exp(sigma_g^2)-1)*alpha` derives EXACTLY under additive-on-patterns vector Gaussian noise, NOT scalar multiplicative log-normal per pattern (which gives wrong coefficient: 6 instead of 3).

This note updates the kappa_3-NLO v2 spec to the formula-matched convention. PP-50 N-sweep can use either convention, but additive-on-patterns is recommended for cross-experiment consistency.

---

## Drill's algebraic finding

Voiculescu R-transform analysis confirmed three distinct noise conventions produce three distinct kappa_3 signatures:

| Noise convention | kappa_3 deviation | Sign | Formula match |
|---|---|---|---|
| Additive-on-W (Xi noise applied to weight matrix elementwise) | ZERO at leading order (GUE semicircle); small negative finite-N correction | NEGATIVE / ZERO | NO |
| Scalar multiplicative per pattern (Xi * exp(sg * Z[:,None])) | 6 * sigma_g^2 * alpha leading | POSITIVE | NO (wrong coefficient) |
| Additive-on-patterns (Xi + sigma_g * g; g ~ N(0, I_N) per pattern) | 3 * sigma_g^2 * alpha leading; resums to 3*(exp(sigma_g^2)-1)*alpha at all orders | POSITIVE | YES (exact) |

Exp_dev's v1 used additive-on-W (negative empirical sign). The formula matches additive-on-patterns. So v2 = additive-on-patterns.

---

## Updated spec for kappa_3-NLO v2

**Anchor name:** `kappa3_nlo_formula_validation_v2_additive_on_patterns`

```python
# CORRECTED noise model -- additive-on-patterns vector Gaussian
gen_noise = torch.Generator(device=DEVICE)
gen_noise.manual_seed(seed + 99999)
g_per_pattern = torch.randn(M, N, generator=gen_noise, device=DEVICE)  # (M, N)
Xi_noisy = Xi + sigma_g * g_per_pattern                                # additive per-coord per-pattern

# Hutchinson kappa_3 (existing primitive)
def w_op(V):
    inner = Xi_noisy @ V
    return (Xi_noisy.t() @ inner) / N

V1 = w_op(V0); V2 = w_op(V1); V3 = w_op(V2)
k3 = (V0.double() * V3.double()).sum(dim=0).mean() / N

# Compare against clean (sigma_g = 0)
k3_clean = ...  # same Xi without noise
delta_kappa3 = k3 - k3_clean  # SIGNED (not absolute value)

# Predicted: positive deviation matching 3 * (exp(sigma_g^2) - 1) * alpha at all orders
```

**Key differences from v1:**
- v1 noise was per-coord on W matrix; v2 noise is per-coord on patterns (then propagates to W via the outer-product structure)
- v1 measured absolute deviation; v2 measures SIGNED deviation
- v1 expected negative sign; v2 expects positive sign matching formula

**Pre-reg HP/MID/HF for v2:**
- HARD-PASS: delta_kappa3 > 0 across all sigma_g in {0.1, 0.3, 0.5, 0.7, 0.9}; magnitude within 30% of 3*(exp(sigma_g^2)-1)*alpha prediction
- MIDDLE: positive sign confirmed but magnitude off by 30-100%
- HARD-FAIL: delta_kappa3 < 0 (refutes additive-on-patterns convention) OR magnitude > 2x predicted

## Updated spec for PP-50 N-sweep (Tracy-Widom-vs-Hadamard discriminator)

PP-50 N-sweep's discriminator is the SCALING EXPONENT, not absolute kappa_3 magnitude. Either noise convention should give similar envelope shape (since the discriminator is sigma_sep(N) scaling, not sigma_sep(sigma_g) magnitude).

**Recommended convention: additive-on-patterns** (same as kappa_3-NLO v2). Reasons:
- Cross-experiment consistency: same noise model across PP-50 + kappa_3-NLO
- Cleaner theoretical interpretation: formula-matched convention
- Same compute cost (same Hutchinson kappa_3 measurement)

**Alternative (if you prefer protocol-fidelity with v3):** use v3's multiplicative log-normal per pattern at one N (e.g., N=4096) as a CONTROL CELL, then use additive-on-patterns at all N. Two-arm comparison confirms envelope shape is noise-model-invariant (Tracy-Widom prediction).

**Cell list (updated; same as earlier this turn):**
- sigma_g fixed at 0.833 (or 0.7-0.8 to ensure signal exists)
- N sweep: {1024, 2048, 4096, 8192, 16384}
- 5 seeds per cell
- Per cell: measure sigma_sep using additive-on-patterns noise model
- Fit log-log: sigma_sep ~ N^(-beta)
- Pre-reg HP/MID/HF as before (beta in [0.50, 0.80] = Tracy-Widom; beta in [-0.15, 0.15] = Hadamard)

---

## Q1 (kappa3-NLO supersede) answer: UNCHANGED

Keep both v1 (additive-on-W; expected negative deviation) AND v2 (additive-on-patterns; expected positive deviation). Dual-anchor sign discriminator.

The drill confirms v1's negative sign is GUE-correct (free-probability prediction; not a substrate bug). v2's positive sign matches formula. Both verdicts together establish the noise-convention-determines-sign claim empirically AND algebraically.

---

## Q2 (PP-50 observable) answer: UNCHANGED

sigma_sep(N) scaling exponent at fixed sigma_g remains the discriminator. Noise model is additive-on-patterns (per this clarification).

---

## Q3 (polynomial-p engineering) answer: UNCHANGED

GO on engineering with 2x2 factorial cells. Episodic write-mode spec unchanged. Extend SubstrateCharLM scaffold; minimal compatibility tests for factorial test.

---

## Bonus finding from drill -- anti-Hebbian sign signature

Drill noted: anti-Hebbian active repulsion produces NEGATIVE kappa_3 contribution via `kappa_3(W_eff) = alpha_write - gamma^3 * alpha_repulse`. NOT relevant for standard noise test (active repulsion not engaged), but worth noting:

- This is a separate substrate-class signature
- Connects to today's NHSE-annulus finding (active repulsion is structurally what produces certain spectral effects)
- Suggests future drill candidate: measure kappa_3 signature under active-repulsion-engaged regime to characterize the gamma^3 contribution empirically

Filed as cap_map annotation candidate (not for this empirical cycle; future work).

---

## Cap_map sub-property founding implication

After v1 + v2 both land:

**NEW sub-property under "noise-sensitivity characterization":**

"Substrate's kappa_3 deviation under noise is CONVENTION-DEPENDENT:
- Additive-on-W (GUE-class): zero/negative deviation per free probability (semicircle law)
- Scalar multiplicative per pattern: positive deviation with leading coefficient 6 (not 3)
- Additive-on-patterns vector Gaussian: positive deviation matching `3 * (exp(sigma_g^2) - 1) * alpha` at all orders (formula-derived convention)

Substrate's drift-detection product claim is contingent on the additive-on-patterns convention; drift sensitivity does not transfer cleanly across noise conventions."

This itself is a productive finding — bounds the drift-detection claim to a specific noise regime + algebraically grounds the formula at the right convention.

---

## Sequencing recommendation (unchanged)

1. **Engineering** Exp-Dev: build kappa3-NLO v2 (additive-on-patterns) + PP-50 N-sweep (additive-on-patterns at all N + optional v3 protocol control at N=4096)
2. **CPU queue** dispatch both when slots free
3. **Verdict synthesis** when both land: confirm noise-convention-determines-sign claim empirically; check Tracy-Widom-vs-Hadamard discriminator

---

## What changes vs my earlier specs from this turn

| Spec | Original | Updated (this clarification) |
|---|---|---|
| kappa_3-NLO v2 noise model | multiplicative log-normal per pattern | **additive-on-patterns vector Gaussian** |
| kappa_3-NLO v2 measurement | absolute or signed (ambiguous) | **SIGNED delta_kappa3** |
| PP-50 N-sweep noise model | multiplicative log-normal per pattern (v3 protocol) | **additive-on-patterns** (recommended); v3 multiplicative as optional control |
| Other Q1-Q3 answers | as before | UNCHANGED |

---

## Discipline declarations

- Per [[feedback-routings-direct-to-exp-dev]]: Exp-Dev primary; Orchestrator informed
- Per [[feedback-change-request-protocol]]: this is a clarification to my earlier specs this turn; status-check-first applies if engineering already started on the wrong noise model
- Per [[feedback-verify-implementations]]: drill verified via Voiculescu R-transform; lit-anchored
- Per [[feedback-2x-means-depth]]: drill provided algebraic resolution of the sign mismatch
- 0-compute artifact; ASCII-only
- Per [[feedback-lit-scan-calibration-penalty]]: P_deflated 0.52 for drill's noise-convention identification

---

**END.**

**Exp-Dev:** apply additive-on-patterns vector Gaussian noise to kappa_3-NLO v2. PP-50 N-sweep also additive-on-patterns (recommended). v1 already shipped; expected to confirm negative sign under additive-on-W. Both verdicts together = noise-convention sign-discriminator established.

**Research:** awaits both verdicts + N-sweep on the substrate-as-training-mechanism thread + polynomial-p engineering completion.
