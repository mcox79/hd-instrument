# Pre-registration: wave14_hatano_sasa_ness_audit_v1

**Date:** 2026-05-29
**Anchor:** wave14_hatano_sasa_ness_audit_v1
**Script:** experiments/exp_wave14_hatano_sasa_ness_audit_v1.py
**Queue:** remote_cpu_queue
**Timeout:** 900s

## Hypothesis

The Hatano-Sasa fluctuation theorem identity `<exp(-W_ex)>=1` holds for the
substrate's Cap-3 streaming dynamics at N=8192, and cross-basin trajectory
fraction > 0 (NESS cost is non-zero). Confirms that substrate streaming is a
genuine Markov-consistent NESS process.

Parent: hatano_sasa_v4_glauber (HARD_PASS sigma_hk>0 at N=8192, 5-seed).
This is the AUDIT variant: single seed, N=8192, 650 trajectories across 5
noise levels, testing HS identity directly.

## Configuration

- N: 8192 (FULL), 2048 (SMOKE)
- M: 150 FULL, 60 SMOKE
- n_traj_per_level: 130 FULL, 30 SMOKE
- noise_levels: [0.10, 0.15, 0.20, 0.25, 0.30] FULL, [0.10, 0.20, 0.30] SMOKE
- seed: 42 (single seed)
- max_iter: 60 FULL, 40 SMOKE

## Metrics

- hs_identity_val: `<exp(-W_ex)>` (should be ~1.0 for Markov NESS)
- sigma_hk: mean housekeeping entropy production proxy
- cross_basin_frac: fraction of trajectories that crossed attractor basins

## Pre-registered bands

**HARD_PASS (NESS_CERT_PASS):**
HS identity within tol=0.15 AND cross_basin_frac >= 0.02 AND sigma_hk >= 0.02.
Substrate streaming is a Markov-consistent NESS with measurable housekeeping cost.

**HARD_FAIL (NESS_CERT_FAIL):**
|`<exp(-W_ex)>` - 1.0| > 0.15.
HS identity violated; substrate NESS is not Markov-consistent.

**MIDDLE_BAND (NESS_CERT_PARTIAL):**
HS identity holds but cross_basin_frac < 0.02 or sigma_hk < 0.02.
Insufficient basin crossings to resolve NESS cost; M/N too low for this N.

NOTE: Smoke ran PARTIAL at N=2048 (all trajectories in spurious attractors at
M/N=0.029). FULL at N=8192, M=150 (M/N=0.018) may also show PARTIAL if spurious
attractor fraction is high at large N. MIDDLE_BAND acceptable for this first AUDIT.

Calibration probe (first direct HS identity check): bands set at +-50% of
theoretical prediction (HS identity=1.0 for any NESS). Band range [0.85, 1.15]
per calibration probe policy.

## Timeout estimate

Smoke: N=2048, 1 seed, 90 traj, 3 noise levels = 3.06s.
Full: N=8192, 1 seed, 650 traj, 5 noise levels.
N-scale: (8192/2048)^2 = 16x. Traj scale: 650/90 = 7.2x.
Estimate: 3.06 * 16 * 7.2 = 352s. Safety 1.5 * 5 = 2641s. Cap at 900s.
timeout_s = 900.

## Downstream

- HARD_PASS: HS identity confirmed at N=8192 with direct trajectory audit;
  Cap-3 NESS cert promoted to AUDIT-LEVEL. Cap_map row 🟢 upgrade.
- MIDDLE_BAND: HS identity holds but no basin crossings; likely M/N too low;
  investigate with higher M or targeted noise levels.
- HARD_FAIL: Substrate NESS fails HS audit; major finding requiring investigation.
