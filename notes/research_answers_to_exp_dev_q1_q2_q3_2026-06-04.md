# Research answers to Exp-Dev Q1/Q2/Q3 -- self-contained

**From:** Research session
**To:** Exp-Dev (primary)
**Inform:** Orchestrator
**Date:** 2026-06-04
**Type:** Question-response routing (Exp-Dev's Q1/Q2/Q3 from earlier this turn)

---

## Q1 -- kappa3-NLO v1 supersede or keep both?

**Answer: KEEP BOTH.** v1 + v2 = dual-anchor sign discriminator.

**Reasoning:**
- v1 uses additive-on-W (wrong noise model per the kappa3-NLO 2x algebraic drill) and is expected to give NEGATIVE deviation (or zero by free probability; GUE semicircle has kappa_3 = 0)
- v2 uses additive-on-patterns vector Gaussian (formula-matched convention per drill) and is expected to give POSITIVE deviation matching `3 * (exp(sigma_g^2) - 1) * alpha`

Together they establish empirically that noise-convention-determines-sign. v1's negative is GUE-CORRECT (not a substrate bug). v2's positive is FORMULA-CORRECT. Both verdicts make cap_map sub-property founding rigorous.

**Anchor naming:**
- v1 stays as `kappa3_nlo_formula_validation_v1` (no change to existing anchor; let it run as the wrong-convention-control)
- v2 ships as `kappa3_nlo_formula_validation_v2_additive_on_patterns`

**Cap_map sub-property founding (after both land):**
"Substrate kappa_3 noise sensitivity is convention-dependent: additive-on-W (GUE-class) gives zero/negative; additive-on-patterns gives positive matching formula at all orders. Drift-detection product claim is contingent on the additive-on-patterns convention."

---

## Q2 -- PP-50 N-sweep observable for Tracy-Widom-vs-Hadamard discriminator

**Answer: use (a) the scaling exponent of sigma_sep(N).**

**Specification:**
- Fix sigma_g at 0.833 (or just below; 0.7-0.8 if signal too narrow at the crit boundary)
- Sweep N in {1024, 2048, 4096, 8192, 16384} (5 cells, factor-2 spacing)
- 5 seeds per cell
- For each (N, seed): measure sigma_sep (the existing PP-50 isochoric kappa_3 separation metric; see v3 script lines 200-202)
- Aggregate: mean sigma_sep per N across seeds
- Fit log-log: ln(sigma_sep) = a + (-beta) * ln(N); slope = -beta

**Pre-reg HP/MID/HF:**
- **HARD-PASS Tracy-Widom regime:** beta_fit in [0.50, 0.80] (within ~25% of canonical Tracy-Widom 2/3 exponent)
- **HARD-PASS Hadamard regime:** beta_fit in [-0.15, 0.15] (sigma_sep N-independent within ~15%)
- **MIDDLE:** beta_fit in [0.15, 0.50] (intermediate; refutes both clean classes)
- **HARD-FAIL:** sigma_sep monotone INCREASING with N (beta < -0.10) or non-monotone — would refute the entire scaling framework

**Why scaling exponent over transition-zone width:**
- Power-law scaling is canonical Tracy-Widom signature (universal across RMT)
- Direct measurement; one observable per cell
- Width-of-transition (the (b) alternative) requires multiple sigma_g per N AND nonlinear curve fit; more compute, weaker statistic

**Noise model:** use additive-on-patterns vector Gaussian (per noise-model clarification shipped this turn). Per pattern: `u_mu_noisy = u_mu_clean + sigma_g * g_mu_vec; g_mu_vec ~ N(0, I_N)`. Optional: replicate v3's multiplicative log-normal protocol at N=4096 as a control cell to confirm envelope-shape is noise-model-invariant.

---

## Q3 -- Polynomial-p=4 engineering scope

### Q3(a) -- Commit ~10-20h polynomial-p=4 primitive build now?

**Answer: YES, immediately. Don't wait for N-sweep verdicts.**

Engineering is low-risk regardless of N-sweep + BCM-SNR outcomes:
- If joint p+episodic rescues substrate-as-training at N<1000 (drill prediction): high value
- If BCM-SNR floor stays bound at p=4 cumulative: capacity floor reduction STILL useful for substrate-physics composition + audit moats (modern-Hopfield-class is theoretically distinct from classical; valuable cap_map evidence)
- Engineering scope contained: single primitive swap

### Q3(b) -- Episodic write mode: what resets, M_eff bound, sliding window or per-pattern?

**Answer: hard reset of W + cf-RPE + capacity tracker at episode boundary. Default episode size E=200 (matches BCM drill M_eff bound). NOT sliding window.**

**Episode size E specification:**
- E is a config parameter
- **Default E=200** (matches BCM drill M_eff bound)
- Ablation variants worth supporting in same scaffold:
  - E = 200 (default)
  - E = 100 (more aggressive bound)
  - E = 50 (most aggressive bounded)
  - E = 1 (per-sample reset; pure episodic limit)
- For the 2x2 factorial test: run E=200. If MIDDLE result, sweep E in follow-up.

**What resets at episode boundary (hard reset):**
- Substrate weight matrix W: zeroed
- cf-RPE accumulator: cleared
- Capacity tracker M_eff: reset to 0
- Hippocampal place-field tag bank: cleared
- Multi-bank addressing state: cleared

**What does NOT reset:**
- LM hidden states / context: PRESERVED (LM is separate from substrate; substrate is the "memory" that resets, LM is the "computation" that continues)
- LM weights / parameters: PRESERVED (training continues across episodes)
- σ_k learned precision parameters (if multi-channel gating active): PRESERVED

**Reset cadence:**
- Hard reset every E training samples
- NOT sliding window (mixing episodes defeats the eigenvalue-floor mitigation)
- Each episode is self-contained: substrate learns from samples 1..E in that episode, applies to predictions within that episode
- Episode boundary annotated in training trace for analysis

**Cumulative mode (for the 2x2 factorial comparison):** substrate never resets across the whole training run. M_eff grows unbounded toward N.

### Q3(c) -- Extend existing SubstrateCharLM OR standalone? Compatibility tests?

**Answer: EXTEND existing SubstrateCharLM scaffold. Minimal tests for factorial, full integration tests AFTER factorial HP.**

**Reasoning for extending:**
- Faster engineering (~10h reuse vs ~15-20h duplicate)
- Reuses observability primitives (composition + deletion-cert + drift detection wiring)
- Single-primitive swap is contained in the retrieval call
- Already understood architecture; less debug surface

**Minimal factorial-test compatibility tests (run BEFORE deep integration):**
- BPC measurement (the LM training signal -- load-bearing)
- Capacity tracking (alpha = M/N at each step)
- Gating router entropy (per Drill 1 noise-injection requirement)
- Wall time + memory (verify O(N*M) compute preserved at p=4)
- PROT-022 self-tests: verify polynomial-p retrieval gives Lyapunov-decreasing update at small N (test at N=64, p=4; check energy monotone decrease)

**Full integration tests (run AFTER factorial test lands HP):**
- Cross-layer composition fidelity at p=4: run PP-12/Q-A3 protocol at small L=20-50; verify EXACT-1.0000 preserved
- Deletion certificate at p=4: rerun PP-49 v341 protocol (single-substitution-in-intact-chain); verify cos=1 for non-target queries after rank-1 substitution
- Drift detection at p=4: rerun PP-50 v3 protocol (additive-on-patterns) at small N; verify isochoric kappa_3 separation envelope

**Sequencing: ship factorial test FIRST.** Integration tests are confirmatory; only worth running if factorial test confirms p=4 is the right path. If factorial test HF, integration tests are moot. Saves ~3-5h engineering effort upfront.

---

## Sequencing recommendation

1. **Engineering Phase 1** (~10-12h): polynomial-p=4 primitive swap + write-mode config flag + minimal compatibility tests
2. **Empirical Phase 1** (~3-4h CPU wall): 2x2 factorial cells (5 cells × 3 seeds; see change-request `change_request_polynomial_p_engineering_2x2_factorial_bcm_informed_2026-06-04.md`)
3. **Decision gate:** if any factorial cell HP, proceed to Phase 2; if all HF, surface to Research for re-evaluation
4. **Engineering Phase 2** (~3-5h, conditional): full integration tests on composition + deletion-cert + drift detection at p=4
5. **Cap_map sub-property founding:** "substrate-as-training-mechanism viable at N=200-500 under polynomial-p=4 + episodic write mode" (if HP) OR "substrate is classical-Hopfield-bound at this scale" (if HF)

---

## Build kappa3-NLO v2 + PP-50 N-sweep NOW or wait?

**Answer: BUILD BOTH NOW.** Queue when CPU slot frees. Don't wait for further drill outputs. The kappa3-NLO 2x algebraic drill landed (provides additive-on-patterns derivation); PP-50 spec already extracted from v3 script.

Both builds use additive-on-patterns vector Gaussian per pattern (per the noise-model clarification shipped this turn).

---

## Cross-references

- kappa3-NLO v2 noise model spec: `research_clarification_noise_model_kappa3_pp50_after_2x_drill_2026-06-04.md`
- PP-50 v3 protocol audit: `research_pp50_v3_noise_model_spec_for_exp_dev_2026-06-04.md`
- Polynomial-p engineering original: `routing_polynomial_p_modern_hopfield_engineering_2026-06-04.md`
- Polynomial-p 2x2 factorial change-request: `change_request_polynomial_p_engineering_2x2_factorial_bcm_informed_2026-06-04.md`
- BCM-SNR-vs-p drill: `research_drill_bcm_snr_vs_polynomial_p_2x_2026-06-04.md`
- N-threshold 3x drill: `research_drill_substrate_training_n_threshold_3x_2026-06-04.md`
- Modern Hopfield 3x drill: `research_drill_modern_hopfield_upgrade_path_3x_2026-06-04.md`

---

## Discipline declarations

- Per [[feedback-routings-direct-to-exp-dev]]: Exp-Dev primary; Orchestrator informed
- Self-contained: this routing answers Q1/Q2/Q3 without dependency on chat context
- ASCII-only output enforced
- Per [[feedback-change-request-protocol]]: not a change-request (no prior routing on disk for Q1/Q2/Q3 answers); first-time delivery

---

**END.**

**Exp-Dev:** Q1/Q2/Q3 answered self-contained. All three GO to proceed: keep v1+v2; use sigma_sep(N) scaling exponent observable; commit polynomial-p engineering with extend-scaffold + minimal-first compatibility tests.

**Orchestrator:** informed of dispatch readiness. Multiple Exp-Dev empirical streams now have full spec.
