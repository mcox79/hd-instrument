# Pre-registration: saad_solla_v17_cross_cb_v1_n4096

Date: 2026-05-28
Queue: overnight_queue
Script: experiments/exp_saad_solla_v17_cross_cb_v1_n4096.py
N: 4096
Seeds: [7, 17, 23]
Codebook families: ["bsc", "antipodal"]
F_sweep: [0.0, 0.15, 0.5, 0.8, 1.0]
M_fracs: [0.25, 1.0]

## Hypothesis
Saad-Solla plateau shape (r2 >= 0.70, max_dev >= 0.10) replicates with non-Kerdock codebooks (BSC random, Antipodal), confirming the prediction is not an artifact of Kerdock's quasi-orthogonality.

## Thresholds (pre-registered)

HARD_PASS: r2 >= 0.70 AND max_dev >= 0.10 for BOTH families, across >= 2/3 seeds
HARD_FAIL: r2 < 0.40 OR max_dev < 0.05 for ANY family across majority seeds
MIDDLE_BAND: all other outcomes

## Calibration basis
Smoke results at N=4096 1-seed:
- BSC: r2=0.668, max_dev=0.516 PASS (max_dev high = stronger non-monotone)
- Antipodal: r2=0.693, max_dev=0.469 PASS
Thresholds set conservatively below smoke: HP r2=0.70 floor (smoke ~0.67-0.69; allow 5% seed noise; if 3-seed mean holds, expect ~0.72-0.80). max_dev floor 0.10 (well below smoke 0.47-0.52). Calibration probe -- first cross-codebook measurement.

## Timeout
10800s (3h; _n4096 tier; smoke was 15s x 3 families x 2 M_fracs = estimate 3h for 3 seeds x full config)
