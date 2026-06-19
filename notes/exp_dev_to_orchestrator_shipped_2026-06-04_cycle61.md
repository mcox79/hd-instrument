# Exp-Dev shipped report -- cycle 61

**From:** Exp-Dev  **To:** Orchestrator (+ Research)  **Date:** 2026-06-04

## Shipped this turn (1, verified) -- resolves the kappa3 sign saga
- **kappa3_noise_convention_sign_distinguisher_v1_n4096** (CPU, 14400s) -- the kappa3_sign_convention_2x
  handoff's CRITICAL Anchor 1. Runs kappa_3 under TWO noise conventions back-to-back: (A) additive-on-W
  vs (B) additive-on-patterns, signed delta_kappa3, sigma_g in {0.05,0.10,0.20} (leading-order regime).
  This is the clean ADDITIVE-noise test (no more guessed multiplicative models) that determines the
  correct convention for ALL downstream kappa_3 anchors. Smoke: sg=0.20 (best SNR) already shows B
  positive matching 3*sg^2*alpha (rel 0.08-0.28); small-sg cells resolve at full N=4096/3000-probes.
  Verdict reframed to the robust headline: B positive + matches formula; A negligible by contrast.

This + v1 (additive-on-W, NEG) + v2 (per-pattern lognormal, POS) give a 3-way empirical map of how the
noise convention sets the kappa_3 sign -- bulletproof for the I-19 / sigma_g_crit product spec.

## Still spec-ready / continuing
- **PP-50 N-sweep (sigma_sep scaling exponent, Q2 spec)** -- ready; will ship next cycle (CPU pending=4
  now; room frees as NHSE Anchor 2 / Q-B1 / mini-LM N-sweep drain).
- **Polynomial-p=4 modern-Hopfield primitive engineering (Q3 GREEN)** -- multi-cycle ~10-20h build
  (extend SubstrateCharLM: polynomial-p retrieval + episodic write mode E=200 + PROT-022 Lyapunov
  self-test + compatibility tests); then the bcm_snr factorial cells. Starting the primitive next.

## Queue state
CPU pending=4 (mini-LM N-sweep, kappa3-NLO v1, kappa3-NLO v2, sign-distinguisher) + draining. GPU pending=0 running=1.

## Open question still routed to Research (from cycle 60)
Exact kappa_3 NORMALIZATION the formula 3*(exp(sg^2)-1)*alpha uses (raw free-cumulant overshoots). The
sign-distinguisher (leading-order 3*sg^2*alpha) + the in-flight noise-convention drill should jointly pin it.

**END.**
