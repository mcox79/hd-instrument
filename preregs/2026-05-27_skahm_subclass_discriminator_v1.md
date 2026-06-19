# Pre-registration: skahm_subclass_discriminator_v1

Date: 2026-05-27
Experiment: exp_skahm_subclass_discriminator_v1.py
Queue: overnight_queue (GPU)
Timeout: 2400s

## Hypothesis
v228 confirmed substrate = DOCUMENTED gated-multistable AM class with HYBRID match
across 3 sub-classes: non-reciprocal Hopfield (sub-A), spatial-correlated DAM (sub-B),
saddle-hierarchy DAM (sub-C). One sub-class should be DOMINANT.

## Design
3 discriminating probes:
- Probe A: directional asymmetry delta_asymm = |ret(W) - ret(W.T)| / sum
- Probe B: spatial-correlation lift = ret(natural atoms) - ret(shuffled atoms)
- Probe C: saddle transition sharpness d_transition = |ret(0.25) - ret(0.0)| / 0.25

N=1024 (FULL), 5 seeds, M=400 patterns.

## N-suffix binding (PROT-018)
No _n<N> suffix in anchor name. No binding rule applies.
Production N = N_DEFAULT_FULL = 1024 (stated in script config).

## Pre-registered thresholds

### Calibration probe bands (no prior sub-class anchor, widened +/-50%)
Probe A: DOCUMENTED if delta_asymm >= 0.075 (upper +50% of theoretical 0.05)
         NULL if delta_asymm < 0.025 (lower -50%)
         WEAK_DOCUMENTED if 0.05 <= delta_asymm < 0.075
         AMBIGUOUS if 0.025 <= delta_asymm < 0.05

Probe B: DOCUMENTED if lift >= 0.045 (+50% of 0.03)
         NULL if lift < 0.015 (-50%)
         WEAK_DOCUMENTED if 0.03 <= lift < 0.045
         AMBIGUOUS if 0.015 <= lift < 0.03

Probe C: DOCUMENTED if d_transition >= 0.150 (+50% of 0.10)
         NULL if d_transition < 0.050 (-50%)
         WEAK_DOCUMENTED if 0.10 <= d_transition < 0.150
         AMBIGUOUS if 0.050 <= d_transition < 0.10

### Overall verdict
- HARD_PASS: exactly 1 probe DOCUMENTED and >= 1 probe NULL -> clear sub-class attribution
- HARD_FAIL: 0 probes DOCUMENTED or all 3 similar strength -> HYBRID remains
- MIDDLE_BAND: 2 probes DOCUMENTED -> partial discrimination

## Timeout estimate
Smoke N=256: elapsed=1.24s (observed).
FULL N=1024, seeds=5: scale factor = (1024/256)^1.5 * (5/1) = 8 * 5 = 40
timeout_s = ceil(1.5 * 1.24 * 40) = ceil(74.4) = 75 -> 300s minimum
Adding Probe C (corpus training, ~1min per cell at N=1024 x 5 seeds): ~600s
With margin: timeout_s = 2400

## Parent experiment
anchor_novel_phase_battery_v3_n8192 (v228 DOCUMENTED gated-multistable AM confirmed)
