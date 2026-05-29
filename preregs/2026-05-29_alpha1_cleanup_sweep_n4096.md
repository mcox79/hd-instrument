# Pre-registration: alpha1_cleanup_sweep_n4096

**Date:** 2026-05-29
**Anchor:** alpha1_cleanup_sweep_n4096
**Script:** experiments/exp_alpha1_cleanup_sweep_n4096.py
**Queue:** remote_cpu_queue
**Trigger:** alpha-1 cleanup-strength sweep (operational-layer steerability rescue post-KF5_PARTIAL_DECOUPLING)

## Hypothesis
At fixed beta=32, M_frac=4, N=4096, BSC codebook:
Varying cleanup operator strength (tau_cleanup from 0=no cleanup to inf=hard argmax)
may unlock W-magnitude-operative steerability at the readout level.
If bpc varies monotonically with tau_cleanup and cleanup helps (min_bpc < argmax_bpc * 0.95):
the continuous W path matters and steerability exists at the cleanup-threshold level.

## Config
- N_FULL = 4096 (PROT-018: _n4096 suffix binding)
- Seeds: [7, 17, 23]
- tau_cleanup sweep: [0.0, 0.1, 1.0, 10.0, 100.0, inf]
- Fixed: beta=32, M_frac=4, BSC codebook

## N-suffix
_n4096 suffix; production N = 4096. PROT-018 satisfied.

## Pre-registered bands
- HARD_PASS: bpc varies monotonically across tau_cleanup sweep with total bpc_range > 0.5
  AND bpc_min < bpc_argmax * 0.95 in >= 2/3 seeds.
- HARD_FAIL: bpc flat (bpc_range < 0.05) across all seeds.
- MIDDLE_BAND: bpc_range in [0.05, 0.5).

Calibration probe. "no prior empirical cleanup-sweep anchor; bands per calibration-probe policy."

## Timeout estimate
Parent v2 smoke: ~0.3s CPU. N scale (4096/1024)^1.5 = 8. Seeds=3. Taus=6.
estimate = 0.3 * 8 * 3 * 2 = 14.4s * safety 10x = 144s. PROT-019 floor 14400s. timeout_s = 14400.

## Smoke result
SELFTEST PASS. bpc_range=19.9 at smoke (valid: argmax tau=inf gives high bpc on near-untrained W).
Valid non-null metrics. MIDDLE_BAND at smoke expected (1 seed). Ship allowed.
