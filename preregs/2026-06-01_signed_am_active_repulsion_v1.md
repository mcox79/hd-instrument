# Prereq: signed_am_active_repulsion_v1

## Scientific question
Does W_signed = W_A - W_B create active repulsion for B-patterns (energy maxima)?
One-step update from noisy B should move to anti-B.

## Pre-registered bands
HARD-PASS: fraction_anti_b >= 0.75 AND b_energy > rand_energy in >= 4/5 seeds.
MIDDLE: fraction_anti_b >= 0.50.
HARD-FAIL: fraction_anti_b < 0.30 in >= 3/5 seeds.
Calibration probe; +-50%. HP at 0.75; HF at 0.30.

## N-suffix
No _nN suffix; production N=2048; rationale: signed-AM test, GPU memory budget.

## Timeout estimate
smoke_wall_s=1.2. GPU ~10x faster. ceil(1.5 * 1.2 * (5/2)) = 4.5s -> timeout_s=300.

## Date
2026-06-01
