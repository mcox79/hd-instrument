# Pre-Registration: saad_solla_v21_n4096_m_sweep_v2

Date: 2026-05-29
Anchor: saad_solla_v21_n4096_m_sweep_v2
Queue: remote_cpu_queue
Script: experiments/exp_saad_solla_v21_n4096_m_sweep_v2.py
Timeout: 14400s

## Question
Does the Saad-Solla saddle-cascade signature (R2 < 0.85 OR max_dev >= 0.40) hold under
varying corpus sizes as a proxy for memory load?

## Config
N=4096, SEEDS=[7,17,23], F_SWEEP=[0.0,0.15,0.50,0.80,1.0], CORPUS=[4_000,150_000]

## Pre-Registered Thresholds
HARD_PASS: R2 < 0.85 OR max_dev >= 0.40 (saddle-cascade visible) at 2+ corpus sizes
HARD_FAIL: R2 >= 0.85 AND max_dev < 0.40 at all corpus sizes (pure linear, no cascade)
MIDDLE_BAND: signature present at 1 corpus size only

## Calibration Note
Prior: v20 attempted at N=4096 (module load failure). v11 confirmed at its N config.
Bands calibrated at prior v11 empirical values +/-50%.
