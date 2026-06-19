# Pre-registration: wave14cpu_alpha_c_extended

Date: 2026-05-20
Status: Pre-registered, gated, CPU experiment
Experiment: [exp_wave14cpu_alpha_c_extended.py](../experiments/exp_wave14cpu_alpha_c_extended.py)

## Why

wave14m_alpha_c measured alpha_c=0.153 at N=4096. AGS asymptote is 0.138.
Slope was 1.45 (super-linear). Need to extend to larger N to confirm finite-N
correction is ~1/sqrt(N) and substrate truly is canonical AGS Hopfield.

CPU-suitable (matmul-light, sequential bundle ops, long runtime acceptable).

## Hypothesis

alpha_c at N=8192, 16384 trends toward 0.138 as 1/sqrt(N) correction.
Predicted: 0.146 at N=8192, 0.142 at N=16384.

## Operational definition

- N in {8192, 16384}, CPU
- K_factor_grid from 0.05 to 0.40
- M=32768 fixed codebook
- 3 seeds, 15 trials per K
- K* via linear interp at recovery 0.5

## Expected runtime

Smoke: ~5 sec
Full: ~30-60 min on CPU

## Verdict labels

- `EXT_ALPHAC_AGS_CONSISTENT`: deviation within 2x finite-N estimate
- `EXT_ALPHAC_NOT_AGS`: alpha_c > 0.20 - not canonical AGS
- `EXT_ALPHAC_DEVIATES`: too far from 0.138
- `EXT_ALPHAC_INCONCLUSIVE`: K* not found
