# Pre-registration: kf2_cross_codebook_v1_n4096

Date: 2026-05-28
Queue: remote_cpu_queue
Script: experiments/exp_kf2_cross_codebook_v1_n4096.py
N: 4096
Seeds: [7, 17, 23, 31, 41]
M_fracs: [0.25, 0.5, 1.0, 2.0, 4.0]
Codebook families: ["kerdock", "bsc", "gaussian"]

## Hypothesis
KF-2 edit isolation (max_iso < 0.05) holds across all 3 codebook families, confirming the isolation property is architecture-general not Kerdock-specific.

## Thresholds (pre-registered)

HARD_PASS: max_iso < 0.05 for ALL families across >= 4/5 seeds and all M_fracs
HARD_FAIL: max_iso >= 0.10 for any family at majority seeds
MIDDLE_BAND: isolation holds for Kerdock but fails for BSC or Gaussian (architecture-specific)

## Calibration basis
Smoke results at N=4096 1 seed:
- kerdock: max_iso=0.010 (PASS; matches theory bound 1/sqrt(4096)=0.0156)
- bsc: max_iso=0.040 (PASS; slightly higher, within 2.5x of theory)
- gaussian: max_iso=0.020 (PASS)
All well below 0.05 threshold. 5-seed FULL run to confirm across seeds.

## Timeout
1800s (remote CPU; 3 families x 5 seeds x 5 M_fracs = 75 cells; ~30min budget)
