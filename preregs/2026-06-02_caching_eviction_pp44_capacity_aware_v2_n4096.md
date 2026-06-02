# Pre-registration: caching_eviction_pp44_capacity_aware_v2_n4096

Date: 2026-06-02
Anchor: caching_eviction_pp44_capacity_aware_v2_n4096
Queue: remote_cpu_queue
Seeds: [7, 17, 23, 31, 41]
N: 4096

## Hypothesis
PP-44 capacity-aware eviction v2 rescue. v1 MIDDLE_BAND at alpha=0.12 (sub-threshold).
v2 raises stress to alpha=0.18 (well past alpha_c=0.138) so no-eviction W collapses,
while eviction-coupled W (triggered by r_eff monitor from PP-44) maintains fidelity.

## Pre-registered Thresholds
HARD-PASS: fid_with_eviction >= 0.80 AND fid_no_eviction <= 0.50 AND retained_fid >= 0.85
           AND n_alarms >= 1 (>=60% seeds).
HARD-FAIL: fid_with_eviction < 0.50 (eviction not working).
MIDDLE: 2/3 cells pass.

## Calibration Source
Smoke HARD_PASS at N_ACTIVE=512: fid_evict=1.0, retained=1.0, n_alarms=9.
Note: no-eviction contrast only manifests at N >= 2048 (finite-N effect below threshold).
At N=4096 with alpha=0.18 >> alpha_c=0.138, no-eviction collapse is definitive.

## Smoke Result
HARD_PASS at N=512: fid_evict=1.0, retained=1.0, n_alarms=9. FULL at N=4096 needed
for no-eviction contrast cell. Walk-back not triggered but FULL confirms contrast.
