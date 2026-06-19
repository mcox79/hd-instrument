# Prereg: symbolic_prim_battery_v1

**Filed:** 2026-06-01
**Anchor:** symbolic_prim_battery_v1
**Queue:** remote_cpu_queue
**Script:** experiments/exp_symbolic_prim_battery_v1.py

## Hypothesis

The substrate functions as a partial native inference engine at N=2048.
Four sub-tests: S1 (rule-fire K=8), S2 (disjunction K=4), S3 (4-step chain),
S5 (backward 1-step).

## Pre-registered bands

- HARD-PASS: >= 3/4 sub-tests pass HP criteria (>= 4/5 seeds for each sub-test).
  S1: rule-fire gap > 0.3; S2: disjunction gap > 0.2;
  S3: chain cos > 0.25 at step 4; S5: backward hop cos > 0.25.
- MIDDLE: 2/4 sub-tests pass HP.
- HARD-FAIL: <= 1/4 sub-tests pass HP.

## Design

N=2048. 5 seeds. All sub-tests share pattern generation.

## Timeout estimate

~2s total. timeout_s = 300 (floor).

## N-suffix note

No _nN suffix. Production N = 2048; symbolic-primitive battery at standard size.
