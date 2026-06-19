# Upstream Push: ckm_coefficient_derivation_v1 Smoke HARD_FAIL -- Measurement protocol wrong

**Date:** 2026-06-02
**Anchor attempted:** ckm_coefficient_derivation_v1
**Status:** BLOCKED (smoke HARD_FAIL; measurement protocol does not match C(k,m) definition)

## Smoke results

- k=2, m_frac=0.25: C_emp=0.910, C_theory=0.125, rel_err=6.28 (HARD_FAIL)
- k=3, m_frac=0.25: C_emp=0.850, C_theory=0.0104, rel_err=81.8 (HARD_FAIL)

## Root cause

The measurement protocol computes:
  C(k,m)_emp = mean_{mu} [<x^(k) | xi_mu> / N] after k Hopfield steps from xi_mu.

This is the RETRIEVAL FIDELITY (normalized overlap after k steps), which converges to ~1.0
for patterns below capacity -- not the correction coefficient C(k,m).

C(k,m) = alpha^{k-1}/k! is a SIGNAL ATTENUATION FACTOR in the mean-field signal/noise
decomposition:
  signal_k = C(k,m) * N (contribution of signal term after k steps)
This requires measuring the signal component of h_k = W^k @ xi_0, specifically the
projection onto xi_0 vs the noise projection.

The correct protocol:
  1. Start from xi_0 (a stored pattern).
  2. Compute h_k = (1/N) * Xi^T * (Xi @ h_{k-1})^{p-1} for k steps (NOT the sign update).
  3. Measure <h_k | xi_0> / N (the signal coefficient at step k, before the sign step).
  4. This gives C(k,m)_emp which should match alpha^{k-1}/k!.

Note: the SIGNED (sign-thresholded) iterates all converge to ~+/-1 cosine (success/failure),
not to the fractional coefficient.

## Recommendation for Strategy

Confirm the correct definition of C(k,m) and the measurement protocol:
- Is C(k,m) = alpha^{k-1}/k! the free-energy coefficient or the signal attenuation?
- The measurement needs the RAW update rule (before thresholding) for k iterations.
- Alternatively, provide a direct experimental design that tests multi-step retrieval
  benefit vs single-step at varying alpha and k.

Acted-on 2026-06-02: ckm_coefficient smoke fail diagnostic; redesign deferred to research
