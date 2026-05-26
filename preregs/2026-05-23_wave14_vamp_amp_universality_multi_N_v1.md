# Prereg: wave14_vamp_amp_universality_multi_N_v1

**Date**: 2026-05-23 (emergency refill batch #3)
**Queue**: overnight_queue (GPU)
**Hypothesis class**: substrate-product split at scale (VAMP works, AMP fails)

## Scientific claim under test
v164a v2 VAMP_AMP_CONTRAST_PASS at N=4096 promoted the "VAMP-on-Kerdock holds where AMP fails" row to ✅. This experiment scale-stresses that contrast at N in {1024, 4096, 16384}.

## Design
- N in {1024, 4096, 16384} (8192 skipped per Kerdock MM even-log2 constraint)
- alpha in {0.5, 1.0, 2.0, 4.0}, 10 seeds per cell
- Same Gauss-Gauss matched setup as v1 (sigma_noise=0.1, signal_var=1.0)
- VAMP-SE via closed-form posterior MSE over empirical singular spectrum
- Empirical VAMP via Rangan-Schniter-Fletcher 2017 Alg 1 with MMSE Gaussian denoiser
- AMP-SE Bayati-Montanari scalar; empirical AMP via GAMP-style iter

## Hard-fail thresholds
- Self-test 5/5 passes verdict-branch sanity
- N=4096 results must replicate v1 CONTRAST_PASS (regression)
- metrics.json validate + atomic write

## Verdict labels
- VAMP_AMP_CONTRAST_HOLDS_AT_SCALE: contrast PASS in >= 2/3 of N tested
- VAMP_AMP_CONTRAST_BREAKS_AT_SCALE: contrast PASS at small N but not at largest N
- VAMP_AMP_BOTH_MATCH_AT_SCALE: SE recovers asymptotically
- VAMP_AMP_MULTI_N_INCONCLUSIVE

## Expected runtime
SVD at N=16384, M up to 65536 dominates. ~45 min wallclock GPU.

## Implications
- HOLDS_AT_SCALE => substrate-product asymptotic story confirmed
- BREAKS_AT_SCALE => substrate falls outside VAMP universality asymptotically; need OAMP / generalized framework
- BOTH_MATCH_AT_SCALE => challenge to v163 AMP_SE_DIVERGES at finite-N scale
