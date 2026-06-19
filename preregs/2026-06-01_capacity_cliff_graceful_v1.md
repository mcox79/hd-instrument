# Prereq: capacity_cliff_graceful_v1

## Scientific question
Graceful vs sharp degradation near alpha_c. Fine alpha sweep around 0.138.

## Pre-registered bands
HARD-PASS (graceful): R(0.13) > 0.60 in >= 4/5 seeds.
HARD-PASS (sharp): R(0.12) > 0.80 AND R(0.15) < 0.30 in >= 4/5 seeds.
MIDDLE: R(0.13) in [0.30, 0.60] and monotone.
HARD-FAIL: non-monotone in >= 3/5 seeds.

## N-suffix
_n4096 binding. Production N MUST = 4096.

## Timeout estimate
smoke_wall_s=0.1. FULL N=4096: ceil(1.5 * 0.1 * (4096/512)^1.5 * (5/2) * (12/5)) = ceil(53) -> timeout_s=300.

## Date
2026-06-01
