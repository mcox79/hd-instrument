# Prereg — wave14_cap8_vamp_ensemble_variance_overlay_v1

**Date**: 2026-05-24
**Anchor**: Bet Z.5 S2 closure anchor; Research drill `notes/research_audit_followup_drills_2026-05-24.md` Section 1.5
**Queue**: remote_cpu_queue
**ETA**: 30-45 min CPU
**Script**: experiments/exp_wave14_cap8_vamp_ensemble_variance_overlay_v1.py

## Hypothesis under test

Bet Z.5 (absorbing-discrete-diffusion smoother per Diao 2025, arXiv:2507.07586) claimed that per-coordinate empirical variance across K independent denoising trajectories Spearman-correlates with per-coordinate reconstruction error (paper reports rho=0.996 on WikiText-2). The S1 structural-equivalence drill (notes/research_audit_followup_drills_2026-05-24.md Section 1.5) found Bet Z.5 NOT structurally equivalent to and NOT contained in Cap 8 (VAMP-on-chain), on the per-coordinate-variance axis.

**This S2 anchor tests whether the per-coordinate-variance axis is recoverable from Cap 8 + a cheap K-trace ensemble overlay**, without committing to a fresh absorbing-diffusion impl (S3).

Operationally: K=64 seed-perturbed VAMP-on-chain traces on Kerdock substrate at N=4096, alpha=0.5. For each of 5 test codewords, compute per-coordinate empirical sample variance across the K traces and per-coordinate reconstruction error (squared deviation of the per-coord mean from x_true), then Spearman ρ across N=4096 coords.

## Protocol

- **Substrate**: Kerdock 4-coset codebook (substrate's primary structured family).
- **Shape**: N=4096, M=2048 (alpha = M/N = 0.5, in-capacity regime).
- **Codewords**: n_codewords=5 (per S2 anchor proposal in Research note Section 1.5.5). Each codeword x_true sampled from Gaussian prior with signal_var=1.0.
- **Perturbation axis**: noise seed (channel matrix W and x_true held fixed within a codeword; noise z ~ N(0, sigma_sq*I) varies across K traces). sigma_noise=0.1.
- **K**: 64 traces per codeword (per Section 1.5.5 anchor proposal).
- **VAMP**: canonical Rangan-Schniter-Fletcher 2017 Algorithm 1 with cached SVD, Gaussian prior denoiser, 1e-10 MSE-band early-stop. n_iter cap = 200.

## Hard-pass / hard-fail / middle-band (verbatim from Research drill)

- **HARD PASS** (Bet Z.5 closes-by-absorption into Cap 8 envelope annotation):
  - Spearman rho >= 0.50 in >= 3/5 codewords.
  - Interpretation: VAMP-ensemble variance is informative about reconstruction error; Cap 8 + K-trace overlay subsumes Bet Z.5's distinguishing axis. Annotation text: "Cap 8 VAMP-on-chain envelope extends to per-coordinate posterior-variance estimation via K-trace ensemble overlay (Spearman rho >= 0.50 vs reconstruction error); equivalent to absorbing-discrete-diffusion ensemble certificate (Diao 2025) without fresh impl."
- **HARD FAIL** (Bet Z.5 has genuine novelty NOT in Cap 8):
  - Spearman rho < 0.30 in >= 3/5 codewords.
  - Interpretation: VAMP-ensemble variance is not informative; Bet Z.5's per-coordinate-variance certificate is genuinely additional capability. File S3 toy-scale fresh impl (N=512) as a NEW 🔬 row P=0.40 with the per-coord-variance certificate as the distinguishing capability.
- **MIDDLE BAND**:
  - Anything else (1-2 codewords pass, others don't, or some inconclusive).
  - Interpretation: per-codeword variability rather than universal pattern. Annotate Cap 8 with "ensemble-variance overlay is partially informative"; Bet Z.5 stays 🔬 but with reduced priority.

## Pre-registered calibration

- P(HARD PASS): ~0.55 (per [[feedback-lit-scan-calibration-penalty]] deflated -0.15 because cross-noise-seed ensemble variance is conceptually distinct from cross-mask ensemble variance and the universality is not proved).
- P(HARD FAIL): ~0.25.
- P(MIDDLE): ~0.20.

Portfolio impact: portfolio does NOT grow regardless of outcome -- this is a stale-row closure attempt. Importance MEDIUM.

## Self-tests (in script)

1. **VAMP IID Gaussian sanity** -- on N=128 iid-Gaussian channel, final MSE matches AMP-SE closed form within 20% relative error.
2. **Ensemble variance analytical** -- K=200 unit-Gaussian samples yield sample variance approx 1.0 (|mean_var - 1.0| < 0.05) per coord.
3. **Spearman rho monotonicity** -- var = err + tiny noise yields rho > 0.99.
4. **Spearman rho null** -- var independent of err yields |rho| < 0.20 (5-sigma bound at N=1000).
5. **Verdict-branch test** -- synthetic per-codeword rho arrays produce expected verdict for PASS / FAIL / MIDDLE / INCONCLUSIVE.

## Smoke (local pre-ship gate)

N=64, K=4, n_codewords=1, Kerdock builder; verify end-to-end ensemble-variance computation is finite and matches the analytical test. Self-tests run as part of smoke.

## Sources

- Diao et al., "Your Absorbing Discrete Diffusion Secretly Models the Bayesian Posterior", arXiv:2507.07586 (2025)
- Rangan-Schniter-Fletcher 2017, "Vector Approximate Message Passing"
- Berthier-Montanari-Nguyen 2020, VAMP state-evolution
- Research drill: notes/research_audit_followup_drills_2026-05-24.md Section 1.5
