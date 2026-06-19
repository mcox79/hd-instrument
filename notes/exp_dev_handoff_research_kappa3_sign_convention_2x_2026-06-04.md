# exp_dev hand-off -- research: kappa3 NLO sign convention (2x depth)

**Filed-by:** research sub-agent (2026-06-04)
**Trigger:** notes/research_drill_kappa3_nlo_noise_convention_2x_2026-06-04.md --
algebraic drill identified that the empirical NEGATIVE kappa_3 deviation (exp_dev)
vs POSITIVE formula RHS is explained by noise convention mismatch (Explanation A):
exp_dev added noise to W (additive-on-W), while the formula derives under
additive-on-patterns (or log-normal multiplicative per-pattern) noise.

**Per [[feedback-no-experiment-design-in-prompts]]**: exp_dev chooses anchor names,
sweep grids, threshold formulas, and queue routing. This handoff provides
TASK + WHY + CONTRACT + AUTONOMY only.

---

## Pause state block

Check data/orchestrator_paused.flag before dispatching. If paused, hold this
handoff -- do not queue.

---

## Anchor candidates (rank-ordered)

**Anchor 1 -- noise convention sign distinguisher (CRITICAL; cheap)**
Anchor pointer: run kappa_3 measurement under two noise conventions back-to-back
at the same sigma_g, alpha to confirm sign direction.
Substrate-product reading: confirms which noise convention matches the formula and
explains the sign mismatch. Directly determines the correct experiment spec for all
future kappa_3 noise-robustness anchors (I-19 series and sigma_g_crit validation).
Tier hint: smoke / fast run; N=2048-4096, M=alpha*N, sigma_g in {0.05, 0.10, 0.20}.
Two conditions: (A) additive-on-W: W_noisy = W_clean + sigma_g * G/sqrt(N) where
G is i.i.d. Gaussian; (B) additive-on-patterns: u_mu_noisy = u_mu_clean + sigma_g * g_mu_vec
where g_mu_vec ~ N(0,I_N). Measure SIGNED delta_kappa3 = kappa3(W_noisy) - kappa3(W_clean)
under both conditions. Prediction: condition A gives small negative delta_kappa3;
condition B gives positive delta_kappa3 matching 3*sigma_g^2*alpha to within 30%.
Why now: every kappa_3 noise anchor in flight may have the wrong convention. Cheapest
possible fix; blocks all downstream I-19 sigma_g_crit validation if not confirmed.

**Anchor 2 -- log-normal per-pattern noise sweep (SECONDARY)**
Anchor pointer: test whether log-normal per-pattern noise (scalar multiplier
exp(sigma_g*g_mu - sigma_g^2/2) per pattern) recovers the FULL exponential form
exp(sigma_g^2) - 1 rather than just the leading-order sigma_g^2 term.
Substrate-product reading: if full exponential form is recovered, the formula
`kappa_3/alpha - 1 = 3*(exp(sigma_g^2)-1)*alpha` is established as a NLO
lognormal-noise identity; this sharpens the sigma_g_crit product spec.
Tier hint: FULL run, sigma_g in {0.10, 0.30, 0.50, 0.70}; N=4096.
Why now: secondary after Anchor 1 confirms sign direction. If Anchor 1 confirms
additive-on-patterns (positive sign), this anchor refines whether the exponent
form or the leading-order sigma_g^2 approximation is adequate.

**Anchor 3 -- anti-Hebbian repulsion kappa_3 calibration (EXPLORATORY)**
Anchor pointer: if substrate uses active anti-Hebbian repulsion term
W_eff = W_write - gamma * W_repulse, measure kappa_3(W_eff) vs kappa_3(W_write)
to calibrate gamma.
Substrate-product reading: the ratio kappa_3(W_eff)/kappa_3(W_write) = 1 - gamma^3 *
(alpha_repulse/alpha_write) directly calibrates repulsion strength. If the empirical
negative kappa_3 deviation was from repulsion (not from additive-on-W noise), this
anchor would show the negative shift at gamma=0 noise added (pure W_write).
Tier hint: only dispatch if Anchor 1 shows a LARGER negative deviation than
free-probability theory predicts for additive-on-W. That would trigger Explanation C.
Why now: secondary diagnostic; only relevant if Anchor 1 fails HP1.

---

## Context pointers

- Research note (this drill): d:/AI/hd-instrument/notes/research_drill_kappa3_nlo_noise_convention_2x_2026-06-04.md
- Prior NLO note: d:/AI/hd-instrument/notes/research_drill_kappa3_noise_robustness_nlo_correction_deep_dive_2026-06-03.md
- Prior handoff (sigma_g_crit): d:/AI/hd-instrument/notes/exp_dev_handoff_research_kappa3_noise_robustness_nlo_2026-06-03.md
- Wave-2 source: d:/AI/hd-instrument/notes/research_drill_free_probability_rram_noise_2026-06-02.md
- Existing empirical data: d:/AI/hd-instrument/data/ (search for kappa3_noise_robustness_sigma_g_sweep_v1_n4096)

---

## Contract section

The research note establishes:
1. Additive-on-W noise (GUE): kappa_3 deviation is ZERO at leading order (free
   probability: GUE has kappa_k=0 for k>=3); finite-N correction is NEGATIVE.
2. Additive-on-patterns: kappa_3 deviation is POSITIVE, matching 3*sigma_g^2*alpha
   at leading order; full exponential form via resummation.
3. Non-reciprocal Hopfield: kappa_3 NOT modified by non-reciprocity for bipolar
   patterns (SCS g=0 regime; E[v_i u_i]=0).
4. Log-normal per-pattern: POSITIVE deviation, form exp(2*sigma_g^2)-1 or
   exp(4*sigma_g^2)-1 depending on parameterization.

Exp_dev should verify these predictions empirically (SIGNED measurement) and
confirm which convention matches the formula before continuing I-19 series.

---

## Autonomy declaration

Exp_dev has full autonomy over:
- Exact anchor names (PROT-018 suffix rules apply)
- Sweep grid for sigma_g and alpha
- Queue choice (local GPU or CPU; N=2048-4096 is CPU-feasible)
- Pre-registration of HP/MID/HF bands per envelope-expansion protocol
- Whether to run Anchor 2 and 3 given Anchor 1 outcome

Do NOT pre-commit cap_map changes -- wait for Anchor 1 result.
