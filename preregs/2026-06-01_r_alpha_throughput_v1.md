# Prereq: r_alpha_throughput_v1

## Scientific question
R(alpha) sweep to pin v1b operating point. HP: R(0.01) > 0.97, monotone, cliff in [0.10, 0.20].

## Pre-registered bands
HARD-PASS: R(0.01) > 0.97 AND monotone in >= 4/5 seeds.
MIDDLE: R(0.01) > 0.90 AND monotone.
HARD-FAIL: R(0.01) < 0.80 in >= 3/5 seeds.
Calibration probe; +-50%. HP at 0.97; HF at 0.80.

## N-suffix
_n4096 binding. Production N MUST = 4096.

## Timeout estimate
smoke_wall_s=0.1 (N=512). FULL N=4096: ceil(1.5 * 0.1 * (4096/512)^1.5 * (5/2) * (12/4)) = ceil(88) -> timeout_s=600.

## Date
2026-06-01
