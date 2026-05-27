# Prereg: wave14e_bet_n_wta_v5

**Date:** 2026-05-26
**Parent:** wave14e_bet_n_wta_v4 (in-flight; K=512 codebook)
**Trigger:** ship when v4 returns BET_N_TIER1_PROMOTION or BET_N_PARTIAL_TIER2
**Question:** Does the WTA codebook scale to K=1024 / K=2048, or does collapse onset occur?

## Hypothesis
v4 tests K=512. If P2 and P3 both pass, a larger codebook may provide more discriminative
power. K=1024 is the natural next doubling. At K=2048, dead-atom collapse is predicted
if the winner-fatigue anti-collapse rate (rho=0.05) is insufficient.

## Design
- K sweep: {512, 1024, 2048}  (K=512 overlap for continuity)
- N=4096, K_active=12, n_epochs=8, eta=0.01, rho=0.05
- 5 seeds, M=2000 for P2 anchor
- Additional metric: dead_atom_frac (fraction of atoms never selected as winner)
- GPU overnight_queue (~5-7 hrs)

## Pre-registered bands
- **HARD_PASS**: P2_ratio >= 1.10 AND P3_gap >= 0.05 AND dead_frac < 0.30 at K=1024
- **HARD_FAIL** (collapse): dead_frac >= 0.50 at K=1024 OR P2_ratio < 1.05
- **MIDDLE_BAND**: dead_frac in [0.30, 0.50) OR P2_ratio in [1.05, 1.10)
- **INSTRUMENTATION_FAIL**: P1 utilization gate < 5% OR NaN in any metric

## Calibration
Prior anchor: v4 (K=512). No anchor at K=1024. Dead-atom threshold of 0.50 comes from
observation that K=512 with 50%+ dead atoms renders the codebook equivalent to K=256.
Bands at +-50% of v4 P2_ratio threshold per calibration-probe policy.

## Middle-band outcome plan
If MIDDLE_BAND: find optimal K between 512 and 1024 via exp_wave14e_bet_n_wta_v5b (K=384 intermediate).
