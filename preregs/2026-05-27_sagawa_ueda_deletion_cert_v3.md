# Pre-registration: sagawa_ueda_deletion_cert_v3

**Date**: 2026-05-27
**Anchor**: sagawa_ueda_deletion_cert_v3
**Script**: experiments/exp_sagawa_ueda_deletion_cert_v3.py
**Queue**: remote_cpu_queue
**Parent**: sagawa_ueda_deletion_cert_v2 (MIDDLE_BAND; N={128,256} only ran at 1 seed)

## Hypothesis

SU deletion certificate (su_frac >= 0.70) holds across N in {256,512,1024,4096} at 5 seeds.

## Pre-registered bands

- HARD-PASS: su_frac >= 0.70 in >= 4/4 N-values AND all excess_mean > 0
- HARD-FAIL: su_frac < 0.40 in >= 3/4 N-values
- MIDDLE-BAND: partial pass

## Timeout estimate

smoke_wall_s = 0.12s (smoke overhead dominated). Use analog: v1 at N=1024 5 seeds ~5-10s.
FULL sweep {256,512,1024,4096} x 5 seeds: ~60-120s.
timeout_s = 600s (conservative margin for N=4096).
