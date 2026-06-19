# Prereg: wave14_cap12_noise_cleanup_optshrink_v1

Date: 2026-05-24
Queue: remote_cpu_queue
ETA: 45-60 min CPU
Type: NEW-CAPABILITY (Cap 12 noise envelope EXPANSION via upstream codebook denoising)

## Purpose

Close Portfolio Gap 1 (Cap 12 customer-facing noise envelope; v178 narrowed
to eta <= 0.01) by adding a Donoho-Gavish-Nadakuditi optimal SVD-shrinkage
preprocessing step. Anchor pulled from
`notes/research_audit_followup_drills_2026-05-24.md` Section 3.

## Hypothesis

Applying single-pass OptShrink data-driven hard-threshold SVD denoising to an
eta-bit-flip-corrupted codebook W_noisy reconstructs W_cleaned such that:
1. eta_effective <= eta_input / 3 (>=3x effective noise reduction) at
   eta_input in {0.05, 0.10} across >=4/5 codebook families; AND
2. Cap 12 MP-KS routing on W_cleaned >= 4/5 at eta_input <= 0.10.

If both hold, Portfolio Gap 1 closes; Cap 12 customer envelope extends from
eta <= 0.01 to eta_input <= 0.10 with OptShrink preprocessing.

## Math (Donoho-Gavish 2014 + Nadakuditi 2014 OptShrink)

For Y = X + sigma * G (M x N, beta = min(M,N)/max(M,N) in (0, 1]):
  lambda*(beta) = sqrt(2*(beta+1) + 8*beta/((beta+1) + sqrt(beta^2 + 14*beta + 1)))
  threshold     = lambda*(beta) * sigma * sqrt(max(M, N))
