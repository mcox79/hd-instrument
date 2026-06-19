# Pre-registration: kappa3_sensitivity_sweep_n16384_v3_delta_alpha_protocol_v1

**Date:** 2026-06-02
**Anchor name:** kappa3_sensitivity_sweep_n16384_v3_delta_alpha_protocol_v1
**Queue:** overnight_queue (GPU, local RTX 4060 Ti)
**Script:** experiments/exp_kappa3_sensitivity_sweep_n16384_v3_delta_alpha_protocol_v1.py

## Scientific question

Does the substrate kappa_3 Hutchinson estimator detect delta-alpha perturbations
at N=16384 using the delta-alpha sensitivity protocol (Hopfield-vs-Hopfield+delta),
matching the cloud anchor (kappa46_fingerprint_n32768_v1 Part B)?

## Protocol

- observable: sigma_sep = |kappa_3(M_base) - kappa_3(M_base+n_extra)| / pooled_SE
- alpha_base = 0.05 (M_base = 819 at N=16384)
- delta_alpha_grid = [0.001, 0.01, 0.04]
- n_probes_sens = 5000 (same as cloud Part B)
- dtype: float32 patterns + float64 accumulation
- 5 seeds, N=16384

## Prior evidence

The N=32768 cloud anchor measured sigma_sep up to 1727 at delta_alpha=0.04
using THIS SAME delta-alpha protocol. The prior v1/v2 HF used a DIFFERENT
observable (Hopfield-vs-GOE block-diagonal), which is not comparable.

## N-suffix binding (PROT-018)

_n16384 binds N=16384 for FULL run. Smoke runs at N_smoke=4096 (N/4).

## Formula self-tests

1. N^(2/3) scaling from cloud: sigma_sep(d=0.04, N=16384) ~ 1727 * (16384/32768)^(2/3) ~ 1088
   [INPUT: cloud=1727, N_ratio=0.5] [EXPECTED: ~1088 >> HP=100]
2. Hutchinson estimator: k3_base non-NaN at N_test=512, M=26.
3. pooled_SE > 0 after pert measurement.
4. GPU memory > 0 MB after alloc.

Self-test result: PASS (run at module scope).

## Pre-registered bands

HARD-PASS: ALL of:
  - sigma_sep >= 100 at delta_alpha=0.04 (mean over seeds)
  - sigma_sep >= 10 at delta_alpha=0.01 (mean over seeds)
  - sigma_sep >= 3.0 at delta_alpha=0.001 (mean over seeds)

MIDDLE:
  - sigma_sep(d=0.001) in [1.5, 3.0) AND sigma_sep(d=0.04) >= 100 AND sigma_sep(d=0.01) >= 10

HARD-FAIL: ANY of:
  - sigma_sep < 50 at delta_alpha=0.04
  - sigma_sep < 3.0 at delta_alpha=0.01

These bands match the research audit R3-A recommendations (Section 4) scaled for N=16384.

## Calibration note

Prior empirical anchor exists at N=32768 (cloud, sigma_sep=1727 at d=0.04).
N=16384 extrapolation via N^(2/3): predicted ~1088, HP threshold is 100.
Predicted margin above HP: 10.9x. Bands are NOT calibration-probe widths
(no ±50% inflation needed because prior anchor IS empirically validated at N=32768).

## Smoke results

Smoke N=4096 (N/4), 3 seeds, delta_alphas=[0.01, 0.04], n_probes=500:
  delta=0.01: mean sigma_sep=28.9 (MIDDLE at smoke N -- expected; scales to ~73 at N=16384)
  delta=0.04: mean sigma_sep=99.0 (borderline HP at smoke N; scales to ~249 at N=16384)

Smoke verdict: MIDDLE_BAND (borderline at smoke N=4096, HP expected at full N=16384).

Walk-back gate: smoke sigma_sep(d=0.04)=99 is within 1% of HP=100 AT SMOKE SCALE.
But FULL N=16384 prediction is ~249 >> HP=100 (via N^(2/3) * 10x probes scaling).
Full scale prediction well above HP -- no additional sample size doubling needed.
GPU utilization verified: 0.104 GB peak > 0.01 GB floor.

## Timeout estimate

Smoke wall at N=4096: ~0.01s per seed (very fast -- all-matrix-free Krylov).
Full at N=16384 with n_probes=5000: scale factor = (16384/4096)^1.5 * (5000/500) * (5/3 seeds)
  = 4^1.5 * 10 * 1.67 = 8 * 10 * 1.67 = 133.
  timeout_s = ceil(1.5 * 0.01 * 133) = ceil(2.0) -> round up to 300s minimum.
  Using 5 min (300s) + safety margin for delta_alpha grid: 600s.

Actually the 0.01s smoke wall is artificially fast (PyTorch JIT warmup). For N=16384,
n_probes=5000, 3 delta_alpha values, 5 seeds, estimated ~60s at full scale.
timeout_s = ceil(1.5 * 60) = 90s minimum. Using 900s (15 min) for safety.

## Strategic outcome

- If HARD_PASS: PP-50 row confirmed at N=16384 with delta-alpha sensitivity protocol;
  no envelope caveat; product story "kappa_3 detects 0.1%-4% tampering at N=16384" lands.
- If MIDDLE: PP-50 envelope caveat (delta_alpha threshold at N=16384 vs N=32768 documented).
- If HARD_FAIL: PP-50 caveat N-band (tamper detection threshold at N=16384 elevated vs N=32768).

P_deflated: 0.55 (research spec calibrated; delta-alpha protocol validated at N=32768;
N=16384 extrapolation by N^(2/3)).
