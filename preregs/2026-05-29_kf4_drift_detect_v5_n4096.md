# Pre-Registration: kf4_drift_detect_v5_n4096

Date: 2026-05-29
Anchor: kf4_drift_detect_v5_n4096
Queue: remote_cpu_queue
Script: experiments/exp_kf4_drift_detect_v5_n4096.py
Timeout: 14400s

## Question
Does drift detection accuracy drop (acc_drop) increase monotonically with N_DRIFT (drift
intensity)? Does the substrate show dose-response at N=4096?

## Config
N=4096, M_FRACS=[0.5,2.0], SEEDS=[7,17,23], N_DRIFT_STEPS=[50,200,500]

## Pre-Registered Thresholds
HARD_PASS: mean_acc_drop at N_DRIFT=500 >= 0.10 (dose-response present)
HARD_FAIL: acc_drop < 0.02 at all N_DRIFT levels (no drift signature)
MIDDLE_BAND: acc_drop > 0 at some levels but not monotone or < 0.10 at max

## Calibration Note
Prior: v4 single N_DRIFT=200. v5 extends to 3-point dose response.
No prior N_DRIFT sweep anchor; bands set at 0.10 +/-50% = [0.05, 0.15].
