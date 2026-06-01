# Pre-registration: wave14_spin_ice_frustration_comparison_v1

**Date:** 2026-05-27
**Script:** experiments/exp_wave14_spin_ice_frustration_comparison_v1.py
**Queue:** remote_cpu_queue (CPU; ~1-2h)
**Trigger:** exp_wave14_1rsb_rate_dep_hysteresis_v1 returns RATE_DEPENDENT_KINETIC

## Hypothesis

If substrate shows rate-dependent hysteresis (kinetic glass), does the frustration pattern
match documented Ising/dipolar spin-ice, or is it qualitatively distinct?

## Design

4-signature battery: SIG1 (ice rule), SIG2 (correlation decay), SIG3 (non-monotone gap),
SIG4 (Kasteleyn threshold). N=1024, 3 seeds, extended epochs {1..128}.

## Pre-registered bands

- **SPIN_ICE_MATCH:** SIG3 non-monotone (gap peak) AND SIG4 Kasteleyn-sharp. P=0.18 (calibrated).
- **KINETIC_GLASS_DISTINCT:** SIG3 monotone-decreasing + SIG4 smooth. P=0.40.
- **FRUSTRATED_NOVEL:** mixed pattern; structured-codebook frustration. P=0.35.
