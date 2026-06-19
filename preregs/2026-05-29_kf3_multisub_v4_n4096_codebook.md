# Pre-Registration: kf3_multisub_v4_n4096_codebook

Date: 2026-05-29
Anchor: kf3_multisub_v4_n4096_codebook
Queue: remote_cpu_queue
Script: experiments/exp_kf3_multisub_v4_n4096_codebook.py
Timeout: 14400s

## Question
Is multi-substrate isolation codebook-agnostic? Tests BSC codebook (v2 used Kerdock).
Cross-substrate leakage should remain <= 0.05.

## Config
N=4096, M_FRACS=[0.5,2.0,8.0], SEEDS=[7,17,23,31,41]

## Pre-Registered Thresholds
HARD_PASS: leakage_mean <= 0.05 at M_frac=2.0 (HP_LEAKAGE_MAX=0.05)
HARD_FAIL: leakage_mean >= 0.20 at M_frac=2.0 (codebook-specific failure)
MIDDLE_BAND: leakage between 0.05 and 0.20

## Calibration Note
Prior: kf3_multisub_v2 (Kerdock) was HARD_PASS. v4 tests BSC codebook.
3x-theory-bound HP_LEAKAGE_MAX=0.05 is wider than Kerdock v2 to account for BSC differences.
