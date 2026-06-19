# Pre-registration: wave14_r17_delta_eff_probe2

Date: 2026-05-21
Status: Pre-registered, gated
Priority: R17 Probe 2 (Δ_eff scaling — sequenced AFTER Probe 1 area-law positive)
Author: experiment_dev session, pipeline tick 72

## Why

R17 Probe 1 returned R17_AREA_LAW_LIKE — substrate has area-law-like entropy
scaling. Per R17 spec: "Probe 2 only if Probe 1 gives area-law-like positive."
Condition met; Probe 2 is now sequenced.

Probe 2 tests whether substrate codebook carries Δ_eff > 1/2, enabling
Sang-Hsieh-Zou AQEC noise-tolerance derivation.

## Mechanism (per R17 Probe 2 spec)

Compute position-pair two-point correlation over each codebook:
  C[i, j] = (1/M) sum_mu codebook[mu, i] * codebook[mu, j]
Aggregate by position-distance r = |i - j|:
  C_avg(r) = mean of |C[i, j]| over all pairs with |i-j| = r
Fit log|C_avg(r)| vs log(r+1) for r in [1, N/2]; slope = -Δ_eff.

Codebooks tested: random_bsc, hadamard, kerdock (4-coset). Per codebook,
report Δ_eff and whether fit is well-defined (R^2 > 0.7).

## Verdict labels

- DELTA_EFF_AQEC_ENABLE (>=2 codebooks give Δ_eff > 0.5 with R^2 > 0.7)
- DELTA_EFF_PRESENT (some codebook has power-law decay; Δ_eff defined but < 0.5)
- DELTA_EFF_NO_POWERLAW (no codebook gives R^2 > 0.7; no AQEC analog)
- DELTA_EFF_INCONCLUSIVE

## Runtime: ~3 min CPU
