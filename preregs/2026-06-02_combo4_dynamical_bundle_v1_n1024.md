# Pre-registration: combo4_dynamical_bundle_v1_n1024

**Date:** 2026-06-02
**Script:** experiments/exp_combo4_dynamical_bundle_v1_n1024.py
**Queue:** overnight_queue
**N:** 1024 (PROT-018 binding)
**Seeds:** [7, 17, 23]
**Smoke result:** MIDDLE_BAND (M_dyn=1.1893 HARD_PASS, collapse_mse=0.005 HARD_PASS, mu=0.128 noise at smoke scale)

## Hypothesis

The SKAH-M substrate exhibits dynamical ultrametricity in trajectory space (M_dyn > 1.0 threshold) and saddle-collapse MSE < 0.01. The dynamical order parameter mu captures non-equilibrium activity.

## Metrics

- `M_dyn`: mean C_13/min(C_12,C_23) for Glauber dynamics replicas (three-time triangle ratio)
- `collapse_mse`: MSE of saddle midpoint collapse trajectory
- `mu`: mean activity (non-equilibrium order parameter)

## Thresholds (pre-registered)

**HARD_PASS:** M_dyn >= 1.10 AND collapse_mse <= 0.05
**HARD_FAIL:** M_dyn < 0.80 OR collapse_mse > 0.20
**MIDDLE_BAND:** between HP and HF

Walk-back note: smoke mu=0.128 unreliable at N=256/T=256 (smoke scale noise); full N=1024 expected to be reliable.

## Timeout

1200s (from: 1.5 * 3.0s * (1024/256)^2 * (200/50) * 3/2 = 864s, rounded up)
