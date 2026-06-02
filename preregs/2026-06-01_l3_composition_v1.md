# Prereq: l3_composition_v1

## Scientific question
Does L=3 Hadamard-binding composition achieve end-to-end accuracy > 0.55 at alpha <= 0.02 per level?

## Pre-registered bands
HARD-PASS: mean accuracy > 0.55 in >= 3/5 seeds.
MIDDLE: 0.52 <= accuracy <= 0.55.
HARD-FAIL: accuracy < 0.52 in >= 3/5 seeds.
Calibration probe; +-50% per policy. HP at 0.55; HF at 0.52.

## N-suffix
_n4096 binding. Production N MUST = 4096.

## Timeout estimate
smoke_wall_s=0.1 (CPU, N=512). GPU at N=4096: ceil(1.5 * 0.1 * (4096/512)^1.5 * (5/2)) = ceil(5.6) -> timeout_s=600.

## Date
2026-06-01
