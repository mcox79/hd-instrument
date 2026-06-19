# Prereq: c_infty_seb_detection_v1

## Scientific question
Does C(t,tw) plateau at C_infty > 0 as t/tw grows? Strong ergodicity breaking (SEB) vs weak (C_infty -> 0).

## Pre-registered bands
HARD-PASS: C_infty > 0.05 in >= 4/5 seeds at alpha=0.15.
MIDDLE: C_infty > 0.02 in >= 3/5 seeds.
HARD-FAIL: C_infty < 0.02 in >= 4/5 seeds.
Calibration probe; +-50% per policy. HP at 0.05; HF at 0.02.

## N-suffix
No _nN suffix; production N=2048; rationale: SEB detection, GPU memory budget.

## Timeout estimate
smoke_wall_s=1.0. GPU ~10x faster for Glauber. ceil(1.5 * 1.0 * (5/2)) = 4s -> timeout_s=300.

## Date
2026-06-01
