# Prereq: batched_deletion_extended_v1

## Scientific question
Extend Q22 to k={1,5,10,20,50,100} with 3 correlation levels. Verify R(k) ~ r_1^k for independent.

## Pre-registered bands
HARD-PASS: r_1 in [0.88, 0.96] AND R(10)/r_1^10 in [0.7, 1.3] in >= 4/5 seeds.
MIDDLE: r_1 in [0.85, 0.99] AND direction correct.
HARD-FAIL: r_1 < 0.80 in >= 3/5 seeds.
Calibration probe; +-50%.

## N-suffix
_n4096 binding. Production N MUST = 4096.

## Timeout estimate
smoke_wall_s=1.5 (N=512). FULL N=4096: ceil(1.5 * 1.5 * (4096/512)^1.5 * (5/2)) = ceil(168) -> timeout_s=300.

## Date
2026-06-01