At beta=1 (the substrate's canonical regime): lambda*(1) = 4/sqrt(3) ~ 2.309.

For eta-bit-flip noise on bipolar +/-1 entries:
  Z = W * (flip - 1); flip-1 in {-2, 0} with P(-2)=eta.
  Var(Z) = 4*eta*(1-eta) * W^2  =>  sigma_noise_per_entry = 2*sqrt(eta*(1-eta))
                                    (on the unnormalized +/-1 scale)

Algorithm per cell (codebook, eta, seed):
  1. Build clean W (substrate scale 1/sqrt(N)); denormalize to {+/-1}.
  2. Apply per-entry bit-flip with probability eta on the +/-1 matrix.
  3. SVD; hard-threshold singular values at lambda*(beta) * sigma_noise * sqrt(N_larger).
  4. Reconstruct; for bipolar codebooks re-quantize via sign(); for iid_gauss
     keep continuous-valued.
  5. Renormalize to 1/sqrt(N) substrate scale.
  6. Measure eta_effective = fraction of bit-flips remaining after cleaning
     (for bipolar codebooks: sign-flip rate vs W_clean; for iid_gauss:
     Frobenius relative residual amplitude).
  7. Run MP-KS pre-test on both W_noisy and W_cleaned.
  8. Route via route_from_ks(ks_mean, tau=0.20); record correct vs
     expected_clean_route.

## Design

- 5 codebooks: iid_gauss, srht, hadamard, rm_1_m, kerdock
- 5 eta_input values: {0.01, 0.02, 0.05, 0.10, 0.20}
- 5 seeds per cell
- N = 1024, M/N = 1.0, tau_fixed = 0.20
- Total cells = 125

Reuses noise model from `exp_wave14_mp_ks_noise_envelope_sweep_v1.apply_signflip_noise`
and codebook builders + mp_ks_stat from
`exp_wave14_kappa_profile_cross_codebook_v1`. Adds OptShrink denoiser:
`optshrink_denoise(W, sigma_noise)`.

## HARD PASS (Portfolio Gap 1 closes; envelope extends to eta_input <= 0.10)

- eta_effective <= eta_input / 3 (>=3x effective noise reduction) at
  eta_input in {0.05, 0.10} across >=4/5 families
- AND mean routing fidelity on W_cleaned >= 4/5 at every eta_input <= 0.10

Substrate-product claim: "Cap 12 tolerates noise up to eta_input = 10% when
upstream OptShrink preprocessing is applied to the customer codebook before
substrate ingestion."

## HARD FAIL HF1 (OptShrink insufficient; envelope remains substrate-bounded)

- eta_effective > 0.02 at eta_input = 0.05 across >=4/5 families

Substrate-product claim narrows to: "Cap 12 customer envelope remains at
eta <= 0.01; customer must supply pre-cleaned codebooks; OptShrink is not a
viable preprocessing step in this regime."

## HARD FAIL HF2 (rank truncation collapses codebook; switch family)

- OptShrink rank_kept drops to 0 at any eta_input >= 0.05 in any family

Upstream-push to Research: switch to family-2 method (sparse soft-thresholding
in a structured basis — Hadamard / Walsh / RM-projection per Section 2.2 of
the literature drill).

## HARD FAIL HF3 (denoising actively HARMS clean substrate; abandon)

- Mean routing fidelity on W_cleaned at eta_input = 0.01 < 0.50

Substrate-product claim: OptShrink is anti-correlated with substrate
performance; abandon entirely. Customer envelope stays at eta <= 0.01
without any preprocessing.

## MIDDLE BAND

- Some noise reduction observed (eta_effective in (eta_input/3, eta_input/2))
  but routing still degrades, OR HARD PASS holds at eta=0.05 only and fails
  at eta=0.10.

Substrate-product claim: "Cap 12 customer envelope extends to eta_input <=
0.03-0.05 with OptShrink preprocessing." Annotation only; not a full Gap 1
closure.

## Self-tests (executed before main run)

1. `optshrink_lambda_beta(1.0) == 4/sqrt(3)` (Donoho-Gavish closed form).
2. `optshrink_lambda_beta(beta)` non-decreasing on beta in (0, 1].
3. **Critical**: OptShrink on a CLEAN Hadamard at eta=0 -> threshold=0,
   rank_kept=N, singular values preserved to floating-point, Frobenius
   relative reconstruction error < 1e-4. (Per
   [[feedback-strategy-spec-formula-selftests]].)
4. `apply_signflip_noise` at eta=0 is identity.
5. `measure_eta_effective(W, W) == 0`.
6. `bipolar_signnorm` is the inverse of denormalize-by-sqrt(N).
7. `aggregate_per_family_per_eta` groups correctly.
8. Synthetic HARD PASS branch verdict.
9. Synthetic HF1 branch verdict.
10. Synthetic HF2 branch verdict.
11. Synthetic HF3 branch verdict.
12. Synthetic MIDDLE band verdict.
13. Missing-cells -> INCONCLUSIVE.

## Smoke (PASS)

```
N=64, 1 seed, eta in {0.0, 0.05}, codebooks={iid_gauss, hadamard}
Self-tests: 13/13 PASS
eta=0 baseline: ks_noisy == ks_cleaned, eta_eff=0.0, rank_kept=64, routings correct (both)
eta=0.05: smoke at N=64 shows rank truncation to 25-29 (expected at small N where
  OptShrink overfits noise); production N=1024 should retain more structure
VERDICT: CAP12_NOISE_CLEANUP_OPTSHRINK_INCONCLUSIVE (4 < 25 cells; expected)
metrics.json written
```

OptShrink threshold formula sanity (per Research's anchor proposal):
- lambda*(beta=1) computed = 2.30940108..., expected 4/sqrt(3) = 2.30940108...
  (passes to 1e-6).
- At eta=0 (sigma=0), threshold = 0, all singular values retained,
  reconstruction exact (Frobenius rel err < 1e-4).

## Calibration penalty (per [[feedback-lit-scan-calibration-penalty]])

Research filed novel-synthesis P deflated to 0.40. Donoho-Gavish is proved for
Gaussian noise; bit-flip noise has bounded-but-heavier tails per entry
(discrete two-state distribution vs Gaussian) which may shift the effective
threshold slightly. The 0.40 ceiling reflects this unverified regime.

## Risks / open questions

- iid_gauss is NOT bipolar; the sign-quantize-then-renormalize step is
  replaced with identity. eta_effective for iid_gauss is reported as
  Frobenius relative residual amplitude, NOT a sign-flip rate. The HF1 check
  uses the bipolar families primarily; iid_gauss serves as a control.
- At small N (smoke N=64) OptShrink overshoots the threshold and truncates
  aggressively. Production N=1024 has cleaner separation between signal +
  noise singular values; this is the same scaling regime where DG is proved
  asymptotically optimal.
- Bit-flip noise has a small systematic mean bias (E[Z] = -2*eta*W) that
  pulls singular vectors slightly toward -X. DG's optimality is for
  zero-mean noise; the bias may degrade performance at higher eta. If HF1
  triggers, an upstream-push to Research should request a mean-corrected
  variant (subtract E[Z] = -2*eta*W_noisy_avg before SVD).
