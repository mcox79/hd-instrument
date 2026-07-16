# Pre-reg: lexicon_grounding_realvec_encoding_fix_v1

Date: 2026-07-16. Author: exp_dev (hdi_exp_dev). Local/CPU, no push/atoms.

## Provenance / what this repairs

`exp_lexicon_grounding_loop_realvec_v1` (MIDDLE) localized the ONLY real grounding
degradation to the raw->phasor ENCODING: the raw CoDEx TransE embedding X (k=24) is
BENIGN (d_eff/D = 0.761), but the FHRR/FPE phasor lift at the median-coherence-selected
bandwidth CONCENTRATES it (effrank_ratio 0.032, coherence_excess 0.889), degrading the
grounding loop's negatives-gate (RANDOM negrej 1.0 -> REAL_FPE 0.72, AUC 1.0 -> 0.90).
Neither the prior cell's sparse-expansion nor whitening (post-hoc codebook fixes)
recovered. The prior cell also flagged that its FPE selector TARGETED median coherence
0.146 but the reported coherence_mu was 0.91 -- a 7x apparent miss.

This cell DIAGNOSES the concentration mechanism and searches the glass-box encoding
menu for a lift that preserves the raw embedding's benign rank AND recovers the gate.

## Diagnosis (pre-computed on the cached fit; locked here before the full run)

- The apparent "7x target miss" is a STATISTIC MISMATCH plus a real effect: the selector
  targeted MEDIAN off-diagonal coherence (achieved ~0.14), but the reported coherence_mu
  is the MAX (0.91). The load-bearing quantity is neither -- it is the MEAN off-diagonal
  coherence.
- FPE of real vectors gives an ALL-POSITIVE RBF-kernel Gram (coherence_ab ~
  exp(-0.5 sigma^2 ||Xn_a - Xn_b||^2) > 0 for all pairs). An all-positive kernel has a
  large positive MEAN -> a rank-1 common-mode (DC) component. Measured: mean_off_coherence
  0.16 == DC_energy_fraction 0.16 (||mean phasor||^2 / N). Random phasors cancel to
  mean_coh ~0.028, DC_frac ~0.0007.
- The DC caps effective rank: PR <= (trace/lambda_DC)^2 ~ 1/DC_frac^2 ~ 39; measured
  PR 30-33 (effrank_ratio 0.03). This is the entire concentration -- it is the positive
  DC of the RBF lift, NOT a collapse of the raw manifold (raw d_eff/D 0.76 is intact).
- The negatives-gate breaks because the DC gives every negative object a positive
  baseline resonance with every bundle (~ #matching-role-terms x mean_coh).

## Metrics

- negrej = neg_reject_at_90recall; auc = auc_pos_vs_neg (gate quality; higher better).
- geomPres = Spearman( lifted pairwise coherence |<v_a,v_b>|/N , raw-cosine(Xn_a,Xn_b) )
  over a fixed 6000-pair sample (bandwidth-INDEPENDENT reference). RANDOM ~ 0 (no real
  geometry); full-fidelity FPE ~ 0.94 (lift tracks raw geometry). This is the honesty
  gate that distinguishes "gate recovered by grounding" from "gate recovered by
  orthogonalizing away the geometry (codebook became statistically random)."
- effrank_ratio, coherence_excess, DC_energy_fraction, mean_off_coherence (codebook).

## Encodings tested (glass-box menu)

- RANDOM: i.i.d. phasors (ideal ceiling; geomPres ~0, gate ~1.0).
- FPE_BROKEN: FPE at the prior cell's median-coherence-selected bandwidth (the failure).
- DC_DEFLATE: FPE(median-heuristic bw) + remove the leading common-mode (subtract codebook
  mean direction, re-unitize by phase) -- glass-box kernel-centering; targets the DC
  artifact directly while retaining geometry. HEADLINE geometry-preserving fix.
- FPE_MODERATE: FPE at ~3x median-heuristic bw (sharper kernel; partial geometry).
- FPE_WIDE: FPE at ~4.5x median-heuristic bw (kernel ~ identity; codebook ~ random) --
  the geometry-DISCARDING full-recovery reference.
- Dense bandwidth sweep + a raw-per-dim-standardized-FPE landmark (raw-space whitening
  BEFORE the lift, distinct from the post-hoc codebook whiten that HARD_FAILED) to test
  whether ANY glass-box lift breaks the frontier.

## Pre-registered bands (envelope-fail)

HARD-PASS: SOME glass-box encoding achieves negrej >= 0.90 AND auc >= 0.90 AND
  geomPres >= 0.20. The concentration is a fixable lift artifact AND a working gate
  coexists with genuine grounding.

HARD-FAIL: NO encoding -- INCLUDING the geometry-discarding wide-bandwidth limit --
  reaches negrej >= 0.90. The gate cannot be recovered by any glass-box lift of this
  embedding -> intrinsic representational wall -> escalate.

MIDDLE: the gate recovers ONLY in the geometry-discarding limit -- the best
  geometry-preserving encoding (geomPres >= 0.20) has negrej < 0.90, while a
  geomPres < 0.10 encoding reaches negrej >= 0.90. Recovery and grounding are in
  tension; report the frontier + the removable-DC decomposition. (This is the
  HYPOTHESIZED outcome from the pre-run diagnosis.)

## Supporting quantitative claims (reported, honesty-locked; not the gate)

- DC removable: DC_DEFLATE raises effrank_ratio >= 2x over FPE_BROKEN AND recovers
  negrej >= 0.04 while retaining geomPres >= 0.20 -> the DC/common-mode is a removable
  lift artifact (rules out a pure representational wall / HARD-FAIL).
- Frontier tension: Spearman(geomPres, negrej) across the swept encodings <= -0.5 ->
  geometry preservation and gate recovery are anti-correlated (intrinsic tradeoff of
  lifting THIS embedding).

## Honest-read guardrails (do NOT over-read)

- geomPres ~0 with a recovered gate is NOT grounding -- it is a codebook that has become
  statistically random. Full negrej=1.0 is the RANDOM ceiling precisely because random
  codes have no semantic neighbors; a genuinely grounded codebook is EXPECTED to sit
  below 1.0 because geometrically-near negatives are legitimately harder to reject.
  Report partial recovery numbers honestly; do not frame the random-collapse limit as
  a fix.
- The residual gate gap surviving DC-removal is geometry-structured (residual coherence
  still correlates with raw geometry), but "the residual maps to semantically-harder
  negatives" is INTERPRETATION, flagged as such, not a proven claim.

## Ops

Local numpy + torch-CPU (fit only; cached). Reuses realvec_v1's fitter/loop/diagnostics
by import (no re-derivation). ASCII-only. Deterministic seeds. Atomic metrics
(tmp+os.replace). arms-must-differ hash gate. Hardened self-test (real fitter path,
unit-modulus, DC-deflate raises PR / lowers DC_frac, geomPres discriminates, loop
telemetry-sensitive). Full: N=2048, fit_epochs=200, 5 lift-seeds; wall < ~10 min.
No queue/GPU/atoms/push.
