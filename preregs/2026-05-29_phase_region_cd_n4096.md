# Phase Region C/D Probe -- N=4096, beta=64

Filed: 2026-05-29
Anchors:
  region_c_kf1_n4096_beta64_mfrac4
  region_c_kf2_n4096_beta64_mfrac4
  region_d_kf1_n4096_beta64_mfrac12
  region_d_kf2_n4096_beta64_mfrac12
Driver script: experiments/exp_phase_region_cd_v1_n4096.py
Parent: t1_beta_sweep_v1_n4096 (v267 HARD_PASS, beta_c localized at M_frac=8)

## Scientific Question

At beta=64 (safely above beta_c~10-16 from v267):
1. Region C (M_frac=4, M < M_c): does retention approach 1.0? (ferromagnetic state stabilized)
2. Region D (M_frac=12, M > M_c): is retention suppressed despite high beta? (M_c boundary holds)

## Phase Diagram Context

Phase regions (Hopfield-like substrate at N=4096 Kerdock):
- Region A: M < M_c, beta < beta_c -- paramagnetic
- Region B (= Region C here): M < M_c, beta > beta_c -- ferromagnetic
- Region C (D in some conventions): M > M_c, beta > beta_c -- overcapacity + high beta

beta_c estimated at ~10-16 from v267. beta=64 is 4-6x above beta_c.
M_c estimated at M_frac~8-12 from axis1 chunks.
Region C probe: M_frac=4 (well below M_c), Region D: M_frac=12 (well above M_c).

Note on M cap: store_facts_batched handles M > C by repeating codebook permutations.
At N=4096, C=16384 (Kerdock 4-coset). M_frac=12 -> M=49152 = 3x repetitions = genuine overcapacity.

## Calibration Note

No prior empirical anchor for beta > beta_c unprobed regime.
Bands set per calibration-probe policy: +/-50% around theoretical prediction.

## Pre-registered Bands

### Region C (kf1 and kf2 variants):
- HARD_PASS: mean_retention >= 0.70 at >= 3/5 seeds
  (ferromagnetic: high beta + undercapacity stabilizes retrieval)
- HARD_FAIL: mean_retention < 0.35 (ferromagnet absent despite high beta)
- MIDDLE_BAND: 0.35 <= mean_retention < 0.70

### Region D (kf1 and kf2 variants):
- HARD_PASS: mean_retention < 0.30 at >= 3/5 seeds
  (M_c boundary holds: overcapacity suppresses retrieval even at high beta)
- HARD_FAIL: mean_retention >= 0.60 (unexpected high retention above M_c)
- MIDDLE_BAND: 0.30 <= mean_retention < 0.60

## Formula Self-tests (verified pre-ship)

1. N = 4096 (PROT-018 binding) -- verified
2. M at M_frac=4, N=4096: M=16384 -- verified
3. M at M_frac=12, N=4096: M=49152 (> C=16384; repeating permutations) -- verified
4. beta_c~10-16 from v267; beta=64 is safely above -- verified
5. smoke: ret_C=1.0 (undercapacity + high beta = perfect), ret_D=0.302 (overcapacity suppressed) -- verified

## Timeout Estimate

smoke_wall_s = 0.17s (region_C, 1 seed) and 0.43s (region_D, 1 seed).
FULL: N=4096, 5 seeds, 2 regions.
Scaling: N ratio = 4096/1024 = 4x. Seeds ratio = 5/1. Scaling_exp=1.5.
formula for region_D (slower): ceil(1.5 * 0.43 * 4^1.5 * 5) = ceil(1.5 * 0.43 * 8 * 5) = ceil(25.8) = 26s.
PROT-019 _n4096 floor = 14400s. timeout_s = 14400.
Note: actual runtime << 14400; floor applies because of _n4096 suffix.

## TCFT / Saad-Solla Blocker

TCFT and Saad-Solla versions of this probe blocked:
- TCFT: no Hopfield-style beta parameter (fixed thermodynamic KBT=1.0)
- Saad-Solla: LM framework, beta_inf is softmax temperature not Hopfield beta_c
Blocker filed at: notes/exp_dev_to_strategy_phase_cd_tcft_ss_blocker_2026-05-29.md
