# Pre-registration: wave14_delta_lambda_drift_v1

Date: 2026-05-22
Status: Pre-registered, gated
Priority: Strategy cycle 85 "best 1-GPU-hour ROI" — critical-point / Griffiths-phase gating test

Sweep alpha in {0.10, 0.13, 0.153, 0.18, 0.22}; measure rho(t) relaxation;
fit power-law delta(alpha). Pattern distinguishes critical / Griffiths /
tricritical / no-regime.

## Verdict labels
- DELTA_DRIFT_PINNED (true criticality)
- DELTA_DRIFT_GRIFFITHS (continuously-tunable exponent; PRODUCT UPGRADE)
- DELTA_DRIFT_JUMP (tricritical)
- DELTA_DRIFT_NOISE / NO_POWERLAW (not in critical regime)
- DELTA_DRIFT_INCONCLUSIVE

## Runtime: ~10 min
