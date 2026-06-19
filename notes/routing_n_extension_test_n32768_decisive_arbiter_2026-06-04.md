# Routing -- N-extension test (N=32768, 20 seeds) decisive spectral-regime arbiter

**From:** Research session
**To:** Exp-Dev (primary)
**Inform:** Orchestrator
**Date:** 2026-06-04
**Type:** Empirical decisive test
**Source:** intermediate-regime 2x drill landed 2026-06-04 (research_drill_substrate_intermediate_regime_scaling_2x)

---

## Capability question

Does substrate's spectral edge fluctuation scaling exponent beta_local converge to 1/3 (BBP-critical class), 1/2 (Gaussian / non-Hermitian), or 2/3 (Tracy-Widom restored) at extended N=32768 with high-seed statistics (20+ seeds)? Resolves whether substrate is in BBP-critical / NESS-critical regime + empirically calibrates the deletion-certificate sigma threshold.

## Pre-reg HP/MID/HF bands

**HARD-PASS (BBP-critical confirmed):** beta_local in [0.28, 0.40] at N=32768 with 20+ seeds. Substrate identified as BBP-critical Wishart + non-Hermitian deformation class per Baik-Ben Arous-Peche 2005 + Bertini 2015 active-driven NESS framework. Deletion-cert sigma threshold formula gets empirical 5x recalibration constant.

**MIDDLE-BAND:** beta_local in [0.40, 0.55] -- mixed regime of empirical noise + structural; not a clean class.

**HARD-FAIL (BBP framework refuted):**
- beta_local > 0.55 → Tracy-Widom restored at higher N → substrate is finite-N-corrected pure-Wishart class (not BBP-critical)
- beta_local < 0.20 → noise floor dominates → not enough seeds or measurement instability

## Resource

Remote GPU 4060 Ti 8GB (per `feedback_cloud_only_when_absolutely_necessary`; no cloud).

## Cost ceiling

$0. Wall ~5-10 min GPU (single matrix-free Hutchinson + power iteration at N=32768; cheap).

## P_deflated

- BBP-critical confirmed (beta_local in [0.28, 0.40]): **0.45**
- TW restored (beta_local > 0.55): 0.15 (would refute drill's BBP-critical hypothesis)
- MIDDLE: 0.30
- Noise floor: 0.10

## What this is (plain language)

Today's PP-50 v4 lambda_1 N-sweep gave beta_std=0.355 with 5 seeds across N={1024..16384}. The intermediate-regime drill identified this as near-BBP-critical (beta=1/3 in clean limit) + non-Hermitian deformation. But 5 seeds + 5 N values gives slope CI of +/-0.10 to +/-0.15 -- statistically consistent with 1/3, 0.355, OR 1/2. Need higher seed count + extended N to resolve.

This is the cheapest decisive arbiter for substrate's spectral regime classification AND empirically calibrates the deletion-certificate confidence threshold.

## Experiment design

**Anchor:** `substrate_spectral_edge_n_extension_decisive_v1_n32768_20seeds`

**Cells:**
- N values: 8192, 16384, 32768 (3 points; finer resolution at high N + ensures finite-N effects visible)
- Seeds: 20 per N (vs current 5; reduces slope CI by ~2x)
- Sigma_g fixed at 0.7-0.8 (just below sigma_g_crit; ensures signal)
- Noise model: additive-on-patterns vector Gaussian (per kappa3-NLO 2x drill spec)

**Per-cell:**
- Compute W_noisy = Xi_noisy^T Xi_noisy / N at each (N, seed)
- Power iteration: lambda_1 via 20 power iterations
- Aggregate: std(lambda_1) across 20 seeds at each N
- Fit log-log: ln(std(lambda_1)) vs ln(N); slope = -beta_local

**Total compute:**
- N=8192: ~10s per cell × 20 seeds = ~3-4 min
- N=16384: ~30s per cell × 20 seeds = ~10 min
- N=32768: ~60s per cell × 20 seeds = ~20 min
- Total ~30-40 min GPU; conservative estimate

**Actually -- much less. Power iteration at M=alpha*N is cheap:**
- M = 0.05*32768 = 1638 patterns
- Per power iteration: O(M*N) = ~5e7 ops; 20 iters = ~10e8 ops per lambda_1
- 20 seeds × 3 N values = 60 lambda_1 measurements
- Total: ~10s-1 min GPU. **Genuinely cheap.**

## Why N=32768 specifically

- Doubles from current N=16384 max
- Reduces finite-N corrections by ~25% (Bourgade 2022 O(N^{-1/3}) convergence)
- 20 seeds reduces slope CI from +/-0.10-0.15 to +/-0.05-0.07
- Combined: discriminates beta=1/3 from beta=1/2 with statistical confidence

## Product-critical implication

Per drill: TW-assumption deletion-certificate threshold formula OVERSTATES CONFIDENCE BY 5X. The empirical std(lambda_1) is 5x larger than pure TW predicts → "high-confidence deletion" sigma threshold is 5x off.

**This N-extension test produces the empirical recalibration constant.** Once we know the actual beta_local at extended N, the deletion-cert sigma threshold can be empirically calibrated. Until then, do NOT ship deletion-cert product framing at the TW-derived threshold (would overstate confidence by 5x).

## Strategic outcomes

**If HP (BBP-critical confirmed at beta in [0.28, 0.40]):**
- Substrate algebraic class identified: BBP-critical Wishart + non-Hermitian + active-driven NESS
- Bertini 2015 macroscopic fluctuation theory becomes substrate's spectral lit anchor
- Deletion-cert sigma threshold gets empirical recalibration (5x adjustment)
- Cap_map: NEW sub-property founding under "substrate spectral regime classification"

**If MIDDLE:** still informative; tighter slope CI than current measurement. Possibly substrate operates in mixed regime; need framework that includes mixing.

**If HARD-FAIL beta > 0.55 (TW restored):** rebuild the spectral framework picture; intermediate-regime drill's BBP-critical hypothesis refuted. Substrate may be in finite-N-corrected pure-Wishart at smaller N + asymptotic TW at large N.

## Sequencing

**HIGH PRIORITY immediate dispatch.** Single cheap test with major product implication. Should be Bundle E if Exp-Dev is bundling. Otherwise standalone.

Can run alongside Bundle A (architectural ablation matrix; CPU) on different runner slots.

## Discipline declarations

- Per [[feedback-routings-direct-to-exp-dev]]: Exp-Dev primary; Orchestrator informed
- Per [[feedback-cloud-only-when-absolutely-necessary]]: remote GPU only; $0
- Per [[feedback-no-padding-experiments]]: single decisive test; product-critical recalibration
- Per [[feedback-no-smoke-preframing-in-task-prompts]]: HP/MID/HF bands explicit; tied to drill predictions
- ASCII-only

PROT-018: anchor uses `_n32768_20seeds` suffix
PROT-021: source=remote GPU, run_mode=full, n_seeds=20

---

**END.**

**Exp-Dev:** dispatch when GPU slot frees. ~5-30 min wall; $0; standalone or as Bundle E. Surface beta_local + 95% CI in verdict. Verdict drives substrate spectral regime classification + deletion-cert sigma recalibration.

**Orchestrator:** informed. Cap_map sub-property founding pending verdict.

**Research session:** holds for verdict; ships consolidated cap_map update + capability-implication note per outcome.
