# Pre-Registration: pb1_susceptibility_v2_n4096

Date: 2026-05-29
Anchor: pb1_susceptibility_v2_n4096
Queue: remote_cpu_queue
Script: experiments/exp_pb1_susceptibility_v2_n4096.py
Timeout: 14400s

## Question
Does retrieval accuracy show a finite chi_peak (susceptibility) as a function of inverse
temperature beta at N=4096? Peak chi_peak > 0 would confirm phase-transition-like behavior.

## Config
N=4096, BETA_VALS=[2,4,8,16,32,64], M_FRAC=1.0, SEEDS=[7,17,23]

## Pre-Registered Thresholds
HARD_PASS: chi_peak > 0 at >= 2/3 seeds (susceptibility peak present)
HARD_FAIL: chi_peak = 0 at all seeds at N=4096 (no transition visible at this scale)
MIDDLE_BAND: chi_peak > 0 at 1/3 seeds only

## Calibration Note
Calibration probe (no prior empirical anchor at N=4096 with this protocol).
chi_peak theoretical prediction: should peak near beta=critical.
Bands: chi_peak > 0 threshold is minimal; HARD_PASS requires consistent non-zero.
Note: at small N smoke chi_peak=0 is expected (acc=1.0 plateaus, no susceptibility peak).
