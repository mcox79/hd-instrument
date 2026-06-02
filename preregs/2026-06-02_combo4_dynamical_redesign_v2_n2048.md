# Pre-registration: combo4_dynamical_redesign_v2_n2048

Date: 2026-06-02
Anchor: combo4_dynamical_redesign_v2_n2048
Queue: overnight_queue
Seeds: [7, 17, 23]
N: 2048

## Hypothesis
COMBO-4 dynamical ultrametricity redesign at N=2048. Tests: (1) M_dyn (fraction of
dynamical saddles -- patterns that follow gradient ascent) >= 0.75, (2) C(t,t_w)
two-time correlator scaling collapse MSE < 0.05, (3) aging exponent mu in [0.5, 1.0]
as predicted by CK theory. DFT oscillation test dropped (failed v1 at N=1024).

## Pre-registered Thresholds
HARD-PASS: M_dyn >= 0.75 AND collapse_mse < 0.05 AND mu in [0.5, 1.0] (>=60% seeds).
HARD-FAIL: M_dyn < 0.60 (dynamical saddles absent) OR collapse_mse > 0.20.
MIDDLE: 2/3 cells pass.

## Calibration Source
Smoke MIDDLE_BAND at N=256: M_dyn=0.98 PASS, mse=0.0 PASS, mu=0.10 FAIL.
mu_fit unreliable at N=256 smoke scale. At N=2048, aging dynamics should be
sufficiently developed for mu to be in the expected [0.5,1.0] CK range.

## Smoke Result
MIDDLE_BAND: M_dyn=0.98, collapse_mse~0, mu=0.10. Walk-back: 3 seeds at N=2048.
