# Prereg: q_f5_oscillating_envelope_v1

## Scientific question
Q-F5: Does the substrate show a Garcia-Lorenzana finite-omega oscillating envelope in C(t,t_w)?

## Pre-registered thresholds (BEFORE running)
- HARD-PASS: Either cell A (DFT SNR >= 3.0 at finite omega) OR cell B (frac_osc >= 0.20).
- HARD-FAIL: Both HF-A (DFT SNR < 1.5) AND HF-B (frac_osc < 0.05).
- MIDDLE-BAND: One cell passes, one HF -- partial oscillation evidence.

## Calibration note
No prior substrate oscillating-envelope measurement. Bands +-50% per calibration-probe policy.

## Smoke result
MIDDLE_BAND: mean_dft_snr=2.324 (below HP=3.0, above HF=1.5), mean_frac_osc=0.065 (below HP=0.20, above HF=0.05).
Partial oscillation signal; neither DFT SNR nor frac_osc decisive at N=512.
Walk-back applied: FULL at N=1024 (2x from smoke N=512).

## Timeout estimate
Smoke wall: 30.7s, N=512->1024 (2x), seeds=2->5, scaling=1.5
timeout = ceil(1.5 * 30.7 * 2^1.5 * 2.5) = ceil(1.5*30.7*2.83*2.5) = ceil(325) = 325s.
timeout=600s (2x buffer for Glauber overhead).

## N-suffix note
No _nN suffix; production N=1024 per rule 3. Rationale: larger N needed for cleaner oscillation signal.
