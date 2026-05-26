# Pre-registration: wave14xrd_structured_keys

Date: 2026-05-20
Status: Pre-registered, gated
Experiment: [exp_wave14xrd_structured_keys.py](../experiments/exp_wave14xrd_structured_keys.py)

## Why

wave14xrd with RANDOM keys gave NO_PEAKS. This matches Agent 1's prediction:
random +/-1 destroys spectral structure. Hadamard-row keys should give
crystalline Bragg peaks in WHT.

## Hypothesis

Hadamard-keyed substrate gives max WHT-spectrum SNR >= 5.0; random-keyed
substrate gives max SNR < 2.0.

## Operational

Sweep K in {50, 100, 200, 400, 600, 900, 1300, 2000, 3000}. For each (K,
key_source in {random, hadamard}), build 10 trials x 8 seeds = 80 W-matrices
per cell. Compute WHT, measure peak SNR.

## Expected runtime

Smoke: ~5 sec
Full: ~5-10 min on GPU
