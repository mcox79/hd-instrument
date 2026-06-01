# Prereq: large_deviations_substrate_v1

Date: 2026-05-27
Anchor: large_deviations_substrate_v1
Queue: remote_cpu_queue
Script: experiments/exp_large_deviations_substrate_v1.py
Timeout: 2100s

## Hypothesis
Substrate memory trajectories satisfy Gallavotti-Cohen large-deviations symmetry (gc_r2 >= 0.80, asymmetry > 0.01). First application of large-deviation rate function to HD-substrate memory system.

## Pre-registered bands (calibration probe, no prior anchor)
- HARD-PASS: gc_linearity_r2 >= 0.80 AND gc_sigma_match < 0.50 AND asymmetry > 0.01
- HARD-FAIL: gc_linearity_r2 < 0.20 OR asymmetry < 0.001
- MIDDLE-BAND: otherwise
Bands set at +-50% of theoretical prediction per calibration-probe policy.

## Timeout estimate
Smoke N=512 T=500: ~3s. Full N=4096 5 seeds T=2000: 1.5 * 3 * 22.6 * 4 * 5 = 2034s -> 2100s.
